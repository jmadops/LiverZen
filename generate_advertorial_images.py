#!/usr/bin/env python3
"""
Generate hyper-realistic, iPhone-style advertorial images for LiverZen
using fal.ai nano-banana-2/edit.

Outputs land in assets/generated/. Concurrent generation (7 prompts).
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
    print("ERROR: FAL_KEY missing")
    sys.exit(1)
os.environ["FAL_KEY"] = FAL_KEY

OUT = PROJECT / "assets" / "generated"
OUT.mkdir(parents=True, exist_ok=True)

# Upload product reference once
print("Uploading product.png to fal...")
PRODUCT_URL = fal_client.upload_file(str(PROJECT / "assets" / "product.png"))
print(f"  -> {PRODUCT_URL}")

# Shared style suffix — drives the iPhone/hyper-real look
IPHONE_STYLE = (
    "Shot on iPhone 15 Pro, available light only, no studio strobes, no flash. "
    "Hyper-realistic, documentary-style candid photography. Natural skin texture "
    "with visible pores, fine lines, age spots — absolutely no skin smoothing or "
    "retouching. Slight grain, slight motion imperfection, subtle chromatic edge. "
    "Real-world environment with depth and context — never a plain studio backdrop. "
    "Composition feels casual, like a real person snapped this on their phone."
)

PROMPTS = [
    {
        "id": "hero",
        "aspect_ratio": "16:9",
        "image_urls": [],
        "prompt": (
            "A dimly-lit American kitchen at night, around 10pm. A short crystal "
            "rocks glass holding two fingers of bourbon and one large clear ice "
            "cube sits on a worn butcher-block wooden counter, condensation "
            "beading on the glass. A 50-something man's hand visible from the "
            "wrist down, slightly weathered, wearing a simple gold wedding band, "
            "rests near the glass — not gripping it, just present. A laptop "
            "glowing in the soft background blur. Warm tungsten pendant light "
            "overhead casts long shadows. Shallow depth of field, focus on the "
            "ice cube and bourbon. Mood: end of a long day, quiet contemplation. "
            + IPHONE_STYLE
        ),
    },
    {
        "id": "article-1-bloodwork",
        "aspect_ratio": "16:9",
        "image_urls": [],
        "prompt": (
            "Top-down close-up of a printed lab results page on a doctor's "
            "clipboard, laid on a wooden desk. The paper shows liver enzyme "
            "results in printed serif text: AST, ALT (SGPT), ALP, BILIRUBIN. "
            "The 'ALT (SGPT)' row stands out — circled in blue ballpoint pen "
            "with visible pen indentation in the paper. The ALT value reads "
            "'67 H' with H meaning HIGH. Reference range column: '7-56 U/L'. "
            "Other rows visible but unhighlighted. Slight angle, not perfectly "
            "aligned, as if just dropped on the desk. Soft afternoon window "
            "light from the upper-left, gentle shadow under the clipboard. "
            "Out-of-focus edge of a stethoscope and a tissue box at the frame "
            "edge. Hand of a patient — visible at the corner — holding a "
            "ballpoint pen. Real paper texture, slight crease. "
            + IPHONE_STYLE
        ),
    },
    {
        "id": "article-2-trend",
        "aspect_ratio": "16:9",
        "image_urls": [],
        "prompt": (
            "Hyper-realistic photo of a printed black-and-white line chart held "
            "in a man's weathered hand at a slight angle, taken from his POV. "
            "Title at top reads 'ALT (SGPT) — 36 month trend'. Three labeled "
            "data points connected by a slowly-rising line: '2022 — 41', "
            "'2023 — 52', '2024 — 67'. A dotted horizontal red reference line "
            "at 56 labeled 'Upper normal limit'. Y-axis labeled 'U/L'. The "
            "line clearly crosses above the dotted limit between the second "
            "and third points. Slight crease where the paper has been folded. "
            "Background out-of-focus: an exam-room paper-roll table, edge of "
            "a blood-pressure cuff. Soft fluorescent overhead light, real and "
            "slightly cool. Natural shadow on the paper. "
            + IPHONE_STYLE
        ),
    },
    {
        "id": "sidebar-comparison",
        "aspect_ratio": "4:3",
        "image_urls": [PRODUCT_URL],
        "prompt": (
            "Three supplement bottles in a clean row on an off-white kitchen "
            "countertop, soft daylight from a window on the left. "
            "LEFT bottle: a generic CVS-style brown HDPE plastic supplement "
            "bottle with a basic white printed label, 'MILK THISTLE' in plain "
            "block lettering, small subtext '30% silymarin'. "
            "MIDDLE bottle: a slightly cleaner pharmacy-brand white plastic "
            "bottle with a beige label, 'MILK THISTLE EXTRACT' header, small "
            "subtext '50% silymarin'. "
            "RIGHT bottle: USE THE PROVIDED REFERENCE IMAGE EXACTLY — this is "
            "the LiverZen bottle, white with green honeycomb pattern, '80% "
            "silymarin' label. Match it precisely, don't redesign. "
            "All three bottles roughly the same height. The right (LiverZen) "
            "bottle is subtly forward, in sharper focus than the other two. "
            "Soft natural shadows beneath each bottle. Composition is honest "
            "documentary product comparison, not a studio shot. "
            + IPHONE_STYLE
        ),
    },
    {
        "id": "testimonial-mark",
        "aspect_ratio": "4:3",
        "image_urls": [],
        "prompt": (
            "A candid head-and-shoulders portrait of a 62-year-old white "
            "American man at his kitchen table in suburban Denver, Colorado. "
            "Short cropped grey hair, deep crow's feet, weathered tan from "
            "years outdoors, slight stubble. Wearing a faded chambray work "
            "shirt with the top button undone. A heavy ceramic coffee mug "
            "rests in his hand. He's looking slightly off-camera, mid-thought, "
            "small natural smile. Soft morning natural light pouring through "
            "the kitchen window behind him, creating a gentle rim on his "
            "shoulder. Out-of-focus background: modest American kitchen, edge "
            "of a refrigerator with a few magnets, blurred. Honest, real face "
            "— no skin smoothing, age spots and pores visible. "
            + IPHONE_STYLE
        ),
    },
    {
        "id": "testimonial-dave",
        "aspect_ratio": "4:3",
        "image_urls": [],
        "prompt": (
            "A candid head-and-shoulders portrait of a 56-year-old Black "
            "American man in his Atlanta, Georgia home office. Close-cropped "
            "salt-and-pepper hair and beard, intelligent eyes, faint laugh "
            "lines. Wearing a navy polo shirt. Slightly leaning back in a "
            "leather desk chair, looking off-camera with a thoughtful "
            "half-smile. Warm afternoon light through window blinds — soft "
            "horizontal striping on the wall behind. Out-of-focus background: "
            "wood-paneled wall, a couple of framed family photos and a "
            "bookshelf, all blurred. Documentary, real, totally unposed feel. "
            "No skin retouching, natural texture. "
            + IPHONE_STYLE
        ),
    },
    {
        "id": "testimonial-greg",
        "aspect_ratio": "4:3",
        "image_urls": [],
        "prompt": (
            "A candid head-and-shoulders portrait of a 58-year-old Hispanic "
            "American man standing in his backyard in suburban Houston, Texas. "
            "Receding hairline, grey at the temples, working-man's tan, slight "
            "moustache. Wearing a faded navy company polo (logo on the chest "
            "is intentionally unreadable / blurred — no real-world brand). "
            "Hands on hips, relaxed posture, looking just past the camera with "
            "a small genuine smile, not posed. Late-afternoon golden-hour sun "
            "raking from the side, casting a soft warm rim. Background "
            "out-of-focus: wooden suburban fence, edge of a grill, a bit of "
            "lawn. Honest face — no smoothing, real pores, real skin. "
            + IPHONE_STYLE
        ),
    },
]


def generate_one(entry):
    name = entry["id"]
    dest = OUT / f"{name}.png"
    if dest.exists() and dest.stat().st_size > 100_000:
        print(f"[skip ] {name}  (already exists)")
        return {"id": name, "ok": True, "path": str(dest), "skipped": True}
    t0 = time.time()
    print(f"[start] {name}  aspect={entry['aspect_ratio']}  refs={len(entry['image_urls'])}")
    args = {
        "prompt": entry["prompt"],
        "aspect_ratio": entry["aspect_ratio"],
        "num_images": 1,
        "output_format": "png",
        "resolution": "2K",
        "safety_tolerance": "5",
    }
    if entry["image_urls"]:
        args["image_urls"] = entry["image_urls"]
        endpoint = "fal-ai/nano-banana-2/edit"
    else:
        endpoint = "fal-ai/nano-banana-2"
    try:
        result = fal_client.subscribe(endpoint, arguments=args)
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        return {"id": name, "ok": False, "err": str(e)}
    images = result.get("images", [])
    if not images:
        print(f"[FAIL] {name}: no images returned")
        return {"id": name, "ok": False, "err": "no images"}
    url = images[0]["url"]
    r = requests.get(url, timeout=120, stream=True)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    dt = time.time() - t0
    print(f"[done ] {name}  -> {dest.name}  ({dt:.1f}s)")
    return {"id": name, "ok": True, "path": str(dest)}


def main():
    results = []
    with ThreadPoolExecutor(max_workers=7) as ex:
        futs = {ex.submit(generate_one, p): p["id"] for p in PROMPTS}
        for fut in as_completed(futs):
            results.append(fut.result())
    print("\n=== SUMMARY ===")
    for r in results:
        status = "OK " if r.get("ok") else "FAIL"
        extra = r.get("path") or r.get("err", "")
        print(f"  {status}  {r['id']}: {extra}")


if __name__ == "__main__":
    main()
