import os


def configure_telemetry() -> None:
    """Enable Django tracing when the OpenTelemetry dependencies are installed."""
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.django import DjangoInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider = TracerProvider(
            resource=Resource.create({"service.name": os.getenv("OTEL_SERVICE_NAME", "cinema-api")})
        )
        provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(
                    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://alloy:4318")
                    + "/v1/traces"
                )
            )
        )
        trace.set_tracer_provider(provider)
        DjangoInstrumentor().instrument()
    except ImportError:
        pass
