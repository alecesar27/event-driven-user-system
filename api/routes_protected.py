# api/routes_protected.py
from fastapi import APIRouter, Depends, HTTPException, status
from core.jwt_utils import decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

async def authenticated_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return payload

@router.get("/protected/onboarding-status")
@router.post("/protected/onboarding-status")
async def get_protected_status(user=Depends(authenticated_user)):
    return {"status": "Onboarding in progress", "user": user}
