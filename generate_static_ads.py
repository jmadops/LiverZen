#!/usr/bin/env python3
"""
Page-specific static ads for the LiverZen advertorial. Five ads built
following the CE V2 Static Ad Agent template-mode procedure, with copy
mapped to the strongest hooks in the bourbon-confession advertorial:

  - Doctor's confession ("I take the 80% myself")
  - 30% vs 80% silymarin pharmacy comparison
  - 80% standardisation as the differentiator
  - 7-weeks-back-to-normal outcome
  - "Same bourbon, same hours, one thing different"

Product reference (product.png) is attached so the bottle renders
faithfully. No invented stats — copy pulled from advertorial body.
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

OUT = PROJECT / "assets" / "static-ads"
OUT.mkdir(parents=True, exist_ok=True)

print("Uploading product.png reference...")
PRODUCT_URL = fal_client.upload_file(str(PROJECT / "assets" / "product.png"))
print(f"  -> {PRODUCT_URL}")

PRODUCT_RULE = (
    "USE THE PROVIDED PRODUCT REFERENCE IMAGE EXACTLY for the LiverZen "
    "bottle — preserve the white body, green honeycomb pattern, label "
    "typography, proportions, and silhouette. Never redesign, restyle, "
    "or alter the bottle. The label and bottle must be instantly "
    "recognisable as the reference. "
)

CLOSER = (
    "Professional DTC static ad, high-resolution, clean layout, "
    "production-ready. Hyper-realistic photography, never AI-illustrated. "
)

PROMPTS = [
    # ──────────── Ad 1: Curiosity Gap (Template 16) ────────────
    {
        "id": "01-curiosity-doctors-shelf",
        "aspect_ratio": "1:1",
        "template": "16 — Curiosity Gap",
        "prompt": (
            "A square 1:1 social ad on a moody, dimly-lit medicine cabinet "
            "shelf at home. Background: warm wood-grain shelf with subtle "
            "shadows, soft amber kitchen-light glow from the right edge. "
            "Color palette: deep charcoal backdrop, warm wood mid-tone, "
            "creamy off-white text. The provided product reference image "
            "of the LiverZen bottle is positioned slightly right-of-center, "
            "occupying about 45% of the frame, lit warmly from the side. "
            "On the upper-left third of the frame, a serif editorial "
            "headline in clean off-white reads exactly: \"What your doctor "
            "takes that he won't write on a prescription pad.\" Headline "
            "wraps over three lines, generous line height, slight italic on "
            "\"won't\". Below the headline, a thin off-white horizontal rule, "
            "then small sans-serif subline reads exactly: \"It's not what "
            "they sell at CVS.\" No other text. No logos beyond what is on "
            "the bottle label itself. " + PRODUCT_RULE + CLOSER
        ),
    },
    # ──────────── Ad 2: Us vs Them (Template 7) ────────────
    {
        "id": "02-vs-pharmacy-comparison",
        "aspect_ratio": "1:1",
        "template": "7 — Us vs Them",
        "prompt": (
            "A square 1:1 ad with a clean vertical 50/50 split. LEFT half "
            "background: soft cool grey #E8E8E8, label-style 'PHARMACY "
            "MILK THISTLE' header in small cap sans-serif at top, then a "
            "generic brown HDPE supplement bottle (CVS-style) with plain "
            "white label reading 'MILK THISTLE — 30% silymarin', positioned "
            "centered. Below it, three red X marks next to small "
            "lowercase items: \"under-standardised\", \"30% silymarin\", "
            "\"often unverified\". RIGHT half background: warm off-white "
            "#F8F4EC, label header 'LIVERZEN' in small cap sans-serif at "
            "top, then the provided product reference image of the LiverZen "
            "bottle centered. Below it, three muted-green checkmarks next "
            "to small lowercase items: \"fully standardised\", \"80% "
            "silymarin\", \"third-party tested\". A thin vertical rule "
            "down the middle. Across the very bottom of the full frame, "
            "in a deep navy band, centered serif text reads exactly: "
            "\"Why the bottle from CVS didn't work.\" "
            + PRODUCT_RULE + CLOSER
        ),
    },
    # ──────────── Ad 3: Hero + Stat Bar (Template 35) ────────────
    {
        "id": "03-hero-80-percent-stat",
        "aspect_ratio": "4:5",
        "template": "35 — Hero + Stat Bar",
        "prompt": (
            "A 4:5 portrait ad. Background: soft warm gradient from "
            "buttercream #F5EFE3 at top to muted sage #C9D6BD at bottom. "
            "The provided product reference image of the LiverZen bottle "
            "is positioned slightly left-of-center, occupying about 55% of "
            "the frame's height, with a soft natural drop shadow beneath. "
            "Scattered around the base of the bottle: a few real milk "
            "thistle seeds and one fresh milk thistle flower head (purple "
            "spikes), photographed naturalistically. To the right of the "
            "bottle, in clean serif typography, a single huge number "
            "\"80%\" in deep forest green, beneath it in smaller sans "
            "all-caps text: \"STANDARDISED SILYMARIN\". Below those, a "
            "thin horizontal rule and a single line of italic serif text "
            "reads exactly: \"the version your doctor probably takes.\" "
            "No other text. No logos. " + PRODUCT_RULE + CLOSER
        ),
    },
    # ──────────── Ad 4: Stat Callout / lifestyle (Template 26) ────────────
    {
        "id": "04-stat-callout-7-weeks",
        "aspect_ratio": "4:5",
        "template": "26 — Stat Callout",
        "prompt": (
            "A 4:5 portrait ad. Top 65% of the frame: a hyper-realistic "
            "iPhone-style photo of a moody late-evening American kitchen "
            "scene. A short rocks glass with two fingers of bourbon and one "
            "ice cube on a worn butcher-block counter, with the provided "
            "product reference image of the LiverZen bottle standing "
            "naturally beside the glass. Warm tungsten pendant light "
            "overhead, dim background blurred. The mood is calm — end of a "
            "long day, not a problem ad. "
            "Bottom 35% of the frame: a flat band in deep navy #14202E. "
            "Centered in the band, a serif headline in cream off-white "
            "reads exactly: \"ALT back to normal in 7 weeks.\" "
            "Beneath it, smaller sans-serif italic in muted gold reads "
            "exactly: \"Same bourbon. Same 60-hour weeks. One thing "
            "different.\" No other text. No logos. "
            + PRODUCT_RULE + CLOSER
        ),
    },
    # ──────────── Ad 5: Advertorial / editorial portrait (Template 20) ────────────
    {
        "id": "05-advertorial-editorial-portrait",
        "aspect_ratio": "1:1",
        "template": "20 — Advertorial",
        "prompt": (
            "A square 1:1 editorial-style ad. The frame is divided 60/40 "
            "horizontally. TOP 60%: a moody hyper-realistic photo of a "
            "60-something American man at his kitchen table at dusk, "
            "looking down thoughtfully at a piece of paper in his hand "
            "(implied bloodwork results, not legible). Short grey hair, "
            "weathered face, faded chambray work shirt. Soft warm pendant "
            "light from above-left, deep shadows, very low-key. "
            "Documentary, real, no smoothing. Background blurred kitchen. "
            "BOTTOM 40%: a flat block of warm off-white #F5EFE3. Across "
            "this block, a centered serif editorial headline in deep "
            "charcoal reads exactly, line-broken naturally over three "
            "lines: \"I'd written off every supplement on the shelf. "
            "Then my doctor told me what HE takes.\" Below the headline, "
            "a thin charcoal horizontal rule and a single small sans-serif "
            "line in muted forest green: \"Read the full story →\" "
            "No other text, no logos, no product visible in this ad — "
            "the curiosity gap is the hook. " + CLOSER
        ),
        # No product ref needed for this one — pure editorial hook
        "use_product_ref": False,
    },
]


def gen_one(entry):
    name = entry["id"]
    dest = OUT / f"{name}.png"
    if dest.exists() and dest.stat().st_size > 100_000:
        print(f"[skip ] {name}")
        return {"id": name, "ok": True, "skipped": True}
    t0 = time.time()
    use_ref = entry.get("use_product_ref", True)
    print(f"[start] {name}  ratio={entry['aspect_ratio']}  ref={use_ref}")
    args = {
        "prompt": entry["prompt"],
        "aspect_ratio": entry["aspect_ratio"],
        "num_images": 1,
        "output_format": "png",
        "resolution": "2K",
        "safety_tolerance": "5",
    }
    if use_ref:
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
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(gen_one, p): p["id"] for p in PROMPTS}
        for fut in as_completed(futs):
            results.append(fut.result())
    print("\n=== SUMMARY ===")
    for r in results:
        flag = "OK " if r.get("ok") else "FAIL"
        print(f"  {flag}  {r['id']}: {r.get('path') or r.get('err','')}")


if __name__ == "__main__":
    main()
