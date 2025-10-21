"""
Time window definition for MOXIE study phases.

The Window class defines temporal segments of the recording based on event markers,
allowing for phase-specific analysis (e.g., baseline, stress task, recovery).
"""

import pandas as pd
from typing import List, Optional


class Window:
    """
    Represents a temporal window within a physiological recording.

    Windows are defined by start and end event markers from the ACQ file.
    This allows analysis to be segmented by study phases (baseline, task, recovery, etc.).

    Attributes:
        name: Display name for the window
        start_flag: Event marker text for window start
        end_flag: Event marker text for window end
        start_time: Start time in seconds
        end_time: End time in seconds
        start_index: Which occurrence of start_flag to use (1-indexed)
        end_index: Which occurrence of end_flag to use (1-indexed)
    """

    def __init__(
        self,
        start_flag: str,
        end_flag: str,
        name: str,
        start_index: int,
        end_index: int,
        ACQ_Sampling_Rate: float,
        acq,
        target_markers: Optional[List[str]] = None
    ):
        """
        Initialize a time window from event markers.

        Args:
            start_flag: Event marker text for start
            end_flag: Event marker text for end
            name: Display name for the window
            start_index: Which occurrence of start_flag (1-indexed)
            end_index: Which occurrence of end_flag (1-indexed)
            ACQ_Sampling_Rate: Sampling rate from ACQ file
            acq: Bioread ACQ file object
            target_markers: Optional list of valid marker names for validation
        """
        self.name = name
        self.start_flag = start_flag
        self.end_flag = end_flag
        self.start_time = None
        self.end_time = None
        self.start_marker = None
        self.end_marker = None
        self.ACQ_Sampling_Rate = ACQ_Sampling_Rate

        # Validate markers if target list provided
        if target_markers:
            if start_flag.lower() not in target_markers:
                print(f"Warning: Window '{name}' - start marker '{start_flag}' "
                      f"not in target markers list")
            if end_flag.lower() not in target_markers:
                print(f"Warning: Window '{name}' - end marker '{end_flag}' "
                      f"not in target markers list")

        # Find start marker
        counter = 1
        for marker in acq.event_markers:
            if self.start_flag.lower() == marker.text.lower():
                self.start_marker = marker
                self.start_time = marker.sample_index / ACQ_Sampling_Rate
                if counter == start_index:
                    break
                counter += 1

        # Find end marker
        counter = 1
        for marker in acq.event_markers:
            if self.end_flag.lower() == marker.text.lower():
                self.end_marker = marker
                self.end_time = marker.sample_index / ACQ_Sampling_Rate
                if counter == end_index:
                    break
                counter += 1

        # Handle invalid windows
        if self.start_time is None or self.end_time is None:
            print(f"Warning: Window '{name}' invalid - start or end time is None")
            print(f"  Start flag: '{start_flag}' (occurrence {start_index})")
            print(f"  End flag: '{end_flag}' (occurrence {end_index})")
            self.start_time = 0
            self.end_time = 0

    def fix_window(self, new_start_time: float, new_end_time: float) -> None:
        """
        Manually override window times.

        Args:
            new_start_time: New start time in seconds
            new_end_time: New end time in seconds
        """
        self.start_time = new_start_time
        self.end_time = new_end_time

    def return_mask(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate a boolean mask for filtering data within this window.

        Args:
            df: DataFrame with 'time_seconds' column

        Returns:
            Boolean mask (True for points within window)
        """
        mask = (df["time_seconds"] > self.start_time) & \
               (df["time_seconds"] <= self.end_time)
        return mask

    def get_duration(self) -> float:
        """Get window duration in seconds."""
        if self.start_time is not None and self.end_time is not None:
            return self.end_time - self.start_time
        return 0.0

    def get_duration_minutes(self) -> float:
        """Get window duration in minutes."""
        return self.get_duration() / 60.0

    def print_info(self) -> None:
        """Print detailed window information."""
        print(f"\nWindow: {self.name}")
        print(f"  Start Time: {self.start_time:.2f}s")
        print(f"  End Time: {self.end_time:.2f}s")
        print(f"  Duration: {self.get_duration():.2f}s ({self.get_duration_minutes():.2f} min)")
        print(f"  Start Marker: {self.start_marker}")
        print(f"  End Marker: {self.end_marker}")

    def is_valid(self) -> bool:
        """Check if window has valid start and end times."""
        return (self.start_time is not None and
                self.end_time is not None and
                self.start_time != 0 and
                self.end_time != 0 and
                self.end_time > self.start_time)

    def __repr__(self):
        return (f"Window(name='{self.name}', "
                f"start={self.start_time:.2f}s, "
                f"end={self.end_time:.2f}s, "
                f"duration={self.get_duration():.2f}s)")
