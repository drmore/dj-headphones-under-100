from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from paapi import PaapiClient, PaapiConfig


@dataclass
class Product:
    asin: str
    title: str
    price_amount: float
    price_display: str
    currency: str
    url: str
    image_url: Optional[str] = None


def _extract_products(resp: Dict[str, Any]) -> List[Product]:
    items = (((resp or {}).get("SearchResult") or {}).get("Items")) or []
    out: List[Product] = []
    for it in items:
        asin = it.get("ASIN") or ""
        title = (((it.get("ItemInfo") or {}).get("Title") or {}).get("DisplayValue")) or ""
        offers = (it.get("Offers") or {}).get("Listings") or []
        if not offers:
            continue
        price = (offers[0].get("Price") or {})
        amount = price.get("Amount")
        display = price.get("DisplayAmount") or ""
        currency = price.get("Currency") or ""

        if amount is None:
            continue

        url = it.get("DetailPageURL") or ""
        img = (((it.get("Images") or {}).get("Primary") or {}).get("Small") or {}).get("URL")

        out.append(Product(
            asin=str(asin),
            title=str(title).strip(),
            price_amount=float(amount),
            price_display=str(display),
            currency=str(currency),
            url=str(url),
            image_url=str(img) if img else None,
        ))
    return out


def fetch_all(
    keywords: str = "DJ headphones",
    max_price_usd: float = 100.0,
    max_pages: int = 10,
) -> List[Product]:
    access_key = os.environ.get("PAAPI_ACCESS_KEY", "").strip()
    secret_key = os.environ.get("PAAPI_SECRET_KEY", "").strip()
    partner_tag = os.environ.get("PAAPI_PARTNER_TAG", "").strip()

    if not (access_key and secret_key and partner_tag):
        raise SystemExit(
            "Missing secrets. Set PAAPI_ACCESS_KEY, PAAPI_SECRET_KEY, PAAPI_PARTNER_TAG as environment variables."
        )

    cfg = PaapiConfig(
        access_key=access_key,
        secret_key=secret_key,
        partner_tag=partner_tag,
        marketplace=os.environ.get("PAAPI_MARKETPLACE", "www.amazon.com"),
        host=os.environ.get("PAAPI_HOST", "webservices.amazon.com"),
        region=os.environ.get("PAAPI_REGION", "us-east-1"),
    )
    client = PaapiClient(cfg)

    max_price_cents = int(round(max_price_usd * 100))

    all_products: List[Product] = []
    seen_asin = set()

    for page in range(1, max_pages + 1):
        resp = client.search_items(
            keywords=keywords,
            max_price_cents=max_price_cents,
            item_page=page,
            item_count=10,
            search_index=os.environ.get("PAAPI_SEARCH_INDEX", "Electronics"),
            availability=os.environ.get("PAAPI_AVAILABILITY", "Available"),
        )
        prods = _extract_products(resp)

        if not prods:
            break

        for p in prods:
            if p.asin in seen_asin:
                continue
            seen_asin.add(p.asin)
            all_products.append(p)

    all_products.sort(key=lambda p: p.price_amount)
    return all_products


def to_json(products: List[Product]) -> List[Dict[str, Any]]:
    return [
        {
            "asin": p.asin,
            "title": p.title,
            "price_amount": p.price_amount,
            "price_display": p.price_display,
            "currency": p.currency,
            "url": p.url,
            "image_url": p.image_url,
        }
        for p in products
    ]


if __name__ == "__main__":
    items = fetch_all()
    print(json.dumps(to_json(items), indent=2, ensure_ascii=False))
