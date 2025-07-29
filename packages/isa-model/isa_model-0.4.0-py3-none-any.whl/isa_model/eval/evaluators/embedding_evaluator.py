"""
Embedding Evaluator for ISA Model evaluation framework.

Provides comprehensive evaluation capabilities for embedding and retrieval tasks including:
- Semantic similarity evaluation
- Information retrieval evaluation (Precision@K, Recall@K, NDCG)
- Reranking effectiveness evaluation
- Cross-lingual embedding evaluation
- Document ranking evaluation
- Clustering evaluation

Supports ISA custom embedding services and standard embedding models.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import precision_score, recall_score, f1_score
import json

from .base_evaluator import BaseEvaluator, EvaluationResult

logger = logging.getLogger(__name__)


class EmbeddingEvaluator(BaseEvaluator):
    """
    Comprehensive embedding model evaluator.
    
    Supports evaluation of:
    - Semantic similarity tasks (STS, semantic textual similarity)
    - Information retrieval (IR) tasks with Precision@K, Recall@K, NDCG
    - Reranking effectiveness (MAP, MRR, NDCG improvements)
    - Cross-lingual embedding alignment
    - Document clustering quality
    - Zero-shot classification accuracy
    """
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 experiment_tracker: Optional[Any] = None):
        """
        Initialize the embedding evaluator.
        
        Args:
            config: Evaluation configuration
            experiment_tracker: Optional experiment tracking instance
        """
        super().__init__(
            evaluator_name="embedding_evaluator",
            config=config,
            experiment_tracker=experiment_tracker
        )
        
        # Embedding-specific configuration
        self.embedding_dim = self.config.get("embedding_dim", None)  # Auto-detect if None
        self.normalize_embeddings = self.config.get("normalize_embeddings", True)
        self.similarity_metric = self.config.get("similarity_metric", "cosine")  # cosine, dot, euclidean
        
        # Evaluation task types
        self.task_type = self.config.get("task_type", "similarity")  # similarity, retrieval, reranking, clustering
        
        # Retrieval evaluation settings
        self.k_values = self.config.get("k_values", [1, 5, 10, 20])  # For Precision@K, Recall@K
        self.relevance_threshold = self.config.get("relevance_threshold", 0.5)
        
        # Multilingual settings
        self.enable_multilingual = self.config.get("enable_multilingual", True)
        self.languages = self.config.get("languages", ["en", "zh", "es", "fr", "de"])
        
        logger.info(f"Initialized EmbeddingEvaluator for task: {self.task_type}")
    
    async def evaluate_sample(self, 
                            sample: Dict[str, Any],
                            model_interface: Any) -> Dict[str, Any]:
        """
        Evaluate a single embedding sample.
        
        Args:
            sample: Embedding sample containing text and expected output
            model_interface: Embedding model interface
            
        Returns:
            Evaluation result for the sample
        """
        try:
            # Extract sample data
            text_input = sample.get("text", "")
            query = sample.get("query", "")
            documents = sample.get("documents", [])
            expected_output = sample.get("expected_output")
            task_type = sample.get("task_type", self.task_type)
            
            # Get embeddings based on task type
            if task_type == "similarity":
                result = await self._evaluate_similarity_sample(
                    model_interface, text_input, expected_output, sample
                )
            elif task_type == "retrieval":
                result = await self._evaluate_retrieval_sample(
                    model_interface, query, documents, expected_output, sample
                )
            elif task_type == "reranking":
                result = await self._evaluate_reranking_sample(
                    model_interface, query, documents, expected_output, sample
                )
            elif task_type == "clustering":
                result = await self._evaluate_clustering_sample(
                    model_interface, text_input, expected_output, sample
                )
            else:
                # Generic embedding evaluation
                result = await self._evaluate_generic_sample(
                    model_interface, text_input, expected_output, sample
                )
            
            result["task_type"] = task_type
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating embedding sample: {e}")
            raise
    
    async def _evaluate_similarity_sample(self, 
                                        model_interface: Any,
                                        text_input: str,
                                        expected_output: Any,
                                        sample: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate semantic similarity task."""
        try:
            # Extract text pairs
            text1 = sample.get("text1", text_input)
            text2 = sample.get("text2", "")
            expected_similarity = float(expected_output) if expected_output is not None else 0.0
            
            # Get embeddings
            emb1 = await self._get_embedding(model_interface, text1)
            emb2 = await self._get_embedding(model_interface, text2)
            
            # Compute similarity
            predicted_similarity = self._compute_similarity(emb1, emb2)
            
            # Compute metrics
            sample_metrics = {
                "predicted_similarity": predicted_similarity,
                "expected_similarity": expected_similarity,
                "similarity_error": abs(predicted_similarity - expected_similarity),
                "similarity_correlation": self._compute_correlation([predicted_similarity], [expected_similarity])
            }
            
            return {
                "prediction": predicted_similarity,
                "expected_output": expected_similarity,
                "sample_metrics": sample_metrics,
                "embeddings": {"text1": emb1.tolist(), "text2": emb2.tolist()}
            }
            
        except Exception as e:
            logger.error(f"Error evaluating similarity sample: {e}")
            raise
    
    async def _evaluate_retrieval_sample(self, 
                                       model_interface: Any,
                                       query: str,
                                       documents: List[str],
                                       expected_output: Any,
                                       sample: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate information retrieval task."""
        try:
            # Get query embedding
            query_embedding = await self._get_embedding(model_interface, query)
            
            # Get document embeddings
            doc_embeddings = []
            for doc in documents:
                doc_emb = await self._get_embedding(model_interface, doc)
                doc_embeddings.append(doc_emb)
            
            if not doc_embeddings:
                raise ValueError("No documents provided for retrieval evaluation")
            
            doc_embeddings = np.array(doc_embeddings)
            
            # Compute similarities
            similarities = self._compute_similarity_matrix(query_embedding, doc_embeddings)
            
            # Rank documents
            ranked_indices = np.argsort(similarities)[::-1]  # Descending order
            
            # Extract relevance labels
            relevance_labels = expected_output if isinstance(expected_output, list) else []
            
            # Compute retrieval metrics
            sample_metrics = self._compute_retrieval_metrics(ranked_indices, relevance_labels)
            
            return {
                "prediction": ranked_indices.tolist(),
                "expected_output": relevance_labels,
                "sample_metrics": sample_metrics,
                "similarities": similarities.tolist(),
                "query_embedding": query_embedding.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error evaluating retrieval sample: {e}")
            raise
    
    async def _evaluate_reranking_sample(self, 
                                       model_interface: Any,
                                       query: str,
                                       documents: List[str],
                                       expected_output: Any,
                                       sample: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate reranking task."""
        try:
            # Get initial rankings (if provided)
            initial_ranking = sample.get("initial_ranking", list(range(len(documents))))
            
            # Rerank using embedding model
            if hasattr(model_interface, 'rerank'):
                # ISA reranking service
                reranked_results = await model_interface.rerank(query, documents)
                if isinstance(reranked_results, list):
                    reranked_indices = [r.get("index", i) for i, r in enumerate(reranked_results)]
                else:
                    reranked_indices = list(range(len(documents)))
            else:
                # Use embedding similarity for reranking
                query_embedding = await self._get_embedding(model_interface, query)
                doc_embeddings = []
                for doc in documents:
                    doc_emb = await self._get_embedding(model_interface, doc)
                    doc_embeddings.append(doc_emb)
                
                doc_embeddings = np.array(doc_embeddings)
                similarities = self._compute_similarity_matrix(query_embedding, doc_embeddings)
                reranked_indices = np.argsort(similarities)[::-1].tolist()
            
            # Extract relevance labels
            relevance_labels = expected_output if isinstance(expected_output, list) else []
            
            # Compute reranking metrics
            initial_metrics = self._compute_retrieval_metrics(initial_ranking, relevance_labels)
            reranked_metrics = self._compute_retrieval_metrics(reranked_indices, relevance_labels)
            
            # Compute improvement
            improvement_metrics = {}
            for metric_name in ["precision_at_1", "precision_at_5", "ndcg_at_10"]:
                initial_score = initial_metrics.get(metric_name, 0.0)
                reranked_score = reranked_metrics.get(metric_name, 0.0)
                improvement_metrics[f"{metric_name}_improvement"] = reranked_score - initial_score
            
            sample_metrics = {
                **reranked_metrics,
                **improvement_metrics,
                "reranking_effectiveness": np.mean(list(improvement_metrics.values()))
            }
            
            return {
                "prediction": reranked_indices,
                "expected_output": relevance_labels,
                "sample_metrics": sample_metrics,
                "initial_ranking": initial_ranking,
                "reranked_ranking": reranked_indices
            }
            
        except Exception as e:
            logger.error(f"Error evaluating reranking sample: {e}")
            raise
    
    async def _evaluate_clustering_sample(self, 
                                        model_interface: Any,
                                        text_input: Union[str, List[str]],
                                        expected_output: Any,
                                        sample: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate clustering task."""
        try:
            # Extract texts for clustering
            texts = text_input if isinstance(text_input, list) else sample.get("texts", [text_input])
            expected_clusters = expected_output if isinstance(expected_output, list) else []
            
            # Get embeddings
            embeddings = []
            for text in texts:
                emb = await self._get_embedding(model_interface, text)
                embeddings.append(emb)
            
            embeddings = np.array(embeddings)
            
            # Perform clustering (simple k-means)
            from sklearn.cluster import KMeans
            
            n_clusters = len(set(expected_clusters)) if expected_clusters else 2
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            predicted_clusters = kmeans.fit_predict(embeddings)
            
            # Compute clustering metrics
            sample_metrics = self._compute_clustering_metrics(predicted_clusters, expected_clusters)
            
            return {
                "prediction": predicted_clusters.tolist(),
                "expected_output": expected_clusters,
                "sample_metrics": sample_metrics,
                "embeddings": embeddings.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error evaluating clustering sample: {e}")
            raise
    
    async def _evaluate_generic_sample(self, 
                                     model_interface: Any,
                                     text_input: str,
                                     expected_output: Any,
                                     sample: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate generic embedding task."""
        try:
            # Get embedding
            embedding = await self._get_embedding(model_interface, text_input)
            
            # Basic embedding quality metrics
            sample_metrics = {
                "embedding_norm": float(np.linalg.norm(embedding)),
                "embedding_mean": float(np.mean(embedding)),
                "embedding_std": float(np.std(embedding)),
                "embedding_dimension": len(embedding)
            }
            
            return {
                "prediction": embedding.tolist(),
                "expected_output": expected_output,
                "sample_metrics": sample_metrics,
                "embedding": embedding.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error evaluating generic sample: {e}")
            raise
    
    async def _get_embedding(self, model_interface: Any, text: str) -> np.ndarray:
        """Get embedding from model interface."""
        try:
            if hasattr(model_interface, 'embed'):
                # ISA embedding service
                result = await model_interface.embed(text)
                if isinstance(result, dict):
                    embedding = result.get("embedding", result.get("vector", []))
                else:
                    embedding = result
            elif hasattr(model_interface, 'encode'):
                # Standard embedding interface
                embedding = await model_interface.encode(text)
            else:
                # Generic interface
                embedding = await model_interface.predict(text)
            
            # Convert to numpy array
            embedding = np.array(embedding, dtype=np.float32)
            
            # Normalize if configured
            if self.normalize_embeddings:
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = embedding / norm
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            raise
    
    def _compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Compute similarity between two embeddings."""
        try:
            if self.similarity_metric == "cosine":
                # Cosine similarity
                return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
            elif self.similarity_metric == "dot":
                # Dot product
                return float(np.dot(emb1, emb2))
            elif self.similarity_metric == "euclidean":
                # Negative euclidean distance (higher = more similar)
                return float(-np.linalg.norm(emb1 - emb2))
            else:
                # Default to cosine
                return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
                
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0
    
    def _compute_similarity_matrix(self, query_emb: np.ndarray, doc_embs: np.ndarray) -> np.ndarray:
        """Compute similarity matrix between query and documents."""
        try:
            if self.similarity_metric == "cosine":
                # Reshape for sklearn cosine_similarity
                query_emb = query_emb.reshape(1, -1)
                similarities = cosine_similarity(query_emb, doc_embs)[0]
            elif self.similarity_metric == "dot":
                similarities = np.dot(doc_embs, query_emb)
            elif self.similarity_metric == "euclidean":
                similarities = -np.linalg.norm(doc_embs - query_emb, axis=1)
            else:
                # Default to cosine
                query_emb = query_emb.reshape(1, -1)
                similarities = cosine_similarity(query_emb, doc_embs)[0]
            
            return similarities
            
        except Exception as e:
            logger.error(f"Error computing similarity matrix: {e}")
            return np.zeros(len(doc_embs))
    
    def _compute_retrieval_metrics(self, 
                                 ranked_indices: List[int],
                                 relevance_labels: List[int]) -> Dict[str, float]:
        """Compute information retrieval metrics."""
        try:
            if not relevance_labels:
                return {"retrieval_error": 1.0}
            
            metrics = {}
            n_docs = len(ranked_indices)
            
            # Ensure relevance labels match document count
            relevance_labels = relevance_labels[:n_docs] + [0] * max(0, n_docs - len(relevance_labels))
            
            # Compute metrics for different K values
            for k in self.k_values:
                if k > n_docs:
                    continue
                
                # Get top-k predictions
                top_k_indices = ranked_indices[:k]
                top_k_relevance = [relevance_labels[i] for i in top_k_indices]
                
                # Precision@K
                precision_k = sum(top_k_relevance) / k if k > 0 else 0.0
                metrics[f"precision_at_{k}"] = precision_k
                
                # Recall@K
                total_relevant = sum(relevance_labels)
                recall_k = sum(top_k_relevance) / total_relevant if total_relevant > 0 else 0.0
                metrics[f"recall_at_{k}"] = recall_k
                
                # F1@K
                if precision_k + recall_k > 0:
                    f1_k = 2 * precision_k * recall_k / (precision_k + recall_k)
                else:
                    f1_k = 0.0
                metrics[f"f1_at_{k}"] = f1_k
            
            # NDCG@K for different K values
            for k in self.k_values:
                if k > n_docs:
                    continue
                ndcg_k = self._compute_ndcg(ranked_indices, relevance_labels, k)
                metrics[f"ndcg_at_{k}"] = ndcg_k
            
            # Mean Average Precision (MAP)
            metrics["map"] = self._compute_map(ranked_indices, relevance_labels)
            
            # Mean Reciprocal Rank (MRR)
            metrics["mrr"] = self._compute_mrr(ranked_indices, relevance_labels)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error computing retrieval metrics: {e}")
            return {"retrieval_error": 1.0}
    
    def _compute_ndcg(self, ranked_indices: List[int], relevance_labels: List[int], k: int) -> float:
        """Compute Normalized Discounted Cumulative Gain@K."""
        try:
            # DCG@K
            dcg = 0.0
            for i, doc_idx in enumerate(ranked_indices[:k]):
                if doc_idx < len(relevance_labels):
                    relevance = relevance_labels[doc_idx]
                    dcg += relevance / np.log2(i + 2)  # i+2 because log2(1) = 0
            
            # IDCG@K (Ideal DCG)
            sorted_relevance = sorted(relevance_labels, reverse=True)
            idcg = 0.0
            for i, relevance in enumerate(sorted_relevance[:k]):
                idcg += relevance / np.log2(i + 2)
            
            # NDCG@K
            ndcg = dcg / idcg if idcg > 0 else 0.0
            return ndcg
            
        except Exception as e:
            logger.error(f"Error computing NDCG: {e}")
            return 0.0
    
    def _compute_map(self, ranked_indices: List[int], relevance_labels: List[int]) -> float:
        """Compute Mean Average Precision."""
        try:
            if not any(relevance_labels):
                return 0.0
            
            precision_sum = 0.0
            relevant_count = 0
            
            for i, doc_idx in enumerate(ranked_indices):
                if doc_idx < len(relevance_labels) and relevance_labels[doc_idx] > 0:
                    relevant_count += 1
                    precision_at_i = relevant_count / (i + 1)
                    precision_sum += precision_at_i
            
            total_relevant = sum(1 for r in relevance_labels if r > 0)
            map_score = precision_sum / total_relevant if total_relevant > 0 else 0.0
            
            return map_score
            
        except Exception as e:
            logger.error(f"Error computing MAP: {e}")
            return 0.0
    
    def _compute_mrr(self, ranked_indices: List[int], relevance_labels: List[int]) -> float:
        """Compute Mean Reciprocal Rank."""
        try:
            for i, doc_idx in enumerate(ranked_indices):
                if doc_idx < len(relevance_labels) and relevance_labels[doc_idx] > 0:
                    return 1.0 / (i + 1)
            return 0.0
            
        except Exception as e:
            logger.error(f"Error computing MRR: {e}")
            return 0.0
    
    def _compute_clustering_metrics(self, 
                                  predicted_clusters: List[int],
                                  expected_clusters: List[int]) -> Dict[str, float]:
        """Compute clustering evaluation metrics."""
        try:
            if not expected_clusters:
                return {"clustering_error": 1.0}
            
            # Ensure equal lengths
            min_len = min(len(predicted_clusters), len(expected_clusters))
            predicted_clusters = predicted_clusters[:min_len]
            expected_clusters = expected_clusters[:min_len]
            
            # Adjusted Rand Index (ARI)
            from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
            
            ari = adjusted_rand_score(expected_clusters, predicted_clusters)
            nmi = normalized_mutual_info_score(expected_clusters, predicted_clusters)
            
            # Silhouette score would require embeddings
            return {
                "adjusted_rand_index": ari,
                "normalized_mutual_info": nmi,
                "clustering_accuracy": (ari + nmi) / 2
            }
            
        except Exception as e:
            logger.error(f"Error computing clustering metrics: {e}")
            return {"clustering_error": 1.0}
    
    def _compute_correlation(self, predictions: List[float], references: List[float]) -> float:
        """Compute correlation between predictions and references."""
        try:
            if len(predictions) < 2 or len(references) < 2:
                return 0.0
            
            from scipy.stats import pearsonr
            correlation, _ = pearsonr(predictions, references)
            return float(correlation) if not np.isnan(correlation) else 0.0
            
        except Exception as e:
            logger.error(f"Error computing correlation: {e}")
            return 0.0
    
    def compute_metrics(self, 
                       predictions: List[Any],
                       references: List[Any],
                       **kwargs) -> Dict[str, float]:
        """
        Compute aggregate embedding evaluation metrics.
        
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
            
            task_type = self.task_type
            
            if task_type == "similarity":
                return self._compute_aggregate_similarity_metrics(predictions, references)
            elif task_type == "retrieval":
                return self._compute_aggregate_retrieval_metrics(predictions, references)
            elif task_type == "reranking":
                return self._compute_aggregate_reranking_metrics(predictions, references)
            elif task_type == "clustering":
                return self._compute_aggregate_clustering_metrics(predictions, references)
            else:
                # Generic metrics
                return {
                    "total_samples": len(predictions),
                    "task_type": task_type,
                    "evaluation_success_rate": 1.0
                }
            
        except Exception as e:
            logger.error(f"Error computing aggregate metrics: {e}")
            return {"error_rate": 1.0}
    
    def _compute_aggregate_similarity_metrics(self, 
                                            predictions: List[float],
                                            references: List[float]) -> Dict[str, float]:
        """Compute aggregate similarity metrics."""
        try:
            # Convert to float if needed
            pred_vals = [float(p) for p in predictions if p is not None]
            ref_vals = [float(r) for r in references if r is not None]
            
            if not pred_vals or not ref_vals:
                return {"similarity_error": 1.0}
            
            # Correlation
            correlation = self._compute_correlation(pred_vals, ref_vals)
            
            # Mean absolute error
            errors = [abs(p - r) for p, r in zip(pred_vals, ref_vals)]
            mae = np.mean(errors) if errors else 1.0
            
            # Mean squared error
            mse = np.mean([(p - r)**2 for p, r in zip(pred_vals, ref_vals)]) if pred_vals else 1.0
            
            return {
                "similarity_correlation": correlation,
                "similarity_mae": mae,
                "similarity_mse": mse,
                "similarity_rmse": np.sqrt(mse),
                "total_samples": len(pred_vals)
            }
            
        except Exception as e:
            logger.error(f"Error computing aggregate similarity metrics: {e}")
            return {"similarity_error": 1.0}
    
    def _compute_aggregate_retrieval_metrics(self, 
                                           predictions: List[List[int]],
                                           references: List[List[int]]) -> Dict[str, float]:
        """Compute aggregate retrieval metrics."""
        try:
            all_metrics = {}
            metric_names = [f"precision_at_{k}" for k in self.k_values] + \
                          [f"recall_at_{k}" for k in self.k_values] + \
                          [f"ndcg_at_{k}" for k in self.k_values] + \
                          ["map", "mrr"]
            
            # Initialize metric accumulators
            for metric_name in metric_names:
                all_metrics[metric_name] = []
            
            # Compute metrics for each sample
            for pred, ref in zip(predictions, references):
                if isinstance(pred, list) and isinstance(ref, list):
                    sample_metrics = self._compute_retrieval_metrics(pred, ref)
                    for metric_name in metric_names:
                        if metric_name in sample_metrics:
                            all_metrics[metric_name].append(sample_metrics[metric_name])
            
            # Compute averages
            avg_metrics = {}
            for metric_name, values in all_metrics.items():
                if values:
                    avg_metrics[f"avg_{metric_name}"] = np.mean(values)
            
            avg_metrics["total_samples"] = len(predictions)
            return avg_metrics
            
        except Exception as e:
            logger.error(f"Error computing aggregate retrieval metrics: {e}")
            return {"retrieval_error": 1.0}
    
    def _compute_aggregate_reranking_metrics(self, 
                                           predictions: List[List[int]],
                                           references: List[List[int]]) -> Dict[str, float]:
        """Compute aggregate reranking metrics."""
        # Similar to retrieval but focus on improvement metrics
        return self._compute_aggregate_retrieval_metrics(predictions, references)
    
    def _compute_aggregate_clustering_metrics(self, 
                                            predictions: List[List[int]],
                                            references: List[List[int]]) -> Dict[str, float]:
        """Compute aggregate clustering metrics."""
        try:
            ari_scores = []
            nmi_scores = []
            
            for pred, ref in zip(predictions, references):
                if isinstance(pred, list) and isinstance(ref, list):
                    sample_metrics = self._compute_clustering_metrics(pred, ref)
                    ari_scores.append(sample_metrics.get("adjusted_rand_index", 0.0))
                    nmi_scores.append(sample_metrics.get("normalized_mutual_info", 0.0))
            
            return {
                "avg_adjusted_rand_index": np.mean(ari_scores) if ari_scores else 0.0,
                "avg_normalized_mutual_info": np.mean(nmi_scores) if nmi_scores else 0.0,
                "avg_clustering_accuracy": np.mean(ari_scores + nmi_scores) / 2 if ari_scores or nmi_scores else 0.0,
                "total_samples": len(predictions)
            }
            
        except Exception as e:
            logger.error(f"Error computing aggregate clustering metrics: {e}")
            return {"clustering_error": 1.0}
    
    def get_supported_metrics(self) -> List[str]:
        """Get list of metrics supported by this evaluator."""
        base_metrics = ["total_samples", "evaluation_success_rate"]
        
        task_specific_metrics = {
            "similarity": ["similarity_correlation", "similarity_mae", "similarity_mse", "similarity_rmse"],
            "retrieval": [f"precision_at_{k}" for k in self.k_values] + 
                        [f"recall_at_{k}" for k in self.k_values] +
                        [f"ndcg_at_{k}" for k in self.k_values] +
                        ["map", "mrr"],
            "reranking": [f"precision_at_{k}_improvement" for k in self.k_values] +
                        ["reranking_effectiveness"],
            "clustering": ["adjusted_rand_index", "normalized_mutual_info", "clustering_accuracy"]
        }
        
        return base_metrics + task_specific_metrics.get(self.task_type, [])