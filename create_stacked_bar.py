import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import io

# --- Helper functions (Unchanged) ---
def _format_value(v):
    if v > 1000:
        return f'{v/1000:.1f}K'
    elif v > 0:
        return f'{v:.1f}'
    return ''

def _get_text_color_for_bg(bg_color):
    luminance = (0.299 * bg_color[0] + 0.587 * bg_color[1] + 0.114 * bg_color[2])
    return 'white' if luminance < 0.5 else 'black'


def _add_labels_to_stacked_bar(ax: Axes, horizontal: bool, threshold_percentage: float = 5.0):
    """
    Adds value labels to a stacked bar chart, handling orientation and avoiding clutter.

    This function iterates through each bar segment, adding labels only to those that
    exceed a size threshold. It works for both vertical and horizontal charts.

    Args:
        ax (matplotlib.axes.Axes): The axes object containing the chart.
        horizontal (bool): The orientation of the bar chart. True for horizontal, False for vertical.
        threshold_percentage (float): The minimum size a segment must be (as a percentage of
                                      the total bar) to receive a label.
    """
    # --- 1. Calculate Totals ---
    # This list will hold the total size (width or height) of each full stacked bar.
    totals = []
    # Define a function to get the correct dimension (width or height) based on orientation.
    get_size = (lambda bar: bar.get_width()) if horizontal else (lambda bar: bar.get_height())

    for container in ax.containers:
        bar_sizes = [get_size(bar) for bar in container]
        if not totals:
            totals = bar_sizes
        else:
            # Add the sizes of the current layer to the running totals.
            totals = [sum(x) for x in zip(totals, bar_sizes)]

    max_overall_total = max(totals) if totals else 0
    # --- 2. Add Segment and Total Labels ---
    # This tracks the bottom/left edge of the next segment to be drawn.
    offsets = np.zeros(len(totals))
    
    

    for container in ax.containers:
        # Get the sizes of segments in the current layer.
        bar_sizes = np.array([get_size(bar) for bar in container])

        for i, bar in enumerate(container):
            # --- Add Individual Segment Label ---
            segment_size = get_size(bar)
            total_bar_size = totals[i]

            # Only add a label if the total is > 0 and the segment meets the threshold.
            if total_bar_size > 0 and (segment_size / max_overall_total * 100) > threshold_percentage:
                # Determine the label's position (center of the segment).
                if horizontal:
                    x_pos = offsets[i] + segment_size / 2
                    y_pos = bar.get_y() + bar.get_height() / 2
                else: # Vertical
                    x_pos = bar.get_x() + bar.get_width() / 2
                    y_pos = offsets[i] + segment_size / 2

                # Get the contrasting text color for the segment's background.
                text_color = _get_text_color_for_bg(bar.get_facecolor())

                # Place the label using annotate for full control.
                ax.annotate(
                    _format_value(segment_size),
                    xy=(x_pos, y_pos),
                    ha='center', va='center',
                    color=text_color,
                    fontsize=9, fontweight='bold'
                )
        # Update the offsets for the next layer of segments.
        offsets += bar_sizes

    # --- 3. Add Total Labels at the End of Each Bar ---
    for i, total in enumerate(totals):
        if total > 0:
            # Get the last bar in the stack to determine positioning.
            bar = ax.containers[-1][i]
            if horizontal:
                xy = (total, bar.get_y() + bar.get_height() / 2)
                xytext = (5, 0) # 5 points horizontal offset
                ha, va = 'left', 'center'
            else: # Vertical
                xy = (bar.get_x() + bar.get_width() / 2, total)
                xytext = (0, 5) # 5 points vertical offset
                ha, va = 'center', 'bottom'

            ax.annotate(
                _format_value(total),
                xy=xy,
                xytext=xytext,
                textcoords='offset points',
                ha=ha, va=va,
                fontsize=10, fontweight='bold'
            )


def create_stacked_bar(
    ax: Axes,
    working_dataframe: pd.DataFrame,
    x_column: str,
    y_columns: list = None,
    color: dict | list = None,
    debug: bool = False,
    horizontal: bool = True, # Added parameter for orientation
    show_values: bool = False,
) -> Axes:
    """
    Creates a general-purpose horizontal or vertical stacked bar chart.

    Args:
        ax (matplotlib.axes.Axes): The axes object to draw on.
        working_dataframe (pd.DataFrame): The DataFrame with data.
        x_column (str): The column for bar labels (x-axis for vertical, y-axis for horizontal).
        y_columns (list, optional): Columns to stack. Inferred if None.
        color (dict or list, optional): Color mapping.
        debug (bool, optional): Enables debug prints.
        horizontal (bool, optional): If True, creates a horizontal chart. Defaults to True.
        show_values (bool, optional): If True, adds value labels. Defaults to False.

    Returns:
        matplotlib.axes.Axes: The modified axes object.
    """
    if y_columns is None:
        numeric_cols = working_dataframe.select_dtypes(include=np.number).columns.tolist()
        if x_column in numeric_cols:
            numeric_cols.remove(x_column)
        y_columns = numeric_cols
        if debug: print(f"Inferred y_columns for stacking: {y_columns}")

    if not y_columns:
        raise ValueError("Could not determine columns for stacking.")

    color_map = {}
    if isinstance(color, dict):
        color_map = color
    elif isinstance(color, list):
        color_map = {col: color[i % len(color)] for i, col in enumerate(y_columns)}
    else:
        color_map = {col: plt.cm.viridis(i/len(y_columns)) for i, col in enumerate(y_columns)}
        if debug: print("Using default color mapping.")

    # Use 'bar' for vertical and 'barh' for horizontal
    bar_func = ax.barh if horizontal else ax.bar
    # The offset is 'left' for horizontal and 'bottom' for vertical
    offset_kwarg = 'left' if horizontal else 'bottom'
    offset = np.zeros(len(working_dataframe))

    # Determine the arguments for the bar function based on orientation
    x_data = working_dataframe[x_column]
    
    for column in y_columns:
        bar_color = color_map.get(column)
        
        if horizontal:
            bar_func(x_data, working_dataframe[column], color=bar_color, height=0.6, label=column, **{offset_kwarg: offset})
        else: # Vertical
            bar_func(x_data, working_dataframe[column], color=bar_color, width=0.6, label=column, **{offset_kwarg: offset})
            
        offset += working_dataframe[column].values

    # --- Integration of the revised labeling feature ---
    if show_values:
        _add_labels_to_stacked_bar(ax, horizontal=horizontal, threshold_percentage=5)

    return ax
