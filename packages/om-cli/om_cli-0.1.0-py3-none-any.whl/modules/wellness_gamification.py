#!/usr/bin/env python3
"""
Wellness Gamification for om
Mental health achievement and progress tracking system
Adapted from logbuch gamification for wellness focus
"""

import datetime
import json
import os
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class AchievementType(Enum):
    MOOD_TRACKING = "mood_tracking"
    BREATHING_PRACTICE = "breathing_practice"
    MEDITATION = "meditation"
    GRATITUDE_PRACTICE = "gratitude_practice"
    CONSISTENCY = "consistency"
    MILESTONE = "milestone"
    SELF_CARE = "self_care"
    CRISIS_RECOVERY = "crisis_recovery"
    MINDFULNESS = "mindfulness"
    SOCIAL_CONNECTION = "social_connection"

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    icon: str
    type: AchievementType
    wellness_points: int
    rarity: str  # common, rare, epic, legendary
    unlocked: bool = False
    unlocked_at: Optional[datetime.datetime] = None
    progress: int = 0
    target: int = 1
    hidden: bool = False  # Hidden until unlocked

@dataclass
class WellnessStats:
    level: int = 1
    wellness_points: int = 0
    total_points: int = 0
    mood_entries: int = 0
    breathing_sessions: int = 0
    meditation_minutes: int = 0
    gratitude_entries: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    days_active: int = 0
    crisis_recoveries: int = 0
    self_care_actions: int = 0

@dataclass
class DailyChallenge:
    id: str
    title: str
    description: str
    challenge_type: str
    target: int
    progress: int = 0
    completed: bool = False
    date: datetime.date = None
    reward_points: int = 50

class WellnessGamification:
    def __init__(self):
        self.data_dir = os.path.expanduser("~/.om")
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.achievements_file = os.path.join(self.data_dir, "achievements.json")
        self.stats_file = os.path.join(self.data_dir, "wellness_stats.json")
        self.challenges_file = os.path.join(self.data_dir, "daily_challenges.json")
        
        self.achievements = self._load_achievements()
        self.stats = self._load_stats()
        self.daily_challenges = self._load_daily_challenges()
        
        # Initialize default achievements if none exist
        if not self.achievements:
            self._create_default_achievements()
    
    def _load_achievements(self) -> List[Achievement]:
        """Load achievements from storage"""
        if os.path.exists(self.achievements_file):
            try:
                with open(self.achievements_file, 'r') as f:
                    data = json.load(f)
                    return [self._dict_to_achievement(item) for item in data]
            except Exception:
                return []
        return []
    
    def _load_stats(self) -> WellnessStats:
        """Load wellness stats from storage"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
                    return WellnessStats(**data)
            except Exception:
                return WellnessStats()
        return WellnessStats()
    
    def _load_daily_challenges(self) -> List[DailyChallenge]:
        """Load daily challenges from storage"""
        if os.path.exists(self.challenges_file):
            try:
                with open(self.challenges_file, 'r') as f:
                    data = json.load(f)
                    challenges = []
                    for item in data:
                        if 'date' in item and item['date']:
                            item['date'] = datetime.datetime.fromisoformat(item['date']).date()
                        challenges.append(DailyChallenge(**item))
                    return challenges
            except Exception:
                return []
        return []
    
    def _save_achievements(self):
        """Save achievements to storage"""
        try:
            data = [self._achievement_to_dict(achievement) for achievement in self.achievements]
            with open(self.achievements_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving achievements: {e}")
    
    def _save_stats(self):
        """Save stats to storage"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(asdict(self.stats), f, indent=2)
        except Exception as e:
            print(f"Error saving stats: {e}")
    
    def _save_daily_challenges(self):
        """Save daily challenges to storage"""
        try:
            data = []
            for challenge in self.daily_challenges:
                challenge_dict = asdict(challenge)
                if challenge.date:
                    challenge_dict['date'] = challenge.date.isoformat()
                data.append(challenge_dict)
            
            with open(self.challenges_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving challenges: {e}")
    
    def _dict_to_achievement(self, data: dict) -> Achievement:
        """Convert dictionary to Achievement"""
        data['type'] = AchievementType(data['type'])
        if data.get('unlocked_at'):
            data['unlocked_at'] = datetime.datetime.fromisoformat(data['unlocked_at'])
        return Achievement(**data)
    
    def _achievement_to_dict(self, achievement: Achievement) -> dict:
        """Convert Achievement to dictionary"""
        data = asdict(achievement)
        data['type'] = achievement.type.value
        if achievement.unlocked_at:
            data['unlocked_at'] = achievement.unlocked_at.isoformat()
        return data
    
    def _create_default_achievements(self):
        """Create default wellness achievements"""
        default_achievements = [
            # Mood Tracking Achievements
            Achievement("first_mood", "First Steps", "Record your first mood entry", "🌱", 
                       AchievementType.MOOD_TRACKING, 10, "common", target=1),
            Achievement("mood_week", "Week of Awareness", "Track your mood for 7 days", "📊", 
                       AchievementType.MOOD_TRACKING, 50, "rare", target=7),
            Achievement("mood_month", "Monthly Mindfulness", "Track your mood for 30 days", "🗓️", 
                       AchievementType.MOOD_TRACKING, 200, "epic", target=30),
            Achievement("mood_100", "Century of Self-Awareness", "Record 100 mood entries", "💯", 
                       AchievementType.MOOD_TRACKING, 500, "legendary", target=100),
            
            # Breathing Practice Achievements
            Achievement("first_breath", "First Breath", "Complete your first breathing exercise", "🫁", 
                       AchievementType.BREATHING_PRACTICE, 15, "common", target=1),
            Achievement("breath_master", "Breath Master", "Complete 50 breathing sessions", "🧘‍♀️", 
                       AchievementType.BREATHING_PRACTICE, 250, "epic", target=50),
            Achievement("daily_breather", "Daily Breather", "Practice breathing for 7 consecutive days", "🌬️", 
                       AchievementType.BREATHING_PRACTICE, 100, "rare", target=7),
            
            # Gratitude Achievements
            Achievement("grateful_heart", "Grateful Heart", "Write your first gratitude entry", "🙏", 
                       AchievementType.GRATITUDE_PRACTICE, 10, "common", target=1),
            Achievement("gratitude_week", "Week of Gratitude", "Practice gratitude for 7 days", "✨", 
                       AchievementType.GRATITUDE_PRACTICE, 75, "rare", target=7),
            Achievement("thankful_soul", "Thankful Soul", "Write 100 gratitude entries", "🌟", 
                       AchievementType.GRATITUDE_PRACTICE, 300, "epic", target=100),
            
            # Consistency Achievements
            Achievement("streak_3", "Getting Started", "Maintain a 3-day wellness streak", "🔥", 
                       AchievementType.CONSISTENCY, 30, "common", target=3),
            Achievement("streak_7", "Week Warrior", "Maintain a 7-day wellness streak", "⚡", 
                       AchievementType.CONSISTENCY, 70, "rare", target=7),
            Achievement("streak_30", "Monthly Master", "Maintain a 30-day wellness streak", "🏆", 
                       AchievementType.CONSISTENCY, 300, "epic", target=30),
            Achievement("streak_100", "Centurion", "Maintain a 100-day wellness streak", "👑", 
                       AchievementType.CONSISTENCY, 1000, "legendary", target=100),
            
            # Self-Care Achievements
            Achievement("self_care_start", "Self-Care Starter", "Complete your first self-care action", "💚", 
                       AchievementType.SELF_CARE, 15, "common", target=1),
            Achievement("self_care_week", "Self-Care Week", "Practice self-care for 7 days", "🌸", 
                       AchievementType.SELF_CARE, 80, "rare", target=7),
            
            # Crisis Recovery Achievements
            Achievement("crisis_survivor", "Crisis Survivor", "Use crisis support tools", "🛡️", 
                       AchievementType.CRISIS_RECOVERY, 100, "rare", target=1, hidden=True),
            Achievement("recovery_champion", "Recovery Champion", "Complete 5 crisis recovery sessions", "🦋", 
                       AchievementType.CRISIS_RECOVERY, 500, "epic", target=5, hidden=True),
            
            # Milestone Achievements
            Achievement("level_5", "Rising Star", "Reach wellness level 5", "⭐", 
                       AchievementType.MILESTONE, 0, "rare", target=5),
            Achievement("level_10", "Wellness Warrior", "Reach wellness level 10", "🌟", 
                       AchievementType.MILESTONE, 0, "epic", target=10),
            Achievement("level_25", "Mindfulness Master", "Reach wellness level 25", "🏅", 
                       AchievementType.MILESTONE, 0, "legendary", target=25),
            
            # Special Hidden Achievements
            Achievement("night_owl", "Night Owl", "Use om after midnight", "🦉", 
                       AchievementType.MINDFULNESS, 25, "rare", target=1, hidden=True),
            Achievement("early_bird", "Early Bird", "Use om before 6 AM", "🐦", 
                       AchievementType.MINDFULNESS, 25, "rare", target=1, hidden=True),
            Achievement("weekend_warrior", "Weekend Warrior", "Practice wellness on weekends", "🏖️", 
                       AchievementType.CONSISTENCY, 50, "rare", target=2, hidden=True),
        ]
        
        self.achievements = default_achievements
        self._save_achievements()
    
    def record_mood_entry(self):
        """Record a mood entry and update achievements"""
        self.stats.mood_entries += 1
        self._update_daily_activity()
        self._check_achievements("mood_entry")
        self._save_stats()
    
    def record_breathing_session(self, duration_minutes: int = 5):
        """Record a breathing session"""
        self.stats.breathing_sessions += 1
        self._update_daily_activity()
        self._check_achievements("breathing_session")
        self._save_stats()
    
    def record_meditation_session(self, duration_minutes: int):
        """Record a meditation session"""
        self.stats.meditation_minutes += duration_minutes
        self._update_daily_activity()
        self._check_achievements("meditation_session")
        self._save_stats()
    
    def record_gratitude_entry(self):
        """Record a gratitude entry"""
        self.stats.gratitude_entries += 1
        self._update_daily_activity()
        self._check_achievements("gratitude_entry")
        self._save_stats()
    
    def record_self_care_action(self):
        """Record a self-care action"""
        self.stats.self_care_actions += 1
        self._update_daily_activity()
        self._check_achievements("self_care_action")
        self._save_stats()
    
    def record_crisis_recovery(self):
        """Record use of crisis recovery tools"""
        self.stats.crisis_recoveries += 1
        self._check_achievements("crisis_recovery")
        self._save_stats()
    
    def _update_daily_activity(self):
        """Update daily activity and streak"""
        # This is a simplified version - in reality you'd track daily activity more precisely
        self.stats.current_streak += 1
        if self.stats.current_streak > self.stats.longest_streak:
            self.stats.longest_streak = self.stats.current_streak
        
        self.stats.days_active += 1
    
    def _check_achievements(self, action_type: str):
        """Check and unlock achievements based on actions"""
        newly_unlocked = []
        
        for achievement in self.achievements:
            if achievement.unlocked:
                continue
            
            # Update progress based on action type and achievement type
            if action_type == "mood_entry" and achievement.type == AchievementType.MOOD_TRACKING:
                if achievement.id == "first_mood":
                    achievement.progress = 1
                elif achievement.id == "mood_week":
                    achievement.progress = min(self.stats.mood_entries, 7)
                elif achievement.id == "mood_month":
                    achievement.progress = min(self.stats.mood_entries, 30)
                elif achievement.id == "mood_100":
                    achievement.progress = min(self.stats.mood_entries, 100)
            
            elif action_type == "breathing_session" and achievement.type == AchievementType.BREATHING_PRACTICE:
                if achievement.id == "first_breath":
                    achievement.progress = 1
                elif achievement.id == "breath_master":
                    achievement.progress = min(self.stats.breathing_sessions, 50)
                elif achievement.id == "daily_breather":
                    achievement.progress = min(self.stats.current_streak, 7)
            
            elif action_type == "gratitude_entry" and achievement.type == AchievementType.GRATITUDE_PRACTICE:
                if achievement.id == "grateful_heart":
                    achievement.progress = 1
                elif achievement.id == "gratitude_week":
                    achievement.progress = min(self.stats.gratitude_entries, 7)
                elif achievement.id == "thankful_soul":
                    achievement.progress = min(self.stats.gratitude_entries, 100)
            
            elif action_type == "self_care_action" and achievement.type == AchievementType.SELF_CARE:
                if achievement.id == "self_care_start":
                    achievement.progress = 1
                elif achievement.id == "self_care_week":
                    achievement.progress = min(self.stats.self_care_actions, 7)
            
            elif action_type == "crisis_recovery" and achievement.type == AchievementType.CRISIS_RECOVERY:
                if achievement.id == "crisis_survivor":
                    achievement.progress = 1
                elif achievement.id == "recovery_champion":
                    achievement.progress = min(self.stats.crisis_recoveries, 5)
            
            # Check consistency achievements
            if achievement.type == AchievementType.CONSISTENCY:
                if achievement.id == "streak_3":
                    achievement.progress = min(self.stats.current_streak, 3)
                elif achievement.id == "streak_7":
                    achievement.progress = min(self.stats.current_streak, 7)
                elif achievement.id == "streak_30":
                    achievement.progress = min(self.stats.current_streak, 30)
                elif achievement.id == "streak_100":
                    achievement.progress = min(self.stats.current_streak, 100)
            
            # Check if achievement is unlocked
            if achievement.progress >= achievement.target and not achievement.unlocked:
                achievement.unlocked = True
                achievement.unlocked_at = datetime.datetime.now()
                self.stats.wellness_points += achievement.wellness_points
                self.stats.total_points += achievement.wellness_points
                newly_unlocked.append(achievement)
        
        # Check level achievements
        new_level = self._calculate_level()
        if new_level > self.stats.level:
            self.stats.level = new_level
            # Check level-based achievements
            for achievement in self.achievements:
                if achievement.type == AchievementType.MILESTONE and not achievement.unlocked:
                    if ((achievement.id == "level_5" and new_level >= 5) or
                        (achievement.id == "level_10" and new_level >= 10) or
                        (achievement.id == "level_25" and new_level >= 25)):
                        achievement.unlocked = True
                        achievement.unlocked_at = datetime.datetime.now()
                        achievement.progress = new_level
                        newly_unlocked.append(achievement)
        
        # Check time-based hidden achievements
        now = datetime.datetime.now()
        if now.hour >= 0 and now.hour < 6:  # Early bird
            early_bird = next((a for a in self.achievements if a.id == "early_bird"), None)
            if early_bird and not early_bird.unlocked:
                early_bird.progress = 1
                early_bird.unlocked = True
                early_bird.unlocked_at = now
                self.stats.wellness_points += early_bird.wellness_points
                newly_unlocked.append(early_bird)
        
        elif now.hour >= 0 and now.hour < 6:  # Night owl
            night_owl = next((a for a in self.achievements if a.id == "night_owl"), None)
            if night_owl and not night_owl.unlocked:
                night_owl.progress = 1
                night_owl.unlocked = True
                night_owl.unlocked_at = now
                self.stats.wellness_points += night_owl.wellness_points
                newly_unlocked.append(night_owl)
        
        if newly_unlocked:
            self._save_achievements()
            self._show_achievement_notifications(newly_unlocked)
    
    def _calculate_level(self) -> int:
        """Calculate wellness level based on total points"""
        # Level formula: level = sqrt(total_points / 100) + 1
        import math
        return int(math.sqrt(self.stats.total_points / 100)) + 1
    
    def _show_achievement_notifications(self, achievements: List[Achievement]):
        """Show notifications for newly unlocked achievements"""
        for achievement in achievements:
            rarity_emoji = {
                "common": "🥉",
                "rare": "🥈", 
                "epic": "🥇",
                "legendary": "👑"
            }
            
            print(f"\n🎉 ACHIEVEMENT UNLOCKED! {rarity_emoji.get(achievement.rarity, '🏆')}")
            print(f"{achievement.icon} {achievement.name}")
            print(f"   {achievement.description}")
            print(f"   +{achievement.wellness_points} wellness points!")
            print(f"   Rarity: {achievement.rarity.title()}")
    
    def generate_daily_challenge(self) -> DailyChallenge:
        """Generate a daily challenge"""
        today = datetime.date.today()
        
        # Check if we already have a challenge for today
        existing = next((c for c in self.daily_challenges if c.date == today), None)
        if existing:
            return existing
        
        # Generate new challenge
        challenges = [
            DailyChallenge("mood_3x", "Triple Check", "Check your mood 3 times today", "mood_check", 3, 0, False, today, 30),
            DailyChallenge("breathe_2x", "Breathing Buddy", "Complete 2 breathing exercises", "breathing", 2, 0, False, today, 40),
            DailyChallenge("gratitude_5", "Gratitude Five", "List 5 things you're grateful for", "gratitude", 5, 0, False, today, 50),
            DailyChallenge("mindful_moments", "Mindful Moments", "Take 3 mindful moments throughout the day", "mindfulness", 3, 0, False, today, 35),
            DailyChallenge("self_care_act", "Self-Care Sunday", "Perform one act of self-care", "self_care", 1, 0, False, today, 25),
        ]
        
        # Select challenge based on user's patterns and day of week
        if today.weekday() == 6:  # Sunday
            challenge = next((c for c in challenges if "Self-Care" in c.title), random.choice(challenges))
        else:
            challenge = random.choice(challenges)
        
        self.daily_challenges.append(challenge)
        self._save_daily_challenges()
        
        return challenge
    
    def update_daily_challenge_progress(self, challenge_type: str, amount: int = 1):
        """Update progress on today's daily challenge"""
        today = datetime.date.today()
        challenge = next((c for c in self.daily_challenges if c.date == today), None)
        
        if challenge and challenge.challenge_type == challenge_type and not challenge.completed:
            challenge.progress = min(challenge.progress + amount, challenge.target)
            
            if challenge.progress >= challenge.target and not challenge.completed:
                challenge.completed = True
                self.stats.wellness_points += challenge.reward_points
                self.stats.total_points += challenge.reward_points
                print(f"\n🎯 DAILY CHALLENGE COMPLETED!")
                print(f"   {challenge.title}: {challenge.description}")
                print(f"   +{challenge.reward_points} wellness points!")
            
            self._save_daily_challenges()
            self._save_stats()
    
    def get_progress_summary(self) -> dict:
        """Get overall progress summary"""
        total_achievements = len(self.achievements)
        unlocked_achievements = len([a for a in self.achievements if a.unlocked])
        
        return {
            "level": self.stats.level,
            "wellness_points": self.stats.wellness_points,
            "total_points": self.stats.total_points,
            "achievements_unlocked": unlocked_achievements,
            "total_achievements": total_achievements,
            "achievement_percentage": (unlocked_achievements / total_achievements) * 100,
            "current_streak": self.stats.current_streak,
            "longest_streak": self.stats.longest_streak,
            "mood_entries": self.stats.mood_entries,
            "breathing_sessions": self.stats.breathing_sessions,
            "gratitude_entries": self.stats.gratitude_entries,
            "days_active": self.stats.days_active
        }

def run(args=None):
    """Main function to run wellness gamification"""
    gamification = WellnessGamification()
    
    if not args or args[0] == "status":
        # Show gamification status
        summary = gamification.get_progress_summary()
        print(f"\n🎮 Wellness Progress")
        print("=" * 40)
        print(f"Level: {summary['level']} ⭐")
        print(f"Wellness Points: {summary['wellness_points']} 💎")
        print(f"Current Streak: {summary['current_streak']} days 🔥")
        print(f"Achievements: {summary['achievements_unlocked']}/{summary['total_achievements']} ({summary['achievement_percentage']:.1f}%) 🏆")
        print()
        print("📊 Activity Summary:")
        print(f"  Mood entries: {summary['mood_entries']}")
        print(f"  Breathing sessions: {summary['breathing_sessions']}")
        print(f"  Gratitude entries: {summary['gratitude_entries']}")
        print(f"  Days active: {summary['days_active']}")
    
    elif args[0] == "achievements":
        # Show achievements
        unlocked = [a for a in gamification.achievements if a.unlocked and not a.hidden]
        locked = [a for a in gamification.achievements if not a.unlocked and not a.hidden]
        
        if unlocked:
            print("\n🏆 Unlocked Achievements")
            print("=" * 40)
            for achievement in unlocked:
                rarity_color = {"common": "🥉", "rare": "🥈", "epic": "🥇", "legendary": "👑"}
                print(f"{rarity_color.get(achievement.rarity, '🏆')} {achievement.icon} {achievement.name}")
                print(f"   {achievement.description}")
                print(f"   +{achievement.wellness_points} points | {achievement.rarity.title()}")
                if achievement.unlocked_at:
                    print(f"   Unlocked: {achievement.unlocked_at.strftime('%Y-%m-%d')}")
                print()
        
        if locked:
            print("🔒 Locked Achievements")
            print("=" * 40)
            for achievement in locked[:10]:  # Show first 10 locked achievements
                progress_bar = "█" * int((achievement.progress / achievement.target) * 10)
                progress_bar += "░" * (10 - len(progress_bar))
                print(f"🔒 {achievement.icon} {achievement.name}")
                print(f"   {achievement.description}")
                print(f"   Progress: [{progress_bar}] {achievement.progress}/{achievement.target}")
                print(f"   Reward: {achievement.wellness_points} points | {achievement.rarity.title()}")
                print()
    
    elif args[0] == "challenge":
        # Show daily challenge
        challenge = gamification.generate_daily_challenge()
        progress_bar = "█" * int((challenge.progress / challenge.target) * 10)
        progress_bar += "░" * (10 - len(progress_bar))
        
        print(f"\n🎯 Daily Challenge - {challenge.date}")
        print("=" * 40)
        print(f"🏅 {challenge.title}")
        print(f"   {challenge.description}")
        print(f"   Progress: [{progress_bar}] {challenge.progress}/{challenge.target}")
        print(f"   Reward: {challenge.reward_points} wellness points")
        
        if challenge.completed:
            print("   ✅ COMPLETED!")
        else:
            print(f"   Keep going! You need {challenge.target - challenge.progress} more.")
    
    elif args[0] == "leaderboard":
        # Show personal leaderboard/stats
        summary = gamification.get_progress_summary()
        print("\n📈 Personal Wellness Leaderboard")
        print("=" * 40)
        print(f"🥇 Longest Streak: {summary['longest_streak']} days")
        print(f"🥈 Total Mood Entries: {summary['mood_entries']}")
        print(f"🥉 Total Breathing Sessions: {summary['breathing_sessions']}")
        print(f"🏅 Total Gratitude Entries: {summary['gratitude_entries']}")
        print(f"⭐ Wellness Level: {summary['level']}")
        print(f"💎 Total Points Earned: {summary['total_points']}")
    
    else:
        print("\n🎮 Wellness Gamification")
        print("=" * 30)
        print("Available commands:")
        print("  om gamify status       - Show progress overview")
        print("  om gamify achievements - View achievements")
        print("  om gamify challenge    - View daily challenge")
        print("  om gamify leaderboard  - Personal stats leaderboard")

if __name__ == "__main__":
    run()
