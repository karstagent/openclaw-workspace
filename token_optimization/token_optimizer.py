import tiktoken
import hashlib
import json
from typing import List, Dict, Any

class TokenOptimizer:
    def __init__(self, default_model='gpt-3.5-turbo'):
        self.cache = {}
        self.model = default_model
        self.encoder = tiktoken.encoding_for_model(self.model)
        self.token_usage_log = []
    
    def count_tokens(self, text: str) -> int:
        """Count tokens for a given text."""
        return len(self.encoder.encode(text))
    
    def compress_context(self, context: List[Dict[str, Any]], max_tokens: int = 2000) -> List[Dict[str, Any]]:
        """Compress context to fit within token limit."""
        compressed_context = []
        current_tokens = 0
        
        # Reverse to keep most recent context
        for message in reversed(context):
            message_tokens = self.count_tokens(json.dumps(message))
            
            if current_tokens + message_tokens <= max_tokens:
                compressed_context.insert(0, message)
                current_tokens += message_tokens
            else:
                break
        
        return compressed_context
    
    def cache_result(self, prompt: str, response: str):
        """Cache results to avoid redundant processing."""
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        self.cache[prompt_hash] = {
            'response': response,
            'timestamp': datetime.now(),
            'tokens_saved': self.count_tokens(prompt) + self.count_tokens(response)
        }
    
    def get_cached_result(self, prompt: str):
        """Retrieve cached result if available."""
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        return self.cache.get(prompt_hash)
    
    def select_optimal_model(self, task_complexity: str) -> str:
        """Dynamically select the most cost-effective model."""
        model_routing = {
            'low': 'gpt-3.5-turbo',
            'medium': 'claude-3-haiku',
            'high': 'claude-3-sonnet',
            'complex': 'claude-3-opus'
        }
        return model_routing.get(task_complexity, self.model)
    
    def log_token_usage(self, prompt_tokens: int, response_tokens: int):
        """Log token usage for analytics."""
        self.token_usage_log.append({
            'timestamp': datetime.now(),
            'prompt_tokens': prompt_tokens,
            'response_tokens': response_tokens,
            'total_tokens': prompt_tokens + response_tokens
        })
    
    def get_usage_summary(self):
        """Generate token usage summary."""
        if not self.token_usage_log:
            return None
        
        total_prompts = len(self.token_usage_log)
        total_tokens = sum(
            entry['total_tokens'] for entry in self.token_usage_log
        )
        
        return {
            'total_prompts': total_prompts,
            'avg_tokens_per_prompt': total_tokens / total_prompts,
            'total_tokens': total_tokens
        }

# Example usage
def main():
    optimizer = TokenOptimizer()
    
    # Example context compression
    long_context = [
        {'role': 'system', 'content': 'Long system prompt...'},
        {'role': 'user', 'content': 'First message...'},
        # ... many more messages
    ]
    
    compressed_context = optimizer.compress_context(long_context)
    
    # Optimal model selection
    model = optimizer.select_optimal_model('medium')
    
    # Token usage logging
    optimizer.log_token_usage(500, 300)
    
    # Get usage summary
    usage_summary = optimizer.get_usage_summary()
    print(json.dumps(usage_summary, indent=2))

if __name__ == '__main__':
    main()