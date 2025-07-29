"""
Runtime Management for Self-Owned Deployed Services

This module manages the runtime aspects of self-owned deployed model services.
It does NOT handle third-party API services (OpenAI, Replicate) - those are 
managed in the inference module.

Only for services deployed by ISADeploymentService or similar self-owned deployments.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import httpx
from pathlib import Path

from ...core.types import (
    ServiceStatus, 
    DeploymentPlatform,
    HealthMetrics,
    ServiceMetrics,
    ResourceRequirements
)

logger = logging.getLogger(__name__)


@dataclass
class DeployedService:
    """Runtime information for a self-owned deployed service"""
    service_id: str
    deployment_id: str
    model_id: str
    platform: DeploymentPlatform
    endpoint_url: str
    status: ServiceStatus = ServiceStatus.PENDING
    health_check_url: Optional[str] = None
    api_key: Optional[str] = None
    resource_requirements: Optional[ResourceRequirements] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_health_check: Optional[datetime] = None
    health_metrics: Optional[HealthMetrics] = None
    service_metrics: Optional[ServiceMetrics] = None


class DeployedServiceManager:
    """
    Manages runtime aspects of self-owned deployed services.
    
    Features:
    - Health monitoring for deployed services
    - Service discovery and status tracking
    - Runtime metrics collection
    - Service lifecycle management
    
    Example:
        ```python
        from isa_model.deployment.runtime import DeployedServiceManager
        
        manager = DeployedServiceManager()
        
        # Register a newly deployed service
        service = await manager.register_deployed_service(
            service_id="gemma-4b-alpaca-v1-prod",
            deployment_id="gemma-4b-alpaca-v1-int8-20241230-143022",
            model_id="gemma-4b-alpaca-v1",
            platform=DeploymentPlatform.RUNPOD,
            endpoint_url="https://api.runpod.ai/v2/xyz123/inference"
        )
        
        # Monitor health
        health = await manager.check_service_health(service.service_id)
        ```
    """
    
    def __init__(self, storage_backend: str = "local"):
        """Initialize deployed service manager"""
        self.storage_backend = storage_backend
        self.services: Dict[str, DeployedService] = {}
        self.health_check_interval = 60  # seconds
        self.health_check_timeout = 30   # seconds
        self._monitoring_tasks: Dict[str, asyncio.Task] = {}
        
        logger.info(f"DeployedServiceManager initialized with {storage_backend} backend")
    
    async def register_deployed_service(self,
                                      service_id: str,
                                      deployment_id: str,
                                      model_id: str,
                                      platform: DeploymentPlatform,
                                      endpoint_url: str,
                                      health_check_url: Optional[str] = None,
                                      api_key: Optional[str] = None,
                                      resource_requirements: Optional[ResourceRequirements] = None,
                                      metadata: Optional[Dict[str, Any]] = None) -> DeployedService:
        """Register a newly deployed self-owned service"""
        
        if health_check_url is None:
            # Try common health check patterns
            if endpoint_url.endswith('/'):
                health_check_url = f"{endpoint_url}health"
            else:
                health_check_url = f"{endpoint_url}/health"
        
        service = DeployedService(
            service_id=service_id,
            deployment_id=deployment_id,
            model_id=model_id,
            platform=platform,
            endpoint_url=endpoint_url,
            health_check_url=health_check_url,
            api_key=api_key,
            resource_requirements=resource_requirements,
            metadata=metadata or {},
            status=ServiceStatus.DEPLOYING
        )
        
        self.services[service_id] = service
        
        # Start health monitoring
        await self._start_health_monitoring(service_id)
        
        logger.info(f"Registered deployed service: {service_id} on {platform.value}")
        return service
    
    async def get_service(self, service_id: str) -> Optional[DeployedService]:
        """Get service information"""
        return self.services.get(service_id)
    
    async def list_services(self, 
                          platform: Optional[DeploymentPlatform] = None,
                          status: Optional[ServiceStatus] = None) -> List[DeployedService]:
        """List deployed services with optional filtering"""
        services = list(self.services.values())
        
        if platform:
            services = [s for s in services if s.platform == platform]
        
        if status:
            services = [s for s in services if s.status == status]
        
        return services
    
    async def check_service_health(self, service_id: str) -> Optional[HealthMetrics]:
        """Perform health check on a specific service"""
        service = self.services.get(service_id)
        if not service or not service.health_check_url:
            return None
        
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=self.health_check_timeout) as client:
                headers = {}
                if service.api_key:
                    headers["Authorization"] = f"Bearer {service.api_key}"
                
                response = await client.get(service.health_check_url, headers=headers)
                
                response_time_ms = int((time.time() - start_time) * 1000)
                
                is_healthy = response.status_code == 200
                
                # Try to extract additional metrics from response
                metrics_data = {}
                try:
                    if response.headers.get('content-type', '').startswith('application/json'):
                        metrics_data = response.json()
                except:
                    pass
                
                health_metrics = HealthMetrics(
                    is_healthy=is_healthy,
                    response_time_ms=response_time_ms,
                    status_code=response.status_code,
                    cpu_usage_percent=metrics_data.get('cpu_usage'),
                    memory_usage_mb=metrics_data.get('memory_usage_mb'),
                    gpu_usage_percent=metrics_data.get('gpu_usage'),
                    error_message=None if is_healthy else f"HTTP {response.status_code}",
                    checked_at=datetime.now()
                )
                
                # Update service status based on health
                if is_healthy and service.status == ServiceStatus.DEPLOYING:
                    service.status = ServiceStatus.HEALTHY
                elif not is_healthy and service.status == ServiceStatus.HEALTHY:
                    service.status = ServiceStatus.UNHEALTHY
                
                service.last_health_check = datetime.now()
                service.health_metrics = health_metrics
                
                return health_metrics
                
        except Exception as e:
            logger.error(f"Health check failed for {service_id}: {e}")
            
            error_metrics = HealthMetrics(
                is_healthy=False,
                response_time_ms=int((time.time() - start_time) * 1000),
                error_message=str(e),
                checked_at=datetime.now()
            )
            
            service.status = ServiceStatus.UNHEALTHY
            service.last_health_check = datetime.now()
            service.health_metrics = error_metrics
            
            return error_metrics
    
    async def update_service_metrics(self, 
                                   service_id: str,
                                   request_count: int = 0,
                                   processing_time_ms: int = 0,
                                   error_count: int = 0,
                                   cost_usd: float = 0.0):
        """Update service runtime metrics"""
        service = self.services.get(service_id)
        if not service:
            return
        
        if not service.service_metrics:
            service.service_metrics = ServiceMetrics(
                window_start=datetime.now()
            )
        
        service.service_metrics.request_count += request_count
        service.service_metrics.total_processing_time_ms += processing_time_ms
        service.service_metrics.error_count += error_count
        service.service_metrics.total_cost_usd += cost_usd
        service.service_metrics.window_end = datetime.now()
    
    async def stop_service(self, service_id: str) -> bool:
        """Stop a deployed service and cleanup resources"""
        service = self.services.get(service_id)
        if not service:
            return False
        
        # Stop health monitoring
        await self._stop_health_monitoring(service_id)
        
        # Update status
        service.status = ServiceStatus.STOPPED
        
        # Note: Actual service termination would depend on the platform
        # For RunPod, Modal, etc., we would call their respective APIs
        
        logger.info(f"Stopped service: {service_id}")
        return True
    
    async def remove_service(self, service_id: str) -> bool:
        """Remove service from registry"""
        if service_id in self.services:
            await self._stop_health_monitoring(service_id)
            del self.services[service_id]
            logger.info(f"Removed service: {service_id}")
            return True
        return False
    
    async def _start_health_monitoring(self, service_id: str):
        """Start background health monitoring for a service"""
        if service_id in self._monitoring_tasks:
            return  # Already monitoring
        
        async def health_monitor():
            while service_id in self.services:
                try:
                    await self.check_service_health(service_id)
                    await asyncio.sleep(self.health_check_interval)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Health monitoring error for {service_id}: {e}")
                    await asyncio.sleep(self.health_check_interval)
        
        task = asyncio.create_task(health_monitor())
        self._monitoring_tasks[service_id] = task
        logger.info(f"Started health monitoring for {service_id}")
    
    async def _stop_health_monitoring(self, service_id: str):
        """Stop health monitoring for a service"""
        if service_id in self._monitoring_tasks:
            task = self._monitoring_tasks.pop(service_id)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            logger.info(f"Stopped health monitoring for {service_id}")
    
    async def get_service_status_summary(self) -> Dict[str, Any]:
        """Get summary of all deployed services"""
        summary = {
            "total_services": len(self.services),
            "healthy_services": 0,
            "unhealthy_services": 0,
            "deploying_services": 0,
            "stopped_services": 0,
            "platforms": {},
            "last_updated": datetime.now().isoformat()
        }
        
        for service in self.services.values():
            # Count by status
            if service.status == ServiceStatus.HEALTHY:
                summary["healthy_services"] += 1
            elif service.status == ServiceStatus.UNHEALTHY:
                summary["unhealthy_services"] += 1
            elif service.status == ServiceStatus.DEPLOYING:
                summary["deploying_services"] += 1
            elif service.status == ServiceStatus.STOPPED:
                summary["stopped_services"] += 1
            
            # Count by platform
            platform = service.platform.value
            summary["platforms"][platform] = summary["platforms"].get(platform, 0) + 1
        
        return summary
    
    async def cleanup_old_services(self, max_age_hours: int = 24):
        """Remove services that haven't been healthy for a specified time"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        services_to_remove = []
        for service_id, service in self.services.items():
            if (service.status == ServiceStatus.STOPPED and 
                service.last_health_check and 
                service.last_health_check < cutoff_time):
                services_to_remove.append(service_id)
        
        for service_id in services_to_remove:
            await self.remove_service(service_id)
        
        logger.info(f"Cleaned up {len(services_to_remove)} old services")
        return len(services_to_remove)