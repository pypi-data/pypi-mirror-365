#!/usr/bin/env python3
"""
CBT Toolkit - Cognitive Behavioral Therapy Tools
Inspired by MindShift CBT, Quirk, Sanvello, and Woebot

Features:
- Thought challenging and reframing
- Cognitive distortion identification
- Anxiety coping strategies
- Mood-thought connection tracking
- CBT exercises and worksheets
"""

import json
import os
from datetime import datetime, timedelta
import random

class CBTToolkit:
    def __init__(self):
        self.data_dir = os.path.expanduser("~/.om")
        os.makedirs(self.data_dir, exist_ok=True)
        self.thoughts_file = os.path.join(self.data_dir, "cbt_thoughts.json")
        self.exercises_file = os.path.join(self.data_dir, "cbt_exercises.json")
        
        # Cognitive distortions database
        self.distortions = {
            "all_or_nothing": {
                "name": "All-or-Nothing Thinking",
                "description": "Seeing things in black and white categories",
                "example": "If I'm not perfect, I'm a total failure",
                "challenge": "What would be a more balanced way to see this?"
            },
            "overgeneralization": {
                "name": "Overgeneralization", 
                "description": "Drawing broad conclusions from single events",
                "example": "I failed this test, I'll never succeed at anything",
                "challenge": "Is this one event really representative of everything?"
            },
            "mental_filter": {
                "name": "Mental Filter",
                "description": "Focusing only on negative details",
                "example": "The presentation went badly (ignoring positive feedback)",
                "challenge": "What positive aspects am I overlooking?"
            },
            "catastrophizing": {
                "name": "Catastrophizing",
                "description": "Expecting the worst possible outcome",
                "example": "If I make a mistake, I'll be fired and homeless",
                "challenge": "What's the most realistic outcome here?"
            },
            "mind_reading": {
                "name": "Mind Reading",
                "description": "Assuming you know what others are thinking",
                "example": "They think I'm stupid",
                "challenge": "What evidence do I have for this assumption?"
            },
            "fortune_telling": {
                "name": "Fortune Telling",
                "description": "Predicting negative outcomes without evidence",
                "example": "This will definitely go wrong",
                "challenge": "What other outcomes are possible?"
            },
            "emotional_reasoning": {
                "name": "Emotional Reasoning",
                "description": "Believing feelings reflect reality",
                "example": "I feel guilty, so I must have done something wrong",
                "challenge": "Are my feelings based on facts or assumptions?"
            },
            "should_statements": {
                "name": "Should Statements",
                "description": "Using rigid rules about how things 'should' be",
                "example": "I should never make mistakes",
                "challenge": "Is this expectation realistic and helpful?"
            },
            "labeling": {
                "name": "Labeling",
                "description": "Defining yourself or others with negative labels",
                "example": "I'm such an idiot",
                "challenge": "What would I say to a friend in this situation?"
            },
            "personalization": {
                "name": "Personalization",
                "description": "Taking responsibility for things outside your control",
                "example": "It's my fault the team project failed",
                "challenge": "What factors were actually within my control?"
            }
        }

    def load_thoughts(self):
        """Load saved thought records"""
        try:
            with open(self.thoughts_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_thought(self, thought_record):
        """Save a thought record"""
        thoughts = self.load_thoughts()
        thought_record['timestamp'] = datetime.now().isoformat()
        thoughts.append(thought_record)
        
        with open(self.thoughts_file, 'w') as f:
            json.dump(thoughts, f, indent=2)

    def thought_challenging_session(self):
        """Interactive thought challenging session"""
        print("🧠 CBT Thought Challenging Session")
        print("=" * 40)
        print("Let's examine a troubling thought together.\n")
        
        # Step 1: Identify the thought
        situation = input("What situation triggered this thought? ")
        thought = input("What specific thought went through your mind? ")
        emotion = input("What emotion did you feel? ")
        intensity = input("How intense was this emotion (1-10)? ")
        
        print(f"\n📝 Situation: {situation}")
        print(f"💭 Thought: {thought}")
        print(f"😔 Emotion: {emotion} (intensity: {intensity}/10)")
        
        # Step 2: Identify cognitive distortions
        print("\n🔍 Let's check for cognitive distortions...")
        self.identify_distortions(thought)
        
        # Step 3: Challenge the thought
        print("\n❓ Now let's challenge this thought:")
        self.challenge_thought(thought)
        
        # Step 4: Develop balanced thought
        balanced_thought = input("\nWhat would be a more balanced, realistic thought? ")
        new_emotion = input("How do you feel now with this new thought? ")
        new_intensity = input("What's the intensity now (1-10)? ")
        
        # Save the record
        thought_record = {
            'situation': situation,
            'original_thought': thought,
            'original_emotion': emotion,
            'original_intensity': int(intensity),
            'balanced_thought': balanced_thought,
            'new_emotion': new_emotion,
            'new_intensity': int(new_intensity)
        }
        
        self.save_thought(thought_record)
        
        print(f"\n✅ Great work! Your emotional intensity went from {intensity}/10 to {new_intensity}/10")
        print("💾 This thought record has been saved for future reference.")

    def identify_distortions(self, thought):
        """Help identify cognitive distortions in a thought"""
        print("\nCommon cognitive distortions to check for:")
        
        for key, distortion in self.distortions.items():
            print(f"\n🔸 {distortion['name']}")
            print(f"   {distortion['description']}")
            print(f"   Example: '{distortion['example']}'")
            
            response = input(f"   Does your thought show this pattern? (y/n): ").lower()
            if response == 'y':
                print(f"   💡 Challenge: {distortion['challenge']}")

    def challenge_thought(self, thought):
        """Guide through thought challenging questions"""
        questions = [
            "What evidence supports this thought?",
            "What evidence contradicts this thought?", 
            "What would you tell a friend having this thought?",
            "What's the worst that could realistically happen?",
            "What's the best that could happen?",
            "What's most likely to happen?",
            "How will this matter in 5 years?",
            "Are you taking responsibility for something outside your control?",
            "What would be a more balanced way to think about this?"
        ]
        
        for question in questions:
            print(f"\n❓ {question}")
            answer = input("Your answer: ")
            if answer.strip():
                print(f"   💭 Noted: {answer}")

    def anxiety_coping_strategies(self):
        """Provide anxiety-specific CBT strategies"""
        print("🌊 Anxiety Coping Strategies (CBT-based)")
        print("=" * 40)
        
        strategies = [
            {
                "name": "5-4-3-2-1 Grounding",
                "description": "Name 5 things you see, 4 you hear, 3 you touch, 2 you smell, 1 you taste"
            },
            {
                "name": "Worry Time",
                "description": "Schedule 15 minutes daily to worry, postpone anxious thoughts until then"
            },
            {
                "name": "Probability Estimation",
                "description": "Rate the actual likelihood (0-100%) of your feared outcome"
            },
            {
                "name": "Coping Statements",
                "description": "Prepare realistic, calming statements for anxious moments"
            },
            {
                "name": "Behavioral Experiments",
                "description": "Test anxious predictions through small, safe experiments"
            }
        ]
        
        for i, strategy in enumerate(strategies, 1):
            print(f"\n{i}. {strategy['name']}")
            print(f"   {strategy['description']}")
        
        choice = input(f"\nWhich strategy would you like to try? (1-{len(strategies)}): ")
        try:
            selected = strategies[int(choice) - 1]
            self.practice_strategy(selected)
        except (ValueError, IndexError):
            print("Invalid choice. Try again with 'om cbt anxiety'")

    def practice_strategy(self, strategy):
        """Guide through practicing a specific strategy"""
        print(f"\n🎯 Practicing: {strategy['name']}")
        print("=" * 30)
        
        if strategy['name'] == "5-4-3-2-1 Grounding":
            print("Let's ground yourself in the present moment:")
            input("Name 5 things you can see: ")
            input("Name 4 things you can hear: ")
            input("Name 3 things you can touch: ")
            input("Name 2 things you can smell: ")
            input("Name 1 thing you can taste: ")
            print("✅ Great! How do you feel now?")
            
        elif strategy['name'] == "Probability Estimation":
            worry = input("What are you worried about? ")
            probability = input("What's the realistic probability (0-100%) this will happen? ")
            print(f"You estimated {probability}% chance. Often our anxiety makes things seem more likely than they are.")
            
        elif strategy['name'] == "Coping Statements":
            print("Let's create some coping statements:")
            statements = []
            for i in range(3):
                stmt = input(f"Coping statement {i+1}: ")
                statements.append(stmt)
            print("\n💪 Your coping statements:")
            for stmt in statements:
                print(f"  • {stmt}")

    def mood_thought_tracker(self):
        """Track the connection between moods and thoughts"""
        print("📊 Mood-Thought Connection Tracker")
        print("=" * 35)
        
        mood = input("Current mood (1-10, 1=very low, 10=excellent): ")
        thoughts = input("What thoughts are going through your mind? ")
        
        # Analyze thought patterns
        negative_words = ['never', 'always', 'terrible', 'awful', 'disaster', 'hopeless', 'worthless']
        thought_lower = thoughts.lower()
        
        found_patterns = [word for word in negative_words if word in thought_lower]
        
        if found_patterns:
            print(f"\n🚨 I noticed some potentially unhelpful thinking patterns:")
            for pattern in found_patterns:
                print(f"  • '{pattern}' - this might be making you feel worse")
            print("\nWould you like to challenge these thoughts?")
            if input("(y/n): ").lower() == 'y':
                self.thought_challenging_session()
        else:
            print("\n✅ Your thoughts seem balanced. Keep it up!")

    def daily_cbt_exercise(self):
        """Provide a daily CBT exercise"""
        exercises = [
            {
                "name": "Gratitude + Reframe",
                "instruction": "Write 3 things you're grateful for, then reframe one negative thought from today"
            },
            {
                "name": "Evidence Gathering",
                "instruction": "Pick a worry and list evidence for AND against it happening"
            },
            {
                "name": "Behavioral Activation",
                "instruction": "Plan one small activity that usually brings you joy or accomplishment"
            },
            {
                "name": "Mindful Observation",
                "instruction": "Spend 5 minutes observing your thoughts without judgment"
            },
            {
                "name": "Values Check-in",
                "instruction": "Identify one action today that aligned with your core values"
            }
        ]
        
        today_exercise = exercises[datetime.now().day % len(exercises)]
        
        print("🌟 Today's CBT Exercise")
        print("=" * 25)
        print(f"📋 {today_exercise['name']}")
        print(f"🎯 {today_exercise['instruction']}")
        print("\nTake a few minutes to complete this exercise.")
        
        completed = input("\nDid you complete the exercise? (y/n): ").lower() == 'y'
        if completed:
            reflection = input("How did it go? Any insights? ")
            print("✅ Great work! Consistency in CBT practice builds mental resilience.")

def run(args=None):
    """Main entry point for CBT toolkit"""
    cbt = CBTToolkit()
    
    if not args:
        print("🧠 CBT Toolkit - Choose an option:")
        print("1. Thought challenging session")
        print("2. Anxiety coping strategies") 
        print("3. Mood-thought tracker")
        print("4. Daily CBT exercise")
        print("5. View past thought records")
        
        choice = input("\nEnter choice (1-5): ")
        args = [choice]
    
    if args[0] in ['1', 'challenge', 'thoughts']:
        cbt.thought_challenging_session()
    elif args[0] in ['2', 'anxiety', 'coping']:
        cbt.anxiety_coping_strategies()
    elif args[0] in ['3', 'mood', 'tracker']:
        cbt.mood_thought_tracker()
    elif args[0] in ['4', 'daily', 'exercise']:
        cbt.daily_cbt_exercise()
    elif args[0] in ['5', 'history', 'records']:
        thoughts = cbt.load_thoughts()
        if thoughts:
            print(f"\n📚 You have {len(thoughts)} thought records:")
            for i, record in enumerate(thoughts[-5:], 1):  # Show last 5
                date = datetime.fromisoformat(record['timestamp']).strftime("%Y-%m-%d")
                print(f"{i}. {date}: {record['original_thought'][:50]}...")
        else:
            print("No thought records yet. Start with 'om cbt challenge'")
    else:
        print("Usage: om cbt [challenge|anxiety|mood|daily|history]")

if __name__ == "__main__":
    run()
