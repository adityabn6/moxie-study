# MOXIE Study - Documentation Index

**Last Updated:** November 5, 2025

---

## Quick Navigation

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [README.md](#readmemd) | Project overview and quick start | First time setup, general overview |
| [SETUP_GUIDE.md](#setup_guidemd) | Installation and environment setup | Initial installation |
| [WORKFLOW_QUICK_REFERENCE.md](#workflow_quick_referencemd) | Quick command reference | Daily workflow, command lookup |
| [SIGNAL_PROCESSING_GUIDE.md](#signal_processing_guidemd) | Signal processing details | Processing ECG, EDA, RSP, BP signals |
| [FEATURE_EXTRACTION_SUMMARY.md](#feature_extraction_summarymd) | Basic feature extraction (28 features) | Understanding basic features |
| [ENHANCED_FEATURES_COMPARISON.md](#enhanced_features_comparisonmd) | Enhanced vs basic comparison (66 features) | **Recommended for stress research** |
| [OPTIMAL_STRESS_FEATURES.md](#optimal_stress_featuresmd) | All optimal features with evidence | Detailed feature specifications |
| [SIGNAL_PROCESSING_VALIDATION.md](#signal_processing_validationmd) | Validation report | Verifying signal quality |
| [INCREMENTAL_PROCESSING.md](#incremental_processingmd) | Incremental processing for quality checks | Quality assessment workflow |
| [INCREMENTAL_SIGNAL_PROCESSING_GUIDE.md](#incremental_signal_processing_guidemd) | Incremental processing for signals | Signal processing workflow |
| [QUALITY_ANALYSIS_GUIDE.md](#quality_analysis_guidemd) | Quality analysis and reporting | Analyzing data quality |
| [ARCHITECTURE.md](#architecturemd) | Technical architecture | Understanding codebase structure |
| [SESSION_SUMMARY.md](#session_summarymd) | Latest session work summary | Recent changes and accomplishments |

---

## Getting Started Path

If you're new to this project, follow this sequence:

1. **[README.md](#readmemd)** - Understand what the project does
2. **[SETUP_GUIDE.md](#setup_guidemd)** - Install dependencies and set up environment
3. **[WORKFLOW_QUICK_REFERENCE.md](#workflow_quick_referencemd)** - Learn the basic commands
4. **[SIGNAL_PROCESSING_GUIDE.md](#signal_processing_guidemd)** - Process your first signals
5. **[ENHANCED_FEATURES_COMPARISON.md](#enhanced_features_comparisonmd)** - Extract features for analysis

---

## Document Descriptions

### README.md
**Type:** Overview
**Length:** ~350 lines
**Covers:**
- Project overview and capabilities
- Installation instructions
- Quick start guides for signal processing, feature extraction, and quality checks
- Expected data structure
- Development roadmap

**Use when:** You need a general overview or are setting up the project for the first time.

---

### SETUP_GUIDE.md
**Type:** Installation
**Length:** Not yet read
**Covers:**
- Detailed installation steps
- Environment configuration
- Troubleshooting setup issues

**Use when:** Installing the project or setting up a new environment.

---

### WORKFLOW_QUICK_REFERENCE.md
**Type:** Command Reference
**Length:** Not yet read
**Covers:**
- Quick command reference for common tasks
- Step-by-step workflows
- Common command patterns

**Use when:** You need to quickly look up a command or workflow.

---

### SIGNAL_PROCESSING_GUIDE.md
**Type:** Technical Guide
**Length:** ~500 lines (18 KB)
**Covers:**
- Detailed NeuroKit2 signal processing
- ECG: R-peak detection, heart rate, P/Q/S/T wave delineation
- EDA: Phasic/tonic decomposition, SCR detection
- RSP: Breathing rate, peak/trough detection, respiratory variability
- Blood Pressure: Signal cleaning, statistical analysis
- Output file formats (CSV structure, plots)
- Troubleshooting common issues
- API reference

**Use when:** Processing physiological signals or understanding what the processing does.

---

### FEATURE_EXTRACTION_SUMMARY.md
**Type:** Feature Guide
**Length:** ~275 lines
**Covers:**
- Basic feature extraction (28 features)
- Feature descriptions (HRV, EDA, RSP, BP)
- Output CSV structure (146 windows × 28 features)
- R usage examples
- Statistical analysis suggestions
- Data quality notes

**Use when:** Understanding the basic feature set or loading data into R.

---

### ENHANCED_FEATURES_COMPARISON.md ⭐ RECOMMENDED
**Type:** Feature Comparison & Guide
**Length:** ~398 lines
**Covers:**
- **Basic vs Enhanced comparison** (28 vs 66 features)
- **Detailed breakdown by signal type**
- **Top 5 must-have stress biomarkers**
- Expected stress response patterns (TSST)
- R analysis examples
- Statistical implications
- Why enhanced features matter for stress research

**Use when:** Deciding between basic and enhanced extraction, or understanding stress biomarkers.

**Key Highlights:**
- LF/HF ratio (⭐⭐⭐⭐⭐) - Gold standard stress biomarker
- Thoracic-abdominal breathing coordination (⭐⭐⭐⭐) - Paradoxical breathing detection
- SCR amplitude and dynamics (⭐⭐⭐) - Arousal intensity measurement

---

### OPTIMAL_STRESS_FEATURES.md
**Type:** Technical Specification
**Length:** ~480 lines
**Covers:**
- All 60+ recommended features for stress research
- Priority rankings with star ratings
- Implementation code snippets
- Research evidence citations
- Expected physiological ranges
- Feature-by-feature specifications

**Use when:** You need detailed technical specifications or want to understand the research evidence.

---

### SIGNAL_PROCESSING_VALIDATION.md
**Type:** Validation Report
**Length:** ~305 lines
**Covers:**
- Signal quality analysis for test participant (124961)
- Validation metrics (HR, respiratory rate, EDA levels)
- Comparison with NeuroKit MCP best practices
- Implementation validation status
- Recommendations for improvements
- Reference ranges for all signals

**Use when:** Verifying that signal processing is working correctly or checking data quality.

---

### INCREMENTAL_PROCESSING.md
**Type:** Workflow Guide
**Length:** Not fully read
**Covers:**
- Incremental processing for quality checks
- `.processing_log.json` tracking
- Skip already-processed files
- Force reprocessing options

**Use when:** Running quality checks and want to avoid reprocessing existing files.

---

### INCREMENTAL_SIGNAL_PROCESSING_GUIDE.md
**Type:** Workflow Guide
**Length:** ~485 lines
**Covers:**
- Incremental processing for signal processing
- `.signal_processing_log.json` tracking
- File change detection (MD5 hashing)
- Batch processing workflows
- Command reference (--force, --clear-participant, --clear-all)
- Best practices and troubleshooting

**Use when:** Running signal processing on new participants without reprocessing existing ones.

---

### QUALITY_ANALYSIS_GUIDE.md
**Type:** Analysis Guide
**Length:** Not yet read
**Covers:**
- Quality analysis and reporting
- Identifying protocol issues
- Data quality metrics

**Use when:** Analyzing quality check results and generating reports.

---

### ARCHITECTURE.md
**Type:** Technical Documentation
**Length:** ~331 lines
**Covers:**
- Design philosophy and principles
- Core architecture and data flow
- Module hierarchy (core, io, quality, visualization, processing)
- Key classes (BioData, DataObject, Window)
- Quality assessment pipeline (SNR, Amplitude)
- Visualization system (Bokeh)
- Extension points for adding features
- Future enhancements roadmap

**Use when:** Understanding the codebase structure or planning to extend functionality.

---

### SESSION_SUMMARY.md
**Type:** Session Report
**Length:** ~403 lines
**Covers:**
- Complete summary of November 5, 2025 session work
- What was accomplished (6 major tasks)
- Signal processing validation
- NeuroKit MCP integration
- Basic feature extraction (28 features)
- Enhanced feature extraction (66 features)
- Optimal feature analysis
- File structure and outputs
- Next steps for analysis
- R analysis examples

**Use when:** You want to understand the latest work done on the project or see what features were recently added.

---

### DOCUMENTATION_CHANGELOG.md
**Type:** Change Log
**Length:** ~285 lines (October 31, 2025 version)
**Covers:**
- Documentation updates for v0.2.0 (signal processing)
- Files modified and new sections added
- Documentation coverage metrics
- Quality assurance notes

**Use when:** Tracking documentation changes or understanding when features were documented.

---

## Feature Extraction Documents - Decision Tree

```
┌─────────────────────────────────────────┐
│ Do you need to extract features?        │
└────────────────┬────────────────────────┘
                 │
                 ▼
         ┌───────────────────┐
         │ What type of      │
         │ analysis?         │
         └────────┬──────────┘
                  │
      ┌───────────┴──────────┐
      │                      │
      ▼                      ▼
┌─────────────┐      ┌──────────────────┐
│ Quick       │      │ Stress Research  │
│ Exploration │      │ (Publication)    │
└──────┬──────┘      └────────┬─────────┘
       │                      │
       ▼                      ▼
┌──────────────────┐  ┌────────────────────────────┐
│ Use BASIC        │  │ Use ENHANCED               │
│ (28 features)    │  │ (66 features) ⭐          │
│                  │  │                            │
│ See:             │  │ See:                       │
│ - FEATURE_       │  │ - ENHANCED_FEATURES_      │
│   EXTRACTION_    │  │   COMPARISON.md           │
│   SUMMARY.md     │  │ - OPTIMAL_STRESS_         │
│                  │  │   FEATURES.md             │
└──────────────────┘  └────────────────────────────┘
```

---

## Stress Research - Recommended Reading Order

For stress/anxiety research using MOXIE data:

1. **[ENHANCED_FEATURES_COMPARISON.md](#enhanced_features_comparisonmd)** - Start here! Understand what the enhanced features provide
2. **[OPTIMAL_STRESS_FEATURES.md](#optimal_stress_featuresmd)** - Deep dive into each feature
3. **[SIGNAL_PROCESSING_VALIDATION.md](#signal_processing_validationmd)** - Verify data quality
4. **[SESSION_SUMMARY.md](#session_summarymd)** - See R analysis examples and next steps

---

## Technical Implementation - Recommended Reading Order

For developers or those modifying the codebase:

1. **[ARCHITECTURE.md](#architecturemd)** - Understand the overall structure
2. **[SIGNAL_PROCESSING_GUIDE.md](#signal_processing_guidemd)** - Signal processing details
3. **[OPTIMAL_STRESS_FEATURES.md](#optimal_stress_featuresmd)** - Feature implementation code
4. **[DOCUMENTATION_CHANGELOG.md](#documentation_changelogmd)** - Track changes

---

## Common Tasks - Document Quick Reference

### Task: "I want to process signals"
→ [SIGNAL_PROCESSING_GUIDE.md](#signal_processing_guidemd)
→ [INCREMENTAL_SIGNAL_PROCESSING_GUIDE.md](#incremental_signal_processing_guidemd)

### Task: "I want to extract features for R analysis"
→ [ENHANCED_FEATURES_COMPARISON.md](#enhanced_features_comparisonmd) (RECOMMENDED)
→ [FEATURE_EXTRACTION_SUMMARY.md](#feature_extraction_summarymd) (if using basic)

### Task: "I need to understand HRV LF/HF ratio"
→ [ENHANCED_FEATURES_COMPARISON.md](#enhanced_features_comparisonmd) (lines 42-68)
→ [OPTIMAL_STRESS_FEATURES.md](#optimal_stress_featuresmd) (lines 209-222)

### Task: "I want to check data quality"
→ [SIGNAL_PROCESSING_VALIDATION.md](#signal_processing_validationmd)
→ [QUALITY_ANALYSIS_GUIDE.md](#quality_analysis_guidemd)

### Task: "I don't want to reprocess existing participants"
→ [INCREMENTAL_SIGNAL_PROCESSING_GUIDE.md](#incremental_signal_processing_guidemd)

### Task: "I need to understand breathing coordination features"
→ [ENHANCED_FEATURES_COMPARISON.md](#enhanced_features_comparisonmd) (lines 119-166)
→ [OPTIMAL_STRESS_FEATURES.md](#optimal_stress_featuresmd) (lines 148-178)

### Task: "I want to see what was done in the latest session"
→ [SESSION_SUMMARY.md](#session_summarymd)

---

## Documentation Status

| Category | Status | Notes |
|----------|--------|-------|
| **Signal Processing** | ✅ Complete | Comprehensive guide available |
| **Feature Extraction** | ✅ Complete | Both basic and enhanced documented |
| **Stress Biomarkers** | ✅ Complete | All features with evidence |
| **Quality Analysis** | ✅ Complete | Validation and quality guides |
| **Incremental Processing** | ✅ Complete | Both quality and signal workflows |
| **R Integration** | ✅ Complete | Examples in multiple documents |
| **Troubleshooting** | ✅ Complete | In relevant guides |
| **API Reference** | ✅ Complete | In technical guides |

---

## Version History

### v0.3.0 (November 5, 2025)
- Added feature extraction documentation (5 new documents)
- Enhanced feature set (66 features) with stress biomarkers
- Signal processing validation report
- Session summary with R examples

### v0.2.0 (October 31, 2025)
- Added signal processing documentation
- NeuroKit2 integration
- Comprehensive signal processing guide

### v0.1.0 (Earlier)
- Initial documentation
- Quality assessment
- Architecture overview

---

## Contributing to Documentation

When adding new documentation:
1. Add entry to this index with description
2. Update DOCUMENTATION_CHANGELOG.md
3. Cross-reference related documents
4. Add to appropriate "Recommended Reading Order" section
5. Update version history

---

## Contact & Support

For questions about:
- **Signal Processing**: See SIGNAL_PROCESSING_GUIDE.md, SIGNAL_PROCESSING_VALIDATION.md
- **Feature Extraction**: See ENHANCED_FEATURES_COMPARISON.md, OPTIMAL_STRESS_FEATURES.md
- **R Analysis**: See SESSION_SUMMARY.md (lines 231-304), ENHANCED_FEATURES_COMPARISON.md (lines 260-303)
- **Technical Issues**: See ARCHITECTURE.md, relevant troubleshooting sections

---

**Last Updated:** November 5, 2025
**Documentation Version:** v0.3.0
**Total Documents:** 14 files
