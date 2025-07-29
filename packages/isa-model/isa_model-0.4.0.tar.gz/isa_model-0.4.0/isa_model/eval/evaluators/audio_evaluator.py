"""
Audio Evaluator for ISA Model evaluation framework.

Provides comprehensive evaluation capabilities for audio tasks including:
- Speech-to-Text (STT) evaluation with WER/CER metrics
- Speaker diarization evaluation  
- Emotion recognition evaluation
- Voice activity detection evaluation
- Speech enhancement evaluation
- Text-to-Speech (TTS) quality evaluation

Supports ISA custom audio services and standard audio models.
"""

import asyncio
import logging
import librosa
import numpy as np
import re
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import tempfile
import wave

from .base_evaluator import BaseEvaluator, EvaluationResult
from ..metrics import compute_text_metrics

logger = logging.getLogger(__name__)


class AudioEvaluator(BaseEvaluator):
    """
    Comprehensive audio model evaluator.
    
    Supports evaluation of:
    - Speech-to-Text accuracy (WER, CER, BLEU)
    - Speaker diarization accuracy (DER, Speaker F1)
    - Emotion recognition accuracy
    - Voice activity detection (Precision, Recall, F1)
    - Speech enhancement quality (SNR, PESQ, STOI)
    - Text-to-Speech naturalness and intelligibility
    """
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 experiment_tracker: Optional[Any] = None):
        """
        Initialize the audio evaluator.
        
        Args:
            config: Evaluation configuration
            experiment_tracker: Optional experiment tracking instance
        """
        super().__init__(
            evaluator_name="audio_evaluator",
            config=config,
            experiment_tracker=experiment_tracker
        )
        
        # Audio-specific configuration
        self.sample_rate = self.config.get("sample_rate", 16000)
        self.supported_formats = self.config.get("supported_formats", ["wav", "mp3", "flac", "m4a"])
        self.max_duration = self.config.get("max_duration_seconds", 300)  # 5 minutes
        
        # Evaluation task types
        self.task_type = self.config.get("task_type", "stt")  # stt, diarization, emotion, tts, enhancement
        
        # STT evaluation settings
        self.normalize_text = self.config.get("normalize_text", True)
        self.case_sensitive = self.config.get("case_sensitive", False)
        self.remove_punctuation = self.config.get("remove_punctuation", True)
        
        # Speaker diarization settings
        self.collar_tolerance = self.config.get("collar_tolerance", 0.25)  # 250ms tolerance
        
        logger.info(f"Initialized AudioEvaluator for task: {self.task_type}")
    
    async def evaluate_sample(self, 
                            sample: Dict[str, Any],
                            model_interface: Any) -> Dict[str, Any]:
        """
        Evaluate a single audio sample.
        
        Args:
            sample: Audio sample containing audio data and expected output
            model_interface: Audio model interface
            
        Returns:
            Evaluation result for the sample
        """
        try:
            # Extract sample data
            audio_data = sample.get("audio")
            expected_output = sample.get("expected_output", "")
            task_type = sample.get("task_type", self.task_type)
            metadata = sample.get("metadata", {})
            
            # Process audio
            processed_audio, audio_info = await self._process_audio(audio_data)
            
            # Get model prediction based on task type
            prediction = await self._get_model_prediction(
                model_interface, processed_audio, task_type, metadata
            )
            
            # Compute sample-level metrics
            sample_metrics = self._compute_sample_metrics(
                prediction, expected_output, task_type, audio_info
            )
            
            return {
                "prediction": prediction,
                "expected_output": expected_output,
                "task_type": task_type,
                "sample_metrics": sample_metrics,
                "audio_info": audio_info,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error evaluating audio sample: {e}")
            raise
    
    async def _process_audio(self, audio_data: Union[str, bytes, np.ndarray, Path]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Process and validate audio data.
        
        Args:
            audio_data: Audio in various formats
            
        Returns:
            Tuple of (processed audio array, audio info dict)
        """
        try:
            if isinstance(audio_data, str) and Path(audio_data).exists():
                # File path
                audio_array, sr = librosa.load(audio_data, sr=self.sample_rate)
                original_sr = librosa.get_samplerate(audio_data)
            
            elif isinstance(audio_data, Path):
                # Path object
                audio_array, sr = librosa.load(str(audio_data), sr=self.sample_rate)
                original_sr = librosa.get_samplerate(str(audio_data))
            
            elif isinstance(audio_data, bytes):
                # Raw audio bytes - save to temp file first
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                    tmp_file.write(audio_data)
                    tmp_path = tmp_file.name
                
                audio_array, sr = librosa.load(tmp_path, sr=self.sample_rate)
                original_sr = self.sample_rate  # Assume target sample rate
                Path(tmp_path).unlink()  # Clean up temp file
            
            elif isinstance(audio_data, np.ndarray):
                # NumPy array
                audio_array = audio_data
                sr = self.sample_rate
                original_sr = self.sample_rate
                
                # Resample if needed
                if len(audio_array.shape) > 1:
                    audio_array = librosa.to_mono(audio_array)
            
            else:
                raise ValueError(f"Unsupported audio data type: {type(audio_data)}")
            
            # Validate duration
            duration = len(audio_array) / sr
            if duration > self.max_duration:
                logger.warning(f"Audio duration {duration:.2f}s exceeds max duration {self.max_duration}s, truncating")
                max_samples = int(self.max_duration * sr)
                audio_array = audio_array[:max_samples]
                duration = self.max_duration
            
            # Compute audio features
            audio_info = {
                "duration_seconds": duration,
                "sample_rate": sr,
                "original_sample_rate": original_sr,
                "num_samples": len(audio_array),
                "rms_energy": float(np.sqrt(np.mean(audio_array**2))),
                "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(audio_array))),
                "spectral_centroid": float(np.mean(librosa.feature.spectral_centroid(y=audio_array, sr=sr)))
            }
            
            return audio_array, audio_info
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            raise
    
    async def _get_model_prediction(self, 
                                  model_interface: Any,
                                  audio: np.ndarray,
                                  task_type: str,
                                  metadata: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
        """
        Get model prediction for audio task.
        
        Args:
            model_interface: Audio model interface
            audio: Processed audio array
            task_type: Type of audio task
            metadata: Additional metadata
            
        Returns:
            Model prediction (string for STT, dict for complex tasks)
        """
        try:
            # Save audio to temporary file for model processing
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                # Convert to int16 for wav format
                audio_int16 = (audio * 32767).astype(np.int16)
                
                # Write WAV file
                with wave.open(tmp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(self.sample_rate)
                    wav_file.writeframes(audio_int16.tobytes())
                
                tmp_path = tmp_file.name
            
            try:
                if task_type == "stt":
                    # Speech-to-Text
                    if hasattr(model_interface, 'transcribe'):
                        result = await model_interface.transcribe(tmp_path)
                        prediction = result.get("text", "") if isinstance(result, dict) else str(result)
                    elif hasattr(model_interface, 'stt'):
                        prediction = await model_interface.stt(tmp_path)
                    else:
                        prediction = await model_interface.predict(tmp_path)
                    
                    return str(prediction).strip()
                
                elif task_type == "diarization":
                    # Speaker diarization
                    if hasattr(model_interface, 'diarize'):
                        result = await model_interface.diarize(tmp_path)
                    else:
                        result = await model_interface.predict(tmp_path, task="diarization")
                    
                    return result  # Should be dict with speaker segments
                
                elif task_type == "emotion":
                    # Emotion recognition
                    if hasattr(model_interface, 'detect_emotion'):
                        result = await model_interface.detect_emotion(tmp_path)
                    else:
                        result = await model_interface.predict(tmp_path, task="emotion")
                    
                    return result  # Should be emotion label or dict
                
                elif task_type == "tts":
                    # Text-to-Speech (reverse evaluation)
                    text_input = metadata.get("text_input", "")
                    if hasattr(model_interface, 'synthesize'):
                        result = await model_interface.synthesize(text_input)
                    else:
                        result = await model_interface.predict(text_input, task="tts")
                    
                    return result  # Should be synthesized audio
                
                else:
                    # Generic prediction
                    prediction = await model_interface.predict(tmp_path)
                    return prediction
            
            finally:
                # Clean up temporary file
                Path(tmp_path).unlink()
            
        except Exception as e:
            logger.error(f"Error getting model prediction: {e}")
            raise
    
    def _compute_sample_metrics(self, 
                              prediction: Union[str, Dict[str, Any]],
                              expected_output: Union[str, Dict[str, Any]],
                              task_type: str,
                              audio_info: Dict[str, Any]) -> Dict[str, float]:
        """
        Compute metrics for a single sample.
        
        Args:
            prediction: Model prediction
            expected_output: Expected/reference output
            task_type: Type of audio task
            audio_info: Audio metadata
            
        Returns:
            Dictionary of sample-level metrics
        """
        try:
            metrics = {}
            
            if task_type == "stt":
                # Speech-to-Text metrics
                if isinstance(prediction, str) and isinstance(expected_output, str):
                    metrics.update(self._compute_stt_metrics(prediction, expected_output))
            
            elif task_type == "diarization":
                # Speaker diarization metrics
                metrics.update(self._compute_diarization_metrics(prediction, expected_output))
            
            elif task_type == "emotion":
                # Emotion recognition metrics
                metrics.update(self._compute_emotion_metrics(prediction, expected_output))
            
            elif task_type == "tts":
                # TTS quality metrics
                metrics.update(self._compute_tts_metrics(prediction, expected_output, audio_info))
            
            # Add audio metadata
            metrics.update({
                "audio_duration": audio_info.get("duration_seconds", 0.0),
                "audio_quality_score": self._compute_audio_quality_score(audio_info)
            })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error computing sample metrics: {e}")
            return {"error": 1.0}
    
    def _compute_stt_metrics(self, prediction: str, reference: str) -> Dict[str, float]:
        """Compute Speech-to-Text specific metrics."""
        try:
            # Normalize text if configured
            if self.normalize_text:
                prediction = self._normalize_text(prediction)
                reference = self._normalize_text(reference)
            
            # Word Error Rate (WER)
            wer = self._compute_wer(prediction, reference)
            
            # Character Error Rate (CER)
            cer = self._compute_cer(prediction, reference)
            
            # Additional text metrics
            text_metrics = compute_text_metrics(prediction, reference)
            
            return {
                "wer": wer,
                "cer": cer,
                "word_accuracy": 1.0 - wer,
                "char_accuracy": 1.0 - cer,
                **text_metrics
            }
            
        except Exception as e:
            logger.error(f"Error computing STT metrics: {e}")
            return {"stt_error": 1.0}
    
    def _compute_wer(self, prediction: str, reference: str) -> float:
        """Compute Word Error Rate."""
        try:
            pred_words = prediction.strip().split()
            ref_words = reference.strip().split()
            
            if not ref_words:
                return 0.0 if not pred_words else 1.0
            
            # Compute edit distance
            distance = self._edit_distance(pred_words, ref_words)
            wer = distance / len(ref_words)
            
            return min(1.0, wer)  # Cap at 100%
            
        except Exception as e:
            logger.error(f"Error computing WER: {e}")
            return 1.0
    
    def _compute_cer(self, prediction: str, reference: str) -> float:
        """Compute Character Error Rate."""
        try:
            pred_chars = list(prediction.strip())
            ref_chars = list(reference.strip())
            
            if not ref_chars:
                return 0.0 if not pred_chars else 1.0
            
            # Compute edit distance
            distance = self._edit_distance(pred_chars, ref_chars)
            cer = distance / len(ref_chars)
            
            return min(1.0, cer)  # Cap at 100%
            
        except Exception as e:
            logger.error(f"Error computing CER: {e}")
            return 1.0
    
    def _edit_distance(self, seq1: List[str], seq2: List[str]) -> int:
        """Compute Levenshtein edit distance."""
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Initialize base cases
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        # Fill the DP table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i-1][j],    # deletion
                        dp[i][j-1],    # insertion
                        dp[i-1][j-1]   # substitution
                    )
        
        return dp[m][n]
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for evaluation."""
        # Convert to lowercase if not case sensitive
        if not self.case_sensitive:
            text = text.lower()
        
        # Remove punctuation if configured
        if self.remove_punctuation:
            text = re.sub(r'[^\w\s]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _compute_diarization_metrics(self, 
                                   prediction: Dict[str, Any],
                                   reference: Dict[str, Any]) -> Dict[str, float]:
        """Compute speaker diarization metrics."""
        try:
            # Extract speaker segments
            pred_segments = prediction.get("segments", []) if isinstance(prediction, dict) else []
            ref_segments = reference.get("segments", []) if isinstance(reference, dict) else []
            
            if not ref_segments:
                return {"diarization_error": 1.0}
            
            # Compute Diarization Error Rate (DER)
            der = self._compute_der(pred_segments, ref_segments)
            
            # Compute Speaker F1 score
            speaker_f1 = self._compute_speaker_f1(pred_segments, ref_segments)
            
            return {
                "diarization_error_rate": der,
                "speaker_f1_score": speaker_f1,
                "num_predicted_speakers": len(set(seg.get("speaker", "") for seg in pred_segments)),
                "num_reference_speakers": len(set(seg.get("speaker", "") for seg in ref_segments))
            }
            
        except Exception as e:
            logger.error(f"Error computing diarization metrics: {e}")
            return {"diarization_error": 1.0}
    
    def _compute_der(self, pred_segments: List[Dict], ref_segments: List[Dict]) -> float:
        """Compute Diarization Error Rate."""
        try:
            # This is a simplified DER computation
            # In practice, you'd use specialized libraries like pyannote.metrics
            
            total_time = 0.0
            error_time = 0.0
            
            # Find overall time range
            all_segments = pred_segments + ref_segments
            if not all_segments:
                return 0.0
            
            start_time = min(seg.get("start", 0.0) for seg in all_segments)
            end_time = max(seg.get("end", 0.0) for seg in all_segments)
            total_time = end_time - start_time
            
            if total_time <= 0:
                return 0.0
            
            # Sample time points and check for errors
            time_step = 0.1  # 100ms resolution
            num_steps = int(total_time / time_step)
            
            for i in range(num_steps):
                t = start_time + i * time_step
                
                # Find speakers at time t
                pred_speaker = self._get_speaker_at_time(t, pred_segments)
                ref_speaker = self._get_speaker_at_time(t, ref_segments)
                
                if pred_speaker != ref_speaker:
                    error_time += time_step
            
            der = error_time / total_time if total_time > 0 else 0.0
            return min(1.0, der)
            
        except Exception as e:
            logger.error(f"Error computing DER: {e}")
            return 1.0
    
    def _get_speaker_at_time(self, time: float, segments: List[Dict]) -> Optional[str]:
        """Get the speaker at a specific time point."""
        for segment in segments:
            start = segment.get("start", 0.0)
            end = segment.get("end", 0.0)
            if start <= time < end:
                return segment.get("speaker")
        return None
    
    def _compute_speaker_f1(self, pred_segments: List[Dict], ref_segments: List[Dict]) -> float:
        """Compute Speaker F1 score."""
        try:
            # Extract unique speakers
            pred_speakers = set(seg.get("speaker", "") for seg in pred_segments)
            ref_speakers = set(seg.get("speaker", "") for seg in ref_segments)
            
            pred_speakers.discard("")  # Remove empty speakers
            ref_speakers.discard("")
            
            if not ref_speakers:
                return 1.0 if not pred_speakers else 0.0
            
            # Simple speaker overlap metric
            intersection = len(pred_speakers.intersection(ref_speakers))
            precision = intersection / len(pred_speakers) if pred_speakers else 0.0
            recall = intersection / len(ref_speakers) if ref_speakers else 0.0
            
            if precision + recall == 0:
                return 0.0
            
            f1 = 2 * precision * recall / (precision + recall)
            return f1
            
        except Exception as e:
            logger.error(f"Error computing speaker F1: {e}")
            return 0.0
    
    def _compute_emotion_metrics(self, 
                               prediction: Union[str, Dict[str, Any]],
                               reference: Union[str, Dict[str, Any]]) -> Dict[str, float]:
        """Compute emotion recognition metrics."""
        try:
            # Extract emotion labels
            if isinstance(prediction, dict):
                pred_emotion = prediction.get("emotion", "")
                pred_confidence = prediction.get("confidence", 0.0)
            else:
                pred_emotion = str(prediction)
                pred_confidence = 1.0
            
            if isinstance(reference, dict):
                ref_emotion = reference.get("emotion", "")
            else:
                ref_emotion = str(reference)
            
            # Compute accuracy
            emotion_accuracy = 1.0 if pred_emotion.lower() == ref_emotion.lower() else 0.0
            
            return {
                "emotion_accuracy": emotion_accuracy,
                "emotion_confidence": pred_confidence,
                "predicted_emotion": pred_emotion,
                "reference_emotion": ref_emotion
            }
            
        except Exception as e:
            logger.error(f"Error computing emotion metrics: {e}")
            return {"emotion_error": 1.0}
    
    def _compute_tts_metrics(self, 
                           prediction: Any,
                           reference: Any,
                           audio_info: Dict[str, Any]) -> Dict[str, float]:
        """Compute Text-to-Speech quality metrics."""
        try:
            # This is a placeholder for TTS evaluation
            # In practice, you'd use specialized metrics like MOS, PESQ, STOI
            
            return {
                "tts_quality_score": 0.8,  # Placeholder
                "synthesis_success": 1.0 if prediction is not None else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error computing TTS metrics: {e}")
            return {"tts_error": 1.0}
    
    def _compute_audio_quality_score(self, audio_info: Dict[str, Any]) -> float:
        """Compute a simple audio quality score based on audio features."""
        try:
            # Simple heuristic based on RMS energy and other features
            rms_energy = audio_info.get("rms_energy", 0.0)
            duration = audio_info.get("duration_seconds", 0.0)
            
            # Normalize RMS energy (assuming good audio is in range 0.01-0.1)
            energy_score = min(1.0, max(0.0, (rms_energy - 0.001) / 0.1))
            
            # Duration score (prefer reasonable durations)
            duration_score = 1.0 if 1.0 <= duration <= 60.0 else 0.5
            
            quality_score = (energy_score + duration_score) / 2
            return quality_score
            
        except Exception as e:
            logger.error(f"Error computing audio quality score: {e}")
            return 0.5
    
    def compute_metrics(self, 
                       predictions: List[Any],
                       references: List[Any],
                       **kwargs) -> Dict[str, float]:
        """
        Compute aggregate audio evaluation metrics.
        
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
            
            if task_type == "stt":
                return self._compute_aggregate_stt_metrics(predictions, references)
            elif task_type == "diarization":
                return self._compute_aggregate_diarization_metrics(predictions, references)
            elif task_type == "emotion":
                return self._compute_aggregate_emotion_metrics(predictions, references)
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
    
    def _compute_aggregate_stt_metrics(self, 
                                     predictions: List[str],
                                     references: List[str]) -> Dict[str, float]:
        """Compute aggregate STT metrics."""
        wer_scores = []
        cer_scores = []
        
        for pred, ref in zip(predictions, references):
            if isinstance(pred, str) and isinstance(ref, str):
                sample_metrics = self._compute_stt_metrics(pred, ref)
                wer_scores.append(sample_metrics.get("wer", 1.0))
                cer_scores.append(sample_metrics.get("cer", 1.0))
        
        return {
            "avg_wer": np.mean(wer_scores) if wer_scores else 1.0,
            "avg_cer": np.mean(cer_scores) if cer_scores else 1.0,
            "avg_word_accuracy": 1.0 - np.mean(wer_scores) if wer_scores else 0.0,
            "avg_char_accuracy": 1.0 - np.mean(cer_scores) if cer_scores else 0.0,
            "total_samples": len(predictions)
        }
    
    def _compute_aggregate_diarization_metrics(self, 
                                             predictions: List[Dict],
                                             references: List[Dict]) -> Dict[str, float]:
        """Compute aggregate diarization metrics."""
        der_scores = []
        f1_scores = []
        
        for pred, ref in zip(predictions, references):
            if isinstance(pred, dict) and isinstance(ref, dict):
                sample_metrics = self._compute_diarization_metrics(pred, ref)
                der_scores.append(sample_metrics.get("diarization_error_rate", 1.0))
                f1_scores.append(sample_metrics.get("speaker_f1_score", 0.0))
        
        return {
            "avg_diarization_error_rate": np.mean(der_scores) if der_scores else 1.0,
            "avg_speaker_f1_score": np.mean(f1_scores) if f1_scores else 0.0,
            "total_samples": len(predictions)
        }
    
    def _compute_aggregate_emotion_metrics(self, 
                                         predictions: List[Any],
                                         references: List[Any]) -> Dict[str, float]:
        """Compute aggregate emotion recognition metrics."""
        accuracies = []
        confidences = []
        
        for pred, ref in zip(predictions, references):
            sample_metrics = self._compute_emotion_metrics(pred, ref)
            accuracies.append(sample_metrics.get("emotion_accuracy", 0.0))
            confidences.append(sample_metrics.get("emotion_confidence", 0.0))
        
        return {
            "avg_emotion_accuracy": np.mean(accuracies) if accuracies else 0.0,
            "avg_confidence": np.mean(confidences) if confidences else 0.0,
            "total_samples": len(predictions)
        }
    
    def get_supported_metrics(self) -> List[str]:
        """Get list of metrics supported by this evaluator."""
        base_metrics = ["total_samples", "evaluation_success_rate"]
        
        task_specific_metrics = {
            "stt": ["wer", "cer", "word_accuracy", "char_accuracy", "bleu_score", "rouge_l"],
            "diarization": ["diarization_error_rate", "speaker_f1_score"],
            "emotion": ["emotion_accuracy", "emotion_confidence"],
            "tts": ["tts_quality_score", "synthesis_success"]
        }
        
        return base_metrics + task_specific_metrics.get(self.task_type, [])