# Incremental Signal Processing Guide

Complete guide for using the incremental processing feature in signal processing to avoid reprocessing already-analyzed participants.

---

## Overview

The signal processing pipeline now supports **incremental processing**, which:
- ✅ Tracks which files have been successfully processed
- ✅ Automatically skips already-processed files on subsequent runs
- ✅ Detects file changes and reprocesses modified files
- ✅ Allows selective reprocessing of specific participants
- ✅ Maintains a processing log with metadata and statistics

This is especially useful when:
- Adding new participants to an ongoing study
- Reprocessing after parameter changes
- Recovering from processing errors

---

## Quick Start

### First Run - Process All Participants

```bash
python scripts/process_signals.py --all --data-dir "Participant Data" -o "processed_signals"
```

**What happens:**
1. Finds all ACQ files in "Participant Data"
2. Processes each file (ECG, EDA, RSP, Blood Pressure)
3. Saves processed CSV files to output directory
4. Creates `.signal_processing_log.json` tracking file
5. Marks each successfully processed file in the log

---

### Subsequent Runs - Only New Participants

```bash
# Same command - only processes NEW participants!
python scripts/process_signals.py --all --data-dir "Participant Data" -o "processed_signals"
```

**Output:**
```
Found 50 ACQ files
Skipping 45 already-processed files
Processing 5 new/changed files

[1/5]
Processing: TSST_Acqknowledge_NewParticipant_11_01_25.acq
...
```

**Result:** Only the 5 new participants are processed. The other 45 are skipped!

---

## Usage Examples

### 1. Normal Workflow (Incremental Processing)

```bash
# Week 1: Process initial 20 participants
python scripts/process_signals.py --all --data-dir "Participant Data"

# Week 2: Add 5 new participants, run same command
python scripts/process_signals.py --all --data-dir "Participant Data"
# → Only processes the 5 new ones!

# Week 3: Add 3 more participants
python scripts/process_signals.py --all --data-dir "Participant Data"
# → Only processes the 3 new ones!
```

---

### 2. Force Reprocess Everything

When you update processing parameters or fix a bug, reprocess all files:

```bash
python scripts/process_signals.py --all --data-dir "Participant Data" --force
```

This ignores the processing log and reprocesses every file.

---

### 3. Reprocess Specific Participant

If one participant's data was bad or you need to reprocess them:

```bash
# Clear their history
python scripts/process_signals.py --all --clear-participant 125761

# Then run normally (will only process this participant)
python scripts/process_signals.py --all --data-dir "Participant Data"
```

---

### 4. Clear All History

Start fresh (clears the log but doesn't delete processed files):

```bash
python scripts/process_signals.py --all --clear-all
```

Next run will process everything again.

---

## Processing Log

### Location

The processing log is saved as `.signal_processing_log.json`:

```
Participant Data/
├── .signal_processing_log.json  ← Tracking file (if no -o specified)
├── Participant_001/
│   └── TSST Visit/
│       └── Acqknowledge/
│           └── session.acq
...
```

Or if using `-o` option:

```
processed_signals/
├── .signal_processing_log.json  ← Tracking file (in output dir)
├── Participant_001/
│   └── TSST/
│       └── neurokit_processed/
...
```

---

### Log Structure

The log is a JSON file tracking each processed file:

```json
{
  "/path/to/file.acq": {
    "participant_id": "125761",
    "visit_type": "TSST Visit",
    "filename": "TSST_Acqknowledge_125761_09_23_25.acq",
    "processed_date": "2025-10-31T02:30:15.123456",
    "success": true,
    "file_hash": "a1b2c3d4e5f6...",
    "quality_summary": {
      "channels_processed": 5,
      "channel_names": [
        "ECG2108000293",
        "EDA2107000289",
        "RSP2106000165",
        "RSP2208000207",
        "Blood Pressure - NIBP100E"
      ]
    },
    "error_message": null
  }
}
```

**Fields:**
- `participant_id`: Participant identifier
- `visit_type`: TSST or PDST visit
- `filename`: ACQ filename
- `processed_date`: When processed (ISO format)
- `success`: True if successful, false if failed
- `file_hash`: MD5 hash to detect file changes
- `quality_summary`: Channels processed and names
- `error_message`: Error details if failed

---

## File Change Detection

The tracker computes an MD5 hash of each ACQ file. If the file changes:

```bash
# Original file processed
python scripts/process_signals.py --all

# File is modified (e.g., re-exported from AcqKnowledge)
# Next run automatically detects change
python scripts/process_signals.py --all
# → "File changed since last processing: session.acq"
# → File is reprocessed automatically
```

---

## Command Reference

### Main Commands

```bash
# Process all files (incremental)
python scripts/process_signals.py --all

# Process with specific data directory
python scripts/process_signals.py --all --data-dir "path/to/data"

# Save to specific output directory
python scripts/process_signals.py --all -o "output/dir"

# Verbose output (show details)
python scripts/process_signals.py --all -v
```

---

### Incremental Processing Options

```bash
# Force reprocess all files
python scripts/process_signals.py --all --force

# Clear specific participant
python scripts/process_signals.py --all --clear-participant 125761

# Clear all history
python scripts/process_signals.py --all --clear-all
```

---

### Single File Processing

Single files are NOT tracked (no incremental processing):

```bash
# Process one file (always processes, no tracking)
python scripts/process_signals.py "path/to/file.acq" -o "output"
```

---

## Processing Summary

After processing, you'll see a summary:

```
================================================================================
Batch Processing Complete
================================================================================
Total files: 5
  Successful: 5
  Failed: 0

Processing log saved to: Participant Data/.signal_processing_log.json

============================================================
Processing History Summary
============================================================
Total files processed: 45
  Successful: 44
  Failed: 1
Participants: 22
  IDs: 124874, 124883, 124940, ..., 127476
============================================================
```

---

## Best Practices

### 1. Don't Delete the Processing Log

The `.signal_processing_log.json` file is crucial for incremental processing:

```bash
# ❌ DON'T delete this file unless you want to reprocess everything
rm Participant\ Data/.signal_processing_log.json

# ✅ Use --clear-all instead
python scripts/process_signals.py --all --clear-all
```

---

### 2. Regular Processing Schedule

```bash
#!/bin/bash
# weekly_processing.sh

# Activate environment
source venv/bin/activate

# Process only new participants
python scripts/process_signals.py --all --data-dir "Participant Data" -o "processed"

# Check for errors
if [ $? -eq 0 ]; then
    echo "Processing complete!"
    # Optionally: commit processed files, run analysis, etc.
else
    echo "Processing failed - check logs"
fi
```

---

### 3. Version Control

Add to `.gitignore`:

```
# Processing logs (participant-specific, don't commit)
.signal_processing_log.json
**/neurokit_processed/
processed_signals/
```

---

### 4. Backup Before --force

Before reprocessing everything with `--force`:

```bash
# Backup processed files
cp -r processed_signals processed_signals_backup_$(date +%Y%m%d)

# Then force reprocess
python scripts/process_signals.py --all --force
```

---

## Troubleshooting

### "All files already processed!"

**This is normal!** It means you don't have any new participants.

**Solution:**
- Add new participants and run again
- Use `--force` to reprocess existing ones
- Use `--clear-participant ID` to reprocess specific participant

---

### File Not Being Reprocessed After Changes

**Cause:** File hash hasn't changed (file identical)

**Solution:**
- Verify file was actually modified
- Use `--clear-participant ID` to force reprocess
- Check processing log to see current hash

---

### Processing Log Shows Failed Files

View failed files in the log:

```bash
cat "Participant Data/.signal_processing_log.json" | grep '"success": false' -A 10
```

**Solution:**
- Review error messages in log
- Fix underlying issues
- Use `--clear-participant ID` to retry

---

### Want to Move Processing Log

The log location depends on output directory:

```bash
# Log in data directory
python scripts/process_signals.py --all
# → Creates: Participant Data/.signal_processing_log.json

# Log in output directory
python scripts/process_signals.py --all -o "processed"
# → Creates: processed/.signal_processing_log.json
```

---

## Integration with Quality Check

Both pipelines use the same tracking system:

```bash
# 1. Quality check (creates .processing_log.json)
python scripts/quality_check.py "Participant Data" -o quality_output

# 2. Signal processing (creates .signal_processing_log.json)
python scripts/process_signals.py --all -o signal_output
```

**Note:** They use separate log files, so you can:
- Run quality check on all participants
- Run signal processing only on good-quality participants
- They won't interfere with each other

---

## Advanced Usage

### Conditional Processing Based on Quality

```bash
# Get list of good-quality participants from quality log
cat quality_output/.processing_log.json | \
    grep '"success": true' | \
    grep -o '"participant_id": "[^"]*"' | \
    cut -d'"' -f4 > good_participants.txt

# Process only those participants
while read pid; do
    python scripts/process_signals.py --all --clear-participant $pid
    # Process them
done < good_participants.txt
```

---

### Parallel Processing

**Warning:** Don't run multiple instances with the same log file!

Instead, process different directories:

```bash
# Terminal 1: TSST visits
python scripts/process_signals.py --all --data-dir "TSST_Data" -o "tsst_processed"

# Terminal 2: PDST visits (different log!)
python scripts/process_signals.py --all --data-dir "PDST_Data" -o "pdst_processed"
```

---

## Summary

**Key Benefits:**
- ✅ Saves time by skipping already-processed files
- ✅ Automatically detects file changes
- ✅ Maintains processing history and metadata
- ✅ Allows selective reprocessing
- ✅ Tracks success/failure for each file

**Common Commands:**
```bash
# Normal use (incremental)
python scripts/process_signals.py --all

# Reprocess everything
python scripts/process_signals.py --all --force

# Reprocess one participant
python scripts/process_signals.py --all --clear-participant ID
```

**Processing Log:**
- Location: `<data_dir>/.signal_processing_log.json` or `<output_dir>/.signal_processing_log.json`
- Contains: File hash, processing date, success status, channels processed
- Keep it! Don't delete unless you want to reprocess everything

---

**Questions?** See `SIGNAL_PROCESSING_GUIDE.md` for comprehensive signal processing documentation.

**Last Updated:** October 31, 2025
