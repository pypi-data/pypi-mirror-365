#!/usr/bin/env python3
"""
Demo script to showcase the beautiful om achievements gallery
Shows the difference between text and visual modes
"""

import os
import subprocess
import sys

def main():
    print("🧘‍♀️ om Mental Health CLI - Achievements Demo")
    print("=" * 50)
    print()
    
    print("This demo shows the difference between:")
    print("• Simple text mode (for daily use)")
    print("• Beautiful visual mode (for celebration)")
    print()
    
    # Show text mode first
    print("1️⃣ TEXT MODE (om gamify status)")
    print("─" * 30)
    subprocess.run([sys.executable, "main.py", "gamify", "status"])
    print()
    
    input("Press Enter to see the beautiful visual mode...")
    print()
    
    print("2️⃣ VISUAL MODE (om gamify status -v)")
    print("─" * 30)
    print("🎨 Launching beautiful achievements gallery...")
    print("✨ Use 'q' to quit when you're done exploring!")
    print()
    
    # Launch visual mode
    subprocess.run([sys.executable, "main.py", "gamify", "status", "-v"])
    
    print()
    print("🌟 That's the power of the -v flag!")
    print("• Quick text for daily check-ins")
    print("• Beautiful visuals for celebrating progress")
    print("• Same data, different experiences based on your mood")

if __name__ == "__main__":
    # Change to the om directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    main()
