#!/usr/bin/env python3
"""
Visual Achievements Integration for om
Bridges the gap between text-based gamification and beautiful Textual gallery
"""

import sys
import os
import subprocess
from typing import List, Optional

def launch_achievements_gallery():
    """Launch the beautiful Textual achievements gallery"""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        gallery_path = os.path.join(script_dir, 'achievements_gallery.py')
        
        # Launch the achievements gallery
        subprocess.run([sys.executable, gallery_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching achievements gallery: {e}")
        return False
    except FileNotFoundError:
        print("❌ Achievements gallery not found. Please ensure achievements_gallery.py exists.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def handle_gamify_visual(args: List[str]) -> bool:
    """Handle gamify command with visual flag"""
    
    # Check if visual flag is present
    visual_mode = False
    cleaned_args = []
    
    for arg in args:
        if arg in ['-v', '--visual']:
            visual_mode = True
        else:
            cleaned_args.append(arg)
    
    # If visual mode requested, launch the beautiful gallery
    if visual_mode:
        print("🎨 Launching beautiful achievements gallery...")
        print("✨ Celebrating your mental wellness journey!")
        print()
        return launch_achievements_gallery()
    
    # Otherwise, return False to let the normal text-based command handle it
    return False

def handle_dashboard_visual(args: List[str]) -> bool:
    """Handle dashboard command with visual flag (future implementation)"""
    
    # Check if visual flag is present
    visual_mode = False
    for arg in args:
        if arg in ['-v', '--visual']:
            visual_mode = True
            break
    
    if visual_mode:
        print("🎨 Visual dashboard coming soon!")
        print("✨ For now, enjoy the text-based dashboard")
        return False
    
    return False

def handle_coach_visual(args: List[str]) -> bool:
    """Handle coach command with visual flag (future implementation)"""
    
    # Check if visual flag is present
    visual_mode = False
    for arg in args:
        if arg in ['-v', '--visual']:
            visual_mode = True
            break
    
    if visual_mode:
        print("🎨 Visual AI coaching analysis coming soon!")
        print("✨ For now, enjoy the text-based coaching")
        return False
    
    return False

# Main visual command router
VISUAL_HANDLERS = {
    'gamify': handle_gamify_visual,
    'game': handle_gamify_visual,
    'achievements': handle_gamify_visual,
    'dashboard': handle_dashboard_visual,
    'coach': handle_coach_visual,
}

def handle_visual_command(command: str, args: List[str]) -> bool:
    """
    Handle visual commands with -v flag
    Returns True if handled visually, False if should fall back to text
    """
    
    if command in VISUAL_HANDLERS:
        return VISUAL_HANDLERS[command](args)
    
    return False

if __name__ == "__main__":
    # Test the achievements gallery
    print("🧪 Testing achievements gallery...")
    launch_achievements_gallery()
