"""
Enhanced Database Models for om Mental Health Platform API
Integrates SQLAlchemy models adapted from logbuch-flask for wellness tracking
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
import uuid
import json

# Create db instance that will be initialized later
db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and wellness data"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Wellness preferences
    timezone = db.Column(db.String(50), default='UTC')
    wellness_goals = db.Column(db.Text)  # JSON string of goals
    notification_preferences = db.Column(db.Text)  # JSON string
    
    # Relationships
    mood_entries = db.relationship('MoodEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    checkin_entries = db.relationship('CheckinEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    wellness_sessions = db.relationship('WellnessSession', backref='user', lazy=True, cascade='all, delete-orphan')
    goals = db.relationship('WellnessGoal', backref='user', lazy=True, cascade='all, delete-orphan')
    achievements = db.relationship('UserAchievement', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_wellness_score(self, days=7):
        """Calculate overall wellness score based on recent activity"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get recent mood entries
        recent_moods = MoodEntry.query.filter(
            MoodEntry.user_id == self.id,
            MoodEntry.date >= start_date
        ).all()
        
        # Get recent check-ins
        recent_checkins = CheckinEntry.query.filter(
            CheckinEntry.user_id == self.id,
            CheckinEntry.date >= start_date
        ).all()
        
        # Calculate score (simplified algorithm)
        mood_score = sum(entry.intensity or 5 for entry in recent_moods) / len(recent_moods) if recent_moods else 5
        checkin_score = len(recent_checkins) * 2  # Consistency bonus
        
        return min(100, (mood_score * 10) + checkin_score)


class MoodEntry(db.Model):
    """Enhanced mood tracking with intensity and triggers"""
    MOOD_CHOICES = [
        ('amazing', '🤩 Amazing'),
        ('happy', '😊 Happy'),
        ('grateful', '🙏 Grateful'),
        ('content', '😌 Content'),
        ('calm', '😌 Calm'),
        ('energetic', '⚡ Energetic'),
        ('focused', '🎯 Focused'),
        ('creative', '🎨 Creative'),
        ('okay', '😐 Okay'),
        ('tired', '😴 Tired'),
        ('stressed', '😰 Stressed'),
        ('overwhelmed', '🤯 Overwhelmed'),
        ('sad', '😢 Sad'),
        ('anxious', '😟 Anxious'),
        ('frustrated', '😤 Frustrated'),
        ('lonely', '😔 Lonely'),
    ]
    
    TRIGGER_CHOICES = [
        'work_success', 'work_stress', 'exercise', 'good_weather', 'bad_weather',
        'social_interaction', 'alone_time', 'family_time', 'achievement',
        'setback', 'health_issue', 'sleep_quality', 'nutrition', 'meditation',
        'creative_work', 'learning', 'helping_others', 'nature', 'music'
    ]
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    mood = db.Column(db.String(20), nullable=False)
    intensity = db.Column(db.Integer)  # 1-10 scale
    notes = db.Column(db.Text, default='')
    triggers = db.Column(db.Text)  # JSON array of triggers
    location = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<MoodEntry {self.date.strftime("%Y-%m-%d")} - {self.mood}>'
    
    def get_mood_display(self):
        """Get the display value for mood"""
        mood_dict = dict(self.MOOD_CHOICES)
        return mood_dict.get(self.mood, self.mood)
    
    def get_triggers_list(self):
        """Get triggers as a list"""
        if self.triggers:
            try:
                return json.loads(self.triggers)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_triggers_list(self, triggers_list):
        """Set triggers from a list"""
        self.triggers = json.dumps(triggers_list) if triggers_list else None


class CheckinEntry(db.Model):
    """Daily check-in entries for comprehensive wellness tracking"""
    CHECKIN_TYPES = [
        ('quick_checkin', 'Quick Check-in'),
        ('full_checkin', 'Full Check-in'),
        ('morning_checkin', 'Morning Check-in'),
        ('evening_checkin', 'Evening Check-in')
    ]
    
    SLEEP_QUALITY_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('terrible', 'Terrible')
    ]
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String(20), default='quick_checkin')
    
    # Mood and energy
    mood = db.Column(db.String(20))
    mood_intensity = db.Column(db.Integer)  # 1-10
    energy_level = db.Column(db.Integer)  # 1-10
    stress_level = db.Column(db.Integer)  # 1-10
    
    # Sleep tracking
    sleep_quality = db.Column(db.String(20))
    sleep_hours = db.Column(db.Float)
    
    # Reflection questions
    going_well = db.Column(db.Text)
    challenges = db.Column(db.Text)
    daily_goal = db.Column(db.Text)
    daily_priority = db.Column(db.Text)
    gratitude = db.Column(db.Text)
    self_care_plan = db.Column(db.Text)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<CheckinEntry {self.date.strftime("%Y-%m-%d")} - {self.type}>'


class WellnessSession(db.Model):
    """Track wellness activities like meditation, breathing exercises, etc."""
    ACTIVITY_TYPES = [
        ('breathing', 'Breathing Exercise'),
        ('meditation', 'Meditation'),
        ('mindfulness', 'Mindfulness'),
        ('gratitude', 'Gratitude Practice'),
        ('journaling', 'Journaling'),
        ('exercise', 'Physical Exercise'),
        ('stretching', 'Stretching'),
        ('reading', 'Reading'),
        ('music', 'Music/Audio'),
        ('nature', 'Nature Time'),
        ('social', 'Social Connection'),
        ('creative', 'Creative Activity'),
        ('learning', 'Learning/Growth')
    ]
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    activity_type = db.Column(db.String(20), nullable=False)
    duration_minutes = db.Column(db.Integer)
    notes = db.Column(db.Text)
    rating = db.Column(db.Integer)  # 1-5 how helpful it was
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<WellnessSession {self.activity_type} - {self.duration_minutes}min>'


class WellnessGoal(db.Model):
    """Wellness-focused goals with progress tracking"""
    GOAL_CATEGORIES = [
        ('mood', 'Mood & Emotional'),
        ('stress', 'Stress Management'),
        ('sleep', 'Sleep Quality'),
        ('exercise', 'Physical Activity'),
        ('mindfulness', 'Mindfulness & Meditation'),
        ('social', 'Social Connection'),
        ('habits', 'Healthy Habits'),
        ('growth', 'Personal Growth'),
        ('balance', 'Work-Life Balance')
    ]
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(20))
    target_value = db.Column(db.Integer)  # e.g., 30 days, 10 sessions
    current_value = db.Column(db.Integer, default=0)
    unit = db.Column(db.String(20))  # days, sessions, minutes, etc.
    
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    target_date = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False)
    completed_date = db.Column(db.DateTime)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<WellnessGoal {self.title}>'
    
    @property
    def progress_percentage(self):
        """Calculate progress as percentage"""
        if not self.target_value:
            return 0
        return min(100, (self.current_value / self.target_value) * 100)
    
    def update_progress(self, increment=1):
        """Update goal progress"""
        self.current_value += increment
        if self.current_value >= self.target_value and not self.completed:
            self.completed = True
            self.completed_date = datetime.utcnow()
        db.session.commit()


class Achievement(db.Model):
    """Available achievements for gamification"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(10))  # emoji
    category = db.Column(db.String(50))
    points = db.Column(db.Integer, default=10)
    
    # Achievement criteria (JSON)
    criteria = db.Column(db.Text)  # JSON string defining unlock conditions
    
    def __repr__(self):
        return f'<Achievement {self.name}>'


class UserAchievement(db.Model):
    """User's unlocked achievements"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_id = db.Column(db.String(36), db.ForeignKey('achievement.id'), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    achievement = db.relationship('Achievement', backref='user_achievements')
    
    def __repr__(self):
        return f'<UserAchievement {self.achievement.name}>'


class APIKey(db.Model):
    """API key management"""
    id = db.Column(db.Integer, primary_key=True)
    key_hash = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    permissions = db.Column(db.Text)  # JSON array of permissions
    rate_limit = db.Column(db.Integer, default=1000)  # requests per hour
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    def __repr__(self):
        return f'<APIKey {self.name}>'
    
    def get_permissions_list(self):
        """Get permissions as a list"""
        if self.permissions:
            try:
                return json.loads(self.permissions)
            except json.JSONDecodeError:
                return ['read']
        return ['read']
    
    def has_permission(self, permission):
        """Check if key has specific permission"""
        return permission in self.get_permissions_list()
