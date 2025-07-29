#!/usr/bin/env python3
"""
ASCII Art utilities for om - Mental Health CLI
Beautiful visual elements to enhance user experience
"""

import random
from datetime import datetime

# Color codes for terminal
class Colors:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    PINK = '\033[95m'
    ORANGE = '\033[38;5;208m'

def get_om_logo():
    """Main om logo with meditation theme"""
    return f"""{Colors.CYAN}{Colors.BOLD}
    ╔═══════════════════════════════════════╗
    ║                                       ║
    ║        ████████  ██████████           ║
    ║       ██      ██ ██        ██         ║
    ║      ██        ████        ██         ║
    ║      ██        ████        ██         ║
    ║       ██      ██ ██        ██         ║
    ║        ████████  ██████████           ║
    ║                                       ║
    ║     🧘‍♀️ Mental Health CLI Platform 🧘‍♂️     ║
    ║                                       ║
    ╚═══════════════════════════════════════╝{Colors.END}
    """

def get_simple_om_logo():
    """Simpler om logo for quick display"""
    return f"""{Colors.PURPLE}{Colors.BOLD}
   ╭─────────────────────╮
   │    ██████  ███████  │
   │   ██    ████     ██ │
   │   ██    ████     ██ │
   │    ██████  ███████  │
   │                     │
   │   🧘‍♀️ om wellness 🧘‍♂️   │
   ╰─────────────────────╯{Colors.END}
   """

def get_mood_art(mood_level=None):
    """ASCII art for mood tracking"""
    if mood_level is None or mood_level >= 8:
        return f"""{Colors.GREEN}
        😊 ✨ 🌟 ✨ 😊
       ╭─────────────────╮
       │  Feeling Great! │
       ╰─────────────────╯{Colors.END}"""
    elif mood_level >= 6:
        return f"""{Colors.YELLOW}
        🙂 ☀️ 🌤️ ☀️ 🙂
       ╭─────────────────╮
       │  Doing Okay!    │
       ╰─────────────────╯{Colors.END}"""
    elif mood_level >= 4:
        return f"""{Colors.ORANGE}
        😐 ⛅ 🌥️ ⛅ 😐
       ╭─────────────────╮
       │  Neutral Day    │
       ╰─────────────────╯{Colors.END}"""
    else:
        return f"""{Colors.CYAN}
        🤗 💙 🫂 💙 🤗
       ╭─────────────────╮
       │  Need Support   │
       ╰─────────────────╯{Colors.END}"""

def get_breathing_art():
    """ASCII art for breathing exercises"""
    return f"""{Colors.BLUE}
    ╭─────────────────────────────╮
    │        🌬️  BREATHE  🌬️        │
    │                             │
    │    ∞ ∞ ∞ ∞ ∞ ∞ ∞ ∞ ∞ ∞    │
    │                             │
    │   Inhale... Hold... Exhale  │
    ╰─────────────────────────────╯{Colors.END}
    """

def get_gratitude_art():
    """ASCII art for gratitude practice"""
    return f"""{Colors.PINK}
    ╭─────────────────────────────╮
    │       🙏 GRATITUDE 🙏       │
    │                             │
    │    ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥ ♥    │
    │                             │
    │   Count Your Blessings      │
    ╰─────────────────────────────╯{Colors.END}
    """

def get_meditation_art():
    """ASCII art for meditation"""
    return f"""{Colors.PURPLE}
    ╭─────────────────────────────╮
    │      🧘‍♀️ MEDITATION 🧘‍♂️      │
    │                             │
    │        ॐ   ॐ   ॐ   ॐ        │
    │                             │
    │    Find Your Inner Peace    │
    ╰─────────────────────────────╯{Colors.END}
    """

def get_crisis_support_art():
    """ASCII art for crisis support"""
    return f"""{Colors.RED}{Colors.BOLD}
    ╔═══════════════════════════════╗
    ║         🆘 CRISIS SUPPORT 🆘   ║
    ║                               ║
    ║    You are not alone.         ║
    ║    Help is available.         ║
    ║                               ║
    ║    National: 988              ║
    ║    Crisis Text: 741741        ║
    ╚═══════════════════════════════╝{Colors.END}
    """

def get_achievement_art():
    """ASCII art for achievements"""
    return f"""{Colors.YELLOW}{Colors.BOLD}
    ╭─────────────────────────────╮
    │       🏆 ACHIEVEMENT! 🏆     │
    │                             │
    │    ⭐ ⭐ ⭐ ⭐ ⭐ ⭐ ⭐    │
    │                             │
    │   You're doing great!       │
    ╰─────────────────────────────╯{Colors.END}
    """

def get_progress_bar(percentage, width=30):
    """Create a visual progress bar"""
    filled = int(width * percentage / 100)
    bar = '█' * filled + '░' * (width - filled)
    
    if percentage >= 80:
        color = Colors.GREEN
    elif percentage >= 60:
        color = Colors.YELLOW
    elif percentage >= 40:
        color = Colors.ORANGE
    else:
        color = Colors.RED
    
    return f"{color}[{bar}] {percentage}%{Colors.END}"

def get_wellness_dashboard_header():
    """Header for wellness dashboard"""
    now = datetime.now()
    return f"""{Colors.CYAN}{Colors.BOLD}
    ╔══════════════════════════════════════════════════════════╗
    ║                    🌟 WELLNESS DASHBOARD 🌟               ║
    ║                                                          ║
    ║    {now.strftime("%A, %B %d, %Y - %I:%M %p")}                    ║
    ╚══════════════════════════════════════════════════════════╝{Colors.END}
    """

def get_daily_quote():
    """Random inspirational quote with ASCII decoration"""
    quotes = [
        "The present moment is the only time over which we have dominion. - Thich Nhat Hanh",
        "You are braver than you believe, stronger than you seem, and smarter than you think. - A.A. Milne",
        "Mental health is not a destination, but a process. - Noam Shpancer",
        "Your mental health is a priority. Your happiness is essential. Your self-care is a necessity.",
        "It's okay to not be okay. It's not okay to stay that way.",
        "Healing isn't linear. Be patient with yourself.",
        "You don't have to be positive all the time. It's perfectly okay to feel sad, angry, annoyed, frustrated, scared, or anxious.",
        "Take time to make your soul happy.",
        "Self-care is not selfish. You cannot serve from an empty vessel.",
        "Progress, not perfection."
    ]
    
    quote = random.choice(quotes)
    return f"""{Colors.GREEN}
    ╭─────────────────────────────────────────────────────────╮
    │  💭 Daily Inspiration                                   │
    │                                                         │
    │  "{quote[:50]}...                                       │
    │   {quote[50:] if len(quote) > 50 else ''}              │
    ╰─────────────────────────────────────────────────────────╯{Colors.END}
    """

def get_quick_action_menu():
    """ASCII menu for quick actions"""
    return f"""{Colors.BLUE}
    ╭─────────────────────────────────────╮
    │           ⚡ QUICK ACTIONS ⚡         │
    │                                     │
    │  qm  - Quick Mood Check    😊       │
    │  qb  - Quick Breathing     🌬️       │
    │  qg  - Quick Gratitude     🙏       │
    │  qf  - Quick Focus         🎯       │
    │  qc  - Quick Calm          😌       │
    │                                     │
    ╰─────────────────────────────────────╯{Colors.END}
    """

def get_level_up_art(level):
    """ASCII art for level up notification"""
    return f"""{Colors.YELLOW}{Colors.BOLD}
    ╔═══════════════════════════════════════╗
    ║            🎉 LEVEL UP! 🎉            ║
    ║                                       ║
    ║         You reached Level {level:2d}!        ║
    ║                                       ║
    ║    ⭐ ⭐ ⭐ ⭐ ⭐ ⭐ ⭐ ⭐ ⭐ ⭐    ║
    ║                                       ║
    ║      Keep up the great work!          ║
    ╚═══════════════════════════════════════╝{Colors.END}
    """

def get_streak_art(days):
    """ASCII art for streak achievements"""
    if days >= 30:
        emoji = "🔥🔥🔥"
        message = "INCREDIBLE STREAK!"
    elif days >= 7:
        emoji = "🔥🔥"
        message = "AMAZING STREAK!"
    else:
        emoji = "🔥"
        message = "Great Streak!"
    
    return f"""{Colors.ORANGE}{Colors.BOLD}
    ╭─────────────────────────────╮
    │      {emoji} {days} DAY STREAK! {emoji}      │
    │                             │
    │       {message}        │
    ╰─────────────────────────────╯{Colors.END}
    """

def get_welcome_art():
    """Welcome message with ASCII art"""
    return f"""{Colors.PURPLE}{Colors.BOLD}
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║    Welcome to om - Your Mental Health Companion! 🧘‍♀️      ║
    ║                                                           ║
    ║    ✨ Track your mood and wellness                        ║
    ║    🌬️  Practice breathing and meditation                  ║
    ║    🙏 Cultivate gratitude and positivity                 ║
    ║    🎯 Build healthy mental health habits                  ║
    ║    🆘 Access crisis support when needed                   ║
    ║                                                           ║
    ║    Type 'om help' to get started!                        ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝{Colors.END}
    """

def get_help_art():
    """ASCII art for help display"""
    return f"""{Colors.CYAN}
    ╭─────────────────────────────────────────╮
    │              📚 HELP MENU 📚             │
    │                                         │
    │  Core Commands:                         │
    │  • mood, m     - Track your mood        │
    │  • breathe, b  - Breathing exercises    │
    │  • gratitude,g - Gratitude practice     │
    │  • meditate    - Meditation sessions    │
    │  • dashboard   - Wellness overview      │
    │                                         │
    │  Support:                               │
    │  • anxiety     - Anxiety management     │
    │  • depression  - Depression support     │
    │  • rescue      - Crisis support         │
    │                                         │
    │  Quick Actions: qm, qb, qg, qf, qc      │
    ╰─────────────────────────────────────────╯{Colors.END}
    """

def get_loading_animation():
    """Simple loading animation frames"""
    frames = [
        "⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"
    ]
    return frames

def get_separator(width=50, char="─"):
    """Create a decorative separator"""
    return f"{Colors.CYAN}{char * width}{Colors.END}"

def get_box_border(text, padding=2):
    """Create a bordered box around text"""
    lines = text.split('\n')
    max_width = max(len(line) for line in lines) + (padding * 2)
    
    border = f"{Colors.CYAN}╭{'─' * max_width}╮{Colors.END}"
    content = []
    for line in lines:
        padded_line = f"{Colors.CYAN}│{Colors.END}{' ' * padding}{line}{' ' * (max_width - len(line) - padding)}{Colors.CYAN}│{Colors.END}"
        content.append(padded_line)
    bottom = f"{Colors.CYAN}╰{'─' * max_width}╯{Colors.END}"
    
    return '\n'.join([border] + content + [bottom])

def print_with_animation(text, delay=0.03):
    """Print text with typewriter animation"""
    import time
    import sys
    
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

if __name__ == "__main__":
    # Demo of ASCII art
    print(get_om_logo())
    print(get_mood_art(8))
    print(get_breathing_art())
    print(get_gratitude_art())
    print(get_daily_quote())
    print(get_quick_action_menu())
