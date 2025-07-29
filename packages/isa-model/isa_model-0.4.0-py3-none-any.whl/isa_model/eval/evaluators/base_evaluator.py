"""
Base evaluator class implementing industry best practices for AI model evaluation.

Features:
- Async/await support for concurrent evaluation
- Comprehensive error handling and retry logic
- Experiment tracking integration (W&B, MLflow)
- Distributed evaluation support
- Memory-efficient batch processing
- Comprehensive logging and metrics
"""

import asyncio
import logging
import time
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Callable, AsyncGenerator
from datetime import datetime
from pathlib import Path
import json

try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False

try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """
    Standardized evaluation result container.
    
    Follows MLOps best practices for result tracking and reproducibility.
    """
    
    # Core results
    metrics: Dict[str, float] = field(default_factory=dict)
    predictions: List[Any] = field(default_factory=list)
    references: List[Any] = field(default_factory=list)
    
    # Metadata
    model_name: str = ""
    dataset_name: str = ""
    evaluation_type: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Performance metrics
    total_samples: int = 0
    successful_samples: int = 0
    failed_samples: int = 0
    evaluation_time_seconds: float = 0.0
    throughput_samples_per_second: float = 0.0
    
    # Cost and resource tracking
    total_tokens_used: int = 0
    estimated_cost_usd: float = 0.0
    memory_peak_mb: float = 0.0
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    environment_info: Dict[str, Any] = field(default_factory=dict)
    
    # Error tracking
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Detailed results
    sample_results: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "metrics": self.metrics,
            "predictions": self.predictions,
            "references": self.references,
            "model_name": self.model_name,
            "dataset_name": self.dataset_name,
            "evaluation_type": self.evaluation_type,
            "timestamp": self.timestamp,
            "total_samples": self.total_samples,
            "successful_samples": self.successful_samples,
            "failed_samples": self.failed_samples,
            "evaluation_time_seconds": self.evaluation_time_seconds,
            "throughput_samples_per_second": self.throughput_samples_per_second,
            "total_tokens_used": self.total_tokens_used,
            "estimated_cost_usd": self.estimated_cost_usd,
            "memory_peak_mb": self.memory_peak_mb,
            "config": self.config,
            "environment_info": self.environment_info,
            "errors": self.errors,
            "warnings": self.warnings,
            "sample_results": self.sample_results
        }
    
    def save_to_file(self, file_path: Union[str, Path]) -> None:
        """Save results to JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, file_path: Union[str, Path]) -> 'EvaluationResult':
        """Load results from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        result = cls()
        for key, value in data.items():
            if hasattr(result, key):
                setattr(result, key, value)
        
        return result
    
    def get_summary(self) -> Dict[str, Any]:
        """Get evaluation summary."""
        success_rate = self.successful_samples / self.total_samples if self.total_samples > 0 else 0.0
        
        return {
            "model_name": self.model_name,
            "dataset_name": self.dataset_name,
            "evaluation_type": self.evaluation_type,
            "timestamp": self.timestamp,
            "success_rate": success_rate,
            "total_samples": self.total_samples,
            "evaluation_time_seconds": self.evaluation_time_seconds,
            "throughput_samples_per_second": self.throughput_samples_per_second,
            "estimated_cost_usd": self.estimated_cost_usd,
            "key_metrics": self.metrics,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }


class BaseEvaluator(ABC):
    """
    Abstract base evaluator implementing industry best practices.
    
    Features:
    - Async evaluation with concurrency control
    - Comprehensive error handling and retry logic
    - Experiment tracking integration
    - Memory-efficient batch processing
    - Progress monitoring and cancellation support
    """
    
    def __init__(self, 
                 evaluator_name: str,
                 config: Optional[Dict[str, Any]] = None,
                 experiment_tracker: Optional[Any] = None):
        """
        Initialize the base evaluator.
        
        Args:
            evaluator_name: Name identifier for this evaluator
            config: Evaluation configuration
            experiment_tracker: Optional experiment tracking instance
        """
        self.evaluator_name = evaluator_name
        self.config = config or {}
        self.experiment_tracker = experiment_tracker
        
        # State management
        self._is_running = False
        self._should_stop = False
        self._current_result: Optional[EvaluationResult] = None
        
        # Performance monitoring
        self._start_time: Optional[float] = None
        self._peak_memory_mb: float = 0.0
        
        # Concurrency control
        self.max_concurrent_requests = self.config.get("max_concurrent_requests", 10)
        self.semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        
        # Retry configuration
        self.max_retries = self.config.get("max_retries", 3)
        self.retry_delay = self.config.get("retry_delay_seconds", 1.0)
        
        logger.info(f"Initialized {evaluator_name} evaluator with config: {self.config}")
    
    @abstractmethod
    async def evaluate_sample(self, 
                            sample: Dict[str, Any],
                            model_interface: Any) -> Dict[str, Any]:
        """
        Evaluate a single sample.
        
        Args:
            sample: Data sample to evaluate
            model_interface: Model interface for inference
            
        Returns:
            Evaluation result for the sample
        """
        pass
    
    @abstractmethod
    def compute_metrics(self, 
                       predictions: List[Any],
                       references: List[Any],
                       **kwargs) -> Dict[str, float]:
        """
        Compute evaluation metrics.
        
        Args:
            predictions: Model predictions
            references: Ground truth references
            **kwargs: Additional parameters
            
        Returns:
            Dictionary of computed metrics
        """
        pass
    
    async def evaluate(self,
                      model_interface: Any,
                      dataset: List[Dict[str, Any]],
                      dataset_name: str = "unknown",
                      model_name: str = "unknown",
                      batch_size: Optional[int] = None,
                      save_predictions: bool = True,
                      progress_callback: Optional[Callable] = None) -> EvaluationResult:
        """
        Perform comprehensive evaluation with industry best practices.
        
        Args:
            model_interface: Model interface for inference
            dataset: Dataset to evaluate on
            dataset_name: Name of the dataset
            model_name: Name of the model
            batch_size: Batch size for processing
            save_predictions: Whether to save individual predictions
            progress_callback: Optional callback for progress updates
            
        Returns:
            Comprehensive evaluation results
        """
        
        # Initialize evaluation
        self._start_evaluation()
        result = EvaluationResult(
            model_name=model_name,
            dataset_name=dataset_name,
            evaluation_type=self.evaluator_name,
            config=self.config.copy(),
            environment_info=self._get_environment_info()
        )
        
        try:
            # Start experiment tracking
            await self._start_experiment_tracking(model_name, dataset_name)
            
            # Process dataset in batches
            batch_size = batch_size or self.config.get("batch_size", 32)
            total_batches = (len(dataset) + batch_size - 1) // batch_size
            
            all_predictions = []
            all_references = []
            all_sample_results = []
            
            for batch_idx in range(total_batches):
                if self._should_stop:
                    logger.info("Evaluation stopped by user request")
                    break
                
                # Get batch
                start_idx = batch_idx * batch_size
                end_idx = min(start_idx + batch_size, len(dataset))
                batch = dataset[start_idx:end_idx]
                
                # Process batch
                batch_results = await self._process_batch(batch, model_interface)
                
                # Collect results
                for sample_result in batch_results:
                    if sample_result.get("success", False):
                        all_predictions.append(sample_result.get("prediction"))
                        all_references.append(sample_result.get("reference"))
                        result.successful_samples += 1
                    else:
                        result.failed_samples += 1
                        result.errors.append({
                            "sample_id": sample_result.get("sample_id"),
                            "error": sample_result.get("error"),
                            "timestamp": datetime.now().isoformat()
                        })
                    
                    if save_predictions:
                        all_sample_results.append(sample_result)
                
                # Update progress
                progress = (batch_idx + 1) / total_batches
                if progress_callback:
                    await progress_callback(progress, batch_idx + 1, total_batches)
                
                # Log progress
                if (batch_idx + 1) % 10 == 0 or batch_idx == total_batches - 1:
                    logger.info(f"Processed {batch_idx + 1}/{total_batches} batches "
                              f"({result.successful_samples} successful, {result.failed_samples} failed)")
            
            # Compute final metrics
            if all_predictions and all_references:
                result.metrics = self.compute_metrics(all_predictions, all_references)
                logger.info(f"Computed metrics: {result.metrics}")
            else:
                logger.warning("No valid predictions available for metric computation")
                result.warnings.append("No valid predictions available for metric computation")
            
            # Finalize results
            result.predictions = all_predictions
            result.references = all_references
            result.sample_results = all_sample_results
            result.total_samples = len(dataset)
            
            # Log experiment results
            await self._log_experiment_results(result)
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            logger.error(traceback.format_exc())
            result.errors.append({
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc(),
                "timestamp": datetime.now().isoformat()
            })
        
        finally:
            # Finalize evaluation
            self._end_evaluation(result)
            await self._end_experiment_tracking()
            self._current_result = result
        
        return result
    
    async def _process_batch(self, 
                           batch: List[Dict[str, Any]], 
                           model_interface: Any) -> List[Dict[str, Any]]:
        """Process a batch of samples with concurrency control."""
        tasks = []
        
        for sample in batch:
            task = asyncio.create_task(
                self._process_sample_with_retry(sample, model_interface)
            )
            tasks.append(task)
        
        # Wait for all tasks in batch to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "sample_id": batch[i].get("id", f"sample_{i}"),
                    "success": False,
                    "error": str(result),
                    "prediction": None,
                    "reference": batch[i].get("reference")
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _process_sample_with_retry(self, 
                                       sample: Dict[str, Any], 
                                       model_interface: Any) -> Dict[str, Any]:
        """Process a single sample with retry logic and concurrency control."""
        async with self.semaphore:  # Limit concurrent requests
            for attempt in range(self.max_retries + 1):
                try:
                    result = await self.evaluate_sample(sample, model_interface)
                    result["success"] = True
                    result["sample_id"] = sample.get("id", "unknown")
                    result["reference"] = sample.get("reference")
                    return result
                
                except Exception as e:
                    if attempt == self.max_retries:
                        # Final attempt failed
                        logger.error(f"Sample evaluation failed after {self.max_retries + 1} attempts: {e}")
                        return {
                            "sample_id": sample.get("id", "unknown"),
                            "success": False,
                            "error": str(e),
                            "prediction": None,
                            "reference": sample.get("reference")
                        }
                    else:
                        # Retry with exponential backoff
                        delay = self.retry_delay * (2 ** attempt)
                        logger.warning(f"Sample evaluation failed (attempt {attempt + 1}), retrying in {delay}s: {e}")
                        await asyncio.sleep(delay)
    
    def _start_evaluation(self) -> None:
        """Mark the start of evaluation."""
        self._is_running = True
        self._should_stop = False
        self._start_time = time.time()
        
        # Monitor memory usage
        try:
            import psutil
            process = psutil.Process()
            self._peak_memory_mb = process.memory_info().rss / 1024 / 1024
        except ImportError:
            pass
    
    def _end_evaluation(self, result: EvaluationResult) -> None:
        """Finalize evaluation with performance metrics."""
        self._is_running = False
        end_time = time.time()
        
        if self._start_time:
            result.evaluation_time_seconds = end_time - self._start_time
            if result.total_samples > 0:
                result.throughput_samples_per_second = result.total_samples / result.evaluation_time_seconds
        
        result.memory_peak_mb = self._peak_memory_mb
        
        logger.info(f"Evaluation completed in {result.evaluation_time_seconds:.2f}s "
                   f"({result.throughput_samples_per_second:.2f} samples/sec)")
    
    def _get_environment_info(self) -> Dict[str, Any]:
        """Get environment information for reproducibility."""
        import platform
        import sys
        
        env_info = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "hostname": platform.node(),
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            import torch
            env_info["torch_version"] = torch.__version__
            env_info["cuda_available"] = torch.cuda.is_available()
            if torch.cuda.is_available():
                env_info["cuda_device_count"] = torch.cuda.device_count()
                env_info["cuda_device_name"] = torch.cuda.get_device_name()
        except ImportError:
            pass
        
        return env_info
    
    async def _start_experiment_tracking(self, model_name: str, dataset_name: str) -> None:
        """Start experiment tracking if available."""
        if self.experiment_tracker:
            try:
                await self.experiment_tracker.start_run(
                    name=f"{self.evaluator_name}_{model_name}_{dataset_name}",
                    config=self.config
                )
            except Exception as e:
                logger.warning(f"Failed to start experiment tracking: {e}")
    
    async def _log_experiment_results(self, result: EvaluationResult) -> None:
        """Log results to experiment tracker."""
        if self.experiment_tracker:
            try:
                await self.experiment_tracker.log_metrics(result.metrics)
                await self.experiment_tracker.log_params(result.config)
            except Exception as e:
                logger.warning(f"Failed to log experiment results: {e}")
    
    async def _end_experiment_tracking(self) -> None:
        """End experiment tracking."""
        if self.experiment_tracker:
            try:
                await self.experiment_tracker.end_run()
            except Exception as e:
                logger.warning(f"Failed to end experiment tracking: {e}")
    
    def stop_evaluation(self) -> None:
        """Request evaluation to stop gracefully."""
        self._should_stop = True
        logger.info("Evaluation stop requested")
    
    def is_running(self) -> bool:
        """Check if evaluation is currently running."""
        return self._is_running
    
    def get_current_result(self) -> Optional[EvaluationResult]:
        """Get the current/latest evaluation result."""
        return self._current_result
    
    def get_supported_metrics(self) -> List[str]:
        """Get list of metrics supported by this evaluator."""
        return []  # To be overridden by subclasses