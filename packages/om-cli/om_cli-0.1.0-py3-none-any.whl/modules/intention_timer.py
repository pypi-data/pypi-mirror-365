"""
Intention Timer Module for om
Inspired by https://github.com/janitastic/Intention-Timer

A focused timer for intentional activities like study, meditation, and exercise.
Helps users set intentions, track time, and log their progress.
"""

import json
import os
import sqlite3
import time
import uuid
from datetime import datetime, timedelta
import threading
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

# Database connection
def get_db_connection():
    """Get database connection"""
    db_path = os.path.expanduser("~/.om/om.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return sqlite3.connect(db_path)

def initialize_intention_timer_db():
    """Initialize the intention timer database schema"""
    conn = get_db_connection()
    
    # Create intention_activities table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS intention_activities (
            id TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            planned_minutes INTEGER NOT NULL,
            planned_seconds INTEGER DEFAULT 0,
            actual_duration INTEGER, -- actual seconds completed
            status TEXT DEFAULT 'planned', -- planned, in_progress, completed, abandoned
            started_at TEXT,
            completed_at TEXT,
            notes TEXT,
            effectiveness_rating INTEGER, -- 1-10 scale
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create intention_sessions table for detailed tracking
    conn.execute("""
        CREATE TABLE IF NOT EXISTS intention_sessions (
            id TEXT PRIMARY KEY,
            activity_id TEXT NOT NULL,
            session_start TEXT NOT NULL,
            session_end TEXT,
            duration_seconds INTEGER,
            interruptions INTEGER DEFAULT 0,
            focus_rating INTEGER, -- 1-10 scale
            notes TEXT,
            FOREIGN KEY (activity_id) REFERENCES intention_activities (id)
        )
    """)
    
    # Create indexes
    conn.execute("CREATE INDEX IF NOT EXISTS idx_intention_activities_category ON intention_activities(category)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_intention_activities_status ON intention_activities(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_intention_activities_created_at ON intention_activities(created_at)")
    
    conn.commit()
    conn.close()

class IntentionActivity:
    """Represents an intention-based activity"""
    
    def __init__(self, category, description, minutes, seconds=0):
        self.id = str(uuid.uuid4())
        self.category = category.lower()
        self.description = description
        self.planned_minutes = int(minutes)
        self.planned_seconds = int(seconds)
        self.total_planned_seconds = (self.planned_minutes * 60) + self.planned_seconds
        self.remaining_seconds = self.total_planned_seconds
        self.status = 'planned'
        self.started_at = None
        self.completed_at = None
        self.timer_thread = None
        self.is_running = False
        self.is_paused = False
        
    def save_to_db(self):
        """Save activity to database"""
        conn = get_db_connection()
        
        actual_duration = None
        if self.status == 'completed':
            actual_duration = self.total_planned_seconds - self.remaining_seconds
        
        conn.execute("""
            INSERT OR REPLACE INTO intention_activities 
            (id, category, description, planned_minutes, planned_seconds, 
             actual_duration, status, started_at, completed_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (self.id, self.category, self.description, self.planned_minutes, 
              self.planned_seconds, actual_duration, self.status, 
              self.started_at, self.completed_at, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def start_timer(self):
        """Start the intention timer"""
        if self.is_running:
            return False
        
        self.is_running = True
        self.is_paused = False
        self.status = 'in_progress'
        self.started_at = datetime.now().isoformat()
        
        # Start timer in separate thread
        self.timer_thread = threading.Thread(target=self._run_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()
        
        return True
    
    def pause_timer(self):
        """Pause the timer"""
        self.is_paused = True
    
    def resume_timer(self):
        """Resume the timer"""
        self.is_paused = False
    
    def stop_timer(self):
        """Stop the timer"""
        self.is_running = False
        if self.remaining_seconds <= 0:
            self.status = 'completed'
            self.completed_at = datetime.now().isoformat()
        else:
            self.status = 'abandoned'
        
        self.save_to_db()
    
    def _run_timer(self):
        """Internal timer loop"""
        while self.is_running and self.remaining_seconds > 0:
            if not self.is_paused:
                time.sleep(1)
                self.remaining_seconds -= 1
            else:
                time.sleep(0.1)  # Check pause status frequently
        
        if self.remaining_seconds <= 0:
            self.status = 'completed'
            self.completed_at = datetime.now().isoformat()
            self.is_running = False
    
    def get_formatted_time(self, seconds=None):
        """Get formatted time string"""
        if seconds is None:
            seconds = self.remaining_seconds
        
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
    
    def get_progress_percentage(self):
        """Get completion percentage"""
        completed = self.total_planned_seconds - self.remaining_seconds
        return (completed / self.total_planned_seconds) * 100

def create_new_intention():
    """Create a new intention activity"""
    console.print("\n🎯 [bold blue]Create New Intention[/bold blue]")
    console.print("Set your intention and focus on what matters most.\n")
    
    # Category selection
    categories = {
        '1': ('study', '📚', 'Study & Learning'),
        '2': ('meditate', '🧘', 'Meditation & Mindfulness'), 
        '3': ('exercise', '💪', 'Exercise & Movement'),
        '4': ('work', '💼', 'Focused Work'),
        '5': ('creative', '🎨', 'Creative Practice'),
        '6': ('reading', '📖', 'Reading & Research')
    }
    
    console.print("[bold]Select a category:[/bold]")
    for key, (cat, emoji, name) in categories.items():
        console.print(f"  {key}. {emoji} {name}")
    
    while True:
        choice = Prompt.ask("\nEnter your choice (1-6)")
        if choice in categories:
            category, emoji, name = categories[choice]
            break
        console.print("[red]Please enter a valid choice (1-6)[/red]")
    
    # Description
    console.print(f"\n{emoji} [bold]{name}[/bold] selected!")
    description = Prompt.ask("\n[bold]What would you like to accomplish during this time?[/bold]")
    
    # Time input
    console.print("\n[bold]Set your intention time:[/bold]")
    while True:
        try:
            minutes = int(Prompt.ask("Minutes", default="25"))
            seconds = int(Prompt.ask("Seconds", default="0"))
            if minutes >= 0 and seconds >= 0 and (minutes > 0 or seconds > 0):
                break
            console.print("[red]Please enter valid time values (at least 1 second total)[/red]")
        except ValueError:
            console.print("[red]Please enter valid numbers[/red]")
    
    # Create activity
    activity = IntentionActivity(category, description, minutes, seconds)
    
    # Confirmation
    total_time = activity.get_formatted_time(activity.total_planned_seconds)
    
    panel_content = f"""[bold]{emoji} {name}[/bold]
    
[bold]Intention:[/bold] {description}
[bold]Duration:[/bold] {total_time}

Ready to begin your focused session?"""
    
    console.print(Panel(panel_content, title="🎯 Intention Set", border_style="blue"))
    
    if Confirm.ask("\nStart your intention timer?", default=True):
        run_intention_timer(activity)
    else:
        console.print("💭 Intention saved for later. Use 'om intention start' to begin.")
        activity.save_to_db()

def run_intention_timer(activity):
    """Run the intention timer with live display"""
    console.clear()
    
    # Get category emoji
    category_emojis = {
        'study': '📚', 'meditate': '🧘', 'exercise': '💪',
        'work': '💼', 'creative': '🎨', 'reading': '📖'
    }
    emoji = category_emojis.get(activity.category, '🎯')
    
    # Start the timer
    activity.start_timer()
    
    console.print(f"\n{emoji} [bold blue]Intention Timer Started[/bold blue]\n")
    console.print(f"[bold]Focus:[/bold] {activity.description}")
    console.print(f"[bold]Duration:[/bold] {activity.get_formatted_time(activity.total_planned_seconds)}\n")
    
    console.print("[dim]Press Ctrl+C to pause/stop the timer[/dim]\n")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Time Remaining: {task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
            transient=False
        ) as progress:
            
            task = progress.add_task(
                activity.get_formatted_time(),
                total=activity.total_planned_seconds
            )
            
            while activity.is_running and activity.remaining_seconds > 0:
                if not activity.is_paused:
                    progress.update(
                        task,
                        description=activity.get_formatted_time(),
                        completed=activity.total_planned_seconds - activity.remaining_seconds
                    )
                
                time.sleep(0.5)
            
            # Timer completed
            if activity.remaining_seconds <= 0:
                progress.update(task, completed=activity.total_planned_seconds)
                console.print(f"\n🎉 [bold green]INTENTION COMPLETED![/bold green] 🎉")
                console.print(f"✨ You focused on: {activity.description}")
                console.print(f"⏱️  Duration: {activity.get_formatted_time(activity.total_planned_seconds)}")
                
                # Log completion
                log_completed_intention(activity)
            
    except KeyboardInterrupt:
        handle_timer_interrupt(activity)

def handle_timer_interrupt(activity):
    """Handle timer interruption (pause/stop)"""
    activity.pause_timer()
    
    console.print("\n⏸️  [yellow]Timer Paused[/yellow]")
    console.print(f"Time remaining: {activity.get_formatted_time()}")
    
    choices = [
        "Resume timer",
        "Stop and log progress", 
        "Abandon session"
    ]
    
    console.print("\n[bold]What would you like to do?[/bold]")
    for i, choice in enumerate(choices, 1):
        console.print(f"  {i}. {choice}")
    
    while True:
        try:
            choice = int(Prompt.ask("\nEnter your choice (1-3)"))
            if 1 <= choice <= 3:
                break
        except ValueError:
            pass
        console.print("[red]Please enter 1, 2, or 3[/red]")
    
    if choice == 1:  # Resume
        console.print("▶️  Resuming timer...")
        activity.resume_timer()
        run_intention_timer(activity)  # Continue with display
    elif choice == 2:  # Stop and log
        activity.stop_timer()
        console.print(f"\n📝 [bold]Session Stopped[/bold]")
        console.print(f"Time completed: {activity.get_formatted_time(activity.total_planned_seconds - activity.remaining_seconds)}")
        log_completed_intention(activity)
    else:  # Abandon
        activity.stop_timer()
        console.print("❌ Session abandoned. No progress logged.")

def log_completed_intention(activity):
    """Log completed intention with optional rating and notes"""
    console.print("\n📊 [bold]Log Your Session[/bold]")
    
    # Effectiveness rating
    while True:
        try:
            rating = Prompt.ask(
                "How effective was this session? (1-10, or press Enter to skip)",
                default=""
            )
            if rating == "":
                rating = None
                break
            rating = int(rating)
            if 1 <= rating <= 10:
                break
            console.print("[red]Please enter a number between 1 and 10[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
    
    # Optional notes
    notes = Prompt.ask(
        "Any notes about this session? (optional)",
        default=""
    ) or None
    
    # Save to database with rating and notes
    conn = get_db_connection()
    conn.execute("""
        UPDATE intention_activities 
        SET effectiveness_rating = ?, notes = ?
        WHERE id = ?
    """, (rating, notes, activity.id))
    conn.commit()
    conn.close()
    
    console.print("✅ [green]Session logged successfully![/green]")
    
    # Show summary
    show_session_summary(activity, rating, notes)

def show_session_summary(activity, rating=None, notes=None):
    """Show session summary"""
    category_emojis = {
        'study': '📚', 'meditate': '🧘', 'exercise': '💪',
        'work': '💼', 'creative': '🎨', 'reading': '📖'
    }
    emoji = category_emojis.get(activity.category, '🎯')
    
    completed_time = activity.total_planned_seconds - activity.remaining_seconds
    completion_percentage = (completed_time / activity.total_planned_seconds) * 100
    
    summary = f"""[bold]{emoji} Session Summary[/bold]

[bold]Intention:[/bold] {activity.description}
[bold]Category:[/bold] {activity.category.title()}
[bold]Planned Time:[/bold] {activity.get_formatted_time(activity.total_planned_seconds)}
[bold]Completed Time:[/bold] {activity.get_formatted_time(completed_time)}
[bold]Completion:[/bold] {completion_percentage:.1f}%"""
    
    if rating:
        summary += f"\n[bold]Effectiveness:[/bold] {rating}/10"
    
    if notes:
        summary += f"\n[bold]Notes:[/bold] {notes}"
    
    console.print(Panel(summary, title="📊 Session Complete", border_style="green"))

def show_past_activities(limit=10):
    """Show past intention activities"""
    conn = get_db_connection()
    
    cursor = conn.execute("""
        SELECT category, description, planned_minutes, planned_seconds,
               actual_duration, status, effectiveness_rating, notes,
               created_at, completed_at
        FROM intention_activities
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    
    activities = cursor.fetchall()
    conn.close()
    
    if not activities:
        console.print("📝 No past activities found. Create your first intention!")
        return
    
    console.print(f"\n📚 [bold]Past Intentions[/bold] (Last {len(activities)})")
    console.print("=" * 60)
    
    category_emojis = {
        'study': '📚', 'meditate': '🧘', 'exercise': '💪',
        'work': '💼', 'creative': '🎨', 'reading': '📖'
    }
    
    for i, activity in enumerate(activities, 1):
        category, description, planned_min, planned_sec, actual_duration, status, rating, notes, created_at, completed_at = activity
        
        emoji = category_emojis.get(category, '🎯')
        planned_total = (planned_min * 60) + planned_sec
        
        # Status indicator
        status_indicators = {
            'completed': '✅',
            'abandoned': '❌', 
            'in_progress': '⏳',
            'planned': '📋'
        }
        status_emoji = status_indicators.get(status, '❓')
        
        console.print(f"\n{i}. {status_emoji} {emoji} [bold]{description}[/bold]")
        console.print(f"   📂 {category.title()}")
        
        # Time information
        planned_time = f"{planned_min:02d}:{planned_sec:02d}"
        if actual_duration is not None:
            actual_min = actual_duration // 60
            actual_sec = actual_duration % 60
            actual_time = f"{actual_min:02d}:{actual_sec:02d}"
            completion = (actual_duration / planned_total) * 100
            console.print(f"   ⏱️  Planned: {planned_time} | Completed: {actual_time} ({completion:.1f}%)")
        else:
            console.print(f"   ⏱️  Planned: {planned_time}")
        
        # Rating and notes
        if rating:
            console.print(f"   ⭐ Effectiveness: {rating}/10")
        
        if notes:
            console.print(f"   📝 {notes}")
        
        # Date
        created_date = datetime.fromisoformat(created_at).strftime("%Y-%m-%d %H:%M")
        console.print(f"   📅 {created_date}")

def show_intention_stats():
    """Show intention timer statistics"""
    conn = get_db_connection()
    
    # Overall stats
    cursor = conn.execute("""
        SELECT 
            COUNT(*) as total_activities,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
            COUNT(CASE WHEN status = 'abandoned' THEN 1 END) as abandoned,
            AVG(CASE WHEN effectiveness_rating IS NOT NULL THEN effectiveness_rating END) as avg_rating,
            SUM(CASE WHEN actual_duration IS NOT NULL THEN actual_duration ELSE 0 END) as total_time
        FROM intention_activities
    """)
    
    stats = cursor.fetchone()
    total, completed, abandoned, avg_rating, total_time = stats
    
    # Category breakdown
    cursor = conn.execute("""
        SELECT category, COUNT(*) as count,
               COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count
        FROM intention_activities
        GROUP BY category
        ORDER BY count DESC
    """)
    
    category_stats = cursor.fetchall()
    conn.close()
    
    if total == 0:
        console.print("📊 No intention activities yet. Start your first session!")
        return
    
    console.print("\n📊 [bold blue]Intention Timer Statistics[/bold blue]")
    console.print("=" * 50)
    
    # Overall stats
    completion_rate = (completed / total * 100) if total > 0 else 0
    total_hours = total_time // 3600
    total_minutes = (total_time % 3600) // 60
    
    console.print(f"\n📈 [bold]Overall Performance[/bold]")
    console.print(f"   Total Sessions: {total}")
    console.print(f"   Completed: {completed} ({completion_rate:.1f}%)")
    console.print(f"   Abandoned: {abandoned}")
    console.print(f"   Total Focus Time: {total_hours}h {total_minutes}m")
    
    if avg_rating:
        console.print(f"   Average Effectiveness: {avg_rating:.1f}/10")
    
    # Category breakdown
    if category_stats:
        console.print(f"\n📂 [bold]By Category[/bold]")
        
        category_emojis = {
            'study': '📚', 'meditate': '🧘', 'exercise': '💪',
            'work': '💼', 'creative': '🎨', 'reading': '📖'
        }
        
        for category, count, completed_count in category_stats:
            emoji = category_emojis.get(category, '🎯')
            completion_rate = (completed_count / count * 100) if count > 0 else 0
            console.print(f"   {emoji} {category.title()}: {count} sessions ({completed_count} completed, {completion_rate:.1f}%)")

def run(args=None):
    """Main entry point for the intention timer module"""
    
    # Initialize database
    initialize_intention_timer_db()
    
    if not args:
        console.print("🎯 [bold blue]Intention Timer[/bold blue]")
        console.print("Set focused intentions and track your progress")
        console.print()
        console.print("Available commands:")
        console.print("  om intention new          - Create a new intention")
        console.print("  om intention start         - Start a new intention (alias for new)")
        console.print("  om intention history       - View past activities")
        console.print("  om intention stats         - Show statistics")
        console.print()
        console.print("💡 [dim]Tip: Use focused time blocks to accomplish meaningful goals[/dim]")
        return
    
    command = args[0].lower()
    
    if command in ['new', 'start', 'create']:
        create_new_intention()
        
    elif command in ['history', 'past', 'log']:
        limit = 20
        if len(args) > 1:
            try:
                limit = int(args[1])
            except ValueError:
                pass
        show_past_activities(limit)
        
    elif command in ['stats', 'statistics', 'summary']:
        show_intention_stats()
        
    else:
        console.print(f"❌ Unknown command: {command}")
        console.print("Use 'om intention' to see available commands")

def main():
    """Alternative entry point for direct execution"""
    import sys
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    run(args)

if __name__ == "__main__":
    main()
