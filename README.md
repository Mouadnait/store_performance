# Store Performance Analytics Platform

A professional, enterprise-grade retail analytics and business intelligence solution designed for store managers and business owners to optimize operations, predict trends, and drive data-driven decisions.

**Version:** 1.0.0  
**Status:** Production Ready  
**License:** MIT

## Overview

Store Performance is a comprehensive analytics platform built with Django 5, Django REST Framework, and modern data science tools. It provides:

- **Real-time KPI Dashboard** – Revenue, sales trends, customer metrics at a glance
- **Predictive Analytics** – Sales forecasting, anomaly detection, trend analysis
- **Customer Intelligence** – RFM segmentation, behavior analysis, recommendations
- **Multi-store Management** – Centralized control for retail chains
- **Role-Based Access Control** – Granular permissions for teams
- **Payment & Notification Integration** – Stripe, SendGrid, Twilio
- **Audit & Compliance** – Full transaction history, data governance
- **Export & Reporting** – CSV, Excel exports, custom report builder
- **Production-Ready** – Docker, Kubernetes, monitoring, backups

## Features

### Analytics & Insights
- **Daily Metrics Aggregation** – Revenue, units sold, customer counts
- **Forecasting** – ARIMA, Prophet models for revenue/quantity predictions
- **Anomaly Detection** – Statistical outlier identification with severity levels
- **RFM Analysis** – Customer segmentation for targeted campaigns
- **Product Recommendations** – "Also bought" + collaborative filtering
- **Trend Analysis** – 7/30/90-day slopes for KPIs and products

### Dashboard & Visualization
- **Interactive Charts** – Plotly/Chart.js visualizations
- **Metric Cards** – Real-time KPI updates with trend indicators
- **Date Filtering** – Day/week/month/custom ranges
- **Drill-Down Navigation** – Click through to detail views
- **Custom Reports** – Build reports by metrics/dimensions
- **Dark Mode** – Eye-friendly theme with preferences

### Multi-Tenant & Security
- **Multi-Store Support** – Manage multiple locations from one platform
- **Role-Based Permissions** – Admin, Manager, Clerk, Viewer roles
- **Audit Logging** – Complete action history with before/after snapshots
- **Data Encryption** – Secure at-rest and in-transit
- **OAuth/JWT** – Modern authentication methods
- **GDPR-Ready** – Data export, right to forget compliance

### Integrations
- **Payment Processing** – Stripe for transactions
- **Email Notifications** – SendGrid for transactional & marketing emails
- **SMS Alerts** – Twilio for critical notifications
- **Accounting** – QuickBooks/Xero sync (coming soon)
- **POS Systems** – CSV/JSON import for external inventory
- **Webhooks** – Real-time event triggers

### Operations & DevOps
- **Docker/Docker Compose** – Containerized deployment
- **Kubernetes Ready** – Helm charts for scaling
- **CI/CD** – GitHub Actions for automated testing & deployment
- **Monitoring** – Sentry for error tracking, structured logging
- **Backups** – Automated DB/file backups to S3
- **Health Checks** – Readiness/liveness probes

## Tech Stack

- **Backend:** Django 5.0.7, Django REST Framework
- **Database:** PostgreSQL (Prod), SQLite (Dev)
- **Cache & Queue:** Redis, Celery, Celery Beat
- **Analytics:** Pandas, NumPy, Scikit-learn, Statsmodels, Prophet
- **API:** DRF-Spectacular (OpenAPI 3.0), CORS
- **Frontend:** Django Templates + Plotly/Chart.js (Vue/React SPA ready)
- **Auth:** JWT (djangorestframework-simplejwt), Sessions
- **Email:** SendGrid API
- **SMS:** Twilio API
- **Payments:** Stripe API
- **Monitoring:** Sentry, Python JSON Logger
- **Deployment:** Docker, Gunicorn, WhiteNoise

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- Redis 6+
- Docker & Docker Compose (optional)

### Development Setup

```bash
# Clone repository
git clone <repo-url>
cd performance

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata core/fixtures/sample_data.json

# Run development server
python manage.py runserver

# In another terminal, run Celery worker
celery -A performance worker -l info

# In another terminal, run Celery beat (scheduler)
celery -A performance beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

Access:
- Admin: http://localhost:8000/admin
- Dashboard: http://localhost:8000/
- API Docs: http://localhost:8000/api/schema/swagger/
- Flower (Celery): http://localhost:5555

### Environment Variables

```bash
# Django
DJANGO_ENV=development  # development, production, testing
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=store_performance
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis & Caching
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Email (SendGrid)
SENDGRID_API_KEY=your-sendgrid-key
DEFAULT_FROM_EMAIL=noreply@storeperformance.local

# SMS (Twilio)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE=+1234567890

# Payments (Stripe)
STRIPE_API_KEY=your-stripe-key

# Monitoring (Sentry)
SENTRY_DSN=https://key@sentry.io/project-id

# Feature Flags
GPT5_ENABLED=False
ENABLE_NOTIFICATIONS=True
ENABLE_FORECASTING=True
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f web

# Run migrations in container
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

## API Documentation

Interactive API docs available at:
- **Swagger UI:** `/api/schema/swagger/`
- **ReDoc:** `/api/schema/redoc/`
- **OpenAPI Schema:** `/api/schema/`

### Key Endpoints

```
Authentication
  POST   /api/token/                 # Get JWT token
  POST   /api/token/refresh/         # Refresh JWT
  POST   /auth/logout/               # Logout

Analytics
  GET    /api/analytics/kpis/        # Key Performance Indicators
  GET    /api/analytics/trends/      # Trend analysis (day/week/month)
  GET    /api/analytics/forecast/    # Sales forecasts
  GET    /api/analytics/anomalies/   # Detected anomalies
  GET    /api/analytics/segments/    # Customer segments
  GET    /api/recommendations/       # Product recommendations

Products
  GET    /api/products/              # List products
  POST   /api/products/              # Create product
  GET    /api/products/{id}/         # Product detail
  PUT    /api/products/{id}/         # Update product

Clients
  GET    /api/clients/               # List clients
  POST   /api/clients/               # Create client
  GET    /api/clients/{id}/          # Client detail

Sales
  GET    /api/sales/                 # List sales
  POST   /api/sales/                 # Create sale
  GET    /api/sales/{id}/            # Sale detail
  GET    /api/sales/export/          # Export sales data

Reports
  GET    /api/reports/               # List saved reports
  POST   /api/reports/               # Create custom report
  GET    /api/reports/{id}/export/   # Export report (CSV/XLSX)

Notifications
  GET    /api/notifications/         # Get notifications
  POST   /api/notifications/{id}/read/ # Mark as read
```

## Project Structure

```
performance/
├── manage.py                    # Django CLI
├── requirements.txt             # Python dependencies
├── .env                        # Environment variables (git-ignored)
├── .env.example                # Example env file
├── db.sqlite3                  # Dev database
│
├── performance/                # Main Django project
│   ├── settings.py             # Settings loader (env-aware)
│   ├── settings_base.py        # Base settings (shared)
│   ├── settings_dev.py         # Development overrides
│   ├── settings_prod.py        # Production overrides
│   ├── urls.py                 # Root URL config
│   ├── wsgi.py                 # WSGI app
│   └── asgi.py                 # ASGI app (WebSockets)
│
├── api/                        # DRF API app
│   ├── serializers.py          # API serializers
│   ├── views.py                # API views
│   ├── urls.py                 # API routes
│   └── permissions.py          # Custom permissions
│
├── core/                       # Core business logic
│   ├── models.py               # Data models
│   ├── models_enhanced.py      # New models (Store, Audit, etc.)
│   ├── admin.py                # Admin customization
│   ├── views.py                # Template views
│   ├── forms.py                # Django forms
│   ├── urls.py                 # Routes
│   └── management/commands/    # Custom management commands
│
├── analytics/                  # Analytics & forecasting
│   ├── services.py             # Analytics business logic
│   ├── models.py               # DailyMetric, Forecast, Anomaly
│   ├── tasks.py                # Celery tasks
│   ├── views.py                # API views
│   └── urls.py                 # Routes
│
├── notifications/              # Email/SMS alerts
│   ├── services.py             # Notification logic
│   ├── models.py               # Notification records
│   ├── tasks.py                # Async notification tasks
│   └── templates/              # Email templates
│
├── userauths/                  # User authentication
│   ├── models.py               # User, Profile models
│   ├── views.py                # Auth views
│   └── urls.py                 # Auth routes
│
├── static/                     # Static assets
│   ├── css/                    # Stylesheets
│   ├── javascript/             # Client-side JS
│   └── images/                 # Images & icons
│
├── templates/                  # Django HTML templates
│   ├── base.html               # Base layout
│   ├── core/                   # Core app templates
│   ├── userauths/              # Auth templates
│   └── api/                    # API-related templates
│
├── media/                      # User-uploaded files
│   ├── user_*/ → 
│   ├── product_images/         # Product images
│   └── store_logos/            # Store logos
│
├── tests/                      # Test suite
│   ├── test_api.py
│   ├── test_analytics.py
│   └── test_models.py
│
├── docker-compose.yml          # Docker Compose config
├── Dockerfile                  # Docker image
├── .dockerignore
├── .gitignore
├── README.md                   # This file
└── DEPLOYMENT.md               # Deployment guide
```

## User Roles & Permissions

| Role | Dashboard | Analytics | Reports | Admin | Audit |
|------|-----------|-----------|---------|-------|-------|
| **Admin** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Manager** | ✓ | ✓ | ✓ | ✗ | View Only |
| **Clerk** | ✓ | Limited | ✗ | ✗ | ✗ |
| **Viewer** | View Only | View Only | View Only | ✗ | ✗ |

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test core.tests

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html

# Run API tests
pytest api/tests/ -v
```

## Performance Optimization

- **Caching:** Redis cache for KPIs, forecasts (24h TTL)
- **Pagination:** 25 items/page by default (configurable)
- **Database Indexing:** Key fields indexed for fast queries
- **Query Optimization:** Select_related, prefetch_related usage
- **Async Tasks:** Celery for heavy computations (forecasting, exports)
- **Compression:** GZip static files in production
- **CDN Ready:** S3/CloudFront for media & static files

## Monitoring & Logging

- **Structured Logging:** JSON logs for ELK/Datadog ingestion
- **Error Tracking:** Sentry integration for exceptions
- **Performance:** New Relic APM (optional)
- **Metrics:** Prometheus-compatible /metrics endpoint
- **Health Checks:** `/health/` endpoint for load balancers

View logs:
```bash
tail -f logs/app.log                    # App logs
docker-compose logs -f web              # Container logs
celery -A performance inspect active    # Active Celery tasks
```

## Deployment

### Heroku

```bash
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### AWS (EC2 + RDS + ElastiCache)

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed setup guide.

### Docker/Kubernetes

```bash
docker build -t storeperformance:1.0.0 .
docker push registry.example.com/storeperformance:1.0.0

kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure:
- Code passes `black`, `flake8`, `isort` checks
- Tests pass with >80% coverage
- Documentation is updated

## Security & Compliance

- **GDPR:** Data export, right to forget, consent tracking
- **PCI-DSS:** Stripe handles card data (not stored locally)
- **Encryption:** TLS 1.2+ for transit, AES-256 for at-rest
- **Secrets:** Managed via environment variables (12-factor app)
- **CORS:** Configurable allowed origins
- **Rate Limiting:** DRF throttling + django-ratelimit
- **Audit Logging:** Full transaction history

## Support & Community

- **Documentation:** [docs/](./docs/)
- **Issues:** GitHub Issues for bug reports
- **Discussions:** GitHub Discussions for Q&A
- **Email:** support@storeperformance.local

## Roadmap

### Q1 2026
- [ ] Mobile app (React Native)
- [ ] Advanced ML models (LSTM, XGBoost)
- [ ] Graph analytics (Neo4j integration)
- [ ] Real-time dashboards (WebSockets/Channels)

### Q2 2026
- [ ] Multi-currency support
- [ ] Accounting software sync (QuickBooks, Xero)
- [ ] Advanced permissions (row-level security)
- [ ] Data warehouse (Snowflake/BigQuery)

### Q3 2026
- [ ] AI-powered insights (GPT-4 integration)
- [ ] Prescriptive analytics (optimization recommendations)
- [ ] Marketplace (third-party integrations)
- [ ] Enterprise SSO (SAML 2.0)

## License

MIT License – See [LICENSE](./LICENSE) for details.

## Acknowledgments

Built with ❤️ using Django, DRF, Pandas, Plotly, and open-source community tools.

---

**Ready to transform your retail business?** Get started today: [Quick Start Guide](./docs/QUICK_START.md)
