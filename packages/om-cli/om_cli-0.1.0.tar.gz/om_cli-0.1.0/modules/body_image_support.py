"""
Body image concerns support module for om
Evidence-based tools for improving body image and self-acceptance
"""

import json
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional

BODY_IMAGE_FILE = os.path.expanduser("~/.om_body_image.json")

class BodyImageSupport:
    def __init__(self):
        self.body_appreciation_statements = [
            "My body allows me to experience life",
            "My body is capable of amazing things",
            "I am grateful for what my body does for me",
            "My body deserves care and respect",
            "I appreciate my body's strength and resilience",
            "My body is unique and that's beautiful",
            "I honor my body by treating it with kindness",
            "My body carries me through each day",
            "I am more than my appearance",
            "My body is worthy of love and acceptance"
        ]
        
        self.body_functions = [
            "breathing and providing oxygen to every cell",
            "healing cuts, bruises, and injuries",
            "fighting off infections and illnesses",
            "allowing you to hug loved ones",
            "enabling you to taste delicious food",
            "letting you hear beautiful music",
            "giving you the ability to see colors and beauty",
            "allowing you to feel textures and temperatures",
            "enabling movement and physical activity",
            "processing emotions and experiences",
            "creating new cells and repairing damage",
            "maintaining balance and coordination"
        ]
        
        self.cognitive_distortions = {
            "all_or_nothing": {
                "name": "All-or-Nothing Thinking",
                "description": "Seeing body image in extremes (perfect or terrible)",
                "example": "I look completely awful today",
                "challenge": "What would be a more balanced view? Are there parts you appreciate?"
            },
            "mental_filter": {
                "name": "Mental Filter",
                "description": "Focusing only on perceived flaws while ignoring positives",
                "example": "All I can see is my stomach",
                "challenge": "What other parts of your body are you not noticing?"
            },
            "mind_reading": {
                "name": "Mind Reading",
                "description": "Assuming others are judging your appearance",
                "example": "Everyone is staring at my arms",
                "challenge": "Do you have evidence for this? What else might they be thinking?"
            },
            "fortune_telling": {
                "name": "Fortune Telling",
                "description": "Predicting negative outcomes based on appearance",
                "example": "No one will like me because of how I look",
                "challenge": "Is this prediction based on facts? What evidence contradicts this?"
            },
            "should_statements": {
                "name": "Should Statements",
                "description": "Rigid rules about how your body 'should' look",
                "example": "I should be thinner/more muscular",
                "challenge": "Says who? What would be more flexible and kind?"
            }
        }
        
        self.self_care_activities = {
            "physical": [
                "Take a relaxing bath or shower",
                "Apply moisturizer mindfully",
                "Do gentle stretching or yoga",
                "Get a massage or self-massage",
                "Wear clothes that feel comfortable",
                "Practice good posture",
                "Engage in enjoyable physical activity"
            ],
            "emotional": [
                "Practice self-compassion",
                "Write yourself a kind letter",
                "Practice gratitude for your body",
                "Engage in activities you enjoy",
                "Spend time with supportive people",
                "Practice mindfulness",
                "Challenge negative self-talk"
            ],
            "social": [
                "Surround yourself with body-positive people",
                "Limit exposure to triggering media",
                "Engage in meaningful conversations",
                "Practice setting boundaries",
                "Seek support when needed",
                "Share your struggles with trusted friends",
                "Participate in body-positive communities"
            ]
        }
    
    def body_image_assessment(self):
        """Assess current body image concerns"""
        print("🪞 Body Image Assessment")
        print("=" * 40)
        print("This assessment helps identify your relationship with your body.")
        print("Answer honestly - this is for your own understanding.")
        print()
        
        # Body satisfaction questions
        questions = [
            "I am satisfied with my overall appearance",
            "I feel comfortable in my own skin",
            "I appreciate what my body can do",
            "I avoid looking at myself in mirrors",
            "I compare my body to others frequently",
            "I feel anxious about how others see my body",
            "I engage in behaviors to hide my body",
            "My mood is often affected by how I think I look",
            "I avoid certain activities because of my appearance",
            "I spend a lot of time thinking about my body"
        ]
        
        scale_options = {
            "1": "Never",
            "2": "Rarely", 
            "3": "Sometimes",
            "4": "Often",
            "5": "Always"
        }
        
        print("Rate how often each statement applies to you:")
        print("1 = Never, 2 = Rarely, 3 = Sometimes, 4 = Often, 5 = Always")
        print()
        
        responses = []
        total_score = 0
        
        for i, question in enumerate(questions, 1):
            print(f"{i}. {question}")
            while True:
                response = input("   Your answer (1-5): ").strip()
                if response in scale_options:
                    score = int(response)
                    # Reverse score positive items (1, 2, 3)
                    if i <= 3:
                        score = 6 - score
                    responses.append(score)
                    total_score += score
                    print(f"   {scale_options[response]}")
                    break
                else:
                    print("   Please enter 1, 2, 3, 4, or 5")
            print()
        
        # Body areas of concern
        print("Which body areas cause you the most concern? (check all that apply)")
        body_areas = [
            "face", "hair", "arms", "hands", "chest/breasts", "stomach/abdomen",
            "hips", "thighs", "legs", "feet", "overall weight", "overall shape",
            "skin", "height", "muscle tone", "none"
        ]
        
        concern_areas = []
        for area in body_areas:
            response = input(f"   {area}? (y/n): ").strip().lower()
            if response == 'y':
                concern_areas.append(area)
        
        # Interpret results
        self._interpret_body_image_assessment(total_score, concern_areas)
        
        # Save assessment
        self._save_body_image_assessment(total_score, responses, concern_areas)
        
        return total_score
    
    def body_appreciation_exercise(self):
        """Practice body appreciation and gratitude"""
        print("💝 Body Appreciation Exercise")
        print("=" * 40)
        print("This exercise helps shift focus from appearance to function and appreciation.")
        print()
        
        # Random body function appreciation
        functions = random.sample(self.body_functions, 3)
        
        print("🌟 Let's appreciate what your body does for you:")
        print("Right now, your body is:")
        
        for function in functions:
            print(f"   • {function}")
        
        print()
        input("Take a moment to really appreciate these functions... Press Enter to continue.")
        print()
        
        # Guided appreciation
        print("🤲 Now let's practice specific body appreciation:")
        
        appreciation_prompts = [
            "Place your hand on your heart. Feel it beating. Thank your heart for working tirelessly for you.",
            "Take a deep breath. Thank your lungs for providing oxygen to every cell in your body.",
            "Look at your hands. Thank them for all they help you accomplish each day.",
            "Think about your legs and feet. Thank them for carrying you through life.",
            "Consider your brain. Thank it for processing thoughts, memories, and experiences.",
            "Appreciate your senses. Thank them for allowing you to experience the world."
        ]
        
        for prompt in appreciation_prompts:
            print(f"💭 {prompt}")
            input("   Take your time with this... Press Enter for the next one.")
            print()
        
        # Personal appreciation
        print("✍️ Now write your own body appreciation:")
        personal_appreciation = input("I appreciate my body because... ").strip()
        
        if personal_appreciation:
            print(f"\n🌟 Beautiful: \"I appreciate my body because {personal_appreciation}\"")
            print("Remember this appreciation when negative thoughts arise.")
        
        # Daily appreciation suggestion
        daily_statement = random.choice(self.body_appreciation_statements)
        print(f"\n📝 Today's body appreciation statement:")
        print(f"   \"{daily_statement}\"")
        print("Consider repeating this throughout the day.")
        
        # Save appreciation
        self._save_body_appreciation(personal_appreciation, daily_statement)
    
    def mirror_work_exercise(self):
        """Guided mirror work for body acceptance"""
        print("🪞 Mirror Work Exercise")
        print("=" * 40)
        print("This exercise helps develop a more compassionate relationship with your reflection.")
        print("You'll need access to a mirror for this exercise.")
        print()
        
        has_mirror = input("Do you have access to a mirror right now? (y/n): ").strip().lower()
        
        if has_mirror != 'y':
            print("That's okay! You can do this exercise later when you have access to a mirror.")
            print("For now, let's practice the mental aspects.")
        
        print("\n🌱 Mirror Work Steps:")
        print()
        
        # Preparation
        print("1️⃣ Preparation:")
        print("   • Stand or sit comfortably in front of the mirror")
        print("   • Take three deep breaths")
        print("   • Set an intention to be kind to yourself")
        print("   • Remember: this is practice, not judgment")
        
        input("\nPress Enter when you're ready...")
        print()
        
        # Looking with compassion
        print("2️⃣ Compassionate Looking:")
        print("   • Look at your whole self, not just specific parts")
        print("   • Notice any urge to focus on 'flaws' - that's normal")
        print("   • Gently redirect attention to your whole being")
        print("   • Breathe deeply and relax your shoulders")
        
        input("\nTake your time with this step... Press Enter to continue.")
        print()
        
        # Positive affirmations
        print("3️⃣ Positive Affirmations:")
        print("   Look at yourself and say (out loud if possible):")
        
        affirmations = [
            "I am worthy of love and respect",
            "My body is doing its best for me",
            "I choose to speak kindly to myself",
            "I am more than my appearance",
            "I deserve compassion, especially from myself"
        ]
        
        for affirmation in affirmations:
            print(f"   • \"{affirmation}\"")
            input("     Say this and let it sink in... Press Enter for the next one.")
        
        print()
        
        # Gratitude practice
        print("4️⃣ Gratitude Practice:")
        print("   Look at different parts of your body and thank them:")
        
        gratitude_prompts = [
            "Thank your eyes for allowing you to see beauty",
            "Thank your mouth for letting you taste and speak",
            "Thank your arms for hugging and helping",
            "Thank your legs for carrying you",
            "Thank your whole body for being your home"
        ]
        
        for prompt in gratitude_prompts:
            print(f"   • {prompt}")
            input("     Take a moment for gratitude... Press Enter to continue.")
        
        print()
        
        # Closing
        print("5️⃣ Closing:")
        print("   • Take three more deep breaths")
        print("   • Place your hand on your heart")
        print("   • Say: 'I am learning to love and accept myself'")
        print("   • Thank yourself for doing this brave work")
        
        input("\nPress Enter when you've completed the exercise...")
        
        # Reflection
        print("\n💭 Reflection:")
        feeling = input("How did that feel? What did you notice? ").strip()
        
        if feeling:
            print(f"Thank you for sharing: {feeling}")
            print("Remember, mirror work gets easier with practice.")
        
        print("\n💡 Mirror Work Tips:")
        print("• Start with short sessions (1-2 minutes)")
        print("• Practice regularly, even when it feels difficult")
        print("• Be patient with yourself - this is challenging work")
        print("• Focus on function over form when possible")
        print("• Celebrate small improvements in self-compassion")
        
        # Save mirror work session
        self._save_mirror_work(feeling)
    
    def body_image_thought_challenging(self):
        """Challenge negative body image thoughts"""
        print("🧠 Body Image Thought Challenging")
        print("=" * 40)
        print("Let's examine and challenge a negative thought about your body.")
        print()
        
        # Identify the thought
        negative_thought = input("What negative thought about your body is bothering you? ").strip()
        
        if not negative_thought:
            print("Take your time. What critical thought about your appearance comes up?")
            negative_thought = input("> ").strip()
        
        if not negative_thought:
            print("It's okay if you can't think of something specific right now.")
            return
        
        print(f"\nNegative thought: \"{negative_thought}\"")
        print()
        
        # Identify thinking pattern
        print("Does this thought match any of these patterns?")
        patterns = list(self.cognitive_distortions.keys())
        
        for i, pattern_key in enumerate(patterns, 1):
            pattern = self.cognitive_distortions[pattern_key]
            print(f"{i}. {pattern['name']}: {pattern['description']}")
        
        print()
        pattern_choice = input("Choose a pattern (1-5) or press Enter to skip: ").strip()
        
        identified_pattern = None
        if pattern_choice.isdigit():
            try:
                pattern_idx = int(pattern_choice) - 1
                if 0 <= pattern_idx < len(patterns):
                    identified_pattern = patterns[pattern_idx]
                    pattern_info = self.cognitive_distortions[identified_pattern]
                    print(f"\nIdentified pattern: {pattern_info['name']}")
                    print(f"Challenge: {pattern_info['challenge']}")
            except ValueError:
                pass
        
        print()
        
        # Challenge questions
        print("Let's challenge this thought:")
        
        challenge_questions = [
            "Is this thought based on facts or feelings?",
            "Would you say this to a friend about their body?",
            "What would a loving friend say to you about this?",
            "How does this thought affect your mood and behavior?",
            "What evidence contradicts this thought?",
            "Is this thought helping or hurting you?",
            "What would you think if you weren't focused on appearance?",
            "How important will this be in 5 years?"
        ]
        
        responses = []
        for question in challenge_questions:
            print(f"\n❓ {question}")
            response = input("   ").strip()
            responses.append(response)
        
        # Create balanced thought
        print("\nBased on your responses, create a more balanced, compassionate thought:")
        balanced_thought = input("> ").strip()
        
        if balanced_thought:
            print(f"\n🌟 Excellent work! You've reframed:")
            print(f"   From: \"{negative_thought}\"")
            print(f"   To: \"{balanced_thought}\"")
            print("\nPractice this balanced thought when the negative one returns.")
        
        # Coping strategy
        print("\n💪 Choose a coping strategy for when this thought returns:")
        strategies = [
            "Practice the balanced thought you just created",
            "Do a body appreciation exercise",
            "Engage in a self-care activity",
            "Talk to a supportive friend",
            "Focus on what your body can do",
            "Practice mindfulness and let the thought pass"
        ]
        
        for i, strategy in enumerate(strategies, 1):
            print(f"{i}. {strategy}")
        
        strategy_choice = input("\nChoose a strategy (1-6): ").strip()
        chosen_strategy = None
        
        try:
            strategy_idx = int(strategy_choice) - 1
            if 0 <= strategy_idx < len(strategies):
                chosen_strategy = strategies[strategy_idx]
                print(f"Great choice: {chosen_strategy}")
        except ValueError:
            pass
        
        # Save thought challenge
        self._save_thought_challenge(negative_thought, balanced_thought, 
                                   identified_pattern, chosen_strategy)
    
    def body_positive_activities(self):
        """Suggest body-positive activities"""
        print("🌈 Body-Positive Activities")
        print("=" * 40)
        print("These activities help build a healthier relationship with your body.")
        print()
        
        # Current mood check
        mood = input("How are you feeling about your body right now? (1-10, 10=very positive): ").strip()
        
        try:
            mood = max(1, min(10, int(mood)))
        except ValueError:
            mood = 5
        
        print(f"Current body image mood: {mood}/10")
        print()
        
        # Suggest activities based on mood
        if mood <= 3:
            print("🤗 Gentle activities for difficult body image days:")
            suggested_activities = self.self_care_activities["emotional"][:3]
        elif mood <= 6:
            print("🌱 Nurturing activities to improve body relationship:")
            suggested_activities = (self.self_care_activities["physical"][:2] + 
                                  self.self_care_activities["emotional"][:2])
        else:
            print("✨ Activities to maintain positive body image:")
            suggested_activities = (self.self_care_activities["physical"][:2] + 
                                  self.self_care_activities["social"][:2])
        
        print()
        for i, activity in enumerate(suggested_activities, 1):
            print(f"{i}. {activity}")
        
        print()
        
        # Let user choose activity
        choice = input("Choose an activity (number) or describe your own: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(suggested_activities):
            chosen_activity = suggested_activities[int(choice) - 1]
        else:
            chosen_activity = choice if choice else suggested_activities[0]
        
        print(f"\n🎯 Your chosen activity: {chosen_activity}")
        
        # Plan the activity
        when = input("When will you do this activity? ").strip()
        
        print(f"\n📅 Activity Plan:")
        print(f"   Activity: {chosen_activity}")
        print(f"   When: {when}")
        
        print("\n💡 Remember:")
        print("• The goal is self-care, not self-improvement")
        print("• Focus on how activities make you feel, not how they make you look")
        print("• Be gentle and patient with yourself")
        print("• Celebrate small acts of self-compassion")
        
        # Save activity plan
        self._save_activity_plan(chosen_activity, when, mood)
    
    def _interpret_body_image_assessment(self, total_score: int, concern_areas: List[str]):
        """Interpret body image assessment results"""
        print(f"📊 Body Image Assessment Results:")
        print(f"Total score: {total_score}/50")
        print()
        
        if total_score <= 20:
            severity = "Low concern"
            recommendation = "You seem to have a relatively positive body image. Continue with self-care practices."
        elif total_score <= 30:
            severity = "Moderate concern"
            recommendation = "You may benefit from body image improvement techniques and self-compassion practices."
        elif total_score <= 40:
            severity = "High concern"
            recommendation = "Body image concerns may be significantly impacting you. Consider professional support."
        else:
            severity = "Very high concern"
            recommendation = "Body image concerns appear severe. Professional help is strongly recommended."
        
        print(f"Concern level: {severity}")
        print(f"Recommendation: {recommendation}")
        print()
        
        if concern_areas and "none" not in concern_areas:
            print(f"Areas of concern: {', '.join(concern_areas)}")
            print("Remember: These concerns are common and you're not alone.")
        
        print("\n💡 Helpful techniques for you:")
        if total_score <= 25:
            print("   • Body appreciation exercises")
            print("   • Mindful self-care activities")
        else:
            print("   • Thought challenging for body image")
            print("   • Mirror work exercises")
            print("   • Professional counseling consideration")
        
        print("\nNote: This assessment is for self-understanding, not diagnosis.")
    
    def _save_body_image_assessment(self, total_score: int, responses: List[int], concern_areas: List[str]):
        """Save body image assessment"""
        data = self._load_body_image_data()
        
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "total_score": total_score,
            "responses": responses,
            "concern_areas": concern_areas
        }
        
        data.setdefault('assessments', []).append(assessment)
        self._save_body_image_data(data)
    
    def _save_body_appreciation(self, personal_appreciation: str, daily_statement: str):
        """Save body appreciation exercise"""
        data = self._load_body_image_data()
        
        appreciation = {
            "timestamp": datetime.now().isoformat(),
            "personal_appreciation": personal_appreciation,
            "daily_statement": daily_statement
        }
        
        data.setdefault('appreciations', []).append(appreciation)
        self._save_body_image_data(data)
    
    def _save_mirror_work(self, reflection: str):
        """Save mirror work session"""
        data = self._load_body_image_data()
        
        mirror_work = {
            "timestamp": datetime.now().isoformat(),
            "reflection": reflection
        }
        
        data.setdefault('mirror_work', []).append(mirror_work)
        self._save_body_image_data(data)
    
    def _save_thought_challenge(self, negative_thought: str, balanced_thought: str,
                              pattern: str, strategy: str):
        """Save thought challenging session"""
        data = self._load_body_image_data()
        
        thought_challenge = {
            "timestamp": datetime.now().isoformat(),
            "negative_thought": negative_thought,
            "balanced_thought": balanced_thought,
            "thinking_pattern": pattern,
            "coping_strategy": strategy
        }
        
        data.setdefault('thought_challenges', []).append(thought_challenge)
        self._save_body_image_data(data)
    
    def _save_activity_plan(self, activity: str, when: str, mood: int):
        """Save body-positive activity plan"""
        data = self._load_body_image_data()
        
        activity_plan = {
            "timestamp": datetime.now().isoformat(),
            "activity": activity,
            "when": when,
            "mood_before": mood
        }
        
        data.setdefault('activity_plans', []).append(activity_plan)
        self._save_body_image_data(data)
    
    def _load_body_image_data(self) -> Dict:
        """Load body image support data"""
        if not os.path.exists(BODY_IMAGE_FILE):
            return {}
        
        try:
            with open(BODY_IMAGE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_body_image_data(self, data: Dict):
        """Save body image support data"""
        try:
            with open(BODY_IMAGE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save body image data: {e}")


def body_image_command(action: str = "menu", **kwargs):
    """Main body image support command interface"""
    support = BodyImageSupport()
    
    if action == "menu":
        print("🪞 Body Image Support Menu")
        print("=" * 40)
        print("1. Body image assessment")
        print("2. Body appreciation exercise")
        print("3. Mirror work exercise")
        print("4. Thought challenging")
        print("5. Body-positive activities")
        print()
        
        choice = input("Choose an option (1-5): ").strip()
        
        if choice == "1":
            support.body_image_assessment()
        elif choice == "2":
            support.body_appreciation_exercise()
        elif choice == "3":
            support.mirror_work_exercise()
        elif choice == "4":
            support.body_image_thought_challenging()
        elif choice == "5":
            support.body_positive_activities()
        else:
            print("Invalid choice.")
    
    elif action == "assessment":
        support.body_image_assessment()
    elif action == "appreciation":
        support.body_appreciation_exercise()
    elif action == "mirror":
        support.mirror_work_exercise()
    elif action == "thoughts":
        support.body_image_thought_challenging()
    elif action == "activities":
        support.body_positive_activities()
    else:
        print(f"Unknown body image action: {action}")
        print("Available actions: menu, assessment, appreciation, mirror, thoughts, activities")
