# 🏰 Clan System Migration Guide

## Overview
This guide explains how to apply the SQL migration for the clan system to your Neon PostgreSQL database.

## Migration File
**File:** `sql/012_create_clan_system.sql`

## Prerequisites
1. Access to your Neon Console
2. Your PostgreSQL connection string
3. Admin/owner permissions on the database

## Steps to Apply Migration

### 1. Open Neon Console
- Go to https://console.neon.tech
- Log in to your account
- Select your project

### 2. Navigate to SQL Editor
- Click on your project
- Select "SQL Editor" from the left sidebar
- You'll see a query editor interface

### 3. Read the Migration File
Open `sql/012_create_clan_system.sql` in a text editor and copy all its contents.

### 4. Execute the Migration
1. Paste the SQL migration code into the SQL Editor
2. Review the migration:
   - Creates `clans` table
   - Creates `clan_members` table
   - Creates `clan_events` table
   - Creates `clan_event_participations` table
   - Creates `clan_chat_messages` table
   - Adds `clan_id` column to `users` table
   - Creates indexes for performance
3. Click "Run" or press Ctrl+Enter
4. Wait for execution to complete

### 5. Verify Migration
Run these queries to verify the tables were created:

```sql
-- Check if tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('clans', 'clan_members', 'clan_events', 'clan_event_participations', 'clan_chat_messages')
ORDER BY table_name;

-- Check if clan_id column was added to users
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' 
  AND column_name = 'clan_id';
```

Expected results:
- 5 tables created successfully
- `clan_id` column added to `users` table

## Post-Migration
1. Restart your bot application
2. Test clan functionality:
   - Create a clan
   - Join a clan
   - Send chat messages
   - Leave a clan

## Troubleshooting

### Error: "table already exists"
If tables already exist, the migration uses `IF NOT EXISTS` so it should skip creation. Check if the tables are correctly structured.

### Error: "relation does not exist"
If you get this error for the `users` table:
1. Make sure you're connected to the correct database
2. Check that previous migrations have been applied

### Error: "column already exists"
If `clan_id` already exists in `users` table, the migration will skip it due to `ADD COLUMN IF NOT EXISTS`.

## What's Created

### Tables
1. **clans** - Main clan information
   - id, name, tag, description, emblem_id
   - type (open/invite/closed)
   - leader_id, level, experience, total_power
   - created_at, settings (JSON)

2. **clan_members** - Clan membership
   - clan_id, user_id, role (leader/officer/member)
   - joined_at, last_active
   - donated_gold, donated_skills

3. **clan_events** - Clan events
   - clan_id, event_type
   - started_at, ends_at, status
   - data, rewards (JSON)

4. **clan_event_participations** - Event participation
   - event_id, user_id
   - score, contribution (JSON)

5. **clan_chat_messages** - Clan chat
   - clan_id, user_id, message
   - created_at, is_deleted

### Indexes
- Performance indexes on foreign keys and commonly queried columns
- Helps with lookups and joins

## Next Steps
After applying this migration:
1. ✅ Restart your bot
2. ✅ Test clan creation in WebApp
3. ✅ Test joining/searching clans
4. ✅ Test clan chat
5. ⏳ Implement clan events (Phase 2)

## Support
If you encounter issues:
1. Check the bot logs for detailed errors
2. Verify all previous migrations have been applied
3. Ensure you have the correct database permissions

Good luck! 🚀

