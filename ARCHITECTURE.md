# MOXIE Analysis - Architecture Overview

## Design Philosophy

This codebase is designed with the following principles:

1. **Modularity**: Separate concerns into distinct modules (I/O, quality, processing, visualization)
2. **Extensibility**: Easy to add new signal processing methods and quality metrics
3. **Maintainability**: Clear naming, comprehensive documentation, type hints
4. **Reproducibility**: Configuration-driven with version control
5. **User-friendly**: Both CLI scripts and programmatic API available

## Core Architecture

### Data Flow

```
ACQ Files → Data Loading → BioData Objects → Quality Assessment → Visualization
                ↓              ↓                    ↓                  ↓
           Event Markers   Channels +         SNR + Amplitude    HTML Reports
                          Time Windows         Metrics
```

### Module Hierarchy

```
src/
├── core/           # Foundation - data structures and config
│   ├── data_models.py   # BioData, DataObject classes
│   ├── window.py        # Time window definitions
│   └── config.py        # Centralized configuration
│
├── io/             # Data input/output
│   ├── file_discovery.py  # Find ACQ files
│   └── data_loader.py     # Load and parse ACQ files
│
├── quality/        # Quality assessment
│   ├── snr.py           # SNR-based quality
│   ├── amplitude.py     # Amplitude-based quality
│   └── report.py        # Quality reporting
│
├── visualization/  # Interactive plots
│   └── bokeh_plots.py   # Bokeh HTML visualizations
│
└── processing/     # Signal processing (extensible)
    └── (future: ecg.py, eda.py, rsp.py, etc.)
```

## Key Classes

### BioData
**Purpose**: Central container for all data from one recording session

**Responsibilities**:
- Store multiple DataObjects (channels)
- Manage time windows
- Provide unified interface for data access
- Track quality metrics

**Key Methods**:
- `get_dataframe(name)`: Retrieve channel data
- `append_to_dataframe(data_obj)`: Add new channel or derived data
- `add_window(window)`: Register time window
- `return_downsample_dataframe(name, rate)`: Get downsampled data for plotting

### DataObject
**Purpose**: Represent a single physiological channel

**Responsibilities**:
- Store signal data and metadata
- Maintain time vector
- Store quality features (SNR, amplitude flags)

**Attributes**:
- `data`: Signal values (numpy array)
- `name`: Channel identifier
- `sampling_rate`: Hz
- `time_column`: Time vector in seconds
- `snr_feature`: Binary quality flags (optional)
- `amplitude_feature`: Binary quality flags (optional)

### Window
**Purpose**: Define temporal segments based on event markers

**Responsibilities**:
- Parse event markers from ACQ file
- Calculate start/end times
- Provide masks for data filtering
- Support nth-occurrence selection (e.g., "2nd arithmetic period")

**Key Methods**:
- `return_mask(df)`: Boolean mask for filtering
- `is_valid()`: Check if window was found
- `get_duration()`: Window length in seconds

## Quality Assessment Pipeline

### SNR (Signal-to-Noise Ratio)

**Algorithm**:
1. Divide signal into overlapping windows (30s window, 15s overlap)
2. Compute power spectral density using Welch's method
3. Calculate spectral flatness: `geometric_mean(PSD) / arithmetic_mean(PSD)`
4. Convert to SNR in dB: `10 * log10(1 / spectral_flatness)`
5. Flag windows where SNR < threshold (α = 0.5)

**Output**:
- New DataObject: `{channel_name}_SNR`
- Binary flags stored in `snr_feature` attribute
- Summary statistics printed to console

### Amplitude

**Algorithm**:
1. Divide signal into overlapping windows (30s window, 15s overlap)
2. Compute amplitude: `sum(signal²) / window_duration`
3. Calculate baseline: `min(signal²) + β * std(signal²)`
4. Flag windows where amplitude < baseline

**Output**:
- New DataObject: `{channel_name}_Amplitude`
- Binary flags stored in `amplitude_feature` attribute
- Summary statistics printed to console

## Visualization System

### Interactive Bokeh Plots

**Features**:
- Shared x-axis across all plots for synchronized navigation
- Range slider for time window selection
- Quality flag overlays (triangles for SNR, squares for amplitude)
- Time window annotations (colored boxes with labels)
- Downsampling for performance

**Implementation**:
- Each channel gets its own subplot
- Plots are vertically stacked
- JavaScript-linked range slider
- HTML output for easy sharing

## Configuration System

All parameters centralized in `src/core/config.py`:

```python
QUALITY_CHECK_PARAMS = {
    "window_size_seconds": 30,
    "overlap_seconds": 15,
    "snr_alpha_threshold": 0.5,
    "amplitude_beta": 0.5
}

DEFAULT_CHANNELS = [
    "EDA2107000289",
    "EMG2212000279",
    # ... etc
]
```

**Benefits**:
- Single source of truth
- Easy to modify parameters
- Can be overridden programmatically
- Version-controlled with code

## Processing Workflow

### Standard Pipeline (quality_check.py)

```
1. Discovery
   └→ Find all ACQ files in directory tree

2. For each file:
   ├→ Load ACQ file (bioread + neurokit2)
   ├→ Create BioData object
   ├→ Extract event markers
   ├→ Create time windows (TSST or PDST)
   ├→ For each channel:
   │  ├→ Compute SNR over windows
   │  ├→ Compute Amplitude over windows
   │  └→ Append quality DataObjects
   ├→ Generate quality report (JSON)
   └→ Create visualizations (HTML)

3. Summary
   └→ Print overall statistics
```

## Extension Points

### Adding New Quality Metrics

1. Create new module in `src/quality/`
2. Implement computation function
3. Return DataObject with quality flags
4. Update visualization to show new metric
5. Add to quality report

**Example**: Adding kurtosis-based quality check

```python
# src/quality/kurtosis.py
def compute_and_append_kurtosis(biodata, channel_name, ...):
    # Compute kurtosis over windows
    # Create DataObject with results
    # Append to biodata
    pass
```

### Adding Signal Processing

1. Create module in `src/processing/`
2. Use NeuroKit2 or custom algorithms
3. Append processed signals as new DataObjects
4. Update visualization pipeline

**Example**: ECG R-peak detection

```python
# src/processing/ecg.py
import neurokit2 as nk

def process_ecg(biodata, channel_name):
    data, time = biodata.get_dataframe(channel_name)
    signals, info = nk.ecg_process(data, sampling_rate=...)

    # Append processed signals
    biodata.append_to_dataframe(
        DataObject(signals['ECG_Clean'], f"{channel_name}_Clean", ...)
    )
```

## Future Enhancements

### Phase 1 (Near-term)
- [ ] ECG: R-peak detection, HRV time/frequency domain
- [ ] EDA: Phasic/tonic decomposition, SCR detection
- [ ] RSP: Peak/trough detection, breathing rate
- [ ] Feature extraction per time window
- [ ] Statistical comparisons (baseline vs. stress)

### Phase 2 (Medium-term)
- [ ] Automated artifact detection
- [ ] Cross-participant analysis
- [ ] Integration with statistical packages (R, statsmodels)
- [ ] Database backend for large studies
- [ ] Parallel processing for batch jobs

### Phase 3 (Long-term)
- [ ] Machine learning pipelines
- [ ] Real-time processing support
- [ ] Web-based dashboard
- [ ] Multi-modal analysis (physio + behavioral)
- [ ] Standardized output formats (BIDS-like)

## Testing Strategy (To Be Implemented)

```
tests/
├── test_data_models.py   # Unit tests for BioData, DataObject
├── test_quality.py       # Test SNR, amplitude calculations
├── test_io.py            # Test file discovery, loading
├── fixtures/             # Sample ACQ files for testing
└── integration/          # End-to-end workflow tests
```

## Performance Considerations

### Current Bottlenecks
1. **File I/O**: ACQ files can be large (100+ MB)
2. **Welch's method**: Computationally expensive for high sampling rates
3. **Visualization**: Plotting millions of points

### Optimizations Implemented
1. **Downsampling**: Reduce data for visualization
2. **Windowing**: Process in chunks rather than all at once
3. **Lazy loading**: Only load channels that are needed

### Future Optimizations
1. **Parallel processing**: Process multiple files simultaneously
2. **Caching**: Store intermediate results
3. **GPU acceleration**: For spectral analysis
4. **Incremental processing**: Resume interrupted jobs

## Dependencies

### Core
- `numpy`: Numerical operations
- `pandas`: Data structures
- `scipy`: Signal processing (Welch's method)

### I/O
- `bioread`: Parse BIOPAC ACQ files
- `neurokit2`: ACQ reading, signal processing

### Visualization
- `bokeh`: Interactive HTML plots

### Future
- `scikit-learn`: Machine learning
- `statsmodels`: Statistical analysis
- `mne`: Advanced signal processing

## Design Decisions

### Why BioData instead of pure DataFrames?
- **Type safety**: Explicit data structures with validation
- **Metadata**: Sampling rates, quality flags per channel
- **Flexibility**: Can store non-uniform sampling rates
- **Extensibility**: Easy to add methods without monkey-patching

### Why Bokeh instead of Matplotlib?
- **Interactivity**: Range slider, linked plots
- **No backend needed**: Pure HTML/JavaScript
- **Sharing**: HTML files can be emailed or hosted
- **Performance**: Handles large datasets well

### Why modular structure instead of monolithic scripts?
- **Testability**: Each module can be tested independently
- **Reusability**: Import quality checks into other projects
- **Maintainability**: Changes are localized
- **Collaboration**: Multiple people can work on different modules

## Conclusion

This architecture provides a solid foundation for MOXIE data analysis with room for growth. The modular design allows incremental enhancement while maintaining backward compatibility.

For questions or suggestions, consult the development team.
