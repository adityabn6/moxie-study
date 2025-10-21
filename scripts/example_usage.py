#!/usr/bin/env python3
"""
Example usage of MOXIE analysis modules.

This script demonstrates how to use the MOXIE analysis package
programmatically (as opposed to using the command-line scripts).
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config import DEFAULT_CHANNELS, QUALITY_CHECK_PARAMS
from data_io.file_discovery import find_acq_files, get_participant_info
from data_io.data_loader import load_and_prepare_session
from quality.snr import compute_and_append_snr
from quality.amplitude import compute_and_append_amplitude
from quality.report import generate_quality_report
from visualization.bokeh_plots import save_bokeh_plot


def example_single_file_processing():
    """Example: Process a single ACQ file."""

    print("\n" + "="*80)
    print("Example: Processing a Single ACQ File")
    print("="*80 + "\n")

    # Specify your file path
    file_path = Path("../Participant_Data/Participant_001/TSST Visit/Acqknowledge/session.acq")

    # Check if file exists
    if not file_path.exists():
        print(f"File not found: {file_path}")
        print("Please update the file_path variable with a valid ACQ file path.")
        return

    # Load the file
    print("Step 1: Loading ACQ file...")
    biodata, participant_id, visit_type = load_and_prepare_session(
        file_path,
        verbose=True
    )

    print(f"\nLoaded: {participant_id} - {visit_type}")
    print(f"Channels: {biodata.get_channel_count()}")
    print(f"Windows: {biodata.get_window_count()}")

    # Select a channel to process
    channel = "ECG2108000293"  # Change to a channel that exists in your data

    if channel not in biodata.ChannelNames:
        print(f"\nChannel '{channel}' not found. Available channels:")
        for ch in biodata.ChannelNames[:10]:  # Show first 10
            print(f"  - {ch}")
        return

    # Compute quality metrics
    print(f"\nStep 2: Computing quality metrics for {channel}...")

    window_size = QUALITY_CHECK_PARAMS["window_size_seconds"]
    overlap = QUALITY_CHECK_PARAMS["overlap_seconds"]

    # SNR
    snr_values, snr_times, snr_flags = compute_and_append_snr(
        biodata=biodata,
        channel_name=channel,
        fs=biodata.Data[0].sampling_rate,
        window_size_sec=window_size,
        overlap_sec=overlap,
        alpha=0.5
    )

    # Amplitude
    amp_values, amp_times, amp_flags = compute_and_append_amplitude(
        biodata=biodata,
        channel_name=channel,
        fs=biodata.Data[0].sampling_rate,
        window_size_sec=window_size,
        overlap_sec=overlap,
        beta=0.5
    )

    # Generate visualization
    print("\nStep 3: Creating visualization...")
    output_file = Path("./example_output.html")

    quality_sampling_rate = 1 / (window_size - overlap)

    save_bokeh_plot(
        biodata=biodata,
        filename=str(output_file),
        sampling_rates=[20, quality_sampling_rate, quality_sampling_rate],
        channel_names=[channel, f"{channel}_SNR", f"{channel}_Amplitude"]
    )

    print(f"\nVisualization saved to: {output_file}")
    print("\n" + "="*80 + "\n")


def example_batch_processing():
    """Example: Discover and process multiple files."""

    print("\n" + "="*80)
    print("Example: Batch Processing Multiple Files")
    print("="*80 + "\n")

    # Specify data directory
    data_dir = Path("../Participant_Data")

    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}")
        print("Please update the data_dir variable.")
        return

    # Discover all ACQ files
    print("Discovering ACQ files...")
    acq_files = find_acq_files(str(data_dir))

    print(f"Found {len(acq_files)} ACQ files\n")

    # Show file information
    for i, file_path in enumerate(acq_files[:5], 1):  # Show first 5
        info = get_participant_info(file_path)
        print(f"{i}. {info['participant_id']} - {info['visit_type']}")
        print(f"   {info['filename']}")

    if len(acq_files) > 5:
        print(f"   ... and {len(acq_files) - 5} more files")

    print("\n" + "="*80 + "\n")


def example_quality_report():
    """Example: Generate a quality report."""

    print("\n" + "="*80)
    print("Example: Generating Quality Report")
    print("="*80 + "\n")

    # You would typically have a processed BioData object here
    # This example shows the structure

    print("Quality report structure:")
    print("""
    {
        "participant_id": "Participant_001",
        "visit_type": "TSST Visit",
        "channels": {
            "ECG2108000293": {
                "snr_stats": {
                    "mean_snr": 15.3,
                    "percentage_flagged": 8.2
                },
                "amplitude_stats": {
                    "percentage_flagged": 5.1
                },
                "overall_quality": "excellent"
            },
            ...
        }
    }
    """)

    print("See quality_check.py for complete implementation")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# MOXIE Analysis - Example Usage")
    print("#"*80)

    # Run examples
    # example_single_file_processing()
    example_batch_processing()
    # example_quality_report()

    print("\n" + "#"*80)
    print("# Examples Complete")
    print("#" + "#"*78 + "#\n")

    print("To run full processing, use:")
    print("  python scripts/quality_check.py /path/to/data -o ./output")
    print()
