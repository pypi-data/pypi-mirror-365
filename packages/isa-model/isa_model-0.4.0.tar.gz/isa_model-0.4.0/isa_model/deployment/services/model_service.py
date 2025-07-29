"""
ModelService - Core abstraction for deployed model services in the MaaS platform

This represents a deployed service instance that can be discovered, monitored, and invoked.
It's the bridge between the high-level AIFactory interface and the underlying platform services.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ServiceStatus(str, Enum):
    """Service deployment and health status"""
    PENDING = "pending"
    DEPLOYING = "deploying"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STOPPED = "stopped"

class ServiceType(str, Enum):
    """Types of services available in the platform"""
    LLM = "llm"
    EMBEDDING = "embedding"
    VISION = "vision"
    AUDIO = "audio"
    IMAGE_GEN = "image_gen"

class DeploymentPlatform(str, Enum):
    """Supported deployment platforms for self-owned services only"""
    MODAL = "modal"
    KUBERNETES = "kubernetes"
    RUNPOD = "runpod"
    YYDS = "yyds"
    OLLAMA = "ollama"  # Local deployment

@dataclass
class HealthMetrics:
    """Service health metrics"""
    is_healthy: bool
    response_time_ms: Optional[int] = None
    status_code: Optional[int] = None
    cpu_usage_percent: Optional[float] = None
    memory_usage_mb: Optional[int] = None
    gpu_usage_percent: Optional[float] = None
    error_message: Optional[str] = None
    checked_at: Optional[datetime] = None

@dataclass
class UsageMetrics:
    """Service usage and cost metrics"""
    request_count: int = 0
    total_processing_time_ms: int = 0
    error_count: int = 0
    total_cost_usd: float = 0.0
    window_start: Optional[datetime] = None
    window_end: Optional[datetime] = None

@dataclass
class ResourceRequirements:
    """Service resource requirements"""
    gpu_type: Optional[str] = None
    memory_mb: Optional[int] = None
    cpu_cores: Optional[int] = None
    storage_gb: Optional[int] = None
    min_replicas: int = 0
    max_replicas: int = 1

class ModelService:
    """
    Core abstraction for a deployed model service in the MaaS platform
    
    This class represents a self-owned deployed service instance that:
    - Has been deployed to a platform (Modal, Kubernetes, RunPod, etc.)
    - Can be discovered through the ServiceRegistry
    - Can be health-checked and monitored
    - Provides inference capabilities through specific endpoints
    
    Note: This is only for self-owned deployments. Third-party services 
    (OpenAI, Replicate, etc.) are managed by ThirdPartyServiceManager.
    """
    
    def __init__(
        self,
        service_id: str,
        service_name: str,
        model_id: Optional[str],
        deployment_platform: DeploymentPlatform,
        service_type: ServiceType,
        inference_endpoint: Optional[str] = None,
        health_endpoint: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None,
        resource_requirements: Optional[ResourceRequirements] = None,
        metadata: Optional[Dict[str, Any]] = None,
        status: ServiceStatus = ServiceStatus.PENDING
    ):
        self.service_id = service_id
        self.service_name = service_name
        self.model_id = model_id
        self.deployment_platform = deployment_platform
        self.service_type = service_type
        self.status = status
        
        # Endpoints
        self.inference_endpoint = inference_endpoint
        self.health_endpoint = health_endpoint
        
        # Capabilities and configuration
        self.capabilities = capabilities or []
        self.config = config or {}
        self.resource_requirements = resource_requirements or ResourceRequirements()
        self.metadata = metadata or {}
        
        # Metrics (populated by monitoring systems)
        self.health_metrics: Optional[HealthMetrics] = None
        self.usage_metrics: Optional[UsageMetrics] = None
        
        # Timestamps
        self.created_at: Optional[datetime] = None
        self.updated_at: Optional[datetime] = None
        
        logger.debug(f"Created ModelService: {service_id} ({service_name})")
    
    def is_healthy(self) -> bool:
        """Check if the service is currently healthy"""
        if self.status != ServiceStatus.HEALTHY:
            return False
        
        if self.health_metrics:
            return self.health_metrics.is_healthy
        
        # If no health metrics, assume healthy if status is healthy
        return True
    
    def is_available(self) -> bool:
        """Check if the service is available for inference requests"""
        return (
            self.status == ServiceStatus.HEALTHY and
            self.inference_endpoint is not None and
            self.is_healthy()
        )
    
    def has_capability(self, capability: str) -> bool:
        """Check if this service provides a specific capability"""
        return capability in self.capabilities
    
    def get_endpoint_url(self, endpoint_type: str = "inference") -> Optional[str]:
        """Get endpoint URL for the service"""
        if endpoint_type == "inference":
            return self.inference_endpoint
        elif endpoint_type == "health":
            return self.health_endpoint
        else:
            # Check if it's in metadata
            endpoints = self.metadata.get("endpoints", {})
            return endpoints.get(endpoint_type)
    
    def update_health_metrics(self, metrics: HealthMetrics) -> None:
        """Update health metrics for this service"""
        self.health_metrics = metrics
        
        # Update service status based on health
        if metrics.is_healthy:
            if self.status != ServiceStatus.HEALTHY:
                self.status = ServiceStatus.HEALTHY
                logger.info(f"Service {self.service_id} is now healthy")
        else:
            if self.status == ServiceStatus.HEALTHY:
                self.status = ServiceStatus.UNHEALTHY
                logger.warning(f"Service {self.service_id} is now unhealthy: {metrics.error_message}")
    
    def update_usage_metrics(self, metrics: UsageMetrics) -> None:
        """Update usage metrics for this service"""
        self.usage_metrics = metrics
        logger.debug(f"Updated usage metrics for {self.service_id}: {metrics.request_count} requests")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert service to dictionary representation"""
        return {
            "service_id": self.service_id,
            "service_name": self.service_name,
            "model_id": self.model_id,
            "deployment_platform": self.deployment_platform.value,
            "service_type": self.service_type.value,
            "status": self.status.value,
            "inference_endpoint": self.inference_endpoint,
            "health_endpoint": self.health_endpoint,
            "capabilities": self.capabilities,
            "config": self.config,
            "resource_requirements": {
                "gpu_type": self.resource_requirements.gpu_type,
                "memory_mb": self.resource_requirements.memory_mb,
                "cpu_cores": self.resource_requirements.cpu_cores,
                "storage_gb": self.resource_requirements.storage_gb,
                "min_replicas": self.resource_requirements.min_replicas,
                "max_replicas": self.resource_requirements.max_replicas,
            },
            "metadata": self.metadata,
            "health_metrics": {
                "is_healthy": self.health_metrics.is_healthy if self.health_metrics else None,
                "response_time_ms": self.health_metrics.response_time_ms if self.health_metrics else None,
                "status_code": self.health_metrics.status_code if self.health_metrics else None,
                "error_message": self.health_metrics.error_message if self.health_metrics else None,
                "checked_at": self.health_metrics.checked_at.isoformat() if self.health_metrics and self.health_metrics.checked_at else None,
            } if self.health_metrics else None,
            "usage_metrics": {
                "request_count": self.usage_metrics.request_count if self.usage_metrics else 0,
                "total_processing_time_ms": self.usage_metrics.total_processing_time_ms if self.usage_metrics else 0,
                "error_count": self.usage_metrics.error_count if self.usage_metrics else 0,
                "total_cost_usd": self.usage_metrics.total_cost_usd if self.usage_metrics else 0.0,
            } if self.usage_metrics else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelService':
        """Create ModelService from dictionary representation"""
        # Create resource requirements
        resource_data = data.get("resource_requirements", {})
        resources = ResourceRequirements(
            gpu_type=resource_data.get("gpu_type"),
            memory_mb=resource_data.get("memory_mb"),
            cpu_cores=resource_data.get("cpu_cores"),
            storage_gb=resource_data.get("storage_gb"),
            min_replicas=resource_data.get("min_replicas", 0),
            max_replicas=resource_data.get("max_replicas", 1),
        )
        
        # Create service
        service = cls(
            service_id=data["service_id"],
            service_name=data["service_name"],
            model_id=data.get("model_id"),
            deployment_platform=DeploymentPlatform(data["deployment_platform"]),
            service_type=ServiceType(data["service_type"]),
            status=ServiceStatus(data.get("status", "pending")),
            inference_endpoint=data.get("inference_endpoint"),
            health_endpoint=data.get("health_endpoint"),
            capabilities=data.get("capabilities", []),
            config=data.get("config", {}),
            resource_requirements=resources,
            metadata=data.get("metadata", {}),
        )
        
        # Set timestamps
        if data.get("created_at"):
            service.created_at = datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
        if data.get("updated_at"):
            service.updated_at = datetime.fromisoformat(data["updated_at"].replace('Z', '+00:00'))
        
        # Set health metrics
        health_data = data.get("health_metrics")
        if health_data and health_data.get("is_healthy") is not None:
            checked_at = None
            if health_data.get("checked_at"):
                checked_at = datetime.fromisoformat(health_data["checked_at"].replace('Z', '+00:00'))
            
            service.health_metrics = HealthMetrics(
                is_healthy=health_data["is_healthy"],
                response_time_ms=health_data.get("response_time_ms"),
                status_code=health_data.get("status_code"),
                error_message=health_data.get("error_message"),
                checked_at=checked_at,
            )
        
        # Set usage metrics
        usage_data = data.get("usage_metrics")
        if usage_data:
            service.usage_metrics = UsageMetrics(
                request_count=usage_data.get("request_count", 0),
                total_processing_time_ms=usage_data.get("total_processing_time_ms", 0),
                error_count=usage_data.get("error_count", 0),
                total_cost_usd=usage_data.get("total_cost_usd", 0.0),
            )
        
        return service
    
    def __repr__(self) -> str:
        return f"ModelService(id={self.service_id}, name={self.service_name}, platform={self.deployment_platform.value}, status={self.status.value})"
    
    def __str__(self) -> str:
        return f"{self.service_name} ({self.service_id}) on {self.deployment_platform.value} - {self.status.value}"

# Factory functions for common service types

def create_modal_service(
    service_name: str,
    model_id: str,
    inference_endpoint: str,
    health_endpoint: Optional[str] = None,
    capabilities: Optional[List[str]] = None,
    gpu_type: str = "T4",
    memory_mb: int = 16384,
    **kwargs
) -> ModelService:
    """Factory function for Modal-deployed services"""
    service_id = f"{service_name}-modal-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    resources = ResourceRequirements(
        gpu_type=gpu_type,
        memory_mb=memory_mb,
        min_replicas=0,  # Modal can scale to zero
        max_replicas=10,  # Reasonable default
    )
    
    return ModelService(
        service_id=service_id,
        service_name=service_name,
        model_id=model_id,
        deployment_platform=DeploymentPlatform.MODAL,
        service_type=ServiceType.VISION,  # Most Modal services are vision
        inference_endpoint=inference_endpoint,
        health_endpoint=health_endpoint,
        capabilities=capabilities or [],
        resource_requirements=resources,
        metadata={
            "platform": "modal",
            "auto_scaling": True,
            "scale_to_zero": True,
            **kwargs
        },
        status=ServiceStatus.HEALTHY,  # Assume healthy when creating
    )

# REMOVED: create_openai_service function
# OpenAI is a third-party service provider, not a deployment platform.
# Use ThirdPartyServiceManager in the inference module instead.