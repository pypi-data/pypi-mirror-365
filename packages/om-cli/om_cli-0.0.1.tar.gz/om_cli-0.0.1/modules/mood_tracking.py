"""
Enhanced mood tracking module for om - inspired by Logbuch
"""

import json
import os
import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Import ASCII art utilities
try:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from ascii_art import *
    ASCII_AVAILABLE = True
except ImportError:
    ASCII_AVAILABLE = False

MOOD_FILE = os.path.expanduser("~/.om_moods.json")

class MoodCategory(Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    CHALLENGING = "challenging"
    COMPLEX = "complex"

@dataclass
class MoodEntry:
    mood: str
    category: str  # Changed from MoodCategory to str for JSON serialization
    intensity: int  # 1-10 scale
    notes: str
    date: str
    context: List[str]  # tags like 'work', 'home', 'exercise'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'mood': self.mood,
            'category': self.category,
            'intensity': self.intensity,
            'notes': self.notes,
            'date': self.date,
            'context': self.context
        }

class MoodTracker:
    def __init__(self):
        self.moods_by_category = {
            "positive": [
                "happy", "joyful", "excited", "content", "peaceful", "grateful", 
                "optimistic", "energetic", "confident", "relaxed", "inspired", 
                "motivated", "cheerful", "blissful", "euphoric", "serene",
                "accomplished", "proud", "satisfied", "delighted", "elated"
            ],
            "neutral": [
                "calm", "focused", "balanced", "steady", "neutral", "contemplative",
                "pensive", "reflective", "curious", "alert", "observant",
                "routine", "stable", "composed", "centered"
            ],
            "challenging": [
                "tired", "stressed", "anxious", "overwhelmed", "frustrated", 
                "sad", "melancholy", "worried", "restless", "confused", 
                "disappointed", "lonely", "irritated", "bored", "uncertain",
                "drained", "tense", "discouraged", "impatient", "scattered"
            ],
            "complex": [
                "nostalgic", "hopeful", "determined", "ambitious", "creative",
                "adventurous", "romantic", "philosophical", "introspective",
                "empathetic", "compassionate", "vulnerable", "conflicted",
                "bittersweet", "anticipatory", "wistful", "contemplative"
            ]
        }
    
    def log_mood(self, mood: str = None, intensity: int = 5, notes: str = "", context: List[str] = None):
        """Log a mood entry with enhanced tracking"""
        if not mood:
            mood = self.get_random_mood()
        
        # Determine category
        category = self._get_mood_category(mood)
        
        if context is None:
            context = []
        
        entry = MoodEntry(
            mood=mood,
            category=category,
            intensity=intensity,
            notes=notes,
            date=datetime.now().isoformat(),
            context=context
        )
        
        self._save_mood_entry(entry)
        self._display_mood_logged(entry)
        
        # Show insights if we have enough data
        self._show_quick_insights()
    
    def get_random_mood(self) -> str:
        """Get a random mood suggestion"""
        all_moods = []
        for moods in self.moods_by_category.values():
            all_moods.extend(moods)
        return random.choice(all_moods)
    
    def get_random_moods(self, count: int = 5) -> List[str]:
        """Get multiple random mood suggestions"""
        all_moods = []
        for moods in self.moods_by_category.values():
            all_moods.extend(moods)
        return random.sample(all_moods, min(count, len(all_moods)))
    
    def suggest_moods(self):
        """Interactive mood suggestion"""
        print("🎭 Not sure how you're feeling? Here are some suggestions:")
        print()
        
        for category in MoodCategory:
            moods = random.sample(self.moods_by_category[category], 3)
            emoji = self._get_category_emoji(category)
            print(f"{emoji} {category.value.title()}: {', '.join(moods)}")
        
        print()
        choice = input("Pick one, or type your own mood: ").strip().lower()
        
        if choice:
            # Get intensity
            try:
                intensity = int(input("Intensity (1-10): ") or "5")
                intensity = max(1, min(10, intensity))
            except ValueError:
                intensity = 5
            
            # Get notes
            notes = input("Any notes about this mood? (optional): ").strip()
            
            # Get context
            print("Context tags (work, home, exercise, social, etc.):")
            context_input = input("Tags (comma-separated): ").strip()
            context = [tag.strip() for tag in context_input.split(",") if tag.strip()]
            
            self.log_mood(choice, intensity, notes, context)
    
    def show_mood_trends(self, days: int = 7):
        """Show mood trends and analytics"""
        entries = self._load_mood_entries()
        
        if not entries:
            print("No mood entries found. Start tracking with 'om mood log'")
            return
        
        # Filter recent entries
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_entries = [
            entry for entry in entries 
            if datetime.fromisoformat(entry['date']) >= cutoff_date
        ]
        
        if not recent_entries:
            print(f"No mood entries in the last {days} days.")
            return
        
        print(f"📊 Mood Trends - Last {days} Days")
        print("=" * 40)
        
        # Category breakdown
        category_counts = {}
        intensity_sum = {}
        
        for entry in recent_entries:
            cat = entry['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
            intensity_sum[cat] = intensity_sum.get(cat, 0) + entry['intensity']
        
        print("\n🎭 Mood Categories:")
        for category, count in category_counts.items():
            avg_intensity = intensity_sum[category] / count
            emoji = self._get_category_emoji(MoodCategory(category))
            percentage = (count / len(recent_entries)) * 100
            print(f"{emoji} {category.title()}: {count} entries ({percentage:.1f}%) - Avg intensity: {avg_intensity:.1f}")
        
        # Most common moods
        mood_counts = {}
        for entry in recent_entries:
            mood = entry['mood']
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        
        print(f"\n🔥 Most Common Moods:")
        sorted_moods = sorted(mood_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for mood, count in sorted_moods:
            print(f"  {mood}: {count} times")
        
        # Context analysis
        context_counts = {}
        for entry in recent_entries:
            for context in entry.get('context', []):
                context_counts[context] = context_counts.get(context, 0) + 1
        
        if context_counts:
            print(f"\n🏷️ Common Contexts:")
            sorted_contexts = sorted(context_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            for context, count in sorted_contexts:
                print(f"  {context}: {count} times")
        
        # Simple mood chart
        self._show_mood_chart(recent_entries)
    
    def _show_mood_chart(self, entries: List[Dict]):
        """Show a simple ASCII mood chart"""
        print(f"\n📈 Mood Intensity Over Time:")
        
        # Group by day
        daily_moods = {}
        for entry in entries:
            day = datetime.fromisoformat(entry['date']).date()
            if day not in daily_moods:
                daily_moods[day] = []
            daily_moods[day].append(entry['intensity'])
        
        # Calculate daily averages
        daily_averages = {}
        for day, intensities in daily_moods.items():
            daily_averages[day] = sum(intensities) / len(intensities)
        
        # Sort by date
        sorted_days = sorted(daily_averages.items())
        
        # Create simple chart
        for day, avg_intensity in sorted_days[-7:]:  # Last 7 days
            bar_length = int(avg_intensity * 2)  # Scale to 20 chars max
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"{day.strftime('%m-%d')}: {bar} {avg_intensity:.1f}")
    
    def _get_mood_category(self, mood: str) -> MoodCategory:
        """Determine the category of a mood"""
        mood_lower = mood.lower()
        for category, moods in self.moods_by_category.items():
            if mood_lower in moods:
                return category
        return MoodCategory.NEUTRAL  # Default
    
    def _get_category_emoji(self, category: MoodCategory) -> str:
        """Get emoji for mood category"""
        emojis = {
            MoodCategory.POSITIVE: "😊",
            MoodCategory.NEUTRAL: "😐", 
            MoodCategory.CHALLENGING: "😔",
            MoodCategory.COMPLEX: "🤔"
        }
        return emojis.get(category, "🎭")
    
    def _save_mood_entry(self, entry: MoodEntry):
        """Save mood entry to file"""
        try:
            entries = self._load_mood_entries()
            entries.append(entry.to_dict())  # Use to_dict method instead of asdict
            
            with open(MOOD_FILE, 'w') as f:
                json.dump(entries, f, indent=2)
        except Exception as e:
            print(f"Could not save mood entry: {e}")
    
    def _load_mood_entries(self) -> List[Dict]:
        """Load mood entries from file"""
        if not os.path.exists(MOOD_FILE):
            return []
        
        try:
            with open(MOOD_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    
    def _display_mood_logged(self, entry: MoodEntry):
        """Display confirmation of logged mood"""
        emoji = self._get_category_emoji(entry.category)
        print(f"\n{emoji} Mood logged: {entry.mood}")
        print(f"   Category: {entry.category}")  # Removed .value since category is now a string
        print(f"   Intensity: {entry.intensity}/10")
        if entry.notes:
            print(f"   Notes: {entry.notes}")
        if entry.context:
            print(f"   Context: {', '.join(entry.context)}")
    
    def _show_quick_insights(self):
        """Show quick insights based on recent mood data"""
        entries = self._load_mood_entries()
        
        if len(entries) < 3:
            return
        
        # Get last 3 entries
        recent = entries[-3:]
        moods = [entry['mood'] for entry in recent]
        
        print(f"\n💡 Quick insight: Your recent moods have been {', '.join(moods)}")
        
        # Simple pattern detection
        categories = [entry['category'] for entry in recent]
        if all(cat == 'challenging' for cat in categories):
            print("   Consider trying a breathing exercise or meditation to help balance your mood.")
        elif all(cat == 'positive' for cat in categories):
            print("   You're on a positive streak! Great job maintaining good mental health.")


def mood_command(action: str = "log", **kwargs):
    """Main mood tracking command interface"""
    tracker = MoodTracker()
    
    if action == "log":
        mood = kwargs.get('mood')
        intensity = kwargs.get('intensity', 5)
        notes = kwargs.get('notes', '')
        context = kwargs.get('context', [])
        tracker.log_mood(mood, intensity, notes, context)
    
    elif action == "suggest":
        tracker.suggest_moods()
    
    elif action == "trends":
        days = kwargs.get('days', 7)
        tracker.show_mood_trends(days)
    
    elif action == "random":
        count = kwargs.get('count', 5)
        moods = tracker.get_random_moods(count)
        print("🎭 Random mood suggestions:")
        for mood in moods:
            category = tracker._get_mood_category(mood)
            emoji = tracker._get_category_emoji(category)
            print(f"  {emoji} {mood}")
    
    else:
        print(f"Unknown mood action: {action}")
        print("Available actions: log, suggest, trends, random")
