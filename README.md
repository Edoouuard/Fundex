# Fundex

**Base de données de fonds VC européenne + outil de scouting / matching.**

Live site : https://fundex-scout.vercel.app/

## Contenu du repo

| Fichier | Description |
|---|---|
| `index.html` | Le site (app single-page, charge les données depuis Supabase) |
| `fundex-data-enriched.json` | **Base enrichie** : 2044 fonds (id, name, aum, check_size, sector_focus, stage_focus, scout_network, latest_deals…) |
| `deal-watch.py` | **Sous-agent de veille des derniers deals** (scan / apply / report) |
| `README.md` | Ce fichier |

## Architecture

- **Front** : app single-page autonome (`index.html`), données chargées depuis **Supabase**
  (table `investors`).
- **Base Supabase** : 2044 fonds · URL `https://wxtklptwwvcrjfrejrtl.supabase.co`
- **Veille deals** : `deal-watch.py` identifie les fonds notables (37 `scout_network`),
  délègue la recherche des derniers investissements à des sous-agents, applique les
  résultats vérifiés, et met à jour Supabase. Automatisé via un cron hebdomadaire.

## Champs de la table investors (principaux)

`id`, `slug`, `name`, `description`, `thesis`, `investment_thesis`, `overview`,
`fund_history_text`, `team_highlights`, `team_size`, `aum`, `check_size_min`,
`check_size_max`, `founded_year`, `headquarters`, `country`, `sector_focus`,
`stage_focus`, `website`, `notable_portfolio`, `logo_url`, `featured`,
`scout_network` (bool), `vcbeast_url`, `latest_deals` (ajouté par la veille),
`deals_last_checked`, `created_at`.

## Veille deals — usage du script

```bash
python deal-watch.py scan --top 30   # voir les fonds notables à traiter
python deal-watch.py apply fichier.json  # appliquer les deals vérifiés
python deal-watch.py report            # état d'enrichissement
```

Le cron hebdomadaire (lundi 09h00) exécute le cycle complet : scan → délégation de
recherche → application → PATCH Supabase.
