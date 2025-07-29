#!/usr/bin/env python3
"""
Mental Health AI Coach for om
Adapted from logbuch AI coach for mental health and wellness insights
"""

import datetime
import json
import statistics
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import random

class CoachingType(Enum):
    MOOD_OPTIMIZATION = "mood_optimization"
    STRESS_MANAGEMENT = "stress_management"
    ANXIETY_SUPPORT = "anxiety_support"
    DEPRESSION_SUPPORT = "depression_support"
    SLEEP_IMPROVEMENT = "sleep_improvement"
    MINDFULNESS_PRACTICE = "mindfulness_practice"
    EMOTIONAL_REGULATION = "emotional_regulation"
    SELF_CARE_HABITS = "self_care_habits"
    CRISIS_PREVENTION = "crisis_prevention"

@dataclass
class MentalHealthInsight:
    id: str
    type: CoachingType
    title: str
    insight: str
    action_items: List[str]
    confidence: float
    urgency: str  # low, medium, high, critical
    data_points: List[str]
    created_at: datetime.datetime
    implemented: bool = False
    effectiveness_rating: Optional[int] = None
    follow_up_date: Optional[datetime.datetime] = None

@dataclass
class WellnessPattern:
    pattern_type: str
    description: str
    frequency: float
    impact: str
    recommendation: str
    triggers: List[str]
    coping_strategies: List[str]

@dataclass
class MoodTrend:
    period: str  # daily, weekly, monthly
    average_mood: float
    trend_direction: str  # improving, declining, stable
    volatility: float
    concerning_patterns: List[str]
    positive_patterns: List[str]

class MentalHealthCoach:
    def __init__(self):
        self.data_dir = os.path.expanduser("~/.om")
        os.makedirs(self.data_dir, exist_ok=True)
        self.insights_file = os.path.join(self.data_dir, "coach_insights.json")
        self.patterns_file = os.path.join(self.data_dir, "wellness_patterns.json")
        self.insights = self._load_insights()
        self.patterns = self._load_patterns()
    
    def _load_insights(self) -> List[MentalHealthInsight]:
        """Load existing insights from storage"""
        if os.path.exists(self.insights_file):
            try:
                with open(self.insights_file, 'r') as f:
                    data = json.load(f)
                    return [self._dict_to_insight(item) for item in data]
            except Exception:
                return []
        return []
    
    def _load_patterns(self) -> List[WellnessPattern]:
        """Load wellness patterns from storage"""
        if os.path.exists(self.patterns_file):
            try:
                with open(self.patterns_file, 'r') as f:
                    data = json.load(f)
                    return [WellnessPattern(**item) for item in data]
            except Exception:
                return []
        return []
    
    def _save_insights(self):
        """Save insights to storage"""
        try:
            data = [self._insight_to_dict(insight) for insight in self.insights]
            with open(self.insights_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving insights: {e}")
    
    def _save_patterns(self):
        """Save patterns to storage"""
        try:
            data = [asdict(pattern) for pattern in self.patterns]
            with open(self.patterns_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving patterns: {e}")
    
    def _dict_to_insight(self, data: dict) -> MentalHealthInsight:
        """Convert dictionary to MentalHealthInsight"""
        data['type'] = CoachingType(data['type'])
        data['created_at'] = datetime.datetime.fromisoformat(data['created_at'])
        if data.get('follow_up_date'):
            data['follow_up_date'] = datetime.datetime.fromisoformat(data['follow_up_date'])
        return MentalHealthInsight(**data)
    
    def _insight_to_dict(self, insight: MentalHealthInsight) -> dict:
        """Convert MentalHealthInsight to dictionary"""
        data = asdict(insight)
        data['type'] = insight.type.value
        data['created_at'] = insight.created_at.isoformat()
        if insight.follow_up_date:
            data['follow_up_date'] = insight.follow_up_date.isoformat()
        return data
    
    def analyze_mood_data(self, mood_entries: List[dict]) -> List[MentalHealthInsight]:
        """Analyze mood data and generate insights"""
        if not mood_entries:
            return []
        
        insights = []
        
        # Analyze mood trends
        recent_moods = [entry.get('mood', 5) for entry in mood_entries[-14:]]  # Last 2 weeks
        if len(recent_moods) >= 3:
            trend = self._analyze_mood_trend(recent_moods)
            if trend:
                insights.append(trend)
        
        # Analyze stress patterns
        stress_insight = self._analyze_stress_patterns(mood_entries)
        if stress_insight:
            insights.append(stress_insight)
        
        # Check for concerning patterns
        concerning_insight = self._check_concerning_patterns(mood_entries)
        if concerning_insight:
            insights.append(concerning_insight)
        
        # Positive reinforcement
        positive_insight = self._generate_positive_reinforcement(mood_entries)
        if positive_insight:
            insights.append(positive_insight)
        
        # Save new insights
        self.insights.extend(insights)
        self._save_insights()
        
        return insights
    
    def _analyze_mood_trend(self, moods: List[float]) -> Optional[MentalHealthInsight]:
        """Analyze mood trend and provide insights"""
        if len(moods) < 3:
            return None
        
        avg_mood = statistics.mean(moods)
        recent_avg = statistics.mean(moods[-7:]) if len(moods) >= 7 else avg_mood
        earlier_avg = statistics.mean(moods[:-7]) if len(moods) >= 14 else avg_mood
        
        trend_direction = "stable"
        if recent_avg > earlier_avg + 0.5:
            trend_direction = "improving"
        elif recent_avg < earlier_avg - 0.5:
            trend_direction = "declining"
        
        if trend_direction == "declining" and avg_mood < 4:
            return MentalHealthInsight(
                id=f"mood_trend_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type=CoachingType.MOOD_OPTIMIZATION,
                title="Declining Mood Pattern Detected",
                insight=f"Your mood has been trending downward over the past week (average: {recent_avg:.1f}/10). This might indicate increased stress or other challenges.",
                action_items=[
                    "Consider scheduling a check-in with a mental health professional",
                    "Try the 'om rescue' command for immediate support techniques",
                    "Practice daily mindfulness with 'om meditate'",
                    "Ensure you're getting adequate sleep and nutrition"
                ],
                confidence=0.8,
                urgency="high" if avg_mood < 3 else "medium",
                data_points=[f"Recent mood average: {recent_avg:.1f}", f"Trend: {trend_direction}"],
                created_at=datetime.datetime.now(),
                follow_up_date=datetime.datetime.now() + datetime.timedelta(days=3)
            )
        
        elif trend_direction == "improving":
            return MentalHealthInsight(
                id=f"mood_improvement_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type=CoachingType.MOOD_OPTIMIZATION,
                title="Positive Mood Trend",
                insight=f"Great news! Your mood has been improving over the past week (average: {recent_avg:.1f}/10). Keep up the good work!",
                action_items=[
                    "Reflect on what's been working well for you",
                    "Consider documenting your successful strategies",
                    "Continue your current self-care practices",
                    "Share your progress with someone you trust"
                ],
                confidence=0.9,
                urgency="low",
                data_points=[f"Recent mood average: {recent_avg:.1f}", f"Trend: {trend_direction}"],
                created_at=datetime.datetime.now()
            )
        
        return None
    
    def _analyze_stress_patterns(self, mood_entries: List[dict]) -> Optional[MentalHealthInsight]:
        """Analyze stress patterns in mood data"""
        stress_entries = [entry for entry in mood_entries if entry.get('stress', 0) > 6]
        
        if len(stress_entries) >= 3:
            # Look for time patterns
            stress_times = [datetime.datetime.fromisoformat(entry['timestamp']).hour 
                          for entry in stress_entries if 'timestamp' in entry]
            
            if stress_times:
                common_hour = max(set(stress_times), key=stress_times.count)
                
                return MentalHealthInsight(
                    id=f"stress_pattern_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    type=CoachingType.STRESS_MANAGEMENT,
                    title="Recurring Stress Pattern Identified",
                    insight=f"You tend to experience higher stress levels around {common_hour}:00. Identifying this pattern can help you prepare and cope better.",
                    action_items=[
                        f"Set a reminder for {common_hour-1}:00 to practice preventive stress management",
                        "Try 'om quick breathe' before your typical stress time",
                        "Consider what triggers stress at this time and how to address them",
                        "Practice the 5-4-3-2-1 grounding technique with 'om quick grounding'"
                    ],
                    confidence=0.7,
                    urgency="medium",
                    data_points=[f"High stress episodes: {len(stress_entries)}", f"Common time: {common_hour}:00"],
                    created_at=datetime.datetime.now()
                )
        
        return None
    
    def _check_concerning_patterns(self, mood_entries: List[dict]) -> Optional[MentalHealthInsight]:
        """Check for concerning mental health patterns"""
        recent_entries = mood_entries[-7:]  # Last week
        
        if not recent_entries:
            return None
        
        low_mood_count = sum(1 for entry in recent_entries if entry.get('mood', 5) <= 3)
        high_stress_count = sum(1 for entry in recent_entries if entry.get('stress', 0) >= 8)
        
        if low_mood_count >= 4 or high_stress_count >= 3:
            return MentalHealthInsight(
                id=f"concerning_pattern_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type=CoachingType.CRISIS_PREVENTION,
                title="Concerning Pattern Detected",
                insight="Your recent mood and stress levels indicate you may be going through a difficult time. It's important to reach out for support.",
                action_items=[
                    "Consider contacting a mental health professional",
                    "Reach out to a trusted friend or family member",
                    "Use 'om rescue' for immediate crisis support resources",
                    "Practice daily self-care activities",
                    "If you're having thoughts of self-harm, please seek immediate help"
                ],
                confidence=0.9,
                urgency="critical",
                data_points=[f"Low mood days: {low_mood_count}/7", f"High stress days: {high_stress_count}/7"],
                created_at=datetime.datetime.now(),
                follow_up_date=datetime.datetime.now() + datetime.timedelta(days=1)
            )
        
        return None
    
    def _generate_positive_reinforcement(self, mood_entries: List[dict]) -> Optional[MentalHealthInsight]:
        """Generate positive reinforcement based on good patterns"""
        if not mood_entries:
            return None
        
        recent_entries = mood_entries[-7:]
        good_mood_count = sum(1 for entry in recent_entries if entry.get('mood', 5) >= 7)
        
        if good_mood_count >= 4:
            return MentalHealthInsight(
                id=f"positive_pattern_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type=CoachingType.MOOD_OPTIMIZATION,
                title="Positive Mental Health Pattern",
                insight=f"You've had {good_mood_count} good mood days this week! This shows your mental health strategies are working.",
                action_items=[
                    "Take a moment to acknowledge your progress",
                    "Reflect on what's been helping you feel good",
                    "Consider sharing your success with someone supportive",
                    "Keep up your current self-care routine"
                ],
                confidence=0.8,
                urgency="low",
                data_points=[f"Good mood days: {good_mood_count}/7"],
                created_at=datetime.datetime.now()
            )
        
        return None
    
    def get_daily_coaching(self) -> Optional[MentalHealthInsight]:
        """Get daily coaching insight"""
        # Check for pending follow-ups
        today = datetime.datetime.now().date()
        
        for insight in self.insights:
            if (insight.follow_up_date and 
                insight.follow_up_date.date() <= today and 
                not insight.implemented):
                return insight
        
        # Generate daily wisdom
        daily_tips = [
            {
                "title": "Mindfulness Moment",
                "insight": "Take three deep breaths and notice how you're feeling right now. Awareness is the first step to wellness.",
                "actions": ["Try 'om quick breathe' for a 2-minute breathing exercise", "Practice mindful awareness throughout the day"]
            },
            {
                "title": "Gratitude Practice",
                "insight": "Focusing on what you're grateful for can shift your perspective and improve your mood.",
                "actions": ["Use 'om quick gratitude' to practice appreciation", "Write down three things you're grateful for"]
            },
            {
                "title": "Self-Compassion Reminder",
                "insight": "Be kind to yourself today. You're doing the best you can with what you have right now.",
                "actions": ["Practice self-compassionate self-talk", "Treat yourself with the same kindness you'd show a good friend"]
            },
            {
                "title": "Movement and Mood",
                "insight": "Physical movement can significantly impact your mental state. Even small movements help.",
                "actions": ["Try 'om quick stretch' for physical tension release", "Take a short walk if possible"]
            }
        ]
        
        tip = random.choice(daily_tips)
        
        return MentalHealthInsight(
            id=f"daily_tip_{datetime.datetime.now().strftime('%Y%m%d')}",
            type=CoachingType.MINDFULNESS_PRACTICE,
            title=tip["title"],
            insight=tip["insight"],
            action_items=tip["actions"],
            confidence=0.6,
            urgency="low",
            data_points=["Daily coaching tip"],
            created_at=datetime.datetime.now()
        )
    
    def get_urgent_insights(self) -> List[MentalHealthInsight]:
        """Get insights that require immediate attention"""
        return [insight for insight in self.insights 
                if insight.urgency in ["high", "critical"] and not insight.implemented]
    
    def mark_insight_implemented(self, insight_id: str, effectiveness_rating: int):
        """Mark an insight as implemented with effectiveness rating"""
        for insight in self.insights:
            if insight.id == insight_id:
                insight.implemented = True
                insight.effectiveness_rating = effectiveness_rating
                break
        self._save_insights()
    
    def get_coaching_summary(self) -> dict:
        """Get summary of coaching insights"""
        total_insights = len(self.insights)
        implemented = sum(1 for i in self.insights if i.implemented)
        urgent = len(self.get_urgent_insights())
        
        effectiveness_ratings = [i.effectiveness_rating for i in self.insights 
                               if i.effectiveness_rating is not None]
        avg_effectiveness = statistics.mean(effectiveness_ratings) if effectiveness_ratings else 0
        
        return {
            "total_insights": total_insights,
            "implemented": implemented,
            "urgent": urgent,
            "average_effectiveness": avg_effectiveness,
            "implementation_rate": implemented / total_insights if total_insights > 0 else 0
        }

def run(args=None):
    """Main function to run the mental health coach"""
    coach = MentalHealthCoach()
    
    if not args or args[0] == "daily":
        # Show daily coaching
        insight = coach.get_daily_coaching()
        if insight:
            print(f"\n🧠 {insight.title}")
            print("=" * 50)
            print(f"💡 {insight.insight}")
            print("\n📋 Suggested Actions:")
            for i, action in enumerate(insight.action_items, 1):
                print(f"  {i}. {action}")
            print()
    
    elif args[0] == "urgent":
        # Show urgent insights
        urgent_insights = coach.get_urgent_insights()
        if urgent_insights:
            print("\n🚨 Urgent Mental Health Insights")
            print("=" * 50)
            for insight in urgent_insights:
                print(f"\n⚠️  {insight.title} ({insight.urgency.upper()})")
                print(f"💡 {insight.insight}")
                print("📋 Actions:")
                for action in insight.action_items:
                    print(f"  • {action}")
        else:
            print("\n✅ No urgent insights at this time.")
    
    elif args[0] == "summary":
        # Show coaching summary
        summary = coach.get_coaching_summary()
        print("\n📊 Mental Health Coaching Summary")
        print("=" * 50)
        print(f"Total insights generated: {summary['total_insights']}")
        print(f"Insights implemented: {summary['implemented']}")
        print(f"Implementation rate: {summary['implementation_rate']:.1%}")
        print(f"Urgent insights pending: {summary['urgent']}")
        if summary['average_effectiveness'] > 0:
            print(f"Average effectiveness rating: {summary['average_effectiveness']:.1f}/10")
    
    elif args[0] == "analyze":
        # Analyze mood data if available
        mood_file = os.path.expanduser("~/.om/mood_data.json")
        if os.path.exists(mood_file):
            try:
                with open(mood_file, 'r') as f:
                    mood_data = json.load(f)
                
                insights = coach.analyze_mood_data(mood_data)
                if insights:
                    print(f"\n🔍 Generated {len(insights)} new insights from your mood data:")
                    for insight in insights:
                        print(f"\n• {insight.title}")
                        print(f"  {insight.insight}")
                else:
                    print("\n📊 Your mood data looks good - no new insights generated.")
            except Exception as e:
                print(f"Error analyzing mood data: {e}")
        else:
            print("\n📝 No mood data found. Start tracking your mood with 'om mood' to get personalized insights!")
    
    else:
        print("\n🧠 Mental Health AI Coach")
        print("=" * 30)
        print("Available commands:")
        print("  om coach daily    - Get daily coaching insight")
        print("  om coach urgent   - Show urgent insights")
        print("  om coach analyze  - Analyze your mood data")
        print("  om coach summary  - Show coaching summary")

if __name__ == "__main__":
    run()
