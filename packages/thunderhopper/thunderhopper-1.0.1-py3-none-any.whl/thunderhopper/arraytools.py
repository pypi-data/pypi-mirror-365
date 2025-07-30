import numpy as np
from .misctools import string_series, equal_sequences


## CHECKS & VALIDATION ##


def is_valid_numpy_index(ind):
    """ Checks if the given variable is valid for indexing numpy arrays.
        Valid array indices can be integers, bools, arrays of ints or bools,
        slice objects, ellipsis, None, or tuples of a combination of those.

    Parameters
    ----------
    ind : any type (any shape)
        The variable to validate as numpy array index.

    Returns
    -------
    valid : bool
        Returns True if ind can be used to index numpy arrays, False otherwise.
    """
    # Force dimension specificity:    
    if not isinstance(ind, tuple):
        ind = (ind,)

    for dim in ind:
        # Validate indices along each array dimension separately:
        data_type = type(dim) if not isinstance(dim, np.ndarray) else dim.dtype
        is_int = np.issubdtype(data_type, np.integer)
        is_bool = np.issubdtype(data_type, np.bool_)
        is_slice = isinstance(dim, slice)
        # Type violation early exit:
        if not any([is_int, is_bool, is_slice, dim is Ellipsis, dim is None]):
            return False
    return True


def broadcastable(*shapes, vars=None, crash=False, output=True):
    """ Checks if the given array shapes are broadcastable to a common shape.
        Upon failure, can either return normally or immediately raise an error. 
        Can return the common shape expected from operations with these arrays.

    Parameters
    ----------
    shapes : array-like (m,) of array-likes of ints, optional
        Array shapes to be validated. The default is None.
    vars : array-like (m,) of arrays, floats or ints, optional
        Variables whose shapes are to be validated. Overrides shapes if given.
        Only accepts ndarrays and scalars. The default is None.
    crash : bool, optional
        If True, failed broadcasting raises a ValueError, while successful
        broadcasting returns shape without valid. If False, always returns
        valid, together with shape if output is True. The default is False.
    output : bool, optional
        If True, returns the common shape of the arrays in addition to valid.
        Ignored if crash is True. The default is True.

    Returns
    -------
    valid : bool
        Returns True if all array shapes are broadcastable to a common shape.
        Only returned if crash is False.
    shape : tuple of ints, optional
        Array shape resulting from broadcasting. Bullshit if valid is False.
        Only returned if output is True.
    """    
    # Input interpretation:
    if vars is not None:
        shapes = [(1,) if np.isscalar(var) else var.shape for var in vars]

    # Check array dimensionality:
    dims = np.array([len(shape) for shape in shapes])
    reference = np.array(shapes[np.argmax(dims)])

    # Align shapes by trailing dimensions:
    aligned = np.ones((dims.size, dims.max()), dtype=int)
    for i, shape in enumerate(shapes):
        aligned[i, -dims[i]:] = shape

    # Check if sizes of each dimension are compatible:
    valid = ((aligned == reference) | (aligned == 1) | (reference == 1)).all()
    common_shape = tuple(aligned.max(axis=0))

    # Return options:
    if crash and not valid:
        msg = f'Array shapes {string_series(shapes, delimit=" ")} '\
               'are not broadcastable to a common shape.'
        raise ValueError(msg)
    elif crash:
        return common_shape
    return (valid, common_shape) if output else valid


## ARRAY MANIPULATION (VIEW) ##


def reduce_array(array, squeeze=False, unpack=False):
    """ Wrapper to quickly squeeze and itemize numpy arrays, if possible.
        Allows to remove singleton dimensions (squeeze, maintains at least 1D)
        and to convert single-entry arrays into scalar output (unpack). 

    Parameters
    ----------
    array : ND-array of arbitrary type and shape
        Array to be shape-checked and reduced to simpler formats, if possible.
        Must be at least 1D. Array is not copied or modified by this function.
    squeeze : bool, optional
        If True, calls np.squeeze() on array to remove dimensions of size 1. If 
        array is size 1, retains a single dimension to prevent 0D output. The
        default is False.
    unpack : bool, optional
        If True and output would be an array of size 1, converts the array into
        a single scalar. Applied after squeezing. The default is False. 

    Returns
    -------
    array : 1D...ND-array or scalar of array.dtype
        View of input array after dimensional pruning and scalar conversion.
        If squeeze is True, may have fewer dimensions (down to 1D). If unpack
        is True, may be converted to a scalar. If input array has no singleton
        dimensions and is not size 1, the output is the same as the input. If
        squeeze and unpack are both False, immediately returns the input array.
    """
    # Optional dimensional pruning:
    if squeeze and array.ndim > 1:
        # Remove all singleton dimensions, retaining at least 1D:
        axes = (ind for ind, size in enumerate(array.shape)[1:] if size == 1)
        array = np.squeeze(array, axis=axes)
    # Optional scalar conversion of single-entry 1D arrays:
    return array.item() if (unpack and array.size == 1) else array


def slice_index(dims, axis=0, start=None, stop=None, step=1, include=False):
    """ Indices to slice an N-dimensional array along one or multiple axes.
        Shamelessly stolen and adapted from scipy.signal._arraytools.

    Parameters
    ----------
    dims : int
        Number of dimensions of the target array.
    axis : int or tuple/list/1D array of ints (m,), optional
        Target axis or axes along which to slice the array. If several, enables
        multi-dimensional slicing, also accepting sequence-like inputs for each
        of start, stop, and step. Single elements apply to all target axes.
        The default is 0.
    start : int or tuple/list/1D array of ints (m,), optional
        Inclusive start index of the slice. The default is None.
    stop : int or tuple/list/1D array of ints (m,), optional
        Stop index of the slice. Inclusive if include is True, otherwise
        exclusive as by standard python doctrine. The default is None.
    step : int or tuple/list/1D array of ints (m,), optional
        Step size between indices in the slice. The default is 1.
    include : bool, optional
        If True, makes the specified stop the last index of the slice.
        The default is False.

    Returns
    -------
    slice_inds : tuple of slice objects (dims,)
        Indices for slicing along the given target axes.
    """
    # Ensure 1D sequence-likes of equal length:
    axis, start, stop, step = equal_sequences(axis, start, stop, step,
                                              skip_None=False)

    # Full slice along each dimension:
    slice_inds = [slice(None)] * dims
    for ax, first, last, interval in zip(axis, start, stop, step):
        if include and last is not None:
            # Ensure inclusive stop:
            step_sign = np.sign(interval)
            # Sanitize edge cases (specific combinations of stop and step):
            if any(np.isin([-1, 0], last) & np.isin([1, -1], step_sign)):
                last = None
            else:
                # One more or less:
                last += step_sign
        # Adjust slice along each target axis:
        slice_inds[ax] = slice(first, last, interval)
    return tuple(slice_inds)


def array_slice(array, axis=0, start=None, stop=None, step=1,
                include=False, squeeze=False, unpack=False):
    """ Slices an N-dimensional array along one or multiple target axes.
        Returns a view of the sliced input array, preserving dimensionality.
        Sliced arrays can optionally be squeezed to remove excess singleton
        dimensions. Single-entry arrays can further be converted to scalars.
        Shamelessly stolen and adapted from scipy.signal._arraytools.

    Parameters
    ----------
    array : ND-array of arbitrary type and shape
        Input array to be sliced.
    axis : int or list of ints (m,), optional
        Target axis or axes along which to slice the array. If several, enables
        multi-dimensional slicing, also accepting list inputs for start, stop,
        and step (integer inputs apply to all target axes). The default is 0.
    start : int or list of ints (m,), optional
        Inclusive start index of the slice. The default is None.
    stop : int or list of ints (m,), optional
        Stop index of the slice. Inclusive if include is True, otherwise
        exclusive as by standard python doctrine. The default is None.
    step : int or list of ints (m,), optional
        Step size between indices in the slice. The default is 1.
    include : bool, optional
        If True, makes the specified stop the last index of the slice.
        The default is False.
    squeeze : bool, optional
        If True, calls np.squeeze() on the sliced array to remove dimensions of
        size 1, retaining at least a single dimension. The default is False.
    unpack : bool, optional
        If True and output would be an array of size 1, converts the array into
        a single scalar. Applied after squeezing. The default is False.

    Returns
    -------
    sliced : array of array.dtype or scalar of array.dtype
        View of the sliced array with as many dimensions as the input array.
        If squeeze is True, may have less dimensions (but will be at least 1D).
        If unpack is True, may be a scalar instead of an array.
    """
    slice_inds = slice_index(array.ndim, axis, start, stop, step, include)
    return reduce_array(array[slice_inds], squeeze, unpack)


def remap_array(array, axes_map, dims=None, shape=None,
                invert=False, pass_scalars=False, validate=True):
    """ Freely adds and moves array dimensions without changing the data.
        Consists of a call to np.expand_dims() to match the required target
        dimensionality, followed by np.moveaxis() to position the specified
        input dimensions at the requested output dimensions. Allows to undo a
        previous reshape operation based on the used axes_map input and the
        original dimensionality using np.moveaxis() and np.squeeze().

    Parameters
    ----------
    array : ND array of any type (any shape)
        Input array to be reshaped.
    axes_map : dict {ints: ints} or 1D array-like (>=array.ndim,) of ints
        Index mapping linking input dimensions to their respective output
        dimension. If dict, moves only the input dimensions specified by the
        keys while maintaining order of the remaining dimensions. Otherwise,
        expects at least as many output dimensions as array.ndim, one for each
        array dimension in original order, or more to add singleton dimensions. 
        Input dimensions must be unique and in [-array.ndim, array.ndim - 1].
        Output dimensions must be unique and in [-dims, dims - 1]. Provided
        indices may be negative, regardless of input format.
    dims : int, optional
        Dimensionality of the output array. If specified while invert is False,
        appends singleton dimensions until array matches this dimensionality.
        If specified while invert is True, applies inverse index mapping, then
        prunes singleton dimensions until array matches this dimensionality.
        Replaced by shape. If neither is provided, falls back to the highest
        provided output dimension, the dimensionality of array (invert=False),
        or the number of non-singleton dimensions in array (invert=True),
        whatever is larger. The default is None.
    shape : 1D array-like (>=array.ndim,) of ints, optional
        Replaces dims by the number of dimensions in shape and executes as
        usual. If specified while invert is False, validates that the remapped
        array is broadcast-compatible with shape in every dimension. Functional
        but not recomended for use while invert is True. The default is None.
    invert : bool, optional
        If True, switches to inverse index mapping by swapping the provided
        input dimensions and output dimensions in order to undo a previous
        reshape operation by this function that produced the array at hand.
        Requires axes_map to be the same argument as used previously, and dims
        to be the number of dimensions in the original array. If False, simply
        applies the specified index mapping. The default is False.
    pass_scalars : bool, optional
        If True, immediately returns scalar array inputs such as ints, floats,
        bools, None, or 0D arrays. If False, treats scalar inputs as 1D arrays
        of size 1. The default is False.
    validate : bool, optional
        If True, extensively validates the input parameters. If False, skips
        validation entirely and attempts direct execution. Has no effect on
        the broadcasting validation triggered by shape. The default is True.

    Returns
    -------
    array : ND array of any type
        View on the reshaped array with the required target dimensionality.

    Raises
    ------
    ValueError
        Breaks if axes_map specifies duplicate input or output dimensions,
        if any specified dimension is out of bounds with dims or array.ndim,
        or if an array-like axes_map is not at least of length array.ndim.
        Also breaks if the remapped array is not broadcast-compatible (equal
        axis sizes or one singleton) with the provided shape in all dimensions.
    """    
    # Input interpretation:
    if np.ndim(array) == 0:
        if pass_scalars:
            return array
        # Promote scalar to 1D array:
        array = np.array(array, ndmin=1)
    elif not isinstance(array, np.ndarray):
        # Ensure ND array format:
        array = np.array(array)

    if isinstance(axes_map, dict):
        # Selective mapping of individual dimensions:
        input_axes, output_axes = zip(*axes_map.items())
    elif np.iterable(axes_map):
        # Full mapping, at least one for each array dimension: 
        input_axes, output_axes = (*range(len(axes_map)),), axes_map
        
    if invert:
        # Swap indices to undo a previous reshape:
        input_axes, output_axes = output_axes, input_axes
    if shape is not None:
        # Replace/override:
        dims = len(shape)

    # Input validation:
    n_in, n_out, n = len(input_axes), len(output_axes), array.ndim
    out_of_bounds = lambda axes, d: any(ax >= d or ax < -d for ax in axes)
    validate_dims = validate and (dims is not None)
    dict_input = isinstance(axes_map, dict)
    s = f' (invert={invert})'
    if validate and invert and n_in != len(set(input_axes)):
        msg = f'Cannot remap from duplicate input dimensions{s}: {input_axes}'
        raise ValueError(msg)
    elif validate and not invert and n_out != len(set(output_axes)):
        msg = f'Cannot remap to duplicate output dimensions{s}: {output_axes}'
        raise ValueError(msg)
    elif validate_dims and invert and dims > n:
        msg = f'Cannot remap array from {n} to {dims} dimensions. '\
              f'Output cannot have more dimensions than input{s}.'
        raise ValueError(msg) 
    elif validate_dims and not invert and dims < n:
        msg = f'Cannot remap array from {n} to {dims} dimensions. '\
              f'Output cannot have fewer dimensions than input{s}.'
        raise ValueError(msg)
    elif validate_dims and not invert and out_of_bounds(output_axes, dims):
        msg = f'With {dims} output dimensions, cannot remap to dimensions '\
              f'greater than {dims - 1} or less than {-dims}: {output_axes}'
        raise ValueError(msg)
    elif validate and (dict_input or invert) and out_of_bounds(input_axes, n):
        msg = f'With {n} input dimensions, cannot remap from dimensions '\
              f'greater than {n - 1} or less than {-n}{s}: {input_axes}'
        raise ValueError(msg)
    elif validate and not (dict_input or invert) and n_out < array.ndim:
        msg = 'Without input dimensions to remap from, requires at least as '\
             f'many output dimensions as array dimensions ({n}, got {n_out}).'
        raise ValueError(msg)

    # Backward:
    if invert:
        if dims is None:
            # Count non-singleton dimensions: 
            n_full = sum(np.array(array.shape) > 1)
            # Maximize with the highest requested output dimension:
            dims = max(max(output_axes) + 1, abs(min(output_axes)), n_full)
        # Move array dimensions back into original positions:
        array = np.moveaxis(array, input_axes, output_axes)
        # Prune any trailing singleton dimensions:
        return np.squeeze(array, tuple(range(dims, n)))

    # Forward:
    if dims is None:
        # Maximize array dimensionality with highest output dimension:
        dims = max((max(output_axes) + 1, abs(min(output_axes)), n))
    # Append singleton axes to match target dimensionality:
    array = np.expand_dims(array, tuple(range(n, dims)))
    # Move array dimensions to their target positions:
    array = np.moveaxis(array, input_axes, output_axes)
    if shape is not None:
        # Validate broadcasting compatibility with requested shape:
        shape1, shape2 = np.array(array.shape), np.array(shape)
        # Assert compatible axis sizes (equal or one) in each dimension:
        if not all((shape1 == shape2) | (shape1 == 1) | (shape2 == 1)):
            raise ValueError(f'Remapped array shape {array.shape} is not '\
                             f'compatible with the requested shape {shape}.')
    return array


## ARRAY MANIPULATION (COPY/CREATE) ##


def align_arrays(arrays, new_axis=0, align='center', pad=0, dtype=float):
    """ Appends arrays as aligned slices along a new dimension of the output.

    Parameters
    ----------
    arrays : tuple or list (m,) of ND arrays
        Arrays to be aligned in a new array. Must all have the same data type
        and number of dimensions. Arrays are appended in the provided order.
        Single arrays are 
        If a single array is given, adds a singleton dimension along new_axis. 
    new_axis : int, optional
        Additional axis of the output array along which the input arrays are
        appended. The order of other axes is preserved. The default is 0.
    align : str, optional
        Defines how input arrays are inserted in each output axis. Options are
        # 'center': Aligns to the axis mid, padding both sides.
        # 'start': Aligns to the axis beginning, padding afterwards.
        # 'end': Aligns to the axis ending, padding before.
        If 'center', padding at the ending may be one sample larger if the
        number of padded samples is odd. The default is 'center'.
    pad : float or int or bool or np.nan, optional
        Fill value to initialize the output array with. The default is 0.
    dtype : dtype class, optional
        Data type to initialize the output array with. Must be compatible
        with the fill value specified by pad. The default is float.

    Returns
    -------
    output : N+1D array (..., m, ...) of dtype
        Output array with the input arrays inserted along new_axis.

    Raises
    ------
    ValueError
        Breaks if any input arrays have different dimensionality.
    """
    if isinstance(arrays, np.ndarray):
        # Simple axis insertion early exit:
        return np.expand_dims(arrays, axis=new_axis)

    # Determine extent of each array:
    dims, shapes = zip(*[(array.ndim, array.shape) for array in arrays])
    dims, max_dims = np.array(dims), max(dims)

    # Validate equal dimensionality:
    invalid = np.nonzero(dims < max_dims)[0]
    if invalid.size:
        txt = string_series(invalid, prefix=['Array', 'Arrays'], 
                            suffix=['is ', 'are '], conj='and')
        raise ValueError(f'{txt} incompatible with dimensionality {max_dims}.')

    # Get maximum extent per dimension:
    shapes = np.array(shapes, dtype=int)
    max_shape = np.max(shapes, axis=0)

    # Determine unfilled spaces:
    paddings = max_shape - shapes
    if align == 'center':
        starts = paddings // 2
    elif align == 'start':
        starts = np.zeros_like(paddings)
    elif align == 'end':
        starts = paddings
    stops = starts + shapes

    # Initialize output array with additional axis to merge arrays along:
    full_shape = (*max_shape[:new_axis], dims.size, *max_shape[new_axis:])
    output = np.full(full_shape, fill_value=pad, dtype=dtype)

    # Prepare indices for array insertion:
    slice_axes = list(range(output.ndim))
    starts, stops = starts.tolist(), stops.tolist()

    # Insert each aligned array slice into the output array:
    for i, (array, start, stop) in enumerate(zip(arrays, starts, stops)):
        start.insert(new_axis, i), stop.insert(new_axis, i + 1)
        inds = slice_index(output.ndim, slice_axes, start, stop)
        output[inds] = np.expand_dims(array, axis=new_axis)
    return output


## ARRAY INSPECTION ##


def edge_along_axis(array, axis=0, which=-1, validate=True, reduce=False):
    """ In a 2D array, finds first or last non-zero entry per column or row.
        Designed for multiple distributions or multi-channel time series data,
        but can handle 1D arrays by a separate processing branch. By default,
        identified non-zero entries are returned as a tuple of 1D arrays that
        can be used to index the original array (np.nonzero format). Output can
        be reduced to a single 1D array of indices along the given axis.

    Parameters
    ----------
    array : 2D array (m, n) or 1D array (m,) of arbitrary type 
        Array in which to identify the requested edge indices.
    axis : int, optional
        Array dimension along which to find the requested edge indices. Options
        are 0 or 1. If axis is 0, searches along each array column. If axis
        is 1, searches along each array row. Must be 0 if array is 1D. The
        default is 0.
    which : int, optional
        Specifies whether to find the first or last non-zero entry along the
        given axis. Options are 0 (first) and -1 (last). The default is -1.
    validate : bool, optional
        If True and array contains all-zero columns/rows, omits corresponding
        indices from the output. If False, returns indices for all slices (non-
        sensical integers in case of all-zero slices). The default is True.
    reduce : bool, optional
        If False, returns a tuple of two 1D arrays (one if input array is 1D),
        which provide the full index pair for each column/row. This format is
        valid for indexing both 1D and 2D input arrays, producing 1D output. If
        True, returns a single 1D array of indices along the given array axis,
        with one entry per slice. This format is good to access the indices
        themselves but may be unsuitable for indexing. The default is False.

    Returns
    -------
    inds : 1D array (p,) or tuple (2, or 1,) of 1D arrays (p,)
        Indices of the first or last non-zero entry per column or row in array.
        If reduce is True, returns a single 1D array of indices along axis,
        else a tuple of one or two 1D index arrays (depending on array.ndim).
        Can at most hold as many entries as specified slices in array (less if
        validate is True and and array contains all-zero slices).

    Raises
    ------
    ValueError
        Breaks if array is neither 1D nor 2D. Breaks immediately if array
        contains no non-zero entries. If validate is True, breaks if no entries
        remain after omitting all-zero slices.
    """
    # All-zero early exit:
    if not np.any(array):
        raise ValueError('No non-zero entries found in the given array.') 

    # Input interpretation:
    if which == 0:
        # Find first indices:
        mask_value = np.inf
        func = np.argmin
    elif which == -1:
        # Find last indices:
        mask_value = -np.inf
        func = np.argmax

    # Univariate early exit:
    if array.ndim == 1 or (array.ndim == 2 and 1 in array.shape):
        # Get index coordinates of entry:
        inds = np.argwhere(array)[which]
        if reduce:
            # Slice coordinates to single dimension (1D array):
            return array_slice(inds, start=axis, stop=axis, include=True)
        # Ensure index use (tuple of 1D arrays):
        return tuple(i for i in inds[:, None])
    # Shape validation:
    elif array.ndim != 2:
        raise ValueError('Input array must be 1D or 2D.')

    # Draw parallel index gridlines along axis:
    grid_inds = np.arange(array.shape[axis])
    grid_inds = np.expand_dims(grid_inds, axis=1 - axis)
    # Set non-zero entries to indices, hide others:
    masked_array = np.where(array, grid_inds, mask_value)
    # Find smallest/largest index per column/row:
    inds = func(masked_array, axis=axis).astype(int)

    # Return options:
    if validate:
        # Omit all-zero columns/rows:
        is_valid = np.any(array, axis=axis)
        inds = inds[is_valid]
        if inds.size == 0:
            # Break instead of returning empty index array:
            raise ValueError('No non-zero entries found in the given array.')
    if reduce:
        # 1D array:
        return inds
    # Complete index pairs by each row/column:
    other_inds = np.arange(array.shape[1 - axis])
    if validate:
        # Match to valid counterparts:
        other_inds = other_inds[is_valid]
    # Return sorted to enable index use (tuple of 1D arrays):
    return (other_inds, inds) if axis else (inds, other_inds)


## ADJUSTED BEHAVIOR ##


def safe_fraction(numerator, denominator, shape=None, value=np.nan, sign=None):
    """ Divides two arrays element-wise, avoiding divisions by zero.
        Wrapper to np.divide(). Skips invalid operations and sets the output to
        the given replace value. Can filter further by the sign of the output.

    Parameters
    ----------
    numerator : ND-array of floats or ints
        Numerator of element-wise division. 
    denominator : ND-array of floats or ints
        Denominator of element-wise division, broadcastable to numerator.
    shape : tuple of ints, optional
        Shape of the output array. If not specified, inferred from the shapes
        of numerator and denominator, if possible. The default is None.
    value : scalar, optional
        Value to replace the output of invalid or filtered operations.
        The default is np.nan.
    sign : int or array-like of ints
        If specified, also skips operations that produce output with a sign
        other than the specified ones. Options are 1 for positive, -1 for
        negative, and 0. The default is None.

    Returns
    -------
    output : ND-array of floats (shape)
        Result of element-wise division of numerator by denominator.

    Raises
    ------
    ValueError
        Breaks if numerator and denominator are not broadcastable. 
    """ 
    # Input validation:
    if shape is None:
        valid, shape = broadcastable([numerator.shape, denominator.shape])
        if not valid:
            msg = 'Numerator and denominator must be broadcastable.'
            raise ValueError(msg)

    # Initialize storage array and find zero divisions:
    out, where = np.full(shape, value), denominator != 0
    if sign is not None:
        # Optional filtering of positive, negative, or zero output:
        where &= np.isin(np.sign(numerator) * np.sign(denominator), sign)
    return np.divide(numerator, denominator, out=out, where=where)

