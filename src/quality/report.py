"""
Quality assessment reporting.

Generate comprehensive quality reports for MOXIE data sessions.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any
from pathlib import Path
import json

from core.data_models import BioData
from quality.snr import get_snr_statistics
from quality.amplitude import get_amplitude_statistics


def convert_numpy_types(obj: Any) -> Any:
    """Convert numpy types to Python native types for JSON serialization."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj


class QualityMetrics:
    """Container for quality metrics of a single channel."""

    def __init__(self, channel_name: str):
        self.channel_name = channel_name
        self.snr_stats = None
        self.amplitude_stats = None
        self.overall_quality = None

    def set_snr_stats(self, snr_values: np.ndarray, threshold_flags: np.ndarray):
        """Set SNR statistics."""
        self.snr_stats = get_snr_statistics(snr_values, threshold_flags)

    def set_amplitude_stats(self, amplitude_values: np.ndarray, threshold_flags: np.ndarray):
        """Set amplitude statistics."""
        self.amplitude_stats = get_amplitude_statistics(amplitude_values, threshold_flags)

    def calculate_overall_quality(self) -> str:
        """
        Calculate overall quality rating based on SNR and amplitude.

        Returns:
            "excellent", "good", "fair", or "poor"
        """
        if self.snr_stats is None or self.amplitude_stats is None:
            return "unknown"

        # Calculate combined flagged percentage
        snr_flagged = self.snr_stats["percentage_flagged"]
        amp_flagged = self.amplitude_stats["percentage_flagged"]
        avg_flagged = (snr_flagged + amp_flagged) / 2

        if avg_flagged < 10:
            quality = "excellent"
        elif avg_flagged < 25:
            quality = "good"
        elif avg_flagged < 50:
            quality = "fair"
        else:
            quality = "poor"

        self.overall_quality = quality
        return quality

    def to_dict(self) -> Dict:
        """Convert to dictionary for export."""
        return {
            "channel_name": self.channel_name,
            "snr_stats": self.snr_stats,
            "amplitude_stats": self.amplitude_stats,
            "overall_quality": self.overall_quality
        }


def generate_quality_report(
    biodata: BioData,
    channels: List[str],
    participant_id: str,
    visit_type: str,
    output_path: Path = None
) -> Dict[str, QualityMetrics]:
    """
    Generate a comprehensive quality report for all processed channels.

    Args:
        biodata: BioData object with quality metrics computed
        channels: List of channel names to include in report
        participant_id: Participant identifier
        visit_type: Visit type (TSST or PDST)
        output_path: Optional path to save JSON report

    Returns:
        Dictionary mapping channel names to QualityMetrics objects
    """
    print(f"\n{'='*60}")
    print(f"Quality Report: {participant_id} - {visit_type}")
    print(f"{'='*60}\n")

    metrics = {}

    for channel in channels:
        if channel not in biodata.ChannelNames:
            print(f"⚠ Channel '{channel}' not found, skipping...")
            continue

        qm = QualityMetrics(channel)

        # Get SNR data
        snr_channel = f"{channel}_SNR"
        if snr_channel in biodata.ChannelNames:
            snr_result = biodata.get_dataframe(snr_channel)
            if snr_result is not None:
                snr_values, _ = snr_result
                snr_flags = biodata.get_snr_feature(snr_channel)
                if snr_flags is not None:
                    qm.set_snr_stats(snr_values, snr_flags)

        # Get amplitude data
        amp_channel = f"{channel}_Amplitude"
        if amp_channel in biodata.ChannelNames:
            amp_result = biodata.get_dataframe(amp_channel)
            if amp_result is not None:
                amp_values, _ = amp_result
                amp_flags = biodata.get_amplitude_feature(amp_channel)
                if amp_flags is not None:
                    qm.set_amplitude_stats(amp_values, amp_flags)

        # Calculate overall quality
        quality = qm.calculate_overall_quality()
        metrics[channel] = qm

        # Print summary
        print(f"{channel}: {quality.upper()}")
        if qm.snr_stats:
            print(f"  SNR: {qm.snr_stats['mean_snr']:.2f} dB "
                  f"({qm.snr_stats['percentage_flagged']:.1f}% flagged)")
        if qm.amplitude_stats:
            print(f"  Amplitude: {qm.amplitude_stats['percentage_flagged']:.1f}% flagged")
        print()

    # Save to JSON if output path provided
    if output_path:
        report_data = {
            "participant_id": participant_id,
            "visit_type": visit_type,
            "channels": {ch: metrics[ch].to_dict() for ch in metrics}
        }

        # Convert numpy types to Python native types
        report_data = convert_numpy_types(report_data)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"Quality report saved to: {output_path}")

    print(f"{'='*60}\n")

    return metrics


def create_quality_summary_table(metrics_dict: Dict[str, QualityMetrics]) -> pd.DataFrame:
    """
    Create a summary table of quality metrics.

    Args:
        metrics_dict: Dictionary of channel names to QualityMetrics

    Returns:
        DataFrame with summary statistics
    """
    rows = []

    for channel, qm in metrics_dict.items():
        row = {"channel": channel}

        if qm.snr_stats:
            row["snr_mean"] = qm.snr_stats["mean_snr"]
            row["snr_flagged_pct"] = qm.snr_stats["percentage_flagged"]

        if qm.amplitude_stats:
            row["amp_flagged_pct"] = qm.amplitude_stats["percentage_flagged"]

        row["overall_quality"] = qm.overall_quality

        rows.append(row)

    return pd.DataFrame(rows)
