import os
import json
from datetime import datetime
from context_manager import ContextManager

class ContextMiddleware:
    """
    Middleware that automatically applies context management to LLM API requests.
    This can be integrated into your API client, router, or server.
    """
    
    def __init__(self, context_manager=None):
        """
        Initialize the middleware with an optional custom context manager.
        
        Args:
            context_manager: ContextManager instance (will create default if None)
        """
        self.context_manager = context_manager or ContextManager()
        self.log_path = os.path.join(os.path.dirname(__file__), "logs/context_middleware.log")
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
    
    def log(self, message):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_path, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def process_request(self, request_data):
        """
        Process an LLM API request, applying context management if needed.
        
        Args:
            request_data: Dictionary containing the LLM request data
            
        Returns:
            Processed request data that will fit within context limits
        """
        try:
            # Make a copy to avoid modifying the original
            processed_data = request_data.copy()
            
            # Apply context management
            before_msg_count = len(processed_data.get('messages', []))
            before_max_tokens = processed_data.get('max_tokens', 32000)
            
            processed_data = self.context_manager.optimize_request(processed_data)
            
            after_msg_count = len(processed_data.get('messages', []))
            after_max_tokens = processed_data.get('max_tokens', 32000)
            
            # Log if changes were made
            if before_msg_count != after_msg_count or before_max_tokens != after_max_tokens:
                self.log(f"Modified request: messages {before_msg_count}->{after_msg_count}, " +
                         f"max_tokens {before_max_tokens}->{after_max_tokens}")
            
            return processed_data
            
        except Exception as e:
            # Log error but allow request to continue (possibly fail at the API)
            self.log(f"Error processing request: {str(e)}")
            return request_data

# Example integration with an API client
class LLMClient:
    """
    Example LLM API client with context management middleware.
    Replace this with your actual API client implementation.
    """
    
    def __init__(self, api_key=None, base_url=None):
        """Initialize the client with API credentials"""
        self.api_key = api_key or os.environ.get("LLM_API_KEY")
        self.base_url = base_url or os.environ.get("LLM_API_URL", "https://api.example.com/v1")
        self.middleware = ContextMiddleware()
    
    async def chat_completion(self, messages, max_tokens=None, temperature=0.7, model="default-model"):
        """
        Send a chat completion request with automatic context management.
        
        Args:
            messages: List of message objects with role and content
            max_tokens: Maximum tokens in the response
            temperature: Sampling temperature
            model: Model identifier
            
        Returns:
            API response
        """
        # Prepare request data
        request_data = {
            "messages": messages,
            "model": model,
            "temperature": temperature
        }
        
        if max_tokens is not None:
            request_data["max_tokens"] = max_tokens
        
        # Apply middleware processing
        processed_data = self.middleware.process_request(request_data)
        
        # In a real implementation, you would send the processed request to the API
        # For this example, we'll just return the processed data
        return {
            "processed_request": processed_data,
            "would_send_to_api": True,
            "original_message_count": len(messages),
            "processed_message_count": len(processed_data["messages"])
        }

# Example usage
if __name__ == "__main__":
    # Create a client
    client = LLMClient()
    
    # Sample request that would exceed limits
    sample_messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    
    # Generate mock messages for testing
    for i in range(200):
        if i % 2 == 0:
            sample_messages.append({
                "role": "user", 
                "content": f"This is message {i}. " + "A " * 1000  # Long content to simulate token issues
            })
        else:
            sample_messages.append({
                "role": "assistant",
                "content": f"Response {i}. " + "B " * 1000
            })
    
    # Make a request with automatic context management
    import asyncio
    
    async def test_request():
        response = await client.chat_completion(
            messages=sample_messages,
            max_tokens=32000
        )
        print(json.dumps(response, indent=2))
    
    asyncio.run(test_request())