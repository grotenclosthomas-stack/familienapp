// Firebase-Konfiguration
// 1. https://console.firebase.google.com → Projekt anlegen
// 2. Projekt-Einstellungen → "Meine Apps" → Web-App (</>) hinzufügen
// 3. Das dort angezeigte firebaseConfig-Objekt hier eintragen
// 4. Für Push: Projekt-Einstellungen → Cloud Messaging → "Web Push certificates" → Schlüsselpaar erzeugen → als vapidKey eintragen
// Solange apiKey leer ist, läuft die App im lokalen Demo-Modus (nur dieses Gerät, kein Sync, kein Push).

window.FAMILY_FIREBASE_CONFIG = {
  apiKey: "AIzaSyDbD3xmUjWV5RD1RyWY8gF3nncOic353io",
  authDomain: "familienapp-f93c7.firebaseapp.com",
  projectId: "familienapp-f93c7",
  storageBucket: "familienapp-f93c7.firebasestorage.app",
  messagingSenderId: "158364623902",
  appId: "1:158364623902:web:942c76fb9d402627f17a0f",
  vapidKey: "BDCoe99vTPdLXSq43RtFBtrnN5W29EJcCO5ipQiHYK_yb0M0HSxC2brC2zZCaQoiOdsbwu_wnfR1s9AHyiPWMsc",
  // Cloudflare Worker für die Rezept-Recherche (siehe worker/worker.js)
  recipeApi: "https://familienapp-rezepte.ihr-fairer-makler.workers.dev/"
};
