#!/usr/bin/env python3
"""
om - Unified Mental Health CLI Platform
Complete integration of all features with correct function imports
"""

import sys
import os
import argparse
from datetime import datetime
import json

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# Import visual command support
VISUAL_SUPPORT = False
try:
    from modules.visual_achievements import handle_visual_command
    VISUAL_SUPPORT = True
    print("✨ Visual/TUI support enabled")
except ImportError as e:
    print("📝 Running in text-only mode")
    def handle_visual_command(command, args):
        return False
except Exception as e:
    print("📝 Running in text-only mode (visual module error)")
    def handle_visual_command(command, args):
        return False

# Import ASCII art utilities
try:
    from modules.ascii_art import *
    ASCII_AVAILABLE = True
except ImportError:
    ASCII_AVAILABLE = False

# Available modules and their actual command functions
AVAILABLE_MODULES = {}

def safe_import(module_name, function_name):
    """Safely import modules and track availability"""
    try:
        module = __import__(module_name)
        if hasattr(module, function_name):
            AVAILABLE_MODULES[module_name] = getattr(module, function_name)
            return True
        else:
            return False
    except ImportError:
        return False
    except Exception:
        return False

def safe_import_with_wrapper(module_name, main_function, wrapper_function):
    """Import module and create a wrapper function"""
    try:
        module = __import__(module_name)
        if hasattr(module, main_function):
            AVAILABLE_MODULES[module_name] = wrapper_function(module, main_function)
            return True
        else:
            return False
    except ImportError:
        return False
    except Exception:
        return False

# Wrapper functions for existing modules
def create_mood_wrapper(module, function_name):
    def wrapper(args=None):
        if not args:
            # Default mood logging
            module.mood_command("log")
        elif args[0] == "trends":
            tracker = module.MoodTracker()
            tracker.show_mood_trends()
        elif args[0] == "suggest":
            tracker = module.MoodTracker()
            tracker.suggest_moods()
        else:
            module.mood_command(args[0] if args else "log")
    return wrapper

def create_breathing_wrapper(module, function_name):
    def wrapper(args=None):
        technique = "4-7-8"
        duration = 5
        
        if args:
            if "--technique" in args:
                idx = args.index("--technique")
                if idx + 1 < len(args):
                    technique = args[idx + 1]
            if "--duration" in args:
                idx = args.index("--duration")
                if idx + 1 < len(args):
                    try:
                        duration = int(args[idx + 1])
                    except ValueError:
                        duration = 5
        
        module.breathing_session(technique, duration)
    return wrapper

def create_gratitude_wrapper(module, function_name):
    def wrapper(args=None):
        entries = 3
        
        if args:
            if "--entries" in args:
                idx = args.index("--entries")
                if idx + 1 < len(args):
                    try:
                        entries = int(args[idx + 1])
                    except ValueError:
                        entries = 3
            elif args[0] == "history":
                module.show_gratitude_history()
                return
        
        module.gratitude_practice(entries)
    return wrapper

def create_meditation_wrapper(module, function_name):
    def wrapper(args=None):
        meditation_type = "mindfulness"
        duration = 10
        
        if args:
            if "--type" in args:
                idx = args.index("--type")
                if idx + 1 < len(args):
                    meditation_type = args[idx + 1]
            if "--duration" in args:
                idx = args.index("--duration")
                if idx + 1 < len(args):
                    try:
                        duration = int(args[idx + 1])
                    except ValueError:
                        duration = 10
        
        if hasattr(module, 'meditation_session'):
            module.meditation_session(meditation_type, duration)
        else:
            print(f"🧘 Starting {meditation_type} meditation for {duration} minutes...")
            print("Focus on your breath and let thoughts pass by like clouds.")
    return wrapper

def create_sleep_sounds_wrapper(module, function_name):
    def wrapper(args=None, action=None):
        # Save original sys.argv
        original_argv = sys.argv.copy()
        
        try:
            # Handle different calling patterns
            if action and action != "menu":
                # Called with action parameter from run_module
                sys.argv = ['sleep_sounds.py', action]
            elif args:
                # Called with args list
                if isinstance(args, list) and len(args) > 0:
                    sys.argv = ['sleep_sounds.py'] + args
                else:
                    sys.argv = ['sleep_sounds.py', 'categories']
            else:
                # Default to categories
                sys.argv = ['sleep_sounds.py', 'categories']
            
            module.main()
        finally:
            # Restore original sys.argv
            sys.argv = original_argv
    return wrapper

def create_affirmations_wrapper(module, function_name):
    def wrapper(args=None, action=None):
        # Save original sys.argv
        original_argv = sys.argv.copy()
        
        try:
            # Handle different calling patterns
            if action and action != "menu":
                # Called with action parameter from run_module
                sys.argv = ['affirmations.py', action]
            elif args:
                # Called with args list
                if isinstance(args, list) and len(args) > 0:
                    sys.argv = ['affirmations.py'] + args
                else:
                    sys.argv = ['affirmations.py', 'daily']
            else:
                # Default to daily affirmation
                sys.argv = ['affirmations.py', 'daily']
            
            module.main()
        finally:
            # Restore original sys.argv
            sys.argv = original_argv
    return wrapper

def create_classifier_wrapper(module, function_name):
    def wrapper(args=None, action=None):
        # Save original sys.argv
        original_argv = sys.argv.copy()
        
        try:
            # Handle different calling patterns
            if action and action != "menu":
                # Called with action parameter from run_module
                if action == "interactive":
                    sys.argv = ['mental_health_classifier.py', 'interactive']
                else:
                    # Treat action as the text to classify
                    sys.argv = ['mental_health_classifier.py', 'classify', action]
            elif args:
                # Called with args list
                if isinstance(args, list) and len(args) > 0:
                    if args[0] in ['classify', 'history', 'stats', 'interactive', 'test']:
                        sys.argv = ['mental_health_classifier.py'] + args
                    else:
                        # Treat first arg as text to classify
                        sys.argv = ['mental_health_classifier.py', 'classify'] + args
                else:
                    sys.argv = ['mental_health_classifier.py', 'interactive']
            else:
                # Default to interactive mode
                sys.argv = ['mental_health_classifier.py', 'interactive']
            
            module.main()
        finally:
            # Restore original sys.argv
            sys.argv = original_argv
    return wrapper

def create_physical_wrapper(module, function_name):
    def wrapper(args=None):
        focus = "all"
        
        if args and "--focus" in args:
            idx = args.index("--focus")
            if idx + 1 < len(args):
                focus = args[idx + 1]
        
        if hasattr(module, 'physical_exercise'):
            module.physical_exercise(focus)
        else:
            print(f"💪 Starting {focus} physical exercises...")
            print("Take care of your body to support your mental health.")
    return wrapper

def create_generic_wrapper(module_name):
    def wrapper(args=None):
        print(f"🔧 {module_name.replace('_', ' ').title()} module")
        print("This module is available but may need configuration.")
        print(f"Try: python3 modules/{module_name}.py")
    return wrapper

# Import existing modules with their actual function names
safe_import_with_wrapper('mood_tracking', 'mood_command', create_mood_wrapper)
safe_import_with_wrapper('breathing', 'breathing_session', create_breathing_wrapper)
safe_import_with_wrapper('gratitude', 'gratitude_practice', create_gratitude_wrapper)
safe_import_with_wrapper('meditation', 'meditation_session', create_meditation_wrapper)
safe_import_with_wrapper('physical', 'physical_exercise', create_physical_wrapper)

# For modules that might not have the expected functions, create generic wrappers
module_list = [
    # Core mental health modules
    'habits', 'chatbot', 'mental_health_articles', 'intention_timer', 'anxiety_support', 'depression_support', 'insomnia_support',
    'body_image_support', 'addiction_recovery', 'coping_strategies', 'coping_skills',
    'rescue_sessions', 'guided_journals', 'learning_paths', 'enhanced_meditation',
    'hypnosis_sessions', 'neurowave_stimulation', 'social_connection', 'emotion_analysis',
    'quick_capture', 'external_integrations',
    
    # MISSING MODULES - Now added!
    'achievements_gallery', 'api_server', 'ascii_art', 'backup_export', 
    'daily_checkin', 'demo_achievements', 'smart_suggestions', 'textual_example',
    'visual_achievements', 'wellness_dashboard_enhanced', 'quick_actions'
]

# Import modules with their correct command function names
command_function_map = {
    # Existing mappings
    'mental_health_articles': 'run',
    'intention_timer': 'run',
    'anxiety_support': 'anxiety_command',
    'depression_support': 'depression_command', 
    'addiction_recovery': 'addiction_recovery_command',
    'coping_strategies': 'coping_strategies_command',
    'coping_skills': 'coping_command',
    'rescue_sessions': 'rescue_sessions_command',
    'crisis': 'crisis_command',
    'emergency': 'emergency_command',
    'guided_journals': 'guided_journals_command',
    'learning_paths': 'learning_paths_command',
    'enhanced_meditation': 'enhanced_meditation_command',
    'hypnosis_sessions': 'hypnosis_command',
    'neurowave_stimulation': 'neurowave_command',
    'social_connection': 'social_command',
    'emotion_analysis': 'emotion_analysis_command',
    'quick_capture': 'capture_command',
    'external_integrations': 'external_command',
    'body_image_support': 'body_image_command',
    'insomnia_support': 'insomnia_command',
    
    # MISSING MODULES - Command function mappings
    'api_server': 'api_server_command',
    'backup_export': 'backup_command',
    'daily_checkin': 'daily_checkin_command',
    'visual_achievements': 'handle_visual_command',
    'wellness_dashboard_enhanced': 'wellness_dashboard_command'
}

for module_name in module_list:
    if module_name not in AVAILABLE_MODULES:
        try:
            module = __import__(module_name)
            
            # Special handling for modules with main() functions that don't take arguments
            if module_name in ['achievements_gallery', 'demo_achievements']:
                def create_main_wrapper(mod):
                    def wrapper(action="menu"):
                        mod.main()
                    return wrapper
                AVAILABLE_MODULES[module_name] = create_main_wrapper(module)
                continue
            
            # Special handling for modules with specific function patterns
            if module_name == 'smart_suggestions':
                def create_suggestions_wrapper(mod):
                    def wrapper(action="menu"):
                        print("💡 Smart Suggestions")
                        print("=" * 20)
                        suggestions = mod.get_smart_suggestions()
                        for i, suggestion in enumerate(suggestions, 1):
                            print(f"{i}. {suggestion}")
                    return wrapper
                AVAILABLE_MODULES[module_name] = create_suggestions_wrapper(module)
                continue
            
            if module_name == 'ascii_art':
                def create_ascii_wrapper(mod):
                    def wrapper(action="menu"):
                        print("🎨 ASCII Art Generator")
                        print("This module provides ASCII art functionality.")
                        print("Try: python3 modules/ascii_art.py")
                    return wrapper
                AVAILABLE_MODULES[module_name] = create_ascii_wrapper(module)
                continue
            
            if module_name == 'textual_example':
                def create_textual_wrapper(mod):
                    def wrapper(action="menu"):
                        print("📱 Textual TUI Examples")
                        print("This module provides Textual interface examples.")
                        print("Try: python3 modules/textual_example.py")
                    return wrapper
                AVAILABLE_MODULES[module_name] = create_textual_wrapper(module)
                continue
            
            # Try the specific command function first
            if module_name in command_function_map:
                func_name = command_function_map[module_name]
                if hasattr(module, func_name):
                    AVAILABLE_MODULES[module_name] = getattr(module, func_name)
                    continue
            
            # Try to find a main function
            if hasattr(module, 'run'):
                AVAILABLE_MODULES[module_name] = module.run
            elif hasattr(module, 'main'):
                AVAILABLE_MODULES[module_name] = module.main
            else:
                AVAILABLE_MODULES[module_name] = create_generic_wrapper(module_name)
        except ImportError:
            pass

# NEW: Advanced features adapted from logbuch (these have proper run functions)
safe_import('mental_health_coach', 'run')
safe_import('wellness_autopilot', 'run')
safe_import('wellness_gamification', 'run')
safe_import('wellness_dashboard', 'run')

# NEW: Enhanced mood tracking (special case)
safe_import('enhanced_mood_tracking', 'enhanced_mood_command')

# NEW: Evidence-based modules inspired by successful mental health apps
safe_import('cbt_toolkit', 'run')          # CBT tools (MindShift, Quirk, Sanvello)
safe_import('ai_companion', 'run')         # AI chatbot (Woebot, Wysa, EmoBay)
safe_import('sleep_optimization', 'run')   # Sleep tools (Nyxo, Wake Up Time)
safe_import('positive_psychology', 'run')  # Positive psychology (Three Good Things, Happify)
safe_import('enhanced_chatbot', 'run')     # Enhanced mental health chatbot integration

# NEW: AI-powered mental health text classification
safe_import_with_wrapper('mental_health_classifier', 'main', create_classifier_wrapper)

# NEW: Positive affirmations system
safe_import_with_wrapper('affirmations', 'main', create_affirmations_wrapper)

# NEW: Sleep sounds and insomnia support
safe_import_with_wrapper('sleep_sounds', 'main', create_sleep_sounds_wrapper)

# NEW: Visual/TUI support
# (Already handled above)

# Command aliases for easy access
COMMAND_ALIASES = {
    # Core commands
    'mood': 'mood_tracking',
    'm': 'mood_tracking',
    'breathe': 'breathing',
    'b': 'breathing',
    'meditate': 'meditation',
    'med': 'meditation',
    'gratitude': 'gratitude',
    'g': 'gratitude',
    'stretch': 'physical',
    's': 'physical',
    'habits': 'habits',
    'h': 'habits',
    'chat': 'enhanced_chatbot',
    'c': 'enhanced_chatbot',
    'chatbot': 'enhanced_chatbot',
    'enhanced_chat': 'enhanced_chatbot',
    
    # Mental health articles and resources
    'articles': 'mental_health_articles',
    'article': 'mental_health_articles',
    'resources': 'mental_health_articles',
    'library': 'mental_health_articles',
    'reading': 'mental_health_articles',
    'learn': 'mental_health_articles',
    
    # Intention timer
    'intention': 'intention_timer',
    'intent': 'intention_timer',
    'focus': 'intention_timer',
    'timer': 'intention_timer',
    'pomodoro': 'intention_timer',
    
    # Mental health support
    'anxiety': 'anxiety_support',
    'anx': 'anxiety_support',
    'depression': 'depression_support',
    'dep': 'depression_support',
    'insomnia': 'insomnia_support',
    'sleep': 'insomnia_support',
    'body': 'body_image_support',
    'addiction': 'addiction_recovery',
    'recovery': 'addiction_recovery',
    'rec': 'addiction_recovery',
    'coping': 'coping_strategies',
    'cope': 'coping_strategies',
    'rescue': 'rescue_sessions',
    'resc': 'rescue_sessions',
    'crisis': 'crisis',
    'emergency': 'emergency',
    'sos': 'rescue_sessions',
    '911': 'emergency',
    '112': 'emergency',
    '999': 'emergency',
    'journal': 'guided_journals',
    'j': 'guided_journals',
    'learn': 'learning_paths',
    'learning': 'learning_paths',
    
    # Advanced techniques
    'hypnosis': 'hypnosis_sessions',
    'hyp': 'hypnosis_sessions',
    'neurowave': 'neurowave_stimulation',
    'neuro': 'neurowave_stimulation',
    
    # Social and analysis
    'social': 'social_connection',
    'soc': 'social_connection',
    'analysis': 'emotion_analysis',
    'analyze': 'emotion_analysis',
    'capture': 'quick_capture',
    'cap': 'quick_capture',
    'share': 'social_connection',
    'palette': 'emotion_analysis',
    'triggers': 'emotion_analysis',
    'connect': 'social_connection',
    
    # Integration
    'external': 'external_integrations',
    'integrations': 'external_integrations',
    'int': 'external_integrations',
    
    # NEW: Evidence-based modules
    'cbt': 'cbt_toolkit',
    'cognitive': 'cbt_toolkit',
    'thoughts': 'cbt_toolkit',
    'thinking': 'cbt_toolkit',
    'ai': 'ai_companion',
    'companion': 'ai_companion',
    'chat': 'ai_companion',
    'talk': 'ai_companion',
    'sleep': 'sleep_optimization',
    'rest': 'sleep_optimization',
    'nap': 'sleep_optimization',
    'positive': 'positive_psychology',
    'three': 'positive_psychology',
    'strengths': 'positive_psychology',
    'optimism': 'positive_psychology',
    
    # NEW: Nicky Case guide integration
    'nicky': 'nicky_case_guide',
    'wolf': 'nicky_case_guide',
    'habits': 'nicky_case_guide',
    'guide': 'nicky_case_guide',
    'fear': 'nicky_case_guide',
    
    # NEW: AI Mental Health Classification
    'classify': 'mental_health_classifier',
    'classifier': 'mental_health_classifier',
    'ai_classify': 'mental_health_classifier',
    'text_analysis': 'mental_health_classifier',
    'mental_analysis': 'mental_health_classifier',
    'analyze_text': 'mental_health_classifier',
    
    # NEW: Positive Affirmations
    'affirmations': 'affirmations',
    'affirm': 'affirmations',
    'positive': 'affirmations',
    'daily_affirmation': 'affirmations',
    'inspire': 'affirmations',
    'motivation': 'affirmations',
    
    # NEW: Sleep Sounds & Insomnia Support
    'sleep': 'sleep_sounds',
    'sleep_sounds': 'sleep_sounds',
    'insomnia': 'sleep_sounds',
    'sounds': 'sleep_sounds',
    'white_noise': 'sleep_sounds',
    'nature_sounds': 'sleep_sounds',
    'sleep_aid': 'sleep_sounds',
    
    # Quick Actions
    'qm': 'mood_tracking',
    'qb': 'breathing',
    'qg': 'gratitude',
    'qf': 'meditation',  # Quick focus -> meditation
    'qc': 'meditation',  # Quick calm -> meditation
    
    # NEW: Advanced features
    'coach': 'mental_health_coach',
    'ai': 'mental_health_coach',
    'autopilot': 'wellness_autopilot',
    'auto': 'wellness_autopilot',
    'gamify': 'wellness_gamification',
    'game': 'wellness_gamification',
    'achievements': 'wellness_gamification',
    'dashboard': 'wellness_dashboard',
    'dash': 'wellness_dashboard',
    'd': 'wellness_dashboard',
    
    # NEW: Logbuch-inspired commands
    'checkin': 'daily_checkin',
    'check': 'daily_checkin',
    'morning': 'daily_checkin',
    'evening': 'daily_checkin',
    'reflect': 'daily_checkin',
    
    'enhanced_mood': 'enhanced_mood_tracking',
    'mood_enhanced': 'enhanced_mood_tracking',
    'mood_analytics': 'enhanced_mood_tracking',
    'moods': 'enhanced_mood_tracking',
    
    'wellness_dashboard': 'wellness_dashboard_enhanced',
    'dashboard_enhanced': 'wellness_dashboard_enhanced',
    
    # MISSING MODULES - New aliases added!
    'achievements_gallery': 'achievements_gallery',
    'gallery': 'achievements_gallery',
    'showcase': 'achievements_gallery',
    
    'api': 'api_server',
    'server': 'api_server',
    'api_server': 'api_server',
    
    'ascii': 'ascii_art',
    'art': 'ascii_art',
    'ascii_art': 'ascii_art',
    
    'backup': 'backup_export',
    'export': 'backup_export',
    'backup_export': 'backup_export',
    
    'daily': 'daily_checkin',
    'daily_checkin': 'daily_checkin',
    
    'demo': 'demo_achievements',
    'demo_achievements': 'demo_achievements',
    
    'suggestions': 'smart_suggestions',
    'smart': 'smart_suggestions',
    'smart_suggestions': 'smart_suggestions',
    
    'textual': 'textual_example',
    'tui': 'textual_example',
    'textual_example': 'textual_example',
    
    'visual': 'visual_achievements',
    'visual_achievements': 'visual_achievements',
    
    'quick_actions': 'quick_actions',
    'qa': 'quick_actions',
    'stats': 'wellness_dashboard_enhanced',
    'summary': 'wellness_dashboard_enhanced',
    'insights': 'wellness_dashboard_enhanced',
    
    'backup_export': 'backup_export',
    'save_data': 'backup_export',
    'restore_data': 'backup_export',
    'import_data': 'backup_export',
    
    # API server
    'api': 'api_server',
    'server': 'api_server',
    'api_server': 'api_server',
    'web': 'api_server',
    
    # System commands
    'about': 'about',
    'a': 'about',
    'status': 'status',
    'export': 'export',
    'backup': 'backup',
    'privacy': 'privacy'
}

def show_welcome():
    """Show welcome message with ASCII art and new features highlighted"""
    if ASCII_AVAILABLE:
        print(get_welcome_art())
        print(get_daily_quote())
        print(get_quick_action_menu())
    else:
        print("🧘‍♀️ Welcome to om - Your Advanced Mental Health Companion")
        print("=" * 65)
        print()
        print("🆕 NEW FEATURES:")
        print("  🧠 AI Coach        - Personalized mental health insights")
        print("  🤖 Autopilot      - Automated wellness task management")
        print("  🎮 Gamification   - Achievement system & progress tracking")
        print("  📊 Dashboard      - Real-time wellness metrics visualization")
        print()
        print("🎯 CORE FEATURES:")
        print("  📈 Mood Tracking  - Monitor your emotional wellbeing")
        print("  🫁 Breathing      - Guided breathing exercises")
        print("  🧘 Meditation     - Mindfulness and meditation sessions")
        print("  🙏 Gratitude      - Daily gratitude practice")
        print("  💪 Physical       - Body wellness and stretching")
        print("  🔄 Habits         - Build healthy mental health habits")
        print()
        print("🆘 SUPPORT FEATURES:")
        print("  😰 Anxiety        - Anxiety management tools")
        print("  😔 Depression     - Depression support resources")
        print("  😴 Sleep          - Insomnia and sleep support")
        print("  🆘 Crisis         - Emergency mental health support")
        print("  📝 Journal        - Guided journaling exercises")
        print("  🎓 Learning       - Mental health education paths")
        print()
        print("⚡ QUICK ACTIONS:")
        print("  om coach daily    - Get your daily AI insight")
    print("  om dashboard      - View your wellness dashboard")
    print("  om autopilot      - Check automated recommendations")
    print("  om gamify status  - See your progress & achievements")
    print()
    print("💡 Type 'om <command>' to get started, or 'om help' for full options")
    print()

def show_help():
    """Show comprehensive help with ASCII art enhancement"""
    if ASCII_AVAILABLE:
        print(get_simple_om_logo())
        print(get_help_art())
        print(get_separator())
    else:
        print("🧘‍♀️ om - Advanced Mental Health CLI Platform")
        print("=" * 50)
    
    print()
    print(f"{Colors.PURPLE if ASCII_AVAILABLE else ''}🆕 ADVANCED FEATURES:{Colors.END if ASCII_AVAILABLE else ''}")
    print("  coach [daily|urgent|analyze|summary] - AI-powered mental health coaching")
    print("  autopilot [status|tasks|recommendations] - Automated wellness management")
    print("  gamify [status|achievements|challenge] [-v] - Progress tracking & achievements")
    print("  dashboard [show|live|summary|export] - Visual wellness metrics")
    print("  classify <text> - AI-powered mental health text classification")
    print("  affirmations [daily|category|favorites] - Daily positive affirmations")
    print("  sleep [categories|sounds|play] - Sleep sounds and insomnia support")
    print()
    print(f"{Colors.YELLOW if ASCII_AVAILABLE else ''}✨ VISUAL MODE:{Colors.END if ASCII_AVAILABLE else ''}")
    print("  Add -v or --visual to supported commands for beautiful interfaces:")
    print("  om gamify status -v       # Beautiful achievements gallery")
    print("  om dashboard -v           # Rich visual dashboard (coming soon)")
    print("  om coach analyze -v       # Interactive AI analysis (coming soon)")
    print()
    print(f"{Colors.CYAN if ASCII_AVAILABLE else ''}🎯 CORE COMMANDS:{Colors.END if ASCII_AVAILABLE else ''}")
    print("  mood              - Track your mood and emotions")
    print("  breathe           - Guided breathing exercises")
    print("  meditate          - Meditation and mindfulness sessions")
    print("  gratitude         - Practice gratitude and appreciation")
    print("  stretch           - Physical wellness and movement")
    print("  habits            - Build and track healthy habits")
    print("  chat              - Interactive mental health chatbot")
    print()
    print(f"{Colors.RED if ASCII_AVAILABLE else ''}🆘 MENTAL HEALTH SUPPORT:{Colors.END if ASCII_AVAILABLE else ''}")
    print("  anxiety           - Anxiety management and coping tools")
    print("  depression        - Depression support and resources")
    print("  insomnia          - Sleep support and insomnia help")
    print("  rescue            - Crisis support and emergency resources")
    print("  coping            - Coping strategies and techniques")
    print("  journal           - Guided journaling and reflection")
    print("  learn             - Mental health education and learning paths")
    print()
    print(f"{Colors.BLUE if ASCII_AVAILABLE else ''}🔬 ADVANCED TECHNIQUES:{Colors.END if ASCII_AVAILABLE else ''}")
    print("  hypnosis          - Guided hypnosis and deep relaxation")
    print("  neurowave         - Brainwave entrainment and stimulation")
    print("  social            - Social connection and support tools")
    print("  analysis          - Emotion analysis and pattern recognition")
    print()
    print(f"{Colors.GREEN if ASCII_AVAILABLE else ''}⚙️  SYSTEM COMMANDS:{Colors.END if ASCII_AVAILABLE else ''}")
    print("  about             - About om and mental health resources")
    print("  status            - System status and module availability")
    print("  export            - Export your data")
    print("  backup            - Backup your mental health data")
    print("  privacy           - Privacy settings and data management")
    print()
    
    if ASCII_AVAILABLE:
        print(get_quick_action_menu())
    else:
        print("🔗 ALIASES:")
        print("  Short forms: m (mood), b (breathe), g (gratitude), d (dashboard)")
        print("  Quick access: anx (anxiety), dep (depression), resc (rescue)")
    
    print()
    print(f"{Colors.YELLOW if ASCII_AVAILABLE else ''}💡 EXAMPLES:{Colors.END if ASCII_AVAILABLE else ''}")
    print("  om coach daily           # Get daily AI coaching insight")
    print("  om dashboard live        # Start live wellness dashboard")
    print("  om autopilot tasks       # View automated wellness tasks")
    print("  om gamify achievements   # See your mental health achievements")
    print("  om classify \"I feel anxious\" # Classify mental health text")
    print("  om affirmations daily    # Get daily positive affirmation")
    print("  om sleep sounds nature   # Browse nature sleep sounds")
    print("  om mood                  # Quick mood check")
    print("  om rescue                # Emergency mental health support")
    
    if ASCII_AVAILABLE:
        print(get_daily_quote())
    print()

def show_status():
    """Show system status including new modules with ASCII art"""
    if ASCII_AVAILABLE:
        print(get_wellness_dashboard_header())
    else:
        print("🧘‍♀️ om System Status")
        print("=" * 30)
    
    print(f"Total modules available: {len(AVAILABLE_MODULES)}")
    print()
    
    categories = {
        "🆕 Advanced Features": [
            'mental_health_coach', 'wellness_autopilot', 
            'wellness_gamification', 'wellness_dashboard'
        ],
        "🎯 Core Modules": [
            'mood_tracking', 'breathing', 'meditation', 
            'gratitude', 'physical', 'habits', 'chatbot'
        ],
        "🆘 Mental Health Support": [
            'anxiety_support', 'depression_support', 'insomnia_support',
            'rescue_sessions', 'coping_strategies', 'guided_journals'
        ],
        "🔬 Advanced Techniques": [
            'hypnosis_sessions', 'neurowave_stimulation', 
            'enhanced_meditation', 'learning_paths'
        ],
        "🌐 Social & Analysis": [
            'social_connection', 'emotion_analysis', 'quick_capture'
        ],
        "⚙️  Integration": [
            'external_integrations'
        ]
    }
    
    for category, modules in categories.items():
        if ASCII_AVAILABLE:
            print(f"{Colors.CYAN}{category}:{Colors.END}")
        else:
            print(f"{category}:")
        
        available_count = 0
        for module in modules:
            status = "✅" if module in AVAILABLE_MODULES else "❌"
            if module in AVAILABLE_MODULES:
                available_count += 1
            print(f"  {status} {module}")
        
        if ASCII_AVAILABLE:
            percentage = (available_count / len(modules)) * 100
            print(f"  {get_progress_bar(percentage, 20)}")
        print()
    
    # Show data directory info
    data_dir = os.path.expanduser("~/.om")
    if os.path.exists(data_dir):
        files = os.listdir(data_dir)
        print(f"📁 Data directory: {data_dir}")
        print(f"   Files: {len(files)} data files")
    else:
        print("📁 Data directory: Not yet created")
    
    print()
    print("💡 Use 'om <module_name> --help' for module-specific help")

def show_about():
    """Show about information with new features"""
    print("🧘‍♀️ om - Advanced Mental Health CLI Platform")
    print("=" * 50)
    print()
    print("🎯 MISSION:")
    print("Providing accessible, private, and comprehensive mental health")
    print("support directly in your terminal with AI-powered insights.")
    print()
    print("🆕 ADVANCED FEATURES:")
    print("• AI Mental Health Coach - Personalized insights and recommendations")
    print("• Wellness Autopilot - Automated task management and routines")
    print("• Gamification System - Achievement tracking and progress motivation")
    print("• Visual Dashboard - Real-time wellness metrics and visualization")
    print()
    print("🌟 CORE PRINCIPLES:")
    print("• Privacy First - All data stays on your device")
    print("• Evidence-Based - Built on proven mental health techniques")
    print("• Accessible - Available 24/7 in your terminal")
    print("• Comprehensive - From daily wellness to crisis support")
    print("• Personalized - AI learns your patterns and preferences")
    print()
    print("🔒 PRIVACY & SECURITY:")
    print("• No data transmission - everything stays local")
    print("• Encrypted storage options available")
    print("• User-controlled data retention")
    print("• Open source and transparent")
    print()
    print("🆘 CRISIS SUPPORT:")
    print("If you're experiencing a mental health crisis:")
    print("• Use 'om rescue' for immediate support resources")
    print("• Contact emergency services if in immediate danger")
    print("• Reach out to a mental health professional")
    print()
    print("📞 RESOURCES:")
    print("• National Suicide Prevention Lifeline: 988")
    print("• Crisis Text Line: Text HOME to 741741")
    print("• International Association for Suicide Prevention: iasp.info")
    print()
    print("💝 Remember: You matter, your mental health matters, and help is available.")
    print()

def list_modules():
    """List all available modules with descriptions"""
    print("📋 Available om Modules")
    print("=" * 30)
    
    module_descriptions = {
        # Advanced features
        'mental_health_coach': "🧠 AI-powered personalized mental health coaching and insights",
        'wellness_autopilot': "🤖 Automated wellness task management and routine optimization",
        'wellness_gamification': "🎮 Achievement system, progress tracking, and motivation",
        'wellness_dashboard': "📊 Real-time visual wellness metrics and progress dashboard",
        'mental_health_classifier': "🔍 AI-powered mental health text classification and analysis",
        'affirmations': "✨ Daily positive affirmations for self-love, healing, and motivation",
        'sleep_sounds': "🎵 Sleep sounds, white noise, and insomnia support with mental health focus",
        
        # Core modules
        'mood_tracking': "📈 Track and analyze your mood patterns over time",
        'breathing': "🫁 Guided breathing exercises for relaxation and focus",
        'meditation': "🧘 Mindfulness and meditation sessions for mental clarity",
        'gratitude': "🙏 Daily gratitude practice for positive mindset",
        'physical': "💪 Physical wellness, stretching, and movement exercises",
        'habits': "🔄 Build and maintain healthy mental health habits",
        'chatbot': "💬 Interactive AI chatbot for mental health conversations",
        'enhanced_chatbot': "💬 Enhanced AI chatbot with advanced mental health conversation support",
        'mental_health_articles': "📚 Curated mental health articles and resources library",
        'intention_timer': "🎯 Focused intention timer for study, meditation, and mindful activities",
        
        # Mental health support
        'anxiety_support': "😰 Comprehensive anxiety management tools and techniques",
        'depression_support': "😔 Depression support resources and coping strategies",
        'insomnia_support': "😴 Sleep improvement and insomnia management tools",
        'rescue_sessions': "🆘 Crisis support and emergency mental health resources",
        'coping_strategies': "🛡️ Evidence-based coping techniques for difficult times",
        'guided_journals': "📝 Structured journaling for self-reflection and growth",
        'learning_paths': "🎓 Educational content about mental health and wellness",
        
        # Advanced techniques
        'hypnosis_sessions': "🌀 Guided hypnosis for deep relaxation and healing",
        'neurowave_stimulation': "🧠 Brainwave entrainment for enhanced mental states",
        'enhanced_meditation': "🧘‍♀️ Advanced meditation techniques and practices",
        
        # Social and analysis
        'social_connection': "🤝 Tools for building and maintaining social connections",
        'emotion_analysis': "🔍 Advanced emotion pattern analysis and insights",
        'quick_capture': "⚡ Rapid mood and thought capture for busy moments",
        
        # Integration
        'external_integrations': "🔗 Connect with external health and wellness platforms",
        
        # MISSING MODULES - Descriptions added!
        'achievements_gallery': "🏆 Visual gallery of wellness achievements and progress milestones",
        'api_server': "🌐 REST API server for external integrations and web interfaces",
        'ascii_art': "🎨 ASCII art generator for beautiful terminal displays",
        'backup_export': "💾 Data backup, export, and recovery management system",
        'daily_checkin': "📅 Daily wellness check-ins and reflection prompts",
        'demo_achievements': "🎯 Achievement system demonstration and testing tools",
        'smart_suggestions': "💡 AI-powered smart suggestions for wellness activities",
        'textual_example': "📱 Textual TUI interface examples and demonstrations",
        'visual_achievements': "👁️ Visual achievement displays and progress visualization",
        'wellness_dashboard_enhanced': "📈 Enhanced wellness dashboard with advanced analytics",
        'quick_actions': "⚡ Quick wellness actions and rapid intervention tools"
    }
    
    for module_name in sorted(AVAILABLE_MODULES.keys()):
        description = module_descriptions.get(module_name, "Mental health support module")
        status = "✅" if module_name in AVAILABLE_MODULES else "❌"
        print(f"{status} {module_name}")
        print(f"   {description}")
        print()

def run_module(module_name, args):
    """Run a specific module with arguments"""
    if module_name in AVAILABLE_MODULES:
        try:
            # Check for visual mode first (if -v flag or visual support available)
            if VISUAL_SUPPORT and (args and '-v' in args or '--visual' in args):
                # Remove visual flags from args
                visual_args = [arg for arg in args if arg not in ['-v', '--visual']]
                if handle_visual_command(module_name, visual_args):
                    return  # Visual command handled successfully
            
            # Pass the first argument as action, rest as kwargs
            action = args[0] if args else "menu"
            kwargs = {}
            
            # For modules that expect specific argument patterns
            if len(args) > 1:
                # Pass additional args as kwargs or handle specific patterns
                if module_name in ['mood_tracking', 'breathing', 'gratitude', 'meditation', 'physical', 'mental_health_articles', 'intention_timer']:
                    # These use wrapper functions that handle args differently
                    AVAILABLE_MODULES[module_name](args)
                elif module_name in ['mental_health_classifier', 'affirmations', 'sleep_sounds']:
                    # Special handling for modules that use sys.argv
                    AVAILABLE_MODULES[module_name](args=args)
                elif module_name in ['cbt_toolkit', 'ai_companion', 'sleep_optimization', 'positive_psychology', 'nicky_case_guide']:
                    # New evidence-based modules expect args list
                    AVAILABLE_MODULES[module_name](args)
                else:
                    # Advanced modules expect action and kwargs
                    AVAILABLE_MODULES[module_name](action=action)
            else:
                if module_name in ['mood_tracking', 'breathing', 'gratitude', 'meditation', 'physical', 'mental_health_articles', 'intention_timer']:
                    AVAILABLE_MODULES[module_name](args)
                elif module_name in ['mental_health_classifier', 'affirmations', 'sleep_sounds']:
                    # Special handling for modules that use sys.argv
                    AVAILABLE_MODULES[module_name](action=action)
                elif module_name in ['cbt_toolkit', 'ai_companion', 'sleep_optimization', 'positive_psychology', 'nicky_case_guide']:
                    # New evidence-based modules expect args list (can be empty)
                    AVAILABLE_MODULES[module_name](args)
                else:
                    AVAILABLE_MODULES[module_name](action=action)
        except Exception as e:
            print(f"Error running {module_name}: {e}")
            print("This might be a module compatibility issue.")
    else:
        print(f"Module '{module_name}' is not available.")
        print("Use 'om status' to see available modules.")

def main():
    """Main entry point with enhanced argument parsing"""
    if len(sys.argv) == 1:
        show_welcome()
        return
    
    command = sys.argv[1].lower()
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    # Handle system commands
    if command in ['help', '--help', '-h']:
        show_help()
    elif command == 'about':
        show_about()
    elif command == 'status':
        show_status()
    elif command in ['list-modules', '--list-modules']:
        list_modules()
    elif command == 'version':
        print("om version 0.0.1 - Advanced Mental Health CLI Platform")
        print("Evidence-based mental health support with privacy-first design")
    
    # Handle module commands with visual support
    elif command in COMMAND_ALIASES:
        module_name = COMMAND_ALIASES[command]
        
        # Check for visual mode first
        if VISUAL_SUPPORT and handle_visual_command(command, args):
            return  # Visual command handled
        
        # Fall back to text-based command
        run_module(module_name, args)
    elif command in AVAILABLE_MODULES:
        
        # Check for visual mode first
        if VISUAL_SUPPORT and handle_visual_command(command, args):
            return  # Visual command handled
        
        # Fall back to text-based command
        run_module(command, args)
    
    # Handle special combined commands
    elif command == 'quick':
        if args and args[0] in ['mood', 'breathe', 'gratitude']:
            # Redirect to quick actions
            print(f"💡 Try: om {args[0]} for {args[0]} tracking")
            if args[0] in COMMAND_ALIASES:
                run_module(COMMAND_ALIASES[args[0]], args[1:])
        else:
            print("Quick actions: mood, breathe, gratitude")
    
    # Handle data management commands
    elif command == 'export':
        print("📤 Data Export")
        print("Use 'om dashboard export' for wellness metrics export")
        print("Individual modules may have their own export options")
    
    elif command == 'backup':
        data_dir = os.path.expanduser("~/.om")
        if os.path.exists(data_dir):
            backup_dir = f"{data_dir}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            import shutil
            shutil.copytree(data_dir, backup_dir)
            print(f"✅ Data backed up to: {backup_dir}")
        else:
            print("No data directory found to backup")
    
    elif command == 'privacy':
        print("🔒 Privacy & Data Management")
        print("=" * 30)
        data_dir = os.path.expanduser("~/.om")
        print(f"Data location: {data_dir}")
        if os.path.exists(data_dir):
            files = os.listdir(data_dir)
            print(f"Data files: {len(files)}")
            print("All data is stored locally on your device")
            print("No data is transmitted to external servers")
        print("\nTo delete all data: rm -rf ~/.om")
        print("To backup data: om backup")
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'om help' to see available commands")
        print()
        print("🆕 Try these new advanced features:")
        print("  om coach daily    - Get AI coaching insight")
        print("  om dashboard      - View wellness dashboard")
        print("  om autopilot      - Check automated tasks")
        print("  om gamify status  - See achievements")
        print("  om coach daily    - Get AI coaching insight")
        print("  om dashboard      - View wellness dashboard")
        print("  om autopilot      - Check automated tasks")
        print("  om gamify status  - See achievements")

if __name__ == "__main__":
    main()
