"""
Pydantic models for API responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Job status values"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FileInfo(BaseModel):
    """Information about an uploaded file"""
    file_id: str
    filename: str
    size_bytes: int
    format: str
    uploaded_at: datetime
    rows: Optional[int] = None
    columns: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "abc123",
                "filename": "sales_data.csv",
                "size_bytes": 524288,
                "format": "csv",
                "uploaded_at": "2024-01-15T10:30:00",
                "rows": 1000,
                "columns": 12
            }
        }


class UploadResponse(BaseModel):
    """Response after file upload"""
    success: bool
    file_id: str
    filename: str
    size_bytes: int
    message: str = "File uploaded successfully"
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "file_id": "abc123",
                "filename": "sales_data.csv",
                "size_bytes": 524288,
                "message": "File uploaded successfully"
            }
        }


class JobResponse(BaseModel):
    """Response for job creation"""
    job_id: str
    status: JobStatus
    created_at: datetime
    message: str = "Job created successfully"
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "job_xyz",
                "status": "pending",
                "created_at": "2024-01-15T10:30:00",
                "message": "Job created successfully"
            }
        }


class JobStatusResponse(BaseModel):
    """Detailed job status"""
    job_id: str
    status: JobStatus
    progress: int = Field(ge=0, le=100, description="Progress percentage")
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result_file_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "job_xyz",
                "status": "completed",
                "progress": 100,
                "created_at": "2024-01-15T10:30:00",
                "started_at": "2024-01-15T10:30:05",
                "completed_at": "2024-01-15T10:30:15",
                "error": None,
                "result_file_id": "result_abc"
            }
        }


class CleaningReport(BaseModel):
    """Report of cleaning operations"""
    operations_performed: List[str]
    rows_before: int
    rows_after: int
    columns_modified: List[str]
    rows_removed: int
    cells_modified: int
    quality_score_before: float
    quality_score_after: float
    
    class Config:
        json_schema_extra = {
            "example": {
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
        }


class ProfileReport(BaseModel):
    """Data quality profile report"""
    total_rows: int
    total_columns: int
    duplicate_rows: int
    memory_usage_mb: float
    quality_score: float
    issues_summary: Dict[str, int]
    column_details: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_rows": 1000,
                "total_columns": 12,
                "duplicate_rows": 5,
                "memory_usage_mb": 2.5,
                "quality_score": 72.5,
                "issues_summary": {
                    "high_null_columns": 2,
                    "duplicate_rows": 5,
                    "columns_with_mixed_types": 1
                }
            }
        }


class ValidationReport(BaseModel):
    """Validation results"""
    passed: bool
    total_issues: int
    errors: List[Dict[str, str]]
    warnings: List[Dict[str, str]]
    schema_compliant: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "passed": False,
                "total_issues": 3,
                "errors": [
                    {"column": "email", "message": "5 invalid email formats"}
                ],
                "warnings": [
                    {"column": "age", "message": "Contains 2 outliers"}
                ],
                "schema_compliant": True
            }
        }


class HealthResponse(BaseModel):
    """API health check response"""
    status: str = "healthy"
    version: str
    uptime_seconds: float
    timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "uptime_seconds": 3600.5,
                "timestamp": "2024-01-15T10:30:00"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: bool = True
    message: str
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": True,
                "message": "File not found",
                "details": {
                    "file_id": "abc123"
                }
            }
        }