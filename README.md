# Badminton Club Challenge App

Eine Web-App für Badminton-Vereine zur Verwaltung von Herausforderungsspielen und einer ELO-basierten Rangliste.

---

## Inhalt

- [Was macht die App?](#was-macht-die-app)
- [Funktionen im Überblick](#funktionen-im-überblick)
- [Herausforderungsprozess](#herausforderungsprozess)
- [ELO-Rangliste](#elo-rangliste)
- [Für Spieler: Erste Schritte](#für-spieler-erste-schritte)
- [Für Administratoren](#für-administratoren)
- [Technischer Stack](#technischer-stack)
- [Installation & Deployment](#installation--deployment)

---

## Was macht die App?

Die Badminton Club Challenge App ermöglicht es Vereinsmitgliedern, sich gegenseitig zu Wettkampfspielen herauszufordern. Basierend auf den Spielergebnissen wird eine Rangliste nach dem **ELO-System** (bekannt aus dem Schach) geführt und laufend aktualisiert.

**Kernidee:** Wer einen besser platzierten Mitspieler schlägt, steigt in der Rangliste auf – wer verliert, fällt ab. So entsteht eine faire, dynamische Rangliste, die den tatsächlichen Leistungsstand widerspiegelt.

---

## Funktionen im Überblick

| Funktion | Beschreibung |
|---|---|
| **Registrierung** | Spieler legen ein Konto mit Benutzername, E-Mail und Passwort an |
| **Rangliste** | Öffentlich einsehbare ELO-Rangliste aller aktiven Spieler |
| **Herausforderungen** | Jeden höher platzierten Spieler herausfordern |
| **Annehmen / Ablehnen** | Herausgeforderter kann annehmen oder ablehnen (mit ELO-Konsequenz) |
| **Ergebnis eintragen** | Einer der beiden Spieler trägt das Spielergebnis ein |
| **ELO-Verlauf** | Vollständige Historie aller ELO-Änderungen |
| **Passwort-Reset** | Selbstständiges Zurücksetzen per E-Mail-Link |
| **Admin-Panel** | Verwaltung von Spielern, Rangliste und Herausforderungen |

---

## Herausforderungsprozess

### Regeln

1. **Wen kann ich herausfordern?**
   Jeden Spieler, der in der Rangliste **höher** steht als du (besserer Platz = niedrigere Zahl). Es gibt keine Begrenzung, wie viele Plätze du überspringen kannst.

2. **Blockierungsregel**
   Sobald eine Herausforderung aktiv ist (ausstehend oder angenommen), können **beide** beteiligten Spieler weder herausfordern noch herausgefordert werden – bis das Spiel abgeschlossen ist.

3. **Ablehnen hat Konsequenzen**
   Wer eine Herausforderung ablehnt, verliert ELO-Punkte (als hätte er das Spiel verloren, jedoch mit halbem K-Faktor).

4. **Ergebnis eintragen**
   Nach dem Spiel trägt einer der beiden Spieler das Ergebnis in der App ein. Eine Bestätigung durch den zweiten Spieler ist nicht erforderlich.

### Ablauf einer Herausforderung

```
Spieler B fordert Spieler A heraus
          │
          ▼
    [AUSSTEHEND]
    Spieler A entscheidet:
          │
    ┌─────┴─────┐
    │           │
 Annehmen    Ablehnen
    │           │
    ▼           ▼
[ANGENOMMEN]  [ABGELEHNT]
Spiel findet  ELO-Abzug für
   statt       Spieler A
    │
    ▼
Ergebnis wird eingetragen
    │
    ▼
[ABGESCHLOSSEN]
ELO & Rangliste werden
   aktualisiert
```

---

## ELO-Rangliste

### Wie funktioniert ELO?

Das ELO-System berechnet nach jedem Spiel, wie viele Punkte der Sieger vom Verlierer erhält. Dabei gilt:

- **Favorit gewinnt** → wenige Punkte wechseln den Besitzer (Ergebnis war erwartet)
- **Außenseiter gewinnt** → viele Punkte wechseln den Besitzer (Überraschungsergebnis)

### Parameter

| Parameter | Wert | Bedeutung |
|---|---|---|
| Start-ELO | 1200 | Jeder neue Spieler beginnt hier |
| K-Faktor (Spiel) | 32 | Maximale Punkte pro Match |
| K-Faktor (Ablehnung) | 16 | Halbierte Strafe bei Ablehnung |
| ELO-Minimum | 100 | Untergrenze, kein weiterer Abzug darunter |

### Beispiel

> Spieler B (ELO 1200) fordert Spieler A (ELO 1400) heraus und **gewinnt**.
> - Spieler B: +25 ELO → 1225
> - Spieler A: −25 ELO → 1375
>
> Die Rangliste wird sofort neu berechnet.

---

## Für Spieler: Erste Schritte

### 1. Registrieren

Öffne die App im Browser und klicke auf **„Registrieren"**.

Fülle das Formular aus:
- **Benutzername** – dein eindeutiger Login-Name
- **Vorname / Nachname** – optional, wird in der Rangliste angezeigt
- **E-Mail-Adresse** – wird für den Passwort-Reset benötigt
- **Passwort** – mind. 8 Zeichen

Nach der Registrierung bist du automatisch angemeldet. Dein ELO-Startwert wird vom Admin festgelegt.

### 2. Rangliste anschauen

Die Rangliste ist die Startseite der App – auch ohne Anmeldung einsehbar. Du siehst:
- Deinen aktuellen Rang und ELO-Wert
- Den Status aller Spieler (frei / aktive Herausforderung)
- Einen „Herausfordern"-Button bei Spielern, die du herausfordern kannst

### 3. Einen Spieler herausfordern

1. Klicke in der Rangliste auf **„Herausfordern"** neben dem gewünschten Spieler
   *(Button erscheint nur bei höher platzierten, freien Spielern)*
2. Bestätige die Herausforderung
3. Der Gegner erhält eine E-Mail-Benachrichtigung

### 4. Auf eine Herausforderung reagieren

Wenn du herausgefordert wirst:
1. Du erhältst eine E-Mail-Benachrichtigung
2. Melde dich in der App an
3. Gehe zu **„Meine Herausforderungen"**
4. Klicke auf **„Antworten"** und wähle:
   - **Annehmen** → Vereinbart den Spieltermin direkt mit dem Herausforderer
   - **Ablehnen** → Möglich, aber mit ELO-Abzug!

### 5. Ergebnis eintragen

Nach dem Spiel:
1. Gehe zu **„Meine Herausforderungen"** → aktive Herausforderung
2. Klicke auf **„Ergebnis eintragen"**
3. Wähle den Sieger und trage optional das Spielergebnis ein (z.B. `21-15, 21-18`)
4. Klicke auf **„Ergebnis speichern"**

Die ELO-Punkte und die Rangliste werden sofort aktualisiert.

### 6. Passwort vergessen?

Auf der Anmeldeseite findest du den Link **„Passwort vergessen?"**. Gib deine E-Mail-Adresse ein und du erhältst einen Reset-Link per E-Mail.

---

## Für Administratoren

Der Admin-Bereich ist unter `/admin/` erreichbar (nur für Benutzer mit Staff-Rechten).

### Initiale Rangliste einrichten

Nach dem Start der App:

1. **Admin-Panel öffnen** → `/admin/`
2. **Auth > Users** → alle registrierten Spieler sind sichtbar
3. Jeden Spieler anklicken → im Abschnitt **„Spielerprofil"** den gewünschten **ELO-Startwert** eintragen
4. Speichern → die Rangliste berechnet sich automatisch neu

Alternativ: Spieler auswählen → Admin-Aktion **„ELO auf 1200 setzen"** für einen Massenreset.

### Passwort-Reset für Spieler

1. Admin-Panel → Auth > Users
2. Betroffenen Spieler auswählen
3. Admin-Aktion: **„Passwort-Reset-E-Mail senden"**
4. Der Spieler erhält einen Reset-Link per E-Mail

### Herausforderungen verwalten

Im Admin-Panel unter **Challenges > Challenges** kannst du:
- Den Status aller Herausforderungen einsehen
- Aktive Herausforderungen **abbrechen** (z.B. bei Inaktivität eines Spielers)
- Ergebnisse einsehen und Statistiken prüfen

---

## Technischer Stack

| Komponente | Technologie |
|---|---|
| Backend | Python 3.12 + Django 5.x |
| Frontend | Django-Templates + Bootstrap 5 |
| Datenbank | PostgreSQL 16 |
| Web-Server | Nginx (Reverse Proxy + Static Files) |
| App-Server | Gunicorn (WSGI) |
| SSL/TLS | Let's Encrypt (Certbot) |
| Deployment | Docker Compose |
| E-Mail | SMTP (konfigurierbar) |

---

## Installation & Deployment

Vollständige Anleitung: siehe **[DEPLOYMENT.md](DEPLOYMENT.md)**

### Schnellstart (Entwicklung lokal)

```bash
# Repository klonen
git clone https://github.com/farun-cgn/badminton_challenge.git
cd badminton_challenge

# Python-Abhängigkeiten installieren
pip install -r requirements.txt

# Datenbank initialisieren
python manage.py migrate

# Admin-Benutzer anlegen
python manage.py createsuperuser

# Entwicklungsserver starten
python manage.py runserver
```

App ist dann unter `http://localhost:8000` erreichbar.

### Produktions-Deployment (VPS mit Docker)

```bash
# Repository auf dem VPS klonen
git clone https://github.com/farun-cgn/badminton_challenge.git /opt/badminton-club
cd /opt/badminton-club

# Konfiguration anpassen
cp .env.example .env
nano .env  # Werte eintragen

# App starten
docker compose up -d

# Migrationen & Superuser
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Detaillierte Schritte inkl. HTTPS-Zertifikat: **[DEPLOYMENT.md](DEPLOYMENT.md)**

---

## Lizenz

Dieses Projekt ist für den internen Vereinsgebrauch entwickelt.
