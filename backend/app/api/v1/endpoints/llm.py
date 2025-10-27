"""
LLM (AI Suggestions) endpoints
"""
import json
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import openai
from openai import AsyncOpenAI

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User, Suggestion, TranscriptSegment, Resume
from app.schemas.user import SuggestionResponse, SuggestionCreate
from app.services.llm_service import LLMService
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None


@router.post("/suggestions", response_model=SuggestionResponse)
async def generate_suggestion(
    suggestion_data: SuggestionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate AI suggestion based on context"""
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API not configured"
        )
    
    # Get recent transcript segments
    result = await db.execute(
        select(TranscriptSegment)
        .where(TranscriptSegment.session_id == suggestion_data.session_id)
        .order_by(TranscriptSegment.created_at.desc())
        .limit(10)
    )
    recent_segments = result.scalars().all()
    
    # Get user's resume for personalization
    resume_result = await db.execute(
        select(Resume)
        .where(
            Resume.user_id == current_user.id,
            Resume.is_active == True
        )
        .order_by(Resume.uploaded_at.desc())
        .limit(1)
    )
    resume = resume_result.scalar_one_or_none()
    
    # Generate suggestion
    llm_service = LLMService(client, db)
    
    try:
        suggestion_text = await llm_service.generate_suggestion(
            recent_segments,
            resume,
            suggestion_data.suggestion_type
        )
        
        # Create suggestion record
        suggestion = Suggestion(
            session_id=suggestion_data.session_id,
            segment_id=suggestion_data.segment_id,
            content=suggestion_text,
            suggestion_type=suggestion_data.suggestion_type,
            llm_model=settings.OPENAI_MODEL
        )
        
        db.add(suggestion)
        await db.commit()
        await db.refresh(suggestion)
        
        return suggestion
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate suggestion: {str(e)}"
        )


@router.get("/suggestions/{session_id}", response_model=List[SuggestionResponse])
async def get_session_suggestions(
    session_id: int,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get suggestions for a session"""
    
    result = await db.execute(
        select(Suggestion)
        .where(Suggestion.session_id == session_id)
        .order_by(Suggestion.created_at.desc())
        .limit(limit)
    )
    suggestions = result.scalars().all()
    
    return suggestions


@router.patch("/suggestions/{suggestion_id}/feedback")
async def update_suggestion_feedback(
    suggestion_id: int,
    accepted: Optional[bool] = None,
    rating: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update suggestion feedback"""
    
    result = await db.execute(
        select(Suggestion).where(Suggestion.id == suggestion_id)
    )
    suggestion = result.scalar_one_or_none()
    
    if not suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found"
        )
    
    # Update feedback
    if accepted is not None:
        suggestion.accepted = accepted
        if accepted:
            suggestion.dismissed = False
    
    if rating is not None:
        if rating < 1 or rating > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )
        suggestion.feedback_rating = rating
    
    await db.commit()
    await db.refresh(suggestion)
    
    return {"message": "Feedback updated successfully"}


@router.post("/chat")
async def chat_with_ai(
    message: str,
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Chat with AI for general questions"""
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API not configured"
        )
    
    llm_service = LLMService(client, db)
    
    try:
        response = await llm_service.chat(message, current_user.id)
        return {"response": response}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )
