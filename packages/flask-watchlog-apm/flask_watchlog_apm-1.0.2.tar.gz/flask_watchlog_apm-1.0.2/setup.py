from setuptools import setup, find_packages

setup(
    name="flask_watchlog_apm",
    license="MIT",
    version="1.0.2",
    description="Flask instrumentation for Watchlog APM with JSON OTLP export",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Mohammadreza",
    author_email="mohammadnajm75@gmail.com",
    url="https://github.com/Watchlog-monitoring/flask_watchlog_apm",
    packages=find_packages(),
    install_requires=[
        # Core API & SDK
        "opentelemetry-api>=1.9.0",
        "opentelemetry-sdk>=1.9.0",

        # OTLP HTTP exporter
        "opentelemetry-exporter-otlp-proto-http>=1.9.0",

        # Instrumentation for Flask & outgoing HTTP
        "opentelemetry-instrumentation-flask>=0.34b0",
        "opentelemetry-instrumentation-requests>=0.34b0",

        # برای شناسایی Kubernetes DNS
        "dnspython>=2.0.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Flask",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
