# Connect Vercel Frontend to Railway Backend

Your backend is now deployed! 🎉
- **Backend URL**: https://refyne-api-production.up.railway.app
- **API Docs**: https://refyne-api-production.up.railway.app/docs

## Configure Vercel Environment Variable

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. **Select your Refyne project**
3. **Go to Settings** → **Environment Variables**
4. **Add new variable**:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://refyne-api-production.up.railway.app`
   - **Environments**: Check all (Production, Preview, Development)
5. **Click "Save"**
6. **Redeploy**:
   - Go to "Deployments" tab
   - Click "..." on latest deployment
   - Click "Redeploy"

## Update CORS in Backend (if needed)

If you get CORS errors, update the Railway backend CORS settings:

1. **In Railway dashboard**:
   - Go to your service
   - Click "Variables" tab
   - Add variable:
     - `CORS_ORIGINS` = `https://your-vercel-app.vercel.app,https://refyne-api-production.up.railway.app`

2. **Or update in code** (api/config.py):
```python
cors_origins: List[str] = [
    "https://your-vercel-app.vercel.app",
    "https://refyne-api-production.up.railway.app",
    "http://localhost:3000",
]
```

## Test the Connection

Once Vercel redeploys:
1. Visit your Vercel app
2. Try uploading a file
3. The app should now use the Railway backend

## Your URLs

- **Frontend (Vercel)**: https://your-app.vercel.app
- **Backend (Railway)**: https://refyne-api-production.up.railway.app
- **API Docs**: https://refyne-api-production.up.railway.app/docs

## Troubleshooting

### CORS Errors
Add your Vercel URL to CORS_ORIGINS in Railway environment variables

### API Not Found
Check that NEXT_PUBLIC_API_URL is set correctly in Vercel

### Network Errors
Verify Railway backend is running (check health endpoint)

## Success! 🚀

Your full-stack application is now deployed:
- ✅ Frontend on Vercel
- ✅ Backend on Railway
- ✅ Both connected and working
