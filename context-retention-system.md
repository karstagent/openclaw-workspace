# Context Retention System Documentation

The Context Retention System (CRS) is a comprehensive solution for maintaining long-term memory and conversational context in AI assistants. It addresses the limitations of context windows by providing memory persistence, retrieval, and injection capabilities.

## System Components

The CRS consists of four main components:

1. **Hourly Memory Summarizer** - Extracts and preserves key information from conversations
2. **Post-Compaction Context Injector** - Detects context resets and injects relevant memory
3. **Vector Memory Pipeline** - Enables semantic search of past conversations (upcoming)
4. **Semantic Recall Hook System** - Automatically injects relevant context (upcoming)

## 1. Hourly Memory Summarizer

### Purpose
- Regularly captures and preserves conversational context
- Extracts key information (decisions, action items, topics)
- Maintains structured memory files for future reference

### Implementation
- Script: `hourly-memory-summarizer.py`
- Runs every hour via cron job
- Processes conversation logs from the past hour
- Extracts:
  - Main topics
  - Decisions made
  - Action items identified
  - Tool usage patterns
- Generates:
  - Hourly summary files (`memory/hourly-summaries/YYYY-MM-DD-HHMM.md`)
  - Updates daily summary files (`memory/YYYY-MM-DD.md`)

### Usage

1. **Manual run for current hour:**
   ```
   python3 /Users/karst/.openclaw/workspace/hourly-memory-summarizer.py
   ```

2. **Manual run for specific hour:**
   ```
   python3 /Users/karst/.openclaw/workspace/hourly-memory-summarizer.py --hour 14
   ```

3. **Setup automatic cron job:**
   ```
   /Users/karst/.openclaw/workspace/setup-memory-cron.sh
   ```

### Output Example

```markdown
# Hourly Summary: 14:00 - 14:59

Generated: 2026-02-09 14:46:01

ID: summary-20260209-14-eca34b31

## Topics
kanban, github, create, system, team

## Decisions
- to use a JSON file for storing the Kanban data

## Action Items
- Create the basic Kanban structure
- Add priority tracking
- Implement GitHub integration
- Set up automated movement of cards

## Tool Usage
- exec: 5 calls
- read: 3 calls
- write: 1 calls

## Statistics
- Total Messages: 8
- Human Messages: 4
- Assistant Messages: 4
```

## 2. Post-Compaction Context Injector

### Purpose
- Detect context window compaction/resets
- Retrieve relevant memory content
- Inject memory summaries to maintain continuity

### Implementation
- Script: `post-compaction-inject.py`
- Runs as a background service
- Detection strategies:
  - Reset markers in messages
  - Repeated system messages
  - Message sequence analysis
- Retrieves:
  - Recent hourly summaries
  - Daily memory content
  - Recent message history

### Usage

1. **Manual simulation:**
   ```
   python3 /Users/karst/.openclaw/workspace/post-compaction-inject.py --simulate
   ```

2. **Monitor specific session:**
   ```
   python3 /Users/karst/.openclaw/workspace/post-compaction-inject.py --session <session_id>
   ```

3. **Setup as service:**
   ```
   /Users/karst/.openclaw/workspace/setup-compaction-service.sh
   ```

### Injection Example

```markdown
# Context Continuity

*Memory injection at 2026-02-09 14:48:38*

## Recent Activity (2026-02-09 14:00)

### Key Decisions
- to use a JSON file for storing the Kanban data

### Action Items
- Create the basic Kanban structure
- Add priority tracking
- Implement GitHub integration

## Today's Context (2026-02-09)
[Excerpt of today's key discussions...]

## Continuity Note
The conversation context was reset or compacted. 
This summary has been injected to maintain continuity.
```

## 3. Vector Memory Pipeline (Upcoming)

### Purpose
- Enable semantic search of past conversations
- Index and store conversation embeddings
- Provide relevance-based retrieval

### Planned Implementation
- Script: `vector-memory.py`
- Features:
  - Embedding generation with sentence-transformers
  - Vector storage with FAISS
  - Efficient search with cosine similarity
  - Relevance scoring and ranking

## 4. Semantic Recall Hook System (Upcoming)

### Purpose
- Automatically inject relevant context
- Enhance responses with past knowledge
- Maintain coherent long-term conversations

### Planned Implementation
- Script: `semantic-recall.py`
- Features:
  - Query generation from user input
  - Semantic search against vector memory
  - Automatic context injection
  - Relevance threshold filtering

## System Integration

### Memory Flow
1. **Capture:** Hourly summaries extract and preserve key information
2. **Store:** Structured memory files maintain historical context
3. **Index:** Vector memory enables efficient semantic search
4. **Retrieve:** Context injector and semantic hooks access relevant memory
5. **Use:** Memory is injected to maintain conversation continuity

### Directory Structure
```
/Users/karst/.openclaw/workspace/
├── hourly-memory-summarizer.py   # Component 1
├── post-compaction-inject.py     # Component 2
├── vector-memory.py              # Component 3 (upcoming)
├── semantic-recall.py            # Component 4 (upcoming)
├── setup-memory-cron.sh          # Setup script for Component 1
├── setup-compaction-service.sh   # Setup script for Component 2
├── memory/
│   ├── YYYY-MM-DD.md             # Daily memory files
│   ├── hourly-summaries/         # Hourly summary files
│   │   └── YYYY-MM-DD-HHMM.md
│   └── vectors/                  # Vector embeddings (upcoming)
└── logs/
    └── sessions/                 # Session logs
```

## Testing and Verification

Each component includes a test script for validation:

1. `test-memory-summarizer.py` - Tests the Hourly Memory Summarizer
2. `test-compaction-injector.py` - Tests the Post-Compaction Context Injector
3. `test-vector-memory.py` - Will test the Vector Memory Pipeline
4. `test-semantic-recall.py` - Will test the Semantic Recall Hooks

## Maintenance and Monitoring

### Logs
- Memory summarizer: `/Users/karst/.openclaw/workspace/logs/memory-summarizer.log`
- Compaction injector: `/Users/karst/.openclaw/workspace/logs/compaction-injector.log`

### State Files
- Context state: `/Users/karst/.openclaw/workspace/context-state.json`
- Vector index: `/Users/karst/.openclaw/workspace/memory/vectors/index.faiss` (upcoming)

### Cron Jobs
- Memory summarizer: Runs hourly at minute 0
- Vector indexing: Will run daily at midnight

## Benefits

1. **Continuous Memory:** Maintains knowledge across context windows
2. **Contextual Awareness:** Provides relevant historical information
3. **Coherent Conversations:** Enables long-running discussions
4. **Knowledge Persistence:** Preserves important decisions and facts
5. **Adaptive Retrieval:** Only injects information when needed and relevant

## Future Enhancements

1. **Fine-Tuned Embeddings:** Domain-specific embedding models
2. **Hierarchical Memory:** Different tiers for short/medium/long-term memory
3. **Cross-Session Awareness:** Memory sharing between related sessions
4. **Memory Consolidation:** Periodic review and synthesis of key information
5. **Proactive Reminders:** Surfacing relevant past commitments when appropriate