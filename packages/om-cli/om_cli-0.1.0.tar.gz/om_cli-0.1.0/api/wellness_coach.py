"""
AI Wellness Coach for om Mental Health Platform
Adapted from logbuch-flask AI coach for wellness-focused insights and recommendations
"""

import json
from datetime import datetime, timedelta
from sqlalchemy import func
from collections import Counter, defaultdict
import statistics

class WellnessCoach:
    """AI-powered wellness coach that analyzes patterns and provides insights"""
    
    def __init__(self, user):
        self.user = user
        
    def analyze_wellness_patterns(self, days=30):
        """Analyze user's wellness patterns over the last N days"""
        from models import MoodEntry, CheckinEntry, WellnessSession, WellnessGoal
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Mood patterns
        mood_entries = MoodEntry.query.filter(
            MoodEntry.user_id == self.user.id, 
            MoodEntry.date >= start_date
        ).all()
        
        # Check-in patterns
        checkin_entries = CheckinEntry.query.filter(
            CheckinEntry.user_id == self.user.id, 
            CheckinEntry.date >= start_date
        ).all()
        
        # Wellness session patterns
        wellness_sessions = WellnessSession.query.filter(
            WellnessSession.user_id == self.user.id, 
            WellnessSession.date >= start_date
        ).all()
        
        # Goal progress patterns
        goals = WellnessGoal.query.filter(
            WellnessGoal.user_id == self.user.id, 
            WellnessGoal.created_date >= start_date
        ).all()
        
        patterns = {
            'mood_stability': self._calculate_mood_stability(mood_entries),
            'mood_trends': self._analyze_mood_trends(mood_entries),
            'checkin_consistency': len(checkin_entries) / days,
            'wellness_activity_frequency': len(wellness_sessions) / days,
            'favorite_activities': self._get_favorite_activities(wellness_sessions),
            'stress_patterns': self._analyze_stress_patterns(checkin_entries),
            'sleep_patterns': self._analyze_sleep_patterns(checkin_entries),
            'goal_progress_rate': self._calculate_goal_progress_rate(goals),
            'trigger_analysis': self._analyze_mood_triggers(mood_entries),
            'energy_patterns': self._analyze_energy_patterns(checkin_entries),
        }
        
        return patterns
    
    def _calculate_mood_stability(self, mood_entries):
        """Calculate mood stability score (0-100)"""
        if len(mood_entries) < 2:
            return 50  # Neutral score for insufficient data
        
        # Map moods to numeric values for analysis
        mood_values = {
            'amazing': 10, 'happy': 9, 'grateful': 8, 'content': 7, 'calm': 7,
            'energetic': 8, 'focused': 7, 'creative': 8, 'okay': 5,
            'tired': 4, 'stressed': 3, 'overwhelmed': 2, 'sad': 2,
            'anxious': 3, 'frustrated': 3, 'lonely': 2
        }
        
        values = [mood_values.get(entry.mood, 5) for entry in mood_entries]
        
        if len(values) < 2:
            return 50
        
        # Calculate stability based on standard deviation
        std_dev = statistics.stdev(values)
        # Convert to 0-100 scale (lower std_dev = higher stability)
        stability = max(0, 100 - (std_dev * 20))
        
        return round(stability, 1)
    
    def _analyze_mood_trends(self, mood_entries):
        """Analyze mood trends over time"""
        if len(mood_entries) < 3:
            return {'trend': 'insufficient_data', 'direction': 'stable'}
        
        # Sort by date
        sorted_entries = sorted(mood_entries, key=lambda x: x.date)
        
        # Map moods to numeric values
        mood_values = {
            'amazing': 10, 'happy': 9, 'grateful': 8, 'content': 7, 'calm': 7,
            'energetic': 8, 'focused': 7, 'creative': 8, 'okay': 5,
            'tired': 4, 'stressed': 3, 'overwhelmed': 2, 'sad': 2,
            'anxious': 3, 'frustrated': 3, 'lonely': 2
        }
        
        values = [mood_values.get(entry.mood, 5) for entry in sorted_entries]
        
        # Simple trend analysis
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        difference = second_avg - first_avg
        
        if difference > 0.5:
            trend = 'improving'
        elif difference < -0.5:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'direction': 'up' if difference > 0 else 'down' if difference < 0 else 'stable',
            'change_magnitude': abs(difference),
            'recent_average': second_avg,
            'overall_average': sum(values) / len(values)
        }
    
    def _get_favorite_activities(self, wellness_sessions):
        """Get user's favorite wellness activities"""
        if not wellness_sessions:
            return []
        
        activity_counts = Counter(session.activity_type for session in wellness_sessions)
        activity_ratings = defaultdict(list)
        
        for session in wellness_sessions:
            if session.rating:
                activity_ratings[session.activity_type].append(session.rating)
        
        # Calculate weighted favorites (frequency + rating)
        favorites = []
        for activity, count in activity_counts.most_common():
            avg_rating = statistics.mean(activity_ratings[activity]) if activity_ratings[activity] else 3
            score = count * avg_rating
            favorites.append({
                'activity': activity,
                'count': count,
                'avg_rating': round(avg_rating, 1),
                'score': round(score, 1)
            })
        
        return sorted(favorites, key=lambda x: x['score'], reverse=True)[:5]
    
    def _analyze_stress_patterns(self, checkin_entries):
        """Analyze stress level patterns"""
        stress_levels = [entry.stress_level for entry in checkin_entries if entry.stress_level]
        
        if not stress_levels:
            return {'average': None, 'trend': 'no_data'}
        
        avg_stress = statistics.mean(stress_levels)
        
        # Analyze trend
        if len(stress_levels) >= 3:
            recent_stress = statistics.mean(stress_levels[-3:])
            trend = 'increasing' if recent_stress > avg_stress else 'decreasing' if recent_stress < avg_stress else 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'average': round(avg_stress, 1),
            'trend': trend,
            'high_stress_days': len([s for s in stress_levels if s >= 7]),
            'low_stress_days': len([s for s in stress_levels if s <= 3])
        }
    
    def _analyze_sleep_patterns(self, checkin_entries):
        """Analyze sleep patterns"""
        sleep_hours = [entry.sleep_hours for entry in checkin_entries if entry.sleep_hours]
        sleep_quality = [entry.sleep_quality for entry in checkin_entries if entry.sleep_quality]
        
        patterns = {}
        
        if sleep_hours:
            patterns['avg_hours'] = round(statistics.mean(sleep_hours), 1)
            patterns['sleep_consistency'] = 'good' if statistics.stdev(sleep_hours) < 1.5 else 'poor'
        
        if sleep_quality:
            quality_counts = Counter(sleep_quality)
            patterns['quality_distribution'] = dict(quality_counts)
            patterns['good_sleep_percentage'] = (quality_counts.get('excellent', 0) + quality_counts.get('good', 0)) / len(sleep_quality) * 100
        
        return patterns
    
    def _calculate_goal_progress_rate(self, goals):
        """Calculate overall goal progress rate"""
        if not goals:
            return 0
        
        total_progress = sum(goal.progress_percentage for goal in goals)
        return round(total_progress / len(goals), 1)
    
    def _analyze_mood_triggers(self, mood_entries):
        """Analyze what triggers different moods"""
        positive_triggers = Counter()
        negative_triggers = Counter()
        
        positive_moods = {'amazing', 'happy', 'grateful', 'content', 'calm', 'energetic', 'focused', 'creative'}
        
        for entry in mood_entries:
            triggers = entry.get_triggers_list()
            if triggers:
                if entry.mood in positive_moods:
                    positive_triggers.update(triggers)
                else:
                    negative_triggers.update(triggers)
        
        return {
            'positive_triggers': dict(positive_triggers.most_common(5)),
            'negative_triggers': dict(negative_triggers.most_common(5))
        }
    
    def _analyze_energy_patterns(self, checkin_entries):
        """Analyze energy level patterns"""
        energy_levels = [entry.energy_level for entry in checkin_entries if entry.energy_level]
        
        if not energy_levels:
            return {'average': None, 'pattern': 'no_data'}
        
        avg_energy = statistics.mean(energy_levels)
        
        # Analyze by time of day if we have timestamps
        morning_energy = []
        evening_energy = []
        
        for entry in checkin_entries:
            if entry.energy_level:
                hour = entry.date.hour
                if 5 <= hour <= 12:
                    morning_energy.append(entry.energy_level)
                elif 17 <= hour <= 23:
                    evening_energy.append(entry.energy_level)
        
        patterns = {
            'average': round(avg_energy, 1),
            'high_energy_days': len([e for e in energy_levels if e >= 7]),
            'low_energy_days': len([e for e in energy_levels if e <= 3])
        }
        
        if morning_energy and evening_energy:
            patterns['morning_avg'] = round(statistics.mean(morning_energy), 1)
            patterns['evening_avg'] = round(statistics.mean(evening_energy), 1)
            patterns['energy_type'] = 'morning_person' if patterns['morning_avg'] > patterns['evening_avg'] else 'evening_person'
        
        return patterns
    
    def generate_daily_insights(self):
        """Generate daily wellness insights and recommendations"""
        patterns = self.analyze_wellness_patterns(days=7)  # Last week
        
        insights = []
        recommendations = []
        
        # Mood insights
        mood_trend = patterns.get('mood_trends', {})
        if mood_trend.get('trend') == 'improving':
            insights.append("🌟 Your mood has been trending upward this week - great progress!")
        elif mood_trend.get('trend') == 'declining':
            insights.append("💙 Your mood has been lower lately. Remember, it's okay to have difficult periods.")
            recommendations.append("Consider trying a mindfulness exercise or reaching out to someone you trust.")
        
        # Stress insights
        stress_patterns = patterns.get('stress_patterns', {})
        if stress_patterns.get('average', 0) > 6:
            insights.append("⚠️ Your stress levels have been elevated recently.")
            recommendations.append("Try some breathing exercises or take short breaks throughout the day.")
        
        # Activity insights
        favorite_activities = patterns.get('favorite_activities', [])
        if favorite_activities:
            top_activity = favorite_activities[0]
            insights.append(f"🎯 Your most effective wellness activity is {top_activity['activity']} (rated {top_activity['avg_rating']}/5)")
            recommendations.append(f"Consider doing more {top_activity['activity']} - it seems to work well for you!")
        
        # Sleep insights
        sleep_patterns = patterns.get('sleep_patterns', {})
        if sleep_patterns.get('avg_hours', 8) < 7:
            insights.append("😴 You might benefit from more sleep - aim for 7-9 hours per night.")
            recommendations.append("Try establishing a consistent bedtime routine.")
        
        # Goal progress
        goal_progress = patterns.get('goal_progress_rate', 0)
        if goal_progress > 70:
            insights.append(f"🎯 Excellent goal progress at {goal_progress}%!")
        elif goal_progress < 30:
            recommendations.append("Consider breaking your goals into smaller, more manageable steps.")
        
        return {
            'insights': insights,
            'recommendations': recommendations,
            'wellness_score': self.user.get_wellness_score(),
            'patterns_summary': patterns
        }
    
    def suggest_activities(self, mood=None, available_time=None):
        """Suggest wellness activities based on current state"""
        suggestions = []
        
        # Base suggestions
        base_activities = [
            {'activity': 'breathing', 'duration': 5, 'reason': 'Quick stress relief'},
            {'activity': 'meditation', 'duration': 10, 'reason': 'Mental clarity'},
            {'activity': 'gratitude', 'duration': 3, 'reason': 'Positive mindset'},
            {'activity': 'stretching', 'duration': 5, 'reason': 'Physical wellness'},
            {'activity': 'journaling', 'duration': 10, 'reason': 'Self-reflection'}
        ]
        
        # Mood-specific suggestions
        if mood:
            if mood in ['stressed', 'overwhelmed', 'anxious']:
                suggestions.extend([
                    {'activity': 'breathing', 'duration': 5, 'reason': 'Immediate calm'},
                    {'activity': 'meditation', 'duration': 10, 'reason': 'Stress reduction'},
                    {'activity': 'nature', 'duration': 15, 'reason': 'Natural stress relief'}
                ])
            elif mood in ['sad', 'lonely']:
                suggestions.extend([
                    {'activity': 'gratitude', 'duration': 5, 'reason': 'Shift perspective'},
                    {'activity': 'social', 'duration': 20, 'reason': 'Connection'},
                    {'activity': 'creative', 'duration': 15, 'reason': 'Self-expression'}
                ])
            elif mood in ['tired', 'low_energy']:
                suggestions.extend([
                    {'activity': 'stretching', 'duration': 5, 'reason': 'Gentle energy boost'},
                    {'activity': 'music', 'duration': 10, 'reason': 'Mood lift'},
                    {'activity': 'nature', 'duration': 10, 'reason': 'Natural energy'}
                ])
        
        # Time-based filtering
        if available_time:
            suggestions = [s for s in suggestions if s['duration'] <= available_time]
        
        # Get user's favorite activities for personalization
        patterns = self.analyze_wellness_patterns(days=30)
        favorites = patterns.get('favorite_activities', [])
        
        if favorites:
            # Boost suggestions that match user preferences
            favorite_types = [fav['activity'] for fav in favorites[:3]]
            for suggestion in suggestions:
                if suggestion['activity'] in favorite_types:
                    suggestion['personalized'] = True
                    suggestion['reason'] += ' (you enjoy this!)'
        
        # Remove duplicates and sort by relevance
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            key = suggestion['activity']
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions[:5]  # Return top 5 suggestions
