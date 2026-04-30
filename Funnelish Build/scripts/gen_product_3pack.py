#!/usr/bin/env python3
"""
Generate a clean 3-pack {product} product render for the 3-month pricing card.
Uses fal nano-banana-pro/edit with the existing product catalog shot as a reference
so the packaging stays visually consistent with the 1-month card.
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

import os, sys
from pathlib import Path
import requests
import fal_client
from dotenv import load_dotenv

ROOT = Path("/Users/jaymilne/A/Workspace/Client Work/LiverZen/Funnelish Build")
OUT = ROOT / "Pages" / "images" / "product"
REF_IMAGE = ROOT / "Pages" / "images" / "product" / "{product_catalog}.png"  # TODO: provide your catalog reference shot

for env_path in [Path("/Users/jaymilne/A/Adgentiks/outreach-agent/.env"), Path("/Users/jaymilne/A/.env")]:
    if env_path.exists():
        load_dotenv(env_path)
        break

FAL_KEY = os.getenv("FAL_KEY")
if not FAL_KEY:
    print("ERROR: FAL_KEY not found"); sys.exit(1)
os.environ["FAL_KEY"] = FAL_KEY

PROMPT = (
    "Hero product photography of THREE identical {product} boxes (the white box "
    "with the navy R logo and '{product}' label) arranged in a clean trio — one "
    "in front, two slightly behind on either side — on a pure white seamless "
    "background with a soft shadow underneath. Same camera angle, same lighting, "
    "same box scale-in-frame as the reference 1-box shot. No additional props, "
    "no ingredients scattered around. Just the three boxes, clean, centered, "
    "premium e-commerce hero shot. Subtle cream gradient background. 1:1 square."
)


def upload_ref() -> str:
    print(f"Uploading reference: {REF_IMAGE}")
    url = fal_client.upload_file(str(REF_IMAGE))
    print(f"  → {url}")
    return url


def main():
    ref_url = upload_ref()
    print("\nGenerating 3-pack ...")
    result = fal_client.subscribe(
        "fal-ai/nano-banana-pro/edit",
        arguments={
            "prompt": PROMPT,
            "image_urls": [ref_url],
            "aspect_ratio": "1:1",
            "num_images": 1,
            "output_format": "png",
        },
    )
    images = result.get("images") or []
    if not images:
        print(f"FAIL: {result}"); sys.exit(1)
    url = images[0]["url"]
    print(f"  → {url}")
    dest = OUT / "pricing_3pack.png"
    r = requests.get(url, timeout=60); r.raise_for_status()
    dest.write_bytes(r.content)
    print(f"saved: {dest}")


if __name__ == "__main__":
    main()
