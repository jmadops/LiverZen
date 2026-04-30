#!/usr/bin/env python3
"""
Generate 4 circular {product} Promise icons via fal.ai (Nano Banana Pro).
{brand}-style: navy + gold on cream, cohesive vector feel, 1:1.
Saves into Pages/images/decor/.
"""
#
# ── EDIT BEFORE RUNNING ────────────────────────────────────────────────
#   1. PROMPT / STYLE / PROFILES below contain {brand}, {product},
#      {key_ingredient}, {brand_primary} placeholders -- replace with
#      LiverZen specifics.
#   2. Reference image paths marked TODO: provide your own.
#   3. Output filenames already match the {{IMG_*}} token slots used by
#      Pages/template.html.
# ───────────────────────────────────────────────────────────────────────

import os, sys, argparse
from pathlib import Path
import requests
import fal_client
from dotenv import load_dotenv

ROOT = Path("/Users/jaymilne/A/Workspace/Client Work/LiverZen/Funnelish Build")
OUT = ROOT / "Pages" / "images" / "decor"

for env_path in [Path("/Users/jaymilne/A/Adgentiks/outreach-agent/.env"), Path("/Users/jaymilne/A/.env")]:
    if env_path.exists():
        load_dotenv(env_path)
        break

FAL_KEY = os.getenv("FAL_KEY")
if not FAL_KEY:
    print("ERROR: FAL_KEY not found"); sys.exit(1)
os.environ["FAL_KEY"] = FAL_KEY

STYLE = (
    "Circular badge/emblem composition on a soft cream background (#F5EFE4) "
    "with a subtle gold inner ring frame. Strict palette: deep {brand_primary} ({brand_primary_hex}) "
    "for the main shape, warm {brand_accent} ({brand_accent_hex}) for accents, muted {brand_secondary} as a "
    "secondary. Thin consistent line art with flat fill, editorial health-brand "
    "feel, {reference_brand_quality} quality, {brand} brand tone. No text, no letters, "
    "no borders beyond the subtle gold ring. Centered, symmetrical, emblem-like. "
    "Square 1:1 aspect ratio."
)

PROMPTS = [
    ("clinical_natural",
     "A laboratory flask entwined with a single green leaf at its base, clean line-art, "
     "the flask in navy with a gold neckline and a single drop of gold inside. "
     "Represents clinically backed natural ingredients. " + STYLE),
    ("noninvasive",
     "A single gentle coffee mug silhouette in navy with soft rising steam lines in gold, "
     "symmetrical and calm, representing a non-invasive daily ritual. No needles, no pills. " + STYLE),
    ("pillfree",
     "A coffee mug in navy with a gold plus mark in the center replacing a classic pill bottle — "
     "a prescription pill bottle faintly outlined behind it being crossed out with a gold diagonal slash. " + STYLE),
    ("sideeffectfree",
     "A rounded shield emblem in navy with a bold gold checkmark at its center, "
     "small sparkle accents around it, symmetrical and protective feel. " + STYLE),
]


def download(url: str, dest: Path) -> None:
    r = requests.get(url, timeout=60); r.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(r.content)


def generate(slot: str, prompt: str) -> None:
    print(f"\n=== {slot} ===")
    result = fal_client.subscribe(
        "fal-ai/nano-banana-pro",
        arguments={
            "prompt": prompt,
            "aspect_ratio": "1:1",
            "num_images": 1,
            "output_format": "png",
        },
    )
    images = result.get("images") or []
    if not images:
        print(f"  FAIL no images: {result}"); return
    url = images[0]["url"]
    print(f"  → {url}")
    fname = f"promise_{slot}.png"
    src = OUT / fname
    download(url, src)
    print(f"  saved: {src}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+")
    args = ap.parse_args()
    targets = PROMPTS if not args.only else [p for p in PROMPTS if p[0] in args.only]
    for slot, prompt in targets:
        generate(slot, prompt)
    print("\nDone.")


if __name__ == "__main__":
    main()
