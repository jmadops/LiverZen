#!/usr/bin/env python3
"""
Generate 6 POV / lifestyle photos for the 3 "Highest Rated (With Photos)" review
cards in template.html. Two photos per card, matched to the card's narrative.

We pass nf_product_1box_cream.png as the reference image so the generated scenes
show the correct {brand} coffee box (cream/navy label) rather than an invented
product. Style target: real iPhone photo — not product photography.

Output: /v2-images/social/nf_review_photo_01.png ... nf_review_photo_06.png
        (mirrored to /{brand} Pages/v2-images/social/)
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

import os
import sys
from pathlib import Path
import requests
import fal_client
from dotenv import load_dotenv

ROOT = Path("/Users/jaymilne/A/Workspace/Client Work/LiverZen/Funnelish Build")
OUT = ROOT / "Pages" / "images" / "social"
REF_BOX = ROOT / "v2-images" / "product" / "nf_product_1box_cream.png"

for env_path in [
    Path("/Users/jaymilne/A/Adgentiks/outreach-agent/.output"),
    Path("/Users/jaymilne/A/Adgentiks/outreach-agent/.env"),
    Path("/Users/jaymilne/A/.env"),
]:
    if env_path.exists():
        load_dotenv(env_path)
        break

FAL_KEY = os.getenv("FAL_KEY")
if not FAL_KEY:
    print("ERROR: FAL_KEY not found")
    sys.exit(1)
os.environ["FAL_KEY"] = FAL_KEY

if not REF_BOX.exists():
    print(f"ERROR: reference box image missing at {REF_BOX}")
    sys.exit(1)

BASE_STYLE = (
    "Casual iPhone photo aesthetic — not product photography. Natural morning "
    "window light, slightly imperfect framing, shallow depth of field only where "
    "a real phone would produce it, subtle sensor grain. Warm neutral tones, "
    "cream / beige / soft gold. The {brand} coffee box in the frame must match "
    "the reference image exactly — same cream/navy label, same proportions, "
    "same product. No text overlays, no logos beyond what the box itself shows, "
    "no watermarks. 1:1 square crop."
)

# 6 scenes: 2 per review card (Carol, James, Patricia)
SCENES = [
    # Carol W. — twelve weeks, buttoned her own shirt
    ("nf_review_photo_01",
     "Overhead POV of a simple white kitchen counter in soft morning light. "
     "A cream ceramic coffee mug with steam rising, the {brand} coffee box "
     "(matching the reference) placed to the right of the mug, a folded "
     "newspaper corner visible at the edge. Warm, domestic, unposed."),
    ("nf_review_photo_02",
     "Over-the-shoulder angle of an older woman (early 70s, soft white hair) "
     "in a cream cardigan at a breakfast nook, holding a coffee mug with both "
     "hands, looking out a sunlit window. The {brand} coffee box sits on the "
     "wooden table in front of her. Back-lit, warm, iPhone candid feel. "
     "Her face is mostly turned away — this is a lifestyle shot, not a portrait."),

    # James P. — caregiver, dad walked to the mailbox
    ("nf_review_photo_03",
     "Kitchen counter shot: the {brand} coffee box (matching reference) next "
     "to a glass French press and a handwritten grocery list on lined paper. "
     "Morning sun streaming through a window behind. Very domestic, slightly "
     "cluttered in the homey way a real kitchen is. Not staged."),
    ("nf_review_photo_04",
     "POV hand reaching for a dark ceramic mug on a wooden table. The {brand} "
     "coffee box (matching reference) visible in the background, slightly "
     "out of focus. Also in the background: the edge of a walking cane leaning "
     "against a chair. iPhone photo, morning light."),

    # Patricia L. — handwriting came back
    ("nf_review_photo_05",
     "A handwritten birthday card in neat cursive on cream paper, placed on a "
     "wooden table next to a coffee mug and the {brand} coffee box (matching "
     "reference). A fountain pen rests on top of the card. Soft overhead light, "
     "real-life moment, not styled."),
    ("nf_review_photo_06",
     "Flatlay from above: the {brand} coffee box (matching reference) centered, "
     "a small open recovery journal with handwritten notes to its left, a mug "
     "of black coffee to its right, a pair of reading glasses folded at the top "
     "of the frame. Soft morning shadow across the wood grain. Warm tones."),
]

ASPECT = "1:1"


def generate_one(stem: str, scene: str, ref_url: str):
    prompt = scene + " " + BASE_STYLE
    print(f"\n[{stem}]")
    print(f"  scene: {scene[:90]}...")
    result = fal_client.subscribe(
        "fal-ai/nano-banana-pro/edit",
        arguments={
            "prompt": prompt,
            "image_urls": [ref_url],
            "aspect_ratio": ASPECT,
            "num_images": 1,
            "output_format": "png",
        },
    )
    images = result.get("images") or []
    if not images:
        print(f"  FAIL: {result}")
        return False
    url = images[0]["url"]
    print(f"  url: {url}")
    dest = OUT / f"{stem}.png"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(r.content)
    print(f"  saved: {dest}")
    return True


def main():
    print(f"Uploading reference box: {REF_BOX}")
    ref_url = fal_client.upload_file(str(REF_BOX))
    print(f"  → {ref_url}")

    print(f"\nGenerating {len(SCENES)} review POV photos")
    ok = 0
    for stem, scene in SCENES:
        if generate_one(stem, scene, ref_url):
            ok += 1
    print(f"\nDone: {ok}/{len(SCENES)} generated")


if __name__ == "__main__":
    main()
