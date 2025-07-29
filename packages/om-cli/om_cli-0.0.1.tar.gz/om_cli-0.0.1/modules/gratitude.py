"""
Gratitude practice module for om
"""

import json
import os
from datetime import datetime

GRATITUDE_FILE = os.path.expanduser("~/.om_gratitude.json")

def gratitude_practice(num_entries):
    """Interactive gratitude practice"""
    print("🙏 Welcome to your gratitude practice")
    print("Taking time to appreciate what we have can improve our mental well-being.")
    print(f"Let's think of {num_entries} things you're grateful for today.\n")
    
    entries = []
    
    for i in range(num_entries):
        while True:
            try:
                entry = input(f"💝 What are you grateful for today? ({i+1}/{num_entries}): ").strip()
                if entry:
                    entries.append(entry)
                    print(f"   Beautiful! {entry}")
                    break
                else:
                    print("   Please share something you're grateful for.")
            except EOFError:
                # Handle EOF gracefully (e.g., when input is piped)
                if entries:  # If we have at least one entry, that's enough
                    print(f"   Received {len(entries)} gratitude entries.")
                    break
                else:
                    entries.append("Being present in this moment")
                    print("   Beautiful! Being present in this moment")
                    break
        print()
    
    # Save entries
    save_gratitude_entries(entries)
    
    print("✨ Thank you for taking time to practice gratitude!")
    print("Research shows that regular gratitude practice can:")
    print("  • Improve mood and life satisfaction")
    print("  • Reduce stress and anxiety") 
    print("  • Strengthen relationships")
    print("  • Improve sleep quality")
    print("\nYour entries have been saved. Come back anytime! 🌟")

def save_gratitude_entries(entries):
    """Save gratitude entries to file"""
    try:
        # Load existing entries
        if os.path.exists(GRATITUDE_FILE):
            with open(GRATITUDE_FILE, 'r') as f:
                data = json.load(f)
        else:
            data = {"entries": []}
        
        # Add new entries
        timestamp = datetime.now().isoformat()
        for entry in entries:
            data["entries"].append({
                "text": entry,
                "date": timestamp
            })
        
        # Save back to file
        with open(GRATITUDE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        print(f"Note: Could not save entries ({e}), but your practice still counts!")

def show_gratitude_history():
    """Show previous gratitude entries"""
    if not os.path.exists(GRATITUDE_FILE):
        print("No previous gratitude entries found.")
        return
    
    try:
        with open(GRATITUDE_FILE, 'r') as f:
            data = json.load(f)
        
        entries = data.get("entries", [])
        if not entries:
            print("No gratitude entries found.")
            return
        
        print("🙏 Your gratitude journey:")
        print("-" * 40)
        
        for entry in entries[-10:]:  # Show last 10 entries
            date = datetime.fromisoformat(entry["date"]).strftime("%Y-%m-%d")
            print(f"{date}: {entry['text']}")
        
        if len(entries) > 10:
            print(f"\n... and {len(entries) - 10} more entries")
            
    except Exception as e:
        print(f"Could not load gratitude history: {e}")
