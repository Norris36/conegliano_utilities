"""
Transaction Comparator

Compares transactions across multiple bank statement files to validate data integrity
and identify duplicates, missing transactions, and discrepancies.

Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from datetime import timedelta


class TransactionComparator:
    """Compare and validate transactions across multiple files."""

    def __init__(self, tolerance_days: int = 0, tolerance_amount: float = 0.01):
        """
        Initialize the comparator.

        Args:
            tolerance_days: Number of days tolerance for date matching (default: 0 = exact match)
            tolerance_amount: Amount tolerance for matching (default: 0.01 = 1 cent)
        """
        self.tolerance_days = tolerance_days
        self.tolerance_amount = tolerance_amount
        self.files = {}
        self.combined_df = None

    def add_file(self, name: str, df: pd.DataFrame):
        """
        Add a preprocessed DataFrame to the comparison set.

        Args:
            name: Identifier for this file/dataset
            df: Preprocessed DataFrame
        """
        # Add source column to track which file each transaction came from
        df = df.copy()
        df['source_file'] = name
        self.files[name] = df

    def combine_all(self) -> pd.DataFrame:
        """
        Combine all files into a single DataFrame.

        Returns:
            Combined DataFrame with all transactions
        """
        if not self.files:
            raise ValueError("No files added yet. Use add_file() first.")

        all_dfs = list(self.files.values())
        self.combined_df = pd.concat(all_dfs, ignore_index=True)

        # Sort by booking date
        self.combined_df = self.combined_df.sort_values('booking_date')

        return self.combined_df

    def create_transaction_key(self, row: pd.Series) -> str:
        """
        Create a unique key for a transaction based on key fields.

        Args:
            row: Transaction row

        Returns:
            String key for matching
        """
        date = row['booking_date'].strftime('%Y-%m-%d') if pd.notna(row['booking_date']) else 'NA'
        amount = f"{row['amount']:.2f}" if pd.notna(row['amount']) else 'NA'
        description = str(row['description'])[:50] if pd.notna(row['description']) else 'NA'

        return f"{date}|{amount}|{description}"

    def find_duplicates(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Find duplicate transactions within a dataset.

        Duplicates are defined as transactions with:
        - Same booking date
        - Same amount
        - Same description

        Args:
            df: DataFrame to check (defaults to combined_df)

        Returns:
            DataFrame containing only duplicate transactions
        """
        if df is None:
            df = self.combined_df

        if df is None:
            raise ValueError("No data available. Run combine_all() first.")

        # Create transaction key
        df = df.copy()
        df['transaction_key'] = df.apply(self.create_transaction_key, axis=1)

        # Find duplicates
        duplicate_mask = df.duplicated(subset=['transaction_key'], keep=False)
        duplicates = df[duplicate_mask].copy()

        # Count occurrences
        dup_counts = df['transaction_key'].value_counts()
        duplicates['duplicate_count'] = duplicates['transaction_key'].map(dup_counts)

        # Sort by transaction key and booking date
        duplicates = duplicates.sort_values(['transaction_key', 'booking_date'])

        return duplicates

    def find_exact_duplicates(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Find EXACT duplicate transactions (same in every field).

        This is more strict than find_duplicates() and identifies truly identical rows.

        Args:
            df: DataFrame to check (defaults to combined_df)

        Returns:
            DataFrame containing only exact duplicate transactions
        """
        if df is None:
            df = self.combined_df

        if df is None:
            raise ValueError("No data available. Run combine_all() first.")

        # Check for duplicates across all columns except source_file
        check_columns = [col for col in df.columns if col not in ['source_file', 'source_file_date']]

        duplicate_mask = df.duplicated(subset=check_columns, keep=False)
        exact_duplicates = df[duplicate_mask].copy()

        return exact_duplicates.sort_values('booking_date')

    def compare_files(self, file1: str, file2: str) -> Dict:
        """
        Compare two files to find matches and differences.

        Args:
            file1: Name of first file
            file2: Name of second file

        Returns:
            Dictionary with comparison results
        """
        if file1 not in self.files or file2 not in self.files:
            raise ValueError(f"Files not found. Available files: {list(self.files.keys())}")

        df1 = self.files[file1].copy()
        df2 = self.files[file2].copy()

        # Create transaction keys
        df1['transaction_key'] = df1.apply(self.create_transaction_key, axis=1)
        df2['transaction_key'] = df2.apply(self.create_transaction_key, axis=1)

        # Find matches
        keys1 = set(df1['transaction_key'])
        keys2 = set(df2['transaction_key'])

        in_both = keys1 & keys2
        only_in_file1 = keys1 - keys2
        only_in_file2 = keys2 - keys1

        # Get actual transactions
        matches = df1[df1['transaction_key'].isin(in_both)]
        only_1 = df1[df1['transaction_key'].isin(only_in_file1)]
        only_2 = df2[df2['transaction_key'].isin(only_in_file2)]

        return {
            'file1_name': file1,
            'file2_name': file2,
            'file1_count': len(df1),
            'file2_count': len(df2),
            'matches_count': len(in_both),
            'only_in_file1_count': len(only_in_file1),
            'only_in_file2_count': len(only_in_file2),
            'matches': matches,
            'only_in_file1': only_1,
            'only_in_file2': only_2
        }

    def validate_all_files(self) -> Dict:
        """
        Run comprehensive validation across all files.

        Returns:
            Dictionary with validation results
        """
        if not self.files:
            raise ValueError("No files added yet. Use add_file() first.")

        # Combine all files
        combined = self.combine_all()

        # Find duplicates
        duplicates = self.find_duplicates(combined)
        exact_duplicates = self.find_exact_duplicates(combined)

        # Statistics per file
        file_stats = {}
        for name, df in self.files.items():
            file_stats[name] = {
                'transaction_count': len(df),
                'date_range': (df['booking_date'].min(), df['booking_date'].max()),
                'total_amount': df['amount'].sum(),
                'unique_descriptions': df['description'].nunique()
            }

        return {
            'total_files': len(self.files),
            'total_transactions': len(combined),
            'duplicate_transactions': len(duplicates),
            'exact_duplicate_transactions': len(exact_duplicates),
            'file_statistics': file_stats,
            'duplicates_df': duplicates,
            'exact_duplicates_df': exact_duplicates
        }

    def generate_report(self, output_dir: str = '.'):
        """
        Generate comprehensive comparison report.

        Creates multiple CSV files:
        - combined_transactions.csv: All transactions from all files
        - duplicate_transactions.csv: Potential duplicate transactions
        - exact_duplicates.csv: Exact duplicate transactions
        - validation_summary.txt: Summary report

        Args:
            output_dir: Directory to save reports
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Run validation
        results = self.validate_all_files()

        # Save combined transactions
        combined_path = output_path / 'combined_transactions.csv'
        self.combined_df.to_csv(combined_path, index=False)

        # Save duplicates
        if len(results['duplicates_df']) > 0:
            dup_path = output_path / 'duplicate_transactions.csv'
            results['duplicates_df'].to_csv(dup_path, index=False)

        # Save exact duplicates
        if len(results['exact_duplicates_df']) > 0:
            exact_dup_path = output_path / 'exact_duplicates.csv'
            results['exact_duplicates_df'].to_csv(exact_dup_path, index=False)

        # Generate summary report
        summary_path = output_path / 'validation_summary.txt'
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("TRANSACTION VALIDATION REPORT\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"Total Files Processed: {results['total_files']}\n")
            f.write(f"Total Transactions: {results['total_transactions']}\n")
            f.write(f"Potential Duplicates: {results['duplicate_transactions']}\n")
            f.write(f"Exact Duplicates: {results['exact_duplicate_transactions']}\n\n")

            f.write("-" * 60 + "\n")
            f.write("FILE STATISTICS\n")
            f.write("-" * 60 + "\n\n")

            for file_name, stats in results['file_statistics'].items():
                f.write(f"\n{file_name}:\n")
                f.write(f"  Transactions: {stats['transaction_count']}\n")
                f.write(f"  Date Range: {stats['date_range'][0]} to {stats['date_range'][1]}\n")
                f.write(f"  Total Amount: {stats['total_amount']:.2f}\n")
                f.write(f"  Unique Vendors: {stats['unique_descriptions']}\n")

            if results['duplicate_transactions'] > 0:
                f.write("\n" + "-" * 60 + "\n")
                f.write("DUPLICATE ANALYSIS\n")
                f.write("-" * 60 + "\n")
                f.write(f"\nFound {results['duplicate_transactions']} potential duplicate transactions.\n")
                f.write("These are transactions with matching date, amount, and description.\n")
                f.write("Review 'duplicate_transactions.csv' for details.\n")

                # Show top duplicate patterns
                if len(results['duplicates_df']) > 0:
                    dup_summary = results['duplicates_df'].groupby('description').size().sort_values(ascending=False).head(10)
                    f.write("\nTop 10 Most Common Duplicate Descriptions:\n")
                    for desc, count in dup_summary.items():
                        f.write(f"  {count}x: {desc[:60]}\n")

            if results['exact_duplicate_transactions'] > 0:
                f.write("\n" + "-" * 60 + "\n")
                f.write("EXACT DUPLICATES\n")
                f.write("-" * 60 + "\n")
                f.write(f"\nFound {results['exact_duplicate_transactions']} exact duplicate transactions.\n")
                f.write("These are completely identical rows that should be investigated.\n")
                f.write("Review 'exact_duplicates.csv' for details.\n")

            f.write("\n" + "=" * 60 + "\n")

        print(f"\nReport generated in: {output_path}")
        print(f"  - {combined_path.name}")
        if results['duplicate_transactions'] > 0:
            print(f"  - duplicate_transactions.csv")
        if results['exact_duplicate_transactions'] > 0:
            print(f"  - exact_duplicates.csv")
        print(f"  - {summary_path.name}")

        return results


if __name__ == "__main__":
    print("Transaction Comparator Module")
    print("Import this module to use in your scripts.")
    print("\nExample usage:")
    print("""
    from danish_bank_preprocessor import DanishBankPreprocessor
    from transaction_comparator import TransactionComparator

    # Process files
    preprocessor = DanishBankPreprocessor()
    df1 = preprocessor.process_file('file1.csv')
    df2 = preprocessor.process_file('file2.csv')

    # Compare
    comparator = TransactionComparator()
    comparator.add_file('File 1', df1)
    comparator.add_file('File 2', df2)
    comparator.generate_report('./reports')
    """)
