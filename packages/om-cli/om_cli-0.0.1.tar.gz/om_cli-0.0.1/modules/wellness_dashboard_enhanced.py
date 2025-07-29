#!/usr/bin/env python3
"""
Enhanced Wellness Dashboard for om - Inspired by Logbuch
Comprehensive wellness overview with rich visualization
"""

import os
import json
import datetime
from pathlib import Path
from typing import Dict, List, Optional

def get_data_dir():
    """Get om data directory"""
    home = Path.home()
    data_dir = home / ".om" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def load_wellness_data():
    """Load all wellness data"""
    data_dir = get_data_dir()
    
    data = {
        "mood_entries": [],
        "wellness_sessions": [],
        "achievements": [],
        "habits": [],
        "goals": [],
        "sleep_entries": [],
        "stress_levels": [],
        "gratitude_entries": []
    }
    
    # Load mood data
    mood_file = data_dir / "mood_entries.json"
    if mood_file.exists():
        try:
            with open(mood_file, 'r') as f:
                mood_data = json.load(f)
                data["mood_entries"] = mood_data.get("entries", [])
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    
    # Load wellness sessions (quick actions, etc.)
    sessions_file = data_dir / "wellness_sessions.json"
    if sessions_file.exists():
        try:
            with open(sessions_file, 'r') as f:
                data["wellness_sessions"] = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    
    # Load other data files similarly...
    for data_type in ["achievements", "habits", "goals", "sleep_entries", "stress_levels", "gratitude_entries"]:
        file_path = data_dir / f"{data_type}.json"
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    data[data_type] = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
    
    return data

def get_wellness_stats():
    """Get comprehensive wellness statistics"""
    data = load_wellness_data()
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    stats = {
        "today": today.strftime("%A, %B %d, %Y"),
        "mood": analyze_mood_data(data["mood_entries"]),
        "wellness_sessions": analyze_wellness_sessions(data["wellness_sessions"]),
        "achievements": analyze_achievements(data["achievements"]),
        "habits": analyze_habits(data["habits"]),
        "goals": analyze_goals(data["goals"]),
        "sleep": analyze_sleep_data(data["sleep_entries"]),
        "stress": analyze_stress_data(data["stress_levels"]),
        "gratitude": analyze_gratitude_data(data["gratitude_entries"]),
        "overall_wellness": calculate_overall_wellness(data)
    }
    
    return stats

def analyze_mood_data(mood_entries):
    """Analyze mood data for dashboard"""
    if not mood_entries:
        return {
            "status": "No mood data",
            "suggestion": "Start tracking your mood with: om qm"
        }
    
    today = datetime.date.today()
    week_entries = [e for e in mood_entries if 
                   datetime.datetime.fromisoformat(e["date"]).date() >= today - datetime.timedelta(days=7)]
    
    recent_entry = mood_entries[0] if mood_entries else None
    
    # Calculate mood trend
    if len(mood_entries) >= 5:
        recent_moods = mood_entries[:5]
        trend = calculate_mood_trend(recent_moods)
    else:
        trend = "stable"
    
    return {
        "total_entries": len(mood_entries),
        "entries_this_week": len(week_entries),
        "current_mood": recent_entry["mood"] if recent_entry else "Unknown",
        "last_logged": recent_entry["date"] if recent_entry else None,
        "trend": trend,
        "average_intensity": calculate_average_intensity(mood_entries)
    }

def analyze_wellness_sessions(sessions):
    """Analyze wellness session data"""
    if not sessions:
        return {
            "total_sessions": 0,
            "sessions_today": 0,
            "sessions_this_week": 0,
            "favorite_activity": "None",
            "suggestion": "Try a quick wellness action: om qb"
        }
    
    today = datetime.date.today()
    today_sessions = [s for s in sessions if 
                     datetime.datetime.fromisoformat(s.get("date", "")).date() == today]
    week_sessions = [s for s in sessions if 
                    datetime.datetime.fromisoformat(s.get("date", "")).date() >= today - datetime.timedelta(days=7)]
    
    # Find most common activity
    activity_counts = {}
    for session in sessions:
        activity = session.get("activity", "unknown")
        activity_counts[activity] = activity_counts.get(activity, 0) + 1
    
    favorite_activity = max(activity_counts.items(), key=lambda x: x[1])[0] if activity_counts else "None"
    
    return {
        "total_sessions": len(sessions),
        "sessions_today": len(today_sessions),
        "sessions_this_week": len(week_sessions),
        "favorite_activity": favorite_activity,
        "activity_distribution": activity_counts
    }

def analyze_achievements(achievements):
    """Analyze achievement data"""
    if not achievements:
        return {
            "total_unlocked": 0,
            "recent_achievements": [],
            "suggestion": "Complete wellness activities to unlock achievements!"
        }
    
    unlocked = [a for a in achievements if a.get("unlocked", False)]
    recent = sorted([a for a in unlocked if a.get("date")], 
                   key=lambda x: x["date"], reverse=True)[:3]
    
    return {
        "total_unlocked": len(unlocked),
        "total_available": len(achievements),
        "recent_achievements": recent,
        "completion_rate": (len(unlocked) / len(achievements)) * 100 if achievements else 0
    }

def analyze_habits(habits):
    """Analyze habit tracking data"""
    if not habits:
        return {
            "active_habits": 0,
            "completion_rate": 0,
            "suggestion": "Build healthy habits with: om habits"
        }
    
    active_habits = [h for h in habits if h.get("active", True)]
    
    # Calculate completion rates
    total_completions = sum(h.get("completions", 0) for h in active_habits)
    total_possible = sum(h.get("target_frequency", 1) for h in active_habits) * 7  # Weekly
    
    completion_rate = (total_completions / total_possible) * 100 if total_possible > 0 else 0
    
    return {
        "active_habits": len(active_habits),
        "total_habits": len(habits),
        "completion_rate": round(completion_rate, 1),
        "streak_info": get_habit_streaks(active_habits)
    }

def analyze_goals(goals):
    """Analyze goal data"""
    if not goals:
        return {
            "active_goals": 0,
            "completed_goals": 0,
            "suggestion": "Set wellness goals to track progress!"
        }
    
    active_goals = [g for g in goals if not g.get("completed", False)]
    completed_goals = [g for g in goals if g.get("completed", False)]
    
    # Calculate average progress
    avg_progress = sum(g.get("progress", 0) for g in active_goals) / len(active_goals) if active_goals else 0
    
    return {
        "active_goals": len(active_goals),
        "completed_goals": len(completed_goals),
        "total_goals": len(goals),
        "average_progress": round(avg_progress, 1),
        "next_goal": active_goals[0] if active_goals else None
    }

def analyze_sleep_data(sleep_entries):
    """Analyze sleep data"""
    if not sleep_entries:
        return {
            "status": "No sleep data",
            "suggestion": "Track your sleep with: om sleep"
        }
    
    recent_sleep = sleep_entries[:7] if len(sleep_entries) >= 7 else sleep_entries
    avg_hours = sum(e.get("hours", 0) for e in recent_sleep) / len(recent_sleep)
    
    last_entry = sleep_entries[0] if sleep_entries else None
    
    return {
        "last_sleep": last_entry.get("hours") if last_entry else None,
        "average_7_days": round(avg_hours, 1),
        "total_entries": len(sleep_entries),
        "sleep_quality": assess_sleep_quality(avg_hours)
    }

def analyze_stress_data(stress_entries):
    """Analyze stress level data"""
    if not stress_entries:
        return {
            "status": "No stress data",
            "current_level": "Unknown",
            "suggestion": "Monitor stress with wellness check-ins"
        }
    
    recent_entry = stress_entries[0] if stress_entries else None
    week_entries = stress_entries[:7] if len(stress_entries) >= 7 else stress_entries
    avg_stress = sum(e.get("level", 5) for e in week_entries) / len(week_entries) if week_entries else 5
    
    return {
        "current_level": recent_entry.get("level") if recent_entry else "Unknown",
        "average_week": round(avg_stress, 1),
        "trend": calculate_stress_trend(stress_entries[:10] if len(stress_entries) >= 10 else stress_entries)
    }

def analyze_gratitude_data(gratitude_entries):
    """Analyze gratitude practice data"""
    if not gratitude_entries:
        return {
            "total_entries": 0,
            "entries_this_week": 0,
            "suggestion": "Practice gratitude with: om qg"
        }
    
    today = datetime.date.today()
    week_entries = [e for e in gratitude_entries if 
                   datetime.datetime.fromisoformat(e.get("date", "")).date() >= today - datetime.timedelta(days=7)]
    
    return {
        "total_entries": len(gratitude_entries),
        "entries_this_week": len(week_entries),
        "last_entry": gratitude_entries[0].get("content", "") if gratitude_entries else None,
        "consistency": calculate_gratitude_consistency(gratitude_entries)
    }

def calculate_overall_wellness(data):
    """Calculate overall wellness score"""
    scores = []
    
    # Mood score (based on recent entries and trend)
    mood_entries = data["mood_entries"]
    if mood_entries:
        recent_intensities = [e.get("intensity", 5) for e in mood_entries[:7] if e.get("intensity")]
        if recent_intensities:
            mood_score = (sum(recent_intensities) / len(recent_intensities)) * 10
            scores.append(mood_score)
    
    # Activity score (based on wellness sessions)
    sessions = data["wellness_sessions"]
    if sessions:
        today = datetime.date.today()
        week_sessions = [s for s in sessions if 
                        datetime.datetime.fromisoformat(s.get("date", "")).date() >= today - datetime.timedelta(days=7)]
        activity_score = min(len(week_sessions) * 10, 100)  # Cap at 100
        scores.append(activity_score)
    
    # Habit score
    habits = data["habits"]
    if habits:
        active_habits = [h for h in habits if h.get("active", True)]
        if active_habits:
            total_completions = sum(h.get("completions", 0) for h in active_habits)
            total_possible = sum(h.get("target_frequency", 1) for h in active_habits) * 7
            habit_score = (total_completions / total_possible) * 100 if total_possible > 0 else 0
            scores.append(habit_score)
    
    # Sleep score
    sleep_entries = data["sleep_entries"]
    if sleep_entries:
        recent_sleep = sleep_entries[:7] if len(sleep_entries) >= 7 else sleep_entries
        avg_hours = sum(e.get("hours", 0) for e in recent_sleep) / len(recent_sleep)
        # Optimal sleep is 7-9 hours
        if 7 <= avg_hours <= 9:
            sleep_score = 100
        elif 6 <= avg_hours < 7 or 9 < avg_hours <= 10:
            sleep_score = 80
        else:
            sleep_score = 60
        scores.append(sleep_score)
    
    overall_score = sum(scores) / len(scores) if scores else 50
    return {
        "score": round(overall_score, 1),
        "level": get_wellness_level(overall_score),
        "components": len(scores),
        "suggestion": get_wellness_suggestion(overall_score)
    }

def display_wellness_dashboard():
    """Display comprehensive wellness dashboard"""
    stats = get_wellness_stats()
    
    print("🧘‍♀️ om Wellness Dashboard")
    print("=" * 60)
    print(f"📅 {stats['today']}")
    print()
    
    # Overall wellness score
    overall = stats["overall_wellness"]
    print(f"🌟 Overall Wellness: {overall['score']}/100 ({overall['level']})")
    print(f"   {overall['suggestion']}")
    print()
    
    # Mood section
    mood = stats["mood"]
    print("😊 Mood & Emotions:")
    if mood.get("current_mood") != "Unknown":
        print(f"   Current: {mood['current_mood']} (Trend: {mood['trend']})")
        print(f"   This week: {mood['entries_this_week']} entries")
        if mood.get("average_intensity"):
            print(f"   Avg intensity: {mood['average_intensity']}/10")
    else:
        print(f"   {mood.get('suggestion', 'No mood data')}")
    print()
    
    # Wellness activities
    sessions = stats["wellness_sessions"]
    print("🎯 Wellness Activities:")
    print(f"   Today: {sessions['sessions_today']} sessions")
    print(f"   This week: {sessions['sessions_this_week']} sessions")
    if sessions.get("favorite_activity") != "None":
        print(f"   Favorite: {sessions['favorite_activity']}")
    else:
        print(f"   {sessions.get('suggestion', '')}")
    print()
    
    # Achievements
    achievements = stats["achievements"]
    print("🏆 Achievements:")
    if achievements["total_unlocked"] > 0:
        print(f"   Unlocked: {achievements['total_unlocked']}/{achievements['total_available']}")
        print(f"   Completion: {achievements['completion_rate']:.1f}%")
        if achievements["recent_achievements"]:
            recent = achievements["recent_achievements"][0]
            print(f"   Latest: {recent.get('name', 'Achievement')}")
    else:
        print(f"   {achievements.get('suggestion', 'No achievements yet')}")
    print()
    
    # Habits
    habits = stats["habits"]
    print("📋 Habits:")
    if habits["active_habits"] > 0:
        print(f"   Active habits: {habits['active_habits']}")
        print(f"   Completion rate: {habits['completion_rate']}%")
    else:
        print(f"   {habits.get('suggestion', 'No active habits')}")
    print()
    
    # Goals
    goals = stats["goals"]
    print("🎯 Goals:")
    if goals["active_goals"] > 0:
        print(f"   Active: {goals['active_goals']} | Completed: {goals['completed_goals']}")
        print(f"   Average progress: {goals['average_progress']}%")
        if goals["next_goal"]:
            print(f"   Next: {goals['next_goal'].get('description', 'Goal')}")
    else:
        print(f"   {goals.get('suggestion', 'No active goals')}")
    print()
    
    # Sleep
    sleep = stats["sleep"]
    print("😴 Sleep:")
    if sleep.get("last_sleep"):
        print(f"   Last night: {sleep['last_sleep']} hours")
        print(f"   7-day average: {sleep['average_7_days']} hours")
        print(f"   Quality: {sleep['sleep_quality']}")
    else:
        print(f"   {sleep.get('suggestion', 'No sleep data')}")
    print()
    
    # Gratitude
    gratitude = stats["gratitude"]
    print("🙏 Gratitude:")
    if gratitude["total_entries"] > 0:
        print(f"   Total entries: {gratitude['total_entries']}")
        print(f"   This week: {gratitude['entries_this_week']}")
        print(f"   Consistency: {gratitude['consistency']}")
    else:
        print(f"   {gratitude.get('suggestion', 'No gratitude entries')}")
    print()
    
    # Quick actions
    print("⚡ Quick Actions:")
    print("   om qm          # Quick mood check")
    print("   om qb          # 2-minute breathing")
    print("   om qg          # Gratitude practice")
    print("   om coach       # AI coaching insight")
    print("   om gamify      # View achievements")

# Helper functions
def calculate_mood_trend(recent_moods):
    """Calculate mood trend from recent entries"""
    # Simplified trend calculation
    if len(recent_moods) < 3:
        return "stable"
    
    # This would need more sophisticated analysis
    return "stable"

def calculate_average_intensity(mood_entries):
    """Calculate average mood intensity"""
    intensities = [e.get("intensity") for e in mood_entries if e.get("intensity")]
    return round(sum(intensities) / len(intensities), 1) if intensities else None

def get_habit_streaks(habits):
    """Get habit streak information"""
    # Simplified streak calculation
    return {"longest": 0, "current": 0}

def assess_sleep_quality(avg_hours):
    """Assess sleep quality based on average hours"""
    if 7 <= avg_hours <= 9:
        return "Good"
    elif 6 <= avg_hours < 7 or 9 < avg_hours <= 10:
        return "Fair"
    else:
        return "Poor"

def calculate_stress_trend(stress_entries):
    """Calculate stress trend"""
    if len(stress_entries) < 3:
        return "stable"
    return "stable"  # Simplified

def calculate_gratitude_consistency(gratitude_entries):
    """Calculate gratitude practice consistency"""
    if len(gratitude_entries) < 7:
        return "Getting started"
    return "Good"  # Simplified

def get_wellness_level(score):
    """Get wellness level based on score"""
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Fair"
    else:
        return "Needs attention"

def get_wellness_suggestion(score):
    """Get wellness suggestion based on score"""
    if score >= 80:
        return "Keep up the great work! You're doing excellent."
    elif score >= 60:
        return "Good progress! Try adding more variety to your wellness routine."
    elif score >= 40:
        return "You're on the right track. Consider daily check-ins with om qm."
    else:
        return "Focus on basic wellness: mood tracking, breathing, and gratitude."

def wellness_dashboard_command(action="show"):
    """Wellness dashboard command"""
    if action == "show" or action == "display":
        display_wellness_dashboard()
    elif action == "summary":
        display_dashboard_summary()
    elif action == "export":
        export_dashboard_data()
    else:
        display_wellness_dashboard()

def display_dashboard_summary():
    """Display condensed dashboard summary"""
    stats = get_wellness_stats()
    overall = stats["overall_wellness"]
    
    print("📊 Wellness Summary")
    print("-" * 30)
    print(f"Overall Score: {overall['score']}/100 ({overall['level']})")
    print(f"Mood: {stats['mood'].get('current_mood', 'Unknown')}")
    print(f"Activities today: {stats['wellness_sessions']['sessions_today']}")
    print(f"Sleep average: {stats['sleep'].get('average_7_days', 'N/A')} hours")
    print(f"Active goals: {stats['goals']['active_goals']}")

def export_dashboard_data():
    """Export dashboard data"""
    stats = get_wellness_stats()
    export_file = get_data_dir() / f"dashboard_export_{datetime.date.today().isoformat()}.json"
    
    with open(export_file, 'w') as f:
        json.dump(stats, f, indent=2, default=str)
    
    print(f"✅ Dashboard data exported to: {export_file}")

if __name__ == "__main__":
    import sys
    args = sys.argv[1:] if len(sys.argv) > 1 else ["show"]
    wellness_dashboard_command(*args)
