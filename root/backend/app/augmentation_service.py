"""
Data Augmentation Service for DataVein
Provides statistical data augmentation methods with MinIO storage support
"""

import pandas as pd
import numpy as np
import io
import uuid
import os
import boto3
from typing import Optional, Callable, Dict, Any
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Literal
import logging
import io
from pathlib import Path

logger = logging.getLogger(__name__)


class DataAugmentationService:
    """
    Service for augmenting data using statistical methods
    with MinIO storage for results
    """
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        self.progress_callback = progress_callback
        self.task_id = str(uuid.uuid4())
        
        # Define available augmentation methods
        self.available_methods = [
            'noise_injection',
            'bootstrap_sampling', 
            'interpolation'
        ]
        
        # Initialize MinIO client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin"),
            endpoint_url=os.getenv("S3_ENDPOINT_URL", "http://localhost:9000")
        )
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "datavein-dev")
        
        # Ensure bucket exists
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure the MinIO bucket exists"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"Created bucket: {self.bucket_name}")
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
            else:
                logger.error(f"Error checking bucket: {e}")
    
    def _generate_storage_key(self, task_id: str, format: str) -> str:
        """Generate S3 key for storing augmented data"""
        return f"augmented/{task_id}/result.{format}"
    
    def _store_in_minio(self, data: bytes, task_id: str, format: str) -> str:
        """Store augmented data in MinIO and return the key"""
        key = self._generate_storage_key(task_id, format)
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=data,
                ContentType='application/octet-stream' if format == 'parquet' else 'text/csv'
            )
            logger.info(f"Stored file in MinIO: {key}")
            return key
        except ClientError as e:
            logger.error(f"Failed to store file in MinIO: {e}")
            raise
    
    def set_progress_callback(self, callback):
        """Set a callback function for progress tracking."""
        self.progress_callback = callback
    
    def _update_progress(self, step: str, percentage: float, message: str = ""):
        """Update progress if callback is set."""
        if self.progress_callback:
            self.progress_callback({
                'step': step,
                'percentage': percentage,
                'message': message
            })
    
    def augment_data(self, data: pd.DataFrame, method: str = 'noise_injection', 
                    target_size: Optional[int] = None, **kwargs) -> pd.DataFrame:
        """
        Augment the provided data using the specified method.
        
        Args:
            data: Input DataFrame to augment
            method: Augmentation method to use
            target_size: Target number of rows for augmented dataset
            **kwargs: Additional parameters for augmentation
            
        Returns:
            Augmented DataFrame
        """
        if method not in self.available_methods:
            raise ValueError(f"Method {method} not available. Choose from: {self.available_methods}")
        
        logger.info(f"Augmenting data with method: {method}")
        self._update_progress("initialization", 10, f"Starting {method} augmentation")
        
        if method == 'noise_injection':
            result = self._augment_with_noise(data, target_size, **kwargs)
        elif method == 'bootstrap_sampling':
            result = self._augment_with_bootstrap(data, target_size, **kwargs)
        elif method == 'interpolation':
            result = self._augment_with_interpolation(data, target_size, **kwargs)
        else:
            result = self._augment_with_noise(data, target_size, **kwargs)
        
        self._update_progress("completed", 100, "Augmentation completed successfully")
        return result
    
    def export_data(self, data: pd.DataFrame, format: str = 'csv', 
                   filename: Optional[str] = None, store_in_minio: bool = True) -> Dict[str, Any]:
        """
        Export augmented data to specified format and optionally store in MinIO
        
        Args:
            data: DataFrame to export
            format: Export format ('csv' or 'parquet')
            filename: Optional filename (for metadata)
            store_in_minio: Whether to store the file in MinIO
            
        Returns:
            Dict containing file data and storage info
        """
        self._update_progress("export", 80, f"Exporting data as {format}")
        
        # Generate file content
        if format == 'csv':
            buffer = io.StringIO()
            data.to_csv(buffer, index=False)
            file_content = buffer.getvalue().encode('utf-8')
        elif format == 'parquet':
            buffer = io.BytesIO()
            data.to_parquet(buffer, index=False, engine='pyarrow')
            file_content = buffer.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        result = {
            'content': file_content,
            'format': format,
            'size': len(file_content)
        }
        
        # Store in MinIO if requested
        if store_in_minio:
            self._update_progress("export", 85, f"Storing in MinIO")
            storage_key = self._store_in_minio(file_content, self.task_id, format)
            result['storage_key'] = storage_key
            result['download_url'] = self._generate_download_url(storage_key)
        
        self._update_progress("export", 90, f"Export completed")
        return result
    
    def _generate_download_url(self, storage_key: str, expiry: int = 3600) -> str:
        """Generate a presigned URL for downloading from MinIO"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': storage_key},
                ExpiresIn=expiry
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate download URL: {e}")
            raise
    
    def get_file_from_minio(self, storage_key: str) -> bytes:
        """Retrieve file content from MinIO"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=storage_key)
            return response['Body'].read()
        except ClientError as e:
            logger.error(f"Failed to retrieve file from MinIO: {e}")
            raise
    
    def _augment_with_noise(self, data: pd.DataFrame, target_size: Optional[int] = None, 
                           noise_level: float = 0.1) -> pd.DataFrame:
        """Augment data by adding gaussian noise to numeric columns."""
        self._update_progress("processing", 30, "Analyzing data structure")
        
        if target_size is None:
            target_size = len(data) * 2
        
        # Separate numeric and non-numeric columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        non_numeric_cols = data.select_dtypes(exclude=[np.number]).columns
        
        self._update_progress("processing", 40, "Generating synthetic data")
        
        augmented_rows = []
        current_size = len(data)
        total_to_generate = target_size - current_size
        
        for i in range(total_to_generate):
            if i % max(1, total_to_generate // 10) == 0:  # Update every 10%
                progress = 40 + (i / total_to_generate) * 30  # 40-70% range
                self._update_progress("processing", progress, f"Generated {i}/{total_to_generate} rows")
            
            # Sample a random row
            base_row = data.sample(n=1).copy()
            
            # Add noise to numeric columns
            for col in numeric_cols:
                if not base_row[col].isna().iloc[0]:
                    original_val = base_row[col].iloc[0]
                    noise = np.random.normal(0, abs(original_val) * noise_level)
                    base_row[col] = original_val + noise
            
            augmented_rows.append(base_row)
            current_size += 1
        
        self._update_progress("processing", 70, "Combining datasets")
        
        if augmented_rows:
            augmented_df = pd.concat([data] + augmented_rows, ignore_index=True)
        else:
            augmented_df = data.copy()
        
        logger.info(f"Generated {len(augmented_df) - len(data)} synthetic rows using noise injection")
        return augmented_df
    
    def _augment_with_bootstrap(self, data: pd.DataFrame, target_size: Optional[int] = None) -> pd.DataFrame:
        """Augment data using bootstrap sampling."""
        if target_size is None:
            target_size = len(data) * 2
        
        additional_rows = target_size - len(data)
        if additional_rows <= 0:
            return data.copy()
        
        # Bootstrap sample
        sampled_rows = data.sample(n=additional_rows, replace=True, ignore_index=True)
        augmented_df = pd.concat([data, sampled_rows], ignore_index=True)
        
        logger.info(f"Generated {additional_rows} synthetic rows using bootstrap sampling")
        return augmented_df
    
    def _augment_with_interpolation(self, data: pd.DataFrame, target_size: Optional[int] = None) -> pd.DataFrame:
        """Augment data using linear interpolation between rows."""
        if target_size is None:
            target_size = len(data) * 2
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            logger.warning("No numeric columns found for interpolation, falling back to bootstrap")
            return self._augment_with_bootstrap(data, target_size)
        
        additional_rows = target_size - len(data)
        if additional_rows <= 0:
            return data.copy()
        
        augmented_rows = []
        
        for _ in range(additional_rows):
            # Select two random rows
            indices = np.random.choice(len(data), size=2, replace=True)
            row1 = data.iloc[indices[0]].copy()
            row2 = data.iloc[indices[1]].copy()
            
            # Interpolate numeric columns
            alpha = np.random.random()  # Random weight between 0 and 1
            new_row = row1.copy()
            
            for col in numeric_cols:
                if not (pd.isna(row1[col]) or pd.isna(row2[col])):
                    new_row[col] = alpha * row1[col] + (1 - alpha) * row2[col]
            
            augmented_rows.append(new_row.to_frame().T)
        
        if augmented_rows:
            augmented_df = pd.concat([data] + augmented_rows, ignore_index=True)
        else:
            augmented_df = data.copy()
        
        logger.info(f"Generated {len(augmented_df) - len(data)} synthetic rows using interpolation")
        return augmented_df
    
    def get_available_methods(self) -> list:
        """Return list of available augmentation methods."""
        return self.available_methods.copy()


# DataDreamer integration (commented out due to dependency conflicts)
# 
# TODO: Uncomment when DataDreamer dependencies are resolved
#
# from datadreamer import DataDreamer
# from datadreamer.llms import OpenAI
# from datadreamer.datasets import Dataset
# 
# class DataDreamerAugmentationService(DataAugmentationService):
#     """Enhanced augmentation service using DataDreamer."""
#     
#     def __init__(self, openai_api_key: Optional[str] = None):
#         super().__init__()
#         self.openai_api_key = openai_api_key
#         self.available_methods.extend([
#             'llm_generation',
#             'synthetic_generation',
#             'paraphrasing'
#         ])
#     
#     def _augment_with_datadreamer(self, data: pd.DataFrame, method: str, **kwargs) -> pd.DataFrame:
#         """Use DataDreamer for advanced augmentation."""
#         with DataDreamer("./cache"):
#             llm = OpenAI("gpt-3.5-turbo", api_key=self.openai_api_key)
#             
#             # Convert DataFrame to DataDreamer Dataset
#             dataset = Dataset.from_pandas(data)
#             
#             # Generate synthetic data based on method
#             if method == 'llm_generation':
#                 return self._llm_generate_similar(dataset, llm, **kwargs)
#             elif method == 'synthetic_generation':
#                 return self._synthetic_generate(dataset, llm, **kwargs)
#             elif method == 'paraphrasing':
#                 return self._paraphrase_text_columns(dataset, llm, **kwargs)
#         
#         return data
