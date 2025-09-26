import pandas as pd
import os

def get_folder_sizes(root_folder):
    folder_sizes = {}

    # Get only immediate subdirectories (not files)
    for item in os.listdir(root_folder):
        item_path = os.path.join(root_folder, item)
        if os.path.isdir(item_path):
            dir_size = 0
            for dirpath, dirnames, filenames in os.walk(item_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        dir_size += os.path.getsize(filepath)
                    except (OSError, PermissionError):
                        continue  # Skip inaccessible files
            folder_sizes[item_path] = dir_size

    return folder_sizes

def create_dataframe(folder_sizes):
    df = pd.DataFrame({
        "path": list(folder_sizes.keys()),
        "size (GB)": [size / (1024 ** 3) for size in folder_sizes.values()]
    })
    df["size (GB)"] = df["size (GB)"].round(2)  # Round to 2 decimal places
    df.sort_values(by="size (GB)", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    # now lets get the cummulative size
    df["cum (size)"] = df["size (GB)"].cumsum().round(2)
    # and the percentage of total size
    df['percentage(size)'] = (df["size (GB)"] / df["size (GB)"].sum() * 100).round(2)
    # and the cumulative percentage of total size
    df['cum percentage (size)'] = (df['cum (size)'] / df["size (GB)"].sum() * 100).round(2)
    df["basename"] = df["path"].apply(os.path.basename)
    return df

def get_filesize_dataframe(folder_path):
    folder_path = folder_path.strip()
    if not os.path.isdir(folder_path):
        raise ValueError("The provided path is not a valid directory.")
    folder_sizes = get_folder_sizes(folder_path)
    df = create_dataframe(folder_sizes)
    df.sort_values(by="size (GB)", ascending=False, inplace=True)
    return df
