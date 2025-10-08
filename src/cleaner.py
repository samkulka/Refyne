"""
Data cleaning and transformation logic
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class CleaningReport:
    """Report of cleaning operations performed"""
    operations_performed: List[str]
    rows_before: int
    rows_after: int
    columns_modified: List[str]
    rows_removed: int
    cells_modified: int


class DataCleaner:
    """Smart data cleaning and transformation"""
    
    def __init__(self, aggressive: bool = False):
        """
        Args:
            aggressive: If True, apply more aggressive cleaning (e.g., drop high-null columns)
        """
        self.aggressive = aggressive
        self.operations = []
        self.cells_modified = 0
        self.columns_modified = set()
    
    def clean(self, df: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
        """
        Apply all cleaning operations to the DataFrame
        
        Returns:
            Tuple of (cleaned_df, cleaning_report)
        """
        logger.info("Starting data cleaning process")
        
        df_clean = df.copy()
        rows_before = len(df_clean)
        
        # Reset tracking
        self.operations = []
        self.cells_modified = 0
        self.columns_modified = set()
        
        # 1. Remove duplicate rows
        df_clean = self._remove_duplicates(df_clean)
        
        # 2. Standardize column names
        df_clean = self._standardize_column_names(df_clean)
        
        # 3. Handle missing values
        df_clean = self._handle_missing_values(df_clean)
        
        # 4. Fix data types
        df_clean = self._fix_data_types(df_clean)
        
        # 5. Standardize text fields
        df_clean = self._standardize_text(df_clean)
        
        # 6. Handle outliers (if aggressive)
        if self.aggressive:
            df_clean = self._handle_outliers(df_clean)
        
        # 7. Validate and fix specific patterns
        df_clean = self._validate_patterns(df_clean)
        
        rows_after = len(df_clean)
        
        report = CleaningReport(
            operations_performed=self.operations,
            rows_before=rows_before,
            rows_after=rows_after,
            columns_modified=list(self.columns_modified),
            rows_removed=rows_before - rows_after,
            cells_modified=self.cells_modified
        )
        
        logger.info(f"Cleaning complete: {len(self.operations)} operations performed")
        
        return df_clean, report
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate rows"""
        duplicates = df.duplicated().sum()
        
        if duplicates > 0:
            df = df.drop_duplicates()
            self.operations.append(f"Removed {duplicates} duplicate rows")
            logger.info(f"Removed {duplicates} duplicate rows")
        
        return df
    
    def _standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to snake_case"""
        new_columns = {}
        
        for col in df.columns:
            # Convert to lowercase, replace spaces/special chars with underscore
            new_name = re.sub(r'[^\w\s]', '', str(col))  # Remove special chars
            new_name = re.sub(r'\s+', '_', new_name)  # Replace spaces
            new_name = new_name.lower().strip('_')
            
            if new_name != col:
                new_columns[col] = new_name
        
        if new_columns:
            df = df.rename(columns=new_columns)
            self.operations.append(f"Standardized {len(new_columns)} column names to snake_case")
            logger.info(f"Standardized column names: {new_columns}")
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values intelligently based on column type"""
        
        for col in df.columns:
            null_count = df[col].isna().sum()
            
            if null_count == 0:
                continue
            
            null_pct = (null_count / len(df)) * 100
            
            # If too many nulls, drop column (only in aggressive mode)
            if self.aggressive and null_pct > 80:
                df = df.drop(columns=[col])
                self.operations.append(f"Dropped column '{col}' (>{null_pct:.1f}% null)")
                continue
            
            # Strategy depends on data type
            if pd.api.types.is_numeric_dtype(df[col]):
                # Use median for numeric
                fill_value = df[col].median()
                df[col] = df[col].fillna(fill_value)
                self.operations.append(f"Filled {null_count} nulls in '{col}' with median ({fill_value})")
                self.cells_modified += null_count
                self.columns_modified.add(col)
                
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                # Forward fill for dates
                df[col] = df[col].fillna(method='ffill')
                self.operations.append(f"Forward-filled {null_count} nulls in '{col}'")
                self.cells_modified += null_count
                self.columns_modified.add(col)
                
            else:
                # For categorical/text, use mode or 'Unknown'
                mode_value = df[col].mode()
                if len(mode_value) > 0:
                    fill_value = mode_value[0]
                else:
                    fill_value = 'Unknown'
                
                df[col] = df[col].fillna(fill_value)
                self.operations.append(f"Filled {null_count} nulls in '{col}' with '{fill_value}'")
                self.cells_modified += null_count
                self.columns_modified.add(col)
        
        return df
    
    def _fix_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Attempt to fix/convert data types"""
        
        for col in df.columns:
            # Skip if already numeric or datetime
            if pd.api.types.is_numeric_dtype(df[col]) or pd.api.types.is_datetime64_any_dtype(df[col]):
                continue
            
            # Try to convert to numeric
            if self._looks_numeric(df[col]):
                try:
                    # Clean numeric strings first
                    cleaned = df[col].astype(str).str.replace(r'[^\d.-]', '', regex=True)
                    df[col] = pd.to_numeric(cleaned, errors='coerce')
                    self.operations.append(f"Converted '{col}' to numeric type")
                    self.columns_modified.add(col)
                except:
                    pass
            
            # Try to convert to datetime
            elif self._looks_datetime(df[col]):
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
                    self.operations.append(f"Converted '{col}' to datetime type")
                    self.columns_modified.add(col)
                except:
                    pass
        
        return df
    
    def _standardize_text(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize text fields (casing, whitespace, etc.)"""
        
        for col in df.columns:
            if df[col].dtype == 'object':
                original = df[col].copy()
                
                # Strip leading/trailing whitespace
                df[col] = df[col].astype(str).str.strip()
                
                # Check if this looks like a categorical column (low cardinality)
                unique_ratio = df[col].nunique() / len(df)
                
                if unique_ratio < 0.1:  # Likely categorical
                    # Standardize casing (lowercase for consistency)
                    df[col] = df[col].str.lower()
                    
                    if not df[col].equals(original):
                        self.operations.append(f"Standardized text in '{col}' (lowercase, trimmed)")
                        modified_count = (df[col] != original).sum()
                        self.cells_modified += modified_count
                        self.columns_modified.add(col)
        
        return df
    
    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle outliers in numeric columns (aggressive mode only)"""
        
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                # Use IQR method
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                outliers_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
                outlier_count = outliers_mask.sum()
                
                if outlier_count > 0:
                    # Cap outliers at bounds
                    df.loc[df[col] < lower_bound, col] = lower_bound
                    df.loc[df[col] > upper_bound, col] = upper_bound
                    
                    self.operations.append(f"Capped {outlier_count} outliers in '{col}'")
                    self.cells_modified += outlier_count
                    self.columns_modified.add(col)
        
        return df
    
    def _validate_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and fix specific patterns (emails, dates, etc.)"""
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Email validation and cleaning
            if 'email' in col_lower:
                original = df[col].copy()
                # Lowercase emails
                df[col] = df[col].astype(str).str.lower().str.strip()
                
                # Remove invalid emails
                invalid_mask = ~df[col].str.contains(r'@.*\.', regex=True, na=False)
                invalid_count = invalid_mask.sum()
                
                if invalid_count > 0:
                    df.loc[invalid_mask, col] = pd.NA
                    self.operations.append(f"Removed {invalid_count} invalid emails from '{col}'")
                    self.cells_modified += invalid_count
                    self.columns_modified.add(col)
            
            # Fix common status/category inconsistencies
            if any(keyword in col_lower for keyword in ['status', 'category', 'type', 'region']):
                if df[col].dtype == 'object':
                    original = df[col].copy()
                    # Lowercase and strip
                    df[col] = df[col].astype(str).str.lower().str.strip()
                    
                    modified_count = (df[col] != original).sum()
                    if modified_count > 0:
                        self.cells_modified += modified_count
                        self.columns_modified.add(col)
        
        return df
    
    @staticmethod
    def _looks_numeric(series: pd.Series) -> bool:
        """Check if a series looks like it should be numeric"""
        if pd.api.types.is_numeric_dtype(series):
            return False  # Already numeric
        
        # Sample some non-null values
        sample = series.dropna().astype(str).head(50)
        
        if len(sample) == 0:
            return False
        
        # Check if most values look numeric
        numeric_pattern = sample.str.match(r'^-?\d+\.?\d*')
        return numeric_pattern.sum() / len(sample) > 0.8
    
    @staticmethod
    def _looks_datetime(series: pd.Series) -> bool:
        """Check if a series looks like it should be datetime"""
        if pd.api.types.is_datetime64_any_dtype(series):
            return False  # Already datetime
        
        # Sample some non-null values
        sample = series.dropna().head(20)
        
        if len(sample) == 0:
            return False
        
        # Try to parse as datetime
        try:
            pd.to_datetime(sample, errors='raise')
            return True
        except:
            return False