#!/usr/bin/env python3
"""
Compare our HRV feature extraction with NeuroKit MCP tool calculations.
This validates our processing pipeline against NeuroKit best practices.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

def load_processed_ecg_sample(file_path: Path, duration_seconds: int = 300):
    """Load a sample of processed ECG data."""
    sample_rate = 2000
    sample_rows = duration_seconds * sample_rate

    df = pd.read_csv(file_path, nrows=sample_rows)

    # Extract ECG clean signal
    ecg_clean = df['ECG_Clean'].values

    return ecg_clean, sample_rate


def main():
    test_dir = Path("test_output/124961_TSST")

    # Find ECG file
    ecg_files = list(test_dir.glob("*ECG*_processed.csv"))

    if not ecg_files:
        print("Error: No ECG file found")
        return

    ecg_file = ecg_files[0]
    print(f"Loading ECG data from: {ecg_file.name}")

    # Load 5-minute sample
    ecg_signal, sampling_rate = load_processed_ecg_sample(ecg_file, duration_seconds=300)

    print(f"\nLoaded {len(ecg_signal)} samples at {sampling_rate} Hz")
    print(f"Duration: {len(ecg_signal) / sampling_rate:.2f} seconds")

    # Save signal array to numpy file for easier loading
    output_dir = Path("test_output/mcp_validation")
    output_dir.mkdir(exist_ok=True)

    np.save(output_dir / "ecg_clean_signal.npy", ecg_signal)
    print(f"\nSaved ECG signal to: {output_dir / 'ecg_clean_signal.npy'}")

    # Also save sampling rate
    with open(output_dir / "metadata.json", 'w') as f:
        json.dump({
            'sampling_rate': sampling_rate,
            'duration_seconds': len(ecg_signal) / sampling_rate,
            'n_samples': len(ecg_signal)
        }, f, indent=2)

    print(f"Saved metadata to: {output_dir / 'metadata.json'}")

    print("\n" + "=" * 80)
    print("Ready for MCP tool validation")
    print("=" * 80)
    print("\nNext: Use NeuroKit MCP tools to:")
    print("1. Extract R-peaks from this signal")
    print("2. Compute HRV metrics (RMSSD, SDNN, pNN50, etc.)")
    print("3. Compare with our extracted features")


if __name__ == "__main__":
    main()
