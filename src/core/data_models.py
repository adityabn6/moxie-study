"""
Core data models for MOXIE physiological data analysis.

Classes:
    DataObject: Represents a single physiological channel with metadata
    BioData: Container for multiple DataObjects with time windows and quality metrics
"""

import numpy as np
import pandas as pd
from typing import List, Optional, Tuple


class DataObject:
    """
    Represents a single physiological data channel.

    Attributes:
        data: The physiological signal data
        name: Channel name (e.g., 'ECG2108000293')
        sampling_rate: Sampling rate in Hz
        time_column: Time vector in seconds
        snr_feature: Binary array indicating SNR quality (1=poor, 0=good)
        amplitude_feature: Binary array indicating amplitude quality (1=poor, 0=good)
    """

    def __init__(
        self,
        data: np.ndarray,
        name: str,
        sampling_rate: float,
        snr_feature: Optional[np.ndarray] = None,
        amplitude_feature: Optional[np.ndarray] = None
    ):
        self.data = data
        self.name = name
        self.sampling_rate = sampling_rate

        # Generate time vector
        max_samples = len(data)
        indices = np.arange(max_samples)
        self.time_column = indices / sampling_rate

        # Quality features
        self.snr_feature = snr_feature
        self.amplitude_feature = amplitude_feature

    def __repr__(self):
        return (f"DataObject(name='{self.name}', "
                f"samples={len(self.data)}, "
                f"sampling_rate={self.sampling_rate}Hz, "
                f"duration={self.time_column[-1]:.2f}s)")


class BioData:
    """
    Container for all physiological data channels from a single recording session.

    This class serves as the central data structure for MOXIE analysis, holding
    multiple DataObjects (channels) and associated metadata like time windows.

    Attributes:
        Data: List of DataObject instances
        start_time: Recording start time in seconds
        end_time: Recording end time in seconds
        Window_List: List of Window objects defining study phases
        ChannelNames: List of all channel names
    """

    def __init__(self, Data: List[DataObject]):
        self.Data = Data
        self.start_time = 0
        self.end_time = 0

        # Calculate max end time across all channels
        for data in Data:
            self.end_time = max(self.end_time, data.time_column.max())

        self.Window_List = []
        self.ChannelNames = [data.name for data in Data]

    def get_dataframe(self, name: str) -> Optional[Tuple[pd.Series, np.ndarray]]:
        """
        Get data and time vector for a specific channel.

        Args:
            name: Channel name to retrieve

        Returns:
            Tuple of (data_series, time_array) or None if not found
        """
        for data in self.Data:
            if data.name == name:
                return data.data, data.time_column

        print(f"Warning: Data with name '{name}' not found")
        return None

    def get_snr_feature(self, name: str) -> Optional[np.ndarray]:
        """Get SNR quality feature for a channel."""
        for data in self.Data:
            if data.name == name:
                return data.snr_feature
        return None

    def get_amplitude_feature(self, name: str) -> Optional[np.ndarray]:
        """Get amplitude quality feature for a channel."""
        for data in self.Data:
            if data.name == name:
                return data.amplitude_feature
        return None

    def append_to_dataframe(self, data: DataObject) -> None:
        """
        Append a new DataObject to the collection.

        Args:
            data: DataObject to append
        """
        self.Data.append(data)
        self.end_time = max(self.end_time, data.time_column.max())
        self.ChannelNames.append(data.name)

    def add_window(self, window) -> None:
        """
        Add a time window to the collection.

        Args:
            window: Window object defining a study phase
        """
        self.Window_List.append(window)

    def print_metadata(self) -> None:
        """Print metadata for all channels."""
        print(f"\n{'='*60}")
        print(f"BioData Summary: {len(self.Data)} channels")
        print(f"Total Duration: {self.end_time:.2f} seconds ({self.end_time/60:.2f} minutes)")
        print(f"{'='*60}\n")

        for data in self.Data:
            print(f"Channel: {data.name}")
            print(f"  Sampling Rate: {data.sampling_rate} Hz")
            print(f"  Samples: {len(data.data)}")
            print(f"  Duration: {data.time_column[-1]:.2f} seconds")
            print(f"  Has SNR: {data.snr_feature is not None}")
            print(f"  Has Amplitude: {data.amplitude_feature is not None}")
            print()

    def return_downsample_dataframe(
        self,
        name: str,
        new_sampling_rate: int
    ) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Return downsampled data for visualization.

        Args:
            name: Channel name
            new_sampling_rate: Target sampling rate in Hz

        Returns:
            Tuple of (downsampled_data, downsampled_time) or None
        """
        for data in self.Data:
            if data.name == name:
                ratio = int(data.sampling_rate / new_sampling_rate)
                if ratio < 1:
                    ratio = 1
                data_downsampled = data.data[::ratio]
                time_downsampled = data.time_column[::ratio]
                return data_downsampled, time_downsampled

        print(f"Warning: Data with name '{name}' not found")
        return None

    def get_channel_count(self) -> int:
        """Get total number of channels."""
        return len(self.Data)

    def get_window_count(self) -> int:
        """Get total number of time windows."""
        return len(self.Window_List)

    def __repr__(self):
        return (f"BioData(channels={len(self.Data)}, "
                f"windows={len(self.Window_List)}, "
                f"duration={self.end_time:.2f}s)")
