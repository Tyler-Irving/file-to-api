"""
Core models for File-to-API Platform.
"""
import uuid
from django.db import models
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator


class Dataset(models.Model):
    """Represents an uploaded file and its generated API."""
    
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text='User-facing dataset name')
    slug = models.SlugField(max_length=255, unique=True, help_text='URL-safe identifier')
    
    # File metadata
    original_filename = models.CharField(max_length=255)
    file = models.FileField(
        upload_to='uploads/',
        validators=[FileExtensionValidator(allowed_extensions=['csv', 'xlsx', 'xls'])]
    )
    file_size = models.IntegerField(help_text='File size in bytes')
    
    # Processing status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    error_message = models.TextField(blank=True)
    
    # Dataset metrics
    row_count = models.IntegerField(default=0)
    table_name = models.CharField(max_length=255, help_text='Dynamic SQLite table name')
    
    # Ownership & timestamps
    api_key = models.ForeignKey('auth_keys.APIKey', on_delete=models.CASCADE, related_name='datasets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['api_key', 'created_at']),
        ]
    
    def __str__(self):
        return f'{self.name} ({self.slug})'
    
    def save(self, *args, **kwargs):
        """Auto-generate slug and table name if not set."""
        if not self.slug:
            base_slug = slugify(self.name)[:200]
            # Ensure uniqueness
            slug = base_slug
            counter = 1
            while Dataset.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        
        if not self.table_name:
            # Use first 8 chars of UUID for table name
            short_id = str(self.id).replace('-', '')[:8]
            self.table_name = f'dataset_{short_id}'
        
        super().save(*args, **kwargs)
    
    def get_api_url(self):
        """Return the base URL for this dataset's API."""
        return f'/api/v1/data/{self.slug}/'


class DatasetColumn(models.Model):
    """Represents a column in a dataset's schema."""
    
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='columns')
    
    # Column identity
    name = models.CharField(max_length=255, help_text='Original column name from file')
    field_name = models.CharField(max_length=255, help_text='Sanitized Python/Django field name')
    
    # Type information
    data_type = models.CharField(
        max_length=50,
        help_text='Detected type: text, integer, float, boolean, date, datetime'
    )
    field_type = models.CharField(
        max_length=50,
        help_text='Django field class name'
    )
    
    # Constraints
    nullable = models.BooleanField(default=True)
    unique = models.BooleanField(default=False)
    max_length = models.IntegerField(null=True, blank=True, help_text='For CharField')
    
    # Metadata
    sample_values = models.JSONField(default=list, help_text='First 5 values for preview')
    position = models.IntegerField(help_text='Column order in original file')
    
    class Meta:
        ordering = ['position']
        unique_together = [['dataset', 'field_name']]
    
    def __str__(self):
        return f'{self.dataset.slug}.{self.field_name} ({self.data_type})'
