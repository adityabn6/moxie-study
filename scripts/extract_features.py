#!/usr/bin/env python3
"""
Extract aggregated features from processed physiological signals for each protocol phase.

This script:
1. Loads ACQ files to get time windows (event markers) for each protocol phase
2. Loads processed signal CSVs
3. Extracts features (HRV, RSP, EDA, BP) for each time window
4. Outputs a CSV file suitable for regression analysis in R

Features extracted:
- HRV: RMSSD, SDNN, pNN50, mean HR, min/max HR, HF/LF power
- RSP: mean rate, rate variability, mean amplitude
- EDA: mean, std, num peaks
- BP: mean, std, min, max

Usage:
    python extract_features.py --all  # Process all participants
    python extract_features.py --participant-id 124874  # Single participant
"""

import argparse
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_io.data_loader import load_acq_file, create_windows_for_visit
from data_io.file_discovery import find_acq_files


def calculate_hrv_features(ecg_data: pd.DataFrame, window_start: float, window_end: float) -> Dict[str, float]:
    """
    Calculate HRV features from ECG data within a time window.

    Args:
        ecg_data: DataFrame with ECG processed data (columns: Time, ECG_R_Peaks, ECG_Rate, etc.)
        window_start: Start time in seconds
        window_end: End time in seconds

    Returns:
        Dictionary of HRV features
    """
    features = {}

    # Filter data to window
    mask = (ecg_data['Time'] >= window_start) & (ecg_data['Time'] <= window_end)
    window_data = ecg_data[mask]

    if len(window_data) == 0:
        return {
            'hrv_mean_hr': np.nan,
            'hrv_std_hr': np.nan,
            'hrv_min_hr': np.nan,
            'hrv_max_hr': np.nan,
            'hrv_rmssd': np.nan,
            'hrv_sdnn': np.nan,
            'hrv_pnn50': np.nan,
            'hrv_num_beats': np.nan
        }

    # Heart rate features
    heart_rate = window_data['ECG_Rate'].dropna()
    if len(heart_rate) > 0:
        features['hrv_mean_hr'] = heart_rate.mean()
        features['hrv_std_hr'] = heart_rate.std()
        features['hrv_min_hr'] = heart_rate.min()
        features['hrv_max_hr'] = heart_rate.max()
    else:
        features['hrv_mean_hr'] = np.nan
        features['hrv_std_hr'] = np.nan
        features['hrv_min_hr'] = np.nan
        features['hrv_max_hr'] = np.nan

    # R-peak based features (for RMSSD, SDNN, pNN50)
    r_peaks = window_data[window_data['ECG_R_Peaks'] == 1]

    if len(r_peaks) >= 2:
        # Get RR intervals (in milliseconds)
        rr_intervals = np.diff(r_peaks['Time'].values) * 1000  # Convert to ms

        features['hrv_num_beats'] = len(r_peaks)

        if len(rr_intervals) >= 2:
            # RMSSD: Root mean square of successive differences
            successive_diffs = np.diff(rr_intervals)
            features['hrv_rmssd'] = np.sqrt(np.mean(successive_diffs ** 2))

            # SDNN: Standard deviation of NN intervals
            features['hrv_sdnn'] = np.std(rr_intervals, ddof=1)

            # pNN50: Percentage of successive RR intervals that differ by more than 50 ms
            nn50 = np.sum(np.abs(successive_diffs) > 50)
            features['hrv_pnn50'] = (nn50 / len(successive_diffs)) * 100
        else:
            features['hrv_rmssd'] = np.nan
            features['hrv_sdnn'] = np.nan
            features['hrv_pnn50'] = np.nan
    else:
        features['hrv_num_beats'] = 0
        features['hrv_rmssd'] = np.nan
        features['hrv_sdnn'] = np.nan
        features['hrv_pnn50'] = np.nan

    return features


def calculate_rsp_features(rsp_data: pd.DataFrame, window_start: float, window_end: float) -> Dict[str, float]:
    """
    Calculate respiratory features from RSP data within a time window.

    Args:
        rsp_data: DataFrame with RSP processed data
        window_start: Start time in seconds
        window_end: End time in seconds

    Returns:
        Dictionary of RSP features
    """
    features = {}

    # Filter data to window
    mask = (rsp_data['Time'] >= window_start) & (rsp_data['Time'] <= window_end)
    window_data = rsp_data[mask]

    if len(window_data) == 0:
        return {
            'rsp_mean_rate': np.nan,
            'rsp_std_rate': np.nan,
            'rsp_mean_amplitude': np.nan,
            'rsp_std_amplitude': np.nan,
            'rsp_num_breaths': np.nan
        }

    # Respiratory rate
    rate = window_data['RSP_Rate'].dropna()
    if len(rate) > 0:
        features['rsp_mean_rate'] = rate.mean()
        features['rsp_std_rate'] = rate.std()
    else:
        features['rsp_mean_rate'] = np.nan
        features['rsp_std_rate'] = np.nan

    # Respiratory amplitude
    amplitude = window_data['RSP_Amplitude'].dropna()
    if len(amplitude) > 0:
        features['rsp_mean_amplitude'] = amplitude.mean()
        features['rsp_std_amplitude'] = amplitude.std()
    else:
        features['rsp_mean_amplitude'] = np.nan
        features['rsp_std_amplitude'] = np.nan

    # Number of breaths (count peaks)
    peaks = window_data[window_data['RSP_Peaks'] == 1]
    features['rsp_num_breaths'] = len(peaks)

    return features


def calculate_eda_features(eda_data: pd.DataFrame, window_start: float, window_end: float) -> Dict[str, float]:
    """
    Calculate EDA features from EDA data within a time window.

    Args:
        eda_data: DataFrame with EDA processed data
        window_start: Start time in seconds
        window_end: End time in seconds

    Returns:
        Dictionary of EDA features
    """
    features = {}

    # Filter data to window
    mask = (eda_data['Time'] >= window_start) & (eda_data['Time'] <= window_end)
    window_data = eda_data[mask]

    if len(window_data) == 0 or 'EDA_Clean' not in window_data.columns:
        return {
            'eda_mean': np.nan,
            'eda_std': np.nan,
            'eda_min': np.nan,
            'eda_max': np.nan,
            'eda_num_peaks': np.nan
        }

    # EDA level features
    eda_clean = window_data['EDA_Clean'].dropna()
    if len(eda_clean) > 0:
        features['eda_mean'] = eda_clean.mean()
        features['eda_std'] = eda_clean.std()
        features['eda_min'] = eda_clean.min()
        features['eda_max'] = eda_clean.max()
    else:
        features['eda_mean'] = np.nan
        features['eda_std'] = np.nan
        features['eda_min'] = np.nan
        features['eda_max'] = np.nan

    # Number of SCR peaks
    if 'EDA_Peaks' in window_data.columns:
        peaks = window_data[window_data['EDA_Peaks'] == 1]
        features['eda_num_peaks'] = len(peaks)
    else:
        features['eda_num_peaks'] = np.nan

    return features


def calculate_bp_features(bp_data: pd.DataFrame, window_start: float, window_end: float) -> Dict[str, float]:
    """
    Calculate blood pressure features from BP data within a time window.

    Args:
        bp_data: DataFrame with BP processed data
        window_start: Start time in seconds
        window_end: End time in seconds

    Returns:
        Dictionary of BP features
    """
    features = {}

    # Filter data to window
    mask = (bp_data['Time'] >= window_start) & (bp_data['Time'] <= window_end)
    window_data = bp_data[mask]

    if len(window_data) == 0:
        return {
            'bp_mean': np.nan,
            'bp_std': np.nan,
            'bp_min': np.nan,
            'bp_max': np.nan
        }

    # Determine which column to use (could be different names)
    bp_column = None
    for col in window_data.columns:
        if 'Clean' in col or 'Raw' in col:
            bp_column = col
            break

    if bp_column is None:
        return {
            'bp_mean': np.nan,
            'bp_std': np.nan,
            'bp_min': np.nan,
            'bp_max': np.nan
        }

    bp_clean = window_data[bp_column].dropna()
    if len(bp_clean) > 0:
        features['bp_mean'] = bp_clean.mean()
        features['bp_std'] = bp_clean.std()
        features['bp_min'] = bp_clean.min()
        features['bp_max'] = bp_clean.max()
    else:
        features['bp_mean'] = np.nan
        features['bp_std'] = np.nan
        features['bp_min'] = np.nan
        features['bp_max'] = np.nan

    return features


def load_processed_signal(processed_dir: Path, signal_pattern: str) -> Optional[pd.DataFrame]:
    """
    Load a processed signal CSV file.

    Args:
        processed_dir: Directory containing processed signal files
        signal_pattern: Pattern to match signal filename (e.g., 'ECG', 'RSP')

    Returns:
        DataFrame with processed signal data, or None if not found
    """
    # Find matching files
    matching_files = list(processed_dir.glob(f'*{signal_pattern}*_processed.csv'))

    if not matching_files:
        return None

    # Load the first matching file
    try:
        df = pd.read_csv(matching_files[0])
        return df
    except Exception as e:
        print(f"  Warning: Could not load {matching_files[0]}: {e}")
        return None


def extract_features_for_session(
    acq_file_path: Path,
    processed_base_dir: Path,
    verbose: bool = False
) -> List[Dict]:
    """
    Extract features for all windows in a single ACQ session.

    Args:
        acq_file_path: Path to original ACQ file (for event markers)
        processed_base_dir: Base directory containing processed signals
        verbose: Print detailed information

    Returns:
        List of feature dictionaries (one per window)
    """
    if verbose:
        print(f"\n{'='*80}")
        print(f"Extracting features: {acq_file_path.name}")
        print(f"{'='*80}")

    # Extract metadata from path
    parts = acq_file_path.parts
    participant_id = parts[-4] if len(parts) >= 4 else "unknown"

    # Determine visit type
    visit_type = None
    for part in parts:
        if "TSST" in part:
            visit_type = "TSST Visit"
        elif "PDST" in part:
            visit_type = "PDST Visit"

    if visit_type is None:
        print(f"  Warning: Could not determine visit type for {acq_file_path}")
        return []

    # Load ACQ file for event markers
    try:
        acq, _, sampling_rate = load_acq_file(acq_file_path, verbose=False)
    except Exception as e:
        print(f"  Error loading ACQ file: {e}")
        return []

    # Create windows
    windows = create_windows_for_visit(
        visit_type=visit_type,
        acq=acq,
        sampling_rate=sampling_rate,
        verbose=verbose
    )

    # Construct path to processed signals
    # Path structure: processed_base_dir / participant_id / visit_type / Acqknowledge / neurokit_processed
    processed_dir = processed_base_dir / participant_id / visit_type / "Acqknowledge" / "neurokit_processed"

    if not processed_dir.exists():
        print(f"  Warning: Processed signals directory not found: {processed_dir}")
        return []

    if verbose:
        print(f"  Loading processed signals from: {processed_dir}")

    # Load processed signals
    ecg_data = load_processed_signal(processed_dir, 'ECG')
    rsp1_data = load_processed_signal(processed_dir, 'RSP2208000207')  # RSP1
    rsp2_data = load_processed_signal(processed_dir, 'RSP2106000165')  # RSP2
    eda_data = load_processed_signal(processed_dir, 'EDA')
    bp_data = load_processed_signal(processed_dir, 'Blood Pressure')

    # Use RSP1 if available, otherwise RSP2
    rsp_data = rsp1_data if rsp1_data is not None else rsp2_data

    # Extract features for each window
    all_features = []

    for window in windows:
        if not window.is_valid():
            if verbose:
                print(f"  Skipping invalid window: {window.name}")
            continue

        if verbose:
            print(f"\n  Window: {window.name} ({window.start_time:.2f}s - {window.end_time:.2f}s)")

        # Initialize feature dict
        features = {
            'participant_id': participant_id,
            'visit_type': visit_type,
            'phase': window.name,
            'window_start_time': window.start_time,
            'window_end_time': window.end_time,
            'window_duration': window.get_duration()
        }

        # Extract ECG/HRV features
        if ecg_data is not None:
            hrv_features = calculate_hrv_features(ecg_data, window.start_time, window.end_time)
            features.update(hrv_features)
            if verbose:
                print(f"    HRV: mean_hr={hrv_features.get('hrv_mean_hr', np.nan):.1f}, "
                      f"rmssd={hrv_features.get('hrv_rmssd', np.nan):.1f}")

        # Extract RSP features
        if rsp_data is not None:
            rsp_features = calculate_rsp_features(rsp_data, window.start_time, window.end_time)
            features.update(rsp_features)
            if verbose:
                print(f"    RSP: mean_rate={rsp_features.get('rsp_mean_rate', np.nan):.1f}")

        # Extract EDA features
        if eda_data is not None:
            eda_features = calculate_eda_features(eda_data, window.start_time, window.end_time)
            features.update(eda_features)
            if verbose:
                print(f"    EDA: mean={eda_features.get('eda_mean', np.nan):.2f}")

        # Extract BP features
        if bp_data is not None:
            bp_features = calculate_bp_features(bp_data, window.start_time, window.end_time)
            features.update(bp_features)
            if verbose:
                print(f"    BP: mean={bp_features.get('bp_mean', np.nan):.1f}")

        all_features.append(features)

    return all_features


def process_all_sessions(
    data_dir: Path,
    processed_base_dir: Path,
    output_file: Path,
    verbose: bool = False
):
    """
    Process all ACQ sessions and extract features.

    Args:
        data_dir: Directory containing participant ACQ files
        processed_base_dir: Base directory containing processed signals
        output_file: Path to output CSV file
        verbose: Print detailed information
    """
    # Find all ACQ files
    all_acq_files = find_acq_files(str(data_dir))

    print(f"\nFound {len(all_acq_files)} ACQ files")
    print(f"Processed signals directory: {processed_base_dir}")
    print(f"Output file: {output_file}")

    all_features = []

    # Process each file
    for i, acq_file in enumerate(all_acq_files, 1):
        print(f"\n[{i}/{len(all_acq_files)}] {acq_file.name}")

        try:
            features = extract_features_for_session(
                acq_file_path=acq_file,
                processed_base_dir=processed_base_dir,
                verbose=verbose
            )
            all_features.extend(features)
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()

    # Convert to DataFrame and save
    if all_features:
        df = pd.DataFrame(all_features)

        # Reorder columns for better readability
        id_cols = ['participant_id', 'visit_type', 'phase', 'window_start_time', 'window_end_time', 'window_duration']
        feature_cols = [col for col in df.columns if col not in id_cols]
        df = df[id_cols + sorted(feature_cols)]

        # Save to CSV
        output_file.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_file, index=False)

        print(f"\n{'='*80}")
        print(f"Feature Extraction Complete")
        print(f"{'='*80}")
        print(f"Total windows processed: {len(df)}")
        print(f"Participants: {df['participant_id'].nunique()}")
        print(f"Visit types: {df['visit_type'].unique().tolist()}")
        print(f"Phases: {df['phase'].unique().tolist()}")
        print(f"\nOutput saved to: {output_file}")
        print(f"{'='*80}\n")

        # Display sample
        print("\nSample of extracted features:")
        print(df.head(10).to_string())
    else:
        print("\nNo features extracted!")


def process_single_participant(
    participant_id: str,
    data_dir: Path,
    processed_base_dir: Path,
    output_file: Path,
    verbose: bool = True
):
    """
    Process a single participant and extract features.

    Args:
        participant_id: Participant ID
        data_dir: Directory containing participant ACQ files
        processed_base_dir: Base directory containing processed signals
        output_file: Path to output CSV file
        verbose: Print detailed information
    """
    # Find ACQ files for this participant
    all_acq_files = find_acq_files(str(data_dir))
    participant_files = [f for f in all_acq_files if participant_id in str(f)]

    if not participant_files:
        print(f"No ACQ files found for participant {participant_id}")
        return

    print(f"\nFound {len(participant_files)} ACQ files for participant {participant_id}")

    all_features = []

    for acq_file in participant_files:
        features = extract_features_for_session(
            acq_file_path=acq_file,
            processed_base_dir=processed_base_dir,
            verbose=verbose
        )
        all_features.extend(features)

    # Convert to DataFrame and save
    if all_features:
        df = pd.DataFrame(all_features)

        # Reorder columns
        id_cols = ['participant_id', 'visit_type', 'phase', 'window_start_time', 'window_end_time', 'window_duration']
        feature_cols = [col for col in df.columns if col not in id_cols]
        df = df[id_cols + sorted(feature_cols)]

        # Save
        output_file.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_file, index=False)

        print(f"\n{'='*80}")
        print(f"Feature Extraction Complete for {participant_id}")
        print(f"{'='*80}")
        print(f"Total windows processed: {len(df)}")
        print(f"\nOutput saved to: {output_file}")
        print(f"{'='*80}\n")

        print(df.to_string())
    else:
        print("\nNo features extracted!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract aggregated features from processed physiological signals"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all participants"
    )
    parser.add_argument(
        "--participant-id",
        help="Process single participant by ID"
    )
    parser.add_argument(
        "--data-dir",
        default="Participant Data",
        help="Directory containing participant ACQ files (default: Participant Data)"
    )
    parser.add_argument(
        "--processed-dir",
        default="/scratch/sungchoi_root/sungchoi99/adityabn/processed_signals",
        help="Directory containing processed signals"
    )
    parser.add_argument(
        "-o", "--output",
        default="extracted_features.csv",
        help="Output CSV file (default: extracted_features.csv)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed information"
    )

    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    processed_dir = Path(args.processed_dir)
    output_file = Path(args.output)

    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        sys.exit(1)

    if not processed_dir.exists():
        print(f"Error: Processed signals directory not found: {processed_dir}")
        sys.exit(1)

    if args.all:
        process_all_sessions(
            data_dir=data_dir,
            processed_base_dir=processed_dir,
            output_file=output_file,
            verbose=args.verbose
        )
    elif args.participant_id:
        process_single_participant(
            participant_id=args.participant_id,
            data_dir=data_dir,
            processed_base_dir=processed_dir,
            output_file=output_file,
            verbose=args.verbose
        )
    else:
        parser.print_help()
        sys.exit(1)
