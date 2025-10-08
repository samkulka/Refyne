from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from api.services.storage_service import StorageService

router = APIRouter()
storage_service = StorageService()


@router.get("/download/{file_id}")
async def download_file(file_id: str, output: bool = False):
    """
    Download a file by ID
    
    Args:
        file_id: The unique file identifier
        output: If True, download from outputs folder (cleaned files)
    """
    try:
        directory = storage_service.OUTPUT_DIR if output else storage_service.UPLOAD_DIR
        file_path = storage_service.get_file_path(file_id, directory)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        filename = os.path.basename(file_path)
        # Remove UUID prefix for cleaner download name
        clean_filename = "_".join(filename.split("_")[1:])
        
        return FileResponse(
            path=file_path,
            filename=clean_filename,
            media_type="application/octet-stream"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/files")
async def list_files(output: bool = False):
    """
    List all uploaded or cleaned files
    
    Args:
        output: If True, list output files; otherwise list uploaded files
    """
    try:
        directory = storage_service.OUTPUT_DIR if output else storage_service.UPLOAD_DIR
        
        if not os.path.exists(directory):
            return {"files": []}
        
        files = []
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_id = filename.split("_")[0]
                files.append({
                    "file_id": file_id,
                    "filename": "_".join(filename.split("_")[1:]),
                    "full_path": filename,
                    "size_bytes": os.path.getsize(file_path),
                    "modified_at": os.path.getmtime(file_path)
                })
        
        # Sort by modified time (newest first)
        files.sort(key=lambda x: x["modified_at"], reverse=True)
        
        return {
            "count": len(files),
            "type": "outputs" if output else "uploads",
            "files": files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")
