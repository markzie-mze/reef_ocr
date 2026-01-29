# Datasheet Lifecycle Management

How to handle datasheet versions, deprecation, and evolution.

## Why Versioning Matters

Field datasheets change over time:
- New fields added
- Fields removed or renamed
- Layout changes
- Checkbox options updated
- Species lists revised

Without version control:
- Old prompts break on new datasheets
- New prompts fail on historical data
- No way to track what changed

## Version Structure

Each datasheet type has versioned subfolders:

```
datasheets/coral/fish_census/
├── README.md           # Overview + version history
├── v1/                 # Version 1 (e.g., 2023 format)
│   ├── prompt.py
│   ├── config.json
│   ├── GUIDE.md
│   └── examples/
├── v2/                 # Version 2 (e.g., 2024 format)
│   ├── prompt.py
│   ├── config.json
│   ├── GUIDE.md
│   └── examples/
└── v3/                 # Version 3 (current)
    └── ...
```

## When to Create a New Version

### Requires New Version (v1 → v2)
- ❗ Field positions changed
- ❗ New fields added to datasheet
- ❗ Fields removed from datasheet
- ❗ Checkbox options changed
- ❗ Table structure changed
- ❗ Species list significantly revised

### Same Version, Update Files
- ✅ Prompt wording improvements
- ✅ Bug fixes in extraction logic
- ✅ Adding more reading tips
- ✅ Minor species list corrections
- ✅ Better examples added

## Creating a New Version

### Step 1: Identify the Change

Document what changed between datasheet versions:
- Compare old and new datasheet PDFs/images
- List all field changes
- Note any layout differences

### Step 2: Create Version Folder

```bash
mkdir datasheets/coral/fish_census/v2
```

### Step 3: Copy and Modify

```bash
# Start from previous version
cp datasheets/coral/fish_census/v1/* datasheets/coral/fish_census/v2/

# Then modify for new format
```

### Step 4: Update the Prompt

Edit `v2/prompt.py`:
- Update field locations
- Add/remove fields
- Update valid values
- Revise reading tips

### Step 5: Update Config

Edit `v2/config.json`:
- Update species lists
- Update valid value options
- Change output field names if needed

### Step 6: Add Examples

Add to `v2/examples/`:
- At least 2 photos of new format
- Expected CSV output
- Both clean and messy examples

### Step 7: Update README

In `datasheets/coral/fish_census/README.md`:

```markdown
## Version History

| Version | Date Range | Datasheet Dates | Changes |
|---------|------------|-----------------|---------|
| v2 | 2024-present | Nov 2024+ | Added GPS field, removed Current |
| v1 | 2023-2024 | Jan 2023 - Oct 2024 | Initial version |

## Current Version: v2

Use v2 for datasheets dated November 2024 or later.

## Migration Notes

v1 → v2 changes:
- GPS coordinates field added (top right)
- Current field removed
- Wave Exposure options changed from 3 to 4 choices
```

### Step 8: Test Both Versions

Ensure:
- v1 still works on old datasheets
- v2 works on new datasheets
- Script can select correct version

## Version Selection

### Manual Selection

User specifies version:
```bash
python scripts/extract.py coral/fish_census --version v2 ~/photos ~/output.csv
```

### Auto-Detection (Advanced)

For critical workflows, implement version detection:

```python
def detect_version(image_path):
    """Detect datasheet version from image features."""
    # Could check for:
    # - Presence of specific fields
    # - Logo differences
    # - Layout markers
    # - Date on sheet
    pass
```

### Date-Based Guidance

In the README, provide clear guidance:
```
- Datasheets dated before Nov 2024 → use v1
- Datasheets dated Nov 2024 or later → use v2
```

## Deprecating Versions

When a version is no longer in active use:

### Step 1: Mark as Deprecated

In `v1/GUIDE.md`:
```markdown
> ⚠️ **DEPRECATED**: This version is for historical datasheets only.
> For new datasheets, use v2.
```

### Step 2: Update Main README

```markdown
| v1 | 2023-2024 | ⚠️ Deprecated | Historical data only |
```

### Step 3: Keep It Working

**Never delete old versions** - you may need to reprocess historical data.

## Parallel Processing

During transition periods, you may have both old and new datasheets:

### Option 1: Separate Folders
```bash
# Process old format sheets
python scripts/extract.py coral/fish_census --version v1 ~/old_sheets ~/old_output.csv

# Process new format sheets
python scripts/extract.py coral/fish_census --version v2 ~/new_sheets ~/new_output.csv
```

### Option 2: Mixed Folder with Manual Sorting

1. Sort photos by datasheet version (check dates)
2. Process each batch separately
3. Combine outputs

## Testing Across Versions

When modifying shared code:

```bash
# Run tests for all versions
python -m pytest tests/

# Test specific version
python -m pytest tests/test_fish_census_v1.py
python -m pytest tests/test_fish_census_v2.py
```

## Version Compatibility Matrix

Maintain a compatibility matrix:

| Datasheet | Script v1.0 | Script v1.1 | Script v2.0 |
|-----------|-------------|-------------|-------------|
| fish_census v1 | ✅ | ✅ | ✅ |
| fish_census v2 | ❌ | ❌ | ✅ |

## Checklist for New Version

- [ ] Change documented in datasheet README
- [ ] Version folder created
- [ ] Prompt updated for new format
- [ ] Config updated (species, valid values)
- [ ] Guide updated with new field locations
- [ ] Examples added (min 2 images + expected output)
- [ ] Old version still works
- [ ] Tests pass for both versions
- [ ] Main README table updated
