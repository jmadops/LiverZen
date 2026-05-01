#!/usr/bin/env python3
"""
Regenerate:
  1. hero0-headline.png   — LiverZen-as-brand-mark headline ad (1:1)
  2. life-2-counter.png   — Replacement for the afternoon-desk lifestyle
                             (kitchen counter scene, no person, no time-of-day)
"""

import os
import sys
import time
import requests
import fal_client
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

PROJECT = Path(__file__).resolve().parent
load_dotenv(Path("/Users/jaymilne/A/.env"))
FAL_KEY = os.getenv("FAL_KEY")
if not FAL_KEY:
    sys.exit("ERROR: FAL_KEY missing")
os.environ["FAL_KEY"] = FAL_KEY

PDP_OUT = PROJECT / "assets" / "pdp"
LIFESTYLE_OUT = PROJECT / "assets" / "lifestyle"
PDP_OUT.mkdir(parents=True, exist_ok=True)
LIFESTYLE_OUT.mkdir(parents=True, exist_ok=True)

print("Uploading product reference...")
PRODUCT_URL = fal_client.upload_file(str(PROJECT / "assets" / "product.png"))
print(f"  -> {PRODUCT_URL}")

PRODUCT_RULE = (
    "USE THE PROVIDED PRODUCT REFERENCE IMAGE EXACTLY for the LiverZen "
    "bottle — preserve white body, green honeycomb pattern, label "
    "typography, proportions and silhouette. Never redesign. "
)

PROMPTS = [
    {
        "id": "hero0-headline",
        "out_dir": PDP_OUT,
        "aspect_ratio": "1:1",
        "prompt": (
            "A premium 1:1 static-ad hero image. Composition split: TOP "
            "55% is a solid deep forest green block, hex #1F4632. BOTTOM "
            "45% is a warm cream block, hex #F5EFE3, with a thin "
            "charcoal hairline rule along the join.\n"
            "TOP BLOCK: at the very top, very small all-caps cream "
            "tracked-out sans-serif eyebrow text reads exactly: \"DAILY "
            "LIVER SUPPORT\". Below that, centered, a LARGE editorial "
            "italic-friendly serif wordmark in cream off-white reads "
            "exactly: \"LiverZen\" — letterforms confidently large, "
            "this is the dominant element of the top block. Below the "
            "wordmark, centered, a thin cream horizontal rule about a "
            "third the width of the wordmark. Below that rule, a "
            "smaller editorial serif sub-headline in cream, reads "
            "exactly over two lines:\n"
            "    save your liver —\n"
            "    without quitting drinking.\n"
            "Both lines centered. Generous line-height. The "
            "sub-headline is set in italic for emphasis. Tone: calm, "
            "premium, confident, NOT clinical. NO mention of ALT, "
            "bloodwork, silymarin, percentages or numbers anywhere "
            "in the top block.\n"
            "BOTTOM BLOCK: the provided product reference image of the "
            "LiverZen bottle is centered, occupying about 75% of the "
            "block's height, label face-on. Subtle natural shadow under "
            "the bottle. To the bottom-right of the bottle, three tiny "
            "stacked benefit lines in small charcoal sans-serif:\n"
            "    ✓ Healthy liver support\n"
            "    ✓ Daily, with breakfast\n"
            "    ✓ 60-day empty-bottle refund\n"
            "Clean hierarchy. No logos other than what is on the bottle "
            "label. Premium DTC static ad, production-ready. "
            + PRODUCT_RULE
        ),
    },
    {
        "id": "life-2-counter",
        "out_dir": LIFESTYLE_OUT,
        "aspect_ratio": "9:16",
        "prompt": (
            "A vertical 9:16 hyper-realistic environmental still-life "
            "lifestyle photo. A clean, lived-in modern American kitchen "
            "counter at calm midday — soft warm sidelight from a window "
            "off-frame to the left. Centered on a butcher-block counter: "
            "the provided product reference image of the LiverZen "
            "bottle, label face-on, sharp focus. Around it: a small "
            "ceramic bowl of fresh fruit (lemons, an apple), a folded "
            "linen tea towel, an open cookbook face-down, a small clear "
            "glass with water, a single sprig of rosemary on the "
            "counter. Out-of-focus background: warm wood cabinets, a "
            "few plants on a shelf, the corner of a stovetop. Mood: "
            "the bottle lives here. Calm, real, unbranded, no person "
            "in frame, no headlines, no banners, no overlay text. Shot "
            "on iPhone 15 Pro, available natural light, shallow depth "
            "of field, real-world textures, slight grain, documentary. "
            + PRODUCT_RULE
        ),
    },
]


def gen_one(entry):
    name = entry["id"]
    dest = entry["out_dir"] / f"{name}.png"
    if dest.exists() and dest.stat().st_size > 100_000:
        print(f"[skip ] {name}")
        return {"id": name, "ok": True, "skipped": True}
    t0 = time.time()
    print(f"[start] {name}")
    try:
        result = fal_client.subscribe(
            "fal-ai/nano-banana-2/edit",
            arguments={
                "prompt": entry["prompt"],
                "image_urls": [PRODUCT_URL],
                "aspect_ratio": entry["aspect_ratio"],
                "num_images": 1,
                "output_format": "png",
                "resolution": "2K",
                "safety_tolerance": "5",
            },
        )
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        return {"id": name, "ok": False, "err": str(e)}
    url = result["images"][0]["url"]
    r = requests.get(url, timeout=120, stream=True)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"[done ] {name}  ({time.time()-t0:.1f}s)")
    return {"id": name, "ok": True, "path": str(dest)}


def main():
    results = []
    with ThreadPoolExecutor(max_workers=2) as ex:
        futs = {ex.submit(gen_one, p): p["id"] for p in PROMPTS}
        for fut in as_completed(futs):
            results.append(fut.result())
    print("\n=== SUMMARY ===")
    for r in results:
        flag = "OK " if r.get("ok") else "FAIL"
        print(f"  {flag}  {r['id']}: {r.get('path') or r.get('err','')}")


if __name__ == "__main__":
    main()
