"""
Data validation and schema checking
"""
import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema, Check
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Individual validation issue"""
    level: ValidationLevel
    column: Optional[str]
    message: str
    count: int = 1
    sample_values: List[Any] = None


@dataclass
class ValidationReport:
    """Complete validation report"""
    passed: bool
    total_issues: int
    errors: List[ValidationIssue]
    warnings: List[ValidationIssue]
    info: List[ValidationIssue]
    schema_compliant: bool
    
    def summary(self) -> str:
        """Generate text summary"""
        if self.passed:
            return "✅ All validation checks passed!"
        
        summary = f"❌ Validation found {self.total_issues} issues:\n"
        summary += f"  - {len(self.errors)} errors\n"
        summary += f"  - {len(self.warnings)} warnings\n"
        summary += f"  - {len(self.info)} info messages\n"
        return summary


class DataValidator:
    """Validate data quality and schema compliance"""
    
    def __init__(self, strict: bool = False):
        """
        Args:
            strict: If True, warnings are treated as errors
        """
        self.strict = strict
        self.issues: List[ValidationIssue] = []
    
    def validate(self, df: pd.DataFrame, schema: Optional[DataFrameSchema] = None) -> ValidationReport:
        """
        Validate DataFrame against quality rules and optional schema
        
        Args:
            df: DataFrame to validate
            schema: Optional Pandera schema to validate against
            
        Returns:
            ValidationReport with all issues found
        """
        logger.info("Starting data validation")
        
        self.issues = []
        
        # Run validation checks
        self._validate_structure(df)
        self._validate_data_types(df)
        self._validate_data_quality(df)
        self._validate_business_rules(df)
        
        # Validate against schema if provided
        schema_compliant = True
        if schema:
            schema_compliant = self._validate_schema(df, schema)
        
        # Categorize issues
        errors = [i for i in self.issues if i.level == ValidationLevel.ERROR]
        warnings = [i for i in self.issues if i.level == ValidationLevel.WARNING]
        info = [i for i in self.issues if i.level == ValidationLevel.INFO]
        
        # In strict mode, warnings become errors
        if self.strict:
            errors.extend(warnings)
            warnings = []
        
        passed = len(errors) == 0
        
        report = ValidationReport(
            passed=passed,
            total_issues=len(self.issues),
            errors=errors,
            warnings=warnings,
            info=info,
            schema_compliant=schema_compliant
        )
        
        logger.info(f"Validation complete: {report.summary()}")
        
        return report
    
    def _validate_structure(self, df: pd.DataFrame) -> None:
        """Validate basic DataFrame structure"""
        
        # Check for empty DataFrame
        if len(df) == 0:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                column=None,
                message="DataFrame is empty (0 rows)"
            ))
            return
        
        if len(df.columns) == 0:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                column=None,
                message="DataFrame has no columns"
            ))
            return
        
        # Check for duplicate column names
        duplicate_cols = df.columns[df.columns.duplicated()].tolist()
        if duplicate_cols:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                column=None,
                message=f"Duplicate column names found: {duplicate_cols}"
            ))
        
        # Check for unnamed columns
        unnamed_cols = [col for col in df.columns if str(col).startswith('Unnamed:')]
        if unnamed_cols:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                column=None,
                message=f"Unnamed columns detected: {unnamed_cols}"
            ))
    
    def _validate_data_types(self, df: pd.DataFrame) -> None:
        """Validate data types consistency"""
        
        for col in df.columns:
            # Check for mixed types in object columns
            if df[col].dtype == 'object':
                non_null = df[col].dropna()
                if len(non_null) == 0:
                    continue
                
                # Get types of values
                types = non_null.apply(type).unique()
                if len(types) > 1:
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        column=col,
                        message=f"Mixed types detected: {[t.__name__ for t in types]}"
                    ))
    
    def _validate_data_quality(self, df: pd.DataFrame) -> None:
        """Validate data quality metrics"""
        
        for col in df.columns:
            # Check null percentage
            null_pct = (df[col].isna().sum() / len(df)) * 100
            
            if null_pct == 100:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    column=col,
                    message="Column is entirely null"
                ))
            elif null_pct > 50:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    column=col,
                    message=f"High null percentage: {null_pct:.1f}%"
                ))
            elif null_pct > 10:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.INFO,
                    column=col,
                    message=f"Moderate null percentage: {null_pct:.1f}%"
                ))
            
            # Check for constant values
            if df[col].nunique() == 1:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    column=col,
                    message="Column has only one unique value (constant)",
                    sample_values=[df[col].iloc[0]]
                ))
            
            # Check for very high cardinality (might indicate data issues)
            if df[col].nunique() == len(df) and len(df) > 100:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.INFO,
                    column=col,
                    message="Very high cardinality (all values unique)"
                ))
    
    def _validate_business_rules(self, df: pd.DataFrame) -> None:
        """Validate common business rules"""
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Numeric validations
            if pd.api.types.is_numeric_dtype(df[col]):
                
                # Check for negative values in columns that shouldn't have them
                if any(keyword in col_lower for keyword in ['price', 'cost', 'amount', 'quantity', 'count', 'age']):
                    negative_count = (df[col] < 0).sum()
                    if negative_count > 0:
                        self.issues.append(ValidationIssue(
                            level=ValidationLevel.WARNING,
                            column=col,
                            message=f"Contains {negative_count} negative values (unusual for {col})",
                            count=negative_count
                        ))
                
                # Check for zero values in quantity/count columns
                if any(keyword in col_lower for keyword in ['quantity', 'count']):
                    zero_count = (df[col] == 0).sum()
                    if zero_count > len(df) * 0.1:  # More than 10% zeros
                        self.issues.append(ValidationIssue(
                            level=ValidationLevel.INFO,
                            column=col,
                            message=f"{zero_count} zero values ({(zero_count/len(df)*100):.1f}%)",
                            count=zero_count
                        ))
            
            # Email validation
            if 'email' in col_lower:
                non_null = df[col].dropna().astype(str)
                if len(non_null) > 0:
                    # Simple email pattern check
                    valid_emails = non_null.str.contains(r'@.*\.', regex=True, na=False)
                    invalid_count = (~valid_emails).sum()
                    
                    if invalid_count > 0:
                        self.issues.append(ValidationIssue(
                            level=ValidationLevel.WARNING,
                            column=col,
                            message=f"{invalid_count} invalid email formats",
                            count=invalid_count,
                            sample_values=non_null[~valid_emails].head(3).tolist()
                        ))
            
            # Date validation
            if any(keyword in col_lower for keyword in ['date', 'time', 'timestamp']):
                if not pd.api.types.is_datetime64_any_dtype(df[col]):
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.INFO,
                        column=col,
                        message="Column name suggests date/time but not datetime type"
                    ))
    
    def _validate_schema(self, df: pd.DataFrame, schema: DataFrameSchema) -> bool:
        """
        Validate DataFrame against a Pandera schema
        
        Returns:
            True if schema validation passes
        """
        try:
            schema.validate(df, lazy=True)
            logger.info("Schema validation passed")
            return True
            
        except pa.errors.SchemaErrors as e:
            logger.warning(f"Schema validation failed: {len(e.failure_cases)} issues")
            
            # Convert schema errors to validation issues
            for _, error in e.failure_cases.iterrows():
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    column=error.get('column'),
                    message=f"Schema violation: {error.get('check')}"
                ))
            
            return False
    
    @staticmethod
    def create_schema_from_df(df: pd.DataFrame, nullable: bool = True) -> DataFrameSchema:
        """
        Auto-generate a Pandera schema from a DataFrame
        
        Args:
            df: DataFrame to generate schema from
            nullable: Whether to allow null values
            
        Returns:
            Pandera DataFrameSchema
        """
        columns = {}
        
        for col in df.columns:
            checks = []
            
            # Add type-specific checks
            if pd.api.types.is_numeric_dtype(df[col]):
                # Add range checks based on observed values
                min_val = df[col].min()
                max_val = df[col].max()
                
                if not pd.isna(min_val):
                    checks.append(Check.greater_than_or_equal_to(min_val))
                if not pd.isna(max_val):
                    checks.append(Check.less_than_or_equal_to(max_val))
            
            elif pd.api.types.is_string_dtype(df[col]) or df[col].dtype == 'object':
                # Add string length check
                max_length = df[col].astype(str).str.len().max()
                if not pd.isna(max_length):
                    checks.append(Check(lambda s: s.astype(str).str.len() <= max_length))
            
            columns[col] = Column(
                dtype=df[col].dtype,
                checks=checks,
                nullable=nullable,
                required=True
            )
        
        return DataFrameSchema(columns=columns, strict=True)
    
    @staticmethod
    def save_schema(schema: DataFrameSchema, filepath: str) -> None:
        """Save schema to YAML file"""
        schema.to_yaml(filepath)
        logger.info(f"Schema saved to {filepath}")
    
    @staticmethod
    def load_schema(filepath: str) -> DataFrameSchema:
        """Load schema from YAML file"""
        schema = DataFrameSchema.from_yaml(filepath)
        logger.info(f"Schema loaded from {filepath}")
        return schema