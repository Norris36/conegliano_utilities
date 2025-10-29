from __future__ import annotations              # modern typing (<3.10 support)
from __future__ import annotations

from typing import List, Optional, Union
# STANDARD LIB
import os
import pathlib
from pathlib import Path
import pandas as pd
import numpy as np
from tqdm import tqdm
import difflib                               # fuzzy string matching (nice error msgs)
import colorsys                              # HSL color space conversions

# THIRD-PARTY
import matplotlib as mpl # main plotting lib
import matplotlib.pyplot as plt                 # main plotting lib
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle
import matplotlib.font_manager as fm
from matplotlib.axes import Axes                # explicit type hints
from matplotlib.lines import Line2D             # identify line-plots
from matplotlib.patches import Rectangle, Wedge # identify bar / pie
from matplotlib.collections import PathCollection

"""
visualising.py
==============

Central styling helper used by every plotting routine in the project.

Public API
----------
get_color_palette(palette_name: str, /) -> dict[str, str]
setup_plot(*, color: str = "default", figsize: tuple[int, int] = (12, 6))
"""


# ────────────────────────────────────────────────────────────────
# 1. CORPORATE COLOUR PALETTES (four in total)
# ────────────────────────────────────────────────────────────────
# NOTE:
# • Every palette keeps the brand's "Primary" orange (#F57600).  
# • Extra keys "Accent" and "Grid" are provided so downstream code can
#   style markers, annotations, or grid-lines consistently.

# Define the colour palettes once at module import time
_PALETTES: dict[str, dict[str, str]] = {
    # 1) Default (light background, dark text)
    "default": {
        "Primary":    "#F57600",
        "Secondary":  "#253746",
        "TertiaryA":  "#d3cec9",
        "Background": "#f0efed",
        "Accent":     "#0072F5",   # blue for highlights
        "Grid":       "#d6d6d6"
    },
    # 2) Dark-mode (dark background, light text)
    "dark mode": {
        "Primary":    "#F57600",
        "Secondary":  "#B6ADA5",
        "TertiaryA":  "#7c8790",
        "Background": "#253746",
        "Accent":     "#40C4FF",
        "Grid":       "#555555"
    },
    # 3) Alternative (brand orange on subtle grey background)
    "alternative": {
        "Primary":    "#F57600",
        "Secondary":  "#253746",
        "TertiaryA":  "#d3cec9",
        "Background": "#d3cec9",
        "Accent":     "#C2185B",   # magenta
        "Grid":       "#b3b3b3"
    },
    # 4) Greyscale (for print-outs, still carries brand orange)
    "greyscale": {
        "Primary":    "#F57600",
        "Secondary":  "#404040",
        "TertiaryA":  "#808080",
        "Background": "#F5F5F5",
        "Accent":     "#BDBDBD",
        "Grid":       "#B0B0B0"
    },
    "steelseries_1":{
        'Primary':    '#fc4c02',  # orange
        'Secondary':  '#007ec8',  # brand-blue
        'TertiaryA':  '#a5a7aa',  # mid-grey
        'Background': '#e6e6e6',  # off-white
        'Accent':     '#ffbe00',  # brand-yellow
        'Grid':       '#c8c8c8'   # light grey
    },
    "steelseries_darkmode": {
        'Primary':    '#0f0d0e',  # off-black
        'Secondary':  '#462b7c',  # brand-dark-purple
        'TertiaryA':  '#313131',  # dark grey
        'Background': '#212121',  # darkest grey
        'Accent':     '#41a930',  # brand-green
        'Grid':       '#262626'   # darker grey
    },
    "steelseries_alternative": {
        'Primary':    '#754bd3',  # brand-purple
        'Secondary':  '#41a930',  # brand-green
        'TertiaryA':  '#c8c8c8',  # lightest grey
        'Background': '#e6e6e6',  # off-white
        'Accent':     '#fc4c02',  # orange
        'Grid':       '#a5a7aa'   # grey
    }
}

# ────────────────────────────────────────────────────────────────
# 2. GLOBAL DEFAULTS FOR FIGURE SIZE AND FONTS
# ────────────────────────────────────────────────────────────────
# These global variables control the default size and font settings
# for all plots created with setup_plot() and setup_subplots().
# Use the getter/setter functions below to customize these values.

_GLOBAL_FIGSIZE: tuple[int, int] = (12, 6)
_GLOBAL_FONT_SIZE_BODY: int = 12
_GLOBAL_FONT_SIZE_HEADER: int = 16

# ────────────────────────────────────────────────────────────────
# GETTERS - Retrieve current global settings
# ────────────────────────────────────────────────────────────────

def get_global_figsize() -> tuple[int, int]:
    """
    Get the current global default figure size.

    Returns:
        tuple[int, int]: Figure size as (width, height) in inches.
    """
    return _GLOBAL_FIGSIZE

def get_global_font_size_body() -> int:
    """
    Get the current global default body font size.

    Returns:
        int: Font size in points for body text (labels, ticks, annotations).
    """
    return _GLOBAL_FONT_SIZE_BODY

def get_global_font_size_header() -> int:
    """
    Get the current global default header font size.

    Returns:
        int: Font size in points for headers (titles, legend titles).
    """
    return _GLOBAL_FONT_SIZE_HEADER

# ────────────────────────────────────────────────────────────────
# SETTERS - Update global settings
# ────────────────────────────────────────────────────────────────

def set_global_figsize(width: int, height: int) -> None:
    """
    Set the global default figure size for all future plots.

    Args:
        width (int): Figure width in inches.
        height (int): Figure height in inches.

    Example:
        >>> set_global_figsize(16, 10)  # All plots will now be 16x10 by default
    """
    global _GLOBAL_FIGSIZE
    _GLOBAL_FIGSIZE = (width, height)

def set_global_font_size_body(size: int) -> None:
    """
    Set the global default body font size for all future plots.

    Args:
        size (int): Font size in points for body text.

    Example:
        >>> set_global_font_size_body(14)  # All body text will be 14pt
    """
    global _GLOBAL_FONT_SIZE_BODY
    _GLOBAL_FONT_SIZE_BODY = size

def set_global_font_size_header(size: int) -> None:
    """
    Set the global default header font size for all future plots.

    Args:
        size (int): Font size in points for headers.

    Example:
        >>> set_global_font_size_header(18)  # All headers will be 18pt
    """
    global _GLOBAL_FONT_SIZE_HEADER
    _GLOBAL_FONT_SIZE_HEADER = size

def set_global_plot_defaults(figsize: tuple[int, int] = None,
                             font_size_body: int = None,
                             font_size_header: int = None) -> None:
    """
    Convenience function to set multiple global plot defaults at once.

    Args:
        figsize (tuple[int, int], optional): Figure size as (width, height).
        font_size_body (int, optional): Body font size in points.
        font_size_header (int, optional): Header font size in points.

    Example:
        >>> set_global_plot_defaults(figsize=(16, 10), font_size_body=14, font_size_header=18)
        >>> # OR set just one parameter
        >>> set_global_plot_defaults(font_size_body=16)
    """
    if figsize is not None:
        set_global_figsize(figsize[0], figsize[1])
    if font_size_body is not None:
        set_global_font_size_body(font_size_body)
    if font_size_header is not None:
        set_global_font_size_header(font_size_header)

def get_global_plot_defaults() -> dict:
    """
    Get all current global plot defaults as a dictionary.

    Returns:
        dict: Dictionary containing 'figsize', 'font_size_body', 'font_size_header'.

    Example:
        >>> defaults = get_global_plot_defaults()
        >>> print(defaults)
        {'figsize': (12, 6), 'font_size_body': 12, 'font_size_header': 16}
    """
    return {
        'figsize': _GLOBAL_FIGSIZE,
        'font_size_body': _GLOBAL_FONT_SIZE_BODY,
        'font_size_header': _GLOBAL_FONT_SIZE_HEADER
    }

# ────────────────────────────────────────────────────────────────
# COLOR PALETTE FUNCTIONS
# ────────────────────────────────────────────────────────────────

def get_color_palette(palette_name: str = "default", /) -> dict[str, str]:
    """
    One-line description
        Return the company colour palette that best matches *palette_name*.

    Summary
        • Accepts names in any case and tolerates minor typos or
          underscore/space differences (e.g., "DarkMode", "dark_mode",
          "Dark  mode" all resolve to "dark mode").
        • Provides a clear, actionable error message if it cannot find
          a sufficiently close match.

    Args
    ----
    palette_name : str
        The user-provided palette identifier.

    Returns
    -------
    dict[str, str]
        Mapping of semantic colour names to HEX strings.

    Raises
    ------
    ValueError
        If the name is unrecognised and no close suggestion exists.
    """
    # ------------------------------------------------------------
    # Normalise user input: lower-case, collapse spaces/underscores
    # ------------------------------------------------------------
    raw_input = palette_name                       # preserve original for msgs
    pname = palette_name.strip().lower().replace("_", " ")

    # Direct hit?  Early-out for speed.
    if pname in _PALETTES:
        return _PALETTES[pname]

    # ------------------------------------------------------------
    # Fuzzy matching: suggest the closest palette if similarity ≥ 0.6
    # ------------------------------------------------------------
    close = difflib.get_close_matches(pname, _PALETTES.keys(), n=1, cutoff=0.6)
    if close:
        suggestion = close[0]
        raise ValueError(
            f"Palette '{raw_input}' not found. Did you mean '{suggestion}'?"
        )
    else:
        # Build human-readable list of valid names
        valid = ", ".join(sorted(_PALETTES.keys()))
        raise ValueError(
            f"Palette '{raw_input}' is unknown. Valid options are: {valid}"
        )

def get_figsize(name = 'default'):
    sizes = {
        'default': (12, 8),
        'small': (8, 6),
        'large': (16, 10),
        'PP_Vertical_Half': (12,10),
        'PP_Focus': (12.93, 31.22),
        'PP_Full': (19.05, 33.87)
    }
    if name not in sizes.keys():
        raise ValueError(f"Unknown figure size '{name}'. Available sizes: {list(sizes.keys())}")
    return sizes.get(name, sizes['default'])

def set_fontsizes(fig, ax, font_size_body=None, font_size_header=None):
    """
    Uniformly set two different font sizes on an existing Matplotlib
    figure/axes pair.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
    ax  : matplotlib.axes.Axes     (any axes object that lives in *fig*)
    font_size_body   : int | float, optional
        Size in points for tick labels, axis labels, annotation texts, etc.
        If None, uses the global default set by set_global_font_size_body().
    font_size_header : int | float, optional
        Size in points for figure title, axes titles, legend titles.
        If None, uses the global default set by set_global_font_size_header().

    Returns
    -------
    (fig, ax) : the same objects for convenient chaining.
    """
    # Use global defaults if not specified
    if font_size_body is None:
        font_size_body = _GLOBAL_FONT_SIZE_BODY
    if font_size_header is None:
        font_size_header = _GLOBAL_FONT_SIZE_HEADER

    # ------------------------------------------------------------------
    # 1)  Update the defaults so any *future* text will inherit new sizes
    # ------------------------------------------------------------------
    mpl.rcParams.update({'font.size'      : font_size_body,
                         'axes.titlesize' : font_size_header,
                         'figure.titlesize': font_size_header})

    # ------------------------------------------------------------------
    # 2)  Body text: every Text object except titles & legend titles
    # ------------------------------------------------------------------
    for text in fig.findobj(mpl.text.Text):
        text.set_fontsize(font_size_body)

    # ------------------------------------------------------------------
    # 3)  Promote headers
    # ------------------------------------------------------------------
    # Figure title (suptitle)
    if fig._suptitle is not None:
        fig._suptitle.set_fontsize(font_size_header)

    # Each axes that lives in this figure
    for axes in fig.get_axes():
        # Axes title
        axes.title.set_fontsize(font_size_header)

        # Axis labels (body size)
        axes.xaxis.label.set_size(font_size_body)
        axes.yaxis.label.set_size(font_size_body)

        # Tick labels
        axes.tick_params(axis='both', which='major', labelsize=font_size_body)
        axes.tick_params(axis='both', which='minor', labelsize=font_size_body * 0.8)

        # Legend (if any)
        leg = axes.get_legend()
        if leg:
            leg.get_title().set_fontsize(font_size_header)
            for txt in leg.get_texts():
                txt.set_fontsize(font_size_body)

    return fig, ax

import urllib.request
from pathlib import Path
import tempfile
from urllib.error import URLError

def get_github_otf_path() -> Path:
    """
    Downloads a .otf font from a raw GitHub URL to a local temporary file
    and returns its path.

    This function is designed to be efficient by checking if the file already
    exists in the temporary directory. If it does, it skips the download.

    Returns
    -------
    pathlib.Path
        The local file path to the downloaded .otf font.

    Raises
    ------
    FileNotFoundError
        If the font file cannot be downloaded from the URL.
    """
    # The specific raw GitHub URL for the font file.
    FONT_URL = "https://github.com/Norris36/conegliano_utilities/raw/864e308854b8b706bad7340abafeca04a89c4c1f/data/GNElliot-Regular.otf"
    
    # Define a path for the font in the system's temporary directory.
    # This avoids cluttering the user's project directory.
    font_filename = Path(FONT_URL).name
    font_path = Path(tempfile.gettempdir()) / font_filename

    # --- Caching Logic ---
    # If the font file already exists, return the path immediately.
    if font_path.exists():
        # This print statement is optional but helpful for debugging.
        # print(f"Font '{font_filename}' already exists locally.")
        return font_path

    # --- Download Logic ---
    # If the file doesn't exist, download it.
    print(f"Downloading font '{font_filename}' to '{font_path}'...")
    try:
        # Make the request to the URL.
        with urllib.request.urlopen(FONT_URL) as response:
            # Check if the request was successful.
            if response.status != 200:
                raise FileNotFoundError(
                    f"Failed to download font. HTTP Status: {response.status}"
                )
            
            # Write the content of the response to the local file in binary mode.
            with open(font_path, 'wb') as f:
                f.write(response.read())

    except URLError as e:
        # Handle network errors (e.g., no internet connection).
        raise FileNotFoundError(
            f"Failed to download font from '{FONT_URL}'. "
            f"Please check your internet connection. Error: {e}"
        ) from e

    return font_path

def _apply_style(fig, ax, colors: dict[str, str]) -> None:
    """
    Apply corporate styling to *ax*.

    Parameters
    ----------
    fig, ax           : matplotlib Figure & Axes to style.
    colors            : dict returned by `get_color_palette`.
    """
    # ------------------------------------------------------------
    # 1. Load corporate font (once per interpreter session)
    # ------------------------------------------------------------
    otf_file_path = get_github_otf_path()
    font_properties = fm.FontProperties(fname=str(otf_file_path))
    # Register font globally with Matplotlib (no-op if already added)
    fm.fontManager.addfont(str(otf_file_path))
    # -------- background & grid ---------------------------------
    fig.patch.set_facecolor(colors["Background"])
    ax.set_facecolor(colors["Background"])

    # Draw grid lines using palette's "Grid" colour
    # ax.grid(True, color=colors["Grid"], linewidth=0.5, alpha=0.7)

    # -------- tick / label / title styling ----------------------
    ax.tick_params(colors=colors["Secondary"])
    for spine in ax.spines.values():
        spine.set_color(colors["Secondary"])

    # Label & title fonts
    ax.title.set_color(colors["Secondary"])
    ax.xaxis.label.set_color(colors["Secondary"])
    ax.yaxis.label.set_color(colors["Secondary"])

    # -------- figure-wide font ----------------------------------
    plt.rcParams["font.family"] = font_properties.get_name()

def setup_plot(*, color: str = "default", figsize: tuple[int, int] = None):
    """
    One-line description
        Create a single (fig, ax) pair pre-styled with the company theme.

    Summary
        * Loads the corporate font (once) from the `resources/fonts`
          directory. The font file is expected to be named
          'CorporateSans.otf'.
        * Retrieves the requested colour palette via `get_color_palette`.
        * Applies background, grid, and text colours uniformly.
        * Returns the freshly created Figure and Axes objects.

    Args
    ----
    color   : str
        Palette name.  Case-insensitive, minor typos allowed.
    figsize : tuple[int, int], optional
        Size in inches, forwarded to `plt.subplots`.
        If None, uses the global default set by set_global_figsize().

    Returns
    -------
    fig, ax : matplotlib.figure.Figure, matplotlib.axes.Axes
        The newly created figure & axes ready for plotting.
    """
    # ------------------------------------------------------------
    # 1. Use global figsize if not specified
    # ------------------------------------------------------------
    if figsize is None:
        figsize = _GLOBAL_FIGSIZE

    # ------------------------------------------------------------
    # 2. Retrieve colour palette (handles user typos)
    # ------------------------------------------------------------
    colors = get_color_palette(color)

    # ------------------------------------------------------------
    # 3. Create figure & axes, then apply style
    # ------------------------------------------------------------
    fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)
    _apply_style(fig, ax, colors)

    # ------------------------------------------------------------
    # 4. Apply global font sizes
    # ------------------------------------------------------------
    set_fontsizes(fig, ax)

    return fig, ax

def get_current_path():
    # oh it would be nice to get path for the folder i'm working in 
    return str(pathlib.Path().absolute())

def get_parent_dir(path):
    path = pathlib.Path(path)
    return str(path.parent)

def my_log(
    ax: Axes,
    axis: str = "x",
    extend_pct: Optional[float] = None
) -> Axes:
    """
    Put the chosen axis on a logarithmic scale **and** show numeric tick labels,
    with optional breathing room above the original max.

    One-line description
    --------------------
    Log-scale helper that hides scientific notation *and* guarantees the top
    original limit is always labelled.

    Summary
    -------
    1. Switch the requested axis to log scale.
    2. Optionally extend the upper data range by a percentage (default 5%).
       The lower limit stays at the original minimum.
    3. Build aesthetically pleasing tick positions based on the classic
       1-2-5 sequence, but **cap ticks at the original maximum**.
    4. Guarantee the *original* maximum value is part of the tick list.
    5. Apply the ticks and render them as plain integers.
    6. Hide minor tick labels to avoid visual clutter.

    Args
    ----
    ax         : matplotlib.axes.Axes
                 The axis object containing your chart.
    axis       : str, optional
                 Which axis to adjust – `"x"` (default) or `"y"`.
    extend_pct : float or None, optional
                 Fractional extension above the original max (e.g. 0.05 for 5%).
                 If None, defaults to 0.05. Lower bound is never extended.

    Returns
    -------
    matplotlib.axes.Axes
        The same axis object, now edited.
    """

    # 1) Decide which methods and limits to use
    default_pct = 0.05
    pct = default_pct if extend_pct is None else extend_pct

    axis = axis.lower()
    if axis == "x":
        ax.set_xscale("log")
        orig_low, orig_high = ax.get_xlim()
        new_high = orig_high * (1 + pct)
        ax.set_xlim(orig_low, new_high)
        tick_setter = ax.set_xticks
        label_setter = ax.set_xticklabels

    elif axis == "y":
        ax.set_yscale("log")
        orig_low, orig_high = ax.get_ylim()
        new_high = orig_high * (1 + pct)
        ax.set_ylim(orig_low, new_high)
        tick_setter = ax.set_yticks
        label_setter = ax.set_yticklabels

    else:
        raise ValueError("axis must be 'x' or 'y'")

    # 2) Build “nice” tick candidates (1-2-5 rule), capped at original max
    lim_low, lim_high = orig_low, new_high
    exp_min = int(np.floor(np.log10(lim_low)))
    exp_max = int(np.ceil (np.log10(lim_high)))

    candidate_ticks: List[float] = []
    upper_cap = orig_high

    for exp in range(exp_min, exp_max + 1):
        for mantissa in (1, 2, 5):
            tick_val = mantissa * (10 ** exp)
            if lim_low <= tick_val <= upper_cap:
                candidate_ticks.append(tick_val)

    # 3) Guarantee the *original* max is labelled
    if candidate_ticks:
        last = candidate_ticks[-1]
        if last < orig_high * 0.99:
            candidate_ticks.append(orig_high)
    else:
        # If no tick at all, just use the original max
        candidate_ticks.append(orig_high)

    # 4) Apply tick positions and plain-number labels
    tick_setter(candidate_ticks)
    label_setter([f"{int(t):,}" for t in candidate_ticks])

    # 5) Hide minor tick labels
    if axis == "x":
        ax.xaxis.set_minor_formatter(mticker.NullFormatter())
    else:
        ax.yaxis.set_minor_formatter(mticker.NullFormatter())

    return ax

###
###
### FONT PATHS
###

def get_otf_path():
    """
    Returns the path to the GNElliot-Regular.otf font file.
    """
    # Static variable to store the font path
    if not hasattr(get_otf_path, "font_path"):
        # Now lets get the current path
        current_path = get_current_path()
        # Now lets get the parent directory
        parent_dir = get_parent_dir(current_path)
        # Now lets apply the hygin function to get the path to the font file
        lookup = 'GNElliot-Regular.otf'
        font_path = hygin(parent_dir, lookup)
        if isinstance(font_path, list):
            for item in font_path:
                if item.endswith(lookup):
                    get_otf_path.font_path = item
                    break
        else:
            get_otf_path.font_path = font_path
    
    return get_otf_path.font_path

def smart_text_labels(ax,
                      x, y, labels,
                      *,
                      fontsize=9,
                      rotation=30,
                      ha='left', va='bottom',
                      min_sep=20,
                      offset_px=5,
                      max_iter=50,
                      **text_kwargs):
    """
    Annotate points while automatically nudging overlapping labels.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
    x, y : 1-D sequences (same length)
        Coordinates of the points.
    labels : 1-D sequence (same length)
        Text to display at each point.
    fontsize, rotation, ha, va : text properties (forwarded to ax.text)
    min_sep : int
        Minimum pixel distance allowed between two label centres.
    offset_px : int
        Vertical pixel offset applied each time an overlap is detected.
    max_iter : int
        Maximum iterations per label before giving up.
    text_kwargs : dict
        Any extra arguments accepted by `ax.text`.

    Returns
    -------
    list[matplotlib.text.Text]
        The created Text objects (in insertion order).
    """
    tr      = ax.transData            # data ➜ pixels
    tr_inv  = ax.transData.inverted() # pixels ➜ data
    placed  = []                      # store pixel coords of existing labels
    texts   = []

    for xi, yi, lab in zip(x, y, labels):
        # Start at the data point itself (in pixel space)
        x_pix, y_pix = tr.transform((xi, yi))

        for _ in range(max_iter):
            # Test against centres of already-placed labels
            if all(((x_pix - xp)**2 + (y_pix - yp)**2)**0.5 >= min_sep
                   for xp, yp in placed):
                break  # no overlap -> good spot
            y_pix += offset_px        # push up and retry

        # Back to data space
        x_dat, y_dat = tr_inv.transform((x_pix, y_pix))
        txt = ax.text(x_dat, y_dat, lab,
                      fontsize=fontsize, rotation=rotation,
                      ha=ha, va=va, **text_kwargs)
        texts.append(txt)
        placed.append((x_pix, y_pix))

    return texts

###
### Colors
###

def generate_shades(hex_color: str, num_shades: int = 5) -> list[str]:
    """
    Generates a list of darker shades for a given hex color.

    This function converts a hex color string into the HSL (Hue, Lightness, Saturation)
    color space. It then creates a series of new colors by decreasing the "Lightness"
    value, effectively producing darker shades of the original color. These new HSL
    colors are then converted back to hex format.

    Args:
        hex_color (str): The base color in hex format (e.g., '#3498db' or '3498db').
        num_shades (int): The number of darker shades to generate. Defaults to 5.

    Returns:
        list[str]: A list of hex color strings representing the shades, from darkest to lightest (the original color).
    """
    # Line 1: Remove the '#' prefix from the hex string if it exists.
    # The lstrip('#') method removes any leading '#' characters.
    clean_hex = hex_color.lstrip('#')

    # Line 2: Convert the 6-character hex string into three separate integer values for Red, Green, and Blue.
    # We parse the string in chunks of 2 characters (e.g., '34', '98', 'db') and convert each
    # hexadecimal chunk to its corresponding integer value (0-255).
    rgb = tuple(int(clean_hex[i:i+2], 16) for i in (0, 2, 4))

    # Line 3: Convert the RGB tuple (e.g., (52, 152, 219)) to the HLS (Hue, Lightness, Saturation) color space.
    # The colorsys library requires RGB values to be normalized to a 0-1 scale, so we divide each by 255.
    # Mathematics: HLS is a cylindrical representation of colors. 'Lightness' is the central axis,
    # from black (0) to white (1). By changing only Lightness, we create shades and tints without altering the base color (Hue).
    h, l, s = colorsys.rgb_to_hls(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)

    # Line 4: Generate a list to store the resulting hex codes for the shades.
    shades_hex = []

    # Line 5: Create an array of evenly spaced "Lightness" values.
    # We use numpy's linspace to create `num_shades` values starting from a dark value (l * 0.2) up to the original lightness (l).
    # This creates the steps for our gradient of shades.
    lightness_steps = np.linspace(l * 0.2, l, num_shades)

    # Line 6: Loop through each of the new lightness values to create the corresponding shade.
    for step in lightness_steps:
        # Line 7: Convert the HLS color (with the new, modified lightness) back to an RGB tuple.
        # The hue (h) and saturation (s) remain constant to preserve the original color's character.
        new_rgb_normalized = colorsys.hls_to_rgb(h, step, s)

        # Line 8: Convert the normalized RGB values (0-1) back to the standard 0-255 scale.
        # We multiply by 255 and round to the nearest integer.
        new_rgb = tuple(int(c * 255) for c in new_rgb_normalized)

        # Line 9: Format the RGB tuple back into a hex string.
        # The format specifier '{:02x}' ensures each R, G, B value is a two-digit lowercase hex number (e.g., 10 becomes '0a').
        # We then join them and prepend with a '#' to form the final hex code.
        hex_code = f"#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}"

        # Line 10: Add the newly generated hex code to our list of shades.
        shades_hex.append(hex_code)

    # Line 11: Return the complete list of shades.
    return shades_hex


def highlight_values(dataframe, column, command, amount):        
    """
    Highlights the specified number of top or bottom values in a dataframe column.

    Parameters:
    dataframe (pandas.DataFrame): The dataframe to be modified.
    column (str): The column name in the dataframe.
    command (str): The command to determine whether to highlight 'max' or 'min' values.
    amount (int): The number of values to highlight.

    Returns:
    pandas.DataFrame: The modified dataframe with highlighted values.
    """
    # Define your company colors
    color_palette = get_color_palette('default')
    
    # Initialize the 'color' column with default color
    dataframe['color'] = color_palette['TertiaryA']
    
    # Find the indices for the max or min values
    if command == 'max':
        indices = dataframe[column].nlargest(amount).index
    elif command == 'min':    
        indices = dataframe[column].nsmallest(amount).index

    # Apply the primary color to the specified number of top or bottom values
    dataframe.loc[indices, 'color'] = color_palette['Primary']

    return dataframe

def highlight_blue_values(dataframe, column, command, amount):
    """
    Highlights the specified number of top or bottom values in a DataFrame column with a blue color.

    Parameters:
    dataframe (pandas.DataFrame): The DataFrame to be modified.
    column (str): The column name in the DataFrame.
    command (str): The command to determine whether to highlight the 'max' or 'min' values.
    amount (int): The number of values to highlight.

    Returns:
    pandas.DataFrame: The modified DataFrame with highlighted values.
    """
    # Convert list to DataFrame

    filtered_df = dataframe[dataframe.color == '#d3cec9' ]
    
    # Define your company colors
    color_palette = get_color_palette(palette_name='default')
    
    # Initialize the 'color' column with default color
    # filtered_df['color'] = color_palette['TertiaryA']
    
    # Find the indices for the max or min values
    if command == 'max':
        indices = filtered_df[column].nlargest(amount).index
    elif command == 'min':    
        indices = filtered_df[column].nsmallest(amount).index

    # Apply the Secondary color to the specified number of top or bottom values
    dataframe.loc[indices, 'color'] = color_palette['Secondary']

    return dataframe
 
def get_primary_color():
    """
    Returns the primary color as a hexadecimal value.

    Returns:
        str: The primary color in hexadecimal format.
    """
    colors = get_color_palette(palette_name='default')
    return colors['Primary']

def get_secondary_color():
    """
    Returns the secondary color as a hexadecimal value.

    Returns:
        str: The secondary color in hexadecimal format.
    """
    colors = get_color_palette(palette_name='default')
    return colors['Secondary']

def get_base_color():
    """
    Returns the base color used in the statistics template.
    
    Returns:
        str: The base color in hexadecimal format.
    """
    colors = get_color_palette(palette_name='default')
    return colors['TertiaryA']

def convert_to_dark_mode(dataframe):
    """
    Converts the colors in the given dataframe to dark mode colors.
    
    Parameters:
        dataframe (pandas.DataFrame): The dataframe containing the colors to be converted.
        
    Returns:
        pandas.DataFrame: The dataframe with the colors converted to dark mode colors.
    """
    # now lets get the default color palette
    default = get_color_palette(palette_name='default')
    # now lets get the dark mode color palette
    dark_mode = get_color_palette(palette_name='dark mode')
    
    # now lets replace the default colors with the dark mode colors
    dataframe.loc[dataframe.color == default['Primary'], 'color'] = dark_mode['Primary']
    dataframe.loc[dataframe.color == default['Secondary'], 'color'] = dark_mode['Secondary']
    dataframe.loc[dataframe.color == default['TertiaryA'], 'color'] = dark_mode['TertiaryA']
    dataframe.loc[dataframe.color == default['Background'], 'color'] = dark_mode['Background']
    
    return dataframe

def color_pareto(working_dataframe, column = "delta_amount", color_palette = 'default'):
    """
    This function colors the DataFrame based on the Pareto principle.
    It assigns a color based on whether the row contributes to 80% of the total or not.
    """
    working_dataframe['colour'] = working_dataframe.apply(
        lambda row: get_color_palette(color_palette)['Primary'] if row['pareto'] else get_color_palette(color_palette)['Secondary'], axis=1
    )
    return working_dataframe

###
###
###

def pareto(working_dataframe, column = "delta_amount"):
    """
    This function calculates the Pareto principle (80/20 rule) for a given column in a DataFrame.
    It computes the percentage of each value in the column relative to the total sum of that column,
    sorts the DataFrame by this percentage in descending order, and then calculates the cumulative percentage.
    It also identifies which rows contribute to 80% of the total and marks them with a boolean column 'pareto'.
    """ 

    working_dataframe['my_working_percentage'] = working_dataframe[column] / working_dataframe[column].sum() * 100
    working_dataframe.sort_values(by='my_working_percentage', ascending=False, inplace=True)
    working_dataframe['my_cumulative_percentage'] = working_dataframe['my_working_percentage'].cumsum()
    working_dataframe['pareto'] = working_dataframe['my_cumulative_percentage'] <= 80

    working_dataframe.drop(columns=['my_working_percentage', 'my_cumulative_percentage'], inplace=True)

    return working_dataframe


###
### Pre made charts
###

def create_stacked_bar(ax, working_dataframe, color, x_column = 'top_manager', y_columns: list = []):
    """
    Creates a horizontal stacked bar chart showing composition breakdown for each item.
    
    This function takes a prepared DataFrame and creates a horizontal stacked bar chart
    where each bar represents an entity (e.g., manager) and the segments of each bar
    represent different categories (e.g., country types).
    
    Args:
        ax (matplotlib.axes.Axes): The matplotlib axes object to draw on
        working_dataframe (pd.DataFrame): DataFrame containing the data to plot
        color (dict): Dictionary mapping category names to color values
        x_column (str, optional): Name of column to use for bar labels. Defaults to 'top_manager'.
        y_columns (list, optional): List of column names for stacked segments. Defaults to 
                                    ['top', 'mid', 'low', 'satelite'].
    
    Returns:
        matplotlib.axes.Axes: The modified axes object with the stacked bar chart
    """
    # Check if y_columns is empty, if so, raise an error
    if not y_columns or len(y_columns) == 0:
        raise ValueError("y_columns must contain at least one column name for stacking.")
    
    # If color is not provided we need to create a default color mapping
    if not isinstance(color, dict):
        # Now lets print, "No color mapping provided, using default colors."
        print("No color mapping provided, using default colors.")
        # Now we need to check, if there is one in the dataframe
        if 'colour' in working_dataframe.columns or 'color' in working_dataframe.columns:
            # If there is a color column, we can use that
            color = working_dataframe['colour'].unique().tolist()
            if len(color) == 0:
                raise ValueError("No color mapping found in the DataFrame.")
        else:
            # If there is no color column, we can create a default color mapping
            color = {col: plt.cm.tab10(i) for i, col in enumerate(y_columns)}
            print("Using default color mapping:", color)
        # Now we need to create 
    # Initialize bottom as None for the first segment (no offset needed)
    bottom = None
    
    # Loop through each category column to create stacked segments
    for column in y_columns:
        if bottom is None:
            # For the first segment, create bars starting at position 0
            ax.barh(working_dataframe[x_column], 
                    working_dataframe[column], 
                    color=color[column], height=0.6, label=column)
            # Store these values as the bottom reference for the next segment
            bottom = working_dataframe[column]
        else:
            # For subsequent segments, start from the accumulated position
            ax.barh(working_dataframe[x_column],
                    working_dataframe[column], 
                    left=bottom, color=color[column], height=0.6, label=column)
            # Update the accumulated position by adding the current segment width
            bottom += working_dataframe[column]
            
    # Return the modified axes object
    return ax


def create_stacked_bar_chart(ax, working_dataframe: pd.DataFrame, primary_color: str = '#00447E', horizontal: bool = True, bar_width: float = 0.8):
    """
    Creates a versatile horizontal or vertical stacked bar chart from a DataFrame.

    This function automatically uses the first column for categories and all other
    numerical columns for stacked segments. It sorts the categories to ensure a logical
    order (e.g., chronological). It supports both horizontal and vertical orientations.

    Args:
        ax (matplotlib.axes.Axes): The axes object to draw the chart on.
        working_dataframe (pd.DataFrame): DataFrame where the first column is the category
                                          and subsequent columns are numerical values.
        primary_color (str, optional): Base hex color for the palette. Defaults to '#00447E'.
        horizontal (bool, optional): If True, creates a horizontal bar chart.
                                     If False, creates a vertical bar chart. Defaults to True.
        bar_width (float, optional): The width (or height for horizontal) of the bars.
                                     Defaults to 0.8.

    Returns:
        matplotlib.axes.Axes: The modified axes object with the chart.
    """
    # Line 1: Identify the category column (first column) and value columns (the rest).
    category_column = working_dataframe.columns[0]
    value_columns = working_dataframe.columns[1:]

    # Line 2: Sort the DataFrame by the category column to ensure a consistent, logical order.
    # For dates or numbers, this creates a chronological or numerical axis.
    df_sorted = working_dataframe.sort_values(by=category_column, ascending=True)

    # Line 3: Verify that there are value columns to plot.
    if len(value_columns) == 0:
        raise ValueError("DataFrame must have at least two columns: one for categories and one for values.")

    # Line 4: Generate a color palette from the primary color.
    colors = generate_shades(primary_color, num_shades=len(value_columns))
    color_map = {col: color for col, color in zip(value_columns, colors)}

    # Line 5: Get the sorted category labels for the axis.
    categories = df_sorted[category_column]

    # Line 6: Check the orientation and plot accordingly.
    if horizontal:
        # Line 7: For horizontal bars, initialize a `left` offset array to stack segments from left to right.
        left = np.zeros(len(df_sorted))
        # Line 8: Loop through each value column to plot its segment.
        for column in value_columns:
            values = df_sorted[column]
            # Line 9: Plot the horizontal bar segment. `left` determines its starting position.
            ax.barh(categories, values, left=left, color=color_map[column], height=bar_width, label=column)
            # Line 10: Update the `left` offset for the next segment.
            left += values.values
        # Line 11: Invert the y-axis so that categories (like dates) are ascending from bottom to top.
        ax.invert_yaxis()
    else:
        # Line 12: For vertical bars, initialize a `bottom` offset array to stack segments upwards.
        bottom = np.zeros(len(df_sorted))
        # Line 13: Loop through each value column to plot its segment.
        for column in value_columns:
            values = df_sorted[column]
            # Line 14: Plot the vertical bar segment. `bottom` determines its starting position.
            ax.bar(categories, values, bottom=bottom, color=color_map[column], width=bar_width, label=column)
            # Line 15: Update the `bottom` offset for the next segment.
            bottom += values.values

    # Line 16: Return the modified axes object.
    return ax


###
###
###


def setup_subplots(
    nrows: int = 1,
    ncols: int = 1,
    color: str = "default",
    sharex=False,
    sharey=False,
    figsize=None,
    **kwargs,):
    """
    Create a grid of subplots that already follow the corporate style.

    Parameters
    ----------
    nrows, ncols : int    – handed to `plt.subplots`
    color        : str    – palette name passed to `get_color_palette`
    sharex/sharey: bool   – forwarded to `plt.subplots`
    figsize      : tuple, optional  – inches, forwarded to `plt.subplots`
                   If None, uses the global default set by set_global_figsize().
    **kwargs             – any other kwarg accepted by `plt.subplots`

    Returns
    -------
    fig, axs     – same objects as `plt.subplots` would return
    """
    # Use global figsize if not specified
    if figsize is None:
        figsize = _GLOBAL_FIGSIZE

    colors = get_color_palette(palette_name=color)

    fig, axs = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        sharex=sharex,
        sharey=sharey,
        figsize=figsize,
        constrained_layout=True,
        **kwargs,
    )

    _apply_style(fig, axs, colors)

    # Apply global font sizes to all axes
    # axs might be a single Axes or an array of Axes
    if isinstance(axs, np.ndarray):
        for ax in axs.flat:
            set_fontsizes(fig, ax)
    else:
        set_fontsizes(fig, axs)

    return fig, axs

def _tag_figure(fig, font_properties, colors):
    """
    Store style objects on the figure so we can retrieve them later
    (e.g. when the caller adds a secondary y-axis).
    """
    fig._corp_font   = font_properties
    fig._corp_colors = colors

def style_extra_axis(ax):
    """
    Apply the corporate background colour and custom font to an
    axis that was created *after* the initial call to
    `setup_plot()` / `setup_subplots()` (e.g. via `ax.twinx()`).

    Usage
    -----
        ax2 = ax1.twinx()
        vis.style_extra_axis(ax2)
    """
    fig = ax.get_figure()

    # Figure must have been created by `setup_*`
    if not hasattr(fig, "_corp_font") or not hasattr(fig, "_corp_colors"):
        return  # silently skip – nothing to style against

    font   = fig._corp_font
    colors = fig._corp_colors

    ax.set_facecolor(colors["Background"])
    for item in (ax.title, ax.xaxis.label, ax.yaxis.label):
        item.set_fontproperties(font)
    for txt in ax.texts:
        txt.set_fontproperties(font)

def _detect_plot_type(ax: Axes) -> str:
    """
    Detect the most likely Matplotlib plot type living inside *ax*.

    Summary
    -------
    Scans the child artists of `ax` for tell-tale classes:
    • Wedge          → pie plot  
    • PathCollection → scatter plot  
    • Line2D         → line plot  
    • Rectangle      → bar / histogram  
    • ax.images      → heatmap / imshow

    Args
    ----
    ax (Axes): The Axes instance to classify.

    Returns
    -------
    str
        One of {"pie", "scatter", "line", "bar/hist", "heatmap", "unknown"}.
    """
    children = ax.get_children()                             # all artist objs

    # Pie → made of Wedge patches
    if any(isinstance(child, Wedge) for child in children):
        return "pie"

    # Scatter → PathCollection container
    if any(isinstance(child, PathCollection) for child in children):
        return "scatter"

    # Line → user-supplied Line2D with >1 datapoint
    user_lines = [
        ln for ln in children
        if isinstance(ln, Line2D) and ln.get_label() != "_nolegend_"
    ]
    if any(len(ln.get_xdata()) > 1 for ln in user_lines):
        return "line"

    # Bar / hist → Rectangle bars
    if any(isinstance(child, Rectangle) for child in children):
        return "bar/hist"

    # Heatmap → any AxesImage present
    if ax.images:
        return "heatmap"

    # Could not decide
    return "unknown"

def _extract_line_data(ax: Axes) -> list[dict]:
    """Return a list of dictionaries describing every user line."""
    data = []
    for ln in ax.get_lines():
        if ln.get_label() == "_nolegend_":               # skip spines/grids
            continue
        data.append(
            {
                "x": ln.get_xdata(),
                "y": ln.get_ydata(),
                "label": ln.get_label(),
                "style": {
                    "linewidth": ln.get_linewidth(),
                    "linestyle": ln.get_linestyle(),
                    "marker":   ln.get_marker(),
                },
            }
        )
    return data

def _extract_bar_data(ax: Axes) -> list[dict]:
    """Return [{x_left, height, width}, ...] for every bar rectangle."""
    data = []
    for patch in ax.patches:
        if not isinstance(patch, Rectangle):
            continue
        x_left, y_bottom = patch.get_xy()
        data.append(
            {
                "x_left": x_left,
                "height": patch.get_height(),
                "width":  patch.get_width(),
            }
        )
    return data

def _extract_scatter_data(ax: Axes) -> list[dict]:
    """Return [{x, y, sizes, alpha}, ...] for every scatter PathCollection."""
    data = []
    for pcoll in ax.collections:
        if not isinstance(pcoll, PathCollection):
            continue
        offsets = pcoll.get_offsets()            # N×2 ndarray of (x, y)
        data.append(
            {
                "x": offsets[:, 0],
                "y": offsets[:, 1],
                "sizes": pcoll.get_sizes(),
                "alpha": pcoll.get_alpha(),
            }
        )
    return data

_EXTRACTORS = {
    "line":     _extract_line_data,
    "bar/hist": _extract_bar_data,
    "scatter":  _extract_scatter_data,
}

def _rgba_to_hex(rgba) -> str:
    """
    Convert a Matplotlib RGBA tuple (or array of 4 floats 0-1) to hex.

    Example
    -------
    >>> _rgba_to_hex((0.96, 0.46, 0.00, 1.0))
    '#f57600'
    """
    r, g, b, *_ = rgba                                 # ignore alpha
    return "#{:02x}{:02x}{:02x}".format(
        int(round(r * 255)),
        int(round(g * 255)),
        int(round(b * 255)),
    ).lower()

def _rgba_to_hex(rgba: tuple[float, float, float, float]) -> str:
    """
    Internal one-liner that converts an RGBA-tuple (0-1 floats) to a #RRGGBB hex.
    """
    return mcolors.to_hex(rgba, keep_alpha=False)


"""
───────────────────────────────────────────────────────────────────────────────
 Helper-function: decide which edge colour (if any) should be applied to a
 cloned bar.  The function is *completely independent* from the surrounding
 plotting code so you can drop it into any module.
───────────────────────────────────────────────────────────────────────────────
"""
def decide_bar_edgecolor(
    original_patch: Rectangle,
    hex2key_map: dict[str, str | None],
    active_palette: dict[str, str],
) -> Optional[str]:
    """_Return an appropriate edge colour for a cloned bar (or ``None``)._

    Summary
    -------
    1. Inspect the *original* bar (a Matplotlib ``Rectangle``) to find out
       whether it carries an **explicit** edge colour.  
       • If the artist has *no* edge (``edgecolor is 'none'`` or the alpha  
         channel is 0) we return ``None`` – the caller should *omit* the  
         ``edgecolor=…`` keyword entirely.  
       • If an edge *is* present, we translate its colour into the **active
         corporate palette** if possible, otherwise we keep the original hex.

    2. The translation is done via *hex2key_map*, which comes straight from
       your ``clone_plot_with_palettes`` function.  That map already tells us
       which palette-key (e.g. ``"Secondary"``) corresponds to the bar’s
       original hex value.

    Parameters
    ----------
    original_patch : matplotlib.patches.Rectangle
        A single bar (or histogram bin) taken from the *source* Axes.
    hex2key_map : dict[str, str | None]
        Mapping “original hex → palette-key” produced in Step 3 of the clone
        algorithm.  Unknown colours map to ``None``.
    active_palette : dict[str, str]
        The palette currently being rendered (e.g. the dict returned by your
        ``get_color_palette("dark mode")`` helper).

    Returns
    -------
    str | None
        • Hex string (``"#RRGGBB"``) if an edge should be drawn.  
        • ``None`` if the cloned bar should inherit Matplotlib’s default,
          which effectively means “no edge”.

    Examples
    --------
    ```python
    edge_col = decide_bar_edgecolor(patch, hex2key, palette)
    ax.bar(..., color=new_face, edgecolor=edge_col)
    ```
    """
    # ------------------------------------------------------------------
    # 1. Retrieve the original edge colour as an RGBA tuple.
    #    Matplotlib returns *one* of the following:
    #       • "none"                              → no edge
    #       • tuple(len=4, alpha=0.0)             → fully transparent → no edge
    #       • tuple(len=4, alpha>0.0)             → explicit colour
    # ------------------------------------------------------------------
    edge_rgba = original_patch.get_edgecolor()

    # Matplotlib may give the literal string "none"; we treat that as “absent”.
    if isinstance(edge_rgba, str) and edge_rgba.lower() == "none":
        return None

    # Convert possible colour-spec strings (e.g. "#123456") to RGBA first.
    if isinstance(edge_rgba, str):
        edge_rgba = mcolors.to_rgba(edge_rgba)

    # At this point we *must* have an (r, g, b, a) tuple.
    if not isinstance(edge_rgba, tuple) or len(edge_rgba) != 4:
        # Unexpected – play safe: no explicit edge.
        return None

    # Fully transparent (alpha == 0) counts as “no edge”.
    if edge_rgba[3] == 0.0:  # alpha component
        return None

    # ------------------------------------------------------------------
    # 2. The bar definitely has an edge.  Decide which *hex* colour to draw.
    # ------------------------------------------------------------------
    orig_hex = _rgba_to_hex(edge_rgba)
    mapped_key = hex2key_map.get(orig_hex)

    # If the original colour is recognised and the key lives inside the
    # current palette, perform the swap; otherwise keep the original.
    if mapped_key in active_palette:
        return active_palette[mapped_key]

    return orig_hex  # fall-back: use the exact original colour

# ════════════════════════════════════════════════════════════════
# Main public API
# ════════════════════════════════════════════════════════════════
def clone_plot_with_palettes(
    original_ax: Axes,
    palettes: list[str] | None = None,
    n_cols: int = 2,
    figsize_per_plot: tuple[int, int] = (6, 4),
):
    """
    Duplicate *original_ax* into N sub-plots, replacing its colours with
    those from each requested corporate palette.

    One-line description
    --------------------
    “Colour-aware” plot cloning utility for line, bar, and scatter plots.

    Summary
    -------
    1. Detect the plot type inside *original_ax* (line / bar / scatter).
    2. Harvest plot data *plus* any explicit colour assignments that
       came from a DataFrame column named 'c', 'color', or 'colour'.
       (Detection is heuristic: if every data point / bar already owns
       an explicit colour we assume such a column was used.)
    3. Build a mapping
           original_hex_colour  →  <palette-key | 'UNMAPPED'>
       by comparing the extracted hex codes to the four corporate
       palettes.  Unknown colours remain unchanged.
    4. Draw one subplot per palette (default order:
       "default", "dark mode", "alternative", "greyscale").
       • Each recognised colour is swapped to its equivalent in the
         active palette (e.g. old '#253746' → new palette['Secondary']).
       • Unrecognised colours are left untouched.
    5. Return the new (fig, axes_list).

    Parameters
    ----------
    original_ax : matplotlib.axes.Axes
        The Axes you want to replicate.
    palettes : list[str] | None, default None
        Palette names understood by `get_color_palette`.  If *None*,
        uses the four corporate palettes in the canonical order.
    n_cols : int, default 2
        Column count of the subplot grid.
    figsize_per_plot : tuple[int, int], default (6, 4)
        Physical size in inches *per subplot*.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The newly created Figure containing all clones.
    axes_list : list[matplotlib.axes.Axes]
        Flat list of cloned Axes in left-to-right order.

    Raises
    ------
    NotImplementedError
        If *original_ax* hosts an unsupported plot type.
    """

    # ------------------------------------------------------------
    # 0. Default to the four corporate palettes if none provided.
    # ------------------------------------------------------------
    if palettes is None:
        palettes = ["default", "dark mode", "alternative", "greyscale"]

    # ------------------------------------------------------------
    # 1. Identify the plot type (line, bar/hist, scatter).
    # ------------------------------------------------------------
    plot_type = _detect_plot_type(original_ax)
    if plot_type not in {"line", "bar/hist", "scatter"}:
        raise NotImplementedError(
            f"clone_plot_with_palettes supports line, bar/hist, "
            f"and scatter plots only (got '{plot_type}')."
        )

    # ------------------------------------------------------------
    # 2. Extract DATA  +  PER-ELEMENT original colours ────────────
    #    (Only scatter & bar really need colour harvesting.)
    # ------------------------------------------------------------
    if plot_type == "line":
        # —— LINE: simple; colour per *line* not per data point.
        lines_data = []
        for ln in original_ax.get_lines():
            if ln.get_label() == "_nolegend_":          # skip spines/grids
                continue
            lines_data.append(
                {
                    "x": ln.get_xdata(),
                    "y": ln.get_ydata(),
                    "style": {
                        "linewidth": ln.get_linewidth(),
                        "linestyle": ln.get_linestyle(),
                        "marker":    ln.get_marker(),
                    },
                    "orig_hex": _rgba_to_hex(ln.get_color_rgba()),
                }
            )
        plot_data = lines_data

    elif plot_type == "bar/hist":
        bars_data = []
        for patch in original_ax.patches:
            if not isinstance(patch, Rectangle):
                continue
            x_left, _ = patch.get_xy()
            bars_data.append(
                {
                    "x_left":   x_left,
                    "height":   patch.get_height(),
                    "width":    patch.get_width(),
                    "orig_hex": _rgba_to_hex(patch.get_facecolor()),
                }
            )
        plot_data = bars_data

    elif plot_type == "scatter":
        scat_data = []
        for pc in original_ax.collections:
            if not isinstance(pc, PathCollection):
                continue
            offsets     = pc.get_offsets()
            sizes       = pc.get_sizes()
            facecolors  = pc.get_facecolors()
            # If no per-point colours were supplied, Matplotlib may store
            # only one RGBA; replicate to match point count.
            if len(facecolors) == 1:
                facecolors = facecolors.repeat(offsets.shape[0], axis=0)
            scat_data.append(
                {
                    "x": offsets[:, 0],
                    "y": offsets[:, 1],
                    "sizes": sizes,
                    "alpha": pc.get_alpha() or 1.0,
                    # store list[str] of original hex codes (one per point)
                    "orig_hex": [_rgba_to_hex(fc) for fc in facecolors],
                }
            )
        plot_data = scat_data

    # ------------------------------------------------------------
    # 3. Build ORIGINAL_HEX  →  palette-KEY mapping.
    #    • We look across all corporate palettes; when a hex matches
    #      any colour exactly, we remember the associated key
    #      ('Primary', 'Secondary', ...).  Otherwise mark 'UNMAPPED'.
    # ------------------------------------------------------------
    from itertools import chain

    # Collect every hex colour encountered in the plot.
    if plot_type == "scatter":
        all_hex = set(chain.from_iterable(d["orig_hex"] for d in plot_data))
    else:  # line / bar
        all_hex = {d["orig_hex"] for d in plot_data}

    hex2key: dict[str, str | None] = {}                 # mapping result
    for hx in all_hex:
        matched_key = None                              # default “unmapped”
        for palette in ["default", "dark mode", "alternative", "greyscale"]:
            for key_name, key_hex in _PALETTES[palette].items():
                if hx.lower() == key_hex.lower():
                    matched_key = key_name              # e.g. "Secondary"
                    break
            if matched_key:
                break
        hex2key[hx] = matched_key                       # may be None

    # ------------------------------------------------------------
    # 4. Allocate a new Figure with an r×c grid.
    # ------------------------------------------------------------
    n_plots = len(palettes)
    n_rows  = -(-n_plots // n_cols)                     # ceiling division
    total_figsize = (figsize_per_plot[0] * n_cols,
                     figsize_per_plot[1] * n_rows)
    fig = plt.figure(figsize=total_figsize, constrained_layout=True)
    axes_clones: list[Axes] = []                        # output container

    # ------------------------------------------------------------
    # 5. Loop over each requested palette and draw the clone.
    # ------------------------------------------------------------
    for idx, pal_name in enumerate(palettes, start=1):
        # a) Build a styled subplot using corporate helper ─────────
        sub_fig, _ = setup_plot(color=pal_name, figsize=figsize_per_plot)
        ax = fig.add_subplot(n_rows, n_cols, idx)       # real target Axes
        pal_colors = get_color_palette(pal_name)
        # re-apply style (font already registered globally)
        _apply_style(fig, ax, pal_colors)
        axes_clones.append(ax)

        # b) Draw data, swapping colours where we know the mapping ──
        if plot_type == "line":
            for ln_data in plot_data:
                # decide which colour to use
                mapped_key = hex2key[ln_data["orig_hex"]]
                new_col = (
                    pal_colors[mapped_key]
                    if mapped_key in pal_colors
                    else ln_data["orig_hex"]
                )
                ax.plot(
                    ln_data["x"],
                    ln_data["y"],
                    color=new_col,
                    **ln_data["style"],
                )

        elif plot_type == "bar/hist":
            for original_patch, bar in zip(original_ax.patches, plot_data):
                mapped_key = hex2key[bar["orig_hex"]]
                new_facecol = (
                    pal_colors[mapped_key]
                    if mapped_key in pal_colors
                    else bar["orig_hex"]
                )

                # ── NEW: decide whether an edge colour is needed ──────────────
                new_edgecol = decide_bar_edgecolor(
                    original_patch=original_patch,
                    hex2key_map=hex2key,
                    active_palette=pal_colors,
                )

                ax.bar(
                    x=bar["x_left"],
                    height=bar["height"],
                    width=bar["width"],
                    color=new_facecol,
                    edgecolor=new_edgecol,   # ← could be a hex or None
                )
        elif plot_type == "scatter":
            for sc in plot_data:
                # Translate list of original hex codes into new ones
                new_cols = [
                    pal_colors[hex2key[hx]]             # swap if mapped
                    if hex2key[hx] in pal_colors
                    else hx                             # leave unchanged
                    for hx in sc["orig_hex"]
                ]
                ax.scatter(
                    sc["x"], sc["y"],
                    s=sc["sizes"],
                    c=new_cols,                         # per-point colours
                    alpha=sc["alpha"],
                )

        # c) Title
        ax.set_title(f"Palette: {pal_name}",
                     loc="left", color=pal_colors["Secondary"])

        # Discard temp figure generated by setup_plot (no memory leak)
        plt.close(sub_fig)

    # ------------------------------------------------------------
    # 6. Return the freshly minted Figure + list of Axes
    # ------------------------------------------------------------
    return fig, axes_clones

