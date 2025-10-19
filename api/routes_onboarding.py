from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import jwt
import json
from datetime import datetime, timedelta
from core.config import settings

router = APIRouter()

# Simulação de um pequeno banco de usuários
USERS_DB = {
    "1": {"id": "1", "name": "Alice", "role": "Engineer"},
    "2": {"id": "2", "name": "Bob", "role": "Manager"},
}


from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

# Função auxiliar para processar queries GraphQL (pode ser mockada nos testes)
def graphql_execute(query: str):
    # Aqui você pode integrar um schema real ou simular dados
    # Simulação de resposta para onboarding users
    return {
        "onboardingUsers": [
            {"id": "1", "name": "Alice", "role": "Engineer", "status": "in progress"},
            {"id": "2", "name": "Bob", "role": "Manager", "status": "completed"},
        ]
    }

@router.post("/graphql")
async def graphql_endpoint(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    query = body.get("query")
    if not query:
        return JSONResponse(status_code=400, content={"error": "Missing 'query' in request body"})

    try:
        # Executa a query via função auxiliar
        data = graphql_execute(query)
        return JSONResponse(status_code=200, content={"data": data})
    except Exception:
        # Captura qualquer erro interno
        return JSONResponse(status_code=500, content={"error": "Internal server error"})


    

@router.post("/generate-token")
async def generate_token(request: Request):
    """
    Gera um token JWT para um usuário específico.
    Deve retornar:
      - token (JWT)
      - message
    E tratar:
      - JSON inválido
      - Campos ausentes
    """
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    user_id = data.get("user_id")
    role = data.get("role")

    if not user_id or not role:
        return JSONResponse(status_code=400, content={"error": "Missing 'user_id' or 'role'"})

    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

    return JSONResponse(
        status_code=200,
        content={"token": token, "message": "Token generated successfully"}
    )


@router.get("/trigger-onboarding-workflow")
@router.post("/trigger-onboarding-workflow")
async def trigger_onboarding_workflow(request: Request):
    """
    Simula o início do workflow de onboarding.
    GET: query params
    POST: JSON body
    """
    if request.method == "GET":
        user_id = request.query_params.get("user_id")
        role = request.query_params.get("role")
    else:
        try:
            body = await request.json()
        except json.JSONDecodeError:
            return JSONResponse(status_code=400, content={"error": "Invalid JSON"})
        user_id = body.get("user_id")
        role = body.get("role")

    if not user_id or not role:
        return JSONResponse(status_code=400, content={"error": "Missing 'user_id' or 'role'"})

    user = USERS_DB.get(str(user_id))
    if not user:
        return JSONResponse(status_code=404, content={"error": "No onboarding user found"})

    workflow_plan = {
        "steps": ["Account Creation", "Access Provisioning", "Training Assignment"],
        "status": "In Progress",
    }

    message = f"AI workflow started for user {user['name']} with role {role}"

    return JSONResponse(
        status_code=200,
        content={
            "message": message,
            "user": user,
            "workflow_plan": workflow_plan,
        }
    )


# ⚙️ Rota protegida (para test_protected_route*)
@router.get("/protected/onboarding-status")
async def protected_onboarding_status(request: Request):
    """
    Simula uma rota protegida que requer JWT no header Authorization.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        scheme, token = auth_header.split(" ")
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authentication header")

    try:
        decoded = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return JSONResponse(
        status_code=200,
        content={
            "status": f"Onboarding in progress for user {decoded['user_id']} ({decoded['role']})"
        },
    )




