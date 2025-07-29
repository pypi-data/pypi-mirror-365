"""
Experiment tracking infrastructure with W&B and MLflow integration.

Implements industry best practices for ML experiment tracking:
- Automatic metric logging and visualization
- Hyperparameter tracking and optimization
- Model artifact management
- Distributed experiment coordination
- Cost and resource tracking
"""

import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False

try:
    import mlflow
    import mlflow.tracking
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

logger = logging.getLogger(__name__)


class ExperimentTracker(ABC):
    """
    Abstract base class for experiment tracking systems.
    
    Provides unified interface for different tracking backends.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize experiment tracker.
        
        Args:
            config: Tracker configuration
        """
        self.config = config or {}
        self.active_run_id: Optional[str] = None
        self.is_running = False
    
    @abstractmethod
    async def start_run(self, name: str, config: Dict[str, Any]) -> str:
        """
        Start a new experiment run.
        
        Args:
            name: Run name
            config: Run configuration
            
        Returns:
            Run ID
        """
        pass
    
    @abstractmethod
    async def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None) -> None:
        """
        Log metrics to the experiment tracker.
        
        Args:
            metrics: Metrics to log
            step: Optional step number
        """
        pass
    
    @abstractmethod
    async def log_params(self, params: Dict[str, Any]) -> None:
        """
        Log parameters to the experiment tracker.
        
        Args:
            params: Parameters to log
        """
        pass
    
    @abstractmethod
    async def log_artifacts(self, artifacts: Dict[str, Any]) -> None:
        """
        Log artifacts to the experiment tracker.
        
        Args:
            artifacts: Artifacts to log
        """
        pass
    
    @abstractmethod
    async def end_run(self) -> None:
        """End the current experiment run."""
        pass
    
    def get_run_id(self) -> Optional[str]:
        """Get current run ID."""
        return self.active_run_id


class WandBTracker(ExperimentTracker):
    """
    Weights & Biases experiment tracker.
    
    Features:
    - Real-time metric visualization
    - Hyperparameter sweeps
    - Model artifact tracking
    - Team collaboration
    """
    
    def __init__(self, 
                 project: str,
                 entity: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize W&B tracker.
        
        Args:
            project: W&B project name
            entity: W&B entity (team) name
            config: Additional configuration
        """
        super().__init__(config)
        
        if not WANDB_AVAILABLE:
            raise ImportError("wandb is not installed. Install with: pip install wandb")
        
        self.project = project
        self.entity = entity
        self.run = None
        
        logger.info(f"Initialized W&B tracker for project: {project}")
    
    async def start_run(self, name: str, config: Dict[str, Any]) -> str:
        """Start a new W&B run."""
        try:
            # Initialize wandb run
            self.run = wandb.init(
                project=self.project,
                entity=self.entity,
                name=name,
                config=config,
                reinit=True
            )
            
            self.active_run_id = self.run.id
            self.is_running = True
            
            logger.info(f"Started W&B run: {name} (ID: {self.active_run_id})")
            return self.active_run_id
            
        except Exception as e:
            logger.error(f"Failed to start W&B run: {e}")
            raise
    
    async def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None) -> None:
        """Log metrics to W&B."""
        if not self.is_running or not self.run:
            logger.warning("No active W&B run for logging metrics")
            return
        
        try:
            # Filter out non-numeric values
            numeric_metrics = {k: v for k, v in metrics.items() 
                             if isinstance(v, (int, float)) and not str(v).lower() in ['nan', 'inf', '-inf']}
            
            if numeric_metrics:
                self.run.log(numeric_metrics, step=step)
                logger.debug(f"Logged {len(numeric_metrics)} metrics to W&B")
            
        except Exception as e:
            logger.error(f"Failed to log metrics to W&B: {e}")
    
    async def log_params(self, params: Dict[str, Any]) -> None:
        """Log parameters to W&B."""
        if not self.is_running or not self.run:
            logger.warning("No active W&B run for logging params")
            return
        
        try:
            # W&B config is set during init, but we can update it
            for key, value in params.items():
                self.run.config[key] = value
            
            logger.debug(f"Logged {len(params)} parameters to W&B")
            
        except Exception as e:
            logger.error(f"Failed to log parameters to W&B: {e}")
    
    async def log_artifacts(self, artifacts: Dict[str, Any]) -> None:
        """Log artifacts to W&B."""
        if not self.is_running or not self.run:
            logger.warning("No active W&B run for logging artifacts")
            return
        
        try:
            for name, artifact in artifacts.items():
                if isinstance(artifact, str):
                    # File path
                    self.run.save(artifact, base_path=".")
                elif isinstance(artifact, dict):
                    # Save as JSON
                    artifact_path = f"{name}.json"
                    with open(artifact_path, 'w') as f:
                        json.dump(artifact, f, indent=2)
                    self.run.save(artifact_path)
                
            logger.debug(f"Logged {len(artifacts)} artifacts to W&B")
            
        except Exception as e:
            logger.error(f"Failed to log artifacts to W&B: {e}")
    
    async def end_run(self) -> None:
        """End the current W&B run."""
        if self.run:
            try:
                self.run.finish()
                logger.info(f"Ended W&B run: {self.active_run_id}")
            except Exception as e:
                logger.error(f"Failed to end W&B run: {e}")
            finally:
                self.run = None
                self.active_run_id = None
                self.is_running = False


class MLflowTracker(ExperimentTracker):
    """
    MLflow experiment tracker.
    
    Features:
    - Model lifecycle management
    - Experiment comparison
    - Model registry integration
    - Production deployment tracking
    """
    
    def __init__(self, 
                 experiment_name: str,
                 tracking_uri: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize MLflow tracker.
        
        Args:
            experiment_name: MLflow experiment name
            tracking_uri: MLflow tracking server URI
            config: Additional configuration
        """
        super().__init__(config)
        
        if not MLFLOW_AVAILABLE:
            raise ImportError("mlflow is not installed. Install with: pip install mlflow")
        
        self.experiment_name = experiment_name
        
        # Set tracking URI if provided
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        
        # Get or create experiment
        try:
            self.experiment = mlflow.get_experiment_by_name(experiment_name)
            if self.experiment is None:
                experiment_id = mlflow.create_experiment(experiment_name)
                self.experiment = mlflow.get_experiment(experiment_id)
        except Exception as e:
            logger.error(f"Failed to initialize MLflow experiment: {e}")
            raise
        
        logger.info(f"Initialized MLflow tracker for experiment: {experiment_name}")
    
    async def start_run(self, name: str, config: Dict[str, Any]) -> str:
        """Start a new MLflow run."""
        try:
            mlflow.start_run(
                experiment_id=self.experiment.experiment_id,
                run_name=name
            )
            
            run = mlflow.active_run()
            self.active_run_id = run.info.run_id
            self.is_running = True
            
            # Log initial config
            await self.log_params(config)
            
            logger.info(f"Started MLflow run: {name} (ID: {self.active_run_id})")
            return self.active_run_id
            
        except Exception as e:
            logger.error(f"Failed to start MLflow run: {e}")
            raise
    
    async def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None) -> None:
        """Log metrics to MLflow."""
        if not self.is_running:
            logger.warning("No active MLflow run for logging metrics")
            return
        
        try:
            for key, value in metrics.items():
                if isinstance(value, (int, float)) and not str(value).lower() in ['nan', 'inf', '-inf']:
                    mlflow.log_metric(key, value, step=step)
            
            logger.debug(f"Logged {len(metrics)} metrics to MLflow")
            
        except Exception as e:
            logger.error(f"Failed to log metrics to MLflow: {e}")
    
    async def log_params(self, params: Dict[str, Any]) -> None:
        """Log parameters to MLflow."""
        if not self.is_running:
            logger.warning("No active MLflow run for logging params")
            return
        
        try:
            # Convert complex objects to strings
            str_params = {}
            for key, value in params.items():
                if isinstance(value, (dict, list)):
                    str_params[key] = json.dumps(value)
                else:
                    str_params[key] = str(value)
            
            mlflow.log_params(str_params)
            logger.debug(f"Logged {len(params)} parameters to MLflow")
            
        except Exception as e:
            logger.error(f"Failed to log parameters to MLflow: {e}")
    
    async def log_artifacts(self, artifacts: Dict[str, Any]) -> None:
        """Log artifacts to MLflow."""
        if not self.is_running:
            logger.warning("No active MLflow run for logging artifacts")
            return
        
        try:
            for name, artifact in artifacts.items():
                if isinstance(artifact, str):
                    # File path
                    mlflow.log_artifact(artifact)
                elif isinstance(artifact, dict):
                    # Save as JSON and log
                    artifact_path = f"{name}.json"
                    with open(artifact_path, 'w') as f:
                        json.dump(artifact, f, indent=2)
                    mlflow.log_artifact(artifact_path)
            
            logger.debug(f"Logged {len(artifacts)} artifacts to MLflow")
            
        except Exception as e:
            logger.error(f"Failed to log artifacts to MLflow: {e}")
    
    async def end_run(self) -> None:
        """End the current MLflow run."""
        if self.is_running:
            try:
                mlflow.end_run()
                logger.info(f"Ended MLflow run: {self.active_run_id}")
            except Exception as e:
                logger.error(f"Failed to end MLflow run: {e}")
            finally:
                self.active_run_id = None
                self.is_running = False


class MultiTracker(ExperimentTracker):
    """
    Multi-backend experiment tracker.
    
    Logs to multiple tracking systems simultaneously for redundancy.
    """
    
    def __init__(self, trackers: List[ExperimentTracker]):
        """
        Initialize multi-tracker.
        
        Args:
            trackers: List of tracker instances
        """
        super().__init__()
        self.trackers = trackers
        logger.info(f"Initialized multi-tracker with {len(trackers)} backends")
    
    async def start_run(self, name: str, config: Dict[str, Any]) -> str:
        """Start runs on all trackers."""
        run_ids = []
        
        for tracker in self.trackers:
            try:
                run_id = await tracker.start_run(name, config)
                run_ids.append(run_id)
            except Exception as e:
                logger.error(f"Failed to start run on {type(tracker).__name__}: {e}")
        
        self.is_running = len(run_ids) > 0
        self.active_run_id = run_ids[0] if run_ids else None
        
        return self.active_run_id or "multi_tracker_run"
    
    async def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None) -> None:
        """Log metrics to all trackers."""
        tasks = []
        for tracker in self.trackers:
            tasks.append(tracker.log_metrics(metrics, step))
        
        # Run all logging tasks concurrently
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def log_params(self, params: Dict[str, Any]) -> None:
        """Log parameters to all trackers."""
        tasks = []
        for tracker in self.trackers:
            tasks.append(tracker.log_params(params))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def log_artifacts(self, artifacts: Dict[str, Any]) -> None:
        """Log artifacts to all trackers."""
        tasks = []
        for tracker in self.trackers:
            tasks.append(tracker.log_artifacts(artifacts))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def end_run(self) -> None:
        """End runs on all trackers."""
        tasks = []
        for tracker in self.trackers:
            tasks.append(tracker.end_run())
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        self.is_running = False
        self.active_run_id = None


def create_experiment_tracker(tracker_type: str, **kwargs) -> ExperimentTracker:
    """
    Factory function to create experiment trackers.
    
    Args:
        tracker_type: Type of tracker ("wandb", "mlflow", "multi")
        **kwargs: Tracker-specific configuration
        
    Returns:
        Configured experiment tracker
    """
    if tracker_type.lower() == "wandb":
        return WandBTracker(**kwargs)
    elif tracker_type.lower() == "mlflow":
        return MLflowTracker(**kwargs)
    elif tracker_type.lower() == "multi":
        trackers = kwargs.get("trackers", [])
        return MultiTracker(trackers)
    else:
        raise ValueError(f"Unknown tracker type: {tracker_type}")