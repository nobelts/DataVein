"""
Pipeline Stages - All data processing stages in one file for simpler deployment.
Contains validation, profiling, and stub stages for augmentation, parquetize, and finalize.
"""
import pandas as pd
import boto3
import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class PipelineStages:
    """Consolidated pipeline stages for data processing"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            endpoint_url=os.getenv("S3_ENDPOINT_URL")
        )
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "datavein-dev")
    
    # STAGE 1: VALIDATION
    def validate_file(self, s3_key: str, filename: str) -> Dict[str, Any]:
        """Validate file format and structure"""
        try:
            logger.info(f"Validating file: {filename}")
            
            # Determine file type
            file_type = self._get_file_type(filename)
            if not file_type:
                return {"error": "Unsupported file type. Must be CSV, JSON, or NDJSON"}
            
            # Load and validate based on type
            if file_type == "csv":
                df = self._load_csv(s3_key)
            elif file_type == "json":
                df = self._load_json(s3_key)
            elif file_type == "ndjson":
                df = self._load_ndjson(s3_key)
            
            # Basic validation
            if df.empty:
                return {"error": "File is empty"}
            
            if len(df.columns) == 0:
                return {"error": "No columns found"}
            
            return {
                "file_type": file_type,
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "file_size_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
            }
            
        except Exception as e:
            logger.error(f"Validation failed for {filename}: {str(e)}")
            return {"error": f"Validation failed: {str(e)}"}
    
    # STAGE 2: PROFILING
    def profile_data(self, s3_key: str, filename: str, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Profile data to understand column types and distributions"""
        try:
            logger.info(f"Profiling data: {filename}")
            
            # Load data based on file type
            if validation_result["file_type"] == "csv":
                df = self._load_csv(s3_key)
            elif validation_result["file_type"] == "json":
                df = self._load_json(s3_key)
            elif validation_result["file_type"] == "ndjson":
                df = self._load_ndjson(s3_key)
            
            profile = {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "columns": {}
            }
            
            # Profile each column
            for column in df.columns:
                col_profile = self._profile_column(df[column])
                profile["columns"][column] = col_profile
            
            # Add sample data (first 3 rows)
            profile["sample_data"] = df.head(3).to_dict("records")
            
            return profile
            
        except Exception as e:
            logger.error(f"Profiling failed for {filename}: {str(e)}")
            return {"error": f"Profiling failed: {str(e)}"}
    
    # STAGE 3: AUGMENTATION (Stub)
    def augment_data(self, profiling_result: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Augment data with synthetic records (stub implementation)"""
        try:
            synthetic_multiplier = config.get("synthetic_multiplier", 1)
            original_rows = profiling_result.get("total_rows", 0)
            synthetic_rows = original_rows * synthetic_multiplier
            
            return {
                "original_rows": original_rows,
                "synthetic_multiplier": synthetic_multiplier,
                "synthetic_rows_generated": synthetic_rows,
                "message": "Synthetic data generation completed (stub)"
            }
        except Exception as e:
            return {"error": f"Augmentation failed: {str(e)}"}
    
    # STAGE 4: PARQUETIZE (Stub)
    def parquetize_data(self, s3_key: str, filename: str, user_id: int) -> Dict[str, Any]:
        """Convert data to Parquet format (stub implementation)"""
        try:
            output_filename = filename.replace('.csv', '.parquet').replace('.json', '.parquet')
            output_key = f"processed/{user_id}/{output_filename}"
            
            return {
                "input_format": "csv/json",
                "output_format": "parquet",
                "output_key": output_key,
                "compression": "snappy",
                "message": "Parquet conversion completed (stub)"
            }
        except Exception as e:
            return {"error": f"Parquetize failed: {str(e)}"}
    
    # STAGE 5: FINALIZE (Stub)
    def finalize_pipeline(self, parquetize_result: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize pipeline with cleanup and metadata (stub implementation)"""
        try:
            output_location = parquetize_result.get("output_key")
            
            return {
                "output_location": output_location,
                "metadata_created": True,
                "cleanup_completed": True,
                "message": "Pipeline finalization completed (stub)"
            }
        except Exception as e:
            return {"error": f"Finalize failed: {str(e)}"}
    
    # HELPER METHODS
    def _get_file_type(self, filename: str) -> str:
        """Determine file type from filename"""
        filename = filename.lower()
        if filename.endswith('.csv'):
            return "csv"
        elif filename.endswith('.json'):
            return "json"
        elif filename.endswith('.ndjson') or filename.endswith('.jsonl'):
            return "ndjson"
        return None
    
    def _load_csv(self, s3_key: str) -> pd.DataFrame:
        """Load CSV file from S3"""
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
        return pd.read_csv(response['Body'])
    
    def _load_json(self, s3_key: str) -> pd.DataFrame:
        """Load JSON file from S3"""
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
        data = json.loads(response['Body'].read())
        return pd.DataFrame(data)
    
    def _load_ndjson(self, s3_key: str) -> pd.DataFrame:
        """Load NDJSON file from S3"""
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
        lines = response['Body'].read().decode('utf-8').strip().split('\n')
        data = [json.loads(line) for line in lines if line.strip()]
        return pd.DataFrame(data)
    
    def _profile_column(self, series: pd.Series) -> Dict[str, Any]:
        """Profile a single column with type inference and statistics"""
        profile = {
            "name": series.name,
            "data_type": str(series.dtype),
            "null_count": int(series.isnull().sum()),
            "null_percentage": round(float(series.isnull().sum() / len(series) * 100), 2),
            "unique_count": int(series.nunique()),
            "unique_percentage": round(float(series.nunique() / len(series) * 100), 2)
        }
        
        # Infer semantic type
        profile["inferred_type"] = self._infer_semantic_type(series)
        
        # Add type-specific statistics
        if pd.api.types.is_numeric_dtype(series):
            profile.update(self._numeric_stats(series))
        elif pd.api.types.is_string_dtype(series) or series.dtype == 'object':
            profile.update(self._string_stats(series))
        
        return profile
    
    def _infer_semantic_type(self, series: pd.Series) -> str:
        """Infer semantic type of column data"""
        clean_series = series.dropna()
        
        if len(clean_series) == 0:
            return "empty"
        
        if pd.api.types.is_numeric_dtype(clean_series):
            return "numeric"
        
        if clean_series.dtype == 'object':
            # Check for email pattern
            if clean_series.astype(str).str.contains(r'^[^@]+@[^@]+\.[^@]+$', regex=True).any():
                return "email"
            
            # Check for categorical data (less than 10% unique)
            if clean_series.nunique() / len(clean_series) < 0.1:
                return "categorical"
            
            return "text"
        
        return "unknown"
    
    def _numeric_stats(self, series: pd.Series) -> Dict[str, Any]:
        """Calculate statistics for numeric columns"""
        clean_series = series.dropna()
        
        if len(clean_series) == 0:
            return {"min": None, "max": None, "mean": None}
        
        return {
            "min": float(clean_series.min()),
            "max": float(clean_series.max()),
            "mean": round(float(clean_series.mean()), 3),
            "median": float(clean_series.median())
        }
    
    def _string_stats(self, series: pd.Series) -> Dict[str, Any]:
        """Calculate statistics for string columns"""
        clean_series = series.dropna().astype(str)
        
        if len(clean_series) == 0:
            return {"min_length": None, "max_length": None}
        
        lengths = clean_series.str.len()
        
        return {
            "min_length": int(lengths.min()),
            "max_length": int(lengths.max()),
            "avg_length": round(float(lengths.mean()), 1),
            "most_common": clean_series.value_counts().head(3).to_dict()
        }


# Global instance for use in tasks
pipeline_stages = PipelineStages()
