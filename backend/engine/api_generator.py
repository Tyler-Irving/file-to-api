"""
Dynamic API generation for datasets.

Creates ViewSets and Serializers at runtime based on detected schema.
"""
import logging
from rest_framework import serializers, viewsets, status
from rest_framework.response import Response
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.conf import settings

from .table_builder import (
    query_table, get_single_row, insert_row, 
    update_row, delete_row, get_table_row_count
)

logger = logging.getLogger(__name__)

# Global registry of generated APIs
_API_REGISTRY = {}  # slug -> (ViewSet, Serializer)


def generate_api(dataset):
    """
    Generate a complete REST API for a dataset.
    
    Creates:
    - Serializer class with fields matching the schema
    - ViewSet class with full CRUD operations
    
    Args:
        dataset: Dataset model instance
    
    Returns:
        type: Generated ViewSet class
    """
    logger.info(f'Generating API for dataset: {dataset.slug}')
    
    # Get column definitions
    columns = list(dataset.columns.all().order_by('position'))
    
    # Build serializer fields
    serializer_fields = generate_serializer_fields(columns)
    
    # Create dynamic serializer class
    serializer_class = create_serializer_class(dataset.slug, serializer_fields)
    
    # Create dynamic viewset class
    viewset_class = create_viewset_class(dataset, columns, serializer_class)
    
    # Store in registry
    _API_REGISTRY[dataset.slug] = (viewset_class, serializer_class)
    
    logger.info(f'Successfully generated API for: {dataset.slug}')
    return viewset_class


def generate_serializer_fields(columns):
    """
    Generate DRF serializer fields from column definitions.
    
    Args:
        columns: List of DatasetColumn instances
    
    Returns:
        dict: Field name -> serializer field instance
    """
    FIELD_MAP = {
        'text': serializers.CharField,
        'integer': serializers.IntegerField,
        'float': serializers.FloatField,
        'boolean': serializers.BooleanField,
        'date': serializers.DateField,
        'datetime': serializers.DateTimeField,
    }
    
    fields = {
        'id': serializers.IntegerField(read_only=True),
    }
    
    for col in columns:
        field_class = FIELD_MAP.get(col.data_type, serializers.CharField)
        
        field_kwargs = {
            'required': not col.nullable,
            'allow_null': col.nullable,
        }
        
        # Add max_length for CharField
        if col.data_type == 'text' and col.max_length:
            field_kwargs['max_length'] = col.max_length
        
        fields[col.field_name] = field_class(**field_kwargs)
    
    return fields


def create_serializer_class(slug: str, fields: dict):
    """
    Dynamically create a Serializer class.
    
    Args:
        slug: Dataset slug (for class name)
        fields: Dict of field_name -> serializer field
    
    Returns:
        type: Serializer class
    """
    class_name = f'{slug.replace("-", "_").title()}Serializer'
    
    # Add Meta class
    class Meta:
        fields = list(fields.keys())
    
    fields['Meta'] = Meta
    
    # Create the serializer class
    serializer_class = type(class_name, (serializers.Serializer,), fields)
    
    return serializer_class


def create_viewset_class(dataset, columns, serializer_class):
    """
    Dynamically create a ViewSet class with CRUD operations.
    
    Args:
        dataset: Dataset model instance
        columns: List of DatasetColumn instances
        serializer_class: Generated serializer class
    
    Returns:
        type: ViewSet class
    """
    table_name = dataset.table_name
    slug = dataset.slug
    
    class DynamicViewSet(viewsets.ViewSet):
        """Auto-generated REST API for dataset."""
        
        serializer_class = serializer_class
        
        def get_permissions(self):
            """Check that request is authenticated with dataset owner's API key."""
            from rest_framework.permissions import IsAuthenticated
            return [IsAuthenticated()]
        
        def check_ownership(self, request):
            """Verify that the API key owns this dataset."""
            if not hasattr(request, 'api_key'):
                return False
            return request.api_key == dataset.api_key
        
        @method_decorator(ratelimit(key='user', rate=settings.RATE_LIMIT_READ, method='GET'))
        def list(self, request):
            """List all rows with pagination and filtering."""
            if not self.check_ownership(request):
                return Response(
                    {'error': 'Unauthorized'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get query parameters
            page = int(request.query_params.get('page', 1))
            page_size = min(int(request.query_params.get('page_size', 25)), 100)
            order_by = request.query_params.get('ordering', None)
            
            # Build filters from query params
            filters = {}
            for col in columns:
                if col.field_name in request.query_params:
                    filters[col.field_name] = request.query_params[col.field_name]
            
            # Calculate offset
            offset = (page - 1) * page_size
            
            # Query table
            rows = query_table(
                table_name,
                columns,
                filters=filters if filters else None,
                order_by=order_by,
                limit=page_size,
                offset=offset
            )
            
            # Get total count
            total_count = get_table_row_count(table_name)
            
            # Serialize
            serializer = serializer_class(rows, many=True)
            
            return Response({
                'count': total_count,
                'next': f'?page={page + 1}' if offset + page_size < total_count else None,
                'previous': f'?page={page - 1}' if page > 1 else None,
                'results': serializer.data,
            })
        
        @method_decorator(ratelimit(key='user', rate=settings.RATE_LIMIT_READ, method='GET'))
        def retrieve(self, request, pk=None):
            """Get a single row by ID."""
            if not self.check_ownership(request):
                return Response(
                    {'error': 'Unauthorized'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            try:
                row_id = int(pk)
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid ID'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            row = get_single_row(table_name, columns, row_id)
            
            if not row:
                return Response(
                    {'error': 'Not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = serializer_class(row)
            return Response(serializer.data)
        
        @method_decorator(ratelimit(key='user', rate=settings.RATE_LIMIT_WRITE, method='POST'))
        def create(self, request):
            """Create a new row."""
            if not self.check_ownership(request):
                return Response(
                    {'error': 'Unauthorized'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Insert row
            row_id = insert_row(table_name, columns, serializer.validated_data)
            
            # Fetch created row
            row = get_single_row(table_name, columns, row_id)
            output_serializer = serializer_class(row)
            
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        
        @method_decorator(ratelimit(key='user', rate=settings.RATE_LIMIT_WRITE, method='PUT'))
        def update(self, request, pk=None):
            """Update a row (full update)."""
            if not self.check_ownership(request):
                return Response(
                    {'error': 'Unauthorized'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            try:
                row_id = int(pk)
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid ID'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if row exists
            existing = get_single_row(table_name, columns, row_id)
            if not existing:
                return Response(
                    {'error': 'Not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Update row
            update_row(table_name, columns, row_id, serializer.validated_data)
            
            # Fetch updated row
            row = get_single_row(table_name, columns, row_id)
            output_serializer = serializer_class(row)
            
            return Response(output_serializer.data)
        
        @method_decorator(ratelimit(key='user', rate=settings.RATE_LIMIT_WRITE, method='PATCH'))
        def partial_update(self, request, pk=None):
            """Update a row (partial update)."""
            if not self.check_ownership(request):
                return Response(
                    {'error': 'Unauthorized'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            try:
                row_id = int(pk)
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid ID'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if row exists
            existing = get_single_row(table_name, columns, row_id)
            if not existing:
                return Response(
                    {'error': 'Not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = serializer_class(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            # Update row
            update_row(table_name, columns, row_id, serializer.validated_data)
            
            # Fetch updated row
            row = get_single_row(table_name, columns, row_id)
            output_serializer = serializer_class(row)
            
            return Response(output_serializer.data)
        
        @method_decorator(ratelimit(key='user', rate=settings.RATE_LIMIT_WRITE, method='DELETE'))
        def destroy(self, request, pk=None):
            """Delete a row."""
            if not self.check_ownership(request):
                return Response(
                    {'error': 'Unauthorized'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            try:
                row_id = int(pk)
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid ID'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Delete row
            deleted = delete_row(table_name, row_id)
            
            if not deleted:
                return Response(
                    {'error': 'Not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(status=status.HTTP_204_NO_CONTENT)
    
    # Set a meaningful class name
    DynamicViewSet.__name__ = f'{slug.replace("-", "_").title()}ViewSet'
    
    return DynamicViewSet


def get_api(slug: str):
    """
    Get a registered API by slug.
    
    Args:
        slug: Dataset slug
    
    Returns:
        tuple: (ViewSet class, Serializer class) or None
    """
    return _API_REGISTRY.get(slug)


def unregister_api(slug: str):
    """
    Remove an API from the registry.
    
    Args:
        slug: Dataset slug
    """
    if slug in _API_REGISTRY:
        del _API_REGISTRY[slug]
        logger.info(f'Unregistered API: {slug}')
