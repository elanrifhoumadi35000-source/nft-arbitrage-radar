from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Set, Tuple

from .opensea import OpenSeaClient
from .pricing import extract_price

@dataclass
class Opportunity:
    collection: str
    chain: str
    contract: str
    token_id: str
    currency: str
    buy_price: Decimal
    best_offer: Decimal
    estimated_cost: Decimal
    estimated_profit: Decimal
    estimated_profit_pct: Decimal
    listing_hash: str
    offer_hash: str

def _asset(order: Dict[str, Any]) -> Tuple[str, str]:
    asset = order.get("asset") or {}
    contract = str(asset.get("contract") or "")
    identifier = str(asset.get("identifier") or "")
    return contract, identifier

def _order_hash(order: Dict[str, Any]) -> str:
    return str(order.get("order_hash") or "")

def scan_collection(
    client: OpenSeaClient,
    slug: str,
    max_listings: int,
    extra_fees_pct: Decimal,
    gas_reserve_native: Decimal,
    minimum_profit_native: Decimal,
    minimum_profit_pct: Decimal,
) -> List[Opportunity]:
    listings = client.get_collection_listings(slug, limit=max_listings)
    opportunities: List[Opportunity] = []
    seen: Set[Tuple[str, str]] = set()

    for listing in listings:
        contract, token_id = _asset(listing)
        if not contract or not token_id:
            continue

        unique = (contract.lower(), token_id)
        if unique in seen:
            continue
        seen.add(unique)

        listing_price = extract_price(listing)
        if listing_price is None or listing_price.amount <= 0:
            continue

        offers = client.get_nft_offers(slug, token_id, limit=100)
        same_currency = []

        for offer in offers:
            offer_contract, offer_token = _asset(offer)
            if offer_token and offer_token != token_id:
                continue
            if offer_contract and offer_contract.lower() != contract.lower():
                continue

            p = extract_price(offer)
            if p is None or p.amount <= 0:
                continue
            if p.currency != listing_price.currency:
                continue
            same_currency.append((offer, p))

        if not same_currency:
            continue

        best_offer_order, best_offer_price = max(same_currency, key=lambda item: item[1].amount)

        fees = listing_price.amount * (extra_fees_pct / Decimal("100"))
        estimated_cost = listing_price.amount + fees + gas_reserve_native
        profit = best_offer_price.amount - estimated_cost

        if listing_price.amount:
            profit_pct = (profit / listing_price.amount) * Decimal("100")
        else:
            profit_pct = Decimal("0")

        if profit < minimum_profit_native:
            continue
        if profit_pct < minimum_profit_pct:
            continue

        opportunities.append(
            Opportunity(
                collection=slug,
                chain=str(listing.get("chain") or ""),
                contract=contract,
                token_id=token_id,
                currency=listing_price.currency,
                buy_price=listing_price.amount,
                best_offer=best_offer_price.amount,
                estimated_cost=estimated_cost,
                estimated_profit=profit,
                estimated_profit_pct=profit_pct,
                listing_hash=_order_hash(listing),
                offer_hash=_order_hash(best_offer_order),
            )
        )

    return sorted(opportunities, key=lambda x: x.estimated_profit_pct, reverse=True)
