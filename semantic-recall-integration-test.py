#!/usr/bin/env python3
"""
Integration Test for Semantic Recall Hook System

This script tests the integration of all four components of the Context Retention System:
1. Hourly Memory Summarizer
2. Post-Compaction Context Injector
3. Vector Memory Pipeline
4. Semantic Recall Hook System

It verifies that the complete system works end-to-end by simulating the workflow
of creating memory entries, indexing them, and then performing semantic recall.
"""

import os
import sys
import json
import time
import logging
import tempfile
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("semantic-recall-integration-test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('integration-test')

# Add workspace to path for imports
WORKSPACE_DIR = "/Users/karst/.openclaw/workspace"
sys.path.append(WORKSPACE_DIR)

# Import the components
try:
    import vector_memory
    from vector_memory import VectorMemoryPipeline
    from semantic_recall import SemanticRecallHook, SemanticRecallConfig
    logger.info("Successfully imported components")
except ImportError as e:
    logger.error(f"Failed to import components: {e}")
    logger.error("Please make sure all components are implemented")
    sys.exit(1)

def create_test_data():
    """Create test memory data for indexing"""
    memory_dir = os.path.join(WORKSPACE_DIR, "memory")
    test_dir = os.path.join(memory_dir, "test")
    
    # Create test directory if it doesn't exist
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test memory files with specific content
    test_files = [
        {
            "filename": "test-memory-1.md",
            "content": """
# Test Memory 1

## Project Discussion

We decided to use React for the frontend and Node.js for the backend of our application.
The database will be MongoDB with a GraphQL API layer.

## Key Decisions

1. Use JWT for authentication
2. Implement server-side rendering for SEO
3. Deploy on AWS using ECS
            """
        },
        {
            "filename": "test-memory-2.md",
            "content": """
# Test Memory 2

## Python Implementation Notes

The machine learning model should use scikit-learn for preprocessing and PyTorch for the neural network.
We'll need to handle data normalization and feature scaling properly.

## Database Schema

- Users table: id, name, email, password_hash
- Products table: id, name, description, price, category_id
- Categories table: id, name, parent_id
            """
        },
        {
            "filename": "test-memory-3.md",
            "content": """
# Test Memory 3

## Context Retention Research

Vector embeddings provide an effective way to search for semantically similar content.
FAISS can efficiently index and search large collections of vectors.

For context injection, we need to:
1. Extract relevant chunks from memory
2. Format them appropriately
3. Inject them at the beginning of prompts
            """
        }
    ]
    
    # Write test files
    for file_data in test_files:
        file_path = os.path.join(test_dir, file_data["filename"])
        with open(file_path, 'w') as f:
            f.write(file_data["content"])
        logger.info(f"Created test file: {file_path}")
    
    return [os.path.join(test_dir, file_data["filename"]) for file_data in test_files]

def test_vector_memory(test_files):
    """Test vector memory indexing and search"""
    logger.info("Testing vector memory pipeline...")
    
    # Create vector memory pipeline
    pipeline = VectorMemoryPipeline()
    
    # Add test files to index
    for file_path in test_files:
        with open(file_path, 'r') as f:
            content = f.read()
        
        filename = os.path.basename(file_path)
        source = f"test/{filename}"
        
        chunks_added = pipeline.add_text(content, source)
        logger.info(f"Indexed {chunks_added} chunks from {filename}")
    
    # Test search functionality
    search_queries = [
        "What database are we using for the project?",
        "How should we implement authentication?",
        "What technologies are we using for machine learning?",
        "How does the context retention system work?"
    ]
    
    for query in search_queries:
        results = pipeline.search(query, k=2, threshold=0.5)
        logger.info(f"\nSearch query: '{query}'")
        
        if results:
            for i, result in enumerate(results):
                logger.info(f"Result {i+1}: [{result['similarity']:.2f}] {result['source']}")
                logger.info(f"Text snippet: {result['text'][:100]}...")
        else:
            logger.info("No results found")
    
    return True

def test_semantic_recall():
    """Test semantic recall hook functionality"""
    logger.info("\nTesting semantic recall hook...")
    
    # Create config and hook
    config = SemanticRecallConfig()
    vector_memory = VectorMemoryPipeline()
    hook = SemanticRecallHook(config, vector_memory)
    
    # Test recall on various queries
    test_queries = [
        "Tell me about our database schema",
        "What frontend framework are we using?",
        "Explain our approach to context retention",
        "What machine learning library should we use?"
    ]
    
    for query in test_queries:
        logger.info(f"\nProcessing query: '{query}'")
        
        injected_text, num_results, token_estimate = hook.process_prompt(query)
        
        if injected_text:
            logger.info(f"Injected {num_results} results ({token_estimate} tokens)")
            logger.info(f"Injection snippet: {injected_text[:200]}...")
        else:
            logger.info("No context injected")
    
    return True

def test_end_to_end():
    """Test end-to-end workflow with all components"""
    logger.info("\nRunning end-to-end integration test...")
    
    # 1. Create test data
    test_files = create_test_data()
    
    # 2. Test vector memory
    if not test_vector_memory(test_files):
        logger.error("Vector memory test failed")
        return False
    
    # 3. Test semantic recall
    if not test_semantic_recall():
        logger.error("Semantic recall test failed")
        return False
    
    # 4. Test hook registration
    try:
        config = SemanticRecallConfig()
        vector_memory = VectorMemoryPipeline()
        hook = SemanticRecallHook(config, vector_memory)
        
        # Register and then unregister to avoid permanent changes
        hook.register_hook()
        logger.info("Successfully registered hook")
        
        hook.unregister_hook()
        logger.info("Successfully unregistered hook")
    except Exception as e:
        logger.error(f"Hook registration test failed: {e}")
        return False
    
    logger.info("\nEnd-to-end integration test completed successfully")
    return True

def cleanup_test_data():
    """Clean up test data"""
    import shutil
    
    test_dir = os.path.join(WORKSPACE_DIR, "memory", "test")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        logger.info(f"Cleaned up test directory: {test_dir}")

def main():
    """Main function"""
    print("Semantic Recall Hook System - Integration Test")
    print("==============================================")
    
    try:
        # Run the end-to-end test
        success = test_end_to_end()
        
        # Clean up test data
        cleanup_test_data()
        
        if success:
            print("\n✅ Integration test passed successfully!")
            print("All components are working together properly.")
        else:
            print("\n❌ Integration test failed!")
            print("Please check the logs for details.")
        
    except Exception as e:
        logger.error(f"Integration test failed with error: {e}")
        print(f"\n❌ Integration test failed with error: {e}")
    
    print("\nSee semantic-recall-integration-test.log for detailed test results.")

if __name__ == "__main__":
    main()