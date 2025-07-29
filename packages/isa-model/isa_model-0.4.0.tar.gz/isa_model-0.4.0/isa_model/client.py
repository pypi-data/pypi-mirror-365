#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ISA Model Client - Unified AI Service Interface
===============================================

功能描述：
ISA Model平台的统一客户端接口，提供智能模型选择和简化的API调用

主要功能：
- 多模态AI服务统一接口：文本、视觉、音频、图像生成、嵌入向量
- 智能模型自动选择：基于任务类型和输入数据自动选择最适合的模型
- 流式响应支持：支持实时流式文本生成，提供更好的用户体验  
- 远程/本地服务：支持本地服务调用和远程API调用两种模式
- 成本跟踪：自动计算和跟踪API调用成本
- 工具支持：支持LangChain工具集成，扩展模型能力
- 缓存机制：服务实例缓存，提高性能

输入接口：
- input_data: 多类型输入数据（文本、图像路径、音频文件、字节数据等）
- task: 任务类型（chat, analyze, generate_speech, transcribe等）
- service_type: 服务类型（text, vision, audio, image, embedding）
- model: 可选模型名称（如不指定则智能选择）
- provider: 可选提供商名称（openai, ollama, replicate等）

输出格式：
- 统一响应字典，包含result和metadata
- 流式响应：包含stream异步生成器
- 非流式响应：包含result结果数据
- metadata：包含模型信息、计费信息、选择原因等

核心依赖：
- isa_model.inference.ai_factory: AI服务工厂
- isa_model.core.services.intelligent_model_selector: 智能模型选择器
- aiohttp: HTTP客户端（远程API模式）
- asyncio: 异步编程支持

使用示例：
```python
# 创建客户端
client = ISAModelClient()

# 流式文本生成
result = await client.invoke("写一个故事", "chat", "text")
async for token in result["stream"]:
    print(token, end="", flush=True)

# 图像分析
result = await client.invoke("image.jpg", "analyze", "vision")
print(result["result"])

# 语音合成
result = await client.invoke("Hello world", "generate_speech", "audio")
print(result["result"])
```

架构特点：
- 单例模式：确保配置一致性
- 异步支持：所有操作都是异步的
- 错误处理：统一的错误处理和响应格式
- 可扩展性：支持新的服务提供商和模型

优化建议：
1. 增加请求重试机制：处理网络不稳定情况
2. 添加请求限流：避免超出API限制
3. 优化缓存策略：支持LRU缓存和TTL过期
4. 增加监控指标：记录延迟、成功率等指标
5. 支持批处理：提高大量请求的处理效率
6. 添加配置验证：启动时验证API密钥和配置
"""

import logging
import asyncio
from typing import Any, Dict, Optional, List, Union
from pathlib import Path

from isa_model.inference.ai_factory import AIFactory

try:
    from isa_model.core.services.intelligent_model_selector import IntelligentModelSelector, get_model_selector
    INTELLIGENT_SELECTOR_AVAILABLE = True
except ImportError:
    IntelligentModelSelector = None
    get_model_selector = None
    INTELLIGENT_SELECTOR_AVAILABLE = False

logger = logging.getLogger(__name__)


class ISAModelClient:
    """
    Unified ISA Model Client with intelligent model selection
    
    Usage:
        client = ISAModelClient()
        response = await client.invoke("image.jpg", "analyze_image", "vision")
        response = await client.invoke("Hello world", "generate_speech", "audio")
        response = await client.invoke("audio.mp3", "transcribe", "audio") 
    """
    
    # Consolidated task mappings for all service types
    TASK_MAPPINGS = {
        "vision": {
            # Core tasks (direct mapping)
            "analyze": "analyze",
            "describe": "describe", 
            "extract": "extract",
            "detect": "detect",
            "classify": "classify",
            "compare": "compare",
            
            # Common aliases (backward compatibility)
            "analyze_image": "analyze",
            "describe_image": "describe",
            "extract_text": "extract",
            "extract_table": "extract", 
            "detect_objects": "detect",
            "detect_ui": "detect",
            "detect_ui_elements": "detect",
            "get_coordinates": "detect",
            "ocr": "extract",
            "ui_analysis": "analyze",
            "navigation": "analyze"
        },
        "audio": {
            "generate_speech": "synthesize",
            "text_to_speech": "synthesize", 
            "tts": "synthesize",
            "transcribe": "transcribe",
            "speech_to_text": "transcribe",
            "stt": "transcribe",
            "translate": "translate",
            "detect_language": "detect_language"
        },
        "text": {
            "chat": "chat",
            "generate": "generate",
            "complete": "complete",
            "translate": "translate",
            "summarize": "summarize",
            "analyze": "analyze",
            "extract": "extract",
            "classify": "classify"
        },
        "image": {
            "generate_image": "generate",
            "generate": "generate",
            "img2img": "img2img", 
            "image_to_image": "img2img",
            "generate_batch": "generate_batch"
        },
        "embedding": {
            "create_embedding": "embed",
            "embed": "embed",
            "embed_batch": "embed_batch",
            "chunk_and_embed": "chunk_and_embed",
            "similarity": "similarity",
            "find_similar": "find_similar",
            "rerank": "rerank",
            "rerank_documents": "rerank_documents",
            "document_ranking": "document_ranking"
        }
    }
    
    # Service type configuration
    SUPPORTED_SERVICE_TYPES = {"vision", "audio", "text", "image", "embedding"}
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 service_endpoint: Optional[str] = None,
                 api_key: Optional[str] = None):
        """Initialize ISA Model Client
        
        Args:
            config: Optional configuration override
            service_endpoint: Optional service endpoint URL (if None, uses local AI Factory)
            api_key: Optional API key for authentication (can also be set via ISA_API_KEY env var)
        """
        self.config = config or {}
        self.service_endpoint = service_endpoint
        
        # Handle API key authentication
        import os
        self.api_key = api_key or os.getenv("ISA_API_KEY")
        if self.api_key:
            logger.info("API key provided for authentication")
        else:
            logger.debug("No API key provided - using anonymous access")
        
        # Initialize AI Factory for direct service access (when service_endpoint is None)
        if not self.service_endpoint:
            self.ai_factory = AIFactory.get_instance()
        else:
            self.ai_factory = None
            logger.info(f"Using remote service endpoint: {self.service_endpoint}")
            
        # HTTP client for remote API calls
        self._http_session = None
        
        # Initialize intelligent model selector
        self.model_selector = None
        if INTELLIGENT_SELECTOR_AVAILABLE:
            try:
                # Initialize asynchronously later
                self._model_selector_task = None
                logger.info("Intelligent model selector will be initialized on first use")
            except Exception as e:
                logger.warning(f"Failed to setup model selector: {e}")
        else:
            logger.info("Intelligent model selector not available, using default selection")
        
        # Cache for frequently used services
        self._service_cache: Dict[str, Any] = {}
        
        logger.info("ISA Model Client initialized")
    
    async def _get_http_session(self):
        """Get or create HTTP session for remote API calls"""
        if self._http_session is None:
            import aiohttp
            headers = {}
            
            # Add API key authentication if available
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
                headers["X-API-Key"] = self.api_key
            
            self._http_session = aiohttp.ClientSession(headers=headers)
            
        return self._http_session
    
    async def _make_api_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to remote API endpoint"""
        if not self.service_endpoint:
            raise ValueError("Service endpoint not configured for remote API calls")
        
        session = await self._get_http_session()
        url = f"{self.service_endpoint.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            async with session.post(url, json=data) as response:
                if response.status == 401:
                    raise Exception("Authentication required or invalid API key")
                elif response.status == 403:
                    raise Exception("Insufficient permissions")
                elif not response.ok:
                    error_detail = await response.text()
                    raise Exception(f"API request failed ({response.status}): {error_detail}")
                
                return await response.json()
                
        except Exception as e:
            logger.error(f"Remote API request failed: {e}")
            raise
    
    async def close(self):
        """Close HTTP session and cleanup resources"""
        if self._http_session:
            await self._http_session.close()
            self._http_session = None
    
    async def _invoke_remote_api(
        self,
        input_data: Union[str, bytes, Path, Dict[str, Any], List[Any]],
        task: str,
        service_type: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        stream: Optional[bool] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Invoke remote API endpoint"""
        try:
            # Prepare request data for unified API
            request_data = {
                "task": task,
                "service_type": service_type,
                **kwargs
            }
            
            # Add model and provider if specified
            if model:
                request_data["model"] = model
            if provider:
                request_data["provider"] = provider
            # For remote API, disable streaming to get JSON response
            request_data["stream"] = False
            
            # Handle different input data types
            if isinstance(input_data, (str, Path)):
                request_data["input_data"] = str(input_data)
            elif isinstance(input_data, (dict, list)):
                request_data["input_data"] = input_data
            else:
                # For binary data, convert to base64
                import base64
                if isinstance(input_data, bytes):
                    request_data["input_data"] = base64.b64encode(input_data).decode()
                    request_data["data_type"] = "base64"
                else:
                    request_data["input_data"] = str(input_data)
            
            # Make API request
            response = await self._make_api_request("api/v1/invoke", request_data)
            
            return response
            
        except Exception as e:
            logger.error(f"Remote API invocation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "task": task,
                    "service_type": service_type,
                    "endpoint": "remote"
                }
            }
    
    async def invoke(
        self, 
        input_data: Union[str, bytes, Path, Dict[str, Any], List[Any]], 
        task: str, 
        service_type: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        stream: Optional[bool] = None,
        show_reasoning: Optional[bool] = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Unified invoke method with intelligent model selection
        
        Args:
            input_data: Input data (str, LangChain messages, image path, audio, etc.)
            task: Task to perform (chat, analyze_image, generate_speech, transcribe, etc.)
            service_type: Type of service (text, vision, audio, image, embedding)
            model: Model name (if None, uses intelligent selection)
            provider: Provider name (if None, uses intelligent selection)
            stream: Enable streaming for text tasks (default True for chat/generate tasks, supports tools)
            show_reasoning: Show reasoning process for O4 models (uses Responses API)
            **kwargs: Additional task-specific parameters (including tools for LangChain)
            
        Returns:
            Unified response dictionary with result and metadata
            For streaming: result["stream"] contains async generator
            For non-streaming: result["result"] contains the response
            
        Examples:
            # Text tasks with streaming (default for chat)
            result = await client.invoke("Write a story", "chat", "text")
            if "stream" in result:
                async for chunk in result["stream"]:
                    print(chunk, end="", flush=True)
            else:
                print(result["result"])
            
            # Text tasks with tools (also supports streaming)
            result = await client.invoke("What's the weather?", "chat", "text", tools=[get_weather])
            if "stream" in result:
                async for chunk in result["stream"]:
                    print(chunk, end="", flush=True)
            else:
                print(result["result"])
            
            # Vision tasks (always non-streaming)
            result = await client.invoke("image.jpg", "analyze", "vision")
            print(result["result"])
            
            # Audio tasks  
            result = await client.invoke("Hello world", "generate_speech", "audio")
            print(result["result"])
            
            # Image generation
            result = await client.invoke("A beautiful sunset", "generate_image", "image")
            print(result["result"])
            
            # Embedding
            result = await client.invoke("Text to embed", "create_embedding", "embedding")
            print(result["result"])
        """
        try:
            # If using remote service endpoint, make API call
            if self.service_endpoint:
                return await self._invoke_remote_api(
                    input_data=input_data,
                    task=task,
                    service_type=service_type,
                    model=model,
                    provider=provider,
                    stream=stream,
                    **kwargs
                )
            
            # Set default streaming for text tasks
            if stream is None and service_type == "text":
                if task in ["chat", "generate"]:
                    stream = True   # Enable streaming for chat and generate tasks
                else:
                    stream = False  # Disable for other text tasks
            
            # If streaming is enabled for text tasks, return streaming response
            if stream and service_type == "text":
                return await self._invoke_service_streaming(
                    input_data=input_data,
                    task=task,
                    service_type=service_type,
                    model_hint=model,
                    provider_hint=provider,
                    show_reasoning=show_reasoning,  # Explicitly pass show_reasoning
                    **kwargs
                )
            else:
                # Use regular non-streaming service
                return await self._invoke_service(
                    input_data=input_data,
                    task=task,
                    service_type=service_type,
                    model_hint=model,
                    provider_hint=provider,
                    stream=False,  # Force non-streaming
                    **kwargs
                )
                
        except Exception as e:
            return self._handle_error(e, {
                "operation": "invoke",
                "task": task,
                "service_type": service_type,
                "input_type": type(input_data).__name__
            })
    
    async def invoke_stream(
        self, 
        input_data: Union[str, bytes, Path, Dict[str, Any], List[Any]], 
        task: str, 
        service_type: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        return_metadata: bool = False,
        **kwargs
    ):
        """
        Unified streaming invoke method - returns async generator for real-time token streaming
        
        Args:
            input_data: Input data (str, LangChain messages, image path, audio, etc.)
            task: Task to perform (chat, analyze_image, generate_speech, transcribe, etc.)
            service_type: Type of service (text, vision, audio, image, embedding)
            model: Model name (if None, uses intelligent selection)
            provider: Provider name (if None, uses intelligent selection)
            return_metadata: If True, yields ('metadata', metadata_dict) as final item
            **kwargs: Additional task-specific parameters (including tools for LangChain)
            
        Returns:
            For text services: AsyncGenerator[Union[str, Tuple[str, Dict]], None] - yields tokens as they arrive
            - Normal items: token strings
            - Final item (if return_metadata=True): ('metadata', metadata_dict) with billing info
            For other services: Raises ValueError (streaming not supported)
            
        Examples:
            # Simple streaming
            async for token in client.invoke_stream("Hello!", "chat", "text"):
                print(token, end='', flush=True)
            
            # Streaming with metadata
            async for item in client.invoke_stream("Hello!", "chat", "text", return_metadata=True):
                if isinstance(item, tuple) and item[0] == 'metadata':
                    print(f"\nBilling: {item[1]['billing']}")
                else:
                    print(item, end='', flush=True)
        """
        try:
            # Only text services support streaming
            if service_type != "text":
                raise ValueError(f"Streaming not supported for service type: {service_type}")
            
            # Tools are supported with streaming
            
            # Step 1: Select best model for this task
            selected_model = await self._select_model(
                input_data=input_data,
                task=task, 
                service_type=service_type,
                model_hint=model,
                provider_hint=provider
            )
            
            # Step 2: Get appropriate service
            service = await self._get_service(
                service_type=service_type,
                model_name=selected_model["model_id"],
                provider=selected_model["provider"],
                task=task,
                use_cache=False  # Don't cache for streaming to avoid state issues
            )
            
            # Step 3: Ensure service supports streaming
            if not hasattr(service, 'astream'):
                raise ValueError(f"Service {selected_model['provider']}/{selected_model['model_id']} does not support streaming")
            
            # Step 4: Enable streaming on the service
            if hasattr(service, 'streaming'):
                service.streaming = True
            
            # Step 5: Stream tokens and collect for billing
            content_chunks = []
            async for token in service.astream(input_data):
                content_chunks.append(token)
                yield token
            
            # Step 6: After streaming is complete, calculate billing info and optionally return metadata
            try:
                await asyncio.sleep(0.01)  # Small delay to ensure billing tracking completes
                
                # Get billing info (similar to _invoke_service)
                billing_info = self._get_billing_info(service, selected_model["model_id"])
                
                # Log billing info for tracking
                logger.info(f"Streaming completed - Model: {selected_model['model_id']}, "
                           f"Tokens: {billing_info.get('total_tokens', 'N/A')}, "
                           f"Cost: ${billing_info.get('cost_usd', 0):.4f}")
                
                # Return metadata if requested
                if return_metadata:
                    metadata = {
                        "model_used": selected_model["model_id"],
                        "provider": selected_model["provider"], 
                        "task": task,
                        "service_type": service_type,
                        "selection_reason": selected_model.get("reason", "Default selection"),
                        "billing": billing_info,
                        "streaming": True,
                        "tokens_streamed": len(content_chunks),
                        "content_length": len("".join(content_chunks))
                    }
                    yield ('metadata', metadata)
                
            except Exception as billing_error:
                logger.warning(f"Failed to track billing for streaming: {billing_error}")
                if return_metadata:
                    # Return fallback metadata even if billing fails
                    fallback_metadata = {
                        "model_used": selected_model["model_id"],
                        "provider": selected_model["provider"], 
                        "task": task,
                        "service_type": service_type,
                        "selection_reason": selected_model.get("reason", "Default selection"),
                        "billing": {
                            "cost_usd": 0.0,
                            "error": str(billing_error),
                            "currency": "USD"
                        },
                        "streaming": True,
                        "tokens_streamed": len(content_chunks),
                        "content_length": len("".join(content_chunks))
                    }
                    yield ('metadata', fallback_metadata)
                
        except Exception as e:
            logger.error(f"Streaming invoke failed: {e}")
            raise
    
    async def _select_model(
        self,
        input_data: Any,
        task: str,
        service_type: str, 
        model_hint: Optional[str] = None,
        provider_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """Select the best model for the given task"""
        
        # If explicit hints provided, use them
        if model_hint and provider_hint:
            return {
                "model_id": model_hint,
                "provider": provider_hint, 
                "reason": "User specified"
            }
        
        # If model_hint provided but no provider_hint, handle special cases
        if model_hint:
            # Special handling for hybrid service
            if model_hint == "hybrid":
                return {
                    "model_id": model_hint,
                    "provider": "hybrid",
                    "reason": "Hybrid service requested"
                }
            # If only model_hint provided, use default provider for that service type
            elif provider_hint is None:
                default_provider = self._get_default_provider(service_type)
                return {
                    "model_id": model_hint,
                    "provider": default_provider,
                    "reason": "Model specified with default provider"
                }
        
        # Use intelligent model selector if available
        if INTELLIGENT_SELECTOR_AVAILABLE and get_model_selector:
            try:
                # Initialize model selector if not already done
                if self.model_selector is None:
                    self.model_selector = await get_model_selector(self.config)
                
                # Create selection request
                request = f"{task} for {service_type}"
                if isinstance(input_data, (str, Path)):
                    request += f" with input: {str(input_data)[:100]}"
                
                selection = await self.model_selector.select_model(
                    request=request,
                    service_type=service_type,
                    context={
                        "task": task,
                        "input_type": type(input_data).__name__,
                        "provider_hint": provider_hint,
                        "model_hint": model_hint
                    }
                )
                
                if selection["success"]:
                    return {
                        "model_id": selection["selected_model"]["model_id"],
                        "provider": selection["selected_model"]["provider"],
                        "reason": selection["selection_reason"]
                    }
                
            except Exception as e:
                logger.warning(f"Intelligent selection failed: {e}, using defaults")
        
        # Fallback to default model selection
        return self._get_default_model(service_type, task, provider_hint)
    
    def _get_default_provider(self, service_type: str) -> str:
        """Get default provider for service type"""
        defaults = {
            "vision": "openai",
            "audio": "openai", 
            "text": "openai",
            "image": "replicate",
            "embedding": "openai"
        }
        return defaults.get(service_type, "openai")
    
    def _get_default_model(
        self, 
        service_type: str, 
        task: str,
        provider_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get default model for service type and task"""
        
        defaults = {
            "vision": {
                "model_id": "gpt-4.1-nano",
                "provider": "openai"
            },
            "audio": {
                "tts": {"model_id": "tts-1", "provider": "openai"},
                "stt": {"model_id": "whisper-1", "provider": "openai"},
                "default": {"model_id": "whisper-1", "provider": "openai"}
            },
            "text": {
                "model_id": "gpt-4.1-nano", 
                "provider": "openai"
            },
            "image": {
                "model_id": "black-forest-labs/flux-schnell",
                "provider": "replicate"
            },
            "embedding": {
                "embed": {"model_id": "text-embedding-3-small", "provider": "openai"},
                "rerank": {"model_id": "isa-jina-reranker-v2-service", "provider": "isa"},
                "default": {"model_id": "text-embedding-3-small", "provider": "openai"}
            }
        }
        
        # Handle audio service type with task-specific models
        if service_type == "audio":
            if "speech" in task or "tts" in task:
                default = defaults["audio"]["tts"]
            elif "transcribe" in task or "stt" in task:
                default = defaults["audio"]["stt"] 
            else:
                default = defaults["audio"]["default"]
        # Handle embedding service type with task-specific models
        elif service_type == "embedding":
            if "rerank" in task:
                default = defaults["embedding"]["rerank"]
            elif "embed" in task:
                default = defaults["embedding"]["embed"]
            else:
                default = defaults["embedding"]["default"]
        else:
            default = defaults.get(service_type, defaults["vision"])
        
        # Apply provider hint if provided
        if provider_hint:
            default = dict(default)
            default["provider"] = provider_hint
        
        return {
            **default,
            "reason": "Default selection"
        }
    
    async def _get_service(
        self,
        service_type: str,
        model_name: str,
        provider: str,
        task: str,
        use_cache: bool = True
    ) -> Any:
        """Get appropriate service instance"""
        
        cache_key = f"{service_type}_{provider}_{model_name}"
        
        # Check cache first (if caching is enabled)
        if use_cache and cache_key in self._service_cache:
            return self._service_cache[cache_key]
        
        try:
            # Validate service type
            self._validate_service_type(service_type)
            
            # Route to appropriate AIFactory method
            if service_type == "vision":
                service = self.ai_factory.get_vision(model_name, provider)
            elif service_type == "audio":
                if "speech" in task or "tts" in task:
                    service = self.ai_factory.get_tts(model_name, provider)
                elif "transcribe" in task or "stt" in task:
                    service = self.ai_factory.get_stt(model_name, provider)
                else:
                    service = self.ai_factory.get_stt(model_name, provider)
            elif service_type == "text":
                service = self.ai_factory.get_llm(model_name, provider)
            elif service_type == "image":
                service = self.ai_factory.get_img("t2i", model_name, provider)
            elif service_type == "embedding":
                service = self.ai_factory.get_embed(model_name, provider)
            
            # Cache the service (if caching is enabled)
            if use_cache:
                self._service_cache[cache_key] = service
            return service
            
        except Exception as e:
            logger.error(f"Failed to get service {service_type}/{provider}/{model_name}: {e}")
            raise
    
    def _validate_service_type(self, service_type: str) -> None:
        """Validate service type is supported"""
        if service_type not in self.SUPPORTED_SERVICE_TYPES:
            raise ValueError(f"Unsupported service type: {service_type}")
    
    def _map_task(self, task: str, service_type: str) -> str:
        """Map common task names to unified task names"""
        task_mapping = self.TASK_MAPPINGS.get(service_type, {})
        return task_mapping.get(task, task)
    
    async def _execute_task(
        self,
        service: Any,
        input_data: Any,
        task: str,
        service_type: str,
        **kwargs
    ) -> Any:
        """Execute the task using the appropriate service"""
        
        try:
            self._validate_service_type(service_type)
            unified_task = self._map_task(task, service_type)
            
            if service_type == "vision":
                return await service.invoke(
                    image=input_data,
                    task=unified_task,
                    **kwargs
                )
            
            elif service_type == "audio":
                if unified_task in ["synthesize", "text_to_speech", "tts"]:
                    return await service.invoke(
                        text=input_data,
                        task=unified_task,
                        **kwargs
                    )
                else:
                    return await service.invoke(
                        audio_input=input_data,
                        task=unified_task,
                        **kwargs
                    )
            
            elif service_type == "text":
                # Extract show_reasoning from kwargs if present
                show_reasoning = kwargs.pop('show_reasoning', False)
                result = await service.invoke(
                    input_data=input_data,
                    task=unified_task,
                    show_reasoning=show_reasoning,
                    **kwargs
                )
                
                logger.debug(f"Service result type: {type(result)}")
                logger.debug(f"Service result: {result}")
                
                if isinstance(result, dict) and 'message' in result:
                    message = result['message']
                    logger.debug(f"Extracted message type: {type(message)}")
                    logger.debug(f"Extracted message: {message}")
                    return message
                else:
                    return result
            
            elif service_type == "image":
                return await service.invoke(
                    prompt=input_data,
                    task=unified_task,
                    **kwargs
                )
            
            elif service_type == "embedding":
                return await service.invoke(
                    input_data=input_data,
                    task=unified_task,
                    **kwargs
                )
                
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            raise
    
    
    def clear_cache(self):
        """Clear service cache"""
        self._service_cache.clear()
        logger.info("Service cache cleared")
    
    async def get_available_models(self, service_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available models
        
        Args:
            service_type: Optional filter by service type
            
        Returns:
            List of available models with metadata
        """
        if INTELLIGENT_SELECTOR_AVAILABLE and get_model_selector:
            try:
                if self.model_selector is None:
                    self.model_selector = await get_model_selector(self.config)
                return await self.model_selector.get_available_models(service_type)
            except Exception as e:
                logger.error(f"Failed to get available models: {e}")
                return []
        else:
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of client and underlying services
        
        Returns:
            Health status dictionary
        """
        try:
            health_status = {
                "client": "healthy",
                "ai_factory": "healthy" if self.ai_factory else "unavailable",
                "model_selector": "healthy" if self.model_selector else "unavailable",
                "services": {}
            }
            
            # Check a few key services
            test_services = [
                ("vision", "openai", "gpt-4.1-mini"),
                ("audio", "openai", "whisper-1"),
                ("text", "openai", "gpt-4.1-mini")
            ]
            
            for service_type, provider, model in test_services:
                try:
                    await self._get_service(service_type, model, provider, "test")
                    health_status["services"][f"{service_type}_{provider}"] = "healthy"
                except Exception as e:
                    health_status["services"][f"{service_type}_{provider}"] = f"error: {str(e)}"
            
            return health_status
            
        except Exception as e:
            return {
                "client": "error",
                "error": str(e)
            }
    
    def _handle_error(self, e: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle errors consistently across methods"""
        error_msg = f"Failed to {context.get('operation', 'execute')} {context.get('task', '')} on {context.get('service_type', '')}: {e}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": str(e),
            "metadata": context
        }
    
    async def _invoke_service_streaming(
        self,
        input_data: Union[str, bytes, Path, Dict[str, Any], List[Any]],
        task: str,
        service_type: str,
        model_hint: Optional[str] = None,
        provider_hint: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Service invoke that returns streaming response with async generator"""
        try:
            # Step 1: Select best model for this task
            selected_model = await self._select_model(
                input_data=input_data,
                task=task, 
                service_type=service_type,
                model_hint=model_hint,
                provider_hint=provider_hint
            )
            
            # Step 2: Get appropriate service
            service = await self._get_service(
                service_type=service_type,
                model_name=selected_model["model_id"],
                provider=selected_model["provider"],
                task=task,
                use_cache=False  # Don't cache for streaming to avoid state issues
            )
            
            # Step 3: Handle tools for LLM services (bind tools if provided)
            tools = kwargs.pop("tools", None)
            if service_type == "text" and tools:
                service = await self._get_service(
                    service_type=service_type,
                    model_name=selected_model["model_id"],
                    provider=selected_model["provider"],
                    task=task,
                    use_cache=False
                )
                service = service.bind_tools(tools)
            
            # Step 4: Ensure service supports streaming
            if not hasattr(service, 'astream'):
                raise ValueError(f"Service {selected_model['provider']}/{selected_model['model_id']} does not support streaming")
            
            # Step 5: Enable streaming on the service
            if hasattr(service, 'streaming'):
                service.streaming = True
            
            # Step 6: Create async generator wrapper that yields tokens
            async def stream_generator():
                # Pass show_reasoning parameter if available for LLM services
                if service_type == "text" and hasattr(service, 'astream'):
                    show_reasoning = kwargs.get('show_reasoning', False)
                    logger.debug(f"Stream generator: show_reasoning={show_reasoning}")
                    if 'show_reasoning' in kwargs:
                        async for token in service.astream(input_data, show_reasoning=show_reasoning):
                            yield token
                    else:
                        async for token in service.astream(input_data):
                            yield token
                else:
                    async for token in service.astream(input_data):
                        yield token
            
            # Return response with stream generator and metadata
            return {
                "success": True,
                "stream": stream_generator(),
                "metadata": {
                    "model_used": selected_model["model_id"],
                    "provider": selected_model["provider"], 
                    "task": task,
                    "service_type": service_type,
                    "selection_reason": selected_model.get("reason", "Default selection"),
                    "streaming": True
                }
            }
        except Exception as e:
            logger.error(f"Streaming service invoke failed: {e}")
            raise

    async def _invoke_service(
        self,
        input_data: Union[str, bytes, Path, Dict[str, Any], List[Any]],
        task: str,
        service_type: str,
        model_hint: Optional[str] = None,
        provider_hint: Optional[str] = None,
        stream: Optional[bool] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Direct service invoke - passes LangChain objects and tools directly to services"""
        try:
            # Step 1: Select best model for this task
            selected_model = await self._select_model(
                input_data=input_data,
                task=task, 
                service_type=service_type,
                model_hint=model_hint,
                provider_hint=provider_hint
            )
            
            # Step 2: Get appropriate service
            service = await self._get_service(
                service_type=service_type,
                model_name=selected_model["model_id"],
                provider=selected_model["provider"],
                task=task
            )
            
            # Step 3: Handle tools for LLM services (bind tools if provided)
            tools = kwargs.pop("tools", None)
            if service_type == "text" and tools:
                service = await self._get_service(
                    service_type=service_type,
                    model_name=selected_model["model_id"],
                    provider=selected_model["provider"],
                    task=task,
                    use_cache=False
                )
                service = service.bind_tools(tools)
                # Note: streaming is still supported with tools
            
            # Step 4: Set streaming for text services
            if service_type == "text" and stream is not None:
                if hasattr(service, 'streaming'):
                    service.streaming = stream
            
            # Step 5: Execute task with unified interface
            result = await self._execute_task(
                service=service,
                input_data=input_data,
                task=task,
                service_type=service_type,
                **kwargs
            )
            
            # Step 6: Wait for billing tracking to complete, then get billing information
            await asyncio.sleep(0.01)  # Small delay to ensure billing tracking completes
            billing_info = self._get_billing_info(service, selected_model["model_id"])
            
            # Return unified response
            return {
                "success": True,
                "result": result,
                "metadata": {
                    "model_used": selected_model["model_id"],
                    "provider": selected_model["provider"], 
                    "task": task,
                    "service_type": service_type,
                    "selection_reason": selected_model.get("reason", "Default selection"),
                    "billing": billing_info
                }
            }
        except Exception as e:
            logger.error(f"Service invoke failed: {e}")
            raise
    
    def _get_billing_info(self, service: Any, model_id: str) -> Dict[str, Any]:
        """Extract billing information from service after task execution"""
        try:
            # Check if service has model_manager with billing_tracker
            if hasattr(service, 'model_manager') and hasattr(service.model_manager, 'billing_tracker'):
                billing_tracker = service.model_manager.billing_tracker
                
                # Get the latest usage record for this model
                model_records = [
                    record for record in billing_tracker.usage_records
                    if record.model_id == model_id
                ]
                
                if model_records:
                    # Get the most recent record
                    latest_record = max(model_records, key=lambda r: r.timestamp)
                    
                    return {
                        "cost_usd": latest_record.cost_usd,
                        "input_tokens": latest_record.input_tokens,
                        "output_tokens": latest_record.output_tokens,
                        "total_tokens": latest_record.total_tokens,
                        "operation": latest_record.operation,
                        "timestamp": latest_record.timestamp,
                        "currency": "USD"
                    }
            
            # Fallback: no billing info available
            return {
                "cost_usd": 0.0,
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
                "operation": None,
                "timestamp": None,
                "currency": "USD",
                "note": "Billing information not available"
            }
            
        except Exception as e:
            logger.warning(f"Failed to get billing info: {e}")
            return {
                "cost_usd": 0.0,
                "error": str(e),
                "currency": "USD"
            }
    


# Convenience function for quick access
def create_client(
    config: Optional[Dict[str, Any]] = None,
    service_endpoint: Optional[str] = None,
    api_key: Optional[str] = None
) -> ISAModelClient:
    """Create ISA Model Client instance
    
    Args:
        config: Optional configuration
        service_endpoint: Optional service endpoint URL (if None, uses local AI Factory)
        api_key: Optional API key for authentication (can also be set via ISA_API_KEY env var)
        
    Returns:
        ISAModelClient instance
    """
    return ISAModelClient(config=config, service_endpoint=service_endpoint, api_key=api_key)


# Export for easy import
__all__ = ["ISAModelClient", "create_client"]