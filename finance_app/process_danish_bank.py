"""
Process Danish Bank Files - Main Script

Easy-to-use script for processing and comparing Danish bank transaction files.

Usage:
    python process_danish_bank.py <file1.csv> [file2.csv] [file3.csv] ...

Version: 1.0
"""

import sys
from pathlib import Path
from danish_bank_preprocessor import DanishBankPreprocessor
from transaction_comparator import TransactionComparator


def process_and_compare_files(file_paths: list, output_dir: str = './processed'):
    """
    Process multiple Danish bank CSV files and compare them.

    Args:
        file_paths: List of CSV file paths
        output_dir: Directory to save processed files and reports
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("DANISH BANK TRANSACTION PROCESSOR")
    print("=" * 70)
    print()

    # Initialize preprocessor and comparator
    preprocessor = DanishBankPreprocessor()
    comparator = TransactionComparator()

    processed_files = {}

    # Process each file
    print(f"Processing {len(file_paths)} file(s)...\n")

    for i, file_path in enumerate(file_paths, 1):
        file_path = Path(file_path)

        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue

        print(f"[{i}/{len(file_paths)}] Processing: {file_path.name}")

        try:
            # Process file
            df = preprocessor.process_file(str(file_path))

            # Save processed version
            output_file = output_path / f"{file_path.stem}_processed.csv"
            preprocessor.save_processed(df, str(output_file))

            # Add to comparator
            file_id = file_path.stem
            comparator.add_file(file_id, df)
            processed_files[file_id] = df

            # Show file summary
            print(f"   ✓ Transactions: {len(df)}")
            print(f"   ✓ Date range: {df['booking_date'].min().strftime('%Y-%m-%d')} to {df['booking_date'].max().strftime('%Y-%m-%d')}")
            print(f"   ✓ Total amount: {df['amount'].sum():.2f} DKK")
            print(f"   ✓ Saved to: {output_file.name}")
            print()

        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
            print()
            continue

    # If we have multiple files, run comparison
    if len(processed_files) > 1:
        print("-" * 70)
        print("RUNNING CROSS-FILE VALIDATION")
        print("-" * 70)
        print()

        try:
            # Generate comparison report
            report_dir = output_path / 'validation_report'
            results = comparator.generate_report(str(report_dir))

            print("\n✓ Validation complete!")
            print(f"\nSummary:")
            print(f"  Total transactions across all files: {results['total_transactions']}")
            print(f"  Potential duplicates found: {results['duplicate_transactions']}")
            print(f"  Exact duplicates found: {results['exact_duplicate_transactions']}")

            if results['duplicate_transactions'] > 0:
                print(f"\n⚠️  WARNING: Found {results['duplicate_transactions']} potential duplicate transactions!")
                print("     These could be:")
                print("     - Legitimate repeated transactions (e.g., multiple savings transfers)")
                print("     - Duplicate entries that need investigation")
                print(f"     Review: {report_dir}/duplicate_transactions.csv")

            if results['exact_duplicate_transactions'] > 0:
                print(f"\n⚠️  ALERT: Found {results['exact_duplicate_transactions']} EXACT duplicate transactions!")
                print("     These are completely identical rows.")
                print(f"     Review: {report_dir}/exact_duplicates.csv")

            print(f"\nFull report available in: {report_dir}/")

        except Exception as e:
            print(f"✗ Error during validation: {str(e)}")

    elif len(processed_files) == 1:
        print("-" * 70)
        print("Single file processed - no cross-file validation needed")
        print("-" * 70)
    else:
        print("⚠️  No files were successfully processed")

    print("\n" + "=" * 70)
    print("PROCESSING COMPLETE")
    print("=" * 70)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Danish Bank Transaction Processor")
        print()
        print("Usage:")
        print("  python process_danish_bank.py <file1.csv> [file2.csv] [file3.csv] ...")
        print()
        print("Examples:")
        print("  # Process single file")
        print("  python process_danish_bank.py transactions_202208.csv")
        print()
        print("  # Process and compare multiple files")
        print("  python process_danish_bank.py august.csv september.csv october.csv")
        print()
        print("Output:")
        print("  - Processed CSV files will be saved to ./processed/")
        print("  - Validation reports will be saved to ./processed/validation_report/")
        sys.exit(1)

    # Get file paths from command line arguments
    file_paths = sys.argv[1:]

    # Process files
    process_and_compare_files(file_paths)


if __name__ == "__main__":
    main()
