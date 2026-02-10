# Mission Control Vercel Deployment Plan

## Overview
This document outlines the step-by-step plan for deploying the updated Mission Control dashboard to Vercel while ensuring that local development capabilities are preserved.

## Prerequisites
- Vercel CLI installed (`npm i -g vercel`)
- Access to Vercel account credentials
- Updated Mission Control codebase with synthetic data removed

## Deployment Steps

### 1. Authentication Setup ✅
- [x] Run `npx vercel login` to authenticate with Vercel
- [x] Verify authentication success with `npx vercel whoami`
- [x] Set up project linking with `npx vercel link` (if not already linked)

### 2. Configuration Updates (CURRENT STEP)
- [x] Update vercel.json with proper build settings
  - [x] Located existing configuration at `/Users/karst/.openclaw/workspace/mission-control/vercel.json`
  - [x] Add environment variables for WebSocket connections
  - [x] Configure build outputs for proper CSS processing
- [x] Create .env.production with production settings
- [x] Ensure .gitignore excludes local development files

### 3. Code Preparation (CURRENT STEP)
- [x] Verify all synthetic data has been removed from codebase
  - [x] Confirm MockWebSocket replacement with real WebSocketClient
  - [x] Verify automatic fake task generation has been disabled
  - [x] Check that static realistic metrics data is in place
- [x] Implement environment-based configuration for API endpoints
  - [x] Local development: use localhost endpoints
  - [x] Production: use deployed API endpoints

### 4. Build & Deploy (CURRENT STEP)
- [x] Run local build test with `npm run build`
- [x] Fix any build errors or warnings
- [ ] Deploy to Vercel preview with `npx vercel`
- [ ] Test preview deployment thoroughly
- [ ] Deploy to production with `npx vercel --prod`

### 5. Post-Deployment Verification
- [ ] Verify UI styling and Liquid Glass effects work in production
- [ ] Test WebSocket connections with real data
- [ ] Confirm all dashboard components are functioning
- [ ] Document the production URL and update redirect page

### 6. Documentation Updates
- [ ] Update MEMORY.md with deployment details
- [ ] Create user access guide for deployed version
- [ ] Document the process for future deployments

## Timeline
- Authentication Setup: 30 minutes
- Configuration Updates: 45 minutes
- Code Preparation: 1 hour
- Build & Deploy: 30 minutes
- Post-Deployment Verification: 30 minutes
- Documentation Updates: 15 minutes

## Expected Completion
Total estimated time: 3 hours
Target completion: February 9, 2026 at 11:30 AM PST