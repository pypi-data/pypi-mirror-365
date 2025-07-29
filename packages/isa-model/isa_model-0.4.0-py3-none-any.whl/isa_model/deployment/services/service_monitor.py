"""
Service Health Monitor - Automated health checking and service discovery for MaaS platform

This module provides automated health monitoring and service discovery capabilities
for the ISA Model MaaS platform.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import httpx
import json

from .service_registry import ServiceRegistry
from .model_service import ModelService, HealthMetrics, ServiceStatus

logger = logging.getLogger(__name__)

class ServiceMonitor:
    """
    Service health monitor that automatically checks service health and updates registry
    
    Features:
    - Periodic health checks for all registered services
    - Automatic service discovery from endpoints
    - Health metrics collection and storage
    - Service status updates based on health
    """
    
    def __init__(self, service_registry: ServiceRegistry, check_interval: int = 300):
        """
        Initialize the service monitor
        
        Args:
            service_registry: ServiceRegistry instance to monitor
            check_interval: Health check interval in seconds (default: 5 minutes)
        """
        self.service_registry = service_registry
        self.check_interval = check_interval
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        
        logger.info(f"ServiceMonitor initialized with {check_interval}s check interval")
    
    async def start_monitoring(self):
        """Start the health monitoring background task"""
        if self._monitoring:
            logger.warning("Service monitoring is already running")
            return
        
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Service health monitoring started")
    
    async def stop_monitoring(self):
        """Stop the health monitoring background task"""
        if not self._monitoring:
            return
        
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Service health monitoring stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop that runs health checks periodically"""
        while self._monitoring:
            try:
                await self.check_all_services()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(min(self.check_interval, 60))  # Don't wait too long on error
    
    async def check_all_services(self) -> Dict[str, bool]:
        """
        Check health of all registered services
        
        Returns:
            Dictionary mapping service_id to health status (True = healthy)
        """
        # Get all services from registry - this is a simplified implementation
        # In practice, you'd want a method to get all services from ServiceRegistry
        results = {}
        
        try:
            # For now, we'll check known service names
            known_services = ["isa_vision_table", "isa_vision_ui", "isa_vision_doc"]
            
            for service_name in known_services:
                try:
                    services = await self.service_registry.get_services_by_name(service_name)
                    for service in services:
                        health_result = await self.check_service_health(service)
                        results[service.service_id] = health_result
                except Exception as e:
                    logger.error(f"Failed to check services for {service_name}: {e}")
            
            logger.info(f"Health check completed for {len(results)} services")
            return results
            
        except Exception as e:
            logger.error(f"Failed to check all services: {e}")
            return results
    
    async def check_service_health(self, service: ModelService) -> bool:
        """
        Check health of a specific service
        
        Args:
            service: ModelService instance to check
            
        Returns:
            True if service is healthy, False otherwise
        """
        start_time = time.time()
        
        try:
            # Check if service has a health endpoint
            health_endpoint = service.health_endpoint or service.get_endpoint_url("health")
            
            if not health_endpoint:
                # No health endpoint, try to ping inference endpoint
                health_endpoint = service.inference_endpoint
            
            if not health_endpoint:
                logger.warning(f"No endpoint available for service {service.service_id}")
                return False
            
            # Perform health check
            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    response = await client.get(health_endpoint)
                    response_time_ms = int((time.time() - start_time) * 1000)
                    
                    # Create health metrics
                    health_metrics = HealthMetrics(
                        is_healthy=response.status_code == 200,
                        response_time_ms=response_time_ms,
                        status_code=response.status_code,
                        checked_at=datetime.now(timezone.utc)
                    )
                    
                    # Try to extract additional metrics from response
                    if response.status_code == 200:
                        try:
                            health_data = response.json()
                            if isinstance(health_data, dict):
                                # Extract metrics if available
                                health_metrics.cpu_usage_percent = health_data.get("cpu_usage")
                                health_metrics.memory_usage_mb = health_data.get("memory_usage_mb")
                                health_metrics.gpu_usage_percent = health_data.get("gpu_usage")
                        except json.JSONDecodeError:
                            pass  # Health endpoint might not return JSON
                    else:
                        health_metrics.error_message = f"HTTP {response.status_code}: {response.text[:200]}"
                    
                    # Update service health in registry
                    await self.service_registry.update_service_health(service.service_id, health_metrics)
                    
                    logger.debug(f"Health check for {service.service_id}: {health_metrics.is_healthy} ({response_time_ms}ms)")
                    return health_metrics.is_healthy
                    
                except httpx.TimeoutException:
                    # Service is not responding
                    health_metrics = HealthMetrics(
                        is_healthy=False,
                        response_time_ms=int((time.time() - start_time) * 1000),
                        error_message="Service timeout",
                        checked_at=datetime.now(timezone.utc)
                    )
                    
                    await self.service_registry.update_service_health(service.service_id, health_metrics)
                    logger.warning(f"Service {service.service_id} health check timed out")
                    return False
                    
                except httpx.RequestError as e:
                    # Network or connection error
                    health_metrics = HealthMetrics(
                        is_healthy=False,
                        response_time_ms=int((time.time() - start_time) * 1000),
                        error_message=f"Request error: {str(e)}",
                        checked_at=datetime.now(timezone.utc)
                    )
                    
                    await self.service_registry.update_service_health(service.service_id, health_metrics)
                    logger.warning(f"Service {service.service_id} health check failed: {e}")
                    return False
                    
        except Exception as e:
            # Unexpected error
            health_metrics = HealthMetrics(
                is_healthy=False,
                response_time_ms=int((time.time() - start_time) * 1000),
                error_message=f"Health check error: {str(e)}",
                checked_at=datetime.now(timezone.utc)
            )
            
            try:
                await self.service_registry.update_service_health(service.service_id, health_metrics)
            except Exception as update_error:
                logger.error(f"Failed to update health metrics: {update_error}")
            
            logger.error(f"Unexpected error checking service {service.service_id}: {e}")
            return False
    
    async def discover_services(self) -> List[ModelService]:
        """
        Discover services from known endpoints and register them if not already registered
        
        Returns:
            List of discovered ModelService instances
        """
        discovered_services = []
        
        # Known service endpoints to check for discovery
        known_endpoints = [
            {
                "name": "isa_vision_table",
                "base_url": "https://qwen-vision-table.modal.run",
                "service_type": "vision",
                "capabilities": ["table_detection", "table_structure_recognition"]
            },
            {
                "name": "isa_vision_doc", 
                "base_url": "https://isa-vision-doc.modal.run",
                "service_type": "vision",
                "capabilities": ["table_detection", "ocr", "image_analysis"]
            },
            {
                "name": "isa_vision_ui",
                "base_url": "https://isa-vision-ui.modal.run", 
                "service_type": "vision",
                "capabilities": ["ui_detection", "element_detection"]
            }
        ]
        
        for endpoint_info in known_endpoints:
            try:
                service = await self._discover_service_from_endpoint(endpoint_info)
                if service:
                    discovered_services.append(service)
            except Exception as e:
                logger.warning(f"Failed to discover service from {endpoint_info['name']}: {e}")
        
        logger.info(f"Discovered {len(discovered_services)} services")
        return discovered_services
    
    async def _discover_service_from_endpoint(self, endpoint_info: Dict[str, Any]) -> Optional[ModelService]:
        """
        Discover a service from an endpoint by checking its health/info endpoint
        
        Args:
            endpoint_info: Dictionary with service endpoint information
            
        Returns:
            ModelService instance if discovered successfully, None otherwise
        """
        try:
            base_url = endpoint_info["base_url"]
            health_url = f"{base_url}/health_check"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(health_url)
                
                if response.status_code == 200:
                    # Service is responding, check if it's already registered
                    existing_services = await self.service_registry.get_services_by_name(endpoint_info["name"])
                    
                    if existing_services:
                        logger.debug(f"Service {endpoint_info['name']} already registered")
                        return existing_services[0]  # Return existing service
                    
                    # Service is not registered, create and register it
                    from .model_service import ServiceType, DeploymentPlatform, ServiceStatus, ResourceRequirements
                    
                    service = ModelService(
                        service_id=f"{endpoint_info['name']}-discovered-{int(time.time())}",
                        service_name=endpoint_info["name"],
                        model_id=f"{endpoint_info['name']}-model",
                        deployment_platform=DeploymentPlatform.MODAL,
                        service_type=ServiceType.VISION,
                        status=ServiceStatus.HEALTHY,
                        inference_endpoint=f"{base_url}/",
                        health_endpoint=health_url,
                        capabilities=endpoint_info.get("capabilities", []),
                        resource_requirements=ResourceRequirements(),
                        metadata={
                            "discovered": True,
                            "discovery_time": datetime.now(timezone.utc).isoformat(),
                            "base_url": base_url
                        }
                    )
                    
                    # Register the discovered service
                    success = await self.service_registry.register_service(service)
                    
                    if success:
                        logger.info(f"Successfully registered discovered service: {endpoint_info['name']}")
                        return service
                    else:
                        logger.warning(f"Failed to register discovered service: {endpoint_info['name']}")
                        return None
                        
                else:
                    logger.debug(f"Service at {base_url} not responding (HTTP {response.status_code})")
                    return None
                    
        except Exception as e:
            logger.warning(f"Failed to discover service from {endpoint_info['base_url']}: {e}")
            return None
    
    async def get_service_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive service statistics including health metrics
        
        Returns:
            Dictionary with service statistics
        """
        try:
            # Get basic statistics from registry
            stats = await self.service_registry.get_service_statistics()
            
            # Add monitoring-specific statistics
            stats.update({
                "monitoring_enabled": self._monitoring,
                "check_interval_seconds": self.check_interval,
                "last_check": datetime.now(timezone.utc).isoformat()
            })
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get service statistics: {e}")
            return {
                "error": str(e),
                "monitoring_enabled": self._monitoring,
                "check_interval_seconds": self.check_interval
            }
    
    def __del__(self):
        """Cleanup when monitor is destroyed"""
        if self._monitoring and self._monitor_task:
            try:
                self._monitor_task.cancel()
            except:
                pass