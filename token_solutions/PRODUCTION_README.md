# Token Solutions - Production Deployment

This is a production deployment of token management solutions for large language models. The solution addresses context window limitations through two complementary approaches:

1. **Semantic Compression**: Reduces token count while preserving meaning
2. **Context Extension**: Attempts to increase available context window size

## Getting Started

Activate the environment:
```bash
source ./activate.sh
```

## Usage

### Python API

The main entry point is the `token_solutions` module:

```python
from token_solutions import process_request, compress_text

# Process API requests with automatic token management
response = process_request(
    messages=[{"role": "user", "content": very_long_content}],
    model="gpt-4",
    max_tokens=4000
)

# Directly compress text
compressed = compress_text(very_long_text, compression_ratio=6)
```

### Drop-in Replacement for OpenAI

Replace your OpenAI imports with the wrapped version:

```python
# Before:
# from openai import OpenAI
# client = OpenAI()

# After:
import sys
sys.path.append('/path/to/services')
from openai_wrapper import OpenAI
client = OpenAI()

# Use exactly as you would use standard OpenAI client
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": very_long_content}],
    max_tokens=4000
)
```

### Command Line Interface

```bash
# Compress text
python token_solutions.py compress --input long_document.txt --output compressed.txt --ratio 6

# Use context extension
python token_solutions.py extend --input document.txt --model gpt-4 --output response.txt

# View usage statistics
python token_solutions.py stats
```

## Configuration

The system is configured via `config/token_solutions.json`. Key options:

- `semantic_compression.enabled`: Enable/disable compression
- `semantic_compression.default_compression_ratio`: Default compression level (higher = more compression)
- `context_extension.enabled`: Enable/disable context extension
- `context_extension.target_context_length`: Requested context length

## Monitoring

The system tracks token usage and savings. View statistics with:

```python
from token_solutions import get_statistics
stats = get_statistics()
print(stats)
```

Or from command line:
```bash
python token_solutions.py stats
```

## Troubleshooting

Common issues:

1. **API errors**: Check API keys are properly set in environment variables:
   ```bash
   export OPENAI_API_KEY=your_api_key
   export ANTHROPIC_API_KEY=your_api_key  # If using Anthropic
   export OPENROUTER_API_KEY=your_api_key  # If using OpenRouter
   ```

2. **Out of memory**: If compression fails with OOM errors, force CPU mode:
   ```bash
   export CUDA_VISIBLE_DEVICES=-1  # Force CPU mode
   ```

3. **Very large inputs**: For extremely large inputs (millions of tokens), process in chunks:
   ```python
   chunks = [doc[i:i+500000] for i in range(0, len(doc), 500000)]
   compressed_chunks = [compress_text(chunk) for chunk in chunks]
   compressed = "\n".join(compressed_chunks)
   ```

## Upgrading

To install updates:
```bash
./install.sh
```
