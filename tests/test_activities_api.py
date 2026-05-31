import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
TEST_ACTIVITY = "Chess Club"
TEST_EMAIL = "teststudent@mergington.edu"


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert TEST_ACTIVITY in data
    assert data[TEST_ACTIVITY]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_creates_participant():
    response = client.post(f"/activities/{TEST_ACTIVITY}/signup?email={TEST_EMAIL}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {TEST_EMAIL} for {TEST_ACTIVITY}"
    assert TEST_EMAIL in activities[TEST_ACTIVITY]["participants"]


def test_signup_invalid_domain_rejected():
    bad_email = "tom@mergington.edi"
    response = client.post(f"/activities/{TEST_ACTIVITY}/signup?email={bad_email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid email domain"


def test_duplicate_signup_returns_400():
    response = client.post(f"/activities/{TEST_ACTIVITY}/signup?email=michael@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_participant():
    remove_email = "daniel@mergington.edu"
    response = client.delete(f"/activities/{TEST_ACTIVITY}/signup?email={remove_email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {remove_email} from {TEST_ACTIVITY}"
    assert remove_email not in activities[TEST_ACTIVITY]["participants"]


def test_unregister_missing_participant_returns_404():
    response = client.delete(f"/activities/{TEST_ACTIVITY}/signup?email=missing@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"
