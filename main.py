# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api.routes_onboarding import router as onboarding_router
from api.routes_graphql import router as graphql_router
from api.routes_protected import router as protected_router
from fastapi.responses import JSONResponse

app = FastAPI(title="AI-Driven Onboarding System")
app.include_router(onboarding_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui todos os routers
app.include_router(onboarding_router)
app.include_router(graphql_router)
app.include_router(protected_router)

@app.get("/")
async def root():
    return {"message": "AI-Driven Onboarding System is running"}

@app.exception_handler(Exception)
async def internal_error_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": "Internal server error"})
