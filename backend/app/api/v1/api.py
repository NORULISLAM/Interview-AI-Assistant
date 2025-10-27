"""
Main API router for v1
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, resumes, sessions, asr, llm

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(asr.router, prefix="/asr", tags=["speech-recognition"])
api_router.include_router(llm.router, prefix="/llm", tags=["ai-suggestions"])
