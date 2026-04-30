#!/usr/bin/env python3
"""
Generate a tall 4:5 portrait of {founder_name} for the "Why We Built It"
founder section. Uses the existing dr_jones_email_header.png as a photo
reference so the face stays consistent across surfaces.
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
OUT = ROOT / "Pages" / "images" / "social"
REF_IMAGE = Path("/Users/jaymilne/A/Workspace/Client Work/{brand}/R Email Agent/brand_kit/generated_images/plain_text_header/dr_jones_email_header.png")

for env_path in [Path("/Users/jaymilne/A/Adgentiks/outreach-agent/.output"), Path("/Users/jaymilne/A/Adgentiks/outreach-agent/.env"), Path("/Users/jaymilne/A/.env")]:
    if env_path.exists():
        load_dotenv(env_path)
        break

FAL_KEY = os.getenv("FAL_KEY")
if not FAL_KEY:
    print("ERROR: FAL_KEY not found"); sys.exit(1)
os.environ["FAL_KEY"] = FAL_KEY

PROMPT = (
    "Professional editorial portrait of {founder_name} (the man on the right "
    "side of the reference banner) — same face, same glasses, same beard. "
    "Waist-up portrait, slight angle, warm natural light, wearing a clean white "
    "clinician coat over a casual soft blue shirt, looking thoughtfully at "
    "camera with a calm, trustworthy expression. Background: softly blurred "
    "warm neutral studio or home office (not medical facility), cream and soft "
    "gold tones. Shot on 85mm lens, shallow depth of field. No text, no logos, "
    "no overlays, no letters. Editorial health-brand feel. "
    "Portrait orientation, 4:5 aspect ratio."
)


def main():
    print(f"Uploading reference: {REF_IMAGE}")
    ref_url = fal_client.upload_file(str(REF_IMAGE))
    print(f"  → {ref_url}")
    print("\nGenerating Dr. Jones portrait ...")
    result = fal_client.subscribe(
        "fal-ai/nano-banana-pro/edit",
        arguments={
            "prompt": PROMPT,
            "image_urls": [ref_url],
            "aspect_ratio": "4:5",
            "num_images": 1,
            "output_format": "png",
        },
    )
    images = result.get("images") or []
    if not images:
        print(f"FAIL: {result}"); sys.exit(1)
    url = images[0]["url"]
    print(f"  → {url}")
    dest = OUT / "nf_founder_dr_jones.png"
    r = requests.get(url, timeout=60); r.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(r.content)
    print(f"saved: {dest}")


if __name__ == "__main__":
    main()
