#!/usr/bin/env python3
"""
Analyze processed test signals to verify signal quality and ranges.
Uses a subset of data for analysis due to file size.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def analyze_ecg_signal(file_path: Path, sample_rate: int = 2000):
    """Analyze processed ECG signal."""
    print(f"\nAnalyzing ECG: {file_path.name}")
    print("=" * 80)

    # Read file in chunks to avoid memory issues
    # Sample first 5 minutes of data (5 * 60 * sample_rate rows)
    sample_rows = 5 * 60 * sample_rate  # 600,000 rows = 5 minutes

    df = pd.read_csv(file_path, nrows=sample_rows)

    print(f"Data shape: {df.shape}")
    print(f"Duration: {df['Time'].max():.2f} seconds ({df['Time'].max()/60:.2f} minutes)")
    print(f"\nColumns: {list(df.columns)}")

    # Analyze ECG metrics
    print(f"\n{'='*80}")
    print("ECG SIGNAL ANALYSIS")
    print(f"{'='*80}")

    # Heart Rate
    hr_values = df['ECG_Rate'].dropna()
    print(f"\nHeart Rate (BPM):")
    print(f"  Mean: {hr_values.mean():.2f}")
    print(f"  Std:  {hr_values.std():.2f}")
    print(f"  Min:  {hr_values.min():.2f}")
    print(f"  Max:  {hr_values.max():.2f}")
    print(f"  Expected range: 40-180 BPM (normal: 60-100 BPM)")

    # Check if within expected range
    if hr_values.min() < 40 or hr_values.max() > 180:
        print(f"  ⚠️  WARNING: Heart rate outside typical range!")
    else:
        print(f"  ✓ Heart rate within expected range")

    # Signal Quality
    quality_values = df['ECG_Quality'].dropna()
    print(f"\nSignal Quality:")
    print(f"  Mean: {quality_values.mean():.3f}")
    print(f"  Min:  {quality_values.min():.3f}")
    print(f"  Max:  {quality_values.max():.3f}")
    print(f"  Expected: >0.5 is good, >0.8 is excellent")

    if quality_values.mean() > 0.8:
        print(f"  ✓ Excellent signal quality")
    elif quality_values.mean() > 0.5:
        print(f"  ✓ Good signal quality")
    else:
        print(f"  ⚠️  WARNING: Poor signal quality!")

    # Count R-peaks
    r_peaks = df['ECG_R_Peaks'].sum()
    duration_min = df['Time'].max() / 60
    expected_beats = duration_min * hr_values.mean()

    print(f"\nR-Peaks Detected:")
    print(f"  Count: {r_peaks}")
    print(f"  Expected (~{hr_values.mean():.1f} BPM * {duration_min:.2f} min): ~{expected_beats:.0f}")

    if abs(r_peaks - expected_beats) / expected_beats < 0.1:
        print(f"  ✓ R-peak count matches expected")
    else:
        print(f"  ⚠️  WARNING: R-peak count differs from expected")

    # Raw vs Clean signal
    print(f"\nRaw Signal:")
    print(f"  Mean: {df['ECG_Raw'].mean():.4f}")
    print(f"  Std:  {df['ECG_Raw'].std():.4f}")

    print(f"\nCleaned Signal:")
    print(f"  Mean: {df['ECG_Clean'].mean():.4f}")
    print(f"  Std:  {df['ECG_Clean'].std():.4f}")

    return df


def analyze_rsp_signal(file_path: Path, sample_rate: int = 2000):
    """Analyze processed RSP signal."""
    print(f"\n\nAnalyzing RSP: {file_path.name}")
    print("=" * 80)

    # Sample first 5 minutes
    sample_rows = 5 * 60 * sample_rate

    df = pd.read_csv(file_path, nrows=sample_rows)

    print(f"Data shape: {df.shape}")
    print(f"Duration: {df['Time'].max():.2f} seconds ({df['Time'].max()/60:.2f} minutes)")

    print(f"\n{'='*80}")
    print("RESPIRATORY SIGNAL ANALYSIS")
    print(f"{'='*80}")

    # Respiratory Rate
    rr_values = df['RSP_Rate'].dropna()
    print(f"\nRespiratory Rate (breaths/min):")
    print(f"  Mean: {rr_values.mean():.2f}")
    print(f"  Std:  {rr_values.std():.2f}")
    print(f"  Min:  {rr_values.min():.2f}")
    print(f"  Max:  {rr_values.max():.2f}")
    print(f"  Expected range: 8-40 breaths/min (normal: 12-20)")

    if rr_values.min() < 8 or rr_values.max() > 40:
        print(f"  ⚠️  WARNING: Respiratory rate outside typical range!")
    else:
        print(f"  ✓ Respiratory rate within expected range")

    # Amplitude
    amp_values = df['RSP_Amplitude'].dropna()
    print(f"\nRespiratory Amplitude:")
    print(f"  Mean: {amp_values.mean():.4f}")
    print(f"  Std:  {amp_values.std():.4f}")
    print(f"  Min:  {amp_values.min():.4f}")
    print(f"  Max:  {amp_values.max():.4f}")

    # Peaks
    peaks = df['RSP_Peaks'].sum()
    duration_min = df['Time'].max() / 60
    expected_breaths = duration_min * rr_values.mean()

    print(f"\nRespiratory Peaks Detected:")
    print(f"  Count: {peaks}")
    print(f"  Expected (~{rr_values.mean():.1f} br/min * {duration_min:.2f} min): ~{expected_breaths:.0f}")

    if abs(peaks - expected_breaths) / expected_breaths < 0.15:
        print(f"  ✓ Peak count matches expected")
    else:
        print(f"  ⚠️  WARNING: Peak count differs from expected")

    return df


def analyze_eda_signal(file_path: Path, sample_rate: int = 2000):
    """Analyze processed EDA signal."""
    print(f"\n\nAnalyzing EDA: {file_path.name}")
    print("=" * 80)

    # Sample first 5 minutes
    sample_rows = 5 * 60 * sample_rate

    df = pd.read_csv(file_path, nrows=sample_rows)

    print(f"Data shape: {df.shape}")
    print(f"Duration: {df['Time'].max():.2f} seconds ({df['Time'].max()/60:.2f} minutes)")

    print(f"\n{'='*80}")
    print("EDA SIGNAL ANALYSIS")
    print(f"{'='*80}")

    # Tonic (SCL)
    tonic_values = df['EDA_Tonic'].dropna()
    print(f"\nTonic Component (Skin Conductance Level - µS):")
    print(f"  Mean: {tonic_values.mean():.4f}")
    print(f"  Std:  {tonic_values.std():.4f}")
    print(f"  Min:  {tonic_values.min():.4f}")
    print(f"  Max:  {tonic_values.max():.4f}")
    print(f"  Expected range: 0-40 µS (typical: 2-20 µS)")

    if tonic_values.min() < 0 or tonic_values.max() > 40:
        print(f"  ⚠️  WARNING: EDA values outside typical range!")
    else:
        print(f"  ✓ EDA values within expected range")

    # Phasic (SCR)
    phasic_values = df['EDA_Phasic'].dropna()
    print(f"\nPhasic Component (Skin Conductance Response - µS):")
    print(f"  Mean: {phasic_values.mean():.4f}")
    print(f"  Std:  {phasic_values.std():.4f}")
    print(f"  Min:  {phasic_values.min():.4f}")
    print(f"  Max:  {phasic_values.max():.4f}")

    # Peaks (SCRs)
    scr_peaks = df['SCR_Peaks'].sum()
    duration_min = df['Time'].max() / 60

    print(f"\nSCR Peaks Detected:")
    print(f"  Count: {scr_peaks}")
    print(f"  Rate: {scr_peaks / duration_min:.2f} peaks/min")
    print(f"  Expected: 1-3 peaks/min (varies with arousal)")

    return df


def main():
    test_dir = Path("test_output/124961_TSST")

    if not test_dir.exists():
        print(f"Error: Test directory not found: {test_dir}")
        return

    print("\n" + "=" * 80)
    print("SIGNAL QUALITY ANALYSIS - Participant 124961 TSST")
    print("=" * 80)
    print(f"\nAnalyzing first 5 minutes of each signal...")

    # Find processed files
    ecg_file = list(test_dir.glob("*ECG*_processed.csv"))
    rsp_file = list(test_dir.glob("*RSP*_processed.csv"))
    eda_file = list(test_dir.glob("*EDA*_processed.csv"))

    # Analyze each signal type
    if ecg_file:
        analyze_ecg_signal(ecg_file[0])
    else:
        print("\n⚠️  No ECG file found")

    if rsp_file:
        analyze_rsp_signal(rsp_file[0])
    else:
        print("\n⚠️  No RSP file found")

    if eda_file:
        analyze_eda_signal(eda_file[0])
    else:
        print("\n⚠️  No EDA file found")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nKey Findings:")
    print("- Check that all values are within expected physiological ranges")
    print("- Verify peak counts match expected rates")
    print("- Confirm signal quality is good (>0.5) or excellent (>0.8)")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
