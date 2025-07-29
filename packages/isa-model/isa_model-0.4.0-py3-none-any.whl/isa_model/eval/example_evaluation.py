"""
Example evaluation script demonstrating the ISA Model evaluation framework.

Shows how to:
1. Evaluate standard benchmarks (MMLU, HellaSwag, etc.)
2. Test ISA custom services
3. Run multimodal evaluations
4. Perform comprehensive service benchmarking
"""

import asyncio
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Import evaluation components
from .benchmarks import create_mmlu_benchmark, create_gsm8k_benchmark
from .benchmarks.multimodal_datasets import create_vqa_dataset, create_coco_captions_dataset
from .evaluators import LLMEvaluator, VisionEvaluator, AudioEvaluator, EmbeddingEvaluator
from .isa_integration import ISAModelInterface
from .isa_benchmarks import run_isa_service_benchmark
from .factory import EvaluationFactory

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_standard_llm_evaluation():
    """Example: Run standard LLM evaluation on MMLU and GSM8K."""
    logger.info("🚀 Running Standard LLM Evaluation")
    
    # Create evaluator
    evaluator = LLMEvaluator(config={
        "max_concurrent_requests": 5,
        "batch_size": 10
    })
    
    # Create ISA model interface
    model_interface = ISAModelInterface()
    
    # Test MMLU
    logger.info("📚 Testing MMLU benchmark")
    mmlu_benchmark = create_mmlu_benchmark(subjects=["anatomy", "astronomy", "business_ethics"])
    mmlu_data = mmlu_benchmark.load_data(max_samples=20)
    
    mmlu_result = await evaluator.evaluate(
        model_interface=model_interface,
        dataset=mmlu_data,
        dataset_name="MMLU",
        model_name="gpt-4.1-nano"
    )
    
    logger.info(f"MMLU Results: {mmlu_result.get_summary()}")
    
    # Test GSM8K
    logger.info("🧮 Testing GSM8K benchmark")
    gsm8k_benchmark = create_gsm8k_benchmark()
    gsm8k_data = gsm8k_benchmark.load_data(max_samples=10)
    
    gsm8k_result = await evaluator.evaluate(
        model_interface=model_interface,
        dataset=gsm8k_data,
        dataset_name="GSM8K",
        model_name="gpt-4.1-nano"
    )
    
    logger.info(f"GSM8K Results: {gsm8k_result.get_summary()}")
    
    return {
        "mmlu": mmlu_result.to_dict(),
        "gsm8k": gsm8k_result.to_dict()
    }


async def run_vision_evaluation():
    """Example: Run vision evaluation with VQA and image captioning."""
    logger.info("👁️ Running Vision Evaluation")
    
    # Create vision evaluator
    evaluator = VisionEvaluator(config={
        "task_type": "vqa",
        "max_image_size": (1024, 1024)
    })
    
    # Create ISA model interface
    model_interface = ISAModelInterface()
    
    # Test VQA
    logger.info("❓ Testing VQA dataset")
    vqa_dataset = create_vqa_dataset()
    vqa_data = vqa_dataset.load_data(max_samples=10, use_real_data=False)  # Use placeholder for demo
    
    vqa_result = await evaluator.evaluate(
        model_interface=model_interface,
        dataset=vqa_data,
        dataset_name="VQA_v2",
        model_name="gpt-4.1-mini"
    )
    
    logger.info(f"VQA Results: {vqa_result.get_summary()}")
    
    # Test Image Captioning
    logger.info("🖼️ Testing Image Captioning")
    caption_evaluator = VisionEvaluator(config={"task_type": "caption"})
    
    coco_dataset = create_coco_captions_dataset()
    caption_data = coco_dataset.load_data(max_samples=5, use_real_data=False)
    
    caption_result = await caption_evaluator.evaluate(
        model_interface=model_interface,
        dataset=caption_data,
        dataset_name="COCO_Captions",
        model_name="gpt-4.1-mini"
    )
    
    logger.info(f"Caption Results: {caption_result.get_summary()}")
    
    return {
        "vqa": vqa_result.to_dict(),
        "captioning": caption_result.to_dict()
    }


async def run_audio_evaluation():
    """Example: Run audio evaluation for STT and emotion recognition."""
    logger.info("🎵 Running Audio Evaluation")
    
    # STT Evaluation
    stt_evaluator = AudioEvaluator(config={
        "task_type": "stt",
        "normalize_text": True,
        "case_sensitive": False
    })
    
    model_interface = ISAModelInterface()
    
    # Create mock STT dataset
    stt_data = [
        {
            "audio": "mock_audio_1.wav",
            "expected_output": "The quick brown fox jumps over the lazy dog",
            "task_type": "stt",
            "id": "stt_test_1"
        },
        {
            "audio": "mock_audio_2.wav", 
            "expected_output": "Machine learning is transforming artificial intelligence",
            "task_type": "stt",
            "id": "stt_test_2"
        }
    ]
    
    stt_result = await stt_evaluator.evaluate(
        model_interface=model_interface,
        dataset=stt_data,
        dataset_name="LibriSpeech_Test",
        model_name="isa_audio_sota_service"
    )
    
    logger.info(f"STT Results: {stt_result.get_summary()}")
    
    # Emotion Recognition Evaluation
    emotion_evaluator = AudioEvaluator(config={"task_type": "emotion"})
    
    emotion_data = [
        {
            "audio": "mock_emotion_1.wav",
            "expected_output": "happy",
            "task_type": "emotion",
            "id": "emotion_test_1"
        },
        {
            "audio": "mock_emotion_2.wav",
            "expected_output": "sad", 
            "task_type": "emotion",
            "id": "emotion_test_2"
        }
    ]
    
    emotion_result = await emotion_evaluator.evaluate(
        model_interface=model_interface,
        dataset=emotion_data,
        dataset_name="Emotion_Test",
        model_name="isa_audio_sota_service"
    )
    
    logger.info(f"Emotion Results: {emotion_result.get_summary()}")
    
    return {
        "stt": stt_result.to_dict(),
        "emotion": emotion_result.to_dict()
    }


async def run_embedding_evaluation():
    """Example: Run embedding evaluation for similarity and retrieval."""
    logger.info("🔍 Running Embedding Evaluation")
    
    # Similarity Evaluation
    similarity_evaluator = EmbeddingEvaluator(config={
        "task_type": "similarity",
        "similarity_metric": "cosine"
    })
    
    model_interface = ISAModelInterface()
    
    # Create similarity dataset
    similarity_data = [
        {
            "text1": "The cat is sleeping on the couch",
            "text2": "A feline is resting on the sofa",
            "expected_output": 0.8,  # High similarity
            "task_type": "similarity",
            "id": "sim_test_1"
        },
        {
            "text1": "I love pizza",
            "text2": "The weather is sunny today",
            "expected_output": 0.1,  # Low similarity
            "task_type": "similarity", 
            "id": "sim_test_2"
        }
    ]
    
    similarity_result = await similarity_evaluator.evaluate(
        model_interface=model_interface,
        dataset=similarity_data,
        dataset_name="Similarity_Test",
        model_name="text-embedding-3-small"
    )
    
    logger.info(f"Similarity Results: {similarity_result.get_summary()}")
    
    # Retrieval Evaluation
    retrieval_evaluator = EmbeddingEvaluator(config={
        "task_type": "retrieval",
        "k_values": [1, 3, 5]
    })
    
    retrieval_data = [
        {
            "query": "machine learning algorithms",
            "documents": [
                "Neural networks are a type of machine learning algorithm",
                "The weather is nice today",
                "Deep learning uses artificial neural networks",
                "I like to cook pasta"
            ],
            "expected_output": [1, 0, 1, 0],  # Relevance labels
            "task_type": "retrieval",
            "id": "retrieval_test_1"
        }
    ]
    
    retrieval_result = await retrieval_evaluator.evaluate(
        model_interface=model_interface,
        dataset=retrieval_data,
        dataset_name="Retrieval_Test",
        model_name="text-embedding-3-small"
    )
    
    logger.info(f"Retrieval Results: {retrieval_result.get_summary()}")
    
    return {
        "similarity": similarity_result.to_dict(),
        "retrieval": retrieval_result.to_dict()
    }


async def run_isa_service_benchmark_example():
    """Example: Run comprehensive ISA service benchmarking."""
    logger.info("⚡ Running ISA Service Benchmark")
    
    benchmark_config = {
        "test_duration_seconds": 30,  # Short test for demo
        "max_concurrent_requests": 5,
        "warmup_requests": 3,
        "services_to_test": [
            "isa_ocr_service",
            "isa_audio_sota_service",
            "isa_embedding_reranking_service"
        ]
    }
    
    benchmark_results = await run_isa_service_benchmark(benchmark_config)
    
    logger.info("📊 ISA Service Benchmark Summary:")
    summary = benchmark_results.get("summary", {})
    logger.info(f"Services tested: {summary.get('total_services_tested', 0)}")
    logger.info(f"Successful services: {summary.get('successful_services', 0)}")
    
    # Log performance highlights
    comparative = benchmark_results.get("comparative_analysis", {})
    recommendations = comparative.get("recommendations", [])
    for rec in recommendations:
        logger.info(f"💡 {rec}")
    
    return benchmark_results


async def run_factory_evaluation():
    """Example: Use EvaluationFactory for simplified multi-model comparison."""
    logger.info("🏭 Running Factory-based Multi-Model Evaluation")
    
    factory = EvaluationFactory()
    
    # Define models to compare
    models = [
        {"name": "gpt-4.1-nano", "provider": "openai"},
        {"name": "llama3.2:3b-instruct-fp16", "provider": "ollama"},
        {"name": "claude-sonnet-4-20250514", "provider": "yyds"}
    ]
    
    # Create simple test dataset
    test_data = [
        {
            "input": "What is 2+2?",
            "output": "4",
            "id": "math_test_1"
        },
        {
            "input": "Name the capital of France.",
            "output": "Paris",
            "id": "geography_test_1"
        }
    ]
    
    # Run comparison
    comparison_results = await factory.compare_models(
        models=models,
        dataset=test_data,
        evaluator_type="llm",
        metrics=["accuracy", "f1_score", "latency"]
    )
    
    logger.info("📈 Model Comparison Results:")
    for model_name, results in comparison_results.items():
        metrics = results.get("metrics", {})
        logger.info(f"{model_name}: Accuracy={metrics.get('accuracy', 0):.3f}, "
                   f"F1={metrics.get('f1_score', 0):.3f}")
    
    return comparison_results


async def save_results(results: Dict[str, Any], output_file: str = "evaluation_results.json"):
    """Save evaluation results to file."""
    output_path = Path(output_file)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    logger.info(f"💾 Results saved to {output_path}")


async def main():
    """Run comprehensive evaluation examples."""
    logger.info("🔬 Starting ISA Model Evaluation Framework Demo")
    
    results = {}
    
    try:
        # Run all evaluation examples
        results["llm_evaluation"] = await run_standard_llm_evaluation()
        results["vision_evaluation"] = await run_vision_evaluation()
        results["audio_evaluation"] = await run_audio_evaluation()
        results["embedding_evaluation"] = await run_embedding_evaluation()
        results["isa_benchmarks"] = await run_isa_service_benchmark_example()
        results["factory_comparison"] = await run_factory_evaluation()
        
        # Save results
        await save_results(results)
        
        logger.info("✅ All evaluations completed successfully!")
        
        # Print summary
        logger.info("\n📋 Evaluation Summary:")
        logger.info(f"- LLM evaluations: {len(results['llm_evaluation'])} benchmarks")
        logger.info(f"- Vision evaluations: {len(results['vision_evaluation'])} tasks")
        logger.info(f"- Audio evaluations: {len(results['audio_evaluation'])} tasks")
        logger.info(f"- Embedding evaluations: {len(results['embedding_evaluation'])} tasks")
        logger.info(f"- ISA service benchmarks: {results['isa_benchmarks']['summary']['total_services_tested']} services")
        logger.info(f"- Model comparisons: {len(results['factory_comparison'])} models")
        
    except Exception as e:
        logger.error(f"❌ Evaluation failed: {e}")
        raise
    
    return results


if __name__ == "__main__":
    # Run the evaluation demo
    asyncio.run(main())