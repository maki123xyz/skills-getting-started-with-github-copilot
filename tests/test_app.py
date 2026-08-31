"""
Comprehensive tests for the Mergington High School Activities API.

Tests follow the AAA (Arrange-Act-Assert) pattern:
- ARRANGE: Set up test data and preconditions via fixtures
- ACT: Execute the API request being tested
- ASSERT: Verify the HTTP response and state changes
"""

import pytest


class TestRootRedirect:
    """Tests for the GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """
        ARRANGE: Client is ready
        ACT: Make GET request to root endpoint
        ASSERT: Response is a redirect to /static/index.html
        """
        # ACT
        response = client.get("/", follow_redirects=False)
        
        # ASSERT
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        ARRANGE: Activities are loaded in the test app
        ACT: Make GET request to /activities
        ASSERT: Response contains all activities with correct structure
        """
        # ACT
        response = client.get("/activities")
        
        # ASSERT
        assert response.status_code == 200
        activities = response.json()
        
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Art Studio" in activities
        assert len(activities) == 3

    def test_get_activities_includes_participants(self, client):
        """
        ARRANGE: Activities with known participants exist
        ACT: Make GET request to /activities
        ASSERT: Response includes participants list for each activity
        """
        # ACT
        response = client.get("/activities")
        
        # ASSERT
        assert response.status_code == 200
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
        assert len(chess_club["participants"]) == 2
        assert "alice@test.edu" in chess_club["participants"]
        assert "bob@test.edu" in chess_club["participants"]

    def test_get_activities_includes_all_required_fields(self, client):
        """
        ARRANGE: Activities exist with all data
        ACT: Make GET request to /activities
        ASSERT: Each activity has description, schedule, max_participants, and participants
        """
        # ACT
        response = client.get("/activities")
        
        # ASSERT
        assert response.status_code == 200
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client, existing_activity, unregistered_email):
        """
        ARRANGE: An existing activity and an unregistered email
        ACT: POST request to signup endpoint
        ASSERT: Response is 200, message confirms signup, participant is added to list
        """
        # ARRANGE
        activity_name = existing_activity
        email = unregistered_email
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            params={"email": email}
        )
        
        # ASSERT - HTTP response
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        
        # ASSERT - state change: verify participant was added
        activities_after = client.get("/activities").json()
        assert email in activities_after[activity_name]["participants"]

    def test_signup_nonexistent_activity(self, client, nonexistent_activity, valid_email):
        """
        ARRANGE: A nonexistent activity and a valid email
        ACT: POST request to signup for nonexistent activity
        ASSERT: Response is 404 with appropriate error message
        """
        # ARRANGE
        activity_name = nonexistent_activity
        email = valid_email
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_duplicate_email(self, client, existing_activity, registered_email):
        """
        ARRANGE: An existing activity and an email already registered for it
        ACT: POST request to signup with duplicate email
        ASSERT: Response is 400 indicating student already signed up
        """
        # ARRANGE
        activity_name = existing_activity
        email = registered_email  # alice@test.edu is already in Chess Club
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_missing_email_parameter(self, client, existing_activity):
        """
        ARRANGE: A signup request without email parameter
        ACT: POST request without email query parameter
        ASSERT: Response is 422 validation error
        """
        # ARRANGE
        activity_name = existing_activity
        
        # ACT
        response = client.post(f"/activities/{activity_name}/signup")
        
        # ASSERT
        assert response.status_code == 422

    def test_signup_updates_participant_count(self, client, existing_activity, unregistered_email):
        """
        ARRANGE: An activity with known participant count and unregistered email
        ACT: Signup the email and fetch activities
        ASSERT: Participant count increased by 1
        """
        # ARRANGE
        activity_name = existing_activity
        email = unregistered_email
        activities_before = client.get("/activities").json()
        count_before = len(activities_before[activity_name]["participants"])
        
        # ACT
        client.post(
            f"/activities/{activity_name}/signup?email={email}",
            params={"email": email}
        )
        
        # ASSERT
        activities_after = client.get("/activities").json()
        count_after = len(activities_after[activity_name]["participants"])
        assert count_after == count_before + 1


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client, existing_activity, registered_email):
        """
        ARRANGE: An existing activity and a registered email
        ACT: DELETE request to unregister endpoint
        ASSERT: Response is 200, message confirms unregistration, participant removed from list
        """
        # ARRANGE
        activity_name = existing_activity
        email = registered_email  # alice@test.edu is in Chess Club
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}",
            params={"email": email}
        )
        
        # ASSERT - HTTP response
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        
        # ASSERT - state change: verify participant was removed
        activities_after = client.get("/activities").json()
        assert email not in activities_after[activity_name]["participants"]

    def test_unregister_nonexistent_activity(self, client, nonexistent_activity, valid_email):
        """
        ARRANGE: A nonexistent activity and a valid email
        ACT: DELETE request to unregister from nonexistent activity
        ASSERT: Response is 404 with appropriate error message
        """
        # ARRANGE
        activity_name = nonexistent_activity
        email = valid_email
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_not_registered_email(self, client, existing_activity, unregistered_email):
        """
        ARRANGE: An existing activity and an email not registered for it
        ACT: DELETE request to unregister with unregistered email
        ASSERT: Response is 400 indicating student not registered
        """
        # ARRANGE
        activity_name = existing_activity
        email = unregistered_email
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()

    def test_unregister_missing_email_parameter(self, client, existing_activity):
        """
        ARRANGE: An unregister request without email parameter
        ACT: DELETE request without email query parameter
        ASSERT: Response is 422 validation error
        """
        # ARRANGE
        activity_name = existing_activity
        
        # ACT
        response = client.delete(f"/activities/{activity_name}/unregister")
        
        # ASSERT
        assert response.status_code == 422

    def test_unregister_updates_participant_count(self, client, existing_activity, registered_email):
        """
        ARRANGE: An activity with known participant count including registered email
        ACT: Unregister the email and fetch activities
        ASSERT: Participant count decreased by 1
        """
        # ARRANGE
        activity_name = existing_activity
        email = registered_email
        activities_before = client.get("/activities").json()
        count_before = len(activities_before[activity_name]["participants"])
        
        # ACT
        client.delete(
            f"/activities/{activity_name}/unregister?email={email}",
            params={"email": email}
        )
        
        # ASSERT
        activities_after = client.get("/activities").json()
        count_after = len(activities_after[activity_name]["participants"])
        assert count_after == count_before - 1


class TestIntegration:
    """Integration tests for multi-step workflows."""

    def test_signup_then_unregister_sequence(self, client, existing_activity, unregistered_email):
        """
        ARRANGE: An activity and unregistered email
        ACT: Signup, verify participant added, then unregister, verify participant removed
        ASSERT: Participant appears after signup, disappears after unregister
        """
        # ARRANGE
        activity_name = existing_activity
        email = unregistered_email
        
        # ACT 1: Signup
        response_signup = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            params={"email": email}
        )
        assert response_signup.status_code == 200
        
        # ASSERT 1: Participant added
        activities_after_signup = client.get("/activities").json()
        assert email in activities_after_signup[activity_name]["participants"]
        
        # ACT 2: Unregister
        response_unregister = client.delete(
            f"/activities/{activity_name}/unregister?email={email}",
            params={"email": email}
        )
        assert response_unregister.status_code == 200
        
        # ASSERT 2: Participant removed
        activities_after_unregister = client.get("/activities").json()
        assert email not in activities_after_unregister[activity_name]["participants"]

    def test_multiple_signups_independent(self, client, existing_activity):
        """
        ARRANGE: An activity and multiple unregistered emails
        ACT: Signup multiple emails to same activity
        ASSERT: All emails are added without affecting other activities
        """
        # ARRANGE
        activity_name = existing_activity
        emails = ["eve@test.edu", "frank@test.edu", "grace@test.edu"]
        
        # ACT: Signup all emails
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # ASSERT: All emails in participants list
        activities = client.get("/activities").json()
        for email in emails:
            assert email in activities[activity_name]["participants"]
        
        # ASSERT: Other activities unaffected
        programming_class = activities["Programming Class"]
        assert len(programming_class["participants"]) == 1  # Still only charlie@test.edu
