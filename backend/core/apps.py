from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        """Load dynamic APIs on startup."""
        # Import here to avoid circular imports
        from engine.loader import load_existing_datasets
        load_existing_datasets()
