#!/usr/bin/env python3
"""
SQLite-powered om Mental Health Platform API Server
Integrates the SQLite storage system with the om API
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
    from werkzeug.security import generate_password_hash, check_password_hash
    import jwt
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("⚠️  Flask not available. Install with: pip install flask flask-cors pyjwt")

from sqlite_storage import OMSQLiteStorage

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

class SQLiteOMAPIServer:
    """SQLite-powered API server for om platform"""
    
    def __init__(self, host='localhost', port=5000, debug=False, db_path=None):
        if not FLASK_AVAILABLE:
            raise ImportError("Flask is required for API server")
        
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = self._get_or_create_secret_key()
        
        # Enable CORS for web clients
        CORS(self.app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
        
        self.host = host
        self.port = port
        self.debug = debug
        
        # Initialize SQLite storage
        self.storage = OMSQLiteStorage(db_path)
        
        # Initialize data directory
        self.data_dir = self._get_data_dir()
        self.api_dir = self.data_dir / "api"
        self.api_dir.mkdir(exist_ok=True)
        
        # Setup routes
        self._setup_routes()
        
        # Initialize API keys
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
        api_keys_file = self.api_dir / "api_keys.json"
        if not api_keys_file.exists():
            # Create default API key
            default_key = self._generate_api_key("default", "Default API access")
            api_keys = {
                "keys": {
                    default_key["key"]: {
                        "name": default_key["name"],
                        "description": default_key["description"],
                        "created_at": default_key["created_at"],
                        "permissions": ["read", "write"],
                        "rate_limit": 1000,  # requests per hour
                        "active": True
                    }
                }
            }
            with open(api_keys_file, 'w') as f:
                json.dump(api_keys, f, indent=2)
            
            print(f"🔑 Default API key created: {default_key['key']}")
            print("   Store this key securely - it won't be shown again!")
    
    def _generate_api_key(self, name, description):
        """Generate new API key"""
        key = f"om_{secrets.token_urlsafe(32)}"
        return {
            "key": key,
            "name": name,
            "description": description,
            "created_at": datetime.datetime.now().isoformat()
        }
    
    def _verify_api_key(self, api_key):
        """Verify API key and return permissions"""
        api_keys_file = self.api_dir / "api_keys.json"
        if not api_keys_file.exists():
            return None
        
        try:
            with open(api_keys_file, 'r') as f:
                api_keys = json.load(f)
            
            key_info = api_keys.get("keys", {}).get(api_key)
            if key_info and key_info.get("active", False):
                return key_info
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        
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
                
                if permission not in key_info.get("permissions", []):
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
            stats = self.storage.get_database_stats()
            return jsonify(asdict(APIResponse(
                success=True,
                data={
                    "status": "healthy",
                    "version": "2.0.0",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "storage": "SQLite",
                    "database_size_mb": stats.get('database_size_mb', 0),
                    "total_entries": sum(v for k, v in stats.items() if k.endswith('_entries'))
                },
                message="SQLite om API server is running"
            )))
        
        # API info
        @self.app.route('/api/info', methods=['GET'])
        @self.require_api_key("read")
        def api_info():
            stats = self.storage.get_database_stats()
            return jsonify(asdict(APIResponse(
                success=True,
                data={
                    "version": "2.0.0",
                    "storage": "SQLite",
                    "features": ["mood_tracking", "checkins", "wellness_sessions", "goals", "achievements", "analytics"],
                    "endpoints": ["/health", "/api/mood/*", "/api/checkin/*", "/api/wellness/*", "/api/goals/*", "/api/dashboard/*"],
                    "authentication": "API key required",
                    "database_stats": stats
                }
            )))
        
        # Mood tracking endpoints
        @self.app.route('/api/mood', methods=['GET'])
        @self.require_api_key("read")
        def get_moods():
            limit = min(int(request.args.get('limit', 50)), 100)
            days = int(request.args.get('days', 30)) if request.args.get('days') else None
            
            moods = self.storage.get_mood_entries(limit=limit, days=days)
            
            # Format for API response
            mood_data = []
            for mood in moods:
                mood_data.append({
                    'id': mood['id'],
                    'mood': mood['mood'],
                    'intensity': mood['intensity'],
                    'notes': mood['notes'],
                    'triggers': mood['triggers'],
                    'location': mood['location'],
                    'energy_level': mood['energy_level'],
                    'stress_level': mood['stress_level'],
                    'date': mood['date'],
                    'timestamp': int(datetime.datetime.fromisoformat(mood['date']).timestamp())
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
            
            # Add mood entry
            entry_id = self.storage.add_mood_entry(
                mood=data['mood'],
                intensity=data.get('intensity'),
                notes=data.get('notes', ''),
                triggers=data.get('triggers'),
                location=data.get('location'),
                energy_level=data.get('energy_level'),
                stress_level=data.get('stress_level')
            )
            
            # Get the created entry
            entries = self.storage.get_mood_entries(limit=1)
            if entries:
                entry = entries[0]
                return jsonify(asdict(APIResponse(
                    success=True,
                    data={
                        'id': entry['id'],
                        'mood': entry['mood'],
                        'intensity': entry['intensity'],
                        'notes': entry['notes'],
                        'triggers': entry['triggers'],
                        'location': entry['location'],
                        'energy_level': entry['energy_level'],
                        'stress_level': entry['stress_level'],
                        'date': entry['date'],
                        'timestamp': int(datetime.datetime.fromisoformat(entry['date']).timestamp())
                    },
                    message="Mood entry added successfully"
                )))
            
            return jsonify(asdict(APIResponse(
                success=True,
                data={"id": entry_id},
                message="Mood entry added successfully"
            )))
        
        @self.app.route('/api/mood/analytics', methods=['GET'])
        @self.require_api_key("read")
        def get_mood_analytics():
            days = int(request.args.get('days', 30))
            analytics = self.storage.get_mood_analytics(days=days)
            
            return jsonify(asdict(APIResponse(
                success=True,
                data=analytics,
                message="Mood analytics retrieved successfully"
            )))
        
        # Check-in endpoints
        @self.app.route('/api/checkin', methods=['GET'])
        @self.require_api_key("read")
        def get_checkins():
            limit = min(int(request.args.get('limit', 30)), 100)
            days = int(request.args.get('days', 7)) if request.args.get('days') else None
            
            checkins = self.storage.get_checkin_entries(limit=limit, days=days)
            
            return jsonify(asdict(APIResponse(
                success=True,
                data={
                    "checkins": checkins,
                    "count": len(checkins)
                },
                message=f"Retrieved {len(checkins)} check-in entries"
            )))
        
        @self.app.route('/api/checkin', methods=['POST'])
        @self.require_api_key("write")
        def add_checkin():
            data = request.get_json()
            
            if not data:
                return jsonify(asdict(APIResponse(
                    success=False,
                    error="Missing check-in data"
                ))), 400
            
            entry_id = self.storage.add_checkin_entry(data)
            
            return jsonify(asdict(APIResponse(
                success=True,
                data={"id": entry_id},
                message="Check-in entry added successfully"
            )))
        
        # Wellness session endpoints
        @self.app.route('/api/wellness/sessions', methods=['GET'])
        @self.require_api_key("read")
        def get_wellness_sessions():
            limit = min(int(request.args.get('limit', 50)), 100)
            days = int(request.args.get('days', 30)) if request.args.get('days') else None
            
            sessions = self.storage.get_wellness_sessions(limit=limit, days=days)
            
            return jsonify(asdict(APIResponse(
                success=True,
                data={
                    "sessions": sessions,
                    "count": len(sessions)
                },
                message=f"Retrieved {len(sessions)} wellness sessions"
            )))
        
        @self.app.route('/api/wellness/sessions', methods=['POST'])
        @self.require_api_key("write")
        def add_wellness_session():
            data = request.get_json()
            
            if not data or 'activity_type' not in data:
                return jsonify(asdict(APIResponse(
                    success=False,
                    error="Missing required field: activity_type"
                ))), 400
            
            session_id = self.storage.add_wellness_session(
                activity_type=data['activity_type'],
                duration_minutes=data.get('duration_minutes'),
                notes=data.get('notes', ''),
                rating=data.get('rating'),
                mood_before=data.get('mood_before'),
                mood_after=data.get('mood_after')
            )
            
            return jsonify(asdict(APIResponse(
                success=True,
                data={"id": session_id},
                message="Wellness session added successfully"
            )))
        
        # Goals endpoints
        @self.app.route('/api/goals', methods=['GET'])
        @self.require_api_key("read")
        def get_goals():
            active_only = request.args.get('active_only', 'false').lower() == 'true'
            goals = self.storage.get_wellness_goals(active_only=active_only)
            
            return jsonify(asdict(APIResponse(
                success=True,
                data={
                    "goals": goals,
                    "count": len(goals)
                },
                message=f"Retrieved {len(goals)} wellness goals"
            )))
        
        @self.app.route('/api/goals', methods=['POST'])
        @self.require_api_key("write")
        def add_goal():
            data = request.get_json()
            
            if not data or 'title' not in data:
                return jsonify(asdict(APIResponse(
                    success=False,
                    error="Missing required field: title"
                ))), 400
            
            goal_id = self.storage.add_wellness_goal(
                title=data['title'],
                description=data.get('description', ''),
                category=data.get('category', 'general'),
                target_value=data.get('target_value', 1),
                unit=data.get('unit', 'times'),
                target_date=data.get('target_date'),
                priority=data.get('priority', 'medium')
            )
            
            return jsonify(asdict(APIResponse(
                success=True,
                data={"id": goal_id},
                message="Wellness goal added successfully"
            )))
        
        @self.app.route('/api/goals/<goal_id>/progress', methods=['POST'])
        @self.require_api_key("write")
        def update_goal_progress(goal_id):
            data = request.get_json() or {}
            increment = data.get('increment', 1)
            
            success = self.storage.update_goal_progress(goal_id, increment)
            
            if success:
                return jsonify(asdict(APIResponse(
                    success=True,
                    message="Goal progress updated successfully"
                )))
            else:
                return jsonify(asdict(APIResponse(
                    success=False,
                    error="Goal not found"
                ))), 404
        
        # Achievements endpoints
        @self.app.route('/api/achievements', methods=['GET'])
        @self.require_api_key("read")
        def get_achievements():
            achievements = self.storage.get_user_achievements()
            
            return jsonify(asdict(APIResponse(
                success=True,
                data={
                    "achievements": achievements,
                    "count": len(achievements)
                },
                message=f"Retrieved {len(achievements)} unlocked achievements"
            )))
        
        # Dashboard endpoint
        @self.app.route('/api/dashboard', methods=['GET'])
        @self.require_api_key("read")
        def get_dashboard():
            dashboard_data = self.storage.get_dashboard_data()
            
            # Format dashboard response
            formatted_data = {
                "today": datetime.datetime.now().strftime("%A, %B %d, %Y"),
                "overall_wellness": {
                    "score": dashboard_data['wellness_score'],
                    "level": self._get_wellness_level(dashboard_data['wellness_score']),
                    "trend": dashboard_data['mood_trend']
                },
                "mood": {
                    "current_mood": dashboard_data['recent_moods'][0]['mood'] if dashboard_data['recent_moods'] else None,
                    "trend": dashboard_data['mood_trend'],
                    "entries_this_week": len([m for m in dashboard_data['recent_moods'] if self._is_this_week(m['date'])]),
                    "average_intensity": self._calculate_avg_intensity(dashboard_data['recent_moods'])
                },
                "wellness_sessions": {
                    "sessions_today": len([s for s in dashboard_data['recent_sessions'] if self._is_today(s['date'])]),
                    "sessions_this_week": len(dashboard_data['recent_sessions']),
                    "favorite_activity": dashboard_data['session_stats']['favorite_activity']
                },
                "achievements": {
                    "total_unlocked": dashboard_data['achievement_count'],
                    "completion_rate": self._calculate_achievement_completion_rate(dashboard_data['achievement_count'])
                },
                "active_goals": len(dashboard_data['active_goals']),
                "goal_progress": self._calculate_avg_goal_progress(dashboard_data['active_goals'])
            }
            
            return jsonify(asdict(APIResponse(
                success=True,
                data=formatted_data,
                message="Dashboard data retrieved successfully"
            )))
        
        # Quick actions endpoints
        @self.app.route('/api/quick/mood', methods=['POST'])
        @self.require_api_key("write")
        def quick_mood_log():
            data = request.get_json() or {}
            mood = data.get('mood', 'content')  # Default mood
            
            entry_id = self.storage.add_mood_entry(mood=mood, notes="Quick mood log")
            self.storage.log_quick_action('mood_log', {'mood': mood, 'entry_id': entry_id})
            
            return jsonify(asdict(APIResponse(
                success=True,
                data={"id": entry_id, "mood": mood},
                message=f"Quick mood logged: {mood}"
            )))
        
        @self.app.route('/api/quick/gratitude', methods=['POST'])
        @self.require_api_key("write")
        def quick_gratitude():
            data = request.get_json()
            
            if not data or 'content' not in data:
                return jsonify(asdict(APIResponse(
                    success=False,
                    error="Missing required field: content"
                ))), 400
            
            action_id = self.storage.log_quick_action('gratitude', {'content': data['content']})
            
            return jsonify(asdict(APIResponse(
                success=True,
                data={"id": action_id},
                message="Gratitude entry added successfully"
            )))
        
        # Backup endpoints
        @self.app.route('/api/backup', methods=['POST'])
        @self.require_api_key("write")
        def create_backup():
            data = request.get_json() or {}
            backup_name = data.get('name')
            
            backup_path = self.storage.create_backup(backup_name)
            
            return jsonify(asdict(APIResponse(
                success=True,
                data={
                    "backup_path": backup_path,
                    "backup_name": backup_name or Path(backup_path).stem
                },
                message="Backup created successfully"
            )))
        
        @self.app.route('/api/stats', methods=['GET'])
        @self.require_api_key("read")
        def get_stats():
            stats = self.storage.get_database_stats()
            
            return jsonify(asdict(APIResponse(
                success=True,
                data=stats,
                message="Database statistics retrieved successfully"
            )))
    
    def _get_wellness_level(self, score: float) -> str:
        """Convert wellness score to level"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Needs Attention"
    
    def _is_today(self, date_str: str) -> bool:
        """Check if date is today"""
        try:
            date = datetime.datetime.fromisoformat(date_str).date()
            return date == datetime.date.today()
        except:
            return False
    
    def _is_this_week(self, date_str: str) -> bool:
        """Check if date is within this week"""
        try:
            date = datetime.datetime.fromisoformat(date_str).date()
            today = datetime.date.today()
            week_start = today - datetime.timedelta(days=today.weekday())
            return date >= week_start
        except:
            return False
    
    def _calculate_avg_intensity(self, moods: List[Dict]) -> float:
        """Calculate average mood intensity"""
        intensities = [m['intensity'] for m in moods if m.get('intensity')]
        return sum(intensities) / len(intensities) if intensities else 5.0
    
    def _calculate_achievement_completion_rate(self, unlocked_count: int) -> float:
        """Calculate achievement completion rate"""
        # Assuming 6 default achievements for now
        total_achievements = 6
        return (unlocked_count / total_achievements) * 100 if total_achievements > 0 else 0
    
    def _calculate_avg_goal_progress(self, goals: List[Dict]) -> float:
        """Calculate average goal progress"""
        if not goals:
            return 0
        
        total_progress = sum(
            (goal['current_value'] / goal['target_value'] * 100) if goal['target_value'] > 0 else 0
            for goal in goals
        )
        return total_progress / len(goals)
    
    def run(self):
        """Start the API server"""
        print(f"🚀 Starting SQLite om API Server...")
        print(f"   Host: {self.host}")
        print(f"   Port: {self.port}")
        print(f"   Debug: {self.debug}")
        print(f"   Database: {self.storage.db_path}")
        print(f"   Health check: http://{self.host}:{self.port}/health")
        
        # Show database stats
        stats = self.storage.get_database_stats()
        print(f"   Database size: {stats.get('database_size_mb', 0):.2f} MB")
        print(f"   Total entries: {sum(v for k, v in stats.items() if k.endswith('_entries'))}")
        print()
        
        self.app.run(host=self.host, port=self.port, debug=self.debug)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SQLite om Mental Health Platform API Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--db-path', help='Custom database path')
    
    args = parser.parse_args()
    
    try:
        server = SQLiteOMAPIServer(
            host=args.host, 
            port=args.port, 
            debug=args.debug,
            db_path=args.db_path
        )
        server.run()
    except KeyboardInterrupt:
        print("\n👋 Shutting down SQLite om API Server...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
