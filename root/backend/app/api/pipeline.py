from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_database
from app.auth import get_current_user
from app.models import User, Upload, Pipeline, PipelineEvent
from app.schemas import PipelineCreateRequest, PipelineStatus, PipelineDetails, PipelineEvent
from app.pipeline.tasks import process_pipeline

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/start", response_model=PipelineStatus)
async def start_pipeline(
    pipeline_data: PipelineCreateRequest,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """
    Start a new pipeline for processing an uploaded file.
    """
    # Verify the upload exists and belongs to the user
    upload = db.query(Upload).filter(
        Upload.id == pipeline_data.upload_id,
        Upload.user_id == current_user.id,
        Upload.status == "completed"
    ).first()
    
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found or not completed"
        )
    
    # Check if pipeline already exists for this upload
    existing_pipeline = db.query(Pipeline).filter(
        Pipeline.upload_id == pipeline_data.upload_id
    ).first()
    
    if existing_pipeline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pipeline already exists for this upload"
        )
    
    # Create new pipeline
    pipeline = Pipeline(
        upload_id=pipeline_data.upload_id,
        user_id=current_user.id,
        config=pipeline_data.config.dict() if pipeline_data.config else None,
        status="queued",
        created_at=datetime.utcnow()
    )
    
    db.add(pipeline)
    db.commit()
    db.refresh(pipeline)
    
    # Start the pipeline task asynchronously
    task = process_pipeline.delay(pipeline.id)
    
    # Update pipeline with task ID
    pipeline.task_id = task.id
    db.commit()
    
    return PipelineStatus(
        id=pipeline.id,
        upload_id=pipeline.upload_id,
        status=pipeline.status,
        config=pipeline.config,
        created_at=pipeline.created_at,
        started_at=pipeline.started_at,
        completed_at=pipeline.completed_at,
        output_location=pipeline.output_location,
        task_id=pipeline.task_id
    )


@router.get("/{pipeline_id}", response_model=PipelineStatus)
async def get_pipeline(
    pipeline_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """
    Get pipeline status and details.
    """
    pipeline = db.query(Pipeline).filter(
        Pipeline.id == pipeline_id,
        Pipeline.user_id == current_user.id
    ).first()
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )
    
    return PipelineStatus(
        id=pipeline.id,
        upload_id=pipeline.upload_id,
        status=pipeline.status,
        config=pipeline.config,
        created_at=pipeline.created_at,
        started_at=pipeline.started_at,
        completed_at=pipeline.completed_at,
        output_location=pipeline.output_location,
        task_id=pipeline.task_id
    )


@router.get("/{pipeline_id}/events", response_model=List[PipelineEvent])
async def get_pipeline_events(
    pipeline_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """
    Get all events for a pipeline (for monitoring progress).
    """
    # Verify pipeline belongs to user
    pipeline = db.query(Pipeline).filter(
        Pipeline.id == pipeline_id,
        Pipeline.user_id == current_user.id
    ).first()
    
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline not found"
        )
    
    # Get all events for this pipeline
    events = db.query(PipelineEvent).filter(
        PipelineEvent.pipeline_id == pipeline_id
    ).order_by(PipelineEvent.timestamp).all()
    
    return [
        PipelineEvent(
            id=event.id,
            pipeline_id=event.pipeline_id,
            event_type=event.event_type,
            data=event.data,
            timestamp=event.timestamp
        )
        for event in events
    ]


@router.get("/", response_model=List[PipelineStatus])
async def list_pipelines(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """
    List all pipelines for the current user.
    """
    pipelines = db.query(Pipeline).filter(
        Pipeline.user_id == current_user.id
    ).order_by(Pipeline.created_at.desc()).all()
    
    return [
        PipelineStatus(
            id=pipeline.id,
            upload_id=pipeline.upload_id,
            status=pipeline.status,
            config=pipeline.config,
            created_at=pipeline.created_at,
            started_at=pipeline.started_at,
            completed_at=pipeline.completed_at,
            output_location=pipeline.output_location,
            task_id=pipeline.task_id
        )
        for pipeline in pipelines
    ]
