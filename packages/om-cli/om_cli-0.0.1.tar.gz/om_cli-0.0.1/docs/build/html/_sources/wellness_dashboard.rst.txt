Wellness Dashboard
==================

The Wellness Dashboard provides a comprehensive overview of your mental health journey, displaying key metrics, progress tracking, and personalized insights in a beautiful, easy-to-understand format.

Overview
--------

The dashboard serves as your mental health command center, bringing together data from all om features into a unified view. It shows your current wellness state, recent progress, and actionable insights to guide your mental health journey.

**Key Features:**
- Real-time wellness metrics
- Progress visualization
- Achievement highlights
- AI-powered insights
- Trend analysis
- Quick action suggestions

Quick Start
-----------

Access your wellness dashboard with::

    om dashboard
    om dashboard show    # Static overview
    om dashboard live    # Live updating dashboard
    om d                 # Quick alias

Dashboard Sections
------------------

Current Wellness State
~~~~~~~~~~~~~~~~~~~~~~

**Wellness Score**: Overall wellness rating (1-10) based on:
- Recent mood entries
- Activity consistency
- Sleep quality
- Stress levels
- Achievement progress

**Today's Summary**:
- Current mood status
- Completed wellness activities
- Streak information
- Daily challenge progress

Recent Activity
~~~~~~~~~~~~~~~

**7-Day Overview**:
- Mood trend visualization
- Activity completion rates
- Sleep quality patterns
- Stress level changes

**Activity Breakdown**:
- Breathing sessions completed
- Meditation minutes
- Gratitude entries
- Physical exercises
- CBT toolkit usage

Progress Tracking
~~~~~~~~~~~~~~~~~

**Streaks and Consistency**:
- Current wellness streaks
- Weekly consistency scores
- Monthly progress indicators
- Long-term trend analysis

**Achievement Highlights**:
- Recently unlocked achievements
- Progress toward next milestones
- Level and XP information
- Completion percentages

AI Insights
~~~~~~~~~~~

**Personalized Recommendations**:
- Suggested activities based on patterns
- Optimal timing for wellness practices
- Areas for improvement
- Celebration of progress

**Pattern Recognition**:
- Mood pattern insights
- Activity effectiveness analysis
- Trigger identification
- Success factor analysis

Dashboard Commands
------------------

Basic Dashboard
~~~~~~~~~~~~~~~

View your standard wellness overview::

    om dashboard
    om dashboard show

This displays:
- Current wellness score
- Today's activity summary
- Recent mood trends
- Achievement highlights
- Quick recommendations

Live Dashboard
~~~~~~~~~~~~~~

Real-time updating dashboard::

    om dashboard live
    om dashboard live 30    # Update every 30 seconds

Features:
- Auto-refreshing metrics
- Real-time activity tracking
- Live mood updates
- Dynamic recommendations

Dashboard Export
~~~~~~~~~~~~~~~~

Export dashboard data for external analysis::

    om dashboard export
    om dashboard export csv
    om dashboard export json

Export includes:
- All wellness metrics
- Historical data
- Achievement records
- Activity logs

Quick Summary
~~~~~~~~~~~~~

Condensed dashboard view::

    om dashboard summary
    om dashboard quick

Shows only:
- Wellness score
- Today's key metrics
- Current streaks
- Urgent recommendations

Dashboard Customization
-----------------------

Display Options
~~~~~~~~~~~~~~~

Customize what appears on your dashboard::

    om dashboard config
    
Options include:
- Metric visibility
- Time range settings
- Chart preferences
- Color themes
- Update frequency

Privacy Settings
~~~~~~~~~~~~~~~~

Control data display::

    om dashboard privacy
    
Settings:
- Hide sensitive metrics
- Anonymize data exports
- Limit historical display
- Secure mode options

Data Integration
----------------

The dashboard pulls data from all om modules:

**Mood Tracking**
    - Daily mood entries
    - Emotional patterns
    - Intensity trends
    - Trigger analysis

**Activity Modules**
    - Breathing session counts
    - Meditation minutes
    - Gratitude entries
    - Physical exercise logs

**Mental Health Tools**
    - CBT toolkit usage
    - AI companion interactions
    - Crisis support access
    - Sleep optimization data

**Gamification**
    - Achievement progress
    - XP and level information
    - Streak tracking
    - Challenge completion

Wellness Metrics
----------------

Wellness Score Calculation
~~~~~~~~~~~~~~~~~~~~~~~~~~

Your wellness score (1-10) is calculated from:

**Mood Component (30%)**
    - Average mood rating
    - Mood stability
    - Positive trend bonus

**Activity Component (25%)**
    - Consistency of wellness practices
    - Variety of activities
    - Daily completion rates

**Sleep Component (20%)**
    - Sleep quality ratings
    - Sleep duration consistency
    - Sleep hygiene practices

**Stress Management (15%)**
    - Stress level trends
    - Coping strategy usage
    - Crisis support needs

**Growth Component (10%)**
    - New skill development
    - Achievement unlocks
    - Learning engagement

Trend Analysis
~~~~~~~~~~~~~~

**Short-term Trends (7 days)**
    - Daily fluctuations
    - Weekly patterns
    - Recent improvements

**Medium-term Trends (30 days)**
    - Monthly progress
    - Seasonal patterns
    - Habit formation

**Long-term Trends (90+ days)**
    - Overall trajectory
    - Major milestones
    - Life event impacts

Visual Features
---------------

Charts and Graphs
~~~~~~~~~~~~~~~~~~

**Mood Line Chart**
    - Daily mood trends
    - 7-day moving average
    - Significant events marked

**Activity Heatmap**
    - Daily activity completion
    - Consistency visualization
    - Gap identification

**Progress Bars**
    - Achievement progress
    - Streak indicators
    - Goal completion

**Wellness Gauge**
    - Current wellness score
    - Target ranges
    - Historical comparison

Color Coding
~~~~~~~~~~~~

**Green**: Positive trends, good progress
**Yellow**: Neutral state, room for improvement
**Red**: Concerning patterns, needs attention
**Blue**: Information, neutral data
**Purple**: Achievements, celebrations

Dashboard Insights
------------------

AI-Powered Analysis
~~~~~~~~~~~~~~~~~~~

The dashboard uses AI to provide:

**Pattern Recognition**
    - "Your mood improves after breathing exercises"
    - "Stress levels are highest on Mondays"
    - "Sleep quality affects next-day wellness"

**Personalized Suggestions**
    - "Try meditation when stress is high"
    - "Your best wellness time is 9 AM"
    - "Consider CBT tools for anxiety patterns"

**Progress Celebrations**
    - "7-day meditation streak achieved!"
    - "Mood stability improved 20% this month"
    - "New personal wellness record!"

Actionable Recommendations
~~~~~~~~~~~~~~~~~~~~~~~~~~

Based on your data, the dashboard suggests:

**Immediate Actions**
    - Quick mood check if overdue
    - Breathing exercise for stress
    - Gratitude practice for mood boost

**Daily Practices**
    - Optimal times for activities
    - Recommended session lengths
    - Priority wellness tasks

**Weekly Goals**
    - Consistency improvements
    - New skill development
    - Challenge participation

Privacy and Data
----------------

Local Storage
~~~~~~~~~~~~~

All dashboard data is stored locally in::

    ~/.om/wellness_stats.json
    ~/.om/dashboard_config.json

Privacy Features:
- No external data transmission
- User-controlled data retention
- Secure local storage
- Easy data deletion

Data Export
~~~~~~~~~~~

Export your dashboard data::

    om dashboard export --format json
    om dashboard export --range 30d
    om dashboard export --anonymize

Export options:
- Multiple formats (JSON, CSV)
- Date range selection
- Data anonymization
- Selective export

Integration with om
-------------------

The dashboard integrates with all om features:

**Quick Actions**
    - Launch activities from dashboard
    - One-click wellness practices
    - Rapid mood updates

**AI Companion**
    - Dashboard insights in conversations
    - Progress discussions
    - Goal setting support

**Gamification**
    - Achievement displays
    - Progress celebrations
    - Streak visualizations

**Crisis Support**
    - Wellness alerts
    - Automatic resource suggestions
    - Emergency contact integration

Troubleshooting
---------------

**Dashboard Not Loading**
    - Check data file permissions
    - Verify module installation
    - Clear cache: `om dashboard --clear-cache`

**Missing Data**
    - Ensure modules are active
    - Check data file integrity
    - Rebuild dashboard: `om dashboard --rebuild`

**Performance Issues**
    - Reduce update frequency
    - Limit historical data display
    - Use summary view instead

**Export Problems**
    - Check file permissions
    - Verify export directory
    - Try different format

Command Reference
-----------------

.. code-block:: bash

    # Basic dashboard
    om dashboard              # Show main dashboard
    om dashboard show         # Static dashboard view
    om d                      # Quick alias
    
    # Live dashboard
    om dashboard live         # Auto-updating dashboard
    om dashboard live 60      # Update every 60 seconds
    
    # Dashboard variants
    om dashboard summary      # Quick summary view
    om dashboard quick        # Condensed view
    
    # Data export
    om dashboard export       # Export all data
    om dashboard export csv   # Export as CSV
    om dashboard export json  # Export as JSON
    
    # Configuration
    om dashboard config       # Configure display
    om dashboard privacy      # Privacy settings
    om dashboard --rebuild    # Rebuild dashboard data

Best Practices
--------------

**Regular Monitoring**
    - Check dashboard daily for insights
    - Review weekly trends
    - Celebrate monthly progress

**Data Quality**
    - Maintain consistent data entry
    - Use all om features regularly
    - Keep sleep and mood logs current

**Goal Setting**
    - Set realistic wellness targets
    - Track progress consistently
    - Adjust goals based on insights

**Privacy Awareness**
    - Regularly review privacy settings
    - Secure data exports
    - Understand data retention

See Also
--------

* :doc:`wellness_gamification` - Achievement and gamification system
* :doc:`mental_health_coach` - AI coaching insights
* :doc:`mood_tracking` - Mood data integration
* :doc:`quick_actions` - Dashboard quick actions
