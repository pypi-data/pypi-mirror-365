Sleep Optimization
==================

The Sleep Optimization module provides evidence-based tools for improving sleep quality and timing. Inspired by successful apps like Nyxo and Wake Up Time, it uses sleep science to help you feel more rested.

Overview
--------

Sleep optimization in om provides:

* **Sleep Cycle Calculations**: Based on 90-minute sleep cycles
* **Optimal Timing**: Best bedtimes and wake times for feeling refreshed
* **Sleep Quality Tracking**: Monitor and improve your sleep patterns
* **Sleep Hygiene Education**: Evidence-based practices for better sleep
* **Pattern Analysis**: Identify trends in your sleep data
* **Power Nap Optimization**: Strategic napping for energy without grogginess

Quick Start
-----------

Access sleep optimization with any of these commands::

    om sleep
    om rest
    om nap

Sleep Science Foundation
------------------------

90-Minute Sleep Cycles
~~~~~~~~~~~~~~~~~~~~~~

Sleep occurs in cycles of approximately 90 minutes, consisting of:

1. **Light Sleep (N1)**: Transition from wakefulness
2. **Deep Sleep (N2)**: Body restoration and memory consolidation
3. **Deep Sleep (N3)**: Physical recovery and growth hormone release
4. **REM Sleep**: Dreaming, emotional processing, and learning

**Key Insight**: Waking up at the end of a complete cycle (rather than in the middle) helps you feel more refreshed and alert.

Sleep Latency
~~~~~~~~~~~~~

Most people take about 15 minutes to fall asleep after getting into bed. The sleep calculator accounts for this "sleep latency" when recommending bedtimes.

Features
--------

Optimal Wake Times
~~~~~~~~~~~~~~~~~~

Calculate the best wake times for a given bedtime::

    om sleep wake
    om sleep 1

Example usage::

    What time do you plan to go to bed? (HH:MM): 22:30
    
    💤 Optimal Wake Times for Bedtime: 22:30
    ========================================
    Assuming you fall asleep by: 22:45
    
    🌅 Best wake-up times (end of sleep cycles):
      00:15 - 6.0 hours (4 cycles)
      01:45 - 7.5 hours (5 cycles)  ← Recommended
      03:15 - 9.0 hours (6 cycles)

Optimal Bedtimes
~~~~~~~~~~~~~~~~

Calculate the best bedtimes for a target wake time::

    om sleep bedtime
    om sleep 2

Example usage::

    What time do you need to wake up? (HH:MM): 07:00
    
    🌙 Optimal Bedtimes for Wake Time: 07:00
    ========================================
    🛏️  Recommended bedtimes (including 15min to fall asleep):
      21:15 (previous day) - 6.0 hours (4 cycles)
      22:45 (previous day) - 7.5 hours (5 cycles)  ← Recommended
      00:15 - 9.0 hours (6 cycles)

Sleep Quality Tracking
~~~~~~~~~~~~~~~~~~~~~~~

Monitor your sleep patterns over time::

    om sleep track
    om sleep 3

The tracker records:

* **Bedtime and Wake Time**: Actual sleep schedule
* **Sleep Duration**: Total time in bed
* **Quality Rating**: Subjective sleep quality (1-10)
* **Sleep Latency**: Time taken to fall asleep
* **Night Wakings**: Number of times you woke up
* **Morning Feeling**: How you felt upon waking
* **Sleep Efficiency**: Percentage of time actually sleeping

Sleep Hygiene Tips
~~~~~~~~~~~~~~~~~~

Access evidence-based sleep improvement strategies::

    om sleep hygiene
    om sleep 4

Sleep hygiene categories include:

**Environment**
    * Keep bedroom cool (60-67°F/15-19°C)
    * Make room as dark as possible
    * Minimize noise or use white noise
    * Invest in comfortable mattress and pillows
    * Reserve bed for sleep and intimacy only

**Timing**
    * Keep consistent sleep/wake times, even weekends
    * Avoid naps after 3 PM
    * Stop caffeine 6+ hours before bedtime
    * Finish eating 2-3 hours before bed
    * Exercise regularly, but not close to bedtime

**Pre-Sleep Routine**
    * Start winding down 1 hour before bed
    * Avoid screens 1 hour before sleep
    * Try reading, gentle stretching, or meditation
    * Take a warm bath or shower
    * Practice relaxation techniques

**What to Avoid**
    * Alcohol close to bedtime (disrupts sleep cycles)
    * Large meals or spicy foods before bed
    * Intense exercise within 4 hours of sleep
    * Checking the clock if you wake up
    * Lying in bed awake for more than 20 minutes

Sleep Pattern Analysis
~~~~~~~~~~~~~~~~~~~~~~

Analyze your sleep trends::

    om sleep analyze
    om sleep 5

Analysis includes:

* **Average Sleep Duration**: Your typical sleep length
* **Average Sleep Quality**: Mean quality ratings
* **Best and Worst Nights**: Identify patterns
* **Consistency Metrics**: Bedtime and wake time variance
* **Recommendations**: Personalized suggestions based on your data

Power Nap Timer
~~~~~~~~~~~~~~~

Optimize napping for energy without grogginess::

    om sleep nap
    om sleep 6

Nap duration options:

**10-20 Minutes**
    * Quick refresh without entering deep sleep
    * No grogginess upon waking
    * Ideal for alertness boost

**30 Minutes**
    * Risk of sleep inertia (grogginess)
    * Generally not recommended

**90 Minutes**
    * Full sleep cycle
    * Wake up refreshed if you can spare the time
    * Good for significant sleep debt

Data Storage
------------

Sleep data is stored locally in::

    ~/.om/sleep_data.json

Data retention:

* **30-Day History**: Automatically removes data older than 30 days
* **Privacy First**: All data stays on your device
* **Export Capable**: Can be exported for external analysis

Sleep Entry Structure
~~~~~~~~~~~~~~~~~~~~~

Each sleep tracking entry contains::

    {
        "timestamp": "2024-01-15T08:00:00",
        "bedtime": "22:30",
        "wake_time": "07:00",
        "duration_hours": 8.5,
        "quality_rating": "7",
        "sleep_latency_minutes": "10",
        "night_wakings": "1",
        "morning_feeling": "refreshed",
        "sleep_efficiency": 94.1
    }

Sleep Recommendations
---------------------

Based on Sleep Research
~~~~~~~~~~~~~~~~~~~~~~~

**Most Adults Need 7-9 Hours**
    Corresponding to 5-6 complete sleep cycles

**Consistency Matters More Than Duration**
    Regular sleep/wake times are crucial for circadian rhythm

**Quality Over Quantity**
    Better to have 6 hours of uninterrupted sleep than 8 hours of fragmented sleep

**Individual Variation**
    Some people naturally need more or less sleep

Personalized Suggestions
~~~~~~~~~~~~~~~~~~~~~~~~

The system provides recommendations based on your data:

**Short Sleep Duration (< 7 hours)**
    * Try going to bed 30 minutes earlier
    * Check for sleep environment issues
    * Consider if caffeine or screen time is interfering

**Poor Sleep Quality (< 6/10)**
    * Review sleep hygiene practices
    * Look for patterns in low-quality nights
    * Consider stress management techniques

**Inconsistent Bedtimes (> 1 hour variance)**
    * Work toward more regular sleep schedule
    * Use bedtime reminders
    * Avoid "social jet lag" on weekends

Integration with om
-------------------

Sleep optimization integrates with other om features:

**Mood Tracking**
    Poor sleep often correlates with mood changes

**AI Companion**
    Discusses sleep issues and provides support

**Anxiety Support**
    Sleep problems often relate to anxiety

**Physical Wellness**
    Exercise timing affects sleep quality

**Dashboard**
    Visualizes sleep trends alongside other wellness metrics

Advanced Features
-----------------

Circadian Rhythm Support
~~~~~~~~~~~~~~~~~~~~~~~~

The module considers:

* **Natural Sleep Drive**: Builds throughout the day
* **Circadian Alerting**: Body's natural wake-promoting signals
* **Light Exposure**: Impact on melatonin production
* **Temperature Rhythms**: Body temperature changes affecting sleepiness

Sleep Debt Calculation
~~~~~~~~~~~~~~~~~~~~~~

Tracks cumulative sleep deficit:

* **Daily Deficit**: Difference between needed and actual sleep
* **Weekly Patterns**: Identifies chronic sleep debt
* **Recovery Recommendations**: Suggests catch-up strategies

Shift Work Support
~~~~~~~~~~~~~~~~~~

Special considerations for non-traditional schedules:

* **Flexible Cycle Calculations**: Adapts to any sleep schedule
* **Light Management**: Recommendations for shift workers
* **Nap Strategies**: Optimal napping for shift workers

Best Practices
--------------

**Consistent Tracking**
    Log sleep data regularly for meaningful patterns

**Gradual Changes**
    Adjust sleep schedule by 15-30 minutes at a time

**Environment Optimization**
    Invest in sleep environment improvements

**Professional Consultation**
    Consult a sleep specialist for persistent issues

**Patience with Changes**
    Sleep improvements take time to show results

Command Reference
-----------------

.. code-block:: bash

    # Main sleep menu
    om sleep
    
    # Specific features
    om sleep wake         # Calculate optimal wake times
    om sleep bedtime      # Calculate optimal bedtimes
    om sleep track        # Track sleep quality
    om sleep hygiene      # Sleep hygiene tips
    om sleep analyze      # Analyze sleep patterns
    om sleep nap          # Power nap timer
    
    # Aliases
    om rest              # Same as 'om sleep'
    om nap               # Same as 'om sleep nap'

Common Sleep Issues
-------------------

Insomnia
~~~~~~~~

If you have trouble falling or staying asleep:

* Use the sleep hygiene guidelines
* Try the 20-minute rule: If not asleep in 20 minutes, get up
* Consider relaxation techniques
* Access ``om insomnia`` for specialized support

Sleep Anxiety
~~~~~~~~~~~~~

If worry about sleep keeps you awake:

* Use CBT techniques: ``om cbt anxiety``
* Practice acceptance of occasional poor sleep
* Focus on rest rather than sleep
* Avoid clock-watching

Early Morning Awakening
~~~~~~~~~~~~~~~~~~~~~~~

If you wake up too early and can't get back to sleep:

* Check for depression symptoms
* Evaluate alcohol consumption
* Consider light exposure timing
* Maintain consistent wake times

Troubleshooting
---------------

**Calculation Errors**
    Ensure time format is HH:MM (24-hour format)

**Data Not Saving**
    Check ~/.om/ directory permissions

**Unrealistic Recommendations**
    Remember these are guidelines; adjust for your lifestyle

**Pattern Analysis Issues**
    Need at least 3 nights of data for meaningful analysis

See Also
--------

* :doc:`insomnia_support` - Specialized insomnia management
* :doc:`anxiety_support` - Anxiety's impact on sleep
* :doc:`mood_tracking` - Sleep-mood connections
* :doc:`physical_wellness` - Exercise and sleep relationship
