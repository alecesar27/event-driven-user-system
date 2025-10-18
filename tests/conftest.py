import pytest
from fastapi.testclient import TestClient

# Import app with explicit path handling
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # Add project root
from main import app

@pytest.fixture
def client():
    """Fixture for FastAPI TestClient."""
    return TestClient(app)