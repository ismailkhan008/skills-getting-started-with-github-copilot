import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_activity_list():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert payload["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert isinstance(payload["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    activity_name = "Chess Club"
    email = "teststudent@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_duplicate_returns_400():
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"

    first_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert first_response.status_code == 200

    duplicate_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_from_activity_removes_participant():
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_from_activity_nonexistent_returns_404():
    response = client.delete(
        "/activities/Nonexistent Activity/signup",
        params={"email": "ghost@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
