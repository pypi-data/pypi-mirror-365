AI Mental Health Companion
==========================

The AI Mental Health Companion provides 24/7 conversational support, crisis detection, and personalized mental health guidance. Inspired by successful apps like Woebot, Wysa, EmoBay, and Youper.

Overview
--------

The AI Companion offers:

* **24/7 Conversational Support**: Always available for mental health conversations
* **Crisis Detection**: Automatic identification of concerning language patterns
* **Mood-Based Responses**: Contextual support based on emotional state
* **Personalized Check-ins**: Tailored interactions based on your history
* **Learning System**: Adapts to your patterns and preferences over time
* **CBT-Informed Conversations**: Incorporates cognitive behavioral therapy principles

Quick Start
-----------

Access the AI Companion with any of these commands::

    om ai
    om companion
    om chat
    om talk

Features
--------

Chat Session
~~~~~~~~~~~~

Start an interactive conversation::

    om ai chat
    om ai 1

The AI Companion provides:

* **Natural Conversation**: Responds to your thoughts and feelings
* **Active Listening**: Acknowledges and validates your experiences
* **Gentle Guidance**: Offers suggestions without being prescriptive
* **Crisis Support**: Immediately provides resources if concerning language is detected

Example conversation::

    You: I'm feeling really anxious about my presentation tomorrow
    
    AI: I hear that you're feeling anxious about your presentation. 
        That takes courage to share. Anxiety can feel overwhelming. 
        Let's take this one step at a time.
        
        What thoughts are racing through your mind about the presentation?

Personalized Check-in
~~~~~~~~~~~~~~~~~~~~~

Get a tailored check-in based on your history::

    om ai checkin
    om ai 2

The check-in considers:

* **Previous Conversations**: References past discussions when relevant
* **Time Since Last Contact**: Acknowledges gaps in communication
* **Mood Patterns**: Adapts based on your recent emotional state
* **Personal Preferences**: Uses learned information about what helps you

Mood-Based Suggestions
~~~~~~~~~~~~~~~~~~~~~~

Receive personalized recommendations::

    om ai suggestions
    om ai 3

The AI analyzes your recent conversation patterns to suggest:

* **Anxiety Management**: When anxiety themes are frequent
* **Depression Support**: For persistent low mood patterns
* **Positive Reinforcement**: When you're doing well
* **Maintenance Strategies**: For balanced emotional states

Conversation Insights
~~~~~~~~~~~~~~~~~~~~~

View analytics about your conversations::

    om ai insights
    om ai 4

Insights include:

* **Conversation Statistics**: Total conversations, active days
* **Mood Distribution**: Patterns in emotional states
* **Crisis Support History**: Times emergency resources were provided
* **Progress Indicators**: Changes in conversation tone over time

AI Response System
------------------

Mood Detection
~~~~~~~~~~~~~~

The AI analyzes your text for emotional indicators:

**Crisis Keywords**
    Detects concerning language and immediately provides crisis resources

**Positive Indicators**
    Words like: good, great, happy, excited, wonderful, amazing

**Anxiety Indicators**
    Words like: anxious, worried, nervous, panic, stress, overwhelmed

**Low Mood Indicators**
    Words like: sad, depressed, down, terrible, awful, hopeless

**Neutral State**
    Balanced or unclear emotional indicators

Response Templates
~~~~~~~~~~~~~~~~~~

The AI uses contextual response templates:

**For Anxiety**::

    "Anxiety can feel overwhelming. Let's take this one step at a time."
    "I notice you're feeling anxious. What thoughts are racing through your mind?"
    "When anxiety hits, grounding can help. Can you name 3 things you can see right now?"

**For Low Mood**::

    "I hear that you're going through a tough time. That takes courage to share."
    "It sounds like things feel heavy right now. You're not alone in this."
    "What's one small thing that usually brings you comfort?"

**For Positive States**::

    "It's wonderful to hear you're doing well! What's contributing to these good feelings?"
    "I love hearing positive updates! What's been the highlight of your day?"

CBT-Informed Questions
~~~~~~~~~~~~~~~~~~~~~~

The AI incorporates CBT principles with questions like:

* "What evidence do you have for that thought?"
* "How would you advise a friend in this situation?"
* "What's the worst that could realistically happen?"
* "Are you taking responsibility for something outside your control?"
* "What would be a more balanced way to see this?"

Crisis Detection & Response
----------------------------

Crisis Keywords
~~~~~~~~~~~~~~~

The system monitors for concerning language:

* suicide, kill myself, end it all
* not worth living, better off dead
* hurt myself, self harm
* hopeless, can't go on
* want to die, no point, give up

Crisis Response
~~~~~~~~~~~~~~~

When crisis language is detected, the AI immediately:

1. **Acknowledges Concern**: "I'm concerned about what you've shared"
2. **Provides Resources**: Lists crisis hotlines and emergency contacts
3. **Emphasizes Support**: "You matter. You are not alone. Help is available."
4. **Logs Incident**: Records for pattern analysis (while maintaining privacy)

Emergency Resources Provided::

    🆘 IMMEDIATE HELP:
    • National Suicide Prevention Lifeline: 988
    • Crisis Text Line: Text HOME to 741741
    • Emergency Services: 911

Data Storage & Privacy
----------------------

Conversation Storage
~~~~~~~~~~~~~~~~~~~~

Conversations are stored locally in::

    ~/.om/ai_conversations.json    # Chat history (last 100 exchanges)
    ~/.om/ai_user_profile.json     # Learned preferences and patterns

Privacy Features:

* **Local Only**: All data stays on your device
* **Limited History**: Only keeps last 100 conversations
* **No External Transmission**: Never sent to external servers
* **User Control**: You can delete data anytime

User Profile Learning
~~~~~~~~~~~~~~~~~~~~~

The AI learns and stores:

* **Preferred Coping Strategies**: What techniques work for you
* **Common Triggers**: Patterns in what causes distress
* **Positive Activities**: What brings you joy and comfort
* **Communication Style**: How you prefer to interact

Conversation Structure
~~~~~~~~~~~~~~~~~~~~~~

Each conversation exchange is stored as::

    {
        "timestamp": "2024-01-15T14:30:00",
        "user_input": "I'm feeling overwhelmed with work",
        "ai_response": "I hear that work is feeling overwhelming...",
        "mood": "anxiety",
        "crisis_detected": false
    }

Integration with om
-------------------

The AI Companion integrates with other om features:

**CBT Toolkit**
    Suggests CBT exercises when appropriate

**Crisis Support**
    Seamlessly escalates to crisis resources

**Mood Tracking**
    Incorporates mood data into conversations

**Sleep Support**
    Recommends sleep tools for fatigue-related issues

**Positive Psychology**
    Suggests gratitude and optimism exercises

Therapeutic Approach
--------------------

The AI Companion follows evidence-based principles:

**Person-Centered**
    Focuses on your experience and perspective

**Non-Judgmental**
    Accepts your thoughts and feelings without criticism

**Collaborative**
    Works with you rather than directing you

**Strengths-Based**
    Highlights your capabilities and resources

**Trauma-Informed**
    Sensitive to potential trauma history

**Crisis-Aware**
    Prioritizes safety and appropriate resource connection

Best Practices
--------------

**Regular Check-ins**
    Use the AI companion for routine mental health maintenance

**Honest Communication**
    Share authentically for more helpful responses

**Professional Support**
    Remember this supplements, not replaces, professional care

**Crisis Resources**
    Always use emergency services for immediate safety concerns

**Privacy Awareness**
    While data is local, be mindful of shared devices

Command Reference
-----------------

.. code-block:: bash

    # Main AI menu
    om ai
    
    # Specific features
    om ai chat            # Start chat session
    om ai checkin         # Personalized check-in
    om ai suggestions     # Mood-based suggestions
    om ai insights        # Conversation analytics
    
    # Aliases
    om companion          # Same as 'om ai'
    om chat              # Same as 'om ai chat'
    om talk              # Same as 'om ai chat'

Advanced Features
-----------------

Conversation Patterns
~~~~~~~~~~~~~~~~~~~~~

The AI tracks patterns to provide better support:

* **Time of Day**: When you typically need support
* **Emotional Cycles**: Recurring mood patterns
* **Trigger Identification**: Common stressors
* **Effective Interventions**: What helps you most

Learning Adaptation
~~~~~~~~~~~~~~~~~~~

Over time, the AI companion:

* **Personalizes Responses**: Uses language that resonates with you
* **Suggests Relevant Tools**: Recommends om features you find helpful
* **Adjusts Timing**: Learns when you're most receptive to suggestions
* **Builds Rapport**: Develops a consistent, supportive relationship

Limitations
-----------

**Not a Replacement for Therapy**
    Professional mental health care is irreplaceable

**Limited Context**
    Cannot access external information about your life

**Pattern Recognition**
    May miss subtle emotional cues

**Crisis Response**
    Cannot provide immediate physical intervention

**Learning Curve**
    Takes time to understand your unique patterns

Troubleshooting
---------------

**Repetitive Responses**
    Clear conversation history or restart the session

**Inappropriate Suggestions**
    The AI is learning; provide feedback through continued use

**Crisis Detection Issues**
    Always use direct crisis resources if AI doesn't respond appropriately

**Data Concerns**
    Delete ~/.om/ai_conversations.json to clear history

See Also
--------

* :doc:`cbt_toolkit` - Cognitive behavioral therapy tools
* :doc:`crisis_support` - Emergency mental health resources
* :doc:`mood_tracking` - Comprehensive mood monitoring
* :doc:`positive_psychology` - Positive psychology practices
