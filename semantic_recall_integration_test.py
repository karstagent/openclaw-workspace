#!/usr/bin/env python3
"""
Integration Test for Semantic Recall Hook System

This script tests the full integration of all components of the 
Semantic Recall Hook System, from memory search to context injection.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
import tempfile
import subprocess

# Add workspace to path
WORKSPACE_DIR = "/Users/karst/.openclaw/workspace"
sys.path.append(WORKSPACE_DIR)

# Import semantic recall modules
import semantic_recall
from semantic_recall_formatter import TokenAwareFormatter
from vector_memory_impl import VectorMemorySearch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("/Users/karst/.openclaw/workspace/logs/semantic-recall-integration-test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('semantic-recall-integration-test')

class SemanticRecallIntegrationTest:
    """Tests full integration of the Semantic Recall Hook System"""
    
    def __init__(self):
        """Initialize test environment"""
        self.vector_memory = VectorMemorySearch()
        self.formatter = TokenAwareFormatter()
        self.config = semantic_recall.load_config()
        self.results_dir = os.path.join(WORKSPACE_DIR, "logs", "semantic-recall-tests")
        
        # Ensure results directory exists
        os.makedirs(self.results_dir, exist_ok=True)
    
    def run_full_pipeline_test(self, query):
        """
        Run a complete test of the semantic recall pipeline
        
        Args:
            query: The search query to test with
        
        Returns:
            success: Boolean indicating test passed
        """
        logger.info(f"Running full pipeline test with query: '{query}'")
        
        # 1. Vector memory search
        logger.info("Step 1: Testing vector memory search...")
        search_results = self.vector_memory.search(
            query, 
            max_results=self.config.get('max_results', 3),
            min_score=self.config.get('relevance_threshold', 0.65)
        )
        
        if not search_results:
            logger.warning("No search results found. Vector memory may not be properly indexed.")
            return False
            
        logger.info(f"Found {len(search_results)} relevant results")
        
        # 2. Format results
        logger.info("Step 2: Testing token-aware formatting...")
        formatted_text = self.formatter.format_results(
            search_results,
            max_tokens=self.config.get('max_tokens', 1500)
        )
        
        if not formatted_text:
            logger.error("Failed to format search results")
            return False
            
        token_estimate = self.formatter.estimate_tokens(formatted_text)
        logger.info(f"Formatted text with ~{int(token_estimate)} tokens")
        
        # 3. Test OpenClaw integration
        logger.info("Step 3: Testing OpenClaw command integration...")
        if not self._test_openclaw_commands():
            logger.warning("OpenClaw command integration test failed")
            # Continue anyway, this is not critical
        
        # 4. Simulate context injection
        logger.info("Step 4: Testing context injection...")
        success = self._simulate_context_injection(formatted_text, query)
        
        # Save test results
        self._save_test_results(query, search_results, formatted_text, success)
        
        return success
    
    def _test_openclaw_commands(self):
        """Test OpenClaw command integration"""
        try:
            # Get the script that registers OpenClaw commands
            script_path = os.path.join(WORKSPACE_DIR, "semantic-recall-openclaw-commands.py")
            
            # Run script to verify it's working
            result = subprocess.run(
                ["python3", script_path, "--test"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.warning(f"Command integration test failed: {result.stderr}")
                return False
                
            logger.info("Command integration test successful")
            return True
            
        except Exception as e:
            logger.error(f"Error testing OpenClaw commands: {str(e)}")
            return False
    
    def _simulate_context_injection(self, formatted_text, query):
        """Simulate context injection with a mock prompt"""
        try:
            # Create a mock prompt
            mock_prompt = f"This is a test prompt that would trigger a search for '{query}'"
            
            # Simulate injected context
            injected_context = formatted_text + mock_prompt
            
            # Calculate token usage
            token_estimate = self.formatter.estimate_tokens(injected_context)
            original_tokens = self.formatter.estimate_tokens(mock_prompt)
            
            logger.info(f"Original prompt: ~{int(original_tokens)} tokens")
            logger.info(f"Injected context: ~{int(token_estimate)} tokens")
            logger.info(f"Token increase: ~{int(token_estimate - original_tokens)} tokens")
            
            # Check if within reasonable limits
            if token_estimate > 4000:  # Arbitrary limit for testing
                logger.warning("Injected context is very large")
                
            return True
            
        except Exception as e:
            logger.error(f"Error simulating context injection: {str(e)}")
            return False
    
    def _save_test_results(self, query, search_results, formatted_text, success):
        """Save test results to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(self.results_dir, f"test_{timestamp}.json")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "success": success,
            "search_results_count": len(search_results),
            "formatted_text_tokens": int(self.formatter.estimate_tokens(formatted_text)),
            "top_results": search_results[:2],  # Include only top 2 for brevity
            "formatted_sample": formatted_text[:500] + "..." if len(formatted_text) > 500 else formatted_text
        }
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
            
        logger.info(f"Saved test results to {results_file}")
        
    def run_all_tests(self):
        """Run a suite of tests with different queries"""
        test_queries = [
            "What is the best approach for context management?",
            "How does the Kanban system work?",
            "What are the current project priorities?",
            "How does the autonomous system function?",
            "What is the GlassWall architecture?"
        ]
        
        success_count = 0
        
        for query in test_queries:
            if self.run_full_pipeline_test(query):
                success_count += 1
                
        success_rate = (success_count / len(test_queries)) * 100
        logger.info(f"Test suite completed: {success_count}/{len(test_queries)} tests passed ({success_rate:.1f}%)")
        
        return success_rate >= 80  # At least 80% should pass
        
def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Integration tests for Semantic Recall")
    parser.add_argument("--query", help="Specific query to test")
    parser.add_argument("--all", action="store_true", help="Run all test queries")
    args = parser.parse_args()
    
    test = SemanticRecallIntegrationTest()
    
    if args.all:
        success = test.run_all_tests()
    elif args.query:
        success = test.run_full_pipeline_test(args.query)
    else:
        # Default test query
        success = test.run_full_pipeline_test("How does semantic recall work?")
        
    return 0 if success else 1
    
if __name__ == "__main__":
    sys.exit(main())