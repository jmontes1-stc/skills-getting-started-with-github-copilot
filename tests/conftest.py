"""
Pytest configuration and fixtures for FastAPI tests.
Provides test client and sample data for testing.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def test_client():
    """
    Provide a FastAPI TestClient for the application.
    """
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """
    Provide a fresh copy of the activities data for each test.
    This ensures test isolation - modifications in one test won't affect others.
    """
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice basketball skills and compete in interschool games",
            "schedule": "Mondays and Thursdays, 5:00 PM - 7:00 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu", "maria@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Train for soccer matches and improve teamwork",
            "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["jordan@mergington.edu", "nina@mergington.edu"]
        },
        "Art Workshop": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["lily@mergington.edu", "noah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Rehearse plays and perform theatrical productions",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": ["ella@mergington.edu", "ethan@mergington.edu"]
        },
        "Debate Team": {
            "description": "Prepare for debate competitions and practice public speaking",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["sophia@mergington.edu", "liam@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Work on science and engineering challenges for tournaments",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 14,
            "participants": ["olivia@mergington.edu", "mason@mergington.edu"]
        }
    }


@pytest.fixture(autouse=True)
def reset_activities(fresh_activities):
    """
    Reset the global activities dictionary before each test.
    This fixture is automatically used by all tests (autouse=True) to ensure
    each test starts with clean, consistent data.
    """
    # Clear and repopulate the global activities dict
    activities.clear()
    activities.update(fresh_activities)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(fresh_activities)
