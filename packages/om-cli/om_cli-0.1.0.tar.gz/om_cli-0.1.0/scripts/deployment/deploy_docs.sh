#!/bin/bash

# Deploy om documentation to GitHub Pages
echo "📚 Deploying om documentation to GitHub Pages..."

# Build documentation
echo "🔨 Building documentation..."
cd docs
make clean
make html

# Check if gh-pages branch exists
if git show-ref --verify --quiet refs/heads/gh-pages; then
    echo "📄 Updating gh-pages branch..."
    git checkout gh-pages
else
    echo "🆕 Creating gh-pages branch..."
    git checkout --orphan gh-pages
fi

# Copy built documentation
echo "📋 Copying documentation files..."
cp -r build/html/* .

# Add .nojekyll file for GitHub Pages
touch .nojekyll

# Commit and push
echo "🚀 Deploying to GitHub Pages..."
git add .
git commit -m "Update documentation $(date)"
git push origin gh-pages

# Return to main branch
git checkout main

echo "✅ Documentation deployed!"
echo "📖 Available at: https://yourusername.github.io/om/"
