# 🗄️ Setup Neon Database - Complete Guide

## ✅ **Bot is Connected!** But Tables Are Missing

Your logs show:
```
✅ Waifu Bot is ready!
📡 Polling for updates...
```

But also:
```
❌ Error: relation "waifu" does not exist
```

This means the bot connected to Neon successfully, but the database is **empty** - no tables exist yet!

---

## 🎯 **Solution: Create Database Tables**

You have **2 options**:

---

### **Option 1: Use Neon SQL Editor** (Easiest for Production)

#### **Step 1: Open Neon SQL Editor**

1. Go to: https://console.neon.tech
2. Login and select your project
3. Click **"SQL Editor"** in the left sidebar

#### **Step 2: Run SQL Scripts**

Copy and paste each script below **in order**, clicking **"Run"** after each one:

**Script 1: Create Basic Tables**
```sql
-- users
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  tg_id BIGINT UNIQUE NOT NULL,
  username TEXT,
  display_name TEXT,
  coins BIGINT DEFAULT 0,
  gems BIGINT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now(),
  last_daily TIMESTAMPTZ DEFAULT '1970-01-01',
  daily_streak INT DEFAULT 0,
  pity_counter INT DEFAULT 0,
  daily_xp INT DEFAULT 0,
  last_xp_reset TIMESTAMPTZ DEFAULT now()
);

-- waifu_templates
CREATE TABLE IF NOT EXISTS waifu_templates (
  template_id SERIAL PRIMARY KEY,
  code TEXT UNIQUE,
  name TEXT,
  rarity TEXT,
  artwork_url TEXT,
  base_stats JSONB,
  skills JSONB,
  tags TEXT[],
  created_at TIMESTAMPTZ DEFAULT now()
);

-- waifus (instances)
CREATE TABLE IF NOT EXISTS waifus (
  id BIGSERIAL PRIMARY KEY,
  owner_id INT REFERENCES users(id) ON DELETE CASCADE,
  template_id INT REFERENCES waifu_templates(template_id),
  nickname TEXT,
  level INT DEFAULT 1,
  xp BIGINT DEFAULT 0,
  affection INT DEFAULT 0,
  skin_id INT DEFAULT NULL,
  is_active BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now(),
  last_xp_at TIMESTAMPTZ DEFAULT '1970-01-01'
);

-- xp logs
CREATE TABLE IF NOT EXISTS xp_logs (
  id BIGSERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  waifu_id BIGINT REFERENCES waifus(id),
  source TEXT,
  amount INT,
  meta JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- pull history
CREATE TABLE IF NOT EXISTS pull_history (
  id BIGSERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  type TEXT,
  cost JSONB,
  result JSONB,
  pity_counter INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- transactions
CREATE TABLE IF NOT EXISTS transactions (
  id BIGSERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  kind TEXT,
  amount BIGINT,
  currency TEXT,
  reason TEXT,
  meta JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- indexes
CREATE INDEX IF NOT EXISTS idx_users_tg_id ON users(tg_id);
CREATE INDEX IF NOT EXISTS idx_waifus_owner_id ON waifus(owner_id);
CREATE INDEX IF NOT EXISTS idx_xp_logs_user_id ON xp_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_pull_history_user_id ON pull_history(user_id);
```

Click **"Run"** ✅

**Script 2: Create Waifu Table (Main Pool)**
```sql
-- Create the main waifu table (for generated/pool waifus)
CREATE TABLE IF NOT EXISTS waifu (
    id TEXT PRIMARY KEY,
    card_number INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    rarity TEXT NOT NULL,
    race TEXT NOT NULL,
    profession TEXT NOT NULL,
    nationality TEXT NOT NULL,
    image_url TEXT,
    owner_id BIGINT,
    level INTEGER NOT NULL DEFAULT 1,
    xp INTEGER NOT NULL DEFAULT 0,
    stats JSONB NOT NULL,
    dynamic JSONB NOT NULL,
    tags JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create events table
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    start_time TIMESTAMPTZ NOT NULL DEFAULT now(),
    end_time TIMESTAMPTZ,
    rewards JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create event_participations table
CREATE TABLE IF NOT EXISTS event_participations (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    waifu_id TEXT NOT NULL REFERENCES waifu(id),
    event_id INTEGER NOT NULL REFERENCES events(id),
    score DOUBLE PRECISION NOT NULL,
    rewards_received JSONB,
    participated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_waifu_owner_id ON waifu(owner_id);
CREATE INDEX IF NOT EXISTS idx_waifu_rarity ON waifu(rarity);
CREATE INDEX IF NOT EXISTS idx_waifu_card_number ON waifu(card_number);
CREATE INDEX IF NOT EXISTS idx_event_participations_user_id ON event_participations(user_id);
CREATE INDEX IF NOT EXISTS idx_event_participations_waifu_id ON event_participations(waifu_id);
```

Click **"Run"** ✅

#### **Step 3: Verify Tables Created**

Run this query to check:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

You should see these tables:
- ✅ `users`
- ✅ `waifu`
- ✅ `waifus`
- ✅ `waifu_templates`
- ✅ `events`
- ✅ `event_participations`
- ✅ `xp_logs`
- ✅ `pull_history`
- ✅ `transactions`

#### **Step 4: Restart Bot**

1. Go to Render Dashboard
2. Click your service
3. Click **"Manual Deploy"** → **"Deploy latest commit"**
4. Wait for deployment
5. Check logs - errors should be gone!

---

### **Option 2: Run Migration Locally** (For Development)

If you want to run migrations from your local machine:

#### **Step 1: Set DATABASE_URL Locally**

Create `.env` file in project root:
```
DATABASE_URL=postgresql://your-neon-url-here
```

(Copy the full URL from Neon dashboard)

#### **Step 2: Activate Virtual Environment**
```bash
.venv\Scripts\activate.ps1
```

#### **Step 3: Run Migration**
```bash
python run_migration.py
```

This will initialize the dynamic stats for existing waifus.

---

## 🔍 **After Setup - Verify Everything Works**

### **Check Render Logs**

After restarting, you should see:
```
✅ Waifu Bot is ready!
📡 Polling for updates...
✅ Restored stats for X waifus
```

**No more errors about "waifu" not existing!** ✅

### **Test the Bot**

1. Open bot in Telegram: `/start`
2. The bot should respond normally
3. Try commands - should work now!

---

## 🆘 **Troubleshooting**

### **Issue: Still Getting "relation waifu does not exist"**

**Solutions:**
1. Make sure you ran **both SQL scripts** in Neon
2. Verify tables exist (run verification query)
3. Restart Render service
4. Check you're using the correct Neon database

### **Issue: SQL Script Fails**

**Check:**
- Are you using the Neon SQL Editor (not local psql)?
- Did you run scripts in order (Script 1, then Script 2)?
- Any error messages in Neon console?

### **Issue: Tables Created But Bot Still Errors**

**Solutions:**
1. Check Render is using correct DATABASE_URL
2. Verify DATABASE_URL points to same Neon database
3. Try restarting Render service
4. Check Neon database is not paused

---

## 📊 **Database Schema Overview**

After setup, you'll have:

### **User Management:**
- `users` - Telegram users
- `transactions` - Coin/gem transactions

### **Waifu System:**
- `waifu` - Main waifu pool (all generated waifus)
- `waifus` - User-owned waifu instances
- `waifu_templates` - Waifu templates

### **Events:**
- `events` - Event definitions
- `event_participations` - Event participation records

### **Progression:**
- `xp_logs` - XP gain history
- `pull_history` - Gacha pull history

---

## ✅ **Success Checklist**

After running the setup:

- [ ] Ran Script 1 in Neon SQL Editor
- [ ] Ran Script 2 in Neon SQL Editor  
- [ ] Verified tables exist (ran verification query)
- [ ] Restarted Render service
- [ ] Checked Render logs - no "relation waifu" errors
- [ ] Tested bot in Telegram - responds normally
- [ ] All features work (events, waifus, etc.)

---

## 🎯 **Quick Setup Summary**

1. **Open Neon SQL Editor**
2. **Run Script 1** (users, waifus, transactions, etc.)
3. **Run Script 2** (waifu table, events, participations)
4. **Verify** tables created
5. **Restart** Render service
6. **Test** bot in Telegram

**That's it!** Your database will be ready! 🎉

---

## 📞 **Need Help?**

If you encounter issues:

1. **Share Neon SQL Editor output** (any errors)
2. **Share Render logs** after restart
3. **List tables** (run verification query)

This will help diagnose the problem!

---

**Run the SQL scripts now and your bot will be fully functional!** 🚀

