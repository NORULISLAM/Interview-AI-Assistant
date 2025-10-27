"""
User database models
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    auth_provider = Column(String(50), default="email")  # email, google, microsoft
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Privacy settings
    auto_delete_enabled = Column(Boolean, default=True)
    retention_hours = Column(Integer, default=24)
    
    # Preferences
    preferred_llm_model = Column(String(50), default="gpt-4o-mini")
    overlay_position = Column(String(20), default="bottom-right")  # bottom-right, top-right, etc.


class Resume(Base):
    """Resume model"""
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    storage_uri = Column(String(500), nullable=False)  # S3 URI
    sha256_hash = Column(String(64), unique=True, nullable=False)
    
    # Parsed content
    parsed_json = Column(Text)  # JSON string of parsed content
    embedding_indexed_at = Column(DateTime(timezone=True))
    
    # Metadata
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Extracted entities (for quick access)
    skills = Column(Text)  # JSON array of skills
    experience_years = Column(Integer)
    education_level = Column(String(100))
    current_role = Column(String(200))


class Session(Base):
    """Interview session model"""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Session metadata
    platform = Column(String(50))  # zoom, meet, teams, desktop
    session_type = Column(String(50), default="interview")  # interview, coding, general
    
    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)
    
    # Settings
    retention_policy = Column(String(20), default="auto")  # auto, manual, never
    settings_json = Column(Text)  # JSON of session-specific settings
    
    # Status
    is_active = Column(Boolean, default=True)
    privacy_mode = Column(Boolean, default=False)  # Zero retention mode


class TranscriptSegment(Base):
    """Transcript segment model"""
    __tablename__ = "transcript_segments"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, index=True, nullable=False)
    
    # Timing
    start_ms = Column(Integer, nullable=False)
    end_ms = Column(Integer, nullable=False)
    
    # Content
    text = Column(Text, nullable=False)
    speaker = Column(String(50))  # user, interviewer, unknown
    confidence = Column(Integer)  # 0-100
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_final = Column(Boolean, default=False)


class Suggestion(Base):
    """AI suggestion model"""
    __tablename__ = "suggestions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, index=True, nullable=False)
    segment_id = Column(Integer, index=True)  # Optional reference to transcript segment
    
    # Content
    content = Column(Text, nullable=False)
    suggestion_type = Column(String(50), nullable=False)  # answer, question, tip, code
    
    # AI metadata
    llm_model = Column(String(50))
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    latency_ms = Column(Integer)
    
    # User interaction
    accepted = Column(Boolean, default=False)
    dismissed = Column(Boolean, default=False)
    feedback_rating = Column(Integer)  # 1-5 stars
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    """Audit log for privacy and compliance"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Event details
    event_type = Column(String(100), nullable=False)  # login, upload, delete, etc.
    event_data = Column(Text)  # JSON metadata
    
    # Privacy
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Retention
    retention_until = Column(DateTime(timezone=True))
