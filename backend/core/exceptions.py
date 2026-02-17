"""
Custom exception handling for File-to-API Platform.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error formatting.
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Standardize error format
        custom_response = {
            'error': True,
            'message': str(exc),
        }
        
        # Add field-specific errors if available
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                custom_response['message'] = response.data['detail']
            else:
                custom_response['errors'] = response.data
        
        response.data = custom_response
    
    return response
