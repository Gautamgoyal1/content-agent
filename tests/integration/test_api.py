"""Integration tests for FastAPI endpoints."""

from fastapi.testclient import TestClient
from content_agent.main import app

client = TestClient(app)


def test_health_check_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["workflow"] == "autonomous_langgraph"


def test_index_page_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    assert "Content Agent" in res.text
    assert "Autonomous Multi-Agent Pipeline" in res.text


def test_brief_validation_endpoints():
    res = client.post("/api/briefs/validate", json={
        "topic": "Container Security",
        "content_type": "blog",
        "target_word_count": 550,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["topic"] == "Container Security"

    profile_res = client.post("/api/briefs/profile", json={
        "topic": "Container Security",
        "target_audience": "DevOps Engineers",
    })
    assert profile_res.status_code == 200
    assert profile_res.json()["technical_depth"] == "deep_technical"


def test_full_run_lifecycle_and_exports():
    # 1. Create run
    create_res = client.post("/api/runs", json={
        "topic": "Distributed Tracing at Scale",
        "content_type": "blog",
        "target_audience": "Site Reliability Engineers",
        "target_word_count": 450,
    })
    assert create_res.status_code == 200
    run_data = create_res.json()
    run_id = run_data["id"]
    assert run_id.startswith("run-")
    assert run_data["export_ready"] is True

    # 2. Get run
    get_res = client.get(f"/api/runs/{run_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == run_id

    # 3. List runs
    list_res = client.get("/api/runs")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 4. Export Markdown
    md_res = client.get(f"/api/exports/{run_id}?format=markdown")
    assert md_res.status_code == 200
    assert "text/markdown" in md_res.headers["content-type"]
    assert "---" in md_res.text

    # 5. Export HTML
    html_res = client.get(f"/api/exports/{run_id}?format=html")
    assert html_res.status_code == 200
    assert "<!DOCTYPE html>" in html_res.text

    # 6. Export Docx / Text
    txt_res = client.get(f"/api/exports/{run_id}?format=text")
    assert txt_res.status_code == 200
    assert "TITLE:" in txt_res.text

    # 7. Approvals override
    app_res = client.post(f"/api/approvals/{run_id}", json={
        "status": "approved",
        "notes": "Manual override signoff",
    })
    assert app_res.status_code == 200
    assert app_res.json()["export_ready"] is True
