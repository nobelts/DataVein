"""
API endpoints for data augmentation functionality
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Optional, Literal
import pandas as pd
import io
import uuid
from app.augmentation_service import DataAugmentationService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/augmentation", tags=["augmentation"])

# Store for progress tracking (in production, use Redis)
progress_store = {}

class AugmentationProgress:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.data = None
        self.augmented_data = None
        self.storage_keys = {}  # Store MinIO keys for different formats
        self.download_urls = {}  # Store presigned download URLs
        self.progress = {'step': 'initialized', 'percentage': 0, 'message': 'Task created'}
    
    def update_progress(self, progress_data):
        self.progress = progress_data
        progress_store[self.task_id] = self

@router.post("/upload")
async def upload_for_augmentation(file: UploadFile = File(...)):
    """Upload a CSV file for augmentation."""
    try:
        # Read the uploaded file
        content = await file.read()
        filename_lower = file.filename.lower()
        
        if filename_lower.endswith('.csv'):
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        elif filename_lower.endswith('.parquet'):
            df = pd.read_parquet(io.BytesIO(content))
        elif filename_lower.endswith('.json'):
            df = pd.read_json(io.StringIO(content.decode('utf-8')))
        elif filename_lower.endswith('.tsv') or filename_lower.endswith('.tab'):
            df = pd.read_csv(io.StringIO(content.decode('utf-8')), sep='\t')
        elif filename_lower.endswith('.txt'):
            # Try to detect delimiter
            text_content = content.decode('utf-8')
            if '\t' in text_content.split('\n')[0]:
                df = pd.read_csv(io.StringIO(text_content), sep='\t')
            else:
                df = pd.read_csv(io.StringIO(text_content))
        elif filename_lower.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Supported formats: CSV, TSV, TXT, JSON, Excel (.xlsx/.xls), Parquet")
        
        # Create task for progress tracking
        task_id = str(uuid.uuid4())
        progress_tracker = AugmentationProgress(task_id)
        progress_tracker.data = df
        progress_store[task_id] = progress_tracker
        
        return {
            "task_id": task_id,
            "filename": file.filename,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
    
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.post("/augment/{task_id}")
async def augment_data(
    task_id: str,
    background_tasks: BackgroundTasks,
    method: str = Form(...),
    target_size: Optional[int] = Form(None),
    noise_level: float = Form(0.1)
):
    """Start data augmentation process."""
    if task_id not in progress_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    progress_tracker = progress_store[task_id]
    
    if progress_tracker.data is None:
        raise HTTPException(status_code=400, detail="No data uploaded for this task")
    
    # Start augmentation in background
    background_tasks.add_task(
        _perform_augmentation,
        task_id,
        method,
        target_size,
        noise_level
    )
    
    return {
        "task_id": task_id,
        "status": "started",
        "method": method,
        "target_size": target_size
    }

async def _perform_augmentation(task_id: str, method: str, target_size: Optional[int], noise_level: float):
    """Perform the augmentation in background."""
    try:
        progress_tracker = progress_store[task_id]
        service = DataAugmentationService()
        
        # Set up progress callback
        service.set_progress_callback(progress_tracker.update_progress)
        
        # Perform augmentation
        kwargs = {}
        if method == 'noise_injection':
            kwargs['noise_level'] = noise_level
        
        augmented_df = service.augment_data(
            progress_tracker.data,
            method=method,
            target_size=target_size,
            **kwargs
        )
        
        # Store results in MinIO
        progress_tracker.augmented_data = augmented_df
        
        # Export and store in both CSV and Parquet formats
        csv_result = service.export_data(augmented_df, format='csv', store_in_minio=True)
        parquet_result = service.export_data(augmented_df, format='parquet', store_in_minio=True)
        
        # Store storage keys and download URLs
        progress_tracker.storage_keys = {
            'csv': csv_result['storage_key'],
            'parquet': parquet_result['storage_key']
        }
        progress_tracker.download_urls = {
            'csv': csv_result['download_url'],
            'parquet': parquet_result['download_url']
        }
        
        progress_tracker.update_progress({
            'step': 'completed',
            'percentage': 100,
            'message': f'Generated {len(augmented_df)} total rows and stored in MinIO'
        })
        
    except Exception as e:
        logger.error(f"Error in augmentation: {str(e)}")
        progress_tracker.update_progress({
            'step': 'error',
            'percentage': 0,
            'message': f'Error: {str(e)}'
        })

@router.get("/progress/{task_id}")
async def get_progress(task_id: str):
    """Get progress of augmentation task."""
    if task_id not in progress_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    progress_tracker = progress_store[task_id]
    result = {
        "task_id": task_id,
        "progress": progress_tracker.progress
    }
    
    if progress_tracker.augmented_data is not None:
        result["result_info"] = {
            "total_rows": len(progress_tracker.augmented_data),
            "original_rows": len(progress_tracker.data),
            "generated_rows": len(progress_tracker.augmented_data) - len(progress_tracker.data)
        }
        
        # Include storage information if available
        if progress_tracker.storage_keys:
            result["storage_info"] = {
                "formats_available": list(progress_tracker.storage_keys.keys()),
                "download_urls": progress_tracker.download_urls
            }
    
    return result

@router.get("/download/{task_id}")
async def download_augmented_data(
    task_id: str,
    format: Literal['csv', 'parquet'] = 'csv'
):
    """Download the augmented data from MinIO storage."""
    if task_id not in progress_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    progress_tracker = progress_store[task_id]
    
    if progress_tracker.augmented_data is None:
        raise HTTPException(status_code=400, detail="No augmented data available")
    
    try:
        # Check if file exists in MinIO storage
        if format in progress_tracker.storage_keys:
            # Download from MinIO
            service = DataAugmentationService()
            storage_key = progress_tracker.storage_keys[format]
            file_data = service.get_file_from_minio(storage_key)
        else:
            # Fallback: generate on-demand
            service = DataAugmentationService()
            service.set_progress_callback(progress_tracker.update_progress)
            export_result = service.export_data(progress_tracker.augmented_data, format=format, store_in_minio=False)
            file_data = export_result['content']
        
        # Set appropriate content type and filename
        if format == 'csv':
            media_type = 'text/csv'
            filename = f"augmented_data_{task_id[:8]}.csv"
        else:
            media_type = 'application/octet-stream'
            filename = f"augmented_data_{task_id[:8]}.parquet"
        
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        logger.error(f"Error downloading data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating download: {str(e)}")

# Alternative presigned URL download for really large files (>100MB) - currently disabled
# This approach bypasses the backend but requires MinIO to be publicly accessible
"""
@router.get("/download-url/{task_id}")
async def get_download_url(
    task_id: str,
    format: Literal['csv', 'parquet'] = 'csv'
):
    \"\"\"Get a presigned download URL for the augmented data.\"\"\"
    if task_id not in progress_store:
        raise HTTPException(status_code=404, detail="Task not found")
    
    progress_tracker = progress_store[task_id]
    
    if format not in progress_tracker.download_urls:
        raise HTTPException(status_code=404, detail=f"No {format} file available")
    
    return {
        "download_url": progress_tracker.download_urls[format],
        "format": format,
        "expires_in": 3600  # 1 hour
    }
"""

@router.get("/methods")
async def get_available_methods():
    """Get list of available augmentation methods."""
    service = DataAugmentationService()
    return {
        "methods": service.get_available_methods(),
        "descriptions": {
            "noise_injection": "Add Gaussian noise to numeric columns",
            "bootstrap_sampling": "Create variations through resampling",
            "interpolation": "Generate synthetic rows by blending existing data"
        }
    }

@router.delete("/task/{task_id}")
async def cleanup_task(task_id: str):
    """Clean up task data."""
    if task_id in progress_store:
        del progress_store[task_id]
        return {"message": "Task cleaned up successfully"}
    raise HTTPException(status_code=404, detail="Task not found")
