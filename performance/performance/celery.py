"""
Celery configuration for Store Performance Analytics.
Handles async task execution, scheduling, and monitoring.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'performance.settings')

app = Celery('performance')

# Load configuration from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Define the Celery Beat schedule
app.conf.beat_schedule = {
    # Forecast computation: daily at 2 AM UTC
    'compute-daily-forecasts': {
        'task': 'analytics.tasks.compute_daily_forecasts',
        'schedule': crontab(hour=2, minute=0),
    },
    # Anomaly detection: daily at 3 AM UTC
    'detect-daily-anomalies': {
        'task': 'analytics.tasks.detect_daily_anomalies',
        'schedule': crontab(hour=3, minute=0),
    },
    # Customer segmentation: weekly (Sundays at 4 AM UTC)
    'segment-customers-weekly': {
        'task': 'analytics.tasks.segment_customers',
        'schedule': crontab(day_of_week=6, hour=4, minute=0),
    },
    # Compute daily metrics: every hour
    'compute-hourly-metrics': {
        'task': 'analytics.tasks.compute_daily_metrics',
        'schedule': crontab(minute=0),
    },
    # Send pending notifications: every 5 minutes
    'send-pending-notifications': {
        'task': 'notifications.tasks.send_pending_notifications',
        'schedule': crontab(minute='*/5'),
    },
    # Clean up old audit logs: daily at 1 AM UTC
    'cleanup-audit-logs': {
        'task': 'core.tasks.cleanup_old_audit_logs',
        'schedule': crontab(hour=1, minute=0),
    },
    # Database backup: daily at 11 PM UTC
    'backup-database': {
        'task': 'core.tasks.backup_database',
        'schedule': crontab(hour=23, minute=0),
    },
}

# Task settings
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    result_expires=3600,  # 1 hour
    broker_connection_retry_on_startup=True,  # Retry broker connection on startup
)

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f'Request: {self.request!r}')
