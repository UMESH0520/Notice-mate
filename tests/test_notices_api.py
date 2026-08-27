"""End-to-end API test suite for NoticeMate."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.database import init_db
from backend.app.main import app

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    init_db()

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "NoticeMate"
    assert "version" in data
    assert "ai_enabled" in data
    assert "ai_mode" in data


def test_demo_notices_catalog():
    response = client.get("/api/demo/notices")
    assert response.status_code == 200
    catalog = response.json()
    assert isinstance(catalog, list)
    assert len(catalog) >= 3
    demo_ids = [item["id"] for item in catalog]
    assert "tax-143-1" in demo_ids


def test_create_demo_notice_flow():
    # 1. Create notice from demo ID
    res_create = client.post("/api/notices/demo", json={"demo_id": "tax-143-1"})
    assert res_create.status_code == 201
    notice_data = res_create.json()
    notice_id = notice_data["id"]
    assert notice_id is not None
    assert "disclaimer" in notice_data

    # 2. Analyze notice
    res_analyze = client.post(f"/api/notices/{notice_id}/analyze", json={"language": "en"})
    assert res_analyze.status_code == 200
    analysis = res_analyze.json()
    assert analysis["notice_type"] is not None
    assert analysis["deadline"] is not None

    # 3. Get detail
    res_detail = client.get(f"/api/notices/{notice_id}")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["id"] == notice_id
    assert len(detail["important_dates"]) > 0
    assert isinstance(detail["eligibility"], list)

    # 4. Dates sub-resource endpoint
    res_dates = client.get(f"/api/notices/{notice_id}/dates")
    assert res_dates.status_code == 200
    dates = res_dates.json()
    assert isinstance(dates, list)
    assert len(dates) > 0

    # 5. Eligibility sub-resource endpoint
    res_elig = client.get(f"/api/notices/{notice_id}/eligibility")
    assert res_elig.status_code == 200
    elig = res_elig.json()
    assert isinstance(elig, list)

    # 6. Roadmap sub-resource endpoint
    res_roadmap = client.get(f"/api/notices/{notice_id}/roadmap")
    assert res_roadmap.status_code == 200
    roadmap = res_roadmap.json()
    assert "steps" in roadmap
    assert len(roadmap["steps"]) > 0

    # 7. Update preparation step
    step_key = roadmap["steps"][0]["key"]
    res_prep = client.put(
        f"/api/notices/{notice_id}/preparation",
        json={"step_key": step_key, "state": "completed"},
    )
    assert res_prep.status_code == 200
    updated_roadmap = res_prep.json()
    assert updated_roadmap["completed"] >= 1

    # 8. Research sub-resource endpoint
    res_research = client.post(f"/api/notices/{notice_id}/research")
    assert res_research.status_code == 200
    research = res_research.json()
    assert "sources" in research

    res_sources = client.get(f"/api/notices/{notice_id}/sources")
    assert res_sources.status_code == 200

    # 9. Draft response
    res_draft = client.post(f"/api/notices/{notice_id}/response", json={"language": "en"})
    assert res_draft.status_code == 200
    draft = res_draft.json()
    assert "content" in draft

    # 10. Simulated Submit
    res_sub = client.post(f"/api/notices/{notice_id}/submit", json={"confirmed": True})
    assert res_sub.status_code == 201
    submission = res_sub.json()
    assert submission["reference"] is not None


def test_create_text_notice():
    text_content = (
        "DEMO RECRUITMENT NOTICE\n"
        "Department of Public Works\n"
        "Reference No: DPW/2026/099\n"
        "Applications invited for Junior Engineer.\n"
        "Last date to apply: 30 October 2026.\n"
        "Fee: Rs. 500.\n"
        "Required: Degree Certificate, Photo, Aadhaar proof.\n"
    )
    res = client.post("/api/notices/text", json={"text": text_content, "filename": "test.txt"})
    assert res.status_code == 201
    notice_id = res.json()["id"]

    res_analyze = client.post(f"/api/notices/{notice_id}/analyze")
    assert res_analyze.status_code == 200
    analysis = res_analyze.json()
    assert analysis["deadline"] == "30 October 2026"


def test_documents_format_size_and_research_enrichment():
    # 1. Create notice for Karnataka lift notice
    res_create = client.post("/api/notices/demo", json={"demo_id": "karnataka-lift-notice-2023"})
    assert res_create.status_code == 201
    notice_id = res_create.json()["id"]

    # 2. Analyze
    res_analyze = client.post(f"/api/notices/{notice_id}/analyze", json={"language": "en"})
    assert res_analyze.status_code == 200

    # 3. Check documents endpoint
    res_docs = client.get(f"/api/notices/{notice_id}/documents")
    assert res_docs.status_code == 200
    docs = res_docs.json()
    assert len(docs) >= 3

    # Verify doc_format and size_limit are populated
    for d in docs:
        assert d["name"] is not None
        assert "doc_format" in d
        assert "size_limit" in d
        assert "source_note" in d

    # 4. Upload a test PDF document
    doc_id = docs[0]["id"]
    test_pdf_content = b"%PDF-1.4 dummy valid pdf file content for testing portal validation limits."
    res_up = client.post(
        f"/api/notices/{notice_id}/documents",
        data={"document_id": doc_id, "name": docs[0]["name"]},
        files={"file": ("test_safety_certificate.pdf", test_pdf_content, "application/pdf")},
    )
    assert res_up.status_code == 200
    up_doc = res_up.json()
    assert up_doc["status"] == "uploaded"
    assert "validation" in up_doc
    assert up_doc["validation"]["ok"] is True
    checks = up_doc["validation"]["checks"]
    check_labels = [c["label"] for c in checks]
    assert any("size limit" in lbl.lower() for lbl in check_labels)
    assert any("format" in lbl.lower() for lbl in check_labels)

    # 5. Run research and verify documents are enriched
    res_research = client.post(f"/api/notices/{notice_id}/research")
    assert res_research.status_code == 200
    research_data = res_research.json()
    assert research_data["mode"] == "demo"

    res_docs_after = client.get(f"/api/notices/{notice_id}/documents")
    assert res_docs_after.status_code == 200
    docs_after = res_docs_after.json()
    assert len(docs_after) >= len(docs)

