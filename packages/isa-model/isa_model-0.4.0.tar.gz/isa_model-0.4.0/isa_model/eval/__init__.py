"""
ISA Model Evaluation Framework

Enterprise-grade evaluation framework implementing MLOps best practices:

Key Features:
- Multi-modal evaluation (LLM, Vision, Multimodal)
- Async evaluation with smart concurrency management  
- Comprehensive experiment tracking (W&B, MLflow)
- Production-ready error handling and monitoring
- Distributed evaluation support
- Cost tracking and optimization
- Reproducible evaluation pipelines

Quick Start:
    ```python
    import asyncio
    from isa_model.eval import EvaluationFactory
    
    async def main():
        # Initialize factory with experiment tracking
        factory = EvaluationFactory(
            experiment_tracking={
                "type": "wandb",
                "project": "model-evaluation"
            }
        )
        
        # Evaluate LLM
        result = await factory.evaluate_llm(
            model_name="gpt-4.1-mini",
            provider="openai",
            dataset_path="eval_data.json",
            save_results=True
        )
        
        print(f"Accuracy: {result.metrics['exact_match']:.3f}")
        
        # Cleanup
        await factory.cleanup()
    
    asyncio.run(main())
    ```

Architecture:
- evaluators/: Specialized evaluators by modality
- infrastructure/: Experiment tracking, async runners, storage
- config/: Configuration management
- metrics/: Metric computation by type
- benchmarks/: Standard benchmark implementations
- utils/: Data processing and visualization utilities
"""

# Main interfaces
from .factory import EvaluationFactory, evaluate_llm_quick, run_benchmark_quick

# Core components
from .evaluators import BaseEvaluator, EvaluationResult, LLMEvaluator
from .config import EvaluationConfig, ConfigManager

# Infrastructure (optional imports)
try:
    from .infrastructure import ExperimentTracker, WandBTracker, MLflowTracker
    INFRASTRUCTURE_AVAILABLE = True
except ImportError:
    INFRASTRUCTURE_AVAILABLE = False

__all__ = [
    # Main interfaces
    "EvaluationFactory",
    "evaluate_llm_quick", 
    "run_benchmark_quick",
    
    # Core components
    "BaseEvaluator",
    "EvaluationResult",
    "LLMEvaluator",
    "EvaluationConfig",
    "ConfigManager"
]

# Add infrastructure components if available
if INFRASTRUCTURE_AVAILABLE:
    __all__.extend([
        "ExperimentTracker",
        "WandBTracker", 
        "MLflowTracker"
    ])

# Version info
__version__ = "1.0.0"
__author__ = "ISA Model Team" 