#!/usr/bin/env python3
"""
Verification script for token limit solution.
Tests the token management system with inputs that would exceed context limits.
"""

import os
import sys
import time
import logging
import random
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "logs/token_verification.log"))
    ]
)
logger = logging.getLogger("token-verification")

# Add paths
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_SOLUTIONS_DIR = os.path.join(WORKSPACE_DIR, "token_solutions")
SERVICES_DIR = os.path.join(WORKSPACE_DIR, "services")

sys.path.append(TOKEN_SOLUTIONS_DIR)
sys.path.append(SERVICES_DIR)

def generate_large_document(target_tokens=190000):
    """Generate a document with approximately the target number of tokens"""
    logger.info(f"Generating document with ~{target_tokens} tokens")
    
    paragraphs = []
    base_paragraph = """
    Large language models (LLMs) have revolutionized natural language processing, enabling sophisticated 
    text generation, translation, and understanding capabilities. These models use attention mechanisms 
    that scale quadratically with input length, creating computational challenges. When context windows 
    fill up with too much information, the model can lose track of important earlier details, leading to 
    reduced coherence and accuracy in responses. To address this limitation, semantic compression techniques 
    can be applied to reduce redundancy while preserving key information, enabling significantly longer 
    effective context within existing model constraints. This approach maintains the essential meaning of 
    the input while reducing the token count required to represent it.
    
    The architectural design of transformer-based models creates inherent limitations on context length.
    Self-attention mechanisms require each token to attend to all other tokens, creating an O(n²) computational
    complexity that becomes prohibitive for very long sequences. As a result, most models have hard limits
    on their maximum context window size. When these limits are reached, important information may be lost
    or fragmented, affecting the quality and consistency of model outputs.
    
    Various strategies have been developed to address these constraints, including sliding window approaches,
    hierarchical attention mechanisms, and memory-augmented architectures. However, semantic compression
    represents a particularly effective approach because it operates on the content itself rather than
    the model architecture. By identifying and eliminating redundancies while preserving meaning, it enables
    significantly more information to be packed into the available context window.
    """
    
    # Add variations to avoid exact repetition
    variations = [
        "Transformer-based language models",
        "Neural language architectures",
        "Foundation models",
        "Modern AI language systems",
        "Large-scale neural networks",
        "Deep learning language models",
        "GPT-style architectures",
        "Contemporary language processors",
        "Advanced neural language models",
        "State-of-the-art AI systems"
    ]
    
    topics = [
        "context length limitations",
        "token optimization strategies",
        "semantic compression techniques",
        "memory efficiency approaches",
        "information density challenges",
        "attention mechanism constraints",
        "computational complexity issues",
        "model architecture considerations",
        "input processing optimizations",
        "resource utilization improvements"
    ]
    
    # Generate enough paragraphs to reach target token count
    tokens_so_far = 0
    paragraph_count = 0
    
    while tokens_so_far < target_tokens:
        # Create a variation of the paragraph
        variation = random.choice(variations)
        topic = random.choice(topics)
        
        paragraph = base_paragraph.replace("Large language models (LLMs)", variation)
        paragraph = paragraph.replace("context length", topic)
        
        # Add some random additional sentences for variety
        additional_sentences = [
            f"The implications of this approach extend to {random.choice(['enterprise', 'research', 'educational', 'creative', 'technical'])} applications.",
            f"Ongoing research continues to improve {random.choice(['efficiency', 'accuracy', 'reliability', 'scalability'])} of these methods.",
            f"Implementation requires careful consideration of {random.choice(['trade-offs', 'computational resources', 'latency requirements', 'accuracy metrics'])}.",
            f"User experience can be significantly enhanced through {random.choice(['thoughtful design', 'appropriate model selection', 'optimized processing', 'intelligent caching'])}.",
            f"The future of this technology points toward {random.choice(['greater autonomy', 'increased personalization', 'improved reasoning', 'enhanced multimodal capabilities'])}."
        ]
        
        for _ in range(random.randint(1, 3)):
            paragraph += " " + random.choice(additional_sentences)
        
        paragraphs.append(paragraph)
        paragraph_count += 1
        
        # Estimate tokens (rough approximation)
        tokens_so_far = len(" ".join(paragraphs)) // 4
        
        if paragraph_count % 10 == 0:
            logger.info(f"Generated {paragraph_count} paragraphs, ~{tokens_so_far} tokens")
    
    document = "\n\n".join(paragraphs)
    logger.info(f"Generated document with {len(document)} characters, ~{len(document) // 4} tokens")
    
    return document

def verify_compression():
    """Test the semantic compression component"""
    logger.info("Testing semantic compression")
    
    try:
        # Import from token_solutions
        from token_solutions import compress_text, count_tokens
        
        # Generate test document
        document = generate_large_document(target_tokens=190000)
        token_count = count_tokens(document)
        
        logger.info(f"Original document: {token_count} tokens")
        
        # Compress the document
        start_time = time.time()
        compressed = compress_text(document)
        elapsed_time = time.time() - start_time
        
        compressed_tokens = count_tokens(compressed)
        compression_ratio = token_count / compressed_tokens if compressed_tokens > 0 else 0
        
        logger.info(f"Compressed document: {compressed_tokens} tokens")
        logger.info(f"Compression ratio: {compression_ratio:.2f}x")
        logger.info(f"Compression time: {elapsed_time:.2f} seconds")
        
        # Verify the compressed document is below context limit
        if compressed_tokens < 100000:
            logger.info("PASS: Compression reduced document below context limit")
            return True
        else:
            logger.error(f"FAIL: Compressed document still exceeds limit ({compressed_tokens} tokens)")
            return False
    
    except Exception as e:
        logger.error(f"Error testing compression: {e}")
        return False

def verify_wrapper_integration():
    """Test the OpenAI wrapper integration"""
    logger.info("Testing OpenAI wrapper integration")
    
    try:
        # Import the wrapper
        from openai_wrapper import OpenAI
        
        # Create a client
        client = OpenAI()
        
        # Generate test document (smaller for API testing)
        document = generate_large_document(target_tokens=10000)
        
        # Test the client
        logger.info("Making API request through wrapper")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": document}],
            max_tokens=100
        )
        
        if response and hasattr(response, 'choices') and response.choices:
            logger.info("PASS: Successfully made API request through wrapper")
            logger.info(f"Response: {response.choices[0].message.content[:100]}...")
            return True
        else:
            logger.error("FAIL: API request failed or returned unexpected response")
            return False
    
    except Exception as e:
        logger.error(f"Error testing wrapper integration: {e}")
        return False

def verify_real_use_case():
    """Test the reported use case that's failing"""
    logger.info("Testing reported failing use case (187K tokens + 18K max_tokens)")
    
    try:
        # Import the wrapper
        from openai_wrapper import OpenAI
        
        # Create a client
        client = OpenAI()
        
        # Generate test document matching the reported size
        document = generate_large_document(target_tokens=187000)
        
        # Test the client with the reported max_tokens
        logger.info("Making API request with 187K tokens + 18K max_tokens")
        response = client.chat.completions.create(
            model="gpt-4",  # Use GPT-4 to match likely real use case
            messages=[{"role": "user", "content": document}],
            max_tokens=18000
        )
        
        if response and hasattr(response, 'choices') and response.choices:
            logger.info("PASS: Successfully handled 187K + 18K token request")
            logger.info(f"Response: {response.choices[0].message.content[:100]}...")
            return True
        else:
            logger.error("FAIL: Large token request failed or returned unexpected response")
            return False
    
    except Exception as e:
        logger.error(f"Error testing large token request: {e}")
        return False

def save_document_for_debug(size=187000):
    """Generate and save a test document for debugging"""
    document = generate_large_document(target_tokens=size)
    
    from token_solutions import count_tokens
    actual_tokens = count_tokens(document)
    
    output_path = os.path.join(WORKSPACE_DIR, f"test_document_{actual_tokens}_tokens.txt")
    with open(output_path, 'w') as f:
        f.write(document)
    
    logger.info(f"Saved test document with {actual_tokens} tokens to {output_path}")
    return output_path

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Verify token limit solution")
    parser.add_argument("--skip-compression", action="store_true", help="Skip compression test")
    parser.add_argument("--skip-wrapper", action="store_true", help="Skip wrapper test")
    parser.add_argument("--skip-use-case", action="store_true", help="Skip reported use case test")
    parser.add_argument("--save-document", action="store_true", help="Save test document")
    
    args = parser.parse_args()
    
    logger.info("Starting token limit solution verification")
    
    results = []
    
    if args.save_document:
        save_document_for_debug()
    
    if not args.skip_compression:
        compression_result = verify_compression()
        results.append(("Semantic Compression", compression_result))
    
    if not args.skip_wrapper:
        wrapper_result = verify_wrapper_integration()
        results.append(("Wrapper Integration", wrapper_result))
    
    if not args.skip_use_case:
        use_case_result = verify_real_use_case()
        results.append(("Reported Use Case", use_case_result))
    
    # Print summary
    logger.info("Verification Results:")
    all_passed = True
    
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        logger.info(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        logger.info("All tests passed! Token solution is working correctly.")
    else:
        logger.error("Some tests failed. Token solution may need adjustments.")

if __name__ == "__main__":
    main()