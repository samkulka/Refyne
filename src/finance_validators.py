"""
Financial data validators for Refyne
Specialized validation for finance industry data
"""
import re
import pandas as pd
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class FinanceValidationResult:
    """Result of financial validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    fixed_values: Dict[str, Any] = None


class FinanceValidator:
    """Validator for financial data"""
    
    # Currency patterns
    CURRENCY_PATTERNS = {
        'USD': r'^\$?\s*[\d,]+\.?\d{0,2}$',
        'EUR': r'^€?\s*[\d,]+\.?\d{0,2}$',
        'GBP': r'^£?\s*[\d,]+\.?\d{0,2}$',
    }
    
    # ISIN pattern (12 characters: 2 letter country code + 9 alphanumeric + 1 check digit)
    ISIN_PATTERN = r'^[A-Z]{2}[A-Z0-9]{9}[0-9]$'
    
    # CUSIP pattern (9 characters)
    CUSIP_PATTERN = r'^[0-9]{3}[A-Z0-9]{5}[0-9]$'
    
    # Account number patterns
    ACCOUNT_PATTERNS = {
        'US_BANK': r'^\d{8,17}$',  # US bank account
        'IBAN': r'^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$',  # International
    }
    
    @staticmethod
    def validate_currency(value: str, currency: str = 'USD') -> Tuple[bool, float]:
        """
        Validate and parse currency value
        
        Args:
            value: String currency value
            currency: Currency code (USD, EUR, GBP)
            
        Returns:
            (is_valid, parsed_amount)
        """
        if pd.isna(value):
            return False, None
            
        # Remove currency symbols and whitespace
        clean = str(value).replace('$', '').replace('€', '').replace('£', '')
        clean = clean.replace(',', '').strip()
        
        try:
            amount = float(clean)
            # Validate reasonable range
            if amount < 0:
                return False, None
            if amount > 1e12:  # Too large
                return False, None
            return True, round(amount, 2)
        except (ValueError, TypeError):
            return False, None
    
    @staticmethod
    def validate_isin(value: str) -> Tuple[bool, str]:
        """
        Validate ISIN (International Securities Identification Number)
        
        Args:
            value: ISIN string
            
        Returns:
            (is_valid, cleaned_isin)
        """
        if pd.isna(value):
            return False, None
            
        # Clean and uppercase
        clean = str(value).strip().upper().replace(' ', '').replace('-', '')
        
        # Check pattern
        if not re.match(FinanceValidator.ISIN_PATTERN, clean):
            return False, None
            
        # TODO: Implement full ISIN checksum validation
        return True, clean
    
    @staticmethod
    def validate_cusip(value: str) -> Tuple[bool, str]:
        """
        Validate CUSIP (Committee on Uniform Securities Identification Procedures)
        
        Args:
            value: CUSIP string
            
        Returns:
            (is_valid, cleaned_cusip)
        """
        if pd.isna(value):
            return False, None
            
        # Clean and uppercase
        clean = str(value).strip().upper().replace(' ', '').replace('-', '')
        
        # Check pattern
        if not re.match(FinanceValidator.CUSIP_PATTERN, clean):
            return False, None
            
        return True, clean
    
    @staticmethod
    def validate_account_number(value: str, account_type: str = 'US_BANK') -> Tuple[bool, str]:
        """
        Validate account number
        
        Args:
            value: Account number
            account_type: Type of account (US_BANK, IBAN)
            
        Returns:
            (is_valid, cleaned_account)
        """
        if pd.isna(value):
            return False, None
            
        # Clean
        clean = str(value).strip().upper().replace(' ', '').replace('-', '')
        
        # Get pattern
        pattern = FinanceValidator.ACCOUNT_PATTERNS.get(account_type)
        if not pattern:
            return False, None
            
        # Check pattern
        if not re.match(pattern, clean):
            return False, None
            
        return True, clean
    
    @staticmethod
    def validate_transaction_id(value: str) -> Tuple[bool, str]:
        """
        Validate transaction ID
        
        Args:
            value: Transaction ID
            
        Returns:
            (is_valid, cleaned_id)
        """
        if pd.isna(value):
            return False, None
            
        # Transaction IDs are typically alphanumeric, 6-50 chars
        clean = str(value).strip()
        
        if len(clean) < 6 or len(clean) > 50:
            return False, None
            
        # Must be alphanumeric (with possible dashes/underscores)
        if not re.match(r'^[A-Za-z0-9_-]+$', clean):
            return False, None
            
        return True, clean.upper()
    
    @staticmethod
    def detect_pii(df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Detect columns that likely contain PII
        
        Args:
            df: DataFrame to check
            
        Returns:
            Dictionary of PII types and column names
        """
        pii_columns = {
            'ssn': [],
            'credit_card': [],
            'email': [],
            'phone': [],
            'address': [],
            'name': []
        }
        
        for col in df.columns:
            col_lower = col.lower()
            sample = df[col].dropna().astype(str).head(100)
            
            # SSN pattern
            if any(keyword in col_lower for keyword in ['ssn', 'social_security', 'tax_id']):
                pii_columns['ssn'].append(col)
            
            # Credit card
            elif any(keyword in col_lower for keyword in ['card', 'credit', 'cc_']):
                # Check if values look like card numbers
                card_pattern = sample.str.match(r'^\d{13,19}$')
                if card_pattern.sum() > len(sample) * 0.5:
                    pii_columns['credit_card'].append(col)
            
            # Email (already detected by profiler)
            elif 'email' in col_lower:
                pii_columns['email'].append(col)
            
            # Phone
            elif any(keyword in col_lower for keyword in ['phone', 'mobile', 'tel']):
                pii_columns['phone'].append(col)
            
            # Address
            elif any(keyword in col_lower for keyword in ['address', 'street', 'zip', 'postal']):
                pii_columns['address'].append(col)
            
            # Name
            elif any(keyword in col_lower for keyword in ['name', 'first_name', 'last_name', 'full_name']):
                pii_columns['name'].append(col)
        
        # Filter out empty lists
        return {k: v for k, v in pii_columns.items() if v}
    
    @staticmethod
    def mask_pii(value: str, pii_type: str = 'generic') -> str:
        """
        Mask PII data
        
        Args:
            value: Value to mask
            pii_type: Type of PII
            
        Returns:
            Masked value
        """
        if pd.isna(value):
            return value
            
        value_str = str(value)
        
        if pii_type == 'ssn':
            # Show last 4 digits only
            if len(value_str) >= 4:
                return 'XXX-XX-' + value_str[-4:]
            return 'XXX-XX-XXXX'
        
        elif pii_type == 'credit_card':
            # Show last 4 digits only
            if len(value_str) >= 4:
                return '**** **** **** ' + value_str[-4:]
            return '**** **** **** ****'
        
        elif pii_type == 'email':
            # Mask email but keep domain
            if '@' in value_str:
                parts = value_str.split('@')
                if len(parts[0]) > 2:
                    return parts[0][:2] + '***@' + parts[1]
            return '***@***.com'
        
        elif pii_type == 'phone':
            # Show last 4 digits
            if len(value_str) >= 4:
                return '***-***-' + value_str[-4:]
            return '***-***-****'
        
        else:
            # Generic masking - show first and last char
            if len(value_str) > 2:
                return value_str[0] + '*' * (len(value_str) - 2) + value_str[-1]
            return '***'


class FinancialDataCleaner:
    """Specialized cleaner for financial data"""
    
    def __init__(self):
        self.validator = FinanceValidator()
    
    def clean_financial_dataset(self, df: pd.DataFrame, 
                                mask_pii: bool = False) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Clean financial dataset with finance-specific rules
        
        Args:
            df: Input DataFrame
            mask_pii: Whether to mask PII data
            
        Returns:
            (cleaned_df, report)
        """
        df_clean = df.copy()
        operations = []
        
        # Detect PII
        pii_detected = self.validator.detect_pii(df_clean)
        if pii_detected:
            operations.append(f"Detected PII in columns: {list(pii_detected.keys())}")
        
        # Clean currency columns
        for col in df_clean.columns:
            col_lower = col.lower()
            
            # Currency amounts
            if any(keyword in col_lower for keyword in ['amount', 'price', 'value', 'balance', 'cost']):
                cleaned_count = 0
                for idx, value in df_clean[col].items():
                    is_valid, parsed = self.validator.validate_currency(value)
                    if is_valid:
                        df_clean.at[idx, col] = parsed
                        cleaned_count += 1
                
                if cleaned_count > 0:
                    operations.append(f"Validated and formatted {cleaned_count} currency values in '{col}'")
            
            # ISIN codes
            elif 'isin' in col_lower:
                cleaned_count = 0
                for idx, value in df_clean[col].items():
                    is_valid, cleaned = self.validator.validate_isin(value)
                    if is_valid:
                        df_clean.at[idx, col] = cleaned
                        cleaned_count += 1
                
                if cleaned_count > 0:
                    operations.append(f"Validated {cleaned_count} ISIN codes in '{col}'")
            
            # CUSIP codes
            elif 'cusip' in col_lower:
                cleaned_count = 0
                for idx, value in df_clean[col].items():
                    is_valid, cleaned = self.validator.validate_cusip(value)
                    if is_valid:
                        df_clean.at[idx, col] = cleaned
                        cleaned_count += 1
                
                if cleaned_count > 0:
                    operations.append(f"Validated {cleaned_count} CUSIP codes in '{col}'")
            
            # Account numbers
            elif any(keyword in col_lower for keyword in ['account', 'acct']):
                if mask_pii:
                    # Mask account numbers
                    df_clean[col] = df_clean[col].apply(
                        lambda x: self.validator.mask_pii(x, 'generic')
                    )
                    operations.append(f"Masked account numbers in '{col}' for privacy")
        
        # Mask PII if requested
        if mask_pii and pii_detected:
            for pii_type, columns in pii_detected.items():
                for col in columns:
                    if col in df_clean.columns:
                        df_clean[col] = df_clean[col].apply(
                            lambda x: self.validator.mask_pii(x, pii_type)
                        )
                        operations.append(f"Masked {pii_type} data in '{col}'")
        
        report = {
            'operations_performed': operations,
            'pii_detected': pii_detected,
            'rows_processed': len(df_clean)
        }
        
        return df_clean, report
