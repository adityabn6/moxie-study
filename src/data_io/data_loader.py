"""
Data loading utilities for MOXIE ACQ files.

Functions for loading ACQ files and creating BioData objects with proper windowing.
"""

import bioread
import neurokit2 as nk
import pandas as pd
from pathlib import Path
from typing import List, Tuple, Optional

from core.data_models import BioData, DataObject
from core.window import Window
from core.config import TSST_TARGET_MARKERS, PDST_TARGET_MARKERS


def load_acq_file(file_path: Path, verbose: bool = False) -> Tuple[object, pd.DataFrame, float]:
    """
    Load an ACQ file using bioread and neurokit2.

    Args:
        file_path: Path to ACQ file
        verbose: Print event markers if True

    Returns:
        Tuple of (acq_object, dataframe, sampling_rate)
    """
    print(f"\nLoading: {file_path.name}")

    # Load with bioread for event markers
    acq = bioread.read_file(file_path)

    # Load with neurokit2 for data
    df, sampling_rate = nk.read_acqknowledge(str(file_path))

    if verbose:
        print(f"  Sampling rate: {sampling_rate} Hz")
        print(f"  Channels: {len(df.columns)}")
        print(f"  Duration: {len(df) / sampling_rate:.2f} seconds")
        print(f"  Event markers: {len(acq.event_markers)}")

        print("\n  Event markers found:")
        for marker in acq.event_markers:
            # Skip some verbose markers
            if marker.text.startswith('ME') or marker.text.startswith('NBP'):
                continue
            print(f"    - {marker.text} at {marker.sample_index / sampling_rate:.2f}s")

    return acq, df, sampling_rate


def create_biodata_from_acq(
    acq: object,
    df: pd.DataFrame,
    sampling_rate: float
) -> BioData:
    """
    Create a BioData object from ACQ data.

    Args:
        acq: Bioread ACQ object
        df: DataFrame with channel data
        sampling_rate: Sampling rate in Hz

    Returns:
        BioData object containing all channels
    """
    data_objects = []

    for column in df.columns:
        data_obj = DataObject(
            data=df[column].values,
            name=column,
            sampling_rate=sampling_rate
        )
        data_objects.append(data_obj)

    biodata = BioData(data_objects)

    return biodata


def create_windows_for_visit(
    visit_type: str,
    acq: object,
    sampling_rate: float,
    target_markers: Optional[List[str]] = None,
    verbose: bool = False
) -> List[Window]:
    """
    Create time windows based on visit type (TSST or PDST).

    Args:
        visit_type: "TSST Visit" or "PDST Visit"
        acq: Bioread ACQ object with event markers
        sampling_rate: Sampling rate in Hz
        target_markers: Optional list of valid markers (uses defaults if None)
        verbose: Print window info if True

    Returns:
        List of Window objects
    """
    windows = []

    # Use default target markers if not provided
    if target_markers is None:
        target_markers = TSST_TARGET_MARKERS if "TSST" in visit_type else PDST_TARGET_MARKERS

    if "TSST" in visit_type:
        # TSST Visit windows
        windows_config = [
            ("Speech Period", "Speech Period", "Speech", 1, 2),
            ("Arithmetic period", "Arithmetic period", "Arithmetic", 1, 2),
            ("Baseline Resting Period", "Baseline Resting Period", "Baseline", 1, 2),
            ("Recovery Period", "Recovery Period", "Recovery", 1, 2),
            ("Task Introduction", "Task Introduction", "Task Intro", 1, 2),
            ("Speech Preperation", "Speech Preperation", "Speech Prep", 1, 2),
            ("Debrief Period", "Recovery Period", "Debrief", 1, 1)
        ]

    elif "PDST" in visit_type:
        # PDST Visit windows
        windows_config = [
            ("Baseline Resting Period", "Baseline Resting Period", "Baseline", 1, 2),
            ("Recovery Period", "Recovery Period", "Recovery", 1, 2),
            ("Debrief Period", "Recovery Period", "Debrief", 1, 1),
            ("Survey Session", "Debrief Period", "Debate", 2, 1)
        ]

    else:
        print(f"Warning: Unknown visit type '{visit_type}'")
        return windows

    # Create Window objects
    for start_flag, end_flag, name, start_idx, end_idx in windows_config:
        window = Window(
            start_flag=start_flag,
            end_flag=end_flag,
            name=name,
            start_index=start_idx,
            end_index=end_idx,
            ACQ_Sampling_Rate=sampling_rate,
            acq=acq,
            target_markers=target_markers
        )
        windows.append(window)

        if verbose:
            window.print_info()

    return windows


def load_and_prepare_session(
    file_path: Path,
    verbose: bool = False
) -> Tuple[BioData, str, str]:
    """
    Complete workflow: load ACQ file and prepare BioData with windows.

    Args:
        file_path: Path to ACQ file
        verbose: Print detailed information

    Returns:
        Tuple of (BioData object, participant_id, visit_type)
    """
    # Extract metadata from path
    parts = file_path.parts
    participant_id = parts[-4] if len(parts) >= 4 else "unknown"

    # Determine visit type
    visit_type = None
    for part in parts:
        if "TSST" in part:
            visit_type = "TSST Visit"
        elif "PDST" in part:
            visit_type = "PDST Visit"

    # Load ACQ file
    acq, df, sampling_rate = load_acq_file(file_path, verbose=verbose)

    # Create BioData
    biodata = create_biodata_from_acq(acq, df, sampling_rate)

    # Create and add windows
    if visit_type:
        windows = create_windows_for_visit(
            visit_type=visit_type,
            acq=acq,
            sampling_rate=sampling_rate,
            verbose=verbose
        )

        for window in windows:
            biodata.add_window(window)

    if verbose:
        print(f"\n{'='*60}")
        print(f"Loaded session: {participant_id} - {visit_type}")
        print(f"Channels: {biodata.get_channel_count()}")
        print(f"Windows: {biodata.get_window_count()}")
        print(f"{'='*60}\n")

    return biodata, participant_id, visit_type
