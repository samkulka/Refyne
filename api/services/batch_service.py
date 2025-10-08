from typing import List, Dict, Any
from fastapi import UploadFile
import os
import uuid
from datetime import datetime
import json

from api.services.cleaner_service import CleanerService
from api.services.storage_service import StorageService


class BatchService:
    """Service for batch processing operations"""
    
    JOBS_DIR = "storage/jobs"
    
    def __init__(self):
        self.cleaner = CleanerService()
        self.storage = StorageService()
        os.makedirs(self.JOBS_DIR, exist_ok=True)
    
    async def upload_multiple(self, files: List[UploadFile]) -> Dict[str, Any]:
        """Upload multiple files"""
        uploaded = []
        errors = []
        
        for file in files:
            try:
                # Validate file extension
                allowed_extensions = {'.csv', '.xlsx', '.xls', '.json', '.parquet'}
                file_ext = os.path.splitext(file.filename)[1].lower()
                
                if file_ext not in allowed_extensions:
                    errors.append({
                        "filename": file.filename,
                        "error": f"Unsupported file format: {file_ext}"
                    })
                    continue
                
                # Generate unique file ID
                file_id = str(uuid.uuid4())
                safe_filename = f"{file_id}_{file.filename}"
                file_path = os.path.join(self.storage.UPLOAD_DIR, safe_filename)
                
                # Save file
                contents = await file.read()
                with open(file_path, "wb") as f:
                    f.write(contents)
                
                uploaded.append({
                    "file_id": file_id,
                    "filename": file.filename,
                    "size_bytes": len(contents),
                    "file_type": file_ext
                })
                
            except Exception as e:
                errors.append({
                    "filename": file.filename,
                    "error": str(e)
                })
        
        return {
            "total_files": len(files),
            "uploaded": len(uploaded),
            "failed": len(errors),
            "files": uploaded,
            "errors": errors,
            "message": f"Uploaded {len(uploaded)}/{len(files)} files successfully"
        }
    
    def create_clean_job(self, file_ids: List[str], aggressive: bool = False) -> Dict[str, Any]:
        """Create a batch cleaning job"""
        job_id = str(uuid.uuid4())
        
        job_data = {
            "job_id": job_id,
            "file_ids": file_ids,
            "aggressive": aggressive,
            "total_files": len(file_ids),
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "completed_files": 0,
            "results": []
        }
        
        # Save job metadata
        job_path = os.path.join(self.JOBS_DIR, f"{job_id}.json")
        with open(job_path, "w") as f:
            json.dump(job_data, f, indent=2)
        
        # Process files (in a real app, this would be async/background task)
        self._process_batch_job(job_id, file_ids, aggressive)
        
        return {
            "job_id": job_id,
            "total_files": len(file_ids),
            "status": "processing",
            "message": f"Batch job created with {len(file_ids)} files"
        }
    
    def _process_batch_job(self, job_id: str, file_ids: List[str], aggressive: bool):
        """Process batch cleaning job"""
        job_path = os.path.join(self.JOBS_DIR, f"{job_id}.json")
        
        with open(job_path, "r") as f:
            job_data = json.load(f)
        
        job_data["status"] = "processing"
        
        for file_id in file_ids:
            try:
                # Clean the file
                result = self.cleaner.clean_data(file_id, aggressive=aggressive)
                job_data["results"].append({
                    "file_id": file_id,
                    "status": "success",
                    "output_file_id": result["output_file_id"]
                })
                job_data["completed_files"] += 1
                
            except Exception as e:
                job_data["results"].append({
                    "file_id": file_id,
                    "status": "failed",
                    "error": str(e)
                })
        
        job_data["status"] = "completed"
        job_data["completed_at"] = datetime.utcnow().isoformat()
        
        # Save updated job data
        with open(job_path, "w") as f:
            json.dump(job_data, f, indent=2)
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a batch job"""
        job_path = os.path.join(self.JOBS_DIR, f"{job_id}.json")
        
        if not os.path.exists(job_path):
            return None
        
        with open(job_path, "r") as f:
            return json.load(f)
    
    def list_jobs(self) -> Dict[str, Any]:
        """List all batch jobs"""
        jobs = []
        
        for filename in os.listdir(self.JOBS_DIR):
            if filename.endswith('.json'):
                job_path = os.path.join(self.JOBS_DIR, filename)
                with open(job_path, "r") as f:
                    job_data = json.load(f)
                    jobs.append({
                        "job_id": job_data["job_id"],
                        "status": job_data["status"],
                        "total_files": job_data["total_files"],
                        "completed_files": job_data["completed_files"],
                        "created_at": job_data["created_at"]
                    })
        
        # Sort by created_at (newest first)
        jobs.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "total_jobs": len(jobs),
            "jobs": jobs
        }
