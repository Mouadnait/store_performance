"""
Development settings for Store Performance.
Extends base settings with dev-specific overrides.
"""
from .settings_base import *

# Development-specific overrides
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*.local']

# SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Permissive CORS for development
CORS_ALLOW_ALL_ORIGINS = True

# In-memory cache for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'store-performance-dev-cache',
    }
}

# Celery: Use eager task execution in dev (synchronous)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Email backend for testing (console output)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable security middleware for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# CSRF configuration for development
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://*.local:8000',
]

# Debug toolbar (optional - install django-debug-toolbar if needed)
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
# INTERNAL_IPS = ['127.0.0.1']

# Verbose logging in development
LOGGING['loggers']['django']['level'] = 'DEBUG'

# Disable Sentry in development
SENTRY_DSN = None
