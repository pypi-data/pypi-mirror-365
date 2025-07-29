"""
Unified Model Registry with Supabase Backend

Simplified architecture using only Supabase for model metadata and capabilities.
No SQLite support - uses unified configuration management.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime

try:
    from ..database.supabase_client import get_supabase_client, get_supabase_table
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

from ..config import ConfigManager

logger = logging.getLogger(__name__)

class ModelCapability(str, Enum):
    """Model capabilities"""
    TEXT_GENERATION = "text_generation"
    CHAT = "chat"
    EMBEDDING = "embedding"
    RERANKING = "reranking"
    REASONING = "reasoning"
    IMAGE_GENERATION = "image_generation"
    IMAGE_ANALYSIS = "image_analysis"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    AUDIO_REALTIME = "audio_realtime"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    CONVERSATION = "conversation"
    IMAGE_UNDERSTANDING = "image_understanding"
    UI_DETECTION = "ui_detection"
    OCR = "ocr"
    TABLE_DETECTION = "table_detection"
    TABLE_STRUCTURE_RECOGNITION = "table_structure_recognition"

class ModelType(str, Enum):
    """Model types"""
    LLM = "llm"
    EMBEDDING = "embedding"
    RERANK = "rerank"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    VISION = "vision"

class ModelRegistry:
    """Unified Model Registry with Supabase backend"""
    
    def __init__(self):
        if not SUPABASE_AVAILABLE:
            raise ImportError("supabase-py is required. Install with: pip install supabase")
        
        # Get centralized Supabase client
        self.supabase_client = get_supabase_client()
        self.schema = self.supabase_client.get_schema()
        self.environment = self.supabase_client.get_environment()
        
        # Verify connection
        self._ensure_tables()
        
        logger.info(f"Model registry initialized with centralized Supabase client (env: {self.environment}, schema: {self.schema})")
    
    def _table(self, table_name: str):
        """Get table with correct schema"""
        return self.supabase_client.table(table_name)
    
    def _ensure_tables(self):
        """Ensure required tables exist in Supabase"""
        try:
            # Check if models table exists by trying to query it
            result = self._table('models').select('model_id').limit(1).execute()
            logger.debug(f"Models table verified in {self.schema} schema")
        except Exception as e:
            logger.warning(f"Models table might not exist in {self.schema} schema: {e}")
            # In production, tables should be created via Supabase migrations
    
    def register_model(self, 
                      model_id: str,
                      model_type: ModelType,
                      capabilities: List[ModelCapability],
                      metadata: Dict[str, Any],
                      provider: Optional[str] = None) -> bool:
        """Register a model with its capabilities and metadata"""
        try:
            current_time = datetime.now().isoformat()
            
            # Extract provider from metadata or use parameter
            provider_value = provider or metadata.get('provider')
            if not provider_value:
                raise ValueError("Provider must be specified either as parameter or in metadata")
            
            # Prepare model data
            model_data = {
                'model_id': model_id,
                'model_type': model_type.value,
                'provider': provider_value,
                'metadata': json.dumps(metadata),
                'created_at': current_time,
                'updated_at': current_time
            }
            
            # Insert or update model
            result = self._table('models').upsert(model_data).execute()
            
            if not result.data:
                logger.error(f"Failed to insert model {model_id}")
                return False
            
            # Delete existing capabilities
            self._table('model_capabilities').delete().eq('model_id', model_id).execute()
            
            # Insert new capabilities
            if capabilities:
                capability_data = [
                    {
                        'model_id': model_id,
                        'capability': capability.value,
                        'created_at': current_time
                    }
                    for capability in capabilities
                ]
                
                cap_result = self._table('model_capabilities').insert(capability_data).execute()
                
                if not cap_result.data:
                    logger.error(f"Failed to insert capabilities for {model_id}")
                    return False
            
            logger.info(f"Successfully registered model {model_id} with {len(capabilities)} capabilities")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register model {model_id}: {e}")
            return False
    
    def unregister_model(self, model_id: str) -> bool:
        """Unregister a model"""
        try:
            # Delete model (capabilities will be cascade deleted)
            result = self._table('models').delete().eq('model_id', model_id).execute()
            
            if result.data:
                logger.info(f"Unregistered model {model_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to unregister model {model_id}: {e}")
            return False
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model information"""
        try:
            # Get model info
            model_result = self._table('models').select('*').eq('model_id', model_id).execute()
            
            if not model_result.data:
                return None
            
            model_row = model_result.data[0]
            
            # Get capabilities
            cap_result = self._table('model_capabilities').select('capability').eq('model_id', model_id).execute()
            capabilities = [cap['capability'] for cap in cap_result.data]
            
            model_info = {
                "model_id": model_row["model_id"],
                "type": model_row["model_type"],
                "capabilities": capabilities,
                "metadata": json.loads(model_row["metadata"]) if model_row["metadata"] else {},
                "created_at": model_row["created_at"],
                "updated_at": model_row["updated_at"]
            }
            
            return model_info
            
        except Exception as e:
            logger.error(f"Failed to get model info for {model_id}: {e}")
            return None
    
    def get_models_by_type(self, model_type: ModelType) -> Dict[str, Dict[str, Any]]:
        """Get all models of a specific type"""
        try:
            models_result = self._table('models').select('*').eq('model_type', model_type.value).execute()
            
            result = {}
            for model in models_result.data:
                model_id = model["model_id"]
                
                # Get capabilities for this model
                cap_result = self._table('model_capabilities').select('capability').eq('model_id', model_id).execute()
                capabilities = [cap['capability'] for cap in cap_result.data]
                
                result[model_id] = {
                    "type": model["model_type"],
                    "capabilities": capabilities,
                    "metadata": json.loads(model["metadata"]) if model["metadata"] else {},
                    "created_at": model["created_at"],
                    "updated_at": model["updated_at"]
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get models by type {model_type}: {e}")
            return {}
    
    def get_models_by_capability(self, capability: ModelCapability) -> Dict[str, Dict[str, Any]]:
        """Get all models with a specific capability"""
        try:
            # Get model IDs with specific capability
            cap_result = self._table('model_capabilities').select('model_id').eq('capability', capability.value).execute()
            model_ids = [row['model_id'] for row in cap_result.data]
            
            if not model_ids:
                return {}
            
            # Get model details
            models_result = self._table('models').select('*').in_('model_id', model_ids).execute()
            
            result = {}
            for model in models_result.data:
                model_id = model["model_id"]
                
                # Get all capabilities for this model
                all_caps_result = self._table('model_capabilities').select('capability').eq('model_id', model_id).execute()
                capabilities = [cap['capability'] for cap in all_caps_result.data]
                
                result[model_id] = {
                    "type": model["model_type"],
                    "capabilities": capabilities,
                    "metadata": json.loads(model["metadata"]) if model["metadata"] else {},
                    "created_at": model["created_at"],
                    "updated_at": model["updated_at"]
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get models by capability {capability}: {e}")
            return {}
    
    def has_capability(self, model_id: str, capability: ModelCapability) -> bool:
        """Check if a model has a specific capability"""
        try:
            result = self._table('model_capabilities').select('model_id').eq('model_id', model_id).eq('capability', capability.value).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to check capability for {model_id}: {e}")
            return False
    
    def list_models(self) -> Dict[str, Dict[str, Any]]:
        """List all registered models"""
        try:
            models_result = self._table('models').select('*').order('created_at', desc=True).execute()
            
            result = {}
            for model in models_result.data:
                model_id = model["model_id"]
                
                # Get capabilities for this model
                cap_result = self._table('model_capabilities').select('capability').eq('model_id', model_id).execute()
                capabilities = [cap['capability'] for cap in cap_result.data]
                
                result[model_id] = {
                    "type": model["model_type"],
                    "capabilities": capabilities,
                    "metadata": json.loads(model["metadata"]) if model["metadata"] else {},
                    "created_at": model["created_at"],
                    "updated_at": model["updated_at"]
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return {}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        try:
            # Count total models
            total_result = self._table('models').select('model_id', count='exact').execute()
            total_models = total_result.count if total_result.count is not None else 0
            
            # Count by type (manual aggregation since RPC might not exist)
            models_result = self._table('models').select('model_type').execute()
            type_counts = {}
            for model in models_result.data:
                model_type = model['model_type']
                type_counts[model_type] = type_counts.get(model_type, 0) + 1
            
            # Count by capability
            caps_result = self._table('model_capabilities').select('capability').execute()
            capability_counts = {}
            for cap in caps_result.data:
                capability = cap['capability']
                capability_counts[capability] = capability_counts.get(capability, 0) + 1
            
            return {
                "total_models": total_models,
                "models_by_type": type_counts,
                "models_by_capability": capability_counts
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"total_models": 0, "models_by_type": {}, "models_by_capability": {}}
    
    def search_models(self, query: str) -> Dict[str, Dict[str, Any]]:
        """Search models by name or metadata"""
        try:
            # Search in model_id and metadata
            models_result = self._table('models').select('*').or_(
                f'model_id.ilike.%{query}%,metadata.ilike.%{query}%'
            ).order('created_at', desc=True).execute()
            
            result = {}
            for model in models_result.data:
                model_id = model["model_id"]
                
                # Get capabilities for this model
                cap_result = self._table('model_capabilities').select('capability').eq('model_id', model_id).execute()
                capabilities = [cap['capability'] for cap in cap_result.data]
                
                result[model_id] = {
                    "type": model["model_type"],
                    "capabilities": capabilities,
                    "metadata": json.loads(model["metadata"]) if model["metadata"] else {},
                    "created_at": model["created_at"],
                    "updated_at": model["updated_at"]
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to search models with query '{query}': {e}")
            return {}