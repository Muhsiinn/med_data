# How to Deploy to Render.com (Free)

## Quick Deploy Steps

1. **Go to Render.com**
   - Visit: https://render.com
   - Sign up or log in (you can use your GitHub account)

2. **Create New Web Service**
   - Click "New +" button
   - Select "Web Service"
   - Connect your GitHub repository: `Muhsiinn/med_data`

3. **Configure the Service**
   - **Name**: `klinikum-report-editor` (or any name you like)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`

4. **Deploy**
   - Click "Create Web Service"
   - Wait 2-3 minutes for deployment
   - Your app will be live at: `https://your-app-name.onrender.com`

## Alternative: Railway.app

1. Visit https://railway.app
2. Connect GitHub and select the `med_data` repository
3. Railway will auto-detect and deploy your Flask app
4. Free tier includes 500 hours/month

## Note

- The free tier may sleep after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- Your sample data will persist on the server
