#!/usr/bin/env python3
"""
MOXIE Quality Analysis Script

Analyzes the .processing_log.json file to generate comprehensive quality reports
and visualizations. Helps identify:
- Participants with poor data quality
- Channels with consistent issues
- Potential experimental protocol problems
- Quality trends across the study

Usage:
    python scripts/analyze_quality.py ./output
    python scripts/analyze_quality.py ./output --export-csv
    python scripts/analyze_quality.py ./output --detailed
"""

import sys
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def load_processing_log(log_file: Path) -> Dict:
    """Load the processing log JSON file."""
    if not log_file.exists():
        raise FileNotFoundError(f"Processing log not found: {log_file}")

    with open(log_file, 'r') as f:
        return json.load(f)


def parse_log_data(log_data: Dict) -> pd.DataFrame:
    """
    Parse processing log into a structured DataFrame.

    Returns:
        DataFrame with columns: participant_id, visit_type, channel,
                               overall_quality, snr_flagged_pct, amp_flagged_pct
    """
    rows = []

    for file_path, info in log_data.items():
        if not info.get('success', False):
            continue

        participant_id = info.get('participant_id')
        visit_type = info.get('visit_type')
        quality_summary = info.get('quality_summary', {})

        for channel, metrics in quality_summary.items():
            rows.append({
                'participant_id': participant_id,
                'visit_type': visit_type,
                'channel': channel,
                'overall_quality': metrics.get('overall_quality'),
                'snr_flagged_pct': metrics.get('snr_flagged_pct'),
                'amp_flagged_pct': metrics.get('amp_flagged_pct'),
                'filename': info.get('filename'),
                'processed_date': info.get('processed_date')
            })

    return pd.DataFrame(rows)


def analyze_by_participant(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze quality by participant."""

    # Count quality ratings per participant
    quality_counts = df.groupby(['participant_id', 'overall_quality']).size().unstack(fill_value=0)

    # Calculate average flagged percentages
    participant_stats = df.groupby('participant_id').agg({
        'snr_flagged_pct': 'mean',
        'amp_flagged_pct': 'mean',
        'channel': 'count'
    }).rename(columns={'channel': 'total_channels'})

    # Combine
    result = pd.concat([quality_counts, participant_stats], axis=1)
    result['avg_flagged_pct'] = (result['snr_flagged_pct'] + result['amp_flagged_pct']) / 2

    # Sort by worst quality first
    result = result.sort_values('avg_flagged_pct', ascending=False)

    return result


def analyze_by_channel(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze quality by channel across all participants."""

    channel_stats = df.groupby('channel').agg({
        'snr_flagged_pct': ['mean', 'std', 'max'],
        'amp_flagged_pct': ['mean', 'std', 'max'],
        'participant_id': 'count'
    })

    # Flatten column names
    channel_stats.columns = ['_'.join(col).strip() for col in channel_stats.columns.values]
    channel_stats = channel_stats.rename(columns={'participant_id_count': 'n_recordings'})

    # Count quality ratings
    quality_dist = df.groupby(['channel', 'overall_quality']).size().unstack(fill_value=0)

    result = pd.concat([channel_stats, quality_dist], axis=1)
    result['avg_flagged_pct'] = (result['snr_flagged_pct_mean'] + result['amp_flagged_pct_mean']) / 2

    # Sort by worst quality
    result = result.sort_values('avg_flagged_pct', ascending=False)

    return result


def analyze_by_visit_type(df: pd.DataFrame) -> pd.DataFrame:
    """Compare quality between TSST and PDST visits."""

    visit_stats = df.groupby('visit_type').agg({
        'snr_flagged_pct': 'mean',
        'amp_flagged_pct': 'mean',
        'participant_id': 'nunique',
        'channel': 'count'
    }).rename(columns={
        'participant_id': 'n_participants',
        'channel': 'n_recordings'
    })

    # Quality distribution
    quality_dist = df.groupby(['visit_type', 'overall_quality']).size().unstack(fill_value=0)

    result = pd.concat([visit_stats, quality_dist], axis=1)

    return result


def identify_problem_participants(df: pd.DataFrame, threshold: float = 25.0) -> List[str]:
    """
    Identify participants with consistently poor quality.

    Args:
        df: Quality DataFrame
        threshold: Average flagged percentage threshold (default 25%)

    Returns:
        List of participant IDs with quality issues
    """
    participant_stats = df.groupby('participant_id').agg({
        'snr_flagged_pct': 'mean',
        'amp_flagged_pct': 'mean'
    })

    participant_stats['avg_flagged'] = (
        participant_stats['snr_flagged_pct'] + participant_stats['amp_flagged_pct']
    ) / 2

    problem_participants = participant_stats[
        participant_stats['avg_flagged'] > threshold
    ].index.tolist()

    return problem_participants


def identify_problem_channels(df: pd.DataFrame, threshold: float = 25.0) -> List[str]:
    """
    Identify channels with consistently poor quality across participants.

    Args:
        df: Quality DataFrame
        threshold: Average flagged percentage threshold (default 25%)

    Returns:
        List of channel names with quality issues
    """
    channel_stats = df.groupby('channel').agg({
        'snr_flagged_pct': 'mean',
        'amp_flagged_pct': 'mean'
    })

    channel_stats['avg_flagged'] = (
        channel_stats['snr_flagged_pct'] + channel_stats['amp_flagged_pct']
    ) / 2

    problem_channels = channel_stats[
        channel_stats['avg_flagged'] > threshold
    ].index.tolist()

    return problem_channels


def generate_text_report(df: pd.DataFrame, output_dir: Path):
    """Generate a comprehensive text report."""

    report_file = output_dir / "quality_analysis_report.txt"

    with open(report_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("MOXIE Study - Quality Analysis Report\n")
        f.write("="*80 + "\n\n")

        # Overall statistics
        f.write("OVERALL STATISTICS\n")
        f.write("-"*80 + "\n")
        f.write(f"Total recordings: {len(df)}\n")
        f.write(f"Participants: {df['participant_id'].nunique()}\n")
        f.write(f"Channels analyzed: {df['channel'].nunique()}\n")
        f.write(f"Visit types: {', '.join(df['visit_type'].unique())}\n\n")

        # Quality distribution
        f.write("QUALITY DISTRIBUTION\n")
        f.write("-"*80 + "\n")
        quality_counts = df['overall_quality'].value_counts()
        for quality, count in quality_counts.items():
            pct = (count / len(df)) * 100
            f.write(f"  {quality.upper():12s}: {count:4d} ({pct:5.1f}%)\n")
        f.write("\n")

        # Average metrics
        f.write("AVERAGE QUALITY METRICS\n")
        f.write("-"*80 + "\n")
        f.write(f"  SNR flagged:       {df['snr_flagged_pct'].mean():5.1f}%\n")
        f.write(f"  Amplitude flagged: {df['amp_flagged_pct'].mean():5.1f}%\n\n")

        # Problem participants
        problem_participants = identify_problem_participants(df)
        f.write("PARTICIPANTS WITH QUALITY CONCERNS (>25% flagged)\n")
        f.write("-"*80 + "\n")
        if problem_participants:
            participant_stats = df.groupby('participant_id').agg({
                'snr_flagged_pct': 'mean',
                'amp_flagged_pct': 'mean'
            })
            participant_stats['avg'] = (
                participant_stats['snr_flagged_pct'] + participant_stats['amp_flagged_pct']
            ) / 2

            for pid in problem_participants:
                stats = participant_stats.loc[pid]
                f.write(f"  {pid}: {stats['avg']:.1f}% avg flagged ")
                f.write(f"(SNR: {stats['snr_flagged_pct']:.1f}%, ")
                f.write(f"Amp: {stats['amp_flagged_pct']:.1f}%)\n")
        else:
            f.write("  None identified\n")
        f.write("\n")

        # Problem channels
        problem_channels = identify_problem_channels(df)
        f.write("CHANNELS WITH QUALITY CONCERNS (>25% flagged)\n")
        f.write("-"*80 + "\n")
        if problem_channels:
            channel_stats = df.groupby('channel').agg({
                'snr_flagged_pct': 'mean',
                'amp_flagged_pct': 'mean',
                'participant_id': 'count'
            })
            channel_stats['avg'] = (
                channel_stats['snr_flagged_pct'] + channel_stats['amp_flagged_pct']
            ) / 2

            for channel in problem_channels:
                stats = channel_stats.loc[channel]
                f.write(f"  {channel}:\n")
                f.write(f"    Avg flagged: {stats['avg']:.1f}% ")
                f.write(f"(SNR: {stats['snr_flagged_pct']:.1f}%, ")
                f.write(f"Amp: {stats['amp_flagged_pct']:.1f}%)\n")
                f.write(f"    Recordings: {stats['participant_id']:.0f}\n")
        else:
            f.write("  None identified\n")
        f.write("\n")

        # Visit type comparison
        f.write("VISIT TYPE COMPARISON\n")
        f.write("-"*80 + "\n")
        visit_stats = df.groupby('visit_type').agg({
            'snr_flagged_pct': 'mean',
            'amp_flagged_pct': 'mean',
            'participant_id': 'nunique'
        })

        for visit_type in visit_stats.index:
            stats = visit_stats.loc[visit_type]
            f.write(f"  {visit_type}:\n")
            f.write(f"    Participants: {stats['participant_id']:.0f}\n")
            f.write(f"    SNR flagged: {stats['snr_flagged_pct']:.1f}%\n")
            f.write(f"    Amp flagged: {stats['amp_flagged_pct']:.1f}%\n")
        f.write("\n")

        # Recommendations
        f.write("RECOMMENDATIONS\n")
        f.write("-"*80 + "\n")

        if problem_participants:
            f.write("1. PARTICIPANT-LEVEL ISSUES:\n")
            f.write("   - Review experimental setup for flagged participants\n")
            f.write("   - Check sensor placement and connection quality\n")
            f.write("   - Consider participant-specific factors (movement, skin conductance)\n\n")

        if problem_channels:
            f.write("2. CHANNEL-LEVEL ISSUES:\n")
            for channel in problem_channels:
                if "Blood Pressure" in channel or "NIBP" in channel:
                    f.write(f"   - {channel}: Consider intermittent measurement nature\n")
                elif "Custom" in channel or "DA100C" in channel:
                    f.write(f"   - {channel}: Verify sensor configuration and calibration\n")
                else:
                    f.write(f"   - {channel}: Check sensor placement protocol\n")
            f.write("\n")

        if not problem_participants and not problem_channels:
            f.write("✓ Overall data quality appears good!\n")
            f.write("  Continue current experimental protocols.\n\n")

        f.write("="*80 + "\n")

    print(f"Text report saved to: {report_file}")
    return report_file


def generate_csv_exports(df: pd.DataFrame, output_dir: Path):
    """Generate CSV files for further analysis."""

    # Summary by participant
    participant_summary = analyze_by_participant(df)
    participant_file = output_dir / "quality_by_participant.csv"
    participant_summary.to_csv(participant_file)
    print(f"Participant summary saved to: {participant_file}")

    # Summary by channel
    channel_summary = analyze_by_channel(df)
    channel_file = output_dir / "quality_by_channel.csv"
    channel_summary.to_csv(channel_file)
    print(f"Channel summary saved to: {channel_file}")

    # Summary by visit type
    visit_summary = analyze_by_visit_type(df)
    visit_file = output_dir / "quality_by_visit_type.csv"
    visit_summary.to_csv(visit_file)
    print(f"Visit type summary saved to: {visit_file}")

    # Detailed data
    detail_file = output_dir / "quality_detailed.csv"
    df.to_csv(detail_file, index=False)
    print(f"Detailed data saved to: {detail_file}")


def print_console_summary(df: pd.DataFrame):
    """Print summary to console."""

    print("\n" + "="*80)
    print("MOXIE QUALITY ANALYSIS SUMMARY")
    print("="*80 + "\n")

    # Overall stats
    print(f"Total recordings: {len(df)}")
    print(f"Participants: {df['participant_id'].nunique()}")
    print(f"Channels: {df['channel'].nunique()}")
    print()

    # Quality distribution
    print("Quality Distribution:")
    quality_counts = df['overall_quality'].value_counts()
    for quality in ['excellent', 'good', 'fair', 'poor']:
        if quality in quality_counts:
            count = quality_counts[quality]
            pct = (count / len(df)) * 100
            print(f"  {quality.upper():12s}: {count:4d} ({pct:5.1f}%)")
    print()

    # Problem identification
    problem_participants = identify_problem_participants(df)
    problem_channels = identify_problem_channels(df)

    if problem_participants:
        print(f"⚠ Participants with quality concerns: {len(problem_participants)}")
        for pid in problem_participants[:5]:  # Show first 5
            print(f"   - {pid}")
        if len(problem_participants) > 5:
            print(f"   ... and {len(problem_participants) - 5} more")
    else:
        print("✓ No participants with major quality concerns")
    print()

    if problem_channels:
        print(f"⚠ Channels with quality concerns: {len(problem_channels)}")
        for channel in problem_channels:
            avg_flagged = df[df['channel'] == channel].agg({
                'snr_flagged_pct': 'mean',
                'amp_flagged_pct': 'mean'
            })
            avg = (avg_flagged['snr_flagged_pct'] + avg_flagged['amp_flagged_pct']) / 2
            print(f"   - {channel}: {avg:.1f}% flagged")
    else:
        print("✓ No channels with major quality concerns")
    print()

    print("="*80 + "\n")


def main(output_dir: str, export_csv: bool = False, detailed: bool = False):
    """
    Main analysis function.

    Args:
        output_dir: Directory containing .processing_log.json
        export_csv: Export detailed CSV files
        detailed: Show detailed console output
    """
    output_path = Path(output_dir)
    log_file = output_path / ".processing_log.json"

    print(f"\nLoading processing log from: {log_file}")

    try:
        log_data = load_processing_log(log_file)
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure you've run quality_check.py first!")
        return

    print(f"Found {len(log_data)} files in processing log\n")

    # Parse data
    df = parse_log_data(log_data)

    if len(df) == 0:
        print("No successful processing entries found in log.")
        return

    # Console summary
    print_console_summary(df)

    # Generate text report
    print("Generating reports...")
    report_file = generate_text_report(df, output_path)
    print(f"\n✓ Text report saved: {report_file}")

    # Export CSVs if requested
    if export_csv:
        print("\nExporting CSV files...")
        generate_csv_exports(df, output_path)

    # Detailed output if requested
    if detailed:
        print("\n" + "="*80)
        print("DETAILED ANALYSIS")
        print("="*80 + "\n")

        print("BY PARTICIPANT:")
        print(analyze_by_participant(df))
        print("\n")

        print("BY CHANNEL:")
        print(analyze_by_channel(df))
        print("\n")

        print("BY VISIT TYPE:")
        print(analyze_by_visit_type(df))
        print()

    print("\n" + "="*80)
    print("Analysis complete!")
    print(f"Review {report_file} for detailed findings")
    if export_csv:
        print(f"CSV files exported to: {output_path}")
    print("="*80 + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze MOXIE quality data from processing log"
    )
    parser.add_argument(
        "output_dir",
        type=str,
        help="Output directory containing .processing_log.json"
    )
    parser.add_argument(
        "--export-csv",
        action="store_true",
        help="Export detailed CSV files for analysis"
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed console output"
    )

    args = parser.parse_args()

    main(args.output_dir, args.export_csv, args.detailed)
