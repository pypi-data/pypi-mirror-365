"""
ServiceRegistry - Enhanced registry for managing deployed model services

This registry extends the basic ModelRegistry to provide full service lifecycle management
including service discovery, health monitoring, and deployment tracking.
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime, timezone
import asyncio
import json

from .deployment_service import (
    DeployedService, ServiceStatus, ServiceType, DeploymentPlatform,
    HealthMetrics, ServiceMetrics, ResourceRequirements
)
# Backward compatibility
ModelService = DeployedService
UsageMetrics = ServiceMetrics
from .model_repo import ModelRegistry, ModelType, ModelCapability

logger = logging.getLogger(__name__)

class ServiceRegistry:
    """
    Enhanced registry for managing deployed model services in the MaaS platform
    
    This registry provides:
    - Service registration and discovery
    - Health monitoring and status tracking
    - Deployment management
    - Usage metrics collection
    - Integration with existing ModelRegistry
    """
    
    def __init__(self, model_registry: Optional[ModelRegistry] = None):
        self.model_registry = model_registry or ModelRegistry()
        self._service_cache: Dict[str, ModelService] = {}
        self._last_cache_update: Optional[datetime] = None
        self._cache_ttl_seconds = 300  # 5 minutes cache TTL
        
        logger.info("ServiceRegistry initialized with Supabase backend")
    
    # Service Registration and Management
    
    async def register_service(self, service: DeployedService) -> bool:
        """
        Register a new service in the platform
        
        Args:
            service: ModelService instance to register
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            # First ensure the underlying model is registered
            if service.model_id:
                await self._ensure_model_registered(service)
            
            # Check if using Supabase backend
            if hasattr(self.model_registry, 'use_supabase') and self.model_registry.use_supabase:
                return await self._register_service_supabase(service)
            else:
                return await self._register_service_sqlite(service)
                
        except Exception as e:
            logger.error(f"Failed to register service {service.service_id}: {e}")
            return False
    
    async def _register_service_supabase(self, service: DeployedService) -> bool:
        """Register service using Supabase backend"""
        try:
            backend = self.model_registry.backend
            
            # Prepare service data
            service_data = {
                'service_id': service.deployment_id,  # Updated field name
                'service_name': service.service_name,
                'model_id': service.model_id,
                'deployment_platform': service.deployment_platform.value,
                'service_type': service.service_type.value,
                'status': service.status.value,
                'inference_endpoint': service.inference_endpoint,
                'health_endpoint': service.health_endpoint,
                'config': json.dumps(service.config),
                'gpu_type': service.resource_requirements.gpu_type,
                'memory_mb': service.resource_requirements.memory_mb,
                'cpu_cores': service.resource_requirements.cpu_cores,
                'metadata': json.dumps(service.metadata),
            }
            
            # Insert service
            result = backend.supabase.table('services').upsert(service_data).execute()
            
            if not result.data:
                logger.error(f"Failed to insert service {service.service_id}")
                return False
            
            # Insert service capabilities
            if service.capabilities:
                capability_data = [
                    {
                        'service_id': service.service_id,
                        'capability': capability
                    }
                    for capability in service.capabilities
                ]
                
                # Delete existing capabilities first
                backend.supabase.table('service_capabilities').delete().eq('service_id', service.service_id).execute()
                
                # Insert new capabilities
                cap_result = backend.supabase.table('service_capabilities').insert(capability_data).execute()
                
                if not cap_result.data:
                    logger.warning(f"Failed to insert capabilities for service {service.service_id}")
            
            # Update cache
            self._service_cache[service.service_id] = service
            
            logger.info(f"Successfully registered service {service.service_id} in Supabase")
            return True
            
        except Exception as e:
            logger.error(f"Supabase service registration failed: {e}")
            return False
    
    async def _register_service_sqlite(self, service: ModelService) -> bool:
        """Register service using SQLite backend (for development/testing)"""
        # For SQLite, we'll store services in the models table with a special marker
        try:
            success = self.model_registry.register_model(
                model_id=service.service_id,
                model_type=ModelType.VISION,  # Default type
                capabilities=[ModelCapability(cap) for cap in service.capabilities if hasattr(ModelCapability, cap.upper())],
                metadata={
                    **service.metadata,
                    'is_service': True,
                    'service_name': service.service_name,
                    'deployment_platform': service.deployment_platform.value,
                    'service_type': service.service_type.value,
                    'inference_endpoint': service.inference_endpoint,
                    'health_endpoint': service.health_endpoint,
                    'status': service.status.value,
                }
            )
            
            if success:
                self._service_cache[service.service_id] = service
                logger.info(f"Successfully registered service {service.service_id} in SQLite")
            
            return success
            
        except Exception as e:
            logger.error(f"SQLite service registration failed: {e}")
            return False
    
    async def unregister_service(self, service_id: str) -> bool:
        """
        Unregister a service from the platform
        
        Args:
            service_id: ID of the service to unregister
            
        Returns:
            True if unregistration successful, False otherwise
        """
        try:
            if hasattr(self.model_registry, 'use_supabase') and self.model_registry.use_supabase:
                backend = self.model_registry.backend
                result = backend.supabase.table('services').delete().eq('service_id', service_id).execute()
                success = bool(result.data)
            else:
                success = self.model_registry.unregister_model(service_id)
            
            if success and service_id in self._service_cache:
                del self._service_cache[service_id]
                logger.info(f"Unregistered service {service_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to unregister service {service_id}: {e}")
            return False
    
    # Service Discovery
    
    async def get_service(self, service_id: str) -> Optional[DeployedService]:
        """Get a specific service by ID"""
        try:
            # Check cache first
            if service_id in self._service_cache:
                return self._service_cache[service_id]
            
            if hasattr(self.model_registry, 'use_supabase') and self.model_registry.use_supabase:
                return await self._get_service_supabase(service_id)
            else:
                return await self._get_service_sqlite(service_id)
                
        except Exception as e:
            logger.error(f"Failed to get service {service_id}: {e}")
            return None
    
    async def _get_service_supabase(self, service_id: str) -> Optional[ModelService]:
        """Get service from Supabase backend"""
        try:
            backend = self.model_registry.backend
            
            # Get service data
            result = backend.supabase.table('services').select('*').eq('service_id', service_id).execute()
            
            if not result.data:
                return None
            
            service_data = result.data[0]
            
            # Get service capabilities
            cap_result = backend.supabase.table('service_capabilities').select('capability').eq('service_id', service_id).execute()
            capabilities = [cap['capability'] for cap in cap_result.data]
            
            # Create ModelService instance
            service = self._create_service_from_data(service_data, capabilities)
            
            # Cache the service
            self._service_cache[service_id] = service
            
            return service
            
        except Exception as e:
            logger.error(f"Failed to get service from Supabase: {e}")
            return None
    
    async def _get_service_sqlite(self, service_id: str) -> Optional[ModelService]:
        """Get service from SQLite backend"""
        try:
            model_info = self.model_registry.get_model_info(service_id)
            if not model_info or not model_info.get('metadata', {}).get('is_service'):
                return None
            
            # Convert model info to service
            metadata = model_info.get('metadata', {})
            
            # Create basic service from stored metadata
            service = ModelService(
                service_id=service_id,
                service_name=metadata.get('service_name', service_id),
                model_id=metadata.get('model_id'),
                deployment_platform=DeploymentPlatform(metadata.get('deployment_platform', 'modal')),
                service_type=ServiceType(metadata.get('service_type', 'vision')),
                status=ServiceStatus(metadata.get('status', 'healthy')),
                inference_endpoint=metadata.get('inference_endpoint'),
                health_endpoint=metadata.get('health_endpoint'),
                capabilities=model_info.get('capabilities', []),
                metadata=metadata,
            )
            
            self._service_cache[service_id] = service
            return service
            
        except Exception as e:
            logger.error(f"Failed to get service from SQLite: {e}")
            return None
    
    async def get_services_by_name(self, service_name: str) -> List[ModelService]:
        """Get all services with a specific name (multiple deployments)"""
        try:
            if hasattr(self.model_registry, 'use_supabase') and self.model_registry.use_supabase:
                backend = self.model_registry.backend
                result = backend.supabase.rpc('get_healthy_services_by_name', {'name_pattern': service_name}).execute()
                
                services = []
                for row in result.data or []:
                    service = ModelService(
                        service_id=row['service_id'],
                        service_name=row['service_name'],
                        model_id=row['model_id'],
                        deployment_platform=DeploymentPlatform(row['deployment_platform']),
                        service_type=ServiceType.VISION,  # Default, should be in data
                        inference_endpoint=row['inference_endpoint'],
                        health_endpoint=row['health_endpoint'],
                        status=ServiceStatus.HEALTHY,  # From healthy services query
                    )
                    services.append(service)
                    self._service_cache[service.service_id] = service
                
                return services
            else:
                # SQLite fallback - search in model registry
                models = self.model_registry.search_models(service_name)
                services = []
                
                for model_id, model_info in models.items():
                    metadata = model_info.get('metadata', {})
                    if metadata.get('is_service') and metadata.get('service_name') == service_name:
                        service = await self._get_service_sqlite(model_id)
                        if service:
                            services.append(service)
                
                return services
                
        except Exception as e:
            logger.error(f"Failed to get services by name {service_name}: {e}")
            return []
    
    async def get_services_by_capability(self, capability: str) -> List[ModelService]:
        """Get all services that provide a specific capability"""
        try:
            if hasattr(self.model_registry, 'use_supabase') and self.model_registry.use_supabase:
                backend = self.model_registry.backend
                result = backend.supabase.rpc('get_services_by_capability', {'capability_name': capability}).execute()
                
                services = []
                for row in result.data or []:
                    service = self._create_service_from_supabase_row(row)
                    services.append(service)
                    self._service_cache[service.service_id] = service
                
                return services
            else:
                # SQLite fallback
                models = self.model_registry.get_models_by_capability(ModelCapability(capability))
                services = []
                
                for model_id, model_info in models.items():
                    if model_info.get('metadata', {}).get('is_service'):
                        service = await self._get_service_sqlite(model_id)
                        if service:
                            services.append(service)
                
                return services
                
        except Exception as e:
            logger.error(f"Failed to get services by capability {capability}: {e}")
            return []
    
    async def get_active_service(self, service_name: str) -> Optional[ModelService]:
        """
        Get the best active service for a given service name
        
        Returns the healthiest service with the most recent health check
        """
        services = await self.get_services_by_name(service_name)
        
        if not services:
            return None
        
        # Filter to only healthy services
        healthy_services = [s for s in services if s.is_healthy()]
        
        if not healthy_services:
            logger.warning(f"No healthy services found for {service_name}")
            return None
        
        # Return the first healthy service (could add more sophisticated selection logic)
        return healthy_services[0]
    
    # Health Monitoring
    
    async def update_service_health(
        self, 
        service_id: str, 
        health_metrics: HealthMetrics
    ) -> bool:
        """Update health metrics for a service"""
        try:
            if hasattr(self.model_registry, 'use_supabase') and self.model_registry.use_supabase:
                backend = self.model_registry.backend
                
                # Insert health check record
                health_data = {
                    'service_id': service_id,
                    'is_healthy': health_metrics.is_healthy,
                    'response_time_ms': health_metrics.response_time_ms,
                    'status_code': health_metrics.status_code,
                    'cpu_usage_percent': health_metrics.cpu_usage_percent,
                    'memory_usage_mb': health_metrics.memory_usage_mb,
                    'gpu_usage_percent': health_metrics.gpu_usage_percent,
                    'error_message': health_metrics.error_message,
                    'checked_at': health_metrics.checked_at.isoformat() if health_metrics.checked_at else datetime.now(timezone.utc).isoformat(),
                }
                
                result = backend.supabase.table('service_health').insert(health_data).execute()
                
                # Update service status
                new_status = ServiceStatus.HEALTHY if health_metrics.is_healthy else ServiceStatus.UNHEALTHY
                backend.supabase.table('services').update({'status': new_status.value}).eq('service_id', service_id).execute()
                
                # Update cached service
                if service_id in self._service_cache:
                    self._service_cache[service_id].update_health_metrics(health_metrics)
                
                return bool(result.data)
            else:
                # For SQLite, just update cached service
                if service_id in self._service_cache:
                    self._service_cache[service_id].update_health_metrics(health_metrics)
                return True
                
        except Exception as e:
            logger.error(f"Failed to update health for service {service_id}: {e}")
            return False
    
    # Statistics and Monitoring
    
    async def get_service_statistics(self) -> Dict[str, Any]:
        """Get platform-wide service statistics"""
        try:
            if hasattr(self.model_registry, 'use_supabase') and self.model_registry.use_supabase:
                backend = self.model_registry.backend
                result = backend.supabase.rpc('get_service_statistics').execute()
                
                if result.data:
                    return result.data[0]
                
            return {
                "total_services": 0,
                "healthy_services": 0,
                "platforms": {},
                "service_types": {}
            }
            
        except Exception as e:
            logger.error(f"Failed to get service statistics: {e}")
            return {}
    
    # Helper Methods
    
    def _create_service_from_data(self, service_data: Dict[str, Any], capabilities: List[str]) -> ModelService:
        """Create ModelService instance from database row data"""
        # Parse JSON fields
        config = json.loads(service_data.get('config', '{}')) if service_data.get('config') else {}
        metadata = json.loads(service_data.get('metadata', '{}')) if service_data.get('metadata') else {}
        
        # Create resource requirements
        resources = ResourceRequirements(
            gpu_type=service_data.get('gpu_type'),
            memory_mb=service_data.get('memory_mb'),
            cpu_cores=service_data.get('cpu_cores'),
        )
        
        # Create service
        service = ModelService(
            service_id=service_data['service_id'],
            service_name=service_data['service_name'],
            model_id=service_data.get('model_id'),
            deployment_platform=DeploymentPlatform(service_data['deployment_platform']),
            service_type=ServiceType(service_data['service_type']),
            status=ServiceStatus(service_data.get('status', 'pending')),
            inference_endpoint=service_data.get('inference_endpoint'),
            health_endpoint=service_data.get('health_endpoint'),
            capabilities=capabilities,
            config=config,
            resource_requirements=resources,
            metadata=metadata,
        )
        
        # Set timestamps
        if service_data.get('created_at'):
            service.created_at = datetime.fromisoformat(service_data['created_at'].replace('Z', '+00:00'))
        if service_data.get('updated_at'):
            service.updated_at = datetime.fromisoformat(service_data['updated_at'].replace('Z', '+00:00'))
        
        return service
    
    def _create_service_from_supabase_row(self, row: Dict[str, Any]) -> ModelService:
        """Create ModelService from Supabase RPC result row"""
        # Parse JSON fields safely
        config = {}
        metadata = {}
        
        if row.get('config'):
            try:
                config = json.loads(row['config']) if isinstance(row['config'], str) else row['config']
            except json.JSONDecodeError:
                config = {}
        
        if row.get('metadata'):
            try:
                metadata = json.loads(row['metadata']) if isinstance(row['metadata'], str) else row['metadata']
            except json.JSONDecodeError:
                metadata = {}
        
        return ModelService(
            service_id=row['service_id'],
            service_name=row['service_name'],
            model_id=row.get('model_id'),
            deployment_platform=DeploymentPlatform(row['deployment_platform']),
            service_type=ServiceType(row['service_type']),
            status=ServiceStatus(row.get('status', 'pending')),
            inference_endpoint=row.get('inference_endpoint'),
            health_endpoint=row.get('health_endpoint'),
            config=config,
            metadata=metadata,
        )
    
    async def _ensure_model_registered(self, service: ModelService) -> None:
        """Ensure the underlying model is registered in the model registry"""
        if not service.model_id:
            return
        
        # Check if model exists
        model_info = self.model_registry.get_model_info(service.model_id)
        
        if not model_info:
            # Register the model
            model_type = ModelType.VISION  # Default, could be inferred from service type
            capabilities = [ModelCapability(cap) for cap in service.capabilities if hasattr(ModelCapability, cap.upper())]
            
            self.model_registry.register_model(
                model_id=service.model_id,
                model_type=model_type,
                capabilities=capabilities,
                metadata={
                    "description": f"Model used by service {service.service_name}",
                    "registered_by_service": service.service_id,
                }
            )
            
            logger.info(f"Auto-registered model {service.model_id} for service {service.service_id}")
    
    def clear_cache(self) -> None:
        """Clear the service cache"""
        self._service_cache.clear()
        self._last_cache_update = None
        logger.info("Service cache cleared")