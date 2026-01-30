#!/usr/bin/env python
"""
Quick health check script for Store Performance Platform
Run this to verify all systems are operational
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'performance.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from django.core.cache import cache

def print_status(message, status):
    """Print colored status message"""
    if status:
        print(f"✓ {message}")
    else:
        print(f"✗ {message}")

def check_database():
    """Check database connection"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

def check_cache():
    """Check cache functionality"""
    try:
        cache.set('health_check', 'ok', 30)
        result = cache.get('health_check')
        return result == 'ok'
    except Exception as e:
        print(f"  Error: {e}")
        return False

def check_migrations():
    """Check if all migrations are applied"""
    try:
        from io import StringIO
        output = StringIO()
        call_command('showmigrations', '--plan', stdout=output)
        output_str = output.getvalue()
        return '[ ]' not in output_str
    except Exception as e:
        print(f"  Error: {e}")
        return False

def check_static_files():
    """Check if static files are collected"""
    from django.conf import settings
    static_root = settings.STATIC_ROOT
    return os.path.exists(static_root) and len(os.listdir(static_root)) > 0

def main():
    print("\n" + "="*60)
    print("Store Performance Platform - Health Check")
    print("="*60 + "\n")

    # Check database
    print("Database Connection...")
    print_status("Database connected", check_database())

    # Check cache
    print("\nCache System...")
    print_status("Cache working", check_cache())

    # Check migrations
    print("\nDatabase Migrations...")
    print_status("All migrations applied", check_migrations())

    # Check static files
    print("\nStatic Files...")
    print_status("Static files collected", check_static_files())

    # Environment info
    print("\nEnvironment Information:")
    from django.conf import settings
    print(f"  Django Environment: {os.environ.get('DJANGO_ENV', 'development')}")
    print(f"  Debug Mode: {settings.DEBUG}")
    print(f"  Database: {settings.DATABASES['default']['ENGINE'].split('.')[-1]}")

    print("\n" + "="*60)
    print("Health check completed!")
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nHealth check cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError during health check: {e}")
        sys.exit(1)
