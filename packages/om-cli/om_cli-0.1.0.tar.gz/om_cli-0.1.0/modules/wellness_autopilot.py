#!/usr/bin/env python3
"""
Wellness Autopilot for om
Automated mental health and wellness task management
Adapted from logbuch autopilot for mental health focus
"""

import datetime
import json
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import random

class AutopilotMode(Enum):
    FULL_AUTO = "full_auto"          # Complete automation
    ASSISTED = "assisted"            # Suggestions with confirmation
    MANUAL = "manual"                # User-controlled
    LEARNING = "learning"            # Learning user patterns

class WellnessTaskType(Enum):
    BREATHING = "breathing"
    MEDITATION = "meditation"
    MOOD_CHECK = "mood_check"
    GRATITUDE = "gratitude"
    PHYSICAL_CARE = "physical_care"
    SOCIAL_CONNECTION = "social_connection"
    CRISIS_PREVENTION = "crisis_prevention"
    SELF_REFLECTION = "self_reflection"

@dataclass
class WellnessTask:
    id: str
    title: str
    description: str
    task_type: WellnessTaskType
    priority: str  # low, medium, high, critical
    estimated_duration: int  # minutes
    optimal_time: str       # time of day or specific time
    context: str           # why it was created
    confidence: float      # AI confidence in suggestion
    created_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None
    effectiveness_rating: Optional[int] = None
    auto_execute: bool = False

@dataclass
class WellnessSession:
    start_time: datetime.datetime
    duration: int  # minutes
    task_ids: List[str]
    session_type: str  # morning_routine, stress_relief, evening_wind_down, etc.
    mood_before: Optional[int] = None
    mood_after: Optional[int] = None
    notes: str = ""

@dataclass
class UserPattern:
    pattern_type: str
    description: str
    frequency: float
    optimal_times: List[str]
    effectiveness: float
    last_updated: datetime.datetime

class WellnessAutopilot:
    def __init__(self):
        self.data_dir = os.path.expanduser("~/.om")
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.tasks_file = os.path.join(self.data_dir, "autopilot_tasks.json")
        self.sessions_file = os.path.join(self.data_dir, "wellness_sessions.json")
        self.patterns_file = os.path.join(self.data_dir, "user_patterns.json")
        self.config_file = os.path.join(self.data_dir, "autopilot_config.json")
        
        self.mode = AutopilotMode.ASSISTED
        self.tasks = self._load_tasks()
        self.sessions = self._load_sessions()
        self.patterns = self._load_patterns()
        self.config = self._load_config()
    
    def _load_tasks(self) -> List[WellnessTask]:
        """Load wellness tasks from storage"""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r') as f:
                    data = json.load(f)
                    return [self._dict_to_task(item) for item in data]
            except Exception:
                return []
        return []
    
    def _load_sessions(self) -> List[WellnessSession]:
        """Load wellness sessions from storage"""
        if os.path.exists(self.sessions_file):
            try:
                with open(self.sessions_file, 'r') as f:
                    data = json.load(f)
                    return [self._dict_to_session(item) for item in data]
            except Exception:
                return []
        return []
    
    def _load_patterns(self) -> List[UserPattern]:
        """Load user patterns from storage"""
        if os.path.exists(self.patterns_file):
            try:
                with open(self.patterns_file, 'r') as f:
                    data = json.load(f)
                    return [self._dict_to_pattern(item) for item in data]
            except Exception:
                return []
        return []
    
    def _load_config(self) -> dict:
        """Load autopilot configuration"""
        default_config = {
            "mode": "assisted",
            "auto_morning_routine": True,
            "auto_stress_detection": True,
            "auto_evening_routine": True,
            "crisis_monitoring": True,
            "learning_enabled": True,
            "notification_times": ["09:00", "15:00", "21:00"]
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return {**default_config, **config}
            except Exception:
                return default_config
        return default_config
    
    def _save_tasks(self):
        """Save tasks to storage"""
        try:
            data = [self._task_to_dict(task) for task in self.tasks]
            with open(self.tasks_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def _save_sessions(self):
        """Save sessions to storage"""
        try:
            data = [self._session_to_dict(session) for session in self.sessions]
            with open(self.sessions_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving sessions: {e}")
    
    def _save_patterns(self):
        """Save patterns to storage"""
        try:
            data = [self._pattern_to_dict(pattern) for pattern in self.patterns]
            with open(self.patterns_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving patterns: {e}")
    
    def _save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def _dict_to_task(self, data: dict) -> WellnessTask:
        """Convert dictionary to WellnessTask"""
        data['task_type'] = WellnessTaskType(data['task_type'])
        data['created_at'] = datetime.datetime.fromisoformat(data['created_at'])
        if data.get('completed_at'):
            data['completed_at'] = datetime.datetime.fromisoformat(data['completed_at'])
        return WellnessTask(**data)
    
    def _task_to_dict(self, task: WellnessTask) -> dict:
        """Convert WellnessTask to dictionary"""
        data = asdict(task)
        data['task_type'] = task.task_type.value
        data['created_at'] = task.created_at.isoformat()
        if task.completed_at:
            data['completed_at'] = task.completed_at.isoformat()
        return data
    
    def _dict_to_session(self, data: dict) -> WellnessSession:
        """Convert dictionary to WellnessSession"""
        data['start_time'] = datetime.datetime.fromisoformat(data['start_time'])
        return WellnessSession(**data)
    
    def _session_to_dict(self, session: WellnessSession) -> dict:
        """Convert WellnessSession to dictionary"""
        data = asdict(session)
        data['start_time'] = session.start_time.isoformat()
        return data
    
    def _dict_to_pattern(self, data: dict) -> UserPattern:
        """Convert dictionary to UserPattern"""
        data['last_updated'] = datetime.datetime.fromisoformat(data['last_updated'])
        return UserPattern(**data)
    
    def _pattern_to_dict(self, pattern: UserPattern) -> dict:
        """Convert UserPattern to dictionary"""
        data = asdict(pattern)
        data['last_updated'] = pattern.last_updated.isoformat()
        return data
    
    def analyze_mood_data_for_tasks(self, mood_entries: List[dict]) -> List[WellnessTask]:
        """Analyze mood data and generate appropriate wellness tasks"""
        if not mood_entries:
            return []
        
        tasks = []
        recent_entries = mood_entries[-7:]  # Last week
        
        # Check for low mood patterns
        low_mood_count = sum(1 for entry in recent_entries if entry.get('mood', 5) <= 3)
        if low_mood_count >= 3:
            tasks.append(WellnessTask(
                id=f"mood_support_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title="Mood Support Session",
                description="Your mood has been low recently. Let's work on some mood-boosting activities.",
                task_type=WellnessTaskType.MOOD_CHECK,
                priority="high",
                estimated_duration=15,
                optimal_time="morning",
                context=f"Low mood detected in {low_mood_count}/7 recent entries",
                confidence=0.8,
                created_at=datetime.datetime.now()
            ))
        
        # Check for high stress patterns
        high_stress_count = sum(1 for entry in recent_entries if entry.get('stress', 0) >= 7)
        if high_stress_count >= 2:
            tasks.append(WellnessTask(
                id=f"stress_relief_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title="Stress Relief Session",
                description="You've been experiencing high stress. Let's practice some stress reduction techniques.",
                task_type=WellnessTaskType.BREATHING,
                priority="high",
                estimated_duration=10,
                optimal_time="afternoon",
                context=f"High stress detected in {high_stress_count}/7 recent entries",
                confidence=0.9,
                created_at=datetime.datetime.now()
            ))
        
        # Check for gratitude opportunities
        if not any('gratitude' in entry.get('notes', '').lower() for entry in recent_entries):
            tasks.append(WellnessTask(
                id=f"gratitude_practice_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title="Gratitude Practice",
                description="It's been a while since you practiced gratitude. This can help improve your overall mood.",
                task_type=WellnessTaskType.GRATITUDE,
                priority="medium",
                estimated_duration=5,
                optimal_time="evening",
                context="No recent gratitude practice detected",
                confidence=0.7,
                created_at=datetime.datetime.now()
            ))
        
        return tasks
    
    def generate_daily_routine(self) -> List[WellnessTask]:
        """Generate daily wellness routine based on patterns and preferences"""
        now = datetime.datetime.now()
        hour = now.hour
        
        routine_tasks = []
        
        # Morning routine (6-10 AM)
        if 6 <= hour <= 10 and self.config.get("auto_morning_routine", True):
            routine_tasks.extend([
                WellnessTask(
                    id=f"morning_mood_{now.strftime('%Y%m%d')}",
                    title="Morning Mood Check",
                    description="Start your day by checking in with yourself",
                    task_type=WellnessTaskType.MOOD_CHECK,
                    priority="medium",
                    estimated_duration=2,
                    optimal_time="morning",
                    context="Daily morning routine",
                    confidence=0.8,
                    created_at=now
                ),
                WellnessTask(
                    id=f"morning_breathing_{now.strftime('%Y%m%d')}",
                    title="Morning Breathing Exercise",
                    description="Energize yourself with a morning breathing practice",
                    task_type=WellnessTaskType.BREATHING,
                    priority="medium",
                    estimated_duration=5,
                    optimal_time="morning",
                    context="Daily morning routine",
                    confidence=0.8,
                    created_at=now
                )
            ])
        
        # Afternoon check-in (2-4 PM)
        elif 14 <= hour <= 16:
            routine_tasks.append(WellnessTask(
                id=f"afternoon_checkin_{now.strftime('%Y%m%d')}",
                title="Afternoon Wellness Check",
                description="Take a moment to assess your stress and energy levels",
                task_type=WellnessTaskType.MOOD_CHECK,
                priority="low",
                estimated_duration=3,
                optimal_time="afternoon",
                context="Daily afternoon check-in",
                confidence=0.6,
                created_at=now
            ))
        
        # Evening routine (7-10 PM)
        elif 19 <= hour <= 22 and self.config.get("auto_evening_routine", True):
            routine_tasks.extend([
                WellnessTask(
                    id=f"evening_gratitude_{now.strftime('%Y%m%d')}",
                    title="Evening Gratitude",
                    description="Reflect on the positive aspects of your day",
                    task_type=WellnessTaskType.GRATITUDE,
                    priority="medium",
                    estimated_duration=5,
                    optimal_time="evening",
                    context="Daily evening routine",
                    confidence=0.8,
                    created_at=now
                ),
                WellnessTask(
                    id=f"evening_reflection_{now.strftime('%Y%m%d')}",
                    title="Evening Reflection",
                    description="Take time to process your day and prepare for rest",
                    task_type=WellnessTaskType.SELF_REFLECTION,
                    priority="medium",
                    estimated_duration=10,
                    optimal_time="evening",
                    context="Daily evening routine",
                    confidence=0.7,
                    created_at=now
                )
            ])
        
        return routine_tasks
    
    def get_pending_tasks(self) -> List[WellnessTask]:
        """Get all pending wellness tasks"""
        return [task for task in self.tasks if task.completed_at is None]
    
    def get_priority_tasks(self) -> List[WellnessTask]:
        """Get high priority pending tasks"""
        pending = self.get_pending_tasks()
        return [task for task in pending if task.priority in ["high", "critical"]]
    
    def complete_task(self, task_id: str, effectiveness_rating: int, notes: str = ""):
        """Mark a task as completed"""
        for task in self.tasks:
            if task.id == task_id:
                task.completed_at = datetime.datetime.now()
                task.effectiveness_rating = effectiveness_rating
                break
        
        self._save_tasks()
        self._update_patterns_from_completion(task_id, effectiveness_rating)
    
    def _update_patterns_from_completion(self, task_id: str, effectiveness_rating: int):
        """Update user patterns based on task completion"""
        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            return
        
        # Find or create pattern for this task type
        pattern_type = f"{task.task_type.value}_{task.optimal_time}"
        existing_pattern = next((p for p in self.patterns if p.pattern_type == pattern_type), None)
        
        if existing_pattern:
            # Update existing pattern
            existing_pattern.effectiveness = (existing_pattern.effectiveness + effectiveness_rating) / 2
            existing_pattern.frequency += 0.1
            existing_pattern.last_updated = datetime.datetime.now()
        else:
            # Create new pattern
            self.patterns.append(UserPattern(
                pattern_type=pattern_type,
                description=f"{task.task_type.value} practice during {task.optimal_time}",
                frequency=1.0,
                optimal_times=[task.optimal_time],
                effectiveness=effectiveness_rating,
                last_updated=datetime.datetime.now()
            ))
        
        self._save_patterns()
    
    def get_recommendations(self) -> List[WellnessTask]:
        """Get AI-powered wellness recommendations"""
        recommendations = []
        
        # Check for routine tasks
        routine_tasks = self.generate_daily_routine()
        
        # Filter out tasks that already exist today
        today = datetime.datetime.now().date()
        existing_today = [t for t in self.tasks 
                         if t.created_at.date() == today]
        existing_types_today = {t.task_type for t in existing_today}
        
        for task in routine_tasks:
            if task.task_type not in existing_types_today:
                recommendations.append(task)
        
        # Add mood-based recommendations if mood data exists
        mood_file = os.path.expanduser("~/.om/mood_data.json")
        if os.path.exists(mood_file):
            try:
                with open(mood_file, 'r') as f:
                    mood_data = json.load(f)
                mood_tasks = self.analyze_mood_data_for_tasks(mood_data)
                recommendations.extend(mood_tasks)
            except Exception:
                pass
        
        return recommendations
    
    def auto_execute_tasks(self):
        """Execute tasks that are marked for auto-execution"""
        if self.mode != AutopilotMode.FULL_AUTO:
            return
        
        auto_tasks = [task for task in self.get_pending_tasks() if task.auto_execute]
        
        for task in auto_tasks:
            if task.task_type == WellnessTaskType.MOOD_CHECK:
                # Auto mood check - just log that it happened
                self.complete_task(task.id, 7, "Auto-executed mood check")
            elif task.task_type == WellnessTaskType.BREATHING:
                # Could trigger a breathing exercise
                print(f"🫁 Auto-executing: {task.title}")
                # In a real implementation, this might trigger the breathing module
            # Add more auto-execution logic as needed
    
    def get_autopilot_status(self) -> dict:
        """Get current autopilot status"""
        pending = len(self.get_pending_tasks())
        priority = len(self.get_priority_tasks())
        completed_today = len([t for t in self.tasks 
                              if t.completed_at and t.completed_at.date() == datetime.datetime.now().date()])
        
        return {
            "mode": self.mode.value,
            "pending_tasks": pending,
            "priority_tasks": priority,
            "completed_today": completed_today,
            "patterns_learned": len(self.patterns),
            "auto_routines_enabled": self.config.get("auto_morning_routine", False) or self.config.get("auto_evening_routine", False)
        }

def run(args=None):
    """Main function to run wellness autopilot"""
    autopilot = WellnessAutopilot()
    
    if not args or args[0] == "status":
        # Show autopilot status
        status = autopilot.get_autopilot_status()
        print("\n🤖 Wellness Autopilot Status")
        print("=" * 40)
        print(f"Mode: {status['mode'].replace('_', ' ').title()}")
        print(f"Pending tasks: {status['pending_tasks']}")
        print(f"Priority tasks: {status['priority_tasks']}")
        print(f"Completed today: {status['completed_today']}")
        print(f"Patterns learned: {status['patterns_learned']}")
        print(f"Auto routines: {'Enabled' if status['auto_routines_enabled'] else 'Disabled'}")
    
    elif args[0] == "tasks":
        # Show pending tasks
        pending = autopilot.get_pending_tasks()
        if pending:
            print("\n📋 Pending Wellness Tasks")
            print("=" * 40)
            for i, task in enumerate(pending, 1):
                priority_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴", "critical": "🚨"}
                print(f"{i}. {priority_emoji.get(task.priority, '⚪')} {task.title}")
                print(f"   {task.description}")
                print(f"   Duration: {task.estimated_duration} min | Best time: {task.optimal_time}")
                print(f"   Confidence: {task.confidence:.1%}")
                print()
        else:
            print("\n✅ No pending wellness tasks!")
    
    elif args[0] == "recommendations":
        # Show AI recommendations
        recommendations = autopilot.get_recommendations()
        if recommendations:
            print("\n🧠 AI Wellness Recommendations")
            print("=" * 40)
            for i, task in enumerate(recommendations, 1):
                print(f"{i}. {task.title}")
                print(f"   {task.description}")
                print(f"   Type: {task.task_type.value.replace('_', ' ').title()}")
                print(f"   Duration: {task.estimated_duration} min")
                print()
            
            # Add recommendations to tasks
            autopilot.tasks.extend(recommendations)
            autopilot._save_tasks()
            print(f"✅ Added {len(recommendations)} recommendations to your task list!")
        else:
            print("\n😌 No new recommendations at this time. You're doing great!")
    
    elif args[0] == "complete" and len(args) >= 3:
        # Complete a task
        try:
            task_index = int(args[1]) - 1
            effectiveness = int(args[2])
            
            pending = autopilot.get_pending_tasks()
            if 0 <= task_index < len(pending):
                task = pending[task_index]
                autopilot.complete_task(task.id, effectiveness)
                print(f"✅ Completed: {task.title}")
                print(f"   Effectiveness rating: {effectiveness}/10")
            else:
                print("❌ Invalid task number")
        except (ValueError, IndexError):
            print("❌ Usage: om autopilot complete <task_number> <effectiveness_1-10>")
    
    elif args[0] == "config":
        # Show/modify configuration
        if len(args) == 1:
            print("\n⚙️  Autopilot Configuration")
            print("=" * 40)
            for key, value in autopilot.config.items():
                print(f"{key}: {value}")
        else:
            print("Configuration modification not implemented yet")
    
    else:
        print("\n🤖 Wellness Autopilot")
        print("=" * 30)
        print("Available commands:")
        print("  om autopilot status         - Show autopilot status")
        print("  om autopilot tasks          - Show pending tasks")
        print("  om autopilot recommendations - Get AI recommendations")
        print("  om autopilot complete <n> <rating> - Complete task n with rating 1-10")
        print("  om autopilot config         - Show configuration")

if __name__ == "__main__":
    run()
