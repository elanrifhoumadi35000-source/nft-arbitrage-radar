# NFT Arbitrage Radar

Scanner Python pour rechercher des écarts potentiels entre le prix d'achat d'un NFT listé sur OpenSea et la meilleure offre active sur **le même NFT**.

## Ce que fait cette version

- récupère les listings OpenSea d'une collection ;
- vérifie le `contract + token ID` du NFT ;
- récupère les offres disponibles pour ce token ;
- garde uniquement les comparaisons dans la même devise ;
- estime la marge après frais configurables ;
- affiche uniquement les opportunités qui dépassent le seuil choisi ;
- n'achète et ne revend rien automatiquement.

## Installation rapide sous Windows

1. Installe Python 3.10 ou plus récent.
2. Double-clique sur `LANCER_WINDOWS.bat`.
3. Au premier lancement, le programme crée `.env`.
4. Ouvre `.env` et colle ta clé OpenSea dans :
   `OPENSEA_API_KEY=...`
5. Mets les collections à surveiller dans `config.json`.
6. Relance `LANCER_WINDOWS.bat`.

## Configuration

Exemple `config.json` :

```json
{
  "collections": ["collection-slug-ici"],
  "max_listings_per_collection": 20,
  "request_delay_seconds": 0.25,
  "extra_fees_pct": 0.0,
  "gas_reserve_native": 0.0,
  "minimum_profit_native": 0.0,
  "minimum_profit_pct": 1.0
}
```

`extra_fees_pct` doit contenir ton estimation totale des frais applicables à la revente
(frais marketplace + royalties éventuelles + autres coûts proportionnels).

`gas_reserve_native` est une réserve fixe exprimée dans la devise native comparée.
Pour éviter des calculs trompeurs, le scanner ne convertit pas automatiquement entre ETH, WETH, USDC, etc.

## Sécurité

Ne mets jamais ta vraie clé API dans GitHub.

Le fichier `.env` est volontairement exclu par `.gitignore`.

## Limites importantes

Un résultat affiché n'est pas une garantie d'arbitrage exécutable. Il faut encore vérifier :

- que l'offre n'expire pas avant l'exécution ;
- que l'offre est réellement remplissable ;
- les frais et royalties applicables ;
- les approvals / autorisations nécessaires ;
- le gas ;
- le risque que le listing ou l'offre soit annulé entre les deux opérations ;
- les conditions du protocole Seaport ;
- la faisabilité d'une exécution atomique si l'on veut un vrai achat + revente « tout ou rien ».

La version actuelle est un **radar de détection**, pas un bot de trading automatique.

## Lancer manuellement

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
