import numpy as np
from scipy.ndimage import label
from itertools import product


## STRING FORMATTING ##


def string_series(series, delimit=', ', prefix='', suffix='', conj='',
                  add_spaces=True):
    """ Returns a single formatted string listing the elements of a sequence.
        Series elements are separated by the given delimiter, which can be
        modified with a conjuction at the last link. The full series may be
        preceded or followed by additional singular/plural-selective text.

    Parameters
    ----------
    series : iterable of arbitrary types (m,)
        Sequence of elements to be listed in string format.
    delimit : str, optional
        Delimiter text to separate series elements. Not modified before joining
        elements, any bordering spaces must be included. The default is ', '.
    prefix : str or iterable (2,) of str, optional
       Text to insert before the first element of the sequence. If some pair,
       uses prefix[0] for single elements and prefix[1] for multiple elements.
       The default is ''.
    suffix : str or iterable (2,) of str, optional
        Text to insert after the last element of the sequence. If some pair,
        uses suffix[0] for single elements and suffix[1] for multiple elements.
        The default is ''.
    conj : str, optional
        Text for modifying the last delimiter in the series. Ignored if series
        contains only one element. Replaces the delimiter if series contains
        two elements. Else, inserted between last delimiter and last element.
        The default is ''.
    add_spaces : bool, optional
        If True, adds a space before the suffix and after the prefix as well as
        the conjunction, if not already present. The default is True.

    Returns
    -------
    str (n,)
        Formatted string listing all elements of the sequence.
    """    
    # Ensure strings in mutable wrapper:
    series = [f'{element}' for element in series]
    n = len(series)

    # Manage text at series start:
    if not isinstance(prefix, str):
        prefix = prefix[n > 1]
    if prefix and add_spaces and not prefix.endswith(' '):
        prefix += ' '

    # Manage text at series end:
    if not isinstance(suffix, str):
        suffix = suffix[n > 1]
    if suffix and add_spaces and not suffix.startswith(' '):
        suffix = ' ' + suffix

    # Manage linkage text:
    if conj and n > 1:
        if add_spaces and not conj.endswith(' '):
            conj += ' '
        if n == 2:
            return f'{prefix}{series[0]} {conj}{series[1]}{suffix}'
        series[-1] = f'{conj}{series[-1]}'
    return f'{prefix}{delimit.join(series)}{suffix}'


## TYPE CHECKING & VARIABLE EQUALIZATION ##


def check_list(*variables, skip_None=True):
    """ Type-checks passed variables and wraps each non-list in a list.
        Enables functions expecting iterable arguments (as in single for-loops)
        to handle scalars. Nones are kept as is unless requested otherwise.

    Parameters
    ----------
    *variables : arbitrary types (m,)
        One or multiple variables to be type-checked and wrapped if required.
    skip_None : bool, optional
        If True, returns Nones as Nones (else treated as any other variables).

    Returns
    -------
    vars : (generator of) lists or Nones (m,)
        Type-checked and wrapped input variables, ready for unpacking.
        Returns a single variable explicitly, else a generator.
    """
    skip_var = lambda v: isinstance(v, list) or (skip_None and v is None)
    checked = (var if skip_var(var) else [var] for var in variables)
    return checked if len(variables) > 1 else tuple(checked)[0]


def equal_lists(vars, skip_None=True):
    """ Ensures that each variable is a list of length of longest passed list.
        Wrapped variables of length 1 are repeated to match the longest list.
        Ignores empty lists. Nones are kept as is unless requested otherwise.

    Parameters
    ----------
    vars : tuple of arbitrary types (m,)
        Multiple variables to type-check and equalize in length, if possible.
    skip_None : bool, optional
        If True, returns Nones as Nones (else treated as any other variables).

    Returns
    -------
    vars : tuple of lists or Nones (m,)
        Type-checked and equalized variables, ready for unpacking.

    Raises
    ------
    ValueError
        Breaks if any list has more than one element but less than the maximum.
    """    
    # Assert iterables:
    vars = tuple(check_list(*vars, skip_None=skip_None))

    # Count elements:
    n = 1 - skip_None
    lengths = np.array([len(var) if var is not None else n for var in vars])
    target = max(lengths)

    # Control for lengths that are not directly adjustable:
    if not all(n in (0, 1, target) for n in lengths):
        msg = 'Cannot equalize list variables whose length is neither 1 nor '\
             f'equal to the length of the longest list ({target},).'
        raise ValueError(msg)
    return tuple(v * target if l == 1 else v for v, l in zip(vars, lengths))


def ensure_sequence(*vars, skip_None=True, unwrap=True):
    """ Ensures that all passed variables are iterable and sequence-like.
        Allows functions expecting iterable inputs (e.g in single for-loops) to
        handle scalar inputs, as well. "Sequence-like" refers to tuples, lists,
        and ND arrays with at least one dimension (np.ndim(var) > 0). Variables
        of these types are returned unchanged. Scalars (ints/floats/bools) or
        other iterables (dicts/strings/sets) are converted to single-element
        tuples. 0D arrays are expanded to 1D arrays. Nones can be treated as
        scalar variables or be passed through as None on request. 

    Parameters
    ----------
    *vars : arbitrary types (m,)
        One or multiple variables to be checked and converted if necessary.
    skip_None : bool, optional
        If True, returns Nones as Nones, else as single-element tuples (None,).
        The default is True.
    unwrap : bool, optional
        If True and only a single variable is passed, returns the converted
        variable without enclosing tuple. If False, output is always wrapped in
        a tuple, even if only one variable is passed. The default is True.

    Returns
    -------
    vars : tuple of arbitrary types (m,)
        Checked and converted input variable or variables.
    """    
    # Delegate type-checking and sequence enforcement to helpers:
    skip_var = lambda v: np.ndim(v) > 0 or (skip_None and v is None)
    make_sequence = lambda v: v[None] if isinstance(v, np.ndarray) else (v,)
    # Check each input variable and modify it if necessary:
    vars = tuple(v if skip_var(v) else make_sequence(v) for v in vars)
    return vars[0] if unwrap and len(vars) == 1 else vars


def equal_sequences(*vars, skip_None=True):
    """ Ensures that all passed variables are sequence-likes of same length.
        "Sequence-like" refers to tuples, lists, and ND arrays with at least
        one dimension (np.ndim(var) > 0). Calls ensure_sequence() to convert
        any other variables to single-element tuples or 1D arrays. Nones can
        either be tuple-wrapped or passed through as None. Single-element
        sequences are repeated to match the length of the longest sequence,
        converting all arrays to lists beforehand.

    Parameters
    ----------
    *vars : arbitrary types (m,)
        Multiple variables to be type-checked and equalized, if possible.
    skip_None : bool, optional
        If True, returns Nones as Nones. If False, treats Nones as single-
        element tuples (None,) to be repeated. The default is True.

    Returns
    -------
    vars : tuple of arbitrary types (m,)
        Checked and equalized input variables.

    Raises
    ------
    ValueError
        Breaks if any sequence size is neither 1 nor the maximum across vars.
    """  
    # Enforce tuples, letting lists and arrays >0D pass through:
    vars = ensure_sequence(*vars, skip_None=skip_None, unwrap=False)

    # Count number of elements in each sequence:
    sizes = [len(v) if v is not None else (1 - skip_None) for v in vars]
    target = max(sizes)

    # Validate compatibility of element counts:
    if not all(n in (0, 1, target) for n in sizes):
        msg = f'With a maximum sequence length of {target}, variables can '\
              f'only have length {target} or 1 or be None: {sizes}'
        raise ValueError(msg)

    # Equalize sequence length across variables:
    convert_var = lambda v: v.tolist() if isinstance(v, np.ndarray) else v
    zipped = zip(vars, sizes)
    return tuple(convert_var(v) * target if l == 1 else v for v, l in zipped)


def ensure_iterable(vars=None, var=None, equalize=False, convert=np.array):
    """ Type-checks passed variables and converts to some iterable, if needed.
        Non-iterable variables (e.g. int, float, 0D array) are converted to
        numpy arrays with ndmin=1. Other iterables (e.g. list, tuple, 1D array)
        and Nones are left as is. Iterables can then be equalized in length,
        if possible, or converted to a different iterable type. 

    Parameters
    ----------
    vars : list or tuple (m,) of any type, optional
        Multiple variables to check, convert, and equalize if requested.
        Takes precedence over var. The default is None.
    var : any type, optional
        Single variable to check and convert. Allows to distinguish between a
        tuple of multiple variables (vars) and a single variable of type tuple.
        Overwritten by vars. The default is None.
    equalize : bool, optional
        If True, gets the number of elements to iterate over for each variable,
        finds the maximum, and expands single-element iterables to match it.
        Raises an error if the number of elements is ambiguous. Ignored if
        input is a single variable. The default is False.
    convert : func, optional
        Function to convert all variables to a certain iterable type after
        first conversion of non-iterables to 1D arrays. Should take an iterable
        as only argument and return a new iterable, e.g. list() or tuple().
        If None, no further conversion is performed. The default is np.array().  

    Returns
    -------
    vars : tuple of iterables or Nones (m,)
        Multiple type-checked and converted variables, ready for unpacking.
        Returned in order of the input variables. Nones are returned as Nones.
    var : iterable or None
        Single type-checked and converted variable. Returned instead of vars
        whenever a single input variable is passed. None is returned as None.

    Raises
    ------
    ValueError
        Breaks if equalize is True and the number of elements in each iterable
        is ambiguous (may only be either 1 or a common maximum).
    """    
    # Input interpretation:
    if vars is None:
        vars = [var]
    elif not isinstance(vars, list):
        # Ensure mutable:
        vars = list(vars)

    # Type-check and convert variables:
    n_elements = np.zeros(len(vars)) - 1
    for i, var in enumerate(vars):
        if var is not None:
            if not np.iterable(var):
                vars[i] = np.array(var, ndmin=1)
            if convert is not None:
                vars[i] = convert(vars[i])
            n_elements[i] = len(vars[i])

    # Disabled or redundant length-check early exit:
    if not equalize or all(n_elements == n_elements[0]):
        return vars[0] if len(vars) == 1 else tuple(vars)

    # Equalize iterable lengths:
    n_target = max(n_elements)
    if not all(np.isin(n_elements, [-1, 1, n_target])):
        msg = f'Cannot equalize ambiguous iterable lengths: {n_elements}.'
        raise ValueError(msg)
        
    # Expand each single-element iterable:
    for ind in np.nonzero(n_elements == 1)[0]:
        if n_elements[ind] == 1:
            vars[ind] = np.repeat(vars[ind], n_target)
            if convert is not None:
                vars[ind] = convert(vars[ind])
    return tuple(vars)


def ensure_array(vars=None, var=None, copy=False, dtype=float,
                 dims=None, shape=None, list_shapes=False, verbose=False):
    """ Turns variables to arrays, validates dimensionality, and adjusts shape.
        Calls np.array() with the specified dtype on the given variables. Can
        be set to break if one of the resulting arrays has an unexpected number
        of dimensions. Validated arrays can then be rearranged into a given
        shape. Specify either vars as tuple to pass multiple variables, or var
        to pass a single variable (ensures correct behavior if var is tuple).

    Parameters
    ----------
    vars : tuple or list of arbitrary types (m,), optional
        Multiple variables to be type-checked. Elements of vars that are tuples
        are handled as expected. The default is None.
    var : arbitrary type, optional
        Single variable to be type-checked. Serves to distinguish between a
        tuple of multiple variables and a single variable of tuple type. The
        default is None.
    copy : bool, optional
        If True, calls np.array() on every variable, including those that are
        already arrays. If False, calls np.array() only on non-array variables.
        The default is False.
    dtype : str, optional
        If specified, calls np.array(dtype=dtype) where requested, depending on
        the copy parameter. Else, set by np.array() to fit the contents of each
        variable it is called upon. Forcing a given dtype may cause loss of
        precision. The default is float.
    dims : int or tuple or list or 1D array of ints (n,), optional
        If specified, ensures that the number of dimensions of each (passed or
        newly created) array is one of the specified values. Raises an error
        for arrays with unexpected dimensionality. The default is None.
    shape : tuple or list or 1D array of ints (p,), optional
        If specified, attempts to force each array into the desired shape and
        fails with an error if broadcast is not possible. By np.reshape()
        default, one dimension can be set to -1 to be inferred from remaining
        dimensions. In addition, one or several dimensions can be unspecified
        as None. If an array has the same number of dimensions as the requested
        shape, unspecified dimensions are adopted from the initial shape of the
        array. If an array has as many dimensions as the requested shape minus
        the number of unspecified dimensions, each unspecified dimension is set
        to 1. All other cases are considered ambiguous and raise an error.
        Unspecified dimensions can only be used to expand from a single lower
        dimension (e.g. 1D) to some higher dimension (e.g. 2D), but not from
        e.g. 1D to 3D and 2D to 3D at the same time. Use (-1, None) to turn 1D
        arrays into single-column 2D arrays (2D arrays are accepted normally as
        they are). Use (None, -1) to turn 1D arrays into single-row 2D arrays.
        The default is None.
    list_shapes : bool, optional
        If True, returns the initial shape of each array (after conversion and
        dimensionality validation, but before reshaping) in addition to the
        arrays themselves. Can be used to retrieve the original shape of
        converted non-array variables, if required. The default is False.
    verbose : bool, optional
        If True, prints a warning every time the shape of an array has been
        changed, logging the initial and the new shape. The default is False.

    Returns
    -------
    arrays : array or list (m,) of arrays (arbitrary shape)
        One or several variables in array format with validated dimensionality.
        Single variables are returned as an unwrapped array. Multiple variables
        are returned as a list of arrays, ready for unpacking.
    input_shapes : tuple or list (m,) of tuples (arbitrary length)
        Original shape of each variable in array format (after conversion, but
        before reshaping). Only returned if list_shapes is True.

    Raises
    ------
    ValueError
        Breaks if an array has invalid dimensionality (before reshaping).
    ValueError
        Breaks if unspecified dimensions (None) in the requested shape are
        ambiguous for the initial shape of the array. Happens when the desired
        number of dimensions is not equal to the initial number of dimensions,
        or to the initial number of dimensions minus the number of unspecified
        dimensions.
    """    
    # Input interpretation:
    if var is not None:
        vars = (var,)
    # Validate dimensionality:
    if dims is not None:
        # Assert iterable:
        if not isinstance(dims, (list, tuple)):
            dims = (dims,)
        valid = string_series(dims, conj='or')
        msg_dims = f"Number of array dimensions must be {valid}."
    # Prepare reshaping:
    if shape is not None:
        shape = np.array(shape)
        buffer_dims = shape == None
        n_buffers = sum(buffer_dims)

    # Run type-checks:
    arrays, input_shapes = [], []
    for var in vars:
        # Force into array format:
        if copy or (not isinstance(var, np.ndarray)):
            var = np.array(var, dtype)
        # Optional dimensionality validation:
        if dims is not None and var.ndim not in dims:
            raise ValueError(msg_dims)
        # Log initial array shape:
        input_shapes.append(var.shape)
        # Optional reshaping:
        if shape is not None:
            initial = np.array(var.shape)
            target = shape.copy()
            # Manage unspecified dimensions:    
            if n_buffers and initial.size == shape.size:
                # Preserve shapes of matching dimensionality:
                target[buffer_dims] = initial[buffer_dims]
            elif n_buffers and initial.size == shape.size - n_buffers:
                # Expand if possible:
                target[buffer_dims] = 1
            elif n_buffers:
                # Report failure to infer unspecified dimensions:
                msg_shape = f'Unspecified dimensions in {target} are '\
                            f'ambiguous for initial shape {initial}.' 
                raise ValueError(msg_shape)
            var = var.reshape(target)
            if verbose and not np.array_equal(initial, var.shape):
                # Report deviation from initial array shape:
                print(f'WARNING: Reshaped {tuple(initial)} to {var.shape}.')
        if len(vars) == 1:
            # Single variable early exit:
            return (var, input_shapes[0]) if list_shapes else var
        # Log finalized array:
        arrays.append(var)
    return (*arrays, input_shapes) if list_shapes else arrays


## ADJUSTED BEHAVIOR ##


def safe_zip(*variables, crash=True):
    """ Zips input variables together after checking for size consistency.
        Counts and compares the number of elements per variable using len().
        On mismatch, can either raise an error or execute with a warning.   
        Treats scalars as single-element tuples to be zipped if possible.

    Parameters
    ----------
    variables : iterable (m,) of iterables (any shape)
        Input variables to parallelize.
    crash : bool, optional
        If True, responds to size mismatches with a ValueError. If False,
        prints a warning and proceeds with zipping. The default is True.

    Returns
    -------
    zipped : zip generator
        Parallelized input variables.

    Raises
    ------
    ValueError
        Breaks if crash is True and input variables differ in size.
    """
    variables = [var if np.iterable(var) else (var,) for var in variables]
    reference = len(variables[0])
    if not all(len(var) == reference for var in variables):
        if crash:
            raise ValueError('Refusing to zip variables that differ in size.')
        print('WARNING: Zipping variables that differ in size.')
    return zip(*variables)


def unsort_unique(data, axis=None):
    """ Filters unique elements in data in the order of first occurence.
        Reverses the output sorting of np.unique() by indexing along axis.

    Parameters
    ----------
    data : array-like of floats or ints or str (any shape)
        Data to be filtered for unique elements. Cannot handle object arrays.
    axis : int, optional
        Axis argument passed to np.unique(). If specified and data is >1D,
        returns unique slices along the specified axis, else unique entries
        along the flattened data. The default is None.

    Returns
    -------
    unsorted : ND array of floats or ints (n,)
        Unique elements in the order of their first occurence in data. If axis
        is specified and data is >1D, maintains input dimensionality (else 1D).
    """
    values, inds = np.unique(data, return_index=True, axis=axis)
    if values.ndim > 1:
        slice_inds = [slice(None)] * values.ndim
        slice_inds[axis] = np.argsort(inds)
        return values[tuple(slice_inds)]
    return values[np.argsort(inds)]
    

## NUMERICS & INDICES ##


def valid_decimals(value, n_decimal=15):
    """ Rounds number, counts non-zero decimals, and returns as fitting type.
        Also returns number of non-zero decimals for the given rounding.
        Useful as switch between float and int for printing and annotating.
        Function is bound to limits of floating point representation.

    Parameters
    ----------
    value : float
        Value to format by conversion to f-string. Rounds to n_decimal places
        and crops trailing zeros before counting non-zero decimals. 
    n_decimal : int, optional
        Number of decimal places to round the value. The default is 15, which
        is the maximum amount for reliable float representation.

    Returns
    -------
    value : float or int
        Formatted value as the appropriate type for the remaining non-zero
        decimals after rounding. If no non-zero decimals remain, returns int.
        Else, returns float.
    n_valid : int
        Number of non-zero decimal places in the formatted value.
    """    
    value = f'{value:.{n_decimal}f}'
    n_valid = len(value.strip('0').split('.')[1])
    return float(value) if n_valid else int(value.split('.')[0]), n_valid


def round_decimal(value, n_decimal=None, which='ceil'):
    """ Ceil or floor rounding to the specified decimal place.

    Parameters
    ----------
    value : float
        Value to be rounded.
    n_decimal : int, optional
        Number of decimal places to round to. If unspecified, counts non-zero
        decimals in value and rounds to next smaller decimal (one to the left).
        If 0, rounds to nearest integer, which is the same as calling np.ceil()
        or np.floor(). The default is None.
    which : str, optional
        Rounding direction. If 'ceil', rounds the given decimal place up to the
        next-higher number. If 'floor', rounds decimal place down to the
        next-lower number. Else, simply calls np.round(decimals=n_decimals) as
        a fallback. The default is 'ceil'.

    Returns
    -------
    rounded : float
        Rounded value according to the specified decimal place and direction.
    """    
    if n_decimal is None:
        # Auto-generate target decimal:
        _, n_decimal = valid_decimals(value)
        n_decimal -= 1
    if which == 'ceil':
        # Round up to nearest decimal place:
        rounded = np.ceil(value * 10**n_decimal) / 10**n_decimal
    elif which == 'floor':
        # Round down to nearest decimal place:
        rounded = int(value * 10**n_decimal) / 10**n_decimal
    else:
        # Fall-back (standard rounding):
        rounded =  np.round(value, n_decimal)
    return rounded


def as_power(value, base=10):
    """ Computes the exponent to represent value as a power of the given base.

    Parameters
    ----------
    value : float or int
        Value to represent as a power of base.
    base : float or int
        Base of the power representation. The default is 10.

    Returns
    -------
    exponent : float
        Exponent of the power representation, so that base**exponent = value.
        Reverse calculation of value might result in floating point errors.
    """    
    exponent = np.log(value) / np.log(base)
    return exponent


def round_power(value, base, which='round'):
    """ Closest approximation of value as an integer exponent raised to base.

    Parameters
    ----------
    value : float or int
        Value to approximate as a power of base.
    base : float or int
        Base of the power approximation.
    which : str, optional
        Direction to round exponent. If 'round', rounds to the nearest integer.
        If 'ceil', rounds up to the next-higher integer. If 'floor', rounds
        down to the next-lower integer. The default is 'round'.

    Returns
    -------
    rounded : float
        Power approximation of value according to the given base and rounding.
    exponent : int
        Integer exponent that gives closest approximation of value as a power
        of base.
    """    
    if which == 'round':
        exponent = int(np.round(np.log(value) / np.log(base)))
    elif which == 'ceil':
        exponent = int(np.ceil(np.log(value) / np.log(base)))
    elif which == 'floor':
        exponent = int(np.floor(np.log(value) / np.log(base)))
    return base**exponent, exponent


def remap_inds(subsets, return_all=False):
    """ Hierarchical remapping of indices between different subset levels.
        Remapping is performed by np.searchsorted() from highest to lowest
        level such that array[remap[0]]...[remap[i]] == array[subsets[i]].

    Parameters
    ----------
    subsets : list or tuple (m,) of 1D arrays of ints
        Indices on the target axis of the source array that define steadily
        decreasing subsets of elements or slices. First subset is the highest
        level. Each subsequent index array must be a subset of the previous.
        Consequently, the lowest subset may also consist of a single index.  
    return_all : bool, optional
        If True, returns the full sequence of index arrays, where the first
        subset is left unchanged and all subsequent subsets are remapped to
        match their predecessors. If False, returns only the lowest subset.

    Returns
    -------
    subsets : 1D array of ints or list (m,) of 1D arrays of ints
        Remapped indices of the lowest subset level, or the full sequence of
        index arrays if return_all is True. Index array size is maintained.

    Raises
    ------
    ValueError
        Breaks if hierarchical structure is violated, i.e. if any lower-level
        subset contains indices that are not part of the first index array.
    """    
    # Ensure mutable iterable:
    if not isinstance(subsets, list):
        subsets = list(subsets)
    # Validate subset hierarchy:
    if not all([np.isin(inds, subsets[0]).all() for inds in subsets[1:]]):
        raise ValueError('Indices must form a hierarchical subset structure.')

    # Iterative hierarchical remapping:
    for i in range(len(subsets) - 1):
        # Remap all lower index subsets to match the current index subset:
        remap = [np.searchsorted(subsets[i], inds) for inds in subsets[i + 1:]]
        # Update successors:
        subsets[i + 1:] = remap
    return subsets if return_all else subsets[-1]


## DICTIONARY MANIPULATION ##


def merge_dicts(parent, child, prefix='', suffix='', overwrite=False):
    """ Returns the union of the parent dictionary and the child dictionary.
        Child keys are prefixed or suffixed for distinction in the output. If
        a child key is already in the parent dictionary, the parent entry can
        either be replaced by or kept alongside the respective child entry.

    Parameters
    ----------
    parent : dict
        Primary dictionary for merging.
    child : dict
        Secondary dictionary for merging. May be larger than or contain any
        subset of parent. Child keys are modified to be distinct in the output.
    prefix : str, optional
        Key tag prepended to child keys. If both prefix and suffix are empty,
        disables tagging, preventing use of unmerge_dicts(). The default is ''.
    suffix : str, optional
        Key tag appended to child keys. If both prefix and suffix are empty,
        disables tagging, preventing use of unmerge_dicts(). The default is ''.
    overwrite : bool, optional
        If True, child entries replace parent entries with the same key. Else,
        the parent entry remains in the output and the child entry is added
        under the modified key. The default is False. 

    Returns
    -------
    union : dict
        Single dictionary that contains the entries of both parent and child.
        If overwrite is True, some parent entries might be removed from union.  
    """    
    union = parent.copy()
    for key, value in child.items():
        if overwrite and key in union:
            union.pop(key)
        union[prefix + key + suffix] = value
    return union


def unmerge_dicts(union, prefix='', suffix=''):
    """ Splits the dictionary into a parent dictionary and a child dictionary.
        Child entries are identified by their key prefix or suffix and removed
        from union. The remainders are treated as parent entries. 

    Parameters
    ----------
    union : dict
        Result of merging parent and child, as returned by merge_dicts().
    prefix : str, optional
        Key tag prepended to child keys. If both prefix and suffix are empty,
        all entries of union are treated as child entries. The default is ''.
    suffix : str, optional
        Key tag appended to child keys. If both prefix and suffix are empty,
        all entries of union are treated as child entries. The default is ''.

    Returns
    -------
    child : dict
        Split-off secondary dictionary. Child entries have the key tags
        removed. Returns union if both prefix and suffix are empty.
    parent : dict
        Remaining primary dictionary after extraction of tagged child entries.
        Returns {} if both prefix and suffix are empty.
    """    
    child = {}
    for key in list(union.keys()):
        if key.startswith(prefix) and key.endswith(suffix):
            child[key[len(prefix):].replace(suffix, '')] = union.pop(key)
    return child, union
    

## ARRAY INSPECTION ##


def closest_value(array, value, tol=None):
    """ Finds index of datapoint closest to given value.
        Optionally, finds all datapoints within tolerated distance to value.

    Parameters
    ----------
    array : array of floats (arbitrary shape)
        Dataset in which to search for matches to the desired value.
        Dimensionality of array slightly changes output. May not be 0D.
    value : float
        Reference value to compare with entries of array.
    tol : float, optional
        Optional tolerance criterion for matching. If specified, returns
        indices of all entries whose absolute distance to value is below or
        equal to tol, using np.nonzero(). Else, returns index of entry with
        minimum absolute distance to value using np.argmin(). In this case,
        returns only first match if multiple exist. The default is None.

    Returns
    -------
    ind : int or 1D array of ints (m,) or tuple (n,) of (arrays) of ints (m,)
        Index or indices of datapoint(s) closest to value, depending on
        whether tol is specified or not. If tol is None, ind is a single scalar
        for 1D data and a tuple of scalars for n-dimensional data. If tol is
        specified, ind is a 1D array for 1D data and a tuple of 1D arrays for
        n-dimensional data. Returned indices can be used to access the found
        matches in array.
    """    
    if tol is None:
        # Index of first closest value:
        ind = np.argmin(np.abs(array - value))
        if array.ndim > 1:
            # Adjust index dimensions:
            ind = np.unravel_index(ind, array.shape)
    else:
        # Indices of all values within tolerance:
        ind = np.nonzero(np.abs(array - value) <= tol)
        if array.ndim == 1:
            # Open tuple:
            ind = ind[0]
    return ind


def nonzero_inds(array, grouping='dim', single_entry=False,
                 single_dim=True, axis=None):
    """ Wrapper for np.nonzero() or np.argwhere() to extract non-zero indices.
        Returns indices of M non-zero entries in an N-dimensional array, which
        are grouped by either array dimension (nonzero: tuple of N 1D arrays of
        length M) or entry (argwhere: MxN 2D row array). Depending on grouping,
        the output can be unpacked in case of single non-zero entries or
        dimensions in array, e.g. converting arrays to scalars, or removing the
        tuple wrapper.

    Parameters
    ----------
    array : ND-array of arbitrary type and shape
        Input array for extracting indices of non-zero entries.
    grouping : str, optional
        Specifies the function to use, which in turn determines output index
        format and keyword argument interpretation. Options are 'dim' to group
        indices by array dimension (nonzero) or 'entry' to group by non-zero
        entries (argwhere). The default is 'dim'.
    single_entry : bool, optional
        If True, applies if array contains only a single non-zero entry, and 
        adjusts the output format. If grouping is 'dim', converts 1D arrays of
        length 1 into a single numpy integer per array dimension (tuple-wrapped
        by default). If grouping is 'entry', converts the single-row 2D array
        to 1D (or 1D array to scalar if single_dim applies as well).
        The default is False.
    single_dim : bool, optional
        If True, applies if array is 1D or axis is specified, and adjusts the
        output format. If grouping is 'dim', removes the tuple wrapper and
        returns a single 1D array (or integer if single_entry applies as well).
        If grouping is 'entry', converts the single-column 2D array to 1D.
        The default is True.
    axis : int, optional
        If specified, returns the indices of non-zero entries only along the
        given array dimension. Automatically triggers single_dim.
        The default is None.

    Returns
    -------
    inds : (tuple of) int(s) or 1D-array(s) of int(s)
        Indices of non-zero entries in array in the specified format. Different
        formats have different use cases, and only np.nonzero() indices can be
        used directly for indexing the entries in array. Index formats accepted
        by numpy include integers (yields scalars), 1D arrays (yields arrays),
        and tuples of the former two, with one entry per array dimension. 
    """    
    # Per dimension:
    if grouping == 'dim':
        # Tuple of 1D arrays:
        inds = np.nonzero(array)
        # Array to scalar for each dimension:
        if single_entry and inds[0].size == 1:
            inds = tuple(ind[0] for ind in inds)
        # Subset special case:
        if axis is not None:
            return inds[axis]
        # Tuple to single array/integer:
        elif single_dim and len(inds) == 1:
            return inds[0]

    # Per non-zero entry:
    elif grouping == 'entry':
        # 2D row array:
        inds = np.argwhere(array)
        # Subset special case:
        if axis is not None:
            inds = inds[:, axis]
        # Flatten single 2D column:
        if single_dim and inds.shape[1] == 1:
            inds = inds[:, 0]
        # Return single 1D array/scalar:
        if single_entry and inds.shape[0] == 1:
            return inds[0]
        # Adjust to standard output format:
        return tuple(entry for entry in inds)
    return inds


def rank_extremes(array, n_ranks=1, ordered=True):
    """ Indices of smallest and largest values in array, including duplicates.

    Parameters
    ----------
    array : 1D array of floats or ints (m,)
        Dataset in which to identify entries that are among the n_ranks
        smallest and largest unique ranked values, respectively.
    n_ranks : int, optional
        Number of largest and smallest ranks to consider, respectively. The
        default is 1, which returns the indices of all entries that yield the
        global minimum and maximum of array.
    ordered : bool, optional
        If True, returns indices of identified entries for each rank, sorted
        after their position in array. Else, returns indices of all entries
        within the specified range of ranks at once, sorted after their
        position in array but not separated by rank. The default is True.

    Returns
    -------
    max_inds : list (n,) of 1D arrays of ints (p,) or 1D array of ints (q,)
        Indeces of entries in array that are among the n_ranks largest unique
        values. If ordered is True, returns a list of arrays, each containing
        the entries for one rank (starting with the global maximum). If ordered
        is False, returns a single array with all entries within the specified
        range of ranks.
    min_inds : list (n,) of 1D arrays of ints (r,) or 1D array of ints (s,)
        Indeces of entries in array that are among the n_ranks smallest unique
        values. If ordered is True, returns a list of arrays, each containing
        the entries for one rank (starting with the global minimum). If ordered
        is False, returns a single array with all entries within the specified
        range of ranks.
    """    
    uni = np.unique(array)
    if ordered:
        # Separate indices for each rank:
        max_inds, min_inds = [], []
        for i in range(n_ranks):
            # Find entries with next-smaller maximum value:
            max_inds.append(np.nonzero(array == uni[-(i + 1)])[0])
            # Find entries with next-larger minimum value:
            min_inds.append(np.nonzero(array == uni[i])[0])
    else:
        # Indices for whole range of ranks:
        max_inds = np.nonzero(array >= uni[-n_ranks])[0]
        min_inds = np.nonzero(array <= uni[n_ranks - 1])[0]
    return max_inds, min_inds


def longest_segment(array):
    """ Finds the longest segment of consecutive non-zero values in array.
        Individual segments must be separated by at least one zero value.
        Different consecutive non-zero values are treated as a single segment.
        Values of zero or False are not considered as segments.

    Parameters
    ----------
    array : 1D array of floats, ints or bools (m,)
        Array to check for longest segment. Must contain some values of zero or
        False against which to identify non-zero segments.

    Returns
    -------
    longest : 1D array of bools (m,)
        Indices of longest non-zero segment in array. If several segments have
        the same length, returns the first one.
    """    
    # Label consecutive segments:
    labeled_array, _ = label(array)
    # Get segment lengths (ignore zeros):
    counts = np.bincount(labeled_array)
    counts[0] = 0
    # Indices of longest segment:
    longest_segment = (labeled_array == counts.argmax())
    return longest_segment


## AXES GENERATION ##


def mirror_linspace(max_val=None, rate=None, n_half=None, delta=None):
    """ Linearly scaled axis, precisely mirrored around zero.
        Axis consists of two half-ranges plus zero. Arguments are optimized for
        time axis generation, but function can be used for any linear axis.
        Must be provided with either max_val or n_half, everything else is
        optional.

    Parameters
    ----------
    max_val : float or int, optional
        Largest absolute non-zero value in half-range. Always included in axis,
        but may not always be the precise endpoint (depending on specified
        sampling). Used to calculate number of values per half-range if n_half
        is None, else ignored. The default is None.
    rate : float or int, optional
        If specified, used as sampling rate of axis (in Hz, if a time axis is
        desired). Else, calculated from sampling interval delta, or set to 1 if
        neither is given. The default is None.
    n_half : int, optional
        Number of values per half-range. If specified, overrides max_val and
        adjusts limits of axis to contain the desired number of samples,
        according to rate. The default is None.
    delta : float, optional
        If specified, used as sampling interval of axis (in s, if a time axis
        is desired). Used to calculate sampling rate if rate is not specified,
        else ignored. The default is None.

    Returns
    -------
    full_range : 1D array of floats (2 * n_half + 1,)
        Linear axis with equal negative and positive values, centered around a
        value of zero.
    """    
    # Input interpretation:
    if rate is None:
        rate = 1 / delta if delta is not None else 1
    if n_half is None:
        n_half = int(np.ceil(max_val * rate))
    # Initialize array and generate half-range:
    full_range = np.zeros(2 * n_half + 1)    
    half_range = np.arange(1, n_half + 1) / rate
    # Mirror half-range around zero:
    full_range[:n_half] = -half_range[::-1]
    full_range[-n_half:] = half_range
    return full_range


def mirror_logspace(n_half, exp_low, exp_high):
    """ Logarithmically scaled axis (base 10), precisely mirrored around zero.
        Axis consists of two half-ranges (each with n_half values) plus zero.

    Parameters
    ----------
    n_half : int
        Number of values per half-range.
    exp_low : float or int
        Exponent of smallest absolute non-zero value in half-range.
    exp_high : float or int
        Exponent of largest absolute non-zero value in half-range. Determines
        minimum (negative) and maximum (positive) value of the full axis.

    Returns
    -------
    full_range : 1D array of floats (2 * n_half + 1,)
        Logarithmic axis with equal negative and positive values, centered
        around a value of zero.
    """
    # Initialize array and generate half-range:    
    full_range = np.zeros(2 * n_half + 1)
    half_range = np.logspace(exp_low, exp_high, n_half, endpoint=True)
    # Mirror half-range around zero:
    full_range[:n_half] = -half_range[::-1]
    full_range[-n_half:] = half_range
    return full_range


def make_circle(radius=1., x_off=0., y_off=0., n=1000, full=False):
    """ Generates x- and y-coordinates for a (half) circle of given radius.

    Parameters
    ----------
    radius : float or int, optional
        Radius of the circle. The default is 1.0.
    x_off : float or int, optional
        Offset of the circle along the x-axis. The default is 0.
    y_off : float or int, optional
        Offset of the circle along the y-axis. The default is 0.
    n : int, optional
        Number of coordinates to generate. The default is 1000.
    full : bool, optional
        If True, returns x and y for a full circle, where each x-value has two
        corresponding y-values. Else, returns only the top half of the circle,
        which is a proper single-valued function. The default is False.

    Returns
    -------
    x : 1D array of floats (n,)
        The x-coordinates of the circle. Contains duplicates if full is True.
    y : 1D array of floats (n,)
        The y-coordinates of the circle.
    """    
    if full:
        phase = np.linspace(0, 2 * np.pi, n)
        x = radius * np.cos(phase)
        y = radius * np.sin(phase)
    else:
        x = np.linspace(-radius, radius, n)
        y = np.sqrt(radius**2 - x**2)
    return x + x_off, y + y_off


## RECURSIVE FUNCTIONS ##


def flat_list(nested):
    """ Recursive list flattening over arbitrary levels of nested sub-lists.

    Parameters
    ----------
    nested : list of nested lists (arbitrary length and content)
        Primary list to flatten until it contains no more sub-lists. Sub-lists
        can be nested to an arbitrary depth. May contain non-list data types at
        any given level.

    Returns
    -------
    flattened : list (m,)
        Fully flattened primary list without any remaining sublists. Retains
        original order of elements.
    """
    # Append elements of next-deeper nesting level:
    wrapped = [item if isinstance(item, list) else [item] for item in nested]  
    flattened = sum(wrapped, [])
    # Check for remaining sub-lists and recurse if necessary:                                               
    has_sublist = any(isinstance(item, list) for item in flattened)      
    return flat_list(flattened) if has_sublist else flattened


def flat_iterable(nested, same_type=False):
    """ Recursively flattens a nested structure of lists, tuples, or arrays.

    Parameters
    ----------
    nested : list or tuple or np.ndarray
        Wrapper iterable to flatten until it holds no more nested structures.
    same_type : bool, optional
        If True, assumes that any nested element is of the same type as the
        wrapper iterable for all levels of nesting. If False, type-checks for
        lists, tuples, and arrays, excluding strings. The default is False.

    Returns
    -------
    nested : type(nested)
        Fully flattened wrapper iterable of the same type as the input thats
        holds no more lists, tuples or arrays. Retains order of input elements.
    """    
    # Simple numpy early exit:
    if isinstance(nested, np.ndarray):
        return nested.flat()
    # Flatten list or tuple input:
    type_class = nested.__class__
    if same_type:
        # All elements have type of first nesting level:
        check_type = lambda v: isinstance(v, type_class)
        wrap = lambda v: v if check_type(v) else type_class((v,))
    else:
        # Recognize list, tuple, and array elements, excluding strings:
        check_type = lambda v: isinstance(v, (list, tuple, np.ndarray))
        wrap = lambda v: type_class((*v,) if check_type(v) else (v,))
    # Collapse the current first nesting level of the input:
    nested = sum(type_class(wrap(v) for v in nested), start=type_class())
    # Check for deeper levels of nesting:
    sublevels = any(check_type(v) for v in nested)
    return flat_iterable(nested, same_type) if sublevels else nested


def combination_array(components):
    """ Unique element combinations from multiple hierachically nested arrays.
        Elements of arrays in tuple containers are combined cross-wise using
        itertools.product() into n = n1 * n2 * ... * ni possible combinations.
        Elements of same-size arrays in list containers are combined pair-wise
        by zip() into n = n1 = n2 = ... = ni combinations. Recursively resolves
        deeper levels of nesting until no more containers remain and flattens
        the final result into a 2D array (combinations x components).

    Parameters
    ----------
    components : tuple or list of (nested containers of) 1D arrays
        Hierarchically nested tuple/list container structure holding arrays
        whose elements are to be combined. Tuples mean cross-combination, lists
        pair-wise combination (parallelization, requires equal array lengths).
        Note that (a, b, c) is equivalent to ((a, b), c) and (a, (b, c)), since
        nesting within the product is not preserved in the flattened output.

    Returns
    -------
    combinations : 2D array
        Unique combinations of elements from the input components. Each row
        corresponds to one combination, each column to one array in components.
    """    
    # Prepare type-dependent component linking:
    link_func = {list: safe_zip, tuple: product}
    link_components = link_func[type(components)]

    # Identify tuple and list containers in wrapper as nested components:
    check_nesting = lambda comp: [isinstance(c, (tuple, list)) for c in comp]
    is_nested = check_nesting(components)

    # Input interpretation:
    if not any(is_nested):
        return np.array(list(link_components(*components)))

    # Ensure mutable wrapper:
    components = [*components]

    # Iteratively resolve nested components:
    for ind in np.nonzero(is_nested)[0]:
        # Check for any nested sub-components:
        if any(check_nesting(components[ind])):
            # Recursively resolve next-deeper nesting level:
            components[ind] = combination_array(components[ind])
            continue
        link_subcomponents = link_func[type(components[ind])]
        components[ind] = np.array(list(link_subcomponents(*components[ind])))
    return np.array([flat_iterable(c) for c in link_components(*components)])


def spread_shuffle(data, n_near=1, attempts=100):
    """ Shuffles data so that neighbouring entries are separated.
        Restarts recursively when running into dead ends.

    Parameters
    ----------
    data : list or 1D array of ints or floats (m,)
        Data to be shuffled. If list, shuffles only top-level entries.
    n_near : int, optional
        Number of entries that define the neighbourhood left and right of each
        value in data. Neighbouring entries of the last picked value are 
        blocked for the next random pick. If too large (so that neighbourhood
        of a central entry would cover all of data), throws a warning and
        reduces n_near to len(data) // 2 - 1. The default is 1, corresponding
        to the two direct neighbours of the last pick.
    attempts : int, optional
        Number of times to retry shuffling when running into dead ends before
        giving up. The default is 100.

    Returns
    -------
    new_data : list or 1D array of ints or floats (m,)
        Shuffled data that satisfies the specified neighbourhood requirement.
        Throws a warning and returns original data if no valid shuffle could be
        found within the specified number of attempts.
    """                                   
    # Input interpretation:
    n = len(data)
    new_data = np.zeros(n) if 'np' in str(type(data)) else np.zeros(n).tolist()
    if n_near >= n // 2:
        # Reduce if n_near covers entire data (for entry at center):
        print('WARNING: n_near is too large for shuffling. '\
              f'Reduced n_near from {n_near} to {n // 2 - 1}.')
        n_near = n // 2 - 1
    # Initiate shuffle:
    free = np.full(n, True)
    # Pick first entry:
    ind = np.random.choice(n)
    new_data[0] = data[ind]
    free[ind] = False
    for i in range(1, n):
        # Neighbourhood of last pick:            
        lower = max(0, ind - n_near)                                        
        upper = min(n - 1, ind + n_near)
        # Indices of neighbouring and available entries:                                       
        nearby = np.isin(np.arange(n), np.arange(lower, upper + 1))
        options = free & ~nearby
        # Handle dead ends:
        if np.sum(options) == 0:
            attempts -= 1
            if attempts == 0:
                # Return unsuccessful:
                print('WARNING: Used all attempts. Shuffling failed!')
                return data
            else:
                # Retry:
                return spread_shuffle(data, n_near, attempts)
        # Pick next entry:                                               
        ind = np.random.choice(np.arange(n)[options])
        new_data[i] = data[ind]
        free[ind] = False
    return new_data


# SONGDETECTOR-SPECIFIC FUNCTIONS:


def lowpass_props(cutoff=None, tau=None, rise=None):
    """ Cut-off frequency, time constant and rise time of a low-pass filter.
        Estimates the two missing properties based on the specified one.
        Estimated properties are only valid for a first-order low-pass filter!

    Parameters
    ----------
    cutoff : float, optional
        Cut-off frequency of the low-pass filter in Hz. Used to estimate tau
        and, from that, rise. The default is None.
    tau : float, optional
        Time constant of the low-pass filter in seconds. Used to estimate
        cutoff and rise time. The default is None.
    rise : float, optional
        Rise time (to change signal from 10% to 90% of final value) of the
        low-pass filter in seconds. Used to estimate tau and, from that,
        cutoff. The default is None.

    Returns
    -------
    properties : dict
        Properties of the first-order low-pass filter in the order 'cutoff',
        'tau' and 'rise'. Always returns all three parameters, including the 
        one that was specified.
    """    
    if cutoff is not None:
        tau = 1 / (2 * np.pi * cutoff)
        rise = 2.197 * tau
    elif tau is not None:
        cutoff = 1 / (2 * np.pi * tau)
        rise = 2.197 * tau
    elif rise is not None:
        tau = rise / 2.197
        cutoff = 1 / (2 * np.pi * tau)
    properties = {'cutoff': cutoff, 'tau': tau, 'rise': rise}
    return properties


def artificial_song(rate, pause=None, syllable=None, n_cycles=5,
                    duration=None, period=None, duty_cycle=None,
                    pause_value=-1.0, syl_values=1.0, syl_segments=None,
                    syllable_first=False, center_mean=False):
    """ Customizable "grasshopper song" of alternating pauses and syllables.
        Basic structure is that of a box-car function with varying temporal
        parameters and amplitude values. Syllables may have a more complex
        shape defined by a sequence of sub-segments with different values.       
        Temporal characteristics may be specified by various argument
        combinations (in the order of evaluation):
            1) Syllable duration and pause duration
            2) Duty cycle and period duration
            3) Period duration and pause duration
            4) Period duration and syllable duration
        Invalid combinations of arguments will raise a ValueError.

    Parameters
    ----------
    rate : float or int
        Sampling rate of the song in Hz. All temporal input parameters are
        are given in seconds and will be converted to points using this rate.
    pause : float or int, optional
        Pause duration of a single song cycle in seconds. Used to calculate
        period if specified together with syllable. Used to calculate syllable
        if specified together with period. Calculated from period and syllable
        or period and duty_cycle if those are specified, respectively. The
        default is None.
    syllable : float or int, optional
        Syllable duration of a single song cycle in seconds. Used to calculate
        period if specified together with pause. Used to calculate pause if
        specified together with period. Calculated from period and syllable or
        period and duty_cycle if those are specified, respectively. The default
        is None.
    n_cycles : int, optional
        Number of repetitions of the song cycle, which consists of a pause and
        a syllable. Ignored if duration is specified. The default is 5.
    duration : float or int, optional
        Total song duration in seconds. Overrides n_cycles if specified.
        Expanded to fit an integer number of song cycles. The default is None.
    period : float or int, optional
        Duration of a single song cycle in seconds. Calculated from pause and
        syllable if those are specified. Used to calculate syllable if
        specified together with pause (and vice versa). Used to calculate both
        pause and syllable if specified together with duty_cycle. The default
        is None.
    duty_cycle : float, optional
        Ratio of syllable duration to period duration. Used to calculate both
        pause and syllable if specified together with period. The default is
        None.
    pause_value : float or int, optional
        Constant value of the song amplitude during pauses. The default is -1.
    syl_segments : list of floats (m,), optional
        If specified, defines the relative length of different syllable sub-
        segments. The sum of all segments must be 1 to produce correct results.
        The default is None.
    syl_values : float or list (m,) of floats/tuples of floats (2,), optional
        Value(s) of the song amplitude during syllables. If scalar, results in
        a constant amplitude, similar to pause_value. If list, must be given
        together with syl_segments. Scalar entries result in a flat plateau for
        a given sub-segment. Tuples result in a linear ramp from the first to
        the second value. If pause is 0, this argument allows to control the 
        structure of the entire song cycle. The default is 1.
    syllable_first : bool, optional
        If True, starts each song cycle with a syllable. If False, start with
        a pause. The default is False.
    center_mean : bool, optional
        If True, subtracts the mean from the finalized song to balance positive
        and negative integrals. The default is False.

    Returns
    -------
    song : array of floats (n,)
        Artificial grasshopper song with the specified parameters.

    Raises
    ------
    ValueError
        Breaks if the combination of provided temporal parameters (pause,
        syllable, period, and/or duty_cycle) is not sufficient to characterize
        the song cycle.
    """    
    # Input interpretation (cycle parameters):
    if pause is not None and syllable is not None:
        period = syllable + pause   
    elif duty_cycle is not None and period is not None:
        syllable = period * duty_cycle
        pause = period - syllable
    elif syllable is None and period is not None and pause is not None:
        syllable = period - pause
    elif pause is None and period is not None and syllable is not None:
        pause = period - syllable
    else:
        msg = 'Invalid combination of pause, syllable, period, and duty_cycle.'
        raise ValueError(msg)
    # Input interpretation (cycle repetitions):
    if duration is not None:
        n_cycles = int(np.ceil(duration / period))
    # Basic cycle components:
    period_unit = np.zeros(int(period * rate)) + pause_value
    syl_unit = np.ones(int(syllable * rate))
    if isinstance(syl_values, (float, int)):
        syl_unit *= syl_values
    # Optional customized syllable shape:
    if syl_segments is not None and syl_values is not None:
        # Length of and transitions between syllable segments in points:
        intervals = [int(segment * len(syl_unit)) for segment in syl_segments]
        steps = np.cumsum([0] + intervals)
        # Fill segments with different values:
        for i, value in enumerate(syl_values):
            if isinstance(value, (list, tuple)):
                # Linear ramp instead of flat plateau:
                value = np.linspace(value[0], value[1], intervals[i])
            syl_unit[steps[i]:steps[i + 1]] = value
    # Pause-syllable order:
    if syllable_first:
        period_unit[:len(syl_unit)] = syl_unit
    else:
        period_unit[-len(syl_unit):] = syl_unit
    # Assemble song:
    song = np.tile(period_unit, n_cycles)
    if center_mean:
        song -= np.mean(song)
    return song


def song_series(rate, varied, n_iter, fixed={}):
    """ Wrapper for repeated calls to artificial_song() with varying arguments.
        Generates and appends a new segment to the song for each iteration.

    Parameters
    ----------
    rate : float or int
        Sampling rate of the song in Hz. All temporal input parameters are
        are given in seconds and will be converted to points using this rate.
    varied : dict of iterables
        Varied input arguments (keys) and their respective values for each
        iteration. All iterables must have length n_iter. Keys must match
        keyword argument names of artificial_song().
    n_iter : int
        Number of song segments to append. Must be equal to the length of each
        iterable in varied.
    fixed : dict, optional
        Constant input arguments (keys) and their respective values, which are
        the same for each iteration. Keys must match keyword argument names of
        artificial_song(). Default is {}.

    Returns
    -------
    song : 1D array of floats (m,)
        Artificial "grasshopper song" with changing parameters over time.
    segment_code : 1D array of ints (m,)
        Segment-specific labels for each datapoint in the song. Tag values are 
        in the range [0, n_iter - 1].
    """    
    # Initialize parameter configuration:
    kwargs = {'rate': rate}
    kwargs.update(fixed)
    song, segment_code = [], []
    for i in range(n_iter):
        # Iterate and update to next version of varied parameters:
        [kwargs.update({key: value[i]}) for key, value in varied.items()]
        # Generate song and encode segment:
        song.append(artificial_song(**kwargs))
        segment_code.append(np.ones(len(song[-1]), dtype=int) * i)
    return np.concatenate(song), np.concatenate(segment_code)
