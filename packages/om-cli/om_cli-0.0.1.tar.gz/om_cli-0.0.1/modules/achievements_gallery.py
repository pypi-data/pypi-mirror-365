#!/usr/bin/env python3
"""
Beautiful Achievements Gallery for om Mental Health CLI
Celebrates user progress with stunning visuals and animations
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, Grid, ScrollableContainer
from textual.widgets import (
    Header, Footer, Button, Static, ProgressBar, Label, 
    Tabs, TabPane, Collapsible, Tree, ListView, ListItem
)
from textual.reactive import reactive, var
from textual.screen import Screen, ModalScreen
from textual.binding import Binding
from textual.timer import Timer
from textual.message import Message
from textual import events
import random

# Data paths
OM_DIR = os.path.expanduser("~/.om")
ACHIEVEMENTS_FILE = os.path.join(OM_DIR, "achievements.json")
WELLNESS_FILE = os.path.join(OM_DIR, "wellness_stats.json")
MOOD_FILE = os.path.join(OM_DIR, "mood_data.json")

os.makedirs(OM_DIR, exist_ok=True)

class AchievementStatus(Enum):
    LOCKED = "locked"
    IN_PROGRESS = "in_progress"
    UNLOCKED = "unlocked"
    MASTERED = "mastered"

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    category: str
    emoji: str
    status: AchievementStatus
    progress: int = 0
    max_progress: int = 1
    unlock_date: Optional[str] = None
    rarity: str = "common"  # common, rare, epic, legendary
    points: int = 10

class AchievementCard(Static):
    """Beautiful card displaying a single achievement"""
    
    def __init__(self, achievement: Achievement, **kwargs):
        super().__init__(**kwargs)
        self.achievement = achievement
        self.is_highlighted = False
        self.sparkle_timer: Optional[Timer] = None
    
    def on_mount(self) -> None:
        """Start sparkle animation for unlocked achievements"""
        if self.achievement.status == AchievementStatus.UNLOCKED:
            self.sparkle_timer = self.set_interval(2.0, self.sparkle_animation)
    
    def sparkle_animation(self) -> None:
        """Add sparkle effect to unlocked achievements"""
        sparkles = ["✨", "⭐", "🌟", "💫", "⚡"]
        sparkle = random.choice(sparkles)
        self.add_class("sparkle")
        self.set_timer(0.5, lambda: self.remove_class("sparkle"))
    
    def render(self) -> str:
        """Render the achievement card with beautiful styling"""
        a = self.achievement
        
        # Status styling
        if a.status == AchievementStatus.LOCKED:
            border_color = "dim"
            status_emoji = "🔒"
            status_text = "Locked"
            progress_color = "dim"
        elif a.status == AchievementStatus.IN_PROGRESS:
            border_color = "yellow"
            status_emoji = "🔄"
            status_text = "In Progress"
            progress_color = "yellow"
        elif a.status == AchievementStatus.UNLOCKED:
            border_color = "green"
            status_emoji = "✅"
            status_text = "Unlocked!"
            progress_color = "green"
        else:  # MASTERED
            border_color = "magenta"
            status_emoji = "👑"
            status_text = "Mastered!"
            progress_color = "magenta"
        
        # Rarity styling
        rarity_colors = {
            "common": "white",
            "rare": "blue",
            "epic": "magenta",
            "legendary": "gold"
        }
        rarity_color = rarity_colors.get(a.rarity, "white")
        
        # Progress bar
        if a.max_progress > 1:
            progress_percent = (a.progress / a.max_progress) * 100
            progress_bar = self.create_progress_bar(progress_percent, progress_color)
            progress_text = f"{a.progress}/{a.max_progress}"
        else:
            progress_bar = ""
            progress_text = ""
        
        # Unlock date
        unlock_info = ""
        if a.unlock_date:
            date_obj = datetime.fromisoformat(a.unlock_date)
            unlock_info = f"\n[dim]Unlocked: {date_obj.strftime('%b %d, %Y')}[/]"
        
        # Points display
        points_display = f"[bold {rarity_color}]{a.points} pts[/]"
        
        return f"""[{border_color}]╭─────────────────────────────────────╮[/]
[{border_color}]│[/] {a.emoji}  [bold]{a.name}[/] {status_emoji}
[{border_color}]│[/] 
[{border_color}]│[/] [dim]{a.description}[/]
[{border_color}]│[/] 
[{border_color}]│[/] Category: [cyan]{a.category}[/]
[{border_color}]│[/] Status: [{progress_color}]{status_text}[/] {points_display}
[{border_color}]│[/] {progress_bar}
[{border_color}]│[/] {progress_text}{unlock_info}
[{border_color}]╰─────────────────────────────────────╯[/]"""
    
    def create_progress_bar(self, percent: float, color: str) -> str:
        """Create a beautiful ASCII progress bar"""
        width = 30
        filled = int((percent / 100) * width)
        empty = width - filled
        
        bar = "█" * filled + "░" * empty
        return f"[{color}]{bar}[/] {percent:.0f}%"

class CategoryFilter(Static):
    """Filter achievements by category"""
    
    categories = reactive(["All", "Mood", "Breathing", "Gratitude", "Consistency", "Milestones", "Crisis Recovery"])
    selected_category = reactive("All")
    
    def render(self) -> str:
        """Render category filter buttons"""
        buttons = []
        for cat in self.categories:
            if cat == self.selected_category:
                buttons.append(f"[bold green]● {cat}[/]")
            else:
                buttons.append(f"[dim]○ {cat}[/]")
        
        return f"""[bold cyan]╭─── Filter by Category ───╮[/]
[bold cyan]│[/] {' '.join(buttons[:4])}
[bold cyan]│[/] {' '.join(buttons[4:])}
[bold cyan]╰───────────────────────────╯[/]"""

class StatsOverview(Static):
    """Overview of achievement statistics"""
    
    def __init__(self, achievements: List[Achievement], **kwargs):
        super().__init__(**kwargs)
        self.achievements = achievements
    
    def render(self) -> str:
        """Render achievement statistics"""
        total = len(self.achievements)
        unlocked = len([a for a in self.achievements if a.status == AchievementStatus.UNLOCKED])
        in_progress = len([a for a in self.achievements if a.status == AchievementStatus.IN_PROGRESS])
        locked = len([a for a in self.achievements if a.status == AchievementStatus.LOCKED])
        mastered = len([a for a in self.achievements if a.status == AchievementStatus.MASTERED])
        
        total_points = sum(a.points for a in self.achievements if a.status in [AchievementStatus.UNLOCKED, AchievementStatus.MASTERED])
        
        completion_percent = ((unlocked + mastered) / total) * 100 if total > 0 else 0
        
        # Level calculation based on points
        level = min(100, max(1, total_points // 100 + 1))
        level_progress = (total_points % 100)
        
        return f"""[bold magenta]╭─── Your Wellness Journey ───╮[/]
[bold magenta]│[/]                              [bold magenta]│[/]
[bold magenta]│[/]  🏆 Total: [yellow]{total}[/] achievements    [bold magenta]│[/]
[bold magenta]│[/]  ✅ Unlocked: [green]{unlocked}[/]             [bold magenta]│[/]
[bold magenta]│[/]  👑 Mastered: [magenta]{mastered}[/]             [bold magenta]│[/]
[bold magenta]│[/]  🔄 In Progress: [yellow]{in_progress}[/]         [bold magenta]│[/]
[bold magenta]│[/]  🔒 Locked: [dim]{locked}[/]               [bold magenta]│[/]
[bold magenta]│[/]                              [bold magenta]│[/]
[bold magenta]│[/]  ⭐ Level: [bold yellow]{level}[/]                [bold magenta]│[/]
[bold magenta]│[/]  💎 Points: [bold cyan]{total_points}[/]              [bold magenta]│[/]
[bold magenta]│[/]  📊 Completion: [bold green]{completion_percent:.1f}%[/]      [bold magenta]│[/]
[bold magenta]│[/]                              [bold magenta]│[/]
[bold magenta]╰──────────────────────────────╯[/]"""

class RecentUnlocks(Static):
    """Show recently unlocked achievements with celebration"""
    
    def __init__(self, achievements: List[Achievement], **kwargs):
        super().__init__(**kwargs)
        self.recent_achievements = self.get_recent_unlocks(achievements)
        self.celebration_timer: Optional[Timer] = None
    
    def get_recent_unlocks(self, achievements: List[Achievement]) -> List[Achievement]:
        """Get achievements unlocked in the last 7 days"""
        recent = []
        cutoff_date = datetime.now() - timedelta(days=7)
        
        for achievement in achievements:
            if (achievement.status in [AchievementStatus.UNLOCKED, AchievementStatus.MASTERED] 
                and achievement.unlock_date):
                unlock_date = datetime.fromisoformat(achievement.unlock_date)
                if unlock_date >= cutoff_date:
                    recent.append(achievement)
        
        return sorted(recent, key=lambda a: a.unlock_date, reverse=True)
    
    def on_mount(self) -> None:
        """Start celebration animation for recent unlocks"""
        if self.recent_achievements:
            self.celebration_timer = self.set_interval(1.5, self.celebrate)
    
    def celebrate(self) -> None:
        """Celebration animation"""
        celebrations = ["🎉", "🎊", "🌟", "✨", "🎈", "🎁", "🏆"]
        celebration = random.choice(celebrations)
        self.add_class("celebrate")
        self.set_timer(0.8, lambda: self.remove_class("celebrate"))
    
    def render(self) -> str:
        """Render recent unlocks with celebration"""
        if not self.recent_achievements:
            return f"""[bold yellow]╭─── Recent Unlocks (7 days) ───╮[/]
[bold yellow]│[/]                               [bold yellow]│[/]
[bold yellow]│[/]  No recent unlocks yet...     [bold yellow]│[/]
[bold yellow]│[/]  Keep up your wellness        [bold yellow]│[/]
[bold yellow]│[/]  practice! 💪                 [bold yellow]│[/]
[bold yellow]│[/]                               [bold yellow]│[/]
[bold yellow]╰─────────────────────────────────╯[/]"""
        
        recent_text = ""
        for i, achievement in enumerate(self.recent_achievements[:3]):  # Show top 3
            date_obj = datetime.fromisoformat(achievement.unlock_date)
            days_ago = (datetime.now() - date_obj).days
            
            if days_ago == 0:
                time_text = "Today! 🎉"
            elif days_ago == 1:
                time_text = "Yesterday ✨"
            else:
                time_text = f"{days_ago} days ago"
            
            recent_text += f"[bold yellow]│[/]  {achievement.emoji} [green]{achievement.name}[/]\n"
            recent_text += f"[bold yellow]│[/]     [dim]{time_text}[/]\n"
            if i < len(self.recent_achievements[:3]) - 1:
                recent_text += f"[bold yellow]│[/]\n"
        
        return f"""[bold yellow]╭─── Recent Unlocks (7 days) ───╮[/]
[bold yellow]│[/]                               [bold yellow]│[/]
{recent_text}[bold yellow]│[/]                               [bold yellow]│[/]
[bold yellow]╰─────────────────────────────────╯[/]"""

class AchievementsGallery(ScrollableContainer):
    """Main achievements gallery with filtering and beautiful display"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.achievements = self.load_achievements()
        self.filtered_achievements = self.achievements
        self.selected_category = "All"
    
    def compose(self) -> ComposeResult:
        """Compose the achievements gallery"""
        with Vertical():
            # Header with stats
            yield StatsOverview(self.achievements, id="stats_overview")
            
            # Recent unlocks celebration
            yield RecentUnlocks(self.achievements, id="recent_unlocks")
            
            # Category filter
            yield CategoryFilter(id="category_filter")
            
            # Achievement cards grid
            with Grid(id="achievements_grid"):
                for achievement in self.filtered_achievements:
                    yield AchievementCard(achievement, classes="achievement_card")
    
    def load_achievements(self) -> List[Achievement]:
        """Load achievements from file and generate based on user data"""
        # Load existing achievements
        try:
            with open(ACHIEVEMENTS_FILE, 'r') as f:
                achievements_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            achievements_data = {}
        
        # Load user stats to determine achievement progress
        user_stats = self.load_user_stats()
        
        # Define all possible achievements
        all_achievements = self.define_achievements(user_stats)
        
        # Update with saved data
        for achievement in all_achievements:
            if achievement.id in achievements_data:
                saved_data = achievements_data[achievement.id]
                achievement.status = AchievementStatus(saved_data.get('status', 'locked'))
                achievement.progress = saved_data.get('progress', 0)
                achievement.unlock_date = saved_data.get('unlock_date')
        
        return all_achievements
    
    def load_user_stats(self) -> Dict:
        """Load user statistics for achievement calculation"""
        stats = {}
        
        # Load wellness stats
        try:
            with open(WELLNESS_FILE, 'r') as f:
                stats.update(json.load(f))
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        # Load mood data
        try:
            with open(MOOD_FILE, 'r') as f:
                mood_data = json.load(f)
                stats['total_mood_entries'] = len(mood_data)
                
                # Calculate streaks
                if mood_data:
                    stats['current_streak'] = self.calculate_streak(mood_data)
                    stats['longest_streak'] = self.calculate_longest_streak(mood_data)
        except (FileNotFoundError, json.JSONDecodeError):
            stats['total_mood_entries'] = 0
            stats['current_streak'] = 0
            stats['longest_streak'] = 0
        
        return stats
    
    def calculate_streak(self, mood_data: List[Dict]) -> int:
        """Calculate current wellness streak"""
        if not mood_data:
            return 0
        
        # Simple streak calculation based on consecutive days with entries
        today = datetime.now().date()
        streak = 0
        
        for i in range(len(mood_data) - 1, -1, -1):
            entry_date = datetime.fromisoformat(mood_data[i]['timestamp']).date()
            expected_date = today - timedelta(days=streak)
            
            if entry_date == expected_date:
                streak += 1
            else:
                break
        
        return streak
    
    def calculate_longest_streak(self, mood_data: List[Dict]) -> int:
        """Calculate longest wellness streak"""
        if not mood_data:
            return 0
        
        # This is a simplified version - in reality you'd want more sophisticated streak tracking
        return max(7, len(mood_data) // 3)  # Placeholder calculation
    
    def define_achievements(self, stats: Dict) -> List[Achievement]:
        """Define all possible achievements with current progress"""
        achievements = []
        
        # Mood Tracking Achievements
        mood_entries = stats.get('total_mood_entries', 0)
        
        achievements.extend([
            Achievement(
                id="first_mood",
                name="First Steps",
                description="Log your first mood entry",
                category="Mood",
                emoji="🌱",
                status=AchievementStatus.UNLOCKED if mood_entries >= 1 else AchievementStatus.LOCKED,
                progress=min(1, mood_entries),
                max_progress=1,
                unlock_date=datetime.now().isoformat() if mood_entries >= 1 else None,
                rarity="common",
                points=10
            ),
            Achievement(
                id="mood_week",
                name="Weekly Tracker",
                description="Log your mood for 7 consecutive days",
                category="Mood",
                emoji="📅",
                status=self.get_status_from_progress(stats.get('current_streak', 0), 7),
                progress=min(7, stats.get('current_streak', 0)),
                max_progress=7,
                unlock_date=datetime.now().isoformat() if stats.get('current_streak', 0) >= 7 else None,
                rarity="rare",
                points=50
            ),
            Achievement(
                id="mood_month",
                name="Monthly Warrior",
                description="Maintain mood tracking for 30 days",
                category="Mood",
                emoji="🗓️",
                status=self.get_status_from_progress(stats.get('longest_streak', 0), 30),
                progress=min(30, stats.get('longest_streak', 0)),
                max_progress=30,
                unlock_date=datetime.now().isoformat() if stats.get('longest_streak', 0) >= 30 else None,
                rarity="epic",
                points=200
            )
        ])
        
        # Breathing Achievements
        breathing_sessions = stats.get('breathing_sessions', 0)
        
        achievements.extend([
            Achievement(
                id="first_breath",
                name="First Breath",
                description="Complete your first breathing exercise",
                category="Breathing",
                emoji="🫁",
                status=AchievementStatus.UNLOCKED if breathing_sessions >= 1 else AchievementStatus.LOCKED,
                progress=min(1, breathing_sessions),
                max_progress=1,
                unlock_date=datetime.now().isoformat() if breathing_sessions >= 1 else None,
                rarity="common",
                points=15
            ),
            Achievement(
                id="breathing_master",
                name="Breathing Master",
                description="Complete 50 breathing exercises",
                category="Breathing",
                emoji="🌬️",
                status=self.get_status_from_progress(breathing_sessions, 50),
                progress=min(50, breathing_sessions),
                max_progress=50,
                unlock_date=datetime.now().isoformat() if breathing_sessions >= 50 else None,
                rarity="epic",
                points=250
            )
        ])
        
        # Gratitude Achievements
        gratitude_entries = stats.get('gratitude_entries', 0)
        
        achievements.extend([
            Achievement(
                id="grateful_heart",
                name="Grateful Heart",
                description="Complete your first gratitude practice",
                category="Gratitude",
                emoji="🙏",
                status=AchievementStatus.UNLOCKED if gratitude_entries >= 1 else AchievementStatus.LOCKED,
                progress=min(1, gratitude_entries),
                max_progress=1,
                unlock_date=datetime.now().isoformat() if gratitude_entries >= 1 else None,
                rarity="common",
                points=20
            ),
            Achievement(
                id="thankful_soul",
                name="Thankful Soul",
                description="Practice gratitude 100 times",
                category="Gratitude",
                emoji="✨",
                status=self.get_status_from_progress(gratitude_entries, 100),
                progress=min(100, gratitude_entries),
                max_progress=100,
                unlock_date=datetime.now().isoformat() if gratitude_entries >= 100 else None,
                rarity="legendary",
                points=500
            )
        ])
        
        # Consistency Achievements
        current_streak = stats.get('current_streak', 0)
        
        achievements.extend([
            Achievement(
                id="streak_3",
                name="Getting Started",
                description="Maintain a 3-day wellness streak",
                category="Consistency",
                emoji="🔥",
                status=self.get_status_from_progress(current_streak, 3),
                progress=min(3, current_streak),
                max_progress=3,
                unlock_date=datetime.now().isoformat() if current_streak >= 3 else None,
                rarity="common",
                points=30
            ),
            Achievement(
                id="streak_30",
                name="Dedication",
                description="Maintain a 30-day wellness streak",
                category="Consistency",
                emoji="💪",
                status=self.get_status_from_progress(current_streak, 30),
                progress=min(30, current_streak),
                max_progress=30,
                unlock_date=datetime.now().isoformat() if current_streak >= 30 else None,
                rarity="epic",
                points=300
            ),
            Achievement(
                id="streak_100",
                name="Wellness Legend",
                description="Maintain a 100-day wellness streak",
                category="Consistency",
                emoji="👑",
                status=self.get_status_from_progress(current_streak, 100),
                progress=min(100, current_streak),
                max_progress=100,
                unlock_date=datetime.now().isoformat() if current_streak >= 100 else None,
                rarity="legendary",
                points=1000
            )
        ])
        
        # Milestone Achievements
        total_activities = mood_entries + breathing_sessions + gratitude_entries
        
        achievements.extend([
            Achievement(
                id="milestone_10",
                name="Explorer",
                description="Complete 10 wellness activities",
                category="Milestones",
                emoji="🗺️",
                status=self.get_status_from_progress(total_activities, 10),
                progress=min(10, total_activities),
                max_progress=10,
                unlock_date=datetime.now().isoformat() if total_activities >= 10 else None,
                rarity="common",
                points=40
            ),
            Achievement(
                id="milestone_100",
                name="Wellness Enthusiast",
                description="Complete 100 wellness activities",
                category="Milestones",
                emoji="🎯",
                status=self.get_status_from_progress(total_activities, 100),
                progress=min(100, total_activities),
                max_progress=100,
                unlock_date=datetime.now().isoformat() if total_activities >= 100 else None,
                rarity="rare",
                points=150
            ),
            Achievement(
                id="milestone_1000",
                name="Wellness Master",
                description="Complete 1000 wellness activities",
                category="Milestones",
                emoji="🏆",
                status=self.get_status_from_progress(total_activities, 1000),
                progress=min(1000, total_activities),
                max_progress=1000,
                unlock_date=datetime.now().isoformat() if total_activities >= 1000 else None,
                rarity="legendary",
                points=2000
            )
        ])
        
        return achievements
    
    def get_status_from_progress(self, current: int, target: int) -> AchievementStatus:
        """Determine achievement status from progress"""
        if current >= target:
            return AchievementStatus.UNLOCKED
        elif current > 0:
            return AchievementStatus.IN_PROGRESS
        else:
            return AchievementStatus.LOCKED
    
    def save_achievements(self) -> None:
        """Save achievements to file"""
        achievements_data = {}
        for achievement in self.achievements:
            achievements_data[achievement.id] = {
                'status': achievement.status.value,
                'progress': achievement.progress,
                'unlock_date': achievement.unlock_date
            }
        
        with open(ACHIEVEMENTS_FILE, 'w') as f:
            json.dump(achievements_data, f, indent=2)

class AchievementsApp(App):
    """Beautiful achievements gallery application"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #achievements_grid {
        layout: grid;
        grid-size: 2;
        grid-gutter: 1;
        margin: 1;
    }
    
    .achievement_card {
        margin: 1;
        padding: 1;
        border: solid $primary;
    }
    
    .achievement_card.sparkle {
        border: solid $success;
        background: $success 10%;
    }
    
    .achievement_card.celebrate {
        border: solid $warning;
        background: $warning 20%;
    }
    
    #stats_overview {
        margin: 1;
        padding: 1;
        text-align: center;
    }
    
    #recent_unlocks {
        margin: 1;
        padding: 1;
    }
    
    #recent_unlocks.celebrate {
        background: $success 15%;
    }
    
    #category_filter {
        margin: 1;
        padding: 1;
        text-align: center;
    }
    
    ScrollableContainer {
        height: 100%;
    }
    """
    
    TITLE = "🏆 om Achievements Gallery"
    SUB_TITLE = "Celebrating your mental wellness journey"
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("f", "filter", "Filter"),
        Binding("s", "save", "Save"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield AchievementsGallery(id="gallery")
        yield Footer()
    
    def action_refresh(self) -> None:
        """Refresh achievements data"""
        gallery = self.query_one("#gallery", AchievementsGallery)
        gallery.achievements = gallery.load_achievements()
        self.notify("🔄 Achievements refreshed!", timeout=2)
    
    def action_save(self) -> None:
        """Save achievements data"""
        gallery = self.query_one("#gallery", AchievementsGallery)
        gallery.save_achievements()
        self.notify("💾 Achievements saved!", timeout=2)
    
    def action_filter(self) -> None:
        """Toggle category filter"""
        self.notify("🔍 Category filtering coming soon!", timeout=2)
    
    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()

def main():
    """Main entry point for achievements gallery"""
    app = AchievementsApp()
    app.run()

if __name__ == "__main__":
    main()
