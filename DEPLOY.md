# Railway Deployment - Quick Start

## Automatic Deployment from GitHub

Railway will automatically build and deploy this application when you push to GitHub.

## Required Services

This project needs **2 services** in Railway:

### 1. Web Application (from GitHub)
- **Already linked**: This repository
- **Builds from**: Dockerfile
- **Exposes**: Public domain
- **Environment**: Production

### 2. PostgreSQL Database
**YOU MUST ADD THIS MANUALLY**

```bash
# Via CLI
railway add --database postgres

# Or via Dashboard:
# Railway → Your Project → "+ New" → "Database" → "Add PostgreSQL"
```

## How It Works

```
GitHub Push → Railway Detects → Builds Docker → Deploys
                ↓
         Sets DATABASE_URL automatically
                ↓
         App connects to PostgreSQL
                ↓
         Tables auto-created
                ↓
         Live at your Railway domain!
```

## Deployment Steps

### Step 1: Add PostgreSQL (ONE TIME ONLY)

**Option A: Railway Dashboard**
1. Go to https://railway.app
2. Open project: "desirable-beauty"
3. Click "+ New" → "Database" → "Add PostgreSQL"
4. Done! (Railway auto-connects everything)

**Option B: Railway CLI**
```bash
cd /home/geofnoakes/code/airport_weather
railway add --database postgres
```

### Step 2: Verify Services

You should see TWO services:
```
Your Project
├── 🌐 airport_weather (from GitHub)
└── 🗄️  postgres (database)
```

### Step 3: Check Deployment

```bash
railway logs
```

Look for:
```
✅ Database initialized successfully
Connected to: postgresql://...
[INFO] Listening at: http://0.0.0.0:XXXX
```

### Step 4: Access Your App

- **Main app**: `https://airportweather-production.up.railway.app`
- **Stats page**: `https://airportweather-production.up.railway.app/stats`
- **Health check**: `https://airportweather-production.up.railway.app/health`

## Environment Variables (Automatic)

Railway automatically sets:
- `PORT` - Assigned dynamically
- `DATABASE_URL` - PostgreSQL connection string

No manual configuration needed!

## Future Deployments

After initial setup, just push to GitHub:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

Railway automatically:
1. Detects the push
2. Builds new Docker image
3. Deploys with zero downtime
4. Keeps DATABASE_URL connected

## Database Access

Connect to PostgreSQL:
```bash
railway connect postgres
```

See [DATABASE_ACCESS.md](DATABASE_ACCESS.md) for full guide.

## Troubleshooting

### "Database connection error"
→ Make sure PostgreSQL service is added (see Step 1)

### "Service postgres not found"
→ Add PostgreSQL: `railway add --database postgres`

### "Tables don't exist"
→ App auto-creates tables on startup. Check logs: `railway logs`

### "Can't see stats"
→ Visit `/stats` after PostgreSQL is added and app restarts

## Files Used by Railway

- `Dockerfile` - Builds the container
- `railway.json` - Deployment configuration
- `railway.toml` - Service settings
- `requirements.txt` - Python dependencies

All configured and ready to go! 🚀
