"""
Pytest configuration and shared fixtures for FastAPI backend tests.

Fixtures provide isolated test data and a TestClient for testing the API endpoints.
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
import src.app as app_module
from src.app import app


@pytest.fixture
def test_activities():
    """
    Provides deterministic test data for activities.
    
    Returns:
        dict: A dictionary of test activities with known participants.
    """
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["alice@test.edu", "bob@test.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["charlie@test.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and visual arts techniques",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": []
        }
    }


@pytest.fixture
def client(test_activities):
    """
    Provides a FastAPI TestClient with isolated test data.
    
    This fixture patches the app module's activities with test data before each test
    and restores the original data after the test completes.
    
    Args:
        test_activities: The test data fixture
        
    Returns:
        TestClient: A test client configured for the FastAPI app with test data.
    """
    # Store the original activities
    original_activities = deepcopy(app_module.activities)
    
    # Replace with test data (deep copy to ensure isolation)
    app_module.activities = deepcopy(test_activities)
    
    # Create and yield the client
    test_client = TestClient(app)
    yield test_client
    
    # Restore original activities after test
    app_module.activities = original_activities


# Helper fixtures for common test data access

@pytest.fixture
def existing_activity():
    """Returns an activity name that exists in test data."""
    return "Chess Club"


@pytest.fixture
def nonexistent_activity():
    """Returns an activity name that does not exist in test data."""
    return "Nonexistent Activity"


@pytest.fixture
def registered_email():
    """Returns an email that is already registered for an activity."""
    return "alice@test.edu"


@pytest.fixture
def unregistered_email():
    """Returns an email that is not registered for any activity."""
    return "david@test.edu"


@pytest.fixture
def valid_email():
    """Returns a valid test email."""
    return "test@test.edu"
