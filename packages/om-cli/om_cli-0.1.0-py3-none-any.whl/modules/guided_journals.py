"""
Guided Journals module for om - inspired by Intellect app
Structured journaling for mental health and self-reflection
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

JOURNALS_FILE = os.path.expanduser("~/.om_journals.json")

class GuidedJournals:
    def __init__(self):
        self.journal_types = {
            "problem_solving": {
                "title": "Problem-Solving Journal",
                "description": "Gain clarity on challenges you're facing",
                "duration": "10-15 minutes",
                "prompts": [
                    "What specific problem or challenge are you facing right now?",
                    "How is this problem affecting you emotionally and practically?",
                    "What factors might be contributing to this problem?",
                    "What aspects of this problem are within your control?",
                    "What aspects are outside your control?",
                    "What are 3 possible solutions or approaches you could try?",
                    "What would be the first small step you could take?",
                    "What support or resources might help you with this?",
                    "What would you tell a friend facing this same problem?"
                ]
            },
            "gratitude": {
                "title": "Gratitude Journal",
                "description": "Express appreciation and cultivate positive emotions",
                "duration": "5-10 minutes",
                "prompts": [
                    "What are three things you're grateful for today, and why?",
                    "Who is someone you appreciate, and what do they mean to you?",
                    "What's something positive that happened recently that you might have overlooked?",
                    "What's a challenge you've overcome that you can be grateful for?",
                    "What's something about your body or health you can appreciate?",
                    "What's a simple pleasure you enjoyed today?",
                    "What's something in your environment (home, nature, community) you're thankful for?",
                    "How has expressing gratitude affected your mood right now?"
                ]
            },
            "emotional_processing": {
                "title": "Emotional Processing Journal",
                "description": "Understand and work through difficult emotions",
                "duration": "10-20 minutes",
                "prompts": [
                    "What emotion(s) are you experiencing right now?",
                    "Where do you feel this emotion in your body?",
                    "What situation or thought triggered this emotion?",
                    "What is this emotion trying to tell you or protect you from?",
                    "Have you felt this way before? When?",
                    "What thoughts are connected to this emotion?",
                    "If this emotion could speak, what would it say?",
                    "What do you need right now to take care of yourself?",
                    "How can you show yourself compassion in this moment?"
                ]
            },
            "daily_reflection": {
                "title": "Daily Reflection Journal",
                "description": "Process your day and set intentions",
                "duration": "8-12 minutes",
                "prompts": [
                    "How would you describe your overall mood today?",
                    "What was the highlight of your day?",
                    "What was the most challenging part of your day?",
                    "What did you learn about yourself today?",
                    "How did you take care of your mental health today?",
                    "What are you proud of accomplishing today, no matter how small?",
                    "What would you do differently if you could repeat today?",
                    "What are you looking forward to tomorrow?",
                    "What intention do you want to set for tomorrow?"
                ]
            },
            "anxiety_exploration": {
                "title": "Anxiety Exploration Journal",
                "description": "Understand and manage anxious thoughts and feelings",
                "duration": "10-15 minutes",
                "prompts": [
                    "What are you feeling anxious about right now?",
                    "What physical sensations do you notice in your body?",
                    "What thoughts are going through your mind?",
                    "How likely is it that your worst fear will actually happen?",
                    "What evidence do you have for and against your anxious thoughts?",
                    "What would you tell a friend who had these same worries?",
                    "What's the worst that could realistically happen, and how would you cope?",
                    "What can you control in this situation?",
                    "What coping strategies have helped you with anxiety before?"
                ]
            },
            "self_compassion": {
                "title": "Self-Compassion Journal",
                "description": "Practice kindness and understanding toward yourself",
                "duration": "8-12 minutes",
                "prompts": [
                    "What are you being hard on yourself about right now?",
                    "How are you talking to yourself about this situation?",
                    "What would you say to a good friend in this same situation?",
                    "What part of this experience is part of being human?",
                    "How can you show yourself the same kindness you'd show a friend?",
                    "What do you need to hear right now to feel supported?",
                    "What's one thing you appreciate about how you're handling this challenge?",
                    "How can you take care of yourself today?",
                    "What would unconditional self-acceptance look like in this moment?"
                ]
            },
            "goal_setting": {
                "title": "Goal Setting & Motivation Journal",
                "description": "Clarify your goals and build motivation",
                "duration": "10-15 minutes",
                "prompts": [
                    "What's something important you want to achieve or change?",
                    "Why is this goal meaningful to you?",
                    "How will achieving this goal improve your life?",
                    "What obstacles might get in your way?",
                    "What strengths and resources do you have to help you succeed?",
                    "What would be the first small step toward this goal?",
                    "How will you know when you're making progress?",
                    "Who could support you in working toward this goal?",
                    "What would you tell yourself on days when motivation is low?"
                ]
            },
            "relationship_reflection": {
                "title": "Relationship Reflection Journal",
                "description": "Explore and improve your relationships",
                "duration": "10-15 minutes",
                "prompts": [
                    "Think of a relationship that's on your mind. What's happening in this relationship?",
                    "How do you feel when you're with this person?",
                    "What do you appreciate about this person?",
                    "What challenges exist in this relationship?",
                    "How do you contribute to the positive aspects of this relationship?",
                    "How might you be contributing to any difficulties?",
                    "What would you like to be different in this relationship?",
                    "What's one thing you could do to improve this relationship?",
                    "How can you communicate more effectively with this person?"
                ]
            },
            "open_writing": {
                "title": "Open Writing Journal",
                "description": "Free-form writing to explore whatever is on your mind",
                "duration": "10-20 minutes",
                "prompts": [
                    "What's on your mind right now? Write about whatever comes up...",
                    "Continue writing about whatever feels important to explore...",
                    "Keep writing, letting your thoughts flow freely...",
                    "What else wants to be expressed or explored?",
                    "As you continue writing, what are you noticing?",
                    "What insights or realizations are emerging?",
                    "What do you want to remember from this writing session?",
                    "How do you feel now compared to when you started writing?"
                ]
            }
        }
    
    def show_journal_menu(self):
        """Display available journal types"""
        print("📝 Guided Journals - Safe Space for Your Thoughts")
        print("=" * 60)
        print("Choose a journal type based on what you'd like to explore:")
        print()
        
        journal_types = list(self.journal_types.keys())
        for i, journal_type in enumerate(journal_types, 1):
            journal_info = self.journal_types[journal_type]
            print(f"{i}. {journal_info['title']}")
            print(f"   {journal_info['description']}")
            print(f"   Duration: {journal_info['duration']}")
            print()
        
        # Show recent entries
        recent_entries = self._get_recent_entries(5)
        if recent_entries:
            print("📖 Recent Journal Entries:")
            for entry in recent_entries:
                date = datetime.fromisoformat(entry["timestamp"]).strftime("%m-%d")
                journal_title = self.journal_types[entry["journal_type"]]["title"]
                print(f"   {date}: {journal_title}")
            print()
        
        choice = input("Choose a journal type (1-9) or press Enter to return: ").strip()
        
        if choice.isdigit():
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(journal_types):
                    self.start_journal_session(journal_types[choice_idx])
            except ValueError:
                pass
    
    def start_journal_session(self, journal_type: str):
        """Start a guided journal session"""
        if journal_type not in self.journal_types:
            print(f"Journal type '{journal_type}' not found.")
            return
        
        journal_info = self.journal_types[journal_type]
        
        print(f"\n📝 {journal_info['title']}")
        print("=" * 60)
        print(f"{journal_info['description']}")
        print(f"Estimated time: {journal_info['duration']}")
        print()
        
        print("💙 Welcome to your safe space for reflection.")
        print("There are no right or wrong answers - just write what feels true for you.")
        print("You can write as much or as little as you'd like for each prompt.")
        print()
        
        input("Press Enter when you're ready to begin...")
        print()
        
        # Journal session
        responses = []
        prompts = journal_info["prompts"]
        
        for i, prompt in enumerate(prompts, 1):
            print(f"📝 Prompt {i}/{len(prompts)}:")
            print(f"{prompt}")
            print()
            
            if journal_type == "open_writing" and i == 1:
                print("💡 Tip: For open writing, just let your thoughts flow. Don't worry about")
                print("   grammar, structure, or making sense. Write whatever comes to mind.")
                print()
            
            response = input("Your response: ").strip()
            
            if response:
                responses.append({
                    "prompt": prompt,
                    "response": response
                })
            else:
                # Allow skipping prompts
                skip = input("Skip this prompt? (y/n): ").strip().lower()
                if skip != 'y':
                    response = input("Your response: ").strip()
                    if response:
                        responses.append({
                            "prompt": prompt,
                            "response": response
                        })
            
            print()
            
            # Option to continue or finish early
            if i < len(prompts) and len(responses) >= 3:
                continue_choice = input("Continue with more prompts? (y/n): ").strip().lower()
                if continue_choice == 'n':
                    break
        
        # Session completion
        self._complete_journal_session(journal_type, journal_info, responses)
    
    def _complete_journal_session(self, journal_type: str, journal_info: Dict, responses: List[Dict]):
        """Complete the journal session with reflection and saving"""
        if not responses:
            print("No responses recorded. That's okay - sometimes just taking time")
            print("to think about these questions is valuable.")
            return
        
        print("✨ Journal Session Complete")
        print("=" * 40)
        print(f"You explored {len(responses)} prompts in your {journal_info['title']}.")
        print()
        
        # Brief reflection
        print("💭 Take a moment to reflect:")
        print("• How do you feel now compared to when you started?")
        print("• What insights or realizations emerged for you?")
        print("• What would you like to remember from this session?")
        print()
        
        reflection = input("Any final thoughts or insights? (optional): ").strip()
        
        # Save the journal entry
        entry_data = {
            "timestamp": datetime.now().isoformat(),
            "journal_type": journal_type,
            "journal_title": journal_info["title"],
            "responses": responses,
            "reflection": reflection,
            "session_duration": journal_info["duration"]
        }
        
        self._save_journal_entry(entry_data)
        
        print("\n📚 Your journal entry has been saved securely.")
        print("You can review your entries anytime with 'om journal --action history'")
        
        # Suggestions for follow-up
        self._suggest_followup_actions(journal_type, responses)
    
    def _suggest_followup_actions(self, journal_type: str, responses: List[Dict]):
        """Suggest follow-up actions based on journal type and content"""
        print("\n💡 Suggested next steps:")
        
        suggestions = {
            "problem_solving": [
                "• Take the first small step you identified",
                "• Use 'om coping' if you're feeling stressed about the problem",
                "• Consider discussing this with someone you trust"
            ],
            "gratitude": [
                "• Express appreciation to someone you wrote about",
                "• Notice more moments of gratitude throughout your day",
                "• Use 'om mood' to track how gratitude affects your mood"
            ],
            "emotional_processing": [
                "• Practice self-compassion as you process these emotions",
                "• Use 'om rescue' if you need immediate emotional support",
                "• Consider professional support if emotions feel overwhelming"
            ],
            "daily_reflection": [
                "• Set an intention for tomorrow based on your reflection",
                "• Use 'om habits' to track positive daily practices",
                "• Make daily reflection a regular practice"
            ],
            "anxiety_exploration": [
                "• Try 'om anxiety' for specific anxiety management techniques",
                "• Practice the coping strategies you identified",
                "• Use 'om rescue --feeling anxious' if anxiety feels overwhelming"
            ],
            "self_compassion": [
                "• Practice speaking to yourself with the kindness you wrote about",
                "• Use 'om rescue --feeling sad' if you need gentle support",
                "• Remember that self-compassion is a practice, not perfection"
            ],
            "goal_setting": [
                "• Take the first small step you identified",
                "• Use 'om habits' to track progress toward your goal",
                "• Break your goal into smaller, manageable steps"
            ],
            "relationship_reflection": [
                "• Consider having a conversation with the person you wrote about",
                "• Practice the communication strategies you identified",
                "• Use 'om learn' to explore relationship skills"
            ],
            "open_writing": [
                "• Re-read your writing in a few days for new insights",
                "• Continue free-writing regularly to process thoughts",
                "• Notice patterns in what you write about over time"
            ]
        }
        
        if journal_type in suggestions:
            for suggestion in suggestions[journal_type]:
                print(suggestion)
        
        print("• Return to journaling whenever you need to process thoughts and feelings")
    
    def show_journal_history(self):
        """Show history of journal entries"""
        entries = self._load_journal_entries()
        
        if not entries:
            print("📖 Journal History")
            print("=" * 30)
            print("You haven't written any journal entries yet.")
            print("Start with 'om journal' to begin your journaling journey!")
            return
        
        print("📖 Your Journal History")
        print("=" * 40)
        
        # Recent entries
        recent_entries = entries[-10:]
        print("Recent journal entries:")
        
        for entry in recent_entries:
            date = datetime.fromisoformat(entry["timestamp"]).strftime("%m-%d %H:%M")
            journal_title = entry["journal_title"]
            response_count = len(entry.get("responses", []))
            
            print(f"   {date}: {journal_title} ({response_count} responses)")
        
        print()
        
        # Statistics
        total_entries = len(entries)
        total_responses = sum(len(entry.get("responses", [])) for entry in entries)
        
        print(f"📊 Statistics:")
        print(f"   Total journal entries: {total_entries}")
        print(f"   Total responses written: {total_responses}")
        
        # Most used journal types
        type_counts = {}
        for entry in entries:
            journal_type = entry.get("journal_type", "unknown")
            type_counts[journal_type] = type_counts.get(journal_type, 0) + 1
        
        if type_counts:
            print(f"\n📝 Most used journal types:")
            sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
            for journal_type, count in sorted_types[:3]:
                if journal_type in self.journal_types:
                    journal_title = self.journal_types[journal_type]["title"]
                    print(f"   {journal_title}: {count} times")
        
        # Journaling streak
        streak = self._calculate_journaling_streak(entries)
        if streak > 0:
            print(f"\n🔥 Journaling streak: {streak} days")
        
        print("\n💡 Regular journaling helps you:")
        print("   • Process emotions and experiences")
        print("   • Gain insights about yourself")
        print("   • Track your mental health journey")
        print("   • Develop self-awareness and emotional intelligence")
        
        # Option to view specific entry
        print()
        view_entry = input("Would you like to view a specific entry? (y/n): ").strip().lower()
        if view_entry == 'y':
            self._view_specific_entry(entries)
    
    def _view_specific_entry(self, entries: List[Dict]):
        """Allow user to view a specific journal entry"""
        print("\nRecent entries:")
        recent_entries = entries[-10:]
        
        for i, entry in enumerate(recent_entries, 1):
            date = datetime.fromisoformat(entry["timestamp"]).strftime("%m-%d %H:%M")
            journal_title = entry["journal_title"]
            print(f"{i}. {date}: {journal_title}")
        
        choice = input(f"\nChoose entry to view (1-{len(recent_entries)}): ").strip()
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(recent_entries):
                entry = recent_entries[choice_idx]
                self._display_journal_entry(entry)
        except ValueError:
            print("Invalid choice.")
    
    def _display_journal_entry(self, entry: Dict):
        """Display a specific journal entry"""
        date = datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M")
        
        print(f"\n📖 {entry['journal_title']}")
        print(f"Date: {date}")
        print("=" * 50)
        
        for i, response_data in enumerate(entry.get("responses", []), 1):
            print(f"\nPrompt {i}: {response_data['prompt']}")
            print(f"Response: {response_data['response']}")
        
        if entry.get("reflection"):
            print(f"\nFinal Reflection: {entry['reflection']}")
        
        print("\n" + "=" * 50)
    
    def _calculate_journaling_streak(self, entries: List[Dict]) -> int:
        """Calculate current journaling streak"""
        if not entries:
            return 0
        
        # Get unique dates of journal entries
        entry_dates = []
        for entry in entries:
            entry_date = datetime.fromisoformat(entry["timestamp"]).date()
            entry_dates.append(entry_date)
        
        unique_dates = sorted(set(entry_dates), reverse=True)
        
        streak = 0
        current_date = datetime.now().date()
        
        for entry_date in unique_dates:
            if entry_date == current_date or entry_date == current_date - timedelta(days=streak):
                streak += 1
                current_date = entry_date
            else:
                break
        
        return streak
    
    def _get_recent_entries(self, limit: int = 5) -> List[Dict]:
        """Get recent journal entries"""
        entries = self._load_journal_entries()
        return entries[-limit:] if entries else []
    
    def _save_journal_entry(self, entry_data: Dict):
        """Save a journal entry"""
        entries = self._load_journal_entries()
        entries.append(entry_data)
        
        try:
            with open(JOURNALS_FILE, 'w') as f:
                json.dump(entries, f, indent=2)
        except Exception as e:
            print(f"Could not save journal entry: {e}")
    
    def _load_journal_entries(self) -> List[Dict]:
        """Load journal entries"""
        if not os.path.exists(JOURNALS_FILE):
            return []
        
        try:
            with open(JOURNALS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []


def guided_journals_command(action: str = "menu", **kwargs):
    """Main guided journals command interface"""
    journals = GuidedJournals()
    
    if action == "menu":
        journals.show_journal_menu()
    elif action == "start":
        journal_type = kwargs.get('type')
        if journal_type and journal_type in journals.journal_types:
            journals.start_journal_session(journal_type)
        else:
            print(f"Unknown journal type: {journal_type}")
            print(f"Available types: {', '.join(journals.journal_types.keys())}")
    elif action == "history":
        journals.show_journal_history()
    else:
        print(f"Unknown journal action: {action}")
        print("Available actions: menu, start, history")
