# MOXIE Analysis - Quick Reference Card

## Complete Workflow

### 1️⃣ Initial Setup (One Time)

```bash
cd moxie_analysis
pip install -r requirements.txt
```

### 2️⃣ Process Signals (NeuroKit2)

```bash
# Process a single ACQ file
python scripts/process_signals.py "Participant Data/ID/Visit/Acqknowledge/file.acq" -o ./processed

# Process all ACQ files
python scripts/process_signals.py --all --data-dir "Participant Data" -o ./processed
```

**Outputs:**
- ECG: R-peaks, heart rate, P/Q/S/T waves
- EDA: SCR peaks, tonic/phasic decomposition
- RSP: Breathing rate, respiratory cycles
- Blood Pressure: Cleaned signal, statistics

### 3️⃣ Quality Assessment

```bash
# Process all new/changed files (incremental mode)
python scripts/quality_check.py "/path/to/Participant Data" -o ./output

# First run processes everything
# Subsequent runs only process new participants!
```

### 4️⃣ Analyze Quality

```bash
# Generate text report
python scripts/analyze_quality.py ./output

# Generate visualizations
python scripts/visualize_quality.py ./output

# Export CSV for statistical analysis
python scripts/analyze_quality.py ./output --export-csv
```

### 5️⃣ Review Results

**Check these files:**
- `processed/{channel}_processed.csv` - Processed signals with features
- `processed/{channel}_plot.png` - Signal visualizations
- `output/quality_analysis_report.txt` - Detailed findings
- `output/visualizations/*.png` - Quality charts
- `output/{participant}/{visit}/*.html` - Interactive plots

---

## Common Commands

### Signal Processing

```bash
# Single file (basic)
python scripts/process_signals.py "file.acq" -o ./output

# Single file (verbose)
python scripts/process_signals.py "file.acq" -o ./output -v

# All files in directory
python scripts/process_signals.py --all --data-dir "Participant Data"

# Don't save artifacts (CSV only, no plots)
python scripts/process_signals.py "file.acq" -o ./output --no-save
```

### Quality Assessment

```bash
# Normal (skip already processed)
python scripts/quality_check.py "/path/to/data" -o ./output

# Force reprocess everything
python scripts/quality_check.py "/path/to/data" -o ./output --force

# Reprocess one participant
python scripts/quality_check.py "/path/to/data" -o ./output --clear-participant 124961

# Verbose output
python scripts/quality_check.py "/path/to/data" -o ./output -v
```

### Analysis

```bash
# Quick summary
python scripts/analyze_quality.py ./output

# Detailed console output
python scripts/analyze_quality.py ./output --detailed

# Export CSVs
python scripts/analyze_quality.py ./output --export-csv

# Generate visualizations (PNG)
python scripts/visualize_quality.py ./output

# Generate visualizations (PDF)
python scripts/visualize_quality.py ./output --format pdf
```

---

## Key Files

### Input
- `Participant_Data/{ID}/{TSST|PDST Visit}/Acqknowledge/*.acq`

### Output
- `output/.processing_log.json` - Processing history (DO NOT DELETE)
- `output/{ID}/{TSST|PDST}/*.html` - Interactive visualizations
- `output/{ID}/{TSST|PDST}/quality_report.json` - Quality metrics
- `output/quality_analysis_report.txt` - Study-wide analysis
- `output/visualizations/*.png` - Quality charts
- `output/quality_*.csv` - Exportable data (if --export-csv used)

---

## Quality Interpretation

### Overall Ratings
- **Excellent** (<10% flagged) ✓ - Ready for analysis
- **Good** (10-25%) ✓ - Minor issues, acceptable
- **Fair** (25-50%) ⚠️ - Review carefully
- **Poor** (>50%) ❌ - Consider exclusion

### What to Check

**If a PARTICIPANT has issues:**
- Review their HTML plots
- Check recording notes
- Verify sensor placement
- Consider re-recording

**If a CHANNEL has issues:**
- Review sensor placement protocol
- Check equipment calibration
- Verify ACQ settings
- Check for systematic patterns

**If TSST vs PDST differ:**
- Different experimenters?
- Different equipment?
- Protocol drift over time?

---

## Typical Weekly Workflow

### Monday: Data Collection
```bash
# Add new participants to Participant_Data/
```

### Tuesday: Signal Processing
```bash
cd moxie_analysis
source venv/bin/activate

# Process physiological signals
python scripts/process_signals.py --all --data-dir "Participant Data" -o ./processed
```
✓ Extracts ECG, EDA, RSP, Blood Pressure features

### Wednesday: Quality Assessment
```bash
# Quality check on raw signals
python scripts/quality_check.py "/path/to/Participant Data" -o ./output
```
✓ Only new participants are processed!

### Thursday: Quality Review
```bash
python scripts/analyze_quality.py ./output --export-csv
python scripts/visualize_quality.py ./output
```

Review:
- Text report for flagged issues
- Visualizations for patterns
- Individual HTML plots for detailed inspection

### Friday: Follow-up
- Address any quality concerns
- Update protocols if needed
- Document decisions
- Re-record if necessary
- Export processed features for statistical analysis

---

## Troubleshooting

### "No ACQ files found"
✓ Check directory structure matches expected format
✓ Verify path is correct

### "All files already processed"
✓ This is normal! Add new participants to process them
✓ Use `--force` to reprocess everything

### "matplotlib not installed"
✓ `pip install matplotlib seaborn`

### Processing is slow
✓ Normal! Large ACQ files take time
✓ Script processes incrementally, so it's fast next time

### Want to reprocess specific participant
```bash
python scripts/quality_check.py "/path/to/data" -o ./output --clear-participant 124961
python scripts/quality_check.py "/path/to/data" -o ./output
```

---

## Tips

💡 **Run analysis after every data collection session** - Catch issues early

💡 **Keep the `.processing_log.json`** - It remembers what's been processed

💡 **Review visualizations regularly** - Patterns are easier to spot visually

💡 **Export CSVs for presentations** - Easy to use in R, Excel, etc.

💡 **Check Blood Pressure carefully** - Intermittent measurements often flagged

💡 **Document all quality decisions** - For reproducibility

---

## Help & Documentation

- `README.md` - Complete overview
- `SIGNAL_PROCESSING_GUIDE.md` - Signal processing documentation
- `INCREMENTAL_PROCESSING.md` - Incremental processing details
- `QUALITY_ANALYSIS_GUIDE.md` - Comprehensive analysis guide
- `SETUP_GUIDE.md` - Installation instructions
- `ARCHITECTURE.md` - Technical details

---

## Quick Diagnostics

**Check processing status:**
```bash
cat output/.processing_log.json | grep "success" | wc -l
```

**List processed participants:**
```bash
ls -1 output/
```

**Count quality reports:**
```bash
find output -name "quality_report.json" | wc -l
```

**Check for errors in log:**
```bash
cat output/.processing_log.json | grep '"success": false'
```

---

## Summary

**Start to finish for new data:**
```bash
# 1. Process signals (extract features)
python scripts/process_signals.py --all --data-dir "Participant Data" -o ./processed

# 2. Quality check (assess data quality)
python scripts/quality_check.py "/path/to/data" -o ./output

# 3. Analyze quality
python scripts/analyze_quality.py ./output --export-csv
python scripts/visualize_quality.py ./output

# 4. Review
cat output/quality_analysis_report.txt
open output/visualizations/
ls processed/*.csv  # Your processed signal features
```

**That's it!** 🎉
