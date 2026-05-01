#!/usr/bin/env python3
"""
Hero gallery v2 — 4 ad-style images for the PDP hero gallery.

  1. hero1-blueprint.png   — Bottle with scientific-blueprint annotations (Template 4/68)
  2. hero2-vs-them.png     — Pharmacy 30% vs LiverZen 80% bullet-point comparison (Template 7)
  3. hero3-supp-facts.png  — Bottle + supplement-facts panel + ingredient elements
  4. hero4-breakfast.png   — Lifestyle: capsule + breakfast scene
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
OUT.mkdir(parents=True, exist_ok=True)

print("Uploading product.png + ingredients.png references...")
PRODUCT_URL = fal_client.upload_file(str(PROJECT / "assets" / "product.png"))
INGREDIENTS_URL = fal_client.upload_file(str(PROJECT / "assets" / "ingredients.png"))
print(f"  product   -> {PRODUCT_URL}")
print(f"  ingredients -> {INGREDIENTS_URL}")

PRODUCT_RULE = (
    "USE THE PROVIDED PRODUCT REFERENCE IMAGE EXACTLY for the LiverZen "
    "bottle — preserve white body, green honeycomb pattern, label "
    "typography, proportions and silhouette. Never redesign the bottle. "
)

PROMPTS = [
    # ──────────── Hero 1: Blueprint Annotation ────────────
    {
        "id": "hero1-blueprint",
        "aspect_ratio": "1:1",
        "image_urls": [PRODUCT_URL],
        "prompt": (
            "A clean 1:1 'scientific blueprint' style hero ad. Background: "
            "soft warm cream #F5EFE3 with a barely-visible thin "
            "blueprint grid pattern (very faint, 4% opacity charcoal). "
            "The provided product reference image of the LiverZen bottle "
            "is positioned slightly left-of-center, occupying about 55% "
            "of the frame's height. From the bottle, four to five thin "
            "charcoal connector lines extend outward to small annotation "
            "text labels — like a technical diagram. "
            "ANNOTATIONS in clean small-cap sans-serif charcoal text:\n"
            "- Top right: \"80% STANDARDISED SILYMARIN\"\n"
            "- Mid right: \"300mg MILK THISTLE EXTRACT\"\n"
            "- Lower right: \"+ TURMERIC, PUERARIA, L-METHIONINE\"\n"
            "- Top left: \"3RD-PARTY BATCH TESTED\"\n"
            "- Lower left: \"90 VEGETARIAN CAPSULES\"\n"
            "Each annotation has a small dot/circle at the connector "
            "endpoint touching the bottle, like a real engineering "
            "drawing. Lines are precise, restrained, NOT decorative. "
            "Tone: calm, premium, intelligent. No banners, no big "
            "headlines, no logos beyond what's on the bottle label "
            "itself. Professional DTC static ad. "
            + PRODUCT_RULE
        ),
    },
    # ──────────── Hero 2: Us vs Them ────────────
    {
        "id": "hero2-vs-them",
        "aspect_ratio": "1:1",
        "image_urls": [PRODUCT_URL],
        "prompt": (
            "A 1:1 polished hero ad with a vertical 50/50 split. "
            "LEFT half: soft cool grey #EAEAEA background. Small "
            "all-caps header at top in muted charcoal: \"PHARMACY MILK "
            "THISTLE\". Below it, a generic brown HDPE supplement bottle "
            "(CVS-style) with a basic white label reading 'MILK THISTLE "
            "30% silymarin', centered. Below the bottle, three lines "
            "with small red X icons next to text in clean sans-serif:\n"
            "✗ Under-standardised\n"
            "✗ 30–50% silymarin\n"
            "✗ Often unverified\n"
            "RIGHT half: warm off-white #F8F4EC background. Small "
            "all-caps header at top in muted charcoal: \"LIVERZEN\". "
            "Below it, the provided product reference image of the "
            "LiverZen bottle, centered. Below the bottle, three lines "
            "with small muted-green check icons:\n"
            "✓ Fully standardised\n"
            "✓ 80% silymarin\n"
            "✓ 3rd-party tested\n"
            "Thin vertical rule down the middle. Clean composition, "
            "no other text. Premium DTC ad presentation. "
            + PRODUCT_RULE
        ),
    },
    # ──────────── Hero 3: Supplement Facts + Ingredients ────────────
    {
        "id": "hero3-supp-facts",
        "aspect_ratio": "1:1",
        "image_urls": [PRODUCT_URL, INGREDIENTS_URL],
        "prompt": (
            "A 1:1 premium overhead flat-lay hero ad. Background: warm "
            "off-white #F8F4EC. Composition split: the FIRST provided "
            "reference image is the LiverZen bottle (centered slightly "
            "right) — match it exactly, do not redesign. The SECOND "
            "provided reference image is the supplement-facts back-of-"
            "label panel — render that panel as a clean separate "
            "rectangular insert positioned to the LEFT of the bottle, "
            "showing the actual ingredient values clearly: Vitamin C "
            "10mg, Milk Thistle Extract 300mg (80% silymarin), Inositol "
            "200mg, Pueraria extract 68mg, L-methionine 10mg, Turmeric "
            "extract 4mg. Around the bottle and panel, photograph "
            "naturalistic ingredient cues: a small cluster of milk "
            "thistle seeds and one purple thistle flower head (top), a "
            "small pile of bright orange turmeric powder with a "
            "turmeric root (right), a pueraria root slice (bottom), "
            "a small porcelain dish with two open vegetarian capsules "
            "(near the bottle base). Soft directional natural light, "
            "real shadows, hyper-realistic, premium editorial. NO "
            "OVERLAID HEADLINES. " + PRODUCT_RULE
        ),
    },
    # ──────────── Hero 4: Capsule with Breakfast (lifestyle) ────────────
    {
        "id": "hero4-breakfast",
        "aspect_ratio": "1:1",
        "image_urls": [PRODUCT_URL],
        "prompt": (
            "A 1:1 hyper-realistic morning lifestyle photo. A "
            "60-something American man's weathered hand placing a "
            "single open-form vegetarian capsule (natural off-white) "
            "on a small white porcelain saucer beside a steaming mug "
            "of black coffee. On the same wooden breakfast table: a "
            "half-eaten bowl of oatmeal with blueberries, a folded "
            "morning newspaper, a slice of whole-grain toast with "
            "butter, a glass of water, and the provided product "
            "reference image of the LiverZen bottle standing nearby — "
            "label face-on, sharp focus, just behind the capsule. Soft "
            "warm morning sunlight streaming through a window from the "
            "left, casting gentle long shadows on the table. Mood: "
            "calm, deliberate, real. Real American kitchen vibe. "
            "Documentary, candid, iPhone 15 Pro look. NO TEXT, NO "
            "OVERLAYS. " + PRODUCT_RULE
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
    print(f"[start] {name}  ratio={entry['aspect_ratio']}  refs={len(entry['image_urls'])}")
    try:
        result = fal_client.subscribe(
            "fal-ai/nano-banana-2/edit",
            arguments={
                "prompt": entry["prompt"],
                "image_urls": entry["image_urls"],
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
