"""
Training Repository

High-level repository pattern for training data access.
Provides a clean, unified interface for training data operations
with automatic core integration.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

from .training_storage import TrainingStorage, TrainingJobRecord, TrainingMetrics
from .core_integration import CoreModelIntegration

logger = logging.getLogger(__name__)


class TrainingRepository:
    """
    High-level repository for training data management.
    
    Provides a unified interface for all training data operations
    with automatic core integration and intelligent features.
    
    Example:
        ```python
        repo = TrainingRepository()
        
        # Create and track training job
        job_id = repo.create_training_job(
            job_name="medical_chatbot_training",
            base_model="google/gemma-2-4b-it",
            task_type="chat",
            domain="medical",
            dataset_source="medical_qa.json",
            training_config={"epochs": 3},
            user_id="user_123"
        )
        
        # Update job status
        repo.update_job_status(job_id, "running")
        
        # Record training metrics
        repo.record_metrics(job_id, {
            "epoch": 1,
            "training_loss": 0.5,
            "validation_loss": 0.6
        })
        
        # Complete training and register model
        repo.complete_training(
            job_id,
            model_path="/path/to/model",
            final_metrics={"accuracy": 0.95}
        )
        ```
    """
    
    def __init__(self, 
                 storage: Optional[TrainingStorage] = None,
                 core_integration: Optional[CoreModelIntegration] = None):
        """
        Initialize training repository.
        
        Args:
            storage: Training storage backend
            core_integration: Core model integration
        """
        self.storage = storage or TrainingStorage()
        self.core_integration = core_integration or CoreModelIntegration(
            training_storage=self.storage
        )
        
        logger.info("Training repository initialized")
    
    def create_training_job(
        self,
        job_name: str,
        base_model: str,
        task_type: str,
        domain: str,
        dataset_source: str,
        training_config: Dict[str, Any],
        resource_config: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        project_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Create a new training job record.
        
        Args:
            job_name: Human-readable job name
            base_model: Base model identifier
            task_type: Type of training task
            domain: Application domain
            dataset_source: Dataset source path or identifier
            training_config: Training configuration parameters
            resource_config: Resource configuration (GPU, cloud provider, etc.)
            user_id: User identifier
            project_name: Project name
            tags: Additional tags
            
        Returns:
            Job ID of created training job
        """
        try:
            import uuid
            
            job_id = f"training_{uuid.uuid4().hex[:8]}"
            
            job_record = TrainingJobRecord(
                job_id=job_id,
                job_name=job_name,
                status="pending",
                base_model=base_model,
                task_type=task_type,
                domain=domain,
                dataset_source=dataset_source,
                training_config=training_config,
                resource_config=resource_config or {},
                user_id=user_id,
                project_name=project_name,
                tags=tags or {}
            )
            
            success = self.storage.save_training_job(job_record)
            
            if success:
                logger.info(f"Created training job: {job_id} ({job_name})")
                return job_id
            else:
                raise Exception("Failed to save training job")
                
        except Exception as e:
            logger.error(f"Failed to create training job: {e}")
            raise
    
    def update_job_status(
        self, 
        job_id: str, 
        status: str, 
        error_message: Optional[str] = None,
        additional_updates: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update training job status.
        
        Args:
            job_id: Job ID to update
            status: New status ("pending", "running", "completed", "failed", "cancelled")
            error_message: Error message if failed
            additional_updates: Additional fields to update
            
        Returns:
            True if successful
        """
        try:
            updates = {"status": status}
            
            if status == "running" and not additional_updates or "started_at" not in additional_updates:
                updates["started_at"] = datetime.now()
            elif status in ["completed", "failed", "cancelled"]:
                updates["completed_at"] = datetime.now()
                
            if error_message:
                updates["error_message"] = error_message
                
            if additional_updates:
                updates.update(additional_updates)
            
            success = self.storage.update_training_job(job_id, updates)
            
            if success:
                logger.info(f"Updated job {job_id} status to: {status}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update job status for {job_id}: {e}")
            return False
    
    def record_metrics(
        self,
        job_id: str,
        metrics_data: Dict[str, Any]
    ) -> bool:
        """
        Record training metrics for a job.
        
        Args:
            job_id: Job ID
            metrics_data: Metrics data dictionary
            
        Returns:
            True if successful
        """
        try:
            # Create TrainingMetrics object
            metrics = TrainingMetrics(
                job_id=job_id,
                epoch=metrics_data.get("epoch", 0),
                step=metrics_data.get("step", 0),
                total_steps=metrics_data.get("total_steps", 0),
                training_loss=metrics_data.get("training_loss"),
                validation_loss=metrics_data.get("validation_loss"),
                perplexity=metrics_data.get("perplexity"),
                accuracy=metrics_data.get("accuracy"),
                f1_score=metrics_data.get("f1_score"),
                bleu_score=metrics_data.get("bleu_score"),
                rouge_score=metrics_data.get("rouge_score"),
                gpu_utilization=metrics_data.get("gpu_utilization"),
                memory_usage=metrics_data.get("memory_usage"),
                epoch_time=metrics_data.get("epoch_time"),
                samples_per_second=metrics_data.get("samples_per_second"),
                custom_metrics=metrics_data.get("custom_metrics", {})
            )
            
            success = self.storage.save_training_metrics(metrics)
            
            if success:
                logger.debug(f"Recorded metrics for job {job_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to record metrics for job {job_id}: {e}")
            return False
    
    def complete_training(
        self,
        job_id: str,
        model_path: str,
        final_metrics: Optional[Dict[str, Any]] = None,
        cost_breakdown: Optional[Dict[str, float]] = None
    ) -> Optional[str]:
        """
        Complete training and register the trained model.
        
        Args:
            job_id: Job ID
            model_path: Path to the trained model
            final_metrics: Final performance metrics
            cost_breakdown: Training cost breakdown
            
        Returns:
            Core model ID if successful, None otherwise
        """
        try:
            # Update job status to completed
            updates = {
                "status": "completed",
                "completed_at": datetime.now(),
                "output_model_path": model_path
            }
            
            if final_metrics:
                updates["training_metrics"] = final_metrics
                
            if cost_breakdown:
                updates["cost_breakdown"] = cost_breakdown
            
            success = self.storage.update_training_job(job_id, updates)
            
            if not success:
                logger.error(f"Failed to update job {job_id} as completed")
                return None
            
            # Get updated job record
            job_record = self.storage.get_training_job(job_id)
            if not job_record:
                logger.error(f"Failed to retrieve completed job record {job_id}")
                return None
            
            # Register model in core system
            core_model_id = self.core_integration.register_trained_model(
                job_record=job_record,
                model_path=model_path,
                performance_metrics=final_metrics
            )
            
            if core_model_id:
                logger.info(f"Training completed and model registered: {core_model_id}")
            
            return core_model_id
            
        except Exception as e:
            logger.error(f"Failed to complete training for job {job_id}: {e}")
            return None
    
    def get_job(self, job_id: str) -> Optional[TrainingJobRecord]:
        """Get training job by ID."""
        return self.storage.get_training_job(job_id)
    
    def list_jobs(
        self,
        status: Optional[str] = None,
        user_id: Optional[str] = None,
        project_name: Optional[str] = None,
        limit: int = 100
    ) -> List[TrainingJobRecord]:
        """
        List training jobs with filtering.
        
        Args:
            status: Filter by status
            user_id: Filter by user ID
            project_name: Filter by project name
            limit: Maximum number of jobs
            
        Returns:
            List of training job records
        """
        jobs = self.storage.list_training_jobs(status=status, user_id=user_id, limit=limit)
        
        # Additional filtering for project_name
        if project_name:
            jobs = [job for job in jobs if job.project_name == project_name]
        
        return jobs
    
    def get_job_metrics(self, job_id: str) -> List[TrainingMetrics]:
        """Get all metrics for a training job."""
        return self.storage.get_training_metrics(job_id)
    
    def get_job_progress(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get training job progress summary.
        
        Args:
            job_id: Job ID
            
        Returns:
            Progress summary with latest metrics
        """
        try:
            job = self.get_job(job_id)
            if not job:
                return None
            
            metrics_list = self.get_job_metrics(job_id)
            latest_metrics = metrics_list[-1] if metrics_list else None
            
            progress = {
                "job_id": job_id,
                "job_name": job.job_name,
                "status": job.status,
                "created_at": job.created_at.isoformat(),
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None
            }
            
            if latest_metrics:
                progress.update({
                    "current_epoch": latest_metrics.epoch,
                    "current_step": latest_metrics.step,
                    "total_steps": latest_metrics.total_steps,
                    "progress_percentage": (latest_metrics.step / latest_metrics.total_steps * 100) if latest_metrics.total_steps > 0 else 0,
                    "latest_loss": latest_metrics.training_loss,
                    "latest_validation_loss": latest_metrics.validation_loss
                })
            
            # Calculate duration
            if job.started_at:
                end_time = job.completed_at or datetime.now()
                duration = end_time - job.started_at
                progress["duration_seconds"] = duration.total_seconds()
                progress["duration_formatted"] = str(duration).split(".")[0]  # Remove microseconds
            
            return progress
            
        except Exception as e:
            logger.error(f"Failed to get job progress for {job_id}: {e}")
            return None
    
    def delete_job(self, job_id: str) -> bool:
        """Delete training job and all associated data."""
        try:
            success = self.storage.delete_training_job(job_id)
            
            if success:
                logger.info(f"Deleted training job: {job_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete job {job_id}: {e}")
            return False
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get training statistics for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            User training statistics
        """
        try:
            user_jobs = self.list_jobs(user_id=user_id, limit=1000)
            
            total_jobs = len(user_jobs)
            status_counts = {}
            total_cost = 0.0
            total_duration = timedelta()
            
            for job in user_jobs:
                # Count by status
                status_counts[job.status] = status_counts.get(job.status, 0) + 1
                
                # Sum costs
                if job.cost_breakdown:
                    total_cost += sum(job.cost_breakdown.values())
                
                # Sum duration
                if job.started_at and job.completed_at:
                    total_duration += (job.completed_at - job.started_at)
            
            return {
                "user_id": user_id,
                "total_jobs": total_jobs,
                "status_breakdown": status_counts,
                "total_cost_usd": total_cost,
                "total_training_time": str(total_duration).split(".")[0],
                "average_cost_per_job": total_cost / total_jobs if total_jobs > 0 else 0,
                "success_rate": status_counts.get("completed", 0) / total_jobs if total_jobs > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get user statistics for {user_id}: {e}")
            return {"error": str(e)}
    
    def get_recent_activity(self, days: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent training activity.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of activities
            
        Returns:
            List of recent activities
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            all_jobs = self.list_jobs(limit=limit * 2)  # Get more to filter by date
            
            recent_jobs = [
                job for job in all_jobs 
                if job.created_at >= cutoff_date
            ][:limit]
            
            activities = []
            for job in recent_jobs:
                activity = {
                    "job_id": job.job_id,
                    "job_name": job.job_name,
                    "status": job.status,
                    "base_model": job.base_model,
                    "task_type": job.task_type,
                    "domain": job.domain,
                    "created_at": job.created_at.isoformat(),
                    "user_id": job.user_id
                }
                
                if job.completed_at:
                    activity["completed_at"] = job.completed_at.isoformat()
                
                if job.cost_breakdown:
                    activity["total_cost"] = sum(job.cost_breakdown.values())
                
                activities.append(activity)
            
            return activities
            
        except Exception as e:
            logger.error(f"Failed to get recent activity: {e}")
            return []
    
    def cleanup_old_jobs(self, days: int = 30, dry_run: bool = True) -> Dict[str, Any]:
        """
        Cleanup old training jobs.
        
        Args:
            days: Delete jobs older than this many days
            dry_run: If True, only return what would be deleted
            
        Returns:
            Cleanup summary
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            all_jobs = self.list_jobs(limit=1000)
            old_jobs = [
                job for job in all_jobs 
                if job.created_at < cutoff_date and job.status in ["completed", "failed", "cancelled"]
            ]
            
            summary = {
                "total_jobs_found": len(old_jobs),
                "cutoff_date": cutoff_date.isoformat(),
                "dry_run": dry_run,
                "deleted_jobs": []
            }
            
            if not dry_run:
                deleted_count = 0
                for job in old_jobs:
                    if self.delete_job(job.job_id):
                        deleted_count += 1
                        summary["deleted_jobs"].append({
                            "job_id": job.job_id,
                            "job_name": job.job_name,
                            "created_at": job.created_at.isoformat()
                        })
                
                summary["deleted_count"] = deleted_count
            else:
                summary["would_delete"] = [
                    {
                        "job_id": job.job_id,
                        "job_name": job.job_name,
                        "created_at": job.created_at.isoformat()
                    }
                    for job in old_jobs
                ]
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to cleanup old jobs: {e}")
            return {"error": str(e)}
    
    def get_repository_statistics(self) -> Dict[str, Any]:
        """Get overall repository statistics."""
        try:
            storage_stats = self.storage.get_statistics()
            integration_status = self.core_integration.get_integration_status()
            
            return {
                "storage": storage_stats,
                "core_integration": integration_status,
                "repository_version": "1.0.0"
            }
            
        except Exception as e:
            logger.error(f"Failed to get repository statistics: {e}")
            return {"error": str(e)}