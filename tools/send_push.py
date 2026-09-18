#!/usr/bin/env python3
"""
Push-Erinnerung zur Einkaufsliste (läuft sonntags 12 + 18 Uhr als GitHub Action).
Env: FIREBASE_SERVICE_ACCOUNT (JSON-Inhalt), APP_URL, SLOT (12|18|test)
"""
import os, sys, json, datetime, zoneinfo, requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

SA = json.loads(os.environ['FIREBASE_SERVICE_ACCOUNT'])
PROJECT = SA['project_id']
APP_URL = os.environ.get('APP_URL', './')
SLOT = os.environ.get('SLOT', '')
TZ = zoneinfo.ZoneInfo('Europe/Berlin')
now = datetime.datetime.now(TZ)

# Ohne SLOT: nur laufen, wenn es in Berlin gerade 12 oder 18 Uhr ist (Cron läuft in UTC, Sommer-/Winterzeit)
if not SLOT:
    if now.weekday() != 6 or now.hour not in (12, 18):
        print(f'Kein Sendezeitpunkt ({now:%a %H:%M} Berlin) – nichts zu tun'); sys.exit(0)
    SLOT = str(now.hour)

creds = service_account.Credentials.from_service_account_info(SA, scopes=[
    'https://www.googleapis.com/auth/firebase.messaging', 'https://www.googleapis.com/auth/datastore'])
creds.refresh(Request())
H = {'Authorization': f'Bearer {creds.token}', 'Content-Type': 'application/json'}
FS = f'https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents'

# Zielwoche = kommende KW (Sonntag → morgen ist Montag)
monday = now.date() + datetime.timedelta(days=(7 - now.weekday()) % 7 or 7)
iso = monday.isocalendar(); week_key = f'{iso[0]}-W{iso[1]:02d}'; kw = iso[1]
docs = requests.get(f'{FS}/shopping?pageSize=300', headers=H, timeout=30).json().get('documents', [])
open_items = sum(1 for d in docs if d['fields'].get('week', {}).get('stringValue') == week_key
                 and not d['fields'].get('done', {}).get('booleanValue', False))
artikel = '1 Artikel' if open_items == 1 else f'{open_items} Artikel'
if SLOT == 'nachricht':  # Freitext aus dem Workflow-Formular
    title, body = os.environ.get('TITLE') or 'Familie', os.environ.get('BODY') or ''
elif SLOT == 'test':
    title, body = 'Test 🎉', 'Push-Erinnerungen funktionieren.'
elif int(SLOT) < 15:
    title, body = f'Einkaufsliste KW {kw}', f'Bis 18 Uhr eintragen, was nächste Woche fehlt – aktuell {artikel}.'
else:
    title, body = f'Einkaufsliste KW {kw} steht', f'{artikel} auf der Liste. Letzte Chance für Ergänzungen.'

tokens = requests.get(f'{FS}/pushTokens?pageSize=100', headers=H, timeout=30).json().get('documents', [])
sent = removed = 0
for d in tokens:
    token = d['fields'].get('token', {}).get('stringValue')
    if not token: continue
    msg = {'message': {'token': token, 'notification': {'title': title, 'body': body},
                       'data': {'url': APP_URL, 'tag': f'einkauf-{SLOT}'},
                       'webpush': {'headers': {'Urgency': 'high', 'TTL': '3600'}}}}
    r = requests.post(f'https://fcm.googleapis.com/v1/projects/{PROJECT}/messages:send', headers=H, json=msg, timeout=30)
    if r.ok: sent += 1
    elif r.status_code == 404 or 'UNREGISTERED' in r.text or 'INVALID_ARGUMENT' in r.text:
        requests.delete(f"https://firestore.googleapis.com/v1/{d['name']}", headers=H, timeout=30); removed += 1
    else: print('Fehler', r.status_code, r.text[:200])
print(f'{title} – {body}\nGesendet: {sent}, entfernt: {removed}, Geräte gesamt: {len(tokens)}')
