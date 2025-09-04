# Conegliano Utilities

## Overview
`conegliano-utilities` is a Python package that provides a collection of utility functions for data science and development tasks, including data manipulation, web interactions, visualization, and workout generation. This package is designed to simplify common programming tasks and enhance productivity.

## Installation

### First Time Installation
Install directly from GitHub:

```bash
pip install git+https://github.com/Norris36/conegliano_utilities.git
```

### Development Installation
For development or local modifications:

```bash
git clone https://github.com/Norris36/conegliano_utilities.git
cd conegliano_utilities
pip install -e .
```

## Updates

The package includes automatic update checking! When you import it, you'll be notified if a newer version is available.

### Update to Latest Version
```bash
pip install --upgrade git+https://github.com/Norris36/conegliano_utilities.git
```

### Install Specific Version
```bash
pip install git+https://github.com/Norris36/conegliano_utilities.git@v1.0.8
```

## Usage
After installing the package, you can import the utilities in your Python scripts:

```python
import conegliano_utilities
# or import specific modules
from conegliano_utilities import core, data_utils, web_utils, viz_utils, workout
```

### Examples

#### Data Analysis
```python
import pandas as pd
from conegliano_utilities.data_utils import get_columns, humanise_df

# Get column information from Excel/CSV
columns_info = get_columns('data.xlsx')
print(columns_info)

# Humanize DataFrame column names
df = pd.read_csv('data.csv')
clean_df = humanise_df(df)
```

#### Workout Generation
```python
from conegliano_utilities.workout import WorkoutGenerator
import pandas as pd

# Create workout data
exercises = pd.DataFrame({
    'exercise': ['Push-ups', 'Squats', 'Crunches'],
    'area': ['Upper', 'Legs', 'Abs'],
    'diffucility': [3, 4, 2]
})

# Generate workout plan
generator = WorkoutGenerator(exercises)
workout_plan = generator.generate_workout_plan([3, 4, 5])
```

#### File Operations
```python
from conegliano_utilities.core import hygin, find_files

# Search for files
python_files = hygin('/path/to/search', '*.py', extensions=['py'])

# Find files by date
recent_files = find_files(python_files, target_date='2024-01-01', days=30)
```

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.