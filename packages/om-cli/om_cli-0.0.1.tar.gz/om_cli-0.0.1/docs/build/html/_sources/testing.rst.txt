Testing Strategy
================

This document outlines the comprehensive testing approach for the om mental health CLI application.

🎯 Testing Philosophy
---------------------

Mental health applications require exceptional reliability, security, and accessibility. Our testing strategy ensures:

- **Reliability**: The application works consistently across different environments
- **Security**: User data and privacy are protected
- **Accessibility**: The tool is usable by people with diverse needs
- **Performance**: Quick response times for immediate mental health support
- **Usability**: Intuitive interface that doesn't add stress to users' lives

📋 Test Categories
------------------

1. Unit Tests
~~~~~~~~~~~~~

**Purpose**: Test individual components in isolation

**Location**: ``tests/test_suite.py``, ``tests/test_modules.py``

**Coverage**:
   - Module imports and basic functionality
   - Individual function behavior
   - Error handling at the component level
   - Data validation and processing

**Example**:

.. code-block:: python

   def test_mood_tracking_basic():
       """Test basic mood tracking functionality"""
       from modules.mood_tracking import mood_command
       
       # Test mood entry creation
       result = mood_command(['add', 'happy', '8'])
       assert result is not None
       
       # Test mood validation
       with pytest.raises(ValueError):
           mood_command(['add', 'invalid_mood', '15'])

2. Integration Tests
~~~~~~~~~~~~~~~~~~~

**Purpose**: Test component interactions and workflows

**Location**: ``tests/test_integration.py``

**Coverage**:
   - End-to-end user workflows
   - Command-line interface interactions
   - Data persistence across sessions
   - Module communication

**Example**:

.. code-block:: python

   def test_daily_wellness_workflow():
       """Test complete daily wellness routine"""
       # Morning routine
       result1 = run_command(['morning'])
       assert 'wellness routine' in result1.output
       
       # Quick actions throughout day
       result2 = run_command(['qm'])
       result3 = run_command(['qb'])
       result4 = run_command(['qg'])
       
       # Evening review
       result5 = run_command(['evening'])
       assert all(r.exit_code == 0 for r in [result1, result2, result3, result4, result5])

3. Performance Tests
~~~~~~~~~~~~~~~~~~~

**Purpose**: Ensure responsive user experience

**Location**: ``tests/test_performance.py``

**Coverage**:
   - Startup time (target: <3 seconds average)
   - Memory usage (target: <50MB)
   - Concurrent execution handling
   - Large dataset processing
   - Quick action responsiveness (target: <5 seconds)

**Example**:

.. code-block:: python

   def test_startup_performance():
       """Test application startup time"""
       import time
       
       start_time = time.time()
       result = run_command(['help'])
       end_time = time.time()
       
       startup_time = end_time - start_time
       assert startup_time < 3.0, f"Startup took {startup_time:.2f}s, expected <3s"

4. Security Tests
~~~~~~~~~~~~~~~~

**Purpose**: Protect user data and prevent vulnerabilities

**Location**: ``tests/test_security_accessibility.py``

**Coverage**:
   - Input sanitization and validation
   - File permission security
   - Data encryption verification
   - Privacy protection measures
   - SQL injection prevention

**Example**:

.. code-block:: python

   def test_input_sanitization():
       """Test that user input is properly sanitized"""
       malicious_inputs = [
           "'; DROP TABLE mood_entries; --",
           "<script>alert('xss')</script>",
           "../../../etc/passwd",
           "$(rm -rf /)"
       ]
       
       for malicious_input in malicious_inputs:
           result = run_command(['mood', 'add', malicious_input])
           # Should not crash or execute malicious code
           assert result.exit_code in [0, 1]  # Success or handled error

5. Accessibility Tests
~~~~~~~~~~~~~~~~~~~~~

**Purpose**: Ensure usability for people with diverse needs

**Coverage**:
   - Screen reader compatibility
   - Keyboard-only navigation
   - Color contrast requirements
   - Text size and readability
   - Cognitive load assessment

**Example**:

.. code-block:: python

   def test_screen_reader_compatibility():
       """Test that output is screen reader friendly"""
       result = run_command(['gamify', 'status'])
       
       # Check for proper structure
       assert 'Level' in result.output
       assert 'Points' in result.output
       
       # Ensure no visual-only information
       assert not any(char in result.output for char in ['█', '▓', '▒', '░'])

6. Crisis Support Tests
~~~~~~~~~~~~~~~~~~~~~~

**Purpose**: Ensure crisis support features work reliably

**Coverage**:
   - Crisis detection accuracy
   - Resource accessibility
   - Emergency contact functionality
   - Safety planning tools
   - Response time verification

**Example**:

.. code-block:: python

   def test_crisis_support_availability():
       """Test that crisis support is always available"""
       crisis_commands = ['rescue', 'crisis', 'emergency', 'resc']
       
       for command in crisis_commands:
           result = run_command([command])
           assert result.exit_code == 0
           assert 'crisis' in result.output.lower() or 'emergency' in result.output.lower()
           assert 'help' in result.output.lower()

🧪 Test Implementation
---------------------

Test Suite Structure
~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   tests/
   ├── __init__.py
   ├── conftest.py                 # Pytest configuration and fixtures
   ├── test_suite.py              # Main test suite
   ├── test_modules.py            # Individual module tests
   ├── test_integration.py        # Integration tests
   ├── test_performance.py        # Performance benchmarks
   ├── test_security_accessibility.py  # Security and accessibility
   ├── test_crisis_support.py     # Crisis support specific tests
   ├── test_data/                 # Test data files
   │   ├── sample_mood_data.json
   │   ├── test_achievements.json
   │   └── mock_responses.json
   └── fixtures/                  # Test fixtures
       ├── database_fixtures.py
       ├── mock_data.py
       └── test_helpers.py

Test Configuration
~~~~~~~~~~~~~~~~~

**conftest.py**:

.. code-block:: python

   import pytest
   import tempfile
   import os
   from unittest.mock import patch
   
   @pytest.fixture
   def temp_data_dir():
       """Create temporary directory for test data"""
       with tempfile.TemporaryDirectory() as temp_dir:
           with patch.dict(os.environ, {'OM_DATA_DIR': temp_dir}):
               yield temp_dir
   
   @pytest.fixture
   def mock_database():
       """Create mock database for testing"""
       from om_database import DatabaseManager
       with tempfile.NamedTemporaryFile(suffix='.db') as temp_db:
           db = DatabaseManager(temp_db.name)
           db.initialize_database()
           yield db
   
   @pytest.fixture
   def sample_mood_data():
       """Provide sample mood data for testing"""
       return [
           {'mood': 'happy', 'intensity': 8, 'date': '2025-01-01'},
           {'mood': 'anxious', 'intensity': 6, 'date': '2025-01-02'},
           {'mood': 'calm', 'intensity': 7, 'date': '2025-01-03'}
       ]

Running Tests
~~~~~~~~~~~~

**Quick Test Suite**:

.. code-block:: bash

   # Run basic functionality tests
   ./test.sh quick

**Full Test Suite**:

.. code-block:: bash

   # Run all tests including performance and security
   ./test.sh

**Specific Test Categories**:

.. code-block:: bash

   # Unit tests only
   pytest tests/test_modules.py -v
   
   # Integration tests
   pytest tests/test_integration.py -v
   
   # Performance tests
   pytest tests/test_performance.py -v
   
   # Security tests
   pytest tests/test_security_accessibility.py -v

**Coverage Report**:

.. code-block:: bash

   # Generate coverage report
   pytest --cov=modules --cov-report=html tests/

📊 Test Metrics and Targets
---------------------------

Quality Targets
~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Metric
     - Target
     - Description
   * - Code Coverage
     - >90%
     - Percentage of code covered by tests
   * - Test Pass Rate
     - >95%
     - Percentage of tests passing
   * - Startup Time
     - <3 seconds
     - Average application startup time
   * - Memory Usage
     - <50MB
     - Peak memory usage during operation
   * - Crisis Response
     - <1 second
     - Time to display crisis resources
   * - Quick Actions
     - <5 seconds
     - Time to complete quick wellness actions

Performance Benchmarks
~~~~~~~~~~~~~~~~~~~~~~

**Startup Performance**:

.. code-block:: python

   def test_startup_benchmarks():
       """Benchmark application startup performance"""
       times = []
       for _ in range(10):
           start = time.time()
           run_command(['--version'])
           end = time.time()
           times.append(end - start)
       
       avg_time = sum(times) / len(times)
       assert avg_time < 3.0, f"Average startup: {avg_time:.2f}s"

**Memory Usage**:

.. code-block:: python

   def test_memory_usage():
       """Monitor memory usage during operation"""
       import psutil
       import os
       
       process = psutil.Process(os.getpid())
       initial_memory = process.memory_info().rss
       
       # Run memory-intensive operations
       run_command(['dashboard', 'show'])
       run_command(['gamify', 'status', '-v'])
       run_command(['coach', 'analyze'])
       
       peak_memory = process.memory_info().rss
       memory_used = (peak_memory - initial_memory) / 1024 / 1024  # MB
       
       assert memory_used < 50, f"Memory usage: {memory_used:.1f}MB"

🔒 Security Testing
------------------

Input Validation Tests
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def test_sql_injection_prevention():
       """Test SQL injection attack prevention"""
       malicious_inputs = [
           "'; DROP TABLE mood_entries; --",
           "1' OR '1'='1",
           "'; INSERT INTO mood_entries VALUES ('hack'); --"
       ]
       
       for injection in malicious_inputs:
           result = run_command(['mood', 'add', injection])
           # Should handle gracefully without executing SQL
           assert result.exit_code in [0, 1]

File Security Tests
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def test_file_permissions():
       """Test that data files have secure permissions"""
       import stat
       
       data_files = [
           '~/.om/mood_data.json',
           '~/.om/wellness_stats.json',
           '~/.om/achievements.json'
       ]
       
       for file_path in data_files:
           expanded_path = os.path.expanduser(file_path)
           if os.path.exists(expanded_path):
               file_stat = os.stat(expanded_path)
               permissions = stat.filemode(file_stat.st_mode)
               # Should be readable/writable by owner only
               assert permissions.startswith('-rw-------')

♿ Accessibility Testing
-----------------------

Screen Reader Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def test_screen_reader_output():
       """Test output is screen reader friendly"""
       result = run_command(['help'])
       
       # Check for proper headings
       assert any(line.strip().endswith(':') for line in result.output.split('\n'))
       
       # Check for descriptive text
       assert 'mental health' in result.output.lower()
       assert 'wellness' in result.output.lower()

Color Accessibility
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def test_color_independence():
       """Test that information isn't conveyed by color alone"""
       result = run_command(['gamify', 'status'])
       
       # Should have text indicators, not just colors
       assert any(word in result.output for word in ['Level', 'Points', 'Progress'])
       
       # Check for symbols or text alongside any color coding
       if '█' in result.output:  # Progress bars
           assert any(char.isdigit() for char in result.output)  # Should have numbers too

🚨 Crisis Support Testing
-------------------------

Crisis Detection Tests
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def test_crisis_keyword_detection():
       """Test crisis keyword detection in user input"""
       crisis_phrases = [
           "I want to hurt myself",
           "I'm thinking about suicide",
           "I can't go on anymore",
           "I'm having a panic attack"
       ]
       
       for phrase in crisis_phrases:
           # Test that crisis support is triggered
           result = run_command(['mood', 'add', phrase])
           assert 'crisis' in result.output.lower() or 'help' in result.output.lower()

Resource Availability Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def test_crisis_resources_always_available():
       """Test that crisis resources are always accessible"""
       # Test multiple ways to access crisis support
       crisis_commands = ['rescue', 'crisis', 'emergency', 'help']
       
       for command in crisis_commands:
           result = run_command([command])
           assert result.exit_code == 0
           assert len(result.output) > 0
           
           # Should contain emergency contact information
           assert any(number in result.output for number in ['988', '741741'])

🔄 Continuous Integration
------------------------

Automated Testing Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # .github/workflows/test.yml
   name: Test Suite
   
   on: [push, pull_request]
   
   jobs:
     test:
       runs-on: ubuntu-latest
       strategy:
         matrix:
           python-version: [3.9, 3.10, 3.11]
       
       steps:
       - uses: actions/checkout@v2
       - name: Set up Python
         uses: actions/setup-python@v2
         with:
           python-version: ${{ matrix.python-version }}
       
       - name: Install dependencies
         run: |
           pip install -r requirements.txt
           pip install -r tests/requirements-test.txt
       
       - name: Run tests
         run: |
           pytest tests/ --cov=modules --cov-report=xml
       
       - name: Upload coverage
         uses: codecov/codecov-action@v1

Test Reporting
~~~~~~~~~~~~~

.. code-block:: python

   def generate_test_report():
       """Generate comprehensive test report"""
       import json
       from datetime import datetime
       
       report = {
           'timestamp': datetime.now().isoformat(),
           'test_results': {
               'total_tests': 0,
               'passed': 0,
               'failed': 0,
               'skipped': 0
           },
           'performance_metrics': {
               'startup_time': 0,
               'memory_usage': 0,
               'response_times': {}
           },
           'coverage': {
               'percentage': 0,
               'missing_lines': []
           }
       }
       
       # Save report
       with open('test_report.json', 'w') as f:
           json.dump(report, f, indent=2)

📝 Test Documentation
---------------------

Writing Good Tests
~~~~~~~~~~~~~~~~~

**Test Naming Convention**:

.. code-block:: python

   def test_[component]_[scenario]_[expected_result]():
       """Test that [component] [does something] when [condition]"""
       pass

**Test Structure (AAA Pattern)**:

.. code-block:: python

   def test_mood_tracking_adds_entry_successfully():
       """Test that mood tracking adds entry successfully"""
       # Arrange
       initial_count = get_mood_entry_count()
       
       # Act
       result = add_mood_entry('happy', 8)
       
       # Assert
       assert result.success is True
       assert get_mood_entry_count() == initial_count + 1

**Error Testing**:

.. code-block:: python

   def test_mood_tracking_handles_invalid_input():
       """Test that mood tracking handles invalid input gracefully"""
       with pytest.raises(ValueError, match="Invalid mood value"):
           add_mood_entry('invalid_mood', 15)

Test Maintenance
~~~~~~~~~~~~~~~

- **Regular Review**: Review and update tests monthly
- **Refactoring**: Keep tests clean and maintainable
- **Documentation**: Document complex test scenarios
- **Performance**: Monitor test execution time
- **Coverage**: Maintain high test coverage

The comprehensive testing strategy ensures that the om mental health platform is reliable, secure, accessible, and performant, providing users with a trustworthy tool for their mental wellness journey.
