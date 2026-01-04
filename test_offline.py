from __future__ import annotations

import json
from pathlib import Path

from fetch_products import _extract_products, to_json
from build_page import render_rows, HTML_TEMPLATE, PAGE_TITLE, PAGE_DESC, _html_escape
from datetime import datetime, timezone


def main() -> None:
    resp = json.loads(Path("sample_response.json").read_text(encoding="utf-8"))
    products = _extract_products(resp)
    payload = to_json(products)

    html = HTML_TEMPLATE.format(
        title=_html_escape(PAGE_TITLE),
        desc=_html_escape(PAGE_DESC),
        h1=_html_escape(PAGE_TITLE),
        pdesc=_html_escape(PAGE_DESC),
        updated=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        rows=render_rows(payload),
    )
    Path("index.offline.html").write_text(html, encoding="utf-8")
    print("Wrote index.offline.html with", len(payload), "rows")


if __name__ == "__main__":
    main()
