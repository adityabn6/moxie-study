"""
Amplitude-based quality assessment.

Amplitude quality checks detect periods of abnormally low signal amplitude,
which may indicate sensor disconnection or other technical issues.
"""

import numpy as np
from typing import Tuple

from core.data_models import BioData, DataObject


def compute_and_append_amplitude(
    biodata: BioData,
    channel_name: str,
    fs: float,
    window_size_sec: float = 30,
    overlap_sec: float = 15,
    beta: float = 0.5
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute amplitude over sliding windows and append to BioData.

    Amplitude is computed as the sum of squared signal values divided by window duration.
    A baseline threshold is calculated as: minimum + beta * std_deviation

    Quality flag = 1 if amplitude < baseline (poor quality)
    Quality flag = 0 if amplitude >= baseline (good quality)

    Args:
        biodata: BioData object containing the channel
        channel_name: Name of channel to process
        fs: Sampling rate in Hz
        window_size_sec: Window size in seconds
        overlap_sec: Overlap between windows in seconds
        beta: Factor for baseline calculation (baseline = min + beta * std)

    Returns:
        Tuple of (amplitude_values, amplitude_times, threshold_flags)
    """
    result = biodata.get_dataframe(channel_name)
    if result is None:
        raise ValueError(f"Channel '{channel_name}' not found in BioData")

    data_column, time_column = result
    amplitude_data, amplitude_time, threshold = [], [], []

    current = 0
    while current + window_size_sec < biodata.end_time:
        # Create time mask for current window
        mask = (time_column >= current) & (time_column < current + window_size_sec)
        segment = data_column[mask]

        if len(segment) == 0:
            current += overlap_sec
            continue

        # Compute amplitude (normalized sum of squares)
        segment_squared = np.square(segment)
        amplitude_value = np.sum(segment_squared) / window_size_sec
        amplitude_data.append(amplitude_value)
        amplitude_time.append(current + window_size_sec / 2)  # Center of window

        current += overlap_sec

    # Calculate baseline threshold from entire signal
    data_squared = np.square(data_column)
    minimum = np.min(data_squared)
    standard_dev = np.std(data_squared)
    baseline_threshold = minimum + beta * standard_dev

    # Create binary threshold flags
    threshold = [1 if val < baseline_threshold else 0 for val in amplitude_data]

    # Calculate output sampling rate
    sampling_rate_out = 1 / (window_size_sec - overlap_sec)

    # Create and append new DataObject
    amplitude_obj = DataObject(
        data=np.array(amplitude_data),
        name=f"{channel_name}_Amplitude",
        sampling_rate=sampling_rate_out,
        amplitude_feature=np.array(threshold)
    )
    biodata.append_to_dataframe(amplitude_obj)

    # Summary statistics
    flagged_windows = np.sum(threshold)
    total_windows = len(threshold)
    percentage_flagged = (flagged_windows / total_windows * 100) if total_windows > 0 else 0

    print(f"[Amplitude] {channel_name}: {total_windows} windows computed")
    print(f"            Flagged: {flagged_windows}/{total_windows} ({percentage_flagged:.1f}%)")
    print(f"            Mean: {np.mean(amplitude_data):.2e}, Baseline: {baseline_threshold:.2e}")

    return np.array(amplitude_data), np.array(amplitude_time), np.array(threshold)


def get_amplitude_statistics(
    amplitude_values: np.ndarray,
    threshold_flags: np.ndarray
) -> dict:
    """
    Calculate summary statistics for amplitude quality assessment.

    Args:
        amplitude_values: Array of amplitude values
        threshold_flags: Binary flags (1=poor, 0=good)

    Returns:
        Dictionary of statistics
    """
    return {
        "mean_amplitude": np.mean(amplitude_values),
        "std_amplitude": np.std(amplitude_values),
        "min_amplitude": np.min(amplitude_values),
        "max_amplitude": np.max(amplitude_values),
        "median_amplitude": np.median(amplitude_values),
        "total_windows": len(amplitude_values),
        "flagged_windows": np.sum(threshold_flags),
        "percentage_flagged": (np.sum(threshold_flags) / len(threshold_flags) * 100)
        if len(threshold_flags) > 0 else 0
    }
