#!/usr/bin/env python3
"""
Generate a silent medical-illustration animation: healthy liver gradually
deteriorating into fatty/inflamed state. For the article-2 spot in the
LiverZen advertorial. No copy/text in frame.

Pipeline:
  1. Nano Banana 2 -> medical-illustration starter frame (16:9)
  2. Kling 2.5 image-to-video -> 5s of subtle deterioration
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

VIDEO_DIR = PROJECT / "assets" / "video"
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

FRAME_PATH = VIDEO_DIR / "liver-decline-frame.png"
VIDEO_PATH = VIDEO_DIR / "liver-decline.mp4"

FRAME_PROMPT = (
    "A clean, anatomically accurate medical illustration of a HEALTHY human "
    "liver, three-quarter angle, deep rich red-brown color with subtle "
    "burgundy undertones, smooth glossy surface with delicate hepatic vein "
    "structure faintly visible beneath. The liver sits centered in frame on "
    "a soft out-of-focus dark teal-to-charcoal gradient background, almost "
    "abstract — no medical instruments, no text, no labels, no anatomy "
    "callouts, NO COPY OR TEXT ANYWHERE. Editorial medical-illustration "
    "style — half painting, half hyper-detailed CGI rendering. Soft "
    "rim-lighting from above-left, gentle shadow beneath, slight specular "
    "highlight catching the upper curve. Cinematic depth of field. "
    "Premium pharmaceutical/biotech aesthetic — restrained, almost luxurious, "
    "definitely not gore. The liver looks alive, breathing, healthy. "
    "16:9 wide composition with the liver occupying the central 60% of frame."
)

VIDEO_PROMPT = (
    "Slow, almost imperceptible deterioration over 5 seconds. The liver "
    "gradually develops faint yellowish fatty deposits across its surface, "
    "subtle inflammation patches blooming in soft amber-orange. The deep "
    "red-brown color shifts slightly toward a duller, more muted tone. A "
    "very gentle pulsing motion, like slow breathing. Background remains "
    "still, soft teal-to-charcoal gradient. Cinematic, restrained, no abrupt "
    "movements, no text, no labels appear. Editorial medical-illustration "
    "aesthetic. Subtle camera dolly-in over the duration."
)

NEGATIVE = (
    "text, labels, captions, anatomy callouts, watermark, logo, blood "
    "splatter, gore, jerky motion, harsh cuts, low quality, distorted, "
    "warping, artifacts, surgical instruments, hands"
)


def gen_frame():
    if FRAME_PATH.exists() and FRAME_PATH.stat().st_size > 100_000:
        print(f"[skip ] frame already exists -> {FRAME_PATH.name}")
        return
    t0 = time.time()
    print(f"[start] starter frame")
    result = fal_client.subscribe(
        "fal-ai/nano-banana-2",
        arguments={
            "prompt": FRAME_PROMPT,
            "aspect_ratio": "16:9",
            "num_images": 1,
            "output_format": "png",
            "resolution": "2K",
            "safety_tolerance": "5",
        },
    )
    url = result["images"][0]["url"]
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    FRAME_PATH.write_bytes(r.content)
    print(f"[done ] frame -> {FRAME_PATH.name}  ({time.time()-t0:.1f}s)")


def gen_video():
    if VIDEO_PATH.exists() and VIDEO_PATH.stat().st_size > 100_000:
        print(f"[skip ] video already exists -> {VIDEO_PATH.name}")
        return
    print(f"[start] uploading frame to fal...")
    frame_url = fal_client.upload_file(str(FRAME_PATH))
    print(f"  -> {frame_url}")
    t0 = time.time()
    print(f"[start] kling i2v 5s")
    result = fal_client.subscribe(
        "fal-ai/kling-video/v2.5-turbo/pro/image-to-video",
        arguments={
            "prompt": VIDEO_PROMPT,
            "image_url": frame_url,
            "duration": "5",
            "aspect_ratio": "16:9",
            "negative_prompt": NEGATIVE,
            "cfg_scale": 0.5,
        },
    )
    video_url = result["video"]["url"]
    print(f"  -> {video_url}")
    r = requests.get(video_url, timeout=180, stream=True)
    r.raise_for_status()
    with open(VIDEO_PATH, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"[done ] video -> {VIDEO_PATH.name}  ({time.time()-t0:.1f}s)")


if __name__ == "__main__":
    gen_frame()
    gen_video()
    print("\n=== DONE ===")
    print(f"  Frame: {FRAME_PATH}")
    print(f"  Video: {VIDEO_PATH}")
