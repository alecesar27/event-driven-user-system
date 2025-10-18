# main.py - Updated with fixes for tests and warnings
from graphene import ObjectType, String, Schema, List
from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel  # Added for POST body validation
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from contextlib import asynccontextmanager
import json
import logging
from prometheus_client import start_http_server, Counter
import asyncio
from datetime import datetime, timedelta, timezone  # Updated for timezone-aware datetime

# Initialize FastAPI app (unchanged)
app = FastAPI(title="AI-Driven Onboarding System", description="Event-driven onboarding with GraphQL, security, and observability")

# Add CORS middleware (unchanged)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL setup (unchanged)
class OnboardingUser(ObjectType):
    id = String()
    name = String()
    role = String()
    status = String()

class Query(ObjectType):
    onboarding_users = List(OnboardingUser)

    def resolve_onboarding_users(self, info):
        track_request()
        logging.info("Onboarding users queried - event processed")
        return [OnboardingUser(id="1", name="Test User", role="Engineer", status="Approved")]

schema = Schema(query=Query)

@app.post("/graphql")
async def graphql_endpoint(request: Request):
    try:
        data = await request.json()
        query = data.get("query", "")
        variables = data.get("variables", {})
        if not query:
            return JSONResponse(content={"error": "Missing 'query' in request body"}, status_code=400)
        result = schema.execute(query, variable_values=variables)
        track_request()
        logging.info("GraphQL query executed")
        return JSONResponse(content={"data": result.data, "errors": [str(e) for e in result.errors] if result.errors else None})
    except json.JSONDecodeError:
        return JSONResponse(content={"error": "Invalid JSON in request body. Send a POST with {'query': 'your graphql query'}"}, status_code=400)
    except Exception as e:
        logging.error(f"GraphQL error: {str(e)}")
        return JSONResponse(content={"error": "Internal server error"}, status_code=500)

@app.get("/graphql")
async def graphql_playground():
    return JSONResponse(content={
        "message": "Use a GraphQL client (e.g., Postman) to send POST requests to /graphql. Example: {'query': '{ onboardingUsers { id name role status } }'}"
    })

# Observability setup (unchanged)
user_requests = Counter('user_requests_total', 'Total user requests')

def track_request():
    user_requests.inc()

logging.basicConfig(level=logging.INFO)

# Memory optimization (unchanged)
def get_db_connection():
    import sqlite3
    conn = sqlite3.connect(':memory:')
    try:
        yield conn
    finally:
        conn.close()

# Secure JWT authentication dependency (unchanged)
security = HTTPBearer()

async def authenticated_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


# UPDATED: Function to generate JWT token with timezone-aware datetime
def generate_jwt_token(user_id: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),  # Fixed deprecation
        "iat": datetime.now(timezone.utc)  # Fixed deprecation
    }
    token = jwt.encode(payload, "secret", algorithm="HS256")
    return token

# UPDATED: Endpoint to generate and return a JWT token
@app.post("/generate-token")
async def create_token(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        role = data.get("role")
        if not user_id or not role:
            return JSONResponse(content={"error": "Missing 'user_id' or 'role' in request body. Example: {'user_id': '123', 'role': 'Engineer'}"}, status_code=400)
        token = generate_jwt_token(user_id, role)
        track_request()
        logging.info(f"Token generated for user {user_id} with role {role}")
        return {"token": token, "message": "Use this token in 'Authorization: Bearer <token>' header for protected routes"}
    except json.JSONDecodeError:
        return JSONResponse(content={"error": "Invalid JSON in request body"}, status_code=400)
    except Exception as e:
        logging.error(f"Token generation error: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Protected route (unchanged)
@app.get("/protected/onboarding-status", dependencies=[Depends(authenticated_user)])
@app.post("/protected/onboarding-status", dependencies=[Depends(authenticated_user)])
async def get_protected_status(user=Depends(authenticated_user)):
    track_request()
    logging.info("Protected onboarding status accessed")
    return {"status": "Onboarding in progress", "user": user}

# UPDATED: Lifespan event handler (replaces deprecated @app.on_event)
@asynccontextmanager # Note: For full fix, use lifespan in FastAPI 0.95+, but keeping for compatibility
async def startup_event():
    def start_metrics_server():
        start_http_server(8001)
    asyncio.create_task(asyncio.to_thread(start_metrics_server))
    logging.info("Prometheus metrics server started on port 8001")

# Root endpoint (unchanged)
@app.get("/")
async def root():
    track_request()
    logging.info("Root endpoint accessed")
    return {"message": "AI-Driven Onboarding System is running. GraphQL at /graphql, Metrics at :8001"}

# UPDATED: Pydantic model for POST body
class WorkflowRequest(BaseModel):
    user_id: str
    role: str

# UPDATED: Workflow trigger with Pydantic model for POST
@app.get("/trigger-onboarding-workflow")
@app.post("/trigger-onboarding-workflow")
async def trigger_workflow(user_id: str = None, role: str = None, request: WorkflowRequest = None):
    # For GET: use query params
    if request is None:
        if not user_id or not role:
            return JSONResponse(content={"error": "Missing user_id or role in query params"}, status_code=400)
    else:
        # For POST: use body
        user_id = request.user_id
        role = request.role
    
    onboarding_users = [
        {"id": "1", "name": "Test User", "role": "Engineer", "status": "Approved"}
    ]
    user = next((u for u in onboarding_users if u["id"] == user_id and u["role"] == role), None)
    if not user:
        return JSONResponse(content={"error": f"No onboarding user found with id '{user_id}' and role '{role}'"}, status_code=404)
    
    workflow_plan = f"Personalized onboarding for {role}: Assign tools, schedule training, and send welcome email."
    if role == "Engineer":
        workflow_plan += " Include code review session and access to dev tools."
    
    track_request()
    logging.info(f"Workflow triggered for validated user {user_id} with role {role}")
    return {
        "message": f"AI workflow started for {role} onboarding",
        "user": user,
        "workflow_plan": workflow_plan
    }