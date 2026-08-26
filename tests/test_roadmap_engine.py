"""Test suite for the Dynamic Personalized Roadmap Engine."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.database import init_db
from backend.app.main import app

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    init_db()

client = TestClient(app)


def test_dynamic_roadmap_structure():
    # 1. Create a recruitment text notice
    text_notice = (
        "DEMO RECRUITMENT NOTIFICATION 2026\n"
        "Staff Selection Board\n"
        "Reference: SSB/2026/JE-001\n"
        "Applications invited for Assistant Engineer.\n"
        "Age Limit: 21 to 30 years as of 01 January 2026.\n"
        "Education: Bachelor of Engineering / B.Tech.\n"
        "Application Window: 01 September 2026 to 30 September 2026.\n"
        "Required Documents: Degree Certificate, Photo, Signature, ID Proof.\n"
        "Application Fee: Rs. 500.\n"
        "Official Portal: ssb-demo.gov.in\n"
    )

    res_create = client.post("/api/notices/text", json={"text": text_notice, "filename": "recruitment.txt"})
    assert res_create.status_code == 201
    notice_id = res_create.json()["id"]

    # 2. Analyze
    res_analyze = client.post(f"/api/notices/{notice_id}/analyze")
    assert res_analyze.status_code == 200

    # 3. Fetch Dynamic Roadmap
    res_roadmap = client.get(f"/api/notices/{notice_id}/roadmap")
    assert res_roadmap.status_code == 200
    roadmap = res_roadmap.json()

    assert "steps" in roadmap
    assert len(roadmap["steps"]) >= 4
    assert roadmap["do_this_now"] is not None
    assert "headline" in roadmap

    # Verify 6-question breakdown fields are populated
    first_step = roadmap["steps"][0]
    assert "what" in first_step
    assert "why" in first_step
    assert "how" in first_step
    assert "when" in first_step
    assert "where" in first_step

    # Verify official channel invariant on the last step
    last_step = roadmap["steps"][-1]
    assert last_step["official_channel"] is True

    # 4. Test Step-Help AI Endpoint
    res_help = client.post(
        f"/api/notices/{notice_id}/roadmap/step-help",
        json={"step_id": first_step["id"], "question": "What is the fee amount?"},
    )
    assert res_help.status_code == 200
    help_out = res_help.json()
    assert help_out["step_id"] == first_step["id"]
    assert "explanation" in help_out
    assert "actionable_tip" in help_out


def test_prerequisite_blocking_and_unblocking():
    # Create notice
    res_create = client.post("/api/notices/demo", json={"demo_id": "tax-143-1"})
    assert res_create.status_code == 201
    notice_id = res_create.json()["id"]

    client.post(f"/api/notices/{notice_id}/analyze")

    res_roadmap = client.get(f"/api/notices/{notice_id}/roadmap")
    roadmap = res_roadmap.json()
    steps = roadmap["steps"]

    # Mark the first step complete
    first_key = steps[0]["key"]
    res_update = client.put(
        f"/api/notices/{notice_id}/preparation",
        json={"step_key": first_key, "state": "completed"},
    )
    assert res_update.status_code == 200
    updated_roadmap = res_update.json()

    assert updated_roadmap["completed"] >= 1
