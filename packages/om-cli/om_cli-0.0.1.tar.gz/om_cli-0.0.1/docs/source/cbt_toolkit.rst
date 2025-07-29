CBT Toolkit
===========

The CBT (Cognitive Behavioral Therapy) Toolkit provides evidence-based tools for managing thoughts, emotions, and behaviors. Inspired by successful apps like MindShift CBT, Quirk, and Sanvello.

Overview
--------

CBT is one of the most researched and effective forms of psychotherapy. The CBT Toolkit in om provides:

* **Thought Challenging**: Systematic examination of negative thoughts
* **Cognitive Distortion Identification**: Recognition of unhelpful thinking patterns
* **Anxiety Coping Strategies**: Evidence-based techniques for managing anxiety
* **Mood-Thought Connection**: Understanding the relationship between thoughts and feelings
* **Daily CBT Exercises**: Regular practice for building mental resilience

Quick Start
-----------

Access the CBT Toolkit with any of these commands::

    om cbt
    om cognitive
    om thoughts
    om thinking

Features
--------

Thought Challenging Session
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Interactive sessions to examine and reframe troubling thoughts::

    om cbt challenge
    om cbt 1

The thought challenging process follows these steps:

1. **Identify the Situation**: What triggered the thought?
2. **Capture the Thought**: What specific thought occurred?
3. **Notice the Emotion**: What did you feel and how intensely?
4. **Identify Distortions**: Check for cognitive distortions
5. **Challenge the Thought**: Use evidence-based questions
6. **Develop Balanced Thinking**: Create more realistic thoughts
7. **Reassess Emotions**: Notice changes in emotional intensity

Cognitive Distortions
~~~~~~~~~~~~~~~~~~~~~

The toolkit helps identify 10 common cognitive distortions:

**All-or-Nothing Thinking**
    Seeing things in black and white categories
    
    *Example*: "If I'm not perfect, I'm a total failure"

**Overgeneralization**
    Drawing broad conclusions from single events
    
    *Example*: "I failed this test, I'll never succeed at anything"

**Mental Filter**
    Focusing only on negative details
    
    *Example*: Ignoring positive feedback and focusing only on criticism

**Catastrophizing**
    Expecting the worst possible outcome
    
    *Example*: "If I make a mistake, I'll be fired and homeless"

**Mind Reading**
    Assuming you know what others are thinking
    
    *Example*: "They think I'm stupid"

**Fortune Telling**
    Predicting negative outcomes without evidence
    
    *Example*: "This will definitely go wrong"

**Emotional Reasoning**
    Believing feelings reflect reality
    
    *Example*: "I feel guilty, so I must have done something wrong"

**Should Statements**
    Using rigid rules about how things 'should' be
    
    *Example*: "I should never make mistakes"

**Labeling**
    Defining yourself or others with negative labels
    
    *Example*: "I'm such an idiot"

**Personalization**
    Taking responsibility for things outside your control
    
    *Example*: "It's my fault the team project failed"

Anxiety Coping Strategies
~~~~~~~~~~~~~~~~~~~~~~~~~

Access anxiety-specific CBT tools::

    om cbt anxiety
    om cbt 2

Available strategies include:

**5-4-3-2-1 Grounding**
    Name 5 things you see, 4 you hear, 3 you touch, 2 you smell, 1 you taste

**Worry Time**
    Schedule 15 minutes daily to worry, postpone anxious thoughts until then

**Probability Estimation**
    Rate the actual likelihood (0-100%) of your feared outcome

**Coping Statements**
    Prepare realistic, calming statements for anxious moments

**Behavioral Experiments**
    Test anxious predictions through small, safe experiments

Mood-Thought Tracker
~~~~~~~~~~~~~~~~~~~~

Track the connection between moods and thoughts::

    om cbt mood
    om cbt 3

This feature:

* Monitors current mood levels (1-10 scale)
* Identifies thought patterns
* Detects potentially unhelpful thinking
* Suggests thought challenging when needed

Daily CBT Exercise
~~~~~~~~~~~~~~~~~~

Get a daily CBT practice::

    om cbt daily
    om cbt 4

Daily exercises rotate through:

* **Gratitude + Reframe**: Combine gratitude with thought reframing
* **Evidence Gathering**: List evidence for and against worries
* **Behavioral Activation**: Plan mood-boosting activities
* **Mindful Observation**: Practice observing thoughts without judgment
* **Values Check-in**: Connect actions with core values

Data Storage
------------

CBT Toolkit data is stored locally in::

    ~/.om/cbt_thoughts.json      # Thought records
    ~/.om/cbt_exercises.json     # Exercise completions

All data remains private and under your control.

Thought Record Structure
~~~~~~~~~~~~~~~~~~~~~~~~

Each thought record contains::

    {
        "timestamp": "2024-01-15T10:30:00",
        "situation": "Meeting with boss",
        "original_thought": "I'm going to get fired",
        "original_emotion": "anxiety",
        "original_intensity": 8,
        "balanced_thought": "This is one meeting, not a performance review",
        "new_emotion": "nervous but manageable",
        "new_intensity": 4
    }

Clinical Integration
--------------------

The CBT Toolkit is designed to complement, not replace, professional therapy:

* **Self-Help Tool**: For between-session practice
* **Skill Building**: Develops CBT techniques
* **Progress Tracking**: Shows thought pattern changes over time
* **Crisis Support**: Integrates with om's crisis resources

Best Practices
--------------

**Regular Practice**
    Use CBT tools consistently, not just during crises

**Be Patient**
    Thought patterns take time to change

**Seek Professional Help**
    For persistent mental health concerns

**Use Crisis Resources**
    Access ``om rescue`` for immediate support needs

**Track Progress**
    Review past thought records to see improvement

Research Foundation
-------------------

The CBT Toolkit is based on decades of research showing CBT's effectiveness for:

* Depression
* Anxiety disorders
* Panic disorder
* Social anxiety
* Generalized anxiety disorder
* Post-traumatic stress disorder

Integration with om
-------------------

The CBT Toolkit integrates seamlessly with other om features:

* **AI Coach**: Provides CBT-informed insights
* **Mood Tracking**: Connects thoughts with mood patterns
* **Crisis Support**: Escalates to crisis resources when needed
* **Gamification**: Tracks CBT practice achievements
* **Dashboard**: Visualizes thought pattern improvements

Command Reference
-----------------

.. code-block:: bash

    # Main CBT menu
    om cbt
    
    # Specific features
    om cbt challenge        # Thought challenging session
    om cbt anxiety         # Anxiety coping strategies
    om cbt mood           # Mood-thought tracker
    om cbt daily          # Daily CBT exercise
    om cbt history        # View past thought records
    
    # Aliases
    om cognitive          # Same as 'om cbt'
    om thoughts          # Same as 'om cbt'
    om thinking          # Same as 'om cbt'

Troubleshooting
---------------

**Module Not Found**
    Ensure you're using the latest version of om

**Input Errors**
    Use Ctrl+C to exit any input prompt

**Data Issues**
    Check that ~/.om/ directory has write permissions

**Performance**
    Large thought record histories may slow loading

See Also
--------

* :doc:`ai_companion` - AI-powered mental health support
* :doc:`mood_tracking` - Comprehensive mood monitoring
* :doc:`anxiety_support` - Additional anxiety management tools
* :doc:`crisis_support` - Emergency mental health resources
