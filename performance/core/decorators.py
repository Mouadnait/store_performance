"""
Security Decorators for Store Performance Platform
Rate limiting and access control decorators
"""
from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse, HttpResponseForbidden
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def rate_limit(requests=60, window=60, key_prefix='rate_limit'):
    """
    Rate limiting decorator for views.
    
    Args:
        requests: Number of allowed requests
        window: Time window in seconds
        key_prefix: Cache key prefix
    
    Usage:
        @rate_limit(requests=10, window=60)
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not getattr(settings, 'ENABLE_RATE_LIMITING', True):
                return view_func(request, *args, **kwargs)
            
            # Skip for staff users
            if request.user.is_authenticated and request.user.is_staff:
                return view_func(request, *args, **kwargs)
            
            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR', '')
            
            # Create cache key
            cache_key = f'{key_prefix}:{ip}:{view_func.__name__}'
            
            # Get current count
            count = cache.get(cache_key, 0)
            
            if count >= requests:
                logger.warning(
                    f"Rate limit exceeded for {ip} on {view_func.__name__}"
                )
                
                if request.path.startswith('/api/'):
                    return JsonResponse({
                        'error': 'Rate limit exceeded',
                        'retry_after': window
                    }, status=429)
                else:
                    return HttpResponseForbidden(
                        "Rate limit exceeded. Please try again later."
                    )
            
            # Increment counter
            cache.set(cache_key, count + 1, window)
            
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def require_api_key(view_func):
    """
    Require API key for API endpoints.
    
    Usage:
        @require_api_key
        def api_view(request):
            ...
    """
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        api_key = request.META.get('HTTP_X_API_KEY') or request.GET.get('api_key')
        
        if not api_key:
            return JsonResponse({
                'error': 'API key required'
            }, status=401)
        
        # Validate API key (you should store valid keys in database/cache)
        valid_key = settings.API_KEY if hasattr(settings, 'API_KEY') else None
        
        if api_key != valid_key:
            logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
            return JsonResponse({
                'error': 'Invalid API key'
            }, status=403)
        
        return view_func(request, *args, **kwargs)
    return wrapped


def require_verified_email(view_func):
    """
    Require verified email for sensitive operations.
    
    Usage:
        @require_verified_email
        def sensitive_view(request):
            ...
    """
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Authentication required")
        
        # Check if user has verified email (you need to add this field to User model)
        if hasattr(request.user, 'email_verified') and not request.user.email_verified:
            return HttpResponseForbidden(
                "Please verify your email address to access this feature"
            )
        
        return view_func(request, *args, **kwargs)
    return wrapped


def log_access(view_func):
    """
    Log all access to sensitive views.
    
    Usage:
        @log_access
        def sensitive_view(request):
            ...
    """
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        logger.info(
            f"Access to {view_func.__name__} by user {request.user} "
            f"from IP {request.META.get('REMOTE_ADDR')}"
        )
        return view_func(request, *args, **kwargs)
    return wrapped


def require_https(view_func):
    """
    Require HTTPS for sensitive views.
    
    Usage:
        @require_https
        def secure_view(request):
            ...
    """
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.is_secure() and not settings.DEBUG:
            return HttpResponseForbidden(
                "This page requires a secure connection (HTTPS)"
            )
        return view_func(request, *args, **kwargs)
    return wrapped


def sanitize_input(fields=None):
    """
    Sanitize user input to prevent XSS.
    
    Args:
        fields: List of POST/GET fields to sanitize
    
    Usage:
        @sanitize_input(fields=['name', 'email', 'message'])
        def contact_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if fields and request.method == 'POST':
                try:
                    import bleach
                    for field in fields:
                        if field in request.POST:
                            # Sanitize the field
                            cleaned = bleach.clean(
                                request.POST.get(field, ''),
                                tags=[],  # No HTML tags allowed
                                strip=True
                            )
                            request.POST._mutable = True
                            request.POST[field] = cleaned
                            request.POST._mutable = False
                except ImportError:
                    # Bleach not installed, use basic HTML escaping
                    from django.utils.html import escape
                    for field in fields:
                        if field in request.POST:
                            cleaned = escape(request.POST.get(field, ''))
                            request.POST._mutable = True
                            request.POST[field] = cleaned
                            request.POST._mutable = False
            
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def ajax_compatible(view_func):
    """
    Make a view AJAX-compatible.
    Returns only the content section when accessed via AJAX.
    
    Usage:
        @ajax_compatible
        def my_view(request):
            return render(request, 'template.html', context)
    """
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # If it's a template response, return the full HTML
            # The JavaScript will parse and extract the needed content
            return response
        
        return response
    return wrapped
