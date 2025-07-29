"""
Physical wellness module for om
Quick exercises and movement for mental health
"""

import time
import random

def main(args):
    """Main entry point for physical wellness"""
    if not args:
        show_physical_menu()
    elif args[0] == 'stretch':
        desk_stretch_routine()
    elif args[0] == 'walk':
        walking_meditation()
    elif args[0] == 'quick':
        quick_movement()
    else:
        show_physical_menu()

def show_physical_menu():
    """Show physical wellness options"""
    print("🏃‍♀️ Physical Wellness for Mental Health")
    print("=" * 40)
    print()
    print("Physical movement is crucial for mental wellbeing!")
    print()
    print("Available exercises:")
    print("  stretch  - 5-minute desk stretching routine")
    print("  walk     - Guided walking meditation")
    print("  quick    - 2-minute energy boost")
    print()
    print("💡 Usage: om physical stretch")

def desk_stretch_routine():
    """5-minute desk stretching routine"""
    print("🧘‍♀️ 5-Minute Desk Stretching Routine")
    print("=" * 40)
    print("Perfect for reducing stress and tension!")
    print()
    
    stretches = [
        ("Neck rolls", "Slowly roll your head in circles", 30),
        ("Shoulder shrugs", "Lift shoulders to ears, hold, release", 20),
        ("Arm circles", "Make small then large circles with arms", 30),
        ("Spinal twist", "Twist gently left and right in your chair", 30),
        ("Ankle rolls", "Lift feet and roll ankles in circles", 20),
        ("Deep breathing", "Take 5 deep, calming breaths", 30),
    ]
    
    print("Starting in 3 seconds... Get ready!")
    time.sleep(3)
    
    for i, (name, instruction, duration) in enumerate(stretches, 1):
        print(f"\n{i}/6: {name}")
        print(f"   {instruction}")
        print(f"   Duration: {duration} seconds")
        
        # Countdown
        for remaining in range(duration, 0, -5):
            print(f"   {remaining}s remaining...", end='\r')
            time.sleep(5)
        
        print("   ✅ Complete!                    ")
        if i < len(stretches):
            print("   Take a 5-second break...")
            time.sleep(5)
    
    print("\n🌟 Great job! You've completed the stretching routine!")
    print("💪 Regular movement helps reduce stress and improve focus.")

def walking_meditation():
    """Guided walking meditation"""
    print("🚶‍♀️ Walking Meditation")
    print("=" * 40)
    print()
    print("Walking meditation combines physical movement with mindfulness.")
    print("Find a quiet space where you can walk slowly for 5-10 minutes.")
    print()
    print("Instructions:")
    print("1. Start walking very slowly")
    print("2. Focus on the sensation of your feet touching the ground")
    print("3. Notice the rhythm of your steps")
    print("4. When your mind wanders, gently return focus to walking")
    print("5. Breathe naturally and stay present")
    print()
    print("🎯 Benefits:")
    print("  • Reduces anxiety and stress")
    print("  • Improves focus and concentration")
    print("  • Combines exercise with mindfulness")
    print()
    print("Take your time and enjoy this moving meditation! 🌿")

def quick_movement():
    """2-minute energy boost"""
    print("⚡ 2-Minute Energy Boost")
    print("=" * 40)
    print("Quick movements to energize body and mind!")
    print()
    
    exercises = [
        "10 jumping jacks",
        "10 arm swings",
        "5 deep squats", 
        "10 marching in place",
        "5 deep breaths with arm raises"
    ]
    
    print("Let's do this quick routine:")
    for i, exercise in enumerate(exercises, 1):
        print(f"\n{i}. {exercise}")
        input("   Press Enter when ready...")
        print("   Go! 💪")
        time.sleep(3)
        print("   Great job! ✅")
    
    print("\n🎉 Excellent! You've boosted your energy!")
    print("💡 Even 2 minutes of movement can improve mood and focus.")

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
