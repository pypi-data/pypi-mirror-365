Installation Guide
==================

System Requirements
-------------------

- Python 3.11 or higher
- macOS, Linux, or Windows
- Terminal/Command Line access

Quick Installation
------------------

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/yourusername/om.git
   cd om

   # Install dependencies
   pip install -r requirements.txt

   # Make executable (macOS/Linux)
   chmod +x om install.sh
   ./install.sh

   # Test installation
   om --version

Manual Installation
-------------------

If the automatic installation doesn't work:

.. code-block:: bash

   # Install Python dependencies
   pip install -r requirements.txt

   # Create symbolic link (optional)
   ln -s $(pwd)/om /usr/local/bin/om

   # Or add to PATH
   export PATH="$PATH:$(pwd)"

Dependencies
------------

Core dependencies from ``requirements.txt``:

.. code-block:: text

   rich>=13.0.0
   textual>=0.40.0
   click>=8.0.0
   python-dateutil>=2.8.0
   matplotlib>=3.5.0
   numpy>=1.21.0

Verification
------------

Test your installation:

.. code-block:: bash

   # Check version
   om --version

   # Run help
   om help

   # Test core functionality
   om qm  # Quick mood check

Troubleshooting
---------------

**Permission Denied**
   .. code-block:: bash

      chmod +x om

**Module Not Found**
   .. code-block:: bash

      pip install -r requirements.txt

**Command Not Found**
   Add the om directory to your PATH or use the full path:
   
   .. code-block:: bash

      /path/to/om/om help
