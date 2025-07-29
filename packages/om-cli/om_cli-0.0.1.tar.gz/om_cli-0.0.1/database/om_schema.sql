-- Om Mental Health Database Schema
-- Following logbuch.db pattern but focused on mental health tracking
-- Location: ~/.om/om.db

-- Configuration table (following logbuch pattern)
CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Core mood tracking (enhanced from existing mood_data.json)
CREATE TABLE mood_entries (
    id TEXT PRIMARY KEY,
    mood TEXT NOT NULL,
    level INTEGER CHECK (level >= 1 AND level <= 10),
    energy_level INTEGER CHECK (energy_level >= 1 AND energy_level <= 10),
    stress_level INTEGER CHECK (stress_level >= 1 AND stress_level <= 10),
    anxiety_level INTEGER CHECK (anxiety_level >= 1 AND anxiety_level <= 10),
    notes TEXT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mood tags (following logbuch journal_tags pattern)
CREATE TABLE mood_tags (
    entry_id TEXT,
    tag TEXT,
    PRIMARY KEY (entry_id, tag),
    FOREIGN KEY (entry_id) REFERENCES mood_entries(id)
);

-- Wellness sessions (breathing, meditation, etc.)
CREATE TABLE wellness_sessions (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    technique TEXT,
    duration_seconds INTEGER,
    effectiveness INTEGER CHECK (effectiveness >= 1 AND effectiveness <= 10),
    notes TEXT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Session tags
CREATE TABLE session_tags (
    session_id TEXT,
    tag TEXT,
    PRIMARY KEY (session_id, tag),
    FOREIGN KEY (session_id) REFERENCES wellness_sessions(id)
);

-- Gratitude entries
CREATE TABLE gratitude_entries (
    id TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    category TEXT,
    intensity INTEGER CHECK (intensity >= 1 AND intensity <= 10),
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mental health goals (following logbuch goals pattern)
CREATE TABLE wellness_goals (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    target_value INTEGER,
    current_progress INTEGER DEFAULT 0,
    target_date TEXT,
    completed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Daily wellness tasks (following logbuch tasks pattern)
CREATE TABLE wellness_tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT DEFAULT 'general',
    priority TEXT DEFAULT 'medium',
    estimated_minutes INTEGER,
    completed BOOLEAN DEFAULT 0,
    effectiveness INTEGER CHECK (effectiveness >= 1 AND effectiveness <= 10),
    date TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Task tags
CREATE TABLE task_tags (
    task_id TEXT,
    tag TEXT,
    PRIMARY KEY (task_id, tag),
    FOREIGN KEY (task_id) REFERENCES wellness_tasks(id)
);

-- Crisis support events
CREATE TABLE crisis_events (
    id TEXT PRIMARY KEY,
    severity INTEGER CHECK (severity >= 1 AND severity <= 5),
    description TEXT,
    triggers TEXT,
    support_used TEXT,
    outcome TEXT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    resolved BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Coaching insights (AI-generated or manual)
CREATE TABLE coaching_insights (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    confidence REAL CHECK (confidence >= 0 AND confidence <= 1),
    source TEXT,
    acted_upon BOOLEAN DEFAULT 0,
    effectiveness INTEGER CHECK (effectiveness >= 1 AND effectiveness <= 10),
    date TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User statistics and gamification
CREATE TABLE user_stats (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    wellness_points INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    total_mood_entries INTEGER DEFAULT 0,
    total_wellness_sessions INTEGER DEFAULT 0,
    total_meditation_minutes INTEGER DEFAULT 0,
    total_breathing_sessions INTEGER DEFAULT 0,
    total_gratitude_entries INTEGER DEFAULT 0,
    last_activity_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Achievements
CREATE TABLE achievements (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    requirement_type TEXT NOT NULL,
    requirement_value INTEGER NOT NULL,
    xp_reward INTEGER DEFAULT 0,
    points_reward INTEGER DEFAULT 0,
    icon TEXT,
    hidden BOOLEAN DEFAULT 0
);

-- User achievement progress
CREATE TABLE user_achievements (
    id TEXT PRIMARY KEY,
    achievement_id TEXT NOT NULL,
    progress INTEGER DEFAULT 0,
    unlocked BOOLEAN DEFAULT 0,
    unlocked_at TIMESTAMP,
    FOREIGN KEY (achievement_id) REFERENCES achievements(id)
);

-- Habit tracking
CREATE TABLE habits (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    frequency TEXT DEFAULT 'daily',
    target_count INTEGER DEFAULT 1,
    active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Habit completions
CREATE TABLE habit_completions (
    id TEXT PRIMARY KEY,
    habit_id TEXT NOT NULL,
    date TEXT NOT NULL,
    count INTEGER DEFAULT 1,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (habit_id) REFERENCES habits(id)
);

-- Sleep tracking (following logbuch sleep_entries pattern)
CREATE TABLE sleep_entries (
    id TEXT PRIMARY KEY,
    hours REAL,
    quality INTEGER CHECK (quality >= 1 AND quality <= 10),
    notes TEXT,
    date TEXT NOT NULL,
    bedtime TEXT,
    wake_time TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Physical wellness activities
CREATE TABLE physical_activities (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    duration_minutes INTEGER,
    intensity INTEGER CHECK (intensity >= 1 AND intensity <= 10),
    notes TEXT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Learning and growth tracking
CREATE TABLE learning_sessions (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    content TEXT,
    duration_minutes INTEGER,
    effectiveness INTEGER CHECK (effectiveness >= 1 AND effectiveness <= 10),
    notes TEXT,
    date TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Social connections and interactions
CREATE TABLE social_interactions (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    description TEXT,
    quality INTEGER CHECK (quality >= 1 AND quality <= 10),
    duration_minutes INTEGER,
    notes TEXT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Backup and export logs
CREATE TABLE backup_logs (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    file_path TEXT,
    size_bytes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data export logs
CREATE TABLE export_logs (
    id TEXT PRIMARY KEY,
    export_type TEXT NOT NULL,
    file_path TEXT,
    record_count INTEGER,
    date_range_start TEXT,
    date_range_end TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance (following logbuch pattern)
CREATE INDEX idx_mood_entries_date ON mood_entries(date);
CREATE INDEX idx_mood_entries_level ON mood_entries(level);
CREATE INDEX idx_wellness_sessions_date ON wellness_sessions(date);
CREATE INDEX idx_wellness_sessions_type ON wellness_sessions(type);
CREATE INDEX idx_gratitude_entries_date ON gratitude_entries(date);
CREATE INDEX idx_wellness_tasks_date ON wellness_tasks(date);
CREATE INDEX idx_wellness_tasks_completed ON wellness_tasks(completed);
CREATE INDEX idx_crisis_events_date ON crisis_events(date);
CREATE INDEX idx_coaching_insights_date ON coaching_insights(date);
CREATE INDEX idx_habit_completions_date ON habit_completions(date);
CREATE INDEX idx_sleep_entries_date ON sleep_entries(date);

-- Triggers for maintaining statistics (following logbuch pattern)
CREATE TRIGGER update_stats_mood_entry
AFTER INSERT ON mood_entries
BEGIN
    UPDATE user_stats 
    SET total_mood_entries = total_mood_entries + 1,
        last_activity_date = NEW.date,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = 1;
END;

CREATE TRIGGER update_stats_wellness_session
AFTER INSERT ON wellness_sessions
BEGIN
    UPDATE user_stats 
    SET total_wellness_sessions = total_wellness_sessions + 1,
        total_breathing_sessions = CASE 
            WHEN NEW.type = 'breathing' THEN total_breathing_sessions + 1 
            ELSE total_breathing_sessions 
        END,
        total_meditation_minutes = CASE 
            WHEN NEW.type = 'meditation' THEN total_meditation_minutes + (NEW.duration_seconds / 60)
            ELSE total_meditation_minutes 
        END,
        last_activity_date = NEW.date,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = 1;
END;

CREATE TRIGGER update_stats_gratitude_entry
AFTER INSERT ON gratitude_entries
BEGIN
    UPDATE user_stats 
    SET total_gratitude_entries = total_gratitude_entries + 1,
        last_activity_date = NEW.date,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = 1;
END;

-- Initialize user stats
INSERT OR IGNORE INTO user_stats (id) VALUES (1);

-- Insert default configuration
INSERT OR IGNORE INTO config (key, value) VALUES 
    ('version', '1.0'),
    ('created_date', datetime('now')),
    ('backup_enabled', 'true'),
    ('gamification_enabled', 'true'),
    ('privacy_mode', 'local_only');

-- Insert default achievements
INSERT OR IGNORE INTO achievements VALUES
    ('first_mood', 'First Mood Entry', 'Record your first mood', 'mood', 'count', 1, 10, 5, '😊', 0),
    ('mood_week', 'Weekly Tracker', 'Track mood for 7 days', 'mood', 'count', 7, 25, 15, '📊', 0),
    ('mood_month', 'Monthly Consistency', 'Track mood for 30 days', 'mood', 'count', 30, 100, 50, '🗓️', 0),
    ('first_breath', 'First Breath', 'Complete first breathing session', 'breathing', 'count', 1, 10, 5, '🫁', 0),
    ('breath_daily', 'Daily Breather', 'Complete breathing sessions for 7 days', 'breathing', 'streak', 7, 50, 25, '🌬️', 0),
    ('breath_master', 'Breathing Master', 'Complete 100 breathing sessions', 'breathing', 'count', 100, 200, 100, '🧘', 0),
    ('grateful_heart', 'Grateful Heart', 'Write first gratitude entry', 'gratitude', 'count', 1, 10, 5, '🙏', 0),
    ('gratitude_week', 'Week of Thanks', 'Practice gratitude for 7 days', 'gratitude', 'count', 7, 30, 20, '💝', 0),
    ('streak_3', 'Getting Started', 'Maintain 3-day wellness streak', 'consistency', 'streak', 3, 15, 10, '🔥', 0),
    ('streak_7', 'Week Warrior', 'Maintain 7-day wellness streak', 'consistency', 'streak', 7, 50, 30, '⚡', 0),
    ('streak_30', 'Monthly Master', 'Maintain 30-day wellness streak', 'consistency', 'streak', 30, 300, 150, '👑', 0),
    ('level_5', 'Rising Star', 'Reach level 5', 'milestone', 'level', 5, 100, 50, '⭐', 0),
    ('level_10', 'Wellness Warrior', 'Reach level 10', 'milestone', 'level', 10, 250, 125, '🏆', 0),
    ('self_care', 'Self Care Champion', 'Complete 10 wellness tasks', 'tasks', 'count', 10, 75, 40, '💆', 0),
    ('crisis_support', 'Seeking Help', 'Use crisis support resources', 'support', 'count', 1, 20, 10, '🆘', 1);
