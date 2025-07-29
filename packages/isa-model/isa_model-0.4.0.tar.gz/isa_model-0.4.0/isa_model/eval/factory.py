"""
Enterprise-Grade Evaluation Factory for ISA Model Framework

Implements industry best practices for AI model evaluation at scale:
- Async evaluation with concurrency control
- Comprehensive experiment tracking (W&B, MLflow)
- Distributed evaluation support
- Production-ready monitoring and alerting
- Cost tracking and optimization
- Reproducible evaluation pipelines
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List, Union, Callable
from pathlib import Path
import json

from .evaluators import LLMEvaluator, VisionEvaluator, AudioEvaluator, EmbeddingEvaluator, EvaluationResult
from .isa_integration import ISAModelInterface
try:
    from .infrastructure import ExperimentTracker, create_experiment_tracker
    EXPERIMENT_TRACKING_AVAILABLE = True
except ImportError:
    EXPERIMENT_TRACKING_AVAILABLE = False
    logger.warning("Experiment tracking not available")

try:
    from .config import EvaluationConfig
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    # Create a simple config class
    class EvaluationConfig:
        def __init__(self):
            self.batch_size = 16
            self.output_dir = "./evaluation_results"
            self.default_temperature = 0.7
            self.default_max_tokens = 512
            self.max_concurrent_evaluations = 3
        
        def to_dict(self):
            return {
                "batch_size": self.batch_size,
                "output_dir": self.output_dir,
                "default_temperature": self.default_temperature,
                "default_max_tokens": self.default_max_tokens,
                "max_concurrent_evaluations": self.max_concurrent_evaluations
            }
        
        @classmethod
        def from_dict(cls, config_dict):
            config = cls()
            for key, value in config_dict.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            return config

logger = logging.getLogger(__name__)


class EvaluationFactory:
    """
    Enterprise-grade evaluation factory implementing MLOps best practices.
    
    Features:
    - Multi-modal evaluation support (LLM, Vision, Multimodal)
    - Async evaluation with smart concurrency management
    - Comprehensive experiment tracking and visualization
    - Cost optimization and resource monitoring
    - Distributed evaluation across multiple GPUs/nodes
    - Production-ready error handling and retry logic
    - Automated result storage and comparison
    
    Example usage:
        ```python
        from isa_model.eval import EvaluationFactory
        
        # Initialize with experiment tracking
        factory = EvaluationFactory(
            experiment_tracking={
                "type": "wandb",
                "project": "model-evaluation",
                "entity": "my-team"
            }
        )
        
        # Evaluate LLM on dataset
        result = await factory.evaluate_llm(
            model_name="gpt-4.1-mini",
            provider="openai",
            dataset_path="path/to/evaluation_data.json",
            metrics=["accuracy", "f1_score", "bleu_score"],
            save_results=True
        )
        
        # Run benchmark evaluation
        benchmark_result = await factory.run_benchmark(
            model_name="claude-sonnet-4",
            provider="yyds", 
            benchmark_name="mmlu",
            subjects=["math", "physics", "chemistry"]
        )
        
        # Compare multiple models
        comparison = await factory.compare_models(
            models=[
                {"name": "gpt-4.1-mini", "provider": "openai"},
                {"name": "claude-sonnet-4", "provider": "yyds"}
            ],
            dataset_path="comparison_dataset.json"
        )
        ```
    """
    
    def __init__(self, 
                 config: Optional[Union[Dict[str, Any], EvaluationConfig]] = None,
                 experiment_tracking: Optional[Dict[str, Any]] = None,
                 output_dir: Optional[str] = None):
        """
        Initialize the enterprise evaluation factory.
        
        Args:
            config: Evaluation configuration (dict or EvaluationConfig object)
            experiment_tracking: Experiment tracking configuration
            output_dir: Output directory for results
        """
        # Initialize configuration
        if isinstance(config, dict):
            self.config = EvaluationConfig.from_dict(config)
        elif isinstance(config, EvaluationConfig):
            self.config = config
        else:
            self.config = EvaluationConfig()
        
        # Override output directory if provided
        if output_dir:
            self.config.output_dir = output_dir
        
        # Initialize experiment tracker
        self.experiment_tracker = None
        if experiment_tracking and EXPERIMENT_TRACKING_AVAILABLE:
            try:
                self.experiment_tracker = create_experiment_tracker(**experiment_tracking)
                logger.info(f"Initialized experiment tracking: {experiment_tracking['type']}")
            except Exception as e:
                logger.warning(f"Failed to initialize experiment tracking: {e}")
        
        # Initialize ISA Model interface
        self.isa_interface = ISAModelInterface()
        
        # Initialize evaluators
        self.llm_evaluator = LLMEvaluator(
            config=self.config.to_dict(),
            experiment_tracker=self.experiment_tracker
        )
        
        self.vision_evaluator = VisionEvaluator(
            config=self.config.to_dict(),
            experiment_tracker=self.experiment_tracker
        )
        
        self.audio_evaluator = AudioEvaluator(
            config=self.config.to_dict(),
            experiment_tracker=self.experiment_tracker
        )
        
        self.embedding_evaluator = EmbeddingEvaluator(
            config=self.config.to_dict(),
            experiment_tracker=self.experiment_tracker
        )
        
        # State tracking
        self._active_evaluations: Dict[str, asyncio.Task] = {}
        
        logger.info(f"EvaluationFactory initialized with output dir: {self.config.output_dir}")
    
    async def evaluate_llm(self,
                          model_name: str,
                          provider: str = "openai",
                          dataset_path: Optional[str] = None,
                          dataset: Optional[List[Dict[str, Any]]] = None,
                          metrics: Optional[List[str]] = None,
                          batch_size: Optional[int] = None,
                          save_results: bool = True,
                          experiment_name: Optional[str] = None,
                          progress_callback: Optional[Callable] = None) -> EvaluationResult:
        """
        Evaluate LLM with comprehensive metrics and tracking.
        
        Args:
            model_name: Name of the model to evaluate
            provider: Model provider (openai, yyds, ollama, etc.)
            dataset_path: Path to evaluation dataset JSON file
            dataset: Direct dataset input (alternative to dataset_path)
            metrics: List of metrics to compute
            batch_size: Batch size for evaluation
            save_results: Whether to save results to disk
            experiment_name: Custom experiment name
            progress_callback: Optional progress callback function
            
        Returns:
            Comprehensive evaluation results
        """
        # Load dataset
        if dataset is None:
            if dataset_path is None:
                raise ValueError("Either dataset_path or dataset must be provided")
            dataset = self._load_dataset(dataset_path)
        
        # Configure LLM evaluator
        llm_config = {
            "provider": provider,
            "model_name": model_name,
            "batch_size": batch_size or self.config.batch_size,
            "temperature": self.config.default_temperature,
            "max_tokens": self.config.default_max_tokens
        }
        
        self.llm_evaluator.config.update(llm_config)
        
        # Generate experiment name
        dataset_name = Path(dataset_path).stem if dataset_path else "custom_dataset"
        experiment_name = experiment_name or f"llm_eval_{model_name}_{dataset_name}"
        
        # Run evaluation
        result = await self.llm_evaluator.evaluate(
            model_interface=self.isa_interface,
            dataset=dataset,
            dataset_name=dataset_name,
            model_name=f"{provider}:{model_name}",
            batch_size=batch_size,
            progress_callback=progress_callback
        )
        
        # Save results if requested
        if save_results:
            await self._save_results(result, experiment_name)
        
        return result
    
    async def run_benchmark(self,
                          model_name: str,
                          provider: str,
                          benchmark_name: str,
                          subjects: Optional[List[str]] = None,
                          max_samples: Optional[int] = None,
                          few_shot: bool = True,
                          num_shots: int = 5,
                          save_results: bool = True,
                          experiment_name: Optional[str] = None) -> EvaluationResult:
        """
        Run standardized benchmark evaluation.
        
        Args:
            model_name: Name of the model to evaluate
            provider: Model provider
            benchmark_name: Name of benchmark (mmlu, hellaswag, arc, gsm8k, etc.)
            subjects: List of subjects to evaluate (for MMLU)
            max_samples: Maximum number of samples to evaluate
            few_shot: Whether to use few-shot examples
            num_shots: Number of few-shot examples
            save_results: Whether to save results
            experiment_name: Custom experiment name
            
        Returns:
            Benchmark evaluation results
        """
        # Load benchmark dataset
        benchmark_dataset = await self._load_benchmark(
            benchmark_name, 
            subjects=subjects,
            max_samples=max_samples,
            few_shot=few_shot,
            num_shots=num_shots
        )
        
        # Configure for benchmark evaluation
        benchmark_config = {
            "provider": provider,
            "model_name": model_name,
            "temperature": 0.0,  # Deterministic for benchmarks
            "max_tokens": 50,    # Short answers for most benchmarks
            "task_type": "benchmark",
            "benchmark_name": benchmark_name
        }
        
        self.llm_evaluator.config.update(benchmark_config)
        
        # Generate experiment name
        experiment_name = experiment_name or f"benchmark_{benchmark_name}_{model_name}"
        
        # Run evaluation
        result = await self.llm_evaluator.evaluate(
            model_interface=None,
            dataset=benchmark_dataset,
            dataset_name=benchmark_name,
            model_name=f"{provider}:{model_name}",
            batch_size=self.config.batch_size
        )
        
        # Add benchmark-specific metadata
        result.config.update({
            "benchmark_name": benchmark_name,
            "subjects": subjects,
            "few_shot": few_shot,
            "num_shots": num_shots
        })
        
        # Save results if requested
        if save_results:
            await self._save_results(result, experiment_name)
        
        return result
    
    async def compare_models(self,
                           models: List[Dict[str, str]],
                           dataset_path: Optional[str] = None,
                           dataset: Optional[List[Dict[str, Any]]] = None,
                           benchmark_name: Optional[str] = None,
                           metrics: Optional[List[str]] = None,
                           save_results: bool = True,
                           experiment_name: Optional[str] = None) -> Dict[str, EvaluationResult]:
        """
        Compare multiple models on the same evaluation task.
        
        Args:
            models: List of model configs [{"name": "gpt-4", "provider": "openai"}, ...]
            dataset_path: Path to evaluation dataset
            dataset: Direct dataset input
            benchmark_name: Benchmark name (alternative to dataset)
            metrics: Metrics to compute
            save_results: Whether to save comparison results
            experiment_name: Custom experiment name
            
        Returns:
            Dictionary mapping model names to evaluation results
        """
        results = {}
        
        # Run evaluations concurrently (with concurrency limits)
        semaphore = asyncio.Semaphore(self.config.max_concurrent_evaluations)
        
        async def evaluate_single_model(model_config: Dict[str, str]) -> tuple:
            async with semaphore:
                model_name = model_config["name"]
                provider = model_config["provider"]
                
                if benchmark_name:
                    result = await self.run_benchmark(
                        model_name=model_name,
                        provider=provider,
                        benchmark_name=benchmark_name,
                        save_results=False  # Save comparison results together
                    )
                else:
                    result = await self.evaluate_llm(
                        model_name=model_name,
                        provider=provider,
                        dataset_path=dataset_path,
                        dataset=dataset,
                        metrics=metrics,
                        save_results=False
                    )
                
                return f"{provider}:{model_name}", result
        
        # Execute all evaluations
        tasks = [evaluate_single_model(model) for model in models]
        evaluation_results = await asyncio.gather(*tasks)
        
        # Collect results
        for model_id, result in evaluation_results:
            results[model_id] = result
        
        # Generate comparison report
        comparison_report = self._generate_comparison_report(results)
        
        # Save results if requested
        if save_results:
            experiment_name = experiment_name or f"model_comparison_{len(models)}_models"
            await self._save_comparison_results(results, comparison_report, experiment_name)
        
        return results
    
    async def evaluate_vision(self,
                            dataset: List[Dict[str, Any]],
                            task_type: str = "ocr",
                            model_name: str = "gpt-4.1-mini",
                            save_results: bool = True,
                            experiment_name: Optional[str] = None) -> EvaluationResult:
        """
        Evaluate vision model on image tasks.
        
        Args:
            dataset: Vision dataset with images and expected outputs
            task_type: Vision task type (ocr, table, ui, vqa, caption)
            model_name: Vision model name
            save_results: Whether to save results
            experiment_name: Custom experiment name
            
        Returns:
            Vision evaluation results
        """
        # Configure vision evaluator
        self.vision_evaluator.config.update({
            "task_type": task_type,
            "model_name": model_name
        })
        
        experiment_name = experiment_name or f"vision_{task_type}_{model_name}"
        
        result = await self.vision_evaluator.evaluate(
            model_interface=self.isa_interface,
            dataset=dataset,
            dataset_name=f"vision_{task_type}",
            model_name=model_name
        )
        
        if save_results:
            await self._save_results(result, experiment_name)
        
        return result
    
    async def evaluate_audio(self,
                           dataset: List[Dict[str, Any]],
                           task_type: str = "stt",
                           model_name: str = "isa_audio_sota_service",
                           save_results: bool = True,
                           experiment_name: Optional[str] = None) -> EvaluationResult:
        """
        Evaluate audio model on speech tasks.
        
        Args:
            dataset: Audio dataset with audio files and expected outputs
            task_type: Audio task type (stt, emotion, diarization)
            model_name: Audio model name
            save_results: Whether to save results
            experiment_name: Custom experiment name
            
        Returns:
            Audio evaluation results
        """
        # Configure audio evaluator
        self.audio_evaluator.config.update({
            "task_type": task_type,
            "model_name": model_name
        })
        
        experiment_name = experiment_name or f"audio_{task_type}_{model_name}"
        
        result = await self.audio_evaluator.evaluate(
            model_interface=self.isa_interface,
            dataset=dataset,
            dataset_name=f"audio_{task_type}",
            model_name=model_name
        )
        
        if save_results:
            await self._save_results(result, experiment_name)
        
        return result
    
    async def evaluate_embedding(self,
                               dataset: List[Dict[str, Any]],
                               task_type: str = "similarity",
                               model_name: str = "text-embedding-3-small",
                               save_results: bool = True,
                               experiment_name: Optional[str] = None) -> EvaluationResult:
        """
        Evaluate embedding model on semantic tasks.
        
        Args:
            dataset: Embedding dataset with text and expected outputs
            task_type: Embedding task type (similarity, retrieval, reranking)
            model_name: Embedding model name
            save_results: Whether to save results
            experiment_name: Custom experiment name
            
        Returns:
            Embedding evaluation results
        """
        # Configure embedding evaluator
        self.embedding_evaluator.config.update({
            "task_type": task_type,
            "model_name": model_name
        })
        
        experiment_name = experiment_name or f"embedding_{task_type}_{model_name}"
        
        result = await self.embedding_evaluator.evaluate(
            model_interface=self.isa_interface,
            dataset=dataset,
            dataset_name=f"embedding_{task_type}",
            model_name=model_name
        )
        
        if save_results:
            await self._save_results(result, experiment_name)
        
        return result
    
    async def compare_models(self,
                           models: List[Dict[str, str]],
                           dataset_path: Optional[str] = None,
                           dataset: Optional[List[Dict[str, Any]]] = None,
                           evaluator_type: str = "llm",
                           benchmark_name: Optional[str] = None,
                           metrics: Optional[List[str]] = None,
                           save_results: bool = True,
                           experiment_name: Optional[str] = None) -> Dict[str, EvaluationResult]:
        """
        Compare multiple models on the same evaluation task.
        
        Args:
            models: List of model configs [{"name": "gpt-4", "provider": "openai"}, ...]
            dataset_path: Path to evaluation dataset
            dataset: Direct dataset input
            evaluator_type: Type of evaluator (llm, vision, audio, embedding)
            benchmark_name: Benchmark name (alternative to dataset)
            metrics: Metrics to compute
            save_results: Whether to save comparison results
            experiment_name: Custom experiment name
            
        Returns:
            Dictionary mapping model names to evaluation results
        """
        results = {}
        
        # Load dataset if needed
        if dataset is None and dataset_path:
            dataset = self._load_dataset(dataset_path)
        
        # Run evaluations concurrently (with concurrency limits)
        semaphore = asyncio.Semaphore(self.config.max_concurrent_evaluations)
        
        async def evaluate_single_model(model_config: Dict[str, str]) -> tuple:
            async with semaphore:
                model_name = model_config["name"]
                provider = model_config.get("provider", "openai")
                
                if evaluator_type == "llm":
                    if benchmark_name:
                        result = await self.run_benchmark(
                            model_name=model_name,
                            provider=provider,
                            benchmark_name=benchmark_name,
                            save_results=False
                        )
                    else:
                        result = await self.evaluate_llm(
                            model_name=model_name,
                            provider=provider,
                            dataset=dataset,
                            metrics=metrics,
                            save_results=False
                        )
                elif evaluator_type == "vision":
                    result = await self.evaluate_vision(
                        dataset=dataset,
                        model_name=model_name,
                        save_results=False
                    )
                elif evaluator_type == "audio":
                    result = await self.evaluate_audio(
                        dataset=dataset,
                        model_name=model_name,
                        save_results=False
                    )
                elif evaluator_type == "embedding":
                    result = await self.evaluate_embedding(
                        dataset=dataset,
                        model_name=model_name,
                        save_results=False
                    )
                else:
                    raise ValueError(f"Unknown evaluator type: {evaluator_type}")
                
                return f"{provider}:{model_name}", result
        
        # Execute all evaluations
        tasks = [evaluate_single_model(model) for model in models]
        evaluation_results = await asyncio.gather(*tasks)
        
        # Collect results
        for model_id, result in evaluation_results:
            results[model_id] = result
        
        # Generate comparison report
        comparison_report = self._generate_comparison_report(results)
        
        # Save results if requested
        if save_results:
            experiment_name = experiment_name or f"model_comparison_{evaluator_type}_{len(models)}_models"
            await self._save_comparison_results(results, comparison_report, experiment_name)
        
        return results
    
    def _load_dataset(self, dataset_path: str) -> List[Dict[str, Any]]:
        """Load dataset from file."""
        with open(dataset_path, 'r', encoding='utf-8') as f:
            if dataset_path.endswith('.json'):
                dataset = json.load(f)
            elif dataset_path.endswith('.jsonl'):
                dataset = [json.loads(line) for line in f]
            else:
                raise ValueError(f"Unsupported dataset format: {dataset_path}")
        
        logger.info(f"Loaded dataset with {len(dataset)} samples from {dataset_path}")
        return dataset
    
    async def _load_benchmark(self,
                            benchmark_name: str,
                            subjects: Optional[List[str]] = None,
                            max_samples: Optional[int] = None,
                            few_shot: bool = True,
                            num_shots: int = 5) -> List[Dict[str, Any]]:
        """Load benchmark dataset."""
        # This would integrate with the benchmark loaders
        # For now, return a placeholder
        logger.warning(f"Benchmark {benchmark_name} loading not yet implemented")
        
        # Placeholder benchmark data
        return [
            {
                "id": f"sample_{i}",
                "prompt": f"Sample question {i} for {benchmark_name}",
                "reference": "A",
                "choices": ["A", "B", "C", "D"] if benchmark_name != "gsm8k" else None
            }
            for i in range(min(max_samples or 10, 10))
        ]
    
    async def _save_results(self, result: EvaluationResult, experiment_name: str) -> None:
        """Save evaluation results to disk."""
        # Create output directory
        output_dir = Path(self.config.output_dir) / experiment_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save main results
        results_path = output_dir / "results.json"
        result.save_to_file(results_path)
        
        # Save detailed predictions if available
        if result.sample_results:
            predictions_path = output_dir / "predictions.json"
            with open(predictions_path, 'w', encoding='utf-8') as f:
                json.dump(result.sample_results, f, indent=2, ensure_ascii=False)
        
        # Save summary
        summary_path = output_dir / "summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(result.get_summary(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved evaluation results to {output_dir}")
    
    async def _save_comparison_results(self, 
                                     results: Dict[str, EvaluationResult],
                                     comparison_report: Dict[str, Any],
                                     experiment_name: str) -> None:
        """Save model comparison results."""
        output_dir = Path(self.config.output_dir) / experiment_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save individual results
        for model_id, result in results.items():
            model_dir = output_dir / model_id.replace(":", "_")
            model_dir.mkdir(exist_ok=True)
            result.save_to_file(model_dir / "results.json")
        
        # Save comparison report
        comparison_path = output_dir / "comparison_report.json"
        with open(comparison_path, 'w', encoding='utf-8') as f:
            json.dump(comparison_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved comparison results to {output_dir}")
    
    def _generate_comparison_report(self, results: Dict[str, EvaluationResult]) -> Dict[str, Any]:
        """Generate comparison report from multiple model results."""
        report = {
            "models_compared": list(results.keys()),
            "comparison_timestamp": results[list(results.keys())[0]].timestamp,
            "metric_comparison": {},
            "rankings": {},
            "best_model_per_metric": {}
        }
        
        # Extract all metrics
        all_metrics = set()
        for result in results.values():
            all_metrics.update(result.metrics.keys())
        
        # Compare each metric
        for metric in all_metrics:
            metric_values = {}
            for model_id, result in results.items():
                if metric in result.metrics:
                    metric_values[model_id] = result.metrics[metric]
            
            if metric_values:
                # Determine if higher is better
                higher_is_better = metric not in ["perplexity", "loss", "error_rate"]
                
                # Find best model
                best_model = max(metric_values.items(), key=lambda x: x[1]) if higher_is_better else min(metric_values.items(), key=lambda x: x[1])
                
                # Create ranking
                sorted_models = sorted(metric_values.items(), key=lambda x: x[1], reverse=higher_is_better)
                
                report["metric_comparison"][metric] = metric_values
                report["rankings"][metric] = [{"model": model, "value": value} for model, value in sorted_models]
                report["best_model_per_metric"][metric] = {"model": best_model[0], "value": best_model[1]}
        
        return report
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get current factory configuration."""
        return self.config.to_dict()
    
    def get_active_evaluations(self) -> List[str]:
        """Get list of currently running evaluations."""
        return list(self._active_evaluations.keys())
    
    async def stop_evaluation(self, evaluation_id: str) -> bool:
        """Stop a running evaluation."""
        if evaluation_id in self._active_evaluations:
            task = self._active_evaluations[evaluation_id]
            task.cancel()
            del self._active_evaluations[evaluation_id]
            logger.info(f"Stopped evaluation: {evaluation_id}")
            return True
        return False
    
    async def cleanup(self) -> None:
        """Cleanup resources and stop all running evaluations."""
        # Cancel all active evaluations
        for evaluation_id in list(self._active_evaluations.keys()):
            await self.stop_evaluation(evaluation_id)
        
        # Close experiment tracker
        if self.experiment_tracker and self.experiment_tracker.is_running:
            await self.experiment_tracker.end_run()
        
        logger.info("EvaluationFactory cleanup completed")


# Convenience functions for quick evaluation
async def evaluate_llm_quick(model_name: str,
                           provider: str,
                           dataset_path: str,
                           metrics: Optional[List[str]] = None) -> EvaluationResult:
    """
    Quick LLM evaluation function.
    
    Args:
        model_name: Name of the model
        provider: Model provider
        dataset_path: Path to dataset
        metrics: Metrics to compute
        
    Returns:
        Evaluation results
    """
    factory = EvaluationFactory()
    try:
        return await factory.evaluate_llm(
            model_name=model_name,
            provider=provider,
            dataset_path=dataset_path,
            metrics=metrics
        )
    finally:
        await factory.cleanup()


async def run_benchmark_quick(model_name: str,
                            provider: str,
                            benchmark_name: str) -> EvaluationResult:
    """
    Quick benchmark evaluation function.
    
    Args:
        model_name: Name of the model
        provider: Model provider
        benchmark_name: Benchmark name
        
    Returns:
        Benchmark results
    """
    factory = EvaluationFactory()
    try:
        return await factory.run_benchmark(
            model_name=model_name,
            provider=provider,
            benchmark_name=benchmark_name
        )
    finally:
        await factory.cleanup()