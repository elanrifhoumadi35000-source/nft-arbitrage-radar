from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
import requests

class OpenSeaError(RuntimeError):
    pass

class OpenSeaClient:
    BASE_URL = "https://api.opensea.io/api/v2"

    def __init__(self, api_key: str, request_delay_seconds: float = 0.25, timeout: int = 20):
        if not api_key or not api_key.strip():
            raise ValueError("La clé API OpenSea est vide.")
        self.api_key = api_key.strip()
        self.delay = max(0.0, float(request_delay_seconds))
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "application/json",
            "x-api-key": self.api_key,
            "user-agent": "NFT-Arbitrage-Radar/1.0"
        })

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if self.delay:
            time.sleep(self.delay)
        url = f"{self.BASE_URL}{path}"
        try:
            r = self.session.get(url, params=params or {}, timeout=self.timeout)
        except requests.RequestException as exc:
            raise OpenSeaError(f"Erreur réseau OpenSea: {exc}") from exc

        if r.status_code == 401:
            raise OpenSeaError("401 OpenSea: clé API absente ou invalide.")
        if r.status_code == 403:
            raise OpenSeaError("403 OpenSea: accès refusé pour cette clé / ressource.")
        if r.status_code == 429:
            retry_after = r.headers.get("retry-after", "?")
            raise OpenSeaError(f"429 OpenSea: limite de requêtes atteinte. Retry-After={retry_after}")
        if not r.ok:
            snippet = r.text[:500].replace("\n", " ")
            raise OpenSeaError(f"OpenSea HTTP {r.status_code}: {snippet}")

        try:
            return r.json()
        except ValueError as exc:
            raise OpenSeaError("Réponse OpenSea non JSON.") from exc

    def get_collection_listings(self, slug: str, limit: int = 20) -> List[Dict[str, Any]]:
        limit = min(max(int(limit), 1), 200)
        data = self._get(
            f"/listings/collection/{slug}/all",
            params={"limit": limit, "include_private_listings": "false"},
        )
        return list(data.get("listings") or [])

    def get_nft_offers(self, slug: str, identifier: str, limit: int = 50) -> List[Dict[str, Any]]:
        limit = min(max(int(limit), 1), 200)
        data = self._get(
            f"/offers/collection/{slug}/nfts/{identifier}",
            params={"limit": limit},
        )
        return list(data.get("offers") or [])
