🔒 Privacy & Data Protection
============================

Om is built with privacy as a fundamental principle. Your mental health data is deeply personal, and we've designed every aspect of om to protect your privacy completely.

100% Local Storage
------------------

**All your data stays on your device. Period.**

- **No cloud sync** - Your data never leaves your computer
- **No external transmission** - Zero network requests for personal data
- **No analytics tracking** - We don't collect usage statistics
- **No telemetry** - No data about how you use om is sent anywhere

Your mental health information is stored locally in ``~/.om/`` and remains under your complete control.

Data Storage Location
---------------------

All om data is stored in your home directory:

.. code-block:: text

   ~/.om/
   ├── om.db                    # Main SQLite database
   ├── mood_data.json           # Mood tracking history
   ├── wellness_stats.json      # Gamification progress
   ├── achievements.json        # Achievement tracking
   ├── coach_insights.json      # AI coaching insights
   ├── autopilot_tasks.json     # Automated wellness tasks
   ├── wellness_sessions.json   # Session history
   └── user_patterns.json       # Learned behavior patterns

What Data We Store
------------------

Om stores only the data you explicitly provide:

**Mood & Wellness Data**
  - Mood ratings and notes you enter
  - Stress and energy levels you track
  - Breathing exercise sessions
  - Meditation and gratitude practices

**Progress & Achievements**
  - Wellness streaks and consistency
  - Achievement unlocks and progress
  - Gamification points and levels
  - Session completion statistics

**AI Coaching Data**
  - Pattern analysis results (computed locally)
  - Personalized recommendations
  - Coaching effectiveness ratings
  - Crisis detection alerts (local only)

**What We DON'T Store**
  - Personal identifying information
  - Location data
  - Device information
  - Network activity
  - External app usage

Data Control & Management
-------------------------

You have complete control over your data:

**View Your Data**

.. code-block:: bash

   om data show            # View all stored data
   om privacy status       # Check privacy settings
   om data location        # Show data storage location

**Export Your Data**

.. code-block:: bash

   om export --all         # Export all data to JSON
   om backup create        # Create complete backup
   om export --mood        # Export only mood data
   om export --achievements # Export achievement data

**Delete Your Data**

.. code-block:: bash

   om data clear --all     # Delete all data (with confirmation)
   om data clear --mood    # Delete only mood data
   om reset --complete     # Complete reset to fresh install

**Backup & Restore**

.. code-block:: bash

   om backup create        # Create timestamped backup
   om backup restore       # Restore from backup
   om backup list          # List available backups

Security Measures
-----------------

**Local Encryption (Optional)**

.. code-block:: bash

   om security enable      # Enable local data encryption
   om security status      # Check encryption status
   om security change-key  # Change encryption key

**File Permissions**
- Data files are created with restricted permissions (600)
- Only your user account can access om data
- Database files are protected from other users

**No Network Dependencies**
- Om works completely offline
- No internet connection required for core functionality
- Optional API integrations are clearly marked and user-controlled

API Integrations & Privacy
---------------------------

When you choose to enable optional API integrations:

**Crisis Support APIs**
  - Only activated during crisis situations
  - No personal data transmitted
  - Anonymous connection to crisis resources
  - User explicitly chooses when to connect

**Professional Content APIs**
  - Used only for downloading therapeutic content
  - No personal data shared with content providers
  - All content cached locally after download
  - Can be completely disabled

**User Control**

.. code-block:: bash

   om apis list            # Show available API integrations
   om apis disable --all   # Disable all external connections
   om apis status          # Check what's enabled
   om privacy --strict     # Enable maximum privacy mode

Open Source Transparency
-------------------------

**Auditable Code**
- Complete source code available on GitHub
- No hidden functionality or backdoors
- Community can verify privacy claims
- Regular security reviews by contributors

**No Proprietary Components**
- All dependencies are open source
- No closed-source libraries for data handling
- Transparent data processing algorithms
- Community-driven development

Data Retention
--------------

**Your Choice**
- Data is kept as long as you want it
- No automatic deletion or expiration
- You control all retention policies
- Easy to export before deletion

**Automatic Cleanup (Optional)**

.. code-block:: bash

   om cleanup --old-sessions 90d    # Remove sessions older than 90 days
   om cleanup --temp-files          # Clean temporary files
   om cleanup --logs 30d            # Remove old log files

Legal & Compliance
------------------

**No Data Collection**
- We don't collect personal data, so GDPR/CCPA don't apply
- No privacy policy needed for external data handling
- No terms of service for data usage
- Your data, your rules

**Mental Health Considerations**
- Designed with therapeutic confidentiality in mind
- No mandatory reporting or data sharing
- Crisis support respects your privacy choices
- Professional integration is user-controlled

Privacy Best Practices
----------------------

**For Maximum Privacy**

.. code-block:: bash

   # Enable strict privacy mode
   om privacy --strict-mode
   
   # Disable all external connections
   om apis disable --all
   
   # Enable local encryption
   om security enable
   
   # Regular backups to secure location
   om backup create --encrypted

**Regular Privacy Checkups**

.. code-block:: bash

   om privacy audit        # Check all privacy settings
   om data summary         # Review what data is stored
   om security status      # Verify security measures

Frequently Asked Questions
--------------------------

**Q: Does om send any data to external servers?**
A: No. Om operates completely locally unless you explicitly enable optional API integrations for crisis support or professional content.

**Q: Can my therapist or doctor access my om data?**
A: Only if you choose to export and share it. There's no automatic sharing or professional access.

**Q: What happens if I uninstall om?**
A: Your data remains in ``~/.om/`` until you manually delete it. Uninstalling the app doesn't remove your data.

**Q: Can family members or employers see my om data?**
A: No, unless they have administrative access to your computer account. Data files are protected with user-only permissions.

**Q: Is om HIPAA compliant?**
A: Om doesn't need HIPAA compliance because it doesn't transmit or store data on external servers. Your local data storage is under your control.

**Q: What about government surveillance?**
A: Since all data is local and encrypted (optionally), om provides strong protection against external surveillance. No data is transmitted that could be intercepted.

Contact & Questions
-------------------

For privacy-related questions:

- **GitHub Issues**: https://github.com/frism/om/issues
- **Email**: schraube.eins@icloud.com
- **Documentation**: This page and source code

**Remember**: Your privacy is not negotiable. Om is designed to keep your mental health journey completely private and under your control.

.. note::
   
   This privacy approach means om can't offer cloud sync or multi-device features. We believe your privacy is more important than convenience features that compromise your data security.
