from fastapi.testclient import TestClient

from agents.api import app


client = TestClient(app)


def test_lace_endpoint_returns_component_scores():
    response = client.post("/api/lace", json={
        "length_of_stay_days": 14,
        "acute_admission": True,
        "charlson_score": 4,
        "ed_visits_6_months": 4,
    })
    assert response.status_code == 200
    assert response.json() == {
        "length_of_stay": 7, "acute_admission": 3,
        "comorbidity": 5, "emergency_visits": 4, "total": 19
    }


def test_lace_api_rejects_invalid_values():
    req = {"length_of_stay_days": -1, "acute_admission": False,
           "charlson_score": 2, "ed_visits_6_months": 0}
    assert client.post("/api/lace", json=req).status_code == 422
    req["length_of_stay_days"] = 2
    req["acute_admission"] = "false"
    assert client.post("/api/lace", json=req).status_code == 422


def test_metadata_phi_block_is_safe_422():
    response = client.post("/api/audit", json={
        "task_id": "TEST", "target_identifier": "CASE",
        "primary_metric": 10, "attributes": {
            "nested": {"email": "alice@example.org"}
        }
    })
    assert response.status_code == 422
    assert "alice@example.org" not in response.text
