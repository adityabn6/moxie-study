# MOXIE Study Data Analysis

A comprehensive Python package for processing and analyzing physiological data from the MOXIE study (Trier Social Stress Test and Performance Debate Stress Test).

## Overview

The MOXIE study collects multi-channel physiological data during stress tests using the BIOPAC AcqKnowledge system. This codebase provides tools for:

- **Signal Processing**: Complete NeuroKit2-based processing for ECG, EDA, RSP, and Blood Pressure
- **Feature Extraction**: Basic (28 features) and Enhanced (66 features) extraction for stress research
- **Quality Assessment**: SNR and amplitude-based quality checks
- **Incremental Processing**: Track processed files, only process new data
- **Quality Analysis**: Comprehensive reports identifying protocol issues
- **Data Visualization**: Interactive plots and summary charts
- **Data Loading**: Automated discovery and loading of ACQ files
- **Time Windowing**: Event marker-based segmentation of study phases

## Project Structure

```
moxie_analysis/
├── src/
│   ├── core/              # Core data models and configuration
│   │   ├── data_models.py # BioData and DataObject classes
│   │   ├── window.py      # Time window definitions
│   │   └── config.py      # Configuration constants
│   ├── io/                # Input/output operations
│   │   ├── file_discovery.py  # ACQ file discovery
│   │   └── data_loader.py     # Data loading utilities
│   ├── quality/           # Quality assessment
│   │   ├── snr.py         # SNR quality checks
│   │   ├── amplitude.py   # Amplitude quality checks
│   │   └── report.py      # Quality reporting
│   ├── visualization/     # Bokeh visualizations
│   │   └── bokeh_plots.py
│   └── processing/        # NeuroKit2 signal processing
│       └── neurokit_signals.py
├── scripts/               # Main processing scripts
│   ├── quality_check.py              # Quality assessment workflow
│   ├── process_signals.py            # NeuroKit2 signal processing
│   ├── extract_features.py           # Basic feature extraction (28 features)
│   ├── extract_features_enhanced.py  # Enhanced feature extraction (66 features)
│   ├── analyze_quality.py            # Quality analysis and reporting
│   └── process_all.py                # Complete processing pipeline
├── output/                # Generated outputs
└── data/                  # Input data (not tracked)
```

## Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Setup

1. Clone or download this repository

2. Create a virtual environment (recommended):
```bash
cd moxie_analysis
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start: Signal Processing

Process physiological signals (ECG, EDA, RSP, Blood Pressure) using NeuroKit2:

```bash
# Process a single ACQ file
python scripts/process_signals.py "Participant Data/ID/Visit/Acqknowledge/file.acq" -o ./processed

# Process all ACQ files in data directory
python scripts/process_signals.py --all --data-dir "Participant Data" -o ./processed

# With verbose output
python scripts/process_signals.py "file.acq" -o ./processed -v
```

This will:
1. Load the ACQ file and extract all channels
2. **Process ECG**: R-peak detection, heart rate, P/Q/S/T wave delineation, cardiac phases
3. **Process EDA**: SCR detection, tonic/phasic decomposition, skin conductance responses
4. **Process RSP**: Respiratory rate, breathing cycle peaks/troughs, respiratory variability
5. **Process Blood Pressure**: Signal cleaning, statistical analysis, trend detection
6. Save processed signals as CSV files with all extracted features
7. Generate visualization plots for each signal

**Output**: For each signal, you get a CSV file with:
- Raw and cleaned signals
- Detected events (R-peaks, SCR peaks, respiratory cycles)
- Computed features (heart rate, skin conductance levels, breathing rate)
- Time vector for alignment

See [SIGNAL_PROCESSING_GUIDE.md](SIGNAL_PROCESSING_GUIDE.md) for comprehensive documentation.

### Quick Start: Feature Extraction

Extract aggregated physiological features for statistical analysis in R:

```bash
# Basic feature extraction (28 features - time-domain HRV, basic stats)
python scripts/extract_features.py --all -o features.csv

# Enhanced feature extraction (66 features - includes LF/HF ratio, breathing coordination, SCR dynamics)
python scripts/extract_features_enhanced.py --all -o features_enhanced.csv

# Process specific participant
python scripts/extract_features_enhanced.py --participant-id 124961 -v
```

This will:
1. Load processed signal CSVs from `process_signals.py`
2. Extract event markers to identify protocol phases (Baseline, Speech, Arithmetic, Recovery)
3. Calculate features for each time window
4. **Enhanced version adds**: HRV frequency-domain (LF/HF ratio), SCR dynamics (amplitude, rise time), multi-channel breathing coordination
5. Save aggregated features as CSV for regression analysis

**Output**: CSV with one row per protocol phase containing:
- **HRV metrics**: Heart rate, RMSSD, SDNN, pNN50, LF/HF ratio (enhanced)
- **EDA metrics**: Tonic level, SCR count, SCR amplitude/rise time (enhanced)
- **RSP metrics**: Breathing rate, amplitude, thoracic-abdominal coordination (enhanced)
- **BP metrics**: Mean, variability, trend

See [ENHANCED_FEATURES_COMPARISON.md](ENHANCED_FEATURES_COMPARISON.md) for detailed feature comparison and [OPTIMAL_STRESS_FEATURES.md](OPTIMAL_STRESS_FEATURES.md) for stress research recommendations.

### Quick Start: Quality Check

Process all ACQ files and generate quality reports:

```bash
python scripts/quality_check.py /path/to/Participant_Data -o ./output
```

This will:
1. Discover all ACQ files in the data directory
2. **Skip already-processed files** (incremental processing)
3. Load each new/changed file and extract all channels
4. Compute SNR and amplitude quality metrics
5. Generate interactive HTML visualizations
6. Create JSON quality reports

**New Feature:** Incremental processing automatically tracks completed files, so you only process new participants when you add them! See [INCREMENTAL_PROCESSING.md](INCREMENTAL_PROCESSING.md) for details.

### Command Line Options

```bash
python scripts/quality_check.py --help

usage: quality_check.py [-h] [-o OUTPUT] [-v] [--force] [--clear-participant ID] [--clear-all] data_dir

positional arguments:
  data_dir                    Directory containing participant data

optional arguments:
  -h, --help                  show this help message and exit
  -o OUTPUT, --output OUTPUT  Output directory (default: ./output)
  -v, --verbose               Print detailed information
  --force                     Force reprocess all files (ignore history)
  --clear-participant ID      Clear history for specific participant
  --clear-all                 Clear all processing history
```

**Incremental Processing Examples:**

```bash
# Normal: Only process new/changed files
python scripts/quality_check.py /path/to/data -o ./output

# Force reprocess everything (e.g., after updating parameters)
python scripts/quality_check.py /path/to/data -o ./output --force

# Reprocess specific participant
python scripts/quality_check.py /path/to/data -o ./output --clear-participant 124961
```

See [INCREMENTAL_PROCESSING.md](INCREMENTAL_PROCESSING.md) for detailed examples.

### Analyzing Results

After processing, analyze the quality data to identify patterns and protocol issues:

```bash
# Generate text report with recommendations
python scripts/analyze_quality.py ./output

# Generate visualizations (heatmaps, charts)
python scripts/visualize_quality.py ./output

# Export detailed CSV files for statistical analysis
python scripts/analyze_quality.py ./output --export-csv
```

This creates:
- **Text report** identifying participants/channels with quality concerns
- **Visualizations** showing quality patterns across the study
- **CSV files** for further analysis in R, SPSS, etc.
- **Recommendations** for addressing protocol issues

See [QUALITY_ANALYSIS_GUIDE.md](QUALITY_ANALYSIS_GUIDE.md) for detailed usage.

### Expected Data Structure

Your input data should follow this structure:

```
Participant_Data/
├── Participant_001/
│   ├── TSST Visit/
│   │   └── Acqknowledge/
│   │       └── session.acq
│   └── PDST Visit/
│       └── Acqknowledge/
│           └── session.acq
├── Participant_002/
│   └── ...
```

### Output Structure

Outputs are organized by participant and visit:

```
output/
├── Participant_001/
│   ├── TSST/
│   │   ├── quality_report.json
│   │   ├── ECG2108000293.html
│   │   ├── EDA2107000289.html
│   │   ├── RSP2106000165.html
│   │   └── ...
│   └── PDST/
│       └── ...
```

## Quality Metrics

### SNR (Signal-to-Noise Ratio)

- **Method**: Welch's power spectral density
- **Calculation**: `SNR = 10 * log10(1 / spectral_flatness)`
- **Window**: 30 seconds with 15 second overlap (configurable)
- **Threshold**: Default α = 0.5 (values below are flagged)
- **Visualization**: Red triangles mark poor quality windows

### Amplitude

- **Method**: Sum of squared signal / window duration
- **Baseline**: `minimum + β * standard_deviation` (β = 0.5)
- **Window**: 30 seconds with 15 second overlap (configurable)
- **Threshold**: Windows below baseline are flagged
- **Visualization**: Green squares mark poor quality windows

## Processed Channels

Default channels (from MOXIE protocol):

- `ECG2108000293` - Electrocardiography
- `EDA2107000289` - Electrodermal Activity
- `RSP2106000165` - Respiration (sensor 1)
- `RSP2208000207` - Respiration (sensor 2)
- `EMG2212000279` - Electromyography (sensor 1)
- `EMG2308000333` - Electromyography (sensor 2)
- `Blood Pressure - NIBP100E` - Non-invasive Blood Pressure
- `Custom, DA100C` - Custom measurement

Note: Actual channels may vary by participant. Missing channels are automatically skipped.

## Study Phases (Time Windows)

### TSST Visit (Trier Social Stress Test)

- Baseline Resting Period
- Task Introduction
- Speech Preparation
- Speech Period
- Arithmetic Period
- Recovery Period
- Debrief Period

### PDST Visit (Performance Debate Stress Test)

- Baseline Resting Period
- Survey Session (Debate Period)
- Recovery Period
- Debrief Period

Time windows are automatically extracted from event markers in the ACQ files.

## Configuration

Edit `src/core/config.py` to customize:

- Channel names
- Quality check parameters (window size, thresholds)
- Target event markers
- Visualization settings

## Development Roadmap

### Current Features (v0.3.0)
- ✓ ACQ file discovery and loading
- ✓ Quality assessment (SNR, Amplitude)
- ✓ Interactive visualizations
- ✓ Event marker-based time windowing
- ✓ **ECG processing** (R-peak detection, heart rate, P/Q/S/T wave delineation)
- ✓ **EDA processing** (phasic/tonic decomposition, SCR detection)
- ✓ **RSP processing** (breathing rate, respiratory variability, cycle detection)
- ✓ **Blood Pressure processing** (signal cleaning, statistical analysis)
- ✓ **Feature extraction** (basic: 28 features, enhanced: 66 features)
- ✓ **HRV analysis** (time-domain, frequency-domain, non-linear metrics)
- ✓ **Stress biomarkers** (LF/HF ratio, breathing coordination, SCR dynamics)
- ✓ Incremental processing (skip already processed files)
- ✓ Comprehensive quality analysis and reporting

### Planned Features (v0.4.0)
- Statistical analysis across participants
- EMG processing (muscle activity detection)
- Cross-signal synchrony analysis
- Automated outlier detection

### Future Enhancements
- Automated outlier detection
- Cross-participant comparison
- Real-time processing capabilities
- Batch processing with parallel execution
- Database integration for large datasets
- Machine learning-based quality assessment

## Troubleshooting

### No ACQ files found
- Check that data directory structure matches expected format
- Ensure ACQ files are in `{Participant}/TSST Visit/Acqknowledge/` folders
- Try running with `-v` flag for detailed directory scanning

### Missing channels
- Not all participants have all channels - this is normal
- Check the console output to see which channels were found
- Modify `DEFAULT_CHANNELS` in `config.py` if needed

### Out of memory
- Reduce the number of files processed at once
- Increase downsample rates in visualization
- Process participants one at a time

## Contributing

This is a research codebase under active development. To contribute:

1. Document any changes clearly
2. Maintain backward compatibility with existing scripts
3. Add tests for new functionality
4. Update this README for significant changes

## License

Research use only - See study protocol for data usage guidelines.

## Contact

For questions about the MOXIE study or this codebase, contact the research team.

## Documentation

For comprehensive documentation, see:
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Complete documentation navigation guide
- **[ENHANCED_FEATURES_COMPARISON.md](ENHANCED_FEATURES_COMPARISON.md)** - Feature extraction guide (recommended)
- **[SIGNAL_PROCESSING_GUIDE.md](SIGNAL_PROCESSING_GUIDE.md)** - Signal processing details
- **[SESSION_SUMMARY.md](SESSION_SUMMARY.md)** - Latest work summary
- **[DOCUMENTATION_CHANGELOG.md](DOCUMENTATION_CHANGELOG.md)** - Version history

## Acknowledgments

Built using:
- [bioread](https://github.com/uwmadison-chm/bioread) - ACQ file parsing
- [NeuroKit2](https://neuropsychology.github.io/NeuroKit/) - Physiological signal processing
- [Bokeh](https://bokeh.org/) - Interactive visualizations
- [SciPy](https://scipy.org/) - Signal processing algorithms
