# Mission Control Dashboard Documentation

## Overview

Mission Control is a consolidated dashboard with a Liquid Glass dark theme that provides a central hub for monitoring and managing tasks through an interactive Kanban board. The dashboard offers a sleek, modern interface with frosted glass effects for a visually appealing and distraction-free experience.

## Core Features

### Liquid Glass UI Design
- Dark theme with frosted glass effect components
- Subtle animations and transitions
- Modern, clean aesthetic with gradient highlights
- Responsive layout for all device sizes

### Kanban Board
- Interactive drag-and-drop task management
- Customizable task properties (priority, assignee, due date)
- Visual priority indicators
- Progress tracking
- Column-based workflow (Backlog, In Progress, Testing, Completed)

### Dashboard Overview
- System status monitoring
- Recent activity feed
- Upcoming deadlines
- Quick access to key metrics
- Task table with sorting and filtering options

## Technical Architecture

The dashboard is built using:
- **Next.js**: React framework for server-side rendering and routing
- **TypeScript**: Type-safe code
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Zustand**: Lightweight state management
- **DND Kit**: Accessible drag-and-drop library

## Getting Started

### Access
- Access the dashboard at: http://localhost:3001/dashboard/kanban
- Check status: `/Users/karst/.openclaw/workspace/check_mission_control.sh`
- Start/restart: `/Users/karst/.openclaw/workspace/start_mission_control.sh`
- Logs location: `/Users/karst/.openclaw/workspace/logs/mission_control.log`

### Task Management
1. **Add Task**: Click the "+" button in any column or use the "Add New Task" button
2. **Edit Task**: Click the menu icon on any task card and select "Edit Task"
3. **Delete Task**: Click the menu icon on any task card and select "Delete Task"
4. **Move Task**: Drag and drop tasks between columns
5. **View Details**: Click on a task to see its full details

## Customization

The dashboard can be customized in several ways:
- Modify the color scheme in `tailwind.config.js`
- Update column titles via the Kanban interface
- Add new task statuses by extending the Kanban store
- Create additional dashboard widgets as needed

## Troubleshooting

If the dashboard is not working:
1. Check logs: `/Users/karst/.openclaw/workspace/logs/mission_control.log`
2. Restart: `/Users/karst/.openclaw/workspace/start_mission_control.sh`
3. Kill hanging processes: `pkill -f "node.*mission-control"`
4. Reinstall dependencies: `cd /Users/karst/.openclaw/workspace/mission-control && npm install`

## Future Enhancements

- Real-time collaboration features
- Task commenting and discussion threads
- File attachment capabilities
- Advanced filtering and sorting
- Timeline view for tasks
- Integration with external services
- Detailed analytics and reporting
- Customizable dashboard widgets