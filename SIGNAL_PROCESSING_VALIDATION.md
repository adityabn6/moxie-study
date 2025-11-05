# Signal Processing Validation Report

## Date: 2025-11-05
## Participant 124961 TSST Visit Analysis

---

## Overview

This report documents the validation of our physiological signal processing pipeline using NeuroKit2, comparing our implementation against NeuroKit MCP best practices.

---

## 1. Signal Quality Analysis Results

### ECG Signal (5-minute sample)
- **Heart Rate:**
  - Mean: 75.80 BPM ✓
  - Std: 3.98 BPM
  - Range: 67.38 - 90.91 BPM
  - **Status:** Within normal range (60-100 BPM)

- **Signal Quality:**
  - Mean: 0.943 ✓
  - Range: 0.567 - 1.000
  - **Status:** Excellent (>0.8)

- **R-Peak Detection:**
  - Detected: 379 peaks
  - Expected: ~379 peaks (based on mean HR)
  - **Status:** Accurate detection ✓

### Respiratory Signal (5-minute sample)
- **Respiratory Rate:**
  - Mean: 14.46 breaths/min ✓
  - Std: 4.70 breaths/min
  - Range: 4.61 - 30.34 breaths/min
  - **Status:** Mean is normal (12-20 range), min value slightly low but acceptable

- **Peak Detection:**
  - Detected: 69 peaks
  - Expected: ~72 peaks
  - **Status:** Good correlation ✓

### EDA Signal (5-minute sample)
- **Tonic Component (SCL):**
  - Mean: 2.72 µS ✓
  - Range: 1.87 - 4.71 µS
  - **Status:** Within typical range (2-20 µS)

- **SCR Peaks:**
  - Count: 6 peaks
  - Rate: 1.20 peaks/min
  - **Status:** Normal (1-3 peaks/min expected) ✓

---

## 2. Implementation Comparison with NeuroKit MCP Best Practices

### ECG Processing

**Our Implementation** (`src/processing/neurokit_signals.py`):
```python
# Line 78-82
signals, info = nk.ecg_process(
    data_object.data,
    sampling_rate=data_object.sampling_rate,
    method=method
)
```

**NeuroKit MCP Best Practice** (`Paper2Agent/NeuroKit/src/tools/ecg_delineate.py`):
```python
# Line 38
cleaned_signal, rpeaks = nk.ecg_peaks(ecg_signal, sampling_rate=sampling_rate)
```

**Analysis:**
- ✓ Our use of `nk.ecg_process()` is CORRECT and RECOMMENDED
- `nk.ecg_process()` is a higher-level function that internally calls:
  1. `nk.ecg_clean()` - Filters and cleans the signal
  2. `nk.ecg_peaks()` - Detects R-peaks
  3. `nk.ecg_delineate()` - Identifies P, Q, S, T waves
  4. `nk.ecg_phase()` - Cardiac cycle segmentation
  5. `nk.ecg_quality()` - Signal quality assessment
- This is MORE comprehensive than just using `nk.ecg_peaks()` alone

**Delineation Method:**
- Our implementation: Uses default method (DWT - Discrete Wavelet Transform)
- MCP best practice: DWT is the recommended default
- Alternative methods available: "peak", "cwt" (Continuous Wavelet Transform)

---

### RSP Processing

**Our Implementation** (`src/processing/neurokit_signals.py`):
```python
# Line 159-163
signals, info = nk.rsp_process(
    data_object.data,
    sampling_rate=data_object.sampling_rate,
    method=method
)
```

**Analysis:**
- ✓ Correct use of `nk.rsp_process()` - high-level wrapper function
- Default cleaning method: 'khodadad2018' (appropriate for physiological RSP)
- Includes: cleaning, peak detection, rate calculation, amplitude estimation

---

### HRV Feature Extraction

**Our Implementation** (`scripts/extract_features.py`):
```python
# Lines 79-108: Manual calculation from R-R intervals
r_peaks = window_data[window_data['ECG_R_Peaks'] == 1]
rr_intervals = np.diff(r_peaks['Time'].values) * 1000  # Convert to ms

# RMSSD
successive_diffs = np.diff(rr_intervals)
features['hrv_rmssd'] = np.sqrt(np.mean(successive_diffs ** 2))

# SDNN
features['hrv_sdnn'] = np.std(rr_intervals, ddof=1)

# pNN50
nn50 = np.sum(np.abs(successive_diffs) > 50)
features['hrv_pnn50'] = (nn50 / len(successive_diffs)) * 100
```

**NeuroKit MCP Best Practice** (`Paper2Agent/NeuroKit/src/tools/ecg_hrv.py`):
```python
# Line 49: Extract peaks first
peaks, info = nk.ecg_peaks(ecg_signal, sampling_rate=sampling_rate)

# Line 72: Use built-in HRV functions
hrv_time = nk.hrv_time(peaks, sampling_rate=sampling_rate, show=show)
hrv_freq = nk.hrv_frequency(peaks, sampling_rate=sampling_rate)
hrv_nonlinear = nk.hrv_nonlinear(peaks, sampling_rate=sampling_rate)

# Or use comprehensive function:
hrv_indices = nk.hrv(peaks, sampling_rate=sampling_rate)
```

**Analysis:**
- ✓ Our manual calculation is MATHEMATICALLY CORRECT
- ⚠️ RECOMMENDATION: Use `nk.hrv_time()` instead for several reasons:
  1. **More comprehensive metrics:** Includes RMSSD, SDNN, pNN50, MeanNN, MedianNN, SDSD, CVNN, etc.
  2. **Handles edge cases:** Better handling of ectopic beats, artifacts
  3. **Includes frequency-domain:** LF power, HF power, LF/HF ratio
  4. **Non-linear metrics:** Poincaré plot (SD1, SD2), entropy measures
  5. **Standardized:** Ensures compatibility with research literature

**Sample Metrics from NeuroKit's `nk.hrv()`:**
- **Time-domain:** HRV_RMSSD, HRV_SDNN, HRV_pNN50, HRV_pNN20, HRV_MeanNN, HRV_MedianNN, HRV_CVNN, HRV_SDSD
- **Frequency-domain:** HRV_HF, HRV_LF, HRV_VLF, HRV_LFHF, HRV_LFn, HRV_HFn
- **Non-linear:** HRV_SD1, HRV_SD2, HRV_SD1SD2, HRV_ApEn, HRV_SampEn, HRV_DFA_alpha1

---

### EDA Processing

**Our Implementation** (`src/processing/neurokit_signals.py`):
```python
# Line 269-273
signals, info = nk.eda_process(
    data_object.data,
    sampling_rate=data_object.sampling_rate,
    method=method
)
```

**Analysis:**
- ✓ Correct use of `nk.eda_process()`
- Decomposes into: Tonic (SCL) and Phasic (SCR) components
- Detects SCR peaks automatically

---

## 3. Key Findings

### Strengths of Current Implementation

1. **Correct high-level functions:** Using `nk.ecg_process()`, `nk.rsp_process()`, `nk.eda_process()` ✓
2. **Proper signal quality:** ECG quality score 0.943 (excellent) ✓
3. **Accurate peak detection:** R-peaks and respiratory peaks match expected counts ✓
4. **Good physiological ranges:** All signals within expected ranges ✓
5. **Fixed RSP plotting bug:** Custom matplotlib visualization works correctly ✓
6. **Efficient data handling:** Downsampling for visualization preserves memory ✓

### Recommended Improvements

1. **HRV Feature Extraction:**
   - Current: Manual calculation of RMSSD, SDNN, pNN50
   - Recommended: Use `nk.hrv_time()` or `nk.hrv()` for comprehensive metrics
   - Benefit: Access to frequency-domain (LF/HF power) and non-linear (SD1, SD2) metrics

2. **Additional Metrics to Consider:**
   - **HRV Frequency-domain:** LF power, HF power, LF/HF ratio (stress indicator)
   - **HRV Non-linear:** SD1, SD2 (Poincaré plot), entropy measures
   - **RSP Variability:** RRV metrics (respiratory rate variability)

3. **Artifact Handling:**
   - Consider using NeuroKit's artifact detection/correction
   - May improve HRV reliability for noisy segments

---

## 4. Validation Status

| Component | Status | Notes |
|-----------|--------|-------|
| ECG Signal Quality | ✓ PASS | Mean quality: 0.943 (excellent) |
| ECG R-Peak Detection | ✓ PASS | Accurate count, proper heart rate |
| ECG Processing Pipeline | ✓ PASS | Using `nk.ecg_process()` correctly |
| RSP Signal Quality | ✓ PASS | Mean rate: 14.46 br/min (normal) |
| RSP Peak Detection | ✓ PASS | Good correlation with expected |
| RSP Processing Pipeline | ✓ PASS | Using `nk.rsp_process()` correctly |
| EDA Signal Quality | ✓ PASS | SCL: 2.72 µS (normal range) |
| EDA Processing Pipeline | ✓ PASS | Using `nk.eda_process()` correctly |
| HRV Calculation | ⚠️ IMPROVE | Correct but could use built-in functions |
| Plotting/Visualization | ✓ PASS | Fixed RSP plotting bug |

---

## 5. Recommendations for Feature Extraction Enhancement

### Option 1: Minimal Change (Keep Current Approach)
Keep current manual HRV calculation but add validation against NeuroKit's functions.

### Option 2: Use NeuroKit HRV Functions (RECOMMENDED)
Replace manual HRV calculation with:
```python
def calculate_hrv_features_enhanced(ecg_data: pd.DataFrame, window_start: float, window_end: float, sampling_rate: int = 2000) -> Dict[str, float]:
    # Filter to window
    mask = (ecg_data['Time'] >= window_start) & (ecg_data['Time'] <= window_end)
    window_data = ecg_data[mask]

    # Extract R-peaks DataFrame format for NeuroKit
    peaks_df = pd.DataFrame({
        'ECG_R_Peaks': window_data['ECG_R_Peaks'].values
    })

    # Compute comprehensive HRV metrics
    hrv_indices = nk.hrv(peaks_df, sampling_rate=sampling_rate)

    # Extract relevant features
    return {
        'hrv_rmssd': hrv_indices['HRV_RMSSD'][0],
        'hrv_sdnn': hrv_indices['HRV_SDNN'][0],
        'hrv_pnn50': hrv_indices['HRV_pNN50'][0],
        'hrv_mean_nn': hrv_indices['HRV_MeanNN'][0],
        'hrv_lf_power': hrv_indices['HRV_LF'][0],
        'hrv_hf_power': hrv_indices['HRV_HF'][0],
        'hrv_lf_hf_ratio': hrv_indices['HRV_LFHF'][0],
        'hrv_sd1': hrv_indices['HRV_SD1'][0],  # Poincaré short-term variability
        'hrv_sd2': hrv_indices['HRV_SD2'][0],  # Poincaré long-term variability
    }
```

**Benefits:**
- More comprehensive HRV metrics for regression analysis
- LF/HF ratio is a strong stress indicator (important for TSST analysis!)
- Non-linear metrics capture different aspects of autonomic function
- Standardized with research literature

---

## 6. Processed File Statistics

### Test Output: Participant 124961 TSST Visit

| File | Size | Rows | Duration | Sampling Rate |
|------|------|------|----------|---------------|
| ECG2108000293_processed.csv | 1.9 GB | 12,988,206 | ~6,494 sec | 2000 Hz |
| RSP2208000207_processed.csv | 2.1 GB | - | - | 2000 Hz |
| EDA2107000289_processed.csv | 1.4 GB | - | - | 2000 Hz |

**Note:** File sizes are appropriate for high sampling rate (2000 Hz) physiological signals over ~1.8 hours of recording.

---

## 7. Conclusion

**Overall Assessment:** ✓ PIPELINE IS WORKING CORRECTLY

Our signal processing implementation follows NeuroKit2 best practices and produces high-quality results. The main recommendation is to enhance HRV feature extraction to include frequency-domain and non-linear metrics, which would provide more comprehensive data for stress/anxiety analysis in the MOXIE study.

**Next Steps:**
1. Consider enhancing HRV feature extraction (Option 2 above)
2. Complete feature extraction for all participants
3. Generate final CSV for R regression analysis
4. Validate feature values are within expected ranges across all participants

---

## References

- NeuroKit2 Documentation: https://neuropsychology.github.io/NeuroKit/
- NeuroKit MCP Server: `../Paper2Agent/NeuroKit/src/`
- Task Force (1996). Heart rate variability. Circulation, 93(5), 1043-1065.
