# Deployment für Einsteiger: Badminton Challenge App auf einem VPS

Diese Anleitung erklärt Schritt für Schritt, wie du die Badminton Challenge App auf einem eigenen Server (VPS) zum Laufen bringst – auch wenn du das noch nie gemacht hast.

---

## Inhaltsverzeichnis

1. [Voraussetzungen](#1-voraussetzungen)
2. [VPS vorbereiten](#2-vps-vorbereiten)
3. [Docker installieren](#3-docker-installieren)
4. [Projekt herunterladen](#4-projekt-herunterladen)
5. [Umgebungsvariablen konfigurieren](#5-umgebungsvariablen-konfigurieren)
6. [Domain und Nginx konfigurieren](#6-domain-und-nginx-konfigurieren)
7. [SSL-Zertifikat holen (HTTPS)](#7-ssl-zertifikat-holen-https)
8. [App starten](#8-app-starten)
9. [Datenbank einrichten](#9-datenbank-einrichten)
10. [Alles testen](#10-alles-testen)
11. [Wartung und Updates](#11-wartung-und-updates)
12. [Häufige Probleme](#12-häufige-probleme)

---

## 1. Voraussetzungen

Bevor du anfängst, brauchst du:

### Was du haben musst:

| Was | Wo bekommst du es |
|-----|-------------------|
| Einen VPS (virtueller Server) | z.B. Hetzner Cloud, DigitalOcean, Netcup, IONOS |
| Eine Domain (z.B. `badminton-club.de`) | z.B. Namecheap, INWX, Strato |
| SSH-Zugang zu deinem VPS | Wird beim Erstellen des VPS angezeigt |
| Einen Computer mit Terminal | Windows: PowerShell oder PuTTY, Mac/Linux: Terminal |

### Empfehlungen für den VPS:

- **Betriebssystem**: Ubuntu 22.04 LTS (empfohlen)
- **RAM**: mindestens 1 GB (2 GB empfohlen)
- **Speicher**: mindestens 20 GB
- **CPU**: 1 vCore reicht für den Anfang

### Domain auf deinen VPS zeigen lassen:

Nachdem du deinen VPS erstellt hast, bekommst du eine **IP-Adresse** (z.B. `123.456.78.90`). Diese musst du bei deinem Domain-Anbieter eintragen:

1. Melde dich beim Domain-Anbieter an
2. Gehe zu den DNS-Einstellungen deiner Domain
3. Erstelle einen **A-Record**:
   - **Name**: `@` (oder deine Domain direkt)
   - **Wert**: deine VPS-IP-Adresse
4. Optional: Erstelle einen weiteren A-Record für `www`:
   - **Name**: `www`
   - **Wert**: deine VPS-IP-Adresse

> **Wichtig**: DNS-Änderungen können bis zu 24 Stunden dauern, bis sie aktiv sind. Meistens geht es aber viel schneller (5–30 Minuten).

---

## 2. VPS vorbereiten

### Schritt 2.1: Mit dem VPS verbinden

Öffne dein Terminal und verbinde dich per SSH mit deinem Server:

```bash
ssh root@DEINE-IP-ADRESSE
```

Ersetze `DEINE-IP-ADRESSE` mit der IP deines VPS, z.B. `ssh root@123.456.78.90`.

Du wirst nach dem Passwort gefragt (oder es wird automatisch dein SSH-Key verwendet).

### Schritt 2.2: System aktualisieren

Führe diese Befehle aus, um den Server auf den neuesten Stand zu bringen:

```bash
apt update && apt upgrade -y
```

> Wenn du gefragt wirst, ob Pakete aktualisiert werden sollen, bestätige immer mit `y` und Enter.

### Schritt 2.3: Hilfsprogramme installieren

```bash
apt install -y curl git nano ufw
```

Diese Programme werden später gebraucht:
- `curl`: Zum Herunterladen von Dateien
- `git`: Zum Klonen des Projekts
- `nano`: Ein einfacher Texteditor
- `ufw`: Firewall

### Schritt 2.4: Firewall einrichten

Die Firewall schützt deinen Server. Nur die Ports 22 (SSH), 80 (HTTP) und 443 (HTTPS) müssen offen sein:

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

Bestätige mit `y`, wenn gefragt. Überprüfe den Status:

```bash
ufw status
```

Die Ausgabe sollte so aussehen:
```
Status: active

To                         Action      From
--                         ------      ----
OpenSSH                    ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
```

---

## 3. Docker installieren

Docker ist die Technologie, mit der die App und alle ihre Abhängigkeiten (Datenbank, Webserver) einfach verwaltet werden.

### Schritt 3.1: Docker installieren

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

Warte, bis die Installation abgeschlossen ist (kann 1–2 Minuten dauern).

### Schritt 3.2: Installation überprüfen

```bash
docker --version
docker compose version
```

Du solltest etwa folgende Ausgabe sehen:
```
Docker version 27.x.x, build ...
Docker Compose version v2.x.x
```

> **Hinweis**: Docker Compose ist seit Docker Version 23 direkt eingebaut (`docker compose`). Ältere Anleitungen verwenden `docker-compose` (mit Bindestrich) – das funktioniert hier nicht mehr.

---

## 4. Projekt herunterladen

### Schritt 4.1: Verzeichnis erstellen und Projekt klonen

```bash
mkdir -p /opt/badminton-club
cd /opt/badminton-club
git clone https://github.com/farun-cgn/badminton_challenge.git .
```

Der Punkt am Ende (`clone ... .`) bedeutet: "Lade das Projekt direkt hier hin, ohne einen Extra-Unterordner."

### Schritt 4.2: Überprüfen, ob alles da ist

```bash
ls -la
```

Du solltest Dateien wie `Dockerfile`, `docker-compose.yml`, `manage.py` und einen Ordner `badminton_club/` sehen.

---

## 5. Umgebungsvariablen konfigurieren

Die App benötigt geheime Einstellungen (Passwörter, API-Keys, Domain). Diese werden in einer `.env`-Datei gespeichert, die **niemals** in Git eingecheckt wird.

### Schritt 5.1: Beispieldatei kopieren

```bash
cp .env.example .env
```

### Schritt 5.2: `.env`-Datei bearbeiten

```bash
nano .env
```

Der Editor öffnet sich. Du siehst folgende Felder, die du ausfüllen musst:

```
SECRET_KEY=change-me-to-a-long-random-string
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://badminton:yourpassword@db:5432/badminton_db

# PostgreSQL
POSTGRES_DB=badminton_db
POSTGRES_USER=badminton
POSTGRES_PASSWORD=yourpassword

# Email (SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=yoursmtppassword
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Was du ändern musst:

#### SECRET_KEY (sehr wichtig!)

Generiere einen sicheren, zufälligen Schlüssel:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Kopiere die Ausgabe und ersetze `change-me-to-a-long-random-string`.

> **Wichtig**: Dieser Schlüssel ist wie ein Masterpasswort für deine App. Teile ihn niemals und gib ihn nicht in Git ein!

#### ALLOWED_HOSTS

Ersetze `yourdomain.com,www.yourdomain.com` mit deiner echten Domain, z.B.:
```
ALLOWED_HOSTS=badminton-club.de,www.badminton-club.de
```

#### POSTGRES_PASSWORD und DATABASE_URL

Wähle ein sicheres Datenbankpasswort (keine Sonderzeichen wie `@`, `#`, `/`). Ersetze `yourpassword` an **beiden Stellen** mit demselben Passwort, z.B.:
```
DATABASE_URL=postgres://badminton:MeinSicheresPasswort123@db:5432/badminton_db
POSTGRES_PASSWORD=MeinSicheresPasswort123
```

#### E-Mail-Einstellungen (optional für den Start)

Falls du keinen SMTP-Server hast, kannst du E-Mail-Funktionen vorerst deaktivieren:
```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Für eine richtige E-Mail-Konfiguration (z.B. mit Gmail):
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=deinegmail@gmail.com
EMAIL_HOST_PASSWORD=dein-app-passwort
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=deinegmail@gmail.com
```

> **Hinweis bei Gmail**: Du brauchst ein "App-Passwort", nicht dein normales Gmail-Passwort. Das findest du in deinen Google-Konto-Einstellungen unter "Sicherheit" → "App-Passwörter".

### Schritt 5.3: Datei speichern

In nano: Drücke `Strg+X`, dann `J` (oder `Y`), dann `Enter`.

### Schritt 5.4: Sicherheit der `.env`-Datei

```bash
chmod 600 .env
```

Damit kann nur der Root-User die Datei lesen.

---

## 6. Domain und Nginx konfigurieren

Nginx ist der Webserver, der Anfragen aus dem Internet an die App weiterleitet.

### Schritt 6.1: Nginx-Konfiguration bearbeiten

```bash
nano nginx/nginx.conf
```

Suche nach allen Stellen, wo `yourdomain.com` oder `www.yourdomain.com` steht, und ersetze sie mit deiner echten Domain.

Drücke in nano `Strg+W` zum Suchen. Suche nach `yourdomain` um alle Stellen zu finden.

Beispiel: Ändere
```
server_name yourdomain.com www.yourdomain.com;
```
zu
```
server_name badminton-club.de www.badminton-club.de;
```

Speichere mit `Strg+X`, dann `J`, dann `Enter`.

---

## 7. SSL-Zertifikat holen (HTTPS)

HTTPS verschlüsselt die Verbindung zwischen Browser und Server. Das Zertifikat ist kostenlos über Let's Encrypt.

### Schritt 7.1: Nginx-Konfiguration für HTTP-Only vorbereiten

Bevor wir das SSL-Zertifikat holen, muss die App erst über HTTP erreichbar sein. Die `nginx/nginx.conf` hat bereits einen HTTP-Block für Let's Encrypt eingebaut.

Stelle sicher, dass der HTTPS-Block in der Nginx-Konfiguration noch **auskommentiert** ist (mit `#`). Das Zertifikat muss erst existieren, bevor Nginx auf Port 443 starten kann.

### Schritt 7.2: Nur Nginx und die App starten (ohne HTTPS)

```bash
cd /opt/badminton-club
docker compose up -d db web nginx
```

Warte 10–15 Sekunden und prüfe, ob alles läuft:

```bash
docker compose ps
```

Die Ausgabe sollte zeigen, dass `db`, `web` und `nginx` den Status `running` haben.

### Schritt 7.3: Erreichbarkeit testen

Öffne im Browser `http://DEINE-DOMAIN.de`. Du solltest eine Webseite sehen (eventuell mit Fehlern, das ist ok).

### Schritt 7.4: SSL-Zertifikat beantragen

```bash
docker compose run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  -d DEINE-DOMAIN.de \
  -d www.DEINE-DOMAIN.de \
  --email deine@email.de \
  --agree-tos \
  --no-eff-email
```

Ersetze:
- `DEINE-DOMAIN.de` mit deiner echten Domain
- `deine@email.de` mit deiner E-Mail-Adresse

Bei Erfolg siehst du:
```
Congratulations! Your certificate and chain have been saved at:
/etc/letsencrypt/live/DEINE-DOMAIN.de/fullchain.pem
```

### Schritt 7.5: HTTPS in Nginx aktivieren

Öffne die Nginx-Konfiguration und entkommentiere den HTTPS-Block:

```bash
nano nginx/nginx.conf
```

Entferne die `#`-Zeichen vor dem HTTPS-Server-Block (der Block, der mit `server {` beginnt und `listen 443 ssl` enthält).

Speichere und starte alle Dienste neu:

```bash
docker compose down
docker compose up -d
```

---

## 8. App starten

### Schritt 8.1: Alle Container starten

```bash
cd /opt/badminton-club
docker compose up -d
```

Das `-d` bedeutet "im Hintergrund" (detached mode).

### Schritt 8.2: Status prüfen

```bash
docker compose ps
```

Du solltest vier Container sehen, alle mit Status `running`:
```
NAME                    STATUS
badminton_club-db-1     Up (healthy)
badminton_club-web-1    Up
badminton_club-nginx-1  Up
badminton_club-certbot-1 Up
```

### Schritt 8.3: Logs beobachten

Falls etwas nicht stimmt, schau dir die Logs an:

```bash
# Alle Logs
docker compose logs -f

# Nur die App-Logs
docker compose logs -f web

# Nur Nginx-Logs
docker compose logs -f nginx
```

Drücke `Strg+C` um die Log-Ansicht zu beenden.

---

## 9. Datenbank einrichten

### Schritt 9.1: Datenbankmigrationen ausführen

Django muss die Datenbanktabellen erstellen. Das geht mit:

```bash
docker compose exec web python manage.py migrate \
  --settings=badminton_club.settings.production
```

Du solltest eine Ausgabe wie diese sehen:
```
Operations to perform:
  Apply all migrations: accounts, admin, auth, challenges, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

### Schritt 9.2: Administrator-Account erstellen

```bash
docker compose exec web python manage.py createsuperuser \
  --settings=badminton_club.settings.production
```

Du wirst nach Benutzername, E-Mail und Passwort gefragt. Merke dir diese Daten – du brauchst sie für das Admin-Panel.

### Schritt 9.3: Statische Dateien sammeln (falls nötig)

Die statischen Dateien (CSS, JS, Bilder) werden normalerweise automatisch beim Docker-Build gesammelt. Falls nicht:

```bash
docker compose exec web python manage.py collectstatic \
  --noinput \
  --settings=badminton_club.settings.production
```

---

## 10. Alles testen

### Schritt 10.1: Website im Browser öffnen

1. Öffne `https://DEINE-DOMAIN.de`
2. Du solltest das Schloss-Symbol in der Adressleiste sehen (HTTPS aktiv)
3. Die Startseite sollte die Rangliste zeigen

### Schritt 10.2: Admin-Panel testen

1. Gehe zu `https://DEINE-DOMAIN.de/admin/`
2. Melde dich mit dem Superuser-Account an
3. Du siehst das Django-Administrations-Panel

### Schritt 10.3: Health-Check

```bash
curl https://DEINE-DOMAIN.de/health/
```

Ausgabe sollte sein: `OK`

### Schritt 10.4: Registrierung testen

1. Gehe zu `https://DEINE-DOMAIN.de/accounts/register/`
2. Erstelle einen Test-Account
3. Melde dich an und überprüfe, ob alles funktioniert

---

## 11. Wartung und Updates

### App aktualisieren

Wenn eine neue Version der App verfügbar ist:

```bash
cd /opt/badminton-club

# Neueste Version herunterladen
git pull

# Neues Docker-Image bauen
docker compose build web

# Datenbankmigrationen ausführen (falls neue Tabellen)
docker compose exec web python manage.py migrate \
  --settings=badminton_club.settings.production

# App neu starten
docker compose up -d
```

### Logs anschauen

```bash
# Live-Logs der App
docker compose logs -f web

# Nginx-Zugriffslog
docker compose logs -f nginx

# Datenbanklog
docker compose logs -f db
```

### Datenbank-Backup erstellen

```bash
docker compose exec db pg_dump -U badminton badminton_db > backup_$(date +%Y%m%d).sql
```

Damit wird eine Sicherungsdatei mit aktuellem Datum erstellt (z.B. `backup_20260315.sql`).

### Backup zurückspielen

```bash
# ACHTUNG: Überschreibt die aktuelle Datenbank!
cat backup_20260315.sql | docker compose exec -T db psql -U badminton badminton_db
```

### SSL-Zertifikat erneuern

Das SSL-Zertifikat wird automatisch durch den certbot-Container erneuert. Um es manuell zu testen:

```bash
docker compose run --rm certbot renew --dry-run
```

Für automatische Erneuerung mit Cron (läuft jeden Tag um 3:00 Uhr nachts):

```bash
crontab -e
```

Füge diese Zeile hinzu:
```
0 3 * * * cd /opt/badminton-club && docker compose run --rm certbot renew && docker compose restart nginx
```

Speichere mit `Strg+X`, `J`, `Enter`.

### Server neustarten

Falls der VPS neugestartet wird, starten die Docker-Container **automatisch wieder** (dank `restart: unless-stopped` in der docker-compose.yml).

### Speicherplatz überprüfen

```bash
df -h
docker system df
```

Falls zu viel Speicher belegt ist (alte Docker-Images):

```bash
docker system prune -f
```

---

## 12. Häufige Probleme

### Problem: Container startet nicht

**Symptom**: `docker compose ps` zeigt einen Container mit Status `Exiting`

**Lösung**: Logs anschauen

```bash
docker compose logs web
```

Häufige Ursachen:
- Fehler in der `.env`-Datei (Tippfehler, fehlende Variable)
- Port 80 oder 443 ist bereits belegt (anderer Webserver läuft)

### Problem: 502 Bad Gateway

**Symptom**: Browser zeigt "502 Bad Gateway"

**Bedeutung**: Nginx läuft, aber die App (web-Container) antwortet nicht

**Lösung**:
```bash
# App-Logs prüfen
docker compose logs web

# App-Container neu starten
docker compose restart web
```

### Problem: Datenbankfehler beim Start

**Symptom**: App-Logs zeigen `could not connect to server` oder `FATAL: password authentication failed`

**Lösung**: Prüfe ob Passwort in `.env` korrekt ist und an beiden Stellen übereinstimmt:
```bash
grep PASSWORD .env
grep DATABASE_URL .env
```

Datenbankcontainer neu starten:
```bash
docker compose restart db
sleep 5
docker compose restart web
```

### Problem: SSL-Zertifikat schlägt fehl

**Symptom**: `certbot` zeigt Fehler beim Beantragen des Zertifikats

**Häufige Ursachen**:
1. Domain zeigt noch nicht auf den Server (DNS noch nicht aktiv)
2. Port 80 ist in der Firewall gesperrt
3. Ein anderer Prozess belegt Port 80

**Überprüfen**:
```bash
# Zeigt deine Domain auf die richtige IP?
nslookup DEINE-DOMAIN.de

# Ist Port 80 offen?
ufw status

# Läuft etwas auf Port 80?
ss -tlnp | grep ':80'
```

### Problem: Statische Dateien fehlen (CSS/JS lädt nicht)

**Symptom**: Die Seite sieht "kaputt" aus, ohne Styling

**Lösung**:
```bash
docker compose exec web python manage.py collectstatic \
  --noinput \
  --settings=badminton_club.settings.production

docker compose restart nginx
```

### Problem: Seite ist langsam oder nicht erreichbar

**Symptom**: Seite lädt sehr langsam oder gibt Timeout

**Überprüfe**:
```bash
# Ressourcenverbrauch prüfen
docker stats

# Falls RAM voll: Container neu starten
docker compose restart
```

Falls RAM dauerhaft voll ist, erwäge ein Upgrade deines VPS-Tarifs.

### Nützliche Befehle auf einen Blick

```bash
# Status aller Container
docker compose ps

# Alle Logs live verfolgen
docker compose logs -f

# Einzelnen Container neu starten
docker compose restart web

# Alle Container stoppen
docker compose down

# Alle Container starten
docker compose up -d

# Django-Shell öffnen (für Debugging)
docker compose exec web python manage.py shell \
  --settings=badminton_club.settings.production

# Datenbank-Shell öffnen
docker compose exec db psql -U badminton badminton_db
```

---

## Zusammenfassung: Schnelle Übersicht der Schritte

1. ✅ VPS mieten und Domain einrichten (DNS-A-Record)
2. ✅ Per SSH verbinden, System updaten, Docker installieren
3. ✅ Projekt nach `/opt/badminton-club` klonen
4. ✅ `.env` aus `.env.example` kopieren und ausfüllen
5. ✅ Domain in `nginx/nginx.conf` eintragen
6. ✅ App starten, SSL-Zertifikat holen, HTTPS aktivieren
7. ✅ Datenbankmigrationen ausführen
8. ✅ Superuser erstellen
9. ✅ Fertig! 🎉

---

*Erstellt für das Badminton Challenge Projekt – github.com/farun-cgn/badminton_challenge*
