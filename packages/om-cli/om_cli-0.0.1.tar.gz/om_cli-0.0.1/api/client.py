#!/usr/bin/env python3
"""
om Mental Health Platform API Client
Python client library for interacting with om API
"""

import json
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  requests not available. Install with: pip install requests")

@dataclass
class OMAPIResponse:
    """API response wrapper"""
    success: bool
    data: Any = None
    message: str = ""
    error: str = ""
    timestamp: str = ""
    status_code: int = 200

class OMAPIClient:
    """Python client for om Mental Health API"""
    
    def __init__(self, base_url: str = "http://localhost:5000", api_key: str = None):
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library is required")
        
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'X-API-Key': api_key})
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> OMAPIResponse:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30
            )
            
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"success": False, "error": "Invalid JSON response"}
            
            return OMAPIResponse(
                success=response_data.get("success", False),
                data=response_data.get("data"),
                message=response_data.get("message", ""),
                error=response_data.get("error", ""),
                timestamp=response_data.get("timestamp", ""),
                status_code=response.status_code
            )
            
        except requests.exceptions.RequestException as e:
            return OMAPIResponse(
                success=False,
                error=f"Request failed: {str(e)}",
                status_code=500
            )
    
    def health_check(self) -> OMAPIResponse:
        """Check API server health"""
        return self._make_request("GET", "/health")
    
    def get_api_info(self) -> OMAPIResponse:
        """Get API information"""
        return self._make_request("GET", "/api/info")
    
    # Mood API methods
    def get_moods(self, limit: int = 50, days: int = None) -> OMAPIResponse:
        """Get mood entries"""
        params = {"limit": limit}
        if days:
            params["days"] = days
        return self._make_request("GET", "/api/mood", params=params)
    
    def add_mood(self, mood: str, notes: str = None, intensity: int = None, 
                 triggers: List[str] = None, location: str = None) -> OMAPIResponse:
        """Add mood entry"""
        data = {"mood": mood}
        if notes:
            data["notes"] = notes
        if intensity:
            data["intensity"] = intensity
        if triggers:
            data["triggers"] = triggers
        if location:
            data["location"] = location
        
        return self._make_request("POST", "/api/mood", data=data)
    
    def get_mood_analytics(self) -> OMAPIResponse:
        """Get mood analytics"""
        return self._make_request("GET", "/api/mood/analytics")
    
    def get_mood_suggestions(self, count: int = 5) -> OMAPIResponse:
        """Get mood suggestions"""
        return self._make_request("GET", "/api/mood/suggestions", params={"count": count})
    
    # Check-in API methods
    def get_checkins(self, limit: int = 50, days: int = None) -> OMAPIResponse:
        """Get check-in entries"""
        params = {"limit": limit}
        if days:
            params["days"] = days
        return self._make_request("GET", "/api/checkin", params=params)
    
    def add_checkin(self, checkin_data: Dict) -> OMAPIResponse:
        """Add check-in entry"""
        return self._make_request("POST", "/api/checkin", data=checkin_data)
    
    # Dashboard API methods
    def get_dashboard(self) -> OMAPIResponse:
        """Get full dashboard data"""
        return self._make_request("GET", "/api/dashboard")
    
    def get_dashboard_summary(self) -> OMAPIResponse:
        """Get dashboard summary"""
        return self._make_request("GET", "/api/dashboard/summary")
    
    # Quick actions API methods
    def quick_mood(self, mood: str = None) -> OMAPIResponse:
        """Quick mood logging"""
        data = {}
        if mood:
            data["mood"] = mood
        return self._make_request("POST", "/api/quick/mood", data=data)
    
    def quick_gratitude(self, content: str) -> OMAPIResponse:
        """Quick gratitude entry"""
        return self._make_request("POST", "/api/quick/gratitude", data={"content": content})
    
    # Backup API methods
    def create_backup(self, name: str = None) -> OMAPIResponse:
        """Create backup"""
        data = {}
        if name:
            data["name"] = name
        return self._make_request("POST", "/api/backup", data=data)
    
    def list_backups(self) -> OMAPIResponse:
        """List available backups"""
        return self._make_request("GET", "/api/backup/list")

class OMAPIHelper:
    """Helper class with convenience methods"""
    
    def __init__(self, client: OMAPIClient):
        self.client = client
    
    def log_daily_mood(self, mood: str, notes: str = None) -> bool:
        """Log daily mood with error handling"""
        response = self.client.add_mood(mood, notes=notes)
        if response.success:
            print(f"✅ Mood logged: {mood}")
            return True
        else:
            print(f"❌ Failed to log mood: {response.error}")
            return False
    
    def quick_checkin(self, mood: str, energy: int, stress: int, notes: str = None) -> bool:
        """Quick daily check-in"""
        checkin_data = {
            "type": "quick_api_checkin",
            "mood": mood,
            "energy_level": energy,
            "stress_level": stress,
            "date": datetime.datetime.now().isoformat()
        }
        
        if notes:
            checkin_data["notes"] = notes
        
        response = self.client.add_checkin(checkin_data)
        if response.success:
            print(f"✅ Check-in completed: {mood} (Energy: {energy}, Stress: {stress})")
            return True
        else:
            print(f"❌ Check-in failed: {response.error}")
            return False
    
    def get_wellness_summary(self) -> Dict:
        """Get wellness summary with error handling"""
        response = self.client.get_dashboard_summary()
        if response.success:
            return response.data
        else:
            print(f"❌ Failed to get wellness summary: {response.error}")
            return {}
    
    def backup_data(self) -> bool:
        """Create backup with timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        response = self.client.create_backup(f"api_backup_{timestamp}")
        
        if response.success:
            print(f"✅ Backup created: {response.data.get('backup_name', 'Unknown')}")
            return True
        else:
            print(f"❌ Backup failed: {response.error}")
            return False

# Example usage and testing
def example_usage():
    """Example usage of the API client"""
    
    # Initialize client (you'll need to provide your API key)
    api_key = "your_api_key_here"  # Replace with actual API key
    client = OMAPIClient(api_key=api_key)
    helper = OMAPIHelper(client)
    
    print("🧘‍♀️ om API Client Example")
    print("=" * 30)
    
    # Health check
    print("1. Health check...")
    health = client.health_check()
    if health.success:
        print(f"   ✅ API server is healthy: {health.data.get('status')}")
    else:
        print(f"   ❌ Health check failed: {health.error}")
        return
    
    # Log mood
    print("\n2. Logging mood...")
    helper.log_daily_mood("happy", "Feeling good today!")
    
    # Quick check-in
    print("\n3. Quick check-in...")
    helper.quick_checkin("content", energy=7, stress=3, notes="Good day overall")
    
    # Get mood analytics
    print("\n4. Getting mood analytics...")
    analytics = client.get_mood_analytics()
    if analytics.success:
        total_entries = analytics.data.get("total_entries", 0)
        print(f"   📊 Total mood entries: {total_entries}")
    
    # Get wellness summary
    print("\n5. Getting wellness summary...")
    summary = helper.get_wellness_summary()
    if summary:
        wellness_score = summary.get("overall_wellness", {}).get("score", "Unknown")
        print(f"   🌟 Wellness score: {wellness_score}")
    
    # Create backup
    print("\n6. Creating backup...")
    helper.backup_data()
    
    print("\n✅ Example completed!")

if __name__ == "__main__":
    if REQUESTS_AVAILABLE:
        example_usage()
    else:
        print("Install requests to run example: pip install requests")
