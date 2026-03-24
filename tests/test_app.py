import pytest
from fastapi.testclient import TestClient
import urllib.parse
from src.app import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

class TestActivitiesAPI:
    """Test suite for the Activities API endpoints."""

    def test_get_activities_success(self, client):
        """Test retrieving all activities successfully."""
        # Arrange
        # (client fixture provides the test client)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        # Check that we have expected activities
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_root_redirect(self, client):
        """Test that root path redirects to static index."""
        # Arrange
        # (client fixture provides the test client)

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"

    def test_signup_success(self, client):
        """Test successful signup for an activity."""
        # Arrange
        email = "test-student@mergington.edu"
        activity = "Programming Class"
        activity_encoded = urllib.parse.quote(activity)

        # Act
        response = client.post(f"/activities/{activity_encoded}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Signed up {email} for {activity}" == data["message"]

        # Verify the participant was added
        response_check = client.get("/activities")
        activities_data = response_check.json()
        assert email in activities_data[activity]["participants"]

    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity."""
        # Arrange
        email = "test-student@mergington.edu"
        activity = "Nonexistent Activity"
        activity_encoded = urllib.parse.quote(activity)

        # Act
        response = client.post(f"/activities/{activity_encoded}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" == data["detail"]

    def test_signup_already_signed_up(self, client):
        """Test signup when student is already signed up."""
        # Arrange
        email = "emma@mergington.edu"  # Already in Programming Class
        activity = "Programming Class"
        activity_encoded = urllib.parse.quote(activity)

        # Act
        response = client.post(f"/activities/{activity_encoded}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student is already signed up for this activity" == data["detail"]

    def test_delete_participant_success(self, client):
        """Test successful deletion of a participant."""
        # Arrange
        email = "daniel@mergington.edu"  # In Chess Club
        activity = "Chess Club"
        activity_encoded = urllib.parse.quote(activity)

        # Act
        response = client.delete(f"/activities/{activity_encoded}/participants/{urllib.parse.quote(email)}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Unregistered {email} from {activity}" == data["message"]

        # Verify the participant was removed
        response_check = client.get("/activities")
        activities_data = response_check.json()
        assert email not in activities_data[activity]["participants"]

    def test_delete_participant_not_found(self, client):
        """Test deletion of non-existent participant."""
        # Arrange
        email = "nonexistent@mergington.edu"
        activity = "Chess Club"
        activity_encoded = urllib.parse.quote(activity)

        # Act
        response = client.delete(f"/activities/{activity_encoded}/participants/{urllib.parse.quote(email)}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Participant not found in this activity" == data["detail"]

    def test_delete_activity_not_found(self, client):
        """Test deletion from non-existent activity."""
        # Arrange
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"
        activity_encoded = urllib.parse.quote(activity)

        # Act
        response = client.delete(f"/activities/{activity_encoded}/participants/{urllib.parse.quote(email)}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" == data["detail"]