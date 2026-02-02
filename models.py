from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Visitor(Base):
    """Track unique IP addresses and visit counts"""
    __tablename__ = 'visitors'

    id = Column(Integer, primary_key=True)
    ip_address = Column(String(45), unique=True, nullable=False, index=True)
    first_visit = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_visit = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    visit_count = Column(Integer, default=1, nullable=False)
    user_agent = Column(String(500))

    def __repr__(self):
        return f"<Visitor(ip={self.ip_address}, visits={self.visit_count})>"


class WeatherSearch(Base):
    """Track all weather searches with IP, city, and results"""
    __tablename__ = 'weather_searches'

    id = Column(Integer, primary_key=True)
    ip_address = Column(String(45), nullable=False, index=True)
    city = Column(String(200), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    success = Column(Boolean, default=True, nullable=False)
    error_message = Column(String(500))
    temperature = Column(String(10))
    weather_description = Column(String(200))
    user_agent = Column(String(500))

    def __repr__(self):
        return f"<WeatherSearch(ip={self.ip_address}, city={self.city}, success={self.success})>"


# Database connection
def get_database_url():
    """Get database URL from environment or use SQLite fallback"""
    return os.environ.get('DATABASE_URL', 'sqlite:///weather.db')


def init_db():
    """Initialize database and create tables"""
    database_url = get_database_url()

    # Railway uses postgres:// but SQLAlchemy needs postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Get database session"""
    database_url = get_database_url()

    # Railway uses postgres:// but SQLAlchemy needs postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    engine = create_engine(database_url, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    return Session()
