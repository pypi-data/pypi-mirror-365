"""
Addiction Recovery module for om - inspired by Try Dry® app
Behavioral science-based approach to addiction recovery and habit change
"""

import json
import os
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any

RECOVERY_FILE = os.path.expanduser("~/.om_recovery.json")

class AddictionRecovery:
    def __init__(self):
        self.substance_types = {
            "alcohol": {
                "name": "Alcohol",
                "unit": "standard drinks",
                "cost_per_unit": 8.0,  # Average cost per drink
                "calories_per_unit": 150,  # Average calories per drink
                "health_risks": [
                    "Heart disease", "Stroke", "Liver disease", "7 types of cancer",
                    "High blood pressure", "Mental health problems", "Dependency"
                ]
            },
            "cigarettes": {
                "name": "Cigarettes",
                "unit": "cigarettes",
                "cost_per_unit": 0.50,  # Average cost per cigarette
                "calories_per_unit": 0,
                "health_risks": [
                    "Lung cancer", "Heart disease", "Stroke", "COPD",
                    "15+ types of cancer", "Reduced immune function", "Premature aging"
                ]
            },
            "caffeine": {
                "name": "Caffeine",
                "unit": "mg",
                "cost_per_unit": 0.10,  # Cost per 100mg
                "calories_per_unit": 5,
                "health_risks": [
                    "Anxiety", "Sleep disruption", "Dependency", "Digestive issues",
                    "Heart palpitations", "Headaches", "Mood swings"
                ]
            },
            "sugar": {
                "name": "Added Sugar",
                "unit": "grams",
                "cost_per_unit": 0.05,
                "calories_per_unit": 4,
                "health_risks": [
                    "Type 2 diabetes", "Obesity", "Heart disease", "Tooth decay",
                    "Fatty liver disease", "Increased inflammation", "Energy crashes"
                ]
            },
            "social_media": {
                "name": "Social Media",
                "unit": "minutes",
                "cost_per_unit": 0.0,  # Time cost
                "calories_per_unit": 0,
                "health_risks": [
                    "Anxiety", "Depression", "Sleep disruption", "FOMO",
                    "Reduced attention span", "Social comparison", "Addiction"
                ]
            }
        }
        
        self.goal_types = {
            "abstinence": "Complete abstinence (0 units)",
            "reduction": "Reduce consumption by X%",
            "limit": "Stay within daily/weekly limits",
            "planned": "Planned consumption only",
            "mindful": "Mindful consumption tracking"
        }
        
        self.badges = {
            # Time-based badges
            "day_1": {"name": "First Day", "description": "Completed your first day", "emoji": "🌱"},
            "day_3": {"name": "Three Days", "description": "Three days strong", "emoji": "🌿"},
            "week_1": {"name": "One Week", "description": "One week milestone", "emoji": "⭐"},
            "week_2": {"name": "Two Weeks", "description": "Two weeks of progress", "emoji": "🌟"},
            "month_1": {"name": "One Month", "description": "One month achievement", "emoji": "🏆"},
            "month_3": {"name": "Three Months", "description": "Three months strong", "emoji": "💎"},
            "month_6": {"name": "Six Months", "description": "Half year milestone", "emoji": "👑"},
            "year_1": {"name": "One Year", "description": "One year anniversary", "emoji": "🎉"},
            
            # Achievement badges
            "money_saver": {"name": "Money Saver", "description": "Saved $100+", "emoji": "💰"},
            "health_hero": {"name": "Health Hero", "description": "Avoided 1000+ calories", "emoji": "💪"},
            "goal_setter": {"name": "Goal Setter", "description": "Set your first goal", "emoji": "🎯"},
            "streak_master": {"name": "Streak Master", "description": "10+ day streak", "emoji": "🔥"},
            "mindful_tracker": {"name": "Mindful Tracker", "description": "Tracked for 30 days", "emoji": "📊"},
            "support_seeker": {"name": "Support Seeker", "description": "Used support resources", "emoji": "🤝"}
        }
    
    def show_recovery_menu(self):
        """Display addiction recovery main menu"""
        print("🌱 Addiction Recovery & Habit Change")
        print("=" * 50)
        print("Science-based approach to overcoming addiction and changing habits")
        print("Inspired by behavioral science and user feedback")
        print()
        
        # Show current tracking status
        data = self._load_recovery_data()
        active_substances = data.get('substances', {})
        
        if active_substances:
            print("📊 Currently Tracking:")
            for substance_id, substance_data in active_substances.items():
                substance_info = self.substance_types[substance_id]
                goal_type = substance_data.get('goal_type', 'reduction')
                print(f"   • {substance_info['name']} - Goal: {self.goal_types[goal_type]}")
            print()
        
        print("🎯 Recovery Options:")
        print("1. Start tracking a substance/habit")
        print("2. Log consumption/usage")
        print("3. View progress and statistics")
        print("4. Set or update goals")
        print("5. View badges and achievements")
        print("6. Get daily motivation")
        print("7. Risk assessment quiz")
        print("8. Recovery resources and support")
        print()
        
        choice = input("Choose an option (1-8) or press Enter to return: ").strip()
        
        if choice == "1":
            self._start_tracking()
        elif choice == "2":
            self._log_consumption()
        elif choice == "3":
            self._show_progress()
        elif choice == "4":
            self._set_goals()
        elif choice == "5":
            self._show_badges()
        elif choice == "6":
            self._daily_motivation()
        elif choice == "7":
            self._risk_assessment()
        elif choice == "8":
            self._recovery_resources()
    
    def _start_tracking(self):
        """Start tracking a new substance or habit"""
        print("\n🎯 Start Tracking")
        print("=" * 30)
        print("Choose what you'd like to track:")
        
        substances = list(self.substance_types.keys())
        for i, substance_id in enumerate(substances, 1):
            substance_info = self.substance_types[substance_id]
            print(f"{i}. {substance_info['name']}")
        
        print()
        choice = input(f"Choose substance/habit (1-{len(substances)}): ").strip()
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(substances):
                substance_id = substances[choice_idx]
                self._setup_substance_tracking(substance_id)
        except ValueError:
            print("Invalid choice.")
    
    def _setup_substance_tracking(self, substance_id: str):
        """Set up tracking for a specific substance"""
        substance_info = self.substance_types[substance_id]
        
        print(f"\n🎯 Setting up {substance_info['name']} tracking")
        print("=" * 40)
        
        # Get baseline information
        print("Let's establish your baseline:")
        current_usage = input(f"How many {substance_info['unit']} do you typically consume per day? ").strip()
        
        try:
            current_usage = float(current_usage)
        except ValueError:
            current_usage = 0
        
        # Choose goal type
        print(f"\nWhat's your goal with {substance_info['name']}?")
        goal_types = list(self.goal_types.keys())
        for i, goal_type in enumerate(goal_types, 1):
            print(f"{i}. {self.goal_types[goal_type]}")
        
        goal_choice = input(f"Choose goal type (1-{len(goal_types)}): ").strip()
        
        try:
            goal_idx = int(goal_choice) - 1
            if 0 <= goal_idx < len(goal_types):
                goal_type = goal_types[goal_idx]
            else:
                goal_type = "reduction"
        except ValueError:
            goal_type = "reduction"
        
        # Set specific goal target
        goal_target = 0
        if goal_type == "reduction":
            reduction_percent = input("What percentage reduction are you aiming for? (e.g., 50): ").strip()
            try:
                reduction_percent = float(reduction_percent)
                goal_target = current_usage * (1 - reduction_percent / 100)
            except ValueError:
                goal_target = current_usage * 0.5
        elif goal_type == "limit":
            limit = input(f"What's your daily limit ({substance_info['unit']})? ").strip()
            try:
                goal_target = float(limit)
            except ValueError:
                goal_target = current_usage * 0.7
        
        # Save tracking setup
        data = self._load_recovery_data()
        
        substance_data = {
            "name": substance_info['name'],
            "unit": substance_info['unit'],
            "baseline_usage": current_usage,
            "goal_type": goal_type,
            "goal_target": goal_target,
            "start_date": datetime.now().isoformat(),
            "cost_per_unit": substance_info['cost_per_unit'],
            "calories_per_unit": substance_info['calories_per_unit'],
            "consumption_log": []
        }
        
        data.setdefault('substances', {})[substance_id] = substance_data
        self._save_recovery_data(data)
        
        print(f"\n✅ {substance_info['name']} tracking started!")
        print(f"Baseline: {current_usage} {substance_info['unit']}/day")
        print(f"Goal: {self.goal_types[goal_type]}")
        if goal_target > 0:
            print(f"Target: {goal_target} {substance_info['unit']}/day")
        
        # Award first badge
        self._check_and_award_badge("goal_setter")
    
    def _log_consumption(self):
        """Log consumption/usage"""
        data = self._load_recovery_data()
        substances = data.get('substances', {})
        
        if not substances:
            print("No substances being tracked. Start tracking first!")
            return
        
        print("\n📝 Log Consumption")
        print("=" * 30)
        
        # Choose substance
        substance_list = list(substances.keys())
        for i, substance_id in enumerate(substance_list, 1):
            substance_data = substances[substance_id]
            print(f"{i}. {substance_data['name']}")
        
        choice = input(f"Choose substance (1-{len(substance_list)}): ").strip()
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(substance_list):
                substance_id = substance_list[choice_idx]
                self._log_substance_consumption(substance_id, substances[substance_id])
        except ValueError:
            print("Invalid choice.")
    
    def _log_substance_consumption(self, substance_id: str, substance_data: Dict):
        """Log consumption for a specific substance"""
        print(f"\n📝 Logging {substance_data['name']}")
        print("=" * 30)
        
        # Get consumption amount
        amount = input(f"How many {substance_data['unit']} did you consume? ").strip()
        
        try:
            amount = float(amount)
        except ValueError:
            print("Invalid amount.")
            return
        
        # Get optional context
        context = input("Any context or notes? (optional): ").strip()
        
        # Calculate costs and calories
        cost = amount * substance_data['cost_per_unit']
        calories = amount * substance_data['calories_per_unit']
        
        # Log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "amount": amount,
            "cost": cost,
            "calories": calories,
            "context": context
        }
        
        substance_data['consumption_log'].append(log_entry)
        
        # Save data
        data = self._load_recovery_data()
        data['substances'][substance_id] = substance_data
        self._save_recovery_data(data)
        
        print(f"\n✅ Logged: {amount} {substance_data['unit']}")
        if cost > 0:
            print(f"💰 Cost: ${cost:.2f}")
        if calories > 0:
            print(f"🔥 Calories: {calories:.0f}")
        
        # Check for badges
        self._check_tracking_badges(substance_id)
    
    def _show_progress(self):
        """Show progress and statistics"""
        data = self._load_recovery_data()
        substances = data.get('substances', {})
        
        if not substances:
            print("No substances being tracked yet.")
            return
        
        print("\n📊 Your Progress")
        print("=" * 40)
        
        for substance_id, substance_data in substances.items():
            self._show_substance_progress(substance_id, substance_data)
            print()
    
    def _show_substance_progress(self, substance_id: str, substance_data: Dict):
        """Show progress for a specific substance"""
        print(f"📈 {substance_data['name']} Progress")
        print("-" * 30)
        
        consumption_log = substance_data.get('consumption_log', [])
        
        if not consumption_log:
            print("No consumption logged yet.")
            return
        
        # Calculate statistics
        start_date = datetime.fromisoformat(substance_data['start_date'])
        days_tracking = (datetime.now() - start_date).days + 1
        
        # Recent consumption (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_consumption = [
            entry for entry in consumption_log
            if datetime.fromisoformat(entry['timestamp']) >= week_ago
        ]
        
        # Total savings
        baseline_daily = substance_data.get('baseline_usage', 0)
        total_baseline_consumption = baseline_daily * days_tracking
        total_actual_consumption = sum(entry['amount'] for entry in consumption_log)
        units_saved = max(0, total_baseline_consumption - total_actual_consumption)
        
        money_saved = units_saved * substance_data['cost_per_unit']
        calories_saved = units_saved * substance_data['calories_per_unit']
        
        print(f"📅 Tracking for: {days_tracking} days")
        print(f"🎯 Goal: {self.goal_types[substance_data.get('goal_type', 'reduction')]}")
        
        if recent_consumption:
            avg_daily = sum(entry['amount'] for entry in recent_consumption) / min(7, len(recent_consumption))
            print(f"📊 Recent average: {avg_daily:.1f} {substance_data['unit']}/day")
        
        print(f"💰 Money saved: ${money_saved:.2f}")
        if calories_saved > 0:
            print(f"🔥 Calories avoided: {calories_saved:.0f}")
        
        # Streak calculation
        streak = self._calculate_streak(substance_id, consumption_log)
        if streak > 0:
            print(f"🔥 Current streak: {streak} days")
        
        # Progress toward goal
        goal_target = substance_data.get('goal_target', 0)
        if goal_target > 0 and recent_consumption:
            recent_avg = sum(entry['amount'] for entry in recent_consumption) / len(recent_consumption)
            if recent_avg <= goal_target:
                print("✅ Meeting your goal!")
            else:
                print(f"🎯 Goal progress: {((baseline_daily - recent_avg) / (baseline_daily - goal_target) * 100):.0f}%")
    
    def _calculate_streak(self, substance_id: str, consumption_log: List[Dict]) -> int:
        """Calculate current abstinence streak"""
        if not consumption_log:
            return 0
        
        # Sort by date (most recent first)
        sorted_log = sorted(consumption_log, key=lambda x: x['timestamp'], reverse=True)
        
        # Check if there's consumption today
        today = datetime.now().date()
        if sorted_log and datetime.fromisoformat(sorted_log[0]['timestamp']).date() == today:
            return 0  # Consumed today, no streak
        
        # Count days since last consumption
        if sorted_log:
            last_consumption = datetime.fromisoformat(sorted_log[0]['timestamp']).date()
            streak = (today - last_consumption).days
            return streak
        
        return 0
    
    def _show_badges(self):
        """Show earned badges and achievements"""
        data = self._load_recovery_data()
        earned_badges = data.get('badges', [])
        
        print("\n🏆 Badges & Achievements")
        print("=" * 40)
        
        if not earned_badges:
            print("No badges earned yet. Keep going!")
            print("\n🎯 Available badges:")
            for badge_id, badge_info in self.badges.items():
                print(f"   {badge_info['emoji']} {badge_info['name']}: {badge_info['description']}")
            return
        
        print("🌟 Earned Badges:")
        for badge_entry in earned_badges:
            badge_id = badge_entry['badge_id']
            if badge_id in self.badges:
                badge_info = self.badges[badge_id]
                earned_date = datetime.fromisoformat(badge_entry['earned_date']).strftime('%Y-%m-%d')
                print(f"   {badge_info['emoji']} {badge_info['name']} - {earned_date}")
                print(f"      {badge_info['description']}")
        
        print(f"\n📊 Total badges: {len(earned_badges)}")
        
        # Show next badges to earn
        unearned_badges = [bid for bid in self.badges.keys() if bid not in [b['badge_id'] for b in earned_badges]]
        if unearned_badges:
            print("\n🎯 Next badges to earn:")
            for badge_id in unearned_badges[:3]:  # Show next 3
                badge_info = self.badges[badge_id]
                print(f"   {badge_info['emoji']} {badge_info['name']}: {badge_info['description']}")
    
    def _daily_motivation(self):
        """Provide daily motivation and encouragement"""
        print("\n💪 Daily Motivation")
        print("=" * 30)
        
        motivational_messages = [
            "Every day you choose recovery is a victory worth celebrating.",
            "Your future self will thank you for the choices you make today.",
            "Progress isn't always linear, but every step forward counts.",
            "You have the strength to overcome any challenge.",
            "Recovery is not just about stopping - it's about starting to live fully.",
            "Each moment of resistance builds your resilience muscle.",
            "You're not just breaking a habit - you're building a better life.",
            "The hardest part is behind you. Keep moving forward.",
            "Your commitment to change is inspiring and powerful.",
            "Today is another opportunity to choose your health and happiness."
        ]
        
        # Show personalized motivation based on progress
        data = self._load_recovery_data()
        substances = data.get('substances', {})
        
        if substances:
            # Calculate overall progress
            total_money_saved = 0
            total_days_tracking = 0
            
            for substance_data in substances.values():
                consumption_log = substance_data.get('consumption_log', [])
                if consumption_log:
                    start_date = datetime.fromisoformat(substance_data['start_date'])
                    days_tracking = (datetime.now() - start_date).days + 1
                    total_days_tracking = max(total_days_tracking, days_tracking)
                    
                    baseline_daily = substance_data.get('baseline_usage', 0)
                    total_baseline = baseline_daily * days_tracking
                    total_actual = sum(entry['amount'] for entry in consumption_log)
                    units_saved = max(0, total_baseline - total_actual)
                    total_money_saved += units_saved * substance_data['cost_per_unit']
            
            print(f"🎯 You've been on your recovery journey for {total_days_tracking} days!")
            if total_money_saved > 0:
                print(f"💰 You've saved ${total_money_saved:.2f} so far!")
            print()
        
        # Random motivational message
        message = random.choice(motivational_messages)
        print(f"💭 {message}")
        
        # Health benefits reminder
        print(f"\n🌟 Remember the benefits you're gaining:")
        if substances:
            for substance_id, substance_data in substances.items():
                substance_info = self.substance_types[substance_id]
                print(f"\n   {substance_info['name']} recovery benefits:")
                for benefit in substance_info['health_risks'][:3]:  # Show top 3 as benefits
                    print(f"   • Reduced risk of {benefit.lower()}")
    
    def _risk_assessment(self):
        """Simple risk assessment quiz"""
        print("\n🔍 Risk Assessment Quiz")
        print("=" * 30)
        print("This brief quiz can help you understand your relationship with substances.")
        print("Answer honestly for the most accurate results.\n")
        
        # Generic risk assessment questions
        questions = [
            "Do you find it difficult to control your consumption?",
            "Have you tried to cut back but found it challenging?",
            "Do you consume more than you originally intended?",
            "Has your consumption affected your work or relationships?",
            "Do you feel anxious or uncomfortable when you can't consume?",
            "Have others expressed concern about your consumption?",
            "Do you consume to cope with stress or negative emotions?",
            "Has your tolerance increased over time?"
        ]
        
        score = 0
        for i, question in enumerate(questions, 1):
            print(f"{i}. {question}")
            answer = input("   (yes/no): ").strip().lower()
            if answer in ['yes', 'y']:
                score += 1
            print()
        
        # Interpret results
        print("📊 Assessment Results:")
        print("-" * 20)
        
        if score <= 2:
            risk_level = "Low Risk"
            message = "Your responses suggest a low risk pattern. Continue monitoring your consumption and maintain healthy habits."
        elif score <= 4:
            risk_level = "Moderate Risk"
            message = "Your responses suggest some concerning patterns. Consider setting stricter limits and tracking your consumption more closely."
        elif score <= 6:
            risk_level = "High Risk"
            message = "Your responses suggest significant risk factors. Consider seeking support from friends, family, or professionals."
        else:
            risk_level = "Very High Risk"
            message = "Your responses suggest serious concerns. We strongly recommend seeking professional help and support."
        
        print(f"Risk Level: {risk_level}")
        print(f"Score: {score}/8")
        print(f"\n💡 {message}")
        
        if score > 4:
            print(f"\n🆘 Support Resources:")
            print("• Consider speaking with a healthcare provider")
            print("• Look into local support groups")
            print("• Use the om recovery tools daily")
            print("• Reach out to trusted friends or family")
    
    def _recovery_resources(self):
        """Show recovery resources and support information"""
        print("\n🤝 Recovery Resources & Support")
        print("=" * 40)
        
        print("🆘 Crisis & Emergency Support:")
        print("• National Suicide Prevention Lifeline: 988")
        print("• Crisis Text Line: Text HOME to 741741")
        print("• Emergency Services: 911")
        print()
        
        print("🍷 Alcohol Support:")
        print("• Alcoholics Anonymous: aa.org")
        print("• SMART Recovery: smartrecovery.org")
        print("• National Helpline: 1-800-662-4357")
        print()
        
        print("🚭 Smoking Cessation:")
        print("• Quitline: 1-800-QUIT-NOW")
        print("• smokefree.gov")
        print("• American Lung Association: lung.org")
        print()
        
        print("💊 Substance Abuse:")
        print("• SAMHSA National Helpline: 1-800-662-4357")
        print("• Narcotics Anonymous: na.org")
        print("• findtreatment.gov")
        print()
        
        print("🧠 Mental Health Support:")
        print("• National Alliance on Mental Illness: nami.org")
        print("• Mental Health America: mhanational.org")
        print("• Psychology Today: psychologytoday.com")
        print()
        
        print("💡 Self-Help Strategies:")
        print("• Use om's daily tracking and motivation features")
        print("• Practice mindfulness: om meditate")
        print("• Build healthy habits: om habits")
        print("• Process emotions: om journal")
        print("• Manage stress: om coping")
        print()
        
        print("🌟 Remember:")
        print("• Recovery is a journey, not a destination")
        print("• Setbacks are normal and part of the process")
        print("• You don't have to do this alone")
        print("• Professional help is available and effective")
        print("• Every day of progress matters")
    
    def _check_and_award_badge(self, badge_id: str):
        """Check and award a specific badge"""
        data = self._load_recovery_data()
        earned_badges = data.get('badges', [])
        
        # Check if already earned
        if any(b['badge_id'] == badge_id for b in earned_badges):
            return
        
        # Award badge
        badge_entry = {
            "badge_id": badge_id,
            "earned_date": datetime.now().isoformat()
        }
        
        earned_badges.append(badge_entry)
        data['badges'] = earned_badges
        self._save_recovery_data(data)
        
        # Celebrate
        if badge_id in self.badges:
            badge_info = self.badges[badge_id]
            print(f"\n🎉 BADGE EARNED! 🎉")
            print(f"{badge_info['emoji']} {badge_info['name']}")
            print(f"{badge_info['description']}")
            print("Keep up the amazing work!")
    
    def _check_tracking_badges(self, substance_id: str):
        """Check for time-based and achievement badges"""
        data = self._load_recovery_data()
        substance_data = data['substances'][substance_id]
        consumption_log = substance_data.get('consumption_log', [])
        
        if not consumption_log:
            return
        
        # Calculate days tracking
        start_date = datetime.fromisoformat(substance_data['start_date'])
        days_tracking = (datetime.now() - start_date).days + 1
        
        # Check time-based badges
        time_badges = {
            1: "day_1",
            3: "day_3", 
            7: "week_1",
            14: "week_2",
            30: "month_1",
            90: "month_3",
            180: "month_6",
            365: "year_1"
        }
        
        for days, badge_id in time_badges.items():
            if days_tracking >= days:
                self._check_and_award_badge(badge_id)
        
        # Check achievement badges
        # Money saved badge
        baseline_daily = substance_data.get('baseline_usage', 0)
        total_baseline = baseline_daily * days_tracking
        total_actual = sum(entry['amount'] for entry in consumption_log)
        units_saved = max(0, total_baseline - total_actual)
        money_saved = units_saved * substance_data['cost_per_unit']
        
        if money_saved >= 100:
            self._check_and_award_badge("money_saver")
        
        # Calories avoided badge
        calories_saved = units_saved * substance_data['calories_per_unit']
        if calories_saved >= 1000:
            self._check_and_award_badge("health_hero")
        
        # Tracking consistency badge
        if days_tracking >= 30:
            self._check_and_award_badge("mindful_tracker")
        
        # Streak badge
        streak = self._calculate_streak(substance_id, consumption_log)
        if streak >= 10:
            self._check_and_award_badge("streak_master")
    
    def _load_recovery_data(self) -> Dict:
        """Load recovery data from file"""
        if not os.path.exists(RECOVERY_FILE):
            return {}
        
        try:
            with open(RECOVERY_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_recovery_data(self, data: Dict):
        """Save recovery data to file"""
        try:
            with open(RECOVERY_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save recovery data: {e}")


def addiction_recovery_command(action: str = "menu", **kwargs):
    """Main addiction recovery command interface"""
    recovery = AddictionRecovery()
    
    if action == "menu":
        recovery.show_recovery_menu()
    elif action == "track":
        substance = kwargs.get('substance')
        if substance and substance in recovery.substance_types:
            recovery._setup_substance_tracking(substance)
        else:
            recovery._start_tracking()
    elif action == "log":
        recovery._log_consumption()
    elif action == "progress":
        recovery._show_progress()
    elif action == "badges":
        recovery._show_badges()
    elif action == "motivation":
        recovery._daily_motivation()
    elif action == "quiz":
        recovery._risk_assessment()
    elif action == "resources":
        recovery._recovery_resources()
    else:
        print(f"Unknown recovery action: {action}")
        print("Available actions: menu, track, log, progress, badges, motivation, quiz, resources")
