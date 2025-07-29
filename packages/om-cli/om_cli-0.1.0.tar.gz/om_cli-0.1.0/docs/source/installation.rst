Installation Guide
==================

System Requirements
-------------------

- **Python 3.11+**
- **50MB disk space**
- **Terminal access**

Quick Install (Recommended)
---------------------------

Install from PyPI with pip:

.. code-block:: bash

   pip install om-cli

Verify the installation:

.. code-block:: bash

   om --version
   om --help
   om qm

Alternative Installation Methods
-------------------------------

Install from Source
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/frism/om.git
   cd om
   pip install -r requirements.txt
   python setup.py install

Development Installation
~~~~~~~~~~~~~~~~~~~~~~~

For contributors and developers:

.. code-block:: bash

   git clone https://github.com/frism/om.git
   cd om
   pip install -e .

This installs om in "editable" mode, so changes to the source code are immediately reflected.

Troubleshooting
---------------

Permission Issues
~~~~~~~~~~~~~~~~~

If you encounter permission errors:

.. code-block:: bash

   pip install --user om-cli

Python Version Issues
~~~~~~~~~~~~~~~~~~~~

om requires Python 3.11+. Check your version:

.. code-block:: bash

   python --version

If you have multiple Python versions, use:

.. code-block:: bash

   python3.11 -m pip install om-cli

Dependencies
------------

Core dependencies are automatically installed with pip:

- **rich** - Beautiful terminal formatting
- **textual** - Modern TUI framework (optional)
- **click** - Command line interface creation
- **colorama** - Cross-platform colored terminal text
- **requests** - HTTP library for external integrations
- **flask** - Web framework for API server (optional)

Verification
------------

Test your installation:

.. code-block:: bash

   # Check version
   om --version

   # View help
   om --help

   # Try a quick action
   om qm

   # Test crisis support
   om rescue

If everything works, you're ready to start your mental wellness journey!

Uninstallation
--------------

To remove om-cli:

.. code-block:: bash

   pip uninstall om-cli

Your personal data in ``~/.om/`` will remain unless manually deleted.
