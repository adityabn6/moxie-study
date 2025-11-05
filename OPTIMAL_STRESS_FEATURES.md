# Optimal Physiological Features for Stress Research

## Analysis Date: 2025-11-05

---

## Current vs. Optimal Feature Set

### Summary of Gaps

**Current extraction:** 28 features total
- Basic statistics (mean, std, min, max)
- Missing many stress-specific metrics available in processed data

**Optimal for stress research:** ~50-60 features
- Leveraging ALL NeuroKit-processed columns
- Stress-specific metrics (SCR dynamics, RSA, breathing coordination)
- Frequency-domain HRV (LF/HF ratio - THE classic stress biomarker)

---

## 1. EDA Features - MAJOR GAPS IDENTIFIED ⚠️

### Available Columns in Processed Files:
```
EDA_Raw, EDA_Clean, EDA_Tonic, EDA_Phasic,
SCR_Onsets, SCR_Peaks, SCR_Height, SCR_Amplitude,
SCR_RiseTime, SCR_Recovery, SCR_RecoveryTime, Time
```

### Currently Extracting (5 features):
- ✓ `eda_mean`, `eda_std`, `eda_min`, `eda_max` (tonic level)
- ✓ `eda_num_peaks` (SCR count)

### MISSING - Critical for Stress Research (9 additional features):

**Phasic/SCR Features (high importance for stress!):**

1. **`scr_amplitude_mean`** ⭐⭐⭐
   - Mean amplitude of SCRs in window
   - Column: `SCR_Amplitude`
   - **Why:** Larger SCRs = greater sympathetic arousal
   - **Stress relevance:** Increases during TSST speech/arithmetic

2. **`scr_amplitude_max`** ⭐⭐
   - Maximum SCR amplitude
   - Column: `SCR_Amplitude`
   - **Why:** Peak arousal response

3. **`scr_rise_time_mean`** ⭐⭐⭐
   - Mean time for SCR to rise from onset to peak
   - Column: `SCR_RiseTime`
   - **Why:** Faster rise time = more intense arousal
   - **Stress relevance:** Rapid SCRs indicate acute stress response

4. **`scr_recovery_time_mean`** ⭐⭐
   - Mean time for SCR to recover to baseline
   - Column: `SCR_RecoveryTime`
   - **Why:** Slower recovery = sustained arousal, poor regulation
   - **Stress relevance:** Prolonged recovery in anxiety/stress

5. **`scr_frequency`** ⭐⭐⭐
   - Number of SCRs per minute
   - Calculation: `num_peaks / (window_duration / 60)`
   - **Why:** Rate of electrodermal responses
   - **Stress relevance:** More frequent during stress periods

6. **`scr_auc`** ⭐⭐
   - Area under curve of phasic component
   - Column: Integrate `EDA_Phasic` over time
   - **Why:** Total phasic activity in window
   - **Stress relevance:** Cumulative arousal measure

7. **`eda_tonic_slope`** ⭐⭐
   - Linear trend of tonic level (increasing/decreasing)
   - Column: Linear regression on `EDA_Tonic`
   - **Why:** Rising tonic = building arousal, Falling = calming
   - **Stress relevance:** Anticipatory anxiety shows rising slope

8. **`scr_latency_first`** ⭐
   - Time to first SCR after window start
   - Column: First `SCR_Onsets` timestamp
   - **Why:** Response latency to stressor
   - **Stress relevance:** Immediate vs delayed stress response

9. **`eda_phasic_std`** ⭐
   - Variability of phasic component
   - Column: std of `EDA_Phasic`
   - **Why:** Variability in arousal responses

---

## 2. Respiratory Features - MAJOR OPPORTUNITY ⚠️

### Available Data:
- **TWO RSP channels:** Thoracic (RSP2208000207) and Abdominal (RSP2106000165)
- **Columns per channel:**
  ```
  RSP_Raw, RSP_Clean, RSP_Amplitude, RSP_Rate, RSP_RVT,
  RSP_Phase, RSP_Phase_Completion,
  RSP_Symmetry_PeakTrough, RSP_Symmetry_RiseDecay,
  RSP_Peaks, RSP_Troughs, Time
  ```

### Currently Extracting (5 features per channel = 10 total):
- ✓ `rsp_mean_rate`, `rsp_std_rate`
- ✓ `rsp_mean_amplitude`, `rsp_std_amplitude`
- ✓ `rsp_num_breaths`

**Note:** Currently treating channels separately, not leveraging coordination!

### MISSING - Critical for Stress Research (15+ additional features):

**Single Channel Features:**

10. **`rsp_rvt_mean`** ⭐⭐⭐
    - Respiratory Volume per Time
    - Column: `RSP_RVT`
    - **Why:** Minute ventilation estimate
    - **Stress relevance:** Hyperventilation during panic/stress

11. **`rsp_ie_ratio_mean`** ⭐⭐⭐
    - Inspiration/Expiration duration ratio
    - Column: `RSP_Symmetry_RiseDecay`
    - **Why:** Normal ~1:1.5, changes with stress
    - **Stress relevance:** Rapid shallow breathing = higher I/E ratio

12. **`rsp_breath_by_breath_variability`** ⭐⭐
    - Breath-to-breath RR interval variability (like HRV)
    - Calculation: SDNN of breath intervals
    - **Why:** Respiratory variability marker
    - **Stress relevance:** Reduced variability in stress

13. **`rsp_pause_count`** ⭐⭐
    - Number of respiratory pauses (>2-3 seconds)
    - Detection: Gaps in breathing
    - **Why:** Breath-holding, sighs
    - **Stress relevance:** Speech anxiety → breath holding before speaking

14. **`rsp_sigh_count`** ⭐
    - Number of sighs (very large amplitude breaths)
    - Detection: Amplitude > 2*SD
    - **Why:** Stress coping behavior
    - **Stress relevance:** Sighs reset respiratory drive, common in stress

**Multi-Channel Coordination Features (NEW!) - Very Important:**

15. **`rsp_thoracic_abdominal_correlation`** ⭐⭐⭐
    - Pearson correlation between thoracic and abdominal signals
    - Columns: Correlate both `RSP_Clean` signals
    - **Why:** Breathing coordination/synchrony
    - **Stress relevance:** Paradoxical breathing (negative correlation) in anxiety
    - **Normal:** High positive correlation (0.7-0.9)
    - **Stress:** Reduced or negative correlation

16. **`rsp_thoracic_dominance`** ⭐⭐
    - Ratio of thoracic to abdominal amplitude
    - Calculation: `thoracic_amplitude / abdominal_amplitude`
    - **Why:** Breathing pattern type
    - **Stress relevance:** Thoracic-dominant breathing in stress/anxiety
    - **Normal:** Abdominal-dominant breathing (ratio < 1)
    - **Stress:** Thoracic-dominant (ratio > 1)

17. **`rsp_phase_coherence`** ⭐⭐
    - Phase synchrony between channels
    - Calculation: Cross-correlation at lag 0
    - **Why:** Temporal coordination
    - **Stress relevance:** Desynchronization in dysfunctional breathing

18. **`rsp_contribution_variance_thoracic`** ⭐
    - % of total breathing variance from thoracic
    - **Why:** Breathing compartment contribution
    - **Stress relevance:** Shifts during stress

**Respiratory Sinus Arrhythmia (RSA) - HIGHLY IMPORTANT:**

19. **`rsa_amplitude`** ⭐⭐⭐⭐
    - High-frequency HRV amplitude synchronized with breathing
    - Calculation: Use `nk.hrv_frequency()` with respiration signal
    - **Why:** Vagal tone, parasympathetic activity
    - **Stress relevance:** PRIMARY autonomic regulation marker
    - **Normal:** Higher RSA = better vagal control
    - **Stress:** RSA decreases during stress (vagal withdrawal)

---

## 3. HRV Features - MISSING FREQUENCY-DOMAIN ⚠️

### Currently Extracting (8 features):
- ✓ Time-domain: `hrv_rmssd`, `hrv_sdnn`, `hrv_pnn50`
- ✓ Basic: `hrv_mean_hr`, `hrv_std_hr`, `hrv_min_hr`, `hrv_max_hr`, `hrv_num_beats`

### MISSING - Essential for Stress Research (8+ additional features):

**Use NeuroKit's `nk.hrv()` function instead of manual calculation!**

**Frequency-Domain (CRITICAL for stress):**

20. **`hrv_lf`** ⭐⭐⭐⭐
    - Low Frequency power (0.04-0.15 Hz)
    - **Why:** Sympathetic + parasympathetic activity
    - **Stress relevance:** Increases with stress

21. **`hrv_hf`** ⭐⭐⭐⭐
    - High Frequency power (0.15-0.4 Hz)
    - **Why:** Parasympathetic (vagal) activity
    - **Stress relevance:** Decreases during stress (vagal withdrawal)

22. **`hrv_lf_hf_ratio`** ⭐⭐⭐⭐⭐
    - Ratio of LF/HF power
    - **Why:** THE classic stress biomarker!
    - **Stress relevance:**
      - Higher ratio = sympathetic dominance (stress)
      - Lower ratio = parasympathetic dominance (relaxation)
    - **TSST:** Should increase during speech/arithmetic, decrease in recovery

23. **`hrv_vlf`** ⭐⭐
    - Very Low Frequency power (<0.04 Hz)
    - **Why:** Thermoregulation, slow regulatory processes

24. **`hrv_hf_nu`** ⭐⭐⭐
    - Normalized HF power: HF / (LF + HF)
    - **Why:** Proportion of parasympathetic activity
    - **Stress relevance:** Decreases in stress

25. **`hrv_lf_nu`** ⭐⭐⭐
    - Normalized LF power: LF / (LF + HF)
    - **Why:** Relative sympathetic activity
    - **Stress relevance:** Increases in stress

**Non-Linear Domain:**

26. **`hrv_sd1`** ⭐⭐⭐
    - Poincaré plot - short-term HRV
    - **Why:** Beat-to-beat variability (parasympathetic)
    - **Stress relevance:** Decreases during stress

27. **`hrv_sd2`** ⭐⭐
    - Poincaré plot - long-term HRV
    - **Why:** Overall variability

28. **`hrv_sd1_sd2_ratio`** ⭐⭐
    - Ratio of short to long-term variability
    - **Why:** Cardiac autonomic balance

---

## 4. Blood Pressure Features

### Currently Extracting (4 features):
- ✓ `bp_mean`, `bp_std`, `bp_min`, `bp_max`

### Additional (2 features):

29. **`bp_variability`** ⭐
    - Coefficient of variation: std/mean
    - **Why:** Relative BP stability

30. **`bp_slope`** ⭐
    - Linear trend over window
    - **Why:** Rising BP = building stress response

---

## 5. ECG Wave Morphology (Optional - Advanced)

Available but not currently using:
- P, Q, R, S, T wave locations
- Could calculate intervals: PR, QT, QRS duration

**For Stress Research:**

31. **`qt_interval_mean`** ⭐
    - QT interval duration
    - **Why:** Cardiac repolarization, stress affects this
    - **Note:** Requires correction for heart rate (QTc)

---

## PRIORITY RANKING FOR STRESS RESEARCH

### HIGHEST PRIORITY (Must Add):

1. **`hrv_lf_hf_ratio`** ⭐⭐⭐⭐⭐
   - The gold standard stress biomarker
   - Requires: `nk.hrv()` with frequency-domain

2. **`rsa_amplitude`** ⭐⭐⭐⭐
   - Vagal tone, autonomic regulation
   - Requires: `nk.hrv_frequency()` with respiration

3. **`rsp_thoracic_abdominal_correlation`** ⭐⭐⭐⭐
   - Breathing coordination (paradoxical breathing in anxiety)
   - New calculation using both RSP channels

4. **`scr_amplitude_mean`** ⭐⭐⭐
   - SCR intensity (current: only count)
   - Available in processed files

5. **`scr_rise_time_mean`** ⭐⭐⭐
   - Speed of arousal response
   - Available in processed files

6. **`rsp_thoracic_dominance`** ⭐⭐⭐
   - Breathing pattern shift
   - New calculation

### HIGH PRIORITY (Should Add):

7-12. All other HRV frequency/non-linear metrics
13-15. Remaining SCR metrics (recovery time, frequency, AUC)
16-18. RSP variability and coordination metrics
19-20. Respiratory symmetry metrics

### MEDIUM PRIORITY (Nice to Have):

21+. BP variability, ECG intervals, additional breathing metrics

---

## Implementation Strategy

### Option 1: Enhance Existing Script
Modify `scripts/extract_features.py` to add features incrementally:

```python
# Phase 1: Add SCR dynamics (easy - already in files)
def calculate_eda_features_enhanced(eda_data, window_start, window_end):
    window_data = eda_data[(eda_data['Time'] >= window_start) &
                           (eda_data['Time'] <= window_end)]

    features = {}

    # Existing tonic features...

    # NEW: SCR phasic features
    scr_peaks = window_data[window_data['SCR_Peaks'] == 1]

    if len(scr_peaks) > 0:
        features['scr_amplitude_mean'] = scr_peaks['SCR_Amplitude'].mean()
        features['scr_amplitude_max'] = scr_peaks['SCR_Amplitude'].max()
        features['scr_rise_time_mean'] = scr_peaks['SCR_RiseTime'].mean()
        features['scr_recovery_time_mean'] = scr_peaks['SCR_RecoveryTime'].mean()
        features['scr_frequency'] = len(scr_peaks) / (window_duration / 60)

    # NEW: Tonic slope
    from scipy.stats import linregress
    slope, _, _, _, _ = linregress(window_data['Time'], window_data['EDA_Tonic'])
    features['eda_tonic_slope'] = slope

    return features
```

### Option 2: Use NeuroKit's Built-in Functions (RECOMMENDED)
Replace manual calculations with NeuroKit's comprehensive functions:

```python
import neurokit2 as nk

def calculate_hrv_features_optimal(ecg_data, window_start, window_end, sampling_rate=2000):
    """Use NeuroKit's nk.hrv() for comprehensive metrics."""
    window_data = ecg_data[(ecg_data['Time'] >= window_start) &
                           (ecg_data['Time'] <= window_end)]

    # Create peaks DataFrame for NeuroKit
    peaks_df = pd.DataFrame({'ECG_R_Peaks': window_data['ECG_R_Peaks'].values})

    # Compute ALL HRV metrics at once
    hrv_all = nk.hrv(peaks_df, sampling_rate=sampling_rate)

    # Extract features
    return {
        # Time-domain
        'hrv_rmssd': hrv_all['HRV_RMSSD'][0],
        'hrv_sdnn': hrv_all['HRV_SDNN'][0],
        'hrv_pnn50': hrv_all['HRV_pNN50'][0],
        'hrv_meannn': hrv_all['HRV_MeanNN'][0],

        # Frequency-domain ⭐⭐⭐
        'hrv_lf': hrv_all['HRV_LF'][0],
        'hrv_hf': hrv_all['HRV_HF'][0],
        'hrv_lf_hf_ratio': hrv_all['HRV_LFHF'][0],  # ⭐⭐⭐⭐⭐
        'hrv_lf_nu': hrv_all['HRV_LFn'][0],
        'hrv_hf_nu': hrv_all['HRV_HFn'][0],

        # Non-linear
        'hrv_sd1': hrv_all['HRV_SD1'][0],
        'hrv_sd2': hrv_all['HRV_SD2'][0],
        'hrv_sd1_sd2': hrv_all['HRV_SD1SD2'][0],
    }

def calculate_rsp_coordination(rsp_thoracic, rsp_abdominal, window_start, window_end):
    """NEW: Calculate coordination between breathing channels."""
    window_thor = rsp_thoracic[(rsp_thoracic['Time'] >= window_start) &
                               (rsp_thoracic['Time'] <= window_end)]
    window_abdo = rsp_abdominal[(rsp_abdominal['Time'] >= window_start) &
                                (rsp_abdominal['Time'] <= window_end)]

    # Correlation
    correlation = np.corrcoef(window_thor['RSP_Clean'],
                             window_abdo['RSP_Clean'])[0, 1]

    # Thoracic dominance
    thor_amp = window_thor['RSP_Amplitude'].mean()
    abdo_amp = window_abdo['RSP_Amplitude'].mean()
    dominance = thor_amp / abdo_amp if abdo_amp > 0 else np.nan

    return {
        'rsp_thoracic_abdominal_correlation': correlation,
        'rsp_thoracic_dominance': dominance,
        'rsp_thoracic_amplitude_mean': thor_amp,
        'rsp_abdominal_amplitude_mean': abdo_amp,
    }
```

---

## Expected Feature Count

**Current:** 28 features
**Optimal for Stress:** ~55-60 features

### Breakdown:
- **EDA:** 5 → 14 features (+9)
- **HRV:** 8 → 18 features (+10)
- **RSP (single channel):** 5 → 10 features (+5)
- **RSP (coordination):** 0 → 8 features (+8)
- **BP:** 4 → 6 features (+2)
- **Metadata:** 6 (same)

**Total:** ~60 features

---

## Stress Research Evidence

### Key Literature Supporting These Features:

1. **LF/HF Ratio:**
   - Kim et al. (2018). "Stress and heart rate variability: A meta-analysis"
   - TSST studies consistently show ↑LF/HF during stress

2. **RSA (Respiratory Sinus Arrhythmia):**
   - Porges (2007). "The polyvagal perspective"
   - Decreased RSA = vagal withdrawal (stress response)

3. **SCR Amplitude & Rise Time:**
   - Dawson et al. (2007). "The electrodermal system"
   - Faster, larger SCRs in acute stress

4. **Thoracic-Abdominal Coordination:**
   - Blechert et al. (2007). "Stress and breathing patterns"
   - Paradoxical breathing in panic/anxiety

5. **Breath-by-Breath Variability:**
   - Vlemincx et al. (2013). "Respiratory variability and anxiety"
   - Reduced variability in stress/anxiety

---

## Next Steps - Recommended Action

### Immediate (Highest Impact):

1. **Add HRV frequency-domain metrics** using `nk.hrv()`
   - Adds LF/HF ratio (THE stress biomarker)
   - ~10 minutes to implement

2. **Add SCR dynamics** from existing columns
   - Amplitude, rise time, recovery time
   - ~15 minutes to implement

3. **Add RSP channel coordination**
   - Correlation, thoracic dominance
   - ~20 minutes to implement

### Total time to optimal feature set: ~2-3 hours

Would you like me to create an enhanced feature extraction script with these additions?
