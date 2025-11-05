#!/usr/bin/env python3
"""
Process physiological signals using NeuroKit2.

Uses the existing data_io.data_loader to load ACQ files, then applies
NeuroKit signal processing to clean, filter, and extract features from
ECG, RSP, Blood Pressure, and other channels.

Supports incremental processing - tracks which files have been processed
and skips them on subsequent runs (similar to quality_check.py).

Usage:
    python process_signals.py <acq_file_path> [options]
    python process_signals.py --all  # Process all files in data directory
    python process_signals.py --all --force  # Force reprocess all files
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
from core.processing_tracker import ProcessingTracker


def process_single_file(
    acq_file_path: Path,
    output_dir: Optional[Path] = None,
    save_artifacts: bool = True,
    verbose: bool = True,
    tracker: Optional[ProcessingTracker] = None
):
    """
    Process a single ACQ file.

    Args:
        acq_file_path: Path to ACQ file
        output_dir: Directory to save processed outputs
        save_artifacts: Whether to save CSV and plots
        verbose: Print detailed information
        tracker: Processing tracker for incremental processing (optional)

    Returns:
        Tuple of (results, biodata, success)
    """
    print(f"\n{'='*80}")
    print(f"Processing: {acq_file_path.name}")
    print(f"{'='*80}")

    # Load ACQ file using existing data loader
    try:
        biodata, participant_id, visit_type = load_and_prepare_session(
            acq_file_path,
            verbose=verbose
        )
    except Exception as e:
        print(f"ERROR loading file: {e}")
        if tracker:
            tracker.mark_processed(
                acq_file_path,
                participant_id="unknown",
                visit_type="unknown",
                success=False,
                error_message=str(e)
            )
        return None, None, False

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

    try:
        results = process_biodata_channels(
            biodata=biodata,
            channel_patterns=channel_patterns,
            output_dir=output_dir,
            save_artifacts=save_artifacts
        )

        success = True
        error_message = None

    except Exception as e:
        print(f"\nERROR processing channels: {e}")
        results = {}
        success = False
        error_message = str(e)

    # Mark as processed if tracker is provided
    if tracker:
        signal_summary = {
            'channels_processed': len(results),
            'channel_names': list(results.keys())
        }
        tracker.mark_processed(
            acq_file_path,
            participant_id=participant_id,
            visit_type=visit_type,
            success=success,
            quality_summary=signal_summary,
            error_message=error_message
        )

    # Summary
    print(f"\n{'='*80}")
    print("Processing Complete" if success else "Processing Failed")
    print(f"{'='*80}")
    print(f"Participant: {participant_id}")
    print(f"Visit: {visit_type}")
    print(f"Channels processed: {len(results)}")
    if output_dir:
        print(f"Output directory: {output_dir}")
    print(f"{'='*80}\n")

    return results, biodata, success


def process_all_files(
    data_dir: Path,
    output_base_dir: Optional[Path] = None,
    save_artifacts: bool = True,
    verbose: bool = False,
    force: bool = False,
    tracker: Optional[ProcessingTracker] = None
):
    """
    Process all ACQ files in a directory with incremental processing support.

    Args:
        data_dir: Directory containing participant data
        output_base_dir: Base directory for outputs (uses data_dir if None)
        save_artifacts: Whether to save CSV and plots
        verbose: Print detailed information for each file
        force: Force reprocess all files (ignore tracking)
        tracker: Processing tracker for incremental processing (optional)
    """
    # Find all ACQ files
    all_acq_files = find_acq_files(str(data_dir))

    print(f"\nFound {len(all_acq_files)} ACQ files")

    # Filter to unprocessed files if tracker is provided and not forcing
    if tracker and not force:
        acq_files = tracker.get_unprocessed_files(all_acq_files)
        skipped = len(all_acq_files) - len(acq_files)

        print(f"Skipping {skipped} already-processed files")
        print(f"Processing {len(acq_files)} new/changed files")

        if len(acq_files) == 0:
            print("\n✓ All files already processed!")
            print("  Use --force to reprocess everything")
            print("  Use --clear-participant ID to reprocess specific participant")
            return
    else:
        acq_files = all_acq_files
        if force:
            print("Force mode: reprocessing all files")

    # Track statistics
    successful = 0
    failed = 0

    # Process each file
    for i, acq_file in enumerate(acq_files, 1):
        print(f"\n[{i}/{len(acq_files)}]")

        # Set output directory based on participant/visit
        if output_base_dir:
            # Convert to absolute paths for relative_to() to work
            acq_file_abs = acq_file.resolve()
            data_dir_abs = data_dir.resolve()
            output_dir = Path(output_base_dir) / acq_file_abs.parent.relative_to(data_dir_abs) / "neurokit_processed"
        else:
            output_dir = acq_file.parent / "neurokit_processed"

        results, biodata, success = process_single_file(
            acq_file_path=acq_file,
            output_dir=output_dir,
            save_artifacts=save_artifacts,
            verbose=verbose,
            tracker=tracker
        )

        if success:
            successful += 1
        else:
            failed += 1

    # Final summary
    print(f"\n{'='*80}")
    print(f"Batch Processing Complete")
    print(f"{'='*80}")
    print(f"Total files: {len(acq_files)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")

    if tracker:
        print(f"\nProcessing log saved to: {tracker.tracker_file}")
        tracker.print_summary()

    print(f"{'='*80}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process physiological signals using NeuroKit2 with incremental processing support"
    )
    parser.add_argument(
        "acq_file",
        nargs='?',
        help="Path to ACQ file (or use --all)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all ACQ files in data directory"
    )
    parser.add_argument(
        "--data-dir",
        default="Participant Data",
        help="Directory containing participant data (used with --all, default: Participant Data)"
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
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reprocess all files (ignore processing history)"
    )
    parser.add_argument(
        "--clear-participant",
        metavar="ID",
        help="Clear processing history for specific participant ID"
    )
    parser.add_argument(
        "--clear-all",
        action="store_true",
        help="Clear all processing history (force reprocess on next run)"
    )

    args = parser.parse_args()

    # Initialize processing tracker for batch processing
    tracker = None
    if args.all:
        data_dir = Path(args.data_dir)
        if not data_dir.exists():
            print(f"Error: Data directory not found: {data_dir}")
            sys.exit(1)

        # Set up tracker file
        if args.output_dir:
            tracker_file = Path(args.output_dir) / ".signal_processing_log.json"
        else:
            tracker_file = data_dir / ".signal_processing_log.json"

        tracker = ProcessingTracker(tracker_file)

        # Handle clear operations
        if args.clear_all:
            print("Clearing all processing history...")
            tracker.clear_all()
            print("Done. Exiting.")
            sys.exit(0)

        if args.clear_participant:
            print(f"Clearing processing history for participant {args.clear_participant}...")
            tracker.clear_participant(args.clear_participant)
            print("Done. Run without --clear-participant to process.")
            sys.exit(0)

        # Process all files with tracker
        process_all_files(
            data_dir=data_dir,
            output_base_dir=Path(args.output_dir) if args.output_dir else None,
            save_artifacts=not args.no_save,
            verbose=args.verbose,
            force=args.force,
            tracker=tracker
        )

    elif args.acq_file:
        # Process single file (no tracking for single files)
        acq_file = Path(args.acq_file)
        if not acq_file.exists():
            print(f"Error: File not found: {acq_file}")
            sys.exit(1)

        process_single_file(
            acq_file_path=acq_file,
            output_dir=Path(args.output_dir) if args.output_dir else None,
            save_artifacts=not args.no_save,
            verbose=args.verbose,
            tracker=None  # No tracking for single file processing
        )

    else:
        parser.print_help()
        sys.exit(1)
