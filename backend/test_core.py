"""
Quick test suite for core functionality.
Run with: python manage.py test
"""
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from auth_keys.models import APIKey
from core.models import Dataset, DatasetColumn
from engine.schema import detect_schema, sanitize_field_name
import pandas as pd


class SchemaDetectionTests(TestCase):
    """Test schema detection algorithm."""
    
    def test_integer_detection(self):
        """Test integer type detection."""
        df = pd.DataFrame({'numbers': [1, 2, 3, 4, 5]})
        schema = detect_schema(df)
        self.assertEqual(schema[0]['data_type'], 'integer')
    
    def test_float_detection(self):
        """Test float type detection."""
        df = pd.DataFrame({'prices': [1.99, 2.50, 3.75]})
        schema = detect_schema(df)
        self.assertEqual(schema[0]['data_type'], 'float')
    
    def test_boolean_detection(self):
        """Test boolean type detection."""
        df = pd.DataFrame({'flags': ['true', 'false', 'true', 'false']})
        schema = detect_schema(df)
        self.assertEqual(schema[0]['data_type'], 'boolean')
    
    def test_date_detection(self):
        """Test date type detection."""
        df = pd.DataFrame({'dates': pd.to_datetime(['2026-01-01', '2026-01-02', '2026-01-03'])})
        schema = detect_schema(df)
        self.assertIn(schema[0]['data_type'], ['date', 'datetime'])
    
    def test_text_detection(self):
        """Test text type detection."""
        df = pd.DataFrame({'names': ['Alice', 'Bob', 'Charlie']})
        schema = detect_schema(df)
        self.assertEqual(schema[0]['data_type'], 'text')
    
    def test_nullable_detection(self):
        """Test nullable field detection."""
        df = pd.DataFrame({'optional': [1, None, 3, None, 5]})
        schema = detect_schema(df)
        self.assertTrue(schema[0]['nullable'])
    
    def test_non_nullable_detection(self):
        """Test non-nullable field detection."""
        df = pd.DataFrame({'required': [1, 2, 3, 4, 5]})
        schema = detect_schema(df)
        self.assertFalse(schema[0]['nullable'])


class FieldNameSanitizationTests(TestCase):
    """Test field name sanitization."""
    
    def test_basic_sanitization(self):
        """Test basic column name cleaning."""
        self.assertEqual(sanitize_field_name('Product Name'), 'product_name')
    
    def test_special_chars(self):
        """Test special character removal."""
        self.assertEqual(sanitize_field_name('Price ($)'), 'price')
    
    def test_reserved_words(self):
        """Test reserved word handling."""
        self.assertEqual(sanitize_field_name('class'), 'field_class')
        self.assertEqual(sanitize_field_name('id'), 'field_id')
    
    def test_leading_number(self):
        """Test leading number handling."""
        self.assertEqual(sanitize_field_name('1st_place'), 'col_1st_place')
    
    def test_multiple_underscores(self):
        """Test consecutive underscore removal."""
        self.assertEqual(sanitize_field_name('a___b___c'), 'a_b_c')


class APIKeyTests(TestCase):
    """Test API key generation and validation."""
    
    def test_key_generation(self):
        """Test API key generation."""
        api_key, full_key = APIKey.generate('Test Key')
        
        self.assertIsNotNone(api_key)
        self.assertIsNotNone(full_key)
        self.assertTrue(full_key.startswith('fta_'))
        self.assertEqual(len(full_key.split('_')), 3)
    
    def test_key_validation_success(self):
        """Test valid key validation."""
        api_key, full_key = APIKey.generate('Test Key')
        
        validated = APIKey.validate_key(full_key)
        self.assertIsNotNone(validated)
        self.assertEqual(validated.id, api_key.id)
    
    def test_key_validation_failure(self):
        """Test invalid key rejection."""
        validated = APIKey.validate_key('fta_invalid_key')
        self.assertIsNone(validated)
    
    def test_key_uniqueness(self):
        """Test that each key is unique."""
        key1, full1 = APIKey.generate('Key 1')
        key2, full2 = APIKey.generate('Key 2')
        
        self.assertNotEqual(full1, full2)
        self.assertNotEqual(key1.prefix, key2.prefix)


class DatasetModelTests(TestCase):
    """Test Dataset model."""
    
    def setUp(self):
        """Create test API key."""
        self.api_key, _ = APIKey.generate('Test Key')
    
    def test_slug_generation(self):
        """Test automatic slug generation."""
        dataset = Dataset.objects.create(
            name='My Test Dataset',
            original_filename='test.csv',
            file_size=1024,
            api_key=self.api_key,
        )
        
        self.assertEqual(dataset.slug, 'my-test-dataset')
    
    def test_table_name_generation(self):
        """Test automatic table name generation."""
        dataset = Dataset.objects.create(
            name='Test Dataset',
            original_filename='test.csv',
            file_size=1024,
            api_key=self.api_key,
        )
        
        self.assertTrue(dataset.table_name.startswith('dataset_'))
    
    def test_api_url(self):
        """Test API URL generation."""
        dataset = Dataset.objects.create(
            name='Test Dataset',
            original_filename='test.csv',
            file_size=1024,
            api_key=self.api_key,
        )
        
        expected_url = f'/api/v1/data/{dataset.slug}/'
        self.assertEqual(dataset.get_api_url(), expected_url)


class IntegrationTests(TestCase):
    """Integration tests for the full pipeline."""
    
    def setUp(self):
        """Set up test environment."""
        self.api_key, self.full_key = APIKey.generate('Test Key')
    
    def test_csv_upload_flow(self):
        """Test complete CSV upload and processing flow."""
        # This would require actual file upload and processing
        # Skipped for brevity - implement in full test suite
        pass


if __name__ == '__main__':
    import django
    django.setup()
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['__main__'])
