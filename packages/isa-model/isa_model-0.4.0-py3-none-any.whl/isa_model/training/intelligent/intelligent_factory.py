"""
Intelligent Training Factory

This module provides the main interface for intelligent AI training.
It extends the existing TrainingFactory with AI-powered capabilities:
- Natural language training request parsing
- Intelligent model and resource selection
- Automatic configuration optimization
- Cost and performance prediction

The IntelligentTrainingFactory maintains backward compatibility while
adding advanced intelligence features.
"""

import logging
from typing import Dict, List, Optional, Any, Union
import os
from datetime import datetime

from ..factory import TrainingFactory
from .decision_engine import IntelligentDecisionEngine, TrainingRequest, TrainingRecommendation
from .task_classifier import TaskClassifier
from .knowledge_base import KnowledgeBase
from .resource_optimizer import ResourceOptimizer
from ..core.config import TrainingConfig, LoRAConfig, DatasetConfig

logger = logging.getLogger(__name__)


class IntelligentTrainingFactory(TrainingFactory):
    """
    Intelligent Training Factory with AI-powered optimization.
    
    This factory extends the base TrainingFactory with intelligent capabilities:
    - Analyzes natural language training requests
    - Automatically selects optimal models and configurations
    - Provides cost and performance predictions
    - Recommends best practices and alternatives
    
    Maintains full backward compatibility with existing TrainingFactory API
    while adding new intelligent features.
    
    Example:
        ```python
        from isa_model.training.intelligent import IntelligentTrainingFactory
        
        # Create intelligent factory
        factory = IntelligentTrainingFactory()
        
        # Traditional usage (backward compatible)
        model_path = factory.train_model(
            model_name="google/gemma-2-4b-it",
            dataset_path="tatsu-lab/alpaca"
        )
        
        # Intelligent usage with natural language
        recommendation = factory.analyze_training_request(
            "Train a Chinese customer service chatbot with high quality",
            dataset_path="my-chinese-dialogues.json",
            budget_limit=500.0,
            time_limit=12
        )
        
        # Train with intelligent recommendation
        model_path = factory.train_with_recommendation(recommendation)
        ```
    """
    
    def __init__(self, 
                 base_output_dir: Optional[str] = None,
                 enable_intelligence: bool = True,
                 knowledge_base_dir: Optional[str] = None,
                 resource_data_dir: Optional[str] = None):
        """
        Initialize intelligent training factory.
        
        Args:
            base_output_dir: Base directory for training outputs
            enable_intelligence: Enable intelligent features
            knowledge_base_dir: Directory for knowledge base data
            resource_data_dir: Directory for resource data
        """
        # Initialize base factory
        super().__init__(base_output_dir)
        
        self.enable_intelligence = enable_intelligence
        
        if enable_intelligence:
            try:
                # Initialize intelligent components
                self.knowledge_base = KnowledgeBase(knowledge_base_dir)
                self.task_classifier = TaskClassifier()
                self.resource_optimizer = ResourceOptimizer(resource_data_dir)
                self.decision_engine = IntelligentDecisionEngine(self.knowledge_base)
                
                # Initialize training data management
                from ..storage import TrainingRepository, CoreModelIntegration
                self.training_repository = TrainingRepository()
                self.core_integration = self.training_repository.core_integration
                
                # Store recommendations for learning
                self.recent_recommendations: List[TrainingRecommendation] = []
                
                logger.info("Intelligent Training Factory initialized with AI capabilities and data persistence")
                self._print_welcome_message()
                
            except Exception as e:
                logger.warning(f"Failed to initialize intelligent components: {e}")
                logger.warning("Falling back to standard training factory mode")
                self.enable_intelligence = False
        else:
            logger.info("Intelligent Training Factory initialized in standard mode")
    
    def _print_welcome_message(self) -> None:
        """Print welcome message with intelligent capabilities."""
        stats = self.knowledge_base.get_statistics()
        resource_stats = self.resource_optimizer.get_statistics()
        
        print("\n" + "="*60)
        print("🧠 INTELLIGENT TRAINING FACTORY READY")
        print("="*60)
        print(f"📚 Knowledge Base: {stats['total_models']} models, {stats['best_practices']} best practices")
        print(f"🖥️  Resource Pool: {resource_stats['total_gpus']} GPUs, {resource_stats['total_providers']} providers")
        print(f"🎯 Task Support: {len(self.task_classifier.get_supported_tasks())} task types")
        print(f"🌍 Domain Support: {len(self.task_classifier.get_supported_domains())} domains")
        print("="*60)
        print("New capabilities available:")
        print("  • analyze_training_request() - Natural language analysis")
        print("  • get_intelligent_recommendation() - Smart configuration")
        print("  • train_with_recommendation() - Optimized training")
        print("  • compare_training_options() - Cost/performance comparison")
        print("="*60 + "\n")
    
    def analyze_training_request(
        self,
        description: str,
        dataset_source: str,
        quality_target: str = "balanced",
        budget_limit: Optional[float] = None,
        time_limit: Optional[int] = None,
        **preferences
    ) -> TrainingRecommendation:
        """
        Analyze a natural language training request and generate recommendation.
        
        Args:
            description: Natural language description of the training task
            dataset_source: Path to dataset or HuggingFace dataset name
            quality_target: Quality target ("fast", "balanced", "high")
            budget_limit: Maximum budget in USD
            time_limit: Maximum time in hours
            **preferences: Additional user preferences
            
        Returns:
            Complete training recommendation with configuration
            
        Example:
            ```python
            recommendation = factory.analyze_training_request(
                "Fine-tune a medical chatbot for patient Q&A in Chinese",
                dataset_source="medical_qa_chinese.json",
                quality_target="high",
                budget_limit=300.0,
                time_limit=8
            )
            ```
        """
        if not self.enable_intelligence:
            raise ValueError("Intelligence features not available. Initialize with enable_intelligence=True")
        
        logger.info(f"Analyzing training request: {description[:50]}...")
        
        try:
            # Create training request object
            request = TrainingRequest(
                description=description,
                dataset_source=dataset_source,
                quality_target=quality_target,
                budget_limit=budget_limit,
                time_limit=time_limit,
                model_preferences=preferences.get("model_preferences"),
                gpu_preferences=preferences.get("gpu_preferences"),
                cloud_preferences=preferences.get("cloud_preferences"),
                use_lora=preferences.get("use_lora"),
                batch_size=preferences.get("batch_size"),
                learning_rate=preferences.get("learning_rate"),
                user_id=preferences.get("user_id"),
                project_name=preferences.get("project_name"),
                tags=preferences.get("tags", {})
            )
            
            # Generate intelligent recommendation
            recommendation = self.decision_engine.analyze_and_recommend(request)
            
            # Store for learning
            self.recent_recommendations.append(recommendation)
            
            # Print summary
            self._print_recommendation_summary(recommendation)
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Failed to analyze training request: {e}")
            raise
    
    def get_intelligent_recommendation(
        self,
        task_type: str,
        domain: str = "general",
        dataset_size: int = 10000,
        quality_target: str = "balanced",
        **constraints
    ) -> TrainingRecommendation:
        """
        Get intelligent recommendation for specific task parameters.
        
        Args:
            task_type: Type of task (chat, classification, etc.)
            domain: Domain/industry
            dataset_size: Size of training dataset
            quality_target: Quality target ("fast", "balanced", "high")
            **constraints: Additional constraints
            
        Returns:
            Training recommendation
        """
        if not self.enable_intelligence:
            raise ValueError("Intelligence features not available")
        
        # Create synthetic request
        description = f"Train a {task_type} model for {domain} domain"
        
        return self.analyze_training_request(
            description=description,
            dataset_source="synthetic_dataset",
            quality_target=quality_target,
            **constraints
        )
    
    def train_with_recommendation(
        self,
        recommendation: TrainingRecommendation,
        dataset_path: Optional[str] = None,
        output_dir: Optional[str] = None,
        user_id: Optional[str] = None,
        project_name: Optional[str] = None,
        **overrides
    ) -> str:
        """
        Train a model using an intelligent recommendation with full tracking.
        
        Args:
            recommendation: Training recommendation from analyze_training_request()
            dataset_path: Override dataset path
            output_dir: Override output directory
            user_id: User identifier for tracking
            project_name: Project name for organization
            **overrides: Override specific configuration parameters
            
        Returns:
            Path to trained model
            
        Example:
            ```python
            # Get recommendation
            rec = factory.analyze_training_request(
                "Train a customer service chatbot",
                "customer_service_data.json"
            )
            
            # Train with recommendation and tracking
            model_path = factory.train_with_recommendation(
                rec, 
                user_id="user_123",
                project_name="medical_chatbot"
            )
            ```
        """
        logger.info(f"Training with intelligent recommendation: {recommendation.model_name}")
        
        job_id = None
        
        try:
            # Create training job record if repository is available
            if hasattr(self, 'training_repository'):
                job_id = self.training_repository.create_training_job(
                    job_name=f"{recommendation.model_name.split('/')[-1]}_training",
                    base_model=recommendation.model_name,
                    task_type=recommendation.trainer_type,
                    domain="general",  # TODO: Extract from recommendation
                    dataset_source=dataset_path or recommendation.training_config.dataset_config.dataset_path,
                    training_config=recommendation.training_config.to_dict(),
                    resource_config={
                        "gpu": recommendation.recommended_gpu,
                        "cloud_provider": recommendation.cloud_provider,
                        "estimated_cost": recommendation.estimated_cost,
                        "estimated_time": recommendation.estimated_time
                    },
                    user_id=user_id,
                    project_name=project_name
                )
                
                # Update job status to running
                self.training_repository.update_job_status(job_id, "running")
            
            # Get configuration from recommendation
            config = recommendation.training_config
            
            # Apply overrides
            if dataset_path:
                config.dataset_config.dataset_path = dataset_path
            if output_dir:
                config.output_dir = output_dir
            
            for key, value in overrides.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                elif config.lora_config and hasattr(config.lora_config, key):
                    setattr(config.lora_config, key, value)
                elif config.dataset_config and hasattr(config.dataset_config, key):
                    setattr(config.dataset_config, key, value)
            
            # Use base factory training with optimized config
            result_path = self.train_model(
                model_name=config.model_name,
                dataset_path=config.dataset_config.dataset_path,
                output_dir=config.output_dir,
                training_type=config.training_type,
                dataset_format=config.dataset_config.dataset_format,
                use_lora=config.lora_config.use_lora if config.lora_config else False,
                batch_size=config.batch_size,
                num_epochs=config.num_epochs,
                learning_rate=config.learning_rate,
                max_length=config.dataset_config.max_length,
                lora_rank=config.lora_config.lora_rank if config.lora_config else 8,
                lora_alpha=config.lora_config.lora_alpha if config.lora_config else 16,
                validation_split=config.dataset_config.validation_split
            )
            
            # Complete training and register model
            if hasattr(self, 'training_repository') and job_id:
                core_model_id = self.training_repository.complete_training(
                    job_id=job_id,
                    model_path=result_path,
                    final_metrics={"training_completed": True},  # TODO: Extract real metrics
                    cost_breakdown={"total": recommendation.estimated_cost}
                )
                
                if core_model_id:
                    logger.info(f"Model registered in core system: {core_model_id}")
            
            # Update knowledge base with results
            if self.enable_intelligence:
                self._update_knowledge_from_training(recommendation, result_path)
            
            logger.info("Training completed with intelligent recommendation")
            return result_path
            
        except Exception as e:
            # Mark job as failed if it was created
            if hasattr(self, 'training_repository') and job_id:
                self.training_repository.update_job_status(
                    job_id, 
                    "failed", 
                    error_message=str(e)
                )
            
            logger.error(f"Training with recommendation failed: {e}")
            raise
    
    def train_on_runpod_intelligent(
        self,
        description: str,
        dataset_path: str,
        runpod_api_key: str,
        template_id: str,
        quality_target: str = "balanced",
        budget_limit: Optional[float] = None,
        time_limit: Optional[int] = None,
        **preferences
    ) -> Dict[str, Any]:
        """
        Intelligent cloud training on RunPod.
        
        Combines natural language analysis with cloud training.
        
        Args:
            description: Natural language description
            dataset_path: Dataset path
            runpod_api_key: RunPod API key
            template_id: RunPod template ID
            quality_target: Quality target
            budget_limit: Budget limit
            time_limit: Time limit
            **preferences: Additional preferences
            
        Returns:
            Training job results
        """
        if not self.enable_intelligence:
            # Fallback to base implementation
            return self.train_on_runpod(
                model_name=preferences.get("model_name", "google/gemma-2-4b-it"),
                dataset_path=dataset_path,
                runpod_api_key=runpod_api_key,
                template_id=template_id,
                **preferences
            )
        
        logger.info("Starting intelligent cloud training on RunPod")
        
        try:
            # Get intelligent recommendation
            recommendation = self.analyze_training_request(
                description=description,
                dataset_source=dataset_path,
                quality_target=quality_target,
                budget_limit=budget_limit,
                time_limit=time_limit,
                **preferences
            )
            
            # Extract configuration
            config = recommendation.training_config
            
            # Use base RunPod training with intelligent config
            result = self.train_on_runpod(
                model_name=config.model_name,
                dataset_path=dataset_path,
                runpod_api_key=runpod_api_key,
                template_id=template_id,
                gpu_type=recommendation.recommended_gpu,
                use_lora=config.lora_config.use_lora if config.lora_config else True,
                batch_size=config.batch_size,
                num_epochs=config.num_epochs,
                learning_rate=config.learning_rate,
                max_length=config.dataset_config.max_length,
                lora_rank=config.lora_config.lora_rank if config.lora_config else 8,
                lora_alpha=config.lora_config.lora_alpha if config.lora_config else 16
            )
            
            # Add intelligent metadata to result
            result["intelligent_recommendation"] = {
                "model_name": recommendation.model_name,
                "estimated_cost": recommendation.estimated_cost,
                "estimated_time": recommendation.estimated_time,
                "confidence": recommendation.confidence_score,
                "decision_reasons": recommendation.decision_reasons
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Intelligent cloud training failed: {e}")
            raise
    
    def compare_training_options(
        self,
        description: str,
        dataset_source: str,
        quality_targets: List[str] = ["fast", "balanced", "high"],
        budget_limits: Optional[List[float]] = None
    ) -> List[TrainingRecommendation]:
        """
        Compare multiple training options for the same task.
        
        Args:
            description: Training task description
            dataset_source: Dataset source
            quality_targets: List of quality targets to compare
            budget_limits: Optional budget limits for each target
            
        Returns:
            List of recommendations for comparison
        """
        if not self.enable_intelligence:
            raise ValueError("Intelligence features not available")
        
        logger.info("Comparing training options...")
        
        recommendations = []
        budget_limits = budget_limits or [None] * len(quality_targets)
        
        for i, quality_target in enumerate(quality_targets):
            budget_limit = budget_limits[i] if i < len(budget_limits) else None
            
            try:
                rec = self.analyze_training_request(
                    description=description,
                    dataset_source=dataset_source,
                    quality_target=quality_target,
                    budget_limit=budget_limit
                )
                recommendations.append(rec)
            except Exception as e:
                logger.warning(f"Failed to generate recommendation for {quality_target}: {e}")
        
        # Print comparison table
        self._print_comparison_table(recommendations)
        
        return recommendations
    
    def get_best_practices(self, task_type: str, domain: str = "general") -> List[str]:
        """
        Get best practices for a specific task and domain.
        
        Args:
            task_type: Type of task
            domain: Domain/industry
            
        Returns:
            List of best practice recommendations
        """
        if not self.enable_intelligence:
            return ["Enable intelligence features to get best practices"]
        
        practices = self.knowledge_base.get_best_practices(task_type, domain)
        return [p.recommendation for p in practices]
    
    def get_supported_capabilities(self) -> Dict[str, List[str]]:
        """
        Get supported capabilities of the intelligent training system.
        
        Returns:
            Dictionary of supported capabilities
        """
        if not self.enable_intelligence:
            return {"status": "Intelligence features disabled"}
        
        return {
            "task_types": self.task_classifier.get_supported_tasks(),
            "domains": self.task_classifier.get_supported_domains(),
            "gpu_types": self.resource_optimizer.get_available_gpus(),
            "cloud_providers": self.resource_optimizer.get_available_providers(),
            "quality_targets": ["fast", "balanced", "high"]
        }
    
    def _print_recommendation_summary(self, recommendation: TrainingRecommendation) -> None:
        """Print a summary of the recommendation."""
        print("\n" + "="*50)
        print("🎯 INTELLIGENT TRAINING RECOMMENDATION")
        print("="*50)
        print(f"📱 Model: {recommendation.model_name}")
        print(f"🖥️  GPU: {recommendation.recommended_gpu}")
        print(f"☁️  Cloud: {recommendation.cloud_provider}")
        print(f"💰 Cost: ${recommendation.estimated_cost:.2f}")
        print(f"⏱️  Time: {recommendation.estimated_time:.1f} hours")
        print(f"🎨 Quality: {recommendation.predicted_quality}")
        print(f"🎯 Confidence: {recommendation.confidence_score:.1%}")
        print("\n📋 Key Decisions:")
        for reason in recommendation.decision_reasons:
            print(f"  • {reason}")
        
        if recommendation.alternatives:
            print(f"\n🔄 {len(recommendation.alternatives)} alternatives available")
        
        print("="*50 + "\n")
    
    def _print_comparison_table(self, recommendations: List[TrainingRecommendation]) -> None:
        """Print comparison table for multiple recommendations."""
        print("\n" + "="*80)
        print("📊 TRAINING OPTIONS COMPARISON")
        print("="*80)
        
        # Table header
        print(f"{'Target':<10} {'Model':<25} {'GPU':<15} {'Cost':<8} {'Time':<6} {'Quality'}")
        print("-" * 80)
        
        # Table rows
        for rec in recommendations:
            quality_target = "unknown"
            if rec.estimated_cost < 50:
                quality_target = "fast"
            elif rec.estimated_cost > 200:
                quality_target = "high"
            else:
                quality_target = "balanced"
            
            print(f"{quality_target:<10} {rec.model_name[:24]:<25} {rec.recommended_gpu[:14]:<15} "
                  f"${rec.estimated_cost:<7.2f} {rec.estimated_time:<5.1f}h {rec.predicted_quality}")
        
        print("="*80 + "\n")
    
    def _update_knowledge_from_training(
        self, 
        recommendation: TrainingRecommendation, 
        result_path: str
    ) -> None:
        """Update knowledge base with training results."""
        try:
            # Create training result record
            training_result = {
                "model_name": recommendation.model_name,
                "task_type": recommendation.trainer_type,
                "dataset_name": "user_dataset",
                "training_cost": recommendation.estimated_cost,
                "gpu_type": recommendation.recommended_gpu,
                "config": recommendation.training_config.to_dict(),
                "result_path": result_path,
                "timestamp": datetime.now().isoformat()
            }
            
            # Update knowledge base
            self.knowledge_base.update_from_training_result(training_result)
            
            logger.info("Updated knowledge base with training results")
            
        except Exception as e:
            logger.warning(f"Failed to update knowledge base: {e}")
    
    def get_intelligence_statistics(self) -> Dict[str, Any]:
        """Get statistics about the intelligent training system."""
        if not self.enable_intelligence:
            return {"status": "Intelligence features disabled"}
        
        kb_stats = self.knowledge_base.get_statistics()
        resource_stats = self.resource_optimizer.get_statistics()
        
        stats = {
            "intelligence_enabled": True,
            "knowledge_base": kb_stats,
            "resource_optimizer": resource_stats,
            "recent_recommendations": len(self.recent_recommendations),
            "supported_tasks": len(self.task_classifier.get_supported_tasks()),
            "supported_domains": len(self.task_classifier.get_supported_domains())
        }
        
        # Add training repository statistics if available
        if hasattr(self, 'training_repository'):
            try:
                repo_stats = self.training_repository.get_repository_statistics()
                stats["training_repository"] = repo_stats
            except Exception as e:
                stats["training_repository"] = {"error": str(e)}
        
        return stats
    
    def get_training_history(self, user_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get training history with intelligent insights.
        
        Args:
            user_id: Filter by user ID
            limit: Maximum number of jobs to return
            
        Returns:
            List of training job summaries with insights
        """
        if not hasattr(self, 'training_repository'):
            return []
        
        try:
            jobs = self.training_repository.list_jobs(user_id=user_id, limit=limit)
            
            history = []
            for job in jobs:
                job_summary = {
                    "job_id": job.job_id,
                    "job_name": job.job_name,
                    "status": job.status,
                    "base_model": job.base_model,
                    "task_type": job.task_type,
                    "domain": job.domain,
                    "created_at": job.created_at.isoformat(),
                    "user_id": job.user_id,
                    "project_name": job.project_name
                }
                
                if job.completed_at:
                    job_summary["completed_at"] = job.completed_at.isoformat()
                    
                if job.cost_breakdown:
                    job_summary["total_cost"] = sum(job.cost_breakdown.values())
                
                # Add progress information
                progress = self.training_repository.get_job_progress(job.job_id)
                if progress:
                    job_summary["progress"] = progress
                
                history.append(job_summary)
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get training history: {e}")
            return []
    
    def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """
        Get intelligent insights for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            User insights and recommendations
        """
        if not hasattr(self, 'training_repository'):
            return {"error": "Training repository not available"}
        
        try:
            # Get user statistics
            user_stats = self.training_repository.get_user_statistics(user_id)
            
            # Get user's training history
            user_jobs = self.training_repository.list_jobs(user_id=user_id, limit=100)
            
            # Analyze patterns
            insights = {
                "user_statistics": user_stats,
                "patterns": self._analyze_user_patterns(user_jobs),
                "recommendations": self._generate_user_recommendations(user_jobs),
                "cost_optimization": self._analyze_cost_optimization(user_jobs)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get user insights for {user_id}: {e}")
            return {"error": str(e)}
    
    def _analyze_user_patterns(self, jobs: List) -> Dict[str, Any]:
        """Analyze user training patterns."""
        if not jobs:
            return {}
        
        patterns = {
            "most_used_models": {},
            "preferred_tasks": {},
            "preferred_domains": {},
            "average_cost": 0.0,
            "cost_trend": "stable"
        }
        
        total_cost = 0.0
        recent_costs = []
        
        for job in jobs:
            # Count model usage
            model = job.base_model
            patterns["most_used_models"][model] = patterns["most_used_models"].get(model, 0) + 1
            
            # Count task types
            task = job.task_type
            patterns["preferred_tasks"][task] = patterns["preferred_tasks"].get(task, 0) + 1
            
            # Count domains
            domain = job.domain
            patterns["preferred_domains"][domain] = patterns["preferred_domains"].get(domain, 0) + 1
            
            # Track costs
            if job.cost_breakdown:
                cost = sum(job.cost_breakdown.values())
                total_cost += cost
                recent_costs.append(cost)
        
        patterns["average_cost"] = total_cost / len(jobs) if jobs else 0.0
        
        # Analyze cost trend (simplified)
        if len(recent_costs) > 1:
            first_half = recent_costs[:len(recent_costs)//2]
            second_half = recent_costs[len(recent_costs)//2:]
            
            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)
            
            if avg_second > avg_first * 1.2:
                patterns["cost_trend"] = "increasing"
            elif avg_second < avg_first * 0.8:
                patterns["cost_trend"] = "decreasing"
        
        return patterns
    
    def _generate_user_recommendations(self, jobs: List) -> List[str]:
        """Generate recommendations for the user based on their history."""
        if not jobs:
            return ["Start with a simple chat model training to get familiar with the system"]
        
        recommendations = []
        
        # Analyze success rate
        completed_jobs = [job for job in jobs if job.status == "completed"]
        success_rate = len(completed_jobs) / len(jobs) if jobs else 0
        
        if success_rate < 0.5:
            recommendations.append("Consider using smaller models or LoRA training to improve success rate")
        
        # Check for cost optimization opportunities
        high_cost_jobs = [job for job in jobs if job.cost_breakdown and sum(job.cost_breakdown.values()) > 50]
        if len(high_cost_jobs) > len(jobs) * 0.3:
            recommendations.append("Consider using more cost-effective GPU options or shorter training times")
        
        # Check for domain diversity
        domains = set(job.domain for job in jobs)
        if len(domains) == 1 and len(jobs) > 5:
            recommendations.append("Try training models for different domains to expand your capabilities")
        
        # Check for recent failures
        recent_jobs = jobs[:5]  # Last 5 jobs
        recent_failures = [job for job in recent_jobs if job.status == "failed"]
        if len(recent_failures) > 2:
            recommendations.append("Recent training failures detected - consider using the intelligent recommendations for more reliable configurations")
        
        return recommendations
    
    def _analyze_cost_optimization(self, jobs: List) -> Dict[str, Any]:
        """Analyze cost optimization opportunities."""
        if not jobs:
            return {}
        
        total_cost = 0.0
        potential_savings = 0.0
        
        for job in jobs:
            if job.cost_breakdown:
                job_cost = sum(job.cost_breakdown.values())
                total_cost += job_cost
                
                # Estimate potential savings with intelligent optimization
                # This is a simplified calculation
                if job_cost > 10:  # Only for jobs that cost more than $10
                    potential_savings += job_cost * 0.3  # Assume 30% savings possible
        
        return {
            "total_spent": total_cost,
            "potential_savings": potential_savings,
            "optimization_percentage": (potential_savings / total_cost * 100) if total_cost > 0 else 0,
            "recommendation": "Use intelligent training recommendations to optimize costs" if potential_savings > 5 else "Your costs are already well optimized"
        }
    
    def save_recommendation(self, recommendation: TrainingRecommendation, filename: str) -> None:
        """
        Save a training recommendation to file.
        
        Args:
            recommendation: Training recommendation to save
            filename: Output filename
        """
        try:
            import json
            from dataclasses import asdict
            
            # Convert recommendation to dict
            rec_dict = asdict(recommendation)
            
            # Convert datetime objects to strings
            def convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return obj
            
            # Save to file
            with open(filename, 'w') as f:
                json.dump(rec_dict, f, indent=2, default=convert_datetime)
            
            logger.info(f"Recommendation saved to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save recommendation: {e}")
            raise
    
    def load_recommendation(self, filename: str) -> TrainingRecommendation:
        """
        Load a training recommendation from file.
        
        Args:
            filename: Input filename
            
        Returns:
            Loaded training recommendation
        """
        try:
            import json
            
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Convert back to TrainingRecommendation
            # Note: This is a simplified version - would need proper deserialization
            # for complex objects like TrainingConfig
            
            logger.info(f"Recommendation loaded from {filename}")
            return data  # Return dict for now
            
        except Exception as e:
            logger.error(f"Failed to load recommendation: {e}")
            raise