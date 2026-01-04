# All DJ headphones under $100 — lowest price first (No-API mode)

This repo runs **without Amazon PA-API access**. It publishes a GitHub Pages site that:
- links to a curated list of DJ headphone products (by ASIN)
- includes an Amazon search link filtered to **under $100** and sorted **price low→high**
- rebuilds once per day via GitHub Actions

## Why no prices?
Amazon requires Product Advertising API access to display live prices programmatically. Until PA-API is enabled on your Associates account, this site does not show prices on-page. Users click through to see the current price on Amazon.

## One-time setup
1. Put your ASINs in `asin_list.json` (already included).
2. Add one GitHub Actions secret:
   - `AMZ_PARTNER_TAG` (your tracking ID, e.g. `yourtag-20`)
3. Enable GitHub Pages (Deploy from branch → main → /root).
4. Run the workflow once.

## Switching to PA-API later
When you gain PA-API access, we can swap to the PA-API version to display live prices and truly sort cheapest-first on-page.
