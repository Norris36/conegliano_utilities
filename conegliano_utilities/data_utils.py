import pandas as pd


def get_columns(path: str) -> str:
    """
    Extract column names from all sheets in an Excel file or CSV file.
    
    Args:
        path (str): File path to the Excel/CSV file to be analyzed
    
    Returns:
        str: A semicolon-separated string containing sheet names and their columns,
             or an error message if the file couldn't be read
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


def humanise_df(local_df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a DataFrame and returns it with humanized column names.
    Removes underscores and applies title case formatting.
    
    Args:
        local_df (pd.DataFrame): Input DataFrame to humanize
        
    Returns:
        pd.DataFrame: DataFrame with humanized column names
    """
    # Create a copy to avoid modifying the original
    df_copy = local_df.copy()
    
    for col in df_copy.columns.tolist():
        # Replace underscores and hyphens with spaces
        new_col = col.replace('_', ' ').replace('-', ' ')
        
        # Split into words and apply title case to first word, lowercase to rest
        words = new_col.split(' ')
        formatted_words = []
        
        for i, word in enumerate(words):
            if i == 0:
                formatted_words.append(word.title())  # First word title case
            else:
                formatted_words.append(word.lower())  # Other words lowercase
        
        # Join words back together
        new_col = ' '.join(formatted_words)
        
        # Rename the column
        df_copy.rename(columns={col: new_col}, inplace=True)
    
    return df_copy


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renames DataFrame columns to a standardized format.
    
    Rules:
    - 'Name' or 'name' columns become 'name_'
    - Other columns: remove double spaces, replace spaces with underscores, lowercase
    
    Args:
        df (pd.DataFrame): The DataFrame whose columns are to be renamed.

    Returns:
        pd.DataFrame: The DataFrame with renamed columns.
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
