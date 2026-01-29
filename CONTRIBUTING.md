# Contributing: Adding New Datasheet Extractors

This guide walks you through creating a new extractor for a datasheet type.

## Before You Start

You'll need:
- [ ] A clear photo of the datasheet (ideally blank + filled example)
- [ ] Understanding of all fields on the datasheet
- [ ] List of valid values for dropdown/checkbox fields
- [ ] Species list or other lookup values (if applicable)
- [ ] Access to Claude API for testing

## Step 1: Create the Folder Structure

```bash
# Example: Adding a turtle nesting survey extractor
mkdir -p datasheets/turtle/nesting_survey/v1/examples
touch datasheets/turtle/nesting_survey/__init__.py
touch datasheets/turtle/nesting_survey/v1/__init__.py
```

Your folder should contain:
```
datasheets/turtle/nesting_survey/
├── README.md            # Overview + version history
├── __init__.py
└── v1/
    ├── __init__.py
    ├── prompt.py        # The extraction prompt
    ├── config.json      # Valid values, species lists
    ├── GUIDE.md         # Field locations & reading tips
    └── examples/        # Test images + expected outputs
```

## Step 2: Analyze the Datasheet

Before writing any code, document the datasheet thoroughly.

### Create DATASHEET_GUIDE.md

```markdown
# Turtle Nesting Survey - Datasheet Guide

## Datasheet Version
- **Current version**: 2024-v1
- **Last updated**: March 2024
- **Changes from previous**: Added GPS coordinates field

## Layout Overview
[Describe the general layout - header position, data sections, etc.]

## Field Locations

### Header Section (Top)
| Field | Position | Format | Example |
|-------|----------|--------|---------|
| Date | Top left | DD/MM/YYYY | 15/03/2024 |
| Beach | Below date | Text | Ras Baridi |
| Observer | Top right | Text | Ahmed |

### Nest Data Section
| Field | Position | Format | Valid Values |
|-------|----------|--------|--------------|
| Species | Column 1 | Checkbox | CM, EI, CC, LO |
| Activity | Column 2 | Checkbox | Nesting, False crawl, Emerged |

## Common Reading Challenges
- GPS coordinates often smudged
- Species checkboxes may be unclear - CM and CC look similar
- Track width written in different units (cm vs m)

## Observer Handwriting Notes
- Ahmed: writes 7s with a cross
- Fatima: very small handwriting, may need zoom
```

## Step 3: Write the Prompt

Start with the template in `templates/PROMPT_TEMPLATE.md`.

### Key Sections to Include

```markdown
## METADATA EXTRACTION
[List every header field with exact location]

## DATA TABLE EXTRACTION  
[Describe each column, valid values, how to read marks]

## VALID VALUES LIST
[Include ALL acceptable values - species, locations, codes]

## READING TIPS
[Specific guidance for this datasheet's challenges]

## OUTPUT FORMAT
[Exact JSON structure expected]

## CHECKLIST
[Final verification steps]
```

### Prompt Writing Tips

1. **Be specific about locations**
   - ❌ "Find the date field"
   - ✅ "Date is in the top-left header box, below the SHAMS logo"

2. **Include all valid values**
   - Don't assume the model knows species codes
   - List every option for checkbox fields

3. **Anticipate reading problems**
   - Note similar-looking characters (1/7, O/0)
   - Mention if pencil vs pen is common

4. **Provide examples in the output format**
   - Show realistic data, not just placeholders

## Step 4: Create the Extraction Script

Copy from `templates/extract_template.py` and customize:

```python
#!/usr/bin/env python3
"""
SHAMS Turtle Nesting Survey Data Extractor

Usage:
    python extract.py INPUT_FOLDER OUTPUT_CSV
"""

# ... [standard imports]

# Embed your prompt here
EXTRACTION_PROMPT = """
[Your complete prompt from PROMPT.md]
"""

# Define your output columns
OUTPUT_FIELDS = [
    "date", "beach", "observer",
    "nest_id", "species", "activity",
    "track_width_cm", "gps_lat", "gps_lon",
    # ... etc
]

# ... [rest of standard extraction code]
```

### Key Customizations

1. **OUTPUT_FIELDS**: Match your CSV column structure
2. **flatten_to_rows()**: Convert JSON response to flat rows
3. **Validation**: Add any data validation specific to this datasheet

## Step 5: Test Thoroughly

### Test with Reference Sheets

1. Add example photos to `reference_sheets/turtle/`
2. Create expected output: `nesting_survey_expected.csv`
3. Run and compare:

```bash
python extract.py ../../reference_sheets/turtle/ test_output.csv
diff test_output.csv ../../reference_sheets/turtle/nesting_survey_expected.csv
```

### Test Edge Cases

- [ ] Blank fields
- [ ] Messy handwriting
- [ ] Partially filled sheets
- [ ] Multiple sheets from same survey
- [ ] Different observers' handwriting

### Document Accuracy

In your PR, include:
- Number of test images
- Accuracy rate per field
- Known issues/limitations

## Step 6: Document for Users

Update the main README.md table:

```markdown
| Turtle | Nesting Survey | ✅ Active | v1.0 |
```

Add usage example to your extractor's folder.

## Step 7: Submit PR

Your PR should include:
- [ ] All files in the extractor folder
- [ ] At least 2 reference images with expected output
- [ ] Accuracy report from testing
- [ ] Updated main README.md

## Version Management

### When to Create a New Version

- Datasheet layout changes
- New fields added
- Fields removed or renamed
- Checkbox options change

### How to Version

```bash
# Archive current version
mv extractors/turtle/nesting_survey/extract.py \
   extractors/turtle/nesting_survey/versions/v1.0/

# Same for prompt and guide
mv extractors/turtle/nesting_survey/PROMPT.md \
   extractors/turtle/nesting_survey/versions/v1.0/

# Create new versions
# ... edit files for new datasheet ...
```

### Version Naming

- `v1.0` - Initial release
- `v1.1` - Minor prompt improvements (same datasheet)
- `v2.0` - New datasheet version

## Getting Help

- **Prompt not working well?** See `docs/PROMPT_ENGINEERING.md`
- **API issues?** See `docs/TROUBLESHOOTING.md`
- **Not sure about structure?** Look at `extractors/coral/fish_census/` as reference

## Checklist for New Extractor

- [ ] Folder structure created
- [ ] DATASHEET_GUIDE.md documents all fields
- [ ] PROMPT.md is comprehensive with valid values
- [ ] extract.py runs without errors
- [ ] Reference images added
- [ ] Expected output CSV created
- [ ] Tested with 5+ real datasheets
- [ ] Accuracy documented
- [ ] Main README.md updated
- [ ] PR submitted
