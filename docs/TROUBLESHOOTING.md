# Troubleshooting Guide

Common issues and solutions for datasheet extraction.

## API Issues

### "Invalid API key"

**Symptoms**: 401 error, "Invalid API key provided"

**Solutions**:
1. Check for extra spaces or line breaks in your key
   ```bash
   echo $ANTHROPIC_API_KEY | cat -A  # Should show no extra chars
   ```

2. Re-export the key as a single line:
   ```bash
   unset ANTHROPIC_API_KEY
   export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
   ```

3. Verify the key at [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)

### "Insufficient credits" / 402 Error

**Symptoms**: Payment required error

**Solutions**:
1. Add credits at [console.anthropic.com/settings/billing](https://console.anthropic.com/settings/billing)
2. Check your spending limit hasn't been reached

### "Rate limit exceeded" / 429 Error

**Symptoms**: Too many requests error

**Solutions**:
1. Add delay between requests:
   ```bash
   python scripts/extract.py coral/fish_census ~/photos ~/output.csv --delay 2
   ```
2. Wait a few minutes and retry
3. For large batches, process in smaller groups

### "Connection error" / Timeout

**Symptoms**: Network errors, timeouts

**Solutions**:
1. Check internet connection
2. Retry - may be temporary API issue
3. For large images, check file size (compress if >10MB)

## File Issues

### "No image files found"

**Symptoms**: Script says no images in folder

**Solutions**:
1. Check the path is correct:
   ```bash
   ls ~/Desktop/fish_photos/  # Should list your images
   ```

2. Check file extensions are supported (.jpg, .jpeg, .png, .heic, .heif)

3. Make sure images aren't in a subfolder:
   ```bash
   # Wrong: ~/photos/subfolder/image.jpg
   # Right: ~/photos/image.jpg
   ```

### "Permission denied"

**Symptoms**: Can't read input or write output

**Solutions**:
1. Check folder permissions:
   ```bash
   ls -la ~/Desktop/fish_photos/
   ```

2. Try a different output location:
   ```bash
   python scripts/extract.py coral/fish_census ~/photos ~/Desktop/output.csv
   ```

### "Path not found"

**Symptoms**: Input folder doesn't exist

**Solutions**:
1. Use absolute path or correct relative path
2. Remember `~` expands to your home directory
3. Check for typos in path

## Extraction Issues

### Missing Species/Observations

**Symptoms**: Known data not appearing in output

**Possible causes**:
1. **Faint marks**: Add note in prompt about pencil marks
2. **Bottom of table**: Some species (like Cheilinus) are easy to miss
3. **Wrong column**: Data attributed to adjacent cell

**Solutions**:
1. Review the prompt for that species location
2. Add explicit notes about commonly missed areas
3. Use Opus model for better accuracy

### Wrong Counts

**Symptoms**: Tally marks miscounted

**Possible causes**:
1. Strike-through not recognized as "5"
2. Multiple tally groups not added
3. Marks too faint

**Solutions**:
1. Add explicit tally examples in prompt:
   ```
   #### = 5 (four with diagonal)
   #### III = 8 (five plus three)
   ```
2. Note about faint pencil marks

### Wrong Metadata

**Symptoms**: Site code, date, observer incorrect

**Common issues**:
1. **Transect always "1"**: Prompt doesn't specify where to find it
2. **Wrong checkbox**: Not checking all options
3. **Date format**: Different than expected

**Solutions**:
1. Add explicit location for each metadata field
2. List all checkbox options with positions
3. Show date format examples

### JSON Parse Error

**Symptoms**: "JSON parse error" in output

**Causes**:
1. Model returned text outside JSON
2. Malformed JSON from model
3. Unexpected characters

**Solutions**:
1. Make prompt clearer about "return ONLY JSON"
2. The script should handle markdown code blocks - check it does
3. If persistent, try different model

## Quality Issues

### Low Accuracy

**Symptoms**: Many errors across extractions

**Diagnosis**:
1. Test with a clean, clear datasheet first
2. If clean sheets fail → prompt issue
3. If only messy sheets fail → handwriting tips needed

**Solutions**:
1. Review and improve prompt (see PROMPT_GUIDE.md)
2. Add more specific field locations
3. Include complete valid values lists
4. Try Opus model instead of Sonnet

### Inconsistent Results

**Symptoms**: Same image gives different results

**Causes**:
1. Model temperature (slight randomness)
2. Ambiguous prompt
3. Genuinely unclear data

**Solutions**:
1. Make prompt more explicit
2. Add verification checklist
3. For critical data, run twice and compare

### Slow Processing

**Symptoms**: Takes very long per image

**Causes**:
1. Large image files
2. Opus model (slower than Sonnet)
3. Rate limiting

**Solutions**:
1. Compress images before processing
2. Use Sonnet for bulk work, Opus for difficult sheets
3. Check for rate limit pauses

## Getting Help

### Before Asking for Help

1. Check this guide first
2. Note the exact error message
3. Try with a single, simple image
4. Check your prompt loads correctly:
   ```bash
   python -c "from datasheets.coral.fish_census.v1.prompt import PROMPT; print(PROMPT[:100])"
   ```

### Reporting Issues

Include:
1. Exact error message
2. Command you ran
3. Python version (`python --version`)
4. Operating system
5. Sample image (if possible)

### Quick Diagnostics

```bash
# Check Python
python --version

# Check anthropic package
pip show anthropic

# Check API key is set
echo $ANTHROPIC_API_KEY | head -c 20

# Test API connection
python -c "import anthropic; c = anthropic.Anthropic(); print('Connected!')"

# Check prompt loads
python -c "from datasheets.coral.fish_census.v1.prompt import PROMPT; print('Loaded!')"
```

## Model Comparison

| Issue | Try Sonnet First | Use Opus |
|-------|------------------|----------|
| Simple, clear datasheets | ✅ | Overkill |
| Messy handwriting | Try first | If errors |
| Complex layouts | Try first | If errors |
| Critical/legal data | ❌ | ✅ |
| Bulk processing | ✅ | Too expensive |
| Accuracy issues | Debug prompt | Last resort |
