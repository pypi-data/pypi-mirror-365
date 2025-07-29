#!/usr/bin/env python3
"""
AI Mental Health Companion
Inspired by Woebot, Wysa, EmoBay, and Youper

Features:
- 24/7 conversational support
- Mood-based responses
- Crisis detection and response
- CBT-informed conversations
- Personalized check-ins
- Learning from user patterns
"""

import json
import os
import random
from datetime import datetime, timedelta
import re

class AICompanion:
    def __init__(self):
        self.data_dir = os.path.expanduser("~/.om")
        os.makedirs(self.data_dir, exist_ok=True)
        self.conversations_file = os.path.join(self.data_dir, "ai_conversations.json")
        self.user_profile_file = os.path.join(self.data_dir, "ai_user_profile.json")
        
        # Crisis keywords for detection
        self.crisis_keywords = [
            'suicide', 'kill myself', 'end it all', 'not worth living', 
            'better off dead', 'hurt myself', 'self harm', 'hopeless',
            'can\'t go on', 'want to die', 'no point', 'give up'
        ]
        
        # Mood-based response templates
        self.responses = {
            'greeting': [
                "Hello! I'm here to listen and support you. How are you feeling today?",
                "Hi there! What's on your mind right now?",
                "Good to see you! How has your day been treating you?",
                "Welcome back! I'm here whenever you need to talk."
            ],
            'low_mood': [
                "I hear that you're going through a tough time. That takes courage to share.",
                "It sounds like things feel heavy right now. You're not alone in this.",
                "I'm sorry you're struggling. What's been the hardest part of your day?",
                "Thank you for trusting me with how you're feeling. Let's work through this together."
            ],
            'anxiety': [
                "Anxiety can feel overwhelming. Let's take this one step at a time.",
                "I notice you're feeling anxious. What thoughts are racing through your mind?",
                "Anxiety is your mind trying to protect you, but sometimes it goes overboard. Let's examine this together.",
                "When anxiety hits, grounding can help. Can you name 3 things you can see right now?"
            ],
            'positive': [
                "It's wonderful to hear you're doing well! What's contributing to these good feelings?",
                "I love hearing positive updates! What's been the highlight of your day?",
                "That's great news! How can we build on this positive momentum?",
                "Your positive energy is contagious! What's working well for you right now?"
            ],
            'neutral': [
                "Thanks for checking in. Sometimes neutral is perfectly okay. What's on your mind?",
                "I appreciate you sharing where you're at. What would make today feel more meaningful?",
                "Neutral days are part of life's rhythm. Is there anything you'd like to explore?",
                "How are you taking care of yourself today?"
            ]
        }
        
        # CBT-informed questions
        self.cbt_questions = [
            "What evidence do you have for that thought?",
            "How would you advise a friend in this situation?",
            "What's the worst that could realistically happen?",
            "Are you taking responsibility for something outside your control?",
            "What would be a more balanced way to see this?",
            "How will this matter in a week? A month? A year?",
            "What are you telling yourself about this situation?",
            "What would need to change for you to feel differently about this?"
        ]

    def load_conversations(self):
        """Load conversation history"""
        try:
            with open(self.conversations_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_conversation(self, user_input, ai_response, mood=None, crisis_detected=False):
        """Save conversation exchange"""
        conversations = self.load_conversations()
        
        exchange = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'ai_response': ai_response,
            'mood': mood,
            'crisis_detected': crisis_detected
        }
        
        conversations.append(exchange)
        
        # Keep only last 100 conversations for privacy
        if len(conversations) > 100:
            conversations = conversations[-100:]
        
        with open(self.conversations_file, 'w') as f:
            json.dump(conversations, f, indent=2)

    def load_user_profile(self):
        """Load user profile and preferences"""
        try:
            with open(self.user_profile_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'name': None,
                'preferred_coping_strategies': [],
                'common_triggers': [],
                'positive_activities': [],
                'last_checkin': None
            }

    def update_user_profile(self, updates):
        """Update user profile"""
        profile = self.load_user_profile()
        profile.update(updates)
        
        with open(self.user_profile_file, 'w') as f:
            json.dump(profile, f, indent=2)

    def detect_crisis(self, text):
        """Detect crisis language in user input"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.crisis_keywords)

    def crisis_response(self):
        """Provide crisis support response"""
        print("\n🚨 CRISIS SUPPORT")
        print("=" * 30)
        print("I'm concerned about what you've shared. Your safety is the top priority.")
        print("\n🆘 IMMEDIATE HELP:")
        print("• National Suicide Prevention Lifeline: 988")
        print("• Crisis Text Line: Text HOME to 741741")
        print("• Emergency Services: 911")
        print("\n💙 You matter. You are not alone. Help is available.")
        print("Please reach out to one of these resources right now.")
        
        return "I've provided crisis resources above. Please use them - you deserve support and care."

    def analyze_mood_from_text(self, text):
        """Simple mood analysis from text"""
        text_lower = text.lower()
        
        # Crisis check first
        if self.detect_crisis(text):
            return 'crisis'
        
        # Positive indicators
        positive_words = ['good', 'great', 'happy', 'excited', 'wonderful', 'amazing', 'fantastic', 'joy', 'love']
        if any(word in text_lower for word in positive_words):
            return 'positive'
        
        # Anxiety indicators  
        anxiety_words = ['anxious', 'worried', 'nervous', 'panic', 'stress', 'overwhelmed', 'racing thoughts']
        if any(word in text_lower for word in anxiety_words):
            return 'anxiety'
        
        # Low mood indicators
        low_mood_words = ['sad', 'depressed', 'down', 'terrible', 'awful', 'hopeless', 'empty', 'numb']
        if any(word in text_lower for word in low_mood_words):
            return 'low_mood'
        
        return 'neutral'

    def generate_response(self, user_input, mood):
        """Generate contextual AI response"""
        if mood == 'crisis':
            return self.crisis_response()
        
        # Get base response for mood
        base_responses = self.responses.get(mood, self.responses['neutral'])
        response = random.choice(base_responses)
        
        # Add follow-up based on context
        if mood == 'anxiety':
            response += "\n\n" + random.choice([
                "Would you like to try a quick breathing exercise?",
                "Sometimes it helps to challenge anxious thoughts. What's the worst-case scenario you're imagining?",
                "Let's ground you in the present moment. What are 3 things you can see right now?"
            ])
        elif mood == 'low_mood':
            response += "\n\n" + random.choice([
                "What's one small thing that usually brings you comfort?",
                "Have you been able to take care of your basic needs today - food, water, rest?",
                "Sometimes when we're down, our thoughts become very harsh. What are you telling yourself right now?"
            ])
        elif mood == 'positive':
            response += "\n\n" + random.choice([
                "I'd love to hear more about what's going well!",
                "How can you carry this positive energy forward?",
                "What made the biggest difference in feeling good today?"
            ])
        
        return response

    def personalized_checkin(self):
        """Personalized check-in based on user history"""
        profile = self.load_user_profile()
        conversations = self.load_conversations()
        
        print("🤖 AI Companion Check-in")
        print("=" * 25)
        
        # Personalized greeting
        if profile.get('name'):
            print(f"Hi {profile['name']}! ")
        
        # Check last conversation
        if conversations:
            last_conv = conversations[-1]
            last_date = datetime.fromisoformat(last_conv['timestamp'])
            days_since = (datetime.now() - last_date).days
            
            if days_since > 3:
                print(f"It's been {days_since} days since we last talked. I've been thinking about you.")
            elif last_conv.get('mood') == 'low_mood':
                print("I remember you were having a tough time when we last spoke. How are you feeling now?")
        
        # Start conversation
        user_input = input("\nWhat's on your mind today? ")
        self.chat_session(user_input)

    def chat_session(self, initial_input=None):
        """Interactive chat session"""
        print("\n💬 Chat with AI Companion")
        print("(Type 'bye' to end, 'help' for options)")
        print("=" * 35)
        
        if initial_input:
            user_input = initial_input
        else:
            user_input = input("You: ")
        
        while user_input.lower() not in ['bye', 'exit', 'quit']:
            if user_input.lower() == 'help':
                print("\nAI Companion Options:")
                print("• Just talk naturally - I'm here to listen")
                print("• Ask for coping strategies")
                print("• Request breathing exercises")
                print("• Share your mood or feelings")
                print("• Type 'bye' when you're ready to end")
                user_input = input("\nYou: ")
                continue
            
            # Analyze mood and generate response
            mood = self.analyze_mood_from_text(user_input)
            crisis_detected = mood == 'crisis'
            
            ai_response = self.generate_response(user_input, mood)
            print(f"\nAI: {ai_response}")
            
            # Save conversation
            self.save_conversation(user_input, ai_response, mood, crisis_detected)
            
            # Continue conversation if not crisis
            if not crisis_detected:
                user_input = input("\nYou: ")
            else:
                break
        
        if not crisis_detected:
            print("\nAI: Take care! Remember, I'm always here when you need to talk. 💙")

    def mood_based_suggestions(self):
        """Provide suggestions based on recent mood patterns"""
        conversations = self.load_conversations()
        if not conversations:
            print("Let's have a conversation first so I can learn about your patterns!")
            return
        
        # Analyze recent mood trends
        recent_convs = conversations[-10:]  # Last 10 conversations
        moods = [conv.get('mood') for conv in recent_convs if conv.get('mood')]
        
        print("🎯 Personalized Suggestions")
        print("=" * 25)
        
        if moods.count('anxiety') > len(moods) * 0.4:
            print("I've noticed anxiety coming up frequently. Here are some strategies:")
            print("• Try 'om breathe' for quick anxiety relief")
            print("• Use 'om cbt anxiety' for cognitive strategies")
            print("• Consider 'om rescue' if anxiety feels overwhelming")
        elif moods.count('low_mood') > len(moods) * 0.4:
            print("You've been experiencing low moods lately. Some gentle suggestions:")
            print("• 'om gratitude' can help shift perspective")
            print("• 'om physical' for mood-boosting movement")
            print("• 'om depression' for specialized support")
        elif moods.count('positive') > len(moods) * 0.6:
            print("You've been doing great lately! Let's maintain this momentum:")
            print("• Keep up your current self-care practices")
            print("• Consider 'om habits' to build on positive patterns")
            print("• Share your success with 'om social'")
        else:
            print("Your mood seems balanced. Here are some maintenance strategies:")
            print("• Regular check-ins with 'om ai checkin'")
            print("• Daily wellness with 'om dashboard'")
            print("• Preventive care with 'om coach daily'")

    def conversation_insights(self):
        """Show insights from conversation history"""
        conversations = self.load_conversations()
        if not conversations:
            print("No conversation history yet. Start chatting with 'om ai chat'!")
            return
        
        print("📊 Your Conversation Insights")
        print("=" * 30)
        
        # Basic stats
        total_convs = len(conversations)
        crisis_count = sum(1 for conv in conversations if conv.get('crisis_detected'))
        
        print(f"Total conversations: {total_convs}")
        print(f"Days active: {len(set(conv['timestamp'][:10] for conv in conversations))}")
        
        if crisis_count > 0:
            print(f"⚠️  Crisis support provided: {crisis_count} times")
            print("Remember: Professional help is always available")
        
        # Mood distribution
        moods = [conv.get('mood') for conv in conversations if conv.get('mood') and conv.get('mood') != 'crisis']
        if moods:
            mood_counts = {mood: moods.count(mood) for mood in set(moods)}
            print(f"\nMood distribution:")
            for mood, count in sorted(mood_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(moods)) * 100
                print(f"  {mood}: {count} times ({percentage:.1f}%)")

def run(args=None):
    """Main entry point for AI companion"""
    companion = AICompanion()
    
    if not args:
        print("🤖 AI Mental Health Companion")
        print("1. Start chat session")
        print("2. Personalized check-in")
        print("3. Mood-based suggestions")
        print("4. Conversation insights")
        
        choice = input("\nChoose option (1-4): ")
        args = [choice]
    
    if args[0] in ['1', 'chat', 'talk']:
        companion.chat_session()
    elif args[0] in ['2', 'checkin', 'check']:
        companion.personalized_checkin()
    elif args[0] in ['3', 'suggestions', 'suggest']:
        companion.mood_based_suggestions()
    elif args[0] in ['4', 'insights', 'history']:
        companion.conversation_insights()
    else:
        print("Usage: om ai [chat|checkin|suggestions|insights]")

if __name__ == "__main__":
    run()
