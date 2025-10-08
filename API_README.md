# 🚀 Refyne API Documentation

REST API for the Refyne Data Cleanser - automatically clean, validate, and transform messy data.

## Quick Start

### Option 1: Run Locally

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-api.txt

# Create storage directories
bash setup_api.sh

# Start the API
python -m api.main

# Or with uvicorn directly
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`

### Option 2: Run with Docker

```bash
# Build and start
docker-compose up --build

# The API will be available at http://localhost:8000
```

## 📖 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔑 Authentication

All endpoints (except `/health`) require an API key.

### Get Your API Key

In development mode, an API key is automatically generated and printed to the console:

```
🔑 Development API Key: refyne_xxxxxxxxxxxxx
```

### Use the API Key

Include it in the `X-API-Key` header:

```bash
curl -H "X-API-Key: refyne_your_key_here" \
     http://localhost:8000/api/v1/health
```

## 📡 API Endpoints

### Health Check
```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 123.45,
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### Upload File
```http
POST /api/v1/upload
Content-Type: multipart/form-data
X-API-Key: your_api_key
```

**Body:**
- `file`: File to upload (CSV, Excel, JSON, Parquet)

**Response:**
```json
{
  "success": true,
  "file_id": "abc123-def456",
  "filename": "sales_data.csv",
  "size_bytes": 524288,
  "message": "File uploaded successfully"
}
```

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "X-API-Key: refyne_your_key" \
  -F "file=@data.csv"
```

---

### Profile Data
```http
POST /api/v1/profile
Content-Type: application/json
X-API-Key: your_api_key
```

**Body:**
```json
{
  "file_id": "abc123-def456",
  "include_samples": true,
  "detailed": false
}
```

**Response:**
```json
{
  "total_rows": 1000,
  "total_columns": 12,
  "duplicate_rows": 5,
  "memory_usage_mb": 2.5,
  "quality_score": 72.5,
  "issues_summary": {
    "high_null_columns": 2,
    "duplicate_rows": 5
  }
}
```

---

### Clean Data
```http
POST /api/v1/clean
Content-Type: application/json
X-API-Key: your_api_key
```

**Body:**
```json
{
  "file_id": "abc123-def456",
  "mode": "standard",
  "remove_duplicates": true,
  "handle_nulls": true,
  "standardize_columns": true,
  "fix_data_types": true,
  "validate_after": true,
  "export_schema": false
}
```

**Response:**
```json
{
  "job_id": "job_xyz789",
  "status": "pending",
  "created_at": "2024-01-15T10:30:00",
  "message": "Cleaning job created successfully"
}
```

---

### Check Job Status
```http
GET /api/v1/jobs/{job_id}
X-API-Key: your_api_key
```

**Response:**
```json
{
  "job_id": "job_xyz789",
  "status": "completed",
  "progress": 100,
  "created_at": "2024-01-15T10:30:00",
  "started_at": "2024-01-15T10:30:05",
  "completed_at": "2024-01-15T10:30:15",
  "error": null,
  "result_file_id": "result_abc123"
}
```

**Status Values:**
- `pending` - Job is queued
- `processing` - Job is running
- `completed` - Job finished successfully
- `failed` - Job encountered an error
- `cancelled` - Job was cancelled

---

### Get Cleaning Report
```http
GET /api/v1/jobs/{job_id}/report
X-API-Key: your_api_key
```

**Response:**
```json
{
  "operations_performed": [
    "Removed 5 duplicate rows",
    "Standardized 12 column names",
    "Filled 45 null values"
  ],
  "rows_before": 1000,
  "rows_after": 995,
  "columns_modified": ["email", "date", "status"],
  "rows_removed": 5,
  "cells_modified": 67,
  "quality_score_before": 72.5,
  "quality_score_after": 94.3
}
```

---

### Download Cleaned File
```http
GET /api/v1/jobs/{job_id}/download
X-API-Key: your_api_key
```

**Response:** File download (CSV/Excel/etc.)

---

## 🔄 Complete Workflow Example

```bash
# 1. Upload file
UPLOAD_RESPONSE=$(curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "X-API-Key: refyne_your_key" \
  -F "file=@messy_data.csv")

FILE_ID=$(echo $UPLOAD_RESPONSE | jq -r '.file_id')
echo "Uploaded file: $FILE_ID"

# 2. Profile the data (optional)
curl -X POST "http://localhost:8000/api/v1/profile" \
  -H "X-API-Key: refyne_your_key" \
  -H "Content-Type: application/json" \
  -d "{\"file_id\": \"$FILE_ID\", \"detailed\": true}"

# 3. Start cleaning job
CLEAN_RESPONSE=$(curl -X POST "http://localhost:8000/api/v1/clean" \
  -H "X-API-Key: refyne_your_key" \
  -H "Content-Type: application/json" \
  -d "{\"file_id\": \"$FILE_ID\", \"mode\": \"standard\"}")

JOB_ID=$(echo $CLEAN_RESPONSE | jq -r '.job_id')
echo "Job created: $JOB_ID"

# 4. Poll for completion
while true; do
  STATUS=$(curl -s "http://localhost:8000/api/v1/jobs/$JOB_ID" \
    -H "X-API-Key: refyne_your_key" | jq -r '.status')
  
  echo "Status: $STATUS"
  
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi
  
  sleep 2
done

# 5. Get the report
curl "http://localhost:8000/api/v1/jobs/$JOB_ID/report" \
  -H "X-API-Key: refyne_your_key"

# 6. Download cleaned file
curl "http://localhost:8000/api/v1/jobs/$JOB_ID/download" \
  -H "X-API-Key: refyne_your_key" \
  -o cleaned_data.csv

echo "✅ Done! Cleaned file saved to cleaned_data.csv"
```

## 🐍 Python Client Example

```python
import requests
import time

API_URL = "http://localhost:8000/api/v1"
API_KEY = "refyne_your_key"

headers = {"X-API-Key": API_KEY}

# Upload file
with open("messy_data.csv", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{API_URL}/upload", files=files, headers=headers)
    file_id = response.json()["file_id"]
    print(f"Uploaded: {file_id}")

# Start cleaning
clean_request = {
    "file_id": file_id,
    "mode": "standard",
    "validate_after": True
}
response = requests.post(f"{API_URL}/clean", json=clean_request, headers=headers)
job_id = response.json()["job_id"]
print(f"Job ID: {job_id}")

# Poll for completion
while True:
    response = requests.get(f"{API_URL}/jobs/{job_id}", headers=headers)
    status = response.json()["status"]
    progress = response.json()["progress"]
    
    print(f"Status: {status} ({progress}%)")
    
    if status in ["completed", "failed"]:
        break
    
    time.sleep(2)

# Download result
if status == "completed":
    response = requests.get(f"{API_URL}/jobs/{job_id}/download", headers=headers)
    
    with open("cleaned_data.csv", "wb") as f:
        f.write(response.content)
    
    print("✅ Cleaned file downloaded!")
```

## ⚙️ Configuration

Edit `.env` file:

```env
# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Security
SECRET_KEY=your-secret-key-change-this
API_KEY_PREFIX=refyne_

# Storage
MAX_FILE_SIZE_MB=100

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=3600

# Database (optional)
DATABASE_URL=postgresql://user:pass@localhost/refyne

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
```

## 🚦 Rate Limits

- **Free tier**: 100 requests per hour
- Limits apply per API key or IP address
- When exceeded, receive `429 Too Many Requests`
- Check headers:
  - `X-RateLimit-Limit`: Maximum requests
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: When limit resets
  - `Retry-After`: Seconds to wait

## 📊 Supported File Formats

- ✅ CSV (`.csv`)
- ✅ Excel (`.xlsx`, `.xls`)