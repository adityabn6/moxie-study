# Quality Analysis Guide

After running the quality check script, you can analyze the results to identify patterns, problems, and potential issues with experimental protocols.

## Overview

The MOXIE analysis package includes two complementary analysis scripts:

1. **`analyze_quality.py`** - Text-based analysis with detailed reports
2. **`visualize_quality.py`** - Visual analysis with charts and graphs

Both scripts parse the `.processing_log.json` file created by `quality_check.py`.

## Quick Start

### 1. Run Quality Check (if not already done)

```bash
python scripts/quality_check.py "/path/to/Participant Data" -o ./output
```

### 2. Generate Analysis Report

```bash
python scripts/analyze_quality.py ./output
```

### 3. Generate Visualizations

```bash
# Install visualization libraries first (if needed)
pip install matplotlib seaborn

# Generate plots
python scripts/visualize_quality.py ./output
```

## Detailed Usage

### Text Analysis (`analyze_quality.py`)

**Basic usage:**
```bash
python scripts/analyze_quality.py ./output
```

**Export detailed CSV files:**
```bash
python scripts/analyze_quality.py ./output --export-csv
```

This creates:
- `quality_by_participant.csv` - Per-participant quality summary
- `quality_by_channel.csv` - Per-channel quality summary
- `quality_by_visit_type.csv` - TSST vs PDST comparison
- `quality_detailed.csv` - All quality data in tabular format

**Show detailed console output:**
```bash
python scripts/analyze_quality.py ./output --detailed
```

### Visual Analysis (`visualize_quality.py`)

**Generate PNG visualizations (default):**
```bash
python scripts/visualize_quality.py ./output
```

**Generate PDF or SVG:**
```bash
python scripts/visualize_quality.py ./output --format pdf
python scripts/visualize_quality.py ./output --format svg
```

**Generated visualizations:**
- `quality_distribution.png` - Overall quality ratings
- `participant_overview.png` - Quality by participant
- `participant_heatmap.png` - Heatmap of all channels x participants
- `channel_comparison.png` - SNR and amplitude by channel
- `visit_comparison.png` - TSST vs PDST quality comparison
- `snr_vs_amplitude.png` - Scatter plot showing SNR vs amplitude relationship

All visualizations are saved to `output/visualizations/`

## What the Analysis Reveals

### 1. Participant-Level Issues

**Indicators:**
- High average flagged percentage (>25%)
- Consistently poor quality across multiple channels
- Poor quality in both TSST and PDST visits

**Possible causes:**
- Sensor placement issues
- Participant movement during recording
- Skin conductivity issues (for EDA)
- Incorrect equipment setup

**Recommendations:**
- Review sensor placement protocol for that participant
- Check recording notes for environmental factors
- Consider participant-specific factors (anxiety, medication, etc.)
- May need to exclude participant if quality is consistently poor

### 2. Channel-Level Issues

**Indicators:**
- High flagged percentage across multiple participants
- Consistent poor quality ratings
- High standard deviation (inconsistent quality)

**Possible causes:**
- Systematic sensor placement problem
- Equipment calibration issues
- Incompatible measurement settings
- Environmental interference

**Recommendations:**
- Review sensor placement protocol document
- Check equipment calibration
- Verify measurement parameters in ACQ settings
- Consider environmental factors (electrical interference, temperature)

### 3. Visit Type Differences

**Indicators:**
- Significant quality differences between TSST and PDST
- One visit type consistently worse than the other

**Possible causes:**
- Different experimental conditions
- Different experimenters
- Different equipment or setup
- Protocol drift over time

**Recommendations:**
- Review protocol differences between visits
- Check if different experimenters handled different visits
- Verify equipment consistency across visits
- Review temporal sequence (were later participants different?)

## Example Analysis Workflow

### Scenario: New Data Collection Completed

1. **Run quality check:**
   ```bash
   python scripts/quality_check.py "/path/to/data" -o ./output
   ```

2. **Generate analysis:**
   ```bash
   python scripts/analyze_quality.py ./output --export-csv
   python scripts/visualize_quality.py ./output
   ```

3. **Review text report:**
   - Open `output/quality_analysis_report.txt`
   - Look for flagged participants and channels
   - Read recommendations section

4. **Review visualizations:**
   - Open `output/visualizations/`
   - Check participant heatmap for patterns
   - Review channel comparison for systematic issues
   - Compare TSST vs PDST quality

5. **Investigate issues:**
   - If specific participants are flagged:
     * Review their HTML visualizations in detail
     * Check recording notes for environmental factors
     * Consider re-recording if possible

   - If specific channels are flagged:
     * Review sensor placement protocol
     * Check equipment calibration logs
     * Verify with experienced experimenters

6. **Document findings:**
   - Note any systematic issues in study documentation
   - Update protocols if needed
   - Flag participants for exclusion if necessary

### Example: Investigating Channel Issues

If `Blood Pressure - NIBP100E` shows high flagged percentage:

```bash
# Run detailed analysis
python scripts/analyze_quality.py ./output --detailed

# Check CSV for specific details
# Open: output/quality_by_channel.csv
```

**What to look for:**
- Is the issue consistent across all participants?
- Is it worse in TSST vs PDST?
- What's the SNR vs amplitude contribution?

**Interpretation:**
- High SNR flagging → Signal noise/interference issues
- High amplitude flagging → Sensor disconnection or very low signal
- Consistent across participants → Systematic protocol/equipment issue
- Variable across participants → Participant-specific factors

## Understanding Quality Metrics

### Overall Quality Ratings

- **Excellent** (<10% flagged): High quality, ready for analysis
- **Good** (10-25% flagged): Acceptable quality with minor issues
- **Fair** (25-50% flagged): Significant quality concerns, review carefully
- **Poor** (>50% flagged): Major quality issues, consider exclusion

### SNR (Signal-to-Noise Ratio)

- **What it measures:** Signal clarity and interference levels
- **Low SNR indicates:** Electrical noise, movement artifacts, equipment issues
- **Typical values:** Excellent channels show <5% flagged

### Amplitude

- **What it measures:** Signal strength and sensor connection
- **Low amplitude indicates:** Loose sensors, disconnection, very weak signal
- **Typical values:** Well-connected sensors show <2% flagged

## Common Patterns and Solutions

### Pattern 1: One Participant, Multiple Channels Poor

**Likely cause:** Participant-specific issue
**Check:** Movement, sweating, anxiety, clothing interference
**Solution:** Review that session's notes, consider re-recording

### Pattern 2: One Channel, Multiple Participants Poor

**Likely cause:** Systematic equipment or protocol issue
**Check:** Sensor type, placement protocol, calibration
**Solution:** Review/update protocol, check equipment

### Pattern 3: Blood Pressure Always Flagged

**Expected:** Blood pressure is intermittent (not continuous)
**Action:** This is normal; focus on other continuous signals
**Note:** SNR flagging expected between measurements

### Pattern 4: Custom/DA100C Always Poor

**Check:** Is this channel actually in use?
**Action:** Verify sensor configuration in ACQ settings
**Note:** May be recording noise if not properly configured

### Pattern 5: TSST Worse Than PDST (or vice versa)

**Check:** Different experimenters? Different equipment?
**Action:** Review protocols, ensure consistency
**Note:** Some difference is normal due to task differences

## Troubleshooting

### "Processing log not found"
**Solution:** Run `quality_check.py` first to create the log

### "No data found in processing log"
**Solution:** Check that quality_check.py completed successfully

### "matplotlib/seaborn not installed"
**Solution:** `pip install matplotlib seaborn`

### Visualizations are too small/crowded
**Solution:** Open the image file and zoom in, or regenerate as PDF/SVG for vector graphics

### Want to analyze specific participants only
**Solution:** Use pandas to filter the CSV files generated with `--export-csv`

## Advanced Analysis

### Using the CSV Files

```python
import pandas as pd

# Load detailed data
df = pd.read_csv('output/quality_detailed.csv')

# Filter specific participant
participant_data = df[df['participant_id'] == '124961']

# Calculate custom metrics
df['combined_flagged'] = (df['snr_flagged_pct'] + df['amp_flagged_pct']) / 2

# Group by custom criteria
channel_by_visit = df.groupby(['channel', 'visit_type'])['combined_flagged'].mean()
```

### Longitudinal Analysis

If you have multiple data collection waves:

```bash
# Wave 1
python scripts/quality_check.py "/data/wave1" -o ./output_wave1
python scripts/analyze_quality.py ./output_wave1 --export-csv

# Wave 2
python scripts/quality_check.py "/data/wave2" -o ./output_wave2
python scripts/analyze_quality.py ./output_wave2 --export-csv

# Compare CSV files to track quality trends over time
```

## Integration with Statistical Analysis

Export CSV files for use in R, SPSS, or other statistical packages:

```bash
python scripts/analyze_quality.py ./output --export-csv
```

Then in R:
```r
library(tidyverse)

# Load quality data
quality <- read_csv("output/quality_detailed.csv")

# Statistical tests
t.test(snr_flagged_pct ~ visit_type, data = quality)

# Visualize
ggplot(quality, aes(x = channel, y = snr_flagged_pct, fill = visit_type)) +
  geom_boxplot() +
  theme_minimal()
```

## Best Practices

1. **Run analysis after each data collection session** - Catch issues early
2. **Review visualizations regularly** - Patterns are easier to spot visually
3. **Keep historical reports** - Track quality trends over time
4. **Document decisions** - Note why participants/channels were excluded
5. **Update protocols** - Use findings to improve data collection
6. **Share with team** - Use visualizations in team meetings

## Questions to Ask

When reviewing the analysis:

- [ ] Are there any participants with >25% flagged data?
- [ ] Are there consistent issues with specific channels?
- [ ] Is quality improving or degrading over time?
- [ ] Are there differences between experimenters?
- [ ] Are there differences between visit types?
- [ ] Do equipment changes correlate with quality changes?
- [ ] Are there seasonal or temporal patterns?

## Getting Help

- Check the generated text report for automated recommendations
- Review the main README.md for general troubleshooting
- Consult with experienced team members about unusual patterns
- Document all quality decisions for reproducibility

## Summary Commands

```bash
# Complete analysis workflow
python scripts/quality_check.py "/path/to/data" -o ./output
python scripts/analyze_quality.py ./output --export-csv
python scripts/visualize_quality.py ./output

# Quick check on existing results
python scripts/analyze_quality.py ./output

# Regenerate visualizations only
python scripts/visualize_quality.py ./output --format pdf
```
