#!/usr/bin/env python3
"""
Test script for Refyne Data Cleanser API
"""
import requests
import json
import time

API_BASE = "http://localhost:8000/api/v1"

def test_workflow():
    """Test the complete upload -> profile -> clean -> download workflow"""
    
    print("=" * 50)
    print("  Refyne API Workflow Test")
    print("=" * 50)
    print()
    
    # Step 1: Upload
    print("STEP 1: Uploading file...")
    with open('/tmp/test_workflow.csv', 'rb') as f:
        response = requests.post(f"{API_BASE}/upload", files={'file': f})
    
    upload_data = response.json()
    file_id = upload_data['file_id']
    print(f"✓ Uploaded! File ID: {file_id}")
    print(f"  Size: {upload_data['size_bytes']} bytes")
    print()
    
    # Step 2: Profile
    print("STEP 2: Profiling data quality...")
    response = requests.post(
        f"{API_BASE}/profile",
        json={"file_id": file_id}
    )
    profile_data = response.json()
    print(f"✓ Quality Score: {profile_data['overall_quality_score']}/100")
    print(f"  Rows: {profile_data['rows']}, Columns: {profile_data['columns']}")
    print()
    
    # Step 3: Clean
    print("STEP 3: Cleaning data...")
    response = requests.post(
        f"{API_BASE}/clean",
        json={"file_id": file_id, "aggressive": False}
    )
    clean_data = response.json()
    output_id = clean_data['output_file_id']
    print(f"✓ Cleaned! Output ID: {output_id}")
    print(f"  Rows: {clean_data['rows_before']} → {clean_data['rows_after']}")
    print(f"  Quality: {clean_data['quality_score_before']} → {clean_data['quality_score_after']}")
    print()
    print("  Operations performed:")
    for op in clean_data['operations_performed']:
        print(f"    - {op}")
    print()
    
    # Step 4: Download
    print("STEP 4: Downloading cleaned file...")
    response = requests.get(f"{API_BASE}/download/{output_id}?output=true")
    with open('/tmp/cleaned_python.csv', 'wb') as f:
        f.write(response.content)
    print("✓ Downloaded to /tmp/cleaned_python.csv")
    print()
    
    # Step 5: List files
    print("STEP 5: Listing all files...")
    response = requests.get(f"{API_BASE}/files?output=true")
    files_data = response.json()
    print(f"✓ Found {files_data['count']} cleaned files")
    print()
    
    print("=" * 50)
    print("  ✓ All tests passed!")
    print("=" * 50)


def test_batch_upload():
    """Test batch upload feature"""
    print("\n" + "=" * 50)
    print("  Testing Batch Upload")
    print("=" * 50)
    print()
    
    # Create multiple test files
    files = [
        ('files', ('file1.csv', open('/tmp/test_workflow.csv', 'rb'), 'text/csv')),
        ('files', ('file2.csv', open('/tmp/test_workflow.csv', 'rb'), 'text/csv')),
    ]
    
    response = requests.post(f"{API_BASE}/batch/upload", files=files)
    batch_data = response.json()
    
    print(f"✓ Uploaded {batch_data['uploaded']}/{batch_data['total_files']} files")
    for file_info in batch_data['files']:
        print(f"  - {file_info['filename']}: {file_info['file_id']}")
    print()


def test_validation():
    """Test validation and schema inference"""
    print("\n" + "=" * 50)
    print("  Testing Validation & Schema")
    print("=" * 50)
    print()
    
    # Upload a file first
    with open('/tmp/test_workflow.csv', 'rb') as f:
        response = requests.post(f"{API_BASE}/upload", files={'file': f})
    file_id = response.json()['file_id']
    
    # Clean it
    response = requests.post(
        f"{API_BASE}/clean",
        json={"file_id": file_id, "aggressive": False}
    )
    output_id = response.json()['output_file_id']
    
    # Infer schema
    print("Inferring schema from cleaned data...")
    response = requests.post(f"{API_BASE}/schema/infer?file_id={output_id}")
    schema_data = response.json()
    print(f"✓ Schema inferred: {schema_data['columns']} columns")
    print()
    
    # Validate
    print("Validating data...")
    response = requests.post(
        f"{API_BASE}/validate",
        json={"file_id": file_id}
    )
    validation_data = response.json()
    print(f"✓ Validation {'PASSED' if validation_data['passed'] else 'FAILED'}")
    if validation_data['warnings']:
        print("  Warnings:")
        for warning in validation_data['warnings']:
            print(f"    - {warning}")
    print()


if __name__ == "__main__":
    try:
        test_workflow()
        test_batch_upload()
        test_validation()
        
        print("\n" + "🎉 All API tests completed successfully! 🎉\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
