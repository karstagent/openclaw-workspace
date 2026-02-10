#!/usr/bin/env python3
"""
Test Script for Post-Compaction Context Injector

This script provides a comprehensive test suite for validating the
Post-Compaction Context Injector functionality.
"""

import os
import sys
import json
import unittest
from unittest import mock
import subprocess
import tempfile
from datetime import datetime

# Import the post-compaction-inject module
sys.path.append('/Users/karst/.openclaw/workspace')
import post_compaction_inject

class TestContextStateManager(unittest.TestCase):
    """Test the ContextStateManager class"""
    
    def setUp(self):
        # Create a temporary state file
        self.temp_state_file = tempfile.mktemp(suffix='.json')
        self.state_manager = post_compaction_inject.ContextStateManager(state_file=self.temp_state_file)
    
    def tearDown(self):
        # Clean up temporary file
        if os.path.exists(self.temp_state_file):
            os.remove(self.temp_state_file)
    
    def test_register_message(self):
        """Test message registration"""
        # Register a test message
        session_id = "test-session"
        message_id = "test-msg-1"
        content = "This is a test message"
        role = "user"
        
        result = self.state_manager.register_message(session_id, message_id, content, role)
        self.assertTrue(result)
        
        # Verify session was created
        self.assertIn(session_id, self.state_manager.state["sessions"])
        
        # Verify message was stored
        session = self.state_manager.state["sessions"][session_id]
        self.assertEqual(session["last_message_id"], message_id)
        self.assertEqual(session["message_count"], 1)
        self.assertEqual(len(session["messages"]), 1)
        
        # Try registering the same message again (should be rejected as duplicate)
        result = self.state_manager.register_message(session_id, message_id, content, role)
        self.assertFalse(result)
    
    def test_detect_compaction(self):
        """Test compaction detection"""
        session_id = "test-session"
        
        # Register some initial messages
        for i in range(5):
            self.state_manager.register_message(
                session_id=session_id,
                message_id=f"msg_{i}",
                content=f"Test message {i}",
                role="user" if i % 2 == 0 else "assistant"
            )
        
        # Test detection via reset marker
        result = self.state_manager.detect_compaction(
            session_id=session_id,
            message_id="new_msg",
            content="I'll start fresh with a new context",
            role="assistant"
        )
        self.assertTrue(result)
        
        # Test detection via context limit message
        result = self.state_manager.detect_compaction(
            session_id=session_id,
            message_id="limit_msg",
            content="Error: input length and max_tokens exceed context limit: 180000 > 16000",
            role="system"
        )
        self.assertTrue(result)
        
        # Test non-compaction message
        result = self.state_manager.detect_compaction(
            session_id=session_id,
            message_id="normal_msg",
            content="This is a normal message without any compaction indicators",
            role="user"
        )
        self.assertFalse(result)

class TestMemoryRetriever(unittest.TestCase):
    """Test the MemoryRetriever class"""
    
    def setUp(self):
        self.memory_retriever = post_compaction_inject.MemoryRetriever()
    
    @mock.patch('post_compaction_inject.MemoryRetriever.get_task_context')
    @mock.patch('post_compaction_inject.MemoryRetriever.get_main_memory_content')
    @mock.patch('post_compaction_inject.MemoryRetriever.get_daily_memory')
    def test_generate_context_injection(self, mock_daily, mock_memory, mock_task):
        """Test context injection generation"""
        # Mock data
        mock_task.return_value = {
            "title": "Test Task",
            "description": "This is a test task description",
            "progress": 65,
            "priority": "high"
        }
        
        mock_memory.return_value = """# MEMORY.md - Long-Term Memory

## Identity & Purpose
- I am Pip, an autonomous digital partner for Jordan Karstadt

## Current Projects
- GlassWall - A platform for agent communities with a two-tier messaging system
"""
        
        mock_daily.return_value = [
            {
                "date": "2026-02-09",
                "content": "Today's work included progress on the context injector system.",
                "path": "/fake/path/2026-02-09.md"
            }
        ]
        
        # Generate injection
        injection = self.memory_retriever.generate_context_injection(
            session_id="test-session",
            detected_compaction=True,
            max_tokens=2000
        )
        
        # Verify content
        self.assertIn("Context Continuity", injection)
        self.assertIn("Memory injection at", injection)
        self.assertIn("Continuity Note", injection)
        self.assertIn("Test Task", injection)
        self.assertIn("Current Projects", injection)
        self.assertIn("Identity & Purpose", injection)

class TestCompactionHandler(unittest.TestCase):
    """Test the CompactionHandler class"""
    
    def setUp(self):
        self.handler = post_compaction_inject.CompactionHandler()
        
        # Create a temporary state file for the handler's state manager
        self.temp_state_file = tempfile.mktemp(suffix='.json')
        self.handler.state_manager = post_compaction_inject.ContextStateManager(state_file=self.temp_state_file)
    
    def tearDown(self):
        # Clean up temporary file
        if os.path.exists(self.temp_state_file):
            os.remove(self.temp_state_file)
    
    @mock.patch('post_compaction_inject.MemoryRetriever.generate_context_injection')
    @mock.patch('post_compaction_inject.MessagingManager.inject_context')
    def test_process_message_with_compaction(self, mock_inject, mock_generate):
        """Test message processing with compaction detection"""
        # Mock return values
        mock_generate.return_value = "Mocked injection content"
        mock_inject.return_value = True
        
        # Test with compaction indicator
        result = self.handler.process_message(
            session_id="test-session",
            message_id="compaction-msg",
            content="I'll start fresh with a new context",
            role="assistant"
        )
        
        # Verify injection was generated and sent
        self.assertEqual(result, "Mocked injection content")
        mock_generate.assert_called_once()
        mock_inject.assert_called_once()
        
        # Test with normal message
        mock_generate.reset_mock()
        mock_inject.reset_mock()
        
        result = self.handler.process_message(
            session_id="test-session",
            message_id="normal-msg",
            content="This is a normal message",
            role="user"
        )
        
        # Verify no injection was generated or sent
        self.assertIsNone(result)
        mock_generate.assert_not_called()
        mock_inject.assert_not_called()

def run_integration_test():
    """Run an integration test that executes the actual script"""
    test_session = f"test-session-{int(datetime.now().timestamp())}"
    
    print(f"Running integration test with session ID: {test_session}")
    
    try:
        # Run with --test flag
        process = subprocess.run(
            ["/Users/karst/.openclaw/workspace/post-compaction-inject.py", "--test", "--session", test_session],
            capture_output=True,
            text=True,
            check=True
        )
        
        print("\nTest injection output:")
        print(process.stdout)
        
        # Try with --simulate flag
        process = subprocess.run(
            ["/Users/karst/.openclaw/workspace/post-compaction-inject.py", "--simulate", "--session", test_session],
            capture_output=True,
            text=True,
            check=True
        )
        
        print("\nSimulation output:")
        print(process.stdout)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Integration test failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Run the tests"""
    print("Running unit tests...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    print("\nRunning integration test...")
    success = run_integration_test()
    
    if success:
        print("\nAll tests completed successfully!")
    else:
        print("\nIntegration test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()