Project Structure
=================

The Om mental health platform is organized with a clean, professional structure focused on the core application and comprehensive documentation.

📁 Current Project Structure
----------------------------

.. code-block:: text

   om/
   ├── 📖 Documentation
   │   ├── README.md                    # Main project README
   │   ├── LICENSE                      # MIT License
   │   └── docs/                        # Sphinx documentation system
   │       ├── source/                  # Documentation source files
   │       │   ├── index.rst           # Main documentation hub
   │       │   ├── installation.rst    # Installation guide
   │       │   ├── quickstart.rst      # Quick start guide
   │       │   ├── cli_reference.rst   # Complete CLI reference
   │       │   ├── features.rst        # Features overview
   │       │   ├── modules.rst         # Module reference
   │       │   ├── visual_features.rst # Visual interface guide
   │       │   ├── database_system.rst # Database documentation
   │       │   ├── api_implementation.rst # API documentation
   │       │   ├── testing.rst         # Testing strategy
   │       │   ├── project_structure.rst # This file
   │       │   ├── contributing.rst    # Contributing guide
   │       │   ├── conf.py             # Sphinx configuration
   │       │   └── _static/            # Custom CSS and assets
   │       ├── build/html/             # Generated HTML documentation
   │       ├── requirements.txt        # Documentation dependencies
   │       └── Makefile               # Documentation build automation
   │
   ├── 🧠 Core Application
   │   ├── main.py                     # Main application entry point
   │   ├── om                          # CLI executable
   │   ├── om_database.py              # Database manager (SQLite)
   │   ├── om_database_schema.sql      # Database schema
   │   ├── requirements.txt           # Application dependencies
   │   ├── setup.py                   # Package setup
   │   └── install.sh                 # Installation script
   │
   ├── 🧪 Testing & Quality
   │   ├── test_production.py         # Production readiness tests
   │   ├── test_om_db.py             # Database tests
   │   └── migrate_to_sqlite.py      # Database migration tools
   │
   ├── 🎮 Features & Modules
   │   ├── modules/                   # Feature modules (39 modules)
   │   │   ├── mood_tracking.py      # Enhanced mood tracking
   │   │   ├── anxiety_support.py    # Anxiety management
   │   │   ├── depression_support.py # Depression support
   │   │   ├── breathing.py          # Breathing exercises
   │   │   ├── meditation.py         # Meditation sessions
   │   │   ├── gratitude.py          # Gratitude practice
   │   │   ├── physical.py           # Physical wellness
   │   │   ├── habits.py             # Habit tracking
   │   │   ├── mental_health_coach.py # AI coaching
   │   │   ├── wellness_autopilot.py # Automated wellness
   │   │   ├── wellness_gamification.py # Achievement system
   │   │   ├── wellness_dashboard.py # Visual dashboard
   │   │   ├── rescue_sessions.py    # Crisis support
   │   │   ├── coping_strategies.py  # Coping techniques
   │   │   ├── guided_journals.py    # Journaling exercises
   │   │   ├── social_connection.py  # Social wellness
   │   │   ├── learning_paths.py     # Educational content
   │   │   ├── enhanced_meditation.py # Advanced meditation
   │   │   ├── hypnosis_sessions.py  # Guided hypnosis
   │   │   ├── neurowave_stimulation.py # Brainwave entrainment
   │   │   ├── insomnia_support.py   # Sleep support
   │   │   ├── addiction_recovery.py # Addiction support
   │   │   ├── body_image_support.py # Body image support
   │   │   ├── emotion_analysis.py   # Emotion analysis
   │   │   ├── coping_skills.py      # Additional coping skills
   │   │   ├── quick_capture.py      # Quick note taking
   │   │   ├── external_integrations.py # External tool integration
   │   │   ├── chatbot.py            # Interactive chatbot
   │   │   ├── api_server.py         # API server module
   │   │   ├── backup_export.py      # Data backup tools
   │   │   ├── daily_checkin.py      # Daily wellness check-ins
   │   │   ├── enhanced_mood_tracking.py # Advanced mood features
   │   │   ├── wellness_dashboard_enhanced.py # Enhanced dashboard
   │   │   ├── achievements_gallery.py # Visual achievements
   │   │   ├── visual_achievements.py # Achievement display
   │   │   └── textual_example.py    # TUI examples
   │   ├── quick_actions.py          # Ultra-fast wellness actions
   │   ├── smart_suggestions.py      # AI-powered suggestions
   │   ├── ascii_art.py              # Visual elements
   │   └── demo_achievements.py      # Achievement demonstrations
   │
   ├── 🌐 API & Integration
   │   └── api/                      # REST API components
   │       ├── server.py             # Flask API server
   │       ├── client.py             # Python client library
   │       ├── client.js             # JavaScript client library
   │       └── web_dashboard.html    # Example web interface
   │
   ├── 📦 Archive & History
   │   └── archive/                  # Archived development files
   │       └── markdown_docs/        # Historical documentation
   │
   └── 🔧 Utilities
       ├── serve_docs.sh             # Documentation server
       ├── deploy_docs.sh            # GitHub Pages deployment
       └── setup_shortcuts.sh        # Shell shortcuts setup

🎯 Core Components
------------------

Main Application
~~~~~~~~~~~~~~~

**main.py**
   The central application entry point that:
   
   - Imports and integrates all 39 modules
   - Handles command routing and aliases
   - Provides help system and module discovery
   - Manages visual/TUI mode detection
   - Implements error handling and graceful fallbacks

**om (CLI executable)**
   Smart wrapper script that:
   
   - Provides command aliases and shortcuts
   - Handles quick actions (qm, qb, qg, etc.)
   - Manages smart routines (morning, evening)
   - Implements natural language command processing
   - Routes commands to main.py with proper arguments

Database System
~~~~~~~~~~~~~~

**om_database.py**
   Comprehensive SQLite database manager:
   
   - Thread-safe connection management
   - ACID-compliant transactions
   - Performance-optimized queries
   - Automatic schema migrations
   - Backup and recovery capabilities

**om_database_schema.sql**
   Complete database schema with:
   
   - Mental health focused data models
   - Optimized indexes for performance
   - Referential integrity constraints
   - Analytics and reporting views
   - Privacy-conscious design

Module System
~~~~~~~~~~~~~

**39 Integrated Modules**
   Each module provides specific functionality:
   
   - **Core Mental Health** (8 modules): mood, anxiety, depression, addiction, body image, insomnia, coping
   - **Wellness Practices** (6 modules): breathing, meditation, gratitude, physical, habits
   - **Advanced Techniques** (4 modules): hypnosis, neurowave, rescue, journaling
   - **Social & Analysis** (4 modules): social connection, emotion analysis, learning paths
   - **AI-Powered Features** (4 modules): coaching, autopilot, gamification, dashboard
   - **Support & Integration** (13 modules): API, backup, quick actions, external integrations

🔧 Development Structure
-----------------------

Testing Framework
~~~~~~~~~~~~~~~~

**Comprehensive Test Coverage**
   - **Unit Tests**: Individual module functionality
   - **Integration Tests**: End-to-end workflows
   - **Performance Tests**: Response time and memory usage
   - **Security Tests**: Input validation and data protection
   - **Accessibility Tests**: Screen reader and keyboard navigation
   - **Crisis Support Tests**: Emergency feature reliability

**Test Files**
   - ``test_production.py`` - Production readiness validation
   - ``test_om_db.py`` - Database functionality testing
   - ``migrate_to_sqlite.py`` - Database migration testing

Documentation System
~~~~~~~~~~~~~~~~~~~~

**Sphinx Documentation**
   Professional documentation system with:
   
   - **Auto-generated API docs** from code docstrings
   - **Comprehensive user guides** for all features
   - **Developer documentation** for contributors
   - **Search functionality** across all content
   - **Mobile-responsive design** for accessibility
   - **Cross-platform compatibility** documentation

**Documentation Commands**
   .. code-block:: bash
   
      om docs                 # View documentation info
      om docs serve           # Start local documentation server
      om docs-build           # Build documentation
      ./serve_docs.sh         # Alternative documentation server
      ./deploy_docs.sh        # Deploy to GitHub Pages

🎨 Visual & TUI Features
-----------------------

Textual Integration
~~~~~~~~~~~~~~~~~~

**Visual Command Support**
   Beautiful terminal interfaces for enhanced user experience:
   
   .. code-block:: bash
   
      om gamify status -v     # Visual achievements gallery
      om dashboard -v         # Rich visual dashboard
      om achievements -v      # Visual achievement display
      om textual             # TUI examples and demos

**Implementation Details**
   - **Automatic Detection**: Detects Textual availability
   - **Graceful Fallback**: Falls back to text mode if needed
   - **Visual Command Routing**: Routes visual commands to TUI interfaces
   - **Help Integration**: Visual commands documented in help system

Achievement System
~~~~~~~~~~~~~~~~~

**Visual Achievement Gallery**
   - Beautiful achievement cards with progress bars
   - Wellness journey overview with level and points
   - Recent unlocks celebration with animations
   - Category filtering by achievement type
   - Sparkle animations for unlocked achievements
   - Rarity system with color coding

🌐 API & Integration
-------------------

REST API Server
~~~~~~~~~~~~~~

**Flask-based API**
   Comprehensive REST API for external integrations:
   
   - **Secure Authentication**: API key-based access control
   - **Rate Limiting**: Configurable request limits
   - **Local Data Only**: No external data transmission
   - **CORS Support**: Configurable for web applications
   - **Client Libraries**: Python and JavaScript clients

**API Endpoints**
   - Mood tracking and analytics
   - Daily check-ins and wellness sessions
   - Dashboard data and summaries
   - Quick actions and coaching insights
   - Backup and data export

Web Integration
~~~~~~~~~~~~~~

**Web Dashboard Example**
   Complete web interface demonstrating:
   
   - Real-time wellness metrics
   - Interactive charts and visualizations
   - Quick action buttons
   - Responsive design for mobile devices

📦 Archive & History
-------------------

Development Archive
~~~~~~~~~~~~~~~~~~

**archive/markdown_docs/**
   Historical documentation preserved for reference:
   
   - 36 archived markdown files
   - Implementation summaries and guides
   - Feature development documentation
   - Testing strategies and results
   - Production readiness checklists

**Purpose**
   - Preserve development history
   - Reference for future enhancements
   - Documentation evolution tracking
   - Knowledge preservation

🔒 Privacy & Security
--------------------

Data Protection
~~~~~~~~~~~~~~

**100% Local Storage**
   - All data stored in ``~/.om/`` directory
   - No cloud synchronization or external transmission
   - User-controlled data retention and deletion
   - Optional encryption for sensitive data

**Security Measures**
   - Input sanitization and validation
   - SQL injection prevention
   - Secure file permissions
   - Privacy-conscious logging
   - Crisis data anonymization

🚀 Deployment & Distribution
---------------------------

Installation Methods
~~~~~~~~~~~~~~~~~~~

**Automated Installation**
   .. code-block:: bash
   
      git clone https://github.com/yourusername/om.git
      cd om
      ./install.sh

**Manual Installation**
   .. code-block:: bash
   
      pip install -r requirements.txt
      chmod +x om
      ./om help

**Development Setup**
   .. code-block:: bash
   
      pip install -r requirements.txt
      pip install -r docs/requirements.txt
      ./test.sh

Distribution Options
~~~~~~~~~~~~~~~~~~~

**Package Distribution**
   - PyPI package with ``setup.py``
   - Docker container support
   - Homebrew formula (planned)
   - Snap package (planned)

**Documentation Deployment**
   - GitHub Pages integration
   - Local documentation server
   - Offline documentation support

This clean, organized structure ensures the Om mental health platform is maintainable, extensible, and user-friendly while preserving all the valuable development history and comprehensive documentation.
