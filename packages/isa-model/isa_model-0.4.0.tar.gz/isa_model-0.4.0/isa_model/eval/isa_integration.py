"""
ISA Model Client Integration for Evaluation Framework.

Provides interfaces between the evaluation framework and ISA Model services.
Supports all ISA services: LLM, Vision, Audio, Embedding, Image Generation.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import base64
from io import BytesIO
from PIL import Image

try:
    from ..client import ISAModelClient
    ISA_CLIENT_AVAILABLE = True
except ImportError:
    ISA_CLIENT_AVAILABLE = False
    logging.warning("ISA Model Client not available. Using mock interface.")

logger = logging.getLogger(__name__)


class ISAModelInterface:
    """
    Interface adapter for ISA Model services in evaluation framework.
    
    Provides unified interfaces for:
    - LLM services (OpenAI, Ollama, YYDS)
    - Vision services (OCR, Table, UI, Document analysis)
    - Audio services (STT, TTS, Emotion, Diarization)
    - Embedding services (Text embedding, Reranking)
    - Image generation services
    """
    
    def __init__(self, service_config: Optional[Dict[str, Any]] = None):
        """
        Initialize ISA Model interface.
        
        Args:
            service_config: Configuration for ISA services
        """
        self.config = service_config or {}
        
        if ISA_CLIENT_AVAILABLE:
            self.client = ISAModelClient()
        else:
            self.client = None
            logger.warning("ISA Model Client not available, using mock client")
        
        # Performance tracking
        self.request_count = 0
        self.total_latency = 0.0
        self.error_count = 0
    
    async def llm_completion(self, 
                           prompt: str, 
                           model_name: str = "gpt-4.1-nano",
                           provider: str = "openai",
                           **kwargs) -> Dict[str, Any]:
        """
        Generate text completion using ISA LLM services.
        
        Args:
            prompt: Input text prompt
            model_name: Model name (e.g., gpt-4.1-nano, llama3.2:3b-instruct-fp16)
            provider: Provider (openai, ollama, yyds)
            **kwargs: Additional parameters
            
        Returns:
            LLM completion result
        """
        start_time = time.time()
        self.request_count += 1
        
        try:
            if self.client:
                # Use real ISA client
                result = await self.client.invoke(
                    input_data=prompt,
                    task="generate",
                    service_type="text",
                    provider=provider,
                    model_name=model_name,
                    **kwargs
                )
                
                # Extract text from result
                if isinstance(result, dict):
                    text = result.get("result", str(result))
                else:
                    text = str(result)
                
                completion_result = {
                    "text": text,
                    "model": model_name,
                    "provider": provider,
                    "latency": time.time() - start_time,
                    "tokens_used": self._estimate_tokens(prompt + text),
                    "cost_usd": self._estimate_cost(prompt + text, provider)
                }
                
            else:
                # Mock response
                completion_result = {
                    "text": f"Mock response for: {prompt[:50]}...",
                    "model": model_name,
                    "provider": provider,
                    "latency": 0.5,
                    "tokens_used": len(prompt.split()) + 10,
                    "cost_usd": 0.001
                }
            
            self.total_latency += completion_result["latency"]
            return completion_result
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"LLM completion error: {e}")
            raise
    
    async def vision_analysis(self, 
                            image: Union[str, bytes, Image.Image, Path],
                            prompt: str = "",
                            task_type: str = "ocr",
                            model_name: str = "gpt-4.1-mini",
                            **kwargs) -> Dict[str, Any]:
        """
        Analyze image using ISA Vision services.
        
        Args:
            image: Image data (path, bytes, PIL Image, or base64)
            prompt: Analysis prompt
            task_type: Vision task (ocr, table, ui, document, caption)
            model_name: Vision model name
            **kwargs: Additional parameters
            
        Returns:
            Vision analysis result
        """
        start_time = time.time()
        self.request_count += 1
        
        try:
            # Convert image to format expected by ISA client
            image_data = self._prepare_image_data(image)
            
            if self.client:
                # Map task types to ISA service calls
                if task_type == "ocr":
                    result = await self.client.invoke(
                        input_data=image_data,
                        task="extract_text",
                        service_type="vision",
                        model_name="isa-surya-ocr-service",
                        **kwargs
                    )
                elif task_type == "table":
                    result = await self.client.invoke(
                        input_data=image_data,
                        task="extract_table",
                        service_type="vision", 
                        model_name="isa_vision_table",
                        **kwargs
                    )
                elif task_type == "ui":
                    result = await self.client.invoke(
                        input_data=image_data,
                        task="detect_ui",
                        service_type="vision",
                        model_name="isa-omniparser-ui-detection",
                        **kwargs
                    )
                else:
                    # Generic vision analysis
                    result = await self.client.invoke(
                        input_data={"image": image_data, "prompt": prompt},
                        task="analyze",
                        service_type="vision",
                        model_name=model_name,
                        **kwargs
                    )
                
                # Extract text from result
                if isinstance(result, dict):
                    text = result.get("result", result.get("text", str(result)))
                else:
                    text = str(result)
                
                vision_result = {
                    "text": text,
                    "task_type": task_type,
                    "model": model_name,
                    "latency": time.time() - start_time,
                    "cost_usd": self._estimate_vision_cost(task_type)
                }
                
            else:
                # Mock response
                vision_result = {
                    "text": f"Mock {task_type} result for image analysis",
                    "task_type": task_type,
                    "model": model_name,
                    "latency": 1.0,
                    "cost_usd": 0.01
                }
            
            self.total_latency += vision_result["latency"]
            return vision_result
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Vision analysis error: {e}")
            raise
    
    async def audio_processing(self,
                             audio: Union[str, bytes, Path],
                             task_type: str = "stt",
                             model_name: str = "whisper-1",
                             **kwargs) -> Dict[str, Any]:
        """
        Process audio using ISA Audio services.
        
        Args:
            audio: Audio data (path, bytes)
            task_type: Audio task (stt, tts, emotion, diarization)
            model_name: Audio model name
            **kwargs: Additional parameters
            
        Returns:
            Audio processing result
        """
        start_time = time.time()
        self.request_count += 1
        
        try:
            # Prepare audio data
            audio_data = self._prepare_audio_data(audio)
            
            if self.client:
                if task_type == "stt":
                    result = await self.client.invoke(
                        input_data=audio_data,
                        task="transcribe",
                        service_type="audio",
                        model_name="isa_audio_sota_service" if "isa" in model_name else model_name,
                        **kwargs
                    )
                elif task_type == "emotion":
                    result = await self.client.invoke(
                        input_data=audio_data,
                        task="detect_emotion",
                        service_type="audio",
                        model_name="isa_audio_sota_service",
                        **kwargs
                    )
                elif task_type == "diarization":
                    result = await self.client.invoke(
                        input_data=audio_data,
                        task="diarize_speakers",
                        service_type="audio", 
                        model_name="isa_audio_sota_service",
                        **kwargs
                    )
                else:
                    # Generic audio processing
                    result = await self.client.invoke(
                        input_data=audio_data,
                        task=task_type,
                        service_type="audio",
                        model_name=model_name,
                        **kwargs
                    )
                
                # Extract result
                if isinstance(result, dict):
                    if task_type == "stt":
                        text = result.get("result", result.get("text", str(result)))
                    else:
                        text = result
                else:
                    text = str(result)
                
                audio_result = {
                    "result": text,
                    "task_type": task_type,
                    "model": model_name,
                    "latency": time.time() - start_time,
                    "cost_usd": self._estimate_audio_cost(task_type)
                }
                
            else:
                # Mock response
                audio_result = {
                    "result": f"Mock {task_type} result for audio processing",
                    "task_type": task_type,
                    "model": model_name,
                    "latency": 2.0,
                    "cost_usd": 0.005
                }
            
            self.total_latency += audio_result["latency"]
            return audio_result
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Audio processing error: {e}")
            raise
    
    async def embedding_generation(self,
                                 text: str,
                                 model_name: str = "text-embedding-3-small",
                                 **kwargs) -> Dict[str, Any]:
        """
        Generate embeddings using ISA Embedding services.
        
        Args:
            text: Input text
            model_name: Embedding model name
            **kwargs: Additional parameters
            
        Returns:
            Embedding result
        """
        start_time = time.time()
        self.request_count += 1
        
        try:
            if self.client:
                result = await self.client.invoke(
                    input_data=text,
                    task="embed",
                    service_type="embedding",
                    model_name=model_name,
                    **kwargs
                )
                
                # Extract embedding vector
                if isinstance(result, dict):
                    embedding = result.get("result", result.get("embedding", []))
                else:
                    embedding = result if isinstance(result, list) else []
                
                embedding_result = {
                    "embedding": embedding,
                    "model": model_name,
                    "dimension": len(embedding) if embedding else 0,
                    "latency": time.time() - start_time,
                    "cost_usd": self._estimate_embedding_cost(text)
                }
                
            else:
                # Mock embedding (1536 dimensions like OpenAI)
                import numpy as np
                embedding = np.random.randn(1536).tolist()
                
                embedding_result = {
                    "embedding": embedding,
                    "model": model_name,
                    "dimension": 1536,
                    "latency": 0.3,
                    "cost_usd": 0.0001
                }
            
            self.total_latency += embedding_result["latency"]
            return embedding_result
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Embedding generation error: {e}")
            raise
    
    async def reranking(self,
                       query: str,
                       documents: List[str],
                       model_name: str = "isa-jina-reranker-v2-service",
                       **kwargs) -> Dict[str, Any]:
        """
        Rerank documents using ISA Reranking services.
        
        Args:
            query: Search query
            documents: List of documents to rerank
            model_name: Reranking model name
            **kwargs: Additional parameters
            
        Returns:
            Reranking result
        """
        start_time = time.time()
        self.request_count += 1
        
        try:
            if self.client:
                result = await self.client.invoke(
                    input_data={
                        "query": query,
                        "documents": documents
                    },
                    task="rerank",
                    service_type="embedding",
                    model_name=model_name,
                    **kwargs
                )
                
                # Extract reranked results
                if isinstance(result, dict):
                    reranked = result.get("result", result.get("rankings", []))
                else:
                    reranked = result if isinstance(result, list) else []
                
                reranking_result = {
                    "rankings": reranked,
                    "model": model_name,
                    "query": query,
                    "num_documents": len(documents),
                    "latency": time.time() - start_time,
                    "cost_usd": self._estimate_reranking_cost(len(documents))
                }
                
            else:
                # Mock reranking (random shuffle)
                import random
                indices = list(range(len(documents)))
                random.shuffle(indices)
                
                reranking_result = {
                    "rankings": [{"index": i, "score": random.random()} for i in indices],
                    "model": model_name,
                    "query": query,
                    "num_documents": len(documents),
                    "latency": 0.5,
                    "cost_usd": 0.001
                }
            
            self.total_latency += reranking_result["latency"]
            return reranking_result
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Reranking error: {e}")
            raise
    
    def _prepare_image_data(self, image: Union[str, bytes, Image.Image, Path]) -> str:
        """Convert image to base64 string for ISA client."""
        try:
            if isinstance(image, str):
                if image.startswith("data:"):
                    return image  # Already base64 data URL
                elif Path(image).exists():
                    # File path
                    with open(image, "rb") as f:
                        image_bytes = f.read()
                else:
                    # Assume base64 string
                    return f"data:image/jpeg;base64,{image}"
            
            elif isinstance(image, bytes):
                image_bytes = image
            
            elif isinstance(image, Path):
                with open(image, "rb") as f:
                    image_bytes = f.read()
            
            elif isinstance(image, Image.Image):
                buffer = BytesIO()
                image.save(buffer, format="PNG")
                image_bytes = buffer.getvalue()
            
            else:
                raise ValueError(f"Unsupported image type: {type(image)}")
            
            # Convert to base64 data URL
            base64_str = base64.b64encode(image_bytes).decode()
            return f"data:image/jpeg;base64,{base64_str}"
            
        except Exception as e:
            logger.error(f"Error preparing image data: {e}")
            raise
    
    def _prepare_audio_data(self, audio: Union[str, bytes, Path]) -> str:
        """Convert audio to format for ISA client."""
        try:
            if isinstance(audio, (str, Path)):
                # Return file path for ISA client
                return str(audio)
            elif isinstance(audio, bytes):
                # Save to temporary file
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                    tmp_file.write(audio)
                    return tmp_file.name
            else:
                raise ValueError(f"Unsupported audio type: {type(audio)}")
                
        except Exception as e:
            logger.error(f"Error preparing audio data: {e}")
            raise
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)."""
        return len(text.split()) * 1.3  # Rough estimate
    
    def _estimate_cost(self, text: str, provider: str) -> float:
        """Estimate API cost."""
        tokens = self._estimate_tokens(text)
        
        # Rough cost estimates (per 1k tokens)
        cost_per_1k = {
            "openai": 0.002,  # GPT-4 turbo
            "ollama": 0.0,    # Local model
            "yyds": 0.01      # Claude
        }
        
        return (tokens / 1000) * cost_per_1k.get(provider, 0.001)
    
    def _estimate_vision_cost(self, task_type: str) -> float:
        """Estimate vision processing cost."""
        costs = {
            "ocr": 0.01,
            "table": 0.02,
            "ui": 0.015,
            "document": 0.03,
            "caption": 0.02
        }
        return costs.get(task_type, 0.01)
    
    def _estimate_audio_cost(self, task_type: str) -> float:
        """Estimate audio processing cost."""
        costs = {
            "stt": 0.006,     # Whisper pricing
            "tts": 0.015,
            "emotion": 0.01,
            "diarization": 0.02
        }
        return costs.get(task_type, 0.01)
    
    def _estimate_embedding_cost(self, text: str) -> float:
        """Estimate embedding cost."""
        tokens = self._estimate_tokens(text)
        return (tokens / 1000) * 0.0001  # text-embedding-3-small pricing
    
    def _estimate_reranking_cost(self, num_docs: int) -> float:
        """Estimate reranking cost."""
        return num_docs * 0.0001  # Rough estimate per document
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        avg_latency = self.total_latency / self.request_count if self.request_count > 0 else 0
        
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0,
            "avg_latency_seconds": avg_latency,
            "total_latency_seconds": self.total_latency,
            "success_rate": 1 - (self.error_count / self.request_count) if self.request_count > 0 else 0
        }


# Convenience functions for creating service interfaces
def create_llm_interface(config: Optional[Dict[str, Any]] = None) -> ISAModelInterface:
    """Create LLM service interface."""
    return ISAModelInterface(config)


def create_vision_interface(config: Optional[Dict[str, Any]] = None) -> ISAModelInterface:
    """Create Vision service interface."""
    return ISAModelInterface(config)


def create_audio_interface(config: Optional[Dict[str, Any]] = None) -> ISAModelInterface:
    """Create Audio service interface.""" 
    return ISAModelInterface(config)


def create_embedding_interface(config: Optional[Dict[str, Any]] = None) -> ISAModelInterface:
    """Create Embedding service interface."""
    return ISAModelInterface(config)