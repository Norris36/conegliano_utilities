# jensbay-utilities

## Overview
`jensbay-utilities` is a Python package that provides a collection of utility functions for various tasks, including data manipulation, web interactions, and data visualization. This package is designed to simplify common programming tasks and enhance productivity.

## Installation
To install the package, clone the repository and run the following command:

```bash
pip install .
```

Alternatively, you can install the required dependencies directly using:

```bash
pip install -r requirements.txt
```

## Usage
After installing the package, you can import the utilities in your Python scripts as follows:

```python
from jensbay_utilities import core, data_utils, web_utils, viz_utils
```

### Example
Here is a brief example of how to use the utilities:

```python
# Example of using data_utils
import pandas as pd
from jensbay_utilities import data_utils

data = pd.read_csv('data.csv')
cleaned_data = data_utils.clean_data(data)

# Example of using web_utils
from jensbay_utilities import web_utils

response = web_utils.make_request('https://api.example.com/data')

# Example of using viz_utils
from jensbay_utilities import viz_utils

viz_utils.plot_data(cleaned_data)
```

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.