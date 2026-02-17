"""
Views for dataset management.
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.conf import settings

from .models import Dataset
from .serializers import (
    DatasetListSerializer,
    DatasetDetailSerializer,
    DatasetUploadSerializer,
)
from engine.processor import process_uploaded_file

logger = logging.getLogger(__name__)


class DatasetViewSet(viewsets.ModelViewSet):
    """
    API endpoints for dataset management.
    
    list: Get all datasets for the authenticated API key
    retrieve: Get dataset details including schema
    create: Upload a new file and create dataset
    destroy: Delete dataset and associated table
    """
    
    queryset = Dataset.objects.all()
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DatasetUploadSerializer
        elif self.action == 'list':
            return DatasetListSerializer
        return DatasetDetailSerializer
    
    def get_queryset(self):
        """Filter datasets by authenticated API key."""
        if hasattr(self.request, 'api_key'):
            return Dataset.objects.filter(api_key=self.request.api_key)
        return Dataset.objects.none()
    
    @method_decorator(ratelimit(key='user', rate=settings.RATE_LIMIT_UPLOAD, method='POST'))
    def create(self, request, *args, **kwargs):
        """
        Upload a file and create a dataset.
        
        The file is processed asynchronously (or synchronously for MVP).
        Returns immediately with status='processing'.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create initial dataset record
        name = serializer.validated_data.get('name')
        if not name:
            name = serializer.validated_data['file'].name
        
        dataset = Dataset.objects.create(
            name=name,
            original_filename=serializer.validated_data['file'].name,
            file=serializer.validated_data['file'],
            file_size=serializer.validated_data['file'].size,
            api_key=request.api_key,
            status='processing',
        )
        
        # Process file synchronously (for MVP; use Celery for production)
        try:
            process_uploaded_file(dataset)
            dataset.refresh_from_db()
        except Exception as e:
            logger.error(f'Error processing dataset {dataset.id}: {e}', exc_info=True)
            dataset.status = 'error'
            dataset.error_message = str(e)
            dataset.save()
        
        # Return full details
        output_serializer = DatasetDetailSerializer(dataset)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @method_decorator(ratelimit(key='user', rate=settings.RATE_LIMIT_WRITE, method='DELETE'))
    def destroy(self, request, *args, **kwargs):
        """
        Delete a dataset and its associated table.
        """
        dataset = self.get_object()
        
        # Drop the dynamic table
        from engine.table_builder import drop_dynamic_table
        try:
            drop_dynamic_table(dataset.table_name)
        except Exception as e:
            logger.error(f'Error dropping table {dataset.table_name}: {e}')
        
        # Unregister API
        from engine.router import unregister_dataset_api
        unregister_dataset_api(dataset.slug)
        
        # Delete dataset record (file will be deleted by Django)
        dataset.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def schema(self, request, slug=None):
        """Get detailed schema information for a dataset."""
        dataset = self.get_object()
        from .serializers import DatasetColumnSerializer
        columns = DatasetColumnSerializer(dataset.columns.all(), many=True)
        return Response({
            'dataset': dataset.slug,
            'columns': columns.data,
        })
