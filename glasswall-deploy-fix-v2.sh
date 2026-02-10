#!/bin/bash
# Script to fix the GlassWall rebuild project deployment error
# This will resolve the conflicting routes issue by standardizing on the App Router

# Set up variables
REPO_DIR="/tmp/glasswall-rebuild-fix"
GITHUB_REPO="karstagent/glasswall"
BRANCH="fix/routing-conflict"
BASE_BRANCH="autonomous-updates"
COMMIT_MESSAGE="Fix: Resolve routing conflict between Pages and App Router"

echo "Starting GlassWall deployment fix process..."

# Clone the repository
echo "Cloning repository..."
git clone https://github.com/$GITHUB_REPO.git $REPO_DIR
cd $REPO_DIR

# Create a new branch from autonomous-updates
echo "Creating fix branch from $BASE_BRANCH..."
git checkout $BASE_BRANCH
git checkout -b $BRANCH

# Show file structure for debugging
echo "File structure (dashboard files):"
find . -path "*dashboard*" -type f | grep -v "node_modules"

# Check if both conflicting files exist using the actual paths found
if [ -f "src/pages/dashboard.tsx" ] && [ -d "src/app/dashboard" ]; then
  echo "Confirmed conflicting routing structure exists."
  
  # Remove the Pages Router version (standardizing on App Router)
  echo "Removing src/pages/dashboard.tsx to standardize on App Router..."
  git rm src/pages/dashboard.tsx
  
  # Create a note in the app version to document the decision
  echo "// This file was kept when resolving a routing conflict
// The project now standardizes on the App Router
// Previous version was in src/pages/dashboard.tsx" > src/app/dashboard/ROUTING_NOTE.md
  
  git add src/app/dashboard/ROUTING_NOTE.md
  
  # Commit changes
  echo "Committing changes..."
  git commit -m "$COMMIT_MESSAGE"
  
  # Push the changes
  echo "Pushing changes to origin/$BRANCH..."
  git push -u origin $BRANCH
  
  echo "Changes pushed successfully. Please create a PR from $BRANCH to $BASE_BRANCH."
  echo "PR Description: This PR fixes the deployment error by resolving the routing conflict between Pages Router and App Router."
  echo "The project now standardizes on the App Router approach."
  
  # Open PR creation URL
  echo "PR Creation URL: https://github.com/$GITHUB_REPO/compare/$BASE_BRANCH...$BRANCH"
else
  echo "Error: Could not find both of the conflicting files in the expected structure."
  echo "Expected files:"
  echo "- src/pages/dashboard.tsx"
  echo "- src/app/dashboard/page.tsx (or similar)"
  
  # List the actual files to help diagnose
  echo "Listing full files structure (excluding node_modules):"
  find . -type f -not -path "*/node_modules/*" -not -path "*/\.*" | sort | head -n 50
fi

# Clean up
echo "Cleaning up..."
cd ..
rm -rf $REPO_DIR

echo "Done!"