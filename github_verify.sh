#!/bin/bash

# Configure git
git config --global user.email "karstagent@gmail.com"
git config --global user.name "KarstAgent"

# Create a test repo
mkdir -p /tmp/test-repo
cd /tmp/test-repo
git init

# Add a test file
echo "# Test Repository" > README.md
git add README.md
git commit -m "Initial commit"

echo "Git configuration complete and local repository created"
echo "GitHub email: $(git config --global user.email)"
echo "GitHub name: $(git config --global user.name)"