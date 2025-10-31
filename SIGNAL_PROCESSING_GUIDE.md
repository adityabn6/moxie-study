# MOXIE Signal Processing Guide

Complete documentation for physiological signal processing using NeuroKit2.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Signal Types](#signal-types)
4. [Usage Examples](#usage-examples)
5. [Output Files](#output-files)
6. [Processing Details](#processing-details)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Usage](#advanced-usage)

---

## Overview

The MOXIE signal processing pipeline uses [NeuroKit2](https://neuropsychology.github.io/NeuroKit/), a comprehensive Python package for neurophysiological signal processing. This pipeline processes four main signal types from BIOPAC AcqKnowledge files:

- **ECG (Electrocardiography)**: Heart activity and cardiac features
- **EDA (Electrodermal Activity)**: Skin conductance and arousal
- **RSP (Respiration)**: Breathing patterns and respiratory cycles
- **Blood Pressure (NIBP)**: Cardiovascular hemodynamics

### Key Features

✅ **Automatic Processing**: One command processes all signal types
✅ **Feature Extraction**: Extracts clinically relevant features automatically
✅ **Quality Visualization**: Generates plots for visual inspection
✅ **CSV Export**: All processed data saved in analysis-ready format
✅ **Batch Processing**: Process entire datasets efficiently
✅ **Event Marker Support**: Integrates with MOXIE study time windows

---

## Quick Start

### Process a Single File

```bash
python scripts/process_signals.py "Participant Data/127476/PDST Visit/Acqknowledge/file.acq" -o ./output
```

### Process All Files

```bash
python scripts/process_signals.py --all --data-dir "Participant Data" -o ./processed
```

### Basic Options

```bash
# Verbose output (show processing details)
python scripts/process_signals.py "file.acq" -o ./output -v

# Save CSV files only (no plots)
python scripts/process_signals.py "file.acq" -o ./output --no-save
```

---

## Signal Types

### 1. ECG (Electrocardiography)

**What it measures**: Electrical activity of the heart

**Extracted Features**:
- **R-peaks**: Heartbeat detection
- **Heart Rate**: Beats per minute (BPM)
- **P/Q/S/T waves**: Cardiac cycle components
- **Cardiac Phases**: Atrial and ventricular phases
- **Quality Indicators**: Signal quality assessment

**Processing Method**: NeuroKit2's `ecg_process()` using the default 'neurokit' algorithm

**Typical Output Columns**:
```
ECG_Raw, ECG_Clean, ECG_Rate, ECG_Quality, ECG_R_Peaks,
ECG_P_Peaks, ECG_Q_Peaks, ECG_S_Peaks, ECG_T_Peaks,
ECG_Phase_Atrial, ECG_Phase_Ventricular, Time
```

**Clinical Applications**:
- Heart rate variability (HRV) analysis
- Stress response assessment
- Cardiac cycle timing
- Autonomic nervous system activity

---

### 2. EDA (Electrodermal Activity)

**What it measures**: Skin conductance related to sympathetic nervous system arousal

**Extracted Features**:
- **SCR Peaks**: Skin conductance responses
- **Tonic Component**: Baseline skin conductance level
- **Phasic Component**: Rapid changes in response to stimuli
- **SCR Metrics**: Onset, amplitude, rise time, recovery

**Processing Method**: NeuroKit2's `eda_process()` using 'neurokit' method

**Typical Output Columns**:
```
EDA_Raw, EDA_Clean, EDA_Tonic, EDA_Phasic,
SCR_Onsets, SCR_Peaks, SCR_Height, SCR_Amplitude,
SCR_RiseTime, SCR_Recovery, SCR_RecoveryTime, Time
```

**Clinical Applications**:
- Emotional arousal measurement
- Stress response quantification
- Cognitive load assessment
- Lie detection research

---

### 3. RSP (Respiration)

**What it measures**: Breathing patterns and respiratory cycles

**Extracted Features**:
- **Breathing Rate**: Breaths per minute
- **Respiratory Cycles**: Inhalation/exhalation detection
- **Amplitude**: Breathing depth
- **RVT**: Respiratory volume per time
- **Symmetry Metrics**: Breathing pattern characteristics

**Processing Method**: NeuroKit2's `rsp_process()` using 'khodadad2018' algorithm

**Typical Output Columns**:
```
RSP_Raw, RSP_Clean, RSP_Amplitude, RSP_Rate, RSP_RVT,
RSP_Phase, RSP_Phase_Completion, RSP_Symmetry_PeakTrough,
RSP_Symmetry_RiseDecay, RSP_Peaks, RSP_Troughs, Time
```

**Clinical Applications**:
- Respiratory rate variability (RRV)
- Breathing pattern analysis
- Stress-induced hyperventilation detection
- Cardiorespiratory synchronization

**Note**: MOXIE typically records two respiratory channels (RSP2106000165, RSP2208000207), both are processed independently.

---

### 4. Blood Pressure (NIBP)

**What it measures**: Non-invasive blood pressure readings

**Extracted Features**:
- **Cleaned Signal**: Butterworth filtered BP signal
- **Statistical Metrics**: Mean, std, min, max, median
- **Trend Analysis**: Overall pressure patterns

**Processing Method**: Custom signal filtering (NeuroKit2 doesn't have dedicated BP processing)

**Typical Output Columns**:
```
BP_Raw, BP_Clean, Time
```

**Statistical Info** (in metadata):
- Mean_BP, Std_BP, Min_BP, Max_BP, Median_BP

**Clinical Applications**:
- Cardiovascular response to stress
- Blood pressure reactivity
- Hemodynamic patterns

**Note**: Blood pressure in MOXIE is typically intermittent (measured at intervals), not continuous, so processed data may contain gaps.

---

## Usage Examples

### Example 1: Process Single Participant, Single Visit

```bash
python scripts/process_signals.py \
    "Participant Data/127476/PDST Visit/Acqknowledge/PDST_Acqknowledge_127476_10_30_2025.acq" \
    -o "./processed/127476/PDST" \
    -v
```

**Output**:
```
processed/127476/PDST/
├── ECG2108000293_processed.csv
├── ECG2108000293_plot.png
├── EDA2107000289_processed.csv
├── EDA2107000289_plot.png
├── RSP2106000165_processed.csv
├── RSP2106000165_plot.png
├── RSP2208000207_processed.csv
├── RSP2208000207_plot.png
├── Blood Pressure - NIBP100E_processed.csv
└── Blood Pressure - NIBP100E_plot.png
```

---

### Example 2: Batch Process All Participants

```bash
python scripts/process_signals.py \
    --all \
    --data-dir "Participant Data" \
    -o "./processed" \
    --verbose
```

This will:
1. Discover all `.acq` files in the data directory
2. Process each file's ECG, EDA, RSP, and BP channels
3. Save outputs organized by participant/visit
4. Generate summary statistics

**Expected Processing Time**: ~30 minutes per 2-hour recording at 2000 Hz

---

### Example 3: Quick Analysis (No Plots)

```bash
python scripts/process_signals.py \
    "file.acq" \
    -o ./output \
    --no-save
```

Saves CSV files only, skipping visualization generation for faster processing.

---

## Output Files

### CSV File Structure

Each processed signal produces a CSV file with the following structure:

**Example: ECG2108000293_processed.csv**

| Time | ECG_Raw | ECG_Clean | ECG_Rate | ECG_R_Peaks | ... |
|------|---------|-----------|----------|-------------|-----|
| 0.0005 | 0.234 | 0.231 | 0 | 0 | ... |
| 0.0010 | 0.235 | 0.232 | 0 | 0 | ... |
| 0.0015 | 0.237 | 0.234 | 78.5 | 0 | ... |
| ... | ... | ... | ... | ... | ... |

**Key Points**:
- **Time column**: Timestamp in seconds from recording start
- **_Raw**: Original unprocessed signal
- **_Clean**: Filtered/cleaned signal
- **_Peaks/Events**: Binary markers (1 = event detected, 0 = no event)
- **_Rate**: Instantiated rate (HR, breathing rate)
- **One row per sample**: File size = samples × features

---

### Plot Files

Each signal generates a visualization PNG showing:

**ECG/EDA/RSP Plots**:
- Raw vs. cleaned signal comparison
- Detected events (peaks, cycles)
- Rate/amplitude traces
- Phase information

**Blood Pressure Plots**:
- Time series with raw/cleaned overlay
- Distribution histogram
- Statistical annotations

**Resolution**: 150 DPI, suitable for presentations and reports

---

### File Sizes

Typical file sizes for a 2-hour recording at 2000 Hz sampling rate:

| Signal | Samples | CSV Size | Plot Size |
|--------|---------|----------|-----------|
| ECG | 14.1M | ~2.1 GB | ~500 KB |
| EDA | 14.1M | ~1.5 GB | ~500 KB |
| RSP (each) | 14.1M | ~2.2 GB | ~500 KB |
| Blood Pressure | 14.1M | ~600 MB | ~300 KB |

**Total**: ~8-9 GB per complete session

**Storage Recommendation**: Ensure adequate disk space before batch processing.

---

## Processing Details

### ECG Processing Pipeline

```python
# Internal processing steps (automated)
1. Signal loading from ACQ file
2. Cleaning using NeuroKit2 filtering
3. R-peak detection (Pan-Tompkins algorithm)
4. Heart rate computation
5. Wave delineation (P, Q, S, T detection)
6. Quality assessment
7. CSV export with all features
```

**Algorithms Used**:
- **Cleaning**: Bandpass filter (0.5-40 Hz)
- **R-peak Detection**: Pan-Tompkins (default) or alternative methods
- **Wave Delineation**: Discrete wavelet transform (DWT)

---

### EDA Processing Pipeline

```python
1. Signal loading
2. Low-pass filtering (remove high-frequency noise)
3. Tonic-phasic decomposition (cvxEDA)
4. SCR peak detection
5. SCR characteristic extraction
6. Export with tonic/phasic components
```

**Algorithms Used**:
- **Decomposition**: cvxEDA (convex optimization)
- **Peak Detection**: Continuous wavelet transform
- **Feature Extraction**: Automated SCR metrics

---

### RSP Processing Pipeline

```python
1. Signal loading
2. Bandpass filtering
3. Peak/trough detection (breathing cycles)
4. Breathing rate computation
5. Respiratory variability metrics
6. Symmetry analysis
7. Feature export
```

**Algorithms Used**:
- **Filtering**: Butterworth bandpass (0.1-0.5 Hz)
- **Peak Detection**: Khodadad 2018 algorithm
- **Rate Computation**: Instantaneous breathing rate

---

### Blood Pressure Processing

```python
1. Signal loading
2. Butterworth high-pass filtering (0.5 Hz cutoff)
3. Statistical feature computation
4. Trend analysis
5. CSV export with statistics
```

**Note**: This uses custom processing (NeuroKit2 doesn't have built-in BP analysis).

---

## Troubleshooting

### Common Issues

#### 1. "No channels found matching pattern"

**Cause**: Channel names in ACQ file don't match expected patterns

**Solution**:
```bash
# Check available channels
python -c "
import sys
sys.path.insert(0, 'src')
from data_io.data_loader import load_acq_file
from pathlib import Path

acq, df, sr = load_acq_file(Path('your_file.acq'))
print(df.columns.tolist())
"
```

Update channel patterns in `scripts/process_signals.py` if needed.

---

#### 2. "AttributeError: 'NoneType' object has no attribute 'savefig'"

**Cause**: NeuroKit2 plotting function returned None

**Status**: ✅ Fixed in current version (error handling added)

**Fallback**: Processing continues, CSV is saved, plot is skipped with warning

---

#### 3. Out of Memory

**Cause**: Large files with many channels

**Solutions**:
- Process files one at a time (not `--all`)
- Increase system RAM
- Process specific channels only (modify source)
- Use `--no-save` to skip plot generation

---

#### 4. Slow Processing

**Expected**: 30 minutes for 2-hour recording is normal

**Optimization Tips**:
- Use SSD storage for faster I/O
- Disable plot generation (`--no-save`)
- Process in parallel (manual scripting required)

---

#### 5. Missing R-peaks or SCR Peaks

**Cause**: Signal quality issues or algorithm sensitivity

**Solutions**:
- Check signal quality in quality_check.py first
- Review raw vs. cleaned signal in plots
- Consider adjusting algorithm parameters (requires code modification)
- Check electrode placement in original recording

---

## Advanced Usage

### Custom Channel Selection

Modify `scripts/process_signals.py` to process specific channels:

```python
# Edit line ~63-68
channel_patterns = {
    'ecg': 'ECG',           # Process ECG only
    # 'eda': 'EDA',         # Comment out to skip
    # 'rsp': 'RSP',         # Comment out to skip
    # 'bp': 'Blood Pressure'  # Comment out to skip
}
```

---

### Process Specific Time Windows

Combine with time windowing for phase-specific analysis:

```python
from src.data_io.data_loader import load_and_prepare_session
from src.processing.neurokit_signals import process_ecg_signal

# Load with windows
biodata, pid, visit = load_and_prepare_session(acq_file)

# Get specific window (e.g., Speech Period)
speech_window = [w for w in biodata.Window_List if w.name == "Speech"][0]

# Extract ECG data for that window
ecg_data = biodata.Data[0]  # Assuming ECG is first channel
ecg_windowed = ecg_data.data[speech_window.start_index:speech_window.end_index]

# Process windowed data
# (requires creating new DataObject with windowed data)
```

---

### Integration with Statistical Analysis

**Export to R**:

```r
# Load processed ECG data
library(data.table)
ecg <- fread("processed/ECG2108000293_processed.csv")

# Extract R-peaks
rpeaks <- ecg[ECG_R_Peaks == 1, .(Time, ECG_Rate)]

# Compute HRV
rr_intervals <- diff(rpeaks$Time) * 1000  # Convert to ms
hrv_sdnn <- sd(rr_intervals)
hrv_rmssd <- sqrt(mean(diff(rr_intervals)^2))
```

**Load in Python/Pandas**:

```python
import pandas as pd
import numpy as np

# Load processed data
ecg = pd.read_csv("processed/ECG2108000293_processed.csv")

# Extract R-peaks
rpeaks = ecg[ecg['ECG_R_Peaks'] == 1]['Time'].values

# Compute HRV
rr_intervals = np.diff(rpeaks) * 1000  # ms
hrv_sdnn = np.std(rr_intervals)
hrv_rmssd = np.sqrt(np.mean(np.diff(rr_intervals)**2))
```

---

### Parallel Batch Processing

For large datasets, process multiple files in parallel:

```bash
#!/bin/bash
# parallel_process.sh

# Find all ACQ files
find "Participant Data" -name "*.acq" > file_list.txt

# Process in parallel (4 at a time)
cat file_list.txt | xargs -P 4 -I {} \
    python scripts/process_signals.py {} -o ./processed
```

**Warning**: Monitor memory usage with parallel processing.

---

## Best Practices

### 1. Quality Check First

Always run quality assessment before signal processing:

```bash
# Step 1: Quality check
python scripts/quality_check.py "Participant Data" -o ./quality

# Step 2: Review quality reports
python scripts/analyze_quality.py ./quality

# Step 3: Only process good quality data
python scripts/process_signals.py --all --data-dir "Participant Data"
```

---

### 2. Organize Output by Study Phase

```bash
# Create organized output structure
mkdir -p processed/{TSST,PDST}/{baseline,speech,recovery}

# Process TSST baseline periods only
# (requires custom scripting)
```

---

### 3. Document Processing Parameters

Keep a processing log:

```bash
# Save processing metadata
echo "Processed $(date)" >> processed/processing_log.txt
echo "NeuroKit2 version: $(pip show neurokit2 | grep Version)" >> processed/processing_log.txt
```

---

### 4. Backup Raw Data

Always keep original ACQ files:

```bash
# Create backup before processing
cp -r "Participant Data" "Participant Data_BACKUP"
```

---

## API Reference

### Main Functions

Located in `src/processing/neurokit_signals.py`:

#### `process_ecg_signal(data_object, method='neurokit', output_dir=None, save_artifacts=False)`

Process ECG signal and extract cardiac features.

**Parameters**:
- `data_object`: DataObject containing ECG data
- `method`: Algorithm ('neurokit', 'pantompkins1985', 'hamilton2002', etc.)
- `output_dir`: Directory to save outputs
- `save_artifacts`: Whether to save CSV and plots

**Returns**: `(signals_df, info_dict)`

---

#### `process_eda_signal(data_object, method='neurokit', output_dir=None, save_artifacts=False)`

Process EDA signal and detect skin conductance responses.

**Parameters**: Same as ECG
**Returns**: `(signals_df, info_dict)`

---

#### `process_rsp_signal(data_object, method='khodadad2018', output_dir=None, save_artifacts=False)`

Process respiratory signal and extract breathing features.

**Parameters**: Same as ECG
**Returns**: `(signals_df, info_dict)`

---

#### `process_bloodpressure_signal(data_object, output_dir=None, save_artifacts=False)`

Process blood pressure signal with filtering and statistics.

**Parameters**:
- `data_object`: DataObject containing BP data
- `output_dir`: Directory to save outputs
- `save_artifacts`: Whether to save CSV and plots

**Returns**: `(signals_df, info_dict)`

---

#### `process_biodata_channels(biodata, channel_patterns, output_dir=None, save_artifacts=False)`

Process multiple channels in a BioData object.

**Parameters**:
- `biodata`: BioData object with all channels
- `channel_patterns`: Dict mapping signal type to channel name pattern
- `output_dir`: Output directory
- `save_artifacts`: Whether to save outputs

**Returns**: Dict mapping channel names to (signals, info) tuples

---

## Additional Resources

### Documentation
- [NeuroKit2 Documentation](https://neuropsychology.github.io/NeuroKit/)
- [MOXIE Study Protocol](../docs/protocol.md) *(if available)*
- [BIOPAC AcqKnowledge Manual](https://www.biopac.com/knowledge-base/)

### Publications
- Makowski et al. (2021). NeuroKit2: A Python toolbox for neurophysiological signal processing. *Behavior Research Methods*

### Support
- GitHub Issues: For bug reports
- Research Team: For study-specific questions

---

## Version History

### v0.2.0 (Current)
- ✅ Complete ECG processing with wave delineation
- ✅ EDA processing with tonic/phasic decomposition
- ✅ Dual RSP channel processing
- ✅ Blood pressure filtering and analysis
- ✅ Batch processing support
- ✅ Error handling for edge cases

### Planned (v0.3.0)
- HRV time/frequency domain analysis
- EMG signal processing
- Cross-signal coherence analysis
- Real-time processing capabilities

---

## License

Research use only - See main README for details.

## Citation

If you use this pipeline in publications, please cite:

```
[Your citation format here]
```

And acknowledge NeuroKit2:

```
Makowski, D., Pham, T., Lau, Z. J., Brammer, J. C., Lesspinasse, F.,
Pham, H., Schölzel, C., & S H Chen, A. (2021).
NeuroKit2: A Python toolbox for neurophysiological signal processing.
Behavior Research Methods, 53(4), 1689-1696.
```

---

**Last Updated**: October 31, 2025
**Maintainer**: MOXIE Research Team
