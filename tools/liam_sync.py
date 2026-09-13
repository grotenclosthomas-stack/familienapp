#!/usr/bin/env python3
"""
Liest "Planung Liam.xlsx" (Farbraster: Zeile = Tag, Spalten C..Z = Stunde 0–23, Spalte AB = Notiz)
und erzeugt liam.json bzw. schreibt die Tage direkt nach Firestore.

  python3 liam_sync.py Planung\ Liam.xlsx                       -> ../liam.json
  python3 liam_sync.py Planung\ Liam.xlsx --project mein-projekt -> zusätzlich Firestore-Collection "liam"

Benötigt: pip install openpyxl requests
"""
import sys, json, datetime, argparse, os
import openpyxl

LEGEND = {
    'FF00B0F0': 'gil', 'FFFF3399': 'uns', 'FF7030A0': 'beide', 'FFFFC000': 'oma',
    'FF2CFA08': 'schule', 'FF00B050': 'schule', 'FF92D050': 'schule', 'FFFFFF00': 'logo',
}
CUSTODY = {'gil', 'uns', 'beide', 'oma'}

def color(cell):
    f = cell.fill
    if f and f.fill_type == 'solid' and f.fgColor.type == 'rgb':
        return f.fgColor.rgb
    return None

def runs(flags):
    """[(start, end_exclusive)] für zusammenhängende True-Bereiche"""
    out, s = [], None
    for h, v in enumerate(flags + [False]):
        if v and s is None: s = h
        if not v and s is not None: out.append((s, h)); s = None
    return out

def parse(path, since):
    ws = openpyxl.load_workbook(path).active
    days = {}
    for r in range(9, ws.max_row + 1):
        d = ws.cell(r, 1).value
        if not isinstance(d, datetime.datetime) or d.date() < since: continue
        cats = [LEGEND.get(color(ws.cell(r, 3 + h))) for h in range(24)]
        note = ' '.join(str(ws.cell(r, c).value).strip() for c in (27, 28) if ws.cell(r, c).value)
        # Betreuung: Schul-/Logo-Stunden mit der umgebenden Betreuung auffüllen
        cust = [c if c in CUSTODY else None for c in cats]
        last = next((c for c in cust if c), None)
        for i in range(24):
            if cust[i]: last = cust[i]
            else: cust[i] = last
        segs, start = [], 0
        for i in range(1, 25):
            if i == 24 or cust[i] != cust[start]:
                if cust[start]: segs.append({'who': cust[start], 'from': start, 'to': i})
                start = i
        entry = {'custody': segs,
                 'school': [{'from': a, 'to': b} for a, b in runs([c == 'schule' for c in cats])],
                 'logo': [{'from': a, 'to': b} for a, b in runs([c == 'logo' for c in cats])],
                 'note': note}
        if segs or entry['school'] or entry['logo'] or note:
            days[d.strftime('%Y-%m-%d')] = entry
    return days

def push_firestore(project, days):
    import requests
    base = f'https://firestore.googleapis.com/v1/projects/{project}/databases/(default)/documents/liam/'
    def val(v):
        if isinstance(v, bool): return {'booleanValue': v}
        if isinstance(v, int): return {'integerValue': str(v)}
        if isinstance(v, str): return {'stringValue': v}
        if isinstance(v, list): return {'arrayValue': {'values': [val(x) for x in v]}}
        if isinstance(v, dict): return {'mapValue': {'fields': {k: val(x) for k, x in v.items()}}}
        raise TypeError(v)
    ok = 0
    for date, e in days.items():
        r = requests.patch(base + date, json={'fields': {k: val(v) for k, v in e.items()}}, timeout=30)
        if r.ok: ok += 1
        else: print('Fehler', date, r.status_code, r.text[:200])
    print(f'{ok}/{len(days)} Tage nach Firestore geschrieben')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('xlsx'); ap.add_argument('--project'); ap.add_argument('--since', default=None)
    ap.add_argument('--out', default=os.path.join(os.path.dirname(__file__), '..', 'liam.json'))
    a = ap.parse_args()
    since = datetime.date.fromisoformat(a.since) if a.since else (datetime.date.today() - datetime.timedelta(days=60))
    days = parse(a.xlsx, since)
    json.dump(days, open(a.out, 'w'), ensure_ascii=False, indent=0)
    print(f'{len(days)} Tage ab {since} -> {a.out}')
    if a.project: push_firestore(a.project, days)
