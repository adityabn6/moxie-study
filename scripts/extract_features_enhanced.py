#!/usr/bin/env python3
"""
ENHANCED Feature Extraction for Stress Research - MOXIE Study

This enhanced version extracts ~60 optimal features for stress research:
- HRV: Time-domain + Frequency-domain (LF/HF ratio!) + Non-linear (SD1/SD2)
- EDA: Tonic + SCR dynamics (amplitude, rise time, recovery time)
- RSP: Single channel + Multi-channel coordination (thoracic-abdominal)
- BP: Mean, variability, slope

Key additions for stress research:
1. HRV_LF_HF_RATIO - THE gold standard stress biomarker
2. RSP_THORACIC_ABDOMINAL_CORRELATION - Paradoxical breathing in anxiety
3. SCR_AMPLITUDE_MEAN - Arousal intensity (not just frequency)
4. SCR_RISE_TIME - Speed of stress response
5. RSA - Vagal tone / autonomic regulation

Usage:
    python extract_features_enhanced.py --all  # Process all participants
    python extract_features_enhanced.py --participant-id 124874  # Single participant
    python extract_features_enhanced.py --all -o enhanced_features.csv
"""

import argparse
import sys
import pandas as pd
import numpy as np
import neurokit2 as nk
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from scipy.stats import linregress

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_io.data_loader import load_acq_file, create_windows_for_visit
from data_io.file_discovery import find_acq_files


def calculate_hrv_features_enhanced(
    ecg_data: pd.DataFrame,
    window_start: float,
    window_end: float,
    sampling_rate: int = 2000
) -> Dict[str, float]:
    """
    Calculate comprehensive HRV features using NeuroKit's nk.hrv() function.

    Includes:
    - Time-domain: RMSSD, SDNN, pNN50, MeanNN, MedianNN
    - Frequency-domain: LF, HF, LF/HF ratio, VLF, normalized powers
    - Non-linear: SD1, SD2, SD1/SD2 ratio

    Args:
        ecg_data: DataFrame with ECG processed data
        window_start: Start time in seconds
        window_end: End time in seconds
        sampling_rate: Sampling rate in Hz

    Returns:
        Dictionary of HRV features (~18 features)
    """
    # Filter data to window
    mask = (ecg_data['Time'] >= window_start) & (ecg_data['Time'] <= window_end)
    window_data = ecg_data[mask].copy()

    # Initialize all features with NaN
    nan_features = {
        # Time-domain
        'hrv_rmssd': np.nan, 'hrv_sdnn': np.nan, 'hrv_pnn50': np.nan,
        'hrv_meannn': np.nan, 'hrv_mediann': np.nan, 'hrv_cvnn': np.nan,
        'hrv_num_beats': np.nan,
        # Frequency-domain (CRITICAL for stress!)
        'hrv_lf': np.nan, 'hrv_hf': np.nan, 'hrv_vlf': np.nan,
        'hrv_lf_hf_ratio': np.nan,  # ⭐⭐⭐⭐⭐ THE stress biomarker
        'hrv_lf_nu': np.nan, 'hrv_hf_nu': np.nan,
        # Non-linear
        'hrv_sd1': np.nan, 'hrv_sd2': np.nan, 'hrv_sd1_sd2': np.nan,
        # Basic HR stats
        'hrv_mean_hr': np.nan, 'hrv_std_hr': np.nan,
        'hrv_min_hr': np.nan, 'hrv_max_hr': np.nan,
    }

    if len(window_data) == 0:
        return nan_features

    # Basic heart rate stats
    heart_rate = window_data['ECG_Rate'].dropna()
    if len(heart_rate) > 0:
        nan_features['hrv_mean_hr'] = heart_rate.mean()
        nan_features['hrv_std_hr'] = heart_rate.std()
        nan_features['hrv_min_hr'] = heart_rate.min()
        nan_features['hrv_max_hr'] = heart_rate.max()

    # Check if we have enough R-peaks for HRV analysis
    r_peaks = window_data[window_data['ECG_R_Peaks'] == 1]
    nan_features['hrv_num_beats'] = len(r_peaks)

    if len(r_peaks) < 10:  # Need minimum beats for frequency analysis
        return nan_features

    try:
        # Create peaks DataFrame for NeuroKit
        # Reset index to make it continuous for NeuroKit
        peaks_indices = r_peaks.index.values - window_data.index[0]
        peaks_df = pd.DataFrame({'ECG_R_Peaks': 0}, index=range(len(window_data)))
        peaks_df.loc[peaks_indices, 'ECG_R_Peaks'] = 1

        # Use NeuroKit's comprehensive HRV function
        hrv_indices = nk.hrv(peaks_df, sampling_rate=sampling_rate, show=False)

        if hrv_indices is not None and len(hrv_indices) > 0:
            # Time-domain features
            if 'HRV_RMSSD' in hrv_indices.columns:
                nan_features['hrv_rmssd'] = hrv_indices['HRV_RMSSD'].iloc[0]
            if 'HRV_SDNN' in hrv_indices.columns:
                nan_features['hrv_sdnn'] = hrv_indices['HRV_SDNN'].iloc[0]
            if 'HRV_pNN50' in hrv_indices.columns:
                nan_features['hrv_pnn50'] = hrv_indices['HRV_pNN50'].iloc[0]
            if 'HRV_MeanNN' in hrv_indices.columns:
                nan_features['hrv_meannn'] = hrv_indices['HRV_MeanNN'].iloc[0]
            if 'HRV_MedianNN' in hrv_indices.columns:
                nan_features['hrv_mediann'] = hrv_indices['HRV_MedianNN'].iloc[0]
            if 'HRV_CVNN' in hrv_indices.columns:
                nan_features['hrv_cvnn'] = hrv_indices['HRV_CVNN'].iloc[0]

            # Frequency-domain features (CRITICAL!)
            if 'HRV_LF' in hrv_indices.columns:
                nan_features['hrv_lf'] = hrv_indices['HRV_LF'].iloc[0]
            if 'HRV_HF' in hrv_indices.columns:
                nan_features['hrv_hf'] = hrv_indices['HRV_HF'].iloc[0]
            if 'HRV_VLF' in hrv_indices.columns:
                nan_features['hrv_vlf'] = hrv_indices['HRV_VLF'].iloc[0]
            if 'HRV_LFHF' in hrv_indices.columns:
                nan_features['hrv_lf_hf_ratio'] = hrv_indices['HRV_LFHF'].iloc[0]
            if 'HRV_LFn' in hrv_indices.columns:
                nan_features['hrv_lf_nu'] = hrv_indices['HRV_LFn'].iloc[0]
            if 'HRV_HFn' in hrv_indices.columns:
                nan_features['hrv_hf_nu'] = hrv_indices['HRV_HFn'].iloc[0]

            # Non-linear features
            if 'HRV_SD1' in hrv_indices.columns:
                nan_features['hrv_sd1'] = hrv_indices['HRV_SD1'].iloc[0]
            if 'HRV_SD2' in hrv_indices.columns:
                nan_features['hrv_sd2'] = hrv_indices['HRV_SD2'].iloc[0]
            if 'HRV_SD1SD2' in hrv_indices.columns:
                nan_features['hrv_sd1_sd2'] = hrv_indices['HRV_SD1SD2'].iloc[0]

    except Exception as e:
        print(f"    Warning: HRV calculation failed: {e}")

    return nan_features


def calculate_eda_features_enhanced(
    eda_data: pd.DataFrame,
    window_start: float,
    window_end: float
) -> Dict[str, float]:
    """
    Calculate comprehensive EDA features including SCR dynamics.

    Includes:
    - Tonic: mean, std, min, max, slope
    - Phasic: mean, std, AUC
    - SCR: count, frequency, amplitude, rise time, recovery time

    Args:
        eda_data: DataFrame with EDA processed data
        window_start: Start time in seconds
        window_end: End time in seconds

    Returns:
        Dictionary of EDA features (~14 features)
    """
    # Filter data to window
    mask = (eda_data['Time'] >= window_start) & (eda_data['Time'] <= window_end)
    window_data = eda_data[mask]
    window_duration = window_end - window_start

    features = {
        # Tonic features
        'eda_tonic_mean': np.nan, 'eda_tonic_std': np.nan,
        'eda_tonic_min': np.nan, 'eda_tonic_max': np.nan,
        'eda_tonic_slope': np.nan,
        # Phasic features
        'eda_phasic_mean': np.nan, 'eda_phasic_std': np.nan,
        'eda_phasic_auc': np.nan,
        # SCR features
        'scr_num_peaks': np.nan, 'scr_frequency': np.nan,
        'scr_amplitude_mean': np.nan, 'scr_amplitude_max': np.nan,
        'scr_rise_time_mean': np.nan, 'scr_recovery_time_mean': np.nan,
    }

    if len(window_data) == 0:
        return features

    # Tonic (SCL) features
    if 'EDA_Tonic' in window_data.columns:
        tonic = window_data['EDA_Tonic'].dropna()
        if len(tonic) > 0:
            features['eda_tonic_mean'] = tonic.mean()
            features['eda_tonic_std'] = tonic.std()
            features['eda_tonic_min'] = tonic.min()
            features['eda_tonic_max'] = tonic.max()

            # Tonic slope (trend over time)
            if len(tonic) > 2:
                try:
                    time_vals = window_data.loc[tonic.index, 'Time'].values
                    slope, _, _, _, _ = linregress(time_vals, tonic.values)
                    features['eda_tonic_slope'] = slope
                except:
                    pass

    # Phasic (SCR) features
    if 'EDA_Phasic' in window_data.columns:
        phasic = window_data['EDA_Phasic'].dropna()
        if len(phasic) > 0:
            features['eda_phasic_mean'] = phasic.mean()
            features['eda_phasic_std'] = phasic.std()
            # AUC - area under phasic curve (total phasic activity)
            features['eda_phasic_auc'] = np.trapz(phasic.values)

    # SCR peak features (CRITICAL for stress!)
    if 'SCR_Peaks' in window_data.columns:
        scr_peaks = window_data[window_data['SCR_Peaks'] == 1]
        num_scrs = len(scr_peaks)
        features['scr_num_peaks'] = num_scrs

        if num_scrs > 0:
            # SCR frequency (per minute)
            features['scr_frequency'] = num_scrs / (window_duration / 60)

            # SCR amplitude (intensity of arousal)
            if 'SCR_Amplitude' in scr_peaks.columns:
                amplitudes = scr_peaks['SCR_Amplitude'].dropna()
                if len(amplitudes) > 0:
                    features['scr_amplitude_mean'] = amplitudes.mean()
                    features['scr_amplitude_max'] = amplitudes.max()

            # SCR rise time (speed of arousal response)
            if 'SCR_RiseTime' in scr_peaks.columns:
                rise_times = scr_peaks['SCR_RiseTime'].dropna()
                if len(rise_times) > 0:
                    features['scr_rise_time_mean'] = rise_times.mean()

            # SCR recovery time (arousal regulation)
            if 'SCR_RecoveryTime' in scr_peaks.columns:
                recovery_times = scr_peaks['SCR_RecoveryTime'].dropna()
                if len(recovery_times) > 0:
                    features['scr_recovery_time_mean'] = recovery_times.mean()

    return features


def calculate_rsp_features_enhanced(
    rsp_data: pd.DataFrame,
    window_start: float,
    window_end: float,
    channel_name: str = ''
) -> Dict[str, float]:
    """
    Calculate enhanced respiratory features for a single channel.

    Includes:
    - Rate: mean, std, variability
    - Amplitude: mean, std
    - RVT (respiratory volume per time)
    - I/E ratio (inspiration/expiration)
    - Symmetry metrics

    Args:
        rsp_data: DataFrame with RSP processed data
        window_start: Start time in seconds
        window_end: End time in seconds
        channel_name: 'thoracic' or 'abdominal' for feature naming

    Returns:
        Dictionary of RSP features (~10 features per channel)
    """
    prefix = f'rsp_{channel_name}_' if channel_name else 'rsp_'

    # Filter data to window
    mask = (rsp_data['Time'] >= window_start) & (rsp_data['Time'] <= window_end)
    window_data = rsp_data[mask]

    features = {
        f'{prefix}mean_rate': np.nan,
        f'{prefix}std_rate': np.nan,
        f'{prefix}mean_amplitude': np.nan,
        f'{prefix}std_amplitude': np.nan,
        f'{prefix}num_breaths': np.nan,
        f'{prefix}rvt_mean': np.nan,
        f'{prefix}ie_ratio_mean': np.nan,
        f'{prefix}breath_variability': np.nan,
    }

    if len(window_data) == 0:
        return features

    # Respiratory rate
    if 'RSP_Rate' in window_data.columns:
        rate = window_data['RSP_Rate'].dropna()
        if len(rate) > 0:
            features[f'{prefix}mean_rate'] = rate.mean()
            features[f'{prefix}std_rate'] = rate.std()

    # Respiratory amplitude
    if 'RSP_Amplitude' in window_data.columns:
        amplitude = window_data['RSP_Amplitude'].dropna()
        if len(amplitude) > 0:
            features[f'{prefix}mean_amplitude'] = amplitude.mean()
            features[f'{prefix}std_amplitude'] = amplitude.std()

    # Number of breaths
    if 'RSP_Peaks' in window_data.columns:
        peaks = window_data[window_data['RSP_Peaks'] == 1]
        features[f'{prefix}num_breaths'] = len(peaks)

        # Breath-by-breath variability (like HRV for breathing)
        if len(peaks) >= 3:
            breath_intervals = np.diff(peaks['Time'].values)
            features[f'{prefix}breath_variability'] = np.std(breath_intervals, ddof=1)

    # Respiratory Volume per Time (RVT) - minute ventilation estimate
    if 'RSP_RVT' in window_data.columns:
        rvt = window_data['RSP_RVT'].dropna()
        if len(rvt) > 0:
            features[f'{prefix}rvt_mean'] = rvt.mean()

    # I/E ratio (Inspiration/Expiration) - breathing symmetry
    if 'RSP_Symmetry_RiseDecay' in window_data.columns:
        ie_ratio = window_data['RSP_Symmetry_RiseDecay'].dropna()
        if len(ie_ratio) > 0:
            features[f'{prefix}ie_ratio_mean'] = ie_ratio.mean()

    return features


def calculate_rsp_coordination_features(
    rsp_thoracic: pd.DataFrame,
    rsp_abdominal: pd.DataFrame,
    window_start: float,
    window_end: float
) -> Dict[str, float]:
    """
    Calculate coordination features between thoracic and abdominal breathing.

    CRITICAL for stress research:
    - Correlation: Paradoxical breathing (negative) in anxiety
    - Thoracic dominance: Shift from abdominal to thoracic in stress

    Args:
        rsp_thoracic: DataFrame with thoracic RSP data
        rsp_abdominal: DataFrame with abdominal RSP data
        window_start: Start time in seconds
        window_end: End time in seconds

    Returns:
        Dictionary of coordination features (~5 features)
    """
    features = {
        'rsp_thoracic_abdominal_correlation': np.nan,
        'rsp_thoracic_dominance': np.nan,
        'rsp_phase_coherence': np.nan,
        'rsp_contribution_thoracic': np.nan,
    }

    # Filter both channels to window
    mask_thor = (rsp_thoracic['Time'] >= window_start) & (rsp_thoracic['Time'] <= window_end)
    mask_abdo = (rsp_abdominal['Time'] >= window_start) & (rsp_abdominal['Time'] <= window_end)

    window_thor = rsp_thoracic[mask_thor]
    window_abdo = rsp_abdominal[mask_abdo]

    if len(window_thor) == 0 or len(window_abdo) == 0:
        return features

    # Ensure same length for correlation
    min_len = min(len(window_thor), len(window_abdo))

    try:
        # Correlation between cleaned signals (CRITICAL!)
        # Normal: 0.7-0.9, Paradoxical breathing: <0 or very low
        if 'RSP_Clean' in window_thor.columns and 'RSP_Clean' in window_abdo.columns:
            thor_clean = window_thor['RSP_Clean'].iloc[:min_len].values
            abdo_clean = window_abdo['RSP_Clean'].iloc[:min_len].values

            correlation = np.corrcoef(thor_clean, abdo_clean)[0, 1]
            features['rsp_thoracic_abdominal_correlation'] = correlation

            # Phase coherence (cross-correlation at lag 0)
            # Normalized to [-1, 1]
            features['rsp_phase_coherence'] = np.correlate(
                (thor_clean - thor_clean.mean()) / thor_clean.std(),
                (abdo_clean - abdo_clean.mean()) / abdo_clean.std(),
                mode='valid'
            )[0] / min_len

        # Thoracic dominance ratio
        # Normal: <1 (abdominal dominant), Stress: >1 (thoracic dominant)
        if 'RSP_Amplitude' in window_thor.columns and 'RSP_Amplitude' in window_abdo.columns:
            thor_amp = window_thor['RSP_Amplitude'].mean()
            abdo_amp = window_abdo['RSP_Amplitude'].mean()

            if abdo_amp > 0:
                features['rsp_thoracic_dominance'] = thor_amp / abdo_amp

            # Contribution of thoracic to total variance
            thor_var = window_thor['RSP_Amplitude'].var()
            abdo_var = window_abdo['RSP_Amplitude'].var()
            total_var = thor_var + abdo_var

            if total_var > 0:
                features['rsp_contribution_thoracic'] = thor_var / total_var

    except Exception as e:
        print(f"    Warning: RSP coordination calculation failed: {e}")

    return features


def calculate_bp_features_enhanced(
    bp_data: pd.DataFrame,
    window_start: float,
    window_end: float
) -> Dict[str, float]:
    """
    Calculate blood pressure features.

    Args:
        bp_data: DataFrame with BP processed data
        window_start: Start time in seconds
        window_end: End time in seconds

    Returns:
        Dictionary of BP features (~6 features)
    """
    # Filter data to window
    mask = (bp_data['Time'] >= window_start) & (bp_data['Time'] <= window_end)
    window_data = bp_data[mask]

    features = {
        'bp_mean': np.nan,
        'bp_std': np.nan,
        'bp_min': np.nan,
        'bp_max': np.nan,
        'bp_cv': np.nan,  # Coefficient of variation
        'bp_slope': np.nan,  # Trend over time
    }

    if len(window_data) == 0:
        return features

    # Find BP column
    bp_column = None
    for col in window_data.columns:
        if 'Clean' in col or 'Raw' in col:
            bp_column = col
            break

    if bp_column is None:
        return features

    bp_values = window_data[bp_column].dropna()
    if len(bp_values) > 0:
        features['bp_mean'] = bp_values.mean()
        features['bp_std'] = bp_values.std()
        features['bp_min'] = bp_values.min()
        features['bp_max'] = bp_values.max()

        # Coefficient of variation (relative variability)
        if features['bp_mean'] != 0:
            features['bp_cv'] = features['bp_std'] / abs(features['bp_mean'])

        # BP slope (rising BP = building stress response)
        if len(bp_values) > 2:
            try:
                time_vals = window_data.loc[bp_values.index, 'Time'].values
                slope, _, _, _, _ = linregress(time_vals, bp_values.values)
                features['bp_slope'] = slope
            except:
                pass

    return features


def extract_features_for_participant(
    participant_dir: Path,
    processed_signals_dir: Path,
    verbose: bool = False
) -> List[Dict]:
    """
    Extract enhanced features for all windows in a participant's visit.

    Returns:
        List of feature dictionaries (one per window)
    """
    all_features = []

    # Find ACQ files for this participant
    acq_files = list(participant_dir.glob('**/*.acq'))

    for acq_file in acq_files:
        if verbose:
            print(f"\nLoading: {acq_file.name}")

        try:
            # Determine participant ID from directory name
            participant_id = participant_dir.name

            # Determine visit type from filename
            visit_type = None
            if "TSST" in acq_file.name:
                visit_type = "TSST Visit"
            elif "PDST" in acq_file.name:
                visit_type = "PDST Visit"

            if visit_type is None:
                print(f"  Warning: Could not determine visit type")
                continue

            # Load ACQ file to get event markers
            acq, _, sampling_rate = load_acq_file(acq_file, verbose=False)

            # Create windows
            windows = create_windows_for_visit(
                visit_type=visit_type,
                acq=acq,
                sampling_rate=sampling_rate,
                verbose=verbose
            )

            if len(windows) == 0:
                continue

            # Find processed signal files
            # They should be in processed_signals_dir/participant_id/visit_type/Acqknowledge/neurokit_processed/
            processed_dir = processed_signals_dir / participant_id / visit_type / "Acqknowledge" / "neurokit_processed"

            if not processed_dir.exists():
                if verbose:
                    print(f"  Warning: No processed signals found at {processed_dir}")
                continue

            # Load processed signals
            ecg_files = list(processed_dir.glob('*ECG*_processed.csv'))
            eda_files = list(processed_dir.glob('*EDA*_processed.csv'))
            rsp_files = list(processed_dir.glob('*RSP*_processed.csv'))
            bp_files = list(processed_dir.glob('*Blood*_processed.csv'))

            # Load dataframes
            ecg_df = pd.read_csv(ecg_files[0]) if ecg_files else None
            eda_df = pd.read_csv(eda_files[0]) if eda_files else None
            bp_df = pd.read_csv(bp_files[0]) if bp_files else None

            # Load both RSP channels
            rsp_thoracic_df = None
            rsp_abdominal_df = None

            for rsp_file in rsp_files:
                rsp_df = pd.read_csv(rsp_file)
                # Determine which channel based on filename
                if '2208' in rsp_file.name or 'thoracic' in rsp_file.name.lower():
                    rsp_thoracic_df = rsp_df
                elif '2106' in rsp_file.name or 'abdominal' in rsp_file.name.lower():
                    rsp_abdominal_df = rsp_df
                else:
                    # If we don't know which is which, use first as thoracic
                    if rsp_thoracic_df is None:
                        rsp_thoracic_df = rsp_df
                    elif rsp_abdominal_df is None:
                        rsp_abdominal_df = rsp_df

            # Extract features for each window
            for window in windows:
                if window.start_time is None or window.end_time is None:
                    continue

                window_name = window.name
                start_time = window.start_time
                end_time = window.end_time

                if verbose:
                    print(f"  Extracting features: {window_name} ({start_time:.1f}s - {end_time:.1f}s)")

                features = {
                    'participant_id': participant_id,
                    'visit_type': visit_type,
                    'phase': window_name,
                    'window_start_time': start_time,
                    'window_end_time': end_time,
                    'window_duration': end_time - start_time,
                }

                # Extract HRV features (ENHANCED with frequency-domain!)
                if ecg_df is not None:
                    hrv_features = calculate_hrv_features_enhanced(ecg_df, start_time, end_time)
                    features.update(hrv_features)

                # Extract EDA features (ENHANCED with SCR dynamics!)
                if eda_df is not None:
                    eda_features = calculate_eda_features_enhanced(eda_df, start_time, end_time)
                    features.update(eda_features)

                # Extract RSP features for each channel
                if rsp_thoracic_df is not None:
                    rsp_thor_features = calculate_rsp_features_enhanced(
                        rsp_thoracic_df, start_time, end_time, channel_name='thoracic'
                    )
                    features.update(rsp_thor_features)

                if rsp_abdominal_df is not None:
                    rsp_abdo_features = calculate_rsp_features_enhanced(
                        rsp_abdominal_df, start_time, end_time, channel_name='abdominal'
                    )
                    features.update(rsp_abdo_features)

                # Extract RSP coordination features (NEW!)
                if rsp_thoracic_df is not None and rsp_abdominal_df is not None:
                    rsp_coord_features = calculate_rsp_coordination_features(
                        rsp_thoracic_df, rsp_abdominal_df, start_time, end_time
                    )
                    features.update(rsp_coord_features)

                # Extract BP features
                if bp_df is not None:
                    bp_features = calculate_bp_features_enhanced(bp_df, start_time, end_time)
                    features.update(bp_features)

                all_features.append(features)

        except Exception as e:
            print(f"Error processing {acq_file.name}: {e}")
            import traceback
            traceback.print_exc()
            continue

    return all_features


def main():
    parser = argparse.ArgumentParser(
        description="ENHANCED feature extraction with optimal stress biomarkers"
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all participants'
    )
    parser.add_argument(
        '--participant-id',
        help='Process specific participant ID'
    )
    parser.add_argument(
        '--data-dir',
        default='Participant Data',
        help='Directory containing participant ACQ files'
    )
    parser.add_argument(
        '--processed-dir',
        default='/scratch/sungchoi_root/sungchoi99/adityabn/processed_signals',
        help='Directory containing processed signal CSVs'
    )
    parser.add_argument(
        '-o', '--output',
        default='physiological_features_enhanced.csv',
        help='Output CSV file path'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    processed_dir = Path(args.processed_dir)

    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        return 1

    if not processed_dir.exists():
        print(f"Error: Processed signals directory not found: {processed_dir}")
        return 1

    print("\n" + "="*80)
    print("ENHANCED FEATURE EXTRACTION - Optimal Stress Biomarkers")
    print("="*80)
    print(f"\nFeature enhancements:")
    print("  ✓ HRV: Time + Frequency (LF/HF!) + Non-linear (SD1/SD2)")
    print("  ✓ EDA: Tonic + SCR dynamics (amplitude, rise/recovery time)")
    print("  ✓ RSP: Single channel + Thoracic-abdominal coordination")
    print("  ✓ BP: Stats + trend analysis")
    print(f"\nExpected ~60 features per window (vs. 28 in basic extraction)")
    print("="*80 + "\n")

    all_features = []

    if args.all:
        # Process all participants
        participant_dirs = [d for d in data_dir.iterdir() if d.is_dir() and d.name.isdigit()]
        print(f"Found {len(participant_dirs)} participant directories\n")

        for i, participant_dir in enumerate(participant_dirs, 1):
            print(f"[{i}/{len(participant_dirs)}] Processing {participant_dir.name}")
            features = extract_features_for_participant(participant_dir, processed_dir, args.verbose)
            all_features.extend(features)
            print(f"  Extracted {len(features)} windows")

    elif args.participant_id:
        # Process single participant
        participant_dir = data_dir / args.participant_id
        if not participant_dir.exists():
            print(f"Error: Participant directory not found: {participant_dir}")
            return 1

        print(f"Processing participant {args.participant_id}")
        features = extract_features_for_participant(participant_dir, processed_dir, args.verbose)
        all_features.extend(features)

    else:
        parser.print_help()
        return 1

    # Create DataFrame and save
    if all_features:
        df = pd.DataFrame(all_features)

        # Save to CSV
        output_path = Path(args.output)
        df.to_csv(output_path, index=False)

        print("\n" + "="*80)
        print("FEATURE EXTRACTION COMPLETE")
        print("="*80)
        print(f"Total windows: {len(df)}")
        print(f"Participants: {df['participant_id'].nunique()}")
        print(f"Visit types: {df['visit_type'].unique().tolist()}")
        print(f"Phases: {df['phase'].unique().tolist()}")
        print(f"Total features: {len(df.columns)}")
        print(f"\nOutput saved to: {output_path}")
        print("="*80 + "\n")

        # Show sample
        print("Sample of extracted features:")
        print(df.head(5).to_string())
    else:
        print("\nNo features extracted!")

    return 0


if __name__ == '__main__':
    sys.exit(main())
