from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from app.database import get_database
from app.models import User, Upload, FilePart
from app.schemas import (
    UploadInitRequest, 
    UploadInitResponse, 
    UploadCompleteRequest,
    UploadStatus
)
from app.auth import get_current_user
from app.s3_service import s3_service
from app.rate_limiter import limiter

router = APIRouter(prefix="/uploads", tags=["file_uploads"])


@router.post("/init", response_model=UploadInitResponse)
@limiter.limit("10/minute")  # Limit upload initiations
async def initiate_upload(
    request: Request,
    upload_request: UploadInitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Initiate file upload with presigned S3 URL.
    """
    # Create upload record
    new_upload = Upload(
        user_id=current_user.id,
        filename=upload_request.filename,
        status="INITIATED"
    )
    
    db.add(new_upload)
    await db.commit()
    await db.refresh(new_upload)
    
    try:
        # Generate presigned URLs
        s3_key, presigned_urls = await s3_service.generate_presigned_upload_urls(
            user_id=current_user.id,
            upload_id=new_upload.upload_id,
            filename=upload_request.filename,
            file_size=upload_request.file_size
        )
        
        new_upload.status = "UPLOADING"
        await db.commit()
        
        return UploadInitResponse(
            upload_id=new_upload.upload_id,
            upload_urls=presigned_urls,
            s3_key=s3_key
        )
        
    except Exception as e:
        new_upload.status = "FAILED"
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to initiate upload: {str(e)}")


@router.post("/complete")
@limiter.limit("20/minute")  # Limit completion requests
async def complete_upload(
    request: Request,
    complete_request: UploadCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Complete a file upload and validate all parts.
    """
    # Get upload record and verify ownership
    result = await db.execute(
        select(Upload).where(
            Upload.upload_id == complete_request.upload_id,
            Upload.user_id == current_user.id
        )
    )
    upload = result.scalar_one_or_none()
    
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    if upload.status != "UPLOADING":
        raise HTTPException(status_code=400, detail=f"Upload is in {upload.status} status")
    
    # Update upload status
    upload.status = "COMPLETED"
    await db.commit()
    
    return {
        "message": "Upload completed successfully",
        "upload_id": str(upload.upload_id),
        "filename": upload.filename
    }


@router.get("/status/{upload_id}", response_model=UploadStatus)
async def get_upload_status(
    upload_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Get the status of a specific upload.
    
    Returns current upload status, metadata, and progress information.
    Only returns uploads owned by the authenticated user.
    
    Args:
        upload_id: UUID of the upload to check
        current_user: Authenticated user from JWT token
        db: Database session
        
    Returns:
        UploadStatus: Current upload status and metadata
        
    Raises:
        HTTPException: If upload not found or unauthorized
    """
    # Get upload record and verify ownership
    result = await db.execute(
        select(Upload).where(
            Upload.upload_id == upload_id,
            Upload.user_id == current_user.id
        )
    )
    upload = result.scalar_one_or_none()
    
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found or unauthorized"
        )
    
    return UploadStatus.from_orm(upload)


@router.get("/", response_model=List[UploadStatus])
async def list_user_uploads(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database),
    limit: int = 50,
    offset: int = 0
):
    """
    List all uploads for the authenticated user.
    
    Returns paginated list of user's uploads, most recent first.
    Useful for frontend to show upload history.
    
    Args:
        current_user: Authenticated user from JWT token
        db: Database session
        limit: Maximum number of uploads to return (default 50)
        offset: Number of uploads to skip for pagination (default 0)
        
    Returns:
        List[UploadStatus]: List of user's uploads
    """
    result = await db.execute(
        select(Upload)
        .where(Upload.user_id == current_user.id)
        .order_by(Upload.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    uploads = result.scalars().all()
    
    return [UploadStatus.from_orm(upload) for upload in uploads]
