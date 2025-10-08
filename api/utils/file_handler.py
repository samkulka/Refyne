"""
File handling utilities for the API
"""
from pathlib import Path
from typing import Optional, Tuple
import hashlib
import mimetypes
import logging

from api.config import settings

logger = logging.getLogger(__name__)


class FileHandler:
    """Utility class for file operations"""
    
    @staticmethod
    def get_file_hash(file_path: Path) -> str:
        """
        Calculate SHA256 hash of a file
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex string of file hash
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    @staticmethod
    def find_file_by_id(file_id: str, directory: Path) -> Optional[Path]:
        """
        Find a file by its ID in a directory
        
        Args:
            file_id: File identifier
            directory: Directory to search
            
        Returns:
            Path to file if found, None otherwise
        """
        for ext in settings.allowed_extensions:
            candidate = directory / f"{file_id}{ext}"
            if candidate.exists():
                return candidate
        
        return None
    
    @staticmethod
    def get_file_info(file_path: Path) -> dict:
        """
        Get detailed information about a file
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        stats = file_path.stat()
        
        return {
            "name": file_path.name,
            "size_bytes": stats.st_size,
            "size_mb": round(stats.st_size / (1024 * 1024), 2),
            "extension": file_path.suffix,
            "mime_type": mimetypes.guess_type(file_path)[0],
            "created": stats.st_ctime,
            "modified": stats.st_mtime
        }
    
    @staticmethod
    def validate_file_size(size_bytes: int) -> Tuple[bool, Optional[str]]:
        """
        Validate file size against limits
        
        Args:
            size_bytes: File size in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        max_size = settings.max_file_size_mb * 1024 * 1024
        
        if size_bytes > max_size:
            return False, f"File too large. Maximum size: {settings.max_file_size_mb}MB"
        
        if size_bytes == 0:
            return False, "File is empty"
        
        return True, None
    
    @staticmethod
    def validate_file_extension(filename: str) -> Tuple[bool, Optional[str]]:
        """
        Validate file extension
        
        Args:
            filename: Name of file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        ext = Path(filename).suffix.lower()
        
        if ext not in settings.allowed_extensions:
            return False, f"File type {ext} not supported. Allowed: {', '.join(settings.allowed_extensions)}"
        
        return True, None
    
    @staticmethod
    def cleanup_old_files(directory: Path, max_age_hours: int = 24):
        """
        Clean up files older than specified age
        
        Args:
            directory: Directory to clean
            max_age_hours: Maximum age in hours
        """
        import time
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        deleted_count = 0
        
        for file_path in directory.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                
                if file_age > max_age_seconds:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        logger.info(f"Deleted old file: {file_path.name}")
                    except Exception as e:
                        logger.error(f"Failed to delete {file_path.name}: {e}")
        
        if deleted_count > 0:
            logger.info(f"Cleanup complete: deleted {deleted_count} old files from {directory}")
        
        return deleted_count
    
    @staticmethod
    def get_directory_size(directory: Path) -> dict:
        """
        Calculate total size of files in a directory
        
        Args:
            directory: Directory to analyze
            
        Returns:
            Dictionary with size information
        """
        total_size = 0
        file_count = 0
        
        for file_path in directory.iterdir():
            if file_path.is_file():
                total_size += file_path.stat().st_size
                file_count += 1
        
        return {
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_count": file_count
        }