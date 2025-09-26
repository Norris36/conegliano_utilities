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

## Troubleshooting Installation

### Version Not Updating

If `pip install --upgrade` doesn't update to the latest version:

#### **Check Current Version**
```bash
# Before install
pip show conegliano-utilities
python -c "import conegliano_utilities; print(conegliano_utilities.__version__)"
```

#### **Force Clean Install**
```bash
# Clear pip cache and force reinstall
pip install --no-cache-dir --force-reinstall git+https://github.com/Norris36/conegliano_utilities.git
```

#### **Debug Version Issues**
```bash
# Verbose install to see detailed logs
pip install --upgrade --verbose git+https://github.com/Norris36/conegliano_utilities.git

# Check for multiple installations
pip list | grep conegliano
python -c "import conegliano_utilities; print(conegliano_utilities.__file__)"

# Verify GitHub repository version
curl -s https://raw.githubusercontent.com/Norris36/conegliano_utilities/main/setup.py | grep version
```

#### **Common Issues**
- **Pip cache**: Old version cached - use `--no-cache-dir`
- **Multiple installations**: Different locations conflict - check `__file__` path
- **Local development version**: Local repo overriding installed package
- **Import conflicts**: Restart Python session after install

### NumPy Compatibility Issues

If you see `AttributeError: _ARRAY_API not found`:

```bash
# Option 1: Downgrade NumPy (quickest fix)
pip install "numpy<2"

# Option 2: Update incompatible packages
pip install --upgrade pyarrow numexpr bottleneck

# Option 3: Fresh environment
conda create -n new_env python=3.9 numpy=1.24
conda activate new_env
pip install git+https://github.com/Norris36/conegliano_utilities.git
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