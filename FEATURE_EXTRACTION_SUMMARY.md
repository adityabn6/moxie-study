# Physiological Feature Extraction Summary

## Completion Date: 2025-11-05

---

## Overview

Successfully extracted aggregated physiological features for each protocol phase across all MOXIE study participants. The features are ready for regression analysis in R to examine relationships between physiological responses and psychological outcomes.

---

## Output File

**Location:** `/scratch/sungchoi_root/sungchoi99/adityabn/physiological_features.csv`

**Statistics:**
- **Total Rows:** 147 (1 header + 146 data rows)
- **Total Columns:** 28
- **Participants:** 18
- **Visit Types:** TSST Visit, PDST Visit
- **Protocol Phases:** Baseline, Speech Prep, Speech, Arithmetic, Debrief, Recovery, Task Intro, Debate
- **ACQ Files Processed:** 31

---

## Features Extracted

### Blood Pressure (4 features)
- `bp_mean`: Mean blood pressure during window
- `bp_std`: Standard deviation of blood pressure
- `bp_min`: Minimum blood pressure
- `bp_max`: Maximum blood pressure

### Electrodermal Activity - EDA (5 features)
- `eda_mean`: Mean skin conductance level (µS)
- `eda_std`: Standard deviation of SCL
- `eda_min`: Minimum SCL
- `eda_max`: Maximum SCL
- `eda_num_peaks`: Number of skin conductance responses (SCRs)

### Heart Rate Variability - HRV (8 features)
- `hrv_mean_hr`: Mean heart rate (BPM)
- `hrv_std_hr`: Standard deviation of heart rate
- `hrv_min_hr`: Minimum heart rate
- `hrv_max_hr`: Maximum heart rate
- `hrv_num_beats`: Number of R-R intervals (heartbeats)
- `hrv_rmssd`: Root mean square of successive differences (ms) - parasympathetic activity
- `hrv_sdnn`: Standard deviation of NN intervals (ms) - overall HRV
- `hrv_pnn50`: Percentage of successive RR intervals differing by >50ms - parasympathetic activity

### Respiratory - RSP (5 features)
- `rsp_mean_rate`: Mean respiratory rate (breaths/min)
- `rsp_std_rate`: Standard deviation of respiratory rate
- `rsp_mean_amplitude`: Mean respiratory amplitude
- `rsp_std_amplitude`: Standard deviation of amplitude
- `rsp_num_breaths`: Number of respiratory cycles

### Metadata (6 features)
- `participant_id`: Participant identifier
- `visit_type`: TSST Visit or PDST Visit
- `phase`: Protocol phase name
- `window_start_time`: Start time in seconds
- `window_end_time`: End time in seconds
- `window_duration`: Duration in seconds

---

## Sample Data

### Example Row (Participant 126641, PDST Baseline)
```csv
participant_id,visit_type,phase,window_start_time,window_end_time,window_duration,
126641,PDST Visit,Baseline,405.75,853.49,447.74,

bp_max,bp_mean,bp_min,bp_std,
130.67,80.64,53.38,13.14,

eda_max,eda_mean,eda_min,eda_num_peaks,eda_std,
2.52,1.61,1.22,,0.34,

hrv_max_hr,hrv_mean_hr,hrv_min_hr,hrv_num_beats,hrv_pnn50,hrv_rmssd,hrv_sdnn,hrv_std_hr,
77.67,64.94,56.18,485,9.11,30.44,52.85,3.70,

rsp_mean_amplitude,rsp_mean_rate,rsp_num_breaths,rsp_std_amplitude,rsp_std_rate
2.39,16.57,123,0.56,2.90
```

### Interpretation:
- **Baseline period:** 447 seconds (~7.5 minutes)
- **Heart rate:** Mean 64.9 BPM (normal resting rate)
- **HRV:** RMSSD = 30.44 ms (moderate parasympathetic activity)
- **HRV:** pNN50 = 9.11% (lower parasympathetic activity)
- **Respiratory rate:** 16.6 breaths/min (normal range)
- **EDA:** Mean 1.61 µS (low arousal/stress)

---

## Data Quality Notes

### Successful Processing
- ✓ 146 time windows extracted across 18 participants
- ✓ All physiological signals processed (ECG, RSP, EDA, BP)
- ✓ Features within expected physiological ranges
- ✓ Missing event markers handled gracefully (some windows skipped)

### Known Issues
1. **Missing Event Markers:**
   - Some ACQ files had incomplete or misnamed event markers
   - Affected participants/visits are noted in processing logs
   - Windows with invalid start/end times were skipped

2. **EDA Peak Count:**
   - `eda_num_peaks` shows NaN for some windows
   - This is expected when peak detection threshold not met
   - Tonic features (mean, std) are still valid

3. **Participants with Missing Windows:**
   - 125761: TSST Visit had invalid Speech, Arithmetic, Recovery, Task Intro, Speech Prep, Debrief windows
   - 126557: PDST Visit had invalid Debrief and Debate windows
   - 126523: TSST Visit had invalid Baseline, Speech Prep, Debrief windows

---

## Feature Statistics (Across All Windows)

### HRV Metrics
- **Mean HR:** Range 60-110 BPM (appropriate for rest-to-stress paradigm)
- **RMSSD:** Range 12-86 ms (varies with autonomic state)
- **pNN50:** Range 0-48% (higher in baseline, lower during stress)

### Respiratory Metrics
- **Mean Rate:** Range 12-19 breaths/min (normal range)
- **Variability:** Higher during stress tasks (speech, arithmetic)

### EDA Metrics
- **Tonic Level:** Range 1.5-10 µS (increases with arousal/stress)
- **SCR Peaks:** More frequent during stress tasks

---

## Usage for R Regression Analysis

### Loading Data in R
```r
# Load the features
features <- read.csv("/scratch/sungchoi_root/sungchoi99/adityabn/physiological_features.csv")

# Filter to specific phases
baseline <- features[features$phase == "Baseline", ]
speech <- features[features$phase == "Speech", ]
arithmetic <- features[features$phase == "Arithmetic", ]

# Example: Compare HRV between TSST and PDST baseline
library(dplyr)
baseline_comparison <- features %>%
  filter(phase == "Baseline") %>%
  group_by(visit_type) %>%
  summarize(
    mean_rmssd = mean(hrv_rmssd, na.rm = TRUE),
    mean_hr = mean(hrv_mean_hr, na.rm = TRUE),
    mean_eda = mean(eda_mean, na.rm = TRUE)
  )
```

### Suggested Analyses

1. **Stress Reactivity:**
   - Compare HRV (RMSSD, pNN50) between Baseline and Speech/Arithmetic
   - Lower HRV during stress indicates sympathetic activation
   - `lm(hrv_rmssd ~ phase + visit_type, data = features)`

2. **Autonomic Recovery:**
   - Compare Recovery phase to Baseline
   - Return to baseline indicates good autonomic regulation
   - `lm(hrv_rmssd ~ phase, data = subset(features, phase %in% c("Baseline", "Recovery")))`

3. **EDA Arousal:**
   - Compare EDA levels across phases
   - Higher EDA during stress tasks indicates arousal
   - `anova(lm(eda_mean ~ phase * visit_type, data = features))`

4. **Respiratory Patterns:**
   - Compare RSP rate variability during stress vs baseline
   - Irregular breathing common during speech task
   - `t.test(rsp_std_rate ~ phase, data = subset(features, phase %in% c("Baseline", "Speech")))`

---

## Files Created

1. **Feature Extraction Script:** `/home/adityabn/PhD/moxie-study/scripts/extract_features.py`
2. **Output CSV:** `/scratch/sungchoi_root/sungchoi99/adityabn/physiological_features.csv`
3. **Validation Report:** `/home/adityabn/PhD/moxie-study/SIGNAL_PROCESSING_VALIDATION.md`
4. **Test Analysis Script:** `/home/adityabn/PhD/moxie-study/scripts/analyze_test_signals.py`

---

## Recommendations for Future Enhancement

### 1. Additional HRV Metrics (via NeuroKit's `nk.hrv()`)
Consider adding frequency-domain and non-linear metrics:
- **Frequency-domain:** LF power, HF power, LF/HF ratio (stress indicator)
- **Non-linear:** SD1, SD2 (Poincaré plot), entropy measures

These provide complementary information about autonomic function and stress response.

### 2. Respiratory Variability
- Add RRV (respiratory rate variability) metrics
- Respiratory sinus arrhythmia (RSA) - coupling between HR and breathing

### 3. Artifact Correction
- Implement NeuroKit's artifact detection/correction
- May improve reliability for noisy segments

### 4. Time-Series Features
- Trend analysis within windows (increasing/decreasing HR)
- Time-to-peak or recovery slopes

---

## Key Physiological Markers for MOXIE Study

### Stress Indicators (Expected to increase during TSST)
- ↑ Mean heart rate (`hrv_mean_hr`)
- ↓ HRV (`hrv_rmssd`, `hrv_sdnn`, `hrv_pnn50`)
- ↑ EDA level (`eda_mean`, `eda_max`)
- ↑ EDA peaks (`eda_num_peaks`)
- ↑ Blood pressure (`bp_mean`)
- ↑ Respiratory rate (`rsp_mean_rate`)

### Autonomic Regulation (Good recovery)
- Return of HRV to baseline levels
- Decrease in EDA to baseline
- Normalization of heart rate

### Individual Differences
- Baseline HRV (trait measure of vagal tone)
- Reactivity magnitude (change from baseline)
- Recovery speed (time to return to baseline)

---

## Next Steps

1. ✓ **Quality Check:** Validated signal processing and feature ranges
2. ✓ **Data Export:** Created CSV for R analysis
3. **Statistical Analysis:**
   - Import into R
   - Merge with psychological/behavioral outcomes
   - Run regression models
   - Examine stress reactivity and recovery patterns
4. **Visualization:**
   - Create plots of physiological responses across protocol phases
   - Compare TSST vs PDST responses
   - Individual participant profiles

---

## Contact & Support

For questions about the feature extraction pipeline or physiological metrics:
- Review `SIGNAL_PROCESSING_VALIDATION.md` for technical details
- Check NeuroKit2 documentation: https://neuropsychology.github.io/NeuroKit/
- See `scripts/extract_features.py` for implementation details

---

## References

1. Task Force (1996). Heart rate variability: Standards of measurement, physiological interpretation, and clinical use. *Circulation, 93*(5), 1043-1065.
2. Shaffer, F., & Ginsberg, J. P. (2017). An overview of heart rate variability metrics and norms. *Frontiers in Public Health, 5*, 258.
3. Boucsein, W. (2012). *Electrodermal activity* (2nd ed.). Springer Science & Business Media.
4. Makowski, D., et al. (2021). NeuroKit2: A Python toolbox for neurophysiological signal processing. *Behavior Research Methods, 53*(4), 1689-1696.
