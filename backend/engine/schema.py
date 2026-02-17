"""
Schema detection engine for inferring Django field types from pandas DataFrames.
"""
import re
import pandas as pd
import logging
from datetime import datetime
from django.utils.text import slugify

logger = logging.getLogger(__name__)

# Mapping from detected data types to Django field types
DTYPE_MAP = {
    'int64': ('IntegerField', 'integer'),
    'int32': ('IntegerField', 'integer'),
    'float64': ('FloatField', 'float'),
    'float32': ('FloatField', 'float'),
    'bool': ('BooleanField', 'boolean'),
    'datetime64[ns]': ('DateTimeField', 'datetime'),
}

# Reserved Python/Django keywords to avoid
RESERVED_WORDS = {
    'id', 'pk', 'class', 'def', 'return', 'if', 'else', 'for', 'while', 'import',
    'from', 'as', 'try', 'except', 'finally', 'with', 'lambda', 'yield', 'global',
    'nonlocal', 'assert', 'pass', 'break', 'continue', 'raise', 'del', 'in', 'is',
    'not', 'and', 'or', 'true', 'false', 'none', 'self', 'cls',
}


def detect_schema(df: pd.DataFrame) -> list:
    """
    Analyze DataFrame columns and return field definitions.
    
    Args:
        df: pandas DataFrame to analyze
    
    Returns:
        list: List of column definitions with keys:
            - name: Original column name
            - field_name: Sanitized field name
            - field_type: Django field class name
            - data_type: Simple type (text, integer, float, boolean, date, datetime)
            - nullable: Whether the column has null values
            - unique: Whether all values are unique
            - max_length: For text fields, maximum observed length
            - sample_values: First 5 non-null values
            - position: Column order
    """
    columns = []
    
    for i, col in enumerate(df.columns):
        logger.debug(f'Analyzing column {i}: {col}')
        
        series = df[col]
        non_null_series = series.dropna()
        
        # If all values are null, default to text
        if len(non_null_series) == 0:
            field_info = {
                'name': col,
                'field_name': sanitize_field_name(col),
                'field_type': 'TextField',
                'data_type': 'text',
                'nullable': True,
                'unique': False,
                'max_length': None,
                'sample_values': [],
                'position': i,
            }
            columns.append(field_info)
            continue
        
        # Detect field type
        field_type, data_type, max_length = infer_field_type(non_null_series)
        
        # Check for nullability
        nullable = series.isna().any()
        
        # Check for uniqueness (only if reasonable number of rows)
        unique = False
        if len(df) <= 10000:  # Only check uniqueness for smaller datasets
            unique = len(non_null_series.unique()) == len(non_null_series)
        
        # Get sample values
        sample_values = non_null_series.head(5).tolist()
        # Convert datetime objects to strings for JSON serialization
        sample_values = [
            val.isoformat() if isinstance(val, (pd.Timestamp, datetime)) else val
            for val in sample_values
        ]
        
        field_info = {
            'name': col,
            'field_name': sanitize_field_name(col),
            'field_type': field_type,
            'data_type': data_type,
            'nullable': nullable,
            'unique': unique,
            'max_length': max_length,
            'sample_values': sample_values,
            'position': i,
        }
        
        columns.append(field_info)
    
    return columns


def infer_field_type(series: pd.Series) -> tuple:
    """
    Infer the best Django field type for a pandas Series.
    
    Priority order:
    1. Boolean
    2. Integer
    3. Float
    4. Date
    5. DateTime
    6. Text (CharField or TextField)
    
    Returns:
        tuple: (field_type, data_type, max_length)
    """
    dtype_str = str(series.dtype)
    
    # Check pandas dtype first
    if dtype_str in DTYPE_MAP:
        field_type, data_type = DTYPE_MAP[dtype_str]
        return field_type, data_type, None
    
    # For object dtype, try custom detection
    if dtype_str == 'object':
        # Try boolean
        if is_boolean_column(series):
            return 'BooleanField', 'boolean', None
        
        # Try datetime
        if is_datetime_column(series):
            return 'DateTimeField', 'datetime', None
        
        # Try date
        if is_date_column(series):
            return 'DateField', 'date', None
        
        # Try integer
        if is_integer_column(series):
            return 'IntegerField', 'integer', None
        
        # Try float
        if is_float_column(series):
            return 'FloatField', 'float', None
        
        # Default to text
        max_length = series.astype(str).str.len().max()
        if max_length <= 255:
            return 'CharField', 'text', min(max_length * 2, 500)  # Add buffer
        else:
            return 'TextField', 'text', None
    
    # Unknown dtype - default to text
    return 'TextField', 'text', None


def is_boolean_column(series: pd.Series, threshold=0.9) -> bool:
    """Check if series contains boolean-like values."""
    try:
        # Convert to string and lowercase
        str_values = series.astype(str).str.lower().str.strip()
        unique_values = set(str_values.unique())
        
        boolean_values = {
            'true', 'false', 'yes', 'no', '1', '0', 't', 'f', 'y', 'n',
            '1.0', '0.0', 'True', 'False', 'TRUE', 'FALSE', 'YES', 'NO'
        }
        
        # Check if all unique values are boolean-like
        return unique_values.issubset(boolean_values)
    except Exception:
        return False


def is_integer_column(series: pd.Series, threshold=0.95) -> bool:
    """Check if series contains integer values."""
    try:
        # Try converting to numeric
        converted = pd.to_numeric(series, errors='coerce')
        
        # Check how many values were successfully converted
        success_rate = converted.notna().sum() / len(series)
        if success_rate < threshold:
            return False
        
        # Check if all numeric values are integers
        numeric_values = converted.dropna()
        return (numeric_values == numeric_values.astype(int)).all()
    except Exception:
        return False


def is_float_column(series: pd.Series, threshold=0.95) -> bool:
    """Check if series contains float values."""
    try:
        converted = pd.to_numeric(series, errors='coerce')
        success_rate = converted.notna().sum() / len(series)
        return success_rate >= threshold
    except Exception:
        return False


def is_date_column(series: pd.Series, threshold=0.9) -> bool:
    """Check if series contains date values (without time component)."""
    try:
        # Try parsing as datetime
        converted = pd.to_datetime(series, errors='coerce')
        success_rate = converted.notna().sum() / len(series)
        
        if success_rate < threshold:
            return False
        
        # Check if time component is always midnight
        valid_dates = converted.dropna()
        is_date = (valid_dates.dt.hour == 0) & (valid_dates.dt.minute == 0) & (valid_dates.dt.second == 0)
        
        return is_date.mean() > 0.95  # Most values have no time component
    except Exception:
        return False


def is_datetime_column(series: pd.Series, threshold=0.9) -> bool:
    """Check if series contains datetime values."""
    try:
        converted = pd.to_datetime(series, errors='coerce')
        success_rate = converted.notna().sum() / len(series)
        return success_rate >= threshold
    except Exception:
        return False


def sanitize_field_name(name: str) -> str:
    """
    Convert column name to valid Python/Django field name.
    
    Rules:
    - Lowercase
    - Replace spaces and special chars with underscores
    - Remove consecutive underscores
    - Strip leading/trailing underscores
    - Prefix with 'col_' if starts with digit or is reserved word
    - Truncate to 63 characters (PostgreSQL limit)
    """
    # Convert to string and lowercase
    name = str(name).strip().lower()
    
    # Replace spaces and special characters with underscores
    name = re.sub(r'[^a-z0-9_]', '_', name)
    
    # Remove consecutive underscores
    name = re.sub(r'_+', '_', name)
    
    # Strip leading/trailing underscores
    name = name.strip('_')
    
    # Ensure not empty
    if not name:
        name = 'column'
    
    # Prefix if starts with digit
    if name[0].isdigit():
        name = f'col_{name}'
    
    # Prefix if reserved word
    if name in RESERVED_WORDS:
        name = f'field_{name}'
    
    # Truncate to 63 characters
    if len(name) > 63:
        name = name[:63]
    
    return name


def convert_dataframe_types(df: pd.DataFrame, schema: list) -> pd.DataFrame:
    """
    Convert DataFrame columns to match detected schema types.
    
    This ensures data is properly typed before insertion into the database.
    """
    df = df.copy()
    
    for col_info in schema:
        original_name = col_info['name']
        data_type = col_info['data_type']
        
        try:
            if data_type == 'boolean':
                # Convert to boolean
                df[original_name] = df[original_name].astype(str).str.lower().isin(['true', 'yes', '1', 't', 'y', '1.0'])
            
            elif data_type == 'integer':
                df[original_name] = pd.to_numeric(df[original_name], errors='coerce').astype('Int64')
            
            elif data_type == 'float':
                df[original_name] = pd.to_numeric(df[original_name], errors='coerce')
            
            elif data_type in ['date', 'datetime']:
                df[original_name] = pd.to_datetime(df[original_name], errors='coerce')
            
            # Text fields stay as-is
        
        except Exception as e:
            logger.warning(f'Error converting column {original_name} to {data_type}: {e}')
    
    return df
