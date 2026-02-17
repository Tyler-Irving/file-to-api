# Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Make sure your Django backend is running on `http://localhost:8000`

### 3. Start Development Server

```bash
npm run dev
```

Open http://localhost:5173 in your browser 🎉

## First Steps

1. **Generate an API Key** — Go to `/keys` and create your first API key
2. **Upload a Dataset** — Go to `/upload` and drag & drop a CSV or Excel file
3. **Explore Your API** — View the generated API endpoints and try them out!

## Common Commands

- `npm run dev` — Start dev server (hot reload enabled)
- `npm run build` — Build for production
- `npm run preview` — Preview production build locally

## Troubleshooting

**Backend not connecting?**
- Check that Django is running on port 8000
- Verify `VITE_API_BASE_URL` in `.env` is correct
- Check browser console for CORS errors

**Upload not working?**
- Ensure you have a valid API key
- Check file size (max 10MB)
- Only CSV and Excel files are supported

**TypeScript errors?**
- Run `npm install` to ensure all dependencies are installed
- Restart your IDE/editor

## Need Help?

See the full [README.md](./README.md) for detailed documentation.

---

Built with React 19, TypeScript, Vite, and Tailwind CSS
