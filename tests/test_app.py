from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_unregister_participant_removes_email_from_activity():
    response = client.delete("/activities/Chess Club/unregister?email=michael@mergington.edu")

    assert response.status_code == 200
    assert "michael@mergington.edu" not in response.json()["participants"]


def test_unregister_participant_returns_error_for_unknown_participant():
    response = client.delete("/activities/Chess Club/unregister?email=missing@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
