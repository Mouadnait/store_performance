"""
Management command: health check endpoint for deployment monitoring.
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.core.cache import cache
import redis


class Command(BaseCommand):
    help = 'Health check for monitoring systems'

    def handle(self, *args, **options):
        checks = {
            'database': self.check_database(),
            'cache': self.check_cache(),
            'redis': self.check_redis(),
        }
        
        all_ok = all(checks.values())
        
        if all_ok:
            self.stdout.write(self.style.SUCCESS('✓ All systems operational'))
        else:
            failed = [k for k, v in checks.items() if not v]
            self.stdout.write(self.style.ERROR(f'✗ Failed checks: {", ".join(failed)}'))
        
        return 0 if all_ok else 1
    
    def check_database(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            return True
        except Exception as e:
            self.stdout.write(f'Database check failed: {e}')
            return False
    
    def check_cache(self):
        try:
            cache.set('health_check', 'ok', 1)
            return cache.get('health_check') == 'ok'
        except Exception as e:
            self.stdout.write(f'Cache check failed: {e}')
            return False
    
    def check_redis(self):
        try:
            from django.conf import settings
            r = redis.from_url(settings.CELERY_BROKER_URL)
            r.ping()
            return True
        except Exception as e:
            self.stdout.write(f'Redis check failed: {e}')
            return False
