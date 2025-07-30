import numpy as np
from scipy.interpolate import interpn
from scipy.signal import butter, sosfiltfilt, sosfilt, sosfilt_zi
from .misctools import check_list, ensure_array, mirror_linspace
from .arraytools import broadcastable, array_slice, remap_array, align_arrays
from .filtertools import gauss_width, gabor_phase, gabor_freqs, encode_kernels


# DATA TRANSFORMATION:


def decibel(data, ref=None, axis=None, lower_bound=1e-10):
    """ Logarithmic transformation of data to decibel (10 * log10(data / ref)).

    Parameters
    ----------
    data : ND-array of floats (arbitrary shape)
        Data to transform to dB.
    ref : float, optional
        Reference intensity for dB calculation that will correspond to 0 dB.
        If unspecified, uses the maximum over data. If axis is specified, uses
        the maximum along axis. If the maximum is 0, falls back to a reference
        value of 1. The default is None.
    lower_bound : float, optional
        Positive minimum capping value to avoid log(0). The default is 1e-10.

    Returns
    -------
    log_data : ND array of floats (data.shape)
        Logarithmically scaled data in dB.
    """
    if ref is None:
        maximum = np.nanmax(data, axis=axis)
        ref = np.where(maximum != 0, maximum, 1)
    data = np.array(data)
    data[data < lower_bound] = lower_bound
    return 10 * np.log10(data / ref)


def downsampling(data, rate, new_rate, axis=0):
    """ Resamples time series data of given sampling rate to a lower new rate.
        Uses slicing along the specified axis where applicable. Otherwise, uses
        np.interp() for 1D data and scipy.interpolate.interpn() for ND data.
        Interpolation method is linear in both cases.

    Parameters
    ----------
    data : ND-array of floats (arbitrary shape)
        Data to be downsampled. Non-arrays are converted, if possible. Only the
        temporal array dimension specified by axis is resampled.
    rate : float or int
        Current sampling rate of data in Hz. Must be same for all time series.
    new_rate : float or int
        New sampling rate of data in Hz. Must be smaller than rate.
    axis : int, optional
        Time axis of data to be resampled. The default is 0.

    Returns
    -------
    downsampled : ND array of floats (data.shape except shape[axis])
        Downsampled data with the given new rate. Returns data unchanged if
        new_rate is not smaller than rate. Input dimensionality is preserved,
        but the size of axis is reduced.
    """
    # Assert array (any shape):
    data = ensure_array(var=data, dtype=float)
    # Rate conflict early exit:
    if new_rate >= rate:
        return data
    # Sampling rate ratio:
    n = rate / new_rate
    if abs(n - np.round(n)) < 0.01:
        # Clean ratio early exit (nth-entry selection along axis):
        return array_slice(data, axis, step=int(np.round(n)))

    # Interpolation for non-integer ratios:
    t = np.arange(data.shape[0]) / rate
    new_t = np.arange(0, t[-1], 1 / new_rate)
    if data.ndim == 1:
        # 1D interpolation early exit:
        return np.interp(new_t, t, data)

    # Prepare for ND-interpolation along axis:
    data_coords = [np.arange(i) for i in data.shape]
    sample_coords = data_coords.copy()
    data_coords[axis], sample_coords[axis] = t, new_t
    # Expand from dimension-wise to point-wise coordinates:
    sample_coords = np.meshgrid(*sample_coords, indexing='ij')
    sample_coords = np.vstack([grid.ravel() for grid in sample_coords]).T
    # Interpolate from current onto new point grid:
    downsampled = interpn(data_coords, data, sample_coords)
    # Restore initial dimensionality:
    new_shape = list(data.shape)
    new_shape[axis] = len(new_t)
    return downsampled.reshape(new_shape)


def repeated_downsampling(data, rate, new_rates, avoid_interpol):
    #TODO: Adapt to ND downsampling(?):
    """ Repeated downsampling of data to a series of new sampling rates.
        Used to recreate exact result of several downsampling steps in one go.
        Only useful if single downsampling yields unequal array lengths.

    Parameters
    ----------
    data : 1D array (m,) or 2D array (m, n) or list of floats or ints
        Data to be downsampled. Lists are converted to arrays (shape must be 1D
        or 2D). Any other input shapes result in a ValueError. If 2D,
        downsampling is done along the first axis, so that each column is
        treated as a separate time series.
    rate : float
        Original sampling rate of data in Hz.
    new_rates : list of floats (n,)
        New sampling rate of data at each downsampling step in Hz.
    avoid_interpol : bool or list of bools (n,)
        Before each downsampling step, adapts length of data to integer
        multiple of the ratio of the current and the next new sampling rate.
        Used to avoid interpolation during the respective downsampling step.
        First entry corresponds to step from rate to new_rates[0], second entry
        to step from new_rates[0] to new_rates[1], and so on.

    Returns
    -------
    downsampled : 1D array of floats (p,)
        Downsampled data with a sampling rate of new_rates[-1].
    """
    downsampled = np.array(data)
    rates = [rate] + new_rates
    for i in range(len(rates) - 1):
        if avoid_interpol[i]:
            # Crop to multiple of sampling rate ratio:
            ratio = int(np.round(rates[i] / rates[i + 1]))
            downsampled[:(len(downsampled) // ratio) * ratio]
        # Downsampling step:
        downsampled = downsampling(downsampled, rates[i], rates[i + 1])
    return downsampled


# SPECTRAL FILTERS:


def sosfilter(data, rate, cutoff, mode='lp', order=1, axis=0, refilter=True,
              padtype='even', padlen=None, padval=0., sanitize_padlen=True,
              zi=None, init=None):
    """ Applies a digital Butterworth filter in second-order sections format.
        Includes both the sosfilt() and sosfiltfilt() function of scipy.signal.
        Data can be filtered once (forward) or twice (forward-backward, which
        doubles the order of the filter and centers the phase of the output).
        Provides low-pass, high-pass, and band-pass filter types.

        Forward filters by sosfilt() can be set to a given initial state to
        control the start value. Forward-backward filters by sosfiltfilt() can
        be used with all built-in and a custom padding method. The refilter
        argument can be used to switch between the two functions.

    Parameters
    ----------
    data : ND array (any shape) of floats or ints
        Data to be filtered. Filter is applied along the specified time axis.
    rate : float or int
        Sampling rate of the time axis of data in Hz.
    cutoff : float or int or tuple (2,) of floats or ints
        Cut-off frequency of the applied filter in Hz. If mode is 'lp' or 'hp',
        must be a single value. If mode is 'bp', must be a tuple of two values.
    mode : str, optional
        Type of the applied filter. Options are 'lp' (low-pass), 'hp'
        (high-pass), and 'bp' (band-pass). The default is 'lp'.
    order : int, optional
        Order of the applied filter. If refilter is True, actual filter order
        is twice the specified order. The default is 1.
    axis : int, optional
        Time axis of data along which to apply the filter. The default is 0.
    refilter : bool, optional
        If True, uses the forward-backward filtering method of sosfiltfilt(),
        which enables use of padtype, padlen, and padval to control padding. If
        False, uses the forward filtering method of sosfilt(), which enables
        use of zi and init to control the start value. The default is True.
    padtype : str, optional
        Method used to pad the data before forward-backward filtering. Can be:
        # 'constant': Pads with first and last value of data, respectively.
        -> For signals with assessable endpoints (e.g. bound to some baseline).
        # 'even': Mirrors the data around each endpoint.
        -> For (noisy) signals whose statistics do not change much over time.
        # 'odd': Mirrors data, then turns it 180° around the endpoint.
        -> For oscillatory signals or where stable phase and smoothness is key.
        # 'fixed': Pads with padval (managed externally, not by scipy).
        -> For signals that are meant to be seen in a certain temporal context.
        # None: No padding.
        Ignored if refilter is False. The default is 'even'.
    padlen : int, optional
        Number of points added to each side of data. Applies for any padtype.
        Calculated by sosfiltfilt() as a very small number of points if None.
        Ignored if refilter is False or padtype is None or padtype is 'fixed'
        with padval being an array. If sanitize_padlen is True and padtype is
        a built-in method, may be reduced to avoid errors. The default is None.
    padval : float or int or ND array (any shape) of floats or ints, optional
        If specified and padtype is 'fixed', used as custom padding. If scalar,
        creates a constant padding of size padlen with the given value. If
        array, must have the same shape as data except along axis, so that it
        can be concatenated to data. Ignored if refilter is False or padtype is
        not 'fixed'. The default is 0.0.
    sanitize_padlen : bool, optional
        If True and padtype is a built-in method with padlen specified, clips
        padlen to be less than the size of the time axis of data, avoiding an
        internal sosfiltfilt() error. Ignored if refilter is False or padlen is
        None or padtype is 'fixed'. The default is True.
    zi : ND array of floats, optional
        If specified, sets the initial state for each second-order section of
        the applied forward filter, which in turn determines the start value(s)
        for filtering. Either returned by sosfilt() after a previous filtering
        step, or constructed manually. Shape must be (n_sections, ..., 2, ...),
        where n_sections equals sos.shape[0] and ..., 2, ... is the shape of
        data with data.shape[axis] replaced by 2. Use sosfilt_zi() to generate
        the initial state for a single section. If None, creates a filter state
        array of matching shape and adapts the inital state to the start value
        specified by init. Ignored if refilter is True. The default is None.
    init : float or int or ND array (any shape) of floats or ints, optional
        If specified and zi is None, adapts the initial filter state to this
        start values(s). If scalar, determines the start value for all filtered
        slices in data. If array, must have the same shape as data (except that
        init.shape[axis] must be 1) to set the start value for each slice. If
        None, uses the values of the first slice of data along axis. Ignored if
        refilter is True or zi is specified. The default is None.

    Returns
    -------
    filtered : ND array (data.shape) of floats
        Filtered data along the given time axis. If refilter is True, output of
        sosfiltfilt(), else sosfilt(). If mode is 'lp' and cutoff is above the
        Nyquist frequency (rate / 2), returns unchanged data. If mode is 'bp'
        and cutoff[1] is above Nyquist, falls back to pure high-pass filtering.
    next_state : ND array (zi.shape) of floats
        New filter state array after the applied forward filtering step to pass
        on with the next function call. Only returned if refilter is False. 
    """
    # Nyquist low-pass early exit:
    if mode == 'lp' and cutoff > rate / 2:
        return data
    # Nyquist band-pass fallback to high-pass:
    elif mode == 'bp' and cutoff[1] > rate / 2:
        mode, cutoff = 'hp', cutoff[0]

    # Initialize filter as second-order sections:
    sos = butter(order, cutoff, mode, fs=rate, output='sos')

    # FORWARDS:
    if not refilter:
        if zi is None:
            # Initialize filter state array:
            data_shape = list(data.shape)
            data_shape[axis] = 2
            # Shape must be (n_sections, ..., 2, ...):
            zi = np.zeros([sos.shape[0]] + data_shape)

            # Construct initial state:
            shape = [1] * data.ndim
            shape[axis] = 2
            # Shape must be (..., 2, ...):
            init_state = sosfilt_zi(sos).reshape(shape)
            if init is None:
                # Take values of 1st slice along axis:
                init = array_slice(data, axis, 0, 1)

            # Adapt filter state per section:
            for i in range(sos.shape[0]):
                zi[i] = init_state * init

        # Apply filter once with given state and start value:
        filtered, next_state = sosfilt(sos, data, axis, zi)
        return filtered, next_state

    # FORWARDS-BACKWARDS:
    if padtype == 'fixed':
        # Manage custom padding options:
        if isinstance(padval, np.ndarray):
            # Individual values:
            if padval.ndim != data.ndim:
                msg = 'If padval is an array, must have the same dimensions'\
                      'as data and be of matching shape except along axis.'
                raise ValueError(msg)
            data = np.concatenate((padval, data, padval), axis=axis)
            padlen = padval.shape[axis]
        else:
            # Constant value: 
            if padlen is None:
                # Auto-generated as per scipy default:
                padlen = 3 * (2 * len(sos) + 1 - min((sos[:, 2] == 0).sum(),
                                                     (sos[:, 5] == 0).sum()))
            padding = [(0, 0)] * data.ndim
            padding[axis] = (padlen, padlen)
            data = np.pad(data, padding, constant_values=padval)

    # Clip to maximum allowed padding length to avoid scipy error:    
    elif sanitize_padlen and padlen is not None and padlen >= data.shape[axis]:
        padlen = data.shape[axis] - 1

    # Apply filter twice with given padding method:
    filtered = sosfiltfilt(sos, data, axis, padlen=padlen,
                           padtype=None if padtype == 'fixed' else padtype)
    # Return options:
    if padtype == 'fixed':
        # Remove custom padding manually:
        start, stop = padlen, data.shape[axis] - padlen
        return array_slice(filtered, axis, start, stop)
    return filtered


def envelope(data, rate, cutoff=500., env_rate=2000., **kwargs):
    """ Extracts the signal envelope by low-pass filtering the rectified data.
        Envelope can be resampled to a lower rate to reduce memory load.

    Parameters
    ----------
    data : ND array of floats or ints
        Data to be filtered. Non-arrays are converted, if possible. If 1D,
        assumes a single time series. If 2D, assumes that each column is a
        separate time series and performs filtering along the first axis.
    rate : float or int
        Sampling rate of data in Hz.
    cutoff : float or int, optional
        Cut-off frequency of the low-pass filter in Hz. The default is 500.0.
    env_rate : float or int, optional
        Sampling rate of the resampled envelope in Hz. Skips downsampling if
        env_rate >= rate. The default is 2000.0.
    **kwargs : dict, optional
        Additional keyword arguments passed to sosfilter(). Can be used to
        modify properties of the applied low-pass filter.

    Returns
    -------
    env : 1D array (p,) or 2D array (p, n) of floats
        Extracted signal envelope with given sampling rate for each time series
        in data. Returns 1D if input was 1D, else 2D.
    """
    filtered = sosfilter(np.abs(data), rate, cutoff, mode='lp', **kwargs)
    env = downsampling(filtered, rate, env_rate)
    return env


def multi_lowpass(data, rate, cutoffs, new_rate=None, rectify=False, **kwargs):
    """ Temporal averaging of data on multiple different time scales.
        Applies separate low-pass filters with the given cut-off frequencies.
        Data can be rectified before filtering to perform envelope extraction.
        Filtered data can then be downsampled to a new rate.

    Parameters
    ----------
    data : 1D array (m,) or 2D array (m, n) or list of floats or ints
        Data to be averaged by low-pass filtering. Non-arrays are converted, if
        possible. If 1D, assumes a single time series. If 2D, assumes that each
        column is a separate time series and averages along the first axis.
    rate : float or int
        Sampling rate of data in Hz. Must be the same for all columns.
    cutoffs : float or int or list of floats or ints (p,)
        Cut-off frequency of each applied low-pass filter in Hz. Accepts
        scalars (discouraged, use sosfilter() with downsampling() instead). For
        each specified cut-off frequency, adds a block with as many columns as
        data to the filtered array.
    new_rate : float or int
        If specified, downsamples filtered data to this rate in Hz. Ignored if
        new_rate >= rate. The default is None.
    rectify : bool, optional
        If True, applies np.abs() to data before low-pass filtering, turning
        temporal averaging into envelope extraction. The default is False.
    **kwargs : dict, optional
        Additional keyword arguments passed to sosfilter() to control the order
        of the low-pass filter, the filtering method, padding and start values.

    Returns
    -------
    filtered : 2D array of floats (q, n * p)
        Temporally averaged data, optionally downsampled. Columns correspond to
        filtered time series and are ordered block-wise by cut-off frequency of
        each applied low-pass filter. Block order is the same as in cutoffs.
        Within-block column order is the same as in data.
    """
    # Assert 2D array (columns):
    data = ensure_array(var=data, dims=(1, 2), shape=(-1, None))
    # Assert iterable:
    cutoffs = check_list(cutoffs)
    # Manage envelope mode:
    if rectify:
        data = np.abs(data)
    # Manage downsampling:
    if new_rate is None:
        new_rate = rate

    # Time series in data array:
    n_columns = data.shape[1]
    # Length of the (downsampled) time axis:
    n_resampled = int(np.round(new_rate / rate * data.shape[0]))
    # Initialize filtered array as horizontal tile of data array:
    filtered = np.zeros((n_resampled, n_columns * len(cutoffs)))
    for i, cutoff in enumerate(cutoffs):
        # Indices of next filter block along second axis:
        block = np.arange(i * n_columns, (i + 1) * n_columns, dtype=int)
        # Apply low-pass filter for given block to data array:
        filter_block = sosfilter(data, rate, cutoff, 'lp', **kwargs)
        filtered[:, block] = downsampling(filter_block, rate, new_rate)
    return filtered


# GABOR KERNELS:


def gabor_function(sigma, freq, phase, rate=1000, time=None):
    """ Creates a Gabor function by multiplication of a Gaussian and a sine.
        The Gaussian envelope constrains the sinusoidal carrier to a certain
        time interval, resulting in several amplitude-modulated oscillations
        that form the lobes of the Gabor. The number of lobes depends on the
        combination of carrier frequency and envelope width. Lobe alignment and
        sign of the Gabor depend on the phase shift of the carrier. Accepts any
        of sigma, freq, and phase as arrays, as long as they can be broadcast
        to a common output shape together with time.

    Parameters
    ----------
    sigma : int or float or array of ints or floats
        Standard deviation of the Gaussian envelope in s.
    freq : int or float or array of ints or floats
        Frequency of the sinusoidal carrier in Hz.
    phase : int or float or array of ints or floats
        Phase-shift of the sinusoidal carrier in radians.
    rate : int or float, optional
        Sampling rate of the Gabor in Hz. If time is None, used to generate
        the underlying time axis, else ignored. The default is 1000.
    time : array of ints or floats, optional
        Time axis underlying the Gabor in s. Replaces rate if specified, else
        calculated with rate over [-4 * sigma, 4 * sigma]. The generated time
        array matches the output dimensionality defined by sigma, freq, and
        phase, assuming the first dimension is time. The default is None.

    Returns
    -------
    gabor : array of floats
        Gabor function with given Gaussian envelope and sinusoidal carrier.
        Can return multiple Gabors if sigma, freq, or phase are arrays.
    time : array of ints or floats
        Time axis underlying the Gabor in s. If time is specified, returns the
        given array, else the generated array over [-4 * sigma, 4 * sigma].
        Returns a single time axis even if multiple Gabors are returned.
    """
    # Validate broadcasting across Gabor parameters:
    shape = broadcastable(vars=(sigma, freq, phase), crash=True)
    if time is None:
        # Scale time axis to hold the widest Gabor:
        sd = sigma if np.size(sigma) == 1 else sigma.max()
        # Generate time axis array and ensure it is broadcastable:
        time = remap_array(mirror_linspace(4 * sd, rate), {0:0}, shape=shape)

    # Compute components and resulting Gabor:
    gauss = np.exp(-0.5 * (time / sigma)**2)
    sine = np.sin(2 * np.pi * freq * time + phase)
    return gauss * sine, time


def gabor_kernels(sigmas, n_lobes, signs, rate=1000, time=None, as_array=True,
                  normalize=False, freq_kwargs={}, flat_flanks=False):
    #TODO: Add docstring!
    # Ensure array format (also effective downstream):
    check = lambda x: x if isinstance(x, np.ndarray) else np.array(x, ndmin=1)
    sigmas, n_lobes, signs = (check(var) for var in (sigmas, n_lobes, signs))

    # Get parameters of the carrier for each kernel:
    phases = gabor_phase(n_lobes, signs, radians=True)
    if 'rel_height' in freq_kwargs: 
        # Compute Gaussian widths at relative height:
        widths = gauss_width(sigmas, freq_kwargs.pop('rel_height'))
        # Update frequency settings:
        freq_kwargs['gauss_width'] = widths
    freqs = gabor_freqs(n_lobes, sigma=sigmas, **freq_kwargs)

    # Accumulate Gabor parameters of each kernel in the set:
    params, param_generator = [], zip(sigmas, freqs, phases, n_lobes, signs)
    for sigma, freq, phase, n, sign in param_generator:
        params.append({
            'sigma': sigma,
            'freq': freq,
            'phase': phase,
            'lobes': int(n),
            'sign': int(sign)})

    # Run parallel:
    if as_array:
        # Generate full kernel set as 2D array (time x kernels):
        kernels, time = gabor_function(sigmas[None, :], freqs[None, :],
                                       phases[None, :], rate, time)

        # Apply post-generation adjustments to kernel array:
        if flat_flanks and 'gauss_width' in freq_kwargs:
            # Optional wiping of lobes beyond Gaussian width:
            inds = (np.abs(time) > freq_kwargs['gauss_width']) & (n_lobes > 1)
            if inds.any():
                kernels[inds] = 0
        if normalize:
            # Optional kernel integral normalization:
            kernels /= np.sqrt(np.trapezoid(kernels**2, time, axis=0))
        return kernels, time, params

    # Run in series:
    kernels, times = [], []
    param_generator = zip(sigmas, freqs, phases, n_lobes)
    for i, (sigma, freq, phase, n) in enumerate(param_generator):
        # Generate single kernel with individual time axis:
        gabor, t = gabor_function(sigma, freq, phase, rate, time)
        # Apply post-generation adjustments and log variables:
        if flat_flanks and 'gauss_width' in freq_kwargs and n > 1:
            gabor[abs(t) > freq_kwargs['gauss_width'][i]] = 0
        if normalize:
            gabor /= np.sqrt(np.trapezoid(gabor**2, t))
        kernels.append(gabor), times.append(t)
    return kernels, times, params


def gabor_set(rate=1000, kernel_dict=None, types=None, sigmas=None,
              channels=None, specs=None, as_array=True, shared_params=(),
              **kwargs):
    #TODO: Add docstring!
    # Input interpretation:
    if specs is None:
        # Sanitize input parameter sets and create specifier array:
        specs = encode_kernels(kernel_dict, types, sigmas, channels,
                               shared_params=shared_params)

    # Generate set of Gabor kernels of given sigma, lobe number, and sign:
    kernels, times, params = gabor_kernels(specs[:, 1], np.abs(specs[:, 0]),
                                           np.sign(specs[:, 0]), rate=rate,
                                           as_array=as_array, **kwargs)                          
    if specs.shape[1] == 2:
        # No channel axis early exit:
        return kernels, specs, times, params

    # Expand each 1D kernel array to 2D (time x channels):
    param_generator = zip(kernels.T if as_array else kernels, specs[:, 2])
    kernels = [np.tile(k[:, None], (1, int(n))) for k, n in param_generator]
    if as_array:
        # Fuse into single 3D array (time x channels x kernels):
        kernels = align_arrays(kernels, new_axis=2, align='center')
    return kernels, specs, times, params


# def gabor_type(sigmas, n_lobes, sign, rate=1000, time=None, normalize=False,
#                freq_kwargs={}, flat_flanks=False):
#     """ Wrapper to gabor_function() to create Gabor kernels of a given type.
#         The desired kernel type is specified by its number of lobes and sign.
#         Generates one Gabor function for each Gaussian standard deviation in
#         sigmas and logs its relevant parameters. Frequency and phase of the
#         sinusoidal carrier are chosen to match the specified type. Features two
#         different methods of frequency estimation, time axis sharing, integral
#         normalization, and removal of unwanted outer kernel oscillations.

#     Parameters
#     ----------
#     sigmas : int or float or list or 1D array of ints or floats (m,)
#         Standard deviation of the Gaussian envelope in s. Always converted to
#         array format. Determines the number of created Gabor kernels. 
#     n_lobes : int or float
#         Number of lobes of the desired type of Gabor kernel. Odd numbers result
#         in mirror-symmetric Gabors, even numbers in point-symmetric Gabors.
#         Must be a positive integer number, although the type may be float.
#     sign : int or float
#         Sign, or vertical orientation, of the desired type of Gabor kernel.
#         Options are +1 (mirror-symmetric with positive central lobe, or point-
#         symmetric with a positive lobe left of the center) and -1 (mirror-
#         symmetric with negative central lobe, or point-symmetric with a
#         negative lobe left of the center). The default is 1.
#     rate : int or float, optional
#         Sampling rate of the Gabor kernels in Hz. If time is None, used to
#         generate the underlying time axes, else ignored. The default is 1000.
#     time : 1D array of ints or floats (n,), optional
#         Shared time axis underlying the Gabor kernels in s. Replaces rate if
#         specified, else calculated individually over [-5 * sigma, 5 * sigma]
#         for each kernel. The default is None.
#     normalize : bool, optional
#         If True, normalizes each created Gabor kernel by the integral over the
#         squared kernel, so that the dot product of the kernel function with
#         itself equals one. The default is False.
#     freq_kwargs : dict of ints or floats or 1D arrays (m,), optional
#         Modifies the frequency estimation method performed by gabor_freqs().
#         Specify any of 'peak_thresh' and 'offset' to change settings of the
#         linear approximation method (used by default). To switch to the width-
#         constrained method, either specify 'gauss_width' with precomputed width
#         estimates of the Gaussian envelopes, or specify 'rel_height' to let
#         gauss_width() compute them on the fly. All entries can be arrays of the
#         same length as sigmas. The default is {}. 
#     flat_flanks : bool, optional
#         If True and width-constrained frequency estimation method is used, sets
#         values of the Gabor kernels beyond the specified width of the Gaussian
#         envelope to zero, wiping outer oscillations. Ignored if freq_kwargs
#         contains neither 'gauss_width' nor 'rel_height'. The default is False.

#     Returns
#     -------
#     gabors : list (m,) of 1D arrays of floats
#         Gabor kernel of the desired type for each standard deviation in sigmas.
#         If time is specified, returns arrays of the same length.
#     times : list (m,) of 1D arrays of floats
#         Time axis underlying each Gabor kernel in s. If time is specified,
#         returns the same shared time axis for each kernel, else individual time
#         axes calculated over [-5 * sigma, 5 * sigma] with the given rate.
#     params : list (m,) of dicts of floats and ints
#         Dictionaries of parameters that characterize each created Gabor kernel
#         with keys 'sigma', 'freq', 'phase', 'lobes', and 'sign'. Includes the
#         standard deviation of the Gaussian envelope in s, the frequency of the
#         sinusoidal carrier in Hz and its phase shift in multiples of pi, as
#         well as the number of lobes and the vertical orientation of the Gabor.
#     """    
#     # Ensure array format:
#     if not isinstance(sigmas, np.ndarray):
#         sigmas = np.array(sigmas, ndmin=1)

#     # Get type-specific carrier parameters per kernel:
#     phase = gabor_phase(n_lobes, sign, radians=False)
#     if 'rel_height' in freq_kwargs:
#         # Live computation of Gaussian widths:
#         widths = gauss_width(sigmas, freq_kwargs['rel_height'])
#         freq_kwargs['gauss_width'] = widths
#         freq_kwargs.pop('rel_height')
#     freqs = gabor_freqs(n_lobes, sigma=sigmas, **freq_kwargs)

#     # Create Gabor kernels of given type:
#     gabors, times, params = [], [], []
#     for i, (sigma, freq) in enumerate(zip(sigmas, freqs)):
#         gabor, t = gabor_function(sigma, freq, phase * np.pi, rate, time)
#         # Posthocs adjustments:
#         if flat_flanks and 'gauss_width' in freq_kwargs and n_lobes > 1:
#             # Optional wiping of lobes beyond Gaussian width:
#             gabor[abs(t) > freq_kwargs['gauss_width'][i]] = 0
#         if normalize:
#             # Optional kernel integral normalization:
#             gabor /= np.sqrt(trapezoid(gabor ** 2, t))
#         # Log variables:
#         gabors.append(gabor)
#         times.append(t)
#         params.append({
#             'sigma': sigma,
#             'freq': freq,
#             'phase': phase,
#             'lobes': int(n_lobes),
#             'sign': int(sign)})
#     return gabors, times, params


# def kernel_set(rate, kernel_dict=None, types=None, sigmas=None,
#                specs=None, share_axis=False, **kwargs):
#     """ Wrapper to gabor_type() to generate a set of Gabor kernels.
#         Accepts a number of formats for specifying the kernels of the set, each
#         of which is defined by a pair of type identifier and sigma (standard
#         deviation of its Gaussian envelope). Valid type identifiers are integer
#         numbers that encode the number of lobes (absolute id value) and the
#         vertical orientation (sign of id) of a given type of Gabor kernel.
#         Returns the kernels of the created set, a two-column specifier array of
#         kernel types and sigmas, as well as the underlying time axis and
#         relevant parameters for each kernel.

#     Parameters
#     ----------
#     rate : int or float
#         Sampling rate of the Gabor kernels in Hz.
#     kernel_dict : dict, optional
#         If specified, defines the included kernel types (keys) and individual
#         Gaussian standard deviations per type in s (values). Accepts scalar
#         values of sigma. Duplicate sigmas for the same type result in duplicate
#         kernels. Overrides types and sigmas. Ignored if specs is given.
#         The default is None.
#     types : int or float or list or 1D array of ints or floats (m,)
#         If specified, defines the included kernel types. Accepts scalar values.
#         Duplicate types result in duplicate kernels. Must be specified together
#         with sigmas. Ignored if either kernel_dict or specs is given.
#         The default is None.
#     sigmas : int or float or list or 1D array of ints or floats (n,)
#         If specified, defines fixed Gaussian standard deviations for all kernel
#         types in s. Accepts scalar values. Duplicate sigmas result in duplicate
#         kernels. Must be specified together with types. Ignored if either
#         kernel_dict or specs is specified. The default is None.
#     specs : 2D array of floats (p, 2)
#         If specified, defines each Gabor kernel in the set as a pair of type
#         identifier (left column) and sigma (right column). The order of rows
#         determines the order of kernels in the created set. Duplicate rows
#         result in duplicate kernels. Overrides kernel_dict, sigmas, and types.
#         The default is None.
#     share_axis : bool, optional
#         If True, generates a single shared time axis for all Gabor kernels over
#         [-5 * max(sigmas), 5 * max(sigmas)]. Ignored if 'time' is specified as
#         keyword argument in kwargs. The default is False.
#     **kwargs : dict, optional
#         Additional keyword arguments passed to gabor_type(). May contain any of
#         'normalize', 'freq_kwargs', 'flat_flanks', and 'time'. If share_axis is
#         True, creates and adds a shared time axis as 'time'. The default is {}.

#     Returns
#     -------
#     kernels : list (q or m*n or p,) of 1D arrays of floats
#         Gabor kernel set of the desired types and Gaussian standard deviations.
#         If share_axis is True, returns arrays of the same length.
#     specs : 2D array of floats (q or m*n or p, 2)
#         Defines each Gabor kernel a pair of type identifier (left column) and
#         sigma (right column). Contains as many rows as there are kernels in the
#         set, including duplicates, in the order of kernels. If specs is
#         specified, returns the same array, else generated by encode_set() from
#         either kernel_dict or types and sigmas. If created, first sorts kernels
#         by type, then by sigma within each type.   
#     times : list (q or m*n or p,) of 1D arrays of floats
#         Time axis underlying each Gabor kernel in s. If 'time' is specified in
#         kwargs, returns the given array. If share_axis is True, returns the
#         newly created time axis over [-5 * max(sigmas), 5 * max(sigmas)]. Else,
#         returns individual time axes over [-5 * sigma, 5 * sigma] for each
#         kernel. Returns an array per kernel even if the time axis is shared.
#     params : list (q or m*n or p,) of dicts of floats and ints
#         Dictionaries of parameters that characterize each created Gabor kernel
#         with keys 'sigma', 'freq', 'phase', 'lobes', and 'sign'. Includes the
#         standard deviation of the Gaussian envelope in s, the frequency of the
#         sinusoidal carrier in Hz and its phase shift in multiples of pi, as
#         well as the number of lobes and the vertical orientation of the Gabor.
#     """    
#     # Input interpretation:
#     if specs is None:
#         # Create specifier array and standardize input types and sigmas:
#         specs, types, sigmas = encode_kernels(kernel_dict, types, sigmas)
#     else:
#         # Read out existing specifier array:
#         types = unsort_unique(specs[:, 0])
#         sigmas = [specs[specs[:, 0] == t, 1] for t in types]
#     if share_axis and 'time' not in kwargs:
#         # Generate shared time axis for all kernels:
#         kwargs['time'] = mirror_linspace(5 * np.max(sigmas), rate)
    
#     # Generate set of Gabor kernels:
#     kernels, times, params = [], [], []
#     for type_id, type_sigmas in zip(types, sigmas):
#         # Characterize current kernel type:
#         n_lobes, sign = abs(type_id), np.sign(type_id)
#         # Generate corresponding Gabors and log variables:
#         k, t, p = gabor_type(type_sigmas, n_lobes, sign, rate, **kwargs)
#         kernels += k
#         times += t
#         params += p
#     return kernels, specs, times, params
