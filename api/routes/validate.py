from fastapi import APIRouter, HTTPException, UploadFile, File
from api.models.requests import ValidateRequest
from api.models.responses import ValidationResponse
from api.services.validator_service import ValidatorService
import os
import uuid

router = APIRouter()
validator_service = ValidatorService()


@router.post("/validate", response_model=ValidationResponse)
async def validate_data(request: ValidateRequest):
    """
    Validate data quality and optionally check against a schema
    
    Returns validation report with:
    - Pass/fail status
    - Errors found
    - Warnings
    """
    try:
        result = validator_service.validate_data(
            file_id=request.file_id,
            schema_file_id=request.schema_file_id
        )
        return ValidationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.post("/schema/infer")
async def infer_schema(file_id: str):
    """
    Infer and generate a schema from a clean dataset
    
    Returns the schema file ID for future validation
    """
    try:
        result = validator_service.infer_schema(file_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema inference failed: {str(e)}")


@router.post("/schema/upload")
async def upload_schema(file: UploadFile = File(...)):
    """
    Upload a schema file (YAML format)
    """
    if not file.filename.endswith('.yaml') and not file.filename.endswith('.yml'):
        raise HTTPException(status_code=400, detail="Schema must be a YAML file")
    
    try:
        schema_id = str(uuid.uuid4())
        schema_dir = "storage/schemas"
        os.makedirs(schema_dir, exist_ok=True)
        
        schema_path = os.path.join(schema_dir, f"{schema_id}_{file.filename}")
        
        contents = await file.read()
        with open(schema_path, "wb") as f:
            f.write(contents)
        
        return {
            "schema_id": schema_id,
            "filename": file.filename,
            "message": "Schema uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema upload failed: {str(e)}")
