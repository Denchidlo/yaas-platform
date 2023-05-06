import scipy.signal as sgnl
import numpy as np
import cv2
from operator import itemgetter
from typing import List, Tuple

from pyyaap.config.fingerprint import (
    FP_HASH_DELTA_MAX, FP_HASH_DELTA_MIN, 
    FP_SPEC_FREQ, FP_SPEC_OVERLAP, FP_SPEC_WIN_SIZE,
    FP_PEAK_WIN_SIZE, FP_PEAK_MIN_AMP, 
    FP_N_NEIGHBOURS,
)


def _get_audio_spectrogram(
    data: np.ndarray, window_sz: int = FP_SPEC_WIN_SIZE, 
    freq: int = FP_SPEC_FREQ, overlap_ratio: float = FP_SPEC_OVERLAP, **kwargs
) -> np.ndarray:
    f, t, spectrum = sgnl.spectrogram(
        data,
        nperseg=window_sz, nfft=window_sz,fs=freq, window='hann',
        noverlap=int(window_sz * overlap_ratio), mode='psd',
        scaling='spectrum'
    )
    spectrum = 10 * np.log10(spectrum)
    return spectrum

def _get_spectrogram_local_peaks(
    spectrogram: np.ndarray, spec_win_size: int = FP_PEAK_WIN_SIZE,
    amp_min: int = FP_PEAK_MIN_AMP, **kwargs
) -> List[Tuple[int, int]]:
    locality_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (spec_win_size, spec_win_size)
    )

    dilated_img = cv2.dilate(spectrogram, locality_kernel, iterations=1)

    peak_map = (spectrogram == dilated_img)
    
    amps =  spectrogram[peak_map].flatten()
    f, t = np.where(peak_map)

    tgt_peak = np.where(amps > amp_min)
    f = f[tgt_peak]
    t = t[tgt_peak]

    return list(
        zip(f, t)
    ) 

def _get_combinatorial_hashes(
    peaks: List[Tuple[int, int]], offset_min: int = FP_HASH_DELTA_MIN, 
    offset_max: int = FP_HASH_DELTA_MAX, n_neighbours: int = FP_N_NEIGHBOURS, **kwargs
) -> List[Tuple[int, int]]:
    # frequencies are in the first position of the tuples
    idx_freq = 0
    # times are in the second position of the tuples
    idx_time = 1
    
    peaks.sort(key=itemgetter(1))

    hashes = []
    for i in range(len(peaks)):
        for j in range(1, n_neighbours):
            anchor_peak = peaks[i]
            if (i + j) < len(peaks):
                candidate_peak = peaks[i + j]

                t1 = anchor_peak[idx_time]
                t2 = candidate_peak[idx_time]
                t_delta = t2 - t1

                if offset_min <= t_delta <= offset_max:
                    anchor_fs = anchor_peak[idx_freq]
                    candidate_fs = candidate_peak[idx_freq]
                    c_hash = (anchor_fs << 32 | candidate_fs << 16 | t_delta)

                    hashes.append((int(c_hash), t1))

    return hashes

def fingerprint(
    data: np.ndarray, **kwargs
) -> List[Tuple[int, int]]:
    return _get_combinatorial_hashes(
        _get_spectrogram_local_peaks(
            _get_audio_spectrogram(data, **kwargs), **kwargs
        ), **kwargs
    )
