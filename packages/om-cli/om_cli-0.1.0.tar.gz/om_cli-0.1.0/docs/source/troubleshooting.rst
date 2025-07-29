🔧 Troubleshooting
==================

Common issues and solutions for the om mental health platform.

Installation Issues
-------------------

**Python Version Problems**

.. code-block:: bash

   # Check Python version (requires 3.11+)
   python --version
   python3 --version
   
   # If version is too old, install newer Python
   # macOS with Homebrew:
   brew install python@3.11
   
   # Ubuntu/Debian:
   sudo apt update
   sudo apt install python3.11

**Permission Errors**

.. code-block:: bash

   # Make om executable
   chmod +x om
   chmod +x install.sh
   
   # If still having issues, try:
   sudo chmod +x om install.sh

**Missing Dependencies**

.. code-block:: bash

   # Install all requirements
   pip install -r requirements.txt
   
   # If pip is missing:
   python -m ensurepip --upgrade
   
   # For specific missing modules:
   pip install textual rich sqlite3

Database Issues
---------------

**Database Corruption**

.. code-block:: bash

   # Check database integrity
   om db check
   
   # Repair database if corrupted
   om db repair
   
   # If repair fails, restore from backup
   om backup restore
   
   # Last resort - reset database (loses data)
   om reset --database-only

**Database Lock Errors**

.. code-block:: bash

   # Check if om is running in another terminal
   ps aux | grep om
   
   # Kill any hanging processes
   pkill -f "python.*om"
   
   # Remove lock file if exists
   rm ~/.om/.db_lock

**Migration Issues**

.. code-block:: bash

   # Force database migration
   om db migrate --force
   
   # Check migration status
   om db status
   
   # Rollback if needed
   om db rollback

Performance Issues
------------------

**Slow Startup**

.. code-block:: bash

   # Check system status
   om status --verbose
   
   # Clear cache files
   om cache clear
   
   # Optimize database
   om db optimize
   
   # Check for large log files
   ls -la ~/.om/logs/

**Memory Usage**

.. code-block:: bash

   # Check memory usage
   om status --memory
   
   # Reduce memory usage
   om config --low-memory-mode
   
   # Clear old session data
   om cleanup --old-sessions 30d

**Dashboard Performance**

.. code-block:: bash

   # Use text mode instead of visual
   om dashboard --text-only
   
   # Reduce update frequency
   om dashboard live 120  # Update every 2 minutes
   
   # Disable animations
   om config --no-animations

Display Issues
--------------

**Terminal Compatibility**

.. code-block:: bash

   # Check terminal capabilities
   om test terminal
   
   # Force text mode if visual issues
   om config --force-text-mode
   
   # Test colors
   om test colors

**Unicode/Emoji Problems**

.. code-block:: bash

   # Disable emoji and unicode
   om config --no-emoji
   
   # Use ASCII-only mode
   om config --ascii-only
   
   # Check locale settings
   locale

**Screen Size Issues**

.. code-block:: bash

   # Check terminal size
   om test screen-size
   
   # Force compact mode
   om config --compact-mode
   
   # Adjust dashboard layout
   om dashboard --layout compact

Data Issues
-----------

**Missing Data**

.. code-block:: bash

   # Check data location
   om data location
   
   # Verify data files exist
   ls -la ~/.om/
   
   # Restore from backup if available
   om backup list
   om backup restore

**Corrupted Data Files**

.. code-block:: bash

   # Validate data integrity
   om data validate
   
   # Repair JSON files
   om data repair --json-files
   
   # Export what's recoverable
   om export --partial

**Import/Export Problems**

.. code-block:: bash

   # Check file permissions
   ls -la backup_file.json
   
   # Validate backup file
   om backup validate backup_file.json
   
   # Import with error recovery
   om import --ignore-errors backup_file.json

AI Coach Issues
---------------

**Coach Not Responding**

.. code-block:: bash

   # Check AI coach status
   om coach status
   
   # Reset AI coach data
   om coach reset
   
   # Rebuild pattern analysis
   om coach rebuild-patterns

**Inaccurate Insights**

.. code-block:: bash

   # Provide feedback to improve accuracy
   om coach feedback --rating 3 --comment "Not helpful"
   
   # Reset learning data
   om coach reset-learning
   
   # Check data quality
   om data quality-check

**Missing Recommendations**

.. code-block:: bash

   # Force recommendation generation
   om coach generate --force
   
   # Check minimum data requirements
   om coach requirements
   
   # Add more mood data for better insights
   om qm  # Quick mood entries

API Integration Issues
----------------------

**Connection Problems**

.. code-block:: bash

   # Test internet connection
   ping google.com
   
   # Check API status
   om apis test
   
   # Disable problematic APIs
   om apis disable crisis-text-line

**Authentication Errors**

.. code-block:: bash

   # Check API keys
   om apis keys --list
   
   # Reset API authentication
   om apis auth --reset
   
   # Test with new keys
   om apis test --key-validation

**Rate Limiting**

.. code-block:: bash

   # Check rate limit status
   om apis limits
   
   # Wait for reset or use local alternatives
   om config --offline-mode

Gamification Issues
-------------------

**Missing Achievements**

.. code-block:: bash

   # Recalculate achievements
   om gamify recalculate
   
   # Check achievement requirements
   om gamify requirements
   
   # Force unlock if earned
   om gamify unlock --force achievement_name

**Incorrect Stats**

.. code-block:: bash

   # Rebuild statistics
   om gamify rebuild-stats
   
   # Validate data consistency
   om gamify validate
   
   # Reset specific stats
   om gamify reset --stats-only

Crisis Support Issues
---------------------

**Emergency Resources Not Loading**

.. code-block:: bash

   # Use offline crisis resources
   om rescue --offline
   
   # Check internet connection
   om test connection
   
   # Access local crisis information
   om crisis --local-resources

**Crisis Detection Problems**

.. code-block:: bash

   # Check crisis detection settings
   om crisis settings
   
   # Test crisis detection manually
   om crisis test-detection
   
   # Adjust sensitivity
   om crisis sensitivity --level medium

System Integration Issues
-------------------------

**Command Not Found**

.. code-block:: bash

   # Check if om is in PATH
   which om
   
   # Add to PATH if needed
   export PATH="$PATH:/path/to/om"
   
   # Or use full path
   /full/path/to/om qm

**Permission Denied**

.. code-block:: bash

   # Check file permissions
   ls -la om
   
   # Fix permissions
   chmod +x om
   
   # Check directory permissions
   ls -la ~/.om/

**Environment Issues**

.. code-block:: bash

   # Check environment variables
   env | grep OM
   
   # Reset environment
   unset OM_CONFIG OM_DATA_DIR
   
   # Use default settings
   om config --reset-env

Getting Help
------------

**Built-in Diagnostics**

.. code-block:: bash

   # Run comprehensive system check
   om doctor
   
   # Generate diagnostic report
   om doctor --report
   
   # Test all components
   om test --all

**Log Files**

.. code-block:: bash

   # View recent logs
   om logs --recent
   
   # Check error logs
   om logs --errors
   
   # Enable debug logging
   om config --debug-mode

**Community Support**

- **GitHub Issues**: https://github.com/frism/om/issues
- **Discussions**: https://github.com/frism/om/discussions
- **Documentation**: https://om-docs.readthedocs.io
- **Email**: schraube.eins@icloud.com

**Reporting Bugs**

When reporting issues, include:

.. code-block:: bash

   # Generate bug report
   om bug-report
   
   # This includes:
   # - System information
   # - Om version and configuration
   # - Recent error logs
   # - Diagnostic test results

**Emergency Mental Health Support**

If you're experiencing a mental health crisis:

- **National Suicide Prevention Lifeline**: 988
- **Crisis Text Line**: Text HOME to 741741
- **Emergency Services**: 911 (US) or your local emergency number

.. code-block:: bash

   # Quick access to crisis resources
   om rescue
   om crisis --immediate

Recovery Procedures
-------------------

**Complete Reset (Last Resort)**

.. code-block:: bash

   # Backup current data first
   om backup create --emergency
   
   # Complete reset (removes all data)
   om reset --complete --confirm
   
   # Reinstall from scratch
   ./install.sh

**Partial Recovery**

.. code-block:: bash

   # Reset only configuration
   om reset --config-only
   
   # Reset only AI coach data
   om reset --coach-only
   
   # Reset only gamification
   om reset --gamify-only

**Data Recovery**

.. code-block:: bash

   # Attempt automatic recovery
   om recover --auto
   
   # Manual data recovery
   om recover --manual --interactive
   
   # Recover from partial backup
   om recover --partial backup_file.json

Prevention
----------

**Regular Maintenance**

.. code-block:: bash

   # Weekly maintenance routine
   om maintenance --weekly
   
   # This includes:
   # - Database optimization
   # - Log rotation
   # - Cache cleanup
   # - Backup creation

**Health Checks**

.. code-block:: bash

   # Daily health check
   om health-check
   
   # Set up automatic health monitoring
   om config --auto-health-check

**Backup Strategy**

.. code-block:: bash

   # Set up automatic backups
   om backup schedule --daily
   
   # Test backup integrity
   om backup test --all
   
   # Keep multiple backup versions
   om backup retention --keep 7

.. note::
   
   Most issues can be resolved without losing your mental health data. Always try the least destructive solutions first, and create backups before making major changes.

.. warning::
   
   If you're experiencing a mental health crisis, prioritize getting immediate help over troubleshooting technical issues. Use ``om rescue`` for quick access to crisis resources.
