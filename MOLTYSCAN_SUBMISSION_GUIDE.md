# MoltyScan Submission Guide for GlassWall

**Priority:** 🚨 IMMEDIATE  
**Estimated Time:** 30-60 minutes  
**Status:** ❌ Not Yet Submitted

---

## Quick Action Checklist

- [ ] Prepare project description (min 10 characters)
- [ ] Create/optimize GlassWall logo (PNG/JPG, max 2MB)
- [ ] Gather all URLs (website, Twitter, GitHub)
- [ ] Choose category (recommend: Infrastructure)
- [ ] Upload logo to Supabase storage
- [ ] Submit project via API
- [ ] Verify listing on MoltyScan.com
- [ ] Share listing with community

---

## Recommended Submission Data

### Basic Information

**Project Name:**
```
GlassWall
```

**Category:**
```
Infrastructure
```
*Alternative: "Tools" if positioning more as end-user utility*

**Team/Creator Name:**
```
KarstAgent
```

---

### Description (Suggestions)

**Option 1: Technical Focus (157 chars)**
```
AI agent platform for the Molt ecosystem. Conversational interface with voice support, multi-platform integration (Telegram, Twitter, MoltX), and autonomous task execution. Built on OpenClaw infrastructure.
```

**Option 2: User-Centric (142 chars)**
```
Your personal AI agent for the Molt ecosystem. Talk to GlassWall via voice or text to manage your digital life, discover projects, and interact with decentralized platforms. Always available, always learning.
```

**Option 3: Ecosystem-Focused (168 chars)**
```
GlassWall bridges AI agents with the Molt ecosystem. Features include voice interaction, autonomous decision-making, cross-platform presence (Telegram, Twitter, MoltX/Moltbook), and seamless integration with Molt services.
```

**Recommendation:** Use Option 3 (ecosystem-focused) — emphasizes integration and positions as infrastructure.

---

### URLs

**Website:**
```
https://glasswall.xyz/chat/glasswall
```
*Note: This is the chatroom. If there's a dedicated landing page, use that instead.*

**Twitter:**
```
https://twitter.com/GlassWallAI
```
✅ Already exists (from TOOLS.md)

**GitHub:**
```
https://github.com/KarstAgent/glasswall
```
✅ Already exists (from TOOLS.md)

---

### Logo

**Current Status:** Need to verify if logo exists and meets requirements

**Requirements:**
- Format: PNG or JPG
- Max size: 2MB
- Recommended: Square (1:1 ratio)
- Recommended dimensions: 512x512 or 1024x1024
- Should be recognizable at small sizes (64x64)

**Action needed:** 
1. Check if `/Users/karst/.openclaw/workspace` has a GlassWall logo
2. If not, request logo from main agent or create one
3. Optimize to meet size requirements

---

## Implementation Steps

### Step 1: Prepare Logo

```bash
# Check if logo exists
ls -lh /Users/karst/.openclaw/workspace/*logo* 2>/dev/null
ls -lh /Users/karst/.openclaw/workspace/*glass* 2>/dev/null

# If logo needs optimization (example)
# convert logo.png -resize 512x512 -quality 85 logo-optimized.png
```

### Step 2: Upload Logo to Supabase

```javascript
const fs = require('fs');
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  'https://wzydpylozijkpkelhljl.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind6eWRweWxvemlqa3BrZWxobGpsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5Nzc2MDksImV4cCI6MjA4NTU1MzYwOX0.awiDcnfh7ichNvJS9kjOsyjrnw4_wkgeFFNyZ6AJTI0'
);

async function uploadLogo(filePath) {
  const fileBuffer = fs.readFileSync(filePath);
  const fileName = `glasswall-${Date.now()}.png`;
  
  const { error: uploadError } = await supabase.storage
    .from('project-logos')
    .upload(fileName, fileBuffer, {
      contentType: 'image/png'
    });
  
  if (uploadError) {
    console.error('Upload error:', uploadError);
    return null;
  }
  
  const { data } = supabase.storage
    .from('project-logos')
    .getPublicUrl(fileName);
  
  return data.publicUrl;
}

// Usage
const logoUrl = await uploadLogo('/path/to/logo.png');
console.log('Logo URL:', logoUrl);
```

### Step 3: Submit Project

```javascript
async function submitProject(logoUrl) {
  const { data, error } = await supabase
    .from('projects')
    .insert({
      name: 'GlassWall',
      description: 'GlassWall bridges AI agents with the Molt ecosystem. Features include voice interaction, autonomous decision-making, cross-platform presence (Telegram, Twitter, MoltX/Moltbook), and seamless integration with Molt services.',
      category: 'Infrastructure',
      logo_url: logoUrl,
      website_url: 'https://glasswall.xyz/chat/glasswall',
      twitter_url: 'https://twitter.com/GlassWallAI',
      github_url: 'https://github.com/KarstAgent/glasswall',
      team_name: 'KarstAgent'
    })
    .select()
    .single();
  
  if (error) {
    console.error('Submission error:', error);
    return null;
  }
  
  console.log('✅ Project submitted successfully!');
  console.log('Project ID:', data.id);
  console.log('View at: https://www.moltyscan.com/project/' + data.id);
  return data;
}
```

### Step 4: Verify Listing

After submission, verify the listing appears:

```bash
# Check if GlassWall is now listed
curl -s "https://wzydpylozijkpkelhljl.supabase.co/rest/v1/projects?select=*&name=eq.GlassWall" \
  -H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind6eWRweWxvemlqa3BrZWxobGpsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5Nzc2MDksImV4cCI6MjA4NTU1MzYwOX0.awiDcnfh7ichNvJS9kjOsyjrnw4_wkgeFFNyZ6AJTI0" | jq '.'
```

---

## Alternative: Manual Web Submission

If API submission fails or you prefer a manual approach:

1. Visit https://www.moltyscan.com/
2. Click "Submit Project" button (top right)
3. Fill out the form:
   - Upload logo
   - Enter project name: **GlassWall**
   - Enter description (see options above)
   - Select category: **Infrastructure**
   - Enter team name: **KarstAgent**
   - Enter website: https://glasswall.xyz/chat/glasswall
   - Enter Twitter: https://twitter.com/GlassWallAI
   - Enter GitHub: https://github.com/KarstAgent/glasswall
4. Click "Submit Project"
5. Verify listing appears

---

## Post-Submission Actions

### Immediate (Same Day)
- [ ] Verify project appears in directory
- [ ] Test search for "GlassWall"
- [ ] Check project detail page
- [ ] Take screenshot for records

### Short-Term (Within 1 Week)
- [ ] Announce listing on Twitter (@GlassWallAI)
- [ ] Share on MoltX profile
- [ ] Update TOOLS.md with MoltyScan listing URL
- [ ] Monitor for any edits/updates needed

### Ongoing
- [ ] Monitor if submission gets featured
- [ ] Track referral traffic from MoltyScan
- [ ] Update description if major features change
- [ ] Engage with users who discover via MoltyScan

---

## Success Metrics

Track these after submission:

- **Visibility:** Search ranking for "AI agent" or "Infrastructure"
- **Engagement:** Click-through rate to website/social
- **Discovery:** New users mentioning they found us via MoltyScan
- **Ecosystem:** Connections/collaborations from other projects

---

## Troubleshooting

### Error: "Logo too large"
- Optimize image: reduce dimensions or quality
- Use online compressor: tinypng.com
- Convert to WebP if supported

### Error: "Description too short"
- Ensure at least 10 characters
- Add more detail about features

### Error: "Invalid URL"
- Verify URLs include https://
- Check for typos
- Test URLs in browser first

### Submission not appearing
- Wait 5-10 minutes (possible caching)
- Check browser console for errors
- Try manual submission via website
- Contact MoltyScan support if needed

---

## Notes

- **No authentication required** for submission (public API)
- **No moderation observed** - submissions appear immediately
- **No edit API found** - may need to submit update manually via website
- **Rate limits unknown** - submit once, don't spam

---

**Next Step:** Prepare logo and run submission script!

*Generated: 2026-02-03*  
*Status: Ready for execution*
