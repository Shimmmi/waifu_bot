# 🔧 Fix: DATABASE_URL Not Set on Render

## ❌ **Error:**
```
sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL from given URL string
```

This means `DATABASE_URL` environment variable is either:
1. Not set at all
2. Set to an empty string
3. Set to an invalid format

---

## ✅ **Solution: Set DATABASE_URL in Render**

### **Step 1: Get Your Neon Database URL**

1. Go to: https://console.neon.tech
2. Select your project
3. Click on your database
4. Find **"Connection String"** section
5. Copy the **full connection string**

It should look like:
```
postgresql://username:password@ep-xxxx-xxxx.region.aws.neon.tech/databasename?sslmode=require
```

### **Step 2: Add to Render Environment Variables**

1. Go to: https://dashboard.render.com
2. Select your **Web Service**
3. Click **"Environment"** tab (left sidebar)
4. Click **"Add Environment Variable"** button
5. Add:
   - **Key:** `DATABASE_URL`
   - **Value:** (paste your Neon connection string)
6. Click **"Save Changes"**

**⚠️ IMPORTANT:** After adding/changing environment variables, Render will automatically redeploy your service!

---

## 🔍 **Verify Environment Variables**

Make sure you have these set in Render:

| Variable | Example Value | Required |
|----------|---------------|----------|
| `BOT_TOKEN` | `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` | ✅ Yes |
| `DATABASE_URL` | `postgresql://user:pass@host/db` | ✅ Yes |
| `REDIS_URL` | `redis://localhost:6379/0` | ⚠️ Optional |
| `ENV` | `production` | ⚠️ Optional |

---

## 📊 **What the New Logs Will Show**

After deploying with the updated code, you'll see better error messages:

### **If DATABASE_URL is not set:**
```
❌ DATABASE_URL environment variable is not set!
```

### **If DATABASE_URL is set correctly:**
```
📊 Configuring database connection...
✅ DATABASE_URL found (length: 150 chars)
   Database type: postgresql
🔗 Creating database engine...
   URL scheme: postgresql
✅ Database engine created successfully
```

### **If DATABASE_URL format is wrong:**
```
❌ Failed to create database engine: Could not parse SQLAlchemy URL...
   DATABASE_URL starts with: sqlite:///waifu_bot...
```

---

## 🎯 **Common Issues & Solutions**

### **Issue 1: Using SQLite URL**

**Wrong:**
```
DATABASE_URL=sqlite:///waifu_bot.db
```

**Correct (Neon):**
```
DATABASE_URL=postgresql://username:password@ep-xxxx.neon.tech/dbname
```

**Why:** Render doesn't support SQLite (no persistent disk). You must use PostgreSQL (Neon).

---

### **Issue 2: Missing `?sslmode=require`**

**Without SSL (might fail):**
```
postgresql://user:pass@host/db
```

**With SSL (recommended):**
```
postgresql://user:pass@host/db?sslmode=require
```

**Solution:** Copy the full connection string from Neon dashboard.

---

### **Issue 3: Wrong Connection String Format**

Neon provides multiple formats. Use the **"Connection String"** format:

**✅ CORRECT:**
```
postgresql://username:password@ep-xxxxx.neon.tech/database
```

**❌ WRONG (this is for psql CLI):**
```
psql postgresql://username:password@ep-xxxxx.neon.tech/database
```

**❌ WRONG (this is connection details, not URL):**
```
Host: ep-xxxxx.neon.tech
Database: mydb
User: username
```

---

## 🚀 **Step-by-Step: Complete Setup**

### **1. Get Neon Connection String**

1. Login to Neon: https://console.neon.tech
2. Select your project
3. Navigate to **Dashboard** or **Connection Details**
4. Look for "Connection string" or "Connection URI"
5. Click **"Copy"** button
6. The string should start with `postgresql://`

### **2. Set in Render**

1. Login to Render: https://dashboard.render.com
2. Click your Web Service
3. Click **"Environment"** in left sidebar
4. If `DATABASE_URL` exists:
   - Click **"Edit"** (pencil icon)
   - Paste new value
   - Click **"Save"**
5. If it doesn't exist:
   - Click **"Add Environment Variable"**
   - Key: `DATABASE_URL`
   - Value: (paste connection string)
   - Click **"Add"**

### **3. Wait for Redeploy**

- Render will automatically redeploy
- Wait 2-3 minutes
- Watch "Events" tab for completion

### **4. Check Logs**

Go to **"Logs"** tab and look for:
```
✅ DATABASE_URL found
✅ Database engine created successfully
🚀 Starting Waifu Bot...
```

If you see these, database is connected! ✅

---

## 🔍 **Debugging Checklist**

If still having issues:

- [ ] **Check DATABASE_URL is set** in Render Environment tab
- [ ] **Verify format** starts with `postgresql://`
- [ ] **Check Neon database** is running (not paused)
- [ ] **Test connection** from Neon dashboard SQL editor
- [ ] **Check Render logs** for specific error messages
- [ ] **Try copying** connection string again from Neon
- [ ] **Restart Render service** after changing variables

---

## 📞 **Get Your Neon Connection String**

### **Quick Guide:**

1. **Login:** https://console.neon.tech
2. **Click your project name**
3. **Go to "Dashboard"**
4. **Look for "Connection Details" box**
5. **Find "Connection string" dropdown**
6. **Select "Connection string"** (not psql, not parameters)
7. **Click copy button** 📋
8. **Paste into Render** as `DATABASE_URL`

---

## ✅ **Expected Format**

Your `DATABASE_URL` should look like:

```
postgresql://neondb_owner:npg_xxxxxxxxxxxx@ep-xxxxxx-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require
```

**Parts:**
- `postgresql://` - Protocol
- `neondb_owner` - Username
- `npg_xxxx` - Password
- `@ep-xxxxx.neon.tech` - Host
- `/neondb` - Database name
- `?sslmode=require` - SSL parameter

---

## 🎯 **After Setting DATABASE_URL**

1. **Save** environment variable in Render
2. **Wait** for automatic redeploy (2-3 min)
3. **Check logs** for success messages
4. **Test bot** in Telegram
5. **Participate in event** 
6. **Check if stats update**

If you see database connection errors in logs, share the exact error message!

---

## 🆘 **Still Need Help?**

Share these details:

1. **First 20 characters of DATABASE_URL** (from Render Environment tab)
   - Example: `postgresql://neondb_`
2. **Render logs** showing the error
3. **Neon dashboard screenshot** showing connection string section

**⚠️ NEVER share the full DATABASE_URL publicly (contains password)!**

---

**Set DATABASE_URL now and redeploy!** 🚀

