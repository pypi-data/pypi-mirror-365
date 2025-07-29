"""
Rescue Sessions module for om - International Crisis Support Integration
Quick bite-sized support for overwhelming feelings with global crisis resources
"""

import random
import time
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

# Import international crisis support
try:
    from .international_crisis import InternationalCrisisSupport
except ImportError:
    # Fallback if running standalone
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from international_crisis import InternationalCrisisSupport

RESCUE_SESSIONS_FILE = os.path.expanduser("~/.om_rescue_sessions.json")

class RescueSessions:
    def __init__(self):
        self.crisis_support = InternationalCrisisSupport()
        self.sessions = {
            "overwhelmed": {
                "title": "Feeling Overwhelmed",
                "description": "Quick techniques to regain control when everything feels too much",
                "duration": "3-5 minutes",
                "techniques": [
                    {
                        "name": "5-4-3-2-1 Grounding",
                        "steps": [
                            "Take a deep breath and look around you",
                            "Name 5 things you can see",
                            "Name 4 things you can touch",
                            "Name 3 things you can hear", 
                            "Name 2 things you can smell",
                            "Name 1 thing you can taste",
                            "Notice how you feel now compared to when you started"
                        ]
                    },
                    {
                        "name": "Brain Dump",
                        "steps": [
                            "Get a piece of paper or open a notes app",
                            "Set a timer for 2 minutes",
                            "Write down everything on your mind - don't edit or organize",
                            "When the timer goes off, stop writing",
                            "Look at your list and circle the top 3 most important items",
                            "Focus only on those 3 things for now"
                        ]
                    },
                    {
                        "name": "One Thing at a Time",
                        "steps": [
                            "Say to yourself: 'Right now, I only need to focus on one thing'",
                            "Choose the smallest, most manageable task in front of you",
                            "Do only that one thing - ignore everything else",
                            "When finished, acknowledge your accomplishment",
                            "Then choose the next single thing to focus on"
                        ]
                    }
                ]
            },
            "anxious": {
                "title": "Feeling Anxious",
                "description": "Calm your nervous system when anxiety strikes",
                "duration": "3-7 minutes",
                "techniques": [
                    {
                        "name": "4-7-8 Breathing",
                        "steps": [
                            "Sit comfortably and exhale completely",
                            "Breathe in through your nose for 4 counts",
                            "Hold your breath for 7 counts",
                            "Exhale through your mouth for 8 counts",
                            "Repeat this cycle 3-4 times",
                            "Return to normal breathing and notice the calm"
                        ]
                    },
                    {
                        "name": "Anxiety Reality Check",
                        "steps": [
                            "Ask yourself: 'What am I worried about right now?'",
                            "Ask: 'Is this worry about something happening right now or in the future?'",
                            "Ask: 'What evidence do I have that this will actually happen?'",
                            "Ask: 'Even if it did happen, how would I cope?'",
                            "Remind yourself: 'I can handle whatever comes my way'",
                            "Focus on what you can control in this moment"
                        ]
                    },
                    {
                        "name": "Progressive Muscle Release",
                        "steps": [
                            "Start with your toes - tense them for 5 seconds, then release",
                            "Move to your calves - tense and release",
                            "Continue with thighs, stomach, hands, arms, shoulders",
                            "Finally, scrunch your face muscles, then release",
                            "Take a moment to notice the relaxation in your body",
                            "Breathe deeply and enjoy this calm feeling"
                        ]
                    }
                ]
            },
            "angry": {
                "title": "Feeling Angry",
                "description": "Cool down and respond thoughtfully instead of reacting",
                "duration": "2-5 minutes",
                "techniques": [
                    {
                        "name": "STOP Technique",
                        "steps": [
                            "S - Stop what you're doing",
                            "T - Take a deep breath (or several)",
                            "O - Observe what you're feeling and thinking",
                            "P - Proceed with intention, not reaction",
                            "Ask yourself: 'What response would I be proud of later?'",
                            "Choose your next action based on your values, not your anger"
                        ]
                    },
                    {
                        "name": "Anger Release",
                        "steps": [
                            "Find a private space where you can move freely",
                            "Clench your fists tightly for 10 seconds, then release",
                            "Do 10 jumping jacks or push-ups to release physical energy",
                            "Take 5 deep breaths, making your exhales longer than inhales",
                            "Say out loud: 'I acknowledge my anger and I choose how to respond'",
                            "Think of one constructive action you can take"
                        ]
                    },
                    {
                        "name": "Perspective Shift",
                        "steps": [
                            "Ask yourself: 'Will this matter in 5 years?'",
                            "Consider: 'What might the other person be going through?'",
                            "Think: 'What would someone I respect do in this situation?'",
                            "Remember a time when you handled anger well",
                            "Focus on what you can learn from this situation",
                            "Choose a response that aligns with who you want to be"
                        ]
                    }
                ]
            },
            "sad": {
                "title": "Feeling Sad",
                "description": "Gentle support and comfort for difficult emotions",
                "duration": "3-8 minutes",
                "techniques": [
                    {
                        "name": "Self-Compassion Break",
                        "steps": [
                            "Place your hand on your heart or another comforting place",
                            "Say to yourself: 'This is a moment of suffering'",
                            "Say: 'Suffering is part of life - I'm not alone in this'",
                            "Say: 'May I be kind to myself in this moment'",
                            "Take a few deep breaths and feel the warmth of self-compassion",
                            "Ask: 'What do I need right now to take care of myself?'"
                        ]
                    },
                    {
                        "name": "Gentle Movement",
                        "steps": [
                            "Stand up slowly and stretch your arms above your head",
                            "Roll your shoulders back and forth gently",
                            "Take a slow walk, even if just around the room",
                            "Notice how movement affects your mood",
                            "Do any gentle movement that feels good to your body",
                            "End with a few deep breaths and thank your body"
                        ]
                    },
                    {
                        "name": "Gratitude in Sadness",
                        "steps": [
                            "Acknowledge that it's okay to feel sad",
                            "Think of one small thing you're grateful for today",
                            "Think of one person who cares about you",
                            "Remember one good memory from this week",
                            "Notice one thing in your environment that brings you peace",
                            "Hold these positive thoughts gently alongside your sadness"
                        ]
                    }
                ]
            },
            "restless": {
                "title": "Feeling Restless",
                "description": "Channel restless energy into calm focus",
                "duration": "2-6 minutes",
                "techniques": [
                    {
                        "name": "Energy Release",
                        "steps": [
                            "Do 20 jumping jacks or run in place for 30 seconds",
                            "Shake out your hands and arms vigorously",
                            "Roll your head and shoulders",
                            "Take 5 deep breaths, focusing on the exhale",
                            "Notice how your body feels after releasing the energy",
                            "Sit quietly for a moment and enjoy the calm"
                        ]
                    },
                    {
                        "name": "Mindful Walking",
                        "steps": [
                            "Find a space where you can walk back and forth",
                            "Walk very slowly, focusing on each step",
                            "Feel your feet touching the ground",
                            "Notice the movement of your legs and arms",
                            "If your mind wanders, gently return focus to walking",
                            "Continue for 2-3 minutes, then stand still and breathe"
                        ]
                    },
                    {
                        "name": "Focus Anchor",
                        "steps": [
                            "Choose one object in your environment to focus on",
                            "Look at it closely - notice its color, texture, shape",
                            "Describe it to yourself in detail",
                            "When your mind wanders, gently return to the object",
                            "Continue for 2-3 minutes",
                            "Notice how focused attention calms restlessness"
                        ]
                    }
                ]
            },
            "lonely": {
                "title": "Feeling Lonely",
                "description": "Connect with yourself and others when feeling isolated",
                "duration": "3-7 minutes",
                "techniques": [
                    {
                        "name": "Self-Connection",
                        "steps": [
                            "Place both hands on your heart",
                            "Say to yourself: 'I am here with me'",
                            "Take 5 deep breaths, feeling your own presence",
                            "Think of three qualities you appreciate about yourself",
                            "Remember that you are worthy of love and connection",
                            "Commit to one small act of self-care today"
                        ]
                    },
                    {
                        "name": "Reaching Out",
                        "steps": [
                            "Think of three people who care about you",
                            "Choose one person you could reach out to",
                            "Send them a simple message: 'Thinking of you' or 'Hope you're well'",
                            "If messaging feels too hard, just think loving thoughts about them",
                            "Remember that connection doesn't require big gestures",
                            "Plan one small social activity for this week"
                        ]
                    },
                    {
                        "name": "Universal Connection",
                        "steps": [
                            "Sit quietly and think about all the people in the world",
                            "Remember that many people feel lonely sometimes - you're not alone in this",
                            "Send kind thoughts to others who might be feeling lonely right now",
                            "Think about the ways you're connected to others (family, friends, community)",
                            "Feel your connection to all living beings",
                            "Rest in this sense of universal connection"
                        ]
                    }
                ]
            }
        }
    
    def show_rescue_menu(self):
        """Show the main rescue menu with crisis support"""
        print("🆘 RESCUE SESSIONS - IMMEDIATE SUPPORT")
        print("=" * 45)
        
        # Check for crisis indicators first
        print("\n🚨 CRISIS SUPPORT:")
        print("1. 🆘 Crisis Resources (Emergency help)")
        print("2. 🌍 International Crisis Lines")
        print("3. ⚙️  Setup Crisis Support for Your Country")
        
        print("\n💙 RESCUE TECHNIQUES:")
        for i, (key, session) in enumerate(self.sessions.items(), 4):
            print(f"{i}. {session['title']} ({session['duration']})")
        
        print(f"\n{len(self.sessions) + 4}. 🎲 Quick Random Rescue")
        print(f"{len(self.sessions) + 5}. 📊 View Rescue History")
        print("0. Exit")
        
        try:
            choice = input("\nSelect an option (0-{}): ".format(len(self.sessions) + 5)).strip()
            
            if choice == "0":
                return
            elif choice == "1":
                self.crisis_support.display_crisis_help()
            elif choice == "2":
                self.show_international_crisis_menu()
            elif choice == "3":
                self.crisis_support.interactive_country_setup()
            elif choice == str(len(self.sessions) + 4):
                self.quick_rescue()
            elif choice == str(len(self.sessions) + 5):
                self.show_rescue_history()
            else:
                try:
                    idx = int(choice) - 4
                    if 0 <= idx < len(self.sessions):
                        feeling = list(self.sessions.keys())[idx]
                        self.start_rescue_session(feeling)
                    else:
                        print("❌ Invalid selection")
                except ValueError:
                    print("❌ Please enter a number")
        except KeyboardInterrupt:
            print("\n\nStay safe. You matter. 💝")

    def show_international_crisis_menu(self):
        """Show international crisis support menu"""
        print("\n🌍 INTERNATIONAL CRISIS SUPPORT")
        print("=" * 35)
        print("1. 📞 Show Crisis Resources for My Country")
        print("2. 🗺️  List All Available Countries")
        print("3. 🏥 Add Custom Local Resource")
        print("4. 📋 View My Custom Resources")
        print("5. 🔧 Change Country Setting")
        print("0. Back to Main Menu")
        
        try:
            choice = input("\nSelect option (0-5): ").strip()
            
            if choice == "0":
                return
            elif choice == "1":
                self.crisis_support.display_crisis_help()
            elif choice == "2":
                self.crisis_support.list_available_countries()
            elif choice == "3":
                self.add_custom_crisis_resource()
            elif choice == "4":
                self.crisis_support.show_custom_resources()
            elif choice == "5":
                self.crisis_support.interactive_country_setup()
            else:
                print("❌ Invalid selection")
                
            input("\nPress Enter to continue...")
        except KeyboardInterrupt:
            print("\n\nReturning to main menu...")

    def add_custom_crisis_resource(self):
        """Interactive custom crisis resource addition"""
        print("\n🏥 ADD CUSTOM CRISIS RESOURCE")
        print("=" * 32)
        print("Add a local crisis resource specific to your area")
        
        try:
            name = input("Resource name (e.g., 'Local Crisis Center'): ").strip()
            if not name:
                print("❌ Name is required")
                return
                
            number = input("Phone number: ").strip()
            if not number:
                print("❌ Phone number is required")
                return
                
            description = input("Description (optional): ").strip()
            
            if self.crisis_support.add_custom_resource(name, number, description):
                print(f"\n✅ Added: {name}")
                print("This resource will now appear in your crisis support options.")
            else:
                print("❌ Failed to add resource")
                
        except KeyboardInterrupt:
            print("\n\nCancelled.")

    def check_crisis_indicators(self, user_input=""):
        """Check for crisis indicators in user input"""
        crisis_keywords = [
            'suicide', 'kill myself', 'end it all', 'want to die', 'hurt myself',
            'self harm', 'cutting', 'overdose', 'jump', 'hanging', 'gun',
            'razor', 'pills', 'bridge', 'worthless', 'hopeless', 'no point',
            'better off dead', 'can\'t go on', 'give up', 'end the pain'
        ]
        
        user_lower = user_input.lower()
        for keyword in crisis_keywords:
            if keyword in user_lower:
                return True
        return False

    def crisis_intervention(self):
        """Immediate crisis intervention"""
        print("\n" + "🆘" * 20)
        print("CRISIS SUPPORT ACTIVATED")
        print("🆘" * 20)
        
        print("\n💝 You reached out, and that takes courage.")
        print("🐺 Your inner wolf is trying to protect you from pain.")
        print("🤝 You don't have to face this alone.")
        
        print("\n🚨 IMMEDIATE HELP:")
        self.crisis_support.display_crisis_help()
        
        print("\n" + "─" * 50)
        print("🧘 WHILE YOU WAIT FOR HELP:")
        print("• Stay with someone if possible")
        print("• Remove any means of self-harm")
        print("• Focus on your breathing")
        print("• Remember: This feeling is temporary")
        print("• You have survived difficult times before")
        
        print("\n💙 QUICK GROUNDING TECHNIQUE:")
        self.emergency_grounding()
        
        print("\n🔄 Would you like to:")
        print("1. Call a crisis line now")
        print("2. Try a calming technique")
        print("3. See more crisis resources")
        
        try:
            choice = input("\nChoose (1-3): ").strip()
            if choice == "1":
                self.crisis_support.display_crisis_help()
            elif choice == "2":
                self.start_rescue_session("panic")
            elif choice == "3":
                self.show_international_crisis_menu()
        except KeyboardInterrupt:
            print("\n\n🆘 Please reach out for help. You matter.")

    def emergency_grounding(self):
        """Emergency grounding technique"""
        print("\n🧘 EMERGENCY GROUNDING (30 seconds)")
        print("Follow along - this will help:")
        
        techniques = [
            "Take a slow, deep breath in through your nose...",
            "Hold it for 3 seconds... 1... 2... 3...",
            "Slowly breathe out through your mouth...",
            "Feel your feet on the ground",
            "Notice 3 things you can see around you",
            "Say your name out loud",
            "Remember: You are safe in this moment"
        ]
        
        for technique in techniques:
            print(f"• {technique}")
            time.sleep(3)
        
        print("\n💙 How do you feel now? Even a small improvement matters.")

    def show_rescue_menu(self):
        """Show available rescue sessions"""
        print("🚨 Rescue Sessions - Quick Support When You Need It")
        print("=" * 60)
        print("Choose what you're feeling right now for immediate support:")
        print()
        
        feelings = list(self.sessions.keys())
        for i, feeling in enumerate(feelings, 1):
            session_info = self.sessions[feeling]
            print(f"{i}. {session_info['title']}")
            print(f"   {session_info['description']}")
            print(f"   Duration: {session_info['duration']}")
            print()
        
        choice = input("Choose a rescue session (1-6) or press Enter to return: ").strip()
        
        if choice.isdigit():
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(feelings):
                    self.start_rescue_session(feelings[choice_idx])
            except ValueError:
                pass
    
    def start_rescue_session(self, feeling: str):
        """Start a rescue session for a specific feeling"""
        if feeling not in self.sessions:
            print(f"Rescue session for '{feeling}' not found.")
            return
        
        session_info = self.sessions[feeling]
        
        print(f"\n🆘 {session_info['title']} - Rescue Session")
        print("=" * 50)
        print(f"{session_info['description']}")
        print(f"This will take about {session_info['duration']}")
        print()
        
        print("💙 First, take a moment to acknowledge what you're feeling.")
        print("It's completely normal and okay to feel this way.")
        print("You're taking a positive step by seeking support.")
        print()
        
        input("Press Enter when you're ready to begin...")
        print()
        
        # Choose a technique (random or let user choose)
        techniques = session_info["techniques"]
        
        if len(techniques) > 1:
            print("Choose a technique:")
            for i, technique in enumerate(techniques, 1):
                print(f"{i}. {technique['name']}")
            
            print()
            technique_choice = input("Choose technique (1-3) or press Enter for random: ").strip()
            
            if technique_choice.isdigit():
                try:
                    technique_idx = int(technique_choice) - 1
                    if 0 <= technique_idx < len(techniques):
                        chosen_technique = techniques[technique_idx]
                    else:
                        chosen_technique = random.choice(techniques)
                except ValueError:
                    chosen_technique = random.choice(techniques)
            else:
                chosen_technique = random.choice(techniques)
        else:
            chosen_technique = techniques[0]
        
        # Deliver the technique
        self._deliver_rescue_technique(chosen_technique)
        
        # Post-session check-in
        self._post_rescue_checkin(feeling, chosen_technique)
    
    def _deliver_rescue_technique(self, technique: Dict):
        """Deliver a rescue technique step by step"""
        print(f"🎯 {technique['name']}")
        print("=" * 40)
        print("Follow these steps at your own pace:")
        print()
        
        for i, step in enumerate(technique["steps"], 1):
            print(f"{i}. {step}")
            
            if i < len(technique["steps"]):
                input("   Press Enter when ready for the next step...")
                print()
        
        print("\n✨ Take a moment to notice how you feel now.")
        time.sleep(2)
    
    def _post_rescue_checkin(self, feeling: str, technique: Dict):
        """Check in with user after rescue session"""
        print("\n💙 How are you feeling now?")
        print("=" * 30)
        
        # Simple mood check
        mood_before = input("How were you feeling before (1-10, 1=very difficult, 10=great)? ").strip()
        mood_after = input("How are you feeling now (1-10)? ").strip()
        
        try:
            mood_before = max(1, min(10, int(mood_before)))
            mood_after = max(1, min(10, int(mood_after)))
            
            if mood_after > mood_before:
                print(f"🌟 Great! Your mood improved from {mood_before} to {mood_after}")
                print("That's the power of taking action when you're struggling.")
            elif mood_after == mood_before:
                print(f"Your mood stayed at {mood_after}. Sometimes that's exactly what we need.")
                print("You showed up for yourself, and that matters.")
            else:
                print(f"Your mood is at {mood_after}. That's okay.")
                print("Sometimes we need more support, and that's completely normal.")
        except ValueError:
            pass
        
        # Helpful reflection
        print("\n💭 Remember:")
        print("• You took positive action when you were struggling")
        print("• These techniques get more effective with practice")
        print("• It's okay to use rescue sessions as often as you need")
        print("• You're building resilience by learning these skills")
        
        # Additional support options
        print("\n🔗 Additional Support:")
        print("• Try another rescue session if you need more help")
        print("• Use 'om mood' to track how you're feeling over time")
        print("• Consider 'om learn' for longer-term skill building")
        print("• Remember that professional help is available if needed")
        
        # Save session data
        self._save_rescue_session(feeling, technique["name"], mood_before if 'mood_before' in locals() else None, 
                                 mood_after if 'mood_after' in locals() else None)
        
        # Offer follow-up
        print()
        another = input("Would you like to try another rescue session? (y/n): ").strip().lower()
        if another == 'y':
            self.show_rescue_menu()
    
    def quick_rescue(self):
        """Quick rescue session based on immediate need assessment"""
        print("⚡ Quick Rescue - Immediate Support")
        print("=" * 40)
        print("Let's quickly identify what you need right now.")
        print()
        
        # Quick assessment
        questions = [
            ("Are you feeling overwhelmed by everything on your plate?", "overwhelmed"),
            ("Are you feeling anxious or worried about something?", "anxious"),
            ("Are you feeling angry or frustrated?", "angry"),
            ("Are you feeling sad or down?", "sad"),
            ("Are you feeling restless or unable to sit still?", "restless"),
            ("Are you feeling lonely or disconnected?", "lonely")
        ]
        
        print("Answer yes/no to these quick questions:")
        print()
        
        matches = []
        for question, feeling in questions:
            answer = input(f"{question} (y/n): ").strip().lower()
            if answer == 'y':
                matches.append(feeling)
        
        if not matches:
            print("\nIt sounds like you might just need a moment of calm.")
            print("Let's do a quick breathing exercise.")
            self._quick_breathing_exercise()
        elif len(matches) == 1:
            print(f"\nI'll start a rescue session for feeling {matches[0]}.")
            self.start_rescue_session(matches[0])
        else:
            print(f"\nYou're dealing with multiple difficult feelings. That's tough.")
            print("Let's start with the one that feels most intense right now.")
            print()
            
            for i, feeling in enumerate(matches, 1):
                session_title = self.sessions[feeling]["title"]
                print(f"{i}. {session_title}")
            
            choice = input(f"\nChoose the most pressing feeling (1-{len(matches)}): ").strip()
            
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(matches):
                    self.start_rescue_session(matches[choice_idx])
                else:
                    self.start_rescue_session(matches[0])
            except ValueError:
                self.start_rescue_session(matches[0])
    
    def _quick_breathing_exercise(self):
        """Simple breathing exercise for general calm"""
        print("\n🫁 Quick Calm Breathing")
        print("=" * 30)
        print("Let's do a simple breathing exercise to help you feel more centered.")
        print()
        
        input("Get comfortable and press Enter to begin...")
        print()
        
        for round_num in range(3):
            print(f"Round {round_num + 1}/3")
            print("Breathe in slowly... 1...2...3...4")
            time.sleep(4)
            print("Hold gently... 1...2")
            time.sleep(2)
            print("Breathe out slowly... 1...2...3...4...5...6")
            time.sleep(6)
            print("Rest...")
            time.sleep(2)
            print()
        
        print("✨ Take a moment to notice how you feel.")
        print("Sometimes a few mindful breaths is all we need.")
    
    def show_rescue_history(self):
        """Show history of rescue sessions used"""
        data = self._load_rescue_data()
        sessions = data.get("sessions", [])
        
        if not sessions:
            print("📊 Rescue Session History")
            print("=" * 30)
            print("You haven't used any rescue sessions yet.")
            print("They're here whenever you need quick support!")
            return
        
        print("📊 Your Rescue Session History")
        print("=" * 40)
        
        # Recent sessions
        recent_sessions = sessions[-10:]
        print("Recent rescue sessions:")
        
        for session in recent_sessions:
            date = datetime.fromisoformat(session["timestamp"]).strftime("%m-%d %H:%M")
            feeling = session["feeling"].replace("_", " ").title()
            technique = session["technique"]
            
            mood_info = ""
            if session.get("mood_before") and session.get("mood_after"):
                mood_info = f" ({session['mood_before']}→{session['mood_after']})"
            
            print(f"   {date}: {feeling} - {technique}{mood_info}")
        
        print()
        
        # Statistics
        total_sessions = len(sessions)
        print(f"📈 Statistics:")
        print(f"   Total rescue sessions: {total_sessions}")
        
        # Most common feelings
        feeling_counts = {}
        for session in sessions:
            feeling = session["feeling"]
            feeling_counts[feeling] = feeling_counts.get(feeling, 0) + 1
        
        if feeling_counts:
            print(f"\n🎯 Most common challenges:")
            sorted_feelings = sorted(feeling_counts.items(), key=lambda x: x[1], reverse=True)
            for feeling, count in sorted_feelings[:3]:
                feeling_title = self.sessions[feeling]["title"]
                print(f"   {feeling_title}: {count} times")
        
        # Effectiveness
        effective_sessions = [s for s in sessions if s.get("mood_after", 0) > s.get("mood_before", 0)]
        if len(sessions) > 0:
            effectiveness = (len(effective_sessions) / len(sessions)) * 100
            print(f"\n⭐ Sessions that improved mood: {len(effective_sessions)}/{len(sessions)} ({effectiveness:.0f}%)")
        
        print("\n💡 Remember: Each time you use a rescue session, you're building")
        print("    your emotional resilience and coping skills!")
    
    def _save_rescue_session(self, feeling: str, technique: str, mood_before: Optional[int], mood_after: Optional[int]):
        """Save rescue session data"""
        data = self._load_rescue_data()
        
        session = {
            "timestamp": datetime.now().isoformat(),
            "feeling": feeling,
            "technique": technique,
            "mood_before": mood_before,
            "mood_after": mood_after
        }
        
        data.setdefault("sessions", []).append(session)
        self._save_rescue_data(data)
    
    def _load_rescue_data(self) -> Dict:
        """Load rescue session data"""
        if not os.path.exists(RESCUE_SESSIONS_FILE):
            return {}
        
        try:
            with open(RESCUE_SESSIONS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_rescue_data(self, data: Dict):
        """Save rescue session data"""
        try:
            with open(RESCUE_SESSIONS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save rescue session data: {e}")


def rescue_sessions_command(action: str = "menu", **kwargs):
    """Main rescue sessions command interface with international crisis support"""
    rescue = RescueSessions()
    
    if action == "menu":
        rescue.show_rescue_menu()
    elif action == "crisis":
        rescue.crisis_support.display_crisis_help()
    elif action == "international":
        rescue.show_international_crisis_menu()
    elif action == "setup":
        rescue.crisis_support.interactive_country_setup()
    elif action == "countries":
        rescue.crisis_support.list_available_countries()
    elif action == "custom":
        rescue.crisis_support.show_custom_resources()
    elif action == "add-custom":
        rescue.add_custom_crisis_resource()
    elif action == "emergency":
        rescue.crisis_intervention()
    elif action == "quick":
        rescue.quick_rescue()
    elif action == "history":
        rescue.show_rescue_history()
    elif action == "feeling":
        feeling = kwargs.get('feeling')
        if feeling and feeling in rescue.sessions:
            rescue.start_rescue_session(feeling)
        else:
            print(f"Unknown feeling: {feeling}")
            print(f"Available: {', '.join(rescue.sessions.keys())}")
    elif action == "country":
        country = kwargs.get('country', '').upper()
        if country:
            rescue.crisis_support.display_crisis_help(country)
        else:
            print("Please specify a country code (e.g., om rescue country US)")
    else:
        print(f"🆘 RESCUE SESSIONS - Available Commands:")
        print("=" * 40)
        print("Crisis Support:")
        print("  om rescue crisis          - Show crisis resources for your country")
        print("  om rescue international   - International crisis support menu")
        print("  om rescue setup          - Setup your country for crisis support")
        print("  om rescue countries      - List all available countries")
        print("  om rescue country [CODE] - Show crisis resources for specific country")
        print("  om rescue emergency      - Immediate crisis intervention")
        print("")
        print("Rescue Techniques:")
        print("  om rescue menu           - Interactive rescue menu")
        print("  om rescue quick          - Quick random rescue technique")
        print("  om rescue feeling [TYPE] - Specific rescue session")
        print("  om rescue history        - View rescue session history")
        print("")
        print("Custom Resources:")
        print("  om rescue custom         - View your custom crisis resources")
        print("  om rescue add-custom     - Add a custom local crisis resource")
        print("")
        print(f"Available feelings: {', '.join(rescue.sessions.keys())}")


# Command aliases for easier access
def crisis_command(**kwargs):
    """Direct crisis support command"""
    return rescue_sessions_command("crisis", **kwargs)

def emergency_command(**kwargs):
    """Emergency crisis intervention command"""
    return rescue_sessions_command("emergency", **kwargs)
