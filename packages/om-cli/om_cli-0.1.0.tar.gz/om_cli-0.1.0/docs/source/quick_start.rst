Quick Start Guide
=================

Welcome to om! This guide will get you up and running with your mental health journey in just a few minutes.

🚀 First Launch (30 seconds)
=============================

After installation, let's verify everything is working:

.. code-block:: bash

   # Check that om is installed
   om --version

   # See what's available
   om help

   # Check system status
   om status

You should see:

.. code-block:: text

   om Mental Health CLI Platform
   ✅ All systems operational
   📊 Database: Connected
   🎮 Gamification: Active
   🧠 AI Coach: Ready

🌟 Your First Wellness Actions
===============================

Let's start with the most popular quick actions:

**1. Quick Mood Check (10 seconds)**

.. code-block:: bash

   om qm

This will prompt you to rate your mood and optionally add notes. It's the foundation of your wellness tracking.

**2. Quick Breathing Exercise (2 minutes)**

.. code-block:: bash

   om qb

Follow the guided 4-7-8 breathing technique. Perfect for stress relief or focus.

**3. Quick Gratitude Practice (30 seconds)**

.. code-block:: bash

   om qg

Write down something you're grateful for. A simple practice with powerful effects.

**4. View Your Dashboard**

.. code-block:: bash

   om dashboard

See your wellness overview, including mood trends, activity summary, and achievements.

🎮 Gamification & Progress
==========================

om includes a motivating gamification system:

**Check Your Progress:**

.. code-block:: bash

   # View your level, XP, and achievements
   om gamify status

   # See all achievements (including locked ones)
   om achievements

   # Beautiful visual achievements gallery
   om gamify status -v

**Your First Achievements:**

After your first few actions, you'll unlock:

- 🏆 **First Mood Entry** - Record your first mood
- 🏆 **First Breath** - Complete first breathing session  
- 🏆 **Grateful Heart** - Write first gratitude entry

🧠 AI Mental Health Coach
=========================

Get personalized insights from your AI coach:

.. code-block:: bash

   # Get daily personalized guidance
   om coach daily

   # Analyze your mood patterns
   om coach analyze

   # Check for urgent mental health alerts
   om coach urgent

The AI coach learns from your data to provide increasingly personalized recommendations.

🤖 Wellness Autopilot
=====================

Let om help manage your wellness automatically:

.. code-block:: bash

   # View automated wellness tasks
   om autopilot tasks

   # Check autopilot status
   om autopilot status

   # Complete a task (replace 1 with actual task ID)
   om autopilot complete 1 8

The autopilot system generates personalized wellness tasks based on your patterns and needs.

🆘 Crisis Support
=================

om provides immediate access to mental health resources:

.. code-block:: bash

   # Immediate crisis support resources
   om rescue

   # Anxiety management tools
   om anxiety

   # Depression support resources
   om depression

**Emergency Resources Always Available:**

- **National Suicide Prevention Lifeline**: 988
- **Crisis Text Line**: Text HOME to 741741
- **International Association for Suicide Prevention**: iasp.info

📱 Daily Workflows
==================

Here are some recommended daily routines:

**Morning Routine (3 minutes):**

.. code-block:: bash

   # Check your mood
   om qm

   # Get AI coaching for the day
   om coach daily

   # Practice gratitude
   om qg

**Work Break (2 minutes):**

.. code-block:: bash

   # Quick breathing reset
   om qb

   # Check pending wellness tasks
   om autopilot tasks

**Evening Reflection (3 minutes):**

.. code-block:: bash

   # Evening mood check
   om qm

   # View your progress
   om dashboard

   # Celebrate achievements
   om gamify status -v

🔤 Command Shortcuts
====================

om has extensive shortcuts for convenience:

**Ultra-Quick Actions:**

- ``om qm`` - Quick mood check
- ``om qb`` - Quick breathing
- ``om qg`` - Quick gratitude
- ``om qf`` - Quick focus reset
- ``om qc`` - Quick calm technique

**Natural Language:**

- ``om stressed`` → Breathing exercise
- ``om anxious`` → Grounding technique
- ``om tired`` → Energy boost
- ``om overwhelmed`` → Complete reset

**Core Commands:**

- ``om m`` - Full mood tracking
- ``om d`` - Dashboard
- ``om coach`` - AI coaching
- ``om game`` - Gamification

See the complete :doc:`shortcuts_reference` for all available shortcuts.

📊 Understanding Your Data
==========================

All your data is stored locally in ``~/.om/``:

**View Your Data:**

.. code-block:: bash

   # Export your data
   om export

   # Create a backup
   om backup

   # View privacy settings
   om privacy

**Data Files:**

.. code-block:: text

   ~/.om/
   ├── om.db                    # Main SQLite database
   ├── backups/                 # Automatic backups
   ├── mood_data.json          # Legacy data (migrated)
   └── wellness_stats.json     # Legacy data (migrated)

🎨 Visual Features
==================

om supports beautiful visual interfaces for special moments:

**Text Mode (Default):**

.. code-block:: bash

   om gamify status          # Simple text output
   om dashboard             # Basic wellness overview

**Visual Mode (Special Occasions):**

.. code-block:: bash

   om gamify status -v       # 🎨 Stunning achievements gallery
   om dashboard -v           # 📊 Rich visual dashboard (coming soon)

Use visual mode when you want to celebrate your progress or need motivation!

🔧 Customization
================

**Configuration:**

Edit ``~/.om/config.json`` to customize your experience:

.. code-block:: json

   {
     "privacy_mode": "local_only",
     "gamification_enabled": true,
     "visual_mode_default": false,
     "ai_coaching_enabled": true,
     "autopilot_enabled": true
   }

**Autopilot Settings:**

.. code-block:: bash

   # Configure autopilot behavior
   om autopilot config

**Dashboard Customization:**

.. code-block:: bash

   # Live updating dashboard (60-second refresh)
   om dashboard live 60

💡 Pro Tips
===========

**1. Chain Commands:**

.. code-block:: bash

   # Morning combo
   om qm && om coach daily && om qg

   # Stress relief combo
   om stressed && om qa

**2. Use Natural Language:**

Instead of remembering exact commands, just describe how you feel:

.. code-block:: bash

   om stressed    # → Breathing exercise
   om anxious     # → Grounding technique
   om grateful    # → Gratitude practice

**3. Emergency Access:**

Remember these for crisis moments:

.. code-block:: bash

   om crisis      # Crisis resources
   om panic       # Immediate grounding
   om help        # Emergency help

**4. Build Habits:**

Start small and build consistency:

- Week 1: Just ``om qm`` daily
- Week 2: Add ``om qb`` when stressed
- Week 3: Add ``om qg`` for gratitude
- Week 4: Explore ``om coach daily``

🎯 What's Next?
===============

Now that you're set up, explore these areas:

**Core Features:**

- :doc:`mood_tracking` - Comprehensive emotional awareness
- :doc:`breathing_exercises` - Stress relief and focus
- :doc:`gratitude_practice` - Positive psychology techniques

**Advanced Features:**

- :doc:`ai_coaching` - Personalized mental health insights
- :doc:`wellness_autopilot` - Automated wellness management
- :doc:`visual_dashboard` - Beautiful progress visualization

**Mental Health Support:**

- :doc:`anxiety_management` - Anxiety coping strategies
- :doc:`depression_support` - Depression management tools
- :doc:`crisis_support` - Emergency resources and support

**Technical:**

- :doc:`database_system` - Understanding your data
- :doc:`cli_reference` - Complete command reference
- :doc:`shortcuts_reference` - All available shortcuts

🌟 Remember
===========

Mental health is a journey, not a destination. om is here to support you every step of the way:

- **Start small** - Even one mood check per day makes a difference
- **Be consistent** - Regular practice builds lasting habits
- **Celebrate progress** - Use visual mode to appreciate your growth
- **Seek help when needed** - om complements but doesn't replace professional care

**You matter, your mental health matters, and help is available.**

💝 **Take care of yourself. You deserve wellness and happiness.**

---

**Ready to begin your wellness journey? Start with:** ``om qm``
