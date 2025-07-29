# Om Mental Health Platform - Testing System

Comprehensive testing suite for the om mental health CLI platform.

## 🧪 Testing Scripts

### 1. **Comprehensive Test Suite** (`test_all_commands.sh`)
Tests every single command available in the om platform with detailed logging and error reporting.

```bash
# Run complete test suite
./test_all_commands.sh

# Features:
# - Tests 200+ commands and variations
# - Detailed logging with timestamps
# - Color-coded output (PASS/FAIL/SKIP)
# - Comprehensive error reporting
# - Success rate calculation
# - Full test log saved to file
```

### 2. **Quick Test** (`quick_test.sh`)
Fast verification of essential commands for basic functionality checking.

```bash
# Run quick essential tests
./quick_test.sh

# Features:
# - Tests ~20 core commands
# - 3-second timeout per command
# - Quick pass/fail results
# - Perfect for CI/CD pipelines
```

### 3. **Advanced Test Runner** (`run_tests.sh`)
JSON-configured test runner with category-based testing and advanced reporting.

```bash
# Run all test categories
./run_tests.sh

# Run specific categories
./run_tests.sh quick_actions crisis_support
./run_tests.sh ai_features dashboard

# Show available categories
./run_tests.sh --help
```

## 📋 Test Categories

### **Core Functionality**
- **quick_actions** - Ultra-fast wellness commands (qm, qb, qg, etc.)
- **crisis_support** - International crisis intervention system
- **ai_features** - AI coaching, autopilot, and gamification
- **dashboard** - Visual wellness dashboard and metrics

### **Mental Health Features**
- **mood_tracking** - Mood tracking and mental health monitoring
- **wellness_practices** - Breathing, meditation, gratitude, affirmations
- **sleep_support** - Sleep optimization and therapeutic sounds
- **cbt_therapeutic** - CBT toolkit and therapeutic tools

### **Advanced Features**
- **nicky_case** - Nicky Case integration and guides
- **advanced_features** - Intention timer, hypnosis, neurowave
- **habits_routines** - Habit tracking and daily routines

### **System Management**
- **data_management** - Backup, export, and data tools
- **system_config** - Configuration, help, and status
- **api_integrations** - API server and external integrations
- **testing_diagnostics** - System testing and diagnostics

## 🎯 Test Configuration

### **JSON Configuration** (`test_config.json`)
Centralized configuration for test categories, commands, and settings:

```json
{
  "test_categories": {
    "quick_actions": {
      "description": "Ultra-fast wellness commands",
      "commands": [
        {"cmd": "qm", "desc": "Quick mood check"},
        {"cmd": "qb", "desc": "Quick breathing exercise"}
      ]
    }
  },
  "test_settings": {
    "timeout_seconds": 10,
    "max_retries": 2,
    "skip_interactive": true
  }
}
```

## 📊 Test Results

### **Output Format**
```
🧘‍♀️ Om Mental Health Platform - Test Results
=============================================

🔧 TESTING SECTION: QUICK ACTIONS
==================================================
✅ PASS | qm | Quick mood check (10 seconds)
✅ PASS | qb | Quick breathing exercise (2 minutes)
❌ FAIL | qc | Command produced error output
⏭️  SKIP | setup | Command timed out (interactive)

🏁 TEST RESULTS SUMMARY
=========================
Total Tests: 150
Passed: 142
Failed: 3
Skipped: 5
Success Rate: 94%
```

### **Log Files**
- **Comprehensive logs**: `om_test_results_YYYYMMDD_HHMMSS.log`
- **Quick test logs**: Console output only
- **Advanced runner logs**: `test_results_YYYYMMDD_HHMMSS.log`

## 🚀 Usage Examples

### **Development Testing**
```bash
# Test specific feature during development
./run_tests.sh crisis_support

# Quick smoke test
./quick_test.sh

# Full regression test
./test_all_commands.sh
```

### **CI/CD Integration**
```bash
# In your CI pipeline
./quick_test.sh || exit 1

# For comprehensive testing
./run_tests.sh && echo "All tests passed" || echo "Tests failed"
```

### **Pre-deployment Verification**
```bash
# Full system test before deployment
./test_all_commands.sh > deployment_test.log 2>&1

# Check critical systems
./run_tests.sh crisis_support ai_features system_config
```

## 🔧 Test Command Categories

### **Quick Actions (Q-Series)**
```bash
qm    # Quick mood check (10s)
qb    # Quick breathing (2min)
qg    # Quick gratitude (30s)
qf    # Quick focus (1min)
qc    # Quick calm (90s)
```

### **Crisis Support**
```bash
crisis              # Crisis resources
emergency           # Emergency intervention
rescue              # Rescue sessions
rescue international # Global crisis menu
911/112/999         # Emergency aliases
```

### **AI Features**
```bash
coach               # AI mental health coach
coach daily         # Daily insights
autopilot           # Wellness autopilot
gamify              # Gamification system
dashboard           # Wellness dashboard
```

### **Mental Health Core**
```bash
mood                # Mood tracking
anxiety             # Anxiety support
depression          # Depression resources
breathing           # Breathing exercises
meditation          # Meditation sessions
```

## 📈 Success Criteria

### **Test Categories**
- **90%+ Pass Rate**: Excellent system health
- **75-89% Pass Rate**: Good functionality, minor issues
- **<75% Pass Rate**: Needs attention, significant problems

### **Critical Commands**
These commands must always pass:
- `help`, `status`, `version`
- `crisis`, `emergency`, `rescue`
- `qm`, `qb`, `qg` (quick actions)
- `coach`, `dashboard`

### **Expected Behaviors**
- **Interactive commands** may timeout (expected)
- **Help commands** should always work
- **Crisis commands** are critical and must pass
- **Quick commands** should complete in <10 seconds

## 🛠️ Troubleshooting

### **Common Issues**

**Command Not Found**
```bash
# Ensure om is executable
chmod +x ./om

# Check if running from correct directory
ls -la ./om
```

**Timeout Issues**
```bash
# Increase timeout in test scripts
TIMEOUT=30  # Increase from default 10 seconds

# Skip interactive commands
./run_tests.sh --skip-interactive
```

**Permission Errors**
```bash
# Make all test scripts executable
chmod +x *.sh

# Check file permissions
ls -la test_*.sh run_tests.sh
```

### **Test Failures**

**High Failure Rate**
1. Check om executable exists and is working
2. Verify all dependencies are installed
3. Check for missing modules or files
4. Review error logs for specific issues

**Specific Command Failures**
1. Run command manually to see error
2. Check if command requires setup/configuration
3. Verify command syntax and arguments
4. Check for missing dependencies

## 📝 Adding New Tests

### **Add to Comprehensive Test**
Edit `test_all_commands.sh`:
```bash
# Add to appropriate section
test_command "new_command" "Description of new command"
test_command_with_args "command" "args" "Description"
```

### **Add to JSON Configuration**
Edit `test_config.json`:
```json
{
  "commands": [
    {"cmd": "new_command", "desc": "New command description"}
  ]
}
```

### **Create New Category**
```json
{
  "new_category": {
    "description": "New feature category",
    "commands": [
      {"cmd": "command1", "desc": "First command"},
      {"cmd": "command2", "desc": "Second command"}
    ]
  }
}
```

## 🎯 Best Practices

### **Running Tests**
1. **Always test from project root**: `cd /path/to/om && ./test_all_commands.sh`
2. **Use appropriate test level**: Quick for development, comprehensive for releases
3. **Check logs for failures**: Don't just look at pass/fail counts
4. **Test after major changes**: Especially crisis support and AI features

### **Test Development**
1. **Test both success and failure cases**
2. **Include edge cases and invalid inputs**
3. **Test interactive and non-interactive modes**
4. **Verify error handling and graceful degradation**

### **Continuous Integration**
1. **Use quick_test.sh for fast feedback**
2. **Run comprehensive tests on releases**
3. **Test on multiple environments**
4. **Archive test logs for debugging**

## 🔒 Privacy & Security Testing

### **Data Protection Tests**
- Verify no sensitive data in logs
- Test data export/import functionality
- Validate local-only storage
- Check crisis data privacy

### **Security Considerations**
- Test input validation
- Verify no code injection vulnerabilities
- Check file permission handling
- Validate API security (if enabled)

---

**Remember**: The om platform deals with sensitive mental health data. Always ensure tests respect user privacy and don't expose personal information in logs or outputs.

**For support**: schraube.eins@icloud.com | GitHub: https://github.com/frism/om
