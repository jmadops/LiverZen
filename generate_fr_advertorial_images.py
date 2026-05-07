#!/usr/bin/env python3
"""
Generate hyper-realistic, iPhone-style images for the LiverZen FR
"Worried Wife" advertorial. Uses fal.ai nano-banana-2.

Outputs land in assets/generated-fr/. Concurrent generation.
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

OUT = PROJECT / "assets" / "generated-fr"
OUT.mkdir(parents=True, exist_ok=True)

# Upload product reference once (used for the bottle comparison + product shots)
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

# Facebook profile photo style for comment avatars
FB_AVATAR_STYLE = (
    "Authentic Facebook profile photo — the kind a French woman in her 50s "
    "would actually use. NOT a professional portrait. Taken by a family member "
    "on a phone at a real location. FULL depth of field, the background must be "
    "in focus, no portrait-mode blur. Natural daylight or slightly harsh phone "
    "light. Slightly amateur framing — head a bit off-center, maybe a tiny tilt. "
    "Subject looking roughly at the camera with a real, unposed everyday smile. "
    "Everyday French middle-class clothes: simple blouse, cardigan, scarf. "
    "Natural skin texture, visible age lines, real pores. No airbrushing, no "
    "watermarks, no text overlays. 1:1 square, framed shoulders up like a real "
    "profile photo."
)

PROMPTS = [
    # ============ ARTICLE IMAGES (16:9) ============
    {
        "id": "fr-hero",
        "aspect_ratio": "16:9",
        "image_urls": [],
        "prompt": (
            "A French country kitchen at night, around 9pm. A stemmed wine glass "
            "holding a generous pour of red Bordeaux wine sits on a worn wooden "
            "kitchen table, the glass slightly out of focus. A woman in her early "
            "50s — Catherine, French, shoulder-length brown hair with subtle "
            "grey, wearing a simple cardigan — visible from across the table, "
            "out of focus, hands resting near a folded napkin. Warm pendant "
            "light overhead casts long shadows. A cleared dinner plate just "
            "visible at the edge of frame. An old wooden chair in the soft "
            "background blur. Mood: end of a long day, quiet worry. Shallow "
            "depth of field, focus on the wine glass on the table. "
            + IPHONE_STYLE
        ),
    },
    {
        "id": "fr-article-1",
        "aspect_ratio": "16:9",
        "image_urls": [],
        "prompt": (
            "Half-empty wine glass with red Bordeaux wine on a cleared French "
            "dinner table. Late evening, around 9:30pm. Crumbs on the wood, a "
            "folded cloth napkin, the corner of an empty white dinner plate "
            "with a fork resting on it. Warm overhead lighting from a "
            "Mediterranean-style pendant lamp. The wine glass stem is slightly "
            "smudged with fingerprints. In the soft background blur: a stone "
            "wall, a wooden cabinet, and the edge of an old French armoire. "
            "Composition feels like the photo was taken just after dinner, "
            "from a wife's perspective sitting across the table. "
            + IPHONE_STYLE
        ),
    },
    {
        "id": "fr-article-2",
        "aspect_ratio": "16:9",
        "image_urls": [],
        "prompt": (
            "Top-down close-up of a printed French bilan hépatique (liver panel) "
            "lab results page on a wooden kitchen table. The paper shows liver "
            "enzyme results in printed serif text in French: ASAT, ALAT, GGT, "
            "Bilirubine. The 'GGT' (Gamma-GT) row stands out — circled in blue "
            "ballpoint pen with visible pen indentation in the paper. The GGT "
            "value reads '142 UI/L'. Reference range column shows '< 55 UI/L'. "
            "French laboratory header at top reads 'LABORATOIRE D'ANALYSES "
            "MÉDICALES'. Patient name area shows 'PATRICK M.'. Slight angle, "
            "not perfectly aligned, as if just dropped on the table. Soft "
            "afternoon window light from upper-left, gentle shadow. A reading "
            "glasses and a half-drunk café crème mug visible at the frame edge. "
            "Real paper texture, slight crease. "
            + IPHONE_STYLE
        ),
    },
    {
        "id": "fr-article-3",
        "aspect_ratio": "16:9",
        "image_urls": [],
        "prompt": (
            "Close-up of a milk thistle plant in full bloom (Silybum marianum) "
            "growing in a French country garden — distinctive purple-pink "
            "thistle flower heads with spiky green bracts and silvery-veined "
            "leaves. Soft morning light, slight dew. To the right side of the "
            "frame, a small open glass dish holding a few harvested milk thistle "
            "seeds and an open green capsule. Out-of-focus background: a stone "
            "garden wall and other herbs. The composition feels educational but "
            "natural, like a French herbalist took the photo. "
            + IPHONE_STYLE
        ),
    },
    {
        "id": "fr-article-4",
        "aspect_ratio": "16:9",
        "image_urls": [],
        "prompt": (
            "Side-by-side comparison of two supplement bottles on a marble French "
            "kitchen counter. LEFT: a generic French pharmacy-style brown plastic "
            "bottle with a basic white-and-green label. The label reads in clear "
            "French sans-serif: 'CHARDON-MARIE' as the main name, with smaller "
            "text below: '30% silymarine'. RIGHT: a clean modern white bottle "
            "with a green honeycomb pattern (LiverZen-style) — its label clearly "
            "shows 'CHARDON-MARIE 80% SILYMARINE STANDARDISÉE'. Both bottles at "
            "the same height, soft daylight from a window. Natural shadows. "
            "Honest, documentary product comparison, not a glossy studio shot. "
            + IPHONE_STYLE
        ),
    },
    {
        "id": "fr-article-5",
        "aspect_ratio": "16:9",
        "image_urls": [PRODUCT_URL],
        "prompt": (
            "A modern French kitchen counter shelf in the morning. The reference "
            "image shows the LiverZen bottle exactly — match it precisely, do not "
            "redesign. The LiverZen bottle (white with green honeycomb pattern) "
            "sits on a small wooden tray next to other supplements: a glass jar "
            "of magnesium tablets, a small vitamin D bottle, a French "
            "moisturizer tube. Beside the tray: a glass of water and a small "
            "espresso cup with a steaming café. Soft morning light from the "
            "window. The shelf has a cookbook in French and a wooden spoon "
            "leaning. Honest documentary kitchen scene. "
            + IPHONE_STYLE
        ),
    },
    {
        "id": "fr-article-6",
        "aspect_ratio": "16:9",
        "image_urls": [],
        "prompt": (
            "Close-up top-down of two French bilan hépatique (liver panel) lab "
            "results pages laid side by side on a wooden kitchen table. LEFT "
            "page (older, slightly yellowed): GGT row reads '142 UI/L' "
            "highlighted in blue pen. RIGHT page (fresh, bright white): GGT row "
            "reads '47 UI/L' circled in green pen. Both pages show 'Patient: "
            "PATRICK M.' in the header. Reference range column shows "
            "'< 55 UI/L' on both. The contrast between the two values is "
            "obvious. Soft afternoon window light. A pair of reading glasses "
            "and a half-empty espresso cup at the frame edge. Real paper "
            "texture, slight curl. "
            + IPHONE_STYLE
        ),
    },
    {
        "id": "fr-article-7",
        "aspect_ratio": "16:9",
        "image_urls": [],
        "prompt": (
            "Three candid Facebook-profile-style photos of French women in "
            "their early 50s, displayed as a horizontal triptych. LEFT: Sylvie, "
            "54, brown hair with grey strands, in a Lyon market, with bright "
            "fruit stalls behind her. CENTER: Isabelle, 49, blonde hair pinned "
            "back, wearing a navy blazer, in a Bordeaux home with bookshelf "
            "behind. RIGHT: Nathalie, 56, dark hair cut short, wearing a "
            "cream blouse, on a balcony in suburban Paris with apartment "
            "buildings behind. All three women in natural daylight, real "
            "expressions — not posed. Real skin texture. Composition reads "
            "like three real Facebook photos placed beside each other. "
            + IPHONE_STYLE
        ),
    },

    # ============ TESTIMONIAL GOLD CARD AVATARS (4:3) ============
    {
        "id": "fr-testimonial-sylvie",
        "aspect_ratio": "4:3",
        "image_urls": [],
        "prompt": (
            "A candid head-and-shoulders portrait of a 54-year-old French "
            "woman in Lyon. Brown hair with subtle grey strands, just past the "
            "shoulder, no glasses. Warm hazel eyes, faint laugh lines. Wearing "
            "a simple beige cardigan over a white blouse. Standing in her "
            "kitchen — behind her you can see French country tiles, a wooden "
            "table edge with a basket of bread, a window with morning light. "
            "She's looking slightly off-camera, a small natural smile, "
            "mid-thought. Honest unposed feel — taken by her daughter on a "
            "phone. No skin smoothing, real pores, real age lines. "
            + IPHONE_STYLE
        ),
    },
    {
        "id": "fr-testimonial-isabelle",
        "aspect_ratio": "4:3",
        "image_urls": [],
        "prompt": (
            "A candid head-and-shoulders portrait of a 49-year-old French "
            "woman in Bordeaux. Honey-blonde hair pinned back loosely, a few "
            "strands escaping. Blue-grey eyes, light freckles, light makeup. "
            "Wearing a navy blazer over a striped Breton top. Sitting at a "
            "modern kitchen island — behind her a Bordeaux apartment with "
            "white walls, a small bookshelf, late-morning daylight through "
            "tall windows. Slight half-smile, looking just past camera, "
            "thoughtful. Real, no smoothing, slight under-eye softness, "
            "natural skin texture. "
            + IPHONE_STYLE
        ),
    },
    {
        "id": "fr-testimonial-nathalie",
        "aspect_ratio": "4:3",
        "image_urls": [],
        "prompt": (
            "A candid head-and-shoulders portrait of a 56-year-old French "
            "woman on the small balcony of her suburban Paris apartment. "
            "Short dark brown hair, a few greys, simple silver earrings. "
            "Wearing a cream cotton blouse with the top button undone. Late "
            "afternoon golden light from the side. Behind her: blurred but "
            "visible Parisian banlieue apartment buildings, an iron balcony "
            "railing with a few potted geraniums. Natural unposed expression "
            "— she's looking at the camera with a small smile, like her "
            "husband took the photo. Honest face — real pores, real lines, "
            "no retouching. "
            + IPHONE_STYLE
        ),
    },

    # ============ SIDEBAR COMPARISON (4:3) ============
    {
        "id": "fr-sidebar-comparison",
        "aspect_ratio": "4:3",
        "image_urls": [PRODUCT_URL],
        "prompt": (
            "Three supplement bottles in a clean row on an off-white French "
            "marble kitchen counter, soft daylight from a window on the left. "
            "LEFT bottle: a generic French pharmacy-style brown plastic bottle "
            "with a plain white label, 'CHARDON-MARIE' in block lettering, "
            "small subtext '30% silymarine'. "
            "MIDDLE bottle: a slightly cleaner pharmacy-brand white plastic "
            "bottle with a beige label, 'CHARDON-MARIE EXTRAIT' header, small "
            "subtext '50% silymarine'. "
            "RIGHT bottle: USE THE PROVIDED REFERENCE IMAGE EXACTLY — this is "
            "the LiverZen bottle, white with green honeycomb pattern, label "
            "showing '80% SILYMARINE'. Match it precisely, do not redesign. "
            "All three roughly the same height. The right (LiverZen) bottle is "
            "subtly forward, in sharper focus. Soft natural shadows beneath "
            "each bottle. Honest documentary product comparison, not a glossy "
            "studio shot. "
            + IPHONE_STYLE
        ),
    },

    # ============ COMMENT AVATARS (1:1) — 10 French women ============
    {
        "id": "fr-avatar-sylvie-b",
        "aspect_ratio": "1:1",
        "image_urls": [],
        "prompt": (
            "Woman in her mid-50s, French, shoulder-length light-brown hair "
            "with grey at the temples, soft hazel eyes. Wearing a simple navy "
            "cardigan over a white blouse. Standing in front of a French "
            "village stone wall, sunlit afternoon. Slight tight-lipped smile, "
            "looking just at the camera. Background fully in focus: stone, "
            "ivy, a window shutter painted blue. "
            + FB_AVATAR_STYLE
        ),
    },
    {
        "id": "fr-avatar-marie-claude-l",
        "aspect_ratio": "1:1",
        "image_urls": [],
        "prompt": (
            "Woman in her early 60s, French, short silver bob haircut, "
            "tortoiseshell reading glasses pushed up on her head. Wearing a "
            "rust-colored knit pullover and a small gold necklace. Sitting at "
            "an outdoor café table, espresso cup in front of her. Background "
            "fully in focus: classic French café terrace with rattan chairs, a "
            "blurred-but-clear pedestrian street. Warm tight smile. "
            + FB_AVATAR_STYLE
        ),
    },
    {
        "id": "fr-avatar-florence-t",
        "aspect_ratio": "1:1",
        "image_urls": [],
        "prompt": (
            "Woman in her mid-50s, French, dark brown bobbed hair with subtle "
            "highlights, blue-grey eyes, no glasses. Wearing a soft pink "
            "blouse with a small floral print. Standing in her own garden in "
            "front of rose bushes. Sunny afternoon, in-focus garden behind her "
            "— roses, a stone path, a bit of lawn, a wooden gate. Real "
            "everyday smile, slightly self-conscious. "
            + FB_AVATAR_STYLE
        ),
    },
    {
        "id": "fr-avatar-brigitte-m",
        "aspect_ratio": "1:1",
        "image_urls": [],
        "prompt": (
            "Woman in her late 50s, French, ash-blonde hair in a chin-length "
            "bob, hazel eyes, gold hoop earrings. Wearing a cream cashmere "
            "sweater and a thin gold chain. Sitting at her kitchen table — "
            "behind her, a French country kitchen with copper pots, a wooden "
            "shelf with cookbooks, a window with white curtains. Soft morning "
            "light. Genuine warm smile. "
            + FB_AVATAR_STYLE
        ),
    },
    {
        "id": "fr-avatar-anne-d",
        "aspect_ratio": "1:1",
        "image_urls": [],
        "prompt": (
            "Woman in her early 60s, French, silver-grey hair pulled back "
            "into a low ponytail, kind brown eyes, simple silver studs. "
            "Wearing an olive-green linen shirt. Standing on the front porch "
            "of a French country home, late afternoon sun. Background fully "
            "in focus: the painted blue front door, a terracotta planter with "
            "lavender, a stone wall. Calm, slight smile. "
            + FB_AVATAR_STYLE
        ),
    },
    {
        "id": "fr-avatar-sophie-v",
        "aspect_ratio": "1:1",
        "image_urls": [],
        "prompt": (
            "Woman in her late 40s, French, long dark brown hair pulled into a "
            "loose low ponytail, light makeup, a thin gold pendant necklace. "
            "Wearing a striped Breton-style top. Sitting on a sofa in her "
            "modern apartment — behind her, a wall with framed photos, a "
            "bookshelf, a leafy houseplant. Warm afternoon daylight. Soft "
            "uncertain smile, like she's mid-conversation. "
            + FB_AVATAR_STYLE
        ),
    },
    {
        "id": "fr-avatar-catherine-m",
        "aspect_ratio": "1:1",
        "image_urls": [],
        "prompt": (
            "Woman in her early 50s, French — this is Catherine, a college "
            "teacher. Shoulder-length dark brown hair with a few greys, brown "
            "eyes, no makeup, no glasses. Wearing a soft grey cardigan over a "
            "simple navy top. Standing in her kitchen with a slightly tired "
            "but warm smile. Background fully in focus: French country "
            "kitchen with wooden cabinets, a window with herbs in pots, a "
            "stone backsplash. Soft daylight. "
            + FB_AVATAR_STYLE
        ),
    },
    {
        "id": "fr-avatar-valerie-f",
        "aspect_ratio": "1:1",
        "image_urls": [],
        "prompt": (
            "Woman in her mid-50s, French, copper-red hair cut to her "
            "shoulders, green eyes, freckles, light makeup. Wearing a "
            "burgundy turtleneck. Standing at a Parisian café terrace with "
            "the city street behind her — blurred but in focus, traditional "
            "wrought-iron café chairs, awnings, a few passersby. Cool "
            "overcast Paris daylight. Polite reserved smile. "
            + FB_AVATAR_STYLE
        ),
    },
    {
        "id": "fr-avatar-helene-p",
        "aspect_ratio": "1:1",
        "image_urls": [],
        "prompt": (
            "Woman in her mid-50s, French, salt-and-pepper hair in a casual "
            "shoulder-length cut, kind grey eyes, simple pearl earrings. "
            "Wearing a cream blouse and a thin scarf. Sitting at a long wooden "
            "dining table at a family lunch — behind her, in focus, you can see "
            "an empty plate with breadcrumbs, a wine glass, a relative's blurred "
            "shoulder. Late lunch warm light from a window. "
            + FB_AVATAR_STYLE
        ),
    },
    {
        "id": "fr-avatar-christine-r",
        "aspect_ratio": "1:1",
        "image_urls": [],
        "prompt": (
            "Woman in her early 60s, French, white hair cut short, hazel eyes, "
            "rectangular black glasses. Wearing a navy fisherman sweater. "
            "Standing in front of a French seaside village house with blue "
            "shutters. Background fully in focus: the stone wall, a window "
            "box of red geraniums, a sliver of sea. Cool coastal daylight. "
            "Genuine, slightly weather-worn smile. "
            + FB_AVATAR_STYLE
        ),
    },
    {
        "id": "fr-avatar-nicole-g",
        "aspect_ratio": "1:1",
        "image_urls": [],
        "prompt": (
            "Woman in her late 60s, French, soft grey-white hair set in a "
            "gentle wave, blue eyes, gold-rimmed reading glasses. Wearing a "
            "lavender knit cardigan and a thin gold chain. Sitting at her "
            "kitchen table — behind her, fully in focus: a French country "
            "kitchen with floral curtains, a row of mason jars on a shelf, a "
            "kettle on the stove. Soft afternoon light. Warm grandmotherly "
            "smile. "
            + FB_AVATAR_STYLE
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
    print(f"\nGenerating {len(PROMPTS)} images for FR advertorial...")
    results = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(generate_one, p): p["id"] for p in PROMPTS}
        for fut in as_completed(futs):
            results.append(fut.result())
    print("\n=== SUMMARY ===")
    ok = sum(1 for r in results if r.get("ok"))
    fail = len(results) - ok
    print(f"OK: {ok}   FAIL: {fail}")
    for r in results:
        status = "OK " if r.get("ok") else "FAIL"
        extra = r.get("path") or r.get("err", "")
        print(f"  {status}  {r['id']}: {extra}")


if __name__ == "__main__":
    main()
