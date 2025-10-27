"""
User Pydantic schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    auth_provider: str = "email"


class UserCreate(UserBase):
    """User creation schema"""
    pass


class UserUpdate(BaseModel):
    """User update schema"""
    auto_delete_enabled: Optional[bool] = None
    retention_hours: Optional[int] = Field(None, ge=1, le=168)  # 1 hour to 1 week
    preferred_llm_model: Optional[str] = None
    overlay_position: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""
    id: int
    is_active: bool
    is_verified: bool
    auto_delete_enabled: bool
    retention_hours: int
    preferred_llm_model: str
    overlay_position: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ResumeBase(BaseModel):
    """Base resume schema"""
    filename: str
    file_size: int
    mime_type: str


class ResumeCreate(ResumeBase):
    """Resume creation schema"""
    storage_uri: str
    sha256_hash: str


class ResumeResponse(ResumeBase):
    """Resume response schema"""
    id: int
    user_id: int
    storage_uri: str
    sha256_hash: str
    parsed_json: Optional[str] = None
    embedding_indexed_at: Optional[datetime] = None
    skills: Optional[str] = None
    experience_years: Optional[int] = None
    education_level: Optional[str] = None
    current_role: Optional[str] = None
    uploaded_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class SessionBase(BaseModel):
    """Base session schema"""
    platform: Optional[str] = None
    session_type: str = "interview"


class SessionCreate(SessionBase):
    """Session creation schema"""
    retention_policy: str = "auto"
    privacy_mode: bool = False


class SessionResponse(SessionBase):
    """Session response schema"""
    id: int
    user_id: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    retention_policy: str
    privacy_mode: bool
    is_active: bool

    class Config:
        from_attributes = True


class TranscriptSegmentBase(BaseModel):
    """Base transcript segment schema"""
    start_ms: int
    end_ms: int
    text: str
    speaker: Optional[str] = None
    confidence: Optional[int] = None


class TranscriptSegmentCreate(TranscriptSegmentBase):
    """Transcript segment creation schema"""
    session_id: int
    is_final: bool = False


class TranscriptSegmentResponse(TranscriptSegmentBase):
    """Transcript segment response schema"""
    id: int
    session_id: int
    is_final: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SuggestionBase(BaseModel):
    """Base suggestion schema"""
    content: str
    suggestion_type: str


class SuggestionCreate(SuggestionBase):
    """Suggestion creation schema"""
    session_id: int
    segment_id: Optional[int] = None
    llm_model: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    latency_ms: Optional[int] = None


class SuggestionResponse(SuggestionBase):
    """Suggestion response schema"""
    id: int
    session_id: int
    segment_id: Optional[int] = None
    llm_model: Optional[str] = None
    accepted: bool
    dismissed: bool
    feedback_rating: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuthRequest(BaseModel):
    """Authentication request schema"""
    email: EmailStr


class AuthResponse(BaseModel):
    """Authentication response schema"""
    message: str
    token: Optional[str] = None


class MagicLinkRequest(BaseModel):
    """Magic link request schema"""
    email: EmailStr


class MagicLinkResponse(BaseModel):
    """Magic link response schema"""
    message: str
    expires_in: int  # seconds
