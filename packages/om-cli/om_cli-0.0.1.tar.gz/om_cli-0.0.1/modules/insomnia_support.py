"""
Insomnia symptoms support module for om
Evidence-based tools for improving sleep quality
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional

SLEEP_FILE = os.path.expanduser("~/.om_sleep.json")

class InsomniaSupport:
    def __init__(self):
        self.sleep_hygiene_tips = {
            "bedroom_environment": [
                "Keep bedroom cool (60-67°F/15-19°C)",
                "Make room as dark as possible",
                "Minimize noise or use white noise",
                "Use comfortable mattress and pillows",
                "Reserve bed for sleep and intimacy only"
            ],
            "daily_habits": [
                "Maintain consistent sleep/wake times",
                "Get morning sunlight exposure",
                "Exercise regularly (but not close to bedtime)",
                "Limit daytime naps to 20-30 minutes",
                "Avoid large meals close to bedtime"
            ],
            "substances": [
                "Limit caffeine after 2 PM",
                "Avoid alcohol close to bedtime",
                "Don't smoke, especially in evening",
                "Be cautious with sleep medications",
                "Stay hydrated but limit fluids before bed"
            ],
            "evening_routine": [
                "Start winding down 1-2 hours before bed",
                "Dim lights in the evening",
                "Avoid screens 1 hour before bed",
                "Try relaxing activities (reading, bath, meditation)",
                "Keep a consistent bedtime routine"
            ]
        }
        
        self.relaxation_techniques = {
            "progressive_muscle": "Progressive muscle relaxation",
            "breathing": "Deep breathing exercises", 
            "visualization": "Guided imagery/visualization",
            "body_scan": "Body scan meditation",
            "counting": "Counting techniques",
            "mindfulness": "Mindfulness meditation"
        }
    
    def sleep_assessment(self):
        """Comprehensive sleep assessment"""
        print("😴 Sleep Assessment")
        print("=" * 40)
        print("Let's assess your sleep patterns and identify areas for improvement.")
        print()
        
        # Basic sleep metrics
        bedtime = input("What time do you usually go to bed? ").strip()
        sleep_time = input("How long does it take you to fall asleep? (minutes): ").strip()
        wake_time = input("What time do you usually wake up? ").strip()
        sleep_quality = input("Rate your sleep quality (1-10, 10=excellent): ").strip()
        
        try:
            sleep_time = int(sleep_time)
            sleep_quality = max(1, min(10, int(sleep_quality)))
        except ValueError:
            sleep_time = 30
            sleep_quality = 5
        
        # Sleep problems
        print("\nWhich sleep problems do you experience? (y/n for each)")
        problems = {}
        sleep_issues = [
            ("difficulty_falling_asleep", "Difficulty falling asleep"),
            ("frequent_waking", "Waking up frequently during the night"),
            ("early_waking", "Waking up too early and can't get back to sleep"),
            ("unrefreshing_sleep", "Sleep doesn't feel refreshing"),
            ("daytime_fatigue", "Feeling tired during the day"),
            ("mood_effects", "Sleep problems affecting your mood"),
            ("concentration_issues", "Difficulty concentrating due to poor sleep")
        ]
        
        for key, description in sleep_issues:
            response = input(f"   {description}? (y/n): ").strip().lower()
            problems[key] = response == 'y'
        
        # Sleep hygiene assessment
        print("\nSleep Hygiene Check:")
        hygiene_score = 0
        hygiene_issues = []
        
        hygiene_questions = [
            ("Do you go to bed and wake up at the same time every day?", "consistent_schedule"),
            ("Is your bedroom cool, dark, and quiet?", "bedroom_environment"),
            ("Do you avoid screens for 1 hour before bed?", "screen_avoidance"),
            ("Do you avoid caffeine after 2 PM?", "caffeine_timing"),
            ("Do you have a relaxing bedtime routine?", "bedtime_routine"),
            ("Do you only use your bed for sleep?", "bed_association"),
            ("Do you avoid long daytime naps?", "nap_control"),
            ("Do you get regular exercise (not close to bedtime)?", "exercise_timing")
        ]
        
        for question, key in hygiene_questions:
            response = input(f"   {question} (y/n): ").strip().lower()
            if response == 'y':
                hygiene_score += 1
            else:
                hygiene_issues.append(key)
        
        # Results
        print(f"\n📊 Sleep Assessment Results:")
        print(f"   Bedtime: {bedtime}")
        print(f"   Time to fall asleep: {sleep_time} minutes")
        print(f"   Wake time: {wake_time}")
        print(f"   Sleep quality: {sleep_quality}/10")
        print(f"   Sleep hygiene score: {hygiene_score}/8")
        
        # Identify main issues
        main_issues = [desc for key, desc in sleep_issues if problems[key]]
        if main_issues:
            print(f"\n🎯 Main sleep issues:")
            for issue in main_issues:
                print(f"   • {issue}")
        
        # Recommendations
        self._provide_sleep_recommendations(sleep_time, sleep_quality, hygiene_score, 
                                          problems, hygiene_issues)
        
        # Save assessment
        self._save_sleep_assessment(bedtime, sleep_time, wake_time, sleep_quality,
                                  problems, hygiene_score, hygiene_issues)
    
    def sleep_hygiene_education(self):
        """Comprehensive sleep hygiene education"""
        print("🛏️ Sleep Hygiene Education")
        print("=" * 40)
        print("Good sleep hygiene forms the foundation of healthy sleep.")
        print("Let's review the key areas:")
        print()
        
        for category, tips in self.sleep_hygiene_tips.items():
            print(f"🔹 {category.replace('_', ' ').title()}:")
            for tip in tips:
                print(f"   • {tip}")
            print()
        
        # Interactive hygiene planner
        print("Let's create your personalized sleep hygiene plan:")
        print()
        
        improvements = []
        for category, tips in self.sleep_hygiene_tips.items():
            print(f"📋 {category.replace('_', ' ').title()}:")
            print("Which of these could you improve?")
            
            for i, tip in enumerate(tips, 1):
                print(f"   {i}. {tip}")
            
            choices = input("Enter numbers of areas to improve (e.g., 1,3,5): ").strip()
            
            if choices:
                try:
                    selected = [int(x.strip()) for x in choices.split(',')]
                    for choice in selected:
                        if 1 <= choice <= len(tips):
                            improvements.append(tips[choice - 1])
                except ValueError:
                    pass
            print()
        
        if improvements:
            print("🎯 Your Sleep Hygiene Improvement Plan:")
            for i, improvement in enumerate(improvements, 1):
                print(f"   {i}. {improvement}")
            
            print("\n💡 Implementation Tips:")
            print("• Start with 1-2 changes at a time")
            print("• Be consistent for at least 2 weeks")
            print("• Track your progress")
            print("• Be patient - sleep improvements take time")
            
            # Save improvement plan
            self._save_hygiene_plan(improvements)
    
    def bedtime_routine_builder(self):
        """Help create a personalized bedtime routine"""
        print("🌙 Bedtime Routine Builder")
        print("=" * 40)
        print("A consistent bedtime routine signals to your body that it's time to sleep.")
        print("Let's create your personalized routine.")
        print()
        
        # Determine routine timing
        bedtime = input("What time do you want to go to bed? ").strip()
        routine_start = input("How long before bedtime should your routine start? (minutes): ").strip()
        
        try:
            routine_duration = int(routine_start)
        except ValueError:
            routine_duration = 60
        
        print(f"\nYour routine will start {routine_duration} minutes before {bedtime}")
        print()
        
        # Activity categories
        activity_options = {
            "relaxation": [
                "Take a warm bath or shower",
                "Practice deep breathing",
                "Do gentle stretching or yoga",
                "Listen to calming music",
                "Practice meditation",
                "Progressive muscle relaxation"
            ],
            "preparation": [
                "Prepare clothes for tomorrow",
                "Set out items needed for morning",
                "Do light tidying",
                "Check doors and locks",
                "Set phone to do not disturb",
                "Dim the lights"
            ],
            "mental": [
                "Write in a journal",
                "Read a book (not on screen)",
                "Practice gratitude",
                "Review the day's positives",
                "Do a brain dump of tomorrow's tasks",
                "Listen to a podcast or audiobook"
            ],
            "physical": [
                "Gentle skincare routine",
                "Brush teeth",
                "Change into comfortable sleepwear",
                "Apply lotion or essential oils",
                "Do neck and shoulder stretches",
                "Practice good posture"
            ]
        }
        
        # Build routine
        routine_activities = []
        total_time = 0
        
        print("Choose activities for your routine:")
        print("(We'll aim for activities that total about {routine_duration} minutes)")
        print()
        
        for category, activities in activity_options.items():
            print(f"🔹 {category.title()} Activities:")
            for i, activity in enumerate(activities, 1):
                print(f"   {i}. {activity}")
            
            choices = input("Choose activities (e.g., 1,3,5) or press Enter to skip: ").strip()
            
            if choices:
                try:
                    selected = [int(x.strip()) for x in choices.split(',')]
                    for choice in selected:
                        if 1 <= choice <= len(activities):
                            activity = activities[choice - 1]
                            duration = input(f"How many minutes for '{activity}'? ").strip()
                            
                            try:
                                duration = int(duration)
                                routine_activities.append({
                                    "activity": activity,
                                    "duration": duration,
                                    "category": category
                                })
                                total_time += duration
                            except ValueError:
                                routine_activities.append({
                                    "activity": activity,
                                    "duration": 10,
                                    "category": category
                                })
                                total_time += 10
                except ValueError:
                    pass
            print()
        
        # Display routine
        if routine_activities:
            print("🌙 Your Personalized Bedtime Routine:")
            print(f"Total time: {total_time} minutes")
            print()
            
            # Sort by category for logical flow
            category_order = ["preparation", "physical", "mental", "relaxation"]
            sorted_activities = []
            
            for category in category_order:
                category_activities = [a for a in routine_activities if a["category"] == category]
                sorted_activities.extend(category_activities)
            
            for i, activity in enumerate(sorted_activities, 1):
                print(f"{i}. {activity['activity']} ({activity['duration']} min)")
            
            print(f"\n⏰ Start your routine at: {routine_duration} minutes before {bedtime}")
            
            print("\n💡 Routine Tips:")
            print("• Be consistent - do this every night")
            print("• Adjust timing as needed")
            print("• Make it enjoyable, not a chore")
            print("• Turn off screens during routine")
            print("• Keep the routine even on weekends")
            
            # Save routine
            self._save_bedtime_routine(routine_activities, bedtime, routine_duration)
        else:
            print("No routine activities selected.")
    
    def sleep_relaxation_techniques(self):
        """Guided sleep relaxation techniques"""
        print("😌 Sleep Relaxation Techniques")
        print("=" * 40)
        print("These techniques can help you relax and prepare for sleep.")
        print()
        
        print("Choose a relaxation technique:")
        techniques = list(self.relaxation_techniques.items())
        
        for i, (key, name) in enumerate(techniques, 1):
            print(f"{i}. {name}")
        
        print()
        choice = input("Choose technique (1-6): ").strip()
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(techniques):
                technique_key = techniques[choice_idx][0]
                self._perform_relaxation_technique(technique_key)
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid choice.")
    
    def _perform_relaxation_technique(self, technique: str):
        """Perform specific relaxation technique"""
        if technique == "progressive_muscle":
            self._progressive_muscle_for_sleep()
        elif technique == "breathing":
            self._sleep_breathing_exercise()
        elif technique == "visualization":
            self._sleep_visualization()
        elif technique == "body_scan":
            self._body_scan_for_sleep()
        elif technique == "counting":
            self._counting_techniques()
        elif technique == "mindfulness":
            self._mindfulness_for_sleep()
    
    def _progressive_muscle_for_sleep(self):
        """Progressive muscle relaxation for sleep"""
        print("\n💪 Progressive Muscle Relaxation for Sleep")
        print("=" * 50)
        print("This technique helps release physical tension before sleep.")
        print("Lie down comfortably and follow along.")
        print()
        
        input("Press Enter when you're lying down comfortably...")
        print()
        
        muscle_groups = [
            "Tense your toes and feet... hold for 5 seconds... now release and relax",
            "Tense your calf muscles... hold... now let them go completely",
            "Tense your thigh muscles... hold... now release all tension",
            "Tense your buttocks and hips... hold... now relax completely",
            "Tense your stomach muscles... hold... now let them soften",
            "Make fists and tense your arms... hold... now let your arms fall heavy",
            "Tense your shoulders up to your ears... hold... now let them drop",
            "Scrunch your face muscles... hold... now let your face go soft",
            "Tense your whole body... hold... now release everything and sink into relaxation"
        ]
        
        for instruction in muscle_groups:
            print(f"🎯 {instruction}")
            time.sleep(8)
            print("   Notice the contrast between tension and relaxation...")
            time.sleep(3)
            print()
        
        print("✨ Your body is now completely relaxed and ready for sleep.")
        print("Let this relaxation carry you into peaceful sleep.")
    
    def _sleep_breathing_exercise(self):
        """4-7-8 breathing for sleep"""
        print("\n🫁 4-7-8 Breathing for Sleep")
        print("=" * 40)
        print("This breathing pattern is specifically designed to promote sleep.")
        print("Breathe in for 4, hold for 7, exhale for 8.")
        print()
        
        input("Get comfortable and press Enter to begin...")
        print()
        
        for cycle in range(4):
            print(f"Cycle {cycle + 1}/4")
            
            print("Breathe in through your nose... 1...2...3...4")
            time.sleep(4)
            
            print("Hold your breath... 1...2...3...4...5...6...7")
            time.sleep(7)
            
            print("Exhale slowly through your mouth... 1...2...3...4...5...6...7...8")
            time.sleep(8)
            
            print("Rest and breathe naturally...")
            time.sleep(3)
            print()
        
        print("✨ Continue breathing naturally and let sleep come naturally.")
    
    def _sleep_visualization(self):
        """Guided sleep visualization"""
        print("\n🏞️ Sleep Visualization")
        print("=" * 30)
        print("Imagine a peaceful place where you can rest completely.")
        print()
        
        input("Close your eyes and press Enter...")
        print()
        
        prompts = [
            "Imagine you're in a peaceful, comfortable place... maybe a cozy bedroom, a quiet beach, or a serene forest...",
            "Notice the gentle sounds around you... perhaps soft waves, rustling leaves, or complete silence...",
            "Feel the perfect temperature on your skin... not too warm, not too cool... just right for rest...",
            "Notice how safe and secure you feel in this place... completely protected and at peace...",
            "Your body feels heavy and relaxed... sinking into the most comfortable surface...",
            "Your mind is quiet and calm... thoughts drift away like clouds in the sky...",
            "You feel deeply peaceful and ready for restorative sleep...",
            "Let this peaceful feeling carry you into deep, restful sleep..."
        ]
        
        for prompt in prompts:
            print(f"💭 {prompt}")
            time.sleep(10)
            print()
        
        print("✨ Rest in this peaceful place and let sleep come naturally.")
    
    def _provide_sleep_recommendations(self, sleep_time: int, sleep_quality: int,
                                     hygiene_score: int, problems: Dict, hygiene_issues: List):
        """Provide personalized sleep recommendations"""
        print(f"\n💡 Personalized Recommendations:")
        
        # Sleep onset issues
        if sleep_time > 30:
            print("   🎯 For difficulty falling asleep:")
            print("     • Try the 4-7-8 breathing technique")
            print("     • Practice progressive muscle relaxation")
            print("     • Consider the 'worry time' technique earlier in the day")
            print("     • Avoid screens 1-2 hours before bed")
        
        # Sleep quality issues
        if sleep_quality < 6:
            print("   🎯 For improving sleep quality:")
            print("     • Optimize your bedroom environment (cool, dark, quiet)")
            print("     • Maintain consistent sleep/wake times")
            print("     • Limit caffeine and alcohol")
            print("     • Consider if stress or anxiety are affecting sleep")
        
        # Sleep hygiene issues
        if hygiene_score < 6:
            print("   🎯 Priority sleep hygiene improvements:")
            if "consistent_schedule" in hygiene_issues:
                print("     • Establish consistent bedtime and wake time")
            if "bedroom_environment" in hygiene_issues:
                print("     • Optimize bedroom: cool, dark, quiet")
            if "screen_avoidance" in hygiene_issues:
                print("     • Avoid screens 1 hour before bed")
            if "bedtime_routine" in hygiene_issues:
                print("     • Create a relaxing bedtime routine")
        
        # Specific problem recommendations
        if problems.get("frequent_waking"):
            print("   🎯 For frequent night wakings:")
            print("     • Practice body scan meditation")
            print("     • Keep bedroom cool and comfortable")
            print("     • Avoid looking at the clock if you wake up")
        
        if problems.get("early_waking"):
            print("   🎯 For early morning awakening:")
            print("     • Ensure adequate light exposure during day")
            print("     • Consider if depression or anxiety might be factors")
            print("     • Avoid caffeine after 2 PM")
        
        if problems.get("daytime_fatigue"):
            print("   🎯 For daytime fatigue:")
            print("     • Maintain consistent sleep schedule")
            print("     • Get morning sunlight exposure")
            print("     • Limit naps to 20-30 minutes before 3 PM")
        
        print("\n🏥 Consider professional help if:")
        print("   • Sleep problems persist despite good sleep hygiene")
        print("   • You snore loudly or stop breathing during sleep")
        print("   • Daytime fatigue significantly impacts your life")
        print("   • You have symptoms of depression or anxiety")
    
    def _save_sleep_assessment(self, bedtime: str, sleep_time: int, wake_time: str,
                             sleep_quality: int, problems: Dict, hygiene_score: int,
                             hygiene_issues: List):
        """Save sleep assessment data"""
        data = self._load_sleep_data()
        
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "bedtime": bedtime,
            "sleep_onset_time": sleep_time,
            "wake_time": wake_time,
            "sleep_quality": sleep_quality,
            "problems": problems,
            "hygiene_score": hygiene_score,
            "hygiene_issues": hygiene_issues
        }
        
        data.setdefault('assessments', []).append(assessment)
        self._save_sleep_data(data)
    
    def _save_hygiene_plan(self, improvements: List[str]):
        """Save sleep hygiene improvement plan"""
        data = self._load_sleep_data()
        
        plan = {
            "timestamp": datetime.now().isoformat(),
            "improvements": improvements
        }
        
        data.setdefault('hygiene_plans', []).append(plan)
        self._save_sleep_data(data)
    
    def _save_bedtime_routine(self, activities: List[Dict], bedtime: str, duration: int):
        """Save bedtime routine"""
        data = self._load_sleep_data()
        
        routine = {
            "timestamp": datetime.now().isoformat(),
            "activities": activities,
            "bedtime": bedtime,
            "routine_duration": duration
        }
        
        data.setdefault('bedtime_routines', []).append(routine)
        self._save_sleep_data(data)
    
    def _load_sleep_data(self) -> Dict:
        """Load sleep support data"""
        if not os.path.exists(SLEEP_FILE):
            return {}
        
        try:
            with open(SLEEP_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_sleep_data(self, data: Dict):
        """Save sleep support data"""
        try:
            with open(SLEEP_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save sleep data: {e}")


def insomnia_command(action: str = "menu", **kwargs):
    """Main insomnia support command interface"""
    support = InsomniaSupport()
    
    if action == "menu":
        print("😴 Insomnia Support Menu")
        print("=" * 40)
        print("1. Sleep assessment")
        print("2. Sleep hygiene education")
        print("3. Bedtime routine builder")
        print("4. Sleep relaxation techniques")
        print()
        
        choice = input("Choose an option (1-4): ").strip()
        
        if choice == "1":
            support.sleep_assessment()
        elif choice == "2":
            support.sleep_hygiene_education()
        elif choice == "3":
            support.bedtime_routine_builder()
        elif choice == "4":
            support.sleep_relaxation_techniques()
        else:
            print("Invalid choice.")
    
    elif action == "assessment":
        support.sleep_assessment()
    elif action == "hygiene":
        support.sleep_hygiene_education()
    elif action == "routine":
        support.bedtime_routine_builder()
    elif action == "relaxation":
        support.sleep_relaxation_techniques()
    else:
        print(f"Unknown insomnia action: {action}")
        print("Available actions: menu, assessment, hygiene, routine, relaxation")
