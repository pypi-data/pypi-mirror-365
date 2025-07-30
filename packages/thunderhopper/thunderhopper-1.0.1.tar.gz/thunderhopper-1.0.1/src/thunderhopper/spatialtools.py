import numpy as np
from itertools import combinations
from .misctools import string_series, make_circle
from .arraytools import is_valid_numpy_index, broadcastable, safe_fraction
from .stats import moving_center
from .plottools import setup_fig, color_range


def speed_of_sound(temperature=20., c=None):
    """ Converts between temperature and speed of sound in dry air.
        For the given temperature in degrees Celsius, calculates the speed of
        sound as linear approximation of the actual temperature dependency. If
        a speed measurement is specified instead, estimates the corresponding
        temperature. Valid for temperatures between around -80 and 50 °C.

    Parameters
    ----------
    temperature : float or int, optional
        Air temperature in °C. The default is 20.
    c : float or int, optional
        Speed of sound in m/s. Overrides temperature if specified.
        The default is None.

    Returns
    -------
    c : float
        Speed of sound in dry air at the specified temperature in m/s.
    temperature : float
        Temperature corresponding to the specified speed of sound in °C.
    """
    if c is not None:
        return (c - 331.5) / 0.606  
    return 0.606 * temperature + 331.5


def complete_coordinates(points, index, template=0., n=None):
    """ Validates and standardizes point coordinates to common dimensionality.
        Equalizes inferior coordinate dimensionality (less than n coordinates)
        by inserting the available coordinates at the position given by index
        in an appropriately sized 1D array with values given by template.

    Parameters
    ----------
    points : array-like (m,) of array-likes or floats or ints or None
        Collection of points to be standardized.
    index : int or array-like of ints, optional
        Dimensions at which to insert coordinates of inferior dimensionality.
    template : float or array-like of floats or None, optional
        Value(s) of the 1D array in which to insert coordinates of inferior
        dimensionality. Iterables must be of length n. If None, attempts to
        generate a template from those points that already have n coordinates,
        as long as they are consistent across all dimensions not in index.
        The default is 0.0.
    n : int, optional
        Requested coordinate dimensionality for all points. If None, uses the
        maximum dimensionality found across points. The default is None.

    Returns
    -------
    points : list (m,) of 1D arrays (n,) of floats
        Collection of points in standard format and of common dimensionality.
        Undefined points (Nones) are returned as such.

    Raises
    ------
    ValueError
        Breaks if points have more than n coordinates or are incompatible with
        index. Breaks for negative or out-of-bounds indices. If template is
        None, breaks during template generation if either no points with n
        coordinates are available or if coordinates are inconsistent.
    """    
    # Input interpretation:
    if not isinstance(points, list):
        points = list(points)
    if not is_valid_numpy_index(index) or not np.iterable(index):
        index = np.atleast_1d(index).astype(int)

    # Ensure array format and count dimensions:
    n_dims = np.zeros(len(points), dtype=int)
    for i, point in enumerate(points):
        if point is not None:
            # Handle points with defined coordinates:
            points[i] = np.atleast_1d(point).astype(float)
            n_dims[i] = points[i].size
        else:
            # Undefined coordinates:
            points[i] = np.array([])

    # Manage target:
    max_dims = n_dims.max()
    if n is None:
        n = max_dims
    elif n < max_dims:
        raise ValueError(f'Point dimensionality {max_dims} exceeds '\
                         f'requested coordinate dimensionality {n}.')

    # Equality early exit:
    if n_dims.min() == n:
        return points
        
    # Validate indices for insertion:
    invalid = (index < 0) | (index >= n)
    if any(invalid):
        txt = string_series(index[invalid], prefix=['index', 'indices'])
        raise ValueError(f'Invalid {txt} for requested '\
                         f'coordinate dimensionality {n}.')
    elif any(~np.isin(n_dims, [n, index.size, 0])):
        msg = 'Point dimensionalities must match either the requested '\
             f'coordinate dimensionality {n} or the index size {index.size}.'
        raise ValueError(msg)

    # Prepare insertion:
    if template is None:
        # Get points of sufficient dimensionality:
        completed = np.nonzero(n_dims == n)[0]
        error = 'Failed to generate template for coordinate insertion: '
        if not completed.size:
            raise ValueError(f'{error}No points with requested coordinate '\
                             f'dimensionality {n} available.')

        # Derive fixed coordinate values for unspecified dimensions:
        template = np.mean([points[ind] for ind in completed], axis=0)
        no_index = ~np.isin(np.arange(n), index)
        invalid = template[no_index] != points[completed[0]][no_index]
        if any(invalid):
            invalid = np.arange(n)[no_index][np.nonzero(invalid)[0]]
            txt = string_series(invalid, prefix=['dimension', 'dimensions'])
            raise ValueError(f'{error}Point coordinates are '\
                             f'inconsistent along {txt}.')
        
    # Equalize point dimensionalities:
    for i, point in enumerate(points):
        if point.size == 0:
            points[i] = None
        elif point.size < n:
            points[i] = np.zeros(n) + template
            points[i][index] = point
    return points


def collinear_coordinates(points, axis):
    """ Validates and standardizes point coordinates on a line in 2D space.
        Checks if all points are on a vertical or horizontal line and redefines
        each point as a single coordinate along axis with a common line offset
        along the dimension perpendicular to axis.

    Parameters
    ----------
    points : array-like (m,) of array-likes (1 or 2,) or floats or ints or None
        Collection of points to be standardized.
    axis : int
        Dimension of 2D space along which the points are aligned. Options are
        either 0 (horizontal along x-axis) or 1 (vertical along y-axis).

    Returns
    -------
    points : array-like (m,) of floats or None
        Collection of points defined as single coordinates along axis.
        Undefined points (Nones) are returned as such.
    offset : float
        Common line offset along the dimension perpendicular to axis.
    """
    # Check general coordinate format:
    is_iterable = np.nonzero([np.iterable(point) for point in points])[0]

    # Axis line early exit:
    if not is_iterable.size:
        return [None if p is None else float(p) for p in points], 0.0

    # Check if any points are defined in 2D space:
    is_dual = [i in is_iterable and len(p) > 1 for i, p in enumerate(points)]
    is_dual = np.nonzero(is_dual)[0]

    # Determine line offset:
    if is_dual.size == 0:
        offset = 0.0
    elif is_dual.size == 1:
        # Define offset by only available 2D point:
        offset = float(points[is_dual[0]][1 - axis])
    else:
        # Validate common offset for all available 2D points:
        points = complete_coordinates(points, axis, template=None, n=2)
        offset = points[0][1 - axis]
        return [None if p is None else p[axis] for p in points], offset
    
    # Ensure mutable iterable:
    if not isinstance(points, list):
        points = list(points)

    # Re-define points:
    for i in is_iterable:
        points[i] = points[i][axis] if i in is_dual else points[i][0]
    return [None if p is None else float(p) for p in points], offset


def duplicate_coordinates(points):
    """ Checks if any of the specified point coordinates are identical.
        Duplicate points lead to zero division in most estimation functions.
        All point coordinates must be standardized to common dimensionality. 

    Parameters
    ----------
    points : array-like (m,) of array-likes (1 or 2,) or floats or ints
        Collection of standardized points to be validated. If 1D, checks for
        duplicate values. If 2D, checks for duplicate rows. Lists and tuples
        are converted to arrays, as long as they yield homogenous shapes.

    Returns
    -------
    True or False
        Indicates whether points contains any duplicate coordinates.
    """    
    if np.unique(points, axis=0).shape[0] < len(points):
        print('WARNING: Insufficient spatial information. '\
              'Two or more channels are at the same position.')
        return True
    return False


def estimate_c(p2, p3, p4, t2, t3, t4, p1=0., axis=1, validate=True, y_first=False):
    """ Four-point method to estimate the speed of sound in a microphone array.
        Operates along a linear (horizontal or vertical) microphone array with
        a single reference channel at position p1 and three additional channels
        at positions p2, p3, and p4, which have a measured signal transmission
        delay t2, t3, and t4 relative to reference. Initial runtime from sender
        to reference (or the sender position itself) is not required. The order
        of channel positions (p1, p2, p3, p4) along the array is irrelevant.
        Both the channel positions and the time delays can be negative-valued.
        Accepts channel positions as both 2D and single coordinates, as long as
        all points are on a line in 2D space with an orientation given by axis.

    Parameters
    ----------
    p2 : float or int or array-like (2,) of floats or ints
        Position of channel 2 (first additional channel) along the array in m.
    p3 : float or int or array-like (2,) of floats or ints
        Position of channel 3 (second additional channel) along the array in m.
    p4 : float or int or array-like (2,) of floats or ints
        Position of channel 4 (third additional channel) along the array in m.
    t2 : float or int
        Signal transmission delay between reference and channel 2 in s.
    t3 : float or int
        Signal transmission delay between reference and channel 3 in s.
    t4 : float or int
        Signal transmission delay between reference and channel 4 in s.
    p1 : float or int or array-like (2,) of floats or ints, optional
        Position of channel 1 (reference channel) along the array in m.
        The default is 0.0.
    axis : int, optional
        Dimension of 2D space along which the array is oriented. Options are
        either 0 (horizontal along x-axis) or 1 (vertical along y-axis).
        Ignored if validate is False. The default is 1.
    validate : bool, optional
        If True, calls collinear_coordinates() on p1, p2, p3, and p4 to ensure
        that the orientation of the array is either horizontal or vertical, and
        redefines each point as a single coordinate along axis. If False, all
        channel positions must already be scalar. The default is True.

    Returns
    -------
    sos : float or np.nan
        Estimated speed of sound at the time of recording in m/s. Returns NaN
        if there is no valid solution, supressing any np.sqrt() RuntimeWarning.
        Exits with warning if any of the four channel positions are not unique.
    """
    if validate:
        # Standardize and validate point coordinates:
        (p1, p2, p3, p4), _ = collinear_coordinates([p1, p2, p3, p4], axis)

    # Zero division early exit:
    if duplicate_coordinates([p1, p2, p3, p4]):
        shape = broadcastable(vars=[t2, t3, t4], crash=True)
        return np.full(shape, np.nan)

    # Calculate equation terms:
    s1, s2, s3, s4 = p1**2, p2**2, p3**2, p4**2
    if y_first:
        # Scheduled order of estimation: c -> y -> t1 -> x:
        numerator = t2 * t2 * (s3*p1 - s1*p3 + s1*p4 - s4*p1 + s4*p3 - s3*p4)
        numerator += t2 * t3 * (s1*p2 - s2*p1 + s4*p1 - s1*p4 + s2*p4 - s4*p2)
        numerator += t2 * t4 * (s2*p1 - s1*p2 + s1*p3 - s3*p1 + s3*p2 - s2*p3)

        denominator = t2**3 * t3 * (p4 - p1)
        denominator += t2**3 * t4 * (p1 - p3)
        denominator += t2**2 * t3**2 * (p1 - p4)
        denominator += t2**2 * t4**2 * (p3 - p1)
        denominator += t2**2 * t3 * t4 * (p1 - p2)
        denominator += t2**2 * t3 * t4 * (p2 - p1)
        denominator += t2 * t3**2 * t4 * (p2 - p1)
        denominator += t2 * t3 * t4**2 * (p1 - p2)
    else:
        # Scheduled order of estimation: c -> t1 -> y -> x:
        numerator = t2 * (s1 * (p1*p3 - p1*p4 - p2*p3 + p2*p4) + s3 * (p1*p2 + p1*p4 - p2*p4 - s1) - s4 * (p1*p2 + p1*p3 - p2*p3 - s1))
        numerator += t3 * (s1 * (-p1*p2 + p1*p4 - p2*p4 + s2) + s2 * (-p1*p2 - p1*p4 + p2*p4 + s1) + s4 * (2*p1*p2 - s1 - s2))
        numerator -= t4 * (s1 * (-p1*p2 + p1*p3 - p2*p3 + s2) + s2 * (-p1*p2 - p1*p3 + p2*p3 + s1) + s3 * (2*p1*p2 - s1 - s2))

        denominator = t2**2 * (t4*(p1*p2 + p1*p3 - p2*p3 - s1) - t3*(p1*p2 + p1*p4 - p2*p4 - s1))
        denominator += t3**2 * (t4*(-2*p1*p2 + s1 + s2) - t2*(-p1*p2 - p1*p4 + p2*p4 + s1))
        denominator += t4**2 * (t2*(-p1*p2 - p1*p3 + p2*p3 + s1) - t3*(-2*p1*p2 + s1 + s2))
    # Insert terms and solve equation if possible:
    return np.sqrt(safe_fraction(numerator, denominator, sign=[0, 1]))


def estimate_t1_first(p2, p3, t2, t3, c, p1=0., axis=1, validate=True):
    if validate:
        # Standardize and validate point coordinates:
        (p1, p2, p3), _ = collinear_coordinates([p1, p2, p3], axis)

    # Zero division early exit:
    if duplicate_coordinates([p1, p2, p3]):
        shape = broadcastable(vars=[t2, t3, c], crash=True)
        return np.full(shape, np.nan)

    # Calculate equation terms:
    numerator = (t2 * c)**2 * (p3 - p1)
    numerator += (t3 * c)**2 * (p1 - p2)
    numerator += p1**2 * (p3 - p2) + p2**2 * (p1 - p3) + p3**2 * (p2 - p1)
    denominator = 2 * c**2 * (t2 * (p1 - p3) - t3 * (p1 - p2))
    # Insert terms and solve equation if possible:
    return safe_fraction(numerator, denominator)


def estimate_t1(p2, t2, c, y, p1=0., axis=1, validate=True):
    """ Two-point method to get the initial delay between sender and reference.
        Operates along a linear (horizontal or vertical) microphone array with
        a single reference channel at position p1 and one additional channel at
        position p2 which has a measured signal transmission delay t2 relative
        to reference. Both the channel positions and the time delay can be
        negative-valued. Accepts channel positions as both 2D and single
        coordinates, as long as all points are on a line in 2D space with
        an orientation given by axis.

    Parameters
    ----------
    p2 : float or int or array-like (2,) of floats or ints
        Position of channel 2 (non-reference) along the array in m.
    t2 : float or int
        Signal transmission delay between reference and channel 2 in s.
    y : float or int
        Sender position along the dimension specified by axis in m.
    c : float or int
        Speed of sound at the time of recording in m/s.
    p1 : float or int or array-like (2,) of floats or ints, optional
        Position of channel 1 (reference channel) along the array in m.
        The default is 0.0.
    axis : int, optional
        Dimension of 2D space along which the array is oriented. Options are
        either 0 (horizontal along x-axis) or 1 (vertical along y-axis).
        Ignored if validate is False. The default is 1.
    validate : bool, optional
        If True, calls collinear_coordinates() on p1 and p2 to ensure that the
        orientation of the array is either horizontal or vertical, redefining
        each point as a single coordinate along axis. If False, all channel
        positions must already be scalar. The default is True.

    Returns
    -------
    t1 : float or np.nan
        Initial runtime between sender and reference in s. Returns NaN if there
        is no valid solution, supressing any ZeroDivisionError.
    """    
    if validate:
        # Standardize and validate point coordinates:
        (p1, p2), _ = collinear_coordinates([p1, p2], axis)

    # Zero division early exit:
    if duplicate_coordinates([p1, p2]):
        shape = broadcastable(vars=[t2, c, y], crash=True)
        return np.full(shape, np.nan)

    # Calculate equation terms:
    numerator = 2 * y * (p1 - p2) - p1**2 + p2**2 - (t2 * c)**2
    denominator = 2 * t2 * c**2
    # Insert terms and solve equation if possible:
    return safe_fraction(numerator, denominator)


def estimate_y_first(p2, p3, t2, t3, c, p1=0., axis=1, validate=True):
    if validate:  
        # Standardize and validate point coordinates:
        (p1, p2, p3), _ = collinear_coordinates([p1, p2, p3], axis)

    # Zero division early exit:
    if duplicate_coordinates([p1, p2, p3]):
        shape = broadcastable(vars=[t2, t3, c], crash=True)
        return np.full(shape, np.nan)

    # Calculate equation terms:
    numerator = t2 * (p1**2 - p3**2 + (t3 * c)**2)
    numerator += t3 * (p2**2 - p1**2 - (t2 * c)**2)
    denominator = 2 * t2 * (p1 - p3) - 2 * t3 * (p1 - p2)
    # Insert terms and solve equation if possible:
    return safe_fraction(numerator, denominator)


def estimate_y(p2, t2, c, t1, p1=0., axis=1, validate=True):
    if validate:
        # Standardize and validate point coordinates:
        (p1, p2), _ = collinear_coordinates([p1, p2], axis)

    # Zero division early exit:
    if duplicate_coordinates([p1, p2]):
        shape = broadcastable(vars=[t2, c, t1], crash=True)
        return np.full(shape, np.nan)

    # Calculate equation terms:
    numerator = (t2 * c)**2 + 2 * t1 * t2 * c**2 + p1**2 - p2**2
    denominator = 2 * (p1 - p2)
    # Insert terms and solve equation if possible:
    return safe_fraction(numerator, denominator)


def estimate_x(p2, t2, c, t1, y, p1=0., axis=1, validate=True):

    offset = 0.0
    if validate:  
        # Standardize and validate point coordinates:
        (p1, p2), offset = collinear_coordinates([p1, p2], axis)

    # Zero division early exit:
    if duplicate_coordinates([p1, p2]):
        shape = broadcastable(vars=[t2, c, t1, y], crash=True)
        return np.full(shape, np.nan)

    # Calculate terms of second coordinate:
    adjacent, hypotenuse = abs(y - p2), (t1 + t2) * c

    # Solve equation if Pythagoras holds:
    squared_sides = hypotenuse**2 - adjacent**2
    return np.nan if squared_sides < 0 else np.sqrt(squared_sides) + offset


# def runtime_triangulation(p2, p3, t2, t3, c, p1=0., axis=1, validate=True):
#     """ Three-point method to estimate sender position in a microphone array.
#         Operates along a linear (horizontal or vertical) microphone array with
#         a single reference channel at position p1 and two additional channels
#         at positions p2 and p3, which have a measured signal transmission delay
#         t2 and t3 relative to reference. Initial runtime from the sender to
#         reference is not required. Order of channel positions (p1, p2, p3, p4) 
#         along the array is irrelevant. Both the channel positions and the time
#         delays can be negative-valued. Accepts channel positions as both 2D and
#         single coordinates, as long as all points are on a line in 2D space
#         with an orientation given by axis.

#     Parameters
#     ----------
#     p2 : float or int or array-like (2,) of floats or ints
#         Position of channel 2 (first additional channel) along the array in m.
#     p3 : float or int or array-like (2,) of floats or ints
#         Position of channel 3 (second additional channel) along the array in m.
#     p4 : float or int or array-like (2,) of floats or ints
#         Position of channel 4 (third additional channel) along the array in m.
#     t2 : float or int
#         Signal transmission delay between reference and channel 2 in s.
#     t3 : float or int
#         Signal transmission delay between reference and channel 3 in s.
#     c : float or int
#         Speed of sound at the time of recording in m/s.
#     p1 : float or int or array-like (2,) of floats or ints, optional
#         Position of channel 1 (reference channel) along the array in m.
#         The default is 0.0.
#     axis : int, optional
#         Dimension of 2D space along which the array is oriented. Options are
#         either 0 (horizontal along x-axis) or 1 (vertical along y-axis).
#         Ignored if validate is False. The default is 1.
#     validate : bool, optional
#         If True, calls collinear_coordinates() on p1, p2, and p3 to ensure that
#         the orientation of the array is either horizontal or vertical, and
#         redefines each point as a single coordinate along axis. If False, all
#         channel positions must already be scalar. The default is True.

#     Returns
#     -------
#     (x, y) : tuple (2,) of floats or np.nans
#         Estimated sender position in m. Returns NaN if there is no valid
#         solution, supressing any ZeroDivisionError or np.sqrt() RuntimeWarning.
#         Order of the two coordinates is determined by axis, not variable names.
#     """    
#     offset = 0.0
#     if validate:  
#         # Standardize and validate point coordinates:
#         (p1, p2, p3), offset = collinear_coordinates([p1, p2, p3], axis)

#     # Zero division early exit I:
#     if duplicate_coordinates([p1, p2, p3]):
#         return (np.nan, np.nan)

#     # Calculate terms of first coordinate:
#     numerator = t2 * (p1**2 - p3**2 + (t3 * c)**2)
#     numerator += t3 * (p2**2 - p1**2 - (t2 * c)**2)
#     denominator = 2 * t2 * (p1 - p3) - 2 * t3 * (p1 - p2)

#     # Zero division early exit II:
#     if denominator == 0:
#         return (np.nan, np.nan)

#     # Solve first coordinate:
#     y = numerator / denominator

#     # Calculate terms of second coordinate:
#     t1 = estimate_t1(p2, t2, y, c, p1, axis, validate=False)
#     adjacent, hypotenuse = y - p2, (t1 + t2) * c

#     # Solve second coordinate, if Pythagoras holds:
#     squared_sides = hypotenuse**2 - adjacent**2
#     x = np.nan if squared_sides < 0 else np.sqrt(squared_sides) + offset
#     return (x, y) if axis else (y, x) 


# def multi_triangulation(positions, times, c, p1=0., axis=1, validate=True):
#     """ Three-point sender estimation on different channel combinations.
#         Operates along a linear (horizontal or vertical) microphone array with
#         a single reference channel at position p1 and at least two additional
#         channels at the given positions, with a measured signal transmission
#         delay relative to reference per channel. Calls runtime_triangulation()
#         on each unique two-channel combination to estimate a value. Both the
#         channel positions and the time delays can be negative-valued. Accepts
#         channel positions as both 2D and single coordinates, as long as all
#         points are on a line in 2D space with an orientation given by axis.

#     Parameters
#     ----------
#     positions : array-like (m,) of (array-likes (2,)) of floats or ints
#         Positions of additional (non-reference) channels along the array in m.
#     times : array-like (m,) of floats or ints
#         Signal transmission delays between reference and each channel in s.
#     p1 : float or int or array-like (2,) of floats or ints, optional
#         Position of channel 1 (reference channel) along the array in m.
#         The default is 0.0.
#     axis : int, optional
#         Dimension of 2D space along which the array is oriented. Options are
#         either 0 (horizontal along x-axis) or 1 (vertical along y-axis).
#         Ignored if validate is False. The default is 1.
#     validate : bool, optional
#         If True, calls collinear_coordinates() on p1 and all points to ensure
#         that the orientation of the array is either horizontal or vertical, and
#         redefines each point as a single coordinate along axis. If False, all
#         channel positions must already be scalar. The default is True.

#     Returns
#     -------
#     positions : 2D array (binom(m, 2), 2) of floats or np.nans
#         Estimated sender positions in m. Returns NaN if there is no valid
#         solution, supressing any ZeroDivisionError or np.sqrt() RuntimeWarning.

#     Raises
#     ------
#     ValueError
#         Breaks if less than two additional channels are specified, or if the
#         number of specified channels does not match the number of time delays.
#     """    
#     # Input validation:
#     if len(positions) < 2:
#         msg = 'Specify at least two channels plus a single initial one.'
#         raise ValueError(msg)
#     if len(positions) != len(times):
#         raise ValueError('Specify one time difference per channel position.')

#     offset = 0.0
#     if validate:
#         # Standardize and validate point coordinates:
#         positions, offset = collinear_coordinates([p1, *positions], axis)
#         p1, positions = positions[0], positions[1:]

#     # Generate unique two-channel combinations:
#     combinations = list(itertools.combinations(range(len(positions)), 2))

#     # Combination-wise estimation:
#     sender = np.zeros((len(combinations), 2))
#     for ind, (i1, i2) in enumerate(combinations):
#         p2, p3 = positions[i1], positions[i2]
#         t2, t3 = times[i1], times[i2]
#         sender[ind, :] = runtime_triangulation(p2, p3, t2, t3, c, p1,
#                                                axis, validate=False)
#     sender[:, 1 - axis] += offset
#     return positions


def filter_estimates(estimates, groups, full_return=False):
    """ Checks which inputs are most likely responsible for unsolved equations.
        Following combination-wise estimation of some variable, gets all input
        combinations that produced NaN estimates and ranks the associated group
        members by frequency of occurence in unsolved equations relative to the
        total occurence in groups. Iterates over most frequent members until
        all unsolved equations can be linked to at least one responsible input.

    Parameters
    ----------
    estimates : list or tuple or 1D array (m,) of floats or ints or np.nans
        Estimated variable for each group, as returned by combi_estimation().
        All invalid outputs must be marked as NaN. No other values supported.
    groups : 2D array (m, n) of floats or ints
        Unique combinations of n inputs, as returned by combi_estimation().
    full_return : bool, optional
        If True, returns the subset of valid estimates and corresponding groups
        in addition to the remaining group members. The default is False.

    Returns
    -------
    estimates : 1D array (q,) of floats or ints, optional
        Subset of valid estimates, equal to estimates[~np.isnan(estimates)].
        Returned in first place if full_return is True, else omitted.
    groups : 2D array (q, n) of floats or ints, optional
        Subset of valid groups, equal to groups[~np.isnan(groups)].
        Returned in second place if full_return is True, else omitted.
    members : 1D array (p,) of floats or ints
        Remaining unique group members, likely not linked to any NaN estimates.
    """    
    # Identify unsolved equations:
    nan_inds = np.isnan(estimates)
    nan_groups = groups[nan_inds]

    # Count occurences of each unique member across all groups:
    all_members, all_counts = np.unique(groups, return_counts=True)

    # All valid early exit:
    if not nan_groups.size:
        return (estimates, groups, all_members) if full_return else all_members

    # Count occurences of unique members across NaN-associated groups:
    nan_members, nan_counts = np.unique(nan_groups, return_counts=True)

    # Sort members by frequency of occurence in descending order:
    ratios = nan_counts / all_counts[np.isin(all_members, nan_members)]
    nan_members = nan_members[np.argsort(ratios)][::-1]

    # Omit frequent members until no unsolved equations remain:
    explained = np.zeros(nan_groups.shape[0], dtype=bool)
    valid_members = all_members.tolist()
    for entry in nan_members:
        if explained.all():
            break
        explained[(nan_groups == entry).any(axis=1)] = True
        valid_members.remove(entry)
    valid_members = np.array(valid_members)

    # Return options:
    if full_return:
        valid = ~nan_inds
        return estimates[valid], groups[valid], valid_members
    return valid_members


def combi_estimation(positions, delays, mode, p1=0., axis=1, validate=True,
                     filtered=False, **kwargs):
    """ General micarray variable estimation by different channel combinations.
        Operates along a linear (horizontal or vertical) microphone array with
        a single reference channel at position p1 and a number of additional
        channels at the given positions, with a measured signal transmission
        delay relative to reference for each channel. Repeatedly calls the
        specified estimation function on each unique n-channel combination of
        positions and times to estimate a value. Both the channel positions and
        the time delays can be negative-valued. Accepts channel positions as
        both 2D and single coordinates, as long as all points are on a line in
        2D space with an orientation given by axis.

    Parameters
    ----------
    positions : array-like (m,) of (array-likes (2,)) of floats or ints
        Positions of additional (non-reference) channels along the array in m.
    delays : array-like (m,) of floats or ints
        Signal transmission delays between reference and each channel in s.
    mode : str
        Estimation function to call. Options are 'init' for estimate_init(),
        'x' for estimate_x(), 'y' for estimate_y(), 'sos' for estimate_sos().
    p1 : float or int or array-like (2,) of floats or ints, optional
        Position of channel 1 (reference channel) along the array in m.
        The default is 0.0.
    axis : int, optional
        Dimension of 2D space along which the array is oriented. Options are
        either 0 (horizontal along x-axis) or 1 (vertical along y-axis).
        Ignored if validate is False. The default is 1.
    validate : bool, optional
        If True, calls collinear_coordinates() on p1 and positions to ensure
        that the orientation of the array is either horizontal or vertical, and
        redefines each point as a single coordinate along axis. If False, all
        channel positions must already be scalar. The default is True.
    filtered : bool, optional
        If True, calls filter_estimates() on the resulting estimates to check
        for NaN outputs (unsolved equations) and identify responsible channels.
        Returns the valid subsets of estimates and groups and the indices of
        remaining channels after filtering. The default is False.
    **kwargs : dict, optional
        Additional keyword arguments required by the estimation function.

    Returns
    -------
    estimates : 1D array (p,) of floats or ints (or np.nans)
        Estimated variable for each channel combination in groups. Invalid
        outputs are removed if filtered is True, else marked as NaN.
    groups : 2D array (p, n) of ints
        Unique combinations of n channel indices, corresponding to estimates.
    indices : 1D array (q,) of ints, optional
        Unique channel indices along positions, consistent with groups.
        Only returned if filtered is True.

    Raises
    ------
    ValueError
        Breaks if the number of given channel positions is insufficient for the
        requested estimation function, or if the number of positions does not
        match the number of specified time delays.
    """
    # Input interpretation:
    func, n = {
        'x': (estimate_x, 1),
        't1': (estimate_t1, 1),
        'y': (estimate_y, 1),
        't1_first': (estimate_t1_first, 2),
        'y_first': (estimate_y_first, 2),
        'c': (estimate_c, 3),
    }[mode]

    # Input validation:
    if len(positions) < n:
        msg = f'Specify at least {n} channels in addition to the reference.'
        raise ValueError(msg)
    if len(positions) != len(delays):
        raise ValueError('Specify one signal transmission delay per channel.')

    if validate:
        # Standardize and validate point coordinates:
        positions, _ = collinear_coordinates([p1, *positions], axis)
        p1, positions = positions[0], positions[1:]

    # Ensure iterable-indexable format:
    if not isinstance(positions, np.ndarray):
        positions = np.array(positions)
    if not isinstance(delays, np.ndarray):
        delays = np.array(delays)

    # Generate unique n-channel combinations (excluding reference):
    groups = np.array(list(combinations(range(positions.size), n)))

    # Combination-wise estimation:
    estimates = np.zeros(groups.shape[0])
    for i, group in enumerate(groups):
        estimates[i] = func(*positions[group], *delays[group], p1=p1,
                            axis=axis, validate=False, **kwargs)
    # Return options:
    if filtered:
        return filter_estimates(estimates, groups, full_return=True)
    return estimates, groups, np.arange(positions.shape[0])


def analyze_micarray(positions, delays, p1=0, axis=1, validate=True,
                     y_first=True, filtered=True, strict_filter=False,
                     condense_c=False, n_close=5, error={}):

    offset = 0.0
    if validate:
        # Standardize and validate point coordinates:
        positions, offset = collinear_coordinates([p1, *positions], axis)
        p1, positions = positions[0], positions[1:]

    # Ensure iterable-indexable format:
    if not isinstance(positions, np.ndarray):
        positions = np.array(positions)
    if not isinstance(delays, np.ndarray):
        delays = np.array(delays)

    # Prepare general estimation arguments:
    args = dict(p1=p1, axis=axis, validate=False)
    combi_args = args | dict(filtered=filtered, y_first=y_first)

    # Estimate speed of sound:
    sos, groups, valid = combi_estimation(positions, delays, 'c', **combi_args)
    if strict_filter:
        inds = np.isin(groups, valid).all(axis=1)
        sos, groups = sos[inds], groups[inds]
    if condense_c:
        inds, _ = moving_center(sos, np.median, iterations=sos.size - n_close)
        sos, groups = sos[inds], groups[inds]

    # Initialize output storage:
    shape = (groups.shape[0], len(error) + 1) if error else (groups.shape[0])
    t1, y, x = [np.zeros(shape) for _ in range(3)]

    # Run downstream pipeline:
    channels = list(error.keys())
    for i in range(len(error) + 1):
        times = delays.copy()
        if i:
            # Update specific channel delay with fixed error:
            channel, deviation = channels[i - 1], error[channels[i - 1]]
            times[channel] += deviation

        # Focus on channel combinations with valid speed estimates:
        for j, (c, group) in enumerate(zip(sos, groups)):

            # Ensure to include error:
            if i and channel in group:
                group = np.roll(group, -np.nonzero(group == channel)[0][0])

            # Select channel subset:
            p, t = positions[group], times[group]
            # Map to storage index:
            ind = (j, i) if error else j

            if y_first:
                # Estimate y-coordinate of sender:
                y[ind] = estimate_y_first(*p[:-1], *t[:-1], c=c, **args)
                # Estimate initial runtime:
                t1[ind] = estimate_t1(*p[:-2], *t[:-2], c=c, y=y[ind], **args)
            else:
                # Estimate initial runtime:
                t1[ind] = estimate_t1_first(*p[:-1], *t[:-1], c=c, **args)
                # Estimate y-coordinate of sender:
                y[ind] = estimate_y(*p[:-2], *t[:-2], c=c, t1=t1[ind], **args)

            # Estimate x-coordinate of sender:
            x[ind] = estimate_x(p[0], t[0], c=c, t1=t1[ind], y=y[ind], **args)
    x += offset
    return sos, y, t1, x, groups


def plot_micarray(points, ref=0, axis=1, ax=None, mirror=False, cross=True,
                  path=False, circle=False, radii=None, delays=None, c=None,
                  t1=None, sender=None, sender_x=None, sender_y=None, groups=None, error={},
                  array_kwargs={}, ref_kwargs={}, sender_kwargs={},
                  cross_kwargs={}, plot_kwargs={}, **kwargs):

    # Standardize and validate point coordinates:
    points = np.array(complete_coordinates(points, axis, n=2))
    if sender is not None:
        sender = complete_coordinates([sender], axis, template=np.zeros(2))[0]

    # Unpack reference channel and array coordinates:
    p1, array_x, array_y = points[ref, :], points[:, 0], points[:, 1]

    # Hierarchical input validation and completion:
    if radii is not None and len(radii) != points.shape[0]:
        msg = 'Specify one radius for each channel, including reference.'\
             f' Expected {points.shape[0]}, got {len(radii)}.'
        raise ValueError(msg)
    elif radii is None and delays is not None: 
        if len(delays) != points.shape[0] - 1:
            msg = 'Specify one delay for each non-reference channel.'\
                f' Expected {points.shape[0] - 1}, got {len(delays)}.'
            raise ValueError(msg)
        elif any([variable is None for variable in (c, t1, sender)]):
            # Estimate missing parameters, overriding any user input:
            out = analyze_micarray(array_y if axis else array_x, delays,
                                   p1[axis], axis, error=error, validate=False, **kwargs)
            c, sender_y, t1, sender_x, groups = out
        if np.isscalar(t1):
            radii = (np.insert(delays, ref, 0.0) + t1) * c
        else:
            radii = (np.insert(delays, ref, 0.0)[:, None] + t1) * c
    if (circle or path) and radii is None and sender is not None:
        # Mimic ideal signal transmission from sender:
        radii = np.linalg.norm(sender - points, axis=1)    

    # Define default plot arguments and update with user settings:
    cross_kwargs = dict(c='k', ls='dotted', lw=1, zorder=1) | cross_kwargs
    array_kwargs = dict(marker='o', ms=10, ls='-', lw=3, zorder=2,
                        c='k', mfc='w', mec='k') | array_kwargs | plot_kwargs
    ref_kwargs = dict(marker='o', ms=10, ls='', zorder=3,
                      c='k', mfc='k', mec='k') | ref_kwargs | plot_kwargs
    sender_kwargs = dict(marker='o', ms=10, ls='', zorder=4,
                         c='k', mfc='r', mec='k') | sender_kwargs | plot_kwargs

    # Manage subplot:
    if ax is None:
        _, ax = setup_fig(width=20, height=20, layout='constrained')

    # Plot microphone array:
    ax.plot(array_x, array_y, **array_kwargs)
    ax.plot(*p1, **ref_kwargs)
    if cross:
        # Indicate coordinate system:
        ax.axhline(0, **cross_kwargs)
        ax.axvline(0, **cross_kwargs)

    # Plot sender position:
    if sender is not None:
        ax.plot(*sender, **sender_kwargs)
        if mirror:
            # Account for symmetry:
            other_sender = sender.copy()
            other_sender[1 - axis] *= -1
            ax.plot(*other_sender, **sender_kwargs)

    if error:
        colors = ['k'] + color_range('turbo', len(error))

    if groups is not None:

        for i, group in enumerate(groups):
            # Plot perimeter around each channel:
            if circle and radii is not None:
                for r, p in zip(radii[group, i], points[group]):
                    if mirror:
                        # Draw full circle around each channel:
                        circle_x, circle_y = make_circle(r, *p, full=True)
                    else:
                        # Reduce to half-circle divided by axis:
                        circle_y, circle_x = make_circle(r, *p[::-1])
                    ax.plot(circle_x, circle_y, c=colors[i], lw=1)
            # Plot estimated sender positions:
            if sender_x is not None and sender_y is not None:
                ax.plot(sender_x[i], sender_y[i], c=colors[i], **plot_kwargs)
                if mirror:
                    coords = [sender_x[i], sender_y[i]]
                    coords[1 - axis] *= -1
                    ax.plot(*coords, c=colors[i], **plot_kwargs)
        return ax

    # Plot estimated sender positions:
    if sender_x is not None and sender_y is not None:
        ax.plot(sender_x, sender_y, **plot_kwargs)
        if mirror:
            coords = [sender_x, sender_y]
            coords[1 - axis] *= -1
            ax.plot(*coords, **plot_kwargs)

    # Plot perimeter around each channel:
    if circle and radii is not None:
        for radius, point in zip(radii, points):
            if mirror:
                # Draw full circle around each channel:
                circle_x, circle_y = make_circle(radius, *point, full=True)
            else:
                # Reduce to half-circle divided by axis:
                circle_y, circle_x = make_circle(radius, *point[::-1])
            ax.plot(circle_x, circle_y, c='k', lw=1)

    # Indicate signal transmission:
    # if path and sender is not None:
    #     sender_coords = np.repeat(sender[None, :], points.shape[0], axis=0)
    #     x, y = np.concatenate((points, sender_coords))
    #     x_coords = np.concatenate((sender_coords[:, 0], array_x))
    #     y_coords = np.concatenate((sender_coords[:, 1], array_y))
    return ax


# def aim_micarray(distance, offset=None, delay=None, angled=False):
#     """ Converts between signal transmission delay and offset sender position.
#         For a given distance between two channels along a linear microphone
#         array, links the time difference between first and second channel to an
#         offset in sender position, assuming that the sender resides on a line
#         orthogonal to the array at the point of the first channel. Can accept
#         and return offset as either distance between sender and first channel,
#         or as angle between the array and the direction of the sender. If the
#         sender is right at the first channel (offset = 0), the delay is given
#         by distance / speed_of_sound, and increases for larger offsets.

#     Parameters
#     ----------
#     distance : float or int
#         Distance along the microphone array between the two channels in m.
#     offset : float or int, optional
#         If specified, offset in sender position in either m or °. Requests
#         the corresponding delay. The default is None.
#     delay : float or int, optional
#         If specified, time difference between first and second channel in s.
#         Requests the corresponding offset. The default is None.
#     angled : bool, optional
#         If True, interprets offset as angle between array and sender at the
#         point of the second channel, else as distance between array and sender
#         at the point of the first channel. Applies to both argument and return.
#         The default is False.

#     Returns
#     -------
#     delay : float or int, optional
#         If offset is specified, returns the corresponding delay in s.
#     offset : float or int, optional
#         If delay is specified, returns the corresponding offset in m or °.
#     """    
#     # Input interpretation:
#     if angled and offset is not None:
#         offset = np.tan(np.radians(offset)) * distance

#     if offset is not None:
#         # Compute corresponding time delay:
#         return distance / speed_of_sound * np.sqrt(1 + (offset / distance)**2)
        
#     if delay is not None:
#         # Compute corresponding sender offset:
#         output =  np.sqrt((delay * speed_of_sound)**2 - distance**2)
#         return np.degrees(np.arctan(output / distance)) if angled else output

