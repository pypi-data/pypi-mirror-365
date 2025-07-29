#!/usr/bin/env python3
"""
Nicky Case Mental Health Guide Integration
Based on the brilliant essay "How to Mental Health" by Nicky Case
https://github.com/ncase/mental-health

This module integrates the 9 evidence-based mental health habits
and the "fear as friend" philosophy into om's ecosystem.
"""

import json
import os
import random
from datetime import datetime, timedelta

class NickyCaseGuide:
    def __init__(self):
        self.data_dir = os.path.expanduser("~/.om")
        os.makedirs(self.data_dir, exist_ok=True)
        self.habits_file = os.path.join(self.data_dir, "nicky_habits.json")
        self.wolf_file = os.path.join(self.data_dir, "wolf_conversations.json")
        
        # The 9 Evidence-Based Mental Health Habits from Nicky Case
        self.habits = {
            "meditation": {
                "category": "Know Your Wolf",
                "title": "😌 Meditation",
                "description": "Observe your mind like a scientist: non-judgmentally",
                "goal": "NOT to clear your mind, but to OBSERVE it",
                "example_plan": "After brushing my teeth in the morning, I will go to the living room and set a timer to meditate for 2 minutes.",
                "benefits": "Meta-analyses show meditation improves anxiety & depression",
                "om_integration": ["om meditate", "om breathe", "om qb"]
            },
            "journaling": {
                "category": "Know Your Wolf", 
                "title": "📓 Journaling",
                "description": "Write about emotions AND try to understand them",
                "template": "Today when [event], I felt [feeling] because it seemed to fulfill/challenge my need for [need]. Next time, I'll try [experiments around that need].",
                "example_plan": "Before going to sleep, I will write/draw about my feelings for 10 minutes.",
                "benefits": "Moderately improves psychological AND physical health",
                "om_integration": ["om journal", "om mood", "om qm"]
            },
            "sleep": {
                "category": "Physical Needs",
                "title": "😴 Sleep", 
                "description": "Natural selection knocked you unconscious for 1/3 of life - there's a huge benefit",
                "benefits": "Reduces risk for heart disease, cancer, Alzheimer's, depression, anxiety",
                "example_plan": "When it's 10pm, I will turn off all my devices, and put them on charger, outside the bedroom, in a trash can, where they belong.",
                "om_integration": ["om sleep", "om insomnia", "om rest"]
            },
            "exercise": {
                "category": "Physical Needs",
                "title": "🏃‍♀️ Exercise",
                "description": "Just half an hour of moderate exercise a day",
                "benefits": "Exercise reduces depression AS MUCH AS psychotherapy or medication!",
                "example_plan": "After getting home in the evening, I'll go for a 10 minute stroll.",
                "om_integration": ["om physical", "om stretch", "om qs"]
            },
            "eat": {
                "category": "Physical Needs", 
                "title": "🍆 Eat",
                "description": "Your gut bacteria makes 90% of your body's serotonin",
                "philosophy": "Eat food, not too much, mostly plants (Michael Pollan)",
                "example_plan": "Before grocery shopping, I'll eat a fruit so I'm not hungry and won't get tempted to buy chocolate-flavored Cheetos. Again.",
                "om_integration": ["om habits", "om physical"]
            },
            "talk_friends": {
                "category": "Social Needs",
                "title": "👯‍♂️ Talk To Friends",
                "description": "High-quality social connections reduce depression, anxiety, and early death by 50%",
                "hierarchy": "Real-Life Face-To-Face > Videochat > Phone Call > Text/Email",
                "tips": ["Meet friends OUTSIDE usual context", "Regularly schedule friend-hangouts", "Share thoughts & feelings"],
                "example_plan": "Every first Monday of the month, I'll video-call my good friend who's in the distant, faraway land of New Haven, CT.",
                "om_integration": ["om social", "om connect"]
            },
            "make_friends": {
                "category": "Social Needs",
                "title": "🎳 Make New Friends", 
                "description": "Ask friends to introduce you, or join classes/volunteer groups",
                "options": ["Ask friends to introduce you to their friends", "Join a class or volunteer group or bowling league on Meetup.com"],
                "example_plan": "Every Thursday evening, I'll go to the French Meetup pour pratiquer mon terrible français.",
                "om_integration": ["om social", "om connect"]
            },
            "learning": {
                "category": "Becoming Better",
                "title": "💭 Learning",
                "description": "Push yourself to your fullest human potential",
                "examples": ["Draw", "Play ukulele", "Understand quantum computing", "Flirt in French", "Split apples with bare hands", "Make plushies", "Learn Morse code", "Try team sports", "Make chiptunes", "Learn Python", "Cook"],
                "example_plan": "Every Sunday evening, I'll try cooking a new recipe.",
                "om_integration": ["om learn", "om articles"]
            },
            "character": {
                "category": "Becoming Better",
                "title": "😇 'It Builds Character'",
                "description": "Benjamin Franklin's method: track virtues daily",
                "method": "Specific When→Then plans for moral improvement",
                "example_plan": "When I'm about to post something angry on the internet, I will wait one hour before hitting Send.",
                "philosophy": "Be the change you want to see in the world",
                "om_integration": ["om habits", "om gamify"]
            }
        }
        
        # Wolf wisdom quotes from Nicky Case
        self.wolf_wisdom = [
            "Fear is a guard dog for your needs.",
            "Pain is a protector.",
            "All feelings are imperfect signals about met/unmet needs.",
            "Healthy people don't 'cope' with emotions, they collaborate with them.",
            "Don't shoot the hyperactive guard dog - retrain it by forming habits.",
            "Physical health affects mental health & vice versa. Hardware affects software, software affects hardware.",
            "The goal of meditation is NOT to clear your mind, but to OBSERVE it.",
            "Your gut bacteria makes 90% of your body's serotonin - keep your microbes happy!",
            "High-quality social connections reduce your risk of early death by 50%.",
            "Exercise reduces depression as much as psychotherapy or medication!"
        ]

    def load_habits_data(self):
        """Load habit tracking data"""
        try:
            with open(self.habits_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_habits_data(self, data):
        """Save habit tracking data"""
        with open(self.habits_file, 'w') as f:
            json.dump(data, f, indent=2)

    def show_main_menu(self):
        """Show the main Nicky Case guide menu"""
        print("🐺 Nicky Case's Mental Health Guide")
        print("=" * 35)
        print("\"Fear is a guard dog for your needs\"")
        print()
        print("1. 📖 Read the full guide")
        print("2. 🎯 9 Evidence-Based Habits")
        print("3. 🐺 Talk to your inner wolf")
        print("4. 📊 Habit tracking dashboard")
        print("5. 💡 Daily wolf wisdom")
        print("6. 🔗 Integration with om features")
        print()
        
        choice = input("Choose an option (1-6): ")
        return choice

    def show_full_guide(self):
        """Display key excerpts from Nicky Case's guide"""
        print("📖 Nicky Case's Mental Health Guide")
        print("=" * 35)
        print()
        print("🐺 THE CORE INSIGHT:")
        print("Fear is not your enemy. Fear is your FRIEND.")
        print("Fear is a guard dog for your needs.")
        print()
        print("🧠 THE PHILOSOPHY:")
        print("• Do not fear fear itself")
        print("• Pain is a protector")
        print("• All feelings are imperfect signals about met/unmet needs")
        print("• Healthy people don't 'cope' with emotions, they COLLABORATE with them")
        print("• Use 'negative' emotions as clues, constructive criticism to improve your lives")
        print()
        print("🎯 THE METHOD:")
        print("If your fear guard-dog is hyperactive, don't shoot the dog! Retrain it by forming habits.")
        print("Habit = When X, Then Y")
        print("Track progress for ~66 days. One habit at a time.")
        print()
        print("🏗️ THE FOUNDATION:")
        print("Our fundamental human needs are:")
        print("• Physical needs (sleep, exercise, nutrition)")
        print("• Social needs (friends, connection, belonging)")
        print("• 'Becoming a better person' needs (learning, character, purpose)")
        print()
        print("💡 Read the full guide at: https://ncase.me/mental-health/")
        print()
        input("Press Enter to continue...")

    def show_nine_habits(self):
        """Display the 9 evidence-based habits"""
        print("🎯 9 Evidence-Based Mental Health Habits")
        print("=" * 40)
        print("Pick ONE habit, make a When→Then plan, track for 66 days!")
        print()
        
        categories = {
            "Know Your Wolf": [],
            "Physical Needs": [],
            "Social Needs": [],
            "Becoming Better": []
        }
        
        for habit_id, habit in self.habits.items():
            categories[habit["category"]].append((habit_id, habit))
        
        for category, habits in categories.items():
            print(f"🔸 {category}:")
            for habit_id, habit in habits:
                print(f"   {habit['title']}")
                print(f"   {habit['description']}")
                if 'om_integration' in habit:
                    print(f"   💻 Try: {', '.join(habit['om_integration'])}")
                print()
        
        habit_choice = input("Enter habit name to learn more (or 'back'): ").lower()
        
        # Find matching habit
        for habit_id, habit in self.habits.items():
            if habit_choice in habit_id or habit_choice in habit['title'].lower():
                self.show_habit_detail(habit_id, habit)
                return
        
        if habit_choice != 'back':
            print("Habit not found. Try again!")

    def show_habit_detail(self, habit_id, habit):
        """Show detailed information about a specific habit"""
        print(f"\n{habit['title']}")
        print("=" * len(habit['title']))
        print(f"Category: {habit['category']}")
        print()
        print(f"📝 Description: {habit['description']}")
        print()
        
        if 'benefits' in habit:
            print(f"✅ Benefits: {habit['benefits']}")
            print()
        
        if 'example_plan' in habit:
            print(f"📋 Example When→Then Plan:")
            print(f"   \"{habit['example_plan']}\"")
            print()
        
        if 'template' in habit:
            print(f"📝 Template: {habit['template']}")
            print()
        
        if 'om_integration' in habit:
            print(f"💻 Try these om commands:")
            for cmd in habit['om_integration']:
                print(f"   • {cmd}")
            print()
        
        start_tracking = input("Start tracking this habit? (y/n): ").lower()
        if start_tracking == 'y':
            self.start_habit_tracking(habit_id, habit)

    def start_habit_tracking(self, habit_id, habit):
        """Start tracking a specific habit"""
        print(f"\n🎯 Starting to track: {habit['title']}")
        print()
        
        when_part = input("When will you do this habit? (e.g., 'After brushing teeth'): ")
        then_part = input("What exactly will you do? (e.g., 'meditate for 2 minutes'): ")
        
        habit_plan = f"When {when_part}, then I will {then_part}."
        
        print(f"\n📋 Your habit plan: {habit_plan}")
        
        data = self.load_habits_data()
        if 'active_habits' not in data:
            data['active_habits'] = {}
        
        data['active_habits'][habit_id] = {
            'title': habit['title'],
            'when': when_part,
            'then': then_part,
            'full_plan': habit_plan,
            'start_date': datetime.now().isoformat(),
            'completions': [],
            'target_days': 66
        }
        
        self.save_habits_data(data)
        
        print("✅ Habit tracking started!")
        print("💡 Use 'om nicky habits' to track daily progress")
        print("🎯 Goal: Track for 66 days until it becomes automatic")

    def wolf_conversation(self):
        """Interactive conversation with your inner wolf"""
        print("🐺 Talk to Your Inner Wolf")
        print("=" * 25)
        print("Your inner wolf is trying to protect you.")
        print("Let's listen to what it's trying to say...")
        print()
        
        situation = input("What situation is making you feel anxious/worried/scared? ")
        print()
        
        print("🐺 Wolf says:")
        wolf_responses = [
            f"I'm worried about '{situation}' because I want to keep us safe!",
            f"This '{situation}' feels dangerous - what if something bad happens?",
            f"I don't like '{situation}' - it threatens our needs!",
            f"We need to be careful about '{situation}' - I'm just trying to protect us!"
        ]
        print(f"   {random.choice(wolf_responses)}")
        print()
        
        print("🤔 Let's understand what need the wolf is protecting:")
        print("1. Physical safety (health, security, survival)")
        print("2. Social belonging (friendship, love, acceptance)")
        print("3. Personal growth (learning, purpose, becoming better)")
        print("4. Other/combination")
        
        need_choice = input("\nWhich need feels most threatened? (1-4): ")
        
        needs_map = {
            '1': "physical safety and security",
            '2': "social belonging and connection", 
            '3': "personal growth and purpose",
            '4': "multiple important needs"
        }
        
        identified_need = needs_map.get(need_choice, "important needs")
        
        print(f"\n💡 Insight: Your wolf is protecting your need for {identified_need}.")
        print()
        print("🤝 Now let's collaborate with your wolf:")
        print("Instead of fighting the fear, let's work WITH it to meet this need.")
        print()
        
        experiment = input(f"What's one small experiment you could try to better meet your need for {identified_need}? ")
        
        print(f"\n✨ Great! Your wolf appreciates that you're listening.")
        print(f"🎯 Experiment: {experiment}")
        print()
        print("💭 Remember: Fear is not your enemy - it's a guard dog for your needs.")
        print("   The goal is to help your fear be a BETTER helper.")
        
        # Save the conversation
        wolf_data = self.load_wolf_conversations()
        wolf_data.append({
            'timestamp': datetime.now().isoformat(),
            'situation': situation,
            'identified_need': identified_need,
            'experiment': experiment
        })
        self.save_wolf_conversations(wolf_data)

    def load_wolf_conversations(self):
        """Load wolf conversation history"""
        try:
            with open(self.wolf_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_wolf_conversations(self, data):
        """Save wolf conversation history"""
        with open(self.wolf_file, 'w') as f:
            json.dump(data, f, indent=2)

    def habit_dashboard(self):
        """Show habit tracking dashboard"""
        data = self.load_habits_data()
        
        print("📊 Habit Tracking Dashboard")
        print("=" * 27)
        
        if 'active_habits' not in data or not data['active_habits']:
            print("No active habits yet!")
            print("💡 Use 'om nicky habits' to start tracking the 9 evidence-based habits")
            return
        
        for habit_id, habit_data in data['active_habits'].items():
            print(f"\n{habit_data['title']}")
            print(f"📋 Plan: {habit_data['full_plan']}")
            
            start_date = datetime.fromisoformat(habit_data['start_date'])
            days_since_start = (datetime.now() - start_date).days
            completions = len(habit_data['completions'])
            target_days = habit_data['target_days']
            
            print(f"📈 Progress: {completions}/{target_days} days ({completions/target_days*100:.1f}%)")
            print(f"⏰ Started: {days_since_start} days ago")
            
            # Show recent completions
            if habit_data['completions']:
                recent = habit_data['completions'][-7:]  # Last 7 days
                print(f"📅 Recent: {', '.join(recent[-5:])}")
            
            # Check if completed today
            today = datetime.now().strftime("%Y-%m-%d")
            if today not in habit_data['completions']:
                mark_done = input(f"Mark {habit_data['title']} as done today? (y/n): ").lower()
                if mark_done == 'y':
                    habit_data['completions'].append(today)
                    print("✅ Marked as complete!")
        
        self.save_habits_data(data)

    def daily_wolf_wisdom(self):
        """Show daily wisdom from the wolf"""
        print("💡 Daily Wolf Wisdom")
        print("=" * 20)
        
        wisdom = random.choice(self.wolf_wisdom)
        print(f"🐺 \"{wisdom}\"")
        print()
        
        # Add context based on the wisdom
        if "guard dog" in wisdom:
            print("💭 Your emotions are trying to protect you.")
            print("   Instead of fighting them, listen to what they're guarding.")
        elif "collaborate" in wisdom:
            print("💭 Healthy mental health isn't about eliminating negative emotions.")
            print("   It's about working WITH them as helpful signals.")
        elif "hardware" in wisdom:
            print("💭 Your physical health directly affects your mental health.")
            print("   Sleep, exercise, and nutrition are mental health tools!")
        elif "serotonin" in wisdom:
            print("💭 Your gut health affects your mood more than you might think.")
            print("   Taking care of your body helps your mind too.")
        
        print()
        print("🎯 How might this wisdom apply to your life today?")
        reflection = input("Your reflection: ")
        
        if reflection.strip():
            print(f"✨ Great insight: {reflection}")

    def om_integration_guide(self):
        """Show how Nicky Case habits integrate with om features"""
        print("🔗 Integration with om Features")
        print("=" * 30)
        print("Nicky Case's 9 habits work perfectly with om's existing tools!")
        print()
        
        integrations = {
            "😌 Meditation": {
                "nicky": "Observe your mind like a scientist",
                "om_commands": ["om meditate", "om breathe", "om qb"],
                "connection": "om's breathing exercises are perfect for meditation practice"
            },
            "📓 Journaling": {
                "nicky": "Write about emotions AND understand them",
                "om_commands": ["om journal", "om mood", "om qm"],
                "connection": "om's mood tracking includes journaling and reflection"
            },
            "😴 Sleep": {
                "nicky": "Sleep affects everything - heart, brain, mood",
                "om_commands": ["om sleep", "om insomnia", "om rest"],
                "connection": "om's sleep optimization uses 90-minute cycle science"
            },
            "🏃‍♀️ Exercise": {
                "nicky": "Exercise = natural antidepressant",
                "om_commands": ["om physical", "om stretch", "om qs"],
                "connection": "om's physical wellness includes mood-boosting movement"
            },
            "👯‍♂️ Social Connection": {
                "nicky": "High-quality relationships reduce death risk by 50%",
                "om_commands": ["om social", "om connect"],
                "connection": "om helps you maintain and build meaningful relationships"
            },
            "💭 Learning": {
                "nicky": "Push yourself to fullest human potential",
                "om_commands": ["om learn", "om articles"],
                "connection": "om's learning paths support continuous growth"
            }
        }
        
        for habit, info in integrations.items():
            print(f"{habit}")
            print(f"   🎯 Nicky's insight: {info['nicky']}")
            print(f"   💻 om commands: {', '.join(info['om_commands'])}")
            print(f"   🔗 Connection: {info['connection']}")
            print()
        
        print("💡 The beauty of om is that all these habits work together!")
        print("   Your mood data informs sleep recommendations.")
        print("   Your sleep quality affects your meditation practice.")
        print("   Your social connections support your learning goals.")
        print("   Everything is connected - just like Nicky Case teaches!")

def run(args=None):
    """Main entry point for Nicky Case guide"""
    guide = NickyCaseGuide()
    
    if not args:
        choice = guide.show_main_menu()
        args = [choice]
    
    if args[0] in ['1', 'guide', 'read']:
        guide.show_full_guide()
    elif args[0] in ['2', 'habits', '9']:
        guide.show_nine_habits()
    elif args[0] in ['3', 'wolf', 'talk']:
        guide.wolf_conversation()
    elif args[0] in ['4', 'dashboard', 'track']:
        guide.habit_dashboard()
    elif args[0] in ['5', 'wisdom', 'daily']:
        guide.daily_wolf_wisdom()
    elif args[0] in ['6', 'integration', 'om']:
        guide.om_integration_guide()
    else:
        print("Usage: om nicky [guide|habits|wolf|dashboard|wisdom|integration]")

if __name__ == "__main__":
    run()
