#!/usr/bin/env python3
"""
Smart Suggestions Engine for om - Context-aware mental health recommendations
"""

import os
import json
from datetime import datetime, timedelta
import random

def get_user_data_file():
    """Get path to user data file"""
    home_dir = os.path.expanduser("~")
    om_dir = os.path.join(home_dir, ".om")
    os.makedirs(om_dir, exist_ok=True)
    return os.path.join(om_dir, "user_data.json")

def load_user_data():
    """Load user data from file"""
    try:
        with open(get_user_data_file(), 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "last_mood": None,
            "last_mood_time": None,
            "favorite_actions": {},
            "usage_patterns": {},
            "preferences": {}
        }

def save_user_data(data):
    """Save user data to file"""
    try:
        with open(get_user_data_file(), 'w') as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass  # Fail silently if can't save

def get_time_based_suggestions():
    """Get suggestions based on current time"""
    hour = datetime.now().hour
    day_of_week = datetime.now().weekday()  # 0=Monday, 6=Sunday
    
    # Weekend vs weekday suggestions
    is_weekend = day_of_week >= 5
    
    if 5 <= hour < 9:  # Morning
        if is_weekend:
            return [
                "🌅 Weekend morning! Try: om qg (start with gratitude)",
                "☕ Slow start: om qc (gentle calming)",
                "🧘 Weekend meditation: om meditate (longer session)"
            ]
        else:
            return [
                "🌅 Good morning! Try: om qm (quick mood check)",
                "☕ Energize your day: om qe (energy boost)",
                "🧘 Center yourself: om qf (focus for the day ahead)"
            ]
    elif 9 <= hour < 12:  # Late morning
        return [
            "☀️ Mid-morning boost: om qf (refocus your attention)",
            "💪 Physical reset: om qs (quick stretch break)",
            "🎯 Productivity: om qm (check your energy levels)"
        ]
    elif 12 <= hour < 14:  # Lunch
        return [
            "🍽️ Lunch break wellness: om qm (midday check-in)",
            "💪 Recharge: om qs (stretch those muscles)",
            "🧘 Mindful break: om qb (breathing reset)"
        ]
    elif 14 <= hour < 17:  # Afternoon
        return [
            "🌤️ Afternoon focus: om qf (beat the afternoon slump)",
            "⚡ Energy boost: om qe (re-energize)",
            "🧘 Mindful moment: om qgr (grounding technique)"
        ]
    elif 17 <= hour < 20:  # Evening
        return [
            "🌆 Transition time: om qr (complete day reset)",
            "📝 Reflect: om qch (comprehensive check-in)",
            "🙏 Evening gratitude: om qg (appreciate your day)"
        ]
    elif 20 <= hour < 23:  # Night
        return [
            "🌙 Wind down: om qc (progressive relaxation)",
            "😴 Prepare for rest: om qb (calming breathing)",
            "🧘 Evening meditation: om meditate (peaceful session)"
        ]
    else:  # Late night/early morning
        return [
            "🌃 Late night support: om rescue (if you need help)",
            "😰 Can't sleep?: om insomnia (sleep support)",
            "🫁 Calm your mind: om qc (deep relaxation)"
        ]

def get_mood_based_suggestions(mood_level):
    """Get suggestions based on recent mood"""
    if mood_level <= 2:  # Struggling
        return [
            "🆘 Immediate support: om rescue (crisis resources)",
            "🌍 Ground yourself: om qgr (5-4-3-2-1 technique)",
            "💪 Gentle support: om qa (positive affirmations)",
            "🫁 Breathe through it: om qb (calming breathing)"
        ]
    elif mood_level <= 4:  # Not great/challenging
        return [
            "🌱 Gentle care: om qc (progressive relaxation)",
            "💪 Build strength: om qa (affirmations)",
            "🧘 Find center: om qgr (grounding)",
            "🙏 Find positives: om qg (gratitude practice)"
        ]
    elif mood_level <= 6:  # Okay/neutral
        return [
            "⚡ Boost energy: om qe (energy techniques)",
            "🎯 Sharpen focus: om qf (attention reset)",
            "💪 Physical care: om qs (stretch break)",
            "🧘 Mindful moment: om qb (breathing)"
        ]
    else:  # Good/great
        return [
            "🌟 Maintain momentum: om qf (stay focused)",
            "🙏 Celebrate: om qg (gratitude practice)",
            "💪 Physical wellness: om qs (energizing stretch)",
            "🧘 Mindful appreciation: om qch (check-in)"
        ]

def get_usage_based_suggestions():
    """Get suggestions based on usage patterns"""
    user_data = load_user_data()
    favorite_actions = user_data.get("favorite_actions", {})
    
    if not favorite_actions:
        return [
            "🚀 Try something new: om qa (positive affirmations)",
            "🌱 Explore: om qgr (grounding technique)",
            "💪 Discover: om qe (energy boost methods)"
        ]
    
    # Suggest variety if user has favorites
    most_used = max(favorite_actions.items(), key=lambda x: x[1])[0] if favorite_actions else None
    
    suggestions = []
    if most_used == "breathe":
        suggestions.extend([
            "🔄 Try variety: om qc (progressive relaxation)",
            "🌱 Expand practice: om qgr (grounding technique)"
        ])
    elif most_used == "mood":
        suggestions.extend([
            "📊 Deep dive: om qch (complete check-in)",
            "🌱 Build on awareness: om qa (affirmations)"
        ])
    else:
        suggestions.extend([
            "🔄 Mix it up: om qr (complete reset)",
            "🌟 Try popular: om qb (breathing exercise)"
        ])
    
    return suggestions

def get_smart_suggestions():
    """Get comprehensive smart suggestions"""
    user_data = load_user_data()
    suggestions = []
    
    # Time-based suggestions (always include)
    suggestions.extend(get_time_based_suggestions())
    
    # Mood-based suggestions if recent mood available
    last_mood = user_data.get("last_mood")
    last_mood_time = user_data.get("last_mood_time")
    
    if last_mood and last_mood_time:
        # Only use mood suggestions if mood was logged recently (within 4 hours)
        mood_time = datetime.fromisoformat(last_mood_time)
        if datetime.now() - mood_time < timedelta(hours=4):
            mood_suggestions = get_mood_based_suggestions(last_mood)
            suggestions.extend(mood_suggestions[:2])  # Add top 2 mood suggestions
    
    # Usage-based suggestions
    usage_suggestions = get_usage_based_suggestions()
    suggestions.extend(usage_suggestions[:1])  # Add top usage suggestion
    
    # Remove duplicates while preserving order
    seen = set()
    unique_suggestions = []
    for suggestion in suggestions:
        if suggestion not in seen:
            seen.add(suggestion)
            unique_suggestions.append(suggestion)
    
    return unique_suggestions[:4]  # Return top 4 suggestions

def record_action_usage(action):
    """Record that user used an action"""
    user_data = load_user_data()
    favorite_actions = user_data.get("favorite_actions", {})
    favorite_actions[action] = favorite_actions.get(action, 0) + 1
    user_data["favorite_actions"] = favorite_actions
    save_user_data(user_data)

def record_mood(mood_level):
    """Record user's mood"""
    user_data = load_user_data()
    user_data["last_mood"] = mood_level
    user_data["last_mood_time"] = datetime.now().isoformat()
    save_user_data(user_data)

def get_encouragement_message():
    """Get a random encouragement message"""
    messages = [
        "🌟 You're taking great care of your mental health!",
        "💪 Every small step counts toward wellness!",
        "🌱 Your mindfulness practice is growing stronger!",
        "✨ You're building healthy habits one action at a time!",
        "🧘‍♀️ Taking time for yourself is an act of self-love!",
        "🌈 Your mental health journey is uniquely yours!",
        "💝 You deserve this moment of self-care!",
        "🚀 You're developing powerful coping skills!",
        "🌸 Each practice session makes you more resilient!",
        "⭐ You're investing in your most important relationship - with yourself!"
    ]
    return random.choice(messages)

if __name__ == "__main__":
    # Test the suggestions
    print("🧠 Smart Suggestions Test")
    print("=" * 30)
    suggestions = get_smart_suggestions()
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")
    print(f"\n{get_encouragement_message()}")
