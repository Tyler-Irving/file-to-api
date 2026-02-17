# File-to-API Frontend

A clean, modern React frontend for the File-to-API platform. Upload CSV or Excel files and get a fully functional REST API with interactive documentation.

## Features

- 🎯 **Drag & Drop Upload** — Intuitive file upload with validation
- 📊 **Dataset Management** — List, view, and delete datasets
- 🔍 **API Explorer** — Interactive examples with copy-paste curl commands
- 🔑 **API Key Management** — Generate, list, and revoke authentication keys
- 📱 **Responsive Design** — Works beautifully on desktop and mobile
- ⚡ **Built with Modern Stack** — React 19, TypeScript, Vite, Tailwind CSS

## Tech Stack

- **Framework:** React 19 with TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **State Management:** TanStack Query (React Query)
- **HTTP Client:** Axios
- **Icons:** Lucide React
- **Routing:** React Router v6

## Prerequisites

- Node.js 18+ and npm
- Django backend running on `http://localhost:8000` (or configure `VITE_API_BASE_URL`)

## Installation

1. **Install dependencies:**

```bash
npm install
```

2. **Configure environment:**

```bash
cp .env.example .env
```

Edit `.env` to point to your Django backend:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Development

Start the development server:

```bash
npm run dev
```

The app will be available at **http://localhost:5173**

Hot module replacement (HMR) is enabled — changes will reflect instantly.

## Building for Production

Build the production bundle:

```bash
npm run build
```

This creates an optimized build in the `dist/` directory.

Preview the production build locally:

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── api/                 # API client and service functions
│   │   ├── client.ts        # Axios instance with interceptors
│   │   ├── datasets.ts      # Dataset API calls
│   │   └── keys.ts          # API key management
│   ├── components/          # React components
│   │   ├── Layout.tsx       # Main layout with header/footer
│   │   ├── DatasetList.tsx  # List all datasets
│   │   ├── DatasetDetail.tsx # Dataset detail page
│   │   ├── FileUpload.tsx   # Drag-and-drop upload
│   │   ├── SchemaTable.tsx  # Display dataset schema
│   │   ├── APIExplorer.tsx  # Interactive API examples
│   │   └── APIKeys.tsx      # API key management
│   ├── types.ts             # TypeScript interfaces
│   ├── utils/
│   │   └── cn.ts            # Tailwind class merger
│   ├── App.tsx              # Root component with routing
│   ├── main.tsx             # App entry point
│   └── index.css            # Global styles + Tailwind
├── public/                  # Static assets
├── .env.example             # Environment variables template
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # Tailwind CSS config
├── tsconfig.json            # TypeScript config
└── package.json             # Dependencies and scripts
```

## API Integration

The frontend expects the Django backend to expose these endpoints:

### Dataset Management
- `POST /api/v1/datasets/` — Upload file
- `GET /api/v1/datasets/` — List datasets
- `GET /api/v1/datasets/{slug}/` — Dataset detail
- `DELETE /api/v1/datasets/{slug}/` — Delete dataset

### API Keys
- `POST /api/v1/keys/` — Generate new key
- `GET /api/v1/keys/` — List keys
- `DELETE /api/v1/keys/{id}/` — Revoke key

### Dynamic Data (per dataset)
- `GET /api/v1/data/{slug}/` — List records
- `POST /api/v1/data/{slug}/` — Create record
- `GET /api/v1/data/{slug}/{id}/` — Get record
- `PUT /api/v1/data/{slug}/{id}/` — Update record
- `DELETE /api/v1/data/{slug}/{id}/` — Delete record

## Authentication

API keys are stored in `localStorage` and automatically added to requests via an Axios interceptor:

```typescript
Authorization: Api-Key {your_api_key}
```

Generate a key in the **API Keys** page and it will be used for all subsequent requests.

## Deployment

### Static Hosting (Netlify, Vercel, etc.)

1. Build the production bundle:
   ```bash
   npm run build
   ```

2. Deploy the `dist/` folder to your hosting provider

3. Configure environment variables:
   ```
   VITE_API_BASE_URL=https://your-backend-api.com
   ```

4. Set up redirects for client-side routing (e.g., Netlify `_redirects`):
   ```
   /*  /index.html  200
   ```

### Nginx (Self-Hosted)

Example nginx config:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/file-to-api/dist;
    index index.html;

    # Client-side routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to Django
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Customization

### Styling

Tailwind CSS is configured in `tailwind.config.js`. Extend the theme to customize colors, fonts, etc.

Global styles and custom utility classes are in `src/index.css`.

### API Base URL

The API base URL defaults to `http://localhost:8000` but can be overridden via the `VITE_API_BASE_URL` environment variable.

### File Upload Limits

Max file size (10MB) and allowed types are configured in `src/components/FileUpload.tsx`:

```typescript
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ALLOWED_TYPES = ['text/csv', 'application/vnd.ms-excel', ...];
```

## Scripts

- `npm run dev` — Start development server
- `npm run build` — Build for production
- `npm run preview` — Preview production build
- `npm run lint` — Run ESLint

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## License

MIT

---

**Built with React, TypeScript, and modern web technologies**
