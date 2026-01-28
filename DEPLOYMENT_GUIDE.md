# 🚀 Production Deployment Guide

## Pre-Deployment Security Checklist

### 1. Environment Variables (REQUIRED)

Create a `.env` file or set these in your hosting environment:

```bash
# Core Settings
DJANGO_ENV=production
DEBUG=False
SECRET_KEY=your-super-secret-key-at-least-50-characters-long-random-string
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (adjust for your DB)
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_strong_database_password
DB_HOST=localhost
DB_PORT=5432

# Email (for password resets, notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Optional: Error Monitoring (Recommended)
SENTRY_DSN=https://your-sentry-dsn-here

# Optional: Redis (for better caching)
REDIS_URL=redis://localhost:6379/0
```

### 2. Install All Dependencies

```bash
# Base installation
pip install -r requirements.txt

# Verify installation
python manage.py check --deploy
```

### 3. Run Security Audit

```bash
python manage.py security_audit
```

**Fix any CRITICAL issues before deploying!**

Expected output for production:
```
✓ DEBUG is disabled in production
✓ SECRET_KEY has sufficient length
✓ ALLOWED_HOSTS is configured
✓ CSRF middleware is enabled
✓ Security middleware is enabled
✓ SESSION_COOKIE_HTTPONLY is enabled
✓ CSRF_COOKIE_HTTPONLY is enabled
✓ SECURE_SSL_REDIRECT is enabled
✓ SESSION_COOKIE_SECURE is enabled
✓ CSRF_COOKIE_SECURE is enabled
✓ 4 password validators configured
✓ Rate limiting is enabled
✓ All custom middleware active
```

### 4. Database Migration

```bash
# Backup existing database first!
python manage.py dumpdata > backup_$(date +%Y%m%d).json

# Run migrations
python manage.py migrate

# Create superuser if needed
python manage.py createsuperuser
```

### 5. Static Files

```bash
# Collect static files
python manage.py collectstatic --noinput

# Verify
ls -lh staticfiles/
```

## Security Configuration

### Middleware Stack (Already Configured)

Your [performance/settings_base.py](performance/settings_base.py) has:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Custom Security Middleware (NEW)
    'core.middleware.SecurityHeadersMiddleware',
    'core.middleware.RateLimitMiddleware',
    'core.middleware.RequestLoggingMiddleware',
    'core.middleware.SecurityEventMiddleware',
]
```

### Production Settings (Already Configured)

Your [performance/settings_prod.py](performance/settings_prod.py) has:

```python
# HTTPS Enforcement
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Secure Cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
# ... more CSP settings
```

## Server Configuration

### Option 1: Using Gunicorn (Recommended)

```bash
# Install gunicorn
pip install gunicorn

# Test run
gunicorn performance.wsgi:application --bind 0.0.0.0:8000

# Production run (with workers)
gunicorn performance.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info
```

### Option 2: Using uWSGI

```bash
# Install uwsgi
pip install uwsgi

# Create uwsgi.ini
cat > uwsgi.ini << EOF
[uwsgi]
module = performance.wsgi:application
master = true
processes = 4
threads = 2
socket = /tmp/performance.sock
chmod-socket = 666
vacuum = true
die-on-term = true
EOF

# Run
uwsgi --ini uwsgi.ini
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Security headers (Django middleware adds these, but belt-and-suspenders)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/store_performance/performance/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /path/to/store_performance/performance/media/;
        expires 7d;
    }
}
```

## Celery Configuration (Background Tasks)

### Start Celery Worker

```bash
# Development
celery -A performance worker -l info

# Production (with supervisor or systemd)
celery -A performance worker \
    -l info \
    --logfile=logs/celery_worker.log \
    --pidfile=logs/celery_worker.pid
```

### Start Celery Beat (Scheduled Tasks)

```bash
# Development
celery -A performance beat -l info

# Production
celery -A performance beat \
    -l info \
    --logfile=logs/celery_beat.log \
    --pidfile=logs/celery_beat.pid \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Systemd Service Files

Create `/etc/systemd/system/celery.service`:

```ini
[Unit]
Description=Celery Worker
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/store_performance/performance
Environment="DJANGO_ENV=production"
ExecStart=/path/to/venv/bin/celery -A performance worker -l info --logfile=logs/celery_worker.log --pidfile=logs/celery_worker.pid
ExecStop=/path/to/venv/bin/celery -A performance control shutdown
Restart=always

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/celerybeat.service`:

```ini
[Unit]
Description=Celery Beat
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/store_performance/performance
Environment="DJANGO_ENV=production"
ExecStart=/path/to/venv/bin/celery -A performance beat -l info --logfile=logs/celery_beat.log
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable celery celerybeat
sudo systemctl start celery celerybeat
```

## Monitoring & Maintenance

### 1. Log Monitoring

```bash
# Real-time monitoring
tail -f logs/app.log
tail -f logs/security.log
tail -f logs/error.log

# Search for issues
grep "ERROR" logs/app.log
grep "CRITICAL" logs/app.log
grep "Rate limit exceeded" logs/security.log
```

### 2. Sentry Integration (Optional but Recommended)

1. Sign up at [sentry.io](https://sentry.io)
2. Create a new Django project
3. Get your DSN
4. Set environment variable:
   ```bash
   export SENTRY_DSN="https://your-sentry-dsn"
   ```

Your [settings_prod.py](performance/settings_prod.py) already has Sentry configured!

### 3. Regular Security Audits

Schedule weekly:
```bash
# Add to crontab
0 2 * * 0 cd /path/to/project && python manage.py security_audit > logs/security_audit_$(date +\%Y\%m\%d).log
```

### 4. Database Backups

Daily backups:
```bash
# Add to crontab
0 1 * * * cd /path/to/project && python manage.py dumpdata > backups/backup_$(date +\%Y\%m\%d).json
```

## Performance Optimization

### 1. Enable Redis Caching (Optional but Recommended)

Install Redis:
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis
```

Update [settings_prod.py](performance/settings_prod.py):
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 2. Database Connection Pooling

For PostgreSQL, add to `requirements.txt`:
```
psycopg2-binary==2.9.9
```

Update database settings:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}
```

## Troubleshooting

### Issue: 403 Forbidden on POST requests
**Solution:** Check CSRF token is included in forms/AJAX requests

### Issue: Rate limit blocking legitimate users
**Solution:** Adjust rate limits in [core/middleware.py](performance/core/middleware.py):
```python
API_RATE_LIMIT = 120  # Increase from 60
LOGIN_RATE_LIMIT = 10  # Increase from 5
```

### Issue: Slow requests
**Solution:** Check [logs/app.log](performance/logs/app.log) for slow request logs (>2s)

### Issue: High memory usage
**Solution:** Reduce Gunicorn workers or optimize database queries

### Issue: Static files not loading
**Solution:**
```bash
python manage.py collectstatic --clear --noinput
```

## Security Incident Response

### Suspected Breach

1. **Immediate actions:**
   ```bash
   # Check security logs
   grep "blocked" logs/security.log
   grep "CRITICAL" logs/security.log
   
   # Check failed login attempts
   grep "Failed login" logs/security.log
   
   # Check suspicious IPs
   grep "Suspicious" logs/security.log
   ```

2. **If confirmed breach:**
   - Change `SECRET_KEY` immediately
   - Force all users to logout (clear sessions)
   - Rotate database credentials
   - Review user permissions
   - Check for unauthorized admin users

3. **Post-incident:**
   - Run `python manage.py security_audit`
   - Review logs for entry point
   - Update security measures
   - Document incident

## Production Deployment Checklist

- [ ] Set all environment variables
- [ ] Set `DEBUG=False`
- [ ] Set `ALLOWED_HOSTS` correctly
- [ ] Generate strong `SECRET_KEY` (50+ characters)
- [ ] Run `python manage.py check --deploy` (no errors)
- [ ] Run `python manage.py security_audit` (all passed)
- [ ] Run `python manage.py migrate`
- [ ] Run `python manage.py collectstatic`
- [ ] Configure HTTPS/SSL certificates
- [ ] Set up Nginx/Apache reverse proxy
- [ ] Start Gunicorn/uWSGI service
- [ ] Start Celery worker and beat
- [ ] Enable firewall (UFW/iptables)
- [ ] Set up automated backups
- [ ] Configure log rotation
- [ ] Set up monitoring (Sentry recommended)
- [ ] Test all critical endpoints
- [ ] Test rate limiting (try 6 failed logins)
- [ ] Test security headers (check browser dev tools)
- [ ] Document admin credentials securely
- [ ] Set up uptime monitoring

## Quick Commands Reference

```bash
# Check deployment readiness
python manage.py check --deploy

# Security audit
python manage.py security_audit

# Collect static files
python manage.py collectstatic --noinput

# Database migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start Gunicorn
gunicorn performance.wsgi:application --bind 0.0.0.0:8000 --workers 4

# Start Celery
celery -A performance worker -l info
celery -A performance beat -l info

# Monitor logs
tail -f logs/security.log
tail -f logs/error.log

# Check what IPs are blocked
grep "blocked" logs/security.log | cut -d' ' -f5 | sort | uniq -c
```

## Support & Documentation

- **Security Features:** See [SECURITY_IMPLEMENTATION.md](SECURITY_IMPLEMENTATION.md)
- **Detailed Security Docs:** See [SECURITY.md](SECURITY.md)
- **Quick Start:** See [QUICK_START.md](QUICK_START.md)
- **Django Deployment:** https://docs.djangoproject.com/en/5.0/howto/deployment/

---

**Ready to deploy? Follow this guide step-by-step. Your platform has enterprise-level security already configured!**

**Last Updated:** January 28, 2026
