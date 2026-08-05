# Fundex

**Base de données de fonds VC européenne + outil de scouting / matching.**

Live site : https://fundex-scout.vercel.app/

## Version

`index.html` = la **version live actuelle** (« Fundex: VC Intelligence »), chargée via
Supabase. La base contient **2044 fonds** (table Supabase `investors`), pas un snapshot
statique.

## Architecture

- **Front** : app single-page autonome (`index.html`, JS vanilla + `pdf.js` pour l'export)
- **Backend données** : **Supabase** (Postgres REST). Clés anon côté client (publiques).
  - Base : `https://wxtklptwwvcrjfrejrtl.supabase.co`
  - Table : `investors` (2044 lignes)
- **Fonctionnalités** : filtres par stage/secteur/pays, **Scout Network** (37 fonds),
  matching par taille de fonds, portfolio, deep linking, export.

## Champs de la table investors (24)

`id`, `slug`, `name`, `description`, `thesis`, `investment_thesis`, `overview`,
`fund_history_text`, `team_highlights`, `team_size`, `aum`, `check_size_min`,
`check_size_max`, `founded_year`, `headquarters`, `country`, `sector_focus`,
`stage_focus`, `website`, `notable_portfolio`, `logo_url`, `featured`,
`scout_network` (bool), `vcbeast_url`, `created_at`.

## Couverture clé (sur 2044 fonds)

- `name`, `website`, `overview`, `scout_network`, `stage_focus` ≈ 95–100 %
- `sector_focus` 95 % · `thesis` 88 % · `check_size_min/max` 76 %/71 %
- `aum` 42 % · `notable_portfolio` 56 % · `founded_year` 47 %

## Note

L'ancienne version embarquait les données en dur dans le HTML (1285 fonds). La version
actuelle charge les 2044 via Supabase — c'est la source de vérité à jour.
