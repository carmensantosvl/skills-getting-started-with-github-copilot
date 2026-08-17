"""
Tests for GET /activities endpoint using AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestGetActivities:
    """Test suite for the GET /activities endpoint."""

    def test_get_activities_returns_200_status(self, client):
        """
        ARRANGE: No additional setup needed (client fixture provided)
        ACT: Make GET request to /activities
        ASSERT: Verify response status is 200
        """
        # ACT
        response = client.get("/activities")
        
        # ASSERT
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, client):
        """
        ARRANGE: Client fixture is set up with 3 activities
        ACT: Make GET request to /activities
        ASSERT: Verify all activities are returned
        """
        # ACT
        response = client.get("/activities")
        data = response.json()
        
        # ASSERT
        assert len(data) == 3
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_returns_required_fields(self, client):
        """
        ARRANGE: Client fixture with activities
        ACT: Make GET request to /activities
        ASSERT: Verify each activity has required fields
        """
        # ACT
        response = client.get("/activities")
        data = response.json()
        
        # ASSERT
        required_fields = {"description", "schedule", "max_participants", "participants"}
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data, dict)
            assert required_fields.issubset(activity_data.keys())

    def test_get_activities_participants_are_populated(self, client):
        """
        ARRANGE: Client fixture with activities that have existing participants
        ACT: Make GET request to /activities
        ASSERT: Verify participants lists are populated correctly
        """
        # ACT
        response = client.get("/activities")
        data = response.json()
        
        # ASSERT
        assert isinstance(data["Chess Club"]["participants"], list)
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
        
        assert len(data["Programming Class"]["participants"]) == 2
        assert len(data["Gym Class"]["participants"]) == 2

    def test_get_activities_response_format(self, client):
        """
        ARRANGE: Client fixture with activities
        ACT: Make GET request to /activities
        ASSERT: Verify response structure and field types
        """
        # ACT
        response = client.get("/activities")
        data = response.json()
        
        # ASSERT
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            assert activity_data["max_participants"] > 0
