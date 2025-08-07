"""NLP Enhancement Demo

This script demonstrates the enhanced NLP capabilities including:
- Real transformer embeddings with caching
- Domain-specific model selection
- Historical risk prediction
- Vector-based similarity search
- Comprehensive text processing
"""

import logging
import time
from pathlib import Path
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Run the NLP enhancement demonstration."""
    
    print("=" * 80)
    print("DataScience Platform - NLP Enhancement Demo")
    print("=" * 80)
    
    try:
        # Import NLP modules
        from src.datascience_platform.nlp.core.embedder import SemanticEmbedder
        from src.datascience_platform.nlp.domain.model_selector import DomainModelSelector, DomainType
        from src.datascience_platform.nlp.risk.predictor import HistoricalRiskPredictor, RiskFeatures, HistoricalOutcome, RiskType
        from src.datascience_platform.nlp.vector_store.faiss_store import VectorStore
        from src.datascience_platform.nlp.utils.text_processing import TextProcessor
        from src.datascience_platform.nlp.utils.model_utils import ModelManager
        
        print("✓ Successfully imported all NLP enhancement modules")
        
    except ImportError as e:
        print(f"✗ Failed to import NLP modules: {e}")
        print("Make sure you have installed the required dependencies:")
        print("pip install -r requirements-nlp.txt")
        return
    
    # Set up demo data directory
    demo_dir = Path("demo_nlp_data")
    demo_dir.mkdir(exist_ok=True)
    
    print(f"\n📁 Using demo directory: {demo_dir}")
    
    # Sample work items for demonstration
    work_items = [
        {
            "id": "FIN-001",
            "title": "Implement quarterly financial risk assessment dashboard",
            "description": """
            Create a comprehensive dashboard for monitoring financial risks including:
            - Real-time revenue tracking and budget variance analysis
            - Investment portfolio risk metrics with VaR calculations
            - Cash flow forecasting with scenario modeling
            - Regulatory compliance monitoring for financial reporting
            
            This requires integration with external financial data APIs and complex
            risk calculation algorithms. The implementation has dependencies on
            the data warehouse team and requires security review.
            """,
            "type": "financial",
            "priority": "high",
            "team_size": 6,
            "estimated_hours": 120,
            "dependencies": ["data-warehouse", "security-team", "finance-api"]
        },
        {
            "id": "SEC-002", 
            "title": "Security vulnerability assessment and penetration testing",
            "description": """
            Conduct comprehensive security assessment including:
            - Automated vulnerability scanning of all web applications
            - Manual penetration testing of critical systems
            - Security code review of authentication mechanisms
            - Network security assessment and firewall configuration review
            
            This is a critical security initiative requiring external security
            consultants and may uncover issues requiring immediate patches.
            """,
            "type": "security",
            "priority": "critical",
            "team_size": 4,
            "estimated_hours": 80,
            "dependencies": ["external-consultant", "infrastructure-team"]
        },
        {
            "id": "TECH-003",
            "title": "Microservices architecture migration",
            "description": """
            Migrate monolithic application to microservices architecture:
            - Design service boundaries and API contracts
            - Implement service discovery and load balancing
            - Set up distributed logging and monitoring
            - Database decomposition and data migration strategies
            
            This is a complex technical transformation with significant
            architectural implications and coordination requirements.
            """,
            "type": "technical", 
            "priority": "medium",
            "team_size": 8,
            "estimated_hours": 200,
            "dependencies": ["architecture-team", "devops", "database-team"]
        },
        {
            "id": "LEG-004",
            "title": "GDPR compliance implementation for user data",
            "description": """
            Implement comprehensive GDPR compliance including:
            - User consent management system
            - Data subject rights fulfillment (access, rectification, erasure)
            - Privacy impact assessments and documentation
            - Cross-border data transfer compliance mechanisms
            
            Requires legal review and coordination with privacy office.
            Non-compliance could result in significant regulatory penalties.
            """,
            "type": "legal",
            "priority": "high", 
            "team_size": 5,
            "estimated_hours": 100,
            "dependencies": ["legal-team", "privacy-office", "data-protection-officer"]
        }
    ]
    
    # 1. Demonstrate Enhanced Semantic Embedder
    print("\n" + "="*60)
    print("1. Enhanced Semantic Embedder Demo")
    print("="*60)
    
    embedder = SemanticEmbedder(
        model_name="sentence-transformers/all-mpnet-base-v2",
        use_cache=True,
        cache_dir=demo_dir / "embeddings"
    )
    
    print(f"📊 Model Info: {embedder.get_model_info()}")
    
    # Warm up the model
    print("🔥 Warming up embedder...")
    start_time = time.time()
    embedder.warm_up()
    warmup_time = time.time() - start_time
    print(f"✓ Warmup completed in {warmup_time:.2f} seconds")
    
    # Generate embeddings for work items
    print("\n🔍 Generating embeddings for work items...")
    embeddings = {}
    
    for item in work_items:
        full_text = f"{item['title']} {item['description']}"
        
        start_time = time.time()
        embedding = embedder.embed_text(full_text, document_type=item['type'])
        embed_time = time.time() - start_time
        
        embeddings[item['id']] = embedding
        print(f"  {item['id']}: {embedding.shape} in {embed_time:.3f}s")
    
    # Test similarity
    print("\n🔗 Testing similarity between work items:")
    items_list = list(work_items)
    for i in range(len(items_list) - 1):
        item1, item2 = items_list[i], items_list[i + 1]
        similarity = embedder.calculate_similarity(embeddings[item1['id']], embeddings[item2['id']])
        print(f"  {item1['id']} ↔ {item2['id']}: {similarity:.3f}")
    
    # 2. Demonstrate Domain Model Selector
    print("\n" + "="*60)
    print("2. Domain-Specific Model Selection Demo")
    print("="*60)
    
    domain_selector = DomainModelSelector(cache_dir=demo_dir / "models")
    
    print("🎯 Available domains:")
    for domain, description, available in domain_selector.get_available_domains():
        status = "✓" if available else "✗"
        print(f"  {status} {domain.value}: {description}")
    
    print("\n🔍 Domain detection for work items:")
    for item in work_items:
        domain, confidence = domain_selector.detect_domain(item['description'], item['type'])
        model_name, selected_domain, metadata = domain_selector.select_model(
            item['description'], 
            item['type']
        )
        
        print(f"  {item['id']}: {domain.value} (confidence: {confidence:.3f})")
        print(f"    Selected model: {model_name}")
        print(f"    Keywords matched: {metadata.get('keywords_matched', [])}")
    
    # 3. Demonstrate Historical Risk Predictor  
    print("\n" + "="*60)
    print("3. Historical Risk Prediction Demo")
    print("="*60)
    
    risk_predictor = HistoricalRiskPredictor(
        data_dir=demo_dir / "risk_data",
        embedder=embedder
    )
    
    # Add some synthetic historical data
    print("📚 Adding synthetic historical outcomes...")
    
    historical_data = [
        {
            "item_id": "HIST-001",
            "planned_days": 10, "actual_days": 12,
            "planned_cost": 50000, "actual_cost": 55000,
            "quality_score": 0.85, "success": True,
            "issues": ["minor scope creep"]
        },
        {
            "item_id": "HIST-002", 
            "planned_days": 15, "actual_days": 22,
            "planned_cost": 75000, "actual_cost": 95000,
            "quality_score": 0.65, "success": False,
            "issues": ["external dependency delay", "technical complexity"]
        },
        {
            "item_id": "HIST-003",
            "planned_days": 8, "actual_days": 8,
            "planned_cost": 40000, "actual_cost": 38000,
            "quality_score": 0.95, "success": True,
            "issues": []
        }
    ]
    
    for i, hist in enumerate(historical_data):
        # Create synthetic features
        features = RiskFeatures(
            title_length=30 + i * 10,
            description_length=200 + i * 100,
            complexity_keywords=i % 3,
            uncertainty_keywords=i % 2,
            external_dependency_mentions=i % 2,
            technical_debt_indicators=0,
            semantic_similarity_to_past_issues=0.1 + i * 0.2,
            domain_confidence=0.7 + i * 0.1,
            team_size=4 + i,
            estimated_hours=hist['planned_days'] * 8,
            priority_score=0.5 + i * 0.2,
            dependency_count=i + 1,
            team_velocity=1.0,
            similar_item_success_rate=0.8,
            recent_team_performance=0.8
        )
        
        outcome = HistoricalOutcome(
            item_id=hist['item_id'],
            features=features,
            actual_duration_days=hist['actual_days'],
            planned_duration_days=hist['planned_days'],
            actual_cost=hist['actual_cost'],
            planned_cost=hist['planned_cost'],
            quality_score=hist['quality_score'],
            success=hist['success'],
            completion_date=datetime.now() - timedelta(days=(i + 1) * 30),
            issues_encountered=hist['issues'],
            risk_type=RiskType.SCHEDULE_DELAY
        )
        
        risk_predictor.add_historical_outcome(outcome)
    
    print(f"✓ Added {len(historical_data)} historical outcomes")
    
    # Train models
    print("🎯 Training risk prediction models...")
    risk_predictor.train_models()
    
    # Make predictions for current work items
    print("\n🔮 Risk predictions for current work items:")
    
    for item in work_items[:2]:  # Predict for first 2 items
        predictions = risk_predictor.predict_risk(
            title=item['title'],
            description=item['description'],
            team_size=item['team_size'],
            estimated_hours=item['estimated_hours'],
            priority=item['priority'],
            dependencies=item['dependencies']
        )
        
        print(f"\n  {item['id']}: {item['title'][:50]}...")
        for pred in predictions:
            print(f"    {pred.risk_type.value}: {pred.probability:.3f} prob, {pred.severity:.3f} severity, {pred.confidence:.3f} conf")
            if pred.recommended_actions:
                print(f"      Recommendations: {', '.join(pred.recommended_actions[:2])}")
    
    # 4. Demonstrate Vector Store
    print("\n" + "="*60)
    print("4. Vector Store and Similarity Search Demo")
    print("="*60)
    
    vector_store = VectorStore(
        dimension=embeddings[work_items[0]['id']].shape[0],
        index_type="flat",
        cache_dir=demo_dir / "vectors"
    )
    
    print("💾 Storing work item embeddings in vector database...")
    
    for item in work_items:
        success = vector_store.add_vector(
            doc_id=item['id'],
            vector=embeddings[item['id']],
            metadata={
                'title': item['title'],
                'type': item['type'],
                'priority': item['priority'],
                'team_size': item['team_size'],
                'estimated_hours': item['estimated_hours']
            }
        )
        print(f"  {item['id']}: {'✓' if success else '✗'}")
    
    # Test similarity search
    print("\n🔍 Similarity search demo:")
    
    search_queries = [
        "financial risk management and budget analysis",
        "security vulnerabilities and penetration testing",
        "technical architecture and system design"
    ]
    
    for query in search_queries:
        print(f"\n  Query: '{query}'")
        
        query_embedding = embedder.embed_text(query)
        results = vector_store.search(query_embedding, k=2, include_metadata=True)
        
        for doc_id, similarity, metadata in results:
            print(f"    {doc_id}: {similarity:.3f} - {metadata['title'][:60]}...")
    
    # 5. Demonstrate Text Processing
    print("\n" + "="*60)
    print("5. Advanced Text Processing Demo") 
    print("="*60)
    
    text_processor = TextProcessor(
        use_lemmatization=True,
        remove_stopwords=True,
        min_word_length=3
    )
    
    sample_text = work_items[0]['description']
    print(f"📝 Processing sample text ({len(sample_text)} characters)...")
    
    processed = text_processor.process_text(
        sample_text,
        return_tokens=True,
        return_sentences=True,
        remove_urls=True,
        remove_special_chars=True
    )
    
    print(f"  Original tokens: {processed['token_count_before']}")
    print(f"  Processed tokens: {processed['token_count_after']}")
    print(f"  Reduction: {processed['reduction_percentage']:.1f}%")
    print(f"  Sentences: {len(processed['sentences'])}")
    print(f"  Sample tokens: {processed['tokens'][:10]}")
    
    # Extract keywords
    keywords = text_processor.extract_keywords(sample_text, max_keywords=5)
    print(f"  Keywords: {[kw for kw, score in keywords]}")
    
    # 6. Demonstrate Model Management
    print("\n" + "="*60)
    print("6. Model Management and Performance Demo")
    print("="*60)
    
    model_manager = ModelManager(
        cache_dir=demo_dir / "model_cache",
        enable_monitoring=True
    )
    
    # Register models
    model_manager.register_model("embedder", embedder, {"type": "sentence-transformer"})
    model_manager.register_model("domain_selector", domain_selector, {"type": "domain-classifier"})
    model_manager.register_model("risk_predictor", risk_predictor, {"type": "ml-predictor"})
    
    # Simulate some operations with timing
    print("⏱️  Running timed operations...")
    
    test_texts = [item['title'] for item in work_items]
    
    with model_manager.time_inference("embedder"):
        batch_embeddings = embedder.embed_texts(test_texts)
    
    print(f"✓ Batch embedded {len(test_texts)} texts: {batch_embeddings.shape}")
    
    # Get comprehensive statistics
    print("\n📊 Final Statistics:")
    
    all_stats = model_manager.get_all_stats()
    
    print("  Embedder stats:")
    embedder_stats = embedder.get_stats()
    for key, value in embedder_stats.items():
        if isinstance(value, (int, float)):
            print(f"    {key}: {value}")
    
    print("  Vector store stats:")
    vector_stats = vector_store.get_stats()
    for key, value in vector_stats.items():
        if isinstance(value, (int, float, str, bool)):
            print(f"    {key}: {value}")
    
    print("  Text processor stats:")
    processor_stats = text_processor.get_stats()
    for key, value in processor_stats.items():
        print(f"    {key}: {value}")
    
    # 7. End-to-End Workflow Demo
    print("\n" + "="*60)
    print("7. End-to-End Workflow Demo")
    print("="*60)
    
    print("🔄 Running complete NLP pipeline on new work item...")
    
    new_item = {
        "id": "NEW-001",
        "title": "AI-powered customer service chatbot implementation",
        "description": """
        Develop and deploy an intelligent customer service chatbot using
        natural language processing and machine learning. The system should
        handle common customer inquiries, escalate complex issues to human
        agents, and integrate with existing CRM and knowledge base systems.
        This is a strategic initiative requiring careful AI/ML model selection
        and extensive testing to ensure customer satisfaction.
        """,
        "type": "technical",
        "priority": "high"
    }
    
    # Complete pipeline
    pipeline_start = time.time()
    
    # 1. Text processing
    processed_text = text_processor.process_text(new_item['description'])
    
    # 2. Domain detection
    domain, domain_conf = domain_selector.detect_domain(new_item['description'], new_item['type'])
    
    # 3. Embedding generation
    embedding = embedder.embed_text(f"{new_item['title']} {new_item['description']}")
    
    # 4. Risk prediction
    risk_features = risk_predictor.extract_features(
        new_item['title'], 
        new_item['description'],
        priority=new_item['priority']
    )
    
    # 5. Similar item search
    similar_items = vector_store.search(embedding, k=3, include_metadata=True)
    
    # 6. Store new item
    vector_store.add_vector(
        new_item['id'],
        embedding,
        {
            'title': new_item['title'],
            'type': new_item['type'],
            'priority': new_item['priority'],
            'domain': domain.value,
            'domain_confidence': domain_conf
        }
    )
    
    pipeline_time = time.time() - pipeline_start
    
    print(f"✓ Pipeline completed in {pipeline_time:.3f} seconds")
    print(f"  Detected domain: {domain.value} (confidence: {domain_conf:.3f})")
    print(f"  Processed tokens: {processed_text['token_count_after']}")
    print(f"  Embedding shape: {embedding.shape}")
    print(f"  Risk features extracted: {len(vars(risk_features))} features")
    
    print(f"\n  Most similar existing items:")
    for doc_id, similarity, metadata in similar_items:
        print(f"    {doc_id}: {similarity:.3f} - {metadata['title'][:50]}...")
    
    print("\n" + "="*80)
    print("🎉 NLP Enhancement Demo Completed Successfully!")
    print("="*80)
    
    print("\nKey capabilities demonstrated:")
    print("✓ Production-ready semantic embeddings with caching")
    print("✓ Domain-specific model selection and routing")
    print("✓ ML-based historical risk prediction")
    print("✓ Efficient vector similarity search")
    print("✓ Advanced text processing and keyword extraction")
    print("✓ Comprehensive model management and monitoring")
    print("✓ End-to-end integrated NLP pipeline")
    
    print(f"\n📁 Demo data saved to: {demo_dir}")
    print("You can explore the cached models, embeddings, and data files.")


if __name__ == "__main__":
    main()