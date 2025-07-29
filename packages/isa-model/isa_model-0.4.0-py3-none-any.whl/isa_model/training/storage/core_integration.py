"""
Training-Core Integration Layer

This module provides seamless integration between the training module 
and the core model management system, ensuring:
- Trained models are automatically registered in Core ModelManager
- Training costs are tracked through Core billing system
- Model lifecycle is managed consistently
- No duplication of model metadata
"""

import logging
from typing import Dict, Optional, Any, List
from datetime import datetime
from pathlib import Path

try:
    from ...core.models.model_manager import ModelManager
    from ...core.models.model_repo import ModelType, ModelCapability
    from ...core.models.model_billing_tracker import ModelBillingTracker, ModelOperationType
    from ...core.models.model_statistics_tracker import ModelStatisticsTracker
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False

from .training_storage import TrainingStorage, TrainingJobRecord

logger = logging.getLogger(__name__)


class CoreModelIntegration:
    """
    Integration layer between training and core model management.
    
    This class ensures that:
    1. Trained models are registered in the core ModelManager
    2. Training costs are tracked through the core billing system
    3. Model metadata is kept consistent between training and core
    4. Training metrics are available in the core statistics system
    
    Example:
        ```python
        integration = CoreModelIntegration()
        
        # After training completion
        integration.register_trained_model(
            job_record=training_job,
            model_path="/path/to/trained/model",
            performance_metrics={"accuracy": 0.95}
        )
        
        # This will:
        # 1. Register model in CoreModelManager
        # 2. Record training costs in billing tracker
        # 3. Update model statistics
        # 4. Link training job to core model record
        ```
    """
    
    def __init__(self, 
                 model_manager: Optional[ModelManager] = None,
                 training_storage: Optional[TrainingStorage] = None):
        """
        Initialize core integration.
        
        Args:
            model_manager: Core model manager instance
            training_storage: Training storage instance
        """
        self.core_available = CORE_AVAILABLE
        
        if self.core_available:
            self.model_manager = model_manager or ModelManager()
            self.billing_tracker = self.model_manager.billing_tracker
            self.statistics_tracker = self.model_manager.statistics_tracker
            self.model_registry = self.model_manager.registry
        else:
            logger.warning("Core model management not available")
            self.model_manager = None
            self.billing_tracker = None
            self.statistics_tracker = None
            self.model_registry = None
        
        self.training_storage = training_storage or TrainingStorage()
        
        logger.info(f"Core integration initialized (Core available: {self.core_available})")
    
    def register_trained_model(
        self,
        job_record: TrainingJobRecord,
        model_path: str,
        performance_metrics: Optional[Dict[str, float]] = None,
        model_size_mb: Optional[float] = None
    ) -> Optional[str]:
        """
        Register a trained model in the core system.
        
        Args:
            job_record: Training job record
            model_path: Path to the trained model
            performance_metrics: Model performance metrics
            model_size_mb: Model size in MB
            
        Returns:
            Core model ID if successful, None otherwise
        """
        if not self.core_available:
            logger.warning("Core integration not available, skipping model registration")
            return None
        
        try:
            # Determine model type based on task
            model_type = self._get_model_type_from_task(job_record.task_type)
            
            # Determine capabilities
            capabilities = self._get_capabilities_from_task(job_record.task_type, job_record.domain)
            
            # Create model metadata
            model_metadata = {
                "base_model": job_record.base_model,
                "training_job_id": job_record.job_id,
                "task_type": job_record.task_type,
                "domain": job_record.domain,
                "dataset_source": job_record.dataset_source,
                "training_config": job_record.training_config,
                "performance_metrics": performance_metrics or {},
                "trained_at": job_record.completed_at.isoformat() if job_record.completed_at else None,
                "training_cost": sum(job_record.cost_breakdown.values()) if job_record.cost_breakdown else None,
                "model_size_mb": model_size_mb
            }
            
            # Generate model name
            model_name = self._generate_model_name(job_record)
            
            # Register model in core registry
            success = self.model_registry.register_model(
                model_id=model_name,
                model_type=model_type,
                capabilities=capabilities,
                metadata=model_metadata,
                local_path=model_path
            )
            
            if success:
                logger.info(f"Successfully registered trained model: {model_name}")
                
                # Update training job with core model ID
                self.training_storage.update_training_job(
                    job_record.job_id, 
                    {"core_model_id": model_name}
                )
                
                # Record training costs
                self._record_training_costs(job_record, model_name)
                
                # Update statistics
                self._update_model_statistics(job_record, model_name, performance_metrics)
                
                return model_name
            else:
                logger.error("Failed to register model in core registry")
                return None
                
        except Exception as e:
            logger.error(f"Failed to register trained model: {e}")
            return None
    
    def sync_training_knowledge_to_core(self) -> bool:
        """
        Sync training knowledge base data to core model registry.
        
        This helps keep the core system updated with training capabilities
        and model information discovered through intelligent training.
        
        Returns:
            True if successful
        """
        if not self.core_available:
            return False
        
        try:
            # Import training knowledge base
            from ..intelligent.knowledge_base import KnowledgeBase
            
            kb = KnowledgeBase()
            
            # Sync model specifications
            synced_count = 0
            for model_name, model_spec in kb.models.items():
                try:
                    # Convert training model spec to core format
                    model_type = self._convert_model_type(model_spec.model_type)
                    capabilities = self._convert_capabilities(model_spec.supported_tasks)
                    
                    metadata = {
                        "source": "training_knowledge_base",
                        "parameters": model_spec.parameters,
                        "context_length": model_spec.context_length,
                        "supported_tasks": model_spec.supported_tasks,
                        "supported_domains": model_spec.supported_domains,
                        "quality_score": model_spec.quality_score,
                        "efficiency_score": model_spec.efficiency_score,
                        "is_popular": model_spec.is_popular,
                        "description": model_spec.description,
                        "synced_at": datetime.now().isoformat()
                    }
                    
                    # Only register if not already exists
                    existing = self.model_registry.get_model_by_id(model_name)
                    if not existing:
                        success = self.model_registry.register_model(
                            model_id=model_name,
                            model_type=model_type,
                            capabilities=capabilities,
                            metadata=metadata
                        )
                        if success:
                            synced_count += 1
                
                except Exception as e:
                    logger.warning(f"Failed to sync model {model_name}: {e}")
                    continue
            
            logger.info(f"Synced {synced_count} models from training knowledge base to core")
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync training knowledge to core: {e}")
            return False
    
    def get_core_model_for_training(self, base_model: str) -> Optional[Dict[str, Any]]:
        """
        Get core model information for a base model used in training.
        
        Args:
            base_model: Base model identifier
            
        Returns:
            Core model information if available
        """
        if not self.core_available:
            return None
        
        try:
            return self.model_registry.get_model_by_id(base_model)
        except Exception as e:
            logger.error(f"Failed to get core model info for {base_model}: {e}")
            return None
    
    def get_training_history_for_model(self, model_id: str) -> List[TrainingJobRecord]:
        """
        Get training history for a specific model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            List of training job records
        """
        try:
            # Search for training jobs that produced this model
            all_jobs = self.training_storage.list_training_jobs(limit=1000)
            
            model_training_jobs = []
            for job in all_jobs:
                # Check if this job produced the model
                if (hasattr(job, 'core_model_id') and job.core_model_id == model_id) or \
                   job.base_model == model_id:
                    model_training_jobs.append(job)
            
            return model_training_jobs
            
        except Exception as e:
            logger.error(f"Failed to get training history for model {model_id}: {e}")
            return []
    
    def calculate_model_training_cost(self, model_id: str) -> Optional[float]:
        """
        Calculate total training cost for a model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Total training cost in USD
        """
        try:
            training_jobs = self.get_training_history_for_model(model_id)
            
            total_cost = 0.0
            for job in training_jobs:
                if job.cost_breakdown:
                    total_cost += sum(job.cost_breakdown.values())
            
            return total_cost if total_cost > 0 else None
            
        except Exception as e:
            logger.error(f"Failed to calculate training cost for model {model_id}: {e}")
            return None
    
    def _get_model_type_from_task(self, task_type: str) -> ModelType:
        """Convert training task type to core model type."""
        task_to_type_map = {
            "chat": ModelType.CHAT,
            "classification": ModelType.CLASSIFICATION,
            "generation": ModelType.GENERATION,
            "summarization": ModelType.SUMMARIZATION,
            "translation": ModelType.TRANSLATION,
            "code": ModelType.CODE_GENERATION,
            "image_generation": ModelType.IMAGE_GENERATION
        }
        
        return task_to_type_map.get(task_type, ModelType.CHAT)
    
    def _get_capabilities_from_task(self, task_type: str, domain: str) -> List[ModelCapability]:
        """Determine model capabilities from task and domain."""
        capabilities = []
        
        # Task-based capabilities
        if task_type in ["chat", "generation"]:
            capabilities.append(ModelCapability.TEXT_GENERATION)
        if task_type == "classification":
            capabilities.append(ModelCapability.TEXT_CLASSIFICATION)
        if task_type == "summarization":
            capabilities.append(ModelCapability.SUMMARIZATION)
        if task_type == "translation":
            capabilities.append(ModelCapability.TRANSLATION)
        if task_type == "code":
            capabilities.append(ModelCapability.CODE_GENERATION)
        
        # Domain-based capabilities
        if domain == "medical":
            capabilities.append(ModelCapability.DOMAIN_SPECIFIC)
        if domain in ["legal", "financial", "technical"]:
            capabilities.append(ModelCapability.DOMAIN_SPECIFIC)
        
        return capabilities
    
    def _generate_model_name(self, job_record: TrainingJobRecord) -> str:
        """Generate a unique model name for core registration."""
        base_name = job_record.base_model.split("/")[-1] if "/" in job_record.base_model else job_record.base_model
        timestamp = job_record.created_at.strftime("%Y%m%d_%H%M%S")
        task = job_record.task_type
        domain = job_record.domain
        
        return f"{base_name}_{task}_{domain}_{timestamp}"
    
    def _record_training_costs(self, job_record: TrainingJobRecord, model_name: str) -> None:
        """Record training costs in the core billing system."""
        if not self.billing_tracker or not job_record.cost_breakdown:
            return
        
        try:
            total_cost = sum(job_record.cost_breakdown.values())
            
            # Record training operation cost
            self.billing_tracker.record_operation(
                model_id=model_name,
                operation_type=ModelOperationType.TRAINING,
                cost=total_cost,
                metadata={
                    "training_job_id": job_record.job_id,
                    "base_model": job_record.base_model,
                    "task_type": job_record.task_type,
                    "cost_breakdown": job_record.cost_breakdown,
                    "training_duration": str(job_record.completed_at - job_record.started_at) if job_record.completed_at and job_record.started_at else None
                }
            )
            
            logger.info(f"Recorded training cost ${total_cost:.2f} for model {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to record training costs: {e}")
    
    def _update_model_statistics(
        self, 
        job_record: TrainingJobRecord, 
        model_name: str, 
        performance_metrics: Optional[Dict[str, float]]
    ) -> None:
        """Update model statistics in the core system."""
        if not self.statistics_tracker:
            return
        
        try:
            # Record training completion
            self.statistics_tracker.record_usage(
                model_id=model_name,
                operation_type="training",
                metadata={
                    "training_job_id": job_record.job_id,
                    "task_type": job_record.task_type,
                    "domain": job_record.domain,
                    "performance_metrics": performance_metrics or {}
                }
            )
            
            logger.info(f"Updated statistics for model {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to update model statistics: {e}")
    
    def _convert_model_type(self, training_model_type: str) -> ModelType:
        """Convert training model type to core model type."""
        type_map = {
            "llm": ModelType.CHAT,
            "sd": ModelType.IMAGE_GENERATION,
            "ml": ModelType.CLASSIFICATION
        }
        
        return type_map.get(training_model_type, ModelType.CHAT)
    
    def _convert_capabilities(self, supported_tasks: List[str]) -> List[ModelCapability]:
        """Convert training supported tasks to core capabilities."""
        capabilities = []
        
        for task in supported_tasks:
            if task in ["chat", "generation"]:
                capabilities.append(ModelCapability.TEXT_GENERATION)
            elif task == "classification":
                capabilities.append(ModelCapability.TEXT_CLASSIFICATION)
            elif task == "summarization":
                capabilities.append(ModelCapability.SUMMARIZATION)
            elif task == "translation":
                capabilities.append(ModelCapability.TRANSLATION)
            elif task == "code":
                capabilities.append(ModelCapability.CODE_GENERATION)
        
        return list(set(capabilities))  # Remove duplicates
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of core integration."""
        return {
            "core_available": self.core_available,
            "model_manager_connected": self.model_manager is not None,
            "billing_tracker_available": self.billing_tracker is not None,
            "statistics_tracker_available": self.statistics_tracker is not None,
            "training_storage_available": self.training_storage is not None
        }