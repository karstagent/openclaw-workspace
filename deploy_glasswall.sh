#!/bin/bash
# Automatic deployment script for GlassWall
# This script commits changes and deploys to Vercel

# Configuration
REPO_DIR="/Users/karst/.openclaw/workspace/glasswall-rebuild"
# Tokens should be provided as environment variables
# export GITHUB_TOKEN="your-github-token"
# export VERCEL_TOKEN="your-vercel-token"

# Change to repository directory
cd "$REPO_DIR" || { echo "Failed to change to repository directory"; exit 1; }

# Get timestamp for commit message
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Commit changes
git add .
git commit -m "Automated deployment: $TIMESTAMP"

# Push to GitHub
git push origin autonomous-updates

# Deploy to Vercel
vercel --token "$VERCEL_TOKEN" --prod --confirm

echo "Deployment completed at $(date '+%Y-%m-%d %H:%M:%S')"