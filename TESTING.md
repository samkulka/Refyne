# Testing the Refyne API

This guide shows you how to test the Refyne Data Cleanser API.

## Quick Test

Run the simple test script:

```bash
python3 test_api_simple.py
```

This tests the core workflow: Upload → Profile → Clean → Download

## Comprehensive Test

Run the full test suite:

```bash
# Bash version (with colors)
./test_api_workflow.sh

# Python version (more detailed)
python3 test_api.py
```

## Manual Testing with cURL

### 1. Upload a file

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@/tmp/test_workflow.csv"
```

### 2. Profile the data

```bash
FILE_ID="your-file-id-here"
curl -X POST http://localhost:8000/api/v1/profile \
  -H "Content-Type: application/json" \
  -d "{\"file_id\": \"$FILE_ID\"}"
```

### 3. Clean the data

```bash
curl -X POST http://localhost:8000/api/v1/clean \
  -H "Content-Type: application/json" \
  -d "{\"file_id\": \"$FILE_ID\", \"aggressive\": false}"
```

### 4. Download cleaned file

```bash
OUTPUT_ID="your-output-id-here"
curl -O "http://localhost:8000/api/v1/download/$OUTPUT_ID?output=true"
```

## Testing with Python Requests

```python
import requests

API = "http://localhost:8000/api/v1"

# Upload
with open('data.csv', 'rb') as f:
    r = requests.post(f"{API}/upload", files={'file': f})
file_id = r.json()['file_id']

# Profile
r = requests.post(f"{API}/profile", json={"file_id": file_id})
print(r.json())

# Clean
r = requests.post(f"{API}/clean", json={"file_id": file_id})
output_id = r.json()['output_file_id']

# Download
r = requests.get(f"{API}/download/{output_id}?output=true")
with open('cleaned.csv', 'wb') as f:
    f.write(r.content)
```

## Interactive Testing

Visit the **Swagger UI** for interactive API testing:

```
http://localhost:8000/docs
```

Features:
- Try out all endpoints directly in the browser
- See request/response schemas
- Download responses
- Test authentication (if enabled)

## Advanced Features to Test

### Batch Upload

```bash
curl -X POST http://localhost:8000/api/v1/batch/upload \
  -F "files=@file1.csv" \
  -F "files=@file2.csv" \
  -F "files=@file3.csv"
```

### Custom Cleaning Rules

```bash
curl -X POST http://localhost:8000/api/v1/clean/custom \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "your-file-id",
    "rules": {
      "drop_columns": ["unwanted_col"],
      "lowercase_columns": ["email"],
      "fill_nulls": {"age": 0}
    }
  }'
```

### Schema Validation

```bash
# Infer schema
curl -X POST "http://localhost:8000/api/v1/schema/infer?file_id=$FILE_ID"

# Validate against schema
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{"file_id": "new-file-id", "schema_file_id": "schema-id"}'
```

### List Files

```bash
# List uploaded files
curl http://localhost:8000/api/v1/files?output=false

# List cleaned files
curl http://localhost:8000/api/v1/files?output=true
```

## Test Data

A sample test file is available at `/tmp/test_workflow.csv` with intentional issues:
- Duplicate rows
- Mixed date formats
- Invalid emails
- Missing values
- Inconsistent casing

## Expected Results

After cleaning, you should see:
- ✅ Duplicates removed
- ✅ Column names standardized to snake_case
- ✅ Null values filled with appropriate defaults
- ✅ Invalid data cleaned or removed
- ✅ Consistent text casing

## Troubleshooting

**API not responding?**
- Check if server is running: `curl http://localhost:8000/health`
- Restart server: `uvicorn api.main:app --reload --port 8000`

**File not found error?**
- Verify file ID is correct
- Check file exists: `curl http://localhost:8000/api/v1/files`

**Import errors?**
- Install dependencies: `pip install -r requirements-api.txt`

## Performance Testing

For load testing, use tools like:
- **Apache Bench**: `ab -n 100 -c 10 http://localhost:8000/health`
- **wrk**: `wrk -t12 -c400 -d30s http://localhost:8000/`
- **Locust**: Write custom test scenarios

## Continuous Integration

Add to your CI/CD pipeline:

```yaml
# .github/workflows/test-api.yml
- name: Test API
  run: |
    uvicorn api.main:app --host 0.0.0.0 --port 8000 &
    sleep 5
    python3 test_api_simple.py
```

---

**Questions?** Check the [API_README.md](API_README.md) for complete documentation.
