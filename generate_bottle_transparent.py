#!/usr/bin/env python3
"""
Strip the white background off product.png so we can float the bottle
above the comparison table on the PDP.
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

SRC = PROJECT / "assets" / "product.png"
OUT = PROJECT / "assets" / "product-transparent.png"

if OUT.exists() and OUT.stat().st_size > 50_000:
    print(f"[skip] {OUT.name} exists ({OUT.stat().st_size // 1024}KB)")
    sys.exit(0)

t0 = time.time()
print(f"[start] removing bg from {SRC.name}")

src_url = fal_client.upload_file(str(SRC))
print(f"  uploaded source -> {src_url[:80]}…")

result = fal_client.subscribe(
    "fal-ai/birefnet/v2",
    arguments={"image_url": src_url, "output_format": "png"},
)

img_url = result.get("image", {}).get("url") or result.get("images", [{}])[0].get("url")
if not img_url:
    sys.exit(f"ERROR: unexpected response shape: {result}")

r = requests.get(img_url, timeout=180, stream=True)
r.raise_for_status()
with open(OUT, "wb") as f:
    for chunk in r.iter_content(chunk_size=8192):
        f.write(chunk)

print(f"[done] {OUT.name} ({time.time()-t0:.1f}s, {OUT.stat().st_size // 1024}KB)")
