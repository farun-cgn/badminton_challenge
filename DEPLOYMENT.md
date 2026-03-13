# Deployment-Anleitung – Badminton Club App

## Voraussetzungen auf dem VPS

- Docker & Docker Compose installiert
- Domain/Subdomain zeigt auf die VPS-IP
- Port 80 und 443 sind in der Firewall freigegeben

## Erstinstallation

```bash
# 1. Repository klonen
git clone <repo-url> /opt/badminton-club
cd /opt/badminton-club

# 2. Umgebungsvariablen konfigurieren
cp .env.example .env
nano .env  # Werte anpassen: SECRET_KEY, ALLOWED_HOSTS, DB-Daten, SMTP

# 3. nginx.conf anpassen
nano nginx/nginx.conf  # 'yourdomain.com' durch echte Domain ersetzen

# 4. Erst nur HTTP starten (für Let's Encrypt)
# nginx.conf: HTTPS-Block auskommentieren (oder Port-443-Server-Block entfernen)
docker compose up -d db nginx

# 5. Erstzertifikat anfordern
docker compose run --rm certbot certonly --webroot -w /var/www/certbot -d yourdomain.com --email admin@yourdomain.com --agree-tos

# 6. HTTPS-Block in nginx.conf einkommentieren/aktivieren
# 7. Alle Services starten
docker compose up -d

# 8. Datenbankmigrationen ausführen
docker compose exec web python manage.py migrate --settings=badminton_club.settings.production

# 9. Superuser anlegen (für Django-Admin)
docker compose exec web python manage.py createsuperuser --settings=badminton_club.settings.production

# 10. Statische Dateien sammeln (falls nicht im Dockerfile erledigt)
docker compose exec web python manage.py collectstatic --noinput --settings=badminton_club.settings.production
```

## Initiale Rangliste einrichten

1. Unter `https://yourdomain.com/admin/` einloggen
2. Alle Spieler sollten sich bereits registriert haben
3. Unter **Auth > Users**: Jeden Spieler auswählen → Inline-Profil: ELO-Wert setzen
4. Alternativ: Admin-Aktion "ELO auf 1200 setzen" für alle nutzen, dann manuell anpassen

## Zertifikat automatisch erneuern (Cron)

```bash
crontab -e
# Folgende Zeile hinzufügen:
0 3 * * * cd /opt/badminton-club && docker compose run --rm certbot renew && docker compose restart nginx
```

## Updates einspielen

```bash
cd /opt/badminton-club
git pull
docker compose build web
docker compose exec web python manage.py migrate --settings=badminton_club.settings.production
docker compose up -d
```

## Logs einsehen

```bash
docker compose logs web -f    # Django/Gunicorn logs
docker compose logs nginx -f  # Nginx logs
docker compose logs db -f     # PostgreSQL logs
```
