#!/usr/bin/env python3
"""
Generate 9 review-card avatar portraits for the Trustpilot-style review section
in template.html. These are shot to look like casual iPhone selfies / home-taken
profile photos rather than studio headshots — so they read as real customers,
not stock models. Target demographic: {audience} + caregivers, 55-75.

Output: Pages/images/social/avatar_01.png ... avatar_09.png
"""
#
# ── EDIT BEFORE RUNNING ────────────────────────────────────────────────
#   1. PROMPT / STYLE / PROFILES below contain {brand}, {product},
#      {key_ingredient}, {brand_primary} placeholders -- replace with
#      LiverZen specifics.
#   2. Reference image paths marked TODO: provide your own.
#   3. Output filenames already match the {{IMG_*}} token slots used by
#      Pages/template.html.
# ───────────────────────────────────────────────────────────────────────

import os
import sys
from pathlib import Path
import requests
import fal_client
from dotenv import load_dotenv

ROOT = Path("/Users/jaymilne/A/Workspace/Client Work/LiverZen/Funnelish Build")
OUT = ROOT / "Pages" / "images" / "social"

for env_path in [
    Path("/Users/jaymilne/A/Adgentiks/outreach-agent/.output"),
    Path("/Users/jaymilne/A/Adgentiks/outreach-agent/.env"),
    Path("/Users/jaymilne/A/.env"),
]:
    if env_path.exists():
        load_dotenv(env_path)
        break

FAL_KEY = os.getenv("FAL_KEY")
if not FAL_KEY:
    print("ERROR: FAL_KEY not found")
    sys.exit(1)
os.environ["FAL_KEY"] = FAL_KEY

BASE_STYLE = (
    "Authentic Facebook profile photo — the kind a parent would use. NOT a "
    "professional portrait. Taken by a family member on a phone, probably at "
    "a real event or location (backyard, patio, vacation spot, restaurant, "
    "front porch, garden, family gathering). "
    "CRITICAL: FULL depth of field — the background must be completely in "
    "focus, no bokeh, no portrait-mode blur, no shallow DOF. You can see "
    "everything behind the person clearly. "
    "Natural or mixed lighting: direct sun, overcast daylight, or the slightly "
    "harsh light a phone camera produces. Slightly amateur framing — maybe the "
    "head is a bit high or low in the frame, maybe slightly off-center, maybe "
    "a tiny tilt. Subject is looking roughly at the camera with a real, "
    "unposed, everyday smile (could be tight-lipped, could be mid-laugh, could "
    "be self-conscious). Everyday clothes: polo shirt, floral blouse, fishing "
    "vest, holiday sweater, simple cardigan, cruise-ship outfit. "
    "Natural skin texture, visible age lines, real people. No airbrushing. "
    "No watermarks, no text overlays. 1:1 square crop, framed from chest up "
    "or shoulders up like a real profile photo."
)

# 9 varied profiles — age 55-75, mixed gender, mixed ethnicity, mixed US/UK/AU feel.
# Each profile specifies the person AND a believable everyday setting.
PROFILES = [
    ("avatar_01",
     "Woman in her early 60s, shoulder-length warm-blonde hair with subtle gray strands, blue eyes, "
     "wearing a simple light-blue polo shirt. Standing in her sunny backyard in front of a flower bed "
     "on a bright afternoon. The photo was taken by her husband. You can see the lawn, a wooden fence, "
     "and part of a neighbor's house behind her — all crisp and in focus."),
    ("avatar_02",
     "Woman in her mid 60s, silver-gray hair in a short bob, tortoiseshell glasses (with a slight "
     "window reflection in one lens), wearing a floral-print blouse. Sitting on a patio chair on a "
     "wooden deck. Behind her: a patio umbrella, a BBQ grill, and green hedges — all fully in focus. "
     "Slightly overexposed from afternoon sun. Tight-lipped friendly smile."),
    ("avatar_03",
     "Man in his late 60s, salt-and-pepper hair and neat short beard, wearing a navy polo shirt with "
     "a small chest logo. Standing in front of a lake or pond on a cloudy day, holding a fishing rod "
     "tip visible in the corner of the frame. Background: crisp view of water, distant trees, a "
     "wooden dock — everything in focus. Looks like his wife took the photo."),
    ("avatar_04",
     "Woman in her late 60s, soft white hair pulled back loosely, wearing a dusty-rose blouse and a "
     "simple cross necklace. Sitting at a restaurant table — you can see a glass of iced tea, a "
     "menu, and other diners in the background, all in focus. Overhead restaurant lighting, slightly "
     "yellow tone. Warm, grandmotherly smile."),
    ("avatar_05",
     "Man in his mid 40s, short dark hair, clean shaven, wearing a casual olive-green flannel shirt. "
     "Standing in his driveway next to a parked SUV. Behind him: the garage door, a basketball hoop, "
     "a bit of neighborhood street — all crisp and in focus. Bright overcast daylight. Taken mid-step "
     "by his wife so his smile is a little caught-off-guard. Real everyday energy."),
    ("avatar_06",
     "Woman in her early 70s with shoulder-length silver hair, warm hazel eyes, wearing a soft "
     "lavender cardigan and a simple pearl necklace, standing in an English country garden. Behind "
     "her: clearly-in-focus rose bushes, a stone wall, a small wooden gate. Soft UK overcast "
     "daylight, slightly cool tone. Polite British smile."),
    ("avatar_07",
     "Woman in her late 50s, auburn-brown hair just past her shoulders, no glasses, wearing a "
     "crew-neck navy sweater. Standing in her kitchen — behind her you can see the refrigerator "
     "(covered in kid drawings and magnets), part of the stove, a coffee maker on the counter. "
     "Everything behind her in focus. Overhead kitchen lighting. Practical, slightly awkward "
     "no-nonsense smile."),
    ("avatar_08",
     "Man in his mid 60s of East Asian heritage, short graying hair, rimless glasses, wearing a "
     "quarter-zip fleece in heather gray. Standing at a family dinner — a dining table with dishes "
     "visible behind him, a hutch with family photos, a lamp. Background fully in focus. Warm "
     "indoor lighting, slight yellow tone from incandescent bulbs. Quiet closed-mouth smile."),
    ("avatar_09",
     "Man in his early 70s of Australian/European heritage, tanned skin with sun lines, short "
     "silver hair, wearing a lightweight linen shirt. Standing in front of a caravan/RV at a "
     "coastal caravan park. Behind him: the caravan door, a folding chair, a view of the ocean in "
     "the distance — all in focus. Bright Australian sunlight, slight squint. Big crinkly smile."),
]

ASPECT = "1:1"


def generate_one(stem: str, subject_prompt: str):
    prompt = subject_prompt + " " + BASE_STYLE
    print(f"\n[{stem}]", flush=True)
    print(f"  prompt: {subject_prompt[:90]}...", flush=True)
    result = fal_client.subscribe(
        "fal-ai/nano-banana-pro",
        arguments={
            "prompt": prompt,
            "aspect_ratio": ASPECT,
            "num_images": 1,
            "output_format": "png",
        },
    )
    images = result.get("images") or []
    if not images:
        print(f"  FAIL: {result}")
        return False
    url = images[0]["url"]
    print(f"  url: {url}")
    dest = OUT / f"{stem}.png"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(r.content)
    print(f"  saved: {dest}")
    return True


def main():
    print(f"Generating {len(PROFILES)} review avatars via nano-banana-pro/edit")
    ok = 0
    for stem, subject in PROFILES:
        if generate_one(stem, subject):
            ok += 1
    print(f"\nDone: {ok}/{len(PROFILES)} generated")


if __name__ == "__main__":
    main()
