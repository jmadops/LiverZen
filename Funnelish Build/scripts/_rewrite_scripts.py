#!/usr/bin/env python3
"""
One-shot rewrite of the gen_*.py scripts copied from Restural so they:
  - point at the LiverZen folder
  - use a single OUT path (no dual repo mirror)
  - replace Restural/NeuroFuel brand mentions in prompt strings with
    generic {brand}/{product}/{key_ingredient} tokens that the user
    will fill in before running

Run once:
    python3 scripts/_rewrite_scripts.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = sorted(p for p in ROOT.glob("gen_*.py"))

# Path rewrites (do FIRST -- before brand identifier renames so they
# don't pre-empt anything inside path strings)
PATH_SUBS = [
    (
        'Path("/Users/jaymilne/A/Workspace/Client Work/Restural/Funnelish Build")',
        'Path("/Users/jaymilne/A/Workspace/Client Work/LiverZen/Funnelish Build")',
    ),
    # Restural mirrors output to a separate "Restural Pages" folder for
    # the git repo. LiverZen uses a single OUT path under Pages/images.
    (
        'OUT_SRC = ROOT / "v2-images" / "social"\n'
        'OUT_REPO = ROOT / "Restural Pages" / "v2-images" / "social"',
        'OUT = ROOT / "Pages" / "images" / "social"',
    ),
    (
        'OUT_SRC = ROOT / "v2-images" / "product"\n'
        'OUT_REPO = ROOT / "Restural Pages" / "v2-images" / "product"',
        'OUT = ROOT / "Pages" / "images" / "product"',
    ),
    (
        'OUT_SRC = ROOT / "v2-images" / "decor"\n'
        'OUT_REPO = ROOT / "Restural Pages" / "v2-images" / "decor"',
        'OUT = ROOT / "Pages" / "images" / "decor"',
    ),
    (
        'OUT_SRC = ROOT / "v2-images" / "stats"\n'
        'OUT_REPO = ROOT / "Restural Pages" / "v2-images" / "stats"',
        'OUT = ROOT / "Pages" / "images" / "stats"',
    ),
    # Reference images used by the product renderers and the founder
    # portrait — those references don't exist for LiverZen yet, so flag
    # them with a TODO. The user will swap to their own reference image
    # path before running.
    (
        'BOX_REF = ROOT / "v2-images" / "product" / "nf_product_1box_cream.png"',
        'BOX_REF = ROOT / "Pages" / "images" / "product" / "{product_box}.png"  # TODO: provide a reference shot of your product box',
    ),
    (
        'REF_IMAGE = ROOT / "v2-images" / "product" / "nf_product_catalog.png"',
        'REF_IMAGE = ROOT / "Pages" / "images" / "product" / "{product_catalog}.png"  # TODO: provide your catalog reference shot',
    ),
    (
        'DR_REF = Path(\n'
        '    "/Users/jaymilne/A/Workspace/Client Work/Restural/R Email Agent/"\n'
        '    "brand_kit/generated_images/plain_text_header/dr_jones_email_header.png"\n'
        ')',
        'DR_REF = Path("TODO_path_to_founder_reference_image.png")  # TODO: a portrait reference of your founder/spokesperson',
    ),
]

# Filename prefix: "nf_" was Restural's NeuroFuel prefix. Drop it.
FILENAME_SUBS = [
    # Specific output filenames -- mapping nf_* to the LiverZen template
    # token names so files line up with template.html out of the box.
    ('"nf_founder_dr_jones_holding_box.png"', '"founder_holding_product.png"'),
    ('"nf_product_3pack.png"', '"pricing_3pack.png"'),
    ('f"nf_review_avatar_{stem}.png"', 'f"review_avatar_{stem}.png"'),
    ('f"{stem}.png"', 'f"{stem}.png"'),  # already neutral
    ('f"nf_promise_{slot}.png"', 'f"promise_{slot}.png"'),
    ('f"nf_stats_card_{slot}.png"', 'f"stats_card_{slot}.png"'),
    # Inside review-avatars, profile stems include nf_review_avatar_* —
    # leave the stems alone since they're keys not filenames; the rename
    # happens in the f-string above.
]

# Brand-identifier rewrites in prompt strings. After this pass the prompts
# read as templates the user fills in. Order: longer first.
BRAND_PROMPT_SUBS = [
    ("Dr. Steven Jones", "{founder_name}"),
    ("Restural NeuroFuel", "{brand} {product}"),
    ("NeuroFuel", "{product}"),
    ("Restural", "{brand}"),
    ("Lion's Mane mushroom", "{key_ingredient_long}"),
    ("Lion's mane", "{key_ingredient}"),
    ("Lion's Mane", "{key_ingredient}"),
    ("lion's mane", "{key_ingredient_lc}"),
    ("stroke survivors", "{audience}"),
    ("stroke recovery", "{audience_outcome}"),
    # Restural visual system -- replaced with placeholder colour vars
    ("deep navy (#0E1F5A)", "deep {brand_primary} ({brand_primary_hex})"),
    ("warm gold (#E0A832)", "warm {brand_accent} ({brand_accent_hex})"),
    ("soft cream (#F5EFE4)", "soft {brand_neutral} ({brand_neutral_hex})"),
    ("muted sage", "muted {brand_secondary}"),
    ("Primal Queen", "{reference_brand_quality}"),
    # Specific docstring/prompt phrases that name the section
    ('Belief section ("Your Brain Doesn\'t Need More Pills")', "Belief section"),
]

# Add a top-of-file banner explaining what the user must edit
HEADER_BANNER = '''#
# ── EDIT BEFORE RUNNING ────────────────────────────────────────────────
#   1. PROMPT / STYLE / PROFILES below contain {brand}, {product},
#      {key_ingredient}, {brand_primary} placeholders -- replace with
#      LiverZen specifics.
#   2. Reference image paths marked TODO: provide your own.
#   3. Output filenames already match the {{IMG_*}} token slots used by
#      Pages/template.html.
# ───────────────────────────────────────────────────────────────────────
'''


def rewrite(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    original = text
    for needle, replacement in PATH_SUBS + FILENAME_SUBS + BRAND_PROMPT_SUBS:
        text = text.replace(needle, replacement)

    # Collapse the dual OUT_SRC/OUT_REPO write pattern down to a single
    # OUT path. Restural mirrored to a "Restural Pages" repo folder; the
    # LiverZen layout doesn't need that.
    text = text.replace("OUT_SRC", "OUT")
    # Drop the OUT_REPO mirror lines entirely. Match on full lines
    # (leading whitespace + content + trailing newline) so we don't
    # accidentally glue two statements together.
    text = re.sub(r"^[ \t]*OUT_REPO\.mkdir\(parents=True, exist_ok=True\)\n", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[ \t]*shutil\.copy2\(dest, OUT_REPO / [^)]+\)\n", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[ \t]*shutil\.copy2\(src, OUT_REPO / [^)]+\)\n", "", text, flags=re.MULTILINE)
    # Tidy up "         {OUT_REPO / ...}" trailing prints
    text = re.sub(r"\\n\s+\{OUT_REPO / [^}]+\}", "", text)
    # If shutil is no longer used, prune from imports
    if "shutil." not in text:
        text = text.replace("import os, sys, shutil, argparse", "import os, sys, argparse")
        text = text.replace("import os, sys, shutil", "import os, sys")
        text = re.sub(r"^import shutil\n", "", text, flags=re.MULTILINE)

    # Stems used as filename roots in the review-avatar profile list.
    # Drop the "nf_review_avatar_" prefix so generated filenames slot
    # straight into Pages/images/social/avatar_NN.png.
    text = text.replace('"nf_review_avatar_', '"avatar_')

    # Clean up obsolete path references inside docstrings/comments
    text = text.replace(
        "Output: /v2-images/social/nf_review_avatar_01.png ... nf_review_avatar_09.png\n"
        "        (mirrored to /{brand} Pages/v2-images/social/)",
        "Output: Pages/images/social/avatar_01.png ... avatar_09.png",
    )
    text = text.replace(
        "Saves into v2-images/decor/ (source) AND {brand} Pages/v2-images/decor/ (repo).",
        "Saves into Pages/images/decor/.",
    )
    text = text.replace(
        "Saves into v2-images/stats/ (source) AND {brand} Pages/v2-images/stats/ (git repo).",
        "Saves into Pages/images/stats/.",
    )
    text = text.replace(
        "in no-lab.html. ", "in template.html. ",
    )

    # Cosmetic: replace remaining Dr. Jones print labels with neutral wording
    text = text.replace("Uploading Dr. Jones reference", "Uploading founder reference")
    text = text.replace("Generating Dr. Jones holding the box", "Generating founder holding the product")

    # Inject the banner right after the docstring (after the first """
    # ... """ block).
    if HEADER_BANNER not in text and '"""' in text:
        match = re.search(r'^("""[\s\S]*?""")', text, flags=re.MULTILINE)
        if match:
            end = match.end()
            text = text[:end] + "\n" + HEADER_BANNER + text[end:]

    if text != original:
        path.write_text(text, encoding="utf-8")
        print(f"  rewrote: {path.name}")
    else:
        print(f"  unchanged: {path.name}")


def main():
    for s in SCRIPTS:
        rewrite(s)
    print(f"\nrewrote {len(SCRIPTS)} script(s) under {ROOT}")


if __name__ == "__main__":
    main()
