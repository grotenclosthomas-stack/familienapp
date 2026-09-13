# Familien-App (PWA)

Wochenkalender mit Liams Plan · Einkaufsliste pro KW · Essensplan pro KW · Push-Erinnerungen sonntags.
Gehostet auf GitHub Pages, Daten in Firebase Firestore (Projekt `familienapp-f93c7`), Push per GitHub Action.

## Dateien
```
index.html                    – die App
firebase-config.js            – Firebase-Zugangsdaten (bereits eingetragen)
manifest.webmanifest, sw.js   – PWA / Offline / Push-Empfang
icons/                        – App-Icon
tools/send_push.py            – Push-Sender (läuft als GitHub Action)
tools/liam_sync.py            – Planung Liam.xlsx → Firestore
.github/workflows/push.yml    – Zeitplan: sonntags 12 + 18 Uhr (Berlin)
```

## Einrichtung auf GitHub
1. Repository `familienapp` anlegen (public – GitHub Pages ist nur bei public kostenlos), alle Dateien hochladen.
2. **Settings → Pages** → Source „Deploy from a branch“, Branch `main`, Ordner `/ (root)` → Save.
   App-URL: `https://DEINNAME.github.io/familienapp/`
3. **Settings → Secrets and variables → Actions → New repository secret**: Name `FIREBASE_SERVICE_ACCOUNT`, Wert = kompletter Inhalt der Datei `familienapp-f93c7-firebase-adminsdk-….json`.
4. Test: **Actions → Einkaufslisten-Erinnerung → Run workflow** (slot = test) → auf aktivierten Handys kommt eine Testnachricht.

## Auf den iPhones
URL in Safari öffnen → Teilen → **Zum Home-Bildschirm** → App öffnen → **Mehr → Erinnerungen aktivieren**.

## Push-Logik
Sonntag 12 Uhr: „Bis 18 Uhr eintragen, was nächste Woche fehlt – aktuell N Artikel.“ · 18 Uhr: „Liste steht: N Artikel.“
Bezieht sich auf die kommende KW; die App zeigt ab Sonntag automatisch die nächste Woche.

## Liams Plan aktualisieren
`tools/liam_sync.py "Planung Liam.xlsx" --project familienapp-f93c7` (liest die Zellfarben: Gil = blau, Swantje = pink, beide = lila, Oma & Opa = orange, Schule = grün, Logopädie = gelb) und schreibt nach Firestore.

## Updates
Dateien im Repo ändern → Pages baut automatisch neu; bei `sw.js`-Änderungen `VERSION` hochzählen.
