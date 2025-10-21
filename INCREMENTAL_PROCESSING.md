# Incremental Processing Guide

The MOXIE quality check script now supports **incremental processing**, which tracks completed files and only processes new or changed data. This is especially useful when adding new participants to your study!

## How It Works

The script maintains a processing log (`.processing_log.json`) in your output directory that tracks:
- Which files have been processed
- When they were processed
- File checksums to detect changes
- Quality metrics summary
- Any processing errors

## Usage Examples

### 1. Normal Processing (Incremental Mode - Default)

```bash
python scripts/quality_check.py "/path/to/Participant Data" -o ./output
```

**What happens:**
- First run: Processes all files
- Subsequent runs: Only processes new/changed files
- Already-processed files are skipped automatically

**Example output:**
```
Processing History Summary
============================================================
Total files processed: 14
  Successful: 14
  Failed: 0
Participants: 7

Found 20 total ACQ files
Incremental mode: 6 new/changed files to process
                  14 files already processed (skipping)
```

### 2. Force Reprocess Everything

```bash
python scripts/quality_check.py "/path/to/Participant Data" -o ./output --force
```

Use when:
- You've updated the analysis code
- You want to regenerate all outputs
- You want to apply new quality parameters

### 3. Reprocess Specific Participant

```bash
python scripts/quality_check.py "/path/to/Participant Data" -o ./output --clear-participant 124961
```

This clears the processing history for participant 124961, so they'll be reprocessed on the next run.

Then run normal processing:
```bash
python scripts/quality_check.py "/path/to/Participant Data" -o ./output
```

### 4. Clear All History

```bash
python scripts/quality_check.py "/path/to/Participant Data" -o ./output --clear-all
```

**Warning:** This deletes all processing history. Next run will process all files.

## Processing Log

The processing log is stored in `output/.processing_log.json` and contains:

```json
{
  "/path/to/file.acq": {
    "participant_id": "124961",
    "visit_type": "TSST Visit",
    "filename": "TSST_Acqknowledge_124961_07_23_25.acq",
    "processed_date": "2025-10-19T17:45:23.123456",
    "success": true,
    "file_hash": "abc123...",
    "quality_summary": {
      "ECG2108000293": {
        "overall_quality": "excellent",
        "snr_flagged_pct": 0.0,
        "amp_flagged_pct": 0.0
      }
    }
  }
}
```

## Workflow Examples

### Adding New Participants

1. **Add new ACQ files** to your data directory:
   ```
   Participant_Data/
   ├── 124961/  (already processed)
   ├── 125200/  (NEW!)
   └── 125201/  (NEW!)
   ```

2. **Run quality check** (incremental mode):
   ```bash
   python scripts/quality_check.py "/path/to/Participant Data" -o ./output
   ```

3. **Only new participants are processed:**
   ```
   Found 20 total ACQ files
   Incremental mode: 4 new/changed files to process
                     16 files already processed (skipping)
   ```

### Updating Analysis Parameters

If you change quality check parameters (e.g., SNR threshold):

1. **Update config** in `src/core/config.py`:
   ```python
   QUALITY_CHECK_PARAMS = {
       "snr_alpha_threshold": 0.3,  # Changed from 0.5
       ...
   }
   ```

2. **Force reprocess** to apply new parameters:
   ```bash
   python scripts/quality_check.py "/path/to/Participant Data" -o ./output --force
   ```

### File Change Detection

The script automatically detects if ACQ files have changed:

```
Found 14 total ACQ files
  File changed since last processing: TSST_Acqknowledge_124961_07_23_25.acq
Incremental mode: 1 new/changed files to process
                  13 files already processed (skipping)
```

## Tips

1. **Don't delete `.processing_log.json`** unless you want to reprocess everything

2. **Version control:** Add `.processing_log.json` to `.gitignore` (it's already there)

3. **Check processing status:**
   ```bash
   # See what's been processed
   python scripts/quality_check.py "/path/to/Participant Data" -o ./output
   # (Will show summary and exit if all files are processed)
   ```

4. **Reprocess after errors:** Failed files are tracked. Fix the issue and run again - they'll be retried automatically.

## Command Reference

```
Options:
  -o, --output DIR           Output directory (default: ./output)
  -v, --verbose              Print detailed information
  --force                    Force reprocess all files
  --clear-participant ID     Clear history for specific participant
  --clear-all                Clear all processing history
  -h, --help                 Show help message
```

## Benefits

✓ **Save time**: Don't reprocess hundreds of files when adding a few participants
✓ **Track progress**: See what's been processed and what's pending
✓ **Detect changes**: Automatically reprocess if source files change
✓ **Error recovery**: Failed files are tracked and can be retried
✓ **Quality history**: Keep summary of quality metrics for each file

## Troubleshooting

**Q: All files are being reprocessed even though I didn't use --force**
A: Check if `.processing_log.json` exists in your output directory. If not, it's a fresh run.

**Q: A file keeps getting skipped but I want to reprocess it**
A: Use `--clear-participant <ID>` to clear that participant's history.

**Q: I want to start fresh**
A: Use `--clear-all` to delete all processing history.

**Q: Can I manually edit the processing log?**
A: Yes, it's JSON, but be careful! Better to use `--clear-participant` or `--clear-all`.
