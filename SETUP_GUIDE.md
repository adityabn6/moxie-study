# MOXIE Analysis - Setup Guide

## Quick Setup

### 1. Prerequisites

Ensure you have Python 3.8 or higher installed:

```bash
python --version
```

### 2. Install Dependencies

From the `moxie_analysis` directory:

```bash
# Option 1: Install in virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Option 2: Install globally
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
python -c "import bioread, neurokit2, bokeh; print('All packages installed!')"
```

### 4. Prepare Your Data

Organize your ACQ files in this structure:

```
Participant_Data/
├── Participant_001/
│   ├── TSST Visit/
│   │   └── Acqknowledge/
│   │       └── your_file.acq
│   └── PDST Visit/
│       └── Acqknowledge/
│           └── your_file.acq
```

### 5. Run Quality Check

```bash
cd scripts
python quality_check.py /path/to/Participant_Data -o ../output
```

### 6. View Results

Open the HTML files in the `output` directory with your web browser:

```
output/
├── Participant_001/
│   ├── TSST/
│   │   ├── ECG2108000293.html  ← Open in browser
│   │   ├── EDA2107000289.html
│   │   └── quality_report.json
```

## Troubleshooting

### Issue: "No module named 'bioread'"

**Solution:** Activate your virtual environment first:
```bash
source venv/bin/activate  # Or venv\Scripts\activate on Windows
```

### Issue: "No ACQ files found"

**Solution:** Check your directory structure:
```bash
cd /path/to/Participant_Data
ls -R  # Should show participant directories with Visit folders
```

### Issue: "Channel not found"

**Solution:** Not all participants have all channels. Check which channels are available:
```bash
python quality_check.py /path/to/data -o output -v
```

The `-v` flag will show all available channels for each file.

### Issue: Plots are empty or not loading

**Solution:**
1. Check that the output HTML file was created
2. Open in a modern browser (Chrome, Firefox, Safari)
3. Check browser console for JavaScript errors (F12)

## Next Steps

1. **Customize channels**: Edit `src/core/config.py` → `DEFAULT_CHANNELS`
2. **Adjust quality thresholds**: Edit `src/core/config.py` → `QUALITY_CHECK_PARAMS`
3. **Add signal processing**: Extend `src/processing/` modules
4. **Batch processing**: Use `scripts/process_all.py` for large datasets

## Getting Help

- Check the main README.md for detailed documentation
- Look at `scripts/example_usage.py` for code examples
- Review the source code - it's well-commented!

## Common Workflows

### Process a single participant

```bash
python quality_check.py /path/to/Participant_Data/Participant_001 -o output
```

### Process with verbose output

```bash
python quality_check.py /path/to/Participant_Data -o output -v
```

### Custom output location

```bash
python quality_check.py /path/to/Participant_Data -o /custom/path/results
```

## Development Mode

If you want to modify the code:

```bash
# Install in editable mode
pip install -e .

# Make changes to src/ files
# They'll be immediately available without reinstalling
```

Enjoy analyzing your MOXIE data!
