#!/usr/bin/env python3
"""
Example Textual TUI for om - Mental Health Dashboard
This shows how we could enhance om with rich terminal interfaces
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Header, Footer, Button, Static, ProgressBar, 
    DataTable, Input, TextArea, Label
)
from textual.reactive import reactive
from datetime import datetime
import asyncio

class MoodWidget(Static):
    """Widget to display current mood with emoji"""
    mood_level = reactive(5)
    
    def render(self) -> str:
        mood_emojis = {
            1: "😔", 2: "😕", 3: "😐", 4: "🙂", 5: "😊",
            6: "😄", 7: "😁", 8: "🤩", 9: "🥳", 10: "🌟"
        }
        emoji = mood_emojis.get(self.mood_level, "😐")
        return f"""
╭─────────────────╮
│   Current Mood  │
│                 │
│       {emoji}        │
│    {self.mood_level}/10 Level    │
╰─────────────────╯
        """

class WellnessStats(Static):
    """Widget showing wellness statistics"""
    
    def render(self) -> str:
        return """
╭─── Wellness Stats ───╮
│                      │
│ 🧘 Meditation: 5 min │
│ 🫁 Breathing:  3 min │
│ 🙏 Gratitude:  Done  │
│ 💪 Exercise:   None  │
│                      │
│ Streak: 🔥 7 days    │
╰──────────────────────╯
        """

class QuickActions(Container):
    """Container for quick action buttons"""
    
    def compose(self) -> ComposeResult:
        yield Button("Quick Mood 😊", id="mood", variant="primary")
        yield Button("Breathing 🫁", id="breathe", variant="success")
        yield Button("Gratitude 🙏", id="gratitude", variant="warning")
        yield Button("Crisis Help 🆘", id="crisis", variant="error")

class AchievementGallery(DataTable):
    """Table showing recent achievements"""
    
    def on_mount(self) -> None:
        self.add_columns("Achievement", "Date", "Status")
        self.add_rows([
            ("First Mood Entry", "2025-01-20", "✅"),
            ("3-Day Streak", "2025-01-22", "✅"),
            ("Breathing Master", "2025-01-25", "🔄"),
            ("Gratitude Heart", "2025-01-26", "🔄"),
        ])

class BreathingGuide(Container):
    """Interactive breathing exercise widget"""
    
    def compose(self) -> ComposeResult:
        yield Label("🫁 4-7-8 Breathing Exercise")
        yield ProgressBar(total=100, show_eta=False, id="breath_progress")
        yield Static("Breathe in... Hold... Breathe out...", id="breath_instruction")
        yield Button("Start Breathing", id="start_breathing", variant="primary")

class OmDashboard(App):
    """Main om mental health dashboard TUI"""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 3 3;
        grid-gutter: 1;
    }
    
    MoodWidget {
        column-span: 1;
        row-span: 1;
        border: solid $primary;
        text-align: center;
    }
    
    WellnessStats {
        column-span: 1;
        row-span: 2;
        border: solid $success;
    }
    
    QuickActions {
        column-span: 1;
        row-span: 1;
        layout: vertical;
    }
    
    QuickActions Button {
        margin: 1;
        width: 100%;
    }
    
    AchievementGallery {
        column-span: 2;
        row-span: 1;
        border: solid $warning;
    }
    
    BreathingGuide {
        column-span: 2;
        row-span: 1;
        border: solid $accent;
        layout: vertical;
    }
    
    #breath_progress {
        margin: 1;
    }
    
    #breath_instruction {
        text-align: center;
        margin: 1;
    }
    """
    
    TITLE = "om - Mental Health Dashboard 🧘‍♀️"
    SUB_TITLE = "Your wellness companion"
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield MoodWidget()
        yield WellnessStats()
        yield QuickActions()
        yield AchievementGallery()
        yield BreathingGuide()
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "mood":
            self.notify("Quick mood check started! 😊")
            # Here we could launch the mood tracking
            
        elif button_id == "breathe":
            self.notify("Starting breathing exercise... 🫁")
            # Launch breathing exercise
            
        elif button_id == "gratitude":
            self.notify("Gratitude practice time! 🙏")
            # Launch gratitude practice
            
        elif button_id == "crisis":
            self.notify("Crisis support resources available 🆘", severity="error")
            # Show crisis support
            
        elif button_id == "start_breathing":
            self.start_breathing_exercise()
    
    async def start_breathing_exercise(self):
        """Animated breathing exercise"""
        progress_bar = self.query_one("#breath_progress", ProgressBar)
        instruction = self.query_one("#breath_instruction", Static)
        
        # 4-7-8 breathing cycle
        for cycle in range(4):  # 4 cycles
            # Inhale (4 seconds)
            instruction.update("🌬️ Breathe in through nose...")
            for i in range(4):
                progress_bar.progress = (i + 1) * 25
                await asyncio.sleep(1)
            
            # Hold (7 seconds)
            instruction.update("⏸️ Hold your breath...")
            await asyncio.sleep(7)
            
            # Exhale (8 seconds)
            instruction.update("💨 Breathe out through mouth...")
            for i in range(4):
                progress_bar.progress = 100 - (i + 1) * 25
                await asyncio.sleep(2)
            
            progress_bar.progress = 0
            
        instruction.update("✅ Breathing exercise complete!")
        self.notify("Great job! You completed 4 breathing cycles 🌟")

if __name__ == "__main__":
    app = OmDashboard()
    app.run()
