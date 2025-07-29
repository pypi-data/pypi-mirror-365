#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LLM工具函数和实用程序
提供LLM服务的通用工具函数，包括文本处理、token计算、响应解析等
"""

import re
import json
import tiktoken
from typing import Dict, List, Optional, Any, Union, Tuple
import logging

logger = logging.getLogger(__name__)

class TokenCounter:
    """Token计数器"""
    
    def __init__(self, model_name: str = "gpt-4"):
        """初始化token计数器"""
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # 如果模型不支持，使用默认编码
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """计算文本的token数量"""
        return len(self.encoding.encode(text))
    
    def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """计算消息列表的总token数量"""
        total_tokens = 0
        for message in messages:
            # 每个消息有固定的开销（role等）
            total_tokens += 4  # 每个消息的基本开销
            for key, value in message.items():
                total_tokens += self.count_tokens(str(value))
        total_tokens += 2  # 对话的基本开销
        return total_tokens
    
    def truncate_text(self, text: str, max_tokens: int) -> str:
        """截断文本以适应token限制"""
        tokens = self.encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text
        
        truncated_tokens = tokens[:max_tokens]
        return self.encoding.decode(truncated_tokens)
    
    def split_text_by_tokens(self, text: str, chunk_size: int, overlap: int = 0) -> List[str]:
        """按token数量分割文本"""
        tokens = self.encoding.encode(text)
        chunks = []
        
        start = 0
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunks.append(self.encoding.decode(chunk_tokens))
            
            if end >= len(tokens):
                break
            
            start = end - overlap
        
        return chunks

class TextProcessor:
    """文本处理工具"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """清理文本，移除多余的空白字符"""
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        # 移除首尾空白
        text = text.strip()
        return text
    
    @staticmethod
    def extract_code_blocks(text: str) -> List[Dict[str, str]]:
        """从文本中提取代码块"""
        code_pattern = r'```(\w+)?\n(.*?)\n```'
        matches = re.findall(code_pattern, text, re.DOTALL)
        
        code_blocks = []
        for language, code in matches:
            code_blocks.append({
                "language": language or "text",
                "code": code.strip()
            })
        
        return code_blocks
    
    @staticmethod
    def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
        """从文本中提取JSON"""
        # 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # 尝试提取JSON代码块
        json_pattern = r'```json\n(.*?)\n```'
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        # 尝试提取花括号内容
        brace_pattern = r'\{.*\}'
        match = re.search(brace_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        
        return None
    
    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """将文本分割为句子"""
        # 简单的句子分割，基于句号、问号、感叹号
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def extract_entities(text: str, entity_types: List[str] = None) -> Dict[str, List[str]]:
        """提取文本中的实体（简单版本）"""
        entities = {}
        
        if not entity_types:
            entity_types = ["email", "url", "phone", "date"]
        
        patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "url": r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "date": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        }
        
        for entity_type in entity_types:
            if entity_type in patterns:
                matches = re.findall(patterns[entity_type], text)
                entities[entity_type] = matches
        
        return entities

class ResponseParser:
    """响应解析器"""
    
    @staticmethod
    def parse_structured_response(response: str, expected_format: str = "json") -> Any:
        """解析结构化响应"""
        if expected_format == "json":
            return TextProcessor.extract_json_from_text(response)
        elif expected_format == "code":
            return TextProcessor.extract_code_blocks(response)
        else:
            return response
    
    @staticmethod
    def parse_classification_response(response: str, categories: List[str]) -> Tuple[str, float]:
        """解析分类响应，返回类别和置信度"""
        response_lower = response.lower()
        
        # 查找匹配的类别
        for category in categories:
            if category.lower() in response_lower:
                # 尝试提取置信度
                confidence_pattern = r'(\d+(?:\.\d+)?)%|confidence[:\s]*(\d+(?:\.\d+)?)'
                match = re.search(confidence_pattern, response_lower)
                confidence = float(match.group(1) or match.group(2)) / 100 if match else 0.8
                return category, confidence
        
        # 如果没有找到匹配的类别，返回最可能的一个
        return categories[0] if categories else "unknown", 0.5
    
    @staticmethod
    def parse_sentiment_response(response: str) -> Tuple[str, float]:
        """解析情感分析响应"""
        response_lower = response.lower()
        
        # 定义情感关键词
        sentiments = {
            "positive": ["positive", "good", "great", "excellent", "happy", "pleased"],
            "negative": ["negative", "bad", "terrible", "awful", "sad", "disappointed"],
            "neutral": ["neutral", "okay", "average", "mixed", "unclear"]
        }
        
        # 查找匹配的情感
        for sentiment, keywords in sentiments.items():
            for keyword in keywords:
                if keyword in response_lower:
                    # 尝试提取置信度
                    confidence_pattern = r'(\d+(?:\.\d+)?)%|confidence[:\s]*(\d+(?:\.\d+)?)'
                    match = re.search(confidence_pattern, response_lower)
                    confidence = float(match.group(1) or match.group(2)) / 100 if match else 0.7
                    return sentiment, confidence
        
        return "neutral", 0.5

class LLMMetrics:
    """
    LLM性能指标计算工具
    
    注意：计费和使用跟踪功能已经统一到BaseService中的_track_usage()方法。
    LLM服务应该使用BaseLLMService中的_track_llm_usage()方法来跟踪使用情况。
    """
    
    @staticmethod  
    def calculate_latency_metrics(start_time: float, end_time: float, token_count: int) -> Dict[str, float]:
        """计算延迟指标"""
        total_time = end_time - start_time
        tokens_per_second = token_count / total_time if total_time > 0 else 0
        
        return {
            "total_time": total_time,
            "tokens_per_second": tokens_per_second,
            "ms_per_token": (total_time * 1000) / token_count if token_count > 0 else 0
        }
    

def validate_model_response(response: Any, expected_type: type = str) -> bool:
    """验证模型响应是否符合预期类型"""
    return isinstance(response, expected_type)

def format_chat_history(messages: List[Dict[str, str]], max_history: int = 10) -> List[Dict[str, str]]:
    """格式化聊天历史，保留最近的消息"""
    if len(messages) <= max_history:
        return messages
    
    # 保留系统消息和最近的消息
    system_messages = [msg for msg in messages if msg.get("role") == "system"]
    other_messages = [msg for msg in messages if msg.get("role") != "system"]
    
    recent_messages = other_messages[-max_history+len(system_messages):]
    return system_messages + recent_messages

def extract_function_calls(response: str) -> List[Dict[str, Any]]:
    """从响应中提取函数调用"""
    function_calls = []
    
    # 查找JSON格式的函数调用
    json_pattern = r'\{[^{}]*"function_name"[^{}]*\}'
    matches = re.findall(json_pattern, response)
    
    for match in matches:
        try:
            call = json.loads(match)
            if "function_name" in call:
                function_calls.append(call)
        except json.JSONDecodeError:
            continue
    
    return function_calls

def merge_streaming_tokens(tokens: List[str]) -> str:
    """合并流式token为完整文本"""
    return ''.join(tokens)

def detect_language(text: str) -> str:
    """检测文本语言（简单版本）"""
    # 简单的语言检测，基于字符模式
    if re.search(r'[\u4e00-\u9fff]', text):
        return "zh"
    elif re.search(r'[а-яё]', text, re.IGNORECASE):
        return "ru"
    elif re.search(r'[ひらがなカタカナ]', text):
        return "ja"
    elif re.search(r'[가-힣]', text):
        return "ko"
    else:
        return "en"