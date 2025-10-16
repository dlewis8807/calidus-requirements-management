# Vercel Deployment Guide

Complete guide for deploying the CALIDUS frontend to Vercel.

## Prerequisites

- GitHub account
- Vercel account (free tier available at [vercel.com](https://vercel.com))
- Backend API deployed and accessible via public URL
- Git repository with frontend code

## Deployment Methods

### Method 1: GitHub Integration (Recommended)

This method enables automatic deployments on every push to main branch.

#### Step 1: Push Code to GitHub

```bash
# Add all frontend files
git add frontend/

# Commit
git commit -m "feat: Add Next.js frontend for Vercel deployment"

# Push to GitHub
git push origin main
```

#### Step 2: Import to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New Project"**
3. Click **"Import Git Repository"**
4. Select your repository: `zozisteam/cls-requirement_management`
5. Configure project:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)
   - **Install Command**: `npm install` (default)

#### Step 3: Configure Environment Variables

Add the following environment variable in Vercel:

| Name | Value | Description |
|------|-------|-------------|
| `NEXT_PUBLIC_API_URL` | `https://your-backend-api.com` | Your production backend API URL |

**Important**: Replace `https://your-backend-api.com` with your actual backend API URL.

#### Step 4: Deploy

1. Click **"Deploy"**
2. Wait 2-3 minutes for build to complete
3. Vercel will provide a deployment URL (e.g., `https://calidus.vercel.app`)

#### Step 5: Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain (e.g., `demo.calidus.com`)
3. Follow Vercel's DNS configuration instructions

### Method 2: Vercel CLI

For quick deployments from command line.

#### Installation

```bash
# Install Vercel CLI globally
npm install -g vercel

# Login to Vercel
vercel login
```

#### Deploy

```bash
# Navigate to frontend directory
cd frontend

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

#### Set Environment Variables

```bash
# Add environment variable
vercel env add NEXT_PUBLIC_API_URL production

# When prompted, enter your backend API URL
# Example: https://api.calidus.com
```

### Method 3: Deploy Button

Add a deploy button to your README.md:

```markdown
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/zozisteam/cls-requirement_management/tree/main/frontend&env=NEXT_PUBLIC_API_URL&envDescription=Backend%20API%20URL&envLink=https://github.com/zozisteam/cls-requirement_management)
```

## Configuration Files

### vercel.json

Located at `/frontend/vercel.json`:

```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-backend-api.com/api/:path*"
    }
  ],
  "env": {
    "NEXT_PUBLIC_API_URL": "https://your-backend-api.com"
  }
}
```

**Update the `destination` and `NEXT_PUBLIC_API_URL` with your production backend URL.**

### Environment Variables

**Development** (`.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Production** (Vercel Dashboard):
```env
NEXT_PUBLIC_API_URL=https://api.calidus.com
```

## Backend API Requirements

Your backend API must be:

1. **Publicly accessible** - Not running on localhost
2. **CORS enabled** - Allow requests from your Vercel domain
3. **HTTPS enabled** - Vercel requires HTTPS for production

### CORS Configuration

Update your backend `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",           # Local development
        "https://calidus.vercel.app",      # Your Vercel domain
        "https://demo.calidus.com",        # Custom domain (if any)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Deployment Options for Backend

### Option 1: Railway.app
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy backend
cd backend
railway up
```

### Option 2: Render.com
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect GitHub repository
4. Select `backend` directory
5. Use Docker deployment method

### Option 3: Fly.io
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy
cd backend
fly launch
```

### Option 4: AWS/DigitalOcean/Linode
Deploy using Docker Compose on a VPS:
```bash
# SSH to server
ssh user@your-server

# Clone repository
git clone https://github.com/zozisteam/cls-requirement_management.git
cd cls-requirement_management

# Start services
docker compose up -d
```

## Testing Deployment

### 1. Check Build Logs

In Vercel dashboard:
- Go to **Deployments**
- Click on latest deployment
- View **Build Logs** for any errors

### 2. Test API Connection

Once deployed, test API connectivity:

```bash
# Check frontend loads
curl https://calidus.vercel.app

# Check API proxy works
curl https://calidus.vercel.app/api/health
```

### 3. Manual Testing

1. Visit your Vercel URL
2. Check homepage loads with API status
3. Test login page:
   - Click demo account buttons
   - Try logging in with: `admin` / `demo2024`
4. Test demo page interactive features
5. Verify all links and navigation work

## Troubleshooting

### Build Fails

**Error**: `Module not found`
```bash
# Solution: Clear cache and rebuild
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

**Error**: `TypeScript errors`
```bash
# Solution: Fix TypeScript errors locally first
npm run build
# Fix all reported errors
# Then push to GitHub
```

### API Connection Issues

**Symptom**: Frontend loads but can't connect to backend

**Checklist**:
1. ✅ Verify `NEXT_PUBLIC_API_URL` is set correctly in Vercel
2. ✅ Check backend is running and publicly accessible
3. ✅ Verify CORS is configured to allow Vercel domain
4. ✅ Check browser console for CORS errors
5. ✅ Test backend directly: `curl https://api.calidus.com/health`

### Environment Variables Not Working

**Issue**: Changes to environment variables not reflected

**Solution**: Redeploy after changing environment variables
1. Go to Vercel Dashboard
2. Settings → Environment Variables
3. Add/update variables
4. Deployments → Latest → Redeploy

### 404 on Page Refresh

**Issue**: Page works initially but 404 on refresh

**Solution**: This shouldn't happen with Next.js App Router, but if it does:
1. Check `vercel.json` is in frontend directory
2. Ensure `framework: "nextjs"` is specified
3. Verify no custom routing conflicts

## Performance Optimization

### 1. Enable Caching

Vercel automatically caches static assets. For API caching:

```javascript
// In API fetch calls, add cache headers
const response = await fetch('/api/data', {
  next: { revalidate: 60 } // Cache for 60 seconds
});
```

### 2. Image Optimization

Use Next.js Image component:

```jsx
import Image from 'next/image';

<Image
  src="/logo.png"
  alt="CALIDUS"
  width={100}
  height={100}
/>
```

### 3. Bundle Size

Check bundle size after build:

```bash
npm run build
# Review bundle analysis in output
```

## Continuous Deployment

Vercel automatically deploys when you push to GitHub:

```bash
# Make changes to frontend
git add frontend/
git commit -m "feat: Update dashboard UI"
git push origin main

# Vercel auto-deploys in ~2-3 minutes
# Check deployment status at vercel.com
```

### Preview Deployments

Every branch and PR gets a preview deployment:

```bash
# Create feature branch
git checkout -b feature/new-dashboard

# Make changes and push
git push origin feature/new-dashboard

# Vercel creates preview URL: https://calidus-abc123.vercel.app
```

## Security Best Practices

1. **Environment Variables**: Never commit `.env.local` to Git
2. **API Keys**: Store sensitive keys only in Vercel dashboard
3. **HTTPS**: Always use HTTPS in production
4. **CORS**: Restrict CORS to specific domains
5. **Rate Limiting**: Implement rate limiting on backend API

## Monitoring

### Vercel Analytics

Enable Vercel Analytics for free:
1. Go to Project Settings → Analytics
2. Enable Web Analytics
3. View metrics in Vercel dashboard

### Custom Monitoring

Add error tracking:

```bash
# Install Sentry
npm install @sentry/nextjs

# Follow Sentry Next.js setup guide
```

## Cost Estimation

**Vercel Free Tier** includes:
- Unlimited deployments
- 100GB bandwidth/month
- Automatic HTTPS
- Preview deployments
- Analytics

**Vercel Pro** ($20/month):
- 1TB bandwidth/month
- Advanced analytics
- Custom domains
- Team collaboration

## Checklist

Before deploying to production:

- [ ] Backend API is publicly accessible
- [ ] CORS configured with Vercel domain
- [ ] Environment variables set in Vercel
- [ ] `vercel.json` updated with production API URL
- [ ] All tests pass locally
- [ ] Build succeeds: `npm run build`
- [ ] Demo accounts work in production
- [ ] Custom domain configured (optional)
- [ ] Analytics enabled
- [ ] Error tracking configured

## Support

- **Vercel Docs**: https://vercel.com/docs
- **Next.js Docs**: https://nextjs.org/docs
- **CALIDUS Issues**: https://github.com/zozisteam/cls-requirement_management/issues

## Quick Reference

```bash
# Local development
cd frontend
npm run dev          # Start dev server (http://localhost:3000)
npm run build        # Build for production
npm run start        # Start production server

# Vercel CLI
vercel               # Deploy to preview
vercel --prod        # Deploy to production
vercel logs          # View deployment logs
vercel env ls        # List environment variables
```

---

Generated: 2025-10-16
Project: CALIDUS Requirements Management & Traceability
