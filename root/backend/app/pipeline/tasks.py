from celery import Celery
from sqlalchemy.orm import Session
from app.database import get_database
from app.models import Pipeline, PipelineEvent
from app.pipeline.stages import pipeline_stages
import logging
import json
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Import the celery app
from app.pipeline.celery_app import celery_app


@celery_app.task(bind=True)
def process_pipeline(self, pipeline_id: int):
    """
    Main pipeline task that processes a file through all stages.
    This task coordinates the entire pipeline flow.
    """
    logger.info(f"Starting pipeline processing for pipeline_id: {pipeline_id}")
    
    db = next(get_database())
    
    try:
        # Get pipeline from database
        pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
        if not pipeline:
            logger.error(f"Pipeline {pipeline_id} not found")
            return {"error": "Pipeline not found"}
        
        # Update pipeline status
        pipeline.status = "running"
        pipeline.started_at = datetime.utcnow()
        db.commit()
        
        # Log start event
        _create_pipeline_event(db, pipeline_id, "PIPELINE_STARTED", {"message": "Pipeline processing started"})
        
        # Stage 1: Validation
        validation_result = _run_validation_stage(db, pipeline)
        if "error" in validation_result:
            _handle_pipeline_failure(db, pipeline, "validation", validation_result["error"])
            return validation_result
        
        # Stage 2: Profiling
        profiling_result = _run_profiling_stage(db, pipeline, validation_result)
        if "error" in profiling_result:
            _handle_pipeline_failure(db, pipeline, "profiling", profiling_result["error"])
            return profiling_result
        
        # Stage 3: Augmentation (stub for MVP)
        augmentation_result = _run_augmentation_stage(db, pipeline, profiling_result)
        if "error" in augmentation_result:
            _handle_pipeline_failure(db, pipeline, "augmentation", augmentation_result["error"])
            return augmentation_result
        
        # Stage 4: Parquetize (stub for MVP)
        parquetize_result = _run_parquetize_stage(db, pipeline, augmentation_result)
        if "error" in parquetize_result:
            _handle_pipeline_failure(db, pipeline, "parquetize", parquetize_result["error"])
            return parquetize_result
        
        # Stage 5: Finalize (stub for MVP)
        finalize_result = _run_finalize_stage(db, pipeline, parquetize_result)
        if "error" in finalize_result:
            _handle_pipeline_failure(db, pipeline, "finalize", finalize_result["error"])
            return finalize_result
        
        # Mark pipeline as completed
        pipeline.status = "completed"
        pipeline.completed_at = datetime.utcnow()
        pipeline.output_location = finalize_result.get("output_location")
        db.commit()
        
        _create_pipeline_event(db, pipeline_id, "PIPELINE_COMPLETED", {"message": "Pipeline processing completed successfully"})
        
        logger.info(f"Pipeline {pipeline_id} completed successfully")
        return {"status": "completed", "output_location": pipeline.output_location}
        
    except Exception as e:
        logger.error(f"Pipeline {pipeline_id} failed with error: {str(e)}")
        _handle_pipeline_failure(db, pipeline, "system", str(e))
        return {"error": f"Pipeline failed: {str(e)}"}
    
    finally:
        db.close()


def _run_validation_stage(db: Session, pipeline: Pipeline) -> Dict[str, Any]:
    """Run the validation stage"""
    try:
        logger.info(f"Running validation stage for pipeline {pipeline.id}")
        
        _create_pipeline_event(db, pipeline.id, "STAGE_STARTED", {"stage": "validation"})
        
        # Use the validation stage
        result = pipeline_stages.validate_file(
            s3_key=pipeline.upload.file_key,
            filename=pipeline.upload.filename
        )
        
        if "error" in result:
            _create_pipeline_event(db, pipeline.id, "STAGE_FAILED", {
                "stage": "validation", 
                "error": result["error"]
            })
            return result
        
        _create_pipeline_event(db, pipeline.id, "STAGE_COMPLETED", {
            "stage": "validation",
            "result": result
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Validation stage failed: {str(e)}")
        return {"error": f"Validation failed: {str(e)}"}


def _run_profiling_stage(db: Session, pipeline: Pipeline, validation_result: Dict[str, Any]) -> Dict[str, Any]:
    """Run the profiling stage"""
    try:
        logger.info(f"Running profiling stage for pipeline {pipeline.id}")
        
        _create_pipeline_event(db, pipeline.id, "STAGE_STARTED", {"stage": "profiling"})
        
        # Use the profiling stage
        result = pipeline_stages.profile_data(
            s3_key=pipeline.upload.file_key,
            filename=pipeline.upload.filename,
            validation_result=validation_result
        )
        
        if "error" in result:
            _create_pipeline_event(db, pipeline.id, "STAGE_FAILED", {
                "stage": "profiling", 
                "error": result["error"]
            })
            return result
        
        _create_pipeline_event(db, pipeline.id, "STAGE_COMPLETED", {
            "stage": "profiling",
            "result": result
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Profiling stage failed: {str(e)}")
        return {"error": f"Profiling failed: {str(e)}"}


def _run_augmentation_stage(db: Session, pipeline: Pipeline, profiling_result: Dict[str, Any]) -> Dict[str, Any]:
    """Run the augmentation stage (stub implementation for MVP)"""
    try:
        logger.info(f"Running augmentation stage for pipeline {pipeline.id}")
        
        _create_pipeline_event(db, pipeline.id, "STAGE_STARTED", {"stage": "augmentation"})
        
        # Use consolidated stages
        config = pipeline.config or {}
        result = pipeline_stages.augment_data(profiling_result, config)
        
        _create_pipeline_event(db, pipeline.id, "STAGE_COMPLETED", {
            "stage": "augmentation",
            "result": result
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Augmentation stage failed: {str(e)}")
        return {"error": f"Augmentation failed: {str(e)}"}


def _run_parquetize_stage(db: Session, pipeline: Pipeline, augmentation_result: Dict[str, Any]) -> Dict[str, Any]:
    """Run the parquetize stage (stub implementation for MVP)"""
    try:
        logger.info(f"Running parquetize stage for pipeline {pipeline.id}")
        
        _create_pipeline_event(db, pipeline.id, "STAGE_STARTED", {"stage": "parquetize"})
        
        # Use consolidated stages
        result = pipeline_stages.parquetize_data(
            s3_key=pipeline.upload.file_key,
            filename=pipeline.upload.filename,
            user_id=pipeline.user_id
        )
        
        _create_pipeline_event(db, pipeline.id, "STAGE_COMPLETED", {
            "stage": "parquetize",
            "result": result
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Parquetize stage failed: {str(e)}")
        return {"error": f"Parquetize failed: {str(e)}"}


def _run_finalize_stage(db: Session, pipeline: Pipeline, parquetize_result: Dict[str, Any]) -> Dict[str, Any]:
    """Run the finalize stage (stub implementation for MVP)"""
    try:
        logger.info(f"Running finalize stage for pipeline {pipeline.id}")
        
        _create_pipeline_event(db, pipeline.id, "STAGE_STARTED", {"stage": "finalize"})
        
        # Use consolidated stages
        result = pipeline_stages.finalize_pipeline(parquetize_result)
        
        _create_pipeline_event(db, pipeline.id, "STAGE_COMPLETED", {
            "stage": "finalize",
            "result": result
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Finalize stage failed: {str(e)}")
        return {"error": f"Finalize failed: {str(e)}"}


def _create_pipeline_event(db: Session, pipeline_id: int, event_type: str, data: Dict[str, Any]):
    """Create a pipeline event record"""
    event = PipelineEvent(
        pipeline_id=pipeline_id,
        event_type=event_type,
        data=data,
        timestamp=datetime.utcnow()
    )
    db.add(event)
    db.commit()


def _handle_pipeline_failure(db: Session, pipeline: Pipeline, stage: str, error: str):
    """Handle pipeline failure"""
    pipeline.status = "failed"
    pipeline.completed_at = datetime.utcnow()
    db.commit()
    
    _create_pipeline_event(db, pipeline.id, "PIPELINE_FAILED", {
        "stage": stage,
        "error": error
    })
