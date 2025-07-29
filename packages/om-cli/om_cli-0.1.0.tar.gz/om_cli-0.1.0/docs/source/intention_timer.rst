Intention Timer
===============

The Intention Timer is a focused timing system inspired by the Pomodoro Technique and mindful productivity practices. It helps you set clear intentions for focused work sessions and track your progress over time.

🎯 Overview
-----------

The Intention Timer provides:

- **Focused Sessions**: Set clear intentions for study, meditation, exercise, and work
- **Multiple Categories**: Choose from 6 different activity types
- **Progress Tracking**: Monitor completion rates and effectiveness
- **Rich Interface**: Beautiful terminal interface with progress bars and animations
- **Session History**: Review past activities and track improvements
- **Statistics**: Analyze your focus patterns and productivity

✨ Key Features
--------------

**🎯 Intentional Focus**
   Set a clear intention before starting any focused activity

**⏱️ Flexible Timing**
   Choose any duration from seconds to hours

**📊 Progress Tracking**
   Visual progress bars and real-time countdown

**📚 Multiple Categories**
   - 📚 Study & Learning
   - 🧘 Meditation & Mindfulness
   - 💪 Exercise & Movement
   - 💼 Focused Work
   - 🎨 Creative Practice
   - 📖 Reading & Research

**📈 Analytics**
   Track completion rates, total focus time, and effectiveness ratings

🚀 Getting Started
------------------

Basic Commands
~~~~~~~~~~~~~

.. code-block:: bash

   # View all available commands
   om intention

   # Create a new intention session
   om intention new

   # Start a new intention (alias for new)
   om intention start

   # View past activities
   om intention history

   # Show statistics and analytics
   om intention stats

Quick Access Aliases
~~~~~~~~~~~~~~~~~~~

The intention timer can be accessed through multiple aliases:

.. code-block:: bash

   om intention new    # Full command
   om intent new       # Short alias
   om focus new        # Focus alias
   om timer new        # Timer alias
   om pomodoro new     # Pomodoro alias

🎯 Creating an Intention
-----------------------

Step-by-Step Process
~~~~~~~~~~~~~~~~~~~

1. **Choose Category**: Select from 6 activity types
2. **Set Intention**: Describe what you want to accomplish
3. **Set Duration**: Choose minutes and seconds
4. **Confirm & Start**: Review and begin your focused session

Example Session
~~~~~~~~~~~~~~

.. code-block:: bash

   om intention new

Interactive prompts will guide you through:

.. code-block:: text

   🎯 Create New Intention
   Set your intention and focus on what matters most.

   Select a category:
     1. 📚 Study & Learning
     2. 🧘 Meditation & Mindfulness
     3. 💪 Exercise & Movement
     4. 💼 Focused Work
     5. 🎨 Creative Practice
     6. 📖 Reading & Research

   Enter your choice (1-6): 2

   🧘 Meditation & Mindfulness selected!

   What would you like to accomplish during this time?: Practice mindfulness meditation

   Set your intention time:
   Minutes (25): 10
   Seconds (0): 0

   ╭────────────────────────────── 🎯 Intention Set ──────────────────────────────╮
   │ 🧘 Meditation & Mindfulness                                                  │
   │                                                                              │
   │ Intention: Practice mindfulness meditation                                   │
   │ Duration: 10:00                                                              │
   │                                                                              │
   │ Ready to begin your focused session?                                         │
   ╰──────────────────────────────────────────────────────────────────────────────╯

⏱️ Timer Interface
-----------------

Live Progress Display
~~~~~~~~~~~~~~~~~~~

When you start a timer, you'll see:

- **Real-time countdown** with minutes and seconds
- **Progress bar** showing completion percentage
- **Elapsed time** tracker
- **Pause/resume** functionality (Ctrl+C)

Timer Controls
~~~~~~~~~~~~~

During a session:

- **Ctrl+C**: Pause the timer and show options
- **Resume**: Continue the session
- **Stop and Log**: End early but log progress
- **Abandon**: Cancel without logging

Example Timer Display
~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   🧘 Intention Timer Started

   Focus: Practice mindfulness meditation
   Duration: 10:00

   Press Ctrl+C to pause/stop the timer

   ⠋ Time Remaining: 08:45 ████████████████████▌         17%  0:01:15

Session Completion
~~~~~~~~~~~~~~~~~

When a session completes:

.. code-block:: text

   🎉 INTENTION COMPLETED! 🎉
   ✨ You focused on: Practice mindfulness meditation
   ⏱️  Duration: 10:00

   📊 Log Your Session
   How effective was this session? (1-10, or press Enter to skip): 8
   Any notes about this session? (optional): Felt very centered and calm

   ✅ Session logged successfully!

📊 Progress Tracking
-------------------

Session History
~~~~~~~~~~~~~~

View your past intentions and their outcomes:

.. code-block:: bash

   om intention history

Example output:

.. code-block:: text

   📚 Past Intentions (Last 10)
   ============================================================

   1. ✅ 🧘 Practice mindfulness meditation
      📂 Meditate
      ⏱️  Planned: 10:00 | Completed: 10:00 (100.0%)
      ⭐ Effectiveness: 8/10
      📝 Felt very centered and calm
      📅 2025-01-15 14:30

   2. ❌ 📚 Study Python programming
      📂 Study
      ⏱️  Planned: 25:00 | Completed: 18:30 (74.0%)
      📅 2025-01-15 13:00

Statistics Dashboard
~~~~~~~~~~~~~~~~~~~

Track your overall progress:

.. code-block:: bash

   om intention stats

Example output:

.. code-block:: text

   📊 Intention Timer Statistics
   ==================================================

   📈 Overall Performance
      Total Sessions: 15
      Completed: 12 (80.0%)
      Abandoned: 3
      Total Focus Time: 6h 45m
      Average Effectiveness: 7.8/10

   📂 By Category
      🧘 Meditate: 8 sessions (8 completed, 100.0%)
      📚 Study: 4 sessions (3 completed, 75.0%)
      💪 Exercise: 2 sessions (1 completed, 50.0%)
      💼 Work: 1 sessions (0 completed, 0.0%)

🎯 Use Cases
-----------

Study Sessions
~~~~~~~~~~~~~

.. code-block:: bash

   # 25-minute focused study session
   om intention new
   # Select: Study & Learning
   # Intention: "Review calculus concepts"
   # Duration: 25:00

Meditation Practice
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 10-minute mindfulness session
   om focus new
   # Select: Meditation & Mindfulness
   # Intention: "Practice breath awareness"
   # Duration: 10:00

Work Focus Blocks
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 45-minute deep work session
   om timer new
   # Select: Focused Work
   # Intention: "Complete project documentation"
   # Duration: 45:00

Exercise Routines
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 20-minute workout session
   om pomodoro new
   # Select: Exercise & Movement
   # Intention: "Full body strength training"
   # Duration: 20:00

🔧 Technical Features
--------------------

Database Storage
~~~~~~~~~~~~~~~

All intention data is stored locally in SQLite:

**intention_activities table**:
   - Activity details (category, description, duration)
   - Status tracking (planned, in_progress, completed, abandoned)
   - Effectiveness ratings and notes
   - Timestamps for analysis

**intention_sessions table**:
   - Detailed session tracking
   - Interruption counting
   - Focus ratings
   - Session notes

Rich Terminal Interface
~~~~~~~~~~~~~~~~~~~~~~

Built with the Rich library for beautiful terminal output:

- **Progress bars** with real-time updates
- **Colored panels** for better organization
- **Interactive prompts** for user input
- **Animated spinners** during active sessions
- **Tables** for statistics display

Threading Support
~~~~~~~~~~~~~~~~

- **Non-blocking timers** using Python threading
- **Responsive controls** during active sessions
- **Safe interruption** handling
- **Clean shutdown** procedures

🎨 Design Philosophy
-------------------

Intentional Focus
~~~~~~~~~~~~~~~~

Every session starts with setting a clear intention, promoting:

- **Mindful engagement** with activities
- **Purpose-driven** time blocks
- **Reflection** on goals and outcomes
- **Conscious** time management

Minimal Friction
~~~~~~~~~~~~~~~

- **Quick setup** with sensible defaults
- **Intuitive commands** and aliases
- **Clear visual feedback** throughout
- **Flexible timing** options

Progress Awareness
~~~~~~~~~~~~~~~~~

- **Visual progress** indicators
- **Completion tracking** and statistics
- **Effectiveness ratings** for improvement
- **Historical analysis** of patterns

🚀 Integration with om Ecosystem
-------------------------------

Mental Health Focus
~~~~~~~~~~~~~~~~~~

The intention timer integrates with om's mental health focus:

- **Meditation sessions** support mindfulness practice
- **Study blocks** reduce academic stress
- **Exercise timers** promote physical wellness
- **Work focus** prevents burnout

Data Integration
~~~~~~~~~~~~~~~

Future integrations with other om modules:

- **Mood correlation** with session effectiveness
- **Habit tracking** integration for routine building
- **AI coaching** recommendations for optimal timing
- **Wellness dashboard** inclusion of focus metrics

🔮 Future Enhancements
---------------------

Planned Features
~~~~~~~~~~~~~~~

- **Session templates** for recurring activities
- **Break reminders** and Pomodoro technique support
- **Focus music** integration
- **Team sessions** for collaborative work
- **Calendar integration** for scheduled intentions
- **Mobile notifications** for session reminders

Advanced Analytics
~~~~~~~~~~~~~~~~~

- **Optimal timing** analysis for different activities
- **Productivity patterns** identification
- **Focus quality** metrics and trends
- **Distraction tracking** and analysis

Social Features
~~~~~~~~~~~~~~

- **Shared intentions** with accountability partners
- **Focus groups** for collaborative sessions
- **Achievement sharing** and motivation
- **Community challenges** and goals

📖 Example Workflows
-------------------

Daily Study Routine
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Morning study block
   om intention new
   # Category: Study & Learning
   # Intention: "Review yesterday's notes"
   # Duration: 15:00

   # Focused study session
   om intention new
   # Category: Study & Learning  
   # Intention: "Complete chapter 5 exercises"
   # Duration: 45:00

   # Review session
   om intention new
   # Category: Study & Learning
   # Intention: "Summarize key concepts"
   # Duration: 20:00

Mindfulness Practice
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Morning meditation
   om focus new
   # Category: Meditation & Mindfulness
   # Intention: "Start day with breath awareness"
   # Duration: 10:00

   # Midday reset
   om focus new
   # Category: Meditation & Mindfulness
   # Intention: "Reset focus and energy"
   # Duration: 5:00

   # Evening reflection
   om focus new
   # Category: Meditation & Mindfulness
   # Intention: "Reflect on the day"
   # Duration: 15:00

Work Productivity
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Deep work session
   om timer new
   # Category: Focused Work
   # Intention: "Complete feature implementation"
   # Duration: 90:00

   # Code review session
   om timer new
   # Category: Focused Work
   # Intention: "Review team pull requests"
   # Duration: 30:00

   # Documentation work
   om timer new
   # Category: Focused Work
   # Intention: "Update project documentation"
   # Duration: 45:00

The Intention Timer transforms time management from reactive scheduling to intentional, mindful engagement with your goals and activities. By combining clear intentions with focused time blocks, it helps build sustainable productivity habits while supporting mental wellness and personal growth.
