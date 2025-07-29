"""
Enhanced Mental Health Chatbot for om
Integrates Rogendo's Mental Health Chatbot with om's privacy-first architecture
https://github.com/Rogendo/Mental-health-Chatbot
"""

import json
import random
import pickle
import os
import sys
from datetime import datetime
import re

class EnhancedMentalHealthChatbot:
    def __init__(self):
        self.data_dir = os.path.expanduser("~/.om")
        os.makedirs(self.data_dir, exist_ok=True)
        self.conversation_file = os.path.join(self.data_dir, "chatbot_conversations.json")
        
        # Mental health intents based on Rogendo's chatbot
        self.intents = {
            "greeting": {
                "patterns": ["hi", "hey", "hello", "hi there", "hey there", "howdy", "hola", "good morning", "good afternoon", "good evening"],
                "responses": [
                    "Hello there. Tell me how are you feeling today?",
                    "Hi there. What brings you here today?", 
                    "Hi there. How are you feeling today?",
                    "Great to see you. How do you feel currently?",
                    "Hello there. Glad to see you're back. What's going on in your world right now?"
                ]
            },
            "goodbye": {
                "patterns": ["bye", "see you later", "goodbye", "bye then", "farewell", "take care"],
                "responses": [
                    "Take care of yourself. Remember, I'm here whenever you need support.",
                    "See you later. Don't hesitate to come back if you need to talk.",
                    "Goodbye for now. Remember that you matter and help is always available.",
                    "I'll see you soon. Take care of your mental health."
                ]
            },
            "thanks": {
                "patterns": ["thanks", "thank you", "that's helpful", "thanks for the help", "appreciate it"],
                "responses": [
                    "Happy to help! Your mental health matters.",
                    "Any time! I'm here to support you.",
                    "My pleasure. Taking care of your mental health is important.",
                    "You're most welcome! Keep taking care of yourself."
                ]
            },
            "about": {
                "patterns": ["who are you", "what are you", "tell me about yourself", "what's your name"],
                "responses": [
                    "I'm your Personal Mental Health AI Assistant in om. How are you feeling today?",
                    "I'm a therapeutic AI assistant designed to provide mental health support. Tell me about yourself.",
                    "I'm your om mental health companion. I'm here to listen and provide support. How are you feeling today?",
                    "You can think of me as your personal mental health supporter within om."
                ]
            },
            "sad": {
                "patterns": ["i am feeling lonely", "i feel down", "i feel sad", "i am sad", "i feel empty", "i don't have anyone", "feeling depressed"],
                "responses": [
                    "I'm sorry to hear that. I'm here for you. Talking about it might help. So, tell me why do you think you're feeling this way?",
                    "I'm here for you. Could you tell me why you're feeling this way?",
                    "Why do you think you feel this way? Sometimes understanding the cause can help.",
                    "How long have you been feeling this way? You don't have to go through this alone.",
                    "Your feelings are valid. Would you like to try some om tools that might help? Try 'om qb' for breathing exercises or 'om qg' for gratitude practice."
                ]
            },
            "stressed": {
                "patterns": ["i am so stressed", "i feel stressed", "i am stressed out", "i feel stuck", "i am burned out", "overwhelmed"],
                "responses": [
                    "What do you think is causing this stress? Understanding the source can help us address it.",
                    "Take a deep breath and gather your thoughts. Try 'om qb' for a quick breathing exercise right now.",
                    "Give yourself a break. Go easy on yourself. Stress is your body's way of saying you need care.",
                    "I am sorry to hear that. What is the reason behind this? Let's work through it together.",
                    "When feeling overwhelmed, try 'om qgr' for grounding techniques or 'om qc' for quick calming."
                ]
            },
            "anxious": {
                "patterns": ["i feel anxious", "i'm so anxious", "anxiety", "panic", "worried", "nervous"],
                "responses": [
                    "Don't be hard on yourself. What's the reason behind this anxiety?",
                    "Can you tell me more about this feeling? Anxiety often has specific triggers.",
                    "I understand that anxiety can be scary. Tell me more about what you're experiencing.",
                    "Don't let worries overwhelm you. Try 'om qgr' for the 5-4-3-2-1 grounding technique.",
                    "For immediate anxiety relief, try 'om qb' for breathing exercises or 'om rescue' if you need crisis support."
                ]
            },
            "worthless": {
                "patterns": ["i feel worthless", "no one likes me", "i can't do anything", "i am useless", "nothing makes sense"],
                "responses": [
                    "It's natural to feel this way sometimes, but these thoughts don't define your worth. Tell me more about what's on your mind.",
                    "Let's discuss further why you're feeling this way. You are not alone in these feelings.",
                    "I want you to know that you are not alone and there is always someone there to help. You can change these feelings by being open to trying.",
                    "Your worth isn't determined by these difficult moments. Would you like to try 'om qa' for some positive affirmations?",
                    "These feelings are temporary, even when they feel overwhelming. Try 'om positive three' to focus on good things in your life."
                ]
            },
            "depressed": {
                "patterns": ["i can't take it anymore", "i am depressed", "i think i'm depressed", "i have depression", "suicidal", "want to die"],
                "responses": [
                    "I'm concerned about what you've shared. Please know that help is available. Try 'om rescue' for immediate crisis resources.",
                    "It helps to talk about what's happening. You're going to be okay. If you're having thoughts of self-harm, please call 988 immediately.",
                    "Talk to me. Tell me more. It helps to open up, and professional help is also available.",
                    "Sometimes when we are depressed, it's hard to care about anything. Give yourself time to heal, and please reach out for professional support.",
                    "🆘 If you're having thoughts of self-harm, please contact: National Suicide Prevention Lifeline: 988 or try 'om rescue' for immediate resources."
                ]
            },
            "happy": {
                "patterns": ["i feel great", "i am happy", "i feel happy", "i'm good", "cheerful", "i'm fine", "feeling better"],
                "responses": [
                    "That's great to hear! I'm glad you're feeling this way.",
                    "Oh I see. That's wonderful. What's contributing to these positive feelings?",
                    "Did something happen which made you feel this way? It's great to celebrate good moments.",
                    "I love hearing that! Keep nurturing whatever is making you feel good."
                ]
            },
            "sleep": {
                "patterns": ["i have insomnia", "i can't sleep", "haven't slept", "can't seem to sleep", "sleep problems"],
                "responses": [
                    "Sleep problems can really affect mental health. What do you think might be causing this?",
                    "That sounds difficult. Try 'om sleep' for sleep optimization tools and techniques.",
                    "Sleep issues are often connected to stress or anxiety. Have you tried 'om sleep sounds' for relaxing audio?",
                    "Poor sleep can make everything harder. Let's explore what might help - try 'om insomnia' for specific support."
                ]
            },
            "help": {
                "patterns": ["help me", "i need help", "can you help", "support me", "what can you do"],
                "responses": [
                    "Of course I can help. Tell me what's going on and how you're feeling.",
                    "I'm here to support you. What would be most helpful right now?",
                    "Yes, I'm here for you. You can talk to me about anything on your mind.",
                    "I can provide emotional support, suggest om tools, and help you access resources. What do you need?",
                    "Here are some om tools that might help: 'om qm' for mood check, 'om qb' for breathing, 'om rescue' for crisis support."
                ]
            },
            "crisis": {
                "patterns": ["crisis", "emergency", "urgent", "immediate help", "can't cope", "breaking down"],
                "responses": [
                    "🆘 I'm here for you. For immediate crisis support, try 'om rescue' or call 988 (National Suicide Prevention Lifeline).",
                    "This sounds urgent. Please try 'om rescue' for immediate resources or contact emergency services if you're in danger.",
                    "I'm concerned about you. Immediate help is available: 988 for crisis support, or 'om rescue' for resources and grounding techniques.",
                    "You don't have to handle this alone. Try 'om rescue' now for crisis support, or call 911 if you're in immediate danger."
                ]
            }
        }
        
        # Load conversation history
        self.conversation_history = self.load_conversation_history()
    
    def load_conversation_history(self):
        """Load conversation history from local storage"""
        try:
            with open(self.conversation_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_conversation_history(self):
        """Save conversation history to local storage"""
        with open(self.conversation_file, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
    
    def detect_intent(self, user_input):
        """Detect user intent from input using pattern matching"""
        user_input_lower = user_input.lower()
        
        # Check for crisis keywords first (highest priority)
        crisis_keywords = ["kill myself", "end it all", "suicide", "want to die", "can't go on", "no point living"]
        for keyword in crisis_keywords:
            if keyword in user_input_lower:
                return "crisis"
        
        # Check other intents
        for intent, data in self.intents.items():
            for pattern in data["patterns"]:
                if pattern in user_input_lower:
                    return intent
        
        return "general"
    
    def get_response(self, user_input, intent):
        """Get appropriate response based on intent"""
        if intent in self.intents:
            response = random.choice(self.intents[intent]["responses"])
        else:
            # General supportive responses
            general_responses = [
                "I'm listening. Please tell me more about how you're feeling.",
                "Can you elaborate on that? I'm here to support you.",
                "That sounds important. How is this affecting you?",
                "I want to understand better. Can you share more about this?",
                "Your feelings matter. What else is on your mind?",
                "I'm here for you. Would you like to explore this further?",
                "Sometimes it helps to talk through things. What's been on your mind lately?"
            ]
            response = random.choice(general_responses)
        
        return response
    
    def log_conversation(self, user_input, bot_response, intent):
        """Log conversation for pattern analysis (privacy-safe)"""
        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "intent": intent,
            "user_input_length": len(user_input),  # Don't store actual input for privacy
            "response_type": intent,
            "crisis_detected": intent == "crisis"
        }
        
        self.conversation_history.append(conversation_entry)
        
        # Keep only last 100 conversations for privacy
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
        
        self.save_conversation_history()
    
    def get_conversation_stats(self):
        """Get conversation statistics for wellness insights"""
        if not self.conversation_history:
            return "No conversation history yet."
        
        total_conversations = len(self.conversation_history)
        crisis_conversations = sum(1 for conv in self.conversation_history if conv.get("crisis_detected", False))
        
        # Count intent types
        intent_counts = {}
        for conv in self.conversation_history:
            intent = conv.get("intent", "unknown")
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        stats = f"""
💬 Conversation Statistics:
• Total conversations: {total_conversations}
• Crisis conversations: {crisis_conversations}
• Most common topics: {', '.join(sorted(intent_counts.keys())[:3])}

💡 This data helps om understand your needs better while keeping your privacy.
"""
        return stats
    
    def start_chat(self):
        """Start interactive chat session"""
        print("💬 Enhanced Mental Health Chat")
        print("=" * 30)
        print("I'm your om mental health companion, enhanced with advanced conversational AI.")
        print("I'm here to provide support, resources, and a listening ear.")
        print("Type 'quit', 'exit', or 'bye' to end our conversation.")
        print("Type 'help' to see what I can do for you.")
        print("Type 'stats' to see conversation insights.\n")
        
        # Welcome message
        print("Bot: Hello! I'm here to support your mental health journey. How are you feeling today?")
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                    intent = self.detect_intent(user_input)
                    response = self.get_response(user_input, intent)
                    print(f"Bot: {response}")
                    break
                
                # Check for stats command
                if user_input.lower() in ['stats', 'statistics']:
                    print(self.get_conversation_stats())
                    continue
                
                # Check for om command suggestions
                if user_input.lower() in ['help', 'what can you do']:
                    help_response = """
I can help you with:
• 💭 Emotional support and listening
• 🆘 Crisis support (try 'om rescue' for immediate help)
• 🧘 Breathing exercises (try 'om qb')
• 🙏 Gratitude practice (try 'om qg') 
• 😌 Mood tracking (try 'om qm')
• 💤 Sleep support (try 'om sleep')
• 🎯 Quick actions for immediate relief
• 📞 Connecting you to professional resources

What would you like to talk about?
"""
                    print(f"Bot: {help_response}")
                    continue
                
                # Detect intent and generate response
                intent = self.detect_intent(user_input)
                response = self.get_response(user_input, intent)
                
                # Log conversation (privacy-safe)
                self.log_conversation(user_input, response, intent)
                
                # Display response
                print(f"Bot: {response}")
                
                # Provide additional om tool suggestions for certain intents
                if intent == "stressed":
                    print("💡 Try: 'om qb' for breathing exercises or 'om qc' for quick calming")
                elif intent == "anxious":
                    print("💡 Try: 'om qgr' for grounding or 'om rescue' if you need immediate support")
                elif intent == "sad":
                    print("💡 Try: 'om qg' for gratitude practice or 'om positive three' for positivity")
                elif intent == "sleep":
                    print("💡 Try: 'om sleep' for sleep tools or 'om sleep sounds' for relaxing audio")
                elif intent == "crisis":
                    print("🆘 IMMEDIATE HELP: 'om rescue' or call 988 (National Suicide Prevention Lifeline)")
                
            except KeyboardInterrupt:
                print("\n\nBot: Take care of yourself. Remember, I'm here whenever you need support.")
                break
            except Exception as e:
                print(f"Bot: I'm sorry, I encountered an issue. Please try again or type 'help' for assistance.")
                continue

def run(args=None):
    """Main entry point for enhanced chatbot"""
    chatbot = EnhancedMentalHealthChatbot()
    
    if args and len(args) > 0:
        if args[0] in ['stats', 'statistics']:
            print(chatbot.get_conversation_stats())
            return
        elif args[0] in ['help', '--help']:
            print("""
Enhanced Mental Health Chatbot Commands:

om chatbot              # Start interactive chat
om chatbot stats        # View conversation statistics  
om chatbot help         # Show this help

The chatbot provides:
• Emotional support and active listening
• Crisis detection and resource connection
• Integration with om mental health tools
• Privacy-safe conversation logging
• Personalized responses based on your needs

All conversations are stored locally and never transmitted externally.
""")
            return
    
    # Start interactive chat
    chatbot.start_chat()

if __name__ == "__main__":
    run()
