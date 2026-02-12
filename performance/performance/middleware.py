"""
Middleware to handle cache control and prevent stale CSS/JS loading.
This ensures that navigating between pages loads fresh static files.
"""

from django.utils.deprecation import MiddlewareMixin


class NoCacheMiddleware(MiddlewareMixin):
    """
    Middleware to disable caching of HTML pages in development.
    This prevents issues where CSS/JS files don't load when navigating between pages.
    """
    
    def process_response(self, request, response):
        # Disable caching for HTML pages
        if 'text/html' in response.get('Content-Type', ''):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        # Allow caching for static files (CSS, JS, images) but with validation
        elif any(response.get('Content-Type', '').startswith(ct) for ct in ['text/css', 'application/javascript', 'image']):
            response['Cache-Control'] = 'public, max-age=3600, must-revalidate'
        
        return response
