"""
Learning Paths module for om - inspired by Intellect app
Structured CBT programs for common mental health challenges
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

LEARNING_PATHS_FILE = os.path.expanduser("~/.om_learning_paths.json")

class LearningPaths:
    def __init__(self):
        self.paths = {
            "managing_emotions": {
                "title": "Managing Your Emotions",
                "description": "Learn to understand, accept, and regulate your emotions effectively",
                "duration": "7 sessions",
                "difficulty": "Beginner",
                "sessions": [
                    {
                        "id": 1,
                        "title": "Understanding Emotions",
                        "description": "Learn what emotions are and why we have them",
                        "duration": "10 minutes",
                        "content": "emotions_basics",
                        "tasks": ["emotion_wheel_exercise", "daily_emotion_check"]
                    },
                    {
                        "id": 2,
                        "title": "The Emotion-Thought Connection",
                        "description": "Discover how thoughts influence feelings",
                        "duration": "12 minutes",
                        "content": "thought_emotion_link",
                        "tasks": ["thought_record", "emotion_trigger_identification"]
                    },
                    {
                        "id": 3,
                        "title": "Emotional Awareness",
                        "description": "Practice mindful awareness of your emotional states",
                        "duration": "15 minutes",
                        "content": "emotional_mindfulness",
                        "tasks": ["body_scan_emotions", "emotion_labeling_practice"]
                    },
                    {
                        "id": 4,
                        "title": "Acceptance vs. Resistance",
                        "description": "Learn when to accept emotions and when to change them",
                        "duration": "12 minutes",
                        "content": "emotional_acceptance",
                        "tasks": ["acceptance_meditation", "emotion_surfing"]
                    },
                    {
                        "id": 5,
                        "title": "Healthy Expression",
                        "description": "Find healthy ways to express and communicate emotions",
                        "duration": "14 minutes",
                        "content": "emotion_expression",
                        "tasks": ["assertive_communication", "creative_expression"]
                    },
                    {
                        "id": 6,
                        "title": "Regulation Strategies",
                        "description": "Build your toolkit of emotion regulation techniques",
                        "duration": "16 minutes",
                        "content": "regulation_techniques",
                        "tasks": ["breathing_for_regulation", "cognitive_reappraisal"]
                    },
                    {
                        "id": 7,
                        "title": "Integration & Practice",
                        "description": "Put it all together and plan for ongoing practice",
                        "duration": "10 minutes",
                        "content": "integration_planning",
                        "tasks": ["personal_emotion_plan", "progress_reflection"]
                    }
                ]
            },
            "better_sleep": {
                "title": "Better Sleep Habits",
                "description": "Develop healthy sleep patterns and overcome insomnia",
                "duration": "6 sessions",
                "difficulty": "Beginner",
                "sessions": [
                    {
                        "id": 1,
                        "title": "Understanding Sleep",
                        "description": "Learn about sleep cycles and what affects sleep quality",
                        "duration": "8 minutes",
                        "content": "sleep_science",
                        "tasks": ["sleep_diary_start", "sleep_assessment"]
                    },
                    {
                        "id": 2,
                        "title": "Sleep Hygiene Basics",
                        "description": "Essential habits for better sleep",
                        "duration": "12 minutes",
                        "content": "sleep_hygiene",
                        "tasks": ["bedroom_audit", "sleep_schedule_planning"]
                    },
                    {
                        "id": 3,
                        "title": "Managing Racing Thoughts",
                        "description": "Techniques for quieting the mind at bedtime",
                        "duration": "15 minutes",
                        "content": "bedtime_thoughts",
                        "tasks": ["worry_time", "thought_parking"]
                    },
                    {
                        "id": 4,
                        "title": "Relaxation for Sleep",
                        "description": "Body and mind relaxation techniques",
                        "duration": "18 minutes",
                        "content": "sleep_relaxation",
                        "tasks": ["progressive_relaxation", "sleep_meditation"]
                    },
                    {
                        "id": 5,
                        "title": "Dealing with Sleep Anxiety",
                        "description": "Overcome anxiety about not sleeping",
                        "duration": "14 minutes",
                        "content": "sleep_anxiety",
                        "tasks": ["sleep_restriction", "anxiety_challenging"]
                    },
                    {
                        "id": 6,
                        "title": "Maintaining Good Sleep",
                        "description": "Long-term strategies for consistent sleep",
                        "duration": "10 minutes",
                        "content": "sleep_maintenance",
                        "tasks": ["sleep_plan_creation", "relapse_prevention"]
                    }
                ]
            },
            "anxiety_management": {
                "title": "Managing Anxiety",
                "description": "Evidence-based techniques to reduce anxiety and worry",
                "duration": "8 sessions",
                "difficulty": "Intermediate",
                "sessions": [
                    {
                        "id": 1,
                        "title": "Understanding Anxiety",
                        "description": "Learn about anxiety, its purpose, and when it becomes problematic",
                        "duration": "10 minutes",
                        "content": "anxiety_basics",
                        "tasks": ["anxiety_self_assessment", "trigger_identification"]
                    },
                    {
                        "id": 2,
                        "title": "The Anxiety Cycle",
                        "description": "How thoughts, feelings, and behaviors maintain anxiety",
                        "duration": "12 minutes",
                        "content": "anxiety_cycle",
                        "tasks": ["cycle_mapping", "pattern_recognition"]
                    },
                    {
                        "id": 3,
                        "title": "Breathing and Grounding",
                        "description": "Immediate techniques for anxiety relief",
                        "duration": "15 minutes",
                        "content": "anxiety_relief",
                        "tasks": ["breathing_practice", "grounding_techniques"]
                    },
                    {
                        "id": 4,
                        "title": "Challenging Anxious Thoughts",
                        "description": "Cognitive techniques to question worry thoughts",
                        "duration": "16 minutes",
                        "content": "thought_challenging",
                        "tasks": ["thought_records", "evidence_examination"]
                    },
                    {
                        "id": 5,
                        "title": "Facing Your Fears",
                        "description": "Introduction to gradual exposure",
                        "duration": "14 minutes",
                        "content": "exposure_basics",
                        "tasks": ["fear_hierarchy", "first_exposure"]
                    },
                    {
                        "id": 6,
                        "title": "Worry Time Technique",
                        "description": "Contain worry to specific times",
                        "duration": "12 minutes",
                        "content": "worry_management",
                        "tasks": ["worry_scheduling", "worry_evaluation"]
                    },
                    {
                        "id": 7,
                        "title": "Building Confidence",
                        "description": "Develop self-efficacy and resilience",
                        "duration": "14 minutes",
                        "content": "confidence_building",
                        "tasks": ["strength_identification", "success_planning"]
                    },
                    {
                        "id": 8,
                        "title": "Maintaining Progress",
                        "description": "Long-term strategies for managing anxiety",
                        "duration": "10 minutes",
                        "content": "anxiety_maintenance",
                        "tasks": ["relapse_plan", "ongoing_practice"]
                    }
                ]
            },
            "stress_management": {
                "title": "Stress Management",
                "description": "Learn to identify, manage, and reduce stress in daily life",
                "duration": "6 sessions",
                "difficulty": "Beginner",
                "sessions": [
                    {
                        "id": 1,
                        "title": "Understanding Stress",
                        "description": "What stress is and how it affects you",
                        "duration": "8 minutes",
                        "content": "stress_basics",
                        "tasks": ["stress_assessment", "stress_diary"]
                    },
                    {
                        "id": 2,
                        "title": "Stress Triggers",
                        "description": "Identify your personal stress triggers",
                        "duration": "10 minutes",
                        "content": "stress_triggers",
                        "tasks": ["trigger_mapping", "stress_log"]
                    },
                    {
                        "id": 3,
                        "title": "Quick Stress Relief",
                        "description": "Immediate techniques for stress relief",
                        "duration": "12 minutes",
                        "content": "immediate_relief",
                        "tasks": ["breathing_techniques", "quick_relaxation"]
                    },
                    {
                        "id": 4,
                        "title": "Problem-Solving Skills",
                        "description": "Tackle stress at its source",
                        "duration": "15 minutes",
                        "content": "problem_solving",
                        "tasks": ["problem_analysis", "solution_brainstorming"]
                    },
                    {
                        "id": 5,
                        "title": "Building Resilience",
                        "description": "Develop your ability to bounce back",
                        "duration": "14 minutes",
                        "content": "resilience_building",
                        "tasks": ["strength_building", "support_network"]
                    },
                    {
                        "id": 6,
                        "title": "Stress Prevention",
                        "description": "Long-term strategies to prevent stress",
                        "duration": "12 minutes",
                        "content": "stress_prevention",
                        "tasks": ["lifestyle_planning", "boundary_setting"]
                    }
                ]
            },
            "relationship_skills": {
                "title": "Relationship Skills",
                "description": "Improve communication and build healthier relationships",
                "duration": "7 sessions",
                "difficulty": "Intermediate",
                "sessions": [
                    {
                        "id": 1,
                        "title": "Understanding Relationships",
                        "description": "The foundation of healthy relationships",
                        "duration": "10 minutes",
                        "content": "relationship_basics",
                        "tasks": ["relationship_assessment", "values_clarification"]
                    },
                    {
                        "id": 2,
                        "title": "Communication Basics",
                        "description": "Essential communication skills",
                        "duration": "12 minutes",
                        "content": "communication_skills",
                        "tasks": ["active_listening", "i_statements"]
                    },
                    {
                        "id": 3,
                        "title": "Managing Conflict",
                        "description": "Healthy ways to handle disagreements",
                        "duration": "15 minutes",
                        "content": "conflict_resolution",
                        "tasks": ["conflict_analysis", "resolution_practice"]
                    },
                    {
                        "id": 4,
                        "title": "Setting Boundaries",
                        "description": "Learn to set and maintain healthy boundaries",
                        "duration": "14 minutes",
                        "content": "boundary_setting",
                        "tasks": ["boundary_identification", "assertiveness_practice"]
                    },
                    {
                        "id": 5,
                        "title": "Building Empathy",
                        "description": "Understand and connect with others",
                        "duration": "12 minutes",
                        "content": "empathy_building",
                        "tasks": ["perspective_taking", "empathy_practice"]
                    },
                    {
                        "id": 6,
                        "title": "Trust and Intimacy",
                        "description": "Deepen connections with others",
                        "duration": "14 minutes",
                        "content": "trust_building",
                        "tasks": ["trust_exercises", "vulnerability_practice"]
                    },
                    {
                        "id": 7,
                        "title": "Maintaining Relationships",
                        "description": "Long-term relationship maintenance",
                        "duration": "10 minutes",
                        "content": "relationship_maintenance",
                        "tasks": ["relationship_planning", "ongoing_practice"]
                    }
                ]
            }
        }
    
    def list_paths(self):
        """Display available learning paths"""
        print("📚 Available Learning Paths")
        print("=" * 50)
        print("Choose a structured program to work through specific challenges:")
        print()
        
        for i, (path_id, path_info) in enumerate(self.paths.items(), 1):
            difficulty_emoji = {"Beginner": "🟢", "Intermediate": "🟡", "Advanced": "🔴"}
            emoji = difficulty_emoji.get(path_info["difficulty"], "🟢")
            
            print(f"{i}. {emoji} {path_info['title']}")
            print(f"   {path_info['description']}")
            print(f"   Duration: {path_info['duration']} | Difficulty: {path_info['difficulty']}")
            print()
        
        # Show user progress
        progress_data = self._load_progress_data()
        if progress_data:
            print("📈 Your Progress:")
            for path_id, path_progress in progress_data.items():
                if path_id in self.paths:
                    path_title = self.paths[path_id]["title"]
                    completed_sessions = len([s for s in path_progress.get("sessions", {}).values() if s.get("completed")])
                    total_sessions = len(self.paths[path_id]["sessions"])
                    progress_percent = (completed_sessions / total_sessions) * 100
                    
                    print(f"   {path_title}: {completed_sessions}/{total_sessions} sessions ({progress_percent:.0f}%)")
            print()
        
        # Let user choose a path
        choice = input("Choose a learning path (1-5) or press Enter to return: ").strip()
        
        if choice.isdigit():
            try:
                choice_idx = int(choice) - 1
                path_ids = list(self.paths.keys())
                if 0 <= choice_idx < len(path_ids):
                    self.start_path(path_ids[choice_idx])
            except ValueError:
                pass
    
    def start_path(self, path_id: str):
        """Start or continue a learning path"""
        if path_id not in self.paths:
            print(f"Learning path '{path_id}' not found.")
            return
        
        path_info = self.paths[path_id]
        progress_data = self._load_progress_data()
        path_progress = progress_data.get(path_id, {"sessions": {}, "started": False})
        
        print(f"\n📖 {path_info['title']}")
        print("=" * 60)
        print(f"{path_info['description']}")
        print(f"Duration: {path_info['duration']} | Difficulty: {path_info['difficulty']}")
        print()
        
        if not path_progress["started"]:
            print("🌟 Welcome to your learning journey!")
            print("This path is designed to be completed over several days or weeks.")
            print("Take your time with each session and practice the exercises.")
            print()
            
            start_confirm = input("Ready to start? (y/n): ").strip().lower()
            if start_confirm != 'y':
                return
            
            path_progress["started"] = True
            path_progress["start_date"] = datetime.now().isoformat()
        
        # Show session menu
        self._show_session_menu(path_id, path_info, path_progress)
        
        # Save progress
        progress_data[path_id] = path_progress
        self._save_progress_data(progress_data)
    
    def _show_session_menu(self, path_id: str, path_info: Dict, path_progress: Dict):
        """Show sessions in a learning path"""
        print("📋 Sessions:")
        
        for session in path_info["sessions"]:
            session_id = session["id"]
            session_progress = path_progress["sessions"].get(str(session_id), {})
            
            # Status indicators
            if session_progress.get("completed"):
                status = "✅"
            elif session_progress.get("started"):
                status = "🔄"
            else:
                status = "⭕"
            
            print(f"{status} Session {session_id}: {session['title']}")
            print(f"    {session['description']} ({session['duration']})")
        
        print()
        
        # Find next session
        next_session = None
        for session in path_info["sessions"]:
            session_id = str(session["id"])
            if not path_progress["sessions"].get(session_id, {}).get("completed"):
                next_session = session
                break
        
        if next_session:
            print(f"🎯 Next: Session {next_session['id']} - {next_session['title']}")
            start_next = input("Start this session? (y/n): ").strip().lower()
            
            if start_next == 'y':
                self._start_session(path_id, next_session, path_progress)
        else:
            print("🎉 Congratulations! You've completed this learning path!")
            self._show_path_completion(path_id, path_info)
    
    def _start_session(self, path_id: str, session: Dict, path_progress: Dict):
        """Start a learning session"""
        session_id = str(session["id"])
        
        print(f"\n📖 Session {session['id']}: {session['title']}")
        print("=" * 50)
        print(f"{session['description']}")
        print(f"Estimated time: {session['duration']}")
        print()
        
        # Mark session as started
        if session_id not in path_progress["sessions"]:
            path_progress["sessions"][session_id] = {}
        
        path_progress["sessions"][session_id]["started"] = True
        path_progress["sessions"][session_id]["start_time"] = datetime.now().isoformat()
        
        # Deliver session content
        self._deliver_session_content(session)
        
        # Session tasks
        if session.get("tasks"):
            print("\n📝 Practice Tasks:")
            print("Complete these tasks to reinforce your learning:")
            
            for i, task in enumerate(session["tasks"], 1):
                task_name = task.replace("_", " ").title()
                print(f"{i}. {task_name}")
            
            print()
            print("💡 Take your time with these tasks. They're designed to help you")
            print("   apply what you've learned in real situations.")
        
        # Session completion
        print("\n" + "="*50)
        completed = input("Have you completed this session? (y/n): ").strip().lower()
        
        if completed == 'y':
            path_progress["sessions"][session_id]["completed"] = True
            path_progress["sessions"][session_id]["completion_time"] = datetime.now().isoformat()
            
            # Session reflection
            reflection = input("What's one key insight from this session? (optional): ").strip()
            if reflection:
                path_progress["sessions"][session_id]["reflection"] = reflection
            
            print("✅ Session completed! Great work on your mental health journey.")
            
            # Check if path is complete
            completed_sessions = len([s for s in path_progress["sessions"].values() if s.get("completed")])
            total_sessions = len(self.paths[path_id]["sessions"])
            
            if completed_sessions == total_sessions:
                print("\n🎉 Congratulations! You've completed the entire learning path!")
                path_progress["completed"] = True
                path_progress["completion_date"] = datetime.now().isoformat()
        else:
            print("That's okay! You can continue this session anytime.")
            print("Remember: learning is a process, not a race.")
    
    def _deliver_session_content(self, session: Dict):
        """Deliver the main content of a session"""
        content_type = session.get("content", "")
        
        # This is a simplified content delivery
        # In a full implementation, you'd have rich content for each session
        
        content_library = {
            "emotions_basics": """
🧠 Understanding Emotions

Emotions are natural responses to situations that help us navigate life.
They provide important information about our needs, values, and environment.

Key Points:
• Emotions are neither good nor bad - they're information
• All emotions serve a purpose, even uncomfortable ones
• Emotions are temporary - they come and go like waves
• We can learn to observe emotions without being overwhelmed by them

Common emotions and their messages:
• Anger: Something important to you is being threatened
• Sadness: You've experienced a loss or disappointment  
• Fear: You perceive danger or threat
• Joy: Your needs or values are being met
• Guilt: You may have acted against your values
• Shame: You feel fundamentally flawed (often inaccurate)

Remember: You are not your emotions. You are the observer of your emotions.
            """,
            
            "sleep_science": """
😴 Understanding Sleep

Sleep is essential for physical health, mental wellbeing, and cognitive function.
Understanding how sleep works can help you improve your sleep quality.

Sleep Stages:
• Light Sleep (Stage 1-2): Transition into sleep, easy to wake
• Deep Sleep (Stage 3): Physical restoration, hard to wake
• REM Sleep: Dreams, memory consolidation, emotional processing

Sleep Cycles:
• Complete cycle: ~90 minutes
• 4-6 cycles per night for adults
• Each stage serves important functions

What Affects Sleep:
• Circadian rhythm (internal body clock)
• Light exposure (especially blue light)
• Temperature (cooler is better)
• Caffeine, alcohol, and medications
• Stress and anxiety
• Physical activity and timing
• Bedroom environment

Good sleep isn't luxury - it's essential for mental health.
            """,
            
            "anxiety_basics": """
😰 Understanding Anxiety

Anxiety is a normal emotion that becomes problematic when it's excessive,
persistent, or interferes with daily life.

Normal vs. Problematic Anxiety:
• Normal: Helps you prepare for challenges, motivates action
• Problematic: Excessive worry, avoidance, physical symptoms

The Anxiety Response:
• Fight/Flight/Freeze: Ancient survival mechanism
• Physical symptoms: Racing heart, sweating, muscle tension
• Mental symptoms: Racing thoughts, catastrophizing, difficulty concentrating
• Behavioral symptoms: Avoidance, restlessness, seeking reassurance

Common Anxiety Triggers:
• Uncertainty and unpredictability
• Perceived threats (real or imagined)
• Past traumatic experiences
• Major life changes
• Health concerns
• Social situations

Remember: Anxiety is treatable. You can learn to manage it effectively.
            """
        }
        
        content = content_library.get(content_type, f"Content for {content_type} would be delivered here.")
        print(content)
        
        input("\nPress Enter to continue...")
    
    def _show_path_completion(self, path_id: str, path_info: Dict):
        """Show completion celebration and next steps"""
        print("\n🎉 Path Completion Celebration!")
        print("=" * 40)
        print(f"You've successfully completed: {path_info['title']}")
        print()
        print("🌟 What you've accomplished:")
        print(f"• Completed {len(path_info['sessions'])} structured sessions")
        print("• Learned evidence-based techniques")
        print("• Practiced new skills and strategies")
        print("• Invested in your mental health and wellbeing")
        print()
        print("🚀 Next Steps:")
        print("• Continue practicing the techniques you've learned")
        print("• Consider starting another learning path")
        print("• Use the rescue sessions when you need quick support")
        print("• Track your mood to see your progress over time")
        print()
        
        # Suggest related paths
        related_paths = {
            "managing_emotions": ["anxiety_management", "stress_management"],
            "better_sleep": ["stress_management", "anxiety_management"],
            "anxiety_management": ["managing_emotions", "stress_management"],
            "stress_management": ["managing_emotions", "relationship_skills"],
            "relationship_skills": ["managing_emotions", "stress_management"]
        }
        
        if path_id in related_paths:
            print("📚 You might also be interested in:")
            for related_id in related_paths[path_id]:
                if related_id in self.paths:
                    related_title = self.paths[related_id]["title"]
                    print(f"• {related_title}")
    
    def show_progress(self):
        """Show overall learning progress"""
        progress_data = self._load_progress_data()
        
        if not progress_data:
            print("📊 Learning Progress")
            print("=" * 30)
            print("You haven't started any learning paths yet.")
            print("Use 'om learn' to see available paths and get started!")
            return
        
        print("📊 Your Learning Journey")
        print("=" * 40)
        
        total_paths = len(self.paths)
        started_paths = len(progress_data)
        completed_paths = len([p for p in progress_data.values() if p.get("completed")])
        
        print(f"Paths started: {started_paths}/{total_paths}")
        print(f"Paths completed: {completed_paths}/{total_paths}")
        print()
        
        for path_id, path_progress in progress_data.items():
            if path_id in self.paths:
                path_info = self.paths[path_id]
                
                # Calculate progress
                completed_sessions = len([s for s in path_progress.get("sessions", {}).values() if s.get("completed")])
                total_sessions = len(path_info["sessions"])
                progress_percent = (completed_sessions / total_sessions) * 100
                
                # Status
                if path_progress.get("completed"):
                    status = "✅ Completed"
                elif completed_sessions > 0:
                    status = f"🔄 In Progress ({progress_percent:.0f}%)"
                else:
                    status = "⭕ Started"
                
                print(f"{status} {path_info['title']}")
                print(f"   Sessions: {completed_sessions}/{total_sessions}")
                
                if path_progress.get("start_date"):
                    start_date = datetime.fromisoformat(path_progress["start_date"]).strftime("%Y-%m-%d")
                    print(f"   Started: {start_date}")
                
                if path_progress.get("completion_date"):
                    completion_date = datetime.fromisoformat(path_progress["completion_date"]).strftime("%Y-%m-%d")
                    print(f"   Completed: {completion_date}")
                
                print()
        
        # Learning streak
        streak = self._calculate_learning_streak(progress_data)
        if streak > 0:
            print(f"🔥 Learning streak: {streak} days")
        
        print("💡 Keep up the great work on your mental health journey!")
    
    def _calculate_learning_streak(self, progress_data: Dict) -> int:
        """Calculate current learning streak"""
        # Simplified streak calculation
        # In a full implementation, you'd track daily session completions
        
        all_completions = []
        for path_progress in progress_data.values():
            for session_progress in path_progress.get("sessions", {}).values():
                if session_progress.get("completion_time"):
                    completion_date = datetime.fromisoformat(session_progress["completion_time"]).date()
                    all_completions.append(completion_date)
        
        if not all_completions:
            return 0
        
        # Sort completions and find consecutive days
        unique_dates = sorted(set(all_completions), reverse=True)
        
        streak = 0
        current_date = datetime.now().date()
        
        for completion_date in unique_dates:
            if completion_date == current_date or completion_date == current_date - timedelta(days=streak):
                streak += 1
                current_date = completion_date
            else:
                break
        
        return streak
    
    def _load_progress_data(self) -> Dict:
        """Load learning progress data"""
        if not os.path.exists(LEARNING_PATHS_FILE):
            return {}
        
        try:
            with open(LEARNING_PATHS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_progress_data(self, data: Dict):
        """Save learning progress data"""
        try:
            with open(LEARNING_PATHS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save learning progress: {e}")


def learning_paths_command(action: str = "list", **kwargs):
    """Main learning paths command interface"""
    paths = LearningPaths()
    
    if action == "list":
        paths.list_paths()
    elif action == "start":
        path_id = kwargs.get('path')
        if path_id:
            paths.start_path(path_id)
        else:
            print("Please specify a path to start")
    elif action == "progress":
        paths.show_progress()
    else:
        print(f"Unknown learning paths action: {action}")
        print("Available actions: list, start, progress")
