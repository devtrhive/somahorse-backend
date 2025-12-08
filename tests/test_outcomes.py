from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_outcome_validation():
    payload = {
        "forecast_accuracy_percentage": 120.0,  # invalid
        "client_satisfaction_rating": 3,
        "code_quality_score": 4,
        "delivery_speed_days": 10
    }
    r = client.post("/v1/projects/1/outcomes", json=payload, headers={"Authorization":"Bearer test-token"})
    assert r.status_code == 400 or r.status_code == 422
