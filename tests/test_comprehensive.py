"""
Comprehensive test suite for FastAPI activities management application.
All tests follow the AAA (Arrange-Act-Assert) pattern for clarity and consistency.

Tests are organized by endpoint:
- GET /activities — Activity listing
- POST /activities/{activity_name}/signup — Student signup
- DELETE /activities/{activity_name}/unregister — Student unregister
- GET / — Root redirect
"""

from fastapi.testclient import TestClient
from src.app import app


# ============================================================================
# GET /activities endpoint tests
# ============================================================================

def test_activities_endpoint_returns_all_activities():
    """
    Test that GET /activities returns all 9 hardcoded activities.
    
    Arrange: Create TestClient connected to the FastAPI app
    Act: Make a GET request to /activities endpoint
    Assert: Verify status 200 and response contains 9 activities
    """
    # Arrange
    client = TestClient(app)
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert len(activities) == 9
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities


def test_activities_endpoint_returns_required_fields():
    """
    Test that each activity contains all required fields.
    
    Arrange: Create TestClient
    Act: GET /activities and extract first activity
    Assert: Verify activity has description, schedule, max_participants, participants
    """
    # Arrange
    client = TestClient(app)
    
    # Act
    response = client.get("/activities")
    activities = response.json()
    first_activity = list(activities.values())[0]
    
    # Assert
    required_fields = {"description", "schedule", "max_participants", "participants"}
    assert set(first_activity.keys()) == required_fields
    assert isinstance(first_activity["description"], str)
    assert isinstance(first_activity["schedule"], str)
    assert isinstance(first_activity["max_participants"], int)
    assert isinstance(first_activity["participants"], list)


def test_activities_endpoint_has_cache_control_header():
    """
    Test that GET /activities response includes Cache-Control header.
    
    Arrange: Create TestClient
    Act: GET /activities
    Assert: Verify Cache-Control header is present with correct value
    """
    # Arrange
    client = TestClient(app)
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert "cache-control" in response.headers
    assert "no-store" in response.headers["cache-control"].lower()


def test_activities_endpoint_participants_are_lists():
    """
    Test that each activity's participants field is a list.
    
    Arrange: Create TestClient
    Act: GET /activities
    Assert: Verify all activities have participants as list
    """
    # Arrange
    client = TestClient(app)
    
    # Act
    response = client.get("/activities")
    activities = response.json()
    
    # Assert
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_data["participants"], list)
        # Each participant entry should be a string (email)
        for participant in activity_data["participants"]:
            assert isinstance(participant, str)


def test_activities_endpoint_response_is_json():
    """
    Test that GET /activities returns valid JSON response.
    
    Arrange: Create TestClient
    Act: GET /activities
    Assert: Verify response is valid JSON that can be parsed
    """
    # Arrange
    client = TestClient(app)
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    activities = response.json()  # This will raise if not valid JSON
    assert len(activities) > 0
    assert isinstance(activities, dict)


def test_activities_endpoint_all_activity_names_present():
    """
    Test that all expected hardcoded activities are present.
    
    Arrange: Create TestClient
    Act: GET /activities
    Assert: Verify all 9 activity names are in response
    """
    # Arrange
    client = TestClient(app)
    expected_activities = {
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Soccer Team",
        "Basketball Club",
        "Drama Club",
        "Art Workshop",
        "Debate Team",
        "Science Olympiad"
    }
    
    # Act
    response = client.get("/activities")
    activities = response.json()
    
    # Assert
    assert set(activities.keys()) == expected_activities


# ============================================================================
# POST /activities/{activity_name}/signup endpoint tests
# ============================================================================

def test_valid_signup_adds_email_to_activity():
    """
    Test that a valid signup adds email to activity participants.
    
    Arrange: Create TestClient and prepare test email
    Act: POST to /activities/{activity}/signup with email query parameter
    Assert: Verify status 200 and email appears in participants
    """
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "student1@example.com"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    
    # Assert
    assert response.status_code == 200
    # Verify email is now in the activity's participants
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]


def test_signup_invalid_activity_returns_404():
    """
    Test that signup to non-existent activity returns 404.
    
    Arrange: Create TestClient and prepare non-existent activity name
    Act: POST to /activities/{invalid_activity}/signup
    Assert: Verify status 404
    """
    # Arrange
    client = TestClient(app)
    invalid_activity = "NonExistentActivity"
    email = "student2@example.com"
    
    # Act
    response = client.post(
        f"/activities/{invalid_activity}/signup?email={email}"
    )
    
    # Assert
    assert response.status_code == 404


def test_signup_duplicate_email_returns_error():
    """
    Test that duplicate signup attempts return 400 error.
    
    Arrange: Create TestClient, signup email first time
    Act: Attempt signup with same email again
    Assert: Verify 400 Bad Request on duplicate
    """
    # Arrange
    client = TestClient(app)
    activity_name = "Programming Class"
    email = "student3@example.com"
    
    # Sign up first time
    response1 = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    
    # Act - Try to signup again with same email
    response2 = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    
    # Assert
    assert response1.status_code == 200
    assert response2.status_code == 400  # Duplicate signup returns 400


def test_signup_same_email_to_multiple_activities():
    """
    Test that same email can be signed up to multiple activities independently.
    
    Arrange: Create TestClient and prepare email
    Act: Signup same email to two different activities
    Assert: Email appears in both activities
    """
    # Arrange
    client = TestClient(app)
    email = "multi_activity@example.com"
    activity1 = "Soccer Team"
    activity2 = "Basketball Club"
    
    # Act - Sign up to first activity
    response1 = client.post(
        f"/activities/{activity1}/signup?email={email}"
    )
    
    # Act - Sign up to second activity
    response2 = client.post(
        f"/activities/{activity2}/signup?email={email}"
    )
    
    # Assert
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    # Verify email appears in both activities
    activities_response = client.get("/activities")
    activities = activities_response.json()
    
    assert email in activities[activity1]["participants"]
    assert email in activities[activity2]["participants"]


def test_signup_with_empty_email():
    """
    Test that signup with empty email is handled.
    
    Arrange: Create TestClient
    Act: POST with empty email string
    Assert: Verify appropriate response (may be added as empty or rejected)
    """
    # Arrange
    client = TestClient(app)
    activity_name = "Gym Class"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email="
    )
    
    # Assert - Could be 200 (accepted) or 422 (validation error)
    assert response.status_code in [200, 422, 400]


def test_signup_response_contains_confirmation_message():
    """
    Test that signup response contains confirmation message.
    
    Arrange: Create TestClient and prepare valid email
    Act: POST to signup endpoint
    Assert: Verify response contains success message
    """
    # Arrange
    client = TestClient(app)
    activity_name = "Art Workshop"
    email = "artist@example.com"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]


def test_signup_special_characters_in_email():
    """
    Test signup with email containing special characters.
    
    Arrange: Create TestClient with email containing special chars
    Act: POST with special characters in email
    Assert: Verify response (acceptance depends on validation)
    """
    # Arrange
    client = TestClient(app)
    activity_name = "Drama Club"
    email = "student+tag@example.com"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    
    # Assert - Should either accept or reject consistently
    assert response.status_code in [200, 400, 422]


# ============================================================================
# DELETE /activities/{activity_name}/unregister endpoint tests
# ============================================================================

def test_valid_unregister_removes_email_from_activity():
    """
    Test that unregister removes email from activity participants.
    
    Arrange: Create TestClient, signup participant first
    Act: DELETE /activities/{activity}/unregister with email query parameter
    Assert: Verify email no longer in participants
    """
    # Arrange
    client = TestClient(app)
    activity_name = "Debate Team"
    email = "debater@example.com"
    
    # First signup
    signup_response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    assert signup_response.status_code == 200
    
    # Act - Unregister
    unregister_response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )
    
    # Assert
    assert unregister_response.status_code == 200
    
    # Verify email is removed from participants
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity_name]["participants"]


def test_unregister_invalid_activity_returns_404():
    """
    Test that unregister from non-existent activity returns 404.
    
    Arrange: Create TestClient with non-existent activity
    Act: DELETE from /activities/{invalid_activity}/unregister
    Assert: Verify status 404
    """
    # Arrange
    client = TestClient(app)
    invalid_activity = "NonExistentActivity"
    email = "someone@example.com"
    
    # Act
    response = client.delete(
        f"/activities/{invalid_activity}/unregister?email={email}"
    )
    
    # Assert
    assert response.status_code == 404


def test_unregister_email_not_in_activity_returns_404():
    """
    Test that unregister with email not in activity returns 404.
    
    Arrange: Create TestClient with email not signed up
    Act: DELETE to unregister email that was never added
    Assert: Verify status 404
    """
    # Arrange
    client = TestClient(app)
    activity_name = "Science Olympiad"
    email_not_signed_up = "notamember@example.com"
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email_not_signed_up}"
    )
    
    # Assert
    assert response.status_code == 404


def test_unregister_with_empty_email():
    """
    Test that unregister with empty email is handled.
    
    Arrange: Create TestClient
    Act: DELETE with empty email
    Assert: Verify response (may accept empty string)
    """
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email="
    )
    
    # Assert - Could be 404 (not found) or accept empty string
    assert response.status_code in [404, 422, 400, 200]


def test_unregister_response_structure():
    """
    Test that unregister response has expected structure.
    
    Arrange: Create TestClient, signup participant
    Act: DELETE to unregister
    Assert: Verify response is valid JSON
    """
    # Arrange
    client = TestClient(app)
    activity_name = "Programming Class"
    email = "coder@example.com"
    
    # Signup first
    client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data


def test_unregister_does_not_affect_other_emails():
    """
    Test that unregistering one email doesn't affect other emails in same activity.
    
    Arrange: Create TestClient, signup two different emails
    Act: Unregister first email
    Assert: Second email still in participants
    """
    # Arrange
    client = TestClient(app)
    activity_name = "Gym Class"
    email1 = "student_a@example.com"
    email2 = "student_b@example.com"
    
    # Signup both emails
    client.post(f"/activities/{activity_name}/signup?email={email1}")
    client.post(f"/activities/{activity_name}/signup?email={email2}")
    
    # Act - Unregister first email
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email1}"
    )
    
    # Assert
    assert response.status_code == 200
    
    # Verify email1 is removed but email2 is still there
    activities_response = client.get("/activities")
    activities = activities_response.json()
    
    assert email1 not in activities[activity_name]["participants"]
    assert email2 in activities[activity_name]["participants"]


def test_unregister_signup_flow():
    """
    Test full flow: signup, then unregister, then can signup again.
    
    Arrange: Create TestClient, prepare email
    Act: Signup -> Unregister -> Signup
    Assert: Email flows correctly through all states
    """
    # Arrange
    client = TestClient(app)
    activity_name = "Soccer Team"
    email = "player@example.com"
    
    # Act 1 - Signup
    signup1 = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    assert signup1.status_code == 200
    
    # Verify email is in participants
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]
    
    # Act 2 - Unregister
    unregister = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )
    assert unregister.status_code == 200
    
    # Verify email is removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]
    
    # Act 3 - Signup again
    signup2 = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    assert signup2.status_code == 200
    
    # Verify email is back in participants
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]


# ============================================================================
# GET / redirect endpoint tests
# ============================================================================

def test_root_endpoint_redirects_to_static_index():
    """
    Test that GET / redirects to /static/index.html.
    
    Arrange: Create TestClient
    Act: GET / with follow_redirects=False to capture redirect
    Assert: Verify status 307 or 302 and Location header
    """
    # Arrange
    client = TestClient(app)
    
    # Act - Make request without following redirect
    response = client.get("/", follow_redirects=False)
    
    # Assert
    # Verify redirect status code (307 Temporary Redirect or 302 Found)
    assert response.status_code in [307, 302]
    
    # Verify Location header points to static index
    assert "location" in response.headers
    location = response.headers["location"]
    assert "index.html" in location or "static" in location


def test_root_endpoint_redirect_location():
    """
    Test that GET / redirect location is exactly /static/index.html or similar.
    
    Arrange: Create TestClient
    Act: GET / without following redirect
    Assert: Location header contains expected path
    """
    # Arrange
    client = TestClient(app)
    
    # Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code in [307, 302]
    location = response.headers.get("location", "")
    
    # The location should point to static/index.html
    assert "static" in location.lower() or "index.html" in location


def test_root_endpoint_returns_html_when_followed():
    """
    Test that following the redirect from GET / returns HTML.
    
    Arrange: Create TestClient
    Act: GET / with follow_redirects=True
    Assert: Response contains HTML content
    """
    # Arrange
    client = TestClient(app)
    
    # Act - Follow redirects
    response = client.get("/", follow_redirects=True)
    
    # Assert
    assert response.status_code == 200
    content = response.text
    
    # Should contain HTML content
    assert "<!DOCTYPE html>" in content or "<html" in content or ".html" in response.headers.get("content-type", "")


def test_root_endpoint_response_is_successful():
    """
    Test that following GET / redirect results in 200 OK.
    
    Arrange: Create TestClient
    Act: GET / with follow_redirects=True
    Assert: Final status is 200
    """
    # Arrange
    client = TestClient(app)
    
    # Act
    response = client.get("/", follow_redirects=True)
    
    # Assert
    assert response.status_code == 200


def test_root_endpoint_direct_access():
    """
    Test that GET / can be accessed (with redirect handling).
    
    Arrange: Create TestClient
    Act: GET /
    Assert: Request succeeds (either redirect or final response)
    """
    # Arrange
    client = TestClient(app)
    
    # Act
    response = client.get("/")
    
    # Assert - Should either redirect or succeed
    assert response.status_code in [200, 307, 302]
