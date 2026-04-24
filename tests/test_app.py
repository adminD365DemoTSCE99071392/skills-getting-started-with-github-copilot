"""Tests for the Mergington High School API FastAPI application."""

import pytest
from fastapi.testclient import TestClient


def test_get_root_redirect(client: TestClient):
    """Test that GET / redirects to /static/index.html."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.url.path == "/static/index.html"


def test_get_activities(client: TestClient):
    """Test that GET /activities returns all activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()

    # Should have 10 activities
    assert len(data) == 10

    # Check that all expected activities are present
    expected_activities = [
        "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
        "Tennis Club", "Art Studio", "Music Band", "Debate Club", "Science Club"
    ]
    for activity in expected_activities:
        assert activity in data

    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_success(client: TestClient):
    """Test successful signup for an activity."""
    response = client.post("/activities/Chess Club/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up test@example.com for Chess Club" in data["message"]

    # Verify the student was added
    response = client.get("/activities")
    activities = response.json()
    assert "test@example.com" in activities["Chess Club"]["participants"]


def test_signup_activity_not_found(client: TestClient):
    """Test signup for non-existent activity returns 404."""
    response = client.post("/activities/NonExistent Activity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_duplicate(client: TestClient):
    """Test that duplicate signup returns 400."""
    # First signup
    client.post("/activities/Programming Class/signup?email=duplicate@example.com")

    # Second signup should fail
    response = client.post("/activities/Programming Class/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student already signed up for this activity" in data["detail"]


def test_unregister_success(client: TestClient):
    """Test successful unregister from an activity."""
    # First signup
    client.post("/activities/Tennis Club/signup?email=unregister@example.com")

    # Then unregister
    response = client.delete("/activities/Tennis Club/unregister?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered unregister@example.com from Tennis Club" in data["message"]

    # Verify the student was removed
    response = client.get("/activities")
    activities = response.json()
    assert "unregister@example.com" not in activities["Tennis Club"]["participants"]


def test_unregister_activity_not_found(client: TestClient):
    """Test unregister from non-existent activity returns 404."""
    response = client.delete("/activities/NonExistent Activity/unregister?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_not_signed_up(client: TestClient):
    """Test unregister when student is not signed up returns 400."""
    response = client.delete("/activities/Art Studio/unregister?email=notsignedup@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student is not signed up for this activity" in data["detail"]