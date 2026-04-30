#!/usr/bin/env python3
"""
Tokenize the Restural no-lab-white.html into a brand-neutral Funnelish template.

Reads the Restural source, applies ordered substitutions, writes
LiverZen/Funnelish Build/Pages/template.html.

Strategy:
  - Rename CSS prefixes (restural-lp- -> lp-, --rlp- -> --lp-) so the
    namespace is brand-neutral
  - Replace brand identifiers (Restural, NeuroFuel, founder name, key
    ingredient/mechanism, stats, prices, support email) with {{TOKENS}}
  - Replace Shopify CDN image URLs with {{IMG_<role>}} tokens
  - Leave prose paragraphs intact so the structure & word counts are visible
    -- the user overwrites them when populating

Run:
  python3 scripts/tokenize_from_restural.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(
    "/Users/jaymilne/A/Workspace/Client Work/Restural/Funnelish Build/"
    "Restural Pages/no-lab-white.html"
)
OUT = ROOT / "Pages" / "template.html"


# Ordered: longer/more-specific patterns first so they win over shorter ones.
# Each entry is (pattern, replacement, is_regex)
SUBS = [
    # ---- CSS namespace rename --------------------------------------------
    ("restural-lp-", "lp-", False),
    ("--rlp-", "--lp-", False),
    ("RESTURAL_IMG_", "IMG_", False),
    ("RESTURAL_PRICE_", "PRICE_", False),
    ("RESTURAL_URL_", "URL_", False),

    # ---- Page title / meta -----------------------------------------------
    (
        "<title>Restural NeuroFuel — Morning Coffee for Neural Recovery</title>",
        "<title>{{PAGE_TITLE}}</title>",
        False,
    ),

    # ---- Founder name (do BEFORE Restural global rename) -----------------
    ("Dr. Steven Jones", "{{FOUNDER_FULL_NAME}}", False),
    ("Dr Jones", "{{FOUNDER_LAST_NAME}}", False),

    # ---- Domain/email ----------------------------------------------------
    ("help@restural.com", "{{SUPPORT_EMAIL}}", False),

    # ---- Stats (specific numbers Restural uses repeatedly) ---------------
    ("12,038", "{{REVIEW_COUNT}}", False),
    ("12,000+", "{{CUSTOMER_COUNT}}", False),
    ("40 rehabilitation clinics", "{{CLINIC_COUNT_LABEL}}", False),
    ("520 patients", "{{STUDY_PARTICIPANTS_LABEL}}", False),
    ("520 clinical participants", "{{STUDY_PARTICIPANTS_CLINICAL_LABEL}}", False),
    ("4,014", "{{ORDERS_TODAY}}", False),
    ("4.7/5 by 12,000+ Customers", "{{RATING_SCORE}}/5 by {{CUSTOMER_COUNT}}", False),
    ("4.7", "{{RATING_SCORE}}", False),
    ("365-Day", "{{GUARANTEE_DAYS}}-Day", False),
    ("365 days", "{{GUARANTEE_DAYS}} days", False),
    ("365-day", "{{GUARANTEE_DAYS}}-day", False),
    # Generic 365 in standalone contexts (after the dashed forms above)
    ("365<br>Guarantee", "{{GUARANTEE_DAYS}}<br>Guarantee", False),

    # ---- Pricing ---------------------------------------------------------
    ("$179.85", "{{PRICE_3MO_OLD}}", False),
    ("$119.85", "{{PRICE_3MO_NEW}}", False),
    ("$59.95", "{{PRICE_1MO_OLD}}", False),
    ("$49.95", "{{PRICE_1MO_NEW}}", False),
    ("$1.33/day", "{{PRICE_3MO_PER_DAY}}", False),
    ("$1.66/day", "{{PRICE_1MO_PER_DAY}}", False),
    ("$19 value", "{{BONUS_GUIDE_VALUE}} value", False),

    # ---- Mechanism / ingredient terms ------------------------------------
    # Order: longer first
    ("hericenones and erinacines", "{{KEY_COMPOUNDS}}", False),
    ("Lion's Mane Extract", "{{KEY_INGREDIENT_FORMAL}}", False),
    ("Lion's Mane mushroom", "{{KEY_INGREDIENT_FORMAL_LONG}}", False),
    ("Lion's mane", "{{KEY_INGREDIENT}}", False),  # title-case start of sentence
    ("Lion's Mane", "{{KEY_INGREDIENT}}", False),
    ("lion's mane", "{{KEY_INGREDIENT_LC}}", False),
    ("Nerve Growth Factor (NGF)", "{{MECHANISM_FULL}} ({{MECHANISM_ABBR}})", False),
    ("Nerve Growth Factor", "{{MECHANISM_FULL}}", False),

    # ---- Hero arch image alt + CDN ---------------------------------------
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/nf_hero_powder_burst.png?v=1776580298&width=1000",
        "{{IMG_HERO_PRODUCT}}",
        False,
    ),
    (
        'alt="NeuroFuel lion\'s mane coffee with ingredient burst"',
        'alt="{{IMG_HERO_PRODUCT_ALT}}"',
        False,
    ),

    # ---- Belief / problem / article images -------------------------------
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/Section_2_1.png?v=1776507075&width=1000",
        "{{IMG_PROBLEM_PLATEAU}}",
        False,
    ),
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/nf_founder_dr_jones_holding_box.png?v=1777327635",
        "{{IMG_FOUNDER_HOLDING_PRODUCT}}",
        False,
    ),
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/nf_cuh.png?v=1774238143&width=600",
        "{{IMG_PRODUCT_CLOSEUP}}",
        False,
    ),
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/nf_content_bundle.png?v=1776580298&width=800",
        "{{IMG_BUNDLE_SCARCITY}}",
        False,
    ),
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/8_1.png?v=1773224707&width=1000",
        "{{IMG_FOUNDER_LIFESTYLE}}",
        False,
    ),

    # ---- Mechanism comparison stat-card images ---------------------------
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/nf_stats_card_ngf.png?v=1776580298&width=600",
        "{{IMG_STATS_CARD_1}}",
        False,
    ),
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/nf_stats_card_bbb.png?v=1776580299&width=600",
        "{{IMG_STATS_CARD_2}}",
        False,
    ),
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/nf_stats_card_bioav.png?v=1776580298&width=600",
        "{{IMG_STATS_CARD_3}}",
        False,
    ),
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/nf_stats_card_adherence.png?v=1776580298&width=600",
        "{{IMG_STATS_CARD_4}}",
        False,
    ),
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/nf_stats_card_synergy.png?v=1776580299&width=600",
        "{{IMG_STATS_CARD_5}}",
        False,
    ),
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/nf_stats_card_clinical.png?v=1776580298&width=600",
        "{{IMG_STATS_CARD_6}}",
        False,
    ),

    # ---- Promise badges --------------------------------------------------
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/nf_promise_clinical_natural.png?v=1776580298&width=400",
        "{{IMG_PROMISE_1}}",
        False,
    ),
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/nf_promise_noninvasive.png?v=1776580298&width=400",
        "{{IMG_PROMISE_2}}",
        False,
    ),
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/nf_promise_pillfree.png?v=1776580298&width=400",
        "{{IMG_PROMISE_3}}",
        False,
    ),
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/nf_promise_sideeffectfree.png?v=1776580298&width=400",
        "{{IMG_PROMISE_4}}",
        False,
    ),

    # ---- Pricing card images (3-pack + 1-month + thumbs) -----------------
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/nf_product_3pack.png?v=1776580299&width=600",
        "{{IMG_PRICING_3PACK}}",
        False,
    ),
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/nf_product_1box_cream.png?v=1776580298&width=600",
        "{{IMG_PRICING_1PACK}}",
        False,
    ),
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/howto_drink_25pct.png?v=1777328374",
        "{{IMG_HOWTO_DRINK}}",
        False,
    ),
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/howto_open_75pct.png?v=1777328383",
        "{{IMG_HOWTO_OPEN}}",
        False,
    ),
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/6_2_cd21c43f-2646-4d78-813e-dffeeab2ee8f.png?v=1773224707&width=1000",
        "{{IMG_PRICING_INGREDIENTS}}",
        False,
    ),

    # ---- Social proof (FB-style review screenshots) ----------------------
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/hf_20260418_102051_02df5980-1e61-455d-9797-efb9f84596a7.png?v=1776507743&width=1000",
        "{{IMG_FB_REVIEW_1}}",
        False,
    ),
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/hf_20260418_102102_ed4e539f-8b63-400b-a9ba-e0e08f09424f.png?v=1776507743&width=1000",
        "{{IMG_FB_REVIEW_2}}",
        False,
    ),
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/hf_20260418_102028_e3c44e29-7ff8-4e48-8ebd-22e4e77f24e0.png?v=1776507745&width=1000",
        "{{IMG_FB_REVIEW_3}}",
        False,
    ),
    (
        "https://cdn.shopify.com/s/files/1/0741/8282/0057/files/hf_20260418_102042_237b262e-2c37-4730-9df0-a5d3e889b9ed.png?v=1776507743&width=1000",
        "{{IMG_FB_REVIEW_4}}",
        False,
    ),

    # ---- Hero carousel avatars (Replo CDN) -------------------------------
    (
        "https://assets.replocdn.com/projects/40749ede-d98e-4bd4-a112-7c86bc47db1e/228aa8d5-1533-4cb3-a733-d0df4619d728",
        "{{IMG_HERO_AVATAR_1}}",
        False,
    ),
    (
        "https://assets.replocdn.com/projects/40749ede-d98e-4bd4-a112-7c86bc47db1e/b66cdb1b-2e13-4b42-8809-6a19518c5066",
        "{{IMG_HERO_AVATAR_2}}",
        False,
    ),
    (
        "https://assets.replocdn.com/projects/40749ede-d98e-4bd4-a112-7c86bc47db1e/be10fa9e-7d22-477c-a6a0-bb013e5ebb22",
        "{{IMG_HERO_AVATAR_3}}",
        False,
    ),
    (
        "https://assets.replocdn.com/projects/40749ede-d98e-4bd4-a112-7c86bc47db1e/dcf93927-9382-47b9-8ce7-aab92989ffae",
        "{{IMG_HERO_AVATAR_4}}",
        False,
    ),
    (
        "https://assets.replocdn.com/projects/40749ede-d98e-4bd4-a112-7c86bc47db1e/e9f9042d-7731-4a6c-9f38-a26bd87efcc8",
        "{{IMG_HERO_CAROUSEL_1}}",
        False,
    ),
    (
        "https://assets.replocdn.com/projects/40749ede-d98e-4bd4-a112-7c86bc47db1e/deedbe79-b8c8-480d-882b-bb7ac9b1f5b5",
        "{{IMG_HERO_CAROUSEL_2}}",
        False,
    ),
    (
        "https://assets.replocdn.com/projects/40749ede-d98e-4bd4-a112-7c86bc47db1e/0aa12dd6-28e4-4c29-96b8-0e9cff61caed",
        "{{IMG_HERO_CAROUSEL_3}}",
        False,
    ),
    (
        "https://assets.replocdn.com/projects/40749ede-d98e-4bd4-a112-7c86bc47db1e/05257eaf-46d3-4996-8e09-ced22c69e3a6",
        "{{IMG_HERO_CAROUSEL_4}}",
        False,
    ),
    (
        "https://assets.replocdn.com/projects/40749ede-d98e-4bd4-a112-7c86bc47db1e/b23e064b-ae17-47eb-a089-c625612b545b",
        "{{IMG_HERO_CAROUSEL_5}}",
        False,
    ),

    # ---- Trustpilot review avatars (relative paths) ----------------------
    ("v2-images/social/nf_review_avatar_01.png", "{{IMG_REVIEW_AVATAR_1}}", False),
    ("v2-images/social/nf_review_avatar_02.png", "{{IMG_REVIEW_AVATAR_2}}", False),
    ("v2-images/social/nf_review_avatar_03.png", "{{IMG_REVIEW_AVATAR_3}}", False),
    ("v2-images/social/nf_review_avatar_04.png", "{{IMG_REVIEW_AVATAR_4}}", False),
    ("v2-images/social/nf_review_avatar_05.png", "{{IMG_REVIEW_AVATAR_5}}", False),
    ("v2-images/social/nf_review_avatar_06.png", "{{IMG_REVIEW_AVATAR_6}}", False),
    ("v2-images/social/nf_review_avatar_07.png", "{{IMG_REVIEW_AVATAR_7}}", False),
    ("v2-images/social/nf_review_avatar_08.png", "{{IMG_REVIEW_AVATAR_8}}", False),
    ("v2-images/social/nf_review_avatar_09.png", "{{IMG_REVIEW_AVATAR_9}}", False),

    # ---- Video sources (Shopify) -----------------------------------------
    (
        "https://cdn.shopify.com/videos/c/o/v/6509cbc42f0f458d916d5e97f8c76552.mp4",
        "{{VIDEO_PROBLEM_LIVED_EXPERIENCE}}",
        False,
    ),
    (
        "https://cdn.shopify.com/videos/c/o/v/c49a7cf673954345bcc1d28e3938473a.mp4",
        "{{VIDEO_ARTICLE_MECHANISM}}",
        False,
    ),
    (
        "https://cdn.shopify.com/videos/c/o/v/99aa26981daf44dc9e9ee314869e824f.mp4",
        "{{VIDEO_ARTICLE_INGREDIENT}}",
        False,
    ),
    (
        "https://cdn.shopify.com/videos/c/o/v/1cbb0d464c2d43ccb407cc32448a7101.mp4",
        "{{VIDEO_ARTICLE_TRIAL}}",
        False,
    ),
    (
        "https://cdn.shopify.com/videos/c/o/v/8139901a18d449e98fd5b3a727e7fc87.mp4",
        "{{VIDEO_HOWTO_STEP_1}}",
        False,
    ),
    (
        "https://cdn.shopify.com/videos/c/o/v/8c42aed818ae4d4698c8c9ab21801f8d.mp4",
        "{{VIDEO_HOWTO_STEP_2}}",
        False,
    ),
    (
        "https://cdn.shopify.com/videos/c/o/v/45cda82ebfd14b07917c3a20f5dc60a5.mp4",
        "{{VIDEO_HOWTO_STEP_3}}",
        False,
    ),

    # ---- Brand identifiers (do LAST so they don't pre-empt URL/email subs)
    ("NeuroFuel", "{{PRODUCT_NAME}}", False),
    ("NEUROFUEL", "{{PRODUCT_NAME_UPPER}}", False),
    ("Restural", "{{BRAND_NAME}}", False),
]


def main():
    src = SRC.read_text(encoding="utf-8")
    out = src
    for needle, replacement, is_regex in SUBS:
        if is_regex:
            out = re.sub(needle, replacement, out)
        else:
            out = out.replace(needle, replacement)

    # Banner header so the user knows the file is templated
    banner = (
        "<!--\n"
        "  TEMPLATE: Funnelish landing-page skeleton, tokenized from Restural's\n"
        "  white-medical variant. See README.md for the full token glossary.\n"
        "  Copy is intentionally LEFT IN PLACE so structure & word counts are\n"
        "  visible -- overwrite the prose with your own when populating.\n"
        "-->\n"
    )
    if "<!DOCTYPE html>" in out:
        out = out.replace("<!DOCTYPE html>\n", "<!DOCTYPE html>\n" + banner, 1)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(out, encoding="utf-8")
    print(f"wrote: {OUT} ({len(out):,} chars, {out.count(chr(10)):,} lines)")

    # Sanity report
    leftover_brand = out.count("Restural") + out.count("NeuroFuel")
    leftover_prefix = out.count("restural-lp-") + out.count("--rlp-")
    print(f"  leftover Restural/NeuroFuel mentions: {leftover_brand}")
    print(f"  leftover restural-lp-/--rlp- prefix:  {leftover_prefix}")
    print(f"  unique {{TOKEN}} count:                {len(set(re.findall(r'{{[A-Z_0-9]+}}', out)))}")


if __name__ == "__main__":
    main()
