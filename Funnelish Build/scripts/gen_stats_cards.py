#!/usr/bin/env python3
"""
Generate 6 {product} stat-card illustrations via fal.ai (Nano Banana Pro, text-to-image).
Saves into Pages/images/stats/.
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
OUT = ROOT / "Pages" / "images" / "stats"

for env_path in [Path("/Users/jaymilne/A/Adgentiks/outreach-agent/.env"), Path("/Users/jaymilne/A/.env")]:
    if env_path.exists():
        load_dotenv(env_path)
        break

FAL_KEY = os.getenv("FAL_KEY")
if not FAL_KEY:
    print("ERROR: FAL_KEY not found"); sys.exit(1)
os.environ["FAL_KEY"] = FAL_KEY

STYLE = (
    "Clean modern editorial illustration, thin line art with flat fill, "
    "palette strictly: deep {brand_primary} ({brand_primary_hex}), warm {brand_accent} ({brand_accent_hex}), soft cream "
    "(#F5EFE4), muted {brand_secondary} green. Centered composition on soft cream background "
    "with subtle radial glow. No text. No borders. No photoreal elements. "
    "Editorial health-brand aesthetic like {reference_brand_quality}, {brand} tone. "
    "Square 1:1."
)

PROMPTS = [
    ("ngf", "Stylised human brain silhouette in deep navy viewed from the side, with thin gold neural pathways branching outward and upward from the cortex like growing tree roots. Small sparkle accents. " + STYLE),
    ("bbb", "Abstract cross-section of a protective cellular barrier membrane rendered as a stack of rounded capsule shapes in navy, with a single glowing gold droplet passing cleanly through the barrier leaving a trailing arrow. " + STYLE),
    ("bioav", "A minimalist human silhouette cross-section showing a gold droplet being absorbed into flowing navy bloodstream lines radiating outward. Clean diagrammatic feel. " + STYLE),
    ("adherence", "A simple 4x7 calendar grid in navy outline on cream, with 94 percent of cells filled with small gold checkmarks and a subtle glowing highlight across the filled week. " + STYLE),
    ("synergy", "A coffee bean and a {key_ingredient_lc} mushroom rendered as paired icons meeting at center, connected by a gold plus-sign that emits outward rays. Symmetrical, emblem-like composition. " + STYLE),
    ("clinical", "A hexagonal beta-glucan molecular structure in navy line-art, centered, with a small gold clinical-grade stamp badge overlapping the lower right. " + STYLE),
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
    fname = f"stats_card_{slot}.png"
    src = OUT / fname
    download(url, src)
    print(f"  saved: {src}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+", help="slot keys to generate (e.g. ngf bbb)")
    args = ap.parse_args()
    targets = PROMPTS if not args.only else [p for p in PROMPTS if p[0] in args.only]
    for slot, prompt in targets:
        generate(slot, prompt)
    print("\nDone.")


if __name__ == "__main__":
    main()
