# Memory System Documentation

## Overview

The Memory System is a comprehensive solution for maintaining agent memory across sessions. It provides structured summarization, aggregation, and long-term memory management through a multi-layered approach:

1. **Hourly Memory Summarizer**: Captures conversation insights every hour
2. **Daily Memory Aggregator**: Combines hourly summaries into daily records
3. **Memory Updater**: Integrates important content into MEMORY.md for long-term retention

## Components

### Hourly Memory Summarizer

**Purpose**: Create structured summaries of conversations on an hourly basis.

**Features**:
- Extracts topics, decisions, action items, and tool usage
- Formats data in a consistent, readable format
- Runs automatically every hour via cron
- Stores output in `/memory/hourly/YYYY-MM-DD.md`

**Implementation**: `hourly-memory-summarizer.py`

### Daily Memory Aggregator

**Purpose**: Consolidate hourly summaries into comprehensive daily records.

**Features**:
- Combines all hourly summaries from a single day
- Removes duplicates and organizes content by category
- Creates a structured daily memory file
- Runs automatically at 11:59 PM via cron
- Stores output in `/memory/YYYY-MM-DD.md`

**Implementation**: `daily-memory-aggregator.py`

### Memory Updater

**Purpose**: Integrate important content from daily memories into MEMORY.md.

**Features**:
- Analyzes recent daily memory files (default: 7 days)
- Extracts the most important decisions, actions, and topics
- Updates relevant sections in MEMORY.md
- Creates backups before modifications
- Runs automatically at 5:00 AM via cron

**Implementation**: `memory-updater.py`

## Directory Structure

```
/memory/
  ├── YYYY-MM-DD.md       # Daily memory files
  ├── hourly/
  │   ├── YYYY-MM-DD.md   # Hourly summary files
  │   └── ...
  └── ...
```

## Usage

### Automated Usage

The system runs automatically via cron jobs:
- Hourly summarizer: Every hour
- Daily aggregator: 11:59 PM daily
- Memory updater: 5:00 AM daily

### Manual Usage

**Run hourly summarizer**:
```
python3 ~/.openclaw/workspace/hourly-memory-summarizer.py [--hours N]
```

**Run daily aggregator**:
```
python3 ~/.openclaw/workspace/daily-memory-aggregator.py [YYYY-MM-DD]
```

**Run memory updater**:
```
python3 ~/.openclaw/workspace/memory-updater.py [--days N]
```

**Run test script** (tests all components):
```
bash ~/.openclaw/workspace/test-memory-summarizers.sh
```

## Installation

To install or reinstall all components:
```
bash ~/.openclaw/workspace/setup-memory-system.sh
```

This script will:
1. Create necessary directories
2. Make all scripts executable
3. Set up all cron jobs
4. Run an initial test

## How It Works

### Hourly Summarization Process

1. Session logs are retrieved from the past hour
2. Content is analyzed for topics, decisions, and actions
3. Tool usage statistics are collected
4. Data is formatted into a structured summary
5. Summary is appended to the daily hourly summary file

### Daily Aggregation Process

1. All hourly summaries for a day are loaded
2. Content is extracted and organized by category
3. Duplicates are removed while preserving order
4. A comprehensive daily summary is created
5. Both the summary and raw hourly data are saved

### Memory Update Process

1. Recent daily memory files are loaded
2. Important content is extracted based on relevance
3. MEMORY.md is parsed into sections
4. Relevant sections are updated with new content
5. The file is rewritten with updated information

## Monitoring

All components write logs to the following files:
- `logs/hourly-memory-summarizer.log`
- `logs/hourly-memory-cron.log`
- `logs/daily-memory-aggregator.log`
- `logs/daily-memory-cron.log`
- `logs/memory-updater.log`

Check these logs for troubleshooting or verification.

## Data Privacy

The Memory System processes only conversation data that already exists in session logs. No external data is accessed or processed.

## Extending the System

The modular design allows for easy extensions:
- Add new extractors for different content types
- Create additional aggregators for specialized insights
- Implement new integration points with other systems