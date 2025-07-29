-- Sleep Sounds & Insomnia Support Database Schema
-- This schema supports comprehensive sleep tracking and sound management

-- Sleep sessions tracking
CREATE TABLE IF NOT EXISTS sleep_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    duration_minutes INTEGER,
    sounds_used TEXT, -- JSON array of sounds
    volume_levels TEXT, -- JSON object of sound:volume pairs
    sleep_timer_minutes INTEGER,
    quality_rating INTEGER CHECK(quality_rating >= 1 AND quality_rating <= 5),
    mood_before TEXT,
    mood_after TEXT,
    notes TEXT,
    sleep_efficiency REAL, -- percentage of time actually sleeping
    interruptions INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Sound library with mental health categorization
CREATE TABLE IF NOT EXISTS sound_library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    file_path TEXT,
    description TEXT,
    duration_seconds INTEGER,
    is_loopable BOOLEAN DEFAULT TRUE,
    mental_health_tags TEXT, -- JSON array of tags like 'anxiety', 'depression', 'ptsd'
    usage_count INTEGER DEFAULT 0,
    avg_rating REAL DEFAULT 0.0,
    total_ratings INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Custom sound mixes created by users
CREATE TABLE IF NOT EXISTS sound_mixes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    sounds TEXT NOT NULL, -- JSON array of sound names
    volumes TEXT NOT NULL, -- JSON object of sound:volume pairs
    description TEXT,
    category TEXT DEFAULT 'custom',
    usage_count INTEGER DEFAULT 0,
    avg_rating REAL DEFAULT 0.0,
    is_favorite BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Daily sleep quality analytics
CREATE TABLE IF NOT EXISTS sleep_analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL UNIQUE,
    total_sessions INTEGER DEFAULT 0,
    total_duration_minutes INTEGER DEFAULT 0,
    avg_duration REAL DEFAULT 0.0,
    avg_quality REAL DEFAULT 0.0,
    most_used_sounds TEXT, -- JSON array
    sleep_efficiency REAL DEFAULT 0.0,
    mood_improvement REAL DEFAULT 0.0,
    insomnia_severity INTEGER DEFAULT 0, -- 0-4 scale
    sleep_onset_time INTEGER DEFAULT 0, -- minutes to fall asleep
    wake_frequency INTEGER DEFAULT 0 -- number of times woken up
);

-- User preferences and settings
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    default_timer_minutes INTEGER DEFAULT 30,
    default_volume INTEGER DEFAULT 50,
    auto_fade_out BOOLEAN DEFAULT TRUE,
    fade_duration_seconds INTEGER DEFAULT 60,
    background_mode BOOLEAN DEFAULT TRUE,
    preferred_categories TEXT, -- JSON array
    notification_enabled BOOLEAN DEFAULT TRUE,
    sleep_goal_hours REAL DEFAULT 8.0,
    bedtime_reminder TEXT, -- HH:MM format
    wake_time_reminder TEXT, -- HH:MM format
    dark_mode BOOLEAN DEFAULT TRUE
);

-- Sound ratings and reviews
CREATE TABLE IF NOT EXISTS sound_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sound_name TEXT NOT NULL,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    review TEXT,
    effectiveness_tags TEXT, -- JSON array of effectiveness tags
    mental_health_condition TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sound_name) REFERENCES sound_library(name)
);

-- Sleep disorders and conditions tracking
CREATE TABLE IF NOT EXISTS sleep_conditions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    condition_name TEXT NOT NULL,
    severity INTEGER CHECK(severity >= 1 AND severity <= 5),
    symptoms TEXT, -- JSON array
    triggers TEXT, -- JSON array
    effective_sounds TEXT, -- JSON array
    notes TEXT,
    diagnosed_date TEXT,
    last_updated TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Integration with other om modules
CREATE TABLE IF NOT EXISTS module_integrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    module_name TEXT NOT NULL, -- 'mood_tracking', 'mental_health_classifier', etc.
    integration_type TEXT NOT NULL,
    data TEXT, -- JSON data for integration
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sleep_sessions(id)
);

-- Sleep environment factors
CREATE TABLE IF NOT EXISTS sleep_environment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    room_temperature REAL,
    humidity_level REAL,
    noise_level INTEGER, -- 1-10 scale
    light_level INTEGER, -- 1-10 scale
    comfort_rating INTEGER CHECK(comfort_rating >= 1 AND comfort_rating <= 5),
    environmental_notes TEXT,
    FOREIGN KEY (session_id) REFERENCES sleep_sessions(id)
);

-- Sleep goals and challenges
CREATE TABLE IF NOT EXISTS sleep_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_type TEXT NOT NULL, -- 'duration', 'quality', 'consistency', 'onset_time'
    target_value REAL NOT NULL,
    current_value REAL DEFAULT 0.0,
    start_date TEXT NOT NULL,
    end_date TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    progress_percentage REAL DEFAULT 0.0,
    reward_earned BOOLEAN DEFAULT FALSE
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_sleep_sessions_date ON sleep_sessions(date);
CREATE INDEX IF NOT EXISTS idx_sleep_sessions_quality ON sleep_sessions(quality_rating);
CREATE INDEX IF NOT EXISTS idx_sound_library_category ON sound_library(category);
CREATE INDEX IF NOT EXISTS idx_sound_library_tags ON sound_library(mental_health_tags);
CREATE INDEX IF NOT EXISTS idx_sound_mixes_favorite ON sound_mixes(is_favorite);
CREATE INDEX IF NOT EXISTS idx_analytics_date ON sleep_analytics(date);
CREATE INDEX IF NOT EXISTS idx_ratings_sound ON sound_ratings(sound_name);

-- Views for common queries
CREATE VIEW IF NOT EXISTS sleep_quality_trends AS
SELECT 
    date,
    avg_quality,
    total_sessions,
    avg_duration,
    sleep_efficiency,
    LAG(avg_quality) OVER (ORDER BY date) as prev_quality,
    (avg_quality - LAG(avg_quality) OVER (ORDER BY date)) as quality_change
FROM sleep_analytics
WHERE total_sessions > 0
ORDER BY date DESC;

CREATE VIEW IF NOT EXISTS popular_sounds AS
SELECT 
    sl.name,
    sl.category,
    sl.description,
    sl.mental_health_tags,
    sl.usage_count,
    sl.avg_rating,
    COUNT(sr.id) as review_count
FROM sound_library sl
LEFT JOIN sound_ratings sr ON sl.name = sr.sound_name
WHERE sl.is_active = TRUE
GROUP BY sl.name, sl.category, sl.description, sl.mental_health_tags, sl.usage_count, sl.avg_rating
ORDER BY sl.usage_count DESC, sl.avg_rating DESC;

CREATE VIEW IF NOT EXISTS mental_health_sound_recommendations AS
SELECT 
    sl.name,
    sl.category,
    sl.description,
    sl.mental_health_tags,
    sl.avg_rating,
    AVG(sr.rating) as user_rating,
    COUNT(sr.id) as rating_count
FROM sound_library sl
LEFT JOIN sound_ratings sr ON sl.name = sr.sound_name
WHERE sl.is_active = TRUE AND sl.mental_health_tags IS NOT NULL
GROUP BY sl.name, sl.category, sl.description, sl.mental_health_tags, sl.avg_rating
HAVING AVG(sr.rating) >= 3.5 OR sl.avg_rating >= 3.5
ORDER BY user_rating DESC, sl.avg_rating DESC;

CREATE VIEW IF NOT EXISTS sleep_session_summary AS
SELECT 
    ss.date,
    ss.duration_minutes,
    ss.quality_rating,
    ss.sounds_used,
    ss.sleep_timer_minutes,
    ss.mood_before,
    ss.mood_after,
    CASE 
        WHEN ss.mood_after > ss.mood_before THEN 'Improved'
        WHEN ss.mood_after < ss.mood_before THEN 'Declined'
        ELSE 'Stable'
    END as mood_change
FROM sleep_sessions ss
WHERE ss.end_time IS NOT NULL
ORDER BY ss.date DESC, ss.start_time DESC;

-- Triggers for automatic updates
CREATE TRIGGER IF NOT EXISTS update_sound_usage_stats
AFTER INSERT ON sleep_sessions
WHEN NEW.sounds_used IS NOT NULL
BEGIN
    UPDATE sound_library 
    SET usage_count = usage_count + 1
    WHERE name IN (
        SELECT value FROM json_each(NEW.sounds_used)
    );
END;

CREATE TRIGGER IF NOT EXISTS update_daily_analytics
AFTER UPDATE ON sleep_sessions
WHEN NEW.end_time IS NOT NULL AND OLD.end_time IS NULL
BEGIN
    INSERT OR REPLACE INTO sleep_analytics (
        date, total_sessions, total_duration_minutes, avg_duration, avg_quality
    )
    SELECT 
        NEW.date,
        COUNT(*) as total_sessions,
        SUM(duration_minutes) as total_duration,
        AVG(duration_minutes) as avg_duration,
        AVG(quality_rating) as avg_quality
    FROM sleep_sessions 
    WHERE date = NEW.date AND end_time IS NOT NULL;
END;

CREATE TRIGGER IF NOT EXISTS update_sound_ratings
AFTER INSERT ON sound_ratings
BEGIN
    UPDATE sound_library 
    SET avg_rating = (
        SELECT AVG(rating) FROM sound_ratings WHERE sound_name = NEW.sound_name
    ),
    total_ratings = (
        SELECT COUNT(*) FROM sound_ratings WHERE sound_name = NEW.sound_name
    )
    WHERE name = NEW.sound_name;
END;

CREATE TRIGGER IF NOT EXISTS update_mix_usage
AFTER INSERT ON sleep_sessions
WHEN NEW.sounds_used IS NOT NULL
BEGIN
    UPDATE sound_mixes 
    SET usage_count = usage_count + 1
    WHERE sounds = NEW.sounds_used;
END;

-- Initialize default categories and preferences
INSERT OR IGNORE INTO user_preferences (id) VALUES (1);

-- Insert default sound categories data would go here
-- (This would be populated by the Python initialization code)
