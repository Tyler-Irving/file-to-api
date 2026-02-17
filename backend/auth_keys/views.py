"""
Views for API key management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import APIKey
from .serializers import APIKeySerializer, APIKeyCreateSerializer


class APIKeyViewSet(viewsets.ViewSet):
    """
    API key management endpoints.
    
    - POST /api/v1/keys/ - Generate a new API key
    - GET /api/v1/keys/ - List your API keys (requires auth)
    - DELETE /api/v1/keys/{id}/ - Revoke an API key
    """
    
    def get_permissions(self):
        """Allow anyone to create a key, require auth for other actions."""
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()
    
    def create(self, request):
        """
        Generate a new API key.
        
        This endpoint is public - anyone can generate a key.
        In production, you might want to add email verification or reCAPTCHA.
        """
        serializer = APIKeyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Generate key
        api_key, full_key = APIKey.generate(
            name=serializer.validated_data['name']
        )
        
        return Response({
            'id': str(api_key.id),
            'name': api_key.name,
            'prefix': api_key.prefix,
            'key': full_key,
            'created_at': api_key.created_at,
            'warning': 'Save this key securely. It will not be shown again.',
        }, status=status.HTTP_201_CREATED)
    
    def list(self, request):
        """List API keys for the authenticated user."""
        if not hasattr(request, 'api_key'):
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Return just this key (we don't have multi-user yet)
        keys = APIKey.objects.filter(id=request.api_key.id, is_active=True)
        serializer = APIKeySerializer(keys, many=True)
        return Response(serializer.data)
    
    def destroy(self, request, pk=None):
        """Revoke an API key."""
        if not hasattr(request, 'api_key'):
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            api_key = APIKey.objects.get(id=pk)
        except APIKey.DoesNotExist:
            return Response(
                {'error': 'Not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Only allow revoking your own key
        if api_key.id != request.api_key.id:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Soft delete by marking inactive
        api_key.is_active = False
        api_key.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
