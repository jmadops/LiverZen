#!/usr/bin/env python3
"""
Generate all PDP imagery in parallel:
  - Hero gallery: 1 main + 4 thumbs (1:1)
  - Mechanism cards: 3 (4:3) — Weeks 1-2 / 3-5 / 5-7
  - Pricing bundles: 3-bottle + 6-bottle (1:1)
  - Testimonial avatars: 3 (1:1)

All product shots use product.png as reference. Avatars are text-to-image.
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

print("Uploading product.png reference...")
PRODUCT_URL = fal_client.upload_file(str(PROJECT / "assets" / "product.png"))
print(f"  -> {PRODUCT_URL}")

PRODUCT_RULE = (
    "USE THE PROVIDED PRODUCT REFERENCE IMAGE EXACTLY for the LiverZen "
    "bottle — preserve the white body, green honeycomb pattern, label "
    "typography, proportions, and silhouette. Never redesign, restyle, "
    "or alter the bottle. The label and bottle must be instantly "
    "recognisable as the reference. NO TEXT OR COPY anywhere else in "
    "the frame — no banners, no overlays, no captions. "
)

PHOTO_STYLE = (
    "Hyper-realistic, premium DTC product photography, shot on iPhone 15 "
    "Pro with available natural light, shallow depth of field, real-world "
    "textures. Clean, calm, premium wellness aesthetic — never sterile, "
    "never staged-looking, no studio strobe glare. "
)

PROMPTS = [
    # ──────────── Hero gallery ────────────
    {
        "id": "hero-main",
        "aspect_ratio": "1:1",
        "use_ref": True,
        "prompt": (
            "A premium 1:1 hero shot of a single LiverZen bottle standing "
            "on a smooth pale-cream concrete surface. Soft warm directional "
            "morning light from the upper-left, gentle natural shadow "
            "beneath. A sprig of fresh milk thistle plant lies at the base "
            "(green spiky leaves, one purple-pink flower head). Background: "
            "very soft out-of-focus warm beige with a hint of sage green "
            "fading to lighter cream at the top. The bottle occupies the "
            "central vertical 60% of the frame, label face-on. " + PRODUCT_RULE + PHOTO_STYLE
        ),
    },
    {
        "id": "hero-slider-1-capsules",
        "aspect_ratio": "1:1",
        "use_ref": True,
        "prompt": (
            "A 1:1 product shot of the LiverZen bottle laid on its side on "
            "a soft cream linen cloth, with three vegetarian capsules "
            "(natural off-white with subtle gradient, no logos or text) "
            "spilling out from the open cap toward the camera. The bottle "
            "is in sharp focus, capsules tactile, soft window light from "
            "the right, slight grain. Composition: bottle on the right "
            "two-thirds, capsules trailing toward the left. " + PRODUCT_RULE + PHOTO_STYLE
        ),
    },
    {
        "id": "hero-slider-2-thistle",
        "aspect_ratio": "1:1",
        "use_ref": True,
        "prompt": (
            "A 1:1 product shot — overhead flat-lay. The LiverZen bottle "
            "centered, with a fresh-cut milk thistle plant artfully "
            "arranged around it: spiky green leaves with white veining, "
            "one open purple-pink flower head to the upper-right of the "
            "bottle, a few loose milk thistle seeds scattered. Background: "
            "dark walnut wood with subtle natural grain. Soft directional "
            "natural light, real shadow. " + PRODUCT_RULE + PHOTO_STYLE
        ),
    },
    {
        "id": "hero-slider-3-kitchen",
        "aspect_ratio": "1:1",
        "use_ref": True,
        "prompt": (
            "A 1:1 lifestyle product shot. The LiverZen bottle on a clean "
            "off-white kitchen counter, slightly to the left of center, "
            "next to a small French-press coffee maker (just out of focus) "
            "and a folded linen napkin. Soft morning window light from "
            "the right, gentle shadow. Background: blurred warm kitchen "
            "interior — wooden cabinets, plants on a shelf. The mood is "
            "the start of a calm morning routine. " + PRODUCT_RULE + PHOTO_STYLE
        ),
    },
    {
        "id": "hero-slider-4-ingredients",
        "aspect_ratio": "1:1",
        "use_ref": True,
        "prompt": (
            "A 1:1 ingredient flat-lay overhead shot. The LiverZen bottle "
            "centered. Around it, ingredients laid out in small clusters: "
            "milk thistle seeds and one purple flower head (top-left), a "
            "small pile of bright orange turmeric powder with a fresh "
            "turmeric root (top-right), a pueraria root slice "
            "(bottom-left), a small porcelain bowl of two open vegetarian "
            "capsules (bottom-right). Background: warm soft beige linen. "
            "Soft directional natural light, shadows clean and real. "
            "Editorial composition, balanced negative space. "
            + PRODUCT_RULE + PHOTO_STYLE
        ),
    },
    # ──────────── Mechanism cards ────────────
    {
        "id": "mech-1-internal",
        "aspect_ratio": "4:3",
        "use_ref": False,
        "prompt": (
            "A premium editorial medical-illustration style image. "
            "Anatomically accurate human liver, deep rich red-brown with "
            "subtle hepatic vein structure, three-quarter angle, centered. "
            "Background: soft out-of-focus dark teal-to-charcoal gradient "
            "with very faint glowing cellular dot patterns suggesting "
            "internal repair work happening at a microscopic level. The "
            "liver looks alive, healthy, working. Cinematic, restrained, "
            "almost luxurious — half painting, half hyper-detailed CGI. "
            "Soft rim-lighting from above-left. NO TEXT, NO LABELS, NO "
            "ANATOMY CALLOUTS. " + PHOTO_STYLE
        ),
    },
    {
        "id": "mech-2-clear-mind",
        "aspect_ratio": "4:3",
        "use_ref": False,
        "prompt": (
            "A hyper-realistic candid iPhone-style photo of a 50-something "
            "American man at a home-office desk, mid-afternoon, looking "
            "sharp and focused — clear-eyed, awake, slight relaxed smile, "
            "leaning slightly forward. Soft sunlight through window blinds "
            "casting gentle horizontal stripes on the back wall. Out-of-"
            "focus desk: laptop, mug of coffee, a notepad. Warm "
            "afternoon light. Composition is candid, real, mid-thought. "
            "Conveys: the afternoon fog has lifted, mind is clear. "
            "Documentary feel, no skin smoothing. NO TEXT, NO OVERLAYS. "
            + PHOTO_STYLE
        ),
    },
    {
        "id": "mech-3-bloodwork-improved",
        "aspect_ratio": "4:3",
        "use_ref": False,
        "prompt": (
            "Top-down hyper-realistic iPhone shot of a printed lab "
            "results page on a doctor's clipboard on a wood desk. The "
            "sheet shows a liver function panel. The 'ALT (SGPT)' row is "
            "circled in green ballpoint pen and the value reads '38' (no "
            "'H' flag) within the printed reference range '7-56 U/L'. "
            "A second sheet beneath the first is partly visible — an "
            "older result showing ALT '67 H' (the H circled in red), "
            "now superseded. Slight angle, real paper texture, soft "
            "afternoon window light, edge of a stethoscope blurred at "
            "the upper-right. The narrative: numbers came back into "
            "range. NO TEXT OVERLAYS. " + PHOTO_STYLE
        ),
    },
    # ──────────── Pricing bundles ────────────
    {
        "id": "tier-3-bottles",
        "aspect_ratio": "1:1",
        "use_ref": True,
        "prompt": (
            "A clean 1:1 product photo of EXACTLY THREE identical LiverZen "
            "bottles arranged in a slight V-formation — one bottle "
            "centered slightly forward and lower, two bottles flanking "
            "behind on either side, all upright, all face-on to camera. "
            "Soft cream gradient background fading from warm white at "
            "top to soft beige at bottom. Gentle natural shadows. All "
            "three bottles must look identical and match the provided "
            "product reference image precisely — same label, same "
            "honeycomb pattern, same proportions. Premium bundle "
            "presentation, e-commerce ready. " + PRODUCT_RULE + PHOTO_STYLE
        ),
    },
    {
        "id": "tier-6-bottles",
        "aspect_ratio": "1:1",
        "use_ref": True,
        "prompt": (
            "A clean 1:1 product photo of EXACTLY SIX identical LiverZen "
            "bottles arranged in a 2-row staggered formation — three "
            "bottles in the back row, three in the front row offset, all "
            "upright and face-on to camera, one slightly central in "
            "front. Soft cream gradient background fading from warm "
            "white at top to soft sage-tinted beige at bottom. Gentle "
            "natural shadows. All six bottles must look identical and "
            "match the provided product reference image precisely — "
            "same label, same honeycomb pattern, same proportions. "
            "Premium bundle presentation, e-commerce ready. "
            + PRODUCT_RULE + PHOTO_STYLE
        ),
    },
    # ──────────── Testimonial avatars ────────────
    {
        "id": "avatar-tom",
        "aspect_ratio": "1:1",
        "use_ref": False,
        "prompt": (
            "A tight 1:1 candid head-and-shoulders avatar portrait of "
            "Tom B., a 56-year-old white American man from Cleveland, "
            "Ohio. Salt-and-pepper short hair, weathered face with deep "
            "smile lines, slight stubble. Wearing a faded olive-green "
            "Henley shirt. Looking just past the camera with a small "
            "natural smile. Soft window light from the upper-left, "
            "background out-of-focus suggesting a Midwestern home "
            "interior — warm wood tones. Documentary, real, no skin "
            "smoothing. Tight crop on face and shoulders. " + PHOTO_STYLE
        ),
    },
    {
        "id": "avatar-dave",
        "aspect_ratio": "1:1",
        "use_ref": False,
        "prompt": (
            "A tight 1:1 candid head-and-shoulders avatar portrait of "
            "Dave R., a 51-year-old white American man from Charlotte, "
            "North Carolina. Short brown hair greying at the temples, "
            "trimmed beard, intelligent eyes. Wearing a dark grey "
            "polo shirt. Looking just past the camera, expression "
            "neutral-to-mildly-amused. Soft afternoon natural light, "
            "background out-of-focus suggesting a Southern American "
            "home — warm tones. Documentary, real. Tight crop on face "
            "and shoulders. " + PHOTO_STYLE
        ),
    },
    {
        "id": "avatar-mike",
        "aspect_ratio": "1:1",
        "use_ref": False,
        "prompt": (
            "A tight 1:1 candid head-and-shoulders avatar portrait of "
            "Mike R., a 54-year-old white American man from Indianapolis, "
            "Indiana. Light brown hair, clean-shaven, friendly face with "
            "laugh lines. Wearing a navy blue collared shirt. Looking "
            "into the camera with a relaxed half-smile. Soft natural "
            "light from a window, background out-of-focus suggesting "
            "a Midwestern living room — warm domestic tones. "
            "Documentary, real, no skin smoothing. Tight crop on face "
            "and shoulders. " + PHOTO_STYLE
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
    print(f"[start] {name}  ratio={entry['aspect_ratio']}  ref={entry['use_ref']}")
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
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(gen_one, p): p["id"] for p in PROMPTS}
        for fut in as_completed(futs):
            results.append(fut.result())
    print("\n=== SUMMARY ===")
    for r in results:
        flag = "OK " if r.get("ok") else "FAIL"
        print(f"  {flag}  {r['id']}: {r.get('path') or r.get('err','')}")


if __name__ == "__main__":
    main()
