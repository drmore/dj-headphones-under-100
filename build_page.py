from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


PAGE_TITLE = "All DJ headphones under $100 — lowest price first"
PAGE_DESC = (
    "Curated list of DJ headphones commonly priced under $100 on Amazon US. "
    "Because Product Advertising API access is not enabled yet, this page does not display live prices. "
    "Use the buttons to view current prices on Amazon."
)

DEFAULT_KEYWORDS = "dj headphones"
DEFAULT_MAX_PRICE_CENTS = 10000  # $100.00


def _html_escape(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&#39;"))


def load_asins(path: str = "asin_list.json") -> List[str]:
    data = json.loads(open(path, "r", encoding="utf-8").read())
    out: List[str] = []
    for row in data:
        asin = (row.get("asin") or "").strip()
        if asin and asin not in out:
            out.append(asin)
    return out


def affiliate_dp_url(asin: str, partner_tag: str) -> str:
    # Simple, robust DP URL with tracking tag
    # Example: https://www.amazon.com/dp/B000AJIF4E?tag=yourtag-20
    return f"https://www.amazon.com/dp/{asin}?tag={partner_tag}"


def affiliate_search_url(partner_tag: str, keywords: str = DEFAULT_KEYWORDS, max_price_cents: int = DEFAULT_MAX_PRICE_CENTS) -> str:
    # Search for DJ headphones under $100.
    # Note: "s=price-asc-rank" generally sorts low->high on Amazon search.
    # We include tag for attribution.
    from urllib.parse import quote_plus
    return (
        "https://www.amazon.com/s?"
        f"k={quote_plus(keywords)}"
        f"&rh=p_36%3A-{max_price_cents}"
        "&s=price-asc-rank"
        f"&tag={partner_tag}"
    )


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 0; background:#fafafa; color:#111; }}
    header {{ max-width: 980px; margin: 0 auto; padding: 28px 16px 8px; }}
    h1 {{ font-size: 28px; margin: 0 0 8px; }}
    p {{ margin: 0 0 10px; line-height: 1.4; }}
    .meta {{ color:#444; font-size: 14px; }}
    main {{ max-width: 980px; margin: 0 auto; padding: 8px 16px 32px; }}
    .card {{ background:white; border-radius: 12px; overflow:hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.06); padding: 14px; margin-bottom: 14px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 12px 10px; border-bottom: 1px solid #eee; vertical-align: middle; }}
    th {{ text-align: left; font-size: 13px; color:#444; background:#f5f5f5; }}
    td.buy {{ width: 160px; text-align: right; white-space:nowrap; }}
    a {{ color:#0b57d0; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .btn {{ display:inline-block; padding: 9px 12px; border:1px solid #ddd; border-radius: 10px; background:#fff; font-weight: 600; }}
    .btn:hover {{ background:#f7f7f7; text-decoration:none; }}
    .note {{ font-size: 14px; color:#444; }}
    footer {{ max-width: 980px; margin: 0 auto; padding: 18px 16px 40px; color:#555; font-size: 13px; }}
    footer a {{ color:#444; }}
  </style>
</head>
<body>
  <header>
    <h1>{h1}</h1>
    <p>{pdesc}</p>
    <p class="meta">Daily build: {updated}</p>
  </header>

  <main>
    <div class="card">
      <p class="note"><strong>Note:</strong> Live prices require Amazon Product Advertising API access. Until then, use the buttons below to view current prices on Amazon.</p>
      <p><a class="btn" href="{search_url}" rel="nofollow sponsored">View Amazon results under $100 (price low→high)</a></p>
    </div>

    <div class="card">
      <table>
        <thead>
          <tr>
            <th>ASIN</th>
            <th>Product link</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {rows}
        </tbody>
      </table>
    </div>
  </main>

  <footer>
    <p><strong>Affiliate disclosure:</strong> As an Amazon Associate, I earn from qualifying purchases.</p>
    <p><a href="privacy.html">Privacy</a> · <a href="disclosure.html">Disclosure</a></p>
  </footer>
</body>
</html>
"""


def render_rows(asins: List[str], partner_tag: str) -> str:
    if not asins:
        return '<tr><td colspan="3">No ASINs found. Add them to asin_list.json.</td></tr>'
    out = []
    for asin in asins:
        url = affiliate_dp_url(asin, partner_tag)
        out.append(
            "<tr>"
            f"<td>{_html_escape(asin)}</td>"
            f'<td><a href="{_html_escape(url)}" rel="nofollow sponsored">Open product</a></td>'
            f'<td class="buy"><a class="btn" href="{_html_escape(url)}" rel="nofollow sponsored">Check price</a></td>'
            "</tr>"
        )
    return "\n".join(out)


def main() -> None:
    partner_tag = os.environ.get("AMZ_PARTNER_TAG", "").strip()
    if not partner_tag:
        raise SystemExit("Missing AMZ_PARTNER_TAG. Set it as an environment variable or GitHub Actions secret.")

    asins = load_asins()
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = HTML_TEMPLATE.format(
        title=_html_escape(PAGE_TITLE),
        desc=_html_escape(PAGE_DESC),
        h1=_html_escape(PAGE_TITLE),
        pdesc=_html_escape(PAGE_DESC),
        updated=updated,
        rows=render_rows(asins, partner_tag),
        search_url=_html_escape(affiliate_search_url(partner_tag)),
    )
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    # Emit a simple JSON artifact for debugging
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump({"asins": asins, "updated": updated}, f, indent=2)


if __name__ == "__main__":
    main()
