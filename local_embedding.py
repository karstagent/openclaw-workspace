import torch
from sentence_transformers import SentenceTransformer

class LocalEmbedder:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
    
    def embed_text(self, texts):
        """
        Generate embeddings for input texts
        
        Args:
            texts (list or str): Text(s) to embed
        
        Returns:
            numpy array of embeddings
        """
        return self.model.encode(texts)
    
    def semantic_search(self, query, corpus, top_k=5):
        """
        Perform semantic search
        
        Args:
            query (str): Search query
            corpus (list): List of texts to search
            top_k (int): Number of top results to return
        
        Returns:
            List of top k most similar texts
        """
        query_embedding = self.embed_text(query)
        corpus_embeddings = self.embed_text(corpus)
        
        # Compute cosine similarities
        similarities = torch.nn.functional.cosine_similarity(
            torch.tensor(query_embedding), 
            torch.tensor(corpus_embeddings)
        )
        
        # Get top k results
        top_results = similarities.topk(min(top_k, len(corpus)))
        return [corpus[idx] for idx in top_results.indices]

# Example usage
if __name__ == '__main__':
    embedder = LocalEmbedder()
    
    corpus = [
        "Machine learning is fascinating",
        "AI is changing the world",
        "Deep learning requires large datasets",
        "Natural language processing is complex"
    ]
    
    query = "Tell me about artificial intelligence"
    results = embedder.semantic_search(query, corpus)
    
    print("Search Results:")
    for result in results:
        print(result)