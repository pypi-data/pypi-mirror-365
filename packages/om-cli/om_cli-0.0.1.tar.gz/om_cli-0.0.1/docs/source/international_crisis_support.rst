🌍 International Crisis Support
===============================

Om provides comprehensive crisis intervention resources for users worldwide, integrating country-specific emergency services and crisis hotlines with the compassionate "Fear as Friend" philosophy from Nicky Case.

Global Crisis Coverage
----------------------

**Supported Countries & Regions:**

.. list-table::
   :header-rows: 1
   :widths: 15 25 35 25

   * - Country
     - Emergency
     - Primary Crisis Line
     - Languages
   * - 🇺🇸 United States
     - 911
     - 988 Suicide & Crisis Lifeline
     - English, Spanish
   * - 🇨🇦 Canada
     - 911
     - Talk Suicide Canada (1-833-456-4566)
     - English, French
   * - 🇬🇧 United Kingdom
     - 999
     - Samaritans (116 123)
     - English
   * - 🇩🇪 Germany
     - 112
     - Telefonseelsorge (0800 111 0 111)
     - German
   * - 🇫🇷 France
     - 112
     - SOS Amitié (09 72 39 40 50)
     - French
   * - 🇳🇱 Netherlands
     - 112
     - 113 Zelfmoordpreventie (113)
     - Dutch
   * - 🇦🇺 Australia
     - 000
     - Lifeline Australia (13 11 14)
     - English
   * - 🇳🇿 New Zealand
     - 111
     - Lifeline Aotearoa (0800 543 354)
     - English, Māori
   * - 🇯🇵 Japan
     - 110/119
     - TELL Lifeline (03-5774-0992)
     - English, Japanese

Quick Access Commands
---------------------

**Immediate Crisis Support:**

.. code-block:: bash

   # Show crisis resources for your country
   om crisis
   om rescue crisis
   om emergency

   # International crisis support menu
   om rescue international

   # Emergency intervention with grounding techniques
   om rescue emergency

**Country-Specific Support:**

.. code-block:: bash

   # Show resources for specific country
   om rescue country US        # United States
   om rescue country GB        # United Kingdom  
   om rescue country DE        # Germany
   om rescue country AU        # Australia

   # List all available countries
   om rescue countries

**Setup & Configuration:**

.. code-block:: bash

   # Interactive country setup
   om rescue setup

   # Add custom local crisis resource
   om rescue add-custom

   # View your custom resources
   om rescue custom

Automatic Country Detection
---------------------------

Om automatically detects your country using:

1. **System Locale**: Primary detection method
2. **Timezone Information**: Secondary detection
3. **Manual Setup**: User override option

**Setup Your Country:**

.. code-block:: bash

   # Interactive setup with country detection
   om rescue setup

   # Manual country selection
   om rescue setup
   # Then select from the list or enter country code

The system will remember your preference and show appropriate crisis resources.

Nicky Case Integration
----------------------

The crisis support system integrates Nicky Case's "Fear as Friend" philosophy:

**Core Principles:**
- 🐺 **Your fear is trying to protect you** - Anxiety and distress are signals, not enemies
- 💝 **Reaching out is strength** - Asking for help shows courage and self-awareness
- 🤝 **You're not alone** - Crisis support exists because people care about you
- 🌅 **This feeling is temporary** - Difficult emotions and situations do change
- 💪 **You have survived before** - You have resilience and coping abilities

**Integrated Messaging:**

.. code-block:: bash

   om rescue emergency
   # Shows crisis resources with compassionate messaging:
   # "🐺 Your inner wolf is trying to protect you from pain"
   # "💝 You reached out, and that takes courage"
   # "🤝 You don't have to face this alone"

Crisis Detection & Intervention
-------------------------------

**Automatic Crisis Detection:**

Om monitors for crisis indicators in user input and automatically provides appropriate support:

.. code-block:: python

   # Crisis keywords trigger immediate support
   crisis_keywords = [
       'suicide', 'kill myself', 'end it all', 'want to die',
       'hurt myself', 'self harm', 'worthless', 'hopeless',
       'better off dead', 'can\'t go on', 'give up'
   ]

**Immediate Intervention:**

When crisis indicators are detected:

1. **Immediate Crisis Resources** - Country-specific emergency contacts
2. **Emergency Grounding** - 30-second calming technique
3. **Safety Planning** - Practical immediate steps
4. **Compassionate Messaging** - Nicky Case-inspired support

Custom Local Resources
----------------------

**Add Your Local Resources:**

.. code-block:: bash

   # Interactive custom resource addition
   om rescue add-custom
   
   # Example:
   # Resource name: Local Crisis Center
   # Phone number: (555) 123-4567
   # Description: 24/7 local crisis support

**View Custom Resources:**

.. code-block:: bash

   # Show all your custom resources
   om rescue custom

Custom resources are stored locally and integrated with official crisis resources.

Emergency Grounding Techniques
------------------------------

**Built-in Emergency Techniques:**

.. code-block:: bash

   # 30-second emergency grounding
   om rescue emergency

**Grounding Steps:**
1. Deep breathing with guided timing
2. Physical grounding (feel feet on ground)
3. 5-4-3-2-1 sensory technique
4. Name recognition and present moment awareness
5. Safety affirmation

**Integration with Rescue Sessions:**

.. code-block:: bash

   # Access full rescue techniques
   om rescue menu
   
   # Quick rescue technique
   om rescue quick
   
   # Specific techniques for different feelings
   om rescue feeling overwhelmed
   om rescue feeling panic
   om rescue feeling hopeless

Privacy & Data Protection
-------------------------

**Local Storage Only:**
- All crisis preferences stored locally in ``~/.om/``
- No external transmission of personal crisis data
- User controls all crisis resource information

**Data Files:**

.. code-block:: text

   ~/.om/
   ├── crisis_resources.json      # Official crisis resources cache
   ├── user_location.json         # Your country preference
   └── custom_crisis_resources.json # Your custom local resources

**Privacy Features:**
- Country detection is optional and user-controlled
- Custom resources remain completely private
- No tracking of crisis resource usage
- All data can be deleted or exported

International Expansion
-----------------------

**Adding New Countries:**

The crisis support system is designed for easy expansion:

.. code-block:: python

   # New countries can be added to crisis_resources dictionary
   "NEW_COUNTRY": {
       "country": "Country Name",
       "emergency": "Emergency Number",
       "crisis_lines": [
           {
               "name": "Crisis Line Name",
               "number": "Phone Number",
               "website": "Website URL",
               "available": "24/7",
               "languages": ["Language1", "Language2"]
           }
       ]
   }

**Community Contributions:**

We welcome contributions of crisis resources for additional countries:

- Submit via GitHub issues or pull requests
- Include official crisis line information
- Verify accuracy of contact information
- Provide multiple language options when available

**Fallback Support:**

For unsupported countries, om provides:

- International crisis resource directories
- Global crisis support organizations
- Generic emergency guidance
- Ability to add custom local resources

Usage Examples
--------------

**Daily Usage:**

.. code-block:: bash

   # Quick crisis check during difficult times
   om crisis

   # Access rescue techniques
   om rescue menu

**Crisis Situations:**

.. code-block:: bash

   # Immediate crisis support
   om emergency
   om 911    # US emergency alias
   om 112    # European emergency alias
   om 999    # UK emergency alias

**Setup & Maintenance:**

.. code-block:: bash

   # Initial setup
   om rescue setup

   # Add local resources
   om rescue add-custom

   # Check available countries
   om rescue countries

**Integration with Other Features:**

.. code-block:: bash

   # Crisis support integrated with other om features
   om coach urgent     # AI coach crisis detection
   om qm              # Quick mood check with crisis detection
   om wolf            # Nicky Case guide with crisis awareness

Best Practices
--------------

**For Users:**

1. **Set up your country** during initial om configuration
2. **Add local resources** specific to your area
3. **Test the system** when you're feeling stable
4. **Share with trusted contacts** who might need support
5. **Keep emergency numbers** easily accessible

**For Mental Health Professionals:**

1. **Recommend om setup** to clients for crisis support
2. **Add your practice** as a custom resource if appropriate
3. **Integrate with safety planning** discussions
4. **Use as backup support** between sessions
5. **Respect privacy** - om data stays with the user

**For Organizations:**

1. **Provide setup guidance** to users in your region
2. **Contribute local resources** for your area
3. **Integrate with existing** crisis support systems
4. **Train staff** on om crisis features
5. **Maintain updated** contact information

Technical Implementation
------------------------

**Architecture:**

.. code-block:: text

   International Crisis Support System
   ├── Country Detection (locale, timezone)
   ├── Resource Database (comprehensive crisis lines)
   ├── Custom Resources (user-added local support)
   ├── Crisis Detection (keyword monitoring)
   ├── Emergency Intervention (immediate support)
   └── Nicky Case Integration (compassionate messaging)

**Key Components:**

- ``InternationalCrisisSupport`` class for core functionality
- Integration with existing ``RescueSessions`` module
- Automatic country detection and manual override
- Custom resource management with local storage
- Crisis keyword detection and intervention protocols

**Extensibility:**

The system is designed for easy expansion:

- New countries can be added without code changes
- Custom resources integrate seamlessly
- Crisis detection can be enhanced with additional keywords
- Integration points for external crisis APIs
- Localization support for multiple languages

Remember: You Matter
--------------------

**The om crisis support system exists because:**

- 💝 **Your life has value** - You matter to people, even when it doesn't feel that way
- 🤝 **Help is available** - Crisis support exists because people care about you
- 🌅 **Tomorrow can be different** - Difficult situations and feelings do change
- 💪 **You have strength** - You've survived difficult times before
- 🐺 **Your fear is trying to protect you** - Even distress serves a purpose

**If you're in crisis right now:**

.. code-block:: bash

   om emergency

**Remember:** Reaching out for help is a sign of strength, not weakness. The crisis support resources in om are here because people believe in your worth and want to help you through difficult times.

.. note::
   
   Om's crisis support is designed to complement, not replace, professional mental health care and emergency services. Always call your local emergency number (911, 112, 999, etc.) if you're in immediate physical danger.

.. warning::
   
   If you're experiencing thoughts of suicide or self-harm, please reach out for immediate help. Use ``om emergency`` for quick access to crisis resources, but don't hesitate to call emergency services or go to your nearest emergency room if you're in immediate danger.
