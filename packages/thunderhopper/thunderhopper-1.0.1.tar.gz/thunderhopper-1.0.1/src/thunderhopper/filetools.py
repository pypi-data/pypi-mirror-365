import pathlib
import io
import zipfile
import json
import numpy as np
from audioio import load_audio, write_audio
from datetime import datetime, timedelta
from .misctools import check_list, unmerge_dicts


# GENERAL PATH & FILE MANAGEMENT:


def assert_dir(dir_path, as_path=False):
    """ Checks if folder exists and creates it, if necessary.
        Returns pathlib-standardized version of the given path as either a
        string or a pathlib.Path object.

    Parameters
    ----------
    dir_path : str or pathlib.Path object
        Relative or absolute path to folder. Creates full directory tree,
        including any missing parent folders.
    as_path : bool, optional
        If True, returns folder path as a pathlib.Path object. Else, returns a
        string. The default is False.
    """
    # Input interpretation:
    if not isinstance(dir_path, pathlib.Path):
        dir_path = pathlib.Path(dir_path)
    # Ensure folder existence:
    if not dir_path.exists():
        print(f'WARNING: Directory "{str(dir_path)}" does not exist. '\
              'Added missing folders.')
        dir_path.mkdir(parents=True)
    return dir_path if as_path else str(dir_path)


def check_extension(path, extension, n_suffixes=1):
    """ Ensures that the given path has a correct file extension.
        Controls for presence of the specified target extension(s) in path. If
        path has no extension, appends the first target extension. If path has
        a different extension, replaces it accordingly. Can handle paths
        with multiple suffixes (more than a single "." in path).

    Parameters
    ----------
    path : str
        Absolute or relative path to check. Always treated as a file path.
    extension : str or tuple or list of str
        Target extension(s) to search for in path. Returns the given path if it
        contains any target extension. Else, uses the first provided target
        extension to complete the path or replace the current extension.
    n_suffixes : int, optional
        Number of path suffixes (segments starting with ".") to treat as the
        current file extension to be checked and replaced, if necessary. If 0,
        appends the target extension to the path regardless of any existing
        suffixes. If > 1, assumes a chained extension (e.g., ".tar.gz") that
        comprises the last n_suffixes segments. Warns about paths that contain
        more suffixes than expected. The default is 1.

    Returns
    -------
    path : str
        Checked path with the correct file extension. Returns either the given
        path or a modified version with the target extension appended or in
        place of the current extension.
    """    
    # Assert iterable:
    if not isinstance(extension, (list, tuple)):
        extension = [extension] 
    # Assert leading dot in given target extension(s):
    extension = [ex if ex.startswith('.') else '.' + ex for ex in extension]

    # Get path segments with a leading dot:
    suffixes = pathlib.Path(path).suffixes
    # Take all identified:
    if n_suffixes is None:
        n_suffixes = len(suffixes)
    # Report violated expectations:
    if len(suffixes) > n_suffixes:
        print('WARNING: Path contains more suffixes (".") than expected.')

    # Append (first) target extension:
    if not suffixes or n_suffixes == 0:
        return path + extension[0]
    # Keep or replace current extension:
    current_ext = ''.join(suffixes[-n_suffixes:])
    if current_ext in extension:
        return path
    return path[:-len(current_ext)] + extension[0]


def crop_paths(paths):
    """ Crops parent folders from paths and removes any file extensions.

    Parameters
    ----------
    paths : str or list of str (m,)
        Absolute or relative paths to the desired target folders or files.

    Returns
    -------
    cropped : list of str (m,)
        Bare names of the folders and files in paths.
    """    
    # Assert iterable:
    paths = check_list(paths)
    # Reduce paths to filenames:
    cropped = [pathlib.Path(path).stem for path in paths]
    return cropped


def search_files(keywords='*', excl=[], incl=[], dir='../data/raw/', ext='*',
                 subdirs=False, resolve=True, as_path=False):
    """ Multi-keyword search among file paths in the given directory.
        Allows for post-search exclusion/inclusion criteria before returning.
        Uses pathlib's globbing, supporting path resolution and recursive
        subdirectory search.

        KEYWORD SYNTAX (current songdetector archive):
        Genus: Uppercase ('Chorthippus')
        Species: Lowercase ('_mollis')
        (Sub-species: Lowercase ('-ignifer'))
        Full name: 'Chorthippus_mollis-ignifer'
        Source: 'BM93', 'BM04', 'DJN', 'GBC', 'FTN'
        Temperature: '_T' or 'C_'
        Doubletag: 'DT' (potential duplicate segments within recording)
        Caution: 'CAUTION' (Only BM: '93/'04 might be same recording)      

    Parameters
    ----------
    keywords : str or list of str (m,)
        Search keywords for repetitive globbing of file paths. Multiple keyword
        hits do not result in duplicates in the returned file list. If any
        keyword is '*', performs an all-out wildcard search for the given file
        extension(s) in the specified directory. Excluder and includer keywords
        are applied normally, if present. The default is '*'.
    excl : str or list of str (n,), optional
        Excluder keywords. Omits all globbed paths that contain any excluders.
        Excluders are applied before and take precedence over includers. The
        default is [].
    incl : str or list of str (p,), optional
        Includer keywords. Omits all globbed paths that lack any includers.
        Includers are applied after excluders. The default is [].
    dir : str or pathlib.Path object, optional
        Relative or absolute path to the wider directory in which to perform
        the keyword search. The default is '../data/Raw/'.
    ext : str, optional
        File extension to narrow keyword search to the desired format (for
        example, 'wav'). Does not have to start with '.' The default is '*',
        corresponding to any file type.
    subdirs : bool, optional
        If True, performs recursive search in all sub-directories of dir. Else,
        strictly searches the given folder only. The default is False.
    resolve : bool, optional
        If True, converts dir to an absolute path, resolving any symbolic links
        such as '..'. Raises an error if the given directory does not exist.
        Determines the format of the returned file paths (absolute/relative).
        The default is True.
    as_path : bool, optional
        If True, returns file paths as pathlib.Path objects. Else, returns
        strings. The default is False.

    Returns
    -------
    file_list : list of str (q,)
        Paths to files that match the specified keyword criteria in
        alphabetical order. Each path in the list is unique, regardless of the
        number of matching keywords.
    """
    # Input interpretation:
    if not ext.startswith('.'):
        ext = '.' + ext
    if not isinstance(dir, pathlib.Path):
        dir = pathlib.Path(dir)
    # Assert iterables:
    keywords, excl, incl = check_list(keywords, excl, incl)
    # Enable recursive folder search:
    wild_dir = '**/' if subdirs else ''
    if resolve:
        # Make absolute, check existence:
        dir = dir.resolve(strict=True)
    if '*' in keywords:
        # Pure wildcard search:
        keywords = ['*']
    else:
        # Wildcard buffer:
        ext = '*' + ext
        wild_dir += '*'

    # Search for files that contain any search keywords:
    files = [list(dir.glob(f'{wild_dir}{kw}{ext}')) for kw in keywords]
    # Join lists, remove duplicates, sort alphabetically, Path to string:
    file_list = [str(file) for file in sorted(list(set(sum(files, []))))]
    if excl:
        # Omit all files that contain any excluder keywords:
        file_list = [f for f in file_list if not any(ex in f for ex in excl)]
    if incl:
        # Omit all files that lack any includer keywords:
        file_list = [f for f in file_list if all(inc in f for inc in incl)]
    if as_path:
        # Convert strings back to Path objects:
        file_list = [pathlib.Path(f) for f in file_list]
    return file_list


# NUMPY FILE MANAGEMENT:


def to_archive(data):
    """ Re-codes None entries as empty 1D arrays for writing to a npz archive.
        Avoids creation of arrays of data type object, which require pickling.

    Parameters
    ----------
    data : dict
        Data to be written to file using np.savez(). Other hard-to-serialize
        types like dictionaries, sets, or inhomogenous lists are not treated.

    Returns
    -------
    data : dict
        Data in storable format.
    """
    return {k: np.array([]) if v is None else v for k, v in data.items()}


def from_archive(data):
    """ Retrieves data from a npz archive, restoring much of the original form.
        Unpacks single ints, floats, bools, and strings from their 0D array
        containers. Converts empty 1D arrays back to Nones.

    Parameters
    ----------
    data : dict or NPZ archive object
        Data loaded from a npz archive using np.load(). Arrays of other
        or more complex data types like object are not treated.

    Returns
    -------
    data : dict
        Data in working format.
    """
    # Input interpreation:
    if not isinstance(data, dict):
        data = dict(data)

    # Convert arrays where necessary:
    for key, value in data.items():
        # Restore Nones from empty 1D arrays:
        if value.ndim == 1 and not value.size:
            data[key] = None
        # Restore singular entries from 0D arrays:
        elif value.ndim == 0 and value.size == 1:
            try:
                if np.isdtype(value.dtype, 'signed integer'):
                    data[key] = int(value)
                elif np.isdtype(value.dtype, 'real floating'):
                    data[key] = float(value)
                elif np.isdtype(value.dtype, 'bool'):
                    data[key] = bool(value)
                elif np.isdtype(value.dtype, np.str_):
                    data[key] = str(value)
            except AttributeError:
                # np.isdtype() was added in numpy version 2.0!
                # This might also work:
                data[key] = value.item()
    return data


def load_npz(path, files=[], keywords=[], prefix='', suffix=''):
    #TODO: Document prefix and suffix keyword arguments.
    """ Pre-loads npz archive and loads the contained npy files into memory.
        Returns a dictionary of arrays. Output can be limited to files whose
        names are explicitly given or contain any of the specified keywords.
        The archive is closed again upon retrieving the requested data.

    Parameters
    ----------
    path : str or pathlib.Path
        Absolute or relative path to the npz archive.
    files : str or list or tuple of str (m,), optional
        Selection of names of npy files to load from the archive. Ignores file
        names that cannot be found in archive.files. The default is [].
    keywords : str or list or tuple of str (n,), optional
        Keywords to match against npy file names. The default is [].

    Returns
    -------
    data : dict of arrays (p,)
        Contents of the loaded npy files retrieved from the npz archive. If no
        files or keywords are specified, returns the entire archive. Else, only
        returns the subset of files that match the given criteria.
    """    
    # Get zipped npy files:
    archive = np.load(path)

    # Load data into memory:
    if not files and not keywords:
        # Unselective early exit:
        data = dict(archive)
    else:
        # Ensure iterable:
        if isinstance(keywords, str):
            keywords = [keywords]

        # Select files to load by name or keywords:
        selected = lambda f: f in files or any(kw in f for kw in keywords)
        data = {f: archive[f] for f in filter(selected, archive.files)}

    # Safe return:
    archive.close()
    return unmerge_dicts(data, prefix, suffix) if prefix or suffix else data


# def load_npz(path, files=[], keywords=[], prefix='', suffix=''):
#     """ Pre-loads npz archive and loads the contained npy files into memory.
#         Returns a dictionary of arrays. Output can be limited to files whose
#         names are explicitly given or contain any of the specified keywords.
#         The archive is closed again upon retrieving the requested data.

#     Parameters
#     ----------
#     path : str or pathlib.Path
#         Absolute or relative path to the npz archive.
#     files : str or list or tuple of str (m,), optional
#         Selection of names of npy files to load from the archive. Ignores file
#         names that cannot be found in archive.files. The default is [].
#     keywords : str or list or tuple of str (n,), optional
#         Keywords to match against npy file names. The default is [].

#     Returns
#     -------
#     data : dict of arrays (p,)
#         Contents of the loaded npy files retrieved from the npz archive. If no
#         files or keywords are specified, returns the entire archive. Else, only
#         returns the subset of files that match the given criteria.
#     """    
#     # Get zipped npy files:
#     archive = np.load(path)

#     # Unselective early exit:
#     if not files and not keywords:
#         data = dict(archive)
#         archive.close()
#         if prefix or suffix:
#             return unmerge_dicts(data, prefix, suffix)
#         return data
    
#     # Ensure iterable:
#     if isinstance(keywords, str):
#         keywords = [keywords]

#     # Select files to load by name or keywords:
#     selected = lambda file: file in files or any(kw in file for kw in keywords)
#     data = {file: archive[file] for file in filter(selected, archive.files)}
#     archive.close()
#     return data


def expand_npz(path, **data):
    """ Appends passed variables to an existing npz archive of npy files.
        Variables must be compatible with np.save(). Each variable is first
        saved as in-memory buffer, so no extra files are created on disk apart
        from those added to the ZIP archive. Does not support file overwriting.

    Parameters
    ----------
    path : str or pathlib.Path
        Absolute or relative path to the existing npz archive.
    **data : dict
        Keyword arguments defining each variable and the name of the npy file
        to be created in the archive. Must be compatible with np.save(). May
        not contain any file names that are already present in the archive.
    """    
    for name, variable in data.items():
        # Create in-memory npy file:
        file_buffer = io.BytesIO()
        np.save(file_buffer, variable)
        # Rewind to start:
        file_buffer.seek(0)
        # Write npy file to existing npz archive:
        with zipfile.ZipFile(path, mode='a') as zipf:
            zipf.writestr(name + '.npy', file_buffer.read())
    return None


def trim_npz(path, files=[], keywords=[]):
    """ Removes specified npy files from an existing npz archive.
        Deleted files can be specified by name or by the presence of keywords.
        If any files are to be deleted, rewrites the archive without them.

    Parameters
    ----------
    path : str or pathlib.Path
        Absolute or relative path to the existing npz archive.
    files : str or list or tuple of str (m,), optional
        Selection of names of npy files to remove from the archive. Ignores
        file names that cannot be found in archive.files. The default is [].
    keywords : str or list or tuple of str (n,), optional
        Keywords to match against npy file names. The default is [].
    """    
    # Ensure iterable:
    if isinstance(keywords, str):
        keywords = [keywords]
    if isinstance(files, str):
        files = [files]

    # Select files to keep by name or keywords:
    files = [f'{file}.npy' for file in files]
    selected = lambda f: f not in files and not any(kw in f for kw in keywords)

    # List existing npy files in npz archive:
    with zipfile.ZipFile(path, mode='r') as zipf:
        archive_files = zipf.namelist()
        keep = {f: zipf.read(f) for f in filter(selected, archive_files)}

    # Check if rewrite can be avoided:
    if len(keep) == len(archive_files):
        return None
    
    # Recreate archive without deleted files:
    with zipfile.ZipFile(path, 'w') as zipf:
        for name, file in keep.items():
            zipf.writestr(name, file)
    return None


def update_npz(path, **data):
    """ Inserts passed variables to an existing npz archive of npy files.
        Variables must be compatible with np.save(). If all variables are novel
        to the archive, calls expand_npz() to append them. If any file name is
        already present in the archive, rewrites the archive without the files
        to be overwritten, then calls expand_npz() to append the new variables.

    Parameters
    ----------
    path : str or pathlib.Path
        Absolute or relative path to the existing npz archive.
    **data : dict
        Keyword arguments defining each variable and the name of the npy file
        to be inserted in the archive. Must be compatible with np.save().
    """    
    # List existing npy files in npz archive:
    with zipfile.ZipFile(path, mode='r') as zipf:
        # Get current archive contents:
        archive_files = zipf.namelist()
        # Identify archive files that will not be updated:
        untouched = [f for f in archive_files if f[:-4] not in data.keys()]
        # Check if file overwrite can be avoided:
        if len(untouched) == len(archive_files):
            # Pure append early exit:
            expand_npz(path, **data)
            return None
        # Gather contents of non-updated files:
        untouched = {f: zipf.read(f) for f in untouched}

    # Recreate archive without overwrites:
    with zipfile.ZipFile(path, 'w') as zipf:
        for name, file in untouched.items():
            zipf.writestr(name, file)
    # Append to new archive:
    expand_npz(path, **data)
    return None


# JSON SAVING & LOADING:


def write_json(data, path, make_dir=True):
    """ Writes data collection in dictionary format to .json or .txt file.

    Parameters
    ----------
    data : dict
        Data to be saved. May contain different types of data. Data is rendered
        JSON-serializable before writing: Numpy int/float scalars to built-in
        types, Numpy ndarrays (and ndarrays in a list) to lists. Conversion
        may cause loss of precision!
    path : str
        Absolute or relative path to file in which data is saved.
    make_dir : bool, optional
        If True, creates missing parent folders in path. Else, raises a
        FileNotFoundError if directory does not exist. The default is True.
    """    
    # JSON serialization:
    dictionary = data.copy()
    for key in dictionary.keys():
        value = dictionary[key]
        data_type = str(type(value))
        # Numpy integer types to built-in int:
        if 'int' in data_type and 'numpy' in data_type:                        
            dictionary.update({key: int(value)})
        # Numpy float types to built-in float:
        elif 'float' in data_type and 'numpy' in data_type:                    
            dictionary.update({key: float(value)})
        # Numpy ndarrays to list:
        elif 'ndarray' in data_type:                                           
            dictionary.update({key: value.tolist()})
        # Numpy ndarrays in list to lists:
        elif 'list' in data_type:                                              
            for i, val in enumerate(value):
                if 'ndarray' in str(type(val)):
                    value[i] = val.tolist()
            dictionary.update({key: value})
    if make_dir:
        # Optional folder creation:
        assert_dir(str(pathlib.Path(path).parent))
    # Write data to file:
    with open(path, 'w') as file:
        json.dump(dictionary, file, ensure_ascii=False, indent=4)
    return None


def load_json(path, restore=None):
    """ Loads data collection in dictionary format from .json or .txt file.

    Parameters
    ----------
    path : str
        Absolute or relative path to file in which data is stored.
    restore : str, optional
        If specified, converts stored lists back to Numpy ndarrays. If 'full',
        calls np.array() on entire list. If 'inner', leaves outer wrapper list
        as is and calls np.array() on all of its elements that are lists. Lists
        that contain any strings are always treated in the latter way. May have
        unexpected outcomes for higher levels of nesting! The default is None.

    Returns
    -------
    data : dict
        Dictionary containing loaded data.
    """    
    # Read data from file:
    with open(path, 'r') as file:
        data = json.load(file)
    if restore in ['full', 'inner']:
        # Revert array JSON serialization:
        for key in data.keys():
            value = data[key]
            # Skip scalars and strings:
            if type(value) is not list:
                continue
            # Check data type of list elements:
            types = [type(val) for val in value]
            if restore == 'inner' or (str in types):
                # Inner lists to arrays:
                for i, val in enumerate(value):
                    if type(val) is list:
                        value[i] = np.array(val)
                data.update({key: value})
            else:
                # Entire list to array:
                data.update({key: np.array(value)})
    return data


# AUDIO FILE HANDLING:


def merge_wavs(file_paths, save_path=None, return_out=False):
    """ Loads and concatenates audio recording data from multiple .wav files.
        Merged data can be written to a new .wav file and/or returned directly.
        Wrapper to audioio's load_audio() and write_audio() functions. 

    Parameters
    ----------
    file_paths : list or tuple (m,) of str
        Collection of paths to several .wav files for merging. Recording data
        must have the same sampling rate and channel count. Arrays are stacked
        vertically along the time axis in order of the input list, so that data
        from the first file is on top.
    save_path : str, optional
        If specified, writes the merged recording data to a new .wav file at
        the given path. The default is None.
    return_out : bool, optional
        If True, returns the merged recording data as a numpy array together
        with the underlying sampling rate in Hz as float. Auto-enabled if
        save_path is not specified. The default is False.

    Returns
    -------
    merged : 2D array of floats (n, p)
        Merged recording data from all input files. Rows correspond to time,
        columns to individual channels. Only returned if return_out is True or
        save_path is None.
    rate : float
        Sampling rate of the merged recording data in Hz. Only returned if
        return_out is True or save_path is None.

    Raises
    ------
    ValueError
        Breaks if any input file has a different sampling rate than the others.
        Breals without dedicated error if channel count differs between files.
    """    
    # Load recording data from audio files:
    signals, rates = zip(*[load_audio(str(path)) for path in file_paths])
    if len(set(rates)) > 1:
        # Validate sampling rate consistency:
        raise ValueError('All recordings must have the same sampling rate.')

    # Merge recording list:
    merged = np.vstack(signals)
    if save_path is not None:
        # Optional saving to new audio file:
        write_audio(save_path, merged, rates[0])
    if return_out or save_path is None:
        # Optional outputting:
        return merged, rates[0]
    return None


def merge_wav_series(rec_dur=20., unit='seconds', format='%Y%m%dT%H%M%S',
                     n_tag=15, save_dir=None, return_out=False,
                     return_paths=False, **search_kwargs):
    """ Automatic identification and merging of consecutive audio recordings.
        Uses search_files() to fetch all .wav files in the target directory
        that match the given search criteria, then extracts the time stamp from
        the end of each file name. Recordings whose start times are separated
        by an interval matching the specified duration are appended into a
        series and written to a new .wav file. Can return the merged recording
        data and/or a dictionary of paths to the new files and the merged ones.

    Parameters
    ----------
    rec_dur : float, optional
        Standard recording duration in the given unit. Must be the same for all
        files in a series for correct identification. The default is 20.0.
    unit : str, optional
        Unit of the recording duration. Must be known to datetime's timedelta
        class. The default is 'seconds'. 
    format : str, optional
        Standard time stamp format used in all file names. Must be readable by
        datetime's strptime/strftime functions. Newly created files are tagged
        in the same format. May contain non-coding letters (no leading "%"),
        which are inherited by the time stamps of new files. The default is
        '%Y%m%dT%H%M%S', so 19980330T102700 for March 30th 1998 at 10:27 am.
    n_tag : int, optional
        Number of characters occupied by the time stamp at the end of each file
        name. This is not the same as the length of the format string! The
        default is 15, matching the default format.
    save_dir : str or pathlib.Path object, optional
        Path to the folder where the merged recording data should be written to
        file. If None, saves into sub-folder "merged" in the target directory.
        The directory is created if missing in both cases. The default is None. 
    return_out : bool, optional
        If True, returns a list of tuples containing the merged recording data
        and the corresponding sampling rate per series. If both return options
        are True, returns a tuple (data, paths). The default is False.
    return_paths : bool, optional
        If True, returns a dictionary of the paths to the new .wav files (keys)
        and lists of paths to the merged original files (values) for reference.
        If both return options are True, returns a tuple (data, paths). The
        default is False.
    **search_kwargs : dict
        Keyword arguments passed to search_files() for specifying the search
        criteria when fetching .wav files. Use 'dir' to set the target
        directory (default is current directory). Use 'keywords', 'incl', and
        'excl' to filter by file name (default is any .wav file). Forces 'ext'
        to 'wav' and 'as_path' to True. The default is {}.

    Returns
    -------
    merge_data : list (m,) of tuples (2,) of 2D array (n, p) and float
        For each identified recording series, the merged recording data from
        all matching .wav files as a numpy array and the corresponding sampling
        rate in Hz as float. Rows correspond to time, columns to individual
        channels. Only returned if return_out is True.
    merge_files : dict
        For each identified recording series, the path to the newly created
        .wav file in the given storage folder (keys) and a list of paths to the
        original .wav files that have been merged (values). All paths are 
        returned as pathlib.Path object. Only returned if return_paths is True.
    """    
    # Enforce function-specific default search settings:
    search_kwargs.update({'ext': 'wav', 'as_path': True})
    # Optional default settings:
    if 'dir' not in search_kwargs:
        search_kwargs['dir'] = '.'
    if 'resolve' not in search_kwargs:
        search_kwargs['resolve'] = False

    # Fetch all matching .wav files:
    paths = search_files(**search_kwargs)
    if not paths:
        # Early exit for unsuccessful file search in target directory:
        print('WARNING: No .wav files found matching the search criteria.')
        return None

    # Extract time stamp from end of file names and convert to precise times:
    times = [datetime.strptime(path.stem[-n_tag:], format) for path in paths]
    delta = timedelta(**{unit: rec_dur})
    # Sort start times chronologically:
    sorted_inds = np.argsort(times)
    times, paths = np.array(times)[sorted_inds], np.array(paths)[sorted_inds]
    # Match start-to-start intervals against standard recording duration:
    break_inds = np.nonzero(np.append(np.diff(times) != delta, True))[0]

    # Identify and extract recording series:
    series_paths, series_times, start_ind = [], [], 0
    for end_ind in break_inds:
        if end_ind - start_ind:
            # Series must contain at least two consecutive recordings:
            series_paths.append(paths[start_ind : end_ind + 1].tolist())
            series_times.append(times[start_ind : end_ind + 1].tolist())
        start_ind = end_ind + 1
    if not series_paths:
        # Early exit for failure to identify any recording series:
        print('WARNING: No recording series found among the given .wav files.'\
              '\nA series must contain at least two recordings with a time'\
              f'stamp interval of {rec_dur} {unit}.')
        return None

    # Prepare storage:
    if save_dir is None:
        # Default to sub-folder "merged" in target directory:
        save_dir = pathlib.Path(search_kwargs['dir']) / 'merged'
    # Ensure folder existence (given or default):
    save_dir = assert_dir(save_dir, as_path=True)

    # Merge each recording series:
    merge_data, merge_files = [], {}
    for series, start_times in zip(series_paths, series_times):
        # Adapt series time stamp (full duration):
        t_start = start_times[0].strftime(format)
        t_end = (start_times[-1] + delta).strftime(format)
        # Assemble path to save new .wav file into storage folder:
        name = pathlib.Path(series[0]).stem[:-n_tag] + f'{t_start}-{t_end}.wav'
        name = str(save_dir / name)
        # Merge recording data and write array to file:
        out = merge_wavs(series, name, return_out=return_out)
        # Log signal and rate:
        merge_data.append(out)
        # Log new and merged files:
        merge_files[name] = series

    # Return options:
    if return_out and return_paths:
        return (merge_data, merge_files)
    elif return_out:
        return merge_data
    elif return_paths:
        return merge_files
    return None


# SONGDETECTOR-SPECIFIC FUNCTIONS:


def species_collection():
    """ Shortcut to retrieve the current species scope of the songdetector.
        Add or remove species to modify model scope.

    Returns
    -------
    species_list : list of str (m,)
        Species names in alphabetical order.
    """
    species_list = ["Arcyptera_fusca",
                    "Chorthippus_albomarginatus",
                    "Chorthippus_apricarius",
                    "Chorthippus_biguttulus",
                    "Chorthippus_bornhalmi",
                    "Chorthippus_brunneus",
                    "Chorthippus_dorsatus",
                    "Chorthippus_mollis",
                    "Chorthippus_pullus",
                    "Chorthippus_vagans",
                    "Chrysochraon_dispar",
                    "Euthystira_brachyptera",
                    "Gomphocerippus_rufus",
                    "Gomphocerus_sibiricus",
                    "Omocestus_haemorrhoidalis",
                    "Omocestus_rufipes",
                    "Omocestus_viridulus",
                    "Pseudochorthippus_montanus",
                    "Pseudochorthippus_parallelus",
                    "Sphingonotus_caerulans",
                    "Stauroderus_scalaris",
                    "Stenobothrus_lineatus",
                    "Stenobothrus_nigromaculatus",
                    "Stenobothrus_rubicundulus",
                    "Stenobothrus_stigmaticus",
                    "Stethophyma_grossum"]
    return species_list


def genus_collection():
    """ Retrieves each unique genus in the current species_collection().

    Returns
    -------
    list of str (m,)
        Genus names in alphabetical order.
    """
    genus_list = [spec.split('_')[0] for spec in species_collection()]
    return list(np.unique(genus_list))


def extract_species(paths, omit_noise=True, omit_subspec=True,
                    pretty_format=False, short_genus=False, tex_it=False):
    """ Extracts unique species names from a collection of file paths.
        Filenames must start with species names in the format "Genus_species_*"
        or "Genus_species-subspecies_*". Remainders of filenames are ignored.

    Parameters
    ----------
    paths : str or list of str (m,)
        Paths to files whose name contains a species name.
    omit_noise : bool, optional
        If True, skips any filename that contains the word "noise". The default
        is True.
    omit_subspec : bool, optional
        If True, removes sub-species designations from species names. The
        default is True.
    pretty_format : bool, optional
        If True, replaces original separators ('_', '-') with whitespace for
        pretty printing. This behavior also applies if short_genus or tex_it
        are True, regardless of pretty_format. The default is False.
    short_genus : bool, optional
        If True, abbreviates genus designations to their first letter and uses
        whitespace as separators. The default is False.
    tex_it : bool, optional
        If True, formats species names to Latex italic font and uses whitespace
        as separators. The default is False.

    Returns
    -------
    species_list : list of str (n,)
        Formatted unique species names in the given collection of file paths. 
    """    
    # Set up separators for different formatting styles:
    sep = [' ', ' '] if pretty_format or short_genus or tex_it else ['_', '-']
    # Extract filenames from paths:
    paths = crop_paths(paths)
    species_list = []
    for path in paths:
        # Skip over noise files:
        if omit_noise and 'noise' in path:
            continue
        # Split filename into segments:
        path_segments = path.split('_')
        if omit_subspec:
            # Remove sub-species designation:
            species_segment = path_segments[1].split('-')[0]
        else:
            # Keep sub-species with desired separator:
            species_segment = path_segments[1].replace('-', sep[1])
        if short_genus:
            # Abbreviate genus designation:
            name = path_segments[0][0] + '.' + sep[0] + species_segment
        else:
            # Keep full genus with desired separator:
            name = path_segments[0] + sep[0] + species_segment
        if name not in species_list:
            # Add novel species:
            species_list.append(name)
    if tex_it:
        # Format species names in italic LaTeX font:
        species_list = [f'\\textit{{{species}}}' for species in species_list]
    return species_list


def count_files(paths, spec_list=None, as_array=False, **kwargs):
    """ Counts the occurrences of target species in a collection of file paths.
        Format of species names must be consistent between paths and spec_list.

    Parameters
    ----------
    paths : str or list of str (m,)
        Paths to files whose name contains a species name. The name of one
        species must follow the same format across paths to avoid miscounts.
    spec_list : str or list of str (n,), optional
        Species names to search for in paths. If None, uses extract_species()
        to retrieve all unique species names from paths. The default is None.
    as_array : bool, optional
        If True, returns file counts as Numpy array (in order of spec_list).
        Else, returns a dictionary with species names as keys for readability
        and saving. The default is False.
    **kwargs : dict, optional
        Keyword arguments passed to extract_species() if spec_list is None.
        Can be used to format dictionary keys or to treat sub-species as
        separate categories during counting.

    Returns
    -------
    file_count : dict or 1D array of ints (n,)
        Counts of files containing each target species in the specified format.
    """    
    if spec_list is None:
        # Auto-generate target species:
        spec_list = extract_species(paths, **kwargs)
    # Assert iterable:
    spec_list = check_list(spec_list)
    # Count occurrences of each species:
    file_count = np.zeros(len(spec_list), dtype=int) if as_array else {}
    for i, species in enumerate(spec_list):
        species_count = np.sum([species in path for path in paths])
        file_count[i if as_array else species] = species_count
    return file_count


# SONGDETECTOR CORE FUNCTIONALITY:


def create_subsets(paths, amount_train, spec_list=None):
    """ Splits a collection of file paths into a training and a test subsets.
        Randomly assigns the given amount of species-specific files to the
        training set and any remainders to the test set. Format of species
        names must be consistent between paths and spec_list.

    Parameters
    ----------
    paths : list of str (m,)
        Paths to files from which to create subsets. Each filename must
        contain a species name to identify species-specific files.
    amount_train : int or float
        If int, the absolute number of training files per species. 
        If float, the proportion of training files per species (ensures at
        least one file per species). Training takes precedence over testing, so
        that there may be no files left for the test set if too many training
        files are requested.
    spec_list : str or list of str (n,), optional
        Species to consider in file collection when creating subsets. If None,
        uses extract_species() to retrieve all unique species names from paths.
        The default is None.

    Returns
    -------
    train_subset : list of str (p,)
        Randomly assigned species-specific training files.
    test_subset : list of str (q,)
        Remaining species-specific test files.
    """    
    if spec_list is None:
        # Auto-generate target species:
        spec_list = extract_species(paths)
    train_subset = []
    test_subset = []
    # Assemble file subsets:
    for species in spec_list:
        # Get species-specific files:
        species_files = [file for file in paths if species in file]
        n_files = len(species_files)
        if isinstance(amount_train, int):
            # Absolute number of training files (not more than available):
            n_train = amount_train if amount_train < n_files else n_files
        elif isinstance(amount_train, float):
            # Proportion of training files (at least one):
            n_train = np.max([int(np.round(n_files*amount_train)), 1])
        # Shuffle and split:
        np.random.shuffle(species_files)
        train_subset += species_files[:n_train]
        test_subset += species_files[n_train:]
    return train_subset, test_subset


def file_subsets(learn_files, nolearn_files, amount_train, verbose=None):
    """ Wraps create_subsets() to split both learn and nolearn file collection.
        Learn files contain data that the model should learn to recognize.
        Nolearn files contain data that the model should learn to avoid.
        Both are split into training and test subsets.

    Parameters
    ----------
    learn_files : list of str (m,)
        Paths to files that contain desired learn data. Each filename must
        contain a species name to identify species-specific files.
    nolearn_files : list of str (n,)
        Paths to files that contain desired nolearn data. Each filename must
        contain a species name to identify species-specific files.
    amount_train : int or float
        If int, the absolute number of training files per species. 
        If float, the proportion of training files per species (ensures at
        least one file per species). Training takes precedence over testing, so
        that there may be no files left for the test set if too many training
        files are requested.
    verbose : str, optional
        If 'short', prints summary of file and species counts for each subset.
        If 'full', prints additional metadata for each subset: Doubletag (file
        may contain duplicate segments), Caution (file may not be unique), 
        Temp (file has some temperature information). The default is None.

    Returns
    -------
    learn_train : list of str (p,)
        Randomly assigned species-specific training files (learn data).
    nolearn_train : list of str (q,)
        Randomly assigned species-specific training files (nolearn data).
    test_files : list of str (r,)
        Remaining species-specific test files (both learn and nolearn data).
    """    
    # Create separate subsets for learn and nolearn data:
    learn_train, learn_test = create_subsets(learn_files, amount_train)
    nolearn_train, nolearn_test = create_subsets(nolearn_files, amount_train)
    test_files = learn_test + nolearn_test
    # Optional feedback:
    if verbose in ['short', 'full']:
        # Count included files:
        n_all = len(learn_files) + len(nolearn_files)
        n_learn = len(learn_train)
        n_nolearn = len(nolearn_train)
        n_test = len(test_files)
        # Count included species:
        learn_species = len(extract_species(learn_train))
        nolearn_species = len(extract_species(nolearn_train))
        test_species = len(extract_species(test_files))
        all_species = learn_species + nolearn_species
        # Print short summary:
        print(f'\nfetched {n_all} files / {all_species} species'\
              f'\nlearn: {n_learn} / {learn_species}'\
              f'\nnolearn: {n_nolearn} / {nolearn_species}'\
              f'\ntest: {n_test} / {test_species}\n')
        if verbose == 'full':
            # Gather additional metadata per subset:
            subsets = [learn_train, nolearn_train, test_files]
            strings = ['learn:', 'nolearn:', 'test:']
            print('files with special tags:')
            for subset, string in zip(subsets, strings):
                # Count and print occurences of file tags:
                n_dt = len([f for f in subset if 'DT' in f])
                n_caution = len([f for f in subset if 'CAUTION' in f])
                n_temp = len([f for f in subset if '_T' in f])
                print(f'{string} doubletag: {n_dt}, caution: {n_caution}, '\
                      f'temp: {n_temp}')
    return learn_train, nolearn_train, test_files


def organize_files(target, amount_train, auto_complete=False, verbose=None,
                   **kwargs):
    """ Top-level file search and creation of training and test subsets.
        Finds target among pre-defined species scopes and fetches corresponding
        files to be split into subsets. Target species determines learn files
        (data that the model should learn to recognize), other species in the
        scope determine nolearn files (data that the model should learn to
        avoid). Currently available scopes are grasshoppers, frogs, frog
        courtship calls, and frog territorial calls.

    Parameters
    ----------
    target : str or list of str (m,)
        Target species that determine selection of learn files. Must be in the
        format "Genus_species" or "Genus_species_calltype". Returns with a 
        warning if no known scope is found for the target. If 'grasshoppers',
        'frogs', 'frogs_courtship', or 'frogs_territorial', returns early with
        all files and species in this scope.
    amount_train : int or float
        Amount of training files for creation of training and test subsets.
        If int, the absolute number of training files per species. 
        If float, the proportion of training files per species (ensures at
        least one file per species). Training takes precedence over testing, so
        that there may be no files left for the test set if too many training
        files are requested.
    auto_complete : bool, optional
        If True, automatically completes target species if it is a substring of
        grasshopper and frog species (no calltype distinction). Allows passing
        of targets in the format "species" without returning a warning. May
        result in multiple potentially conflicting target species. The default
        is False.
    verbose : str, optional
        If 'short', prints summary of file and species counts for each subset.
        If 'full', prints additional metadata for each subset: Doubletag (file
        may contain duplicate segments), Caution (file may not be unique), 
        Temp (file has some temperature information). The default is None.
    **kwargs : dict, optional
        Keyword arguments passed to search_files() when fetching learn/nolearn
        files, or when returning with a shortcut. Can be used to specify a
        custom directory and file extension for the file search.

    Returns
    -------
    file_bundle : list (3,) of lists of str
        Paths to subset files in the order [learn, nolearn, test]. Some entries
        may be empty if no files are found in the given directory, or if too
        many training files are requested. If target is a shortcut string,
        returns a flat list of all files in the corresponding scope.
    species_bundle : list (3,) of lists of str
        Species names corresponding to file_bundle in the same order. If target
        is a shortcut string, returns a flat list of all species in the
        corresponding scope.
    """    
    # Available species scopes:
    grasshoppers = species_collection()
    frogs = ['Rana_esculenta', 'Rana_lessonae', 'Rana_ridibunda']
    frogs_courtship = [frog + '_courtship' for frog in frogs]
    frogs_territorial = [frog + '_territorial' for frog in frogs]
    all_species = grasshoppers + frogs

    if auto_complete:
        # Auto-complete target species:
        target = [spec for spec in all_species if target in spec]
    # Determine desired scope and handle shortcuts:
    if any(np.isin(grasshoppers + ['grasshoppers'], target)):
        species = grasshoppers
        # Fetch all grasshopper files:
        if target == 'grasshoppers':
            return search_files(grasshoppers, **kwargs), species
    elif any(np.isin(frogs + ['frogs'], target)):
        species = frogs
        # Fetch all frog files:
        if target == 'frogs':
            return search_files(frogs, **kwargs), species
    elif any(np.isin(frogs_courtship + ['frogs_courtship'], target)):
        species = frogs_courtship
        # Fetch all files with frog courtship calls:
        if target == 'frogs_courtship':
            return search_files(frogs_courtship, **kwargs), species
    elif any(np.isin(frogs_territorial + ['frogs_territorial'], target)):
        species = frogs_territorial
        # Fetch all files with frog territorial calls:
        if target == 'frogs_territorial':
            return search_files(frogs_territorial, **kwargs), species
    else:
        print(f'WARNING: No known model scope for target {target}.')
        return None, None
    # Assert iterable:
    target = check_list(target)
    # Fetch learn files (target species):
    learn = search_files(target, **kwargs)
    # Fetch nolearn files (non-target species):
    others = [spec for spec in species if not (spec in target)]
    nolearn = search_files(others, **kwargs)
    # Assemble training and test subsets:
    file_bundle = list(file_subsets(learn, nolearn, amount_train, verbose))
    species_bundle = [target, others, extract_species(file_bundle[2])]
    return file_bundle, species_bundle

