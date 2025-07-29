#!/usr/bin/env python3
"""
Positive Psychology Module
Inspired by Three Good Things, Happify, and positive psychology research

Features:
- Three Good Things daily practice
- Gratitude exercises with variety
- Strengths identification and development
- Positive emotion cultivation
- Resilience building activities
- Optimism training
"""

import json
import os
import random
from datetime import datetime, timedelta

class PositivePsychology:
    def __init__(self):
        self.data_dir = os.path.expanduser("~/.om")
        os.makedirs(self.data_dir, exist_ok=True)
        self.positive_data_file = os.path.join(self.data_dir, "positive_psychology.json")
        
        # Character strengths (VIA Survey categories)
        self.character_strengths = {
            "Wisdom": ["Creativity", "Curiosity", "Judgment", "Love of Learning", "Perspective"],
            "Courage": ["Bravery", "Perseverance", "Honesty", "Zest"],
            "Humanity": ["Love", "Kindness", "Social Intelligence"],
            "Justice": ["Teamwork", "Fairness", "Leadership"],
            "Temperance": ["Forgiveness", "Humility", "Prudence", "Self-Regulation"],
            "Transcendence": ["Appreciation of Beauty", "Gratitude", "Hope", "Humor", "Spirituality"]
        }
        
        # Positive emotion activities
        self.positive_activities = {
            "Joy": [
                "Dance to your favorite song",
                "Watch funny videos or comedy",
                "Spend time with loved ones",
                "Engage in a hobby you love",
                "Celebrate a small win"
            ],
            "Gratitude": [
                "Write a thank-you note",
                "Call someone to express appreciation",
                "Notice beauty in your environment",
                "Appreciate your body and health",
                "Reflect on lessons learned from challenges"
            ],
            "Serenity": [
                "Practice mindful breathing",
                "Spend time in nature",
                "Listen to calming music",
                "Take a warm bath",
                "Practice gentle yoga"
            ],
            "Interest": [
                "Learn something new",
                "Explore a new place",
                "Read about a fascinating topic",
                "Try a new recipe",
                "Start a creative project"
            ],
            "Hope": [
                "Set a meaningful goal",
                "Visualize your ideal future",
                "Make plans for something exciting",
                "Connect with your values",
                "Help someone else"
            ],
            "Pride": [
                "Acknowledge a recent accomplishment",
                "Share your success with others",
                "Reflect on your growth",
                "Use your strengths to help others",
                "Celebrate your unique qualities"
            ],
            "Amusement": [
                "Share jokes with friends",
                "Watch or read comedy",
                "Play games",
                "Be silly and playful",
                "Find humor in everyday situations"
            ],
            "Inspiration": [
                "Read about people you admire",
                "Watch inspiring videos",
                "Connect with your purpose",
                "Volunteer for a cause you care about",
                "Create something meaningful"
            ],
            "Awe": [
                "Look at the stars",
                "Appreciate art or music",
                "Contemplate nature's complexity",
                "Learn about scientific discoveries",
                "Reflect on human achievements"
            ],
            "Love": [
                "Express affection to loved ones",
                "Practice self-compassion",
                "Connect deeply with others",
                "Show kindness to strangers",
                "Appreciate relationships"
            ]
        }

    def load_positive_data(self):
        """Load positive psychology tracking data"""
        try:
            with open(self.positive_data_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "three_good_things": [],
                "strengths_activities": [],
                "positive_emotions": [],
                "gratitude_letters": [],
                "best_possible_self": []
            }

    def save_positive_data(self, data):
        """Save positive psychology data"""
        with open(self.positive_data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def three_good_things_practice(self):
        """Three Good Things daily practice"""
        print("✨ Three Good Things Practice")
        print("=" * 30)
        print("Research shows that writing down three good things that happened")
        print("each day can significantly increase happiness and life satisfaction.\n")
        
        data = self.load_positive_data()
        
        # Check if already done today
        today = datetime.now().strftime("%Y-%m-%d")
        today_entries = [entry for entry in data["three_good_things"] 
                        if entry.get("date") == today]
        
        if today_entries:
            print(f"✅ You already completed Three Good Things today!")
            print("Here's what you wrote:")
            for i, thing in enumerate(today_entries[0]["things"], 1):
                print(f"{i}. {thing['what']}")
                if thing.get('why'):
                    print(f"   Why: {thing['why']}")
            return
        
        print("Think about three things that went well today:")
        things = []
        
        for i in range(1, 4):
            print(f"\n{i}. What went well?")
            what = input("   Describe what happened: ")
            why = input("   Why do you think this good thing happened? ")
            
            things.append({
                "what": what,
                "why": why
            })
        
        # Save entry
        entry = {
            "date": today,
            "timestamp": datetime.now().isoformat(),
            "things": things
        }
        
        data["three_good_things"].append(entry)
        self.save_positive_data(data)
        
        print("\n🌟 Wonderful! You've completed today's Three Good Things practice.")
        print("Research shows this simple exercise can boost happiness for months!")

    def gratitude_letter_exercise(self):
        """Gratitude letter writing exercise"""
        print("💌 Gratitude Letter Exercise")
        print("=" * 28)
        print("Think of someone who has been kind to you but whom you've")
        print("never properly thanked. Write them a gratitude letter.\n")
        
        recipient = input("Who would you like to thank? ")
        print(f"\nWrite a letter to {recipient}:")
        print("(Press Enter twice when finished)\n")
        
        letter_lines = []
        while True:
            line = input()
            if line == "" and letter_lines and letter_lines[-1] == "":
                break
            letter_lines.append(line)
        
        letter_content = "\n".join(letter_lines[:-1])  # Remove last empty line
        
        data = self.load_positive_data()
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
            "recipient": recipient,
            "letter": letter_content
        }
        
        data["gratitude_letters"].append(entry)
        self.save_positive_data(data)
        
        print(f"\n✅ Gratitude letter saved!")
        print(f"💡 Consider sharing this with {recipient} - it could make their day!")
        
        deliver = input(f"\nWould you like to send/deliver this letter to {recipient}? (y/n): ")
        if deliver.lower() == 'y':
            print("📮 That's wonderful! Delivering gratitude letters has been shown")
            print("   to create lasting happiness for both sender and receiver.")

    def strengths_identification(self):
        """Help identify and develop character strengths"""
        print("💪 Character Strengths Identification")
        print("=" * 35)
        print("Character strengths are positive traits that energize you")
        print("and come naturally. Let's explore yours!\n")
        
        print("Here are the 24 character strengths organized by virtue:")
        
        for virtue, strengths in self.character_strengths.items():
            print(f"\n🔸 {virtue}:")
            for strength in strengths:
                print(f"   • {strength}")
        
        print(f"\nWhich 3-5 strengths resonate most with you?")
        print("(These should feel authentic and energizing)")
        
        top_strengths = []
        for i in range(1, 6):
            strength = input(f"{i}. Your strength: ").strip()
            if strength:
                top_strengths.append(strength)
            else:
                break
        
        if top_strengths:
            print(f"\n🌟 Your top character strengths:")
            for strength in top_strengths:
                print(f"   • {strength}")
            
            # Suggest strength-based activity
            print(f"\n💡 Strength-based activity suggestion:")
            print(f"Choose one of your strengths and find a new way to use it today.")
            print(f"Using strengths in novel ways increases happiness and life satisfaction!")
            
            # Save strengths
            data = self.load_positive_data()
            entry = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "timestamp": datetime.now().isoformat(),
                "identified_strengths": top_strengths
            }
            data["strengths_activities"].append(entry)
            self.save_positive_data(data)

    def positive_emotion_cultivation(self):
        """Cultivate specific positive emotions"""
        print("😊 Positive Emotion Cultivation")
        print("=" * 30)
        print("Which positive emotion would you like to cultivate today?\n")
        
        emotions = list(self.positive_activities.keys())
        for i, emotion in enumerate(emotions, 1):
            print(f"{i}. {emotion}")
        
        try:
            choice = int(input(f"\nChoose an emotion (1-{len(emotions)}): ")) - 1
            chosen_emotion = emotions[choice]
        except (ValueError, IndexError):
            chosen_emotion = random.choice(emotions)
            print(f"I'll choose {chosen_emotion} for you!")
        
        activities = self.positive_activities[chosen_emotion]
        
        print(f"\n✨ Cultivating {chosen_emotion}")
        print("=" * (13 + len(chosen_emotion)))
        print(f"Here are some activities to cultivate {chosen_emotion.lower()}:")
        
        for i, activity in enumerate(activities, 1):
            print(f"{i}. {activity}")
        
        print(f"\nWhich activity appeals to you most?")
        activity_choice = input("Choose one to try: ")
        
        print(f"\n🎯 Great choice! Take some time to {activity_choice.lower()}.")
        print(f"Notice how {chosen_emotion.lower()} feels in your body and mind.")
        
        # Track the activity
        data = self.load_positive_data()
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
            "target_emotion": chosen_emotion,
            "chosen_activity": activity_choice
        }
        data["positive_emotions"].append(entry)
        self.save_positive_data(data)

    def best_possible_self_exercise(self):
        """Best Possible Self visualization exercise"""
        print("🌟 Best Possible Self Exercise")
        print("=" * 30)
        print("Imagine yourself in the future, after everything has gone")
        print("as well as it possibly could. You have worked hard and")
        print("succeeded at accomplishing all your life goals.\n")
        
        print("Think about this best possible self in different areas:")
        
        areas = [
            "Personal relationships",
            "Career and work life", 
            "Health and fitness",
            "Personal growth and learning",
            "Hobbies and interests",
            "Community and contribution"
        ]
        
        visions = {}
        for area in areas:
            print(f"\n🔸 {area}:")
            vision = input(f"   Describe your best possible self in this area: ")
            if vision.strip():
                visions[area] = vision
        
        print(f"\n✨ Your Best Possible Self Vision:")
        print("=" * 35)
        for area, vision in visions.items():
            print(f"\n{area}:")
            print(f"  {vision}")
        
        # Identify next steps
        print(f"\n🎯 What's one small step you could take this week")
        print(f"   toward any aspect of your best possible self?")
        next_step = input("Your next step: ")
        
        # Save the exercise
        data = self.load_positive_data()
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
            "visions": visions,
            "next_step": next_step
        }
        data["best_possible_self"].append(entry)
        self.save_positive_data(data)
        
        print(f"\n💾 Your Best Possible Self vision has been saved!")
        print(f"💡 Regularly visualizing your best possible self increases")
        print(f"   optimism and motivation to achieve your goals.")

    def optimism_training(self):
        """Optimism and resilience building exercise"""
        print("🌈 Optimism Training")
        print("=" * 20)
        print("Let's practice thinking about challenges in a more optimistic way.\n")
        
        challenge = input("Describe a current challenge or setback you're facing: ")
        
        print(f"\nLet's reframe this challenge using the 3 P's of optimism:")
        print("(Personalization, Pervasiveness, Permanence)\n")
        
        # Personalization
        print("1. PERSONALIZATION - Is this entirely your fault?")
        print("   Pessimistic: 'It's all my fault'")
        print("   Optimistic: 'Multiple factors contributed to this'")
        personal = input("   What factors beyond your control contributed? ")
        
        # Pervasiveness  
        print("\n2. PERVASIVENESS - Does this affect everything in your life?")
        print("   Pessimistic: 'This ruins everything'")
        print("   Optimistic: 'This affects one area of my life'")
        pervasive = input("   What areas of your life are still going well? ")
        
        # Permanence
        print("\n3. PERMANENCE - Will this last forever?")
        print("   Pessimistic: 'This will never get better'")
        print("   Optimistic: 'This is temporary and changeable'")
        permanent = input("   How might this situation improve over time? ")
        
        print(f"\n✨ Optimistic Reframe:")
        print("=" * 20)
        print(f"Challenge: {challenge}")
        print(f"Contributing factors: {personal}")
        print(f"What's still working: {pervasive}")
        print(f"How it can improve: {permanent}")
        
        print(f"\n💪 This reframing helps build resilience and optimism!")

    def positive_psychology_dashboard(self):
        """Show positive psychology practice summary"""
        data = self.load_positive_data()
        
        print("📊 Positive Psychology Dashboard")
        print("=" * 32)
        
        # Three Good Things streak
        tgt_entries = data.get("three_good_things", [])
        if tgt_entries:
            last_entry = max(tgt_entries, key=lambda x: x["timestamp"])
            last_date = datetime.fromisoformat(last_entry["timestamp"]).date()
            days_since = (datetime.now().date() - last_date).days
            
            print(f"Three Good Things:")
            print(f"  Total entries: {len(tgt_entries)}")
            print(f"  Last entry: {days_since} days ago")
            
            if days_since == 0:
                print("  ✅ Completed today!")
            elif days_since == 1:
                print("  💡 Ready for today's entry")
            else:
                print("  💡 Time for a new entry!")
        
        # Other practices
        practices = [
            ("Gratitude Letters", "gratitude_letters"),
            ("Strengths Activities", "strengths_activities"), 
            ("Positive Emotions", "positive_emotions"),
            ("Best Possible Self", "best_possible_self")
        ]
        
        for name, key in practices:
            entries = data.get(key, [])
            if entries:
                print(f"\n{name}: {len(entries)} completed")
        
        print(f"\n🌟 Keep up the positive psychology practices!")
        print(f"   Research shows they create lasting happiness increases.")

def run(args=None):
    """Main entry point for positive psychology module"""
    pp = PositivePsychology()
    
    if not args:
        print("✨ Positive Psychology Practices")
        print("1. Three Good Things (daily)")
        print("2. Gratitude letter")
        print("3. Identify character strengths")
        print("4. Cultivate positive emotions")
        print("5. Best possible self")
        print("6. Optimism training")
        print("7. View dashboard")
        
        choice = input("\nChoose practice (1-7): ")
        args = [choice]
    
    if args[0] in ['1', 'three', 'good', 'things']:
        pp.three_good_things_practice()
    elif args[0] in ['2', 'gratitude', 'letter']:
        pp.gratitude_letter_exercise()
    elif args[0] in ['3', 'strengths', 'character']:
        pp.strengths_identification()
    elif args[0] in ['4', 'emotions', 'positive']:
        pp.positive_emotion_cultivation()
    elif args[0] in ['5', 'best', 'self', 'future']:
        pp.best_possible_self_exercise()
    elif args[0] in ['6', 'optimism', 'resilience']:
        pp.optimism_training()
    elif args[0] in ['7', 'dashboard', 'summary']:
        pp.positive_psychology_dashboard()
    else:
        print("Usage: om positive [three|gratitude|strengths|emotions|best|optimism|dashboard]")

if __name__ == "__main__":
    run()
