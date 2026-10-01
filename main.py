from __future__ import annotations

import json
import os
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from nft_radar.opensea import OpenSeaClient, OpenSeaError
from nft_radar.scanner import scan_collection

console = Console()

def D(value) -> Decimal:
    return Decimal(str(value))

def load_config() -> dict:
    path = Path("config.json")
    if not path.exists():
        raise FileNotFoundError("config.json introuvable.")
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    load_dotenv()
    api_key = os.getenv("OPENSEA_API_KEY", "").strip()
    if not api_key:
        console.print("[red]Clé OpenSea absente.[/red] Ouvre .env et renseigne OPENSEA_API_KEY.")
        return 2

    cfg = load_config()
    collections = [str(x).strip() for x in cfg.get("collections", []) if str(x).strip()]
    collections = [x for x in collections if x != "collection-slug-ici"]

    if not collections:
        console.print("[yellow]Aucune collection configurée.[/yellow]")
        console.print("Ouvre config.json puis remplace 'collection-slug-ici' par un slug OpenSea.")
        return 2

    client = OpenSeaClient(
        api_key=api_key,
        request_delay_seconds=float(cfg.get("request_delay_seconds", 0.25)),
    )

    all_opps = []
    for slug in collections:
        console.print(f"\n[bold cyan]Scan : {slug}[/bold cyan]")
        try:
            opps = scan_collection(
                client=client,
                slug=slug,
                max_listings=int(cfg.get("max_listings_per_collection", 20)),
                extra_fees_pct=D(cfg.get("extra_fees_pct", 0)),
                gas_reserve_native=D(cfg.get("gas_reserve_native", 0)),
                minimum_profit_native=D(cfg.get("minimum_profit_native", 0)),
                minimum_profit_pct=D(cfg.get("minimum_profit_pct", 1)),
            )
            all_opps.extend(opps)
            console.print(f"{len(opps)} opportunité(s) au-dessus des seuils.")
        except OpenSeaError as exc:
            console.print(f"[red]{exc}[/red]")

    if not all_opps:
        console.print("\n[yellow]Aucune opportunité détectée avec les paramètres actuels.[/yellow]")
        return 0

    table = Table(title="NFT Arbitrage Radar")
    table.add_column("Collection")
    table.add_column("Token")
    table.add_column("Devise")
    table.add_column("Achat", justify="right")
    table.add_column("Offre", justify="right")
    table.add_column("Profit est.", justify="right")
    table.add_column("Marge", justify="right")

    for o in sorted(all_opps, key=lambda x: x.estimated_profit_pct, reverse=True):
        table.add_row(
            o.collection,
            o.token_id,
            o.currency,
            f"{o.buy_price:.8f}",
            f"{o.best_offer:.8f}",
            f"{o.estimated_profit:.8f}",
            f"{o.estimated_profit_pct:.2f}%",
        )

    console.print()
    console.print(table)
    console.print(
        "\n[dim]Attention : radar uniquement. Une offre détectée peut être annulée, expirer, "
        "devenir non remplissable ou générer des coûts supplémentaires avant l'exécution.[/dim]"
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
