"""
CSV Parser Module for Finance App

This module handles reading and parsing CSV files from various financial sources.
"""

import pandas as pd
from typing import Optional, List, Dict
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CSVParser:
    """Parse financial CSV files and standardize the format."""

    def __init__(self):
        """Initialize the CSV parser."""
        self.supported_formats = ['csv', 'txt']

    def read_csv(self, file_path: str, encoding: str = 'utf-8') -> Optional[pd.DataFrame]:
        """
        Read a CSV file and return a pandas DataFrame.

        Args:
            file_path: Path to the CSV file
            encoding: File encoding (default: utf-8)

        Returns:
            DataFrame containing the parsed data or None if error
        """
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            logger.info(f"Successfully read {file_path}: {len(df)} rows")
            return df
        except UnicodeDecodeError:
            # Try alternative encodings
            try:
                df = pd.read_csv(file_path, encoding='latin-1')
                logger.info(f"Successfully read {file_path} with latin-1 encoding: {len(df)} rows")
                return df
            except Exception as e:
                logger.error(f"Error reading {file_path} with latin-1: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"Error reading {file_path}: {str(e)}")
            return None

    def standardize_columns(self, df: pd.DataFrame,
                          column_mapping: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        Standardize column names to a common format.

        Args:
            df: Input DataFrame
            column_mapping: Dictionary mapping original column names to standard names

        Returns:
            DataFrame with standardized column names
        """
        if column_mapping:
            df = df.rename(columns=column_mapping)

        # Convert column names to lowercase and replace spaces with underscores
        df.columns = df.columns.str.lower().str.replace(' ', '_')

        return df

    def parse_transaction_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Parse and clean transaction data.

        Args:
            df: Input DataFrame with transaction data

        Returns:
            Cleaned and parsed DataFrame
        """
        # Make a copy to avoid modifying original
        df = df.copy()

        # Common column names to look for
        date_columns = ['date', 'transaction_date', 'posting_date', 'transaction_dt']
        amount_columns = ['amount', 'transaction_amount', 'debit', 'credit']
        vendor_columns = ['description', 'merchant', 'vendor', 'payee', 'memo']

        # Identify and rename columns
        for col in df.columns:
            col_lower = col.lower()

            # Date column
            if any(date_term in col_lower for date_term in date_columns):
                if 'date' not in df.columns:
                    df.rename(columns={col: 'date'}, inplace=True)

            # Amount column
            elif any(amt_term in col_lower for amt_term in amount_columns):
                if 'amount' not in df.columns:
                    df.rename(columns={col: 'amount'}, inplace=True)

            # Vendor/Description column
            elif any(vendor_term in col_lower for vendor_term in vendor_columns):
                if 'vendor' not in df.columns:
                    df.rename(columns={col: 'vendor'}, inplace=True)

        # Parse date column if it exists
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')

        # Parse amount column if it exists
        if 'amount' in df.columns:
            # Remove currency symbols and convert to float
            df['amount'] = df['amount'].replace('[\$,]', '', regex=True).astype(float)

        # Clean vendor names
        if 'vendor' in df.columns:
            df['vendor'] = df['vendor'].str.strip()

        logger.info(f"Parsed {len(df)} transactions")
        return df

    def validate_data(self, df: pd.DataFrame) -> tuple[bool, List[str]]:
        """
        Validate that the DataFrame has required columns.

        Args:
            df: DataFrame to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        required_columns = ['date', 'amount', 'vendor']

        for col in required_columns:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")

        if df.empty:
            errors.append("DataFrame is empty")

        is_valid = len(errors) == 0
        return is_valid, errors
