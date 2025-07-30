import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import label
from .misctools import ensure_array
from .plottools import plot_spectrogram


# GENERAL & APPLIED SEGMENT IDENTIFICATION:


def label_along_axis(array, axis=0):
    """ Wrapper to scipy.ndimage.label() that connects only along a given axis.
        Marks segments of consecutive non-zero elements along axis of the input
        array with unique integer labels. Does not distinguish between non-zero
        elements of different values. Neighbouring non-zero elements along any
        dimension other than axis are not connected. Individual segments along
        axis must be separated by at least one zero element.

    Parameters
    ----------
    array : ND array of floats, ints, or bools (any shape)
        Input array in which to mark segments.
    axis : int, optional
        Target dimension of array along which to connect non-zero elements.
        The default is 0.

    Returns
    -------
    marked_segments : ND array of ints (array.shape)
        Labeled array with unique label values for each non-zero segment. Label
        values are in [1, n_segments]. Other elements have a value of 0. 
    n_segments : int
        Total number of non-zero segments in marked_segments.
    """
    # Equilateral connectivity matrix:
    structure = np.zeros((3,) * array.ndim)
    # Connect only along axis:
    connect_ind = [1] * array.ndim
    connect_ind[axis] = slice(None)
    # Insert centered connector bar:
    structure[tuple(connect_ind)] = 1
    return label(array, structure)


def bundle_inds(array):
    """ Finds separate segments of consecutive non-zero data points in array.
        Individual segments must be separated by at least one zero value.
        Different consecutive non-zero values are treated as a single segment.
        Values of zero or False are not considered in the returned indices.

    Parameters
    ----------
    array : 1D array of ints, floats, or bools (m,)
        Array in which to find and bundle segment indices. Must contain some
        values of zero or False against which to identify non-zero segments.

    Returns
    -------
    inds : list (n,) of 1D arrays of ints (p,)
        Indices of each non-zero segment in array. Returns an empty list if no 
        non-zero segments are found (that is, if array is all zero).
    """    
    marked_segs, n_segs = label(array.ravel())
    inds = [np.nonzero(marked_segs == i)[0] for i in range(1, n_segs + 1)]
    return inds


def bundle_songs(spec_code, spec_list, do_noise=False, file_code=None):
    """ Finds species-specific song segments (and noise) in spec_code.
        Applies bundle_inds() to song labels as tagged by encoder().

    Parameters
    ----------
    spec_code : 1D array of ints (m,)
        Species-specific song labels for each datapoint, indicating the
        position of the associated species among all species in spec_list.
        Expected tag values are in the range [1, n] and 0 for noise.
    spec_list : list of str (n,)
        Names of all included species.
    do_noise : bool, optional
        If True, returns indices of noise segments in addition to songs. Noise
        across file boundaries is treated as a single segment, except when
        file_code is specified. The default is False.
    file_code : 1D array of ints, optional
        File tag for each datapoint, indicating the position of the associated
        file among all files. Expected tag values start at 1 and end with the
        total number of files. If specified, returns indices of noise segments
        even if do_noise is False. Noise segments are separated at file
        boundaries. The default is None.

    Returns
    -------
    songs : dict of lists (p,) of 1D arrays of ints (q,)
        Indices of individual song segments for each species (keys). May
        contain empty lists if no song segments are found for a species.
    noise : list (r,) of 1D arrays of ints (s,)
        Indices of noise segments between songs. Only returned if do_noise is
        True or file_code is specified.
    """    
    # Indices of species-specific song segments:
    tags = range(1, len(spec_list) + 1)
    songs = {s: bundle_inds(spec_code == i) for s, i in zip(spec_list, tags)}
    # Indices of noise segments between songs:
    if do_noise or (file_code is not None):
        ind = spec_code == 0
        if file_code is not None:
            # Separate noise at file boundaries:
            tags = range(1, np.max(file_code) + 1)
            noise = [bundle_inds((file_code == tag) & ind) for tag in tags]
        else:
            # Noise segments across files:
            noise = bundle_inds(ind)
        return songs, noise
    return songs


def bundle_detections(predict):
    """ Finds detected segments for each species-specific model in predict.
        Applies bundle_inds() to binary model predictions. Input format
        determines output format.

    Parameters
    ----------
    predict : dict of 1D arrays of floats (m,) or 2D array of floats (m, n)
        Predictions of n models over m datapoints (1 = detected, 0 = rejected).

    Returns
    -------
    inds : dict or list (n,) of lists (p,) of 1D arrays of ints (q,)
        Indices of model-specific detection segments. If input is dict, output
        is dict of lists with the same keys. If input is array, output is list
        of lists, each of which corresponds to a column in the input array.
    """    
    if isinstance(predict, dict):
        # Model detections for saving and printing:
        inds = {key: bundle_inds(predict[key]) for key in predict.keys()}
    elif isinstance(predict, np.ndarray):
        # Model detections in less explicit compact format:
        inds = [bundle_inds(predict[:, i]) for i in range(predict.shape[1])]
    return inds


def find_segment(array, target='max', index=None, eval_func='any'):
    """ Selects one or multiple segments meeting the specified criterion.
        Applies bundle_inds() to array to find separate segment indices of
        consecutive non-zero data points, then selects matching segments from
        the list. Can target the longest or shortest segment, or any segment(s)
        containing specific target indices. 

    Parameters
    ----------
    array : 1D array of ints, floats, or bools (m,)
        Array in which to find and bundle segment indices for selection. Must
        contain some values of zero or False against which to identify
        non-zero segments.
    target : str, optional
        Criterion for selecting target segments. Options are 'max' (longest),
        'min' (shortest), or 'ind' (containing target indices). If 'ind', the 
        index (required) and eval_func keyword arguments control selection
        fine-tuning. The default is 'max'.
    index : int or 1D array or list (n,) of ints, optional
        Target index or indices for segment selection. Required if target is
        'ind', else ignored. For multiple targets, eval_func controls whether
        any or all of them must be present in a segment. The default is None.
    eval_func : str, optional
        Operation to evaluate presence of target indices in each segment (if
        target is 'ind', else ignored). If 'all', all targets must be contained
        within a single segment, which is returned immediately once found. If
        'any', a segment must contain at least one target to be selected,
        resulting in up to len(index) returned segments. The default is 'any'.

    Returns
    -------
    segments : 1D array (p,) of ints or list (q,) of 1D arrays of ints
        Identified segment indices in array that match the specified criterion.
        If target is 'max', 'min', or 'ind' with eval_func 'all', returns the
        selected segment as a single array of indices. If target is 'ind' with
        eval_func 'any' (enables multiple matches), returns a list of arrays,
        even if only a single segment is selected.

    Raises
    ------
    ValueError
        Breaks if no segments could be found for the given target criterion.
    """    
    # Bundle consecutive indices:
    ind_segments = bundle_inds(array)

    # Target segment(s) by included indices:
    if index is not None and target == 'ind':
        # Assert array format:
        index = ensure_array(var=index, dtype=int, shape=(-1,))
        segments = []

        # Check for target indices:
        for segment in ind_segments:
            # Find targets contained in current segment:
            intersection = np.intersect1d(segment, index)
            if len(intersection) == len(index):
                # Early exit if one segment contains all indices:
                return segment if eval_func == 'all' else [segment]
            elif eval_func == 'any' and len(intersection):
                # Log and continue:
                segments.append(segment)
                
        if not len(segments):
            # Report failure under given match criterion:
            ind = 'indices' if len(index) > 1 else 'index'
            s = 's' if (eval_func == 'any') and (len(index) > 1) else ''
            raise ValueError(f'No segment{s} found for target {ind} {index}.')
        return segments

    # Target segment by number of data points:
    lengths = [len(seg) for seg in ind_segments]
    if target == 'max':
        # Find longest segment:
        return ind_segments[np.argmax(lengths)]
    elif target == 'min':
        # Find shortest segment:
        return ind_segments[np.argmin(lengths)]


def edge_to_binary(edges, rate, n, dtype=bool):
    """ Converts time intervals into a binary label array with given sampling.
        Time points within each labeled segment are set to 1, else 0. Allows to
        adapt label information to the rate and size of some reference array.

    Parameters
    ----------
    edges : 2D array (m, 2) or list (m,) of lists (2,) of floats or ints
        Start and end time points of each labeled segment in s.
    rate : float or int
        Sampling rate of the reference array and the returned labels in Hz.
    n : int
        Number of samples in the reference array and the returned labels.
    dtype : type, optional
        Numpy data type of the returned label array. The default is bool.

    Returns
    -------
    labels : 1D array of dtype (n,)
        Binary label array corresponding to the reference array. Overlapping
        time intervals are merged into a single continuous segment.
    """
    labels = np.zeros(n, dtype=dtype)
    time = np.arange(n) / rate
    for edge in edges:
        labels[(time >= edge[0]) & (time <= edge[1])] = 1
    return labels


def edge_to_inds(edges, rate, n):
    """ Converts time intervals into indices along some reference array.
        First creates a binary label array of rate and size of the reference,
        then bundles the indices of time points within each labeled segment.

    Parameters
    ----------
    edges : 2D array (m, 2) or list (m,) of lists (2,) of floats or ints
        Start and end time points of each labeled segment in s.
    rate : float or int
        Sampling rate of the reference array in Hz.
    n : int
        Number of samples in the reference array.

    Returns
    -------
    inds : list (m,) of 1D arrays (n,) of ints
        Indices of time points within each labeled segment along the reference.
        Segment order corresponds to temporal order, not to the order in edges.
        Overlapping time intervals are merged into a single continuous segment.
    """    
    return bundle_inds(edge_to_binary(edges, rate, n))


# SEGMENT CLEANUP:


def defragment(array, tol, rel_tol=None, replace=0, as_ind=False,
               skip_single=False):
    """ Removes non-zero segments if their length is below tolerance.
        Applies bundle_inds() to array to identify individual segments.

    Parameters
    ----------
    array : 1D array of ints, floats, or bools (m,)
        Array to defragment. Values of zero or False are not considered during
        the defragmentation.
    tol : int or None
        Minimum tolerated length of a single non-zero segment. If None,
        immediately returns array without changes.
    rel_tol : float, optional
        If specified, overrides tol with a flexible criterion relative to the
        length of the largest non-zero segment in array. The default is None.
    replace : int, float, or bool, optional
        Sets gap segments below tolerance to the given value. Can be used to
        specify a desired datatype should the insertion of value into array
        fail unexpectedly. The default is 0.
    as_ind : bool, optional
        If True, returns indices of remaining non-zero segments in the
        defragmented array instead of the array itself. If replace is non-zero,
        the result is identical to calling np.nonzero() on the original array.
        The default is False.
    skip_single : bool, optional
        If True, leaves array unchanged if it contains only a single non-zero
        segment. The default is False.

    Returns
    -------
    data : 1D array of ints, floats, or bools (m,) or 1D array of ints (n,)
        Defragmented array, or indices of remaining non-zero segments if as_ind
        is True. Returns unchanged array if tol is None, array contains no
        segments, or array contains a single segment and skip_single is True.
    """    
    # Silent skip:
    if tol is None:
        return array
    # Find segments and handle other skips:
    segments = bundle_inds(array)
    if len(segments) == 0:
        # Nothing labeled:                                                     
        print('WARNING: No non-zero segments found for defragmentation.')
        return array
    elif skip_single and len(segments) == 1:                              
        return array
    # Segment lengths and flexible tolerance:
    len_segments = [len(segment) for segment in segments]
    if rel_tol is not None:
        tol = int(rel_tol * np.max(len_segments))
    data = array.copy()
    # Apply tolerance criterion:
    for segment, n in zip(segments, len_segments):
        if n < tol:
            data[segment] = replace
    return np.nonzero(data)[0] if as_ind else data


def desegment(array, tol, rel_tol=None, replace=1, as_ind=False, 
              with_edges=False):
    """ Fills gaps between non-zero segments if gap length is below tolerance.
        Applies bundle_inds() to array to identify individual gap segments.

    Parameters
    ----------
    array : 1D array of ints, floats, or bools (m,)
        Array to desegment. Non-zero values are not considered during the
        desegmentation.
    tol : int or None
        Minimum tolerated length of a single gap segment. If None, immediately
        returns array without changes.
    rel_tol : float, optional
        If specified, overrides tol with a flexible criterion relative to the
        length of the largest gap segment in array. The default is None.
    replace : ints, float, or bool, optional
        Sets gap segments below tolerance to the given value. Can be used to
        specify a desired datatype should the insertion of value into array
        fail unexpectedly. The default is 1.
    as_ind : bool, optional
        If True, returns indices of merged non-zero segments in the desegmented
        array instead of the array itself. If replace is not non-zero, the
        result is identical to calling np.nonzero() on the original array. The
        default is False.
    with_edges : bool, optional
        If True, applies tolerance criterion to gap segments that include the 
        first or last index of array. Else, omits these edge gaps from 
        desegmentation. The default is False.

    Returns
    -------
    data : 1D array of ints, floats, or bools (m,) or 1D array of ints (n,)
        Desegmented array, or indices of merged non-zero segments if as_ind
        is True. Returns unchanged array if tol is None or array contains no
        gap segments.
    """    
    # Silent skip:
    if tol is None:
        return array
    # Find segments and handle other skips:
    segments = bundle_inds(array == 0)
    if len(segments) == 0:
        print('WARNING: No unlabeled segments found for desegmentation.')
        return array
    # Handle edge cases:
    if not with_edges:
        # Omit gap at start:
        if segments[0][0] == 0:
            segments = segments[1:]
        # Omit gap at end:
        if segments[-1][-1] == len(array) - 1:
            segments = segments[:-1]
    # Segment lengths and flexible tolerance:
    len_segments = [len(segment) for segment in segments]
    if rel_tol is not None:
        tol = int(rel_tol * np.max(len_segments))
    data = array.copy()
    # Apply tolerance criterion:
    for segment, n in zip(segments, len_segments):
        if n < tol:
            data[segment] = replace
    return np.nonzero(data)[0] if as_ind else data


# def enhance_contrast(signal, rate, mode='std', pre_filter=None,
#                      pre_cutoff=None, pre_order=1, env_cutoff=None, n_env=3,
#                      min_env=1, max_env=None, window=100, reducer='mean',
#                      log=True, cap=1e-3, square=False, post_filter=None,
#                      post_cutoff=None, post_order=1, crop_noise=False, norm=True):
#     """ Useful transformations to support threshold-based event detection.
#         The signal undergoes a main transformation specified by mode, which is
#         either based on envelope extraction or a sliding window statistics.
#         Transformation can be applied independently on multiple time-scales, in
#         which case the different outputs are condensed back into a single time
#         series using the given reducer function. Afterwards, the signal can
#         be re-scaled by logarithm and/or squaring. Pre-filtering (before main
#         transformation) and post-filtering (after re-scaling) each support low-
#         pass, high-pass, and band-pass filters of given order and cut-off.

#     Parameters
#     ----------
#     signal : 1D array (m,) or 2D array (m, 1) of floats
#         _description_
#     rate : _type_
#         _description_
#     mode : str, optional
#         _description_, by default 'std'
#     pre_filter : _type_, optional
#         _description_, by default None
#     pre_cutoff : _type_, optional
#         _description_, by default None
#     pre_order : int, optional
#         _description_, by default 1
#     env_cutoff : _type_, optional
#         _description_, by default None
#     n_env : int, optional
#         _description_, by default 3
#     min_env : int, optional
#         _description_, by default 1
#     max_env : _type_, optional
#         _description_, by default None
#     window : int, optional
#         _description_, by default 100
#     reduce : str, optional
#         _description_, by default 'mean'
#     log : bool, optional
#         _description_, by default True
#     cap : _type_, optional
#         _description_, by default 1e-3
#     square : bool, optional
#         _description_, by default False
#     post_filter : _type_, optional
#         _description_, by default None
#     post_cutoff : _type_, optional
#         _description_, by default None
#     post_order : int, optional
#         _description_, by default 1
#     crop_noise : bool, optional
#         _description_, by default True
#     norm : bool, optional
#         _description_, by default True

#     Returns
#     -------
#     _type_
#         _description_

#     Raises
#     ------
#     ValueError
#         _description_
#     ValueError
#         _description_
#     """    
#     # Input interpretation:
#     if signal.ndim == 1:
#         signal = signal[:, None]
#     elif signal.ndim != 2 or signal.shape[1] != 1:
#         raise ValueError('Signal must be 1D or a single 2D column.')

#     # Pre-filtering (low-pass, high-pass, or band-pass):
#     if pre_filter is not None and pre_cutoff is not None:
#         signal = sosfilter(signal, rate, pre_cutoff, pre_filter, pre_order)

#     # Envelope extraction:
#     if mode == 'env':
#         # Manage low-pass bank:
#         if env_cutoff is None:
#             if max_env is None:
#                 max_env = rate // 2
#             # Auto-generate range of cut-off frequencies:
#             min_env, max_env = np.log10(min_env), np.log10(max_env)
#             env_cutoff = np.logspace(min_env, max_env, n_env)
#         # Multi-scale temporal averaging by low-pass filtering:
#         output = multi_lowpass(signal, rate, env_cutoff, rectify=True)

#     # C-implemented sliding window statistics:
#     elif mode in ('sum', 'mean', 'std', 'var', 'min', 'max',
#                   'argmin', 'argmax', 'median', 'rank'):
#         # Assert iterable:
#         window = check_list(window)
#         # Manage window interpretation (seconds or samples):
#         window = [int(w * rate) if isinstance(w, float) else w for w in window]
#         # Sliding window(s) of specified measure:
#         output = np.zeros((len(signal), len(window)))
#         for i, win in enumerate(window):
#             output[:, i] = bn_window(signal, win, mode, fix_edge=True)[:, 0]
#     else:
#         raise ValueError(f'Invalid mode for contrast enhancement: {mode}')

#     # Post-processing:
#     reducer_func = {
#         'sum': np.sum,
#         'prod': np.prod,
#         'mean': np.mean,
#         'std': np.std,
#         'median': np.median
#         }[reducer]
#     # Condense into single time series:
#     contrast = reducer_func(output, axis=1)
#     if log:
#         # Functional contrast enhancement:
#         contrast = decibel(contrast - min(contrast), lower_bound=cap)
#     if square:
#         # Visual contrast enhancement:
#         contrast = (contrast - min(contrast))**2
#     if post_filter is not None and post_cutoff is not None:
#         # Post-filtering (low-pass, high-pass, or band-pass):
#         contrast = sosfilter(contrast, rate, post_cutoff,
#                              post_filter, post_order)
#     if crop_noise:
#         n_bins = 1000
#         win = n_bins // 100
#         crit =0
#         # Get distribution of transformed data:
#         hist, edges = np.histogram(contrast, bins=n_bins, density=True)
#         hist = bn_window(hist[1:], win, 'max', fix_edge=False)
#         centers = (edges[:-1] + np.diff(edges) / 2)[1:]
#         hist_diff = np.diff(hist)
#         # Estimate segments of non-zero derivative:
#         up_slopes = bundle_inds(hist_diff > 0)
#         down_slopes = bundle_inds(hist_diff < 0)
#         up_lengths = [len(seg) for seg in up_slopes]
#         down_lengths = [len(seg) for seg in down_slopes]
#         up_change = [sum(hist_diff[seg]) for seg in up_slopes]
#         down_change = [sum(hist_diff[seg]) for seg in down_slopes]
#         up_derivatives = [sum(hist_diff[s]) / len(s) for s in up_slopes]
#         down_derivatives = [sum(hist_diff[s]) / len(s) for s in down_slopes]

#         # Locate major slopes in distribution:
#         up_slopes = [seg for seg in up_slopes if len(seg) > crit]
#         down_slopes = [seg for seg in down_slopes if len(seg) > crit]
#         start_ind = up_slopes[0][-1]
#         end_ind = down_slopes[0][0]
#         noise_floor = centers[(start_ind + end_ind) // 2]
#         contrast -= noise_floor
#     else:
#         # Assert non-negativity:
#         contrast -= min(contrast)
#     if norm:
#         # Re-scale to [0, 1]:
#         contrast /= max(contrast)
#     return contrast


# SONGDETECTOR CORE FUNCTIONALITY:


def label_songs(rate, threshold=None, norm=None, features=None, channels=None,
                ref_channel=None, global_ref=False, wrap=False, config=None):
    """ Identifies song events by thresholding the norm of the feature set.
        Accepts either the norm itself or the feature set to compute the norm.
        Can process a single or multiple channels. The applied threshold is
        relative to the channel-wise or global maximum of the feature norm, or
        to the maximum of a specified reference channel. Returns start and end
        time of each identified song segment to render the label information
        independent of the sampling rate.

    Parameters
    ----------
    rate : float or int
        Sampling rate of the feature set and the corresponding norm in Hz.
    threshold : float or 1D array (m,) of floats
        Threshold to apply relative to the maximum of the feature norm. Scalars
        are applied to all target channels. Arrays must have a length matching
        the number of specified target channels. The default is None.
    norm : 1D array (t,) or 2D array (t, c) of floats, optional
        Pre-computed norm over the kernel axis of the feature set (could be any
        time-series to be labeled). First axis must be time. If 1D, expects a
        single channel. If 2D, expects several channels. Ignored if features
        is specified. The default is None.
    features : 2D array (t, k) or 3D array (t, k, c) of floats, optional
        If specified, the feature set to compute the norm from. First axis must
        be time, second axis must be kernels. Calls np.linalg.norm(axis=1) to
        condense the features into the default Frobenius norm. If 2D, expects a
        single channel. If 3D, expects several channels. Overrides norm if
        specified. The default is None.
    channels : int or 1D array (m,) of ints, optional
        For multi-channel data (2D norm or 3D features), specifies a subset of
        one or more target channels for labeling. If not specified, labels all
        channels. Ignored for single-channel data. The default is None.
    ref_channel : int, optional
        For multiple target channels, specifies a single channel whose maximum
        norm is used as reference for thresholding, overriding global_ref. Must
        be one of the specified target channels. The default is None.
    global_ref : bool, optional
        If True and ref_channel is None, labels multiple target channels using
        the global maximum across channels, else relative to the maximum of
        each channel. Ignored for single target channels. The default is True.
    wrap : bool, optional
        For single target channels, returns the array of edge times wrapped in
        a tuple to match multi-channel output format. The default is False.
    config : dict, optional
        Top-level parameter configuration in the format of configuration() that
        replaces all keyword arguments except 'rate', 'norm', 'features', and
        'wrap' if specified. The default is None.

    Returns
    -------
    edges : 2D array (n, 2) or tuple (m,) of 2D arrays (n, 2) of floats
        Edge times (start, end) of identified song events in seconds, one row
        per segment. Returns one array for each target channel.

    Raises
    ------
    ValueError
        Breaks if both norm and features are None, or if norm is not 1D or 2D.
    """
    # Input interpretation:
    if features is not None:
        norm = np.linalg.norm(features, axis=1)
    elif norm is None:
        raise ValueError('Either norm or features must be specified.')
    elif norm.ndim not in (1, 2):
        raise ValueError('Norm must be a 1D or 2D array.')
    if config is not None:
        threshold = config['label_thresh']
        channels = config['label_channels']
        ref_channel = config['label_ref']
        global_ref = config['global_ref']

    # Channel subset selection:
    if channels is not None and norm.ndim == 2:
        norm = norm[:, channels]

    # Single channel:
    if norm.ndim == 1:
        # Identify consecutive supra-threshold elements:
        segments = bundle_inds(norm >= threshold * norm.max())
        # Convert to start/end time points:
        edges = np.zeros((len(segments), 2))
        for i, segment in enumerate(segments):
            edges[i] = [segment[0], segment[-1]]
        return (edges / rate,) if wrap else edges / rate

    # Multi-channel labeling:
    reference = norm.max(axis=0)
    if ref_channel is not None:
        # Relative to maximum of single reference channel:
        reference = reference[np.searchsorted(channel, ref_channel)]
    elif global_ref:
        # Relative to global maximum:
        reference = reference.max()

    # Mark consecutive supra-threshold elements in individual channels:
    marked, n_segs = label_along_axis(norm >= threshold * reference, axis=0)
    edges = [[] for _ in range(norm.shape[1])]
    for i in range(1, n_segs + 1):
        # Get segment indices along both dimensions:
        segment, channel = np.nonzero(marked == i)
        # Assign edge elements to corresponding channel:
        edges[channel[0]].append([segment[0], segment[-1]])
    # Convert to start/end time points:
    return tuple(np.array(edge) / rate for edge in edges)


def encoder(labels, path, paths, species_list=None):
    """ Tag datapoints in labels to indicate corresponding file and species.
        Used to identify specific segments within a larger appended dataset.

    Parameters
    ----------
    labels : 1D array of floats or ints or bools (m,)
        Song labels for each datapoint (1 = song, 0 = no song/noise). Any other
        values are considered buffer zones and treated as unlabeled (0). If
        zero-array, skips species encoding even if spec_list is not None.
    path : str
        Path to the current file. Current species is determined by
        correspondence between path and entries of species_list. Format of
        species name must be consistent between path and spec_list.
    paths : list of str (n,)
        Paths to all included files. File tag is index of path in paths + 1.
    species_list : list of str (p,), optional
        Names of all included species. Species tag is index of current species
        (that matches path) in spec_list + 1. If not specified, skips species
        encoding even if labels is no zero-array. The default is None.

    Returns
    -------
    file_code : 1D array of ints (m,)
        File tag for each datapoint in labels, indicating the position of the 
        current file among all files in paths. Possible tag values are in the
        range [1, n].
    species_code : 1D array of ints (m,)
        Species-specific song labels for each datapoint in labels, indicating
        the position of the current species among all species in species_list.
        If species_list is None, labels is a zero-array, or path contains
        "noise", the returned array is a zero-array of fitting length. Possible
        tag values are in the range [1, p].
    """    
    # Encode file number:
    file_code = np.zeros(len(labels), dtype=int) + (paths.index(path) + 1)
    # Encode species-specific song labels:
    if species_list is None or 'noise' in path or (np.sum(labels) == 0):
        # Disabled species code/Empty labels/Noise file:
        species_code = np.zeros(len(labels), dtype=int)
    else:
        # Treat buffer values as unlabeled (0):
        species_code = (labels == 1).astype(int)
        # Identify species corresponding to current file:
        tag = [i for i, species in enumerate(species_list) if species in path]
        species_code *= np.array(tag) + 1
    return file_code, species_code


def buffer(labels, buff_value=0., start_out=0, start_in=0, end_in=0, end_out=0,
           config=None):
    """ Applies buffer zones around edges of labeled song segments.
        Buffer zones can be used to omit data from classifier training.
        Four possible buffer zones per segment: Inward and outward at segment
        start and end, respectively. Inward buffers are limited to datapoints
        of the labeled segment, while outward buffers are limited to the
        unlabeled datapoints between neighbouring segments (independent of the
        specified extents.)

    Parameters
    ----------
    labels : 1D array of floats (m,)
        Song labels for each datapoint (1 = song, 0 = no song/noise). Any other
        non-zero values are treated as song labels.
    buff_value : float, optional
        Sets datapoints in buffer zones to the given value. May not be 1.0,
        which is the tag value to encode song segments! The default is 0.0, so
        that any noise segments are also interpreted as buffer zones during
        modification of training data by debuffer().
    start_out : int or float, optional
        Outward buffer zone at the start of each segment, excluding the first
        index of the segment. If int, the buffer extent in points. If float,
        the buffer extent as a proportion of the segment length (at least one
        point). The default is 0.
    start_in : int or float, optional
        Inward buffer zone at the start of each segment, including the first
        index of the segment. If int, the buffer extent in points. If float,
        the buffer extent as a proportion of the segment length (at least one
        point). The default is 0.
    end_in : int or float, optional
        Inward buffer zone at the end of each segment, including the last index
        of the segment. If int, the buffer extent in points. If float, the
        buffer extent as a proportion of the segment length (at least one 
        point). The default is 0.
    end_out : int or float, optional
        Outward buffer zone at the end of each segment, excluding the last
        index of the segment. If int, the buffer extent in points. If float,
        the buffer extent as a proportion of the segment length (at least one
        point). The default is 0.
    config : dict, optional
        Top-level parameter configuration in the format of configuration() that
        replaces all keyword arguments if specified. The default is None.

    Returns
    -------
    buff_labels : 1D array of floats (m,)
        Buffered song labels for each datapoint (1 = song, 0 = no song/noise,
        buff_value = buffer zone). If all specified buffer extents are 0,
        returns the unchanged labels.
    """    
    # Input interpretation:
    if config is not None:
        buff_value = config['buff_value']
        n_buff = config['n_buff']
    else:
        n_buff = [start_out, start_in, end_in, end_out]
    # Skip if no buffers are requested:
    if not any(n_buff):
        return labels
    # Find labeled segments:
    buff_labels = labels.copy()
    segments = bundle_inds(labels)
    for i, segment in enumerate(segments):
        # Segment extent:
        start = segment[0]
        end = segment[-1]
        length = len(segment)
        # Length and boundaries of each of the four buffer zones in points:
        n = [int(np.ceil(n*length)) if type(n) == float else n for n in n_buff]
        edges = np.array([start - n[0], start + n[1], end - n[2], end + n[3]])
        # Assert valid indices:
        edges[edges < 0] = 0
        edges[edges > len(labels) - 1] = len(labels) - 1
        # Assert inward buffers in segment:
        edges[1] = min(edges[1], end)
        edges[2] = max(edges[2], start)
        # Assert outward buffers not in nearby segments:
        if i > 0:
            edges[0] = max(edges[0], segments[i - 1][-1] + 1)
        if i < len(segments) - 1:
            edges[3] = min(edges[3], segments[i + 1][0] - 1)
        # Apply buffer zones to labels:
        buff_labels[edges[0]:edges[1]] = buff_value
        buff_labels[edges[2] + 1:edges[3] + 1] = buff_value
    return buff_labels


def debuffer(buff_labels, buff_value=0.0, learn_ind=None, mod_nolearn=True):
    """ Omits buffers from training data before it is shown to classifier.
        Modifications depend on the combination of chosen buffer extents and
        buff_value applied by buffer() as well as learn_ind and mod_nolearn:

        1) Buffer extents determine if data is modified at all:
           If no buffer zones were applied, use full data (do not call this
           function in any case!).
        2) buff_value determines which data is treated as buffers:
           If non-zero, omit explicitly declared buffer zones, keep noise.
           If zero, omit buffer zones plus all noise (use pure song data).
        3) learn_ind determines interpretation of appended data:
           If unspecified, assume pure learn files (target songs + noise).
           If given, assume combination of learn and nolearn files (no-target
           songs + noise). Target songs and no-target songs require different
           class labels for classifier training.
           Buffers are omitted according to 2) in both cases.
        4) mod_nolearn determines if learn files (target songs + noise) and
           nolearn files (no-target songs + noise) are modified differently:
           If unspecified, omit any buffers everywhere in the data.
           If given, omit buffers in learn files, preserve nolearn files.
           Always requires learn_ind for the creation of correct class labels.
           Buffers are omitted according to 2) in both cases.
        TARGET SONGS ARE ALWAYS LABELED AS 1, NO-TARGET SONGS AND NOISE AS 0.

    Parameters
    ----------
    buff_labels : 1D array of floats (m,)
        Buffered song labels for each datapoint (1 = song, 0 = no song/noise,
        buff_value = buffer zones). Can also handle other song labels, as long
        as they are not the same as buff_value. If learn_ind is given, can
        also handle species-specific song labels in the style of encoder().
    buff_value : float, optional
        Tag value that encodes buffer zones in buff_labels. The default is 0.0,
        so that any noise segments are also interpreted as buffer zones.
    learn_ind : 1D array of bools (m,), optional
        If specified, indicates portions of the data that contain target songs.
        Obligate to create correct class labels if buff_labels contains song
        segments of multiple species (learn + nolearn files). Else, assumes
        that all song segments are target songs (pure learn files). The default
        is None.
    mod_nolearn : bool, optional
        If True, omits buffers in learn files as indicated by learn_ind, while
        sparing nolearn files from any modifications. If False, omits buffers
        in entire data. Ignored if learn_ind is None. The default is True.

    Returns
    -------
    train_labels : 1D array of floats (n,)
        Portions of buff_labels that are used for classifier training. All
        buffers are omitted according to the specified conditions. Target songs
        are always labeled as 1, no-target songs and noise as 0.
    ind : 1D array of bools (m,)
        Indeces of remaining datapoints in buff_labels after buffer omission.
        Can be used to select corresponding portions of feature data.
    """
    train_labels = buff_labels.copy()    
    if learn_ind is None:
        # Assume pure learn files, omit buffers everywhere:
        ind = (train_labels != buff_value)
        # Adjust training class labels:
        train_labels[ind & (train_labels != 0)] = 1
    else:
        # Assume both learn and nolearn files:
        nolearn_ind = np.invert(learn_ind)
        if mod_nolearn:
            # Omit buffers everywhere:
            ind = (train_labels != buff_value)
        else:
            # Omit buffers in learn files only:
            ind = ((train_labels != buff_value) & learn_ind) | nolearn_ind
        # Adjust training class labels:
        train_labels[ind & learn_ind & (train_labels != 0)] = 1
        train_labels[ind & nolearn_ind] = 0
    return train_labels[ind], ind


# INTERACTIVITY:


def label_gui(signal, rate, edges=None, labels=None, fullscreen=True,
              spec_kwargs={}, **plot_kwargs):
    """ Simple matplotlib GUI for labeling segments of a time series signal.
        Consists of a line plot of the signal with optional spectrogram. Each
        label is represented by a pair of edge times and indicated as a patch
        that ranges from one edge to the other. Accepts pre-computed labels as
        either edge times or a binary label array. Mouse clicks can be used to
        place new edges and remove existing labels. Keys can be used to add new
        labels, to exit or restart the GUI, or move along the working history.
        Working history logs all instances of added and removed labels, which
        can then be undone or redone. While down the history, further adding or
        removing of labels will clear the "future" history branch.

        MOUSE INTERACTIONS:
        - primary (left): place 1st edge
        - secondary (right): place 2nd edge
        - tertiary (wheel): remove label
        KEY BINDINGS:
        - space: add label from 1st to 2nd edge
        - escape: exit GUI and return label edges
        - r: restart GUI with initial input arguments
        - arrow down: go back in working history
        - arrow up: go forward in working history
        - o/p: auto-toggle mouse interactivity
        
    Parameters
    ----------
    signal : 1D array (m,) of floats or ints
        Time series signal used as reference for labeling.
    rate : float or int
        Sampling rate of the signal in Hz.
    edges : 2D array (n, 2) or list (n,) of lists (2,) of floats, optional
        If specified, edge times (start, end) of each initial label in seconds.
        The default is None.
    labels : 1D array (m,) of bools or floats or ints, optional
        If specified, binary array that indicates initial labels as segments of
        non-zero values. Must be sampled with the same rate as signal. Ignored
        if edges is specified. The default is None.
    fullscreen : bool, optional
        If True, opens the GUI in full-screen mode. The default is True.
    spec_kwargs : dict, optional
        If not empty, adds a spectrogram subplot to the GUI and passes the
        specified keyword arguments to the spectrogram() wrapper function to
        compute the frequency spectrum of the signal. The default is {}.
    **plot_kwargs : dict, optional
        Keyword arguments passed to plot_spectrogram() for displaying the
        spectrogram, balancing rendering speed and visual quality. May contain
        any of 'quick_render', 'f_resample', and 't_resample', as well as any
        keyword argument accepted by plt.pcolormesh() if quick_render=False,
        or plt.imshow() if quick_render=True. Ignored if spec_kwargs is empty. 

    Returns
    -------
    edges : 2D array (n, 2) of floats or empty 1D array
        Edge times (start, end) of each labeled segment in seconds. Returns
        an empty array if the GUI was exited without adding any labels.
    """    
    # Input interpretation:
    if edges is None and labels is not None:
        # Find consecutive non-zero elements:
        segments = bundle_inds(labels)
        # Convert and bundle start and end time of each segment:
        edges = [[seg[0] / rate, seg[-1] / rate] for seg in segments]
        input_edges = None
    elif isinstance(edges, np.ndarray):
        # Ensure simple mutable:
        edges = edges.tolist()
        input_edges = edges.copy()
    elif edges is None:
        # No pre-existing labels:
        edges, input_edges = [], []
    else:
        # Retain original input:
        input_edges = edges.copy()
    plt.ion()

    # Initialize interface:
    n = 2 if spec_kwargs else 1
    fig, axes = plt.subplots(n, 1, figsize=(16, 9), sharex=True, squeeze=False)
    axes = axes[:, 0].tolist()                                                 
    if fullscreen:
        # Optionally opening in full-screen mode:
        fig.canvas.manager.full_screen_toggle()

    # Prepare signal subplot variables:
    time = np.arange(signal.shape[0]) / rate
    signal_limits = np.array([signal.min(), signal.max()])
    signal_limits += np.array([-1, 1]) * np.diff(signal_limits) * 0.1
    patch_alpha = [0.5]                                                       

    # Plot signal trace:
    axes[0].plot(time, signal, 'k', lw=0.5)
    axes[0].set_xlim(time[0], time[-1])
    axes[0].set_ylim(signal_limits)
    if signal_limits[0] < 0 < signal_limits[1]:
        # Add optional zero line:
        axes[0].axhline(0, color='k', lw=0.5, ls='dotted')

    if spec_kwargs:
        # Compute and plot spectrogram:
        f, _, _ = plot_spectrogram(signal, rate, axes[1], spec_kwargs,
                                   **plot_kwargs)
        axes[1].set_ylim(f[0], f[-1])
        patch_alpha.append(0.25)

    # Prepare persistent variables:
    mouse = [True]                                                             # Enables GUI-specific mouse events
    patches = [[] for _ in range(n)]                                           # Subplot-specific label patches
    lines = [[None, None] for _ in range(n)]                                   # Subplot-specific temporary lines
    current_times = [None, None]                                               # Currently registered 1st and 2nd edge time
    history = []                                                               # Chronology of add/remove events [1/0, edges, [patches]]                  
    state_ind = [-1]                                                           # Current position along history
    retry = [False]                                                            # Flag for recursive GUI recall

    # Indicate any initial labels:
    for segment_edges in edges:
        for i, ax in enumerate(axes):
            patches[i].append(ax.axvspan(*segment_edges, fc='r', ec='k',
                                         alpha=patch_alpha[i], lw=1,
                                         picker=10, rasterized=True))
    # Interactivity:
    def on_key(event):
        # Toggle mouse interactivity:
        if event.key in ['o', 'p']:
            mouse[0] = not mouse[0]
            return None

        # Exit and return results:
        elif event.key == 'escape':
            plt.close(fig)
            print('Finished labeling.')
            return None

        # Abort and start over:
        elif event.key == 'r':
            plt.close(fig)
            retry[0] = True
            print('Aborted labeling. Retrying...')
            return None

        # Turn registered edge times into a new label:
        elif event.key == ' ' and all(current_times):
            # Ensure correct temporal order:
            if current_times[0] > current_times[1]:
                current_times.reverse()
            # Indicate in interface:
            for i, ax in enumerate(axes):
                # Wipe temporary lines and reset:
                lines[i][0].remove(), lines[i][1].remove()
                lines[i][0], lines[i][1] = None, None
                # Replace with new patch from edge to edge:
                patches[i].append(ax.axvspan(*current_times, fc='r', ec='k',
                                             alpha=patch_alpha[i], lw=1,
                                             picker=10, rasterized=True))
            print(f'Added {current_times[0]:.4f} - {current_times[1]:.4f}')
            # Log edge times and reset:
            edges.append(current_times.copy())
            current_times[0], current_times[1] = None, None
            # Update history:
            if state_ind[0] < -1:
                # Clear "future" branch (later than current state):
                [history.pop() for _ in range(-1 - state_ind[0])]
                state_ind[0] = -1
            # Remember add-event as new most recent history state:
            history.append([1, edges[-1], [patches[i][-1] for i in range(n)]])
            # Update interface:
            fig.canvas.draw()
            return None

        # Go back in history:
        elif event.key == 'down':
            # Ignore if at beginning of history:
            if state_ind[0] == -len(history) - 1:
                return None
            state = history[state_ind[0]]
            if state[0]:
                # Undo add event:
                edges.remove(state[1])
                for i, state_patch in enumerate(state[2]):
                    patches[i].remove(state_patch)
                    state_patch.remove()
            elif not state[0]:
                # Undo remove event:
                edges.append(state[1])
                for i, ax in enumerate(axes):
                    patches[i].append(state[2][i])
                    ax.add_patch(state[2][i])
            # To earlier state:
            state_ind[0] -= 1
            # Update interface:
            fig.canvas.draw()
            return None

        # Go forward in history:
        elif event.key == 'up':
            if state_ind[0] == -1:
                return None
            # To later state:
            state_ind[0] += 1
            state = history[state_ind[0]]
            if state[0]:
                # Redo add event:
                edges.append(state[1])
                for i, ax in enumerate(axes):
                    patches[i].append(state[2][i])
                    ax.add_patch(state[2][i])
            elif not state[0]:
                # Redo remove event:
                edges.remove(state[1])
                for i, state_patch in enumerate(state[2]):
                    patches[i].remove(state_patch)
                    state_patch.remove()
            # Update interface:
            fig.canvas.draw()
            return None

    # Edge registration:
    def on_click(event):
        # Ignore suspended inputs, out-of-focus, or wrong button:
        if not mouse[0] or event.inaxes is None or event.button not in [1, 3]:
            return None
        # Decide between 1st and 2nd edge:
        ind = {1: 0, 3: 1}[event.button]
        # Register selected time point:
        current_times[ind] = event.xdata
        # Indicate in interface:
        for i, ax in enumerate(axes):
            if lines[i][ind]:
                # Wipe previous line:
                lines[i][ind].remove()
            # Replace with new temporary line at edge time:
            lines[i][ind] = ax.axvline(current_times[ind], color='r', lw=1)
        # Update interface:
        fig.canvas.draw()
        return None

    # Label removal:
    def on_pick(event):
        # Ignore suspended inputs or wrong button:
        if not mouse[0] or event.mouseevent.button != 2:
            return None
        # Identify label from selected patch:
        ax_ind = axes.index(event.artist.axes)
        label_ind = patches[ax_ind].index(event.artist)
        # Update history:
        if state_ind[0] < -1:
            # Clear "future" branch (later than current state):
            [history.pop() for _ in range(-1 - state_ind[0])]
            state_ind[0] = -1
        # Remember remove-event as new most recent history state:
        history_patches = [patches[i][label_ind] for i in range(n)]
        history.append([0, edges[label_ind], history_patches])
        # Wipe from interface:
        for i in range(len(axes)):
            patches[i][label_ind].remove()
            patches[i].pop(label_ind)
        print(f'Wiped {edges[label_ind][0]:.4f} - {edges[label_ind][1]:.4f}')
        # Unlog edge times:
        edges.pop(label_ind)
        # Update interface:
        fig.canvas.draw()
        return None

    # Establish interactivity:
    plt.connect('key_press_event', on_key)
    plt.connect('button_press_event', on_click)
    plt.connect('pick_event', on_pick)
    plt.ioff()
    plt.show()
    if retry[0]:
        # Recursive recall with unmodified initial input arguments:
        return label_gui(signal, rate, input_edges, labels, fullscreen,
                         spec_kwargs, **plot_kwargs)
    # Return options:
    edges = np.array(edges)
    if edges.ndim == 2:
        # Return chronologically sorted:
        return edges[np.argsort(edges[:, 0]), :]
    # Return empty:
    return edges
