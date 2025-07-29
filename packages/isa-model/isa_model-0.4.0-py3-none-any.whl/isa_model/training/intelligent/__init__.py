"""
Intelligent Training Service Components

This module provides AI-powered training optimization and automation:
- Intelligent decision engine for configuration recommendations
- Task classification and model selection
- Resource optimization and cost estimation
- Natural language interface for training requests
"""

from .decision_engine import IntelligentDecisionEngine, TrainingRequest, TrainingRecommendation
from .task_classifier import TaskClassifier
from .knowledge_base import KnowledgeBase
from .resource_optimizer import ResourceOptimizer
from .intelligent_factory import IntelligentTrainingFactory

__all__ = [
    'IntelligentDecisionEngine',
    'TaskClassifier', 
    'KnowledgeBase',
    'ResourceOptimizer',
    'IntelligentTrainingFactory',
    'TrainingRequest',
    'TrainingRecommendation'
]