# Implementation Instructions for Token Limit Solution

This guide provides step-by-step instructions for implementing the token limit solution to address the error:

```
LLM request rejected: input length and max_tokens exceed context limit: 179949 + 32000 > 200000
```

## Quick Start

1. **Setup the environment**:
   ```bash
   chmod +x /Users/karst/.openclaw/workspace/setup_compression.sh
   /Users/karst/.openclaw/workspace/setup_compression.sh
   source /Users/karst/.openclaw/workspace/activate_compression.sh
   ```

2. **Test the compression**:
   ```bash
   # Create a test file with your long content
   python -c "print('Testing compression' * 10000)" > test_long.txt
   
   # Compress it
   ./semantic_compression.py --input test_long.txt --output test_compressed.txt --ratio 6
   ```

3. **Configure the API integration**:
   ```bash
   # If using OpenAI API
   export OPENAI_API_KEY=your_api_key
   
   # If using Anthropic API
   export ANTHROPIC_API_KEY=your_api_key
   
   # If using OpenRouter
   export OPENROUTER_API_KEY=your_api_key
   ```

## Implementation Options

You have two main options to solve the token limit issue:

### Option 1: Semantic Compression (Recommended for Immediate Use)

This approach compresses your input to fit within existing token limits:

1. **For direct API usage**:
   ```python
   from api_integration import CompressionEnabledClient
   
   # Initialize the client
   client = CompressionEnabledClient(
       compression_ratio=6,  # Adjust based on your needs
       token_limit_threshold=150000  # When to trigger compression
   )
   
   # Make API calls as usual
   response = client.chat_completions_create(
       model="gpt-4",
       messages=[{"role": "user", "content": very_long_content}],
       max_tokens=4000
   )
   ```

2. **For compressing files before sending**:
   ```bash
   ./semantic_compression.py --input your_long_document.txt --output compressed_document.txt --ratio 6
   ```

3. **For automatic integration with existing code**:
   ```python
   # Replace standard OpenAI client
   # from openai import OpenAI
   # client = OpenAI()
   
   # With compression-enabled client
   from api_integration import CompressionEnabledClient
   client = CompressionEnabledClient()
   ```

### Option 2: Extended Context Window (For Compatible Models)

This approach attempts to increase the model's context window:

1. **For direct API usage**:
   ```python
   from increase_context_window import ContextWindowExtender
   
   # Initialize the extender
   extender = ContextWindowExtender(
       target_context_length=400000,  # Request 400K context
       api_type="openai"  # or "anthropic" or "openrouter"
   )
   
   # Make API calls with extended context
   response = extender.extend_request(
       model="gpt-4",
       messages=[{"role": "user", "content": very_long_content}],
       max_tokens=4000
   )
   ```

2. **For command-line testing**:
   ```bash
   ./increase_context_window.py --input your_long_document.txt --api openai --context-length 400000
   ```

## Combining Both Approaches

For maximum reliability, you can combine both methods:

```python
from api_integration import CompressionEnabledClient
from increase_context_window import ContextWindowExtender

def process_long_document(document, model="gpt-4", api_type="openai"):
    # First try with extended context
    extender = ContextWindowExtender(
        target_context_length=400000,
        api_type=api_type,
        verbose=True
    )
    
    try:
        # Attempt with extended context
        response = extender.extend_request(
            model=model,
            messages=[{"role": "user", "content": document}],
            max_tokens=4000
        )
        return response
    except Exception as e:
        print(f"Extended context failed: {e}")
        
        # Fall back to compression
        client = CompressionEnabledClient(
            compression_ratio=6,
            verbose=True
        )
        
        if api_type == "openai" or api_type == "openrouter":
            return client.chat_completions_create(
                model=model,
                messages=[{"role": "user", "content": document}],
                max_tokens=4000
            )
        else:  # anthropic
            return client.messages_create(
                model=model,
                messages=[{"role": "user", "content": document}],
                max_tokens=4000
            )
```

## Customization

### Adjusting Compression Ratio

The compression ratio determines how much the input is condensed:

- **Lower ratio (2-4)**: Preserves more details but less compression
- **Medium ratio (5-7)**: Good balance for most use cases
- **Higher ratio (8+)**: Maximum compression but may lose details

Adjust based on your specific needs:

```python
client = CompressionEnabledClient(compression_ratio=4)  # More detail preservation
```

### Model Selection for Compression

The compression pipeline uses two models:

1. **Embedding model**: For text similarity analysis
2. **Summarization model**: For condensing text clusters

You can customize these:

```python
client = CompressionEnabledClient(
    embedding_model="sentence-transformers/all-mpnet-base-v2",  # More accurate embeddings
    summarizer_model="facebook/bart-large-cnn"  # Default summarizer
)
```

## Troubleshooting

### Common Issues

1. **Dependencies missing**:
   ```bash
   pip install torch transformers scikit-learn numpy tqdm sentence-transformers
   ```

2. **Out of memory errors**:
   - Reduce batch size by setting: `export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb=512`
   - Or force CPU mode: `client = CompressionEnabledClient(device="cpu")`

3. **API errors**:
   - Check API keys are correctly set
   - Verify model names are valid
   - Ensure network connectivity to API endpoints

### Getting Help

For additional assistance:
- Check the documentation in `/Users/karst/.openclaw/workspace/COMPRESSION_README.md`
- Review the source code for detailed parameter options
- Run scripts with `--verbose` flag for more detailed logging