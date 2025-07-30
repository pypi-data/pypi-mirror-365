import string
import distinctipy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize, ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.spatial.distance import pdist, squareform
from .misctools import check_list, equal_sequences, flat_list, spread_shuffle, \
                       round_power
from .filters import downsampling
from .stats import spectrogram


# FIGURES & AXES:


def setup_fig(rows=1, cols=1, size=None, width=16., height=None, row_height=3.,
              unit=1 / 2.54, with_axes=True, return_specs=False,
              letter_specs={}, uppercase=False, **kwargs):
    """ Creates a standardized figure, with or without a grid of subplots.
        Figure size can be specified directly or calculated from other inputs.
        Size-related parameters are converted from inches to the desired unit.
        Can optionally return a dictionary of figure size, grid layout, and
        characters for subplot annotations with specified font properties.

    Parameters
    ----------
    rows : int, optional
        Number of subplot rows in the grid. The default is 1.
    cols : int, optional
        Number of subplot columns in the grid. The default is 1.
    size : tuple or list (2,) of floats or ints, optional
        If specified, sets the figure size (width, height) in the given unit.
    width : float or int, optional
        If specified and size is None, sets the figure width in unit.
        The default is 16.0.
    height : float or int, optional
        If specified and size is None, sets the figure height in unit. If both
        size and height are None, calculated as row_height * rows in unit.
        The default is None.
    row_height : float or int, optional
        If specified and height and size are None, determines the figure height
        by row_height * rows in unit. Height of rendered subplots will likely
        be smaller due to padding space taken from figure. The default is 3.0.
    unit : float, optional
        Conversion factor to transform size, width, height, and row_height from
        default inches to the desired unit. The default is 1 / 2.54 for cm.
    with_axes : bool, optional
        If True, calls plt.subplots() with rows, cols, figsize, and additional
        keyword arguments, and returns the figure and axes handles. Else, calls
        plt.figure() with figsize and additional keyword arguments, and returns
        the figure handle. The default is True.
    return_specs : bool, optional
        If True, also returns a dictionary of figure properties and subplot
        annotation letters. Contains 'size', 'grid', 'chars', and 'char_specs'.
        The default is False.
    letter_specs : dict, optional
        Text properties to update returned default 'char_specs' dictionary.
        Ignored if return_specs is False. The default is {}.
    uppercase : bool, optional
        If True, returns uppercase strings as letters for subplot annotations,
        else lowercase. Ignored if return_specs is False. The default is False.
    **kwargs : dict, optional
        Additional keyword arguments passed to plt.subplots() if with_axes is
        True, or to plt.figure() if with_axes is False.

    Returns
    -------
    fig : matplotlib figure object
        Handle to the created figure.
    axes : (array of) matplotlib axes objects
        Handles to the created subplots in the requested grid layout.
        Only returned if with_axes is True.
    params : dict
        Contains 'size' for the figure size (width, height) in unit, 'grid' for
        the grid layout (rows, cols), 'chars' for a list of string characters
        for subplot annotations (as many as axes), and 'char_specs' for a
        dictionary of text properties to pass to plt.text() when annotating
        subplots. Only returned if return_specs is True.
    """       
    # Input interpretation:
    if size is None:
        if height is None:
            # Equal aspect for single subplot, else scaled by row number:
            height = width if (rows * cols) == 1 else rows * row_height
        size = (width * unit, height * unit)
    else:
        # Convert units of specified size:
        size = (size[0] * unit, size[1] * unit)
    # Expand figure settings:
    kwargs['figsize'] = size

    if return_specs:
        # Fetch letters for subplot annotations:
        chars = string.ascii_uppercase if uppercase else string.ascii_lowercase
        chars = list(chars[:rows * cols])
        # Default font:
        char_specs = {
            'x': 0,
            'y': 1.125,
            'c': 'k',
            'fontsize': 15,
            'weight': 'bold',
            'ha': 'center',
            'va': 'center'
        }
        # Override with user settings:
        char_specs.update(letter_specs)
        # Wrap up:
        specs = {
            'size': size,
            'grid': (rows, cols),
            'chars': chars,
            'char_specs': char_specs
        }

    # Return options:
    if with_axes:
        # Figure with one or multiple subplots:
        fig, axes = plt.subplots(rows, cols, **kwargs)
        return (fig, axes, specs) if return_specs else (fig, axes)
    # Blank figure:
    fig = plt.figure(**kwargs)
    return (fig, specs) if return_specs else fig


def switch_transforms(coords, current, target, bbox=False):
    """ Converts coordinates from one matplotlib transform to another.
        Each of matplotlib's transforms maps only from one distinct coordinate
        system into display coordinates, or back using the inverse transform.
        To remap coordinates from one non-display coordinate system to another,
        coordinates must first be converted to display coordinates using the
        current transform, and then mapped to the desired coordinate system
        using the inverse of the target transform.

        Available transforms include:
        # ax.transAxes (relative axes coordinates)
        # ax.transData (axes coordinates in data units) -> CHANGES WITH LIMITS!
        # subfigure.transSubfigure (relative subfigure coordinates)
        # fig.transFigure (relative figure coordinates)
        # fig.dpi_scale_trans (figure coordinates in inches)
        # ax.get_xaxis_transform() (blended relative/data axes coordinates)
        # ax.get_yaxis_transform() (blended relative/data axes coordinates)
        # IdentityTransform (display coordinates, no conversion).

    Parameters
    ----------
    coords : 2D array (m, 2) or array-like (2 * m,) of floats or ints
        Coordinates to be transformed. Number of elements must be even. If bbox
        is False, expects pure point coordinates as pairs (x, y). If bbox is
        True, expects bounding boxes as multiples of 4 (x, y, width, height).
    current : matplotlib transform
        Current coordinate system of the provided coordinates.
    target : matplotlib transform
        Target coordinate system to convert coordinates to.
    bbox : bool, optional
        If True, expects bounding box coordinates (x, y, width, height).
        Necessary to correctly convert rectangle extents. The default is False.

    Returns
    -------
    coordinates : 2D array (m, 2) or 1D array (2 * m,) of floats
        Converted coordinates in the coordinate system specified by target.
        If bbox is True, output shape is (m, 4) or (4 * m,) instead.
    """
    # Define required transformation:
    double_transform = current + target.inverted()
    if not bbox:
        # Pure point coordinates:
        return double_transform.transform(coords)

    # Bounding box coordinates:
    if not isinstance(coords, np.ndarray):
        coords = np.array(coords)
    dims = coords.ndim
    coords = np.reshape(coords, (-1, 4))
    coords[:, 2:] += coords[:, :2]
    coords = double_transform.transform(coords).reshape(-1, 4)
    coords[:, 2:] -= coords[:, :2]
    return coords if dims == 2 else coords.ravel()


def update_limits(ax, which, low=None, high=None, axes=None, expand=True):
    """ Decides whether to adjust current axes limits to the specified bounds.
        Can either contract or expand the limits by choosing the smaller or
        larger of the current and the given bound. Applies new axes limits to
        the target subplot as well as any other passed subplot. Best used in
        combination with a tick locator.

    Parameters
    ----------
    ax : matplotlib axes object
        Target subplot whose current axes limits are used as reference.
    which : str
        Target axis or axes of the subplot. Options are 'x', 'y', or 'both'.
    low : float or int, optional
        If specified, potential new lower bound of the requested target axis.
        The default is None.
    high : float or int, optional
        If specified, potential new upper bound of the requested target axis.
        The default is None.
    axes : (1D array or list or tuple of) matplotlib axes object(s), optional
        If specified, applies the new axes limits to these subplots as well.
        The default is None.
    expand : bool, optional
        If True, expands the current axis limits by taking the smaller lower
        bound and the larger upper bound. Else, contracts the limits by taking
        the larger lower bound and smaller upper bound. The default is True.
    """
    # Bundle targets:
    subplots = [ax]
    if np.iterable(axes):
        subplots.extend(axes)
    elif axes is not None:
        subplots.append(axes)

    # Decide between expanding or contracting axes limits:
    low_func, high_func = (min, max) if expand else (max, min)

    # Treat x-axis limits:    
    if which == 'x' or which == 'both':
        limits = ax.get_xlim()
        if low is not None:
            low_limit = low_func([limits[0], low])
            [ax.set_xlim(left=low_limit) for ax in subplots]
        if high is not None:
            high_limit = high_func([limits[1], high])
            [ax.set_xlim(right=high_limit) for ax in subplots]

    # Treat y-axis limits:
    if which == 'y' or which == 'both':
        limits = ax.get_ylim()
        if low is not None:
            low_limit = low_func([limits[0], low])
            [ax.set_ylim(bottom=low_limit) for ax in subplots]
        if high is not None:
            high_limit = high_func([limits[1], high])
            [ax.set_ylim(top=high_limit) for ax in subplots]
    return None


def data_limits(data, margins=0.1, axes=None, which=None, log=False):
    """ Computes padded lower and upper axes limits to fully encompass data.
        Limits are calculated as minimum and maximum values of data padded by
        some proportion of the data range. Same functionality as ax.margin(),
        but supports individual margins for lower and upper limits.

    Parameters
    ----------
    data : list of floats or ints (m,) or array of arbitrary shape
        Plotted data for which to compute limits. Accepts any iterable.
        Extreme values are always calculated over the flattened data.
    margins : float or tuple/list of floats (2,), optional
        Proportion of the data range (maximum - minimum) to use for padding.
        If scalar, uses the same margin for both lower and upper limits. Two
        provided values define individual margins for lower and upper limits,
        respectively. The default is 0.1.
    axes : matplotlib axes object or list of axes objects, optional
        If specified, directly applies the calculated limits to the desired
        axes of the given subplots. The default is None.
    which : str, optional
        Target axis or axes of each given subplot to apply the calculated
        limits. Ignored if axes is None. Options are 'x', 'y', or 'both'.
        The default is None.
    log : bool, optional
        If True, assumes log-scaled data and adjusts padding calculation so
        that the same margin for lower and upper limits results in visually
        equal padding on a logarithmic scale. The default is False.

    Returns
    -------
    limits : tuple of floats (2,)
        Calculated axes limits to encompass the data with the given margins.
    """    
    # Input interpretation:
    if not isinstance(margins, (list, tuple)):
        margins = (margins, margins)
    # Assert iterable:
    axes = check_list(axes)
    # Determine extremes and range of data:
    minimum, maximum = np.min(data), np.max(data)
    span = maximum - minimum
    if not log:
        # Pad extremes by proportion of data range on a linear scale:
        limits = (minimum - span * margins[0], maximum + span * margins[1])
    else:
        # Pad on a logarithmic scale and convert back to linear scale:
        limits = (10**(np.log10(minimum) - np.log10(span) * margins[0]),
                  10**(np.log10(maximum) + np.log10(span) * margins[1]))
    # Optional application of calculated axes limits:
    if axes is not None and (which == 'x' or which == 'both'):
        [ax.set_xlim(limits) for ax in axes]
    if axes is not None and (which == 'y' or which == 'both'):
        [ax.set_ylim(limits) for ax in axes]
    return limits


def log_axes(axes, which, scale='log', base=10, subs=[2, 3, 4, 5, 6, 7, 8, 9],
             linthresh=None, linscale=None, x=None, y=None,
             xlim=(None, None), ylim=(None, None), zerotol=None):
    """ Logarithmic rescaling of one or both axes of the given target subplots.
        Can handle log-incompatible (zero or negative) values in the axis data
        by switching to a symmetric pseudo-logarithmic (symlog) axis scaling. 

    Parameters
    ----------
    axes : matplotlib axes or 1D array-like of matplotlib axes
        One or several target subplots for logarithmic axis rescaling.
    which : str
        Target axis for rescaling. Options are 'x', 'y', or 'both'.
    scale : str, optional
        Type of logarithmic scale to apply. Options are 'log' for standard
        logarithmic scaling, or 'symlog' for symmetric pseudo-logarithmic
        scaling with a central linear region around zero and two mirrored
        logarithmic sides. If x or y axis data is given and contains any non-
        positive values, replaces log with symlog scale. The default is 'log'. 
    base : int, optional
        Base of the logarithm. The default is 10.
    subs : 1D array-like of ints, optional
        Number and position of minor axis ticks within one decade on the log
        scale (e.g. from 1 to 10). The default is [2, 3, 4, 5, 6, 7, 8, 9],
        resulting in 8 equally spaced minor ticks for a base-10 logarithm. 
    linthresh : float or int, optional
        Transition point between the linear region and each logarithmic side of
        the symlog scale. If x or y axis data is given, set to the minimum
        absolute non-zero value with respect to zerotol, else falls back to
        a default value of 1e-3. The default is None.
    linscale : float, optional
        Factor for warping each side of the linear region on the symlog scale,
        in multiples of the visual space occupied by a single decade on the
        logarithmic sides. If x or y axis data is given, set to 0.25 for a one-
        sided symlog (one axis limit at 0), or 0.5 for two-sided. The default is None.
    x : ND array of floats or ints, optional
        Collection of values to be represented on the x-axis. Triggers switch
        to symlog scale if any non-positive values are present. Used to infer
        missing linthresh and linscale inputs. Unspecified axis limits are set
        to match the range of the data. The default is None.
    y : ND array of floats or ints, optional
        Collection of values to be represented on the y-axis. Triggers switch
        to symlog scale if any non-positive values are present. Used to infer
        missing linthresh and linscale inputs. Unspecified axis limits are set
        to match the range of the data. The default is None.
    xlim : 1D array-like of floats or ints or None (2,), optional
        Left and right limit of the x-axis. Nones are treated as unspecified
        limits (can be auto-completed from x). The default is (None, None).
    ylim : 1D array-like of floats or ints or None (2,), optional
        Lower and upper limit of the y-axis. Nones are treated as unspecified
        limits (can be auto-completed from y). The default is (None, None).
    zerotol : float, optional
        Maximum allowed distance for snapping one of two axis limits to zero.
        No snapping is performed if zerotol is not given. The default is None.
    """
    
    # Initialize helpers for axis rescaling:
    set_x = lambda ax, **args: ax.set_xscale(**args)
    set_y = lambda ax, **args: ax.set_yscale(**args)
    set_scale = {'x': (set_x,), 'y': (set_y,), 'both': (set_x, set_y)}[which]

    # Initialize helpers for axis limits:
    set_x = lambda ax, limits: ax.set_xlim(limits)
    set_y = lambda ax, limits: ax.set_ylim(limits)
    set_limit = {'x': (set_x,), 'y': (set_y,), 'both': (set_x, set_y)}[which]
    limits = {'x': [xlim], 'y': [ylim], 'both': [xlim, ylim]}[which] 

    # Prepare general log/symlog scale settings:
    args = {'value': scale, 'base': base, 'subs': subs}
    if scale == 'symlog':
        # Expand with symlog scale-specific settings:
        args.update({'linthresh': linthresh, 'linscale': linscale})
    # Split into axis-specific settings:
    args = [args.copy() for _ in set_scale]

    # Consider switch from log to symlog to represent non-positive axis data:
    for i, data in enumerate({'x': (x,), 'y': (y,), 'both': (x, y)}[which]):

        # Data-free early exit:
        if data is None:
            # Fall back to default settings:
            if 'linthresh' in args[i] and linthresh is None:
                args[i]['linthresh'] = 1e-3
            if 'linscale' in args[i] and linscale is None:
                args[i]['linscale'] = 0.5
            continue

        # Determine extent of data on target axis:
        data_range = np.array([np.min(data), np.max(data)])
        # Snap endpoint to zero:
        if zerotol is not None:
            distance = data_range.abs()
            # Choose endpoint closer to zero (if both are within tolerance):
            data_range[(distance <= zerotol) & (distance == distance.min())] = 0

        # Auto-complete user-defined limits:
        zipped = zip(data_range, limits[i])
        limits[i] = [value if lim is None else lim for value, lim in zipped]

        # All-positive early exit:
        if limits[i][0] > 0:
            continue

        # Allow non-positive values:
        args[i]['value'] = 'symlog'
        if linscale is None:
            # Half linear space of one-sided symlog:
            linscale = 0.25 if 0 in limits[i] else 0.5
        args[i]['linscale'] = linscale
        if linthresh is None:
            # Prepare indices of non-zero data points within axis limits:
            ind = (data >= limits[i][0]) & (data <= limits[i][1]) & (data != 0)
            # Get minimum distance to zero:
            thresh = np.abs(data[ind]).min()
            # Find next-closer integer exponent towards zero:
            linthresh = round_power(thresh, base, which='floor')[0]
        args[i]['linthresh'] = linthresh

    # Apply axis limits and scaling to one or more subplots:
    for ax in (axes,) if isinstance(axes, plt.Axes) else axes:
        [func(ax, lims) for func, lims in zip(set_limit, limits)]
        [func(ax, **kwargs) for func, kwargs in zip(set_scale, args)]
    return None


def sync_axes(main_ax, sub_axes, which, hide_labels=True):
    """ Synchronizes axes limits and tick locators between the given subplots.
        Meant to create look of shared axes if actual sharing is not feasible.
        Limits and locators of reference subplot should be set before calling.

    Parameters
    ----------
    main_ax : matplotlib axes object
        Reference subplot that determines the desired limits and locators. If
        hide_labels is True, main_ax should be the first subplot in line, as it
        is the only one that retains all axes labels and tick labels.
    sub_axes : matplotlib axes object or list of axes objects
        Dependent subplots whose limits and locators are adjusted.
    which : str
        Target axis or axes of dependent subplots to synchronize to the 
        reference. Options are 'x', 'y', 'both'.
    hide_labels : bool, optional
        If True, removes specified tick labels and axes labels from each
        dependent subplot but leaves ticks as is. The default is True.
    """    
    # Input interpretation:
    if isinstance(sub_axes, np.ndarray):
        sub_axes = sub_axes.tolist()
    else:
        # Assert iterable:
        sub_axes = check_list(sub_axes)
        
    for sub_ax in sub_axes:
        # Treat x-axis limits and ticks:
        if which == 'x' or which == 'both':
            sub_ax.set_xlim(main_ax.get_xlim())
            sub_ax.xaxis.set_major_locator(main_ax.xaxis.get_major_locator())
            sub_ax.xaxis.set_minor_locator(main_ax.xaxis.get_minor_locator())
            if hide_labels:
                sub_ax.set_xticklabels([])
                sub_ax.set_xlabel('')
        # Treat y-axis limits and ticks:
        if which == 'y' or which == 'both':
            sub_ax.set_ylim(main_ax.get_ylim())
            sub_ax.yaxis.set_major_locator(main_ax.yaxis.get_major_locator())
            sub_ax.yaxis.set_minor_locator(main_ax.yaxis.get_minor_locator())
            if hide_labels:
                sub_ax.set_yticklabels([])
                sub_ax.set_ylabel('')
    return None


def split_axes(ax, side, percent=10, pad=5):
    """ Divides parent subplot into two or more separate subplots.
        Meant to create smaller axes objects whose width or height matches the
        parent (e.g. for colorbars). Repeated calls on the same parent might
        have undesirable effects, so all splits should be done in one go. For
        multiple splits, pass any of side, percent, or pad as sequence-likes of
        equal number of elements. Single-element inputs are repeated to match.

    Parameters
    ----------
    ax : matplotlib axes object
        Parent subplot to be divided.
    side : str or tuple/list/1D array of str (m,)
        Side of the parent subplot where each new subplot should be split off.
        Options are 'top', 'bottom', 'left', 'right'.
    percent : int or tuple/list/1D array of ints, optional
        Extent of each new subplot relative to the parent subplot as percentage
        of width (if side is 'left' or 'right') or height (if side is 'top' or
        'bottom'). This proportion does not appear as expected in the displayed
        figure due to internal unit differences! The default is 10.
    pad : int or tuple/list/1D array of ints, optional
        Padding between each new subplot and the remainder of the parent
        subplot as percentage of the parent's width or height (same behavior as
        the percent argument). The default is 5.

    Returns
    -------
    matplotlib axes object or list of axes objects
        New subplot(s) split off from the parent subplot. Extent and padding do
        not appear as expected in the displayed figure due to internal unit
        differences but are consistent between each other.
    """    
    # Open divider on parent axes:
    div = make_axes_locatable(ax)

    # Return single split for single-element inputs:
    if not any(np.ndim(variable) for variable in [side, percent, pad]):
        return div.append_axes(side, size=f'{percent}%', pad=f'{pad}%')

    # Equalize lengths and return multiple splits:
    vars = zip(equal_sequences(side, percent, pad))
    return [div.append_axes(s, f'{per}%', f'{p}%') for s, per, p in vars]


def inset_axes(ax, transform, x=None, y=None, width=None, height=None,
               xn=1, yn=1, **kwargs):
    """ Adds one or more inset axes to the given parent subplot.

    Parameters
    ----------
    ax : matplotlib axes
        Target subplot to insert the inset axes.
    transform : matplotlib transform
        Coordinate system of all of x, y, width, and height. Pass ax.transAxes
        to use relative coordinates or ax.transData to use data coordinates.
    x : float or int or array-like (m,) of floats or ints, optional
        Coordinates of the center of the inset axes in x. If not provided, 
        generates xn evenly spaced center coordinates. The default is None. 
    y : float or int or array-like (m,) of floats or ints, optional
        Coordinates of the center of the inset axes in y. If not provided,
        generates yn evenly spaced center coordinates. The default is None.
    width : float or int or array-like (m,) of floats or ints, optional
        Horizontal extent of the inset axes. If not provided, uses the minimum
        distance between x-coordinates, or the whole x-axis range in case of
        a single inset axes. The default is None.
    height : float or int or array-like (m,) of floats or ints, optional
        Vertical extent of the inset axes. If not provided, uses the minimum
        distance between y-ccordinates, or the whole y-axis range in case of
        a single inset axes. The default is None.
    xn : int, optional
        If x is None, the number of center coordinates to create in x.
        New x is converted to match the given transform. The default is 1.
    yn : int, optional
        If y is None, the number of center coordinates to create in y.
        New y is converted to match the given transform. The default is 1.
    **kwargs : dict, optional
        Additional keyword arguments passed to ax.inset_axes().

    Returns
    -------
    sub_axes : list of matplotlib axes
        One or more inset axes in the given parent subplot.
    """
    def complete_inputs(which, coords, extent, n):
        # Get full axis range in relative or data coordinates:
        limits = {'x': ax.get_xlim, 'y': ax.get_ylim}[which]()
        full = limits[1] - limits[0] if transform is ax.transData else 1
        if coords is None:
            # Create equidistant centered relative coordinates:
            coords = np.linspace(0, 1, n + 1)[:-1] + 1 / n / 2
            if transform is ax.transData:
                # Data coordinates:
                coords *= full
                coords += limits[0]
        if extent is None:
            # Default to all available space on axis or between coordinates:
            extent = full if np.size(coords) == 1 else min(np.diff(coords))
        return coords, extent

    # Input interpretation and completion:
    x, width = complete_inputs('x', x, width, xn)
    y, height = complete_inputs('y', y, height, yn)

    # Ensure sequence-likes with equal numbers of elements:
    x, y, width, height = equal_sequences(x, y, width, height, skip_None=True)

    # Create axes:
    sub_axes = []
    for x0, y0, w, h in zip(x, y, width, height):
        extent = (x0 - w / 2, y0 - h / 2, w, h)
        sub_axes.append(ax.inset_axes(extent, transform=transform, **kwargs))
    return sub_axes


def auto_plotgrid(n_plots, fig=None, order='row', long_axis=0, grid_min=2,
                  n_rows=None, n_cols=None, plot_size=5, x=None, y=None,
                  **kwargs):
    """ Mass-produces subplots in an optimized grid layout of given attributes.
        Grid layout can be constrained to a fixed number of rows or columns, or
        automatically calculated as a pair of integers whose product matches
        the requested number of subplots as closely as possible. The aspect of
        the grid can be controlled by specifying the longer axis. Created
        subplots are filled into the grid in the specified order (default: row-
        major). The order of the returned axes matches the order of creation.
        If no target figure is provided, creates a new figure and scales its
        size to the grid extent. This function is meant for quick visualization
        of data with many variables or categories, and returns the created axes
        in an order that allows for plotting structured data in a single loop.

    Parameters
    ----------
    n_plots : int
        Total number of subplots to create.
    fig : Matplotlib figure object, optional
        If specified, the target figure to add subplots to. Else, creates a new
        figure with constrained layout and varying size. Figure size is the
        number of rows and columns in the grid scaled by plot_size in inches,
        and clipped to a minimum of 1x1 and a maximum of 20x10 inches.
    order : str, optional
        Order of created subplots in grid (determines order of returned axes).
        Should correspond to the order in which subplots are supposed to be
        filled later. Options are 'row' for row-major order or 'col' for
        column-major order. The default is 'row'.
    long_axis : int, optional
        The grid axis to extend if n_plots does not fit a square grid. Options
        are 0 for rows or 1 for columns. If n_plots does not fit a rectangular
        grid, an additional row or column that is not completely filled is
        appended to the shorter axis, so that the extent of the longer axis
        increases by one. Can be overridden by certain values of n_rows and
        n_cols. The default is 0.
    grid_min : int, optional
        If specified without n_rows and n_cols, the minimum number of rows or
        columns that are allowed in the auto-adjusted grid. During auto-
        adjustment, first attempts to find a square grid that fits n_plots
        with side length int(np.sqrt(n_plots). Next, gets all integer numbers 
        in [grid_min, side length] that divide n_plots evenly, and takes the
        largest one (if any). This gives a rectangular grid with exactly
        n_plots positions, whose aspect depends on long_axis. As a fallback,
        expands one side of the square grid to hold at least n_plots axes,
        which results in overhanging subplots arrangements. Given grid_min is
        always clipped to [1, side length + 1]. Pass None to disable search for
        clean rectangular grid shapes. The default is 2.
    n_rows : int, optional
        If specified, a fixed number of rows in the grid. The number of columns
        is calculated as np.ceil(n_plots / n_rows), which may result in over-
        hanging subplots. If specified together with n_cols, enforces a fixed
        rectangular grid (likely underfilled, may throw an error if too small).
        Overrides grid_min and potentially long_axis, too. The default is None.
    n_cols : int, optional
        If specified, a fixed number of columns in the grid. The number of rows
        is calculated as np.ceil(n_plots / n_cols), which may result in over-
        hanging subplots. If specified together with n_rows, enforces a fixed
        rectangular grid (likely underfilled, may throw an error if too small).
        Overrides grid_min and potentially long_axis, too. The default is None.
    plot_size : float or int or tuple or list (2,) of floats or ints, optional
        If fig is not specified, sets the size of the created figure by scaling
        the extent of the finalized grid (so that each row/column is around
        plot_size inches wide). Add conversion fators to plot_size for other
        units. Single values specify equal widths for both rows and columns.
        Two values specify different widths in the format (columns, rows). Mind
        that the input order is in standard figsize format (width, height)
        instead of matrix format (rows, columns). Always clipped to a minimum
        of 1 inch and a maximum of 20 inches width and 10 inches height. The
        default is 5.
    x : str, optional
        If specified, used as x-axis label of the bottom-most subplot in each
        column. Passing the xlabel keyword argument instead applies the label
        to all subplots. The default is None.
    y : str, optional
        If specified, used as y-axis label of the left-most subplot in each
        row. Passing the ylabel keyword argument instead applies the label to
        all subplots. The default is None.
    **kwargs : dict, optional
        Additional keyword arguments passed to plt.subplot2grid() and further
        to plt.add_subplot() to specify additional subplot attributes. If the
        sharex or sharey keyword arguments are provided, they must be specified
        as a bool instead of the usual axes object (if True, uses first created
        subplot as reference whose axes are shared by all other subplots).

    Returns
    -------
    axes : list of Matplotlib axes objects [n_plots,]
        Created subplots in the order of their insertion into the grid. If
        order is 'col', subplots are added column-wise from top to bottom and
        left to right. Else, subplots are added row-wise from left to right and
        top to bottom. Can be used to plot data in a structured way without
        iterating in nested loops (e.g. over 2D arrays of axes objects).

    Raises
    ------
    ValueError
        Breaks if long_axis is not 0 or 1, or if n_rows * n_cols < n_plots.
    """    
    # Validate inputs:
    if long_axis not in [0, 1]:
        raise ValueError('Longer grid axis must be 0 (rows) or 1 (columns).')
    # Range-check inputs:
    even_side = int(np.sqrt(n_plots))
    if grid_min is None:
        grid_min = even_side + 1
    grid_min = min(max(grid_min, 1), even_side + 1)
    if n_rows is not None:
        n_rows = min(max(n_rows, 1), n_plots)
    if n_cols is not None:
        n_cols = min(max(n_cols, 1), n_plots)
    if n_rows is not None and n_cols is not None:
        if n_rows * n_cols < n_plots:
            msg = 'A grid with n_rows x n_cols must hold at least n_plots.'
            raise ValueError(msg)
    # Manage keywords:
    keywords = kwargs.copy()
    switch_keys = [key for key in ['sharex', 'sharey'] if key in kwargs]
    # Disable shared axes for first created subplot:
    keywords.update({key: None for key in switch_keys})

    # Shape of overall subplot grid:
    if n_rows is not None and n_cols is not None:
        # Fixed rectangular grid:
        grid = [n_rows, n_cols]
    if n_rows is not None and n_cols is None:
        # Rectangular grid with fixed number of rows:
        grid = [n_rows, int(np.ceil(n_plots / n_rows))]
    elif n_rows is None and n_cols is not None:
        # Rectangular grid with fixed number of columns:
        grid = [int(np.ceil(n_plots / n_cols)), n_cols]
    else:
        # Initial square grid:
        even_side = int(np.sqrt(n_plots))
        if even_side**2 == n_plots:
            # Clean square grid:
            grid = [even_side, even_side]
        else:
            # Check for integers that divide n_plots evenly:
            test_ints = np.arange(even_side, grid_min - 1, -1)
            factors = test_ints[n_plots % test_ints == 0]
            if len(factors):
                # Clean rectangular grid without overhang:
                grid = [factors[0], n_plots // factors[0]]
                # Assign larger number of subplots to long side of grid:
                grid[long_axis], grid[1 - long_axis] = max(grid), min(grid)
            else:
                # Overhanging rectangular grid:
                grid = [even_side, even_side]
                # Append half-filled row/column to short side of grid:
                grid[long_axis] = int(np.ceil(n_plots / even_side))

    # Get coordinates of each possible subplot in grid:
    row_coords, col_coords = np.mgrid[:grid[0], :grid[1]]
    if order == 'col':
        # Flip grid to flatten in column-major order:
        row_coords, col_coords = row_coords.T, col_coords.T
    # Flatten grid coordinates into position vectors (row, col):
    position = np.vstack([row_coords.ravel(), col_coords.ravel()]).T
    # Truncate to requested amount:
    position = position[:n_plots, :]

    # Manage figure:      
    if fig is None:
        # Adapt figure size to grid extent:
        figsize = plot_size * np.array(grid)[::-1]
        # Range-check calculated size and create figure:
        figsize = np.where(figsize >= 1, figsize, (1, 1))
        figsize = np.where(figsize <= (20, 10), figsize, (20, 10))
        fig = plt.figure(constrained_layout=True, figsize=figsize)

    axes = []
    # Fill grid in the specified order:
    for i, pos in enumerate(position):
        if i == 1:
            # Re-enable shared axes for all other subplots:
            keywords.update({key: axes[0] for key in switch_keys})
        # Add subplot to figure:
        axes.append(plt.subplot2grid(grid, pos, fig=fig, **keywords))
        # Manage outer axis labels:
        if x is not None and i >= n_plots - grid[1]:
            axes[-1].set_xlabel(x)
        if y is not None and pos[1] == 0:
            axes[-1].set_ylabel(y)
    return axes


# COLORS & COLORMAPS:


def remake_cmap(cmap, low=0., high=1., segments=None, n=1000, reverse=False,
                resample=True, name=None):
    """ Truncates colormap or cuts/repeats segments to create a new colormap.

    Parameters
    ----------
    cmap : matplotlib colormap object or str
        Underlying colormap. Accepts both a ready colormap object or a name
        string known to Matplotlib.
    low : float, optional
        Lower bound of the new colormap (in [0,1]) relative to the original. If
        high is not None, low should be < high. Ignored if segments are given.
        The default is 0.0.
    high : float, optional
        Upper bound of the new colormap (in [0,1]) relative to the original. If
        low is not None, high should be > low. Ignored if segments are given.
        The default is 1.0.
    segments : list (m,) of tuples or lists of floats (2,), optional
        Segments to extract from the original colormap and concatenate into the
        new colormap. Each segment must have start and end points in [0,1].
        Allows for repetitions and re-ordering of segments. Overrides low and
        high if specified. The default is None.
    n : int, optional
        Number of color samples to draw from the original colormap. The default
        is 1000.
    reverse : bool, optional
        If True, reverses the order of colors in the new colormap. The default
        is False.
    resample : bool, optional
        If True, restores original number of color samples specified by n
        before returning the new colormap. Takes place after reversing. The
        default is True.
    name : str, optional
        If specified, registers the new colormap under this name in Matplotlib.
        Allows use as standard colormap that is recognized by its name string.
        Takes place after reversing and resampling. The default is None.

    Returns
    -------
    new_cmap : matplotlib colormap object
        Re-structured colormap based on the given cmap.
    """    
    # Input interpretation:
    if isinstance(cmap, str):
        cmap = plt.colormaps.get_cmap(cmap)
    # Draw number of colors:
    colors = cmap(np.linspace(0, 1, n))

    if segments is None:
        # Truncate edges:
        colors = colors[int(n * low):int(n * high), :]
    else:
        # Segment-wise re-structuring:
        cols = []
        for segment in segments:
            start, end = int(n * segment[0]), int(n * segment[1])
            step = 1 if start < end else -1
            cols.append(colors[start:end:step, :])
        colors = np.vstack(cols)
        # cols = [colors[int(n * s[0]):int(n * s[1]):, :] for s in segments]
        # colors = np.vstack(cols)
    new_cmap = ListedColormap(colors)

    if reverse:
        # Reverse order:
        new_cmap = new_cmap.reversed()
    if resample:
        # Restore original resolution:
        new_cmap = new_cmap.resampled(n)
    if name is not None:
        # Add reference by string:
        new_cmap.name = name
        plt.colormaps.register(new_cmap)
    return new_cmap


def color_range(cmap, n, alpha=None, reverse=False, alternate=False,
                shuffle=False, n_near=1, low=None, high=None, segments=None):
    """ Draws given number of colors from the specified colormap.

    Parameters
    ----------
    cmap : matplotlib colormap object or str
        Underlying colormap. Accepts both a ready colormap object or a name
        string known to Matplotlib.
    n : int
        Number of colors to draw from the colormap. Drawn colors are equally
        spaced in cmap and always include the first and last color.
    alpha : float, optional
        If specified, returns colors as RGBA tuples (4,) with this alpha value.
        Adds alpha channel if not present in the colormap. If None, crops alpha
        channel if present and returns RGB tuples (3,). The default is None.
    reverse : bool, optional
        If True, reverses the order of the drawn colors. Takes place before 
        alternating or shuffling. The default is False.
    alternate : bool, optional
        If True, alternates drawn colors by reversing front and back at every
        second index, so that [0, -2, 2, ... , -3, 1, -1]. First and last entry
        is always preserved. If n is odd, the central entry is also preserved.
        Prevents shuffling. The default is False.
    shuffle : bool, optional
        If True, calls spread_shuffle() on the drawn colors to shuffle them
        while avoiding to place a entry next to its n_near neighbours to the
        left and right, respectively. Ignored if alternate is True. The default
        is False.
    n_near : int, optional
        Number of neighbours to avoid when shuffling. Ignored if
        shuffle is False or alternate is True. The default is 1, which
        corresponds to the direct neighbours left and right of each entry.
    low : float, optional
        If specified, passed to remake_cmap() to truncate the original colormap
        to a relative lower bound in [0, 1]. Ignored if segments are given.
        The default is None.
    high : float, optional
        If specified, passed to remake_cmap() to truncate the original colormap
        to a relative upper bound in [0, 1]. Ignored if segments are given.
        The default is None.
    segments : list (m,) of tuples or lists of floats (2,), optional
        If specified, passed to remake_cmap() to reduce the original colormap
        to a set of relative segments in [0, 1]. Overrides low and high if
        given. The default is None.

    Returns
    -------
    colors : list (n,) of tuples of floats (3, or 4, if alpha is not None)
        Drawn colors from cmap as RGB or RGBA tuples in the desired order.
    """    
    # Input interpretation:
    if isinstance(cmap, str):
        cmap = plt.colormaps.get_cmap(cmap)
    if low is not None or high is not None or segments is not None:
        # Optional colormap re-structuring:
        cmap = remake_cmap(cmap, low, high, segments)
    # Draw number of colors:
    colors = cmap(np.linspace(0, 1, n))

    if alpha is None:
        # Crop alpha channel, if present:
        colors = colors[:, :3] if colors.shape[1] == 4 else colors
    elif colors.shape[1] == 4 and alpha < 1 and alpha >= 0:
        # Set non-default value:
        colors[:, 3] = alpha
    elif colors.shape[1] == 3 and alpha >= 0 and alpha <= 1:
        # Add alpha channel with any value:
        colors = np.concatenate((colors, alpha * np.ones((n, 1))), axis=1)
    colors = [tuple(c) for c in colors]

    if reverse:
        # Reverse order:
        colors = colors[::-1]
    if alternate:
        # Alternate from ends towards center: 
        for i in range(1, n // 2 + 1, 2):
            colors[i], colors[-i - 1] = colors[-i - 1], colors[i]
    elif shuffle:
        # Shuffle while avoiding neighbours:
        colors = spread_shuffle(colors, n_near)
    return colors


def sort_colors(colors, sort_start='min', background=(1, 1, 1)):
    """ Sorts a set of RGB(A) colors by minimizing pairwise distances.
        Distances are computed as Euclidean metric and will thus not match the
        actual perceived color difference. Provides several options to specify
        the entry point of the sorting process.

    Parameters
    ----------
    colors : list (m,) of tuples of floats (3 or 4,)
        Set of colors in RGB or RGBA format to sort. If RGBA, omits the alpha
        channel and performs distance computation on a mixture of each color 
        with the given background: color * alpha + background * (1 - alpha). 
    sort_start : str or int or None, optional
        Determines the entry point of the sorting process. Options are 'min' to
        start with the "darkest" color (minimum RGB sum), 'max' to start with
        the "lightest" color (maximum RGB sum), None to choose the first color
        randomly, or a fixed integer index. The default is 'min'.
    background : tuple of floats (3,)
        RGB background color for alpha blending. May not have an alpha channel.
        The default is (1, 1, 1), corresponding to a white background.

    Returns
    -------
    sorted_colors : list (m,) of tuples of floats (3 or 4,)
        Set of colors sorted by pairwise distance minimization. The resulting
        order of colors strongly depends on the chosen entry point and does not
        reflect how an observer percieves the (dis)similarity between colors.
    """    
    # Ensure RGB(A) array format:
    color_array = np.array(colors)
    n = color_array.shape[0]
    # Manage alpha channel:
    if color_array.shape[1] == 4:
        # Ensure simple RGB format:
        alpha = color_array[:, 3]
        # Mix colors with background color:
        color_array = color_array[:, :3] * alpha
        color_array += np.array(background) * (1 - alpha)
    
    # Input interpretation:
    if sort_start == 'min':
        # Pseudo-darkest color first:
        ind = np.argmin(np.sum(color_array, axis=1))
    elif sort_start == 'max':
        # Pseudo-lightest color first:
        ind = np.argmax(np.sum(color_array, axis=1))
    elif sort_start is None:
        # Random entry point:
        ind = np.random.default_rng().integers(0, n)
    else:
        # Sanitize and use specified start:
        ind = np.clip(sort_start, -n, n - 1) 

    # Compute pairwise distance matrix:
    distances = squareform(pdist(color_array, metric='euclidean'))
    distances[np.diag_indices(n)] = np.nan

    # Sort by minimal distance:
    sorted_colors = [colors[ind]]
    distances[ind, :] = np.nan
    for _ in range(n - 1):
        # Find closest remaining neighbor:
        ind = np.nanargmin(distances[:, ind])
        # Log and disable chosen color:
        sorted_colors.append(colors[ind])
        distances[ind, :] = np.nan
    return sorted_colors


def sort_distinctipy(n, sort_start='min', batch=1, gap=0, clean_end=True,
                     **kwargs):
    """ Wrapper to distinctipy.get_colors() to create a categorical color set.
        Generates a number of perceptually distinct colors and sorts them by
        pairwise RGB distance. Can also create and sort a larger color set and
        subsample it into batches of successive colors separated by gaps of
        redundant colors to achieve a grouping effect.

    Parameters
    ----------
    n : int
        Number of colors to generate and sort. If not an integer multiple of
        batch, the number of colors is rounded up to the next multiple.
    sort_start : str or int or None, optional
        Determines the entry point of the sorting process. Options are 'min' to
        start with the "darkest" color (minimum RGB sum), 'max' to start with
        the "lightest" color (maximum RGB sum), None to choose the first color
        randomly, or a fixed integer index. The default is 'min'.
    batch : int, optional
        Number of colors to group together in the returned color subset.
        The default is 1.
    gap : int, optional
        Number of redundant colors between two batches. Not returned in the
        final color subset. The default is 0.
    clean_end : bool, optional
        If True, generates one additional color, sorts all, and removes the
        last of the sorted colors. Ensures that the end point of the final
        color set is based on actual RGB distance to its predecessor and not
        just the last available color. The default is True.
    **kwargs : dict, optional
        Additional keyword arguments passed to distinctipy.get_colors().

    Returns
    -------
    color_subset : list (n,) of tuples of floats (3,)
        Sorted set of perceptually distinct colors in RGB format. If n is not
        an integer multiple of batch, might return more colors than requested.
    """    
    if n % batch:
        # Ensure greater integer multiple:
        n = (n // batch + 1) * batch
    # Expand for later subsampling:
    total = n + (n // batch - 1) * gap

    # Generate a number of distinct colors:
    colors = distinctipy.get_colors(total + clean_end, **kwargs)
    # Sort colors by pairwise RGB distance:
    colors = sort_colors(colors, sort_start)
    if clean_end:
        colors = colors[:-1]

    # Full color set early exit:
    if batch == 1 and gap == 0:
        return colors
    # Subsample colors:
    color_subset = []
    for i in range(0, total, batch + gap):
        color_subset += colors[i : i + batch]
    return color_subset


def mappable_cmap(cmap, low=0., high=1.):
    """ Creates a linear scalar mappable from the specified colormap.
        Enables colorbars with custom mapping of values to colors, and without
        reference to actual image or scatter data. Normalization boundaries
        are the smallest and largest values that will be mapped to colors.
        Defines the ticklabels on the colorbar.

    Parameters
    ----------
    cmap : matplotlib colormap object or str
        Underlying colormap. Accepts both a ready colormap object or a name
        string known to Matplotlib.
    low : float, optional
        Custom lower normalization boundary, corresponding to the first color
        in the colormap (and the smallest mappable value). The default is 0.0.
    high : float, optional
        Custom upper normalization boundary, corresponding to the last color
        in the colormap (and the largest mappable value). The default is 1.0.

    Returns
    -------
    mappable : matplotlib ScalarMappable object
        Scalar mappable object representing the colormap. Can be passed to a
        colorbar function instead of an actual artist, such as an image.
    """    
    # Input interpretation:
    if isinstance(cmap, str):
        cmap = plt.colormaps.get_cmap(cmap)
    # Define mapping of values to colors:
    mappable = ScalarMappable(Normalize(low, high), cmap)
    return mappable


# LEGEND FUNCTIONALITY:


def proxy_handles(labels, iter_kwargs={}, mode='line', **kwargs):
    """ Creates a collection of custom proxy artists for use in a legend.
        Call plt.legend(handles=artists) without labels argument to set the
        proxies as legend entries. Supports Line2D and Patch artist class.

    Parameters
    ----------
    labels : array-like (m,) of strings, floats or ints
        Artist-specific legend labels.
    iter_kwargs : dict of array-likes (m,), optional
        Artist-specific keyword arguments. Must be compatible with the artist 
        class specified by mode. The default is {}.
    mode : str, optional
        The artist class to use for creating the proxies. Options are 'line'
        for Line2D and 'patch' for Patch objects. The default is 'line'.
    **kwargs : dict, optional
        General keyword arguments to apply to all artists. Must be compatible
        with the artist class specified by mode. 

    Returns
    -------
    artists : list of matplotlib Line2D or Patch objects (m,)
        Legend proxy artists with the specified properties and labels.
    """    
    func = {
        'line': Line2D,
        'patch': Patch
    }[mode]

    if mode == 'line':
        kwargs.update({'xdata': [], 'ydata': []})

    artists = []
    for i, label in enumerate(labels):
        artist_kwargs = {key: value[i] for key, value in iter_kwargs.items()}
        artists.append(func(label=label, **artist_kwargs, **kwargs))
    return artists


# PLOT PRE-SETS:


def kill_ax(axes, turn_off=True):
    # TODO docstring
    axes = check_list(axes)
    for ax in axes:
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_xticks([], [])
        ax.set_yticks([], [])
        ax.tick_params('both', length=0, width=0)
        ax.spines[:].set(visible=False, lw=0)
        if turn_off:
            ax.axis('off')
    return None


def ax_box(ax):
    """ Hides all axes, labels, and ticks, but draws the full box of spines.

    Parameters
    ----------
    ax : matplotlib axes object
        Target subplot to frame. 
    """       
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.spines[:].set_visible(True)
    return None


def ax_cross(ax, **kwargs):
    """ Draws horizontal and vertical zero lines in the given subplot.

    Parameters
    ----------
    ax : matplotlib axes object
        Target subplot to add the cross of zero lines.
    **kwargs : dict, optional
        Keyword arguments passed to axhline() and axvline() for customizing the
        zero lines. Defaults to {'c': 'k', 'lw': 0.5, 'ls': 'dotted'} if
        nothing else is provided.
    """    
    if not kwargs:
        kwargs = {'c': 'k', 'lw': 0.5, 'ls': 'dotted'}  
    ax.axhline(0, **kwargs)
    ax.axvline(0, **kwargs)
    return None


def quick_hist(ax, data, n_bins=50, bins=None, density=True, width=0.8,
               **kwargs):
    """ Computes a histogram over the data and plots it to the given subplot.
        Does exactly the same as plt.hist().

    Parameters
    ----------
    ax : matplotlib axes object
        Target subplot to which the bar plot of the histogram is added.
        Axes limits are set to [edges[0], edges[-1]] and [0, max(hist)*1.05]
        for x and y, respectively.
    data : 1D array of floats or ints (m,)
        Data over which the histogram is computed.
    n_bins : int, optional
        Number of bins passed to np.histogram(). Ignored if bins is specified.
        The default is 50. 
    bins : 1D array or list of floats (n,), optional
        Bin edges passed to np.histogram(). Overrides n_bins if specified.
        The default is None.
    density : bool, optional
        Density argument passed to np.histogram(). If True, the histogram is
        normalized to form a probability density. The default is True.
    width : float, optional
        Width of the bars in the bar plot relative to width of each bin. Should
        be in [0, 1]. The default is 0.8.
    **kwargs : dict, optional
        Keyword arguments passed to ax.bar() to specify additional properties.
        The default is {'fc': 'k', 'lw': 0}.

    Returns
    -------
    hist : 1D array of floats (n,)
        Histogram counts or density values for each bin.
    centers : 1D array of floats (n,)
        Bin centers computed from the bin edges.
    edges : 1D array of floats (n + 1,)
        Bin edges corresponding to centers. Returns given bins if specified.
    """    
    if not kwargs:
        kwargs = {'fc': 'k', 'lw': 0}
    # Compute histogram and bin centers:
    hist, edges = np.histogram(data, bins=n_bins if bins is None else bins,
                               density=density)
    bar_widths = edges[1:] - edges[:-1]
    centers = edges[:-1] + 0.5 * bar_widths
    # Add barplot and adjust axes limits:
    ax.bar(centers, hist, width * bar_widths, **kwargs)
    ax.set_xlim(edges[0], edges[-1])
    ax.set_ylim(0, max(hist) * 1.05)
    return hist, centers, edges


def quick_boxplot(ax, data, c_line, c_median=None, c_out=None, lw=2., ms=8.,
                  mew=1.5, alpha=1., alpha_out=None, **kwargs):
    """ Wrapper for plt.boxplot() to quickly create single-color boxplots.
        Applies the given line color and width to all parts of a boxplot (box,
        whiskers, caps) except median and outliers. Accepts any other keyword
        arguments of plt.boxplot().

    Parameters
    ----------
    ax : matplotlib axes object
        Target subplot in which the boxplots are added.
    data : 1D (m,) or 2D (m,n) array of floats or ints or list of arrays
        The data to be represented by boxplots. If 1D, draws a single boxplot.
        If 2D, draws a boxplot for each column. If list, draws a boxplot for
        each array in the list.
    c_line : str
        Color of the box, whiskers, and caps. Also applied to median lines if
        c_median is None, and to face and edge of outliers if c_out is None.
    c_median : str, optional
        If specified, different color for median lines (else c_line). The
        default is None.
    c_out : str or tuple of str (2,), optional
        If specified, different color for face and edge of outliers (else
        c_line). A single string sets both at once. The default is None.
    lw : float or int, optional
        Width of box, whiskers, caps, and median lines in points. The default
        is 2.0.
    ms : float or int, optional
        Size of outlier markers in points. The default is 8.0.
    mew : float or int, optional
        Width of outlier marker edges in points. The default is 1.5.
    alpha : float, optional
        Alpha value of box, whiskers, caps, and median lines in [0, 1]. Also
        applied to outliers if alpha_out is None. The default is 1.0.
    alpha_out : float, optional
        If specified, different alpha value of outliers in [0, 1]. The default
        is None.
    **kwargs : dict, optional
        Additional keyword arguments passed to plt.boxplot() to specify
        properties such as outlier symbols or legend labels.

    Returns
    -------
    b : dict of lists of Line2D objects
        Collection of line artists that represent different boxplot components,
        as returned by plt.boxplot(). 
    """    
    # Input interpretation:
    if isinstance(c_out, str):
        c_out = (c_out, c_out)
    if not kwargs:
        kwargs = {'sym': '+'}
    # Bundle properties:
    line_props = {
        'c': c_line,
        'lw': lw,
        'alpha': alpha
        }
    median_props = {
        'c': c_line if c_median is None else c_median,
        'lw': lw,
        'alpha': alpha
        }
    outlier_props = {
        'mfc': c_line if c_out is None else c_out[0],
        'mec': c_line if c_out is None else c_out[1],
        'alpha': alpha if alpha_out is None else alpha_out,
        'ms': ms,
        'mew': mew
        }
    # Create boxplot:
    b = ax.boxplot(data, boxprops=line_props, whiskerprops=line_props,
                   capprops=line_props, medianprops=median_props,
                   flierprops=outlier_props, **kwargs)
    return b


def cross_plot(array, grid=None, start_row=0, start_col=0, fig=None,
               labels=None, **kwargs):
    """ Plots unique pairs of array columns against each other in an axes grid.
        Subplots are arranged in a triangle shape. Each subplot row corresponds
        to one of the array columns (excluding the last one). The data from
        this column is always treated as independent variable and plotted
        in separate subplots against the data from the following array columns.
        Self-pairs and duplicate pairings are not included. The subplot
        triangle can be placed at different positions in a larger grid by
        specifying the coordinates of its top-left corner. 

    Parameters
    ----------
    array : 2D array of floats or ints (m, n)
        Data to be plotted against each other column-wise. For n array columns,
        there are (n**2 - n) / 2 unique pairings and as many subplots in the
        triangle with n - 1 rows and n - 1 columns.
    grid : tuple of ints (2,), optional
        If specified, determines the axes grid in which all created subplots
        are placed as (rows, columns). If not specified, the grid is set to
        (n - 1, n - 1), so that the subplot triangle fits exactly into it.
        The default is None.
    start_row : int, optional
        Row coordinate of the subplot triangle's top-left corner. Can be used
        to shift the triangle in vertical direction. The default is 0.
    start_col : int, optional
        Column coordinate of the subplot triangle's top-left corner. Can be
        used to shift the triangle in horizontal direction. The default is 0.
    fig : matplotlib figure object, optional
        If specified, creates subplots in this figure according to the given
        grid. If not specified, creates a new figure with constrained_layout.
        The default is None.
    labels : list of str (n,), optional
        Column-specific names to be used as x- and y-axis labels for each
        subplot. If not specified, creates default labels that indicate the 
        corresponding array column as a number in [1, n]. The default is None.
    **kwargs : dict, optional
        Additional keyword arguments passed to plt.plot() for each subplot.
        Defaults to black 'o' markers with white edge and linestyle ''.

    Returns
    -------
    axes = list of matplotlib axes objects
        The created subplots in the triangle in row-wise order (left to right,
        then top to bottom), one for each unique pairing of array columns. All
        axes have the same limits for both x- and y-axis.
    handles = list of matplotlib line objects
        Plot handles corresponding to axes in the same order.

    Raises
    ------
    ValueError
        Breaks if the grid space occupied by a subplot triangle with given
        corner coordinates would exceed the borders of the full grid.
    """    
    # Input interpretation:
    n = array.shape[1]
    if grid is None:
        grid = (n - 1, n - 1)
    if (grid[0] - start_row) < (n - 1) or (grid[1] - start_col) < (n - 1):
        # Break if required space conflicts with borders of subplot grid:
        msg = f'Grid {grid} is too small for subplot triangle with starting '\
              f'coordinates ({start_row}, {start_col}) and size {n - 1}.' 
        raise ValueError(msg)
    if not kwargs:
        kwargs = {'marker': 'o', 'ls': '', 'ms': 5, 'mfc': 'k', 'mec': 'w'}
    if fig is None:
        fig = plt.figure(constrained_layout=True)
    if labels is None:
        labels = [f'dim$_{i}$' for i in range(1, n + 1)]

    # Cross-wise comparison:
    axes, handles = [], []
    for i in range(n):
        # Manage indices of subplots and array columns:     
        for col_ind, j in enumerate(np.arange(n)[i + 1:]):
            # Create subplot at given position in grid:
            ax = plt.subplot2grid(grid, (start_row + i, start_col + col_ind))
            ax.set_xlabel(labels[i])
            ax.set_ylabel(labels[j])
            axes.append(ax)
            # Plot paired data against each other:
            handle = ax.plot(array[:, i], array[:, j], **kwargs)[0]
            handles.append(handle)
    # Define fixed axes limits for all subplots:
    data_limits(array, margins=0.1, axes=axes, which='both')
    return axes, handles


def plot_spectrogram(signal, rate, ax, spec_kwargs, quick_render=True,
                     f_resample=None, t_resample=None, **plot_kwargs):
    """ Computes and displays a spectrogram of the signal in the given subplot.
        Calls spectrogram() for calculation and uses either plt.imshow() or
        plt.pcolormesh() for plotting. Allows to control the balance between
        rendering speed and visual quality of the displayed spectrogram. 

    Parameters
    ----------
    signal : 1D array of floats or ints (m,)
        Signal from which to compute the spectrogram.
    rate : float or int
        Sampling rate of the signal in Hz.
    ax : matplotlib axes object
        Target subplot in which to plot the spectrogram.
    spec_kwargs : dict
        Keyword arguments passed to the spectrogram() wrapper function to
        specify the computation parameters. Obligated to have some content.
    quick_render : bool, optional
        If True, uses plt.imshow() to speed up (re-)rendering at the cost of
        visual quality. Else, uses plt.pcolormesh() to create prettier plots
        with a greatly increased computational overhead. The default is True.
    f_resample : int, optional
        If specified, reduces the spectrogram's frequency axis load by
        downsampling with this factor. Must be > 1. The default is None.
    t_resample : int, optional
        If specified, reduces the spectrogram's time axis load by downsampling
        with this factor. Must be > 1. The default is None.
    **plot_kwargs : dict, optional
        Additional keyword arguments passed to plt.imshow() or plt.pcolormesh()
        to modify default settings, particularly imshow()'s 'interpolation' or
        pcolormesh()'s 'shading', which have a great impact on rendering speed.
        Default interpolation is 'none', default shading is 'flat'.

    Returns
    -------
    freqs : 1D array of floats (n,)
        Frequency axis of the spectrogram in Hz (axis 0 of spectrum).
    times : 1D array of floats (p,)
        Time axis of the spectrogram in s (axis 1 of spectrum).
    spectrum : 2D array of floats (n, p)
        Spectrogram powers in either unit ** 2 / Hz or dB. 
    """    
    # Compute spectrogram:
    f, t, spectrum = spectrogram(signal, rate, **spec_kwargs)

    # Optional downsampling:
    if f_resample is not None:
        # Reduce frequency axis load:
        f, spectrum = f[::f_resample], spectrum[::f_resample, :]
    if t_resample is not None:
        # Reduce time axis load:
        t, spectrum = t[::t_resample], spectrum[:, ::t_resample]

    # Plot spectrogram:
    if quick_render:
        # With plt.imshow():
        plot_settings = {
            'interpolation': 'none',
            'origin': 'lower',
            'aspect': 'auto',
            'extent': [t[0], t[-1], f[0], f[-1]],
            'rasterized': True
            }
        plot_settings.update(plot_kwargs)
        ax.imshow(spectrum, **plot_settings)
    else:
        # With plt.pcolormesh():
        plot_settings = {
            'shading': 'flat',
            'rasterized': True
            }
        plot_settings.update(plot_kwargs)
        if plot_settings['shading'] == 'flat':
            # Ensure shape compatibility:
            spectrum = spectrum[:f.size - 1, :t.size - 1]
        ax.pcolormesh(t, f, spectrum, **plot_settings)
    return f, t, spectrum


# TIME-SERIES VISUALIZATION:


def time_axis(array, rate, axis=0, start=None, end=None, zero_start=True,
              pad=None, pad_start=1, pad_end=1, down_rate=None,
              maximum=None, minimum=None):
    """ Creates a custom time axis over an N-dimensional array of data.
        Initial time axis has given sampling rate and starts at zero. Supports
        cropping to some time frame, downsampling, and capping of data values.

    Parameters
    ----------
    array : N-dimensional array of arbitrary type
        The dataset for which to compute the time axis. The given axis of the
        array must correspond to time, sampled with rate.
    rate : float or int
        Sampling rate of the dataset along the given axis in Hz.
    axis : int, optional
        Dimension of array that corresponds to time. The default is 0.
    start : float or int, optional
        If specified, crops dataset to start at this time in s. If zero_start
        is True, recomputes time axis to start at zero again after cropping.
        The default is None.
    end : float or int, optional
        If specified, crops dataset to end at this time in s. If zero_start is
        True, the last included time point in the time axis changes
        accordingly. The default is None.
    zero_start : bool, optional
        If True, adjusts time axis to start at zero every time it is cropped.
        Else, cuts returned time axis from the initial time axis to match the
        specified time frame (for plotting zoom-ins). The default is True.
    pad : float or int, optional
        If positive, trims edges of dataset in time by some multiples of this
        value in s. Adds to any specified start or end. Set pad_start and
        pad_end to modify the factor of pad at each edge. If zero_start is
        True, recomputes time axis to start at zero again. Meant to apply fixed
        temporal buffers or to skip over filter edge effects. The default is 0.
    pad_start : float or int, optional
        If specified, trims start of dataset in time by pad * pad_start in s.
        If zero_start is True, recomputes time axis to start at zero. Ignored
        if period is zero. The default is None.
    pad_end : _type_, optional
        If specified, trims end of dataset in time by pad * pad_end in s. If
        zero_start is True, the last included time point in the time axis
        changes accordingly. Ignored if period is zero. The default is None.
    down_rate : float or int, optional
        If specified, downsamples cropped or trimmed dataset to this rate in Hz
        and adjusts time axis accordingly. 1D arrays are downsampled with
        interpolation if needed. Multi-dimensional arrays are downsampled by
        simple nth-entry selection with a step size of around rate/down_rate.
        Meant to reduce data load for plotting, not for analysis. The default
        is None.
    minimum : float or int, optional
        If specified, caps entire array to this minimum value. Applies to all
        dimensions. The default is None.
    maximum : float or int, optional
        If specified, caps entire array to this maximum value. Applies to all
        dimensions. The default is None.

    Returns
    -------
    time : 1D array of floats (m,)
        Customized time axis over the returned array in s. Start and end times
        depend on the specified keyword arguments. Always starts at zero and
        encompasses the full given dataset if called with default settings.
    array : N-dimensional array of arbitrary type
        Cropped, trimmed, downsampled, and capped dataset of the same shape as
        the given array. Returns unmodified array if called with default 
        settings.
    """    
    # Create initials:
    array = array.copy()
    time = np.arange(array.shape[axis]) / rate
    # Optional trimming or cropping to time frame:
    if start is not None or end is not None or pad is not None:
        # Argument fallbacks:
        if start is None:
            start = 0
        if end is None:
            end = time[-1]
        if pad is not None:
            # Adjust edges for padding:
            start += pad_start * pad
            end -= pad_end * pad
        # Crop to time frame and optionally recompute axis:
        ind = np.nonzero((time >= start) & (time <= end))[0]
        array = np.take(array, ind, axis=axis)
        time = np.arange(array.shape[axis]) / rate if zero_start else time[ind]
    # Optional downsampling:
    if down_rate is not None:
        if array.ndim == 1:
            # Downsample with interpolation if needed:
            array = downsampling(array, rate, down_rate)
            time = np.arange(len(array)) / down_rate
            if not zero_start:
                # Adjust again:
                time += start
        else:
            # Simple nth-entry selection:
            rate_ratio = int(np.round(rate / down_rate))
            ind = np.arange(0, array.shape[axis], rate_ratio)
            array = np.take(array, ind, axis=axis)
            time = time[ind]
    # Optional capping of data:
    if minimum is not None:
        array[array <= minimum] = minimum
    if maximum is not None:
        array[array >= maximum] = maximum
    return time, array


# TEXT VISUALIZATION:


def text_box(ax, text, xy, width, height, transform=None,
             ha='center', va='center', **kwargs):
    """ Maximizes fontsize of text to fit into a given bounding box.
        Calculated fontsize depends on the aspect ratio of the bounding box,
        the aspect ratio and alignment of the text, and the resolution and size
        of the underlying figure. Text is not updated when resizing the figure.

    Parameters
    ----------
    ax : matplotlib axes object
        Target subplot to annotate the text.
    text : str
        Text to fit into the specified bounding box under the given alignments.
    xy : tuple of floats or ints (2,)
        Text position in the coordinate system specified by transform.
    width : float or int
        Rectangle width in the coordinate system specified by transform.
    height : float or int
        Rectangle height in the coordinate system specified by transform.
    transform : matplotlib transform, optional
        Underlying coordinate system of the bounding box. Determines the
        interpretation of xy, width, and height. Falls back to data coordinates
        if unspecified. The default is None.
    ha : str, optional
        Horizontal alignment of bounding box and text relative to the given xy.
        The default is 'center'.
    va : str, optional
        Vertical alignment of bounding box and text relative to the given xy.
        The default is 'center'.
    **kwargs : dict, optional
        Additional keyword arguments passed to ax.annotate() for specifying
        different font properties of the returned text object.

    Returns
    -------
    t : matplotlib text object
        Annotated text object with adjusted fontsize to fit the bounding box.
    """    
    # Input interpretation:
    if transform is None:
        transform = ax.transData
    fig = ax.get_figure()
    x, y = xy
    # Alignment-specific anchor points:
    x_align1, x_align2 = {
        'center': (x - width / 2, x + width / 2),
        'left': (x, x + width),
        'right': (x - width, x),
    }[ha]
    y_align1, y_align2 = {
        'center': (y - height / 2, y + height / 2),
        'bottom': (y, y + height),
        'top': (y - height, y),
    }[va]
    # Anchor points in pixel:
    left_corner = transform.transform((x_align1, y_align1))
    right_corner = transform.transform((x_align2, y_align2))
    # Bounding rectangle size in pixel:
    pixel_width = right_corner[0] - left_corner[0]
    pixel_height = right_corner[1] - left_corner[1]
    # Adjust fontsize to box height (inch):
    dpi = fig.dpi
    rect_height = pixel_height / dpi
    fs_initial = rect_height * 72
    # Plot first draft of the text:
    t = ax.annotate(text, xy, ha=ha, va=va, xycoords=transform, **kwargs)
    t.set_fontsize(fs_initial)
    # Adjust fontsize to box width (inch):
    bbox = t.get_window_extent(fig.canvas.get_renderer())
    fs_adjusted = fs_initial * pixel_width / bbox.width
    t.set_fontsize(fs_adjusted)
    return t


def text_graph(text, save_str=None, size=None, ax=None, show=False,
               close=False, **kwargs):
    """ Turns entire subplot into a text box that displays the given text.
        Fontsize is maximized to fit the available bounding box. Text is always
        centered in the subplot. Meant for creating scalable text elements that
        comply with the style of other plot elements, especially for posters.

    Parameters
    ----------
    text : str
        Text to be displayed. Can be multiline. Text fontsize is maximized by
        text_box() to fit a bounding box that covers the entire axes area.
    save_str : str, optional
        If specified, saves the underlying figure under the given path. For
        best results, use a vector format such as .svg). The default is None.
    size : tuple of floats or ints (2,), optional
        If specified, creates a new figure with given size in inches and a
        single subplot. Indirectly controls the aspect ratio of the text box.
        Must be specified if ax is None. The default is None.
    ax : matplotlib axes object, optional
        If specified, the target subplot to turn into a text box. Can be used
        to set more properties such as the background color of the text box.
        Must be specified if size is None. The default is None.
    show : bool, optional
        If True, displays the figure before returning. Else, returns without
        showing the figure. The default is False.
    **kwargs : dict, optional
        Keyword arguments passed to text_box() and further to ax.annotate() for
        specifying additional font properties of the displayed text.

    Raises
    ------
    ValueError
        Breaks if neither size nor ax is specified to define a target subplot.
    """    
    # Input interpretation:
    if size is not None:
        fig, ax = plt.subplots(figsize=size)
    elif ax is not None:
        fig = ax.get_figure()
    else:
        raise ValueError('Either size or ax must be specified.')
    # Turn drawable area of axes into a single text box:
    text_box(ax, text, (0.5, 0.5), 1, 1, ax.transAxes, **kwargs)
    # Hide other axes elements:
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.spines[:].set_visible(False)
    # Return options:
    if save_str is not None:
        fig.savefig(save_str, bbox_inches='tight')
    if show:
        plt.show()
    return None


# PRESENTATION FIGURES:


def serial_save(fig, ax_stages, name, x_temp=None, y_temp=None, delimit='_'):
    """ Iteratively saves a figure with different axes revealed at each stage.
        Supports options for synchronized axes so that only one axis bears
        visible axes labels and tick labels at a given stage, which are cleared
        before the next stage. Discouraged for use with shared axes. Instead,
        use sync_axes(hide_labels=False) and empty axes labels before calling
        this function with either the x_temp or the y_temp keyword argument.

    Parameters
    ----------
    fig : matplotlib figure object
        Target figure in the finalized layout before plt.show().
    ax_stages : list (m,) of matplotlib axes objects or lists of axes objects
        Subplots to be revealed at each of the m stages. Saves one file for
        each element in ax_stages, so that the last one shows the full figure.
        Multiple subplots can be bundled to reveal them at once. If given an
        ndarray of axes (Matplotlib standard), converts it to list so that each
        subplot row in the grid is treated as a single stage.
    name : str or list/tuple of str (2,)
        Path template under which all files are saved. Adds a number in [1, m]
        to indicate the current stage in each filename. If given a single
        string, sets tag as last filename component before the file extension.
        If given two string segments, places tag in between. Tags are separated
        from the rest of the filename by the delimit string.
    x_temp : str, optional
        If specified, assumes a synchronized x-axis between certain subplots
        and reveals or hides x-axis labels and tick labels accordingly at each
        stage. Upon revealing a new stage, applies the temporary label to the
        staged subplot. For multiple staged subplots, applies label to the last
        subplot in line and hides the tick labels of the others. After saving
        the given stage, clears temporary label and hides tick labels of all
        staged subplots before revealing the next stage. The default is None.
    y_temp : str, optional
        If specified, assumes a synchronized y-axis between certain subplots
        and reveals or hides y-axis labels and tick labels accordingly at each
        stage. Upon revealing a new stage, applies the temporary label to the
        staged subplot. For multiple staged subplots, applies label to the last
        subplot in line and hides the tick labels of the others. After saving
        the given stage, clears temporary label and hides tick labels of all
        staged subplots before revealing the next stage. The default is None.
    delimit : str, optional
        Delimiter string to separate the stage tag from the rest of name when
        creating the path for each saved figure. The default is '_'.
    """    
    # Input interpretation:
    if isinstance(ax_stages, np.ndarray):
        # Fallback for axes grids:
        ax_stages = ax_stages.tolist()
    else:
        # Assert iterable of iterables:
        ax_stages = check_list(ax_stages)
    ax_stages = [check_list(stage) for stage in ax_stages]
    if isinstance(name, (tuple, list)):
        # Tag between given segments:
        pre_str = name[0] + delimit
        post_str = delimit + name[1]
    else:
        # Tag in last place before extension:
        post_str = '.' + name.split('.')[-1]
        pre_str = name[:-len(post_str)] + delimit
    
    # Initialize by hiding all staged axes:
    [ax.set_visible(False) for ax in flat_list(ax_stages)]
    for i, new_axes in enumerate(ax_stages):
        # Add temporary labels to main axes:
        if x_temp is not None:
            new_axes[-1].set_xlabel(x_temp)
            [ax.set_xticks(ax.get_xticks(), []) for ax in new_axes[:-1]]
        if y_temp is not None:
            new_axes[-1].set_ylabel(y_temp)
            [ax.set_yticks(ax.get_yticks(), []) for ax in new_axes[:-1]]
        # Reveal current stage and save step:
        [ax.set_visible(True) for ax in new_axes]
        fig.savefig(f'{pre_str}{i + 1}{post_str}')
        # Clear temporary labels:
        if x_temp is not None and (i < len(ax_stages) - 1):
            new_axes[-1].set_xlabel('')
            new_axes[-1].set_xticks(new_axes[-1].get_xticks(), [])
        if y_temp is not None and (i < len(ax_stages) - 1):
            new_axes[-1].set_ylabel('')
            new_axes[-1].set_yticks(new_axes[-1].get_yticks(), [])
    return None


# EVENT FUNCTIONS:


def pick_legend(legend_artists, plot_artists, radius=5.):
    """ Makes legend artists pickable and maps them to chosen plot artists.
        Allows to trigger events by clicking on legend artists while the 
        resulting action is applied to the linked plot artists.

    Parameters
    ----------
    legend_artists : Matplotlib legend object or (list of) legend artists (m,)
        Artists of the legend entries to make pickable. Accepts a single handle
        or a list of handles. If given a legend object, extracts all inlcuded
        legend handles as legend.legend_handles.
    plot_artists : plot artist or list (m,) (of lists) of plot artists
        Artists of the plot elements to link to each legend artist. Accepts a
        single handle (if legend_artists is a single handle) or a list of one
        or several handles (one for each legend artist). Number and order of
        provided plot_artists must correspond to legend_artists for correct
        mapping.
    radius : float or int, optional
        Pick radius in points to apply to legend artists that are lines (but
        not patches). The default is 5.0.

    Returns
    -------
    linked_handles : dict
        Mapping of each provided legend artist (keys) to its linked plot
        artists (values). Plot artists are always lists of handles, even if
        only one is linked to a legend artist. If an event is triggered by
        clicking on a specific legend artist, this artist can be used to
        identify all plot artists that should be affected by the action.
    """    
    # Input intepretation:
    if 'Legend' in str(type(legend_artists)):
        legend_artists = legend_artists.legend_handles
    else:
        # Assert iterables:
        legend_artists = check_list(legend_artists)
    plot_artists = check_list(plot_artists)

    linked_handles = {}
    for handle_legend, handle_plot in zip(legend_artists, plot_artists):
        # Make legend artists pickable:
        handle_legend.set_picker(True)
        if 'Line2D' in str(type(handle_legend)):
            handle_legend.set_pickradius(radius)
        # Map legend artists to one or several wrapped plot artists:
        linked_handles[handle_legend] = check_list(handle_plot)
    return linked_handles




