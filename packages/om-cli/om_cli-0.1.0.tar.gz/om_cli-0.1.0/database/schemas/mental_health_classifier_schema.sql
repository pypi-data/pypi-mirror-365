-- Mental Health Text Classification Database Schema
-- This schema supports the AI-powered mental health text classification system

-- Table to store individual text classifications
CREATE TABLE IF NOT EXISTS classifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    text TEXT NOT NULL,
    predicted_category TEXT NOT NULL,
    confidence REAL NOT NULL,
    all_scores TEXT NOT NULL, -- JSON string of all category scores
    user_feedback TEXT, -- User can provide feedback on accuracy
    notes TEXT, -- Additional user notes
    session_id TEXT, -- Optional session grouping
    source TEXT DEFAULT 'manual' -- Source of classification (manual, journal, mood, etc.)
);

-- Table to track statistics for each mental health category
CREATE TABLE IF NOT EXISTS category_stats (
    category TEXT PRIMARY KEY,
    count INTEGER DEFAULT 0,
    avg_confidence REAL DEFAULT 0.0,
    last_detected TEXT,
    first_detected TEXT,
    description TEXT
);

-- Table to store model performance metrics
CREATE TABLE IF NOT EXISTS model_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    model_name TEXT NOT NULL,
    accuracy REAL,
    total_classifications INTEGER DEFAULT 0,
    avg_confidence REAL DEFAULT 0.0,
    notes TEXT
);

-- Table to track user feedback and model improvement
CREATE TABLE IF NOT EXISTS feedback_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    classification_id INTEGER,
    timestamp TEXT NOT NULL,
    feedback_type TEXT NOT NULL, -- 'correct', 'incorrect', 'partially_correct'
    expected_category TEXT,
    confidence_rating INTEGER, -- 1-5 scale
    comments TEXT,
    FOREIGN KEY (classification_id) REFERENCES classifications(id)
);

-- Table to store classification patterns and trends
CREATE TABLE IF NOT EXISTS classification_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL, -- YYYY-MM-DD format
    category TEXT NOT NULL,
    count INTEGER DEFAULT 0,
    avg_confidence REAL DEFAULT 0.0,
    trend_direction TEXT, -- 'increasing', 'decreasing', 'stable'
    UNIQUE(date, category)
);

-- Table to store crisis detection alerts
CREATE TABLE IF NOT EXISTS crisis_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    classification_id INTEGER,
    timestamp TEXT NOT NULL,
    category TEXT NOT NULL,
    confidence REAL NOT NULL,
    alert_level TEXT NOT NULL, -- 'low', 'medium', 'high', 'critical'
    acknowledged BOOLEAN DEFAULT FALSE,
    response_taken TEXT,
    notes TEXT,
    FOREIGN KEY (classification_id) REFERENCES classifications(id)
);

-- Table to store integration with other om modules
CREATE TABLE IF NOT EXISTS module_integrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    classification_id INTEGER,
    module_name TEXT NOT NULL,
    integration_type TEXT NOT NULL, -- 'mood_correlation', 'journal_analysis', etc.
    data TEXT, -- JSON data for integration
    timestamp TEXT NOT NULL,
    FOREIGN KEY (classification_id) REFERENCES classifications(id)
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_classifications_timestamp ON classifications(timestamp);
CREATE INDEX IF NOT EXISTS idx_classifications_category ON classifications(predicted_category);
CREATE INDEX IF NOT EXISTS idx_classifications_confidence ON classifications(confidence);
CREATE INDEX IF NOT EXISTS idx_classifications_source ON classifications(source);
CREATE INDEX IF NOT EXISTS idx_patterns_date ON classification_patterns(date);
CREATE INDEX IF NOT EXISTS idx_patterns_category ON classification_patterns(category);
CREATE INDEX IF NOT EXISTS idx_crisis_alerts_timestamp ON crisis_alerts(timestamp);
CREATE INDEX IF NOT EXISTS idx_crisis_alerts_level ON crisis_alerts(alert_level);

-- Initialize category statistics with all supported categories
INSERT OR IGNORE INTO category_stats (category, count, avg_confidence, description) VALUES
('EDAnonymous', 0, 0.0, 'Eating disorders and body image issues'),
('addiction', 0, 0.0, 'Substance or behavioral dependencies'),
('alcoholism', 0, 0.0, 'Alcohol-related problems and dependencies'),
('adhd', 0, 0.0, 'Attention deficit hyperactivity disorder'),
('anxiety', 0, 0.0, 'General anxiety and worry'),
('autism', 0, 0.0, 'Autism spectrum conditions'),
('bipolarreddit', 0, 0.0, 'Bipolar disorder and mood swings'),
('bpd', 0, 0.0, 'Borderline personality disorder'),
('depression', 0, 0.0, 'Depression and persistent sadness'),
('healthanxiety', 0, 0.0, 'Health-related anxiety and hypochondria'),
('lonely', 0, 0.0, 'Loneliness and social isolation'),
('ptsd', 0, 0.0, 'Post-traumatic stress disorder'),
('schizophrenia', 0, 0.0, 'Schizophrenia and psychotic symptoms'),
('socialanxiety', 0, 0.0, 'Social anxiety and social fears'),
('suicidewatch', 0, 0.0, 'Suicidal thoughts and crisis situations');

-- Initialize model metrics
INSERT OR IGNORE INTO model_metrics (timestamp, model_name, accuracy, notes) VALUES
(datetime('now'), 'tahaenesaslanturk/mental-health-classification-v0.1', 0.64, 'Initial model setup - 64% accuracy as reported by model author');

-- Views for common queries
CREATE VIEW IF NOT EXISTS recent_classifications AS
SELECT 
    id,
    timestamp,
    SUBSTR(text, 1, 100) || CASE WHEN LENGTH(text) > 100 THEN '...' ELSE '' END as text_preview,
    predicted_category,
    confidence,
    user_feedback,
    source
FROM classifications
ORDER BY timestamp DESC
LIMIT 50;

CREATE VIEW IF NOT EXISTS category_summary AS
SELECT 
    cs.category,
    cs.count,
    cs.avg_confidence,
    cs.last_detected,
    cs.description,
    COUNT(c.id) as recent_count
FROM category_stats cs
LEFT JOIN classifications c ON cs.category = c.predicted_category 
    AND c.timestamp > datetime('now', '-7 days')
GROUP BY cs.category
ORDER BY cs.count DESC;

CREATE VIEW IF NOT EXISTS high_risk_classifications AS
SELECT 
    c.*,
    CASE 
        WHEN c.predicted_category = 'suicidewatch' AND c.confidence > 0.6 THEN 'CRITICAL'
        WHEN c.predicted_category IN ('depression', 'ptsd') AND c.confidence > 0.7 THEN 'HIGH'
        WHEN c.predicted_category IN ('anxiety', 'socialanxiety') AND c.confidence > 0.8 THEN 'MEDIUM'
        ELSE 'LOW'
    END as risk_level
FROM classifications c
WHERE c.predicted_category IN ('suicidewatch', 'depression', 'ptsd', 'anxiety', 'socialanxiety')
    AND c.confidence > 0.5
ORDER BY 
    CASE 
        WHEN c.predicted_category = 'suicidewatch' THEN 1
        WHEN c.predicted_category = 'depression' THEN 2
        WHEN c.predicted_category = 'ptsd' THEN 3
        ELSE 4
    END,
    c.confidence DESC,
    c.timestamp DESC;

-- Triggers for automatic updates
CREATE TRIGGER IF NOT EXISTS update_category_stats_on_insert
AFTER INSERT ON classifications
BEGIN
    UPDATE category_stats 
    SET count = count + 1,
        avg_confidence = (avg_confidence * (count - 1) + NEW.confidence) / count,
        last_detected = NEW.timestamp,
        first_detected = COALESCE(first_detected, NEW.timestamp)
    WHERE category = NEW.predicted_category;
    
    -- Update daily patterns
    INSERT OR REPLACE INTO classification_patterns (date, category, count, avg_confidence)
    VALUES (
        DATE(NEW.timestamp),
        NEW.predicted_category,
        COALESCE((SELECT count FROM classification_patterns 
                 WHERE date = DATE(NEW.timestamp) AND category = NEW.predicted_category), 0) + 1,
        (COALESCE((SELECT avg_confidence * count FROM classification_patterns 
                  WHERE date = DATE(NEW.timestamp) AND category = NEW.predicted_category), 0) + NEW.confidence) /
        (COALESCE((SELECT count FROM classification_patterns 
                  WHERE date = DATE(NEW.timestamp) AND category = NEW.predicted_category), 0) + 1)
    );
    
    -- Create crisis alert if needed
    INSERT INTO crisis_alerts (classification_id, timestamp, category, confidence, alert_level)
    SELECT 
        NEW.id,
        NEW.timestamp,
        NEW.predicted_category,
        NEW.confidence,
        CASE 
            WHEN NEW.predicted_category = 'suicidewatch' AND NEW.confidence > 0.6 THEN 'critical'
            WHEN NEW.predicted_category IN ('depression', 'ptsd') AND NEW.confidence > 0.7 THEN 'high'
            WHEN NEW.predicted_category IN ('anxiety', 'socialanxiety') AND NEW.confidence > 0.8 THEN 'medium'
            ELSE 'low'
        END
    WHERE NEW.predicted_category IN ('suicidewatch', 'depression', 'ptsd', 'anxiety', 'socialanxiety')
        AND NEW.confidence > 0.5;
END;

-- Update model metrics trigger
CREATE TRIGGER IF NOT EXISTS update_model_metrics
AFTER INSERT ON classifications
BEGIN
    UPDATE model_metrics 
    SET total_classifications = total_classifications + 1,
        avg_confidence = (avg_confidence * (total_classifications - 1) + NEW.confidence) / total_classifications
    WHERE model_name = 'tahaenesaslanturk/mental-health-classification-v0.1';
END;
