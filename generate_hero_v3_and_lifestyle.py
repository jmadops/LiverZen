#!/usr/bin/env python3
"""
Generate:
  1. hero0-headline.png   — Slot-1 headline static ad (1:1, color background,
                             product, problem-solution headline). Template-1
                             style: bold serif headline + product on color block.
  2-4. Three vertical 9:16 lifestyle shots for the "See It for Yourself"
       carousel — narrating the daily arc: morning / afternoon / evening.
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

OUT = PROJECT / "assets" / "pdp"
LIFESTYLE_OUT = PROJECT / "assets" / "lifestyle"
OUT.mkdir(parents=True, exist_ok=True)
LIFESTYLE_OUT.mkdir(parents=True, exist_ok=True)

print("Uploading product reference...")
PRODUCT_URL = fal_client.upload_file(str(PROJECT / "assets" / "product.png"))
print(f"  -> {PRODUCT_URL}")

PRODUCT_RULE = (
    "USE THE PROVIDED PRODUCT REFERENCE IMAGE EXACTLY for the LiverZen "
    "bottle — preserve white body, green honeycomb pattern, label "
    "typography, proportions and silhouette. Never redesign. "
)

IPHONE_STYLE = (
    "Hyper-realistic, shot on iPhone 15 Pro, available natural light, "
    "shallow depth of field, real-world textures, slight grain. "
    "Documentary candid feel, no studio lighting, no skin smoothing. "
)

PROMPTS = [
    # ──────────── Headline static ad ────────────
    {
        "id": "hero0-headline",
        "out_dir": OUT,
        "aspect_ratio": "1:1",
        "use_ref": True,
        "prompt": (
            "A premium 1:1 static-ad hero image — bold editorial DTC ad "
            "treatment. Composition is split horizontally: TOP 55% is a "
            "solid deep forest green block, hex #1F4632. BOTTOM 45% is "
            "warm cream block, hex #F5EFE3, with a thin charcoal hairline "
            "rule along the join.\n"
            "TOP BLOCK: at the very top, small all-caps cream sans-serif "
            "tracked-out eyebrow text reads exactly: \"LIVERZEN — DAILY "
            "LIVER SUPPORT\". Below that, centered, a large editorial "
            "serif headline in cream off-white reads exactly, breaking "
            "naturally over THREE lines:\n"
            "    Bring your ALT\n"
            "    back to normal —\n"
            "    without quitting bourbon.\n"
            "The third line \"without quitting bourbon\" is rendered in "
            "italic for emphasis. Generous line-height. Headline is the "
            "dominant element of the top block.\n"
            "BOTTOM BLOCK: the provided product reference image of the "
            "LiverZen bottle is centered, occupying about 75% of the "
            "block's height, label face-on. Subtle natural shadow under "
            "the bottle. To the bottom-right of the bottle, three tiny "
            "stacked benefit lines in small charcoal sans-serif:\n"
            "    ✓ 80% standardised silymarin\n"
            "    ✓ 30+ clinical studies\n"
            "    ✓ 60-day empty-bottle refund\n"
            "Clean hierarchy. NO LOGOS other than what is on the bottle "
            "label. Premium DTC static ad, production-ready. "
            + PRODUCT_RULE
        ),
    },
    # ──────────── Lifestyle — Morning ────────────
    {
        "id": "life-1-morning",
        "out_dir": LIFESTYLE_OUT,
        "aspect_ratio": "9:16",
        "use_ref": True,
        "prompt": (
            "A vertical 9:16 hyper-realistic morning lifestyle photo, "
            "shot from a slightly elevated POV looking down at a "
            "wooden breakfast table. A 60-something American man's "
            "weathered hand is visible in frame holding the provided "
            "product reference image of the LiverZen bottle — label "
            "face-on, sharp focus. On the table around: a steaming mug "
            "of black coffee, a half-eaten bowl of oatmeal with "
            "blueberries, a folded morning newspaper, a glass of water, "
            "warm window light streaming in from the upper left "
            "casting long natural shadows. Mood: calm, beginning of a "
            "real day. " + PRODUCT_RULE + IPHONE_STYLE
        ),
    },
    # ──────────── Lifestyle — Afternoon ────────────
    {
        "id": "life-2-afternoon",
        "out_dir": LIFESTYLE_OUT,
        "aspect_ratio": "9:16",
        "use_ref": True,
        "prompt": (
            "A vertical 9:16 hyper-realistic mid-afternoon home-office "
            "lifestyle photo. A 50-something American man at his desk, "
            "leaning forward focused on a laptop screen, slight relaxed "
            "smile, clear-eyed and alert. Soft afternoon sunlight "
            "through window blinds casting horizontal stripes on the "
            "wall behind. On the corner of the desk, the provided "
            "product reference image of the LiverZen bottle stands "
            "next to a half-full coffee mug. Background: framed "
            "pictures, plants, blurred home-office details. Mood: "
            "sharp through 3pm, no afternoon fog. " + PRODUCT_RULE + IPHONE_STYLE
        ),
    },
    # ──────────── Lifestyle — Evening ────────────
    {
        "id": "life-3-evening",
        "out_dir": LIFESTYLE_OUT,
        "aspect_ratio": "9:16",
        "use_ref": True,
        "prompt": (
            "A vertical 9:16 hyper-realistic evening kitchen scene. A "
            "50-60-something American man's hand pouring bourbon from a "
            "decanter into a short crystal rocks glass with a single "
            "large clear ice cube, on a worn butcher-block kitchen "
            "counter. Warm tungsten pendant light overhead, dim "
            "background — evening, end of day. The provided product "
            "reference image of the LiverZen bottle is visible on the "
            "counter just beyond the glass, label face-on, sharp focus. "
            "Mood: he's earned this pour, his evening unchanged, his "
            "liver supported. " + PRODUCT_RULE + IPHONE_STYLE
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
    print(f"[start] {name}  ratio={entry['aspect_ratio']}")
    args = {
        "prompt": entry["prompt"],
        "aspect_ratio": entry["aspect_ratio"],
        "num_images": 1,
        "output_format": "png",
        "resolution": "2K",
        "safety_tolerance": "5",
    }
    if entry["use_ref"]:
        args["image_urls"] = [PRODUCT_URL]
        endpoint = "fal-ai/nano-banana-2/edit"
    else:
        endpoint = "fal-ai/nano-banana-2"
    try:
        result = fal_client.subscribe(endpoint, arguments=args)
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
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(gen_one, p): p["id"] for p in PROMPTS}
        for fut in as_completed(futs):
            results.append(fut.result())
    print("\n=== SUMMARY ===")
    for r in results:
        flag = "OK " if r.get("ok") else "FAIL"
        print(f"  {flag}  {r['id']}: {r.get('path') or r.get('err','')}")


if __name__ == "__main__":
    main()
