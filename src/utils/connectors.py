"""
Data connectors for reading various file formats
"""
import pandas as pd
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DataConnector:
    """Universal data connector for various file formats"""
    
    SUPPORTED_FORMATS = {'.csv', '.xlsx', '.xls', '.json', '.parquet'}
    
    @staticmethod
    def read_file(file_path: str, **kwargs) -> pd.DataFrame:
        """
        Read data from various file formats into a pandas DataFrame
        
        Args:
            file_path: Path to the data file
            **kwargs: Additional arguments to pass to the reader
            
        Returns:
            pd.DataFrame: Loaded data
            
        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        suffix = path.suffix.lower()
        
        if suffix not in DataConnector.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported file format: {suffix}. "
                f"Supported formats: {DataConnector.SUPPORTED_FORMATS}"
            )
        
        logger.info(f"Reading file: {file_path}")
        
        try:
            if suffix == '.csv':
                df = pd.read_csv(
                    file_path,
                    encoding='utf-8',
                    low_memory=False,
                    **kwargs
                )
            elif suffix in {'.xlsx', '.xls'}:
                df = pd.read_excel(file_path, **kwargs)
            elif suffix == '.json':
                df = pd.read_json(file_path, **kwargs)
            elif suffix == '.parquet':
                df = pd.read_parquet(file_path, **kwargs)
            
            logger.info(f"Successfully loaded {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}")
            raise
    
    @staticmethod
    def write_file(df: pd.DataFrame, file_path: str, **kwargs) -> None:
        """
        Write DataFrame to file in specified format
        
        Args:
            df: DataFrame to write
            file_path: Output file path
            **kwargs: Additional arguments to pass to the writer
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        # Create parent directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Writing to file: {file_path}")
        
        if suffix == '.csv':
            df.to_csv(file_path, index=False, **kwargs)
        elif suffix in {'.xlsx', '.xls'}:
            df.to_excel(file_path, index=False, **kwargs)
        elif suffix == '.json':
            df.to_json(file_path, orient='records', indent=2, **kwargs)
        elif suffix == '.parquet':
            df.to_parquet(file_path, index=False, **kwargs)
        else:
            raise ValueError(f"Unsupported output format: {suffix}")
        
        logger.info(f"Successfully wrote {len(df)} rows to {file_path}")
