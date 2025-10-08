"""
Data profiling utilities for analyzing DataFrames
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class DataProfiler:
    """Profile DataFrames to generate statistical summaries and data quality metrics"""

    def __init__(self, df: pd.DataFrame):
        """
        Initialize DataProfiler with a DataFrame

        Args:
            df: DataFrame to profile
        """
        self.df = df
        self.profile_results: Dict[str, Any] = {}

    def profile(self) -> Dict[str, Any]:
        """
        Generate comprehensive profile of the DataFrame

        Returns:
            Dictionary containing profile information
        """
        logger.info(f"Profiling DataFrame with {len(self.df)} rows and {len(self.df.columns)} columns")

        self.profile_results = {
            'overview': self._get_overview(),
            'columns': self._profile_columns(),
            'missing_data': self._analyze_missing_data(),
            'duplicates': self._analyze_duplicates(),
        }

        return self.profile_results

    def _get_overview(self) -> Dict[str, Any]:
        """Get basic overview statistics"""
        return {
            'num_rows': len(self.df),
            'num_columns': len(self.df.columns),
            'memory_usage_mb': self.df.memory_usage(deep=True).sum() / 1024**2,
            'column_names': list(self.df.columns),
        }

    def _profile_columns(self) -> Dict[str, Dict[str, Any]]:
        """Profile each column individually"""
        column_profiles = {}

        for col in self.df.columns:
            column_profiles[col] = self._profile_single_column(col)

        return column_profiles

    def _profile_single_column(self, col: str) -> Dict[str, Any]:
        """Profile a single column"""
        series = self.df[col]

        profile = {
            'dtype': str(series.dtype),
            'non_null_count': series.notna().sum(),
            'null_count': series.isna().sum(),
            'null_percentage': (series.isna().sum() / len(series)) * 100,
            'unique_count': series.nunique(),
            'unique_percentage': (series.nunique() / series.notna().sum() * 100) if series.notna().sum() > 0 else 0,
        }

        # Numeric column statistics
        if pd.api.types.is_numeric_dtype(series):
            profile.update({
                'mean': series.mean(),
                'std': series.std(),
                'min': series.min(),
                'max': series.max(),
                'median': series.median(),
                'q25': series.quantile(0.25),
                'q75': series.quantile(0.75),
            })

        # String/object column statistics
        elif pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series):
            non_null = series.dropna()
            if len(non_null) > 0:
                profile.update({
                    'top_values': series.value_counts().head(5).to_dict(),
                    'avg_length': non_null.astype(str).str.len().mean() if len(non_null) > 0 else 0,
                })

        # DateTime column statistics
        elif pd.api.types.is_datetime64_any_dtype(series):
            profile.update({
                'min_date': series.min(),
                'max_date': series.max(),
            })

        return profile

    def _analyze_missing_data(self) -> Dict[str, Any]:
        """Analyze missing data patterns"""
        total_cells = self.df.shape[0] * self.df.shape[1]
        missing_cells = self.df.isna().sum().sum()

        return {
            'total_missing_cells': int(missing_cells),
            'missing_percentage': (missing_cells / total_cells * 100) if total_cells > 0 else 0,
            'columns_with_missing': self.df.columns[self.df.isna().any()].tolist(),
        }

    def _analyze_duplicates(self) -> Dict[str, Any]:
        """Analyze duplicate rows"""
        duplicate_rows = self.df.duplicated().sum()

        return {
            'duplicate_row_count': int(duplicate_rows),
            'duplicate_percentage': (duplicate_rows / len(self.df) * 100) if len(self.df) > 0 else 0,
        }

    def get_summary_report(self) -> str:
        """
        Generate a human-readable summary report

        Returns:
            Formatted string report
        """
        if not self.profile_results:
            self.profile()

        report = []
        report.append("=" * 60)
        report.append("DATA PROFILE REPORT")
        report.append("=" * 60)

        # Overview
        overview = self.profile_results['overview']
        report.append(f"\nRows: {overview['num_rows']:,}")
        report.append(f"Columns: {overview['num_columns']}")
        report.append(f"Memory Usage: {overview['memory_usage_mb']:.2f} MB")

        # Missing data
        missing = self.profile_results['missing_data']
        report.append(f"\nMissing Data: {missing['total_missing_cells']:,} cells ({missing['missing_percentage']:.2f}%)")

        # Duplicates
        duplicates = self.profile_results['duplicates']
        report.append(f"Duplicate Rows: {duplicates['duplicate_row_count']:,} ({duplicates['duplicate_percentage']:.2f}%)")

        report.append("\n" + "=" * 60)

        return "\n".join(report)
