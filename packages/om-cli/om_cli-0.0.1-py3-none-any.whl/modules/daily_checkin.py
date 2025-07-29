#!/usr/bin/env python3
"""
Daily Check-in Module for om - Inspired by Logbuch
Comprehensive daily wellness check-in with smart follow-ups
"""

import os
import json
import datetime
from pathlib import Path

def get_data_dir():
    """Get om data directory"""
    home = Path.home()
    data_dir = home / ".om" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def save_checkin_data(data, filename):
    """Save check-in data to file"""
    file_path = get_data_dir() / filename
    
    # Load existing data
    existing_data = []
    if file_path.exists():
        try:
            with open(file_path, 'r') as f:
                existing_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    
    # Add new entry
    existing_data.insert(0, data)  # Most recent first
    
    # Keep only last 100 entries
    existing_data = existing_data[:100]
    
    # Save
    with open(file_path, 'w') as f:
        json.dump(existing_data, f, indent=2)

def get_mood_suggestions():
    """Get mood suggestions for check-in"""
    return [
        "energetic", "calm", "happy", "focused", "grateful",
        "tired", "stressed", "anxious", "neutral", "excited",
        "peaceful", "overwhelmed", "content", "restless", "optimistic"
    ]

def get_energy_level_description(level):
    """Get description for energy level"""
    descriptions = {
        1: "Completely drained",
        2: "Very low energy", 
        3: "Low energy",
        4: "Below average",
        5: "Average energy",
        6: "Above average",
        7: "Good energy",
        8: "High energy",
        9: "Very energetic",
        10: "Peak energy"
    }
    return descriptions.get(level, "Unknown")

def get_stress_level_description(level):
    """Get description for stress level"""
    descriptions = {
        1: "Completely relaxed",
        2: "Very relaxed",
        3: "Relaxed",
        4: "Slightly tense",
        5: "Moderate stress",
        6: "Somewhat stressed",
        7: "Stressed",
        8: "Very stressed",
        9: "Extremely stressed",
        10: "Overwhelmed"
    }
    return descriptions.get(level, "Unknown")

def daily_checkin_full():
    """Comprehensive daily check-in"""
    print("🌅 Daily Wellness Check-in")
    print("=" * 40)
    print("Take a moment to reflect on your current state...")
    print()
    
    checkin_data = {
        "date": datetime.datetime.now().isoformat(),
        "type": "full_checkin"
    }
    
    try:
        # Mood check
        print("😊 How are you feeling emotionally?")
        mood_suggestions = get_mood_suggestions()
        for i, mood in enumerate(mood_suggestions[:8], 1):
            print(f"{i}. {mood}")
        print("9. Other (type your own)")
        
        mood_choice = input("\nChoose a mood (1-9) or type directly: ").strip()
        
        if mood_choice.isdigit() and 1 <= int(mood_choice) <= 8:
            mood = mood_suggestions[int(mood_choice) - 1]
        elif mood_choice == "9":
            mood = input("Enter your mood: ").strip()
        else:
            mood = mood_choice
        
        checkin_data["mood"] = mood
        
        # Mood intensity
        intensity_str = input("Rate the intensity of this mood (1-10): ").strip()
        if intensity_str.isdigit() and 1 <= int(intensity_str) <= 10:
            checkin_data["mood_intensity"] = int(intensity_str)
        
        # Energy level
        print(f"\n⚡ Energy Level:")
        energy_str = input("Rate your energy level (1-10): ").strip()
        if energy_str.isdigit() and 1 <= int(energy_str) <= 10:
            energy_level = int(energy_str)
            checkin_data["energy_level"] = energy_level
            print(f"   {get_energy_level_description(energy_level)}")
        
        # Stress level
        print(f"\n😰 Stress Level:")
        stress_str = input("Rate your stress level (1-10): ").strip()
        if stress_str.isdigit() and 1 <= int(stress_str) <= 10:
            stress_level = int(stress_str)
            checkin_data["stress_level"] = stress_level
            print(f"   {get_stress_level_description(stress_level)}")
        
        # Sleep quality (if morning/afternoon)
        hour = datetime.datetime.now().hour
        if 6 <= hour <= 16:  # Morning to afternoon
            print(f"\n😴 Sleep Quality:")
            sleep_quality = input("How did you sleep last night? (poor/fair/good/excellent): ").strip().lower()
            if sleep_quality in ["poor", "fair", "good", "excellent"]:
                checkin_data["sleep_quality"] = sleep_quality
            
            sleep_hours = input("How many hours did you sleep? (optional): ").strip()
            if sleep_hours.replace('.', '').isdigit():
                checkin_data["sleep_hours"] = float(sleep_hours)
        
        # Physical symptoms
        print(f"\n🏥 Physical State:")
        symptoms = input("Any physical symptoms? (headache, fatigue, tension, etc. - optional): ").strip()
        if symptoms:
            checkin_data["physical_symptoms"] = symptoms.split(", ")
        
        # What's going well
        print(f"\n🌟 Positive Reflection:")
        going_well = input("What's going well today? ").strip()
        if going_well:
            checkin_data["going_well"] = going_well
        
        # Challenges
        print(f"\n⚠️ Challenges:")
        challenges = input("Any challenges or concerns? (optional): ").strip()
        if challenges:
            checkin_data["challenges"] = challenges
        
        # Goals for today
        print(f"\n🎯 Today's Focus:")
        daily_goal = input("What's your main focus/goal for today? ").strip()
        if daily_goal:
            checkin_data["daily_goal"] = daily_goal
        
        # Gratitude
        print(f"\n🙏 Gratitude:")
        gratitude = input("What are you grateful for today? ").strip()
        if gratitude:
            checkin_data["gratitude"] = gratitude
            # Save to gratitude file
            gratitude_entry = {
                "content": gratitude,
                "date": datetime.datetime.now().isoformat(),
                "source": "daily_checkin"
            }
            save_checkin_data(gratitude_entry, "gratitude_entries.json")
        
        # Self-care plan
        print(f"\n💆 Self-Care:")
        self_care = input("How will you take care of yourself today? ").strip()
        if self_care:
            checkin_data["self_care_plan"] = self_care
        
        # Save check-in data
        save_checkin_data(checkin_data, "daily_checkins.json")
        
        # Show summary
        print("\n✅ Daily Check-in Complete!")
        print("=" * 30)
        print(f"Mood: {mood}")
        if checkin_data.get("energy_level"):
            print(f"Energy: {checkin_data['energy_level']}/10")
        if checkin_data.get("stress_level"):
            print(f"Stress: {checkin_data['stress_level']}/10")
        if going_well:
            print(f"Going well: {going_well}")
        if daily_goal:
            print(f"Today's focus: {daily_goal}")
        
        # Smart recommendations
        provide_smart_recommendations(checkin_data)
        
    except KeyboardInterrupt:
        print("\n👋 Check-in cancelled. Take care!")

def daily_checkin_quick():
    """Quick daily check-in (2-3 minutes)"""
    print("⚡ Quick Daily Check-in")
    print("=" * 30)
    
    checkin_data = {
        "date": datetime.datetime.now().isoformat(),
        "type": "quick_checkin"
    }
    
    try:
        # Quick mood
        mood_suggestions = get_mood_suggestions()[:5]
        print("😊 How are you feeling?")
        for i, mood in enumerate(mood_suggestions, 1):
            print(f"{i}. {mood}")
        
        mood_choice = input("Choose (1-5) or type your mood: ").strip()
        if mood_choice.isdigit() and 1 <= int(mood_choice) <= 5:
            mood = mood_suggestions[int(mood_choice) - 1]
        else:
            mood = mood_choice
        
        checkin_data["mood"] = mood
        
        # Energy and stress (quick)
        energy = input("Energy level (1-10): ").strip()
        if energy.isdigit() and 1 <= int(energy) <= 10:
            checkin_data["energy_level"] = int(energy)
        
        stress = input("Stress level (1-10): ").strip()
        if stress.isdigit() and 1 <= int(stress) <= 10:
            checkin_data["stress_level"] = int(stress)
        
        # One thing going well
        going_well = input("One thing going well: ").strip()
        if going_well:
            checkin_data["going_well"] = going_well
        
        # One priority
        priority = input("Top priority today: ").strip()
        if priority:
            checkin_data["daily_priority"] = priority
        
        # Save data
        save_checkin_data(checkin_data, "daily_checkins.json")
        
        print(f"\n✅ Quick check-in complete! Mood: {mood}")
        
        # Quick recommendations
        provide_quick_recommendations(checkin_data)
        
    except KeyboardInterrupt:
        print("\n👋 Take care!")

def evening_checkin():
    """Evening reflection check-in"""
    print("🌙 Evening Reflection")
    print("=" * 25)
    
    checkin_data = {
        "date": datetime.datetime.now().isoformat(),
        "type": "evening_checkin"
    }
    
    try:
        # How was your day
        print("How was your day overall?")
        day_rating = input("Rate your day (1-10): ").strip()
        if day_rating.isdigit() and 1 <= int(day_rating) <= 10:
            checkin_data["day_rating"] = int(day_rating)
        
        # Accomplishments
        accomplishments = input("What did you accomplish today? ").strip()
        if accomplishments:
            checkin_data["accomplishments"] = accomplishments
        
        # Challenges faced
        challenges = input("What challenges did you face? ").strip()
        if challenges:
            checkin_data["challenges"] = challenges
        
        # Lessons learned
        lessons = input("What did you learn today? ").strip()
        if lessons:
            checkin_data["lessons_learned"] = lessons
        
        # Gratitude
        gratitude = input("What are you grateful for from today? ").strip()
        if gratitude:
            checkin_data["gratitude"] = gratitude
            # Save to gratitude file
            gratitude_entry = {
                "content": gratitude,
                "date": datetime.datetime.now().isoformat(),
                "source": "evening_checkin"
            }
            save_checkin_data(gratitude_entry, "gratitude_entries.json")
        
        # Tomorrow's intention
        tomorrow = input("What's your intention for tomorrow? ").strip()
        if tomorrow:
            checkin_data["tomorrow_intention"] = tomorrow
        
        # Current mood
        mood = input("How are you feeling right now? ").strip()
        if mood:
            checkin_data["evening_mood"] = mood
        
        # Save data
        save_checkin_data(checkin_data, "daily_checkins.json")
        
        print("\n✅ Evening reflection complete!")
        print("🌙 Rest well and take care of yourself.")
        
        # Evening recommendations
        provide_evening_recommendations(checkin_data)
        
    except KeyboardInterrupt:
        print("\n🌙 Good night!")

def provide_smart_recommendations(checkin_data):
    """Provide smart recommendations based on check-in data"""
    print("\n💡 Personalized Recommendations:")
    
    stress_level = checkin_data.get("stress_level", 5)
    energy_level = checkin_data.get("energy_level", 5)
    mood = checkin_data.get("mood", "").lower()
    
    recommendations = []
    
    # Stress-based recommendations
    if stress_level >= 7:
        recommendations.append("🫁 High stress detected: Try om qb (breathing exercise)")
        recommendations.append("🌍 Consider om qgr (grounding technique)")
    elif stress_level >= 5:
        recommendations.append("😌 Moderate stress: Try om qc (progressive relaxation)")
    
    # Energy-based recommendations
    if energy_level <= 3:
        recommendations.append("⚡ Low energy: Try om qe (energy boost techniques)")
        recommendations.append("☕ Consider a short break or gentle movement")
    elif energy_level >= 8:
        recommendations.append("🎯 High energy: Great time for om qf (focused work)")
    
    # Mood-based recommendations
    if any(word in mood for word in ["sad", "down", "low", "depressed"]):
        recommendations.append("💪 Try om qa (positive affirmations)")
        recommendations.append("🙏 Consider om qg (gratitude practice)")
    elif any(word in mood for word in ["anxious", "worried", "nervous"]):
        recommendations.append("🌍 Try om qgr (5-4-3-2-1 grounding)")
        recommendations.append("🫁 Consider om qb (calming breathing)")
    elif any(word in mood for word in ["happy", "good", "great", "excited"]):
        recommendations.append("🌟 Great mood! Consider om qg (gratitude to maintain positivity)")
    
    # Physical symptoms
    if checkin_data.get("physical_symptoms"):
        symptoms = checkin_data["physical_symptoms"]
        if any("tension" in s or "headache" in s for s in symptoms):
            recommendations.append("💆 Physical tension: Try om qs (quick stretch)")
    
    # Show recommendations
    for rec in recommendations[:3]:  # Show top 3
        print(f"   • {rec}")
    
    if not recommendations:
        print("   • You're doing well! Try om qg (gratitude) to maintain positivity")

def provide_quick_recommendations(checkin_data):
    """Provide quick recommendations"""
    stress_level = checkin_data.get("stress_level", 5)
    energy_level = checkin_data.get("energy_level", 5)
    
    if stress_level >= 6:
        print("💡 Try: om qb (2-minute breathing for stress relief)")
    elif energy_level <= 4:
        print("💡 Try: om qe (energy boost techniques)")
    else:
        print("💡 Try: om qf (focus reset for productivity)")

def provide_evening_recommendations(checkin_data):
    """Provide evening-specific recommendations"""
    day_rating = checkin_data.get("day_rating", 5)
    
    print("\n💡 Evening Suggestions:")
    if day_rating <= 4:
        print("   • Difficult day: Try om qc (progressive relaxation)")
        print("   • Consider om qa (positive affirmations)")
    elif day_rating >= 8:
        print("   • Great day! Try om qg (gratitude to celebrate)")
    
    print("   • Wind down: om qc (progressive relaxation)")
    print("   • If trouble sleeping: om insomnia")

def view_checkin_history(days=7):
    """View recent check-in history"""
    checkin_file = get_data_dir() / "daily_checkins.json"
    
    if not checkin_file.exists():
        print("No check-in history found. Start with: om checkin")
        return
    
    try:
        with open(checkin_file, 'r') as f:
            checkins = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print("No check-in history found.")
        return
    
    # Filter by days
    cutoff_date = datetime.date.today() - datetime.timedelta(days=days)
    recent_checkins = []
    
    for checkin in checkins:
        checkin_date = datetime.datetime.fromisoformat(checkin["date"]).date()
        if checkin_date >= cutoff_date:
            recent_checkins.append(checkin)
    
    if not recent_checkins:
        print(f"No check-ins in the last {days} days.")
        return
    
    print(f"📋 Check-in History (Last {days} days)")
    print("=" * 40)
    
    for checkin in recent_checkins:
        date_obj = datetime.datetime.fromisoformat(checkin["date"])
        date_str = date_obj.strftime("%m-%d %H:%M")
        checkin_type = checkin.get("type", "checkin").replace("_", " ").title()
        
        print(f"\n{date_str} - {checkin_type}")
        
        if checkin.get("mood"):
            mood_display = checkin["mood"]
            if checkin.get("mood_intensity"):
                mood_display += f" ({checkin['mood_intensity']}/10)"
            print(f"   Mood: {mood_display}")
        
        if checkin.get("energy_level"):
            print(f"   Energy: {checkin['energy_level']}/10")
        
        if checkin.get("stress_level"):
            print(f"   Stress: {checkin['stress_level']}/10")
        
        if checkin.get("going_well"):
            print(f"   Going well: {checkin['going_well']}")
        
        if checkin.get("daily_goal"):
            print(f"   Goal: {checkin['daily_goal']}")
        
        if checkin.get("day_rating"):
            print(f"   Day rating: {checkin['day_rating']}/10")

def daily_checkin_command(action="menu"):
    """Daily check-in command handler"""
    if action == "menu" or not action:
        show_checkin_menu()
    elif action == "full":
        daily_checkin_full()
    elif action == "quick":
        daily_checkin_quick()
    elif action == "evening":
        evening_checkin()
    elif action == "history":
        view_checkin_history()
    elif action == "week":
        view_checkin_history(7)
    elif action == "month":
        view_checkin_history(30)
    else:
        show_checkin_menu()

def show_checkin_menu():
    """Show check-in menu"""
    print("🌅 Daily Check-in Options")
    print("=" * 30)
    print("1. Full check-in (5-7 minutes)")
    print("2. Quick check-in (2-3 minutes)")
    print("3. Evening reflection")
    print("4. View history")
    print("5. Weekly summary")
    
    try:
        choice = input("\nChoose an option (1-5): ").strip()
        
        if choice == "1":
            daily_checkin_full()
        elif choice == "2":
            daily_checkin_quick()
        elif choice == "3":
            evening_checkin()
        elif choice == "4":
            view_checkin_history()
        elif choice == "5":
            view_checkin_history(7)
        else:
            print("Invalid choice")
    except KeyboardInterrupt:
        print("\n👋 Take care!")

if __name__ == "__main__":
    import sys
    args = sys.argv[1:] if len(sys.argv) > 1 else ["menu"]
    daily_checkin_command(*args)
