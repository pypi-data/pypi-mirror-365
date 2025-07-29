#!/usr/bin/env python3
"""
Production readiness test script for om
Tests all core functionality to ensure everything works
"""

import subprocess
import sys
import os
import json
import tempfile
from pathlib import Path

# Get the correct path to main.py (one level up from tests)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
MAIN_PY = os.path.join(PROJECT_DIR, 'main.py')
OM_EXECUTABLE = os.path.join(PROJECT_DIR, 'om')

def run_command(cmd, input_text=None, timeout=5):
    """Run a command and return result"""
    try:
        if input_text:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, 
                input=input_text, timeout=timeout
            )
        else:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=timeout
            )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_basic_commands():
    """Test basic command functionality"""
    print("🧪 Testing Basic Commands")
    print("=" * 40)
    
    tests = [
        (f"python3 {MAIN_PY}", None, "Welcome screen"),
        (f"python3 {MAIN_PY} help", None, "Help command"),
        (f"python3 {MAIN_PY} status", None, "Status command"),
        (f"python3 {MAIN_PY} about", None, "About command"),
    ]
    
    results = []
    for cmd, input_text, description in tests:
        success, stdout, stderr = run_command(cmd, input_text)
        status = "✅" if success else "❌"
        print(f"{status} {description}")
        if not success:
            print(f"   Error: {stderr}")
        results.append((description, success))
    
    return results

def test_quick_actions():
    """Test quick action commands"""
    print("\n🚀 Testing Quick Actions")
    print("=" * 40)
    
    tests = [
        (f"python3 {MAIN_PY} qm", "7\n", "Quick mood (qm)"),
        (f"python3 {MAIN_PY} qg", "grateful for health\n\n\n", "Quick gratitude (qg)"),
    ]
    
    results = []
    for cmd, input_text, description in tests:
        success, stdout, stderr = run_command(cmd, input_text, timeout=10)
        status = "✅" if success else "❌"
        print(f"{status} {description}")
        if not success:
            print(f"   Error: {stderr}")
        if "Error running" in stdout:
            print(f"   Module error in output")
            success = False
        results.append((description, success))
    
    return results

def test_advanced_features():
    """Test advanced features"""
    print("\n🎯 Testing Advanced Features")
    print("=" * 40)
    
    tests = [
        (f"python3 {MAIN_PY} gamify status", None, "Gamification status"),
        (f"python3 {MAIN_PY} coach daily", None, "AI coach daily"),
        (f"python3 {MAIN_PY} dashboard show", None, "Dashboard show"),
        (f"python3 {MAIN_PY} autopilot status", None, "Autopilot status"),
    ]
    
    results = []
    for cmd, input_text, description in tests:
        success, stdout, stderr = run_command(cmd, input_text)
        status = "✅" if success else "❌"
        print(f"{status} {description}")
        if not success:
            print(f"   Error: {stderr}")
        results.append((description, success))
    
    return results

def test_visual_mode():
    """Test visual mode functionality"""
    print("\n✨ Testing Visual Mode")
    print("=" * 40)
    
    # Test that visual achievements can be imported
    try:
        from modules.visual_achievements import handle_visual_command
        print("✅ Visual achievements module imports")
        visual_import = True
    except Exception as e:
        print(f"❌ Visual achievements import failed: {e}")
        visual_import = False
    
    # Test that achievements gallery exists
    gallery_path = os.path.join(PROJECT_DIR, "modules", "achievements_gallery.py")
    gallery_exists = os.path.exists(gallery_path)
    status = "✅" if gallery_exists else "❌"
    print(f"{status} Achievements gallery file exists")
    
    return [
        ("Visual module import", visual_import),
        ("Gallery file exists", gallery_exists)
    ]

def test_data_persistence():
    """Test data saving and loading"""
    print("\n💾 Testing Data Persistence")
    print("=" * 40)
    
    # Check if .om directory exists
    om_dir = Path.home() / ".om"
    om_exists = om_dir.exists()
    status = "✅" if om_exists else "❌"
    print(f"{status} ~/.om directory exists")
    
    # Check for data files
    data_files = []
    if om_exists:
        for file in om_dir.glob("*.json"):
            data_files.append(file.name)
    
    print(f"📁 Data files found: {len(data_files)}")
    for file in data_files:
        print(f"   - {file}")
    
    return [("Data directory exists", om_exists)]

def test_error_handling():
    """Test error handling"""
    print("\n🛡️ Testing Error Handling")
    print("=" * 40)
    
    tests = [
        (f"python3 {MAIN_PY} nonexistent", None, "Invalid command"),
        (f"python3 {MAIN_PY} mood --invalid-flag", None, "Invalid flag"),
    ]
    
    results = []
    for cmd, input_text, description in tests:
        success, stdout, stderr = run_command(cmd, input_text)
        # For error handling tests, we expect graceful error messages
        graceful_failure = ("Unknown command" in stdout or 
                          "help" in stdout.lower() or 
                          "available commands" in stdout.lower())
        status = "✅" if graceful_failure else "❌"
        print(f"{status} {description} - Graceful failure")
        if not graceful_failure:
            print(f"   Output: {stdout[:100]}...")
        results.append((description, graceful_failure))
    
    return results

def generate_report(all_results):
    """Generate final report"""
    print("\n" + "=" * 60)
    print("🎯 PRODUCTION READINESS REPORT")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    
    for category, results in all_results.items():
        print(f"\n{category}:")
        for test_name, success in results:
            status = "✅" if success else "❌"
            print(f"  {status} {test_name}")
            total_tests += 1
            if success:
                passed_tests += 1
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"\n📊 SUMMARY:")
    print(f"   Tests passed: {passed_tests}/{total_tests}")
    print(f"   Success rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 READY FOR PRODUCTION!")
    elif success_rate >= 75:
        print("⚠️  MOSTLY READY - Fix remaining issues")
    else:
        print("❌ NOT READY - Major issues need fixing")
    
    return success_rate

def main():
    """Run all tests"""
    print("🧘‍♀️ om Production Readiness Test")
    print("=" * 60)
    
    # Change to om directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run all test categories
    all_results = {
        "Basic Commands": test_basic_commands(),
        "Quick Actions": test_quick_actions(),
        "Advanced Features": test_advanced_features(),
        "Visual Mode": test_visual_mode(),
        "Data Persistence": test_data_persistence(),
        "Error Handling": test_error_handling(),
    }
    
    # Generate final report
    success_rate = generate_report(all_results)
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 90 else 1)

if __name__ == "__main__":
    main()
