#!/usr/bin/env python3
"""
MOXIE Quality Visualization Script

Generates visualizations from the processing log to help identify
quality patterns and protocol issues.

Usage:
    python scripts/visualize_quality.py ./output
    python scripts/visualize_quality.py ./output --format png
"""

import sys
import json
from pathlib import Path
from collections import defaultdict
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False
    print("Warning: matplotlib/seaborn not installed. Install with:")
    print("  pip install matplotlib seaborn")


def load_and_parse_log(log_file: Path) -> pd.DataFrame:
    """Load processing log and parse into DataFrame."""
    with open(log_file, 'r') as f:
        log_data = json.load(f)

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
                'amp_flagged_pct': metrics.get('amp_flagged_pct')
            })

    return pd.DataFrame(rows)


def plot_quality_distribution(df: pd.DataFrame, output_file: Path):
    """Plot overall quality distribution."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Quality rating counts
    quality_order = ['excellent', 'good', 'fair', 'poor']
    quality_counts = df['overall_quality'].value_counts()

    colors = {'excellent': '#2ecc71', 'good': '#3498db', 'fair': '#f39c12', 'poor': '#e74c3c'}
    plot_colors = [colors.get(q, 'gray') for q in quality_order if q in quality_counts]

    axes[0].bar(
        range(len(quality_counts)),
        [quality_counts.get(q, 0) for q in quality_order if q in quality_counts],
        color=plot_colors
    )
    axes[0].set_xticks(range(len(quality_counts)))
    axes[0].set_xticklabels([q.capitalize() for q in quality_order if q in quality_counts])
    axes[0].set_ylabel('Number of Recordings')
    axes[0].set_title('Overall Quality Distribution')
    axes[0].grid(axis='y', alpha=0.3)

    # Percentage
    total = len(df)
    percentages = [quality_counts.get(q, 0) / total * 100 for q in quality_order if q in quality_counts]
    axes[1].bar(range(len(percentages)), percentages, color=plot_colors)
    axes[1].set_xticks(range(len(percentages)))
    axes[1].set_xticklabels([q.capitalize() for q in quality_order if q in quality_counts])
    axes[1].set_ylabel('Percentage (%)')
    axes[1].set_title('Quality Distribution (%)')
    axes[1].grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {output_file.name}")


def plot_participant_heatmap(df: pd.DataFrame, output_file: Path):
    """Plot heatmap of quality by participant and channel."""
    # Create pivot table: participants x channels with avg flagged %
    df['avg_flagged'] = (df['snr_flagged_pct'] + df['amp_flagged_pct']) / 2

    pivot = df.pivot_table(
        values='avg_flagged',
        index='participant_id',
        columns='channel',
        aggfunc='mean'
    )

    # Sort by worst quality
    pivot = pivot.loc[pivot.mean(axis=1).sort_values(ascending=False).index]

    fig, ax = plt.subplots(figsize=(14, max(6, len(pivot) * 0.4)))

    sns.heatmap(
        pivot,
        annot=True,
        fmt='.1f',
        cmap='RdYlGn_r',
        center=25,
        vmin=0,
        vmax=100,
        cbar_kws={'label': 'Avg Flagged %'},
        linewidths=0.5,
        ax=ax
    )

    ax.set_title('Quality Heatmap: Average Flagged % by Participant and Channel')
    ax.set_xlabel('Channel')
    ax.set_ylabel('Participant ID')

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {output_file.name}")


def plot_channel_comparison(df: pd.DataFrame, output_file: Path):
    """Plot channel quality comparison."""
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    # SNR flagged percentage by channel
    channel_snr = df.groupby('channel')['snr_flagged_pct'].agg(['mean', 'std']).sort_values('mean', ascending=False)

    axes[0].bar(range(len(channel_snr)), channel_snr['mean'], yerr=channel_snr['std'], capsize=5)
    axes[0].set_xticks(range(len(channel_snr)))
    axes[0].set_xticklabels(channel_snr.index, rotation=45, ha='right')
    axes[0].set_ylabel('SNR Flagged %')
    axes[0].set_title('SNR Quality by Channel (lower is better)')
    axes[0].axhline(y=25, color='r', linestyle='--', alpha=0.5, label='Concern threshold (25%)')
    axes[0].legend()
    axes[0].grid(axis='y', alpha=0.3)

    # Amplitude flagged percentage by channel
    channel_amp = df.groupby('channel')['amp_flagged_pct'].agg(['mean', 'std']).sort_values('mean', ascending=False)

    axes[1].bar(range(len(channel_amp)), channel_amp['mean'], yerr=channel_amp['std'], capsize=5, color='orange')
    axes[1].set_xticks(range(len(channel_amp)))
    axes[1].set_xticklabels(channel_amp.index, rotation=45, ha='right')
    axes[1].set_ylabel('Amplitude Flagged %')
    axes[1].set_title('Amplitude Quality by Channel (lower is better)')
    axes[1].axhline(y=25, color='r', linestyle='--', alpha=0.5, label='Concern threshold (25%)')
    axes[1].legend()
    axes[1].grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {output_file.name}")


def plot_visit_comparison(df: pd.DataFrame, output_file: Path):
    """Compare quality between visit types."""
    if df['visit_type'].nunique() < 2:
        print("  ⊘ Skipping visit comparison (only one visit type)")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Quality distribution by visit
    visit_quality = pd.crosstab(df['visit_type'], df['overall_quality'], normalize='index') * 100

    quality_order = ['excellent', 'good', 'fair', 'poor']
    colors_list = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']

    visit_quality = visit_quality[[q for q in quality_order if q in visit_quality.columns]]

    visit_quality.plot(kind='bar', stacked=True, ax=axes[0], color=colors_list[:len(visit_quality.columns)])
    axes[0].set_ylabel('Percentage (%)')
    axes[0].set_xlabel('Visit Type')
    axes[0].set_title('Quality Distribution by Visit Type')
    axes[0].legend(title='Quality', loc='upper right')
    axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=0)

    # Average flagged percentage by visit
    visit_flagged = df.groupby('visit_type').agg({
        'snr_flagged_pct': 'mean',
        'amp_flagged_pct': 'mean'
    })

    x = np.arange(len(visit_flagged))
    width = 0.35

    axes[1].bar(x - width/2, visit_flagged['snr_flagged_pct'], width, label='SNR Flagged', color='steelblue')
    axes[1].bar(x + width/2, visit_flagged['amp_flagged_pct'], width, label='Amplitude Flagged', color='orange')

    axes[1].set_ylabel('Average Flagged %')
    axes[1].set_xlabel('Visit Type')
    axes[1].set_title('Average Flagged Percentage by Visit Type')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(visit_flagged.index, rotation=0)
    axes[1].legend()
    axes[1].grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {output_file.name}")


def plot_participant_overview(df: pd.DataFrame, output_file: Path):
    """Plot per-participant quality overview."""
    participant_stats = df.groupby('participant_id').agg({
        'snr_flagged_pct': 'mean',
        'amp_flagged_pct': 'mean',
        'channel': 'count'
    }).rename(columns={'channel': 'n_channels'})

    participant_stats['avg_flagged'] = (
        participant_stats['snr_flagged_pct'] + participant_stats['amp_flagged_pct']
    ) / 2

    participant_stats = participant_stats.sort_values('avg_flagged', ascending=False)

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    # Bar plot of average flagged percentage
    x = range(len(participant_stats))
    axes[0].bar(x, participant_stats['avg_flagged'], color='steelblue')
    axes[0].axhline(y=25, color='r', linestyle='--', alpha=0.5, label='Concern threshold (25%)')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(participant_stats.index, rotation=45, ha='right')
    axes[0].set_ylabel('Average Flagged %')
    axes[0].set_title('Overall Quality by Participant (lower is better)')
    axes[0].legend()
    axes[0].grid(axis='y', alpha=0.3)

    # Stacked bar: SNR vs Amplitude
    axes[1].bar(x, participant_stats['snr_flagged_pct'], label='SNR Flagged', color='steelblue')
    axes[1].bar(x, participant_stats['amp_flagged_pct'], bottom=participant_stats['snr_flagged_pct'],
                label='Amplitude Flagged', color='orange')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(participant_stats.index, rotation=45, ha='right')
    axes[1].set_ylabel('Flagged %')
    axes[1].set_title('SNR vs Amplitude Quality by Participant')
    axes[1].legend()
    axes[1].grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {output_file.name}")


def plot_scatter_snr_vs_amplitude(df: pd.DataFrame, output_file: Path):
    """Scatter plot of SNR vs Amplitude flagged percentages."""
    fig, ax = plt.subplots(figsize=(10, 8))

    # Color by quality
    quality_colors = {
        'excellent': '#2ecc71',
        'good': '#3498db',
        'fair': '#f39c12',
        'poor': '#e74c3c'
    }

    for quality in ['excellent', 'good', 'fair', 'poor']:
        mask = df['overall_quality'] == quality
        if mask.any():
            ax.scatter(
                df.loc[mask, 'snr_flagged_pct'],
                df.loc[mask, 'amp_flagged_pct'],
                c=quality_colors[quality],
                label=quality.capitalize(),
                alpha=0.6,
                s=50
            )

    # Add threshold lines
    ax.axvline(x=25, color='r', linestyle='--', alpha=0.3, label='SNR concern (25%)')
    ax.axhline(y=25, color='r', linestyle='--', alpha=0.3, label='Amp concern (25%)')

    ax.set_xlabel('SNR Flagged %')
    ax.set_ylabel('Amplitude Flagged %')
    ax.set_title('SNR vs Amplitude Quality')
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {output_file.name}")


def main(output_dir: str, format: str = 'png'):
    """
    Generate all visualizations.

    Args:
        output_dir: Directory containing .processing_log.json
        format: Output format (png, pdf, svg)
    """
    if not HAS_PLOTTING:
        print("\n✗ Error: Plotting libraries not available")
        print("Install with: pip install matplotlib seaborn")
        return

    output_path = Path(output_dir)
    log_file = output_path / ".processing_log.json"

    if not log_file.exists():
        print(f"\n✗ Error: Processing log not found: {log_file}")
        print("Run quality_check.py first!")
        return

    print(f"\nLoading processing log from: {log_file}")

    # Load and parse data
    df = load_and_parse_log(log_file)

    if len(df) == 0:
        print("No data found in processing log.")
        return

    print(f"Found {len(df)} quality records")
    print(f"Participants: {df['participant_id'].nunique()}")
    print(f"Channels: {df['channel'].nunique()}\n")

    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.facecolor'] = 'white'

    # Create visualizations directory
    viz_dir = output_path / "visualizations"
    viz_dir.mkdir(exist_ok=True)

    print("Generating visualizations...")

    # Generate plots
    plot_quality_distribution(df, viz_dir / f"quality_distribution.{format}")
    plot_participant_overview(df, viz_dir / f"participant_overview.{format}")
    plot_participant_heatmap(df, viz_dir / f"participant_heatmap.{format}")
    plot_channel_comparison(df, viz_dir / f"channel_comparison.{format}")
    plot_visit_comparison(df, viz_dir / f"visit_comparison.{format}")
    plot_scatter_snr_vs_amplitude(df, viz_dir / f"snr_vs_amplitude.{format}")

    print(f"\n✓ All visualizations saved to: {viz_dir}")
    print(f"  Format: {format.upper()}")
    print("\nOpen these files to review quality patterns!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate quality visualizations from MOXIE processing log"
    )
    parser.add_argument(
        "output_dir",
        type=str,
        help="Output directory containing .processing_log.json"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=['png', 'pdf', 'svg'],
        default='png',
        help="Output format for plots (default: png)"
    )

    args = parser.parse_args()

    main(args.output_dir, args.format)
