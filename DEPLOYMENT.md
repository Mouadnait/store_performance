# Deployment Guide: Store Performance Analytics

This guide covers deploying Store Performance to production environments (AWS, Heroku, DigitalOcean, or on-premise).

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Database Migrations](#database-migrations)
4. [AWS Deployment](#aws-deployment)
5. [Heroku Deployment](#heroku-deployment)
6. [Docker/Kubernetes](#dockerkubernetes)
7. [Monitoring & Scaling](#monitoring--scaling)
8. [Security Hardening](#security-hardening)
9. [Backup & Recovery](#backup--recovery)

---

## Pre-Deployment Checklist

- [ ] Code reviewed and tested
- [ ] All environment variables configured (see `.env.example`)
- [ ] Database backed up
- [ ] HTTPS certificate obtained
- [ ] Secret keys generated (not in repo)
- [ ] SendGrid/Twilio/Stripe keys obtained
- [ ] Sentry project created
- [ ] Monitoring setup (NewRelic, DataDog, etc.)
- [ ] CI/CD pipeline configured
- [ ] Load testing completed

---

## Environment Setup

### 1. Production Environment Variables

Create `.env.production`:

```bash
# Django
DJANGO_ENV=production
SECRET_KEY=$(openssl rand -base64 32)
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL on AWS RDS)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=store_performance_prod
DB_USER=postgres
DB_PASSWORD=$(openssl rand -base64 32)
DB_HOST=store-perf-db.c9akciq32.us-east-1.rds.amazonaws.com
DB_PORT=5432

# Redis (AWS ElastiCache)
REDIS_URL=redis://store-perf-cache.abc123.ng.0001.use1.cache.amazonaws.com:6379/0

# Celery
CELERY_BROKER_URL=$REDIS_URL
CELERY_RESULT_BACKEND=redis://store-perf-cache.abc123.ng.0001.use1.cache.amazonaws.com:6379/1

# Email (SendGrid)
SENDGRID_API_KEY=SG.your-key-here
DEFAULT_FROM_EMAIL=noreply@storeperformance.com

# SMS (Twilio)
TWILIO_ACCOUNT_SID=ACxxxx
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE=+14155552671

# Payments (Stripe)
STRIPE_API_KEY=sk_live_xxxxx

# Monitoring (Sentry)
SENTRY_DSN=https://key@sentry.io/1234567

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000

# S3 Storage (for media/static files)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=storeperf-media-prod
AWS_S3_REGION_NAME=us-east-1

# Logging
LOG_LEVEL=WARNING
```

### 2. Generate Secret Key

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 3. Security Headers

Add to `settings_prod.py`:

```python
# HTTPS/TLS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content Security Policy
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ["'self'"],
    "script-src": ["'self'", "cdn.example.com"],
    "style-src": ["'self'", "'unsafe-inline'"],
}
```

---

## Database Migrations

### 1. Local Dry-Run

```bash
python manage.py migrate --plan --settings=performance.settings_prod
```

### 2. Backup Production DB

```bash
# AWS RDS
aws rds create-db-snapshot \
  --db-instance-identifier store-perf-db \
  --db-snapshot-identifier store-perf-db-pre-migration-$(date +%s)
```

### 3. Run Migrations

```bash
python manage.py migrate --settings=performance.settings_prod
```

### 4. Verify

```bash
python manage.py migrate --check --settings=performance.settings_prod
```

---

## AWS Deployment

### Architecture

```
Internet Gateway
    ↓
Application Load Balancer (ALB)
    ↓
EC2 Auto Scaling Group (Django app)
    ↓
RDS PostgreSQL (master + read replicas)
ElastiCache Redis (cluster mode)
S3 (media files + static assets)
```

### 1. Create RDS PostgreSQL Instance

```bash
aws rds create-db-instance \
  --db-instance-identifier store-perf-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.2 \
  --master-username postgres \
  --master-user-password $(openssl rand -base64 32) \
  --allocated-storage 100 \
  --storage-type gp3 \
  --backup-retention-period 30 \
  --enable-cloudwatch-logs-exports '["postgresql"]' \
  --enable-multi-az \
  --enable-iam-database-authentication
```

### 2. Create ElastiCache Redis Cluster

```bash
aws elasticache create-replication-group \
  --replication-group-description "Store Performance Cache" \
  --engine redis \
  --engine-version 7.0 \
  --cache-node-type cache.t3.micro \
  --num-cache-clusters 3 \
  --automatic-failover-enabled \
  --at-rest-encryption-enabled \
  --transit-encryption-enabled
```

### 3. Create S3 Bucket for Media

```bash
aws s3 mb s3://storeperf-media-prod --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket storeperf-media-prod \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket storeperf-media-prod \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

### 4. Create IAM Role for EC2

```bash
# Create role
aws iam create-role \
  --role-name StorePerformanceAppRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ec2.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach policies
aws iam attach-role-policy \
  --role-name StorePerformanceAppRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-role-policy \
  --role-name StorePerformanceAppRole \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy
```

### 5. Launch EC2 Instance

Create `user-data.sh`:

```bash
#!/bin/bash
set -e

# Update system
apt-get update && apt-get upgrade -y

# Install dependencies
apt-get install -y python3.11 python3.11-venv python3-pip \
  postgresql-client postgresql-contrib \
  git curl wget supervisor nginx

# Create app user
useradd -m -s /bin/bash appuser

# Clone repository
cd /home/appuser
sudo -u appuser git clone https://github.com/yourusername/store_performance.git
cd store_performance

# Create virtual environment
sudo -u appuser python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install gunicorn whitenoise

# Copy env file from Secrets Manager
aws secretsmanager get-secret-value \
  --secret-id store-perf-env \
  --query SecretString \
  --output text > .env

# Run migrations
python manage.py migrate --settings=performance.settings_prod

# Collect static files
python manage.py collectstatic --noinput --settings=performance.settings_prod

# Create log directory
mkdir -p logs
chown -R appuser:appuser /home/appuser/store_performance

# Setup Gunicorn with Supervisor
cat > /etc/supervisor/conf.d/store_performance.conf <<'EOF'
[program:store_performance]
directory=/home/appuser/store_performance
command=/home/appuser/store_performance/venv/bin/gunicorn \
  --workers 4 \
  --worker-class sync \
  --bind 127.0.0.1:8000 \
  --timeout 120 \
  performance.wsgi:application
user=appuser
autostart=true
autorestart=true
stderr_logfile=/var/log/store_performance/error.log
stdout_logfile=/var/log/store_performance/access.log
EOF

# Setup Celery worker
cat > /etc/supervisor/conf.d/store_performance_celery.conf <<'EOF'
[program:store_performance_celery]
directory=/home/appuser/store_performance
command=/home/appuser/store_performance/venv/bin/celery -A performance worker -l info
user=appuser
autostart=true
autorestart=true
stderr_logfile=/var/log/store_performance/celery_error.log
stdout_logfile=/var/log/store_performance/celery_access.log
EOF

# Setup Celery beat
cat > /etc/supervisor/conf.d/store_performance_beat.conf <<'EOF'
[program:store_performance_beat]
directory=/home/appuser/store_performance
command=/home/appuser/store_performance/venv/bin/celery -A performance beat -l info
user=appuser
autostart=true
autorestart=true
stderr_logfile=/var/log/store_performance/beat_error.log
stdout_logfile=/var/log/store_performance/beat_access.log
EOF

supervisorctl reread
supervisorctl update
supervisorctl start all

# Setup Nginx reverse proxy
cat > /etc/nginx/sites-available/store_performance <<'EOF'
upstream gunicorn {
  server 127.0.0.1:8000;
}

server {
  listen 80;
  server_name yourdomain.com www.yourdomain.com;

  client_max_body_size 50M;

  location /static/ {
    alias /home/appuser/store_performance/staticfiles/;
    expires 30d;
  }

  location /media/ {
    alias /home/appuser/store_performance/media/;
    expires 7d;
  }

  location / {
    proxy_pass http://gunicorn;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_redirect off;
  }
}
EOF

ln -sf /etc/nginx/sites-available/store_performance /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# Setup SSL with Let's Encrypt
apt-get install -y certbot python3-certbot-nginx
certbot --nginx -d yourdomain.com -d www.yourdomain.com -n --agree-tos -m your-email@example.com

# CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i -E ./amazon-cloudwatch-agent.deb

echo "✓ Deployment setup complete!"
```

### 6. Create Launch Template

```bash
aws ec2 create-launch-template \
  --launch-template-name store-perf-template \
  --launch-template-data '{
    "ImageId": "ami-xxxxxxxx",
    "InstanceType": "t3.small",
    "IamInstanceProfile": {"Name": "StorePerformanceAppRole"},
    "UserData": "'$(base64 -w0 user-data.sh)'",
    "TagSpecifications": [{
      "ResourceType": "instance",
      "Tags": [
        {"Key": "Name", "Value": "store-perf-app"},
        {"Key": "Environment", "Value": "production"}
      ]
    }]
  }'
```

### 7. Create Auto Scaling Group

```bash
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name store-perf-asg \
  --launch-template LaunchTemplateName=store-perf-template \
  --min-size 2 \
  --max-size 6 \
  --desired-capacity 2 \
  --vpc-zone-identifier subnet-xxxxx,subnet-yyyyy \
  --target-group-arns arn:aws:elasticloadbalancing:us-east-1:123456789:targetgroup/store-perf/xxxxx
```

---

## Heroku Deployment

### 1. Prepare for Heroku

```bash
# Create Procfile
cat > Procfile <<'EOF'
web: gunicorn performance.wsgi:application
worker: celery -A performance worker -l info
beat: celery -A performance beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
EOF

# Create runtime.txt
echo "python-3.11.7" > runtime.txt

# Create .slugignore
cat > .slugignore <<'EOF'
*.pyc
.git
.gitignore
.DS_Store
staticfiles/
media/
__pycache__
tests/
.env*
.venv/
EOF
```

### 2. Deploy

```bash
# Login to Heroku
heroku login

# Create app
heroku create store-perf-prod

# Add PostgreSQL
heroku addons:create heroku-postgresql:standard-0 -a store-perf-prod

# Add Redis
heroku addons:create heroku-redis:premium-0 -a store-perf-prod

# Set environment variables
heroku config:set \
  DJANGO_ENV=production \
  SECRET_KEY=$(openssl rand -base64 32) \
  DEBUG=False \
  SENDGRID_API_KEY=... \
  STRIPE_API_KEY=... \
  -a store-perf-prod

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate -a store-perf-prod

# Create superuser
heroku run python manage.py createsuperuser -a store-perf-prod

# Check logs
heroku logs --tail -a store-perf-prod
```

---

## Docker/Kubernetes

### 1. Build & Push Docker Image

```bash
# Build image
docker build -t storeperformance:1.0.0 .

# Tag for registry
docker tag storeperformance:1.0.0 gcr.io/my-project/storeperformance:1.0.0

# Push to Google Container Registry
docker push gcr.io/my-project/storeperformance:1.0.0
```

### 2. Deploy to Kubernetes

Create `k8s/deployment.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: store-perf-config
data:
  DJANGO_ENV: "production"
  DEBUG: "False"

---
apiVersion: v1
kind: Secret
metadata:
  name: store-perf-secrets
type: Opaque
stringData:
  SECRET_KEY: your-secret-key
  DB_PASSWORD: your-db-password
  SENDGRID_API_KEY: your-sendgrid-key

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: store-perf-web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: store-perf-web
  template:
    metadata:
      labels:
        app: store-perf-web
    spec:
      containers:
      - name: django
        image: gcr.io/my-project/storeperformance:1.0.0
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: store-perf-config
        - secretRef:
            name: store-perf-secrets
        env:
        - name: DB_HOST
          value: "postgres-service"
        - name: DB_PORT
          value: "5432"
        livenessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: store-perf-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: store-perf-web
```

Deploy:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl get pods
kubectl logs deployment/store-perf-web
```

---

## Monitoring & Scaling

### 1. CloudWatch Alarms

```bash
# High CPU usage
aws cloudwatch put-metric-alarm \
  --alarm-name store-perf-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:123456789:store-perf-alerts
```

### 2. Application Performance Monitoring

Install New Relic:

```bash
pip install newrelic
newrelic-admin generate-config YOUR_LICENSE_KEY newrelic.ini

# Run with New Relic
newrelic-admin run-program gunicorn performance.wsgi:application
```

### 3. Database Monitoring

```bash
# Enable Enhanced Monitoring
aws rds modify-db-instance \
  --db-instance-identifier store-perf-db \
  --enable-cloudwatch-logs-exports postgresql \
  --apply-immediately
```

---

## Security Hardening

### 1. WAF (Web Application Firewall)

```bash
# Create WAF rules for ALB
aws wafv2 create-web-acl \
  --region us-east-1 \
  --name store-perf-waf \
  --scope REGIONAL \
  --default-action Block={} \
  --rules file://waf-rules.json
```

### 2. DDoS Protection

```bash
# Enable AWS Shield Advanced (optional)
aws shield subscribe
```

### 3. Secrets Management

```bash
# Store secrets in AWS Secrets Manager
aws secretsmanager create-secret \
  --name store-perf-env \
  --secret-string file://.env.production
```

### 4. Network Security

- Enable VPC with private subnets for DB
- Use Security Groups to restrict traffic
- Enable VPC Flow Logs for monitoring

---

## Backup & Recovery

### 1. Database Backups

```bash
# Automated backups (configured in RDS)
# Retention: 30 days
# Backup window: 03:00-04:00 UTC

# Manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier store-perf-db \
  --db-snapshot-identifier store-perf-db-$(date +%s)
```

### 2. Media Files Backup

```bash
# S3 to Glacier
aws s3api put-bucket-lifecycle-configuration \
  --bucket storeperf-media-prod \
  --lifecycle-configuration file://lifecycle.json
```

### 3. Disaster Recovery Plan

- **RPO (Recovery Point Objective):** 1 hour
- **RTO (Recovery Time Objective):** 4 hours
- Test recovery monthly
- Document runbooks for common failures

---

## Performance Tuning

### Database

```sql
-- Index frequently queried columns
CREATE INDEX idx_bill_date ON core_bill(date DESC);
CREATE INDEX idx_bill_store ON core_bill(store_id);
CREATE INDEX idx_client_email ON core_client(email);

-- Enable query logging (production: disable after analysis)
SET log_statement = 'all';
```

### Caching Strategy

```python
# Cache KPIs for 1 hour
cache.set(f'kpis:{store_id}', kpis_data, timeout=3600)

# Cache forecasts for 24 hours
cache.set(f'forecast:{store_id}', forecast_data, timeout=86400)
```

### Celery Optimization

```python
# Increase worker concurrency
celery -A performance worker -c 10 --max-tasks-per-child=100
```

---

## Rollback Plan

If deployment fails:

```bash
# AWS
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name store-perf-asg \
  --launch-template LaunchTemplateName=store-perf-template-old

# Heroku
heroku releases -a store-perf-prod
heroku releases:rollback v123 -a store-perf-prod

# Kubernetes
kubectl rollout undo deployment/store-perf-web
```

---

## Support & Troubleshooting

For issues during deployment, check:

1. Application logs: `heroku logs --tail` or `kubectl logs`
2. Database migrations: `python manage.py migrate --plan`
3. Static files: `python manage.py collectstatic --noinput`
4. Environment variables: Verify all required keys are set
5. Dependencies: `pip list --outdated`

Need help? Create an issue on GitHub or email support@storeperformance.local
