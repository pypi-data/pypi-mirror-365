from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    if os.path.exists("README_PYPI.md"):
        with open("README_PYPI.md", "r", encoding="utf-8") as fh:
            return fh.read()
    elif os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    else:
        return "Advanced Mental Health CLI Platform with AI-Powered Wellness"

# Read requirements
def read_requirements():
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return []

setup(
    name="om-cli",
    version="0.0.1",
    author="frism",
    author_email="contact@om-cli.org",
    description="Advanced Mental Health CLI Platform - Privacy-first wellness toolkit with AI coaching, CBT tools, crisis support, and evidence-based interventions",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/frism/om",
    packages=find_packages(),
    py_modules=["main", "om_db"],
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json", "*.sql"],
        "modules": ["*.py"],
        "docs": ["**/*"],
        "database": ["**/*"],
        "api": ["**/*"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Utilities",
        "Topic :: Terminals",
        "Environment :: Console",
        "Natural Language :: English",
    ],
    python_requires=">=3.11",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "om=main:main",
        ],
    },
    keywords=[
        "mental-health", "wellness", "cli", "mindfulness", "meditation", 
        "cbt", "therapy", "anxiety", "depression", "self-care", "privacy",
        "terminal", "coaching", "crisis-support", "mood-tracking"
    ],
    project_urls={
        "Homepage": "https://github.com/frism/om",
        "Bug Reports": "https://github.com/frism/om/issues",
        "Source": "https://github.com/frism/om",
        "Documentation": "https://github.com/frism/om/tree/main/docs",
        "Funding": "https://ko-fi.com/omcli",
    },
    zip_safe=False,
)
