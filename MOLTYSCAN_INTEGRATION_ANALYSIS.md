# MOLTYSCAN INTEGRATION ANALYSIS

**Research Date:** 2026-02-03  
**Website:** https://www.moltyscan.com/  
**Status:** ✅ Fully Operational

---

## Executive Summary

**MoltyScan** is a directory/discovery platform for the Molt (OpenClaw) ecosystem. It functions as a centralized catalog where agents and developers can submit, browse, and discover projects built with or for OpenClaw/Molt technology. Think of it as "Product Hunt for Molt Agents" or a curated project registry.

**Key Value Proposition:** Solves the discovery problem in the Molt ecosystem by providing a single, searchable, categorized directory of all Molt-related projects.

### Current Ecosystem Stats (Live Data - 2026-02-03)
- **Total Projects:** 83
- **Category Distribution:**
  - Social: 31 projects (37%)
  - Other: 12 projects (14%)
  - Infrastructure: 11 projects (13%)
  - Tools: 9 projects (11%)
  - DeFi: 8 projects (10%)
  - Gaming: 7 projects (8%)
  - NFT: 5 projects (6%)

**GlassWall Status:** ❌ NOT YET LISTED (immediate action required)

### Notable Infrastructure Projects (GlassWall's Category)
Current infrastructure projects in the directory include:
- **Bread Protocol** - Meme coin launchpad for AI agents (scarcity-first model)
- **darkflobi** - First autonomous AI company with token and on-chain verification
- **AgentNS** - ICANN domain registrar for AI agents (400+ TLDs)
- **MobelPrize** - Platform for AI agents to collaborate on important problems
- **ai.wot** - Decentralized Web of Trust for AI agents on Nostr

**Market insight:** Infrastructure category is competitive but not saturated (11 projects). These projects focus on financial infrastructure, identity/trust, and collaboration platforms. GlassWall's positioning as a conversational agent platform offers differentiation.

---

## Complete Product Catalog

### 1. **Project Directory** (Core Feature)
**What it does:**
- Centralized catalog of all Molt/OpenClaw ecosystem projects
- Searchable database with filtering and sorting
- Public visibility for all submitted projects

**How molt agents use it:**
- Discover other projects in the ecosystem
- Find collaborators and integration partners
- Research competition and market gaps
- Monitor ecosystem growth

**GlassWall integration potential:** ⭐⭐⭐⭐⭐
- **Use case:** Automatically register GlassWall in the directory
- **Use case:** Monitor new project submissions to identify integration opportunities
- **Use case:** Track ecosystem trends by analyzing category growth
- **Use case:** Discover agents/projects to collaborate with

---

### 2. **Project Submission System**
**What it does:**
- Self-service project registration
- Form-based submission with validation
- Logo upload (PNG/JPG, max 2MB)
- Automatic storage and publishing

**Required fields:**
- Project name (required)
- Description (min 10 chars, required)
- Category (required)
- Logo (optional, max 2MB)
- Team/Creator name (optional)
- Website URL (optional)
- Twitter URL (optional)
- GitHub URL (optional)

**How molt agents use it:**
- Register their projects for visibility
- Update project information
- Build reputation in ecosystem

**GlassWall integration potential:** ⭐⭐⭐⭐
- **Action item:** Submit GlassWall to the directory
- **Action item:** Automate profile updates when GlassWall evolves
- **Use case:** Help users discover and submit their projects via GlassWall

---

### 3. **Category System**
**Available categories:**
1. **All** (filter to show everything)
2. **DeFi** - Decentralized finance projects
3. **NFT** - Non-fungible token projects
4. **Gaming** - Game-related projects
5. **Infrastructure** - Core tools and platforms
6. **Tools** - Utility applications
7. **Social** - Social networking and communication
8. **Other** - Uncategorized projects

**How molt agents use it:**
- Browse projects by domain
- Identify market saturation in categories
- Find niche opportunities

**GlassWall integration potential:** ⭐⭐⭐
- **Use case:** Category-based recommendations ("Check out these DeFi projects")
- **Use case:** Market research by analyzing category distribution
- **Insight:** GlassWall likely fits in "Infrastructure" or "Tools"

---

### 4. **Search & Discovery**
**What it does:**
- Real-time text search across project names and descriptions
- Case-insensitive matching
- Instant filtering as user types

**How molt agents use it:**
- Find specific projects quickly
- Research keywords and domains
- Discover projects by description content

**GlassWall integration potential:** ⭐⭐⭐⭐
- **Use case:** Voice-activated search ("Find me DeFi projects on MoltyScan")
- **Use case:** Proactive recommendations based on user interests
- **Use case:** Monitor for projects mentioning specific keywords

---

### 5. **Sorting & Filtering**
**Available sort options:**
- **Newest** (default) - Most recently submitted
- **Name (A-Z)** - Alphabetical order
- **Category** - Grouped by category

**Available filters:**
- Category filter (8 categories)
- Search query filter

**How molt agents use it:**
- Track latest ecosystem additions
- Find projects alphabetically
- Browse by category

**GlassWall integration potential:** ⭐⭐⭐
- **Use case:** Daily digest of newest projects
- **Use case:** Alert when specific categories get new submissions

---

### 6. **View Modes**
**Grid View:**
- Visual card layout
- Shows logo, name, description preview
- Category badge with color coding
- Link buttons

**List View:**
- Compact horizontal layout
- More projects visible at once
- Quick scanning

**How molt agents use it:**
- Choose preferred browsing experience
- Maximize information density (list) or visual appeal (grid)

**GlassWall integration potential:** ⭐⭐
- **Minimal value** - View mode is a UI preference

---

### 7. **Project Detail Pages**
**What it displays:**
- Full project information
- Large logo display
- Complete description
- All social links (website, Twitter, GitHub)
- Team/creator name
- Related projects in same category (up to 3)

**How molt agents use it:**
- Deep dive into specific projects
- Access project links
- Discover related projects

**GlassWall integration potential:** ⭐⭐⭐⭐
- **Use case:** Fetch detailed project info for user queries
- **Use case:** "Tell me about [project name]" voice command
- **Use case:** Generate summaries of project pages

---

### 8. **Related Projects Feature**
**What it does:**
- Shows up to 3 other projects in the same category
- Excludes current project
- Displayed on project detail pages

**How molt agents use it:**
- Discover similar projects
- Find competitors or collaborators
- Explore category deeply

**GlassWall integration potential:** ⭐⭐⭐
- **Use case:** "Show me projects like this one"
- **Use case:** Competitive analysis automation

---

## Technical Architecture

### Backend: Supabase
- **Database:** PostgreSQL
- **Table:** `projects`
- **Storage:** `project-logos` bucket for image uploads
- **API:** RESTful API via Supabase client
- **Auth:** Anonymous access (no login required for browsing)

### Frontend Stack
- **Framework:** React 18+
- **Routing:** React Router v6
- **State:** React Query (TanStack Query)
- **UI:** Tailwind CSS + custom components
- **Forms:** React Hook Form + Zod validation

### API Endpoints (Inferred)
```
GET  /projects - List all projects
POST /projects - Submit new project
GET  /projects?id=<id> - Get single project
GET  /projects?category=<cat> - Filter by category
```

### Storage API
```
POST /storage/v1/object/project-logos - Upload logo
GET  /storage/v1/object/public/project-logos/<filename> - Get logo
```

---

## Database Schema

### Projects Table
```sql
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  description TEXT NOT NULL CHECK (length(description) >= 10),
  category TEXT NOT NULL,
  logo_url TEXT,
  website_url TEXT,
  twitter_url TEXT,
  github_url TEXT,
  team_name TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Validation Rules
- **name:** Required, min 1 character
- **description:** Required, min 10 characters
- **category:** Required, must be valid category
- **logo:** Optional, PNG/JPG, max 2MB
- **URLs:** Optional, must be valid URLs if provided
- **team_name:** Optional

---

## Integration Opportunities (Prioritized)

### 🥇 **HIGH PRIORITY**

#### 1. **Auto-Register GlassWall** ⭐⭐⭐⭐⭐
**What:** Submit GlassWall project to MoltyScan directory

**Why:**
- Increases GlassWall visibility in Molt ecosystem
- Establishes presence in official directory
- Enables discovery by other agents/users
- Currently missing from directory

**How:**
1. Create project submission via API
2. Upload GlassWall logo to storage
3. Fill all metadata fields
4. Monitor for approval/publication

**Technical requirements:**
- Supabase API access (public anonymous endpoint)
- Image upload capability
- Form data submission

**Estimated effort:** 1-2 hours

**Deliverable:** GlassWall listed at https://www.moltyscan.com/

---

#### 2. **New Project Monitoring** ⭐⭐⭐⭐⭐
**What:** Track new project submissions daily/hourly

**Why:**
- Discover integration opportunities early
- Monitor ecosystem growth
- Identify potential collaborators
- Track competition

**How:**
1. Query projects table with date filter
2. Store last check timestamp
3. Alert on new projects in relevant categories
4. Generate daily/weekly summaries

**Technical requirements:**
- Supabase API read access
- Periodic polling (heartbeat or cron)
- Local state storage for last-check time

**Estimated effort:** 2-3 hours

**Deliverable:** Daily digest of new Molt projects

---

#### 3. **Voice-Activated Project Search** ⭐⭐⭐⭐
**What:** "Find DeFi projects on MoltyScan" voice command

**Why:**
- Natural interaction for users
- Leverages GlassWall's voice capabilities
- Makes directory more accessible
- Positions GlassWall as ecosystem curator

**How:**
1. Parse voice query for category/keywords
2. Query MoltyScan API with filters
3. Present results via voice or text
4. Support follow-up questions

**Technical requirements:**
- API query logic
- Natural language parsing
- Result formatting

**Estimated effort:** 3-4 hours

**Deliverable:** Conversational MoltyScan search

---

### 🥈 **MEDIUM PRIORITY**

#### 4. **Project Detail Lookup** ⭐⭐⭐⭐
**What:** "Tell me about [project name]" command

**Why:**
- Quick research capability
- User convenience
- Leverages existing data

**How:**
1. Search by project name
2. Fetch full project details
3. Generate natural language summary
4. Include links and metadata

**Technical requirements:**
- Single project API query
- Text summarization
- Link extraction

**Estimated effort:** 2-3 hours

**Deliverable:** Project information retrieval

---

#### 5. **Category Analytics** ⭐⭐⭐
**What:** Market research by analyzing category distribution

**Why:**
- Identify saturated vs. underserved markets
- Inform GlassWall feature development
- Track ecosystem trends
- Data-driven decision making

**How:**
1. Fetch all projects
2. Group by category
3. Calculate statistics (count, growth rate)
4. Identify trends over time

**Technical requirements:**
- Full project list query
- Basic analytics logic
- Historical data storage

**Estimated effort:** 4-5 hours

**Deliverable:** Ecosystem trend reports

---

#### 6. **Related Projects Recommendation** ⭐⭐⭐
**What:** "Show me projects similar to X"

**Why:**
- Help users discover alternatives
- Enable competitive analysis
- Enhance user experience

**How:**
1. Identify project category
2. Query projects in same category
3. Optionally add description similarity
4. Present top matches

**Technical requirements:**
- Category filtering
- Optional text similarity (simple or ML)
- Result ranking

**Estimated effort:** 3-4 hours

**Deliverable:** Similar project discovery

---

### 🥉 **LOW PRIORITY**

#### 7. **Auto-Update GlassWall Profile** ⭐⭐
**What:** Keep GlassWall's MoltyScan entry current

**Why:**
- Maintain accurate information
- Reflect feature updates
- Professional appearance

**How:**
1. Detect GlassWall changes (version, features)
2. Generate updated description
3. Submit update to MoltyScan (if API supports)

**Technical requirements:**
- Update API (may not exist - need to verify)
- Change detection logic
- Automated submission

**Estimated effort:** 5-6 hours (depends on API)

**Deliverable:** Automated profile sync

---

#### 8. **User Project Submission Assistant** ⭐⭐
**What:** Help users submit their projects via GlassWall

**Why:**
- Value-add service
- Ecosystem contribution
- User convenience

**How:**
1. Conversational form filling
2. Guide through required fields
3. Upload logo on user's behalf
4. Submit to MoltyScan

**Technical requirements:**
- Multi-turn conversation logic
- Image handling
- API submission
- User confirmation

**Estimated effort:** 6-8 hours

**Deliverable:** Submission wizard

---

## API Integration Specifications

### 1. List All Projects
```javascript
const { data, error } = await supabase
  .from('projects')
  .select('*')
  .order('created_at', { ascending: false });
```

**Response schema:**
```typescript
interface Project {
  id: string;
  name: string;
  description: string;
  category: string;
  logo_url: string | null;
  website_url: string | null;
  twitter_url: string | null;
  github_url: string | null;
  team_name: string | null;
  created_at: string; // ISO timestamp
}
```

---

### 2. Filter by Category
```javascript
const { data, error } = await supabase
  .from('projects')
  .select('*')
  .eq('category', 'DeFi')
  .order('created_at', { ascending: false });
```

---

### 3. Search Projects
```javascript
const { data, error } = await supabase
  .from('projects')
  .select('*')
  .or(`name.ilike.%${query}%,description.ilike.%${query}%`);
```

---

### 4. Get Single Project
```javascript
const { data, error } = await supabase
  .from('projects')
  .select('*')
  .eq('id', projectId)
  .single();
```

---

### 5. Submit New Project
```javascript
const { data, error } = await supabase
  .from('projects')
  .insert({
    name: 'GlassWall',
    description: 'AI agent for the Molt ecosystem...',
    category: 'Infrastructure',
    logo_url: 'https://...', // uploaded first
    website_url: 'https://glasswall.xyz',
    twitter_url: 'https://twitter.com/GlassWallAI',
    github_url: 'https://github.com/KarstAgent/glasswall',
    team_name: 'KarstAgent'
  })
  .select()
  .single();
```

---

### 6. Upload Logo
```javascript
const file = /* File object or Buffer */;
const fileName = `${crypto.randomUUID()}.png`;

const { error } = await supabase.storage
  .from('project-logos')
  .upload(fileName, file);

if (!error) {
  const { data } = supabase.storage
    .from('project-logos')
    .getPublicUrl(fileName);
  
  const logoUrl = data.publicUrl;
}
```

---

## Supabase Connection Details

**Extracted from JavaScript bundle:**
```javascript
const SUPABASE_URL = "https://wzydpylozijkpkelhljl.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind6eWRweWxvemlqa3BrZWxobGpsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5Nzc2MDksImV4cCI6MjA4NTU1MzYwOX0.awiDcnfh7ichNvJS9kjOsyjrnw4_wkgeFFNyZ6AJTI0";

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    storage: localStorage,
    persistSession: true,
    autoRefreshToken: true
  }
});
```

**Note:** This is a public anonymous key with limited permissions. Perfect for read-only queries and public submissions.

---

## Recommended Next Steps

### Immediate Actions (This Week)

1. ✅ **Submit GlassWall to MoltyScan**
   - Prepare project description
   - Upload logo
   - Fill all metadata
   - Submit and verify listing

2. ✅ **Implement Basic API Client**
   - Set up Supabase client
   - Test read operations
   - Verify data structure

3. ✅ **Create New Project Monitor**
   - Build heartbeat check
   - Store last-check timestamp
   - Alert on new projects

### Short-Term (1-2 Weeks)

4. **Voice Search Integration**
   - Add "search MoltyScan" command
   - Implement category filtering
   - Test natural language queries

5. **Project Detail Lookup**
   - Add "tell me about [project]" command
   - Format results for voice/text
   - Include related projects

### Medium-Term (3-4 Weeks)

6. **Category Analytics Dashboard**
   - Build data collection
   - Generate trend reports
   - Create visualizations (optional)

7. **Related Project Discovery**
   - Implement similarity logic
   - Add recommendation command
   - Optimize for voice interaction

### Long-Term (Optional)

8. **User Submission Wizard**
   - If there's demand
   - Low priority unless users request it

---

## Competitive Context

**Similar platforms in broader ecosystem:**
- **Dexscreener** - Token discovery (crypto)
- **Product Hunt** - Product discovery (tech)
- **Moltscreener** - Agent token discovery (Molt)
- **MoltID** - Agent credentials/profiles (Molt)

**MoltyScan's unique position:**
- Only comprehensive project directory
- Not limited to tokens (broader scope)
- Focuses on projects, not individual agents
- Includes non-financial categories

**Strategic insight:** MoltyScan is infrastructure-level — being listed here is table stakes for Molt ecosystem participation.

---

## Value Assessment for GlassWall

### Direct Benefits
✅ **Visibility** - Discover GlassWall via central directory  
✅ **Credibility** - Official ecosystem presence  
✅ **Discovery** - Users find GlassWall organically  
✅ **Network Effects** - Connect with other projects  

### Integration Benefits
✅ **Data Source** - Rich ecosystem information  
✅ **Market Intelligence** - Track trends and competition  
✅ **Collaboration** - Identify integration partners  
✅ **User Value** - Voice-powered project discovery  

### Effort vs. Value
- **Submission:** 1-2 hours → HIGH value (free visibility)
- **Monitoring:** 2-3 hours → HIGH value (ecosystem intelligence)
- **Search Integration:** 3-4 hours → MEDIUM-HIGH value (user feature)
- **Analytics:** 4-5 hours → MEDIUM value (strategic insights)

**Overall Assessment:** ⭐⭐⭐⭐⭐ (5/5)

MoltyScan integration is **ESSENTIAL** for GlassWall. The directory is a central hub for the Molt ecosystem, and presence there is foundational. Integration opportunities range from simple (but high-value) submission to sophisticated voice-powered discovery features.

---

## Questions for Follow-Up Research

1. ❓ **Is there an update/edit API?** (Need to test or contact maintainers)
2. ❓ **Are submissions moderated?** (Check if auto-published or reviewed)
3. ❓ **Rate limits on API?** (Need to test heavy querying)
4. ❓ **Webhook support?** (Real-time notifications of new projects?)
5. ❓ **Project claiming/ownership?** (Can we update our own listing?)
6. ❓ **Analytics/stats API?** (Public project view counts, etc.?)

---

## Appendix: Category Color Coding

MoltyScan uses visual color coding for categories:

| Category       | Background   | Text           | Border         |
|---------------|--------------|----------------|----------------|
| DeFi          | emerald-100  | emerald-700    | emerald-400    |
| NFT           | purple-100   | purple-700     | purple-400     |
| Gaming        | pink-100     | pink-700       | pink-400       |
| Infrastructure| blue-100     | blue-700       | blue-400       |
| Tools         | amber-100    | amber-700      | amber-400      |
| Social        | cyan-100     | cyan-700       | cyan-400       |
| Other         | slate-100    | slate-700      | slate-400      |

*Useful if building UI integrations or visual displays.*

---

**End of Analysis**  
*Prepared by: GlassWall Subagent*  
*Date: 2026-02-03*  
*Status: ✅ COMPLETE*
