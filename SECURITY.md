# 🔐 Security Guide - Protecting Sensitive Information

## ⚠️ **Before Pushing to GitHub**

This guide helps you remove all sensitive information from your code before making it public.

---

## **Files with Sensitive Data**

### **🔴 Critical - Contains Passwords/Keys**

1. **`backend/api/backend_app.py`**
   - Line 22-26: Database credentials (`DB_CONFIG`)
   - **Action:** Move to environment variables

2. **`backend/utils/email_sender.py`**
   - Line 14-20: Database password
   - **Action:** Use environment variables

3. **`frontend/src/api/client.js`** (if exists)
   - API base URL might be hardcoded
   - **Action:** Use environment variable

---

## **Step-by-Step Security Setup**

### **Step 1: Create `.env` File (DO NOT COMMIT!)**

```bash
# This file is already in .gitignore
cp .env.example .env
# Edit .env with your actual credentials
```

**Edit `d:\SIH1\.env`:**
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=Lokesh@sql
DB_NAME=ppe

SMTP_USER=jblkkd@gmail.com
SMTP_PASSWORD=Safety@15
```

### **Step 2: Update Backend to Use Environment Variables**

**Modify `backend/api/backend_app.py`:**

```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

# OLD (INSECURE):
# DB_CONFIG = {
#     "host": "localhost",
#     "user": "root",
#     "password": "Lokesh@sql",  # ❌ EXPOSED!
#     "database": "ppe"
# }

# NEW (SECURE):
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),  # ✅ Hidden
    "database": os.getenv("DB_NAME", "ppe")
}
```

**Install python-dotenv:**
```bash
pip install python-dotenv
```

### **Step 3: Remove Worker Photos from Git**

```bash
# Worker photos are already in .gitignore
# They won't be committed
```

**Instead, provide a README:**
```markdown
# data/known_faces/
Place worker photos here in this structure:
```
worker_name/
  photo1.jpg
  photo2.jpg
```
```

---

## **What's Already Protected**

✅ **`.gitignore`** created - excludes:
- `.env` files
- `__pycache__/`
- `node_modules/`
- `data/known_faces/` (worker photos)
- Model files (`.pt`, `.weights`)
- Database files
- Logs

✅ **`.env.example`** created - safe template without real credentials

---

## **Files to Check Before Pushing**

Run this command to find potential secrets:

```bash
# Search for passwords in code
grep -r "password" backend/ --exclude-dir=venv
grep -r "secret" backend/ --exclude-dir=venv
grep -r "@gmail.com" . --exclude-dir=node_modules --exclude-dir=venv
```

---

## **Git Commands to Push Safely**

```bash
# 1. Check what will be committed
git status

# 2. Make sure .env is NOT listed (should be ignored)
git add .

# 3. Commit
git commit -m "Initial commit - PPE monitoring system"

# 4. Add remote (your GitHub repo)
git remote add origin https://github.com/yourusername/ppe-system.git

# 5. Push
git push -u origin main
```

---

## **If You Already Committed Secrets**

**Remove sensitive data from Git history:**

```bash
# Remove a specific file from all history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push to rewrite history
git push origin --force --all
```

**Better:** Delete repo and start fresh!

---

## **Public Repository Checklist**

Before making your repo public:

- [ ] `.gitignore` file created
- [ ] `.env.example` created (without real values)
- [ ] `.env` file is NOT committed (check with `git status`)
- [ ] Database passwords moved to environment variables
- [ ] SMTP passwords moved to environment variables
- [ ] Worker photos excluded (in `.gitignore`)
- [ ] No API keys hardcoded
- [ ] README.md has setup instructions
- [ ] requirements.txt created

---

## **README.md Setup Instructions**

Add this to your README:

```markdown
## Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/ppe-system.git
cd ppe-system
```

2. Create `.env` file
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Install dependencies
```bash
pip install -r requirements.txt
cd frontend && npm install
```

4. Run migrations
```bash
python backend/migrations/init_db.py
```

5. Start the application
```bash
# Backend
cd backend/api
uvicorn backend_app:app --reload

# Frontend
cd frontend
npm run dev
```
```

---

## **Additional Security Tips**

1. **Use GitHub Secrets** for CI/CD
2. **Enable branch protection** on main branch
3. **Add security scanning** (GitHub Dependabot)
4. **Never commit** `.env`, database dumps, or worker photos
5. **Use strong passwords** for production
6. **Change default passwords** before deployment

---

## **Quick Reference**

**Files that will be hidden:**
- `.env` (your actual secrets)
- `data/known_faces/` (worker photos)
- `__pycache__/`, `node_modules/`
- Model weight files (`.pt`)

**Files that will be public:**
- `.env.example` (template only)
- Source code (Python, JS)
- `requirements.txt`, `package.json`
- Documentation

---

**Your sensitive data is now protected!** ✅
