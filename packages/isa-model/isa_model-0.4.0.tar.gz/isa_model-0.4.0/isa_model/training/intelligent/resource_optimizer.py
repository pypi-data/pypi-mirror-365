"""
Resource Optimization System for Training

This module provides intelligent resource selection and cost optimization:
- GPU type selection based on model requirements
- Cloud provider comparison and selection
- Cost estimation and budget optimization
- Performance prediction and time estimation
- Resource availability monitoring

Optimizes for cost, performance, and availability based on user constraints.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)


@dataclass
class GPUSpec:
    """GPU specification and characteristics."""
    
    name: str
    memory_gb: int
    compute_capability: float
    
    # Performance characteristics
    fp16_tflops: float
    fp32_tflops: float
    memory_bandwidth_gbps: float
    
    # Cost (per hour in USD)
    cost_per_hour: float = 0.0
    
    # Availability
    availability_score: float = 1.0  # 0.0 to 1.0
    
    # Provider information
    providers: List[str] = field(default_factory=list)
    
    # Training characteristics
    training_efficiency: float = 1.0  # Relative efficiency for training
    power_efficiency: float = 1.0    # Performance per watt
    
    # Metadata
    is_recommended: bool = False
    description: str = ""


@dataclass
class CloudProvider:
    """Cloud provider specification."""
    
    name: str
    regions: List[str]
    
    # Available GPU types
    available_gpus: List[str]
    
    # Pricing model
    pricing_model: str = "hourly"  # "hourly", "spot", "reserved"
    
    # Features
    supports_spot_instances: bool = False
    supports_auto_scaling: bool = False
    supports_preemption: bool = False
    
    # Performance characteristics
    startup_time_minutes: float = 5.0
    network_performance: str = "standard"  # "low", "standard", "high"
    
    # Reliability
    availability_score: float = 0.99
    
    # Additional costs
    storage_cost_per_gb_hour: float = 0.0
    egress_cost_per_gb: float = 0.0
    
    description: str = ""


@dataclass
class ResourceRecommendation:
    """Resource optimization recommendation."""
    
    # Selected resources
    gpu: str
    cloud_provider: str
    region: str
    instance_type: str
    
    # Cost estimates
    estimated_cost: float
    cost_breakdown: Dict[str, float]
    
    # Performance estimates
    estimated_time: float  # hours
    performance_score: float
    
    # Configuration
    recommended_batch_size: int
    recommended_precision: str  # "fp16", "fp32", "bf16"
    
    # Alternatives
    alternatives: List[Dict[str, Any]]
    
    # Reasoning
    decision_factors: List[str]
    confidence: float
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)


class ResourceOptimizer:
    """
    Intelligent resource optimization system.
    
    This class analyzes training requirements and recommends optimal resources:
    - GPU selection based on model size and requirements
    - Cloud provider comparison for cost and performance
    - Cost estimation and budget optimization
    - Performance prediction and time estimation
    
    Example:
        ```python
        optimizer = ResourceOptimizer()
        
        recommendation = optimizer.optimize_resources(
            model_name="google/gemma-2-7b-it",
            training_config=config,
            budget_limit=100.0,
            time_limit=8
        )
        
        print(f"Recommended: {recommendation.gpu} on {recommendation.cloud_provider}")
        print(f"Cost: ${recommendation.estimated_cost:.2f}")
        ```
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize resource optimizer.
        
        Args:
            data_dir: Directory for storing resource data
        """
        self.data_dir = data_dir or os.path.join(os.getcwd(), "resource_data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize resource databases
        self.gpus: Dict[str, GPUSpec] = {}
        self.cloud_providers: Dict[str, CloudProvider] = {}
        self.pricing_cache: Dict[str, Dict[str, float]] = {}
        
        # Load resource data
        self._load_resource_data()
        
        # Initialize with defaults if empty
        if not self.gpus:
            self._initialize_default_resources()
        
        logger.info(f"Resource optimizer initialized with {len(self.gpus)} GPUs and {len(self.cloud_providers)} providers")
    
    def optimize_resources(
        self,
        model_name: str,
        training_config: Any,
        budget_limit: Optional[float] = None,
        time_limit: Optional[int] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> ResourceRecommendation:
        """
        Optimize resource selection for training requirements.
        
        Args:
            model_name: Name of the model to train
            training_config: Training configuration
            budget_limit: Maximum budget in USD
            time_limit: Maximum time in hours
            preferences: User preferences for GPU/cloud providers
            
        Returns:
            Optimal resource recommendation
        """
        preferences = preferences or {}
        
        logger.info(f"Optimizing resources for {model_name}")
        
        try:
            # Step 1: Analyze model requirements
            model_requirements = self._analyze_model_requirements(model_name, training_config)
            
            # Step 2: Filter compatible GPUs
            compatible_gpus = self._filter_compatible_gpus(model_requirements)
            
            # Step 3: Estimate costs and performance for each option
            gpu_options = []
            total_evaluated = 0
            total_filtered = 0
            
            for gpu_name in compatible_gpus:
                gpu_spec = self.gpus[gpu_name]
                
                # Get best provider for this GPU
                provider_options = self._get_provider_options(gpu_name, preferences)
                
                for provider_name, provider_spec, region, instance_type in provider_options:
                    total_evaluated += 1
                    option = self._evaluate_option(
                        gpu_spec, provider_spec, region, instance_type,
                        model_requirements, budget_limit, time_limit
                    )
                    
                    if option:
                        gpu_options.append(option)
                    else:
                        total_filtered += 1
            
            # Step 4: Rank options by overall score
            if not gpu_options:
                logger.warning(f"No compatible GPU options found. Evaluated {total_evaluated} options, {total_filtered} filtered by constraints.")
                logger.warning(f"Budget limit: {budget_limit}, Time limit: {time_limit}")
                raise ValueError("No compatible GPU options found")
            
            gpu_options.sort(key=lambda x: x["score"], reverse=True)
            
            # Step 5: Select best option
            best_option = gpu_options[0]
            
            # Step 6: Generate alternatives
            alternatives = self._generate_alternatives(gpu_options[1:5])  # Top 5 alternatives
            
            # Step 7: Create recommendation
            recommendation = ResourceRecommendation(
                gpu=best_option["gpu"],
                cloud_provider=best_option["provider"],
                region=best_option["region"],
                instance_type=best_option["instance_type"],
                estimated_cost=best_option["cost"],
                cost_breakdown=best_option["cost_breakdown"],
                estimated_time=best_option["time"],
                performance_score=best_option["performance"],
                recommended_batch_size=best_option["batch_size"],
                recommended_precision=best_option["precision"],
                alternatives=alternatives,
                decision_factors=best_option["reasons"],
                confidence=best_option["confidence"]
            )
            
            logger.info(f"Selected {recommendation.gpu} on {recommendation.cloud_provider} "
                       f"(${recommendation.estimated_cost:.2f}, {recommendation.estimated_time:.1f}h)")
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Resource optimization failed: {e}")
            raise
    
    def _analyze_model_requirements(self, model_name: str, training_config: Any) -> Dict[str, Any]:
        """Analyze model resource requirements."""
        requirements = {
            "min_memory_gb": 8,
            "recommended_memory_gb": 16,
            "compute_intensity": "medium",  # "low", "medium", "high"
            "precision": "fp16",
            "batch_size": getattr(training_config, 'batch_size', 4),
            "sequence_length": 1024,
            "model_size_gb": 4.0,
            "training_type": getattr(training_config, 'training_type', 'sft')
        }
        
        # Estimate model size and requirements based on name
        if "2b" in model_name.lower():
            requirements.update({
                "min_memory_gb": 6,  # Reduced for LoRA training
                "recommended_memory_gb": 10,
                "model_size_gb": 4.0,
                "compute_intensity": "medium"
            })
        elif "4b" in model_name.lower():
            requirements.update({
                "min_memory_gb": 8,  # Reduced for LoRA training
                "recommended_memory_gb": 12,
                "model_size_gb": 8.0,
                "compute_intensity": "medium"
            })
        elif "7b" in model_name.lower():
            requirements.update({
                "min_memory_gb": 12,  # Reduced for LoRA training
                "recommended_memory_gb": 16,
                "model_size_gb": 14.0,
                "compute_intensity": "high"
            })
        elif "13b" in model_name.lower():
            requirements.update({
                "min_memory_gb": 20,  # Reduced for LoRA training
                "recommended_memory_gb": 32,
                "model_size_gb": 26.0,
                "compute_intensity": "high"
            })
        
        # Adjust for LoRA training (most training uses LoRA)
        if hasattr(training_config, 'lora_config') and training_config.lora_config and training_config.lora_config.use_lora:
            requirements["min_memory_gb"] = int(requirements["min_memory_gb"] * 0.8)
            requirements["recommended_memory_gb"] = int(requirements["recommended_memory_gb"] * 0.9)
        else:
            # Assume LoRA by default for most efficient training
            requirements["min_memory_gb"] = int(requirements["min_memory_gb"] * 0.8)
            requirements["recommended_memory_gb"] = int(requirements["recommended_memory_gb"] * 0.9)
        
        # Adjust for batch size
        batch_size = requirements["batch_size"]
        if batch_size > 4:
            requirements["min_memory_gb"] = int(requirements["min_memory_gb"] * (1 + (batch_size - 4) * 0.15))
            requirements["recommended_memory_gb"] = int(requirements["recommended_memory_gb"] * (1 + (batch_size - 4) * 0.15))
        
        return requirements
    
    def _filter_compatible_gpus(self, requirements: Dict[str, Any]) -> List[str]:
        """Filter GPUs that meet the requirements."""
        compatible = []
        
        min_memory = requirements["min_memory_gb"]
        
        for gpu_name, gpu_spec in self.gpus.items():
            if gpu_spec.memory_gb >= min_memory:
                compatible.append(gpu_name)
        
        return compatible
    
    def _get_provider_options(self, gpu_name: str, preferences: Dict[str, Any]) -> List[Tuple[str, CloudProvider, str, str]]:
        """Get provider options for a GPU."""
        options = []
        gpu_spec = self.gpus[gpu_name]
        
        for provider_name in gpu_spec.providers:
            if provider_name in self.cloud_providers:
                provider_spec = self.cloud_providers[provider_name]
                
                # Skip if not in user preferences
                if preferences.get("cloud") and provider_name not in preferences["cloud"]:
                    continue
                
                # Get regions and instance types
                for region in provider_spec.regions[:2]:  # Limit to top 2 regions
                    instance_type = f"{gpu_name.lower().replace(' ', '-')}-instance"
                    options.append((provider_name, provider_spec, region, instance_type))
        
        return options
    
    def _evaluate_option(
        self,
        gpu_spec: GPUSpec,
        provider_spec: CloudProvider,
        region: str,
        instance_type: str,
        requirements: Dict[str, Any],
        budget_limit: Optional[float],
        time_limit: Optional[int]
    ) -> Optional[Dict[str, Any]]:
        """Evaluate a specific resource option."""
        
        # Estimate training time (more realistic for LoRA training)
        base_time = 3.0  # Base training time in hours for LoRA
        time_factor = 1.0 / gpu_spec.training_efficiency
        
        # Adjust base time for model size
        model_size_gb = requirements.get("model_size_gb", 8.0)
        if model_size_gb > 20:  # 13B+ models
            base_time = 6.0
        elif model_size_gb > 12:  # 7B models
            base_time = 4.0
        elif model_size_gb > 6:   # 4B models
            base_time = 3.0
        else:  # 2B models
            base_time = 2.0
        
        # Adjust for compute intensity
        if requirements["compute_intensity"] == "high":
            time_factor *= 1.3
        elif requirements["compute_intensity"] == "low":
            time_factor *= 0.8
        
        # Adjust for training type (LoRA is much faster)
        if requirements.get("training_type") == "sft":
            time_factor *= 0.7  # LoRA SFT is typically faster
        
        estimated_time = base_time * time_factor
        
        # Estimate costs
        compute_cost = gpu_spec.cost_per_hour * estimated_time
        storage_cost = provider_spec.storage_cost_per_gb_hour * 100 * estimated_time  # Assume 100GB storage
        
        total_cost = compute_cost + storage_cost
        
        # Check constraints
        if budget_limit and total_cost > budget_limit:
            return None
        
        if time_limit and estimated_time > time_limit:
            return None
        
        # Calculate performance score
        performance_score = self._calculate_performance_score(gpu_spec, requirements)
        
        # Calculate cost efficiency
        cost_efficiency = performance_score / total_cost if total_cost > 0 else 0
        
        # Calculate overall score
        score = self._calculate_overall_score(
            performance_score, cost_efficiency, gpu_spec, provider_spec, requirements
        )
        
        # Determine optimal batch size and precision
        batch_size = self._determine_optimal_batch_size(gpu_spec, requirements)
        precision = self._determine_optimal_precision(gpu_spec, requirements)
        
        # Generate reasons
        reasons = self._generate_option_reasons(gpu_spec, provider_spec, total_cost, estimated_time)
        
        return {
            "gpu": gpu_spec.name,
            "provider": provider_spec.name,
            "region": region,
            "instance_type": instance_type,
            "cost": total_cost,
            "cost_breakdown": {
                "compute": compute_cost,
                "storage": storage_cost
            },
            "time": estimated_time,
            "performance": performance_score,
            "batch_size": batch_size,
            "precision": precision,
            "score": score,
            "reasons": reasons,
            "confidence": min(1.0, score / 100.0)
        }
    
    def _calculate_performance_score(self, gpu_spec: GPUSpec, requirements: Dict[str, Any]) -> float:
        """Calculate performance score for a GPU."""
        score = 0.0
        
        # Memory adequacy
        memory_ratio = gpu_spec.memory_gb / requirements["recommended_memory_gb"]
        if memory_ratio >= 1.0:
            score += 30
        else:
            score += memory_ratio * 30
        
        # Compute performance
        if requirements["precision"] == "fp16":
            compute_score = min(30, gpu_spec.fp16_tflops / 100 * 30)
        else:
            compute_score = min(30, gpu_spec.fp32_tflops / 50 * 30)
        score += compute_score
        
        # Training efficiency
        score += gpu_spec.training_efficiency * 20
        
        # Memory bandwidth
        bandwidth_score = min(20, gpu_spec.memory_bandwidth_gbps / 1000 * 20)
        score += bandwidth_score
        
        return score
    
    def _calculate_overall_score(
        self,
        performance_score: float,
        cost_efficiency: float,
        gpu_spec: GPUSpec,
        provider_spec: CloudProvider,
        requirements: Dict[str, Any]
    ) -> float:
        """Calculate overall option score."""
        score = 0.0
        
        # Performance weight (40%)
        score += performance_score * 0.4
        
        # Cost efficiency weight (30%)
        score += cost_efficiency * 30 * 0.3
        
        # Availability weight (15%)
        score += gpu_spec.availability_score * provider_spec.availability_score * 15
        
        # Recommendation bonus (10%)
        if gpu_spec.is_recommended:
            score += 10
        
        # Provider reliability (5%)
        score += provider_spec.availability_score * 5
        
        return score
    
    def _determine_optimal_batch_size(self, gpu_spec: GPUSpec, requirements: Dict[str, Any]) -> int:
        """Determine optimal batch size for GPU."""
        base_batch_size = requirements["batch_size"]
        
        # Adjust based on GPU memory
        if gpu_spec.memory_gb >= 40:
            return min(base_batch_size * 4, 16)
        elif gpu_spec.memory_gb >= 24:
            return min(base_batch_size * 2, 8)
        elif gpu_spec.memory_gb >= 16:
            return base_batch_size
        else:
            return max(1, base_batch_size // 2)
    
    def _determine_optimal_precision(self, gpu_spec: GPUSpec, requirements: Dict[str, Any]) -> str:
        """Determine optimal precision for GPU."""
        # Prefer fp16 for modern GPUs with good fp16 performance
        if gpu_spec.fp16_tflops > gpu_spec.fp32_tflops * 1.5:
            return "fp16"
        else:
            return "fp32"
    
    def _generate_option_reasons(
        self, 
        gpu_spec: GPUSpec, 
        provider_spec: CloudProvider,
        cost: float, 
        time: float
    ) -> List[str]:
        """Generate reasons for selecting this option."""
        reasons = []
        
        reasons.append(f"{gpu_spec.name} provides {gpu_spec.memory_gb}GB memory")
        
        if gpu_spec.is_recommended:
            reasons.append("Recommended GPU for this model type")
        
        if cost < 50:
            reasons.append("Cost-effective option")
        elif cost < 100:
            reasons.append("Moderate cost option")
        
        if time < 5:
            reasons.append("Fast training time")
        elif time < 12:
            reasons.append("Reasonable training time")
        
        if provider_spec.availability_score > 0.95:
            reasons.append("High availability provider")
        
        return reasons
    
    def _generate_alternatives(self, options: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate alternative recommendations."""
        alternatives = []
        
        for option in options:
            alt = {
                "gpu": option["gpu"],
                "provider": option["provider"],
                "cost": option["cost"],
                "time": option["time"],
                "performance": option["performance"],
                "reason": f"Alternative option with different cost/performance tradeoff"
            }
            alternatives.append(alt)
        
        return alternatives
    
    def _initialize_default_resources(self) -> None:
        """Initialize with default GPU and cloud provider data."""
        self._add_default_gpus()
        self._add_default_cloud_providers()
        self._save_resource_data()
        
        logger.info("Initialized resource optimizer with default data")
    
    def _add_default_gpus(self) -> None:
        """Add default GPU specifications."""
        gpus = [
            GPUSpec(
                name="NVIDIA RTX A6000",
                memory_gb=48,
                compute_capability=8.6,
                fp16_tflops=150,
                fp32_tflops=38,
                memory_bandwidth_gbps=768,
                cost_per_hour=1.89,
                availability_score=0.8,
                providers=["runpod", "vast", "lambda"],
                training_efficiency=1.0,
                power_efficiency=0.9,
                is_recommended=True,
                description="High-memory professional GPU ideal for large models"
            ),
            GPUSpec(
                name="NVIDIA RTX 4090",
                memory_gb=24,
                compute_capability=8.9,
                fp16_tflops=165,
                fp32_tflops=83,
                memory_bandwidth_gbps=1008,
                cost_per_hour=1.25,
                availability_score=0.9,
                providers=["runpod", "vast"],
                training_efficiency=1.1,
                power_efficiency=1.0,
                is_recommended=True,
                description="Latest consumer GPU with excellent performance"
            ),
            GPUSpec(
                name="NVIDIA A100 40GB",
                memory_gb=40,
                compute_capability=8.0,
                fp16_tflops=312,
                fp32_tflops=19.5,
                memory_bandwidth_gbps=1555,
                cost_per_hour=2.95,
                availability_score=0.7,
                providers=["runpod", "aws", "gcp"],
                training_efficiency=1.2,
                power_efficiency=1.1,
                is_recommended=True,
                description="Data center GPU optimized for AI training"
            ),
            GPUSpec(
                name="NVIDIA RTX 3090",
                memory_gb=24,
                compute_capability=8.6,
                fp16_tflops=142,
                fp32_tflops=35.6,
                memory_bandwidth_gbps=936,
                cost_per_hour=0.89,
                availability_score=0.95,
                providers=["runpod", "vast", "lambda"],
                training_efficiency=0.9,
                power_efficiency=0.8,
                is_recommended=False,
                description="Previous generation high-memory consumer GPU"
            ),
            GPUSpec(
                name="NVIDIA RTX 4080",
                memory_gb=16,
                compute_capability=8.9,
                fp16_tflops=120,
                fp32_tflops=48.7,
                memory_bandwidth_gbps=716,
                cost_per_hour=0.95,
                availability_score=0.85,
                providers=["runpod", "vast"],
                training_efficiency=1.0,
                power_efficiency=1.0,
                is_recommended=False,
                description="Mid-range modern GPU for smaller models"
            ),
            GPUSpec(
                name="NVIDIA RTX 3080",
                memory_gb=10,
                compute_capability=8.6,
                fp16_tflops=119,
                fp32_tflops=29.8,
                memory_bandwidth_gbps=760,
                cost_per_hour=0.55,
                availability_score=0.9,
                providers=["runpod", "vast", "lambda"],
                training_efficiency=0.8,
                power_efficiency=0.8,
                is_recommended=False,
                description="Budget-friendly option for small models"
            )
        ]
        
        for gpu in gpus:
            self.gpus[gpu.name] = gpu
    
    def _add_default_cloud_providers(self) -> None:
        """Add default cloud provider specifications."""
        providers = [
            CloudProvider(
                name="runpod",
                regions=["US-East", "US-West", "EU-West"],
                available_gpus=["NVIDIA RTX A6000", "NVIDIA RTX 4090", "NVIDIA A100 40GB", "NVIDIA RTX 3090", "NVIDIA RTX 4080", "NVIDIA RTX 3080"],
                pricing_model="hourly",
                supports_spot_instances=True,
                supports_auto_scaling=False,
                supports_preemption=True,
                startup_time_minutes=2.0,
                network_performance="high",
                availability_score=0.95,
                storage_cost_per_gb_hour=0.0002,
                egress_cost_per_gb=0.02,
                description="Specialized GPU cloud for AI/ML workloads"
            ),
            CloudProvider(
                name="vast",
                regions=["Global"],
                available_gpus=["NVIDIA RTX A6000", "NVIDIA RTX 4090", "NVIDIA RTX 3090", "NVIDIA RTX 4080", "NVIDIA RTX 3080"],
                pricing_model="spot",
                supports_spot_instances=True,
                supports_auto_scaling=False,
                supports_preemption=True,
                startup_time_minutes=3.0,
                network_performance="standard",
                availability_score=0.85,
                storage_cost_per_gb_hour=0.0001,
                egress_cost_per_gb=0.01,
                description="Decentralized GPU marketplace with competitive pricing"
            ),
            CloudProvider(
                name="lambda",
                regions=["US-East", "US-West"],
                available_gpus=["NVIDIA RTX A6000", "NVIDIA RTX 3090", "NVIDIA RTX 3080"],
                pricing_model="hourly",
                supports_spot_instances=False,
                supports_auto_scaling=True,
                supports_preemption=False,
                startup_time_minutes=1.0,
                network_performance="high",
                availability_score=0.98,
                storage_cost_per_gb_hour=0.0003,
                egress_cost_per_gb=0.05,
                description="Premium GPU cloud with high reliability"
            ),
            CloudProvider(
                name="aws",
                regions=["us-east-1", "us-west-2", "eu-west-1"],
                available_gpus=["NVIDIA A100 40GB"],
                pricing_model="hourly",
                supports_spot_instances=True,
                supports_auto_scaling=True,
                supports_preemption=True,
                startup_time_minutes=5.0,
                network_performance="high",
                availability_score=0.99,
                storage_cost_per_gb_hour=0.0005,
                egress_cost_per_gb=0.09,
                description="Enterprise cloud with comprehensive services"
            ),
            CloudProvider(
                name="gcp",
                regions=["us-central1", "us-east1", "europe-west1"],
                available_gpus=["NVIDIA A100 40GB"],
                pricing_model="hourly",
                supports_spot_instances=True,
                supports_auto_scaling=True,
                supports_preemption=True,
                startup_time_minutes=4.0,
                network_performance="high",
                availability_score=0.99,
                storage_cost_per_gb_hour=0.0004,
                egress_cost_per_gb=0.08,
                description="Google's cloud platform with AI/ML focus"
            )
        ]
        
        for provider in providers:
            self.cloud_providers[provider.name] = provider
    
    def _load_resource_data(self) -> None:
        """Load resource data from disk."""
        try:
            self._load_gpus()
            self._load_cloud_providers()
        except Exception as e:
            logger.warning(f"Failed to load resource data: {e}")
    
    def _save_resource_data(self) -> None:
        """Save resource data to disk."""
        try:
            self._save_gpus()
            self._save_cloud_providers()
        except Exception as e:
            logger.error(f"Failed to save resource data: {e}")
    
    def _load_gpus(self) -> None:
        """Load GPU data from disk."""
        gpus_file = os.path.join(self.data_dir, "gpus.json")
        if os.path.exists(gpus_file):
            with open(gpus_file, 'r') as f:
                data = json.load(f)
                for name, gpu_data in data.items():
                    self.gpus[name] = GPUSpec(**gpu_data)
    
    def _save_gpus(self) -> None:
        """Save GPU data to disk."""
        gpus_file = os.path.join(self.data_dir, "gpus.json")
        with open(gpus_file, 'w') as f:
            from dataclasses import asdict
            data = {name: asdict(gpu) for name, gpu in self.gpus.items()}
            json.dump(data, f, indent=2)
    
    def _load_cloud_providers(self) -> None:
        """Load cloud provider data from disk."""
        providers_file = os.path.join(self.data_dir, "cloud_providers.json")
        if os.path.exists(providers_file):
            with open(providers_file, 'r') as f:
                data = json.load(f)
                for name, provider_data in data.items():
                    self.cloud_providers[name] = CloudProvider(**provider_data)
    
    def _save_cloud_providers(self) -> None:
        """Save cloud provider data to disk."""
        providers_file = os.path.join(self.data_dir, "cloud_providers.json")
        with open(providers_file, 'w') as f:
            from dataclasses import asdict
            data = {name: asdict(provider) for name, provider in self.cloud_providers.items()}
            json.dump(data, f, indent=2)
    
    def get_available_gpus(self) -> List[str]:
        """Get list of available GPU types."""
        return list(self.gpus.keys())
    
    def get_available_providers(self) -> List[str]:
        """Get list of available cloud providers."""
        return list(self.cloud_providers.keys())
    
    def estimate_cost(self, gpu_name: str, provider_name: str, hours: float) -> float:
        """Estimate cost for specific GPU and provider."""
        if gpu_name in self.gpus and provider_name in self.cloud_providers:
            gpu_spec = self.gpus[gpu_name]
            provider_spec = self.cloud_providers[provider_name]
            
            compute_cost = gpu_spec.cost_per_hour * hours
            storage_cost = provider_spec.storage_cost_per_gb_hour * 100 * hours  # Assume 100GB
            
            return compute_cost + storage_cost
        
        return 0.0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get resource optimizer statistics."""
        return {
            "total_gpus": len(self.gpus),
            "total_providers": len(self.cloud_providers),
            "avg_gpu_memory": sum(gpu.memory_gb for gpu in self.gpus.values()) / len(self.gpus) if self.gpus else 0,
            "avg_cost_per_hour": sum(gpu.cost_per_hour for gpu in self.gpus.values()) / len(self.gpus) if self.gpus else 0,
            "recommended_gpus": len([gpu for gpu in self.gpus.values() if gpu.is_recommended])
        }