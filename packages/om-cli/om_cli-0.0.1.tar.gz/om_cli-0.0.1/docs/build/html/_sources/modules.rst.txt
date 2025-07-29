Modules Reference
=================

The om platform is built with a modular architecture. Each module provides specific mental health functionality.

Core Modules
------------

These modules provide the fundamental mental health features:

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Module
     - Command
     - Description
   * - mood_tracking
     - ``om mood``
     - Track and analyze mood patterns over time
   * - breathing
     - ``om breathe``
     - Guided breathing exercises for relaxation
   * - meditation
     - ``om meditate``
     - Mindfulness and meditation sessions
   * - gratitude
     - ``om gratitude``
     - Daily gratitude practice for positivity
   * - physical
     - ``om stretch``
     - Physical wellness and movement exercises
   * - habits
     - ``om habits``
     - Build and maintain healthy habits

Advanced AI Modules
-------------------

These modules provide AI-powered wellness features:

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Module
     - Command
     - Description
   * - mental_health_coach
     - ``om coach``
     - AI-powered personalized mental health coaching
   * - wellness_autopilot
     - ``om autopilot``
     - Automated wellness task management
   * - wellness_gamification
     - ``om gamify``
     - Achievement tracking and progress motivation
   * - wellness_dashboard
     - ``om dashboard``
     - Visual wellness metrics and progress tracking

Mental Health Support Modules
-----------------------------

These modules provide specialized mental health support:

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Module
     - Command
     - Description
   * - anxiety_support
     - ``om anxiety``
     - Comprehensive anxiety management tools
   * - depression_support
     - ``om depression``
     - Depression support resources and strategies
   * - rescue_sessions
     - ``om rescue``
     - Crisis support and emergency resources
   * - insomnia_support
     - ``om sleep``
     - Sleep improvement and insomnia management
   * - coping_strategies
     - ``om cope``
     - Coping strategies and techniques
   * - guided_journals
     - ``om journal``
     - Structured journaling and reflection

Extended Modules
----------------

Additional specialized modules for comprehensive wellness:

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Module
     - Command
     - Description
   * - enhanced_meditation
     - ``om zen``
     - Advanced meditation techniques
   * - hypnosis_sessions
     - ``om hypnosis``
     - Guided hypnosis for relaxation
   * - neurowave_stimulation
     - ``om neurowave``
     - Brainwave entrainment techniques
   * - social_connection
     - ``om social``
     - Social wellness and relationship tools
   * - learning_paths
     - ``om learn``
     - Mental health education and skill building
   * - addiction_recovery
     - ``om recovery``
     - Addiction recovery support tools
   * - body_image_support
     - ``om body``
     - Body image and self-acceptance support
   * - emotion_analysis
     - ``om emotions``
     - Advanced emotional analysis tools

Module Status
-------------

Check which modules are available on your system:

.. code-block:: bash

   om status           # Show all module status
   om list-modules     # List available modules

Module Development
------------------

Creating Custom Modules
~~~~~~~~~~~~~~~~~~~~~~~~

Each module should implement a ``run(args)`` function:

.. code-block:: python

   def run(args=None):
       """Main entry point for the module"""
       if not args:
           # Default behavior
           show_help()
           return
       
       action = args[0].lower() if args else 'default'
       
       if action == 'start':
           start_session()
       elif action == 'stats':
           show_statistics()
       else:
           print(f"Unknown action: {action}")

Module Integration
~~~~~~~~~~~~~~~~~~

Modules are automatically discovered and integrated if they:

1. Are located in the ``modules/`` directory
2. Have a ``run()`` or ``main()`` function
3. Follow the naming convention

Adding Module Aliases
~~~~~~~~~~~~~~~~~~~~~

Add command aliases in the main ``om`` script:

.. code-block:: python

   ALIASES = {
       'mymodule': 'my_custom_module',
       'mm': 'my_custom_module',
   }
