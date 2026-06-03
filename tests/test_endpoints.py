"""
Integration tests for FastAPI endpoints.
Tests all three main endpoints: GET /activities, POST /signup, DELETE /unregister
"""

import pytest
from fastapi.testclient import TestClient
from app import app


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Test suite for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response contains all 9 activities
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Basketball Team" in data
        assert "Soccer Club" in data
        assert "Art Workshop" in data
        assert "Drama Club" in data
        assert "Debate Team" in data
        assert "Science Olympiad" in data

    def test_get_activities_returns_correct_structure(self, client):
        """Test that each activity has the required fields"""
        response = client.get("/activities")
        data = response.json()
        
        # Check that each activity has required fields
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)

    def test_get_activities_returns_correct_participants(self, client):
        """Test that activities have the correct initial participants"""
        response = client.get("/activities")
        data = response.json()
        
        # Verify Chess Club has initial participants
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
        assert len(data["Chess Club"]["participants"]) == 2


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newalex@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newalex@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_updates_participants(self, client):
        """Test that signup actually adds the participant to the activity"""
        new_email = "testuser@mergington.edu"
        
        # Verify user is not signed up initially
        response = client.get("/activities")
        activities_before = response.json()
        assert new_email not in activities_before["Chess Club"]["participants"]
        
        # Sign up
        client.post(
            "/activities/Chess Club/signup",
            params={"email": new_email}
        )
        
        # Verify user is now signed up
        response = client.get("/activities")
        activities_after = response.json()
        assert new_email in activities_after["Chess Club"]["participants"]
        assert len(activities_after["Chess Club"]["participants"]) == 3

    def test_signup_activity_not_found(self, client):
        """Test signup fails with 404 when activity doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_already_registered(self, client):
        """Test signup fails with 400 when student is already registered"""
        # Try to sign up someone who is already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_with_invalid_activity_name(self, client):
        """Test signup with various invalid activity names"""
        invalid_names = [
            "chess club",  # lowercase
            "CHESS CLUB",  # uppercase
            "Chess club",  # mixed case (different from original)
        ]
        
        for invalid_name in invalid_names:
            response = client.post(
                f"/activities/{invalid_name}/signup",
                params={"email": "student@mergington.edu"}
            )
            assert response.status_code == 404

    def test_signup_multiple_activities(self, client):
        """Test that a student can sign up for multiple different activities"""
        email = "newstudent@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify in both activities
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]

    def test_signup_preserves_other_activities(self, client):
        """Test that signing up for one activity doesn't affect others"""
        response_before = client.get("/activities")
        activities_before = response_before.json()
        original_soccer = activities_before["Soccer Club"]["participants"].copy()
        
        # Sign up for Chess Club
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        # Check that Soccer Club participants are unchanged
        response_after = client.get("/activities")
        activities_after = response_after.json()
        assert activities_after["Soccer Club"]["participants"] == original_soccer


class TestUnregisterFromActivity:
    """Test suite for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self, client):
        """Test successful unregister from an activity"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_unregister_updates_participants(self, client):
        """Test that unregister actually removes the participant"""
        email = "michael@mergington.edu"
        
        # Verify user is signed up initially
        response = client.get("/activities")
        activities_before = response.json()
        assert email in activities_before["Chess Club"]["participants"]
        initial_count = len(activities_before["Chess Club"]["participants"])
        
        # Unregister
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        
        # Verify user is no longer signed up
        response = client.get("/activities")
        activities_after = response.json()
        assert email not in activities_after["Chess Club"]["participants"]
        assert len(activities_after["Chess Club"]["participants"]) == initial_count - 1

    def test_unregister_activity_not_found(self, client):
        """Test unregister fails with 404 when activity doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_registered(self, client):
        """Test unregister fails with 400 when student is not registered"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_already_unregistered(self, client):
        """Test that unregistering a second time fails"""
        email = "michael@mergington.edu"
        
        # First unregister should succeed
        response1 = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second unregister should fail
        response2 = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "not registered" in response2.json()["detail"]

    def test_unregister_preserves_other_activities(self, client):
        """Test that unregistering from one activity doesn't affect others"""
        email = "sophia@mergington.edu"  # Initially in Programming Class and Debate Team
        
        # Get initial state
        response_before = client.get("/activities")
        activities_before = response_before.json()
        debate_before = activities_before["Debate Team"]["participants"].copy()
        
        # Unregister from Programming Class
        client.delete(
            "/activities/Programming Class/unregister",
            params={"email": email}
        )
        
        # Check that Debate Team is unchanged
        response_after = client.get("/activities")
        activities_after = response_after.json()
        assert activities_after["Debate Team"]["participants"] == debate_before

    def test_signup_after_unregister(self, client):
        """Test that a student can re-sign up after unregistering"""
        email = "michael@mergington.edu"
        
        # Unregister
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        
        # Sign up again
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify signed up
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]


class TestIntegrationScenarios:
    """Integration tests for complex scenarios involving multiple endpoints"""

    def test_full_signup_and_unregister_cycle(self, client):
        """Test a complete cycle: signup, verify, unregister, verify"""
        email = "newstudent@mergington.edu"
        activity = "Programming Class"
        
        # Verify not signed up
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify signed up
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify not signed up anymore
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]

    def test_multiple_students_signup_to_same_activity(self, client):
        """Test multiple students signing up for the same activity"""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(
                "/activities/Art Workshop/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all are signed up
        response = client.get("/activities")
        activity_participants = response.json()["Art Workshop"]["participants"]
        for email in emails:
            assert email in activity_participants

    def test_participant_count_consistency(self, client):
        """Test that participant counts remain consistent across operations"""
        activity = "Gym Class"
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Sign up 2 students
        client.post(
            f"/activities/{activity}/signup",
            params={"email": "user1@mergington.edu"}
        )
        client.post(
            f"/activities/{activity}/signup",
            params={"email": "user2@mergington.edu"}
        )
        
        response = client.get("/activities")
        current_count = len(response.json()[activity]["participants"])
        assert current_count == initial_count + 2
        
        # Unregister 1 student
        client.delete(
            f"/activities/{activity}/unregister",
            params={"email": "user1@mergington.edu"}
        )
        
        response = client.get("/activities")
        final_count = len(response.json()[activity]["participants"])
        assert final_count == initial_count + 1
