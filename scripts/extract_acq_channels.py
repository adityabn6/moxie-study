"""
Extract individual channels from .acq files to CSV format for NeuroKit processing
Uses bioread library to directly read AcqKnowledge files
"""

import pandas as pd
import argparse
from pathlib import Path

try:
    import bioread
except ImportError:
    print("Error: bioread library not found. Install with: pip install bioread")
    exit(1)


def extract_channels_from_acq(acq_file_path, output_dir=None, channels=None, channel_names=None):
    """
    Extract specified channels from an .acq file and save as individual CSV files

    Parameters:
    -----------
    acq_file_path : str or Path
        Path to the .acq file
    output_dir : str or Path, optional
        Directory to save CSV files. If None, uses same directory as acq_file
    channels : list of int, optional
        List of channel indices to extract. If None, extracts all channels
    channel_names : list of str, optional
        List of channel name patterns to match (case-insensitive substring match)

    Returns:
    --------
    dict : Dictionary mapping channel indices to output file paths
    """
    acq_file = Path(acq_file_path)

    if output_dir is None:
        output_dir = acq_file.parent / "processed"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Read the .acq file
    print(f"Loading {acq_file}...")
    data = bioread.read(str(acq_file))

    print(f"\nFile information:")
    print(f"  Number of channels: {len(data.channels)}")
    print(f"  Sampling rate: {data.samples_per_second} Hz")

    # Display channel information
    print("\nAvailable channels:")
    for i, channel in enumerate(data.channels):
        print(f"  {i}: {channel.name} ({len(channel.data)} samples)")

    # Determine which channels to extract
    if channel_names is not None:
        # Match by name (case-insensitive substring)
        channels_to_extract = []
        for i, channel in enumerate(data.channels):
            for name_pattern in channel_names:
                if name_pattern.lower() in channel.name.lower():
                    channels_to_extract.append(i)
                    break
        print(f"\nMatched {len(channels_to_extract)} channels by name: {channels_to_extract}")
    elif channels is None:
        channels_to_extract = range(len(data.channels))
    else:
        channels_to_extract = channels

    output_files = {}

    # Extract each channel
    for ch_idx in channels_to_extract:
        if ch_idx >= len(data.channels):
            print(f"Warning: Channel {ch_idx} not found, skipping")
            continue

        channel = data.channels[ch_idx]

        # Get channel data
        ch_data = channel.data

        # Clean channel name for filename
        clean_name = channel.name.replace(' ', '_').replace(',', '').replace('-', '_').replace('/', '_')

        # Create output filename
        base_name = acq_file.stem
        output_file = output_dir / f"{base_name}_ch{ch_idx}_{clean_name}.csv"

        # Save as CSV with single column
        df = pd.DataFrame(ch_data, columns=['signal'])
        df.to_csv(output_file, index=False)

        output_files[ch_idx] = output_file

        print(f"Channel {ch_idx} ({channel.name}): {len(ch_data)} samples @ {data.samples_per_second:.1f} Hz -> {output_file.name}")

    return output_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract channels from .acq files")
    parser.add_argument("acq_file", help="Path to .acq file")
    parser.add_argument("-o", "--output-dir", help="Output directory for CSV files")
    parser.add_argument("-c", "--channels", type=int, nargs="+",
                        help="Channel indices to extract (default: all)")
    parser.add_argument("-n", "--channel-names", nargs="+",
                        help="Channel name patterns to match (e.g., ECG RSP)")

    args = parser.parse_args()

    output_files = extract_channels_from_acq(
        args.acq_file,
        output_dir=args.output_dir,
        channels=args.channels,
        channel_names=args.channel_names
    )

    print(f"\n✓ Extracted {len(output_files)} channels successfully")
