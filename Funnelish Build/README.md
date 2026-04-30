# LiverZen — Funnelish Build

Spin-up kit for new Funnelish landing pages. Ported from the Restural
white-medical variant (`no-lab-white.html`) with brand-specific bits tokenized
out so you can drop your own copy/assets in.

## Layout

```
LiverZen/Funnelish Build/
├── README.md                          ← you are here
├── Pages/
│   └── template.html                  ← tokenized landing-page skeleton
└── scripts/
    ├── tokenize_from_restural.py      ← regenerates template.html from source
    └── (image-gen scripts copied below)
```

## How a Funnelish landing page is built

Funnelish takes a single self-contained HTML blob (CSS + markup + JS inline)
and renders it inside its page builder. The build pattern from Restural:

1. **One file, no external deps.** All CSS lives in a single `<style>` block.
   All JS at the bottom in `<script>`. Only Google Fonts is imported. No
   bundlers, no React, no asset pipeline.
2. **CSS namespace prefix** (`lp-`) on every class so styles can't collide
   with whatever Funnelish injects around the page.
3. **`{{SHOPIFY_CART_PERMALINK}}`** is the Funnelish-aware token — every
   primary CTA points to it, and Funnelish substitutes the right cart
   permalink at render time. Keep all CTAs pointing there.
4. **Hosted assets.** Images/videos are loaded from a CDN (Shopify, Replo,
   anything). Tokens like `{{IMG_HERO_PRODUCT}}` mark where each asset goes;
   replace them with a CDN URL once the assets are uploaded.
5. **Countdown timers, sticky bar, FAQ, carousel, review tabs** are all
   inline vanilla JS — no jQuery. Each lives in its own IIFE in the script
   block at the bottom.
6. **Mobile-first sticky CTA** appears after the hero scrolls offscreen
   (mobile only) and disappears near the footer.

## Page section flow (top → bottom)

| # | Section | Job to be done |
|---|---|---|
| 1 | Topbar | Free-shipping offer + countdown timer |
| 2 | Hero | Headline, sub, social-proof avatars, CTA, rotating carousel, hero image |
| 3 | Marquee #1 | Reassurance loop (free shipping, guarantee, customer count) |
| 4 | Problem | Why the audience is stuck — names the pain, sets up the belief |
| 5 | Belief | "Here's what we believe" — repositions the problem so the product makes sense |
| 6 | Article | Long-form mechanism explainer with stat panel and pull-quote |
| 7 | Timeline | What to expect at week 1 / 2-3 / month 1 / 2 / 3 / 6+ |
| 8 | How To Use | 3-step routine with looping product videos |
| 9 | Mechanism Comparison | 6 stat cards — why this beats the alternatives |
| 10 | Scarcity | "Inventory allocated monthly" framing |
| 11 | Social Proof | 4 FB-style review screenshots |
| 12 | Founder | "Why we built it" + ingredient grid |
| 13 | Badges | The 4-icon promise grid |
| 14 | Marquee #2 | Sale-ends loop |
| 15 | Pricing | 3-month autoship (featured) + 1-month, with countdown |
| 16 | Trustpilot | Rating bars + 9 tabbed reviews |
| 17 | FAQ | 13 expandable questions |
| 18 | Marquee #3 | Guarantee strip |
| 19 | Final CTA | Big closer with product shot |
| 20 | Footer | Disclaimer + copyright |
| 21 | Sticky bottom bar | Mobile-only persistent CTA |

## How to populate

1. Open `Pages/template.html`.
2. Find/replace the brand identity tokens in this order:
   - `{{BRAND_NAME}}` → e.g. `LiverZen`
   - `{{PRODUCT_NAME}}` → your product name
   - `{{PRODUCT_NAME_UPPER}}` → uppercase product name (used in CTA buttons)
3. Replace stats, prices, support email, founder name (see glossary below).
4. Generate or upload your image assets, then replace the `{{IMG_*}}` and
   `{{VIDEO_*}}` tokens with CDN URLs.
5. Rewrite the prose paragraphs section by section. The original Restural
   copy is left in place so you can see the intended structure, word count,
   and tone — overwrite each block with your own.
6. Paste the final HTML into Funnelish's Custom HTML widget.

## Token glossary

### Brand identity
| Token | What it is | Example |
|---|---|---|
| `{{BRAND_NAME}}` | Company name shown in logo, footer, copy | `LiverZen` |
| `{{PRODUCT_NAME}}` | Product name | `LiverZen Cleanse` |
| `{{PRODUCT_NAME_UPPER}}` | Same, uppercase, used in CTA labels | `LIVERZEN CLEANSE` |
| `{{PAGE_TITLE}}` | `<title>` tag | `LiverZen — Liver Detox Coffee Ritual` |
| `{{FOUNDER_FULL_NAME}}` | Used in founder section + product imagery | `Dr. Sarah Chen` |
| `{{SUPPORT_EMAIL}}` | Footer + FAQ contact link | `help@liverzen.com` |
| `{{SHOPIFY_CART_PERMALINK}}` | Funnelish substitutes at render — leave as-is in CTAs | _(don't replace)_ |

### Mechanism / ingredient
| Token | What it is |
|---|---|
| `{{KEY_INGREDIENT}}` | Lead ingredient, title case (e.g. `Milk Thistle`) |
| `{{KEY_INGREDIENT_LC}}` | Lowercase variant for mid-sentence use (e.g. `milk thistle`) |
| `{{KEY_INGREDIENT_FORMAL}}` | Formal name for ingredient grid (e.g. `Milk Thistle Extract`) |
| `{{KEY_INGREDIENT_FORMAL_LONG}}` | Same with descriptor (e.g. `Milk Thistle herb`) |
| `{{KEY_COMPOUNDS}}` | Active compounds (e.g. `silybin and silymarin`) |
| `{{MECHANISM_FULL}}` | Mechanism in plain English (e.g. `Glutathione Synthesis`) |
| `{{MECHANISM_ABBR}}` | Abbreviation used in the comparison grid (e.g. `GSH`) |

### Social proof / stats
| Token | Example |
|---|---|
| `{{CUSTOMER_COUNT}}` | `12,000+` |
| `{{REVIEW_COUNT}}` | `12,038` |
| `{{RATING_SCORE}}` | `4.7` |
| `{{ORDERS_TODAY}}` | `4,014` (live counter) |
| `{{CLINIC_COUNT_LABEL}}` | `40 hepatology clinics` |
| `{{STUDY_PARTICIPANTS_LABEL}}` | `520 patients` |
| `{{STUDY_PARTICIPANTS_CLINICAL_LABEL}}` | `520 clinical participants` |
| `{{GUARANTEE_DAYS}}` | `365` |

### Pricing
| Token | Example |
|---|---|
| `{{PRICE_3MO_OLD}}` | `$179.85` (strike-through) |
| `{{PRICE_3MO_NEW}}` | `$119.85` |
| `{{PRICE_3MO_PER_DAY}}` | `$1.33/day` |
| `{{PRICE_1MO_OLD}}` | `$59.95` |
| `{{PRICE_1MO_NEW}}` | `$49.95` |
| `{{PRICE_1MO_PER_DAY}}` | `$1.66/day` |
| `{{BONUS_GUIDE_VALUE}}` | `$19` (value of free guide bonus) |

### Images (need CDN URLs)
| Token | What goes here |
|---|---|
| `{{IMG_HERO_PRODUCT}}` | Hero arch product shot (4:5 portrait) |
| `{{IMG_HERO_AVATAR_1..4}}` | Tiny circular customer avatars in hero |
| `{{IMG_HERO_CAROUSEL_1..5}}` | Square customer headshots in rotating carousel |
| `{{IMG_PROBLEM_PLATEAU}}` | Problem section — frustrated/stuck imagery |
| `{{IMG_FOUNDER_HOLDING_PRODUCT}}` | Founder portrait holding the product |
| `{{IMG_PRODUCT_CLOSEUP}}` | Product close-up (used in belief + final CTA) |
| `{{IMG_FOUNDER_LIFESTYLE}}` | Founder lifestyle/workspace shot |
| `{{IMG_STATS_CARD_1..6}}` | 6 illustrated stat-card icons (mechanism comparison) |
| `{{IMG_PROMISE_1..4}}` | 4 circular promise badges |
| `{{IMG_BUNDLE_SCARCITY}}` | Product bundle shot for scarcity strip |
| `{{IMG_FB_REVIEW_1..4}}` | Screenshot-style FB/IG review images |
| `{{IMG_PRICING_3PACK}}` | 3-month bundle product render |
| `{{IMG_PRICING_1PACK}}` | 1-month single-box render |
| `{{IMG_HOWTO_DRINK}}` | Drinking the product (also used as pricing thumbnail) |
| `{{IMG_HOWTO_OPEN}}` | Opening the sachet |
| `{{IMG_PRICING_INGREDIENTS}}` | Ingredient layout image (pricing thumb) |
| `{{IMG_REVIEW_AVATAR_1..9}}` | 9 amateur-feeling customer profile photos |

### Videos (looping product clips, MP4)
| Token | What goes here |
|---|---|
| `{{VIDEO_PROBLEM_LIVED_EXPERIENCE}}` | Lifestyle clip showing the audience problem |
| `{{VIDEO_ARTICLE_MECHANISM}}` | Animation of the biological mechanism |
| `{{VIDEO_ARTICLE_INGREDIENT}}` | Hero ingredient close-up loop |
| `{{VIDEO_ARTICLE_TRIAL}}` | Patients/clinical context clip |
| `{{VIDEO_HOWTO_STEP_1..3}}` | 3 short looping clips of the product routine |

## Re-running the tokenizer

If the Restural source changes and you want to re-pull a fresh template,
run:

```bash
python3 scripts/tokenize_from_restural.py
```

This overwrites `Pages/template.html`. Edit the `SUBS` list in the script
to add/remove substitutions.

## Image-generation scripts

Restural generated all its product/avatar/icon assets with `fal-ai/nano-banana-pro`.
The scripts in `scripts/` are copies of those, with brand-specific prompts
left in place — edit the `PROMPT` / `STYLE` / `PROFILES` constants to match
LiverZen's palette and product before running. Each script needs `FAL_KEY`
in your environment (or in `~/A/.env`).

| Script | Generates |
|---|---|
| `gen_doctor_holding_box.py` | Founder portrait holding the product |
| `gen_doctor_portrait.py` | Founder headshot |
| `gen_product_1box_cream.py` | Single-box product render |
| `gen_product_3pack.py` | 3-pack bundle render |
| `gen_promise_icons.py` | The 4 circular promise badges |
| `gen_review_avatars.py` | 9 amateur-feeling customer profile photos |
| `gen_review_photos.py` | Customer lifestyle photos |
| `gen_stats_cards.py` | 6 mechanism-comparison stat icons |

The helper `_rewrite_scripts.py` is the one-shot that pulled fresh copies
out of Restural and tokenized them. Re-run it if Restural's scripts evolve
and you want to refresh the LiverZen versions.
