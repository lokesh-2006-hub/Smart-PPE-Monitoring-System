
# ☁️ How to Host Your Application for Free

This guide will help you deploy your Smart PPE Compliance System to the cloud for free using **Vercel** (Frontend), **Render** (Backend), and **TiDB Cloud** (Database).

---

## 📋 Prerequisites
Create free accounts on the following platforms:
1. [GitHub](https://github.com/) (You already have this)
2. [Vercel](https://vercel.com/signup) (Login with GitHub)
3. [Render](https://render.com/register) (Login with GitHub)
4. [TiDB Cloud](https://tidbcloud.com/free-trial?utm_source=chatgpt&utm_medium=chatGPT&utm_campaign=trial) (For MySQL Database)

---

## 1️⃣ Step 1: Set up the Database (TiDB Cloud)
TiDB Cloud offers a generous **Free Tier (Serverless)** that is perfect for this project (5GB storage, free forever).

### 🚀 Creating the Cluster
1. **Sign Up/Login**: Go to [TiDB Cloud](https://tidbcloud.com/) and sign in with Google or GitHub.
2. **Create Cluster**:
   - Click **Create Cluster**.
   - Select **Serverless** (This is the free tier).
   - **Region**: Choose the region closest to you (e.g., AWS us-east-1, etc.).
   - **Cluster Name**: Give it a name like `smart-ppe-db`.
   - Click **Create**.
   - *Wait about 30 seconds for it to be created.*

### 🔑 Getting Connection Info
1. Once created, click on your cluster name to go to the **Overview** page.
2. Click the **Connect** button (top right).
3. Under **Connect with**, select **General**.
4. **Important**:
   - It will show a password generator. Click **Generate Password**.
   - **COPY THIS PASSWORD NOW!** You won't see it again.
5. In the same window, look for the components of your connection, or simply copy the **SQLAlchemy** URI if provided, but typically you need these 4 standard fields for our backend:
   - **Host**: (e.g., `gateway01.us-east-1.prod.aws.tidbcloud.com`)
   - **Port**: `4000`
   - **User**: (e.g., `2SeE...user.root`)
   - **Password**: (The one you just generated)
   - **Database Name**: Default is `test`. You can use `test` or create a new one.

> **Note**: TiDB uses port `4000` by default, not `3306`. This is normal.

---

## 2️⃣ Step 2: Deploy Backend (Render)
1. Log in to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository (`Smart-PPE-Compliance-Monitoring-System`).
4. **Configuration**:
   - **Name**: `smart-ppe-backend`
   - **Root Directory**: `backend` (Important!)
   - **Environment**: `Python 3`
   - **Region**: Choose same region as your database if possible (e.g., US East).
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn api.backend_app:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables**:
   Scroll down to "Environment Variables" and add these:
   - `DB_HOST`: (Your TiDB Host)
   - `DB_PORT`: `4000`
   - `DB_USER`: (Your TiDB User)
   - `DB_PASSWORD`: (Your TiDB Password)
   - `DB_NAME`: `test` (or whatever DB name you used)
   - `ALLOWED_ORIGINS`: `*` (or your Vercel URL later)
6. Click **Create Web Service**.
7. Wait for deployment. Once done, copy your **Backend URL** (e.g., `https://smart-ppe-backend.onrender.com`).

---

## 3️⃣ Step 3: Deploy Frontend (Vercel)
1. Log in to [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New...** -> **Project**.
3. Import your GitHub repository (`Smart-PPE-Compliance-Monitoring-System`).
4. **Configuration**:
   - **Framework Preset**: Vite (should auto-detect).
   - **Root Directory**: `frontend` (Click Edit to select the `frontend` folder).
5. **Environment Variables**:
   - `VITE_API_URL`: Paste your **Backend URL** from Step 2 (e.g., `https://smart-ppe-backend.onrender.com`).
6. Click **Deploy**.
7. Once deployed, you will get a domain (e.g., `https://smart-ppe-frontend.vercel.app`).

---

## 4️⃣ Step 4: Run Detection System (Locally)
The detection system typically needs to run on-site to access cameras and save bandwidth.
1. Open your terminal in VS Code.
2. Navigate to detection folder:
   ```bash
   cd backend/detection
   ```
3. Run the streaming server, pointing it to your **Cloud Backend**:
   ```bash
   python ppe_stream_server.py --source 0 --api-url https://smart-ppe-backend.onrender.com
   ```
   *(Replace the URL with your actual Render Backend URL)*.

### 🎥 Viewing the Video Feed
The video feed runs locally at `http://localhost:5000`.
- If you open your **Vercel Frontend** on the **same computer**, the video will work!
- If you open it on a phone, the video won't load (because `localhost` on the phone is the phone itself).
- **To view video remotely**: You need to use **ngrok**.
  ```bash
  ngrok http 5000
  ```
  Then update your Vercel Environment Variable `VITE_VIDEO_URL` (requires code request) or just accept it's for local viewing.
