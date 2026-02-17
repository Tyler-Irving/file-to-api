"""
Dynamic table creation and data insertion for SQLite.
"""
import logging
import pandas as pd
from django.db import connection
from datetime import datetime

logger = logging.getLogger(__name__)

# Map Django field types to SQLite column types
FIELD_SQL_MAP = {
    'IntegerField': 'INTEGER',
    'FloatField': 'REAL',
    'BooleanField': 'INTEGER',  # SQLite doesn't have native boolean
    'DateField': 'TEXT',
    'DateTimeField': 'TEXT',
    'CharField': 'TEXT',
    'TextField': 'TEXT',
}


def create_dynamic_table(table_name: str, columns: list):
    """
    Create a SQLite table from detected schema.
    
    Args:
        table_name: Name of the table to create
        columns: List of column definitions from schema detector
    """
    logger.info(f'Creating dynamic table: {table_name}')
    
    # Start with auto-increment primary key
    col_defs = ['id INTEGER PRIMARY KEY AUTOINCREMENT']
    
    # Add each column
    for col in columns:
        sql_type = FIELD_SQL_MAP.get(col['field_type'], 'TEXT')
        null_constraint = 'NULL' if col['nullable'] else 'NOT NULL'
        unique_constraint = 'UNIQUE' if col['unique'] else ''
        
        # Quote field name to handle reserved words and special characters
        col_def = f'"{col["field_name"]}" {sql_type} {null_constraint} {unique_constraint}'
        col_defs.append(col_def.strip())
    
    # Build CREATE TABLE statement
    sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(col_defs)})'
    
    logger.debug(f'SQL: {sql}')
    
    # Execute
    with connection.cursor() as cursor:
        cursor.execute(sql)
    
    logger.info(f'Successfully created table: {table_name}')


def bulk_insert(table_name: str, columns: list, df: pd.DataFrame) -> int:
    """
    Insert DataFrame rows into dynamic table.
    
    Args:
        table_name: Name of the target table
        columns: List of column definitions
        df: pandas DataFrame with data to insert
    
    Returns:
        int: Number of rows inserted
    """
    logger.info(f'Inserting {len(df)} rows into {table_name}')
    
    if len(df) == 0:
        return 0
    
    # Get field names in correct order
    field_names = [c['field_name'] for c in columns]
    original_names = [c['name'] for c in columns]
    
    # Build INSERT statement
    placeholders = ', '.join(['?'] * len(field_names))
    cols = ', '.join(f'"{f}"' for f in field_names)
    sql = f'INSERT INTO "{table_name}" ({cols}) VALUES ({placeholders})'
    
    # Prepare rows for insertion
    rows = []
    for _, row in df.iterrows():
        row_values = []
        for i, col_info in enumerate(columns):
            original_name = col_info['name']
            value = row[original_name]
            
            # Handle pandas NA/NaN
            if pd.isna(value):
                row_values.append(None)
            else:
                # Convert to appropriate Python type
                converted_value = convert_value_for_sqlite(value, col_info['data_type'])
                row_values.append(converted_value)
        
        rows.append(tuple(row_values))
    
    # Execute batch insert
    with connection.cursor() as cursor:
        cursor.executemany(sql, rows)
    
    logger.info(f'Successfully inserted {len(rows)} rows into {table_name}')
    return len(rows)


def convert_value_for_sqlite(value, data_type: str):
    """
    Convert Python value to SQLite-compatible format.
    
    Args:
        value: Value to convert
        data_type: Target data type (text, integer, float, boolean, date, datetime)
    
    Returns:
        Converted value suitable for SQLite
    """
    if pd.isna(value) or value is None:
        return None
    
    if data_type == 'boolean':
        # Convert to integer (0 or 1)
        if isinstance(value, bool):
            return 1 if value else 0
        # Handle string representations
        str_val = str(value).lower().strip()
        return 1 if str_val in ['true', 'yes', '1', 't', 'y', '1.0'] else 0
    
    elif data_type == 'integer':
        try:
            return int(float(value))  # Handle '1.0' strings
        except (ValueError, TypeError):
            return None
    
    elif data_type == 'float':
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    elif data_type in ['date', 'datetime']:
        # Convert to ISO format string
        if isinstance(value, (datetime, pd.Timestamp)):
            return value.isoformat()
        return str(value)
    
    elif data_type == 'text':
        return str(value)
    
    return str(value)


def drop_dynamic_table(table_name: str):
    """
    Drop a dynamic table.
    
    Args:
        table_name: Name of the table to drop
    """
    logger.info(f'Dropping table: {table_name}')
    
    sql = f'DROP TABLE IF EXISTS "{table_name}"'
    
    with connection.cursor() as cursor:
        cursor.execute(sql)
    
    logger.info(f'Successfully dropped table: {table_name}')


def get_table_row_count(table_name: str) -> int:
    """
    Get the number of rows in a table.
    
    Args:
        table_name: Name of the table
    
    Returns:
        int: Number of rows
    """
    sql = f'SELECT COUNT(*) FROM "{table_name}"'
    
    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchone()
        return result[0] if result else 0


def query_table(table_name: str, columns: list, filters: dict = None, 
                order_by: str = None, limit: int = None, offset: int = None) -> list:
    """
    Query a dynamic table.
    
    Args:
        table_name: Table to query
        columns: Column definitions
        filters: Dict of field_name -> value for filtering
        order_by: Field name to order by (prefix with '-' for descending)
        limit: Maximum number of rows to return
        offset: Number of rows to skip
    
    Returns:
        list: List of dicts representing rows
    """
    field_names = [c['field_name'] for c in columns]
    cols = ', '.join(f'"{f}"' for f in ['id'] + field_names)
    
    sql = f'SELECT {cols} FROM "{table_name}"'
    params = []
    
    # Add WHERE clause
    if filters:
        conditions = []
        for field, value in filters.items():
            conditions.append(f'"{field}" = ?')
            params.append(value)
        sql += ' WHERE ' + ' AND '.join(conditions)
    
    # Add ORDER BY
    if order_by:
        if order_by.startswith('-'):
            sql += f' ORDER BY "{order_by[1:]}" DESC'
        else:
            sql += f' ORDER BY "{order_by}" ASC'
    
    # Add LIMIT and OFFSET
    if limit:
        sql += f' LIMIT {limit}'
    if offset:
        sql += f' OFFSET {offset}'
    
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        # Convert to list of dicts
        all_fields = ['id'] + field_names
        return [
            {field: value for field, value in zip(all_fields, row)}
            for row in rows
        ]


def get_single_row(table_name: str, columns: list, row_id: int) -> dict:
    """
    Get a single row by ID.
    
    Args:
        table_name: Table to query
        columns: Column definitions
        row_id: Row ID
    
    Returns:
        dict: Row data or None if not found
    """
    results = query_table(table_name, columns, filters={'id': row_id}, limit=1)
    return results[0] if results else None


def insert_row(table_name: str, columns: list, data: dict) -> int:
    """
    Insert a single row.
    
    Args:
        table_name: Table to insert into
        columns: Column definitions
        data: Dict of field_name -> value
    
    Returns:
        int: ID of inserted row
    """
    field_names = [c['field_name'] for c in columns if c['field_name'] in data]
    values = [convert_value_for_sqlite(data[f], 
              next(c['data_type'] for c in columns if c['field_name'] == f))
              for f in field_names]
    
    placeholders = ', '.join(['?'] * len(field_names))
    cols = ', '.join(f'"{f}"' for f in field_names)
    sql = f'INSERT INTO "{table_name}" ({cols}) VALUES ({placeholders})'
    
    with connection.cursor() as cursor:
        cursor.execute(sql, values)
        return cursor.lastrowid


def update_row(table_name: str, columns: list, row_id: int, data: dict) -> bool:
    """
    Update a single row.
    
    Args:
        table_name: Table to update
        columns: Column definitions
        row_id: Row ID
        data: Dict of field_name -> value
    
    Returns:
        bool: True if row was updated
    """
    field_names = [c['field_name'] for c in columns if c['field_name'] in data]
    values = [convert_value_for_sqlite(data[f],
              next(c['data_type'] for c in columns if c['field_name'] == f))
              for f in field_names]
    
    set_clause = ', '.join(f'"{f}" = ?' for f in field_names)
    sql = f'UPDATE "{table_name}" SET {set_clause} WHERE id = ?'
    
    with connection.cursor() as cursor:
        cursor.execute(sql, values + [row_id])
        return cursor.rowcount > 0


def delete_row(table_name: str, row_id: int) -> bool:
    """
    Delete a single row.
    
    Args:
        table_name: Table to delete from
        row_id: Row ID
    
    Returns:
        bool: True if row was deleted
    """
    sql = f'DELETE FROM "{table_name}" WHERE id = ?'
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [row_id])
        return cursor.rowcount > 0
