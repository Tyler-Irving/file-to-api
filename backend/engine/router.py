"""
Dynamic URL router for dataset APIs.
"""
import logging
from rest_framework.routers import SimpleRouter

logger = logging.getLogger(__name__)

# Global router instance
dynamic_router = SimpleRouter()

# Track registered datasets
_registered_datasets = set()


def register_dataset_api(dataset, viewset_class):
    """
    Register a dataset's ViewSet with the dynamic router.
    
    Args:
        dataset: Dataset model instance
        viewset_class: Generated ViewSet class
    """
    if dataset.slug in _registered_datasets:
        logger.warning(f'Dataset already registered: {dataset.slug}')
        return
    
    try:
        # Register with router
        dynamic_router.register(
            dataset.slug,
            viewset_class,
            basename=dataset.slug
        )
        
        _registered_datasets.add(dataset.slug)
        logger.info(f'Registered API route: /api/v1/data/{dataset.slug}/')
    
    except Exception as e:
        logger.error(f'Error registering API for {dataset.slug}: {e}')
        raise


def unregister_dataset_api(slug: str):
    """
    Unregister a dataset's API.
    
    Note: SimpleRouter doesn't support unregistering, but we track it
    for future reference. In production, consider using a custom router
    or restart server after deletion.
    
    Args:
        slug: Dataset slug
    """
    if slug in _registered_datasets:
        _registered_datasets.remove(slug)
        logger.info(f'Unregistered API route (restart required): {slug}')
    
    # Note: Routes will still be active until server restart
    # For true dynamic unregistration, we'd need a custom router


def is_registered(slug: str) -> bool:
    """
    Check if a dataset is registered.
    
    Args:
        slug: Dataset slug
    
    Returns:
        bool: True if registered
    """
    return slug in _registered_datasets
