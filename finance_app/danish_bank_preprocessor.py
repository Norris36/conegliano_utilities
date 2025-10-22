"""
Danish Bank Transaction Preprocessor

Preprocesses transaction data from Danish banks (e.g., Nordea) into standardized format.
Handles Danish column names, date formats, and amount formatting.

Version: 1.0
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple


class DanishBankPreprocessor:
    """Preprocesses Danish bank transaction CSV files."""

    # Column mapping: Danish -> English
    COLUMN_MAPPING = {
        'Bogføringsdato': 'booking_date',
        'Beløb': 'amount',
        'Afsender': 'sender',
        'Modtager': 'receiver',
        'Navn': 'name',
        'Beskrivelse': 'description',
        'Saldo': 'balance',
        'Valuta': 'currency',
        'Afstemt': 'reconciled'
    }

    def __init__(self):
        """Initialize the preprocessor."""
        self.account_number = None
        self.file_date = None

    def extract_metadata_from_filename(self, filename: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract account number and date from filename.

        Expected format: *account_number*date*.csv

        Args:
            filename: The CSV filename

        Returns:
            Tuple of (account_number, date_string)
        """
        # Try to extract account number (assuming it's a sequence of digits)
        account_match = re.search(r'(\d{6,})', filename)
        account = account_match.group(1) if account_match else None

        # Try to extract date (various formats)
        # Format: YYYYMMDD, YYYY-MM-DD, YYYY_MM_DD, etc.
        date_patterns = [
            r'(\d{8})',  # YYYYMMDD
            r'(\d{4}[-_]\d{2}[-_]\d{2})',  # YYYY-MM-DD or YYYY_MM_DD
        ]

        date_str = None
        for pattern in date_patterns:
            date_match = re.search(pattern, filename)
            if date_match:
                date_str = date_match.group(1)
                break

        return account, date_str

    def parse_amount(self, amount_str: str) -> Optional[float]:
        """
        Parse Danish formatted amount string to float.

        Handles formats like:
        - "-1593,72" -> -1593.72
        - "1000,00" -> 1000.00
        - "-10,00" -> -10.00

        Args:
            amount_str: Amount string with comma as decimal separator

        Returns:
            Float value or None if parsing fails
        """
        if pd.isna(amount_str) or amount_str == '':
            return None

        try:
            # Convert to string and strip whitespace
            amount_str = str(amount_str).strip()

            # Replace comma with period for decimal
            amount_str = amount_str.replace(',', '.')

            # Remove any spaces (thousands separator)
            amount_str = amount_str.replace(' ', '')

            return float(amount_str)
        except (ValueError, AttributeError):
            return None

    def extract_purchase_date(self, description: str, booking_date: pd.Timestamp) -> pd.Timestamp:
        """
        Extract purchase date from description field.

        Looks for patterns like "Den 28.08" (The 28.08) in the description.
        If not found, returns the booking date.

        Args:
            description: Transaction description
            booking_date: Booking date as fallback

        Returns:
            Purchase date as Timestamp
        """
        if pd.isna(description):
            return booking_date

        # Pattern: "Den DD.MM"
        pattern = r'Den\s+(\d{1,2})\.(\d{1,2})'
        match = re.search(pattern, str(description))

        if match:
            day = int(match.group(1))
            month = int(match.group(2))

            # Use year from booking date
            year = booking_date.year

            try:
                # Create date
                purchase_date = pd.Timestamp(year=year, month=month, day=day)

                # If purchase date is in the future relative to booking date,
                # it's probably from the previous year
                if purchase_date > booking_date:
                    purchase_date = pd.Timestamp(year=year-1, month=month, day=day)

                return purchase_date
            except ValueError:
                # Invalid date, return booking date
                return booking_date

        # No date found in description, use booking date
        return booking_date

    def parse_date(self, date_str: str) -> Optional[pd.Timestamp]:
        """
        Parse date string to Timestamp.

        Handles format: YYYY/MM/DD

        Args:
            date_str: Date string

        Returns:
            Timestamp or None if parsing fails
        """
        if pd.isna(date_str) or date_str == '' or date_str == 'Reserveret':
            return None

        try:
            # Handle YYYY/MM/DD format
            return pd.to_datetime(date_str, format='%Y/%m/%d')
        except:
            return None

    def read_csv(self, file_path: str, encoding: str = 'utf-8') -> pd.DataFrame:
        """
        Read Danish bank CSV file.

        Args:
            file_path: Path to CSV file
            encoding: File encoding (default: utf-8, falls back to latin-1)

        Returns:
            DataFrame with raw data
        """
        path = Path(file_path)

        # Extract metadata from filename
        self.account_number, self.file_date = self.extract_metadata_from_filename(path.name)

        # Try to read with different encodings
        encodings = [encoding, 'utf-8', 'latin-1', 'iso-8859-1', 'cp1252']

        for enc in encodings:
            try:
                # Read CSV with semicolon separator
                df = pd.read_csv(file_path, sep=';', encoding=enc)
                return df
            except UnicodeDecodeError:
                continue
            except Exception as e:
                raise Exception(f"Failed to read CSV: {str(e)}")

        raise Exception(f"Could not read file with any of the attempted encodings: {encodings}")

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess the DataFrame.

        Steps:
        1. Rename columns from Danish to English
        2. Filter out reserved/pending transactions
        3. Parse dates
        4. Parse amounts
        5. Extract purchase dates from descriptions
        6. Add metadata columns

        Args:
            df: Raw DataFrame

        Returns:
            Preprocessed DataFrame
        """
        # Make a copy
        df = df.copy()

        # Rename columns
        df.rename(columns=self.COLUMN_MAPPING, inplace=True)

        # Filter out reserved transactions (keep only rows with valid booking_date)
        # "Reserveret" will be filtered when we parse dates
        df['booking_date_parsed'] = df['booking_date'].apply(self.parse_date)
        df = df[df['booking_date_parsed'].notna()].copy()
        df.rename(columns={'booking_date_parsed': 'booking_date'}, inplace=True)

        # Parse amounts
        df['amount'] = df['amount'].apply(self.parse_amount)

        # Extract purchase dates from descriptions
        df['purchase_date'] = df.apply(
            lambda row: self.extract_purchase_date(row['description'], row['booking_date']),
            axis=1
        )

        # Parse balance
        if 'balance' in df.columns:
            df['balance'] = df['balance'].apply(self.parse_amount)

        # Add metadata
        df['account_number'] = self.account_number
        df['source_file_date'] = self.file_date

        # Reorder columns for clarity
        column_order = [
            'booking_date',
            'purchase_date',
            'amount',
            'description',
            'sender',
            'receiver',
            'name',
            'balance',
            'currency',
            'account_number',
            'source_file_date',
            'reconciled'
        ]

        # Only include columns that exist
        column_order = [col for col in column_order if col in df.columns]

        # Add any remaining columns not in the order list
        remaining_cols = [col for col in df.columns if col not in column_order]
        column_order.extend(remaining_cols)

        df = df[column_order]

        # Sort by booking date
        df = df.sort_values('booking_date', ascending=True)

        # Reset index
        df.reset_index(drop=True, inplace=True)

        return df

    def process_file(self, file_path: str) -> pd.DataFrame:
        """
        Complete processing pipeline for a single file.

        Args:
            file_path: Path to CSV file

        Returns:
            Preprocessed DataFrame
        """
        df = self.read_csv(file_path)
        df = self.preprocess(df)
        return df

    def save_processed(self, df: pd.DataFrame, output_path: str):
        """
        Save preprocessed DataFrame to CSV.

        Args:
            df: Preprocessed DataFrame
            output_path: Output file path
        """
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"Saved processed data to: {output_path}")


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else file_path.replace('.csv', '_processed.csv')

        preprocessor = DanishBankPreprocessor()
        df = preprocessor.process_file(file_path)

        print(f"\nProcessed {len(df)} transactions")
        print(f"Date range: {df['booking_date'].min()} to {df['booking_date'].max()}")
        print(f"Total amount: {df['amount'].sum():.2f} {df['currency'].iloc[0] if 'currency' in df.columns else ''}")

        preprocessor.save_processed(df, output_path)
    else:
        print("Usage: python danish_bank_preprocessor.py <input_csv> [output_csv]")
