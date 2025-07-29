#!/usr/bin/env python3
"""
om Mental Health Platform API Server
Secure REST API for om wellness data and functionality
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

class OMAPIServer:
    """Main API server for om platform"""
    
    def __init__(self, host='localhost', port=5000, debug=False):
        if not FLASK_AVAILABLE:
            raise ImportError("Flask is required for API server")
        
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = self._get_or_create_secret_key()
        
        # Enable CORS for web clients
        CORS(self.app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
        
        self.host = host
        self.port = port
        self.debug = debug
        
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
                        error="API key required",
                        message="Provide API key in X-API-Key header or api_key parameter"
                    ))), 401
                
                key_info = self._verify_api_key(api_key)
                if not key_info:
                    return jsonify(asdict(APIResponse(
                        success=False,
                        error="Invalid API key"
                    ))), 401
                
                if permission not in key_info.get("permissions", []):
                    return jsonify(asdict(APIResponse(
                        success=False,
                        error="Insufficient permissions",
                        message=f"Required permission: {permission}"
                    ))), 403
                
                g.api_key_info = key_info
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def _setup_routes(self):
        """Setup all API routes"""
        
        # Health check
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify(asdict(APIResponse(
                success=True,
                data={
                    "status": "healthy",
                    "version": "2.0.0",
                    "timestamp": datetime.datetime.now().isoformat()
                },
                message="om API server is running"
            )))
        
        # API info
        @self.app.route('/api/info', methods=['GET'])
        @self.require_api_key("read")
        def api_info():
            return jsonify(asdict(APIResponse(
                success=True,
                data={
                    "version": "2.0.0",
                    "endpoints": [
                        "/health",
                        "/api/info",
                        "/api/mood/*",
                        "/api/checkin/*",
                        "/api/dashboard/*",
                        "/api/quick/*",
                        "/api/backup/*"
                    ],
                    "authentication": "API key required",
                    "rate_limit": g.api_key_info.get("rate_limit", 1000)
                }
            )))
        
        # Mood API endpoints
        self._setup_mood_routes()
        
        # Check-in API endpoints
        self._setup_checkin_routes()
        
        # Dashboard API endpoints
        self._setup_dashboard_routes()
        
        # Quick actions API endpoints
        self._setup_quick_routes()
        
        # Backup API endpoints
        self._setup_backup_routes()
        
        # Error handlers
        self._setup_error_handlers()
    
    def _setup_mood_routes(self):
        """Setup mood tracking API routes"""
        
        @self.app.route('/api/mood', methods=['GET'])
        @self.require_api_key("read")
        def get_moods():
            try:
                from enhanced_mood_tracking import get_mood_entries, get_mood_analytics
                
                limit = request.args.get('limit', 50, type=int)
                days = request.args.get('days', type=int)
                
                entries = get_mood_entries(limit=limit, days=days)
                
                return jsonify(asdict(APIResponse(
                    success=True,
                    data={
                        "entries": entries,
                        "count": len(entries)
                    },
                    message=f"Retrieved {len(entries)} mood entries"
                )))
            except Exception as e:
                return jsonify(asdict(APIResponse(
                    success=False,
                    error=str(e)
                ))), 500
        
        @self.app.route('/api/mood', methods=['POST'])
        @self.require_api_key("write")
        def add_mood():
            try:
                from enhanced_mood_tracking import add_mood_entry
                
                data = request.get_json()
                if not data or 'mood' not in data:
                    return jsonify(asdict(APIResponse(
                        success=False,
                        error="Mood is required"
                    ))), 400
                
                entry = add_mood_entry(
                    mood=data['mood'],
                    notes=data.get('notes'),
                    intensity=data.get('intensity'),
                    triggers=data.get('triggers'),
                    location=data.get('location')
                )
                
                return jsonify(asdict(APIResponse(
                    success=True,
                    data=entry,
                    message="Mood entry added successfully"
                )))
            except Exception as e:
                return jsonify(asdict(APIResponse(
                    success=False,
                    error=str(e)
                ))), 500
        
        @self.app.route('/api/mood/analytics', methods=['GET'])
        @self.require_api_key("read")
        def mood_analytics():
            try:
                from enhanced_mood_tracking import get_mood_analytics
                
                analytics = get_mood_analytics()
                
                return jsonify(asdict(APIResponse(
                    success=True,
                    data=analytics,
                    message="Mood analytics retrieved"
                )))
            except Exception as e:
                return jsonify(asdict(APIResponse(
                    success=False,
                    error=str(e)
                ))), 500
        
        @self.app.route('/api/mood/suggestions', methods=['GET'])
        @self.require_api_key("read")
        def mood_suggestions():
            try:
                from enhanced_mood_tracking import get_mood_suggestions
                
                count = request.args.get('count', 5, type=int)
                suggestions = get_mood_suggestions(count)
                
                return jsonify(asdict(APIResponse(
                    success=True,
                    data={"suggestions": suggestions},
                    message=f"Retrieved {len(suggestions)} mood suggestions"
                )))
            except Exception as e:
                return jsonify(asdict(APIResponse(
                    success=False,
                    error=str(e)
                ))), 500
    
    def _setup_checkin_routes(self):
        """Setup daily check-in API routes"""
        
        @self.app.route('/api/checkin', methods=['GET'])
        @self.require_api_key("read")
        def get_checkins():
            try:
                from daily_checkin import get_data_dir
                
                checkin_file = get_data_dir() / "daily_checkins.json"
                if not checkin_file.exists():
                    return jsonify(asdict(APIResponse(
                        success=True,
                        data={"checkins": []},
                        message="No check-ins found"
                    )))
                
                with open(checkin_file, 'r') as f:
                    checkins = json.load(f)
                
                limit = request.args.get('limit', 50, type=int)
                days = request.args.get('days', type=int)
                
                if days:
                    cutoff_date = datetime.date.today() - datetime.timedelta(days=days)
                    checkins = [c for c in checkins if 
                              datetime.datetime.fromisoformat(c["date"]).date() >= cutoff_date]
                
                checkins = checkins[:limit]
                
                return jsonify(asdict(APIResponse(
                    success=True,
                    data={
                        "checkins": checkins,
                        "count": len(checkins)
                    },
                    message=f"Retrieved {len(checkins)} check-ins"
                )))
            except Exception as e:
                return jsonify(asdict(APIResponse(
                    success=False,
                    error=str(e)
                ))), 500
        
        @self.app.route('/api/checkin', methods=['POST'])
        @self.require_api_key("write")
        def add_checkin():
            try:
                from daily_checkin import save_checkin_data
                
                data = request.get_json()
                if not data:
                    return jsonify(asdict(APIResponse(
                        success=False,
                        error="Check-in data is required"
                    ))), 400
                
                # Add timestamp if not provided
                if 'date' not in data:
                    data['date'] = datetime.datetime.now().isoformat()
                
                # Add API source
                data['source'] = 'api'
                
                save_checkin_data(data, "daily_checkins.json")
                
                return jsonify(asdict(APIResponse(
                    success=True,
                    data=data,
                    message="Check-in saved successfully"
                )))
            except Exception as e:
                return jsonify(asdict(APIResponse(
                    success=False,
                    error=str(e)
                ))), 500
    
    def _setup_dashboard_routes(self):
        """Setup dashboard API routes"""
        
        @self.app.route('/api/dashboard', methods=['GET'])
        @self.require_api_key("read")
        def get_dashboard():
            try:
                from wellness_dashboard_enhanced import get_wellness_stats
                
                stats = get_wellness_stats()
                
                return jsonify(asdict(APIResponse(
                    success=True,
                    data=stats,
                    message="Dashboard data retrieved"
                )))
            except Exception as e:
                return jsonify(asdict(APIResponse(
                    success=False,
                    error=str(e)
                ))), 500
        
        @self.app.route('/api/dashboard/summary', methods=['GET'])
        @self.require_api_key("read")
        def dashboard_summary():
            try:
                from wellness_dashboard_enhanced import get_wellness_stats
                
                stats = get_wellness_stats()
                
                # Create summary
                summary = {
                    "overall_wellness": stats.get("overall_wellness", {}),
                    "mood_current": stats.get("mood", {}).get("current_mood", "Unknown"),
                    "sessions_today": stats.get("wellness_sessions", {}).get("sessions_today", 0),
                    "achievements_unlocked": stats.get("achievements", {}).get("total_unlocked", 0),
                    "active_goals": stats.get("goals", {}).get("active_goals", 0)
                }
                
                return jsonify(asdict(APIResponse(
                    success=True,
                    data=summary,
                    message="Dashboard summary retrieved"
                )))
            except Exception as e:
                return jsonify(asdict(APIResponse(
                    success=False,
                    error=str(e)
                ))), 500
    
    def _setup_quick_routes(self):
        """Setup quick actions API routes"""
        
        @self.app.route('/api/quick/mood', methods=['POST'])
        @self.require_api_key("write")
        def quick_mood():
            try:
                from enhanced_mood_tracking import add_mood_entry
                
                data = request.get_json() or {}
                mood = data.get('mood')
                
                if not mood:
                    # Get random mood if none provided
                    from enhanced_mood_tracking import get_random_mood
                    mood = get_random_mood()
                
                entry = add_mood_entry(mood, notes="Quick API entry")
                
                return jsonify(asdict(APIResponse(
                    success=True,
                    data=entry,
                    message=f"Quick mood logged: {mood}"
                )))
            except Exception as e:
                return jsonify(asdict(APIResponse(
                    success=False,
                    error=str(e)
                ))), 500
        
        @self.app.route('/api/quick/gratitude', methods=['POST'])
        @self.require_api_key("write")
        def quick_gratitude():
            try:
                from daily_checkin import save_checkin_data
                
                data = request.get_json()
                if not data or 'content' not in data:
                    return jsonify(asdict(APIResponse(
                        success=False,
                        error="Gratitude content is required"
                    ))), 400
                
                gratitude_entry = {
                    "content": data['content'],
                    "date": datetime.datetime.now().isoformat(),
                    "source": "quick_api"
                }
                
                save_checkin_data(gratitude_entry, "gratitude_entries.json")
                
                return jsonify(asdict(APIResponse(
                    success=True,
                    data=gratitude_entry,
                    message="Gratitude entry saved"
                )))
            except Exception as e:
                return jsonify(asdict(APIResponse(
                    success=False,
                    error=str(e)
                ))), 500
    
    def _setup_backup_routes(self):
        """Setup backup API routes"""
        
        @self.app.route('/api/backup', methods=['POST'])
        @self.require_api_key("write")
        def create_backup():
            try:
                from backup_export import create_backup
                
                data = request.get_json() or {}
                backup_name = data.get('name')
                
                backup_path = create_backup(backup_name, auto=True)
                
                if backup_path:
                    return jsonify(asdict(APIResponse(
                        success=True,
                        data={
                            "backup_path": str(backup_path),
                            "backup_name": backup_path.stem
                        },
                        message="Backup created successfully"
                    )))
                else:
                    return jsonify(asdict(APIResponse(
                        success=False,
                        error="Backup creation failed"
                    ))), 500
            except Exception as e:
                return jsonify(asdict(APIResponse(
                    success=False,
                    error=str(e)
                ))), 500
        
        @self.app.route('/api/backup/list', methods=['GET'])
        @self.require_api_key("read")
        def list_backups():
            try:
                from backup_export import get_backup_dir
                
                backup_dir = get_backup_dir()
                backups = []
                
                for backup_file in backup_dir.glob("*.json"):
                    try:
                        with open(backup_file, 'r') as f:
                            backup_data = json.load(f)
                        
                        backups.append({
                            "name": backup_file.stem,
                            "created_at": backup_data.get("created_at", "Unknown"),
                            "version": backup_data.get("version", "Unknown"),
                            "size": backup_file.stat().st_size
                        })
                    except:
                        continue
                
                return jsonify(asdict(APIResponse(
                    success=True,
                    data={"backups": backups},
                    message=f"Found {len(backups)} backups"
                )))
            except Exception as e:
                return jsonify(asdict(APIResponse(
                    success=False,
                    error=str(e)
                ))), 500
    
    def _setup_error_handlers(self):
        """Setup error handlers"""
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify(asdict(APIResponse(
                success=False,
                error="Endpoint not found",
                message="The requested API endpoint does not exist"
            ))), 404
        
        @self.app.errorhandler(405)
        def method_not_allowed(error):
            return jsonify(asdict(APIResponse(
                success=False,
                error="Method not allowed",
                message="The HTTP method is not allowed for this endpoint"
            ))), 405
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify(asdict(APIResponse(
                success=False,
                error="Internal server error",
                message="An unexpected error occurred"
            ))), 500
    
    def run(self):
        """Start the API server"""
        print(f"🚀 Starting om API server on {self.host}:{self.port}")
        print(f"📖 API documentation: http://{self.host}:{self.port}/health")
        print(f"🔑 API key required for all endpoints except /health")
        
        self.app.run(
            host=self.host,
            port=self.port,
            debug=self.debug
        )

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="om Mental Health API Server")
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    if not FLASK_AVAILABLE:
        print("❌ Flask is required to run the API server")
        print("Install with: pip install flask flask-cors pyjwt")
        return
    
    try:
        server = OMAPIServer(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
        server.run()
    except KeyboardInterrupt:
        print("\n👋 API server stopped")
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")

if __name__ == "__main__":
    main()
