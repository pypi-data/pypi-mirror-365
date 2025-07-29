"""
Coping skills, relaxation, and stress reduction module for om
Evidence-based techniques for managing stress and building resilience
"""

import time
import random
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

COPING_FILE = os.path.expanduser("~/.om_coping.json")

class CopingSkillsToolkit:
    def __init__(self):
        self.stress_levels = {
            1: "Very low stress",
            2: "Low stress", 
            3: "Mild stress",
            4: "Moderate stress",
            5: "High stress",
            6: "Very high stress",
            7: "Severe stress"
        }
        
        self.coping_techniques = {
            "grounding": {
                "name": "5-4-3-2-1 Grounding",
                "description": "Sensory grounding technique to anchor you in the present",
                "best_for": ["anxiety", "panic", "overwhelm"]
            },
            "progressive_relaxation": {
                "name": "Progressive Muscle Relaxation",
                "description": "Systematic tension and release of muscle groups",
                "best_for": ["physical tension", "stress", "insomnia"]
            },
            "box_breathing": {
                "name": "Box Breathing",
                "description": "4-4-4-4 breathing pattern for calm",
                "best_for": ["anxiety", "stress", "focus"]
            },
            "cognitive_reframe": {
                "name": "Cognitive Reframing",
                "description": "Challenge and reframe negative thoughts",
                "best_for": ["negative thinking", "worry", "catastrophizing"]
            },
            "safe_place": {
                "name": "Safe Place Visualization",
                "description": "Mental imagery of a calm, safe environment",
                "best_for": ["trauma", "anxiety", "stress"]
            },
            "self_compassion": {
                "name": "Self-Compassion Break",
                "description": "Mindful self-kindness practice",
                "best_for": ["self-criticism", "shame", "difficult emotions"]
            }
        }
    
    def assess_stress_level(self):
        """Interactive stress level assessment"""
        print("🌡️ Stress Level Check-In")
        print("=" * 40)
        print("Let's assess your current stress level to recommend appropriate coping skills.")
        print()
        
        # Physical symptoms
        print("Physical symptoms (check any you're experiencing):")
        physical_symptoms = [
            "Muscle tension or pain",
            "Headaches",
            "Rapid heartbeat",
            "Shallow breathing",
            "Fatigue",
            "Digestive issues",
            "Sleep problems"
        ]
        
        physical_score = 0
        for i, symptom in enumerate(physical_symptoms, 1):
            response = input(f"{i}. {symptom}? (y/n): ").strip().lower()
            if response == 'y':
                physical_score += 1
        
        print()
        
        # Emotional symptoms
        print("Emotional symptoms (check any you're experiencing):")
        emotional_symptoms = [
            "Feeling overwhelmed",
            "Irritability or anger",
            "Anxiety or worry",
            "Sadness or depression",
            "Restlessness",
            "Difficulty concentrating",
            "Feeling out of control"
        ]
        
        emotional_score = 0
        for i, symptom in enumerate(emotional_symptoms, 1):
            response = input(f"{i}. {symptom}? (y/n): ").strip().lower()
            if response == 'y':
                emotional_score += 1
        
        # Calculate overall stress level
        total_score = physical_score + emotional_score
        stress_level = min(7, max(1, (total_score // 2) + 1))
        
        print(f"\n📊 Assessment Results:")
        print(f"Physical symptoms: {physical_score}/7")
        print(f"Emotional symptoms: {emotional_score}/7")
        print(f"Overall stress level: {stress_level}/7 - {self.stress_levels[stress_level]}")
        
        # Save assessment
        self._save_stress_assessment(stress_level, physical_score, emotional_score)
        
        # Recommend techniques
        self._recommend_techniques(stress_level)
        
        return stress_level
    
    def grounding_technique(self):
        """5-4-3-2-1 grounding technique"""
        print("🌍 5-4-3-2-1 Grounding Technique")
        print("=" * 40)
        print("This technique helps anchor you in the present moment using your senses.")
        print("Take your time with each step.\n")
        
        input("Press Enter when you're ready to begin...")
        print()
        
        # 5 things you can see
        print("👀 Look around and name 5 things you can SEE:")
        for i in range(1, 6):
            thing = input(f"  {i}. I can see: ").strip()
            if thing:
                print(f"     Good, you noticed: {thing}")
        
        print()
        
        # 4 things you can touch
        print("✋ Name 4 things you can TOUCH or FEEL:")
        for i in range(1, 5):
            thing = input(f"  {i}. I can feel: ").strip()
            if thing:
                print(f"     Good, you're aware of: {thing}")
        
        print()
        
        # 3 things you can hear
        print("👂 Listen and name 3 things you can HEAR:")
        for i in range(1, 4):
            thing = input(f"  {i}. I can hear: ").strip()
            if thing:
                print(f"     Good, you noticed: {thing}")
        
        print()
        
        # 2 things you can smell
        print("👃 Name 2 things you can SMELL:")
        for i in range(1, 3):
            thing = input(f"  {i}. I can smell: ").strip()
            if thing:
                print(f"     Good, you're aware of: {thing}")
        
        print()
        
        # 1 thing you can taste
        print("👅 Name 1 thing you can TASTE:")
        thing = input("  1. I can taste: ").strip()
        if thing:
            print(f"     Good, you noticed: {thing}")
        
        print("\n✨ Excellent work! You've successfully grounded yourself in the present moment.")
        print("Notice how you feel now compared to when you started.")
        
        self._log_technique_use("grounding")
    
    def progressive_relaxation(self):
        """Progressive muscle relaxation technique"""
        print("💪 Progressive Muscle Relaxation")
        print("=" * 40)
        print("This technique involves tensing and then relaxing different muscle groups.")
        print("Hold tension for 5 seconds, then release and notice the relaxation.")
        print()
        
        input("Find a comfortable position and press Enter to begin...")
        print()
        
        muscle_groups = [
            ("hands and forearms", "Make fists with both hands"),
            ("upper arms", "Bend your arms and tense your biceps"),
            ("shoulders", "Raise your shoulders toward your ears"),
            ("face", "Scrunch your facial muscles together"),
            ("chest and back", "Take a deep breath and hold it"),
            ("stomach", "Tense your abdominal muscles"),
            ("thighs", "Tense your thigh muscles"),
            ("calves", "Point your toes upward"),
            ("feet", "Curl your toes downward")
        ]
        
        for muscle_group, instruction in muscle_groups:
            print(f"🎯 {muscle_group.title()}:")
            print(f"   {instruction}")
            input("   Press Enter when you're tensing these muscles...")
            
            print("   Hold the tension... 5")
            time.sleep(1)
            print("   4")
            time.sleep(1)
            print("   3")
            time.sleep(1)
            print("   2")
            time.sleep(1)
            print("   1")
            time.sleep(1)
            print("   Now RELEASE and relax...")
            time.sleep(3)
            print("   Notice the difference between tension and relaxation.")
            print()
        
        print("✨ Wonderful! You've completed the full body relaxation.")
        print("Take a moment to notice how your body feels now.")
        print("This relaxed state is always available to you.")
        
        self._log_technique_use("progressive_relaxation")
    
    def cognitive_reframing(self):
        """Cognitive reframing exercise"""
        print("🧠 Cognitive Reframing Exercise")
        print("=" * 40)
        print("This technique helps you challenge negative thoughts and find more balanced perspectives.")
        print()
        
        # Identify the negative thought
        negative_thought = input("What negative thought or worry is bothering you right now?\n> ").strip()
        
        if not negative_thought:
            print("It's okay if you can't think of something specific right now.")
            return
        
        print(f"\nYour thought: \"{negative_thought}\"")
        print()
        
        # Challenge questions
        print("Let's examine this thought with some questions:")
        print()
        
        questions = [
            "Is this thought 100% true?",
            "What evidence supports this thought?",
            "What evidence contradicts this thought?",
            "What would you tell a friend having this thought?",
            "What's the worst that could realistically happen?",
            "What's the best that could happen?",
            "What's most likely to happen?",
            "How will this matter in 5 years?"
        ]
        
        responses = []
        for question in questions:
            print(f"❓ {question}")
            response = input("   Your answer: ").strip()
            responses.append(response)
            print()
        
        # Generate balanced thought
        print("Based on your responses, try to create a more balanced thought:")
        balanced_thought = input("More balanced perspective: ").strip()
        
        if balanced_thought:
            print(f"\n🌟 Great work! You've reframed:")
            print(f"   From: \"{negative_thought}\"")
            print(f"   To: \"{balanced_thought}\"")
            print("\nRemember this balanced perspective when the negative thought returns.")
        
        self._log_technique_use("cognitive_reframe", {
            "original_thought": negative_thought,
            "balanced_thought": balanced_thought
        })
    
    def safe_place_visualization(self):
        """Safe place visualization technique"""
        print("🏞️ Safe Place Visualization")
        print("=" * 40)
        print("This technique uses your imagination to create a sense of safety and calm.")
        print()
        
        input("Find a comfortable position, close your eyes if you'd like, and press Enter...")
        print()
        
        print("🌅 Let's create your safe place...")
        print("This can be real or imaginary, indoors or outdoors.")
        print()
        
        # Guide through visualization
        prompts = [
            "Where is your safe place? Describe the location...",
            "What do you see around you? Notice the colors, shapes, lighting...",
            "What sounds do you hear in this place?",
            "What can you smell or taste here?",
            "What textures can you feel? The ground, air, objects around you...",
            "What makes this place feel safe and peaceful for you?",
            "How does your body feel in this safe place?",
            "What emotions arise when you're here?"
        ]
        
        responses = []
        for prompt in prompts:
            print(f"💭 {prompt}")
            response = input("   ").strip()
            responses.append(response)
            print("   Take a moment to really experience this...")
            time.sleep(2)
            print()
        
        print("✨ Beautiful! You've created a powerful resource.")
        print("You can return to this safe place anytime you need comfort or calm.")
        print("The more you practice this visualization, the more vivid and helpful it becomes.")
        
        # Offer to save the safe place
        save = input("\nWould you like to save this safe place description? (y/n): ").strip().lower()
        if save == 'y':
            self._save_safe_place(responses)
        
        self._log_technique_use("safe_place")
    
    def self_compassion_break(self):
        """Self-compassion break technique"""
        print("💝 Self-Compassion Break")
        print("=" * 40)
        print("This practice helps you respond to difficult moments with kindness toward yourself.")
        print()
        
        # Identify the difficulty
        difficulty = input("What's causing you pain or difficulty right now?\n> ").strip()
        
        if not difficulty:
            difficulty = "this difficult moment"
        
        print(f"\nAcknowledging: {difficulty}")
        print()
        
        input("Place your hand on your heart or another soothing location and press Enter...")
        print()
        
        # Three components of self-compassion
        print("🤲 Step 1: Mindfulness")
        print("Acknowledge your pain without judgment:")
        print(f"   \"This is a moment of suffering.\"")
        print(f"   \"This is difficult right now.\"")
        input("\nTake a moment to feel this acknowledgment... Press Enter to continue.")
        print()
        
        print("🌍 Step 2: Common Humanity")
        print("Remember you're not alone in experiencing difficulty:")
        print("   \"Suffering is part of life.\"")
        print("   \"I'm not alone in feeling this way.\"")
        print("   \"Many people have felt what I'm feeling.\"")
        input("\nLet this sense of connection settle in... Press Enter to continue.")
        print()
        
        print("💖 Step 3: Self-Kindness")
        print("Offer yourself the same kindness you'd give a good friend:")
        print("   \"May I be kind to myself.\"")
        print("   \"May I give myself the compassion I need.\"")
        print("   \"May I be strong and patient with myself.\"")
        input("\nFeel this kindness flowing toward yourself... Press Enter to continue.")
        print()
        
        print("✨ You've just practiced self-compassion!")
        print("This loving-kindness toward yourself is always available.")
        print("Remember: You deserve the same compassion you'd give others.")
        
        self._log_technique_use("self_compassion", {"difficulty": difficulty})
    
    def quick_stress_relief(self):
        """Quick stress relief techniques for immediate use"""
        techniques = [
            {
                "name": "4-7-8 Breathing",
                "steps": [
                    "Exhale completely",
                    "Inhale through nose for 4 counts",
                    "Hold breath for 7 counts", 
                    "Exhale through mouth for 8 counts",
                    "Repeat 3-4 times"
                ]
            },
            {
                "name": "Cold Water Reset",
                "steps": [
                    "Splash cold water on your face",
                    "Hold cold water in your hands",
                    "Place cold, wet hands on your wrists",
                    "Take 5 deep breaths",
                    "Notice the immediate calming effect"
                ]
            },
            {
                "name": "Butterfly Hug",
                "steps": [
                    "Cross your arms over your chest",
                    "Place hands on opposite shoulders",
                    "Gently pat alternating sides",
                    "Continue for 30 seconds",
                    "Breathe slowly and deeply"
                ]
            },
            {
                "name": "Name It to Tame It",
                "steps": [
                    "Notice what you're feeling",
                    "Name the emotion out loud",
                    "Say: 'I notice I'm feeling [emotion]'",
                    "Take 3 deep breaths",
                    "Remind yourself: 'This feeling will pass'"
                ]
            }
        ]
        
        technique = random.choice(techniques)
        
        print(f"⚡ Quick Relief: {technique['name']}")
        print("=" * 40)
        print("Here's a quick technique you can use right now:")
        print()
        
        for i, step in enumerate(technique['steps'], 1):
            print(f"{i}. {step}")
        
        print()
        input("Try this technique now, then press Enter when finished...")
        
        # Rate effectiveness
        print("\nHow helpful was this technique?")
        rating = input("Rate 1-5 (1=not helpful, 5=very helpful): ").strip()
        
        try:
            rating = int(rating)
            if 1 <= rating <= 5:
                print(f"Thanks for the feedback! You rated it {rating}/5")
                self._log_technique_use("quick_relief", {
                    "technique": technique['name'],
                    "rating": rating
                })
        except ValueError:
            pass
    
    def coping_skills_menu(self):
        """Interactive menu for coping skills"""
        print("🛠️ Coping Skills Toolkit")
        print("=" * 40)
        print("Choose a technique based on what you need right now:")
        print()
        
        options = [
            ("1", "Assess my stress level", self.assess_stress_level),
            ("2", "5-4-3-2-1 Grounding (for anxiety/panic)", self.grounding_technique),
            ("3", "Progressive Muscle Relaxation (for tension)", self.progressive_relaxation),
            ("4", "Cognitive Reframing (for negative thoughts)", self.cognitive_reframing),
            ("5", "Safe Place Visualization (for trauma/stress)", self.safe_place_visualization),
            ("6", "Self-Compassion Break (for self-criticism)", self.self_compassion_break),
            ("7", "Quick Stress Relief (immediate help)", self.quick_stress_relief),
            ("8", "View my coping history", self.show_coping_history)
        ]
        
        for option, description, _ in options:
            print(f"{option}. {description}")
        
        print()
        choice = input("Choose an option (1-8): ").strip()
        
        for option, _, function in options:
            if choice == option:
                print()
                function()
                return
        
        print("Invalid choice. Please try again.")
    
    def show_coping_history(self):
        """Show history of coping technique usage"""
        data = self._load_coping_data()
        
        if not data.get('technique_uses'):
            print("No coping technique history found.")
            print("Start using techniques to track your progress!")
            return
        
        print("📈 Your Coping Skills History")
        print("=" * 40)
        
        # Recent usage
        recent_uses = data['technique_uses'][-10:]
        print("Recent technique usage:")
        
        for use in recent_uses:
            date = datetime.fromisoformat(use['timestamp']).strftime("%m-%d %H:%M")
            technique_name = self.coping_techniques.get(use['technique'], {}).get('name', use['technique'])
            print(f"  {date}: {technique_name}")
        
        print()
        
        # Usage statistics
        technique_counts = {}
        for use in data['technique_uses']:
            technique = use['technique']
            technique_counts[technique] = technique_counts.get(technique, 0) + 1
        
        print("Most used techniques:")
        sorted_techniques = sorted(technique_counts.items(), key=lambda x: x[1], reverse=True)
        
        for technique, count in sorted_techniques[:5]:
            technique_name = self.coping_techniques.get(technique, {}).get('name', technique)
            print(f"  {technique_name}: {count} times")
        
        # Stress level trends
        if data.get('stress_assessments'):
            recent_assessments = data['stress_assessments'][-5:]
            print(f"\nRecent stress levels:")
            
            for assessment in recent_assessments:
                date = datetime.fromisoformat(assessment['timestamp']).strftime("%m-%d")
                level = assessment['stress_level']
                print(f"  {date}: {level}/7 - {self.stress_levels[level]}")
    
    def _recommend_techniques(self, stress_level: int):
        """Recommend techniques based on stress level"""
        print(f"\n💡 Recommended techniques for your stress level:")
        
        if stress_level <= 2:
            recommendations = ["self_compassion", "safe_place"]
            print("   • Focus on maintenance and self-care")
        elif stress_level <= 4:
            recommendations = ["box_breathing", "cognitive_reframe", "progressive_relaxation"]
            print("   • Use preventive techniques to manage stress")
        else:
            recommendations = ["grounding", "box_breathing", "progressive_relaxation"]
            print("   • Use immediate relief techniques")
        
        print()
        for technique in recommendations:
            info = self.coping_techniques[technique]
            print(f"   🎯 {info['name']}: {info['description']}")
    
    def _save_stress_assessment(self, stress_level: int, physical_score: int, emotional_score: int):
        """Save stress assessment data"""
        data = self._load_coping_data()
        
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "stress_level": stress_level,
            "physical_score": physical_score,
            "emotional_score": emotional_score
        }
        
        data.setdefault('stress_assessments', []).append(assessment)
        self._save_coping_data(data)
    
    def _log_technique_use(self, technique: str, details: Dict = None):
        """Log usage of a coping technique"""
        data = self._load_coping_data()
        
        use_log = {
            "timestamp": datetime.now().isoformat(),
            "technique": technique,
            "details": details or {}
        }
        
        data.setdefault('technique_uses', []).append(use_log)
        self._save_coping_data(data)
    
    def _save_safe_place(self, responses: List[str]):
        """Save safe place visualization details"""
        data = self._load_coping_data()
        
        safe_place = {
            "timestamp": datetime.now().isoformat(),
            "description": responses
        }
        
        data.setdefault('safe_places', []).append(safe_place)
        self._save_coping_data(data)
        print("✅ Safe place saved! You can revisit this description anytime.")
    
    def _load_coping_data(self) -> Dict:
        """Load coping skills data"""
        if not os.path.exists(COPING_FILE):
            return {}
        
        try:
            with open(COPING_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_coping_data(self, data: Dict):
        """Save coping skills data"""
        try:
            with open(COPING_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save coping data: {e}")


def coping_command(action: str = "menu", **kwargs):
    """Main coping skills command interface"""
    toolkit = CopingSkillsToolkit()
    
    if action == "menu":
        toolkit.coping_skills_menu()
    elif action == "assess":
        toolkit.assess_stress_level()
    elif action == "grounding":
        toolkit.grounding_technique()
    elif action == "relax":
        toolkit.progressive_relaxation()
    elif action == "reframe":
        toolkit.cognitive_reframing()
    elif action == "safe":
        toolkit.safe_place_visualization()
    elif action == "compassion":
        toolkit.self_compassion_break()
    elif action == "quick":
        toolkit.quick_stress_relief()
    elif action == "history":
        toolkit.show_coping_history()
    else:
        print(f"Unknown coping action: {action}")
        print("Available actions: menu, assess, grounding, relax, reframe, safe, compassion, quick, history")
