"""
Training Data Storage Module

This module provides persistent storage for training-related data:
- Training job records and history
- Model training metadata and metrics
- Cost tracking and billing information
- Integration with core model management
- Model version management and lineage tracking

Works seamlessly with existing core storage infrastructure.
"""

from .training_storage import TrainingStorage, TrainingJobRecord, TrainingMetrics
from .training_repository import TrainingRepository
from .core_integration import CoreModelIntegration

__all__ = [
    'TrainingStorage',
    'TrainingJobRecord', 
    'TrainingMetrics',
    'TrainingRepository',
    'CoreModelIntegration'
]