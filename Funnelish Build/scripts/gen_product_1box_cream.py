#!/usr/bin/env python3
"""
Render a single {product} box on the same cream background + lighting as
the 3-pack (nf_product_3pack.png), so the 1-month and 3-month pricing cards
read as a consistent tier system.
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
REF_IMAGE = ROOT / "v2-images" / "product" / "pricing_3pack.png"

for env_path in [Path("/Users/jaymilne/A/Adgentiks/outreach-agent/.env"), Path("/Users/jaymilne/A/.env")]:
    if env_path.exists():
        load_dotenv(env_path)
        break

FAL_KEY = os.getenv("FAL_KEY")
if not FAL_KEY:
    print("ERROR: FAL_KEY not found"); sys.exit(1)
os.environ["FAL_KEY"] = FAL_KEY

PROMPT = (
    "Hero product photography of a SINGLE {product} box (the white box with the "
    "navy R logo and '{product}' label), centered, on the same soft cream "
    "background as the reference image. Same camera angle, same soft lighting, "
    "same subtle shadow underneath, same scale-in-frame as one of the boxes in "
    "the reference trio. No additional props, no ingredients. Clean premium "
    "e-commerce hero shot. 1:1 square."
)


def main():
    print(f"Uploading reference: {REF_IMAGE}")
    ref_url = fal_client.upload_file(str(REF_IMAGE))
    print(f"  → {ref_url}")
    print("\nGenerating 1-box-on-cream ...")
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
    dest = OUT / "nf_product_1box_cream.png"
    r = requests.get(url, timeout=60); r.raise_for_status()
    dest.write_bytes(r.content)
    print(f"saved: {dest}")


if __name__ == "__main__":
    main()
