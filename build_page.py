from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from fetch_products import fetch_all, to_json


PAGE_TITLE = "All DJ headphones under $100 — lowest price first"
PAGE_DESC = "Self-updating list of DJ headphones priced under $100 on Amazon US, ordered from cheapest to most expensive."
KEYWORDS = "DJ headphones"
MAX_PRICE_USD = 100.0


def _html_escape(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&#39;"))


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
    table {{ width: 100%; border-collapse: collapse; background:white; border-radius: 12px; overflow:hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.06); }}
    th, td {{ padding: 12px 10px; border-bottom: 1px solid #eee; vertical-align: middle; }}
    th {{ text-align: left; font-size: 13px; color:#444; background:#f5f5f5; }}
    td.img {{ width: 56px; }}
    td.price {{ white-space: nowrap; font-weight: 700; }}
    td.buy {{ width: 150px; text-align: right; }}
    a {{ color:#0b57d0; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .btn {{ display:inline-block; padding: 9px 12px; border:1px solid #ddd; border-radius: 10px; background:#fff; font-weight: 600; }}
    .btn:hover {{ background:#f7f7f7; text-decoration:none; }}
    footer {{ max-width: 980px; margin: 0 auto; padding: 18px 16px 40px; color:#555; font-size: 13px; }}
    footer a {{ color:#444; }}
  </style>
</head>
<body>
  <header>
    <h1>{h1}</h1>
    <p>{pdesc}</p>
    <p class="meta">Updated daily. Last build: {updated}</p>
  </header>
  <main>
    <table>
      <thead>
        <tr>
          <th></th>
          <th>Product</th>
          <th>Price</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
  </main>
  <footer>
    <p><strong>Affiliate disclosure:</strong> As an Amazon Associate, I earn from qualifying purchases.</p>
    <p><a href="privacy.html">Privacy</a> · <a href="disclosure.html">Disclosure</a></p>
  </footer>
</body>
</html>
"""


def render_rows(items: List[Dict[str, Any]]) -> str:
    if not items:
        return '<tr><td colspan="4">No items returned. Check API credentials and limits.</td></tr>'

    out = []
    for it in items:
        title = _html_escape(it.get("title", ""))
        price = _html_escape(it.get("price_display", ""))
        url = _html_escape(it.get("url", ""))
        img = it.get("image_url") or ""
        img_html = ""
        if img:
            img_html = f'<img src="{_html_escape(img)}" alt="" loading="lazy" width="48" height="48" style="object-fit:contain;">'

        out.append(
            "<tr>"
            f'<td class="img">{img_html}</td>'
            f'<td class="title"><a href="{url}" rel="nofollow sponsored">{title}</a></td>'
            f'<td class="price">{price}</td>'
            f'<td class="buy"><a class="btn" href="{url}" rel="nofollow sponsored">View on Amazon</a></td>'
            "</tr>"
        )
    return "\n".join(out)


def main() -> None:
    products = fetch_all(keywords=KEYWORDS, max_price_usd=MAX_PRICE_USD)
    payload = to_json(products)

    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    html = HTML_TEMPLATE.format(
        title=_html_escape(PAGE_TITLE),
        desc=_html_escape(PAGE_DESC),
        h1=_html_escape(PAGE_TITLE),
        pdesc=_html_escape(PAGE_DESC),
        updated=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        rows=render_rows(payload),
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
