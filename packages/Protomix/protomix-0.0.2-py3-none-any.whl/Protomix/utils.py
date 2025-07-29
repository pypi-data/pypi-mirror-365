import os
import glob

from typing import Tuple, Union
from scipy.integrate import trapezoid
import numpy as np
import logging

def get_paths(root_directory: str, filename: str) -> list:
    """
    Retrieve all paths matching the specified filename within the root directory and its subdirectories.

    This function performs a recursive search, starting from the given root directory, to find all files 
    that match the specified filename. It returns a list of full paths to these files.

    :param root_directory: The starting directory from which the search begins.
    :type root_directory: str
    :param filename: The name of the file to search for.
    :type filename: str
    
    :return: A list of full paths to the files matching the specified filename. If no files are found, returns an empty list.
    :rtype: list

    :note: This function performs a recursive search, so it will also look in all subdirectories of the root directory.
    """
    
    # Assertive checks for input parameters
    assert isinstance(root_directory, str), "Expected 'root_directory' to be a string."
    assert isinstance(filename, str), "Expected 'filename' to be a string."
    assert root_directory, "'root_directory' should not be an empty string."
    assert filename, "'filename' should not be an empty string."
    assert os.path.isdir(root_directory), f"'{root_directory}' is not a valid directory."
    
    # Construct the search pattern using os.path.join to ensure platform-independent behavior.
    # '**' allows for recursive search in all subdirectories, and the filename is what we're looking for.
    search_pattern = os.path.join(root_directory, '**', filename)
    
    # Use glob with recursive=True to find all matching paths.
    paths = glob.glob(search_pattern, recursive=True)
    
    return paths

def get_index_signal_with_highest_correlation(signals: np.ndarray) -> Tuple[int, np.ndarray]:
    if np.any(np.isnan(signals)):
        # make a local copy of the signals cause we need to interpolate potential NaN's
        signals = signals.copy()
        signals = interpolate_nan(signals)
    # correlation matrix
    corr_matrix = np.corrcoef(signals)
    # return index of the max of sum over each row and signals
    idx = np.argmax(np.sum(corr_matrix, axis=1))
    return idx, signals[idx].copy()

def get_avg2_target(signals: np.ndarray, avg2factor: int) -> np.ndarray:
    if isinstance(signals, np.ndarray) and isinstance(avg2factor, int):
        if signals.ndim == 2:
            if signals.shape[0] <= 1:
                logging.warning('Sure you want to calculate the average of just one signal?')
            tmp_avg = np.nanmean(signals, axis=0)
            baseline_correction = np.min(tmp_avg) if np.min(tmp_avg) > 0 else 0
            return np.multiply((tmp_avg - baseline_correction), avg2factor)
        else:
            raise ValueError('signals dimension not 2')
    else:
        raise ValueError('Wrong input types')

def get_max_signal_idx(signals, signal_axis=1):
    if isinstance(signals, np.ndarray) and isinstance(signal_axis, int):
        if signals.ndim == 2 and signal_axis < signals.ndim:
            return np.argmax(np.sum(signals, axis=signal_axis))
        else:
            raise ValueError('signals dimension not 2 or signal_axis bigger than signals dimension')
    else:
        raise ValueError('Wrong input types')

def interpolate_nan(signals):
    if signals.ndim == 1:
        logging.debug('signal size and signal' + str(signals.size) + str(signals))
        x = np.arange(signals.size)
        mask = np.isfinite(signals)
        return np.interp(x, x[mask], signals[mask])
    elif signals.ndim == 2:
        nan_free_signals = []
        #for signal in list(signals):
        for signal in signals:
            logging.debug('signal size and signal'+str(signal.size)+str(signal))
            x = np.arange(signal.size)
            mask = np.isfinite(signal)
            nan_free_signals.append(np.interp(x, x[mask], signal[mask]))
        return np.array(nan_free_signals)
    else:
        raise ValueError('Max 2 dimensional numpy.ndarrays allowed')

def get_fill_matrix(signals: np.ndarray, fill_type: str) -> np.ndarray:
    """
    Generate a fill matrix for signal processing based on the specified fill type.

    This function creates a matrix used to fill or adjust signals according to the specified method.
    The fill matrix can be used in signal processing tasks, such as zero-filling or padding signals 
    to a desired length.

    :param signals: A 2D numpy array where each row represents a signal, and columns represent data points within the signal.
    :type signals: np.ndarray
    :param fill_type: The type of fill operation to perform. Options might include methods like 'zero', 'mean', or 'edge'.
    :type fill_type: str
    
    :return: A numpy array representing the fill matrix, with the same shape as the input signals array.
    :rtype: np.ndarray
    """

    if isinstance(signals, np.ndarray) and isinstance(fill_type, str):
        if signals.ndim != 2 and fill_type.lower() not in ['nan', 'zero', 'adjacent']:
            raise ValueError('Invalid input')
    if fill_type.lower() == 'nan':
        fill = np.tile(np.nan, (signals.shape[0], 2))
        logging.info('Using fill with numpy.nan')
    elif fill_type.lower() == 'adjacent':
        fill = signals[:, [0, signals.shape[1]-1]]
    else:
        fill = np.zeros((signals.shape[0], 2))
    return fill

def shift_signals(signals: np.ndarray, shifts: np.ndarray, fill: Union[np.ndarray, str]) -> np.ndarray:
    """
    Shift all signals according to the provided shifts.

    :param signals: A 2D numpy.ndarray of shape (m, n) where each row represents a signal of length n.
    :type signals: np.ndarray
    :param shifts: A 1D numpy.ndarray of length m containing the shift values for each signal.
                   Positive values shift to the left.
    :type shifts: np.ndarray
    :param fill: Fill values to use during signal shifting. Defaults to numpy.nan.
                Can be one of the following:
                - A 2D numpy.ndarray of shape (m, 2), where the first column specifies the left fill values
                and the second column specifies the right fill values.
                - A string 'adjacent' to fill with copies of neighboring values.
    :type fill: Union[np.ndarray, str]
    
    :return: A 2D numpy.ndarray of shape (m, n) containing the shifted signals.
    :rtype: np.ndarray
    """

    # check inputs
    logging.debug('start input checks')
    if all([isinstance(x, np.ndarray) for x in [signals, shifts, fill]]):
        if signals.ndim != 2 or shifts.ndim != 1 or fill.ndim != 2 or fill.shape[1] != 2:
            raise ValueError('Invalid dimensions of one/all inputs')
        elif signals.shape[0] != shifts.shape[0] or signals.shape[0] != fill.shape[0]:
            raise ValueError('number of signals and number of shifts/fills do not match')
    else:
        raise ValueError('signals and shifts have to be of type numpy.ndarray')

    logging.debug('input check done - all good')

    # shift signals by using numpy.pad and slice to original size
    # TODO: to speed up parallel execution try to use only numpy functions / does not work with pas as we have different
    # TODO: shifts per row
    shifted_signals = []
    # for shift, signal, f in zip(list(shifts), list(signals), list(fill)):
    for shift, signal, f in zip(shifts, signals, fill):
        logging.debug('running shift (shift, fill, signal): %s %s %s' % (str(shift), str(f), str(signal)))
        if shift > 0:
            shifted_signals.append(np.pad(signal, (0, shift), 'constant', constant_values=(f[1]))[shift:])
        elif shift < 0:
            shifted_signals.append(np.pad(signal, (abs(shift), 0), 'constant', constant_values=(f[0]))[:shift])
        else:
            shifted_signals.append(signal)
    logging.debug('shifted signal: %s' % str(np.array(shifted_signals)))
    return np.array(shifted_signals)

def ccfftshift(target: np.ndarray,
               signals: np.ndarray,
               lower_bound: int=None,
               upper_bound: int=None,
               interpolate=True) -> Tuple[np.ndarray, np.ndarray]:
    """
    This function calculates the shift within the given bounds for each input signal to align optimally with the target
    using FFT. Loosly based on Giorgio Tomasi's implementation for icoshift

    :param target: 1 x n datapoints numpy.ndarray
    :param signals: m x n datapoints numpy.ndarray
    :param lower_bound: integer - lower bound max shift
    :param upper_bound: integer - upper bound max shift
    :param interpolate: bool - if True linear interpolate missing values prior FFT / False will lead to problems in
                        current implementation
    :return: tuple(shifts: 1D numpy.ndarray of length m,
                   costs: 2-D numpy.ndarray shift_range_length x m+1 - first row shift range)
    """
    # TimeDim
    shift_axis = 1

    # check input signals and target - currently max 2D signals, 1D target
    if isinstance(target, np.ndarray) and isinstance(signals, np.ndarray):
        if target.ndim != 1 or signals.ndim != 2:
            raise ValueError('Target has to be a 1-dim and signals a 2-dim numpy.ndarray')
        else:
            if target.shape[0] != signals.shape[1]:
                raise ValueError('target length and signal length (2nd axis) not equal')
            else:
                # create copy of input target / signals to guarantee that the original data does not get modified
                # as most numpy functions create copies and do not modify the original object it might be overkill,
                # but as python has no const input / pass by value I want to be sure
                # garbage collection should prevent mem leak - because the created copies are only used inside this
                # function
                signals = signals.copy()
                target = target.copy()
                logging.debug('Created copies of inputs signals and target - should not create mem leak')
                # mP, nP = nT
                n_signals, signal_length = signals.shape
    else:
        raise ValueError('Target and signals have to be numpy.ndarrays')

    # default options and checks
    if lower_bound is None:
        lower_bound = -1 * int(signal_length * 0.5)
        logging.info('Using default lower bound - in this case %i' % lower_bound)
    elif not isinstance(lower_bound, int):
        raise ValueError('Lower bound has to be None or an integer')
    if upper_bound is None:
        upper_bound = int(signal_length * 0.5)
        logging.info('Using default upper bound - in this case %i' % upper_bound)
    elif not isinstance(upper_bound, int) or upper_bound < lower_bound:
        raise ValueError('Upper bound has to be None or an integer and upper > lower bound')

    # prep target & signal matrix:
    # interpolate NaN's to avoid probs with the FFTs
    if interpolate:
        if np.any(np.isnan(signals)):
            signals = interpolate_nan(signals)
            logging.warning('Found numpy.nan in input signals - interpolating missing values for FFT')
        if np.any(np.isnan(target)):
            target = interpolate_nan(target)
            logging.warning('Found numpy.nan in target - interpolating missing values for FFT')
    # normalisation, all zero data handling
    # update - using trapezoid from scipy for improved normalization performance
    signals_norm = []
    for signal in signals:
        signals_norm.append(abs(trapezoid(y=signal)))
    signals_norm = np.array(signals_norm)
    target_norm = abs(trapezoid(y=target))
    # in the case of zeros in _norm replace 0 by 1
    signals_norm[signals_norm == 0] = 1
    target_norm = 1 if target_norm == 0 else target_norm
    # divide each signal by its normalising factor
    signals_fft = np.divide(signals.T, signals_norm).T
    target = np.divide(target, target_norm)

    # fft length with zero pad to avoid pollution (cf. Press & Teukolsky pg. 540 and 545)
    len_fft = signal_length + np.max(np.abs([lower_bound, upper_bound]))
    shifts = np.arange(lower_bound, upper_bound+1)

    if lower_bound < 0 < upper_bound:
        use_cc_indexes = list(range(len_fft + lower_bound, len_fft)) + list(range(0, upper_bound + 1))
    elif lower_bound < 0 and upper_bound < 0:
        # seams to work
        use_cc_indexes = list(range(len_fft + lower_bound, len_fft + upper_bound+1))
    elif lower_bound < 0 and upper_bound == 0:
        # not so sure if this works correctly
        use_cc_indexes = list(range(len_fft + lower_bound, len_fft)) + [0]
    else:
        use_cc_indexes = list(range(lower_bound, upper_bound+1))

    signals_fft = np.fft.fft(signals_fft, len_fft, axis=shift_axis)
    target_fft = np.conj(np.fft.fft(target, len_fft, axis=0))
    cc = np.fft.ifft(np.multiply(signals_fft, target_fft), len_fft, axis=shift_axis)
    cc = cc[:, use_cc_indexes]
    shift_idx = list(np.argmax(cc, axis=shift_axis))
    costs = np.concatenate((shifts.reshape(1, -1), cc), axis=0)
    shifts = shifts[shift_idx]

    logging.debug('ccfftshift finished')
    return shifts, costs


