import tiktoken
import numpy as np
from typing import List, Dict, Any

class AdvancedTokenizer:
    def __init__(self, model: str = 'cl100k_base', compression_level: float = 0.7):
        """
        Initialize advanced tokenizer with adaptive strategies
        
        :param model: Base tokenization model
        :param compression_level: Desired token compression ratio
        """
        self.encoding = tiktoken.get_encoding(model)
        self.compression_level = compression_level
        self.context_history = []
        
    def tokenize(self, text: str) -> List[int]:
        """
        Adaptive tokenization with context-aware segmentation
        
        :param text: Input text to tokenize
        :return: List of token IDs
        """
        # Basic tokenization
        tokens = self.encoding.encode(text)
        
        # Context-aware compression
        if self.context_history:
            tokens = self._apply_context_compression(tokens)
        
        # Update context history
        self.context_history.append(tokens)
        if len(self.context_history) > 5:
            self.context_history.pop(0)
        
        return tokens
    
    def _apply_context_compression(self, tokens: List[int]) -> List[int]:
        """
        Apply intelligent compression based on context history
        
        :param tokens: Original token list
        :return: Compressed token list
        """
        # Simple compression strategy
        compression_factor = int(len(tokens) * self.compression_level)
        
        # Prioritize recent context and unique tokens
        unique_tokens = list(set(tokens))
        compressed_tokens = unique_tokens[:compression_factor]
        
        return compressed_tokens
    
    def get_token_stats(self, tokens: List[int]) -> Dict[str, Any]:
        """
        Generate token usage statistics
        
        :param tokens: Token list to analyze
        :return: Dictionary of token statistics
        """
        return {
            'total_tokens': len(tokens),
            'unique_tokens': len(set(tokens)),
            'compression_ratio': len(set(tokens)) / len(tokens)
        }
    
    def decode(self, tokens: List[int]) -> str:
        """
        Decode tokens back to text
        
        :param tokens: List of token IDs
        :return: Decoded text
        """
        return self.encoding.decode(tokens)

def main():
    # Example usage
    tokenizer = AdvancedTokenizer(compression_level=0.8)
    
    text1 = "This is a sample text for tokenization and compression."
    text2 = "Another example to demonstrate context-aware tokenization."
    
    tokens1 = tokenizer.tokenize(text1)
    tokens2 = tokenizer.tokenize(text2)
    
    print("Text 1 Token Stats:", tokenizer.get_token_stats(tokens1))
    print("Text 2 Token Stats:", tokenizer.get_token_stats(tokens2))
    print("Decoded Text 1:", tokenizer.decode(tokens1))

if __name__ == '__main__':
    main()