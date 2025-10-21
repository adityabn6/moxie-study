"""
Signal-to-Noise Ratio (SNR) quality assessment.

SNR is computed using Welch's method for spectral analysis over sliding windows.
Low SNR indicates poor signal quality.
"""

import numpy as np
from scipy import signal
from typing import Tuple

from core.data_models import BioData, DataObject


def compute_snr_welch(x: np.ndarray, fs: float) -> float:
    """
    Compute SNR using Welch's method for power spectral density.

    SNR is calculated as:
        SNR = 10 * log10(1 / spectral_flatness)

    Where spectral_flatness = geometric_mean(PSD) / arithmetic_mean(PSD)

    Args:
        x: Signal segment
        fs: Sampling frequency in Hz

    Returns:
        SNR value in dB
    """
    # Compute power spectral density using Welch's method
    f, Pxx = signal.welch(x, fs=fs)

    # Signal power (arithmetic mean)
    signal_power = np.mean(Pxx)

    # Geometric mean (with small epsilon to avoid log(0))
    geometric_mean = np.exp(np.mean(np.log(Pxx + 1e-12)))

    # Spectral flatness
    spectral_flatness = geometric_mean / signal_power

    # SNR in dB
    snr_db = 10 * np.log10(1 / spectral_flatness)

    return snr_db


def compute_and_append_snr(
    biodata: BioData,
    channel_name: str,
    fs: float,
    window_size_sec: float = 30,
    overlap_sec: float = 15,
    alpha: float = 0.5
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute SNR over sliding windows and append to BioData.

    Creates a new DataObject with SNR values and binary quality flags.
    Quality flag = 1 if SNR < alpha (poor quality)
    Quality flag = 0 if SNR >= alpha (good quality)

    Args:
        biodata: BioData object containing the channel
        channel_name: Name of channel to process
        fs: Sampling rate in Hz
        window_size_sec: Window size in seconds
        overlap_sec: Overlap between windows in seconds
        alpha: SNR threshold (values below are flagged)

    Returns:
        Tuple of (snr_values, snr_times, threshold_flags)
    """
    result = biodata.get_dataframe(channel_name)
    if result is None:
        raise ValueError(f"Channel '{channel_name}' not found in BioData")

    data_column, time_column = result
    snr_data, snr_time, threshold = [], [], []

    current = 0
    while current + window_size_sec < biodata.end_time:
        # Create time mask for current window
        mask = (time_column >= current) & (time_column < current + window_size_sec)
        segment = data_column[mask]

        if len(segment) == 0:
            current += overlap_sec
            continue

        # Compute SNR for this window
        snr_value = compute_snr_welch(segment, fs=fs)
        snr_data.append(snr_value)
        snr_time.append(current + window_size_sec / 2)  # Center of window

        current += overlap_sec

    # Create binary threshold flags
    threshold = [1 if val < alpha else 0 for val in snr_data]

    # Calculate output sampling rate
    sampling_rate_out = 1 / (window_size_sec - overlap_sec)

    # Create and append new DataObject
    snr_obj = DataObject(
        data=np.array(snr_data),
        name=f"{channel_name}_SNR",
        sampling_rate=sampling_rate_out,
        snr_feature=np.array(threshold)
    )
    biodata.append_to_dataframe(snr_obj)

    # Summary statistics
    flagged_windows = np.sum(threshold)
    total_windows = len(threshold)
    percentage_flagged = (flagged_windows / total_windows * 100) if total_windows > 0 else 0

    print(f"[SNR] {channel_name}: {total_windows} windows computed")
    print(f"      Flagged: {flagged_windows}/{total_windows} ({percentage_flagged:.1f}%)")
    print(f"      Mean SNR: {np.mean(snr_data):.2f} dB, Std: {np.std(snr_data):.2f} dB")

    return np.array(snr_data), np.array(snr_time), np.array(threshold)


def get_snr_statistics(snr_values: np.ndarray, threshold_flags: np.ndarray) -> dict:
    """
    Calculate summary statistics for SNR quality assessment.

    Args:
        snr_values: Array of SNR values
        threshold_flags: Binary flags (1=poor, 0=good)

    Returns:
        Dictionary of statistics
    """
    return {
        "mean_snr": np.mean(snr_values),
        "std_snr": np.std(snr_values),
        "min_snr": np.min(snr_values),
        "max_snr": np.max(snr_values),
        "median_snr": np.median(snr_values),
        "total_windows": len(snr_values),
        "flagged_windows": np.sum(threshold_flags),
        "percentage_flagged": (np.sum(threshold_flags) / len(threshold_flags) * 100)
        if len(threshold_flags) > 0 else 0
    }
