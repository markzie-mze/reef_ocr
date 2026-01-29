# SHAMS Datasheet Extraction

AI-powered data extraction from field datasheets using Claude Vision API.

## Overview

This repository contains extraction prompts and scripts for digitizing handwritten field datasheets from SHAMS monitoring programs. Each datasheet type has a dedicated prompt optimized for that specific form layout.

**Key features:**
- Modular structure supporting multiple teams and datasheet types
- Version control for evolving datasheet formats
- Standardized prompt templates for consistency
- Validation against known species/value lists

## Supported Datasheets

| Team | Datasheet | Status | Current Version |
|------|-----------|--------|-----------------|
| **Coral** | Fish Census | ✅ Active | v1 |
| **Coral** | Coral Condition | 🚧 In Development | v1 |
| **Coral** | Juvenile Corals | 📋 Planned | - |
| **Coral** | Macroinvertebrate | 📋 Planned | - |
| **Turtle** | Nesting Survey | 📋 Planned | - |
| **Turtle** | Stranding Report | 📋 Planned | - |

## Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/your-org/datasheet_extraction.git
cd datasheet_extraction
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set API Key
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```
See [docs/API_SETUP.md](docs/API_SETUP.md) for detailed instructions.

### 3. Run Extraction
```bash
# Fish census example
python scripts/extract.py coral/fish_census ~/photos ~/output.csv
```

## Repository Structure

```
datasheet_extraction/
│
├── README.md                 # This file
├── CONTRIBUTING.md           # Guide for adding new datasheets
├── requirements.txt          # Python dependencies
├── .gitignore
│
├── datasheets/               # 📁 DATASHEET DEFINITIONS (by team)
│   │
│   ├── coral/                # Coral Monitoring Team
│   │   ├── fish_census/
│   │   │   ├── README.md           # Datasheet overview
│   │   │   └── v1/                 # Version 1 (current)
│   │   │       ├── prompt.py       # Extraction prompt
│   │   │       ├── config.json     # Valid values, species lists
│   │   │       ├── GUIDE.md        # Field locations & reading tips
│   │   │       └── examples/       # Test images + expected outputs
│   │   │
│   │   ├── coral_condition/
│   │   ├── juvenile_coral/
│   │   └── macroinvertebrate/
│   │
│   └── turtle/               # Turtle Conservation Team
│       ├── nesting_survey/
│       └── stranding_report/
│
├── src/                      # 📁 SHARED CODE
│   └── datasheet_extractor/
│       ├── __init__.py
│       ├── extractor.py      # Core extraction engine
│       ├── validators.py     # Data validation utilities
│       └── formatters.py     # Output formatting (CSV, JSON)
│
├── scripts/                  # 📁 CLI TOOLS
│   ├── extract.py            # Main extraction script
│   ├── validate.py           # Validate extraction results
│   └── batch.py              # Batch processing utilities
│
├── tests/                    # 📁 AUTOMATED TESTS
│   ├── test_fish_census.py
│   └── ...
│
└── docs/                     # 📁 DOCUMENTATION
    ├── API_SETUP.md          # Getting API access
    ├── PROMPT_GUIDE.md       # Writing effective prompts
    ├── LIFECYCLE.md          # Version management
    └── TROUBLESHOOTING.md    # Common issues
```

## How It Works

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│ Photo       │ ──▶ │ Claude API   │ ──▶ │ JSON        │ ──▶ │ CSV      │
│ (datasheet) │     │ + Prompt     │     │ (structured)│     │ (output) │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────┘
```

1. User provides folder of datasheet photos
2. Script loads the appropriate prompt for that datasheet type
3. Each image is sent to Claude Vision API
4. Claude extracts data as structured JSON
5. Data is validated and flattened to CSV

## Cost Estimates

| Model | Per Image | 100 sheets | 500 sheets |
|-------|-----------|------------|------------|
| Sonnet 4 | ~$0.03 | ~$3 | ~$15 |
| Opus 4.5 | ~$0.25 | ~$25 | ~$125 |

💡 **Tip**: Use Sonnet for bulk work, Opus for difficult/critical sheets.

## For Contributors

### Adding a New Datasheet

1. Create folder: `datasheets/{team}/{datasheet_name}/v1/`
2. Write the prompt: `prompt.py`
3. Define valid values: `config.json`
4. Document field locations: `GUIDE.md`
5. Add test examples: `examples/`
6. Submit PR with accuracy report

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed instructions.

### Updating an Existing Datasheet

When a datasheet format changes:
1. Keep current version working (for processing old sheets)
2. Create new version folder: `v2/`
3. Update README with migration notes
4. Test with both old and new formats

See [docs/LIFECYCLE.md](docs/LIFECYCLE.md) for version management.

## Team Contacts

| Team | Contact | Responsibility |
|------|---------|----------------|
| Knowledge Management | [name] | Repo maintenance, prompt review |
| Coral Monitoring | [name] | Coral datasheet prompts |
| Turtle Conservation | [name] | Turtle datasheet prompts |

## Links

- [API Setup Guide](docs/API_SETUP.md)
- [Prompt Writing Guide](docs/PROMPT_GUIDE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Anthropic Console](https://console.anthropic.com)
