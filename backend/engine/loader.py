"""
Load existing datasets and register their APIs on startup.
"""
import logging

logger = logging.getLogger(__name__)


def load_existing_datasets():
    """
    Load all 'ready' datasets and register their APIs.
    
    Called on Django startup (in core.apps.CoreConfig.ready())
    """
    try:
        # Import here to avoid circular imports
        from core.models import Dataset
        from .api_generator import generate_api
        from .router import register_dataset_api
        
        # Get all ready datasets
        datasets = Dataset.objects.filter(status='ready').select_related('api_key')
        
        logger.info(f'Loading {datasets.count()} existing datasets...')
        
        for dataset in datasets:
            try:
                # Generate API
                viewset_class = generate_api(dataset)
                
                # Register routes
                register_dataset_api(dataset, viewset_class)
                
                logger.info(f'Loaded dataset: {dataset.slug}')
            
            except Exception as e:
                logger.error(f'Error loading dataset {dataset.slug}: {e}')
        
        logger.info('Finished loading existing datasets')
    
    except Exception as e:
        # Don't crash on startup if there's an error
        logger.error(f'Error loading existing datasets: {e}')
