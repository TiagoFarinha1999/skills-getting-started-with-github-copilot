"""
FastAPI endpoint tests using the AAA (Arrange-Act-Assert) testing pattern.

Each test follows the AAA pattern:
- Arrange: Set up the test data and client
- Act: Make the HTTP request to the endpoint
- Assert: Verify the response status, body, and state
"""

import pytest


class TestRoot:
    """Tests for the root endpoint GET /"""

    def test_root_redirects_to_static_index(self, client):
        """
        Test that the root endpoint redirects to /static/index.html
        
        Arrange: Client is ready (from fixture)
        Act: Make GET request to /
        Assert: Verify redirect status and location header
        """
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """
        Test that GET /activities returns all available activities with correct structure
        
        Arrange: Client is ready
        Act: Make GET request to /activities
        Assert: Verify response contains all expected activities
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Verify all activities are present
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        
        # Verify activity structure
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_get_activities_includes_participants(self, client):
        """
        Test that activities include the current participants list
        
        Arrange: Client is ready
        Act: Make GET request to /activities
        Assert: Verify participants are returned in response
        """
        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client):
        """
        Test successful student signup for an activity
        
        Arrange: Prepare email and activity name
        Act: Make POST request to signup endpoint
        Assert: Verify 200 response and participant is added
        """
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert email in data["message"]
        
        # Verify participant is added to activity
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]

    def test_signup_activity_not_found(self, client):
        """
        Test signup fails when activity doesn't exist
        
        Arrange: Prepare email and invalid activity name
        Act: Make POST request with non-existent activity
        Assert: Verify 404 error response
        """
        # Arrange
        email = "student@mergington.edu"
        activity = "NonExistentActivity"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_registration(self, client):
        """
        Test signup fails when student is already registered
        
        Arrange: Get an existing participant from an activity
        Act: Try to signup the same student again
        Assert: Verify 400 error response for duplicate registration
        """
        # Arrange
        activity = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": existing_email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_different_activities(self, client):
        """
        Test that a student can signup for multiple different activities
        
        Arrange: Prepare student email
        Act: Signup for multiple activities sequentially
        Assert: Verify student appears in all activity rosters
        """
        # Arrange
        email = "versatile@mergington.edu"

        # Act & Assert - signup for first activity
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200

        # Act & Assert - signup for second activity
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 200

        # Verify student is in both activities
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self, client):
        """
        Test successful unregistration of a student from an activity
        
        Arrange: Get existing participant and activity
        Act: Make DELETE request to unregister endpoint
        Assert: Verify 200 response and participant is removed
        """
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Existing participant

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify participant is removed
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]

    def test_unregister_activity_not_found(self, client):
        """
        Test unregister fails when activity doesn't exist
        
        Arrange: Prepare email and invalid activity name
        Act: Make DELETE request with non-existent activity
        Assert: Verify 404 error response
        """
        # Arrange
        email = "student@mergington.edu"
        activity = "NonExistentActivity"

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_not_registered(self, client):
        """
        Test unregister fails when student is not registered for the activity
        
        Arrange: Prepare email that is not in any activity
        Act: Try to unregister non-existent participant
        Assert: Verify 400 error response
        """
        # Arrange
        email = "notregistered@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_from_multiple_activities(self, client):
        """
        Test that a student can be independently unregistered from each activity
        
        Arrange: Signup student for multiple activities
        Act: Unregister from one activity
        Assert: Verify student is removed from one activity but remains in others
        """
        # Arrange
        email = "multiactivity@mergington.edu"
        
        # Setup: sign up for two activities
        client.post("/activities/Chess Club/signup", params={"email": email})
        client.post("/activities/Programming Class/signup", params={"email": email})

        # Act - unregister from one activity
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        
        # Verify removed from Chess Club but still in Programming Class
        activities = client.get("/activities").json()
        assert email not in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]
