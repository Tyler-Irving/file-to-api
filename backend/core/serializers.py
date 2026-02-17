"""
Serializers for dataset management.
"""
from rest_framework import serializers
from .models import Dataset, DatasetColumn


class DatasetColumnSerializer(serializers.ModelSerializer):
    """Serializer for dataset column metadata."""
    
    class Meta:
        model = DatasetColumn
        fields = [
            'name',
            'field_name',
            'data_type',
            'field_type',
            'nullable',
            'unique',
            'max_length',
            'sample_values',
            'position',
        ]


class DatasetListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for dataset list view."""
    
    api_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = [
            'id',
            'name',
            'slug',
            'status',
            'row_count',
            'created_at',
            'api_url',
        ]
    
    def get_api_url(self, obj):
        return obj.get_api_url()


class DatasetDetailSerializer(serializers.ModelSerializer):
    """Full dataset serializer with schema information."""
    
    columns = DatasetColumnSerializer(many=True, read_only=True)
    api_url = serializers.SerializerMethodField()
    docs_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = [
            'id',
            'name',
            'slug',
            'original_filename',
            'file_size',
            'status',
            'error_message',
            'row_count',
            'table_name',
            'columns',
            'api_url',
            'docs_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'slug',
            'table_name',
            'status',
            'error_message',
            'row_count',
            'created_at',
            'updated_at',
        ]
    
    def get_api_url(self, obj):
        return obj.get_api_url()
    
    def get_docs_url(self, obj):
        return f'/api/docs/#/data/{obj.slug}'


class DatasetUploadSerializer(serializers.ModelSerializer):
    """Serializer for file upload endpoint."""
    
    file = serializers.FileField(required=True)
    
    class Meta:
        model = Dataset
        fields = ['name', 'file']
    
    def validate_file(self, value):
        """Validate file size and type."""
        from django.conf import settings
        import magic
        
        # Check file size
        if value.size > settings.MAX_UPLOAD_SIZE:
            size_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            raise serializers.ValidationError(
                f'File too large. Maximum size is {size_mb}MB.'
            )
        
        # Check MIME type
        mime = magic.from_buffer(value.read(2048), mime=True)
        value.seek(0)  # Reset file pointer
        
        allowed_mimes = {
            'text/csv',
            'text/plain',  # Some CSV files are detected as plain text
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
        }
        
        if mime not in allowed_mimes:
            raise serializers.ValidationError(
                f'Unsupported file type: {mime}. Please upload CSV or Excel files only.'
            )
        
        return value
    
    def validate_name(self, value):
        """Validate dataset name."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError('Dataset name cannot be empty.')
        
        if len(value) > 255:
            raise serializers.ValidationError('Dataset name too long (max 255 characters).')
        
        return value.strip()
