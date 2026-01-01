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
    """
    if len(df) <= max_points:
        return df

    # Calculate step size for uniform downsampling
    step = len(df) // max_points
    return df.iloc[::step].copy()


def get_window_and_adjust_info(
    signals: pd.DataFrame,
    info: Dict,
    sampling_rate: float,
    window_duration: float = 60.0,
    plot_type: str = 'ecg'
) -> Tuple[pd.DataFrame, Dict]:
    """
    Slice the signals dataframe to a central window and adjust index-based info keys.
    """
    total_samples = len(signals)
    window_samples = int(window_duration * sampling_rate)
    
    if total_samples <= window_samples:
        return signals, info
        
    start_idx = (total_samples - window_samples) // 2
    end_idx = start_idx + window_samples
    
    # 1. Slice DataFrame
    windowed_signals = signals.iloc[start_idx:end_idx].copy()
    
    # Adjust time to be relative to window for clarity (0-60s) or keep absolute?
    # NeuroKit plots usually ignore indices and plot 0..N samples on X axis unless index is set
    # Let's reset index so 0 is start of plot
    windowed_signals = windowed_signals.reset_index(drop=True)
    
    # 2. Adjust Info Dictionary (Peak Indices)
    windowed_info = info.copy()
    
    # Keys that contain sample indices need to be filtered and shifted
    keys_to_adjust = []
    if plot_type == 'ecg':
        keys_to_adjust = ['ECG_R_Peaks', 'ECG_P_Peaks', 'ECG_Q_Peaks', 'ECG_S_Peaks', 'ECG_T_Peaks',
                          'ECG_P_Onsets', 'ECG_P_Offsets', 'ECG_T_Onsets', 'ECG_T_Offsets']
    elif plot_type == 'eda':
        keys_to_adjust = ['SCR_Peaks', 'SCR_Onsets']
    elif plot_type == 'rsp':
        keys_to_adjust = ['RSP_Peaks', 'RSP_Troughs']
        
    for key in keys_to_adjust:
        if key in windowed_info:
            indices = np.array(windowed_info[key])
            # Filter indices within window
            mask = (indices >= start_idx) & (indices < end_idx)
            # Shift indices to be relative to start of window
            # Also handle NaNs (some peak detectors pad with NaNs)
            valid_indices = indices[mask]
            shifted_indices = valid_indices - start_idx
            windowed_info[key] = shifted_indices
            
    return windowed_signals, windowed_info


def plot_eda_fallback(win_sig, win_info, sampling_rate):
    """Fallback custom plot for EDA if NeuroKit fails."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    t = win_sig['Time'] if 'Time' in win_sig.columns else np.arange(len(win_sig)) / sampling_rate
    
    # Ax1: Raw vs Clean
    ax1.plot(t, win_sig.get('EDA_Raw', win_sig['EDA_Clean']), color='gray', alpha=0.5, label='Raw')
    ax1.plot(t, win_sig['EDA_Clean'], color='purple', label='Clean')
    
    # Mark SCR peaks
    if 'SCR_Peaks' in win_info and len(win_info['SCR_Peaks']) > 0:
        peaks = win_info['SCR_Peaks']
        # Ensure peaks are within bounds
        peaks = peaks[peaks < len(win_sig)]
        ax1.scatter(t.iloc[peaks], win_sig['EDA_Clean'].iloc[peaks], color='red', zorder=5, label='SCR Peaks')
        
    ax1.set_title('EDA Signal (Zoomed)')
    ax1.set_ylabel('Conductance (uS)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Ax2: Components (Phasic / Tonic)
    if 'EDA_Phasic' in win_sig.columns and 'EDA_Tonic' in win_sig.columns:
        ax2.plot(t, win_sig['EDA_Tonic'], color='blue', label='Tonic')
        ax2.plot(t, win_sig['EDA_Phasic'], color='orange', label='Phasic')
        ax2.set_ylabel('Components')
        ax2.legend()
    else:
        ax2.text(0.5, 0.5, "Components not available", ha='center')
        
    ax2.set_xlabel('Time (s)')
    ax2.grid(True, alpha=0.3)
    
    return fig


def generate_hybrid_plot(signals, info, data_object, plot_type, output_file):
    """
    Generate a hybrid plot with a Full-Session Trend (top) and Windowed NeuroKit Plot (bottom).
    """
    # 1. Prepare Windowed Data for NeuroKit Plot
    # Slice a 60s window from the middle
    win_sig, win_info = get_window_and_adjust_info(
        signals, info, data_object.sampling_rate, window_duration=60.0, plot_type=plot_type
    )
    
    # 2. Create Figure
    # We want a layout where top is Trend, bottom is NK.
    # Since NK plots output a Figure, we might need to manipulate it.
    # Strategy: Create NK plot first (which makes a Figure), then resize it and add axes at top.
    
    print(f"  Generating zoomed NeuroKit plot (60s window)...")
    nk_fig = None
    
    try:
        if plot_type == 'ecg':
            # nk.ecg_plot returns None but plots to current figure, OR returns figure depending on version?
            # In standardized usage:
            nk.ecg_plot(win_sig, win_info)
            nk_fig = plt.gcf()
            
        elif plot_type == 'eda':
            # Try NK plot, usually works but can fail on weird windows
            try:
                nk.eda_plot(win_sig, win_info)
                nk_fig = plt.gcf()
            except Exception as nk_e:
                print(f"  NeuroKit EDA plot failed ({nk_e}), using fallback...")
                plt.close('all') # Clear any partial plot
                nk_fig = plot_eda_fallback(win_sig, win_info, data_object.sampling_rate)
            
        elif plot_type == 'rsp':
            nk.rsp_plot(win_sig, win_info)
            nk_fig = plt.gcf()
    except Exception as e:
        print(f"  Warning: NeuroKit plot failed for {plot_type}: {e}")
        # Fallback for others or hard fail
        plt.close('all')
        return
        
    if nk_fig:
        # Resize figure to make room at top
        # Check current size
        w, h = nk_fig.get_size_inches()
        nk_fig.set_size_inches(w, h + 2) # Add some height for the trend
        
        # Add new axes at the top for Trend
        # (left, bottom, width, height) in normalized coordinates
        # Current NK plot typically takes up most space. We can try to use subplots_adjust
        nk_fig.subplots_adjust(top=0.75) # Push NK plot down
        
        ax_trend = nk_fig.add_axes([0.1, 0.8, 0.8, 0.15]) # Top 15%
        
        # ... (rest of trend plotting logic) ...
        # Downsample for performance
        trend_sig = downsample_for_plotting(signals, max_points=10000)
        
        plot_title = f"{data_object.name} (Full Session Trend)"
        
        if plot_type == 'ecg':
             ax_trend.plot(trend_sig['Time'], trend_sig['ECG_Rate'], color='red', linewidth=1)
             ax_trend.set_ylabel('Heart Rate (BPM)')
             plot_title += " - Avg HR: {:.1f}".format(signals['ECG_Rate'].mean())
             
        elif plot_type == 'eda':
             # Plot Tonic component if available, else Raw
             if 'EDA_Tonic' in trend_sig.columns:
                 ax_trend.plot(trend_sig['Time'], trend_sig['EDA_Tonic'], color='purple', linewidth=1, label='Tonic')
                 ax_trend.plot(trend_sig['Time'], trend_sig['EDA_Clean'], color='blue', alpha=0.3, linewidth=0.5, label='Phasic+Tonic')
                 ax_trend.legend(loc='upper right', fontsize='small')
             else:
                 ax_trend.plot(trend_sig['Time'], trend_sig['EDA_Raw'], color='purple')
             ax_trend.set_ylabel('Skin Conductance (uS)')
             
        elif plot_type == 'rsp':
             ax_trend.plot(trend_sig['Time'], trend_sig['RSP_Rate'], color='green', linewidth=1)
             ax_trend.set_ylabel('Breathing Rate (BPM)')
             plot_title += " - Avg: {:.1f}".format(signals['RSP_Rate'].mean())

        ax_trend.set_title(plot_title)
        ax_trend.set_xlabel('Time (s)')
        ax_trend.grid(True, alpha=0.3)
        
        # Add annotation for where the zoom is
        mid_idx = len(signals) // 2
        mid_time = signals.iloc[mid_idx]['Time']
        ax_trend.axvline(mid_time, color='orange', linestyle='--', alpha=0.8, label='Zoom Window')
        ax_trend.legend(loc='upper left', fontsize='small')

        # Save
        nk_fig.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close(nk_fig)
        print(f"  Saved Hybrid Plot: {output_file}")
    else:
        print("Error: Could not capture NeuroKit figure")


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

        # Save plot (Hybrid: Full Trend + Windowed NeuroKit)
        plot_file = output_dir / f"{data_object.name}_plot.png"
        try:
            generate_hybrid_plot(
                signals=signals,
                info=info,
                data_object=data_object,
                plot_type='ecg',
                output_file=plot_file
            )
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
            generate_hybrid_plot(
                signals=signals,
                info=info,
                data_object=data_object,
                plot_type='rsp',
                output_file=plot_file
            )
        except Exception as e:
            print(f"  Warning: Error generating plot: {e}")
            import traceback
            traceback.print_exc()

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
             generate_hybrid_plot(
                signals=signals,
                info=info,
                data_object=data_object,
                plot_type='eda',
                output_file=plot_file
            )
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
    # Use a Low-pass filter to keep DC component (absolute pressure) but remove noise
    # Butterworth low-pass at 40Hz (assuming 2000Hz sampling, this is safe)
    # High-pass would remove the mean pressure (bad!)
    cleaned = nk.signal_filter(
        data_object.data,
        sampling_rate=data_object.sampling_rate,
        lowcut=None,
        highcut=40,
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
            print(f"  Generating plot (Hybrid: Trend + Zoom + Hist)...")
            signals_plot = downsample_for_plotting(signals, max_points=10000)

            # Create Figure with 3 rows
            fig = plt.figure(figsize=(12, 12))
            gs = fig.add_gridspec(3, 1, height_ratios=[1, 1, 1])
            
            # Row 1: Full Trend
            ax1 = fig.add_subplot(gs[0])
            ax1.plot(signals_plot['Time'], signals_plot['BP_Raw'], label='Raw', alpha=0.5, color='gray', linewidth=0.5)
            ax1.plot(signals_plot['Time'], signals_plot['BP_Clean'], label='Cleaned', linewidth=1.0, color='blue')
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Pressure (mmHg)')
            ax1.set_title(f'Blood Pressure: Full Session ({data_object.name})')
            ax1.legend(loc='upper right')
            ax1.grid(True, alpha=0.3)
            
            # Row 2: Zoomed 60s Window (Waveform)
            ax2 = fig.add_subplot(gs[1])
            # Slice
            win_sig, _ = get_window_and_adjust_info(signals, {}, data_object.sampling_rate, window_duration=60.0)
            
            if len(win_sig) > 0:
                ax2.plot(win_sig['Time'], win_sig['BP_Clean'], color='blue', linewidth=1.5)
                ax2.set_title('Zoomed Waveform (60s Window)')
                ax2.set_xlabel('Time (s)')
                ax2.set_ylabel('Pressure (mmHg)')
                # Mark Mean BP
                ax2.axhline(info['Mean_BP'], color='red', linestyle='--', alpha=0.5, label='Mean BP')
                ax2.legend()
                ax2.grid(True, alpha=0.3)
            else:
                ax2.text(0.5, 0.5, "Not enough data for zoom", ha='center')

            # Row 3: Histogram
            ax3 = fig.add_subplot(gs[2])
            ax3.hist(cleaned, bins=50, edgecolor='black', alpha=0.7, density=True)
            ax3.axvline(info['Mean_BP'], color='red', linestyle='--', label=f"Mean: {info['Mean_BP']:.1f}")
            ax3.set_xlabel('Blood Pressure (mmHg)')
            ax3.set_ylabel('Density')
            ax3.set_title('Blood Pressure Distribution')
            ax3.legend()
            ax3.grid(True, alpha=0.3)

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
