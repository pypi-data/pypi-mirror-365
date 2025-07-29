"""
Knowledge Base for Training Intelligence

This module provides a comprehensive knowledge base containing:
- Model specifications and capabilities
- Training best practices and benchmarks
- Performance metrics and cost data
- Historical training results
- Resource requirements and recommendations

The knowledge base serves as the brain of the intelligent training system.
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import os
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ModelSpec:
    """Model specification and metadata."""
    
    name: str
    model_type: str  # "llm", "sd", "cv", "audio"
    parameters: int  # Number of parameters
    
    # Capabilities
    supported_tasks: List[str]
    supported_domains: List[str]
    context_length: int = 2048
    
    # Performance characteristics
    quality_score: float = 0.0  # 0.0 to 1.0
    speed_score: float = 0.0    # 0.0 to 1.0
    efficiency_score: float = 0.0  # 0.0 to 1.0
    
    # Training characteristics
    optimal_dataset_size: int = 10000
    min_dataset_size: int = 100
    supports_lora: bool = True
    supports_full_finetuning: bool = True
    
    # Resource requirements
    min_gpu_memory: int = 8  # GB
    recommended_gpu_memory: int = 16  # GB
    training_time_factor: float = 1.0  # Relative to baseline
    
    # Cost estimates (per hour)
    estimated_cost_per_hour: float = 0.0
    
    # Metadata
    is_popular: bool = False
    is_open_source: bool = True
    release_date: Optional[str] = None
    description: str = ""
    
    # Configuration defaults
    default_config: Dict[str, Any] = field(default_factory=dict)
    lora_targets: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.lora_targets and self.supports_lora:
            self.lora_targets = ["q_proj", "v_proj", "k_proj", "o_proj"]


@dataclass
class BestPractice:
    """Training best practice recommendation."""
    
    task_type: str
    domain: str
    recommendation: str
    reason: str
    confidence: float
    source: str = "expert_knowledge"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PerformanceBenchmark:
    """Performance benchmark data."""
    
    model_name: str
    task_type: str
    dataset_name: str
    
    # Performance metrics
    accuracy: Optional[float] = None
    bleu_score: Optional[float] = None
    rouge_score: Optional[float] = None
    perplexity: Optional[float] = None
    
    # Training metrics
    training_time: Optional[float] = None  # hours
    training_cost: Optional[float] = None  # USD
    gpu_type: Optional[str] = None
    
    # Configuration used
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    source: str = "benchmark"
    created_at: datetime = field(default_factory=datetime.now)


class KnowledgeBase:
    """
    Comprehensive knowledge base for training intelligence.
    
    This class manages all the knowledge required for intelligent training decisions:
    - Model specifications and capabilities
    - Training best practices and guidelines
    - Performance benchmarks and historical data
    - Resource requirements and cost estimates
    
    Example:
        ```python
        kb = KnowledgeBase()
        
        # Get model recommendations
        models = kb.recommend_models(
            task_type="chat",
            domain="medical",
            dataset_size=5000,
            quality_target="high"
        )
        
        # Get best practices
        practices = kb.get_best_practices("chat", "medical")
        ```
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize knowledge base.
        
        Args:
            data_dir: Directory to store/load knowledge base data
        """
        self.data_dir = data_dir or os.path.join(os.getcwd(), "knowledge_base")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize data structures
        self.models: Dict[str, ModelSpec] = {}
        self.best_practices: List[BestPractice] = []
        self.benchmarks: List[PerformanceBenchmark] = []
        self.dataset_info: Dict[str, Dict[str, Any]] = {}
        
        # Load existing data
        self._load_knowledge_base()
        
        # Initialize with default knowledge if empty
        if not self.models:
            self._initialize_default_knowledge()
        
        logger.info(f"Knowledge base initialized with {len(self.models)} models")
    
    def recommend_models(
        self,
        task_type: str,
        domain: str = "general",
        dataset_size: int = 10000,
        quality_target: str = "balanced",
        constraints: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Recommend models for a specific task and requirements.
        
        Args:
            task_type: Type of task (chat, classification, etc.)
            domain: Domain/industry
            dataset_size: Size of training dataset
            quality_target: Quality target (fast, balanced, high)
            constraints: Additional constraints (budget, time, etc.)
            
        Returns:
            List of recommended models with scores
        """
        constraints = constraints or {}
        
        # Filter models by task compatibility
        compatible_models = []
        for model_name, model_spec in self.models.items():
            if self._is_model_compatible(model_spec, task_type, domain, dataset_size):
                score = self._score_model(
                    model_spec, task_type, domain, dataset_size, quality_target, constraints
                )
                
                model_dict = asdict(model_spec)
                model_dict["suitability_score"] = score
                model_dict["task_suitability"] = score / 100.0  # Normalize
                
                # Ensure trainer_type is set based on model_type
                if "trainer_type" not in model_dict or not model_dict["trainer_type"]:
                    if model_spec.model_type == "llm":
                        model_dict["trainer_type"] = "llm"
                    elif model_spec.model_type == "sd":
                        model_dict["trainer_type"] = "sd"
                    elif model_spec.model_type == "ml":
                        model_dict["trainer_type"] = "ml"
                    else:
                        model_dict["trainer_type"] = "llm"  # Default
                
                compatible_models.append(model_dict)
        
        # Sort by suitability score
        compatible_models.sort(key=lambda x: x["suitability_score"], reverse=True)
        
        return compatible_models[:10]  # Return top 10
    
    def _is_model_compatible(
        self, 
        model_spec: ModelSpec, 
        task_type: str, 
        domain: str, 
        dataset_size: int
    ) -> bool:
        """Check if model is compatible with requirements."""
        # Check task compatibility
        if task_type not in model_spec.supported_tasks and "general" not in model_spec.supported_tasks:
            return False
        
        # Check domain compatibility
        if domain not in model_spec.supported_domains and "general" not in model_spec.supported_domains:
            return False
        
        # Check minimum dataset size
        if dataset_size < model_spec.min_dataset_size:
            return False
        
        return True
    
    def _score_model(
        self,
        model_spec: ModelSpec,
        task_type: str,
        domain: str,
        dataset_size: int,
        quality_target: str,
        constraints: Dict[str, Any]
    ) -> float:
        """Score a model's suitability for the task."""
        score = 0.0
        
        # Base compatibility score
        if task_type in model_spec.supported_tasks:
            score += 30
        elif "general" in model_spec.supported_tasks:
            score += 15
        
        if domain in model_spec.supported_domains:
            score += 20
        elif "general" in model_spec.supported_domains:
            score += 10
        
        # Quality vs speed preference
        if quality_target == "high":
            score += model_spec.quality_score * 25
        elif quality_target == "fast":
            score += model_spec.speed_score * 25
        else:  # balanced
            score += (model_spec.quality_score + model_spec.speed_score) * 12.5
        
        # Efficiency bonus
        score += model_spec.efficiency_score * 10
        
        # Popularity bonus
        if model_spec.is_popular:
            score += 5
        
        # Dataset size compatibility
        if dataset_size >= model_spec.optimal_dataset_size:
            score += 10
        else:
            # Penalty for suboptimal dataset size
            ratio = dataset_size / model_spec.optimal_dataset_size
            score += ratio * 10
        
        # Budget constraints
        if constraints.get("budget"):
            budget = constraints["budget"]
            estimated_cost = model_spec.estimated_cost_per_hour * 10  # Assume 10 hours
            if estimated_cost <= budget:
                score += 5
            else:
                score -= 10
        
        # Time constraints
        if constraints.get("time"):
            time_limit = constraints["time"]
            estimated_time = 10 * model_spec.training_time_factor  # Assume 10 base hours
            if estimated_time <= time_limit:
                score += 5
            else:
                score -= 10
        
        # Model preferences
        if constraints.get("preferences"):
            preferences = constraints["preferences"]
            if preferences:
                for pref in preferences:
                    if pref.lower() in model_spec.name.lower():
                        score += 15
        
        return max(0.0, score)
    
    def get_best_practices(self, task_type: str, domain: str = "general") -> List[BestPractice]:
        """Get best practices for a specific task and domain."""
        practices = []
        
        for practice in self.best_practices:
            if (practice.task_type == task_type or practice.task_type == "general") and \
               (practice.domain == domain or practice.domain == "general"):
                practices.append(practice)
        
        # Sort by confidence
        practices.sort(key=lambda x: x.confidence, reverse=True)
        
        return practices
    
    def get_performance_benchmarks(
        self, 
        model_name: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> List[PerformanceBenchmark]:
        """Get performance benchmarks."""
        benchmarks = []
        
        for benchmark in self.benchmarks:
            if model_name and benchmark.model_name != model_name:
                continue
            if task_type and benchmark.task_type != task_type:
                continue
            benchmarks.append(benchmark)
        
        return benchmarks
    
    def get_dataset_info(self, dataset_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a dataset."""
        return self.dataset_info.get(dataset_name)
    
    def add_model(self, model_spec: ModelSpec) -> None:
        """Add a new model to the knowledge base."""
        self.models[model_spec.name] = model_spec
        self._save_models()
        logger.info(f"Added model to knowledge base: {model_spec.name}")
    
    def add_best_practice(self, practice: BestPractice) -> None:
        """Add a best practice to the knowledge base."""
        self.best_practices.append(practice)
        self._save_best_practices()
        logger.info(f"Added best practice: {practice.task_type}/{practice.domain}")
    
    def add_benchmark(self, benchmark: PerformanceBenchmark) -> None:
        """Add a performance benchmark."""
        self.benchmarks.append(benchmark)
        self._save_benchmarks()
        logger.info(f"Added benchmark: {benchmark.model_name}/{benchmark.task_type}")
    
    def update_from_training_result(self, training_result: Dict[str, Any]) -> None:
        """Update knowledge base from training results."""
        # Extract information from training result
        model_name = training_result.get("model_name")
        task_type = training_result.get("task_type")
        
        if model_name and task_type:
            # Create benchmark from result
            benchmark = PerformanceBenchmark(
                model_name=model_name,
                task_type=task_type,
                dataset_name=training_result.get("dataset_name", "unknown"),
                training_time=training_result.get("training_time"),
                training_cost=training_result.get("training_cost"),
                gpu_type=training_result.get("gpu_type"),
                config=training_result.get("config", {}),
                source="training_result"
            )
            
            self.add_benchmark(benchmark)
    
    def _initialize_default_knowledge(self) -> None:
        """Initialize knowledge base with default models and best practices."""
        # Add popular LLM models
        self._add_llm_models()
        
        # Add Stable Diffusion models
        self._add_sd_models()
        
        # Add ML models
        self._add_ml_models()
        
        # Add best practices
        self._add_default_best_practices()
        
        # Add dataset information
        self._add_default_dataset_info()
        
        # Save to disk
        self._save_knowledge_base()
        
        logger.info("Initialized knowledge base with default data")
    
    def _add_llm_models(self) -> None:
        """Add LLM models to knowledge base."""
        llm_models = [
            ModelSpec(
                name="google/gemma-2-2b-it",
                model_type="llm",
                parameters=2_000_000_000,
                supported_tasks=["chat", "classification", "generation", "summarization"],
                supported_domains=["general", "technical", "education"],
                context_length=2048,
                quality_score=0.7,
                speed_score=0.9,
                efficiency_score=0.8,
                optimal_dataset_size=5000,
                min_dataset_size=100,
                min_gpu_memory=8,
                recommended_gpu_memory=12,
                training_time_factor=0.6,
                estimated_cost_per_hour=0.5,
                is_popular=True,
                is_open_source=True,
                description="Lightweight Gemma model optimized for efficiency",
                default_config={"learning_rate": 2e-5, "batch_size": 4, "lora_rank": 8}
            ),
            ModelSpec(
                name="google/gemma-2-4b-it",
                model_type="llm",
                parameters=4_000_000_000,
                supported_tasks=["chat", "classification", "generation", "summarization", "reasoning"],
                supported_domains=["general", "technical", "education", "medical"],
                context_length=2048,
                quality_score=0.8,
                speed_score=0.7,
                efficiency_score=0.8,
                optimal_dataset_size=10000,
                min_dataset_size=200,
                min_gpu_memory=12,
                recommended_gpu_memory=16,
                training_time_factor=0.8,
                estimated_cost_per_hour=0.8,
                is_popular=True,
                is_open_source=True,
                description="Balanced Gemma model with good performance and efficiency",
                default_config={"learning_rate": 2e-5, "batch_size": 2, "lora_rank": 16}
            ),
            ModelSpec(
                name="google/gemma-2-7b-it",
                model_type="llm",
                parameters=7_000_000_000,
                supported_tasks=["chat", "classification", "generation", "summarization", "reasoning", "code"],
                supported_domains=["general", "technical", "education", "medical", "legal"],
                context_length=4096,
                quality_score=0.9,
                speed_score=0.6,
                efficiency_score=0.7,
                optimal_dataset_size=20000,
                min_dataset_size=500,
                min_gpu_memory=16,
                recommended_gpu_memory=24,
                training_time_factor=1.0,
                estimated_cost_per_hour=1.2,
                is_popular=True,
                is_open_source=True,
                description="High-quality Gemma model for demanding tasks",
                default_config={"learning_rate": 1e-5, "batch_size": 1, "lora_rank": 32}
            ),
            ModelSpec(
                name="microsoft/DialoGPT-medium",
                model_type="llm",
                parameters=345_000_000,
                supported_tasks=["chat", "generation"],
                supported_domains=["general", "customer_service"],
                context_length=1024,
                quality_score=0.6,
                speed_score=0.95,
                efficiency_score=0.9,
                optimal_dataset_size=2000,
                min_dataset_size=50,
                min_gpu_memory=4,
                recommended_gpu_memory=8,
                training_time_factor=0.3,
                estimated_cost_per_hour=0.3,
                is_popular=True,
                is_open_source=True,
                description="Fast conversational model for chatbots",
                default_config={"learning_rate": 5e-5, "batch_size": 8, "lora_rank": 4}
            ),
            ModelSpec(
                name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                model_type="llm",
                parameters=1_100_000_000,
                supported_tasks=["chat", "generation"],
                supported_domains=["general", "education"],
                context_length=2048,
                quality_score=0.5,
                speed_score=0.95,
                efficiency_score=0.9,
                optimal_dataset_size=1000,
                min_dataset_size=50,
                min_gpu_memory=4,
                recommended_gpu_memory=6,
                training_time_factor=0.4,
                estimated_cost_per_hour=0.2,
                is_popular=True,
                is_open_source=True,
                description="Extremely lightweight model for resource-constrained environments",
                default_config={"learning_rate": 3e-5, "batch_size": 8, "lora_rank": 8}
            )
        ]
        
        for model in llm_models:
            self.models[model.name] = model
    
    def _add_sd_models(self) -> None:
        """Add Stable Diffusion models."""
        sd_models = [
            ModelSpec(
                name="runwayml/stable-diffusion-v1-5",
                model_type="sd",
                parameters=860_000_000,
                supported_tasks=["image_generation", "image_editing"],
                supported_domains=["art", "design", "general"],
                context_length=77,
                quality_score=0.8,
                speed_score=0.6,
                efficiency_score=0.7,
                optimal_dataset_size=1000,
                min_dataset_size=20,
                min_gpu_memory=8,
                recommended_gpu_memory=12,
                training_time_factor=1.2,
                estimated_cost_per_hour=1.0,
                is_popular=True,
                is_open_source=True,
                description="Popular Stable Diffusion model for image generation",
                default_config={"learning_rate": 1e-6, "batch_size": 1}
            )
        ]
        
        for model in sd_models:
            self.models[model.name] = model
    
    def _add_ml_models(self) -> None:
        """Add traditional ML models."""
        ml_models = [
            ModelSpec(
                name="xgboost_classifier",
                model_type="ml",
                parameters=1000,  # Approximate
                supported_tasks=["classification", "regression"],
                supported_domains=["general", "financial", "medical"],
                context_length=0,
                quality_score=0.8,
                speed_score=0.9,
                efficiency_score=0.95,
                optimal_dataset_size=10000,
                min_dataset_size=100,
                min_gpu_memory=2,
                recommended_gpu_memory=4,
                training_time_factor=0.1,
                estimated_cost_per_hour=0.1,
                is_popular=True,
                is_open_source=True,
                description="Gradient boosting classifier for tabular data",
                default_config={"n_estimators": 100, "learning_rate": 0.1}
            ),
            ModelSpec(
                name="random_forest_classifier",
                model_type="ml",
                parameters=1000,
                supported_tasks=["classification", "regression"],
                supported_domains=["general", "financial", "medical"],
                context_length=0,
                quality_score=0.7,
                speed_score=0.8,
                efficiency_score=0.9,
                optimal_dataset_size=5000,
                min_dataset_size=100,
                min_gpu_memory=2,
                recommended_gpu_memory=4,
                training_time_factor=0.2,
                estimated_cost_per_hour=0.05,
                is_popular=True,
                is_open_source=True,
                description="Random forest classifier for tabular data",
                default_config={"n_estimators": 100, "max_depth": 10}
            )
        ]
        
        for model in ml_models:
            self.models[model.name] = model
    
    def _add_default_best_practices(self) -> None:
        """Add default best practices."""
        practices = [
            BestPractice(
                task_type="chat",
                domain="general",
                recommendation="Use LoRA with rank 8-16 for chat models",
                reason="LoRA provides good performance while reducing training time and memory usage",
                confidence=0.9
            ),
            BestPractice(
                task_type="chat",
                domain="medical",
                recommendation="Use higher learning rates (3e-5) for medical domain adaptation",
                reason="Medical terminology requires stronger adaptation from general models",
                confidence=0.8
            ),
            BestPractice(
                task_type="classification",
                domain="general",
                recommendation="Use batch size 8-16 for classification tasks",
                reason="Larger batch sizes improve stability for classification training",
                confidence=0.85
            ),
            BestPractice(
                task_type="generation",
                domain="general",
                recommendation="Use gradient accumulation for large models",
                reason="Maintains effective batch size while reducing memory usage",
                confidence=0.9
            )
        ]
        
        self.best_practices.extend(practices)
    
    def _add_default_dataset_info(self) -> None:
        """Add default dataset information."""
        self.dataset_info = {
            "tatsu-lab/alpaca": {
                "size": 52000,
                "format": "alpaca",
                "language": "english",
                "domain": "general",
                "quality": "high"
            },
            "Open-Orca/OpenOrca": {
                "size": 4200000,
                "format": "sharegpt",
                "language": "english",
                "domain": "general",
                "quality": "high"
            },
            "microsoft/DialoGPT-medium": {
                "size": 147000000,
                "format": "conversational",
                "language": "english",
                "domain": "general",
                "quality": "medium"
            }
        }
    
    def _load_knowledge_base(self) -> None:
        """Load knowledge base from disk."""
        try:
            self._load_models()
            self._load_best_practices()
            self._load_benchmarks()
            self._load_dataset_info()
        except Exception as e:
            logger.warning(f"Failed to load knowledge base: {e}")
    
    def _save_knowledge_base(self) -> None:
        """Save knowledge base to disk."""
        try:
            self._save_models()
            self._save_best_practices()
            self._save_benchmarks()
            self._save_dataset_info()
        except Exception as e:
            logger.error(f"Failed to save knowledge base: {e}")
    
    def _load_models(self) -> None:
        """Load models from disk."""
        models_file = os.path.join(self.data_dir, "models.json")
        if os.path.exists(models_file):
            with open(models_file, 'r') as f:
                data = json.load(f)
                for name, model_data in data.items():
                    self.models[name] = ModelSpec(**model_data)
    
    def _save_models(self) -> None:
        """Save models to disk."""
        models_file = os.path.join(self.data_dir, "models.json")
        with open(models_file, 'w') as f:
            data = {name: asdict(model) for name, model in self.models.items()}
            json.dump(data, f, indent=2, default=str)
    
    def _load_best_practices(self) -> None:
        """Load best practices from disk."""
        practices_file = os.path.join(self.data_dir, "best_practices.json")
        if os.path.exists(practices_file):
            with open(practices_file, 'r') as f:
                data = json.load(f)
                self.best_practices = [BestPractice(**item) for item in data]
    
    def _save_best_practices(self) -> None:
        """Save best practices to disk."""
        practices_file = os.path.join(self.data_dir, "best_practices.json")
        with open(practices_file, 'w') as f:
            data = [asdict(practice) for practice in self.best_practices]
            json.dump(data, f, indent=2, default=str)
    
    def _load_benchmarks(self) -> None:
        """Load benchmarks from disk."""
        benchmarks_file = os.path.join(self.data_dir, "benchmarks.json")
        if os.path.exists(benchmarks_file):
            with open(benchmarks_file, 'r') as f:
                data = json.load(f)
                self.benchmarks = [PerformanceBenchmark(**item) for item in data]
    
    def _save_benchmarks(self) -> None:
        """Save benchmarks to disk."""
        benchmarks_file = os.path.join(self.data_dir, "benchmarks.json")
        with open(benchmarks_file, 'w') as f:
            data = [asdict(benchmark) for benchmark in self.benchmarks]
            json.dump(data, f, indent=2, default=str)
    
    def _load_dataset_info(self) -> None:
        """Load dataset info from disk."""
        dataset_file = os.path.join(self.data_dir, "datasets.json")
        if os.path.exists(dataset_file):
            with open(dataset_file, 'r') as f:
                self.dataset_info = json.load(f)
    
    def _save_dataset_info(self) -> None:
        """Save dataset info to disk."""
        dataset_file = os.path.join(self.data_dir, "datasets.json")
        with open(dataset_file, 'w') as f:
            json.dump(self.dataset_info, f, indent=2)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        return {
            "total_models": len(self.models),
            "llm_models": len([m for m in self.models.values() if m.model_type == "llm"]),
            "sd_models": len([m for m in self.models.values() if m.model_type == "sd"]),
            "ml_models": len([m for m in self.models.values() if m.model_type == "ml"]),
            "best_practices": len(self.best_practices),
            "benchmarks": len(self.benchmarks),
            "datasets": len(self.dataset_info)
        }