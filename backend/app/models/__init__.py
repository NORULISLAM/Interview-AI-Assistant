# Import all models to ensure they are registered with SQLAlchemy
from .user import User, Resume, Session, TranscriptSegment, Suggestion, AuditLog

__all__ = [
    "User",
    "Resume", 
    "Session",
    "TranscriptSegment",
    "Suggestion",
    "AuditLog"
]