#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Intelligent Model Selector - Embedding-based model selection
Uses embedding similarity matching against model descriptions and metadata
"""

import logging
import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

from ..database.supabase_client import get_supabase_client
from ...inference.ai_factory import AIFactory


class IntelligentModelSelector:
    """
    Intelligent model selector using embedding similarity
    
    Features:
    - Reads models from database registry
    - Uses unified Supabase client
    - Uses existing embedding service for similarity matching
    - Has default models for each service type
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.supabase_client = None
        self.embedding_service = None
        self.models_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Default models for each service type
        self.default_models = {
            "vision": {"model_id": "gpt-4.1-mini", "provider": "openai"},
            "audio": {"model_id": "whisper-1", "provider": "openai"},
            "text": {"model_id": "gpt-4.1-mini", "provider": "openai"},
            "image": {"model_id": "black-forest-labs/flux-schnell", "provider": "replicate"},
            "embedding": {"model_id": "text-embedding-3-small", "provider": "openai"},
            "omni": {"model_id": "gpt-4.1", "provider": "openai"}
        }
        
        logger.info("Intelligent Model Selector initialized")
    
    async def initialize(self):
        """Initialize the model selector"""
        try:
            # Initialize Supabase client
            self.supabase_client = get_supabase_client()
            logger.info("Supabase client initialized")
            
            # Initialize embedding service
            await self._init_embedding_service()
            
            # Load models from database
            await self._load_models_from_database()
            
            logger.info("Model selector fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize model selector: {e}")
            # Continue with fallback mode
    
    async def _init_embedding_service(self):
        """Initialize embedding service for text similarity"""
        try:
            factory = AIFactory.get_instance()
            self.embedding_service = factory.get_embed("text-embedding-3-small", "openai")
            logger.info("Embedding service initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize embedding service: {e}")
    
    async def _load_models_from_database(self):
        """Load models from database registry"""
        try:
            # Get all models from database
            result = self.supabase_client.table('models').select('*').execute()
            models = result.data
            
            logger.info(f"Found {len(models)} models in database registry")
            
            # Process each model
            for model in models:
                model_id = model['model_id']
                
                # Parse metadata if it's a string (from JSONB)
                metadata_raw = model.get('metadata', '{}')
                if isinstance(metadata_raw, str):
                    try:
                        metadata = json.loads(metadata_raw)
                    except json.JSONDecodeError:
                        metadata = {}
                else:
                    metadata = metadata_raw if isinstance(metadata_raw, dict) else {}
                
                # Store model metadata
                self.models_metadata[model_id] = {
                    "provider": model['provider'],
                    "model_type": model['model_type'],
                    "metadata": metadata
                }
            
            # Check embeddings status
            embeddings_result = self.supabase_client.table('model_embeddings').select('model_id').execute()
            existing_embeddings = {row['model_id'] for row in embeddings_result.data}
            
            logger.info(f"Found {len(existing_embeddings)} model embeddings")
            logger.info(f"Loaded {len(self.models_metadata)} models for similarity matching")
            
            # Warn if models don't have embeddings
            missing_embeddings = set(self.models_metadata.keys()) - existing_embeddings
            if missing_embeddings:
                logger.warning(f"Models without embeddings: {list(missing_embeddings)}")
                logger.warning("Embeddings are generated during startup. Consider restarting the service.")
            
        except Exception as e:
            logger.error(f"Failed to load models from database: {e}")
    
    
    async def select_model(
        self,
        request: str,
        service_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Select best model using similarity matching
        
        Args:
            request: User's request/query
            service_type: Type of service needed
            context: Additional context
            
        Returns:
            Selection result with model info and reasoning
        """
        try:
            # Get embedding for user request
            if not self.embedding_service:
                return self._get_default_selection(service_type, "No embedding service available")
            
            request_embedding = await self.embedding_service.create_text_embedding(request)
            
            # Find similar models using Supabase
            candidates = await self._find_similar_models_supabase(request_embedding, service_type)
            
            if not candidates:
                return self._get_default_selection(service_type, "No suitable models found")
            
            # Return best match
            best_match = candidates[0]
            
            return {
                "success": True,
                "selected_model": {
                    "model_id": best_match["model_id"],
                    "provider": best_match["provider"]
                },
                "selection_reason": f"Best similarity match (score: {best_match['similarity']:.3f})",
                "alternatives": candidates[1:3],  # Top 2 alternatives
                "similarity_score": best_match["similarity"]
            }
            
        except Exception as e:
            logger.error(f"Model selection failed: {e}")
            return self._get_default_selection(service_type, f"Selection error: {e}")
    
    async def _find_similar_models_supabase(
        self, 
        request_embedding: List[float], 
        service_type: str
    ) -> List[Dict[str, Any]]:
        """Find similar models using Supabase and embedding service similarity"""
        try:
            # Get all model embeddings from database
            embeddings_result = self.supabase_client.table('model_embeddings').select('*').execute()
            model_embeddings = embeddings_result.data
            
            if not model_embeddings:
                logger.warning("No model embeddings found in database")
                return []
            
            # Calculate similarity for each model
            candidates = []
            for model_embed in model_embeddings:
                model_id = model_embed['model_id']
                model_embedding = model_embed['embedding']
                
                # Get model metadata
                model_metadata = self.models_metadata.get(model_id, {})
                model_type = model_metadata.get('model_type')
                
                # Filter by service type (including omni models)
                if model_type not in [service_type, 'omni']:
                    continue
                
                # Calculate similarity using embedding service
                try:
                    similarity_result = await self.embedding_service.invoke(
                        input_data="",  # Not used for similarity task
                        task="similarity",
                        embedding1=request_embedding,
                        embedding2=model_embedding
                    )
                    similarity = similarity_result['similarity']
                    
                    candidates.append({
                        "model_id": model_id,
                        "provider": model_embed['provider'],
                        "model_type": model_type,
                        "similarity": similarity,
                        "description": model_embed.get('description', '')
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to calculate similarity for {model_id}: {e}")
                    continue
            
            # Sort by similarity score
            candidates.sort(key=lambda x: x["similarity"], reverse=True)
            return candidates[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Supabase similarity search failed: {e}")
            return []
    
    def _get_default_selection(self, service_type: str, reason: str) -> Dict[str, Any]:
        """Get default model selection"""
        default = self.default_models.get(service_type, self.default_models["vision"])
        
        return {
            "success": True,
            "selected_model": default,
            "selection_reason": f"Default selection ({reason})",
            "alternatives": [],
            "similarity_score": 0.0
        }
    
    async def get_available_models(self, service_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available models"""
        try:
            if service_type:
                # Filter by service type
                query = self.supabase_client.table('models').select('*').or_(f'model_type.eq.{service_type},model_type.eq.omni')
            else:
                # Get all models
                query = self.supabase_client.table('models').select('*')
            
            result = query.order('model_id').execute()
            return result.data
                
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    async def close(self):
        """Clean up resources"""
        if self.embedding_service:
            await self.embedding_service.close()
            logger.info("Embedding service closed")


# Singleton instance
_selector_instance = None

async def get_model_selector(config: Optional[Dict[str, Any]] = None) -> IntelligentModelSelector:
    """Get singleton model selector instance"""
    global _selector_instance
    
    if _selector_instance is None:
        _selector_instance = IntelligentModelSelector(config)
        await _selector_instance.initialize()
    
    return _selector_instance