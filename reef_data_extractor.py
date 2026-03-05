#!/usr/bin/env python3
"""
SHAMS Reef Survey Data Sheet Extractor - Cloud API Version
Extracts structured data from photographed field datasheets using AI vision APIs.

============================================================================
HOW THIS WORKS - ONE SCRIPT, MANY DATASHEET TYPES
============================================================================

This is a single generic script. It doesn't know anything about fish surveys
or coral condition or invertebrates — all that knowledge lives in PROMPT FILES.

The architecture:

    reef_data_extractor.py          <-- this script (generic, rarely changes)
    prompts/
        fish_transect_survey_v1.1.txt       <-- knows fish datasheet layout
        coral_condition_v1.1   <-- knows coral datasheet layout
        ...

When you run the script, you tell it which datasheet type you're processing:

    python reef_data_extractor.py image.jpeg --type fish_survey

The script looks up "fish_survey" in PROMPT_FILES (below), finds the matching
.txt file in the prompts/ folder, loads that prompt, and sends it alongside
the image to the AI API. The prompt teaches the AI how to read THAT specific
layout — what species to expect, how columns are arranged, how to handle tally
marks, and what JSON structure to return.

TO ADD A NEW DATASHEET TYPE:
  1. Write a new prompt .txt in prompts/ (copy an existing one as template)
  2. Add one line to the PROMPT_FILES dict below
  3. That's it — run with --type <your_new_type>

============================================================================

Environment variables:
    ANTHROPIC_API_KEY  - Required for Claude provider (default)
    OPENAI_API_KEY     - Required for OpenAI provider
"""

import json
import os
import sys
import csv
import base64
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

try:
    from PIL import Image
except ImportError as e:
    print(f"Missing required package: {e}")
    print("  pip install pillow anthropic --break-system-packages")
    sys.exit(1)


# ---------------------------------------------------------------------------
# PROMPT ROUTING — add new datasheet types here
# ---------------------------------------------------------------------------

PROMPT_DIR = Path(__file__).parent / "prompts"

PROMPT_FILES = {
    "fish_survey_v1.1":      "fish_transect_survey_v1.1",
    "coral_condition_v1.1":  "coral_condition_v1.1",
}


def load_prompt(datasheet_type: Optional[str] = None,
                prompt_path: Optional[str] = None) -> str:
    if prompt_path:
        p = Path(prompt_path)
        if not p.exists():
            print(f"ERROR: Prompt file not found: {prompt_path}")
            sys.exit(1)
        print(f"  Prompt: {p}")
        return p.read_text(encoding="utf-8")

    if datasheet_type and datasheet_type in PROMPT_FILES:
        p = PROMPT_DIR / PROMPT_FILES[datasheet_type]
        if p.exists():
            print(f"  Prompt: {p}")
            return p.read_text(encoding="utf-8")
        else:
            print(f"WARNING: Prompt file not found at {p}")
            print(f"  Falling back to generic prompt.\n")

    if datasheet_type and datasheet_type not in PROMPT_FILES:
        print(f"ERROR: Unknown datasheet type '{datasheet_type}'")
        print(f"  Available: {', '.join(PROMPT_FILES.keys())}")
        sys.exit(1)

    return _generic_prompt()


def _generic_prompt() -> str:
    return """Analyze this reef survey data sheet image.
Extract ALL data and return as structured JSON including:
- metadata (observer, date, site, conditions)
- table data with full species names (expand abbreviations)
- tally marks converted to integers
- confidence per row (High/Medium/Low)
Empty cells = 0. Unreadable = -1 with Low confidence.
Return ONLY the JSON object."""


# ---------------------------------------------------------------------------
# Extractor
# ---------------------------------------------------------------------------

class ReefDataExtractor:

    def __init__(self, provider="claude", api_key=None, model=None):
        self.provider = provider.lower()

        if self.provider == "claude":
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            self.model = model or "claude-sonnet-4-5-20250929"
            if not self.api_key:
                print("ERROR: Set ANTHROPIC_API_KEY environment variable.")
                sys.exit(1)
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                print("ERROR: pip install anthropic --break-system-packages")
                sys.exit(1)

        elif self.provider == "openai":
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            self.model = model or "gpt-4o"
            if not self.api_key:
                print("ERROR: Set OPENAI_API_KEY environment variable.")
                sys.exit(1)
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                print("ERROR: pip install openai --break-system-packages")
                sys.exit(1)

        elif self.provider == "ollama":
            self.model = model or "llava:34b"
            ollama_url = os.getenv("OLLAMA_URL", "http://100.85.136.83:11434")
            try:
                import openai
                self.client = openai.OpenAI(
                    base_url=f"{ollama_url}/v1",
                    api_key="unused",
                )
            except ImportError:
                print("ERROR: pip install openai --break-system-packages")
                sys.exit(1)
            print(f"  Ollama URL: {ollama_url}")

        else:
            print(f"ERROR: Unknown provider '{provider}'.")
            sys.exit(1)

        print(f"  Provider: {self.provider.upper()} ({self.model})")

    @staticmethod
    def _encode_image(path: str) -> str:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    @staticmethod
    def _media_type(path: str) -> str:
        return {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".png": "image/png", ".gif": "image/gif",
                ".webp": "image/webp"}.get(Path(path).suffix.lower(), "image/jpeg")

    def _call_api(self, image_path: str, prompt: str) -> str:
        img_b64 = self._encode_image(image_path)
        mt = self._media_type(image_path)

        if self.provider == "claude":
            msg = self.client.messages.create(
                model=self.model, max_tokens=8192,
                messages=[{"role": "user", "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": mt, "data": img_b64}},
                    {"type": "text", "text": prompt},
                ]}],
            )
            return msg.content[0].text
        else:  # openai and ollama both use OpenAI-compatible format
            resp = self.client.chat.completions.create(
                model=self.model, max_tokens=8192,
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mt};base64,{img_b64}"}},
                ]}],
            )
            return resp.choices[0].message.content

    def extract(self, image_path: str, prompt: str) -> Dict:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        print(f"\nProcessing: {Path(image_path).name}")
        print("  Calling API...", end=" ", flush=True)
        raw = self._call_api(image_path, prompt)
        print("done.")
        return {
            "extracted_data": self._parse_json(raw),
            "raw_response": raw,
            "source_image": str(image_path),
            "provider": self.provider,
            "model": self.model,
            "extracted_at": datetime.utcnow().isoformat() + "Z",
        }

    @staticmethod
    def _parse_json(text: str) -> Dict:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned[cleaned.index("\n") + 1:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
        start, end = cleaned.find("{"), cleaned.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(cleaned[start:end])
            except json.JSONDecodeError as e:
                print(f"  WARNING: JSON parse error: {e}")
                return {"raw_response": text, "parse_error": str(e)}
        print("  WARNING: No JSON found in response")
        return {"raw_response": text}

    # -- save outputs --------------------------------------------------------

    def extract_and_save(self, image_path: str, prompt: str,
                         output_dir: Optional[str] = None,
                         output_format: str = "both") -> List[str]:
        result = self.extract(image_path, prompt)
        stem = Path(image_path).stem
        out_dir = Path(output_dir) if output_dir else Path(".")
        out_dir.mkdir(parents=True, exist_ok=True)
        outputs = []

        if output_format in ("json", "both"):
            p = out_dir / f"{stem}_extracted.json"
            with open(p, "w") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            outputs.append(str(p))
            print(f"  → JSON: {p}")

        if output_format in ("csv", "both"):
            p = out_dir / f"{stem}_extracted.csv"
            self._save_csv(result, str(p))
            outputs.append(str(p))
            print(f"  → CSV:  {p}")

        return outputs

    @staticmethod
    def _save_csv(result: Dict, output_path: str):
        data = result.get("extracted_data", {})
        meta = data.get("metadata", {})
        transects = data.get("transects", [])

        if not transects:
            fb = output_path.replace(".csv", "_raw.json")
            with open(fb, "w") as f:
                json.dump(result, f, indent=2)
            print(f"  WARNING: No transect structure; saved raw JSON to {fb}")
            return

        rows = []
        for t in transects:
            tn = t.get("transect_number", "")
            mc = {
                "site_code": meta.get("site_code", ""),
                "date": meta.get("date", ""),
                "time": meta.get("time", ""),
                "observer": meta.get("observer_name", ""),
                "depth_m": meta.get("exact_depth_m", ""),
                "water_temp_c": meta.get("water_temp_c", ""),
                "visibility_m": meta.get("visibility_m", ""),
                "sea_state": meta.get("sea_state", ""),
                "wave_exposure": meta.get("wave_exposure", ""),
                "reef_zone": meta.get("reef_zone", ""),
                "transect": tn,
            }
            for e in t.get("herbivores_and_commercial", []):
                rows.append({**mc,
                    "data_table": "herbivores_commercial",
                    "family": e.get("family", ""),
                    "species": e.get("species", ""),
                    "lt_10cm": e.get("size_lt_10cm", 0),
                    "11_20cm": e.get("size_11_20cm", 0),
                    "21_30cm": e.get("size_21_30cm", 0),
                    "31_40cm": e.get("size_31_40cm", 0),
                    "41_50cm": e.get("size_41_50cm", 0),
                    "50plus_cm": e.get("size_50plus_cm", 0),
                    "count_all_sizes": "",
                    "confidence": e.get("confidence", ""),
                })
            for e in t.get("coral_dependent", []):
                rows.append({**mc,
                    "data_table": "coral_dependent",
                    "family": e.get("family", ""),
                    "species": e.get("species", ""),
                    "lt_10cm": "", "11_20cm": "", "21_30cm": "",
                    "31_40cm": "", "41_50cm": "", "50plus_cm": "",
                    "count_all_sizes": e.get("count_all_sizes", 0),
                    "confidence": e.get("confidence", ""),
                })
            for e in t.get("incidental_sightings", []):
                rows.append({**mc,
                    "data_table": "incidental",
                    "family": "",
                    "species": e.get("species", ""),
                    "lt_10cm": "", "11_20cm": "", "21_30cm": "",
                    "31_40cm": "", "41_50cm": "", "50plus_cm": "",
                    "count_all_sizes": e.get("count", 0),
                    "confidence": e.get("confidence", ""),
                })

        if rows:
            with open(output_path, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Extract reef survey data from scanned datasheets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s image.jpeg --type fish_survey
  %(prog)s image.jpeg --type coral_condition -f csv
  %(prog)s image.jpeg --prompt prompts/my_test.txt
  %(prog)s image.jpeg --type fish_survey --provider openai
  %(prog)s image.jpeg --type fish_survey -p ollama -m llava:34b

Batch:
  for img in images/Fish/*.jpeg; do
      %(prog)s "$img" --type fish_survey -o outputs/
  done
        """,
    )
    parser.add_argument("image_path")
    parser.add_argument("-t", "--type", dest="datasheet_type",
                        choices=list(PROMPT_FILES.keys()))
    parser.add_argument("--prompt", dest="prompt_path",
                        help="Custom prompt file (overrides --type)")
    parser.add_argument("-o", "--output-dir", default=".")
    parser.add_argument("-f", "--format", choices=["json", "csv", "both"],
                        default="both")
    parser.add_argument("-p", "--provider", choices=["claude", "openai", "ollama"],
                        default="claude")
    parser.add_argument("-m", "--model")
    parser.add_argument("-k", "--api-key", dest="api_key")

    args = parser.parse_args()

    if not args.datasheet_type and not args.prompt_path:
        print("ERROR: Specify --type or --prompt")
        print(f"  Available types: {', '.join(PROMPT_FILES.keys())}")
        sys.exit(1)

    print("=" * 60)
    print("SHAMS Reef Survey Data Extractor")
    print("=" * 60)

    prompt = load_prompt(args.datasheet_type, args.prompt_path)
    extractor = ReefDataExtractor(args.provider, args.api_key, args.model)
    outputs = extractor.extract_and_save(
        args.image_path, prompt, args.output_dir, args.format)

    print(f"\n{'=' * 60}")
    print("Done.")
    print("=" * 60)


if __name__ == "__main__":
    main()
