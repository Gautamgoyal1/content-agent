"""API routes for executing and inspecting autonomous content runs."""

from fastapi import APIRouter, HTTPException
from content_agent.api.schemas import RunCreateRequest
from content_agent.models.draft import ContentDraftRecord
from content_agent.pipeline import execute_content_pipeline, RUNS_STORE

router = APIRouter(prefix="/runs", tags=["Runs"])


@router.post("", response_model=ContentDraftRecord)
def create_run(request: RunCreateRequest):
    """Execute the autonomous LangGraph content generation pipeline."""
    try:
        record = execute_content_pipeline(request)
        return record
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("", response_model=list[ContentDraftRecord])
def list_runs():
    """List all executed content pipeline runs."""
    return list(RUNS_STORE.values())


@router.get("/{run_id}", response_model=ContentDraftRecord)
def get_run(run_id: str):
    """Retrieve details for a specific run."""
    record = RUNS_STORE.get(run_id)
    if not record:
        raise HTTPException(status_code=404, detail="Run not found")
    return record
