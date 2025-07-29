"""
Task Classification System for Training Requests

This module automatically classifies training tasks based on:
- Natural language descriptions
- Dataset characteristics
- Model requirements
- Domain-specific patterns

Supports classification for LLM, CV, Audio, and multi-modal tasks.
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class TaskAnalysis:
    """Results of task classification analysis."""
    
    # Primary classification
    task_type: str  # "chat", "classification", "summarization", "generation", etc.
    domain: str     # "general", "medical", "legal", "technical", etc.
    modality: str   # "text", "image", "audio", "multimodal"
    
    # Training characteristics
    training_type: str  # "sft", "rlhf", "dpo", "pretraining"
    complexity: str     # "simple", "medium", "complex"
    
    # Data characteristics
    language: str = "english"
    dataset_type: str = "instruction"  # "instruction", "conversational", "raw_text"
    estimated_size: int = 0
    
    # Confidence and metadata
    confidence: float = 0.0
    keywords: List[str] = None
    reasoning: List[str] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.reasoning is None:
            self.reasoning = []


class TaskClassifier:
    """
    Intelligent task classification system.
    
    Analyzes training requests and datasets to automatically determine:
    - Task type (chat, classification, summarization, etc.)
    - Domain (medical, legal, technical, etc.)
    - Modality (text, image, audio, multimodal)
    - Training approach (SFT, RLHF, DPO, etc.)
    - Complexity level
    
    Example:
        ```python
        classifier = TaskClassifier()
        
        analysis = classifier.analyze_request(
            "Fine-tune a model for medical question answering",
            "medical_qa_dataset.json"
        )
        
        print(f"Task: {analysis.task_type}")
        print(f"Domain: {analysis.domain}")
        print(f"Training: {analysis.training_type}")
        ```
    """
    
    def __init__(self):
        """Initialize task classifier with pattern libraries."""
        self.task_patterns = self._load_task_patterns()
        self.domain_patterns = self._load_domain_patterns()
        self.language_patterns = self._load_language_patterns()
        
        logger.info("Task classifier initialized")
    
    def analyze_request(self, description: str, dataset_source: str) -> TaskAnalysis:
        """
        Analyze training request and classify task.
        
        Args:
            description: Natural language description of training task
            dataset_source: Path to dataset or dataset identifier
            
        Returns:
            Complete task analysis
        """
        logger.info(f"Classifying task: {description[:50]}...")
        
        try:
            # Step 1: Extract keywords and normalize text
            keywords = self._extract_keywords(description)
            normalized_desc = description.lower()
            
            # Step 2: Classify task type
            task_type, task_confidence = self._classify_task_type(normalized_desc, keywords)
            
            # Step 3: Classify domain
            domain, domain_confidence = self._classify_domain(normalized_desc, keywords)
            
            # Step 4: Determine modality
            modality = self._determine_modality(normalized_desc, keywords, dataset_source)
            
            # Step 5: Determine training type
            training_type = self._determine_training_type(normalized_desc, keywords)
            
            # Step 6: Analyze complexity
            complexity = self._analyze_complexity(normalized_desc, keywords, dataset_source)
            
            # Step 7: Detect language
            language = self._detect_language(normalized_desc, keywords)
            
            # Step 8: Determine dataset type
            dataset_type = self._determine_dataset_type(dataset_source, normalized_desc)
            
            # Step 9: Generate reasoning
            reasoning = self._generate_reasoning(
                task_type, domain, modality, training_type, complexity, keywords
            )
            
            # Step 10: Calculate overall confidence
            overall_confidence = (task_confidence + domain_confidence) / 2
            
            analysis = TaskAnalysis(
                task_type=task_type,
                domain=domain,
                modality=modality,
                training_type=training_type,
                complexity=complexity,
                language=language,
                dataset_type=dataset_type,
                confidence=overall_confidence,
                keywords=keywords,
                reasoning=reasoning
            )
            
            logger.info(f"Task classified: {task_type} ({domain}) - {training_type}")
            return analysis
            
        except Exception as e:
            logger.error(f"Task classification failed: {e}")
            # Return default analysis
            return TaskAnalysis(
                task_type="sft",
                domain="general",
                modality="text",
                training_type="sft",
                complexity="medium",
                confidence=0.1,
                reasoning=["Classification failed, using defaults"]
            )
    
    def _load_task_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load task type classification patterns."""
        return {
            "chat": {
                "keywords": ["chat", "conversation", "dialogue", "chatbot", "assistant", "qa", "question", "answer"],
                "patterns": [
                    r"chat\s*(bot|assistant)",
                    r"(conversation|dialogue)\s*model",
                    r"question\s*answer",
                    r"customer\s*service",
                    r"virtual\s*assistant"
                ],
                "weight": 1.0
            },
            "classification": {
                "keywords": ["classify", "classification", "categorize", "category", "label", "sentiment", "emotion"],
                "patterns": [
                    r"(text|document)\s*classification",
                    r"sentiment\s*analysis",
                    r"categoriz[ae]", 
                    r"label\s*prediction",
                    r"emotion\s*detection"
                ],
                "weight": 1.0
            },
            "summarization": {
                "keywords": ["summarize", "summary", "summarization", "abstract", "brief", "condense"],
                "patterns": [
                    r"summariz[ae]",
                    r"abstract\s*generation",
                    r"text\s*summary",
                    r"document\s*summary"
                ],
                "weight": 1.0
            },
            "generation": {
                "keywords": ["generate", "generation", "creative", "story", "content", "write", "writing"],
                "patterns": [
                    r"text\s*generation",
                    r"content\s*generation",
                    r"creative\s*writing",
                    r"story\s*generation"
                ],
                "weight": 1.0
            },
            "translation": {
                "keywords": ["translate", "translation", "multilingual", "language", "cross-lingual"],
                "patterns": [
                    r"translation",
                    r"translate\s*between",
                    r"multilingual",
                    r"cross-lingual"
                ],
                "weight": 1.0
            },
            "reasoning": {
                "keywords": ["reasoning", "logic", "math", "mathematical", "problem", "solve"],
                "patterns": [
                    r"mathematical\s*reasoning",
                    r"logical\s*reasoning",
                    r"problem\s*solving",
                    r"math\s*problems"
                ],
                "weight": 1.0
            },
            "code": {
                "keywords": ["code", "programming", "python", "javascript", "sql", "development"],
                "patterns": [
                    r"code\s*(generation|completion)",
                    r"programming\s*assistance",
                    r"software\s*development",
                    r"(python|javascript|sql)\s*code"
                ],
                "weight": 1.0
            }
        }
    
    def _load_domain_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load domain classification patterns."""
        return {
            "medical": {
                "keywords": ["medical", "health", "healthcare", "clinical", "patient", "diagnosis", "treatment"],
                "patterns": [
                    r"medical\s*(qa|question|diagnosis)",
                    r"healthcare\s*assistant",
                    r"clinical\s*notes",
                    r"patient\s*records"
                ],
                "weight": 1.0
            },
            "legal": {
                "keywords": ["legal", "law", "lawyer", "court", "contract", "compliance", "regulation"],
                "patterns": [
                    r"legal\s*(document|analysis)",
                    r"law\s*assistant",
                    r"contract\s*review",
                    r"compliance\s*check"
                ],
                "weight": 1.0
            },
            "financial": {
                "keywords": ["financial", "finance", "trading", "investment", "banking", "economic"],
                "patterns": [
                    r"financial\s*analysis",
                    r"trading\s*assistant",
                    r"investment\s*advice",
                    r"banking\s*support"
                ],
                "weight": 1.0
            },
            "technical": {
                "keywords": ["technical", "engineering", "software", "programming", "development", "api"],
                "patterns": [
                    r"technical\s*documentation",
                    r"engineering\s*assistant",
                    r"api\s*documentation",
                    r"software\s*support"
                ],
                "weight": 1.0
            },
            "education": {
                "keywords": ["education", "learning", "teaching", "student", "tutor", "academic"],
                "patterns": [
                    r"educational\s*assistant",
                    r"tutoring\s*system",
                    r"academic\s*support",
                    r"learning\s*companion"
                ],
                "weight": 1.0
            },
            "ecommerce": {
                "keywords": ["ecommerce", "shopping", "product", "recommendation", "retail", "customer"],
                "patterns": [
                    r"product\s*recommendation",
                    r"shopping\s*assistant",
                    r"ecommerce\s*support",
                    r"retail\s*assistant"
                ],
                "weight": 1.0
            },
            "general": {
                "keywords": ["general", "assistant", "helper", "support", "chatbot"],
                "patterns": [
                    r"general\s*purpose",
                    r"personal\s*assistant",
                    r"general\s*chatbot"
                ],
                "weight": 0.5  # Lower weight as fallback
            }
        }
    
    def _load_language_patterns(self) -> Dict[str, List[str]]:
        """Load language detection patterns."""
        return {
            "chinese": ["chinese", "中文", "汉语", "普通话", "mandarin", "cantonese", "zh"],
            "japanese": ["japanese", "日本語", "nihongo", "ja"],
            "korean": ["korean", "한국어", "hangul", "ko"],
            "spanish": ["spanish", "español", "castellano", "es"],
            "french": ["french", "français", "fr"],
            "german": ["german", "deutsch", "de"],
            "italian": ["italian", "italiano", "it"],
            "portuguese": ["portuguese", "português", "pt"],
            "russian": ["russian", "русский", "ru"],
            "arabic": ["arabic", "العربية", "ar"],
            "hindi": ["hindi", "हिंदी", "hi"],
            "english": ["english", "en"]  # Default
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text."""
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'this', 'that', 'these', 'those'}
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:20]  # Return top 20 keywords
    
    def _classify_task_type(self, text: str, keywords: List[str]) -> Tuple[str, float]:
        """Classify the primary task type."""
        scores = {}
        
        for task_type, patterns in self.task_patterns.items():
            score = 0.0
            
            # Check keywords
            for keyword in patterns["keywords"]:
                if keyword in text or keyword in keywords:
                    score += 1.0
            
            # Check regex patterns
            for pattern in patterns["patterns"]:
                if re.search(pattern, text):
                    score += 2.0
            
            # Apply weight
            score *= patterns["weight"]
            scores[task_type] = score
        
        # Find highest scoring task type
        if scores:
            best_task = max(scores, key=scores.get)
            confidence = min(1.0, scores[best_task] / 3.0)  # Normalize confidence
            
            if confidence > 0.3:
                return best_task, confidence
        
        # Default to chat if no clear classification
        return "chat", 0.5
    
    def _classify_domain(self, text: str, keywords: List[str]) -> Tuple[str, float]:
        """Classify the domain/industry."""
        scores = {}
        
        for domain, patterns in self.domain_patterns.items():
            score = 0.0
            
            # Check keywords
            for keyword in patterns["keywords"]:
                if keyword in text or keyword in keywords:
                    score += 1.0
            
            # Check regex patterns
            for pattern in patterns["patterns"]:
                if re.search(pattern, text):
                    score += 2.0
            
            # Apply weight
            score *= patterns["weight"]
            scores[domain] = score
        
        # Find highest scoring domain
        if scores:
            best_domain = max(scores, key=scores.get)
            confidence = min(1.0, scores[best_domain] / 2.0)
            
            if confidence > 0.3:
                return best_domain, confidence
        
        # Default to general
        return "general", 0.5
    
    def _determine_modality(self, text: str, keywords: List[str], dataset_source: str) -> str:
        """Determine the modality (text, image, audio, multimodal)."""
        # Check for image-related keywords
        image_keywords = ["image", "picture", "photo", "visual", "vision", "cnn", "resnet", "vit"]
        if any(keyword in text for keyword in image_keywords):
            return "image"
        
        # Check for audio-related keywords  
        audio_keywords = ["audio", "speech", "voice", "sound", "whisper", "tts", "stt"]
        if any(keyword in text for keyword in audio_keywords):
            return "audio"
        
        # Check for multimodal keywords
        multimodal_keywords = ["multimodal", "vision-language", "clip", "blip", "image-text"]
        if any(keyword in text for keyword in multimodal_keywords):
            return "multimodal"
        
        # Check dataset source for file extensions
        if dataset_source:
            if any(ext in dataset_source.lower() for ext in [".jpg", ".png", ".jpeg", ".gif", ".bmp"]):
                return "image"
            elif any(ext in dataset_source.lower() for ext in [".wav", ".mp3", ".flac", ".m4a"]):
                return "audio"
        
        # Default to text
        return "text"
    
    def _determine_training_type(self, text: str, keywords: List[str]) -> str:
        """Determine the training approach."""
        # Check for specific training types
        if any(keyword in text for keyword in ["rlhf", "reinforcement", "human feedback"]):
            return "rlhf"
        
        if any(keyword in text for keyword in ["dpo", "direct preference", "preference optimization"]):
            return "dpo"
        
        if any(keyword in text for keyword in ["pretrain", "pretraining", "from scratch"]):
            return "pretraining"
        
        if any(keyword in text for keyword in ["instruction", "supervised", "fine-tune", "finetune"]):
            return "sft"
        
        # Default to SFT
        return "sft"
    
    def _analyze_complexity(self, text: str, keywords: List[str], dataset_source: str) -> str:
        """Analyze task complexity."""
        complexity_score = 0
        
        # High complexity indicators
        high_complexity_keywords = ["complex", "advanced", "sophisticated", "multi-step", "reasoning", "mathematical"]
        if any(keyword in text for keyword in high_complexity_keywords):
            complexity_score += 2
        
        # Medium complexity indicators
        medium_complexity_keywords = ["detailed", "comprehensive", "analysis", "professional"]
        if any(keyword in text for keyword in medium_complexity_keywords):
            complexity_score += 1
        
        # Simple complexity indicators
        simple_complexity_keywords = ["simple", "basic", "quick", "fast", "easy"]
        if any(keyword in text for keyword in simple_complexity_keywords):
            complexity_score -= 1
        
        # Determine complexity level
        if complexity_score >= 2:
            return "complex"
        elif complexity_score <= -1:
            return "simple"
        else:
            return "medium"
    
    def _detect_language(self, text: str, keywords: List[str]) -> str:
        """Detect the target language."""
        for language, patterns in self.language_patterns.items():
            if any(pattern in text for pattern in patterns):
                return language
        
        # Default to English
        return "english"
    
    def _determine_dataset_type(self, dataset_source: str, text: str) -> str:
        """Determine the dataset type."""
        if "alpaca" in dataset_source.lower() or "instruction" in text:
            return "instruction"
        elif "sharegpt" in dataset_source.lower() or "conversation" in text:
            return "conversational"
        elif "raw" in text or "text" in text:
            return "raw_text"
        else:
            return "instruction"  # Default
    
    def _generate_reasoning(
        self, 
        task_type: str, 
        domain: str, 
        modality: str, 
        training_type: str, 
        complexity: str, 
        keywords: List[str]
    ) -> List[str]:
        """Generate human-readable reasoning for the classification."""
        reasoning = []
        
        reasoning.append(f"Classified as {task_type} task based on keywords: {', '.join(keywords[:3])}")
        
        if domain != "general":
            reasoning.append(f"Identified {domain} domain specialization")
        
        if modality != "text":
            reasoning.append(f"Detected {modality} modality requirements")
        
        if training_type != "sft":
            reasoning.append(f"Recommended {training_type} training approach")
        
        reasoning.append(f"Estimated {complexity} complexity level")
        
        return reasoning
    
    def get_supported_tasks(self) -> List[str]:
        """Get list of supported task types."""
        return list(self.task_patterns.keys())
    
    def get_supported_domains(self) -> List[str]:
        """Get list of supported domains."""
        return list(self.domain_patterns.keys())
    
    def classify_dataset(self, dataset_path: str) -> Dict[str, Any]:
        """Classify a dataset file directly."""
        try:
            if not Path(dataset_path).exists():
                return {"error": f"Dataset not found: {dataset_path}"}
            
            # Analyze file extension
            suffix = Path(dataset_path).suffix.lower()
            
            analysis = {
                "file_type": suffix,
                "size": 0,
                "format": "unknown",
                "language": "unknown",
                "estimated_samples": 0
            }
            
            if suffix == ".json":
                with open(dataset_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if isinstance(data, list):
                        analysis["estimated_samples"] = len(data)
                        analysis["format"] = "json_list"
                        
                        # Analyze first sample
                        if data:
                            sample = data[0]
                            if isinstance(sample, dict):
                                if "instruction" in sample and "output" in sample:
                                    analysis["format"] = "alpaca"
                                elif "messages" in sample:
                                    analysis["format"] = "sharegpt"
                                elif "conversations" in sample:
                                    analysis["format"] = "conversational"
            
            analysis["size"] = Path(dataset_path).stat().st_size
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to classify dataset {dataset_path}: {e}")
            return {"error": str(e)}