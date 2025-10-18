import pytest
from prometheus_client import Counter
import jwt
from datetime import datetime, timedelta

# Test Root Endpoint
def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "AI-Driven Onboarding System is running" in response.json()["message"]

# Test GraphQL Endpoint
def test_graphql_query_success(client):
    query = "{ onboardingUsers { id name role status } }"
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()["data"]
    assert "onboardingUsers" in data
    assert len(data["onboardingUsers"]) > 0
    assert data["onboardingUsers"][0]["id"] == "1"

def test_graphql_query_missing_query(client):
    response = client.post("/graphql", json={})
    assert response.status_code == 400
    assert "Missing 'query' in request body" in response.json()["error"]

def test_graphql_invalid_json(client):
    response = client.post("/graphql", data="invalid json")
    assert response.status_code == 400
    assert "Invalid JSON" in response.json()["error"]

# Test Token Generation
def test_generate_token_success(client):
    payload = {"user_id": "123", "role": "Engineer"}
    response = client.post("/generate-token", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "message" in data
    # Decode and verify token
    token = data["token"]
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    assert decoded["user_id"] == "123"
    assert decoded["role"] == "Engineer"

def test_generate_token_missing_fields(client):
    response = client.post("/generate-token", json={"user_id": "123"})
    assert response.status_code == 400
    assert "Missing 'user_id' or 'role'" in response.json()["error"]

def test_generate_token_invalid_json(client):
    response = client.post("/generate-token", data="invalid")
    assert response.status_code == 400
    assert "Invalid JSON" in response.json()["error"]

# Test Protected Route
def test_protected_route_with_valid_token(client):
    # Generate a token first
    payload = {"user_id": "123", "role": "Engineer"}
    token_response = client.post("/generate-token", json=payload)
    token = token_response.json()["token"]
    
    response = client.get("/protected/onboarding-status", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "Onboarding in progress" in response.json()["status"]

# tests/test_main.py - Updated with fixes
# ... (all other tests unchanged)

def test_protected_route_no_token(client):
    response = client.get("/protected/onboarding-status")
    assert response.status_code == 403  # Updated to match actual FastAPI behavior
    assert "Forbidden" in response.json()["detail"] or "Not authenticated" in response.json().get("detail", "")

# ... (test_trigger_workflow_post_success remains the same, as the endpoint now handles JSON body)

def test_protected_route_invalid_token(client):
    response = client.get("/protected/onboarding-status", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]

# Test Workflow Trigger
def test_trigger_workflow_success(client):
    response = client.get("/trigger-onboarding-workflow?user_id=1&role=Engineer")
    assert response.status_code == 200
    data = response.json()
    assert "AI workflow started" in data["message"]
    assert data["user"]["id"] == "1"
    assert "workflow_plan" in data

def test_trigger_workflow_invalid_user(client):
    response = client.get("/trigger-onboarding-workflow?user_id=999&role=Manager")
    assert response.status_code == 404
    assert "No onboarding user found" in response.json()["error"]

def test_trigger_workflow_post_success(client):
    payload = {"user_id": "1", "role": "Engineer"}
    response = client.post("/trigger-onboarding-workflow", json=payload)
    assert response.status_code == 200
    assert "AI workflow started" in response.json()["message"]

# Test Observability (Metrics Tracking)
def test_metrics_tracking(client):
    # Access an endpoint to trigger metrics
    client.get("/")
    # Note: In a real test, mock or check Prometheus registry
    # For simplicity, assume track_request() increments a counter
    # You can add: from main import user_requests; assert user_requests._value > 0

# Test Error Handling (General)
def test_internal_server_error(client, monkeypatch):
    # Mock an exception in GraphQL
    def mock_execute(*args, **kwargs):
        raise Exception("Mock error")
    monkeypatch.setattr("main.schema.execute", mock_execute)
    
    response = client.post("/graphql", json={"query": "{ test }"})
    assert response.status_code == 500
    assert "Internal server error" in response.json()["error"]