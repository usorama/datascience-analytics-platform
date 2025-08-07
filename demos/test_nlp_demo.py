#!/usr/bin/env python3
"""
Simple NLP Enhancement Test Demo
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 80)
print("DataScience Platform - NLP Enhancement Test")
print("=" * 80)

try:
    # Test imports
    from datascience_platform.nlp import SemanticEmbedder, DomainModelSelector
    from datascience_platform.ado.semantic import SemanticScorer
    
    print("✓ Successfully imported NLP modules")
    
    # Test the enhanced embedder
    print("\n1. Testing Enhanced Semantic Embedder")
    print("-" * 40)
    
    embedder = SemanticEmbedder()
    
    # Test texts
    test_texts = [
        "Implement financial reporting dashboard with ROI metrics",
        "Enhance security compliance for vulnerability scanning",
        "Optimize database performance and query execution"
    ]
    
    print(f"Embedder type: {type(embedder).__name__}")
    print(f"Model: {getattr(embedder, 'model_name', 'Unknown')}")
    
    # Generate embeddings
    for i, text in enumerate(test_texts):
        embedding = embedder.embed_text(text)
        print(f"\nText {i+1}: '{text[:50]}...'" if len(text) > 50 else f"\nText {i+1}: '{text}'")
        print(f"  Embedding shape: {embedding.shape}")
        print(f"  Embedding sample: [{embedding[0]:.4f}, {embedding[1]:.4f}, {embedding[2]:.4f}, ...]")
    
    # Test similarity
    print("\n2. Testing Similarity Calculation")
    print("-" * 40)
    
    emb1 = embedder.embed_text(test_texts[0])
    emb2 = embedder.embed_text(test_texts[1])
    emb3 = embedder.embed_text(test_texts[0])  # Same as first
    
    sim_12 = embedder.calculate_similarity(emb1, emb2)
    sim_13 = embedder.calculate_similarity(emb1, emb3)
    
    print(f"Similarity between text 1 and 2: {sim_12:.4f}")
    print(f"Similarity between text 1 and 1 (same): {sim_13:.4f}")
    
    # Test domain selection
    print("\n3. Testing Domain Model Selection")
    print("-" * 40)
    
    selector = DomainModelSelector()
    
    for text in test_texts:
        domain, confidence = selector.detect_domain(text)
        print(f"Text: '{text[:50]}...'" if len(text) > 50 else f"Text: '{text}'")
        print(f"  Detected domain: {domain.value} (confidence: {confidence:.2f})")
    
    # Test backward compatibility
    print("\n4. Testing Backward Compatibility")
    print("-" * 40)
    
    try:
        scorer = SemanticScorer()
        print(f"SemanticScorer initialized: {type(scorer).__name__}")
        print(f"Embedder type in scorer: {type(scorer.embedder).__name__}")
    except Exception as e:
        print(f"Error initializing SemanticScorer: {e}")
    
    print("\n✅ NLP Enhancement Test Complete!")
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("\nThis might be because the transformer models are not installed.")
    print("The implementation includes graceful fallback to mock embeddings.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()