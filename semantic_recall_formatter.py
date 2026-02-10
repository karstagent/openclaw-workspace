#!/usr/bin/env python3
"""
Token-Aware Formatter for Semantic Recall Hook System

This module handles the intelligent formatting of search results for
injection into the context window, respecting token limits and
priority ordering.
"""

import os
import json
import logging
from datetime import datetime
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("/Users/karst/.openclaw/workspace/logs/semantic-recall-formatter.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('semantic-recall-formatter')

class TokenAwareFormatter:
    """
    Formats search results for context injection while respecting token limits
    """
    
    def __init__(self, config=None):
        """Initialize with optional config"""
        self.config = config or {}
        self.token_estimation_ratio = self.config.get('token_estimation_ratio', 4.0)  # chars per token
        self.max_tokens = self.config.get('max_tokens', 1500)
        self.include_sources = self.config.get('include_sources', True)
        self.context_format = self.config.get('context_format', 'markdown')
        self.recall_prefix = self.config.get('recall_prefix', '# Relevant Context\n\n*Semantic recall detected relevant information*\n\n')
        self.recall_suffix = self.config.get('recall_suffix', '\n\n---\n\n')
        
    def estimate_tokens(self, text):
        """Estimate token count based on character count"""
        return len(text) / self.token_estimation_ratio if text else 0
    
    def format_results(self, results, max_tokens=None):
        """
        Format search results for injection into context
        
        Args:
            results: List of search results, each with text, source, and score
            max_tokens: Override default max tokens
            
        Returns:
            Formatted text ready for injection
        """
        if not results:
            return None
            
        max_tokens = max_tokens or self.max_tokens
        
        # Sort results by score (highest first)
        sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
        
        # Start with prefix
        formatted_text = self.recall_prefix
        current_tokens = self.estimate_tokens(formatted_text)
        suffix_tokens = self.estimate_tokens(self.recall_suffix)
        
        # Reserve tokens for suffix
        available_tokens = max_tokens - suffix_tokens
        
        # Add results one by one until we hit token limit
        added_results = []
        
        for result in sorted_results:
            # Format this result
            result_text = self._format_single_result(result)
            result_tokens = self.estimate_tokens(result_text)
            
            # Check if we can add it
            if current_tokens + result_tokens <= available_tokens:
                formatted_text += result_text
                current_tokens += result_tokens
                added_results.append(result)
            else:
                # Try truncated version if this is first result
                if not added_results:
                    truncated = self._truncate_result(
                        result, 
                        available_tokens - current_tokens
                    )
                    if truncated:
                        formatted_text += truncated
                        added_results.append(result)
                break
                
        # Add suffix if we added any results
        if added_results:
            formatted_text += self.recall_suffix
            
        # Log what we did
        logger.info(f"Formatted {len(added_results)} of {len(results)} results " +
                   f"using ~{int(current_tokens + suffix_tokens)} tokens " +
                   f"(limit: {max_tokens})")
        
        return formatted_text if added_results else None
    
    def _format_single_result(self, result):
        """Format a single search result"""
        text = result.get('text', '')
        source = result.get('source', 'Unknown')
        score = result.get('score', 0)
        
        if self.context_format == 'markdown':
            formatted = f"## {source}\n\n"
            formatted += text.strip() + "\n\n"
            if self.include_sources:
                formatted += f"*Source: {source} (relevance: {score:.2f})*\n\n"
        else:  # plain text
            formatted = f"{source}:\n\n"
            formatted += text.strip() + "\n\n"
            if self.include_sources:
                formatted += f"Source: {source} (relevance: {score:.2f})\n\n"
                
        return formatted
    
    def _truncate_result(self, result, available_token_count):
        """Truncate a result to fit within available tokens"""
        if available_token_count < 100:
            return None  # Too small to be useful
            
        text = result.get('text', '')
        source = result.get('source', 'Unknown')
        score = result.get('score', 0)
        
        # Calculate how many chars we can keep
        chars_to_keep = int(available_token_count * self.token_estimation_ratio)
        
        # Reserve space for header, source, and truncation notice
        if self.context_format == 'markdown':
            header = f"## {source}\n\n"
            footer = f"\n\n*Source: {source} (relevance: {score:.2f}) [truncated]*\n\n"
        else:
            header = f"{source}:\n\n"
            footer = f"\n\nSource: {source} (relevance: {score:.2f}) [truncated]\n\n"
            
        reserved_chars = len(header) + len(footer)
        
        if chars_to_keep <= reserved_chars:
            return None  # Too small to be useful
            
        # Truncate the text
        content_chars = chars_to_keep - reserved_chars
        truncated_text = text[:content_chars] + "..."
        
        # Format the result
        if self.context_format == 'markdown':
            formatted = header + truncated_text + footer
        else:
            formatted = header + truncated_text + footer
            
        return formatted
        
    def format_metadata(self, results, prompt=None):
        """
        Create metadata about the injection for logging
        
        Args:
            results: List of search results
            prompt: Original prompt that triggered the search
            
        Returns:
            Metadata dictionary
        """
        if not results:
            return None
            
        return {
            "timestamp": datetime.now().isoformat(),
            "prompt_snippet": prompt[:100] + "..." if prompt and len(prompt) > 100 else prompt,
            "results_count": len(results),
            "top_sources": [r.get('source', 'Unknown') for r in results[:3]],
            "token_estimate": int(self.estimate_tokens(self._format_single_result(results[0]))),
            "score_range": [
                min([r.get('score', 0) for r in results]),
                max([r.get('score', 0) for r in results])
            ]
        }

# Test functionality if run directly
if __name__ == "__main__":
    # Create sample results
    sample_results = [
        {
            "text": "The semantic recall system should use a token budget of 1000-1500 tokens for injected content.",
            "source": "memory/2026-02-09.md#L123",
            "score": 0.92
        },
        {
            "text": "Context injection should prioritize more recent and higher-relevance results.",
            "source": "memory/2026-02-08.md#L45",
            "score": 0.85
        },
        {
            "text": "The recall system should include source information and relevance scores.",
            "source": "MEMORY.md#L789",
            "score": 0.79
        }
    ]
    
    # Create formatter with default config
    formatter = TokenAwareFormatter()
    
    # Format results
    formatted = formatter.format_results(sample_results)
    
    # Print the formatted text
    print("\n\n===== FORMATTED OUTPUT =====\n")
    print(formatted)
    print("\n===== END OUTPUT =====\n")
    
    # Print token estimation
    print(f"Estimated tokens: {int(formatter.estimate_tokens(formatted))}")