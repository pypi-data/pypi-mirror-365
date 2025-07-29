Basic Usage
===========

This guide covers the essential daily usage patterns for the om mental health platform.

🎯 Daily Essentials
===================

The Three Core Actions
-----------------------

These three commands form the foundation of daily mental health practice:

**1. Mood Check (10 seconds)**

.. code-block:: bash

   om qm

Rate your current mood on a 1-10 scale and optionally add context.

**2. Breathing Exercise (2 minutes)**

.. code-block:: bash

   om qb

Follow a guided breathing exercise for stress relief and focus.

**3. Gratitude Practice (30 seconds)**

.. code-block:: bash

   om qg

Write down something you're grateful for to boost positive emotions.

**Daily Routine Example:**

.. code-block:: bash

   # Morning (2 minutes)
   om qm                    # Check your starting mood
   om qg                    # Practice gratitude
   
   # Midday reset (2 minutes)
   om qb                    # Breathing break
   
   # Evening reflection (1 minute)
   om qm                    # Check your ending mood

🧠 Understanding Your Mental Health
===================================

Mood Tracking Basics
---------------------

**Simple Mood Check:**

.. code-block:: bash

   om qm 7

Just provide a number from 1-10 where:
- 1-3: Very low mood, consider seeking support
- 4-6: Moderate mood, normal fluctuations
- 7-10: Good to excellent mood

**Enhanced Mood Check:**

.. code-block:: bash

   om qm 7 --energy 8 --stress 4 --notes "Good day at work"

Track multiple dimensions:
- **Mood**: Overall emotional state
- **Energy**: Physical and mental energy
- **Stress**: Current stress level
- **Notes**: Context and triggers

**With Tags:**

.. code-block:: bash

   om qm 6 --tags "work,tired,deadline"

Use tags to categorize and later analyze patterns.

Viewing Your Progress
---------------------

**Dashboard Overview:**

.. code-block:: bash

   om dashboard

See your wellness summary including:
- Recent mood trends
- Activity statistics
- Achievement progress
- AI coaching insights

**Detailed Statistics:**

.. code-block:: bash

   om gamify status         # Level, XP, achievements
   om mood stats           # Mood analytics
   om wellness stats       # Activity statistics

🧘 Wellness Practices
=====================

Breathing Exercises
-------------------

**Quick Breathing (Default):**

.. code-block:: bash

   om qb

Uses the 4-7-8 technique:
- Inhale for 4 counts
- Hold for 7 counts  
- Exhale for 8 counts
- Repeat 4 cycles

**Different Techniques:**

.. code-block:: bash

   om qb --technique box        # Box breathing (4-4-4-4)
   om qb --technique deep       # Deep breathing
   om qb --technique calm       # Calming breath

**Custom Duration:**

.. code-block:: bash

   om qb --duration 300         # 5-minute session

Gratitude Practice
------------------

**Simple Gratitude:**

.. code-block:: bash

   om qg "I'm grateful for my health"

**Categorized Gratitude:**

.. code-block:: bash

   om qg "My supportive family" --category people --intensity 9

**Categories include:**
- people, relationships, family, friends
- health, body, abilities
- experiences, opportunities, achievements
- things, possessions, comfort
- nature, beauty, environment

Focus and Calm Techniques
-------------------------

**Quick Focus Reset:**

.. code-block:: bash

   om qf

2-minute attention reset technique.

**Progressive Relaxation:**

.. code-block:: bash

   om qc

Guided muscle relaxation exercise.

**Complete Mental Reset:**

.. code-block:: bash

   om qr

Comprehensive reset combining multiple techniques.

🤖 AI-Powered Features
======================

Daily AI Coaching
-----------------

**Get Daily Insights:**

.. code-block:: bash

   om coach daily

Receive personalized recommendations based on your patterns:
- Mood trend analysis
- Suggested activities
- Pattern observations
- Motivational guidance

**Example insight:**

.. code-block:: text

   🧠 Daily Coaching Insight
   
   Your mood has been trending upward this week (avg 7.2/10)
   
   💡 Recommendation: Your data shows breathing exercises work 
   best for you in the morning. Try: om qb
   
   🔍 Pattern: You tend to have higher energy on days when 
   you practice gratitude early.

Pattern Analysis
----------------

**Analyze Your Patterns:**

.. code-block:: bash

   om coach analyze

Get insights about:
- Daily and weekly mood cycles
- Most effective wellness techniques
- Common triggers and responses
- Recovery patterns

Automated Wellness Tasks
------------------------

**View Pending Tasks:**

.. code-block:: bash

   om autopilot tasks

See AI-generated wellness tasks tailored to your needs.

**Complete Tasks:**

.. code-block:: bash

   om autopilot complete 1 8    # Complete task 1, rate effectiveness 8/10

The system learns from your ratings to improve future recommendations.

🎮 Progress and Motivation
==========================

Achievement System
------------------

**View Your Progress:**

.. code-block:: bash

   om gamify status

See your:
- Current level and XP
- Wellness points earned
- Current streak
- Recent achievements

**Beautiful Visual Mode:**

.. code-block:: bash

   om gamify status -v

Launch a stunning visual interface showing:
- Achievement gallery with progress bars
- Celebration animations for recent unlocks
- Category filtering and rarity system

**Common First Achievements:**

- 🏆 **First Mood Entry** - Record your first mood
- 🏆 **First Breath** - Complete first breathing session
- 🏆 **Grateful Heart** - Write first gratitude entry
- 🏆 **Getting Started** - Maintain 3-day wellness streak

Streak Tracking
---------------

Build consistency with streak tracking:

.. code-block:: bash

   om gamify status | grep -i streak

Streaks are maintained by:
- Daily mood entries
- Regular wellness activities
- Consistent gratitude practice

🆘 Mental Health Support
========================

When You Need Help
------------------

**Feeling Overwhelmed:**

.. code-block:: bash

   om stressed              # → Breathing exercise
   om overwhelmed           # → Complete reset
   om qgr                   # → Grounding technique

**Anxiety Support:**

.. code-block:: bash

   om anxious               # → Grounding technique
   om anxiety               # → Comprehensive anxiety tools
   om panic                 # → Immediate panic support

**Depression Support:**

.. code-block:: bash

   om sad                   # → Depression support
   om depression            # → Depression management tools
   om low                   # → Mood lifting techniques

**Crisis Support:**

.. code-block:: bash

   om rescue                # → Crisis resources
   om crisis                # → Emergency support
   om help                  # → Mental health help

**Always Available:**
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741

Natural Language Commands
-------------------------

Just describe how you feel:

.. code-block:: bash

   om stressed              # Automatically suggests breathing
   om tired                 # Suggests energy techniques
   om grateful              # Opens gratitude practice
   om anxious               # Provides grounding techniques

📊 Understanding Your Data
==========================

Data Privacy
------------

**Your data is completely private:**

- Stored locally in ``~/.om/om.db``
- Never transmitted externally
- You control all backups and exports
- No tracking or analytics sent anywhere

**Data Location:**

.. code-block:: text

   ~/.om/
   ├── om.db               # Main database
   ├── backups/            # Automatic backups
   └── config.json         # Your settings

Viewing Your Data
-----------------

**Export Your Data:**

.. code-block:: bash

   om export               # Export all data as JSON
   om export --type mood   # Export only mood data
   om backup               # Create database backup

**Data Analysis:**

.. code-block:: bash

   om mood stats           # Mood statistics
   om patterns mood        # Mood patterns
   om coach analyze        # AI pattern analysis

🔧 Customization
================

Configuration
-------------

**View Current Settings:**

.. code-block:: bash

   om config show

**Common Settings:**

.. code-block:: json

   {
     "gamification_enabled": true,
     "ai_coaching_enabled": true,
     "visual_mode_default": false,
     "backup_enabled": true
   }

**Modify Settings:**

.. code-block:: bash

   om config set gamification_enabled false
   om config set visual_mode_default true

Autopilot Configuration
-----------------------

**Configure Automated Tasks:**

.. code-block:: bash

   om autopilot config

Customize:
- Task generation frequency
- Preferred activity types
- Difficulty levels
- Reminder timing

💡 Pro Tips
===========

Building Habits
----------------

**Week 1: Start Simple**
- Just ``om qm`` once daily
- Focus on consistency over perfection

**Week 2: Add Breathing**
- Add ``om qb`` when stressed
- Use natural language: ``om stressed``

**Week 3: Include Gratitude**
- Add ``om qg`` to daily routine
- Try different categories

**Week 4: Explore AI Features**
- Check ``om coach daily`` regularly
- Use ``om autopilot tasks`` for guidance

Effective Usage Patterns
-------------------------

**Morning Routine:**

.. code-block:: bash

   om qm && om coach daily && om qg

**Stress Response:**

.. code-block:: bash

   om stressed && om qa     # Breathing + affirmation

**Evening Reflection:**

.. code-block:: bash

   om qm && om gamify status -v

**Crisis Protocol:**

.. code-block:: bash

   om rescue && om qgr      # Resources + grounding

Command Shortcuts
-----------------

**Remember these shortcuts:**

- ``qm`` = Quick mood
- ``qb`` = Quick breathing  
- ``qg`` = Quick gratitude
- ``d`` = Dashboard
- ``coach`` = AI coaching
- ``game`` = Gamification

**Natural language works too:**

- ``stressed`` → breathing
- ``anxious`` → grounding
- ``grateful`` → gratitude
- ``tired`` → energy boost

🎯 Next Steps
=============

After mastering basic usage:

1. **Explore Advanced Features:**
   - :doc:`ai_coaching` - Personalized insights
   - :doc:`wellness_autopilot` - Automated support
   - :doc:`visual_dashboard` - Beautiful progress tracking

2. **Deepen Your Practice:**
   - :doc:`mood_tracking` - Comprehensive emotional awareness
   - :doc:`breathing_exercises` - Advanced techniques
   - :doc:`pattern_analysis` - Understanding your trends

3. **Get Support:**
   - :doc:`anxiety_management` - Anxiety coping strategies
   - :doc:`depression_support` - Depression management
   - :doc:`crisis_support` - Emergency resources

**Remember**: Mental health is a journey, not a destination. Start small, be consistent, and celebrate your progress.

🌟 **Every small step counts toward your wellness journey.**
