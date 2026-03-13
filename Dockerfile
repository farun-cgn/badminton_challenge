FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=badminton_club.settings.production

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "badminton_club.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
