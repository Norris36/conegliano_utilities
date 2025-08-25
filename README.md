# Jensbay Utilities

Personal utility functions for data science, file operations, and web scraping tasks.

## Features

### Core Utilities (`jensbay_utilities.core`)
- **Code Analysis**: Extract function information from Python files
- **File Search**: Advanced file search with pattern matching and filtering
- **File Operations**: Get creation/modification times, filter by date ranges

### Data Utilities (`jensbay_utilities.data_utils`)
- **DataFrame Operations**: Humanize column names, standardize naming conventions
- **File Analysis**: Extract column information from Excel/CSV files

### Web Utilities (`jensbay_utilities.web_utils`)
- **Web Scraping**: Recursive link discovery and crawling

## Installation

Install directly from GitHub:
```bash
pip install git+https://github.com/yourusername/jensbay-utilities.git
```

## Usage

```python
# Import the entire package
import jensbay_utilities as ju

# Analyze a Python file
functions_df = ju.get_functions_dataframe('my_script.py')

# Search for files
matching_files = ju.hygin('/path/to/search', 'pattern', extensions=['py', 'txt'])

# Humanize DataFrame columns
clean_df = ju.humanise_df(my_dataframe)

# Crawl web links
links = ju.find_all_links('https://example.com', max_links=500)
```

Or import specific modules:
```python
from jensbay_utilities import data_utils, web_utils

# Get column information from a file
columns = data_utils.get_columns('data.xlsx')

# Find links on a website
links = web_utils.find_all_links('https://example.com')
```

## Updating

To get the latest version:
```bash
pip install --upgrade --force-reinstall git+https://github.com/yourusername/jensbay-utilities.git
```

## Requirements

- Python 3.7+
- pandas
- requests
- beautifulsoup4
- tqdm
- numpy
- matplotlib