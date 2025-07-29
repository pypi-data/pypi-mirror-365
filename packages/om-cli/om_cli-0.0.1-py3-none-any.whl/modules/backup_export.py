#!/usr/bin/env python3
"""
Backup and Export Module for om - Inspired by Logbuch
Comprehensive data backup, export, and import functionality
"""

import os
import json
import datetime
import shutil
import zipfile
from pathlib import Path
from typing import Dict, List, Optional

def get_data_dir():
    """Get om data directory"""
    home = Path.home()
    data_dir = home / ".om" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def get_backup_dir():
    """Get backup directory"""
    home = Path.home()
    backup_dir = home / ".om" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir

def collect_all_data():
    """Collect all om data for backup"""
    data_dir = get_data_dir()
    
    backup_data = {
        "created_at": datetime.datetime.now().isoformat(),
        "version": "2.0",
        "om_version": "2.0.0",
        "data": {}
    }
    
    # Data files to backup
    data_files = [
        "mood_entries.json",
        "wellness_sessions.json", 
        "daily_checkins.json",
        "gratitude_entries.json",
        "achievements.json",
        "habits.json",
        "goals.json",
        "sleep_entries.json",
        "stress_levels.json",
        "user_data.json",
        "coaching_insights.json",
        "autopilot_tasks.json",
        "wellness_stats.json"
    ]
    
    for filename in data_files:
        file_path = data_dir / filename
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    backup_data["data"][filename.replace('.json', '')] = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                backup_data["data"][filename.replace('.json', '')] = None
        else:
            backup_data["data"][filename.replace('.json', '')] = None
    
    # Add metadata
    backup_data["metadata"] = {
        "total_files": len([f for f in data_files if (data_dir / f).exists()]),
        "data_size": sum((data_dir / f).stat().st_size for f in data_files if (data_dir / f).exists()),
        "backup_type": "full",
        "platform": "om_mental_health"
    }
    
    return backup_data

def create_backup(backup_name=None, auto=False):
    """Create a comprehensive backup"""
    print("💾 Creating om backup...")
    
    if not backup_name:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"om_backup_{timestamp}"
    
    backup_dir = get_backup_dir()
    backup_path = backup_dir / f"{backup_name}.json"
    
    try:
        # Collect data
        print("📊 Collecting wellness data...")
        backup_data = collect_all_data()
        
        # Save backup
        print("💾 Saving backup...")
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        # Create compressed version
        zip_path = backup_dir / f"{backup_name}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(backup_path, f"{backup_name}.json")
        
        # Get file sizes
        json_size = backup_path.stat().st_size
        zip_size = zip_path.stat().st_size
        
        print("✅ Backup created successfully!")
        print(f"   Location: {backup_path}")
        print(f"   Compressed: {zip_path}")
        print(f"   Size: {json_size:,} bytes ({zip_size:,} bytes compressed)")
        print(f"   Files backed up: {backup_data['metadata']['total_files']}")
        
        if not auto:
            print(f"\n💡 To restore: om backup restore {backup_name}")
        
        return backup_path
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def list_backups():
    """List available backups"""
    backup_dir = get_backup_dir()
    
    # Find backup files
    json_backups = list(backup_dir.glob("*.json"))
    zip_backups = list(backup_dir.glob("*.zip"))
    
    if not json_backups and not zip_backups:
        print("No backups found. Create one with: om backup create")
        return
    
    print("📋 Available Backups")
    print("=" * 40)
    
    # Combine and sort by date
    all_backups = []
    
    for backup_file in json_backups:
        try:
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
                created_at = backup_data.get("created_at", "Unknown")
                version = backup_data.get("version", "Unknown")
                file_count = backup_data.get("metadata", {}).get("total_files", 0)
                
                all_backups.append({
                    "name": backup_file.stem,
                    "path": backup_file,
                    "created_at": created_at,
                    "version": version,
                    "file_count": file_count,
                    "size": backup_file.stat().st_size,
                    "type": "JSON"
                })
        except (json.JSONDecodeError, FileNotFoundError):
            continue
    
    for zip_file in zip_backups:
        # Check if corresponding JSON exists
        json_name = zip_file.stem
        if not any(b["name"] == json_name for b in all_backups):
            all_backups.append({
                "name": json_name,
                "path": zip_file,
                "created_at": "Unknown",
                "version": "Unknown", 
                "file_count": "Unknown",
                "size": zip_file.stat().st_size,
                "type": "ZIP"
            })
    
    # Sort by creation date
    all_backups.sort(key=lambda x: x["created_at"], reverse=True)
    
    for backup in all_backups:
        created_date = "Unknown"
        if backup["created_at"] != "Unknown":
            try:
                date_obj = datetime.datetime.fromisoformat(backup["created_at"])
                created_date = date_obj.strftime("%Y-%m-%d %H:%M")
            except:
                pass
        
        print(f"📦 {backup['name']}")
        print(f"   Created: {created_date}")
        print(f"   Version: {backup['version']}")
        print(f"   Files: {backup['file_count']}")
        print(f"   Size: {backup['size']:,} bytes ({backup['type']})")
        print()

def restore_backup(backup_name):
    """Restore from backup"""
    backup_dir = get_backup_dir()
    
    # Try JSON first, then ZIP
    backup_path = backup_dir / f"{backup_name}.json"
    if not backup_path.exists():
        zip_path = backup_dir / f"{backup_name}.zip"
        if zip_path.exists():
            # Extract ZIP
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(backup_dir)
            backup_path = backup_dir / f"{backup_name}.json"
        else:
            print(f"❌ Backup '{backup_name}' not found")
            return False
    
    try:
        print(f"🔄 Restoring from backup: {backup_name}")
        
        # Load backup data
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
        
        # Confirm restore
        created_at = backup_data.get("created_at", "Unknown")
        version = backup_data.get("version", "Unknown")
        file_count = backup_data.get("metadata", {}).get("total_files", 0)
        
        print(f"   Created: {created_at}")
        print(f"   Version: {version}")
        print(f"   Files: {file_count}")
        
        confirm = input("\n⚠️  This will overwrite current data. Continue? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Restore cancelled.")
            return False
        
        # Create backup of current data first
        print("📦 Creating backup of current data...")
        current_backup = create_backup(f"pre_restore_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}", auto=True)
        
        # Restore data
        data_dir = get_data_dir()
        restored_files = 0
        
        for data_key, data_content in backup_data["data"].items():
            if data_content is not None:
                file_path = data_dir / f"{data_key}.json"
                with open(file_path, 'w') as f:
                    json.dump(data_content, f, indent=2)
                restored_files += 1
        
        print(f"✅ Restore completed!")
        print(f"   Restored {restored_files} data files")
        print(f"   Previous data backed up to: {current_backup.name if current_backup else 'backup failed'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return False

def export_data(format_type="json", date_range=None):
    """Export data in various formats"""
    print(f"📤 Exporting om data ({format_type.upper()})...")
    
    # Collect data
    backup_data = collect_all_data()
    
    # Apply date filtering if specified
    if date_range:
        backup_data = filter_data_by_date(backup_data, date_range)
    
    # Generate filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    export_dir = get_backup_dir() / "exports"
    export_dir.mkdir(exist_ok=True)
    
    if format_type.lower() == "json":
        export_path = export_dir / f"om_export_{timestamp}.json"
        with open(export_path, 'w') as f:
            json.dump(backup_data, f, indent=2)
    
    elif format_type.lower() == "csv":
        export_path = export_dir / f"om_export_{timestamp}.csv"
        export_to_csv(backup_data, export_path)
    
    elif format_type.lower() == "txt":
        export_path = export_dir / f"om_export_{timestamp}.txt"
        export_to_text(backup_data, export_path)
    
    else:
        print(f"❌ Unsupported format: {format_type}")
        return None
    
    print(f"✅ Export completed!")
    print(f"   Location: {export_path}")
    print(f"   Size: {export_path.stat().st_size:,} bytes")
    
    return export_path

def export_to_csv(backup_data, export_path):
    """Export data to CSV format"""
    import csv
    
    with open(export_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Export mood entries
        if backup_data["data"].get("mood_entries"):
            writer.writerow(["=== MOOD ENTRIES ==="])
            writer.writerow(["Date", "Mood", "Intensity", "Notes", "Triggers"])
            
            entries = backup_data["data"]["mood_entries"].get("entries", [])
            for entry in entries:
                writer.writerow([
                    entry.get("date", ""),
                    entry.get("mood", ""),
                    entry.get("intensity", ""),
                    entry.get("notes", ""),
                    ", ".join(entry.get("triggers", []))
                ])
            writer.writerow([])
        
        # Export daily check-ins
        if backup_data["data"].get("daily_checkins"):
            writer.writerow(["=== DAILY CHECK-INS ==="])
            writer.writerow(["Date", "Type", "Mood", "Energy", "Stress", "Going Well"])
            
            for checkin in backup_data["data"]["daily_checkins"]:
                writer.writerow([
                    checkin.get("date", ""),
                    checkin.get("type", ""),
                    checkin.get("mood", ""),
                    checkin.get("energy_level", ""),
                    checkin.get("stress_level", ""),
                    checkin.get("going_well", "")
                ])
            writer.writerow([])
        
        # Export gratitude entries
        if backup_data["data"].get("gratitude_entries"):
            writer.writerow(["=== GRATITUDE ENTRIES ==="])
            writer.writerow(["Date", "Content", "Source"])
            
            for entry in backup_data["data"]["gratitude_entries"]:
                writer.writerow([
                    entry.get("date", ""),
                    entry.get("content", ""),
                    entry.get("source", "")
                ])

def export_to_text(backup_data, export_path):
    """Export data to readable text format"""
    with open(export_path, 'w') as f:
        f.write("om Mental Health Data Export\n")
        f.write("=" * 40 + "\n")
        f.write(f"Generated: {backup_data['created_at']}\n")
        f.write(f"Version: {backup_data['version']}\n\n")
        
        # Mood entries
        if backup_data["data"].get("mood_entries"):
            f.write("MOOD ENTRIES\n")
            f.write("-" * 20 + "\n")
            
            entries = backup_data["data"]["mood_entries"].get("entries", [])
            for entry in entries[-20:]:  # Last 20 entries
                date_obj = datetime.datetime.fromisoformat(entry["date"])
                date_str = date_obj.strftime("%Y-%m-%d %H:%M")
                
                f.write(f"{date_str}: {entry['mood']}")
                if entry.get("intensity"):
                    f.write(f" ({entry['intensity']}/10)")
                f.write("\n")
                
                if entry.get("notes"):
                    f.write(f"  Notes: {entry['notes']}\n")
                if entry.get("triggers"):
                    f.write(f"  Triggers: {', '.join(entry['triggers'])}\n")
                f.write("\n")
        
        # Daily check-ins
        if backup_data["data"].get("daily_checkins"):
            f.write("\nDAILY CHECK-INS\n")
            f.write("-" * 20 + "\n")
            
            for checkin in backup_data["data"]["daily_checkins"][-10:]:  # Last 10
                date_obj = datetime.datetime.fromisoformat(checkin["date"])
                date_str = date_obj.strftime("%Y-%m-%d %H:%M")
                
                f.write(f"{date_str} - {checkin.get('type', 'checkin').title()}\n")
                if checkin.get("mood"):
                    f.write(f"  Mood: {checkin['mood']}\n")
                if checkin.get("energy_level"):
                    f.write(f"  Energy: {checkin['energy_level']}/10\n")
                if checkin.get("stress_level"):
                    f.write(f"  Stress: {checkin['stress_level']}/10\n")
                if checkin.get("going_well"):
                    f.write(f"  Going well: {checkin['going_well']}\n")
                f.write("\n")

def filter_data_by_date(backup_data, date_range):
    """Filter backup data by date range"""
    # This would implement date filtering logic
    # For now, return all data
    return backup_data

def import_data(import_path):
    """Import data from file"""
    import_file = Path(import_path)
    
    if not import_file.exists():
        print(f"❌ Import file not found: {import_path}")
        return False
    
    try:
        print(f"📥 Importing data from: {import_file.name}")
        
        with open(import_file, 'r') as f:
            import_data = json.load(f)
        
        # Validate import data
        if not import_data.get("data"):
            print("❌ Invalid import file format")
            return False
        
        # Show import info
        version = import_data.get("version", "Unknown")
        created_at = import_data.get("created_at", "Unknown")
        file_count = import_data.get("metadata", {}).get("total_files", 0)
        
        print(f"   Version: {version}")
        print(f"   Created: {created_at}")
        print(f"   Files: {file_count}")
        
        confirm = input("\n⚠️  This will merge with current data. Continue? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Import cancelled.")
            return False
        
        # Import data
        data_dir = get_data_dir()
        imported_files = 0
        
        for data_key, data_content in import_data["data"].items():
            if data_content is not None:
                file_path = data_dir / f"{data_key}.json"
                
                # Merge with existing data if it exists
                existing_data = None
                if file_path.exists():
                    try:
                        with open(file_path, 'r') as f:
                            existing_data = json.load(f)
                    except:
                        pass
                
                # Simple merge strategy - combine lists
                if existing_data and isinstance(data_content, list) and isinstance(existing_data, list):
                    merged_data = existing_data + data_content
                    # Remove duplicates based on date if possible
                    seen_dates = set()
                    unique_data = []
                    for item in merged_data:
                        item_date = item.get("date")
                        if item_date and item_date not in seen_dates:
                            seen_dates.add(item_date)
                            unique_data.append(item)
                        elif not item_date:
                            unique_data.append(item)
                    data_content = unique_data
                
                with open(file_path, 'w') as f:
                    json.dump(data_content, f, indent=2)
                imported_files += 1
        
        print(f"✅ Import completed!")
        print(f"   Imported {imported_files} data files")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def backup_command(action="menu", *args):
    """Backup command handler"""
    if action == "menu" or not action:
        show_backup_menu()
    elif action == "create":
        backup_name = args[0] if args else None
        create_backup(backup_name)
    elif action == "list":
        list_backups()
    elif action == "restore":
        if args:
            restore_backup(args[0])
        else:
            print("Usage: om backup restore <backup_name>")
    elif action == "export":
        format_type = args[0] if args else "json"
        export_data(format_type)
    elif action == "import":
        if args:
            import_data(args[0])
        else:
            print("Usage: om backup import <file_path>")
    else:
        show_backup_menu()

def show_backup_menu():
    """Show backup menu"""
    print("💾 Backup & Export Options")
    print("=" * 30)
    print("1. Create backup")
    print("2. List backups")
    print("3. Restore backup")
    print("4. Export data (JSON)")
    print("5. Export data (CSV)")
    print("6. Import data")
    
    try:
        choice = input("\nChoose an option (1-6): ").strip()
        
        if choice == "1":
            create_backup()
        elif choice == "2":
            list_backups()
        elif choice == "3":
            list_backups()
            backup_name = input("\nEnter backup name to restore: ").strip()
            if backup_name:
                restore_backup(backup_name)
        elif choice == "4":
            export_data("json")
        elif choice == "5":
            export_data("csv")
        elif choice == "6":
            import_path = input("Enter import file path: ").strip()
            if import_path:
                import_data(import_path)
        else:
            print("Invalid choice")
    except KeyboardInterrupt:
        print("\n👋 Take care!")

if __name__ == "__main__":
    import sys
    args = sys.argv[1:] if len(sys.argv) > 1 else ["menu"]
    backup_command(*args)
