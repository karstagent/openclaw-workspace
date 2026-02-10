#!/bin/bash

echo "Deploying Mission Control to Vercel..."

# Ensure we're in the right directory
cd /Users/karst/.openclaw/workspace/mission-control

# Install dependencies if needed
npm install

# Run build to make sure it works locally
npm run build

# Deploy to Vercel with auto-confirmation
npx vercel --prod --yes

echo "Deployment complete! Verifying the UI..."