from flask import Flask, render_template, request
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)

# Free weather API - no key required for basic usage
WEATHER_API_URL = "https://wttr.in/{}?format=j1"
IP_LOG_FILE = "visitor_ips.json"
ACCESS_LOG_FILE = "access.log"

def log_access(ip_address, route, method, user_agent=""):
    """Log all access to a tail-able log file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {ip_address} - {method} {route} - {user_agent}\n"

    with open(ACCESS_LOG_FILE, 'a') as f:
        f.write(log_entry)

    print(log_entry.strip())

def log_ip_address(ip_address):
    """Log unique IP addresses with timestamp"""
    # Load existing data
    if os.path.exists(IP_LOG_FILE):
        with open(IP_LOG_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = {"unique_ips": {}, "total_visits": 0}

    # Update visit count
    data["total_visits"] += 1

    # Add or update IP address
    if ip_address not in data["unique_ips"]:
        data["unique_ips"][ip_address] = {
            "first_visit": datetime.now().isoformat(),
            "last_visit": datetime.now().isoformat(),
            "visit_count": 1
        }
        status = f"[NEW VISITOR] Total unique IPs: {len(data['unique_ips'])}"
    else:
        data["unique_ips"][ip_address]["last_visit"] = datetime.now().isoformat()
        data["unique_ips"][ip_address]["visit_count"] += 1
        status = f"[RETURNING] Visit #{data['unique_ips'][ip_address]['visit_count']}"

    # Save updated data
    with open(IP_LOG_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    return status

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return {'status': 'healthy', 'service': 'airport-weather'}, 200

@app.route('/')
def index():
    # Get client IP address
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        ip = request.remote_addr

    user_agent = request.headers.get('User-Agent', 'Unknown')
    status = log_ip_address(ip)
    log_access(ip, '/', 'GET', user_agent)
    print(f"{ip} - {status}")

    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def get_weather():
    # Get client IP address
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        ip = request.remote_addr

    user_agent = request.headers.get('User-Agent', 'Unknown')
    city = request.form.get('city', 'London')

    status = log_ip_address(ip)
    log_access(ip, f'/weather?city={city}', 'POST', user_agent)
    print(f"{ip} - {status} - Searched: {city}")

    try:
        # Using wttr.in - a free weather service (increased timeout for slow responses)
        response = requests.get(WEATHER_API_URL.format(city), timeout=20)

        if response.status_code == 200:
            data = response.json()
            current = data['current_condition'][0]
            location = data['nearest_area'][0]

            weather_data = {
                'city': f"{location['areaName'][0]['value']}, {location['country'][0]['value']}",
                'temperature': current['temp_C'],
                'feels_like': current['FeelsLikeC'],
                'description': current['weatherDesc'][0]['value'],
                'humidity': current['humidity'],
                'wind_speed': current['windspeedKmph'],
                'wind_dir': current['winddir16Point'],
                'pressure': current['pressure'],
                'visibility': current['visibility']
            }
            return render_template('weather.html', weather=weather_data)
        else:
            error = "Could not fetch weather data. Please try again."
            return render_template('index.html', error=error)

    except Exception as e:
        error = f"Error fetching weather: {str(e)}"
        return render_template('index.html', error=error)

if __name__ == '__main__':
    # Get port from environment variable (Railway/Docker) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Set debug to False in production
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
