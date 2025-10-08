"""
AI-powered semantic analysis and enrichment (optional feature)
Requires OpenAI API key set in environment variable OPENAI_API_KEY
"""
import os
import logging
from typing import Dict, List, Optional
import pandas as pd

logger = logging.getLogger(__name__)

# Optional OpenAI import
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not installed. Semantic features will be unavailable.")


class SemanticAnalyzer:
    """Use LLMs to understand and enrich data semantically"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize semantic analyzer
        
        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package not installed. "
                "Install with: pip install openai"
            )
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter"
            )
        
        self.client = OpenAI(api_key=self.api_key)
    
    def suggest_column_names(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Use AI to suggest better column names based on data content
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary mapping old column names to suggested new names
        """
        suggestions = {}
        
        for col in df.columns:
            # Get sample values
            samples = df[col].dropna().head(5).tolist()
            
            if not samples:
                continue
            
            prompt = f"""
            Given a data column with these sample values:
            {samples}
            
            The current column name is: "{col}"
            
            Suggest a clear, descriptive column name following these rules:
            - Use snake_case
            - Be concise but descriptive
            - Indicate the data type/purpose
            
            Respond with ONLY the suggested column name, nothing else.
            """
            
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=20,
                    temperature=0.3
                )
                
                suggested_name = response.choices[0].message.content.strip()
                
                if suggested_name != col:
                    suggestions[col] = suggested_name
                    logger.info(f"Suggested rename: '{col}' -> '{suggested_name}'")
                    
            except Exception as e:
                logger.warning(f"Failed to get suggestion for column '{col}': {e}")
        
        return suggestions
    
    def infer_column_semantics(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Infer semantic meaning and relationships of columns
        
        Returns:
            Dictionary with semantic metadata for each column
        """
        semantics = {}
        
        for col in df.columns:
            samples = df[col].dropna().head(10).tolist()
            
            if not samples:
                continue
            
            prompt = f"""
            Analyze this data column:
            Column name: {col}
            Sample values: {samples}
            
            Provide:
            1. Semantic type (e.g., "email_address", "product_name", "monetary_value", "date", "identifier")
            2. Data sensitivity (low/medium/high)
            3. Suggested validation rules
            
            Format your response as:
            Type: <type>
            Sensitivity: <level>
            Validation: <rules>
            """
            
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100,
                    temperature=0.3
                )
                
                result = response.choices[0].message.content
                
                # Parse response (simple parsing)
                lines = result.strip().split('\n')
                metadata = {}
                
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip().lower()] = value.strip()
                
                semantics[col] = metadata
                logger.info(f"Inferred semantics for '{col}': {metadata}")
                
            except Exception as e:
                logger.warning(f"Failed to infer semantics for '{col}': {e}")
        
        return semantics
    
    def detect_relationships(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect potential relationships between columns
        
        Returns:
            List of detected relationships
        """
        relationships = []
        
        # Get column summary
        column_info = []
        for col in df.columns:
            samples = df[col].dropna().head(3).tolist()
            column_info.append(f"{col}: {samples}")
        
        prompt = f"""
        Given these data columns:
        {chr(10).join(column_info)}
        
        Identify potential relationships or dependencies between columns.
        For example:
        - Foreign key relationships
        - Derived/calculated fields
        - Hierarchical relationships
        
        List only clear, confident relationships.
        Format: "Column1 -> Column2: relationship_type"
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            
            # Parse relationships
            for line in result.strip().split('\n'):
                if '->' in line:
                    relationships.append({"raw": line.strip()})
            
            logger.info(f"Detected {len(relationships)} relationships")
            
        except Exception as e:
            logger.warning(f"Failed to detect relationships: {e}")
        
        return relationships
    
    def suggest_data_quality_rules(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Suggest data quality rules based on column content
        
        Returns:
            Dictionary mapping column names to suggested validation rules
        """
        rules = {}
        
        for col in df.columns:
            samples = df[col].dropna().head(10).tolist()
            dtype = str(df[col].dtype)
            
            prompt = f"""
            For this data column:
            Name: {col}
            Type: {dtype}
            Samples: {samples}
            
            Suggest 2-3 specific data quality validation rules.
            Be concrete and actionable.
            
            Example rules:
            - "Must be between 0 and 100"
            - "Must contain @ symbol"
            - "Must match format: XXX-XXX-XXXX"
            
            List only the rules, one per line.
            """
            
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                    temperature=0.3
                )
                
                suggested_rules = [
                    line.strip('- ').strip()
                    for line in response.choices[0].message.content.strip().split('\n')
                    if line.strip()
                ]
                
                rules[col] = suggested_rules
                logger.info(f"Suggested rules for '{col}': {suggested_rules}")
                
            except Exception as e:
                logger.warning(f"Failed to suggest rules for '{col}': {e}")
        
        return rules


# Convenience function
def analyze_semantics(df: pd.DataFrame, api_key: Optional[str] = None) -> Dict:
    """
    Run full semantic analysis on a DataFrame
    
    Returns:
        Dictionary with all semantic insights
    """
    if not OPENAI_AVAILABLE:
        logger.error("OpenAI package not available for semantic analysis")
        return {}
    
    analyzer = SemanticAnalyzer(api_key=api_key)
    
    return {
        "column_suggestions": analyzer.suggest_column_names(df),
        "column_semantics": analyzer.infer_column_semantics(df),
        "relationships": analyzer.detect_relationships(df),
        "quality_rules": analyzer.suggest_data_quality_rules(df)
    }