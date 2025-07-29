"""
Neurowave Stimulation module for om - inspired by Hypnomatic
Brainwave entrainment and binaural beats for consciousness alteration
"""

import time
import json
import os
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple

NEUROWAVE_FILE = os.path.expanduser("~/.om_neurowave.json")

class NeurowaveStimulation:
    def __init__(self):
        # Brainwave frequency ranges (Hz)
        self.brainwave_types = {
            "delta": {
                "range": (0.5, 4),
                "description": "Deep sleep, healing, regeneration",
                "benefits": ["Deep sleep", "Physical healing", "Growth hormone release", "Immune system boost"],
                "best_for": ["Insomnia", "Recovery", "Deep meditation", "Pain relief"],
                "duration": "30-60 minutes",
                "time_of_day": "Evening/Night"
            },
            "theta": {
                "range": (4, 8),
                "description": "Deep meditation, creativity, memory",
                "benefits": ["Enhanced creativity", "Deep meditation", "Memory consolidation", "Emotional healing"],
                "best_for": ["Meditation", "Creative work", "Trauma healing", "Learning"],
                "duration": "20-45 minutes", 
                "time_of_day": "Morning/Evening"
            },
            "alpha": {
                "range": (8, 13),
                "description": "Relaxed awareness, learning, flow states",
                "benefits": ["Relaxation", "Improved learning", "Stress reduction", "Flow states"],
                "best_for": ["Study", "Relaxation", "Light meditation", "Stress relief"],
                "duration": "15-30 minutes",
                "time_of_day": "Anytime"
            },
            "beta": {
                "range": (13, 30),
                "description": "Alert consciousness, focus, problem-solving",
                "benefits": ["Enhanced focus", "Alertness", "Problem-solving", "Cognitive performance"],
                "best_for": ["Work", "Study", "Mental tasks", "Concentration"],
                "duration": "15-45 minutes",
                "time_of_day": "Morning/Afternoon"
            },
            "gamma": {
                "range": (30, 100),
                "description": "Higher consciousness, insight, peak performance",
                "benefits": ["Peak awareness", "Insight", "Binding consciousness", "Spiritual experiences"],
                "best_for": ["Advanced meditation", "Peak performance", "Insight work", "Consciousness exploration"],
                "duration": "10-20 minutes",
                "time_of_day": "Morning"
            }
        }
        
        # Specific frequency protocols
        self.frequency_protocols = {
            # Relaxation & Stress Relief
            "deep_relaxation": {
                "name": "Deep Relaxation Protocol",
                "frequencies": [(10, 8), (8, 6), (6, 4)],  # Alpha to Theta to Delta
                "duration_per_stage": 10,
                "total_duration": 30,
                "description": "Progressive relaxation from alert to deep rest"
            },
            "stress_relief": {
                "name": "Stress Relief Protocol", 
                "frequencies": [(12, 10), (10, 8)],  # Beta to Alpha
                "duration_per_stage": 15,
                "total_duration": 30,
                "description": "Reduce stress and promote calm alertness"
            },
            
            # Focus & Cognitive Enhancement
            "focus_enhancement": {
                "name": "Focus Enhancement Protocol",
                "frequencies": [(10, 15), (15, 20), (20, 15)],  # Alpha to Beta and back
                "duration_per_stage": 10,
                "total_duration": 30,
                "description": "Enhance concentration and mental clarity"
            },
            "cognitive_boost": {
                "name": "Cognitive Performance Boost",
                "frequencies": [(15, 18), (18, 22), (22, 25)],  # Progressive Beta increase
                "duration_per_stage": 8,
                "total_duration": 24,
                "description": "Optimize cognitive performance and alertness"
            },
            
            # Creativity & Insight
            "creative_flow": {
                "name": "Creative Flow State",
                "frequencies": [(8, 6), (6, 7), (7, 8)],  # Theta variations
                "duration_per_stage": 12,
                "total_duration": 36,
                "description": "Access creative insights and flow states"
            },
            "insight_meditation": {
                "name": "Insight Meditation Protocol",
                "frequencies": [(8, 6), (6, 4), (4, 40)],  # Theta to Delta to Gamma
                "duration_per_stage": 15,
                "total_duration": 45,
                "description": "Deep meditation with insight activation"
            },
            
            # Sleep & Recovery
            "sleep_induction": {
                "name": "Natural Sleep Induction",
                "frequencies": [(10, 8), (8, 6), (6, 4), (4, 2)],  # Progressive to deep sleep
                "duration_per_stage": 12,
                "total_duration": 48,
                "description": "Gentle transition to deep, restorative sleep"
            },
            "power_nap": {
                "name": "20-Minute Power Nap",
                "frequencies": [(8, 6), (6, 4), (4, 6), (6, 8)],  # Down and back up
                "duration_per_stage": 5,
                "total_duration": 20,
                "description": "Refreshing power nap with natural awakening"
            },
            
            # Advanced Protocols
            "consciousness_expansion": {
                "name": "Consciousness Expansion",
                "frequencies": [(8, 6), (6, 40), (40, 60), (60, 40)],  # Theta to Gamma
                "duration_per_stage": 10,
                "total_duration": 40,
                "description": "Advanced protocol for consciousness exploration"
            },
            "healing_frequencies": {
                "name": "Healing & Recovery Protocol",
                "frequencies": [(7.83, 7.83), (528, 528), (4, 4)],  # Schumann, Solfeggio, Delta
                "duration_per_stage": 15,
                "total_duration": 45,
                "description": "Frequencies associated with healing and recovery"
            }
        }
        
        # Safety guidelines for neurowave stimulation
        self.safety_guidelines = [
            "Start with shorter sessions (10-15 minutes) and gradually increase",
            "Do not use if you have epilepsy or seizure disorders",
            "Avoid use if pregnant without medical consultation",
            "Stop immediately if you experience dizziness or discomfort",
            "Do not use while driving or operating machinery",
            "Not recommended for children under 16",
            "Consult healthcare provider if you have neurological conditions"
        ]
    
    def show_neurowave_menu(self):
        """Display neurowave stimulation options"""
        print("🧠 Neurowave Stimulation & Brainwave Entrainment")
        print("=" * 70)
        print("Advanced brainwave entrainment protocols for consciousness optimization")
        print("Based on neuroscience research and binaural beat technology")
        print()
        
        print("🌊 Available Brainwave Types:")
        for wave_type, info in self.brainwave_types.items():
            freq_range = f"{info['range'][0]}-{info['range'][1]} Hz"
            print(f"   {wave_type.upper()}: {freq_range} - {info['description']}")
        print()
        
        print("🎯 Specialized Protocols:")
        protocols = list(self.frequency_protocols.keys())
        for i, protocol_id in enumerate(protocols, 1):
            protocol = self.frequency_protocols[protocol_id]
            print(f"   {i}. {protocol['name']} ({protocol['total_duration']} min)")
            print(f"      {protocol['description']}")
        print()
        
        # Show usage statistics
        self._show_neurowave_stats()
        
        print("⚠️  Important Safety Information:")
        print("• These protocols use simulated brainwave entrainment")
        print("• Not suitable for epilepsy or seizure disorders")
        print("• Start with shorter sessions and build up gradually")
        print("• Stop if you experience any discomfort")
        print()
        
        choice = input(f"Choose a protocol (1-{len(protocols)}) or 'info' for brainwave info: ").strip().lower()
        
        if choice == 'info':
            self._show_brainwave_info()
        elif choice.isdigit():
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(protocols):
                    protocol_id = protocols[choice_idx]
                    self._start_neurowave_protocol(protocol_id)
            except ValueError:
                pass
    
    def _show_brainwave_info(self):
        """Show detailed brainwave information"""
        print("\n🧠 Brainwave Types - Detailed Information")
        print("=" * 60)
        
        for wave_type, info in self.brainwave_types.items():
            print(f"🌊 {wave_type.upper()} WAVES ({info['range'][0]}-{info['range'][1]} Hz)")
            print(f"Description: {info['description']}")
            print(f"Best time: {info['time_of_day']}")
            print(f"Recommended duration: {info['duration']}")
            print()
            
            print("Benefits:")
            for benefit in info['benefits']:
                print(f"   • {benefit}")
            print()
            
            print("Best for:")
            for use_case in info['best_for']:
                print(f"   • {use_case}")
            print()
            print("-" * 50)
        
        input("\nPress Enter to return to the main menu...")
        self.show_neurowave_menu()
    
    def _start_neurowave_protocol(self, protocol_id: str):
        """Start a neurowave stimulation protocol"""
        if protocol_id not in self.frequency_protocols:
            print(f"Protocol '{protocol_id}' not found.")
            return
        
        protocol = self.frequency_protocols[protocol_id]
        
        print(f"\n🧠 {protocol['name']}")
        print("=" * 50)
        print(f"Description: {protocol['description']}")
        print(f"Total Duration: {protocol['total_duration']} minutes")
        print(f"Stages: {len(protocol['frequencies'])}")
        print()
        
        # Show protocol stages
        print("📋 Protocol Stages:")
        for i, (start_freq, end_freq) in enumerate(protocol['frequencies'], 1):
            duration = protocol['duration_per_stage']
            if start_freq == end_freq:
                print(f"   Stage {i}: {start_freq} Hz for {duration} minutes")
            else:
                print(f"   Stage {i}: {start_freq} Hz → {end_freq} Hz over {duration} minutes")
        print()
        
        # Safety confirmation
        print("🛡️  Safety Confirmation:")
        print("Before starting, please confirm:")
        print("• You do not have epilepsy or seizure disorders")
        print("• You are in a safe, comfortable environment")
        print("• You will not be driving or operating machinery")
        print("• You understand this is for wellness, not medical treatment")
        print()
        
        consent = input("Do you confirm the above and wish to proceed? (y/n): ").strip().lower()
        
        if consent == 'y':
            self._execute_neurowave_protocol(protocol_id, protocol)
        else:
            print("Protocol cancelled. Your safety is our priority.")
    
    def _execute_neurowave_protocol(self, protocol_id: str, protocol: Dict):
        """Execute the neurowave stimulation protocol"""
        print(f"\n🧠 Executing: {protocol['name']}")
        print("=" * 50)
        
        # Preparation
        print("🧘‍♀️ Preparation:")
        print("• Find a comfortable position")
        print("• Close your eyes or use an eye mask")
        print("• Use headphones for optimal effect (if available)")
        print("• Focus on your breathing and relax")
        print()
        
        input("Press Enter when ready to begin the protocol...")
        print()
        
        # Execute each stage
        total_stages = len(protocol['frequencies'])
        
        for stage_num, (start_freq, end_freq) in enumerate(protocol['frequencies'], 1):
            duration = protocol['duration_per_stage']
            
            print(f"🌊 Stage {stage_num}/{total_stages}")
            
            if start_freq == end_freq:
                print(f"   Frequency: {start_freq} Hz")
                print(f"   Duration: {duration} minutes")
                print(f"   Effect: {self._get_frequency_effect(start_freq)}")
            else:
                print(f"   Frequency sweep: {start_freq} Hz → {end_freq} Hz")
                print(f"   Duration: {duration} minutes")
                print(f"   Effect: Transitioning from {self._get_frequency_effect(start_freq)} to {self._get_frequency_effect(end_freq)}")
            
            print()
            
            # Simulate the frequency progression
            self._simulate_frequency_stage(start_freq, end_freq, duration)
            
            if stage_num < total_stages:
                print("   Transitioning to next stage...")
                time.sleep(2)
                print()
        
        # Completion
        self._complete_neurowave_session(protocol_id, protocol)
    
    def _simulate_frequency_stage(self, start_freq: float, end_freq: float, duration_minutes: int):
        """Simulate a frequency stage with visual feedback"""
        total_seconds = duration_minutes * 60
        update_interval = 30  # Update every 30 seconds
        updates = total_seconds // update_interval
        
        for update in range(updates):
            # Calculate current frequency
            progress = update / updates
            current_freq = start_freq + (end_freq - start_freq) * progress
            
            # Show progress
            elapsed_minutes = (update * update_interval) // 60
            remaining_minutes = duration_minutes - elapsed_minutes
            
            print(f"   🎵 Current frequency: {current_freq:.1f} Hz | "
                  f"Elapsed: {elapsed_minutes}m | Remaining: {remaining_minutes}m")
            
            # Visual representation of brainwave activity
            wave_intensity = self._calculate_wave_intensity(current_freq)
            wave_visual = "~" * wave_intensity
            print(f"   🧠 Brainwave activity: {wave_visual}")
            
            # Guidance based on frequency
            guidance = self._get_frequency_guidance(current_freq)
            if guidance and update % 2 == 0:  # Show guidance every other update
                print(f"   💭 {guidance}")
            
            print()
            
            # Wait for next update (shortened for demo)
            time.sleep(2)  # In real implementation, this would be update_interval
        
        print(f"   ✅ Stage complete - {duration_minutes} minutes at {start_freq}-{end_freq} Hz")
        print()
    
    def _calculate_wave_intensity(self, frequency: float) -> int:
        """Calculate visual intensity based on frequency"""
        if frequency <= 4:  # Delta
            return 2
        elif frequency <= 8:  # Theta
            return 4
        elif frequency <= 13:  # Alpha
            return 6
        elif frequency <= 30:  # Beta
            return 8
        else:  # Gamma
            return 10
    
    def _get_frequency_effect(self, frequency: float) -> str:
        """Get the expected effect of a frequency"""
        if frequency <= 4:
            return "Deep relaxation/sleep"
        elif frequency <= 8:
            return "Deep meditation/creativity"
        elif frequency <= 13:
            return "Relaxed awareness/learning"
        elif frequency <= 30:
            return "Alert focus/concentration"
        else:
            return "Peak awareness/insight"
    
    def _get_frequency_guidance(self, frequency: float) -> Optional[str]:
        """Get guidance for the current frequency"""
        guidance_map = {
            (0, 4): "Allow yourself to drift into deep relaxation... let go completely...",
            (4, 8): "Notice creative insights arising... stay open to new ideas...",
            (8, 13): "Feel calm and alert... perfect for learning and reflection...",
            (13, 30): "Your mind is sharp and focused... excellent for mental tasks...",
            (30, 100): "Experience heightened awareness... notice expanded consciousness..."
        }
        
        for (low, high), message in guidance_map.items():
            if low <= frequency <= high:
                return message
        return None
    
    def _complete_neurowave_session(self, protocol_id: str, protocol: Dict):
        """Complete the neurowave session with feedback"""
        print("🌟 Neurowave Protocol Complete")
        print("=" * 40)
        
        print(f"You've completed: {protocol['name']}")
        print(f"Total duration: {protocol['total_duration']} minutes")
        print(f"Stages completed: {len(protocol['frequencies'])}")
        print()
        
        # Feedback collection
        print("💭 Post-session feedback:")
        
        mental_state = input("How do you feel mentally? (1-10, 10=excellent): ").strip()
        alertness = input("Rate your alertness level (1-10): ").strip()
        overall_experience = input("Rate the overall experience (1-10): ").strip()
        
        try:
            mental_state = max(1, min(10, int(mental_state)))
            alertness = max(1, min(10, int(alertness)))
            overall_experience = max(1, min(10, int(overall_experience)))
        except ValueError:
            mental_state = alertness = overall_experience = None
        
        effects_noticed = input("What effects did you notice? (optional): ").strip()
        
        # Integration advice
        print(f"\n💡 Integration Advice:")
        integration_tips = self._get_integration_advice(protocol_id)
        for tip in integration_tips:
            print(f"   • {tip}")
        
        # Save session data
        self._save_neurowave_session(protocol_id, protocol, mental_state, alertness, 
                                   overall_experience, effects_noticed)
        
        print("\n🧠 Thank you for exploring consciousness with neurowave stimulation!")
        print("Regular practice can lead to lasting improvements in mental performance.")
    
    def _get_integration_advice(self, protocol_id: str) -> List[str]:
        """Get integration advice for specific protocols"""
        advice_map = {
            "deep_relaxation": [
                "Use this relaxed state for meditation or creative work",
                "Notice how relaxation affects your stress levels throughout the day",
                "Practice this protocol regularly for cumulative benefits"
            ],
            "focus_enhancement": [
                "Apply this enhanced focus to important tasks immediately",
                "Notice improved concentration and mental clarity",
                "Use before studying or important work sessions"
            ],
            "creative_flow": [
                "Engage in creative activities while in this state",
                "Keep a notebook handy for capturing insights",
                "Don't judge ideas - let creativity flow freely"
            ],
            "sleep_induction": [
                "Allow yourself to drift into natural sleep",
                "Maintain a consistent sleep schedule",
                "Create a peaceful sleep environment"
            ]
        }
        
        return advice_map.get(protocol_id, [
            "Notice the effects of this protocol on your mental state",
            "Practice regularly for cumulative benefits",
            "Integrate insights into your daily life"
        ])
    
    def _show_neurowave_stats(self):
        """Show neurowave usage statistics"""
        data = self._load_neurowave_data()
        sessions = data.get('sessions', [])
        
        if not sessions:
            return
        
        print("📊 Your Neurowave Journey:")
        
        # Recent sessions
        recent = sessions[-3:]
        print("Recent sessions:")
        for session in recent:
            date = datetime.fromisoformat(session['timestamp']).strftime("%m-%d")
            protocol_name = self.frequency_protocols.get(session['protocol_id'], {}).get('name', session['protocol_id'])
            rating = session.get('overall_experience', 'N/A')
            print(f"   {date}: {protocol_name} (Rating: {rating}/10)")
        
        # Statistics
        total_sessions = len(sessions)
        total_minutes = sum(self.frequency_protocols.get(s['protocol_id'], {}).get('total_duration', 0) for s in sessions)
        
        print(f"\nTotal sessions: {total_sessions}")
        print(f"Total stimulation time: {total_minutes} minutes ({total_minutes//60}h {total_minutes%60}m)")
        
        # Most used protocol
        protocol_counts = {}
        for session in sessions:
            protocol_id = session['protocol_id']
            protocol_counts[protocol_id] = protocol_counts.get(protocol_id, 0) + 1
        
        if protocol_counts:
            most_used = max(protocol_counts.items(), key=lambda x: x[1])
            protocol_name = self.frequency_protocols.get(most_used[0], {}).get('name', most_used[0])
            print(f"Most used protocol: {protocol_name} ({most_used[1]} times)")
        
        print()
    
    def show_neurowave_history(self):
        """Show detailed neurowave session history"""
        data = self._load_neurowave_data()
        sessions = data.get('sessions', [])
        
        if not sessions:
            print("📊 Neurowave Session History")
            print("=" * 40)
            print("No neurowave sessions completed yet.")
            print("Start your brainwave entrainment journey with 'om neurowave'!")
            return
        
        print("📊 Neurowave Stimulation History")
        print("=" * 50)
        
        for session in sessions[-10:]:  # Show last 10 sessions
            date = datetime.fromisoformat(session['timestamp']).strftime("%Y-%m-%d %H:%M")
            protocol_name = self.frequency_protocols.get(session['protocol_id'], {}).get('name', session['protocol_id'])
            
            print(f"🧠 {date}: {protocol_name}")
            
            if session.get('mental_state'):
                print(f"   Mental state: {session['mental_state']}/10")
            if session.get('alertness'):
                print(f"   Alertness: {session['alertness']}/10")
            if session.get('overall_experience'):
                print(f"   Experience: {session['overall_experience']}/10")
            if session.get('effects_noticed'):
                print(f"   Effects: {session['effects_noticed']}")
            print()
        
        # Overall statistics
        total_sessions = len(sessions)
        avg_experience = None
        experience_ratings = [s.get('overall_experience') for s in sessions if s.get('overall_experience')]
        if experience_ratings:
            avg_experience = sum(experience_ratings) / len(experience_ratings)
        
        print("📈 Overall Statistics:")
        print(f"   Total sessions: {total_sessions}")
        if avg_experience:
            print(f"   Average experience rating: {avg_experience:.1f}/10")
        
        print("\n🧠 Neurowave stimulation works through neuroplasticity.")
        print("   Consistent practice leads to lasting improvements in brain function.")
    
    def _save_neurowave_session(self, protocol_id: str, protocol: Dict, mental_state: Optional[int],
                               alertness: Optional[int], overall_experience: Optional[int], effects_noticed: str):
        """Save neurowave session data"""
        data = self._load_neurowave_data()
        
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "protocol_id": protocol_id,
            "protocol_name": protocol['name'],
            "duration": protocol['total_duration'],
            "mental_state": mental_state,
            "alertness": alertness,
            "overall_experience": overall_experience,
            "effects_noticed": effects_noticed
        }
        
        data.setdefault('sessions', []).append(session_data)
        self._save_neurowave_data(data)
    
    def _load_neurowave_data(self) -> Dict:
        """Load neurowave session data"""
        if not os.path.exists(NEUROWAVE_FILE):
            return {}
        
        try:
            with open(NEUROWAVE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_neurowave_data(self, data: Dict):
        """Save neurowave session data"""
        try:
            with open(NEUROWAVE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save neurowave data: {e}")


def neurowave_command(action: str = "menu", **kwargs):
    """Main neurowave stimulation command interface"""
    neurowave = NeurowaveStimulation()
    
    if action == "menu":
        neurowave.show_neurowave_menu()
    elif action == "history":
        neurowave.show_neurowave_history()
    elif action == "info":
        neurowave._show_brainwave_info()
    elif action == "protocol":
        protocol_id = kwargs.get('protocol')
        if protocol_id and protocol_id in neurowave.frequency_protocols:
            neurowave._start_neurowave_protocol(protocol_id)
        else:
            print(f"Unknown protocol: {protocol_id}")
            print(f"Available protocols: {', '.join(neurowave.frequency_protocols.keys())}")
    else:
        print(f"Unknown neurowave action: {action}")
        print("Available actions: menu, history, info, protocol")
