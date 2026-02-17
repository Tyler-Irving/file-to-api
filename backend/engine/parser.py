"""
File parsing utilities for CSV and Excel files.
"""
import pandas as pd
import logging
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)


class FileParser:
    """Parse uploaded CSV or Excel files into pandas DataFrames."""
    
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.extension = self.file_path.suffix.lower()
    
    def parse(self):
        """
        Parse the file and return a pandas DataFrame.
        
        Returns:
            pd.DataFrame: Parsed data
        
        Raises:
            ValueError: If file format is unsupported or parsing fails
        """
        try:
            if self.extension == '.csv':
                return self._parse_csv()
            elif self.extension in ['.xlsx', '.xls']:
                return self._parse_excel()
            else:
                raise ValueError(f'Unsupported file format: {self.extension}')
        except Exception as e:
            logger.error(f'Error parsing file {self.file_path}: {e}')
            raise ValueError(f'Failed to parse file: {str(e)}')
    
    def _parse_csv(self):
        """Parse CSV file with automatic delimiter detection."""
        try:
            # Try reading with default settings
            df = pd.read_csv(self.file_path, encoding='utf-8')
        except Exception:
            # Try with different encoding
            try:
                df = pd.read_csv(self.file_path, encoding='latin-1')
            except Exception:
                # Last resort: let pandas detect encoding
                df = pd.read_csv(self.file_path, encoding_errors='ignore')
        
        return self._validate_dataframe(df)
    
    def _parse_excel(self):
        """Parse Excel file (supports .xlsx and .xls)."""
        # Read first sheet only
        df = pd.read_excel(self.file_path, sheet_name=0, engine='openpyxl' if self.extension == '.xlsx' else 'xlrd')
        return self._validate_dataframe(df)
    
    def _validate_dataframe(self, df):
        """
        Validate and clean the DataFrame.
        
        - Check row and column limits
        - Remove completely empty rows/columns
        - Ensure column names are strings
        """
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Check limits
        if len(df.columns) > settings.MAX_COLUMNS:
            raise ValueError(
                f'Too many columns ({len(df.columns)}). Maximum is {settings.MAX_COLUMNS}.'
            )
        
        if len(df) > settings.MAX_ROWS:
            raise ValueError(
                f'Too many rows ({len(df)}). Maximum is {settings.MAX_ROWS}.'
            )
        
        if len(df) == 0:
            raise ValueError('File contains no data rows.')
        
        if len(df.columns) == 0:
            raise ValueError('File contains no columns.')
        
        # Ensure column names are strings and not empty
        df.columns = [
            str(col).strip() if str(col).strip() else f'column_{i}'
            for i, col in enumerate(df.columns)
        ]
        
        # Check for duplicate column names
        if len(df.columns) != len(set(df.columns)):
            # Rename duplicates by appending numbers
            seen = {}
            new_cols = []
            for col in df.columns:
                if col in seen:
                    seen[col] += 1
                    new_cols.append(f'{col}_{seen[col]}')
                else:
                    seen[col] = 0
                    new_cols.append(col)
            df.columns = new_cols
        
        return df


def detect_delimiter(file_path):
    """
    Detect the delimiter used in a CSV file.
    
    Returns:
        str: Detected delimiter (comma, semicolon, tab, etc.)
    """
    import csv
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        sample = f.read(4096)
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample)
        return dialect.delimiter
