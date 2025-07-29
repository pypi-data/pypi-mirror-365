"""
Standard AI Benchmarks for ISA Model Framework

This module provides implementations of standard AI benchmarks:
- MMLU (Massive Multitask Language Understanding)
- HellaSwag (Commonsense Reasoning)
- ARC (AI2 Reasoning Challenge)
- GSM8K (Grade School Math)
"""

import os
import json
import logging
import requests
import zipfile
import tarfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
import pandas as pd

logger = logging.getLogger(__name__)


class DatasetDownloader:
    """Utility class for downloading and caching benchmark datasets."""
    
    def __init__(self, cache_dir: str = "~/.isa_model/datasets"):
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Dataset URLs and info
        self.dataset_info = {
            "mmlu": {
                "url": "https://people.eecs.berkeley.edu/~hendrycks/data.tar",
                "filename": "mmlu_data.tar",
                "extracted_dir": "data"
            },
            "hellaswag": {
                "url": "https://raw.githubusercontent.com/rowanz/hellaswag/master/data/hellaswag_val.jsonl",
                "filename": "hellaswag_val.jsonl"
            },
            "arc": {
                "url": "https://s3-us-west-2.amazonaws.com/ai2-website/data/ARC-V1-Feb2018.zip",
                "filename": "arc_data.zip",
                "extracted_dir": "ARC-V1-Feb2018-2"
            },
            "gsm8k": {
                "url": "https://github.com/openai/grade-school-math/raw/master/grade_school_math/data/test.jsonl",
                "filename": "gsm8k_test.jsonl"
            }
        }
    
    def download_dataset(self, dataset_name: str, force_download: bool = False) -> Path:
        """Download and cache a dataset."""
        if dataset_name not in self.dataset_info:
            raise ValueError(f"Unknown dataset: {dataset_name}")
        
        info = self.dataset_info[dataset_name]
        dataset_dir = self.cache_dir / dataset_name
        dataset_dir.mkdir(exist_ok=True)
        
        file_path = dataset_dir / info["filename"]
        
        # Check if already downloaded
        if file_path.exists() and not force_download:
            logger.info(f"Using cached {dataset_name} dataset at {file_path}")
            return self._get_data_path(dataset_name, file_path)
        
        # Download the dataset
        logger.info(f"Downloading {dataset_name} dataset from {info['url']}")
        try:
            response = requests.get(info["url"], stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded {dataset_name} dataset to {file_path}")
            
            # Extract if needed
            return self._get_data_path(dataset_name, file_path)
            
        except Exception as e:
            logger.error(f"Failed to download {dataset_name}: {e}")
            # Fall back to placeholder data
            return None
    
    def _get_data_path(self, dataset_name: str, file_path: Path) -> Path:
        """Get the actual data path, extracting archives if needed."""
        info = self.dataset_info[dataset_name]
        
        if "extracted_dir" in info:
            # Need to extract
            extract_dir = file_path.parent / info["extracted_dir"]
            
            if not extract_dir.exists():
                logger.info(f"Extracting {file_path}")
                
                if file_path.suffix == ".zip":
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(file_path.parent)
                elif file_path.suffix == ".tar" or ".tar." in file_path.name:
                    with tarfile.open(file_path, 'r') as tar_ref:
                        tar_ref.extractall(file_path.parent)
            
            return extract_dir
        else:
            return file_path


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark evaluation."""
    name: str
    description: str
    num_choices: int = 4
    few_shot_examples: int = 5
    max_samples: Optional[int] = None
    subjects: Optional[List[str]] = None


class BaseBenchmark(ABC):
    """Base class for all benchmarks."""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.name = config.name
        self.data = None
        self.downloader = DatasetDownloader()
        self.use_real_data = True  # Flag to control real vs placeholder data
    
    @abstractmethod
    def load_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load benchmark data."""
        pass
    
    @abstractmethod
    def evaluate_sample(self, sample: Dict[str, Any], prediction: str) -> bool:
        """Evaluate a single sample."""
        pass
    
    def format_prompt(self, sample: Dict[str, Any], few_shot_examples: Optional[List[Dict[str, Any]]] = None) -> str:
        """Format prompt for the sample."""
        prompt = ""
        
        # Add few-shot examples if provided
        if few_shot_examples:
            for example in few_shot_examples:
                prompt += self._format_single_example(example, include_answer=True) + "\n\n"
        
        # Add the actual question
        prompt += self._format_single_example(sample, include_answer=False)
        
        return prompt
    
    @abstractmethod
    def _format_single_example(self, sample: Dict[str, Any], include_answer: bool = False) -> str:
        """Format a single example."""
        pass


class MMLU(BaseBenchmark):
    """
    MMLU (Massive Multitask Language Understanding) Benchmark
    
    Tests knowledge across 57 subjects including mathematics, history, 
    computer science, law, and more.
    """
    
    def __init__(self, subjects: Optional[List[str]] = None):
        config = BenchmarkConfig(
            name="MMLU",
            description="Massive Multitask Language Understanding",
            num_choices=4,
            few_shot_examples=5,
            subjects=subjects
        )
        super().__init__(config)
        
        # MMLU subjects
        self.all_subjects = [
            "abstract_algebra", "anatomy", "astronomy", "business_ethics",
            "clinical_knowledge", "college_biology", "college_chemistry",
            "college_computer_science", "college_mathematics", "college_medicine",
            "college_physics", "computer_security", "conceptual_physics",
            "econometrics", "electrical_engineering", "elementary_mathematics",
            "formal_logic", "global_facts", "high_school_biology",
            "high_school_chemistry", "high_school_computer_science",
            "high_school_european_history", "high_school_geography",
            "high_school_government_and_politics", "high_school_macroeconomics",
            "high_school_mathematics", "high_school_microeconomics",
            "high_school_physics", "high_school_psychology", "high_school_statistics",
            "high_school_us_history", "high_school_world_history", "human_aging",
            "human_sexuality", "international_law", "jurisprudence",
            "logical_fallacies", "machine_learning", "management", "marketing",
            "medical_genetics", "miscellaneous", "moral_disputes", "moral_scenarios",
            "nutrition", "philosophy", "prehistory", "professional_accounting",
            "professional_law", "professional_medicine", "professional_psychology",
            "public_relations", "security_studies", "sociology", "us_foreign_policy",
            "virology", "world_religions"
        ]
        
        self.subjects = subjects or self.all_subjects[:10]  # Use first 10 subjects by default
    
    def load_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load MMLU data with real dataset support."""
        if self.use_real_data:
            try:
                return self._load_real_mmlu_data(max_samples)
            except Exception as e:
                logger.warning(f"Failed to load real MMLU data: {e}. Falling back to placeholder data.")
                return self._load_placeholder_mmlu_data(max_samples)
        else:
            return self._load_placeholder_mmlu_data(max_samples)
    
    def _load_real_mmlu_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load real MMLU dataset."""
        data_path = self.downloader.download_dataset("mmlu")
        if not data_path or not data_path.exists():
            raise FileNotFoundError("MMLU dataset not found")
        
        data = []
        samples_per_subject = max_samples // len(self.subjects) if max_samples else None
        
        for subject in self.subjects:
            subject_file = data_path / "test" / f"{subject}_test.csv"
            if not subject_file.exists():
                logger.warning(f"Subject file not found: {subject_file}")
                continue
            
            try:
                # Load CSV data
                df = pd.read_csv(subject_file, header=None, 
                               names=["question", "A", "B", "C", "D", "answer"])
                
                # Convert to our format
                for idx, row in df.iterrows():
                    if samples_per_subject and len([d for d in data if d["subject"] == subject]) >= samples_per_subject:
                        break
                    
                    sample = {
                        "subject": subject,
                        "question": row["question"],
                        "choices": [row["A"], row["B"], row["C"], row["D"]],
                        "answer": str(row["answer"]).strip().upper(),
                        "id": f"{subject}_{idx}"
                    }
                    data.append(sample)
                    
            except Exception as e:
                logger.error(f"Error loading subject {subject}: {e}")
                continue
        
        if max_samples:
            data = data[:max_samples]
        
        logger.info(f"Loaded {len(data)} real MMLU samples across {len(self.subjects)} subjects")
        return data
    
    def _load_placeholder_mmlu_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load placeholder MMLU data."""
        data = []
        
        for subject in self.subjects:
            # Generate sample questions for each subject
            for i in range(min(10, max_samples // len(self.subjects) if max_samples else 10)):
                sample = {
                    "subject": subject,
                    "question": f"Sample {subject} question {i+1}",
                    "choices": [
                        f"Option A for {subject}",
                        f"Option B for {subject}",
                        f"Option C for {subject}",
                        f"Option D for {subject}"
                    ],
                    "answer": "A",  # Simplified
                    "id": f"{subject}_{i}"
                }
                data.append(sample)
        
        if max_samples:
            data = data[:max_samples]
        
        logger.info(f"Loaded {len(data)} placeholder MMLU samples across {len(self.subjects)} subjects")
        return data
    
    def evaluate_sample(self, sample: Dict[str, Any], prediction: str) -> bool:
        """Evaluate a single MMLU sample."""
        # Extract the letter choice from prediction
        prediction = prediction.strip().upper()
        
        # Handle various response formats
        if prediction in ["A", "B", "C", "D"]:
            return prediction == sample["answer"]
        elif prediction.startswith("(") and prediction.endswith(")"):
            letter = prediction[1]
            return letter == sample["answer"]
        else:
            # Try to find A, B, C, or D in the response
            for choice in ["A", "B", "C", "D"]:
                if choice in prediction:
                    return choice == sample["answer"]
        
        return False
    
    def _format_single_example(self, sample: Dict[str, Any], include_answer: bool = False) -> str:
        """Format a single MMLU example."""
        prompt = f"Subject: {sample['subject'].replace('_', ' ').title()}\n"
        prompt += f"Question: {sample['question']}\n"
        
        choices = sample['choices']
        for i, choice in enumerate(choices):
            letter = chr(65 + i)  # A, B, C, D
            prompt += f"{letter}. {choice}\n"
        
        if include_answer:
            prompt += f"Answer: {sample['answer']}"
        else:
            prompt += "Answer:"
        
        return prompt


class HellaSwag(BaseBenchmark):
    """
    HellaSwag Benchmark
    
    Tests commonsense reasoning about physical situations.
    """
    
    def __init__(self):
        config = BenchmarkConfig(
            name="HellaSwag",
            description="Commonsense Reasoning about Physical Situations",
            num_choices=4,
            few_shot_examples=10
        )
        super().__init__(config)
    
    def load_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load HellaSwag data with real dataset support."""
        if self.use_real_data:
            try:
                return self._load_real_hellaswag_data(max_samples)
            except Exception as e:
                logger.warning(f"Failed to load real HellaSwag data: {e}. Falling back to placeholder data.")
                return self._load_placeholder_hellaswag_data(max_samples)
        else:
            return self._load_placeholder_hellaswag_data(max_samples)
    
    def _load_real_hellaswag_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load real HellaSwag dataset."""
        data_path = self.downloader.download_dataset("hellaswag")
        if not data_path or not data_path.exists():
            raise FileNotFoundError("HellaSwag dataset not found")
        
        data = []
        
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if max_samples and i >= max_samples:
                        break
                    
                    item = json.loads(line.strip())
                    
                    sample = {
                        "context": item["ctx"],
                        "question": "What happens next?",
                        "choices": item["endings"],
                        "answer": chr(65 + int(item["label"])),  # Convert 0,1,2,3 to A,B,C,D
                        "id": f"hellaswag_{item.get('ind', i)}"
                    }
                    data.append(sample)
        
        except Exception as e:
            logger.error(f"Error loading HellaSwag data: {e}")
            raise
        
        logger.info(f"Loaded {len(data)} real HellaSwag samples")
        return data
    
    def _load_placeholder_hellaswag_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load placeholder HellaSwag data."""
        data = []
        
        sample_contexts = [
            "A person is washing dishes in the kitchen",
            "Someone is riding a bicycle down a hill",
            "A chef is preparing ingredients for cooking",
            "A student is taking notes in class",
            "A gardener is planting flowers"
        ]
        
        for i, context in enumerate(sample_contexts):
            if max_samples and i >= max_samples:
                break
                
            sample = {
                "context": context,
                "question": "What happens next?",
                "choices": [
                    f"They continue with the logical next step for scenario {i+1}",
                    f"They do something completely unrelated to scenario {i+1}",
                    f"They stop and do something random in scenario {i+1}",
                    f"They repeat the same action in scenario {i+1}"
                ],
                "answer": "A",  # First choice is usually most logical
                "id": f"hellaswag_{i}"
            }
            data.append(sample)
        
        logger.info(f"Loaded {len(data)} placeholder HellaSwag samples")
        return data
    
    def evaluate_sample(self, sample: Dict[str, Any], prediction: str) -> bool:
        """Evaluate a single HellaSwag sample."""
        prediction = prediction.strip().upper()
        
        if prediction in ["A", "B", "C", "D"]:
            return prediction == sample["answer"]
        
        # Try to extract choice from longer response
        for choice in ["A", "B", "C", "D"]:
            if choice in prediction:
                return choice == sample["answer"]
        
        return False
    
    def _format_single_example(self, sample: Dict[str, Any], include_answer: bool = False) -> str:
        """Format a single HellaSwag example."""
        prompt = f"Context: {sample['context']}\n"
        prompt += f"Question: {sample['question']}\n"
        
        choices = sample['choices']
        for i, choice in enumerate(choices):
            letter = chr(65 + i)  # A, B, C, D
            prompt += f"{letter}. {choice}\n"
        
        if include_answer:
            prompt += f"Answer: {sample['answer']}"
        else:
            prompt += "Answer:"
        
        return prompt


class ARC(BaseBenchmark):
    """
    ARC (AI2 Reasoning Challenge) Benchmark
    
    Tests scientific reasoning with grade-school level science questions.
    """
    
    def __init__(self, challenge_set: str = "easy"):
        config = BenchmarkConfig(
            name=f"ARC-{challenge_set}",
            description=f"AI2 Reasoning Challenge ({challenge_set})",
            num_choices=4,
            few_shot_examples=25
        )
        super().__init__(config)
        self.challenge_set = challenge_set  # "easy" or "challenge"
    
    def load_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load ARC data (simplified implementation)."""
        # This is a simplified implementation
        # In practice, you'd load from the actual ARC dataset
        
        data = []
        
        sample_questions = [
            {
                "question": "What happens to water when it freezes?",
                "choices": ["It becomes ice", "It becomes gas", "It disappears", "It becomes hot"],
                "answer": "A"
            },
            {
                "question": "Which planet is closest to the Sun?",
                "choices": ["Earth", "Mars", "Mercury", "Venus"],
                "answer": "C"
            },
            {
                "question": "What do plants need to make their own food?",
                "choices": ["Sunlight and water", "Only water", "Only sunlight", "Soil only"],
                "answer": "A"
            },
            {
                "question": "What is the main gas in Earth's atmosphere?",
                "choices": ["Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen"],
                "answer": "C"
            },
            {
                "question": "How many legs does a spider have?",
                "choices": ["6", "8", "10", "12"],
                "answer": "B"
            }
        ]
        
        for i, q in enumerate(sample_questions):
            if max_samples and i >= max_samples:
                break
                
            sample = {
                "question": q["question"],
                "choices": q["choices"],
                "answer": q["answer"],
                "challenge_set": self.challenge_set,
                "id": f"arc_{self.challenge_set}_{i}"
            }
            data.append(sample)
        
        logger.info(f"Loaded {len(data)} ARC-{self.challenge_set} samples")
        return data
    
    def evaluate_sample(self, sample: Dict[str, Any], prediction: str) -> bool:
        """Evaluate a single ARC sample."""
        prediction = prediction.strip().upper()
        
        if prediction in ["A", "B", "C", "D"]:
            return prediction == sample["answer"]
        
        # Try to extract choice from longer response
        for choice in ["A", "B", "C", "D"]:
            if choice in prediction:
                return choice == sample["answer"]
        
        return False
    
    def _format_single_example(self, sample: Dict[str, Any], include_answer: bool = False) -> str:
        """Format a single ARC example."""
        prompt = f"Question: {sample['question']}\n"
        
        choices = sample['choices']
        for i, choice in enumerate(choices):
            letter = chr(65 + i)  # A, B, C, D
            prompt += f"{letter}. {choice}\n"
        
        if include_answer:
            prompt += f"Answer: {sample['answer']}"
        else:
            prompt += "Answer:"
        
        return prompt


class GSM8K(BaseBenchmark):
    """
    GSM8K Benchmark
    
    Tests mathematical reasoning with grade school math word problems.
    """
    
    def __init__(self):
        config = BenchmarkConfig(
            name="GSM8K",
            description="Grade School Math 8K",
            num_choices=1,  # Open-ended numerical answers
            few_shot_examples=8
        )
        super().__init__(config)
    
    def load_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load GSM8K data with real dataset support."""
        if self.use_real_data:
            try:
                return self._load_real_gsm8k_data(max_samples)
            except Exception as e:
                logger.warning(f"Failed to load real GSM8K data: {e}. Falling back to placeholder data.")
                return self._load_placeholder_gsm8k_data(max_samples)
        else:
            return self._load_placeholder_gsm8k_data(max_samples)
    
    def _load_real_gsm8k_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load real GSM8K dataset."""
        data_path = self.downloader.download_dataset("gsm8k")
        if not data_path or not data_path.exists():
            raise FileNotFoundError("GSM8K dataset not found")
        
        data = []
        
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if max_samples and i >= max_samples:
                        break
                    
                    item = json.loads(line.strip())
                    
                    # Extract numerical answer from solution
                    answer_text = item["answer"]
                    import re
                    numbers = re.findall(r'\d+', answer_text)
                    answer = numbers[-1] if numbers else "0"
                    
                    sample = {
                        "question": item["question"],
                        "answer": answer,
                        "solution": answer_text,  # Keep full solution for reference
                        "id": f"gsm8k_{i}"
                    }
                    data.append(sample)
        
        except Exception as e:
            logger.error(f"Error loading GSM8K data: {e}")
            raise
        
        logger.info(f"Loaded {len(data)} real GSM8K samples")
        return data
    
    def _load_placeholder_gsm8k_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load placeholder GSM8K data."""
        data = []
        
        sample_problems = [
            {
                "question": "Janet has 12 apples. She gives 3 apples to her friend and eats 2 apples. How many apples does Janet have left?",
                "answer": "7"
            },
            {
                "question": "A school has 24 students in each class. If there are 5 classes, how many students are there in total?",
                "answer": "120"
            },
            {
                "question": "Tom buys 4 books for $8 each. How much money does Tom spend in total?",
                "answer": "32"
            },
            {
                "question": "Sarah has 36 stickers. She wants to put them equally into 6 albums. How many stickers will be in each album?",
                "answer": "6"
            },
            {
                "question": "A rectangle has a length of 15 cm and a width of 8 cm. What is the area of the rectangle?",
                "answer": "120"
            }
        ]
        
        for i, problem in enumerate(sample_problems):
            if max_samples and i >= max_samples:
                break
                
            sample = {
                "question": problem["question"],
                "answer": problem["answer"],
                "id": f"gsm8k_{i}"
            }
            data.append(sample)
        
        logger.info(f"Loaded {len(data)} placeholder GSM8K samples")
        return data
    
    def evaluate_sample(self, sample: Dict[str, Any], prediction: str) -> bool:
        """Evaluate a single GSM8K sample."""
        # Extract numerical answer from prediction
        prediction = prediction.strip()
        
        # Try to find the numerical answer
        import re
        numbers = re.findall(r'\d+', prediction)
        
        if numbers:
            # Take the last number found (often the final answer)
            predicted_answer = numbers[-1]
            return predicted_answer == sample["answer"]
        
        return False
    
    def _format_single_example(self, sample: Dict[str, Any], include_answer: bool = False) -> str:
        """Format a single GSM8K example."""
        prompt = f"Problem: {sample['question']}\n"
        
        if include_answer:
            prompt += f"Answer: {sample['answer']}"
        else:
            prompt += "Answer:"
        
        return prompt


# Convenience functions for creating benchmark instances
def create_mmlu_benchmark(subjects: Optional[List[str]] = None) -> MMLU:
    """Create MMLU benchmark instance."""
    return MMLU(subjects=subjects)


def create_hellaswag_benchmark() -> HellaSwag:
    """Create HellaSwag benchmark instance."""
    return HellaSwag()


def create_arc_benchmark(challenge_set: str = "easy") -> ARC:
    """Create ARC benchmark instance."""
    return ARC(challenge_set=challenge_set)


def create_gsm8k_benchmark() -> GSM8K:
    """Create GSM8K benchmark instance."""
    return GSM8K() 