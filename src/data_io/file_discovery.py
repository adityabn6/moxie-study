"""
File discovery utilities for MOXIE study data.

Functions for locating ACQ files within the participant data directory structure.
"""

from pathlib import Path
from typing import List, Dict, Tuple
from core.config import VISIT_TYPES


def find_acq_files(input_path: str) -> List[Path]:
    """
    Discover all ACQ files in the participant data directory.

    Expected directory structure:
        {input_path}/
            {Participant_ID}/
                TSST Visit/
                    Acqknowledge/
                        *.acq
                PDST Visit/
                    Acqknowledge/
                        *.acq

    Args:
        input_path: Root directory containing participant folders

    Returns:
        List of Path objects pointing to ACQ files
    """
    input_dir = Path(input_path)

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_path}")

    acq_file_paths = []

    for participant_dir in input_dir.iterdir():
        if not participant_dir.is_dir():
            continue

        for visit in VISIT_TYPES:
            acq_path = participant_dir / visit / "Acqknowledge"

            if acq_path.exists():
                for file in acq_path.glob("*.acq"):
                    acq_file_paths.append(file.resolve())

    return acq_file_paths


def get_participant_info(acq_file_path: Path) -> Dict[str, str]:
    """
    Extract participant ID and visit type from ACQ file path.

    Args:
        acq_file_path: Path to ACQ file

    Returns:
        Dictionary with 'participant_id', 'visit_type', and 'filename'
    """
    parts = acq_file_path.parts

    # Determine visit type
    visit_type = None
    for part in parts:
        if part in VISIT_TYPES:
            visit_type = part
            break

    # Participant ID is typically 4 levels up from the file
    # .../Participant_ID/Visit/Acqknowledge/file.acq
    participant_id = parts[-4] if len(parts) >= 4 else "unknown"

    return {
        "participant_id": participant_id,
        "visit_type": visit_type,
        "filename": acq_file_path.name,
        "full_path": str(acq_file_path)
    }


def organize_files_by_participant(acq_files: List[Path]) -> Dict[str, Dict[str, List[Path]]]:
    """
    Organize ACQ files by participant and visit type.

    Args:
        acq_files: List of ACQ file paths

    Returns:
        Nested dictionary: {participant_id: {visit_type: [file_paths]}}
    """
    organized = {}

    for file_path in acq_files:
        info = get_participant_info(file_path)
        participant_id = info["participant_id"]
        visit_type = info["visit_type"]

        if participant_id not in organized:
            organized[participant_id] = {}

        if visit_type not in organized[participant_id]:
            organized[participant_id][visit_type] = []

        organized[participant_id][visit_type].append(file_path)

    return organized


def validate_data_structure(input_path: str, verbose: bool = True) -> Tuple[bool, List[str]]:
    """
    Validate that the data directory follows expected structure.

    Args:
        input_path: Root directory containing participant folders
        verbose: Print detailed validation messages

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    input_dir = Path(input_path)

    if not input_dir.exists():
        issues.append(f"Root directory does not exist: {input_path}")
        return False, issues

    participant_dirs = [d for d in input_dir.iterdir() if d.is_dir()]

    if len(participant_dirs) == 0:
        issues.append("No participant directories found")

    for participant_dir in participant_dirs:
        found_visits = False

        for visit in VISIT_TYPES:
            visit_path = participant_dir / visit
            if visit_path.exists():
                found_visits = True
                acq_path = visit_path / "Acqknowledge"

                if not acq_path.exists():
                    issues.append(
                        f"{participant_dir.name}/{visit}: Missing 'Acqknowledge' folder"
                    )
                else:
                    acq_files = list(acq_path.glob("*.acq"))
                    if len(acq_files) == 0:
                        issues.append(
                            f"{participant_dir.name}/{visit}: No ACQ files found"
                        )

        if not found_visits:
            issues.append(f"{participant_dir.name}: No visit folders found")

    if verbose:
        if len(issues) == 0:
            print("✓ Data structure validation passed")
        else:
            print("✗ Data structure validation found issues:")
            for issue in issues:
                print(f"  - {issue}")

    return len(issues) == 0, issues
