import pytest
from fastapi.testclient import TestClient
from main import app
from core.database import Base, engine

# Ensure clean DB for testing
Base.metadata.create_all(bind=engine)
client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_demo_load_and_facts():
    # 1. Load Demo Scenario
    demo_res = client.post("/api/demo/load")
    assert demo_res.status_code == 200
    data = demo_res.json()
    assert "source_id" in data
    assert "project_id" in data
    source_id = data["source_id"]

    # 2. Verify source retrieved
    source_res = client.get(f"/api/sources/{source_id}")
    assert source_res.status_code == 200
    assert "SUBSTATION-4" in source_res.json()["content"]

def test_transformation_pipeline_end_to_end():
    # 1. Load Demo
    demo_res = client.post("/api/demo/load")
    source_id = demo_res.json()["source_id"]

    # 2. Trigger transformation for all 7 outputs
    transform_payload = {
        "source_id": source_id,
        "audience": "Executive",
        "tone": "Professional",
        "language": "English",
        "detail_level": "Medium",
        "objective": "Inform",
        "outputs": ["linkedin", "x", "advisory", "summary", "infographic", "presentation", "video"]
    }
    t_res = client.post("/api/transform/", json=transform_payload)
    assert t_res.status_code == 200
    t_id = t_res.json()["transformation_id"]

    # 3. Check status & outputs
    status_res = client.get(f"/api/transform/{t_id}/status")
    assert status_res.status_code == 200
    assert status_res.json()["status"] in ["QUEUED", "PROCESSING", "COMPLETED", "PARTIAL_SUCCESS"]

    # Wait / query outputs
    outputs_res = client.get(f"/api/transform/{t_id}/outputs")
    assert outputs_res.status_code == 200
    outputs = outputs_res.json()
    assert len(outputs) > 0

    first_out = outputs[0]
    out_id = first_out["id"]

    # 4. Human Review (Approve)
    app_res = client.post(f"/api/outputs/{out_id}/approve")
    assert app_res.status_code == 200
    assert app_res.json()["status"] == "APPROVED"

    # 5. Edit Output (Creates Version 2)
    edit_res = client.patch(f"/api/outputs/{out_id}", json={
        "content": "Updated strategic directive with verified operator notes.",
        "change_description": "Operator Review"
    })
    assert edit_res.status_code == 200
    assert edit_res.json()["current_version"] >= 2

    # 6. Check Versions List
    vers_res = client.get(f"/api/outputs/{out_id}/versions")
    assert vers_res.status_code == 200
    assert len(vers_res.json()) >= 2

    # 7. Test Export Endpoints
    for fmt in ["json", "md", "docx", "pdf", "pptx"]:
        exp_res = client.get(f"/api/outputs/{out_id}/export/{fmt}")
        assert exp_res.status_code == 200
        assert len(exp_res.content) > 0

def test_ssrf_url_validation():
    # Attempting to fetch localhost should fail with 400
    res = client.post("/api/sources/url", json={
        "project_id": 1,
        "url": "http://127.0.0.1:8000/internal"
    })
    assert res.status_code == 400
    assert "prohibited" in res.json()["detail"].lower()

def test_provenance_and_tamper_detection():
    # 1. Check Public Key Endpoint
    pub_res = client.get("/api/provenance/public-key")
    assert pub_res.status_code == 200
    assert "public_key_hex" in pub_res.json()
    assert pub_res.json()["algorithm"] == "Ed25519"

    # 2. Load demo scenario & run transform
    demo_res = client.post("/api/demo/load")
    source_id = demo_res.json()["source_id"]
    t_res = client.post("/api/transform/", json={
        "source_id": source_id,
        "outputs": ["advisory", "linkedin"]
    })
    t_id = t_res.json()["transformation_id"]
    outputs = client.get(f"/api/transform/{t_id}/outputs").json()
    assert len(outputs) > 0
    out_id = outputs[0]["id"]

    # 3. Export original authentic document
    doc_res = client.get(f"/api/outputs/{out_id}/export/docx")
    assert doc_res.status_code == 200
    original_bytes = doc_res.content

    # 4. Verify authentic file
    verify_res = client.post(
        "/api/provenance/verify-file",
        files={"file": ("report.docx", original_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert verify_res.status_code == 200
    verify_data = verify_res.json()
    assert verify_data["is_authentic"] is True
    assert verify_data["status"] == "AUTHENTIC"
    assert verify_data["signature_valid"] is True
    assert verify_data["matched_provenance_id"] is not None

    # 5. Tamper with file (flip 1 byte)
    tampered_bytes = bytearray(original_bytes)
    tampered_bytes[-1] ^= 0xFF
    tamper_res = client.post(
        "/api/provenance/verify-file",
        files={"file": ("tampered.docx", bytes(tampered_bytes), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert tamper_res.status_code == 200
    tamper_data = tamper_res.json()
    assert tamper_data["is_authentic"] is False
    assert tamper_data["status"] == "HASH_MISMATCH"
    assert tamper_data["signature_valid"] is False

