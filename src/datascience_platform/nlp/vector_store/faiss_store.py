"""FAISS-based Vector Store Implementation

This module provides efficient vector storage and retrieval using Facebook AI Similarity Search (FAISS).
Supports hybrid search, metadata filtering, and scalable similarity operations.
"""

import json
import pickle
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

# Try importing FAISS with graceful fallback
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("FAISS not available. Install with: pip install faiss-cpu or faiss-gpu")

try:
    import pickle
    PICKLE_AVAILABLE = True
except ImportError:
    PICKLE_AVAILABLE = False


class MockFAISS:
    """Mock FAISS implementation for when library is not available."""
    
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.vectors = []
        self.is_trained = True
        self.ntotal = 0
    
    def add(self, vectors: np.ndarray):
        """Add vectors to the mock index."""
        if len(vectors.shape) == 1:
            vectors = vectors.reshape(1, -1)
        
        for vector in vectors:
            self.vectors.append(vector)
        
        self.ntotal = len(self.vectors)
    
    def search(self, query_vectors: np.ndarray, k: int) -> Tuple[np.ndarray, np.ndarray]:
        """Search for similar vectors using cosine similarity."""
        if len(query_vectors.shape) == 1:
            query_vectors = query_vectors.reshape(1, -1)
        
        all_distances = []
        all_indices = []
        
        for query in query_vectors:
            distances = []
            indices = []
            
            for i, stored_vector in enumerate(self.vectors):
                # Calculate cosine similarity
                dot_product = np.dot(query, stored_vector)
                norm_query = np.linalg.norm(query)
                norm_stored = np.linalg.norm(stored_vector)
                
                if norm_query > 0 and norm_stored > 0:
                    similarity = dot_product / (norm_query * norm_stored)
                    # Convert to distance (lower is better)
                    distance = 1.0 - similarity
                else:
                    distance = 2.0  # Maximum distance for zero vectors
                
                distances.append(distance)
                indices.append(i)
            
            # Sort by distance and get top k
            sorted_pairs = sorted(zip(distances, indices))
            top_k = sorted_pairs[:k]
            
            top_distances = [d for d, _ in top_k]
            top_indices = [i for _, i in top_k]
            
            # Pad with -1 if not enough results
            while len(top_distances) < k:
                top_distances.append(float('inf'))
                top_indices.append(-1)
            
            all_distances.append(top_distances)
            all_indices.append(top_indices)
        
        return np.array(all_distances), np.array(all_indices)
    
    def train(self, vectors: np.ndarray):
        """Mock training - no-op."""
        pass


class VectorStore:
    """FAISS-based vector store with metadata support and hybrid search."""
    
    def __init__(
        self,
        dimension: int = 768,
        index_type: str = "flat",
        cache_dir: Optional[Path] = None,
        metric_type: str = "cosine"
    ):
        """Initialize the vector store.
        
        Args:
            dimension: Dimension of the vectors
            index_type: Type of FAISS index ("flat", "ivf", "hnsw")
            cache_dir: Directory for persistent storage
            metric_type: Distance metric ("cosine", "euclidean", "inner_product")
        """
        self.dimension = dimension
        self.index_type = index_type
        self.metric_type = metric_type
        
        self.cache_dir = cache_dir or Path.home() / ".cache" / "ds_platform_vectors"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize FAISS index
        self.index = self._create_index()
        
        # Metadata storage
        self.id_to_index: Dict[str, int] = {}  # Document ID to FAISS index mapping
        self.index_to_id: Dict[int, str] = {}  # FAISS index to document ID mapping
        self.metadata: Dict[str, Dict[str, Any]] = {}  # Document metadata
        
        # Vector storage for mock implementation
        self.vectors: Dict[str, np.ndarray] = {}
        
        # Statistics
        self.stats = {
            'total_vectors': 0,
            'searches_performed': 0,
            'vectors_added': 0,
            'cache_hits': 0
        }
        
        # Load existing data
        self._load_persistent_data()
    
    def _create_index(self):
        """Create and configure FAISS index."""
        if not FAISS_AVAILABLE:
            logger.warning("Using mock FAISS implementation")
            return MockFAISS(self.dimension)
        
        if self.metric_type == "cosine":
            # For cosine similarity, we use inner product with normalized vectors
            if self.index_type == "flat":
                index = faiss.IndexFlatIP(self.dimension)
            elif self.index_type == "ivf":
                quantizer = faiss.IndexFlatIP(self.dimension)
                index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)  # 100 centroids
            elif self.index_type == "hnsw":
                index = faiss.IndexHNSWFlat(self.dimension, 32)  # M=32
                index.hnsw.efSearch = 64
            else:
                logger.warning(f"Unknown index type {self.index_type}, using flat")
                index = faiss.IndexFlatIP(self.dimension)
        
        elif self.metric_type == "euclidean":
            if self.index_type == "flat":
                index = faiss.IndexFlatL2(self.dimension)
            elif self.index_type == "ivf":
                quantizer = faiss.IndexFlatL2(self.dimension)
                index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
            elif self.index_type == "hnsw":
                index = faiss.IndexHNSWFlat(self.dimension, 32)
                index.metric_type = faiss.METRIC_L2
            else:
                index = faiss.IndexFlatL2(self.dimension)
        
        else:  # inner_product
            if self.index_type == "flat":
                index = faiss.IndexFlatIP(self.dimension)
            else:
                index = faiss.IndexFlatIP(self.dimension)
        
        logger.info(f"Created FAISS index: {self.index_type} with {self.metric_type} metric")
        return index
    
    def add_vector(
        self,
        doc_id: str,
        vector: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a vector to the store.
        
        Args:
            doc_id: Unique document identifier
            vector: Vector to add
            metadata: Optional metadata dictionary
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            # Validate vector
            if vector.shape[0] != self.dimension:
                logger.error(f"Vector dimension {vector.shape[0]} doesn't match expected {self.dimension}")
                return False
            
            # Normalize vector for cosine similarity
            if self.metric_type == "cosine":
                norm = np.linalg.norm(vector)
                if norm > 0:
                    vector = vector / norm
            
            # Check if document already exists
            if doc_id in self.id_to_index:
                logger.warning(f"Document {doc_id} already exists, updating...")
                return self.update_vector(doc_id, vector, metadata)
            
            # Add to FAISS index
            vector_array = vector.reshape(1, -1).astype(np.float32)
            
            if FAISS_AVAILABLE and not isinstance(self.index, MockFAISS):
                # Train index if needed (for IVF)
                if hasattr(self.index, 'is_trained') and not self.index.is_trained:
                    if self.stats['total_vectors'] >= 100:  # Need enough data to train
                        training_vectors = np.array([v for v in self.vectors.values()])
                        self.index.train(training_vectors.astype(np.float32))
                
                self.index.add(vector_array)
                faiss_index = self.index.ntotal - 1
            else:
                self.index.add(vector_array)
                faiss_index = len(self.vectors)
            
            # Update mappings
            self.id_to_index[doc_id] = faiss_index
            self.index_to_id[faiss_index] = doc_id
            self.vectors[doc_id] = vector
            
            # Store metadata
            if metadata:
                self.metadata[doc_id] = metadata.copy()
            
            # Update statistics
            self.stats['total_vectors'] += 1
            self.stats['vectors_added'] += 1
            
            logger.debug(f"Added vector for document: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding vector for {doc_id}: {e}")
            return False
    
    def add_vectors_batch(
        self,
        doc_ids: List[str],
        vectors: np.ndarray,
        metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> List[bool]:
        """Add multiple vectors efficiently.
        
        Args:
            doc_ids: List of document identifiers
            vectors: 2D array of vectors (n_vectors x dimension)
            metadata_list: Optional list of metadata dictionaries
            
        Returns:
            List of boolean success indicators
        """
        if len(doc_ids) != vectors.shape[0]:
            raise ValueError("Number of doc_ids must match number of vectors")
        
        if metadata_list and len(metadata_list) != len(doc_ids):
            raise ValueError("Number of metadata items must match number of doc_ids")
        
        results = []
        
        try:
            # Normalize vectors for cosine similarity
            if self.metric_type == "cosine":
                norms = np.linalg.norm(vectors, axis=1, keepdims=True)
                norms[norms == 0] = 1  # Avoid division by zero
                vectors = vectors / norms
            
            # Convert to float32 for FAISS
            vectors = vectors.astype(np.float32)
            
            # Train index if needed
            if FAISS_AVAILABLE and not isinstance(self.index, MockFAISS):
                if hasattr(self.index, 'is_trained') and not self.index.is_trained:
                    if len(vectors) >= 100 or self.stats['total_vectors'] + len(vectors) >= 100:
                        self.index.train(vectors)
                
                # Add all vectors at once
                start_index = self.index.ntotal
                self.index.add(vectors)
                
                # Update mappings
                for i, doc_id in enumerate(doc_ids):
                    faiss_index = start_index + i
                    self.id_to_index[doc_id] = faiss_index
                    self.index_to_id[faiss_index] = doc_id
                    self.vectors[doc_id] = vectors[i]
                    
                    if metadata_list and i < len(metadata_list):
                        self.metadata[doc_id] = metadata_list[i].copy()
                    
                    results.append(True)
            else:
                # Mock implementation - add one by one
                for i, doc_id in enumerate(doc_ids):
                    metadata = metadata_list[i] if metadata_list and i < len(metadata_list) else None
                    success = self.add_vector(doc_id, vectors[i], metadata)
                    results.append(success)
            
            # Update statistics
            successful_adds = sum(results)
            self.stats['total_vectors'] += successful_adds
            self.stats['vectors_added'] += successful_adds
            
            logger.info(f"Added {successful_adds}/{len(doc_ids)} vectors successfully")
            
        except Exception as e:
            logger.error(f"Error in batch vector addition: {e}")
            results = [False] * len(doc_ids)
        
        return results
    
    def search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[Tuple[str, float, Optional[Dict[str, Any]]]]:
        """Search for similar vectors.
        
        Args:
            query_vector: Query vector
            k: Number of results to return
            filter_metadata: Metadata filters to apply
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of (doc_id, similarity_score, metadata) tuples
        """
        try:
            if self.stats['total_vectors'] == 0:
                return []
            
            # Normalize query vector for cosine similarity
            if self.metric_type == "cosine":
                norm = np.linalg.norm(query_vector)
                if norm > 0:
                    query_vector = query_vector / norm
            
            # Prepare query
            query_array = query_vector.reshape(1, -1).astype(np.float32)
            
            # Search in FAISS
            # Use larger k for filtering if needed
            search_k = k * 3 if filter_metadata else k
            distances, indices = self.index.search(query_array, min(search_k, self.stats['total_vectors']))
            
            # Process results
            results = []
            for i in range(len(indices[0])):
                idx = indices[0][i]
                distance = distances[0][i]
                
                # Skip invalid indices
                if idx == -1 or idx not in self.index_to_id:
                    continue
                
                doc_id = self.index_to_id[idx]
                
                # Convert distance to similarity score
                if self.metric_type == "cosine":
                    similarity = 1.0 - distance  # For inner product with normalized vectors
                elif self.metric_type == "euclidean":
                    similarity = 1.0 / (1.0 + distance)  # Convert to similarity
                else:  # inner_product
                    similarity = distance
                
                # Apply metadata filtering
                if filter_metadata:
                    doc_metadata = self.metadata.get(doc_id, {})
                    if not self._matches_filter(doc_metadata, filter_metadata):
                        continue
                
                # Prepare metadata for result
                result_metadata = None
                if include_metadata:
                    result_metadata = self.metadata.get(doc_id, {}).copy()
                
                results.append((doc_id, float(similarity), result_metadata))
                
                # Stop when we have enough results
                if len(results) >= k:
                    break
            
            self.stats['searches_performed'] += 1
            return results
            
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            return []
    
    def _matches_filter(self, metadata: Dict[str, Any], filter_criteria: Dict[str, Any]) -> bool:
        """Check if metadata matches filter criteria."""
        for key, expected_value in filter_criteria.items():
            if key not in metadata:
                return False
            
            actual_value = metadata[key]
            
            # Handle different types of filtering
            if isinstance(expected_value, list):
                # Value must be in the list
                if actual_value not in expected_value:
                    return False
            elif isinstance(expected_value, dict):
                # Range filtering (e.g., {'min': 0, 'max': 100})
                if 'min' in expected_value and actual_value < expected_value['min']:
                    return False
                if 'max' in expected_value and actual_value > expected_value['max']:
                    return False
            else:
                # Exact match
                if actual_value != expected_value:
                    return False
        
        return True
    
    def update_vector(
        self,
        doc_id: str,
        vector: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update an existing vector.
        
        Args:
            doc_id: Document identifier
            vector: New vector
            metadata: New metadata
            
        Returns:
            True if updated successfully
        """
        if doc_id not in self.id_to_index:
            logger.warning(f"Document {doc_id} not found for update")
            return self.add_vector(doc_id, vector, metadata)
        
        try:
            # For simplicity, we'll remove and re-add
            # In production, you might want to implement in-place updates
            self.remove_vector(doc_id)
            return self.add_vector(doc_id, vector, metadata)
            
        except Exception as e:
            logger.error(f"Error updating vector for {doc_id}: {e}")
            return False
    
    def remove_vector(self, doc_id: str) -> bool:
        """Remove a vector from the store.
        
        Note: FAISS doesn't support removal, so we mark as deleted.
        Consider rebuilding the index periodically.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            True if removed successfully
        """
        if doc_id not in self.id_to_index:
            return False
        
        try:
            # Remove from mappings and metadata
            faiss_index = self.id_to_index[doc_id]
            del self.id_to_index[doc_id]
            del self.index_to_id[faiss_index]
            
            if doc_id in self.vectors:
                del self.vectors[doc_id]
            
            if doc_id in self.metadata:
                del self.metadata[doc_id]
            
            self.stats['total_vectors'] -= 1
            
            logger.debug(f"Removed vector for document: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing vector for {doc_id}: {e}")
            return False
    
    def get_vector(self, doc_id: str) -> Optional[np.ndarray]:
        """Get vector for a document.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Vector if found, None otherwise
        """
        return self.vectors.get(doc_id)
    
    def get_metadata(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a document.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Metadata if found, None otherwise
        """
        return self.metadata.get(doc_id, {}).copy()
    
    def list_documents(self) -> List[str]:
        """Get list of all document IDs."""
        return list(self.id_to_index.keys())
    
    def clear(self):
        """Clear all vectors and metadata."""
        self.index = self._create_index()
        self.id_to_index.clear()
        self.index_to_id.clear()
        self.vectors.clear()
        self.metadata.clear()
        
        self.stats['total_vectors'] = 0
        
        logger.info("Cleared vector store")
    
    def save(self, filepath: Optional[Union[str, Path]] = None):
        """Save vector store to disk.
        
        Args:
            filepath: Optional custom filepath (string or Path)
        """
        if not filepath:
            filepath = self.cache_dir / "vector_store.pkl"
        else:
            filepath = Path(filepath) if isinstance(filepath, str) else filepath
        
        try:
            data = {
                'id_to_index': self.id_to_index,
                'index_to_id': self.index_to_id,
                'vectors': self.vectors,
                'metadata': self.metadata,
                'stats': self.stats,
                'dimension': self.dimension,
                'index_type': self.index_type,
                'metric_type': self.metric_type
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
            
            # Save FAISS index separately
            if FAISS_AVAILABLE and not isinstance(self.index, MockFAISS):
                index_file = filepath.with_suffix('.faiss')
                faiss.write_index(self.index, str(index_file))
            
            logger.info(f"Saved vector store to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
    
    @classmethod
    def load(cls, filepath: Union[str, Path], dimension: Optional[int] = None) -> 'VectorStore':
        """Load vector store from disk.
        
        Args:
            filepath: Path to the saved vector store
            dimension: Optional dimension (will be determined from loaded data if not provided)
            
        Returns:
            Loaded VectorStore instance
        """
        filepath = Path(filepath) if isinstance(filepath, str) else filepath
        
        if not filepath.exists():
            raise FileNotFoundError(f"Vector store not found at {filepath}")
        
        # Load the pickle file
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        # Determine dimension from loaded vectors if not provided
        if dimension is None:
            if data.get('vectors'):
                first_vector = next(iter(data['vectors'].values()))
                dimension = len(first_vector)
            else:
                dimension = 768  # Default dimension
        
        # Create new instance
        instance = cls(dimension=dimension)
        
        # Restore state
        instance.id_to_index = data.get('id_to_index', {})
        instance.index_to_id = data.get('index_to_id', {})
        instance.vectors = data.get('vectors', {})
        instance.metadata = data.get('metadata', {})
        instance.stats = data.get('stats', instance.stats)
        
        # Load FAISS index
        index_file = filepath.with_suffix('.faiss')
        if FAISS_AVAILABLE and index_file.exists():
            instance.index = faiss.read_index(str(index_file))
            logger.info(f"Loaded FAISS index from {index_file}")
        else:
            # Rebuild index from vectors
            if instance.vectors:
                logger.info("Rebuilding FAISS index from vectors")
                instance._rebuild_index()
        
        logger.info(f"Loaded vector store with {len(instance.vectors)} vectors")
        return instance
    
    def _rebuild_index(self):
        """Rebuild FAISS index from stored vectors."""
        self.index = self._create_index()
        
        if not self.vectors:
            return
        
        # Prepare vectors for batch addition
        doc_ids = list(self.vectors.keys())
        vectors = np.array([self.vectors[doc_id] for doc_id in doc_ids])
        
        # Clear existing mappings
        self.id_to_index.clear()
        self.index_to_id.clear()
        
        # Add vectors
        success = self.add_vectors_batch(doc_ids, vectors)
        successful_count = sum(success)
        
        logger.info(f"Rebuilt index with {successful_count}/{len(doc_ids)} vectors")
    
    def _load_persistent_data(self):
        """Load persistent data on initialization if it exists."""
        default_path = self.cache_dir / "vector_store.pkl"
        if default_path.exists():
            try:
                with open(default_path, 'rb') as f:
                    data = pickle.load(f)
                
                self.id_to_index = data.get('id_to_index', {})
                self.index_to_id = data.get('index_to_id', {})
                self.vectors = data.get('vectors', {})
                self.metadata = data.get('metadata', {})
                self.stats = data.get('stats', self.stats)
                
                # Load FAISS index
                index_file = default_path.with_suffix('.faiss')
                if FAISS_AVAILABLE and index_file.exists():
                    self.index = faiss.read_index(str(index_file))
                    logger.info(f"Loaded FAISS index from {index_file}")
                else:
                    # Rebuild index from vectors
                    if self.vectors:
                        logger.info("Rebuilding FAISS index from vectors")
                        self._rebuild_index()
                
                logger.info(f"Loaded persistent vector store with {len(self.vectors)} vectors")
            except Exception as e:
                logger.warning(f"Could not load persistent data: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        return {
            **self.stats,
            'index_type': self.index_type,
            'metric_type': self.metric_type,
            'dimension': self.dimension,
            'faiss_available': FAISS_AVAILABLE,
            'cache_directory': str(self.cache_dir)
        }