"""
Privacy service for GDPR compliance and data protection
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.user import User, Resume, Session, TranscriptSegment, Suggestion, AuditLog
from app.services.security_service import SecurityService
from app.services.vector_service import VectorService


class PrivacyService:
    """Privacy service for GDPR compliance and data protection"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.security_service = SecurityService()
        self.vector_service = VectorService()
    
    async def get_user_data_summary(self, user_id: int) -> Dict[str, Any]:
        """Get summary of all user data for privacy dashboard"""
        try:
            # Get user info
            user_result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {"error": "User not found"}
            
            # Get data counts
            resumes_count = await self.db.execute(
                select(Resume).where(Resume.user_id == user_id, Resume.is_active == True)
            )
            resumes = resumes_count.scalars().all()
            
            sessions_count = await self.db.execute(
                select(Session).where(Session.user_id == user_id)
            )
            sessions = sessions_count.scalars().all()
            
            transcripts_count = await self.db.execute(
                select(TranscriptSegment).join(Session).where(Session.user_id == user_id)
            )
            transcripts = transcripts_count.scalars().all()
            
            suggestions_count = await self.db.execute(
                select(Suggestion).join(Session).where(Session.user_id == user_id)
            )
            suggestions = suggestions_count.scalars().all()
            
            audit_logs_count = await self.db.execute(
                select(AuditLog).where(AuditLog.user_id == user_id)
            )
            audit_logs = audit_logs_count.scalars().all()
            
            return {
                "user_id": user_id,
                "email": user.email,
                "created_at": user.created_at,
                "data_summary": {
                    "resumes": len(resumes),
                    "sessions": len(sessions),
                    "transcript_segments": len(transcripts),
                    "suggestions": len(suggestions),
                    "audit_logs": len(audit_logs)
                },
                "retention_settings": {
                    "auto_delete_enabled": user.auto_delete_enabled,
                    "retention_hours": user.retention_hours
                },
                "last_updated": datetime.utcnow()
            }
            
        except Exception as e:
            print(f"Error getting user data summary: {e}")
            return {"error": str(e)}
    
    async def export_user_data(self, user_id: int) -> Dict[str, Any]:
        """Export all user data for GDPR data portability"""
        try:
            # Get all user data
            user_result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {"error": "User not found"}
            
            # Get all related data
            resumes_result = await self.db.execute(
                select(Resume).where(Resume.user_id == user_id)
            )
            resumes = resumes_result.scalars().all()
            
            sessions_result = await self.db.execute(
                select(Session).where(Session.user_id == user_id)
            )
            sessions = sessions_result.scalars().all()
            
            # Get transcript segments for user's sessions
            session_ids = [session.id for session in sessions]
            transcripts_result = await self.db.execute(
                select(TranscriptSegment).where(TranscriptSegment.session_id.in_(session_ids))
            )
            transcripts = transcripts_result.scalars().all()
            
            # Get suggestions for user's sessions
            suggestions_result = await self.db.execute(
                select(Suggestion).where(Suggestion.session_id.in_(session_ids))
            )
            suggestions = suggestions_result.scalars().all()
            
            # Get audit logs
            audit_logs_result = await self.db.execute(
                select(AuditLog).where(AuditLog.user_id == user_id)
            )
            audit_logs = audit_logs_result.scalars().all()
            
            # Format data for export
            export_data = {
                "export_info": {
                    "user_id": user_id,
                    "export_date": datetime.utcnow().isoformat(),
                    "data_version": "1.0"
                },
                "user_profile": {
                    "id": user.id,
                    "email": user.email,
                    "auth_provider": user.auth_provider,
                    "created_at": user.created_at.isoformat(),
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "auto_delete_enabled": user.auto_delete_enabled,
                    "retention_hours": user.retention_hours,
                    "preferred_llm_model": user.preferred_llm_model,
                    "overlay_position": user.overlay_position
                },
                "resumes": [
                    {
                        "id": resume.id,
                        "filename": resume.filename,
                        "file_size": resume.file_size,
                        "mime_type": resume.mime_type,
                        "uploaded_at": resume.uploaded_at.isoformat(),
                        "skills": resume.skills,
                        "experience_years": resume.experience_years,
                        "education_level": resume.education_level,
                        "current_role": resume.current_role,
                        "is_active": resume.is_active
                    }
                    for resume in resumes
                ],
                "sessions": [
                    {
                        "id": session.id,
                        "platform": session.platform,
                        "session_type": session.session_type,
                        "started_at": session.started_at.isoformat(),
                        "ended_at": session.ended_at.isoformat() if session.ended_at else None,
                        "duration_minutes": session.duration_minutes,
                        "retention_policy": session.retention_policy,
                        "privacy_mode": session.privacy_mode,
                        "is_active": session.is_active
                    }
                    for session in sessions
                ],
                "transcripts": [
                    {
                        "id": transcript.id,
                        "session_id": transcript.session_id,
                        "start_ms": transcript.start_ms,
                        "end_ms": transcript.end_ms,
                        "text": transcript.text,
                        "speaker": transcript.speaker,
                        "confidence": transcript.confidence,
                        "is_final": transcript.is_final,
                        "created_at": transcript.created_at.isoformat()
                    }
                    for transcript in transcripts
                ],
                "suggestions": [
                    {
                        "id": suggestion.id,
                        "session_id": suggestion.session_id,
                        "segment_id": suggestion.segment_id,
                        "content": suggestion.content,
                        "suggestion_type": suggestion.suggestion_type,
                        "llm_model": suggestion.llm_model,
                        "accepted": suggestion.accepted,
                        "dismissed": suggestion.dismissed,
                        "feedback_rating": suggestion.feedback_rating,
                        "created_at": suggestion.created_at.isoformat()
                    }
                    for suggestion in suggestions
                ],
                "audit_logs": [
                    {
                        "id": log.id,
                        "event_type": log.event_type,
                        "event_data": log.event_data,
                        "ip_address": log.ip_address,
                        "user_agent": log.user_agent,
                        "created_at": log.created_at.isoformat()
                    }
                    for log in audit_logs
                ]
            }
            
            return export_data
            
        except Exception as e:
            print(f"Error exporting user data: {e}")
            return {"error": str(e)}
    
    async def delete_user_data(self, user_id: int, delete_vector_data: bool = True) -> Dict[str, Any]:
        """Delete all user data for GDPR right to be forgotten"""
        try:
            # Get user to verify existence
            user_result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {"error": "User not found"}
            
            deleted_items = {}
            
            # Delete vector data first
            if delete_vector_data:
                vector_deleted = self.vector_service.delete_user_data(user_id)
                deleted_items["vector_data"] = vector_deleted
            
            # Delete audit logs
            audit_result = await self.db.execute(
                delete(AuditLog).where(AuditLog.user_id == user_id)
            )
            deleted_items["audit_logs"] = audit_result.rowcount
            
            # Get session IDs for cascading deletes
            sessions_result = await self.db.execute(
                select(Session).where(Session.user_id == user_id)
            )
            sessions = sessions_result.scalars().all()
            session_ids = [session.id for session in sessions]
            
            # Delete transcript segments
            if session_ids:
                transcripts_result = await self.db.execute(
                    delete(TranscriptSegment).where(TranscriptSegment.session_id.in_(session_ids))
                )
                deleted_items["transcript_segments"] = transcripts_result.rowcount
                
                # Delete suggestions
                suggestions_result = await self.db.execute(
                    delete(Suggestion).where(Suggestion.session_id.in_(session_ids))
                )
                deleted_items["suggestions"] = suggestions_result.rowcount
            
            # Delete sessions
            sessions_result = await self.db.execute(
                delete(Session).where(Session.user_id == user_id)
            )
            deleted_items["sessions"] = sessions_result.rowcount
            
            # Delete resumes
            resumes_result = await self.db.execute(
                delete(Resume).where(Resume.user_id == user_id)
            )
            deleted_items["resumes"] = resumes_result.rowcount
            
            # Delete user
            user_result = await self.db.execute(
                delete(User).where(User.id == user_id)
            )
            deleted_items["user"] = user_result.rowcount
            
            # Commit all changes
            await self.db.commit()
            
            return {
                "success": True,
                "user_id": user_id,
                "deleted_items": deleted_items,
                "deletion_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            await self.db.rollback()
            print(f"Error deleting user data: {e}")
            return {"error": str(e)}
    
    async def auto_delete_expired_data(self) -> Dict[str, Any]:
        """Automatically delete expired data based on retention policies"""
        try:
            deleted_counts = {
                "transcripts": 0,
                "suggestions": 0,
                "sessions": 0,
                "audit_logs": 0
            }
            
            # Get users with auto-delete enabled
            users_result = await self.db.execute(
                select(User).where(User.auto_delete_enabled == True)
            )
            users = users_result.scalars().all()
            
            for user in users:
                retention_hours = user.retention_hours
                if retention_hours <= 0:
                    continue
                
                cutoff_time = datetime.utcnow() - timedelta(hours=retention_hours)
                
                # Delete expired audit logs
                audit_result = await self.db.execute(
                    delete(AuditLog).where(
                        AuditLog.user_id == user.id,
                        AuditLog.created_at < cutoff_time
                    )
                )
                deleted_counts["audit_logs"] += audit_result.rowcount
                
                # Get expired sessions
                expired_sessions_result = await self.db.execute(
                    select(Session).where(
                        Session.user_id == user.id,
                        Session.ended_at < cutoff_time,
                        Session.ended_at.isnot(None)
                    )
                )
                expired_sessions = expired_sessions_result.scalars().all()
                expired_session_ids = [session.id for session in expired_sessions]
                
                if expired_session_ids:
                    # Delete transcript segments
                    transcripts_result = await self.db.execute(
                        delete(TranscriptSegment).where(
                            TranscriptSegment.session_id.in_(expired_session_ids)
                        )
                    )
                    deleted_counts["transcripts"] += transcripts_result.rowcount
                    
                    # Delete suggestions
                    suggestions_result = await self.db.execute(
                        delete(Suggestion).where(
                            Suggestion.session_id.in_(expired_session_ids)
                        )
                    )
                    deleted_counts["suggestions"] += suggestions_result.rowcount
                    
                    # Delete sessions
                    sessions_result = await self.db.execute(
                        delete(Session).where(
                            Session.id.in_(expired_session_ids)
                        )
                    )
                    deleted_counts["sessions"] += sessions_result.rowcount
            
            await self.db.commit()
            
            return {
                "success": True,
                "deleted_counts": deleted_counts,
                "cleanup_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            await self.db.rollback()
            print(f"Error in auto-delete cleanup: {e}")
            return {"error": str(e)}
    
    async def update_retention_policy(self, user_id: int, retention_hours: int) -> Dict[str, Any]:
        """Update user's data retention policy"""
        try:
            user_result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {"error": "User not found"}
            
            # Update retention settings
            user.retention_hours = retention_hours
            user.auto_delete_enabled = True
            
            await self.db.commit()
            
            return {
                "success": True,
                "user_id": user_id,
                "new_retention_hours": retention_hours,
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            await self.db.rollback()
            print(f"Error updating retention policy: {e}")
            return {"error": str(e)}
