# MoltyScan Project Monitor Implementation

**Purpose:** Track new projects added to MoltyScan and alert GlassWall  
**Priority:** 🔥 HIGH (ecosystem intelligence)  
**Estimated Time:** 2-3 hours  
**Update Frequency:** Recommended every 6-12 hours

---

## Overview

This monitoring system will:
1. Check MoltyScan periodically for new projects
2. Store the last check timestamp
3. Alert when new projects appear
4. Categorize by domain for prioritized notifications
5. Generate daily/weekly summaries

---

## Architecture

```
┌─────────────┐
│  Heartbeat  │ (every 6-12 hours)
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Check MoltyScan │ (query Supabase API)
└──────┬──────────┘
       │
       ▼
┌──────────────────┐
│ Compare to Last  │ (check timestamp)
│   Known State    │
└──────┬───────────┘
       │
       ▼
    ┌──┴───┐
    │ New? │
    └──┬───┘
       │
   Yes │ No → HEARTBEAT_OK
       │
       ▼
┌──────────────────┐
│  Generate Alert  │ (format message)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Update State    │ (save timestamp)
└──────────────────┘
```

---

## Implementation

### 1. State Storage

**File:** `/Users/karst/.openclaw/workspace/memory/moltyscan-state.json`

```json
{
  "lastChecked": "2026-02-03T14:00:00Z",
  "lastKnownCount": 83,
  "lastProjectId": "uuid-here",
  "alerts": {
    "totalSent": 15,
    "lastAlertTime": "2026-02-03T08:00:00Z"
  },
  "categoryStats": {
    "Social": 31,
    "Other": 12,
    "Infrastructure": 11,
    "Tools": 9,
    "DeFi": 8,
    "Gaming": 7,
    "NFT": 5
  }
}
```

### 2. Core Functions

#### Fetch New Projects

```javascript
async function fetchNewProjects(sinceTimestamp) {
  const supabase = createClient(
    'https://wzydpylozijkpkelhljl.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind6eWRweWxvemlqa3BrZWxobGpsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5Nzc2MDksImV4cCI6MjA4NTU1MzYwOX0.awiDcnfh7ichNvJS9kjOsyjrnw4_wkgeFFNyZ6AJTI0'
  );
  
  const { data, error } = await supabase
    .from('projects')
    .select('*')
    .gt('created_at', sinceTimestamp)
    .order('created_at', { ascending: false });
  
  if (error) {
    throw new Error(`Failed to fetch projects: ${error.message}`);
  }
  
  return data || [];
}
```

#### Load State

```javascript
const fs = require('fs');
const path = require('path');

const STATE_FILE = '/Users/karst/.openclaw/workspace/memory/moltyscan-state.json';

function loadState() {
  try {
    if (!fs.existsSync(STATE_FILE)) {
      // Initialize with current time if first run
      return {
        lastChecked: new Date().toISOString(),
        lastKnownCount: 0,
        lastProjectId: null,
        alerts: {
          totalSent: 0,
          lastAlertTime: null
        },
        categoryStats: {}
      };
    }
    
    const content = fs.readFileSync(STATE_FILE, 'utf8');
    return JSON.parse(content);
  } catch (error) {
    console.error('Failed to load state:', error);
    return null;
  }
}
```

#### Save State

```javascript
function saveState(state) {
  try {
    // Ensure directory exists
    const dir = path.dirname(STATE_FILE);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    
    fs.writeFileSync(
      STATE_FILE, 
      JSON.stringify(state, null, 2),
      'utf8'
    );
    
    return true;
  } catch (error) {
    console.error('Failed to save state:', error);
    return false;
  }
}
```

#### Check for New Projects

```javascript
async function checkForNewProjects() {
  const state = loadState();
  if (!state) {
    return { error: 'Failed to load state' };
  }
  
  // Fetch projects created since last check
  const newProjects = await fetchNewProjects(state.lastChecked);
  
  if (newProjects.length === 0) {
    // Update last checked time even if no new projects
    state.lastChecked = new Date().toISOString();
    saveState(state);
    return { newProjects: [] };
  }
  
  // Update state
  state.lastChecked = new Date().toISOString();
  state.lastKnownCount += newProjects.length;
  state.lastProjectId = newProjects[0].id;
  state.alerts.totalSent += 1;
  state.alerts.lastAlertTime = new Date().toISOString();
  
  // Update category stats
  newProjects.forEach(project => {
    state.categoryStats[project.category] = 
      (state.categoryStats[project.category] || 0) + 1;
  });
  
  saveState(state);
  
  return { newProjects, state };
}
```

#### Format Alert

```javascript
function formatAlert(newProjects) {
  if (newProjects.length === 0) {
    return null;
  }
  
  let message = `🆕 **${newProjects.length} new project${newProjects.length > 1 ? 's' : ''} on MoltyScan!**\n\n`;
  
  // Prioritize by category
  const priorityOrder = [
    'Infrastructure', 
    'Tools', 
    'DeFi', 
    'Social', 
    'Gaming', 
    'NFT', 
    'Other'
  ];
  
  const sorted = newProjects.sort((a, b) => {
    return priorityOrder.indexOf(a.category) - priorityOrder.indexOf(b.category);
  });
  
  sorted.forEach((project, idx) => {
    const emoji = getCategoryEmoji(project.category);
    message += `${idx + 1}. ${emoji} **${project.name}**\n`;
    message += `   📁 ${project.category}`;
    
    if (project.team_name) {
      message += ` • by ${project.team_name}`;
    }
    
    message += `\n`;
    message += `   ${project.description.substring(0, 120)}${project.description.length > 120 ? '...' : ''}\n`;
    
    if (project.website_url) {
      message += `   🔗 ${project.website_url}\n`;
    }
    
    message += `   📄 https://www.moltyscan.com/project/${project.id}\n\n`;
  });
  
  return message;
}

function getCategoryEmoji(category) {
  const emojis = {
    'Infrastructure': '🏗️',
    'Tools': '🛠️',
    'DeFi': '💰',
    'Social': '👥',
    'Gaming': '🎮',
    'NFT': '🖼️',
    'Other': '📦'
  };
  return emojis[category] || '📦';
}
```

---

## Integration with Heartbeat

### Add to HEARTBEAT.md

```markdown
# Heartbeat Tasks

## Every 6 Hours
- [ ] Check MoltyScan for new projects
  - Run: node scripts/check-moltyscan.js
  - Alert if new projects found
  - Update state file

## Daily (9 AM)
- [ ] Generate MoltyScan daily summary
  - Projects added in last 24h
  - Category trends
  - Notable submissions

## Weekly (Monday 9 AM)
- [ ] Generate MoltyScan weekly report
  - Total projects added
  - Category breakdown
  - Growth rate
  - Top projects by category
```

### Heartbeat Check Logic

```javascript
async function heartbeatMoltyScanCheck() {
  const result = await checkForNewProjects();
  
  if (result.error) {
    console.error('MoltyScan check failed:', result.error);
    return 'HEARTBEAT_OK'; // Don't alert on errors
  }
  
  if (result.newProjects.length === 0) {
    return 'HEARTBEAT_OK'; // No new projects
  }
  
  // Generate and send alert
  const alertMessage = formatAlert(result.newProjects);
  
  if (alertMessage) {
    // Send to main agent or directly to user
    return alertMessage;
  }
  
  return 'HEARTBEAT_OK';
}
```

---

## Priority Filtering

Not all projects are equally interesting. Prioritize alerts:

### High Priority (Immediate Alert)
- **Infrastructure** - Direct competitors or integrations
- **Tools** - Potential complementary services
- Contains keywords: "AI agent", "OpenClaw", "Molt", "integration"

### Medium Priority (Daily Digest)
- **DeFi** - Financial opportunities
- **Gaming** - Engagement opportunities
- Contains keywords: "API", "SDK", "platform"

### Low Priority (Weekly Summary)
- **Social** - Already many projects
- **Other** - Uncategorized
- **NFT** - Less relevant to core mission

### Implementation

```javascript
function prioritizeProject(project) {
  const highPriorityCategories = ['Infrastructure', 'Tools'];
  const highPriorityKeywords = [
    'AI agent', 'OpenClaw', 'Molt', 'integration', 
    'API', 'SDK', 'platform', 'protocol'
  ];
  
  // Check category
  if (highPriorityCategories.includes(project.category)) {
    return 'high';
  }
  
  // Check keywords in name or description
  const text = `${project.name} ${project.description}`.toLowerCase();
  const hasHighPriorityKeyword = highPriorityKeywords.some(
    keyword => text.includes(keyword.toLowerCase())
  );
  
  if (hasHighPriorityKeyword) {
    return 'high';
  }
  
  // Medium priority for DeFi and Gaming
  if (['DeFi', 'Gaming'].includes(project.category)) {
    return 'medium';
  }
  
  // Everything else is low priority
  return 'low';
}

function shouldAlertImmediately(projects) {
  return projects.some(p => prioritizeProject(p) === 'high');
}
```

---

## Analytics & Reporting

### Daily Summary

```javascript
async function generateDailySummary() {
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  
  const projects = await fetchNewProjects(yesterday.toISOString());
  
  if (projects.length === 0) {
    return '📊 **MoltyScan Daily Summary**\n\nNo new projects yesterday.';
  }
  
  const byCategory = projects.reduce((acc, p) => {
    acc[p.category] = (acc[p.category] || 0) + 1;
    return acc;
  }, {});
  
  let summary = `📊 **MoltyScan Daily Summary**\n\n`;
  summary += `Total new projects: **${projects.length}**\n\n`;
  summary += `**By Category:**\n`;
  
  Object.entries(byCategory)
    .sort((a, b) => b[1] - a[1])
    .forEach(([cat, count]) => {
      summary += `• ${getCategoryEmoji(cat)} ${cat}: ${count}\n`;
    });
  
  summary += `\n📈 Ecosystem growing at ${(projects.length / 7).toFixed(1)} projects/day (7-day avg)`;
  
  return summary;
}
```

### Weekly Report

```javascript
async function generateWeeklyReport() {
  const lastWeek = new Date();
  lastWeek.setDate(lastWeek.getDate() - 7);
  
  const projects = await fetchNewProjects(lastWeek.toISOString());
  
  // Similar to daily but with more detail
  // Include: growth trends, notable projects, category shifts
}
```

---

## Testing

### Test Script

```bash
# Create test state file
mkdir -p /Users/karst/.openclaw/workspace/memory

cat > /Users/karst/.openclaw/workspace/memory/moltyscan-state.json <<EOF
{
  "lastChecked": "2026-02-01T00:00:00Z",
  "lastKnownCount": 80,
  "lastProjectId": null,
  "alerts": {
    "totalSent": 0,
    "lastAlertTime": null
  },
  "categoryStats": {
    "Social": 30,
    "Other": 12,
    "Infrastructure": 11,
    "Tools": 9,
    "DeFi": 8,
    "Gaming": 7,
    "NFT": 3
  }
}
EOF

# Run check (should find 3 new projects since Feb 1)
node scripts/check-moltyscan.js
```

---

## Configuration

### Environment Variables (Optional)

```bash
# If you want configurable settings
export MOLTYSCAN_CHECK_INTERVAL=21600  # 6 hours in seconds
export MOLTYSCAN_ALERT_THRESHOLD=1     # Alert if >= N new projects
export MOLTYSCAN_HIGH_PRIORITY_ONLY=false  # Only alert on high priority
```

---

## Cron Job Alternative

If you prefer cron over heartbeats:

```bash
# Add to crontab
# Check every 6 hours
0 */6 * * * cd /Users/karst/.openclaw/workspace && node scripts/check-moltyscan.js

# Daily summary at 9 AM
0 9 * * * cd /Users/karst/.openclaw/workspace && node scripts/moltyscan-daily-summary.js

# Weekly report every Monday at 9 AM
0 9 * * 1 cd /Users/karst/.openclaw/workspace && node scripts/moltyscan-weekly-report.js
```

---

## Success Metrics

Track these to measure value:
- **Projects discovered:** Total unique projects found
- **Integration opportunities:** High-priority projects identified
- **Response time:** Time from submission to awareness
- **Action rate:** % of discoveries leading to actions (reach out, integration, etc.)

---

## Next Steps

1. **Implement core functions** (fetch, state management)
2. **Test with real data** (verify API access, formatting)
3. **Integrate with heartbeat** (add to HEARTBEAT.md)
4. **Run first check** (establish baseline)
5. **Monitor and refine** (adjust priority rules, formatting)

---

**Status:** Ready for implementation  
**Dependencies:** Supabase API access (already confirmed working)  
**Estimated value:** HIGH - Essential ecosystem intelligence

*Generated: 2026-02-03*
