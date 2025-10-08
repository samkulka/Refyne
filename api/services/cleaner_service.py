"""
Cleaner service - wraps core cleaning logic for API use
"""
from pathlib import Path
import logging
from typing import Tuple, Optional

from src.utils.connectors import DataConnector
from src.profiler import DataProfiler
from src.cleaner import DataCleaner, CleaningReport
from src.validator import DataValidator, ValidationReport
from api.models.requests import CleaningMode

logger = logging.getLogger(__name__)


class CleanerService:
    """
    Service layer for data cleaning operations
    
    Wraps the core cleaning logic with API-specific functionality
    """
    
    @staticmethod
    def clean_file(
        input_path: Path,
        output_path: Path,
        mode: CleaningMode = CleaningMode.STANDARD,
        validate: bool = True
    ) -> Tuple[CleaningReport, Optional[ValidationReport], float, float]:
        """
        Clean a data file
        
        Args:
            input_path: Path to input file
            output_path: Path to save cleaned file
            mode: Cleaning mode (standard, aggressive, conservative)
            validate: Whether to validate after cleaning
            
        Returns:
            Tuple of (cleaning_report, validation_report, quality_before, quality_after)
        """
        logger.info(f"Cleaning file: {input_path.name}")
        
        # Load data
        df = DataConnector.read_file(str(input_path))
        logger.debug(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        
        # Profile before cleaning
        profiler = DataProfiler()
        profile_before = profiler.profile_dataset(df)
        quality_before = profile_before.overall_quality_score
        
        # Determine aggressiveness
        aggressive = mode == CleaningMode.AGGRESSIVE
        
        # Clean data
        cleaner = DataCleaner(aggressive=aggressive)
        df_clean, clean_report = cleaner.clean(df)
        
        logger.info(
            f"Cleaning complete: {clean_report.rows_before} → {clean_report.rows_after} rows, "
            f"{clean_report.cells_modified} cells modified"
        )
        
        # Profile after cleaning
        profile_after = profiler.profile_dataset(df_clean)
        quality_after = profile_after.overall_quality_score
        
        # Validate if requested
        validation_report = None
        if validate:
            validator = DataValidator(strict=False)
            validation_report = validator.validate(df_clean)
            logger.info(f"Validation: {'PASSED' if validation_report.passed else 'FAILED'}")
        
        # Save cleaned data
        DataConnector.write_file(df_clean, str(output_path))
        logger.info(f"Saved cleaned data to: {output_path.name}")
        
        return clean_report, validation_report, quality_before, quality_after
    
    @staticmethod
    def profile_file(input_path: Path, detailed: bool = False) -> dict:
        """
        Profile a data file
        
        Args:
            input_path: Path to file
            detailed: Include detailed column statistics
            
        Returns:
            Profile report as dictionary
        """
        logger.info(f"Profiling file: {input_path.name}")
        
        # Load data
        df = DataConnector.read_file(str(input_path))
        
        # Profile
        profiler = DataProfiler()
        profile = profiler.profile_dataset(df)
        
        # Convert to dict
        result = {
            "total_rows": profile.total_rows,
            "total_columns": profile.total_columns,
            "duplicate_rows": profile.duplicate_rows,
            "memory_usage_mb": profile.memory_usage_mb,
            "quality_score": profile.overall_quality_score,
            "issues_summary": profile.issues_summary
        }
        
        if detailed:
            result["columns"] = [
                {
                    "name": col.name,
                    "type": col.inferred_type,
                    "dtype": col.dtype,
                    "null_percentage": col.null_percentage,
                    "unique_count": col.unique_count,
                    "sample_values": col.sample_values,
                    "issues": col.issues,
                    "numeric_stats": col.numeric_stats,
                    "text_stats": col.text_stats
                }
                for col in profile.column_profiles
            ]
        
        logger.info(f"Profile complete: Quality score {profile.overall_quality_score}/100")
        
        return result
    
    @staticmethod
    def validate_file(
        input_path: Path,
        schema_path: Optional[Path] = None,
        strict: bool = False
    ) -> ValidationReport:
        """
        Validate a data file
        
        Args:
            input_path: Path to file to validate
            schema_path: Optional path to schema YAML file
            strict: Strict validation mode
            
        Returns:
            ValidationReport
        """
        logger.info(f"Validating file: {input_path.name}")
        
        # Load data
        df = DataConnector.read_file(str(input_path))
        
        # Load schema if provided
        schema = None
        if schema_path:
            schema = DataValidator.load_schema(str(schema_path))
            logger.info(f"Loaded schema from: {schema_path.name}")
        
        # Validate
        validator = DataValidator(strict=strict)
        validation_report = validator.validate(df, schema=schema)
        
        logger.info(
            f"Validation complete: {'PASSED' if validation_report.passed else 'FAILED'} "
            f"({len(validation_report.errors)} errors, {len(validation_report.warnings)} warnings)"
        )
        
        return validation_report
    
    @staticmethod
    def infer_schema(input_path: Path, output_path: Path, nullable: bool = True):
        """
        Infer schema from a clean dataset
        
        Args:
            input_path: Path to clean data file
            output_path: Path to save schema YAML
            nullable: Allow null values in schema
        """
        logger.info(f"Inferring schema from: {input_path.name}")
        
        # Load data
        df = DataConnector.read_file(str(input_path))
        
        # Infer schema
        schema = DataValidator.create_schema_from_df(df, nullable=nullable)
        
        # Save schema
        DataValidator.save_schema(schema, str(output_path))
        
        logger.info(f"Schema saved to: {output_path.name}")
        
        return schema


# Singleton instance
cleaner_service = CleanerService()