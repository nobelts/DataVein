"""
Simple data augmentation service using pandas
Generates synthetic data rows based on existing patterns
"""

import pandas as pd
import numpy as np
import random
from typing import Dict, List, Any
import tempfile
import os

class SimpleDataAugmenter:
    """Basic data augmentation without complex ML models"""
    
    def __init__(self):
        self.supported_formats = ['csv', 'json']
    
    def augment_data(self, file_path: str, target_rows: int = 100) -> str:
        """
        Generate synthetic data and return path to augmented file
        """
        # Read original data
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        else:
            raise ValueError("Unsupported file format")
        
        # Generate synthetic rows
        synthetic_df = self._generate_synthetic_rows(df, target_rows)
        
        # Combine original and synthetic data
        augmented_df = pd.concat([df, synthetic_df], ignore_index=True)
        
        # Save augmented data as Parquet for efficient download
        output_path = file_path.replace('.csv', '_augmented.parquet').replace('.json', '_augmented.parquet')
        augmented_df.to_parquet(output_path, index=False)
        
        return output_path
    
    def _generate_synthetic_rows(self, df: pd.DataFrame, target_rows: int) -> pd.DataFrame:
        """Generate synthetic rows based on column types"""
        
        synthetic_rows = []
        
        for _ in range(target_rows):
            new_row = {}
            
            for column in df.columns:
                new_row[column] = self._generate_synthetic_value(df[column])
            
            synthetic_rows.append(new_row)
        
        return pd.DataFrame(synthetic_rows)
    
    def _generate_synthetic_value(self, series: pd.Series) -> Any:
        """Generate a synthetic value based on column type and existing data"""
        
        # Remove null values for analysis
        clean_series = series.dropna()
        
        if len(clean_series) == 0:
            return None
        
        # Numeric columns
        if pd.api.types.is_numeric_dtype(clean_series):
            mean_val = clean_series.mean()
            std_val = clean_series.std()
            
            # Generate value within reasonable range
            if std_val > 0:
                synthetic_val = np.random.normal(mean_val, std_val)
                # Keep within min/max bounds
                min_val, max_val = clean_series.min(), clean_series.max()
                synthetic_val = np.clip(synthetic_val, min_val, max_val)
                
                # Convert back to original type
                if clean_series.dtype == 'int64':
                    return int(round(synthetic_val))
                return synthetic_val
            else:
                return clean_series.iloc[0]  # All values are the same
        
        # Text/categorical columns
        else:
            # For text data, randomly sample from existing values
            # This is simple but effective for categorical data
            unique_values = clean_series.unique()
            
            if len(unique_values) > 1:
                return random.choice(unique_values)
            else:
                return unique_values[0]
    
    def get_data_summary(self, file_path: str) -> Dict[str, Any]:
        """Get summary of the data for frontend display"""
        
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        else:
            return {"error": "Unsupported file format"}
        
        return {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "column_types": {col: str(df[col].dtype) for col in df.columns},
            "sample_data": df.head(3).to_dict(orient='records')
        }


# Simple function for worker tasks
def augment_file_data(input_file_path: str, target_rows: int = 100) -> Dict[str, Any]:
    """
    Worker task function for data augmentation
    """
    try:
        augmenter = SimpleDataAugmenter()
        
        # Get original data summary
        original_summary = augmenter.get_data_summary(input_file_path)
        
        # Generate augmented data
        output_file_path = augmenter.augment_data(input_file_path, target_rows)
        
        # Get augmented data summary
        augmented_summary = augmenter.get_data_summary(output_file_path)
        
        return {
            "success": True,
            "original_summary": original_summary,
            "augmented_summary": augmented_summary,
            "output_file": output_file_path,
            "message": f"Generated {target_rows} synthetic rows"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Data augmentation failed"
        }
