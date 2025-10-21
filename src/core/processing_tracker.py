"""
Processing tracker for incremental MOXIE data processing.

Keeps track of which files have been successfully processed to avoid
redundant reprocessing when new participants are added.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional
import hashlib


class ProcessingTracker:
    """
    Track processed files to enable incremental processing.

    Maintains a JSON log of successfully processed files with metadata
    like processing date, quality metrics summary, and file hash.
    """

    def __init__(self, tracker_file: Path):
        """
        Initialize processing tracker.

        Args:
            tracker_file: Path to JSON tracking file
        """
        self.tracker_file = Path(tracker_file)
        self.processed_files: Dict[str, Dict] = {}
        self.load()

    def load(self):
        """Load tracking data from file."""
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file, 'r') as f:
                    self.processed_files = json.load(f)
                print(f"Loaded processing log: {len(self.processed_files)} files tracked")
            except Exception as e:
                print(f"Warning: Could not load tracking file: {e}")
                self.processed_files = {}
        else:
            self.processed_files = {}

    def save(self):
        """Save tracking data to file."""
        self.tracker_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tracker_file, 'w') as f:
            json.dump(self.processed_files, f, indent=2)

    def get_file_hash(self, file_path: Path) -> str:
        """
        Compute MD5 hash of file to detect changes.

        Args:
            file_path: Path to file

        Returns:
            MD5 hash string
        """
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(8192), b''):
                md5.update(chunk)
        return md5.hexdigest()

    def is_processed(
        self,
        file_path: Path,
        check_hash: bool = True
    ) -> bool:
        """
        Check if file has been processed.

        Args:
            file_path: Path to ACQ file
            check_hash: If True, verify file hasn't changed since processing

        Returns:
            True if file has been processed (and is unchanged if check_hash=True)
        """
        file_key = str(file_path)

        if file_key not in self.processed_files:
            return False

        if check_hash:
            current_hash = self.get_file_hash(file_path)
            stored_hash = self.processed_files[file_key].get('file_hash')
            if current_hash != stored_hash:
                print(f"  File changed since last processing: {file_path.name}")
                return False

        return True

    def mark_processed(
        self,
        file_path: Path,
        participant_id: str,
        visit_type: str,
        success: bool = True,
        quality_summary: Optional[Dict] = None,
        error_message: Optional[str] = None
    ):
        """
        Mark a file as processed.

        Args:
            file_path: Path to processed file
            participant_id: Participant identifier
            visit_type: Visit type (TSST/PDST)
            success: Whether processing succeeded
            quality_summary: Optional quality metrics summary
            error_message: Optional error message if failed
        """
        file_key = str(file_path)

        self.processed_files[file_key] = {
            'participant_id': participant_id,
            'visit_type': visit_type,
            'filename': file_path.name,
            'processed_date': datetime.now().isoformat(),
            'success': success,
            'file_hash': self.get_file_hash(file_path),
            'quality_summary': quality_summary,
            'error_message': error_message
        }

        # Auto-save after each file
        self.save()

    def get_processed_participants(self) -> Set[str]:
        """
        Get set of participant IDs that have been processed.

        Returns:
            Set of participant IDs
        """
        return {
            info['participant_id']
            for info in self.processed_files.values()
            if info.get('success', False)
        }

    def get_unprocessed_files(self, all_files: List[Path]) -> List[Path]:
        """
        Filter list of files to only unprocessed ones.

        Args:
            all_files: List of all ACQ files

        Returns:
            List of files that haven't been processed or have changed
        """
        return [
            f for f in all_files
            if not self.is_processed(f, check_hash=True)
        ]

    def get_processing_stats(self) -> Dict:
        """
        Get statistics about processed files.

        Returns:
            Dictionary with processing statistics
        """
        total = len(self.processed_files)
        successful = sum(
            1 for info in self.processed_files.values()
            if info.get('success', False)
        )
        failed = total - successful

        participants = self.get_processed_participants()

        return {
            'total_files': total,
            'successful': successful,
            'failed': failed,
            'participants': len(participants),
            'participant_ids': sorted(list(participants))
        }

    def print_summary(self):
        """Print summary of processing history."""
        stats = self.get_processing_stats()

        print(f"\n{'='*60}")
        print(f"Processing History Summary")
        print(f"{'='*60}")
        print(f"Total files processed: {stats['total_files']}")
        print(f"  Successful: {stats['successful']}")
        print(f"  Failed: {stats['failed']}")
        print(f"Participants: {stats['participants']}")

        if stats['participant_ids']:
            print(f"  IDs: {', '.join(stats['participant_ids'])}")

        print(f"{'='*60}\n")

    def clear_participant(self, participant_id: str):
        """
        Remove a participant from tracking (force reprocessing).

        Args:
            participant_id: Participant ID to remove
        """
        keys_to_remove = [
            key for key, info in self.processed_files.items()
            if info.get('participant_id') == participant_id
        ]

        for key in keys_to_remove:
            del self.processed_files[key]

        self.save()
        print(f"Cleared {len(keys_to_remove)} files for participant {participant_id}")

    def clear_all(self):
        """Clear all tracking data (force reprocess everything)."""
        self.processed_files = {}
        self.save()
        print("Cleared all processing history")
