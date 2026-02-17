"""
Custom API Key authentication for Django REST Framework.
"""
from rest_framework import authentication, exceptions
from .models import APIKey


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    API key authentication.
    
    Expects header: Authorization: Api-Key {key}
    Or query parameter: ?api_key={key}
    """
    
    keyword = 'Api-Key'
    
    def authenticate(self, request):
        """
        Authenticate the request using an API key.
        
        Returns:
            tuple: (user, auth) or None
        """
        # Try header first
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith(f'{self.keyword} '):
            key = auth_header.split(' ', 1)[1]
        else:
            # Try query parameter
            key = request.query_params.get('api_key')
        
        if not key:
            return None  # No key provided, let other auth methods try
        
        # Validate key
        api_key = APIKey.validate_key(key)
        
        if not api_key:
            raise exceptions.AuthenticationFailed('Invalid API key')
        
        # Store API key on request for later use
        request.api_key = api_key
        
        # Return a dummy user (we don't use Django users)
        # The API key itself serves as the principal
        return (None, api_key)
    
    def authenticate_header(self, request):
        """
        Return string to use in WWW-Authenticate header on 401 response.
        """
        return self.keyword
