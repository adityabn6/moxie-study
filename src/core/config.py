"""
Configuration constants for MOXIE study data processing.
"""

# Target event markers for TSST and PDST visits
TSST_TARGET_MARKERS = [
    "tsst arithmetic period",
    "speech period",
    "tsst prep period",
    "baseline resting period",
    "post stress resting period",
    "thought listing",
    "recovery period",
    "arithmetic period",
    "task introduction",
    "debrief period",
    "speech preperation",
    "survey session"
]

PDST_TARGET_MARKERS = [
    "baseline resting period",
    "post stress resting period",
    "recovery period",
    "debrief period",
    "survey session"
]

# Default physiological channels to process
DEFAULT_CHANNELS = [
    "EDA2107000289",           # Electrodermal Activity
    "EMG2212000279",           # Electromyography 1
    "EMG2308000333",           # Electromyography 2
    "ECG2108000293",           # Electrocardiography
    "RSP2208000207",           # Respiration 1
    "RSP2106000165",           # Respiration 2
    "Blood Pressure - NIBP100E",  # Non-invasive Blood Pressure
    "Custom, DA100C"           # Custom measurement
]

# Quality check parameters
QUALITY_CHECK_PARAMS = {
    "window_size_seconds": 30,
    "overlap_seconds": 15,
    "snr_alpha_threshold": 0.5,   # SNR threshold
    "amplitude_beta": 0.5          # Amplitude baseline factor
}

# Visit types
VISIT_TYPES = ["TSST Visit", "PDST Visit"]

# Visualization parameters
VISUALIZATION_PARAMS = {
    "default_downsample_rate": 20,
    "plot_width": 800,
    "plot_height": 300,
    "color_palette": ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'cyan']
}
