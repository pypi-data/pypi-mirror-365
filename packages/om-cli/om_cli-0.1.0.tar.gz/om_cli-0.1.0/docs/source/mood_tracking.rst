Mood Tracking
=============

Comprehensive mood tracking is the foundation of mental health awareness. om provides sophisticated tools for monitoring, analyzing, and understanding your emotional patterns.

🎯 Overview
===========

om's mood tracking system goes beyond simple "good" or "bad" ratings. It captures:

- **Multi-dimensional emotions** (mood, energy, stress, anxiety)
- **Contextual information** (triggers, location, activities)
- **Pattern recognition** (trends, cycles, correlations)
- **Predictive insights** (early warning systems)
- **Tag-based organization** (flexible categorization)

Quick Mood Check
================

The fastest way to log your mood:

.. code-block:: bash

   # Quick mood check (10 seconds)
   om qm

This prompts for:

1. **Mood rating** (1-10 scale)
2. **Optional notes** (context, triggers, thoughts)
3. **Follow-up suggestions** (based on your rating)

**Example interaction:**

.. code-block:: text

   📊 Quick Mood Check
   How are you feeling right now? (1-10): 7
   Any notes about your mood? (optional): Feeling productive after morning coffee
   
   ✅ Mood logged! (7/10)
   💡 Suggestion: Since you're feeling good, this might be a great time for a gratitude practice.
   
   Try: om qg

Enhanced Mood Tracking
======================

For deeper emotional awareness:

.. code-block:: bash

   # Comprehensive mood entry
   om mood

   # Enhanced mood tracking with full details
   om enhanced_mood add

**Enhanced tracking includes:**

- **Mood vocabulary** (60+ emotions across categories)
- **Intensity ratings** for multiple dimensions
- **Trigger identification** (work, relationships, health, etc.)
- **Coping strategies used**
- **Environmental factors** (location, weather, time)
- **Physical symptoms** (fatigue, tension, etc.)

Multi-Dimensional Tracking
==========================

Track multiple emotional dimensions simultaneously:

.. code-block:: bash

   # CLI with multiple dimensions
   om qm great 8 --energy 7 --stress 3 --anxiety 2 --notes "Great morning!"

**Dimensions tracked:**

- **Mood** (1-10): Overall emotional state
- **Energy** (1-10): Physical and mental energy levels
- **Stress** (1-10): Stress and pressure levels
- **Anxiety** (1-10): Anxiety and worry levels

**Database storage:**

.. code-block:: sql

   mood_entries:
   - mood (TEXT): Descriptive mood (great, good, okay, etc.)
   - level (INTEGER): Numeric mood rating (1-10)
   - energy_level (INTEGER): Energy rating (1-10)
   - stress_level (INTEGER): Stress rating (1-10)
   - anxiety_level (INTEGER): Anxiety rating (1-10)
   - notes (TEXT): Contextual information
   - date, time (TEXT): Timestamp
   - triggers (JSON): Array of trigger categories
   - coping_strategies (JSON): Strategies used

Tag System
==========

Organize mood entries with flexible tags:

.. code-block:: bash

   # Add mood with tags
   om qm good 7 --tags "work,productive,coffee"

   # View moods by tag
   om moods --tag work

**Common tag categories:**

- **Context**: work, home, social, travel
- **Activities**: exercise, meditation, reading, music
- **Triggers**: stress, conflict, deadlines, health
- **Emotions**: grateful, anxious, excited, tired
- **Physical**: headache, energized, tense, relaxed

**Tag management:**

.. code-block:: bash

   # List all tags
   om tags list

   # Most used tags
   om tags popular

   # Tag statistics
   om tags stats

Mood Analytics
==============

Gain insights from your mood data:

.. code-block:: bash

   # Comprehensive mood analytics
   om mood_analytics

   # Pattern analysis
   om coach analyze

   # Mood trends
   om moods trends

**Analytics include:**

**1. Basic Statistics:**

- Average mood, energy, stress, anxiety levels
- Mood distribution (how often each rating)
- Most common moods and tags
- Entry frequency and consistency

**2. Temporal Patterns:**

- **Time of day**: Morning vs. evening mood patterns
- **Day of week**: Monday blues, Friday energy, etc.
- **Monthly cycles**: Seasonal patterns, hormonal cycles
- **Long-term trends**: Improving, stable, or declining

**3. Correlation Analysis:**

- Mood vs. energy correlations
- Stress impact on overall mood
- Tag correlations (which tags appear together)
- Activity impact on emotional state

**4. Trigger Analysis:**

- Most common triggers for low moods
- Protective factors for good moods
- Trigger patterns over time
- Effectiveness of coping strategies

Pattern Recognition
==================

om's AI identifies meaningful patterns in your data:

**Automatic Pattern Detection:**

.. code-block:: bash

   # Get AI pattern insights
   om coach daily

   # Deep pattern analysis
   om patterns analyze

**Pattern types identified:**

- **Cyclical patterns**: Weekly, monthly, seasonal cycles
- **Trigger patterns**: Consistent mood responses to specific triggers
- **Recovery patterns**: How quickly you bounce back from low moods
- **Effectiveness patterns**: Which coping strategies work best for you
- **Warning patterns**: Early indicators of mood decline

**Example insights:**

.. code-block:: text

   🧠 Pattern Insights:
   
   📈 Your mood tends to be 15% higher on weekends
   ⚠️  Stress levels spike on Monday mornings (avg 7.2/10)
   ✅ Breathing exercises improve your mood by avg 1.8 points
   🔄 You typically recover from low moods within 2-3 days
   ⏰ Your energy peaks between 10am-12pm

Mood History
============

View and analyze your mood history:

.. code-block:: bash

   # Recent mood entries
   om moods list

   # Mood entries for specific period
   om moods --days 30

   # Mood entries with specific rating
   om moods --level 8-10

   # Export mood data
   om export --type mood --days 90

**History views:**

- **List view**: Chronological entries with details
- **Summary view**: Aggregated statistics
- **Trend view**: Visual trend indicators
- **Calendar view**: Mood calendar overlay

Crisis Detection
================

om monitors for concerning patterns:

**Automatic monitoring:**

- Multiple consecutive low mood entries (≤3)
- Sustained high stress levels (≥8)
- Sustained high anxiety levels (≥8)
- Absence of positive entries for extended periods
- Specific crisis-related tags or notes

**Crisis alerts:**

.. code-block:: bash

   # Check for urgent patterns
   om coach urgent

**Example alert:**

.. code-block:: text

   ⚠️  Concerning Pattern Detected
   
   Multiple low mood entries detected (3 entries ≤3 in past week)
   
   Immediate recommendations:
   • Consider reaching out to a mental health professional
   • Use crisis resources: om rescue
   • Try grounding technique: om qgr
   
   Crisis resources: Call 988 (Suicide & Crisis Lifeline)

Data Export & Backup
====================

Protect and analyze your mood data:

.. code-block:: bash

   # Export mood data
   om export --type mood

   # Export specific date range
   om export --type mood --days 30

   # Create full backup
   om backup

**Export formats:**

- **JSON**: Machine-readable format for analysis
- **CSV**: Spreadsheet-compatible format
- **SQLite**: Database format for advanced queries

**Privacy & Security:**

- All data stored locally in ``~/.om/om.db``
- No external data transmission
- User-controlled backups and exports
- Encrypted storage options (future enhancement)

Integration with Other Features
===============================

Mood tracking integrates with all om features:

**Gamification:**

- XP rewards for consistent mood tracking
- Achievements for tracking milestones
- Streak tracking for daily consistency

**AI Coaching:**

- Personalized insights based on mood patterns
- Recommendations tailored to your emotional state
- Crisis detection and intervention

**Wellness Autopilot:**

- Automated tasks based on mood trends
- Adaptive recommendations for mood improvement
- Smart scheduling based on energy patterns

**Visual Dashboard:**

- Mood trend visualizations
- Pattern recognition charts
- Achievement progress tracking

Best Practices
==============

**1. Consistency is Key:**

- Track mood at the same time daily
- Use quick check (``om qm``) for daily consistency
- Use enhanced tracking (``om mood``) for deeper insights

**2. Be Honest:**

- Rate your actual mood, not how you think you should feel
- Include context in notes (triggers, activities, thoughts)
- Don't judge your emotions - just observe and record

**3. Use Tags Effectively:**

- Develop consistent tag vocabulary
- Tag both positive and negative experiences
- Use tags to identify patterns and triggers

**4. Review Regularly:**

- Check analytics weekly (``om mood_analytics``)
- Review patterns monthly (``om coach analyze``)
- Celebrate progress with visual mode (``om gamify status -v``)

**5. Act on Insights:**

- Follow AI coaching recommendations
- Use identified patterns to make lifestyle changes
- Share insights with mental health professionals

Troubleshooting
===============

**Common Issues:**

**1. Inconsistent Tracking:**

.. code-block:: bash

   # Set up daily reminders
   om autopilot config

   # Check streak status
   om gamify status

**2. Unclear Patterns:**

- Need more data (track for at least 2 weeks)
- Use enhanced tracking for richer data
- Add more contextual tags and notes

**3. Data Concerns:**

.. code-block:: bash

   # Verify data integrity
   om status

   # Create backup
   om backup

   # Export for external analysis
   om export --type mood

**Getting Help:**

- Review :doc:`crisis_support` for mental health resources
- Check :doc:`troubleshooting` for technical issues
- Contact mental health professionals for clinical support

Next Steps
==========

After mastering mood tracking:

1. Explore :doc:`ai_coaching` for personalized insights
2. Learn :doc:`pattern_analysis` for deeper understanding
3. Set up :doc:`wellness_autopilot` for automated support
4. Use :doc:`visual_dashboard` for progress celebration

**Remember**: Mood tracking is a tool for awareness, not judgment. Every emotion is valid, and tracking helps you understand your patterns to make informed decisions about your mental health.

💝 **Your emotional awareness is the first step toward lasting wellness.**
