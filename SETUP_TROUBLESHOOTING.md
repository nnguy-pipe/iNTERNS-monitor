# Quick Setup Guide - SSL Certificate Workaround

If you get SSL certificate errors during `pip install`, use one of these methods:

## Method 1: Disable SSL Verification (Development Only)

```bash
source venv/bin/activate

# Install with SSL disabled (NOT recommended for production)
pip install --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
```

## Method 2: Update CA Certificates

```bash
# On Linux/WSL2
sudo apt-get update
sudo apt-get install -y ca-certificates

# Update Python certificates
source venv/bin/activate
pip install certifi

# Point to certifi
export SSL_CERT_FILE=$(python -c "import certifi; print(certifi.where())")
pip install -r requirements.txt
```

## Method 3: Use Pre-built Wheels (Fastest)

```bash
# Install from cached wheels (no network needed)
pip install --no-index --find-links ./wheels -r requirements.txt
```

## Method 4: One-by-One Installation

If above doesn't work, install packages individually:

```bash
source venv/bin/activate

pip install --trusted-host pypi.python.org fastapi==0.104.1
pip install --trusted-host pypi.python.org pydantic==2.5.0
pip install --trusted-host pypi.python.org sqlalchemy==2.0.23
pip install --trusted-host pypi.python.org uvicorn==0.24.0
pip install --trusted-host pypi.python.org alembic==1.12.1
pip install --trusted-host pypi.python.org python-dotenv==1.0.0
```

## Method 5: Use apt Instead (Linux/WSL2)

```bash
# Install system packages
sudo apt-get install -y python3-fastapi python3-uvicorn python3-sqlalchemy

# Then run directly (without venv)
python3 -m uvicorn src.api.main:app --reload
```

---

## After Installation: Verify It Works

```bash
# Activate venv
source venv/bin/activate

# Test imports
python3 << 'EOF'
import uvicorn
import fastapi
import sqlalchemy
import pydantic
print("✅ All packages installed successfully")
EOF

# Run server
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

---

## Test the Server (In Another Terminal)

```bash
# Health check
curl http://localhost:8000/health

# Welcome message
curl http://localhost:8000/

# API docs (open in browser)
open http://localhost:8000/api/docs
```

---

## If All Else Fails: Docker

```bash
# Build Docker image (no Python/pip needed)
docker build -t ahms-backend .

# Run container
docker run -p 8000:8000 ahms-backend
```

---

## Troubleshooting Steps

1. **Check Python version**: `python3 --version` (need 3.12+)
2. **Check venv activation**: `which python` (should show `venv/bin/python`)
3. **Check pip location**: `which pip` (should show `venv/bin/pip`)
4. **List installed packages**: `pip list`
5. **Check uvicorn**: `python -m pip show uvicorn`

---

## Still Stuck?

Try this complete fresh start:

```bash
# 1. Remove old venv
rm -rf venv/

# 2. Create new venv
python3 -m venv venv

# 3. Activate
source venv/bin/activate

# 4. Upgrade pip
pip install --upgrade pip

# 5. Install with trusted hosts
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# 6. Verify
python -m uvicorn src.api.main:app --reload
```

---

**If none of these work, Docker is the most reliable option:**

```bash
docker-compose up
```

This avoids Python/pip issues entirely.
