"""
NeuroKit signal processing utilities for MOXIE physiological data.

Functions for cleaning, filtering, and processing ECG, RSP, Blood Pressure,
and other physiological signals using NeuroKit2.

Integrates with the BioData/DataObject structure from core.data_models.
"""

import matplotlib
matplotlib.use('Agg')  # Set backend for headless operation BEFORE importing pyplot
import matplotlib.pyplot as plt

import neurokit2 as nk
import numpy as np
import pandas as pd
from typing import Tuple, Optional, Dict
from pathlib import Path

from core.data_models import DataObject, BioData


def downsample_for_plotting(df: pd.DataFrame, max_points: int = 10000) -> pd.DataFrame:
    """
    Downsample a DataFrame for plotting to improve performance.

    For very large datasets (millions of points), plotting every point is slow
    and unnecessary. This function downsamples to a maximum number of points
    while preserving the overall signal shape.

    Args:
        df: DataFrame to downsample
        max_points: Maximum number of points to keep (default: 10000)

    Returns:
        Downsampled DataFrame
    """
    if len(df) <= max_points:
        return df

    # Calculate step size for uniform downsampling
    step = len(df) // max_points
    return df.iloc[::step].copy()


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
        try:
            # Downsample for plotting to improve performance with large datasets
            print(f"  Generating plot (downsampling {len(signals)} points for visualization)...")
            signals_plot = downsample_for_plotting(signals, max_points=10000)

            # NeuroKit plot functions return the figure object
            plot_result = nk.ecg_plot(signals_plot, info)
            # Get the current figure if plot_result is None or axes
            if plot_result is None or not hasattr(plot_result, 'savefig'):
                fig = plt.gcf()
            else:
                fig = plot_result

            fig.savefig(plot_file, dpi=150, bbox_inches='tight')
            plt.close(fig)  # Close figure to free memory
            print(f"  Saved: {plot_file}")
        except Exception as e:
            print(f"  Warning: Error generating plot: {e}")
            import traceback
            traceback.print_exc()

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
        try:
            # Downsample for plotting to improve performance with large datasets
            print(f"  Generating plot (downsampling {len(signals)} points for visualization)...")
            signals_plot = downsample_for_plotting(signals, max_points=10000)

            # Create a simple matplotlib plot instead of using NeuroKit's plot
            # (NeuroKit's rsp_plot has issues with downsampled data and peak indices)
            fig, axes = plt.subplots(3, 1, figsize=(15, 10))

            # Plot raw signal
            axes[0].plot(signals_plot['Time'], signals_plot['RSP_Raw'], color='gray', linewidth=0.5)
            axes[0].set_ylabel('Raw RSP')
            axes[0].set_title(f'Respiratory Signal: {data_object.name}')
            axes[0].grid(True, alpha=0.3)

            # Plot cleaned signal
            axes[1].plot(signals_plot['Time'], signals_plot['RSP_Clean'], color='blue', linewidth=0.7)
            axes[1].set_ylabel('Cleaned RSP')
            axes[1].grid(True, alpha=0.3)

            # Plot respiratory rate
            axes[2].plot(signals_plot['Time'], signals_plot['RSP_Rate'], color='red', linewidth=0.7)
            axes[2].set_ylabel('Rate (breaths/min)')
            axes[2].set_xlabel('Time (s)')
            axes[2].grid(True, alpha=0.3)

            plt.tight_layout()
            fig.savefig(plot_file, dpi=150, bbox_inches='tight')
            plt.close(fig)  # Close figure to free memory
            print(f"  Saved: {plot_file}")
        except Exception as e:
            print(f"  Warning: Error generating plot: {e}")

    return signals, info


def process_eda_signal(
    data_object: DataObject,
    method: str = 'neurokit',
    output_dir: Optional[Path] = None,
    save_artifacts: bool = False
) -> Tuple[pd.DataFrame, Dict]:
    """
    Process Electrodermal Activity (EDA) signal using NeuroKit2.

    Performs:
    - Signal cleaning/filtering
    - SCR (Skin Conductance Response) detection
    - Phasic/tonic decomposition
    - Statistical features

    Args:
        data_object: DataObject containing EDA signal
        method: Cleaning method ('neurokit', 'biosppy', etc.)
        output_dir: Directory to save artifacts
        save_artifacts: Whether to save processed data and plots

    Returns:
        Tuple of (processed_signals_df, info_dict)
    """
    print(f"\nProcessing EDA: {data_object.name}")
    print(f"  Samples: {len(data_object.data)}")
    print(f"  Sampling rate: {data_object.sampling_rate} Hz")
    print(f"  Duration: {data_object.time_column[-1]:.2f} seconds")

    # Process EDA using NeuroKit
    signals, info = nk.eda_process(
        data_object.data,
        sampling_rate=data_object.sampling_rate,
        method=method
    )

    # Add time column
    signals['Time'] = data_object.time_column

    # Print summary
    n_peaks = len(info['SCR_Peaks'])
    print(f"  SCR peaks detected: {n_peaks}")
    if 'EDA_Tonic' in signals.columns:
        print(f"  Mean tonic level: {signals['EDA_Tonic'].mean():.4f}")

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
        try:
            # Downsample for plotting to improve performance with large datasets
            print(f"  Generating plot (downsampling {len(signals)} points for visualization)...")
            signals_plot = downsample_for_plotting(signals, max_points=10000)

            # NeuroKit plot functions return the figure object
            plot_result = nk.eda_plot(signals_plot, info)
            # Get the current figure if plot_result is None or axes
            if plot_result is None or not hasattr(plot_result, 'savefig'):
                fig = plt.gcf()
            else:
                fig = plot_result

            fig.savefig(plot_file, dpi=150, bbox_inches='tight')
            plt.close(fig)  # Close figure to free memory
            print(f"  Saved: {plot_file}")
        except Exception as e:
            print(f"  Warning: Error generating plot: {e}")
            import traceback
            traceback.print_exc()

    return signals, info


def process_bloodpressure_signal(
    data_object: DataObject,
    output_dir: Optional[Path] = None,
    save_artifacts: bool = False
) -> Tuple[pd.DataFrame, Dict]:
    """
    Process Blood Pressure signal.

    Note: NeuroKit2 doesn't have dedicated blood pressure processing,
    so we perform basic cleaning and statistical analysis.

    Performs:
    - Signal cleaning/smoothing
    - Basic statistical features (mean, std, min, max)
    - Trend analysis

    Args:
        data_object: DataObject containing Blood Pressure signal
        output_dir: Directory to save artifacts
        save_artifacts: Whether to save processed data and plots

    Returns:
        Tuple of (processed_signals_df, info_dict)
    """
    print(f"\nProcessing Blood Pressure: {data_object.name}")
    print(f"  Samples: {len(data_object.data)}")
    print(f"  Sampling rate: {data_object.sampling_rate} Hz")
    print(f"  Duration: {data_object.time_column[-1]:.2f} seconds")

    # Create dataframe
    signals = pd.DataFrame()
    signals['BP_Raw'] = data_object.data
    signals['Time'] = data_object.time_column

    # Clean signal using signal processing
    # Use a combination of filters to clean the BP signal
    cleaned = nk.signal_filter(
        data_object.data,
        sampling_rate=data_object.sampling_rate,
        lowcut=0.5,
        highcut=None,
        method='butterworth',
        order=4
    )
    signals['BP_Clean'] = cleaned

    # Calculate basic statistics
    info = {
        'Mean_BP': np.mean(cleaned),
        'Std_BP': np.std(cleaned),
        'Min_BP': np.min(cleaned),
        'Max_BP': np.max(cleaned),
        'Median_BP': np.median(cleaned)
    }

    # Print summary
    print(f"  Mean BP: {info['Mean_BP']:.2f}")
    print(f"  Std BP: {info['Std_BP']:.2f}")
    print(f"  Range: [{info['Min_BP']:.2f}, {info['Max_BP']:.2f}]")

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
        try:
            # Downsample for plotting to improve performance with large datasets
            print(f"  Generating plot (downsampling {len(signals)} points for visualization)...")
            signals_plot = downsample_for_plotting(signals, max_points=10000)

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

            # Plot raw and cleaned signals
            ax1.plot(signals_plot['Time'], signals_plot['BP_Raw'], label='Raw', alpha=0.5)
            ax1.plot(signals_plot['Time'], signals_plot['BP_Clean'], label='Cleaned', linewidth=1.5)
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Blood Pressure')
            ax1.set_title(f'Blood Pressure Signal: {data_object.name}')
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            # Plot histogram (use full data for histogram)
            ax2.hist(cleaned, bins=50, edgecolor='black', alpha=0.7)
            ax2.axvline(info['Mean_BP'], color='red', linestyle='--', label=f"Mean: {info['Mean_BP']:.2f}")
            ax2.set_xlabel('Blood Pressure')
            ax2.set_ylabel('Frequency')
            ax2.set_title('Blood Pressure Distribution')
            ax2.legend()
            ax2.grid(True, alpha=0.3)

            plt.tight_layout()
            fig.savefig(plot_file, dpi=150, bbox_inches='tight')
            plt.close(fig)  # Close figure to free memory
            print(f"  Saved: {plot_file}")
        except Exception as e:
            print(f"  Warning: Error generating plot: {e}")
            import traceback
            traceback.print_exc()

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
            elif signal_type.lower() in ['eda', 'gsr', 'skin conductance']:
                signals, info = process_eda_signal(
                    data_obj,
                    output_dir=output_dir,
                    save_artifacts=save_artifacts
                )
            elif signal_type.lower() in ['bp', 'blood pressure', 'nibp']:
                signals, info = process_bloodpressure_signal(
                    data_obj,
                    output_dir=output_dir,
                    save_artifacts=save_artifacts
                )
            else:
                print(f"Warning: Unknown signal type '{signal_type}', skipping")
                continue

            results[data_obj.name] = (signals, info)

    return results
