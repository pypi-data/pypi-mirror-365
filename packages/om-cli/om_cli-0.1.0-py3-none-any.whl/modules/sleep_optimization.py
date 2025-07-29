#!/usr/bin/env python3
"""
Sleep Optimization Module
Inspired by Nyxo and Wake Up Time

Features:
- Sleep cycle calculation (90-minute cycles)
- Optimal bedtime/wake time recommendations
- Sleep quality tracking
- Sleep hygiene education
- Insomnia support integration
"""

import json
import os
from datetime import datetime, timedelta
import math

class SleepOptimizer:
    def __init__(self):
        self.data_dir = os.path.expanduser("~/.om")
        os.makedirs(self.data_dir, exist_ok=True)
        self.sleep_file = os.path.join(self.data_dir, "sleep_data.json")
        
        # Sleep cycle is approximately 90 minutes
        self.cycle_length = 90  # minutes
        self.sleep_latency = 15  # average time to fall asleep

    def load_sleep_data(self):
        """Load sleep tracking data"""
        try:
            with open(self.sleep_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_sleep_entry(self, entry):
        """Save sleep data entry"""
        data = self.load_sleep_data()
        entry['timestamp'] = datetime.now().isoformat()
        data.append(entry)
        
        # Keep only last 30 days
        cutoff = datetime.now() - timedelta(days=30)
        data = [d for d in data if datetime.fromisoformat(d['timestamp']) > cutoff]
        
        with open(self.sleep_file, 'w') as f:
            json.dump(data, f, indent=2)

    def calculate_optimal_wake_times(self, bedtime_str):
        """Calculate optimal wake times based on sleep cycles"""
        try:
            bedtime = datetime.strptime(bedtime_str, "%H:%M")
        except ValueError:
            print("Please use HH:MM format (e.g., 22:30)")
            return
        
        # Add sleep latency
        sleep_start = bedtime + timedelta(minutes=self.sleep_latency)
        
        print(f"💤 Optimal Wake Times for Bedtime: {bedtime_str}")
        print("=" * 40)
        print(f"Assuming you fall asleep by: {sleep_start.strftime('%H:%M')}")
        print("\n🌅 Best wake-up times (end of sleep cycles):")
        
        # Calculate wake times for 4-6 sleep cycles (6-9 hours)
        for cycles in range(4, 7):
            wake_time = sleep_start + timedelta(minutes=cycles * self.cycle_length)
            hours = cycles * 1.5
            print(f"  {wake_time.strftime('%H:%M')} - {hours} hours ({cycles} cycles)")
        
        print("\n💡 Tip: Waking up at the end of a sleep cycle helps you feel more refreshed!")

    def calculate_optimal_bedtimes(self, wake_time_str):
        """Calculate optimal bedtimes for a target wake time"""
        try:
            wake_time = datetime.strptime(wake_time_str, "%H:%M")
        except ValueError:
            print("Please use HH:MM format (e.g., 07:00)")
            return
        
        print(f"🌙 Optimal Bedtimes for Wake Time: {wake_time_str}")
        print("=" * 40)
        print("🛏️  Recommended bedtimes (including 15min to fall asleep):")
        
        # Calculate bedtimes for 4-6 sleep cycles
        for cycles in range(4, 7):
            sleep_duration = cycles * self.cycle_length
            bedtime = wake_time - timedelta(minutes=sleep_duration + self.sleep_latency)
            hours = cycles * 1.5
            
            # Handle day rollover
            if bedtime.hour > wake_time.hour:
                bedtime_str = bedtime.strftime('%H:%M') + " (previous day)"
            else:
                bedtime_str = bedtime.strftime('%H:%M')
            
            print(f"  {bedtime_str} - {hours} hours ({cycles} cycles)")
        
        print("\n💡 Most adults need 7-9 hours of sleep (5-6 cycles)")

    def sleep_quality_tracker(self):
        """Track sleep quality and patterns"""
        print("📊 Sleep Quality Tracker")
        print("=" * 25)
        
        # Get sleep data
        bedtime = input("What time did you go to bed last night? (HH:MM): ")
        wake_time = input("What time did you wake up? (HH:MM): ")
        
        try:
            bed_dt = datetime.strptime(bedtime, "%H:%M")
            wake_dt = datetime.strptime(wake_time, "%H:%M")
            
            # Handle overnight sleep
            if wake_dt < bed_dt:
                wake_dt += timedelta(days=1)
            
            sleep_duration = wake_dt - bed_dt
            hours = sleep_duration.total_seconds() / 3600
            
        except ValueError:
            print("Invalid time format. Please use HH:MM")
            return
        
        # Quality metrics
        quality = input("How would you rate your sleep quality? (1-10): ")
        time_to_sleep = input("How long did it take to fall asleep? (minutes): ")
        wake_ups = input("How many times did you wake up during the night? ")
        
        # Morning feeling
        morning_feeling = input("How did you feel waking up? (refreshed/tired/groggy): ")
        
        # Calculate sleep efficiency
        try:
            sleep_latency = int(time_to_sleep)
            actual_sleep = hours - (sleep_latency / 60)
            efficiency = (actual_sleep / hours) * 100
        except ValueError:
            efficiency = None
        
        # Save data
        entry = {
            'bedtime': bedtime,
            'wake_time': wake_time,
            'duration_hours': round(hours, 1),
            'quality_rating': quality,
            'sleep_latency_minutes': time_to_sleep,
            'night_wakings': wake_ups,
            'morning_feeling': morning_feeling,
            'sleep_efficiency': round(efficiency, 1) if efficiency else None
        }
        
        self.save_sleep_entry(entry)
        
        # Provide feedback
        print(f"\n📈 Sleep Summary:")
        print(f"Duration: {hours:.1f} hours")
        print(f"Quality: {quality}/10")
        if efficiency:
            print(f"Sleep efficiency: {efficiency:.1f}%")
        
        # Recommendations
        if hours < 7:
            print("\n💡 You might benefit from going to bed earlier")
        elif hours > 9:
            print("\n💡 You might be oversleeping - try a slightly earlier wake time")
        
        if int(quality) < 6:
            print("💡 Consider reviewing your sleep hygiene habits")

    def sleep_hygiene_tips(self):
        """Provide sleep hygiene education"""
        print("🛏️  Sleep Hygiene Guide")
        print("=" * 25)
        
        categories = {
            "Environment": [
                "Keep bedroom cool (60-67°F/15-19°C)",
                "Make room as dark as possible",
                "Minimize noise or use white noise",
                "Invest in comfortable mattress and pillows",
                "Reserve bed for sleep and intimacy only"
            ],
            "Timing": [
                "Keep consistent sleep/wake times, even weekends",
                "Avoid naps after 3 PM",
                "Stop caffeine 6+ hours before bedtime",
                "Finish eating 2-3 hours before bed",
                "Exercise regularly, but not close to bedtime"
            ],
            "Pre-Sleep Routine": [
                "Start winding down 1 hour before bed",
                "Avoid screens 1 hour before sleep",
                "Try reading, gentle stretching, or meditation",
                "Take a warm bath or shower",
                "Practice relaxation techniques"
            ],
            "What to Avoid": [
                "Alcohol close to bedtime (disrupts sleep cycles)",
                "Large meals or spicy foods before bed",
                "Intense exercise within 4 hours of sleep",
                "Checking the clock if you wake up",
                "Lying in bed awake for more than 20 minutes"
            ]
        }
        
        for category, tips in categories.items():
            print(f"\n🔸 {category}:")
            for tip in tips:
                print(f"  • {tip}")
        
        print(f"\n💤 Remember: Good sleep hygiene takes time to show results!")

    def sleep_pattern_analysis(self):
        """Analyze sleep patterns from tracked data"""
        data = self.load_sleep_data()
        
        if len(data) < 3:
            print("Need at least 3 nights of data for pattern analysis.")
            print("Use 'om sleep track' to log your sleep!")
            return
        
        print("📊 Sleep Pattern Analysis")
        print("=" * 25)
        
        # Calculate averages
        durations = [float(entry['duration_hours']) for entry in data if entry.get('duration_hours')]
        qualities = [int(entry['quality_rating']) for entry in data if entry.get('quality_rating')]
        
        if durations:
            avg_duration = sum(durations) / len(durations)
            print(f"Average sleep duration: {avg_duration:.1f} hours")
        
        if qualities:
            avg_quality = sum(qualities) / len(qualities)
            print(f"Average sleep quality: {avg_quality:.1f}/10")
        
        # Identify patterns
        print(f"\n📈 Patterns from last {len(data)} nights:")
        
        # Best and worst nights
        if qualities:
            best_night = max(data, key=lambda x: int(x.get('quality_rating', 0)))
            worst_night = min(data, key=lambda x: int(x.get('quality_rating', 10)))
            
            print(f"Best night: {best_night['quality_rating']}/10 quality")
            print(f"Worst night: {worst_night['quality_rating']}/10 quality")
        
        # Recommendations based on patterns
        print(f"\n💡 Recommendations:")
        if avg_duration < 7:
            print("• Try going to bed 30 minutes earlier")
        if avg_quality < 7:
            print("• Review sleep hygiene practices")
            print("• Consider factors affecting sleep quality")
        
        # Consistency check
        bedtimes = []
        for entry in data:
            try:
                bt = datetime.strptime(entry['bedtime'], "%H:%M")
                bedtimes.append(bt.hour * 60 + bt.minute)  # Convert to minutes
            except:
                continue
        
        if bedtimes:
            bedtime_variance = max(bedtimes) - min(bedtimes)
            if bedtime_variance > 60:  # More than 1 hour variance
                print("• Try to keep more consistent bedtimes")

    def power_nap_timer(self):
        """Optimal power nap timing"""
        print("⚡ Power Nap Optimizer")
        print("=" * 20)
        
        current_time = datetime.now()
        
        print("Optimal nap durations:")
        print("• 10-20 minutes: Quick refresh, no grogginess")
        print("• 30 minutes: Risk of grogginess (sleep inertia)")
        print("• 90 minutes: Full sleep cycle, wake refreshed")
        
        nap_choice = input("\nChoose nap duration (10, 20, or 90 minutes): ")
        
        try:
            duration = int(nap_choice)
            if duration not in [10, 20, 90]:
                duration = 20  # Default
            
            wake_time = current_time + timedelta(minutes=duration)
            
            print(f"\n⏰ Set alarm for: {wake_time.strftime('%H:%M')}")
            print(f"Nap duration: {duration} minutes")
            
            if duration == 90:
                print("💡 This is a full sleep cycle - great for deeper rest")
            else:
                print("💡 Short nap - you should wake up feeling refreshed")
                
        except ValueError:
            print("Invalid duration. Try 'om sleep nap' again.")

def run(args=None):
    """Main entry point for sleep optimization"""
    optimizer = SleepOptimizer()
    
    if not args:
        print("😴 Sleep Optimization Tools")
        print("1. Calculate optimal wake times")
        print("2. Calculate optimal bedtimes") 
        print("3. Track sleep quality")
        print("4. Sleep hygiene tips")
        print("5. Analyze sleep patterns")
        print("6. Power nap timer")
        
        choice = input("\nChoose option (1-6): ")
        args = [choice]
    
    if args[0] in ['1', 'wake', 'wakeup']:
        bedtime = input("What time do you plan to go to bed? (HH:MM): ")
        optimizer.calculate_optimal_wake_times(bedtime)
    elif args[0] in ['2', 'bedtime', 'bed']:
        wake_time = input("What time do you need to wake up? (HH:MM): ")
        optimizer.calculate_optimal_bedtimes(wake_time)
    elif args[0] in ['3', 'track', 'quality']:
        optimizer.sleep_quality_tracker()
    elif args[0] in ['4', 'hygiene', 'tips']:
        optimizer.sleep_hygiene_tips()
    elif args[0] in ['5', 'analyze', 'patterns']:
        optimizer.sleep_pattern_analysis()
    elif args[0] in ['6', 'nap', 'power']:
        optimizer.power_nap_timer()
    else:
        print("Usage: om sleep [wake|bedtime|track|hygiene|analyze|nap]")

if __name__ == "__main__":
    run()
