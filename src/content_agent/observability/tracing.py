"""Execution tracer for multi-agent workflows."""

import time
from dataclasses import dataclass, field


@dataclass
class TraceSpan:
    name: str
    start_time: float
    end_time: float = 0.0
    status: str = "running"
    metadata: dict = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        end = self.end_time or time.time()
        return round((end - self.start_time) * 1000, 2)


class WorkflowTracer:
    """Records timeline spans across agent and tool calls."""

    def __init__(self):
        self.spans: list[TraceSpan] = []

    def start_span(self, name: str, **metadata) -> TraceSpan:
        span = TraceSpan(name=name, start_time=time.time(), metadata=metadata)
        self.spans.append(span)
        return span

    def end_span(self, span: TraceSpan, status: str = "completed", **metadata) -> None:
        span.end_time = time.time()
        span.status = status
        span.metadata.update(metadata)

    def to_dict(self) -> list[dict]:
        return [
            {
                "name": s.name,
                "duration_ms": s.duration_ms,
                "status": s.status,
                "metadata": s.metadata,
            }
            for s in self.spans
        ]
