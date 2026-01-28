"""
Custom Middleware for Store Performance Platform
Handles security, rate limiting, and monitoring
"""
import logging
import time
from django.core.cache import cache
from django.http import HttpResponseForbidden, JsonResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add comprehensive security headers to all responses.
    """
    def process_response(self, request, response):
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Remove server information
        if 'Server' in response:
            del response['Server']
        if 'X-Powered-By' in response:
            del response['X-Powered-By']
            
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Simple rate limiting middleware for API endpoints.
    Limits requests per IP address.
    """
    def process_request(self, request):
        if not getattr(settings, 'ENABLE_RATE_LIMITING', True):
            return None
        
        # Skip rate limiting for authenticated staff users
        if request.user.is_authenticated and request.user.is_staff:
            return None
        
        # Get client IP
        ip = self.get_client_ip(request)
        
        # Define rate limits (requests per minute)
        if request.path.startswith('/api/'):
            limit = 60  # 60 requests per minute for API
            window = 60
        elif request.path in ['/login/', '/signup/']:
            limit = 5  # 5 login attempts per minute
            window = 60
        else:
            limit = 120  # 120 requests per minute for other pages
            window = 60
        
        cache_key = f'rate_limit:{ip}:{request.path}'
        
        # Get current count
        count = cache.get(cache_key, 0)
        
        if count >= limit:
            logger.warning(f"Rate limit exceeded for IP {ip} on path {request.path}")
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Rate limit exceeded. Please try again later.',
                    'retry_after': window
                }, status=429)
            else:
                return HttpResponseForbidden("Rate limit exceeded. Please try again later.")
        
        # Increment counter
        cache.set(cache_key, count + 1, window)
        return None
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Log all requests for monitoring and debugging.
    """
    def process_request(self, request):
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # Log slow requests (> 2 seconds)
            if duration > 2.0:
                logger.warning(
                    f"Slow request: {request.method} {request.path} "
                    f"took {duration:.2f}s - Status: {response.status_code}"
                )
            
            # Log errors
            if response.status_code >= 400:
                logger.error(
                    f"Error response: {request.method} {request.path} "
                    f"- Status: {response.status_code} - User: {request.user}"
                )
        
        return response


class SecurityEventMiddleware(MiddlewareMixin):
    """
    Track and log security-related events.
    """
    def process_request(self, request):
        # Track suspicious patterns
        suspicious_paths = [
            'admin', 'phpmyadmin', 'wp-admin', '.env', 
            'config', 'backup', '.git', 'sql'
        ]
        
        path_lower = request.path.lower()
        if any(sus in path_lower for sus in suspicious_paths):
            ip = RateLimitMiddleware.get_client_ip(request)
            logger.warning(
                f"Suspicious request detected from IP {ip}: "
                f"{request.method} {request.path}"
            )
            
            # Track suspicious IPs
            cache_key = f'suspicious_ip:{ip}'
            count = cache.get(cache_key, 0)
            cache.set(cache_key, count + 1, 3600)  # 1 hour
            
            # Block if too many suspicious requests
            if count > 10:
                logger.critical(f"Blocking IP {ip} due to suspicious activity")
                return HttpResponseForbidden("Access denied.")
        
        return None


# Signal handlers for login tracking
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful login."""
    ip = RateLimitMiddleware.get_client_ip(request)
    logger.info(f"User login: {user.username} from IP {ip}")
    
    # Clear failed login attempts
    cache_key = f'failed_login:{ip}'
    cache.delete(cache_key)


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout."""
    if user:
        ip = RateLimitMiddleware.get_client_ip(request)
        logger.info(f"User logout: {user.username} from IP {ip}")


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """Log and track failed login attempts."""
    if request:
        ip = RateLimitMiddleware.get_client_ip(request)
        email = credentials.get('username', 'unknown')
        logger.warning(f"Failed login attempt for {email} from IP {ip}")
        
        # Track failed attempts
        cache_key = f'failed_login:{ip}'
        count = cache.get(cache_key, 0)
        cache.set(cache_key, count + 1, 900)  # 15 minutes
        
        # Alert if too many failures
        if count >= 5:
            logger.critical(
                f"Multiple failed login attempts detected from IP {ip} "
                f"(count: {count})"
            )
