from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class CleaningRules(BaseModel):
    """Custom cleaning rules configuration"""

    # Column operations
    drop_columns: Optional[List[str]] = Field(default=None, description="Columns to drop")
    rename_columns: Optional[Dict[str, str]] = Field(default=None, description="Column rename mapping")

    # Missing value handling
    fill_nulls: Optional[Dict[str, Any]] = Field(default=None, description="Custom null fill values per column")
    drop_null_threshold: Optional[float] = Field(default=None, description="Drop columns with null % above this")

    # Duplicate handling
    keep_duplicates: Optional[str] = Field(default="first", description="Which duplicate to keep: first, last, or false")
    subset_for_duplicates: Optional[List[str]] = Field(default=None, description="Columns to consider for duplicates")

    # Data type conversions
    force_types: Optional[Dict[str, str]] = Field(default=None, description="Force column types (int64, float64, str, datetime)")

    # Text transformations
    lowercase_columns: Optional[List[str]] = Field(default=None, description="Columns to lowercase")
    uppercase_columns: Optional[List[str]] = Field(default=None, description="Columns to uppercase")
    trim_whitespace: bool = Field(default=True, description="Trim whitespace from text")

    # Value replacements
    replace_values: Optional[Dict[str, Dict[str, Any]]] = Field(
        default=None,
        description="Replace values: {column: {old_value: new_value}}"
    )

    # Outlier handling
    cap_outliers: Optional[List[str]] = Field(default=None, description="Columns to cap outliers using IQR")

    # Custom filters
    filter_rows: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Filter rows: {column: {operator: value}}"
    )


class CleanWithRulesRequest(BaseModel):
    """Request to clean with custom rules"""
    file_id: str
    rules: CleaningRules
    aggressive: bool = False
