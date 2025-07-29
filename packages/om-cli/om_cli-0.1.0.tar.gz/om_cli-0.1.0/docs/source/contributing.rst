Contributing Guide
==================

We welcome contributions to the om mental health platform! This guide will help you get started.

Development Setup
-----------------

1. **Fork and Clone**
   .. code-block:: bash

      git clone https://github.com/yourusername/om.git
      cd om

2. **Install Dependencies**
   .. code-block:: bash

      pip install -r requirements.txt
      pip install -r tests/requirements-test.txt

3. **Run Tests**
   .. code-block:: bash

      ./test.sh quick

Project Structure
-----------------

.. code-block:: text

   om/
   ├── om                    # Main CLI script
   ├── main.py              # Core application logic
   ├── modules/             # Mental health modules
   │   ├── mood_tracking.py
   │   ├── breathing.py
   │   ├── habits.py
   │   └── ...
   ├── docs/                # Documentation
   ├── tests/               # Test suite
   └── requirements.txt     # Dependencies

Contributing Areas
------------------

🧠 **AI Coaching Algorithms**
   - Improve pattern recognition
   - Enhance recommendation systems
   - Add new coaching strategies

🎮 **Gamification Mechanics**
   - Design new achievements
   - Create engaging challenges
   - Improve motivation systems

📊 **Dashboard Visualizations**
   - Add new chart types
   - Improve data presentation
   - Create interactive elements

🧘 **Mental Health Modules**
   - Add new wellness practices
   - Improve existing modules
   - Create specialized tools

🆘 **Crisis Support Tools**
   - Enhance crisis detection
   - Add support resources
   - Improve safety features

Development Guidelines
----------------------

Code Style
~~~~~~~~~~

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and small

Module Development
~~~~~~~~~~~~~~~~~~

When creating new modules:

1. **Follow the Template**
   .. code-block:: python

      """
      Module description
      """
      
      def run(args=None):
          """Main entry point"""
          pass
      
      def main():
          """Alternative entry point"""
          import sys
          args = sys.argv[1:] if len(sys.argv) > 1 else []
          run(args)
      
      if __name__ == "__main__":
          main()

2. **Add Help Text**
   .. code-block:: python

      def show_help():
          print("📋 Module Name")
          print("Description of what this module does")
          print()
          print("Available commands:")
          print("  om module action1  - Description")
          print("  om module action2  - Description")

3. **Handle Errors Gracefully**
   .. code-block:: python

      try:
          # Module logic
          pass
      except Exception as e:
          print(f"❌ Error: {e}")
          print("Please try again or contact support")

Testing
-------

**Run All Tests**
   .. code-block:: bash

      ./test.sh

**Run Quick Tests**
   .. code-block:: bash

      ./test.sh quick

**Test Specific Module**
   .. code-block:: bash

      python -m pytest tests/test_module_name.py

**Add New Tests**
   Create test files in the ``tests/`` directory:
   
   .. code-block:: python

      import unittest
      from modules.your_module import your_function
      
      class TestYourModule(unittest.TestCase):
          def test_basic_functionality(self):
              result = your_function()
              self.assertIsNotNone(result)

Documentation
-------------

**Update Documentation**
   When adding features, update:
   
   - README.md
   - Module docstrings
   - Help text
   - This documentation

**Build Documentation**
   .. code-block:: bash

      cd docs
      make html

**Preview Documentation**
   .. code-block:: bash

      cd docs/build/html
      python -m http.server 8000

Pull Request Process
--------------------

1. **Create Feature Branch**
   .. code-block:: bash

      git checkout -b feature/your-feature-name

2. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

3. **Test Changes**
   .. code-block:: bash

      ./test.sh
      # Ensure all tests pass

4. **Commit Changes**
   .. code-block:: bash

      git add .
      git commit -m "Add: Brief description of changes"

5. **Push and Create PR**
   .. code-block:: bash

      git push origin feature/your-feature-name
      # Create pull request on GitHub

Code Review Guidelines
----------------------

**For Contributors**
   - Write clear commit messages
   - Include tests for new features
   - Update documentation
   - Respond to feedback promptly

**For Reviewers**
   - Be constructive and helpful
   - Focus on code quality and mental health best practices
   - Test the changes locally
   - Approve when ready

Mental Health Considerations
----------------------------

When contributing to om, please consider:

- **User Safety**: Ensure features don't harm users
- **Privacy**: Maintain local-only data storage
- **Accessibility**: Make features usable by everyone
- **Evidence-Based**: Use proven mental health techniques
- **Crisis Support**: Always provide appropriate resources

Getting Help
------------

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Documentation**: Check existing docs first
- **Code Review**: Learn from feedback

Thank you for contributing to mental health technology! 💚
