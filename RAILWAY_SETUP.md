# Railway Deployment Guide

## What is Railway?

Railway is a modern cloud platform that makes deploying applications incredibly simple. Think of it as:
- **Simpler than AWS** - No complex configuration
- **Better than Heroku** - More generous free tier, modern interface
- **Purpose-built for developers** - Git-based deployments, instant previews

### Why Railway for Refyne?

1. **Dockerfile Support**: Railway detects and deploys your Dockerfile automatically
2. **Free Tier**: $5 credit/month (plenty for testing)
3. **Auto-deploys**: Pushes to GitHub automatically deploy
4. **Built-in Monitoring**: Logs, metrics, and health checks
5. **Fast**: Deploy in under 2 minutes

## Step-by-Step Setup (5 minutes)

### 1. Create Railway Account

Visit: https://railway.app

- Click "Start a New Project" or "Login with GitHub"
- Authorize Railway to access your GitHub repos

### 2. Deploy Your Backend

**Option A: From Dashboard**
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose `samkulka/Refyne`
4. Railway automatically detects your Dockerfile
5. Click "Deploy"

**Option B: From GitHub Repo**
1. Go to your repo: https://github.com/samkulka/Refyne
2. Look for "Deploy on Railway" button (if you add the badge)
3. Click and authorize

### 3. Wait for Build (1-2 minutes)

Railway will:
- Clone your repo
- Build the Docker image
- Deploy to a container
- Assign a public URL

### 4. Get Your API URL

Once deployed:
1. Go to your Railway project
2. Click on your service
3. Go to "Settings" → "Domains"
4. Click "Generate Domain"
5. Copy the URL (e.g., `https://refyne-production.up.railway.app`)

### 5. Test Your Backend

```bash
# Test health endpoint
curl https://your-railway-url.railway.app/api/v1/health

# Should return: {"status":"healthy"}
```

### 6. Configure Environment Variables (Optional)

If you need env vars:
1. Go to your service in Railway
2. Click "Variables" tab
3. Add key-value pairs
4. Railway auto-restarts on changes

## Connect Frontend to Backend

### Update Next.js Environment

1. **In your local repo**:
```bash
cd /Users/samkulka/Desktop/Coding/Python/Refyne_github

# Create environment file
cat > .env.local <<EOF
NEXT_PUBLIC_API_URL=https://your-railway-url.railway.app
EOF
```

2. **Update your Next.js API calls** (if needed):
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

3. **Add environment variable to Vercel**:
   - Go to Vercel dashboard
   - Select your project
   - Settings → Environment Variables
   - Add `NEXT_PUBLIC_API_URL` = `https://your-railway-url.railway.app`
   - Redeploy

4. **Commit and push**:
```bash
git add .env.local
git commit -m "Configure backend URL"
git push
```

## Monitoring & Logs

### View Logs
1. Go to Railway dashboard
2. Click your service
3. "Deployments" tab shows build logs
4. Click "View Logs" for runtime logs

### Metrics
Railway shows:
- CPU usage
- Memory usage
- Network traffic
- Request counts

## Troubleshooting

### Build Fails
- Check Railway build logs
- Ensure Dockerfile is in repo root
- Verify requirements.txt is complete

### App Won't Start
- Check if health endpoint works: `/api/v1/health`
- Review runtime logs in Railway
- Ensure port is set to `$PORT` (Railway provides this)

### CORS Errors
Add to your FastAPI app:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-vercel-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Costs

### Free Tier
- $5 credit/month (resets monthly)
- ~500 hours of execution time
- Perfect for development/testing

### Hobby Plan
- $5/month
- More resources
- Custom domains
- Priority support

### Pro Plan
- $20/month
- Team features
- Higher limits

## Auto-Deployments

Railway automatically deploys when you:
1. Push to your `main` branch
2. Merge a pull request
3. Manually trigger from dashboard

### Disable Auto-Deploy (if needed)
1. Railway dashboard → Your service
2. Settings → "Source"
3. Toggle "Auto Deploy"

## Custom Domain (Optional)

1. Railway dashboard → Your service
2. Settings → Domains
3. Click "Custom Domain"
4. Add your domain (e.g., `api.refyne.io`)
5. Add CNAME record in your DNS:
   ```
   CNAME api your-service.up.railway.app
   ```

## Summary

**Deployment Command**: Just push to GitHub!
```bash
git push origin main
# Railway deploys automatically
```

**Your URLs**:
- Backend API: `https://your-service.up.railway.app`
- API Docs: `https://your-service.up.railway.app/docs`
- Health Check: `https://your-service.up.railway.app/api/v1/health`

**Next Step**: Update Vercel environment with your Railway URL
