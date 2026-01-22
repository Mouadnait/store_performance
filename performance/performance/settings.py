"""
Django settings for Store Performance Analytics.
Loads environment-specific settings based on DJANGO_ENV.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Determine environment
DJANGO_ENV = os.environ.get('DJANGO_ENV', 'development')

if DJANGO_ENV == 'production':
    from .settings_prod import *  # noqa
elif DJANGO_ENV == 'testing':
    from .settings_dev import *  # noqa
    DATABASES['default']['NAME'] = ':memory:'
else:
    from .settings_dev import *  # noqa

# Log the current environment
import logging
logger = logging.getLogger(__name__)
logger.info(f"Loaded settings for environment: {DJANGO_ENV}")
