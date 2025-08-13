#!/usr/bin/env python3
"""
Test script for data augmentation file format support
"""

import json
import sys
from pathlib import Path

def test_file_formats():
    """Test that sample files can be loaded properly"""
    sample_data_dir = Path(__file__).parent / "sample_data"
    
    if not sample_data_dir.exists():
        print("Error: sample_data directory not found")
        return False
    
    sample_files = list(sample_data_dir.glob("*.*"))
    print(f"Testing {len(sample_files)} sample files...")
    
    results = []
    for file_path in sample_files:
        try:
            # Basic file validation
            if file_path.suffix.lower() == '.csv':
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                results.append(f"CSV {file_path.name}: {len(lines)} lines")
                
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    results.append(f"JSON {file_path.name}: {len(data)} records")
                else:
                    results.append(f"JSON {file_path.name}: object")
                    
            elif file_path.suffix.lower() == '.tsv':
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                results.append(f"TSV {file_path.name}: {len(lines)} lines")
                
            elif file_path.suffix.lower() == '.txt':
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                results.append(f"TXT {file_path.name}: {len(lines)} lines")
            else:
                results.append(f"Unknown {file_path.name}")
                
        except Exception as e:
            results.append(f"Error {file_path.name}: {str(e)}")
    
    # Print results
    for result in results:
        print(result)
    
    print(f"\nFile format test complete. {len(sample_files)} files processed.")
    return True

if __name__ == "__main__":
    test_file_formats()
