#!/usr/bin/env python3
"""
Visual Wellness Dashboard for om
Real-time mental health metrics and progress visualization
Adapted from logbuch visual dashboard for wellness focus
"""

import time
import datetime
import threading
import json
import os
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

try:
    from rich.live import Live
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TaskProgressColumn
    from rich.table import Table
    from rich.console import Console, Group
    from rich.align import Align
    from rich.text import Text
    from rich.columns import Columns
    from rich import box
    from rich.tree import Tree
    from rich.gauge import Gauge
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

@dataclass
class WellnessDashboardMetrics:
    mood_entries: int
    avg_mood: float
    mood_trend: str
    breathing_sessions: int
    meditation_minutes: int
    gratitude_entries: int
    current_streak: int
    wellness_level: int
    wellness_points: int
    achievements_unlocked: int
    stress_level: float
    energy_level: float
    recent_activities: List[str]
    crisis_alerts: int
    self_care_score: float

class WellnessDashboard:
    def __init__(self):
        self.data_dir = os.path.expanduser("~/.om")
        os.makedirs(self.data_dir, exist_ok=True)
        self.console = Console() if RICH_AVAILABLE else None
        self.running = False
        self.update_thread = None
        
    def _load_mood_data(self) -> List[dict]:
        """Load mood data from storage"""
        mood_file = os.path.join(self.data_dir, "mood_data.json")
        if os.path.exists(mood_file):
            try:
                with open(mood_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def _load_wellness_stats(self) -> dict:
        """Load wellness stats from gamification system"""
        stats_file = os.path.join(self.data_dir, "wellness_stats.json")
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _load_achievements(self) -> List[dict]:
        """Load achievements data"""
        achievements_file = os.path.join(self.data_dir, "achievements.json")
        if os.path.exists(achievements_file):
            try:
                with open(achievements_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def _calculate_metrics(self) -> WellnessDashboardMetrics:
        """Calculate current wellness metrics"""
        mood_data = self._load_mood_data()
        wellness_stats = self._load_wellness_stats()
        achievements = self._load_achievements()
        
        # Calculate mood metrics
        recent_moods = [entry.get('mood', 5) for entry in mood_data[-30:]]  # Last 30 entries
        avg_mood = statistics.mean(recent_moods) if recent_moods else 5.0
        
        # Calculate mood trend
        if len(recent_moods) >= 10:
            recent_avg = statistics.mean(recent_moods[-7:])
            earlier_avg = statistics.mean(recent_moods[-14:-7]) if len(recent_moods) >= 14 else recent_avg
            if recent_avg > earlier_avg + 0.3:
                mood_trend = "📈 Improving"
            elif recent_avg < earlier_avg - 0.3:
                mood_trend = "📉 Declining"
            else:
                mood_trend = "➡️ Stable"
        else:
            mood_trend = "➡️ Stable"
        
        # Calculate stress and energy levels
        recent_stress = [entry.get('stress', 5) for entry in mood_data[-7:]]
        recent_energy = [entry.get('energy', 5) for entry in mood_data[-7:]]
        avg_stress = statistics.mean(recent_stress) if recent_stress else 5.0
        avg_energy = statistics.mean(recent_energy) if recent_energy else 5.0
        
        # Get recent activities
        recent_activities = []
        for entry in mood_data[-5:]:
            if entry.get('notes'):
                activity = entry['notes'][:50] + "..." if len(entry['notes']) > 50 else entry['notes']
                recent_activities.append(activity)
        
        # Calculate self-care score (based on various factors)
        self_care_score = min(10.0, (avg_mood + avg_energy + (10 - avg_stress)) / 3)
        
        # Count crisis alerts (high stress + low mood)
        crisis_alerts = sum(1 for entry in mood_data[-7:] 
                          if entry.get('mood', 5) <= 3 and entry.get('stress', 0) >= 8)
        
        # Count unlocked achievements
        unlocked_achievements = sum(1 for achievement in achievements if achievement.get('unlocked', False))
        
        return WellnessDashboardMetrics(
            mood_entries=len(mood_data),
            avg_mood=avg_mood,
            mood_trend=mood_trend,
            breathing_sessions=wellness_stats.get('breathing_sessions', 0),
            meditation_minutes=wellness_stats.get('meditation_minutes', 0),
            gratitude_entries=wellness_stats.get('gratitude_entries', 0),
            current_streak=wellness_stats.get('current_streak', 0),
            wellness_level=wellness_stats.get('level', 1),
            wellness_points=wellness_stats.get('wellness_points', 0),
            achievements_unlocked=unlocked_achievements,
            stress_level=avg_stress,
            energy_level=avg_energy,
            recent_activities=recent_activities,
            crisis_alerts=crisis_alerts,
            self_care_score=self_care_score
        )
    
    def _create_mood_panel(self, metrics: WellnessDashboardMetrics) -> Panel:
        """Create mood tracking panel"""
        mood_color = "green" if metrics.avg_mood >= 7 else "yellow" if metrics.avg_mood >= 4 else "red"
        
        mood_content = Group(
            Text(f"Average Mood: {metrics.avg_mood:.1f}/10", style=f"bold {mood_color}"),
            Text(f"Trend: {metrics.mood_trend}"),
            Text(f"Total Entries: {metrics.mood_entries}"),
            Text(""),
            Text(f"Stress Level: {metrics.stress_level:.1f}/10", 
                 style="red" if metrics.stress_level >= 7 else "yellow" if metrics.stress_level >= 4 else "green"),
            Text(f"Energy Level: {metrics.energy_level:.1f}/10",
                 style="green" if metrics.energy_level >= 7 else "yellow" if metrics.energy_level >= 4 else "red")
        )
        
        return Panel(mood_content, title="🧠 Mood & Wellbeing", border_style="blue")
    
    def _create_activities_panel(self, metrics: WellnessDashboardMetrics) -> Panel:
        """Create activities panel"""
        activities_content = Group(
            Text(f"🫁 Breathing Sessions: {metrics.breathing_sessions}"),
            Text(f"🧘 Meditation Minutes: {metrics.meditation_minutes}"),
            Text(f"🙏 Gratitude Entries: {metrics.gratitude_entries}"),
            Text(f"🔥 Current Streak: {metrics.current_streak} days"),
            Text(""),
            Text("Recent Activities:", style="bold"),
            *[Text(f"• {activity}", style="dim") for activity in metrics.recent_activities[-3:]]
        )
        
        return Panel(activities_content, title="📊 Activities", border_style="green")
    
    def _create_progress_panel(self, metrics: WellnessDashboardMetrics) -> Panel:
        """Create progress panel"""
        # Create progress bars
        progress = Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            expand=True
        )
        
        # Self-care score progress
        self_care_task = progress.add_task("Self-Care Score", total=10, completed=metrics.self_care_score)
        
        # Wellness level progress (assuming level 25 is max for display)
        level_task = progress.add_task("Wellness Level", total=25, completed=metrics.wellness_level)
        
        progress_content = Group(
            Text(f"⭐ Level: {metrics.wellness_level}"),
            Text(f"💎 Points: {metrics.wellness_points}"),
            Text(f"🏆 Achievements: {metrics.achievements_unlocked}"),
            Text(""),
            progress
        )
        
        return Panel(progress_content, title="🎯 Progress", border_style="magenta")
    
    def _create_alerts_panel(self, metrics: WellnessDashboardMetrics) -> Panel:
        """Create alerts and recommendations panel"""
        alerts = []
        
        if metrics.crisis_alerts > 0:
            alerts.append(Text("🚨 Crisis Alert: High stress + low mood detected", style="bold red"))
            alerts.append(Text("   Consider using 'om rescue' for support", style="red"))
        
        if metrics.avg_mood < 4:
            alerts.append(Text("⚠️  Low mood pattern detected", style="bold yellow"))
            alerts.append(Text("   Try 'om coach daily' for personalized guidance", style="yellow"))
        
        if metrics.stress_level >= 7:
            alerts.append(Text("😰 High stress levels", style="bold orange"))
            alerts.append(Text("   Use 'om quick breathe' for immediate relief", style="orange"))
        
        if metrics.current_streak == 0:
            alerts.append(Text("💡 Start a wellness streak today!", style="bold cyan"))
            alerts.append(Text("   Try 'om quick mood' to begin", style="cyan"))
        
        if not alerts:
            alerts = [
                Text("✅ All systems looking good!", style="bold green"),
                Text("   Keep up the great work with your wellness journey!", style="green")
            ]
        
        alerts_content = Group(*alerts)
        
        return Panel(alerts_content, title="🔔 Alerts & Recommendations", border_style="red" if metrics.crisis_alerts > 0 else "yellow")
    
    def _create_quick_actions_panel(self) -> Panel:
        """Create quick actions panel"""
        actions = [
            "🎯 om quick mood     - Quick mood check",
            "🫁 om quick breathe  - 2-minute breathing",
            "🙏 om quick gratitude - Express gratitude",
            "🧠 om coach daily    - Get daily insight",
            "🎮 om gamify status  - Check progress",
            "🆘 om rescue         - Crisis support"
        ]
        
        actions_content = Group(*[Text(action) for action in actions])
        
        return Panel(actions_content, title="⚡ Quick Actions", border_style="cyan")
    
    def _create_layout(self, metrics: WellnessDashboardMetrics) -> Layout:
        """Create the main dashboard layout"""
        layout = Layout()
        
        # Split into header and body
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body")
        )
        
        # Header
        header_text = Text(f"🧘‍♀️ om Wellness Dashboard - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                          style="bold magenta", justify="center")
        layout["header"].update(Panel(header_text, style="bold"))
        
        # Body split into left and right
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Left side split into top and bottom
        layout["left"].split_column(
            Layout(name="mood", size=12),
            Layout(name="activities", size=12)
        )
        
        # Right side split into three sections
        layout["right"].split_column(
            Layout(name="progress", size=10),
            Layout(name="alerts", size=8),
            Layout(name="actions", size=10)
        )
        
        # Populate panels
        layout["mood"].update(self._create_mood_panel(metrics))
        layout["activities"].update(self._create_activities_panel(metrics))
        layout["progress"].update(self._create_progress_panel(metrics))
        layout["alerts"].update(self._create_alerts_panel(metrics))
        layout["actions"].update(self._create_quick_actions_panel())
        
        return layout
    
    def _create_simple_dashboard(self, metrics: WellnessDashboardMetrics) -> str:
        """Create a simple text-based dashboard for when Rich is not available"""
        dashboard = f"""
🧘‍♀️ om Wellness Dashboard - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}

🧠 MOOD & WELLBEING
  Average Mood: {metrics.avg_mood:.1f}/10
  Trend: {metrics.mood_trend}
  Stress Level: {metrics.stress_level:.1f}/10
  Energy Level: {metrics.energy_level:.1f}/10
  Total Entries: {metrics.mood_entries}

📊 ACTIVITIES
  🫁 Breathing Sessions: {metrics.breathing_sessions}
  🧘 Meditation Minutes: {metrics.meditation_minutes}
  🙏 Gratitude Entries: {metrics.gratitude_entries}
  🔥 Current Streak: {metrics.current_streak} days

🎯 PROGRESS
  ⭐ Wellness Level: {metrics.wellness_level}
  💎 Wellness Points: {metrics.wellness_points}
  🏆 Achievements Unlocked: {metrics.achievements_unlocked}
  💚 Self-Care Score: {metrics.self_care_score:.1f}/10

🔔 ALERTS & RECOMMENDATIONS
"""
        
        if metrics.crisis_alerts > 0:
            dashboard += "  🚨 CRISIS ALERT: High stress + low mood detected\n"
            dashboard += "     Consider using 'om rescue' for immediate support\n"
        elif metrics.avg_mood < 4:
            dashboard += "  ⚠️  Low mood pattern detected\n"
            dashboard += "     Try 'om coach daily' for personalized guidance\n"
        elif metrics.stress_level >= 7:
            dashboard += "  😰 High stress levels detected\n"
            dashboard += "     Use 'om quick breathe' for immediate relief\n"
        else:
            dashboard += "  ✅ All systems looking good!\n"
            dashboard += "     Keep up the great work with your wellness journey!\n"
        
        dashboard += f"""
⚡ QUICK ACTIONS
  🎯 om quick mood     - Quick mood check
  🫁 om quick breathe  - 2-minute breathing
  🙏 om quick gratitude - Express gratitude
  🧠 om coach daily    - Get daily insight
  🎮 om gamify status  - Check progress
  🆘 om rescue         - Crisis support

{'='*80}
"""
        return dashboard
    
    def show_static_dashboard(self):
        """Show a static dashboard"""
        metrics = self._calculate_metrics()
        
        if RICH_AVAILABLE and self.console:
            layout = self._create_layout(metrics)
            self.console.print(layout)
        else:
            dashboard = self._create_simple_dashboard(metrics)
            print(dashboard)
    
    def start_live_dashboard(self, refresh_rate: int = 30):
        """Start a live updating dashboard"""
        if not RICH_AVAILABLE:
            print("Live dashboard requires the 'rich' library. Showing static dashboard instead.")
            self.show_static_dashboard()
            return
        
        self.running = True
        
        def update_dashboard():
            with Live(self._create_layout(self._calculate_metrics()), 
                     refresh_per_second=1/refresh_rate, 
                     console=self.console) as live:
                while self.running:
                    try:
                        time.sleep(refresh_rate)
                        if self.running:
                            metrics = self._calculate_metrics()
                            live.update(self._create_layout(metrics))
                    except KeyboardInterrupt:
                        self.running = False
                        break
        
        try:
            print("🧘‍♀️ Starting live wellness dashboard...")
            print("Press Ctrl+C to exit")
            update_dashboard()
        except KeyboardInterrupt:
            self.running = False
            print("\n👋 Dashboard stopped. Take care of your mental health!")
    
    def stop_dashboard(self):
        """Stop the live dashboard"""
        self.running = False
    
    def export_metrics(self, filename: Optional[str] = None) -> str:
        """Export current metrics to JSON file"""
        metrics = self._calculate_metrics()
        
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.data_dir, f"wellness_metrics_{timestamp}.json")
        
        metrics_dict = {
            "timestamp": datetime.datetime.now().isoformat(),
            "mood_entries": metrics.mood_entries,
            "avg_mood": metrics.avg_mood,
            "mood_trend": metrics.mood_trend,
            "breathing_sessions": metrics.breathing_sessions,
            "meditation_minutes": metrics.meditation_minutes,
            "gratitude_entries": metrics.gratitude_entries,
            "current_streak": metrics.current_streak,
            "wellness_level": metrics.wellness_level,
            "wellness_points": metrics.wellness_points,
            "achievements_unlocked": metrics.achievements_unlocked,
            "stress_level": metrics.stress_level,
            "energy_level": metrics.energy_level,
            "crisis_alerts": metrics.crisis_alerts,
            "self_care_score": metrics.self_care_score
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(metrics_dict, f, indent=2)
            return filename
        except Exception as e:
            print(f"Error exporting metrics: {e}")
            return ""

def run(args=None):
    """Main function to run wellness dashboard"""
    dashboard = WellnessDashboard()
    
    if not args or args[0] == "show":
        # Show static dashboard
        dashboard.show_static_dashboard()
    
    elif args[0] == "live":
        # Start live dashboard
        refresh_rate = 30  # Default 30 seconds
        if len(args) > 1:
            try:
                refresh_rate = int(args[1])
            except ValueError:
                print("Invalid refresh rate. Using default 30 seconds.")
        
        dashboard.start_live_dashboard(refresh_rate)
    
    elif args[0] == "export":
        # Export metrics
        filename = dashboard.export_metrics()
        if filename:
            print(f"✅ Metrics exported to: {filename}")
        else:
            print("❌ Failed to export metrics")
    
    elif args[0] == "summary":
        # Show quick summary
        metrics = dashboard._calculate_metrics()
        print(f"\n🧘‍♀️ Wellness Summary")
        print("=" * 30)
        print(f"Mood: {metrics.avg_mood:.1f}/10 {metrics.mood_trend}")
        print(f"Streak: {metrics.current_streak} days 🔥")
        print(f"Level: {metrics.wellness_level} ⭐")
        print(f"Self-Care Score: {metrics.self_care_score:.1f}/10 💚")
        
        if metrics.crisis_alerts > 0:
            print(f"⚠️  {metrics.crisis_alerts} crisis alert(s)")
    
    else:
        print("\n📊 Wellness Dashboard")
        print("=" * 30)
        print("Available commands:")
        print("  om dashboard show           - Show static dashboard")
        print("  om dashboard live [seconds] - Start live dashboard (default: 30s refresh)")
        print("  om dashboard summary        - Quick wellness summary")
        print("  om dashboard export         - Export metrics to JSON")
        print()
        print("Note: Live dashboard requires 'pip install rich' for best experience")

if __name__ == "__main__":
    run()
