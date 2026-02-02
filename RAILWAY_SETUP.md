# Railway Deployment Setup with PostgreSQL

## Multi-Container Architecture

This application uses **two separate containers** in Railway:

```
┌─────────────────────────────────────────┐
│         Railway Private Network         │
│                                         │
│  ┌─────────────────┐  ┌──────────────┐ │
│  │  Web App        │  │  PostgreSQL  │ │
│  │  Container      │◄─┤  Container   │ │
│  │  (Python/Flask) │  │  (Database)  │ │
│  │  Port: $PORT    │  │  Port: 5432  │ │
│  └────────┬────────┘  └──────────────┘ │
│           │                             │
└───────────┼─────────────────────────────┘
            │
            ▼
    Public Internet
  (Railway Domain)
```

## Step-by-Step Deployment Instructions

### 1. Create PostgreSQL Database Container

In your Railway project:

1. Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway deploys PostgreSQL in a **separate container**
3. Railway automatically sets these environment variables:
   - `DATABASE_URL` - Full connection string with internal IP
     ```
     postgresql://postgres:password@postgres.railway.internal:5432/railway
     ```
   - `PGHOST` - Internal hostname (e.g., `postgres.railway.internal`)
   - `PGPORT` - Port `5432`
   - `PGUSER`, `PGPASSWORD`, `PGDATABASE`

### 2. Deploy Web Application Container

Your web app is already configured to:
- Connect to PostgreSQL using `DATABASE_URL` environment variable
- Resolve internal Railway hostnames automatically
- Initialize database tables automatically on startup
- Fall back to SQLite if DATABASE_URL is not set (for local development)

### 3. Container Networking (Automatic)

Railway handles all networking automatically:

**Private Network Communication:**
- ✅ Web app and PostgreSQL are in the same **private network**
- ✅ Communication uses **internal IPs** (not public internet)
- ✅ `DATABASE_URL` includes internal hostname like `postgres.railway.internal`
- ✅ Fast, secure, no egress charges

**Public Access:**
- ✅ Only the web app is exposed to the internet via Railway domain
- ✅ PostgreSQL is **NOT** publicly accessible (secure by default)
- ✅ Web app acts as the API gateway

### 4. Verify Separate Containers

In Railway dashboard, you should see **two separate services**:

```
Your Railway Project
├── 🌐 airport_weather (Web App Container)
│   ├── Status: Active
│   ├── Domain: airportweather-production.up.railway.app
│   └── Environment: DATABASE_URL → points to postgres container
│
└── 🗄️  PostgreSQL (Database Container)
    ├── Status: Active
    ├── Internal: postgres.railway.internal:5432
    └── No public access (secure)
```

### 5. Verify Deployment

After deployment:

1. **Check web app logs** for:
   ```
   ✅ Database initialized successfully
   Connected to: postgresql://postgres:***@postgres.railway.internal:5432/railway
   [INFO] Listening at: http://0.0.0.0:XXXX
   ```

2. **Verify container networking**:
   - Go to Railway → Web App → Variables
   - Find `DATABASE_URL` - it should contain `postgres.railway.internal` (internal hostname)
   - This confirms containers are communicating via private network

3. **Test the application**:
   - Visit your Railway domain
   - Search for a city
   - Go to `/stats` to see analytics

4. **Check database directly**:
   - Railway → PostgreSQL → Connect
   - Run: `\dt` to see tables (`visitors`, `weather_searches`)
   - Run: `SELECT COUNT(*) FROM visitors;` to see visitor count

## Database Schema

### Table: `visitors`
Tracks unique IP addresses and visit counts.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| ip_address | VARCHAR(45) | IP address (unique, indexed) |
| first_visit | DATETIME | First visit timestamp |
| last_visit | DATETIME | Last visit timestamp |
| visit_count | INTEGER | Total visits from this IP |
| user_agent | VARCHAR(500) | Browser/device info |

### Table: `weather_searches`
Tracks all weather searches with results and errors.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| ip_address | VARCHAR(45) | IP address (indexed) |
| city | VARCHAR(200) | City searched (indexed) |
| timestamp | DATETIME | Search timestamp (indexed) |
| success | BOOLEAN | Search succeeded |
| error_message | VARCHAR(500) | Error if failed |
| temperature | VARCHAR(10) | Temperature result |
| weather_description | VARCHAR(200) | Weather description |
| user_agent | VARCHAR(500) | Browser/device info |

## Analytics Available

The `/stats` page provides:

1. **Summary Stats**
   - Unique visitors
   - Total visits
   - Total searches
   - Unique cities searched

2. **Top Searched Cities**
   - Cities ranked by search count

3. **Top Visitors**
   - IPs ranked by visit count
   - First and last visit timestamps

4. **Searches by IP**
   - How many searches per IP
   - Unique cities per IP

5. **Recent Searches**
   - Last 20 searches with timestamps
   - Success/failure status
   - Error messages

## Environment Variables

Required (automatically set by Railway):
- `DATABASE_URL` - PostgreSQL connection string

Optional:
- `PORT` - Port number (Railway sets automatically)
- `DEBUG` - Set to `true` for debug mode (default: `false`)

## Troubleshooting

### Database Connection Errors

Check Railway logs for connection issues:
```bash
railway logs
```

### Tables Not Created

Run manual initialization:
```bash
railway run python init_db.py
```

### View Database Contents

Connect to PostgreSQL:
```bash
railway connect postgres
```

Then query:
```sql
SELECT COUNT(*) FROM visitors;
SELECT COUNT(*) FROM weather_searches;
SELECT city, COUNT(*) as count FROM weather_searches GROUP BY city ORDER BY count DESC LIMIT 10;
```

## Local Development

For local development without Railway:

1. Set environment variable:
```bash
export DATABASE_URL=postgresql://user:password@localhost:5432/weather
```

Or let it use SQLite fallback:
```bash
# No DATABASE_URL = uses SQLite (weather.db file)
python weather_app.py
```

2. Initialize database:
```bash
python init_db.py
```

3. Run app:
```bash
python weather_app.py
```
