"""
Unified API Route - Single endpoint for all AI services

This is the main API that handles all types of AI requests:
- Vision tasks (image analysis, OCR, UI detection)
- Text tasks (chat, generation, translation) 
- Audio tasks (TTS, STT)
- Image generation tasks
- Embedding tasks
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union, List, AsyncGenerator
import logging
from ..middleware.auth import optional_auth, require_read_access
from ..middleware.security import rate_limit_standard, rate_limit_heavy, sanitize_input
import asyncio
import json
import time
from pathlib import Path

from isa_model.client import ISAModelClient

logger = logging.getLogger(__name__)
router = APIRouter()

class UnifiedRequest(BaseModel):
    """
    **统一请求模型 - 支持所有AI服务类型**
    
    这个模型为所有AI服务（文本、视觉、音频、图像生成、嵌入）提供统一的请求接口。
    
    **支持的服务类型**:
    - `text`: 文本服务 (聊天、生成、翻译)
    - `vision`: 视觉服务 (图像分析、OCR、UI检测)
    - `audio`: 音频服务 (TTS、STT、转录)
    - `image`: 图像生成服务 (文本生成图像、图像转换)
    - `embedding`: 嵌入服务 (文本向量化、相似度计算)
    
    **请求示例**:
    ```json
    {
        "input_data": "你好，世界！",
        "task": "chat",
        "service_type": "text",
        "model": "gpt-4o-mini",
        "provider": "openai"
    }
    ```
    """
    input_data: Union[str, Dict[str, Any]] = Field(
        ..., 
        description="输入数据，支持多种格式：文本字符串、LangChain消息列表、图像URL/路径、音频文件路径等。根据service_type确定具体格式。",
        examples=["你好，世界！", "https://example.com/image.jpg", "/path/to/audio.mp3"]
    )
    task: str = Field(
        ..., 
        description="要执行的任务类型。常见任务：chat(聊天)、analyze_image(图像分析)、generate_speech(语音生成)、create_embedding(创建嵌入)等。",
        examples=["chat", "analyze_image", "generate_speech", "transcribe", "generate_image", "create_embedding"]
    )
    service_type: str = Field(
        ..., 
        description="服务类型，决定使用哪种AI服务。可选值：text、vision、audio、image、embedding。",
        examples=["text", "vision", "audio", "image", "embedding"]
    )
    model: Optional[str] = Field(
        None, 
        description="可选的模型指定。如果指定，系统将尝试使用该模型。常见模型：gpt-4o-mini、gpt-4o、whisper-1、flux-schnell等。",
        examples=["gpt-4o-mini", "gpt-4o", "whisper-1", "tts-1", "flux-schnell", "text-embedding-3-small"]
    )
    provider: Optional[str] = Field(
        None, 
        description="可选的服务提供商指定。如果指定，系统将尝试使用该提供商。常见提供商：openai、replicate、anthropic等。",
        examples=["openai", "replicate", "anthropic"]
    )
    stream: Optional[bool] = Field(
        None, 
        description="是否启用流式响应。仅适用于文本服务。text+chat任务默认启用流式。当使用工具调用时会自动禁用流式响应以确保完整性。"
    )
    tools: Optional[List[Dict[str, Any]]] = Field(
        None, 
        description="可选的工具列表，用于函数调用功能。仅适用于文本服务。工具格式遵循LangChain工具规范。使用工具时会自动禁用流式响应。",
        examples=[[
            {
                "name": "get_weather",
                "description": "获取天气信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "城市名称"}
                    },
                    "required": ["location"]
                }
            }
        ]]
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="额外的任务参数，用于精细控制服务行为。参数内容根据具体服务类型而定，如temperature、max_tokens、voice等。",
        examples=[{"temperature": 0.7, "max_tokens": 1000}, {"voice": "alloy", "speed": 1.0}, {"width": 1024, "height": 1024}]
    )

class UnifiedResponse(BaseModel):
    """
    **统一响应模型 - 所有AI服务的标准响应格式**
    
    提供一致的成功/失败状态、结果数据和元数据信息。
    
    **成功响应示例**:
    ```json
    {
        "success": true,
        "result": {
            "content": "你好！我是AI助手。",
            "tool_calls": [],
            "response_metadata": {
                "token_usage": {
                    "prompt_tokens": 15,
                    "completion_tokens": 10,
                    "total_tokens": 25
                }
            }
        },
        "error": null,
        "metadata": {
            "model_used": "gpt-4o-mini",
            "provider": "openai",
            "task": "chat",
            "service_type": "text",
            "processing_time": 1.23
        }
    }
    ```
    
    **错误响应示例**:
    ```json
    {
        "success": false,
        "result": null,
        "error": "Model 'invalid-model' not found",
        "metadata": {
            "error_code": "MODEL_NOT_FOUND",
            "task": "chat",
            "service_type": "text"
        }
    }
    ```
    """
    success: bool = Field(
        ..., 
        description="请求是否成功执行。true表示成功，false表示失败。"
    )
    result: Optional[Any] = Field(
        None, 
        description="服务执行结果。成功时包含实际数据，失败时为null。数据类型根据服务类型而定：文本服务返回AIMessage对象，视觉服务返回分析文本，音频服务返回文件路径或文本，图像服务返回图像URL，嵌入服务返回向量数组。"
    )
    error: Optional[str] = Field(
        None, 
        description="错误信息描述。成功时为null，失败时包含详细的错误说明。"
    )
    metadata: Dict[str, Any] = Field(
        ..., 
        description="响应元数据，包含执行信息如使用的模型、提供商、处理时间、token使用量等。元数据内容根据服务类型和执行情况而定。"
    )

# Global ISA client instance for server-side processing
_isa_client = None

def get_isa_client():
    """Get or create ISA client for service processing"""
    global _isa_client
    if _isa_client is None:
        _isa_client = ISAModelClient()  # Use direct service mode
    return _isa_client

@router.get("/")
async def unified_info():
    """API information"""
    return {
        "service": "unified_api",
        "status": "active",
        "description": "Single endpoint for all AI services",
        "supported_service_types": ["vision", "text", "audio", "image", "embedding"],
        "version": "1.0.0"
    }

@router.post("/invoke")
@rate_limit_standard()
async def unified_invoke(request: Request, user: Dict = Depends(require_read_access)):
    """
    **Unified API endpoint for all AI services**
    
    Supports both JSON and multipart/form-data requests:
    - JSON: Standard API request with UnifiedRequest body
    - Form: File upload with form parameters
    
    This single endpoint handles:
    - Vision: image analysis, OCR, UI detection
    - Text: chat, generation, translation
    - Audio: TTS, STT, transcription
    - Image: generation, img2img
    - Embedding: text embedding, similarity
    
    **Uses ISAModelClient in local mode - all the complex logic is in client.py**
    """
    try:
        # Get ISA client instance (service mode)
        client = get_isa_client()
        
        # Check content type to determine request format
        content_type = request.headers.get("content-type", "")
        
        if content_type.startswith("multipart/form-data"):
            # Handle form data with file upload
            form = await request.form()
            
            # Extract required fields
            task = form.get("task")
            service_type = form.get("service_type")
            model = form.get("model")
            provider = form.get("provider")
            parameters = form.get("parameters")
            file = form.get("file")
            
            if not task or not service_type:
                raise HTTPException(status_code=400, detail="task and service_type are required")
            
            if file is None:
                raise HTTPException(status_code=400, detail="file is required for multipart requests")
            
            # Read file data
            file_data = await file.read()
            
            # Parse parameters if provided as JSON string
            parsed_params = {}
            if parameters:
                try:
                    parsed_params = json.loads(parameters)
                except json.JSONDecodeError:
                    parsed_params = {}
            
            result = await client._invoke_service(
                input_data=file_data,
                task=task,
                service_type=service_type,
                model_hint=model,
                provider_hint=provider,
                filename=file.filename,
                content_type=file.content_type,
                file_size=len(file_data),
                **parsed_params
            )
            
            # Return the result in our API format
            return UnifiedResponse(
                success=result["success"],
                result=result.get("result"),
                error=result.get("error"),
                metadata={
                    **result["metadata"],
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "file_size": len(file_data)
                }
            )
        
        else:
            # Handle JSON request
            try:
                json_body = await request.json()
                unified_request = UnifiedRequest(**json_body)
                
                # Sanitize string inputs to prevent XSS and injection attacks
                if isinstance(unified_request.input_data, str):
                    unified_request.input_data = sanitize_input(unified_request.input_data)
                
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON request: {e}")
            
            # Prepare parameters, ensuring tools isn't duplicated
            params = dict(unified_request.parameters) if unified_request.parameters else {}
            if unified_request.tools:
                params.pop("tools", None)  # Remove tools from parameters if present
                params["tools"] = unified_request.tools
            
            # Check if this should be a streaming response
            # Default to streaming for text+chat unless explicitly disabled
            is_text_chat = (unified_request.service_type == "text" and unified_request.task == "chat")
            stream_setting = unified_request.stream if unified_request.stream is not None else is_text_chat
            
            should_stream = (
                is_text_chat and 
                not unified_request.tools and  # No tools
                stream_setting  # Stream enabled by default for text+chat or explicitly
            )
            
            
            if should_stream:
                # Return streaming response for text chat
                async def generate_stream():
                    try:
                        # Use streaming invoke but track metadata manually
                        collected_tokens = []
                        selected_model = None
                        service_info = None
                        start_time = time.time()
                        
                        # Get model selection info first (lightweight operation)
                        try:
                            selected_model = await client._select_model(
                                input_data=unified_request.input_data,
                                task=unified_request.task,
                                service_type=unified_request.service_type,
                                model_hint=unified_request.model,
                                provider_hint=unified_request.provider
                            )
                            service_info = {
                                "model_used": selected_model["model_id"],
                                "provider": selected_model["provider"],
                                "task": unified_request.task,
                                "service_type": unified_request.service_type,
                                "selection_reason": selected_model.get("reason", "Default selection"),
                                "streaming": True
                            }
                        except Exception:
                            pass
                        
                        # Stream the tokens and get metadata
                        processing_time = 0
                        async for item in client.invoke_stream(
                            input_data=unified_request.input_data,
                            task=unified_request.task,
                            service_type=unified_request.service_type,
                            model=unified_request.model,
                            provider=unified_request.provider,
                            return_metadata=True,  # Request metadata with billing info
                            **params
                        ):
                            if isinstance(item, tuple) and item[0] == 'metadata':
                                # This is the final metadata with billing info
                                metadata = item[1]
                                processing_time = time.time() - start_time
                                metadata["processing_time"] = processing_time
                                yield f"data: {json.dumps({'metadata': metadata})}\n\n"
                            else:
                                # This is a token
                                collected_tokens.append(item)
                                yield f"data: {json.dumps({'token': item})}\n\n"
                        
                    except Exception as e:
                        # Send error as final event
                        yield f"data: {json.dumps({'error': str(e)})}\n\n"
                    finally:
                        # Send end-of-stream marker
                        yield f"data: {json.dumps({'done': True})}\n\n"
                
                return StreamingResponse(
                    generate_stream(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "X-Accel-Buffering": "no"  # Disable nginx buffering
                    }
                )
            else:
                # Non-streaming response (original behavior)
                result = await client._invoke_service(
                    input_data=unified_request.input_data,
                    task=unified_request.task,
                    service_type=unified_request.service_type,
                    model_hint=unified_request.model,
                    provider_hint=unified_request.provider,
                    **params
                )
                
                # Return the result in our API format
                return UnifiedResponse(
                    success=result["success"],
                    result=result.get("result"),
                    error=result.get("error"),
                    metadata=result["metadata"]
                )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unified invoke failed: {e}")
        return UnifiedResponse(
            success=False,
            error=str(e),
            metadata={}
        )



@router.get("/models")
async def get_available_models(service_type: Optional[str] = None):
    """Get available models (optional filter by service type)"""
    try:
        client = get_isa_client()
        return await client.get_available_models(service_type)
    except Exception as e:
        logger.error(f"Failed to get available models: {e}")
        # Fallback static model list
        return {
            "models": [
                {"service_type": "vision", "provider": "openai", "model_id": "gpt-4.1-mini"},
                {"service_type": "text", "provider": "openai", "model_id": "gpt-4.1-mini"},
                {"service_type": "audio", "provider": "openai", "model_id": "whisper-1"},
                {"service_type": "audio", "provider": "openai", "model_id": "tts-1"},
                {"service_type": "embedding", "provider": "openai", "model_id": "text-embedding-3-small"},
                {"service_type": "image", "provider": "replicate", "model_id": "black-forest-labs/flux-schnell"}
            ]
        }

@router.get("/health")
async def health_check():
    """Health check for unified API"""
    try:
        client = get_isa_client()
        health_result = await client.health_check()
        return {
            "api": "healthy",
            "client_health": health_result
        }
    except Exception as e:
        return {
            "api": "error",
            "error": str(e)
        }