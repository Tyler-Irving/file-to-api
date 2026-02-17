# File-to-API Platform - Django Backend

**Upload a CSV or Excel file. Get an instant REST API.**

This Django backend converts uploaded spreadsheet files into fully functional REST APIs with CRUD operations, automatic schema detection, pagination, filtering, and OpenAPI documentation.

---

## 🚀 Features

- **Zero-config schema detection** - Automatic type inference from file data
- **Dynamic API generation** - Instant REST endpoints for each dataset
- **Full CRUD operations** - Create, Read, Update, Delete on all uploaded data
- **API key authentication** - Secure access control
- **OpenAPI/Swagger docs** - Auto-generated interactive API documentation
- **Rate limiting** - Configurable request limits per endpoint
- **SQLite backend** - No database server required (PostgreSQL-ready)
- **Filtering & pagination** - Query parameters for data exploration

---

## 📋 Requirements

- Python 3.10+
- pip & virtualenv

---

## 🛠️ Local Development Setup

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd file-to-api/backend
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set:

```bash
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
API_KEY_SALT=your-random-salt-here
```

**Generate secure values:**

```bash
# SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# API_KEY_SALT
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

The API will be available at:
- **Base API:** http://localhost:8000/api/v1/
- **Swagger Docs:** http://localhost:8000/api/docs/
- **Django Admin:** http://localhost:8000/admin/

---

## 📡 API Usage

### Step 1: Generate API Key

```bash
curl -X POST http://localhost:8000/api/v1/keys/ \
  -H "Content-Type: application/json" \
  -d '{"name": "My First Key"}'
```

**Response:**

```json
{
  "id": "a1b2c3d4-...",
  "name": "My First Key",
  "prefix": "ab12cd34",
  "key": "fta_ab12cd34_xK9mN...",
  "created_at": "2026-02-16T23:00:00Z",
  "warning": "Save this key securely. It will not be shown again."
}
```

⚠️ **Save the full `key` value** - you'll need it for all subsequent requests.

### Step 2: Upload a File

```bash
curl -X POST http://localhost:8000/api/v1/datasets/ \
  -H "Authorization: Api-Key fta_ab12cd34_xK9mN..." \
  -F "file=@sales_data.csv" \
  -F "name=Sales Data"
```

**Response:**

```json
{
  "id": "...",
  "slug": "sales-data",
  "name": "Sales Data",
  "status": "ready",
  "row_count": 1523,
  "columns": [
    {"name": "Date", "field_name": "date", "data_type": "date"},
    {"name": "Amount", "field_name": "amount", "data_type": "float"},
    {"name": "Category", "field_name": "category", "data_type": "text"}
  ],
  "api_url": "/api/v1/data/sales-data/",
  "docs_url": "/api/docs/#/data/sales-data"
}
```

### Step 3: Query Your Data

```bash
# List all rows (paginated)
curl http://localhost:8000/api/v1/data/sales-data/ \
  -H "Authorization: Api-Key fta_ab12cd34_xK9mN..."

# Filter
curl "http://localhost:8000/api/v1/data/sales-data/?category=Electronics" \
  -H "Authorization: Api-Key fta_ab12cd34_xK9mN..."

# Sort
curl "http://localhost:8000/api/v1/data/sales-data/?ordering=-amount" \
  -H "Authorization: Api-Key fta_ab12cd34_xK9mN..."

# Get single row
curl http://localhost:8000/api/v1/data/sales-data/1/ \
  -H "Authorization: Api-Key fta_ab12cd34_xK9mN..."
```

### Step 4: Create/Update/Delete

```bash
# Create row
curl -X POST http://localhost:8000/api/v1/data/sales-data/ \
  -H "Authorization: Api-Key fta_ab12cd34_xK9mN..." \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-02-16", "amount": 99.99, "category": "Books"}'

# Update row
curl -X PUT http://localhost:8000/api/v1/data/sales-data/1/ \
  -H "Authorization: Api-Key fta_ab12cd34_xK9mN..." \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-02-16", "amount": 149.99, "category": "Books"}'

# Delete row
curl -X DELETE http://localhost:8000/api/v1/data/sales-data/1/ \
  -H "Authorization: Api-Key fta_ab12cd34_xK9mN..."
```

---

## 🌐 Production Deployment

### Option 1: Single Server (VPS/EC2)

#### 1. Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx

# Optional: Install PostgreSQL instead of SQLite
sudo apt install postgresql postgresql-contrib
```

#### 2. Clone & Setup

```bash
cd /var/www
sudo git clone <your-repo> file-to-api
cd file-to-api/backend
sudo chown -R $USER:$USER .

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Configure Production Settings

```bash
cp .env.example .env
nano .env
```

**Production `.env`:**

```bash
SECRET_KEY=<generate-new-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
API_KEY_SALT=<generate-new-salt>

# Optional: PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost:5432/filetoapi
```

#### 4. Collect Static Files & Migrate

```bash
python manage.py collectstatic --noinput
python manage.py migrate
```

#### 5. Setup Gunicorn Service

Create `/etc/systemd/system/filetoapi.service`:

```ini
[Unit]
Description=File-to-API Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/file-to-api/backend
Environment="PATH=/var/www/file-to-api/backend/venv/bin"
ExecStart=/var/www/file-to-api/backend/venv/bin/gunicorn \
          --workers 4 \
          --bind unix:/var/www/file-to-api/backend/gunicorn.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable & start:

```bash
sudo systemctl enable filetoapi
sudo systemctl start filetoapi
sudo systemctl status filetoapi
```

#### 6. Configure Nginx

Create `/etc/nginx/sites-available/filetoapi`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    client_max_body_size 10M;

    location /static/ {
        alias /var/www/file-to-api/backend/staticfiles/;
    }

    location /media/ {
        alias /var/www/file-to-api/backend/media/;
    }

    location / {
        proxy_pass http://unix:/var/www/file-to-api/backend/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/filetoapi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 7. Setup SSL (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

### Option 2: Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations and start Gunicorn
CMD python manage.py migrate && \
    gunicorn --bind 0.0.0.0:8000 --workers 4 config.wsgi:application
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=False
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
    volumes:
      - ./media:/app/media
      - ./db.sqlite3:/app/db.sqlite3
    restart: unless-stopped
```

Run:

```bash
docker-compose up -d
```

---

### Option 3: Railway / Render / Heroku

All three platforms support Django apps out of the box:

1. **Connect GitHub repo**
2. **Add environment variables** (SECRET_KEY, ALLOWED_HOSTS, etc.)
3. **Set build command:** `pip install -r requirements.txt`
4. **Set start command:** `gunicorn config.wsgi:application`

Platforms will auto-detect Django and handle deployment.

---

## 🧪 Testing

```bash
# Run tests (when implemented)
python manage.py test

# Check code coverage
coverage run --source='.' manage.py test
coverage report
```

---

## 🔒 Security Best Practices

1. **Never commit `.env` files** - Use environment variables
2. **Rotate API keys regularly** - Especially if compromised
3. **Use HTTPS in production** - Let's Encrypt is free
4. **Set `DEBUG=False`** - Prevents information leakage
5. **Update dependencies** - Run `pip list --outdated` periodically
6. **File upload validation** - Already implemented (MIME type, size, malicious content)
7. **Rate limiting** - Already implemented per endpoint

---

## 📂 Project Structure

```
backend/
├── config/                 # Django settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                   # Dataset management
│   ├── models.py           # Dataset, DatasetColumn
│   ├── views.py            # Upload, list, delete
│   ├── serializers.py
│   └── urls.py
├── engine/                 # Processing & API generation
│   ├── parser.py           # CSV/Excel parsing
│   ├── schema.py           # Type inference
│   ├── table_builder.py    # Dynamic SQLite tables
│   ├── api_generator.py    # Dynamic ViewSets
│   ├── router.py           # URL registration
│   ├── processor.py        # Orchestration
│   └── loader.py           # Startup loader
├── auth_keys/              # API key auth
│   ├── models.py           # APIKey
│   ├── authentication.py   # DRF backend
│   ├── views.py
│   └── middleware.py       # Rate limiting
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🐛 Known Limitations

- **SQLite concurrency** - Use PostgreSQL for high-traffic production
- **No schema migrations** - Re-uploading files with different schemas requires manual handling
- **No relationships** - Each dataset is independent
- **Server restart for unregister** - DRF's router doesn't support dynamic unregistration

---

## 🔮 Future Enhancements

- [ ] Asynchronous processing (Celery)
- [ ] PostgreSQL support
- [ ] File format auto-conversion (JSON, XML → CSV)
- [ ] Schema drift detection on re-upload
- [ ] Webhooks for data changes
- [ ] GraphQL API option
- [ ] Multi-tenant SaaS features
- [ ] Real-time subscriptions (WebSockets)

---

## 📞 Support

For issues or questions:
- **GitHub Issues:** [your-repo]/issues
- **Documentation:** [your-docs-url]

---

**Built with Django 4.2 + Django REST Framework**
