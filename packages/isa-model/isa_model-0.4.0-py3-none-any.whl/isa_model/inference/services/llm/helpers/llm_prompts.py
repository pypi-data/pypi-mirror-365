#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LLM通用提示词模板和工具函数
提供标准化的提示词模板，用于不同类型的LLM任务
"""

from typing import Dict, List, Optional, Any
import json

class LLMPrompts:
    """LLM提示词模板管理器"""
    
    # ==================== 对话类提示词 ====================
    
    @staticmethod
    def chat_prompt(user_message: str, system_message: Optional[str] = None) -> List[Dict[str, str]]:
        """生成标准对话提示词格式"""
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": user_message})
        return messages
    
    @staticmethod
    def completion_prompt(text: str, instruction: Optional[str] = None) -> str:
        """生成文本补全提示词"""
        if instruction:
            return f"{instruction}\n\n{text}"
        return text
    
    @staticmethod
    def instruct_prompt(task: str, content: str, format_instruction: Optional[str] = None) -> str:
        """生成指令跟随提示词"""
        prompt = f"Task: {task}\n\nContent:\n{content}\n\n"
        if format_instruction:
            prompt += f"Output Format: {format_instruction}\n\n"
        prompt += "Response:"
        return prompt
    
    # ==================== 文本生成类提示词 ====================
    
    @staticmethod
    def rewrite_prompt(text: str, style: Optional[str] = None, tone: Optional[str] = None) -> str:
        """生成文本重写提示词"""
        prompt = f"Please rewrite the following text"
        if style:
            prompt += f" in {style} style"
        if tone:
            prompt += f" with a {tone} tone"
        prompt += f":\n\n{text}\n\nRewritten text:"
        return prompt
    
    @staticmethod
    def summarize_prompt(text: str, max_length: Optional[int] = None, style: Optional[str] = None) -> str:
        """生成文本摘要提示词"""
        prompt = f"Please summarize the following text"
        if max_length:
            prompt += f" in no more than {max_length} words"
        if style:
            prompt += f" in {style} style"
        prompt += f":\n\n{text}\n\nSummary:"
        return prompt
    
    @staticmethod
    def translate_prompt(text: str, target_language: str, source_language: Optional[str] = None) -> str:
        """生成翻译提示词"""
        prompt = f"Please translate the following text"
        if source_language:
            prompt += f" from {source_language}"
        prompt += f" to {target_language}:\n\n{text}\n\nTranslation:"
        return prompt
    
    # ==================== 分析类提示词 ====================
    
    @staticmethod
    def analyze_prompt(text: str, analysis_type: Optional[str] = None) -> str:
        """生成文本分析提示词"""
        if analysis_type:
            prompt = f"Please perform {analysis_type} analysis on the following text:\n\n{text}\n\nAnalysis:"
        else:
            prompt = f"Please analyze the following text:\n\n{text}\n\nAnalysis:"
        return prompt
    
    @staticmethod
    def classify_prompt(text: str, categories: Optional[List[str]] = None) -> str:
        """生成文本分类提示词"""
        prompt = f"Please classify the following text"
        if categories:
            prompt += f" into one of these categories: {', '.join(categories)}"
        prompt += f":\n\n{text}\n\nClassification:"
        return prompt
    
    @staticmethod
    def extract_prompt(text: str, extract_type: Optional[str] = None) -> str:
        """生成信息提取提示词"""
        if extract_type:
            prompt = f"Please extract {extract_type} from the following text:\n\n{text}\n\nExtracted {extract_type}:"
        else:
            prompt = f"Please extract key information from the following text:\n\n{text}\n\nExtracted information:"
        return prompt
    
    @staticmethod
    def sentiment_prompt(text: str) -> str:
        """生成情感分析提示词"""
        return f"Please analyze the sentiment of the following text and classify it as positive, negative, or neutral:\n\n{text}\n\nSentiment:"
    
    # ==================== 编程类提示词 ====================
    
    @staticmethod
    def code_generation_prompt(description: str, language: Optional[str] = None, style: Optional[str] = None) -> str:
        """生成代码生成提示词"""
        prompt = f"Please write code"
        if language:
            prompt += f" in {language}"
        prompt += f" for the following requirement:\n\n{description}\n\n"
        if style:
            prompt += f"Code style: {style}\n\n"
        prompt += "Code:"
        return prompt
    
    @staticmethod
    def code_explanation_prompt(code: str, language: Optional[str] = None) -> str:
        """生成代码解释提示词"""
        prompt = f"Please explain the following"
        if language:
            prompt += f" {language}"
        prompt += f" code:\n\n```{language or ''}\n{code}\n```\n\nExplanation:"
        return prompt
    
    @staticmethod
    def code_debug_prompt(code: str, language: Optional[str] = None, error: Optional[str] = None) -> str:
        """生成代码调试提示词"""
        prompt = f"Please debug the following"
        if language:
            prompt += f" {language}"
        prompt += f" code:\n\n```{language or ''}\n{code}\n```\n\n"
        if error:
            prompt += f"Error message: {error}\n\n"
        prompt += "Fixed code:"
        return prompt
    
    @staticmethod
    def code_refactor_prompt(code: str, language: Optional[str] = None, improvements: Optional[List[str]] = None) -> str:
        """生成代码重构提示词"""
        prompt = f"Please refactor the following"
        if language:
            prompt += f" {language}"
        prompt += f" code"
        if improvements:
            prompt += f" with these improvements: {', '.join(improvements)}"
        prompt += f":\n\n```{language or ''}\n{code}\n```\n\nRefactored code:"
        return prompt
    
    # ==================== 推理类提示词 ====================
    
    @staticmethod
    def reasoning_prompt(question: str, reasoning_type: Optional[str] = None) -> str:
        """生成推理分析提示词"""
        if reasoning_type:
            prompt = f"Please use {reasoning_type} reasoning to answer the following question:\n\n{question}\n\nReasoning and answer:"
        else:
            prompt = f"Please think step by step and answer the following question:\n\n{question}\n\nReasoning and answer:"
        return prompt
    
    @staticmethod
    def problem_solving_prompt(problem: str, problem_type: Optional[str] = None) -> str:
        """生成问题求解提示词"""
        prompt = f"Please solve the following"
        if problem_type:
            prompt += f" {problem_type}"
        prompt += f" problem:\n\n{problem}\n\nSolution:"
        return prompt
    
    @staticmethod
    def planning_prompt(goal: str, plan_type: Optional[str] = None) -> str:
        """生成计划制定提示词"""
        prompt = f"Please create a"
        if plan_type:
            prompt += f" {plan_type}"
        prompt += f" plan for the following goal:\n\n{goal}\n\nPlan:"
        return prompt
    
    # ==================== 工具调用类提示词 ====================
    
    @staticmethod
    def tool_call_prompt(query: str, available_tools: List[Dict[str, Any]]) -> str:
        """生成工具调用提示词"""
        tools_desc = json.dumps(available_tools, indent=2)
        prompt = f"You have access to the following tools:\n\n{tools_desc}\n\n"
        prompt += f"User query: {query}\n\n"
        prompt += "Please use the appropriate tools to answer the query. Respond with tool calls in JSON format."
        return prompt
    
    @staticmethod
    def function_call_prompt(description: str, function_name: str, parameters: Dict[str, Any]) -> str:
        """生成函数调用提示词"""
        params_desc = json.dumps(parameters, indent=2)
        prompt = f"Please call the function '{function_name}' with the following parameters to {description}:\n\n"
        prompt += f"Parameters:\n{params_desc}\n\n"
        prompt += "Function call result:"
        return prompt

class LLMPromptTemplates:
    """预定义的提示词模板"""
    
    # 系统消息模板
    SYSTEM_MESSAGES = {
        "assistant": "You are a helpful AI assistant. Please provide accurate and helpful responses.",
        "code_expert": "You are an expert programmer. Please provide clean, efficient, and well-documented code.",
        "analyst": "You are a data analyst. Please provide detailed and insightful analysis.",
        "writer": "You are a professional writer. Please provide clear, engaging, and well-structured content.",
        "teacher": "You are a patient and knowledgeable teacher. Please explain concepts clearly and provide examples.",
        "translator": "You are a professional translator. Please provide accurate and natural translations."
    }
    
    # 输出格式模板
    OUTPUT_FORMATS = {
        "json": "Please format your response as valid JSON.",
        "markdown": "Please format your response using Markdown syntax.",
        "bullet_points": "Please format your response as bullet points.",
        "numbered_list": "Please format your response as a numbered list.",
        "table": "Please format your response as a table.",
        "code": "Please format your response as code with appropriate syntax highlighting."
    }
    
    # 任务特定模板
    TASK_TEMPLATES = {
        "email": "Please write a professional email with the following content:",
        "report": "Please write a detailed report on the following topic:",
        "proposal": "Please write a project proposal for the following idea:",
        "documentation": "Please write clear documentation for the following:",
        "test_cases": "Please write comprehensive test cases for the following:",
        "user_story": "Please write user stories for the following feature:"
    }

def get_prompt_template(task_type: str, **kwargs) -> str:
    """获取指定任务类型的提示词模板"""
    prompts = LLMPrompts()
    
    if hasattr(prompts, f"{task_type}_prompt"):
        method = getattr(prompts, f"{task_type}_prompt")
        return method(**kwargs)
    else:
        raise ValueError(f"Unsupported task type: {task_type}")

def format_messages(messages: List[Dict[str, str]], system_message: Optional[str] = None) -> List[Dict[str, str]]:
    """格式化消息列表，添加系统消息"""
    formatted = []
    if system_message:
        formatted.append({"role": "system", "content": system_message})
    formatted.extend(messages)
    return formatted

def combine_prompts(prompts: List[str], separator: str = "\n\n") -> str:
    """组合多个提示词"""
    return separator.join(prompts)