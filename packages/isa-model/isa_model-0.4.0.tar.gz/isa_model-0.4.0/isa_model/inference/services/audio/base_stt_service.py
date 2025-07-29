from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional, BinaryIO
from isa_model.inference.services.base_service import BaseService

class BaseSTTService(BaseService):
    """Base class for Speech-to-Text services with unified task dispatch"""
    
    async def invoke(
        self, 
        audio_input: Union[str, BinaryIO, List[Union[str, BinaryIO]]],
        task: Optional[str] = None,
        **kwargs
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        统一的任务分发方法 - Base类提供通用实现
        
        Args:
            audio_input: 音频输入，可以是:
                - str: 音频文件路径
                - BinaryIO: 音频文件对象
                - List: 多个音频文件（批量处理）
            task: 任务类型，支持多种STT任务
            **kwargs: 任务特定的附加参数
            
        Returns:
            Dict or List[Dict] containing task results
        """
        task = task or "transcribe"
        
        # ==================== 语音转文本类任务 ====================
        if task == "transcribe":
            if isinstance(audio_input, list):
                return await self.transcribe_batch(
                    audio_input,
                    kwargs.get("language"),
                    kwargs.get("prompt")
                )
            else:
                return await self.transcribe(
                    audio_input,
                    kwargs.get("language"),
                    kwargs.get("prompt")
                )
        elif task == "translate":
            if isinstance(audio_input, list):
                raise ValueError("translate task requires single audio input")
            return await self.translate(audio_input)
        elif task == "batch_transcribe":
            if not isinstance(audio_input, list):
                audio_input = [audio_input]
            return await self.transcribe_batch(
                audio_input,
                kwargs.get("language"),
                kwargs.get("prompt")
            )
        elif task == "detect_language":
            if isinstance(audio_input, list):
                raise ValueError("detect_language task requires single audio input")
            return await self.detect_language(audio_input)
        else:
            raise NotImplementedError(f"{self.__class__.__name__} does not support task: {task}")
    
    def get_supported_tasks(self) -> List[str]:
        """
        获取支持的任务列表
        
        Returns:
            List of supported task names
        """
        return ["transcribe", "translate", "batch_transcribe", "detect_language"]
    
    @abstractmethod
    async def transcribe(
        self, 
        audio_file: Union[str, BinaryIO], 
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text
        
        Args:
            audio_file: Path to audio file or file-like object
            language: Language code (e.g., 'en', 'es', 'fr')
            prompt: Optional prompt to guide transcription
            
        Returns:
            Dict containing transcription results with keys:
            - text: The transcribed text
            - language: Detected/specified language
            - confidence: Confidence score (if available)
            - segments: Time-segmented transcription (if available)
        """
        pass
    
    @abstractmethod
    async def translate(
        self, 
        audio_file: Union[str, BinaryIO]
    ) -> Dict[str, Any]:
        """
        Translate audio file to English text
        
        Args:
            audio_file: Path to audio file or file-like object
            
        Returns:
            Dict containing translation results with keys:
            - text: The translated text (in English)
            - detected_language: Original language detected
            - confidence: Confidence score (if available)
        """
        pass
    
    @abstractmethod
    async def transcribe_batch(
        self, 
        audio_files: List[Union[str, BinaryIO]], 
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Transcribe multiple audio files
        
        Args:
            audio_files: List of audio file paths or file-like objects
            language: Language code (e.g., 'en', 'es', 'fr')
            prompt: Optional prompt to guide transcription
            
        Returns:
            List of transcription results
        """
        pass
    
    @abstractmethod
    async def detect_language(self, audio_file: Union[str, BinaryIO]) -> Dict[str, Any]:
        """
        Detect language of audio file
        
        Args:
            audio_file: Path to audio file or file-like object
            
        Returns:
            Dict containing language detection results with keys:
            - language: Detected language code
            - confidence: Confidence score
            - alternatives: List of alternative languages with scores
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported audio formats
        
        Returns:
            List of supported file extensions (e.g., ['mp3', 'wav', 'flac'])
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported language codes
        
        Returns:
            List of supported language codes (e.g., ['en', 'es', 'fr'])
        """
        pass
    
    @abstractmethod
    async def close(self):
        """Cleanup resources"""
        pass
