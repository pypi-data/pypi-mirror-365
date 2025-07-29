Positive Affirmations
====================

The Positive Affirmations module provides daily positive affirmations to support mental health and wellbeing. Inspired by the dulce-affirmations-api by misselliev, this module includes a comprehensive collection of affirmations for self-love, healing, confidence, and personal growth.

.. note::
   This module includes affirmations from The 1975's Mindshower.ai for The Birthday Party, curated through the dulce-affirmations-api project.

Features
--------

* **Daily Affirmations**: Get a unique positive affirmation each day
* **Categorized Content**: Affirmations organized by themes (self-love, healing, confidence, etc.)
* **Personal Tracking**: Track your favorite affirmations and progress
* **Streak Tracking**: Monitor your daily affirmation practice consistency
* **Search Functionality**: Find specific affirmations by keywords
* **Beautiful Display**: Rich terminal formatting with category-specific colors
* **Privacy-First**: All data stored locally, no external dependencies

Affirmation Categories
---------------------

The module organizes affirmations into meaningful categories:

**Self-Love** 💖
  Affirmations for self-acceptance and self-worth
  
  * "I love and approve of myself"
  * "I am worthy of love and respect"
  * "I accept myself exactly as I am"

**Healing** 🌿
  Affirmations for physical and emotional healing
  
  * "My body heals quickly and easily"
  * "I am restoring myself to perfect health"
  * "Love flows through my body healing all dis-ease"

**Confidence** 💪
  Affirmations for building confidence and courage
  
  * "I have the courage to live my dreams"
  * "I'm courageous and stand up for myself"
  * "I claim my power and move beyond all limitations"

**Abundance** ✨
  Affirmations for prosperity and success
  
  * "My income is constantly increasing"
  * "I attract money easily into my life"
  * "I prosper wherever I turn"

**Relationships** 💕
  Affirmations for healthy relationships
  
  * "I attract only healthy relationships"
  * "All of my relationships are positive and filled with love"
  * "I radiate love and others reflect love back to me"

**Peace** 🕊️
  Affirmations for inner peace and calm
  
  * "I choose to be at peace"
  * "I am calm, clear and confident"
  * "Peace and harmony flow through my body"

**Health** 🌱
  Affirmations for physical and mental health
  
  * "I am healthy, whole, and complete"
  * "Wellness is the natural state of my body"
  * "Every cell in my body vibrates with energy and health"

**Gratitude** 🙏
  Affirmations for thankfulness and appreciation
  
  * "My day begins and ends with gratitude"
  * "I am filled with gratitude for all that I have"
  * "I am grateful for my healthy body"

Usage
-----

Basic Commands
~~~~~~~~~~~~~

Get your daily affirmation:

.. code-block:: bash

   om affirmations daily
   # or simply
   om affirmations

Get a random affirmation:

.. code-block:: bash

   om affirmations random

View all categories:

.. code-block:: bash

   om affirmations categories

Get affirmations from a specific category:

.. code-block:: bash

   om affirmations category self-love
   om affirmations category healing
   om affirmations category confidence

Search for specific affirmations:

.. code-block:: bash

   om affirmations search "love"
   om affirmations search "healing"
   om affirmations search "success"

Personal Tracking
~~~~~~~~~~~~~~~~

Add current daily affirmation to favorites:

.. code-block:: bash

   om affirmations favorite

View your favorite affirmations:

.. code-block:: bash

   om affirmations favorites

View your statistics and progress:

.. code-block:: bash

   om affirmations stats

Command Aliases
--------------

The affirmations module supports several convenient aliases:

.. code-block:: bash

   om affirmations    # Full command
   om affirm          # Short alias
   om positive        # Descriptive alias
   om daily_affirmation  # Explicit alias
   om inspire         # Motivational alias
   om motivation      # Alternative alias

All aliases support the same subcommands:

.. code-block:: bash

   om affirm daily
   om positive random
   om inspire categories
   om motivation favorites

Integration with om Platform
---------------------------

The affirmations module integrates seamlessly with other om features:

**Mood Tracking Integration**
  * Correlate affirmations with mood improvements
  * Track emotional impact of different affirmation categories
  * Suggest affirmations based on current mood

**Mental Health Classification**
  * Recommend affirmations based on classified mental health patterns
  * Provide targeted support for specific concerns
  * Track effectiveness of affirmations for different conditions

**Gamification System**
  * Earn achievements for consistent affirmation practice
  * Track streaks and milestones
  * Level up your wellness journey with daily affirmations

**Dashboard Integration**
  * View affirmation statistics in wellness dashboard
  * Monitor progress and trends over time
  * See impact on overall mental health metrics

Statistics and Progress Tracking
-------------------------------

The module tracks comprehensive statistics about your affirmation practice:

**Usage Metrics**
  * Total affirmations viewed
  * Number of favorites saved
  * Current daily streak
  * Longest streak achieved
  * Average rating given to affirmations

**Progress Indicators**
  * 🌱 New to affirmations (1-2 days)
  * ✨ Building momentum (3-6 days)
  * ⚡ Strong practice (7-29 days)
  * 🔥 Dedicated practitioner (30+ days)

**Category Exploration**
  * Track which categories you explore most
  * Identify patterns in your affirmation preferences
  * Discover new categories to expand your practice

Example Usage Session
--------------------

Here's a typical daily affirmation session:

.. code-block:: bash

   $ om affirmations daily
   
   ╭───────────────────────────── ✨ Daily Affirmation - Self-Love ✨ ──────────────────────────────╮
   │                                                                                                │
   │                 "I am safe in the universe and all life loves and supports me"                 │
   │                                                                                                │
   ╰────────────────────────────────────────────────────────────────────────────────────────────────╯

   $ om affirmations favorite
   Rate this affirmation (1-5) [5]: 5
   Add notes (optional): This really resonated with me today
   ✅ Added to favorites!

   $ om affirmations stats
   
            📊 Your Affirmation Journey          
    Total Viewed          15               👁️     
    Favorites             3                💖    
    Current Streak        7 days           ⚡    
    Average Rating        4.7/5            ⭐    

   ⚡ Great job! You're developing a wonderful habit!

Data Storage and Privacy
-----------------------

All affirmation data is stored locally in ``~/.om/affirmations.db``:

**Local Storage Benefits**
  * Complete privacy - no data leaves your device
  * Works offline - no internet connection required
  * Fast access - instant loading of affirmations
  * User control - you own your data completely

**Database Tables**
  * ``affirmations`` - Core affirmation content
  * ``daily_affirmations`` - Daily affirmation log
  * ``user_affirmations`` - Personal favorites and ratings
  * ``categories`` - Affirmation category definitions
  * ``affirmation_stats`` - Usage statistics and progress

**Data Export**
  All data can be exported for backup or analysis through the om backup system.

Customization and Extension
--------------------------

The affirmations module is designed to be extensible:

**Custom Categories**
  Add your own affirmation categories through the database

**Personal Affirmations**
  Create and store your own custom affirmations

**Integration APIs**
  Connect with other wellness apps and services

**Reminder System**
  Set up daily reminders for affirmation practice (coming soon)

Best Practices
--------------

**Daily Practice**
  * Set a consistent time for daily affirmations
  * Start with just one affirmation per day
  * Take time to really absorb and reflect on each affirmation
  * Rate affirmations to track what resonates with you

**Mindful Engagement**
  * Read affirmations slowly and thoughtfully
  * Repeat affirmations that particularly resonate
  * Visualize the affirmation as true in your life
  * Use affirmations during meditation or quiet moments

**Progress Tracking**
  * Check your statistics regularly to stay motivated
  * Celebrate streak milestones and achievements
  * Explore different categories to broaden your practice
  * Add meaningful notes to your favorite affirmations

**Integration with Wellness**
  * Use affirmations alongside mood tracking
  * Combine with breathing exercises for deeper impact
  * Share meaningful affirmations with friends and family
  * Apply affirmation principles in daily life situations

Troubleshooting
--------------

**Database Issues**

If affirmations aren't loading:

.. code-block:: bash

   # Reinitialize the database
   rm ~/.om/affirmations.db
   sqlite3 ~/.om/affirmations.db < affirmations_schema.sql

**Missing Affirmations**

If the affirmation database seems empty:

.. code-block:: bash

   # The database will auto-populate on first use
   om affirmations daily

**Statistics Not Updating**

If statistics aren't tracking properly:

.. code-block:: bash

   # Check database integrity
   sqlite3 ~/.om/affirmations.db "PRAGMA integrity_check;"

Future Enhancements
------------------

Planned improvements include:

* **Reminder System**: Customizable daily reminders
* **Audio Affirmations**: Spoken affirmations with different voices
* **Affirmation Cards**: Visual affirmation cards for sharing
* **Community Features**: Share and discover affirmations from others
* **Mood Integration**: Automatic affirmation suggestions based on mood
* **Custom Collections**: Create themed affirmation collections
* **Export Options**: Export affirmations as images or PDFs
* **Multi-language Support**: Affirmations in multiple languages

Contributing
-----------

To contribute to the affirmations module:

1. **Content**: Suggest new affirmations or categories
2. **Features**: Propose new functionality or improvements
3. **Testing**: Test with different usage patterns
4. **Documentation**: Improve user guides and examples
5. **Integration**: Develop connections with other om modules

See the main om repository for contribution guidelines.

Inspiration and Credits
----------------------

This module is inspired by:

* **dulce-affirmations-api** by Elizabeth Villalejos (misselliev)
* **The 1975's Mindshower.ai** for The Birthday Party
* **Louise Hay's** pioneering work on positive affirmations
* **The om community** for feedback and suggestions

The affirmations included are sourced from the dulce-affirmations-api project, which compiled positive affirmations for mental health and wellness support.

Support
-------

For support with the affirmations module:

* **Technical Issues**: Check the om GitHub repository
* **Content Suggestions**: Submit new affirmations or categories
* **General Questions**: Use the om community forums

Remember: Positive affirmations are most effective when practiced consistently and with genuine intention. They work best as part of a comprehensive approach to mental health and wellness.
