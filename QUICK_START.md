# Quick Start Guide - Store Performance Analytics

Get up and running in 5 minutes. Choose your path:

---

## ⚡ Option 1: Local Development (No Docker)

### 1. Setup

```bash
# Navigate to project
cd /mnt/h/Mine/Back-end/store_performance/performance

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env if needed (defaults work for local dev)
```

### 2. Initialize Database

```bash
# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
# Follow prompts: email, password

# Load sample data (optional)
python manage.py loaddata core/fixtures/sample_data.json
```

### 3. Start Services

**Terminal 1 - Django:**
```bash
python manage.py runserver
# Visit: http://localhost:8000
# Admin: http://localhost:8000/admin
```

**Terminal 2 - Celery Worker:**
```bash
celery -A performance worker -l info
```

**Terminal 3 - Celery Beat (Optional):**
```bash
celery -A performance beat -l info
```

### 4. Test

```bash
# Login: http://localhost:8000/login
# Dashboard: http://localhost:8000/dashboard
# API Docs: http://localhost:8000/api/schema/swagger/
```

---

## 🐳 Option 2: Docker Compose (Complete Stack)

### 1. Setup

```bash
cd /mnt/h/Mine/Back-end/store_performance

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web
```

### 2. Initialize

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### 3. Access Services

| Service | URL |
|---------|-----|
| **Web App** | http://localhost:8000 |
| **Django Admin** | http://localhost:8000/admin |
| **API Docs** | http://localhost:8000/api/schema/swagger/ |
| **Flower (Celery)** | http://localhost:5555 |
| **PostgreSQL** | localhost:5432 |
| **Redis** | localhost:6379 |

### 4. Common Commands

```bash
# View all logs
docker-compose logs -f

# Stop all services
docker-compose down

# Remove all data (⚠️ careful!)
docker-compose down -v

# Run Django shell
docker-compose exec web python manage.py shell

# Run tests
docker-compose exec web python manage.py test
```

---

## 📊 First Actions

### 1. Create a Store

```bash
# Visit: http://localhost:8000/admin/core/store/
# Click "Add Store"
# Fill in details (name, description, location)
# Save
```

### 2. Create Products

```bash
# Visit: http://localhost:8000/products/
# Click "Add Product"
# Fill in: title, price, description
# Save
```

### 3. Create a Client

```bash
# Visit: http://localhost:8000/clients/
# Click "Add Client"
# Fill in: full_name, email, phone
# Save
```

### 4. Create a Sales Record

```bash
# Visit: http://localhost:8000/create-bill/
# Select client
# Select product
# Enter quantity, price
# Save
```

### 5. View Analytics Dashboard

```bash
# Visit: http://localhost:8000/dashboard/
# See KPIs, charts, trends
```

---

## 🔌 API Usage

### Get JWT Token

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'

# Response:
# {"access":"eyJ...","refresh":"eyJ..."}
```

### Use Token in Requests

```bash
curl -X GET http://localhost:8000/api/analytics/kpis/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Explore API

Visit: http://localhost:8000/api/schema/swagger/

Click "Try it out" on any endpoint

---

## 📝 Configuration

### Change Database

Edit `.env`:
```bash
# PostgreSQL (recommended for production)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=store_performance
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Enable Email

Set in `.env`:
```bash
SENDGRID_API_KEY=SG.your-key-here
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Enable SMS Alerts

```bash
TWILIO_ACCOUNT_SID=ACxxxx
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE=+1234567890
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
python manage.py runserver 8001
```

### Database Migration Error

```bash
# Show what would be migrated
python manage.py migrate --plan

# Reset migrations (dev only!)
rm core/migrations/000*.py
python manage.py makemigrations core
python manage.py migrate
```

### Celery Not Working

```bash
# Check Redis connection
redis-cli ping
# Should return: PONG

# Run Celery in debug mode
celery -A performance worker -l debug

# Test task execution
python manage.py shell
>>> from analytics.tasks import compute_daily_metrics
>>> compute_daily_metrics.delay()
```

### Docker Issues

```bash
# Rebuild images
docker-compose build --no-cache

# Restart everything
docker-compose restart

# Check logs for specific service
docker-compose logs web
docker-compose logs celery
docker-compose logs postgres
```

---

## 📚 Next Steps

1. **Read Full Docs:** [README_PROFESSIONAL.md](README_PROFESSIONAL.md)
2. **Learn Deployment:** [DEPLOYMENT.md](DEPLOYMENT.md)
3. **View Upgrade Summary:** [UPGRADE_SUMMARY.md](UPGRADE_SUMMARY.md)
4. **Explore API Docs:** http://localhost:8000/api/schema/swagger/

---

## 🚀 Ready to Deploy?

### To Production (AWS)

See [DEPLOYMENT.md](DEPLOYMENT.md) - AWS section

### To Heroku

```bash
# Install Heroku CLI
brew tap heroku/brew && brew install heroku

# Login
heroku login

# Create app
heroku create store-perf-prod

# Add services
heroku addons:create heroku-postgresql:standard-0
heroku addons:create heroku-redis:premium-0

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# View logs
heroku logs --tail
```

### To Docker Registry

```bash
# Build image
docker build -t storeperformance:1.0.0 .

# Tag for registry
docker tag storeperformance:1.0.0 gcr.io/my-project/storeperformance:1.0.0

# Push
docker push gcr.io/my-project/storeperformance:1.0.0
```

---

## 💡 Pro Tips

- **Hot Reload:** Dev server auto-reloads on code changes
- **Shell Plus:** `python manage.py shell_plus` (if django-extensions installed)
- **DB Backup:** `pg_dump store_performance > backup.sql`
- **Clear Cache:** `python manage.py shell` → `cache.clear()`
- **Monitor Tasks:** Visit http://localhost:5555 (Flower)

---

## 🆘 Need Help?

- **Docs:** See README_PROFESSIONAL.md and DEPLOYMENT.md
- **API Docs:** http://localhost:8000/api/schema/swagger/
- **Django Docs:** https://docs.djangoproject.com
- **DRF Docs:** https://www.django-rest-framework.org
- **Celery Docs:** https://docs.celeryproject.io

---

**Happy coding! 🎉**
