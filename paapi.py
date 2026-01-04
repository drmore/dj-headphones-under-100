"""
Minimal Amazon Product Advertising API 5.0 client (PA-API 5.0) with SigV4 signing.

Docs:
- PA-API overview: https://webservices.amazon.com/paapi5/documentation/
- Required headers/signing: https://webservices.amazon.com/paapi5/documentation/sending-request.html
"""
from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests


def _sign(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _hash_sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class PaapiConfig:
    access_key: str
    secret_key: str
    partner_tag: str  # e.g. "yourtag-20"
    marketplace: str = "www.amazon.com"
    host: str = "webservices.amazon.com"
    region: str = "us-east-1"
    service: str = "ProductAdvertisingAPI"

    @property
    def endpoint(self) -> str:
        return f"https://{self.host}"


class PaapiError(RuntimeError):
    pass


class PaapiClient:
    def __init__(self, config: PaapiConfig, session: Optional[requests.Session] = None) -> None:
        self.config = config
        self.session = session or requests.Session()

    def _sigv4_headers(
        self,
        amz_target: str,
        payload: Dict[str, Any],
        request_path: str,
    ) -> Tuple[Dict[str, str], bytes]:
        """
        Create SigV4 Authorization header for PA-API 5.0 requests.

        Required headers per PA-API docs:
          - host
          - content-type: application/json; charset=utf-8
          - content-encoding: amz-1.0
          - x-amz-date: YYYYMMDD'T'HHMMSS'Z'
          - x-amz-target: com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems (example)
        """
        now = datetime.now(timezone.utc)
        amz_date = now.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = now.strftime("%Y%m%d")

        content_type = "application/json; charset=utf-8"
        content_encoding = "amz-1.0"
        host = self.config.host

        body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        payload_hash = _hash_sha256_hex(body)

        canonical_uri = request_path  # e.g. "/paapi5/searchitems"
        canonical_querystring = ""
        canonical_headers = (
            f"content-encoding:{content_encoding}\n"
            f"content-type:{content_type}\n"
            f"host:{host}\n"
            f"x-amz-date:{amz_date}\n"
            f"x-amz-target:{amz_target}\n"
        )
        signed_headers = "content-encoding;content-type;host;x-amz-date;x-amz-target"
        canonical_request = "\n".join([
            "POST",
            canonical_uri,
            canonical_querystring,
            canonical_headers,
            signed_headers,
            payload_hash,
        ])

        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = f"{date_stamp}/{self.config.region}/{self.config.service}/aws4_request"
        string_to_sign = "\n".join([
            algorithm,
            amz_date,
            credential_scope,
            _hash_sha256_hex(canonical_request.encode("utf-8")),
        ])

        k_date = _sign(("AWS4" + self.config.secret_key).encode("utf-8"), date_stamp)
        k_region = _sign(k_date, self.config.region)
        k_service = _sign(k_region, self.config.service)
        k_signing = _sign(k_service, "aws4_request")
        signature = hmac.new(k_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        authorization_header = (
            f"{algorithm} Credential={self.config.access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )

        headers = {
            "host": host,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "x-amz-date": amz_date,
            "x-amz-target": amz_target,
            "Authorization": authorization_header,
        }
        return headers, body

    def _post(self, path: str, target: str, payload: Dict[str, Any], timeout_s: int = 20) -> Dict[str, Any]:
        headers, body = self._sigv4_headers(target, payload, path)
        url = self.config.endpoint + path
        resp = self.session.post(url, headers=headers, data=body, timeout=timeout_s)
        if resp.status_code != 200:
            raise PaapiError(f"PA-API HTTP {resp.status_code}: {resp.text[:500]}")
        data = resp.json()
        if isinstance(data, dict) and data.get("Errors"):
            raise PaapiError(f"PA-API Errors: {json.dumps(data['Errors'], ensure_ascii=False)[:800]}")
        return data

    def search_items(
        self,
        keywords: str,
        max_price_cents: int,
        item_page: int = 1,
        item_count: int = 10,
        search_index: str = "Electronics",
        resources: Optional[List[str]] = None,
        availability: str = "Available",
    ) -> Dict[str, Any]:
        """
        PA-API SearchItems.

        Endpoint path: /paapi5/searchitems (common PA-API 5.0 pattern).
        """
        path = "/paapi5/searchitems"
        target = "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems"

        if resources is None:
            resources = [
                "ItemInfo.Title",
                "Offers.Listings.Price",
                "Offers.Listings.Availability.Message",
                "Images.Primary.Small",
            ]

        payload: Dict[str, Any] = {
            "Keywords": keywords,
            "Marketplace": self.config.marketplace,
            "PartnerTag": self.config.partner_tag,
            "PartnerType": "Associates",
            "Resources": resources,
            "SearchIndex": search_index,
            "MaxPrice": int(max_price_cents),
            "ItemPage": int(item_page),
            "ItemCount": int(item_count),
            "Availability": availability,
        }
        return self._post(path, target, payload)
