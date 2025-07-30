import numpy as np
from .misctools import combination_array


def gauss_width(sigma, rel_height=0.01):
    """ Approximates the width of a Gaussian with given standard deviation.
        Function width is estimated at a height relative to the function peak,
        rendering it independent of horizontal shifts and peak amplitude. The
        function integrals inside and outside the estimated width still depend
        on peak amplitude, while the ratio of both integrals remains constant.

        Accepts array inputs for any of sigma and rel_height, as long as they
        are broadcastable. Arrays go into the equation unchecked and
        unmodified. Input shape compatibility and output shape interpretation
        are the user's responsibility.

    Parameters
    ----------
    sigma : float or int or array of floats or ints
        Gaussian standard deviation in arbitrary units.
    rel_height : float or array of floats, optional
        Proportion of peak height at which to calculate width. May not be
        zero to avoid non-finite ln(0). The default is 0.01.

    Returns
    -------
    width : float or array of floats
        Gaussian function width at a height relative to the function peak.
    """
    return 2 * np.sqrt(2 * np.log(1 / rel_height)) * sigma


def gabor_phase(n_lobes, sign=1, radians=True):
    """ Returns the required phase shift for a specific type of Gabor kernel.
        Chooses one of four possible phase values (0, pi, pi/2, -pi/2) of the
        sinusoidal carrier function, corresponding to one of four general
        classes of Gabor kernel types:

        # Mirror-symmetric Gabors (cosine carrier, odd number of lobes):
            # 0: Positive central lobe ("syllable detectors").
            # pi: Negative central lobe ("pause detectors").

        # Point-symmetric Gabors (sine carrier, even number of lobes):
            # pi/2: Positive lobe left of the center ("onset detectors").
            # -pi/2: Negative lobe left of the center ("offset detectors").

        Accepts array inputs for any of n_lobes and sign, as long as they are
        broadcastable. Arrays go into the equation unchecked and unmodified.
        Input shape compatibility and output shape interpretation are the
        user's responsibility.

    Parameters
    ----------
    n_lobes : int or float or array of ints or floats
        Number of lobes of the desired type of Gabor kernel. Odd numbers result
        in mirror-symmetric Gabors, even numbers in point-symmetric Gabors.
        Must be a positive integer number, although the type may be float.
    sign : int or float or array of ints or floats, optional
        Sign, or vertical orientation, of the desired type of Gabor kernel.
        Options are +1 (mirror-symmetric with positive central lobe, or point-
        symmetric with a positive lobe left of the center) and -1 (mirror-
        symmetric with negative central lobe, or point-symmetric with a
        negative lobe left of the center). The default is 1.
    radians : bool, optional
        If True, returns phase shift in radians for direct use. Else, returns
        phase as a factor of pi (0, 1, 0.5, -0.5). The default is True.

    Returns
    -------
    phase : float or array of floats
        One of four possible values (0, pi, pi/2, -pi/2) of phase shift that is
        required to create Gabor kernels with given n_lobes and sign. Returned
        either in radians or as a factor of pi, depending on the radians flag.
    """
    phase = 0.5 * (1 - n_lobes % 2 + sign)
    if radians:
        phase *= np.pi
    return phase


def gabor_freqs(n_lobes, peak_thresh=0.01, offset=0.5, sigma=1.,
                gauss_width=None):
    """ Finds a suitable carrier frequency for a specific type of Gabor kernel.
        The frequency of the sinusoidal carrier function determines the number
        of oscillations under the Gaussian envelope, which in turn determines
        the number of lobes in the Gabor kernel. Frequency estimation can be
        based on a linear approximation of the near-linear relation between
        frequency and lobe number, or constrained to the width of the Gaussian. 

        Accepts array inputs for any of n_lobes, peak_thresh, offset, sigma,
        and gauss_width, as long as they are broadcastable. Arrays go into the
        equation unchecked and unmodified. Input shape compatibility and output
        shape interpretation are the user's responsibility.

    Parameters
    ----------
    n_lobes : int or float or array of ints or floats
        Number of lobes of the desired type of Gabor kernel. Odd numbers result
        in mirror-symmetric Gabors, even numbers in point-symmetric Gabors.
        Must be a positive integer number, although the type may be float.
    peak_thresh : float or array of floats, optional
        Required for linear frequency approximation method. For a Gabor kernel
        with n_lobes, the next-outer lobe left and right of the main lobes in
        the kernel's central range is less than (rarely equal to) peak_thresh.
        The exact peak value depends heavily on the given peak_thresh and the
        offset of the linear approximation, and decreases for larger n_lobes.
        The default is 0.01.
    offset : float or array of floats, optional
        Required for linear frequency approximation method. Added to n_lobes to
        lift the linear approximation of the frequency-lobe relation. If offset
        is 0.526 and peak_thresh is 0.01, the next-outer lobes are actually
        equal to peak_thresh (for n_lobes of 2, else less). The default is 0.5.
    sigma : int or float or array of ints or floats, optional
        Required for linear frequency approximation method. Used as standard
        deviation is s to adjust for different widths of the Gaussian envelope.
        Can also be done posthoc (frequency / sigma). The default is 1.0.
    gauss_width : float or array of floats, optional
        If specified, switches from linear frequency approximation method to
        width-constrained method (ignoring peak_thresh, offset, and sigma), and
        calculates carrier frequency so that the time interval specified by
        gauss_width holds exactly n_lobes.

    Returns
    -------
    frequency : float or array of floats
        Suitable frequency of the sinusoidal carrier function in Hz to create
        Gabor kernels with the desired number of lobes. Either approximated
        from the near-linear frequency-lobe relation, or calculated precisely
        for a Gaussian envelope of given width. Assigns a frequency of 0 Hz to
        kernels with a single lobe (Gaussians).
    """
    # Input interpretation:
    if np.any(n_lobes == 1):
        # Ensure zero frequency for Gaussian kernels:
        replace = -offset if gauss_width is None else 0
        if isinstance(n_lobes, np.ndarray):
            # Overwrite among multiple:
            n_lobes = n_lobes.copy()
            n_lobes[n_lobes == 1] = replace
        else:
            # Overwrite single:
            n_lobes = replace

    # Compute carrier frequency:
    if gauss_width is not None:
        # From Gaussian width estimate:
        return 0.5 * n_lobes / gauss_width
    # Linear approximation of frequency-lobe relation:
    slope_factor = 4 * np.sqrt(-2 * np.log(peak_thresh))
    return (n_lobes + offset) / slope_factor / sigma


def gabor_derivative(time, sigma, freq, phase=0., carrier='sine'):
    """ Evaluates the first-order derivative of a Gabor kernel at given times.
        The Gabor function is characterized by the standard deviation of its
        Gaussian envelope and the frequency and phase shift of its sinusoidal
        carrier. Can handle both sine and cosine carrier functions.

    Parameters
    ----------
    time : int or float or 1D array (m,) of ints or floats
        Time points at which to evaluate the Gabor derivative in s.
    sigma : int or float
        Standard deviation of the Gaussian envelope in s.
    freq : int or float
        Frequency of the sinusoidal carrier in Hz.
    phase : int or float, optional
        Phase shift of the sinusoidal carrier in radians. The default is 0.0.
    carrier : str, optional
        Specifies whether the carrier function is a sine or cosine, which
        results in different phase shifts of the derivative. Options are 'sine'
        and 'cosine'. The default is 'sine'.

    Returns
    -------
    derivative : float or 1D array (m,) of floats
        Derivative of the given Gabor kernel at the specified time points.
        The derivative of a Gabor function is another Gabor function. It has
        the same standard deviation and frequency but a different amplitude and
        a phase-shift of -0.5*pi/f (or +0.5*pi/f and inverted sign) relative to
        the original Gabor function. The carrier of the derivative always has
        a cosine and a sine component, regardless of the original carrier.
    """
    if carrier == 'sine':
        factors = [2 * np.pi * freq, time / sigma ** 2]
    elif carrier == 'cosine':
        factors = [-time / sigma ** 2, 2 * np.pi * freq]

    derivative = np.exp(-0.5 * (time / sigma) ** 2) * \
        (factors[0] * np.cos(2 * np.pi * freq * time + phase) -
         factors[1] * np.sin(2 * np.pi * freq * time + phase))
    return derivative


def encode_kernels(kernel_dict=None, types=None, sigmas=None, channels=None,
                   all_columns=False, shared_params=(), keep_order=True):
    """ Translates different ways of specifying a set of Gabor kernels.
        Converts more convenient input formats into working formats that can be
        understood by gabor_set(). Returns a 2D column array of kernel type
        identifiers, standard deviations, and optionally channel coverage. Each
        row sufficiently characterizes one Gabor kernel in the set. Valid
        identifiers are integer numbers encoding the number of lobes (absolute
        id value) and the vertical orientation (sign of id) of a given type.

    Parameters
    ----------
    kernel_dict : dict {int: (floats,) or ((floats,), (floats,))}
        If specified, defines the included kernel types (keys) and individual
        Gaussian standard deviations in s and optionally the number of covered
        channels per type (values), overriding types, sigmas, and channels.
        Accepts scalar values of sigmas. If channels are specified, both sigmas
        and channels must be sequences of same length. The default is None.
    types : int or float or 1D array-like of ints or floats (m,)
        If specified, defines the kernel types to combine with sigmas and
        channels. Accepts scalar values. Must be provided together with sigmas.
        Ignored if kernel_dict is given. The default is None.
    sigmas : int or float or 1D array-like of ints or floats (n,)
        If specified, defines Gaussian standard deviations in s to combine with
        types and channels. Accepts scalar values. Must be provided together
        with types. Ignored if kernel_dict is given. The default is None.
    channels : int or float or 1D array-like of ints or floats (p,), optional
        If specified, defines channel coverage as integer numbers to combine
        with types and sigmas. Accepts scalar values. Ignored if kernel_dict is
        given. The default is None.
    all_columns : bool, optional
        If True, the returned specs array will always contain the third column
        (channel coverage). If False, the third column will be included only if
        any channels are provided. The default is False.
    shared_params : 1D array-like of int (2,) or (3,), optional
        If specified, allows to pair-wise combine two or three same-sized sets
        of types (0), sigmas (1), and channels (2). All parameter sets not in
        shared_params, as well as the zipped sets, will be combined cross-wise.
        The default is {}.
    keep_order : bool, optional
        If True, the returned specs array will retain a column order of types,
        sigmas, and channels if shared_params is specified. Else, the columns
        are partitioned with the unshared parameter first, if any, followed by
        the parameters in shared_params. The default is True.

    Returns
    -------
    specs : 2D array of floats (p, 2) or (p, 3)
        Defines each Gabor kernel in the set by combination of a kernel type
        identifier (1st column), standard deviation sigma (2nd column), and
        optionally channel coverage (3rd column). Contains as many rows as
        there are kernels in the set, including duplicates. The order of rows
        determines the order in which gabor_set() returns generated kernels.

    Raises
    ------
    ValueError
        Breaks if neither kernel_dict nor both types and sigmas are provided.
    """
    if kernel_dict is not None:
        # Individual sigma/channel combinations per kernel type:
        types = np.array(list(kernel_dict.keys()), dtype=int)
        # Accumulate type-specific parameter sets:
        type_params = [np.array(kernel_dict[t], ndmin=2) for t in types]
        # Accumulate number of kernels per type:
        n_kernels = np.array([params.shape[1] for params in type_params])
        # Force-enable 3rd column (channels) if any are provided:
        all_columns |= any(params.shape[0] == 2 for params in type_params)

        # Initialize and fill 2D column array:
        specs = np.zeros((n_kernels.sum(), 2 + all_columns))
        # Insert kernel type identifiers:
        specs[:, 0] = np.repeat(types, n_kernels)
        # Prepare slice indices:
        stop_inds = np.cumsum(n_kernels)
        start_inds = stop_inds - n_kernels
        for params, start, stop in zip(type_params, start_inds, stop_inds):
            # Insert type-specific sigma set:
            specs[start:stop, 1] = params[0, :]
            if params.shape[0] == 2:
                # Insert optional channel set:
                specs[start:stop, 2] = params[1, :]
            elif all_columns:
                # Singular place-holder:
                specs[start:stop, 2] = 1

    elif types is not None and sigmas is not None:
        # Cross- and pair-wise parameter combinations:
        params = (np.array(types, dtype=int, ndmin=1),
                  np.array(sigmas, dtype=float, ndmin=1))
        if channels is not None:
            params += (np.array(channels, dtype=int, ndmin=1),)
        elif all_columns:
            params += (np.array([1]),)

        # Parallelize sets:
        if shared_params:
            # Prepare set indices:
            inds = range(len(params))
            # Partition cross-wise and pair-wise parameter combinations:
            cross_params = [i for i in inds if i not in shared_params]
            # Prepare required nested input structure:
            params = (*(params[i] for i in cross_params),
                      [params[i] for i in shared_params])
            # Keep track of original order of parameter sets:
            inds = np.argsort((*cross_params, *shared_params))

        # Combine and flat to 2D column array:
        specs = combination_array(params)
        if keep_order and shared_params:
            # Type-sigma-channel:
            specs = specs[:, inds]
    else:
        raise ValueError('Specify either kernel_dict or types and sigmas.')
    return specs


def link_kernels(specs):
    """ Groups Gabor kernels that are identical or inverted to each other.
        All kernels of a group have the same sigma and the same absolute type
        identifier (i.e. identical waveform up to a sign) and produce only 
        identical or inverted outputs when convolved with a signal. The first
        kernel of each group (base kernel) is mapped to all group members and
        their respective signs. Used by convolve_kernels() to identify base
        kernels and convolve only those instead of the whole group. 

    Parameters
    ----------
    specs : 2D array of floats (m, 2)
        Defines each Gabor kernel in the set as a pair of type identifier (left
        column) and sigma in s (right column). Contains as many rows as there
        are kernels in the set, including duplicates.

    Returns
    -------
    linked_kernels : dict of ints (keys) and tuples (2,) of 1D arrays (values)
        Dictionary with as many entries as groups of Gabor kernels in the set.
        Maps the index of each base kernel to the indices and signs (relative
        to base) of all kernels that are identical (1) or inverted (-1) to it.
    """    
    # Assimilate inverted types:
    specs = specs.copy()
    specs[:, 0] = np.abs(specs[:, 0])

    linked_kernels = {}
    for base in np.unique(specs, axis=0):
        # Get all identical or inverted to the base kernel:
        group = np.nonzero(np.all(specs == base, axis=1))[0]
        # Get sign (+-1) of each kernel relative to the base:
        signs = specs[group, 0] / specs[group[0], 0]
        # Map base to all related kernels:
        linked_kernels[group[0]] = (group, signs)
    return linked_kernels

