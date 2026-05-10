#!/usr/bin/env python3
"""
Generate the four PDP-specific FR images that the existing
assets/generated-fr/ set is missing:

  fr-founder-portrait.webp   Dr Lefèvre, mid-50s French hepatologist,
                              lifestyle shot in his clinic office (square)
  fr-founder-holding.webp    Dr Lefèvre holding the LiverZen bottle (4:5)
  fr-pricing-3pack.webp      Editorial render of 3 LiverZen bottles
                              for the 3-month bundle pricing card (4:3)
  fr-howto-routine.webp      Hand taking a capsule with a glass of water,
                              French kitchen morning routine (1:1)

Uses fal-ai/nano-banana-pro/edit (same model as gen_fr_product_images.py)
with the LiverZen bottle reference so likeness is preserved.
"""
from __future__ import annotations

import os
import sys
from io import BytesIO
from pathlib import Path

import fal_client
import requests
from dotenv import load_dotenv
from PIL import Image

ROOT = Path("/Users/jaymilne/A/Workspace/Client Work/LiverZen")
REF_BOTTLE = ROOT / "1768871742-LiverZen (1).webp"
OUT_DIR = ROOT / "assets" / "generated-fr"

for env_path in [
    Path("/Users/jaymilne/A/.env"),
    Path("/Users/jaymilne/A/Adgentiks/outreach-agent/.env"),
]:
    if env_path.exists():
        load_dotenv(env_path)
        break

if not os.getenv("FAL_KEY"):
    print("ERROR: FAL_KEY not found in env"); sys.exit(1)


JOBS = [
    {
        "filename": "fr-founder-portrait.webp",
        "aspect_ratio": "1:1",
        "use_ref": False,
        "prompt": (
            "Editorial portrait of Dr Lefèvre, a French hepatologist in his "
            "mid-50s, sitting at his desk in a calm modern Parisian medical "
            "office. Salt-and-pepper hair, trimmed beard, kind grey-blue "
            "eyes, light-blue dress shirt with the top button undone, white "
            "doctor's coat draped over the back of his chair. Behind him: a "
            "wall of medical reference books, framed diplomas (text "
            "illegible, just visible as warm beige rectangles), a soft "
            "anatomical poster of the human liver. Soft window daylight from "
            "the side. Looking just past camera with a calm, attentive "
            "expression — the kind of doctor patients trust. Photo-realistic, "
            "shot on a 50mm lens, shallow depth of field but face fully "
            "sharp. No text overlay, no name plates, no logos."
        ),
    },
    {
        "filename": "fr-founder-holding.webp",
        "aspect_ratio": "4:5",
        "use_ref": True,
        "prompt": (
            "Editorial portrait of Dr Lefèvre, a French hepatologist in his "
            "mid-50s, standing in his Parisian clinic office holding the "
            "LiverZen bottle from the reference image — match the bottle "
            "exactly, do not redesign the label. He holds the bottle "
            "label-forward at chest height with both hands, cradling it like "
            "something he believes in. Salt-and-pepper hair, trimmed beard, "
            "kind grey-blue eyes, light-blue dress shirt under an open white "
            "doctor's coat. Background: softly blurred clinic — bookshelf, "
            "framed diplomas, anatomical liver poster, tasteful wood "
            "paneling. Warm window light from the left. Calm, slightly warm "
            "smile. Photo-realistic, editorial, shot on 50mm. The bottle "
            "label and the doctor's face are both in sharp focus. No text "
            "overlay. No props beyond the bottle."
        ),
    },
    {
        "filename": "fr-pricing-3pack.webp",
        "aspect_ratio": "4:3",
        "use_ref": True,
        "prompt": (
            "Editorial e-commerce pack shot of three identical LiverZen "
            "bottles from the reference image, arranged in a clean staggered "
            "row on a soft white-to-pale-grey gradient background. Match the "
            "reference bottle exactly: white slim cylindrical body, white "
            "cap, green LiverZen wordmark, 'SOUTIEN DU FOIE' text on a green "
            "panel. Front bottle is centered and label-forward, the two "
            "behind it are angled slightly to the left and right, partially "
            "visible. Soft studio lighting, gentle natural shadow under each "
            "bottle. Premium clean composition — the kind of pack shot a "
            "French health-supplement brand would put on its 3-month bundle "
            "card. No text overlay. No price stickers. No props. Just the "
            "three bottles."
        ),
    },
    {
        "filename": "fr-howto-routine.webp",
        "aspect_ratio": "1:1",
        "use_ref": True,
        "prompt": (
            "Hyper-realistic close-up of a 50-something French woman's hand "
            "(visible wedding ring, light age spots, no manicure, just real "
            "skin) holding two small white capsules in her palm above a "
            "marble French kitchen counter. Beside her hand on the counter: "
            "a clear glass of water and the LiverZen bottle from the "
            "reference image, cap off, label visible — match the reference "
            "bottle exactly. Soft morning daylight from a window on the "
            "left. Background: softly blurred French country kitchen — a "
            "wooden cutting board, a sprig of fresh thyme, a small espresso "
            "cup. Composition feels candid, like someone snapped this on "
            "their phone during their morning routine. No text overlay, no "
            "captions."
        ),
    },
]


def webp_save(png_url: str, dest: Path) -> None:
    r = requests.get(png_url, timeout=180)
    r.raise_for_status()
    img = Image.open(BytesIO(r.content)).convert("RGB")
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "WEBP", quality=88, method=6)
    size_kb = dest.stat().st_size // 1024
    print(f"  saved: {dest.relative_to(ROOT)} ({size_kb} KB)")


def main() -> None:
    print(f"Uploading reference bottle: {REF_BOTTLE.name}")
    ref_url = fal_client.upload_file(str(REF_BOTTLE))
    print(f"  -> {ref_url}\n")

    for job in JOBS:
        dest = OUT_DIR / job["filename"]
        if dest.exists() and dest.stat().st_size > 50_000:
            print(f"SKIP existing: {dest.name}")
            continue
        endpoint = (
            "fal-ai/nano-banana-pro/edit" if job["use_ref"] else "fal-ai/nano-banana-pro"
        )
        args = {
            "prompt": job["prompt"],
            "aspect_ratio": job["aspect_ratio"],
            "num_images": 1,
            "output_format": "png",
        }
        if job["use_ref"]:
            args["image_urls"] = [ref_url]
        print(f"Generating {job['filename']} ({job['aspect_ratio']}) via {endpoint} …")
        try:
            result = fal_client.subscribe(endpoint, arguments=args)
        except Exception as e:
            print(f"  FAIL: {e}")
            continue
        images = result.get("images") or []
        if not images:
            print(f"  FAIL: no images returned: {result}")
            continue
        webp_save(images[0]["url"], dest)
        print()


if __name__ == "__main__":
    main()
