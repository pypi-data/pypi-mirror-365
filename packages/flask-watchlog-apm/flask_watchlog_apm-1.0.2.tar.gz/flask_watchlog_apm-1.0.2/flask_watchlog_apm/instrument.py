# flask_watchlog_apm/instrument.py

import os
import dns.resolver
import logging
from datetime import datetime

import requests
from google.protobuf.json_format import MessageToDict
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, sampling
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.exporter.otlp.proto.common.trace_encoder import encode_spans
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource

# ---- Logging setup ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("flask_watchlog_apm")


def _is_running_in_k8s() -> bool:
    if os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount/token'):
        return True
    try:
        with open('/proc/1/cgroup') as f:
            if 'kubepods' in f.read():
                return True
    except Exception:
        pass
    try:
        dns.resolver.resolve('kubernetes.default.svc.cluster.local', 'A')
        return True
    except Exception:
        return False


def _detect_endpoint(default: str) -> str:
    if _is_running_in_k8s():
        k8s_url = 'http://watchlog-python-agent.monitoring.svc.cluster.local:3774/apm'
        logger.debug(f"Detected Kubernetes; using endpoint {k8s_url}")
        return k8s_url
    return default


class OTLPJsonSpanExporter(SpanExporter):
    def __init__(self, endpoint: str, headers: dict, timeout: float = 10.0):
        self._endpoint = endpoint
        self._headers = dict(headers or {})
        self._headers['Content-Type'] = 'application/json'
        self._timeout = timeout
        logger.debug(f"[OTLPJsonSpanExporter] endpoint={endpoint}, timeout={timeout}s")

    def export(self, spans) -> SpanExportResult:
        try:
            proto_req = encode_spans(spans)
            # only preserving_proto_field_name for compatibility
            body = MessageToDict(proto_req, preserving_proto_field_name=False)

            # normalize status codes
            STATUS_CODE_MAP = {
                "STATUS_CODE_UNSET": 0,
                "STATUS_CODE_OK": 1,
                "STATUS_CODE_ERROR": 2,
            }
            for rs in body.get("resourceSpans", []):
                if "scopeSpans" in rs:
                    rs["instrumentationLibrarySpans"] = rs.pop("scopeSpans")
                for ils in rs.get("instrumentationLibrarySpans", []):
                    for span in ils.get("spans", []):
                        code = span.get("status", {}).get("code")
                        if isinstance(code, str) and code in STATUS_CODE_MAP:
                            span["status"]["code"] = STATUS_CODE_MAP[code]

            count = sum(
                len(ils.get("spans", []))
                for rs in body.get("resourceSpans", [])
                for ils in rs.get("instrumentationLibrarySpans", [])
            )
            logger.debug(f"[OTLPJsonSpanExporter] exporting {count} spans to {self._endpoint}")

            # perform HTTP POST with timeout
            resp = requests.post(
                self._endpoint,
                json=body,
                headers=self._headers,
                timeout=self._timeout
            )
            logger.debug(f"[OTLPJsonSpanExporter] received HTTP {resp.status_code}")
            resp.raise_for_status()
            return SpanExportResult.SUCCESS

        except Exception as e:
            logger.warning(f"[OTLPJsonSpanExporter] export failed: {e}", exc_info=False)
            # swallow errors so app continues serving
            return SpanExportResult.SUCCESS

    def shutdown(self):
        logger.debug("[OTLPJsonSpanExporter] shutdown called")

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        logger.debug("[OTLPJsonSpanExporter] force_flush called")
        return True


def instrument_app(
    app,
    *,
    service_name: str,
    otlp_endpoint: str = 'http://localhost:3774/apm',
    headers: dict = None,
    batch_max_size: int = 200,
    batch_delay_ms: int = 5000,
    sample_rate: float = 1.0,
    send_error_spans: bool = False,
    error_tps: int = None,
    slow_threshold_ms: int = 0,
    export_timeout: float = 10.0,
):
    """
    Initialize Watchlog APM for Flask — JSON-over-HTTP spans.
    """
    headers = headers or {}
    rate = min(sample_rate, 0.3)
    base = _detect_endpoint(otlp_endpoint)

    # 1) TracerProvider with sampler
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(
        resource=resource,
        sampler=sampling.ParentBased(sampling.TraceIdRatioBased(rate))
    )
    trace.set_tracer_provider(provider)
    logger.info(f"[instrument_app] service_name={service_name}, sample_rate={rate}")

    # 2) Compose final URL
    url = f"{base}/{service_name}/v1/traces"
    logger.info(f"[instrument_app] exporter URL: {url}")

    # 3) Create JSON exporter
    exporter = OTLPJsonSpanExporter(url, headers, timeout=export_timeout)

    # 4) Setup filtering logic
    last_sec = int(datetime.utcnow().timestamp())
    err_count = 0

    def _filter(span):
        nonlocal last_sec, err_count
        now = int(datetime.utcnow().timestamp())
        if now != last_sec:
            last_sec, err_count = now, 0

        if send_error_spans and span.status.status_code.value != 0:
            if error_tps is None or err_count < error_tps:
                err_count += 1
                return True
            return False

        if slow_threshold_ms > 0 and span.start_time and span.end_time:
            dur_ms = (span.end_time - span.start_time) / 1e6
            if dur_ms > slow_threshold_ms:
                return True

        if rate < 1.0:
            from random import random
            return random() < rate

        return True

    # 5) Install BatchSpanProcessor (with optional filtering)
    bsp = BatchSpanProcessor(
        exporter,
        max_export_batch_size=batch_max_size,
        schedule_delay_millis=batch_delay_ms
    )
    if send_error_spans or slow_threshold_ms > 0 or rate < 1.0:
        class _FilteringProcessor(BatchSpanProcessor):
            def __init__(self, exporter, fn, **kw):
                super().__init__(exporter, **kw)
                self._fn = fn

            def on_end(self, span):
                if self._fn(span):
                    super().on_end(span)

        processor = _FilteringProcessor(
            exporter,
            _filter,
            max_export_batch_size=batch_max_size,
            schedule_delay_millis=batch_delay_ms
        )
        logger.info("[instrument_app] using filtering processor")
    else:
        processor = bsp
        logger.info("[instrument_app] using standard processor")

    provider.add_span_processor(processor)

    # 6) Auto-instrument Flask and exclude the exporter URL from HTTP instrumentation
    try:
        FlaskInstrumentor().instrument_app(app)
        RequestsInstrumentor().instrument(
            tracer_provider=provider,
            exclude_urls=[base]
        )
        logger.info("[instrument_app] Flask and Requests auto-instrumented (exporter URL excluded)")
    except Exception as e:
        logger.error(f"[instrument_app] auto-instrumentation failed: {e}", exc_info=True)

    return app


# alias for backward compatibility
instrument = instrument_app
