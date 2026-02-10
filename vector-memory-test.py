#!/usr/bin/env python3
"""
Test Suite for Vector Memory Pipeline

This script contains comprehensive tests for the Vector Memory Pipeline
to ensure the system functions correctly across different usage scenarios.
"""

import os
import sys
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import numpy as np

# Add workspace to path to import vector_memory
WORKSPACE_DIR = "/Users/karst/.openclaw/workspace"
sys.path.append(WORKSPACE_DIR)

# Import the module we're testing
import vector_memory
from vector_memory import VectorMemoryPipeline

class TestVectorMemoryPipeline(unittest.TestCase):
    """Test class for Vector Memory Pipeline"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directories and files for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = self.temp_dir.name
        
        # Create test directories
        self.vector_dir = os.path.join(self.temp_path, "vectors")
        self.memory_dir = os.path.join(self.temp_path, "memory")
        self.hourly_dir = os.path.join(self.memory_dir, "hourly-summaries")
        self.logs_dir = os.path.join(self.temp_path, "logs")
        
        os.makedirs(self.vector_dir, exist_ok=True)
        os.makedirs(self.memory_dir, exist_ok=True)
        os.makedirs(self.hourly_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Set up test paths
        self.index_path = os.path.join(self.vector_dir, "test.index")
        self.metadata_path = os.path.join(self.vector_dir, "test-metadata.json")
        
        # Set up a mock model for testing
        self.mock_model = MagicMock()
        self.mock_model.get_sentence_embedding_dimension.return_value = 384
        self.mock_model.encode.return_value = np.random.rand(1, 384)
        
        # Create test memory files
        self.create_test_files()
    
    def tearDown(self):
        """Clean up test environment"""
        self.temp_dir.cleanup()
    
    def create_test_files(self):
        """Create test memory files and session logs"""
        # Create a daily memory file
        with open(os.path.join(self.memory_dir, "2026-02-09.md"), "w") as f:
            f.write("# Daily Memory for 2026-02-09\n\n"
                    "## Decisions\n"
                    "- Decision 1: Choose FAISS for vector search\n"
                    "- Decision 2: Use 384-dimensional embeddings\n\n"
                    "## Action Items\n"
                    "- Implement chunking algorithm\n"
                    "- Create search functionality\n")
        
        # Create an hourly summary file
        with open(os.path.join(self.hourly_dir, "2026-02-09-1400.md"), "w") as f:
            f.write("# Hourly Summary: 14:00\n\n"
                    "## Topics\n"
                    "- Vector search implementation\n"
                    "- Embedding models\n\n"
                    "## Key Points\n"
                    "- FAISS provides efficient similarity search\n"
                    "- Sentence-Transformers offers good semantic embeddings\n")
        
        # Create a mock session log
        session_log = {
            "messages": [
                {
                    "role": "user", 
                    "content": "How can we implement vector search?",
                    "timestamp": "2026-02-09T14:30:00"
                },
                {
                    "role": "assistant",
                    "content": "We can use FAISS with Sentence-Transformers for efficient vector search.",
                    "timestamp": "2026-02-09T14:31:00"
                }
            ]
        }
        
        with open(os.path.join(self.logs_dir, "test-session.json"), "w") as f:
            json.dump(session_log, f, indent=2)
    
    @patch('vector_memory.SentenceTransformer')
    @patch('vector_memory.faiss')
    def test_initialization(self, mock_faiss, mock_st):
        """Test pipeline initialization"""
        # Set up mocks
        mock_st.return_value = self.mock_model
        mock_index = MagicMock()
        mock_faiss.IndexFlatL2.return_value = mock_index
        mock_faiss.read_index.side_effect = FileNotFoundError
        
        # Initialize pipeline
        pipeline = VectorMemoryPipeline(
            model_name="test-model",
            index_path=self.index_path,
            metadata_path=self.metadata_path
        )
        
        # Verify metadata was created
        self.assertIsInstance(pipeline.metadata, dict)
        self.assertEqual(pipeline.metadata["model_name"], "test-model")
        self.assertEqual(pipeline.metadata["embedding_dim"], 384)
        
        # Load model and verify it's created correctly
        model = pipeline._load_model()
        mock_st.assert_called_once_with("test-model")
        self.assertEqual(model, self.mock_model)
        
        # Load index and verify it's created
        index = pipeline._load_index()
        mock_faiss.IndexFlatL2.assert_called_once_with(384)
        self.assertEqual(index, mock_index)
    
    @patch('vector_memory.SentenceTransformer')
    @patch('vector_memory.faiss')
    def test_add_text(self, mock_faiss, mock_st):
        """Test adding text to the index"""
        # Set up mocks
        mock_st.return_value = self.mock_model
        mock_index = MagicMock()
        mock_index.ntotal = 0
        mock_faiss.IndexFlatL2.return_value = mock_index
        mock_faiss.read_index.side_effect = FileNotFoundError
        
        # Initialize pipeline
        pipeline = VectorMemoryPipeline(
            model_name="test-model",
            index_path=self.index_path,
            metadata_path=self.metadata_path
        )
        
        # Add text
        result = pipeline.add_text(
            text="This is a test document for vector search",
            source="test-source",
            timestamp="2026-02-09T15:00:00"
        )
        
        # Verify text was chunked and added
        self.assertEqual(result, 1)  # One chunk added
        self.mock_model.encode.assert_called_once()
        mock_index.add.assert_called_once()
        mock_faiss.write_index.assert_called_once_with(mock_index, self.index_path)
        
        # Verify metadata was updated
        self.assertEqual(len(pipeline.metadata["chunks"]), 1)
        self.assertEqual(pipeline.metadata["chunks"][0]["source"], "test-source")
        self.assertEqual(pipeline.metadata["chunks"][0]["text"], "This is a test document for vector search")
    
    @patch('vector_memory.SentenceTransformer')
    @patch('vector_memory.faiss')
    def test_search(self, mock_faiss, mock_st):
        """Test searching the index"""
        # Set up mocks
        mock_st.return_value = self.mock_model
        mock_index = MagicMock()
        mock_index.ntotal = 3
        
        # Mock search results
        mock_index.search.return_value = (
            np.array([[0.1, 0.3, 0.8]]),  # Distances
            np.array([[0, 1, 2]])          # Indices
        )
        
        mock_faiss.IndexFlatL2.return_value = mock_index
        
        # Initialize pipeline
        pipeline = VectorMemoryPipeline(
            model_name="test-model",
            index_path=self.index_path,
            metadata_path=self.metadata_path
        )
        
        # Add fake chunks to metadata
        pipeline.metadata["chunks"] = [
            {"id": 0, "text": "First chunk", "source": "source1", "timestamp": "2026-02-09T10:00:00"},
            {"id": 1, "text": "Second chunk", "source": "source2", "timestamp": "2026-02-09T11:00:00"},
            {"id": 2, "text": "Third chunk", "source": "source3", "timestamp": "2026-02-09T12:00:00"},
        ]
        
        # Search
        results = pipeline.search("test query", k=3, threshold=0.4)
        
        # Verify search was performed
        self.mock_model.encode.assert_called_once()
        mock_index.search.assert_called_once()
        
        # Verify results
        self.assertEqual(len(results), 2)  # Only 2 results should be above threshold
        self.assertEqual(results[0]["text"], "First chunk")
        self.assertEqual(results[1]["text"], "Second chunk")
        
        # Check similarity scores (inverted from distance)
        self.assertGreater(results[0]["similarity"], 0.9)  # 1 - (0.1/2.0)
        self.assertGreater(results[1]["similarity"], 0.8)  # 1 - (0.3/2.0)
    
    @patch('vector_memory.SentenceTransformer')
    @patch('vector_memory.faiss')
    def test_chunking(self, mock_faiss, mock_st):
        """Test text chunking"""
        # Set up mocks
        mock_st.return_value = self.mock_model
        mock_index = MagicMock()
        mock_faiss.IndexFlatL2.return_value = mock_index
        
        # Initialize pipeline
        pipeline = VectorMemoryPipeline(
            model_name="test-model",
            index_path=self.index_path,
            metadata_path=self.metadata_path
        )
        
        # Test with short text (should be one chunk)
        chunks = pipeline._create_chunks(
            "Short text that fits in one chunk",
            "test-source"
        )
        self.assertEqual(len(chunks), 1)
        
        # Test with long text (should be multiple chunks)
        long_text = "A" * 2000  # 2000 characters
        chunks = pipeline._create_chunks(
            long_text,
            "test-source",
            overlap=100
        )
        
        # Should be 4-5 chunks with given size and overlap
        self.assertGreater(len(chunks), 3)
        
        # Check overlap
        for i in range(len(chunks) - 1):
            chunk1_end = chunks[i]["end"]
            chunk2_start = chunks[i+1]["start"]
            self.assertLess(chunk2_start, chunk1_end)  # There should be overlap
    
    @patch('vector_memory.SentenceTransformer')
    @patch('vector_memory.faiss')
    def test_index_memory_files(self, mock_faiss, mock_st):
        """Test indexing memory files"""
        # Set up mocks
        mock_st.return_value = self.mock_model
        mock_index = MagicMock()
        mock_faiss.IndexFlatL2.return_value = mock_index
        
        # Override glob to use our test directory
        with patch('vector_memory.glob.glob') as mock_glob:
            # Return our test files for glob calls
            mock_glob.side_effect = lambda pattern: {
                os.path.join(self.memory_dir, "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md"): 
                    [os.path.join(self.memory_dir, "2026-02-09.md")],
                os.path.join(self.hourly_dir, "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9].md"):
                    [os.path.join(self.hourly_dir, "2026-02-09-1400.md")]
            }[pattern]
            
            # Initialize pipeline with test directories
            pipeline = VectorMemoryPipeline(
                model_name="test-model",
                index_path=self.index_path,
                metadata_path=self.metadata_path
            )
            
            # Create a method to bypass file checks and directly add text
            def mock_add_text(self, text, source, timestamp):
                self.metadata["chunks"].append({
                    "id": len(self.metadata["chunks"]),
                    "text": text[:100],  # Truncate for test
                    "source": source,
                    "timestamp": timestamp
                })
                return 1
                
            # Patch the add_text method
            with patch.object(VectorMemoryPipeline, 'add_text', mock_add_text):
                # Index memory files
                result = pipeline.index_memory_files(days_back=30)
                
                # Should have indexed 2 files
                self.assertEqual(result, 2)
                self.assertEqual(len(pipeline.metadata["chunks"]), 2)

def run_tests():
    """Run all tests"""
    unittest.main()

if __name__ == "__main__":
    run_tests()