"""
Depression symptoms support module for om
Evidence-based tools for managing depression symptoms
"""

import json
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional

DEPRESSION_FILE = os.path.expanduser("~/.om_depression.json")

class DepressionSupport:
    def __init__(self):
        self.depression_symptoms = {
            "mood": ["sad", "empty", "hopeless", "worthless", "guilty", "irritable"],
            "energy": ["fatigue", "low energy", "exhaustion", "sluggish"],
            "cognitive": ["difficulty concentrating", "indecisiveness", "memory problems", "negative thoughts"],
            "physical": ["sleep problems", "appetite changes", "aches and pains", "restlessness"],
            "behavioral": ["social withdrawal", "loss of interest", "reduced activity", "neglecting responsibilities"],
            "emotional": ["numbness", "overwhelming sadness", "anxiety", "anger", "despair"]
        }
        
        self.behavioral_activation_activities = {
            "self_care": [
                "Take a shower or bath",
                "Brush your teeth",
                "Get dressed in clean clothes",
                "Eat a nutritious meal",
                "Drink water",
                "Take vitamins",
                "Do skincare routine"
            ],
            "movement": [
                "Take a 5-minute walk",
                "Do gentle stretching",
                "Dance to one song",
                "Do jumping jacks for 30 seconds",
                "Practice yoga poses",
                "Walk up and down stairs",
                "Do desk exercises"
            ],
            "connection": [
                "Text a friend or family member",
                "Call someone you care about",
                "Write in a journal",
                "Pet an animal",
                "Smile at yourself in the mirror",
                "Send a kind message to someone",
                "Join an online community"
            ],
            "accomplishment": [
                "Make your bed",
                "Wash dishes",
                "Organize one small area",
                "Complete one work task",
                "Pay one bill",
                "Write a to-do list",
                "Finish something you started"
            ],
            "pleasure": [
                "Listen to favorite music",
                "Watch funny videos",
                "Look at photos you love",
                "Read a few pages of a book",
                "Do a puzzle or game",
                "Draw or color",
                "Watch the sunset/sunrise"
            ]
        }
        
        self.thought_patterns = {
            "all_or_nothing": {
                "name": "All-or-Nothing Thinking",
                "description": "Seeing things in black and white, no middle ground",
                "example": "I'm a complete failure",
                "challenge": "What would be a more balanced view? Are there shades of gray?"
            },
            "catastrophizing": {
                "name": "Catastrophizing",
                "description": "Expecting the worst possible outcome",
                "example": "This will be a disaster",
                "challenge": "What's the most realistic outcome? What would I tell a friend?"
            },
            "mind_reading": {
                "name": "Mind Reading",
                "description": "Assuming you know what others are thinking",
                "example": "They think I'm stupid",
                "challenge": "Do I have evidence for this? Could there be other explanations?"
            },
            "personalization": {
                "name": "Personalization",
                "description": "Blaming yourself for things outside your control",
                "example": "It's all my fault",
                "challenge": "What factors were outside my control? What would I tell a friend?"
            },
            "should_statements": {
                "name": "Should Statements",
                "description": "Rigid expectations about how things 'should' be",
                "example": "I should be able to handle this",
                "challenge": "Is this expectation realistic? What would be more flexible?"
            }
        }
    
    def depression_screening(self):
        """Simple depression symptom screening"""
        print("🔍 Depression Symptom Check-In")
        print("=" * 40)
        print("This is not a diagnostic tool, but can help you understand your symptoms.")
        print("If you're having thoughts of self-harm, please seek immediate professional help.")
        print()
        
        # PHQ-9 inspired questions (simplified)
        questions = [
            "Little interest or pleasure in doing things",
            "Feeling down, depressed, or hopeless",
            "Trouble falling/staying asleep or sleeping too much",
            "Feeling tired or having little energy",
            "Poor appetite or overeating",
            "Feeling bad about yourself or that you're a failure",
            "Trouble concentrating on things",
            "Moving or speaking slowly, or being restless",
            "Thoughts of being better off dead or hurting yourself"
        ]
        
        frequency_options = {
            "0": "Not at all",
            "1": "Several days", 
            "2": "More than half the days",
            "3": "Nearly every day"
        }
        
        print("Over the last 2 weeks, how often have you been bothered by:")
        print("0 = Not at all, 1 = Several days, 2 = More than half the days, 3 = Nearly every day")
        print()
        
        total_score = 0
        responses = []
        
        for i, question in enumerate(questions, 1):
            print(f"{i}. {question}")
            while True:
                response = input("   Your answer (0-3): ").strip()
                if response in frequency_options:
                    score = int(response)
                    total_score += score
                    responses.append(score)
                    print(f"   {frequency_options[response]}")
                    break
                else:
                    print("   Please enter 0, 1, 2, or 3")
            print()
        
        # Interpret results
        self._interpret_depression_screening(total_score, responses)
        
        # Save screening
        self._save_depression_screening(total_score, responses)
        
        return total_score
    
    def behavioral_activation(self):
        """Behavioral activation exercise"""
        print("🎯 Behavioral Activation")
        print("=" * 40)
        print("When we're depressed, we often withdraw from activities.")
        print("Behavioral activation helps by gradually re-engaging with meaningful activities.")
        print()
        
        # Current mood check
        print("First, let's check in with how you're feeling right now:")
        mood_before = input("Rate your mood 1-10 (1=very low, 10=great): ").strip()
        
        try:
            mood_before = int(mood_before)
            mood_before = max(1, min(10, mood_before))
        except ValueError:
            mood_before = 5
        
        print(f"Current mood: {mood_before}/10")
        print()
        
        # Choose activity category
        print("Choose an activity category:")
        categories = list(self.behavioral_activation_activities.keys())
        
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category.replace('_', ' ').title()}")
        
        print()
        choice = input("Choose category (1-5) or 'random': ").strip().lower()
        
        if choice == 'random':
            category = random.choice(categories)
        else:
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(categories):
                    category = categories[choice_idx]
                else:
                    category = random.choice(categories)
            except ValueError:
                category = random.choice(categories)
        
        # Select activity
        activities = self.behavioral_activation_activities[category]
        activity = random.choice(activities)
        
        print(f"🎯 Your activity: {activity}")
        print(f"Category: {category.replace('_', ' ').title()}")
        print()
        
        # Commitment and planning
        print("Let's make a plan:")
        when = input("When will you do this activity? ").strip()
        where = input("Where will you do this? ").strip()
        
        print(f"\n📋 Your Plan:")
        print(f"   What: {activity}")
        print(f"   When: {when}")
        print(f"   Where: {where}")
        print()
        
        # Predict mood change
        predicted_mood = input("Predict your mood after doing this (1-10): ").strip()
        
        try:
            predicted_mood = int(predicted_mood)
            predicted_mood = max(1, min(10, predicted_mood))
        except ValueError:
            predicted_mood = mood_before + 1
        
        print(f"Predicted mood: {predicted_mood}/10")
        print()
        
        # Encourage action
        print("💪 Remember:")
        print("• You don't have to feel motivated to take action")
        print("• Small steps count and build momentum")
        print("• Action often comes before motivation")
        print("• You're doing something positive for yourself")
        print()
        
        # Follow-up option
        followup = input("Would you like a reminder to check in after this activity? (y/n): ").strip().lower()
        
        # Log the activity plan
        self._log_behavioral_activation(activity, category, mood_before, predicted_mood, when, where)
        
        if followup == 'y':
            print("Great! Remember to use 'om depression --action followup' after completing the activity.")
    
    def thought_record(self):
        """Thought record for challenging negative thoughts"""
        print("📝 Thought Record")
        print("=" * 40)
        print("This exercise helps you examine and challenge negative thoughts.")
        print()
        
        # Identify the situation
        situation = input("What situation triggered difficult thoughts or feelings?\n> ").strip()
        
        if not situation:
            print("It's okay if you can't think of a specific situation right now.")
            return
        
        print(f"\nSituation: {situation}")
        print()
        
        # Identify emotions
        print("What emotions did you feel? (e.g., sad, angry, anxious)")
        emotions = input("> ").strip()
        
        # Rate intensity
        intensity = input("How intense were these emotions? (1-10): ").strip()
        
        try:
            intensity = int(intensity)
            intensity = max(1, min(10, intensity))
        except ValueError:
            intensity = 5
        
        print()
        
        # Identify automatic thoughts
        print("What thoughts went through your mind?")
        automatic_thought = input("> ").strip()
        
        if not automatic_thought:
            print("Take your time. What was going through your mind?")
            automatic_thought = input("> ").strip()
        
        print(f"\nAutomatic thought: \"{automatic_thought}\"")
        print()
        
        # Identify thinking pattern
        print("Does this thought match any of these patterns?")
        patterns = list(self.thought_patterns.keys())
        
        for i, pattern_key in enumerate(patterns, 1):
            pattern = self.thought_patterns[pattern_key]
            print(f"{i}. {pattern['name']}: {pattern['description']}")
        
        print()
        pattern_choice = input("Choose a pattern (1-5) or press Enter to skip: ").strip()
        
        identified_pattern = None
        if pattern_choice.isdigit():
            try:
                pattern_idx = int(pattern_choice) - 1
                if 0 <= pattern_idx < len(patterns):
                    identified_pattern = patterns[pattern_idx]
            except ValueError:
                pass
        
        # Challenge the thought
        print("\nLet's challenge this thought:")
        
        challenge_questions = [
            "What evidence supports this thought?",
            "What evidence contradicts this thought?",
            "What would you tell a friend having this thought?",
            "Is there a more balanced way to look at this?",
            "What's the worst that could happen? How would you cope?",
            "What's the best that could happen?",
            "What's most likely to happen?"
        ]
        
        responses = []
        for question in challenge_questions:
            print(f"\n❓ {question}")
            response = input("   ").strip()
            responses.append(response)
        
        # Create balanced thought
        print("\nBased on your responses, create a more balanced thought:")
        balanced_thought = input("> ").strip()
        
        # Rate new emotion intensity
        new_intensity = input("How intense are your emotions now? (1-10): ").strip()
        
        try:
            new_intensity = int(new_intensity)
            new_intensity = max(1, min(10, new_intensity))
        except ValueError:
            new_intensity = intensity
        
        # Summary
        print(f"\n📊 Thought Record Summary:")
        print(f"   Situation: {situation}")
        print(f"   Original thought: \"{automatic_thought}\"")
        if identified_pattern:
            pattern_info = self.thought_patterns[identified_pattern]
            print(f"   Thinking pattern: {pattern_info['name']}")
        print(f"   Balanced thought: \"{balanced_thought}\"")
        print(f"   Emotion intensity: {intensity}/10 → {new_intensity}/10")
        
        if new_intensity < intensity:
            print("   Great! Your emotions became less intense.")
        
        # Save thought record
        self._save_thought_record(situation, automatic_thought, balanced_thought, 
                                 emotions, intensity, new_intensity, identified_pattern)
    
    def pleasant_activities_scheduling(self):
        """Schedule pleasant activities to combat depression"""
        print("🌟 Pleasant Activities Scheduling")
        print("=" * 40)
        print("Depression often makes us lose interest in things we used to enjoy.")
        print("This exercise helps you reconnect with pleasant activities.")
        print()
        
        # Assess current pleasure and mastery
        print("Think about your recent activities:")
        pleasure_rating = input("How much pleasure/enjoyment have you felt lately? (1-10): ").strip()
        mastery_rating = input("How much sense of accomplishment have you felt? (1-10): ").strip()
        
        try:
            pleasure_rating = max(1, min(10, int(pleasure_rating)))
            mastery_rating = max(1, min(10, int(mastery_rating)))
        except ValueError:
            pleasure_rating = mastery_rating = 5
        
        print(f"\nCurrent levels:")
        print(f"   Pleasure: {pleasure_rating}/10")
        print(f"   Mastery: {mastery_rating}/10")
        print()
        
        # Generate activity suggestions
        if pleasure_rating < 5:
            print("Let's focus on adding more pleasurable activities:")
            suggested_activities = self.behavioral_activation_activities["pleasure"]
        elif mastery_rating < 5:
            print("Let's focus on activities that give you a sense of accomplishment:")
            suggested_activities = self.behavioral_activation_activities["accomplishment"]
        else:
            print("Let's maintain your current level with a mix of activities:")
            suggested_activities = (self.behavioral_activation_activities["pleasure"] + 
                                  self.behavioral_activation_activities["accomplishment"])
        
        # Show suggestions
        print("\nSuggested activities:")
        random.shuffle(suggested_activities)
        
        for i, activity in enumerate(suggested_activities[:5], 1):
            print(f"   {i}. {activity}")
        
        print()
        
        # Let user choose or add their own
        choice = input("Choose an activity (1-5) or describe your own: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= 5:
            chosen_activity = suggested_activities[int(choice) - 1]
        else:
            chosen_activity = choice if choice else suggested_activities[0]
        
        # Schedule the activity
        print(f"\n📅 Scheduling: {chosen_activity}")
        
        when = input("When will you do this? (be specific): ").strip()
        duration = input("How long will you spend on this? ").strip()
        
        # Predict ratings
        predicted_pleasure = input("Predict pleasure level after doing this (1-10): ").strip()
        predicted_mastery = input("Predict mastery/accomplishment level (1-10): ").strip()
        
        try:
            predicted_pleasure = max(1, min(10, int(predicted_pleasure)))
            predicted_mastery = max(1, min(10, int(predicted_mastery)))
        except ValueError:
            predicted_pleasure = pleasure_rating + 2
            predicted_mastery = mastery_rating + 2
        
        # Summary
        print(f"\n📋 Activity Plan:")
        print(f"   Activity: {chosen_activity}")
        print(f"   When: {when}")
        print(f"   Duration: {duration}")
        print(f"   Predicted pleasure: {predicted_pleasure}/10")
        print(f"   Predicted mastery: {predicted_mastery}/10")
        print()
        
        print("💡 Tips for success:")
        print("• Start small - even 5 minutes counts")
        print("• Focus on the process, not perfection")
        print("• Notice any positive feelings, however small")
        print("• Be patient with yourself")
        
        # Save activity plan
        self._save_activity_plan(chosen_activity, when, duration, 
                               predicted_pleasure, predicted_mastery)
    
    def depression_resources(self):
        """Provide depression resources and crisis information"""
        print("📚 Depression Resources & Support")
        print("=" * 40)
        
        print("🚨 CRISIS RESOURCES (if you're having thoughts of self-harm):")
        print("   • National Suicide Prevention Lifeline: 988")
        print("   • Crisis Text Line: Text HOME to 741741")
        print("   • Emergency Services: 911")
        print("   • International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/")
        print()
        
        print("🏥 PROFESSIONAL HELP:")
        print("   • Talk to your primary care doctor")
        print("   • Find a therapist: Psychology Today, BetterHelp, Talkspace")
        print("   • Consider medication evaluation with a psychiatrist")
        print("   • Look into support groups (NAMI, Depression and Bipolar Support Alliance)")
        print()
        
        print("📖 SELF-HELP RESOURCES:")
        print("   • Books: 'Feeling Good' by David Burns, 'The Depression Cure' by Stephen Ilardi")
        print("   • Apps: Headspace, Calm, MindShift, Sanvello")
        print("   • Websites: Centre for Clinical Interventions, MindTools")
        print()
        
        print("🏃‍♀️ LIFESTYLE FACTORS:")
        print("   • Regular exercise (even 10 minutes helps)")
        print("   • Consistent sleep schedule")
        print("   • Balanced nutrition")
        print("   • Social connection")
        print("   • Sunlight exposure")
        print("   • Limit alcohol and substances")
        print()
        
        print("💪 REMEMBER:")
        print("   • Depression is treatable")
        print("   • You're not alone")
        print("   • Small steps count")
        print("   • Recovery is possible")
        print("   • Seeking help is a sign of strength")
    
    def _interpret_depression_screening(self, total_score: int, responses: List[int]):
        """Interpret depression screening results"""
        print(f"📊 Screening Results:")
        print(f"Total score: {total_score}/27")
        print()
        
        if total_score <= 4:
            severity = "Minimal"
            recommendation = "Your symptoms appear minimal. Continue with self-care and monitoring."
        elif total_score <= 9:
            severity = "Mild"
            recommendation = "You may be experiencing mild depression symptoms. Consider self-help strategies and monitoring."
        elif total_score <= 14:
            severity = "Moderate"
            recommendation = "You may be experiencing moderate depression. Consider speaking with a healthcare provider."
        elif total_score <= 19:
            severity = "Moderately Severe"
            recommendation = "You may be experiencing moderately severe depression. Professional help is recommended."
        else:
            severity = "Severe"
            recommendation = "You may be experiencing severe depression. Please seek professional help promptly."
        
        print(f"Severity level: {severity}")
        print(f"Recommendation: {recommendation}")
        print()
        
        # Check for suicidal ideation (question 9)
        if responses[8] > 0:
            print("⚠️  IMPORTANT: You indicated thoughts of self-harm.")
            print("Please reach out for immediate support:")
            print("   • National Suicide Prevention Lifeline: 988")
            print("   • Crisis Text Line: Text HOME to 741741")
            print("   • Emergency Services: 911")
            print()
        
        print("Note: This is not a diagnostic tool. Please consult a healthcare provider for proper evaluation.")
    
    def _save_depression_screening(self, total_score: int, responses: List[int]):
        """Save depression screening results"""
        data = self._load_depression_data()
        
        screening = {
            "timestamp": datetime.now().isoformat(),
            "total_score": total_score,
            "responses": responses
        }
        
        data.setdefault('screenings', []).append(screening)
        self._save_depression_data(data)
    
    def _log_behavioral_activation(self, activity: str, category: str, mood_before: int, 
                                  predicted_mood: int, when: str, where: str):
        """Log behavioral activation activity"""
        data = self._load_depression_data()
        
        ba_log = {
            "timestamp": datetime.now().isoformat(),
            "activity": activity,
            "category": category,
            "mood_before": mood_before,
            "predicted_mood": predicted_mood,
            "when": when,
            "where": where,
            "completed": False
        }
        
        data.setdefault('behavioral_activation', []).append(ba_log)
        self._save_depression_data(data)
    
    def _save_thought_record(self, situation: str, automatic_thought: str, balanced_thought: str,
                           emotions: str, intensity: int, new_intensity: int, pattern: str):
        """Save thought record"""
        data = self._load_depression_data()
        
        thought_record = {
            "timestamp": datetime.now().isoformat(),
            "situation": situation,
            "automatic_thought": automatic_thought,
            "balanced_thought": balanced_thought,
            "emotions": emotions,
            "intensity": intensity,
            "new_intensity": new_intensity,
            "thinking_pattern": pattern
        }
        
        data.setdefault('thought_records', []).append(thought_record)
        self._save_depression_data(data)
    
    def _save_activity_plan(self, activity: str, when: str, duration: str,
                          predicted_pleasure: int, predicted_mastery: int):
        """Save pleasant activity plan"""
        data = self._load_depression_data()
        
        activity_plan = {
            "timestamp": datetime.now().isoformat(),
            "activity": activity,
            "when": when,
            "duration": duration,
            "predicted_pleasure": predicted_pleasure,
            "predicted_mastery": predicted_mastery,
            "completed": False
        }
        
        data.setdefault('activity_plans', []).append(activity_plan)
        self._save_depression_data(data)
    
    def _load_depression_data(self) -> Dict:
        """Load depression support data"""
        if not os.path.exists(DEPRESSION_FILE):
            return {}
        
        try:
            with open(DEPRESSION_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_depression_data(self, data: Dict):
        """Save depression support data"""
        try:
            with open(DEPRESSION_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save depression data: {e}")


def depression_command(action: str = "menu", **kwargs):
    """Main depression support command interface"""
    support = DepressionSupport()
    
    if action == "menu":
        print("🌧️ Depression Support Menu")
        print("=" * 40)
        print("1. Depression symptom screening")
        print("2. Behavioral activation")
        print("3. Thought record")
        print("4. Pleasant activities scheduling")
        print("5. Resources and crisis support")
        print()
        
        choice = input("Choose an option (1-5): ").strip()
        
        if choice == "1":
            support.depression_screening()
        elif choice == "2":
            support.behavioral_activation()
        elif choice == "3":
            support.thought_record()
        elif choice == "4":
            support.pleasant_activities_scheduling()
        elif choice == "5":
            support.depression_resources()
        else:
            print("Invalid choice.")
    
    elif action == "screening":
        support.depression_screening()
    elif action == "activation":
        support.behavioral_activation()
    elif action == "thoughts":
        support.thought_record()
    elif action == "activities":
        support.pleasant_activities_scheduling()
    elif action == "resources":
        support.depression_resources()
    else:
        print(f"Unknown depression action: {action}")
        print("Available actions: menu, screening, activation, thoughts, activities, resources")
