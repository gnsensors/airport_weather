#!/usr/bin/env python3
"""
Database initialization script for Airport Weather app.
This creates all tables in the PostgreSQL database.
"""

from models import init_db
import sys

if __name__ == '__main__':
    try:
        print("Initializing database...")
        engine = init_db()
        print("✅ Database tables created successfully!")
        print(f"   Connected to: {engine.url}")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)
