# Contributing to om 🧘‍♀️

Thank you for your interest in contributing to om! This project is built by and for the mental health community, and we welcome contributions from developers, mental health professionals, researchers, and users.

## 🌟 **Ways to Contribute**

### 🐛 **Bug Reports**
Help us improve reliability by reporting issues:
- Use the [GitHub Issues](https://github.com/yourusername/om/issues) page
- Include steps to reproduce the bug
- Provide system information (OS, Python version)
- Describe expected vs actual behavior

### 💡 **Feature Requests**
Suggest evidence-based improvements:
- Check existing issues to avoid duplicates
- Explain the mental health benefit
- Provide research backing if possible
- Consider privacy implications

### 📝 **Documentation**
Improve guides and references:
- Fix typos and unclear explanations
- Add usage examples
- Translate documentation
- Create video tutorials

### 🧪 **Testing**
Help test on different platforms:
- Test new features before release
- Verify cross-platform compatibility
- Report performance issues
- Test accessibility features

### 🌍 **Translations**
Make om accessible globally:
- Translate command descriptions
- Localize mental health resources
- Adapt cultural considerations
- Maintain translation accuracy

### 💻 **Code Contributions**
Contribute new features or improvements:
- Follow the development setup below
- Maintain code quality standards
- Include tests for new features
- Update documentation

## 🚀 **Getting Started**

### **Development Setup**

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/om.git
   cd om
   ```

2. **Set Up Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r tests/requirements-test.txt
   ```

3. **Run Tests**
   ```bash
   python -m pytest tests/
   python tests/test_production.py
   ```

4. **Test the Application**
   ```bash
   python main.py --help
   python main.py qm
   python main.py dashboard
   ```

### **Project Structure**

```
om/
├── main.py                 # Main application entry point
├── modules/                # Feature modules
│   ├── mood_tracking.py    # Mood tracking functionality
│   ├── cbt_toolkit.py      # CBT tools
│   ├── ai_companion.py     # AI mental health companion
│   ├── sleep_optimization.py # Sleep science tools
│   ├── positive_psychology.py # Positive psychology practices
│   ├── nicky_case_guide.py # Nicky Case integration
│   └── ...                 # Other modules
├── tests/                  # Test suite
├── docs/                   # Documentation
├── requirements.txt        # Dependencies
└── README.md              # Project overview
```

## 📋 **Development Guidelines**

### **Code Style**

- **Python Style**: Follow PEP 8
- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Include type hints where helpful
- **Comments**: Explain complex mental health logic

Example:
```python
def track_mood(mood: str, intensity: int, notes: str = "") -> bool:
    """Track a mood entry with validation.
    
    Args:
        mood: The mood category (e.g., 'happy', 'anxious')
        intensity: Mood intensity from 1-10
        notes: Optional notes about the mood
        
    Returns:
        True if mood was successfully tracked
        
    Raises:
        ValueError: If intensity is not between 1-10
    """
    if not 1 <= intensity <= 10:
        raise ValueError("Intensity must be between 1 and 10")
    
    # Implementation here
    return True
```

### **Mental Health Considerations**

- **Evidence-Based**: All interventions should have research backing
- **Crisis Safety**: Always provide crisis resources when appropriate
- **Privacy First**: Never transmit user data externally
- **Inclusive Language**: Use person-first, non-stigmatizing language
- **Professional Boundaries**: Clearly state limitations and encourage professional help

### **Testing Requirements**

- **Unit Tests**: Test individual functions
- **Integration Tests**: Test feature interactions
- **Privacy Tests**: Ensure no data leakage
- **Crisis Tests**: Verify crisis detection works
- **Accessibility Tests**: Ensure screen reader compatibility

Example test:
```python
def test_mood_tracking_privacy():
    """Ensure mood data stays local."""
    # Test that no network requests are made
    # Test that data is stored locally only
    # Test that data can be deleted
    pass

def test_crisis_detection():
    """Ensure crisis language is properly detected."""
    crisis_phrases = ["want to die", "end it all", "no point living"]
    for phrase in crisis_phrases:
        assert detect_crisis(phrase) == True
```

### **Documentation Standards**

- **User-Focused**: Write for people seeking mental health support
- **Clear Examples**: Provide concrete usage examples
- **Research Citations**: Include sources for evidence-based claims
- **Privacy Notes**: Clearly explain data handling
- **Crisis Information**: Always include crisis resources

## 🧠 **Mental Health Focus Areas**

### **High-Priority Contributions**

1. **Crisis Support Improvements**
   - Better crisis detection algorithms
   - More comprehensive resource databases
   - Improved safety planning tools

2. **Evidence-Based Interventions**
   - Additional CBT techniques
   - Mindfulness exercises
   - Behavioral activation tools
   - Exposure therapy guidance

3. **Accessibility Enhancements**
   - Screen reader optimization
   - Keyboard navigation improvements
   - Color contrast adjustments
   - Font size customization

4. **Privacy & Security**
   - Enhanced data encryption
   - Secure data export/import
   - Privacy audit tools
   - Anonymous usage analytics (opt-in)

### **Research Integration**

When adding new features:

1. **Literature Review**: Research the evidence base
2. **Clinical Validation**: Consult with mental health professionals
3. **User Testing**: Test with target populations
4. **Outcome Measurement**: Track effectiveness metrics

## 🔒 **Privacy & Ethics**

### **Privacy Requirements**

- **Local-Only Data**: All user data must stay on device
- **No Tracking**: No analytics or usage tracking without explicit consent
- **Transparent Storage**: Users must be able to inspect their data
- **Easy Deletion**: Users must be able to delete all data easily

### **Ethical Guidelines**

- **Do No Harm**: Features should not worsen mental health
- **Professional Boundaries**: Clearly state software limitations
- **Crisis Prioritization**: Always prioritize user safety
- **Inclusive Design**: Consider diverse mental health experiences

## 🧪 **Testing Your Contributions**

### **Before Submitting**

1. **Run All Tests**
   ```bash
   python -m pytest tests/ -v
   python tests/test_production.py
   ```

2. **Test Privacy**
   ```bash
   # Ensure no network requests during normal operation
   # Verify data stays in ~/.om/ directory
   # Test data deletion functionality
   ```

3. **Test Accessibility**
   ```bash
   # Test with screen reader
   # Verify keyboard navigation
   # Check color contrast
   ```

4. **Manual Testing**
   ```bash
   python main.py qm          # Quick mood check
   python main.py wolf        # Wolf conversation
   python main.py dashboard   # Dashboard display
   python main.py rescue      # Crisis resources
   ```

## 📝 **Pull Request Process**

### **Before Creating PR**

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow coding standards
   - Add tests
   - Update documentation

3. **Test Thoroughly**
   - Run full test suite
   - Test manually
   - Check privacy compliance

### **PR Description Template**

```markdown
## Description
Brief description of changes and mental health benefit.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Privacy enhancement

## Evidence Base
- Research citations supporting the change
- Mental health professional consultation (if applicable)

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Privacy compliance verified
- [ ] Accessibility tested

## Privacy Impact
- Does this change affect user data handling?
- Are there any new privacy considerations?

## Crisis Safety
- Does this change affect crisis detection or resources?
- Have safety implications been considered?

## Documentation
- [ ] README updated
- [ ] Documentation updated
- [ ] Code comments added
```

## 🌍 **Community Guidelines**

### **Code of Conduct**

- **Be Respectful**: Treat all contributors with respect
- **Be Inclusive**: Welcome diverse perspectives and experiences
- **Be Patient**: Remember that mental health is sensitive
- **Be Supportive**: Help others learn and contribute
- **Be Professional**: Maintain appropriate boundaries

### **Communication Channels**

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community chat
- **Email**: Direct contact for sensitive issues
- **Documentation**: Primary source of information

### **Mental Health Sensitivity**

When discussing mental health topics:

- Use person-first language ("person with depression" not "depressed person")
- Avoid stigmatizing terms
- Be mindful of triggers
- Provide content warnings when appropriate
- Always include crisis resources in relevant discussions

## 🏆 **Recognition**

### **Contributor Recognition**

- Contributors are listed in the README
- Significant contributions are highlighted in release notes
- Mental health professionals who provide guidance are specially acknowledged
- Community members who provide feedback and testing are recognized

### **Types of Contributions Valued**

- **Code**: New features, bug fixes, performance improvements
- **Documentation**: Guides, examples, translations
- **Testing**: Bug reports, compatibility testing, user feedback
- **Research**: Evidence-based feature suggestions, literature reviews
- **Community**: Helping other users, moderating discussions
- **Professional**: Mental health professional guidance and validation

## 📚 **Resources for Contributors**

### **Mental Health Resources**

- [National Institute of Mental Health](https://www.nimh.nih.gov/)
- [American Psychological Association](https://www.apa.org/)
- [World Health Organization Mental Health](https://www.who.int/health-topics/mental-health)

### **Technical Resources**

- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [pytest Documentation](https://docs.pytest.org/)

### **Privacy Resources**

- [Privacy by Design Principles](https://www.ipc.on.ca/wp-content/uploads/resources/7foundationalprinciples.pdf)
- [GDPR Guidelines](https://gdpr.eu/)
- [Mental Health Data Privacy Best Practices](https://www.hhs.gov/hipaa/for-professionals/special-topics/mental-health/index.html)

## 🚀 **Getting Help**

### **For Contributors**

- **Technical Questions**: Use GitHub Discussions
- **Mental Health Questions**: Consult with mental health professionals
- **Privacy Questions**: Email maintainers directly
- **General Help**: Check documentation first, then ask in discussions

### **For Users**

- **Bug Reports**: Use GitHub Issues
- **Feature Requests**: Use GitHub Issues with feature request template
- **Usage Questions**: Check documentation or use GitHub Discussions
- **Crisis Support**: Use `om rescue` command or contact emergency services

## 💝 **Thank You**

Your contributions help make mental health support more accessible, private, and effective. Whether you're fixing a typo, adding a feature, or providing feedback, you're helping people on their mental health journey.

**Remember**: Contributing to open source mental health tools is a form of community care. Thank you for caring about mental health and helping others.

---

**Questions?** Feel free to reach out through GitHub Discussions or email. We're here to help you contribute successfully!

**Crisis Resources**: If you're experiencing a mental health crisis, please contact:
- National Suicide Prevention Lifeline: 988 (US)
- Crisis Text Line: Text HOME to 741741 (US)
- Emergency Services: 911
- International resources: https://iasp.info/
