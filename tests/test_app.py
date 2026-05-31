import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


class TestActivities:
    def test_get_activities_returns_all_activities(self):
        # Arrange
        expected_activity = "Chess Club"

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert expected_activity in data
        assert "description" in data[expected_activity]
        assert "participants" in data[expected_activity]


class TestSignup:
    def test_signup_for_activity_adds_participant(self):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
        assert email in activities[activity_name]["participants"]

    def test_signup_for_activity_duplicate_returns_400(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"

    def test_signup_for_unknown_activity_returns_404(self):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestRemoveParticipant:
    def test_remove_participant_unregisters_student(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
        assert email not in activities[activity_name]["participants"]

    def test_remove_nonexistent_participant_returns_404(self):
        # Arrange
        activity_name = "Chess Club"
        email = "missingstudent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    def test_remove_participant_from_unknown_activity_returns_404(self):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
