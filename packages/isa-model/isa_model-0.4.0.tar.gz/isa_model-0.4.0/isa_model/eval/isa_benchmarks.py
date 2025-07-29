"""
ISA Model Service Benchmarks.

Specialized benchmarks for evaluating ISA custom services:
- Modal deployment performance
- Cost-effectiveness analysis  
- GPU utilization testing
- Service reliability and scalability
- Cross-service comparison
"""

import asyncio
import logging
import time
import statistics
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

from .isa_integration import ISAModelInterface
from .evaluators.base_evaluator import BaseEvaluator, EvaluationResult

logger = logging.getLogger(__name__)


@dataclass
class ServicePerformanceMetrics:
    """Performance metrics for ISA services."""
    service_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput_rps: float  # Requests per second
    total_cost_usd: float
    cost_per_request_usd: float
    gpu_utilization_percent: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    error_rate: float = 0.0


class ISAServiceBenchmark:
    """
    Comprehensive benchmark suite for ISA services.
    
    Tests performance, cost, reliability, and scalability of:
    - ISA OCR Service (Surya OCR)
    - ISA Vision Services (Qwen2.5-VL, Table extraction)
    - ISA Audio SOTA Service
    - ISA Embedding & Reranking Service
    - ISA Video Generation Service
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize ISA service benchmark."""
        self.config = config or {}
        self.interface = ISAModelInterface(config)
        
        # Benchmark configuration
        self.test_duration_seconds = self.config.get("test_duration_seconds", 60)
        self.max_concurrent_requests = self.config.get("max_concurrent_requests", 10)
        self.warmup_requests = self.config.get("warmup_requests", 5)
        
        # Service configurations
        self.services_to_test = self.config.get("services_to_test", [
            "isa_ocr_service",
            "isa_vision_qwen25_service", 
            "isa_audio_sota_service",
            "isa_embedding_reranking_service"
        ])
        
        # Test data
        self.test_samples = self._prepare_test_samples()
    
    def _prepare_test_samples(self) -> Dict[str, List[Dict[str, Any]]]:
        """Prepare test samples for different service types."""
        samples = {
            "ocr": [
                {"text": "Sample OCR text for performance testing", "complexity": "simple"},
                {"text": "More complex OCR text with special characters: éñ中文", "complexity": "medium"},
                {"text": "Very complex OCR text with multiple languages and formatting", "complexity": "complex"}
            ],
            "vision_vqa": [
                {"question": "What color is the object?", "complexity": "simple"},
                {"question": "Describe the scene in detail", "complexity": "medium"},
                {"question": "Analyze the complex relationships in this image", "complexity": "complex"}
            ],
            "audio_stt": [
                {"duration": 5, "content": "Short audio clip", "complexity": "simple"},
                {"duration": 30, "content": "Medium length audio", "complexity": "medium"},
                {"duration": 120, "content": "Long audio clip", "complexity": "complex"}
            ],
            "embedding": [
                {"text": "Short text for embedding", "length": "short"},
                {"text": "Medium length text for embedding testing with more content", "length": "medium"},
                {"text": "Very long text for embedding testing " * 20, "length": "long"}
            ]
        }
        return samples
    
    async def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive benchmark across all ISA services."""
        logger.info("Starting comprehensive ISA service benchmark")
        
        results = {
            "benchmark_start_time": datetime.now().isoformat(),
            "config": self.config,
            "service_results": {},
            "comparative_analysis": {},
            "summary": {}
        }
        
        # Test each service
        for service_name in self.services_to_test:
            logger.info(f"Benchmarking {service_name}")
            try:
                service_results = await self._benchmark_service(service_name)
                results["service_results"][service_name] = service_results
            except Exception as e:
                logger.error(f"Error benchmarking {service_name}: {e}")
                results["service_results"][service_name] = {"error": str(e)}
        
        # Comparative analysis
        results["comparative_analysis"] = self._perform_comparative_analysis(
            results["service_results"]
        )
        
        # Summary
        results["summary"] = self._generate_summary(results["service_results"])
        
        results["benchmark_end_time"] = datetime.now().isoformat()
        
        logger.info("Comprehensive benchmark completed")
        return results
    
    async def _benchmark_service(self, service_name: str) -> Dict[str, Any]:
        """Benchmark a specific ISA service."""
        service_type = self._get_service_type(service_name)
        test_samples = self.test_samples.get(service_type, [])
        
        if not test_samples:
            logger.warning(f"No test samples for service type: {service_type}")
            return {"error": "No test samples available"}
        
        # Warmup
        await self._warmup_service(service_name, test_samples[:self.warmup_requests])
        
        # Performance testing
        performance_results = await self._run_performance_test(service_name, test_samples)
        
        # Load testing  
        load_results = await self._run_load_test(service_name, test_samples)
        
        # Reliability testing
        reliability_results = await self._run_reliability_test(service_name, test_samples)
        
        # Cost analysis
        cost_analysis = self._analyze_costs(performance_results, load_results)
        
        return {
            "service_name": service_name,
            "service_type": service_type,
            "performance_test": performance_results,
            "load_test": load_results,
            "reliability_test": reliability_results,
            "cost_analysis": cost_analysis,
            "overall_metrics": self._calculate_overall_metrics(
                performance_results, load_results, reliability_results
            )
        }
    
    def _get_service_type(self, service_name: str) -> str:
        """Map service name to service type."""
        mapping = {
            "isa_ocr_service": "ocr",
            "isa_vision_qwen25_service": "vision_vqa",
            "isa_audio_sota_service": "audio_stt", 
            "isa_embedding_reranking_service": "embedding"
        }
        return mapping.get(service_name, "unknown")
    
    async def _warmup_service(self, service_name: str, samples: List[Dict[str, Any]]):
        """Warm up the service with initial requests."""
        logger.info(f"Warming up {service_name}")
        
        for sample in samples:
            try:
                await self._make_service_request(service_name, sample)
                await asyncio.sleep(0.5)  # Brief pause between warmup requests
            except Exception as e:
                logger.warning(f"Warmup request failed: {e}")
    
    async def _run_performance_test(self, service_name: str, samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run performance test measuring latency and accuracy."""
        logger.info(f"Running performance test for {service_name}")
        
        results = {
            "test_type": "performance",
            "requests": [],
            "metrics": {}
        }
        
        # Test each sample type
        for sample in samples:
            for _ in range(5):  # 5 requests per sample type
                start_time = time.time()
                try:
                    response = await self._make_service_request(service_name, sample)
                    latency = (time.time() - start_time) * 1000  # Convert to milliseconds
                    
                    request_result = {
                        "success": True,
                        "latency_ms": latency,
                        "sample_complexity": sample.get("complexity", "unknown"),
                        "response_size": len(str(response)),
                        "cost_estimate": response.get("cost_usd", 0.0)
                    }
                    
                except Exception as e:
                    request_result = {
                        "success": False,
                        "error": str(e),
                        "latency_ms": (time.time() - start_time) * 1000,
                        "sample_complexity": sample.get("complexity", "unknown")
                    }
                
                results["requests"].append(request_result)
        
        # Calculate metrics
        successful_requests = [r for r in results["requests"] if r["success"]]
        failed_requests = [r for r in results["requests"] if not r["success"]]
        
        if successful_requests:
            latencies = [r["latency_ms"] for r in successful_requests]
            costs = [r.get("cost_estimate", 0.0) for r in successful_requests]
            
            results["metrics"] = {
                "total_requests": len(results["requests"]),
                "successful_requests": len(successful_requests),
                "failed_requests": len(failed_requests),
                "success_rate": len(successful_requests) / len(results["requests"]),
                "avg_latency_ms": statistics.mean(latencies),
                "median_latency_ms": statistics.median(latencies),
                "p95_latency_ms": self._percentile(latencies, 95),
                "p99_latency_ms": self._percentile(latencies, 99),
                "min_latency_ms": min(latencies),
                "max_latency_ms": max(latencies),
                "total_cost_usd": sum(costs),
                "avg_cost_per_request": statistics.mean(costs) if costs else 0.0
            }
        else:
            results["metrics"] = {
                "total_requests": len(results["requests"]),
                "successful_requests": 0,
                "failed_requests": len(failed_requests),
                "success_rate": 0.0,
                "error": "All requests failed"
            }
        
        return results
    
    async def _run_load_test(self, service_name: str, samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run load test to measure throughput and scalability."""
        logger.info(f"Running load test for {service_name}")
        
        results = {
            "test_type": "load",
            "test_duration_seconds": self.test_duration_seconds,
            "max_concurrent_requests": self.max_concurrent_requests,
            "requests": [],
            "metrics": {}
        }
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        
        start_time = time.time()
        end_time = start_time + self.test_duration_seconds
        
        async def make_request():
            async with semaphore:
                sample = samples[len(results["requests"]) % len(samples)]
                request_start = time.time()
                
                try:
                    response = await self._make_service_request(service_name, sample)
                    latency = (time.time() - request_start) * 1000
                    
                    return {
                        "success": True,
                        "latency_ms": latency,
                        "timestamp": request_start,
                        "cost_estimate": response.get("cost_usd", 0.0)
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "error": str(e),
                        "latency_ms": (time.time() - request_start) * 1000,
                        "timestamp": request_start
                    }
        
        # Generate load
        tasks = []
        while time.time() < end_time:
            if len(tasks) < self.max_concurrent_requests:
                task = asyncio.create_task(make_request())
                tasks.append(task)
            
            # Collect completed tasks
            done_tasks = [task for task in tasks if task.done()]
            for task in done_tasks:
                try:
                    result = await task
                    results["requests"].append(result)
                except Exception as e:
                    logger.error(f"Task error: {e}")
                tasks.remove(task)
            
            await asyncio.sleep(0.1)  # Brief pause
        
        # Wait for remaining tasks
        if tasks:
            remaining_results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in remaining_results:
                if isinstance(result, dict):
                    results["requests"].append(result)
        
        # Calculate load test metrics
        if results["requests"]:
            successful_requests = [r for r in results["requests"] if r["success"]]
            total_time = time.time() - start_time
            
            results["metrics"] = {
                "total_requests": len(results["requests"]),
                "successful_requests": len(successful_requests),
                "failed_requests": len(results["requests"]) - len(successful_requests),
                "success_rate": len(successful_requests) / len(results["requests"]),
                "throughput_rps": len(results["requests"]) / total_time,
                "successful_throughput_rps": len(successful_requests) / total_time,
                "actual_test_duration": total_time,
                "concurrent_requests_achieved": min(self.max_concurrent_requests, len(results["requests"]))
            }
            
            if successful_requests:
                latencies = [r["latency_ms"] for r in successful_requests]
                results["metrics"].update({
                    "avg_latency_ms": statistics.mean(latencies),
                    "p95_latency_ms": self._percentile(latencies, 95),
                    "p99_latency_ms": self._percentile(latencies, 99)
                })
        
        return results
    
    async def _run_reliability_test(self, service_name: str, samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run reliability test to measure service stability."""
        logger.info(f"Running reliability test for {service_name}")
        
        results = {
            "test_type": "reliability",
            "test_scenarios": [],
            "metrics": {}
        }
        
        # Test different reliability scenarios
        scenarios = [
            {"name": "consecutive_requests", "description": "100 consecutive requests"},
            {"name": "burst_requests", "description": "Burst of 20 concurrent requests"},
            {"name": "mixed_complexity", "description": "Mixed complexity requests"}
        ]
        
        for scenario in scenarios:
            scenario_results = await self._run_reliability_scenario(service_name, samples, scenario)
            results["test_scenarios"].append(scenario_results)
        
        # Calculate overall reliability metrics
        all_requests = []
        for scenario in results["test_scenarios"]:
            all_requests.extend(scenario.get("requests", []))
        
        if all_requests:
            successful = [r for r in all_requests if r["success"]]
            results["metrics"] = {
                "total_reliability_requests": len(all_requests),
                "successful_reliability_requests": len(successful),
                "overall_reliability_rate": len(successful) / len(all_requests),
                "failure_types": self._analyze_failure_types(all_requests)
            }
        
        return results
    
    async def _run_reliability_scenario(self, service_name: str, samples: List[Dict[str, Any]], scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a specific reliability scenario."""
        scenario_results = {
            "scenario": scenario,
            "requests": [],
            "metrics": {}
        }
        
        if scenario["name"] == "consecutive_requests":
            # 100 consecutive requests
            for i in range(100):
                sample = samples[i % len(samples)]
                try:
                    start_time = time.time()
                    response = await self._make_service_request(service_name, sample)
                    latency = (time.time() - start_time) * 1000
                    
                    scenario_results["requests"].append({
                        "success": True,
                        "request_number": i,
                        "latency_ms": latency
                    })
                except Exception as e:
                    scenario_results["requests"].append({
                        "success": False,
                        "request_number": i,
                        "error": str(e)
                    })
        
        elif scenario["name"] == "burst_requests":
            # 20 concurrent requests
            tasks = []
            for i in range(20):
                sample = samples[i % len(samples)]
                task = asyncio.create_task(self._make_service_request(service_name, sample))
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    scenario_results["requests"].append({
                        "success": False,
                        "request_number": i,
                        "error": str(result)
                    })
                else:
                    scenario_results["requests"].append({
                        "success": True,
                        "request_number": i,
                        "response": result
                    })
        
        elif scenario["name"] == "mixed_complexity":
            # Mix of different complexity samples
            for _ in range(30):
                for sample in samples:  # Test each complexity
                    try:
                        start_time = time.time()
                        response = await self._make_service_request(service_name, sample)
                        latency = (time.time() - start_time) * 1000
                        
                        scenario_results["requests"].append({
                            "success": True,
                            "complexity": sample.get("complexity", "unknown"),
                            "latency_ms": latency
                        })
                    except Exception as e:
                        scenario_results["requests"].append({
                            "success": False,
                            "complexity": sample.get("complexity", "unknown"),
                            "error": str(e)
                        })
        
        # Calculate scenario metrics
        successful = [r for r in scenario_results["requests"] if r["success"]]
        scenario_results["metrics"] = {
            "total_requests": len(scenario_results["requests"]),
            "successful_requests": len(successful),
            "success_rate": len(successful) / len(scenario_results["requests"]) if scenario_results["requests"] else 0
        }
        
        return scenario_results
    
    async def _make_service_request(self, service_name: str, sample: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to a specific ISA service."""
        service_type = self._get_service_type(service_name)
        
        if service_type == "ocr":
            # Mock image for OCR testing
            return await self.interface.vision_analysis(
                image="mock_image_data",
                task_type="ocr",
                model_name="isa-surya-ocr-service"
            )
        
        elif service_type == "vision_vqa":
            return await self.interface.vision_analysis(
                image="mock_image_data",
                prompt=sample["question"],
                task_type="vqa",
                model_name="isa-qwen25-vision-service"
            )
        
        elif service_type == "audio_stt":
            return await self.interface.audio_processing(
                audio="mock_audio_data",
                task_type="stt",
                model_name="isa_audio_sota_service"
            )
        
        elif service_type == "embedding":
            return await self.interface.embedding_generation(
                text=sample["text"],
                model_name="isa-jina-reranker-v2-service"
            )
        
        else:
            raise ValueError(f"Unknown service type: {service_type}")
    
    def _analyze_costs(self, performance_results: Dict[str, Any], load_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cost-effectiveness of the service."""
        analysis = {
            "cost_breakdown": {},
            "cost_efficiency": {},
            "recommendations": []
        }
        
        # Extract cost data
        perf_costs = []
        load_costs = []
        
        for request in performance_results.get("requests", []):
            if request.get("success") and "cost_estimate" in request:
                perf_costs.append(request["cost_estimate"])
        
        for request in load_results.get("requests", []):
            if request.get("success") and "cost_estimate" in request:
                load_costs.append(request["cost_estimate"])
        
        all_costs = perf_costs + load_costs
        
        if all_costs:
            analysis["cost_breakdown"] = {
                "total_estimated_cost": sum(all_costs),
                "avg_cost_per_request": statistics.mean(all_costs),
                "min_cost_per_request": min(all_costs),
                "max_cost_per_request": max(all_costs),
                "cost_variance": statistics.variance(all_costs) if len(all_costs) > 1 else 0
            }
            
            # Cost efficiency analysis
            perf_metrics = performance_results.get("metrics", {})
            load_metrics = load_results.get("metrics", {})
            
            avg_latency = perf_metrics.get("avg_latency_ms", 0)
            throughput = load_metrics.get("throughput_rps", 0)
            
            if avg_latency > 0 and throughput > 0:
                analysis["cost_efficiency"] = {
                    "cost_per_second_latency": statistics.mean(all_costs) / (avg_latency / 1000),
                    "cost_per_rps": statistics.mean(all_costs) * throughput,
                    "efficiency_score": throughput / (statistics.mean(all_costs) * avg_latency) if avg_latency > 0 else 0
                }
        
        return analysis
    
    def _calculate_overall_metrics(self, performance: Dict, load: Dict, reliability: Dict) -> ServicePerformanceMetrics:
        """Calculate overall service performance metrics."""
        perf_metrics = performance.get("metrics", {})
        load_metrics = load.get("metrics", {})
        reliability_metrics = reliability.get("metrics", {})
        
        return ServicePerformanceMetrics(
            service_name=performance.get("service_name", "unknown"),
            total_requests=perf_metrics.get("total_requests", 0) + load_metrics.get("total_requests", 0),
            successful_requests=perf_metrics.get("successful_requests", 0) + load_metrics.get("successful_requests", 0),
            failed_requests=perf_metrics.get("failed_requests", 0) + load_metrics.get("failed_requests", 0),
            avg_latency_ms=perf_metrics.get("avg_latency_ms", 0),
            p95_latency_ms=perf_metrics.get("p95_latency_ms", 0),
            p99_latency_ms=perf_metrics.get("p99_latency_ms", 0),
            throughput_rps=load_metrics.get("throughput_rps", 0),
            total_cost_usd=perf_metrics.get("total_cost_usd", 0),
            cost_per_request_usd=perf_metrics.get("avg_cost_per_request", 0),
            error_rate=1 - reliability_metrics.get("overall_reliability_rate", 1)
        )
    
    def _perform_comparative_analysis(self, service_results: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comparative analysis across services."""
        analysis = {
            "performance_comparison": {},
            "cost_comparison": {},
            "reliability_comparison": {},
            "recommendations": []
        }
        
        services = list(service_results.keys())
        
        # Performance comparison
        performance_data = {}
        for service in services:
            if "error" not in service_results[service]:
                metrics = service_results[service].get("overall_metrics")
                if metrics:
                    performance_data[service] = {
                        "avg_latency_ms": metrics.avg_latency_ms,
                        "throughput_rps": metrics.throughput_rps,
                        "success_rate": 1 - metrics.error_rate
                    }
        
        analysis["performance_comparison"] = performance_data
        
        # Cost comparison
        cost_data = {}
        for service in services:
            if "error" not in service_results[service]:
                metrics = service_results[service].get("overall_metrics")
                if metrics:
                    cost_data[service] = {
                        "cost_per_request": metrics.cost_per_request_usd,
                        "total_cost": metrics.total_cost_usd
                    }
        
        analysis["cost_comparison"] = cost_data
        
        # Generate recommendations
        if performance_data:
            fastest_service = min(performance_data.keys(), key=lambda x: performance_data[x]["avg_latency_ms"])
            highest_throughput = max(performance_data.keys(), key=lambda x: performance_data[x]["throughput_rps"])
            
            analysis["recommendations"].extend([
                f"Fastest response time: {fastest_service}",
                f"Highest throughput: {highest_throughput}"
            ])
        
        if cost_data:
            most_cost_effective = min(cost_data.keys(), key=lambda x: cost_data[x]["cost_per_request"])
            analysis["recommendations"].append(f"Most cost-effective: {most_cost_effective}")
        
        return analysis
    
    def _generate_summary(self, service_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate benchmark summary."""
        summary = {
            "total_services_tested": len(service_results),
            "successful_services": len([s for s in service_results.values() if "error" not in s]),
            "failed_services": len([s for s in service_results.values() if "error" in s]),
            "overall_performance": {},
            "key_findings": []
        }
        
        # Calculate overall performance across all services
        all_latencies = []
        all_throughputs = []
        all_costs = []
        
        for service_name, results in service_results.items():
            if "error" not in results:
                metrics = results.get("overall_metrics")
                if metrics:
                    all_latencies.append(metrics.avg_latency_ms)
                    all_throughputs.append(metrics.throughput_rps)
                    all_costs.append(metrics.cost_per_request_usd)
        
        if all_latencies:
            summary["overall_performance"] = {
                "avg_latency_across_services": statistics.mean(all_latencies),
                "avg_throughput_across_services": statistics.mean(all_throughputs),
                "avg_cost_across_services": statistics.mean(all_costs) if all_costs else 0
            }
        
        return summary
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _analyze_failure_types(self, requests: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze types of failures."""
        failure_types = {}
        for request in requests:
            if not request.get("success"):
                error = request.get("error", "unknown_error")
                # Categorize error types
                if "timeout" in error.lower():
                    error_type = "timeout"
                elif "connection" in error.lower():
                    error_type = "connection_error"
                elif "rate limit" in error.lower():
                    error_type = "rate_limit"
                else:
                    error_type = "other_error"
                
                failure_types[error_type] = failure_types.get(error_type, 0) + 1
        
        return failure_types


# Convenience function for running ISA benchmarks
async def run_isa_service_benchmark(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run comprehensive ISA service benchmark."""
    benchmark = ISAServiceBenchmark(config)
    return await benchmark.run_comprehensive_benchmark()