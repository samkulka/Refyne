"""
File upload endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pathlib import Path
import uuid
import aiofiles
from datetime import datetime
import logging

from api.models.responses import UploadResponse, FileInfo, ErrorResponse
from api.config import settings
from src.utils.connectors import DataConnector

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file for processing
    
    Accepts CSV, Excel, JSON, and Parquet files
    """
    try:
        # Validate file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in settings.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_extension} not supported. Allowed: {settings.allowed_extensions}"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Create file path
        safe_filename = f"{file_id}{file_extension}"
        file_path = settings.upload_dir / safe_filename
        
        # Read and save file
        content = await file.read()
        file_size = len(content)
        
        # Check file size
        max_size_bytes = settings.max_file_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
            )
        
        # Write file asynchronously
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        logger.info(f"File uploaded: {file_id} ({file.filename}, {file_size} bytes)")
        
        return UploadResponse(
            success=True,
            file_id=file_id,
            filename=file.filename,
            size_bytes=file_size,
            message="File uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/files/{file_id}", response_model=FileInfo)
async def get_file_info(file_id: str):
    """
    Get information about an uploaded file
    """
    try:
        # Find the file
        file_path = None
        for ext in settings.allowed_extensions:
            candidate = settings.upload_dir / f"{file_id}{ext}"
            if candidate.exists():
                file_path = candidate
                break
        
        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {file_id} not found"
            )
        
        # Get file stats
        stats = file_path.stat()
        
        # Try to read file to get row/column count
        rows, columns = None, None
        try:
            df = DataConnector.read_file(str(file_path))
            rows = len(df)
            columns = len(df.columns)
        except:
            pass
        
        return FileInfo(
            file_id=file_id,
            filename=file_path.name,
            size_bytes=stats.st_size,
            format=file_path.suffix.lstrip('.'),
            uploaded_at=datetime.fromtimestamp(stats.st_ctime),
            rows=rows,
            columns=columns
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get file info error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file info: {str(e)}"
        )


@router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """
    Delete an uploaded file
    """
    try:
        # Find and delete the file
        deleted = False
        for ext in settings.allowed_extensions:
            file_path = settings.upload_dir / f"{file_id}{ext}"
            if file_path.exists():
                file_path.unlink()
                deleted = True
                logger.info(f"File deleted: {file_id}")
                break
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {file_id} not found"
            )
        
        return {"success": True, "message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete file error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )