#!/usr/bin/env python3
"""
Generate the doctor-consult image for the advertorial — replaces the
supplement-facts panel image after "What he told me next."
Hyper-realistic clinic scene, GP and patient.
"""

import os
import sys
import time
import requests
import fal_client
from pathlib import Path
from dotenv import load_dotenv

PROJECT = Path(__file__).resolve().parent
load_dotenv(Path("/Users/jaymilne/A/.env"))
FAL_KEY = os.getenv("FAL_KEY")
if not FAL_KEY:
    sys.exit("ERROR: FAL_KEY missing")
os.environ["FAL_KEY"] = FAL_KEY

OUT = PROJECT / "assets" / "generated" / "article-3-doctor-consult.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

PROMPT = (
    "Hyper-realistic editorial photo, 16:9 horizontal. Inside a calm, "
    "modern American doctor's consulting room with soft natural light "
    "from a window. Mid-afternoon warmth. In the foreground, a "
    "55-year-old white American man in a navy work shirt sits in a "
    "patient chair, leaning slightly forward, attentive — relaxed body "
    "language, no fear, no medical drama. Across from him, a 50s "
    "American family-practice doctor in a pale blue button-up with a "
    "stethoscope around the neck, mid-conversation, holding a tablet "
    "casually, gesturing with one hand. A laptop and a small bottle of "
    "supplements sit on the desk between them, OUT OF SHARP FOCUS. "
    "Shot on a Canon R5 with an 85mm lens at f/2.0. Documentary "
    "photojournalism feel. Visible skin texture and pores. "
    "Cinematic depth of field, background softly blurred — clinic "
    "shelves with framed credentials. NO text, NO logos, NO overlays, "
    "NO captions. Editorial, real, unstaged."
)

def main():
    if OUT.exists() and OUT.stat().st_size > 100_000:
        print(f"[skip] {OUT.name} exists ({OUT.stat().st_size // 1024}KB)")
        return
    t0 = time.time()
    print(f"[start] generating {OUT.name}")
    result = fal_client.subscribe(
        "fal-ai/nano-banana-2",
        arguments={
            "prompt": PROMPT,
            "aspect_ratio": "16:9",
            "num_images": 1,
            "output_format": "png",
            "resolution": "2K",
            "safety_tolerance": "5",
        },
    )
    url = result["images"][0]["url"]
    r = requests.get(url, timeout=180, stream=True)
    r.raise_for_status()
    with open(OUT, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"[done] {OUT.name} ({time.time()-t0:.1f}s, {OUT.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    main()
