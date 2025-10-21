#!/usr/bin/env python3
"""
MOXIE Quality Check Script

Processes ACQ files and generates quality assessment reports with visualizations.
This script:
1. Discovers all ACQ files in the data directory
2. Loads each file and creates BioData objects
3. Computes SNR and amplitude quality metrics
4. Generates interactive Bokeh visualizations
5. Creates quality assessment reports
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config import DEFAULT_CHANNELS, QUALITY_CHECK_PARAMS
from core.processing_tracker import ProcessingTracker
from data_io.file_discovery import find_acq_files, get_participant_info
from data_io.data_loader import load_and_prepare_session
from quality.snr import compute_and_append_snr
from quality.amplitude import compute_and_append_amplitude
from quality.report import generate_quality_report
from visualization.bokeh_plots import save_bokeh_plot


def process_single_file(
    file_path: Path,
    output_base_dir: Path,
    tracker: ProcessingTracker = None,
    channels: list = None,
    verbose: bool = True
):
    """
    Process a single ACQ file with quality checks.

    Args:
        file_path: Path to ACQ file
        output_base_dir: Base directory for outputs
        tracker: Processing tracker (optional)
        channels: List of channels to process (uses defaults if None)
        verbose: Print detailed information
    """
    if channels is None:
        channels = DEFAULT_CHANNELS

    print(f"\n{'='*80}")
    print(f"Processing: {file_path.name}")
    print(f"{'='*80}")

    # Load data and create BioData
    biodata, participant_id, visit_type = load_and_prepare_session(
        file_path,
        verbose=verbose
    )

    # Get quality check parameters
    window_size = QUALITY_CHECK_PARAMS["window_size_seconds"]
    overlap = QUALITY_CHECK_PARAMS["overlap_seconds"]
    alpha = QUALITY_CHECK_PARAMS["snr_alpha_threshold"]
    beta = QUALITY_CHECK_PARAMS["amplitude_beta"]

    print(f"\n--- Quality Assessment ---")
    print(f"Window size: {window_size}s, Overlap: {overlap}s")
    print(f"SNR threshold: {alpha}, Amplitude beta: {beta}\n")

    # Compute quality metrics for each channel
    successful_channels = []
    for channel in channels:
        if channel not in biodata.ChannelNames:
            print(f"⚠ Channel '{channel}' not found, skipping...")
            continue

        try:
            # Compute SNR
            compute_and_append_snr(
                biodata=biodata,
                channel_name=channel,
                fs=biodata.Data[0].sampling_rate,  # Assume all same rate
                window_size_sec=window_size,
                overlap_sec=overlap,
                alpha=alpha
            )

            # Compute amplitude
            compute_and_append_amplitude(
                biodata=biodata,
                channel_name=channel,
                fs=biodata.Data[0].sampling_rate,
                window_size_sec=window_size,
                overlap_sec=overlap,
                beta=beta
            )

            successful_channels.append(channel)
            print()

        except Exception as e:
            print(f"✗ Error processing {channel}: {e}\n")
            continue

    # Generate quality report
    visit_short = "TSST" if "TSST" in visit_type else "PDST"
    output_dir = output_base_dir / participant_id / visit_short
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "quality_report.json"
    quality_metrics = generate_quality_report(
        biodata=biodata,
        channels=successful_channels,
        participant_id=participant_id,
        visit_type=visit_type,
        output_path=report_path
    )

    # Generate visualizations
    print(f"--- Generating Visualizations ---\n")

    # Calculate sampling rate for quality metrics
    quality_sampling_rate = 1 / (window_size - overlap)

    for channel in successful_channels:
        try:
            safe_name = channel.replace(" ", "_").replace(",", "")
            html_file = output_dir / f"{safe_name}.html"

            save_bokeh_plot(
                biodata=biodata,
                filename=str(html_file),
                sampling_rates=[20, quality_sampling_rate, quality_sampling_rate],
                channel_names=[
                    channel,
                    f"{channel}_SNR",
                    f"{channel}_Amplitude"
                ]
            )

        except Exception as e:
            print(f"  ✗ Error creating plot for {channel}: {e}")

    print(f"\n{'='*80}")
    print(f"Completed: {participant_id} - {visit_type}")
    print(f"Output directory: {output_dir}")
    print(f"{'='*80}\n")

    # Mark as successfully processed in tracker
    if tracker:
        # Create quality summary for tracking
        quality_summary = {
            ch: {
                'overall_quality': quality_metrics[ch].overall_quality,
                'snr_flagged_pct': quality_metrics[ch].snr_stats['percentage_flagged'] if quality_metrics[ch].snr_stats else None,
                'amp_flagged_pct': quality_metrics[ch].amplitude_stats['percentage_flagged'] if quality_metrics[ch].amplitude_stats else None
            }
            for ch in quality_metrics
        }

        tracker.mark_processed(
            file_path=file_path,
            participant_id=participant_id,
            visit_type=visit_type,
            success=True,
            quality_summary=quality_summary
        )


def main(
    data_dir: str,
    output_dir: str,
    force: bool = False,
    clear_participant: str = None,
    clear_all: bool = False,
    verbose: bool = False
):
    """
    Main processing function with incremental processing support.

    Args:
        data_dir: Directory containing participant data
        output_dir: Directory for output files
        force: Force reprocessing of all files
        clear_participant: Clear specific participant from history
        clear_all: Clear all processing history
        verbose: Print detailed information
    """
    data_path = Path(data_dir)
    output_path = Path(output_dir)

    print(f"\n{'#'*80}")
    print(f"# MOXIE Quality Check")
    print(f"#")
    print(f"# Data directory: {data_path}")
    print(f"# Output directory: {output_path}")
    print(f"# Mode: {'FORCE (reprocess all)' if force else 'INCREMENTAL (skip processed)'}")
    print(f"{'#'*80}\n")

    # Initialize processing tracker
    tracker_file = output_path / ".processing_log.json"
    tracker = ProcessingTracker(tracker_file)

    # Handle clearing operations
    if clear_all:
        print("Clearing all processing history...")
        tracker.clear_all()
        return

    if clear_participant:
        print(f"Clearing processing history for participant {clear_participant}...")
        tracker.clear_participant(clear_participant)
        return

    # Show processing history
    if not force:
        tracker.print_summary()

    # Discover ACQ files
    print("Discovering ACQ files...")
    all_acq_files = find_acq_files(str(data_path))

    if len(all_acq_files) == 0:
        print("No ACQ files found. Please check the data directory structure.")
        print("Expected: {data_dir}/{participant_id}/{TSST|PDST Visit}/Acqknowledge/*.acq")
        return

    print(f"Found {len(all_acq_files)} total ACQ files")

    # Filter to unprocessed files (unless force mode)
    if force:
        acq_files = all_acq_files
        print(f"FORCE mode: Processing all {len(acq_files)} files\n")
    else:
        acq_files = tracker.get_unprocessed_files(all_acq_files)
        skipped = len(all_acq_files) - len(acq_files)
        print(f"Incremental mode: {len(acq_files)} new/changed files to process")
        print(f"                  {skipped} files already processed (skipping)\n")

        if len(acq_files) == 0:
            print("✓ All files already processed!")
            print("  Use --force to reprocess all files")
            print("  Use --clear-participant <ID> to reprocess specific participant")
            return

    # Process each file
    processed_count = 0
    error_count = 0

    for i, file_path in enumerate(acq_files, 1):
        print(f"\n[{i}/{len(acq_files)}] Processing {file_path.name}")

        try:
            process_single_file(
                file_path=file_path,
                output_base_dir=output_path,
                tracker=tracker,
                verbose=verbose
            )
            processed_count += 1

        except Exception as e:
            error_count += 1
            info = get_participant_info(file_path)

            # Mark as failed in tracker
            tracker.mark_processed(
                file_path=file_path,
                participant_id=info['participant_id'],
                visit_type=info['visit_type'],
                success=False,
                error_message=str(e)
            )

            print(f"\n✗ Error processing {file_path.name}: {e}")
            import traceback
            traceback.print_exc()
            print("\nContinuing with next file...\n")
            continue

    print(f"\n{'#'*80}")
    print(f"# Processing Complete!")
    print(f"# Processed: {processed_count} files")
    print(f"# Errors: {error_count} files")
    if not force:
        print(f"# Skipped: {len(all_acq_files) - len(acq_files)} files (already processed)")
    print(f"# Results saved to: {output_path}")
    print(f"{'#'*80}\n")

    # Show final stats
    tracker.print_summary()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="MOXIE Quality Check - Process ACQ files and generate quality reports with incremental processing"
    )
    parser.add_argument(
        "data_dir",
        type=str,
        help="Directory containing participant data"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="./output",
        help="Output directory (default: ./output)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed information"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reprocessing of all files (ignore processing history)"
    )
    parser.add_argument(
        "--clear-participant",
        type=str,
        metavar="ID",
        help="Clear processing history for specific participant ID"
    )
    parser.add_argument(
        "--clear-all",
        action="store_true",
        help="Clear all processing history"
    )

    args = parser.parse_args()

    main(
        data_dir=args.data_dir,
        output_dir=args.output,
        force=args.force,
        clear_participant=args.clear_participant,
        clear_all=args.clear_all,
        verbose=args.verbose
    )
