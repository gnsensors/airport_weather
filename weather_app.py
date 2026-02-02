from flask import Flask, render_template, request
import requests
from datetime import datetime
import os
from models import init_db, get_session, Visitor, WeatherSearch
from sqlalchemy import func, distinct
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)

# Free weather API - no key required for basic usage
WEATHER_API_URL = "https://wttr.in/{}?format=j1"

# Initialize database on startup
try:
    init_db()
    print("✅ Database initialized successfully")
except Exception as e:
    print(f"⚠️  Database initialization warning: {e}")
    print("   App will continue but database features may not work")


def get_client_ip():
    """Extract client IP from request"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr


def log_visitor(ip_address, user_agent):
    """Log visitor to database"""
    try:
        session = get_session()
        visitor = session.query(Visitor).filter_by(ip_address=ip_address).first()

        if visitor:
            visitor.visit_count += 1
            visitor.last_visit = datetime.utcnow()
            visitor.user_agent = user_agent
            status = f"[RETURNING] Visit #{visitor.visit_count}"
        else:
            visitor = Visitor(
                ip_address=ip_address,
                user_agent=user_agent,
                visit_count=1
            )
            session.add(visitor)
            status = f"[NEW VISITOR]"

        session.commit()
        session.close()
        return status
    except SQLAlchemyError as e:
        print(f"Database error logging visitor: {e}")
        return "[ERROR]"


def log_search(ip_address, city, success, error_msg=None, temp=None, description=None, user_agent=None):
    """Log weather search to database"""
    try:
        session = get_session()
        search = WeatherSearch(
            ip_address=ip_address,
            city=city,
            success=success,
            error_message=error_msg,
            temperature=temp,
            weather_description=description,
            user_agent=user_agent
        )
        session.add(search)
        session.commit()
        session.close()
    except SQLAlchemyError as e:
        print(f"Database error logging search: {e}")


@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return {'status': 'healthy', 'service': 'airport-weather'}, 200


@app.route('/')
def index():
    """Home page"""
    ip = get_client_ip()
    user_agent = request.headers.get('User-Agent', 'Unknown')

    status = log_visitor(ip, user_agent)
    print(f"{ip} - {status}")

    return render_template('index.html')


@app.route('/stats')
def stats():
    """Statistics page showing visitor and search analytics"""
    try:
        session = get_session()

        # Get total visitors and visits
        total_visitors = session.query(Visitor).count()
        total_visits = session.query(func.sum(Visitor.visit_count)).scalar() or 0

        # Get top 10 visitors by request count
        top_visitors = session.query(
            Visitor.ip_address,
            Visitor.visit_count,
            Visitor.first_visit,
            Visitor.last_visit
        ).order_by(Visitor.visit_count.desc()).limit(10).all()

        # Get total searches
        total_searches = session.query(WeatherSearch).count()
        successful_searches = session.query(WeatherSearch).filter_by(success=True).count()
        failed_searches = total_searches - successful_searches

        # Get unique cities searched
        unique_cities = session.query(distinct(WeatherSearch.city)).count()

        # Get top 10 searched cities
        top_cities = session.query(
            WeatherSearch.city,
            func.count(WeatherSearch.id).label('search_count')
        ).group_by(WeatherSearch.city).order_by(func.count(WeatherSearch.id).desc()).limit(10).all()

        # Get recent searches (last 20)
        recent_searches = session.query(
            WeatherSearch.ip_address,
            WeatherSearch.city,
            WeatherSearch.timestamp,
            WeatherSearch.success,
            WeatherSearch.error_message
        ).order_by(WeatherSearch.timestamp.desc()).limit(20).all()

        # Get searches by IP (top 10 IPs with most searches)
        searches_by_ip = session.query(
            WeatherSearch.ip_address,
            func.count(WeatherSearch.id).label('search_count'),
            func.count(distinct(WeatherSearch.city)).label('unique_cities')
        ).group_by(WeatherSearch.ip_address).order_by(func.count(WeatherSearch.id).desc()).limit(10).all()

        session.close()

        stats_data = {
            'total_visitors': total_visitors,
            'total_visits': total_visits,
            'total_searches': total_searches,
            'successful_searches': successful_searches,
            'failed_searches': failed_searches,
            'unique_cities': unique_cities,
            'top_visitors': top_visitors,
            'top_cities': top_cities,
            'recent_searches': recent_searches,
            'searches_by_ip': searches_by_ip
        }

        return render_template('stats.html', stats=stats_data)

    except Exception as e:
        print(f"Error fetching stats: {e}")
        return render_template('stats.html', error=str(e))


@app.route('/weather', methods=['POST'])
def get_weather():
    """Handle weather search requests"""
    ip = get_client_ip()
    user_agent = request.headers.get('User-Agent', 'Unknown')
    city = request.form.get('city', 'London')

    status = log_visitor(ip, user_agent)
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

            # Log successful search
            log_search(
                ip_address=ip,
                city=city,
                success=True,
                temp=f"{current['temp_C']}°C",
                description=current['weatherDesc'][0]['value'],
                user_agent=user_agent
            )

            return render_template('weather.html', weather=weather_data)
        else:
            error = "Could not fetch weather data. Please try again."

            # Log failed search
            log_search(
                ip_address=ip,
                city=city,
                success=False,
                error_msg=f"API returned status {response.status_code}",
                user_agent=user_agent
            )

            return render_template('index.html', error=error)

    except Exception as e:
        error = f"Error fetching weather: {str(e)}"

        # Log failed search
        log_search(
            ip_address=ip,
            city=city,
            success=False,
            error_msg=str(e),
            user_agent=user_agent
        )

        return render_template('index.html', error=error)


if __name__ == '__main__':
    # Get port from environment variable (Railway/Docker) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Set debug to False in production
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
