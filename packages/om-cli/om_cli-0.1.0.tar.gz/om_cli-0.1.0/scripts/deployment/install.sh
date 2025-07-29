#!/bin/bash

# om Mental Health CLI Platform - Installation Script
# This script installs om and sets up the necessary environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Unicode symbols
CHECK="✅"
CROSS="❌"
INFO="ℹ️"
ROCKET="🚀"
HEART="💝"

echo -e "${PURPLE}"
echo "🧘‍♀️ om Mental Health CLI Platform"
echo "=================================="
echo -e "${NC}"
echo "Advanced Mental Health CLI with AI-Powered Wellness"
echo "Privacy-first • Evidence-based • Production ready"
echo ""

# Check if Python 3.11+ is available
echo -e "${BLUE}${INFO} Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
        echo -e "${GREEN}${CHECK} Python $PYTHON_VERSION found${NC}"
        PYTHON_CMD="python3"
    else
        echo -e "${RED}${CROSS} Python 3.11+ required, found $PYTHON_VERSION${NC}"
        echo "Please install Python 3.11 or higher"
        exit 1
    fi
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
        echo -e "${GREEN}${CHECK} Python $PYTHON_VERSION found${NC}"
        PYTHON_CMD="python"
    else
        echo -e "${RED}${CROSS} Python 3.11+ required, found $PYTHON_VERSION${NC}"
        echo "Please install Python 3.11 or higher"
        exit 1
    fi
else
    echo -e "${RED}${CROSS} Python not found${NC}"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

# Check if pip is available
echo -e "${BLUE}${INFO} Checking pip...${NC}"
if command -v pip3 &> /dev/null; then
    echo -e "${GREEN}${CHECK} pip3 found${NC}"
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    echo -e "${GREEN}${CHECK} pip found${NC}"
    PIP_CMD="pip"
else
    echo -e "${RED}${CROSS} pip not found${NC}"
    echo "Please install pip"
    exit 1
fi

# Install dependencies
echo -e "${BLUE}${INFO} Installing dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    $PIP_CMD install -r requirements.txt
    echo -e "${GREEN}${CHECK} Dependencies installed${NC}"
else
    echo -e "${RED}${CROSS} requirements.txt not found${NC}"
    echo "Please run this script from the om directory"
    exit 1
fi

# Create data directory
echo -e "${BLUE}${INFO} Setting up data directory...${NC}"
DATA_DIR="$HOME/.om"
if [ ! -d "$DATA_DIR" ]; then
    mkdir -p "$DATA_DIR"
    echo -e "${GREEN}${CHECK} Created data directory: $DATA_DIR${NC}"
else
    echo -e "${GREEN}${CHECK} Data directory exists: $DATA_DIR${NC}"
fi

# Set permissions
echo -e "${BLUE}${INFO} Setting permissions...${NC}"
chmod +x main.py
echo -e "${GREEN}${CHECK} Permissions set${NC}"

# Create symlink for global access (optional)
echo -e "${BLUE}${INFO} Setting up global access...${NC}"
INSTALL_DIR=$(pwd)
SYMLINK_PATH="/usr/local/bin/om"

if [ -w "/usr/local/bin" ]; then
    # Create symlink if we have write access
    if [ -L "$SYMLINK_PATH" ]; then
        rm "$SYMLINK_PATH"
    fi
    ln -s "$INSTALL_DIR/main.py" "$SYMLINK_PATH"
    echo -e "${GREEN}${CHECK} Global 'om' command available${NC}"
elif command -v sudo &> /dev/null; then
    # Try with sudo
    echo -e "${YELLOW}Creating global 'om' command (requires sudo)...${NC}"
    if sudo -n true 2>/dev/null; then
        # Can sudo without password
        if [ -L "$SYMLINK_PATH" ]; then
            sudo rm "$SYMLINK_PATH"
        fi
        sudo ln -s "$INSTALL_DIR/main.py" "$SYMLINK_PATH"
        echo -e "${GREEN}${CHECK} Global 'om' command available${NC}"
    else
        # Need password for sudo
        echo "To enable global 'om' command, please enter your password:"
        if [ -L "$SYMLINK_PATH" ]; then
            sudo rm "$SYMLINK_PATH"
        fi
        if sudo ln -s "$INSTALL_DIR/main.py" "$SYMLINK_PATH"; then
            echo -e "${GREEN}${CHECK} Global 'om' command available${NC}"
        else
            echo -e "${YELLOW}⚠️  Global command setup failed, you can still use: python3 main.py${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Cannot create global command, you can still use: python3 main.py${NC}"
fi

# Run initial setup
echo -e "${BLUE}${INFO} Running initial setup...${NC}"
$PYTHON_CMD main.py --version > /dev/null 2>&1
echo -e "${GREEN}${CHECK} Initial setup complete${NC}"

# Run production tests
echo -e "${BLUE}${INFO} Running production readiness tests...${NC}"
if [ -f "tests/test_production.py" ]; then
    if $PYTHON_CMD tests/test_production.py > /dev/null 2>&1; then
        echo -e "${GREEN}${CHECK} Production tests passed${NC}"
    else
        echo -e "${YELLOW}⚠️  Some production tests failed (non-critical)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Production tests not found${NC}"
fi

# Installation complete
echo ""
echo -e "${GREEN}${ROCKET} Installation Complete!${NC}"
echo ""
echo -e "${CYAN}Quick Start:${NC}"
echo "  om --help          # Show all available commands"
echo "  om qm              # Quick mood check (10 seconds)"
echo "  om qb              # Quick breathing exercise (2 minutes)"
echo "  om wolf            # Talk to your inner wolf (anxiety)"
echo "  om dashboard       # View your wellness dashboard"
echo ""
echo -e "${CYAN}Evidence-Based Features:${NC}"
echo "  om cbt             # CBT toolkit (thought challenging, anxiety tools)"
echo "  om ai              # AI mental health companion"
echo "  om sleep           # Sleep optimization tools"
echo "  om positive        # Positive psychology practices"
echo "  om nicky           # Nicky Case's mental health guide"
echo ""
echo -e "${CYAN}Crisis Support:${NC}"
echo "  om rescue          # Immediate crisis resources"
echo ""
echo -e "${CYAN}Data Location:${NC}"
echo "  ~/.om/             # All your data (100% private and local)"
echo ""
echo -e "${PURPLE}Privacy Guarantee:${NC}"
echo "• All data stays on your device"
echo "• No external data transmission"
echo "• You control your mental health data"
echo ""
echo -e "${HEART} ${GREEN}Thank you for choosing om for your mental health journey!${NC}"
echo ""
echo -e "${YELLOW}Remember: om supports your wellness but doesn't replace professional help.${NC}"
echo -e "${YELLOW}For crisis support: om rescue or call 988 (National Suicide Prevention Lifeline)${NC}"
echo ""

# Check if global command works
if command -v om &> /dev/null; then
    echo -e "${GREEN}${CHECK} You can now use 'om' from anywhere!${NC}"
    echo "Try: om --help"
else
    echo -e "${YELLOW}${INFO} Use 'python3 main.py' or 'python main.py' to run om${NC}"
    echo "Try: python3 main.py --help"
fi

echo ""
echo -e "${BLUE}Documentation: https://github.com/yourusername/om/docs${NC}"
echo -e "${BLUE}Support: https://github.com/yourusername/om/discussions${NC}"
echo ""
