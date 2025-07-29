"""
Quick capture system for om - inspired by Logbuch
Rapidly capture thoughts, ideas, and insights
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum

CAPTURES_FILE = os.path.expanduser("~/.om_captures.json")

class CaptureType(Enum):
    IDEA = "idea"           # 💡 Random ideas and inspirations
    INSIGHT = "insight"     # 🧠 Mental health insights
    GRATITUDE = "gratitude" # 🙏 Things to be grateful for
    AFFIRMATION = "affirmation"  # 💪 Positive self-talk
    GOAL = "goal"           # 🎯 Aspirations and objectives
    REMINDER = "reminder"   # ⏰ Things to remember
    QUOTE = "quote"         # 💬 Memorable quotes
    REFLECTION = "reflection"  # 🤔 Thoughts and reflections

@dataclass
class QuickCapture:
    id: str
    type: CaptureType
    content: str
    tags: List[str]
    priority: str  # low, medium, high
    created_at: datetime
    processed: bool = False
    mood_context: Optional[str] = None

class QuickCaptureSystem:
    def __init__(self):
        self.type_emojis = {
            CaptureType.IDEA: "💡",
            CaptureType.INSIGHT: "🧠", 
            CaptureType.GRATITUDE: "🙏",
            CaptureType.AFFIRMATION: "💪",
            CaptureType.GOAL: "🎯",
            CaptureType.REMINDER: "⏰",
            CaptureType.QUOTE: "💬",
            CaptureType.REFLECTION: "🤔"
        }
    
    def capture(self, content: str, capture_type: str = "idea", tags: List[str] = None, priority: str = "medium"):
        """Quickly capture a thought or idea"""
        if tags is None:
            tags = []
        
        try:
            capture_type_enum = CaptureType(capture_type.lower())
        except ValueError:
            print(f"Unknown capture type: {capture_type}")
            print(f"Available types: {', '.join([t.value for t in CaptureType])}")
            return
        
        capture = QuickCapture(
            id=str(uuid.uuid4())[:8],
            type=capture_type_enum,
            content=content,
            tags=tags,
            priority=priority,
            created_at=datetime.now()
        )
        
        self._save_capture(capture)
        self._display_captured(capture)
    
    def interactive_capture(self):
        """Interactive capture session"""
        print("⚡ Quick Capture - Capture your thoughts instantly!")
        print()
        
        # Show capture types
        print("📝 Capture Types:")
        for i, capture_type in enumerate(CaptureType, 1):
            emoji = self.type_emojis[capture_type]
            print(f"  {i}. {emoji} {capture_type.value.title()}")
        
        print()
        
        # Get capture type
        try:
            choice = input("Choose type (1-8) or type name: ").strip()
            if choice.isdigit():
                type_index = int(choice) - 1
                if 0 <= type_index < len(CaptureType):
                    capture_type = list(CaptureType)[type_index]
                else:
                    capture_type = CaptureType.IDEA
            else:
                capture_type = CaptureType(choice.lower())
        except (ValueError, IndexError):
            capture_type = CaptureType.IDEA
        
        # Get content
        emoji = self.type_emojis[capture_type]
        content = input(f"{emoji} What's on your mind? ").strip()
        
        if not content:
            print("No content entered. Capture cancelled.")
            return
        
        # Get tags
        tags_input = input("Tags (comma-separated, optional): ").strip()
        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
        
        # Get priority
        priority = input("Priority (low/medium/high, default: medium): ").strip().lower()
        if priority not in ['low', 'medium', 'high']:
            priority = 'medium'
        
        # Create capture
        capture = QuickCapture(
            id=str(uuid.uuid4())[:8],
            type=capture_type,
            content=content,
            tags=tags,
            priority=priority,
            created_at=datetime.now()
        )
        
        self._save_capture(capture)
        self._display_captured(capture)
        
        # Ask if they want to capture more
        if input("\nCapture another? (y/N): ").strip().lower() == 'y':
            self.interactive_capture()
    
    def list_captures(self, capture_type: str = None, unprocessed_only: bool = False, limit: int = 20):
        """List captured items"""
        captures = self._load_captures()
        
        if not captures:
            print("No captures found. Use 'om capture' to start capturing thoughts!")
            return
        
        # Filter by type
        if capture_type:
            try:
                type_filter = CaptureType(capture_type.lower())
                captures = [c for c in captures if c['type'] == type_filter.value]
            except ValueError:
                print(f"Unknown capture type: {capture_type}")
                return
        
        # Filter unprocessed
        if unprocessed_only:
            captures = [c for c in captures if not c.get('processed', False)]
        
        # Sort by date (newest first)
        captures.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Limit results
        captures = captures[:limit]
        
        if not captures:
            filter_desc = f" ({capture_type})" if capture_type else ""
            processed_desc = " unprocessed" if unprocessed_only else ""
            print(f"No{processed_desc} captures found{filter_desc}.")
            return
        
        print(f"📋 Your Captures ({len(captures)} items)")
        print("=" * 50)
        
        for capture in captures:
            self._display_capture_item(capture)
    
    def process_capture(self, capture_id: str):
        """Mark a capture as processed"""
        captures = self._load_captures()
        
        for capture in captures:
            if capture['id'] == capture_id:
                capture['processed'] = True
                self._save_captures(captures)
                
                emoji = self.type_emojis[CaptureType(capture['type'])]
                print(f"✅ {emoji} Marked capture as processed: {capture['content'][:50]}...")
                return
        
        print(f"Capture with ID {capture_id} not found.")
    
    def search_captures(self, query: str):
        """Search through captures"""
        captures = self._load_captures()
        
        if not captures:
            print("No captures to search.")
            return
        
        query_lower = query.lower()
        matches = []
        
        for capture in captures:
            # Search in content, tags, and type
            if (query_lower in capture['content'].lower() or 
                any(query_lower in tag.lower() for tag in capture.get('tags', [])) or
                query_lower in capture['type']):
                matches.append(capture)
        
        if not matches:
            print(f"No captures found matching '{query}'")
            return
        
        print(f"🔍 Search Results for '{query}' ({len(matches)} matches)")
        print("=" * 50)
        
        for capture in matches:
            self._display_capture_item(capture)
    
    def stats(self):
        """Show capture statistics"""
        captures = self._load_captures()
        
        if not captures:
            print("No captures found.")
            return
        
        print("📊 Capture Statistics")
        print("=" * 30)
        
        # Total counts
        total = len(captures)
        processed = len([c for c in captures if c.get('processed', False)])
        unprocessed = total - processed
        
        print(f"Total captures: {total}")
        print(f"Processed: {processed}")
        print(f"Unprocessed: {unprocessed}")
        print()
        
        # By type
        type_counts = {}
        for capture in captures:
            capture_type = capture['type']
            type_counts[capture_type] = type_counts.get(capture_type, 0) + 1
        
        print("📝 By Type:")
        for capture_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            emoji = self.type_emojis[CaptureType(capture_type)]
            percentage = (count / total) * 100
            print(f"  {emoji} {capture_type.title()}: {count} ({percentage:.1f}%)")
        
        print()
        
        # By priority
        priority_counts = {}
        for capture in captures:
            priority = capture.get('priority', 'medium')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        print("🎯 By Priority:")
        for priority in ['high', 'medium', 'low']:
            count = priority_counts.get(priority, 0)
            if count > 0:
                percentage = (count / total) * 100
                print(f"  {priority.title()}: {count} ({percentage:.1f}%)")
        
        # Recent activity
        from datetime import timedelta
        recent_captures = [
            c for c in captures 
            if datetime.fromisoformat(c['created_at']) >= datetime.now() - timedelta(days=7)
        ]
        
        print(f"\n📈 Recent Activity:")
        print(f"  Last 7 days: {len(recent_captures)} captures")
    
    def _display_capture_item(self, capture: Dict):
        """Display a single capture item"""
        emoji = self.type_emojis[CaptureType(capture['type'])]
        status = "✅" if capture.get('processed', False) else "⭕"
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(capture.get('priority', 'medium'), "🟡")
        
        created = datetime.fromisoformat(capture['created_at'])
        time_str = created.strftime("%m-%d %H:%M")
        
        print(f"{status} {emoji} [{capture['id']}] {priority_emoji} {capture['content']}")
        
        if capture.get('tags'):
            print(f"    🏷️  {', '.join(capture['tags'])}")
        
        print(f"    📅 {time_str}")
        print()
    
    def _display_captured(self, capture: QuickCapture):
        """Display confirmation of captured item"""
        emoji = self.type_emojis[capture.type]
        print(f"\n⚡ {emoji} Captured: {capture.content}")
        print(f"   Type: {capture.type.value}")
        print(f"   Priority: {capture.priority}")
        if capture.tags:
            print(f"   Tags: {', '.join(capture.tags)}")
        print(f"   ID: {capture.id}")
    
    def _save_capture(self, capture: QuickCapture):
        """Save a single capture"""
        captures = self._load_captures()
        capture_dict = asdict(capture)
        # Convert enum to string for JSON serialization
        capture_dict['type'] = capture_dict['type'].value
        capture_dict['created_at'] = capture_dict['created_at'].isoformat()
        captures.append(capture_dict)
        self._save_captures(captures)
    
    def _save_captures(self, captures: List[Dict]):
        """Save all captures to file"""
        try:
            with open(CAPTURES_FILE, 'w') as f:
                json.dump(captures, f, indent=2)
        except Exception as e:
            print(f"Could not save captures: {e}")
    
    def _load_captures(self) -> List[Dict]:
        """Load captures from file"""
        if not os.path.exists(CAPTURES_FILE):
            return []
        
        try:
            with open(CAPTURES_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []


def capture_command(action: str = "interactive", **kwargs):
    """Main capture command interface"""
    system = QuickCaptureSystem()
    
    if action == "interactive" or action == "add":
        if kwargs.get('content'):
            # Direct capture
            system.capture(
                content=kwargs['content'],
                capture_type=kwargs.get('type', 'idea'),
                tags=kwargs.get('tags', []),
                priority=kwargs.get('priority', 'medium')
            )
        else:
            # Interactive capture
            system.interactive_capture()
    
    elif action == "list":
        system.list_captures(
            capture_type=kwargs.get('type'),
            unprocessed_only=kwargs.get('unprocessed', False),
            limit=kwargs.get('limit', 20)
        )
    
    elif action == "process":
        capture_id = kwargs.get('id')
        if capture_id:
            system.process_capture(capture_id)
        else:
            print("Please provide a capture ID to process")
    
    elif action == "search":
        query = kwargs.get('query')
        if query:
            system.search_captures(query)
        else:
            print("Please provide a search query")
    
    elif action == "stats":
        system.stats()
    
    else:
        print(f"Unknown capture action: {action}")
        print("Available actions: add, list, process, search, stats")
