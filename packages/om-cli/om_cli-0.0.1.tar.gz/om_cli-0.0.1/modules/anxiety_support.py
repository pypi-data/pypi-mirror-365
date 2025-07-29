"""
Anxiety symptoms support module for om
Evidence-based tools for managing anxiety symptoms
"""

import json
import os
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional

ANXIETY_FILE = os.path.expanduser("~/.om_anxiety.json")

class AnxietySupport:
    def __init__(self):
        self.anxiety_types = {
            "generalized": "Generalized Anxiety (persistent worry about various topics)",
            "social": "Social Anxiety (fear of social situations and judgment)",
            "panic": "Panic Disorder (sudden intense fear with physical symptoms)",
            "specific": "Specific Phobias (intense fear of specific objects/situations)",
            "health": "Health Anxiety (excessive worry about health/illness)",
            "performance": "Performance Anxiety (fear of performing in front of others)"
        }
        
        self.physical_symptoms = [
            "rapid heartbeat", "sweating", "trembling", "shortness of breath",
            "chest tightness", "nausea", "dizziness", "muscle tension",
            "headaches", "fatigue", "restlessness", "hot/cold flashes"
        ]
        
        self.cognitive_symptoms = [
            "racing thoughts", "difficulty concentrating", "mind going blank",
            "catastrophic thinking", "fear of losing control", "fear of dying",
            "worry about worry", "anticipatory anxiety", "intrusive thoughts"
        ]
        
        self.behavioral_symptoms = [
            "avoidance", "procrastination", "seeking reassurance", "checking behaviors",
            "restlessness", "fidgeting", "social withdrawal", "perfectionism"
        ]
        
        self.coping_strategies = {
            "immediate": {
                "breathing": "Deep breathing exercises",
                "grounding": "5-4-3-2-1 grounding technique",
                "progressive": "Progressive muscle relaxation",
                "cold_water": "Cold water on face/wrists",
                "movement": "Gentle movement or stretching"
            },
            "cognitive": {
                "reality_check": "Reality testing thoughts",
                "probability": "Probability estimation",
                "worst_case": "Best/worst/most likely scenarios",
                "evidence": "Evidence for and against thoughts",
                "reframe": "Cognitive reframing"
            },
            "behavioral": {
                "gradual_exposure": "Gradual exposure to fears",
                "activity_scheduling": "Pleasant activity scheduling",
                "problem_solving": "Structured problem solving",
                "assertiveness": "Assertiveness training",
                "relaxation": "Regular relaxation practice"
            }
        }
    
    def anxiety_assessment(self):
        """Comprehensive anxiety assessment"""
        print("🔍 Anxiety Assessment")
        print("=" * 40)
        print("This assessment helps identify your anxiety patterns and symptoms.")
        print("This is not a diagnostic tool - consult a professional for diagnosis.")
        print()
        
        # GAD-7 inspired questions
        questions = [
            "Feeling nervous, anxious, or on edge",
            "Not being able to stop or control worrying",
            "Worrying too much about different things",
            "Trouble relaxing",
            "Being so restless that it's hard to sit still",
            "Becoming easily annoyed or irritable",
            "Feeling afraid as if something awful might happen"
        ]
        
        frequency_options = {
            "0": "Not at all",
            "1": "Several days",
            "2": "More than half the days", 
            "3": "Nearly every day"
        }
        
        print("Over the last 2 weeks, how often have you been bothered by:")
        print("0 = Not at all, 1 = Several days, 2 = More than half the days, 3 = Nearly every day")
        print()
        
        total_score = 0
        responses = []
        
        for i, question in enumerate(questions, 1):
            print(f"{i}. {question}")
            while True:
                response = input("   Your answer (0-3): ").strip()
                if response in frequency_options:
                    score = int(response)
                    total_score += score
                    responses.append(score)
                    print(f"   {frequency_options[response]}")
                    break
                else:
                    print("   Please enter 0, 1, 2, or 3")
            print()
        
        # Additional symptom check
        print("Which physical symptoms have you experienced recently?")
        physical_count = 0
        for symptom in self.physical_symptoms:
            response = input(f"   {symptom}? (y/n): ").strip().lower()
            if response == 'y':
                physical_count += 1
        
        print()
        print("Which thinking patterns have you noticed?")
        cognitive_count = 0
        for symptom in self.cognitive_symptoms:
            response = input(f"   {symptom}? (y/n): ").strip().lower()
            if response == 'y':
                cognitive_count += 1
        
        # Interpret results
        self._interpret_anxiety_assessment(total_score, physical_count, cognitive_count)
        
        # Save assessment
        self._save_anxiety_assessment(total_score, responses, physical_count, cognitive_count)
        
        return total_score
    
    def panic_attack_toolkit(self):
        """Emergency toolkit for panic attacks"""
        print("🚨 Panic Attack Emergency Toolkit")
        print("=" * 40)
        print("If you're having a panic attack right now, these techniques can help:")
        print()
        
        print("🫁 IMMEDIATE BREATHING TECHNIQUE:")
        print("1. Breathe in slowly through your nose for 4 counts")
        print("2. Hold your breath for 4 counts")
        print("3. Breathe out slowly through your mouth for 6 counts")
        print("4. Repeat until you feel calmer")
        print()
        
        # Guided breathing
        do_breathing = input("Would you like guided breathing now? (y/n): ").strip().lower()
        if do_breathing == 'y':
            self._guided_panic_breathing()
        
        print("\n🌍 GROUNDING TECHNIQUE:")
        print("Name out loud:")
        print("• 5 things you can see")
        print("• 4 things you can touch")
        print("• 3 things you can hear")
        print("• 2 things you can smell")
        print("• 1 thing you can taste")
        print()
        
        print("💭 PANIC ATTACK REMINDERS:")
        reminders = [
            "This is anxiety, not danger",
            "This feeling will pass",
            "I am safe right now",
            "I have survived this before",
            "My body is responding to false alarm",
            "I can handle this",
            "This will be over soon"
        ]
        
        for reminder in reminders:
            print(f"   • {reminder}")
        
        print()
        
        print("🏥 WHEN TO SEEK HELP:")
        print("• If this is your first panic attack")
        print("• If symptoms don't improve with techniques")
        print("• If you have chest pain or breathing difficulties")
        print("• If panic attacks are frequent or interfering with life")
        
        # Log panic attack
        self._log_panic_attack()
    
    def worry_time_technique(self):
        """Structured worry time technique"""
        print("⏰ Worry Time Technique")
        print("=" * 40)
        print("This technique helps contain worry to a specific time period.")
        print("Instead of worrying throughout the day, you schedule dedicated worry time.")
        print()
        
        # Set up worry time
        print("Let's set up your worry time:")
        duration = input("How long should your worry time be? (suggest 15-20 minutes): ").strip()
        if not duration:
            duration = "15 minutes"
        
        time_of_day = input("What time of day works best? (not close to bedtime): ").strip()
        if not time_of_day:
            time_of_day = "early evening"
        
        print(f"\n📅 Your worry time: {duration} at {time_of_day}")
        print()
        
        # Current worry session
        print("Let's do a worry session now:")
        print("Write down all your current worries. Don't try to solve them yet.")
        print()
        
        worries = []
        print("Enter your worries (press Enter twice when done):")
        
        while True:
            worry = input("Worry: ").strip()
            if not worry:
                break
            worries.append(worry)
        
        if not worries:
            print("No worries entered. That's okay!")
            return
        
        print(f"\nYou've listed {len(worries)} worries:")
        for i, worry in enumerate(worries, 1):
            print(f"{i}. {worry}")
        
        print()
        
        # Categorize worries
        print("Now let's categorize these worries:")
        actionable_worries = []
        hypothetical_worries = []
        
        for worry in worries:
            print(f"\nWorry: {worry}")
            category = input("Is this something you can take action on? (y/n): ").strip().lower()
            
            if category == 'y':
                actionable_worries.append(worry)
                action = input("What's one small action you could take? ").strip()
                print(f"Action noted: {action}")
            else:
                hypothetical_worries.append(worry)
                print("This is a hypothetical worry - noted for acceptance practice.")
        
        # Summary
        print(f"\n📊 Worry Analysis:")
        print(f"   Actionable worries: {len(actionable_worries)}")
        print(f"   Hypothetical worries: {len(hypothetical_worries)}")
        print()
        
        if actionable_worries:
            print("💪 For actionable worries: Focus on what you can control")
        
        if hypothetical_worries:
            print("🕊️ For hypothetical worries: Practice acceptance and letting go")
        
        print("\n📝 Worry Time Rules:")
        print("• When worries come up during the day, write them down for worry time")
        print("• Tell yourself 'I'll think about this during worry time'")
        print("• During worry time, focus only on the worries you've written down")
        print("• After worry time, engage in a pleasant activity")
        
        # Save worry session
        self._save_worry_session(worries, actionable_worries, hypothetical_worries, duration, time_of_day)
    
    def exposure_therapy_planner(self):
        """Plan gradual exposure exercises"""
        print("🎯 Exposure Therapy Planner")
        print("=" * 40)
        print("Gradual exposure helps reduce anxiety by slowly facing feared situations.")
        print("We'll create a step-by-step plan from least to most anxiety-provoking.")
        print()
        
        # Identify the fear
        fear = input("What situation or object causes you anxiety? ").strip()
        
        if not fear:
            print("Please describe what you'd like to work on.")
            return
        
        print(f"\nWorking on: {fear}")
        print()
        
        # Rate current anxiety
        current_anxiety = input("Rate your current anxiety about this (0-10): ").strip()
        
        try:
            current_anxiety = max(0, min(10, int(current_anxiety)))
        except ValueError:
            current_anxiety = 5
        
        print(f"Current anxiety level: {current_anxiety}/10")
        print()
        
        # Create exposure hierarchy
        print("Let's create an exposure hierarchy (from easiest to hardest):")
        print("Think of 5-7 steps, starting with something that causes mild anxiety.")
        print()
        
        hierarchy = []
        print("Enter exposure steps (press Enter twice when done):")
        
        step_num = 1
        while len(hierarchy) < 10:  # Max 10 steps
            step = input(f"Step {step_num}: ").strip()
            if not step:
                break
            
            # Rate anxiety for this step
            anxiety_rating = input(f"Anxiety level for this step (0-10): ").strip()
            
            try:
                anxiety_rating = max(0, min(10, int(anxiety_rating)))
            except ValueError:
                anxiety_rating = 5
            
            hierarchy.append({
                "step": step,
                "anxiety_rating": anxiety_rating,
                "completed": False
            })
            
            step_num += 1
            print()
        
        if not hierarchy:
            print("No steps entered.")
            return
        
        # Sort by anxiety rating
        hierarchy.sort(key=lambda x: x['anxiety_rating'])
        
        print("📋 Your Exposure Hierarchy:")
        for i, item in enumerate(hierarchy, 1):
            print(f"{i}. {item['step']} (Anxiety: {item['anxiety_rating']}/10)")
        
        print()
        
        # Plan first exposure
        print("🎯 Let's plan your first exposure:")
        first_step = hierarchy[0]
        print(f"First step: {first_step['step']}")
        print(f"Expected anxiety: {first_step['anxiety_rating']}/10")
        print()
        
        when = input("When will you try this first step? ").strip()
        duration = input("How long will you stay in the situation? ").strip()
        support = input("Do you need any support or preparation? ").strip()
        
        print(f"\n📅 Exposure Plan:")
        print(f"   Step: {first_step['step']}")
        print(f"   When: {when}")
        print(f"   Duration: {duration}")
        if support:
            print(f"   Support needed: {support}")
        
        print("\n💡 Exposure Tips:")
        print("• Stay in the situation until anxiety decreases by at least 50%")
        print("• Use breathing techniques if needed")
        print("• Don't use safety behaviors (things that reduce anxiety artificially)")
        print("• Record your experience afterward")
        print("• Move to the next step only after mastering the current one")
        
        # Save exposure plan
        self._save_exposure_plan(fear, hierarchy, current_anxiety)
    
    def anxiety_thought_challenging(self):
        """Challenge anxious thoughts"""
        print("🧠 Anxiety Thought Challenging")
        print("=" * 40)
        print("Anxiety often involves overestimating danger and underestimating our ability to cope.")
        print("Let's examine and challenge an anxious thought.")
        print()
        
        # Identify the anxious thought
        anxious_thought = input("What anxious thought is bothering you? ").strip()
        
        if not anxious_thought:
            print("Take your time. What worry or fear is on your mind?")
            anxious_thought = input("> ").strip()
        
        if not anxious_thought:
            print("It's okay if you can't identify a specific thought right now.")
            return
        
        print(f"\nAnxious thought: \"{anxious_thought}\"")
        print()
        
        # Rate belief and anxiety
        belief_rating = input("How much do you believe this thought? (0-100%): ").strip()
        anxiety_rating = input("How anxious does this thought make you? (0-10): ").strip()
        
        try:
            belief_rating = max(0, min(100, int(belief_rating.replace('%', ''))))
            anxiety_rating = max(0, min(10, int(anxiety_rating)))
        except ValueError:
            belief_rating = 50
            anxiety_rating = 5
        
        print(f"Belief: {belief_rating}%")
        print(f"Anxiety: {anxiety_rating}/10")
        print()
        
        # Thought challenging questions
        print("Let's challenge this thought with some questions:")
        
        questions = [
            "What evidence supports this thought?",
            "What evidence contradicts this thought?",
            "What's the worst that could realistically happen?",
            "How likely is this worst-case scenario? (0-100%)",
            "If it did happen, how would you cope?",
            "What would you tell a friend having this thought?",
            "Are you overestimating the danger?",
            "Are you underestimating your ability to cope?",
            "What's a more balanced way to think about this?"
        ]
        
        responses = []
        for question in questions:
            print(f"\n❓ {question}")
            response = input("   ").strip()
            responses.append(response)
        
        # Create balanced thought
        print("\nBased on your responses, create a more balanced thought:")
        balanced_thought = input("> ").strip()
        
        # Re-rate belief and anxiety
        new_belief = input("How much do you believe the original thought now? (0-100%): ").strip()
        new_anxiety = input("How anxious do you feel now? (0-10): ").strip()
        
        try:
            new_belief = max(0, min(100, int(new_belief.replace('%', ''))))
            new_anxiety = max(0, min(10, int(new_anxiety)))
        except ValueError:
            new_belief = belief_rating
            new_anxiety = anxiety_rating
        
        # Summary
        print(f"\n📊 Thought Challenging Results:")
        print(f"   Original thought: \"{anxious_thought}\"")
        print(f"   Balanced thought: \"{balanced_thought}\"")
        print(f"   Belief: {belief_rating}% → {new_belief}%")
        print(f"   Anxiety: {anxiety_rating}/10 → {new_anxiety}/10")
        
        if new_belief < belief_rating or new_anxiety < anxiety_rating:
            print("   Great! Your belief in the anxious thought decreased.")
        
        # Save thought challenge
        self._save_thought_challenge(anxious_thought, balanced_thought, belief_rating, 
                                   new_belief, anxiety_rating, new_anxiety)
    
    def _guided_panic_breathing(self):
        """Guided breathing for panic attacks"""
        print("\n🫁 Guided Panic Breathing")
        print("Follow along with this breathing pattern:")
        print()
        
        for round_num in range(5):
            print(f"Round {round_num + 1}/5")
            
            # Inhale
            print("Breathe IN through your nose... 1", end="", flush=True)
            time.sleep(1)
            print("...2", end="", flush=True)
            time.sleep(1)
            print("...3", end="", flush=True)
            time.sleep(1)
            print("...4", end="", flush=True)
            time.sleep(1)
            
            # Hold
            print(" | HOLD... 1", end="", flush=True)
            time.sleep(1)
            print("...2", end="", flush=True)
            time.sleep(1)
            print("...3", end="", flush=True)
            time.sleep(1)
            print("...4", end="", flush=True)
            time.sleep(1)
            
            # Exhale
            print(" | Breathe OUT through your mouth... 1", end="", flush=True)
            time.sleep(1)
            print("...2", end="", flush=True)
            time.sleep(1)
            print("...3", end="", flush=True)
            time.sleep(1)
            print("...4", end="", flush=True)
            time.sleep(1)
            print("...5", end="", flush=True)
            time.sleep(1)
            print("...6")
            time.sleep(1)
            print()
        
        print("✨ Good job! How do you feel now?")
        feeling = input("Rate your anxiety now (0-10): ").strip()
        
        try:
            feeling = int(feeling)
            print(f"You rated your anxiety as {feeling}/10")
            if feeling < 7:
                print("Great! The breathing helped reduce your anxiety.")
        except ValueError:
            pass
    
    def _interpret_anxiety_assessment(self, total_score: int, physical_count: int, cognitive_count: int):
        """Interpret anxiety assessment results"""
        print(f"📊 Assessment Results:")
        print(f"Anxiety questionnaire score: {total_score}/21")
        print(f"Physical symptoms: {physical_count}/{len(self.physical_symptoms)}")
        print(f"Cognitive symptoms: {cognitive_count}/{len(self.cognitive_symptoms)}")
        print()
        
        if total_score <= 4:
            severity = "Minimal"
            recommendation = "Your anxiety symptoms appear minimal. Continue with self-care."
        elif total_score <= 9:
            severity = "Mild"
            recommendation = "You may be experiencing mild anxiety. Self-help strategies may be beneficial."
        elif total_score <= 14:
            severity = "Moderate"
            recommendation = "You may be experiencing moderate anxiety. Consider professional support."
        else:
            severity = "Severe"
            recommendation = "You may be experiencing severe anxiety. Professional help is strongly recommended."
        
        print(f"Severity level: {severity}")
        print(f"Recommendation: {recommendation}")
        print()
        
        # Suggest appropriate techniques
        if total_score <= 9:
            print("💡 Suggested techniques: Relaxation, worry time, thought challenging")
        else:
            print("💡 Suggested techniques: Panic toolkit, grounding, professional support")
        
        print("\nNote: This is not a diagnostic tool. Consult a healthcare provider for proper evaluation.")
    
    def _log_panic_attack(self):
        """Log panic attack occurrence"""
        data = self._load_anxiety_data()
        
        # Get details about the panic attack
        print("\nOptional: Log details about this panic attack")
        triggers = input("What might have triggered this? (optional): ").strip()
        duration = input("How long did it last? (optional): ").strip()
        techniques_used = input("What techniques did you use? (optional): ").strip()
        
        panic_log = {
            "timestamp": datetime.now().isoformat(),
            "triggers": triggers,
            "duration": duration,
            "techniques_used": techniques_used
        }
        
        data.setdefault('panic_attacks', []).append(panic_log)
        self._save_anxiety_data(data)
        
        print("✅ Panic attack logged. This information can help identify patterns.")
    
    def _save_anxiety_assessment(self, total_score: int, responses: List[int], 
                               physical_count: int, cognitive_count: int):
        """Save anxiety assessment results"""
        data = self._load_anxiety_data()
        
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "total_score": total_score,
            "responses": responses,
            "physical_symptoms": physical_count,
            "cognitive_symptoms": cognitive_count
        }
        
        data.setdefault('assessments', []).append(assessment)
        self._save_anxiety_data(data)
    
    def _save_worry_session(self, worries: List[str], actionable: List[str], 
                          hypothetical: List[str], duration: str, time_of_day: str):
        """Save worry time session"""
        data = self._load_anxiety_data()
        
        worry_session = {
            "timestamp": datetime.now().isoformat(),
            "worries": worries,
            "actionable_worries": actionable,
            "hypothetical_worries": hypothetical,
            "duration": duration,
            "time_of_day": time_of_day
        }
        
        data.setdefault('worry_sessions', []).append(worry_session)
        self._save_anxiety_data(data)
    
    def _save_exposure_plan(self, fear: str, hierarchy: List[Dict], current_anxiety: int):
        """Save exposure therapy plan"""
        data = self._load_anxiety_data()
        
        exposure_plan = {
            "timestamp": datetime.now().isoformat(),
            "fear": fear,
            "hierarchy": hierarchy,
            "current_anxiety": current_anxiety
        }
        
        data.setdefault('exposure_plans', []).append(exposure_plan)
        self._save_anxiety_data(data)
    
    def _save_thought_challenge(self, anxious_thought: str, balanced_thought: str,
                              belief_before: int, belief_after: int,
                              anxiety_before: int, anxiety_after: int):
        """Save thought challenging session"""
        data = self._load_anxiety_data()
        
        thought_challenge = {
            "timestamp": datetime.now().isoformat(),
            "anxious_thought": anxious_thought,
            "balanced_thought": balanced_thought,
            "belief_before": belief_before,
            "belief_after": belief_after,
            "anxiety_before": anxiety_before,
            "anxiety_after": anxiety_after
        }
        
        data.setdefault('thought_challenges', []).append(thought_challenge)
        self._save_anxiety_data(data)
    
    def _load_anxiety_data(self) -> Dict:
        """Load anxiety support data"""
        if not os.path.exists(ANXIETY_FILE):
            return {}
        
        try:
            with open(ANXIETY_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_anxiety_data(self, data: Dict):
        """Save anxiety support data"""
        try:
            with open(ANXIETY_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save anxiety data: {e}")


def anxiety_command(action: str = "menu", **kwargs):
    """Main anxiety support command interface"""
    support = AnxietySupport()
    
    if action == "menu":
        print("😰 Anxiety Support Menu")
        print("=" * 40)
        print("1. Anxiety assessment")
        print("2. Panic attack toolkit")
        print("3. Worry time technique")
        print("4. Exposure therapy planner")
        print("5. Thought challenging")
        print()
        
        choice = input("Choose an option (1-5): ").strip()
        
        if choice == "1":
            support.anxiety_assessment()
        elif choice == "2":
            support.panic_attack_toolkit()
        elif choice == "3":
            support.worry_time_technique()
        elif choice == "4":
            support.exposure_therapy_planner()
        elif choice == "5":
            support.anxiety_thought_challenging()
        else:
            print("Invalid choice.")
    
    elif action == "assessment":
        support.anxiety_assessment()
    elif action == "panic":
        support.panic_attack_toolkit()
    elif action == "worry":
        support.worry_time_technique()
    elif action == "exposure":
        support.exposure_therapy_planner()
    elif action == "thoughts":
        support.anxiety_thought_challenging()
    else:
        print(f"Unknown anxiety action: {action}")
        print("Available actions: menu, assessment, panic, worry, exposure, thoughts")
