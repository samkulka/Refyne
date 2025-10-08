#!/usr/bin/env python3
"""
Simple test script for Refyne Data Cleanser API
Run this to verify the API is working correctly
"""
import requests

API_BASE = "http://localhost:8000/api/v1"

print("=" * 60)
print("  Refyne Data Cleanser API - Simple Test")
print("=" * 60)
print()

# 1. Upload
print("1️⃣  Uploading test file...")
with open('/tmp/test_workflow.csv', 'rb') as f:
    r = requests.post(f"{API_BASE}/upload", files={'file': f})
file_id = r.json()['file_id']
print(f"   ✓ File uploaded: {file_id}\n")

# 2. Profile
print("2️⃣  Profiling data quality...")
r = requests.post(f"{API_BASE}/profile", json={"file_id": file_id})
data = r.json()
print(f"   ✓ Quality Score: {data['overall_quality_score']}/100")
print(f"   ✓ Rows: {data['rows']}, Columns: {data['columns']}\n")

# 3. Clean
print("3️⃣  Cleaning data...")
r = requests.post(f"{API_BASE}/clean", json={"file_id": file_id})
data = r.json()
print(f"   ✓ Rows cleaned: {data['rows_before']} → {data['rows_after']}")
print(f"   ✓ Operations: {len(data['operations_performed'])}")
for op in data['operations_performed'][:3]:
    print(f"      - {op}")
print()

# 4. Download
print("4️⃣  Downloading cleaned file...")
output_id = data['output_file_id']
r = requests.get(f"{API_BASE}/download/{output_id}?output=true")
with open('/tmp/test_cleaned.csv', 'wb') as f:
    f.write(r.content)
print(f"   ✓ Saved to /tmp/test_cleaned.csv\n")

print("=" * 60)
print("  ✅ All tests PASSED! API is working correctly!")
print("=" * 60)
print()
print("Next steps:")
print("  - Visit http://localhost:8000/docs for interactive API docs")
print("  - Check API_README.md for complete documentation")
print("  - Try the batch upload and validation endpoints")
print()
