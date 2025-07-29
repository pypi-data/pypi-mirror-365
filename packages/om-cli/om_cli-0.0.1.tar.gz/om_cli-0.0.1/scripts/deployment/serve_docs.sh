#!/bin/bash

# Serve om documentation locally
echo "🧘‍♀️ Starting om documentation server..."
echo "📚 Documentation will be available at: http://localhost:8000"
echo "🔄 Building documentation first..."

cd docs
make html

echo "🚀 Starting server..."
cd build/html
python3 -m http.server 8000
