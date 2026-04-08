# 🚀 End-to-End Deployment Guide: Cloud & Raspberry Pi

This guide provides step-by-step instructions for hosting your Database, Backend, and Frontend online for free, and details how to set up your Raspberry Pi to run the AI detection model (`ppe_stream_server.py`) and connect it to your cloud infrastructure.

---

## Part 1: Cloud Hosting (Free Tier)

### 1️⃣ Database Hosting (TiDB Cloud)
We will use **TiDB Serverless** since it offers a generous free tier for MySQL databases.

1. **Sign Up**: Go to [TiDB Cloud](https://tidbcloud.com/) and create an account.
2. **Create Cluster**:
   - Choose **Serverless** (Free forever tier).
   - Select the region closest to you.
   - Name it `smart-ppe-db`.
3. **Get Credentials**:
   - Click your cluster name -> **Connect** -> **General**.
   - Generate your password and **COPY IT**.
   - Note down: `Host`, `Port` (usually 4000), `User`, `Password`, and `Database` (default is `test`).

### 2️⃣ Backend API Hosting (Render)
1. **Sign Up / Log In**: Go to [Render](https://render.com/).
2. **Create Web Service**:
   - Click **New** -> **Web Service**.
   - Connect your GitHub and select this repository.
3. **Configuration**:
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn api.backend_app:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables**:
   Add the following variables exactly as you copied them from TiDB:
   - `DB_HOST`: (Your TiDB Host)
   - `DB_PORT`: `4000`
   - `DB_USER`: (Your TiDB User)
   - `DB_PASSWORD`: (Your TiDB Password)
   - `DB_NAME`: `test`
   - `ALLOWED_ORIGINS`: `*`
5. **Deploy** and save your Backend URL (e.g., `https://smart-ppe-backend.onrender.com`).

### 3️⃣ Frontend Dashboard Hosting (Vercel)
1. **Sign Up / Log In**: Go to [Vercel](https://vercel.com/).
2. **Create Project**:
   - Click **Add New** -> **Project**.
   - Import your GitHub repository.
3. **Configuration**:
   - Set **Root Directory** to `frontend`.
   - Vercel will auto-detect Vite.
4. **Environment Variables**:
   - Add `VITE_API_URL` and set its value to your **Backend URL** from Render.
5. **Deploy** and save your Frontend URL (e.g., `https://smart-ppe-frontend.vercel.app`).

> [!TIP]
> After deploying all three, visit your Vercel URL. The dashboard should load and successfully fetch (empty) statistics from your Render backend.

---

## Part 2: Running the Model on Raspberry Pi

The AI Edge device (Raspberry Pi) processes video locally and sends data over your local network or the internet.

### 🍓 Prerequisites
- **Raspberry Pi 4 (4GB or 8GB RAM)** or **Raspberry Pi 5**. (YOLO & Face Recognition require good RAM).
- A compatible webcam plugged into the USB port or a Pi Camera Module.
- **Raspberry Pi OS (64-bit)** installed via [Raspberry Pi Imager](https://www.raspberrypi.com/software/).

### 💻 Step 1: System Preparation
First, boot up your Pi, connect to Wi-Fi, open the terminal, and update the system:
```bash
sudo apt update && sudo apt upgrade -y
```

Install critical system libraries required for OpenCV and Dlib (Face Recognition):
```bash
sudo apt install -y build-essential cmake pkg-config libx11-dev libopenblas-dev
sudo apt install -y libgtk-3-dev libbz2-dev libgl1 python3-opencv
```

### 📦 Step 2: Set Up the Project
Clone your repository to the Raspberry Pi:
```bash
git clone <your-github-repo-url>
cd Smart-PPE-Compliance-Monitoring-System/backend/detection
```

Create a virtual environment with access to the system packages (important for OpenCV):
```bash
python3 -m venv venv --system-site-packages
source venv/bin/activate
```

Install the required Python packages:
```bash
pip install ultralytics flask flask-cors requests
```

> [!WARNING]
> Installing `face_recognition` and its dependency `dlib` natively on a Raspberry Pi can take a very long time (sometimes over an hour) because it compiles from source. Wait patiently.
```bash
pip install face_recognition
```

### 🔗 Step 3: Run the Stream Server
You need to pass the URL of your hosted backend API so the Pi can send attendance and compliance data to the cloud.

Ensure your webcam is connected, then run:
```bash
python ppe_stream_server.py --source 0 --api-url https://smart-ppe-backend.onrender.com
```
*(Replace the `--api-url` value with your actual Render backend URL).*

### 🌐 Step 4: Viewing the Video Stream (Optional)
The Pi hosts a live video stream on port `5000` via HTTP.
- **Local Network**: If you open your **hosted Vercel App** on a phone/PC connected to the **same Wi-Fi network** as the Pi, it will naturally retrieve video from `http://<raspberry-pi-ip>:5000`.
- **Remote Viewing over Internet**: Browsers block loading `http://` streams on an `https://` (Vercel) website due to Mixed Content policies. To bypass this, install `ngrok` on the Pi:
  ```bash
  ngrok http 5000
  ```
  Ngrok will give you an `https://...` URL. You can temporarily update your Frontend's video stream URL variable to use the ngrok URL to view the stream from anywhere in the world.

---

> [!IMPORTANT]  
> **Performance Note**: Running YOLO and Face Recognition simultaneously on a Raspberry Pi CPU will be slow (likely ~1 to 3 FPS). For production, consider attaching a **Google Coral USB Accelerator** or upgrading edge hardware.
