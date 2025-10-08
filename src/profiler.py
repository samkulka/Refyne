"""
Data profiling and quality assessment
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ColumnProfile:
    """Profile information for a single column"""
    name: str
    dtype: str
    inferred_type: str
    total_count: int
    null_count: int
    null_percentage: float
    unique_count: int
    unique_percentage: float
    duplicate_count: int
    sample_values: List[Any]
    issues: List[str]
    numeric_stats: Dict[str, Any] = None
    text_stats: Dict[str, Any] = None
    date_stats: Dict[str, Any] = None


@dataclass
class DatasetProfile:
    """Complete dataset profile"""
    total_rows: int
    total_columns: int
    duplicate_rows: int
    memory_usage_mb: float
    column_profiles: List[ColumnProfile]
    overall_quality_score: float
    issues_summary: Dict[str, int]


class DataProfiler:
    """Profile and analyze data quality"""
    
    @staticmethod
    def infer_column_type(series: pd.Series) -> str:
        """Infer the semantic type of a column"""
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return 'empty'
        
        if pd.api.types.is_numeric_dtype(series):
            return 'numeric'
        
        if pd.api.types.is_datetime64_any_dtype(series):
            return 'datetime'
        
        if pd.api.types.is_object_dtype(series):
            sample = non_null.astype(str).head(100)
            
            if sample.str.contains(r'@', regex=False).sum() / len(sample) > 0.8:
                return 'email'
            
            try:
                pd.to_datetime(sample.head(10), errors='raise')
                return 'datetime'
            except:
                pass
            
            unique_ratio = series.nunique() / len(series)
            if unique_ratio < 0.05 or series.nunique() < 20:
                return 'categorical'
            
            return 'text'
        
        return 'mixed'
    
    @staticmethod
    def profile_column(series: pd.Series) -> ColumnProfile:
        """Profile a single column"""
        issues = []
        total = len(series)
        null_count = series.isna().sum()
        null_pct = (null_count / total * 100) if total > 0 else 0
        unique_count = series.nunique()
        unique_pct = (unique_count / total * 100) if total > 0 else 0
        duplicate_count = total - unique_count
        inferred_type = DataProfiler.infer_column_type(series)
        sample_values = series.dropna().head(5).tolist()
        
        if null_pct > 50:
            issues.append(f"High null rate: {null_pct:.1f}%")
        
        return ColumnProfile(
            name=series.name,
            dtype=str(series.dtype),
            inferred_type=inferred_type,
            total_count=total,
            null_count=null_count,
            null_percentage=null_pct,
            unique_count=unique_count,
            unique_percentage=unique_pct,
            duplicate_count=duplicate_count,
            sample_values=sample_values,
            issues=issues
        )
    
    @staticmethod
    def profile_dataset(df: pd.DataFrame) -> DatasetProfile:
        """Profile entire dataset"""
        logger.info(f"Profiling dataset: {len(df)} rows, {len(df.columns)} columns")
        
        duplicate_rows = df.duplicated().sum()
        memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        
        column_profiles = []
        for col in df.columns:
            profile = DataProfiler.profile_column(df[col])
            column_profiles.append(profile)
        
        quality_score = 85.0  # Simplified for now
        
        issues_summary = {
            'high_null_columns': sum(1 for p in column_profiles if p.null_percentage > 50),
            'duplicate_rows': int(duplicate_rows),
        }
        
        return DatasetProfile(
            total_rows=len(df),
            total_columns=len(df.columns),
            duplicate_rows=int(duplicate_rows),
            memory_usage_mb=float(memory_mb),
            column_profiles=column_profiles,
            overall_quality_score=quality_score,
            issues_summary=issues_summary
        )