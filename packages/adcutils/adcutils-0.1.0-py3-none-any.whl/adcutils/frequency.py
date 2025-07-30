import numpy as np
from typing import Union, Sequence, Literal

def apply_historisis(signal, threshold_low=0, threshold_high=0, threshold_percent:float|None = None, initial=False):
    """
    Apply hysteresis filtering to a signal and return states as 1 or -1.

    Args:
        signal (np.ndarray): Input 1D signal array.
        threshold_low (float, optional): Low threshold for switching off. Defaults to 0.
        threshold_high (float, optional): High threshold for switching on. Defaults to 0.
        threshold_percent (float or None, optional): If set, thresholds are calculated as a 
            percentage of half peak-to-peak amplitude. Overrides fixed thresholds.
        initial (bool, optional): Initial output state. Defaults to False.

    Returns:
        np.ndarray: Array of 1 (on) and -1 (off) states.
    """
    if threshold_percent is not None:
        center = signal.mean()
        offset = (signal.max() - signal.min()) * threshold_percent / 200
        threshold_high = round(center + offset, 6)
        threshold_low = round(center - offset, 6)

    hi = signal >= threshold_high
    lo_or_hi = (signal <= threshold_low) | hi
    ind = np.nonzero(lo_or_hi)[0]
    if not ind.size: # prevent index error if ind is empty
        return np.zeros_like(signal, dtype=bool) | initial
    cnt = np.cumsum(lo_or_hi) # from 0 to len(ind)
    return np.where(np.where(cnt, hi[ind[cnt-1]], initial), 1, -1)

def _get_freq_fft(signal: np.ndarray, sample_rate: float) -> float:
    """
    Estimate frequency using FFT peak detection.

    Parameters:
        signal (np.ndarray): The sampled signal (1D array).
        sample_rate (float): Samples per second.

    Returns:
        float: Estimated frequency in Hz.
    """
    n: int = len(signal)
    spectrum: np.ndarray = np.fft.fft(signal)
    freqs: np.ndarray = np.fft.fftfreq(n, d=1 / sample_rate)
    idx: int = int(np.argmax(np.abs(spectrum[: n // 2])))
    return abs(freqs[idx])


def _get_freq_zero_crossings(
        signal: np.ndarray, 
        sample_rate: float,
        hysterisis: bool = True,
        threshold: float = 10,
    ) -> float:
    """
    Estimate frequency by counting zero crossings.

    Parameters:
        signal (np.ndarray): The sampled signal (1D array).
        sample_rate (float): Samples per second.
        hysterisis (bool, optional): If True, apply hysteresis filtering 
            before counting. Defaults to True.
        threshold (float, optional): Threshold percentage for hysteresis 
            filtering.  Defaults to 10.

    Returns:
        float: Estimated frequency in Hz.
    """
    if hysterisis == True:
        signal = apply_historisis(signal, threshold_percent=threshold)
    zero_crossings: np.ndarray = np.where(np.diff(np.signbit(signal)))[0]
    num_cycles: float = len(zero_crossings)  / 2
    duration: float = len(signal) / sample_rate
    return num_cycles / duration if duration > 0 else 0.0


def get_freq(
    signal: Union[np.ndarray, Sequence[float]],
    sample_rate: float,
    mode: Literal["fft", "zero-crossings"] = "fft",
) -> float:
    """
    Estimate the dominant frequency of an ADC signal.

    Parameters:
        signal (Union[np.ndarray, Sequence[float]]): The sampled signal (1D array or list).
        sample_rate (float): Samples per second.
        mode (Literal['fft', 'zero-crossings']): Estimation method.

    Returns:
        float: Estimated frequency in Hz.
    """
    if not isinstance(signal, np.ndarray):
        signal = np.array(signal, dtype=float)

    if mode == "fft":
        return _get_freq_fft(signal, sample_rate)
    elif mode == "zero-crossings":
        return _get_freq_zero_crossings(signal, sample_rate)
    else:
        raise ValueError(f"Unknown mode '{mode}'. Use 'fft' or 'zero-crossings'.")


__all__ = [
    "get_freq"
]
