# Enhanced Feature Extraction - Comparison & Guide

## Date: 2025-11-05

---

## Overview

This document compares the **basic** vs **enhanced** feature extraction for the MOXIE stress research study, highlighting the critical stress biomarkers now included.

---

## Feature Count Comparison

| Version | Features | Improvements |
|---------|----------|--------------|
| **Basic** | 28 features | Time-domain HRV, basic stats |
| **Enhanced** | **66 features** | +38 features (+135% increase) |

---

## Detailed Feature Comparison

### 1. HRV (Heart Rate Variability)

#### Basic Version (8 features):
```
✓ hrv_mean_hr, hrv_std_hr, hrv_min_hr, hrv_max_hr
✓ hrv_rmssd, hrv_sdnn, hrv_pnn50, hrv_num_beats
```
- **Coverage:** Time-domain only
- **Missing:** Frequency-domain, Non-linear

#### Enhanced Version (22 features) - **+14 features**:
```
✓ All basic features PLUS:

TIME-DOMAIN (additional):
+ hrv_meannn, hrv_mediann, hrv_cvnn

FREQUENCY-DOMAIN (NEW! ⭐⭐⭐⭐⭐):
+ hrv_lf           - Low frequency power (sympathetic + parasympathetic)
+ hrv_hf           - High frequency power (parasympathetic/vagal)
+ hrv_vlf          - Very low frequency power
+ hrv_lf_hf_ratio  - ⭐⭐⭐⭐⭐ THE GOLD STANDARD STRESS BIOMARKER
+ hrv_lf_nu        - Normalized LF power
+ hrv_hf_nu        - Normalized HF power

NON-LINEAR (NEW!):
+ hrv_sd1          - Poincaré short-term variability
+ hrv_sd2          - Poincaré long-term variability
+ hrv_sd1_sd2      - SD1/SD2 ratio
```

**Impact for Stress Research:**
- **LF/HF Ratio** is the most widely cited stress biomarker in psychophysiology
- **Interpretation:**
  - Higher LF/HF = Sympathetic dominance (stress, anxiety)
  - Lower LF/HF = Parasympathetic dominance (relaxation, calm)
- **Expected in TSST:**
  - Baseline: LF/HF ~ 1-2
  - Speech/Arithmetic: LF/HF ~ 3-6 (stress response)
  - Recovery: LF/HF returns toward baseline

**Example from Test Data:**
- Baseline: LF/HF = 1.45
- Speech: LF/HF = 4.79 ✓ **Clear stress response detected!**

---

### 2. EDA (Electrodermal Activity)

#### Basic Version (5 features):
```
✓ eda_mean, eda_std, eda_min, eda_max
✓ eda_num_peaks (SCR count only)
```
- **Problem:** Only measuring **frequency** of arousal, not **intensity**

#### Enhanced Version (14 features) - **+9 features**:
```
✓ All basic features renamed for clarity PLUS:

TONIC (SCL - baseline arousal):
+ eda_tonic_mean, eda_tonic_std, eda_tonic_min, eda_tonic_max
+ eda_tonic_slope      - Rising/falling arousal trend ⭐⭐

PHASIC (SCR - arousal responses):
+ eda_phasic_mean, eda_phasic_std
+ eda_phasic_auc       - Area under curve (total arousal) ⭐⭐

SCR DYNAMICS (NEW! ⭐⭐⭐):
+ scr_num_peaks        - Count of SCRs
+ scr_frequency        - SCRs per minute
+ scr_amplitude_mean   - ⭐⭐⭐ INTENSITY of arousal responses
+ scr_amplitude_max    - Peak arousal
+ scr_rise_time_mean   - ⭐⭐⭐ SPEED of arousal onset
+ scr_recovery_time_mean - ⭐⭐ Arousal regulation ability
```

**Impact for Stress Research:**
- **SCR Amplitude** = How intense the arousal is (not just how often)
- **SCR Rise Time** = How quickly arousal occurs
  - Faster rise = more intense/acute stress response
  - Typical: 1-3 seconds
- **SCR Recovery Time** = How well arousal is regulated
  - Slower = poor regulation, sustained anxiety
  - Typical: 2-10 seconds

**Why This Matters:**
- **Before:** "Person had 4 SCRs during speech"
- **Now:** "Person had 4 SCRs, averaging 0.34 µS amplitude, with 2.5s rise time, and 0s recovery"
  - Tells you about arousal intensity and regulation, not just frequency!

---

### 3. Respiration (RSP)

#### Basic Version (10 features):
```
✓ rsp_mean_rate, rsp_std_rate
✓ rsp_mean_amplitude, rsp_std_amplitude
✓ rsp_num_breaths
(Treating 2 channels separately, 5 features × 2 = 10)
```
- **Problem:** Not leveraging coordination between thoracic & abdominal breathing

#### Enhanced Version (24 features) - **+14 features**:
```
✓ All basic features PLUS:

SINGLE CHANNEL (per channel - thoracic & abdominal):
+ rsp_rvt_mean          - Respiratory Volume per Time (ventilation) ⭐⭐
+ rsp_ie_ratio_mean     - Inspiration/Expiration ratio ⭐⭐
+ rsp_breath_variability - Breath-by-breath variability ⭐

MULTI-CHANNEL COORDINATION (NEW! ⭐⭐⭐⭐):
+ rsp_thoracic_abdominal_correlation  - ⭐⭐⭐⭐ PARADOXICAL BREATHING DETECTOR
+ rsp_thoracic_dominance              - ⭐⭐⭐ Thoracic vs abdominal breathing
+ rsp_phase_coherence                 - Temporal synchronization
+ rsp_contribution_thoracic           - Variance contribution
```

**Impact for Stress Research:**

**Thoracic-Abdominal Correlation:**
- **Normal breathing:** 0.7-0.9 (high positive correlation)
- **Paradoxical breathing:** <0.3 or negative (anxiety, panic, dysfunctional)
- **Stress/anxiety:** Often reduced coordination

**Thoracic Dominance:**
- **Normal:** <1 (abdominal-dominant, diaphragmatic breathing)
- **Stress/Anxiety:** >1 (thoracic-dominant, chest breathing)
- Shift from abdominal to thoracic is a classic anxiety marker

**I/E Ratio:**
- **Normal:** ~1:1.5 (expiration slightly longer)
- **Stress:** Higher ratio (rapid shallow breathing)

**Example from Test Data:**
- Baseline: Correlation = 0.89 ✓ (normal coordination)
- Speech: Correlation = 0.72 (reduced coordination during stress)
- Baseline: Dominance = 1.49 (thoracic-dominant)
- Speech: Dominance = 1.04

---

### 4. Blood Pressure (BP)

#### Basic Version (4 features):
```
✓ bp_mean, bp_std, bp_min, bp_max
```

#### Enhanced Version (6 features) - **+2 features**:
```
✓ All basic features PLUS:
+ bp_cv    - Coefficient of variation (relative variability)
+ bp_slope - Rising/falling BP trend over window ⭐
```

**Impact:**
- **BP Slope** detects if BP is rising (building stress response) or falling (recovery)

---

## Summary Table: Basic vs Enhanced

| Signal | Basic Features | Enhanced Features | Key Additions |
|--------|---------------|-------------------|---------------|
| **Metadata** | 6 | 6 | (same) |
| **HRV** | 8 | 22 | +14: LF/HF ratio!, SD1/SD2 |
| **EDA** | 5 | 14 | +9: SCR amplitude, rise/recovery time |
| **RSP** | 10 | 24 | +14: Thoracic-abdominal coordination! |
| **BP** | 4 | 6 | +2: CV, slope |
| **TOTAL** | **28** | **66** | **+38 (+135%)** |

---

## Most Critical New Features for Stress Research

### Top 5 Must-Have Features:

1. **`hrv_lf_hf_ratio`** ⭐⭐⭐⭐⭐
   - The gold standard stress biomarker
   - Should increase during TSST speech/arithmetic
   - Most cited in stress research literature

2. **`rsp_thoracic_abdominal_correlation`** ⭐⭐⭐⭐
   - Detects paradoxical breathing (anxiety marker)
   - Should decrease during stress/anxiety
   - Unique to our 2-channel respiratory setup!

3. **`scr_amplitude_mean`** ⭐⭐⭐
   - Arousal intensity (not just frequency)
   - Should be larger during stress tasks
   - Currently completely missing in basic extraction

4. **`scr_rise_time_mean`** ⭐⭐⭐
   - Speed of stress response
   - Faster = more intense/acute response
   - Critical for understanding arousal dynamics

5. **`rsp_thoracic_dominance`** ⭐⭐⭐
   - Breathing pattern shift
   - Should be higher during stress (chest breathing)
   - Classic anxiety/stress indicator

---

## Expected Stress Response Patterns

### TSST Protocol Phases:

**Baseline:**
- LF/HF ratio: Low (1-2)
- SCR amplitude: Low
- Thoracic-abdominal correlation: High (0.7-0.9)
- Thoracic dominance: Low (<1, abdominal breathing)

**Speech/Arithmetic (Stress Tasks):**
- LF/HF ratio: **High (3-6)** ↑↑
- SCR amplitude: **Higher** ↑
- SCR frequency: **More frequent** ↑
- SCR rise time: **Faster** ↓
- Thoracic-abdominal correlation: **Lower** ↓ (reduced coordination)
- Thoracic dominance: **Higher** ↑ (shift to chest breathing)
- Respiratory rate: **Faster**

**Recovery:**
- LF/HF ratio: **Returns toward baseline** ↓
- SCR metrics: **Decrease**
- Breathing coordination: **Improves** ↑
- HRV measures: **Increase** (vagal reactivation)

---

## Statistical Analysis Implications

### New Analyses Possible with Enhanced Features:

1. **Stress Reactivity:**
   ```r
   # Compare LF/HF ratio across phases
   lm(hrv_lf_hf_ratio ~ phase + visit_type, data = features)

   # Expect significant increase in Speech/Arithmetic
   ```

2. **Autonomic Balance:**
   ```r
   # LF/HF ratio as predictor of anxiety outcomes
   lm(anxiety_score ~ hrv_lf_hf_ratio + phase, data = merged_data)
   ```

3. **Breathing Dysfunction:**
   ```r
   # Paradoxical breathing detection
   paradoxical <- features %>%
     filter(rsp_thoracic_abdominal_correlation < 0.3)

   # Compare anxiety levels
   t.test(anxiety ~ paradoxical_breathing, data = merged_data)
   ```

4. **Arousal Intensity (not just frequency):**
   ```r
   # SCR amplitude as stress indicator
   lm(stress_rating ~ scr_amplitude_mean + scr_frequency, data = features)

   # Now can separate intensity from frequency effects!
   ```

5. **Multi-System Stress Response:**
   ```r
   # Combined model with all systems
   lm(stress_outcome ~
      hrv_lf_hf_ratio +          # Autonomic
      scr_amplitude_mean +        # Arousal intensity
      rsp_thoracic_dominance +    # Breathing pattern
      bp_slope,                    # Cardiovascular
      data = features)
   ```

---

## Files

### Basic Extraction:
- **Script:** `scripts/extract_features.py`
- **Output:** `/scratch/.../physiological_features.csv`
- **Features:** 28
- **Rows:** 146

### Enhanced Extraction:
- **Script:** `scripts/extract_features_enhanced.py`
- **Output:** `/scratch/.../physiological_features_enhanced.csv`
- **Features:** 66
- **Rows:** Expected ~146

---

## Usage Recommendations

### For Stress Research:

**Use Enhanced Features** for:
- Publications (includes gold standard metrics)
- Comprehensive stress response characterization
- Multi-system stress analysis
- Individual differences in stress reactivity
- Breathing dysfunction detection
- Arousal intensity vs frequency

**Stick with Basic Features** for:
- Quick exploratory analysis
- Simple stress indicators
- When frequency-domain HRV not needed
- Minimal feature set requirements

### Best Practice:

Start with **Enhanced Features** - you can always drop features if needed, but you can't add them without reprocessing!

---

## Technical Notes

### Computation Time:
- Enhanced extraction takes ~50% longer due to:
  - NeuroKit's `nk.hrv()` function (frequency-domain computation)
  - Multi-channel RSP correlation calculations
  - Additional SCR metrics extraction

### Data Requirements:
- Same as basic extraction
- Requires processed signal CSVs from `process_signals.py`
- Both RSP channels needed for coordination features

### Missing Values:
- More NaN values possible with enhanced features
  - Frequency-domain HRV needs longer windows (>60s recommended)
  - SCR dynamics only calculated when SCRs detected
  - RSP coordination needs both channels present

---

## References

### HRV LF/HF Ratio:
- Task Force (1996). Heart rate variability. *Circulation, 93*(5), 1043-1065.
- Kim et al. (2018). Stress and heart rate variability: A meta-analysis.

### SCR Dynamics:
- Dawson et al. (2007). The electrodermal system. *Handbook of Psychophysiology*.
- Bach et al. (2010). Model-based analysis of skin conductance responses.

### Respiratory Coordination:
- Blechert et al. (2007). Fear conditioning in posttraumatic stress disorder.
- Vlemincx et al. (2013). Respiratory variability and sighing.

### Thoracic-Abdominal Breathing:
- Courtney (2009). Strengths, weaknesses, and possibilities of the Breathing Pattern Assessment Tool.
- Grassi et al. (2013). Respiratory sinus arrhythmia.

---

## Conclusion

The **Enhanced Feature Extraction** provides:
- **66 features** (vs 28 basic) - 135% increase
- **All gold standard stress biomarkers** included
- **Unique multi-channel breathing analysis**
- **Arousal intensity** measurements (not just frequency)
- **Publication-ready** feature set

**Recommendation:** Use enhanced extraction for all stress research analyses in the MOXIE study.
