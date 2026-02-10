#!/usr/bin/env python3
"""
Semantic Compression Module for Large Language Models
Efficiently compresses text while preserving semantic meaning.
"""

import argparse
import os
import sys
import numpy as np
import logging
from typing import List, Dict, Tuple, Optional, Union
import json
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("semantic-compression")

# Check for required dependencies and install if needed
try:
    import torch
    from transformers import AutoTokenizer, AutoModel, pipeline
    from sklearn.cluster import SpectralClustering
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    logger.warning("Installing required dependencies...")
    import subprocess
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", 
        "torch", "transformers", "scikit-learn", "tqdm", "sentence-transformers"
    ])
    import torch
    from transformers import AutoTokenizer, AutoModel, pipeline
    from sklearn.cluster import SpectralClustering
    from sklearn.metrics.pairwise import cosine_similarity

class SemanticCompressor:
    """Compress text while preserving semantic meaning using embedding-based clustering and summarization."""
    
    def __init__(
        self, 
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        summarizer_model: str = "facebook/bart-large-cnn",
        device: str = None,
        cache_dir: str = None
    ):
        """Initialize the compressor with specified models."""
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        logger.info(f"Using device: {self.device}")
        
        # Load embedding model
        self.embedding_tokenizer = AutoTokenizer.from_pretrained(embedding_model, cache_dir=cache_dir)
        self.embedding_model = AutoModel.from_pretrained(embedding_model, cache_dir=cache_dir).to(self.device)
        
        # Load summarizer
        self.summarizer = pipeline(
            "summarization", 
            model=summarizer_model, 
            device=0 if self.device == "cuda" else -1,
            cache_dir=cache_dir
        )
        
        logger.info("Models loaded successfully")
    
    def _split_into_segments(
        self, 
        document: str, 
        max_segment_tokens: int = 500,
        overlap_tokens: int = 50
    ) -> List[str]:
        """Split a document into segments with overlap."""
        # Tokenize the document to properly handle token boundaries
        tokens = self.embedding_tokenizer.tokenize(document)
        segments = []
        
        for i in range(0, len(tokens), max_segment_tokens - overlap_tokens):
            segment_tokens = tokens[i:i + max_segment_tokens]
            segment_text = self.embedding_tokenizer.convert_tokens_to_string(segment_tokens)
            segments.append(segment_text)
            
            # Break if we've processed the entire document
            if i + max_segment_tokens >= len(tokens):
                break
                
        logger.info(f"Split document into {len(segments)} segments")
        return segments
    
    def _generate_embeddings(self, segments: List[str]) -> np.ndarray:
        """Generate embeddings for text segments."""
        embeddings = []
        
        for segment in tqdm(segments, desc="Generating embeddings"):
            # Tokenize and generate embeddings
            inputs = self.embedding_tokenizer(
                segment, 
                return_tensors="pt", 
                padding=True, 
                truncation=True, 
                max_length=512
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.embedding_model(**inputs)
                
            # Use mean pooling to get segment embedding
            attention_mask = inputs["attention_mask"]
            mask = attention_mask.unsqueeze(-1).expand(outputs.last_hidden_state.size()).float()
            masked_embeddings = outputs.last_hidden_state * mask
            summed = torch.sum(masked_embeddings, 1)
            counts = torch.clamp(torch.sum(attention_mask, 1, keepdim=True), min=1e-9)
            mean_pooled = summed / counts
            
            # Convert to numpy and append to results
            embeddings.append(mean_pooled.cpu().numpy()[0])
            
        return np.array(embeddings)
    
    def _build_similarity_matrix(self, embeddings: np.ndarray) -> np.ndarray:
        """Build a similarity matrix from embeddings."""
        return cosine_similarity(embeddings)
    
    def _cluster_segments(
        self, 
        similarity_matrix: np.ndarray, 
        n_clusters: int
    ) -> np.ndarray:
        """Cluster segments using spectral clustering on similarity matrix."""
        clustering = SpectralClustering(
            n_clusters=n_clusters, 
            affinity='precomputed', 
            random_state=42,
            assign_labels='discretize'
        )
        return clustering.fit_predict(similarity_matrix)
    
    def _summarize_cluster(
        self, 
        segments: List[str], 
        max_length: int = 150,
        min_length: int = 50
    ) -> str:
        """Summarize a cluster of segments."""
        # Combine segments
        combined_text = " ".join(segments)
        
        # Calculate adaptive length based on input size
        adaptive_max_length = min(max_length, max(min_length, int(len(combined_text.split()) / 4)))
        
        # Generate summary
        summary = self.summarizer(
            combined_text, 
            max_length=adaptive_max_length, 
            min_length=min_length,
            do_sample=False
        )[0]["summary_text"]
        
        return summary
    
    def compress(
        self, 
        document: str, 
        compression_ratio: int = 6,
        min_clusters: int = 3,
        max_clusters: int = 50,
        preserve_structure: bool = True
    ) -> str:
        """
        Compress a document using semantic clustering and summarization.
        
        Args:
            document: Text to compress
            compression_ratio: Target compression ratio (higher = more compression)
            min_clusters: Minimum number of clusters to generate
            max_clusters: Maximum number of clusters to generate
            preserve_structure: Whether to preserve document structure
            
        Returns:
            Compressed document
        """
        # Split document into segments
        segments = self._split_into_segments(document)
        
        # If document is very short, return as is
        if len(segments) <= min_clusters:
            logger.info("Document too short for compression, returning as is")
            return document
            
        # Generate embeddings for segments
        embeddings = self._generate_embeddings(segments)
        
        # Build similarity matrix
        similarity_matrix = self._build_similarity_matrix(embeddings)
        
        # Determine number of clusters based on compression ratio
        n_clusters = max(min_clusters, min(max_clusters, int(len(segments) / compression_ratio)))
        logger.info(f"Using {n_clusters} clusters for compression")
        
        # Cluster segments
        clusters = self._cluster_segments(similarity_matrix, n_clusters)
        
        # Group segments by cluster
        cluster_segments = {}
        for i, cluster_id in enumerate(clusters):
            if cluster_id not in cluster_segments:
                cluster_segments[cluster_id] = []
            cluster_segments[cluster_id].append(segments[i])
        
        # Summarize each cluster
        summaries = []
        for cluster_id, segments_in_cluster in tqdm(cluster_segments.items(), desc="Summarizing clusters"):
            summary = self._summarize_cluster(segments_in_cluster)
            summaries.append((cluster_id, summary))
        
        # If preserving structure, re-order summaries by original document order
        if preserve_structure:
            # Get the first occurrence of each cluster in the original document
            first_occurrences = {}
            for i, cluster_id in enumerate(clusters):
                if cluster_id not in first_occurrences:
                    first_occurrences[cluster_id] = i
            
            # Sort summaries by first occurrence
            summaries.sort(key=lambda x: first_occurrences[x[0]])
        
        # Extract just the summary texts
        summary_texts = [summary for _, summary in summaries]
        
        # Join summaries into final compressed document
        compressed_document = " ".join(summary_texts)
        
        # Calculate compression statistics
        original_tokens = len(self.embedding_tokenizer.tokenize(document))
        compressed_tokens = len(self.embedding_tokenizer.tokenize(compressed_document))
        actual_ratio = original_tokens / max(1, compressed_tokens)
        
        logger.info(f"Compressed from {original_tokens} to {compressed_tokens} tokens")
        logger.info(f"Actual compression ratio: {actual_ratio:.2f}x")
        
        return compressed_document

def count_tokens(text: str, tokenizer_name: str = "gpt2") -> int:
    """Count tokens in text using specified tokenizer."""
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    return len(tokenizer.encode(text))

def main():
    parser = argparse.ArgumentParser(description="Semantic Compression Tool")
    parser.add_argument("--input", "-i", required=True, help="Input file or text")
    parser.add_argument("--output", "-o", help="Output file (default: print to stdout)")
    parser.add_argument("--ratio", "-r", type=int, default=6, help="Target compression ratio (default: 6)")
    parser.add_argument("--embedding-model", default="sentence-transformers/all-MiniLM-L6-v2", 
                      help="Model to use for embeddings")
    parser.add_argument("--summarizer-model", default="facebook/bart-large-cnn", 
                      help="Model to use for summarization")
    parser.add_argument("--device", choices=["cuda", "cpu"], 
                      help="Device to use (default: auto-detect)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize compressor
    compressor = SemanticCompressor(
        embedding_model=args.embedding_model,
        summarizer_model=args.summarizer_model,
        device=args.device
    )
    
    # Read input
    if os.path.exists(args.input):
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = args.input
    
    # Count original tokens
    original_tokens = count_tokens(text)
    logger.info(f"Original document: {original_tokens} tokens")
    
    # Compress text
    compressed_text = compressor.compress(text, compression_ratio=args.ratio)
    
    # Count compressed tokens
    compressed_tokens = count_tokens(compressed_text)
    logger.info(f"Compressed document: {compressed_tokens} tokens")
    logger.info(f"Compression ratio: {original_tokens/compressed_tokens:.2f}x")
    
    # Output result
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(compressed_text)
        print(f"Compressed output written to {args.output}")
    else:
        print(compressed_text)

if __name__ == "__main__":
    main()