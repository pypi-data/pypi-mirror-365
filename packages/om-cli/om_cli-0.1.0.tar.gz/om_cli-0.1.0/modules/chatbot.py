"""
Simple chatbot module for om
"""

import random

def start_chat():
    """Start interactive chat session"""
    print("💬 Welcome to om chat!")
    print("I'm here to provide support and mental health resources.")
    print("Type 'quit' or 'exit' to end our conversation.\n")
    
    responses = {
        'stress': [
            "Stress is a normal response to challenging situations. Try the 4-7-8 breathing technique: breathe in for 4, hold for 7, exhale for 8.",
            "When feeling stressed, try grounding yourself with the 5-4-3-2-1 technique: name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste.",
            "Remember that stress is temporary. Consider taking a short walk or doing some gentle stretches."
        ],
        'anxiety': [
            "Anxiety can feel overwhelming, but you're not alone. Try focusing on your breath and reminding yourself that this feeling will pass.",
            "For anxiety, try progressive muscle relaxation: tense and release each muscle group starting from your toes up to your head.",
            "Anxiety often involves worry about the future. Try to focus on what you can control right now in this moment."
        ],
        'sad': [
            "It's okay to feel sad sometimes. These feelings are valid and part of being human.",
            "When feeling down, try doing something small that usually brings you joy, or reach out to someone you trust.",
            "Consider practicing gratitude - even small things can help shift perspective when we're feeling low."
        ],
        'overwhelmed': [
            "Feeling overwhelmed is a sign you're taking on a lot. Try breaking tasks into smaller, manageable pieces.",
            "When overwhelmed, it can help to write down everything on your mind, then prioritize what truly needs attention today.",
            "Remember: you don't have to do everything at once. One step at a time is enough."
        ]
    }
    
    while True:
        user_input = input("You: ").strip().lower()
        
        if user_input in ['quit', 'exit', 'bye']:
            print("🧘‍♀️ Take care of yourself. Remember, I'm here whenever you need support.")
            break
        
        if not user_input:
            continue
        
        # Simple keyword matching
        response = None
        for keyword, response_list in responses.items():
            if keyword in user_input:
                response = random.choice(response_list)
                break
        
        if not response:
            response = get_general_response(user_input)
        
        print(f"om: {response}\n")

def get_general_response(user_input):
    """Generate general supportive responses"""
    general_responses = [
        "Thank you for sharing that with me. How are you feeling right now?",
        "I hear you. It sounds like you're going through something difficult.",
        "That sounds challenging. What do you think might help you feel better?",
        "I'm here to listen. Would you like to try a breathing exercise or meditation?",
        "It's brave of you to reach out. What kind of support would be most helpful right now?",
        "Your feelings are valid. Have you tried any of the om techniques like breathing or gratitude practice?",
        "Sometimes talking helps. I'm here to listen without judgment.",
        "You're taking a positive step by using om. What would feel most supportive right now?"
    ]
    
    return random.choice(general_responses)
