"""
Main file processing pipeline.

Orchestrates: parsing → schema detection → table creation → data insertion → API generation
"""
import logging
from django.db import transaction
from .parser import FileParser
from .schema import detect_schema, convert_dataframe_types
from .table_builder import create_dynamic_table, bulk_insert
from .api_generator import generate_api
from .router import register_dataset_api

logger = logging.getLogger(__name__)


def process_uploaded_file(dataset):
    """
    Process an uploaded file and generate its API.
    
    This is the main entry point for file processing.
    
    Steps:
    1. Parse file into DataFrame
    2. Detect schema
    3. Save column definitions
    4. Create dynamic table
    5. Insert data
    6. Generate API
    7. Register routes
    8. Update dataset status
    
    Args:
        dataset: Dataset model instance (must have file attached)
    
    Raises:
        Exception: If any step fails
    """
    logger.info(f'Processing dataset: {dataset.id} ({dataset.name})')
    
    try:
        # Step 1: Parse file
        logger.info('Step 1: Parsing file...')
        parser = FileParser(dataset.file.path)
        df = parser.parse()
        logger.info(f'Parsed {len(df)} rows, {len(df.columns)} columns')
        
        # Step 2: Detect schema
        logger.info('Step 2: Detecting schema...')
        schema = detect_schema(df)
        logger.info(f'Detected {len(schema)} columns')
        
        # Step 3: Save column definitions
        logger.info('Step 3: Saving column definitions...')
        from core.models import DatasetColumn
        
        with transaction.atomic():
            # Delete existing columns (in case of re-processing)
            dataset.columns.all().delete()
            
            # Create new columns
            for col_info in schema:
                DatasetColumn.objects.create(
                    dataset=dataset,
                    name=col_info['name'],
                    field_name=col_info['field_name'],
                    data_type=col_info['data_type'],
                    field_type=col_info['field_type'],
                    nullable=col_info['nullable'],
                    unique=col_info['unique'],
                    max_length=col_info.get('max_length'),
                    sample_values=col_info['sample_values'],
                    position=col_info['position'],
                )
        
        logger.info('Saved column definitions')
        
        # Step 4: Create dynamic table
        logger.info('Step 4: Creating dynamic table...')
        create_dynamic_table(dataset.table_name, schema)
        logger.info(f'Created table: {dataset.table_name}')
        
        # Step 5: Convert DataFrame types and insert data
        logger.info('Step 5: Inserting data...')
        df_typed = convert_dataframe_types(df, schema)
        row_count = bulk_insert(dataset.table_name, schema, df_typed)
        logger.info(f'Inserted {row_count} rows')
        
        # Update dataset row count
        dataset.row_count = row_count
        dataset.save()
        
        # Step 6: Generate API
        logger.info('Step 6: Generating API...')
        viewset_class = generate_api(dataset)
        logger.info('Generated ViewSet and Serializer')
        
        # Step 7: Register routes
        logger.info('Step 7: Registering API routes...')
        register_dataset_api(dataset, viewset_class)
        logger.info(f'Registered routes at /api/v1/data/{dataset.slug}/')
        
        # Step 8: Update dataset status
        dataset.status = 'ready'
        dataset.error_message = ''
        dataset.save()
        
        logger.info(f'Successfully processed dataset: {dataset.slug}')
    
    except Exception as e:
        logger.error(f'Error processing dataset {dataset.id}: {e}', exc_info=True)
        
        # Update dataset with error
        dataset.status = 'error'
        dataset.error_message = str(e)
        dataset.save()
        
        raise
