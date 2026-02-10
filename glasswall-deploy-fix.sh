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

# Check if both conflicting files exist
if [ -f "pages/dashboard.tsx" ] && [ -f "app/dashboard/page.tsx" ]; then
  echo "Confirmed both conflicting files exist."
  
  # Remove the Pages Router version (standardizing on App Router)
  echo "Removing pages/dashboard.tsx to standardize on App Router..."
  git rm pages/dashboard.tsx
  
  # Create a note in the app version to document the decision
  echo "// This file was kept when resolving a routing conflict
// The project now standardizes on the App Router
// Previous version was in pages/dashboard.tsx" > app/dashboard/ROUTING_NOTE.md
  
  git add app/dashboard/ROUTING_NOTE.md
  
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
  echo "Error: Could not find one or both of the conflicting files."
  echo "Expected files:"
  echo "- pages/dashboard.tsx"
  echo "- app/dashboard/page.tsx"
  
  # List the actual files to help diagnose
  echo "Listing actual files structure:"
  find . -name "dashboard*" | sort
fi

# Clean up
echo "Cleaning up..."
cd ..
rm -rf $REPO_DIR

echo "Done!"