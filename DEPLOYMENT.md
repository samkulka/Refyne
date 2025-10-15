# Refyne Deployment Guide

## Architecture

- **Frontend**: Next.js (deployed on Vercel)
- **Backend**: Python FastAPI (needs separate deployment)

## Backend Deployment Options

### Option 1: Railway (Recommended - Easiest)

1. **Create Railway Account**: https://railway.app
2. **Deploy from GitHub**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `Refyne` repository
   - Railway will auto-detect the Dockerfile
   - Click "Deploy"

3. **Configure Environment**:
   - Go to project settings
   - Add environment variables if needed
   - Railway will automatically set `PORT`

4. **Get API URL**:
   - Once deployed, Railway provides a URL like: `https://your-app.railway.app`
   - Use this URL in your frontend

### Option 2: Render.com

1. **Create Render Account**: https://render.com
2. **New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will detect `render.yaml` automatically
   - Click "Create Web Service"

3. **Configuration**:
   - Free tier available
   - Auto-deploys on git push
   - URL: `https://refyne-api.onrender.com`

### Option 3: Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login and deploy
fly auth login
fly launch
fly deploy
```

## Frontend Configuration

Once your backend is deployed, update the frontend API URL:

1. **Create `.env.local` in your project root**:
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

2. **Update API calls in Next.js**:
   - The frontend will use `process.env.NEXT_PUBLIC_API_URL`
   - Redeploy to Vercel

## Quick Deploy Commands

```bash
# Commit deployment configs
git add railway.json render.yaml DEPLOYMENT.md
git commit -m "Add deployment configurations"
git push origin main

# Deploy to Railway (after connecting repo)
# Just push to main - Railway auto-deploys

# Or deploy to Render
# Just push to main - Render auto-deploys

# Redeploy frontend on Vercel
# Vercel auto-deploys on push
```

## Health Checks

- Backend health: `GET https://your-api-url/api/v1/health`
- Frontend: Check Vercel deployment logs

## Environment Variables

Backend needs:
- `PORT` (auto-set by platform)
- Add any API keys/secrets as needed

Frontend needs:
- `NEXT_PUBLIC_API_URL` (your deployed backend URL)

## Monitoring

- Railway: Built-in logs and metrics
- Render: Logs in dashboard
- Vercel: Deployment logs and analytics

## Costs

- **Railway**: $5/month (500 hours free for students)
- **Render**: Free tier available (sleeps after inactivity)
- **Vercel**: Free for personal projects
