[![license](https://img.shields.io/pypi/l/thunderhopper.svg)](https://github.com/bendalab/thunderhopper/blob/master/LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/thunderhopper.svg)](https://pypi.python.org/pypi/thunderhopper/)
![downloads](https://img.shields.io/pypi/dm/thunderhopper.svg)
[![contributors](https://img.shields.io/github/contributors/bendalab/thunderhopper)](https://github.com/bendalab/thunderhopper/graphs/contributors)
[![commits](https://img.shields.io/github/commit-activity/m/bendalab/thunderhopper)](https://github.com/bendalab/thunderhopper/pulse)

# ThunderHopper

Model of the auditory pathway of grasshoppers.

[Documentation](https://bendalab.github.io/thunderhopper/) |
[API Reference](https://bendalab.github.io/thunderhopper/api/)


## Auditory pathway

Acoustic signals are sequentially processed along the auditory pathway:

1. Raw auditory signal (`raw`).
2. Bandpass filterd by tympanum (`filt`).
3. Computation of envelope by rectification and low-pass filtering (`env`).
4. Logarithmic transform into decibel (`log`).
5. High-pass filtering to generate intensity invariant envelope (`inv`).
6. Convolution of the envelope with a set of Gabor kerneles (`conv`).
7. Thresholding the convolved traces (`bi`).
8. Low-pass filtering the binary trace to generate slowly varying features (`feat`).

In brackets the acronyms are given that are used by output
dictionaries and for signal selection as described below.

## Usage

First, import what we need:
```py
import numpy as np
import matplotlib.pyplot as plt
from thunderhopper import configuration, process_signal, load_data
```

Second, prepare a configuration dictionary. You simply need to provide
the standard deviations of the Garbor kernels and their types. The
latter is the number of lobes you want, a negative number flips the
kernel on the x-axis:

```py
sigmas = [0.001, 0.002, 0.004, 0.008, 0.016, 0.032]
types = [1, -1, 2, -2, 3, -3, 4, -4, 5, -5,
         6, -6, 7, -7, 8, -8, 9, -9, 10, -10]
config = configuration(types=types, sigmas=sigmas)
```

Then just run the model on an audio recording:

```py
data, rates = process_signal(config, path='recording.wav')
```

That's it!

Both, `data` and `rates` are dictionaries with the same keys. `data`
contains the time series and `rates` the corresponding sampling
rates. To plot the filtered signal and the envelope of the first channel
just run

```py
filt = data['filt'][:, 0]
filt_rate = rates['filt']
tfilt = np.arange(len(filt))/filt_rate

env = data['env'][:, 0]
env_rate = rates['env']
tenv = np.arange(len(env))/env_rate

plt.plot(tfilt, filt)
plt.plot(tenv, env)
plt.show()
```

### Save model traces in file

You can also save all computed traces in a numpy npz file.
Just pass a file path to the `save` argument:

```py
process_signal(config, path=data_path, save='recording.npz')
```

Now, all the computed traces are saved in this file.

Load this file like this:

```py
data, params = load_data('recording.npz', ['filt', 'env'])
filt_rate = params['rate']
env_rate = params['env_rate']
```

The second argument requests only the filtered signal and the envelope
to be loaded from the file. When not specified, all traces are loaded.


### Configuration parameters

After calling `configuration()`, you may change some of the parameters
of the model.

For example, you can set individual thresholds for each feature by
loading them from a file and change the low-pass filter's cutoff
frequency that generates the features:

```py
config.update({
    'feat_thresh': np.load('acrididae.npy') * 0.1,
    'feat_fcut': 0.75,
    })
```

Or run the song detection on a specific input channel with a specific
threshold:

```py
config.update({
    'label_channels': 0,
    'label_thresh': 0.5
    })
```

### Select what to store

If you do not need the traces from every step of the auditory pathway,
you may select what to store via the `returns` argument. For example,
if you are only interested in the features, the norm of the features
and the song labels, call `process_signal()` like this:

```py
returns = ['feat', 'norm', 'songs']
data, rates = process_signal(config, path='recording.wav', returns=returns)
```

