"""
Semantic Recall Module - Context Retention System Component 4

This module provides the core functionality for the Semantic Recall Hook System,
which automatically triggers semantic search against vector memory for every prompt,
injecting relevant past conversations into context before LLM processing.

This is intended to be imported by other components of the Context Retention System.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("/Users/karst/.openclaw/workspace/logs/semantic-recall.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('semantic-recall')

# Constants
WORKSPACE_DIR = "/Users/karst/.openclaw/workspace"
CONFIG_PATH = os.path.join(WORKSPACE_DIR, "semantic-recall-config.json")
HOOK_PATH = os.path.join(WORKSPACE_DIR, "semantic-recall-hook.json")
HISTORY_PATH = os.path.join(WORKSPACE_DIR, "logs", "recall-history.jsonl")
DEFAULT_RELEVANCE_THRESHOLD = 0.65
DEFAULT_MAX_RESULTS = 3
DEFAULT_MAX_TOKENS = 1500
DEFAULT_RECALL_PREFIX = "# Recent Relevant Context\n\n"
DEFAULT_RECALL_SUFFIX = "\n\nConsider the above context in your response.\n\n"

# Make sure directories exist
os.makedirs(os.path.join(WORKSPACE_DIR, "logs"), exist_ok=True)

# Import vector memory system
sys.path.append(WORKSPACE_DIR)
try:
    from vector_memory import VectorMemoryPipeline
except ImportError:
    logger.error("Required dependency not found: vector_memory.py")
    logger.error("Make sure to implement the Vector Memory Pipeline first")

class SemanticRecallConfig:
    """Configuration manager for Semantic Recall"""
    
    def __init__(self, config_path=CONFIG_PATH):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading config: {e}")
                return self._create_default_config()
        else:
            return self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration"""
        return {
            "relevance_threshold": DEFAULT_RELEVANCE_THRESHOLD,
            "max_results": DEFAULT_MAX_RESULTS,
            "max_tokens": DEFAULT_MAX_TOKENS,
            "recall_prefix": DEFAULT_RECALL_PREFIX,
            "recall_suffix": DEFAULT_RECALL_SUFFIX,
            "enabled": True,
            "log_injections": True,
            "token_estimation_ratio": 4.0,  # Characters per token
            "include_sources": True,
            "excluded_sessions": [],
            "context_format": "markdown",  # or "plain"
            "last_updated": datetime.now().isoformat()
        }
    
    def save_config(self):
        """Save configuration to file"""
        self.config["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.debug(f"Config saved to {self.config_path}")
            return True
        except IOError as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def get(self, key, default=None):
        """Get a configuration value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set a configuration value"""
        self.config[key] = value
        return self.save_config()
    
    def enable(self):
        """Enable semantic recall"""
        self.config["enabled"] = True
        return self.save_config()
    
    def disable(self):
        """Disable semantic recall"""
        self.config["enabled"] = False
        return self.save_config()
    
    def is_enabled(self):
        """Check if semantic recall is enabled"""
        return self.config.get("enabled", True)
    
    def update(self, new_config):
        """Update multiple configuration values"""
        self.config.update(new_config)
        return self.save_config()

class SemanticRecallHook:
    """Hook system for semantic recall"""
    
    def __init__(self, config=None, vector_memory=None):
        self.config = config or SemanticRecallConfig()
        self.vector_memory = vector_memory or VectorMemoryPipeline()
        self.recall_history = []
    
    def _estimate_tokens(self, text):
        """Estimate the number of tokens in text"""
        if not text:
            return 0
        ratio = self.config.get("token_estimation_ratio", 4.0)
        return int(len(text) / ratio)
    
    def _log_recall(self, query, results, injected_text, token_estimate):
        """Log recall event to history file"""
        if not self.config.get("log_injections", True):
            return
            
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "num_results": len(results),
            "token_estimate": token_estimate,
            "sources": [r.get("source") for r in results],
            "similarity_range": [min([r.get("similarity", 0) for r in results] or [0]), 
                                max([r.get("similarity", 0) for r in results] or [0])]
        }
        
        # Keep records of past recalls
        self.recall_history.append(log_entry)
        
        # Truncate history if it gets too large
        if len(self.recall_history) > 100:
            self.recall_history = self.recall_history[-100:]
        
        # Append to log file
        try:
            with open(HISTORY_PATH, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
        except IOError as e:
            logger.error(f"Error writing to recall history: {e}")
    
    def format_recalled_context(self, results):
        """Format recalled context for injection"""
        if not results:
            return ""
        
        context_format = self.config.get("context_format", "markdown")
        include_sources = self.config.get("include_sources", True)
        formatted_text = self.config.get("recall_prefix", DEFAULT_RECALL_PREFIX)
        
        for i, result in enumerate(results):
            source = result.get("source", "unknown")
            timestamp = result.get("timestamp")
            similarity = result.get("similarity", 0)
            text = result.get("text", "")
            
            if context_format == "markdown":
                # Format as markdown
                formatted_text += f"### Source {i+1}"
                
                if include_sources:
                    formatted_text += f": {source}"
                    if timestamp:
                        try:
                            dt = datetime.fromisoformat(timestamp)
                            formatted_text += f" ({dt.strftime('%Y-%m-%d')})"
                        except:
                            pass
                
                formatted_text += f"\n\n{text}\n\n"
                
            else:
                # Format as plain text
                formatted_text += f"--- Source {i+1}"
                
                if include_sources:
                    formatted_text += f": {source}"
                    if timestamp:
                        try:
                            dt = datetime.fromisoformat(timestamp)
                            formatted_text += f" ({dt.strftime('%Y-%m-%d')})"
                        except:
                            pass
                
                formatted_text += f" ---\n\n{text}\n\n"
        
        formatted_text += self.config.get("recall_suffix", DEFAULT_RECALL_SUFFIX)
        return formatted_text
    
    def process_prompt(self, prompt, session_id=None):
        """
        Process a prompt and return relevant context
        
        Args:
            prompt: The user prompt to process
            session_id: Optional session ID for logging
            
        Returns:
            Tuple of (injected_text, num_results, token_estimate)
        """
        # Skip if disabled
        if not self.config.is_enabled():
            logger.debug("Semantic recall is disabled, skipping")
            return "", 0, 0
        
        # Skip if session is excluded
        excluded_sessions = self.config.get("excluded_sessions", [])
        if session_id and session_id in excluded_sessions:
            logger.debug(f"Session {session_id} is excluded from semantic recall")
            return "", 0, 0
        
        # Get configuration
        relevance_threshold = self.config.get("relevance_threshold", DEFAULT_RELEVANCE_THRESHOLD)
        max_results = self.config.get("max_results", DEFAULT_MAX_RESULTS)
        max_tokens = self.config.get("max_tokens", DEFAULT_MAX_TOKENS)
        
        # Search vector memory
        try:
            start_time = time.time()
            results = self.vector_memory.search(
                prompt,
                k=max_results * 2,  # Request more to allow filtering
                threshold=relevance_threshold
            )
            search_time = time.time() - start_time
            
            logger.info(f"Vector search found {len(results)} results in {search_time:.2f}s")
            
            # Limit to max_results
            results = results[:max_results]
            
            if not results:
                logger.debug(f"No relevant results found for prompt: {prompt[:50]}...")
                return "", 0, 0
            
            # Format the context
            injected_text = self.format_recalled_context(results)
            
            # Estimate token usage
            token_estimate = self._estimate_tokens(injected_text)
            
            # Check if within token budget
            if token_estimate > max_tokens:
                # Trim results to fit budget
                results_to_keep = max(1, int(len(results) * max_tokens / token_estimate))
                results = results[:results_to_keep]
                injected_text = self.format_recalled_context(results)
                token_estimate = self._estimate_tokens(injected_text)
                
                logger.info(f"Trimmed results to {results_to_keep} to fit token budget")
            
            # Log the recall
            self._log_recall(prompt, results, injected_text, token_estimate)
            
            return injected_text, len(results), token_estimate
            
        except Exception as e:
            logger.error(f"Error in semantic recall: {e}")
            return "", 0, 0
    
    def register_hook(self):
        """Register the hook with OpenClaw"""
        hook_data = {
            "type": "pre_prompt",
            "name": "semantic_recall",
            "script": os.path.abspath(__file__),
            "function": "hook_entry_point",
            "enabled": self.config.is_enabled(),
            "registered_at": datetime.now().isoformat()
        }
        
        try:
            with open(HOOK_PATH, 'w') as f:
                json.dump(hook_data, f, indent=2)
            
            logger.info(f"Registered semantic recall hook at {HOOK_PATH}")
            return True
        except IOError as e:
            logger.error(f"Error registering hook: {e}")
            return False
    
    def unregister_hook(self):
        """Unregister the hook"""
        if os.path.exists(HOOK_PATH):
            try:
                os.remove(HOOK_PATH)
                logger.info("Unregistered semantic recall hook")
                return True
            except IOError as e:
                logger.error(f"Error unregistering hook: {e}")
                return False
        return True

def hook_entry_point(prompt, session_id=None):
    """
    Entry point for OpenClaw hook system
    
    This function is called by OpenClaw before processing a prompt
    """
    config = SemanticRecallConfig()
    vector_memory = VectorMemoryPipeline()
    hook = SemanticRecallHook(config, vector_memory)
    
    injected_text, num_results, token_estimate = hook.process_prompt(prompt, session_id)
    
    if injected_text:
        logger.info(f"Injected {num_results} results ({token_estimate} tokens) for prompt")
    
    return injected_text