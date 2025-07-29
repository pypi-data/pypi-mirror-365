#!/usr/bin/env python3
"""
Test script for Om Mental Health Database
Simple CLI interface to test database functionality
"""

import sys
from om_database import OmDatabase
from datetime import datetime
import json

def main():
    """Main test interface"""
    print("🧘‍♀️ Om Mental Health Database Test Interface")
    print("=" * 50)
    
    # Initialize database
    try:
        db = OmDatabase()
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Initialize achievements
    try:
        db.initialize_achievements()
        print("✅ Achievements initialized")
    except Exception as e:
        print(f"⚠️  Achievement initialization: {e}")
    
    while True:
        print("\n" + "=" * 50)
        print("Choose an option:")
        print("1. Add mood entry")
        print("2. Add wellness session")
        print("3. Add gratitude entry")
        print("4. View dashboard")
        print("5. View user stats")
        print("6. Add autopilot task")
        print("7. View pending tasks")
        print("8. Check achievements")
        print("9. Export data")
        print("10. Backup database")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-10): ").strip()
        
        try:
            if choice == "1":
                test_mood_entry(db)
            elif choice == "2":
                test_wellness_session(db)
            elif choice == "3":
                test_gratitude_entry(db)
            elif choice == "4":
                test_dashboard(db)
            elif choice == "5":
                test_user_stats(db)
            elif choice == "6":
                test_autopilot_task(db)
            elif choice == "7":
                test_pending_tasks(db)
            elif choice == "8":
                test_achievements(db)
            elif choice == "9":
                test_export_data(db)
            elif choice == "10":
                test_backup(db)
            elif choice == "0":
                print("👋 Goodbye! Take care of your mental health.")
                break
            else:
                print("❌ Invalid choice. Please try again.")
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    db.close()

def test_mood_entry(db):
    """Test adding a mood entry"""
    print("\n📊 Adding Mood Entry")
    print("-" * 20)
    
    mood_score = int(input("Mood score (1-10): "))
    energy_level = int(input("Energy level (1-10): "))
    stress_level = int(input("Stress level (1-10): "))
    anxiety_level = int(input("Anxiety level (1-10): "))
    notes = input("Notes (optional): ").strip() or None
    
    triggers_input = input("Triggers (comma-separated, optional): ").strip()
    triggers = [t.strip() for t in triggers_input.split(",")] if triggers_input else None
    
    coping_input = input("Coping strategies (comma-separated, optional): ").strip()
    coping = [c.strip() for c in coping_input.split(",")] if coping_input else None
    
    entry_id = db.add_mood_entry(
        mood_score=mood_score,
        energy_level=energy_level,
        stress_level=stress_level,
        anxiety_level=anxiety_level,
        notes=notes,
        triggers=triggers,
        coping_strategies=coping
    )
    
    # Award XP and points
    db.add_xp_and_points(10, 5, "Mood entry completed")
    db.check_achievements()
    
    print(f"✅ Mood entry added successfully! ID: {entry_id}")

def test_wellness_session(db):
    """Test adding a wellness session"""
    print("\n🧘 Adding Wellness Session")
    print("-" * 25)
    
    session_types = ["breathing", "meditation", "gratitude", "physical", "mindfulness"]
    print(f"Session types: {', '.join(session_types)}")
    session_type = input("Session type: ").strip()
    
    technique = input("Technique (optional): ").strip() or None
    duration = int(input("Duration in seconds: "))
    effectiveness = int(input("Effectiveness rating (1-10): "))
    notes = input("Notes (optional): ").strip() or None
    
    session_id = db.add_wellness_session(
        session_type=session_type,
        technique=technique,
        duration_seconds=duration,
        effectiveness_rating=effectiveness,
        notes=notes
    )
    
    # Award XP and points
    xp_reward = 15 if session_type == "meditation" else 10
    db.add_xp_and_points(xp_reward, 8, f"{session_type} session completed")
    db.check_achievements()
    
    print(f"✅ Wellness session added successfully! ID: {session_id}")

def test_gratitude_entry(db):
    """Test adding a gratitude entry"""
    print("\n🙏 Adding Gratitude Entry")
    print("-" * 22)
    
    gratitude_text = input("What are you grateful for? ")
    
    categories = ["people", "experiences", "things", "health", "opportunities"]
    print(f"Categories: {', '.join(categories)}")
    category = input("Category (optional): ").strip() or None
    
    intensity = input("Intensity (1-10, optional): ").strip()
    intensity = int(intensity) if intensity else None
    
    entry_id = db.add_gratitude_entry(
        gratitude_text=gratitude_text,
        category=category,
        intensity=intensity
    )
    
    # Award XP and points
    db.add_xp_and_points(8, 5, "Gratitude practice completed")
    db.check_achievements()
    
    print(f"✅ Gratitude entry added successfully! ID: {entry_id}")

def test_dashboard(db):
    """Test dashboard data retrieval"""
    print("\n📈 Dashboard Data")
    print("-" * 15)
    
    dashboard = db.get_dashboard_data()
    
    print(f"📊 User Stats:")
    stats = dashboard['user_stats']
    print(f"   Level: {stats['current_level']}")
    print(f"   Total XP: {stats['total_xp']}")
    print(f"   Wellness Points: {stats['wellness_points']}")
    print(f"   Current Streak: {stats['current_streak']}")
    print(f"   Total Sessions: {stats['total_sessions']}")
    print(f"   Total Mood Entries: {stats['total_mood_entries']}")
    
    print(f"\n📝 Recent Moods: {len(dashboard['recent_moods'])} entries")
    print(f"🧘 Wellness Stats: {len(dashboard['wellness_stats'])} activity types")
    print(f"📋 Pending Tasks: {len(dashboard['pending_tasks'])} tasks")
    print(f"🧠 Daily Insights: {len(dashboard['daily_insights'])} insights")

def test_user_stats(db):
    """Test user statistics"""
    print("\n👤 User Statistics")
    print("-" * 17)
    
    stats = db.get_user_stats()
    
    for key, value in stats.items():
        if key not in ['created_at', 'updated_at']:
            print(f"   {key.replace('_', ' ').title()}: {value}")

def test_autopilot_task(db):
    """Test adding an autopilot task"""
    print("\n🤖 Adding Autopilot Task")
    print("-" * 22)
    
    task_types = ["breathing", "mood_check", "gratitude", "physical", "mindfulness"]
    print(f"Task types: {', '.join(task_types)}")
    task_type = input("Task type: ").strip()
    
    title = input("Task title: ").strip()
    description = input("Description (optional): ").strip() or None
    priority = int(input("Priority (1-5): "))
    duration = input("Estimated duration (minutes, optional): ").strip()
    duration = int(duration) if duration else None
    
    task_id = db.add_autopilot_task(
        task_type=task_type,
        title=title,
        description=description,
        priority=priority,
        estimated_duration=duration
    )
    
    print(f"✅ Autopilot task added successfully! ID: {task_id}")

def test_pending_tasks(db):
    """Test viewing pending tasks"""
    print("\n📋 Pending Tasks")
    print("-" * 14)
    
    tasks = db.get_pending_tasks()
    
    if not tasks:
        print("   No pending tasks found.")
        return
    
    for i, task in enumerate(tasks, 1):
        print(f"   {i}. {task['title']} ({task['task_type']})")
        print(f"      Priority: {task['priority']}/5")
        if task['description']:
            print(f"      Description: {task['description']}")
        if task['estimated_duration_minutes']:
            print(f"      Duration: {task['estimated_duration_minutes']} minutes")
        print()
    
    # Option to complete a task
    if input("Complete a task? (y/n): ").lower() == 'y':
        try:
            task_num = int(input("Task number: ")) - 1
            if 0 <= task_num < len(tasks):
                rating = int(input("Completion rating (1-10): "))
                notes = input("Completion notes (optional): ").strip() or None
                
                db.complete_autopilot_task(tasks[task_num]['id'], rating, notes)
                db.add_xp_and_points(12, 8, "Autopilot task completed")
                db.check_achievements()
                
                print("✅ Task completed successfully!")
            else:
                print("❌ Invalid task number.")
        except ValueError:
            print("❌ Invalid input.")

def test_achievements(db):
    """Test achievement checking"""
    print("\n🏆 Checking Achievements")
    print("-" * 21)
    
    # Check for new achievements
    db.check_achievements()
    
    # Get unlocked achievements
    query = """
    SELECT a.name, a.description, a.category, ua.unlocked_at
    FROM achievements a
    JOIN user_achievements ua ON a.id = ua.achievement_id
    WHERE ua.is_unlocked = 1
    ORDER BY ua.unlocked_at DESC
    """
    
    cursor = db.connection.execute(query)
    achievements = [dict(row) for row in cursor.fetchall()]
    
    if achievements:
        print("🎉 Unlocked Achievements:")
        for achievement in achievements:
            print(f"   🏆 {achievement['name']}")
            print(f"      {achievement['description']}")
            print(f"      Category: {achievement['category']}")
            if achievement['unlocked_at']:
                print(f"      Unlocked: {achievement['unlocked_at']}")
            print()
    else:
        print("   No achievements unlocked yet. Keep practicing wellness!")

def test_export_data(db):
    """Test data export"""
    print("\n📤 Exporting Data")
    print("-" * 15)
    
    export_types = ["full", "mood", "wellness", "stats"]
    print(f"Export types: {', '.join(export_types)}")
    export_type = input("Export type: ").strip()
    
    data = db.export_data(export_type)
    
    # Save to file
    filename = f"om_export_{export_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = f"/Users/alexanderstraub/Documents/Projekte/om/{filename}"
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"✅ Data exported to: {filepath}")
    print(f"   Records exported: {sum(len(v) if isinstance(v, list) else 1 for v in data.values())}")

def test_backup(db):
    """Test database backup"""
    print("\n💾 Creating Database Backup")
    print("-" * 26)
    
    backup_path = db.backup_database()
    print(f"✅ Database backed up to: {backup_path}")

if __name__ == "__main__":
    main()
