"""
Security Audit Management Command
Check for common security vulnerabilities
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
import sys

User = get_user_model()


class Command(BaseCommand):
    help = 'Run security audit and check for vulnerabilities'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix issues automatically',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Security Audit Report'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        issues_found = 0
        warnings_found = 0
        
        # Check 1: DEBUG mode
        if settings.DEBUG:
            self.stdout.write(
                self.style.ERROR('❌ DEBUG is enabled! Set DEBUG=False in production.')
            )
            issues_found += 1
        else:
            self.stdout.write(self.style.SUCCESS('✓ DEBUG is disabled'))
        
        # Check 2: SECRET_KEY
        if hasattr(settings, 'SECRET_KEY'):
            if len(settings.SECRET_KEY) < 50:
                self.stdout.write(
                    self.style.WARNING('⚠ SECRET_KEY is too short (should be 50+ characters)')
                )
                warnings_found += 1
            else:
                self.stdout.write(self.style.SUCCESS('✓ SECRET_KEY length is adequate'))
        
        # Check 3: ALLOWED_HOSTS
        if settings.DEBUG:
            self.stdout.write(self.style.WARNING('⚠ Skipping ALLOWED_HOSTS check (DEBUG mode)'))
        elif not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['*']:
            self.stdout.write(
                self.style.ERROR('❌ ALLOWED_HOSTS is not configured properly')
            )
            issues_found += 1
        else:
            self.stdout.write(self.style.SUCCESS('✓ ALLOWED_HOSTS is configured'))
        
        # Check 4: CSRF protection
        if 'django.middleware.csrf.CsrfViewMiddleware' not in settings.MIDDLEWARE:
            self.stdout.write(
                self.style.ERROR('❌ CSRF middleware is not enabled')
            )
            issues_found += 1
        else:
            self.stdout.write(self.style.SUCCESS('✓ CSRF middleware is enabled'))
        
        # Check 5: Security middleware
        if 'django.middleware.security.SecurityMiddleware' not in settings.MIDDLEWARE:
            self.stdout.write(
                self.style.WARNING('⚠ Security middleware is not enabled')
            )
            warnings_found += 1
        else:
            self.stdout.write(self.style.SUCCESS('✓ Security middleware is enabled'))
        
        # Check 6: Session security
        if not getattr(settings, 'SESSION_COOKIE_HTTPONLY', False):
            self.stdout.write(
                self.style.ERROR('❌ SESSION_COOKIE_HTTPONLY is not enabled')
            )
            issues_found += 1
        else:
            self.stdout.write(self.style.SUCCESS('✓ SESSION_COOKIE_HTTPONLY is enabled'))
        
        if not getattr(settings, 'CSRF_COOKIE_HTTPONLY', False):
            self.stdout.write(
                self.style.ERROR('❌ CSRF_COOKIE_HTTPONLY is not enabled')
            )
            issues_found += 1
        else:
            self.stdout.write(self.style.SUCCESS('✓ CSRF_COOKIE_HTTPONLY is enabled'))
        
        # Check 7: HTTPS settings (production)
        if not settings.DEBUG:
            if not getattr(settings, 'SECURE_SSL_REDIRECT', False):
                self.stdout.write(
                    self.style.WARNING('⚠ SECURE_SSL_REDIRECT is not enabled')
                )
                warnings_found += 1
            else:
                self.stdout.write(self.style.SUCCESS('✓ SECURE_SSL_REDIRECT is enabled'))
            
            if not getattr(settings, 'SESSION_COOKIE_SECURE', False):
                self.stdout.write(
                    self.style.WARNING('⚠ SESSION_COOKIE_SECURE is not enabled')
                )
                warnings_found += 1
            else:
                self.stdout.write(self.style.SUCCESS('✓ SESSION_COOKIE_SECURE is enabled'))
        
        # Check 8: Password validators
        validators = getattr(settings, 'AUTH_PASSWORD_VALIDATORS', [])
        if len(validators) < 3:
            self.stdout.write(
                self.style.WARNING('⚠ Less than 3 password validators configured')
            )
            warnings_found += 1
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✓ {len(validators)} password validators configured')
            )
        
        # Check 9: Weak passwords (users with simple passwords)
        try:
            users_with_no_password = User.objects.filter(password='').count()
            if users_with_no_password > 0:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ {users_with_no_password} users have no password set'
                    )
                )
                issues_found += 1
            else:
                self.stdout.write(self.style.SUCCESS('✓ All users have passwords'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠ Could not check passwords: {e}'))
        
        # Check 10: Superuser accounts
        try:
            superusers = User.objects.filter(is_superuser=True).count()
            if superusers > 5:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠ {superusers} superuser accounts exist (recommend < 5)'
                    )
                )
                warnings_found += 1
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {superusers} superuser accounts')
                )
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠ Could not check superusers: {e}'))
        
        # Check 11: Rate limiting
        if not getattr(settings, 'ENABLE_RATE_LIMITING', False):
            self.stdout.write(
                self.style.WARNING('⚠ Rate limiting is not enabled')
            )
            warnings_found += 1
        else:
            self.stdout.write(self.style.SUCCESS('✓ Rate limiting is enabled'))
        
        # Check 12: Custom security middleware
        custom_middleware = [
            'core.middleware.SecurityHeadersMiddleware',
            'core.middleware.RateLimitMiddleware',
            'core.middleware.SecurityEventMiddleware',
        ]
        
        for mw in custom_middleware:
            if mw in settings.MIDDLEWARE:
                self.stdout.write(self.style.SUCCESS(f'✓ {mw.split(".")[-1]} is active'))
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ {mw.split(".")[-1]} is not active')
                )
                warnings_found += 1
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('Security Audit Summary'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        if issues_found == 0 and warnings_found == 0:
            self.stdout.write(self.style.SUCCESS('✓ No security issues found!'))
            return 0
        else:
            if issues_found > 0:
                self.stdout.write(
                    self.style.ERROR(f'❌ {issues_found} critical issues found')
                )
            if warnings_found > 0:
                self.stdout.write(
                    self.style.WARNING(f'⚠ {warnings_found} warnings found')
                )
            
            self.stdout.write('\nRecommendations:')
            self.stdout.write('1. Review settings_prod.py for production configuration')
            self.stdout.write('2. Ensure HTTPS is enabled in production')
            self.stdout.write('3. Use strong, unique SECRET_KEY')
            self.stdout.write('4. Enable all security middleware')
            self.stdout.write('5. Regular security audits and updates')
            self.stdout.write('')
