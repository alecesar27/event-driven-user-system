# app/onboarding_service.py
from graphene import ObjectType, String, Schema, List
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
import jwt  # For identity management
import json

app = FastAPI()

# Define GraphQL types with Graphene (unchanged)
class OnboardingUser(ObjectType):
    id = String()
    name = String()  # Kept simple; adapt fields as needed

class Query(ObjectType):
    onboarding_users = List(OnboardingUser)

    def resolve_onboarding_users(self, info):
        # Simulate fetching users
        return [OnboardingUser(id="1", name="Test User")]

# Create Graphene schema (unchanged)
schema = Schema(query=Query)

# Manual GraphQL route for FastAPI (replaces GraphQLApp)
@app.post("/graphql")
async def graphql_endpoint(request: Request):
    data = await request.json()
    query = data.get("query", "")
    variables = data.get("variables", {})
    result = schema.execute(query, variable_values=variables)
    return JSONResponse(content={"data": result.data, "errors": [str(e) for e in result.errors] if result.errors else None})

# Optional: GET route for GraphiQL (GraphQL playground) - useful for testing
@app.get("/graphql")
async def graphql_playground():
    return JSONResponse(content={
        "message": "Use a GraphQL client like Postman or Insomnia to query /graphql with POST requests."
    })

# Memory optimization: Use context managers for resources (unchanged)
def get_db_connection():
    import sqlite3
    conn = sqlite3.connect(':memory:')
    try:
        yield conn
    finally:
        conn.close()

# Secure endpoint with identity (JWT authentication) - unchanged
async def authenticated_user(token: str = Depends()):
    try:
        return jwt.decode(token, "secret", algorithms=["HS256"])
    except:
        raise Exception("Unauthorized")