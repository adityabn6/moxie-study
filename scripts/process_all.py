#!/usr/bin/env python3
"""
MOXIE Complete Processing Script

Extended processing including:
- Quality checks (SNR, Amplitude)
- Signal processing (ECG, EDA, RSP) - To be implemented
- Feature extraction - To be implemented
- Statistical analysis - To be implemented

For now, this is a template that calls the quality check script.
Future versions will include full signal processing pipeline.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from quality_check import main as quality_check_main


def main(data_dir: str, output_dir: str, verbose: bool = False):
    """
    Complete MOXIE processing pipeline.

    Args:
        data_dir: Directory containing participant data
        output_dir: Directory for output files
        verbose: Print detailed information
    """
    print("\n" + "="*80)
    print("MOXIE Complete Processing Pipeline")
    print("="*80)
    print("\nPhase 1: Quality Assessment")
    print("-"*80 + "\n")

    # Run quality checks
    quality_check_main(data_dir, output_dir, verbose)

    print("\n" + "="*80)
    print("Phase 2: Signal Processing (Coming Soon)")
    print("="*80)
    print("\nFuture features:")
    print("  - ECG: R-peak detection, HRV analysis")
    print("  - EDA: Phasic/tonic decomposition, SCR detection")
    print("  - RSP: Breathing rate, respiratory variability")
    print("  - EMG: Muscle activity analysis")
    print("  - BP: Blood pressure trends")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="MOXIE Complete Processing - Full pipeline for ACQ data analysis"
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

    args = parser.parse_args()

    main(args.data_dir, args.output, args.verbose)
