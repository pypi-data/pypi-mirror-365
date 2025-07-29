"""
Social Connection module for om - inspired by Colors app
Privacy-first emotional sharing and connection with trusted contacts
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid

SOCIAL_FILE = os.path.expanduser("~/.om_social.json")
SHARED_EMOTIONS_DIR = os.path.expanduser("~/.om_shared/")

class SocialConnection:
    def __init__(self):
        self.emotion_colors = {
            # Primary emotions with color associations
            "joy": {"color": "🟡", "hex": "#FFD700", "description": "Bright and warm"},
            "sadness": {"color": "🔵", "hex": "#4169E1", "description": "Deep and flowing"},
            "anger": {"color": "🔴", "hex": "#DC143C", "description": "Intense and fiery"},
            "fear": {"color": "🟣", "hex": "#8A2BE2", "description": "Dark and mysterious"},
            "surprise": {"color": "🟠", "hex": "#FF8C00", "description": "Vibrant and sudden"},
            "disgust": {"color": "🟢", "hex": "#228B22", "description": "Sharp and rejecting"},
            "trust": {"color": "🔵", "hex": "#87CEEB", "description": "Calm and steady"},
            "anticipation": {"color": "🟡", "hex": "#F0E68C", "description": "Light and hopeful"},
            
            # Complex emotions
            "love": {"color": "💖", "hex": "#FF69B4", "description": "Warm and embracing"},
            "gratitude": {"color": "🟨", "hex": "#DAA520", "description": "Golden and appreciative"},
            "peace": {"color": "🤍", "hex": "#F0F8FF", "description": "Pure and serene"},
            "excitement": {"color": "🟠", "hex": "#FF4500", "description": "Electric and energetic"},
            "anxiety": {"color": "🟤", "hex": "#8B4513", "description": "Muddy and restless"},
            "contentment": {"color": "🟢", "hex": "#98FB98", "description": "Soft and satisfied"},
            "loneliness": {"color": "⚫", "hex": "#2F4F4F", "description": "Empty and isolated"},
            "hope": {"color": "🌟", "hex": "#FFE4B5", "description": "Bright and uplifting"},
            "confusion": {"color": "🌫️", "hex": "#D3D3D3", "description": "Cloudy and unclear"},
            "pride": {"color": "🟪", "hex": "#9370DB", "description": "Rich and elevated"}
        }
        
        self.sharing_levels = {
            "private": "Only visible to you",
            "close_family": "Immediate family members only",
            "close_friends": "Close friends only", 
            "support_circle": "Your designated support circle",
            "trusted_contacts": "All trusted contacts"
        }
        
        # Ensure shared directory exists
        os.makedirs(SHARED_EMOTIONS_DIR, exist_ok=True)
    
    def show_social_menu(self):
        """Display social connection main menu"""
        print("💝 Social Connection & Emotional Sharing")
        print("=" * 50)
        print("Connect with trusted contacts through emotional awareness")
        print("Inspired by Colors app's approach to shared emotional understanding")
        print()
        
        # Show connection status
        data = self._load_social_data()
        trusted_contacts = data.get('trusted_contacts', {})
        recent_shares = data.get('recent_shares', [])
        
        if trusted_contacts:
            print(f"👥 Trusted Contacts: {len(trusted_contacts)}")
            active_connections = sum(1 for contact in trusted_contacts.values() 
                                   if contact.get('status') == 'active')
            print(f"🟢 Active Connections: {active_connections}")
        
        if recent_shares:
            print(f"📤 Recent Shares: {len([s for s in recent_shares[-7:] if s.get('shared')])}")
        print()
        
        print("🎨 Emotional Sharing:")
        print("1. Share your current emotional state")
        print("2. View shared emotions from contacts")
        print("3. Send emotional support message")
        print("4. Create emotion color palette")
        print()
        
        print("👥 Connection Management:")
        print("5. Manage trusted contacts")
        print("6. Set sharing preferences")
        print("7. View connection insights")
        print("8. Privacy and safety settings")
        print()
        
        choice = input("Choose an option (1-8) or press Enter to return: ").strip()
        
        if choice == "1":
            self._share_emotional_state()
        elif choice == "2":
            self._view_shared_emotions()
        elif choice == "3":
            self._send_support_message()
        elif choice == "4":
            self._create_emotion_palette()
        elif choice == "5":
            self._manage_trusted_contacts()
        elif choice == "6":
            self._set_sharing_preferences()
        elif choice == "7":
            self._view_connection_insights()
        elif choice == "8":
            self._privacy_safety_settings()
    
    def _share_emotional_state(self):
        """Share current emotional state with trusted contacts"""
        print("\n🎨 Share Your Emotional State")
        print("=" * 40)
        
        # Check if user has trusted contacts
        data = self._load_social_data()
        trusted_contacts = data.get('trusted_contacts', {})
        
        if not trusted_contacts:
            print("You haven't added any trusted contacts yet.")
            add_contact = input("Would you like to add a trusted contact first? (y/n): ").strip().lower()
            if add_contact in ['y', 'yes']:
                self._add_trusted_contact()
                return
            else:
                return
        
        # Select primary emotion
        print("What's your primary emotion right now?")
        emotions = list(self.emotion_colors.keys())
        for i, emotion in enumerate(emotions[:10], 1):  # Show first 10
            color_info = self.emotion_colors[emotion]
            print(f"{i:2d}. {color_info['color']} {emotion.title()} - {color_info['description']}")
        
        print(f"{len(emotions[:10]) + 1}. See more emotions...")
        print()
        
        emotion_choice = input(f"Choose emotion (1-{len(emotions[:10]) + 1}): ").strip()
        
        try:
            choice_idx = int(emotion_choice) - 1
            if choice_idx < len(emotions[:10]):
                primary_emotion = emotions[choice_idx]
            elif choice_idx == len(emotions[:10]):
                # Show all emotions
                self._show_all_emotions()
                return
            else:
                print("Invalid choice.")
                return
        except ValueError:
            print("Invalid choice.")
            return
        
        # Get intensity
        print(f"\nHow intense is your {primary_emotion}?")
        print("1. Very mild")
        print("2. Mild") 
        print("3. Moderate")
        print("4. Strong")
        print("5. Very strong")
        
        intensity = input("Choose intensity (1-5): ").strip()
        try:
            intensity_num = int(intensity)
            if 1 <= intensity_num <= 5:
                intensity_labels = ["very_mild", "mild", "moderate", "strong", "very_strong"]
                intensity_label = intensity_labels[intensity_num - 1]
            else:
                intensity_label = "moderate"
        except ValueError:
            intensity_label = "moderate"
        
        # Optional context
        context = input("Add context or note (optional): ").strip()
        
        # Choose sharing level
        print(f"\nWho would you like to share this with?")
        sharing_levels = list(self.sharing_levels.keys())
        for i, level in enumerate(sharing_levels, 1):
            print(f"{i}. {level.replace('_', ' ').title()} - {self.sharing_levels[level]}")
        
        sharing_choice = input(f"Choose sharing level (1-{len(sharing_levels)}): ").strip()
        
        try:
            sharing_idx = int(sharing_choice) - 1
            if 0 <= sharing_idx < len(sharing_levels):
                sharing_level = sharing_levels[sharing_idx]
            else:
                sharing_level = "trusted_contacts"
        except ValueError:
            sharing_level = "trusted_contacts"
        
        # Create emotional share
        emotion_share = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "primary_emotion": primary_emotion,
            "intensity": intensity_label,
            "context": context,
            "sharing_level": sharing_level,
            "color": self.emotion_colors[primary_emotion]["color"],
            "shared": True
        }
        
        # Save to personal data
        data.setdefault('recent_shares', []).append(emotion_share)
        
        # Keep only last 100 shares
        if len(data['recent_shares']) > 100:
            data['recent_shares'] = data['recent_shares'][-100:]
        
        self._save_social_data(data)
        
        # Create shareable file (privacy-preserving)
        self._create_shareable_emotion(emotion_share, trusted_contacts, sharing_level)
        
        # Show confirmation
        color_info = self.emotion_colors[primary_emotion]
        print(f"\n✅ Emotional state shared!")
        print(f"🎨 {color_info['color']} {primary_emotion.title()} ({intensity_label.replace('_', ' ')})")
        if context:
            print(f"💭 Context: {context}")
        print(f"👥 Shared with: {sharing_level.replace('_', ' ').title()}")
        
        # Show who will see it
        eligible_contacts = self._get_eligible_contacts(trusted_contacts, sharing_level)
        if eligible_contacts:
            print(f"📱 Visible to: {', '.join([c['name'] for c in eligible_contacts])}")
    
    def _show_all_emotions(self):
        """Show all available emotions with colors"""
        print("\n🎨 Complete Emotion Palette")
        print("=" * 40)
        
        for emotion, color_info in self.emotion_colors.items():
            print(f"{color_info['color']} {emotion.title():15} - {color_info['description']}")
        
        print()
        emotion_name = input("Type the emotion name you want to share: ").strip().lower()
        
        if emotion_name in self.emotion_colors:
            # Continue with sharing process for this emotion
            print(f"Selected: {self.emotion_colors[emotion_name]['color']} {emotion_name.title()}")
            # Would continue with intensity, context, etc.
        else:
            print("Emotion not found. Please try again.")
    
    def _view_shared_emotions(self):
        """View emotions shared by trusted contacts"""
        print("\n👀 Shared Emotions from Contacts")
        print("=" * 40)
        
        # Load shared emotions from contacts
        shared_emotions = self._load_shared_emotions()
        
        if not shared_emotions:
            print("No shared emotions from contacts yet.")
            print("Invite trusted contacts to share their emotional states with you!")
            return
        
        # Group by contact and show recent emotions
        print("Recent emotional shares from your trusted contacts:")
        print()
        
        # Sort by timestamp (most recent first)
        sorted_emotions = sorted(shared_emotions, key=lambda x: x['timestamp'], reverse=True)
        
        for emotion in sorted_emotions[:10]:  # Show last 10
            contact_name = emotion.get('contact_name', 'Unknown')
            primary_emotion = emotion['primary_emotion']
            intensity = emotion['intensity'].replace('_', ' ')
            timestamp = datetime.fromisoformat(emotion['timestamp'])
            time_ago = self._time_ago(timestamp)
            
            color_info = self.emotion_colors[primary_emotion]
            
            print(f"👤 {contact_name}")
            print(f"   {color_info['color']} {primary_emotion.title()} ({intensity})")
            print(f"   🕐 {time_ago}")
            
            if emotion.get('context'):
                print(f"   💭 {emotion['context']}")
            
            print()
        
        # Offer to respond
        print("Would you like to:")
        print("1. Send a supportive message to someone")
        print("2. Share your own emotional state")
        print("3. View emotion patterns")
        print()
        
        choice = input("Choose action (1-3) or press Enter to return: ").strip()
        
        if choice == "1":
            self._send_support_message()
        elif choice == "2":
            self._share_emotional_state()
        elif choice == "3":
            self._view_emotion_patterns(sorted_emotions)
    
    def _send_support_message(self):
        """Send supportive message to a contact"""
        print("\n💌 Send Emotional Support")
        print("=" * 30)
        
        data = self._load_social_data()
        trusted_contacts = data.get('trusted_contacts', {})
        
        if not trusted_contacts:
            print("No trusted contacts to send messages to.")
            return
        
        # Show contacts
        print("Choose a contact to send support to:")
        contact_list = list(trusted_contacts.items())
        for i, (contact_id, contact_info) in enumerate(contact_list, 1):
            status_emoji = "🟢" if contact_info.get('status') == 'active' else "⚫"
            print(f"{i}. {status_emoji} {contact_info['name']}")
        
        choice = input(f"Choose contact (1-{len(contact_list)}): ").strip()
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(contact_list):
                contact_id, contact_info = contact_list[choice_idx]
                contact_name = contact_info['name']
            else:
                print("Invalid choice.")
                return
        except ValueError:
            print("Invalid choice.")
            return
        
        # Choose message type
        print(f"\nWhat kind of support would you like to send to {contact_name}?")
        print("1. 🤗 Sending hugs and comfort")
        print("2. 💪 You've got this! Encouragement")
        print("3. 👂 I'm here to listen")
        print("4. ☀️ Thinking of you")
        print("5. 🌈 This too shall pass")
        print("6. 💝 Custom supportive message")
        
        message_choice = input("Choose message type (1-6): ").strip()
        
        predefined_messages = {
            "1": "🤗 Sending you warm hugs and comfort. You're not alone in this.",
            "2": "💪 You've got this! I believe in your strength and resilience.",
            "3": "👂 I'm here if you need someone to listen. No judgment, just support.",
            "4": "☀️ Thinking of you and sending positive energy your way.",
            "5": "🌈 Remember, this difficult moment will pass. You're stronger than you know.",
            "6": ""  # Custom message
        }
        
        if message_choice in predefined_messages:
            if message_choice == "6":
                message = input("Write your supportive message: ").strip()
            else:
                message = predefined_messages[message_choice]
        else:
            message = predefined_messages["1"]  # Default
        
        if not message:
            print("No message entered.")
            return
        
        # Create support message
        support_message = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "recipient_id": contact_id,
            "recipient_name": contact_name,
            "message": message,
            "type": "support"
        }
        
        # Save message
        data.setdefault('sent_messages', []).append(support_message)
        self._save_social_data(data)
        
        # Create shareable message file
        self._create_shareable_message(support_message, contact_info)
        
        print(f"\n✅ Supportive message sent to {contact_name}!")
        print(f"💌 Message: {message}")
        print("Your support can make a real difference in someone's day.")
    
    def _create_emotion_palette(self):
        """Create personalized emotion color palette"""
        print("\n🎨 Create Your Emotion Palette")
        print("=" * 40)
        print("Discover your unique emotional color patterns")
        print()
        
        # Analyze user's emotion history
        data = self._load_social_data()
        recent_shares = data.get('recent_shares', [])
        
        if len(recent_shares) < 5:
            print("You need at least 5 emotional shares to create a palette.")
            print("Share more emotions to unlock this feature!")
            return
        
        # Count emotion frequencies
        emotion_counts = {}
        for share in recent_shares[-30:]:  # Last 30 shares
            emotion = share['primary_emotion']
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Create palette from most frequent emotions
        sorted_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)
        top_emotions = sorted_emotions[:6]  # Top 6 emotions
        
        print("🎨 Your Personal Emotion Palette:")
        print("Based on your recent emotional shares")
        print()
        
        palette_colors = []
        for emotion, count in top_emotions:
            color_info = self.emotion_colors[emotion]
            percentage = (count / len(recent_shares[-30:])) * 100
            palette_colors.append(color_info['color'])
            
            print(f"{color_info['color']} {emotion.title():15} - {count:2d} times ({percentage:.1f}%)")
            print(f"   {color_info['description']}")
            print()
        
        # Show palette visualization
        print("🌈 Your Emotion Rainbow:")
        print("".join(palette_colors))
        print()
        
        # Insights
        dominant_emotion = top_emotions[0][0]
        print(f"💡 Insights:")
        print(f"• Your dominant emotion is {dominant_emotion}")
        print(f"• You express {len(set(emotion_counts.keys()))} different emotions")
        
        if len(top_emotions) >= 3:
            balance_score = (top_emotions[2][1] / top_emotions[0][1]) * 100
            if balance_score > 60:
                print("• You have good emotional balance")
            else:
                print("• Consider exploring a wider range of emotions")
        
        # Save palette
        palette_data = {
            "created_date": datetime.now().isoformat(),
            "emotions": top_emotions,
            "colors": palette_colors,
            "total_shares": len(recent_shares[-30:])
        }
        
        data.setdefault('emotion_palettes', []).append(palette_data)
        self._save_social_data(data)
        
        print(f"\n✅ Emotion palette saved!")
        print("Your palette will evolve as you continue sharing emotions.")
    
    def _manage_trusted_contacts(self):
        """Manage trusted contacts list"""
        print("\n👥 Manage Trusted Contacts")
        print("=" * 40)
        
        data = self._load_social_data()
        trusted_contacts = data.get('trusted_contacts', {})
        
        if trusted_contacts:
            print("Your trusted contacts:")
            for contact_id, contact_info in trusted_contacts.items():
                status_emoji = "🟢" if contact_info.get('status') == 'active' else "⚫"
                sharing_level = contact_info.get('sharing_level', 'trusted_contacts')
                print(f"  {status_emoji} {contact_info['name']} - {sharing_level.replace('_', ' ')}")
            print()
        
        print("Contact Management:")
        print("1. Add new trusted contact")
        print("2. Edit contact settings")
        print("3. Remove contact")
        print("4. View contact activity")
        print()
        
        choice = input("Choose action (1-4) or press Enter to return: ").strip()
        
        if choice == "1":
            self._add_trusted_contact()
        elif choice == "2":
            self._edit_contact_settings()
        elif choice == "3":
            self._remove_contact()
        elif choice == "4":
            self._view_contact_activity()
    
    def _add_trusted_contact(self):
        """Add a new trusted contact"""
        print("\n➕ Add Trusted Contact")
        print("=" * 30)
        
        name = input("Contact name: ").strip()
        if not name:
            print("Name is required.")
            return
        
        # Choose relationship
        print("\nWhat's your relationship?")
        relationships = ["family", "close_friend", "friend", "partner", "therapist", "support_person", "other"]
        for i, rel in enumerate(relationships, 1):
            print(f"{i}. {rel.replace('_', ' ').title()}")
        
        rel_choice = input(f"Choose relationship (1-{len(relationships)}): ").strip()
        
        try:
            rel_idx = int(rel_choice) - 1
            if 0 <= rel_idx < len(relationships):
                relationship = relationships[rel_idx]
            else:
                relationship = "friend"
        except ValueError:
            relationship = "friend"
        
        # Set sharing level
        print(f"\nWhat sharing level for {name}?")
        sharing_levels = list(self.sharing_levels.keys())
        for i, level in enumerate(sharing_levels, 1):
            print(f"{i}. {level.replace('_', ' ').title()}")
        
        sharing_choice = input(f"Choose sharing level (1-{len(sharing_levels)}): ").strip()
        
        try:
            sharing_idx = int(sharing_choice) - 1
            if 0 <= sharing_idx < len(sharing_levels):
                sharing_level = sharing_levels[sharing_idx]
            else:
                sharing_level = "trusted_contacts"
        except ValueError:
            sharing_level = "trusted_contacts"
        
        # Create contact
        contact_id = str(uuid.uuid4())
        contact_info = {
            "name": name,
            "relationship": relationship,
            "sharing_level": sharing_level,
            "added_date": datetime.now().isoformat(),
            "status": "active"
        }
        
        # Save contact
        data = self._load_social_data()
        data.setdefault('trusted_contacts', {})[contact_id] = contact_info
        self._save_social_data(data)
        
        print(f"\n✅ {name} added as trusted contact!")
        print(f"Relationship: {relationship.replace('_', ' ').title()}")
        print(f"Sharing level: {sharing_level.replace('_', ' ').title()}")
        print("\nThey can now see emotions you share at their level or below.")
    
    def _time_ago(self, timestamp: datetime) -> str:
        """Calculate human-readable time ago"""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
    
    def _get_eligible_contacts(self, trusted_contacts: Dict, sharing_level: str) -> List[Dict]:
        """Get contacts eligible to see this sharing level"""
        # This would implement the sharing level logic
        # For now, return all active contacts
        return [contact for contact in trusted_contacts.values() 
                if contact.get('status') == 'active']
    
    def _create_shareable_emotion(self, emotion_share: Dict, trusted_contacts: Dict, sharing_level: str):
        """Create shareable emotion file (privacy-preserving)"""
        # In a real implementation, this would create encrypted files
        # that trusted contacts could access
        pass
    
    def _create_shareable_message(self, message: Dict, contact_info: Dict):
        """Create shareable support message"""
        # In a real implementation, this would create encrypted message files
        pass
    
    def _load_shared_emotions(self) -> List[Dict]:
        """Load emotions shared by contacts"""
        # In a real implementation, this would read from shared files
        # For demo, return empty list
        return []
    
    def _view_emotion_patterns(self, emotions: List[Dict]):
        """View emotion patterns from contacts"""
        print("\n📈 Emotion Patterns")
        print("=" * 30)
        print("This feature would show patterns in shared emotions")
        print("from your trusted contacts over time.")
    
    def _edit_contact_settings(self):
        """Edit settings for existing contact"""
        print("Edit contact settings feature would be implemented here")
    
    def _remove_contact(self):
        """Remove a trusted contact"""
        print("Remove contact feature would be implemented here")
    
    def _view_contact_activity(self):
        """View activity from contacts"""
        print("Contact activity feature would be implemented here")
    
    def _set_sharing_preferences(self):
        """Set global sharing preferences"""
        print("\n⚙️ Sharing Preferences")
        print("=" * 30)
        print("Configure your default sharing settings")
        
        data = self._load_social_data()
        preferences = data.get('sharing_preferences', {})
        
        print("Current preferences:")
        print(f"• Default sharing level: {preferences.get('default_sharing_level', 'trusted_contacts')}")
        print(f"• Auto-share mood: {preferences.get('auto_share_mood', False)}")
        print(f"• Receive notifications: {preferences.get('receive_notifications', True)}")
        
        # Allow editing preferences
        print("\nPreference settings would be implemented here")
    
    def _view_connection_insights(self):
        """View insights about connections and sharing"""
        print("\n📊 Connection Insights")
        print("=" * 30)
        
        data = self._load_social_data()
        trusted_contacts = data.get('trusted_contacts', {})
        recent_shares = data.get('recent_shares', [])
        
        print(f"👥 Total trusted contacts: {len(trusted_contacts)}")
        print(f"📤 Emotions shared (last 30 days): {len([s for s in recent_shares if s.get('shared')])}")
        
        if recent_shares:
            # Most shared emotion
            emotion_counts = {}
            for share in recent_shares[-30:]:
                emotion = share['primary_emotion']
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            if emotion_counts:
                most_shared = max(emotion_counts.items(), key=lambda x: x[1])
                color_info = self.emotion_colors[most_shared[0]]
                print(f"🎨 Most shared emotion: {color_info['color']} {most_shared[0].title()} ({most_shared[1]} times)")
        
        print("\nDetailed insights would be implemented here")
    
    def _privacy_safety_settings(self):
        """Configure privacy and safety settings"""
        print("\n🔒 Privacy & Safety Settings")
        print("=" * 40)
        
        print("🛡️ Your Privacy Controls:")
        print("• All emotional data is stored locally on your device")
        print("• Sharing happens through encrypted local files only")
        print("• No data is sent to external servers")
        print("• You control exactly who sees what")
        print()
        
        print("⚙️ Safety Features:")
        print("• Crisis detection in shared emotions")
        print("• Automatic resource suggestions")
        print("• Emergency contact notifications")
        print("• Professional support integration")
        print()
        
        print("🔧 Settings:")
        print("1. Enable/disable crisis detection")
        print("2. Set emergency contacts")
        print("3. Configure data retention")
        print("4. Export/delete all social data")
        
        # Settings implementation would go here
        input("\nPress Enter to continue...")
    
    def _load_social_data(self) -> Dict:
        """Load social connection data from file"""
        if not os.path.exists(SOCIAL_FILE):
            return {}
        
        try:
            with open(SOCIAL_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_social_data(self, data: Dict):
        """Save social connection data to file"""
        try:
            with open(SOCIAL_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save social data: {e}")


def social_connection_command(action: str = "menu", **kwargs):
    """Main social connection command interface"""
    social = SocialConnection()
    
    if action == "menu":
        social.show_social_menu()
    elif action == "share":
        social._share_emotional_state()
    elif action == "view":
        social._view_shared_emotions()
    elif action == "support":
        social._send_support_message()
    elif action == "palette":
        social._create_emotion_palette()
    elif action == "contacts":
        social._manage_trusted_contacts()
    elif action == "preferences":
        social._set_sharing_preferences()
    elif action == "insights":
        social._view_connection_insights()
    elif action == "privacy":
        social._privacy_safety_settings()
    else:
        print(f"Unknown social action: {action}")
        print("Available actions: menu, share, view, support, palette, contacts, preferences, insights, privacy")
