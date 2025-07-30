import json
import pathlib
import numpy as np
from sklearn.linear_model import Perceptron
from sklearn.svm import SVC
from scipy.sparse import csr_matrix
from .filters import gabor_set
from .stats import batch_correlation
from .misctools import string_series, merge_dicts, unmerge_dicts
from .filetools import check_extension, write_json, load_json, load_npz,\
                       to_archive, from_archive, update_npz


# PIPELINE I/O FUNCTIONS:


def config_to_archive(config):
    """ Converts the song detector parameter configuration to storable format.
        Removes entries that are inhomogeneous lists (kernels, k_times) or very
        large dictionaries (k_props) and can hence not be converted to arrays.
        Re-codes Nones as empty 1D arrays to avoid arrays of data type object.
        Flattens small dictionaries (spec_kwargs) and stores pre-fixed entries.
        Ensures compatibility with npy/npz file format, and prevents pickling.
        Use config_from_storage() to recover configuration in working format.

    Parameters
    ----------
    config : dict
        Top-level parameter configuration in the format of configuration().

    Returns
    -------
    config : dict
        Top-level parameter configuration in a format accepted by np.savez().
    """
    # Exclude non-storable:
    config = config.copy()
    [config.pop(key, None) for key in ('kernels', 'k_times', 'k_props')]
    # Merge sub-dictionaries into configuration:
    spec_kwargs = config.pop('spec_kwargs')
    config = merge_dicts(config, spec_kwargs, prefix='label_gui_')
    return to_archive(config)


def config_from_archive(config, full_recovery=True):
    """ Reverts loaded song detector parameter configuration to working format.
        Expects storage format returned by config_to_storage(). Unpacks ints,
        floats, bools, and strings from their 0D array containers. Restores
        empty 1D arrays to Nones. Bundles pre-fixed entries into the original
        dictionaries (spec_kwargs). Can run kernel_set() with initial settings
        to recover all kernel-related variables (kernels, k_times, k_props).

    Parameters
    ----------
    config : dict
        Top-level parameter configuration in storage format.
    full_recovery : bool, optional
        If True, scans configuration for auxiliary settings used to generate
        the kernel set and re-runs kernel_set() with the k_specs entry to
        recover the non-storable kernels, k_times, and k_props entries. Needed
        to fully restore the original configuration. The default is True. 

    Returns
    -------
    config : dict
        Top-level parameter configuration in working format.
    """
    # Convert arrays where needed:
    config = from_archive(config)

    # Re-bundle sub-dictionaries:
    spec_kwargs, config = unmerge_dicts(config, prefix='label_gui_')
    config['spec_kwargs'] = spec_kwargs

    if full_recovery:
        # Scan for auxiliary settings:
        keys = set(config.keys())
        optional_keys = set(['normalize', 'share_axis', 'time', 'flat_flanks'])
        auxiliaries = {k: config[k] for k in optional_keys & keys}

        # Scan for frequency estimation settings:
        freq_keys = set(['peak_thresh', 'offset', 'gauss_width', 'rel_height'])
        freq_kwargs = {k: config[k] for k in freq_keys & keys}
        if freq_kwargs:
            # Add bundled frequency settings:
            auxiliaries['freq_kwargs'] = freq_kwargs

        # Regenerate unstored kernel-associated variables:
        packed = gabor_set(config['env_rate'], specs=config['k_specs'],
                           **auxiliaries)
        config['kernels'], _, config['k_times'], config['k_props'] = packed
    return config


def save_data(path, data, config, prefix='metadata__', overwrite=False):
    """ Stores processing data and parameter configuration as npz archive.
        Converts configuration to storable format and inserts each parameter
        under its prefixed key into the data dictionary, which is then saved. 

    Parameters
    ----------
    path : str or pathlib.Path
        Absolute or relative path for writing the npz archive to file.
    data : dict of arrays
        Collection of signal representations to include in the archive in a
        format accepted by np.savez(), as returned by process_signal().
    config : dict
        Top-level parameter configuration in the format of configuration().
        Parameter entries have the prefix prepended to their key.
    prefix : str, optional
        Key tag to distinguish parameter entries from data in the archive.
        Empty strings disable tagging, preventing correct separation later on.
        The default is 'metadata__'.
    overwrite : bool, optional
        If True, writes data to a new archive under the given path, overwriting
        any existing file. If False, updates an existing archive with the new
        data, preserving any other archive entries. The default is False.
    """    
    data = merge_dicts(data, config_to_archive(config), prefix)
    if overwrite or not pathlib.Path(path).exists():
        np.savez(path, **data)
    else:
        update_npz(path, **data)
    return None


def load_data(path, files=None, keywords=None, prefix='metadata__',
              full_recovery=True):
    """ Retrieves processed data and parameter configuration from npz archive.
        Output can be limited to files whose names are explicitly given or
        contain any of the specified keywords. Separates prefixed parameter
        entries from data entries and converts the configuration to working
        format. Can regenerate missing kernel-related parameters.

    Parameters
    ----------
    path : str or pathlib.Path
        Absolute or relative path to the npz archive.
    files : str or list or tuple of str (m,), optional
        Selection of names of npy data files to load from the archive. Attempts
        to also return the corresponding sampling rate for each representation
        under the key "{name}_rate", if present. Ignores file names that cannot
        be found in archive.files. The default is None (all representations).
    keywords : str or list or tuple of str (n,), optional
        Keywords to match against npy file names. Pass [] to disable keyword
        search. The default is None (all labels and corresponding lag files).
    prefix : str, optional
        Key tag to identify parameter entries in the archive. Must be the same
        prefix originally passed to save_data(). Empty strings mean that all
        entries are treated as parameter entries. The default is 'metadata__'.
    full_recovery : bool, optional
        If True, scans configuration for auxiliary settings used to generate
        the kernel set and re-runs kernel_set() with the k_specs entry to
        recover the non-storable kernels, k_times, and k_props entries. Needed
        to fully restore the original configuration. The default is True. 

    Returns
    -------
    data : dict of arrays (m,)
        Collection of signal representations loaded from the npz archive. Loads
        all entries if no returns are given. Returns {} if prefix is empty.
    config : dict
        Top-level parameter configuration used in processing. Parameter entries
        have the prefix removed. Holds all archive entries if prefix is empty.
    """
    # Manage fixed returns:
    if files is None:
        # Default to all possible representations:
        files = ['raw', 'filt', 'env', 'log', 'inv',
                 'conv', 'bi', 'feat', 'norm']
    elif isinstance(files, str):
        files = [files]

    # Manage free returns: 
    if keywords is None:
        # Default to any labels:
        keywords = ['songs', 'noise']
    elif isinstance(keywords, str):
        keywords = [keywords]

    # Include sampling rates and parameter configuration:
    files = [*files, *[f'{key}_rate' for key in files]]
    keywords = [*keywords, prefix]

    # Safely retrieve requested data from archive:
    config, data = load_npz(path, files, keywords, prefix)
    return from_archive(data), config_from_archive(config, full_recovery)


# HELPERS FOR AUDIO DATA:


def channel_lags(signal, rate, ref=0, channels=None, frame=None, crop=True,
                 sequential=False, expand=True, full_return=False):
    """ Estimates channel-specific signal delay using cross-correlation.
        Correlates each specified channel with the reference channel and
        identifies the lag time that maximizes the correlation coefficient.
        Can also return the underlying correlation coefficients and lag times.

    Parameters
    ----------
    signal : 2D array of floats (m, n)
        Multi-channel signal data. Axis 0 is time, axis 1 are channels.
    rate : float or int
        Sampling rate of the signal in Hz.
    ref : int or 1D array of int (1,), optional
        Index of the reference channel in signal. The default is 0.
    channels : 1D array of ints (p), optional
        Indices of channels to correlate with the reference. If not specified,
        uses all channels except the reference. The default is None.
    frame : list or tuple of floats or ints (2,) or float or int, optional
        If specified, only considers lag times within the specified bounds in
        seconds when identifying the maximum correlation. Single values are
        taken as symmetric interval [-frame, frame]. The default is None.
    crop : bool, optional
        If True while full_return is True, when frame is given or sequential is
        True, returns rhos and lags only within the considered range of lag
        times from frame[0] to frame[1], or to the final upper bound if expand
        is True. The default is True. 
    sequential : bool, optional
        If True, restricts correlation maximization to increasingly more
        positive lag times for each channel in channels by updating the lower
        frame bound with one channel's computed lag time before proceeding to
        the next channel. If frame is not given, begins with the full range of
        available lag times. The default is False.
    expand : bool, optional
        If True while sequential is True and frame is specified, maintains the
        frame width when increasing the lower bound by updating the upper bound
        accordingly. Else, frame width decreases with each channel. Not secure
        against bounds exceeding each other! The default is True.
    full_return : bool, optional
        If True, returns correlation coefficients (Pearson's rho) and lag times
        of each cross-correlation alongside the delays. The default is False.

    Returns
    -------
    rhos : 2D array of floats (2 * m - 1, p)
        If full_return is True, correlation coefficients for each specified
        channel against the reference, normalized to Pearson's rho in [-1, 1].
    lags : 1D array of floats (2 * m - 1,)
        If full_return is True, lags in [(-m + 1) / rate, (m - 1) / rate] in s.
    delays : 1D array of floats (p)
        Estimated signal delay for each specified channel in seconds. Negative
        lag time means that the signal on a channel leads the signal on the
        reference. Vice versa, positive lag time means that the signal on a
        channel is delayed relative to the reference signal.
    """    
    # Input interpretation:
    if channels is None:
        channels = np.array([i for i in range(signal.shape[1]) if i != ref])
    # Ensure array format to enable slicing:
    elif not isinstance(channels, np.ndarray):
        channels = np.atleast_1d(channels)
    if not isinstance(ref, np.ndarray):
        ref = np.atleast_1d(ref)

    # Fall back to symmetry to ensure two bounds:
    if frame is not None and not np.iterable(frame):
        frame = [-frame, frame]

    # Compute channel-wise cross-correlations and lag times in seconds:
    rhos, lags = batch_correlation(signal[:, channels], signal[:, ref])
    lags = lags / rate    

    # Procedure options:
    if not sequential:
        if frame is None:
            # Find lags that maximize correlation:
            delays = lags[np.argmax(rhos, axis=0)]
        else:
            # Focus on a certain range of lag times:
            inds = (lags >= frame[0]) & (lags <= frame[1])
            delays = lags[inds][np.argmax(rhos[inds, :], axis=0)]
            if full_return and crop:
                # Adjust other outputs to lag range:
                rhos, lags = rhos[inds, :], lags[inds]

    elif sequential:
        if frame is None:
            # Fallback to full range:
            frame = [lags[0], lags[-1]]
            expand = False
        if full_return and crop:
            # Remember initial bound:
            lower_bound = frame[0]
        width = frame[1] - frame[0]

        # Focus on individual lag ranges:
        delays = np.zeros(rhos.shape[1])
        for i in np.arange(rhos.shape[1])[np.argsort(channels)]:
            # Find lag that maximizes current correlation:
            inds = (lags >= frame[0]) & (lags <= frame[1])
            delays[i] = lags[inds][np.argmax(rhos[inds, i])]
            # Update range towards positive lag, optionally maintaining width:
            frame = [delays[i], (delays[i] + width) if expand else frame[1]]
        if full_return and crop:
            # Adjust other outputs to expanded lag range:
            inds = (lags >= lower_bound) & (lags <= frame[1])
            rhos, lags = rhos[inds, :], lags[inds]

    # Return options:
    if full_return:
        return rhos, lags, delays
    return delays


def event_lags(signal, rate, edges, ref=0, channels=None, frame=None, crop=True,
               sequential=False, expand=True, config=None, full_return=False):
    # TODO: Add documentation.
    # Input interpretation:
    if config is not None:
        ref = config['lag_ref']
        channels = config['lag_channels']
        frame = config['lag_frame']
        sequential = config['sequential_lag']
        expand = config['expand_frame']
    if channels is None:
        channels = np.array([i for i in range(signal.shape[1]) if i != ref])
    # Ensure array format to enable slicing:
    elif not isinstance(channels, np.ndarray):
        channels = np.atleast_1d(channels)
    if not isinstance(ref, np.ndarray):
        ref = np.atleast_1d(ref)

    # Fall back to symmetry to ensure two bounds:
    if frame is not None and not np.iterable(frame):
        frame = [-frame, frame]
    
    # Prepare storage and underlying time axis:
    delays, rhos, lags = np.zeros((edges.shape[0], channels.size)), [], []
    time = np.arange(signal.shape[0]) / rate

    # Compute event-specific lagg times:
    for i, event in enumerate(edges):
        inds = (time >= event[0]) & (time <= event[1])
        output = channel_lags(signal[inds, :], rate, ref, channels, frame,
                              crop, sequential, expand, full_return)
        if full_return:
            rhos.append(output[0])
            lags.append(output[1])
            delays[i, :] = output[2]
        else:
            delays[i, :] = output

    # Return options:
    if full_return:
        return rhos, lags, delays
    return delays


# CLASSIFIER SERIALIZATION:


def save_perceptron(model, path):
    """ Writes parameter configuration of a perceptron to .json or .txt file.
        Only supports trained classifiers from sklearn.linear_model.Perceptron.
        Saved configuration can be used to re-assamble the given perceptron.
        Function taken from sklearn-json package.

    Parameters
    ----------
    model : sklearn Perceptron
        Fitted perceptron classifier. The function will crash when trying to
        access the attributes of an untrained model.
    path : str
        Path to text file where the parameter configuration is saved.
    """    
    # JSON-serialize model configuration:
    serialized = {
        'meta': 'perceptron',                                                  # Type meta information
        'coef_': model.coef_.tolist(),                                         # Weights assigned to the features
        'intercept_': model.intercept_.tolist(),                               # Constants in decision function
        'n_iter_': model.n_iter_,                                              # Number of iterations to reach stopping criterion           
        'classes_': model.classes_.tolist(),                                   # Unique class labels
        'params': model.get_params()                                           # Initialization parameters
    }
    # Write to text file:
    with open(path, 'w') as file:
        json.dump(serialized, file)
    return None


def load_perceptron(path):
    """ Loads parameter configuration of a perceptron and rebuilds the model.
        Accepts both .json and .txt files created by save_perceptron().
        Returns assembled model as sklearn.linear_model.Perceptron class.
        Function taken from sklearn-json package.

    Parameters
    ----------
    path : str
        Path to text file where the parameter configuration is stored.

    Returns
    -------
    model : sklearn Perceptron
        Newly created perceptron classifier with all relevant attributes
        overwritten by the loaded parameter configuration. Equivalent to the
        originally saved fitted model.

    Raises
    ------
    ValueError
        Breaks if the type meta information in the loaded parameter 
        configuration does not match 'perceptron', indicating that is has not
        been created by save_perceptron().
    """    
    # Load model configuration:
    with open(path, 'r') as file:
        serialized = json.load(file)
    # Assert correct classifier type:
    if serialized['meta'] != 'perceptron':
        raise ValueError('Loaded classifier is not a perceptron.')
    # Initialize new model:
    model = Perceptron(**serialized['params'])
    # Restore model state by overwriting defaults:
    model.coef_ = np.array(serialized['coef_']).astype(np.float64)             # Weights assigned to the features
    model.intercept_ = np.array(serialized['intercept_']).astype(np.float64)   # Constants in decision function
    model.n_iter_ = np.array(serialized['n_iter_']).astype(np.float64)         # Number of iterations to reach stopping criterion
    model.classes_ = np.array(serialized['classes_']).astype(np.int64)         # Unique class labels 
    return model


def serialize_csr(csr_matrix):
    """ Serializes a CSR matrix to a dictionary of its attributes. CSR
        (Compressed Sparse Row) format is a memory-efficient way to represent
        sparse data. JSON-serialization is required for writing the matrix
        to a text file to restore it later. Function taken from sklearn-json
        package.

    Parameters
    ----------
    csr_matrix : scipy sparse matrix
        CSR matrix to be serialized.

    Returns
    -------
    serialized : dict
        Matrix configuration in JSON-serializable format.
    """    
    # JSON-serialize matrix configuration:
    serialized = {
        'meta': 'csr',                                                         # Type meta information
        'data': csr_matrix.data.tolist(),                                      # Data array of the matrix
        'indices': csr_matrix.indices.tolist(),                                # Index array of the matrix
        'indptr': csr_matrix.indptr.tolist(),                                  # Index pointer array of the matrix
        '_shape': csr_matrix._shape,                                           # Shape of the matrix
    }
    return serialized


def deserialize_csr(serialized, data_type=np.float64, indices_type=np.int32,
                    indptr_type=np.int32):
    """ Rebuilds a CSR matrix from a serialized dictionary of its attributes.
        CSR (Compressed Sparse Row) format is a memory-efficient way to
        represent sparse data. JSON-deserialization is required for loading the
        matrix from a text file. Function taken from sklearn-json package.

    Parameters
    ----------
    serialized : dict
        Matrix configuration in JSON-serializable format.
    data_type : numpy dtype, optional
        Datatype of the data array of the rebuilt CSR matrix. The default
        is np.float64.
    indices_type : numpy dtype, optional
        Datatype of the index array of the rebuilt CSR matrix. The default
        is np.int32.
    indptr_type : numpy dtype, optional
        Datatype of the index pointer array of the rebuilt CSR matrix. The
        default is np.int32.

    Returns
    -------
    csr_matrix : scipy sparse matrix
        Deserialized CSR matrix.
    """    
    # Initialize new CSR matrix:
    csr_matrix = csr_matrix(tuple(serialized['_shape']))
    # Restore matrix state by overwriting defaults:
    csr_matrix.data = np.array(serialized['data']).astype(data_type)           # Data array of the matrix
    csr_matrix.indices = np.array(serialized['indices']).astype(indices_type)  # Index array of the matrix
    csr_matrix.indptr = np.array(serialized['indptr']).astype(indptr_type)     # Index pointer array of the matrix
    return csr_matrix


def save_svc(model, path):
    """ Writes parameter configuration of a SVC to .json or .txt file. SVC
        refers to a support vector machine classifier (in contrast to SVR for
        regression). Only supports trained models from sklearn.svm.SVC. Saved
        configuration can be used to re-assamble the given SVC. Function taken
        from sklearn-json package.

    Parameters
    ----------
    model : sklearn SVC
        Fitted support vector machine classifier. The function will crash when
        trying to access the attributes of an untrained model.
    path : str
        Path to text file where the parameter configuration is saved.
    """   
    # JSON-serialize model configuration:
    serialized = {
        'meta': 'svc',                                                         # Type meta information
        'class_weight_': model.class_weight_.tolist(),                         # Multipliers of regularization parameter C for each class
        'classes_': model.classes_.tolist(),                                   # Class labels
        'support_': model.support_.tolist(),                                   # Indices of support vectors
        '_n_support': model.n_support_.tolist(),                               # Number of support vectors for each class
        'intercept_': model.intercept_.tolist(),                               # Constants in decision function
        '_probA': model.probA_.tolist(),                                       # Parameter learned in Platt scaling when probability=True
        '_probB': model.probB_.tolist(),                                       # Parameter learned in Platt scaling when probability=True 
        '_intercept_': model._intercept_.tolist(),                             # Somehow, there are two intercept arrays in the fitted model
        'shape_fit_': model.shape_fit_,                                        # Shape of training vector
        '_gamma': model._gamma,                                                # Kernel coefficient for kernel types 'rbf', 'poly' and 'sigmoid'
        'params': model.get_params()                                           # Initialization parameters
    }
    # Type-dependent serialization of support vectors (sparse or dense):
    if isinstance(model.support_vectors_, csr_matrix):                         # Support vectors (empty array if kernel is precomputed)
        serialized['support_vectors_'] = serialize_csr(model.support_vectors_) 
    elif isinstance(model.support_vectors_, np.ndarray):
        serialized['support_vectors_'] = model.support_vectors_.tolist()
    # Type-dependent serialization of dual coefficients (sparse or dense):
    if isinstance(model.dual_coef_, csr_matrix):                               # Dual coefficients of the support vector in the decision function
        serialized['dual_coef_'] = serialize_csr(model.dual_coef_)
    elif isinstance(model.dual_coef_, np.ndarray):
        serialized['dual_coef_'] = model.dual_coef_.tolist()
    # Somehow, there are two dual coefficient arrays in the fitted model:
    if isinstance(model._dual_coef_, csr_matrix):
        serialized['_dual_coef_'] = serialize_csr(model._dual_coef_)
    elif isinstance(model._dual_coef_, np.ndarray):
        serialized['_dual_coef_'] = model._dual_coef_.tolist()
    # Write to text file:
    with open(path, 'w') as file:
        json.dump(serialized, file)
    return None


def load_svc(path):
    """ Loads parameter configuration of an SVC and rebuilds the model. SVC
        refers to a support vector machine classifier (in contrast to SVR for
        regression). Accepts both .json and .txt files created by save_svc().
        Returns assembled model as sklearn.svm.SVC class. Function taken from
        sklearn-json package.

    Parameters
    ----------
    path : str
        Path to text file where the parameter configuration is stored.

    Returns
    -------
    model : sklearn SVC
        Newly created support vector machine classifier with all relevant
        attributes overwritten by the loaded parameter configuration.
        Equivalent to the originally saved fitted model.

    Raises
    ------
    ValueError
        Breaks if the type meta information in the loaded parameter
        configuration does not match 'svc', indicating that is has not been
        created by save_svc().
    """  
    # Load model configuration:
    with open(path, 'r') as file:
        serial = json.load(file)
    # Assert correct classifier type:
    if serial['meta'] != 'svc':
        raise ValueError('Loaded classifier is not an SVM classifier.')
    # Initialize new model:
    model = SVC(**serial['params'])
    # Restore model state by overwriting defaults:
    model.shape_fit_ = serial['shape_fit_']                                    # Shape of training vector
    model._gamma = serial['_gamma']                                            # Kernel coefficient for kernel types 'rbf', 'poly' and 'sigmoid'
    model.class_weight_ = np.array(serial['class_weight_']).astype(np.float64) # Multipliers of regularization parameter C for each class
    model.classes_ = np.array(serial['classes_'])                              # Class labels
    model.support_ = np.array(serial['support_']).astype(np.int32)             # Indices of support vectors 
    model._n_support = np.array(serial['_n_support']).astype(np.int32)         # Number of support vectors for each class  
    model.intercept_ = np.array(serial['intercept_']).astype(np.float64)       # Constants in decision function
    model._probA = np.array(serial['_probA']).astype(np.float64)               # Parameter learned in Platt scaling when probability=True
    model._probB = np.array(serial['_probB']).astype(np.float64)               # Parameter learned in Platt scaling when probability=True
    model._intercept_ = np.array(serial['_intercept_']).astype(np.float64)     # Somehow, there are two intercept arrays in the fitted model
    # Type-dependent deserialization of support vectors (sparse or dense):
    support_vectors = serial['support_vectors_']                               # Support vectors (empty array if kernel is precomputed)
    if 'meta' in support_vectors and support_vectors['meta'] == 'csr':
        model.support_vectors_ = deserialize_csr(support_vectors)
        model._sparse = True
    else:
        model.support_vectors_ = np.array(support_vectors).astype(np.float64)
        model._sparse = False
    # Type-dependent deserialization of dual coefficients (sparse or dense):
    dual_coef = serial['dual_coef_']                                           # Dual coefficients of the support vector in the decision function
    if 'meta' in dual_coef and dual_coef['meta'] == 'csr':
        model.dual_coef_ = deserialize_csr(dual_coef)
    else:
        model.dual_coef_ = np.array(dual_coef).astype(np.float64)
    # Somehow, there are two dual coefficient arrays in the fitted model:
    dual_coef = serial['_dual_coef_']
    if 'meta' in dual_coef and dual_coef['meta'] == 'csr':
        model._dual_coef_ = deserialize_csr(dual_coef)
    else:
        model._dual_coef_ = np.array(dual_coef).astype(np.float64)
    return model


# LEGACY FUNCTIONS:


def save_config(config, path):
    """ Writes parameter configuration of the songdetector model to file.
        Supports saving in .json or .txt format. Removes parameters that are
        not easily serializable (classifier) or can be retrieved with the help
        of other parameters (kernels, k_times, k_props).

    Parameters
    ----------
    config : dict
        Top-level parameter configuration as returned by configuration().
    path : str
        Absolute or relative path to the file where the configuration is saved.
        Missing or incorrect file extensions are automatically set to '.txt'.
    """
    # Validate file format:
    path = check_extension(path, ('txt', 'json'))
    # Manage saved parameters:    
    save_dict = config.copy()
    excluded_keys = ['kernels', 'k_times', 'k_props', 'classifier']
    [save_dict.pop(key) for key in excluded_keys]
    # Save configuration to file:
    write_json(save_dict, path)
    return None


def load_config(path):
    """ Loads parameter configuration of the songdetector model from file.
        Supports loading from .json or .txt format. Restores kernel-related
        parameters (kernels, k_times, k_props) omitted by save_config() and
        adds a placeholder for the classifier.

    Parameters
    ----------
    path : str
        Absolute or relative path to the file where the configuration is saved.

    Returns
    -------
    config : dict
        Top-level parameter configuration that matches one returned by
        configuration(), including all original parameter keys.
    """    
    config = load_json(path)
    # Restore kernel-related parameters:
    specs = np.array(config['k_specs'])
    config['k_specs'] = specs
    packed = gabor_set(config['env_rate'], specs=specs)
    config['kernels'] = packed[0]
    config['k_times'] = packed[2]
    config['k_props'] = packed[3]
    # Add classifier placeholder:
    config['classifier'] = None
    return config


def same_config(config1, config2, compare=None, check_kernels=True):
    """ Validates consistency of two parameter configurations.
        Compares the dictionary entries under the specified keys and returns
        a single Boolean indicating whether all comparisons evaluate to True.
        Cannot compare nested variables ('kernels', 'k_times', 'k_props',
        'classifier') and, by default, also excludes parameters with minor
        relevance to pipeline functionality ('seed', 'n_iter'). To check the
        consistency between the two kernel sets, set check_kernels=True to
        enable array comparison of the 'k_specs' parameter. 

    Parameters
    ----------
    config1 : dict or str
        Top-level parameter configuration in the format of configuration(), or
        a path to a config file (txt or json) to recover with load_config().
    config2 : dict or str
        Top-level parameter configuration in the format of configuration(), or
        a path to a config file (txt or json) to recover with load_config().
    compare : list of str, optional
        Valid parameters to compare between the two configurations. If None,
        compares all except 'kernels', 'k_times', 'k_props', 'k_specs',
        'classifier', 'seed', and 'n_iter'. Use check_kernels to enable a
        dedicated comparison of 'k_specs'. The default is None.
    check_kernels : bool, optional
        If True, also checks the consistency of the 'k_specs' parameter to
        assert that the same kernel set is used in both configurations. The
        default is True.

    Returns
    -------
    is_same : bool
        Returns True if all performed comparisons between the two parameter
        configurations evaluate to True. Else, returns False.
    
    Raises
    ------
    ValueError
        Breaks if compare is specified and requests any of the nested variables
        'kernels', 'k_times', 'k_props', 'k_specs', and 'classifier'.
    KeyError
        By default (if compare is unspecified), also breaks if one
        configuration has any keys that are not present in the other.
    """    
    # Input interpretation:
    if isinstance(config1, str):
        config1 = load_config(config1)
    if isinstance(config2, str):
        config2 = load_config(config2)

    # Manage excluded entries:
    skip = ['kernels', 'k_times', 'k_props', 'k_specs', 'classifier']
    if compare is None:
        all_keys = set(config1.keys()).union(config2.keys())
        skip += ['seed', 'n_iter']
        compare = [key for key in all_keys if key not in skip]
    elif any(np.isin(compare, skip)):
        sequence = string_series(skip, conj='and')
        raise ValueError(f'Cannot compare nested parameters ({sequence}). '
                          'Use check_kernels to enable comparison of k_specs.')

    # Compare element-wise:
    is_same = [config1[key] == config2[key] for key in compare]
    if check_kernels:
        # Assert identical kernel sets (array comparison):
        is_same.append(np.all(config1['k_specs'] == config2['k_specs']))
    return all(is_same)
