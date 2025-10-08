from typing import Dict, Any, Optional
import os
from datetime import datetime

from src.validator import DataValidator
from src.utils.connectors import DataConnector
from api.services.storage_service import StorageService


class ValidatorService:
    """Service for data validation operations"""
    
    SCHEMA_DIR = "storage/schemas"
    
    def __init__(self):
        self.storage = StorageService()
        os.makedirs(self.SCHEMA_DIR, exist_ok=True)
        
    def validate_data(self, file_id: str, schema_file_id: Optional[str] = None) -> Dict[str, Any]:
        """Validate data with optional schema"""
        file_path = self.storage.get_file_path(file_id)
        df = DataConnector.read_file(file_path)
        
        validator = DataValidator()
        
        # Load schema if provided
        schema = None
        if schema_file_id:
            schema_path = self._get_schema_path(schema_file_id)
            schema = DataValidator.load_schema(schema_path)
        
        # Validate
        report = validator.validate(df, schema)
        
        # Convert to response format
        return {
            "file_id": file_id,
            "passed": report.passed,
            "errors": [f"{issue.column or 'General'}: {issue.message}" for issue in report.errors],
            "warnings": [f"{issue.column or 'General'}: {issue.message}" for issue in report.warnings],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def infer_schema(self, file_id: str) -> Dict[str, Any]:
        """Infer schema from a dataset"""
        file_path = self.storage.get_file_path(file_id)
        df = DataConnector.read_file(file_path)
        
        # Generate schema
        schema = DataValidator.create_schema_from_df(df)
        
        # Save schema
        schema_id = file_id  # Use same ID as the file
        schema_path = os.path.join(self.SCHEMA_DIR, f"{schema_id}_schema.yaml")
        DataValidator.save_schema(schema, schema_path)
        
        return {
            "schema_id": schema_id,
            "schema_path": schema_path,
            "columns": len(df.columns),
            "message": "Schema inferred and saved successfully"
        }
    
    def _get_schema_path(self, schema_id: str) -> str:
        """Get schema file path by ID"""
        import glob
        pattern = os.path.join(self.SCHEMA_DIR, f"{schema_id}_*")
        matches = glob.glob(pattern)
        
        if not matches:
            raise FileNotFoundError(f"Schema not found: {schema_id}")
        
        return matches[0]
