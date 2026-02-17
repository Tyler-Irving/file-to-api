"""
Rate limiting middleware.
"""
import time
from django.core.cache import cache
from django.http import JsonResponse


class RateLimitMiddleware:
    """
    Simple rate limiting middleware using Django cache.
    
    Limits are configured in settings:
    - RATE_LIMIT_UPLOAD
    - RATE_LIMIT_READ
    - RATE_LIMIT_WRITE
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Rate limiting is handled by decorators on views
        # This middleware is just a placeholder for future global limits
        response = self.get_response(request)
        return response
    
    def get_client_id(self, request):
        """
        Get a unique identifier for the client.
        
        Uses API key if available, otherwise IP address.
        """
        if hasattr(request, 'api_key'):
            return f'apikey:{request.api_key.prefix}'
        
        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        return f'ip:{ip}'
