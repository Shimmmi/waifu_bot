# 🔧 Fix: WebApp Showing Test Data

## 🔴 **Problem**

Your WebApp buttons point to:
```
https://waifu-bot-webapp.onrender.com
```

But this is a **separate service** with its own database (test data)!

Your **bot** service is different and has the real waifu data.

---

## ✅ **Solution: Two Options**

### **Option A: Use Same Service for Bot + API** (Recommended)

Run both the bot AND the API server in the same Render service.

### **Option B: Separate Services**

Keep bot and WebApp as separate services, but connect them properly.

---

## 🎯 **Option A: Combined Service** (Easiest)

### **Step 1: Create Combined Startup Script**

Create `start_combined.py`:

```python
#!/usr/bin/env python3
"""
Start both bot and API server in the same process
"""
import asyncio
import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
os.chdir(project_root)

if __name__ == "__main__":
    import logging
    from multiprocessing import Process
    import uvicorn
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)
    
    def run_bot():
        """Run the Telegram bot"""
        logger.info("🤖 Starting Bot process...")
        import run_bot
    
    def run_api():
        """Run the FastAPI server"""
        logger.info("🌐 Starting API process...")
        port = int(os.getenv('PORT', 10000))
        uvicorn.run(
            "bot.api_server:app",
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    
    # Start API server in background
    api_process = Process(target=run_api)
    api_process.start()
    
    logger.info("✅ API server started in background")
    
    # Start bot in main process
    run_bot()
```

### **Step 2: Update Render Start Command**

In Render Dashboard → Settings → Start Command:
```
python start_combined.py
```

### **Step 3: Update WebApp URLs**

The WebApp buttons should point to YOUR service URL. Find your Render URL:
- Dashboard → Your Service → URL at top (e.g., `your-bot.onrender.com`)

Update the URLs in `src/bot/handlers/menu.py`.

---

## 🎯 **Option B: Keep Separate Services**

If you want to keep the WebApp as a separate service:

### **Step 1: Deploy API Server Separately**

Create a new Render Web Service for the API:
- **Name:** `waifu-bot-api`
- **Start Command:** `uvicorn bot.api_server:app --host 0.0.0.0 --port $PORT`
- **Environment Variables:**
  - `DATABASE_URL` = (same Neon URL as bot)
  - `PORT` = `10000`

### **Step 2: Update WebApp Service**

Your existing `waifu-bot-webapp` service needs to know where the API is.

Add environment variable:
- `API_URL` = `https://waifu-bot-api.onrender.com`

Update WebApp JavaScript to use this URL when fetching data.

### **Step 3: Update Bot WebApp URLs**

Update `src/bot/handlers/menu.py` to point to your WebApp service URL.

---

## 🚀 **Quick Fix: Use Bot Service URL**

The easiest solution right now:

### **Step 1: Get Your Bot Service URL**

1. Go to Render Dashboard
2. Find your bot service
3. Copy the URL (top of page, e.g., `your-bot-name.onrender.com`)

### **Step 2: Update menu.py**

Replace all occurrences of `https://waifu-bot-webapp.onrender.com` with your bot URL.

Example:
```python
# OLD (pointing to separate test service):
web_app=WebAppInfo(url="https://waifu-bot-webapp.onrender.com/waifu-card/...")

# NEW (pointing to your bot service):
web_app=WebAppInfo(url="https://your-bot-name.onrender.com/waifu-card/...")
```

### **Step 3: Ensure API Server is Running**

Make sure `api_server.py` is being served by your bot service.

Add to `run_bot.py` or use the combined startup script above.

---

## 🔍 **Current Architecture**

**You have:**
```
Bot Service (your-bot.onrender.com)
  ├── Telegram Bot (polling)
  ├── Database: Neon PostgreSQL
  └── WebApp URLs point to → waifu-bot-webapp.onrender.com (❌ WRONG!)

Separate WebApp Service (waifu-bot-webapp.onrender.com)
  ├── Has own test database (❌ WRONG!)
  └── Shows test waifus
```

**You need:**
```
Single Service (your-bot.onrender.com)
  ├── Telegram Bot (polling)
  ├── FastAPI Server (port 10000) for /api/waifu endpoints
  ├── Static Files (WebApp HTML/JS/CSS)
  ├── Database: Neon PostgreSQL (shared)
  └── WebApp URLs point to → your-bot.onrender.com (✅ CORRECT!)
```

---

## ✅ **Implementation Steps**

### **1. Add Health Check** (Already done ✅)

The updated `run_bot.py` now includes a health check server on PORT.

### **2. Serve API + Static Files**

Update `run_bot.py` to serve both API and static files:

```python
async def start_web_server():
    """Start FastAPI server for WebApp"""
    from bot.api_server import app as fastapi_app
    
    port = int(os.getenv('PORT', 10000))
    
    config = uvicorn.Config(
        fastapi_app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()
```

### **3. Update WebApp URLs**

In `src/bot/handlers/menu.py`, replace:
```python
"https://waifu-bot-webapp.onrender.com"
```

With:
```python
os.getenv("WEB_APP_URL", "https://your-bot-name.onrender.com")
```

And set `WEB_APP_URL` in Render environment variables.

---

## 📊 **Comparison**

| Approach | Pros | Cons |
|----------|------|------|
| **Single Service** | Simple, one DATABASE_URL, cheaper | Single point of failure |
| **Separate Services** | Independent scaling, isolated failures | Complex, need to sync DATABASE_URL |

**Recommendation:** Use single service for now, split later if needed.

---

## 🆘 **Quick Debug**

### **Check What's Happening:**

1. **Open WebApp in browser**
2. **Open Developer Console** (F12)
3. **Go to Network tab**
4. **Click a waifu button**
5. **Look at API request:**
   - Where is it going? (should be your-bot.onrender.com)
   - What's the response? (should be your waifu data)

This will show exactly where the data is coming from!

---

**For now, the health check fix will solve the port timeout issue. Then we need to properly configure the WebApp URLs!** 🚀

