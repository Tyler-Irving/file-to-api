"""
Views for API key management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import APIKey


class APIKeyViewSet(viewsets.ViewSet):
    """
    API endpoints for API key management.
    """
    permission_classes = [AllowAny]  # Auth checked manually via api_key
    
    def list(self, request):
        """List all API keys for the authenticated user."""
        if not hasattr(request, 'api_key') or not request.api_key:
            return Response(
                {'error': True, 'message': 'API key required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # For now, just return the current API key
        # In a real system, you'd track multiple keys per user
        api_key = request.api_key
        return Response([{
            'id': str(api_key.id),
            'prefix': api_key.prefix,
            'name': api_key.name,
            'created_at': api_key.created_at.isoformat(),
            'is_active': api_key.is_active,
        }])
    
    def create(self, request):
        """Generate a new API key."""
        if not hasattr(request, 'api_key') or not request.api_key:
            return Response(
                {'error': True, 'message': 'API key required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        name = request.data.get('name', 'Untitled Key')
        api_key, full_key = APIKey.generate(name=name)
        
        return Response({
            'id': str(api_key.id),
            'prefix': api_key.prefix,
            'name': api_key.name,
            'created_at': api_key.created_at.isoformat(),
            'is_active': api_key.is_active,
            'full_key': full_key,  # Only shown once
        }, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, pk=None):
        """Delete an API key."""
        if not hasattr(request, 'api_key') or not request.api_key:
            return Response(
                {'error': True, 'message': 'API key required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            api_key = APIKey.objects.get(id=pk)
            
            # Don't allow deleting the current API key
            if api_key.id == request.api_key.id:
                return Response(
                    {'error': True, 'message': 'Cannot delete the current API key'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            api_key.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except APIKey.DoesNotExist:
            return Response(
                {'error': True, 'message': 'API key not found'},
                status=status.HTTP_404_NOT_FOUND
            )
