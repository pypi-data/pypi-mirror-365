# om Documentation

This directory contains the Sphinx documentation for the om mental health CLI platform.

## 🚀 Quick Start

### View Documentation
```bash
# From the om root directory
./om docs                    # Show documentation info
./om docs serve             # Start local server
./om docs-build             # Build documentation
```

### Manual Build
```bash
cd docs
make html                   # Build HTML documentation
make serve                  # Serve documentation locally
make clean                  # Clean build files
```

## 📁 Structure

```
docs/
├── source/                 # Source files
│   ├── index.rst          # Main documentation page
│   ├── installation.rst   # Installation guide
│   ├── quickstart.rst     # Quick start guide
│   ├── features.rst       # Features overview
│   ├── modules.rst        # Modules reference
│   ├── api.rst           # API documentation
│   ├── contributing.rst   # Contributing guide
│   └── conf.py           # Sphinx configuration
├── build/                 # Built documentation
│   └── html/             # HTML output
├── Makefile              # Build commands
└── README.md             # This file
```

## 🛠️ Development

### Prerequisites
```bash
pip install sphinx sphinx-rtd-theme
```

### Adding New Pages
1. Create new `.rst` file in `source/`
2. Add to `toctree` in `index.rst`
3. Build documentation

### Auto-documentation
The API documentation is automatically generated from docstrings in the code using Sphinx autodoc.

### Live Reload (Optional)
```bash
pip install sphinx-autobuild
make livehtml
```

## 📖 Writing Documentation

### reStructuredText Basics
```rst
Page Title
==========

Section
-------

Subsection
~~~~~~~~~~

**Bold text**
*Italic text*
``Code text``

.. code-block:: bash

   om mood track

.. note::
   This is a note box
```

### Code Documentation
Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """Brief description of the function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Example:
        >>> example_function("hello", 42)
        True
    """
    return True
```

## 🎨 Themes and Styling

The documentation uses the Read the Docs theme (`sphinx_rtd_theme`). Customizations can be made in:
- `source/conf.py` - Configuration
- `source/_static/` - Custom CSS/JS
- `source/_templates/` - Custom templates

## 🔧 Troubleshooting

### Common Issues

**Module import errors**
- Ensure all dependencies are installed
- Check Python path in `conf.py`

**Build warnings**
- Missing references to other documents
- Malformed reStructuredText syntax
- Missing docstrings

**Broken links**
- Check internal references
- Verify external URLs

### Getting Help
- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/)

## 📝 Contributing

When contributing to documentation:

1. Follow reStructuredText conventions
2. Update relevant sections for new features
3. Test documentation builds locally
4. Keep language clear and accessible
5. Include code examples where helpful

The documentation is as important as the code - it helps users understand and effectively use om for their mental health journey! 🧘‍♀️
