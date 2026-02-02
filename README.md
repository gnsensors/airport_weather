# Airport Weather App 🌤️

A simple Flask web application that displays real-time weather information for any city worldwide.

## Features

- 🌍 Search weather for any city in the world
- 📊 Displays comprehensive weather data:
  - Current temperature and "feels like" temperature
  - Weather description (Sunny, Cloudy, Rainy, etc.)
  - Humidity percentage
  - Wind speed and direction
  - Atmospheric pressure
  - Visibility distance
- 🎨 Modern, responsive UI with gradient design
- ⏳ Loading spinner for better user experience
- 📝 Access logging for monitoring visitors
- 🔍 Unique IP address tracking

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd airport_weather
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Flask application:
```bash
python weather_app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Enter a city name and click "Get Weather" to see current weather information.

## Docker Deployment

### Build and Run with Docker

1. Build the Docker image:
```bash
docker build -t airport-weather .
```

2. Run the container:
```bash
docker run -p 5000:5000 airport-weather
```

3. Access at `http://localhost:5000`

### Deploy to Railway.com

1. Push your code to GitHub (already done!)
2. Go to [Railway.app](https://railway.app) and sign in
3. Click "New Project" → "Deploy from GitHub repo"
4. Select `gnsensors/airport_weather`
5. Railway will automatically detect the Dockerfile and deploy
6. Your app will be live at a Railway-provided URL!

**Railway Environment Variables** (optional):
- `PORT` - Automatically set by Railway
- `DEBUG` - Set to `true` for debug mode (default: `false`)

## Monitoring

The app creates two log files:

- **access.log** - Records all HTTP requests with timestamps, IP addresses, and user agents
- **visitor_ips.json** - Tracks unique visitors with visit counts and timestamps

To monitor access in real-time:
```bash
tail -f access.log
```

## API

This app uses the [wttr.in](https://wttr.in) free weather API - no API key required!

## Technologies

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **API**: wttr.in Weather Service
- **Logging**: Custom access logging with IP tracking

## Configuration

- Default port: `5000`
- Default host: `0.0.0.0` (accessible on local network)
- API timeout: `20 seconds`

## License

MIT License - feel free to use and modify as needed!

## Author

Created with Claude Code
