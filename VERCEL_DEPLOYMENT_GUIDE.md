# CALIDUS - Vercel Deployment Guide

## 🚀 Quick Deploy to Vercel

### Prerequisites
- GitHub/GitLab/Bitbucket account (for connecting repository)
- Vercel account (free tier works fine)
- Backend API deployed and accessible (or use mock mode)

---

## Option 1: Deploy via Vercel Dashboard (Recommended)

### Step 1: Push Code to Git Repository

```bash
# From the frontend directory
cd /Users/bitgallery/calidus_dre/cls-requirement_management/frontend

# Initialize git if not already done
git init
git add .
git commit -m "Initial commit for Vercel deployment"

# Add remote (replace with your repository URL)
git remote add origin https://github.com/YOUR_USERNAME/calidus-frontend.git
git push -u origin main
```

### Step 2: Import Project to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "Add New..." → "Project"
3. Import your Git repository
4. Vercel will auto-detect Next.js and configure settings

### Step 3: Configure Environment Variables

In the Vercel dashboard, add these environment variables:

| Name | Value | Description |
|------|-------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` (or your backend URL) | Backend API endpoint |

**For Production:**
- If you have a deployed backend, use that URL
- If backend is not deployed, the frontend will show connection errors (expected)

### Step 4: Deploy

1. Click "Deploy"
2. Wait for build to complete (~2-3 minutes)
3. Vercel will provide a live URL (e.g., `https://calidus-frontend.vercel.app`)

---

## Option 2: Deploy via Vercel CLI

### Install Vercel CLI

```bash
npm install -g vercel
```

### Deploy from Command Line

```bash
# Navigate to frontend directory
cd frontend

# Login to Vercel
vercel login

# Deploy to production
vercel --prod
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? (select your account)
- Link to existing project? **N**
- What's your project's name? **calidus-frontend**
- In which directory is your code located? **.**
- Want to override settings? **N**

---

## 🔧 Build Configuration

### Vercel Settings

The project uses these settings (configured in `vercel.json` and `next.config.js`):

```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install"
}
```

### Environment Variables Needed

Create a `.env.production` file or set in Vercel dashboard:

```env
NEXT_PUBLIC_API_URL=https://your-backend-api.com
```

---

## 📱 Testing the Deployment

Once deployed, test these critical pages:

### Public Pages
1. **Homepage**: `https://your-app.vercel.app/`
2. **Login**: `https://your-app.vercel.app/login`
3. **Demo**: `https://your-app.vercel.app/demo`
4. **Consultancy Agreement** (password: 1234): `https://your-app.vercel.app/consultancy-agreement`

### Protected Dashboard Pages (requires login)
Login with: `username: admin`, `password: demo2024`

1. **Dashboard**: `https://your-app.vercel.app/dashboard`
2. **Requirements**: `https://your-app.vercel.app/dashboard/requirements`
3. **Test Cases**: `https://your-app.vercel.app/dashboard/test-cases`
4. **Traceability**: `https://your-app.vercel.app/dashboard/traceability`
5. **Risk Assessment**: `https://your-app.vercel.app/dashboard/risk`
6. **Compliance**: `https://your-app.vercel.app/dashboard/compliance`
7. **Conflicts**: `https://your-app.vercel.app/dashboard/conflicts`

### Test Checklist

- [ ] Homepage loads with CALIDUS logo
- [ ] API status indicator shows (red/yellow/green dot)
- [ ] Login page loads
- [ ] Demo credentials auto-fill works (click Admin/Engineer/Viewer buttons)
- [ ] Login redirects to dashboard
- [ ] Dashboard shows statistics (if backend is connected)
- [ ] Sidebar navigation works
- [ ] Footer link "RUYA Consultancy Agreement" works
- [ ] Password "1234" unlocks consultancy agreement
- [ ] PDF download button works on consultancy agreement page
- [ ] All dashboard pages load without errors

---

## 🔗 Connect to Backend API

### If Backend is Already Deployed

Update environment variable in Vercel:
```
NEXT_PUBLIC_API_URL=https://your-backend-api.com
```

### If Backend is Running Locally

For development/testing only:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Note**: Local backend won't work in production deployment. You need a publicly accessible backend API.

### Backend Deployment Options

1. **Railway.app** (Recommended for quick deploy)
   - Free tier available
   - Auto-deploys from Git
   - Easy PostgreSQL setup

2. **Render.com**
   - Free tier available
   - Docker support

3. **Fly.io**
   - Pay-as-you-go
   - Global edge network

4. **AWS/Azure/GCP**
   - Production-ready
   - More complex setup

---

## 🐛 Troubleshooting

### Build Fails with TypeScript Errors

If the build fails during deployment, you may need to temporarily disable strict type checking:

1. Update `next.config.js`:
```javascript
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,  // Temporary workaround
  },
  eslint: {
    ignoreDuringBuilds: true,  // Skip ESLint during builds
  },
  // ... rest of config
}
```

2. Redeploy

**Note**: Fix type errors properly after deployment for production quality.

### API Connection Errors

If you see "API Offline" or connection errors:

1. Check `NEXT_PUBLIC_API_URL` environment variable
2. Ensure backend is deployed and accessible
3. Check CORS settings on backend (must allow Vercel domain)
4. Verify backend health endpoint: `GET {API_URL}/health`

### Images Not Loading

Ensure logo and images are in `/public/images/` directory:
- `/public/images/CLS-AEROSPACE-LOGO.svg`

### PDF Download Not Working

The PDF generation uses client-side `jsPDF` library, which should work fine. If it doesn't:
1. Check browser console for errors
2. Ensure `jspdf` is in `package.json` dependencies
3. Clear browser cache and retry

---

## 📊 Performance Optimization

### For Production Deployment

1. **Enable Image Optimization**
   - Replace `<img>` tags with Next.js `<Image />` component
   - Vercel will automatically optimize images

2. **Enable Analytics**
   - Go to Vercel dashboard → Analytics → Enable
   - Track page views, Core Web Vitals, etc.

3. **Set up Custom Domain**
   - Vercel dashboard → Settings → Domains
   - Add your custom domain (e.g., `app.calidus.aero`)

---

## 🔐 Security Considerations

### Environment Variables
- Never commit `.env` files to Git
- Use Vercel dashboard to set production env vars
- Rotate API keys regularly

### Authentication
- Current demo credentials are for testing only
- Change admin password before production use
- Implement proper JWT token management

### CORS Configuration
Backend must allow requests from Vercel domain:
```python
# In FastAPI backend
origins = [
    "https://your-app.vercel.app",
    "https://your-custom-domain.com",
]
```

---

## 📈 Monitoring & Logs

### View Deployment Logs
1. Vercel dashboard → Deployments
2. Click on specific deployment
3. View "Building" and "Runtime" logs

### Real-time Logs
```bash
vercel logs
```

---

## 🚀 Continuous Deployment

Vercel automatically deploys when you push to Git:

- **Push to `main`** → Production deployment
- **Push to other branches** → Preview deployment
- Pull requests get unique preview URLs

---

## 📞 Support

If you encounter issues:

1. **Vercel Community**: [vercel.com/community](https://vercel.com/community)
2. **Next.js Docs**: [nextjs.org/docs](https://nextjs.org/docs)
3. **GitHub Issues**: Create an issue in your repository

---

## ✅ Post-Deployment Checklist

- [ ] Frontend deployed to Vercel successfully
- [ ] Custom domain configured (optional)
- [ ] Environment variables set correctly
- [ ] All pages accessible and loading
- [ ] Backend API connection working
- [ ] PDF download functionality tested
- [ ] Password-protected page tested (password: 1234)
- [ ] Mobile responsiveness verified
- [ ] Analytics enabled (optional)
- [ ] SSL certificate active (automatic on Vercel)

---

## 🎯 Next Steps

1. **Deploy Backend**: Deploy your FastAPI backend to make the full app functional
2. **Database**: Set up production PostgreSQL database
3. **Monitoring**: Add error tracking (Sentry, LogRocket)
4. **Testing**: Set up automated E2E tests
5. **Documentation**: Create user guide for stakeholders

---

**Generated**: October 29, 2025
**Version**: 1.0
**Status**: Ready for Deployment ✅
