"""
Hypnosis and Guided Visualization module for om - inspired by Hypnomatic
Digital hypnosis sessions for personal development and psychological wellness
"""

import time
import random
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

HYPNOSIS_FILE = os.path.expanduser("~/.om_hypnosis.json")

class HypnosisSessionManager:
    def __init__(self):
        self.sessions = {
            # Mental Health & Wellness
            "stress_relief": {
                "title": "Deep Stress Relief",
                "category": "Mental Health",
                "duration": "20-25 minutes",
                "description": "Release tension and achieve profound relaxation",
                "benefits": ["Reduces cortisol levels", "Calms nervous system", "Improves sleep quality"],
                "contraindications": ["Active psychosis", "Severe anxiety disorders"],
                "frequency": "Daily for 2 weeks, then as needed"
            },
            "anxiety_reduction": {
                "title": "Anxiety Reduction",
                "category": "Mental Health", 
                "duration": "15-20 minutes",
                "description": "Calm anxious thoughts and build inner peace",
                "benefits": ["Reduces anxiety symptoms", "Builds confidence", "Improves emotional regulation"],
                "contraindications": ["Panic disorder without professional guidance"],
                "frequency": "2-3 times per week"
            },
            "depression_support": {
                "title": "Mood Enhancement",
                "category": "Mental Health",
                "duration": "25-30 minutes", 
                "description": "Lift mood and cultivate positive mental patterns",
                "benefits": ["Improves mood", "Increases motivation", "Builds resilience"],
                "contraindications": ["Severe depression", "Suicidal ideation"],
                "frequency": "3-4 times per week"
            },
            "insomnia_relief": {
                "title": "Deep Sleep Induction",
                "category": "Sleep",
                "duration": "30-45 minutes",
                "description": "Overcome insomnia and achieve restorative sleep",
                "benefits": ["Improves sleep quality", "Reduces sleep latency", "Enhances dream recall"],
                "contraindications": ["Sleep apnea", "Narcolepsy"],
                "frequency": "Nightly for 3-4 weeks"
            },
            
            # Personal Development
            "self_confidence": {
                "title": "Unshakeable Self-Confidence",
                "category": "Personal Development",
                "duration": "20-25 minutes",
                "description": "Build deep, lasting self-confidence and self-worth",
                "benefits": ["Increases self-esteem", "Reduces social anxiety", "Improves performance"],
                "contraindications": ["Narcissistic personality traits"],
                "frequency": "Daily for 3 weeks"
            },
            "focus_concentration": {
                "title": "Laser Focus & Concentration",
                "category": "Cognitive Enhancement",
                "duration": "15-20 minutes",
                "description": "Enhance mental clarity and sustained attention",
                "benefits": ["Improves focus", "Enhances productivity", "Reduces mental fatigue"],
                "contraindications": ["ADHD without professional guidance"],
                "frequency": "Before important tasks"
            },
            "creativity_boost": {
                "title": "Creative Breakthrough",
                "category": "Cognitive Enhancement",
                "duration": "25-30 minutes",
                "description": "Unlock creative potential and innovative thinking",
                "benefits": ["Enhances creativity", "Improves problem-solving", "Increases inspiration"],
                "contraindications": ["Manic episodes"],
                "frequency": "2-3 times per week"
            },
            
            # Habit Change
            "weight_management": {
                "title": "Healthy Weight & Body Image",
                "category": "Habit Change",
                "duration": "25-30 minutes",
                "description": "Develop healthy eating habits and positive body image",
                "benefits": ["Improves eating habits", "Enhances body image", "Increases motivation"],
                "contraindications": ["Eating disorders", "Body dysmorphia"],
                "frequency": "Daily for 6-8 weeks"
            },
            "quit_smoking": {
                "title": "Freedom from Smoking",
                "category": "Habit Change",
                "duration": "30-35 minutes",
                "description": "Break free from smoking addiction permanently",
                "benefits": ["Reduces cravings", "Builds willpower", "Improves health motivation"],
                "contraindications": ["Severe withdrawal symptoms"],
                "frequency": "Daily for first month"
            },
            "overcome_fears": {
                "title": "Fear Liberation",
                "category": "Personal Development",
                "duration": "20-25 minutes",
                "description": "Release limiting fears and phobias",
                "benefits": ["Reduces phobic responses", "Builds courage", "Increases life satisfaction"],
                "contraindications": ["Trauma-related fears without therapy"],
                "frequency": "3-4 times per week"
            },
            
            # Specialized Sessions
            "pain_management": {
                "title": "Natural Pain Relief",
                "category": "Health & Healing",
                "duration": "25-30 minutes",
                "description": "Reduce chronic pain through mind-body techniques",
                "benefits": ["Reduces pain perception", "Improves coping", "Enhances quality of life"],
                "contraindications": ["Undiagnosed pain", "Acute medical conditions"],
                "frequency": "Daily for chronic conditions"
            },
            "lucid_dreaming": {
                "title": "Lucid Dream Mastery",
                "category": "Consciousness",
                "duration": "20-25 minutes",
                "description": "Develop the ability to control your dreams",
                "benefits": ["Enhances dream recall", "Develops lucid dreaming", "Improves sleep quality"],
                "contraindications": ["Sleep disorders", "Nightmares"],
                "frequency": "Before sleep, 4-5 times per week"
            },
            "energy_vitality": {
                "title": "Boundless Energy & Vitality",
                "category": "Health & Healing",
                "duration": "15-20 minutes",
                "description": "Boost natural energy and overcome fatigue",
                "benefits": ["Increases energy", "Improves motivation", "Enhances vitality"],
                "contraindications": ["Chronic fatigue syndrome", "Thyroid disorders"],
                "frequency": "Morning sessions, daily"
            }
        }
        
        # Neurowave frequencies (Hz) for different states
        self.brainwave_frequencies = {
            "delta": (0.5, 4),      # Deep sleep, healing
            "theta": (4, 8),        # Deep meditation, creativity
            "alpha": (8, 13),       # Relaxed awareness, learning
            "beta": (13, 30),       # Normal waking consciousness
            "gamma": (30, 100)      # Higher consciousness, insight
        }
        
        # Safety guidelines
        self.safety_guidelines = [
            "Do not use while driving or operating machinery",
            "Avoid use under influence of alcohol or drugs", 
            "Stop if you experience dizziness or discomfort",
            "Consult healthcare provider if you have medical conditions",
            "Not recommended for epilepsy, schizophrenia, or psychosis",
            "Pregnant women should consult doctor before use",
            "Children under 16 should have parental supervision"
        ]
    
    def show_session_menu(self):
        """Display available hypnosis sessions"""
        print("🌀 Hypnosis & Guided Visualization Sessions")
        print("=" * 70)
        print("Digital hypnosis sessions for personal development and wellness")
        print("Inspired by computerized hypnotic techniques and neurowave stimulation")
        print()
        
        # Group sessions by category
        categories = {}
        for session_id, session_info in self.sessions.items():
            category = session_info["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append((session_id, session_info))
        
        # Display by category
        session_number = 1
        session_map = {}
        
        for category, sessions in categories.items():
            print(f"📂 {category}:")
            for session_id, session_info in sessions:
                print(f"   {session_number}. {session_info['title']}")
                print(f"      {session_info['description']}")
                print(f"      Duration: {session_info['duration']}")
                session_map[session_number] = session_id
                session_number += 1
            print()
        
        # Show usage statistics
        self._show_usage_stats()
        
        # Session selection
        print("⚠️  Important Safety Information:")
        print("• These sessions use guided visualization and relaxation techniques")
        print("• Not suitable for severe mental health conditions without professional guidance")
        print("• Stop immediately if you experience any discomfort")
        print()
        
        choice = input(f"Choose a session (1-{len(self.sessions)}) or press Enter to return: ").strip()
        
        if choice.isdigit():
            try:
                choice_num = int(choice)
                if choice_num in session_map:
                    session_id = session_map[choice_num]
                    self._show_session_details(session_id)
            except ValueError:
                pass
    
    def _show_session_details(self, session_id: str):
        """Show detailed information about a session"""
        if session_id not in self.sessions:
            print(f"Session '{session_id}' not found.")
            return
        
        session = self.sessions[session_id]
        
        print(f"\n🌀 {session['title']}")
        print("=" * 60)
        print(f"Category: {session['category']}")
        print(f"Duration: {session['duration']}")
        print(f"Recommended Frequency: {session['frequency']}")
        print()
        
        print("📋 Description:")
        print(f"   {session['description']}")
        print()
        
        print("✨ Benefits:")
        for benefit in session['benefits']:
            print(f"   • {benefit}")
        print()
        
        print("⚠️  Contraindications:")
        for contraindication in session['contraindications']:
            print(f"   • {contraindication}")
        print()
        
        # Check usage history
        usage_data = self._load_hypnosis_data()
        session_history = [s for s in usage_data.get('sessions', []) if s['session_id'] == session_id]
        
        if session_history:
            last_session = max(session_history, key=lambda x: x['timestamp'])
            last_date = datetime.fromisoformat(last_session['timestamp']).strftime('%Y-%m-%d')
            print(f"📊 Last used: {last_date} (Total uses: {len(session_history)})")
            print()
        
        # Safety check
        print("🛡️  Safety Confirmation:")
        print("Before starting, please confirm:")
        print("• You are in a safe, comfortable environment")
        print("• You will not be driving or operating machinery")
        print("• You do not have any contraindicated conditions")
        print("• You understand this is for wellness, not medical treatment")
        print()
        
        consent = input("Do you confirm the above and wish to proceed? (y/n): ").strip().lower()
        
        if consent == 'y':
            self._start_hypnosis_session(session_id, session)
        else:
            print("Session cancelled. Your safety is our priority.")
    
    def _start_hypnosis_session(self, session_id: str, session: Dict):
        """Start a hypnosis session"""
        print(f"\n🌀 Starting: {session['title']}")
        print("=" * 50)
        
        # Pre-session preparation
        print("🧘‍♀️ Preparation Phase:")
        print("• Find a comfortable position (sitting or lying down)")
        print("• Ensure you won't be disturbed")
        print("• Close your eyes or soften your gaze")
        print("• Take three deep breaths to begin relaxing")
        print()
        
        input("Press Enter when you're ready to begin the session...")
        print()
        
        # Session phases
        self._induction_phase(session)
        self._deepening_phase(session)
        self._therapeutic_phase(session_id, session)
        self._emergence_phase(session)
        
        # Post-session
        self._post_session_integration(session_id, session)
    
    def _induction_phase(self, session: Dict):
        """Hypnotic induction phase"""
        print("🌊 Induction Phase - Entering Relaxation")
        print("=" * 45)
        
        induction_scripts = [
            "Allow your eyes to close gently... and as they do, notice how your body begins to relax...",
            "With each breath you take, you're becoming more and more relaxed...",
            "Feel the tension leaving your body, starting from the top of your head...",
            "Your breathing is becoming slower and deeper... more rhythmic and peaceful...",
            "Notice how comfortable and heavy your body feels as you sink deeper into relaxation...",
            "Your mind is becoming quieter... more peaceful... more focused...",
            "You're entering a state of deep, comfortable relaxation...",
            "This is your time... your space... completely safe and peaceful..."
        ]
        
        for i, script in enumerate(induction_scripts, 1):
            print(f"🌀 {script}")
            
            # Simulate progressive relaxation timing
            if i <= 3:
                time.sleep(8)  # Slower initial pace
            elif i <= 6:
                time.sleep(6)  # Medium pace
            else:
                time.sleep(4)  # Faster as relaxation deepens
            
            print()
        
        print("✨ You are now in a comfortable state of relaxation...")
        time.sleep(3)
        print()
    
    def _deepening_phase(self, session: Dict):
        """Deepening the hypnotic state"""
        print("🌊 Deepening Phase - Going Deeper")
        print("=" * 40)
        
        deepening_techniques = [
            "Imagine yourself at the top of a beautiful staircase with 10 steps...",
            "With each step down, you'll go twice as deep into relaxation...",
            "10... stepping down... feeling more relaxed...",
            "9... deeper and deeper... completely safe...",
            "8... letting go of any remaining tension...",
            "7... your mind becoming quieter and more focused...",
            "6... halfway down... feeling wonderful...",
            "5... deeper still... completely comfortable...",
            "4... almost there... so peaceful and calm...",
            "3... deeper and deeper...",
            "2... almost at the bottom...",
            "1... and now you're at the bottom... in a perfect state of deep relaxation..."
        ]
        
        for technique in deepening_techniques:
            print(f"🌀 {technique}")
            time.sleep(3)
        
        print("\n✨ You are now in a deep, therapeutic state of relaxation...")
        time.sleep(3)
        print()
    
    def _therapeutic_phase(self, session_id: str, session: Dict):
        """Main therapeutic content phase"""
        print(f"🎯 Therapeutic Phase - {session['title']}")
        print("=" * 50)
        
        # Session-specific therapeutic content
        therapeutic_content = self._get_therapeutic_content(session_id)
        
        for i, content in enumerate(therapeutic_content, 1):
            print(f"💫 {content}")
            
            # Vary timing based on content importance
            if "imagine" in content.lower() or "visualize" in content.lower():
                time.sleep(8)  # Longer for visualization
            elif "repeat" in content.lower() or "affirm" in content.lower():
                time.sleep(6)  # Medium for affirmations
            else:
                time.sleep(5)  # Standard timing
            
            print()
        
        print("✨ These positive changes are becoming part of who you are...")
        time.sleep(5)
        print()
    
    def _emergence_phase(self, session: Dict):
        """Bringing the person back to normal consciousness"""
        print("🌅 Emergence Phase - Returning to Awareness")
        print("=" * 45)
        
        emergence_script = [
            "In a moment, I'll count from 1 to 5...",
            "With each number, you'll become more alert and aware...",
            "1... beginning to return... feeling refreshed...",
            "2... becoming more aware of your surroundings...",
            "3... energy returning to your body... feeling wonderful...",
            "4... almost fully alert... feeling positive and confident...",
            "5... eyes open, fully alert, completely refreshed and renewed!"
        ]
        
        for script in emergence_script:
            print(f"🌀 {script}")
            time.sleep(3)
        
        print("\n✨ Welcome back! You are fully alert and feeling wonderful.")
        time.sleep(2)
        print()
    
    def _post_session_integration(self, session_id: str, session: Dict):
        """Post-session integration and feedback"""
        print("🌟 Session Complete - Integration")
        print("=" * 40)
        
        print(f"You've completed: {session['title']}")
        print(f"Duration: {session['duration']}")
        print()
        
        # Feedback collection
        print("💭 How do you feel now?")
        
        mood_after = input("Rate your current state (1-10, 10=excellent): ").strip()
        experience_rating = input("Rate the session experience (1-10): ").strip()
        
        try:
            mood_after = max(1, min(10, int(mood_after)))
            experience_rating = max(1, min(10, int(experience_rating)))
        except ValueError:
            mood_after = experience_rating = None
        
        # Insights and observations
        insights = input("Any insights or observations from the session? (optional): ").strip()
        
        # Integration suggestions
        print(f"\n💡 Integration Suggestions:")
        integration_tips = self._get_integration_tips(session_id)
        for tip in integration_tips:
            print(f"   • {tip}")
        
        print(f"\n📅 Recommended next session: {session['frequency']}")
        
        # Save session data
        self._save_session_data(session_id, session, mood_after, experience_rating, insights)
        
        print("\n🌟 Thank you for taking time for your personal development!")
        print("Remember: Change happens through consistent practice and patience.")
    
    def _get_therapeutic_content(self, session_id: str) -> List[str]:
        """Get session-specific therapeutic content"""
        content_library = {
            "stress_relief": [
                "Imagine all the stress and tension in your body as dark clouds...",
                "Now see a warm, golden light beginning to dissolve these clouds...",
                "With each breath, more stress melts away, replaced by peace and calm...",
                "Your body knows how to relax completely... trust this natural ability...",
                "Repeat silently: 'I am calm, peaceful, and in control'...",
                "See yourself handling future challenges with ease and confidence...",
                "This deep relaxation is always available to you..."
            ],
            
            "anxiety_reduction": [
                "Notice how safe and secure you feel in this peaceful state...",
                "Imagine your anxiety as leaves floating down a gentle stream...",
                "Watch them drift away, carrying your worries with them...",
                "Your breathing is calm and steady... your heart rate peaceful...",
                "Repeat: 'I am safe, I am calm, I trust in my ability to cope'...",
                "Visualize yourself in situations that used to cause anxiety, now feeling confident and at ease...",
                "This inner peace grows stronger each day..."
            ],
            
            "self_confidence": [
                "See yourself as the confident, capable person you truly are...",
                "Feel this confidence radiating from your core, filling every cell...",
                "Remember times when you succeeded, when you felt proud and accomplished...",
                "This confidence is your natural state... it belongs to you...",
                "Repeat: 'I am confident, capable, and worthy of success'...",
                "Imagine yourself in future situations, radiating confidence and self-assurance...",
                "Others are drawn to your authentic confidence and positive energy..."
            ],
            
            "insomnia_relief": [
                "Your body is becoming heavier and more relaxed with each breath...",
                "Imagine yourself in the most comfortable, peaceful place...",
                "All the day's thoughts and concerns are drifting away like clouds...",
                "Your mind is becoming quieter... more peaceful... ready for rest...",
                "Your body knows exactly how to fall into deep, restorative sleep...",
                "Each night, falling asleep becomes easier and more natural...",
                "You wake refreshed and energized after deep, peaceful sleep..."
            ],
            
            "focus_concentration": [
                "Your mind is becoming clear and focused, like a laser beam...",
                "Distractions simply bounce off your concentrated awareness...",
                "You have the ability to focus completely on whatever you choose...",
                "Your concentration grows stronger and more sustained each day...",
                "Repeat: 'My mind is clear, focused, and completely present'...",
                "See yourself accomplishing tasks with ease and sustained attention...",
                "This focused state is natural and available to you whenever needed..."
            ]
        }
        
        return content_library.get(session_id, [
            "You are entering a state of positive transformation...",
            "Your subconscious mind is open to beneficial changes...",
            "These positive suggestions are taking root in your mind...",
            "You have the power to create positive change in your life...",
            "Each day, you become more aligned with your highest potential..."
        ])
    
    def _get_integration_tips(self, session_id: str) -> List[str]:
        """Get session-specific integration tips"""
        tips_library = {
            "stress_relief": [
                "Practice the relaxation response throughout your day",
                "Take 3 deep breaths when you notice stress building",
                "Use the golden light visualization during stressful moments",
                "Schedule regular relaxation breaks"
            ],
            
            "anxiety_reduction": [
                "Use the floating leaves visualization when anxious thoughts arise",
                "Practice the calming affirmations daily",
                "Remember the feeling of safety from this session",
                "Gradually expose yourself to previously anxiety-provoking situations"
            ],
            
            "self_confidence": [
                "Stand tall and maintain confident posture throughout the day",
                "Recall the feeling of confidence from this session before challenges",
                "Practice positive self-talk and affirmations",
                "Celebrate small wins and acknowledge your capabilities"
            ],
            
            "insomnia_relief": [
                "Use the relaxation techniques as part of your bedtime routine",
                "Create a peaceful sleep environment",
                "Avoid screens 1 hour before bed",
                "Practice the session regularly for 2-3 weeks for best results"
            ]
        }
        
        return tips_library.get(session_id, [
            "Practice the techniques learned in this session daily",
            "Be patient with yourself as changes integrate over time",
            "Notice small improvements and celebrate progress",
            "Consistency is key to lasting transformation"
        ])
    
    def _show_usage_stats(self):
        """Show hypnosis session usage statistics"""
        usage_data = self._load_hypnosis_data()
        sessions = usage_data.get('sessions', [])
        
        if not sessions:
            return
        
        print("📊 Your Hypnosis Journey:")
        
        # Recent sessions
        recent_sessions = sessions[-5:]
        print("Recent sessions:")
        for session in recent_sessions:
            date = datetime.fromisoformat(session['timestamp']).strftime("%m-%d")
            session_title = self.sessions.get(session['session_id'], {}).get('title', session['session_id'])
            rating = session.get('experience_rating', 'N/A')
            print(f"   {date}: {session_title} (Rating: {rating}/10)")
        
        # Statistics
        total_sessions = len(sessions)
        unique_sessions = len(set(s['session_id'] for s in sessions))
        
        print(f"\nTotal sessions completed: {total_sessions}")
        print(f"Different session types tried: {unique_sessions}")
        
        # Most used sessions
        session_counts = {}
        for session in sessions:
            session_id = session['session_id']
            session_counts[session_id] = session_counts.get(session_id, 0) + 1
        
        if session_counts:
            most_used = max(session_counts.items(), key=lambda x: x[1])
            session_title = self.sessions.get(most_used[0], {}).get('title', most_used[0])
            print(f"Most used session: {session_title} ({most_used[1]} times)")
        
        print()
    
    def show_session_history(self):
        """Show detailed session history and progress"""
        usage_data = self._load_hypnosis_data()
        sessions = usage_data.get('sessions', [])
        
        if not sessions:
            print("📊 Hypnosis Session History")
            print("=" * 40)
            print("No sessions completed yet.")
            print("Start your hypnosis journey with 'om hypnosis'!")
            return
        
        print("📊 Your Hypnosis Journey - Detailed History")
        print("=" * 60)
        
        # Group sessions by type
        session_groups = {}
        for session in sessions:
            session_id = session['session_id']
            if session_id not in session_groups:
                session_groups[session_id] = []
            session_groups[session_id].append(session)
        
        # Display by session type
        for session_id, session_list in session_groups.items():
            session_info = self.sessions.get(session_id, {})
            session_title = session_info.get('title', session_id)
            
            print(f"🌀 {session_title}")
            print(f"   Sessions completed: {len(session_list)}")
            
            # Calculate average ratings
            ratings = [s.get('experience_rating') for s in session_list if s.get('experience_rating')]
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                print(f"   Average rating: {avg_rating:.1f}/10")
            
            # Show recent sessions
            recent = session_list[-3:]
            for session in recent:
                date = datetime.fromisoformat(session['timestamp']).strftime("%Y-%m-%d")
                mood = session.get('mood_after', 'N/A')
                print(f"     {date}: Mood after {mood}/10")
            
            print()
        
        # Overall statistics
        total_sessions = len(sessions)
        avg_mood = None
        mood_ratings = [s.get('mood_after') for s in sessions if s.get('mood_after')]
        if mood_ratings:
            avg_mood = sum(mood_ratings) / len(mood_ratings)
        
        print("📈 Overall Progress:")
        print(f"   Total sessions: {total_sessions}")
        if avg_mood:
            print(f"   Average post-session mood: {avg_mood:.1f}/10")
        
        # Calculate session streak
        streak = self._calculate_session_streak(sessions)
        if streak > 0:
            print(f"   Current streak: {streak} days")
        
        print("\n💡 Hypnosis works best with consistent practice.")
        print("   Consider establishing a regular session routine for optimal results.")
    
    def _calculate_session_streak(self, sessions: List[Dict]) -> int:
        """Calculate current hypnosis session streak"""
        if not sessions:
            return 0
        
        # Get unique dates of sessions
        session_dates = []
        for session in sessions:
            session_date = datetime.fromisoformat(session['timestamp']).date()
            session_dates.append(session_date)
        
        unique_dates = sorted(set(session_dates), reverse=True)
        
        streak = 0
        current_date = datetime.now().date()
        
        for session_date in unique_dates:
            if session_date == current_date or session_date == current_date - timedelta(days=streak):
                streak += 1
                current_date = session_date
            else:
                break
        
        return streak
    
    def _save_session_data(self, session_id: str, session: Dict, mood_after: Optional[int], 
                          experience_rating: Optional[int], insights: str):
        """Save hypnosis session data"""
        usage_data = self._load_hypnosis_data()
        
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "session_title": session['title'],
            "category": session['category'],
            "mood_after": mood_after,
            "experience_rating": experience_rating,
            "insights": insights
        }
        
        usage_data.setdefault('sessions', []).append(session_data)
        self._save_hypnosis_data(usage_data)
    
    def _load_hypnosis_data(self) -> Dict:
        """Load hypnosis session data"""
        if not os.path.exists(HYPNOSIS_FILE):
            return {}
        
        try:
            with open(HYPNOSIS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_hypnosis_data(self, data: Dict):
        """Save hypnosis session data"""
        try:
            with open(HYPNOSIS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save hypnosis data: {e}")


def hypnosis_command(action: str = "menu", **kwargs):
    """Main hypnosis sessions command interface"""
    hypnosis = HypnosisSessionManager()
    
    if action == "menu":
        hypnosis.show_session_menu()
    elif action == "history":
        hypnosis.show_session_history()
    elif action == "session":
        session_id = kwargs.get('session')
        if session_id and session_id in hypnosis.sessions:
            hypnosis._show_session_details(session_id)
        else:
            print(f"Unknown session: {session_id}")
            print(f"Available sessions: {', '.join(hypnosis.sessions.keys())}")
    else:
        print(f"Unknown hypnosis action: {action}")
        print("Available actions: menu, history, session")
