from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional, AsyncGenerator, Callable
import logging

from isa_model.inference.services.base_service import BaseService
from isa_model.inference.services.llm.helpers.llm_adapter import AdapterManager

logger = logging.getLogger(__name__)

class BaseLLMService(BaseService):
    """Base class for Large Language Model services with unified task dispatch"""
    
    def __init__(self, provider_name: str, model_name: str, **kwargs):
        super().__init__(provider_name, model_name, **kwargs)
        self._bound_tools: List[Any] = []
        self._tool_mappings: Dict[str, tuple] = {}
        
        # 初始化适配器管理器
        self.adapter_manager = AdapterManager()
        
        # Get config from provider
        provider_config = self.get_provider_config()
        self.streaming = provider_config.get("streaming", False)
        self.max_tokens = provider_config.get("max_tokens", 4096)
        self.temperature = provider_config.get("temperature", 0.7)
    
    async def invoke(
        self, 
        input_data: Union[str, List[Dict[str, str]], Any],
        task: Optional[str] = None,
        show_reasoning: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        统一的任务分发方法 - Base类提供通用实现
        
        Args:
            input_data: 输入数据，可以是:
                - str: 简单文本提示
                - list: 消息历史 [{"role": "user", "content": "hello"}]
                - Any: LangChain 消息对象或其他格式
            task: 任务类型，支持多种LLM任务
            **kwargs: 任务特定的附加参数
            
        Returns:
            Dict containing task results
        """
        task = task or "chat"
        
        # ==================== 对话类任务 ====================
        if task == "chat":
            return await self.chat(input_data, kwargs.get("max_tokens", self.max_tokens), show_reasoning=show_reasoning)
        elif task == "complete":
            return await self.complete_text(input_data, kwargs.get("max_tokens", self.max_tokens))
        elif task == "instruct":
            return await self.instruct(input_data, kwargs.get("instruction"), kwargs.get("max_tokens", self.max_tokens))
        
        # ==================== 文本生成类任务 ====================
        elif task == "generate":
            return await self.generate_text(input_data, kwargs.get("max_tokens", self.max_tokens))
        elif task == "rewrite":
            return await self.rewrite_text(input_data, kwargs.get("style"), kwargs.get("tone"))
        elif task == "summarize":
            return await self.summarize_text(input_data, kwargs.get("max_length"), kwargs.get("style"))
        elif task == "translate":
            target_language = kwargs.get("target_language")
            if not target_language:
                raise ValueError("target_language is required for translate task")
            return await self.translate_text(input_data, target_language, kwargs.get("source_language"))
        
        # ==================== 分析类任务 ====================
        elif task == "analyze":
            return await self.analyze_text(input_data, kwargs.get("analysis_type"))
        elif task == "classify":
            return await self.classify_text(input_data, kwargs.get("categories"))
        elif task == "extract":
            return await self.extract_information(input_data, kwargs.get("extract_type"))
        elif task == "sentiment":
            return await self.analyze_sentiment(input_data)
        
        # ==================== 编程类任务 ====================
        elif task == "code":
            return await self.generate_code(input_data, kwargs.get("language"), kwargs.get("style"))
        elif task == "explain_code":
            return await self.explain_code(input_data, kwargs.get("language"))
        elif task == "debug_code":
            return await self.debug_code(input_data, kwargs.get("language"))
        elif task == "refactor_code":
            return await self.refactor_code(input_data, kwargs.get("language"), kwargs.get("improvements"))
        
        # ==================== 推理类任务 ====================
        elif task == "reason":
            return await self.reason_about(input_data, kwargs.get("reasoning_type"))
        elif task == "solve":
            return await self.solve_problem(input_data, kwargs.get("problem_type"))
        elif task == "plan":
            return await self.create_plan(input_data, kwargs.get("plan_type"))
        elif task == "deep_research":
            return await self.deep_research(input_data, kwargs.get("research_type"), kwargs.get("search_enabled", True))
        
        # ==================== 工具调用类任务 ====================
        elif task == "tool_call":
            return await self.call_tools(input_data, kwargs.get("available_tools"))
        elif task == "function_call":
            function_name = kwargs.get("function_name")
            if not function_name:
                raise ValueError("function_name is required for function_call task")
            return await self.call_function(input_data, function_name, kwargs.get("parameters"))
        
        else:
            raise NotImplementedError(f"{self.__class__.__name__} does not support task: {task}")
    
    # ==================== 对话类方法 ====================
    
    async def chat(
        self,
        input_data: Union[str, List[Dict[str, str]], Any],
        max_tokens: Optional[int] = None,
        show_reasoning: bool = False
    ) -> Dict[str, Any]:
        """
        对话聊天 - Provider必须实现
        
        Args:
            input_data: 输入消息
            max_tokens: 最大生成token数
            show_reasoning: 是否显示推理过程
            
        Returns:
            Dict containing chat response
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support chat task")
    
    # ==================== 文本生成类方法 ====================
    
    async def complete_text(
        self,
        input_data: Union[str, Any],
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        文本补全 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support complete_text task")
    
    async def instruct(
        self,
        input_data: Union[str, Any],
        instruction: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        指令跟随 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support instruct task")
    
    async def generate_text(
        self,
        input_data: Union[str, Any],
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        通用文本生成 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support generate_text task")
    
    async def rewrite_text(
        self,
        input_data: Union[str, Any],
        style: Optional[str] = None,
        tone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        文本重写 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support rewrite_text task")
    
    async def summarize_text(
        self,
        input_data: Union[str, Any],
        max_length: Optional[int] = None,
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        文本摘要 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support summarize_text task")
    
    async def translate_text(
        self,
        input_data: Union[str, Any],
        target_language: str,
        source_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        文本翻译 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support translate_text task")
    
    # ==================== 分析类方法 ====================
    
    async def analyze_text(
        self,
        input_data: Union[str, Any],
        analysis_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        文本分析 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support analyze_text task")
    
    async def classify_text(
        self,
        input_data: Union[str, Any],
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        文本分类 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support classify_text task")
    
    async def extract_information(
        self,
        input_data: Union[str, Any],
        extract_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        信息提取 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support extract_information task")
    
    async def analyze_sentiment(
        self,
        input_data: Union[str, Any]
    ) -> Dict[str, Any]:
        """
        情感分析 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support analyze_sentiment task")
    
    # ==================== 编程类方法 ====================
    
    async def generate_code(
        self,
        input_data: Union[str, Any],
        language: Optional[str] = None,
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        代码生成 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support generate_code task")
    
    async def explain_code(
        self,
        input_data: Union[str, Any],
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        代码解释 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support explain_code task")
    
    async def debug_code(
        self,
        input_data: Union[str, Any],
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        代码调试 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support debug_code task")
    
    async def refactor_code(
        self,
        input_data: Union[str, Any],
        language: Optional[str] = None,
        improvements: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        代码重构 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support refactor_code task")
    
    # ==================== 推理类方法 ====================
    
    async def reason_about(
        self,
        input_data: Union[str, Any],
        reasoning_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        推理分析 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support reason_about task")
    
    async def solve_problem(
        self,
        input_data: Union[str, Any],
        problem_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        问题求解 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support solve_problem task")
    
    async def create_plan(
        self,
        input_data: Union[str, Any],
        plan_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        计划制定 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support create_plan task")
    
    async def deep_research(
        self,
        input_data: Union[str, Any],
        research_type: Optional[str] = None,
        search_enabled: bool = True
    ) -> Dict[str, Any]:
        """
        深度研究 - O-series模型专用任务，支持网络搜索和深入分析
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support deep_research task")
    
    # ==================== 工具调用类方法 ====================
    
    async def call_tools(
        self,
        input_data: Union[str, Any],
        available_tools: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """
        工具调用 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support call_tools task")
    
    async def call_function(
        self,
        input_data: Union[str, Any],
        function_name: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        函数调用 - Provider可选实现
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support call_function task")
    
    # ==================== 工具绑定和管理 ====================
    
    def bind_tools(self, tools: List[Any], **kwargs) -> 'BaseLLMService':
        """
        Bind tools to this LLM service for function calling
        
        Args:
            tools: List of tools to bind (functions, LangChain tools, etc.)
            **kwargs: Additional tool binding parameters
            
        Returns:
            Self for method chaining
        """
        self._bound_tools = tools
        return self
    
    async def _prepare_tools_for_request(self) -> List[Dict[str, Any]]:
        """准备工具用于请求"""
        if not self._bound_tools:
            return []
        
        schemas, self._tool_mappings = await self.adapter_manager.convert_tools_to_schemas(self._bound_tools)
        return schemas
    
    def _prepare_messages(self, input_data: Union[str, List[Dict[str, str]], Any]) -> List[Dict[str, str]]:
        """使用适配器管理器转换消息格式"""
        return self.adapter_manager.convert_messages(input_data)
    
    def _format_response(self, response: Union[str, Any], original_input: Any) -> Union[str, Any]:
        """使用适配器管理器格式化响应"""
        return self.adapter_manager.format_response(response, original_input)
    
    async def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """使用适配器管理器执行工具调用"""
        return await self.adapter_manager.execute_tool(tool_name, arguments, self._tool_mappings)
    
    @abstractmethod
    async def astream(self, input_data: Union[str, List[Dict[str, str]], Any]) -> AsyncGenerator[str, None]:
        """
        True streaming method that yields tokens one by one as they arrive
        
        Args:
            input_data: Can be:
                - str: Simple text prompt
                - list: Message history like [{"role": "user", "content": "hello"}]
                - Any: LangChain message objects or other formats
            
        Yields:
            Individual tokens as they arrive from the model
        """
        pass
    
    @abstractmethod
    async def ainvoke(self, input_data: Union[str, List[Dict[str, str]], Any], show_reasoning: bool = False) -> Union[str, Any]:
        """
        Universal async invocation method that handles different input types
        
        Args:
            input_data: Can be:
                - str: Simple text prompt
                - list: Message history like [{"role": "user", "content": "hello"}]
                - Any: LangChain message objects or other formats
            show_reasoning: If True and model supports it, show reasoning process
            
        Returns:
            Model response (string for simple cases, object for complex cases)
        """
        pass
    
    def stream(self, input_data: Union[str, List[Dict[str, str]], Any]):
        """
        Synchronous wrapper for astream - returns the async generator
        
        Args:
            input_data: Same as astream
            
        Returns:
            AsyncGenerator that yields tokens
            
        Usage:
            async for token in llm.stream("Hello"):
                print(token, end="", flush=True)
        """
        return self.astream(input_data)
    
    
    def _has_bound_tools(self) -> bool:
        """Check if this service has bound tools"""
        return bool(self._bound_tools)
    
    def _get_bound_tools(self) -> List[Any]:
        """Get the bound tools"""
        return self._bound_tools
    
    @abstractmethod
    def get_token_usage(self) -> Dict[str, Any]:
        """Get cumulative token usage statistics"""
        pass
    
    @abstractmethod
    def get_last_token_usage(self) -> Dict[str, int]:
        """Get token usage from the last request"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        pass
    
    @abstractmethod
    async def close(self):
        """Cleanup resources and close connections"""
        pass
    
    def get_last_usage_with_cost(self) -> Dict[str, Any]:
        """Get last request usage with cost information"""
        usage = self.get_last_token_usage()
        
        # Calculate cost using centralized pricing manager
        cost = self.model_manager.calculate_cost(
            provider=self.provider_name,
            model_name=self.model_name,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0)
        )
        
        return {
            **usage,
            "cost_usd": cost,
            "model": self.model_name,
            "provider": self.provider_name
        }
    
    async def _track_llm_usage(
        self,
        operation: str,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Track LLM usage using the unified BaseService billing system
        
        Returns:
            Cost in USD
        """
        from isa_model.core.types import ServiceType
        
        await self._track_usage(
            service_type=ServiceType.LLM,
            operation=operation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            metadata=metadata
        )
        
        # Return calculated cost
        if input_tokens is not None and output_tokens is not None:
            return self.model_manager.calculate_cost(
                provider=self.provider_name,
                model_name=self.model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
        return 0.0
    
    # ==================== METADATA AND UTILITY METHODS ====================
    
    def get_supported_tasks(self) -> List[str]:
        """
        获取provider支持的任务列表
        
        Returns:
            List of supported task names
        """
        supported = []
        
        # 检查各类任务支持情况
        method_task_map = {
            # 对话类
            'chat': 'chat',
            'complete_text': 'complete',
            'instruct': 'instruct',
            # 文本生成类
            'generate_text': 'generate',
            'rewrite_text': 'rewrite',
            'summarize_text': 'summarize',
            'translate_text': 'translate',
            # 分析类
            'analyze_text': 'analyze',
            'classify_text': 'classify',
            'extract_information': 'extract',
            'analyze_sentiment': 'sentiment',
            # 编程类
            'generate_code': 'code',
            'explain_code': 'explain_code',
            'debug_code': 'debug_code',
            'refactor_code': 'refactor_code',
            # 推理类
            'reason_about': 'reason',
            'solve_problem': 'solve',
            'create_plan': 'plan',
            'deep_research': 'deep_research',
            # 工具调用类
            'call_tools': 'tool_call',
            'call_function': 'function_call'
        }
        
        for method_name, task_name in method_task_map.items():
            if hasattr(self, method_name):
                # 检查是否是默认实现还是provider自己的实现
                try:
                    import inspect
                    source = inspect.getsource(getattr(self, method_name))
                    if 'NotImplementedError' not in source:
                        supported.append(task_name)
                except:
                    # 如果无法检查源码，假设支持
                    supported.append(task_name)
                    
        return supported
    
    def get_supported_languages(self) -> List[str]:
        """
        获取支持的编程语言列表 - Provider应该实现
        
        Returns:
            List of supported programming languages
        """
        return [
            'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 
            'go', 'rust', 'php', 'ruby', 'swift', 'kotlin', 'scala',
            'r', 'matlab', 'sql', 'html', 'css', 'bash', 'powershell'
        ]  # 通用语言支持
    
    def get_max_context_length(self) -> int:
        """
        获取最大上下文长度 - Provider应该实现
        
        Returns:
            Maximum context length in tokens
        """
        return self.max_tokens or 4096  # 默认值
    
    def get_supported_formats(self) -> List[str]:
        """
        获取支持的输入格式 - Provider应该实现
        
        Returns:
            List of supported input formats
        """
        return ['text', 'json', 'markdown', 'code']  # 通用格式
    
    def supports_streaming(self) -> bool:
        """
        检查是否支持流式输出
        
        Returns:
            True if streaming is supported
        """
        return self.streaming
    
    def supports_function_calling(self) -> bool:
        """
        检查是否支持函数调用
        
        Returns:
            True if function calling is supported
        """
        return hasattr(self, 'call_tools') or hasattr(self, 'call_function')
    
    def get_temperature_range(self) -> Dict[str, float]:
        """
        获取温度参数范围
        
        Returns:
            Dict with min and max temperature values
        """
        return {"min": 0.0, "max": 2.0, "default": self.temperature}
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        获取provider信息
        
        Returns:
            Dict containing provider information
        """
        return {
            "provider": self.provider_name,
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "streaming": self.streaming,
            "supports_tools": self.supports_function_calling(),
            "supported_tasks": self.get_supported_tasks(),
            "supported_languages": self.get_supported_languages(),
            "max_context_length": self.get_max_context_length()
        }
