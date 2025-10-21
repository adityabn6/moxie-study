"""
NeuroKit signal processing utilities for MOXIE physiological data.

Functions for cleaning, filtering, and processing ECG, RSP, Blood Pressure,
and other physiological signals using NeuroKit2.

Integrates with the BioData/DataObject structure from core.data_models.
"""

import neurokit2 as nk
import numpy as np
import pandas as pd
from typing import Tuple, Optional, Dict
from pathlib import Path

from core.data_models import DataObject, BioData


def process_ecg_signal(
    data_object: DataObject,
    method: str = 'neurokit',
    output_dir: Optional[Path] = None,
    save_artifacts: bool = False
) -> Tuple[pd.DataFrame, Dict]:
    """
    Process ECG signal using NeuroKit2.

    Performs:
    - Signal cleaning/filtering
    - R-peak detection
    - Heart rate calculation
    - Quality assessment

    Args:
        data_object: DataObject containing ECG signal
        method: Cleaning method ('neurokit', 'pantompkins1985', 'hamilton2002', etc.)
        output_dir: Directory to save artifacts
        save_artifacts: Whether to save processed data and plots

    Returns:
        Tuple of (processed_signals_df, info_dict)
            - processed_signals_df: DataFrame with cleaned ECG, R-peaks, heart rate
            - info_dict: Dictionary with peak indices, sampling rate, etc.
    """
    print(f"\nProcessing ECG: {data_object.name}")
    print(f"  Samples: {len(data_object.data)}")
    print(f"  Sampling rate: {data_object.sampling_rate} Hz")
    print(f"  Duration: {data_object.time_column[-1]:.2f} seconds")

    # Process ECG using NeuroKit
    signals, info = nk.ecg_process(
        data_object.data,
        sampling_rate=data_object.sampling_rate,
        method=method
    )

    # Add time column
    signals['Time'] = data_object.time_column

    # Print summary
    n_peaks = len(info['ECG_R_Peaks'])
    avg_hr = signals['ECG_Rate'].mean()
    print(f"  R-peaks detected: {n_peaks}")
    print(f"  Average heart rate: {avg_hr:.1f} BPM")

    # Save artifacts if requested
    if save_artifacts and output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save processed signals
        signals_file = output_dir / f"{data_object.name}_processed.csv"
        signals.to_csv(signals_file, index=False)
        print(f"  Saved: {signals_file}")

        # Save plot
        plot_file = output_dir / f"{data_object.name}_plot.png"
        fig = nk.ecg_plot(signals, info)
        fig.savefig(plot_file, dpi=150, bbox_inches='tight')
        print(f"  Saved: {plot_file}")

    return signals, info


def process_rsp_signal(
    data_object: DataObject,
    method: str = 'khodadad2018',
    output_dir: Optional[Path] = None,
    save_artifacts: bool = False
) -> Tuple[pd.DataFrame, Dict]:
    """
    Process respiratory (RSP) signal using NeuroKit2.

    Performs:
    - Signal cleaning/filtering
    - Peak detection (inhalation/exhalation)
    - Respiratory rate calculation
    - Respiratory variability metrics

    Args:
        data_object: DataObject containing RSP signal
        method: Cleaning method ('khodadad2018', 'biosppy', etc.)
        output_dir: Directory to save artifacts
        save_artifacts: Whether to save processed data and plots

    Returns:
        Tuple of (processed_signals_df, info_dict)
    """
    print(f"\nProcessing RSP: {data_object.name}")
    print(f"  Samples: {len(data_object.data)}")
    print(f"  Sampling rate: {data_object.sampling_rate} Hz")
    print(f"  Duration: {data_object.time_column[-1]:.2f} seconds")

    # Process RSP using NeuroKit
    signals, info = nk.rsp_process(
        data_object.data,
        sampling_rate=data_object.sampling_rate,
        method=method
    )

    # Add time column
    signals['Time'] = data_object.time_column

    # Print summary
    n_peaks = len(info['RSP_Peaks'])
    avg_rate = signals['RSP_Rate'].mean()
    print(f"  Respiratory peaks detected: {n_peaks}")
    print(f"  Average respiratory rate: {avg_rate:.1f} breaths/min")

    # Save artifacts if requested
    if save_artifacts and output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save processed signals
        signals_file = output_dir / f"{data_object.name}_processed.csv"
        signals.to_csv(signals_file, index=False)
        print(f"  Saved: {signals_file}")

        # Save plot
        plot_file = output_dir / f"{data_object.name}_plot.png"
        fig = nk.rsp_plot(signals, info)
        fig.savefig(plot_file, dpi=150, bbox_inches='tight')
        print(f"  Saved: {plot_file}")

    return signals, info


def clean_signal(
    data_object: DataObject,
    signal_type: str,
    method: Optional[str] = None
) -> np.ndarray:
    """
    Clean/filter a physiological signal.

    Args:
        data_object: DataObject containing signal
        signal_type: Type of signal ('ecg', 'rsp', 'eda', 'emg', 'ppg')
        method: Cleaning method (None for default)

    Returns:
        Cleaned signal as numpy array
    """
    signal_type = signal_type.lower()

    if signal_type == 'ecg':
        cleaned = nk.ecg_clean(
            data_object.data,
            sampling_rate=data_object.sampling_rate,
            method=method or 'neurokit'
        )
    elif signal_type == 'rsp':
        cleaned = nk.rsp_clean(
            data_object.data,
            sampling_rate=data_object.sampling_rate,
            method=method or 'khodadad2018'
        )
    elif signal_type == 'eda':
        cleaned = nk.eda_clean(
            data_object.data,
            sampling_rate=data_object.sampling_rate,
            method=method or 'neurokit'
        )
    elif signal_type == 'emg':
        cleaned = nk.emg_clean(
            data_object.data,
            sampling_rate=data_object.sampling_rate
        )
    elif signal_type == 'ppg':
        cleaned = nk.ppg_clean(
            data_object.data,
            sampling_rate=data_object.sampling_rate
        )
    else:
        raise ValueError(f"Unknown signal type: {signal_type}")

    print(f"Cleaned {signal_type.upper()} signal: {data_object.name}")

    return cleaned


def add_processed_signal_to_biodata(
    biodata: BioData,
    signals_df: pd.DataFrame,
    original_data_object: DataObject,
    signal_column: str,
    new_name_suffix: str
) -> None:
    """
    Add a processed signal column back to BioData as a new DataObject.

    Args:
        biodata: BioData object to add to
        signals_df: DataFrame with processed signals
        original_data_object: Original DataObject (for metadata)
        signal_column: Column name in signals_df to extract
        new_name_suffix: Suffix to add to original name (e.g., '_cleaned', '_rate')
    """
    if signal_column not in signals_df.columns:
        print(f"Warning: Column '{signal_column}' not found in processed signals")
        return

    new_name = f"{original_data_object.name}{new_name_suffix}"

    new_data_object = DataObject(
        data=signals_df[signal_column].values,
        name=new_name,
        sampling_rate=original_data_object.sampling_rate
    )

    biodata.append_to_dataframe(new_data_object)
    print(f"Added processed signal: {new_name}")


def process_biodata_channels(
    biodata: BioData,
    channel_patterns: Dict[str, str],
    output_dir: Optional[Path] = None,
    save_artifacts: bool = False
) -> Dict[str, Tuple[pd.DataFrame, Dict]]:
    """
    Process multiple channels in a BioData object.

    Args:
        biodata: BioData object with physiological signals
        channel_patterns: Dict mapping signal type to channel name pattern
                         e.g., {'ecg': 'ECG', 'rsp': 'RSP', 'bp': 'Blood Pressure'}
        output_dir: Directory to save artifacts
        save_artifacts: Whether to save processed data and plots

    Returns:
        Dictionary mapping channel names to (signals_df, info_dict) tuples
    """
    results = {}

    for signal_type, pattern in channel_patterns.items():
        # Find matching channels
        matching_channels = [
            data_obj for data_obj in biodata.Data
            if pattern.lower() in data_obj.name.lower()
        ]

        if not matching_channels:
            print(f"Warning: No channels found matching pattern '{pattern}'")
            continue

        # Process each matching channel
        for data_obj in matching_channels:
            if signal_type.lower() == 'ecg':
                signals, info = process_ecg_signal(
                    data_obj,
                    output_dir=output_dir,
                    save_artifacts=save_artifacts
                )
            elif signal_type.lower() in ['rsp', 'respiration', 'breathing']:
                signals, info = process_rsp_signal(
                    data_obj,
                    output_dir=output_dir,
                    save_artifacts=save_artifacts
                )
            else:
                print(f"Warning: Unknown signal type '{signal_type}', skipping")
                continue

            results[data_obj.name] = (signals, info)

    return results
