-- Mental Health Articles Database Schema for om.db
-- Stores curated mental health articles, resources, and content

-- Articles table for storing mental health articles
CREATE TABLE IF NOT EXISTS mental_health_articles (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    author TEXT,
    description TEXT,
    category TEXT NOT NULL, -- 'article', 'book', 'podcast', 'talk', 'app', 'organization'
    subcategory TEXT, -- 'burnout', 'anxiety', 'depression', 'imposter_syndrome', etc.
    source TEXT, -- 'awesome-mental-health', 'user_added', 'curated'
    tags TEXT, -- JSON array of tags
    reading_time_minutes INTEGER,
    difficulty_level TEXT, -- 'beginner', 'intermediate', 'advanced'
    target_audience TEXT, -- 'developers', 'managers', 'general', 'students'
    content_summary TEXT,
    key_takeaways TEXT, -- JSON array of key points
    is_favorite BOOLEAN DEFAULT 0,
    is_read BOOLEAN DEFAULT 0,
    user_rating INTEGER, -- 1-10 scale
    user_notes TEXT,
    date_added TEXT DEFAULT CURRENT_TIMESTAMP,
    date_read TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Article categories lookup table
CREATE TABLE IF NOT EXISTS article_categories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    icon TEXT,
    color TEXT,
    sort_order INTEGER DEFAULT 0
);

-- Article tags for flexible categorization
CREATE TABLE IF NOT EXISTS article_tags (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    usage_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- User reading progress and bookmarks
CREATE TABLE IF NOT EXISTS reading_progress (
    id TEXT PRIMARY KEY,
    article_id TEXT NOT NULL,
    progress_percentage INTEGER DEFAULT 0,
    current_section TEXT,
    bookmarks TEXT, -- JSON array of bookmarked sections
    reading_time_spent INTEGER DEFAULT 0, -- minutes
    last_read_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES mental_health_articles (id)
);

-- User article recommendations and suggestions
CREATE TABLE IF NOT EXISTS article_recommendations (
    id TEXT PRIMARY KEY,
    article_id TEXT NOT NULL,
    recommended_by TEXT, -- 'ai', 'user', 'system'
    reason TEXT,
    relevance_score REAL DEFAULT 0.0,
    based_on_mood TEXT,
    based_on_activity TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES mental_health_articles (id)
);

-- Article collections/playlists
CREATE TABLE IF NOT EXISTS article_collections (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    is_system_collection BOOLEAN DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Many-to-many relationship between articles and collections
CREATE TABLE IF NOT EXISTS collection_articles (
    id TEXT PRIMARY KEY,
    collection_id TEXT NOT NULL,
    article_id TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0,
    added_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (collection_id) REFERENCES article_collections (id),
    FOREIGN KEY (article_id) REFERENCES mental_health_articles (id),
    UNIQUE(collection_id, article_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_articles_category ON mental_health_articles(category);
CREATE INDEX IF NOT EXISTS idx_articles_subcategory ON mental_health_articles(subcategory);
CREATE INDEX IF NOT EXISTS idx_articles_is_favorite ON mental_health_articles(is_favorite);
CREATE INDEX IF NOT EXISTS idx_articles_is_read ON mental_health_articles(is_read);
CREATE INDEX IF NOT EXISTS idx_articles_date_added ON mental_health_articles(date_added);
CREATE INDEX IF NOT EXISTS idx_articles_user_rating ON mental_health_articles(user_rating);
CREATE INDEX IF NOT EXISTS idx_reading_progress_article ON reading_progress(article_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_article ON article_recommendations(article_id);
CREATE INDEX IF NOT EXISTS idx_collection_articles_collection ON collection_articles(collection_id);
CREATE INDEX IF NOT EXISTS idx_collection_articles_article ON collection_articles(article_id);

-- Insert default categories
INSERT OR IGNORE INTO article_categories (id, name, description, icon, sort_order) VALUES
('articles', 'Articles', 'Blog posts, essays, and written content about mental health in tech', '📝', 1),
('books', 'Books', 'Books and longer-form content on mental health and wellness', '📚', 2),
('podcasts', 'Podcasts', 'Audio content and podcast episodes', '🎧', 3),
('talks', 'Talks', 'Conference talks and presentations', '🎤', 4),
('apps', 'Applications', 'Mental health apps and digital tools', '📱', 5),
('organizations', 'Organizations', 'Mental health organizations and communities', '🏢', 6);

-- Insert common tags
INSERT OR IGNORE INTO article_tags (id, name, description) VALUES
('burnout', 'Burnout', 'Content about preventing and recovering from burnout'),
('anxiety', 'Anxiety', 'Resources for managing anxiety and stress'),
('depression', 'Depression', 'Support and information about depression'),
('imposter-syndrome', 'Imposter Syndrome', 'Dealing with imposter syndrome and self-doubt'),
('remote-work', 'Remote Work', 'Mental health challenges of remote work'),
('work-life-balance', 'Work-Life Balance', 'Maintaining healthy boundaries'),
('stress-management', 'Stress Management', 'Techniques for managing stress'),
('self-care', 'Self-Care', 'Self-care practices and strategies'),
('mindfulness', 'Mindfulness', 'Mindfulness and meditation practices'),
('productivity', 'Productivity', 'Healthy productivity and time management'),
('team-culture', 'Team Culture', 'Building mentally healthy team environments'),
('leadership', 'Leadership', 'Mental health considerations for leaders'),
('crisis-support', 'Crisis Support', 'Resources for mental health crises'),
('therapy', 'Therapy', 'Information about therapy and professional help'),
('medication', 'Medication', 'Information about mental health medication'),
('workplace', 'Workplace', 'Mental health in the workplace'),
('diversity', 'Diversity', 'Mental health and diversity/inclusion'),
('stigma', 'Stigma', 'Reducing mental health stigma'),
('recovery', 'Recovery', 'Recovery stories and strategies'),
('prevention', 'Prevention', 'Preventing mental health issues');

-- Create default collections
INSERT OR IGNORE INTO article_collections (id, name, description, is_system_collection) VALUES
('getting-started', 'Getting Started', 'Essential articles for understanding mental health in tech', 1),
('burnout-recovery', 'Burnout Recovery', 'Resources for preventing and recovering from burnout', 1),
('anxiety-management', 'Anxiety Management', 'Tools and techniques for managing anxiety', 1),
('imposter-syndrome', 'Overcoming Imposter Syndrome', 'Resources for dealing with imposter syndrome', 1),
('remote-work-wellness', 'Remote Work Wellness', 'Mental health tips for remote workers', 1),
('leadership-mental-health', 'Mental Health Leadership', 'Resources for leaders and managers', 1),
('crisis-resources', 'Crisis Resources', 'Emergency and crisis support resources', 1),
('personal-stories', 'Personal Stories', 'First-hand accounts and experiences', 1),
('research-studies', 'Research & Studies', 'Academic research and studies', 1),
('daily-wellness', 'Daily Wellness', 'Resources for daily mental health practices', 1);
