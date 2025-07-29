"""
VoxStream - Real-time voice streaming engine

Central streaming orchestrator that manages voice processing pipelines
for optimized real-time streaming with adaptive quality control.
"""

import time
import logging
import threading
from typing import Optional, Dict, Any, List, Callable, Tuple
from dataclasses import dataclass, field
from collections import deque
from enum import Enum

from voxstream.config.types import (
    AudioBytes, StreamConfig, ProcessingMode, AudioFormat,
    AudioConstants, AudioMetadata, BufferConfig, AudioErrorType,
    VADConfig, StreamMetrics
)
from voxstream.core.processor import StreamProcessor, BufferPool, StreamBuffer
from voxstream.exceptions import VoxStreamError, AudioError


class ProcessingStrategy(Enum):
    """Processing strategies for different scenarios"""
    ZERO_COPY = "zero_copy"          # Minimal processing, pass-through
    FAST_LANE = "fast_lane"          # Realtime with minimal features
    BALANCED = "balanced"            # Balance of speed and quality
    QUALITY = "quality"              # Full processing pipeline
    ADAPTIVE = "adaptive"            # Dynamically adjust based on load


class VoxStream:
    """
    Real-time voice streaming engine.
    
    Coordinates voice streaming with adaptive quality optimization.
    Manages resources and processing pipelines for minimal latency.
    """
    
    def __init__(
        self,
        mode: ProcessingMode = ProcessingMode.BALANCED,
        config: StreamConfig = None,
        buffer_config: BufferConfig = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize VoxStream engine.
        
        Args:
            mode: Processing mode (REALTIME, QUALITY, BALANCED)
            config: Stream configuration
            buffer_config: Buffer pool configuration
            logger: Optional logger
        """
        self.mode = mode
        self.config = config or StreamConfig()
        self.buffer_config = buffer_config or BufferConfig()
        self.logger = logger or logging.getLogger(__name__)
        
        # Create processor
        self.processor = StreamProcessor(self.config, mode)
        
        # Initialize buffer pool for realtime mode
        self.buffer_pool: Optional[BufferPool] = None
        if mode == ProcessingMode.REALTIME and self.buffer_config.pre_allocate:
            self._init_buffer_pool()
        
        # Processing history for adaptive optimization
        self._processing_history = deque(maxlen=100)
        self._adaptive_threshold = 10.0  # ms threshold for switching strategies
        
        # Metrics
        self.metrics = StreamMetrics()
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Processing pipeline components
        self._pre_processors: List[Callable] = []
        self._post_processors: List[Callable] = []
        
        # Stream buffer for big lane
        self._stream_buffer: Optional[StreamBuffer] = None
        if mode == ProcessingMode.QUALITY:
            self._stream_buffer = StreamBuffer(
                config=self.buffer_config,
                audio_config=self.config,
                mode=mode
            )
        
        self.logger.info(f"VoxStream initialized in {mode.value} mode")
    
    def _init_buffer_pool(self):
        """Initialize buffer pool for zero-copy operations"""
        pool_size = self.buffer_config.pool_size
        buffer_size = self.buffer_config.pool_buffer_size
        
        self.buffer_pool = BufferPool(pool_size, buffer_size)
        self.logger.debug(f"Buffer pool initialized: {pool_size} buffers of {buffer_size} bytes")
    
    # ============== Main Processing Interface ==============
    
    def process_audio(self, audio_bytes: AudioBytes) -> AudioBytes:
        """
        Process audio through appropriate path.
        
        Routes to fast/balanced/quality processing based on mode.
        
        Args:
            audio_bytes: Input audio data
            
        Returns:
            Processed audio bytes
        """
        start_time = time.perf_counter()
        
        try:
            # Quick validation
            if not audio_bytes:
                return audio_bytes
            
            # Choose processing strategy
            if self.mode == ProcessingMode.REALTIME:
                result = self._process_realtime(audio_bytes)
            elif self.mode == ProcessingMode.QUALITY:
                result = self._process_quality(audio_bytes)
            else:  # BALANCED
                result = self._process_balanced(audio_bytes)
            
            # Update metrics
            processing_time = time.perf_counter() - start_time
            with self._lock:
                self.metrics.update(len(audio_bytes), processing_time)
                self._processing_history.append(processing_time)
            
            return result
            
        except Exception as e:
            self.metrics.record_error(e)
            self.logger.error(f"Processing error: {e}")
            raise
    
    # ============== Processing Strategies ==============
    
    def _process_realtime(self, audio_bytes: AudioBytes) -> AudioBytes:
        """
        Fast lane processing - minimal latency.
        
        Uses buffer pool for zero-copy when possible.
        """
        self.metrics.realtime_chunks += 1
        
        # Try zero-copy with buffer pool
        if self.buffer_pool and len(audio_bytes) <= self.buffer_config.pool_buffer_size:
            buffer = self.buffer_pool.acquire()
            if buffer:
                try:
                    # Process into pre-allocated buffer
                    self.metrics.buffer_pool_hits += 1
                    return self._process_with_buffer(audio_bytes, buffer)
                finally:
                    self.buffer_pool.release(buffer)
            else:
                self.metrics.buffer_pool_misses += 1
        
        # Fallback to minimal processing
        return self.processor.process_realtime(audio_bytes)
    
    def _process_balanced(self, audio_bytes: AudioBytes) -> AudioBytes:
        """
        Balanced processing - adaptive based on load.
        
        Switches between fast and quality based on performance.
        """
        # Check recent processing times
        if self._should_use_fast_path():
            return self._process_realtime(audio_bytes)
        else:
            # Use lighter quality processing
            return self._process_quality_light(audio_bytes)
    
    def _process_quality(self, audio_bytes: AudioBytes) -> AudioBytes:
        """
        Quality processing - full pipeline.
        
        Includes enhancement, normalization, and analysis.
        """
        self.metrics.quality_chunks += 1
        
        # Full quality processing with metadata
        processed, metadata = self.processor.process_quality(
            audio_bytes,
            enhance=True,
            normalize=True
        )
        
        # Store metadata if needed
        if metadata.is_speech:
            if metadata.signal_to_noise_ratio is not None:
                self.logger.debug(f"Speech detected: SNR={metadata.signal_to_noise_ratio:.1f}dB")
            else:
                self.logger.debug("Speech detected: SNR=N/A")
                
        return processed
    
    def _process_quality_light(self, audio_bytes: AudioBytes) -> AudioBytes:
        """Lighter quality processing for balanced mode"""
        # Skip enhancement for faster processing
        processed, _ = self.processor.process_quality(
            audio_bytes,
            enhance=False,
            normalize=True
        )
        return processed
    
    def _process_with_buffer(
        self,
        audio_bytes: AudioBytes,
        buffer: bytearray
    ) -> AudioBytes:
        """Process using pre-allocated buffer for zero-copy"""
        # Copy input to buffer
        buffer[:len(audio_bytes)] = audio_bytes
        
        # Process in-place (simplified - real implementation would modify buffer)
        # For now, just validate and return
        if self.processor._validators['min_size'](len(audio_bytes)):
            return bytes(buffer[:len(audio_bytes)])
        else:
            raise AudioError("Invalid audio size", AudioErrorType.VALIDATION_ERROR)
    
    # ============== Adaptive Optimization ==============
    
    def _should_use_fast_path(self) -> bool:
        """Determine if fast path should be used based on recent performance"""
        if not self._processing_history:
            return True
        
        # Calculate recent average latency
        recent_avg = sum(self._processing_history) / len(self._processing_history) * 1000
        
        # Use fast path if recent latency is high
        return recent_avg > self._adaptive_threshold
    
    def set_adaptive_threshold(self, threshold_ms: float):
        """Set threshold for adaptive processing switching"""
        self._adaptive_threshold = threshold_ms
        self.logger.info(f"Adaptive threshold set to {threshold_ms}ms")
    
    # ============== Pipeline Management ==============
    
    def add_pre_processor(self, processor: Callable[[AudioBytes], AudioBytes]):
        """Add pre-processing stage"""
        self._pre_processors.append(processor)
    
    def add_post_processor(self, processor: Callable[[AudioBytes], AudioBytes]):
        """Add post-processing stage"""
        self._post_processors.append(processor)
    
    def process_with_pipeline(self, audio_bytes: AudioBytes) -> AudioBytes:
        """Process through full pipeline with pre/post processors"""
        # Pre-processing
        for processor in self._pre_processors:
            audio_bytes = processor(audio_bytes)
        
        # Main processing
        audio_bytes = self.process_audio(audio_bytes)
        
        # Post-processing
        for processor in self._post_processors:
            audio_bytes = processor(audio_bytes)
        
        return audio_bytes
    
    # ============== Streaming Support ==============
    
    def process_stream(
        self,
        audio_chunks: List[AudioBytes],
        chunk_callback: Optional[Callable[[AudioBytes, int], None]] = None
    ) -> AudioBytes:
        """
        Process multiple chunks as a stream.
        
        Args:
            audio_chunks: List of audio chunks
            chunk_callback: Optional callback for each processed chunk
            
        Returns:
            Combined processed audio
        """
        processed_chunks = []
        
        for i, chunk in enumerate(audio_chunks):
            processed = self.process_audio(chunk)
            processed_chunks.append(processed)
            
            if chunk_callback:
                chunk_callback(processed, i)
        
        # Combine chunks
        return b''.join(processed_chunks)
    
    def add_to_stream_buffer(self, audio_bytes: AudioBytes) -> Optional[AudioBytes]:
        """
        Add audio to stream buffer (for quality mode).
        
        Returns processed audio when buffer is ready.
        """
        if not self._stream_buffer:
            # No buffering in realtime mode
            return self.process_audio(audio_bytes)
        
        # Add to buffer
        self._stream_buffer.add_audio(audio_bytes)
        
        # Check if we have enough for processing
        chunk_size = int(self.config.sample_rate * 200 / 1000 * self.config.channels * 2)  # 200ms chunks for quality
        
        if self._stream_buffer.get_available_bytes() >= chunk_size:
            chunk = self._stream_buffer.get_chunk(chunk_size)
            if chunk:
                return self.process_audio(chunk)
        
        return None
    
    # ============== Resource Management ==============
    
    def optimize_for_latency(self):
        """Optimize settings for minimum latency"""
        self.mode = ProcessingMode.REALTIME
        self.processor.mode = ProcessingMode.REALTIME
        
        # Ensure buffer pool is available
        if not self.buffer_pool:
            self._init_buffer_pool()
        
        # Clear any heavy processors
        self._pre_processors.clear()
        self._post_processors.clear()
        
        self.logger.info("Optimized for minimum latency")
    
    def optimize_for_quality(self):
        """Optimize settings for best quality"""
        self.mode = ProcessingMode.QUALITY
        self.processor.mode = ProcessingMode.QUALITY
        
        # Initialize stream buffer if needed
        if not self._stream_buffer:
            self._stream_buffer = StreamBuffer(
                config=self.buffer_config,
                audio_config=self.config,
                mode=ProcessingMode.QUALITY
            )
        
        self.logger.info("Optimized for quality")
    
    # ============== Metrics and Monitoring ==============
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive engine metrics"""
        with self._lock:
            metrics = self.metrics.to_dict()
        
        # Add engine-specific metrics
        metrics.update({
            "mode": self.mode.value,
            "has_buffer_pool": self.buffer_pool is not None,
            "pre_processors": len(self._pre_processors),
            "post_processors": len(self._post_processors),
            "adaptive_threshold_ms": self._adaptive_threshold
        })
        
        # Add buffer pool stats if available
        if self.buffer_pool:
            metrics["buffer_pool"] = {
                "pool_size": self.buffer_pool.pool_size,
                "buffer_size": self.buffer_pool.buffer_size,
                "available": len(self.buffer_pool.available),
                "in_use": len(self.buffer_pool.in_use)
            }
        
        # Add stream buffer stats if available
        if self._stream_buffer:
            metrics["stream_buffer"] = self._stream_buffer.get_stats()
        
        return metrics
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get detailed performance analysis"""
        metrics = self.get_metrics()
        
        # Add performance analysis
        if self.metrics.total_chunks > 0:
            # Calculate throughput
            if self.metrics.total_processing_time > 0:
                throughput_mbps = (
                    self.metrics.total_bytes / 1024 / 1024 / 
                    self.metrics.total_processing_time
                )
            else:
                throughput_mbps = 0
            
            # Determine if meeting realtime requirements
            realtime_capable = self.metrics.avg_latency_ms < 20  # 20ms threshold
            
            metrics["performance"] = {
                "throughput_mbps": throughput_mbps,
                "realtime_capable": realtime_capable,
                "processing_efficiency": (
                    1.0 - (self.metrics.avg_latency_ms / 100)  # Efficiency score
                    if self.metrics.avg_latency_ms < 100 else 0
                )
            }
        
        return metrics
    
    def reset_metrics(self):
        """Reset all metrics"""
        with self._lock:
            self.metrics = StreamMetrics()
            self._processing_history.clear()
        
        self.logger.info("Metrics reset")
    
    # ============== Audio Capture & Playback ==============
    
    def configure_devices(self, input_device: Optional[int] = None, output_device: Optional[int] = None):
        """Configure audio input/output devices"""
        self._input_device = input_device
        self._output_device = output_device
        self.logger.info(f"Configured devices - Input: {input_device}, Output: {output_device}")
    
    def configure_vad(self, vad_config: Optional[VADConfig] = None):
        """Configure Voice Activity Detection"""
        self._vad_config = vad_config
        if vad_config:
            self.logger.info(f"VAD configured: {vad_config.type.value}")
        else:
            self.logger.info("VAD disabled")
    
    async def start_capture_stream(self) -> Any:
        """
        Start audio capture and return an async stream.
        This is a placeholder for BaseEngine integration.
        Full implementation would create audio manager and return stream.
        """
        # Import here to avoid circular dependency
        from voxstream.io.manager import AudioManager, AudioManagerConfig
        
        if not hasattr(self, '_audio_manager'):
            # Create audio manager if not exists
            config = AudioManagerConfig(
                input_device=getattr(self, '_input_device', None),
                output_device=getattr(self, '_output_device', None),
                sample_rate=self.config.sample_rate,
                channels=self.config.channels,
                chunk_duration_ms=self.config.chunk_duration_ms,
                vad_enabled=hasattr(self, '_vad_config') and self._vad_config is not None,
                vad_config=getattr(self, '_vad_config', None)
            )
            
            self._audio_manager = AudioManager(config, logger=self.logger)
            await self._audio_manager.initialize()
        
        # Start capture and return queue
        return await self._audio_manager.start_capture()
    
    async def stop_capture_stream(self):
        """Stop audio capture"""
        if hasattr(self, '_audio_manager'):
            await self._audio_manager.stop_capture()
    
    def queue_playback(self, audio_data: AudioBytes):
        """Queue audio for playback through buffered player"""
        # Import here to avoid circular dependency
        from voxstream.io.player import BufferedAudioPlayer
        
        if not hasattr(self, '_buffered_player'):
            # Create buffered player if not exists
            self._buffered_player = BufferedAudioPlayer(
                config=self.config,
                device=getattr(self, '_output_device', None),
                logger=self.logger
            )
        
        # Queue audio for playback
        self._buffered_player.play(audio_data)
    
    def mark_playback_complete(self):
        """Mark that all audio has been received for playback"""
        if hasattr(self, '_buffered_player'):
            self._buffered_player.mark_complete()
    
    def interrupt_playback(self, force: bool = True):
        """Interrupt current audio playback"""
        if hasattr(self, '_buffered_player'):
            self._buffered_player.stop(force=force)
            self.logger.info("Playback interrupted")
    
    def set_playback_callbacks(
        self,
        completion_callback: Optional[Callable] = None,
        chunk_played_callback: Optional[Callable[[int], None]] = None
    ):
        """Set callbacks for playback events"""
        if hasattr(self, '_buffered_player'):
            if completion_callback:
                self._buffered_player.set_completion_callback(completion_callback)
            if chunk_played_callback:
                self._buffered_player.set_chunk_played_callback(chunk_played_callback)
    
    def process_vad_chunk(self, audio_chunk: AudioBytes) -> Optional[str]:
        """Process audio chunk through VAD if configured"""
        if hasattr(self, '_audio_manager'):
            return self._audio_manager.process_vad(audio_chunk)
        return None
    
    @property
    def is_playing(self) -> bool:
        """Check if audio is currently playing"""
        if hasattr(self, '_buffered_player'):
            return self._buffered_player.is_actively_playing
        return False
    
    # ============== Enhanced Metrics ==============
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive engine metrics"""
        with self._lock:
            metrics = self.metrics.to_dict()
        
        # Add engine-specific metrics
        metrics.update({
            "mode": self.mode.value,
            "has_buffer_pool": self.buffer_pool is not None,
            "pre_processors": len(self._pre_processors),
            "post_processors": len(self._post_processors),
            "adaptive_threshold_ms": self._adaptive_threshold,
            "is_playing": self.is_playing  # Add playback status
        })
        
        # Add buffer pool stats if available
        if self.buffer_pool:
            metrics["buffer_pool"] = {
                "pool_size": self.buffer_pool.pool_size,
                "buffer_size": self.buffer_pool.buffer_size,
                "available": len(self.buffer_pool.available),
                "in_use": len(self.buffer_pool.in_use)
            }
        
        # Add stream buffer stats if available
        if self._stream_buffer:
            metrics["stream_buffer"] = self._stream_buffer.get_stats()
        
        # Add component metrics
        if hasattr(self, '_audio_manager'):
            metrics["audio_manager"] = self._audio_manager.get_metrics()
        
        if hasattr(self, '_buffered_player'):
            metrics["buffered_player"] = self._buffered_player.get_metrics()
        
        return metrics
    
    # ============== Cleanup ==============
    
    async def cleanup_async(self):
        """Async cleanup for audio components"""
        # Cleanup audio manager
        if hasattr(self, '_audio_manager'):
            await self._audio_manager.cleanup()
        
        # Stop buffered player
        if hasattr(self, '_buffered_player'):
            self._buffered_player.stop(force=True)
        
        # Call sync cleanup
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        # Clear processors
        self._pre_processors.clear()
        self._post_processors.clear()
        
        # Clear buffer pool
        if self.buffer_pool:
            self.buffer_pool = None
        
        # Clear stream buffer
        if self._stream_buffer:
            self._stream_buffer.clear()
            self._stream_buffer = None
        
        # Reset metrics
        self.reset_metrics()
        
        self.logger.info("VoxStream cleaned up")


# ============== Factory Functions ==============

def create_fast_lane_engine(
    sample_rate: int = 24000,
    chunk_duration_ms: int = 20,
    input_device: Optional[int] = None,
    output_device: Optional[int] = None,
    vad_config: Optional[VADConfig] = None
) -> VoxStream:
    """Create engine optimized for fast lane"""
    config = StreamConfig(
        sample_rate=sample_rate,
        chunk_duration_ms=chunk_duration_ms,
        use_numpy=False,  # Disable numpy for speed
        pre_allocate_buffers=True
    )
    
    buffer_config = BufferConfig(
        pre_allocate=True,
        use_circular=True,
        zero_copy=True,
        pool_size=20,  # More buffers for fast lane
        pool_buffer_size=sample_rate // 10  # 100ms max
    )
    
    engine = VoxStream(
        mode=ProcessingMode.REALTIME,
        config=config,
        buffer_config=buffer_config
    )
    
    # Configure devices and VAD
    engine.configure_devices(input_device, output_device)
    if vad_config:
        engine.configure_vad(vad_config)
    
    return engine


def create_big_lane_engine(
    sample_rate: int = 24000,
    enable_enhancement: bool = True
) -> VoxStream:
    """Create engine optimized for big lane"""
    config = StreamConfig(
        sample_rate=sample_rate,
        chunk_duration_ms=200,  # Larger chunks for quality
        use_numpy=True,
        pre_allocate_buffers=False
    )
    
    buffer_config = BufferConfig(
        pre_allocate=False,
        use_circular=False,
        max_size_bytes=10 * 1024 * 1024,  # 10MB buffer
        overflow_strategy="drop_oldest"
    )
    
    engine = VoxStream(
        mode=ProcessingMode.QUALITY,
        config=config,
        buffer_config=buffer_config
    )
    
    # Add enhancement if requested
    if enable_enhancement:
        # Could add enhancement processors here
        pass
    
    return engine


def create_adaptive_engine(
    sample_rate: int = 24000,
    latency_target_ms: float = 50.0
) -> VoxStream:
    """Create adaptive engine that switches modes based on load"""
    config = StreamConfig(
        sample_rate=sample_rate,
        chunk_duration_ms=50,  # Medium chunks
        use_numpy=True,
        pre_allocate_buffers=True
    )
    
    engine = VoxStream(
        mode=ProcessingMode.BALANCED,
        config=config
    )
    
    # Set adaptive threshold
    engine.set_adaptive_threshold(latency_target_ms)
    
    return engine