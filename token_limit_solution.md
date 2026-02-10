# Token Limit Solution Implementation Plan

## Problem Statement

The LLM request was rejected with the error:
```
LLM request rejected: input length and max_tokens exceed context limit: 179949 + 32000 > 200000, decrease input length or max_tokens and try again The limit was not successfully increased to 400000
```

This indicates that the combined input length (179,949 tokens) and requested output tokens (32,000) exceeded the 200K token context window limit.

## Implementation Plan

Based on our research, we'll implement a two-pronged approach:

1. **Short-term solution**: Deploy semantic compression to reduce input length
2. **Long-term solution**: Configure model with extended context window

### Phase 1: Semantic Compression Implementation (Immediate)

**Goal**: Compress the 179,949 token input to fit within the 200K limit while preserving semantic meaning

#### Step 1: Setup Compression Pipeline
```python
# Create basic semantic compression pipeline
import torch
from transformers import AutoTokenizer, AutoModel, BartForConditionalGeneration, BartTokenizer
from sklearn.cluster import SpectralClustering
import numpy as np

# Initialize models
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
embedding_model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
summarizer_tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
summarizer = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")

def embed_text(text_blocks):
    """Generate embeddings for text blocks"""
    embeddings = []
    
    for block in text_blocks:
        # Tokenize and get embeddings
        inputs = tokenizer(block, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = embedding_model(**inputs)
        
        # Use mean pooling to get sentence embedding
        embeddings.append(outputs.last_hidden_state.mean(dim=1).squeeze().numpy())
    
    return np.array(embeddings)

def cluster_text(embeddings, n_clusters=10):
    """Cluster text embeddings using Spectral Clustering"""
    # Create similarity matrix
    similarity_matrix = np.zeros((len(embeddings), len(embeddings)))
    for i in range(len(embeddings)):
        for j in range(len(embeddings)):
            similarity_matrix[i, j] = np.dot(embeddings[i], embeddings[j]) / (np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j]))
    
    # Apply spectral clustering
    clustering = SpectralClustering(n_clusters=n_clusters, affinity='precomputed', random_state=0)
    clusters = clustering.fit_predict(similarity_matrix)
    
    return clusters

def summarize_cluster(cluster_text, max_length=200):
    """Summarize a cluster of text"""
    inputs = summarizer_tokenizer(cluster_text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = summarizer.generate(inputs["input_ids"], max_length=max_length, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = summarizer_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def semantic_compression(document, compression_ratio=6):
    """Apply semantic compression to a document"""
    # Split document into manageable blocks
    block_size = 500  # words
    words = document.split()
    blocks = [' '.join(words[i:i+block_size]) for i in range(0, len(words), block_size)]
    
    # Estimate number of clusters based on compression ratio
    n_clusters = max(1, len(blocks) // compression_ratio)
    
    # Embed and cluster blocks
    embeddings = embed_text(blocks)
    clusters = cluster_text(embeddings, n_clusters)
    
    # Combine blocks by cluster and summarize
    cluster_texts = {}
    for i, cluster_id in enumerate(clusters):
        if cluster_id not in cluster_texts:
            cluster_texts[cluster_id] = []
        cluster_texts[cluster_id].append(blocks[i])
    
    summaries = []
    for cluster_id, texts in cluster_texts.items():
        combined_text = " ".join(texts)
        summary = summarize_cluster(combined_text)
        summaries.append(summary)
    
    # Return compressed document
    return " ".join(summaries)
```

#### Step 2: Implement API Integration Layer
```python
# api_integration.py
import openai
from openai import OpenAI
from semantic_compression import semantic_compression

# Original OpenAI client for reference
original_client = OpenAI()

class CompressionEnabledClient:
    """OpenAI client wrapper with semantic compression"""
    
    def __init__(self, compression_ratio=6):
        self.compression_ratio = compression_ratio
        self.client = OpenAI()
    
    def chat_completions_create(self, **kwargs):
        """Override chat completions with compression"""
        # Get messages from kwargs
        messages = kwargs.get('messages', [])
        
        # Check if compression is needed (approximating token count)
        token_estimate = sum(len(msg.get('content', '').split()) * 4/3 for msg in messages)
        
        if token_estimate > 150000:  # Allow buffer below 200K limit
            # Apply compression to user messages only
            compressed_messages = []
            for msg in messages:
                if msg.get('role') == 'user':
                    compressed_content = semantic_compression(
                        msg.get('content', ''), 
                        self.compression_ratio
                    )
                    compressed_msg = msg.copy()
                    compressed_msg['content'] = compressed_content
                    compressed_messages.append(compressed_msg)
                else:
                    compressed_messages.append(msg)
            
            # Update kwargs with compressed messages
            kwargs['messages'] = compressed_messages
        
        # Call original client
        return self.client.chat.completions.create(**kwargs)

# Usage:
# client = CompressionEnabledClient()
# response = client.chat_completions_create(
#     model="gpt-4",
#     messages=[{"role": "user", "content": very_long_content}],
#     max_tokens=32000
# )
```

#### Step 3: Create CLI Tool for Document Compression
```python
# compress_document.py
import argparse
from semantic_compression import semantic_compression

def main():
    parser = argparse.ArgumentParser(description="Semantically compress a document")
    parser.add_argument("input_file", help="Path to input document")
    parser.add_argument("output_file", help="Path to output compressed document")
    parser.add_argument("--ratio", type=int, default=6, help="Compression ratio (default: 6)")
    
    args = parser.parse_args()
    
    # Read input document
    with open(args.input_file, 'r') as f:
        document = f.read()
    
    # Apply compression
    compressed_document = semantic_compression(document, args.ratio)
    
    # Write output
    with open(args.output_file, 'w') as f:
        f.write(compressed_document)
    
    print(f"Compressed document from {len(document.split())} words to {len(compressed_document.split())} words")

if __name__ == "__main__":
    main()
```

### Phase 2: Extended Context Window Configuration (Medium Term)

**Goal**: Modify model configuration to support context windows beyond 200K tokens

#### Step 1: API Configuration (if using OpenAI or similar API)

For OpenAI API usage, investigate if the model supports the `base_context_length` parameter to increase the context window. Example configuration:

```python
# Example OpenAI API configuration
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": long_content}],
    max_tokens=32000,
    base_context_length=400000  # Request extended context
)
```

#### Step 2: Self-Hosted Model Configuration

If using a self-hosted model (e.g., Llama 3, Claude, etc.), adjust the deployment configuration:

```bash
# Example for Ollama (local deployment)
cat <<EOF > Modelfile
FROM llama3:latest
PARAMETER num_ctx 400000
PARAMETER num_gpu 2
EOF

ollama create extended-context-llama -f Modelfile
```

For Claude models deployed via container:
```bash
docker run --gpus all \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -e MODEL_NAME=claude-3-haiku-20240307 \
  -e MAX_CTX_LENGTH=200000 \
  -p 8080:8080 \
  anthropic/claude-api-server
```

#### Step 3: Hardware Requirements Assessment

For extended context windows, ensure hardware meets these minimum requirements:

- 32GB+ VRAM for context windows up to 400K tokens
- Multiple GPUs for parallel processing
- 64GB+ system RAM

### Phase 3: Hybrid Long-Document Processing System (Long Term)

**Goal**: Create a robust system that handles documents of any length regardless of model constraints

1. **Document Chunking**: Break documents into overlapping semantic chunks
2. **Query Routing**: Direct questions to the most relevant chunks
3. **Answer Synthesis**: Combine responses from multiple chunks when needed

This will be implemented as a separate project after the initial token limit issue is resolved.

## Immediate Action Items

1. Implement the semantic compression pipeline (Phase 1, Step 1)
2. Integrate compression with the API client (Phase 1, Step 2)
3. Test with the current 179K token document that's failing
4. Document results and refine compression ratio as needed
5. Begin research on extended context window configuration options specific to our deployment

## Resources Needed

1. Python dependencies:
   - transformers
   - pytorch
   - scikit-learn
   - numpy
   - openai (or equivalent client library)

2. Test documents of varying lengths for validation

3. GPU resources for running the compression pipeline efficiently