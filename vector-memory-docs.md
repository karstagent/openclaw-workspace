# Vector Memory Pipeline Documentation

## Overview

The Vector Memory Pipeline is the third component of the Context Retention System. It implements a vector-based memory system using FAISS and sentence-transformers to enable semantic search of past conversations and decisions.

## Key Features

- **Semantic Search**: Find contextually relevant information without exact keyword matches
- **Intelligent Chunking**: Automatically split content into optimal chunks with overlap
- **Memory Indexing**: Efficiently index all memory files and session logs
- **Metadata Tracking**: Comprehensive metadata for each indexed chunk
- **Search Relevance**: Customizable thresholds and result limits
- **Command Integration**: Seamless integration with OpenClaw commands
- **Automated Maintenance**: Daily cron jobs for index updates

## Architecture

The Vector Memory Pipeline consists of three main components:

1. **Core Memory System** (`vector-memory.py`): The main implementation for embedding, indexing, and searching text
2. **OpenClaw Integration** (`vector-memory-integration.py`): Connects the memory system to OpenClaw commands
3. **Test Suite** (`vector-memory-test.py`): Comprehensive tests to ensure system reliability

## Technical Details

### Embedding Model

The system uses the `all-MiniLM-L6-v2` model from Sentence-Transformers, which produces 384-dimensional embeddings that capture the semantic meaning of text. This model offers a good balance between accuracy and performance.

### Chunking Strategy

Text is chunked into segments of 512 characters with 128 characters of overlap between adjacent chunks. This approach ensures that related information that spans chunk boundaries is properly captured in the vector representation.

### Search Algorithm

The system uses FAISS's L2 distance-based search to find the most similar vectors to the query embedding. Distance scores are inverted and normalized to produce similarity scores between 0 and 1, which are then filtered by a customizable threshold.

### Indexing Approach

The system indexes two primary sources of information:

1. **Memory Files**: Daily memory files and hourly summaries from the memory directory
2. **Session Logs**: Chat sessions and conversation history

Files are only re-indexed if they have been modified since the last indexing run, optimizing performance for incremental updates.

## Usage

### OpenClaw Commands

```
# Search vector memory for semantically relevant content
memory_search "What decisions did we make about the context system?"

# Update the vector memory index with recent content
memory_index

# View statistics about the vector memory index
memory_stats
```

### CLI Usage

```bash
# Search for relevant content
python vector-memory.py --search "What decisions did we make about the context system?" --results 5 --threshold 0.5

# Run indexing job
python vector-memory.py --index --memory-days 30 --session-days 7

# Show index statistics
python vector-memory.py --stats

# Add specific file to index
python vector-memory.py --add path/to/file.md

# Set up daily cron job
python vector-memory.py --setup-cron
```

## Integration with Context Retention System

The Vector Memory Pipeline is designed to work seamlessly with the other components of the Context Retention System:

1. **Hourly Memory Summarizer**: Creates concise summaries that are indexed by the Vector Memory Pipeline
2. **Post-Compaction Context Injector**: Can query Vector Memory to retrieve relevant context after compaction
3. **Semantic Recall Hook System**: Will use Vector Memory to find relevant past context for each prompt

## Performance Considerations

- The initial indexing of a large memory corpus can be resource-intensive
- Subsequent incremental updates are very efficient
- Search operations are fast and suitable for real-time use
- Memory usage scales linearly with the number of indexed chunks

## Maintenance

The system includes a daily cron job that runs at 2 AM to update the index with new content. This ensures that recent conversations and memory files are always searchable without manual intervention.

The index can be manually cleared and rebuilt if necessary using the `--clear --confirm` flags.

## Future Enhancements

1. **Improved Chunking**: Semantic chunking based on content boundaries rather than character count
2. **Hybrid Search**: Combine vector search with keyword search for better precision
3. **More Embedding Models**: Support for additional models with different size/accuracy tradeoffs
4. **Memory Pruning**: Automatic removal of outdated or redundant vectors
5. **Multi-Index Support**: Separate indices for different content types