# Danish Bank Transaction Preprocessing

Process and validate Danish bank transaction exports with automatic preprocessing and cross-file validation.

## Overview

This module processes CSV exports from Danish banks (e.g., Nordea) and provides tools to:
- **Standardize** Danish column names to English
- **Parse** Danish number formats (comma as decimal separator)
- **Extract** purchase dates from transaction descriptions
- **Validate** transactions across multiple files
- **Detect** duplicate transactions
- **Generate** comprehensive validation reports

## Features

### 1. Danish Bank Preprocessor (`danish_bank_preprocessor.py`)

Handles the unique formatting of Danish bank exports:

- **Column Translation**: Converts Danish column names to English
  - `Bogføringsdato` → `booking_date`
  - `Beløb` → `amount`
  - `Beskrivelse` → `description`
  - And more...

- **Amount Parsing**: Correctly handles Danish decimal format
  - Input: `1000,72` → Output: `1000.72`
  - Input: `-248,00` → Output: `-248.00`

- **Purchase Date Extraction**: Parses embedded dates from descriptions
  - "PARADIS DANMARK A/S **Den 28.08**" → Extracts August 28th
  - Uses booking date year for full date construction
  - Falls back to booking date if no embedded date found

- **Reserved Transaction Filtering**: Excludes pending/reserved transactions
  - "Reserveret" entries are filtered out for clean analysis

### 2. Transaction Comparator (`transaction_comparator.py`)

Validates transactions across multiple files:

- **Duplicate Detection**:
  - Find transactions with same date + amount + description
  - Identify exact duplicates (all fields identical)
  - Crucial for detecting multiple savings transfers or errors

- **File Comparison**:
  - Compare transactions between any two files
  - Find transactions unique to each file
  - Identify matching transactions

- **Validation Reports**:
  - Combined transaction CSV (all files merged)
  - Duplicate transaction CSV (potential duplicates)
  - Exact duplicates CSV (identical rows)
  - Summary text report with statistics

## Usage

### Quick Start (Command Line)

```bash
cd finance_app
python process_danish_bank.py august_2022.csv september_2022.csv october_2022.csv
```

This will:
1. Process all CSV files
2. Generate standardized output files
3. Run cross-file validation
4. Create detailed reports in `./processed/validation_report/`

### Programmatic Usage

```python
from finance_app.danish_bank_preprocessor import DanishBankPreprocessor
from finance_app.transaction_comparator import TransactionComparator

# Step 1: Preprocess files
preprocessor = DanishBankPreprocessor()
df_august = preprocessor.process_file('transactions_august.csv')
df_september = preprocessor.process_file('transactions_september.csv')

# Step 2: Save preprocessed files (optional)
preprocessor.save_processed(df_august, 'august_processed.csv')
preprocessor.save_processed(df_september, 'september_processed.csv')

# Step 3: Compare and validate
comparator = TransactionComparator()
comparator.add_file('August', df_august)
comparator.add_file('September', df_september)

# Step 4: Generate reports
results = comparator.generate_report('./reports')

# Step 5: Check for issues
if results['duplicate_transactions'] > 0:
    print(f"⚠️ Found {results['duplicate_transactions']} potential duplicates!")
    # Review reports/duplicate_transactions.csv
```

### Single File Processing

```python
from finance_app.danish_bank_preprocessor import DanishBankPreprocessor

preprocessor = DanishBankPreprocessor()
df = preprocessor.process_file('my_bank_export.csv')

# Access standardized data
print(f"Processed {len(df)} transactions")
print(f"Date range: {df['booking_date'].min()} to {df['booking_date'].max()}")
print(f"Total amount: {df['amount'].sum():.2f} DKK")

# View the data
print(df[['booking_date', 'purchase_date', 'amount', 'description']].head())
```

## Input File Format

Your Danish bank CSV should have these columns (Danish names):

```csv
Bogføringsdato;Beløb;Afsender;Modtager;Navn;Beskrivelse;Saldo;Valuta;Afstemt
2022/08/30;-78,00;6881570910;;;PARADIS DANMARK A/S Den 28.08;2983,08;DKK;
2022/08/30;-248,00;6881570910;;;Nordea pay køb. SUND-SULT APS Den 28.08;3061,08;DKK;
```

**Requirements:**
- Semicolon (`;`) as separator
- Comma (`,`) as decimal separator
- Date format: `YYYY/MM/DD`
- Currency: typically DKK

## Output Format

Preprocessed CSV with English column names:

```csv
booking_date,purchase_date,amount,description,sender,receiver,name,balance,currency,account_number,source_file_date
2022-08-30,2022-08-28,-78.00,PARADIS DANMARK A/S Den 28.08,6881570910,,,,2983.08,DKK,6881570910,
```

**Key Improvements:**
- Standard decimal format (period as separator)
- ISO date format (YYYY-MM-DD)
- Extracted purchase dates
- English column names
- Metadata fields (account number, source file)

## Use Cases

### 1. Monthly Reconciliation
Process and compare monthly statements to ensure all transactions are recorded correctly:

```bash
python process_danish_bank.py jan.csv feb.csv mar.csv
```

### 2. Duplicate Detection
Identify repeated transactions (especially important for auto-savings):

```python
comparator = TransactionComparator()
comparator.add_file('Export1', df1)
duplicates = comparator.find_duplicates()
print(f"Found {len(duplicates)} potential duplicates")
```

### 3. Multi-Account Validation
Compare transactions across different accounts to track transfers:

```python
comparator = TransactionComparator()
comparator.add_file('Account_A', df_account_a)
comparator.add_file('Account_B', df_account_b)
results = comparator.compare_files('Account_A', 'Account_B')
```

## Why Duplicate Detection Matters

Danish banks often have legitimate repeated transactions:
- **Auto-savings**: Multiple small transfers (e.g., 10 DKK each)
- **Round-up savings**: Automatic transfers after purchases
- **Recurring payments**: Subscriptions, rent, etc.

The comparator helps you:
1. **Verify** these are legitimate (not errors)
2. **Track** patterns in your savings
3. **Ensure** no accidental double-charges

## Reports Generated

When you run `generate_report()`, you get:

1. **`combined_transactions.csv`**
   - All transactions from all files
   - Includes `source_file` column to track origin

2. **`duplicate_transactions.csv`** (if any found)
   - Transactions with matching date + amount + description
   - Includes `duplicate_count` field
   - Sorted by transaction key for easy review

3. **`exact_duplicates.csv`** (if any found)
   - Completely identical rows
   - Potential data errors that need investigation

4. **`validation_summary.txt`**
   - Overview statistics
   - Per-file breakdown
   - Top duplicate patterns
   - Recommendations for review

## Troubleshooting

### "Failed to read CSV"
- Check that the file uses semicolon (`;`) as separator
- Verify the encoding (UTF-8 or Latin-1)
- Ensure Danish column names are present

### "Invalid data format"
- Verify required columns exist: `Bogføringsdato`, `Beløb`, `Beskrivelse`
- Check that dates are in `YYYY/MM/DD` format
- Ensure amounts use comma as decimal separator

### "Too many duplicates"
- This is often normal for Danish savings accounts
- Review the duplicate patterns in the summary report
- Check if they're auto-savings transfers (usually legitimate)

### "Purchase date extraction failed"
- The preprocessor falls back to booking date automatically
- This happens when "Den DD.MM" pattern is not found
- No action needed - the transaction is still processed

## Integration with Existing Finance App

This module integrates seamlessly with the existing finance app:

```python
# Preprocess Danish bank data
from finance_app.danish_bank_preprocessor import DanishBankPreprocessor
preprocessor = DanishBankPreprocessor()
df = preprocessor.process_file('nordea_export.csv')

# Use with existing categorizer
from finance_app.categorizer import VendorCategorizer
categorizer = VendorCategorizer()
categorized_df = categorizer.categorize_transactions(df)

# Visualize in Streamlit app
# Upload the preprocessed CSV to app.py
```

## Future Enhancements

Planned features:
- [ ] Support for more Danish banks (Danske Bank, Jyske Bank)
- [ ] Automatic transfer matching between accounts
- [ ] Budget comparison against actual spending
- [ ] Recurring transaction detection
- [ ] Export to accounting software formats
- [ ] Web interface for file upload and processing

## Version

Current version: 1.0

## License

Part of the Conegliano Utilities project.
