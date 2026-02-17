# API Testing Guide

Complete guide for testing the File-to-API platform endpoints.

## Prerequisites

1. Backend server running: `python manage.py runserver`
2. `jq` installed (for pretty JSON): `sudo apt install jq` or `brew install jq`

## Environment Variables

```bash
export API_URL="http://localhost:8000/api/v1"
export API_KEY="your-api-key-here"
```

---

## 1. Generate API Key

```bash
curl -X POST $API_URL/keys/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Key"}' | jq
```

**Expected Response:**

```json
{
  "id": "a1b2c3d4-...",
  "name": "Test Key",
  "prefix": "ab12cd34",
  "key": "fta_ab12cd34_xK9mN...",
  "created_at": "2026-02-16T23:00:00Z",
  "warning": "Save this key securely. It will not be shown again."
}
```

**Save the key:**

```bash
export API_KEY="fta_ab12cd34_xK9mN..."
```

---

## 2. Upload CSV File

```bash
curl -X POST $API_URL/datasets/ \
  -H "Authorization: Api-Key $API_KEY" \
  -F "file=@sample_data.csv" \
  -F "name=Sales Data" | jq
```

**Expected Response:**

```json
{
  "id": "...",
  "slug": "sales-data",
  "name": "Sales Data",
  "status": "ready",
  "row_count": 10,
  "columns": [
    {
      "name": "Date",
      "field_name": "date",
      "data_type": "date",
      "nullable": false
    },
    {
      "name": "Product",
      "field_name": "product",
      "data_type": "text",
      "nullable": false
    },
    {
      "name": "Price",
      "field_name": "price",
      "data_type": "float",
      "nullable": false
    }
  ],
  "api_url": "/api/v1/data/sales-data/",
  "docs_url": "/api/docs/#/data/sales-data"
}
```

**Save the slug:**

```bash
export DATASET_SLUG="sales-data"
```

---

## 3. List All Datasets

```bash
curl -X GET $API_URL/datasets/ \
  -H "Authorization: Api-Key $API_KEY" | jq
```

---

## 4. Get Dataset Details

```bash
curl -X GET $API_URL/datasets/$DATASET_SLUG/ \
  -H "Authorization: Api-Key $API_KEY" | jq
```

---

## 5. Query Data (Dynamic API)

### List All Rows

```bash
curl -X GET $API_URL/data/$DATASET_SLUG/ \
  -H "Authorization: Api-Key $API_KEY" | jq
```

### Pagination

```bash
curl -X GET "$API_URL/data/$DATASET_SLUG/?page=1&page_size=5" \
  -H "Authorization: Api-Key $API_KEY" | jq
```

### Filtering

```bash
# Filter by category
curl -X GET "$API_URL/data/$DATASET_SLUG/?category=Electronics" \
  -H "Authorization: Api-Key $API_KEY" | jq

# Filter by multiple fields
curl -X GET "$API_URL/data/$DATASET_SLUG/?category=Electronics&in_stock=true" \
  -H "Authorization: Api-Key $API_KEY" | jq
```

### Sorting

```bash
# Sort by price (ascending)
curl -X GET "$API_URL/data/$DATASET_SLUG/?ordering=price" \
  -H "Authorization: Api-Key $API_KEY" | jq

# Sort by price (descending)
curl -X GET "$API_URL/data/$DATASET_SLUG/?ordering=-price" \
  -H "Authorization: Api-Key $API_KEY" | jq
```

### Get Single Row

```bash
curl -X GET $API_URL/data/$DATASET_SLUG/1/ \
  -H "Authorization: Api-Key $API_KEY" | jq
```

---

## 6. Create Row

```bash
curl -X POST $API_URL/data/$DATASET_SLUG/ \
  -H "Authorization: Api-Key $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-02-16",
    "product": "Tablet",
    "category": "Electronics",
    "price": 599.99,
    "quantity": 3,
    "total": 1799.97,
    "in_stock": true
  }' | jq
```

---

## 7. Update Row (Full)

```bash
curl -X PUT $API_URL/data/$DATASET_SLUG/1/ \
  -H "Authorization: Api-Key $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-02-16",
    "product": "Laptop Pro",
    "category": "Electronics",
    "price": 1299.99,
    "quantity": 5,
    "total": 6499.95,
    "in_stock": true
  }' | jq
```

---

## 8. Update Row (Partial)

```bash
curl -X PATCH $API_URL/data/$DATASET_SLUG/1/ \
  -H "Authorization: Api-Key $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 899.99
  }' | jq
```

---

## 9. Delete Row

```bash
curl -X DELETE $API_URL/data/$DATASET_SLUG/1/ \
  -H "Authorization: Api-Key $API_KEY"
```

**Expected:** HTTP 204 No Content

---

## 10. Delete Dataset

```bash
curl -X DELETE $API_URL/datasets/$DATASET_SLUG/ \
  -H "Authorization: Api-Key $API_KEY"
```

**Expected:** HTTP 204 No Content

---

## 11. OpenAPI Documentation

### Get OpenAPI Schema

```bash
curl -X GET http://localhost:8000/api/schema/ | jq
```

### Access Swagger UI

Open in browser:
```
http://localhost:8000/api/docs/
```

### Access ReDoc

Open in browser:
```
http://localhost:8000/api/redoc/
```

---

## Error Handling Tests

### Test Authentication Failure

```bash
curl -X GET $API_URL/datasets/ \
  -H "Authorization: Api-Key invalid-key"
```

**Expected:**

```json
{
  "error": true,
  "message": "Invalid API key"
}
```

### Test Rate Limiting

```bash
# Make rapid requests to trigger rate limit
for i in {1..15}; do
  curl -X POST $API_URL/datasets/ \
    -H "Authorization: Api-Key $API_KEY" \
    -F "file=@sample_data.csv" \
    -F "name=Test $i"
  sleep 1
done
```

**Expected:** After 10 requests, you'll get HTTP 429 Too Many Requests

### Test File Size Limit

```bash
# Create large file (>10MB)
dd if=/dev/zero of=large.csv bs=1M count=11

curl -X POST $API_URL/datasets/ \
  -H "Authorization: Api-Key $API_KEY" \
  -F "file=@large.csv" \
  -F "name=Too Large"
```

**Expected:**

```json
{
  "error": true,
  "message": "File too large. Maximum size is 10MB."
}
```

### Test Invalid File Type

```bash
echo "Not a CSV" > invalid.txt

curl -X POST $API_URL/datasets/ \
  -H "Authorization: Api-Key $API_KEY" \
  -F "file=@invalid.txt" \
  -F "name=Invalid File"
```

**Expected:**

```json
{
  "error": true,
  "message": "Unsupported file type..."
}
```

---

## Load Testing

### Using Apache Bench

```bash
# Install ab
sudo apt install apache2-utils  # Ubuntu/Debian
brew install httpd              # macOS

# Test read performance
ab -n 1000 -c 10 \
  -H "Authorization: Api-Key $API_KEY" \
  http://localhost:8000/api/v1/data/$DATASET_SLUG/
```

### Using Locust

```python
# locustfile.py
from locust import HttpUser, task, between

class FileToAPIUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        self.api_key = "fta_..."  # Your API key
        self.dataset_slug = "sales-data"
    
    @task(3)
    def list_rows(self):
        self.client.get(
            f"/api/v1/data/{self.dataset_slug}/",
            headers={"Authorization": f"Api-Key {self.api_key}"}
        )
    
    @task(1)
    def get_row(self):
        self.client.get(
            f"/api/v1/data/{self.dataset_slug}/1/",
            headers={"Authorization": f"Api-Key {self.api_key}"}
        )
```

```bash
pip install locust
locust -f locustfile.py
# Visit http://localhost:8089
```

---

## Python SDK Example

```python
import requests

class FileToAPIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {"Authorization": f"Api-Key {api_key}"}
    
    def upload_file(self, file_path, name=None):
        """Upload a CSV/Excel file."""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'name': name or file_path}
            response = requests.post(
                f"{self.base_url}/datasets/",
                headers=self.headers,
                files=files,
                data=data
            )
        return response.json()
    
    def list_rows(self, dataset_slug, page=1, page_size=25, **filters):
        """Query dataset rows."""
        params = {'page': page, 'page_size': page_size, **filters}
        response = requests.get(
            f"{self.base_url}/data/{dataset_slug}/",
            headers=self.headers,
            params=params
        )
        return response.json()
    
    def create_row(self, dataset_slug, data):
        """Create a new row."""
        response = requests.post(
            f"{self.base_url}/data/{dataset_slug}/",
            headers=self.headers,
            json=data
        )
        return response.json()

# Usage
client = FileToAPIClient(
    "http://localhost:8000/api/v1",
    "fta_ab12cd34_xK9mN..."
)

# Upload
dataset = client.upload_file('sales.csv', name='Sales Data')
print(f"Dataset created: {dataset['slug']}")

# Query
rows = client.list_rows('sales-data', category='Electronics')
print(f"Found {len(rows['results'])} rows")

# Create
new_row = client.create_row('sales-data', {
    'date': '2026-02-16',
    'product': 'Mouse',
    'price': 29.99
})
print(f"Created row ID: {new_row['id']}")
```

---

## Monitoring Requests

### Enable Django Debug Toolbar (Development)

```bash
pip install django-debug-toolbar
```

Add to settings:

```python
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']
```

### Log All Requests

Add to `config/settings.py`:

```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

---

## Troubleshooting

### Check Server Logs

```bash
# Development server logs to console
python manage.py runserver

# Production logs
sudo journalctl -u filetoapi -f
```

### Verify Database

```bash
# Open SQLite database
sqlite3 db.sqlite3

# List tables
.tables

# Check dataset
SELECT * FROM core_dataset;

# Check dynamic table
SELECT * FROM dataset_a1b2c3d4;
```

### Reset Everything

```bash
rm db.sqlite3
rm -rf media/uploads/*
python manage.py migrate
```

---

**Happy Testing!** 🚀
