"""
Meditation module for om
"""

import time
import random

def meditation_session(meditation_type, duration):
    """Start a guided meditation session"""
    print(f"🧘‍♀️ Starting {meditation_type} meditation for {duration} minutes")
    print("Find a comfortable position and close your eyes if you'd like.")
    print("Press Ctrl+C to stop at any time\n")
    
    meditations = {
        'mindfulness': mindfulness_meditation,
        'body-scan': body_scan_meditation,
        'loving-kindness': loving_kindness_meditation
    }
    
    if meditation_type not in meditations:
        print(f"❌ Unknown meditation type: {meditation_type}")
        return
    
    try:
        meditations[meditation_type](duration)
    except KeyboardInterrupt:
        pass
    
    print("\n✨ Wonderful! You've completed your meditation.")
    print("Take a moment to transition back to your day mindfully.")

def mindfulness_meditation(duration):
    """Basic mindfulness meditation"""
    prompts = [
        "Focus on your breath. Notice the sensation of air entering and leaving your body.",
        "If your mind wanders, gently bring your attention back to your breath.",
        "Notice any thoughts that arise, acknowledge them, and let them pass.",
        "Feel your body in this moment. Notice any sensations without judgment.",
        "Return to the rhythm of your breathing.",
        "Be present with whatever you're experiencing right now.",
        "Notice the space between your thoughts.",
        "Feel gratitude for taking this time for yourself."
    ]
    
    interval = (duration * 60) // len(prompts)
    
    for prompt in prompts:
        print(f"🌸 {prompt}")
        time.sleep(interval)
        print()

def body_scan_meditation(duration):
    """Body scan meditation"""
    body_parts = [
        "your toes and feet",
        "your legs and knees", 
        "your hips and lower back",
        "your abdomen and chest",
        "your shoulders and arms",
        "your hands and fingers",
        "your neck and throat",
        "your face and head"
    ]
    
    interval = (duration * 60) // len(body_parts)
    
    print("🌸 Let's begin by focusing on different parts of your body...")
    time.sleep(3)
    
    for part in body_parts:
        print(f"🌸 Now bring your attention to {part}.")
        print(f"   Notice any sensations, tension, or relaxation in this area.")
        time.sleep(interval)
        print()

def loving_kindness_meditation(duration):
    """Loving-kindness meditation"""
    phrases = [
        "May I be happy and healthy",
        "May I be at peace",
        "May I be free from suffering",
        "May someone I love be happy and healthy",
        "May they be at peace", 
        "May they be free from suffering",
        "May all beings be happy and healthy",
        "May all beings be at peace",
        "May all beings be free from suffering"
    ]
    
    interval = (duration * 60) // len(phrases)
    
    print("🌸 Let's cultivate loving-kindness, starting with yourself...")
    time.sleep(3)
    
    for phrase in phrases:
        print(f"💝 {phrase}")
        print("   Repeat this silently and feel the intention behind the words.")
        time.sleep(interval)
        print()
