# setup.py

from setuptools import setup, find_packages

setup(
    name="django_watchlog_apm",
    version="1.0.0",
    license="MIT",
    description="Django instrumentation for Watchlog APM with JSON OTLP export",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Mohammadreza",
    author_email="mohammadnajm75@gmail.com",
    url="https://github.com/Watchlog-monitoring/django_watchlog_apm.git",
    packages=find_packages(),
    install_requires=[
        # Use the 1.35.x OpenTelemetry stack
        "opentelemetry-api>=1.35.0,<1.36.0",
        "opentelemetry-sdk~=1.35.0",
        "opentelemetry-proto==1.35.0",

        # OTLP HTTP exporter
        "opentelemetry-exporter-otlp-proto-http==1.35.0",
        "opentelemetry-exporter-otlp-proto-common==1.35.0",

        # gRPC exporter (if you ever need it)
        "opentelemetry-exporter-otlp-proto-grpc~=1.35.0",

        # Instrumentations matching 0.56b0 on that stack
        "opentelemetry-instrumentation-django==0.56b0",
        "opentelemetry-instrumentation-requests==0.56b0",
        "opentelemetry-instrumentation-wsgi==0.56b0",
        "opentelemetry-semantic-conventions==0.56b0",
        "opentelemetry-util-http==0.56b0",

        # Other deps
        "dnspython>=2.0.0",
        "requests>=2.25.0",
        "googleapis-common-protos>=1.56.0",
        "protobuf>=3.20.0,<7.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
