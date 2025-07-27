# 🚀 Render Deployment Guide

## Quick Deploy to Render

### Option 1: Deploy with render.yaml (Recommended)

1. **Fork/Clone this repository** to your GitHub account
2. **Go to [Render Dashboard](https://dashboard.render.com/)**
3. **Click "New +" → "Web Service"**
4. **Connect your GitHub repository**
5. **Render will automatically detect the `render.yaml` file**
6. **Click "Create Web Service"**

### Option 2: Manual Deploy

1. **Go to [Render Dashboard](https://dashboard.render.com/)**
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service:**
   - **Name**: `movie-recommender-system`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app_railway_simple:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
5. **Click "Create Web Service"**

## Configuration Details

### Files Used:
- **`app_railway_simple.py`** - Main Flask application
- **`requirements.txt`** - Python dependencies
- **`render.yaml`** - Render configuration
- **`templates/index_simple.html`** - Web interface

### Environment Variables:
- **`PORT`** - Automatically set by Render
- **`PYTHON_VERSION`** - Set to 3.12.0

### Health Check:
- **Path**: `/health`
- **Expected Response**: 200 OK with JSON status

## Expected Deployment Time

- **Build Time**: 2-3 minutes
- **Startup Time**: 30-60 seconds
- **Total Time**: 3-4 minutes

## Troubleshooting

### If deployment fails:

1. **Check Build Logs**: Look for dependency installation errors
2. **Check Runtime Logs**: Look for application startup errors
3. **Verify Requirements**: Ensure all dependencies are in `requirements.txt`
4. **Check Port Binding**: Ensure app binds to `0.0.0.0:$PORT`

### Common Issues:

1. **Port Issues**: Make sure app uses `$PORT` environment variable
2. **Dependencies**: Ensure all packages are in `requirements.txt`
3. **Start Command**: Verify gunicorn command is correct
4. **Health Check**: Ensure `/health` endpoint returns 200 OK

## Success Indicators

✅ **Build completes successfully**
✅ **Health check passes**
✅ **Application responds to requests**
✅ **Web interface loads**

## Next Steps After Deployment

1. **Test the application** at your Render URL
2. **Add ML functionality** back gradually
3. **Load movie data** in background
4. **Implement full recommendations**

## Support

If you encounter issues:
1. Check Render logs in the dashboard
2. Verify all files are committed to GitHub
3. Ensure repository is public (for free tier)
4. Check Render documentation for common issues 