"""
Pydantic models for API requests
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum


class CleaningMode(str, Enum):
    """Cleaning mode options"""
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"


class CleanRequest(BaseModel):
    """Request to clean a dataset"""
    file_id: str = Field(..., description="ID of uploaded file to clean")
    mode: CleaningMode = Field(
        default=CleaningMode.STANDARD,
        description="Cleaning mode: standard, aggressive, or conservative"
    )
    remove_duplicates: bool = Field(default=True, description="Remove duplicate rows")
    handle_nulls: bool = Field(default=True, description="Handle missing values")
    standardize_columns: bool = Field(default=True, description="Standardize column names")
    fix_data_types: bool = Field(default=True, description="Auto-fix data types")
    validate_after: bool = Field(default=True, description="Validate after cleaning")
    export_schema: bool = Field(default=False, description="Export inferred schema")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "abc123",
                "mode": "standard",
                "remove_duplicates": True,
                "handle_nulls": True,
                "standardize_columns": True,
                "fix_data_types": True,
                "validate_after": True,
                "export_schema": False
            }
        }


class ProfileRequest(BaseModel):
    """Request to profile a dataset"""
    file_id: str = Field(..., description="ID of uploaded file to profile")
    include_samples: bool = Field(default=True, description="Include sample values in report")
    detailed: bool = Field(default=False, description="Generate detailed statistics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "abc123",
                "include_samples": True,
                "detailed": False
            }
        }


class ValidateRequest(BaseModel):
    """Request to validate a dataset"""
    file_id: str = Field(..., description="ID of uploaded file to validate")
    schema_id: Optional[str] = Field(None, description="ID of schema to validate against")
    strict_mode: bool = Field(default=False, description="Treat warnings as errors")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "abc123",
                "schema_id": "schema_xyz",
                "strict_mode": False
            }
        }


class SchemaInferRequest(BaseModel):
    """Request to infer schema from data"""
    file_id: str = Field(..., description="ID of uploaded file")
    nullable: bool = Field(default=True, description="Allow null values in schema")
    strict: bool = Field(default=True, description="Strict schema validation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "abc123",
                "nullable": True,
                "strict": True
            }
        }


class WebhookConfig(BaseModel):
    """Webhook configuration for job completion"""
    url: str = Field(..., description="Webhook URL to call on completion")
    headers: Optional[dict] = Field(default=None, description="Custom headers for webhook")
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Webhook URL must start with http:// or https://')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/webhook",
                "headers": {
                    "Authorization": "Bearer token"
                }
            }
        }