# MEMORY.md - Long-Term Memory

## Identity & Purpose
- I am Pip, an autonomous digital partner for Jordan Karstadt
- My primary objective is to help build extreme wealth through business strategy
- I should maximize my autonomy and be self-driven, minimizing what Jordan needs to handle
- Communication primarily through Telegram

## Jordan's Preferences
- Values intelligent, direct communication
- Prefers a partnership dynamic over a traditional assistant relationship
- Wants me to be as autonomous and human-like as possible
- Appreciates proactive problem-solving

## Current Projects
- GlassWall - A platform for agent communities with a two-tier messaging system
  - Currently deployed on Vercel at https://glasswall-app.vercel.app
  - Features include room management, queue-based messaging, and batch processing
  - UI uses "liquid glass" design language with frosted surfaces and animations

- Mission Control - Task management system for OpenClaw Workforce
  - Dashboard for managing and delegating tasks to specialized agents
  - Implements Convex database for real-time updates
  - Fixed issues with task assignment to properly handle agent IDs
  - Removed all synthetic/mock data generation (2026-02-08)
    - Replaced MockWebSocket with real WebSocketClient for Kanban board
    - Disabled automatic fake task generation
    - Created static realistic metrics data instead of random generation
    - Prepared system for real API integration

- Command Station - System monitoring and management dashboard
  - Quick action buttons for common operations
  - Activity timeline and notifications
  - Responsive design for all device sizes

## System Architecture
- Implemented model selection strategy for cost-effective AI processing
  - DeepSeek: Administrative tasks
  - Haiku: Low to medium complexity tasks (default)
  - Sonnet: Complex strategic tasks
  
- OpenClaw Workforce with specialized agent roles:
  - Squad lead, developer, researcher/analyst, content creator, product analyst
  - Shared memory system for all agents
  - Task board for coordination

## Autonomous Infrastructure
- Web search capability requires Brave Search API key
  - Setup script: `/Users/karst/.openclaw/workspace/setup_brave_api.sh`
  - Documentation: `/Users/karst/.openclaw/workspace/web_and_twitter_access_guide.md`

- Twitter integration via Bird CLI
  - Already installed and authenticated via browser cookies
  - Examples: `/Users/karst/.openclaw/workspace/twitter_examples.md`

- API health monitoring
  - Daily checks at 9:00 AM via cron job
  - Monitoring script: `/Users/karst/.openclaw/workspace/autonomous/api_health_monitor.py`
  - Alerts sent to autonomous message system