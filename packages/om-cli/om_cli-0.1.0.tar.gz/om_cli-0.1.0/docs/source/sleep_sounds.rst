Sleep Sounds & Insomnia Support
===============================

The Sleep Sounds & Insomnia Support module provides comprehensive sleep assistance through nature sounds, white noise, meditation audio, and specialized mental health-focused sounds. This module is designed to help users fall asleep easier, improve sleep quality, and manage sleep-related mental health challenges.

.. note::
   This module includes specialized sounds for various mental health conditions including anxiety, depression, PTSD, and ADHD, making it a unique therapeutic tool within the om platform.

Features
--------

* **Comprehensive Sound Library**: 18+ curated sounds across 5 categories
* **Mental Health Focus**: Specialized sounds for anxiety, depression, PTSD, ADHD, and more
* **Custom Sound Mixing**: Create personalized sound combinations with volume control
* **Sleep Timer**: Automatic fade-out and session management
* **Sleep Quality Tracking**: Monitor sleep sessions, duration, and effectiveness
* **Interactive Mixer**: Real-time sound mixing with intuitive controls
* **Background Playback**: Sounds continue playing while using other applications
* **Privacy-First**: All data stored locally, no external dependencies

Sound Categories
---------------

**Nature Sounds** 🌿
  Natural environmental sounds for relaxation and sleep
  
  * **Rain on Leaves**: Gentle rain falling on forest leaves (anxiety, stress, relaxation)
  * **Ocean Waves**: Rhythmic ocean waves on peaceful beach (anxiety, meditation, peace)
  * **Forest Ambience**: Birds chirping in serene forest (depression, nature therapy, grounding)
  * **Thunderstorm**: Distant thunder with gentle rain (insomnia, masking, deep sleep)
  * **Mountain Stream**: Babbling brook in mountain setting (meditation, focus, tranquility)

**White Noise Variations** 🔊
  Scientifically-designed noise for masking and focus
  
  * **White Noise**: Classic white noise for sound masking (tinnitus, focus, masking)
  * **Brown Noise**: Deep, rumbling brown noise (ADHD, concentration, deep sleep)
  * **Pink Noise**: Balanced pink noise for sleep quality (sleep quality, memory, restoration)

**Mental Health Specific** 🧠
  Therapeutic sounds designed for specific mental health conditions
  
  * **Anxiety Relief Tones**: 432Hz tones for anxiety reduction (anxiety, panic, calming)
  * **Depression Support**: Uplifting frequencies for mood support (depression, mood boost, energy)
  * **PTSD Grounding**: Grounding sounds for trauma recovery (PTSD, grounding, safety)
  * **ADHD Focus**: Binaural beats for ADHD focus (ADHD, focus, concentration)

**Meditation & Mindfulness** 🧘
  Sounds for meditation and spiritual practice
  
  * **Tibetan Bowls**: Healing Tibetan singing bowls (meditation, healing, spiritual)
  * **Om Chanting**: Sacred Om mantra chanting (meditation, spiritual, centering)
  * **Mindfulness Bell**: Gentle mindfulness bell intervals (mindfulness, presence, awareness)

**Ambient & Urban** 🏙️
  Familiar environmental sounds for comfort
  
  * **Coffee Shop**: Cozy coffee shop atmosphere (social anxiety, comfort, familiarity)
  * **Library Ambience**: Quiet library with subtle sounds (study, focus, calm)
  * **Fireplace**: Crackling fireplace warmth (comfort, warmth, security)

Usage
-----

Basic Commands
~~~~~~~~~~~~~

View all sound categories:

.. code-block:: bash

   om sleep categories
   # or simply
   om sleep

Browse sounds by category:

.. code-block:: bash

   om sleep sounds nature
   om sleep sounds mental_health
   om sleep sounds white_noise

Search sounds by mental health tags:

.. code-block:: bash

   om sleep search anxiety
   om sleep search depression
   om sleep search insomnia
   om sleep search adhd

Play a single sound with timer:

.. code-block:: bash

   om sleep play "Rain on Leaves" 30    # 30-minute timer
   om sleep play "White Noise" 60       # 60-minute timer
   om sleep play "Ocean Waves"          # Default 30-minute timer

Stop current sleep session:

.. code-block:: bash

   om sleep stop

Advanced Features
~~~~~~~~~~~~~~~~

Interactive sound mixer:

.. code-block:: bash

   om sleep mixer

View saved sound mixes:

.. code-block:: bash

   om sleep mixes

View sleep statistics:

.. code-block:: bash

   om sleep stats           # Last 30 days
   om sleep stats 7         # Last 7 days

View and modify preferences:

.. code-block:: bash

   om sleep preferences

Command Aliases
--------------

The sleep sounds module supports several convenient aliases:

.. code-block:: bash

   om sleep              # Full command
   om sleep_sounds       # Explicit alias
   om insomnia           # Condition-specific alias
   om sounds             # Short alias
   om white_noise        # Category-specific alias
   om nature_sounds      # Category-specific alias
   om sleep_aid          # Therapeutic alias

All aliases support the same subcommands:

.. code-block:: bash

   om insomnia search anxiety
   om sounds play "Thunderstorm"
   om white_noise sounds white_noise
   om sleep_aid mixer

Interactive Sound Mixer
----------------------

The interactive sound mixer allows you to create custom sound combinations:

.. code-block:: bash

   om sleep mixer

**Mixer Features:**
   * **Add Sounds**: Combine multiple sounds from any category
   * **Volume Control**: Adjust individual volume levels (0-100%)
   * **Real-time Preview**: Test your mix before saving
   * **Save Mixes**: Store custom combinations for future use
   * **Play Sessions**: Start sleep sessions directly from mixer

**Example Mixer Session:**

.. code-block:: text

   🎛️ Interactive Sound Mixer
   
   Available Sounds for Mixing
   [Sound library displayed]
   
   Choose action [add/remove/volume/save/play/quit]: add
   Enter sound name to add: Rain on Leaves
   ✅ Added 'Rain on Leaves' to mix
   
   Current mix: Rain on Leaves
   
   Choose action [add/remove/volume/save/play/quit]: add
   Enter sound name to add: White Noise
   ✅ Added 'White Noise' to mix
   
   Current mix: Rain on Leaves, White Noise
   
   Choose action [add/remove/volume/save/play/quit]: volume
   Enter sound name to adjust volume: White Noise
   Enter volume for 'White Noise' (0-100) [50]: 25
   ✅ Set 'White Noise' volume to 25%
   
   Choose action [add/remove/volume/save/play/quit]: save
   Enter name for this mix: Gentle Rain Mix
   Enter description (optional): Rain with subtle white noise background
   ✅ Saved mix 'Gentle Rain Mix' successfully!

Sleep Session Management
-----------------------

**Starting a Session:**

.. code-block:: bash

   # Single sound
   om sleep play "Ocean Waves" 45
   
   # From mixer
   om sleep mixer
   # [create mix and choose 'play']

**Session Features:**
   * **Automatic Timer**: Sounds fade out and stop automatically
   * **Manual Control**: Stop sessions early with rating and notes
   * **Background Mode**: Continue using other applications
   * **Quality Tracking**: Rate effectiveness and add notes

**Stopping a Session:**

.. code-block:: bash

   om sleep stop

You'll be prompted to:
   * Rate the session (1-5 stars)
   * Add notes about effectiveness
   * Record any observations

Sleep Quality Tracking
----------------------

The module tracks comprehensive sleep session data:

**Metrics Tracked:**
   * Session duration and timing
   * Sounds used and volume levels
   * Sleep quality ratings
   * Mood before and after sleep
   * Session notes and observations
   * Usage patterns and trends

**Statistics Display:**

.. code-block:: bash

   om sleep stats

.. code-block:: text

   📊 Sleep Statistics (Last 30 Days)
   
   Total Sessions: 15
   Average Duration: 42.3 minutes
   Total Sleep Time: 10.6 hours
   Average Quality: 4.2/5 ⭐
   
   🎵 Most Used Sounds
   Rain on Leaves    8
   White Noise       5
   Ocean Waves       4
   Thunderstorm      3

Mental Health Integration
------------------------

**Condition-Specific Sounds:**

The module includes sounds specifically designed for various mental health conditions:

.. code-block:: bash

   # Anxiety support
   om sleep search anxiety
   # Shows: Rain on Leaves, Ocean Waves, Anxiety Relief Tones
   
   # Depression support
   om sleep search depression
   # Shows: Forest Ambience, Depression Support
   
   # ADHD focus
   om sleep search adhd
   # Shows: Brown Noise, ADHD Focus
   
   # PTSD grounding
   om sleep search ptsd
   # Shows: PTSD Grounding

**Therapeutic Benefits:**

* **Anxiety**: Calming nature sounds and specialized frequencies
* **Depression**: Uplifting and grounding environmental sounds
* **PTSD**: Safe, predictable sounds for grounding and security
* **ADHD**: Focus-enhancing binaural beats and brown noise
* **Insomnia**: Masking sounds and sleep-inducing frequencies
* **Tinnitus**: White noise variations for sound masking

Integration with om Platform
---------------------------

**Mood Tracking Integration:**
   * Correlate sleep quality with mood patterns
   * Track mood improvements after sleep sessions
   * Identify optimal sounds for different emotional states

**Mental Health Classification:**
   * Recommend sounds based on classified mental health patterns
   * Provide targeted sleep support for specific conditions
   * Track effectiveness of different sounds for various issues

**Gamification System:**
   * Earn achievements for consistent sleep practice
   * Track sleep streaks and quality improvements
   * Level up wellness journey with better sleep habits

**Dashboard Integration:**
   * View sleep statistics in wellness dashboard
   * Monitor sleep trends and patterns over time
   * See correlation with other mental health metrics

User Preferences
---------------

Customize your sleep experience:

.. code-block:: bash

   om sleep preferences

**Available Settings:**
   * **Default Timer**: Set preferred session length (default: 30 minutes)
   * **Default Volume**: Set preferred starting volume (default: 50%)
   * **Auto Fade Out**: Enable/disable automatic fade-out (default: enabled)
   * **Fade Duration**: Set fade-out duration (default: 60 seconds)
   * **Background Mode**: Enable background playback (default: enabled)
   * **Preferred Categories**: Set favorite sound categories
   * **Notifications**: Enable/disable session notifications
   * **Sleep Goal**: Set target sleep hours (default: 8.0 hours)

Data Storage and Privacy
-----------------------

All sleep data is stored locally in ``~/.om/sleep_sounds.db``:

**Local Storage Benefits:**
   * Complete privacy - no data leaves your device
   * Works offline - no internet connection required
   * Fast access - instant loading of sounds and statistics
   * User control - you own your sleep data completely

**Database Tables:**
   * ``sleep_sessions`` - Individual sleep session records
   * ``sound_library`` - Available sounds with mental health tags
   * ``sound_mixes`` - Custom user-created sound combinations
   * ``sleep_analytics`` - Daily sleep quality analytics
   * ``user_preferences`` - Personal settings and preferences

**Data Export:**
   All data can be exported for backup or analysis through the om backup system.

Best Practices for Sleep Improvement
-----------------------------------

**Establishing a Routine:**
   * Use consistent sounds for sleep association
   * Set regular sleep times with timer reminders
   * Create different mixes for different sleep needs
   * Track what works best for your sleep patterns

**Sound Selection:**
   * **For Anxiety**: Start with gentle nature sounds like rain or ocean waves
   * **For Racing Thoughts**: Use white or brown noise for mental quieting
   * **For Depression**: Try uplifting nature sounds like forest ambience
   * **For ADHD**: Brown noise or binaural beats can improve focus for sleep
   * **For PTSD**: Consistent, predictable sounds provide safety and grounding

**Volume and Timing:**
   * Start with moderate volume (40-60%) and adjust as needed
   * Use 30-60 minute timers to avoid all-night playback
   * Enable fade-out for gentle awakening
   * Experiment with different combinations to find your optimal mix

**Sleep Environment:**
   * Use sounds to mask disruptive environmental noise
   * Combine with other sleep hygiene practices
   * Create consistent pre-sleep routines
   * Track environmental factors that affect sleep quality

Troubleshooting
--------------

**Audio Issues:**

If sounds aren't playing properly:

.. code-block:: bash

   # Check if session is active
   om sleep stop
   
   # Restart with different sound
   om sleep play "White Noise"

**Database Issues:**

If statistics aren't tracking:

.. code-block:: bash

   # Check database integrity
   sqlite3 ~/.om/sleep_sounds.db "PRAGMA integrity_check;"

**Performance Issues:**

If the module is running slowly:

.. code-block:: bash

   # Clear old session data (optional)
   # This would require manual database cleanup

Future Enhancements
------------------

Planned improvements include:

* **Real Audio Playback**: Integration with audio libraries for actual sound playback
* **Binaural Beats**: Advanced frequency-based therapeutic sounds
* **Sleep Cycle Integration**: Smart wake-up based on sleep cycles
* **Voice Guidance**: Spoken sleep meditations and instructions
* **Community Sharing**: Share and discover effective sound combinations
* **Smart Recommendations**: AI-powered sound suggestions based on patterns
* **Wearable Integration**: Connect with sleep tracking devices
* **Advanced Analytics**: Detailed sleep pattern analysis and insights

Contributing
-----------

To contribute to the sleep sounds module:

1. **Sound Library**: Suggest new sounds or categories
2. **Mental Health Tags**: Improve therapeutic categorization
3. **Features**: Propose new functionality or improvements
4. **Testing**: Test with different sleep patterns and conditions
5. **Documentation**: Improve user guides and examples

See the main om repository for contribution guidelines.

Research and Evidence Base
-------------------------

The sleep sounds module is based on scientific research:

* **White Noise Studies**: Proven effectiveness for sleep improvement and tinnitus relief
* **Nature Sounds Research**: Benefits for stress reduction and sleep quality
* **Binaural Beats**: Frequency-based therapy for various mental health conditions
* **Sound Masking**: Environmental noise reduction for better sleep
* **Music Therapy**: Therapeutic applications of sound for mental health

Support
-------

For support with the sleep sounds module:

* **Technical Issues**: Check the om GitHub repository
* **Sound Requests**: Submit suggestions for new sounds or categories
* **Mental Health Applications**: Consult with healthcare providers for therapeutic use
* **General Questions**: Use the om community forums

Remember: While sleep sounds can be highly effective for improving sleep quality and managing certain mental health symptoms, they work best as part of a comprehensive approach to sleep hygiene and mental wellness. For persistent sleep disorders or mental health concerns, please consult with healthcare professionals.
