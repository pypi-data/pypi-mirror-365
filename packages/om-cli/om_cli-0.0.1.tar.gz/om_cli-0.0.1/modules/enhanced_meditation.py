"""
Enhanced meditation and mindfulness module for om
Comprehensive mindfulness practices for mental health
"""

import time
import random
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

MEDITATION_FILE = os.path.expanduser("~/.om_meditation.json")

class EnhancedMeditation:
    def __init__(self):
        self.meditation_types = {
            "mindfulness": {
                "name": "Mindfulness Meditation",
                "description": "Present-moment awareness and acceptance",
                "best_for": ["stress", "anxiety", "general wellbeing"],
                "duration_options": [5, 10, 15, 20, 30]
            },
            "body_scan": {
                "name": "Body Scan Meditation",
                "description": "Systematic awareness of body sensations",
                "best_for": ["tension", "body awareness", "relaxation"],
                "duration_options": [10, 15, 20, 30, 45]
            },
            "loving_kindness": {
                "name": "Loving-Kindness Meditation",
                "description": "Cultivating compassion for self and others",
                "best_for": ["self-criticism", "relationships", "depression"],
                "duration_options": [10, 15, 20, 25, 30]
            },
            "walking": {
                "name": "Walking Meditation",
                "description": "Mindful movement and awareness",
                "best_for": ["restlessness", "grounding", "energy"],
                "duration_options": [5, 10, 15, 20, 30]
            },
            "breathing": {
                "name": "Breathing Meditation",
                "description": "Focus on breath as anchor for awareness",
                "best_for": ["anxiety", "focus", "beginners"],
                "duration_options": [5, 10, 15, 20, 25]
            },
            "noting": {
                "name": "Noting Meditation",
                "description": "Observing and labeling thoughts and sensations",
                "best_for": ["racing thoughts", "emotional regulation", "insight"],
                "duration_options": [10, 15, 20, 25, 30]
            },
            "visualization": {
                "name": "Visualization Meditation",
                "description": "Guided imagery for healing and peace",
                "best_for": ["trauma", "healing", "creativity"],
                "duration_options": [10, 15, 20, 30, 40]
            }
        }
        
        self.mindfulness_exercises = {
            "five_senses": "5-4-3-2-1 Sensory Grounding",
            "mindful_eating": "Mindful Eating Exercise",
            "mindful_listening": "Mindful Listening Practice",
            "breath_awareness": "Simple Breath Awareness",
            "body_awareness": "Body Awareness Check-in",
            "thought_watching": "Thought Watching Exercise",
            "emotion_surfing": "Emotion Surfing Technique"
        }
        
        self.meditation_challenges = [
            "Restlessness or fidgeting",
            "Racing thoughts",
            "Falling asleep",
            "Physical discomfort",
            "Emotional overwhelm",
            "Boredom or impatience",
            "Self-judgment",
            "Difficulty concentrating"
        ]
    
    def meditation_recommendation(self):
        """Recommend meditation based on current needs"""
        print("🧘‍♀️ Meditation Recommendation")
        print("=" * 40)
        print("Let's find the right meditation practice for you right now.")
        print()
        
        # Current state assessment
        print("How are you feeling right now?")
        feelings = [
            ("stressed", "Stressed or overwhelmed"),
            ("anxious", "Anxious or worried"),
            ("sad", "Sad or down"),
            ("angry", "Angry or irritated"),
            ("restless", "Restless or agitated"),
            ("tired", "Tired or low energy"),
            ("neutral", "Neutral or calm"),
            ("curious", "Curious to explore")
        ]
        
        for i, (key, description) in enumerate(feelings, 1):
            print(f"{i}. {description}")
        
        print()
        choice = input("Choose how you're feeling (1-8): ").strip()
        
        feeling_key = "neutral"
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(feelings):
                feeling_key = feelings[choice_idx][0]
        except ValueError:
            pass
        
        # Time available
        time_available = input("How much time do you have? (5, 10, 15, 20, 30+ minutes): ").strip()
        
        try:
            duration = int(time_available.replace('+', ''))
        except ValueError:
            duration = 10
        
        # Experience level
        print("\nWhat's your meditation experience?")
        experience_levels = [
            ("beginner", "Beginner (new to meditation)"),
            ("some", "Some experience (practiced occasionally)"),
            ("regular", "Regular practitioner"),
            ("advanced", "Advanced practitioner")
        ]
        
        for i, (key, description) in enumerate(experience_levels, 1):
            print(f"{i}. {description}")
        
        experience_choice = input("Choose your experience level (1-4): ").strip()
        
        experience = "beginner"
        try:
            exp_idx = int(experience_choice) - 1
            if 0 <= exp_idx < len(experience_levels):
                experience = experience_levels[exp_idx][0]
        except ValueError:
            pass
        
        # Generate recommendation
        recommended_type = self._get_meditation_recommendation(feeling_key, duration, experience)
        
        print(f"\n🎯 Recommended Practice:")
        meditation_info = self.meditation_types[recommended_type]
        print(f"   {meditation_info['name']}")
        print(f"   {meditation_info['description']}")
        print(f"   Best for: {', '.join(meditation_info['best_for'])}")
        print(f"   Suggested duration: {duration} minutes")
        print()
        
        # Offer to start meditation
        start_now = input("Would you like to start this meditation now? (y/n): ").strip().lower()
        
        if start_now == 'y':
            self.guided_meditation(recommended_type, duration)
        else:
            print("You can start this meditation anytime with:")
            print(f"om meditate --type {recommended_type} --duration {duration}")
    
    def guided_meditation(self, meditation_type: str, duration: int):
        """Conduct guided meditation session"""
        if meditation_type not in self.meditation_types:
            print(f"Unknown meditation type: {meditation_type}")
            return
        
        meditation_info = self.meditation_types[meditation_type]
        
        print(f"\n🧘‍♀️ {meditation_info['name']} - {duration} minutes")
        print("=" * 50)
        print(f"{meditation_info['description']}")
        print()
        
        # Preparation
        print("🌱 Preparation:")
        print("• Find a comfortable position (sitting or lying down)")
        print("• Close your eyes or soften your gaze")
        print("• Take three deep breaths to settle in")
        print("• Set an intention for this practice")
        print()
        
        input("Press Enter when you're ready to begin...")
        print()
        
        # Start meditation based on type
        if meditation_type == "mindfulness":
            self._mindfulness_meditation(duration)
        elif meditation_type == "body_scan":
            self._body_scan_meditation(duration)
        elif meditation_type == "loving_kindness":
            self._loving_kindness_meditation(duration)
        elif meditation_type == "walking":
            self._walking_meditation(duration)
        elif meditation_type == "breathing":
            self._breathing_meditation(duration)
        elif meditation_type == "noting":
            self._noting_meditation(duration)
        elif meditation_type == "visualization":
            self._visualization_meditation(duration)
        
        # Closing
        print("\n✨ Meditation Complete")
        print("Take a moment to notice how you feel now.")
        print("Gently wiggle your fingers and toes.")
        print("When you're ready, slowly open your eyes.")
        print()
        
        # Post-meditation reflection
        self._post_meditation_reflection(meditation_type, duration)
    
    def _mindfulness_meditation(self, duration: int):
        """Guided mindfulness meditation"""
        segments = max(4, duration // 3)  # At least 4 segments
        segment_time = (duration * 60) // segments
        
        prompts = [
            "Begin by noticing your breath. Don't change it, just observe the natural rhythm of breathing in and breathing out.",
            "If your mind wanders, that's completely normal. Gently bring your attention back to your breath without judgment.",
            "Notice the sensations of breathing - the air entering your nostrils, your chest or belly rising and falling.",
            "Expand your awareness to include sounds around you. Notice them without needing to identify or judge them.",
            "Now include physical sensations - the feeling of your body against the chair or floor, any areas of tension or relaxation.",
            "Notice any thoughts that arise. Observe them like clouds passing in the sky, then return to your breath.",
            "Include any emotions present. Welcome them with kindness, knowing that all feelings are temporary.",
            "Rest in this open awareness, present with whatever arises in this moment."
        ]
        
        for i in range(segments):
            if i < len(prompts):
                print(f"🌸 {prompts[i]}")
            else:
                print("🌸 Continue resting in mindful awareness of the present moment.")
            
            time.sleep(segment_time)
            if i < segments - 1:
                print()
    
    def _body_scan_meditation(self, duration: int):
        """Guided body scan meditation"""
        body_parts = [
            "your toes and feet", "your ankles and calves", "your knees and thighs",
            "your hips and pelvis", "your lower back and abdomen", "your chest and upper back",
            "your shoulders", "your arms and hands", "your neck and throat", "your face and head"
        ]
        
        segment_time = (duration * 60) // len(body_parts)
        
        print("🌸 Begin by taking a few deep breaths and settling into your body.")
        time.sleep(10)
        print()
        
        for part in body_parts:
            print(f"🌸 Now bring your attention to {part}.")
            print(f"   Notice any sensations - warmth, coolness, tension, relaxation, or perhaps no particular sensation.")
            print(f"   There's no need to change anything, just notice with gentle curiosity.")
            time.sleep(segment_time)
            print()
        
        print("🌸 Now sense your body as a whole, from the top of your head to the tips of your toes.")
        print("   Rest in this complete awareness of your body.")
    
    def _loving_kindness_meditation(self, duration: int):
        """Guided loving-kindness meditation"""
        phases = [
            ("yourself", "May I be happy and healthy. May I be at peace. May I be free from suffering."),
            ("a loved one", "May you be happy and healthy. May you be at peace. May you be free from suffering."),
            ("a neutral person", "May you be happy and healthy. May you be at peace. May you be free from suffering."),
            ("someone difficult", "May you be happy and healthy. May you be at peace. May you be free from suffering."),
            ("all beings", "May all beings be happy and healthy. May all beings be at peace. May all beings be free from suffering.")
        ]
        
        segment_time = (duration * 60) // len(phases)
        
        for target, phrases in phases:
            print(f"💝 Now bring to mind {target}.")
            if target == "yourself":
                print("   Place your hand on your heart if that feels comfortable.")
            elif target != "all beings":
                print("   Picture this person clearly in your mind.")
            
            print(f"   Repeat these phrases with genuine intention:")
            for phrase in phrases.split('. '):
                if phrase.strip():
                    print(f"   {phrase.strip()}.")
            
            time.sleep(segment_time)
            print()
    
    def quick_mindfulness_exercises(self):
        """Short mindfulness exercises for daily life"""
        print("⚡ Quick Mindfulness Exercises")
        print("=" * 40)
        print("These brief exercises can be done anywhere, anytime.")
        print()
        
        print("Choose an exercise:")
        exercises = list(self.mindfulness_exercises.items())
        
        for i, (key, name) in enumerate(exercises, 1):
            print(f"{i}. {name}")
        
        print()
        choice = input("Choose exercise (1-7): ").strip()
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(exercises):
                exercise_key = exercises[choice_idx][0]
                self._perform_mindfulness_exercise(exercise_key)
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid choice.")
    
    def _perform_mindfulness_exercise(self, exercise: str):
        """Perform specific mindfulness exercise"""
        if exercise == "five_senses":
            self._five_senses_exercise()
        elif exercise == "mindful_eating":
            self._mindful_eating_exercise()
        elif exercise == "mindful_listening":
            self._mindful_listening_exercise()
        elif exercise == "breath_awareness":
            self._breath_awareness_exercise()
        elif exercise == "body_awareness":
            self._body_awareness_exercise()
        elif exercise == "thought_watching":
            self._thought_watching_exercise()
        elif exercise == "emotion_surfing":
            self._emotion_surfing_exercise()
    
    def _five_senses_exercise(self):
        """5-4-3-2-1 grounding exercise"""
        print("\n👁️ 5-4-3-2-1 Sensory Grounding")
        print("=" * 40)
        print("This exercise grounds you in the present moment using your senses.")
        print()
        
        senses = [
            (5, "things you can SEE", "👁️"),
            (4, "things you can TOUCH or FEEL", "✋"),
            (3, "things you can HEAR", "👂"),
            (2, "things you can SMELL", "👃"),
            (1, "thing you can TASTE", "👅")
        ]
        
        for count, sense, emoji in senses:
            print(f"{emoji} Name {count} {sense}:")
            for i in range(count):
                thing = input(f"   {i+1}. ").strip()
                if thing:
                    print(f"      Good, you noticed: {thing}")
            print()
        
        print("✨ Excellent! You've grounded yourself in the present moment.")
    
    def meditation_progress_tracker(self):
        """Track meditation practice progress"""
        data = self._load_meditation_data()
        sessions = data.get('sessions', [])
        
        if not sessions:
            print("📊 Meditation Progress")
            print("=" * 30)
            print("No meditation sessions recorded yet.")
            print("Start practicing to track your progress!")
            return
        
        print("📊 Meditation Progress")
        print("=" * 30)
        
        # Recent sessions
        recent_sessions = sessions[-10:]
        print("Recent sessions:")
        
        for session in recent_sessions:
            date = datetime.fromisoformat(session['timestamp']).strftime("%m-%d")
            meditation_type = session['type']
            duration = session['duration']
            rating = session.get('rating', 'N/A')
            print(f"   {date}: {meditation_type} ({duration}min) - Rating: {rating}/5")
        
        print()
        
        # Statistics
        total_sessions = len(sessions)
        total_minutes = sum(session['duration'] for session in sessions)
        
        # Last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_sessions = [
            s for s in sessions 
            if datetime.fromisoformat(s['timestamp']) >= thirty_days_ago
        ]
        
        print(f"📈 Statistics:")
        print(f"   Total sessions: {total_sessions}")
        print(f"   Total meditation time: {total_minutes} minutes ({total_minutes//60}h {total_minutes%60}m)")
        print(f"   Sessions last 30 days: {len(recent_sessions)}")
        
        if recent_sessions:
            avg_duration = sum(s['duration'] for s in recent_sessions) / len(recent_sessions)
            print(f"   Average session length: {avg_duration:.1f} minutes")
        
        # Most practiced types
        type_counts = {}
        for session in sessions:
            session_type = session['type']
            type_counts[session_type] = type_counts.get(session_type, 0) + 1
        
        if type_counts:
            print(f"\n🧘‍♀️ Most practiced:")
            sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
            for meditation_type, count in sorted_types[:3]:
                print(f"   {meditation_type}: {count} sessions")
        
        # Streak calculation
        streak = self._calculate_meditation_streak(sessions)
        if streak > 0:
            print(f"\n🔥 Current streak: {streak} days")
        
        # Ratings analysis
        rated_sessions = [s for s in sessions if s.get('rating')]
        if rated_sessions:
            avg_rating = sum(s['rating'] for s in rated_sessions) / len(rated_sessions)
            print(f"\n⭐ Average session rating: {avg_rating:.1f}/5")
    
    def _get_meditation_recommendation(self, feeling: str, duration: int, experience: str):
        """Get meditation recommendation based on inputs"""
        recommendations = {
            "stressed": ["body_scan", "breathing", "mindfulness"],
            "anxious": ["breathing", "body_scan", "mindfulness"],
            "sad": ["loving_kindness", "mindfulness", "visualization"],
            "angry": ["breathing", "noting", "walking"],
            "restless": ["walking", "noting", "body_scan"],
            "tired": ["body_scan", "visualization", "mindfulness"],
            "neutral": ["mindfulness", "breathing", "loving_kindness"],
            "curious": ["noting", "mindfulness", "visualization"]
        }
        
        # Adjust for experience level
        if experience == "beginner":
            beginner_friendly = ["breathing", "mindfulness", "body_scan"]
            possible = recommendations.get(feeling, ["mindfulness"])
            return next((t for t in possible if t in beginner_friendly), "breathing")
        
        return random.choice(recommendations.get(feeling, ["mindfulness"]))
    
    def _post_meditation_reflection(self, meditation_type: str, duration: int):
        """Post-meditation reflection and logging"""
        print("💭 How was your meditation?")
        
        # Rating
        rating = input("Rate your session (1-5, 5=excellent): ").strip()
        
        try:
            rating = max(1, min(5, int(rating)))
        except ValueError:
            rating = None
        
        # Reflection
        reflection = input("Any insights or observations? (optional): ").strip()
        
        # Challenges
        print("\nDid you experience any challenges?")
        for i, challenge in enumerate(self.meditation_challenges, 1):
            print(f"{i}. {challenge}")
        
        challenge_input = input("Choose challenges (e.g., 1,3,5) or press Enter: ").strip()
        challenges = []
        
        if challenge_input:
            try:
                selected = [int(x.strip()) for x in challenge_input.split(',')]
                challenges = [self.meditation_challenges[i-1] for i in selected 
                            if 1 <= i <= len(self.meditation_challenges)]
            except ValueError:
                pass
        
        # Save session
        self._save_meditation_session(meditation_type, duration, rating, reflection, challenges)
        
        if rating:
            print(f"\n✨ Thank you! You rated this session {rating}/5")
        
        if challenges:
            print("\n💡 Tips for your challenges:")
            for challenge in challenges:
                tip = self._get_challenge_tip(challenge)
                print(f"   • {challenge}: {tip}")
        
        print("\n🌟 Great work on your meditation practice!")
    
    def _get_challenge_tip(self, challenge: str) -> str:
        """Get tip for meditation challenge"""
        tips = {
            "Restlessness or fidgeting": "Try walking meditation or shorter sessions",
            "Racing thoughts": "Use noting technique - label thoughts as 'thinking' and return to breath",
            "Falling asleep": "Sit upright, open eyes slightly, or try earlier in the day",
            "Physical discomfort": "Adjust position as needed - comfort supports concentration",
            "Emotional overwhelm": "Be gentle with yourself - strong emotions are normal in meditation",
            "Boredom or impatience": "Notice boredom with curiosity - it's just another experience",
            "Self-judgment": "Remember: there's no 'perfect' meditation - be kind to yourself",
            "Difficulty concentrating": "Concentration improves with practice - start with shorter sessions"
        }
        return tips.get(challenge, "Be patient and gentle with yourself")
    
    def _calculate_meditation_streak(self, sessions: List[Dict]) -> int:
        """Calculate current meditation streak"""
        if not sessions:
            return 0
        
        # Sort sessions by date
        sorted_sessions = sorted(sessions, key=lambda x: x['timestamp'], reverse=True)
        
        streak = 0
        current_date = datetime.now().date()
        
        # Check each day going backwards
        for i in range(30):  # Check last 30 days
            check_date = current_date - timedelta(days=i)
            
            # Check if there's a session on this date
            has_session = any(
                datetime.fromisoformat(s['timestamp']).date() == check_date
                for s in sorted_sessions
            )
            
            if has_session:
                if i == 0 or streak == i:  # Continuous streak
                    streak += 1
                else:
                    break
            elif i == 0:  # No session today
                break
        
        return streak
    
    def _save_meditation_session(self, meditation_type: str, duration: int, 
                                rating: Optional[int], reflection: str, challenges: List[str]):
        """Save meditation session data"""
        data = self._load_meditation_data()
        
        session = {
            "timestamp": datetime.now().isoformat(),
            "type": meditation_type,
            "duration": duration,
            "rating": rating,
            "reflection": reflection,
            "challenges": challenges
        }
        
        data.setdefault('sessions', []).append(session)
        self._save_meditation_data(data)
    
    def _load_meditation_data(self) -> Dict:
        """Load meditation data"""
        if not os.path.exists(MEDITATION_FILE):
            return {}
        
        try:
            with open(MEDITATION_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_meditation_data(self, data: Dict):
        """Save meditation data"""
        try:
            with open(MEDITATION_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save meditation data: {e}")


def enhanced_meditation_command(action: str = "recommend", **kwargs):
    """Main enhanced meditation command interface"""
    meditation = EnhancedMeditation()
    
    if action == "recommend":
        meditation.meditation_recommendation()
    elif action == "guided":
        meditation_type = kwargs.get('type', 'mindfulness')
        duration = kwargs.get('duration', 10)
        meditation.guided_meditation(meditation_type, duration)
    elif action == "quick":
        meditation.quick_mindfulness_exercises()
    elif action == "progress":
        meditation.meditation_progress_tracker()
    else:
        print(f"Unknown meditation action: {action}")
        print("Available actions: recommend, guided, quick, progress")
