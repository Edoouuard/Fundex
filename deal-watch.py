#!/usr/bin/env python3
"""
deal_watch.py — Sous-agent de veille des derniers deals des fonds notables (Fundex).

Objectif : identifier les fonds « notables » (scout_network, gros AUM, featured),
repérer ceux dont la fiche est datée, et préparer la liste des fonds à enrichir avec
leurs derniers deals. La recherche du contenu réel (sites / news) est déléguée à un
sous-agent LLM ; ce script gère la sélection, le tri et l'application des résultats.

Usage:
  python deal_watch.py scan                 # sélectionne les fonds notables à traiter
  python deal_watch.py apply <deals.json>   # applique les deals trouvés sur les fiches
  python deal_watch.py report               # résumé de l'état d'enrichissement

Base attendue : fundex_2044_enriched.json (à côté du script, ou via --data).
Les corrections écrites dans : fundex_2044_enriched.json (backup auto avant écriture).
"""
import argparse, json, os, sys, re
from datetime import date

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fundex_2044_enriched.json")

def load():
    if not os.path.exists(BASE): sys.exit(f"Base introuvable : {BASE}")
    return json.load(open(BASE, encoding="utf-8"))

def save(data):
    bak = BASE.replace(".json", f".bak_{date.today().isoformat()}.json")
    if not os.path.exists(bak):
        json.dump(data, open(bak, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(data, open(BASE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# --- score de « notabilité » / priorité de traitement ---
EARLY_STAGES = ["pre-seed","seed","series a","series b","angel","accelerator"]
def is_early(d):
    st = [ (s or '').lower() for s in (d.get('stage_focus') or []) ]
    return any(any(e in s for e in EARLY_STAGES) for s in st)

def notability_score(d):
    s = 0
    if d.get('scout_network') is True: s += 500          # fonds scout = priorité absolue
    if d.get('featured') is True: s += 40
    if is_early(d): s += 30                              # early-stage = plus pertinent pour scout
    aum = (d.get('aum') or '')
    m = re.search(r'(\d+(?:\.\d+)?)\s*([MBK])', aum.replace('M€',' M').replace('B€',' B'))
    if m:
        val = float(m.group(1)); unit = m.group(2)
        # pondérer l'AUM pour ne pas écraser les fonds early par les gros PE
        s += min(val * (1000 if unit=='B' else 1 if unit=='M' else 0.001), 300)
    if d.get('notable_portfolio'): s += 5
    return s

def parse_amt(x):
    if not x: return None
    m = re.search(r'(\d+(?:\.\d+)?)\s*([MBK])?', str(x).replace('€','').strip())
    if not m: return None
    val=float(m.group(1)); u=(m.group(2) or 'M')
    mult={'M':1,'B':1000,'K':0.001}.get(u,1)
    return val*mult

def cmd_scan(args):
    data = load()
    funds = []
    for d in data:
        funds.append((notability_score(d), d['name'], d.get('website'), d.get('country'), d.get('scout_network')))
    funds.sort(reverse=True)
    print(f"=== TOP {args.top} fonds notables à traiter ({len(data)} au total) ===")
    for s,name,web,country,scout in funds[:args.top]:
        print(f"  [score {s:6.0f}] {name:34} {country or '?':14} {'SCOUT' if scout else ''}  {web or ''}")

def cmd_apply(args):
    data = load()
    res = json.load(open(args.deals, encoding="utf-8"))
    updated = 0
    for item in res:
        name = item.get('name')
        deals = item.get('latest_deals') or []
        if not deals: 
            print(f"  ! {name}: aucun deal vérifié, fiche inchangée"); continue
        if not item.get('verified', True):
            print(f"  ! {name}: non vérifié, on n'applique pas"); continue
        for d in data:
            if (d.get('name') or '').lower() == name.lower():
                prev = d.get('notable_portfolio') or []
                # ajouter uniquement les nouveaux, dans un champ dédié "latest_deals"
                d['latest_deals'] = deals
                d['deals_last_checked'] = date.today().isoformat()
                merged = list(dict.fromkeys(prev + [x for x in deals if x not in prev]))
                d['notable_portfolio'] = merged
                updated += 1
                print(f"  ✓ {name}: +{len(deals)} deals")
                break
    save(data)
    print(f"\n{updated} fiches mises à jour. Sauvegardé dans {BASE}")

def cmd_report(args):
    data = load()
    n = len(data)
    with_latest = [d for d in data if d.get('latest_deals')]
    checked = [d for d in data if d.get('deals_last_checked')]
    scouts = [d for d in data if d.get('scout_network') is True]
    scouts_checked = [d for d in scouts if d.get('deals_last_checked')]
    print(f"Fonds: {n} | avec latest_deals: {len(with_latest)} | veille faite: {len(checked)}")
    print(f"Scout: {len(scouts)} | scout avec veille: {len(scouts_checked)}")

def main():
    p=argparse.ArgumentParser(prog="deal_watch.py")
    p.add_argument("--data", default=BASE)
    sub=p.add_subparsers(dest="cmd", required=True)
    s=sub.add_parser("scan"); s.add_argument("--top", type=int, default=30); s.set_defaults(fn=cmd_scan)
    a=sub.add_parser("apply"); a.add_argument("deals"); a.set_defaults(fn=cmd_apply)
    r=sub.add_parser("report"); r.set_defaults(fn=cmd_report)
    args=p.parse_args(); args.fn(args)

if __name__=="__main__":
    main()
