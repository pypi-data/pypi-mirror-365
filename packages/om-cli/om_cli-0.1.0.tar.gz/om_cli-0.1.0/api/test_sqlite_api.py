#!/usr/bin/env python3
"""
Test script for SQLite om API implementation
Tests the SQLite storage system and API integration
"""

import requests
import json
import time
from datetime import datetime
from sqlite_storage import OMSQLiteStorage

class SQLiteAPITester:
    """Test the SQLite om API functionality"""
    
    def __init__(self, base_url="http://localhost:5000", api_key=None):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {}
        
        if api_key:
            self.headers['X-API-Key'] = api_key
    
    def test_storage_direct(self):
        """Test SQLite storage directly (without API)"""
        print("🗄️  Testing SQLite storage directly...")
        
        try:
            # Create temporary storage instance
            storage = OMSQLiteStorage(":memory:")  # In-memory database for testing
            
            # Test mood entry
            mood_id = storage.add_mood_entry(
                mood="happy",
                intensity=8,
                notes="Testing SQLite storage",
                triggers=["testing", "development"],
                location="home"
            )
            print(f"   ✅ Added mood entry: {mood_id}")
            
            # Test retrieving moods
            moods = storage.get_mood_entries(limit=5)
            print(f"   ✅ Retrieved {len(moods)} mood entries")
            
            if moods:
                mood = moods[0]
                print(f"   📊 Latest mood: {mood['mood']} (intensity: {mood['intensity']})")
                print(f"   🏷️  Triggers: {mood['triggers']}")
            
            # Test wellness session
            session_id = storage.add_wellness_session(
                activity_type="meditation",
                duration_minutes=10,
                notes="Test meditation session",
                rating=4
            )
            print(f"   ✅ Added wellness session: {session_id}")
            
            # Test goal
            goal_id = storage.add_wellness_goal(
                title="Daily Meditation",
                description="Meditate for 10 minutes daily",
                category="mindfulness",
                target_value=30,
                unit="days"
            )
            print(f"   ✅ Added wellness goal: {goal_id}")
            
            # Test goal progress
            storage.update_goal_progress(goal_id, 1)
            goals = storage.get_wellness_goals()
            if goals:
                goal = goals[0]
                print(f"   📈 Goal progress: {goal['progress_percentage']:.1f}%")
            
            # Test dashboard data
            dashboard = storage.get_dashboard_data()
            print(f"   ✅ Dashboard wellness score: {dashboard['wellness_score']}")
            
            # Test analytics
            analytics = storage.get_mood_analytics()
            print(f"   📊 Mood analytics: {analytics['total_entries']} total entries")
            
            # Test backup
            backup_path = storage.create_backup("test_backup")
            print(f"   💾 Created backup: {backup_path}")
            
            # Test database stats
            stats = storage.get_database_stats()
            print(f"   📈 Database stats: {stats['mood_entries']} mood entries")
            
            storage.close()
            return True
            
        except Exception as e:
            print(f"   ❌ Storage test error: {e}")
            return False
    
    def test_health_check(self):
        """Test health check endpoint"""
        print("🏥 Testing health check...")
        
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Health check passed: {data['data']['status']}")
                print(f"   📊 Storage: {data['data']['storage']}")
                print(f"   💾 Database size: {data['data']['database_size_mb']} MB")
                print(f"   📈 Total entries: {data['data']['total_entries']}")
                return True
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
            return False
    
    def test_mood_tracking(self):
        """Test mood tracking functionality"""
        print("😊 Testing mood tracking...")
        
        try:
            # Test adding multiple mood entries
            mood_entries = [
                {
                    "mood": "happy",
                    "intensity": 8,
                    "notes": "Great day with SQLite!",
                    "triggers": ["work_success", "good_weather"],
                    "location": "office",
                    "energy_level": 9,
                    "stress_level": 2
                },
                {
                    "mood": "calm",
                    "intensity": 7,
                    "notes": "Peaceful evening",
                    "triggers": ["meditation", "nature"],
                    "location": "home",
                    "energy_level": 6,
                    "stress_level": 3
                },
                {
                    "mood": "energetic",
                    "intensity": 9,
                    "notes": "Morning workout boost",
                    "triggers": ["exercise", "music"],
                    "location": "gym",
                    "energy_level": 10,
                    "stress_level": 1
                }
            ]
            
            added_ids = []
            for mood_data in mood_entries:
                response = requests.post(
                    f"{self.base_url}/api/mood",
                    headers=self.headers,
                    json=mood_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    added_ids.append(data['data']['id'])
                    print(f"   ✅ Added mood: {data['data']['mood']} (intensity: {data['data']['intensity']})")
                else:
                    print(f"   ❌ Failed to add mood: {response.status_code}")
                    return False
            
            # Test retrieving mood entries
            response = requests.get(f"{self.base_url}/api/mood?limit=10", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                count = data['data']['count']
                print(f"   ✅ Retrieved {count} mood entries")
                
                if count > 0:
                    latest_mood = data['data']['entries'][0]
                    print(f"   📊 Latest: {latest_mood['mood']} with triggers: {latest_mood['triggers']}")
                    print(f"   ⚡ Energy: {latest_mood['energy_level']}, Stress: {latest_mood['stress_level']}")
            else:
                print(f"   ❌ Failed to get moods: {response.status_code}")
                return False
            
            # Test mood analytics
            response = requests.get(f"{self.base_url}/api/mood/analytics", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                analytics = data['data']
                print(f"   📈 Analytics: {analytics['total_entries']} total, avg intensity: {analytics.get('average_intensity', 0):.1f}")
                print(f"   🎯 Most common mood: {analytics.get('most_common_mood', 'N/A')}")
                return True
            else:
                print(f"   ❌ Failed to get analytics: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Mood tracking error: {e}")
            return False
    
    def test_wellness_sessions(self):
        """Test wellness session functionality"""
        print("🧘 Testing wellness sessions...")
        
        try:
            # Test adding wellness sessions
            sessions = [
                {
                    "activity_type": "meditation",
                    "duration_minutes": 15,
                    "notes": "Morning meditation session",
                    "rating": 5,
                    "mood_before": "stressed",
                    "mood_after": "calm"
                },
                {
                    "activity_type": "breathing",
                    "duration_minutes": 5,
                    "notes": "Quick breathing exercise",
                    "rating": 4,
                    "mood_before": "anxious",
                    "mood_after": "relaxed"
                },
                {
                    "activity_type": "exercise",
                    "duration_minutes": 30,
                    "notes": "Morning jog",
                    "rating": 5,
                    "mood_before": "tired",
                    "mood_after": "energetic"
                }
            ]
            
            for session_data in sessions:
                response = requests.post(
                    f"{self.base_url}/api/wellness/sessions",
                    headers=self.headers,
                    json=session_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Added session: {session_data['activity_type']} ({session_data['duration_minutes']}min, rating: {session_data['rating']})")
                else:
                    print(f"   ❌ Failed to add session: {response.status_code}")
                    return False
            
            # Test retrieving sessions
            response = requests.get(f"{self.base_url}/api/wellness/sessions?limit=10", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                sessions = data['data']['sessions']
                print(f"   ✅ Retrieved {len(sessions)} wellness sessions")
                
                if sessions:
                    session = sessions[0]
                    print(f"   🎯 Latest: {session['activity_type']} - {session['mood_before']} → {session['mood_after']}")
                
                return True
            else:
                print(f"   ❌ Failed to get sessions: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Wellness sessions error: {e}")
            return False
    
    def test_goals(self):
        """Test wellness goals functionality"""
        print("🎯 Testing wellness goals...")
        
        try:
            # Test adding goals
            goals = [
                {
                    "title": "Daily Meditation",
                    "description": "Meditate for 10 minutes every day",
                    "category": "mindfulness",
                    "target_value": 30,
                    "unit": "days",
                    "priority": "high"
                },
                {
                    "title": "Weekly Exercise",
                    "description": "Exercise 3 times per week",
                    "category": "exercise",
                    "target_value": 12,
                    "unit": "sessions",
                    "priority": "medium"
                }
            ]
            
            goal_ids = []
            for goal_data in goals:
                response = requests.post(
                    f"{self.base_url}/api/goals",
                    headers=self.headers,
                    json=goal_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    goal_ids.append(data['data']['id'])
                    print(f"   ✅ Added goal: {goal_data['title']} (target: {goal_data['target_value']} {goal_data['unit']})")
                else:
                    print(f"   ❌ Failed to add goal: {response.status_code}")
                    return False
            
            # Test updating goal progress
            if goal_ids:
                goal_id = goal_ids[0]
                response = requests.post(
                    f"{self.base_url}/api/goals/{goal_id}/progress",
                    headers=self.headers,
                    json={"increment": 3}
                )
                
                if response.status_code == 200:
                    print(f"   ✅ Updated goal progress")
                else:
                    print(f"   ❌ Failed to update progress: {response.status_code}")
            
            # Test retrieving goals
            response = requests.get(f"{self.base_url}/api/goals", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                goals = data['data']['goals']
                print(f"   ✅ Retrieved {len(goals)} wellness goals")
                
                for goal in goals:
                    print(f"   📈 {goal['title']}: {goal['progress_percentage']:.1f}% complete")
                
                return True
            else:
                print(f"   ❌ Failed to get goals: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Goals error: {e}")
            return False
    
    def test_dashboard(self):
        """Test dashboard functionality"""
        print("📊 Testing dashboard...")
        
        try:
            response = requests.get(f"{self.base_url}/api/dashboard", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                dashboard = data['data']
                
                print(f"   ✅ Dashboard data retrieved")
                print(f"   📅 Today: {dashboard['today']}")
                print(f"   💚 Wellness score: {dashboard['overall_wellness']['score']}")
                print(f"   📈 Wellness level: {dashboard['overall_wellness']['level']}")
                print(f"   😊 Current mood: {dashboard['mood']['current_mood'] or 'Not set'}")
                print(f"   📊 Mood trend: {dashboard['mood']['trend']}")
                print(f"   🧘 Sessions today: {dashboard['wellness_sessions']['sessions_today']}")
                print(f"   🎯 Active goals: {dashboard['active_goals']}")
                print(f"   🏆 Achievements: {dashboard['achievements']['total_unlocked']}")
                
                return True
            else:
                print(f"   ❌ Failed to get dashboard: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Dashboard error: {e}")
            return False
    
    def test_quick_actions(self):
        """Test quick actions"""
        print("⚡ Testing quick actions...")
        
        try:
            # Test quick mood log
            response = requests.post(
                f"{self.base_url}/api/quick/mood",
                headers=self.headers,
                json={"mood": "grateful"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Quick mood logged: {data['data']['mood']}")
            else:
                print(f"   ❌ Failed quick mood log: {response.status_code}")
                return False
            
            # Test quick gratitude
            response = requests.post(
                f"{self.base_url}/api/quick/gratitude",
                headers=self.headers,
                json={"content": "Grateful for this SQLite implementation working so well!"}
            )
            
            if response.status_code == 200:
                print(f"   ✅ Quick gratitude logged")
                return True
            else:
                print(f"   ❌ Failed quick gratitude: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Quick actions error: {e}")
            return False
    
    def test_backup_and_stats(self):
        """Test backup and statistics"""
        print("💾 Testing backup and stats...")
        
        try:
            # Test database stats
            response = requests.get(f"{self.base_url}/api/stats", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                stats = data['data']
                print(f"   ✅ Database stats retrieved")
                print(f"   📊 Mood entries: {stats.get('mood_entries', 0)}")
                print(f"   🧘 Wellness sessions: {stats.get('wellness_sessions', 0)}")
                print(f"   🎯 Goals: {stats.get('wellness_goals', 0)}")
                print(f"   💾 Database size: {stats.get('database_size_mb', 0):.2f} MB")
            else:
                print(f"   ❌ Failed to get stats: {response.status_code}")
                return False
            
            # Test backup creation
            response = requests.post(
                f"{self.base_url}/api/backup",
                headers=self.headers,
                json={"name": "test_api_backup"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Backup created: {data['data']['backup_name']}")
                return True
            else:
                print(f"   ❌ Failed to create backup: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Backup/stats error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Running SQLite om API Tests")
        print("=" * 60)
        
        tests = [
            ("Direct Storage", self.test_storage_direct),
            ("Health Check", self.test_health_check),
            ("Mood Tracking", self.test_mood_tracking),
            ("Wellness Sessions", self.test_wellness_sessions),
            ("Goals", self.test_goals),
            ("Dashboard", self.test_dashboard),
            ("Quick Actions", self.test_quick_actions),
            ("Backup & Stats", self.test_backup_and_stats)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name} test...")
            if test_func():
                passed += 1
                print(f"   ✅ {test_name} test PASSED")
            else:
                print(f"   ❌ {test_name} test FAILED")
        
        print("\n" + "=" * 60)
        print(f"🎯 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! SQLite om API is working perfectly.")
            print("🚀 Your mental health platform is ready with robust SQLite storage!")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        
        return passed == total

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test SQLite om API')
    parser.add_argument('--url', default='http://localhost:5000', help='API base URL')
    parser.add_argument('--api-key', help='API key for authentication')
    parser.add_argument('--storage-only', action='store_true', help='Test only direct storage (no API)')
    
    args = parser.parse_args()
    
    if args.storage_only:
        # Test storage directly
        tester = SQLiteAPITester()
        if tester.test_storage_direct():
            print("🎉 Direct storage test passed!")
            return 0
        else:
            print("❌ Direct storage test failed!")
            return 1
    
    if not args.api_key:
        print("⚠️  No API key provided. You'll need to:")
        print("   1. Start the SQLite server: python3 sqlite_server.py")
        print("   2. Copy the API key from the startup output")
        print("   3. Run this test with: python3 test_sqlite_api.py --api-key YOUR_KEY")
        print("\n   Or test storage directly: python3 test_sqlite_api.py --storage-only")
        return 1
    
    tester = SQLiteAPITester(base_url=args.url, api_key=args.api_key)
    
    if tester.run_all_tests():
        return 0
    else:
        return 1

if __name__ == '__main__':
    exit(main())
