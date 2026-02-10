#!/usr/bin/env python3
"""
Vector Memory Pipeline - Context Retention System Component 3

This script implements a vector-based memory system using FAISS and sentence-transformers
to enable semantic search of past conversations and decisions.

Features:
- Embeds conversation chunks for semantic similarity search
- Indexes and stores conversation vectors using FAISS
- Provides relevance-based search with customizable thresholds
- Integrates with existing memory files and conversation logs
- Enables efficient retrieval of contextually relevant past information
"""

import os
import re
import sys
import json
import time
import glob
import logging
import argparse
import numpy as np
from datetime import datetime, timedelta
import hashlib
from typing import List, Dict, Any, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("/Users/karst/.openclaw/workspace/logs/vector-memory.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('vector-memory')

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    logger.error("Required dependencies not found. Please install with:")
    logger.error("pip install faiss-cpu sentence-transformers")
    sys.exit(1)

# Constants
WORKSPACE_DIR = "/Users/karst/.openclaw/workspace"
MEMORY_DIR = os.path.join(WORKSPACE_DIR, "memory")
HOURLY_SUMMARIES_DIR = os.path.join(MEMORY_DIR, "hourly-summaries")
SESSION_LOGS_DIR = os.path.join(WORKSPACE_DIR, "logs", "sessions")
VECTOR_DIR = os.path.join(MEMORY_DIR, "vectors")
FAISS_INDEX_PATH = os.path.join(VECTOR_DIR, "memory.index")
VECTOR_METADATA_PATH = os.path.join(VECTOR_DIR, "metadata.json")
MODEL_NAME = "all-MiniLM-L6-v2"  # 384-dimensional embeddings
CHUNK_SIZE = 512  # Characters per chunk
CHUNK_OVERLAP = 128  # Characters overlap between chunks

# Make sure directories exist
os.makedirs(MEMORY_DIR, exist_ok=True)
os.makedirs(VECTOR_DIR, exist_ok=True)
os.makedirs(os.path.join(WORKSPACE_DIR, "logs"), exist_ok=True)

class VectorMemoryPipeline:
    """Implements a vector-based memory system using FAISS"""
    
    def __init__(self, model_name=MODEL_NAME, index_path=FAISS_INDEX_PATH, metadata_path=VECTOR_METADATA_PATH):
        self.model_name = model_name
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.model = None  # Loaded on demand
        self.index = None  # Loaded on demand
        self.metadata = self._load_metadata()
    
    def _load_model(self):
        """Load the sentence transformer model for embeddings"""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
        return self.model
    
    def _load_index(self, create_if_missing=True):
        """Load or create the FAISS index"""
        if self.index is not None:
            return self.index
            
        model = self._load_model()
        embedding_size = model.get_sentence_embedding_dimension()
        
        if os.path.exists(self.index_path):
            logger.info(f"Loading existing FAISS index from {self.index_path}")
            try:
                self.index = faiss.read_index(self.index_path)
                logger.info(f"Index loaded with {self.index.ntotal} vectors")
                return self.index
            except Exception as e:
                logger.error(f"Error loading FAISS index: {e}")
                if not create_if_missing:
                    raise
                logger.info("Creating new index instead")
        
        if create_if_missing:
            logger.info(f"Creating new FAISS index with dimension {embedding_size}")
            self.index = faiss.IndexFlatL2(embedding_size)
            return self.index
        else:
            raise FileNotFoundError(f"FAISS index not found at {self.index_path}")
    
    def _load_metadata(self):
        """Load vector metadata or create if it doesn't exist"""
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading metadata: {e}")
                return self._create_default_metadata()
        else:
            return self._create_default_metadata()
    
    def _save_metadata(self):
        """Save metadata to file"""
        try:
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            logger.debug(f"Metadata saved to {self.metadata_path}")
        except IOError as e:
            logger.error(f"Error saving metadata: {e}")
    
    def _create_default_metadata(self):
        """Create default metadata structure"""
        return {
            "chunks": [],
            "last_update": None,
            "total_chunks": 0,
            "model_name": self.model_name,
            "embedding_dim": 384,  # Default for all-MiniLM-L6-v2
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP
        }
    
    def _save_index(self):
        """Save the FAISS index to disk"""
        if self.index is None:
            logger.error("Cannot save index: No index loaded")
            return
            
        try:
            faiss.write_index(self.index, self.index_path)
            logger.info(f"Index saved to {self.index_path} with {self.index.ntotal} vectors")
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
    
    def _create_chunks(self, text, source, timestamp=None, overlap=CHUNK_OVERLAP):
        """Split text into overlapping chunks for embedding"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
            
        # Create chunk_size chunks with overlap
        chunks = []
        start = 0
        text_len = len(text)
        
        # For very short texts, just use the entire text
        if text_len <= CHUNK_SIZE:
            return [{
                "text": text,
                "start": 0,
                "end": text_len,
                "source": source,
                "timestamp": timestamp
            }]
        
        # For longer texts, create overlapping chunks
        while start < text_len:
            end = min(start + CHUNK_SIZE, text_len)
            
            # Don't create tiny chunks at the end
            if end - start < CHUNK_SIZE / 3 and start > 0:
                break
                
            chunks.append({
                "text": text[start:end],
                "start": start,
                "end": end,
                "source": source,
                "timestamp": timestamp
            })
            
            start += CHUNK_SIZE - overlap
        
        return chunks
    
    def add_text(self, text, source, timestamp=None):
        """Add text to the vector index"""
        if not text or len(text.strip()) == 0:
            logger.warning(f"Skipping empty text from {source}")
            return
        
        # Create chunks from the text
        chunks = self._create_chunks(text, source, timestamp)
        
        # Load model and index
        model = self._load_model()
        index = self._load_index()
        
        # Create embeddings for chunks
        texts = [chunk["text"] for chunk in chunks]
        embeddings = model.encode(texts, convert_to_numpy=True)
        
        # Check if embeddings is a single vector instead of a batch
        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)
        
        # Add embeddings to the index
        index.add(embeddings)
        
        # Update metadata
        start_idx = len(self.metadata["chunks"])
        for i, chunk in enumerate(chunks):
            chunk_id = start_idx + i
            self.metadata["chunks"].append({
                "id": chunk_id,
                "text": chunk["text"],
                "source": chunk["source"],
                "timestamp": chunk["timestamp"],
                "start": chunk["start"],
                "end": chunk["end"]
            })
        
        self.metadata["total_chunks"] = len(self.metadata["chunks"])
        self.metadata["last_update"] = datetime.now().isoformat()
        
        # Save index and metadata
        self._save_index()
        self._save_metadata()
        
        logger.info(f"Added {len(chunks)} chunks from {source} to the index")
        return len(chunks)
    
    def search(self, query, k=5, threshold=0.5):
        """
        Search for the most similar chunks to the query
        
        Args:
            query: The search query
            k: Number of results to return
            threshold: Similarity threshold (0-1, higher is more strict)
            
        Returns:
            List of dictionaries with search results
        """
        # Load model and index
        model = self._load_model()
        
        try:
            index = self._load_index(create_if_missing=False)
        except FileNotFoundError:
            logger.error("No index found for search")
            return []
        
        # Create query embedding
        query_embedding = model.encode(query, convert_to_numpy=True)
        
        # Reshape to a 2D array if needed
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Search the index
        distances, indices = index.search(query_embedding, k)
        
        # Filter results by threshold and gather metadata
        results = []
        max_dist = 2.0  # Approximate max L2 distance for normalization
        
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            # Skip invalid indices
            if idx == -1 or idx >= len(self.metadata["chunks"]):
                continue
            
            # Normalize distance to a similarity score (0-1)
            # FAISS uses L2 distance, so smaller is better
            # We invert and normalize to get a similarity score
            similarity = 1 - (dist / max_dist)
            
            # Apply threshold
            if similarity < threshold:
                continue
            
            # Get metadata for this chunk
            chunk_meta = self.metadata["chunks"][idx]
            
            # Add to results
            results.append({
                "text": chunk_meta["text"],
                "source": chunk_meta["source"],
                "timestamp": chunk_meta["timestamp"],
                "similarity": similarity,
                "chunk_id": idx
            })
        
        return results
    
    def index_memory_files(self, days_back=30):
        """Index all memory files from the last N days"""
        indexed_count = 0
        now = datetime.now()
        cutoff_date = now - timedelta(days=days_back)
        
        # Index daily memory files
        daily_files = glob.glob(os.path.join(MEMORY_DIR, "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md"))
        for file_path in daily_files:
            try:
                # Extract date from filename
                date_str = os.path.basename(file_path).split('.')[0]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                # Skip if older than cutoff
                if file_date < cutoff_date:
                    continue
                
                # Check if file was modified since last update
                mod_time = os.path.getmtime(file_path)
                last_update = self.metadata.get("last_update")
                
                if last_update:
                    last_update_time = datetime.fromisoformat(last_update).timestamp()
                    if mod_time <= last_update_time:
                        logger.debug(f"Skipping unmodified file: {file_path}")
                        continue
                
                # Read file and add to index
                with open(file_path, 'r') as f:
                    content = f.read()
                
                chunks_added = self.add_text(
                    content,
                    f"memory/{os.path.basename(file_path)}",
                    file_date.isoformat()
                )
                indexed_count += chunks_added
            
            except Exception as e:
                logger.error(f"Error indexing file {file_path}: {e}")
        
        # Index hourly summary files
        summary_files = glob.glob(os.path.join(HOURLY_SUMMARIES_DIR, "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9].md"))
        for file_path in summary_files:
            try:
                # Extract date from filename
                filename = os.path.basename(file_path)
                date_str = filename.split('-')[0:3]
                date_str = '-'.join(date_str)
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                # Skip if older than cutoff
                if file_date < cutoff_date:
                    continue
                
                # Check if file was modified since last update
                mod_time = os.path.getmtime(file_path)
                last_update = self.metadata.get("last_update")
                
                if last_update:
                    last_update_time = datetime.fromisoformat(last_update).timestamp()
                    if mod_time <= last_update_time:
                        logger.debug(f"Skipping unmodified file: {file_path}")
                        continue
                
                # Read file and add to index
                with open(file_path, 'r') as f:
                    content = f.read()
                
                chunks_added = self.add_text(
                    content,
                    f"memory/hourly-summaries/{filename}",
                    file_date.isoformat()
                )
                indexed_count += chunks_added
            
            except Exception as e:
                logger.error(f"Error indexing summary file {file_path}: {e}")
        
        logger.info(f"Indexed {indexed_count} chunks from {len(daily_files) + len(summary_files)} memory files")
        return indexed_count
    
    def index_session_logs(self, days_back=7):
        """Index session logs from the last N days"""
        indexed_count = 0
        now = datetime.now()
        cutoff_time = now - timedelta(days=days_back)
        
        # Get session log files
        log_files = glob.glob(os.path.join(SESSION_LOGS_DIR, "*.json"))
        
        for file_path in log_files:
            try:
                # Check file modification time
                mod_time = os.path.getmtime(file_path)
                file_time = datetime.fromtimestamp(mod_time)
                
                # Skip if older than cutoff
                if file_time < cutoff_time:
                    continue
                
                # Check if file was modified since last update
                last_update = self.metadata.get("last_update")
                if last_update:
                    last_update_time = datetime.fromisoformat(last_update).timestamp()
                    if mod_time <= last_update_time:
                        logger.debug(f"Skipping unmodified log: {file_path}")
                        continue
                
                # Read and process session log
                with open(file_path, 'r') as f:
                    log_data = json.load(f)
                
                if not isinstance(log_data, dict) or 'messages' not in log_data:
                    logger.warning(f"Skipping invalid log format: {file_path}")
                    continue
                
                # Process messages
                messages = log_data.get('messages', [])
                for msg in messages:
                    if 'role' in msg and 'content' in msg:
                        # Format: "[Role] Content"
                        formatted_text = f"[{msg['role']}] {msg['content']}"
                        
                        # Get timestamp
                        timestamp = msg.get('timestamp', mod_time)
                        if isinstance(timestamp, (int, float)):
                            timestamp = datetime.fromtimestamp(timestamp).isoformat()
                        
                        # Add to index
                        chunks_added = self.add_text(
                            formatted_text,
                            f"session/{os.path.basename(file_path)}",
                            timestamp
                        )
                        indexed_count += chunks_added
            
            except Exception as e:
                logger.error(f"Error indexing session log {file_path}: {e}")
        
        logger.info(f"Indexed {indexed_count} chunks from session logs")
        return indexed_count
    
    def run_indexing(self, memory_days=30, session_days=7):
        """Run a full indexing job for all sources"""
        start_time = time.time()
        
        # Start by loading the model and index to avoid repetitive loading
        model = self._load_model()
        index = self._load_index()
        
        # Use batch processing for better performance
        batch_size = 0
        max_batch_size = 100  # Maximum chunks to process before saving
        
        # Index memory files with progress tracking
        logger.info(f"Starting memory file indexing (last {memory_days} days)")
        memory_chunks = self.index_memory_files(days_back=memory_days)
        batch_size += memory_chunks
        
        # Save intermediate results if batch size is reached
        if batch_size >= max_batch_size:
            self._save_index()
            self._save_metadata()
            batch_size = 0
            logger.info(f"Saved intermediate indexing results after memory files")
        
        # Index session logs with progress tracking
        logger.info(f"Starting session log indexing (last {session_days} days)")
        session_chunks = self.index_session_logs(days_back=session_days)
        batch_size += session_chunks
        
        # Final save of index and metadata
        self._save_index()
        self._save_metadata()
        
        # Log results
        total_chunks = memory_chunks + session_chunks
        elapsed_time = time.time() - start_time
        
        logger.info(f"Indexing completed: {total_chunks} chunks indexed in {elapsed_time:.2f} seconds")
        logger.info(f"  Memory files: {memory_chunks} chunks")
        logger.info(f"  Session logs: {session_chunks} chunks")
        
        return {
            "memory_chunks": memory_chunks,
            "session_chunks": session_chunks,
            "total_chunks": total_chunks,
            "elapsed_time": elapsed_time
        }
    
    def get_stats(self):
        """Get statistics about the vector memory index"""
        try:
            index = self._load_index(create_if_missing=False)
            index_size = os.path.getsize(self.index_path) if os.path.exists(self.index_path) else 0
            
            # Group chunks by source
            sources = {}
            for chunk in self.metadata["chunks"]:
                source = chunk["source"]
                if source not in sources:
                    sources[source] = 0
                sources[source] += 1
            
            # Format last update time
            last_update = "Never"
            if self.metadata.get("last_update"):
                try:
                    update_time = datetime.fromisoformat(self.metadata["last_update"])
                    last_update = update_time.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    last_update = self.metadata["last_update"]
            
            return {
                "total_vectors": index.ntotal if index else 0,
                "index_size_mb": index_size / (1024 * 1024),
                "sources": sources,
                "total_chunks": self.metadata["total_chunks"],
                "model_name": self.metadata["model_name"],
                "embedding_dim": self.metadata["embedding_dim"],
                "last_update": last_update
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "error": str(e),
                "total_vectors": 0,
                "index_size_mb": 0,
                "sources": {},
                "total_chunks": self.metadata["total_chunks"],
                "model_name": self.metadata["model_name"],
                "last_update": "Error"
            }
    
    def clear_index(self, confirm=False):
        """Clear the entire index and metadata"""
        if not confirm:
            logger.warning("Clear index requires confirmation. Set confirm=True to proceed.")
            return False
        
        # Reset index
        model = self._load_model()
        embedding_size = model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(embedding_size)
        
        # Reset metadata
        self.metadata = self._create_default_metadata()
        self.metadata["embedding_dim"] = embedding_size
        
        # Save changes
        self._save_index()
        self._save_metadata()
        
        logger.info("Index and metadata cleared successfully")
        return True

def setup_cron_job():
    """Set up daily cron job for the vector memory indexer"""
    import subprocess
    
    script_path = os.path.abspath(__file__)
    cron_command = f"0 2 * * * /usr/bin/python3 {script_path} --index"
    
    try:
        # Check if cron job already exists
        cron_check = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_crontab = cron_check.stdout if cron_check.returncode == 0 else ""
        
        if script_path in current_crontab:
            logger.info("Cron job already exists")
            return
        
        # Add new cron job
        new_crontab = current_crontab + cron_command + "\n"
        subprocess.run(['crontab', '-'], input=new_crontab, text=True)
        logger.info(f"Created daily cron job at 2 AM: {cron_command}")
    except Exception as e:
        logger.error(f"Failed to set up cron job: {e}")

def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(description="Vector Memory Pipeline")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--index", action="store_true", help="Run indexing job")
    group.add_argument("--search", type=str, help="Search for a query")
    group.add_argument("--stats", action="store_true", help="Show index statistics")
    group.add_argument("--add", type=str, help="Add text from file to index")
    group.add_argument("--setup-cron", action="store_true", help="Set up daily cron job")
    group.add_argument("--clear", action="store_true", help="Clear the entire index")
    
    parser.add_argument("--memory-days", type=int, default=30, help="Days of memory files to index")
    parser.add_argument("--session-days", type=int, default=7, help="Days of session logs to index")
    parser.add_argument("--results", type=int, default=5, help="Number of search results")
    parser.add_argument("--threshold", type=float, default=0.5, help="Search similarity threshold (0-1)")
    parser.add_argument("--confirm", action="store_true", help="Confirm destructive operations")
    
    args = parser.parse_args()
    
    pipeline = VectorMemoryPipeline()
    
    if args.index:
        results = pipeline.run_indexing(
            memory_days=args.memory_days,
            session_days=args.session_days
        )
        print(f"Indexed {results['total_chunks']} chunks in {results['elapsed_time']:.2f} seconds")
        print(f"  Memory files: {results['memory_chunks']} chunks")
        print(f"  Session logs: {results['session_chunks']} chunks")
    
    elif args.search:
        results = pipeline.search(
            args.search,
            k=args.results,
            threshold=args.threshold
        )
        
        print(f"\nSearch results for: '{args.search}'\n")
        if not results:
            print("No results found")
        else:
            for i, result in enumerate(results):
                print(f"{i+1}. [{result['similarity']:.2f}] {result['source']}")
                print(f"   {result['text'][:100]}...")
                print()
    
    elif args.stats:
        stats = pipeline.get_stats()
        print("\nVector Memory Index Statistics:\n")
        print(f"Total vectors: {stats['total_vectors']}")
        print(f"Index size: {stats['index_size_mb']:.2f} MB")
        print(f"Model: {stats['model_name']} ({stats['embedding_dim']} dimensions)")
        print(f"Last update: {stats['last_update']}")
        print("\nSources:")
        for source, count in sorted(stats['sources'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {source}: {count} chunks")
    
    elif args.add:
        if not os.path.exists(args.add):
            print(f"Error: File not found: {args.add}")
            return
            
        with open(args.add, 'r') as f:
            content = f.read()
            
        chunks_added = pipeline.add_text(
            content,
            f"file:{os.path.basename(args.add)}",
            datetime.now().isoformat()
        )
        print(f"Added {chunks_added} chunks from {args.add} to the index")
    
    elif args.setup_cron:
        setup_cron_job()
    
    elif args.clear:
        if not args.confirm:
            print("Warning: This will delete all indexed data.")
            print("Run with --confirm to proceed.")
            return
            
        success = pipeline.clear_index(confirm=True)
        if success:
            print("Index cleared successfully")
        else:
            print("Failed to clear index")

if __name__ == "__main__":
    main()