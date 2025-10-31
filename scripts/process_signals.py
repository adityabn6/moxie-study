#!/usr/bin/env python3
"""
Process physiological signals using NeuroKit2.

Uses the existing data_io.data_loader to load ACQ files, then applies
NeuroKit signal processing to clean, filter, and extract features from
ECG, RSP, Blood Pressure, and other channels.

Usage:
    python process_signals.py <acq_file_path> [options]
    python process_signals.py --all  # Process all files in sample_data
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_io.data_loader import load_and_prepare_session
from data_io.file_discovery import find_acq_files
from processing.neurokit_signals import process_biodata_channels


def process_single_file(
    acq_file_path: Path,
    output_dir: Optional[Path] = None,
    save_artifacts: bool = True,
    verbose: bool = True
):
    """
    Process a single ACQ file.

    Args:
        acq_file_path: Path to ACQ file
        output_dir: Directory to save processed outputs
        save_artifacts: Whether to save CSV and plots
        verbose: Print detailed information
    """
    print(f"\n{'='*80}")
    print(f"Processing: {acq_file_path.name}")
    print(f"{'='*80}")

    # Load ACQ file using existing data loader
    biodata, participant_id, visit_type = load_and_prepare_session(
        acq_file_path,
        verbose=verbose
    )

    # Set up output directory
    if output_dir is None:
        output_dir = acq_file_path.parent / "neurokit_processed"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Define channels to process
    # Pattern matching for channel names
    # This will match all channels that contain these strings
    channel_patterns = {
        'ecg': 'ECG',           # ECG signal
        'eda': 'EDA',           # Electrodermal Activity
        'rsp': 'RSP',           # Respiratory signals (will match both RSP channels)
        'bp': 'Blood Pressure'  # Non-invasive Blood Pressure (NIBP)
    }

    # Process channels
    print(f"\n{'='*80}")
    print("Processing Channels with NeuroKit2")
    print(f"{'='*80}")

    results = process_biodata_channels(
        biodata=biodata,
        channel_patterns=channel_patterns,
        output_dir=output_dir,
        save_artifacts=save_artifacts
    )

    # Summary
    print(f"\n{'='*80}")
    print("Processing Complete")
    print(f"{'='*80}")
    print(f"Participant: {participant_id}")
    print(f"Visit: {visit_type}")
    print(f"Channels processed: {len(results)}")
    print(f"Output directory: {output_dir}")
    print(f"{'='*80}\n")

    return results, biodata


def process_all_files(
    data_dir: Path,
    output_base_dir: Optional[Path] = None,
    save_artifacts: bool = True,
    verbose: bool = False
):
    """
    Process all ACQ files in a directory.

    Args:
        data_dir: Directory containing participant data
        output_base_dir: Base directory for outputs (uses data_dir if None)
        save_artifacts: Whether to save CSV and plots
        verbose: Print detailed information for each file
    """
    # Find all ACQ files
    acq_files = find_acq_files(str(data_dir))

    print(f"\nFound {len(acq_files)} ACQ files to process")

    # Process each file
    for i, acq_file in enumerate(acq_files, 1):
        print(f"\n[{i}/{len(acq_files)}]")

        # Set output directory based on participant/visit
        if output_base_dir:
            output_dir = Path(output_base_dir) / acq_file.parent.relative_to(data_dir) / "neurokit_processed"
        else:
            output_dir = acq_file.parent / "neurokit_processed"

        try:
            process_single_file(
                acq_file_path=acq_file,
                output_dir=output_dir,
                save_artifacts=save_artifacts,
                verbose=verbose
            )
        except Exception as e:
            print(f"ERROR processing {acq_file.name}: {e}")
            continue

    print(f"\n{'='*80}")
    print(f"Batch Processing Complete: {len(acq_files)} files")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process physiological signals using NeuroKit2"
    )
    parser.add_argument(
        "acq_file",
        nargs='?',
        help="Path to ACQ file (or use --all)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all ACQ files in sample_data"
    )
    parser.add_argument(
        "--data-dir",
        default="../sample_data/Participant Data",
        help="Directory containing participant data (used with --all)"
    )
    parser.add_argument(
        "-o", "--output-dir",
        help="Output directory for processed files"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save artifacts (CSV and plots)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed information"
    )

    args = parser.parse_args()

    if args.all:
        # Process all files
        data_dir = Path(args.data_dir)
        if not data_dir.exists():
            print(f"Error: Data directory not found: {data_dir}")
            sys.exit(1)

        process_all_files(
            data_dir=data_dir,
            output_base_dir=Path(args.output_dir) if args.output_dir else None,
            save_artifacts=not args.no_save,
            verbose=args.verbose
        )

    elif args.acq_file:
        # Process single file
        acq_file = Path(args.acq_file)
        if not acq_file.exists():
            print(f"Error: File not found: {acq_file}")
            sys.exit(1)

        process_single_file(
            acq_file_path=acq_file,
            output_dir=Path(args.output_dir) if args.output_dir else None,
            save_artifacts=not args.no_save,
            verbose=args.verbose
        )

    else:
        parser.print_help()
        sys.exit(1)
