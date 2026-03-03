#!/usr/bin/env python3
"""
SHAMS Reef Survey Data Sheet Extractor - Cloud API Version
Supports Claude (Anthropic) and OpenAI GPT-4 Vision APIs.

Loads extraction prompts from external .txt files so the team can iterate
on them independently via GitHub without touching this script.

Usage:
    # Extract a fish survey datasheet
    python reef_data_extractor.py path/to/image.jpeg --type fish_survey

    # Extract a coral condition datasheet
    python reef_data_extractor.py path/to/image.jpeg --type coral_condition

    # Use a custom prompt file
    python reef_data_extractor.py path/to/image.jpeg --prompt path/to/prompt.txt

    # Output as CSV
    python reef_data_extractor.py path/to/image.jpeg --type fish_survey -f csv

Environment variables:
    ANTHROPIC_API_KEY - Required for Claude provider (default)
    OPENAI_API_KEY    - Required for OpenAI provider
"""

import json
import os
import sys
import csv
import base64
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

try:
    import requests
    from PIL import Image
except ImportError as e:
    print(f"Missing required package: {e}")
    print("\nPlease install required packages:")
    print("  pip install requests pillow anthropic openai --break-system-packages")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Prompt loading
# ---------------------------------------------------------------------------

# Default directory for prompt files (relative to this script)
PROMPT_DIR = Path(__file__).parent / "prompts"

# Mapping of datasheet type keywords to prompt filenames
PROMPT_FILES = {
    "fish_survey": "fish_survey_extraction_prompt.txt",
    "coral_condition": "coral_condition_extraction_prompt.txt",
    # Add new datasheet types here as prompts are developed:
    # "invertebrate_survey": "invertebrate_survey_extraction_prompt.txt",
    # "benthic_cover": "benthic_cover_extraction_prompt.txt",
}


def load_prompt(datasheet_type: Optional[str] = None,
                prompt_path: Optional[str] = None) -> str:
    """
    Load an extraction prompt from file.

    Priority:
      1. Explicit prompt_path if given
      2. Prompt file matching datasheet_type from PROMPT_DIR
      3. Fallback generic prompt (minimal)

    Returns the prompt text as a string.
    """
    # Option 1: explicit path
    if prompt_path:
        p = Path(prompt_path)
        if not p.exists():
            print(f"ERROR: Prompt file not found: {prompt_path}")
            sys.exit(1)
        print(f"✓ Loaded prompt from: {p}")
        return p.read_text(encoding="utf-8")

    # Option 2: lookup by datasheet type
    if datasheet_type and datasheet_type in PROMPT_FILES:
        p = PROMPT_DIR / PROMPT_FILES[datasheet_type]
        if p.exists():
            print(f"✓ Loaded prompt for '{datasheet_type}' from: {p}")
            return p.read_text(encoding="utf-8")
        else:
            print(f"WARNING: Prompt file for '{datasheet_type}' not found at {p}")
            print(f"  Expected: {p}")
            print(f"  Available types: {', '.join(PROMPT_FILES.keys())}")
            print(f"  Falling back to generic prompt.\n")

    # Option 3: generic fallback
    return _generic_prompt()


def _generic_prompt() -> str:
    """Minimal generic prompt for unknown datasheet types."""
    return """Analyze this reef survey data sheet image.
Extract ALL data from the sheet and return it as a structured JSON object.

Include:
- Any metadata (observer, date, site, conditions)
- All table data with species names expanded (no abbreviations)
- Tally mark counts converted to integers
- A confidence score for each row (High/Medium/Low)

For empty cells, use 0. For unreadable cells, use -1 with Low confidence.
Return ONLY the JSON object, no other text."""


# ---------------------------------------------------------------------------
# Extractor class
# ---------------------------------------------------------------------------

class ReefDataExtractor:
    """Extract structured data from reef survey data sheets using cloud AI APIs."""

    def __init__(
        self,
        provider: str = "claude",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.provider = provider.lower()

        if self.provider == "claude":
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            self.model = model or "claude-sonnet-4-5-20250929"
            if not self.api_key:
                print("ERROR: Anthropic API key required!")
                print("Set the ANTHROPIC_API_KEY environment variable.")
                print("Get your key at: https://console.anthropic.com/")
                sys.exit(1)
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                print("ERROR: anthropic package not installed")
                print("  pip install anthropic --break-system-packages")
                sys.exit(1)

        elif self.provider == "openai":
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            self.model = model or "gpt-4o"
            if not self.api_key:
                print("ERROR: OpenAI API key required!")
                print("Set the OPENAI_API_KEY environment variable.")
                sys.exit(1)
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                print("ERROR: openai package not installed")
                print("  pip install openai --break-system-packages")
                sys.exit(1)

        else:
            print(f"ERROR: Unknown provider '{provider}'")
            print("Supported: 'claude', 'openai'")
            sys.exit(1)

        print(f"✓ Using {self.provider.upper()} API — model: {self.model}")

    # -- image helpers -------------------------------------------------------

    @staticmethod
    def _encode_image(image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    @staticmethod
    def _media_type(image_path: str) -> str:
        ext = Path(image_path).suffix.lower()
        return {
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png", ".gif": "image/gif",
            ".webp": "image/webp",
        }.get(ext, "image/jpeg")

    # -- API calls -----------------------------------------------------------

    def _call_claude(self, image_path: str, prompt: str) -> str:
        data = self._encode_image(image_path)
        msg = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {
                        "type": "base64",
                        "media_type": self._media_type(image_path),
                        "data": data}},
                    {"type": "text", "text": prompt},
                ],
            }],
        )
        return msg.content[0].text

    def _call_openai(self, image_path: str, prompt: str) -> str:
        data = self._encode_image(image_path)
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {
                        "url": f"data:{self._media_type(image_path)};base64,{data}"}},
                ],
            }],
            max_tokens=8192,
        )
        return resp.choices[0].message.content

    # -- extraction ----------------------------------------------------------

    def extract(self, image_path: str, prompt: str) -> Dict:
        """Run extraction and return parsed results."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        print(f"Processing: {image_path}")
        print("Sending to API...")

        raw = (self._call_claude if self.provider == "claude"
               else self._call_openai)(image_path, prompt)

        # Parse JSON from response (handle markdown fences etc.)
        parsed = self._parse_json(raw)

        return {
            "extracted_data": parsed,
            "raw_response": raw,
            "image_path": str(image_path),
            "provider": self.provider,
            "model": self.model,
            "extracted_at": datetime.utcnow().isoformat() + "Z",
        }

    @staticmethod
    def _parse_json(text: str) -> Dict:
        """Extract JSON object from model response text."""
        # Strip markdown code fences if present
        cleaned = text.strip()
        if cleaned.startswith("```"):
            # Remove opening fence (with optional language tag)
            first_nl = cleaned.index("\n")
            cleaned = cleaned[first_nl + 1:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        # Find JSON object boundaries
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(cleaned[start:end])
            except json.JSONDecodeError as e:
                print(f"WARNING: JSON parse error: {e}")
                return {"raw_response": text, "parse_error": str(e)}
        else:
            print("WARNING: No JSON object found in response")
            return {"raw_response": text}

    # -- save ----------------------------------------------------------------

    def extract_and_save(
        self,
        image_path: str,
        prompt: str,
        output_path: Optional[str] = None,
        output_format: str = "json",
    ) -> str:
        result = self.extract(image_path, prompt)

        if output_path is None:
            stem = Path(image_path).stem
            output_path = f"{stem}_extracted.{output_format}"

        if output_format == "json":
            with open(output_path, "w") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

        elif output_format == "csv":
            self._save_csv(result, output_path)

        print(f"✓ Saved to: {output_path}")
        return output_path

    @staticmethod
    def _save_csv(result: Dict, output_path: str):
        """Flatten fish survey JSON into a CSV file."""
        data = result.get("extracted_data", {})
        meta = data.get("metadata", {})
        transects = data.get("transects", [])

        if not transects:
            # Fallback: just dump JSON
            fallback = output_path.replace(".csv", ".json")
            with open(fallback, "w") as f:
                json.dump(result, f, indent=2)
            print(f"WARNING: No transect data found; saved JSON to {fallback}")
            return

        rows = []
        for t in transects:
            tn = t.get("transect_number", "")
            # Herbivores & commercial
            for entry in t.get("herbivores_and_commercial", []):
                rows.append({
                    "site_code": meta.get("site_code", ""),
                    "date": meta.get("date", ""),
                    "observer": meta.get("observer_name", ""),
                    "transect": tn,
                    "table": "herbivores_and_commercial",
                    "family": entry.get("family", ""),
                    "species": entry.get("species", ""),
                    "lt_10cm": entry.get("size_lt_10cm", 0),
                    "11_20cm": entry.get("size_11_20cm", 0),
                    "21_30cm": entry.get("size_21_30cm", 0),
                    "31_40cm": entry.get("size_31_40cm", 0),
                    "41_50cm": entry.get("size_41_50cm", 0),
                    "50plus_cm": entry.get("size_50plus_cm", 0),
                    "count_all_sizes": "",
                    "confidence": entry.get("confidence", ""),
                })
            # Coral dependent
            for entry in t.get("coral_dependent", []):
                rows.append({
                    "site_code": meta.get("site_code", ""),
                    "date": meta.get("date", ""),
                    "observer": meta.get("observer_name", ""),
                    "transect": tn,
                    "table": "coral_dependent",
                    "family": entry.get("family", ""),
                    "species": entry.get("species", ""),
                    "lt_10cm": "",
                    "11_20cm": "",
                    "21_30cm": "",
                    "31_40cm": "",
                    "41_50cm": "",
                    "50plus_cm": "",
                    "count_all_sizes": entry.get("count_all_sizes", 0),
                    "confidence": entry.get("confidence", ""),
                })
            # Incidentals
            for entry in t.get("incidental_sightings", []):
                rows.append({
                    "site_code": meta.get("site_code", ""),
                    "date": meta.get("date", ""),
                    "observer": meta.get("observer_name", ""),
                    "transect": tn,
                    "table": "incidental",
                    "family": "",
                    "species": entry.get("species", ""),
                    "lt_10cm": "",
                    "11_20cm": "",
                    "21_30cm": "",
                    "31_40cm": "",
                    "41_50cm": "",
                    "50plus_cm": "",
                    "count_all_sizes": entry.get("count", 0),
                    "confidence": entry.get("confidence", ""),
                })

        if rows:
            fieldnames = list(rows[0].keys())
            with open(output_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        else:
            print("WARNING: No rows to write")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract reef survey data from scanned datasheets using AI vision APIs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s image.jpeg --type fish_survey
  %(prog)s image.jpeg --type fish_survey -f csv
  %(prog)s image.jpeg --prompt custom_prompt.txt
  %(prog)s image.jpeg --type coral_condition --provider openai
        """,
    )
    parser.add_argument("image_path", help="Path to the scanned datasheet image")
    parser.add_argument("-t", "--type", dest="datasheet_type",
                        choices=list(PROMPT_FILES.keys()),
                        help="Datasheet type (loads matching prompt file)")
    parser.add_argument("--prompt", dest="prompt_path",
                        help="Path to a custom prompt .txt file (overrides --type)")
    parser.add_argument("-o", "--output", help="Output file path (auto-generated if omitted)")
    parser.add_argument("-f", "--format", choices=["json", "csv"], default="json",
                        help="Output format (default: json)")
    parser.add_argument("-p", "--provider", choices=["claude", "openai"], default="claude",
                        help="AI provider (default: claude)")
    parser.add_argument("-m", "--model", help="Specific model override")
    parser.add_argument("-k", "--api-key", dest="api_key",
                        help="API key (prefer env vars ANTHROPIC_API_KEY / OPENAI_API_KEY)")

    args = parser.parse_args()

    # Load prompt
    prompt = load_prompt(
        datasheet_type=args.datasheet_type,
        prompt_path=args.prompt_path,
    )

    # Init extractor
    extractor = ReefDataExtractor(
        provider=args.provider,
        api_key=args.api_key,
        model=args.model,
    )

    # Run
    output_file = extractor.extract_and_save(
        image_path=args.image_path,
        prompt=prompt,
        output_path=args.output,
        output_format=args.format,
    )

    print(f"\n{'='*60}")
    print(f"Extraction complete → {output_file}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
