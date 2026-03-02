# Prompt Writing Guide

How to write effective extraction prompts for SHAMS datasheets.

## Why Prompts Matter

The prompt is the most critical component of extraction accuracy. A well-written prompt can mean the difference between 60% and 95% accuracy.

**Key insight**: Claude has never seen your specific datasheet before. You need to describe it completely as if explaining to someone who's never seen it.

Once it knows and learns idiosyncracies of different datasheets, observers, etc it learns so keep iterating on the prompt to improve it and with it the AI's ability to accurately record and translate the datasheets.

## Prompt Structure

Every extraction prompt should have these sections:

```
1. Introduction (what datasheet is this?)
2. Metadata Fields (header info)
3. Data Table Structure (main content)
4. Valid Values Lists (species, codes, options)
5. Reading Tips (handwriting, tally marks)
6. Output Format (exact JSON structure)
7. Verification Checklist (final checks)
```

## Section-by-Section Guide

### 1. Introduction

Tell Claude exactly what it's looking at:

```markdown
You are extracting data from a SHAMS "Baseline Assessment - Fish census" 
field datasheet used for coral reef monitoring in the Red Sea.

The datasheet has two main sections:
- LEFT: Main fish observation table with size classes
- RIGHT: Metadata panel and indicator species
```

### 2. Metadata Fields

**Be extremely specific about locations:**

❌ Bad:
```markdown
Extract the date from the form.
```

✅ Good:
```markdown
### Date & Time
- Location: Right side "Meta Data" panel, second line below "Observer name"
- Format: DD/MM/YYYY followed by time as HH:MM
- Example: "27/11/2026 12:23"
- Note: Time may use "o" instead of ":" (e.g., "12o23")
```

**Use tables for multiple fields:**

```markdown
| Field | Location | Format | Example |
|-------|----------|--------|---------|
| Site code | Meta Data panel, line 3 | XX0000_00 | FB0015_01 |
| Depth | Below site code | Integer (m) | 6 |
| Bearing | Below Current | Degrees 0-360 | 110 |
```

### 3. Checkbox Fields

Checkboxes are tricky - be explicit:

```markdown
### Sea State (checkbox field)
Three options in a row - only ONE should be marked:
- □ Calm (left box)
- □ Moderate (middle box)  
- □ Rough (right box)

How to identify marks:
- Look for: ✓ checkmark, X, filled/shaded box, or circle
- The mark may be faint pencil
- If unclear, check which box has ANY mark inside it
```

### 4. Data Table Structure

Describe the table layout completely:

```markdown
### Main Fish Table

**Location**: Left 2/3 of datasheet
**Header row**: "<10cm | 11-20cm | 21-30cm | 31-40cm | 41-50cm | 50+cm"

**Row structure**:
- Column 1: Family name (colored band header) or species name
- Columns 2-7: Size class tally marks

**Family groups** (in order from top):
1. Parrotfish (green band) - 13 species
2. Surgeonfish (blue band) - 10 species
3. Rabbitfish (grey band) - 4 species
...

**IMPORTANT**: Cheilinus undulatus (Napoleon wrasse) is at the BOTTOM 
of the table under "Wrasses" - don't miss it!
```

### 5. Valid Values Lists

**Include COMPLETE lists** - don't assume Claude knows species names:

```markdown
### Valid Species - Parrotfish
Extract ONLY these exact names:
- Bolbometopon muricatum
- Calotomus viridescens
- Cetoscarus bicolor
- Chlorurus gibbus
- Chlorurus sordidus
- Hipposcarus harid
- Scarus collana
- Scarus ferrugineus
- Scarus frenatus
- Scarus fuscopurpureus
- Scarus ghobban
- Scarus niger
- Scarus psittacus

If a species name doesn't match this list exactly, flag it in issues.
```

### 6. Reading Tips

This is where your domain knowledge helps:

```markdown
## Tally Mark Reading

Standard tally system:
- I = 1
- II = 2
- III = 3
- IIII = 4
- IIII with diagonal strike (####) = 5

**Common patterns**:
- #### II = 7 (five + two)
- #### #### = 10 (two groups of five)

**Watch for**:
- Faint pencil marks - still count them
- Slanted tallies - common in field conditions
- Multiple tally groups in one cell - add them together
- Tally marks that cross cell boundaries - attribute to correct cell
```

```markdown
## Handwriting Challenges

**Similar characters**:
- 1 and 7: Look for the horizontal stroke on 7
- 0 and O: Context usually clarifies (numbers vs letters)
- 6 and 0: Check the loop closure

**Observer-specific notes**:
- Observer "Ahmed" writes 7s with a cross stroke
- Observer "Fatima" has small writing - zoom in mentally
```

### 7. Output Format

Provide the EXACT JSON structure with realistic examples:

```markdown
## Output Format

Return ONLY valid JSON (no other text):

```json
{
  "metadata": {
    "site_code": "FB0015_01",
    "date": "2026-11-27",
    "time": "12:23",
    "observer": "Mahmoud",
    "transect": 2,
    "depth_m": 6,
    "current": "Low",
    "temp_c": 27,
    "bearing": 110,
    "visibility_m": 10,
    "sea_state": "Calm",
    "wave_exposure": "Exposed",
    "reef_zone": "Slope"
  },
  "fish_observations": [
    {
      "family": "Parrotfish",
      "species": "Scarus ferrugineus",
      "size_class": "11-20cm",
      "count": 3
    }
  ],
  "extraction_notes": {
    "confidence": "HIGH",
    "issues": []
  }
}
```

### Field rules:
- Use `null` for empty/unreadable fields
- Use exact values from valid values lists
- Only include observations where count > 0
- Date format: YYYY-MM-DD
- Time format: HH:MM (24-hour)
```

### 8. Verification Checklist

End with explicit checks:

```markdown
## Before Returning JSON

Verify each of these:

1. ✓ Transect number - did you read the actual number (not assume 1)?
2. ✓ Checkbox fields - did you check ALL boxes to find the marked one?
3. ✓ Species names - do they ALL match the valid species list exactly?
4. ✓ Zero counts - did you exclude rows with no tally marks?
5. ✓ Cheilinus undulatus - did you check the bottom of the main table?
6. ✓ Incidental sightings - did you check the free-text box at bottom right?
```

## Common Prompt Mistakes

### Mistake 1: Vague Locations
❌ "Find the observer name"
✅ "Observer name is at the top of the 'Meta Data' panel on the right side"

### Mistake 2: Missing Valid Values
❌ "Extract the species"
✅ "Species must be one of: [complete list]"

### Mistake 3: Assuming Knowledge
❌ "Use standard tally marks"
✅ "Tally marks: I=1, II=2, III=3, IIII=4, ####=5..."

### Mistake 4: Unclear Output Format
❌ "Return the data as JSON"
✅ [Complete JSON example with all fields]

### Mistake 5: No Error Handling
❌ (nothing about unclear data)
✅ "If a field is unreadable, use null and add to issues list"

## Testing Your Prompt

### Test 1: Clear Datasheet
- Use a cleanly filled example
- Expect 95%+ accuracy
- Any errors indicate prompt gaps

### Test 2: Messy Handwriting
- Use a real field datasheet
- Note which fields fail
- Add reading tips for problem areas

### Test 3: Edge Cases
- Blank optional fields
- Maximum tallies in one cell
- Unusual but valid values

### Test 4: Different Observers
- Test with multiple handwriting styles
- Add observer-specific notes if patterns emerge

## Iterating on Prompts

1. **Run extraction** on 5-10 test images
2. **Compare** output to manual reading
3. **Identify** consistent errors
4. **Add** specific guidance for those errors
5. **Re-test** and repeat

Keep notes on what you changed and why:

```markdown
## Prompt Changelog

### 2024-11-28
- Added explicit note about Cheilinus at bottom of table (was being missed)
- Added tally mark examples for counts over 10
- Specified that ">" in visibility means "greater than"

### 2024-11-25
- Initial prompt version
```

## Prompt Checklist

Before finalizing a prompt:

- [ ] All metadata fields have specific locations
- [ ] All checkbox fields list every option
- [ ] Complete valid values lists included
- [ ] Tally mark reading explained
- [ ] Output JSON format shown with example
- [ ] Verification checklist at end
- [ ] Tested with 5+ real datasheets
- [ ] Error handling for unclear data
- [ ] Observer handwriting notes (if applicable)
