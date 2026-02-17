# File-to-API Backend Architecture

## Overview

This document describes the internal architecture of the File-to-API Django backend.

## Core Components

### 1. Request Flow

```
Client Upload → Authentication → File Validation → Processing Pipeline → API Generation → Response
```

**Detailed Flow:**

1. **Client uploads file** via `POST /api/v1/datasets/`
2. **API Key Authentication** validates `Authorization: Api-Key {key}` header
3. **Rate Limiting** checks request quota
4. **File Validation** checks size, MIME type, extension
5. **Processing Pipeline** executes:
   - Parse file (CSV/Excel → DataFrame)
   - Detect schema (infer types)
   - Create dynamic table (SQLite)
   - Insert data
   - Generate API (ViewSet + Serializer)
   - Register routes
6. **Response** returns dataset metadata + API URL

### 2. Schema Detection Algorithm

**Type Inference Priority:**

```
pandas dtype → boolean → datetime → date → integer → float → text
```

**Implementation (`engine/schema.py`):**

```python
def infer_field_type(series):
    # 1. Check pandas dtype
    if dtype in ['int64', 'float64', 'bool', 'datetime64[ns]']:
        return DTYPE_MAP[dtype]
    
    # 2. For 'object' dtype, try conversions
    if is_boolean_column(series):   # true/false/yes/no/1/0
        return 'BooleanField'
    if is_datetime_column(series):  # ISO dates with time
        return 'DateTimeField'
    if is_date_column(series):      # Dates without time
        return 'DateField'
    if is_integer_column(series):   # Numeric strings that are whole numbers
        return 'IntegerField'
    if is_float_column(series):     # Numeric strings with decimals
        return 'FloatField'
    
    # 3. Default to text
    max_length = series.str.len().max()
    if max_length <= 255:
        return 'CharField'
    else:
        return 'TextField'
```

**Validation Threshold:** 90% of values must match a type for it to be selected.

### 3. Dynamic Table Creation

**Table Naming:** `dataset_{uuid_short}` (e.g., `dataset_a1b2c3d4`)

**SQL Generation (`engine/table_builder.py`):**

```python
def create_dynamic_table(table_name, columns):
    col_defs = ['id INTEGER PRIMARY KEY AUTOINCREMENT']
    
    for col in columns:
        sql_type = FIELD_SQL_MAP[col['field_type']]
        null = 'NULL' if col['nullable'] else 'NOT NULL'
        unique = 'UNIQUE' if col['unique'] else ''
        
        col_defs.append(f'"{col["field_name"]}" {sql_type} {null} {unique}')
    
    sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(col_defs)})'
    cursor.execute(sql)
```

**Field Type Mapping:**

| Django Field | SQLite Type |
|--------------|-------------|
| IntegerField | INTEGER     |
| FloatField   | REAL        |
| BooleanField | INTEGER     |
| DateField    | TEXT        |
| DateTimeField| TEXT        |
| CharField    | TEXT        |
| TextField    | TEXT        |

### 4. Dynamic API Generation

**Generated Components:**

1. **Serializer Class** - DRF Serializer with fields matching schema
2. **ViewSet Class** - CRUD methods (list, retrieve, create, update, destroy)
3. **URL Route** - Registered with dynamic router

**Example (`engine/api_generator.py`):**

```python
def generate_api(dataset):
    # Build serializer fields
    fields = {
        'id': serializers.IntegerField(read_only=True),
        'name': serializers.CharField(required=True),
        'price': serializers.FloatField(required=True),
        # ... more fields
    }
    
    # Create serializer class dynamically
    SerializerClass = type(
        f'{dataset.slug}Serializer',
        (serializers.Serializer,),
        fields
    )
    
    # Create viewset class
    class DynamicViewSet(viewsets.ViewSet):
        serializer_class = SerializerClass
        
        def list(self, request):
            # Query dynamic table
            rows = query_table(dataset.table_name, dataset.columns)
            serializer = SerializerClass(rows, many=True)
            return Response(serializer.data)
        
        # ... create, retrieve, update, destroy
    
    return DynamicViewSet
```

### 5. Authentication & Security

**API Key Storage:**

- **Prefix** (8 chars) - stored in plaintext for lookup
- **Key part** (32+ chars) - hashed with SHA-256 + salt
- **Full key format:** `fta_{prefix}_{key}`

**Validation Flow:**

```python
def validate_key(full_key):
    prefix, key_part = parse_key(full_key)
    api_key = APIKey.objects.get(prefix=prefix)
    hashed = sha256(key_part + salt).hexdigest()
    return hashed == api_key.hashed_key
```

**Rate Limiting:**

- Upload: 10 requests/hour
- Read: 1000 requests/hour
- Write: 100 requests/hour

Implemented via `django-ratelimit` decorators on view methods.

### 6. Data Querying

**Raw SQL vs ORM:**

Dynamic tables use **raw SQL** (via `connection.cursor()`) because:
- Tables created at runtime aren't in Django models
- Direct SQL allows full control over dynamic column names
- Performance is equivalent for simple CRUD

**Parameterized Queries:**

```python
def query_table(table_name, columns, filters):
    sql = f'SELECT * FROM "{table_name}"'
    params = []
    
    if filters:
        conditions = []
        for field, value in filters.items():
            conditions.append(f'"{field}" = ?')
            params.append(value)
        sql += ' WHERE ' + ' AND '.join(conditions)
    
    cursor.execute(sql, params)
```

All values are parameterized (`?` placeholders) to prevent SQL injection.

## Database Schema

### Django-Managed Tables

**`core_dataset`**

| Column           | Type    | Description                    |
|------------------|---------|--------------------------------|
| id               | UUID    | Primary key                    |
| name             | VARCHAR | User-facing name               |
| slug             | VARCHAR | URL-safe identifier (unique)   |
| original_filename| VARCHAR | Uploaded filename              |
| file             | VARCHAR | File path in media/            |
| file_size        | INTEGER | Bytes                          |
| status           | VARCHAR | processing/ready/error         |
| error_message    | TEXT    | Error details                  |
| row_count        | INTEGER | Rows in dynamic table          |
| table_name       | VARCHAR | Dynamic table name             |
| api_key_id       | UUID    | Foreign key to auth_keys       |
| created_at       | DATETIME|                                |
| updated_at       | DATETIME|                                |

**`core_datasetcolumn`**

| Column      | Type    | Description                     |
|-------------|---------|---------------------------------|
| id          | INTEGER | Primary key                     |
| dataset_id  | UUID    | Foreign key                     |
| name        | VARCHAR | Original column name            |
| field_name  | VARCHAR | Sanitized field name            |
| data_type   | VARCHAR | text/integer/float/boolean/date |
| field_type  | VARCHAR | Django field class name         |
| nullable    | BOOLEAN |                                 |
| unique      | BOOLEAN |                                 |
| max_length  | INTEGER | For CharField                   |
| sample_values| JSON   | First 5 values                  |
| position    | INTEGER | Column order                    |

**`auth_keys_apikey`**

| Column      | Type     | Description              |
|-------------|----------|--------------------------|
| id          | UUID     | Primary key              |
| prefix      | VARCHAR  | First 8 chars (indexed)  |
| hashed_key  | VARCHAR  | SHA-256 hash             |
| name        | VARCHAR  | Friendly name            |
| is_active   | BOOLEAN  | Soft delete flag         |
| created_at  | DATETIME |                          |
| last_used   | DATETIME | Updated on each request  |

### Dynamic Tables

**Schema:** `dataset_{uuid_short}`

Example:

```sql
CREATE TABLE "dataset_a1b2c3d4" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    "date" TEXT NOT NULL,
    "product" TEXT NOT NULL,
    "price" REAL NOT NULL,
    "quantity" INTEGER NOT NULL,
    "in_stock" INTEGER NULL
)
```

## Performance Optimizations

### 1. SQLite WAL Mode

```python
DATABASES = {
    'default': {
        'OPTIONS': {
            'init_command': 'PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;'
        }
    }
}
```

Benefits:
- Concurrent reads during writes
- Faster commits
- Better crash recovery

### 2. Bulk Insert

Uses `executemany()` for batch insertion:

```python
cursor.executemany(
    f'INSERT INTO "{table_name}" VALUES (?, ?, ?)',
    [(row1_col1, row1_col2, row1_col3), ...]
)
```

~10x faster than individual inserts.

### 3. Eager Loading

```python
datasets = Dataset.objects.filter(...).select_related('api_key').prefetch_related('columns')
```

Reduces N+1 queries.

### 4. Static File Serving

WhiteNoise serves static files directly from Django with compression and caching.

## Testing Strategy

### Unit Tests

- Schema detection with various data types
- Table creation/deletion
- API key generation/validation
- Serializer validation

### Integration Tests

- Upload → API generation pipeline
- CRUD operations on dynamic tables
- Authentication flow
- Rate limiting

### Test Data

Use `faker` to generate realistic test datasets:

```python
def create_test_csv():
    return pd.DataFrame({
        'name': fake.name(),
        'email': fake.email(),
        'age': random.randint(18, 80),
        # ...
    })
```

## Monitoring & Logging

### Logging Levels

- **DEBUG:** Schema detection decisions, SQL queries
- **INFO:** Dataset processing steps, API registration
- **ERROR:** Processing failures, auth errors

### Key Metrics

- Upload processing time (target: <5 seconds)
- API response time (target: <200ms for list queries)
- Error rates per endpoint
- API key usage patterns

## Scaling Considerations

### Horizontal Scaling

- **Stateless design** - All state in database
- **Session storage** - Use Redis or database-backed sessions
- **File storage** - Move to S3/MinIO for multi-server deployments

### Database Scaling

- **PostgreSQL** - Replace SQLite for production
- **Connection pooling** - PgBouncer
- **Read replicas** - Separate read/write paths

### Async Processing

Add Celery for:
- File processing (move off request thread)
- Periodic cleanup (old files, unused datasets)
- Export jobs

## Security Hardening

### Input Validation

1. **File upload:**
   - Size limit (10MB)
   - MIME type check (python-magic)
   - Extension whitelist
   - CSV formula injection prevention

2. **SQL injection:**
   - All dynamic queries use parameterized placeholders
   - Table/column names validated by regex
   - No user input in SQL identifiers

3. **API key:**
   - Constant-time comparison
   - SHA-256 hashing with salt
   - Rate limiting per key

### OWASP Top 10 Coverage

| Vulnerability       | Mitigation                          |
|---------------------|-------------------------------------|
| Injection           | Parameterized queries               |
| Auth                | API key with secure storage         |
| XSS                 | Django auto-escaping (templates)    |
| Broken Access       | API key ownership checks            |
| Security Misconfig  | DEBUG=False, ALLOWED_HOSTS          |
| Sensitive Data      | Hashed keys, no plaintext storage   |
| Rate Limiting       | django-ratelimit                    |
| CSRF                | CSRF middleware enabled             |
| Components          | Regular dependency updates          |

## Future Architecture Changes

### Planned Improvements

1. **Async pipeline** - Celery tasks for file processing
2. **Caching layer** - Redis for frequently accessed datasets
3. **Search** - ElasticSearch for full-text search across datasets
4. **Webhooks** - Notify on data changes
5. **Real-time** - Django Channels for WebSocket subscriptions
6. **Multi-tenancy** - Organization/team models
7. **Audit log** - Track all data modifications

---

**Last Updated:** 2026-02-16
