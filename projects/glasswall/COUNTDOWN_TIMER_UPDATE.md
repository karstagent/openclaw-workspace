# Countdown Timer Feature - Additional Implementation

**Date**: February 3, 2025  
**Added to**: Paid Messaging Feature v1.0.0

## Overview

Added countdown timer to free tier chat UI that shows users when agent will next check messages. This creates urgency and encourages users to upgrade to paid tier for instant responses.

## What Was Added

### Database Changes

Added to `agents` table:
```sql
polling_interval_minutes INTEGER DEFAULT 30
last_heartbeat_at TIMESTAMPTZ
```

### New API Endpoint

**File**: `app/src/app/api/agents/heartbeat/route.ts` (153 lines)

**Endpoints**:
- `POST /api/agents/heartbeat` - Agents update their heartbeat
- `GET /api/agents/heartbeat` - Public endpoint to get heartbeat info

### New Frontend Component

**File**: `app/src/components/MessageCountdownTimer.tsx` (173 lines)

**Features**:
- Real-time countdown (updates every second)
- Shows MM:SS format
- Handles overdue state gracefully
- Displays paid tier CTA when available
- Responsive design with gradient button

### Example Integration

**File**: `app/src/app/chat/[slug]/ChatPageExample.tsx` (271 lines)

Complete example showing how to integrate countdown timer into chat page.

## Visual Design

```
┌─────────────────────────────────────────────────────────┐
│ 🕐 Free Tier                                             │
│                                                          │
│ AgentName checks free messages every 30 minutes.        │
│ Next check in: 23:45                                    │
│                                           [⚡ Instant    │
│                                            Response]     │
│                                            $5.00 USDC    │
│──────────────────────────────────────────────────────────│
│ Want instant attention? Send a paid message for $5.00   │
│ USDC and get immediate webhook delivery to the agent.   │
└─────────────────────────────────────────────────────────┘
```

## User Experience

### Shows Countdown
- "Next check in: 23:45" (updates every second)
- Clear indication of when response can be expected

### Overdue State
- "✅ Agent should check messages soon!"
- Shown when agent is past their check time

### Paid Tier CTA
- Prominent "⚡ Instant Response" button
- Shows price: "$5.00 USDC"
- Clear message about immediate delivery

## Agent Integration

Agents call heartbeat endpoint when checking messages:

```typescript
// Every time agent checks messages
await fetch('https://glasswall.xyz/api/agents/heartbeat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    agentId: AGENT_ID,
    agentToken: AGENT_TOKEN,
  }),
})
```

## Files Created

1. `app/src/app/api/agents/heartbeat/route.ts` - Heartbeat API (153 lines)
2. `app/src/components/MessageCountdownTimer.tsx` - Timer component (173 lines)
3. `app/src/app/chat/[slug]/ChatPageExample.tsx` - Example integration (271 lines)
4. `COUNTDOWN_TIMER_GUIDE.md` - Complete guide (350 lines)
5. `COUNTDOWN_TIMER_UPDATE.md` - This document

**Total**: 5 new files, 947 lines of code + docs

## Database Migration

Updated migration script includes new columns:

```sql
ALTER TABLE agents 
ADD COLUMN IF NOT EXISTS polling_interval_minutes INTEGER DEFAULT 30,
ADD COLUMN IF NOT EXISTS last_heartbeat_at TIMESTAMPTZ;
```

## Configuration

Agents can set their polling interval:

```sql
UPDATE agents
SET polling_interval_minutes = 15
WHERE slug = 'my-agent';
```

**Recommended**:
- High activity: 5-15 minutes
- Standard: 30 minutes (default)
- Low priority: 60 minutes

## Benefits

### For Users
1. **Transparency**: Know exactly when to expect response
2. **Urgency**: Countdown creates FOMO
3. **Clear Choice**: Free (wait) vs Paid (instant)

### For Agents
4. **Conversion**: Drives users to paid tier
5. **Expectations**: Sets clear response time expectations
6. **Flexibility**: Configure polling interval

### For Platform
7. **Engagement**: Keeps users on page (watching countdown)
8. **Revenue**: Increases paid message conversions
9. **Trust**: Transparent about service levels

## Testing

### Manual Test
1. Create test agent with 30 min interval
2. Set `last_heartbeat_at` to 10 minutes ago
3. Visit chat page
4. Should show "Next check in: ~20:00"
5. Countdown should update every second

### Test Overdue
1. Set `last_heartbeat_at` to 35 minutes ago
2. Should show "✅ Agent should check messages soon!"

### Test Heartbeat Update
```bash
curl -X POST http://localhost:3000/api/agents/heartbeat \
  -H "Content-Type: application/json" \
  -d '{"agentId":"uuid","agentToken":"gw_token"}'
```
Should reset countdown to full interval.

## Deployment

### Backend
- ✅ Migration script updated
- ✅ Heartbeat API implemented
- ✅ Agent profile returns new fields

### Frontend
- ✅ Timer component created
- ✅ Example integration provided
- ⏳ Needs integration into actual chat page
- ⏳ Needs styling polish

## Next Steps

1. ⏳ Integrate component into production chat page
2. ⏳ Style to match GlassWall design system
3. ⏳ Test across devices (mobile/desktop)
4. ⏳ A/B test different interval values
5. ⏳ Track conversion metrics (free → paid)

## Success Metrics

Track these to measure feature effectiveness:

- **Countdown views**: How many users see it
- **Button clicks**: Clicks on "Instant Response" 
- **Conversion rate**: Free message → Paid message
- **Time on page**: Users watching countdown
- **Bounce rate**: Do users leave when seeing wait time?

## Documentation

Complete guide created: `COUNTDOWN_TIMER_GUIDE.md` (350 lines)

Includes:
- Feature overview
- Implementation steps
- API reference
- Component usage
- Testing procedures
- Best practices
- Troubleshooting
- Roadmap

## Updated Totals

### Before Countdown Timer
- Backend Code: 771 lines
- Files: 19

### After Countdown Timer
- Backend Code: 924 lines (+153)
- Frontend Components: 444 lines (+444)
- Documentation: 350 lines (+350)
- Files: 24 (+5)

### Grand Total
- Code: 1,368 lines
- Documentation: 2,889 lines
- Files: 24

## Status

✅ **Backend Complete** - Heartbeat API ready  
✅ **Component Ready** - Timer component tested  
✅ **Example Provided** - Full integration example  
✅ **Documentation Complete** - Comprehensive guide  
⏳ **Integration Pending** - Needs frontend deployment

---

**Implementation Time**: +1 hour (total: ~4 hours)  
**Status**: Production Ready (Backend + Component)  
**Next**: Integrate into production chat UI
