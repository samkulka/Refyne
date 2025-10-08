"""
Data profiling endpoints
"""
from fastapi import APIRouter, HTTPException, status
from pathlib import Path
import logging

from api.models.requests import ProfileRequest
from api.models.responses import ProfileReport
from api.config import settings
from src.utils.connectors import DataConnector
from src.profiler import DataProfiler

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/profile", response_model=ProfileReport)
async def profile_data(request: ProfileRequest):
    """
    Generate a data quality profile report
    
    Analyzes the dataset and returns quality metrics, issues, and statistics
    """
    try:
        # Find the file
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
        
        logger.info(f"Profiling file: {request.file_id}")
        
        # Load data
        df = DataConnector.read_file(str(file_path))
        
        # Profile the dataset
        profiler = DataProfiler()
        profile = profiler.profile_dataset(df)
        
        # Prepare column details if requested
        column_details = None
        if request.detailed:
            column_details = []
            for col_profile in profile.column_profiles:
                col_dict = {
                    "name": col_profile.name,
                    "type": col_profile.inferred_type,
                    "dtype": col_profile.dtype,
                    "null_percentage": col_profile.null_percentage,
                    "unique_count": col_profile.unique_count,
                    "issues": col_profile.issues
                }
                
                if request.include_samples:
                    col_dict["sample_values"] = col_profile.sample_values
                
                if col_profile.numeric_stats:
                    col_dict["numeric_stats"] = col_profile.numeric_stats
                
                column_details.append(col_dict)
        
        logger.info(f"Profile complete for {request.file_id}: score {profile.overall_quality_score}/100")
        
        return ProfileReport(
            total_rows=profile.total_rows,
            total_columns=profile.total_columns,
            duplicate_rows=profile.duplicate_rows,
            memory_usage_mb=profile.memory_usage_mb,
            quality_score=profile.overall_quality_score,
            issues_summary=profile.issues_summary,
            column_details=column_details
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to profile data: {str(e)}"
        )


@router.get("/profile/{file_id}/quick", response_model=ProfileReport)
async def quick_profile(file_id: str):
    """
    Quick profile with basic metrics only (faster)
    """
    request = ProfileRequest(
        file_id=file_id,
        include_samples=False,
        detailed=False
    )
    return await profile_data(request)