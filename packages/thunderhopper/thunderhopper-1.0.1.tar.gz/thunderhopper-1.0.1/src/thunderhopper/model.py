import sys
import numpy as np
import audioio as aio
from .filters import gabor_set, decibel, sosfilter, envelope, downsampling
from .filtertools import link_kernels
from .misctools import ensure_iterable, merge_dicts
from .arraytools import array_slice, remap_array, align_arrays
from .labeltools import label_songs, label_gui
from .modeltools import save_data, event_lags
from .stats import batch_convolution, nonlinearity


def configuration(env_rate=2000, feat_rate=1000, kernel_dict=None, specs=None,
                  types=[1, -1, 2, -2, 3, -3, 4, -4, 5, -5,
                         6, -6, 7, -7, 8, -8, 9, -9, 10, -10],
                  sigmas=[0.001, 0.002, 0.004, 0.008, 0.016, 0.032], **kwargs):
    """ Top-level parameter configuration of the songdetector model.
        Can be used in many functions to overwrite separate keyword arguments.
        Accepts sampling rates and Gabor kernel specifications (keywords, type
        identifiers and sigmas) on call. Other parameters are set to default.
        Valid type identifiers are integer numbers that encode the number of
        lobes (absolute id value) and the vertical orientation (sign of id) of
        a given type of Gabor kernel.

    Parameters
    ----------
    env_rate : float or int, optional
        Sampling rate of the signal envelope in Hz. Defines the first
        downsampling step along the processing pipeline. Also determines the
        sampling of the intensity-invariant envelope, the set of Gabor kernels,
        as well as the raw kernel responses (from convolution of the invariant
        envelope) and the thresholded kernel responses (before averaging into
        features). The default is 2000. 
    feat_rate : float or int, optional
        Sampling rate of the features in Hz. Defines the second downsampling
        step along the processing pipeline. Also determines the sampling of the
        different song labels (general/species-specific, unbuffered/buffered),
        the file encoding for appended data, as well as the classifier
        predictions. The default is 1000.
    kernel_dict : dict, optional
        If specified, defines the included kernel types (keys) and individual
        Gaussian standard deviations per type in s (values). Accepts scalar
        values of sigma. Duplicate sigmas for the same type result in duplicate
        kernels. Overrides types and sigmas. Ignored if specs is given.
        The default is None.
    types : int or float or list or 1D array of ints or floats (m,)
        If specified, defines the included kernel types. Accepts scalar values.
        Duplicate types result in duplicate kernels. Must be specified together
        with sigmas. Ignored if either kernel_dict or specs is given.
        The default is [1, -1, 2, -2, 3, -3, 4, -4].
    sigmas : int or float or list or 1D array of ints or floats (n,)
        If specified, defines fixed Gaussian standard deviations for all kernel
        types in s. Accepts scalar values. Duplicate sigmas result in duplicate
        kernels. Must be specified together with types. Ignored if either
        kernel_dict or specs is specified. The default is [0.001, 0.01].
    specs : 2D array of floats (p, 2)
        If specified, defines each Gabor kernel in the set as a pair of type
        identifier (left column) and sigma (right column). The order of rows
        determines the order of kernels in the created set. Duplicate rows
        result in duplicate kernels. Overrides kernel_dict, sigmas, and types.
        The default is None.
    **kwargs : dict, optional
        Additional keyword arguments passed to gabor_set(). May contain any of
        'normalize', 'freq_kwargs', and 'flat_flanks', as well as one of 'time'
        and 'share_axis'. The default is {}.

    Returns
    -------
    config : dict
        Top-level parameter configuration of the songdetector model. Can be
        passed to many functions to overwrite separate keyword arguments.
    """    
    # Generate set of Gabor kernels and associated variables:
    kernels, specs, times, params = gabor_set(env_rate, kernel_dict, types,
                                              sigmas, specs=specs, **kwargs)

    # OBLIGATE (have default):
    config = {
        # GENERAL:
        'rate': None,                                                          # Sampling rate of the input signal in Hz (float or int)  
        'channel': None,                                                       # Channel subset to process in multi-channel recordings (int or 1D array of ints)
        # SAMPLING RATES:
        'env_rate': env_rate,                                                  # Sampling rate of envelope-related variables in Hz (float or int)
        'feat_rate': feat_rate,                                                # Sampling rate of feature-related variables in Hz (float or int)
        'rate_ratio': int(np.round(env_rate / feat_rate)),                     # Clean downsampling ratio of second relative to first downstampling step (int)
        # CUT-OFF FREQUENCIES:
        'bp_fcut': [5000., 30000.],                                            # Lower & upper cut-off frequency of initial band-pass filter in Hz (tuple or list of 2 floats or ints)
        'env_fcut' : 500.,                                                     # Cut-off frequency of low-pass filter for envelope extraction in Hz (float or int)
        'inv_fcut' : 10.,                                                      # Cut-off frequency of high-pass filter to transform logarithmic to invariant envelope in Hz (float or int)                            
        # GABOR KERNELS:
        'kernels': kernels,                                                    # Set of Gabor kernels (list of 1D arrays of floats)
        'k_specs': specs,                                                      # Type identifier and sigma in s for each kernel (2-column array of floats)
        'k_times': times,                                                      # Time axis of each kernel in s (list of 1D arrays of floats)
        'k_props': params,                                                     # Attributes of each kernel (list of dicts with 'sigma' in s, 'freq' in Hz, 'phase' in multiples of pi, 'lobes', and 'vert')
        # FEATURE EXPANSION:
        'padlen': int(env_rate),                                               # Length of padding added before different filter steps in points (int)
        'feat_fcut' : 1.,                                                      # Cut-off frequency of low-pass filter(s) for averaging thresholded kernel responses into features in Hz (float or int or list of floats or ints)
        'feat_thresh': 0.1,                                                    # Absolute threshold applied to kernel responses between convolution and averaging (float or int)
        'ring_cap': False,                                                     # Cap feature values to range [0, 1] to remove ringing artifacts (bool)
        # LABELS (GENERAL):
        'label_channels': None,                                                # Channel subset to label in multi-channel recordings (int or 1D array of ints or None)
        'label_ref': None,                                                     # Reference channel for global threshold labeling in multi-channel recordings (int)
        'global_ref': False,                                                   # Use maximum feature norm as reference for global threshold labeling if ref_channel is None (bool)
        'label_thresh': 0.25,                                                  # Relative threshold to maximum of target signal for automatic song labeling (float)
        'label_seg': None,                                                     # Minimum tolerated song segment length in points (int)
        'label_seg_rel': None,                                                 # Alternative minimum tolerated song segment length relative to largest segment (float)
        'label_gap': None,                                                     # Minimum tolerated gap length in points (int)
        'label_gap_rel': None,                                                 # Alternative minimum tolerated gap length relative to largest gap (float)
        # LABELS (GUI):
        'quick_render': True,                                                  # Replace plt.pcolormesh() with plt.imshow() for spectrogram display (bool)
        'fullscreen': True,                                                    # Open label GUI in fullscreen mode (bool)
        'f_resample': None,                                                    # Factor to downsample spectrogram frequency axis (int)
        't_resample': None,                                                    # Factor to downsample spectrogram time axis (int)
        'spec_kwargs': {                                                       # Expandable set of keyword arguments for stats.spectrogram() and plottools.plot_spectrogram() (misc)
            'nperseg': 2**8,                                                   # Window size for spectrogram computation (int)
            'hop': 2**7,                                                       # Window shift for spectrogram computation (int)
            'log_power': True,                                                 # Scale spectrogram powers to decibel (bool)
            'db_high': -40                                                     # Drop all upper frequency bands that never exceed this power (float or int)
            },
        # MULTI-CHANNEL LAG:
        'distance': None,                                                      # Multi-channel recording distances in m (1D array of floats)
        'lag_channels': None,                                                  # Channel subset for which to compute transmission delays in multi-channel recordings (int or 1D array of ints or None)
        'lag_ref': 0,                                                          # Reference channel against which to compute transmission delay in multi-channel recordings (int)
        'lag_frame': None,                                                     # Range of lag times to consider when computing transmission delays (float or list/tuple of 2 floats)
        'sequential_lag': True,                                                # Force subsequent channels to have a larger transmission delay than the last (bool) 
        'expand_frame': False,                                                 # Maintain frame width when computing transmission delays sequentially (bool)
        # BUFFER ZONES:
        'add_buffer': True,                                                    # Call buffer() to add buffer zones at edges of labeled song segments (bool)
        'n_buff': [0., 0.1, 0.1, 0.],                                          # Absolute/relative extent of each of the four possible buffer zones per segment in order [start_out, start_in, end_in, end_out] (list of 4 ints or floats)
        'buff_value': 0.,                                                      # Value to encode buffer zones in buffered label array (float or int)
        # CLASSIFIER TRAINING:
        'add_noise': True,                                                     # Append additional pure noise recordings to training data (bool)
        'debuff_nolearn' : True,                                               # Omit buffers also in nolearn training data, not just learn data (bool)
        'seed': 42,                                                            # Random seed for classifier initialization (int)
        'n_iter': 5000,                                                        # Number of iterations of classifier training (int)
        'classifier': None,                                                    # Insert fitted model once training is completed (class object)
        # CLASSIFIER PREDICTIONS:
        'predict_seg': None,                                                   # Minimum tolerated segment length in classifier predictions in points (int)
        'predict_seg_rel': None,                                               # Alternative minimum tolerated prediction segment length relative to largest segment (float)
        'predict_gap': None,                                                   # Minimum tolerated gap length in classifier predictions in points (int) 
        'predict_gap_rel': None,                                               # Alternative minimum tolerated prediction gap length relative to largest gap (float)
    }
    # AUXILIARY (if specified):
    if kwargs:
        for argument, setting in kwargs.items():
            if argument == 'freq_kwargs':
                # Add flattened dictionary:
                config.update(setting)
            else:
                # Append single entry:
                config[argument] = setting
    return config


def extract_env(signal, rate, bp_fcut=(5000., 30000.), env_fcut=500.,
                env_rate=2000., rate_ratio=None, padlen=None, config=None,
                both=False):
    #TODO: Update docstring.
    """ Signal pre-processing by band-pass filtering and envelope extraction.
        The filtered signal is low-pass filtered to obtain the signal envelope,
        which can be downsampled afterwards.

        In the songdetector model, this step relates to the band-pass
        properties of the tympanal membrane and the mechano-transduction of the
        attached population of receptor neurons. 

    Parameters
    ----------
    signal : 1D array of floats or ints (m,)
        Recorded song data, or any other (acoustic) signal. Only accepts a
        single recording channel.
    rate : float or int
        Sampling rate of the signal in Hz.
    bp_fcut : list of floats or ints (2,) or None, optional
        Lower and upper cut-off frequency of initial band-pass filter in Hz.
        Falls back to a high-pass filter if bp_fcut[1] is larger than the
        Nyquist frequency (rate / 2). If None, extracts the envelope of the 
        unfiltered input signal. The default is [5000.0, 30000.0].
    env_fcut : float or int, optional
        Cut-off frequency of the low-pass filter for envelope extraction in Hz.
        The default is 500.0.
    env_rate : float or int, optional
        Sampling rate of the returned signal envelope in Hz. Signal is down-
        sampled accordingly from rate to env_rate after low-pass filtering.
        Ignored if env_rate >= rate. The default is 2000.0.
    rate_ratio : int, optional
        Ratio of second downsampling step (env_rate to feat_rate, during
        feature expansion) relative to first downsampling step (rate to
        env_rate). If specified, crops the signal envelope to integer multiple
        of ratio to avoid interpolation during the second downsampling step.
        The default is None.
    padlen : int, optional
        Keyword argument of sosfilter() to control the length of the padding
        added to each side of the signal to mitigate edge artifacts of the low-
        and band-pass filter. The default is None.
    config : dict, optional
        Top-level parameter configuration in the format of configuration() that
        replaces all keyword arguments if specified. The default is None.

    Returns
    -------
    env : 1D array of floats (n,)
        Envelope over the band-pass filtered signal, optionally downsampled
        and cropped to avoid interpolation during further downsampling steps.
    """    
    # Input interpretation:
    if config is not None:
        bp_fcut = config['bp_fcut']
        env_fcut = config['env_fcut']
        env_rate = config['env_rate']
        rate_ratio = config['rate_ratio']
        padlen = config['padlen']

    if bp_fcut is not None:
        # Initital band-pass filter (mean-padded):
        band_passed = sosfilter(signal, rate, bp_fcut, 'bp',
                                padtype='fixed', padlen=padlen)
    else:
        # Continue unfiltered:
        band_passed = signal

    # Envelope extraction by low-pass filter:
    env = envelope(band_passed, rate, env_fcut, env_rate,
                   padtype='even', padlen=padlen)
    if rate_ratio is not None:
        # Optional envelope cropping:
        env = env[:(len(env) // rate_ratio) * rate_ratio]
    return (band_passed, env) if both else env


def intensity_invariant(signal, rate=2000., inv_fcut=10., padlen=None,
                        config=None, both=False):
    #TODO Update docstring.
    """ Pre-processing to render signal (envelope) intensity-invariant.
        The signal is transformed to a logarithmic scale in dB and then
        high-pass filtered to remove the signal offset. On a log-scale,
        different multiplicative intensity scalings are transformed into
        additive offsets by log(a * x) = log(a) + log(x). Offset log(a) of
        signal log(x) is contained as a constant at 0 Hz in the Fourier
        spectrum (and very low frequencies for transient offsets), which can
        be removed by a high-pass filter.

        In the songdetector model, this step relates to logarithmic intensity-
        tuning of the receptor neurons and spike-frequency adaptation of the
        receptor population and the following local interneurons in the
        metathoracic ganglion.

    Parameters
    ----------
    signal : 1D array of floats (m,)
        Signal envelope as returned by preprocessing(), or any other signal to
        be made intensity-invariant. Only accepts a single recording channel.
    rate : float or int, optional
        Sampling rate of the signal in Hz. The default is 2000.0.
    inv_fcut : float or int, optional
        Cut-off frequency of the high-pass filter for offset removal in Hz.
        The default is 10.0.
    padlen : int, optional
        Keyword argument of sosfilter() to control the length of the padding
        added to each side of the signal to mitigate edge artifacts of the
        high-pass filter. The default is None.
    config : dict, optional
        Top-level parameter configuration in the format of configuration() that
        replaces all keyword arguments if specified. The default is None.

    Returns
    -------
    invariant : 1D array of floats (m,)
        Logarithmically re-scaled, intensity-invariant signal (envelope).
        Equalizes different intensity levels across signal segments while
        preserving more prominent patterns. The effectiveness of this mechanism
        depends on the signal-to-noise ration. The invariant signal is not on a
        proper decibel scale anymore because of the high-pass filtering.
    """    
    # Input interpretation:
    if config is not None:
        rate = config['env_rate']
        inv_fcut = config['inv_fcut']
        padlen = config['padlen']
    log_signal = decibel(signal)
    # Logarithmic scaling and offset removal by high-pass filter:
    invariant = sosfilter(log_signal, rate, inv_fcut, 'hp',
                          padtype='constant', padlen=padlen)
    return (log_signal, invariant) if both else invariant


def convolve_kernels(signal, kernels, specs=None):
    """ Batch-convolves the input signal channel-wise with the kernel set.
        Convolution is pairwise, i.e. each column in signal is convolved with
        every column in kernels. Accepts any combination of 1D and 2D input
        arrays and returns output in a fitting shape (1D, 2D, or 3D). Refer to
        batch_convolution() for details on the convolution process. Allows for
        reduction of the number of performed convolutions if provided with a
        sufficient mapping to group identical/inverted kernels (specs).

    Parameters
    ----------
    signal : 1D array (m,) or 2D array (m, n) of floats
        Signal from one or multiple channels to convolve with the kernel set.
        The first dimension must be time (axis 0 of the output). If 2D, the
        second dimension (channels) is always the last (3rd) output axis.
    kernels : 1D array (p,) or 2D array (p, q) of floats
        Kernel set to convolve with the signal. Can also be a list of 1D arrays
        of varying lengths. If already an array, the first dimension must be
        time. If 2D, the second dimension (kernels) is axis 1 of the output.
    specs : 2D array (2, q) of floats, optional
        For a set of Gabor kernels, defines each kernel as a pair of type
        identifier (left column) and sigma in s (right column). Contains as
        many rows as kernels in the set, including duplicates. When provided,
        enables grouping of all kernels with identical or inverted waveform, so
        that convolution with a single base kernel per group is sufficient to
        obtain the results for all group members. Accepts any other 2D column
        array of defining kernel properties, as long as the first column
        indicates identical/inverted kernels by the sign of its values. 

    Returns
    -------
    convolved : 1D or 2D or 3D array of floats
        Pairwise convolution output of each channel in signal with any of the
        kernels, normalized by kernel length and cropped along the time axis to
        match that of the signal, even if kernels are longer in time. Output
        shape depends on the shape of the input arrays. If both input arrays
        are 1D, returns a 1D array (time,). If one input array is 1D and the
        other 2D, returns a 2D array (time, kernels) or (time, channels). If
        both input arrays are 2D, returns a 3D array (time, kernels, channels).
    """
    # Input interpretation:
    if isinstance(kernels, (list, tuple)):
        # Merge 1D arrays into single 2D array:
        kernels = align_arrays(kernels, new_axis=1)

    # Attempt to reduce number of convolutions:
    if specs is not None and specs.shape[0] > 1:
        # Group identical with inverted kernels:
        base_kernels = link_kernels(specs) 
        base_inds = np.array(list(base_kernels.keys()), dtype=int)
        # Reduce to base kernel subset:
        kernels = kernels[:, base_inds]

    # Batch-convolve signal with the kernel (sub)set:
    signal_axes = {0:0, 1:2} if signal.ndim == 2 else {0:0}
    kernel_axes = {0:0, 1:1} if kernels.ndim == 2 else {0:0} 
    convolved = batch_convolution(signal, kernels, signal_axes, kernel_axes)

    # No skipped convolutions early exit:
    if specs is None or specs.shape[0] == 1:
        return convolved

    # Initial 2D output array (time x kernels):
    shape = [signal.shape[0], specs.shape[0]]
    if signal.ndim == 2:
        # Add channels as 3rd axis:
        shape.append(signal.shape[1])
    # Create 2D or 3D array:
    output = np.zeros(shape)

    # Reassign base kernel convolutions:
    for i, base_ind in enumerate(base_inds):
        # Get group members and signs relative to base:
        group_inds, signs = base_kernels[base_ind]
        # Extract base convolution slice from 2nd axis:
        out = array_slice(convolved, axis=1, start=i, stop=i, include=True)
        # Append a slice per group member (2nd axis):
        tiles = np.ones(convolved.ndim, dtype=int)
        # Initialize 2D or 3D indices for insertion:
        target_inds = [slice(None)] * convolved.ndim
        tiles[1], target_inds[1] = len(group_inds), group_inds
        # Repeatedly insert base convolution slice in output array:
        signs = remap_array(signs, axes_map={0:1}, shape=tiles)
        output[tuple(target_inds)] = np.tile(out, tiles) * signs
    return output


def finalize_features(signal, rate=2000, feat_fcut=1., order=1, padlen=None,
                      feat_rate=None, ring_cap=False, config=None):
    """ Temporally averages binary representations into a set of features. 
        Takes the thresholded convolution outputs per kernel and channel and
        averages each over time by one or several separate low-pass filters.
        The resulting feature set can be resampled to a lower rate. Accepts 2D
        or 3D inputs and returns an array of matching dimensionality. For each
        low-pass filter, a block of features is added to the 2nd output axis.

    Parameters
    ----------
    signal : 1D array (t,) or 2D array (t, k) or 3D array (t, k, c) of floats
        Binary representations of the expanded signal. First axis must be time.
        If 2D, expects a single channel (time, kernels). If 3D, expects several
        channels (time, kernels, channels). Expands 1D to a 2D column vector.
        Dimensions are maintained in the output but may have different size.
    rate : int or float, optional
        Sampling rate of the expanded signal in Hz. The default is 2000.
    feat_fcut : float or int or iterable (m,) of floats or ints, optional
        Cut-off frequency of one or several low-pass filters in Hz. Iterables
        must be of len(order) or contain a single element. The default is 1.
    order : int or iterable (m,) of ints, optional
        Order of one or several low-pass filters. Iterables must be of
        len(feat_fcut) or contain a single element. The default is 1.
    feat_rate : int or float, optional
        If specified, downsamples the feature array to this rate in Hz. Ignored
        if not below the input rate. The default is None.
    padlen : int, optional
        Keyword argument of sosfilter() to control the length of the padding
        added to each side of the signal to mitigate edge artifacts of the
        low-pass filter. The default is None.
    ring_cap : bool, optional
        If True, clips the feature array to [0, 1]. The default is False.
    config : dict, optional
        Top-level parameter configuration in the format of configuration() that
        replaces all keyword arguments if specified. The default is None.

    Returns
    -------
    features : 2D array (t, k * m) or 3D array (t, k * m, c) of floats
        Finalized feature set, optionally downsampled and clipped to [0, 1].
        Dimensionality matches that of the input array (except for 1D inputs).
        For each low-pass filter specified by feat_fcut and order, a block of
        kernel-specific features is appended to axis 1 of the output array. The
        in-block order of the features corresponds to the order of the kernels.
        If feat_rate is specified, axis 0 is downsampled to match the new rate. 
    """    
    # Input intepretation:
    if config is not None:
        rate = config['env_rate']
        feat_fcut = config['feat_fcut']
        feat_rate = config['feat_rate']
        padlen = config['padlen']
        ring_cap = config['ring_cap']
    # Assert 1D arrays of equal length:
    feat_fcut, order = ensure_iterable((feat_fcut, order), equalize=True)
    # Assert at least 2D:
    if signal.ndim == 1:
        signal = signal[:, None]
    # Manage downsampling:
    if feat_rate is None:
        feat_rate = rate

    # Initialize (downsampled) array:
    target_shape = list(signal.shape)
    target_shape[0] = int(np.round(feat_rate / rate * target_shape[0]))
    target_shape[1] *= feat_fcut.size
    features = np.zeros(target_shape)
    n_total = features.shape[1]

    # Feature transformation:
    for i, (fcut, ord) in enumerate(zip(feat_fcut, order)):
        # Apply low-pass filter of given cut-off and order:
        feats = sosfilter(signal, rate, fcut, 'lp', order=ord,
                          padlen=padlen, padtype='fixed', padval=0)
        # Indices of filter-specific feature block:
        target_inds = [slice(None)] * features.ndim
        target_inds[1] = np.arange(i * n_total, (i + 1) * n_total)
        # Insert optionally downsampled block along 2nd axis of array:
        features[tuple(target_inds)] = downsampling(feats, rate, feat_rate)
    return np.clip(features, 0, 1) if ring_cap else features


def expand_signal(signal, kernels=None, specs=None, threshold=None,
                  rate=2000, feat_fcut=None, order=1, padlen=None,
                  feat_rate=None, ring_cap=False, config=None, both=False):
    #TODO: Update docstring.
    """ Expands the signal into a high-dimensional time-series representation.
        Convolves each channel of the input signal with the kernel set, applies
        a threshold non-linearity, and temporally averages the resulting binary
        representations into a set of features. Can return the feature array
        together with the convolution outputs before thresholding.

    Parameters
    ----------
    signal : _type_
        _description_
    kernels : _type_, optional
        _description_, by default None
    specs : _type_, optional
        _description_, by default None
    threshold : _type_, optional
        _description_, by default None
    rate : int or float, optional
        Sampling rate of the signal in Hz. The default is 2000.
    feat_fcut : float or int or iterable (m,) of floats or ints, optional
        Cut-off frequency of one or several averaging low-pass filters in Hz.
        Iterables must be of len(order) or contain a single element.
        The default is 1.
    order : int or iterable (m,) of ints, optional
        Order of one or several averaging low-pass filters. Iterables must be
        of len(feat_fcut) or contain a single element. The default is 1.
    feat_rate : int or float, optional
        If specified, downsamples the feature array to this rate in Hz. Ignored
        if not below the input rate. The default is None.
    padlen : int, optional
        Keyword argument of sosfilter() to control the length of the padding
        added to each side of the signal to mitigate edge artifacts of the
        low-pass filter. The default is None.
    ring_cap : bool, optional
        If True, clips the feature array to [0, 1]. The default is False.
    config : dict, optional
        Top-level parameter configuration in the format of configuration() that
        replaces all keyword arguments except dual_return if specified.
        The default is None.
    both : bool, optional
        _description_, by default False

    Returns
    -------
    _type_
        _description_
    """    
    # Input intepretation:
    if config is not None:
        kernels = config['kernels']
        specs = config['k_specs']
        threshold = config['feat_thresh']
        rate = config['env_rate']
        feat_fcut = config['feat_fcut']
        padlen = config['padlen']
        feat_rate = config['feat_rate']
        ring_cap = config['ring_cap']

    # Convolve channels of signal with the kernel set:
    convolved = convolve_kernels(signal, kernels, specs)
    if both:
        # Retain unmodified version:
        convolved_copy = convolved.copy()

    # Post-expansion processing:
    if threshold is not None:
        # Apply multiple kernel-specific or one general threshold:
        convolved = nonlinearity(convolved, threshold, axes_map={0:1})
    if feat_fcut is not None:
        # Temporal averaging by one or several low-pass filters:
        features = finalize_features(convolved, rate, feat_fcut, order,
                                     padlen, feat_rate, ring_cap)
        return (convolved_copy, features) if both else features
    return convolved


def process_signal(config, returns=None, path=None, signal=None, rate=None,
                   save=None, overwrite=False, label_edit=False):
    """ Full song detector processing pipeline from input audio to feature set.
        Includes band-pass filtering, envelope extraction by rectification and
        low-pass filtering, intensity-invariance by logarithmic compression and
        high-pass filtering, convolutional expansion with the kernel set into a
        high-dimensional representation, thresholding into binary signals, and
        multi-scale temporal averaging by low-pass filtering to finalize the
        feature set. Offers automatic threshold-based song labeling and posthoc
        GUI editing. Supports partial processing to return only a selection of
        requested representations, avoiding redundant computations. Can store
        representation data and parameter configuration in a joint npz archive.
        Can handle both single-channel and multi-channel recordings.

    Parameters
    ----------
    config : dict
        Top-level parameter configuration in the format of configuration() that
        provides required arguments for extract_env(), intensity_invariant(),
        expand_signal(), nonlinearity(), and label_songs(), and defines further
        processing settings. Also includes the kernel set to be used.
    returns : str or list or tuple of str (m,), optional
        Selection of representations to include in the output. Can be any of
        # 'raw':   Unmodified input audio signal.
        # 'filt':  Band-pass filtered input signal.
        # 'env':   Signal envelope over the filtered signal.
        # 'log':   Logarithmically scaled (dB) signal envelope.
        # 'inv':   Intensity-invariant signal envelope.
        # 'conv':  Convolution outputs of invariant signal and kernel set.
        # 'bi':    Binary signals (thresholded convolution outputs).
        # 'feat':  Feature set (temporally averaged binary signals).
        # 'norm':  Frobenius norm across feature vectors.
        # 'songs': Segment edge times of threshold-labeled song events.
        Other strings have either no or unintended effect. Some representations
        are computed implicitly and without request as predecessor for others.
        Returns all representations if none are requested. The default is None.
    path : str, optional
        Absolute or relative path to a wav file for loading the input signal.
        Loaded signal underlies the same dimensionality constraints as signal.
        Overrides signal and rate if specified. The default is None.
    signal : 1D array (t,) or 2D array (t, c) of floats, optional
        Input signal to process. First axis must be time. If 1D, expects a
        single channel. If 2D, expects multiple channels. Requires rate to be
        specified. Ignored if path is provided instead. The default is None.
    rate : float or int, optional
        Initial sampling rate of the input signal in Hz. Requires signal to be
        specified. Ignored if path is provided instead. The default is None.
    save : str, optional
        Absolute or relative path to a npz archive for storing the requested
        representations, corresponding sampling rates, and the used parameter
        configuration. Disables saving if not specified. The default is None.
    overwrite : bool, optional
        If True, writes data to a new archive under the given path, overwriting
        any existing file. If False, updates an existing archive with the new
        data, preserving any other archive entries. Ignored if save is not
        specified. The default is False.
    label_edit : bool, optional
        If True and 'songs' is requested, enables manual GUI-based editing of
        automatically labeled song events in each target channel. Allows to
        delete or add labels and recalculate edge times. The default is False.

    Returns
    -------
    data : dict of arrays
        Collection of requested representations created from the input signal.
        Keys are consistent with returns. Contains all representations if none
        are requested specifically. The dimensionality of each output array
        depends on the number of processed channels. 
    rates : dict of floats or ints
        Collection of sampling rates of the returned representations in Hz.
        Same keys as data. Sampling rates are included in the npz archive.

    Raises
    ------
    ValueError
        Breaks if neither a single path nor signal and rate are specified.
    """
    # Manage source:
    if path is not None:
        signal, rate = aio.load_audio(path)
    elif signal is None or rate is None:
        raise ValueError('Specify either path or both signal and rate.')
    config['rate'] = rate

    # Manage outputs:
    if returns is None:
        returns = ('raw', 'filt', 'env', 'log', 'inv',
                   'conv', 'bi', 'feat', 'norm', 'songs')

    # Select channel subset:
    if config['channel'] is not None:
        signal = signal[:, config['channel']]

    # Initialize storage for output representations:
    data = {'raw': signal} if 'raw' in returns else {}
    
    # Initialize assignment helpers:
    check = lambda key: key in returns
    var_assign = lambda k, v: data.update({k: v}) if check(k) else None
    fun_assign = lambda k, f, a: data.update({k: f(**a)}) if check(k) else None

    # Band-pass and envelope:
    if 'filt' in returns:
        data['filt'], env = extract_env(signal, rate, config=config, both=True)
    else:
        env = extract_env(signal, rate, config=config)
    var_assign('env', env)

    # Decibel and invariance:
    if 'log' in returns:
        data['log'], inv = intensity_invariant(env, config=config, both=True)
    else:
        inv = intensity_invariant(env, config=config)
    var_assign('inv', inv)

    # Expansion to high-dimensional representation:
    if any(np.isin(['conv', 'bi', 'feat', 'norm'], returns)):
        # Bundle threshold settings for call to nonlinearity():
        nl_args = {'thresh': config['feat_thresh'], 'axes_map': {0:1}}
        # Get writable parameters:
        config = config.copy()
        
        # Combination-dependent efficient computation:
        if 'feat' in returns or 'norm' in returns:
            # Feature expansion (threshold and low-pass):
            if 'conv' in returns or 'bi' in returns:
                # Retain raw convolution outputs:
                conv, feat = expand_signal(inv, config=config, both=True)
                # Log pre-features:
                var_assign('conv', conv)
                fun_assign('bi', nonlinearity, nl_args | {'data': conv})
            else:
                feat = expand_signal(inv, config=config)
            # Log feature variables:
            var_assign('feat', feat)
            fun_assign('norm', np.linalg.norm, {'x': feat, 'axis': 1})
        elif 'conv' in returns:
            # Convolutional expansion (optional threshold, no low-pass):
            config['feat_thresh'], config['feat_fcut'] = None, None
            data['conv'] = expand_signal(inv, config=config)
            fun_assign('bi', nonlinearity, nl_args | {'data': data['conv']})
        else:
            # Pure threshold, no low-pass:
            config['feat_fcut'] = None
            data['bi'] = expand_signal(inv, config=config)
    
    # Song event labeling:
    if 'songs' in returns:
        if 'norm' in returns:
            # By channel-wise feature norm: 
            args = {'rate': config['feat_rate'], 'norm': data['norm']}
        elif 'feat' in returns:
            # By norm computed from raw feature set:
            args = {'rate': config['feat_rate'], 'features': data['feat']}
        else:
            # Fallback to channel-wise signal envelope:
            args = {'rate': config['env_rate'], 'norm': env}

        # Get edge times of supra-threshold segments:
        song_edges = label_songs(config=config, wrap=True, **args)

        # Manage target channel references:
        channel_inds = config['label_channels']
        if channel_inds is None:
            # Default to all available channels:
            channel_inds = range(len(song_edges))
        elif not np.iterable(channel_inds):
            # Ensure iterable:
            channel_inds = [channel_inds]

        # Prepare GUI:
        if label_edit:
            gui_kwargs = {
                'quick_render': config['quick_render'],
                'fullscreen': config['fullscreen'],
                'f_resample': config['f_resample'],
                't_resample': config['t_resample'],
                'spec_kwargs': config['spec_kwargs']
            }

        # Channel-wise posthocs and storage:
        for ind, edges in zip(channel_inds, song_edges):
            if label_edit:
                # Optional GUI:
                edges = label_gui(signal[:, ind], rate, edges, **gui_kwargs)
            # Link to target channel:
            data[f'songs_{ind}'] = edges

            # Add transmission delay between multiple channels:
            if 'filt' in returns and config['distance'] is not None:
                delays = event_lags(data['filt'], rate, edges, config=config)
                # Link to reference channel and underlying labels:
                data[f"lag_{config['lag_ref']}_songs_{ind}"] = delays

    # Sampling rate for each representation in storage:
    rates = {'raw': rate, 'filt': rate, 'env': config['env_rate'],
             'log': config['env_rate'], 'inv': config['env_rate'],
             'conv': config['env_rate'], 'bi': config['env_rate'],
             'feat': config['feat_rate'], 'norm': config['feat_rate']}
    [rates.pop(key) for key in list(rates.keys()) if key not in returns]

    # Write to npz archive:
    if save is not None:
        save_data(save, merge_dicts(data, rates, suffix='_rate'),
                  config, overwrite=overwrite)
    return data, rates


def demo(path):
    """ Simple demo demonstrating basic usage of process_signal().
    """
    
    # Configure processing parameters:
    sigmas = [0.001, 0.002, 0.004, 0.008, 0.016, 0.032]
    types = [1, -1, 2, -2, 3, -3, 4, -4, 5, -5,
             6, -6, 7, -7, 8, -8, 9, -9, 10, -10]
    config = configuration(types=types, sigmas=sigmas)

    # Compute model traces:
    data, rates = process_signal(config, path=path)

    # Retrive traces:
    filt = data['filt'][:, 0]
    filt_rate = rates['filt']
    tfilt = np.arange(len(filt))/filt_rate
    env = data['env'][:, 0]
    env_rate = rates['env']
    tenv = np.arange(len(env))/env_rate

    # plot:
    import matplotlib.pyplot as plt
    plt.plot(tfilt, filt)
    plt.plot(tenv, env)
    plt.show()


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('Usage:')
        print('  model recording.wav:')
    else:
        demo(sys.argv[1])
    
