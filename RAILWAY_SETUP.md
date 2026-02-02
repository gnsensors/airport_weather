# Railway Deployment Setup with PostgreSQL

## Step-by-Step Deployment Instructions

### 1. Create PostgreSQL Database

In your Railway project:

1. Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway will automatically create a PostgreSQL database
3. Railway will set these environment variables automatically:
   - `DATABASE_URL` - Full PostgreSQL connection string
   - `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`

### 2. Deploy Web Application

The web app container is already configured to:
- Connect to PostgreSQL using `DATABASE_URL` environment variable
- Initialize database tables automatically on startup
- Fall back to SQLite if DATABASE_URL is not set (for local development)

### 3. Container Networking

Railway automatically handles networking between containers:
- The web app and database are in the same private network
- The `DATABASE_URL` variable automatically includes the internal hostname
- No additional networking configuration needed

### 4. Verify Deployment

After deployment:

1. Check deployment logs for:
   ```
   ✅ Database initialized successfully
   [INFO] Listening at: http://0.0.0.0:XXXX
   ```

2. Test the application:
   - Visit your Railway domain
   - Search for a city
   - Go to `/stats` to see analytics

3. Check database:
   - Railway → PostgreSQL → Connect
   - Run: `\dt` to see tables (`visitors`, `weather_searches`)

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
