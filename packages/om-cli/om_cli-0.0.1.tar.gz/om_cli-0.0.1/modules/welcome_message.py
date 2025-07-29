#!/usr/bin/env python3
"""
Welcome message for new om users with branded ASCII art and messaging
"""

def show_welcome_message():
    """Display the branded welcome message for first-time users"""
    
    welcome_art = """
  ╔═══════════════════════════════════════════════════════════╗
  ║                                                           ║
  ║                    ╭─╮ ╭─╮╭─╮                             ║
  ║                    │ │ │ ││ │                             ║
  ║                    ╰─╯ ╰─╯╰─╯                             ║
  ║                                                           ║
  ║              Welcome to your terminal therapist           ║
  ║                                                           ║
  ║           ◉ breathe ◉ reflect ◉ grow ◉ heal              ║
  ║                                                           ║
  ║              Your mind deserves better code               ║
  ║                                                           ║
  ╚═══════════════════════════════════════════════════════════╝
"""
    
    print(welcome_art)
    print()
    print("🎉 Welcome to om - your comprehensive mental health CLI platform!")
    print()
    print("✨ You now have access to:")
    print("   • 44 evidence-based wellness modules")
    print("   • AI-powered personalized coaching")
    print("   • Global crisis support resources")
    print("   • Therapeutic sleep sounds & affirmations")
    print("   • Complete privacy protection (100% local)")
    print()
    print("🚀 Quick start commands:")
    print("   om qm              # Quick mood check (10 seconds)")
    print("   om rescue setup    # Configure crisis support")
    print("   om coach daily     # Get your first AI insight")
    print("   om help            # See all available commands")
    print()
    print("💡 Pro tip: All your data stays on your device. Always.")
    print()
    print("Ready to debug your mind? Let's start with a quick mood check:")
    print("$ om qm")
    print()

def show_daily_greeting():
    """Display a daily greeting for returning users"""
    
    daily_art = """
    ╭─────────────────────────────╮
   ╱                               ╲
  ╱         ╭─╮╭─╮   Welcome back   ╲
 ╱          │ ││ │                   ╲
╱           ╰─╯╰─╯                    ╲
│                                     │
│    Ready to continue your wellness  │
│    journey? Your mind is worth it.  │
│                                     │
╲                                    ╱
 ╲                                  ╱
  ╲                                ╱
   ╲______________________________╱
"""
    
    print(daily_art)
    print()
    print("🌅 Good to see you again! Here are some quick actions:")
    print("   om qm              # Check in with your mood")
    print("   om coach daily     # Get today's AI insights")
    print("   om gamify status   # See your progress")
    print("   om affirmations    # Daily positive affirmation")
    print()

def show_achievement_celebration(achievement_name, description):
    """Display achievement unlock with branded styling"""
    
    achievement_art = f"""
╔═══════════════════════════════════════════════════════════╗
║                    🏆 ACHIEVEMENT UNLOCKED                ║
║                                                           ║
║                       ╭─╮╭─╮                             ║
║                       │ ││ │                             ║
║                       ╰─╯╰─╯                             ║
║                                                           ║
║                  {achievement_name:^35}                  ║
║                                                           ║
║              {description:^43}              ║
║                                                           ║
║              You're building amazing habits!              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
    
    print(achievement_art)
    print()
    print("🎉 Keep up the great work! Your mental health journey matters.")
    print("   Use 'om gamify status -v' to see all your achievements.")
    print()

def show_crisis_support_banner():
    """Display crisis support information with branded styling"""
    
    crisis_art = """
  ╔═══════════════════════════════════════════════════════════╗
  ║                    🤝 SUPPORT RESOURCES                   ║
  ║                                                           ║
  ║                       ╭─╮╭─╮                             ║
  ║                       │ ││ │                             ║
  ║                       ╰─╯╰─╯                             ║
  ║                                                           ║
  ║              You are not alone. Help is available.       ║
  ║                                                           ║
  ║              om crisis    # Local emergency resources     ║
  ║              om rescue    # Immediate support tools      ║
  ║              om emergency # Quick grounding techniques    ║
  ║                                                           ║
  ║              Your wellbeing matters. You matter.         ║
  ║                                                           ║
  ╚═══════════════════════════════════════════════════════════╝
"""
    
    print(crisis_art)
    print()

def show_loading_animation(message="Processing your wellness data"):
    """Show a branded loading animation"""
    import time
    import sys
    
    frames = [
        "◯ ◯ ◯ ◯ ◯",
        "● ◯ ◯ ◯ ◯", 
        "● ● ◯ ◯ ◯",
        "● ● ● ◯ ◯",
        "● ● ● ● ◯",
        "● ● ● ● ●",
        "◯ ● ● ● ●",
        "◯ ◯ ● ● ●",
        "◯ ◯ ◯ ● ●",
        "◯ ◯ ◯ ◯ ●",
        "◯ ◯ ◯ ◯ ◯"
    ]
    
    print(f"\n{message}...")
    for i in range(3):  # 3 cycles
        for frame in frames:
            sys.stdout.write(f"\r  {frame}  ")
            sys.stdout.flush()
            time.sleep(0.1)
    
    sys.stdout.write(f"\r  ● ● ● ● ●  Complete!\n\n")
    sys.stdout.flush()

def show_mood_prompt():
    """Show a branded mood check prompt"""
    
    mood_art = """
    ╭─────────────────────────────╮
   ╱                               ╲
  ╱         ╭─╮╭─╮   How are you    ╲
 ╱          │ ││ │   feeling today? ╲
╱           ╰─╯╰─╯                   ╲
│                                     │
│  Your emotions are valid and        │
│  important. Let's check in.         │
│                                     │
╲                                    ╱
 ╲                                  ╱
  ╲                                ╱
   ╲______________________________╱
"""
    
    print(mood_art)
    print()

def show_breathing_guide():
    """Show a branded breathing exercise guide"""
    
    breathing_art = """
  ╔═══════════════════════════════════════════════════════════╗
  ║                    🫁 BREATHING EXERCISE                  ║
  ║                                                           ║
  ║                       ╭─╮╭─╮                             ║
  ║                       │ ││ │                             ║
  ║                       ╰─╯╰─╯                             ║
  ║                                                           ║
  ║              Inhale for 4 • Hold for 7 • Exhale for 8    ║
  ║                                                           ║
  ║              Focus on your breath. You've got this.      ║
  ║                                                           ║
  ╚═══════════════════════════════════════════════════════════╝
"""
    
    print(breathing_art)
    print()

if __name__ == "__main__":
    # Demo all the branded messages
    show_welcome_message()
    input("Press Enter to continue...")
    
    show_daily_greeting()
    input("Press Enter to continue...")
    
    show_achievement_celebration("Mindful Master", "7-day meditation streak")
    input("Press Enter to continue...")
    
    show_crisis_support_banner()
    input("Press Enter to continue...")
    
    show_mood_prompt()
    input("Press Enter to continue...")
    
    show_breathing_guide()
    input("Press Enter to continue...")
    
    show_loading_animation("Analyzing your wellness patterns")
