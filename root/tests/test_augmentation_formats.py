#!/usr/bin/env python3
"""
Test script for data augmentation API
"""

import requests
import time
import json
from pathlib import Path

API_BASE = "http://localhost:8000"
SAMPLE_DATA_DIR = Path(__file__).parent / "sample_data"

def test_file_augmentation(file_path):
    """Test file upload and augmentation"""
    print(f"Testing: {file_path.name}")
    
    # Upload file
    with open(file_path, 'rb') as f:
        files = {'file': (file_path.name, f)}
        response = requests.post(f"{API_BASE}/augmentation/upload", files=files)
    
    if response.status_code != 200:
        print(f"Upload failed: {response.text}")
        return False
    
    data = response.json()
    task_id = data['task_id']
    print(f"Upload successful - {data['rows']} rows, {data['columns']} columns")
    
    # Start augmentation
    form_data = {
        'method': 'noise_injection',
        'target_size': str(data['rows'] * 2),
        'noise_level': '0.1'
    }
    
    response = requests.post(f"{API_BASE}/augmentation/augment/{task_id}", data=form_data)
    if response.status_code != 200:
        print(f"Augmentation failed: {response.text}")
        return False
    
    print("Augmentation started...")
    
    # Monitor progress
    for attempt in range(30):
        response = requests.get(f"{API_BASE}/augmentation/progress/{task_id}")
        if response.status_code != 200:
            print(f"Progress check failed: {response.text}")
            return False
        
        progress = response.json()
        status = progress['progress']
        
        if status['step'] == 'completed':
            result_info = progress.get('result_info', {})
            print(f"Completed - Generated {result_info.get('generated_rows', 0)} rows")
            
            # Test download
            download_response = requests.get(f"{API_BASE}/augmentation/download/{task_id}?format=csv")
            if download_response.status_code == 200:
                print(f"Download successful ({len(download_response.content)} bytes)")
            else:
                print("Download failed")
            
            # Cleanup
            requests.delete(f"{API_BASE}/augmentation/task/{task_id}")
            return True
            
        elif status['step'] == 'error':
            print(f"Augmentation failed: {status['message']}")
            return False
        
        time.sleep(1)
    
    print("Timeout")
    return False

def main():
    """Run API tests"""
    print("Testing data augmentation API...")
    
    # Check API
    try:
        response = requests.get(f"{API_BASE}/augmentation/methods")
        if response.status_code != 200:
            print(f"API not accessible: {response.status_code}")
            return
        print("API accessible")
    except Exception as e:
        print(f"Cannot connect to API: {e}")
        return
    
    # Get test files
    test_files = []
    for ext in ['*.csv', '*.json']:
        test_files.extend(SAMPLE_DATA_DIR.glob(ext))
    
    if not test_files:
        print("No test files found")
        return
    
    print(f"Found {len(test_files)} test files")
    
    # Run tests
    results = {}
    for file_path in test_files:
        try:
            results[file_path.name] = test_file_augmentation(file_path)
        except Exception as e:
            print(f"Error testing {file_path.name}: {e}")
            results[file_path.name] = False
    
    # Results
    passed = sum(results.values())
    total = len(results)
    print(f"\nResults: {passed}/{total} tests passed")
    
    for filename, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"{status}: {filename}")

if __name__ == "__main__":
    main()
