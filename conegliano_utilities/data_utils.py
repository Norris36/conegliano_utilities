from matplotlib import pyplot as plt
import pandas as pd


def get_columns(path: str) -> str:
    """
    Extract column names from all sheets in an Excel file or CSV file.
    
    1. Gets file extension from path
    2. Reads file into dataframe based on extension  
    3. Extracts column names into formatted list
    4. Returns semicolon-separated string with results
    
    Args:
        path (str): File path to the Excel/CSV file to be analyzed
    
    Returns type: columns_string (str) - semicolon-separated string containing sheet names and their columns, or error message if file couldn't be read
    """
    try:
        file_extension = path.split('.')[-1].lower()
        
        if file_extension in ['xlsx', 'xlsm', 'xls']:
            # Read all sheets from Excel file
            df = pd.read_excel(path, sheet_name=None)
            columns = []
            
            # Handle multiple sheets
            for sheet_name, sheet_df in df.items():
                columns.append(f"{sheet_name}: {sheet_df.columns.tolist()}")
                
            return "; ".join(columns)
            
        elif file_extension == 'csv':
            # Read CSV file
            df = pd.read_csv(path)
            return f"CSV: {df.columns.tolist()}"
            
        else: 
            return f"{file_extension} is not a supported format. Please provide an Excel or CSV file."
               
    except Exception as e:
        return f"Error reading file: {str(e)}"


def humanise_text(text: str) -> str:
    """
    Transforms a string into human-readable format using the same rules as humanise_df.

    Applies the following transformations:
    1. Replaces underscores with spaces
    2. Replaces hyphens with spaces
    3. Applies title case to the first word
    4. Applies lowercase to remaining words

    This function uses the exact same logic as humanise_df() but works on individual strings
    instead of DataFrame columns.

    Args:
        text (str): Input string to humanize

    Returns:
        str: Humanized text with proper formatting

    Examples:
        >>> humanise_text("customer_id")
        'Customer id'

        >>> humanise_text("total_revenue_USD")
        'Total revenue usd'

        >>> humanise_text("purchase-date")
        'Purchase date'

        >>> humanise_text("FULL_NAME")
        'Full name'
    """
    # Replace underscores and hyphens with spaces
    new_text = text.replace('_', ' ').replace('-', ' ')

    # Split into words and apply title case to first word, lowercase to rest
    words = new_text.split(' ')
    formatted_words = []

    for i, word in enumerate(words):
        if i == 0:
            formatted_words.append(word.title())  # First word title case
        else:
            formatted_words.append(word.lower())  # Other words lowercase

    # Join words back together
    return ' '.join(formatted_words)


def humanise_df(local_df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a DataFrame and returns it with humanized column names.

    Uses humanise_text() to transform each column name:
    1. Creates copy of input DataFrame
    2. Replaces underscores and hyphens with spaces
    3. Applies title case to first word, lowercase to others
    4. Returns DataFrame with formatted column names

    Args:
        local_df (pd.DataFrame): Input DataFrame to humanize

    Returns:
        pd.DataFrame: DataFrame with humanized column names

    Examples:
        >>> df = pd.DataFrame({'customer_id': [1, 2], 'total_revenue_USD': [100, 200]})
        >>> humanised = humanise_df(df)
        >>> humanised.columns.tolist()
        ['Customer id', 'Total revenue usd']
    """
    # Create a copy to avoid modifying the original
    df_copy = local_df.copy()

    # Apply humanise_text to each column name
    column_mapping = {col: humanise_text(col) for col in df_copy.columns}
    df_copy.rename(columns=column_mapping, inplace=True)

    return df_copy


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renames DataFrame columns to a standardized format.
    
    1. Creates copy of input DataFrame
    2. Creates mapping dictionary for column transformations
    3. Applies special rule for 'Name'/'name' columns
    4. Standardizes other columns (remove spaces, underscores, lowercase)
    5. Returns DataFrame with renamed columns
    
    Args:
        df (pd.DataFrame): The DataFrame whose columns are to be renamed

    Returns type: df_copy (pd.DataFrame) - DataFrame with standardized column names
    """
    # Create a copy to avoid modifying the original
    df_copy = df.copy()
    
    # Create a mapping of old to new column names
    column_mapping = {}
    
    for col in df_copy.columns:
        if col in ['Name', 'name']:
            new_name = 'name_'
        else:
            new_name = col.replace("  ", " ")  # Replace double spaces
            new_name = new_name.replace("-", "")  # Remove hyphens
            new_name = new_name.replace(" ", "_")  # Replace spaces with underscores
            new_name = new_name.lower()  # Convert to lowercase
        
        column_mapping[col] = new_name
    
    # Apply the renaming
    df_copy.rename(columns=column_mapping, inplace=True)
    
    return df_copy

def pareto_distribution(value_counts):
    
    index = value_counts.index
    values = value_counts.g_counts
    
    # Plotting the cumulative distribution
    plt.figure(figsize=(10, 6))
    plt.plot(index, values, label='Cumulative Distribution')

    # Adding percentile markers
    percentiles = [10, 25, 50, 75] + list(range(80, 101, 5))
    for percentile in percentiles:
        x_value = np.percentile(index, percentile)
        y_value = np.percentile(values, percentile)
        plt.scatter(x_value, y_value, color='red')  # Mark the percentile
        
        # Adjust text to display percentile and x_value, position bottom-right of the marker
        plt.text(x_value, y_value, f'{percentile}% ({x_value:.2f}, {y_value:.2f})', 
                fontsize=9, 
                verticalalignment='top',
                horizontalalignment='left',
                rotation=(360 - 25))

    # Enhancing the plot
    pl1t.xlabel('Index')
    plt.ylabel('Cumulative Sum Percentage')
    plt.title('Pareto Distribution')
    plt.grid(True)
    plt.legend()
    
    return plt

def analog_count(dataframe, column, simple = True, normalize = False, plot = False):
    """This function returns a dataframe with the counts of the values in a column.
        IF simple = False, it also returns the cumulative counts and the cumulative percentage.
        IF normalize = True, it returns the percentage of the counts.

    Args:
        dataframe (pd.DataFrame): a dataframe containing the column.
        column (str): the name of the column
        simple (bool, optional): defining if it is a simple vc or with cumulative sums and percentages. Defaults to True.
        normalize (bool, optional): with normalised values. Defaults to False.

    Returns:
        _type_: _description_
    """
    y = dataframe[column].value_counts(normalize = normalize).rename_axis(column).reset_index(name='counts')
    
    if simple != True:
        y['h_counts'] = y['counts'].cumsum()
        y['g_counts'] = y['h_counts'] / y['counts'].sum()
    
    try:    
        if plot and simple :
            if simple == True:
                y['h_counts'] = y['counts'].cumsum()
                y['g_counts'] = y['h_counts'] / y['counts'].sum()
            
            my_plot = pareto_distribution(y)
            my_plot.show()                


    except Exception as e:
        print(e)
        return y
    return y

def calculate_column_overlap(df_a, df_b):
    """
    Calculate the percentage overlap between each pair of columns from two DataFrames based on unique values.

    Args:
    df_a (pd.DataFrame): The first DataFrame.
    df_b (pd.DataFrame): The second DataFrame.

    Returns:
    pd.DataFrame: A DataFrame in long format showing the overlap percentage between columns of df_a and df_b.
    """
    # Create a DataFrame to store the overlap data
    data_overlap = pd.DataFrame(index=df_a.columns, columns=df_b.columns)

    # Iterate over each column pair and calculate overlap
    for col_a in data_overlap.index:
        for col_b in data_overlap.columns:
            unique_value_column_a = set(df_a[col_a].unique())
            unique_value_column_b = set(df_b[col_b].unique())

            # Calculate the intersection and percentage overlap
            intersection = len(unique_value_column_a.intersection(unique_value_column_b))
            length = len(df_a)
            data_overlap.loc[col_a, col_b] = round((intersection / length) * 100, 2)

    # Reshape the data_overlap DataFrame to a long format
    data_overlap_long = data_overlap.stack().reset_index()
    data_overlap_long.columns = ['column_a', 'column_b', 'overlap']

    # Sort by overlap and reset the index
    data_overlap_long.sort_values('overlap', ascending=False, inplace=True)
    data_overlap_long.reset_index(drop=True, inplace=True)

    return data_overlap_long