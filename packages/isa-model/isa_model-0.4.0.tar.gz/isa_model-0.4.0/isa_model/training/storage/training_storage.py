"""
Training Data Storage System

Provides persistent storage for training jobs, metrics, and model lifecycle data.
Integrates with the core database system while maintaining training module independence.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
import uuid

try:
    from ...core.database.supabase_client import SupabaseClient
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class TrainingJobRecord:
    """Training job record for persistent storage."""
    
    # Basic information
    job_id: str
    job_name: str
    status: str  # "pending", "running", "completed", "failed", "cancelled"
    
    # Model and task information
    base_model: str
    task_type: str
    domain: str
    dataset_source: str
    
    # Training configuration
    training_config: Dict[str, Any]
    resource_config: Dict[str, Any]
    
    # Results and metrics
    output_model_path: Optional[str] = None
    training_metrics: Optional[Dict[str, Any]] = None
    cost_breakdown: Optional[Dict[str, float]] = None
    
    # Timing information
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # User and project information
    user_id: Optional[str] = None
    project_name: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Error information
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrainingJobRecord':
        """Create from dictionary."""
        # Convert ISO strings back to datetime objects
        datetime_fields = ['created_at', 'started_at', 'completed_at']
        for field_name in datetime_fields:
            if field_name in data and data[field_name]:
                if isinstance(data[field_name], str):
                    data[field_name] = datetime.fromisoformat(data[field_name])
        
        return cls(**data)


@dataclass
class TrainingMetrics:
    """Training metrics and performance data."""
    
    job_id: str
    
    # Training progress
    epoch: int
    step: int
    total_steps: int
    
    # Loss metrics
    training_loss: Optional[float] = None
    validation_loss: Optional[float] = None
    perplexity: Optional[float] = None
    
    # Performance metrics
    accuracy: Optional[float] = None
    f1_score: Optional[float] = None
    bleu_score: Optional[float] = None
    rouge_score: Optional[Dict[str, float]] = None
    
    # Resource utilization
    gpu_utilization: Optional[float] = None
    memory_usage: Optional[float] = None
    
    # Time tracking
    epoch_time: Optional[float] = None
    samples_per_second: Optional[float] = None
    
    # Custom metrics
    custom_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamp
    recorded_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        if isinstance(data['recorded_at'], datetime):
            data['recorded_at'] = data['recorded_at'].isoformat()
        return data


class TrainingStorage:
    """
    Training data storage system.
    
    Provides persistent storage for training jobs, metrics, and related data.
    Uses Supabase when available, falls back to local JSON storage.
    
    Example:
        ```python
        storage = TrainingStorage()
        
        # Store training job
        job_record = TrainingJobRecord(
            job_id="training_123",
            job_name="medical_chatbot_training",
            status="running",
            base_model="google/gemma-2-4b-it",
            task_type="chat",
            domain="medical",
            dataset_source="medical_qa.json",
            training_config={"epochs": 3, "lr": 2e-5},
            resource_config={"gpu": "RTX 4090", "provider": "runpod"}
        )
        
        storage.save_training_job(job_record)
        
        # Store metrics
        metrics = TrainingMetrics(
            job_id="training_123",
            epoch=1,
            step=100,
            total_steps=1000,
            training_loss=0.5,
            validation_loss=0.6
        )
        
        storage.save_training_metrics(metrics)
        ```
    """
    
    def __init__(self, storage_dir: Optional[str] = None, use_database: bool = True):
        """
        Initialize training storage.
        
        Args:
            storage_dir: Local storage directory (fallback)
            use_database: Whether to use database storage
        """
        self.use_database = use_database and SUPABASE_AVAILABLE
        self.storage_dir = Path(storage_dir or "./training_data")
        self.storage_dir.mkdir(exist_ok=True)
        
        if self.use_database:
            try:
                self.db_client = SupabaseClient()
                logger.info("Training storage initialized with database backend")
            except Exception as e:
                logger.warning(f"Failed to initialize database client: {e}")
                self.use_database = False
        
        if not self.use_database:
            logger.info("Training storage initialized with local file backend")
    
    def save_training_job(self, job_record: TrainingJobRecord) -> bool:
        """
        Save training job record.
        
        Args:
            job_record: Training job record to save
            
        Returns:
            True if successful
        """
        try:
            if self.use_database:
                return self._save_job_to_database(job_record)
            else:
                return self._save_job_to_file(job_record)
        except Exception as e:
            logger.error(f"Failed to save training job {job_record.job_id}: {e}")
            return False
    
    def get_training_job(self, job_id: str) -> Optional[TrainingJobRecord]:
        """
        Get training job record by ID.
        
        Args:
            job_id: Job ID to retrieve
            
        Returns:
            Training job record or None if not found
        """
        try:
            if self.use_database:
                return self._get_job_from_database(job_id)
            else:
                return self._get_job_from_file(job_id)
        except Exception as e:
            logger.error(f"Failed to get training job {job_id}: {e}")
            return None
    
    def update_training_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update training job record.
        
        Args:
            job_id: Job ID to update
            updates: Fields to update
            
        Returns:
            True if successful
        """
        try:
            if self.use_database:
                return self._update_job_in_database(job_id, updates)
            else:
                return self._update_job_in_file(job_id, updates)
        except Exception as e:
            logger.error(f"Failed to update training job {job_id}: {e}")
            return False
    
    def list_training_jobs(
        self, 
        status: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[TrainingJobRecord]:
        """
        List training jobs with optional filtering.
        
        Args:
            status: Filter by job status
            user_id: Filter by user ID
            limit: Maximum number of jobs to return
            
        Returns:
            List of training job records
        """
        try:
            if self.use_database:
                return self._list_jobs_from_database(status, user_id, limit)
            else:
                return self._list_jobs_from_files(status, user_id, limit)
        except Exception as e:
            logger.error(f"Failed to list training jobs: {e}")
            return []
    
    def save_training_metrics(self, metrics: TrainingMetrics) -> bool:
        """
        Save training metrics.
        
        Args:
            metrics: Training metrics to save
            
        Returns:
            True if successful
        """
        try:
            if self.use_database:
                return self._save_metrics_to_database(metrics)
            else:
                return self._save_metrics_to_file(metrics)
        except Exception as e:
            logger.error(f"Failed to save training metrics for job {metrics.job_id}: {e}")
            return False
    
    def get_training_metrics(self, job_id: str) -> List[TrainingMetrics]:
        """
        Get training metrics for a job.
        
        Args:
            job_id: Job ID to get metrics for
            
        Returns:
            List of training metrics
        """
        try:
            if self.use_database:
                return self._get_metrics_from_database(job_id)
            else:
                return self._get_metrics_from_files(job_id)
        except Exception as e:
            logger.error(f"Failed to get training metrics for job {job_id}: {e}")
            return []
    
    def delete_training_job(self, job_id: str) -> bool:
        """
        Delete training job and associated data.
        
        Args:
            job_id: Job ID to delete
            
        Returns:
            True if successful
        """
        try:
            if self.use_database:
                return self._delete_job_from_database(job_id)
            else:
                return self._delete_job_from_files(job_id)
        except Exception as e:
            logger.error(f"Failed to delete training job {job_id}: {e}")
            return False
    
    # Database backend methods
    def _save_job_to_database(self, job_record: TrainingJobRecord) -> bool:
        """Save job record to database."""
        if not self.use_database:
            return False
        
        try:
            client = self.db_client.get_client()
            data = job_record.to_dict()
            
            result = client.table("training_jobs").insert(data).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Database save failed: {e}")
            return False
    
    def _get_job_from_database(self, job_id: str) -> Optional[TrainingJobRecord]:
        """Get job record from database."""
        if not self.use_database:
            return None
        
        try:
            client = self.db_client.get_client()
            result = client.table("training_jobs").select("*").eq("job_id", job_id).execute()
            
            if result.data:
                return TrainingJobRecord.from_dict(result.data[0])
            return None
        except Exception as e:
            logger.error(f"Database get failed: {e}")
            return None
    
    def _update_job_in_database(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """Update job record in database."""
        if not self.use_database:
            return False
        
        try:
            client = self.db_client.get_client()
            result = client.table("training_jobs").update(updates).eq("job_id", job_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Database update failed: {e}")
            return False
    
    def _list_jobs_from_database(
        self, 
        status: Optional[str], 
        user_id: Optional[str], 
        limit: int
    ) -> List[TrainingJobRecord]:
        """List job records from database."""
        if not self.use_database:
            return []
        
        try:
            client = self.db_client.get_client()
            query = client.table("training_jobs").select("*")
            
            if status:
                query = query.eq("status", status)
            if user_id:
                query = query.eq("user_id", user_id)
            
            query = query.order("created_at", desc=True).limit(limit)
            result = query.execute()
            
            return [TrainingJobRecord.from_dict(record) for record in result.data]
        except Exception as e:
            logger.error(f"Database list failed: {e}")
            return []
    
    def _save_metrics_to_database(self, metrics: TrainingMetrics) -> bool:
        """Save metrics to database."""
        if not self.use_database:
            return False
        
        try:
            client = self.db_client.get_client()
            data = metrics.to_dict()
            
            result = client.table("training_metrics").insert(data).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Database metrics save failed: {e}")
            return False
    
    def _get_metrics_from_database(self, job_id: str) -> List[TrainingMetrics]:
        """Get metrics from database."""
        if not self.use_database:
            return []
        
        try:
            client = self.db_client.get_client()
            result = client.table("training_metrics").select("*").eq("job_id", job_id).order("recorded_at").execute()
            
            metrics_list = []
            for record in result.data:
                if isinstance(record['recorded_at'], str):
                    record['recorded_at'] = datetime.fromisoformat(record['recorded_at'])
                metrics_list.append(TrainingMetrics(**record))
            
            return metrics_list
        except Exception as e:
            logger.error(f"Database metrics get failed: {e}")
            return []
    
    def _delete_job_from_database(self, job_id: str) -> bool:
        """Delete job from database."""
        if not self.use_database:
            return False
        
        try:
            client = self.db_client.get_client()
            
            # Delete metrics first
            client.table("training_metrics").delete().eq("job_id", job_id).execute()
            
            # Delete job record
            result = client.table("training_jobs").delete().eq("job_id", job_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Database delete failed: {e}")
            return False
    
    # File backend methods (fallback)
    def _save_job_to_file(self, job_record: TrainingJobRecord) -> bool:
        """Save job record to local file."""
        try:
            job_file = self.storage_dir / "jobs" / f"{job_record.job_id}.json"
            job_file.parent.mkdir(exist_ok=True)
            
            with open(job_file, 'w') as f:
                json.dump(job_record.to_dict(), f, indent=2, default=str)
            
            return True
        except Exception as e:
            logger.error(f"File save failed: {e}")
            return False
    
    def _get_job_from_file(self, job_id: str) -> Optional[TrainingJobRecord]:
        """Get job record from local file."""
        try:
            job_file = self.storage_dir / "jobs" / f"{job_id}.json"
            if not job_file.exists():
                return None
            
            with open(job_file, 'r') as f:
                data = json.load(f)
            
            return TrainingJobRecord.from_dict(data)
        except Exception as e:
            logger.error(f"File get failed: {e}")
            return None
    
    def _update_job_in_file(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """Update job record in local file."""
        try:
            job_record = self._get_job_from_file(job_id)
            if not job_record:
                return False
            
            # Update fields
            for key, value in updates.items():
                if hasattr(job_record, key):
                    setattr(job_record, key, value)
            
            return self._save_job_to_file(job_record)
        except Exception as e:
            logger.error(f"File update failed: {e}")
            return False
    
    def _list_jobs_from_files(
        self, 
        status: Optional[str], 
        user_id: Optional[str], 
        limit: int
    ) -> List[TrainingJobRecord]:
        """List job records from local files."""
        try:
            jobs_dir = self.storage_dir / "jobs"
            if not jobs_dir.exists():
                return []
            
            jobs = []
            for job_file in jobs_dir.glob("*.json"):
                try:
                    with open(job_file, 'r') as f:
                        data = json.load(f)
                    
                    job_record = TrainingJobRecord.from_dict(data)
                    
                    # Apply filters
                    if status and job_record.status != status:
                        continue
                    if user_id and job_record.user_id != user_id:
                        continue
                    
                    jobs.append(job_record)
                except Exception as e:
                    logger.warning(f"Failed to load job file {job_file}: {e}")
                    continue
            
            # Sort by creation time (newest first)
            jobs.sort(key=lambda x: x.created_at, reverse=True)
            
            return jobs[:limit]
        except Exception as e:
            logger.error(f"File list failed: {e}")
            return []
    
    def _save_metrics_to_file(self, metrics: TrainingMetrics) -> bool:
        """Save metrics to local file."""
        try:
            metrics_dir = self.storage_dir / "metrics" / metrics.job_id
            metrics_dir.mkdir(parents=True, exist_ok=True)
            
            # Use timestamp for unique filename
            timestamp = metrics.recorded_at.strftime("%Y%m%d_%H%M%S_%f")
            metrics_file = metrics_dir / f"metrics_{timestamp}.json"
            
            with open(metrics_file, 'w') as f:
                json.dump(metrics.to_dict(), f, indent=2, default=str)
            
            return True
        except Exception as e:
            logger.error(f"File metrics save failed: {e}")
            return False
    
    def _get_metrics_from_files(self, job_id: str) -> List[TrainingMetrics]:
        """Get metrics from local files."""
        try:
            metrics_dir = self.storage_dir / "metrics" / job_id
            if not metrics_dir.exists():
                return []
            
            metrics_list = []
            for metrics_file in metrics_dir.glob("metrics_*.json"):
                try:
                    with open(metrics_file, 'r') as f:
                        data = json.load(f)
                    
                    if isinstance(data['recorded_at'], str):
                        data['recorded_at'] = datetime.fromisoformat(data['recorded_at'])
                    
                    metrics_list.append(TrainingMetrics(**data))
                except Exception as e:
                    logger.warning(f"Failed to load metrics file {metrics_file}: {e}")
                    continue
            
            # Sort by recording time
            metrics_list.sort(key=lambda x: x.recorded_at)
            
            return metrics_list
        except Exception as e:
            logger.error(f"File metrics get failed: {e}")
            return []
    
    def _delete_job_from_files(self, job_id: str) -> bool:
        """Delete job from local files."""
        try:
            # Delete job file
            job_file = self.storage_dir / "jobs" / f"{job_id}.json"
            if job_file.exists():
                job_file.unlink()
            
            # Delete metrics directory
            metrics_dir = self.storage_dir / "metrics" / job_id
            if metrics_dir.exists():
                import shutil
                shutil.rmtree(metrics_dir)
            
            return True
        except Exception as e:
            logger.error(f"File delete failed: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            all_jobs = self.list_training_jobs(limit=1000)
            
            total_jobs = len(all_jobs)
            status_counts = {}
            for job in all_jobs:
                status_counts[job.status] = status_counts.get(job.status, 0) + 1
            
            return {
                "total_jobs": total_jobs,
                "status_breakdown": status_counts,
                "backend": "database" if self.use_database else "file",
                "storage_available": SUPABASE_AVAILABLE
            }
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {"error": str(e)}