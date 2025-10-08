"""
Storage service for managing files
Abstracts storage backend (local, S3, GCS, etc.)
"""
from pathlib import Path
from typing import Optional, BinaryIO
import shutil
import logging
from datetime import datetime

from api.config import settings
from api.utils.file_handler import FileHandler

logger = logging.getLogger(__name__)


class StorageService:
    """
    File storage service
    
    Currently uses local filesystem, but designed to be extended
    for cloud storage (S3, GCS, Azure Blob, etc.)
    """
    
    def __init__(self):
        self.upload_dir = settings.upload_dir
        self.output_dir = settings.output_dir
        self.temp_dir = settings.temp_dir
    
    async def save_upload(self, file_id: str, content: bytes, extension: str) -> Path:
        """
        Save an uploaded file
        
        Args:
            file_id: Unique file identifier
            content: File content as bytes
            extension: File extension (e.g., '.csv')
            
        Returns:
            Path to saved file
        """
        filename = f"{file_id}{extension}"
        file_path = self.upload_dir / filename
        
        # Write file
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"Saved upload: {filename} ({len(content)} bytes)")
        
        return file_path
    
    async def save_output(self, file_id: str, source_path: Path) -> Path:
        """
        Save a processed output file
        
        Args:
            file_id: Unique file identifier
            source_path: Path to source file to copy
            
        Returns:
            Path to saved output file
        """
        extension = source_path.suffix
        filename = f"{file_id}{extension}"
        output_path = self.output_dir / filename
        
        # Copy file
        shutil.copy2(source_path, output_path)
        
        logger.info(f"Saved output: {filename}")
        
        return output_path
    
    def get_file(self, file_id: str, file_type: str = 'upload') -> Optional[Path]:
        """
        Get path to a file by ID
        
        Args:
            file_id: File identifier
            file_type: Type of file ('upload', 'output', 'temp')
            
        Returns:
            Path to file if found, None otherwise
        """
        if file_type == 'upload':
            directory = self.upload_dir
        elif file_type == 'output':
            directory = self.output_dir
        elif file_type == 'temp':
            directory = self.temp_dir
        else:
            raise ValueError(f"Invalid file_type: {file_type}")
        
        return FileHandler.find_file_by_id(file_id, directory)
    
    def delete_file(self, file_id: str, file_type: str = 'upload') -> bool:
        """
        Delete a file by ID
        
        Args:
            file_id: File identifier
            file_type: Type of file ('upload', 'output', 'temp')
            
        Returns:
            True if deleted, False if not found
        """
        file_path = self.get_file(file_id, file_type)
        
        if not file_path:
            return False
        
        try:
            file_path.unlink()
            logger.info(f"Deleted file: {file_path.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {file_path.name}: {e}")
            return False
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Clean up old files from all directories
        
        Args:
            max_age_hours: Maximum file age in hours
        """
        logger.info(f"Starting cleanup of files older than {max_age_hours} hours")
        
        upload_deleted = FileHandler.cleanup_old_files(self.upload_dir, max_age_hours)
        output_deleted = FileHandler.cleanup_old_files(self.output_dir, max_age_hours)
        temp_deleted = FileHandler.cleanup_old_files(self.temp_dir, max_age_hours)
        
        total_deleted = upload_deleted + output_deleted + temp_deleted
        
        logger.info(f"Cleanup complete: {total_deleted} total files deleted")
        
        return {
            "upload_deleted": upload_deleted,
            "output_deleted": output_deleted,
            "temp_deleted": temp_deleted,
            "total_deleted": total_deleted
        }
    
    def get_storage_stats(self) -> dict:
        """
        Get storage statistics
        
        Returns:
            Dictionary with storage stats
        """
        upload_stats = FileHandler.get_directory_size(self.upload_dir)
        output_stats = FileHandler.get_directory_size(self.output_dir)
        temp_stats = FileHandler.get_directory_size(self.temp_dir)
        
        total_size = (
            upload_stats['total_size_bytes'] +
            output_stats['total_size_bytes'] +
            temp_stats['total_size_bytes']
        )
        
        total_files = (
            upload_stats['file_count'] +
            output_stats['file_count'] +
            temp_stats['file_count']
        )
        
        return {
            "upload": upload_stats,
            "output": output_stats,
            "temp": temp_stats,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_files": total_files,
            "timestamp": datetime.now().isoformat()
        }


# Singleton instance
storage_service = StorageService()