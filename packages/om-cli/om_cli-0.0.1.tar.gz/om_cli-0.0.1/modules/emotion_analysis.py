"""
Emotion Analysis module for om - inspired by Colors app
Advanced pattern recognition and trigger analysis for emotional wellbeing
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
import statistics

ANALYSIS_FILE = os.path.expanduser("~/.om_analysis.json")

class EmotionAnalysis:
    def __init__(self):
        self.emotion_categories = {
            "positive": ["joy", "love", "gratitude", "peace", "excitement", "contentment", "hope", "pride", "trust"],
            "negative": ["sadness", "anger", "fear", "anxiety", "loneliness", "disgust"],
            "neutral": ["surprise", "anticipation", "confusion"],
            "complex": ["mixed", "overwhelmed", "conflicted", "nostalgic", "bittersweet"]
        }
        
        self.trigger_categories = {
            "work": ["deadline", "meeting", "project", "boss", "colleague", "workload", "promotion", "feedback"],
            "relationships": ["family", "friend", "partner", "conflict", "support", "loneliness", "social"],
            "health": ["sleep", "exercise", "illness", "energy", "pain", "medication", "therapy"],
            "environment": ["weather", "location", "noise", "crowded", "home", "travel", "nature"],
            "activities": ["hobby", "music", "reading", "movie", "game", "sport", "creative"],
            "thoughts": ["memory", "future", "worry", "reflection", "decision", "goal", "fear"],
            "physical": ["tired", "hungry", "stressed", "relaxed", "energetic", "sick"]
        }
        
        self.pattern_types = {
            "daily": "Daily emotional patterns",
            "weekly": "Weekly emotional cycles", 
            "monthly": "Monthly emotional trends",
            "seasonal": "Seasonal emotional changes",
            "trigger_based": "Trigger-emotion relationships",
            "recovery": "Emotional recovery patterns",
            "intensity": "Emotional intensity patterns"
        }
    
    def show_analysis_menu(self):
        """Display emotion analysis main menu"""
        print("📊 Emotion Analysis & Pattern Recognition")
        print("=" * 50)
        print("Discover patterns in your emotional journey and understand your triggers")
        print("Inspired by Colors app's advanced pattern analysis")
        print()
        
        # Show quick stats
        self._show_quick_stats()
        
        print("🔍 Analysis Options:")
        print("1. Comprehensive emotion report")
        print("2. Trigger analysis and insights")
        print("3. Pattern recognition dashboard")
        print("4. Emotional recovery analysis")
        print("5. Mood prediction insights")
        print("6. Comparative analysis (time periods)")
        print("7. Export analysis data")
        print("8. Set analysis preferences")
        print()
        
        choice = input("Choose an option (1-8) or press Enter to return: ").strip()
        
        if choice == "1":
            self._comprehensive_emotion_report()
        elif choice == "2":
            self._trigger_analysis()
        elif choice == "3":
            self._pattern_recognition_dashboard()
        elif choice == "4":
            self._emotional_recovery_analysis()
        elif choice == "5":
            self._mood_prediction_insights()
        elif choice == "6":
            self._comparative_analysis()
        elif choice == "7":
            self._export_analysis_data()
        elif choice == "8":
            self._set_analysis_preferences()
    
    def _show_quick_stats(self):
        """Show quick emotional statistics"""
        mood_data = self._load_mood_data()
        if not mood_data:
            print("📈 No mood data available for analysis yet.")
            print("Start tracking your emotions to unlock powerful insights!")
            print()
            return
        
        # Calculate basic stats
        total_entries = len(mood_data)
        recent_entries = [entry for entry in mood_data 
                         if datetime.fromisoformat(entry['timestamp']) > datetime.now() - timedelta(days=7)]
        
        if recent_entries:
            recent_emotions = [entry['primary_emotion'] for entry in recent_entries]
            most_common = Counter(recent_emotions).most_common(1)[0]
            
            print(f"📊 Quick Stats (Last 7 days):")
            print(f"   • Total entries: {len(recent_entries)}")
            print(f"   • Most common emotion: {most_common[0].title()} ({most_common[1]} times)")
            
            # Emotional balance
            positive_count = sum(1 for emotion in recent_emotions 
                               if emotion in self.emotion_categories['positive'])
            balance_ratio = positive_count / len(recent_emotions) if recent_entries else 0
            
            if balance_ratio > 0.6:
                print(f"   • Emotional balance: 🌟 Positive ({balance_ratio:.1%})")
            elif balance_ratio > 0.4:
                print(f"   • Emotional balance: ⚖️ Balanced ({balance_ratio:.1%})")
            else:
                print(f"   • Emotional balance: 🌧️ Challenging ({balance_ratio:.1%})")
            
            print()
    
    def _comprehensive_emotion_report(self):
        """Generate comprehensive emotion analysis report"""
        print("\n📋 Comprehensive Emotion Report")
        print("=" * 50)
        
        # Time period selection
        print("Select analysis period:")
        print("1. Last 7 days")
        print("2. Last 30 days")
        print("3. Last 90 days")
        print("4. All time")
        print("5. Custom date range")
        
        period_choice = input("Choose period (1-5): ").strip()
        
        start_date, end_date = self._get_date_range(period_choice)
        mood_data = self._load_mood_data_in_range(start_date, end_date)
        
        if not mood_data:
            print("No mood data found for the selected period.")
            return
        
        print(f"\n📊 Analysis Report ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})")
        print("=" * 60)
        
        # 1. Basic Statistics
        self._report_basic_statistics(mood_data)
        
        # 2. Emotion Distribution
        self._report_emotion_distribution(mood_data)
        
        # 3. Intensity Analysis
        self._report_intensity_analysis(mood_data)
        
        # 4. Temporal Patterns
        self._report_temporal_patterns(mood_data)
        
        # 5. Trigger Analysis
        self._report_trigger_summary(mood_data)
        
        # 6. Recommendations
        self._report_recommendations(mood_data)
        
        input("\nPress Enter to continue...")
    
    def _report_basic_statistics(self, mood_data: List[Dict]):
        """Report basic emotional statistics"""
        print("\n📈 Basic Statistics")
        print("-" * 20)
        
        total_entries = len(mood_data)
        unique_emotions = len(set(entry['primary_emotion'] for entry in mood_data))
        
        # Calculate average entries per day
        if mood_data:
            first_date = datetime.fromisoformat(mood_data[0]['timestamp'])
            last_date = datetime.fromisoformat(mood_data[-1]['timestamp'])
            days_span = (last_date - first_date).days + 1
            avg_per_day = total_entries / days_span if days_span > 0 else total_entries
        else:
            avg_per_day = 0
        
        print(f"Total mood entries: {total_entries}")
        print(f"Unique emotions tracked: {unique_emotions}")
        print(f"Average entries per day: {avg_per_day:.1f}")
        
        # Emotional diversity score
        diversity_score = unique_emotions / total_entries if total_entries > 0 else 0
        print(f"Emotional diversity score: {diversity_score:.2f}")
        
        if diversity_score > 0.3:
            print("✅ High emotional awareness - you recognize many different emotions")
        elif diversity_score > 0.15:
            print("⚖️ Moderate emotional awareness - consider exploring more emotion words")
        else:
            print("🎯 Opportunity to expand emotional vocabulary")
    
    def _report_emotion_distribution(self, mood_data: List[Dict]):
        """Report emotion distribution analysis"""
        print("\n🎨 Emotion Distribution")
        print("-" * 25)
        
        # Count emotions by category
        category_counts = defaultdict(int)
        emotion_counts = Counter()
        
        for entry in mood_data:
            emotion = entry['primary_emotion']
            emotion_counts[emotion] += 1
            
            # Categorize emotion
            for category, emotions in self.emotion_categories.items():
                if emotion in emotions:
                    category_counts[category] += 1
                    break
        
        # Show category distribution
        total = len(mood_data)
        print("Emotional categories:")
        for category, count in category_counts.items():
            percentage = (count / total) * 100
            bar = "█" * int(percentage / 5)  # Visual bar
            print(f"  {category.title():10} {count:3d} ({percentage:5.1f}%) {bar}")
        
        print()
        
        # Top emotions
        print("Most frequent emotions:")
        for emotion, count in emotion_counts.most_common(5):
            percentage = (count / total) * 100
            print(f"  {emotion.title():15} {count:3d} times ({percentage:5.1f}%)")
    
    def _report_intensity_analysis(self, mood_data: List[Dict]):
        """Report emotional intensity analysis"""
        print("\n🌡️ Intensity Analysis")
        print("-" * 20)
        
        # Extract intensity values
        intensities = []
        for entry in mood_data:
            intensity = entry.get('intensity', 3)  # Default to 3 if not specified
            if isinstance(intensity, str):
                # Convert string intensities to numbers
                intensity_map = {"very_low": 1, "low": 2, "moderate": 3, "high": 4, "very_high": 5}
                intensity = intensity_map.get(intensity, 3)
            intensities.append(intensity)
        
        if intensities:
            avg_intensity = statistics.mean(intensities)
            median_intensity = statistics.median(intensities)
            intensity_range = max(intensities) - min(intensities)
            
            print(f"Average intensity: {avg_intensity:.1f}/5")
            print(f"Median intensity: {median_intensity:.1f}/5")
            print(f"Intensity range: {intensity_range}")
            
            # Intensity distribution
            intensity_counts = Counter(intensities)
            print("\nIntensity distribution:")
            for i in range(1, 6):
                count = intensity_counts.get(i, 0)
                percentage = (count / len(intensities)) * 100
                stars = "⭐" * i
                print(f"  {stars:10} {count:3d} times ({percentage:5.1f}%)")
            
            # Insights
            if avg_intensity > 4:
                print("\n💡 Your emotions tend to be very intense. Consider stress management techniques.")
            elif avg_intensity > 3.5:
                print("\n💡 You experience moderately intense emotions. This is quite normal.")
            elif avg_intensity < 2.5:
                print("\n💡 Your emotions tend to be mild. Consider if you're fully connecting with your feelings.")
    
    def _report_temporal_patterns(self, mood_data: List[Dict]):
        """Report temporal patterns in emotions"""
        print("\n⏰ Temporal Patterns")
        print("-" * 20)
        
        # Group by hour of day
        hour_emotions = defaultdict(list)
        day_emotions = defaultdict(list)
        
        for entry in mood_data:
            timestamp = datetime.fromisoformat(entry['timestamp'])
            hour = timestamp.hour
            day = timestamp.strftime('%A')
            emotion = entry['primary_emotion']
            
            hour_emotions[hour].append(emotion)
            day_emotions[day].append(emotion)
        
        # Find best and worst times
        if hour_emotions:
            hour_positivity = {}
            for hour, emotions in hour_emotions.items():
                positive_count = sum(1 for e in emotions if e in self.emotion_categories['positive'])
                hour_positivity[hour] = positive_count / len(emotions) if emotions else 0
            
            best_hour = max(hour_positivity.items(), key=lambda x: x[1])
            worst_hour = min(hour_positivity.items(), key=lambda x: x[1])
            
            print(f"Best time of day: {best_hour[0]:02d}:00 ({best_hour[1]:.1%} positive)")
            print(f"Challenging time: {worst_hour[0]:02d}:00 ({worst_hour[1]:.1%} positive)")
        
        # Day of week patterns
        if day_emotions:
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            print("\nDay of week patterns:")
            
            for day in day_order:
                if day in day_emotions:
                    emotions = day_emotions[day]
                    positive_count = sum(1 for e in emotions if e in self.emotion_categories['positive'])
                    positivity = positive_count / len(emotions) if emotions else 0
                    
                    mood_indicator = "😊" if positivity > 0.6 else "😐" if positivity > 0.4 else "😔"
                    print(f"  {day:9} {mood_indicator} {len(emotions):2d} entries ({positivity:.1%} positive)")
    
    def _trigger_analysis(self):
        """Analyze emotional triggers and patterns"""
        print("\n🎯 Trigger Analysis & Insights")
        print("=" * 40)
        
        mood_data = self._load_mood_data()
        if not mood_data:
            print("No mood data available for trigger analysis.")
            return
        
        # Extract triggers from mood entries
        trigger_emotion_map = defaultdict(list)
        trigger_counts = Counter()
        
        for entry in mood_data:
            triggers = entry.get('triggers', [])
            emotion = entry['primary_emotion']
            
            for trigger in triggers:
                trigger_lower = trigger.lower()
                trigger_emotion_map[trigger_lower].append(emotion)
                trigger_counts[trigger_lower] += 1
        
        if not trigger_counts:
            print("No triggers found in your mood data.")
            print("Start adding triggers to your mood entries to unlock trigger analysis!")
            return
        
        print("🔍 Most Common Triggers:")
        for trigger, count in trigger_counts.most_common(10):
            emotions = trigger_emotion_map[trigger]
            
            # Calculate emotional impact
            positive_count = sum(1 for e in emotions if e in self.emotion_categories['positive'])
            negative_count = sum(1 for e in emotions if e in self.emotion_categories['negative'])
            
            if positive_count > negative_count:
                impact = f"😊 Positive ({positive_count}/{len(emotions)})"
            elif negative_count > positive_count:
                impact = f"😔 Negative ({negative_count}/{len(emotions)})"
            else:
                impact = f"😐 Mixed ({len(emotions)} entries)"
            
            print(f"  {trigger.title():20} {count:3d} times - {impact}")
        
        print()
        
        # Trigger categories analysis
        self._analyze_trigger_categories(trigger_emotion_map)
        
        # Recommendations
        self._trigger_recommendations(trigger_emotion_map, trigger_counts)
        
        input("Press Enter to continue...")
    
    def _analyze_trigger_categories(self, trigger_emotion_map: Dict):
        """Analyze triggers by category"""
        print("📊 Trigger Categories:")
        
        category_impacts = defaultdict(lambda: {'positive': 0, 'negative': 0, 'total': 0})
        
        for trigger, emotions in trigger_emotion_map.items():
            # Find category for this trigger
            trigger_category = None
            for category, keywords in self.trigger_categories.items():
                if any(keyword in trigger for keyword in keywords):
                    trigger_category = category
                    break
            
            if not trigger_category:
                trigger_category = 'other'
            
            # Count emotional impacts
            positive_count = sum(1 for e in emotions if e in self.emotion_categories['positive'])
            negative_count = sum(1 for e in emotions if e in self.emotion_categories['negative'])
            
            category_impacts[trigger_category]['positive'] += positive_count
            category_impacts[trigger_category]['negative'] += negative_count
            category_impacts[trigger_category]['total'] += len(emotions)
        
        # Display category analysis
        for category, impacts in sorted(category_impacts.items()):
            total = impacts['total']
            if total == 0:
                continue
                
            positive_ratio = impacts['positive'] / total
            negative_ratio = impacts['negative'] / total
            
            if positive_ratio > 0.6:
                category_mood = "😊 Positive"
            elif negative_ratio > 0.6:
                category_mood = "😔 Challenging"
            else:
                category_mood = "😐 Mixed"
            
            print(f"  {category.title():15} {total:3d} entries - {category_mood}")
    
    def _trigger_recommendations(self, trigger_emotion_map: Dict, trigger_counts: Counter):
        """Provide recommendations based on trigger analysis"""
        print("\n💡 Trigger Insights & Recommendations:")
        
        # Find most problematic triggers
        problematic_triggers = []
        positive_triggers = []
        
        for trigger, emotions in trigger_emotion_map.items():
            if len(emotions) < 3:  # Skip infrequent triggers
                continue
                
            negative_count = sum(1 for e in emotions if e in self.emotion_categories['negative'])
            positive_count = sum(1 for e in emotions if e in self.emotion_categories['positive'])
            
            negative_ratio = negative_count / len(emotions)
            positive_ratio = positive_count / len(emotions)
            
            if negative_ratio > 0.7:
                problematic_triggers.append((trigger, negative_ratio, len(emotions)))
            elif positive_ratio > 0.7:
                positive_triggers.append((trigger, positive_ratio, len(emotions)))
        
        # Show problematic triggers
        if problematic_triggers:
            print("\n⚠️ Challenging Triggers to Address:")
            for trigger, ratio, count in sorted(problematic_triggers, key=lambda x: x[1], reverse=True)[:3]:
                print(f"  • {trigger.title()} - {ratio:.1%} negative impact ({count} times)")
                print(f"    💡 Consider: coping strategies, avoidance, or professional support")
        
        # Show positive triggers
        if positive_triggers:
            print("\n🌟 Positive Triggers to Cultivate:")
            for trigger, ratio, count in sorted(positive_triggers, key=lambda x: x[1], reverse=True)[:3]:
                print(f"  • {trigger.title()} - {ratio:.1%} positive impact ({count} times)")
                print(f"    💡 Consider: increasing exposure or building routines around this")
    
    def _pattern_recognition_dashboard(self):
        """Show pattern recognition dashboard"""
        print("\n🔍 Pattern Recognition Dashboard")
        print("=" * 40)
        
        print("Available pattern analyses:")
        for i, (pattern_type, description) in enumerate(self.pattern_types.items(), 1):
            print(f"{i}. {description}")
        
        print()
        choice = input(f"Choose pattern type (1-{len(self.pattern_types)}) or press Enter to return: ").strip()
        
        try:
            choice_idx = int(choice) - 1
            pattern_types_list = list(self.pattern_types.keys())
            if 0 <= choice_idx < len(pattern_types_list):
                pattern_type = pattern_types_list[choice_idx]
                self._analyze_specific_pattern(pattern_type)
        except ValueError:
            pass
    
    def _analyze_specific_pattern(self, pattern_type: str):
        """Analyze a specific pattern type"""
        print(f"\n📊 {self.pattern_types[pattern_type]}")
        print("=" * 40)
        
        mood_data = self._load_mood_data()
        if not mood_data:
            print("No mood data available for pattern analysis.")
            return
        
        if pattern_type == "daily":
            self._analyze_daily_patterns(mood_data)
        elif pattern_type == "weekly":
            self._analyze_weekly_patterns(mood_data)
        elif pattern_type == "monthly":
            self._analyze_monthly_patterns(mood_data)
        elif pattern_type == "seasonal":
            self._analyze_seasonal_patterns(mood_data)
        elif pattern_type == "trigger_based":
            self._analyze_trigger_patterns(mood_data)
        elif pattern_type == "recovery":
            self._analyze_recovery_patterns(mood_data)
        elif pattern_type == "intensity":
            self._analyze_intensity_patterns(mood_data)
        
        input("\nPress Enter to continue...")
    
    def _analyze_daily_patterns(self, mood_data: List[Dict]):
        """Analyze daily emotional patterns"""
        print("Daily emotional patterns analysis:")
        
        # Group emotions by hour
        hourly_emotions = defaultdict(list)
        for entry in mood_data:
            hour = datetime.fromisoformat(entry['timestamp']).hour
            emotion = entry['primary_emotion']
            hourly_emotions[hour].append(emotion)
        
        # Find patterns
        print("\nHourly emotional trends:")
        for hour in range(24):
            if hour in hourly_emotions:
                emotions = hourly_emotions[hour]
                positive_count = sum(1 for e in emotions if e in self.emotion_categories['positive'])
                ratio = positive_count / len(emotions) if emotions else 0
                
                mood_bar = "█" * int(ratio * 10)
                print(f"{hour:2d}:00 {mood_bar:10} {len(emotions):2d} entries ({ratio:.1%} positive)")
    
    def _get_date_range(self, period_choice: str) -> Tuple[datetime, datetime]:
        """Get date range based on user choice"""
        end_date = datetime.now()
        
        if period_choice == "1":  # Last 7 days
            start_date = end_date - timedelta(days=7)
        elif period_choice == "2":  # Last 30 days
            start_date = end_date - timedelta(days=30)
        elif period_choice == "3":  # Last 90 days
            start_date = end_date - timedelta(days=90)
        elif period_choice == "4":  # All time
            start_date = datetime(2020, 1, 1)  # Far back date
        else:  # Custom or default
            start_date = end_date - timedelta(days=30)  # Default to 30 days
        
        return start_date, end_date
    
    def _load_mood_data(self) -> List[Dict]:
        """Load mood data from mood tracking module"""
        mood_file = os.path.expanduser("~/.om_moods.json")
        if not os.path.exists(mood_file):
            return []
        
        try:
            with open(mood_file, 'r') as f:
                data = json.load(f)
                return data.get('mood_entries', [])
        except Exception:
            return []
    
    def _load_mood_data_in_range(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Load mood data within date range"""
        all_data = self._load_mood_data()
        
        filtered_data = []
        for entry in all_data:
            entry_date = datetime.fromisoformat(entry['timestamp'])
            if start_date <= entry_date <= end_date:
                filtered_data.append(entry)
        
        return filtered_data
    
    def _emotional_recovery_analysis(self):
        """Analyze emotional recovery patterns"""
        print("\n🌱 Emotional Recovery Analysis")
        print("=" * 40)
        print("This feature would analyze how quickly you recover from negative emotions")
        print("and identify your most effective recovery strategies.")
    
    def _mood_prediction_insights(self):
        """Provide mood prediction insights"""
        print("\n🔮 Mood Prediction Insights")
        print("=" * 30)
        print("This feature would use pattern analysis to predict potential mood changes")
        print("and suggest preventive strategies.")
    
    def _comparative_analysis(self):
        """Compare different time periods"""
        print("\n📊 Comparative Analysis")
        print("=" * 30)
        print("This feature would compare emotional patterns between different time periods")
        print("to track progress and identify trends.")
    
    def _export_analysis_data(self):
        """Export analysis data"""
        print("\n💾 Export Analysis Data")
        print("=" * 30)
        print("This feature would export your emotional analysis data")
        print("in various formats for external analysis or sharing with professionals.")
    
    def _set_analysis_preferences(self):
        """Set analysis preferences"""
        print("\n⚙️ Analysis Preferences")
        print("=" * 30)
        print("This feature would allow you to customize analysis parameters")
        print("and set preferences for reports and insights.")


def emotion_analysis_command(action: str = "menu", **kwargs):
    """Main emotion analysis command interface"""
    analysis = EmotionAnalysis()
    
    if action == "menu":
        analysis.show_analysis_menu()
    elif action == "report":
        analysis._comprehensive_emotion_report()
    elif action == "triggers":
        analysis._trigger_analysis()
    elif action == "patterns":
        analysis._pattern_recognition_dashboard()
    elif action == "recovery":
        analysis._emotional_recovery_analysis()
    elif action == "prediction":
        analysis._mood_prediction_insights()
    elif action == "compare":
        analysis._comparative_analysis()
    elif action == "export":
        analysis._export_analysis_data()
    else:
        print(f"Unknown analysis action: {action}")
        print("Available actions: menu, report, triggers, patterns, recovery, prediction, compare, export")
