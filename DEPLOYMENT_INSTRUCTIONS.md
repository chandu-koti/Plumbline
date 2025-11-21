# Render Deployment Instructions

## ✅ Pre-Deployment Checklist (COMPLETED)

- [x] Updated `requirements.txt` with pinned versions
- [x] Updated `Dockerfile` to use Python 3.12
- [x] Created `.streamlit/config.toml` for Streamlit configuration
- [x] Created `render.yaml` for Render deployment
- [x] Updated `README.md` with deployment instructions
- [x] Pushed all changes to GitHub

## 🚀 Deploy to Render

### Step 1: Go to Render Dashboard
1. Visit https://dashboard.render.com
2. Log in with your Render account

### Step 2: Create New Web Service
1. Click **"New +"** button
2. Select **"Web Service"**

### Step 3: Connect GitHub Repository
1. Select **"GitHub"** as the repository source
2. Search for and select **"Plumbline"** repository
3. Click **"Connect"**

### Step 4: Configure Deployment
The following settings should be auto-detected from `render.yaml`:
- **Name**: `plumbline-posture-analysis`
- **Environment**: Python
- **Python Version**: 3.12
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run app.py --server.port=10000 --server.address=0.0.0.0`
- **Plan**: Free (or select your preferred plan)

### Step 5: Deploy
1. Click **"Deploy"**
2. Wait for the build to complete (usually 3-5 minutes)
3. Once deployed, you'll get a URL like: `https://plumbline-posture-analysis.onrender.com`

## 📋 What's Configured

### Dockerfile
- Uses Python 3.12-slim base image
- Installs required system dependencies (OpenCV, FFmpeg, etc.)
- Exposes port 10000
- Runs Streamlit app with proper configuration

### render.yaml
- Specifies Python 3.12 runtime
- Sets up build and start commands
- Configures environment variables

### requirements.txt
- All dependencies pinned to specific versions for consistency:
  - mediapipe==0.10.9
  - opencv-python-headless==4.8.1.78
  - streamlit==1.28.1
  - numpy==1.24.3
  - matplotlib==3.8.2

### .streamlit/config.toml
- Configures Streamlit to run on port 10000
- Sets headless mode for server deployment
- Enables error details for debugging

## 🔍 Monitoring

After deployment:
1. Visit your app URL
2. Upload left and right side view images
3. The app should analyze posture and display results

Check logs in Render dashboard if there are any issues.

## 📝 GitHub Repository
- Repository: https://github.com/chandu-koti/Plumbline
- Branch: main
- Latest commit: Updated to Python 3.12 with pinned versions

---

**Status**: ✅ Ready for Render Deployment
