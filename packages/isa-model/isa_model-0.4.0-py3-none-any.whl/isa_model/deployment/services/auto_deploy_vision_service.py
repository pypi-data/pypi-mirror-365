#!/usr/bin/env python3
"""
Auto-Deploy Vision Service Wrapper

Automatically deploys Modal services when needed and shuts them down after completion.
"""

import logging
from typing import Dict, Any, Optional, Union, List, BinaryIO

from isa_model.inference.services.vision.base_vision_service import BaseVisionService

logger = logging.getLogger(__name__)


class AutoDeployVisionService(BaseVisionService):
    """
    Vision service wrapper that handles automatic deployment and shutdown
    of Modal services for ISA vision tasks.
    """
    
    def __init__(self, model_name: str = "isa_vision_table", config: dict = None, **kwargs):
        # Initialize BaseVisionService with modal provider
        super().__init__("modal", model_name, **kwargs)
        self.model_name = model_name
        self.config = config or {}
        self.underlying_service = None
        self._factory = None
        
    def _get_factory(self):
        """Get AIFactory instance for service management"""
        if not self._factory:
            from isa_model.inference.ai_factory import AIFactory
            self._factory = AIFactory()
        return self._factory
    
    def _ensure_service_deployed(self) -> bool:
        """Ensure the Modal service is deployed before use"""
        factory = self._get_factory()
        
        # Check if service is available
        app_name = factory._get_modal_app_name(self.model_name)
        if not factory._check_modal_service_availability(app_name):
            logger.info(f"Deploying {self.model_name} service...")
            success = factory._auto_deploy_modal_service(self.model_name)
            if not success:
                logger.error(f"Failed to deploy {self.model_name}")
                return False
            
            # Wait for service to be ready
            logger.info(f"Waiting for {self.model_name} service to be ready...")
            self._wait_for_service_ready(app_name)
        
        # Initialize underlying service using proper factory method
        if not self.underlying_service:
            # Use the factory's get_vision method with modal provider
            self.underlying_service = factory.get_vision(
                model_name=self.model_name, 
                provider_name="modal"
            )
            
        return True
    
    def _wait_for_service_ready(self, app_name: str, max_wait_time: int = 300):
        """Wait for Modal service to be ready by checking health endpoint"""
        import time
        
        logger.info(f"Waiting up to {max_wait_time} seconds for {app_name} to be ready...")
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                import modal
                # Try to lookup the app and call health check
                app = modal.App.lookup(app_name)
                
                # Different health check methods for different services
                if "table" in app_name:
                    service_cls = modal.Cls.from_name(app_name, "QwenTableExtractionService")
                elif "ui" in app_name:
                    service_cls = modal.Cls.from_name(app_name, "UIDetectionService") 
                elif "doc" in app_name:
                    service_cls = modal.Cls.from_name(app_name, "DocumentAnalysisService")
                else:
                    # Default wait time for unknown services
                    time.sleep(60)
                    return
                
                # Try to call health check
                health_result = service_cls().health_check.remote()
                if health_result and health_result.get("status") == "healthy":
                    logger.info(f"Service {app_name} is ready!")
                    return
                    
            except Exception as e:
                logger.debug(f"Service not ready yet: {e}")
            
            # Wait 10 seconds before next check
            time.sleep(10)
            logger.info(f"Still waiting for {app_name}... ({int(time.time() - start_time)}s elapsed)")
        
        logger.warning(f"Service {app_name} may not be fully ready after {max_wait_time}s")
    
    def _shutdown_service_after_completion(self):
        """Shutdown Modal service after task completion"""
        try:
            factory = self._get_factory()
            factory._shutdown_modal_service(self.model_name)
        except Exception as e:
            logger.warning(f"Failed to shutdown service {self.model_name}: {e}")
    
    async def extract_table_data(
        self, 
        image: Union[str, BinaryIO],
        extraction_format: str = "markdown",
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract table data with auto-deploy and shutdown"""
        
        # Ensure service is deployed
        if not self._ensure_service_deployed():
            return {
                'success': False,
                'error': f'Failed to deploy {self.model_name} service',
                'service': self.model_name
            }
        
        try:
            # Call the underlying service
            result = await self.underlying_service.extract_table_data(
                image=image,
                extraction_format=extraction_format,
                custom_prompt=custom_prompt
            )
            
            # Shutdown service after completion
            self._shutdown_service_after_completion()
            
            return result
            
        except Exception as e:
            logger.error(f"Table extraction failed: {e}")
            # Still try to shutdown even if request failed
            self._shutdown_service_after_completion()
            
            return {
                'success': False,
                'error': str(e),
                'service': self.model_name
            }
    
    async def batch_extract_tables(
        self, 
        images: List[Union[str, BinaryIO]], 
        extraction_format: str = "markdown"
    ) -> Dict[str, Any]:
        """Batch extract tables with auto-deploy and shutdown"""
        
        # Ensure service is deployed
        if not self._ensure_service_deployed():
            return {
                'success': False,
                'error': f'Failed to deploy {self.model_name} service',
                'service': self.model_name
            }
        
        try:
            # Call the underlying service
            result = await self.underlying_service.batch_extract_tables(
                images=images,
                extraction_format=extraction_format
            )
            
            # Shutdown service after completion
            self._shutdown_service_after_completion()
            
            return result
            
        except Exception as e:
            logger.error(f"Batch table extraction failed: {e}")
            # Still try to shutdown even if request failed
            self._shutdown_service_after_completion()
            
            return {
                'success': False,
                'error': str(e),
                'service': self.model_name
            }
    
    async def detect_ui_elements(self, image: Union[str, BinaryIO]) -> Dict[str, Any]:
        """Detect UI elements with auto-deploy and shutdown"""
        
        # Ensure service is deployed
        if not self._ensure_service_deployed():
            return {
                'success': False,
                'error': f'Failed to deploy {self.model_name} service',
                'service': self.model_name
            }
        
        try:
            # Call the underlying service
            result = await self.underlying_service.detect_ui_elements(image=image)
            
            # Shutdown service after completion
            self._shutdown_service_after_completion()
            
            return result
            
        except Exception as e:
            logger.error(f"UI detection failed: {e}")
            # Still try to shutdown even if request failed
            self._shutdown_service_after_completion()
            
            return {
                'success': False,
                'error': str(e),
                'service': self.model_name
            }
    
    async def analyze_document(self, image: Union[str, BinaryIO]) -> Dict[str, Any]:
        """Analyze document with auto-deploy and shutdown"""
        
        # Ensure service is deployed
        if not self._ensure_service_deployed():
            return {
                'success': False,
                'error': f'Failed to deploy {self.model_name} service',
                'service': self.model_name
            }
        
        try:
            # Call the underlying service
            result = await self.underlying_service.analyze_document(image=image)
            
            # Shutdown service after completion
            self._shutdown_service_after_completion()
            
            return result
            
        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
            # Still try to shutdown even if request failed
            self._shutdown_service_after_completion()
            
            return {
                'success': False,
                'error': str(e),
                'service': self.model_name
            }
    
    # Implement all required abstract methods from BaseVisionService
    
    async def invoke(
        self, 
        image: Union[str, BinaryIO],
        prompt: Optional[str] = None,
        task: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Unified invoke method for all vision operations"""
        if not self._ensure_service_deployed():
            return {
                'success': False,
                'error': f'Failed to deploy {self.model_name} service',
                'service': self.model_name
            }
        
        try:
            result = await self.underlying_service.invoke(image=image, prompt=prompt, task=task, **kwargs)
            self._shutdown_service_after_completion()
            return result
        except Exception as e:
            logger.error(f"Vision invoke failed: {e}")
            self._shutdown_service_after_completion()
            return {
                'success': False,
                'error': str(e),
                'service': self.model_name
            }
    
    async def analyze_image(
        self, 
        image: Union[str, BinaryIO],
        prompt: Optional[str] = None,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Analyze image with auto-deploy and shutdown"""
        if not self._ensure_service_deployed():
            return {
                'success': False,
                'error': f'Failed to deploy {self.model_name} service',
                'service': self.model_name
            }
        
        try:
            result = await self.underlying_service.analyze_image(
                image=image, prompt=prompt, max_tokens=max_tokens
            )
            self._shutdown_service_after_completion()
            return result
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            self._shutdown_service_after_completion()
            return {
                'success': False,
                'error': str(e),
                'service': self.model_name
            }
    
    async def analyze_images(
        self, 
        images: List[Union[str, BinaryIO]],
        prompt: Optional[str] = None,
        max_tokens: int = 1000
    ) -> List[Dict[str, Any]]:
        """Analyze multiple images with auto-deploy and shutdown"""
        if not self._ensure_service_deployed():
            return [{
                'success': False,
                'error': f'Failed to deploy {self.model_name} service',
                'service': self.model_name
            }]
        
        try:
            result = await self.underlying_service.analyze_images(
                images=images, prompt=prompt, max_tokens=max_tokens
            )
            self._shutdown_service_after_completion()
            return result
        except Exception as e:
            logger.error(f"Multiple image analysis failed: {e}")
            self._shutdown_service_after_completion()
            return [{
                'success': False,
                'error': str(e),
                'service': self.model_name
            }]
    
    async def describe_image(
        self, 
        image: Union[str, BinaryIO],
        detail_level: str = "medium"
    ) -> Dict[str, Any]:
        """Generate detailed description of image"""
        if not self._ensure_service_deployed():
            return {
                'success': False,
                'error': f'Failed to deploy {self.model_name} service',
                'service': self.model_name
            }
        
        try:
            result = await self.underlying_service.describe_image(
                image=image, detail_level=detail_level
            )
            self._shutdown_service_after_completion()
            return result
        except Exception as e:
            logger.error(f"Image description failed: {e}")
            self._shutdown_service_after_completion()
            return {
                'success': False,
                'error': str(e),
                'service': self.model_name
            }
    
    async def extract_text(self, image: Union[str, BinaryIO]) -> Dict[str, Any]:
        """Extract text from image (OCR)"""
        if not self._ensure_service_deployed():
            return {
                'success': False,
                'error': f'Failed to deploy {self.model_name} service',
                'service': self.model_name
            }
        
        try:
            result = await self.underlying_service.extract_text(image=image)
            self._shutdown_service_after_completion()
            return result
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            self._shutdown_service_after_completion()
            return {
                'success': False,
                'error': str(e),
                'service': self.model_name
            }
    
    async def detect_objects(
        self, 
        image: Union[str, BinaryIO],
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """Detect objects in image"""
        if not self._ensure_service_deployed():
            return {
                'success': False,
                'error': f'Failed to deploy {self.model_name} service',
                'service': self.model_name
            }
        
        try:
            result = await self.underlying_service.detect_objects(
                image=image, confidence_threshold=confidence_threshold
            )
            self._shutdown_service_after_completion()
            return result
        except Exception as e:
            logger.error(f"Object detection failed: {e}")
            self._shutdown_service_after_completion()
            return {
                'success': False,
                'error': str(e),
                'service': self.model_name
            }
    
    async def get_object_coordinates(
        self,
        image: Union[str, BinaryIO],
        object_name: str
    ) -> Dict[str, Any]:
        """Get coordinates of a specific object in the image"""
        if not self._ensure_service_deployed():
            return {
                'success': False,
                'error': f'Failed to deploy {self.model_name} service',
                'service': self.model_name
            }
        
        try:
            result = await self.underlying_service.get_object_coordinates(
                image=image, object_name=object_name
            )
            self._shutdown_service_after_completion()
            return result
        except Exception as e:
            logger.error(f"Object coordinate detection failed: {e}")
            self._shutdown_service_after_completion()
            return {
                'success': False,
                'error': str(e),
                'service': self.model_name
            }
    
    async def classify_image(
        self, 
        image: Union[str, BinaryIO],
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Classify image into categories"""
        if not self._ensure_service_deployed():
            return {
                'success': False,
                'error': f'Failed to deploy {self.model_name} service',
                'service': self.model_name
            }
        
        try:
            result = await self.underlying_service.classify_image(
                image=image, categories=categories
            )
            self._shutdown_service_after_completion()
            return result
        except Exception as e:
            logger.error(f"Image classification failed: {e}")
            self._shutdown_service_after_completion()
            return {
                'success': False,
                'error': str(e),
                'service': self.model_name
            }
    
    async def compare_images(
        self, 
        image1: Union[str, BinaryIO],
        image2: Union[str, BinaryIO]
    ) -> Dict[str, Any]:
        """Compare two images for similarity"""
        if not self._ensure_service_deployed():
            return {
                'success': False,
                'error': f'Failed to deploy {self.model_name} service',
                'service': self.model_name
            }
        
        try:
            result = await self.underlying_service.compare_images(
                image1=image1, image2=image2
            )
            self._shutdown_service_after_completion()
            return result
        except Exception as e:
            logger.error(f"Image comparison failed: {e}")
            self._shutdown_service_after_completion()
            return {
                'success': False,
                'error': str(e),
                'service': self.model_name
            }
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported image formats"""
        # Initialize underlying service if needed (non-async)
        if not self.underlying_service:
            factory = self._get_factory()
            self.underlying_service = factory.get_vision(
                model_name=self.model_name, 
                provider_name="modal"
            )
        return self.underlying_service.get_supported_formats()
    
    def get_max_image_size(self) -> Dict[str, int]:
        """Get maximum supported image dimensions"""
        # Initialize underlying service if needed (non-async)
        if not self.underlying_service:
            factory = self._get_factory()
            self.underlying_service = factory.get_vision(
                model_name=self.model_name, 
                provider_name="modal"
            )
        return self.underlying_service.get_max_image_size()
    
    async def close(self):
        """Cleanup resources"""
        if self.underlying_service:
            await self.underlying_service.close()
        # Ensure service is shut down
        self._shutdown_service_after_completion()
    
    # Pass through other methods to underlying service
    async def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate image (not applicable for ISA vision services)"""
        return {
            'success': False,
            'error': 'Image generation not supported by ISA vision services',
            'service': self.model_name
        }