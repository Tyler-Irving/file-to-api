"""
Serializers for API key management.
"""
from rest_framework import serializers
from .models import APIKey


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for listing API keys."""
    
    class Meta:
        model = APIKey
        fields = ['id', 'name', 'prefix', 'is_active', 'created_at', 'last_used']
        read_only_fields = ['id', 'prefix', 'created_at', 'last_used']


class APIKeyCreateSerializer(serializers.Serializer):
    """Serializer for creating API keys."""
    
    name = serializers.CharField(
        max_length=255,
        required=True,
        help_text='Friendly name for this API key'
    )
    
    def validate_name(self, value):
        """Validate key name."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError('Name cannot be empty.')
        return value.strip()
