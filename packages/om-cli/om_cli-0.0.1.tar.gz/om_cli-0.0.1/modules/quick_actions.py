#!/usr/bin/env python3
"""
Enhanced Quick Actions for om - User-friendly mental health micro-interventions
"""

import sys
import os
import time
import random
from datetime import datetime

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# Import ASCII art utilities
try:
    from ascii_art import *
    ASCII_AVAILABLE = True
except ImportError:
    ASCII_AVAILABLE = False

# Import smart suggestions
try:
    from smart_suggestions import (
        record_action_usage, record_mood, get_smart_suggestions, 
        get_encouragement_message
    )
    SMART_SUGGESTIONS_AVAILABLE = True
except ImportError:
    SMART_SUGGESTIONS_AVAILABLE = False
    def record_action_usage(action): pass
    def record_mood(mood): pass
    def get_smart_suggestions(): return []
    def get_encouragement_message(): return "🌟 Great job taking care of your mental health!"

def show_progress_bar(duration, label="Progress"):
    """Show a simple progress bar for timed exercises"""
    print(f"\n{label}: ", end="", flush=True)
    for i in range(20):
        time.sleep(duration / 20)
        print("█", end="", flush=True)
    print(" ✅")

def quick_mood_check():
    """Enhanced mood logging with smart follow-ups and ASCII art"""
    if ASCII_AVAILABLE:
        print(get_mood_art())
    else:
        print("🎯 Quick Mood Check")
    
    print("How are you feeling right now?")
    print("1. Great 😊  2. Good 🙂  3. Okay 😐  4. Not great 😕  5. Struggling 😔")
    
    try:
        choice = input("\nChoose (1-5): ").strip()
        moods = {
            '1': ('great', 'positive', 8),
            '2': ('good', 'positive', 7), 
            '3': ('okay', 'neutral', 5),
            '4': ('not great', 'challenging', 3),
            '5': ('struggling', 'challenging', 2)
        }
        
        if choice in moods:
            mood, category, intensity = moods[choice]
            
            # Show mood-specific ASCII art
            if ASCII_AVAILABLE:
                print(get_mood_art(intensity))
            else:
                print(f"\n✅ Logged: {mood} ({intensity}/10)")
            
            # Record mood for smart suggestions
            record_mood(intensity)
            record_action_usage("mood")
            
            # Smart follow-up suggestions
            if intensity <= 3:
                if ASCII_AVAILABLE:
                    print(get_crisis_support_art())
                print("\n🆘 Immediate support suggestions:")
                print("• om qgr (5-4-3-2-1 grounding) - 1 minute")
                print("• om qa (positive affirmation) - 30 seconds")
                print("• om rescue (crisis support) - if needed")
                
                follow_up = input("\nWould you like to try grounding now? (y/n): ").strip().lower()
                if follow_up == 'y':
                    print("\n🌍 Starting grounding exercise...")
                    quick_grounding()
                    
            elif intensity <= 5:
                print("\n💪 Gentle support suggestions:")
                print("• om qb (breathing exercise) - 2 minutes")
                print("• om qc (progressive relaxation) - 90 seconds")
                print("• om qg (gratitude practice) - 30 seconds")
                
                follow_up = input("\nWould you like to try breathing? (y/n): ").strip().lower()
                if follow_up == 'y':
                    print("\n🫁 Starting breathing exercise...")
                    quick_breathing()
                    
            else:
                print("\n🌟 Keep the momentum going:")
                print("• om qg (celebrate with gratitude) - 30 seconds")
                print("• om qf (maintain focus) - 1 minute")
                print("• om qe (energy boost) - 1 minute")
                
                follow_up = input("\nWould you like to practice gratitude? (y/n): ").strip().lower()
                if follow_up == 'y':
                    print("\n🙏 Starting gratitude practice...")
                    quick_gratitude()
                    
            print(f"\n{get_encouragement_message()}")
        else:
            print("Invalid choice. Please select 1-5.")
            
    except KeyboardInterrupt:
        print("\n👋 Take care!")

def quick_breathing():
    """Enhanced breathing with visual guidance and ASCII art"""
    if ASCII_AVAILABLE:
        print(get_breathing_art())
    else:
        print("🫁 Quick Breathing (2 minutes)")
    
    print("4-7-8 breathing pattern for relaxation")
    print("Press Ctrl+C to stop anytime\n")
    
    record_action_usage("breathe")
    
    try:
        for i in range(8):  # 2 minutes of 4-7-8 breathing
            cycle_num = i + 1
            print(f"Cycle {cycle_num}/8:")
            
            # Inhale
            print("  🌬️  Breathe in through nose (4 seconds)... ", end="", flush=True)
            for j in range(4):
                time.sleep(1)
                print("●", end="", flush=True)
            print()
            
            # Hold
            print("  ⏸️  Hold your breath (7 seconds)... ", end="", flush=True)
            for j in range(7):
                time.sleep(1)
                print("○", end="", flush=True)
            print()
            
            # Exhale
            print("  💨 Breathe out through mouth (8 seconds)... ", end="", flush=True)
            for j in range(8):
                time.sleep(1)
                print("◐", end="", flush=True)
            print(" ✨\n")
            
            if i < 7:
                time.sleep(2)  # Brief pause
                
        print("✅ Excellent! You completed 2 minutes of breathing.")
        if ASCII_AVAILABLE:
            print(get_achievement_art())
        print(f"{get_encouragement_message()}")
        
        # Suggest follow-up
        print("\n💡 What's next?")
        print("• Continue with: om qg (gratitude)")
        print("• Or try: om qc (progressive relaxation)")
        
    except KeyboardInterrupt:
        print("\n✅ Good work on the breathing you did!")
        print(f"{get_encouragement_message()}")

def quick_box_breathing():
    """Enhanced 4-4-4-4 box breathing with visual guidance"""
    print("📦 Box Breathing (1 minute)")
    print("Equal timing for focus and clarity")
    print("Press Ctrl+C to stop anytime\n")
    
    record_action_usage("box")
    
    try:
        for i in range(6):  # 1 minute of box breathing
            cycle_num = i + 1
            print(f"Cycle {cycle_num}/6:")
            
            # Visual box representation
            print("  ┌─ Breathe in (4) ─┐")
            for j in range(4):
                time.sleep(1)
                print("  │", end="", flush=True)
            print()
            
            print("  │   Hold (4)      │")
            for j in range(4):
                time.sleep(1)
                print("  │", end="", flush=True)
            print()
            
            print("  │ Breathe out (4) │")
            for j in range(4):
                time.sleep(1)
                print("  │", end="", flush=True)
            print()
            
            print("  └─── Hold (4) ────┘")
            for j in range(4):
                time.sleep(1)
                print("   ", end="", flush=True)
            print(" ✨\n")
            
        print("✅ Excellent focus work! Box breathing complete.")
        print(f"{get_encouragement_message()}")
        
    except KeyboardInterrupt:
        print("\n✅ Good focus work!")

def quick_gratitude():
    """Enhanced gratitude practice with follow-up and ASCII art"""
    if ASCII_AVAILABLE:
        print(get_gratitude_art())
    else:
        print("🙏 Quick Gratitude (30 seconds)")
    
    print("Take a moment to appreciate something good in your life:")
    
    record_action_usage("gratitude")
    
    try:
        gratitude = input("\nI'm grateful for: ").strip()
        if gratitude:
            print(f"\n✅ Noted: {gratitude}")
            print("💝 Let that feeling of appreciation fill you...")
            time.sleep(2)
            
            # Follow-up question
            print("\nTake a moment to really feel that gratitude...")
            time.sleep(3)
            
            follow_up = input("Would you like to add another gratitude? (y/n): ").strip().lower()
            if follow_up == 'y':
                gratitude2 = input("I'm also grateful for: ").strip()
                if gratitude2:
                    print(f"✅ Wonderful: {gratitude2}")
                    if ASCII_AVAILABLE:
                        print(get_achievement_art())
                    print("🌟 Your gratitude practice is growing stronger!")
            
            print(f"\n{get_encouragement_message()}")
        else:
            print("That's okay, gratitude can be hard sometimes.")
            print("💝 Even trying to think of gratitude is a positive step!")
            
    except KeyboardInterrupt:
        print("\n👋 Take care!")

def quick_grounding():
    """Enhanced 5-4-3-2-1 grounding with better guidance"""
    print("🌍 5-4-3-2-1 Grounding (1-2 minutes)")
    print("This helps bring you back to the present moment.")
    print("Take your time with each step.\n")
    
    record_action_usage("grounding")
    
    try:
        print("👀 Look around and name 5 things you can SEE:")
        see_items = []
        for i in range(5):
            see = input(f"  {i+1}. I can see: ").strip()
            if see:
                see_items.append(see)
                print(f"     ✓ {see}")
        
        print("\n✋ Now 4 things you can TOUCH or FEEL:")
        touch_items = []
        for i in range(4):
            touch = input(f"  {i+1}. I can touch/feel: ").strip()
            if touch:
                touch_items.append(touch)
                print(f"     ✓ {touch}")
        
        print("\n👂 Now 3 things you can HEAR:")
        hear_items = []
        for i in range(3):
            hear = input(f"  {i+1}. I can hear: ").strip()
            if hear:
                hear_items.append(hear)
                print(f"     ✓ {hear}")
        
        print("\n👃 Now 2 things you can SMELL:")
        smell_items = []
        for i in range(2):
            smell = input(f"  {i+1}. I can smell: ").strip()
            if smell:
                smell_items.append(smell)
                print(f"     ✓ {smell}")
        
        print("\n👅 Finally, 1 thing you can TASTE:")
        taste = input("  1. I can taste: ").strip()
        if taste:
            print(f"     ✓ {taste}")
        
        print("\n🌟 Excellent grounding work!")
        print("You've successfully anchored yourself in the present moment.")
        print(f"{get_encouragement_message()}")
        
        # Quick check-in
        feeling = input("\nHow do you feel now? (calmer/same/other): ").strip().lower()
        if feeling == "calmer":
            print("🎯 Perfect! Grounding techniques are working for you.")
        elif feeling == "same":
            print("👍 That's okay. Sometimes grounding takes practice.")
            print("💡 Try: om qb (breathing) for additional calming.")
        else:
            print("💪 Every attempt at grounding builds your resilience.")
        
    except KeyboardInterrupt:
        print("\n✅ Good grounding work!")

def quick_affirmation():
    """Enhanced positive affirmation with personalization"""
    affirmations = [
        "I am capable of handling whatever comes my way",
        "This feeling is temporary and will pass",
        "I am worthy of love and respect",
        "I choose to focus on what I can control",
        "I am doing the best I can with what I have",
        "Every breath I take calms my mind and body",
        "I am stronger than my challenges",
        "I deserve peace and happiness",
        "I trust in my ability to overcome difficulties",
        "I am exactly where I need to be right now",
        "I am growing and learning every day",
        "I have the power to create positive change",
        "I am resilient and can bounce back from setbacks",
        "I choose to be kind to myself",
        "I am enough, just as I am"
    ]
    
    print("💪 Quick Affirmation (30-60 seconds)")
    
    record_action_usage("affirmation")
    
    affirmation = random.choice(affirmations)
    print(f"\nYour affirmation for today:")
    print(f"✨ '{affirmation}' ✨")
    
    print("\nTake a deep breath and repeat it to yourself...")
    time.sleep(3)
    
    try:
        print("Say it out loud or in your mind:")
        input("Press Enter when you've repeated it...")
        
        print("Now say it one more time with feeling...")
        input("Press Enter when ready...")
        
        print("✅ Wonderful! You've planted a positive seed in your mind.")
        print(f"{get_encouragement_message()}")
        
        # Option for another affirmation
        another = input("\nWould you like another affirmation? (y/n): ").strip().lower()
        if another == 'y':
            affirmation2 = random.choice([a for a in affirmations if a != affirmation])
            print(f"\nBonus affirmation:")
            print(f"✨ '{affirmation2}' ✨")
            print("💫 You're building a strong foundation of self-compassion!")
            
    except KeyboardInterrupt:
        print("\n✅ You've got this!")

def quick_stretch():
    """Quick physical reset exercises"""
    print("🤸 Quick Physical Reset (1 minute)")
    print("Simple movements to release tension:\n")
    
    exercises = [
        ("Neck rolls", "Slowly roll your head in a circle (5 each direction)"),
        ("Shoulder shrugs", "Lift shoulders to ears, hold 3 seconds, release (5 times)"),
        ("Arm circles", "Small circles forward and backward (10 each)"),
        ("Gentle twist", "Sit tall, twist left and right slowly (5 each)"),
        ("Deep stretch", "Reach arms overhead, stretch up for 10 seconds")
    ]
    
    try:
        for name, instruction in exercises:
            print(f"• {name}: {instruction}")
            input("  Press Enter when done...")
        
        print("\n✅ Great! Your body should feel more relaxed.")
        
    except KeyboardInterrupt:
        print("\n✅ Good movement work!")

def quick_energy():
    """Quick energy boost techniques"""
    print("⚡ Quick Energy Boost (1 minute)")
    
    techniques = [
        "Take 10 deep breaths with strong exhales",
        "Do 10 jumping jacks or march in place",
        "Drink a glass of water mindfully",
        "Step outside for fresh air if possible",
        "Listen to one energizing song"
    ]
    
    print("Choose an energy booster:")
    for i, technique in enumerate(techniques, 1):
        print(f"{i}. {technique}")
    
    try:
        choice = input("\nChoose (1-5): ").strip()
        if choice in ['1', '2', '3', '4', '5']:
            selected = techniques[int(choice)-1]
            print(f"\n🎯 Action: {selected}")
            print("Take your time...")
            input("Press Enter when complete...")
            print("✅ Energy boost complete!")
        else:
            print("Invalid choice")
    except KeyboardInterrupt:
        print("\n✅ Good energy work!")

def quick_focus():
    """Quick focus enhancement technique"""
    print("🎯 Quick Focus Reset (1 minute)")
    print("Clear your mind and sharpen attention:\n")
    
    try:
        print("1. Close your eyes and count backwards from 10...")
        for i in range(10, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
        
        print("\n2. Now set one clear intention for the next hour:")
        intention = input("My focus for the next hour: ").strip()
        
        if intention:
            print(f"✅ Intention set: {intention}")
            print("🎯 You're ready to focus!")
        else:
            print("✅ Mind cleared and ready!")
            
    except KeyboardInterrupt:
        print("\n✅ Good focus work!")

def quick_calm():
    """Quick calming technique"""
    print("🕊️ Quick Calm (90 seconds)")
    print("Progressive muscle relaxation:\n")
    
    try:
        body_parts = [
            "your face and jaw",
            "your shoulders and neck", 
            "your arms and hands",
            "your chest and breathing",
            "your stomach and core",
            "your legs and feet"
        ]
        
        for part in body_parts:
            print(f"Tense {part} for 5 seconds...")
            time.sleep(5)
            print(f"Now release and relax {part}...")
            time.sleep(10)
        
        print("\n✅ Your whole body should feel more relaxed now.")
        
    except KeyboardInterrupt:
        print("\n✅ Good relaxation work!")

def quick_reset():
    """Complete mental reset in 2 minutes"""
    print("🔄 Complete Quick Reset (2 minutes)")
    print("Full mental and physical reset:\n")
    
    try:
        print("Step 1: Three deep cleansing breaths...")
        for i in range(3):
            print(f"Breath {i+1}: In... and out...")
            time.sleep(4)
        
        print("\nStep 2: Quick body scan...")
        print("Notice any tension and let it go...")
        time.sleep(10)
        
        print("\nStep 3: Set a positive intention:")
        intention = input("What do you want to feel right now? ").strip()
        
        print(f"\nStep 4: Affirm your intention...")
        print(f"'I choose to feel {intention or 'peaceful'}'")
        time.sleep(5)
        
        print("\n✅ Complete reset finished! You're refreshed.")
        
    except KeyboardInterrupt:
        print("\n✅ Good reset work!")

def quick_check_in():
    """Comprehensive but fast emotional check-in"""
    print("📋 Quick Check-In (1 minute)")
    print("How are you doing right now?\n")
    
    try:
        print("Physical: How does your body feel? (1-10)")
        physical = input("Body energy: ").strip()
        
        print("Mental: How clear is your thinking? (1-10)")
        mental = input("Mental clarity: ").strip()
        
        print("Emotional: What's your main emotion right now?")
        emotion = input("Main feeling: ").strip()
        
        print("Spiritual: How connected do you feel? (1-10)")
        spiritual = input("Connection level: ").strip()
        
        print(f"\n✅ Check-in complete!")
        print(f"Physical: {physical or 'noted'} | Mental: {mental or 'noted'}")
        print(f"Emotional: {emotion or 'noted'} | Spiritual: {spiritual or 'noted'}")
        
    except KeyboardInterrupt:
        print("\n✅ Good self-awareness work!")

def quick_help():
    """Enhanced help with smart suggestions"""
    print("🚀 om Quick Actions - Your Mental Health Toolkit")
    print("=" * 60)
    
    # Show smart suggestions if available
    if SMART_SUGGESTIONS_AVAILABLE:
        suggestions = get_smart_suggestions()
        if suggestions:
            print("💡 Smart Suggestions for You Right Now:")
            for i, suggestion in enumerate(suggestions[:3], 1):
                print(f"   {i}. {suggestion}")
            print()
    
    print("⚡ Lightning-Fast Mental Health Interventions:")
    print()
    
    print("🎯 Emotional & Mental Support:")
    print("  om qm    (mood)        # 10-second mood check + smart follow-ups")
    print("  om qa    (affirmation) # Personalized positive self-talk")
    print("  om qgr   (grounding)   # 5-4-3-2-1 sensory anchoring")
    print("  om qch   (checkin)     # Complete wellness assessment")
    print("  om qr    (reset)       # Full 2-minute mental reset")
    print()
    
    print("🫁 Breathing & Relaxation:")
    print("  om qb    (breathe)     # 2-minute 4-7-8 with visual guidance")
    print("  om qbox  (box)         # 1-minute box breathing with focus")
    print("  om qc    (calm)        # Progressive muscle relaxation")
    print()
    
    print("💪 Physical & Energy:")
    print("  om qs    (stretch)     # 1-minute tension release routine")
    print("  om qe    (energy)      # Energy boost technique menu")
    print()
    
    print("🧠 Focus & Gratitude:")
    print("  om qf    (focus)       # Attention reset + intention setting")
    print("  om qg    (gratitude)   # Appreciation practice with depth")
    print()
    
    print("🌟 Smart Features:")
    print("• Personalized suggestions based on your usage")
    print("• Time-of-day contextual recommendations")
    print("• Mood-based follow-up actions")
    print("• Progress tracking and encouragement")
    print("• Interactive guidance with visual cues")
    print()
    
    print("💡 Pro Tips:")
    print("• All actions are designed for busy schedules (30s-2min)")
    print("• Press Ctrl+C to exit any exercise early")
    print("• Chain actions together: om qm && om qb && om qg")
    print("• Use throughout your day for micro-wellness breaks")
    print("• The more you use, the smarter suggestions become")
    print()
    
    print("🔗 Quick Combinations:")
    print("  Morning:   om qm && om qg && om qf")
    print("  Stressed:  om qgr && om qb && om qa")
    print("  Tired:     om qs && om qe && om qf")
    print("  Evening:   om qc && om qg")
    print()
    
    print(f"✨ {get_encouragement_message()}")

def main():
    if len(sys.argv) < 2:
        quick_help()
        return
    
    action = sys.argv[1].lower()
    
    # Main quick actions
    if action == 'mood':
        quick_mood_check()
    elif action == 'breathe':
        quick_breathing()
    elif action == 'box':
        quick_box_breathing()
    elif action == 'gratitude':
        quick_gratitude()
    elif action == 'grounding':
        quick_grounding()
    elif action == 'affirmation':
        quick_affirmation()
    elif action == 'stretch':
        quick_stretch()
    elif action == 'energy':
        quick_energy()
    elif action == 'focus':
        quick_focus()
    elif action == 'calm':
        quick_calm()
    elif action == 'reset':
        quick_reset()
    elif action == 'checkin':
        quick_check_in()
    elif action == 'help':
        quick_help()
    else:
        print(f"❌ Unknown quick action: {action}")
        print("💡 Try: om quick help")
        print()
        # Show smart suggestions as fallback
        if SMART_SUGGESTIONS_AVAILABLE:
            suggestions = get_smart_suggestions()
            if suggestions:
                print("🌟 Here are some suggestions for you:")
                for suggestion in suggestions[:2]:
                    print(f"   • {suggestion}")

if __name__ == "__main__":
    main()
