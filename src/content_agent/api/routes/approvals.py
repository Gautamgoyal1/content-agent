"""API routes for inspection and manual override / review."""

from fastapi import APIRouter, HTTPException
from content_agent.api.schemas import ApprovalUpdateRequest
from content_agent.models.draft import ContentDraftRecord
from content_agent.pipeline import RUNS_STORE

router = APIRouter(prefix="/approvals", tags=["Approvals"])


@router.post("/{run_id}", response_model=ContentDraftRecord)
def update_approval(run_id: str, payload: ApprovalUpdateRequest):
    """Update human review approval status for a draft."""
    record = RUNS_STORE.get(run_id)
    if not record:
        raise HTTPException(status_code=404, detail="Run not found")

    record.workflow_status = "completed" if payload.status == "approved" else "failed_qa"
    record.export_ready = payload.status == "approved"
    RUNS_STORE[run_id] = record
    return record
