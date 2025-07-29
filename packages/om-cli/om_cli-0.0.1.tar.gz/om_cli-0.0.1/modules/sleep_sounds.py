#!/usr/bin/env python3
"""
Sleep Sounds & Insomnia Support Module for om Platform

This module provides comprehensive sleep support including nature sounds, white noise,
meditation sounds, and mental health-specific audio for better sleep quality.
Features include custom sound mixes, sleep timers, and integration with mood tracking.

Features:
- Nature sounds (rain, ocean, forest, etc.)
- White noise and brown noise variations
- Mental health-specific sounds (anxiety relief, depression support)
- Custom sound mixing and volume control
- Sleep timer with automatic fade-out
- Background playback support
- Sleep quality tracking and analytics
- Integration with mood and mental health data
"""

import json
import os
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sys
import subprocess
import signal

# Rich imports for beautiful terminal output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.text import Text
    from rich.columns import Columns
    from rich.align import Align
    from rich.layout import Layout
    from rich.live import Live
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

console = Console() if RICH_AVAILABLE else None

class SleepSoundsManager:
    """Manages sleep sounds, timers, and sleep quality tracking"""
    
    def __init__(self):
        self.db_path = os.path.expanduser("~/.om/sleep_sounds.db")
        self.sounds_dir = os.path.expanduser("~/.om/sounds")
        self.current_processes = []  # Track running audio processes
        self.timer_thread = None
        self.is_playing = False
        self.init_database()
        self.init_sounds_directory()
        
    def init_database(self):
        """Initialize the SQLite database for sleep tracking"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Sleep sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sleep_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration_minutes INTEGER,
                    sounds_used TEXT, -- JSON array of sounds
                    volume_levels TEXT, -- JSON object of sound:volume pairs
                    sleep_timer_minutes INTEGER,
                    quality_rating INTEGER CHECK(quality_rating >= 1 AND quality_rating <= 5),
                    mood_before TEXT,
                    mood_after TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Sound library table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sound_library (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    category TEXT NOT NULL,
                    file_path TEXT,
                    description TEXT,
                    duration_seconds INTEGER,
                    is_loopable BOOLEAN DEFAULT TRUE,
                    mental_health_tags TEXT, -- JSON array of tags
                    usage_count INTEGER DEFAULT 0,
                    avg_rating REAL DEFAULT 0.0,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Sound mixes table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sound_mixes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    sounds TEXT NOT NULL, -- JSON array of sound names
                    volumes TEXT NOT NULL, -- JSON object of sound:volume pairs
                    description TEXT,
                    category TEXT DEFAULT 'custom',
                    usage_count INTEGER DEFAULT 0,
                    is_favorite BOOLEAN DEFAULT FALSE,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Sleep quality analytics
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sleep_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL UNIQUE,
                    total_sessions INTEGER DEFAULT 0,
                    avg_duration REAL DEFAULT 0.0,
                    avg_quality REAL DEFAULT 0.0,
                    most_used_sounds TEXT, -- JSON array
                    sleep_efficiency REAL DEFAULT 0.0,
                    mood_improvement REAL DEFAULT 0.0
                )
            """)
            
            # User preferences
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    default_timer_minutes INTEGER DEFAULT 30,
                    default_volume INTEGER DEFAULT 50,
                    auto_fade_out BOOLEAN DEFAULT TRUE,
                    background_mode BOOLEAN DEFAULT TRUE,
                    preferred_categories TEXT, -- JSON array
                    notification_enabled BOOLEAN DEFAULT TRUE,
                    sleep_goal_hours REAL DEFAULT 8.0
                )
            """)
            
            conn.commit()
            
            # Initialize preferences if empty
            cursor = conn.execute("SELECT COUNT(*) FROM user_preferences")
            if cursor.fetchone()[0] == 0:
                conn.execute("INSERT INTO user_preferences DEFAULT VALUES")
                conn.commit()
    
    def init_sounds_directory(self):
        """Initialize the sounds directory and load default sound library"""
        os.makedirs(self.sounds_dir, exist_ok=True)
        
        # Check if sound library is already populated
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM sound_library")
            if cursor.fetchone()[0] > 0:
                return  # Already initialized
        
        # Default sound library (these would be actual audio files in a real implementation)
        default_sounds = [
            # Nature Sounds
            {
                'name': 'Rain on Leaves',
                'category': 'nature',
                'description': 'Gentle rain falling on forest leaves',
                'duration_seconds': 600,
                'mental_health_tags': ['anxiety', 'stress', 'relaxation'],
                'file_path': 'nature/rain_leaves.wav'
            },
            {
                'name': 'Ocean Waves',
                'category': 'nature',
                'description': 'Rhythmic ocean waves on a peaceful beach',
                'duration_seconds': 900,
                'mental_health_tags': ['anxiety', 'meditation', 'peace'],
                'file_path': 'nature/ocean_waves.wav'
            },
            {
                'name': 'Forest Ambience',
                'category': 'nature',
                'description': 'Birds chirping in a serene forest',
                'duration_seconds': 720,
                'mental_health_tags': ['depression', 'nature_therapy', 'grounding'],
                'file_path': 'nature/forest_ambience.wav'
            },
            {
                'name': 'Thunderstorm',
                'category': 'nature',
                'description': 'Distant thunder with gentle rain',
                'duration_seconds': 800,
                'mental_health_tags': ['insomnia', 'masking', 'deep_sleep'],
                'file_path': 'nature/thunderstorm.wav'
            },
            {
                'name': 'Mountain Stream',
                'category': 'nature',
                'description': 'Babbling brook in mountain setting',
                'duration_seconds': 650,
                'mental_health_tags': ['meditation', 'focus', 'tranquility'],
                'file_path': 'nature/mountain_stream.wav'
            },
            
            # White Noise Variations
            {
                'name': 'White Noise',
                'category': 'white_noise',
                'description': 'Classic white noise for masking',
                'duration_seconds': 3600,
                'mental_health_tags': ['tinnitus', 'focus', 'masking'],
                'file_path': 'white_noise/white_noise.wav'
            },
            {
                'name': 'Brown Noise',
                'category': 'white_noise',
                'description': 'Deep, rumbling brown noise',
                'duration_seconds': 3600,
                'mental_health_tags': ['adhd', 'concentration', 'deep_sleep'],
                'file_path': 'white_noise/brown_noise.wav'
            },
            {
                'name': 'Pink Noise',
                'category': 'white_noise',
                'description': 'Balanced pink noise for sleep',
                'duration_seconds': 3600,
                'mental_health_tags': ['sleep_quality', 'memory', 'restoration'],
                'file_path': 'white_noise/pink_noise.wav'
            },
            
            # Mental Health Specific
            {
                'name': 'Anxiety Relief Tones',
                'category': 'mental_health',
                'description': '432Hz tones for anxiety reduction',
                'duration_seconds': 1200,
                'mental_health_tags': ['anxiety', 'panic', 'calming'],
                'file_path': 'mental_health/anxiety_relief.wav'
            },
            {
                'name': 'Depression Support',
                'category': 'mental_health',
                'description': 'Uplifting frequencies for mood support',
                'duration_seconds': 900,
                'mental_health_tags': ['depression', 'mood_boost', 'energy'],
                'file_path': 'mental_health/depression_support.wav'
            },
            {
                'name': 'PTSD Grounding',
                'category': 'mental_health',
                'description': 'Grounding sounds for trauma recovery',
                'duration_seconds': 800,
                'mental_health_tags': ['ptsd', 'grounding', 'safety'],
                'file_path': 'mental_health/ptsd_grounding.wav'
            },
            {
                'name': 'ADHD Focus',
                'category': 'mental_health',
                'description': 'Binaural beats for ADHD focus',
                'duration_seconds': 1800,
                'mental_health_tags': ['adhd', 'focus', 'concentration'],
                'file_path': 'mental_health/adhd_focus.wav'
            },
            
            # Meditation & Mindfulness
            {
                'name': 'Tibetan Bowls',
                'category': 'meditation',
                'description': 'Healing Tibetan singing bowls',
                'duration_seconds': 1200,
                'mental_health_tags': ['meditation', 'healing', 'spiritual'],
                'file_path': 'meditation/tibetan_bowls.wav'
            },
            {
                'name': 'Om Chanting',
                'category': 'meditation',
                'description': 'Sacred Om mantra chanting',
                'duration_seconds': 900,
                'mental_health_tags': ['meditation', 'spiritual', 'centering'],
                'file_path': 'meditation/om_chanting.wav'
            },
            {
                'name': 'Mindfulness Bell',
                'category': 'meditation',
                'description': 'Gentle mindfulness bell intervals',
                'duration_seconds': 600,
                'mental_health_tags': ['mindfulness', 'presence', 'awareness'],
                'file_path': 'meditation/mindfulness_bell.wav'
            },
            
            # Urban & Modern
            {
                'name': 'Coffee Shop',
                'category': 'ambient',
                'description': 'Cozy coffee shop atmosphere',
                'duration_seconds': 1200,
                'mental_health_tags': ['social_anxiety', 'comfort', 'familiarity'],
                'file_path': 'ambient/coffee_shop.wav'
            },
            {
                'name': 'Library Ambience',
                'category': 'ambient',
                'description': 'Quiet library with subtle sounds',
                'duration_seconds': 1800,
                'mental_health_tags': ['study', 'focus', 'calm'],
                'file_path': 'ambient/library.wav'
            },
            {
                'name': 'Fireplace',
                'category': 'ambient',
                'description': 'Crackling fireplace warmth',
                'duration_seconds': 900,
                'mental_health_tags': ['comfort', 'warmth', 'security'],
                'file_path': 'ambient/fireplace.wav'
            }
        ]
        
        # Insert default sounds into database
        with sqlite3.connect(self.db_path) as conn:
            for sound in default_sounds:
                conn.execute("""
                    INSERT INTO sound_library 
                    (name, category, description, duration_seconds, mental_health_tags, file_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    sound['name'],
                    sound['category'],
                    sound['description'],
                    sound['duration_seconds'],
                    json.dumps(sound['mental_health_tags']),
                    sound['file_path']
                ))
            
            conn.commit()
    
    def get_sounds_by_category(self, category: str = None) -> List[Dict]:
        """Get sounds by category or all sounds"""
        with sqlite3.connect(self.db_path) as conn:
            if category:
                cursor = conn.execute("""
                    SELECT name, category, description, duration_seconds, mental_health_tags, usage_count, avg_rating
                    FROM sound_library 
                    WHERE category = ? AND is_active = TRUE
                    ORDER BY usage_count DESC, name
                """, (category,))
            else:
                cursor = conn.execute("""
                    SELECT name, category, description, duration_seconds, mental_health_tags, usage_count, avg_rating
                    FROM sound_library 
                    WHERE is_active = TRUE
                    ORDER BY category, usage_count DESC, name
                """)
            
            sounds = []
            for row in cursor.fetchall():
                sounds.append({
                    'name': row[0],
                    'category': row[1],
                    'description': row[2],
                    'duration_seconds': row[3],
                    'mental_health_tags': json.loads(row[4]) if row[4] else [],
                    'usage_count': row[5],
                    'avg_rating': row[6] or 0.0
                })
            
            return sounds
    
    def get_categories(self) -> List[Dict]:
        """Get all available sound categories"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT category, COUNT(*) as count, AVG(avg_rating) as avg_rating
                FROM sound_library 
                WHERE is_active = TRUE
                GROUP BY category
                ORDER BY count DESC
            """)
            
            categories = []
            category_descriptions = {
                'nature': 'Natural sounds like rain, ocean, and forest',
                'white_noise': 'White, brown, and pink noise for masking',
                'mental_health': 'Specialized sounds for mental health support',
                'meditation': 'Meditation and mindfulness sounds',
                'ambient': 'Urban and atmospheric background sounds'
            }
            
            for row in cursor.fetchall():
                categories.append({
                    'name': row[0],
                    'count': row[1],
                    'avg_rating': row[2] or 0.0,
                    'description': category_descriptions.get(row[0], 'Sound category')
                })
            
            return categories
    
    def search_sounds_by_mental_health_tag(self, tag: str) -> List[Dict]:
        """Search sounds by mental health tags"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT name, category, description, duration_seconds, mental_health_tags, avg_rating
                FROM sound_library 
                WHERE mental_health_tags LIKE ? AND is_active = TRUE
                ORDER BY avg_rating DESC, usage_count DESC
            """, (f'%{tag}%',))
            
            sounds = []
            for row in cursor.fetchall():
                tags = json.loads(row[4]) if row[4] else []
                if tag.lower() in [t.lower() for t in tags]:
                    sounds.append({
                        'name': row[0],
                        'category': row[1],
                        'description': row[2],
                        'duration_seconds': row[3],
                        'mental_health_tags': tags,
                        'avg_rating': row[5] or 0.0
                    })
            
            return sounds
    
    def create_sound_mix(self, name: str, sounds: List[str], volumes: Dict[str, int], description: str = "") -> bool:
        """Create a custom sound mix"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO sound_mixes (name, sounds, volumes, description)
                    VALUES (?, ?, ?, ?)
                """, (name, json.dumps(sounds), json.dumps(volumes), description))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Mix name already exists

def display_sound_categories(categories: List[Dict]):
    """Display available sound categories"""
    if not categories:
        if console:
            console.print("[yellow]No sound categories available.[/yellow]")
        else:
            print("No sound categories available.")
        return
    
    if not RICH_AVAILABLE:
        print("\nSleep Sound Categories:")
        print("=" * 30)
        for cat in categories:
            print(f"• {cat['name'].title()}: {cat['description']} ({cat['count']} sounds)")
            if cat['avg_rating'] > 0:
                print(f"  Average rating: {cat['avg_rating']:.1f}/5")
        return
    
    table = Table(title="🎵 Sleep Sound Categories", show_header=True, header_style="bold blue")
    table.add_column("Category", style="cyan", width=15)
    table.add_column("Description", style="white", width=35)
    table.add_column("Sounds", justify="right", style="green", width=8)
    table.add_column("Rating", justify="right", style="yellow", width=8)
    
    for cat in categories:
        rating_display = f"{cat['avg_rating']:.1f}⭐" if cat['avg_rating'] > 0 else "New"
        table.add_row(
            cat['name'].title(),
            cat['description'],
            str(cat['count']),
            rating_display
        )
    
    console.print(table)

def display_sounds_list(sounds: List[Dict], title: str = "Available Sounds"):
    """Display a list of sounds"""
    if not sounds:
        if console:
            console.print("[yellow]No sounds found.[/yellow]")
        else:
            print("No sounds found.")
        return
    
    if not RICH_AVAILABLE:
        print(f"\n{title}:")
        print("=" * len(title))
        for sound in sounds:
            print(f"• {sound['name']} ({sound['category']})")
            print(f"  {sound['description']}")
            if sound.get('mental_health_tags'):
                print(f"  Tags: {', '.join(sound['mental_health_tags'])}")
            print()
        return
    
    table = Table(title=f"🎵 {title}", show_header=True, header_style="bold blue")
    table.add_column("Sound", style="cyan", width=20)
    table.add_column("Category", style="magenta", width=12)
    table.add_column("Description", style="white", width=30)
    table.add_column("Duration", justify="right", style="green", width=8)
    table.add_column("Tags", style="yellow", width=20)
    
    for sound in sounds:
        duration_str = f"{sound['duration_seconds']//60}m"
        tags_str = ", ".join(sound.get('mental_health_tags', [])[:3])
        if len(sound.get('mental_health_tags', [])) > 3:
            tags_str += "..."
        
        table.add_row(
            sound['name'],
            sound['category'].title(),
            sound['description'][:30] + "..." if len(sound['description']) > 30 else sound['description'],
            duration_str,
            tags_str
        )
    
    console.print(table)

def display_sleep_statistics(stats: Dict):
    """Display sleep statistics"""
    if not stats or stats['total_sessions'] == 0:
        if console:
            console.print("[yellow]No sleep sessions recorded yet.[/yellow]")
        else:
            print("No sleep sessions recorded yet.")
        return
    
    if not RICH_AVAILABLE:
        print("\nSleep Statistics (Last 30 Days):")
        print("=" * 35)
        print(f"Total Sessions: {stats['total_sessions']}")
        print(f"Average Duration: {stats['avg_duration_minutes']:.1f} minutes")
        print(f"Total Sleep Time: {stats['total_hours']:.1f} hours")
        print(f"Average Quality: {stats['avg_quality_rating']:.1f}/5")
        if stats['most_used_sounds']:
            print("\nMost Used Sounds:")
            for sound, count in stats['most_used_sounds'].items():
                print(f"  • {sound}: {count} times")
        return
    
    # Main statistics panel
    stats_text = f"[bold green]Total Sessions:[/bold green] {stats['total_sessions']}\n"
    stats_text += f"[bold blue]Average Duration:[/bold blue] {stats['avg_duration_minutes']:.1f} minutes\n"
    stats_text += f"[bold yellow]Total Sleep Time:[/bold yellow] {stats['total_hours']:.1f} hours\n"
    stats_text += f"[bold magenta]Average Quality:[/bold magenta] {stats['avg_quality_rating']:.1f}/5 ⭐"
    
    console.print(Panel(
        stats_text,
        title="📊 Sleep Statistics (Last 30 Days)",
        border_style="blue"
    ))
    
    # Most used sounds
    if stats['most_used_sounds']:
        sound_table = Table(title="🎵 Most Used Sounds", show_header=True, header_style="bold green")
        sound_table.add_column("Sound", style="cyan")
        sound_table.add_column("Usage Count", justify="right", style="green")
        
        for sound, count in list(stats['most_used_sounds'].items())[:5]:
            sound_table.add_row(sound, str(count))
        
        console.print(sound_table)

def display_sound_mixes(mixes: List[Dict]):
    """Display saved sound mixes"""
    if not mixes:
        if console:
            console.print("[yellow]No saved sound mixes. Create one with 'om sleep create-mix'[/yellow]")
        else:
            print("No saved sound mixes. Create one with 'om sleep create-mix'")
        return
    
    if not RICH_AVAILABLE:
        print("\nSaved Sound Mixes:")
        print("=" * 20)
        for mix in mixes:
            print(f"• {mix['name']}")
            print(f"  Sounds: {', '.join(mix['sounds'])}")
            print(f"  Used {mix['usage_count']} times")
            if mix['is_favorite']:
                print("  ⭐ Favorite")
            print()
        return
    
    table = Table(title="🎛️ Saved Sound Mixes", show_header=True, header_style="bold purple")
    table.add_column("Mix Name", style="cyan", width=20)
    table.add_column("Sounds", style="white", width=30)
    table.add_column("Usage", justify="right", style="green", width=8)
    table.add_column("Favorite", justify="center", style="yellow", width=8)
    
    for mix in mixes:
        sounds_str = ", ".join(mix['sounds'][:3])
        if len(mix['sounds']) > 3:
            sounds_str += f" +{len(mix['sounds'])-3} more"
        
        favorite_str = "⭐" if mix['is_favorite'] else ""
        
        table.add_row(
            mix['name'],
            sounds_str,
            str(mix['usage_count']),
            favorite_str
        )
    
    console.print(table)

def interactive_sound_mixer():
    """Interactive sound mixer for creating custom mixes"""
    if not console:
        print("Interactive mixer requires rich library. Use basic commands instead.")
        return
    
    manager = SleepSoundsManager()
    sounds = manager.get_sounds_by_category()
    
    if not sounds:
        console.print("[red]No sounds available for mixing.[/red]")
        return
    
    console.print(Panel(
        "[bold blue]Interactive Sound Mixer[/bold blue]\n\n"
        "Create your perfect sleep sound mix by selecting sounds and adjusting volumes.\n"
        "You can combine multiple sounds to create a personalized sleep environment.",
        title="🎛️ Sound Mixer",
        border_style="blue"
    ))
    
    # Display available sounds
    display_sounds_list(sounds, "Available Sounds for Mixing")
    
    selected_sounds = []
    volumes = {}
    
    while True:
        if selected_sounds:
            console.print(f"\n[green]Current mix: {', '.join(selected_sounds)}[/green]")
        
        action = Prompt.ask(
            "\nChoose action",
            choices=["add", "remove", "volume", "save", "play", "quit"],
            default="add"
        )
        
        if action == "quit":
            break
        elif action == "add":
            sound_name = Prompt.ask("Enter sound name to add")
            if any(s['name'].lower() == sound_name.lower() for s in sounds):
                # Find the exact name
                exact_name = next(s['name'] for s in sounds if s['name'].lower() == sound_name.lower())
                if exact_name not in selected_sounds:
                    selected_sounds.append(exact_name)
                    volumes[exact_name] = 50  # Default volume
                    console.print(f"[green]Added '{exact_name}' to mix[/green]")
                else:
                    console.print(f"[yellow]'{exact_name}' is already in the mix[/yellow]")
            else:
                console.print(f"[red]Sound '{sound_name}' not found[/red]")
        
        elif action == "remove":
            if not selected_sounds:
                console.print("[yellow]No sounds in mix to remove[/yellow]")
                continue
            
            sound_name = Prompt.ask("Enter sound name to remove")
            if sound_name in selected_sounds:
                selected_sounds.remove(sound_name)
                del volumes[sound_name]
                console.print(f"[green]Removed '{sound_name}' from mix[/green]")
            else:
                console.print(f"[red]'{sound_name}' not in current mix[/red]")
        
        elif action == "volume":
            if not selected_sounds:
                console.print("[yellow]No sounds in mix to adjust[/yellow]")
                continue
            
            sound_name = Prompt.ask("Enter sound name to adjust volume")
            if sound_name in selected_sounds:
                volume = IntPrompt.ask(f"Enter volume for '{sound_name}' (0-100)", default=volumes[sound_name])
                volumes[sound_name] = max(0, min(100, volume))
                console.print(f"[green]Set '{sound_name}' volume to {volumes[sound_name]}%[/green]")
            else:
                console.print(f"[red]'{sound_name}' not in current mix[/red]")
        
        elif action == "save":
            if not selected_sounds:
                console.print("[yellow]No sounds in mix to save[/yellow]")
                continue
            
            mix_name = Prompt.ask("Enter name for this mix")
            description = Prompt.ask("Enter description (optional)", default="")
            
            if manager.create_sound_mix(mix_name, selected_sounds, volumes, description):
                console.print(f"[green]Saved mix '{mix_name}' successfully![/green]")
            else:
                console.print(f"[red]Mix name '{mix_name}' already exists[/red]")
        
        elif action == "play":
            if not selected_sounds:
                console.print("[yellow]No sounds in mix to play[/yellow]")
                continue
            
            timer_minutes = IntPrompt.ask("Enter sleep timer in minutes (0 for no timer)", default=30)
            
            console.print(f"[green]Starting sleep session with: {', '.join(selected_sounds)}[/green]")
            console.print(f"[blue]Timer set for {timer_minutes} minutes[/blue]")
            
            session_id = manager.start_sleep_session(selected_sounds, volumes, timer_minutes)
            
            console.print(f"[green]Sleep session started! Session ID: {session_id}[/green]")
            console.print("[dim]Use 'om sleep stop' to end the session manually[/dim]")
            break

def main():
    """Main function for the sleep sounds module"""
    manager = SleepSoundsManager()
    
    if len(sys.argv) < 2:
        # Default: show categories
        categories = manager.get_categories()
        display_sound_categories(categories)
        return
    
    command = sys.argv[1].lower()
    
    if command == "categories":
        categories = manager.get_categories()
        display_sound_categories(categories)
        
    elif command == "sounds":
        category = sys.argv[2] if len(sys.argv) > 2 else None
        sounds = manager.get_sounds_by_category(category)
        title = f"{category.title()} Sounds" if category else "All Sounds"
        display_sounds_list(sounds, title)
        
    elif command == "search":
        if len(sys.argv) < 3:
            if console:
                console.print("[red]Usage: om sleep search <mental_health_tag>[/red]")
            else:
                print("Usage: om sleep search <mental_health_tag>")
            return
        
        tag = sys.argv[2]
        sounds = manager.search_sounds_by_mental_health_tag(tag)
        display_sounds_list(sounds, f"Sounds for '{tag.title()}'")
        
    elif command == "play":
        if len(sys.argv) < 3:
            if console:
                console.print("[red]Usage: om sleep play <sound_name> [timer_minutes][/red]")
            else:
                print("Usage: om sleep play <sound_name> [timer_minutes]")
            return
        
        sound_name = sys.argv[2]
        timer_minutes = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        
        # Check if sound exists
        sounds = manager.get_sounds_by_category()
        if not any(s['name'].lower() == sound_name.lower() for s in sounds):
            if console:
                console.print(f"[red]Sound '{sound_name}' not found[/red]")
            else:
                print(f"Sound '{sound_name}' not found")
            return
        
        # Find exact name
        exact_name = next(s['name'] for s in sounds if s['name'].lower() == sound_name.lower())
        
        session_id = manager.start_sleep_session([exact_name], {exact_name: 50}, timer_minutes)
        
        if console:
            console.print(f"[green]Playing '{exact_name}' with {timer_minutes} minute timer[/green]")
            console.print(f"[dim]Session ID: {session_id}[/dim]")
        else:
            print(f"Playing '{exact_name}' with {timer_minutes} minute timer")
            print(f"Session ID: {session_id}")
    
    elif command == "stop":
        if manager.stop_sleep_session():
            if console:
                rating = IntPrompt.ask("Rate your sleep session (1-5)", default=3)
                notes = Prompt.ask("Add notes (optional)", default="")
                
                # Update the session with rating and notes
                with sqlite3.connect(manager.db_path) as conn:
                    conn.execute("""
                        UPDATE sleep_sessions 
                        SET quality_rating = ?, notes = ?
                        WHERE end_time = (SELECT MAX(end_time) FROM sleep_sessions)
                    """, (rating, notes))
                    conn.commit()
                
                console.print("[green]Sleep session stopped and saved![/green]")
            else:
                print("Sleep session stopped!")
        else:
            if console:
                console.print("[yellow]No active sleep session to stop[/yellow]")
            else:
                print("No active sleep session to stop")
    
    elif command == "mixer":
        interactive_sound_mixer()
        
    elif command == "mixes":
        mixes = manager.get_sound_mixes()
        display_sound_mixes(mixes)
        
    elif command == "stats":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        stats = manager.get_sleep_statistics(days)
        display_sleep_statistics(stats)
        
    elif command == "preferences":
        prefs = manager.get_user_preferences()
        
        if not RICH_AVAILABLE:
            print("\nCurrent Preferences:")
            print("=" * 20)
            for key, value in prefs.items():
                print(f"{key}: {value}")
            return
        
        table = Table(title="⚙️ Sleep Preferences", show_header=True, header_style="bold blue")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in prefs.items():
            display_key = key.replace('_', ' ').title()
            display_value = str(value)
            if isinstance(value, bool):
                display_value = "✅ Yes" if value else "❌ No"
            elif isinstance(value, list):
                display_value = ", ".join(value) if value else "None"
            
            table.add_row(display_key, display_value)
        
        console.print(table)
    
    else:
        if console:
            console.print(f"[red]Unknown command: {command}[/red]")
            console.print("[yellow]Available commands: categories, sounds, search, play, stop, mixer, mixes, stats, preferences[/yellow]")
        else:
            print(f"Unknown command: {command}")
            print("Available commands: categories, sounds, search, play, stop, mixer, mixes, stats, preferences")

if __name__ == "__main__":
    main()
