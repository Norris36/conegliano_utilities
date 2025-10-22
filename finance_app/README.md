# Finance Transaction Analyzer

A Streamlit-based web application for analyzing and categorizing financial transactions from CSV files.

## Features

- **CSV File Upload**: Upload transaction data from any CSV file
- **Automatic Parsing**: Intelligently detects and standardizes column names
- **Smart Categorization**: Automatically categorizes transactions based on vendor names
- **Visual Analytics**:
  - Spending by category (pie chart)
  - Top categories bar chart
  - Spending trends over time
  - Detailed transaction tables
- **Export Capabilities**: Download processed data and summaries
- **Customizable Categories**: Easily add or modify vendor categorization rules

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Setup

1. Navigate to the finance_app directory:
   ```bash
   cd finance_app
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the App

1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Open your browser and navigate to the URL shown (typically `http://localhost:8501`)

3. Upload your transaction CSV file using the sidebar

4. The app will automatically:
   - Parse your transaction data
   - Categorize transactions by vendor
   - Display interactive visualizations and summaries

### CSV File Format

Your CSV file should contain at least these columns (names may vary):

- **Date**: Transaction date (various formats supported)
- **Amount**: Transaction amount (with or without currency symbols)
- **Vendor/Description**: Merchant or vendor name

#### Example CSV:
```csv
Date,Amount,Description
2024-01-15,45.67,Walmart Grocery
2024-01-16,12.50,Starbucks Coffee
2024-01-17,125.00,Shell Gas Station
2024-01-18,1200.00,Rent Payment
```

The app will automatically detect variations like:
- `Transaction Date`, `Posting Date`, `Transaction_Dt` → `date`
- `Debit`, `Credit`, `Transaction Amount` → `amount`
- `Merchant`, `Payee`, `Memo` → `vendor`

## Customizing Categories

### Using the Config File

Edit `config/vendor_categories.json` to add or modify categories:

```json
{
  "Groceries": ["walmart", "target", "kroger"],
  "Restaurants": ["starbucks", "mcdonald", "chipotle"],
  "Your Custom Category": ["vendor1", "vendor2"]
}
```

### Programmatically

You can also add categories programmatically:

```python
from categorizer import VendorCategorizer

categorizer = VendorCategorizer()
categorizer.add_custom_rule("My Category", ["pattern1", "pattern2"])
categorizer.save_categories()
```

## Project Structure

```
finance_app/
├── app.py                          # Main Streamlit application
├── csv_parser.py                   # CSV parsing and data standardization
├── categorizer.py                  # Transaction categorization logic
├── config/
│   └── vendor_categories.json     # Category configuration
├── data/                           # Sample data (add your CSVs here)
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Modules

### csv_parser.py
Handles reading and parsing CSV files with various formats. Features:
- Multiple encoding support (UTF-8, Latin-1)
- Automatic column name detection and standardization
- Date parsing
- Amount parsing (removes currency symbols)
- Data validation

### categorizer.py
Categorizes transactions based on vendor names. Features:
- Pattern matching with regex support
- Configurable category rules
- Category summary statistics
- Custom rule management

### app.py
Main Streamlit web interface. Features:
- File upload and processing
- Interactive visualizations (pie charts, bar charts, time series)
- Category filtering
- Transaction details table
- Data export (CSV format)

## Future Enhancements

This app is designed to be branched out into a separate repository. Planned features:
- Budget tracking and alerts
- Multi-file upload and comparison
- Machine learning-based categorization
- Bank account integration
- Monthly/yearly reports
- Receipt image upload and OCR
- Split transactions
- Recurring transaction detection

## Troubleshooting

### File Not Loading
- Check that your CSV has the required columns (date, amount, vendor/description)
- Try a different encoding (the app will try UTF-8 and Latin-1)
- Ensure dates are in a recognizable format

### Categories Not Matching
- Check `config/vendor_categories.json` to see available patterns
- Add custom patterns for your specific vendors
- Vendor names are matched case-insensitively

### Performance Issues
- For large files (>10,000 transactions), the initial load may take a few seconds
- Consider filtering by date range if working with very large datasets

## Contributing

This project will be moved to its own repository. For now, submit issues or suggestions through the main conegliano_utilities repository.

## License

Part of the Conegliano Utilities project.
