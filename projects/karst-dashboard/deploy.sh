#!/bin/bash

# Karst Dashboard Deployment Script
# This script automates the deployment process

set -e

echo "🚀 Karst Dashboard Deployment"
echo "=============================="
echo ""

# Check if we're in the right directory
if [ ! -f "index.html" ]; then
    echo "❌ Error: Must run from karst-dashboard directory"
    exit 1
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: Karst Dashboard"
    echo "✅ Git initialized"
    echo ""
fi

# Check if GitHub repo exists
echo "🔍 Checking GitHub repository..."
if ! git remote get-url origin &> /dev/null; then
    echo "📤 Creating GitHub repository..."
    
    # Ask for repo name
    read -p "Enter GitHub repo name [karst-dashboard]: " REPO_NAME
    REPO_NAME=${REPO_NAME:-karst-dashboard}
    
    # Create repo using gh CLI
    if command -v gh &> /dev/null; then
        gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
        echo "✅ GitHub repository created and pushed"
    else
        echo "⚠️  GitHub CLI (gh) not found. Please install it or create repo manually."
        echo "   Install: brew install gh"
        echo "   Or create at: https://github.com/new"
        exit 1
    fi
else
    echo "✅ GitHub repository already configured"
    echo ""
    
    # Push latest changes
    echo "📤 Pushing latest changes..."
    git add .
    if git diff-index --quiet HEAD --; then
        echo "✅ No changes to commit"
    else
        git commit -m "Update dashboard"
        git push
        echo "✅ Changes pushed to GitHub"
    fi
fi

echo ""

# Deploy to Vercel
echo "🌐 Deploying to Vercel..."

if ! command -v vercel &> /dev/null; then
    echo "⚠️  Vercel CLI not found. Installing..."
    npm i -g vercel
fi

# Ask for deployment type
echo ""
echo "Deployment options:"
echo "1. Preview deployment (test)"
echo "2. Production deployment"
read -p "Choose [1-2]: " DEPLOY_TYPE

if [ "$DEPLOY_TYPE" = "2" ]; then
    echo "🚀 Deploying to production..."
    vercel --prod
else
    echo "🧪 Creating preview deployment..."
    vercel
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Test your dashboard"
echo "2. Change the default password in app.js"
echo "3. Enable Vercel password protection (optional)"
echo "4. Set up custom domain (optional)"
echo ""
