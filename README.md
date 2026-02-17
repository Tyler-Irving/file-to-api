# File-to-API Platform

**Turn any CSV or Excel file into a production-ready REST API in minutes, not days.**

File-to-API is an automation-first platform that eliminates the tedious work of building data APIs. Upload a spreadsheet, get a fully-functional REST API with authentication, pagination, filtering, and interactive documentation — automatically.

Perfect for data teams, automation engineers, and rapid prototyping where you need to expose data via API without writing boilerplate code.

---

## 🎯 Why File-to-API?

**The Problem:** Building a REST API for simple data access requires days of work — database setup, schema design, CRUD endpoints, authentication, documentation, deployment. Most of this is repetitive boilerplate.

**The Solution:** File-to-API automates the entire pipeline. Upload your data file, and within seconds you have:
- A fully functional REST API with CRUD operations
- Automatic schema detection (no configuration required)
- API key authentication and rate limiting
- Interactive Swagger/OpenAPI documentation
- Production-ready architecture

**Time Savings:** What takes 2-3 days of development becomes a 2-minute upload.

---

## ✨ Features

### Core Automation
- **Zero-config schema detection** — Automatically infers data types (text, numbers, dates, booleans) from your file
- **Dynamic API generation** — REST endpoints created at runtime, no code generation or compilation needed
- **Instant deployment** — Upload a file, get a working API URL immediately

### API Features
- **Full CRUD operations** — Create, Read, Update, Delete with standard REST conventions
- **Pagination** — Configurable page sizes for large datasets
- **Filtering & sorting** — Query parameters for flexible data exploration
- **OpenAPI documentation** — Auto-generated Swagger UI with interactive examples
- **Rate limiting** — Configurable per-endpoint throttling

### Security & Performance
- **API key authentication** — Secure access control with revocable keys
- **File validation** — MIME type checking, size limits, malicious content detection
- **SQLite backend** — No database server required (PostgreSQL-ready for production)
- **Optimized queries** — Efficient indexing and pagination

### Developer Experience
- **Modern React UI** — Beautiful drag-and-drop interface with real-time feedback
- **Copy-paste examples** — Every API endpoint includes ready-to-use curl commands
- **TypeScript support** — Full type safety in frontend codebase
- **Comprehensive docs** — Clear setup guides for local development and production deployment

---

## 🚀 Quick Start

Get running in under 5 minutes:

### Prerequisites
- Python 3.10+
- Node.js 18+
- pip, npm

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/file-to-api.git
cd file-to-api
```

### 2. Start Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(f'SECRET_KEY={get_random_secret_key()}')" >> .env
python -c "import secrets; print(f'API_KEY_SALT={secrets.token_urlsafe(32)}')" >> .env

# Initialize database
python manage.py migrate

# Start server
python manage.py runserver
```

Backend now running at **http://localhost:8000**

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend now running at **http://localhost:5173**

### 4. Try It Out

1. Open http://localhost:5173 in your browser
2. Generate an API key in the **API Keys** tab
3. Upload the sample CSV file (`backend/sample_data.csv`)
4. View your new API in the **Datasets** tab
5. Copy the curl examples and test your API!

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend (Vite)                    │
│  • File Upload UI • Dataset Explorer • API Key Manager      │
└───────────────────────┬─────────────────────────────────────┘
                        │ REST API (axios)
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    Django REST Framework                     │
│  ┌──────────────┐  ┌─────────────┐  ┌───────────────────┐  │
│  │ Core Module  │  │   Engine    │  │  Auth Keys Module │  │
│  │              │  │             │  │                   │  │
│  │ • Dataset    │→ │ • Parser    │  │ • API Key Model   │  │
│  │   Management │  │ • Schema    │  │ • Authentication  │  │
│  │ • File Upload│  │   Inference │  │ • Rate Limiting   │  │
│  │              │  │ • Dynamic   │  │                   │  │
│  │              │  │   Table Gen │  │                   │  │
│  │              │  │ • API       │  │                   │  │
│  │              │  │   Generation│  │                   │  │
│  └──────────────┘  └─────────────┘  └───────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │  SQLite Database │
              │                  │
              │  • Dataset meta  │
              │  • API keys      │
              │  • Dynamic tables│
              └─────────────────┘
```

### How It Works

1. **File Upload:** User uploads CSV/Excel via React frontend
2. **Parsing:** Django backend reads file using pandas
3. **Schema Detection:** Engine analyzes data and infers types
4. **Table Creation:** SQLite table generated dynamically
5. **API Registration:** DRF ViewSet and URLs registered at runtime
6. **Ready to Use:** API endpoints immediately available

### Key Technical Highlights

- **Dynamic Model Generation:** Creates Django models at runtime using `type()` constructor
- **Runtime ViewSet Registration:** DRF router dynamically updated without server restart
- **Schema Inference:** Statistical analysis of sample data to determine types
- **Secure File Processing:** Validation, sanitization, and isolated execution

---

## 📖 Usage Examples

### Upload a Dataset

```bash
# 1. Generate API key
curl -X POST http://localhost:8000/api/v1/keys/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Production Key"}'

# Response includes your API key (save it!)
# Example: fta_ab12cd34_xK9mN...

# 2. Upload CSV file
curl -X POST http://localhost:8000/api/v1/datasets/ \
  -H "Authorization: Api-Key fta_ab12cd34_xK9mN..." \
  -F "file=@sales_data.csv" \
  -F "name=Sales Data"
```

### Query Your Data

```bash
# List all records (paginated)
curl http://localhost:8000/api/v1/data/sales-data/ \
  -H "Authorization: Api-Key fta_ab12cd34_xK9mN..."

# Filter by field
curl "http://localhost:8000/api/v1/data/sales-data/?category=Electronics" \
  -H "Authorization: Api-Key fta_ab12cd34_xK9mN..."

# Sort descending by price
curl "http://localhost:8000/api/v1/data/sales-data/?ordering=-price" \
  -H "Authorization: Api-Key fta_ab12cd34_xK9mN..."

# Get single record
curl http://localhost:8000/api/v1/data/sales-data/1/ \
  -H "Authorization: Api-Key fta_ab12cd34_xK9mN..."
```

### Create, Update, Delete

```bash
# Create new record
curl -X POST http://localhost:8000/api/v1/data/sales-data/ \
  -H "Authorization: Api-Key fta_ab12cd34_xK9mN..." \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-02-16", "product": "Tablet", "price": 599.99, "quantity": 3}'

# Update existing record
curl -X PUT http://localhost:8000/api/v1/data/sales-data/1/ \
  -H "Authorization: Api-Key fta_ab12cd34_xK9mN..." \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-02-16", "product": "Tablet Pro", "price": 699.99, "quantity": 3}'

# Delete record
curl -X DELETE http://localhost:8000/api/v1/data/sales-data/1/ \
  -H "Authorization: Api-Key fta_ab12cd34_xK9mN..."
```

### Interactive Documentation

Open **http://localhost:8000/api/docs/** in your browser for:
- All available endpoints
- Request/response schemas
- Try-it-out functionality
- Authentication setup

---

## 🛠️ Tech Stack

### Backend
- **Framework:** Django 4.2
- **API:** Django REST Framework 3.14
- **Database:** SQLite (development), PostgreSQL-ready
- **Data Processing:** pandas, openpyxl
- **Authentication:** Custom API key implementation
- **Documentation:** drf-spectacular (OpenAPI 3.0)

### Frontend
- **Framework:** React 19 with TypeScript
- **Build Tool:** Vite 6
- **Styling:** Tailwind CSS 4
- **State Management:** TanStack Query (React Query)
- **HTTP Client:** Axios
- **Routing:** React Router v6
- **Icons:** Lucide React

---

## 🌐 Deployment

### Production Deployment Options

See detailed guides in `backend/README.md`:

1. **Traditional Server (VPS/EC2)**
   - Nginx + Gunicorn setup
   - PostgreSQL database
   - Let's Encrypt SSL
   - Systemd service management

2. **Docker / Docker Compose**
   - Containerized deployment
   - Easy scaling and portability

3. **Platform-as-a-Service**
   - Railway, Render, Heroku
   - One-click deployment
   - Auto-scaling

### Security Checklist for Production

- [ ] Set `DEBUG=False` in Django settings
- [ ] Use strong `SECRET_KEY` and `API_KEY_SALT`
- [ ] Configure `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`
- [ ] Enable HTTPS (SSL certificate)
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up proper file upload limits
- [ ] Configure rate limiting appropriately
- [ ] Regular dependency updates
- [ ] Monitor logs and set up error tracking

---

## 📚 Documentation

- **Backend:** See `backend/README.md` for detailed API docs, deployment guides, and architecture
- **Frontend:** See `frontend/README.md` for React app structure and customization
- **API Testing:** `backend/API_TESTING.md` for endpoint testing examples
- **Architecture:** `backend/ARCHITECTURE.md` for deep technical dive

---

## 🎯 Use Cases

### 1. Data Team Collaboration
Share datasets with analysts and engineers via API without database access. Update data by uploading new files — API schema adapts automatically.

### 2. Rapid Prototyping
Build proof-of-concept applications that need data access. Spend time on business logic, not API boilerplate.

### 3. Automation & Integration
Connect spreadsheet data to automation tools (n8n, Zapier, Make) or custom scripts. No-code users can publish data APIs.

### 4. Legacy System Modernization
Expose data from legacy systems via CSV exports. Transform batch processes into real-time APIs.

### 5. Internal Tools
Quickly spin up internal dashboards, admin panels, or reporting tools backed by file-based data.

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/amazing-feature`
3. **Make your changes** and test thoroughly
4. **Commit with clear messages:** `git commit -m 'Add amazing feature'`
5. **Push to your fork:** `git push origin feature/amazing-feature`
6. **Open a Pull Request** with a description of your changes

### Development Guidelines
- Follow existing code style (PEP 8 for Python, ESLint config for TypeScript)
- Add tests for new features
- Update documentation as needed
- Keep commits focused and atomic

---

## 📝 License

MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## 🐛 Known Limitations

- **SQLite concurrency:** Not suitable for high-traffic production (use PostgreSQL)
- **No schema migrations:** Re-uploading files with different schemas requires manual cleanup
- **No relationships:** Each dataset is independent (no foreign keys)
- **Single-file datasets:** No support for related tables or joins

---

## 🔮 Roadmap

- [ ] Asynchronous file processing (Celery)
- [ ] PostgreSQL support with migrations
- [ ] Schema drift detection on re-upload
- [ ] Multi-file datasets with relationships
- [ ] Webhooks for data change notifications
- [ ] GraphQL API option
- [ ] Real-time subscriptions via WebSockets
- [ ] Multi-tenant SaaS features
- [ ] Scheduled data refreshes
- [ ] Data transformation pipelines

---

## 💡 About

Built as a portfolio project to demonstrate:
- Full-stack development (Django + React)
- Dynamic API generation techniques
- Modern web development practices
- Production-ready architecture
- Developer-focused documentation

**Automation focus:** This project embodies the principle that repetitive development tasks should be automated, freeing developers to focus on unique business logic.

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/file-to-api/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/file-to-api/discussions)

---

**⭐ Star this repo if you find it useful!**

Built with Django, React, and a passion for automation.
