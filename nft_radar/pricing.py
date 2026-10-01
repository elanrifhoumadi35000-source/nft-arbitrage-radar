from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional

@dataclass(frozen=True)
class Price:
    amount: Decimal
    currency: str
    decimals: int
    raw_value: str

def _to_decimal(v: Any) -> Optional[Decimal]:
    try:
        return Decimal(str(v))
    except (InvalidOperation, TypeError, ValueError):
        return None

def extract_price(order: Dict[str, Any]) -> Optional[Price]:
    price = order.get("price") or {}
    current = price.get("current") or price

    currency = (
        current.get("currency")
        or current.get("symbol")
        or price.get("currency")
        or price.get("symbol")
    )
    value = (
        current.get("value")
        or current.get("amount")
        or price.get("value")
        or price.get("amount")
    )
    decimals = (
        current.get("decimals")
        if current.get("decimals") is not None
        else price.get("decimals")
    )

    if currency is None or value is None:
        return None

    try:
        decimals_i = int(decimals) if decimals is not None else 18
    except (TypeError, ValueError):
        decimals_i = 18

    raw = _to_decimal(value)
    if raw is None:
        return None

    value_str = str(value)
    if "." in value_str:
        amount = raw
    else:
        amount = raw / (Decimal(10) ** decimals_i)

    return Price(
        amount=amount,
        currency=str(currency).upper(),
        decimals=decimals_i,
        raw_value=value_str,
    )
