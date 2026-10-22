"""Workflow state checkpoints and persistence utilities."""

from typing import Any
from content_agent.graph.state import ContentAgentState


class StateCheckpointer:
    """Manages snapshot checkpoints of the multi-agent workflow state."""

    def __init__(self):
        self._history: dict[str, list[dict[str, Any]]] = {}

    def save_checkpoint(self, run_id: str, node_name: str, state: ContentAgentState) -> None:
        if run_id not in self._history:
            self._history[run_id] = []
        self._history[run_id].append({
            "node": node_name,
            "revision": state.get("outline_revision_count", 0),
            "iteration": state.get("quality_iteration_count", 0),
            "export_ready": state.get("export_ready", False),
        })

    def get_history(self, run_id: str) -> list[dict[str, Any]]:
        return self._history.get(run_id, [])
