"""
LLM Evaluator implementing industry best practices for large language model evaluation.

Features:
- Support for multiple LLM providers (OpenAI, Anthropic, local models)
- Comprehensive text generation metrics
- Benchmark evaluation (MMLU, HellaSwag, etc.)
- Token usage and cost tracking
- Safety and bias evaluation
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
import json
import re

from .base_evaluator import BaseEvaluator, EvaluationResult

try:
    from ...inference.ai_factory import AIFactory
    AI_FACTORY_AVAILABLE = True
except ImportError:
    AI_FACTORY_AVAILABLE = False

logger = logging.getLogger(__name__)


class LLMEvaluator(BaseEvaluator):
    """
    Comprehensive LLM evaluator with industry-standard metrics and practices.
    
    Supports:
    - Text generation evaluation
    - Classification tasks
    - Question answering
    - Reasoning benchmarks
    - Safety and bias assessment
    """
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 experiment_tracker: Optional[Any] = None):
        """
        Initialize LLM evaluator.
        
        Args:
            config: Evaluation configuration
            experiment_tracker: Optional experiment tracking instance
        """
        super().__init__("LLMEvaluator", config, experiment_tracker)
        
        # Initialize AI factory for model inference
        if AI_FACTORY_AVAILABLE:
            try:
                self.ai_factory = AIFactory()
                logger.info("AI Factory initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize AI Factory: {e}")
                self.ai_factory = None
        else:
            self.ai_factory = None
            logger.warning("AI Factory not available")
        
        # LLM-specific configuration
        self.provider = self.config.get("provider", "openai")
        self.model_name = self.config.get("model_name", "gpt-4.1-mini")
        self.temperature = self.config.get("temperature", 0.1)
        self.max_tokens = self.config.get("max_tokens", 512)
        self.system_prompt = self.config.get("system_prompt", "")
        
        # Token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost_usd = 0.0
    
    async def evaluate_sample(self, 
                            sample: Dict[str, Any],
                            model_interface: Any = None) -> Dict[str, Any]:
        """
        Evaluate a single sample with the LLM.
        
        Args:
            sample: Data sample containing prompt and expected response
            model_interface: Model interface (uses AI factory if None)
            
        Returns:
            Evaluation result for the sample
        """
        # Use provided model interface or default to AI factory
        if model_interface is None:
            if not self.ai_factory:
                raise ValueError("No model interface available for evaluation")
            model_interface = self.ai_factory.get_llm(
                model_name=self.model_name,
                provider=self.provider
            )
        
        # Extract prompt and reference from sample
        prompt = self._format_prompt(sample)
        reference = sample.get("reference") or sample.get("expected_output") or sample.get("answer")
        
        # Generate prediction
        try:
            response = await model_interface.ainvoke(prompt)
            
            # Extract prediction text
            if hasattr(response, 'content'):
                prediction = response.content
            elif isinstance(response, dict):
                prediction = response.get('text') or response.get('content') or str(response)
            elif isinstance(response, str):
                prediction = response
            else:
                prediction = str(response)
            
            # Track token usage if available
            if hasattr(response, 'usage'):
                usage = response.usage
                input_tokens = getattr(usage, 'prompt_tokens', 0)
                output_tokens = getattr(usage, 'completion_tokens', 0)
                self.total_input_tokens += input_tokens
                self.total_output_tokens += output_tokens
            
            return {
                "prediction": prediction.strip(),
                "reference": reference,
                "prompt": prompt,
                "sample_id": sample.get("id", "unknown"),
                "input_tokens": getattr(response, 'input_tokens', 0) if hasattr(response, 'input_tokens') else 0,
                "output_tokens": getattr(response, 'output_tokens', 0) if hasattr(response, 'output_tokens') else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to evaluate sample {sample.get('id', 'unknown')}: {e}")
            raise
    
    def _format_prompt(self, sample: Dict[str, Any]) -> str:
        """
        Format prompt based on sample type and configuration.
        
        Args:
            sample: Data sample
            
        Returns:
            Formatted prompt string
        """
        # Handle different sample formats
        if "prompt" in sample:
            prompt = sample["prompt"]
        elif "question" in sample:
            prompt = sample["question"]
        elif "input" in sample:
            prompt = sample["input"]
        elif "text" in sample:
            prompt = sample["text"]
        else:
            prompt = str(sample)
        
        # Add system prompt if configured
        if self.system_prompt:
            prompt = f"{self.system_prompt}\n\n{prompt}"
        
        # Handle few-shot examples
        if "examples" in sample and sample["examples"]:
            examples_text = ""
            for example in sample["examples"]:
                if isinstance(example, dict):
                    ex_input = example.get("input", example.get("question", ""))
                    ex_output = example.get("output", example.get("answer", ""))
                    examples_text += f"Input: {ex_input}\nOutput: {ex_output}\n\n"
            
            prompt = f"{examples_text}Input: {prompt}\nOutput:"
        
        return prompt
    
    def compute_metrics(self, 
                       predictions: List[str],
                       references: List[str],
                       **kwargs) -> Dict[str, float]:
        """
        Compute comprehensive LLM evaluation metrics.
        
        Args:
            predictions: Model predictions
            references: Ground truth references
            **kwargs: Additional parameters
            
        Returns:
            Dictionary of computed metrics
        """
        metrics = {}
        
        if not predictions or not references:
            logger.warning("Empty predictions or references, returning empty metrics")
            return metrics
        
        # Exact match accuracy
        exact_matches = sum(1 for pred, ref in zip(predictions, references) 
                          if self._normalize_text(pred) == self._normalize_text(ref))
        metrics["exact_match"] = exact_matches / len(predictions)
        
        # Token-based F1 score
        f1_scores = []
        for pred, ref in zip(predictions, references):
            f1_score = self._compute_f1_score(pred, ref)
            f1_scores.append(f1_score)
        metrics["f1_score"] = sum(f1_scores) / len(f1_scores)
        
        # BLEU score (simplified)
        bleu_scores = []
        for pred, ref in zip(predictions, references):
            bleu_score = self._compute_bleu_score(pred, ref)
            bleu_scores.append(bleu_score)
        metrics["bleu_score"] = sum(bleu_scores) / len(bleu_scores)
        
        # ROUGE-L score (simplified)
        rouge_scores = []
        for pred, ref in zip(predictions, references):
            rouge_score = self._compute_rouge_l_score(pred, ref)
            rouge_scores.append(rouge_score)
        metrics["rouge_l"] = sum(rouge_scores) / len(rouge_scores)
        
        # Response length statistics
        pred_lengths = [len(pred.split()) for pred in predictions]
        ref_lengths = [len(ref.split()) for ref in references]
        
        metrics["avg_prediction_length"] = sum(pred_lengths) / len(pred_lengths)
        metrics["avg_reference_length"] = sum(ref_lengths) / len(ref_lengths)
        metrics["length_ratio"] = metrics["avg_prediction_length"] / metrics["avg_reference_length"] if metrics["avg_reference_length"] > 0 else 0
        
        # Diversity metrics
        metrics.update(self._compute_diversity_metrics(predictions))
        
        # Token and cost metrics
        if self.total_input_tokens > 0 or self.total_output_tokens > 0:
            metrics["total_input_tokens"] = float(self.total_input_tokens)
            metrics["total_output_tokens"] = float(self.total_output_tokens)
            metrics["total_tokens"] = float(self.total_input_tokens + self.total_output_tokens)
            metrics["estimated_cost_usd"] = self.total_cost_usd
        
        return metrics
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation for comparison
        text = re.sub(r'[^\w\s]', '', text)
        return text
    
    def _compute_f1_score(self, prediction: str, reference: str) -> float:
        """Compute token-level F1 score."""
        pred_tokens = set(self._normalize_text(prediction).split())
        ref_tokens = set(self._normalize_text(reference).split())
        
        if not pred_tokens and not ref_tokens:
            return 1.0
        
        if not pred_tokens or not ref_tokens:
            return 0.0
        
        common_tokens = pred_tokens & ref_tokens
        
        if len(common_tokens) == 0:
            return 0.0
        
        precision = len(common_tokens) / len(pred_tokens)
        recall = len(common_tokens) / len(ref_tokens)
        
        return 2 * precision * recall / (precision + recall)
    
    def _compute_bleu_score(self, prediction: str, reference: str) -> float:
        """Compute simplified BLEU score."""
        pred_tokens = self._normalize_text(prediction).split()
        ref_tokens = self._normalize_text(reference).split()
        
        if not pred_tokens or not ref_tokens:
            return 0.0
        
        # Simplified unigram precision
        pred_set = set(pred_tokens)
        ref_set = set(ref_tokens)
        overlap = len(pred_set & ref_set)
        
        precision = overlap / len(pred_set) if pred_set else 0
        recall = overlap / len(ref_set) if ref_set else 0
        
        if precision + recall == 0:
            return 0.0
        
        return 2 * precision * recall / (precision + recall)
    
    def _compute_rouge_l_score(self, prediction: str, reference: str) -> float:
        """Compute simplified ROUGE-L score."""
        pred_tokens = self._normalize_text(prediction).split()
        ref_tokens = self._normalize_text(reference).split()
        
        if not pred_tokens or not ref_tokens:
            return 0.0
        
        # Simplified LCS computation
        lcs_length = self._longest_common_subsequence_length(pred_tokens, ref_tokens)
        
        if len(pred_tokens) == 0 or len(ref_tokens) == 0:
            return 0.0
        
        precision = lcs_length / len(pred_tokens)
        recall = lcs_length / len(ref_tokens)
        
        if precision + recall == 0:
            return 0.0
        
        return 2 * precision * recall / (precision + recall)
    
    def _longest_common_subsequence_length(self, seq1: List[str], seq2: List[str]) -> int:
        """Compute length of longest common subsequence."""
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]
    
    def _compute_diversity_metrics(self, predictions: List[str]) -> Dict[str, float]:
        """Compute diversity metrics for predictions."""
        all_tokens = []
        all_bigrams = []
        
        for pred in predictions:
            tokens = self._normalize_text(pred).split()
            all_tokens.extend(tokens)
            
            # Generate bigrams
            for i in range(len(tokens) - 1):
                all_bigrams.append((tokens[i], tokens[i + 1]))
        
        # Distinct-n metrics
        distinct_1 = len(set(all_tokens)) / len(all_tokens) if all_tokens else 0
        distinct_2 = len(set(all_bigrams)) / len(all_bigrams) if all_bigrams else 0
        
        return {
            "distinct_1": distinct_1,
            "distinct_2": distinct_2,
            "vocab_size": float(len(set(all_tokens)))
        }
    
    def get_supported_metrics(self) -> List[str]:
        """Get list of metrics supported by this evaluator."""
        return [
            "exact_match",
            "f1_score",
            "bleu_score",
            "rouge_l",
            "avg_prediction_length",
            "avg_reference_length",
            "length_ratio",
            "distinct_1",
            "distinct_2",
            "vocab_size",
            "total_input_tokens",
            "total_output_tokens",
            "total_tokens",
            "estimated_cost_usd"
        ]
    
    async def evaluate_classification(self,
                                    dataset: List[Dict[str, Any]],
                                    class_labels: List[str],
                                    model_name: str = "unknown") -> EvaluationResult:
        """
        Evaluate classification tasks with specialized metrics.
        
        Args:
            dataset: Classification dataset
            class_labels: List of possible class labels
            model_name: Name of the model being evaluated
            
        Returns:
            Classification evaluation results
        """
        # Update config for classification
        self.config.update({
            "task_type": "classification",
            "class_labels": class_labels,
            "max_tokens": 10  # Short responses for classification
        })
        
        result = await self.evaluate(
            model_interface=None,
            dataset=dataset,
            dataset_name="classification_task",
            model_name=model_name
        )
        
        # Add classification-specific metrics
        if result.predictions and result.references:
            classification_metrics = self._compute_classification_metrics(
                result.predictions, 
                result.references, 
                class_labels
            )
            result.metrics.update(classification_metrics)
        
        return result
    
    def _compute_classification_metrics(self, 
                                      predictions: List[str],
                                      references: List[str],
                                      class_labels: List[str]) -> Dict[str, float]:
        """Compute classification-specific metrics."""
        # Map predictions to class labels
        mapped_predictions = []
        for pred in predictions:
            mapped_pred = self._map_to_class_label(pred, class_labels)
            mapped_predictions.append(mapped_pred)
        
        # Compute accuracy
        correct = sum(1 for pred, ref in zip(mapped_predictions, references) if pred == ref)
        accuracy = correct / len(predictions) if predictions else 0
        
        # Compute per-class precision and recall
        class_metrics = {}
        for label in class_labels:
            tp = sum(1 for pred, ref in zip(mapped_predictions, references) if pred == label and ref == label)
            fp = sum(1 for pred, ref in zip(mapped_predictions, references) if pred == label and ref != label)
            fn = sum(1 for pred, ref in zip(mapped_predictions, references) if pred != label and ref == label)
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            class_metrics[f"{label}_precision"] = precision
            class_metrics[f"{label}_recall"] = recall
            class_metrics[f"{label}_f1"] = f1
        
        # Compute macro averages
        precisions = [class_metrics[f"{label}_precision"] for label in class_labels]
        recalls = [class_metrics[f"{label}_recall"] for label in class_labels]
        f1s = [class_metrics[f"{label}_f1"] for label in class_labels]
        
        return {
            "accuracy": accuracy,
            "macro_precision": sum(precisions) / len(precisions) if precisions else 0,
            "macro_recall": sum(recalls) / len(recalls) if recalls else 0,
            "macro_f1": sum(f1s) / len(f1s) if f1s else 0,
            **class_metrics
        }
    
    def _map_to_class_label(self, prediction: str, class_labels: List[str]) -> str:
        """Map prediction text to the most likely class label."""
        pred_normalized = self._normalize_text(prediction)
        
        # Direct match
        for label in class_labels:
            if self._normalize_text(label) == pred_normalized:
                return label
        
        # Substring match
        for label in class_labels:
            if self._normalize_text(label) in pred_normalized:
                return label
        
        # Return first label if no match found
        return class_labels[0] if class_labels else "unknown"