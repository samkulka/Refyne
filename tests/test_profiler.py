"""
Tests for data profiler
"""
import pytest
import pandas as pd
import numpy as np
from src.profiler import DataProfiler, ColumnProfile


class TestDataProfiler:
    """Test suite for DataProfiler"""
    
    def test_infer_numeric_type(self):
        """Test numeric type inference"""
        series = pd.Series([1, 2, 3, 4, 5], name='test_col')
        inferred_type = DataProfiler.infer_column_type(series)
        assert inferred_type == 'numeric'
    
    def test_infer_categorical_type(self):
        """Test categorical type inference"""
        series = pd.Series(['A', 'B', 'A', 'C', 'B', 'A'], name='test_col')
        inferred_type = DataProfiler.infer_column_type(series)
        assert inferred_type == 'categorical'
    
    def test_infer_email_type(self):
        """Test email type inference"""
        series = pd.Series([
            'user1@example.com',
            'user2@example.com',
            'user3@example.com'
        ], name='email')