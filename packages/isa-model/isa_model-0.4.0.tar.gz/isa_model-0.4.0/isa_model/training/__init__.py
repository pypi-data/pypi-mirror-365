"""
ISA Model Training Module

Provides unified training capabilities for AI models including:
- Local training with SFT (Supervised Fine-Tuning)
- Cloud training on RunPod
- Model evaluation and management
- HuggingFace integration
- 🧠 Intelligent training with AI-powered optimization

Example usage:
    ```python
    from isa_model.training import TrainingFactory, train_gemma
    
    # Quick Gemma training
    model_path = train_gemma(
        dataset_path="tatsu-lab/alpaca",
        model_size="4b",
        num_epochs=3
    )
    
    # Advanced training with custom configuration
    factory = TrainingFactory()
    model_path = factory.train_model(
        model_name="google/gemma-2-4b-it",
        dataset_path="your-dataset.json",
        use_lora=True,
        batch_size=4,
        num_epochs=3
    )
    
    # 🧠 Intelligent training with natural language
    from isa_model.training import IntelligentTrainingFactory
    
    intelligent_factory = IntelligentTrainingFactory()
    recommendation = intelligent_factory.analyze_training_request(
        "Train a customer service chatbot for medical domain",
        dataset_path="medical_dialogues.json",
        quality_target="high",
        budget_limit=200.0
    )
    model_path = intelligent_factory.train_with_recommendation(recommendation)
    ```
"""

# Import the new clean factory
from .factory import TrainingFactory, train_gemma

# Import core components
from .core import (
    TrainingConfig,
    LoRAConfig, 
    DatasetConfig,
    BaseTrainer,
    SFTTrainer,
    TrainingUtils,
    DatasetManager,
    RunPodConfig,
    StorageConfig,
    JobConfig
)

# Import cloud training components
from .cloud import (
    TrainingJobOrchestrator
)

# Import intelligent training components (optional)
try:
    from .intelligent import (
        IntelligentTrainingFactory,
        IntelligentDecisionEngine,
        TaskClassifier,
        KnowledgeBase,
        ResourceOptimizer,
        TrainingRequest,
        TrainingRecommendation
    )
    INTELLIGENT_AVAILABLE = True
except ImportError as e:
    INTELLIGENT_AVAILABLE = False
    # Create placeholder classes for graceful degradation
    class IntelligentTrainingFactory:
        def __init__(self, *args, **kwargs):
            raise ImportError("Intelligent training features not available. Please install required dependencies.")
    
    class IntelligentDecisionEngine:
        def __init__(self, *args, **kwargs):
            raise ImportError("Intelligent training features not available.")
    
    class TaskClassifier:
        def __init__(self, *args, **kwargs):
            raise ImportError("Intelligent training features not available.")
    
    class KnowledgeBase:
        def __init__(self, *args, **kwargs):
            raise ImportError("Intelligent training features not available.")
    
    class ResourceOptimizer:
        def __init__(self, *args, **kwargs):
            raise ImportError("Intelligent training features not available.")
    
    class TrainingRequest:
        def __init__(self, *args, **kwargs):
            raise ImportError("Intelligent training features not available.")
    
    class TrainingRecommendation:
        def __init__(self, *args, **kwargs):
            raise ImportError("Intelligent training features not available.")

__all__ = [
    # Main factory
    'TrainingFactory',
    'train_gemma',
    
    # Core components
    'TrainingConfig',
    'LoRAConfig',
    'DatasetConfig', 
    'BaseTrainer',
    'SFTTrainer',
    'TrainingUtils',
    'DatasetManager',
    
    # Cloud components
    'RunPodConfig',
    'StorageConfig',
    'JobConfig',
    'TrainingJobOrchestrator',
    
    # Intelligent training components
    'IntelligentTrainingFactory',
    'IntelligentDecisionEngine',
    'TaskClassifier',
    'KnowledgeBase',
    'ResourceOptimizer',
    'TrainingRequest',
    'TrainingRecommendation',
    'INTELLIGENT_AVAILABLE',
    
    # Training storage components (optional)
    'TrainingStorage',
    'TrainingRepository',
    'CoreModelIntegration'
]

# Import training storage components (optional)
try:
    from .storage import (
        TrainingStorage,
        TrainingRepository,
        CoreModelIntegration
    )
    STORAGE_AVAILABLE = True
except ImportError:
    STORAGE_AVAILABLE = False
    # Create placeholder classes for graceful degradation
    class TrainingStorage:
        def __init__(self, *args, **kwargs):
            raise ImportError("Training storage features not available.")
    
    class TrainingRepository:
        def __init__(self, *args, **kwargs):
            raise ImportError("Training repository features not available.")
    
    class CoreModelIntegration:
        def __init__(self, *args, **kwargs):
            raise ImportError("Core model integration features not available.") 