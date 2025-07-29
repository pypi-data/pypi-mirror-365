#!/usr/bin/env python3
"""
SQLite3 Storage System for om Mental Health Platform
Based on logbuch.db structure, adapted for wellness and mental health tracking
"""

import sqlite3
import json
import uuid
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from contextlib import contextmanager
import threading

class OMSQLiteStorage:
    """SQLite3 storage system for om mental health platform"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the storage system"""
        if db_path is None:
            # Default to ~/.om/data/om.db
            home = Path.home()
            data_dir = home / ".om" / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / "om.db"
        
        self.db_path = str(db_path)
        self._lock = threading.Lock()
        
        # Initialize database
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper cleanup"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            try:
                yield conn
            finally:
                conn.close()
    
    def _init_database(self):
        """Initialize database with all required tables"""
        with self.get_connection() as conn:
            # Configuration table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            
            # Enhanced mood entries with wellness focus
            conn.execute('''
                CREATE TABLE IF NOT EXISTS mood_entries (
                    id TEXT PRIMARY KEY,
                    mood TEXT NOT NULL,
                    intensity INTEGER,  -- 1-10 scale
                    date TEXT NOT NULL,
                    notes TEXT DEFAULT '',
                    triggers TEXT,  -- JSON array of triggers
                    location TEXT,
                    energy_level INTEGER,  -- 1-10 scale
                    stress_level INTEGER,  -- 1-10 scale
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Daily check-ins for comprehensive wellness tracking
            conn.execute('''
                CREATE TABLE IF NOT EXISTS checkin_entries (
                    id TEXT PRIMARY KEY,
                    date TEXT NOT NULL,
                    type TEXT DEFAULT 'daily',  -- daily, morning, evening, quick
                    mood TEXT,
                    mood_intensity INTEGER,
                    energy_level INTEGER,
                    stress_level INTEGER,
                    sleep_quality TEXT,  -- excellent, good, fair, poor
                    sleep_hours REAL,
                    going_well TEXT,
                    challenges TEXT,
                    daily_goal TEXT,
                    gratitude TEXT,
                    self_care_plan TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Wellness sessions (meditation, breathing, etc.)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS wellness_sessions (
                    id TEXT PRIMARY KEY,
                    activity_type TEXT NOT NULL,  -- breathing, meditation, exercise, etc.
                    duration_minutes INTEGER,
                    date TEXT NOT NULL,
                    notes TEXT DEFAULT '',
                    rating INTEGER,  -- 1-5 how helpful it was
                    mood_before TEXT,
                    mood_after TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Wellness goals with progress tracking
            conn.execute('''
                CREATE TABLE IF NOT EXISTS wellness_goals (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT,  -- mood, stress, sleep, exercise, mindfulness, etc.
                    target_value INTEGER,
                    current_value INTEGER DEFAULT 0,
                    unit TEXT,  -- days, sessions, minutes, etc.
                    created_date TEXT NOT NULL,
                    target_date TEXT,
                    completed BOOLEAN DEFAULT 0,
                    completed_date TEXT,
                    priority TEXT DEFAULT 'medium'  -- low, medium, high
                )
            ''')
            
            # Journal entries for reflection and thoughts
            conn.execute('''
                CREATE TABLE IF NOT EXISTS journal_entries (
                    id TEXT PRIMARY KEY,
                    date TEXT NOT NULL,
                    title TEXT,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'general',  -- general, gratitude, reflection, goals, etc.
                    mood TEXT,
                    tags TEXT,  -- JSON array of tags
                    private BOOLEAN DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Achievements for gamification
            conn.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    icon TEXT,  -- emoji
                    category TEXT,
                    points INTEGER DEFAULT 10,
                    criteria TEXT,  -- JSON criteria for unlocking
                    active BOOLEAN DEFAULT 1
                )
            ''')
            
            # User achievements (unlocked achievements)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    achievement_id TEXT NOT NULL,
                    unlocked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (achievement_id) REFERENCES achievements(id)
                )
            ''')
            
            # Wellness insights and patterns (AI coach data)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS wellness_insights (
                    id TEXT PRIMARY KEY,
                    date TEXT NOT NULL,
                    insight_type TEXT,  -- pattern, recommendation, achievement, etc.
                    title TEXT,
                    content TEXT,
                    data TEXT,  -- JSON data supporting the insight
                    priority TEXT DEFAULT 'medium',
                    read BOOLEAN DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Quick actions log
            conn.execute('''
                CREATE TABLE IF NOT EXISTS quick_actions (
                    id TEXT PRIMARY KEY,
                    action_type TEXT NOT NULL,  -- mood_log, gratitude, breathing, etc.
                    data TEXT,  -- JSON data for the action
                    date TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Backup metadata
            conn.execute('''
                CREATE TABLE IF NOT EXISTS backups (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    file_path TEXT,
                    size_bytes INTEGER,
                    version TEXT
                )
            ''')
            
            conn.commit()
            
            # Initialize default data
            self._init_default_data(conn)
    
    def _init_default_data(self, conn):
        """Initialize default achievements and configuration"""
        # Check if already initialized
        cursor = conn.execute("SELECT value FROM config WHERE key = 'initialized'")
        if cursor.fetchone():
            return
        
        # Default achievements
        default_achievements = [
            {
                'id': str(uuid.uuid4()),
                'name': 'First Steps',
                'description': 'Log your first mood entry',
                'icon': '🌱',
                'category': 'getting_started',
                'points': 10,
                'criteria': json.dumps({'mood_entries': 1})
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Daily Tracker',
                'description': 'Log mood for 7 consecutive days',
                'icon': '📅',
                'category': 'consistency',
                'points': 50,
                'criteria': json.dumps({'consecutive_mood_days': 7})
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Mindful Moment',
                'description': 'Complete your first wellness session',
                'icon': '🧘',
                'category': 'wellness',
                'points': 15,
                'criteria': json.dumps({'wellness_sessions': 1})
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Goal Setter',
                'description': 'Create your first wellness goal',
                'icon': '🎯',
                'category': 'goals',
                'points': 20,
                'criteria': json.dumps({'wellness_goals': 1})
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Reflection Master',
                'description': 'Complete 10 check-ins',
                'icon': '📝',
                'category': 'reflection',
                'points': 30,
                'criteria': json.dumps({'checkin_entries': 10})
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Wellness Warrior',
                'description': 'Complete 30 wellness sessions',
                'icon': '💪',
                'category': 'wellness',
                'points': 100,
                'criteria': json.dumps({'wellness_sessions': 30})
            }
        ]
        
        for achievement in default_achievements:
            conn.execute('''
                INSERT INTO achievements (id, name, description, icon, category, points, criteria)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                achievement['id'], achievement['name'], achievement['description'],
                achievement['icon'], achievement['category'], achievement['points'],
                achievement['criteria']
            ))
        
        # Default configuration
        conn.execute("INSERT INTO config (key, value) VALUES ('initialized', 'true')")
        conn.execute("INSERT INTO config (key, value) VALUES ('version', '2.0.0')")
        conn.execute("INSERT INTO config (key, value) VALUES ('created_at', ?)", (datetime.now().isoformat(),))
        
        conn.commit()
    
    # Mood tracking methods
    def add_mood_entry(self, mood: str, intensity: Optional[int] = None, 
                      notes: str = '', triggers: Optional[List[str]] = None,
                      location: Optional[str] = None, energy_level: Optional[int] = None,
                      stress_level: Optional[int] = None) -> str:
        """Add a new mood entry"""
        entry_id = str(uuid.uuid4())
        date = datetime.now().isoformat()
        triggers_json = json.dumps(triggers) if triggers else None
        
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO mood_entries 
                (id, mood, intensity, date, notes, triggers, location, energy_level, stress_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (entry_id, mood, intensity, date, notes, triggers_json, location, energy_level, stress_level))
            conn.commit()
        
        # Check for achievements
        self._check_achievements()
        
        return entry_id
    
    def get_mood_entries(self, limit: int = 50, days: Optional[int] = None) -> List[Dict]:
        """Get mood entries with optional filtering"""
        with self.get_connection() as conn:
            query = "SELECT * FROM mood_entries"
            params = []
            
            if days:
                start_date = (datetime.now() - timedelta(days=days)).isoformat()
                query += " WHERE date >= ?"
                params.append(start_date)
            
            query += " ORDER BY date DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            entries = []
            
            for row in cursor.fetchall():
                entry = dict(row)
                # Parse JSON fields
                if entry['triggers']:
                    entry['triggers'] = json.loads(entry['triggers'])
                else:
                    entry['triggers'] = []
                entries.append(entry)
            
            return entries
    
    def get_mood_analytics(self, days: int = 30) -> Dict:
        """Get mood analytics and patterns"""
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with self.get_connection() as conn:
            # Basic stats
            cursor = conn.execute('''
                SELECT COUNT(*) as total, 
                       AVG(intensity) as avg_intensity,
                       mood,
                       COUNT(*) as mood_count
                FROM mood_entries 
                WHERE date >= ?
                GROUP BY mood
                ORDER BY mood_count DESC
            ''', (start_date,))
            
            mood_stats = cursor.fetchall()
            
            # Weekly stats
            week_start = (datetime.now() - timedelta(days=7)).isoformat()
            cursor = conn.execute('''
                SELECT COUNT(*) as entries_this_week
                FROM mood_entries 
                WHERE date >= ?
            ''', (week_start,))
            
            week_stats = cursor.fetchone()
            
            # Trend analysis (simplified)
            cursor = conn.execute('''
                SELECT date, intensity, mood
                FROM mood_entries 
                WHERE date >= ? AND intensity IS NOT NULL
                ORDER BY date
            ''', (start_date,))
            
            trend_data = cursor.fetchall()
            
            return {
                'total_entries': sum(row['mood_count'] for row in mood_stats),
                'entries_this_week': week_stats['entries_this_week'],
                'mood_distribution': {row['mood']: row['mood_count'] for row in mood_stats},
                'average_intensity': mood_stats[0]['avg_intensity'] if mood_stats else 0,
                'most_common_mood': mood_stats[0]['mood'] if mood_stats else None,
                'trend_data': [dict(row) for row in trend_data]
            }
    
    # Check-in methods
    def add_checkin_entry(self, checkin_data: Dict) -> str:
        """Add a daily check-in entry"""
        entry_id = str(uuid.uuid4())
        date = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO checkin_entries 
                (id, date, type, mood, mood_intensity, energy_level, stress_level,
                 sleep_quality, sleep_hours, going_well, challenges, daily_goal,
                 gratitude, self_care_plan)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry_id, date,
                checkin_data.get('type', 'daily'),
                checkin_data.get('mood'),
                checkin_data.get('mood_intensity'),
                checkin_data.get('energy_level'),
                checkin_data.get('stress_level'),
                checkin_data.get('sleep_quality'),
                checkin_data.get('sleep_hours'),
                checkin_data.get('going_well'),
                checkin_data.get('challenges'),
                checkin_data.get('daily_goal'),
                checkin_data.get('gratitude'),
                checkin_data.get('self_care_plan')
            ))
            conn.commit()
        
        return entry_id
    
    def get_checkin_entries(self, limit: int = 30, days: Optional[int] = None) -> List[Dict]:
        """Get check-in entries"""
        with self.get_connection() as conn:
            query = "SELECT * FROM checkin_entries"
            params = []
            
            if days:
                start_date = (datetime.now() - timedelta(days=days)).isoformat()
                query += " WHERE date >= ?"
                params.append(start_date)
            
            query += " ORDER BY date DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    # Wellness session methods
    def add_wellness_session(self, activity_type: str, duration_minutes: Optional[int] = None,
                           notes: str = '', rating: Optional[int] = None,
                           mood_before: Optional[str] = None, mood_after: Optional[str] = None) -> str:
        """Add a wellness session"""
        session_id = str(uuid.uuid4())
        date = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO wellness_sessions 
                (id, activity_type, duration_minutes, date, notes, rating, mood_before, mood_after)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, activity_type, duration_minutes, date, notes, rating, mood_before, mood_after))
            conn.commit()
        
        # Check for achievements
        self._check_achievements()
        
        return session_id
    
    def get_wellness_sessions(self, limit: int = 50, days: Optional[int] = None) -> List[Dict]:
        """Get wellness sessions"""
        with self.get_connection() as conn:
            query = "SELECT * FROM wellness_sessions"
            params = []
            
            if days:
                start_date = (datetime.now() - timedelta(days=days)).isoformat()
                query += " WHERE date >= ?"
                params.append(start_date)
            
            query += " ORDER BY date DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    # Goal methods
    def add_wellness_goal(self, title: str, description: str = '', category: str = 'general',
                         target_value: int = 1, unit: str = 'times',
                         target_date: Optional[str] = None, priority: str = 'medium') -> str:
        """Add a wellness goal"""
        goal_id = str(uuid.uuid4())
        created_date = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO wellness_goals 
                (id, title, description, category, target_value, unit, created_date, target_date, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (goal_id, title, description, category, target_value, unit, created_date, target_date, priority))
            conn.commit()
        
        return goal_id
    
    def update_goal_progress(self, goal_id: str, increment: int = 1) -> bool:
        """Update goal progress"""
        with self.get_connection() as conn:
            # Get current progress
            cursor = conn.execute('''
                SELECT current_value, target_value, completed 
                FROM wellness_goals WHERE id = ?
            ''', (goal_id,))
            
            goal = cursor.fetchone()
            if not goal:
                return False
            
            new_value = goal['current_value'] + increment
            completed = new_value >= goal['target_value']
            completed_date = datetime.now().isoformat() if completed and not goal['completed'] else None
            
            conn.execute('''
                UPDATE wellness_goals 
                SET current_value = ?, completed = ?, completed_date = ?
                WHERE id = ?
            ''', (new_value, completed, completed_date, goal_id))
            conn.commit()
            
            return True
    
    def get_wellness_goals(self, active_only: bool = False) -> List[Dict]:
        """Get wellness goals"""
        with self.get_connection() as conn:
            query = "SELECT * FROM wellness_goals"
            if active_only:
                query += " WHERE completed = 0"
            query += " ORDER BY created_date DESC"
            
            cursor = conn.execute(query)
            goals = []
            
            for row in cursor.fetchall():
                goal = dict(row)
                # Calculate progress percentage
                if goal['target_value'] > 0:
                    goal['progress_percentage'] = min(100, (goal['current_value'] / goal['target_value']) * 100)
                else:
                    goal['progress_percentage'] = 0
                goals.append(goal)
            
            return goals
    
    # Achievement methods
    def _check_achievements(self):
        """Check and unlock achievements based on current data"""
        with self.get_connection() as conn:
            # Get all achievements
            cursor = conn.execute("SELECT * FROM achievements WHERE active = 1")
            achievements = cursor.fetchall()
            
            # Get already unlocked achievements
            cursor = conn.execute("SELECT achievement_id FROM user_achievements")
            unlocked = {row['achievement_id'] for row in cursor.fetchall()}
            
            for achievement in achievements:
                if achievement['id'] in unlocked:
                    continue
                
                criteria = json.loads(achievement['criteria'])
                if self._check_achievement_criteria(conn, criteria):
                    self._unlock_achievement(conn, achievement['id'])
    
    def _check_achievement_criteria(self, conn, criteria: Dict) -> bool:
        """Check if achievement criteria are met"""
        for criterion, target in criteria.items():
            if criterion == 'mood_entries':
                cursor = conn.execute("SELECT COUNT(*) as count FROM mood_entries")
                count = cursor.fetchone()['count']
                if count < target:
                    return False
            
            elif criterion == 'wellness_sessions':
                cursor = conn.execute("SELECT COUNT(*) as count FROM wellness_sessions")
                count = cursor.fetchone()['count']
                if count < target:
                    return False
            
            elif criterion == 'checkin_entries':
                cursor = conn.execute("SELECT COUNT(*) as count FROM checkin_entries")
                count = cursor.fetchone()['count']
                if count < target:
                    return False
            
            elif criterion == 'wellness_goals':
                cursor = conn.execute("SELECT COUNT(*) as count FROM wellness_goals")
                count = cursor.fetchone()['count']
                if count < target:
                    return False
            
            elif criterion == 'consecutive_mood_days':
                # Simplified consecutive days check
                cursor = conn.execute('''
                    SELECT date FROM mood_entries 
                    ORDER BY date DESC LIMIT ?
                ''', (target,))
                dates = [row['date'] for row in cursor.fetchall()]
                
                if len(dates) < target:
                    return False
                
                # Check if dates are consecutive (simplified)
                # In a real implementation, you'd want more sophisticated date checking
        
        return True
    
    def _unlock_achievement(self, conn, achievement_id: str):
        """Unlock an achievement"""
        conn.execute('''
            INSERT INTO user_achievements (achievement_id)
            VALUES (?)
        ''', (achievement_id,))
        conn.commit()
    
    def get_user_achievements(self) -> List[Dict]:
        """Get user's unlocked achievements"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT a.*, ua.unlocked_at
                FROM achievements a
                JOIN user_achievements ua ON a.id = ua.achievement_id
                ORDER BY ua.unlocked_at DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    # Dashboard and analytics
    def get_dashboard_data(self) -> Dict:
        """Get comprehensive dashboard data"""
        with self.get_connection() as conn:
            # Recent mood entries
            cursor = conn.execute('''
                SELECT * FROM mood_entries 
                ORDER BY date DESC LIMIT 7
            ''')
            recent_moods = [dict(row) for row in cursor.fetchall()]
            
            # Recent wellness sessions
            cursor = conn.execute('''
                SELECT * FROM wellness_sessions 
                ORDER BY date DESC LIMIT 10
            ''')
            recent_sessions = [dict(row) for row in cursor.fetchall()]
            
            # Active goals
            cursor = conn.execute('''
                SELECT * FROM wellness_goals 
                WHERE completed = 0 
                ORDER BY created_date DESC
            ''')
            active_goals = [dict(row) for row in cursor.fetchall()]
            
            # Achievement count
            cursor = conn.execute("SELECT COUNT(*) as count FROM user_achievements")
            achievement_count = cursor.fetchone()['count']
            
            # Calculate wellness score (simplified)
            wellness_score = self._calculate_wellness_score(conn)
            
            return {
                'wellness_score': wellness_score,
                'recent_moods': recent_moods,
                'recent_sessions': recent_sessions,
                'active_goals': active_goals,
                'achievement_count': achievement_count,
                'mood_trend': self._get_mood_trend(recent_moods),
                'session_stats': self._get_session_stats(recent_sessions)
            }
    
    def _calculate_wellness_score(self, conn) -> float:
        """Calculate overall wellness score"""
        # Get recent data (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        
        # Mood score
        cursor = conn.execute('''
            SELECT AVG(intensity) as avg_intensity
            FROM mood_entries 
            WHERE date >= ? AND intensity IS NOT NULL
        ''', (week_ago,))
        
        mood_result = cursor.fetchone()
        mood_score = (mood_result['avg_intensity'] or 5) * 10  # Scale to 0-100
        
        # Activity score (wellness sessions)
        cursor = conn.execute('''
            SELECT COUNT(*) as session_count
            FROM wellness_sessions 
            WHERE date >= ?
        ''', (week_ago,))
        
        session_count = cursor.fetchone()['session_count']
        activity_score = min(30, session_count * 5)  # Up to 30 points for activity
        
        # Consistency score (check-ins)
        cursor = conn.execute('''
            SELECT COUNT(*) as checkin_count
            FROM checkin_entries 
            WHERE date >= ?
        ''', (week_ago,))
        
        checkin_count = cursor.fetchone()['checkin_count']
        consistency_score = min(20, checkin_count * 3)  # Up to 20 points for consistency
        
        total_score = min(100, mood_score + activity_score + consistency_score)
        return round(total_score, 1)
    
    def _get_mood_trend(self, recent_moods: List[Dict]) -> str:
        """Analyze mood trend"""
        if len(recent_moods) < 3:
            return 'insufficient_data'
        
        # Simple trend analysis based on intensity
        intensities = [mood.get('intensity', 5) for mood in recent_moods if mood.get('intensity')]
        
        if len(intensities) < 3:
            return 'stable'
        
        # Compare first half to second half
        mid = len(intensities) // 2
        first_half_avg = sum(intensities[:mid]) / mid
        second_half_avg = sum(intensities[mid:]) / (len(intensities) - mid)
        
        if second_half_avg > first_half_avg + 0.5:
            return 'improving'
        elif second_half_avg < first_half_avg - 0.5:
            return 'declining'
        else:
            return 'stable'
    
    def _get_session_stats(self, recent_sessions: List[Dict]) -> Dict:
        """Get wellness session statistics"""
        if not recent_sessions:
            return {'total': 0, 'favorite_activity': None, 'avg_rating': 0}
        
        # Count activities
        activity_counts = {}
        ratings = []
        
        for session in recent_sessions:
            activity = session['activity_type']
            activity_counts[activity] = activity_counts.get(activity, 0) + 1
            
            if session['rating']:
                ratings.append(session['rating'])
        
        favorite_activity = max(activity_counts.items(), key=lambda x: x[1])[0] if activity_counts else None
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        return {
            'total': len(recent_sessions),
            'favorite_activity': favorite_activity,
            'avg_rating': round(avg_rating, 1),
            'activity_distribution': activity_counts
        }
    
    # Backup and maintenance
    def create_backup(self, backup_name: Optional[str] = None) -> str:
        """Create a backup of the database"""
        if backup_name is None:
            backup_name = f"om_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_id = str(uuid.uuid4())
        backup_dir = Path(self.db_path).parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        backup_path = backup_dir / f"{backup_name}.db"
        
        # Copy database file
        import shutil
        shutil.copy2(self.db_path, backup_path)
        
        # Record backup metadata
        with self.get_connection() as conn:
            file_size = backup_path.stat().st_size
            conn.execute('''
                INSERT INTO backups (id, name, file_path, size_bytes, version)
                VALUES (?, ?, ?, ?, ?)
            ''', (backup_id, backup_name, str(backup_path), file_size, '2.0.0'))
            conn.commit()
        
        return str(backup_path)
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        with self.get_connection() as conn:
            stats = {}
            
            tables = [
                'mood_entries', 'checkin_entries', 'wellness_sessions',
                'wellness_goals', 'journal_entries', 'achievements',
                'user_achievements', 'wellness_insights', 'quick_actions'
            ]
            
            for table in tables:
                cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table}")
                stats[table] = cursor.fetchone()['count']
            
            # Database file size
            db_size = Path(self.db_path).stat().st_size
            stats['database_size_bytes'] = db_size
            stats['database_size_mb'] = round(db_size / (1024 * 1024), 2)
            
            return stats
    
    # Quick actions
    def log_quick_action(self, action_type: str, data: Dict) -> str:
        """Log a quick action"""
        action_id = str(uuid.uuid4())
        date = datetime.now().isoformat()
        data_json = json.dumps(data)
        
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO quick_actions (id, action_type, data, date)
                VALUES (?, ?, ?, ?)
            ''', (action_id, action_type, data_json, date))
            conn.commit()
        
        return action_id
    
    def close(self):
        """Close the storage system (cleanup if needed)"""
        # SQLite connections are closed automatically in context managers
        pass
