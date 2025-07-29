-- Positive Affirmations Database Schema
-- This schema supports the affirmations module for daily positive affirmations

-- Main affirmations table
CREATE TABLE IF NOT EXISTS affirmations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phrase TEXT NOT NULL UNIQUE,
    category TEXT DEFAULT 'general',
    source TEXT DEFAULT 'dulce-affirmations-api',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- User interactions with affirmations
CREATE TABLE IF NOT EXISTS user_affirmations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    affirmation_id INTEGER,
    date TEXT NOT NULL,
    is_favorite BOOLEAN DEFAULT FALSE,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    notes TEXT,
    mood_before TEXT,
    mood_after TEXT,
    reflection TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (affirmation_id) REFERENCES affirmations(id)
);

-- Daily affirmations log to ensure one per day
CREATE TABLE IF NOT EXISTS daily_affirmations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL UNIQUE,
    affirmation_id INTEGER,
    viewed_at TEXT DEFAULT CURRENT_TIMESTAMP,
    time_spent INTEGER DEFAULT 0, -- seconds spent viewing
    shared BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (affirmation_id) REFERENCES affirmations(id)
);

-- Categories for organizing affirmations
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    color TEXT DEFAULT 'blue',
    icon TEXT DEFAULT '✨',
    is_active BOOLEAN DEFAULT TRUE
);

-- User statistics and progress tracking
CREATE TABLE IF NOT EXISTS affirmation_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    total_viewed INTEGER DEFAULT 0,
    favorites_count INTEGER DEFAULT 0,
    streak_days INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_viewed TEXT,
    avg_rating REAL DEFAULT 0.0,
    total_time_spent INTEGER DEFAULT 0, -- total seconds
    categories_explored INTEGER DEFAULT 0,
    custom_affirmations INTEGER DEFAULT 0
);

-- Custom user-created affirmations
CREATE TABLE IF NOT EXISTS custom_affirmations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phrase TEXT NOT NULL,
    category TEXT DEFAULT 'personal',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0
);

-- Affirmation sharing and community features
CREATE TABLE IF NOT EXISTS shared_affirmations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    affirmation_id INTEGER,
    shared_at TEXT DEFAULT CURRENT_TIMESTAMP,
    platform TEXT, -- 'twitter', 'facebook', 'instagram', etc.
    success BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (affirmation_id) REFERENCES affirmations(id)
);

-- Integration with other om modules
CREATE TABLE IF NOT EXISTS module_integrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    affirmation_id INTEGER,
    module_name TEXT NOT NULL, -- 'mood_tracking', 'mental_health_classifier', etc.
    integration_type TEXT NOT NULL,
    data TEXT, -- JSON data for integration
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (affirmation_id) REFERENCES affirmations(id)
);

-- Affirmation reminders and scheduling
CREATE TABLE IF NOT EXISTS affirmation_reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT NOT NULL, -- HH:MM format
    days_of_week TEXT DEFAULT '1,2,3,4,5,6,7', -- comma-separated
    category TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Performance analytics
CREATE TABLE IF NOT EXISTS affirmation_analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    affirmation_id INTEGER,
    category TEXT,
    rating INTEGER,
    time_spent INTEGER,
    mood_impact TEXT, -- 'positive', 'neutral', 'negative'
    FOREIGN KEY (affirmation_id) REFERENCES affirmations(id)
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_affirmations_category ON affirmations(category);
CREATE INDEX IF NOT EXISTS idx_affirmations_active ON affirmations(is_active);
CREATE INDEX IF NOT EXISTS idx_user_affirmations_date ON user_affirmations(date);
CREATE INDEX IF NOT EXISTS idx_user_affirmations_favorite ON user_affirmations(is_favorite);
CREATE INDEX IF NOT EXISTS idx_daily_affirmations_date ON daily_affirmations(date);
CREATE INDEX IF NOT EXISTS idx_analytics_date ON affirmation_analytics(date);
CREATE INDEX IF NOT EXISTS idx_analytics_category ON affirmation_analytics(category);

-- Views for common queries
CREATE VIEW IF NOT EXISTS popular_affirmations AS
SELECT 
    a.id,
    a.phrase,
    a.category,
    COUNT(ua.id) as usage_count,
    AVG(ua.rating) as avg_rating,
    COUNT(CASE WHEN ua.is_favorite = TRUE THEN 1 END) as favorite_count
FROM affirmations a
LEFT JOIN user_affirmations ua ON a.id = ua.affirmation_id
WHERE a.is_active = TRUE
GROUP BY a.id, a.phrase, a.category
ORDER BY usage_count DESC, avg_rating DESC;

CREATE VIEW IF NOT EXISTS category_stats AS
SELECT 
    c.name,
    c.description,
    c.color,
    c.icon,
    COUNT(a.id) as affirmation_count,
    COUNT(ua.id) as usage_count,
    AVG(ua.rating) as avg_rating
FROM categories c
LEFT JOIN affirmations a ON c.name = a.category AND a.is_active = TRUE
LEFT JOIN user_affirmations ua ON a.id = ua.affirmation_id
WHERE c.is_active = TRUE
GROUP BY c.name, c.description, c.color, c.icon
ORDER BY usage_count DESC;

CREATE VIEW IF NOT EXISTS recent_activity AS
SELECT 
    'daily' as activity_type,
    da.date,
    a.phrase,
    a.category,
    da.viewed_at as timestamp
FROM daily_affirmations da
JOIN affirmations a ON da.affirmation_id = a.id
UNION ALL
SELECT 
    'favorite' as activity_type,
    ua.date,
    a.phrase,
    a.category,
    ua.created_at as timestamp
FROM user_affirmations ua
JOIN affirmations a ON ua.affirmation_id = a.id
WHERE ua.is_favorite = TRUE
ORDER BY timestamp DESC
LIMIT 20;

-- Triggers for automatic updates
CREATE TRIGGER IF NOT EXISTS update_stats_on_daily_view
AFTER INSERT ON daily_affirmations
BEGIN
    UPDATE affirmation_stats 
    SET total_viewed = total_viewed + 1,
        last_viewed = NEW.viewed_at;
    
    -- Update longest streak if current streak is longer
    UPDATE affirmation_stats 
    SET longest_streak = CASE 
        WHEN streak_days > longest_streak THEN streak_days 
        ELSE longest_streak 
    END;
END;

CREATE TRIGGER IF NOT EXISTS update_stats_on_favorite
AFTER INSERT ON user_affirmations
WHEN NEW.is_favorite = TRUE
BEGIN
    UPDATE affirmation_stats 
    SET favorites_count = (
        SELECT COUNT(*) FROM user_affirmations WHERE is_favorite = TRUE
    );
END;

CREATE TRIGGER IF NOT EXISTS update_stats_on_rating
AFTER INSERT ON user_affirmations
WHEN NEW.rating IS NOT NULL
BEGIN
    UPDATE affirmation_stats 
    SET avg_rating = (
        SELECT AVG(rating) FROM user_affirmations WHERE rating IS NOT NULL
    );
END;

CREATE TRIGGER IF NOT EXISTS update_custom_count
AFTER INSERT ON custom_affirmations
BEGIN
    UPDATE affirmation_stats 
    SET custom_affirmations = (
        SELECT COUNT(*) FROM custom_affirmations WHERE is_active = TRUE
    );
END;

-- Insert default categories
INSERT OR IGNORE INTO categories (name, description, color, icon) VALUES
('self-love', 'Affirmations for self-acceptance and self-worth', 'pink', '💖'),
('healing', 'Affirmations for physical and emotional healing', 'green', '🌿'),
('confidence', 'Affirmations for building confidence and courage', 'blue', '💪'),
('abundance', 'Affirmations for prosperity and success', 'gold', '✨'),
('relationships', 'Affirmations for healthy relationships', 'purple', '💕'),
('peace', 'Affirmations for inner peace and calm', 'cyan', '🕊️'),
('health', 'Affirmations for physical and mental health', 'green', '🌱'),
('gratitude', 'Affirmations for thankfulness and appreciation', 'yellow', '🙏'),
('personal', 'Personal custom affirmations', 'orange', '🎯'),
('general', 'General positive affirmations', 'white', '⭐');

-- Initialize stats table
INSERT OR IGNORE INTO affirmation_stats (id) VALUES (1);

-- Insert sample reminders
INSERT OR IGNORE INTO affirmation_reminders (time, days_of_week, category) VALUES
('08:00', '1,2,3,4,5,6,7', 'general'),
('12:00', '1,2,3,4,5', 'confidence'),
('20:00', '1,2,3,4,5,6,7', 'gratitude');
