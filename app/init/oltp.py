from typing import Literal, Optional, Sequence, assert_never

from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as OTLPSpanExporterGRPC,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as OTLPSpanExporterHTTP,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import (
    Decision,
    ParentBasedTraceIdRatio,
    SamplingResult,
)
from opentelemetry.trace import Link, SpanKind, TraceState
from opentelemetry.util.types import Attributes


class DropEventSampler(ParentBasedTraceIdRatio):
    def should_sample(
        self,
        parent_context: Optional["Context"],
        trace_id: int,
        name: str,
        kind: Optional[SpanKind] = None,
        attributes: Attributes = None,
        links: Optional[Sequence["Link"]] = None,
        trace_state: Optional["TraceState"] = None,
    ) -> "SamplingResult":
        if (attributes or {}).get("http.method") == "OPTIONS":
            return SamplingResult(Decision.DROP)

        if name == "connect":
            return SamplingResult(Decision.DROP)

        if kind == SpanKind.INTERNAL:
            return SamplingResult(Decision.DROP)

        return super().should_sample(
            parent_context=parent_context,
            trace_id=trace_id,
            name=name,
            kind=kind,
            attributes=attributes,
            links=links,
            trace_state=trace_state,
        )

    def get_description(self) -> str:
        return "DropEventSampler"


def setup_oltp(
    endpoint: str,
    protocol: Literal["http", "grpc"],
    attributes: dict[str, str] = None,
    headers: dict[str, str] = None,
) -> None:
    # https://www.reddit.com/r/selfhosted/comments/1an8duz/seeking_recommendations_for_selfhosted_otel/

    resource = Resource.create(attributes=attributes)
    tracer = TracerProvider(resource=resource, sampler=DropEventSampler(rate=1.0))
    trace.set_tracer_provider(tracer)

    if protocol == "http":
        OTLPSpanExporter = OTLPSpanExporterHTTP  # noqa N806
    elif protocol == "grpc":
        OTLPSpanExporter = OTLPSpanExporterGRPC  # noqa N806
    else:
        assert_never(protocol)

    otlp_exporter = OTLPSpanExporter(
        endpoint=endpoint,
        headers=headers,
    )

    tracer.add_span_processor(BatchSpanProcessor(otlp_exporter))
