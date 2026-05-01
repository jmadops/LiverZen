#!/usr/bin/env python3
"""
Generate 11 small candid comment avatars + 6 stylized press wordmarks
for the bourbon-confession advertorial.

Avatars: Tom W, Dave H, Greg M, Carl S, Eric T, Steve M, Jerry W
         Ben K, Ron P, Frank L, Pete R
Press: NBC, ABC, CBS, FOX, USA TODAY, FORBES (stylized typographic
       wordmarks — placeholder, not licensed real logos)
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

AV_OUT = PROJECT / "assets" / "avatars"
LOGO_OUT = PROJECT / "assets" / "press"
AV_OUT.mkdir(parents=True, exist_ok=True)
LOGO_OUT.mkdir(parents=True, exist_ok=True)

CANDID_STYLE = (
    "Hyper-realistic candid head-and-shoulders 1:1 portrait, shot on "
    "iPhone 15 Pro with available natural light. Tight crop on face "
    "and shoulders. Real, documentary, no skin smoothing — visible "
    "pores, fine lines, texture. Subject looking just past the camera "
    "with a relaxed expression. Background out-of-focus suggesting an "
    "American home interior. NO TEXT, NO LOGOS, NO OVERLAYS."
)

AVATARS = [
    {
        "id": "tom-w",
        "prompt": (
            "A 58-year-old white American man, Tom W. Salt-and-pepper "
            "hair, neatly trimmed beard, wire-frame glasses pushed up "
            "on his head. Wearing a dark heather-grey tee under an "
            "open chambray shirt. Suburban Midwestern home interior "
            "blurred behind. Slight knowing half-smile. " + CANDID_STYLE
        ),
    },
    {
        "id": "dave-h",
        "prompt": (
            "A 52-year-old Black American man, Dave H. Close-cropped "
            "hair greying at the temples, neat goatee, intelligent "
            "eyes. Wearing a dark navy crew-neck sweater. Soft warm "
            "afternoon light from a window on his left. Atlanta-style "
            "home office in the background, blurred. Mildly amused "
            "expression. " + CANDID_STYLE
        ),
    },
    {
        "id": "greg-m",
        "prompt": (
            "A 49-year-old Hispanic American man, Greg M. Dark brown "
            "hair starting to grey at the temples, clean-shaven, "
            "lined tan from outdoor work. Wearing a faded burgundy "
            "Henley shirt. Working-class Texan kitchen blurred behind. "
            "Slightly furrowed brow, looking thoughtful. " + CANDID_STYLE
        ),
    },
    {
        "id": "carl-s",
        "prompt": (
            "A 61-year-old white American man, Carl S. Mostly grey "
            "hair, clean-shaven, bushy eyebrows. Wearing a moss-green "
            "cardigan over a button-up. Soft afternoon window light, "
            "wooden bookshelf blurred behind. Looking slightly off-"
            "camera with a small warm smile. " + CANDID_STYLE
        ),
    },
    {
        "id": "eric-t",
        "prompt": (
            "A 47-year-old white American man, Eric T. Light brown "
            "hair, short stubble, blue eyes. Wearing a charcoal "
            "polo. Modern home-office background blurred behind, "
            "afternoon light. Slightly skeptical-but-open expression. "
            + CANDID_STYLE
        ),
    },
    {
        "id": "steve-m",
        "prompt": (
            "A 55-year-old white American man, Steve M. Receding "
            "sandy-blond hair greying at the temples, clean-shaven, "
            "ruddy complexion. Wearing a faded blue work jacket. "
            "Suburban garage interior blurred behind, late-afternoon "
            "warm light. Slight pragmatic smile. " + CANDID_STYLE
        ),
    },
    {
        "id": "jerry-w",
        "prompt": (
            "A 58-year-old white American man, Jerry W., owner of a "
            "small contracting business. Short grey hair, weathered "
            "tan, deep crow's feet, full grey moustache. Wearing a "
            "faded navy polo with a barely visible (intentionally "
            "blurred) embroidered logo on the chest. Outdoors at a "
            "construction job site blurred behind, late-afternoon "
            "golden-hour light. Confident, weathered, real. "
            + CANDID_STYLE
        ),
    },
    {
        "id": "ben-k",
        "prompt": (
            "A 51-year-old white American man, Ben K. Short brown "
            "hair greying at the sides, full beard with grey "
            "patches, wearing rectangular glasses. Wearing a "
            "burgundy thermal shirt. Soft window light, blurred "
            "wood-paneled wall behind. Thoughtful slight smile. "
            + CANDID_STYLE
        ),
    },
    {
        "id": "ron-p",
        "prompt": (
            "A 56-year-old white American man, Ron P. Salt-and-"
            "pepper hair pushed back, clean-shaven, friendly face "
            "with deep laugh lines. Wearing a forest-green polo. "
            "Soft afternoon light, blurred home interior with a "
            "framed family photo behind. Warm relaxed smile. "
            + CANDID_STYLE
        ),
    },
    {
        "id": "frank-l",
        "prompt": (
            "A 53-year-old white American man, Frank L. Short "
            "brown hair shaved close at the sides, clean-shaven, "
            "square jaw, slight stubble. Wearing a heather grey "
            "T-shirt. Garage/workshop background blurred behind. "
            "Slightly raised eyebrow, mildly amused. " + CANDID_STYLE
        ),
    },
    {
        "id": "pete-r",
        "prompt": (
            "A 60-year-old white American man, Pete R. Mostly grey "
            "hair receding at the temples, neatly trimmed grey "
            "beard, kind eyes behind reading glasses. Wearing a "
            "navy fleece zip-up. Cozy home den blurred behind, "
            "warm lamp light. Gentle, thoughtful expression. "
            + CANDID_STYLE
        ),
    },
]

LOGOS = [
    {
        "id": "press-nbc",
        "prompt": (
            "A clean stylized typographic wordmark image, 4:1 wide "
            "horizontal aspect. White or very light off-white "
            "background. Centered: the letters \"NBC\" in a strong, "
            "bold, geometric all-caps sans-serif typeface, deep "
            "charcoal grey #555555, rendered exactly. Slight letter-"
            "spacing for clarity. To the right of the letters, a "
            "small simple stylized peacock-feather mark in the same "
            "charcoal grey — abstract three-feather fan shape, NOT "
            "the actual NBC peacock logo. The whole composition reads "
            "like a clean editorial-style press lockup. NO OTHER TEXT, "
            "NO OTHER MARKS. Premium minimal placeholder graphic."
        ),
    },
    {
        "id": "press-abc",
        "prompt": (
            "A clean stylized typographic wordmark image, 4:1 wide "
            "horizontal aspect. White or very light off-white "
            "background. Centered: the letters \"ABC\" in a clean "
            "rounded geometric sans-serif lowercase \"abc\" inside a "
            "simple solid charcoal-grey #555555 circle (the only "
            "graphic element). Like a clean editorial-style press "
            "lockup placeholder. NO OTHER TEXT. Premium minimal."
        ),
    },
    {
        "id": "press-cbs",
        "prompt": (
            "A clean stylized typographic wordmark image, 4:1 wide "
            "horizontal aspect. White or very light off-white "
            "background. Centered: the letters \"CBS\" in a clean "
            "modernist all-caps geometric sans-serif typeface, deep "
            "charcoal grey #555555, slight letter-spacing. To the "
            "left of the letters, a simple abstract stylized eye-"
            "shape mark in the same charcoal — abstract circle-with-"
            "almond-pupil, NOT the actual CBS eye. Editorial press "
            "lockup placeholder. NO OTHER TEXT. Premium minimal."
        ),
    },
    {
        "id": "press-fox",
        "prompt": (
            "A clean stylized typographic wordmark image, 4:1 wide "
            "horizontal aspect. White or very light off-white "
            "background. Centered: the word \"FOX\" in a strong, "
            "bold, slightly compressed all-caps display sans-serif "
            "typeface, deep charcoal grey #555555. Solid, "
            "newspaper-headline weight. NO graphic mark, just "
            "type. Editorial press lockup placeholder. NO OTHER "
            "TEXT. Premium minimal."
        ),
    },
    {
        "id": "press-usa-today",
        "prompt": (
            "A clean stylized typographic wordmark image, 4:1 wide "
            "horizontal aspect. White or very light off-white "
            "background. Centered: the words \"USA TODAY\" in a "
            "modern clean all-caps editorial sans-serif typeface, "
            "deep charcoal grey #555555, slight letter-spacing, "
            "with a thin charcoal underline beneath the words. "
            "Newspaper-style. NO OTHER TEXT, NO MARKS. Editorial "
            "placeholder. Premium minimal."
        ),
    },
    {
        "id": "press-forbes",
        "prompt": (
            "A clean stylized typographic wordmark image, 4:1 wide "
            "horizontal aspect. White or very light off-white "
            "background. Centered: the word \"Forbes\" in a "
            "stately upright old-style serif typeface (looks like "
            "a magazine masthead), deep charcoal grey #555555, "
            "first letter capitalized. Editorial magazine masthead "
            "feel. NO OTHER TEXT, NO MARKS. Premium minimal "
            "placeholder."
        ),
    },
]


def gen_avatar(entry):
    name = entry["id"]
    dest = AV_OUT / f"{name}.png"
    if dest.exists() and dest.stat().st_size > 100_000:
        print(f"[skip ] av:{name}")
        return {"id": name, "ok": True, "kind": "av", "skipped": True}
    t0 = time.time()
    print(f"[start] av:{name}")
    try:
        result = fal_client.subscribe(
            "fal-ai/nano-banana-2",
            arguments={
                "prompt": entry["prompt"],
                "aspect_ratio": "1:1",
                "num_images": 1,
                "output_format": "png",
                "resolution": "2K",
                "safety_tolerance": "5",
            },
        )
    except Exception as e:
        print(f"[FAIL] av:{name}: {e}")
        return {"id": name, "ok": False, "kind": "av", "err": str(e)}
    url = result["images"][0]["url"]
    r = requests.get(url, timeout=120, stream=True)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"[done ] av:{name}  ({time.time()-t0:.1f}s)")
    return {"id": name, "ok": True, "kind": "av", "path": str(dest)}


def gen_logo(entry):
    name = entry["id"]
    dest = LOGO_OUT / f"{name}.png"
    if dest.exists() and dest.stat().st_size > 30_000:
        print(f"[skip ] logo:{name}")
        return {"id": name, "ok": True, "kind": "logo", "skipped": True}
    t0 = time.time()
    print(f"[start] logo:{name}")
    try:
        result = fal_client.subscribe(
            "fal-ai/nano-banana-2",
            arguments={
                "prompt": entry["prompt"],
                "aspect_ratio": "16:9",
                "num_images": 1,
                "output_format": "png",
                "resolution": "1K",
                "safety_tolerance": "5",
            },
        )
    except Exception as e:
        print(f"[FAIL] logo:{name}: {e}")
        return {"id": name, "ok": False, "kind": "logo", "err": str(e)}
    url = result["images"][0]["url"]
    r = requests.get(url, timeout=120, stream=True)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"[done ] logo:{name}  ({time.time()-t0:.1f}s)")
    return {"id": name, "ok": True, "kind": "logo", "path": str(dest)}


def main():
    results = []
    # Run all 17 in a single thread pool
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {}
        for a in AVATARS:
            futs[ex.submit(gen_avatar, a)] = ("av", a["id"])
        for l in LOGOS:
            futs[ex.submit(gen_logo, l)] = ("logo", l["id"])
        for fut in as_completed(futs):
            results.append(fut.result())
    print("\n=== SUMMARY ===")
    for r in results:
        flag = "OK " if r.get("ok") else "FAIL"
        print(f"  {flag}  [{r['kind']}] {r['id']}: {r.get('path') or r.get('err','')}")


if __name__ == "__main__":
    main()
