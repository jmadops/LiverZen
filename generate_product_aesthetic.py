#!/usr/bin/env python3
"""
Six aesthetic hero shots of the LiverZen bottle with natural greenery.
No copy, no text, hyper-realistic, iPhone-style. Uses product.png as
reference so the bottle is rendered faithfully.
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

OUT = PROJECT / "assets" / "aesthetic"
OUT.mkdir(parents=True, exist_ok=True)

print("Uploading product.png reference...")
PRODUCT_URL = fal_client.upload_file(str(PROJECT / "assets" / "product.png"))
print(f"  -> {PRODUCT_URL}")

REF_RULE = (
    "USE THE PROVIDED PRODUCT REFERENCE IMAGE EXACTLY for the LiverZen "
    "bottle — match the white body, green honeycomb pattern, label "
    "typography and proportions precisely. Do not redesign, restyle, or "
    "reinterpret the bottle. The label and bottle silhouette must be "
    "instantly recognizable as the reference. NO TEXT OR COPY anywhere "
    "else in the frame — no banners, no overlays, no captions, no logos "
    "other than what is naturally on the product label itself. "
)

STYLE = (
    "Hyper-realistic, shot on iPhone 15 Pro, available natural light only, "
    "shallow depth of field, slight chromatic edge, real-world textures and "
    "imperfections. Premium editorial wellness photography aesthetic. "
    "Clean, calm, aspirational — never sterile, never staged-looking. "
)

PROMPTS = [
    {
        "id": "01-foliage-morning",
        "aspect_ratio": "4:3",
        "prompt": (
            "A single LiverZen bottle stands on a smooth slab of dark slate "
            "stone, surrounded by lush green leafy foliage — broad monstera "
            "leaves and ferns just out of focus framing the bottle. Soft "
            "dappled morning sunlight filters through the leaves, casting "
            "leaf shadows across the bottle and stone. A few small water "
            "droplets cling to the leaves and the stone surface. " + REF_RULE + STYLE
        ),
    },
    {
        "id": "02-milk-thistle-companion",
        "aspect_ratio": "4:3",
        "prompt": (
            "A single LiverZen bottle on a weathered light-oak wooden plank "
            "table, with a fresh-cut sprig of milk thistle plant — purple-pink "
            "spiky flower head, jagged green leaves with white veining — "
            "lying naturally beside it. A few loose milk thistle seeds "
            "scattered on the wood. Soft window light from the upper-left, "
            "gentle warm tone, slight steam from a teacup just out of frame. "
            + REF_RULE + STYLE
        ),
    },
    {
        "id": "03-stone-overhead-leaves",
        "aspect_ratio": "4:3",
        "prompt": (
            "Top-down overhead shot. A single LiverZen bottle lying on its "
            "side on smooth river-stone surface, surrounded by an asymmetric "
            "scattering of fresh green eucalyptus leaves and small sage "
            "leaves. A few drops of clear water on the leaves and stones. "
            "Soft directional natural light from the right, shadows long "
            "and clean. " + REF_RULE + STYLE
        ),
    },
    {
        "id": "04-mossy-close",
        "aspect_ratio": "4:3",
        "prompt": (
            "Macro close-up of a single LiverZen bottle resting on a bed of "
            "deep emerald moss, with two open vegetarian capsules lying just "
            "in front of the bottle — the moss beneath softly absorbing the "
            "warm light. Bottle in sharp focus, moss texture in extreme "
            "tactile detail, background blurred into rich green bokeh. "
            "Cool morning light, slight mist in the air. " + REF_RULE + STYLE
        ),
    },
    {
        "id": "05-linen-herbs-kitchen",
        "aspect_ratio": "4:3",
        "prompt": (
            "A single LiverZen bottle on a crumpled natural-linen cloth in "
            "a sunlit modern kitchen. Sprigs of fresh rosemary, thyme, and "
            "a small bundle of dried milk thistle flowers arranged loosely "
            "around the base. A linen-textured cutting board peeking in at "
            "the edge of frame. Warm midday window light, soft, real. "
            + REF_RULE + STYLE
        ),
    },
    {
        "id": "06-greenhouse-shelf",
        "aspect_ratio": "3:2",
        "prompt": (
            "A single LiverZen bottle on a worn wooden shelf inside a "
            "small backyard greenhouse, surrounded by potted herbs and "
            "leafy plants — basil, parsley, milk thistle seedlings in terra "
            "cotta. Shafts of soft afternoon sunlight cut through the "
            "greenhouse glass, catching the fine dust in the air. Gentle "
            "warm tones, slightly overgrown, lived-in. " + REF_RULE + STYLE
        ),
    },
]


def gen_one(entry):
    name = entry["id"]
    dest = OUT / f"{name}.png"
    if dest.exists() and dest.stat().st_size > 100_000:
        print(f"[skip ] {name}")
        return {"id": name, "ok": True, "skipped": True}
    t0 = time.time()
    print(f"[start] {name}  aspect={entry['aspect_ratio']}")
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
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(gen_one, p): p["id"] for p in PROMPTS}
        for fut in as_completed(futs):
            results.append(fut.result())
    print("\n=== SUMMARY ===")
    for r in results:
        flag = "OK " if r.get("ok") else "FAIL"
        print(f"  {flag}  {r['id']}: {r.get('path') or r.get('err','')}")


if __name__ == "__main__":
    main()
