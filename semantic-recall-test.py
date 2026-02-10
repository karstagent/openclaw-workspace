#!/usr/bin/env python3
"""
Test suite for the Semantic Recall Hook System

This script provides a comprehensive test suite for validating the 
Semantic Recall Hook System functionality.
"""

import os
import sys
import json
import unittest
from unittest import mock
import tempfile
from datetime import datetime

# Add workspace to path to import semantic_recall
WORKSPACE_DIR = "/Users/karst/.openclaw/workspace"
sys.path.append(WORKSPACE_DIR)

# Import the module we're testing
import semantic_recall
from semantic_recall import SemanticRecallConfig, SemanticRecallHook

class TestSemanticRecallConfig(unittest.TestCase):
    """Test the SemanticRecallConfig class"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary config file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = self.temp_dir.name
        self.config_path = os.path.join(self.temp_path, "test-config.json")
    
    def tearDown(self):
        """Clean up test environment"""
        self.temp_dir.cleanup()
    
    def test_create_default_config(self):
        """Test creating default configuration"""
        config = SemanticRecallConfig(config_path=self.config_path)
        
        # Verify default values
        self.assertEqual(config.get("relevance_threshold"), 0.65)
        self.assertEqual(config.get("max_results"), 3)
        self.assertEqual(config.get("max_tokens"), 1500)
        self.assertTrue(config.get("enabled"))
        self.assertTrue(config.get("log_injections"))
        self.assertEqual(config.get("token_estimation_ratio"), 4.0)
        self.assertTrue(config.get("include_sources"))
        self.assertEqual(config.get("excluded_sessions"), [])
        self.assertEqual(config.get("context_format"), "markdown")
        
        # Verify config was saved to file
        self.assertTrue(os.path.exists(self.config_path))
    
    def test_set_and_get_config(self):
        """Test setting and getting configuration values"""
        config = SemanticRecallConfig(config_path=self.config_path)
        
        # Set a value
        config.set("max_results", 5)
        
        # Verify the value was set
        self.assertEqual(config.get("max_results"), 5)
        
        # Reload the config to verify it was saved
        config2 = SemanticRecallConfig(config_path=self.config_path)
        self.assertEqual(config2.get("max_results"), 5)
    
    def test_enable_disable(self):
        """Test enabling and disabling semantic recall"""
        config = SemanticRecallConfig(config_path=self.config_path)
        
        # Enable
        config.enable()
        self.assertTrue(config.is_enabled())
        
        # Disable
        config.disable()
        self.assertFalse(config.is_enabled())
        
        # Reload the config to verify it was saved
        config2 = SemanticRecallConfig(config_path=self.config_path)
        self.assertFalse(config2.is_enabled())
    
    def test_update_multiple(self):
        """Test updating multiple configuration values"""
        config = SemanticRecallConfig(config_path=self.config_path)
        
        # Update multiple values
        config.update({
            "max_results": 5,
            "relevance_threshold": 0.7,
            "include_sources": False
        })
        
        # Verify values were set
        self.assertEqual(config.get("max_results"), 5)
        self.assertEqual(config.get("relevance_threshold"), 0.7)
        self.assertFalse(config.get("include_sources"))

class TestSemanticRecallHook(unittest.TestCase):
    """Test the SemanticRecallHook class"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary config file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = self.temp_dir.name
        self.config_path = os.path.join(self.temp_path, "test-config.json")
        self.hook_path = os.path.join(self.temp_path, "test-hook.json")
        
        # Create a test config
        self.config = SemanticRecallConfig(config_path=self.config_path)
        
        # Mock vector memory
        self.mock_vector_memory = mock.MagicMock()
    
    def tearDown(self):
        """Clean up test environment"""
        self.temp_dir.cleanup()
    
    @mock.patch('semantic_recall.HOOK_PATH', return_value=None)
    def test_register_unregister_hook(self, mock_hook_path):
        """Test registering and unregistering the hook"""
        # Override hook path
        semantic_recall.HOOK_PATH = self.hook_path
        
        # Create hook
        hook = SemanticRecallHook(config=self.config, vector_memory=self.mock_vector_memory)
        
        # Register hook
        self.assertTrue(hook.register_hook())
        self.assertTrue(os.path.exists(self.hook_path))
        
        # Verify hook data
        with open(self.hook_path, 'r') as f:
            hook_data = json.load(f)
        
        self.assertEqual(hook_data["type"], "pre_prompt")
        self.assertEqual(hook_data["name"], "semantic_recall")
        self.assertTrue(hook_data["enabled"])
        
        # Unregister hook
        self.assertTrue(hook.unregister_hook())
        self.assertFalse(os.path.exists(self.hook_path))
    
    def test_token_estimation(self):
        """Test token estimation"""
        hook = SemanticRecallHook(config=self.config, vector_memory=self.mock_vector_memory)
        
        # Test empty text
        self.assertEqual(hook._estimate_tokens(""), 0)
        
        # Test normal text
        text = "This is a test" * 100  # 1400 characters
        self.assertEqual(hook._estimate_tokens(text), 350)  # 1400 / 4
        
        # Test with custom ratio
        self.config.set("token_estimation_ratio", 2.0)
        self.assertEqual(hook._estimate_tokens(text), 700)  # 1400 / 2
    
    def test_format_recalled_context(self):
        """Test formatting recalled context"""
        hook = SemanticRecallHook(config=self.config, vector_memory=self.mock_vector_memory)
        
        # Test empty results
        self.assertEqual(hook.format_recalled_context([]), "")
        
        # Test markdown format with sources
        results = [
            {
                "source": "test-source-1",
                "timestamp": "2026-02-01T12:00:00",
                "similarity": 0.8,
                "text": "Test content 1"
            },
            {
                "source": "test-source-2",
                "timestamp": "2026-02-02T12:00:00",
                "similarity": 0.7,
                "text": "Test content 2"
            }
        ]
        
        formatted = hook.format_recalled_context(results)
        
        # Verify format
        self.assertIn("# Recent Relevant Context", formatted)
        self.assertIn("### Source 1: test-source-1", formatted)
        self.assertIn("### Source 2: test-source-2", formatted)
        self.assertIn("Test content 1", formatted)
        self.assertIn("Test content 2", formatted)
        self.assertIn("Consider the above context", formatted)
        
        # Test plain text format
        self.config.set("context_format", "plain")
        formatted = hook.format_recalled_context(results)
        
        # Verify format
        self.assertIn("# Recent Relevant Context", formatted)
        self.assertIn("--- Source 1: test-source-1", formatted)
        self.assertIn("--- Source 2: test-source-2", formatted)
        self.assertIn("Test content 1", formatted)
        self.assertIn("Test content 2", formatted)
        
        # Test without sources
        self.config.set("include_sources", False)
        formatted = hook.format_recalled_context(results)
        
        # Verify format
        self.assertIn("--- Source 1", formatted)
        self.assertNotIn("test-source-1", formatted)
    
    @mock.patch('semantic_recall.VectorMemoryPipeline')
    def test_process_prompt(self, mock_vector_memory_class):
        """Test processing a prompt"""
        # Set up mock vector memory
        mock_vm = mock.MagicMock()
        mock_vector_memory_class.return_value = mock_vm
        
        # Set up mock search results
        mock_vm.search.return_value = [
            {
                "source": "test-source-1",
                "timestamp": "2026-02-01T12:00:00",
                "similarity": 0.8,
                "text": "Test content 1"
            },
            {
                "source": "test-source-2",
                "timestamp": "2026-02-02T12:00:00",
                "similarity": 0.7,
                "text": "Test content 2"
            }
        ]
        
        # Set up hook
        hook = SemanticRecallHook()
        
        # Test normal prompt processing
        injected_text, num_results, token_estimate = hook.process_prompt("Test prompt")
        
        # Verify search was called
        mock_vm.search.assert_called_once()
        
        # Verify results
        self.assertGreater(len(injected_text), 0)
        self.assertEqual(num_results, 2)
        self.assertGreater(token_estimate, 0)
        
        # Test disabled
        hook.config.disable()
        injected_text, num_results, token_estimate = hook.process_prompt("Test prompt")
        
        # Verify no results when disabled
        self.assertEqual(injected_text, "")
        self.assertEqual(num_results, 0)
        self.assertEqual(token_estimate, 0)
        
        # Test excluded session
        hook.config.enable()
        hook.config.set("excluded_sessions", ["test-session"])
        injected_text, num_results, token_estimate = hook.process_prompt("Test prompt", session_id="test-session")
        
        # Verify no results for excluded session
        self.assertEqual(injected_text, "")
        self.assertEqual(num_results, 0)
        self.assertEqual(token_estimate, 0)
    
    @mock.patch('semantic_recall.VectorMemoryPipeline')
    def test_token_budget(self, mock_vector_memory_class):
        """Test token budget enforcement"""
        # Set up mock vector memory
        mock_vm = mock.MagicMock()
        mock_vector_memory_class.return_value = mock_vm
        
        # Create long text results
        mock_vm.search.return_value = [
            {
                "source": "test-source-1",
                "timestamp": "2026-02-01T12:00:00",
                "similarity": 0.8,
                "text": "Test content 1" * 1000  # Very long text
            },
            {
                "source": "test-source-2",
                "timestamp": "2026-02-02T12:00:00",
                "similarity": 0.7,
                "text": "Test content 2" * 1000  # Very long text
            }
        ]
        
        # Set up hook with small token budget
        config = SemanticRecallConfig()
        config.set("max_tokens", 100)
        hook = SemanticRecallHook(config=config)
        
        # Process prompt
        injected_text, num_results, token_estimate = hook.process_prompt("Test prompt")
        
        # Verify token budget was enforced
        self.assertLessEqual(token_estimate, 100)

def main():
    """Run the tests"""
    unittest.main()

if __name__ == "__main__":
    main()