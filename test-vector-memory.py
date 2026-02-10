#!/usr/bin/env python3
"""
Test script for Vector Memory Pipeline

This script runs tests for the vector memory pipeline with FAISS
and sentence-transformers to verify functionality.
"""

import os
import sys
import json
import time
import tempfile
import unittest
from datetime import datetime

# Create test directories if they don't exist
TEST_DIR = "/Users/karst/.openclaw/workspace/memory/vectors/test"
os.makedirs(TEST_DIR, exist_ok=True)

# Import the vector memory pipeline
sys.path.append('/Users/karst/.openclaw/workspace')
import importlib.util
spec = importlib.util.spec_from_file_location(
    "vector_memory", 
    "/Users/karst/.openclaw/workspace/vector-memory.py"
)
vector_memory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vector_memory)

class TestVectorMemory(unittest.TestCase):
    """Test cases for the Vector Memory Pipeline"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_index_path = os.path.join(TEST_DIR, "test_memory.index")
        self.test_metadata_path = os.path.join(TEST_DIR, "test_metadata.json")
        
        # Create a test pipeline with separate index and metadata
        self.pipeline = vector_memory.VectorMemoryPipeline(
            model_name="all-MiniLM-L6-v2",
            index_path=self.test_index_path,
            metadata_path=self.test_metadata_path
        )
        
        # Test data
        self.test_data = [
            {
                "text": "The GlassWall project is a platform for agent-human interaction with message batching",
                "source": "test/glasswall.md",
                "timestamp": "2026-02-01T12:00:00"
            },
            {
                "text": "Vector memory uses FAISS and sentence-transformers for semantic search",
                "source": "test/vector-memory.md",
                "timestamp": "2026-02-02T12:00:00"
            },
            {
                "text": "Hourly memory summarization extracts decisions and action items from conversations",
                "source": "test/hourly-memory.md",
                "timestamp": "2026-02-03T12:00:00"
            },
            {
                "text": "Post-compaction context injection maintains continuity after context window resets",
                "source": "test/post-compaction.md",
                "timestamp": "2026-02-04T12:00:00"
            },
            {
                "text": "The Context Retention System has four components for memory management",
                "source": "test/crs.md",
                "timestamp": "2026-02-05T12:00:00"
            }
        ]
    
    def tearDown(self):
        """Clean up test environment"""
        # Remove test files
        if os.path.exists(self.test_index_path):
            os.remove(self.test_index_path)
        
        if os.path.exists(self.test_metadata_path):
            os.remove(self.test_metadata_path)
    
    def test_add_and_search(self):
        """Test adding texts and searching"""
        # Add test data
        for item in self.test_data:
            self.pipeline.add_text(
                text=item["text"],
                source=item["source"],
                timestamp=item["timestamp"]
            )
        
        # Check metadata
        self.assertEqual(len(self.pipeline.metadata["chunks"]), len(self.test_data))
        
        # Test exact search
        results = self.pipeline.search("Vector memory FAISS semantic search")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["source"], "test/vector-memory.md")
        
        # Test conceptual search
        results = self.pipeline.search("How does memory indexing work?")
        self.assertGreater(len(results), 0)
        
        # Test threshold filtering
        results_high_threshold = self.pipeline.search(
            "Context window management", 
            threshold=0.7
        )
        results_low_threshold = self.pipeline.search(
            "Context window management", 
            threshold=0.3
        )
        self.assertLessEqual(len(results_high_threshold), len(results_low_threshold))
    
    def test_chunking(self):
        """Test text chunking functionality"""
        # Create a long text that should be split into chunks
        long_text = "This is a test " * 100  # 1400 characters
        
        chunks = self.pipeline._create_chunks(
            text=long_text,
            source="test/long.txt",
            timestamp="2026-02-06T12:00:00"
        )
        
        # With chunk size 512 and overlap 128, we expect 3-4 chunks
        self.assertGreater(len(chunks), 2)
        
        # Check overlap
        first_chunk_end = chunks[0]["end"]
        second_chunk_start = chunks[1]["start"]
        self.assertLess(second_chunk_start, first_chunk_end)
        self.assertEqual(first_chunk_end - second_chunk_start, vector_memory.CHUNK_OVERLAP)
    
    def test_stats(self):
        """Test statistics reporting"""
        # Add test data
        for item in self.test_data:
            self.pipeline.add_text(
                text=item["text"],
                source=item["source"],
                timestamp=item["timestamp"]
            )
        
        # Get stats
        stats = self.pipeline.get_stats()
        
        # Verify stats content
        self.assertEqual(stats["total_vectors"], len(self.test_data))
        self.assertGreater(stats["index_size_mb"], 0)
        self.assertEqual(stats["total_chunks"], len(self.test_data))
        
        # Check sources
        sources = stats["sources"]
        self.assertEqual(len(sources), len(self.test_data))
        for item in self.test_data:
            self.assertIn(item["source"], sources)
    
    def test_clear_index(self):
        """Test clearing the index"""
        # Add test data
        for item in self.test_data:
            self.pipeline.add_text(
                text=item["text"],
                source=item["source"],
                timestamp=item["timestamp"]
            )
        
        # Verify data is added
        self.assertGreater(len(self.pipeline.metadata["chunks"]), 0)
        
        # Clear index
        self.pipeline.clear_index(confirm=True)
        
        # Verify data is cleared
        self.assertEqual(len(self.pipeline.metadata["chunks"]), 0)
        self.assertEqual(self.pipeline.index.ntotal, 0)

def run_basic_test():
    """Run a basic functionality test"""
    print("=== Vector Memory Pipeline Basic Test ===\n")
    
    # Create a test pipeline
    test_dir = tempfile.mkdtemp()
    test_index_path = os.path.join(test_dir, "test_memory.index")
    test_metadata_path = os.path.join(test_dir, "test_metadata.json")
    
    pipeline = vector_memory.VectorMemoryPipeline(
        model_name="all-MiniLM-L6-v2",
        index_path=test_index_path,
        metadata_path=test_metadata_path
    )
    
    # Test data
    test_data = [
        "The GlassWall project is a platform for agent-human interaction with message batching",
        "Vector memory uses FAISS and sentence-transformers for semantic search",
        "Hourly memory summarization extracts decisions and action items from conversations",
        "Post-compaction context injection maintains continuity after context window resets",
        "The Context Retention System has four components for memory management"
    ]
    
    print("Adding test data...")
    for i, text in enumerate(test_data):
        pipeline.add_text(
            text=text,
            source=f"test/item{i+1}.txt",
            timestamp=datetime.now().isoformat()
        )
    
    print("\nRunning test searches...\n")
    
    queries = [
        "How does vector search work?",
        "What is the GlassWall project?",
        "Memory management systems",
        "Context window problems"
    ]
    
    for query in queries:
        print(f"Query: \"{query}\"")
        results = pipeline.search(query, k=2)
        
        if results:
            for i, result in enumerate(results):
                print(f"  Result {i+1}: [{result['similarity']:.2f}] {result['source']}")
                print(f"    {result['text']}")
        else:
            print("  No results found")
        print()
    
    print("Getting index statistics...")
    stats = pipeline.get_stats()
    print(f"  Total vectors: {stats['total_vectors']}")
    print(f"  Index size: {stats['index_size_mb']:.2f} MB")
    print(f"  Last update: {stats['last_update']}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    run_basic_test()
    
    # Uncomment to run the full unittest suite
    # unittest.main()