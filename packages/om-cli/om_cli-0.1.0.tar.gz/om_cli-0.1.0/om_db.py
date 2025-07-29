#!/usr/bin/env python3
"""
Om Mental Health Database Manager
Following logbuch.db pattern for consistency
"""

import sqlite3
import json
import uuid
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging

class OmDB:
    """Om Mental Health Database Manager - following logbuch pattern"""
    
    def __init__(self, db_path: str = None):
        """Initialize Om database connection"""
        if db_path is None:
            db_path = str(Path.home() / ".om" / "om.db")
        
        self.db_path = db_path
        self.connection = None
        self.logger = logging.getLogger(__name__)
        
        # Ensure .om directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.connect()
        self.initialize_database()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON")
            return True
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            return False
    
    def initialize_database(self):
        """Initialize database schema if needed"""
        try:
            # Check if database is initialized
            cursor = self.connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='config'"
            )
            
            if not cursor.fetchone():
                # Database not initialized, create schema
                schema_path = Path(__file__).parent / "om_schema.sql"
                if schema_path.exists():
                    with open(schema_path, 'r') as f:
                        schema_sql = f.read()
                    
                    # Execute schema
                    self.connection.executescript(schema_sql)
                    self.connection.commit()
                    self.logger.info("Om database initialized successfully")
                else:
                    self.logger.error("Schema file not found")
            
            # Migrate existing JSON data if present
            self._migrate_existing_data()
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # ============================================================================
    # CONFIGURATION METHODS (following logbuch pattern)
    # ============================================================================
    
    def get_config(self, key: str, default: str = None) -> str:
        """Get configuration value"""
        cursor = self.connection.execute("SELECT value FROM config WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result['value'] if result else default
    
    def set_config(self, key: str, value: str):
        """Set configuration value"""
        self.connection.execute(
            "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
            (key, value)
        )
        self.connection.commit()
    
    # ============================================================================
    # MOOD TRACKING METHODS
    # ============================================================================
    
    def add_mood_entry(self, mood: str, level: int, energy_level: int = None,
                      stress_level: int = None, anxiety_level: int = None,
                      notes: str = None, tags: List[str] = None) -> str:
        """Add mood entry (following logbuch journal_entries pattern)"""
        entry_id = str(uuid.uuid4())
        now = datetime.now()
        
        self.connection.execute("""
            INSERT INTO mood_entries 
            (id, mood, level, energy_level, stress_level, anxiety_level, notes, date, time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry_id, mood, level, energy_level, stress_level, anxiety_level,
            notes, now.strftime('%Y-%m-%d'), now.strftime('%H:%M:%S')
        ))
        
        # Add tags (following logbuch journal_tags pattern)
        if tags:
            for tag in tags:
                self.connection.execute(
                    "INSERT INTO mood_tags (entry_id, tag) VALUES (?, ?)",
                    (entry_id, tag)
                )
        
        self.connection.commit()
        self._award_xp(10, "Mood entry")
        self._check_achievements()
        
        return entry_id
    
    def get_mood_entries(self, days: int = 30) -> List[Dict]:
        """Get mood entries with tags"""
        query = """
            SELECT m.*, GROUP_CONCAT(t.tag) as tags
            FROM mood_entries m
            LEFT JOIN mood_tags t ON m.id = t.entry_id
            WHERE m.date >= date('now', '-{} days')
            GROUP BY m.id
            ORDER BY m.date DESC, m.time DESC
        """.format(days)
        
        cursor = self.connection.execute(query)
        entries = []
        for row in cursor.fetchall():
            entry = dict(row)
            entry['tags'] = row['tags'].split(',') if row['tags'] else []
            entries.append(entry)
        
        return entries
    
    def get_mood_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get mood statistics"""
        query = """
            SELECT 
                AVG(level) as avg_mood,
                AVG(energy_level) as avg_energy,
                AVG(stress_level) as avg_stress,
                AVG(anxiety_level) as avg_anxiety,
                COUNT(*) as total_entries,
                MIN(level) as min_mood,
                MAX(level) as max_mood
            FROM mood_entries 
            WHERE date >= date('now', '-{} days')
        """.format(days)
        
        cursor = self.connection.execute(query)
        return dict(cursor.fetchone())
    
    # ============================================================================
    # WELLNESS SESSIONS METHODS
    # ============================================================================
    
    def add_wellness_session(self, session_type: str, technique: str = None,
                           duration_seconds: int = None, effectiveness: int = None,
                           notes: str = None, tags: List[str] = None) -> str:
        """Add wellness session"""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        self.connection.execute("""
            INSERT INTO wellness_sessions 
            (id, type, technique, duration_seconds, effectiveness, notes, date, time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id, session_type, technique, duration_seconds,
            effectiveness, notes, now.strftime('%Y-%m-%d'), now.strftime('%H:%M:%S')
        ))
        
        # Add tags
        if tags:
            for tag in tags:
                self.connection.execute(
                    "INSERT INTO session_tags (session_id, tag) VALUES (?, ?)",
                    (session_id, tag)
                )
        
        self.connection.commit()
        
        # Award XP based on session type
        xp_rewards = {
            'breathing': 15,
            'meditation': 20,
            'gratitude': 10,
            'physical': 12,
            'mindfulness': 18
        }
        self._award_xp(xp_rewards.get(session_type, 10), f"{session_type} session")
        self._check_achievements()
        
        return session_id
    
    def get_wellness_sessions(self, days: int = 30) -> List[Dict]:
        """Get wellness sessions with tags"""
        query = """
            SELECT s.*, GROUP_CONCAT(t.tag) as tags
            FROM wellness_sessions s
            LEFT JOIN session_tags t ON s.id = t.session_id
            WHERE s.date >= date('now', '-{} days')
            GROUP BY s.id
            ORDER BY s.date DESC, s.time DESC
        """.format(days)
        
        cursor = self.connection.execute(query)
        sessions = []
        for row in cursor.fetchall():
            session = dict(row)
            session['tags'] = row['tags'].split(',') if row['tags'] else []
            sessions.append(session)
        
        return sessions
    
    def get_wellness_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get wellness session statistics"""
        query = """
            SELECT 
                type,
                COUNT(*) as session_count,
                AVG(duration_seconds) as avg_duration,
                AVG(effectiveness) as avg_effectiveness,
                SUM(duration_seconds) as total_duration
            FROM wellness_sessions 
            WHERE date >= date('now', '-{} days')
            GROUP BY type
        """.format(days)
        
        cursor = self.connection.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    # ============================================================================
    # GRATITUDE METHODS
    # ============================================================================
    
    def add_gratitude_entry(self, text: str, category: str = None, intensity: int = None) -> str:
        """Add gratitude entry"""
        entry_id = str(uuid.uuid4())
        now = datetime.now()
        
        self.connection.execute("""
            INSERT INTO gratitude_entries (id, text, category, intensity, date, time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            entry_id, text, category, intensity,
            now.strftime('%Y-%m-%d'), now.strftime('%H:%M:%S')
        ))
        
        self.connection.commit()
        self._award_xp(8, "Gratitude practice")
        self._check_achievements()
        
        return entry_id
    
    def get_gratitude_entries(self, days: int = 30) -> List[Dict]:
        """Get gratitude entries"""
        query = """
            SELECT * FROM gratitude_entries 
            WHERE date >= date('now', '-{} days')
            ORDER BY date DESC, time DESC
        """.format(days)
        
        cursor = self.connection.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    # ============================================================================
    # WELLNESS GOALS AND TASKS (following logbuch goals/tasks pattern)
    # ============================================================================
    
    def add_wellness_goal(self, title: str, description: str = None, category: str = None,
                         target_value: int = None, target_date: str = None) -> str:
        """Add wellness goal (following logbuch goals pattern)"""
        goal_id = str(uuid.uuid4())
        
        self.connection.execute("""
            INSERT INTO wellness_goals 
            (id, title, description, category, target_value, target_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (goal_id, title, description, category, target_value, target_date))
        
        self.connection.commit()
        return goal_id
    
    def add_wellness_task(self, title: str, description: str = None, category: str = None,
                         priority: str = 'medium', estimated_minutes: int = None,
                         tags: List[str] = None) -> str:
        """Add wellness task (following logbuch tasks pattern)"""
        task_id = str(uuid.uuid4())
        today = datetime.now().strftime('%Y-%m-%d')
        
        self.connection.execute("""
            INSERT INTO wellness_tasks 
            (id, title, description, category, priority, estimated_minutes, date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (task_id, title, description, category, priority, estimated_minutes, today))
        
        # Add tags
        if tags:
            for tag in tags:
                self.connection.execute(
                    "INSERT INTO task_tags (task_id, tag) VALUES (?, ?)",
                    (task_id, tag)
                )
        
        self.connection.commit()
        return task_id
    
    def complete_wellness_task(self, task_id: str, effectiveness: int = None, notes: str = None):
        """Complete wellness task"""
        self.connection.execute("""
            UPDATE wellness_tasks 
            SET completed = 1, effectiveness = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (effectiveness, task_id))
        
        self.connection.commit()
        self._award_xp(12, "Task completion")
        self._check_achievements()
    
    def get_wellness_tasks(self, completed: bool = False, days: int = 7) -> List[Dict]:
        """Get wellness tasks with tags"""
        query = """
            SELECT t.*, GROUP_CONCAT(tags.tag) as tags
            FROM wellness_tasks t
            LEFT JOIN task_tags tags ON t.id = tags.task_id
            WHERE t.completed = ? AND t.date >= date('now', '-{} days')
            GROUP BY t.id
            ORDER BY t.priority DESC, t.created_at ASC
        """.format(days)
        
        cursor = self.connection.execute(query, (completed,))
        tasks = []
        for row in cursor.fetchall():
            task = dict(row)
            task['tags'] = row['tags'].split(',') if row['tags'] else []
            tasks.append(task)
        
        return tasks
    
    # ============================================================================
    # CRISIS SUPPORT METHODS
    # ============================================================================
    
    def add_crisis_event(self, severity: int, description: str = None,
                        triggers: str = None, support_used: str = None) -> str:
        """Add crisis event"""
        event_id = str(uuid.uuid4())
        now = datetime.now()
        
        self.connection.execute("""
            INSERT INTO crisis_events 
            (id, severity, description, triggers, support_used, date, time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id, severity, description, triggers, support_used,
            now.strftime('%Y-%m-%d'), now.strftime('%H:%M:%S')
        ))
        
        self.connection.commit()
        return event_id
    
    # ============================================================================
    # COACHING INSIGHTS METHODS
    # ============================================================================
    
    def add_coaching_insight(self, insight_type: str, content: str,
                           confidence: float = None, source: str = None) -> str:
        """Add coaching insight"""
        insight_id = str(uuid.uuid4())
        today = datetime.now().strftime('%Y-%m-%d')
        
        self.connection.execute("""
            INSERT INTO coaching_insights (id, type, content, confidence, source, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (insight_id, insight_type, content, confidence, source, today))
        
        self.connection.commit()
        return insight_id
    
    def get_daily_insights(self, target_date: str = None) -> List[Dict]:
        """Get coaching insights for date"""
        if target_date is None:
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        cursor = self.connection.execute(
            "SELECT * FROM coaching_insights WHERE date = ? ORDER BY created_at DESC",
            (target_date,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    # ============================================================================
    # GAMIFICATION METHODS
    # ============================================================================
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics"""
        cursor = self.connection.execute("SELECT * FROM user_stats WHERE id = 1")
        result = cursor.fetchone()
        return dict(result) if result else {}
    
    def _award_xp(self, xp: int, reason: str = None):
        """Award XP and update level"""
        self.connection.execute("""
            UPDATE user_stats 
            SET xp = xp + ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
        """, (xp,))
        
        # Check for level up
        stats = self.get_user_stats()
        current_xp = stats.get('xp', 0)
        current_level = stats.get('level', 1)
        
        # Simple level calculation: 100 XP per level
        new_level = (current_xp // 100) + 1
        
        if new_level > current_level:
            self.connection.execute(
                "UPDATE user_stats SET level = ? WHERE id = 1",
                (new_level,)
            )
        
        self.connection.commit()
    
    def _check_achievements(self):
        """Check and unlock achievements"""
        stats = self.get_user_stats()
        
        # Get unlocked achievement IDs
        cursor = self.connection.execute(
            "SELECT achievement_id FROM user_achievements WHERE unlocked = 1"
        )
        unlocked_ids = {row[0] for row in cursor.fetchall()}
        
        # Get all achievements
        cursor = self.connection.execute("SELECT * FROM achievements")
        achievements = [dict(row) for row in cursor.fetchall()]
        
        for achievement in achievements:
            if achievement['id'] in unlocked_ids:
                continue
            
            if self._check_achievement_requirement(achievement, stats):
                self._unlock_achievement(achievement['id'])
    
    def _check_achievement_requirement(self, achievement: Dict, stats: Dict) -> bool:
        """Check if achievement requirement is met"""
        req_type = achievement['requirement_type']
        req_value = achievement['requirement_value']
        category = achievement['category']
        
        if req_type == 'count':
            if category == 'mood':
                return stats.get('total_mood_entries', 0) >= req_value
            elif category == 'breathing':
                return stats.get('total_breathing_sessions', 0) >= req_value
            elif category == 'gratitude':
                return stats.get('total_gratitude_entries', 0) >= req_value
        elif req_type == 'streak':
            return stats.get('current_streak', 0) >= req_value
        elif req_type == 'level':
            return stats.get('level', 1) >= req_value
        
        return False
    
    def _unlock_achievement(self, achievement_id: str):
        """Unlock achievement and award rewards"""
        # Get achievement details
        cursor = self.connection.execute(
            "SELECT * FROM achievements WHERE id = ?", (achievement_id,)
        )
        achievement = dict(cursor.fetchone())
        
        # Add to user achievements
        user_achievement_id = str(uuid.uuid4())
        self.connection.execute("""
            INSERT INTO user_achievements 
            (id, achievement_id, progress, unlocked, unlocked_at)
            VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
        """, (user_achievement_id, achievement_id, achievement['requirement_value']))
        
        # Award XP and points
        self.connection.execute("""
            UPDATE user_stats 
            SET xp = xp + ?, wellness_points = wellness_points + ?
            WHERE id = 1
        """, (achievement['xp_reward'], achievement['points_reward']))
        
        self.connection.commit()
        return achievement
    
    def get_achievements(self, unlocked_only: bool = False) -> List[Dict]:
        """Get achievements with unlock status"""
        if unlocked_only:
            query = """
                SELECT a.*, ua.unlocked_at
                FROM achievements a
                JOIN user_achievements ua ON a.id = ua.achievement_id
                WHERE ua.unlocked = 1
                ORDER BY ua.unlocked_at DESC
            """
        else:
            query = """
                SELECT a.*, COALESCE(ua.unlocked, 0) as unlocked, ua.unlocked_at
                FROM achievements a
                LEFT JOIN user_achievements ua ON a.id = ua.achievement_id
                ORDER BY a.category, a.requirement_value
            """
        
        cursor = self.connection.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    # ============================================================================
    # HABIT TRACKING METHODS
    # ============================================================================
    
    def add_habit(self, name: str, description: str = None, category: str = None,
                 frequency: str = 'daily', target_count: int = 1) -> str:
        """Add habit"""
        habit_id = str(uuid.uuid4())
        
        self.connection.execute("""
            INSERT INTO habits (id, name, description, category, frequency, target_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (habit_id, name, description, category, frequency, target_count))
        
        self.connection.commit()
        return habit_id
    
    def complete_habit(self, habit_id: str, count: int = 1, notes: str = None):
        """Mark habit as completed for today"""
        today = datetime.now().strftime('%Y-%m-%d')
        completion_id = str(uuid.uuid4())
        
        self.connection.execute("""
            INSERT OR REPLACE INTO habit_completions 
            (id, habit_id, date, count, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (completion_id, habit_id, today, count, notes))
        
        self.connection.commit()
        self._award_xp(5, "Habit completion")
    
    # ============================================================================
    # DASHBOARD AND REPORTING METHODS
    # ============================================================================
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        return {
            'user_stats': self.get_user_stats(),
            'recent_moods': self.get_mood_entries(7),
            'recent_sessions': self.get_wellness_sessions(7),
            'recent_gratitude': self.get_gratitude_entries(7),
            'pending_tasks': self.get_wellness_tasks(completed=False),
            'mood_stats': self.get_mood_stats(30),
            'wellness_stats': self.get_wellness_stats(30),
            'daily_insights': self.get_daily_insights(),
            'achievements': self.get_achievements(unlocked_only=True)
        }
    
    def export_data(self, export_type: str = 'full', days: int = None) -> Dict[str, Any]:
        """Export data"""
        data = {}
        
        if export_type in ['full', 'mood']:
            data['mood_entries'] = self.get_mood_entries(days or 365)
        
        if export_type in ['full', 'wellness']:
            data['wellness_sessions'] = self.get_wellness_sessions(days or 365)
            data['gratitude_entries'] = self.get_gratitude_entries(days or 365)
        
        if export_type in ['full', 'stats']:
            data['user_stats'] = self.get_user_stats()
            data['achievements'] = self.get_achievements()
        
        return data
    
    def backup_database(self, backup_path: str = None) -> str:
        """Create database backup"""
        if backup_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = Path.home() / ".om" / "backups"
            backup_dir.mkdir(exist_ok=True)
            backup_path = str(backup_dir / f"om_backup_{timestamp}.db")
        
        # Create backup
        backup_conn = sqlite3.connect(backup_path)
        self.connection.backup(backup_conn)
        backup_conn.close()
        
        # Log backup
        backup_id = str(uuid.uuid4())
        file_size = Path(backup_path).stat().st_size
        
        self.connection.execute("""
            INSERT INTO backup_logs (id, type, file_path, size_bytes)
            VALUES (?, 'manual', ?, ?)
        """, (backup_id, backup_path, file_size))
        self.connection.commit()
        
        return backup_path
    
    # ============================================================================
    # DATA MIGRATION METHODS
    # ============================================================================
    
    def _migrate_existing_data(self):
        """Migrate existing JSON data to database"""
        om_dir = Path.home() / ".om"
        
        # Migrate mood_data.json
        mood_file = om_dir / "mood_data.json"
        if mood_file.exists():
            try:
                with open(mood_file, 'r') as f:
                    mood_data = json.load(f)
                
                for entry in mood_data:
                    # Convert mood text to level if needed
                    level = entry.get('level', 5)
                    if isinstance(level, str):
                        mood_mapping = {
                            'terrible': 1, 'awful': 2, 'bad': 3, 'poor': 4,
                            'okay': 5, 'fine': 5, 'good': 6, 'great': 7,
                            'excellent': 8, 'amazing': 9, 'fantastic': 10
                        }
                        level = mood_mapping.get(level.lower(), 5)
                    
                    # Parse timestamp
                    timestamp = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                    
                    # Check if entry already exists
                    cursor = self.connection.execute(
                        "SELECT id FROM mood_entries WHERE date = ? AND time = ?",
                        (timestamp.strftime('%Y-%m-%d'), timestamp.strftime('%H:%M:%S'))
                    )
                    
                    if not cursor.fetchone():
                        self.connection.execute("""
                            INSERT INTO mood_entries 
                            (id, mood, level, notes, date, time, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            str(uuid.uuid4()),
                            entry.get('mood', 'neutral'),
                            level,
                            entry.get('notes', ''),
                            timestamp.strftime('%Y-%m-%d'),
                            timestamp.strftime('%H:%M:%S'),
                            timestamp.isoformat()
                        ))
                
                self.connection.commit()
                self.logger.info(f"Migrated mood data from {mood_file}")
                
            except Exception as e:
                self.logger.error(f"Error migrating mood data: {e}")
        
        # Migrate wellness_stats.json to user_stats
        stats_file = om_dir / "wellness_stats.json"
        if stats_file.exists():
            try:
                with open(stats_file, 'r') as f:
                    stats_data = json.load(f)
                
                # Update user stats
                self.connection.execute("""
                    UPDATE user_stats SET
                        total_meditation_minutes = ?,
                        total_breathing_sessions = ?,
                        total_gratitude_entries = ?,
                        total_mood_entries = ?,
                        current_streak = ?
                    WHERE id = 1
                """, (
                    stats_data.get('meditation_minutes', 0),
                    stats_data.get('breathing_sessions', 0),
                    stats_data.get('gratitude_entries', 0),
                    stats_data.get('mood_entries', 0),
                    stats_data.get('streak_days', 0)
                ))
                
                self.connection.commit()
                self.logger.info(f"Migrated wellness stats from {stats_file}")
                
            except Exception as e:
                self.logger.error(f"Error migrating wellness stats: {e}")


# Example usage
if __name__ == "__main__":
    # Initialize database
    db = OmDB()
    
    # Add sample data
    mood_id = db.add_mood_entry("good", 7, energy_level=6, stress_level=4, 
                               notes="Feeling productive today", 
                               tags=["work", "positive"])
    
    session_id = db.add_wellness_session("breathing", "4-7-8", 300, 8, 
                                        "Very relaxing session", 
                                        tags=["morning", "calm"])
    
    gratitude_id = db.add_gratitude_entry("Grateful for my health", "health", 9)
    
    # Get dashboard data
    dashboard = db.get_dashboard_data()
    
    print("Om database initialized successfully!")
    print(f"User stats: Level {dashboard['user_stats']['level']}, XP: {dashboard['user_stats']['xp']}")
    print(f"Recent moods: {len(dashboard['recent_moods'])} entries")
    print(f"Recent sessions: {len(dashboard['recent_sessions'])} sessions")
    
    db.close()
