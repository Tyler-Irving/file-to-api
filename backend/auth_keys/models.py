"""
API Key model for authentication.
"""
import uuid
import secrets
import hashlib
from django.db import models
from django.conf import settings


class APIKey(models.Model):
    """
    API key for authenticating requests.
    
    Keys are stored as: prefix (8 chars) + hashed key (SHA-256)
    Full key format: fta_{prefix}_{random}
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Key components
    prefix = models.CharField(max_length=8, unique=True, db_index=True)
    hashed_key = models.CharField(max_length=128)  # SHA-256 hex = 64 chars
    
    # Metadata
    name = models.CharField(max_length=255, help_text='Friendly name for this key')
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['prefix', 'is_active']),
        ]
    
    def __str__(self):
        return f'{self.name} ({self.prefix}***)'
    
    @classmethod
    def generate(cls, name: str) -> tuple:
        """
        Generate a new API key.
        
        Args:
            name: Friendly name for the key
        
        Returns:
            tuple: (APIKey instance, full_key_string)
            The full key is only returned once and never stored.
        """
        # Generate random components
        prefix = secrets.token_hex(4)  # 8 characters
        key_part = secrets.token_urlsafe(32)  # ~43 characters
        
        # Full key format: fta_{prefix}_{key}
        full_key = f'fta_{prefix}_{key_part}'
        
        # Hash the key part for storage
        hashed = hashlib.sha256(
            f'{key_part}{settings.API_KEY_SALT}'.encode()
        ).hexdigest()
        
        # Create record
        api_key = cls.objects.create(
            prefix=prefix,
            hashed_key=hashed,
            name=name,
        )
        
        return api_key, full_key
    
    @classmethod
    def validate_key(cls, full_key: str):
        """
        Validate a full API key and return the APIKey instance.
        
        Args:
            full_key: Full key string (fta_{prefix}_{key})
        
        Returns:
            APIKey instance or None if invalid
        """
        try:
            # Parse key
            if not full_key.startswith('fta_'):
                return None
            
            parts = full_key.split('_')
            if len(parts) != 3:
                return None
            
            prefix = parts[1]
            key_part = parts[2]
            
            # Look up by prefix
            try:
                api_key = cls.objects.get(prefix=prefix, is_active=True)
            except cls.DoesNotExist:
                return None
            
            # Verify hash
            hashed = hashlib.sha256(
                f'{key_part}{settings.API_KEY_SALT}'.encode()
            ).hexdigest()
            
            if hashed != api_key.hashed_key:
                return None
            
            # Update last used timestamp
            from django.utils import timezone
            api_key.last_used = timezone.now()
            api_key.save(update_fields=['last_used'])
            
            return api_key
        
        except Exception:
            return None
