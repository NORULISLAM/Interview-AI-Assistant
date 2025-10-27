"""
Resume management endpoints
"""
import hashlib
import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User, Resume
from app.schemas.user import ResumeResponse, ResumeCreate
from app.services.resume_service import ResumeService
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and parse resume"""
    
    # Validate file type
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not allowed"
        )
    
    # Validate file size
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size {file_size} exceeds maximum {settings.MAX_FILE_SIZE}"
        )
    
    # Calculate file hash
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Check if resume already exists
    existing_resume = await db.execute(
        select(Resume).where(Resume.sha256_hash == file_hash)
    )
    existing_resume = existing_resume.scalar_one_or_none()
    
    if existing_resume:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume with identical content already exists"
        )
    
    # Upload to S3 (for now, just store locally)
    storage_uri = f"resumes/{current_user.id}/{file.filename}"
    
    # Create resume record
    resume_data = ResumeCreate(
        filename=file.filename,
        file_size=file_size,
        mime_type=file.content_type,
        storage_uri=storage_uri,
        sha256_hash=file_hash
    )
    
    resume_service = ResumeService(db)
    resume = await resume_service.create_resume(current_user.id, resume_data)
    
    # Parse resume content
    try:
        parsed_data = await resume_service.parse_resume(content, file.content_type)
        await resume_service.update_parsed_content(resume.id, parsed_data)
    except Exception as e:
        # Log error but don't fail the upload
        print(f"Failed to parse resume: {e}")
    
    return resume


@router.get("/", response_model=List[ResumeResponse])
async def get_my_resumes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's resumes"""
    result = await db.execute(
        select(Resume).where(
            Resume.user_id == current_user.id,
            Resume.is_active == True
        ).order_by(Resume.uploaded_at.desc())
    )
    resumes = result.scalars().all()
    return resumes


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific resume"""
    result = await db.execute(
        select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == current_user.id,
            Resume.is_active == True
        )
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    return resume


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete resume"""
    result = await db.execute(
        select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == current_user.id,
            Resume.is_active == True
        )
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Soft delete
    resume.is_active = False
    await db.commit()
    
    return {"message": "Resume deleted successfully"}
