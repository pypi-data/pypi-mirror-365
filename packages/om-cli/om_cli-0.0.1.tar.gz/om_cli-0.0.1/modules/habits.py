"""
Habit tracking module for om
"""

import json
import os
from datetime import datetime, date

HABITS_FILE = os.path.expanduser("~/.om_habits.json")

def habit_tracker(action):
    """Main habit tracking interface"""
    actions = {
        'add': add_habit,
        'check': check_habit,
        'list': list_habits,
        'stats': show_stats
    }
    
    if action not in actions:
        print(f"❌ Unknown action: {action}")
        return
    
    actions[action]()

def add_habit():
    """Add a new habit to track"""
    print("🌱 Let's add a new habit to track!")
    print("Building healthy habits is key to mental wellness.")
    print()
    
    habit_name = input("What habit would you like to track? ").strip()
    if not habit_name:
        print("Please enter a habit name.")
        return
    
    description = input("Brief description (optional): ").strip()
    
    # Ask for frequency (optional enhancement)
    print("\nHow often do you want to track this habit?")
    print("1. Daily (default)")
    print("2. Weekly") 
    print("3. Custom")
    
    try:
        freq_choice = input("Choose frequency (1-3, default: 1): ").strip()
        if freq_choice == "2":
            frequency = "weekly"
        elif freq_choice == "3":
            frequency = input("Enter custom frequency: ").strip() or "daily"
        else:
            frequency = "daily"
    except (EOFError, KeyboardInterrupt):
        frequency = "daily"
    
    habit = {
        "name": habit_name,
        "description": description,
        "frequency": frequency,
        "created": datetime.now().isoformat(),
        "completions": []
    }
    
    habits = load_habits()
    habits.append(habit)
    save_habits(habits)
    
    print(f"\n✅ Added {frequency} habit: {habit_name}")
    if description:
        print(f"   Description: {description}")
    print("\n💡 Next steps:")
    print("  • Use 'om habits check' to mark it as complete")
    print("  • Use 'om h' for quick access to your habits")
    print("  • Build consistency - even small steps count!")

def check_habit():
    """Mark a habit as completed for today"""
    habits = load_habits()
    
    if not habits:
        print("No habits found. Add one with 'om habits --action add'")
        return
    
    print("📋 Your habits:")
    for i, habit in enumerate(habits, 1):
        today_str = date.today().isoformat()
        completed_today = today_str in habit.get("completions", [])
        status = "✅" if completed_today else "⭕"
        print(f"{i}. {status} {habit['name']}")
    
    try:
        choice = int(input("\nWhich habit did you complete today? (number): ")) - 1
        if 0 <= choice < len(habits):
            today_str = date.today().isoformat()
            
            if today_str not in habits[choice].get("completions", []):
                habits[choice].setdefault("completions", []).append(today_str)
                save_habits(habits)
                print(f"🎉 Great job completing: {habits[choice]['name']}")
            else:
                print("You already marked this habit as complete today!")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Please enter a valid number.")

def list_habits():
    """List all habits with recent completion status"""
    habits = load_habits()
    
    if not habits:
        print("🌱 No habits found yet!")
        print("\n💡 Getting started:")
        print("  • Add your first habit with 'om habits add'")
        print("  • Start small - consistency beats perfection")
        print("  • Examples: 'Daily meditation', 'Morning walk', 'Gratitude practice'")
        return
    
    print("🌱 Your Habit Garden:")
    print("=" * 60)
    
    today = date.today()
    
    for i, habit in enumerate(habits, 1):
        completions = habit.get("completions", [])
        today_str = today.isoformat()
        completed_today = today_str in completions
        
        # Calculate streak
        streak = calculate_streak(completions)
        
        # Get frequency
        frequency = habit.get("frequency", "daily")
        
        status = "✅" if completed_today else "⭕"
        print(f"{i}. {status} {habit['name']}")
        
        if habit.get('description'):
            print(f"     📝 {habit['description']}")
        
        print(f"     📊 Streak: {streak} days | Total: {len(completions)} | Frequency: {frequency}")
        
        # Show encouragement based on streak
        if streak == 0:
            print("     💪 Ready to start your streak!")
        elif streak < 3:
            print("     🌱 Great start! Keep building momentum")
        elif streak < 7:
            print("     🔥 You're on fire! Consistency is key")
        elif streak < 30:
            print("     ⭐ Amazing streak! You're building a strong habit")
        else:
            print("     🏆 Incredible dedication! This is a lifestyle now")
        
        print()
    
    print("💡 Quick tips:")
    print("  • Use 'om h check' to mark habits complete")
    print("  • Small daily actions create lasting change")
    print("  • Celebrate your progress, no matter how small!")

def show_stats():
    """Show habit statistics"""
    habits = load_habits()
    
    if not habits:
        print("No habits found. Add one with 'om habits --action add'")
        return
    
    print("📊 Habit Statistics")
    print("-" * 30)
    
    for habit in habits:
        completions = habit.get("completions", [])
        streak = calculate_streak(completions)
        
        print(f"🌱 {habit['name']}")
        print(f"   Total completions: {len(completions)}")
        print(f"   Current streak: {streak} days")
        print(f"   Created: {datetime.fromisoformat(habit['created']).strftime('%Y-%m-%d')}")
        print()

def calculate_streak(completions):
    """Calculate current streak of consecutive days"""
    if not completions:
        return 0
    
    # Sort completions in reverse order (most recent first)
    sorted_completions = sorted(completions, reverse=True)
    
    streak = 0
    current_date = date.today()
    
    for completion_str in sorted_completions:
        completion_date = date.fromisoformat(completion_str)
        
        if completion_date == current_date:
            streak += 1
            current_date = date.fromordinal(current_date.toordinal() - 1)
        else:
            break
    
    return streak

def load_habits():
    """Load habits from file"""
    if not os.path.exists(HABITS_FILE):
        return []
    
    try:
        with open(HABITS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return []

def save_habits(habits):
    """Save habits to file"""
    try:
        with open(HABITS_FILE, 'w') as f:
            json.dump(habits, f, indent=2)
    except Exception as e:
        print(f"Could not save habits: {e}")

def run(args=None):
    """Main entry point for the habits module"""
    if not args:
        # Default action - show habits list
        list_habits()
        print("\n💡 Available actions:")
        print("  om habits add     - Add a new habit")
        print("  om habits check   - Mark habit as complete")
        print("  om habits list    - Show all habits")
        print("  om habits stats   - Show habit statistics")
        return
    
    action = args[0].lower() if args else 'list'
    
    if action in ['add', 'new', 'create']:
        add_habit()
    elif action in ['check', 'complete', 'done']:
        check_habit()
    elif action in ['list', 'show', 'all']:
        list_habits()
    elif action in ['stats', 'statistics', 'report']:
        show_stats()
    else:
        print(f"❌ Unknown action: {action}")
        print("Available actions: add, check, list, stats")

def main():
    """Alternative entry point for direct execution"""
    import sys
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    run(args)

if __name__ == "__main__":
    main()
