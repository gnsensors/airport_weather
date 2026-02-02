# Direct Database Access Guide

## Methods to Query Railway PostgreSQL Database

### Method 1: Railway CLI (Easiest)

**Install Railway CLI:**
```bash
npm install -g @railway/cli
# or
brew install railway
```

**Login and Connect:**
```bash
# Login to Railway
railway login

# Link to your project
cd /home/geofnoakes/code/airport_weather
railway link

# Connect directly to PostgreSQL
railway connect postgres
```

This opens a `psql` session directly to your Railway database!

**Example Queries:**
```sql
-- List all tables
\dt

-- Count visitors
SELECT COUNT(*) FROM visitors;

-- View top 10 visitors
SELECT ip_address, visit_count, last_visit
FROM visitors
ORDER BY visit_count DESC
LIMIT 10;

-- Count searches by city
SELECT city, COUNT(*) as count
FROM weather_searches
GROUP BY city
ORDER BY count DESC
LIMIT 10;

-- Recent searches
SELECT ip_address, city, timestamp, success, error_message
FROM weather_searches
ORDER BY timestamp DESC
LIMIT 20;

-- Exit
\q
```

---

### Method 2: SSH Tunnel + psql (Traditional Method)

Railway doesn't expose PostgreSQL publicly by default, but you can use the Railway CLI to create a tunnel.

**Step 1: Get Database Credentials**

In Railway Dashboard:
1. Go to your PostgreSQL service
2. Click "Variables" tab
3. Note these values:
   - `PGHOST`
   - `PGPORT`
   - `PGUSER`
   - `PGPASSWORD`
   - `PGDATABASE`

**Step 2: Create Tunnel with Railway CLI**
```bash
# Start a tunnel (creates local proxy to Railway DB)
railway run --service postgres

# In another terminal, connect using psql
psql -h localhost -p 5432 -U postgres -d railway
# Enter password when prompted
```

---

### Method 3: Railway Proxy (Port Forwarding)

**Using Railway CLI:**
```bash
# Forward Railway PostgreSQL to local port 5433
railway connect postgres --port 5433
```

**Then connect with any PostgreSQL client:**
```bash
# psql
psql postgresql://postgres:password@localhost:5433/railway

# or use GUI tools like pgAdmin, DBeaver, TablePlus
# Connection: localhost:5433
```

---

### Method 4: Direct Connection (If Public Access Enabled)

⚠️ **Not recommended for production** - Railway databases are private by default for security.

If you enable TCP Proxy in Railway:
1. Railway → PostgreSQL → Settings → Enable "TCP Proxy"
2. Get the public hostname (e.g., `postgres-production.railway.app:12345`)

```bash
psql postgresql://postgres:password@postgres-production.railway.app:12345/railway
```

---

## Using GUI Database Clients

### DBeaver, pgAdmin, TablePlus, etc.

**Option A: Via Railway Tunnel**
```bash
# Terminal 1: Create tunnel
railway connect postgres --port 5433
```

**Then in your GUI client:**
- Host: `localhost`
- Port: `5433`
- Database: `railway` (or value from `PGDATABASE`)
- User: `postgres` (or value from `PGUSER`)
- Password: (from `PGPASSWORD` variable)

**Option B: Via Railway Environment Variables**

Get the full `DATABASE_URL`:
```bash
railway variables --service postgres | grep DATABASE_URL
```

Parse the URL:
```
postgresql://postgres:password@postgres.railway.internal:5432/railway
```

Use with tunnel:
```bash
railway connect postgres
# Then connect GUI to localhost:5432
```

---

## Common SQL Queries for Your App

### Visitor Analytics
```sql
-- Total unique visitors
SELECT COUNT(*) FROM visitors;

-- Total visits
SELECT SUM(visit_count) FROM visitors;

-- Top 10 visitors by visits
SELECT ip_address, visit_count, first_visit, last_visit
FROM visitors
ORDER BY visit_count DESC
LIMIT 10;

-- Visitors by date
SELECT DATE(first_visit) as date, COUNT(*) as new_visitors
FROM visitors
GROUP BY DATE(first_visit)
ORDER BY date DESC;
```

### Search Analytics
```sql
-- Total searches
SELECT COUNT(*) FROM weather_searches;

-- Successful vs failed searches
SELECT success, COUNT(*)
FROM weather_searches
GROUP BY success;

-- Top searched cities
SELECT city, COUNT(*) as searches
FROM weather_searches
GROUP BY city
ORDER BY searches DESC
LIMIT 20;

-- Searches per day
SELECT DATE(timestamp) as date, COUNT(*) as searches
FROM weather_searches
GROUP BY DATE(timestamp)
ORDER BY date DESC;

-- Failed searches with errors
SELECT ip_address, city, timestamp, error_message
FROM weather_searches
WHERE success = false
ORDER BY timestamp DESC
LIMIT 20;

-- Searches by specific IP
SELECT city, timestamp, success, temperature, weather_description
FROM weather_searches
WHERE ip_address = '123.456.789.0'
ORDER BY timestamp DESC;
```

### Combined Analytics
```sql
-- Top IPs with search counts
SELECT
    v.ip_address,
    v.visit_count,
    COUNT(w.id) as total_searches,
    COUNT(DISTINCT w.city) as unique_cities
FROM visitors v
LEFT JOIN weather_searches w ON v.ip_address = w.ip_address
GROUP BY v.ip_address, v.visit_count
ORDER BY total_searches DESC
LIMIT 10;

-- Hourly search activity
SELECT
    EXTRACT(HOUR FROM timestamp) as hour,
    COUNT(*) as searches
FROM weather_searches
GROUP BY EXTRACT(HOUR FROM timestamp)
ORDER BY hour;
```

### Database Maintenance
```sql
-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Show indexes
SELECT * FROM pg_indexes WHERE schemaname = 'public';

-- Vacuum analyze (optimize)
VACUUM ANALYZE visitors;
VACUUM ANALYZE weather_searches;
```

---

## Quick Reference

### Railway CLI Commands
```bash
railway login                    # Login to Railway
railway link                     # Link current directory to project
railway connect postgres         # Connect to PostgreSQL
railway variables                # List all environment variables
railway logs                     # View application logs
railway status                   # Check deployment status
```

### PostgreSQL Commands (in psql)
```sql
\dt                              -- List all tables
\d table_name                    -- Describe table structure
\di                              -- List indexes
\l                               -- List databases
\c database_name                 -- Switch database
\q                               -- Quit
```

---

## Troubleshooting

### "railway: command not found"
```bash
# Install Railway CLI
npm install -g @railway/cli
# or
brew install railway
```

### "Connection refused"
- Make sure you're running `railway connect postgres` in a separate terminal
- Check that the tunnel is active

### "Authentication failed"
- Get fresh credentials: `railway variables --service postgres`
- Password might have changed - use the current `PGPASSWORD` value

### "Could not translate host name"
- Railway internal hostnames (`.railway.internal`) only work from within Railway
- Use `railway connect` to create a tunnel to localhost

---

## Security Best Practices

✅ **Do:**
- Use Railway CLI tunnel for development
- Keep database credentials secure (don't commit to git)
- Use read-only queries when exploring data

❌ **Don't:**
- Don't enable public TCP proxy for production databases
- Don't share `DATABASE_URL` or credentials
- Don't commit `.env` files with database passwords
