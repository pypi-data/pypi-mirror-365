#!/usr/bin/env python3
"""
Test script for Enhanced om API
Tests the integrated SQLAlchemy models and wellness coach functionality
"""

import requests
import json
import time
from datetime import datetime

class EnhancedAPITester:
    """Test the enhanced om API functionality"""
    
    def __init__(self, base_url="http://localhost:5000", api_key=None):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {}
        
        if api_key:
            self.headers['X-API-Key'] = api_key
    
    def test_health_check(self):
        """Test health check endpoint"""
        print("🏥 Testing health check...")
        
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Health check passed: {data['data']['status']}")
                print(f"   📊 Version: {data['data']['version']}")
                return True
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
            return False
    
    def test_api_info(self):
        """Test API info endpoint"""
        print("ℹ️  Testing API info...")
        
        try:
            response = requests.get(f"{self.base_url}/api/info", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                features = data['data']['features']
                print(f"   ✅ API info retrieved")
                print(f"   🚀 Features: {', '.join(features)}")
                return True
            else:
                print(f"   ❌ API info failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ API info error: {e}")
            return False
    
    def test_mood_tracking(self):
        """Test mood tracking functionality"""
        print("😊 Testing mood tracking...")
        
        # Test adding a mood entry
        mood_data = {
            "mood": "happy",
            "intensity": 8,
            "notes": "Testing the enhanced API!",
            "triggers": ["work_success", "good_weather"],
            "location": "home"
        }
        
        try:
            # Add mood entry
            response = requests.post(
                f"{self.base_url}/api/mood",
                headers=self.headers,
                json=mood_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Mood entry added: {data['data']['mood']} (intensity: {data['data']['intensity']})")
                mood_id = data['data']['id']
            else:
                print(f"   ❌ Failed to add mood: {response.status_code}")
                return False
            
            # Get mood entries
            response = requests.get(f"{self.base_url}/api/mood?limit=5", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                count = data['data']['count']
                print(f"   ✅ Retrieved {count} mood entries")
                
                if count > 0:
                    latest_mood = data['data']['entries'][0]
                    print(f"   📊 Latest mood: {latest_mood['mood_display']} with triggers: {latest_mood['triggers']}")
                
                return True
            else:
                print(f"   ❌ Failed to get moods: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Mood tracking error: {e}")
            return False
    
    def test_wellness_coach(self):
        """Test wellness coach functionality"""
        print("🧠 Testing wellness coach...")
        
        try:
            # Test insights
            response = requests.get(f"{self.base_url}/api/coach/insights", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                insights = data['data']['insights']
                recommendations = data['data']['recommendations']
                wellness_score = data['data']['wellness_score']
                
                print(f"   ✅ Wellness insights generated")
                print(f"   📊 Wellness score: {wellness_score}")
                print(f"   💡 Insights: {len(insights)} items")
                print(f"   🎯 Recommendations: {len(recommendations)} items")
                
                if insights:
                    print(f"   📝 Sample insight: {insights[0]}")
                if recommendations:
                    print(f"   💭 Sample recommendation: {recommendations[0]}")
            else:
                print(f"   ❌ Failed to get insights: {response.status_code}")
                return False
            
            # Test activity suggestions
            response = requests.get(
                f"{self.base_url}/api/coach/suggestions?mood=stressed&time=10",
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                suggestions = data['data']['suggestions']
                print(f"   ✅ Activity suggestions generated: {len(suggestions)} items")
                
                if suggestions:
                    suggestion = suggestions[0]
                    print(f"   🎯 Top suggestion: {suggestion['activity']} ({suggestion['duration']}min) - {suggestion['reason']}")
                
                return True
            else:
                print(f"   ❌ Failed to get suggestions: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Wellness coach error: {e}")
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
                print(f"   😊 Current mood: {dashboard['mood']['current_mood'] or 'Not set'}")
                print(f"   🏆 Achievements: {dashboard['achievements']['total_unlocked']}")
                print(f"   📈 Completion rate: {dashboard['achievements']['completion_rate']:.1f}%")
                
                return True
            else:
                print(f"   ❌ Failed to get dashboard: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Dashboard error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Running Enhanced om API Tests")
        print("=" * 50)
        
        tests = [
            self.test_health_check,
            self.test_api_info,
            self.test_mood_tracking,
            self.test_wellness_coach,
            self.test_dashboard
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        print("=" * 50)
        print(f"🎯 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Enhanced API is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        
        return passed == total

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Enhanced om API')
    parser.add_argument('--url', default='http://localhost:5000', help='API base URL')
    parser.add_argument('--api-key', help='API key for authentication')
    
    args = parser.parse_args()
    
    if not args.api_key:
        print("⚠️  No API key provided. You'll need to:")
        print("   1. Start the enhanced server: python3 enhanced_server.py")
        print("   2. Copy the API key from the startup output")
        print("   3. Run this test with: python3 test_enhanced_api.py --api-key YOUR_KEY")
        return 1
    
    tester = EnhancedAPITester(base_url=args.url, api_key=args.api_key)
    
    if tester.run_all_tests():
        return 0
    else:
        return 1

if __name__ == '__main__':
    exit(main())
