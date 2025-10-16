# CALIDUS Frontend

Modern Next.js frontend for the CALIDUS Requirements Management & Traceability platform.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Deployment**: Vercel

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
```

## Pages

- **Home** (`/`) - Landing page with features and API status
- **Login** (`/login`) - User authentication with demo accounts
- **Demo** (`/demo`) - Interactive feature preview
- **Dashboard** (`/dashboard`) - Main application interface (requires auth)

## Demo Accounts

| Username | Password | Role |
|----------|----------|------|
| admin | demo2024 | Admin |
| engineer | engineer2024 | Engineer |
| viewer | viewer2024 | Viewer |

## Deployment to Vercel

### Method 1: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel
```

### Method 2: GitHub Integration

1. Push code to GitHub
2. Import repository in Vercel dashboard
3. Configure environment variables:
   - `NEXT_PUBLIC_API_URL` = your backend API URL
4. Deploy

### Method 3: Deploy Button

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/zozisteam/cls-requirement_management/tree/main/frontend)

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, update to your production backend URL.

## Project Structure

```
frontend/
├── app/
│   ├── demo/
│   │   └── page.tsx          # Interactive demo page
│   ├── login/
│   │   └── page.tsx          # Login page
│   ├── globals.css           # Global styles
│   ├── layout.tsx            # Root layout
│   └── page.tsx              # Home page
├── components/               # Reusable components
├── lib/                      # Utilities and helpers
├── public/                   # Static assets
├── .env.example              # Environment template
├── next.config.js            # Next.js configuration
├── tailwind.config.ts        # Tailwind configuration
├── tsconfig.json             # TypeScript configuration
└── vercel.json               # Vercel deployment config
```

## Features

### Authentication
- JWT-based authentication
- Demo account quick-fill
- Protected routes
- Token storage in localStorage

### UI Components
- Responsive design
- Tailwind CSS styling
- Modern card-based layouts
- Interactive tabs and forms

### API Integration
- Axios for HTTP requests
- API proxy configuration
- Error handling
- Loading states

## Development Tips

### Running with Backend

Ensure the backend is running:

```bash
# In backend directory
docker compose up
```

Then start the frontend:

```bash
# In frontend directory
npm run dev
```

### API Proxy

The Next.js config includes API proxying to avoid CORS issues during development:

```javascript
// next.config.js
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: 'http://localhost:8000/api/:path*',
    },
  ]
}
```

## Building for Production

```bash
# Create optimized production build
npm run build

# Start production server locally
npm run start
```

## Troubleshooting

### API Connection Issues

1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
3. Clear browser cache and localStorage
4. Restart dev server

### Build Errors

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

## License

Proprietary - CALIDUS Project
