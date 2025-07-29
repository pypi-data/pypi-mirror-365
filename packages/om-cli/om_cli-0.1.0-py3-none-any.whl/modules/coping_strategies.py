"""
Coping Strategies module for om
Evidence-based techniques for managing stress, anxiety, and difficult emotions
"""

import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

COPING_FILE = os.path.expanduser("~/.om_coping.json")

class CopingStrategies:
    def __init__(self):
        self.coping_categories = {
            "immediate": {
                "name": "Immediate Relief",
                "description": "Quick techniques for acute stress or panic",
                "techniques": [
                    {
                        "name": "5-4-3-2-1 Grounding",
                        "description": "Identify 5 things you see, 4 you hear, 3 you touch, 2 you smell, 1 you taste",
                        "duration": "2-3 minutes",
                        "instructions": [
                            "Look around and name 5 things you can see",
                            "Listen and identify 4 things you can hear", 
                            "Touch and notice 3 different textures",
                            "Identify 2 things you can smell",
                            "Notice 1 thing you can taste"
                        ]
                    },
                    {
                        "name": "Box Breathing",
                        "description": "4-4-4-4 breathing pattern for immediate calm",
                        "duration": "3-5 minutes",
                        "instructions": [
                            "Breathe in for 4 counts",
                            "Hold your breath for 4 counts",
                            "Breathe out for 4 counts", 
                            "Hold empty for 4 counts",
                            "Repeat 8-10 cycles"
                        ]
                    },
                    {
                        "name": "Cold Water Reset",
                        "description": "Use cold water to activate your vagus nerve",
                        "duration": "1-2 minutes",
                        "instructions": [
                            "Splash cold water on your face",
                            "Hold cold water in your mouth for 30 seconds",
                            "Place a cold, damp cloth on your neck",
                            "Take slow, deep breaths",
                            "Notice the calming effect"
                        ]
                    },
                    {
                        "name": "Progressive Muscle Release",
                        "description": "Quick tension release for physical stress",
                        "duration": "3-5 minutes",
                        "instructions": [
                            "Tense your shoulders for 5 seconds, then release",
                            "Clench your fists for 5 seconds, then release",
                            "Tighten your jaw for 5 seconds, then release",
                            "Scrunch your face for 5 seconds, then release",
                            "Notice the contrast between tension and relaxation"
                        ]
                    }
                ]
            },
            "emotional": {
                "name": "Emotional Regulation",
                "description": "Techniques for managing difficult emotions",
                "techniques": [
                    {
                        "name": "RAIN Technique",
                        "description": "Recognize, Allow, Investigate, Non-attachment",
                        "duration": "5-10 minutes",
                        "instructions": [
                            "RECOGNIZE: What emotion am I feeling right now?",
                            "ALLOW: Can I let this feeling be here without fighting it?",
                            "INVESTIGATE: Where do I feel this in my body? What does it need?",
                            "NON-ATTACHMENT: This feeling is temporary and will pass"
                        ]
                    },
                    {
                        "name": "Emotional Surfing",
                        "description": "Ride the wave of emotion without being overwhelmed",
                        "duration": "5-15 minutes",
                        "instructions": [
                            "Notice the emotion arising like a wave",
                            "Observe where you feel it in your body",
                            "Breathe with the sensation, don't fight it",
                            "Watch as it peaks and begins to subside",
                            "Remember: all emotions are temporary"
                        ]
                    },
                    {
                        "name": "Opposite Action",
                        "description": "Act opposite to your emotional urge (DBT technique)",
                        "duration": "Variable",
                        "instructions": [
                            "Identify the emotion and its urge (e.g., anger → attack)",
                            "Ask: Is this emotion justified and helpful?",
                            "If not, do the opposite of the urge",
                            "Angry? Be gentle. Sad? Do something active.",
                            "Notice how acting opposite changes the emotion"
                        ]
                    },
                    {
                        "name": "Self-Compassion Break",
                        "description": "Treat yourself with kindness during difficult moments",
                        "duration": "3-5 minutes",
                        "instructions": [
                            "Place your hand on your heart",
                            "Say: 'This is a moment of suffering'",
                            "Say: 'Suffering is part of human experience'",
                            "Say: 'May I be kind to myself in this moment'",
                            "Breathe with compassion for yourself"
                        ]
                    }
                ]
            },
            "cognitive": {
                "name": "Cognitive Strategies",
                "description": "Techniques for managing thoughts and mental patterns",
                "techniques": [
                    {
                        "name": "Thought Record",
                        "description": "Examine and challenge negative thought patterns",
                        "duration": "10-15 minutes",
                        "instructions": [
                            "Write down the triggering situation",
                            "Identify the automatic thought",
                            "Rate your belief in this thought (0-100%)",
                            "Look for evidence for and against the thought",
                            "Create a more balanced, realistic thought",
                            "Rate your belief in the new thought"
                        ]
                    },
                    {
                        "name": "Cognitive Defusion",
                        "description": "Create distance from unhelpful thoughts",
                        "duration": "3-5 minutes",
                        "instructions": [
                            "Notice the thought you're having",
                            "Say: 'I'm having the thought that...'",
                            "Then say: 'I notice I'm having the thought that...'",
                            "Imagine the thought as words on a screen",
                            "Watch the thought come and go without attachment"
                        ]
                    },
                    {
                        "name": "Worry Time",
                        "description": "Schedule specific time for worrying",
                        "duration": "15-20 minutes",
                        "instructions": [
                            "Set aside 15 minutes daily for 'worry time'",
                            "When worries arise, write them down for later",
                            "During worry time, review your list",
                            "For each worry, ask: Can I do something about this?",
                            "If yes, make an action plan. If no, practice letting go"
                        ]
                    },
                    {
                        "name": "Perspective Taking",
                        "description": "Gain different viewpoints on your situation",
                        "duration": "5-10 minutes",
                        "instructions": [
                            "Describe your situation objectively",
                            "How would a good friend view this situation?",
                            "How will this matter in 5 years?",
                            "What would you tell a friend in this situation?",
                            "What opportunities might this challenge create?"
                        ]
                    }
                ]
            },
            "behavioral": {
                "name": "Behavioral Activation",
                "description": "Actions to improve mood and reduce stress",
                "techniques": [
                    {
                        "name": "Pleasant Activity Scheduling",
                        "description": "Plan enjoyable activities to boost mood",
                        "duration": "Variable",
                        "instructions": [
                            "List 10 activities you usually enjoy",
                            "Rate each activity's pleasure potential (1-10)",
                            "Schedule 2-3 pleasant activities for this week",
                            "Start with small, achievable activities",
                            "Notice how your mood changes after activities"
                        ]
                    },
                    {
                        "name": "Behavioral Experiments",
                        "description": "Test negative predictions through action",
                        "duration": "Variable",
                        "instructions": [
                            "Identify a situation you're avoiding",
                            "Write down your prediction of what will happen",
                            "Rate how strongly you believe this (0-100%)",
                            "Design a small experiment to test this",
                            "Compare the actual outcome to your prediction"
                        ]
                    },
                    {
                        "name": "Mastery Activities",
                        "description": "Engage in activities that provide accomplishment",
                        "duration": "Variable",
                        "instructions": [
                            "Choose a skill you'd like to develop",
                            "Break it into small, manageable steps",
                            "Practice for 10-15 minutes daily",
                            "Track your progress",
                            "Celebrate small improvements"
                        ]
                    },
                    {
                        "name": "Social Connection",
                        "description": "Reach out to others for support",
                        "duration": "Variable",
                        "instructions": [
                            "Identify 3 people you could reach out to",
                            "Choose one person to contact today",
                            "Send a text, make a call, or meet in person",
                            "Share something genuine about how you're doing",
                            "Ask about their life too"
                        ]
                    }
                ]
            },
            "mindfulness": {
                "name": "Mindfulness & Acceptance",
                "description": "Present-moment awareness and acceptance practices",
                "techniques": [
                    {
                        "name": "Body Scan",
                        "description": "Systematic awareness of physical sensations",
                        "duration": "10-20 minutes",
                        "instructions": [
                            "Lie down or sit comfortably",
                            "Start with your toes, notice any sensations",
                            "Slowly move attention up through your body",
                            "Don't try to change anything, just notice",
                            "End with awareness of your whole body"
                        ]
                    },
                    {
                        "name": "Mindful Walking",
                        "description": "Walking meditation for grounding",
                        "duration": "5-15 minutes",
                        "instructions": [
                            "Walk slower than usual",
                            "Feel your feet touching the ground",
                            "Notice the movement of your legs",
                            "When your mind wanders, return to walking",
                            "End by standing still for a moment"
                        ]
                    },
                    {
                        "name": "Loving-Kindness Meditation",
                        "description": "Cultivate compassion for self and others",
                        "duration": "10-15 minutes",
                        "instructions": [
                            "Start by sending loving-kindness to yourself",
                            "Say: 'May I be happy, may I be healthy, may I be at peace'",
                            "Extend these wishes to a loved one",
                            "Then to a neutral person",
                            "Finally to someone you have difficulty with",
                            "End by sending loving-kindness to all beings"
                        ]
                    },
                    {
                        "name": "Acceptance Practice",
                        "description": "Practice accepting difficult experiences",
                        "duration": "5-10 minutes",
                        "instructions": [
                            "Identify something you're struggling to accept",
                            "Notice your resistance to this experience",
                            "Say: 'This is what's here right now'",
                            "Breathe with the difficulty without trying to fix it",
                            "Practice saying: 'I can be with this'"
                        ]
                    }
                ]
            }
        }
        
        self.crisis_resources = {
            "immediate_danger": {
                "title": "Immediate Danger",
                "resources": [
                    "Call 911 for immediate emergency",
                    "Go to your nearest emergency room",
                    "Call National Suicide Prevention Lifeline: 988"
                ]
            },
            "crisis_support": {
                "title": "Crisis Support",
                "resources": [
                    "Crisis Text Line: Text HOME to 741741",
                    "National Suicide Prevention Lifeline: 988",
                    "SAMHSA National Helpline: 1-800-662-4357"
                ]
            },
            "professional_help": {
                "title": "Professional Help",
                "resources": [
                    "Contact your healthcare provider",
                    "Find a therapist: psychologytoday.com",
                    "Employee Assistance Program (if available)",
                    "Community mental health centers"
                ]
            }
        }
    
    def show_coping_menu(self):
        """Display main coping strategies menu"""
        print("🧘 Coping Strategies & Emotional Support")
        print("=" * 50)
        print("Evidence-based techniques for managing stress, anxiety, and difficult emotions")
        print()
        
        # Show recent usage
        data = self._load_coping_data()
        recent_techniques = data.get('recent_techniques', [])
        
        if recent_techniques:
            print("📊 Recently Used:")
            for technique in recent_techniques[-3:]:  # Show last 3
                print(f"   • {technique['name']} - {technique['category']}")
            print()
        
        print("🎯 Coping Categories:")
        categories = list(self.coping_categories.keys())
        for i, category_id in enumerate(categories, 1):
            category = self.coping_categories[category_id]
            print(f"{i}. {category['name']} - {category['description']}")
        
        print(f"{len(categories) + 1}. Crisis resources and emergency support")
        print(f"{len(categories) + 2}. Track your coping practice")
        print(f"{len(categories) + 3}. View your coping history")
        print()
        
        choice = input(f"Choose an option (1-{len(categories) + 3}) or press Enter to return: ").strip()
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(categories):
                category_id = categories[choice_num - 1]
                self._show_category_techniques(category_id)
            elif choice_num == len(categories) + 1:
                self._show_crisis_resources()
            elif choice_num == len(categories) + 2:
                self._track_coping_practice()
            elif choice_num == len(categories) + 3:
                self._show_coping_history()
        except ValueError:
            pass
    
    def _show_category_techniques(self, category_id: str):
        """Show techniques for a specific category"""
        category = self.coping_categories[category_id]
        
        print(f"\n🎯 {category['name']}")
        print("=" * 40)
        print(f"{category['description']}")
        print()
        
        techniques = category['techniques']
        for i, technique in enumerate(techniques, 1):
            print(f"{i}. {technique['name']}")
            print(f"   {technique['description']}")
            print(f"   Duration: {technique['duration']}")
            print()
        
        print(f"{len(techniques) + 1}. Get a random technique from this category")
        print()
        
        choice = input(f"Choose a technique (1-{len(techniques) + 1}) or press Enter to return: ").strip()
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(techniques):
                technique = techniques[choice_num - 1]
                self._guide_technique(technique, category_id)
            elif choice_num == len(techniques) + 1:
                technique = random.choice(techniques)
                print(f"\n🎲 Random technique: {technique['name']}")
                self._guide_technique(technique, category_id)
        except ValueError:
            pass
    
    def _guide_technique(self, technique: Dict, category_id: str):
        """Guide user through a specific technique"""
        print(f"\n🧘 {technique['name']}")
        print("=" * 40)
        print(f"Description: {technique['description']}")
        print(f"Duration: {technique['duration']}")
        print()
        
        print("📋 Instructions:")
        for i, instruction in enumerate(technique['instructions'], 1):
            print(f"{i}. {instruction}")
        print()
        
        # Ask if they want to be guided through it
        guided = input("Would you like guided practice? (y/n): ").strip().lower()
        
        if guided in ['y', 'yes']:
            self._guided_practice(technique, category_id)
        else:
            # Just track that they viewed it
            self._log_technique_use(technique['name'], category_id, "viewed")
            print("Take your time with the technique. Return here when you're done!")
    
    def _guided_practice(self, technique: Dict, category_id: str):
        """Provide guided practice for a technique"""
        print(f"\n🎯 Guided Practice: {technique['name']}")
        print("=" * 40)
        print("Follow along with each step. Press Enter when ready to continue.")
        print()
        
        for i, instruction in enumerate(technique['instructions'], 1):
            input(f"Step {i}: {instruction}\n[Press Enter when ready]")
            print()
        
        print("✅ Great job completing the technique!")
        
        # Get feedback
        print("\nHow are you feeling now?")
        print("1. Much better")
        print("2. Somewhat better") 
        print("3. About the same")
        print("4. Somewhat worse")
        print("5. Much worse")
        
        feeling = input("Rate your current state (1-5): ").strip()
        
        try:
            feeling_num = int(feeling)
            feeling_labels = {
                1: "much_better",
                2: "somewhat_better", 
                3: "same",
                4: "somewhat_worse",
                5: "much_worse"
            }
            feeling_label = feeling_labels.get(feeling_num, "same")
        except ValueError:
            feeling_label = "same"
        
        # Log the practice
        self._log_technique_use(technique['name'], category_id, "completed", feeling_label)
        
        # Provide encouragement
        if feeling_label in ["much_better", "somewhat_better"]:
            print("\n🌟 Wonderful! It's great that the technique helped.")
            print("Consider using this technique again when you need support.")
        elif feeling_label == "same":
            print("\n💪 That's okay! Sometimes techniques take practice to be effective.")
            print("Try using it regularly to build the skill.")
        else:
            print("\n🤗 That's alright. Not every technique works for everyone.")
            print("Try a different technique or consider reaching out for additional support.")
            
            # Suggest crisis resources if feeling much worse
            if feeling_label == "much_worse":
                print("\n⚠️  If you're feeling significantly worse or in crisis:")
                self._show_crisis_resources()
    
    def _show_crisis_resources(self):
        """Show crisis and emergency resources"""
        print("\n🆘 Crisis Resources & Emergency Support")
        print("=" * 50)
        print("If you're in immediate danger or having thoughts of self-harm,")
        print("please reach out for professional help immediately.")
        print()
        
        for resource_type, resource_info in self.crisis_resources.items():
            print(f"🔴 {resource_info['title']}:")
            for resource in resource_info['resources']:
                print(f"   • {resource}")
            print()
        
        print("🌟 Remember:")
        print("• You are not alone in this")
        print("• Crisis feelings are temporary")
        print("• Professional help is available 24/7")
        print("• Reaching out for help is a sign of strength")
        print()
        
        input("Press Enter to continue...")
    
    def _track_coping_practice(self):
        """Track regular coping practice"""
        print("\n📊 Track Your Coping Practice")
        print("=" * 40)
        
        print("How has your overall coping been today?")
        print("1. Excellent - Used multiple strategies effectively")
        print("2. Good - Used some strategies, mostly helpful")
        print("3. Fair - Tried some strategies, mixed results")
        print("4. Poor - Struggled to use strategies effectively")
        print("5. Very difficult - Couldn't use strategies today")
        print()
        
        rating = input("Rate your coping today (1-5): ").strip()
        
        try:
            rating_num = int(rating)
            rating_labels = {
                1: "excellent",
                2: "good",
                3: "fair", 
                4: "poor",
                5: "very_difficult"
            }
            rating_label = rating_labels.get(rating_num, "fair")
        except ValueError:
            rating_label = "fair"
        
        # Get additional context
        stressors = input("What were your main stressors today? (optional): ").strip()
        helpful_strategies = input("What strategies were most helpful? (optional): ").strip()
        notes = input("Any other notes about your coping today? (optional): ").strip()
        
        # Save tracking data
        data = self._load_coping_data()
        
        tracking_entry = {
            "date": datetime.now().isoformat(),
            "rating": rating_label,
            "stressors": stressors,
            "helpful_strategies": helpful_strategies,
            "notes": notes
        }
        
        data.setdefault('daily_tracking', []).append(tracking_entry)
        self._save_coping_data(data)
        
        print(f"\n✅ Coping practice tracked for today!")
        
        # Provide personalized feedback
        if rating_label in ["excellent", "good"]:
            print("🌟 Great job using your coping strategies today!")
        elif rating_label == "fair":
            print("💪 Keep practicing! Coping skills improve with use.")
        else:
            print("🤗 Difficult days happen. Be gentle with yourself.")
            print("Consider trying a different technique or reaching out for support.")
    
    def _show_coping_history(self):
        """Show coping practice history and patterns"""
        data = self._load_coping_data()
        
        print("\n📈 Your Coping History")
        print("=" * 40)
        
        # Show technique usage
        recent_techniques = data.get('recent_techniques', [])
        if recent_techniques:
            print("🎯 Recent Techniques Used:")
            technique_counts = {}
            for technique in recent_techniques[-10:]:  # Last 10
                name = technique['name']
                technique_counts[name] = technique_counts.get(name, 0) + 1
            
            for technique, count in sorted(technique_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {technique}: {count} times")
            print()
        
        # Show daily tracking
        daily_tracking = data.get('daily_tracking', [])
        if daily_tracking:
            print("📊 Recent Daily Ratings:")
            for entry in daily_tracking[-7:]:  # Last 7 days
                date_str = datetime.fromisoformat(entry['date']).strftime('%Y-%m-%d')
                rating = entry['rating'].replace('_', ' ').title()
                print(f"   • {date_str}: {rating}")
            print()
            
            # Calculate average rating
            rating_values = {
                "excellent": 5,
                "good": 4,
                "fair": 3,
                "poor": 2,
                "very_difficult": 1
            }
            
            recent_ratings = [rating_values.get(entry['rating'], 3) for entry in daily_tracking[-7:]]
            if recent_ratings:
                avg_rating = sum(recent_ratings) / len(recent_ratings)
                print(f"📈 Average coping rating (last 7 days): {avg_rating:.1f}/5")
                
                if avg_rating >= 4:
                    print("🌟 You're doing great with your coping strategies!")
                elif avg_rating >= 3:
                    print("💪 You're managing well. Keep practicing!")
                else:
                    print("🤗 Consider trying new techniques or seeking additional support.")
        
        if not recent_techniques and not daily_tracking:
            print("No coping history yet. Start using techniques to build your history!")
        
        print()
        input("Press Enter to continue...")
    
    def _log_technique_use(self, technique_name: str, category_id: str, action: str, feeling: str = None):
        """Log when a technique is used"""
        data = self._load_coping_data()
        
        technique_entry = {
            "name": technique_name,
            "category": category_id,
            "action": action,  # "viewed" or "completed"
            "timestamp": datetime.now().isoformat(),
            "feeling_after": feeling
        }
        
        data.setdefault('recent_techniques', []).append(technique_entry)
        
        # Keep only last 50 entries
        if len(data['recent_techniques']) > 50:
            data['recent_techniques'] = data['recent_techniques'][-50:]
        
        self._save_coping_data(data)
    
    def _load_coping_data(self) -> Dict:
        """Load coping data from file"""
        if not os.path.exists(COPING_FILE):
            return {}
        
        try:
            with open(COPING_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_coping_data(self, data: Dict):
        """Save coping data to file"""
        try:
            with open(COPING_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save coping data: {e}")


def coping_strategies_command(action: str = "menu", **kwargs):
    """Main coping strategies command interface"""
    coping = CopingStrategies()
    
    if action == "menu":
        coping.show_coping_menu()
    elif action == "immediate":
        coping._show_category_techniques("immediate")
    elif action == "emotional":
        coping._show_category_techniques("emotional")
    elif action == "cognitive":
        coping._show_category_techniques("cognitive")
    elif action == "behavioral":
        coping._show_category_techniques("behavioral")
    elif action == "mindfulness":
        coping._show_category_techniques("mindfulness")
    elif action == "crisis":
        coping._show_crisis_resources()
    elif action == "track":
        coping._track_coping_practice()
    elif action == "history":
        coping._show_coping_history()
    else:
        print(f"Unknown coping action: {action}")
        print("Available actions: menu, immediate, emotional, cognitive, behavioral, mindfulness, crisis, track, history")
