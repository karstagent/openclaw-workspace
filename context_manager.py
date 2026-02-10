import os
import json
from datetime import datetime

class ContextManager:
    def __init__(self, max_context=200000, buffer=10000):
        """
        Initialize the context manager with configurable limits.
        
        Args:
            max_context: Maximum total context window size
            buffer: Buffer to leave for response tokens
        """
        self.max_context = max_context
        self.buffer = buffer
        self.max_input_tokens = max_context - buffer
        self.log_path = os.path.join(os.path.dirname(__file__), "logs/context_manager.log")
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        
    def log(self, message):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_path, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def trim_messages(self, messages, current_token_count):
        """
        Intelligently trim conversation history to fit within context limits.
        
        Strategy:
        1. Keep system messages intact (importance level 3)
        2. Preserve recent messages (importance level 2)
        3. Summarize or remove older messages as needed (importance level 1)
        
        Args:
            messages: List of message objects with role and content
            current_token_count: Current token count of the messages
            
        Returns:
            Trimmed list of messages and new token count
        """
        if current_token_count <= self.max_input_tokens:
            return messages, current_token_count
            
        self.log(f"Trimming required: {current_token_count} exceeds {self.max_input_tokens}")
        
        # Categorize messages by importance
        system_messages = []
        recent_messages = []
        older_messages = []
        
        # Define "recent" as the last 10 messages
        recent_threshold = 10
        
        for i, msg in enumerate(messages):
            if msg.get('role') == 'system':
                system_messages.append((i, msg))
            elif i >= len(messages) - recent_threshold:
                recent_messages.append((i, msg))
            else:
                older_messages.append((i, msg))
        
        # Calculate tokens per message (rough estimation)
        message_tokens = []
        for i, msg in enumerate(messages):
            # Rough estimation: 4 chars ≈ 1 token
            est_tokens = len(msg.get('content', '')) // 4
            message_tokens.append((i, est_tokens))
        
        # Sort older messages by estimated token count (descending)
        older_messages.sort(key=lambda x: message_tokens[x[0]][1], reverse=True)
        
        # Start removing older messages until we're under the limit
        removed_count = 0
        removed_tokens = 0
        
        while current_token_count - removed_tokens > self.max_input_tokens and older_messages:
            idx, _ = older_messages.pop(0)
            removed_tokens += message_tokens[idx][1]
            removed_count += 1
        
        if current_token_count - removed_tokens > self.max_input_tokens:
            # If still over limit, we need to remove some recent messages too (from oldest to newest)
            recent_messages.sort(key=lambda x: x[0])  # Sort by index (ascending)
            
            while current_token_count - removed_tokens > self.max_input_tokens and recent_messages:
                idx, _ = recent_messages.pop(0)
                removed_tokens += message_tokens[idx][1]
                removed_count += 1
        
        # Create new message list with remaining messages
        preserved_indices = set([idx for idx, _ in system_messages + recent_messages])
        new_messages = [msg for i, msg in enumerate(messages) if i in preserved_indices]
        
        # Add a system message explaining the trimming
        if removed_count > 0:
            trim_notice = {
                "role": "system",
                "content": f"Note: {removed_count} older messages were removed to fit within context limits."
            }
            new_messages.insert(0, trim_notice)
            
        new_token_count = current_token_count - removed_tokens
        self.log(f"Trimmed {removed_count} messages, reducing tokens from {current_token_count} to {new_token_count}")
        
        return new_messages, new_token_count
        
    def create_summary(self, messages):
        """
        Create a summary of older messages to preserve context while reducing tokens.
        
        Args:
            messages: List of older messages to summarize
            
        Returns:
            A summary message that can replace the individual messages
        """
        # In a practical implementation, you might call an LLM to generate this summary
        # For now, we'll implement a simple approach
        
        speakers = set()
        topics = []
        total_chars = 0
        
        for msg in messages:
            role = msg.get('role', '')
            name = msg.get('name', role)
            speakers.add(name)
            content = msg.get('content', '')
            total_chars += len(content)
            
            # Simple topic extraction - first 50 chars
            if content and len(content) > 50:
                topics.append(content[:50] + "...")
            elif content:
                topics.append(content)
        
        # Select up to 3 topics for brevity
        topic_samples = topics[:3] if len(topics) > 3 else topics
        
        summary = {
            "role": "system",
            "content": f"[Summary of {len(messages)} older messages between {', '.join(speakers)}. "
                       f"Topics included: {'; '.join(topic_samples)}]"
        }
        
        # Log token savings
        estimated_original_tokens = total_chars // 4
        estimated_summary_tokens = len(summary['content']) // 4
        savings = estimated_original_tokens - estimated_summary_tokens
        
        self.log(f"Summary replaced {len(messages)} messages, saving ~{savings} tokens")
        
        return summary
    
    def optimize_request(self, request_data):
        """
        Optimize an LLM request to fit within context limits.
        
        Args:
            request_data: Dictionary containing messages and max_tokens
            
        Returns:
            Optimized request data
        """
        messages = request_data.get('messages', [])
        max_tokens = request_data.get('max_tokens', 32000)
        
        # Estimate current token count
        # This is a rough estimation; in practice, you should use a tokenizer
        current_token_count = 0
        for msg in messages:
            content = msg.get('content', '')
            # Rough estimation: 4 chars ≈ 1 token
            current_token_count += len(content) // 4
        
        self.log(f"Request with {len(messages)} messages, ~{current_token_count} tokens, max_tokens={max_tokens}")
        
        # Check if over limit
        if current_token_count + max_tokens > self.max_context:
            # Need to reduce either input tokens or max_tokens
            
            # First try: reduce max_tokens if it's excessive
            if max_tokens > self.buffer:
                new_max_tokens = min(max_tokens, self.max_context - current_token_count)
                if new_max_tokens >= 1000:  # Ensure reasonable response length
                    request_data['max_tokens'] = new_max_tokens
                    self.log(f"Reduced max_tokens from {max_tokens} to {new_max_tokens}")
                    
                    # Check if this solved the problem
                    if current_token_count + new_max_tokens <= self.max_context:
                        return request_data
            
            # Second try: trim messages
            trimmed_messages, new_token_count = self.trim_messages(messages, current_token_count)
            request_data['messages'] = trimmed_messages
            
            # Final check - if still over limit, reduce max_tokens further
            if new_token_count + request_data.get('max_tokens', 32000) > self.max_context:
                new_max_tokens = max(1000, self.max_context - new_token_count)
                request_data['max_tokens'] = new_max_tokens
                self.log(f"Further reduced max_tokens to {new_max_tokens}")
        
        return request_data

# Example usage
if __name__ == "__main__":
    context_manager = ContextManager()
    
    # Sample request that would exceed limits
    sample_request = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            # Add many messages to simulate a long conversation
        ],
        "max_tokens": 32000
    }
    
    # Generate mock messages for testing
    for i in range(200):
        if i % 2 == 0:
            sample_request["messages"].append({
                "role": "user", 
                "content": f"This is a long user message with lots of content to simulate a real conversation. Question {i}."
            })
        else:
            sample_request["messages"].append({
                "role": "assistant",
                "content": f"This is a detailed response from the assistant that provides comprehensive information about the topic at hand. Answer {i}."
            })
    
    # Optimize the request
    optimized_request = context_manager.optimize_request(sample_request)
    
    # Print results
    print(f"Original message count: {len(sample_request['messages'])}")
    print(f"Optimized message count: {len(optimized_request['messages'])}")
    print(f"Original max_tokens: {sample_request['max_tokens']}")
    print(f"Optimized max_tokens: {optimized_request['max_tokens']}")