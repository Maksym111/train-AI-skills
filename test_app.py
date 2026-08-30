from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_unregister_participant_removes_email_from_activity():
    activity_name = "Test Activity"
    email = "student@example.edu"
    activities[activity_name] = {
        "description": "Temporary activity for testing",
        "schedule": "Mondays, 3:00 PM - 4:00 PM",
        "max_participants": 5,
        "participants": [email],
    }

    response = client.delete(f"/activities/{quote(activity_name)}/unregister?email={email}")

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_signup_and_unregister_flow_works_for_new_activity():
    activity_name = "New Test Activity"
    email = "newstudent@example.edu"
    activities[activity_name] = {
        "description": "Temporary activity for testing",
        "schedule": "Tuesdays, 3:00 PM - 4:00 PM",
        "max_participants": 2,
        "participants": [],
    }

    signup_response = client.post(f"/activities/{quote(activity_name)}/signup?email={email}")
    assert signup_response.status_code == 200
    assert email in activities[activity_name]["participants"]

    unregister_response = client.delete(f"/activities/{quote(activity_name)}/unregister?email={email}")
    assert unregister_response.status_code == 200
    assert email not in activities[activity_name]["participants"]


def test_activities_endpoint_disables_caching():
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.headers.get("Cache-Control") == "no-store"
