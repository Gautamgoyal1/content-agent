"""Quality check results and quality decision models."""

from typing import Literal
from pydantic import BaseModel, Field


class QualityCheckResult(BaseModel):
    """Result of an automated quality gate check."""

    name: str
    passed: bool
    score_or_metric: str
    details: str
    severity: Literal["info", "warning", "error"] = "info"


class QualityDecision(BaseModel):
    """Autonomous decision selected by the Quality Decision Agent."""

    action: Literal[
        "export",
        "research_more",
        "repair_claims",
        "invoke_editor",
        "repair_formatting",
        "terminate_failure",
    ]
    rationale: str
    target_issues: list[str] = Field(default_factory=list)
    action_description: str = ""
