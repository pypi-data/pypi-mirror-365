#!/bin/bash

# Om Mental Health Platform - Enhanced Documentation Builder
# Builds beautiful, modern Sphinx documentation with custom styling
# Author: Alexander Straub (frism)

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🧘‍♀️ Om Documentation Builder${NC}"
echo "================================"

# Check if we're in the right directory
if [ ! -f "om" ] || [ ! -d "docs" ]; then
    echo -e "${RED}❌ Error: Please run this script from the om project root directory${NC}"
    exit 1
fi

# Navigate to docs directory
cd docs

echo -e "${YELLOW}📦 Installing documentation dependencies...${NC}"

# Install/upgrade documentation requirements
pip install -r requirements.txt --upgrade --quiet

echo -e "${YELLOW}🧹 Cleaning previous builds...${NC}"

# Clean previous builds
make clean
rm -rf build/_static 2>/dev/null || true
rm -rf build/_templates 2>/dev/null || true

echo -e "${YELLOW}🎨 Setting up custom styling...${NC}"

# Ensure static directory exists
mkdir -p source/_static
mkdir -p source/_templates

# Copy any additional static files if they exist
if [ -d "../assets" ]; then
    cp -r ../assets/* source/_static/ 2>/dev/null || true
fi

echo -e "${YELLOW}📚 Building HTML documentation...${NC}"

# Build HTML documentation
make html

# Check if build was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Documentation built successfully!${NC}"
else
    echo -e "${RED}❌ Documentation build failed${NC}"
    exit 1
fi

echo -e "${YELLOW}🔍 Running documentation checks...${NC}"

# Check for broken links (if available)
if command -v sphinx-build &> /dev/null; then
    sphinx-build -b linkcheck source build/linkcheck 2>/dev/null || echo "Link check skipped"
fi

# Check for spelling errors (if available)
if command -v sphinx-build &> /dev/null; then
    sphinx-build -b spelling source build/spelling 2>/dev/null || echo "Spell check skipped"
fi

echo -e "${YELLOW}📊 Documentation statistics:${NC}"

# Count documentation files
RST_FILES=$(find source -name "*.rst" | wc -l)
HTML_FILES=$(find build/html -name "*.html" | wc -l)
BUILD_SIZE=$(du -sh build/html | cut -f1)

echo "• RST source files: $RST_FILES"
echo "• Generated HTML files: $HTML_FILES"
echo "• Build size: $BUILD_SIZE"

echo -e "${GREEN}🎉 Documentation build complete!${NC}"
echo ""
echo -e "${BLUE}📖 To view the documentation:${NC}"
echo "• Local: open docs/build/html/index.html"
echo "• Serve: ./scripts/deployment/serve_docs.sh"
echo "• Deploy: ./scripts/deployment/deploy_docs.sh"

# Optional: Open documentation in browser (macOS)
if [[ "$OSTYPE" == "darwin"* ]] && [ "$1" == "--open" ]; then
    echo -e "${YELLOW}🌐 Opening documentation in browser...${NC}"
    open build/html/index.html
fi

# Optional: Start local server
if [ "$1" == "--serve" ]; then
    echo -e "${YELLOW}🌐 Starting local documentation server...${NC}"
    cd build/html
    python -m http.server 8000
fi
