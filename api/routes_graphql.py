# api/routes_graphql.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from graphene import ObjectType, String, Schema, List
import json
import logging

router = APIRouter()

class OnboardingUser(ObjectType):
    id = String()
    name = String()
    role = String()
    status = String()

class Query(ObjectType):
    onboarding_users = List(OnboardingUser)

    def resolve_onboarding_users(self, info):
        logging.info("GraphQL: onboarding_users queried")
        return [OnboardingUser(id="1", name="Test User", role="Engineer", status="Approved")]

schema = Schema(query=Query)

@router.post("/graphql")
async def graphql_endpoint(request: Request):
    try:
        data = await request.json()
        query = data.get("query")
        variables = data.get("variables", {})
        if not query:
            return JSONResponse(content={"error": "Missing query"}, status_code=400)
        result = schema.execute(query, variable_values=variables)
        return JSONResponse(content={"data": result.data})
    except json.JSONDecodeError:
        return JSONResponse(content={"error": "Invalid JSON"}, status_code=400)
