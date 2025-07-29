"""
Multimodal Dataset Support for ISA Model evaluation framework.

Provides dataset loaders for:
- VQA v2.0 (Visual Question Answering)
- COCO Captions (Image Captioning)
- DocVQA (Document Visual Question Answering)
- Audio datasets (LibriSpeech, Common Voice)
"""

import os
import json
import logging
import requests
import zipfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import pandas as pd
from PIL import Image
import base64
from io import BytesIO

logger = logging.getLogger(__name__)


class MultimodalDatasetDownloader:
    """Utility class for downloading multimodal datasets."""
    
    def __init__(self, cache_dir: str = "~/.isa_model/multimodal_datasets"):
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.dataset_info = {
            "vqa_v2": {
                "annotations_url": "https://s3.amazonaws.com/cvmlp/vqa/mscoco/vqa/v2_Annotations_Val_mscoco.zip",
                "questions_url": "https://s3.amazonaws.com/cvmlp/vqa/mscoco/vqa/v2_Questions_Val_mscoco.zip",
                "images_url": "http://images.cocodataset.org/zips/val2014.zip",
                "description": "VQA v2.0 validation set"
            },
            "coco_captions": {
                "annotations_url": "http://images.cocodataset.org/annotations/annotations_trainval2014.zip",
                "images_url": "http://images.cocodataset.org/zips/val2014.zip",
                "description": "COCO Captions validation set"
            },
            "docvqa": {
                "url": "https://datasets.cvc.uab.es/rrc/DocVQA/train.tar.gz",
                "description": "DocVQA training set"
            },
            "librispeech": {
                "url": "http://www.openslr.org/resources/12/test-clean.tar.gz",
                "description": "LibriSpeech test-clean set"
            }
        }
    
    def download_dataset(self, dataset_name: str, subset: str = "val", force_download: bool = False) -> Optional[Path]:
        """Download and cache a multimodal dataset."""
        if dataset_name not in self.dataset_info:
            raise ValueError(f"Unknown dataset: {dataset_name}")
        
        dataset_dir = self.cache_dir / dataset_name
        dataset_dir.mkdir(exist_ok=True)
        
        try:
            if dataset_name == "vqa_v2":
                return self._download_vqa_v2(dataset_dir, force_download)
            elif dataset_name == "coco_captions":
                return self._download_coco_captions(dataset_dir, force_download)
            elif dataset_name == "docvqa":
                return self._download_docvqa(dataset_dir, force_download)
            elif dataset_name == "librispeech":
                return self._download_librispeech(dataset_dir, force_download)
        except Exception as e:
            logger.error(f"Failed to download {dataset_name}: {e}")
            return None
    
    def _download_vqa_v2(self, dataset_dir: Path, force_download: bool) -> Path:
        """Download VQA v2.0 dataset."""
        annotations_file = dataset_dir / "v2_mscoco_val2014_annotations.json"
        questions_file = dataset_dir / "v2_OpenEnded_mscoco_val2014_questions.json"
        
        if annotations_file.exists() and questions_file.exists() and not force_download:
            logger.info("Using cached VQA v2.0 dataset")
            return dataset_dir
        
        info = self.dataset_info["vqa_v2"]
        
        # Download annotations
        if not annotations_file.exists() or force_download:
            logger.info("Downloading VQA v2.0 annotations")
            self._download_and_extract(info["annotations_url"], dataset_dir)
        
        # Download questions
        if not questions_file.exists() or force_download:
            logger.info("Downloading VQA v2.0 questions")
            self._download_and_extract(info["questions_url"], dataset_dir)
        
        return dataset_dir
    
    def _download_coco_captions(self, dataset_dir: Path, force_download: bool) -> Path:
        """Download COCO Captions dataset."""
        captions_file = dataset_dir / "annotations" / "captions_val2014.json"
        
        if captions_file.exists() and not force_download:
            logger.info("Using cached COCO Captions dataset")
            return dataset_dir
        
        info = self.dataset_info["coco_captions"]
        
        # Download annotations
        logger.info("Downloading COCO Captions annotations")
        self._download_and_extract(info["annotations_url"], dataset_dir)
        
        return dataset_dir
    
    def _download_docvqa(self, dataset_dir: Path, force_download: bool) -> Path:
        """Download DocVQA dataset (placeholder implementation)."""
        # This would require actual DocVQA dataset access
        logger.warning("DocVQA dataset download not implemented - using placeholder")
        return dataset_dir
    
    def _download_librispeech(self, dataset_dir: Path, force_download: bool) -> Path:
        """Download LibriSpeech dataset (placeholder implementation)."""
        # This would require actual LibriSpeech dataset download
        logger.warning("LibriSpeech dataset download not implemented - using placeholder")
        return dataset_dir
    
    def _download_and_extract(self, url: str, extract_dir: Path):
        """Download and extract a file."""
        filename = url.split('/')[-1]
        file_path = extract_dir / filename
        
        # Download
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract
        if filename.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        elif filename.endswith('.tar.gz'):
            import tarfile
            with tarfile.open(file_path, 'r:gz') as tar_ref:
                tar_ref.extractall(extract_dir)
        
        # Clean up archive file
        file_path.unlink()


class VQAv2Dataset:
    """VQA v2.0 Dataset loader."""
    
    def __init__(self, cache_dir: str = "~/.isa_model/multimodal_datasets"):
        self.downloader = MultimodalDatasetDownloader(cache_dir)
        self.dataset_dir = None
        self.annotations = None
        self.questions = None
    
    def load_data(self, max_samples: Optional[int] = None, use_real_data: bool = True) -> List[Dict[str, Any]]:
        """Load VQA v2.0 data."""
        if use_real_data:
            try:
                return self._load_real_data(max_samples)
            except Exception as e:
                logger.warning(f"Failed to load real VQA data: {e}. Using placeholder data.")
                return self._load_placeholder_data(max_samples)
        else:
            return self._load_placeholder_data(max_samples)
    
    def _load_real_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load real VQA v2.0 data."""
        self.dataset_dir = self.downloader.download_dataset("vqa_v2")
        if not self.dataset_dir:
            raise FileNotFoundError("VQA v2.0 dataset not found")
        
        # Load annotations and questions
        annotations_file = self.dataset_dir / "v2_mscoco_val2014_annotations.json"
        questions_file = self.dataset_dir / "v2_OpenEnded_mscoco_val2014_questions.json"
        
        with open(annotations_file, 'r') as f:
            annotations_data = json.load(f)
        
        with open(questions_file, 'r') as f:
            questions_data = json.load(f)
        
        # Create question_id -> annotation mapping
        annotations_dict = {ann['question_id']: ann for ann in annotations_data['annotations']}
        
        data = []
        for i, question in enumerate(questions_data['questions']):
            if max_samples and i >= max_samples:
                break
            
            question_id = question['question_id']
            if question_id in annotations_dict:
                annotation = annotations_dict[question_id]
                
                # Get the most common answer
                answers = [ans['answer'] for ans in annotation['answers']]
                most_common_answer = max(set(answers), key=answers.count)
                
                sample = {
                    "image_id": question['image_id'],
                    "question": question['question'],
                    "expected_output": most_common_answer,
                    "task_type": "vqa",
                    "id": f"vqa_{question_id}",
                    "image": f"COCO_val2014_{question['image_id']:012d}.jpg"  # COCO image filename format
                }
                data.append(sample)
        
        logger.info(f"Loaded {len(data)} real VQA v2.0 samples")
        return data
    
    def _load_placeholder_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load placeholder VQA data."""
        sample_questions = [
            {"question": "What color is the cat?", "answer": "orange"},
            {"question": "How many people are in the image?", "answer": "3"},
            {"question": "What is the weather like?", "answer": "sunny"},
            {"question": "What vehicle is shown?", "answer": "car"},
            {"question": "What room is this?", "answer": "kitchen"}
        ]
        
        data = []
        for i, item in enumerate(sample_questions):
            if max_samples and i >= max_samples:
                break
            
            sample = {
                "image_id": f"placeholder_{i}",
                "question": item["question"],
                "expected_output": item["answer"],
                "task_type": "vqa",
                "id": f"vqa_placeholder_{i}",
                "image": None  # Placeholder - no actual image
            }
            data.append(sample)
        
        logger.info(f"Loaded {len(data)} placeholder VQA samples")
        return data


class COCOCaptionsDataset:
    """COCO Captions Dataset loader."""
    
    def __init__(self, cache_dir: str = "~/.isa_model/multimodal_datasets"):
        self.downloader = MultimodalDatasetDownloader(cache_dir)
        self.dataset_dir = None
    
    def load_data(self, max_samples: Optional[int] = None, use_real_data: bool = True) -> List[Dict[str, Any]]:
        """Load COCO Captions data."""
        if use_real_data:
            try:
                return self._load_real_data(max_samples)
            except Exception as e:
                logger.warning(f"Failed to load real COCO Captions data: {e}. Using placeholder data.")
                return self._load_placeholder_data(max_samples)
        else:
            return self._load_placeholder_data(max_samples)
    
    def _load_real_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load real COCO Captions data."""
        self.dataset_dir = self.downloader.download_dataset("coco_captions")
        if not self.dataset_dir:
            raise FileNotFoundError("COCO Captions dataset not found")
        
        # Load captions
        captions_file = self.dataset_dir / "annotations" / "captions_val2014.json"
        
        with open(captions_file, 'r') as f:
            captions_data = json.load(f)
        
        # Group captions by image_id
        image_captions = {}
        for annotation in captions_data['annotations']:
            image_id = annotation['image_id']
            if image_id not in image_captions:
                image_captions[image_id] = []
            image_captions[image_id].append(annotation['caption'])
        
        data = []
        for i, (image_id, captions) in enumerate(image_captions.items()):
            if max_samples and i >= max_samples:
                break
            
            # Use the first caption as the expected output
            sample = {
                "image_id": image_id,
                "expected_output": captions[0],
                "all_captions": captions,  # Keep all captions for evaluation
                "task_type": "caption",
                "prompt": "Generate a detailed caption describing this image.",
                "id": f"coco_caption_{image_id}",
                "image": f"COCO_val2014_{image_id:012d}.jpg"
            }
            data.append(sample)
        
        logger.info(f"Loaded {len(data)} real COCO Captions samples")
        return data
    
    def _load_placeholder_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load placeholder captions data."""
        sample_captions = [
            "A cat sitting on a windowsill looking outside",
            "Three people walking in a park on a sunny day", 
            "A red car parked on a city street",
            "A kitchen with modern appliances and granite countertops",
            "A dog playing fetch in a grassy field"
        ]
        
        data = []
        for i, caption in enumerate(sample_captions):
            if max_samples and i >= max_samples:
                break
            
            sample = {
                "image_id": f"placeholder_{i}",
                "expected_output": caption,
                "task_type": "caption",
                "prompt": "Generate a detailed caption describing this image.",
                "id": f"coco_caption_placeholder_{i}",
                "image": None  # Placeholder - no actual image
            }
            data.append(sample)
        
        logger.info(f"Loaded {len(data)} placeholder caption samples")
        return data


class DocVQADataset:
    """DocVQA Dataset loader."""
    
    def __init__(self, cache_dir: str = "~/.isa_model/multimodal_datasets"):
        self.downloader = MultimodalDatasetDownloader(cache_dir)
        self.dataset_dir = None
    
    def load_data(self, max_samples: Optional[int] = None, use_real_data: bool = False) -> List[Dict[str, Any]]:
        """Load DocVQA data (currently placeholder only)."""
        # For now, only placeholder data since DocVQA requires special access
        return self._load_placeholder_data(max_samples)
    
    def _load_placeholder_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load placeholder DocVQA data."""
        sample_doc_questions = [
            {"question": "What is the title of this document?", "answer": "Annual Report 2023"},
            {"question": "Who is the author?", "answer": "John Smith"},
            {"question": "What is the total revenue?", "answer": "$1.2 million"},
            {"question": "How many pages does this document have?", "answer": "45"},
            {"question": "What year was this published?", "answer": "2023"}
        ]
        
        data = []
        for i, item in enumerate(sample_doc_questions):
            if max_samples and i >= max_samples:
                break
            
            sample = {
                "document_id": f"doc_{i}",
                "question": item["question"],
                "expected_output": item["answer"],
                "task_type": "document_vqa",
                "id": f"docvqa_placeholder_{i}",
                "image": None  # Placeholder - no actual document image
            }
            data.append(sample)
        
        logger.info(f"Loaded {len(data)} placeholder DocVQA samples")
        return data


class AudioDatasetLoader:
    """Audio dataset loader for speech tasks."""
    
    def __init__(self, cache_dir: str = "~/.isa_model/multimodal_datasets"):
        self.downloader = MultimodalDatasetDownloader(cache_dir)
    
    def load_librispeech_data(self, max_samples: Optional[int] = None, use_real_data: bool = False) -> List[Dict[str, Any]]:
        """Load LibriSpeech data (currently placeholder only)."""
        return self._load_placeholder_speech_data(max_samples)
    
    def _load_placeholder_speech_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load placeholder speech data."""
        sample_transcripts = [
            "The quick brown fox jumps over the lazy dog",
            "Machine learning is transforming artificial intelligence",
            "Natural language processing enables computers to understand human speech",
            "Deep learning models require large amounts of training data",
            "Speech recognition technology has improved significantly in recent years"
        ]
        
        data = []
        for i, transcript in enumerate(sample_transcripts):
            if max_samples and i >= max_samples:
                break
            
            sample = {
                "audio_id": f"speech_{i}",
                "expected_output": transcript,
                "task_type": "stt",
                "id": f"librispeech_placeholder_{i}",
                "audio": None,  # Placeholder - no actual audio file
                "metadata": {
                    "speaker": f"speaker_{i % 3}",
                    "gender": "male" if i % 2 == 0 else "female",
                    "duration": 3.5 + i * 0.5
                }
            }
            data.append(sample)
        
        logger.info(f"Loaded {len(data)} placeholder speech samples")
        return data
    
    def load_emotion_data(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load placeholder emotion recognition data."""
        emotions = ["happy", "sad", "angry", "neutral", "surprised"]
        
        data = []
        for i in range(min(max_samples or 20, 20)):
            emotion = emotions[i % len(emotions)]
            
            sample = {
                "audio_id": f"emotion_{i}",
                "expected_output": emotion,
                "task_type": "emotion",
                "id": f"emotion_placeholder_{i}",
                "audio": None,  # Placeholder - no actual audio file
                "metadata": {
                    "speaker": f"speaker_{i % 5}",
                    "intensity": "medium"
                }
            }
            data.append(sample)
        
        logger.info(f"Loaded {len(data)} placeholder emotion samples")
        return data


# Convenience functions
def create_vqa_dataset(cache_dir: str = "~/.isa_model/multimodal_datasets") -> VQAv2Dataset:
    """Create VQA v2.0 dataset instance."""
    return VQAv2Dataset(cache_dir)


def create_coco_captions_dataset(cache_dir: str = "~/.isa_model/multimodal_datasets") -> COCOCaptionsDataset:
    """Create COCO Captions dataset instance."""
    return COCOCaptionsDataset(cache_dir)


def create_docvqa_dataset(cache_dir: str = "~/.isa_model/multimodal_datasets") -> DocVQADataset:
    """Create DocVQA dataset instance."""
    return DocVQADataset(cache_dir)


def create_audio_dataset_loader(cache_dir: str = "~/.isa_model/multimodal_datasets") -> AudioDatasetLoader:
    """Create audio dataset loader instance."""
    return AudioDatasetLoader(cache_dir)