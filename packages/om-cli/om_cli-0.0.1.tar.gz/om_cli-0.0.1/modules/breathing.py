"""
Breathing exercises module for om
"""

import time
import sys

def breathing_session(technique, duration):
    """Start a guided breathing session"""
    print(f"🫁 Starting {technique} breathing exercise for {duration} minutes")
    print("Press Ctrl+C to stop at any time\n")
    
    techniques = {
        'simple': simple_breathing,
        '4-7-8': four_seven_eight,
        'box': box_breathing
    }
    
    if technique not in techniques:
        print(f"❌ Unknown technique: {technique}")
        return
    
    start_time = time.time()
    end_time = start_time + (duration * 60)
    
    try:
        while time.time() < end_time:
            techniques[technique]()
    except KeyboardInterrupt:
        pass
    
    print("\n✨ Great job! You've completed your breathing session.")
    print("Take a moment to notice how you feel.")

def simple_breathing():
    """Simple in-out breathing"""
    print("💨 Breathe in slowly...", end="", flush=True)
    time.sleep(4)
    print(" Hold...", end="", flush=True)
    time.sleep(1)
    print(" Breathe out slowly...")
    time.sleep(4)
    print()

def four_seven_eight():
    """4-7-8 breathing technique"""
    print("💨 Inhale for 4...", end="", flush=True)
    for i in range(4):
        time.sleep(1)
        print(f" {i+1}", end="", flush=True)
    
    print(" | Hold for 7...", end="", flush=True)
    for i in range(7):
        time.sleep(1)
        print(f" {i+1}", end="", flush=True)
    
    print(" | Exhale for 8...", end="", flush=True)
    for i in range(8):
        time.sleep(1)
        print(f" {i+1}", end="", flush=True)
    print("\n")

def box_breathing():
    """Box breathing (4-4-4-4)"""
    steps = [
        ("Inhale", 4),
        ("Hold", 4),
        ("Exhale", 4),
        ("Hold", 4)
    ]
    
    for step_name, duration in steps:
        print(f"💨 {step_name} for {duration}...", end="", flush=True)
        for i in range(duration):
            time.sleep(1)
            print(f" {i+1}", end="", flush=True)
        print(" |", end="", flush=True)
    print("\n")
