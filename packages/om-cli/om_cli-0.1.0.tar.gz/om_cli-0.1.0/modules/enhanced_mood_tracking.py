#!/usr/bin/env python3
"""
Enhanced Mood Tracking Module for om - Inspired by Logbuch
Advanced mood tracking with rich visualization and analytics
"""

import os
import json
import random
import datetime
from typing import Dict, List, Optional
from pathlib import Path

def get_data_dir():
    """Get om data directory"""
    home = Path.home()
    data_dir = home / ".om" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def get_mood_file():
    """Get mood data file path"""
    return get_data_dir() / "mood_entries.json"

def load_mood_data():
    """Load mood data from file"""
    mood_file = get_mood_file()
    if mood_file.exists():
        try:
            with open(mood_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return {"entries": [], "stats": {}}

def save_mood_data(data):
    """Save mood data to file"""
    mood_file = get_mood_file()
    with open(mood_file, 'w') as f:
        json.dump(data, f, indent=2)

def get_comprehensive_moods():
    """Get comprehensive list of mood options"""
    return {
        "positive": [
            "ecstatic", "joyful", "happy", "content", "peaceful", "grateful", 
            "optimistic", "energetic", "confident", "relaxed", "inspired", 
            "motivated", "cheerful", "blissful", "euphoric", "serene",
            "excited", "proud", "accomplished", "loved", "hopeful"
        ],
        "neutral": [
            "calm", "focused", "balanced", "steady", "neutral", "contemplative",
            "pensive", "reflective", "curious", "alert", "observant",
            "thoughtful", "centered", "stable", "composed"
        ],
        "challenging": [
            "tired", "stressed", "anxious", "overwhelmed", "frustrated", 
            "sad", "melancholy", "worried", "restless", "confused", 
            "disappointed", "lonely", "irritated", "bored", "uncertain",
            "angry", "fearful", "discouraged", "empty", "numb"
        ],
        "complex": [
            "nostalgic", "determined", "ambitious", "creative", "adventurous",
            "romantic", "philosophical", "introspective", "empathetic", 
            "compassionate", "humble", "vulnerable", "conflicted", "mixed"
        ]
    }

def get_random_mood():
    """Get a random mood from all categories"""
    all_moods = get_comprehensive_moods()
    category = random.choice(list(all_moods.keys()))
    return random.choice(all_moods[category])

def get_mood_suggestions(count=5):
    """Get mood suggestions across different categories"""
    all_moods = get_comprehensive_moods()
    suggestions = []
    
    # Get at least one from each category
    for category, moods in all_moods.items():
        suggestions.append(random.choice(moods))
    
    # Fill remaining with random selections
    while len(suggestions) < count:
        category = random.choice(list(all_moods.keys()))
        mood = random.choice(all_moods[category])
        if mood not in suggestions:
            suggestions.append(mood)
    
    return suggestions[:count]

def add_mood_entry(mood, notes=None, intensity=None, triggers=None, location=None):
    """Add a comprehensive mood entry"""
    data = load_mood_data()
    
    entry = {
        "id": len(data["entries"]) + 1,
        "mood": mood.lower(),
        "notes": notes,
        "intensity": intensity,  # 1-10 scale
        "triggers": triggers or [],  # List of triggers
        "location": location,
        "date": datetime.datetime.now().isoformat(),
        "timestamp": datetime.datetime.now().timestamp()
    }
    
    data["entries"].append(entry)
    
    # Update stats
    update_mood_stats(data)
    
    save_mood_data(data)
    return entry

def update_mood_stats(data):
    """Update mood statistics"""
    entries = data["entries"]
    if not entries:
        return
    
    # Calculate basic stats
    total_entries = len(entries)
    recent_entries = [e for e in entries if 
                     datetime.datetime.fromisoformat(e["date"]).date() >= 
                     datetime.date.today() - datetime.timedelta(days=7)]
    
    # Mood frequency
    mood_counts = {}
    for entry in entries:
        mood = entry["mood"]
        mood_counts[mood] = mood_counts.get(mood, 0) + 1
    
    # Average intensity
    intensities = [e["intensity"] for e in entries if e.get("intensity")]
    avg_intensity = sum(intensities) / len(intensities) if intensities else None
    
    # Recent trends
    recent_moods = [e["mood"] for e in recent_entries]
    
    data["stats"] = {
        "total_entries": total_entries,
        "entries_this_week": len(recent_entries),
        "most_common_mood": max(mood_counts.items(), key=lambda x: x[1])[0] if mood_counts else None,
        "average_intensity": round(avg_intensity, 1) if avg_intensity else None,
        "recent_moods": recent_moods,
        "mood_distribution": mood_counts,
        "last_updated": datetime.datetime.now().isoformat()
    }

def get_mood_entries(limit=None, days=None):
    """Get mood entries with optional filtering"""
    data = load_mood_data()
    entries = data["entries"]
    
    if days:
        cutoff_date = datetime.date.today() - datetime.timedelta(days=days)
        entries = [e for e in entries if 
                  datetime.datetime.fromisoformat(e["date"]).date() >= cutoff_date]
    
    # Sort by date (newest first)
    entries.sort(key=lambda x: x["timestamp"], reverse=True)
    
    if limit:
        entries = entries[:limit]
    
    return entries

def get_mood_analytics():
    """Get comprehensive mood analytics"""
    data = load_mood_data()
    entries = data["entries"]
    
    if not entries:
        return {"message": "No mood data available yet. Start tracking your mood!"}
    
    # Time-based analysis
    today = datetime.date.today()
    week_entries = [e for e in entries if 
                   datetime.datetime.fromisoformat(e["date"]).date() >= today - datetime.timedelta(days=7)]
    month_entries = [e for e in entries if 
                    datetime.datetime.fromisoformat(e["date"]).date() >= today - datetime.timedelta(days=30)]
    
    # Mood categorization
    all_moods = get_comprehensive_moods()
    mood_categories = {}
    for entry in entries:
        mood = entry["mood"]
        for category, moods in all_moods.items():
            if mood in moods:
                mood_categories[category] = mood_categories.get(category, 0) + 1
                break
    
    # Intensity analysis
    intensities = [e["intensity"] for e in entries if e.get("intensity")]
    
    # Pattern detection
    patterns = detect_mood_patterns(entries)
    
    return {
        "total_entries": len(entries),
        "entries_this_week": len(week_entries),
        "entries_this_month": len(month_entries),
        "mood_categories": mood_categories,
        "average_intensity": round(sum(intensities) / len(intensities), 1) if intensities else None,
        "intensity_range": {"min": min(intensities), "max": max(intensities)} if intensities else None,
        "patterns": patterns,
        "recent_trend": analyze_recent_trend(entries[-10:] if len(entries) >= 10 else entries),
        "stats": data.get("stats", {})
    }

def detect_mood_patterns(entries):
    """Detect patterns in mood data"""
    if len(entries) < 7:
        return {"message": "Need more data to detect patterns"}
    
    patterns = {}
    
    # Day of week patterns
    day_moods = {}
    for entry in entries:
        date_obj = datetime.datetime.fromisoformat(entry["date"])
        day_name = date_obj.strftime("%A")
        if day_name not in day_moods:
            day_moods[day_name] = []
        day_moods[day_name].append(entry["mood"])
    
    # Time of day patterns
    hour_moods = {}
    for entry in entries:
        date_obj = datetime.datetime.fromisoformat(entry["date"])
        hour = date_obj.hour
        time_period = get_time_period(hour)
        if time_period not in hour_moods:
            hour_moods[time_period] = []
        hour_moods[time_period].append(entry["mood"])
    
    patterns["day_patterns"] = day_moods
    patterns["time_patterns"] = hour_moods
    
    return patterns

def get_time_period(hour):
    """Convert hour to time period"""
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"

def analyze_recent_trend(recent_entries):
    """Analyze recent mood trend"""
    if len(recent_entries) < 3:
        return "insufficient_data"
    
    all_moods = get_comprehensive_moods()
    
    # Score moods (positive=1, neutral=0, challenging=-1, complex=0.5)
    mood_scores = []
    for entry in recent_entries:
        mood = entry["mood"]
        for category, moods in all_moods.items():
            if mood in moods:
                if category == "positive":
                    mood_scores.append(1)
                elif category == "neutral":
                    mood_scores.append(0)
                elif category == "challenging":
                    mood_scores.append(-1)
                else:  # complex
                    mood_scores.append(0.5)
                break
    
    if len(mood_scores) < 2:
        return "stable"
    
    # Calculate trend
    first_half = sum(mood_scores[:len(mood_scores)//2]) / (len(mood_scores)//2)
    second_half = sum(mood_scores[len(mood_scores)//2:]) / (len(mood_scores) - len(mood_scores)//2)
    
    difference = second_half - first_half
    
    if difference > 0.3:
        return "improving"
    elif difference < -0.3:
        return "declining"
    else:
        return "stable"

def enhanced_mood_command(action="menu", *args):
    """Enhanced mood tracking command"""
    print("🎭 Enhanced Mood Tracking")
    print("=" * 40)
    
    if action == "menu" or not action:
        show_mood_menu()
    elif action == "add":
        interactive_mood_entry()
    elif action == "list":
        show_mood_list()
    elif action == "analytics":
        show_mood_analytics()
    elif action == "random":
        add_random_mood()
    elif action == "suggest":
        show_mood_suggestions()
    else:
        # Try to add mood directly
        add_mood_entry(action, notes=" ".join(args) if args else None)
        print(f"✅ Added mood: {action}")

def show_mood_menu():
    """Show interactive mood menu"""
    print("\n🎭 Mood Tracking Options:")
    print("1. Add mood entry")
    print("2. View recent moods")
    print("3. Mood analytics")
    print("4. Random mood")
    print("5. Mood suggestions")
    print("6. Quick mood check")
    
    try:
        choice = input("\nChoose an option (1-6): ").strip()
        
        if choice == "1":
            interactive_mood_entry()
        elif choice == "2":
            show_mood_list()
        elif choice == "3":
            show_mood_analytics()
        elif choice == "4":
            add_random_mood()
        elif choice == "5":
            show_mood_suggestions()
        elif choice == "6":
            quick_mood_check()
        else:
            print("Invalid choice")
    except KeyboardInterrupt:
        print("\n👋 Take care!")

def interactive_mood_entry():
    """Interactive mood entry with full details"""
    print("\n📝 Add Mood Entry")
    print("-" * 20)
    
    try:
        # Get mood suggestions
        suggestions = get_mood_suggestions(8)
        print("Mood suggestions:")
        for i, mood in enumerate(suggestions, 1):
            print(f"{i}. {mood}")
        print("9. Other (type your own)")
        
        choice = input("\nChoose a mood (1-9) or type directly: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= 8:
            mood = suggestions[int(choice) - 1]
        elif choice == "9":
            mood = input("Enter your mood: ").strip()
        else:
            mood = choice
        
        if not mood:
            print("No mood entered")
            return
        
        # Get additional details
        notes = input("Notes (optional): ").strip() or None
        
        intensity_str = input("Intensity 1-10 (optional): ").strip()
        intensity = None
        if intensity_str.isdigit() and 1 <= int(intensity_str) <= 10:
            intensity = int(intensity_str)
        
        triggers = input("Triggers (comma-separated, optional): ").strip()
        trigger_list = [t.strip() for t in triggers.split(",")] if triggers else None
        
        location = input("Location (optional): ").strip() or None
        
        # Add entry
        entry = add_mood_entry(mood, notes, intensity, trigger_list, location)
        
        print(f"\n✅ Mood entry added!")
        print(f"   Mood: {entry['mood']}")
        if entry['intensity']:
            print(f"   Intensity: {entry['intensity']}/10")
        if entry['notes']:
            print(f"   Notes: {entry['notes']}")
        
    except KeyboardInterrupt:
        print("\n👋 Take care!")

def show_mood_list(limit=10):
    """Show recent mood entries"""
    entries = get_mood_entries(limit=limit)
    
    if not entries:
        print("No mood entries found. Add your first mood!")
        return
    
    print(f"\n📋 Recent Mood Entries (last {len(entries)}):")
    print("-" * 50)
    
    for entry in entries:
        date_obj = datetime.datetime.fromisoformat(entry["date"])
        date_str = date_obj.strftime("%m-%d %H:%M")
        
        mood_display = entry["mood"]
        if entry.get("intensity"):
            mood_display += f" ({entry['intensity']}/10)"
        
        print(f"{date_str}: {mood_display}")
        if entry.get("notes"):
            print(f"         Notes: {entry['notes']}")
        if entry.get("triggers"):
            print(f"         Triggers: {', '.join(entry['triggers'])}")
        print()

def show_mood_analytics():
    """Show comprehensive mood analytics"""
    analytics = get_mood_analytics()
    
    if "message" in analytics:
        print(f"\n{analytics['message']}")
        return
    
    print("\n📊 Mood Analytics")
    print("=" * 30)
    
    print(f"Total entries: {analytics['total_entries']}")
    print(f"This week: {analytics['entries_this_week']}")
    print(f"This month: {analytics['entries_this_month']}")
    
    if analytics.get("average_intensity"):
        print(f"Average intensity: {analytics['average_intensity']}/10")
    
    print(f"Recent trend: {analytics['recent_trend']}")
    
    # Mood categories
    if analytics.get("mood_categories"):
        print("\n📈 Mood Categories:")
        for category, count in analytics["mood_categories"].items():
            percentage = (count / analytics["total_entries"]) * 100
            print(f"  {category.title()}: {count} ({percentage:.1f}%)")
    
    # Top moods
    if analytics.get("stats", {}).get("mood_distribution"):
        print("\n🏆 Most Common Moods:")
        sorted_moods = sorted(analytics["stats"]["mood_distribution"].items(), 
                            key=lambda x: x[1], reverse=True)
        for mood, count in sorted_moods[:5]:
            print(f"  {mood}: {count} times")

def add_random_mood():
    """Add a random mood entry"""
    mood = get_random_mood()
    entry = add_mood_entry(mood, notes="Random mood entry")
    print(f"🎲 Added random mood: {mood}")

def show_mood_suggestions():
    """Show mood suggestions"""
    suggestions = get_mood_suggestions(10)
    print("\n💡 Mood Suggestions:")
    for i, mood in enumerate(suggestions, 1):
        print(f"{i:2d}. {mood}")

def quick_mood_check():
    """Quick mood check similar to quick_actions"""
    print("\n🎯 Quick Mood Check")
    print("How are you feeling right now?")
    
    suggestions = get_mood_suggestions(5)
    for i, mood in enumerate(suggestions, 1):
        print(f"{i}. {mood}")
    
    try:
        choice = input("\nChoose (1-5) or type your mood: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= 5:
            mood = suggestions[int(choice) - 1]
        else:
            mood = choice
        
        if mood:
            entry = add_mood_entry(mood)
            print(f"✅ Logged: {mood}")
            
            # Quick analytics
            analytics = get_mood_analytics()
            if analytics.get("recent_trend"):
                print(f"Recent trend: {analytics['recent_trend']}")
        
    except KeyboardInterrupt:
        print("\n👋 Take care!")

if __name__ == "__main__":
    import sys
    args = sys.argv[1:] if len(sys.argv) > 1 else ["menu"]
    enhanced_mood_command(*args)
