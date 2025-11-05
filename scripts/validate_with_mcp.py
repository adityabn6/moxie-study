#!/usr/bin/env python3
"""
Validate our processed signals using NeuroKit MCP tools.
This will help verify that our processing matches NeuroKit best practices.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

def extract_ecg_sample_for_validation(file_path: Path, duration_seconds: int = 300):
    """
    Extract ECG sample data for MCP tool validation.

    Args:
        file_path: Path to processed ECG CSV
        duration_seconds: Duration to extract (default 5 minutes)

    Returns:
        Dictionary with ECG signal and sampling rate
    """
    # Read the processed ECG data
    sample_rate = 2000
    sample_rows = duration_seconds * sample_rate

    df = pd.read_csv(file_path, nrows=sample_rows)

    # Extract the cleaned ECG signal
    ecg_signal = df['ECG_Clean'].values

    # Extract R-peaks (indices where ECG_R_Peaks == 1)
    r_peak_indices = df[df['ECG_R_Peaks'] == 1].index.values

    return {
        'ecg_signal': ecg_signal.tolist(),
        'sampling_rate': sample_rate,
        'r_peak_indices': r_peak_indices.tolist(),
        'duration': duration_seconds,
        'n_samples': len(ecg_signal),
        'n_peaks': len(r_peak_indices)
    }


def save_sample_for_analysis(data: dict, output_path: Path):
    """Save extracted data as JSON for analysis."""
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved sample data to: {output_path}")


def main():
    test_dir = Path("test_output/124961_TSST")
    output_dir = Path("test_output/mcp_validation")
    output_dir.mkdir(exist_ok=True)

    # Find ECG file
    ecg_files = list(test_dir.glob("*ECG*_processed.csv"))

    if not ecg_files:
        print("Error: No ECG file found")
        return

    ecg_file = ecg_files[0]
    print(f"Processing: {ecg_file}")

    # Extract 5-minute sample
    print("\nExtracting 5-minute ECG sample for validation...")
    sample_data = extract_ecg_sample_for_validation(ecg_file, duration_seconds=300)

    print(f"\nExtracted Data:")
    print(f"  Duration: {sample_data['duration']} seconds")
    print(f"  Samples: {sample_data['n_samples']}")
    print(f"  Sampling Rate: {sample_data['sampling_rate']} Hz")
    print(f"  R-Peaks: {sample_data['n_peaks']}")
    print(f"  Expected HR: ~{(sample_data['n_peaks'] / sample_data['duration']) * 60:.1f} BPM")

    # Save for potential further analysis
    output_file = output_dir / "ecg_sample_5min.json"
    save_sample_for_analysis(sample_data, output_file)

    print("\n" + "=" * 80)
    print("Next Steps:")
    print("=" * 80)
    print("This sample can be used with NeuroKit MCP tools to:")
    print("1. Verify R-peak detection accuracy")
    print("2. Compute HRV metrics and compare with our feature extraction")
    print("3. Check signal processing best practices")
    print("=" * 80)


if __name__ == "__main__":
    main()
