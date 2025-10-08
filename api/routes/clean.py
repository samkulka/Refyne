"""
Data cleaning endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from fastapi.responses import FileResponse
from pathlib import Path
import uuid
import logging
from datetime import datetime

from api.models.requests import CleanRequest, CleaningMode
from api.models.responses import JobResponse, JobStatusResponse, JobStatus, CleaningReport as APICleaningReport
from api.config import settings
from src.utils.connectors import DataConnector
from src.profiler import DataProfiler
from src.cleaner import DataCleaner
from src.validator import DataValidator

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory job store (use Redis/DB in production)
jobs_store = {}


@router.post("/clean", response_model=JobResponse)
async def create_cleaning_job(
    request: CleanRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new data cleaning job
    
    Returns a job ID that can be used to check status and download results
    """
    try:
        # Validate file exists
        file_path = None
        for ext in settings.allowed_extensions:
            candidate = settings.upload_dir / f"{request.file_id}{ext}"
            if candidate.exists():
                file_path = candidate
                break
        
        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {request.file_id} not found"
            )
        
        # Create job
        job_id = str(uuid.uuid4())
        
        job_data = {
            "job_id": job_id,
            "status": JobStatus.PENDING,
            "created_at": datetime.now(),
            "started_at": None,
            "completed_at": None,
            "file_id": request.file_id,
            "file_path": str(file_path),
            "request": request.dict(),
            "result_file_id": None,
            "error": None,
            "progress": 0,
            "report": None
        }
        
        jobs_store[job_id] = job_data
        
        # Add to background tasks
        background_tasks.add_task(
            process_cleaning_job,
            job_id,
            str(file_path),
            request
        )
        
        logger.info(f"Cleaning job created: {job_id} for file {request.file_id}")
        
        return JobResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            created_at=job_data["created_at"],
            message="Cleaning job created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create cleaning job error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create cleaning job: {str(e)}"
        )


async def process_cleaning_job(job_id: str, file_path: str, request: CleanRequest):
    """
    Background task to process cleaning job
    """
    try:
        # Update status
        jobs_store[job_id]["status"] = JobStatus.PROCESSING
        jobs_store[job_id]["started_at"] = datetime.now()
        jobs_store[job_id]["progress"] = 10
        
        logger.info(f"Processing cleaning job: {job_id}")
        
        # Load data
        df = DataConnector.read_file(file_path)
        jobs_store[job_id]["progress"] = 20
        
        # Profile before cleaning
        profiler = DataProfiler()
        profile_before = profiler.profile_dataset(df)
        quality_before = profile_before.overall_quality_score
        jobs_store[job_id]["progress"] = 40
        
        # Clean data
        aggressive = request.mode == CleaningMode.AGGRESSIVE
        cleaner = DataCleaner(aggressive=aggressive)
        df_clean, clean_report = cleaner.clean(df)
        jobs_store[job_id]["progress"] = 70
        
        # Profile after cleaning
        profile_after = profiler.profile_dataset(df_clean)
        quality_after = profile_after.overall_quality_score
        jobs_store[job_id]["progress"] = 80
        
        # Validate if requested
        validation_passed = True
        if request.validate_after:
            validator = DataValidator(strict=False)
            validation_report = validator.validate(df_clean)
            validation_passed = validation_report.passed
        
        jobs_store[job_id]["progress"] = 90
        
        # Save cleaned data
        result_file_id = str(uuid.uuid4())
        file_ext = Path(file_path).suffix
        output_path = settings.output_dir / f"{result_file_id}{file_ext}"
        DataConnector.write_file(df_clean, str(output_path))
        
        # Store report
        api_report = APICleaningReport(
            operations_performed=clean_report.operations_performed,
            rows_before=clean_report.rows_before,
            rows_after=clean_report.rows_after,
            columns_modified=clean_report.columns_modified,
            rows_removed=clean_report.rows_removed,
            cells_modified=clean_report.cells_modified,
            quality_score_before=quality_before,
            quality_score_after=quality_after
        )
        
        # Update job as completed
        jobs_store[job_id].update({
            "status": JobStatus.COMPLETED,
            "completed_at": datetime.now(),
            "result_file_id": result_file_id,
            "progress": 100,
            "report": api_report.dict()
        })
        
        logger.info(f"Cleaning job completed: {job_id}")
        
    except Exception as e:
        logger.error(f"Cleaning job failed: {job_id} - {e}", exc_info=True)
        jobs_store[job_id].update({
            "status": JobStatus.FAILED,
            "completed_at": datetime.now(),
            "error": str(e),
            "progress": 0
        })


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status of a cleaning job
    """
    if job_id not in jobs_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    job = jobs_store[job_id]
    
    return JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        progress=job["progress"],
        created_at=job["created_at"],
        started_at=job.get("started_at"),
        completed_at=job.get("completed_at"),
        error=job.get("error"),
        result_file_id=job.get("result_file_id")
    )


@router.get("/jobs/{job_id}/report", response_model=APICleaningReport)
async def get_job_report(job_id: str):
    """
    Get the cleaning report for a completed job
    """
    if job_id not in jobs_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    job = jobs_store[job_id]
    
    if job["status"] != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job {job_id} is not completed yet"
        )
    
    if not job.get("report"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report not available for job {job_id}"
        )
    
    return APICleaningReport(**job["report"])


@router.get("/jobs/{job_id}/download")
async def download_cleaned_file(job_id: str):
    """
    Download the cleaned data file
    """
    if job_id not in jobs_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    job = jobs_store[job_id]
    
    if job["status"] != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job {job_id} is not completed yet. Status: {job['status']}"
        )
    
    result_file_id = job.get("result_file_id")
    if not result_file_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Result file not found for job {job_id}"
        )
    
    # Find the result file
    result_path = None
    for ext in settings.allowed_extensions:
        candidate = settings.output_dir / f"{result_file_id}{ext}"
        if candidate.exists():
            result_path = candidate
            break
    
    if not result_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Result file {result_file_id} not found on disk"
        )
    
    # Return file
    original_filename = Path(job["file_path"]).stem
    download_filename = f"{original_filename}_clean{result_path.suffix}"
    
    return FileResponse(
        path=result_path,
        filename=download_filename,
        media_type="application/octet-stream"
    )


@router.delete("/jobs/{job_id}")
async def cancel_job(job_id: str):
    """
    Cancel a pending or running job
    """
    if job_id not in jobs_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    job = jobs_store[job_id]
    
    if job["status"] in [JobStatus.COMPLETED, JobStatus.FAILED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job with status: {job['status']}"
        )
    
    jobs_store[job_id]["status"] = JobStatus.CANCELLED
    jobs_store[job_id]["completed_at"] = datetime.now()
    
    logger.info(f"Job cancelled: {job_id}")
    
    return {"success": True, "message": f"Job {job_id} cancelled"}