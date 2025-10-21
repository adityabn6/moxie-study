# MOXIE Study Data Analysis

A comprehensive Python package for processing and analyzing physiological data from the MOXIE study (Trier Social Stress Test and Performance Debate Stress Test).

## Overview

The MOXIE study collects multi-channel physiological data during stress tests using the BIOPAC AcqKnowledge system. This codebase provides tools for:

- **Quality Assessment**: SNR and amplitude-based quality checks
- **Incremental Processing**: Track processed files, only process new data
- **Quality Analysis**: Comprehensive reports identifying protocol issues
- **Data Visualization**: Interactive plots and summary charts
- **Data Loading**: Automated discovery and loading of ACQ files
- **Time Windowing**: Event marker-based segmentation of study phases
- **Signal Processing**: ECG, EDA, RSP, EMG analysis (in development)

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
│   └── processing/        # Signal processing (in development)
├── scripts/               # Main processing scripts
│   ├── quality_check.py   # Quality assessment workflow
│   └── process_all.py     # Complete processing pipeline
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

### Current Features (v0.1.0)
- ✓ ACQ file discovery and loading
- ✓ Quality assessment (SNR, Amplitude)
- ✓ Interactive visualizations
- ✓ Event marker-based time windowing

### Planned Features (v0.2.0)
- ECG processing (R-peak detection, HRV analysis)
- EDA processing (phasic/tonic decomposition, SCR detection)
- RSP processing (breathing rate, RRV)
- Feature extraction per time window
- Statistical analysis across participants

### Future Enhancements
- Automated outlier detection
- Cross-participant comparison
- Integration with NeuroKit2 MCP server
- Batch processing with parallel execution
- Database integration for large datasets

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

## Acknowledgments

Built using:
- [bioread](https://github.com/uwmadison-chm/bioread) - ACQ file parsing
- [NeuroKit2](https://neuropsychology.github.io/NeuroKit/) - Physiological signal processing
- [Bokeh](https://bokeh.org/) - Interactive visualizations
- [SciPy](https://scipy.org/) - Signal processing algorithms
