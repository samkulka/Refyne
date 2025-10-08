from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from pydantic import BaseModel
from api.services.batch_service import BatchService
import uuid

router = APIRouter()
batch_service = BatchService()


class BatchCleanRequest(BaseModel):
    """Request to clean multiple files"""
    file_ids: List[str]
    aggressive: bool = False


class BatchJobResponse(BaseModel):
    """Response for batch job creation"""
    job_id: str
    total_files: int
    status: str
    message: str


@router.post("/batch/upload", response_model=dict)
async def batch_upload(files: List[UploadFile] = File(...)):
    """
    Upload multiple files at once
    
    Returns list of file IDs
    """
    try:
        result = await batch_service.upload_multiple(files)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch upload failed: {str(e)}")


@router.post("/batch/clean", response_model=BatchJobResponse)
async def batch_clean(request: BatchCleanRequest):
    """
    Clean multiple files in batch
    
    Creates a batch job and processes files asynchronously
    """
    try:
        result = batch_service.create_clean_job(
            file_ids=request.file_ids,
            aggressive=request.aggressive
        )
        return BatchJobResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch clean failed: {str(e)}")


@router.get("/batch/status/{job_id}")
async def get_batch_status(job_id: str):
    """
    Get status of a batch job
    """
    try:
        status = batch_service.get_job_status(job_id)
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")


@router.get("/batch/jobs")
async def list_batch_jobs():
    """
    List all batch jobs
    """
    try:
        jobs = batch_service.list_jobs()
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")
