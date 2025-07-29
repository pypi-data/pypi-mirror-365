"""
Vision Evaluator for ISA Model evaluation framework.

Provides comprehensive evaluation capabilities for vision tasks including:
- OCR (Optical Character Recognition) evaluation
- Table extraction evaluation  
- UI detection evaluation
- Document analysis evaluation
- Image captioning evaluation
- Visual question answering evaluation

Supports ISA custom services and standard vision models.
"""

import asyncio
import logging
import base64
import io
from typing import Dict, List, Any, Optional, Union, Tuple
from PIL import Image
import numpy as np
from pathlib import Path

from .base_evaluator import BaseEvaluator, EvaluationResult
from ..metrics import compute_text_metrics, compute_vision_metrics

logger = logging.getLogger(__name__)


class VisionEvaluator(BaseEvaluator):
    """
    Comprehensive vision model evaluator.
    
    Supports evaluation of:
    - OCR accuracy and multilingual capability
    - Table extraction and structure recognition
    - UI element detection and classification
    - Document understanding and analysis
    - Image captioning quality
    - Visual question answering accuracy
    """
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 experiment_tracker: Optional[Any] = None):
        """
        Initialize the vision evaluator.
        
        Args:
            config: Evaluation configuration
            experiment_tracker: Optional experiment tracking instance
        """
        super().__init__(
            evaluator_name="vision_evaluator",
            config=config,
            experiment_tracker=experiment_tracker
        )
        
        # Vision-specific configuration
        self.supported_formats = self.config.get("supported_formats", ["png", "jpg", "jpeg", "pdf", "webp"])
        self.max_image_size = self.config.get("max_image_size", (2048, 2048))
        self.enable_multilingual = self.config.get("enable_multilingual", True)
        
        # Evaluation task types
        self.task_type = self.config.get("task_type", "ocr")  # ocr, table, ui, vqa, caption
        
        logger.info(f"Initialized VisionEvaluator for task: {self.task_type}")
    
    async def evaluate_sample(self, 
                            sample: Dict[str, Any],
                            model_interface: Any) -> Dict[str, Any]:
        """
        Evaluate a single vision sample.
        
        Args:
            sample: Vision sample containing image and expected output
            model_interface: Vision model interface
            
        Returns:
            Evaluation result for the sample
        """
        try:
            # Extract sample data
            image_data = sample.get("image")
            expected_output = sample.get("expected_output", "")
            task_type = sample.get("task_type", self.task_type)
            prompt = sample.get("prompt", "")
            
            # Process image
            processed_image = await self._process_image(image_data)
            
            # Get model prediction based on task type
            prediction = await self._get_model_prediction(
                model_interface, processed_image, prompt, task_type
            )
            
            # Compute sample-level metrics
            sample_metrics = self._compute_sample_metrics(
                prediction, expected_output, task_type
            )
            
            return {
                "prediction": prediction,
                "expected_output": expected_output,
                "task_type": task_type,
                "sample_metrics": sample_metrics,
                "image_info": self._get_image_info(processed_image)
            }
            
        except Exception as e:
            logger.error(f"Error evaluating vision sample: {e}")
            raise
    
    async def _process_image(self, image_data: Union[str, bytes, Image.Image, Path]) -> Image.Image:
        """
        Process and validate image data.
        
        Args:
            image_data: Image in various formats
            
        Returns:
            Processed PIL Image
        """
        try:
            if isinstance(image_data, str):
                # Handle base64 encoded images or file paths
                if image_data.startswith("data:"):
                    # Base64 data URL
                    header, encoded = image_data.split(",", 1)
                    image_bytes = base64.b64decode(encoded)
                    image = Image.open(io.BytesIO(image_bytes))
                elif Path(image_data).exists():
                    # File path
                    image = Image.open(image_data)
                else:
                    # Assume base64 string
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(io.BytesIO(image_bytes))
            
            elif isinstance(image_data, bytes):
                # Raw bytes
                image = Image.open(io.BytesIO(image_data))
            
            elif isinstance(image_data, Path):
                # Path object
                image = Image.open(image_data)
            
            elif isinstance(image_data, Image.Image):
                # PIL Image
                image = image_data
            
            else:
                raise ValueError(f"Unsupported image data type: {type(image_data)}")
            
            # Convert to RGB if needed
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            # Resize if too large
            if image.size[0] > self.max_image_size[0] or image.size[1] > self.max_image_size[1]:
                image.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)
                logger.info(f"Resized image to {image.size}")
            
            return image
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise
    
    async def _get_model_prediction(self, 
                                  model_interface: Any,
                                  image: Image.Image,
                                  prompt: str,
                                  task_type: str) -> str:
        """
        Get model prediction for vision task.
        
        Args:
            model_interface: Vision model interface
            image: Processed PIL image
            prompt: Task-specific prompt
            task_type: Type of vision task
            
        Returns:
            Model prediction as string
        """
        try:
            # Prepare task-specific prompt
            if not prompt:
                prompt = self._get_default_prompt(task_type)
            
            # Convert image to format expected by model
            if hasattr(model_interface, 'process_image'):
                # ISA custom vision service
                result = await model_interface.process_image(image, prompt, task_type)
                prediction = result.get("text", "") if isinstance(result, dict) else str(result)
            
            elif hasattr(model_interface, 'vision_completion'):
                # OpenAI-style vision API
                # Convert image to base64
                buffer = io.BytesIO()
                image.save(buffer, format="PNG")
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                
                result = await model_interface.vision_completion(
                    prompt=prompt,
                    image_base64=image_base64
                )
                prediction = result.get("content", "") if isinstance(result, dict) else str(result)
            
            else:
                # Generic interface
                prediction = await model_interface.predict(image, prompt)
                prediction = str(prediction)
            
            return prediction.strip()
            
        except Exception as e:
            logger.error(f"Error getting model prediction: {e}")
            raise
    
    def _get_default_prompt(self, task_type: str) -> str:
        """Get default prompt for task type."""
        prompts = {
            "ocr": "Extract all text from this image. Preserve the original formatting and layout.",
            "table": "Extract the table structure and content from this image. Provide the data in a structured format.",
            "ui": "Analyze the UI elements in this image. Identify buttons, text fields, labels, and their relationships.",
            "vqa": "Answer the question about this image accurately and concisely.",
            "caption": "Generate a detailed and accurate caption describing this image.",
            "document": "Analyze this document image and extract the key information, structure, and content."
        }
        return prompts.get(task_type, "Analyze this image and provide relevant information.")
    
    def _compute_sample_metrics(self, 
                              prediction: str,
                              expected_output: str,
                              task_type: str) -> Dict[str, float]:
        """
        Compute metrics for a single sample.
        
        Args:
            prediction: Model prediction
            expected_output: Expected/reference output
            task_type: Type of vision task
            
        Returns:
            Dictionary of sample-level metrics
        """
        try:
            metrics = {}
            
            # Common text-based metrics
            text_metrics = compute_text_metrics(prediction, expected_output)
            metrics.update(text_metrics)
            
            # Task-specific metrics
            if task_type == "ocr":
                metrics.update(self._compute_ocr_metrics(prediction, expected_output))
            elif task_type == "table":
                metrics.update(self._compute_table_metrics(prediction, expected_output))
            elif task_type == "ui":
                metrics.update(self._compute_ui_metrics(prediction, expected_output))
            elif task_type in ["vqa", "caption"]:
                metrics.update(self._compute_semantic_metrics(prediction, expected_output))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error computing sample metrics: {e}")
            return {"error": 1.0}
    
    def _compute_ocr_metrics(self, prediction: str, expected: str) -> Dict[str, float]:
        """Compute OCR-specific metrics."""
        try:
            # Character-level accuracy
            pred_chars = list(prediction.lower().replace(" ", ""))
            exp_chars = list(expected.lower().replace(" ", ""))
            
            char_accuracy = self._compute_sequence_accuracy(pred_chars, exp_chars)
            
            # Word-level accuracy
            pred_words = prediction.lower().split()
            exp_words = expected.lower().split()
            
            word_accuracy = self._compute_sequence_accuracy(pred_words, exp_words)
            
            # Line-level accuracy (for formatted text)
            pred_lines = prediction.strip().split("\n")
            exp_lines = expected.strip().split("\n")
            
            line_accuracy = self._compute_sequence_accuracy(pred_lines, exp_lines)
            
            return {
                "char_accuracy": char_accuracy,
                "word_accuracy": word_accuracy,
                "line_accuracy": line_accuracy,
                "length_ratio": len(prediction) / max(len(expected), 1)
            }
            
        except Exception as e:
            logger.error(f"Error computing OCR metrics: {e}")
            return {"ocr_error": 1.0}
    
    def _compute_table_metrics(self, prediction: str, expected: str) -> Dict[str, float]:
        """Compute table extraction metrics."""
        try:
            # Simple table structure metrics
            pred_rows = prediction.count("\n") + 1
            exp_rows = expected.count("\n") + 1
            
            pred_cells = prediction.count("|") + prediction.count("\t")
            exp_cells = expected.count("|") + expected.count("\t")
            
            row_accuracy = 1.0 - abs(pred_rows - exp_rows) / max(exp_rows, 1)
            cell_count_accuracy = 1.0 - abs(pred_cells - exp_cells) / max(exp_cells, 1)
            
            return {
                "row_accuracy": max(0.0, row_accuracy),
                "cell_count_accuracy": max(0.0, cell_count_accuracy),
                "structure_similarity": (row_accuracy + cell_count_accuracy) / 2
            }
            
        except Exception as e:
            logger.error(f"Error computing table metrics: {e}")
            return {"table_error": 1.0}
    
    def _compute_ui_metrics(self, prediction: str, expected: str) -> Dict[str, float]:
        """Compute UI detection metrics."""
        try:
            # Extract UI elements (simplified approach)
            ui_keywords = ["button", "text", "input", "label", "image", "link", "menu", "icon"]
            
            pred_elements = []
            exp_elements = []
            
            for keyword in ui_keywords:
                pred_count = prediction.lower().count(keyword)
                exp_count = expected.lower().count(keyword)
                pred_elements.extend([keyword] * pred_count)
                exp_elements.extend([keyword] * exp_count)
            
            element_accuracy = self._compute_sequence_accuracy(pred_elements, exp_elements)
            
            return {
                "element_detection_accuracy": element_accuracy,
                "element_count_ratio": len(pred_elements) / max(len(exp_elements), 1)
            }
            
        except Exception as e:
            logger.error(f"Error computing UI metrics: {e}")
            return {"ui_error": 1.0}
    
    def _compute_semantic_metrics(self, prediction: str, expected: str) -> Dict[str, float]:
        """Compute semantic similarity metrics for VQA/captioning."""
        try:
            # Simple semantic metrics
            pred_words = set(prediction.lower().split())
            exp_words = set(expected.lower().split())
            
            if not exp_words:
                return {"semantic_error": 1.0}
            
            intersection = pred_words.intersection(exp_words)
            union = pred_words.union(exp_words)
            
            jaccard_similarity = len(intersection) / len(union) if union else 0.0
            word_overlap = len(intersection) / len(exp_words)
            
            return {
                "jaccard_similarity": jaccard_similarity,
                "word_overlap": word_overlap,
                "semantic_score": (jaccard_similarity + word_overlap) / 2
            }
            
        except Exception as e:
            logger.error(f"Error computing semantic metrics: {e}")
            return {"semantic_error": 1.0}
    
    def _compute_sequence_accuracy(self, pred_seq: List[str], exp_seq: List[str]) -> float:
        """Compute sequence-level accuracy using edit distance."""
        try:
            if not exp_seq:
                return 1.0 if not pred_seq else 0.0
            
            # Simple edit distance computation
            m, n = len(pred_seq), len(exp_seq)
            dp = [[0] * (n + 1) for _ in range(m + 1)]
            
            for i in range(m + 1):
                dp[i][0] = i
            for j in range(n + 1):
                dp[0][j] = j
            
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if pred_seq[i-1] == exp_seq[j-1]:
                        dp[i][j] = dp[i-1][j-1]
                    else:
                        dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
            
            edit_distance = dp[m][n]
            accuracy = 1.0 - edit_distance / max(n, 1)
            return max(0.0, accuracy)
            
        except Exception as e:
            logger.error(f"Error computing sequence accuracy: {e}")
            return 0.0
    
    def _get_image_info(self, image: Image.Image) -> Dict[str, Any]:
        """Get image metadata for analysis."""
        return {
            "width": image.size[0],
            "height": image.size[1],
            "mode": image.mode,
            "format": getattr(image, "format", "unknown"),
            "has_transparency": image.mode in ("RGBA", "LA") or "transparency" in image.info
        }
    
    def compute_metrics(self, 
                       predictions: List[str],
                       references: List[str],
                       **kwargs) -> Dict[str, float]:
        """
        Compute aggregate vision evaluation metrics.
        
        Args:
            predictions: List of model predictions
            references: List of reference outputs
            **kwargs: Additional parameters
            
        Returns:
            Dictionary of computed metrics
        """
        try:
            if not predictions or not references:
                logger.warning("Empty predictions or references provided")
                return {}
            
            # Ensure equal lengths
            min_len = min(len(predictions), len(references))
            predictions = predictions[:min_len]
            references = references[:min_len]
            
            # Compute text-based metrics
            metrics = compute_text_metrics(predictions, references, aggregate=True)
            
            # Compute vision-specific metrics
            vision_metrics = self._compute_vision_aggregate_metrics(predictions, references)
            metrics.update(vision_metrics)
            
            # Add evaluation metadata
            metrics.update({
                "total_samples": len(predictions),
                "task_type": self.task_type,
                "multilingual_enabled": self.enable_multilingual
            })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error computing aggregate metrics: {e}")
            return {"error_rate": 1.0}
    
    def _compute_vision_aggregate_metrics(self, 
                                        predictions: List[str],
                                        references: List[str]) -> Dict[str, float]:
        """Compute aggregate vision-specific metrics."""
        try:
            task_type = self.task_type
            
            if task_type == "ocr":
                return self._compute_aggregate_ocr_metrics(predictions, references)
            elif task_type == "table":
                return self._compute_aggregate_table_metrics(predictions, references)
            elif task_type == "ui":
                return self._compute_aggregate_ui_metrics(predictions, references)
            elif task_type in ["vqa", "caption"]:
                return self._compute_aggregate_semantic_metrics(predictions, references)
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error computing vision aggregate metrics: {e}")
            return {}
    
    def _compute_aggregate_ocr_metrics(self, 
                                     predictions: List[str],
                                     references: List[str]) -> Dict[str, float]:
        """Compute aggregate OCR metrics."""
        char_accuracies = []
        word_accuracies = []
        
        for pred, ref in zip(predictions, references):
            sample_metrics = self._compute_ocr_metrics(pred, ref)
            char_accuracies.append(sample_metrics.get("char_accuracy", 0.0))
            word_accuracies.append(sample_metrics.get("word_accuracy", 0.0))
        
        return {
            "avg_char_accuracy": np.mean(char_accuracies) if char_accuracies else 0.0,
            "avg_word_accuracy": np.mean(word_accuracies) if word_accuracies else 0.0,
            "ocr_score": np.mean(char_accuracies + word_accuracies) if char_accuracies else 0.0
        }
    
    def _compute_aggregate_table_metrics(self, 
                                       predictions: List[str],
                                       references: List[str]) -> Dict[str, float]:
        """Compute aggregate table metrics."""
        structure_similarities = []
        
        for pred, ref in zip(predictions, references):
            sample_metrics = self._compute_table_metrics(pred, ref)
            structure_similarities.append(sample_metrics.get("structure_similarity", 0.0))
        
        return {
            "avg_structure_similarity": np.mean(structure_similarities) if structure_similarities else 0.0,
            "table_extraction_score": np.mean(structure_similarities) if structure_similarities else 0.0
        }
    
    def _compute_aggregate_ui_metrics(self, 
                                    predictions: List[str],
                                    references: List[str]) -> Dict[str, float]:
        """Compute aggregate UI metrics."""
        detection_accuracies = []
        
        for pred, ref in zip(predictions, references):
            sample_metrics = self._compute_ui_metrics(pred, ref)
            detection_accuracies.append(sample_metrics.get("element_detection_accuracy", 0.0))
        
        return {
            "avg_element_detection": np.mean(detection_accuracies) if detection_accuracies else 0.0,
            "ui_detection_score": np.mean(detection_accuracies) if detection_accuracies else 0.0
        }
    
    def _compute_aggregate_semantic_metrics(self, 
                                          predictions: List[str],
                                          references: List[str]) -> Dict[str, float]:
        """Compute aggregate semantic metrics."""
        semantic_scores = []
        
        for pred, ref in zip(predictions, references):
            sample_metrics = self._compute_semantic_metrics(pred, ref)
            semantic_scores.append(sample_metrics.get("semantic_score", 0.0))
        
        return {
            "avg_semantic_similarity": np.mean(semantic_scores) if semantic_scores else 0.0,
            "semantic_understanding_score": np.mean(semantic_scores) if semantic_scores else 0.0
        }
    
    def get_supported_metrics(self) -> List[str]:
        """Get list of metrics supported by this evaluator."""
        base_metrics = [
            "exact_match", "f1_score", "bleu_score", "rouge_l",
            "char_accuracy", "word_accuracy", "line_accuracy"
        ]
        
        task_specific_metrics = {
            "ocr": ["char_accuracy", "word_accuracy", "ocr_score"],
            "table": ["structure_similarity", "table_extraction_score"],
            "ui": ["element_detection_accuracy", "ui_detection_score"],
            "vqa": ["semantic_similarity", "semantic_understanding_score"],
            "caption": ["semantic_similarity", "semantic_understanding_score"]
        }
        
        return base_metrics + task_specific_metrics.get(self.task_type, [])