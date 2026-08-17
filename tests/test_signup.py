"""
Tests for POST /activities/{activity_name}/signup endpoint using AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestSignupForActivity:
    """Test suite for the POST /activities/{activity_name}/signup endpoint."""

    def test_valid_signup_returns_200(self, client):
        """
        ARRANGE: Client fixture with activities, prepare valid email
        ACT: Make POST request with valid activity and email
        ASSERT: Verify response status is 200
        """
        # ARRANGE
        activity = "Chess Club"
        email = "alice@mergington.edu"
        
        # ACT
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # ASSERT
        assert response.status_code == 200

    def test_valid_signup_adds_participant(self, client):
        """
        ARRANGE: Client fixture with activities, prepare valid email
        ACT: Make POST request to signup
        ASSERT: Verify email is added to participants list
        """
        # ARRANGE
        activity = "Chess Club"
        email = "alice@mergington.edu"
        
        # ACT
        response = client.post(f"/activities/{activity}/signup?email={email}")
        response_data = response.json()
        
        # Get updated activities to verify the change
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        # ASSERT
        assert response.status_code == 200
        assert "message" in response_data
        assert email in activities_data[activity]["participants"]

    def test_signup_returns_success_message(self, client):
        """
        ARRANGE: Client fixture with activities, prepare valid email
        ACT: Make POST request to signup
        ASSERT: Verify success message format
        """
        # ARRANGE
        activity = "Programming Class"
        email = "bob@mergington.edu"
        
        # ACT
        response = client.post(f"/activities/{activity}/signup?email={email}")
        data = response.json()
        
        # ASSERT
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]

    def test_invalid_activity_returns_404(self, client):
        """
        ARRANGE: Client fixture with activities, prepare non-existent activity name
        ACT: Make POST request with invalid activity
        ASSERT: Verify response status is 404
        """
        # ARRANGE
        activity = "Non-Existent Activity"
        email = "test@mergington.edu"
        
        # ACT
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # ASSERT
        assert response.status_code == 404

    def test_invalid_activity_returns_error_message(self, client):
        """
        ARRANGE: Client fixture with activities, prepare non-existent activity name
        ACT: Make POST request with invalid activity
        ASSERT: Verify error message is returned
        """
        # ARRANGE
        activity = "Non-Existent Activity"
        email = "test@mergington.edu"
        
        # ACT
        response = client.post(f"/activities/{activity}/signup?email={email}")
        data = response.json()
        
        # ASSERT
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_duplicate_signup_prevention(self, client):
        """
        ARRANGE: Client fixture, student already exists in activity
        ACT: Try to signup same student to same activity twice
        ASSERT: Verify duplicate signup is rejected with 409 Conflict
        """
        # ARRANGE
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club
        
        # Get initial participant count
        response_first = client.get("/activities")
        activities_before = response_first.json()
        original_count = len(activities_before[activity]["participants"])
        
        # ACT - Try to signup (should be rejected)
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # ASSERT
        # Duplicate signup should return 409 Conflict
        assert response.status_code == 409
        assert "already signed up" in response.json()["detail"]
        
        # Verify participant count didn't increase
        response_after = client.get("/activities")
        activities_after = response_after.json()
        new_count = len(activities_after[activity]["participants"])
        assert new_count == original_count

    def test_case_sensitive_activity_name(self, client):
        """
        ARRANGE: Client fixture with 'Chess Club' activity (exact case)
        ACT: Try to signup with different case 'chess club'
        ASSERT: Verify activity name is case-sensitive (should fail if different case)
        """
        # ARRANGE
        correct_activity = "Chess Club"
        wrong_case_activity = "chess club"
        email = "test@mergington.edu"
        
        # ACT
        response = client.post(f"/activities/{wrong_case_activity}/signup?email={email}")
        
        # ASSERT
        # Activity name should be case-sensitive, so lowercase should not match
        assert response.status_code == 404

    def test_max_participants_limit(self, client):
        """
        ARRANGE: Client fixture, fill activity to max capacity
        ACT: Try to signup beyond max_participants limit
        ASSERT: Verify signup is rejected with 400 when at capacity
        """
        # ARRANGE
        activity = "Gym Class"
        # Get current max and participant count
        response_get = client.get("/activities")
        gym_class = response_get.json()[activity]
        max_participants = gym_class["max_participants"]
        current_participants = len(gym_class["participants"])
        
        # Sign up new students until we reach capacity
        for i in range(max_participants - current_participants):
            email = f"student{i}@mergington.edu"
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # ACT - Try to signup beyond capacity
        overflow_email = "overflow@mergington.edu"
        response_overflow = client.post(f"/activities/{activity}/signup?email={overflow_email}")
        
        # ASSERT
        # Should return 400 (Bad Request) when at capacity
        assert response_overflow.status_code == 400
        assert "maximum capacity" in response_overflow.json()["detail"]
        
        # Verify overflow student was not added
        response_check = client.get("/activities")
        final_participants = response_check.json()[activity]["participants"]
        assert overflow_email not in final_participants
        assert len(final_participants) == max_participants

    def test_multiple_valid_signups(self, client):
        """
        ARRANGE: Client fixture with activities
        ACT: Sign up multiple different students to same activity
        ASSERT: Verify all signups succeed and participants increase
        """
        # ARRANGE
        activity = "Programming Class"
        emails = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]
        
        # Get initial count
        response_before = client.get("/activities")
        initial_count = len(response_before.json()[activity]["participants"])
        
        # ACT - Sign up multiple students
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # ASSERT - Verify all were added
        response_after = client.get("/activities")
        final_participants = response_after.json()[activity]["participants"]
        final_count = len(final_participants)
        
        assert final_count == initial_count + len(emails)
        for email in emails:
            assert email in final_participants
