"""
Benchmarks module for ISA Model evaluation framework.

Contains benchmark implementations and dataset loaders.
"""

from .multimodal_datasets import (
    VQAv2Dataset,
    COCOCaptionsDataset,
    DocVQADataset,
    AudioDatasetLoader,
    create_vqa_dataset,
    create_coco_captions_dataset,
    create_docvqa_dataset,
    create_audio_dataset_loader
)

__all__ = [
    "VQAv2Dataset",
    "COCOCaptionsDataset", 
    "DocVQADataset",
    "AudioDatasetLoader",
    "create_vqa_dataset",
    "create_coco_captions_dataset",
    "create_docvqa_dataset",
    "create_audio_dataset_loader"
]