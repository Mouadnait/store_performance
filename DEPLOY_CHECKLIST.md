# Deploy Checklist (Production)

## Environment
- Set required vars: SECRET_KEY, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, REDIS_URL, SENDGRID_API_KEY.
- Optional but recommended: SENTRY_DSN, SECURE_REFERRER_POLICY, DEFAULT_FROM_EMAIL.
- Confirm STATIC_ROOT and MEDIA_ROOT directories are writable by the app user.

## Build & Migrate
- Install deps: `pip install -r requirements.txt`.
- Run migrations: `python manage.py migrate --noinput`.
- Collect static assets: `python manage.py collectstatic --noinput`.

## Application Processes
- Start web: `gunicorn performance.wsgi:application --bind 0.0.0.0:8000` (behind reverse proxy with HTTPS).
- Start Celery worker: `celery -A performance worker --loglevel=info`.
- Start Celery beat: `celery -A performance beat --loglevel=info`.

## Post-Deploy Verification
- Health endpoint responds 200 (e.g., /health/ if enabled).
- Admin login works; create a superuser if none: `python manage.py createsuperuser`.
- Static files served correctly via WhiteNoise/proxy (check CSS/JS load in browser).

## Smoke Tests – Bill Management
- **Create Bill:** Add product to bill → submit → verify product description/quantity/price/amount saved and display on client bills page.
- **Edit Bill:** Click Edit on a bill → modify fields → save → verify changes reflected (description, quantity, price).
- **Delete Bill:** Click Delete → confirm → verify bill removed from list.
- **Print Bill:** Click Print → verify print-friendly view opens with complete bill data.
- **Copy Bill:** Click Copy → confirm → verify duplicate created with today's date.

Check logs for any errors during these operations.
