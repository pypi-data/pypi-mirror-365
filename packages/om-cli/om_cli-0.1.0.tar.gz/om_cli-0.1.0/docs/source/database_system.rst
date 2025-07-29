Database System
===============

The om mental health platform uses a comprehensive SQLite3 storage system for robust local data management, adapted from productivity tools but optimized for wellness and mental health tracking.

🎯 Overview
-----------

The SQLite implementation provides:

- **Robust local storage** with ACID compliance
- **Comprehensive data models** for mental health tracking  
- **Performance optimized** queries and indexing
- **Backup and recovery** capabilities
- **Thread-safe operations** for concurrent access
- **Achievement system** with gamification
- **Analytics and insights** generation

🗄️ Database Schema
------------------

Core Tables
~~~~~~~~~~~

mood_entries
^^^^^^^^^^^^

Enhanced mood tracking with comprehensive data:

.. code-block:: sql

   CREATE TABLE mood_entries (
       id TEXT PRIMARY KEY,
       mood TEXT NOT NULL,
       intensity INTEGER,          -- 1-10 scale
       date TEXT NOT NULL,
       notes TEXT DEFAULT '',
       triggers TEXT,              -- JSON array of triggers
       location TEXT,
       energy_level INTEGER,       -- 1-10 scale
       stress_level INTEGER,       -- 1-10 scale
       created_at TEXT DEFAULT CURRENT_TIMESTAMP
   );

checkin_entries
^^^^^^^^^^^^^^^

Daily check-ins for comprehensive wellness tracking:

.. code-block:: sql

   CREATE TABLE checkin_entries (
       id TEXT PRIMARY KEY,
       date TEXT NOT NULL,
       type TEXT DEFAULT 'daily',  -- daily, morning, evening, quick
       mood TEXT,
       mood_intensity INTEGER,
       energy_level INTEGER,
       stress_level INTEGER,
       sleep_quality TEXT,         -- excellent, good, fair, poor
       sleep_hours REAL,
       going_well TEXT,
       challenges TEXT,
       goals TEXT,
       gratitude TEXT,
       notes TEXT,
       created_at TEXT DEFAULT CURRENT_TIMESTAMP
   );

wellness_sessions
^^^^^^^^^^^^^^^^^

Track all wellness activities and sessions:

.. code-block:: sql

   CREATE TABLE wellness_sessions (
       id TEXT PRIMARY KEY,
       session_type TEXT NOT NULL, -- breathing, meditation, gratitude, etc.
       duration INTEGER,           -- Duration in seconds
       date TEXT NOT NULL,
       effectiveness INTEGER,      -- 1-10 rating
       notes TEXT,
       technique TEXT,             -- Specific technique used
       mood_before TEXT,
       mood_after TEXT,
       created_at TEXT DEFAULT CURRENT_TIMESTAMP
   );

habits
^^^^^^

Habit tracking with streak and frequency management:

.. code-block:: sql

   CREATE TABLE habits (
       id TEXT PRIMARY KEY,
       name TEXT NOT NULL,
       description TEXT,
       frequency TEXT DEFAULT 'daily', -- daily, weekly, custom
       target_count INTEGER DEFAULT 1,
       category TEXT,                   -- wellness, exercise, mindfulness
       created_at TEXT DEFAULT CURRENT_TIMESTAMP,
       is_active BOOLEAN DEFAULT 1
   );

habit_completions
^^^^^^^^^^^^^^^^^

Track habit completion history:

.. code-block:: sql

   CREATE TABLE habit_completions (
       id TEXT PRIMARY KEY,
       habit_id TEXT NOT NULL,
       completion_date TEXT NOT NULL,
       notes TEXT,
       mood_impact INTEGER,        -- 1-10 scale
       created_at TEXT DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (habit_id) REFERENCES habits (id)
   );

Gamification Tables
~~~~~~~~~~~~~~~~~~~

achievements
^^^^^^^^^^^^

Achievement definitions and metadata:

.. code-block:: sql

   CREATE TABLE achievements (
       id TEXT PRIMARY KEY,
       name TEXT NOT NULL,
       description TEXT,
       category TEXT,              -- mood, breathing, gratitude, etc.
       rarity TEXT DEFAULT 'common', -- common, rare, epic, legendary
       points INTEGER DEFAULT 10,
       icon TEXT,
       unlock_criteria TEXT,       -- JSON criteria for unlocking
       created_at TEXT DEFAULT CURRENT_TIMESTAMP
   );

user_achievements
^^^^^^^^^^^^^^^^^

Track user's unlocked achievements:

.. code-block:: sql

   CREATE TABLE user_achievements (
       id TEXT PRIMARY KEY,
       achievement_id TEXT NOT NULL,
       unlocked_at TEXT DEFAULT CURRENT_TIMESTAMP,
       progress INTEGER DEFAULT 100, -- Percentage complete
       FOREIGN KEY (achievement_id) REFERENCES achievements (id)
   );

wellness_stats
^^^^^^^^^^^^^^

Gamification statistics and progress:

.. code-block:: sql

   CREATE TABLE wellness_stats (
       id TEXT PRIMARY KEY DEFAULT 'main',
       level INTEGER DEFAULT 1,
       total_points INTEGER DEFAULT 0,
       current_streak INTEGER DEFAULT 0,
       longest_streak INTEGER DEFAULT 0,
       total_sessions INTEGER DEFAULT 0,
       last_activity_date TEXT,
       created_at TEXT DEFAULT CURRENT_TIMESTAMP,
       updated_at TEXT DEFAULT CURRENT_TIMESTAMP
   );

AI and Coaching Tables
~~~~~~~~~~~~~~~~~~~~~~

coaching_insights
^^^^^^^^^^^^^^^^^

Store AI coaching insights and recommendations:

.. code-block:: sql

   CREATE TABLE coaching_insights (
       id TEXT PRIMARY KEY,
       insight_type TEXT NOT NULL, -- daily, pattern, urgent, recommendation
       title TEXT,
       content TEXT NOT NULL,
       priority INTEGER DEFAULT 1, -- 1=low, 2=medium, 3=high, 4=urgent
       data_sources TEXT,          -- JSON array of data used
       effectiveness_rating INTEGER, -- User feedback 1-10
       date_generated TEXT DEFAULT CURRENT_TIMESTAMP,
       date_viewed TEXT,
       is_dismissed BOOLEAN DEFAULT 0
   );

autopilot_tasks
^^^^^^^^^^^^^^^

Automated wellness task management:

.. code-block:: sql

   CREATE TABLE autopilot_tasks (
       id TEXT PRIMARY KEY,
       task_type TEXT NOT NULL,    -- breathing, gratitude, movement, etc.
       title TEXT NOT NULL,
       description TEXT,
       priority INTEGER DEFAULT 1,
       estimated_duration INTEGER, -- Minutes
       generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
       due_date TEXT,
       completed_at TEXT,
       effectiveness_rating INTEGER, -- User feedback 1-10
       notes TEXT
   );

pattern_analysis
^^^^^^^^^^^^^^^^

Store pattern analysis results:

.. code-block:: sql

   CREATE TABLE pattern_analysis (
       id TEXT PRIMARY KEY,
       analysis_type TEXT NOT NULL, -- mood_trends, trigger_patterns, etc.
       time_period TEXT,            -- week, month, quarter
       patterns_found TEXT,         -- JSON data
       insights TEXT,
       recommendations TEXT,
       confidence_score REAL,       -- 0.0-1.0
       generated_at TEXT DEFAULT CURRENT_TIMESTAMP
   );

Support and Crisis Tables
~~~~~~~~~~~~~~~~~~~~~~~~~

crisis_logs
^^^^^^^^^^^

Track crisis support usage (anonymized):

.. code-block:: sql

   CREATE TABLE crisis_logs (
       id TEXT PRIMARY KEY,
       crisis_type TEXT,           -- anxiety, depression, panic, etc.
       severity INTEGER,           -- 1-10 scale
       resources_accessed TEXT,    -- JSON array
       duration INTEGER,           -- Session duration in minutes
       outcome TEXT,               -- helped, neutral, need_more_support
       follow_up_needed BOOLEAN DEFAULT 0,
       created_at TEXT DEFAULT CURRENT_TIMESTAMP
   );

coping_strategies_usage
^^^^^^^^^^^^^^^^^^^^^^^

Track which coping strategies are most effective:

.. code-block:: sql

   CREATE TABLE coping_strategies_usage (
       id TEXT PRIMARY KEY,
       strategy_name TEXT NOT NULL,
       category TEXT,              -- breathing, grounding, distraction, etc.
       situation TEXT,             -- anxiety, depression, stress, etc.
       effectiveness INTEGER,      -- 1-10 rating
       duration INTEGER,           -- Minutes used
       notes TEXT,
       used_at TEXT DEFAULT CURRENT_TIMESTAMP
   );

🔧 Database Operations
---------------------

Connection Management
~~~~~~~~~~~~~~~~~~~~

The database uses connection pooling and proper transaction management:

.. code-block:: python

   import sqlite3
   import threading
   from contextlib import contextmanager
   
   class DatabaseManager:
       def __init__(self, db_path):
           self.db_path = db_path
           self.local = threading.local()
       
       @contextmanager
       def get_connection(self):
           if not hasattr(self.local, 'connection'):
               self.local.connection = sqlite3.connect(
                   self.db_path, 
                   check_same_thread=False
               )
               self.local.connection.row_factory = sqlite3.Row
           
           try:
               yield self.local.connection
           except Exception:
               self.local.connection.rollback()
               raise
           else:
               self.local.connection.commit()

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~

Key indexes for optimal query performance:

.. code-block:: sql

   -- Mood tracking indexes
   CREATE INDEX idx_mood_entries_date ON mood_entries(date);
   CREATE INDEX idx_mood_entries_mood ON mood_entries(mood);
   CREATE INDEX idx_mood_entries_created_at ON mood_entries(created_at);
   
   -- Wellness sessions indexes
   CREATE INDEX idx_wellness_sessions_type_date ON wellness_sessions(session_type, date);
   CREATE INDEX idx_wellness_sessions_date ON wellness_sessions(date);
   
   -- Habits indexes
   CREATE INDEX idx_habit_completions_habit_date ON habit_completions(habit_id, completion_date);
   CREATE INDEX idx_habits_active ON habits(is_active);
   
   -- Achievements indexes
   CREATE INDEX idx_user_achievements_unlocked ON user_achievements(unlocked_at);
   CREATE INDEX idx_achievements_category ON achievements(category);

Data Analytics Queries
~~~~~~~~~~~~~~~~~~~~~

Common analytics queries for insights:

**Mood Trends**:

.. code-block:: sql

   SELECT 
       date,
       AVG(intensity) as avg_mood,
       AVG(energy_level) as avg_energy,
       AVG(stress_level) as avg_stress
   FROM mood_entries 
   WHERE date >= date('now', '-30 days')
   GROUP BY date
   ORDER BY date;

**Habit Success Rates**:

.. code-block:: sql

   SELECT 
       h.name,
       COUNT(hc.id) as completions,
       COUNT(DISTINCT hc.completion_date) as days_completed,
       ROUND(COUNT(DISTINCT hc.completion_date) * 100.0 / 30, 2) as success_rate
   FROM habits h
   LEFT JOIN habit_completions hc ON h.id = hc.habit_id
   WHERE hc.completion_date >= date('now', '-30 days')
   GROUP BY h.id, h.name;

**Wellness Activity Patterns**:

.. code-block:: sql

   SELECT 
       session_type,
       COUNT(*) as session_count,
       AVG(duration) as avg_duration,
       AVG(effectiveness) as avg_effectiveness
   FROM wellness_sessions
   WHERE date >= date('now', '-7 days')
   GROUP BY session_type
   ORDER BY session_count DESC;

🔄 Data Migration and Backup
----------------------------

Migration System
~~~~~~~~~~~~~~~

Automatic schema migrations for version updates:

.. code-block:: python

   def migrate_database(db_path):
       """Apply database migrations"""
       with sqlite3.connect(db_path) as conn:
           # Check current version
           try:
               version = conn.execute(
                   "SELECT version FROM schema_version"
               ).fetchone()[0]
           except sqlite3.OperationalError:
               version = 0
           
           # Apply migrations
           migrations = [
               migrate_v1_to_v2,
               migrate_v2_to_v3,
               # Add new migrations here
           ]
           
           for i, migration in enumerate(migrations[version:], version + 1):
               migration(conn)
               conn.execute(
                   "INSERT OR REPLACE INTO schema_version VALUES (?)", 
                   (i,)
               )

Backup and Recovery
~~~~~~~~~~~~~~~~~~

Automated backup system:

.. code-block:: python

   def create_backup(db_path, backup_path):
       """Create a complete database backup"""
       with sqlite3.connect(db_path) as source:
           with sqlite3.connect(backup_path) as backup:
               source.backup(backup)
   
   def export_data_json(db_path, export_path):
       """Export data to JSON for external analysis"""
       with sqlite3.connect(db_path) as conn:
           conn.row_factory = sqlite3.Row
           
           data = {}
           tables = ['mood_entries', 'wellness_sessions', 'habits']
           
           for table in tables:
               cursor = conn.execute(f"SELECT * FROM {table}")
               data[table] = [dict(row) for row in cursor.fetchall()]
           
           with open(export_path, 'w') as f:
               json.dump(data, f, indent=2, default=str)

🔒 Privacy and Security
----------------------

Data Protection
~~~~~~~~~~~~~~

- **Local Storage Only**: All data remains on the user's device
- **No Cloud Sync**: No external data transmission
- **Encrypted Backups**: Optional encryption for sensitive data
- **User Control**: Complete user ownership of data

Privacy Features
~~~~~~~~~~~~~~~

.. code-block:: python

   def anonymize_crisis_data(crisis_log):
       """Remove identifying information from crisis logs"""
       return {
           'crisis_type': crisis_log['crisis_type'],
           'severity': crisis_log['severity'],
           'resources_accessed': crisis_log['resources_accessed'],
           'outcome': crisis_log['outcome'],
           # Remove: notes, specific times, identifying details
       }
   
   def secure_delete(db_path, table, record_id):
       """Securely delete sensitive records"""
       with sqlite3.connect(db_path) as conn:
           # First overwrite with random data
           conn.execute(f"""
               UPDATE {table} 
               SET notes = randomblob(length(notes))
               WHERE id = ?
           """, (record_id,))
           
           # Then delete
           conn.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))

📊 Analytics and Insights
-------------------------

Pattern Recognition
~~~~~~~~~~~~~~~~~~

The database supports advanced pattern recognition:

.. code-block:: sql

   -- Identify mood triggers
   WITH mood_patterns AS (
       SELECT 
           triggers,
           AVG(intensity) as avg_mood,
           COUNT(*) as frequency
       FROM mood_entries 
       WHERE triggers IS NOT NULL
       GROUP BY triggers
   )
   SELECT * FROM mood_patterns 
   WHERE frequency >= 3
   ORDER BY avg_mood ASC;

Wellness Insights
~~~~~~~~~~~~~~~~

Generate actionable insights from data:

.. code-block:: sql

   -- Most effective wellness activities
   SELECT 
       session_type,
       AVG(effectiveness) as avg_effectiveness,
       COUNT(*) as usage_count,
       AVG(duration) as avg_duration
   FROM wellness_sessions
   WHERE effectiveness IS NOT NULL
   GROUP BY session_type
   HAVING usage_count >= 5
   ORDER BY avg_effectiveness DESC;

🛠️ Database Maintenance
-----------------------

Regular Maintenance Tasks
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def maintain_database(db_path):
       """Perform regular database maintenance"""
       with sqlite3.connect(db_path) as conn:
           # Vacuum to reclaim space
           conn.execute("VACUUM")
           
           # Analyze for query optimization
           conn.execute("ANALYZE")
           
           # Clean old temporary data
           conn.execute("""
               DELETE FROM pattern_analysis 
               WHERE generated_at < date('now', '-90 days')
           """)
           
           # Archive old crisis logs (anonymized)
           conn.execute("""
               UPDATE crisis_logs 
               SET notes = NULL 
               WHERE created_at < date('now', '-30 days')
           """)

Health Checks
~~~~~~~~~~~~

.. code-block:: python

   def check_database_health(db_path):
       """Check database integrity and performance"""
       with sqlite3.connect(db_path) as conn:
           # Integrity check
           integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
           
           # Size check
           size = conn.execute("""
               SELECT page_count * page_size as size 
               FROM pragma_page_count(), pragma_page_size()
           """).fetchone()[0]
           
           # Index usage stats
           unused_indexes = conn.execute("""
               SELECT name FROM sqlite_master 
               WHERE type='index' AND name NOT IN (
                   SELECT DISTINCT idx FROM sqlite_stat1
               )
           """).fetchall()
           
           return {
               'integrity': integrity,
               'size_bytes': size,
               'unused_indexes': [idx[0] for idx in unused_indexes]
           }

The database system provides a robust foundation for the om mental health platform, ensuring data integrity, performance, and privacy while supporting advanced analytics and insights for user wellness tracking.
