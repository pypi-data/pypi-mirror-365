#!/usr/bin/env python3
"""
Database initialization script for Enhanced om API
Sets up SQLAlchemy database with initial data
"""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, User, Achievement
from enhanced_server import EnhancedOMAPIServer
import json

def init_database():
    """Initialize the database with tables and default data"""
    print("🗄️  Initializing Enhanced om API Database...")
    
    # Create server instance to set up Flask app
    server = EnhancedOMAPIServer()
    
    with server.app.app_context():
        print("   Creating database tables...")
        db.create_all()
        
        print("   Setting up default user...")
        # Create default user if it doesn't exist
        default_user = User.query.filter_by(username="default").first()
        if not default_user:
            default_user = User(
                username="default",
                email="default@om.local",
                timezone="UTC",
                wellness_goals=json.dumps([
                    {"title": "Daily Mood Check", "target": 30, "unit": "days"},
                    {"title": "Weekly Wellness Sessions", "target": 7, "unit": "sessions"}
                ]),
                notification_preferences=json.dumps({
                    "daily_reminders": True,
                    "achievement_notifications": True,
                    "wellness_insights": True
                })
            )
            db.session.add(default_user)
        
        print("   Setting up achievements...")
        # Achievements are already set up in the server initialization
        achievement_count = Achievement.query.count()
        print(f"   ✅ {achievement_count} achievements available")
        
        db.session.commit()
        
        print("   Database initialization complete!")
        print(f"   Database location: {server.app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Print some stats
        user_count = User.query.count()
        print(f"   👥 Users: {user_count}")
        print(f"   🏆 Achievements: {achievement_count}")

def reset_database():
    """Reset the database (WARNING: This will delete all data!)"""
    print("⚠️  RESETTING DATABASE - ALL DATA WILL BE LOST!")
    response = input("Are you sure? Type 'yes' to continue: ")
    
    if response.lower() != 'yes':
        print("Database reset cancelled.")
        return
    
    server = EnhancedOMAPIServer()
    
    with server.app.app_context():
        print("   Dropping all tables...")
        db.drop_all()
        
        print("   Recreating tables...")
        db.create_all()
        
        print("   Reinitializing default data...")
        server._init_default_achievements()
        
        print("   Database reset complete!")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced om API Database Management')
    parser.add_argument('--reset', action='store_true', help='Reset database (WARNING: Deletes all data)')
    
    args = parser.parse_args()
    
    try:
        if args.reset:
            reset_database()
        else:
            init_database()
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
