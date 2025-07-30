import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import bottleneck as bn
from sklearn.linear_model import LinearRegression
from sklearn.metrics import roc_auc_score
from scipy.integrate import trapezoid, cumulative_trapezoid
from scipy.signal import correlate, correlation_lags, convolve, get_window
try:
    from scipy.signal import ShortTimeFFT
    has_shorttimefft = True
except ImportError:
    has_shorttimefft = False
from scipy.signal.windows import hamming
from scipy.cluster.hierarchy import linkage, dendrogram, set_link_color_palette
from .misctools import ensure_array, unsort_unique, safe_zip
from .arraytools import array_slice, remap_array, edge_along_axis


def linear_regression(x, y, ax=None, **kwargs):
    """ Fits an ordinary least squares LinearRegression model of y over x.
        Returns the predicted values of y as well as intercept, coefficients,
        and r**2 coefficient of the regression. Fitted regression line(s) can
        optionally be displayed in the provided subplot.

    Parameters
    ----------
    x : 2D array (m, n) or 1D array (m,) of floats
        One or multiple independent variables (predictors, column-wise).
        If multi-factor, trains a model with several coefficients.
    y : 2D array (m, p) or 1D array (m,) of floats
        One or multiple dependent variables (targets, column-wise).
        If multi-target, trains a model with several outputs.
    ax : matplotlib axes object, optional
        If specified, a subplot to plot regression lines. The default is None.
    **kwargs : dict, optional
        Additional keyword arguments passed to ax.plot().

    Returns
    -------
    fit : 2D array (m, p) of floats
        Predicted values of y over x minimizing the residual Sum of Squares
        between y and the fit. Returns a regression line for each target in y.
    params : dict
        Selection of parameters of the fitted LinearRegression model including
        'intercept': float or 1D array (p,) of floats
        -> Independent term (y-axis intercept) for each target in y.
        'coef': 2D array (n, p) or 1D array (p,) of floats
        -> Coefficient of each predictor in x for each target in y.
        'score': float
        -> Coefficient of determination r**2 = 1 - (residual SS / total SS)
    """    
    # Ensure 2D column:
    if x.ndim == 1:
        x = x[:, None]
    if y.ndim == 1:
        y = y[:, None]

    # Fit regression model to data:
    model = LinearRegression().fit(x, y)
    fit = model.predict(x)
    params = {
        'intercept': model.intercept_,
        'coef': model.coef_,
        'score': model.score(x, y)
    }
    if ax is not None:
        # Optional visualization:
        ax.plot(x, fit, **kwargs)
    return fit, params


def linear_regressions(x, y, cross_x=True, cross_y=True):
    """ Fits some ordinary least squares LinearRegression models of y over x.
        Loop-wrapper to linear_regression() that can train separate models for
        each predictor in x, each target in y, or each cross-wise combination.
        Returns the predicted values of y as well as intercept, coefficients,
        and r**2 of the regressions. If both cross_x and cross_y are False,
        returns immediately with a single call to linear_regression(x, y).

    Parameters
    ----------
    x : 2D array (m, n) or 1D array (m,) of floats
        One or multiple independent variables (predictors, column-wise).
    y : 2D array (m, p) or 1D array (m,) of floats
        One or multiple dependent variables (targets, column-wise).
    cross_x : bool, optional
        If True, performs single-factor regression with each predictor in x,
        else multi-factor regression using all predictors. The default is True.
    cross_y : bool, optional
        If True, performs single-target regression with each target in y, else
        multi-target regression using all targets. The default is True.

    Returns
    -------
    fits : 3D array (m, p, n if cross_x else 1) of floats
        Predicted values of y over x minimizing the residual Sum of Squares
        between y and each fit. Axis 0 are always samples. Axis 1 are targets,
        corresponding to multiple independent models if cross_y is True, else
        the same model. Axis 2 are predictors, corresponding to multiple
        independent models if cross_x is True, else the same model.
    parameters : dict
        Selection of parameters of the fitted LinearRegression models including
        'intercept': 2D array (p, 1) or (1, n) or (p, n) of floats
        -> Independent term (y-axis intercept) per target and/or predictor.
        'coef': 2D array (p, n) of floats
        -> Coefficient of each predictor in x for each target in y.
        'score': 2D array (p, 1) or (1, n) or (p, n) of floats
        -> Coefficient of determination r**2 = 1 - (residual SS / total SS)
    """    
    # Ensure 2D column:
    if x.ndim == 1:
        x = x[:, None]
    if y.ndim == 1:
        y = y[:, None]

    # Single-model early exit:
    if not cross_x and not cross_x:
        return linear_regression(x, y)

    # Prepare output storage arrays:
    nx = x.shape[1] if cross_x else 1
    ny = y.shape[1] if cross_y else 1
    fits = np.zeros((*y.shape, nx))
    parameters = {
        'intercept': np.zeros((ny, nx)),
        'coef': np.zeros((y.shape[1], x.shape[1])),
        'score': np.zeros((ny, nx))
    }

    # Multi-model regression:
    predictor, target = x, y
    for i in range(nx):
        i_slice = slice(i, i + 1)
        if cross_x:
            # Single-factor subset:
            predictor = x[:, i_slice]
        for j in range(ny):
            j_slice = slice(j, j + 1)
            if cross_y:
                # Single-target subset:
                target = y[:, j_slice]

            # Fit regression model to subset of data:
            fit, params = linear_regression(predictor, target)

            # Assign model output to storage:
            fits[:, j_slice, i_slice] = fit[..., None]
            parameters['intercept'][j, i_slice] = params['intercept']
            parameters['coef'][j, i_slice] = params['coef']
            parameters['score'][j, i] = params['score']
    return fits, parameters


def nonlinearity(data, thresh, operator='>', dtype=float, axes_map=None):
    """ Applies a simple threshold non-linearity to the data.
        Provides different comparison operators for applying the threshold.

    Parameters
    ----------
    data : ND array of floats or ints (any shape)
        Dataset to apply the threshold.
    thresh : float or int or array-like of floats or ints (any shape)
        Values of the threshold non-linearity. Scalars are applied to each
        entry of data. Iterables are converted to array format if necessary.
        Must be broadcastable against data if axes_map is not provided.
    operator : str, optional
        Comparison operator for applying the threshold. Options are '>',
        '<', '>=', and '<='. The default is '>'.
    dtype : type, optional
        Data type of the output array. The default is float.
    axes_map : int, optional
        If specified, index mapping linking dimensions of thresh to dimensions
        of data. Calls remap_array() to expand thresh to data.ndim, move its
        dimensions into requested positions, and validate shape compatibility
        of data and the reshaped thresh. Skips all steps if thresh is a scalar.
        The default is None.

    Returns
    -------
    array of dtype (data.shape)
        Binary output of element-wise comparison between data and threshold.
    """
    # Define operation:    
    compare_func = {
        '>': np.greater,
        '<': np.less,
        '>=': np.greater_equal,
        '<=': np.less_equal,
        }[operator]

    # Perform operation:
    if axes_map is not None:
        # Ensure broadcastability by adding and moving dimensions:
        remap_kwargs = dict(shape=data.shape, pass_scalars=True)
        thresh = remap_array(thresh, axes_map, **remap_kwargs)
    return compare_func(data, thresh).astype(dtype)


def auto_correlation(data):
    """ Computes the full 1D auto-correlation of the data with itself.
        Returns Pearson's correlation coefficient rho in the range [-1, 1].
        Clips output to this range to not propagate numerical inaccuracies.

    Parameters
    ---------- 
    data : 1D array of floats or ints (m,)
        Data to to be auto-correlated. 

    Returns
    -------
    correlated : 1D array of floats (2 * m - 1,)
        Auto-correlation of the data, normalized to Pearson's rho in [-1, 1].
    lags : 1D array of ints (2 * m - 1,)
        Lag indices in [-m + 1, m - 1] with index 0 (no lag) at the center.
    """    
    # Center data to zero mean:
    centered = data - data.mean()

    # Compute auto-correlation and corresponding lag indices:
    correlated = correlate(centered, centered, mode='full', method='auto')
    lags = correlation_lags(centered.size, centered.size, 'full')
    
    # Normalize to Pearson's rho:
    correlated /= np.sum(centered**2)
    return np.clip(correlated, -1, 1), lags


def cross_correlation(data1, data2):
    """ Computes the full 1D cross-correlation of the two datasets.
        Returns Pearson's correlation coefficient rho in the range [-1, 1].
        Clips output to this range to not propagate numerical inaccuracies.

    Parameters
    ----------
    data1 : 1D array of floats or ints (m,)
        Primary dataset to be cross-correlated.
    data2 : 1D array of floats or ints (n,)
        Secondary dataset to be cross-correlated.

    Returns
    -------
    correlated : 1D array of floats (m + n - 1,)
        Cross-correlation of the data, normalized to Pearson's rho in [-1, 1].
    lags : 1D array of ints (m + n - 1,)
        Lag indices in [-n + 1, m - 1] with index 0 (no lag) at lags[n - 1].
        Negative lag means data2 leads data1, and vice versa for positive lag.
    """    
    # Center data to zero mean:
    centered1 = data1 - data1.mean()
    centered2 = data2 - data2.mean()

    # Compute cross-correlation and corresponding lag indices:
    correlated = correlate(centered1, centered2, mode='full', method='auto')
    lags = correlation_lags(centered1.size, centered2.size, 'full')

    # Normalize to Pearson's rho:
    correlated /= np.sqrt(np.sum(centered1**2) * np.sum(centered2**2))
    return np.clip(correlated, -1, 1), lags


def shift_ops_shape(shape1, shape2, mode='full'):
    """ Output shape resulting from a shifting operation between two arrays.
        Refers to convolution or correlation with the given mode using scipy.
        Expects the same number of dimensions for both input arrays.

    Parameters
    ----------
    shape1 : array-like of ints (m,)
        Shape of the first input array (array1, the "signal").
    shape2 : array-like of ints (m,)
        Shape of the second input array (array2, the "kernel").
    mode : str, optional
        Defines how to crop the native 'full' output of the operation, which
        begins with a single sample overlap (array1[-1] on array2[0]) and ends
        when both endpoints are aligned (array1[-1] on array2[-1]). Applies
        zero-padding to array1 where array2 is overhanging. Options are
        # 'full': Returns raw uncropped output.
        # 'valid': Crops to area where both inputs overlap completely.
        # 'same': Crops to shape1, centered in the full output.
        # 'axis': Crops to shape1 only along the axes of operation.
        Note that 'axis' is a custom mode that is not inherent to scipy. Axes
        of operation are all dimensions where both inputs are non-singleton.
        The default is 'full'.

    Returns
    -------
    shape : 1D array of ints (m,)
        Shape of the output array resulting from the shifting operation.
    """    
    # Control equal dimensionality:
    zipped = safe_zip(shape1, shape2)
    # Define output shape:
    if mode == 'full':
        return np.array([s1 + s2 - 1 for s1, s2 in zipped])
    elif mode == 'valid':
        return np.array([max(s1 - s2 + 1, 0) for s1, s2 in zipped])
    elif mode == 'same':
        return np.array(shape1)
    elif mode == 'axis':
        shape = [max(s1, s2) if 1 in (s1, s2) else s1 for s1, s2 in zipped]
        return np.array(shape)


def shift_ops_lags(shape1, shape2, mode='full'):
    """ Lag indices resulting from a shifting operation between two arrays.
        Refers to convolution or correlation with the given mode using scipy.
        Expects the same number of dimensions for both input arrays.
        
    Parameters
    ----------
    shape1 : array-like of ints (m,)
        Shape of the first input array (array1, the "signal").
    shape2 : array-like of ints (m,)
        Shape of the second input array (array2, the "kernel").
    mode : str, optional
        Defines how to crop the native 'full' output of the operation, which
        begins with a single sample overlap (array1[-1] on array2[0]) and ends
        when both endpoints are aligned (array1[-1] on array2[-1]). Applies
        zero-padding to array1 where array2 is overhanging. Options are
        # 'full': Returns raw uncropped output.
        # 'valid': Crops to area where both inputs overlap completely.
        # 'same': Crops to shape1, centered in the full output.
        # 'axis': Crops to shape1 only along the axes of operation.
        Note that 'axis' is a custom mode that is not inherent to scipy. Axes
        of operation are all dimensions where both inputs are non-singleton.
        The default is 'full'.

    Returns
    -------
    lags : list (m,) of 1D arrays of ints
        Lag indices resulting from the shifting operation, depending on mode.
        Returns one index array per input dimension. Negative lag means array2
        leads array1, and vice versa for positive lag.
    """    
    # Control equal dimensionality:
    zipped = safe_zip(shape1, shape2)
    # Define lag indices:
    if mode == 'axis':
        modes = ['full' if 1 in (s1, s2) else 'same' for s1, s2 in zipped]
        zipped = zip(shape1, shape2, modes)
        return [correlation_lags(s1, s2, mode) for s1, s2, mode in zipped]
    return [correlation_lags(s1, s2, mode) for s1, s2 in zipped]


# def batch_correlation(signal, kernels, signal_map=None, kernel_map=None,
#                       normalize=True, crop=False):
#     #TODO: Fix normalization and add docstring.

#     # Determine dimensionality of output array:
#     signal_targets = tuple(signal_map.values())
#     kernel_targets = tuple(kernel_map.values())
#     out_dims = max(max((max(signal_targets), max(kernel_targets))) + 1,
#                    abs(min((min(signal_targets), min(kernel_targets)))))

#     # Reshape signal array:
#     if signal_map is not None:
#         signal = remap_array(signal, signal_map, out_dims)
#     signal_shape = np.array(signal.shape)
    
#     # Reshape kernel array:
#     if kernel_map is not None:
#         kernels = remap_array(kernels, kernel_map, out_dims)
#     kernel_shape = np.array(kernels.shape)

#     # Get dimensions that will expand when input arrays are shifted:
#     exposed_axes = np.nonzero((signal_shape > 1) & (kernel_shape > 1))[0]

#     if normalize:
#         # Center both input arrays to zero means along axes of operation:
#         signal -= np.mean(signal, axis=tuple(exposed_axes), keepdims=True)
#         kernels -= np.mean(kernels, axis=tuple(exposed_axes), keepdims=True)

#     # Perform correlation operation and return uncropped output:
#     output = correlate(signal, kernels, mode='full', method='auto')

#     if normalize:
#         # Normalize correlation output to Pearson's r:
#         signal_var = np.sum(signal**2, tuple(exposed_axes), keepdims=True)
#         kernel_var = np.sum(kernels**2, tuple(exposed_axes), keepdims=True)
#         output /= np.sqrt(signal_var * kernel_var)
#         #output = np.clip(output, -1, 1)
#     if crop:
#         # Crop 'full' output along axes of operation:
#         out_shape = np.array(output.shape)[exposed_axes]
#         signal_shape = signal_shape[exposed_axes]
#         overhang = (out_shape - signal_shape) // 2
#         return array_slice(output, exposed_axes.tolist(), overhang.tolist(),
#                            (overhang + signal_shape).tolist())
#     return output  


def batch_correlation(data1, data2, axis=0):
    """ Computes the full 2D cross-correlation of the two datasets along axis.
        Correlates each slice of data1 (2D array) with data2 (1D or 2D array),
        preserving all slices in the output (else reduced to subset by scipy).
        Returns Pearson's correlation coefficient rho in the range [-1, 1].
        Clips output to this range to not propagate numerical inaccuracies.

    Parameters
    ----------
    data1 : 2D array of floats (m, n)
        Primary dataset to be cross-correlated slice-wise with data2.
    data2 : 2D array of floats (p, 1) or (1, p) or 1D array of floats (p,)
        Secondary dataset to be cross-correlated with each slice of data1.
        If 2D, must have one singleton dimension and be oriented along axis.
        If 1D, expanded to a 2D column or row vector, depending on axis.
    axis : int, optional
        Array axis along which correlation is performed. Options are 0 (each
        column of data1) and 1 (each row of data1). The default is 0.

    Returns
    -------
    correlated : 2D array of floats (m + p - 1, n) or (m, n + p - 1)
        Correlation of data slices, normalized to Pearson's rho in [-1, 1].
    lags : 1D array of ints (m + p - 1,) or (n + p - 1,)
        Lag indices in [-p + 1, m - 1] or [-p + 1, n - 1], depending on axis.
        Negative lag means data2 leads data1, and vice versa for positive lag.

    Raises
    ------
    ValueError
        Breaks if data2 is 2D and has no singleton dimension along 1 - axis.
    """    
    # Input interpretation:
    other_axis = 1 - axis
    if data2.ndim == 1:
        # Ensure 2D array:
        data2 = np.expand_dims(data2, axis=other_axis)
    # Input validation:
    elif data2.shape[other_axis] != 1:
        raise ValueError(f'If data2 is 2D and axis is {axis}, '\
                         f'shape[{other_axis}] must be 1.')

    # Center data to zero mean:
    centered1 = data1 - data1.mean(axis=axis, keepdims=True)
    centered2 = data2 - data2.mean(axis=axis, keepdims=True)

    # Compute correlations and corresponding lag indices:
    correlated = correlate(centered1, centered2, mode='full', method='auto')
    lags = correlation_lags(centered1.shape[axis], centered2.shape[axis])

    # Normalize to Pearson's rho:
    correlated /= np.sqrt(np.sum(centered1**2, axis=axis, keepdims=True) *
                          np.sum(centered2**2, axis=axis, keepdims=True))
    return np.clip(correlated, -1, 1), lags
    

def batch_convolution(data1, data2, axes1=None, axes2=None,
                      normalize=True, crop=True):
    """ Performs ND convolution of the two input arrays along one or more axes.
        Computes 'full' convolution using scipy.signal.convolve(), requiring
        data1 and data2 to have the same number of dimensions. With axes1 and
        axes2, the dimensions of the respective input array can be remapped
        onto a higher-dimensional shape to reach common output dimensionality. 
        Convolution operates along all dimensions where both input arrays are
        non-singleton. Along axes of operation, the output can be normalized by
        the size of data2 or cropped to match the original shape of data1.

    Parameters
    ----------
    data1 : ND array of floats
        First input array ("signal") to convolve.
    data2 : ND array of floats
        Second input array ("kernel") to convolve.
    axes1 : dict {ints: ints} or iterable (array.ndim,) of ints
        Index mapping linking dimensions of data1 to their target positions in
        the output array, in a format accepted by remap_array(). If not given,
        data1 and data2 must already have the same dimensionality.
    axes2 : dict {ints: ints} or iterable (array.ndim,) of ints
        Index mapping linking dimensions of data2 to their target positions in
        the output array, in a format accepted by remap_array(). If not given,
        data1 and data2 must already have the same dimensionality.
    normalize : bool, optional
        If True, normalizes the output by the product of the sizes of data2
        along the axes of operation. The default is True.
    crop : bool, optional
        If True, crops the output to match the shape of data1 along the axes
        of operation. If False, returns the 'full' output of the convolution.
        The default is True.

    Returns
    -------
    output : ND array of floats
        Result of the convolution of data1 with data2.
    """    
    # Base output dimensionality on input:
    out_dims = max(data1.ndim, data2.ndim)
    if axes1 is not None:
        # Compare to highest provided target dimension for data1: 
        targets1 = tuple(axes1.values()) if isinstance(axes1, dict) else axes1
        out_dims = max(out_dims, max(targets1) + 1, abs(min(targets1)))
    if axes2 is not None:
        # Compare to highest provided target dimension for data2:
        targets2 = tuple(axes2.values()) if isinstance(axes2, dict) else axes2
        out_dims = max(out_dims, max(targets2) + 1, abs(min(targets2)))

    # Adjust input shapes:
    if axes1 is not None:
        data1 = remap_array(data1, axes1, out_dims)
    if axes2 is not None:
        data2 = remap_array(data2, axes2, out_dims)

    # Perform ND convolution on CPU:
    output = convolve(data1, data2, mode='full', method='auto')

    # No post-processing early exit:
    if not normalize and not crop:
        return output

    # Get axes of operation (expanded size by shift between arrays):
    shape1, shape2 = np.array(data1.shape), np.array(data2.shape)
    ops_axes = np.nonzero((shape1 > 1) & (shape2 > 1))[0]

    if normalize:
        # By kernel size along operation axes:
        output /= np.prod(shape2[ops_axes])
    if crop:
        # From 'full' output along operation axes:
        out_shape = np.array(output.shape)[ops_axes]
        shape1 = shape1[ops_axes]
        overhang = (out_shape - shape1) // 2
        return array_slice(output, ops_axes.tolist(), overhang.tolist(),
                           (overhang + shape1).tolist())
    return output


def sliding_window(data, window, step=None, rate=None, func=np.mean,
                   align='center', over_edge='right', over_win='left'):
    """ Custom sliding window function application to 1D or 2D data.
        Implements sliding window as a general for-loop and is hence slower
        than more specialized functions (e.g. convolution), but more flexible.

    Parameters
    ----------
    data : 2D array (m, n) or 1D array (m,) or list of floats or ints
        Data to apply the given function to. Sliding window is performed along
        each array column (1D is reshaped to 2D). Must be compatible with the
        requirements of func (dtype, ...). 
    window : int or float
        Number of consecutive samples passed to func at each step. Each window
        corresponds to one entry in output. If rate is specified, taken as a
        time interval to calculate the number of included samples. Must not be
        smaller than step. Windows are positioned around their respective
        anchor point as specified by align. Anchor points correspond to one of
        the samples in window. Windows that exceed the data array are cropped
        to size instead of being padded.
    step : int or float, optional
        Number of samples between anchor points (including one of two points).
        If rate is specified, taken as a time interval. Must not exceed window.
        Determines the number of windows and (with respect to align) the
        placing of anchor points along the data array as well as the overlap
        between windows. If unspecified, takes each sample as an anchor point,
        so that the output has as many entries as there are samples in data.
        The default is None.
    rate : int or float, optional
        If specified, window and step are interpreted as time intervals in
        seconds and may be passed as floats. Further determines whether anchor
        points are returned as indices or time points. The default is None.
    func : function, optional
        Function to apply to each window. Must take a 2D array as positional
        argument as well as an axis=0 keyword argument, and return a 1D array.
        Must be compatible with data. The default is np.mean().
    align : str, optional
        The position of the window relative to its anchor point. Determines the
        placement of anchor points along data. Options are
        # 'right': Anchor point is the first sample of each window.
        -> Starts placement at the first sample of data, proceeding forward.
        # 'left': Anchor point is the last sample of each window.
        -> Starts placement at the last sample of data, proceeding backwards.
        # 'center': Anchor point is in the middle of window (see over_win).
        -> Finds possible number of steps over data array, dividing remainders.
        -> Equal space from first/last anchor to array edges (see over_edge).
        The default is 'center'.
    over_edge : str, optiona
        If align is 'center' and remainders % 2 != 0, specifies the side of the
        data array to receive the extra sample when placing the anchor points.
        Options are 'right' and 'left'. The default is 'right'.
    over_win : str, optional
        If align is 'center' and window % 2 == 0, specifies the side of the
        anchor point that receives the extra sample when positioning the
        window. Options are 'right' and 'left'. The default is 'left'. 

    Returns
    -------
    output : 2D array (p, n) or 1D array (p,) of floats
        Accumulated returns of func applied to each window. Returns 1D if input
        was 1D, else 2D.
    inds : 1D array of ints or floats (p,)
        Anchor point corresponding to each window and output row. If rate is
        specified, returned in seconds (else indices along first axis of data).

    Raises
    ------
    ValueError
        Breaks if step is smaller than window.
    """    
    # Input interpretation:
    if rate is not None:
        window = max(int(window * rate), 1)
        if step is not None:
            step = max(int(step * rate), 1)
    if step is None:
        step = 1
    # Input validation:
    if window < step:
        raise ValueError('Step size must not be less than window size.')
    # Assert 2D array (columns):
    data, in_shape = ensure_array(var=data, dims=(1, 2), shape=(-1, None),
                                  list_shapes=True)

    # Manage window anchoring:
    n_rest = data.shape[0] % step
    n_side = n_rest // 2 + (n_rest % 2) * (over_edge == 'left')
    first_anchor = {'right': 0,
                    'left': data.shape[0] - 1,
                    'center': n_side
                    }[align]
    anchors = np.arange(first_anchor,
                        -1 if align == 'left' else data.shape[0],
                        -step if align == 'left' else step)
    # Apply sliding window:
    output = np.zeros((len(anchors), data.shape[1]))
    inds = np.zeros(len(anchors), dtype=int)
    for i, anchor in enumerate(anchors[::-1] if align == 'left' else anchors):
        start = {
            'right': anchor,
            'left': anchor - window + 1,
            'center': anchor - window // 2 + 1
            }[align]
        if (align == 'center') and (over_win == 'left'):
            start -= 1
        start = max(start, 0)
        end = min(start + window, data.shape[0])
        output[i, :] = func(data[start:end], axis=0)
        inds[i] = anchor
    # Time scale conversion:
    if rate is not None:
        inds /= rate
    return output.ravel() if len(in_shape) == 1 else output, inds


def bn_window(data, window, func='mean', min_count=1, fix_edge=True, **kwargs):
    """ Wrapper to bottleneck's C-implemented sliding window functions.
        Less flexible but much faster than any for-loop implementation. Some
        functions

    Parameters
    ----------
    data : 2D array (m, n) or 1D array (m,) or list of floats
        Data to apply the specified bottleneck function to. Sliding window is
        performed along each array column (1D is reshaped to 2D).
    window : int
        Number of consecutive samples in each window. Must be >= 1. Step size
        is always 1, so that the output has as many entries as there are
        samples in data. Windows are always positioned to the left of their
        anchor point, i.e. the anchor point corresponds to the last sample in
        each window. Windows that exceed the start of the data array are padded
        with NaNs.
    func : str, optional
        Specifies one of bottleneck's move_{func} sliding window functions to
        apply to the data. Options are 'sum', 'mean', 'std', 'var', 'min',
        'max', 'argmin', 'argmax', 'median', and 'rank'. The default is 'mean'.
    min_count : int, optional
        Minimum number of non-NaN samples allowed in each window. Must be >= 1.
        If this count is not reached, the respective output entry is set to
        NaN. If min_count is > 1, the first min_count - 1 output entries will
        be Nan due to the window padding. If min_count is 1, behaves as if the
        windows exceeding the start of data are cropped to size, ignoring any
        padding. The default is 1.
    fix_edge : bool, optional
        If True, sets the first window - 1 output entries to the value of the
        first completely overlapping window. Else, leaves output as is (will
        reflect increasing sample count across partially overlapping windows).
        Can be used to eliminate NaNs (if min_count > 1) or to avoid strong
        initial fluctuations. The default is False.
    **kwargs : dict, optional
        If func is 'std' or 'var', allows to specify the ddof keyword argument.
        Specifying the axis keyword argument will result in an error, because
        this function sets axis=0 in all cases.

    Returns
    -------
    output : 2D array (m, n) or 1D array (m,) of floats
        Output of the specified bottleneck function. Has exactly the same shape
        as the input data. Always contains NaN entries unless min_count is 1.
    """    
    # Assert 2D array (columns):
    data, in_shape = ensure_array(var=data, dims=(1, 2), shape=(-1, None),
                                  list_shapes=True)
    # Input interpretation:
    func = {
        'sum': bn.move_sum,
        'mean': bn.move_mean,
        'std': bn.move_std,
        'var': bn.move_var,
        'min': bn.move_min,
        'max': bn.move_max,
        'argmin': bn.move_argmin,
        'argmax': bn.move_argmax,
        'median': bn.move_median,
        'rank': bn.move_rank,
        }[func]
    # Apply sliding window function:
    output = func(data, window, min_count, axis=0, **kwargs)
    if fix_edge:
        # Overwrite upper edge (overlap & NaN policy):
        output[:window - 1, :] = output[window - 1, :]
    return output.ravel() if len(in_shape) == 1 else output


def moving_center(data, func=np.median, threshold=None, criterion=None,
                  iterations=10, full_return=False, **kwargs):
    """ Repeatedly calculates a center metric for a steadily shrinking dataset.
        At each iteration, removes the data point that is furthest from the
        current center, then recalculates the center. Runs for a fixed number
        of iterations or until meeting the specified convergence criterion.

    Parameters
    ----------
    data : 1D array (m,) of floats or ints
        Univariate dataset for which to find a consistent center.
    func : callable, optional
        Function to calculate the center metric. Must accept the data array as
        only argument and return a single value. The default is np.median.
    threshold : float or int or callable, optional
        If specified, critical value to trigger early stopping if the absolute
        difference between previous and current center is smaller. If callable,
        must accept the data array plus any given keyword arguments and return
        a single value. The default is None. 
    criterion : callable, optional
        If specified, advanced criterion to trigger early stopping when its
        output is True. Must accept the data array and a list of all previous
        and current centers as arguments, plus any given keyword arguments, and
        return a single boolean. The default is None.
    iterations : int, optional
        Number of data points to remove. If threshold or criterion is provided,
        set to the largest possible value (data.size - 1). The default is 10.
    full_return : bool, optional
        If True, returns all calculated centers instead of just the final one.
        The default is False.
    **kwargs : optional
        Additional keyword arguments to pass to criterion or threshold.

    Returns
    -------
    included : 1D array of ints (m - iterations,)
        Indices of remaining data points corresponding to the final center.
    center : float or list (iterations,) of floats
        Final center metric, or all calculated centers if full_return is True.

    Raises
    ------
    ValueErrorf
        Breaks if iterations is larger than or equal the number of data points.
    """    
    # Input interpretation:
    if threshold is not None or criterion is not None:
        iterations = data.shape[0] - 1
    # Input validation:
    elif iterations >= data.shape[0]:
        raise ValueError('Number of iterations must be less than data size.')

    # Run algorithm:
    center = func(data)
    centers = [center]
    data_inds = np.arange(data.shape[0])
    included = np.ones(data.shape[0], dtype=bool)
    for _ in range(iterations):

        # Find data point furthest from current center:
        furthest = np.argmax(abs(center - data[included]))
        included[data_inds[included][furthest]] = False

        # Recalculate center:
        center = func(data)

        # Remember current center if required:
        if full_return or threshold is not None:
            centers.append(center)

        # Evaluate convergence if early stopping is enabled:
        if criterion is not None and criterion(data, centers, **kwargs):
            break
        elif threshold is not None:
            step = abs(centers[-2] - centers[-1])
            if callable(threshold) and step < threshold(data, **kwargs):
                break
            if step < threshold:
                break
    included = np.nonzero(included)[0]
    return (included, centers) if full_return else (included, center)


def spectrogram(signal, rate, win=None, hop=None, mfft=None, log_power=False,
                nperseg=None, noverlap=None, oversampling=None,
                fmin=None, fmax=None, factor_low=None, factor_high=None,
                db_low=None, db_high=None, validate=False):
    """ Computes a spectrogram of the signal using scipy's ShortTimeFFT class.
        Convenience wrapper to the spectrogram method that preserves some of
        the arguments and functionality of scipy's older spectrogram function.

    Parameters
    ----------
    signal : 1D array of floats or ints (m,)
        Time-series data for which to compute the spectrogram.
    rate : float or int
        Sampling rate of the signal in Hz.
    win : 1D array of floats (nperseg,) or string or tuple (str, ...), optional
        Time window used in spectrogram calculation. Window size determines the
        resolution of both the time and the frequency axis (may not be longer
        than the signal). Arrays are used directly. Accepts a window specifier
        known to scipy.signal.get_window() in string or tuple format to create
        a window of a specific type with size nperseg. Defaults to a Hamming
        window if not specified. The default is None.
    hop : int, optional
        Increment in samples by which the window is shifted over the signal.
        Must be >= 1. Ignored if noverlap is specified. The default is None.
    mfft : int, optional
        Length of the FFT segment used to estimate the frequency content of the
        signal at each window. Must be >= nperseg. If mfft > nperseg, the FFT
        segment is internally padded with zeros to enhance frequency resolution
        and smoothness of the spectrogram (major computational bottleneck!).
        Ignored if oversampling is specified. If both mfft and oversampling are
        None, mfft is internally set to the window size. The default is None.
    log_power : bool, optional
        If True, rescales spectrogram to decibel relative to the maximum power.
        The default is False.
    nperseg : int, optional
        Window size in samples in the range [1, signal.size], preferably some
        power of base 2. Must be provided if given win is not already an array.
        The default is None.
    noverlap : int, optional
        Overlap in samples between consecutive windows. Must be < nperseg.
        Replaces hop if specified. The default is None.
    oversampling : float or int, optional
        Multiple of the window size by which to oversample the FFT segment.
        Must be >= 1. Replaces mfft if specified. Auto-adjusts FFT length to
        the next-larger power of 2 with integer exponent. The default is None.
    fmin : float or int, optional
        If specified, drops all frequencies < fmin. The default is None.
    fmax : float or int, optional
        If specified, drops all frequencies > fmax. The default is None.
    factor_low : float, optional
        If specified, drops lower range of frequencies where no time slice has
        power exceeding this fraction of the maximum power. Must be in [0, 1].
        Applied on linear scale and rescaled if log_power is True. Applied
        after fmin/fmax. Overrides db_low/db_high. The default is None.
    factor_high : float, optional
        If specified, drops upper range of frequencies where no time slice has
        power exceeding this fraction of the maximum power. Must be in [0, 1].
        Applied on linear scale and rescaled if log_power is True. Applied
        after fmin/fmax. Overrides db_low/db_high. The default is None.
    db_low : float or int, optional
        If specified and log_power is True, drops lower range of frequencies
        where no time slice has power exceeding this absolute threshold in dB.
        Must be <= 0. Applied after fmin/fmax. The default is None.
    db_high : float or int, optional
        If specified and log_power is True, drops upper range of frequencies
        where no time slice has power exceeding this absolute threshold in dB.
        Must be <= 0. Applied after fmin/fmax. The default is None.
    validate : bool, optional
        If True, ensures that nperseg, hop (noverlap), and mfft (oversampling)
        are accepted by silently clipping to the respective lower and/or upper
        bounds. Does not apply to win. The default is False.
        
    Returns
    -------
    freqs : 1D array of floats (n,)
        Frequency axis of the spectrogram in Hz (axis 0 of spectrum). Usually
        ranges up to the Nyquist frequency (rate / 2). If fmin and/or fmax are
        specified, both freqs and spectrum are cropped accordingly. Further
        reduced if factor_low, factor_high, db_low, or db_high are specified.
    times : 1D array of floats (p,)
        Time axis of the spectrogram in s (axis 1 of spectrum). Each time slice
        is centered in its respective window. First slice is always at time 0s.
        Last slice is set to include the last time point of the signal (may be
        slightly longer than the signal duration).
    spectrum : 2D array of floats (n, p)
        Spectrogram powers in unit ** 2 / Hz (or dB if log_power is True). 

    Raises
    ------
    ValueError
        Breaks for invalid formats of win. Further breaks if nperseg is None
        while win is not an array, or if neither hop nor noverlap are provided.
    """
    if not has_shorttimefft:
        raise ImportError('Failed to import scipy.signal.ShortTimeFFT')
    # Manage time window:
    n_samples = signal.shape[0]
    if not isinstance(win, np.ndarray):
        # Validate window size:
        if nperseg is None:
            raise ValueError('Requires nperseg if win is not an array.')
        if validate:
            # Clip window size to signal length:
            nperseg = max(1, min(nperseg, n_samples))

        # Auto-generation:
        if win is None:
            # Fallback to Hamming window:
            win = hamming(nperseg, sym=False)
        elif isinstance(win, (str, tuple)):
            # Generate from specifier with given size:
            win = get_window(win, nperseg, fftbins=True)
        else:
            msg = 'Window can be a 1D array of floats, a specifier in string '\
                  'or tuple format, or None for default Hamming window.'
            raise ValueError(msg)

    # Manage hop size:
    if noverlap is not None:
        # Convert to increment:
        hop = win.size - noverlap
    elif hop is None:
        raise ValueError('Either hop or noverlap must be specified.')
    if validate:
        # Ensure positive:
        hop = max(hop, 1)

    # Manage FFT length:
    if oversampling is not None:
        # Convert to absolute size:
        mfft = oversampling * win.size
        # Adjust to next-larger power of 2 with integer exponent:
        mfft = 2 ** int(np.ceil(np.log(mfft) / np.log(2)))
    if validate and mfft is not None:
        # Ensure at least window size:
        mfft = max(mfft, win.size)

    # Initialize general STFT for non-negative frequencies:
    FFT = ShortTimeFFT(win, hop, fs=rate, mfft=mfft, fft_mode='onesided')

    # Set last included time slice index:
    last_slice = sum(FFT.p_range(n_samples))

    # Compute spectrogram powers (squared absolute STFT):
    spectrum = FFT.spectrogram(signal, p0=0, p1=last_slice)

    # Generate time axis limited to signal extent:
    times = FFT.t(n_samples, p0=0, p1=last_slice)
    # Get frequency bins:
    freqs = FFT.f

    # Optional post-processing:
    if fmin is not None or fmax is not None:
        # Limit frequencies:
        if fmin is None:
            fmin = freqs[0]
        if fmax is None:
            fmax = freqs[-1]
        # Crop spectrogram and frequency axis:
        freq_inds = (freqs >= fmin) & (freqs <= fmax)
        freqs, spectrum = freqs[freq_inds], spectrum[freq_inds, :]
    max_power = np.max(spectrum)

    if log_power:
        # Convert to decibel:
        spectrum = 10 * np.log10(spectrum / max_power)

    range_bounds = None
    if factor_low is not None or factor_high is not None:
        # Apply power threshold relative to maximum:
        range_bounds = [factor_low, factor_high]
        # Identify range of frequency bins with sufficient power:
        for i, (factor, ind) in enumerate(zip(range_bounds, [0, -1])):
            if factor is None:
                continue
            elif factor_low == factor_high and i == 1:
                # Avoid unnecessary recomputation:
                range_bounds[i] = range_inds[ind] + 1
                continue
            # Convert to absolute threshold:
            threshold = factor * max_power
            if log_power:
                # Logarithmic rescaling:
                threshold = 10 * np.log10(threshold / max_power)
            # Get lowest or highest inclusive bin index:
            range_inds = np.nonzero(np.any(spectrum >= threshold, axis=1))[0]
            range_bounds[i] = range_inds[ind] + i
    elif log_power and (db_low is not None or db_high is not None):
        # Apply absolute power threshold (dB):
        range_bounds = [db_low, db_high]
        # Identify range of frequency bins with sufficient power:
        for i, (thresh, ind) in enumerate(zip(range_bounds, [0, -1])):
            if thresh is None:
                continue
            elif db_low == db_high and i == 1:
                # Avoid unnecessary recomputation:
                range_bounds[i] = range_inds[ind] + 1
                continue
            # Get lowest or highest inclusive bin index:
            range_inds = np.nonzero(np.any(spectrum >= thresh, axis=1))[0]
            range_bounds[i] = range_inds[ind] + i
    # Finalize power thresholding:
    if range_bounds is not None:
        # Crop spectrogram and frequency axis:
        range_inds = slice(*range_bounds)
        spectrum = spectrum[range_inds, :]
        freqs = freqs[range_inds]
    return freqs, times, spectrum


# DISTRIBUTIONS:


def multi_histogram(data, n_bins=50, bins=None, share_bins=False, density=True,
                    reduce_arrays=False):
    """ Repeatedly calls np.histogram() on each column in the data array.
        Histogram bins can be shared across columns (either a given bin array
        or generated with n_bins over the range of the flattened data if
        share_bins is True) or individually generated with n_bins over the
        range of each column. Returns 2D arrays of histogram counts, bin
        centers, and bin edges, where each column corresponds to a column in
        the data array. Centers and egdes can be returned as single 2D columns
        if the bins are shared across columns and reduce_arrays is True.  

    Parameters
    ----------
    data : 2D array (m, n) or 1D array (m,) or list of floats or ints
        Dataset to bin column-wise. Non-arrays are converted, if possible. 1D
        data is reshaped into a single 2D column (discouraged, use
        np.histogram() directly).
    n_bins : int, optional
        Number of bins passed to np.histogram(). If share_bins is True, used to
        generate a single bin array for all columns in data. Else, used to
        generate an individual bin array for each column. Ignored if bins is
        specified. The default is 50. 
    bins : 1D array or list of floats (p,), optional
        Bin edges passed to np.histogram(). Used as a single shared bin array
        for all columns in data. Overrides n_bins and share_bins if specified.
        The default is None.
    share_bins : bool, optional
        If True, uses n_bins to generate a single shared bin array for all
        columns in data. Ignored if bins is specified. The default is False.
    density : bool, optional
        Density argument passed to np.histogram(). If True, each histogram is
        normalized to a probability density. The default is True.
    reduce_arrays : bool, optional
        If True and bins are shared across columns, returns all_centers and
        all_edges as 2D columns with shape (p, 1) and (p + 1, 1), respectively.
        Else, returns all_centers and all_edges as 2D arrays with shape (p, n)
        and (p + 1, n), so that each data column has its own bin array (bins
        can still be the same). Automatically set to False if bins are not
        shared. The default is False.

    Returns
    -------
    all_hist : 2D array (p, n) of floats
        Histogram counts for each column in data (normalized if density=True).
        Comparisons between columns are only valid if either the bins are
        shared to ensure equal bin width, or if density is True. 
    all_centers : 2D array of floats (p, n) or (p, 1)
        Bin centers for each histogram in all_hist. If bins are shared and
        reduce_arrays is True, returns a single 2D column.
    all_edges : 2D array of floats (p + 1, n) or (p + 1, 1)
        Bin edges for each histogram in all_hist. If bins are shared and
        reduce_arrays is True, returns a single 2D column.
    """    
    # Input interpretation:
    if bins is not None:
        n_bins = len(bins) - 1
    elif share_bins:
        bins = np.linspace(data.min(), data.max(), n_bins + 1)
    else:
        reduce_arrays = False
    # Assert 2D array (columns):
    data = ensure_array(var=data, dims=(1, 2), shape=(-1, None))
    n_columns = data.shape[1]

    # Initialize output containers:
    all_hist = np.zeros((n_bins, n_columns))
    if reduce_arrays:
        # Return bins once for all columns in data (if bins are shared):
        all_centers = (bins[:-1] + 0.5 * (bins[1:] - bins[:-1]))[:, None]
        all_edges = bins[:, None]
    else:
        # Return bins for each column in data:
        all_centers = np.zeros((n_bins, n_columns))
        all_edges = np.zeros((n_bins + 1, n_columns))

    # Column-wise histograms:
    for i in range(n_columns):
        hist, edges = np.histogram(data[:, i], density=density,
                                   bins=n_bins if bins is None else bins)
        all_hist[:, i] = hist
        if not reduce_arrays:
            # Log column-specific bins:
            all_centers[:, i] = edges[:-1] + 0.5 * (edges[1:] - edges[:-1])
            all_edges[:, i] = edges
    return all_hist, all_centers, all_edges


def gauss_density(data, sigma=None, axis=None, samples=1000,
                  sigma_rule=None, ax=None, which='x', **kwargs):
    """ Gaussian kernel density estimate (KDE) of the distribution of data.
        Uses scipy's gaussian_kde to generate a probability density function.
        Probability density is properly normalized to integrate to 1. Suppports
        univariate and multivariate data. Distribution can be plotted as line
        for 1D data or as image for 2D data.

    Parameters
    ----------
    data : 1D array (m,) or 2D array (n, m) or list of floats or ints
        Data to estimate the density of. Non-arrays are converted, if possible.
        If 1D, assumes univariate dataset. If 2D, assumes multivariate dataset,
        where each row corresponds to a different dimension.
    sigma : float, optional
        If specified, used as kernel bandwidth (standard deviation of the
        Gaussian) for the KDE. Calculated from data according to sigma_rule if
        None. The default is None.
    axis : 1D array (p,) or 2D array (n, p) of floats, optional
        If specified, taken as the kernel axis over which to compute the KDE.
        Must be 1D if data is 1D. Must be 2D if data is 2D. Rows of the 2D axis
        correspond to the dimensions of the data, columns to grid coordinates
        of points at which to evaluate the KDE. If not specified, generated
        with samples over the range of the data (+/- a buffer of 5 * sigma).
        The default is None.
    samples : int, optional
        Number of entries to generate a kernel axis if axis is None.
        The default is 1000.
    sigma_rule : str or None, optional
        Rule of thumb to calculate the kernel bandwidth if sigma is None.
        Options are 'scott' and 'silverman' (very similar) and None for a
        rather wide kernel bandwidth. The default is None. 
    ax : matplotlib axes object, optional
        If specified, adds a plot of the KDE to the subplot. For 1D data, adds
        a line plot of the univariate distribution. For 2D data, adds an image
        of the bivariate distribution. The default is None.
    which : str, optional
        Orientation of the KDE plot if ax is specified. For 1D data, determines
        the subplot axis that corresponds to the kernel axis. For 2D data,
        determines the axis that corresponds to the first dimension. Options
        are 'x' and 'y'. The default is 'x'.
    **kwargs : dict, optional
        Additional keyword arguments passed to ax.plot() or ax.imshow().

    Returns
    -------
    pdf : nD array of floats
        Gaussian probability density estimate of the data. Returned array has
        the same number of dimensions as the dataset.
    axis : 1D array (p,) or 2D array (n, p) of floats
        Kernel axis over which the KDE was computed. Returns given axis if
        specified, else the generated axis.
    sigma : float
        Kernel bandwidth used for the KDE. Returns given sigma if specified,
        else the calculated sigma according to sigma_rule.
    """    
    # Assert 2D array (rows):
    data = ensure_array(var=data, dims=(1, 2), shape=(None, -1))
    n_dims = data.shape[0]
    n_points = data.shape[1]
    # Manage kernel bandwidth:
    if sigma is None:
        if sigma_rule == 'scott':
            sigma = n_points ** (-1 / (n_dims + 4))
        elif sigma_rule == 'silverman':
            sigma = (n_points * (n_dims + 2) / 4) ** (-1 / (n_dims + 4))
        else:
            sigma = min(100 * np.max(np.abs(data), axis=1) / n_points)
            sigma /= np.sqrt(np.square(np.std(data, axis=1, ddof=1)).sum())

    # Manage kernel axis:
    if axis is None:
        # Padded upper and lower bound per dimension:
        lower = np.min(data, axis=1) - 5 * sigma
        upper = np.max(data, axis=1) + 5 * sigma
        if n_dims == 1:
            # Simple 1D data range (row vector, later flattened):
            axis = np.linspace(lower, upper, samples, axis=1)
        else:
            bounds = (lower, upper)
            # Grid of points to cover the data range in each dimension:
            ranges = [np.linspace(mi, ma, samples) for mi, ma in zip(*bounds)]
            grids = np.meshgrid(*ranges, indexing='ij')
            # Coordinate vectors of each grid point (columns):
            axis = np.vstack([grid.ravel() for grid in grids])

    # Gaussian kernel density estimate of data over kernel axis:
    pdf = stats.gaussian_kde(data, sigma)(axis)
    # Manage output shape:
    if n_dims == 1:
        # Flatten to match pdf:
        axis = axis.ravel()
    else:
        # Reshape to match grid dimensionality (equal sides):
        pdf = np.reshape(pdf, (samples,) * data.shape[0])

    # Optional plotting:
    if ax is not None:
        # Univariate data as line:
        if n_dims == 1:
            variables = (axis, pdf)
            if which == 'y':
                variables = variables[::-1]
            ax.plot(*variables, **kwargs if kwargs else {'c': 'k', 'lw': 2})
        # Bivariate data as image:
        elif n_dims == 2:
            extend = [axis[0, :].min(), axis[0, :].max(),
                      axis[1, :].min(), axis[1, :].max()]
            if which == 'y':
                extend = extend[2:] + extend[:2]
            ax.imshow(pdf, **kwargs if kwargs else {'cmap': plt.cm.bone_r},
                      extent=extend)
    return pdf, axis, sigma


def tail_bounds(data, proportion=0.05, side='right', reduce=False):
    """ Finds the indices bounding the tail of one or several distributions.
        Calculates bi-directional cumulative integrals over each distribution
        in data, and finds the index where the integral reaches the specified 
        proportion. Can return bounds for the right, left, or both tails.

    Parameters
    ----------
    data : 2D array (m, n) or 1D array (m,) of floats or ints
        Distribution data for tail bound estimation. Can be both counts and
        probability densities. If 1D, treated as a single distribution. If 2D,
        each column is treated as a separate distribution.
    proportion : float, optional
        Proportion of the total integral held by a tail. Same for all given
        distributions and sides, if multiple. Tail bounds are defined as the
        indices where the cumulative integral from a given side is still less
        than or equal to this proportion. The default is 0.05.
    side : str, optional
        Specifies the distribution tail(s) to find bounds for. Options are
        'right', 'left', or an iterable containing both. Determines the output
        format. The default is 'right'.
    reduce : bool, optional
        If False, returns indices as a tuple of two 1D arrays (one if input
        array is 1D). This format is valid for indexing in data, producing 1D
        output. If True, returns a single 1D array of indices along the first
        axis of data, with one entry per distribution. This format is good to
        access the indices themselves. The default is False.

    Returns
    -------
    inds : 1D array (n,) of ints or tuple (2, or 1,) of 1D arrays of ints
        Index bounding the tail of each distribution in data. If reduce is
        True, returns a single 1D array of indices along the first axis of
        data, else a tuple of one or two 1D index arrays (depending on
        data.ndim). If side contains both 'right' and 'left', returns a
        dictionary with keys 'right' and 'left' holding the respective indices.
    """    
    # PDF-normalized cumulative integral over each distribution:
    from_left = cumulative_trapezoid(data, axis=0, initial=0)
    total_integral = array_slice(from_left, axis=0, start=-1, squeeze=True)
    from_left /= total_integral
    # Invert to skip integration from other side:
    from_right = total_integral - from_left

    inds = {}
    # Get bounding indices:
    if 'right' in side:
        # Check right tail integral for each distribution:
        inds['right'] = edge_along_axis(from_right <= proportion, which=0,
                                        axis=0, reduce=reduce)
    if 'left' in side:
        # Check left tail integral for each distribution:
        inds['left'] = edge_along_axis(from_left <= proportion, which=-1,
                                       axis=0, reduce=reduce)
    # Re-open dictionary if only one side is requested:
    return inds[side] if isinstance(side, str) else inds


# def noise_thresholds(percent=0.95, noise=None, paths=None, label_paths=None,
#                      config=None, bins=1000, channel=0, save=None):
#     #TODO: Docstring this shit.
#     # Input interpretation:
#     if paths is not None and config is not None:
#         if label_paths is None:
#             # Auto-fetch label files:
#             names = crop_paths(paths)
#             label_paths = [f'../data/Labels/{name}.npy' for name in names]
#         noise = []
#         for i, path in enumerate(paths):
#             print(f'Processing file {i + 1} of {len(paths)}...')
#             signal, rate = load_audio(path)
#             edges = np.load(label_paths[i])['edges']
#             if channel is None:
#                 for j in range(signal.shape[1]):
#                     data, _ = process_signal(config, returns='conv',
#                                              signal=signal[:, j], rate=rate)
#                     if j == 0:
#                         labels = restore_labels(edges, rate, data['conv'].shape[0])
#                     noise.append(data['conv'][labels == 0, :])
#             else:
#                 data, _ = process_signal(config, returns='conv', 
#                                          signal=signal[:, channel], rate=rate)
#                 labels = restore_labels(edges, rate, data['conv'].shape[0])
#                 noise.append(data['conv'][labels == 0, :])
#         noise = np.vstack(noise)
#     elif noise is None:
#         raise ValueError('Either noise or paths and config must be specified.')

#     # Compute noise distributions from data:
#     print('Computing noise distributions...')
#     hist, centers, _ = multi_histogram(noise, n_bins=bins, share_bins=True)

#     # Apply probability threshold:
#     print('Applying probability threshold...')
#     integrated = cumulative_trapezoid(hist, dx=centers[1, 0] - centers[0, 0],
#                                       axis=0, initial=0)
#     thresholds = centers[edge_along_axis(integrated >= percent, keep_wrap=True)]

#     # Optional saving:
#     if save is not None:
#         np.save(save, thresholds)
#     return thresholds


# TESTING & CHARACTERIZING NORMAL DISTRIBUTIONS:


def norm_statistics(data, axis=0, test=None):
    """ Bundles different statistics about normally distributed data.
        Returns mean, standard deviation, skewness, and kurtosis to describe
        the distribution of data. Optionally, can include statistical tests
        to check for normality of the data (Kolmogorov-Smirnov, Shapiro-Wilk)
        and to compare skewness and kurtosis of the distribution to that of a
        normal distribution. All test functions taken from scipy.stats.

    Parameters
    ----------
    data : 1D array (m,) or 2D array (m, n) of floats or ints
        Data(set) for which to compute statistics. If data is 2D, performs each
        statistic along the given axis and returns results as arrays of equal
        length (number of columns if axis is 0, else number of rows).
    axis : int, optional
        Axis of data along which to compute statistics. Passed to np.mean,
        np.std, stats.skew, stats.kurtosis, and optionally to stats.skewtest,
        stats.kurtosistest, stats.kstest, and stats.shapiro. The default is 0.
    test : str or tuple or list of str, optional
        If specified, performs the requested statistical tests and adds the
        results to the attributes dictionary. Options are
        # 'ks': Kolmogorov-Smirnov test for normality 
        -> H0: data is normally distributed
        # 'shapiro': Shapiro-Wilk test for normality
        -> H0: data is normally distributed
        # 'skew': Skewness test
        -> H0: distribution of data has skewness of a normal distribution
        # 'kurt': Kurtosis test
        -> H0: distribution of data has kurtosis of a normal distribution
        If 'all', performs all four available tests. The default is None.

    Returns
    -------
    attributes : dict
        Collection of statistics about the given data along the given axis.
        Always contains the keys 'mean', 'std', 'skew', and 'kurt'. If test is
        not None, also includes one or more of the keys 'ks', 'shapiro',
        'skew_stat', and 'kurt_stat'. If data is 2D, statistical measures are
        returned as arrays of values (one per row or column in data).
    """    
    # Descriptive statistics:
    attributes = {
        'mean': np.mean(data, axis=axis),
        'std': np.std(data, axis=axis),
        'skew': stats.skew(data, axis=axis),
        'kurt': stats.kurtosis(data, axis=axis),
    }
    # Manage statistical tests:
    if test is None:
        return attributes
    elif test == 'all':
        test = ('ks', 'shapiro', 'skew', 'kurt')
    if 'ks' in test:
        # Kolmogorov-Smirnov test:
        attributes['ks'] = stats.kstest(data, 'norm', axis=axis)
    if 'shapiro' in test:
        # Shapiro-Wilk test:
        attributes['shapiro'] = stats.shapiro(data, axis=axis)
    if 'skew' in test:
        # Skewness test:
        attributes['skew_stat'] = stats.skewtest(data, axis=axis)
    if 'kurt' in test:
        # Kurtosis test:
        attributes['kurt_stat'] = stats.kurtosistest(data, axis=axis)
    return attributes


# DIMENSIONALITY REDUCTION:


def reduce_dims(data, mode, dims, subsample=None, centered=False,
                do_import=True, transform_dict={}, **kwargs):
    """ Wrapper to sklearn's PCA, UMAP, and LDA dimensionality reduction.
        Reduces dataset to given number of dimensions using the specified mode.
        Data can be subsampled and transformed to standard z-score beforehand.

    Parameters
    ----------
    data : 2D array of floats or ints (m, n)
        Multi-dimensional dataset to reduce to given number of dimensions. The
        number of dimensions of data must be n > dims).
    mode : str
        Dimensionality reduction algorithm to use. Options are 'pca' for
        principal component analysis, 'umap' for uniform manifold approximation
        and projection, and 'lda' for linear discriminant analysis. Determines
        accepted keyword arguments passed with transform_dict and **kwargs.
    dims : int
        Number of dimensions to reduce the dataset to. Must be < data.shape[1].
    subsample : int, optional
        If specified, subsamples the dataset by taking every n-th row before
        dimensionality reduction (but after scaling to z-score). Can be used to
        reduce computational load. The default is None.
    centered : bool, optional
        If True, transforms data to standard z-scores before dimensionality
        reduction. Data is centered to zero mean and normalized by the standard
        deviation. Necessary for compatibility with different algorithms, and
        for comparison over different scales. The default is False.
    do_import : bool, optional
        If True, imports the required classes for the specified mode, as well
        as sklearn's StandardScaler if centered is True. The default is True.
    transform_dict : dict, optional
        Keyword arguments passed to the fit_transform() method of the specified
        dimensionality reduction algorithm. The default is {}.
    **kwargs : optional
        Keyword arguments passed to the constructor of the specified algorithm.
        If mode is 'umap', default is {'verbose': True, 'low_memory': True},
        else {}.

    Returns
    -------
    2D array of floats (m // subsample, dims)
        Dimensionality-reduced dataset, or a subsample thereof.
    
    Raises
    ------
    ValueError
        Breaks if mode is not 'pca', 'umap', or 'lda'.
    """
    # Input interpretation:
    if mode not in ['pca', 'umap', 'lda']:
        raise ValueError('Mode must be one of "pca", "umap", or "lda".')    
    # Manage imports:
    if do_import and centered:
        from sklearn.preprocessing import StandardScaler
    if do_import and mode == 'pca':
        from sklearn.decomposition import PCA
    elif do_import and mode == 'umap':
        import umap
    elif do_import and mode == 'lda':
        from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

    # Prepare data:
    data = ensure_array(var=data, dims=2, copy=True)
    if centered:
        # Optional normalization and centering:
        data = StandardScaler().fit_transform(data)
    if subsample is not None:
        # Optional load reduction:
        data = data[::subsample]

    # Initialize algorithm:
    if mode == 'pca':
        # Principal component analysis:
        reducer = PCA(n_components=dims, **kwargs)
    elif mode == 'umap':
        if not kwargs:
            kwargs = {
                'verbose': True,
                'low_memory': True
                }
        # Uniform manifold approximation and projection:
        reducer = umap.UMAP(n_components=dims, **kwargs)
    elif mode == 'lda':
        # Linear discriminant analysis:
        reducer = LinearDiscriminantAnalysis(n_components=dims, **kwargs)
    # Run dimensionality reduction algorithm:
    return reducer.fit_transform(data, **transform_dict)


# QUANTIFYING DIFFERENCES & OVERLAP BETWEEN DISTRIBUTIONS:


def compare_pdfs(data=None, pdf=None, axis=None, samples=1000, **kwargs):
    """ Quantifies the difference between two 1D probability density functions.
        PDFs can be provided directly or calculated from the data using
        Gaussian kernel density estimation. The returned score is the integral
        over the absolute difference between the two PDFs and ranges 
        from 0 (identical distributions) to 2 (not a single overlapping point).
        Uses scipy.stats.gaussian_kde and scipy.integrate.trapezoid.
        #TODO: Maybe histograms instead of/in addition to KDEs?

    Parameters
    ----------
    data : 2D array of floats or ints (2, m) or (m, 2), optional
        If specified, taken as dataset of two variables from which to compute
        the compared PDFs. Accepts both column and row format (assumes columns
        but can transpose row arrays with exactly 2 rows). Variables should
        roughly be on the same scale. The kernel axis for the Gaussian KDE can
        be either specified by axis or generated with samples over the range of
        the data. Takes precedence over pdf. The default is None.
    pdf : 2D array of floats or ints (2, n) or (n, 2), optional
        If specified, taken as the two PDFs to compare. Accepts both column and
        row format (same as data). Must have been computed over a shared axis,
        which must be provided as well. Must be proper densities (non-negative,
        integral of 1). Ignored if data is specified. The default is None.
    axis : 1D array of floats or ints (n,), optional
        If specified together with data, taken as the shared kernel axis over
        which to compute the two PDFs using Gausian KDE (generated with samples
        if not provided). If specified together with pdf, taken as the shared
        axis over which the two provided PDFs were computed (obligate in this
        case). The default is None.
    samples : int, optional
        Number of samples to generate a kernel axis over the range of data if
        data is specified but axis is not. The default is 1000.
    **kwargs : dict, optional
        Additional keyword arguments passed to gauss_density() for specifying
        the kernel bandwidth or plotting the PDFs. The default is {}.

    Returns
    -------
    score : float
        The integral over the absolute difference between the two PDFs along
        their shared axis. Ranges from 0 (distributions are identical at every
        point along axis) to 2 (not a single point overlap between the two
        distributions, complete separation along axis).

    Raises
    ------
    ValueError
        Breaks if pdf is provided without axis.
    ValueError
        Breaks if neither data nor pdf are provided.
    ValueError
        Breaks if given data or pdf is not a 2D array with 2 columns or rows.
    """    
    # Input interpretation:
    if data is not None:
        values = np.array(data)
    elif pdf is not None:
        values = np.array(pdf)
        # Assert obligate:
        if axis is None:
            msg = 'Passing pdf requires the underlying kernel axis, as well.'
            raise ValueError(msg)
    else:
        raise ValueError('Either data or pdf must be provided.')
    # Assert 2D array of correct shape:
    if (values.ndim == 2) and 2 in values.shape:
        values = values.T if values.shape[0] == 2 else values
    else:
        msg = 'Given data or pdf must be a 2D array with 2 columns or rows.'
        raise ValueError(msg)

    # Manage distributions:
    if data is not None:
        # Calculated:
        data = values
        if axis is None:
            # Shared kernel axis to cover whole data range:
            axis = np.linspace(data.min(), data.max(), samples)
        pdf = np.zeros((len(axis), 2))
        pdf[:, 0] = gauss_density(data[:, 0], axis=axis, **kwargs)[0]
        pdf[:, 1] = gauss_density(data[:, 1], axis=axis, **kwargs)[0]
    else:
        # Provided:
        pdf = values
    
    # Integrate distribution differences:
    difference = np.abs(pdf[:, 1] - pdf[:, 0])
    score = trapezoid(difference, axis)
    return score

    
def separability(data, labels, clusters=None, measure='auc', center='mean'):
    """ Different measures of cluster separability in an n-dimensional space.
        Finds center coordinates for each cluster and cross-wise computes the
        connecting vector between the centers of each cluster pair. Can either
        return the Euclidian distance between centers as separability measure,
        or project the n-dimensionl cluster data onto the connecting unit
        vector for other measures (Cohen's d', the area under the ROC curve
        (AUC), or the discriminant of the ROC curve). Assumes a Euclidian data
        space with continuous, roughly same-scaled variables in each dimension.

    Parameters
    ----------
    data : 2D array (m, n) or 1D array (m,) of floats or ints
        Dataset over an n-dimensional space, corresponding to the stacked data
        of at least two different clusters (total of m points). Order must
        match the labels. Accepts 1D and assumes n = 1.
    labels : 1D array of floats or ints (m,)
        Cluster labels for each data point. Order must match the data.
    clusters : tuple or list of floats or ints (p,), optional
        Label values of specific clusters to compare. Must be >= 2 clusters. If
        unspecified, uses all unique values in labels. The order of the given
        clusters determines order of returned variables. The default is None.
    measure : str, optional
        Measure of cluster separability to return. Options are
        # 'distance': Euclidian distance between cluster centers
        -> Does not require projections but cannot account for cluster spread.
        # 'cohen': Cohen's SD-corrected distance of means d'
        -> Considers spread but assumes normal distributions (center = 'mean').
        # 'auc': Area under the Receiver Operating Characteristic curve
        -> Minimal assumptions about distributions but takes additional time.
        # 'discriminant': Discriminant of the ROC curve (AUC - 0.5)
        -> Shifts AUC scores in [0, 0.5] by subtracting the chance baseline.
        The default is 'auc'.
    center : str, optional
        The method to calculate the center of each cluster. Options are 'mean'
        and 'median'. The default is 'mean'.

    Returns
    -------
    metrics : 2D array of floats (p, p)
        Matrix of separability measures between each cluster pair in the
        requested format. Index order along both axes corresponds to the order
        of the given clusters (if specified), or the order of first appearance
        of unique values in labels. For all measures, only performs comparisons
        in the upper matrix triangular and mirrors the results to the lower
        triangular. The diagonal (from top-left to bottom-right) contains self-
        comparisons and is always set 0.5 for 'auc', else 0.
    centers : 2D array of floats (p, n)
        Coordinates of cluster centers. Each row contains an n-dimensional
        vector of center coordinates relative to the origin of the data space.
    projections : dict of tuples (2,) of 1D arrays
        Scalar projections of two clusters onto the connecting unit vector for
        each performed comparison. Only computed if measure is 'cohen', 'auc',
        or 'discriminant'. Keys are strings of index pairs f'{j}{k}' to access
        specific comparisons from the metrics array. Contains only actually
        performed comparisons (upper matrix triangular). Values are tuples of
        two arrays of projected data that might vary in length, corresponding
        to a reference cluster (row index j) and a comparison cluster (column
        index k). Can be used to further process or plot the 1D distributions
        of the projected cluster.

    Raises
    ------
    ValueError
        Breaks if measure is not 'distance', 'cohen', 'auc', or 'discriminant'.
    ValueError
        Breaks if less than 2 clusters are provided by clusters or labels.
    """    
    # Input interpretation:
    if clusters is None:
        clusters = unsort_unique(labels)
    center_func = {
        'mean': np.mean,
        'median': np.median,
    }[center]
    # Validate requested method:
    if measure not in ['distance', 'cohen', 'auc', 'discriminant']:
        raise ValueError('Invalid separability measure.')
    # Validate target clusters:    
    n_clust = len(clusters)
    if n_clust < 2:
        # For single-cluster data, or scalar input clusters:
        raise ValueError('Provide at least 2 clusters of data.')
    # Assert 2D array (columns):
    data = ensure_array(var=data, dims=(1, 2), shape=(-1, None))
    n_dims = data.shape[1]

    # Coordinate vectors of cluster centers:
    centers = np.zeros((n_clust, n_dims))
    for i, cluster in enumerate(clusters):
        centers[i, :] = center_func(data[labels == cluster, :], axis=0)

    # Cross-wise separability measurements:
    metrics = np.zeros((n_clust, n_clust))
    projections = {}
    for j in range(n_clust):
        # Data points in first cluster:
        reference = labels == clusters[j]
        for k in range(j + 1, n_clust):
            # Data points in second cluster:
            comparison = labels == clusters[k]

            # Vector between both cluster centers:
            connector = centers[k, :] - centers[j, :]
            # Center distance (Euclidian vector norm):
            distance = np.linalg.norm(connector)
            if measure == 'distance':
                metrics[j, k], metrics[k, j] = distance, distance
                continue

            # Transform to unity:
            connector /= distance
            # Project each cluster on unit connector (to 1D):
            ref_proj = np.dot(data[reference, :], connector)
            comp_proj = np.dot(data[comparison, :], connector)
            projections[f'{j}{k}'] = (ref_proj, comp_proj)
            if measure == 'cohen':
                # Cohen's SD-corrected distance between scalar centers:
                ref_sd, comp_sd = np.std(ref_proj), np.std(comp_proj)
                distance /= np.sqrt(0.5 * (ref_sd**2 + comp_sd**2))
                metrics[j, k], metrics[k, j] = distance, distance
                continue

            # Prepare ROC analysis of 1D distributions:
            class_data = np.append(comp_proj, ref_proj)
            class_labels = np.zeros_like(class_data)
            class_labels[:comp_proj.size] = 1
            # Area under ROC curve of projected clusters:
            auc = roc_auc_score(class_labels, class_data)
            metrics[j, k], metrics[k, j] = auc, auc

    # Return options:
    if measure == 'distance':
        # Early return if no projections:
        return metrics, centers
    elif measure in ['auc', 'discriminant']:
        # Insert AUC baseline along diagonal (self-comparisons):
        metrics[np.arange(n_clust), np.arange(n_clust)] = 0.5
        if measure == 'discriminant':
            # Baseline-correction:
            metrics -= 0.5
    return metrics, centers, projections


# HIERARCHY OF CLUSTERS & CLASSES:


def linkage_matrix(data, method='average', metric='euclidean', reorder=True,
                   plot=True, label_cols=None, label_size=None, label_pad=None,
                   cycle_cols=None, **kwargs):
    """ Hierarchical clustering of data based on pairwise distances.
        Uses scipy.cluster.hierarchy.linkage() to establish a hierarchy among
        the given clusters. Each cluster is a vector of n scalar observations.
        Clusters as in collections of points in n-dimensional space are not
        supported directly due to the way in which the function handles the
        provided data. Input can either be equal-sized row vectors of
        observations (if data is 2D) or a pre-computed condensed distance
        matrix (if data is 1D). Returns a 4-column linkage matrix that can be
        passed to scipy.cluster.hierarchy.dendrogram() to visualize the
        computed hierarchy.

        Scipy's linkage() function performs agglomerative clustering, meaning
        that two clusters (the pair with the minimum distance) are merged into
        a single new one at each iteration. The two observation vectors are
        appended, not re-calculated as in the sense of coordinates. The new
        cluster replaces the two merged clusters in the forest of available
        clusters, and the matrix of pairwise distances is updated accordingly.
        The final result is a single cluster holding all initial observations,
        which is the root of the dendrogram. Each initial cluster corresponds
        to a leaf of the tree. Each newly created cluster is an intermediate
        node with two children and a single parent, which connects different
        branches of the tree.

    Parameters
    ----------
    data : 2D array (m, n) or 1D array (p,) of floats
        Input data for clustering. Shape determines interpretation:
        # 2D array of m observation vectors of size n.
        -> Passed to scipy.spatial.distance.pdist() with given metric
        # 1D array of p = m * (m - 1) / 2 pairwise distances between m vectors.
        -> Row-wise flattened upper triangular of a square distance matrix
        -> Custom-made or as returned by scipy's pdist() function
        -> First m - 1 pairs for cluster 1, then m - 2 pairs for cluster 2, ...
    method : str, optional
        The deployed linkage algorithm. This specifies the equation used to
        calculate pairwise cluster distances when updating the distance matrix
        after merging two clusters. Different algorithms use different
        selections of paired observations that factor into the overall cluster
        distance. Options are:
        # 'single': Nearest Point Algorithm (observation-wise minimum)
        # 'complete': Farthest Point Algorithm (observation-wise maximum)
        # 'average': Mean over distances between each possible observation pair
        # 'centroid': Distance between cluster centroids
        -> These compute distance to a new cluster based on pooled observations
        # 'weighted': Mean distance of the two merged clusters to a reference
        # 'median': Distance to mean centroid of the two merged clusters
        # 'ward': Distance by variance minimization
        -> These compute distance to a new cluster without pooling observations
        Methods 'centroid', 'median', 'ward' strictly require Euclidean metric.
        The default is 'average'.
    metric : str, optional
        The underlying distance measure for calculating distance from
        observation vectors (only if data is 2D). Ignored if data is passed as
        a 1D condensed distance matrix. See documentation of scipy's pdist()
        function for available options. The default is 'euclidean'.
    reorder : bool, optional
        If True, reorders the linkage matrix to minimize distances between
        adjacent leaves for a more intuitive tree. May be slow for large data.
        The default is True.
    plot : bool, optional
        If True, passes the computed linkage matrix to scipy's dendrogram()
        function to visualize the computed hierarchy. The default is True.
    label_cols : list of str (m,)
        If specified and plot is True, sets the background color of each leaf
        label text object to the corresponding color in the list. Order of
        colors must match the order of the passed clusters and labels. Colors
        are then rearranged to match the dendrogram leafs. Can be specified
        without providing the labels keyword argument. The default is None.
    label_size : int, optional
        If specified and plot is True, sets the font size of each leaf label
        text object to the given value in points. Can be specified without
        providing the labels keyword argument. The default is None.
    label_pad : int, optional
        If specified and plot is True, taken as padding between each leaf label
        text object and corresponding axis tick in points. Because the ticks of
        the leaf axis are not drawn, the padding is actually between the text
        and the axis border. If specified, also adjusts the horizontal or
        vertical alignment of the labels away from the axis border (depending
        on the orientation of the dendrogram). Can be specified without
        providing the labels keyword argument. The default is None.
    cycle_cols : list of str (q,), optional
        If specified and plot is True, defines the color cycler that is used to
        color different portions of sub-threshold distances in the dendrogram.
        Used in combination with the color_threshold keyword argument. This
        change is global and is resetted after plotting the dendrogram. The
        default is None.
    **kwargs : dict, optional
        Keyword arguments passed to scipy's dendrogram() if plot is True.
        Noteable option are:
        # orientation: 'top', 'bottom', 'left', or 'right'
        -> Where to position the root of the tree
        # labels: list of str
        -> Text label for each initial cluster (leafs of the tree)
        -> If not specified, uses index-based labels
        # ax: matplotlib axes object
        -> Target subplot for plotting the dendrogram
        # color_threshold: float
        -> Cumulative distance below which branches are colored differently 
        -> Separates intermediate clusters along linkage matrix [:, 2]
        -> Nodes >= threshold have above_threshold_color (default 'k')
        -> Nodes < threshold have a color from the current color cycler
        -> Set to <= 0 to color entire tree in above_threshold_color
        # above_threshold_color: str
        -> Branch color for distances above or equal to color_threshold
        -> Internal default is 'C0', function default is 'k'
        Without any kwargs, the dendrogram is plotted with all-black branches.

    Returns
    -------
    linked : 2D array of floats (m - 1, 4)
        Linkage matrix characterizing the computed hierarchy and the repeated
        merging of pairs of clusters. Each iteration of the algorithm fills a
        new row in the linkage matrix. Each column contains:
        [ind_cluster1, ind_cluster2, distance, number of pooled observations]
        In the first two columns, values < m refer to indices of initial
        clusters (in order along the first axis of 2D input data). Values >= m
        refer to new clusters (in order of their creation). For m initial
        clusters, it takes m - 1 iterations for complete merging.
    """
    # Establish cluster hierarchy:    
    linked = linkage(data, method, metric, reorder)
    if plot:
        # Manage keywords:
        if not kwargs:
            # Fallback to all-black branches (no distance thresholding):
            kwargs = {'color_threshold': 0, 'above_threshold_color': 'k'}
        elif 'above_threshold_color' not in kwargs:
            # Replace default root color ('C0'):
            kwargs['above_threshold_color'] = 'k'
        if not 'labels' in kwargs:
            # Default index-based leaf labels (not returned by dendrogram):
            kwargs['labels'] = [str(i) for i in range(linked.shape[0] + 1)]
        if not 'orientation' in kwargs:
            # Explicitly set to default: 
            kwargs['orientation'] = 'top'

        # Set custom branch color cycler:
        set_link_color_palette(cycle_cols)
        # Plot computed hierarchy:
        dendrogram(linked, **kwargs)
        # Undo (global) cycler change:
        set_link_color_palette(None)

        # Post-hoc adjustments:
        if any([l is not None for l in [label_cols, label_size, label_pad]]):
            # Retrieve target subplot (created vs. passed):
            ax = plt.gca() if 'ax' not in kwargs else kwargs['ax']
            # Determine orientation-dependent parameters:
            if kwargs['orientation'] in ['left', 'right']:
                # Leafs to the side of the tree:
                leaf_labels = ax.get_yticklabels()
                which = 'y'
                align = 'ha'
            else:
                # Leafs above or below the tree:
                leaf_labels = ax.get_xticklabels()
                which = 'x'
                align = 'va'
            # Color-code leaf labels:
            if label_cols is not None:
                for leaf in leaf_labels:
                    ind = kwargs['labels'].index(leaf.get_text())
                    leaf.set_backgroundcolor(label_cols[ind])
            # Adjust label font size:
            if label_size is not None:
                [leaf.set_fontsize(label_size) for leaf in leaf_labels]
            # Adjust leaf label padding:
            if label_pad is not None:
                direction = {'left': 'left',
                             'right': 'left',
                             'top': 'bottom',
                             'bottom': 'top'
                             }[kwargs['orientation']]
                [leaf.set(**{align:direction}) for leaf in leaf_labels]
                ax.tick_params(axis=which, pad=label_pad)
    return linked
