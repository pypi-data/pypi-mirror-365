#!/usr/bin/env python3
"""
Enhanced om Mental Health Platform API Server
Integrates SQLAlchemy models and advanced wellness features from logbuch-flask
"""

import os
import json
import datetime
import hashlib
import secrets
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from functools import wraps

try:
    from flask import Flask, request, jsonify, abort, g
    from flask_cors import CORS
    from flask_sqlalchemy import SQLAlchemy
    from flask_migrate import Migrate
    from werkzeug.security import generate_password_hash, check_password_hash
    import jwt
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("⚠️  Flask not available. Install with: pip install flask flask-cors flask-sqlalchemy flask-migrate pyjwt")

# Import our enhanced models and wellness coach
from models import db, User, MoodEntry, CheckinEntry, WellnessSession, WellnessGoal, Achievement, UserAchievement, APIKey
from wellness_coach import WellnessCoach

# Add om modules to path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'modules'))

@dataclass
class APIResponse:
    """Standard API response format"""
    success: bool
    data: Any = None
    message: str = ""
    error: str = ""
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.datetime.now().isoformat()

class EnhancedOMAPIServer:
    """Enhanced API server for om platform with SQLAlchemy integration"""
    
    def __init__(self, host='localhost', port=5000, debug=False):
        if not FLASK_AVAILABLE:
            raise ImportError("Flask is required for API server")
        
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = self._get_or_create_secret_key()
        
        # Database configuration
        self.data_dir = self._get_data_dir()
        db_path = self.data_dir / "om_wellness.db"
        self.app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize database
        db.init_app(self.app)
        self.migrate = Migrate(self.app, db)
        
        # Enable CORS for web clients
        CORS(self.app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
        
        self.host = host
        self.port = port
        self.debug = debug
        
        # Setup routes
        self._setup_routes()
        
        # Initialize database tables and default data
        with self.app.app_context():
            db.create_all()
            self._init_default_achievements()
            self._init_api_keys()
    
    def _get_data_dir(self):
        """Get om data directory"""
        home = Path.home()
        data_dir = home / ".om" / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    
    def _get_or_create_secret_key(self):
        """Get or create secret key for JWT"""
        key_file = self._get_data_dir() / "api" / "secret.key"
        key_file.parent.mkdir(exist_ok=True)
        
        if key_file.exists():
            return key_file.read_text().strip()
        else:
            secret_key = secrets.token_urlsafe(32)
            key_file.write_text(secret_key)
            key_file.chmod(0o600)  # Restrict permissions
            return secret_key
    
    def _init_api_keys(self):
        """Initialize API key system"""
        # Check if we already have API keys
        if APIKey.query.first():
            return
        
        # Create default API key
        default_key = f"om_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(default_key.encode()).hexdigest()
        
        api_key = APIKey(
            key_hash=key_hash,
            name="default",
            description="Default API access",
            permissions=json.dumps(["read", "write"]),
            rate_limit=1000,
            active=True
        )
        
        db.session.add(api_key)
        db.session.commit()
        
        print(f"🔑 Default API key created: {default_key}")
        print("   Store this key securely - it won't be shown again!")
    
    def _init_default_achievements(self):
        """Initialize default achievements"""
        if Achievement.query.first():
            return  # Already initialized
        
        default_achievements = [
            {
                'name': 'First Steps',
                'description': 'Log your first mood entry',
                'icon': '🌱',
                'category': 'getting_started',
                'points': 10,
                'criteria': json.dumps({'mood_entries': 1})
            },
            {
                'name': 'Week Warrior',
                'description': 'Log mood for 7 consecutive days',
                'icon': '🗓️',
                'category': 'consistency',
                'points': 50,
                'criteria': json.dumps({'consecutive_mood_days': 7})
            },
            {
                'name': 'Mindful Moment',
                'description': 'Complete your first wellness session',
                'icon': '🧘',
                'category': 'wellness',
                'points': 15,
                'criteria': json.dumps({'wellness_sessions': 1})
            },
            {
                'name': 'Goal Getter',
                'description': 'Complete your first wellness goal',
                'icon': '🎯',
                'category': 'goals',
                'points': 25,
                'criteria': json.dumps({'completed_goals': 1})
            },
            {
                'name': 'Reflection Master',
                'description': 'Complete 10 check-ins',
                'icon': '📝',
                'category': 'reflection',
                'points': 30,
                'criteria': json.dumps({'checkin_entries': 10})
            }
        ]
        
        for achievement_data in default_achievements:
            achievement = Achievement(**achievement_data)
            db.session.add(achievement)
        
        db.session.commit()
    
    def _verify_api_key(self, api_key):
        """Verify API key and return key info"""
        if not api_key:
            return None
        
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        api_key_obj = APIKey.query.filter_by(key_hash=key_hash, active=True).first()
        
        if api_key_obj:
            # Update last used timestamp
            api_key_obj.last_used = datetime.datetime.utcnow()
            db.session.commit()
            return api_key_obj
        
        return None
    
    def require_api_key(self, permission="read"):
        """Decorator to require API key authentication"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
                
                if not api_key:
                    return jsonify(asdict(APIResponse(
                        success=False,
                        error="Missing API key",
                        message="Provide API key in X-API-Key header or api_key parameter"
                    ))), 401
                
                key_info = self._verify_api_key(api_key)
                if not key_info:
                    return jsonify(asdict(APIResponse(
                        success=False,
                        error="Invalid API key",
                        message="API key is invalid or inactive"
                    ))), 401
                
                if not key_info.has_permission(permission):
                    return jsonify(asdict(APIResponse(
                        success=False,
                        error="Insufficient permissions",
                        message=f"API key lacks '{permission}' permission"
                    ))), 403
                
                g.api_key = key_info
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def _setup_routes(self):
        """Setup all API routes"""
        
        # Health check (no auth required)
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify(asdict(APIResponse(
                success=True,
                data={
                    "status": "healthy",
                    "version": "2.0.0",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "database": "connected"
                },
                message="Enhanced om API server is running"
            )))
        
        # API info
        @self.app.route('/api/info', methods=['GET'])
        @self.require_api_key("read")
        def api_info():
            return jsonify(asdict(APIResponse(
                success=True,
                data={
                    "version": "2.0.0",
                    "features": ["mood_tracking", "checkins", "wellness_sessions", "goals", "achievements", "ai_coach"],
                    "endpoints": ["/health", "/api/mood/*", "/api/checkin/*", "/api/wellness/*", "/api/goals/*", "/api/dashboard/*"],
                    "authentication": "API key required",
                    "database": "SQLAlchemy with SQLite"
                }
            )))
        
        # Mood tracking endpoints
        @self.app.route('/api/mood', methods=['GET'])
        @self.require_api_key("read")
        def get_moods():
            limit = min(int(request.args.get('limit', 50)), 100)
            days = int(request.args.get('days', 30))
            
            start_date = datetime.datetime.now() - datetime.timedelta(days=days)
            
            moods = MoodEntry.query.filter(
                MoodEntry.date >= start_date
            ).order_by(MoodEntry.date.desc()).limit(limit).all()
            
            mood_data = []
            for mood in moods:
                mood_data.append({
                    'id': mood.id,
                    'mood': mood.mood,
                    'mood_display': mood.get_mood_display(),
                    'intensity': mood.intensity,
                    'notes': mood.notes,
                    'triggers': mood.get_triggers_list(),
                    'location': mood.location,
                    'date': mood.date.isoformat(),
                    'timestamp': int(mood.date.timestamp())
                })
            
            return jsonify(asdict(APIResponse(
                success=True,
                data={
                    "entries": mood_data,
                    "count": len(mood_data)
                },
                message=f"Retrieved {len(mood_data)} mood entries"
            )))
        
        @self.app.route('/api/mood', methods=['POST'])
        @self.require_api_key("write")
        def add_mood():
            data = request.get_json()
            
            if not data or 'mood' not in data:
                return jsonify(asdict(APIResponse(
                    success=False,
                    error="Missing required field: mood"
                ))), 400
            
            # Create new mood entry
            mood_entry = MoodEntry(
                mood=data['mood'],
                intensity=data.get('intensity'),
                notes=data.get('notes', ''),
                location=data.get('location'),
                user_id=1  # Default user for now
            )
            
            # Set triggers if provided
            if 'triggers' in data:
                mood_entry.set_triggers_list(data['triggers'])
            
            db.session.add(mood_entry)
            db.session.commit()
            
            return jsonify(asdict(APIResponse(
                success=True,
                data={
                    'id': mood_entry.id,
                    'mood': mood_entry.mood,
                    'mood_display': mood_entry.get_mood_display(),
                    'intensity': mood_entry.intensity,
                    'notes': mood_entry.notes,
                    'triggers': mood_entry.get_triggers_list(),
                    'location': mood_entry.location,
                    'date': mood_entry.date.isoformat(),
                    'timestamp': int(mood_entry.date.timestamp())
                },
                message="Mood entry added successfully"
            )))
        
        # Wellness coach endpoints
        @self.app.route('/api/coach/insights', methods=['GET'])
        @self.require_api_key("read")
        def get_wellness_insights():
            # Get default user (in a real app, this would be from authentication)
            user = User.query.first()
            if not user:
                # Create default user if none exists
                user = User(username="default", email="default@om.local")
                db.session.add(user)
                db.session.commit()
            
            coach = WellnessCoach(user)
            insights = coach.generate_daily_insights()
            
            return jsonify(asdict(APIResponse(
                success=True,
                data=insights,
                message="Generated wellness insights"
            )))
        
        @self.app.route('/api/coach/suggestions', methods=['GET'])
        @self.require_api_key("read")
        def get_activity_suggestions():
            mood = request.args.get('mood')
            available_time = request.args.get('time', type=int)
            
            # Get default user
            user = User.query.first()
            if not user:
                user = User(username="default", email="default@om.local")
                db.session.add(user)
                db.session.commit()
            
            coach = WellnessCoach(user)
            suggestions = coach.suggest_activities(mood=mood, available_time=available_time)
            
            return jsonify(asdict(APIResponse(
                success=True,
                data={"suggestions": suggestions},
                message=f"Generated {len(suggestions)} activity suggestions"
            )))
        
        # Dashboard endpoint
        @self.app.route('/api/dashboard', methods=['GET'])
        @self.require_api_key("read")
        def get_dashboard():
            # Get default user
            user = User.query.first()
            if not user:
                user = User(username="default", email="default@om.local")
                db.session.add(user)
                db.session.commit()
            
            # Get recent data
            recent_moods = MoodEntry.query.filter_by(user_id=user.id).order_by(MoodEntry.date.desc()).limit(7).all()
            recent_checkins = CheckinEntry.query.filter_by(user_id=user.id).order_by(CheckinEntry.date.desc()).limit(7).all()
            recent_sessions = WellnessSession.query.filter_by(user_id=user.id).order_by(WellnessSession.date.desc()).limit(10).all()
            user_achievements = UserAchievement.query.filter_by(user_id=user.id).count()
            
            # Get wellness insights
            coach = WellnessCoach(user)
            insights = coach.generate_daily_insights()
            
            dashboard_data = {
                "today": datetime.datetime.now().strftime("%A, %B %d, %Y"),
                "overall_wellness": {
                    "score": user.get_wellness_score(),
                    "level": "Good" if user.get_wellness_score() > 70 else "Fair" if user.get_wellness_score() > 40 else "Needs Attention",
                    "suggestion": insights['recommendations'][0] if insights['recommendations'] else "Keep up the great work!"
                },
                "mood": {
                    "current_mood": recent_moods[0].mood if recent_moods else None,
                    "trend": insights['patterns_summary'].get('mood_trends', {}).get('trend', 'stable'),
                    "entries_this_week": len(recent_moods),
                    "average_intensity": sum(m.intensity or 5 for m in recent_moods) / len(recent_moods) if recent_moods else 5
                },
                "wellness_sessions": {
                    "sessions_today": len([s for s in recent_sessions if s.date.date() == datetime.date.today()]),
                    "sessions_this_week": len(recent_sessions),
                    "favorite_activity": insights['patterns_summary'].get('favorite_activities', [{}])[0].get('activity', 'breathing') if insights['patterns_summary'].get('favorite_activities') else 'breathing'
                },
                "achievements": {
                    "total_unlocked": user_achievements,
                    "completion_rate": (user_achievements / Achievement.query.count() * 100) if Achievement.query.count() > 0 else 0
                },
                "insights": insights['insights'],
                "recommendations": insights['recommendations']
            }
            
            return jsonify(asdict(APIResponse(
                success=True,
                data=dashboard_data,
                message="Dashboard data retrieved successfully"
            )))
    
    def run(self):
        """Start the API server"""
        print(f"🚀 Starting Enhanced om API Server...")
        print(f"   Host: {self.host}")
        print(f"   Port: {self.port}")
        print(f"   Debug: {self.debug}")
        print(f"   Database: {self.app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"   Health check: http://{self.host}:{self.port}/health")
        print()
        
        self.app.run(host=self.host, port=self.port, debug=self.debug)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced om Mental Health Platform API Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    try:
        server = EnhancedOMAPIServer(host=args.host, port=args.port, debug=args.debug)
        server.run()
    except KeyboardInterrupt:
        print("\n👋 Shutting down Enhanced om API Server...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
