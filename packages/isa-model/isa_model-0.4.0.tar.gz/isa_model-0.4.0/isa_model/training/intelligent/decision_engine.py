"""
Intelligent Decision Engine for Training Configuration

This module provides AI-powered decision making for training configurations,
automatically selecting optimal models, parameters, and resources based on
user requirements, dataset characteristics, and historical performance data.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import os

from .task_classifier import TaskClassifier
from .knowledge_base import KnowledgeBase
from .resource_optimizer import ResourceOptimizer
from ..core.config import TrainingConfig, LoRAConfig, DatasetConfig

logger = logging.getLogger(__name__)


@dataclass
class TrainingRequest:
    """User training request with requirements and constraints."""
    
    # Core requirements
    description: str  # Natural language description
    dataset_source: str  # Dataset path or HuggingFace name
    
    # Quality and performance targets
    quality_target: str = "balanced"  # "fast", "balanced", "high"
    budget_limit: Optional[float] = None  # USD budget limit
    time_limit: Optional[int] = None  # Hours time limit
    
    # Optional constraints
    model_preferences: Optional[List[str]] = None  # Preferred models
    gpu_preferences: Optional[List[str]] = None  # Preferred GPU types
    cloud_preferences: Optional[List[str]] = None  # Preferred cloud providers
    
    # Advanced options
    use_lora: Optional[bool] = None  # Force LoRA usage
    batch_size: Optional[int] = None  # Force batch size
    learning_rate: Optional[float] = None  # Force learning rate
    
    # Metadata
    user_id: Optional[str] = None
    project_name: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class TrainingRecommendation:
    """Intelligent training configuration recommendation."""
    
    # Model selection
    model_name: str
    trainer_type: str  # "llm", "sd", "ml"
    
    # Training configuration
    training_config: TrainingConfig
    
    # Resource selection
    recommended_gpu: str
    cloud_provider: str
    estimated_cost: float
    estimated_time: int  # hours
    
    # Performance predictions
    predicted_quality: str  # "excellent", "good", "fair"
    confidence_score: float  # 0.0 to 1.0
    
    # Rationale
    decision_reasons: List[str]
    alternatives: List[Dict[str, Any]]
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0"


class IntelligentDecisionEngine:
    """
    Core intelligent decision engine for training configuration.
    
    This engine analyzes training requests and generates optimal configuration
    recommendations based on:
    - Task type and complexity analysis
    - Dataset characteristics
    - Historical performance data
    - Resource availability and pricing
    - User preferences and constraints
    
    Example:
        ```python
        engine = IntelligentDecisionEngine()
        
        request = TrainingRequest(
            description="Fine-tune a Chinese dialogue model for customer service",
            dataset_source="my-chinese-dialogues.json",
            quality_target="high",
            budget_limit=500.0,
            time_limit=12
        )
        
        recommendation = engine.analyze_and_recommend(request)
        print(f"Recommended: {recommendation.model_name}")
        print(f"Cost: ${recommendation.estimated_cost}")
        ```
    """
    
    def __init__(self, knowledge_base: Optional[KnowledgeBase] = None):
        """
        Initialize the intelligent decision engine.
        
        Args:
            knowledge_base: Optional knowledge base instance
        """
        self.task_classifier = TaskClassifier()
        self.knowledge_base = knowledge_base or KnowledgeBase()
        self.resource_optimizer = ResourceOptimizer()
        
        # Decision history for learning
        self.decision_history: List[Dict[str, Any]] = []
        
        logger.info("Intelligent Decision Engine initialized")
    
    def analyze_and_recommend(self, request: TrainingRequest) -> TrainingRecommendation:
        """
        Analyze training request and generate intelligent recommendation.
        
        Args:
            request: Training request with requirements
            
        Returns:
            Complete training recommendation
        """
        logger.info(f"Analyzing training request: {request.description[:100]}...")
        
        try:
            # Step 1: Classify task type and extract requirements
            task_analysis = self.task_classifier.analyze_request(
                request.description, 
                request.dataset_source
            )
            
            # Step 2: Analyze dataset characteristics
            dataset_analysis = self._analyze_dataset(request.dataset_source)
            
            # Step 3: Generate model recommendations
            model_candidates = self.knowledge_base.recommend_models(
                task_type=task_analysis.task_type,
                domain=task_analysis.domain,
                dataset_size=dataset_analysis.get("size", 0),
                quality_target=request.quality_target,
                constraints={
                    "budget": request.budget_limit,
                    "time": request.time_limit,
                    "preferences": request.model_preferences
                }
            )
            
            # Step 4: Select optimal model
            selected_model = self._select_optimal_model(
                model_candidates, 
                task_analysis, 
                dataset_analysis, 
                request
            )
            
            # Step 5: Generate training configuration
            training_config = self._generate_training_config(
                selected_model,
                task_analysis,
                dataset_analysis,
                request
            )
            
            # Step 6: Optimize resources
            resource_recommendation = self.resource_optimizer.optimize_resources(
                model_name=selected_model["name"],
                training_config=training_config,
                budget_limit=request.budget_limit,
                time_limit=request.time_limit,
                preferences={
                    "gpu": request.gpu_preferences,
                    "cloud": request.cloud_preferences
                }
            )
            
            # Step 7: Generate alternatives
            alternatives = self._generate_alternatives(
                model_candidates[:3],  # Top 3 alternatives
                task_analysis,
                dataset_analysis,
                request
            )
            
            # Step 8: Create recommendation
            recommendation = TrainingRecommendation(
                model_name=selected_model["name"],
                trainer_type=selected_model["trainer_type"],
                training_config=training_config,
                recommended_gpu=resource_recommendation.gpu,
                cloud_provider=resource_recommendation.cloud_provider,
                estimated_cost=resource_recommendation.estimated_cost,
                estimated_time=resource_recommendation.estimated_time,
                predicted_quality=self._predict_quality(
                    selected_model, training_config, dataset_analysis
                ),
                confidence_score=self._calculate_confidence(
                    selected_model, task_analysis, dataset_analysis
                ),
                decision_reasons=self._generate_decision_reasons(
                    selected_model, resource_recommendation, task_analysis
                ),
                alternatives=alternatives
            )
            
            # Store for learning
            self._store_decision(request, recommendation, task_analysis)
            
            logger.info(f"Generated recommendation: {recommendation.model_name} "
                       f"(${recommendation.estimated_cost:.2f}, {recommendation.estimated_time}h)")
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Failed to analyze training request: {e}")
            raise
    
    def _analyze_dataset(self, dataset_source: str) -> Dict[str, Any]:
        """Analyze dataset characteristics."""
        analysis = {
            "size": 0,
            "format": "unknown",
            "language": "unknown",
            "complexity": "medium",
            "quality": "unknown"
        }
        
        try:
            if os.path.exists(dataset_source):
                # Local dataset analysis
                with open(dataset_source, 'r', encoding='utf-8') as f:
                    if dataset_source.endswith('.json'):
                        data = json.load(f)
                        if isinstance(data, list):
                            analysis["size"] = len(data)
                            analysis["format"] = "json"
                            
                            # Analyze first few samples
                            if data:
                                sample = data[0]
                                if isinstance(sample, dict):
                                    if "instruction" in sample and "output" in sample:
                                        analysis["format"] = "alpaca"
                                    elif "messages" in sample:
                                        analysis["format"] = "sharegpt"
                                    
                                    # Estimate complexity based on text length
                                    text_content = str(sample)
                                    if len(text_content) > 1000:
                                        analysis["complexity"] = "high"
                                    elif len(text_content) < 200:
                                        analysis["complexity"] = "low"
            else:
                # HuggingFace dataset - get from knowledge base
                dataset_info = self.knowledge_base.get_dataset_info(dataset_source)
                if dataset_info:
                    analysis.update(dataset_info)
                else:
                    # Default estimates for unknown HF datasets
                    analysis["size"] = 10000  # Conservative estimate
                    analysis["format"] = "hf_dataset"
        
        except Exception as e:
            logger.warning(f"Failed to analyze dataset {dataset_source}: {e}")
        
        return analysis
    
    def _select_optimal_model(
        self, 
        candidates: List[Dict[str, Any]], 
        task_analysis: Any,
        dataset_analysis: Dict[str, Any],
        request: TrainingRequest
    ) -> Dict[str, Any]:
        """Select the optimal model from candidates."""
        if not candidates:
            raise ValueError("No suitable models found for the task")
        
        # Score each candidate
        scored_candidates = []
        for candidate in candidates:
            score = self._score_model_candidate(
                candidate, task_analysis, dataset_analysis, request
            )
            scored_candidates.append((candidate, score))
        
        # Sort by score (highest first)
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        return scored_candidates[0][0]
    
    def _score_model_candidate(
        self,
        candidate: Dict[str, Any],
        task_analysis: Any,
        dataset_analysis: Dict[str, Any],
        request: TrainingRequest
    ) -> float:
        """Score a model candidate based on suitability."""
        score = 0.0
        
        # Base suitability score
        score += candidate.get("task_suitability", 0.5) * 30
        
        # Quality vs speed tradeoff
        if request.quality_target == "fast":
            score += (1.0 - candidate.get("complexity", 0.5)) * 20
        elif request.quality_target == "high":
            score += candidate.get("quality_score", 0.5) * 20
        else:  # balanced
            score += (candidate.get("quality_score", 0.5) + 
                     (1.0 - candidate.get("complexity", 0.5))) * 10
        
        # Budget considerations
        if request.budget_limit:
            estimated_cost = candidate.get("estimated_cost", float('inf'))
            if estimated_cost <= request.budget_limit:
                score += 15
            else:
                score -= 10
        
        # Time considerations
        if request.time_limit:
            estimated_time = candidate.get("estimated_time", float('inf'))
            if estimated_time <= request.time_limit:
                score += 10
            else:
                score -= 5
        
        # User preferences
        if request.model_preferences:
            for pref in request.model_preferences:
                if pref.lower() in candidate["name"].lower():
                    score += 5
        
        # Dataset size compatibility
        dataset_size = dataset_analysis.get("size", 0)
        if dataset_size > 0:
            optimal_size = candidate.get("optimal_dataset_size", 10000)
            size_ratio = min(dataset_size / optimal_size, optimal_size / dataset_size)
            score += size_ratio * 10
        
        return max(0.0, score)
    
    def _generate_training_config(
        self,
        selected_model: Dict[str, Any],
        task_analysis: Any,
        dataset_analysis: Dict[str, Any],
        request: TrainingRequest
    ) -> TrainingConfig:
        """Generate intelligent training configuration."""
        
        # Base configuration from model defaults
        base_config = selected_model.get("default_config", {})
        
        # Override with intelligent selections
        config_params = {
            "model_name": selected_model["name"],
            "output_dir": f"./training_outputs/{selected_model['name'].replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "training_type": task_analysis.training_type,
            
            # Intelligent parameter selection
            "num_epochs": self._select_num_epochs(dataset_analysis, request),
            "batch_size": self._select_batch_size(selected_model, request),
            "learning_rate": self._select_learning_rate(selected_model, dataset_analysis, request),
            
            # Advanced parameters
            "gradient_accumulation_steps": self._select_gradient_accumulation(selected_model, request),
            "warmup_steps": self._select_warmup_steps(dataset_analysis),
            "weight_decay": base_config.get("weight_decay", 0.01),
            "max_grad_norm": base_config.get("max_grad_norm", 1.0),
        }
        
        # Apply user overrides
        if request.batch_size:
            config_params["batch_size"] = request.batch_size
        if request.learning_rate:
            config_params["learning_rate"] = request.learning_rate
        
        # LoRA configuration
        lora_config = None
        if request.use_lora is not False:  # Default to True unless explicitly False
            lora_config = LoRAConfig(
                use_lora=True,
                lora_rank=self._select_lora_rank(selected_model, request),
                lora_alpha=self._select_lora_alpha(selected_model, request),
                lora_dropout=base_config.get("lora_dropout", 0.05),
                lora_target_modules=selected_model.get("lora_targets", ["q_proj", "v_proj"])
            )
        
        # Dataset configuration
        dataset_config = DatasetConfig(
            dataset_path=request.dataset_source,
            dataset_format=dataset_analysis.get("format", "alpaca"),
            max_length=self._select_max_length(selected_model, task_analysis),
            validation_split=0.1,
            preprocessing_num_workers=4
        )
        
        return TrainingConfig(
            **config_params,
            lora_config=lora_config,
            dataset_config=dataset_config
        )
    
    def _select_num_epochs(self, dataset_analysis: Dict[str, Any], request: TrainingRequest) -> int:
        """Intelligently select number of epochs."""
        dataset_size = dataset_analysis.get("size", 10000)
        
        if request.quality_target == "fast":
            return 1
        elif request.quality_target == "high":
            if dataset_size < 1000:
                return 5
            elif dataset_size < 10000:
                return 3
            else:
                return 2
        else:  # balanced
            if dataset_size < 1000:
                return 3
            elif dataset_size < 10000:
                return 2
            else:
                return 1
    
    def _select_batch_size(self, selected_model: Dict[str, Any], request: TrainingRequest) -> int:
        """Intelligently select batch size."""
        model_size = selected_model.get("parameters", 7_000_000_000)
        
        if model_size > 13_000_000_000:  # 13B+
            return 1
        elif model_size > 7_000_000_000:  # 7B+
            return 2
        else:  # < 7B
            return 4
    
    def _select_learning_rate(
        self, 
        selected_model: Dict[str, Any], 
        dataset_analysis: Dict[str, Any], 
        request: TrainingRequest
    ) -> float:
        """Intelligently select learning rate."""
        base_lr = selected_model.get("default_lr", 2e-5)
        
        # Adjust based on dataset size
        dataset_size = dataset_analysis.get("size", 10000)
        if dataset_size < 1000:
            return base_lr * 0.5  # Lower LR for small datasets
        elif dataset_size > 100000:
            return base_lr * 1.5  # Higher LR for large datasets
        
        return base_lr
    
    def _select_gradient_accumulation(self, selected_model: Dict[str, Any], request: TrainingRequest) -> int:
        """Select gradient accumulation steps."""
        model_size = selected_model.get("parameters", 7_000_000_000)
        
        if model_size > 13_000_000_000:  # 13B+
            return 8
        elif model_size > 7_000_000_000:  # 7B+
            return 4
        else:
            return 2
    
    def _select_warmup_steps(self, dataset_analysis: Dict[str, Any]) -> int:
        """Select warmup steps."""
        dataset_size = dataset_analysis.get("size", 10000)
        return max(10, min(500, dataset_size // 100))
    
    def _select_lora_rank(self, selected_model: Dict[str, Any], request: TrainingRequest) -> int:
        """Select LoRA rank."""
        if request.quality_target == "fast":
            return 4
        elif request.quality_target == "high":
            return 16
        else:  # balanced
            return 8
    
    def _select_lora_alpha(self, selected_model: Dict[str, Any], request: TrainingRequest) -> int:
        """Select LoRA alpha."""
        rank = self._select_lora_rank(selected_model, request)
        return rank * 2  # Common practice: alpha = 2 * rank
    
    def _select_max_length(self, selected_model: Dict[str, Any], task_analysis: Any) -> int:
        """Select maximum sequence length."""
        if task_analysis.task_type == "chat":
            return 2048
        elif task_analysis.task_type == "summarization":
            return 1024
        else:
            return 512
    
    def _predict_quality(
        self, 
        selected_model: Dict[str, Any], 
        training_config: TrainingConfig, 
        dataset_analysis: Dict[str, Any]
    ) -> str:
        """Predict training quality."""
        # Simplified quality prediction
        quality_score = selected_model.get("quality_score", 0.5)
        
        if quality_score > 0.8:
            return "excellent"
        elif quality_score > 0.6:
            return "good"
        else:
            return "fair"
    
    def _calculate_confidence(
        self, 
        selected_model: Dict[str, Any], 
        task_analysis: Any, 
        dataset_analysis: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for recommendation."""
        confidence = 0.7  # Base confidence
        
        # Increase confidence for well-known models
        if selected_model.get("is_popular", False):
            confidence += 0.1
        
        # Increase confidence for good task match
        if selected_model.get("task_suitability", 0.5) > 0.8:
            confidence += 0.1
        
        # Decrease confidence for very small datasets
        if dataset_analysis.get("size", 0) < 100:
            confidence -= 0.2
        
        return max(0.1, min(1.0, confidence))
    
    def _generate_decision_reasons(
        self, 
        selected_model: Dict[str, Any], 
        resource_recommendation: Any, 
        task_analysis: Any
    ) -> List[str]:
        """Generate human-readable reasons for the decision."""
        reasons = []
        
        reasons.append(f"Selected {selected_model['name']} for {task_analysis.task_type} task")
        
        if selected_model.get("is_popular"):
            reasons.append("This model is widely used and well-tested")
        
        if selected_model.get("task_suitability", 0.5) > 0.8:
            reasons.append("Excellent match for your task requirements")
        
        reasons.append(f"Recommended {resource_recommendation.gpu} for optimal performance")
        
        if resource_recommendation.estimated_cost < 100:
            reasons.append("Cost-effective option within budget")
        
        return reasons
    
    def _generate_alternatives(
        self, 
        alternative_models: List[Dict[str, Any]], 
        task_analysis: Any,
        dataset_analysis: Dict[str, Any],
        request: TrainingRequest
    ) -> List[Dict[str, Any]]:
        """Generate alternative recommendations."""
        alternatives = []
        
        for model in alternative_models:
            # Generate simplified config for alternative
            alt_config = {
                "model_name": model["name"],
                "estimated_cost": model.get("estimated_cost", 0.0),
                "estimated_time": model.get("estimated_time", 0),
                "quality_score": model.get("quality_score", 0.5),
                "reason": f"Alternative {model.get('category', 'model')} option"
            }
            alternatives.append(alt_config)
        
        return alternatives
    
    def _store_decision(
        self, 
        request: TrainingRequest, 
        recommendation: TrainingRecommendation, 
        task_analysis: Any
    ) -> None:
        """Store decision for learning and improvement."""
        decision_record = {
            "timestamp": datetime.now().isoformat(),
            "request": {
                "description": request.description,
                "dataset_source": request.dataset_source,
                "quality_target": request.quality_target,
                "budget_limit": request.budget_limit,
                "time_limit": request.time_limit
            },
            "recommendation": {
                "model_name": recommendation.model_name,
                "trainer_type": recommendation.trainer_type,
                "estimated_cost": recommendation.estimated_cost,
                "estimated_time": recommendation.estimated_time,
                "confidence_score": recommendation.confidence_score
            },
            "task_analysis": {
                "task_type": getattr(task_analysis, 'task_type', 'unknown'),
                "domain": getattr(task_analysis, 'domain', 'unknown'),
                "complexity": getattr(task_analysis, 'complexity', 'unknown')
            }
        }
        
        self.decision_history.append(decision_record)
        
        # Keep only last 1000 decisions
        if len(self.decision_history) > 1000:
            self.decision_history = self.decision_history[-1000:]
    
    def get_decision_history(self) -> List[Dict[str, Any]]:
        """Get decision history for analysis."""
        return self.decision_history.copy()
    
    def learn_from_feedback(self, recommendation_id: str, feedback: Dict[str, Any]) -> None:
        """Learn from user feedback to improve future recommendations."""
        # This would implement learning from user feedback
        # For now, just log the feedback
        logger.info(f"Received feedback for recommendation {recommendation_id}: {feedback}")
        # TODO: Implement actual learning mechanism