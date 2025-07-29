-- Om Mental Health Platform - SQLite Database Schema
-- Extends existing logbuch.db structure for comprehensive mental health tracking

-- ============================================================================
-- CORE MENTAL HEALTH TRACKING TABLES
-- ============================================================================

-- Enhanced mood tracking (extends existing mood_entries)
CREATE TABLE IF NOT EXISTS mood_entries_extended (
    id TEXT PRIMARY KEY,
    mood_score INTEGER CHECK (mood_score >= 1 AND mood_score <= 10),
    energy_level INTEGER CHECK (energy_level >= 1 AND energy_level <= 10),
    stress_level INTEGER CHECK (stress_level >= 1 AND stress_level <= 10),
    anxiety_level INTEGER CHECK (anxiety_level >= 1 AND anxiety_level <= 10),
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    notes TEXT,
    triggers TEXT, -- JSON array of triggers
    coping_strategies TEXT, -- JSON array of strategies used
    location TEXT,
    weather TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Wellness sessions (breathing, meditation, etc.)
CREATE TABLE IF NOT EXISTS wellness_sessions (
    id TEXT PRIMARY KEY,
    session_type TEXT NOT NULL, -- 'breathing', 'meditation', 'gratitude', etc.
    technique TEXT, -- '4-7-8', 'box_breathing', 'mindfulness', etc.
    duration_seconds INTEGER,
    effectiveness_rating INTEGER CHECK (effectiveness_rating >= 1 AND effectiveness_rating <= 10),
    notes TEXT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    completed BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crisis support tracking
CREATE TABLE IF NOT EXISTS crisis_events (
    id TEXT PRIMARY KEY,
    severity_level INTEGER CHECK (severity_level >= 1 AND severity_level <= 5),
    trigger_description TEXT,
    support_used TEXT, -- JSON array of support resources used
    outcome TEXT,
    follow_up_needed BOOLEAN DEFAULT 0,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    resolved BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- ============================================================================
-- AI COACHING SYSTEM
-- ============================================================================

-- AI coaching insights and recommendations
CREATE TABLE IF NOT EXISTS coaching_insights (
    id TEXT PRIMARY KEY,
    insight_type TEXT NOT NULL, -- 'daily', 'pattern', 'urgent', 'recommendation'
    content TEXT NOT NULL,
    confidence_score REAL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    data_sources TEXT, -- JSON array of data sources used
    effectiveness_rating INTEGER CHECK (effectiveness_rating >= 1 AND effectiveness_rating <= 10),
    user_feedback TEXT,
    date TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acted_upon BOOLEAN DEFAULT 0,
    acted_upon_at TIMESTAMP
);

-- Pattern analysis results
CREATE TABLE IF NOT EXISTS pattern_analysis (
    id TEXT PRIMARY KEY,
    pattern_type TEXT NOT NULL, -- 'mood_trend', 'trigger_pattern', 'effectiveness_pattern'
    pattern_description TEXT NOT NULL,
    confidence_level REAL CHECK (confidence_level >= 0 AND confidence_level <= 1),
    data_period_start TEXT,
    data_period_end TEXT,
    recommendations TEXT, -- JSON array of recommendations
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- ============================================================================
-- WELLNESS AUTOPILOT SYSTEM
-- ============================================================================

-- Automated wellness tasks
CREATE TABLE IF NOT EXISTS autopilot_tasks (
    id TEXT PRIMARY KEY,
    task_type TEXT NOT NULL, -- 'breathing', 'mood_check', 'gratitude', etc.
    title TEXT NOT NULL,
    description TEXT,
    priority INTEGER CHECK (priority >= 1 AND priority <= 5),
    estimated_duration_minutes INTEGER,
    auto_generated BOOLEAN DEFAULT 1,
    generation_reason TEXT,
    due_date TEXT,
    due_time TEXT,
    completed BOOLEAN DEFAULT 0,
    completion_rating INTEGER CHECK (completion_rating >= 1 AND completion_rating <= 10),
    completion_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Autopilot learning data
CREATE TABLE IF NOT EXISTS autopilot_learning (
    id TEXT PRIMARY KEY,
    user_preference_type TEXT NOT NULL, -- 'time_preference', 'activity_preference', etc.
    preference_value TEXT NOT NULL,
    confidence_score REAL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    data_points_count INTEGER DEFAULT 1,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- ============================================================================
-- GAMIFICATION SYSTEM
-- ============================================================================

-- User progress and stats
CREATE TABLE IF NOT EXISTS user_stats (
    id INTEGER PRIMARY KEY CHECK (id = 1), -- Singleton table
    current_level INTEGER DEFAULT 1,
    total_xp INTEGER DEFAULT 0,
    wellness_points INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    total_sessions INTEGER DEFAULT 0,
    total_mood_entries INTEGER DEFAULT 0,
    total_breathing_sessions INTEGER DEFAULT 0,
    total_meditation_minutes INTEGER DEFAULT 0,
    last_activity_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Achievements system
CREATE TABLE IF NOT EXISTS achievements (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL, -- 'mood', 'breathing', 'consistency', etc.
    requirement_type TEXT NOT NULL, -- 'count', 'streak', 'milestone'
    requirement_value INTEGER NOT NULL,
    xp_reward INTEGER DEFAULT 0,
    points_reward INTEGER DEFAULT 0,
    icon TEXT,
    is_hidden BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User achievement progress
CREATE TABLE IF NOT EXISTS user_achievements (
    id TEXT PRIMARY KEY,
    achievement_id TEXT NOT NULL,
    current_progress INTEGER DEFAULT 0,
    is_unlocked BOOLEAN DEFAULT 0,
    unlocked_at TIMESTAMP,
    FOREIGN KEY (achievement_id) REFERENCES achievements(id)
);

-- Daily challenges
CREATE TABLE IF NOT EXISTS daily_challenges (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    challenge_type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    target_value INTEGER,
    current_progress INTEGER DEFAULT 0,
    xp_reward INTEGER DEFAULT 0,
    points_reward INTEGER DEFAULT 0,
    completed BOOLEAN DEFAULT 0,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- WELLNESS TRACKING TABLES
-- ============================================================================

-- Gratitude entries
CREATE TABLE IF NOT EXISTS gratitude_entries (
    id TEXT PRIMARY KEY,
    gratitude_text TEXT NOT NULL,
    category TEXT, -- 'people', 'experiences', 'things', etc.
    intensity INTEGER CHECK (intensity >= 1 AND intensity <= 10),
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Physical wellness activities
CREATE TABLE IF NOT EXISTS physical_activities (
    id TEXT PRIMARY KEY,
    activity_type TEXT NOT NULL, -- 'back_exercise', 'hand_exercise', 'quick_workout'
    duration_minutes INTEGER,
    intensity INTEGER CHECK (intensity >= 1 AND intensity <= 10),
    effectiveness_rating INTEGER CHECK (effectiveness_rating >= 1 AND effectiveness_rating <= 10),
    notes TEXT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Habit tracking
CREATE TABLE IF NOT EXISTS habits (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT, -- 'mental_health', 'physical', 'social', etc.
    target_frequency TEXT, -- 'daily', 'weekly', 'custom'
    target_count INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Habit completion tracking
CREATE TABLE IF NOT EXISTS habit_completions (
    id TEXT PRIMARY KEY,
    habit_id TEXT NOT NULL,
    date TEXT NOT NULL,
    completed_count INTEGER DEFAULT 1,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (habit_id) REFERENCES habits(id)
);

-- ============================================================================
-- SOCIAL AND LEARNING TABLES
-- ============================================================================

-- Learning progress
CREATE TABLE IF NOT EXISTS learning_progress (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL, -- 'anxiety_management', 'depression_support', etc.
    module_name TEXT NOT NULL,
    progress_percentage INTEGER CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    completed BOOLEAN DEFAULT 0,
    time_spent_minutes INTEGER DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Social connection tracking
CREATE TABLE IF NOT EXISTS social_connections (
    id TEXT PRIMARY KEY,
    connection_type TEXT NOT NULL, -- 'family', 'friend', 'professional', etc.
    interaction_quality INTEGER CHECK (interaction_quality >= 1 AND interaction_quality <= 10),
    duration_minutes INTEGER,
    notes TEXT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SYSTEM AND CONFIGURATION TABLES
-- ============================================================================

-- User preferences and settings
CREATE TABLE IF NOT EXISTS user_preferences (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    data_type TEXT DEFAULT 'string', -- 'string', 'integer', 'boolean', 'json'
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data export logs
CREATE TABLE IF NOT EXISTS export_logs (
    id TEXT PRIMARY KEY,
    export_type TEXT NOT NULL, -- 'full', 'mood_only', 'dashboard', etc.
    file_path TEXT,
    date_range_start TEXT,
    date_range_end TEXT,
    record_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Backup logs
CREATE TABLE IF NOT EXISTS backup_logs (
    id TEXT PRIMARY KEY,
    backup_type TEXT NOT NULL, -- 'automatic', 'manual'
    file_path TEXT NOT NULL,
    file_size_bytes INTEGER,
    tables_included TEXT, -- JSON array of table names
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    restore_tested BOOLEAN DEFAULT 0
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Mood tracking indexes
CREATE INDEX IF NOT EXISTS idx_mood_entries_date ON mood_entries_extended(date);
CREATE INDEX IF NOT EXISTS idx_mood_entries_mood_score ON mood_entries_extended(mood_score);

-- Wellness sessions indexes
CREATE INDEX IF NOT EXISTS idx_wellness_sessions_date ON wellness_sessions(date);
CREATE INDEX IF NOT EXISTS idx_wellness_sessions_type ON wellness_sessions(session_type);

-- Coaching insights indexes
CREATE INDEX IF NOT EXISTS idx_coaching_insights_date ON coaching_insights(date);
CREATE INDEX IF NOT EXISTS idx_coaching_insights_type ON coaching_insights(insight_type);

-- Autopilot tasks indexes
CREATE INDEX IF NOT EXISTS idx_autopilot_tasks_due_date ON autopilot_tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_autopilot_tasks_completed ON autopilot_tasks(completed);

-- Achievement indexes
CREATE INDEX IF NOT EXISTS idx_user_achievements_unlocked ON user_achievements(is_unlocked);
CREATE INDEX IF NOT EXISTS idx_daily_challenges_date ON daily_challenges(date);

-- Habit tracking indexes
CREATE INDEX IF NOT EXISTS idx_habit_completions_date ON habit_completions(date);
CREATE INDEX IF NOT EXISTS idx_habit_completions_habit_id ON habit_completions(habit_id);

-- ============================================================================
-- TRIGGERS FOR DATA INTEGRITY AND AUTOMATION
-- ============================================================================

-- Update user stats when mood entry is added
CREATE TRIGGER IF NOT EXISTS update_stats_on_mood_entry
AFTER INSERT ON mood_entries_extended
BEGIN
    UPDATE user_stats 
    SET total_mood_entries = total_mood_entries + 1,
        last_activity_date = NEW.date,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = 1;
END;

-- Update user stats when wellness session is completed
CREATE TRIGGER IF NOT EXISTS update_stats_on_wellness_session
AFTER INSERT ON wellness_sessions
BEGIN
    UPDATE user_stats 
    SET total_sessions = total_sessions + 1,
        total_breathing_sessions = CASE 
            WHEN NEW.session_type = 'breathing' THEN total_breathing_sessions + 1 
            ELSE total_breathing_sessions 
        END,
        total_meditation_minutes = CASE 
            WHEN NEW.session_type = 'meditation' THEN total_meditation_minutes + (NEW.duration_seconds / 60)
            ELSE total_meditation_minutes 
        END,
        last_activity_date = NEW.date,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = 1;
END;

-- Initialize user stats if not exists
INSERT OR IGNORE INTO user_stats (id) VALUES (1);
