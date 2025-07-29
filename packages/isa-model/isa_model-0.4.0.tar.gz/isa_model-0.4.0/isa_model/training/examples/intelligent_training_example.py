#!/usr/bin/env python3
"""
Intelligent Training System Example

This script demonstrates the capabilities of the intelligent training system:
- Natural language training request analysis
- Automatic model and resource selection
- Cost and performance optimization
- Training option comparison
- Best practices recommendations

Run this script to see the intelligent training system in action.
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

def main():
    """Demonstrate intelligent training capabilities."""
    
    print("🧠 Intelligent Training System Demo")
    print("=" * 50)
    
    try:
        # Import intelligent training components
        from isa_model.training import (
            IntelligentTrainingFactory, 
            INTELLIGENT_AVAILABLE
        )
        
        if not INTELLIGENT_AVAILABLE:
            print("❌ Intelligent training features not available")
            return
        
        print("✅ Intelligent training system loaded successfully\n")
        
        # Initialize intelligent factory
        print("🔧 Initializing intelligent training factory...")
        factory = IntelligentTrainingFactory()
        
        # Example 1: Natural Language Training Request
        print("\n" + "="*50)
        print("📝 EXAMPLE 1: Natural Language Analysis")
        print("="*50)
        
        description = "Train a customer service chatbot for a medical company that can answer patient questions about symptoms and treatments in Chinese"
        dataset_path = "medical_qa_chinese.json"  # Hypothetical dataset
        
        print(f"Request: {description}")
        print(f"Dataset: {dataset_path}")
        
        try:
            recommendation = factory.analyze_training_request(
                description=description,
                dataset_source=dataset_path,
                quality_target="high",
                budget_limit=300.0,
                time_limit=12
            )
            
            print(f"\n✅ Analysis completed successfully!")
            print(f"📱 Recommended Model: {recommendation.model_name}")
            print(f"🖥️  Recommended GPU: {recommendation.recommended_gpu}")
            print(f"💰 Estimated Cost: ${recommendation.estimated_cost:.2f}")
            print(f"⏱️  Estimated Time: {recommendation.estimated_time:.1f} hours")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
        
        # Example 2: Training Options Comparison
        print("\n" + "="*50)
        print("📊 EXAMPLE 2: Training Options Comparison")
        print("="*50)
        
        description2 = "Fine-tune a code generation model for Python development"
        dataset_path2 = "python_code_dataset.json"
        
        print(f"Request: {description2}")
        print(f"Comparing quality targets: fast, balanced, high")
        
        try:
            comparisons = factory.compare_training_options(
                description=description2,
                dataset_source=dataset_path2,
                quality_targets=["fast", "balanced", "high"],
                budget_limits=[50.0, 150.0, 300.0]
            )
            
            print(f"✅ Generated {len(comparisons)} training options for comparison")
            
        except Exception as e:
            print(f"❌ Comparison failed: {e}")
        
        # Example 3: Best Practices
        print("\n" + "="*50)
        print("💡 EXAMPLE 3: Best Practices")
        print("="*50)
        
        task_types = ["chat", "classification", "generation"]
        domains = ["medical", "legal", "general"]
        
        for task_type in task_types:
            for domain in domains:
                try:
                    practices = factory.get_best_practices(task_type, domain)
                    if practices:
                        print(f"\n📋 {task_type.title()} + {domain.title()}:")
                        for practice in practices[:2]:  # Show top 2
                            print(f"  • {practice}")
                except Exception as e:
                    continue
        
        # Example 4: System Capabilities
        print("\n" + "="*50)
        print("🎯 EXAMPLE 4: System Capabilities")
        print("="*50)
        
        try:
            capabilities = factory.get_supported_capabilities()
            
            print(f"📱 Supported Models: {len(capabilities.get('task_types', []))} task types")
            print(f"🌍 Supported Domains: {len(capabilities.get('domains', []))} domains")
            print(f"🖥️  Available GPUs: {len(capabilities.get('gpu_types', []))} types")
            print(f"☁️  Cloud Providers: {len(capabilities.get('cloud_providers', []))} providers")
            
            print("\nTask Types:")
            for task in capabilities.get('task_types', [])[:5]:
                print(f"  • {task}")
            
            print("\nDomains:")
            for domain in capabilities.get('domains', [])[:5]:
                print(f"  • {domain}")
            
            print("\nGPU Types:")
            for gpu in capabilities.get('gpu_types', [])[:5]:
                print(f"  • {gpu}")
                
        except Exception as e:
            print(f"❌ Failed to get capabilities: {e}")
        
        # Example 5: Intelligence Statistics
        print("\n" + "="*50)
        print("📈 EXAMPLE 5: Intelligence Statistics")
        print("="*50)
        
        try:
            stats = factory.get_intelligence_statistics()
            
            if stats.get('intelligence_enabled'):
                kb_stats = stats.get('knowledge_base', {})
                print(f"📚 Knowledge Base:")
                print(f"  • Models: {kb_stats.get('total_models', 0)}")
                print(f"  • Best Practices: {kb_stats.get('best_practices', 0)}")
                print(f"  • Benchmarks: {kb_stats.get('benchmarks', 0)}")
                
                resource_stats = stats.get('resource_optimizer', {})
                print(f"🖥️  Resource Optimizer:")
                print(f"  • GPUs: {resource_stats.get('total_gpus', 0)}")
                print(f"  • Providers: {resource_stats.get('total_providers', 0)}")
                print(f"  • Avg Cost/Hour: ${resource_stats.get('avg_cost_per_hour', 0):.2f}")
            
        except Exception as e:
            print(f"❌ Failed to get statistics: {e}")
        
        # Example 6: Recommendation Scenarios
        print("\n" + "="*50)
        print("🎭 EXAMPLE 6: Different Scenarios")
        print("="*50)
        
        scenarios = [
            {
                "name": "Budget-Conscious Student",
                "description": "Create a simple English grammar checker",
                "dataset": "grammar_corrections.json",
                "budget": 25.0,
                "time": 4,
                "target": "fast"
            },
            {
                "name": "Enterprise Company",
                "description": "Advanced legal document analysis system",
                "dataset": "legal_documents.json", 
                "budget": 1000.0,
                "time": 24,
                "target": "high"
            },
            {
                "name": "Research Lab",
                "description": "Multi-modal medical image description model",
                "dataset": "medical_images_captions.json",
                "budget": 500.0,
                "time": 16,
                "target": "balanced"
            }
        ]
        
        for scenario in scenarios:
            print(f"\n👤 {scenario['name']}:")
            print(f"   Request: {scenario['description']}")
            print(f"   Budget: ${scenario['budget']}, Time: {scenario['time']}h, Target: {scenario['target']}")
            
            try:
                rec = factory.analyze_training_request(
                    description=scenario['description'],
                    dataset_source=scenario['dataset'],
                    quality_target=scenario['target'],
                    budget_limit=scenario['budget'],
                    time_limit=scenario['time']
                )
                
                print(f"   → Model: {rec.model_name}")
                print(f"   → GPU: {rec.recommended_gpu}")
                print(f"   → Cost: ${rec.estimated_cost:.2f}")
                print(f"   → Confidence: {rec.confidence_score:.1%}")
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        
        # Summary
        print("\n" + "="*50)
        print("✅ DEMO COMPLETED SUCCESSFULLY")
        print("="*50)
        print("The intelligent training system is ready to use!")
        print("\nNext steps:")
        print("1. Prepare your dataset in JSON format")
        print("2. Use analyze_training_request() for recommendations")
        print("3. Use train_with_recommendation() to start training")
        print("4. Monitor progress and collect results")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure the isa_model package is properly installed")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


def create_sample_dataset():
    """Create a sample dataset for testing."""
    sample_data = [
        {
            "instruction": "What are the symptoms of the common cold?",
            "input": "",
            "output": "Common cold symptoms include runny nose, sneezing, coughing, sore throat, mild headache, and fatigue."
        },
        {
            "instruction": "How can I prevent getting sick?",
            "input": "",
            "output": "To prevent illness, wash your hands frequently, maintain a healthy diet, get adequate sleep, exercise regularly, and avoid close contact with sick people."
        },
        {
            "instruction": "When should I see a doctor?",
            "input": "I have a fever and cough for 3 days",
            "output": "You should see a doctor if you have a persistent fever and cough for more than 3 days, especially if symptoms are worsening or you have difficulty breathing."
        }
    ]
    
    # Create sample dataset file
    os.makedirs("sample_data", exist_ok=True)
    with open("sample_data/medical_qa_sample.json", "w") as f:
        json.dump(sample_data, f, indent=2)
    
    print("📁 Created sample dataset: sample_data/medical_qa_sample.json")


if __name__ == "__main__":
    print("🚀 Starting Intelligent Training System Demo\n")
    
    # Create sample dataset
    create_sample_dataset()
    
    # Run main demo
    main()
    
    print("\n🎉 Demo finished! Thank you for trying the intelligent training system.")