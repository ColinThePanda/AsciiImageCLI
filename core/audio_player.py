import pyaudio
import threading
import numpy as np
import warnings
from typing import Generator

class AudioPlayer:
    def __init__(self, audio_gen: Generator[np.ndarray, None, None],
                 samplerate=44100, channels=2, blocksize=1024,
                 enable_audio=True):
        self.audio_gen = audio_gen
        self.samplerate = samplerate
        self.channels = channels
        self.blocksize = blocksize
        self.buffer = np.empty((0, channels), dtype=np.float32)
        self.lock = threading.Lock()
        self.done = False
        self.stream = None
        self.feed_thread = None
        self.stopped = False
        self.enable_audio = enable_audio
        self.p = None

    def _check_audio_available(self):
        """Quick check if audio is available - full init happens in start()"""
        try:
            # Just do a minimal check - don't enumerate all devices
            p = pyaudio.PyAudio()
            # Quick check: just verify we can get default output device
            try:
                default_output = p.get_default_output_device_info()
                has_output = int(default_output['maxOutputChannels']) > 0
            except Exception:
                has_output = False
            
            p.terminate()
            
            if not has_output:
                warnings.warn("Audio disabled: no output devices found")
                return False
            
            return True
            
        except Exception as e:
            warnings.warn(f"Audio disabled: {e}")
            return False

    def callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback function"""
        with self.lock:
            if len(self.buffer) >= frame_count:
                data = self.buffer[:frame_count]
                self.buffer = self.buffer[frame_count:]
            else:
                # Not enough data, pad with zeros
                data = np.zeros((frame_count, self.channels), dtype=np.float32)
                if len(self.buffer) > 0:
                    data[:len(self.buffer)] = self.buffer
                    self.buffer = np.empty((0, self.channels), dtype=np.float32)
        
        return (data.tobytes(), pyaudio.paContinue)

    def start(self):
        if not self.enable_audio:
            self._start_silent_consumer()
            return

        try:
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=self.channels,
                rate=self.samplerate,
                output=True,
                frames_per_buffer=self.blocksize,
                stream_callback=self.callback
            )
            self.stream.start_stream()
        except Exception as e:
            warnings.warn(f"Could not start audio stream: {e}")
            self.enable_audio = False
            if self.p:
                self.p.terminate()
                self.p = None
            self._start_silent_consumer()
            return

        def feed():
            try:
                for chunk in self.audio_gen:
                    if self.stopped:
                        break
                    if not isinstance(chunk, np.ndarray):
                        chunk = np.array(chunk, dtype=np.float32)
                    if chunk.dtype != np.float32:
                        chunk = chunk.astype(np.float32) / 32768.0
                    if chunk.ndim == 1 and self.channels == 2:
                        chunk = np.stack([chunk, chunk], axis=-1)
                    elif chunk.ndim == 2 and chunk.shape[1] != self.channels:
                        if chunk.shape[1] == 1:
                            chunk = np.repeat(chunk, self.channels, axis=1)
                        else:
                            warnings.warn("Audio chunk channel mismatch; skipping")
                            continue
                    with self.lock:
                        self.buffer = np.concatenate([self.buffer, chunk])
            except Exception as e:
                warnings.warn(f"Audio feed thread exception: {e}")
            finally:
                self.done = True

        self.feed_thread = threading.Thread(target=feed, daemon=True)
        self.feed_thread.start()

    def _start_silent_consumer(self):
        """Consume generator without audio output"""
        def feed_silent():
            try:
                for _ in self.audio_gen:
                    if self.stopped:
                        break
            except Exception as e:
                warnings.warn(f"Audio generator exception: {e}")
            finally:
                self.done = True
        
        self.feed_thread = threading.Thread(target=feed_silent, daemon=True)
        self.feed_thread.start()
    
    def stop(self):
        self.stopped = True
        if self.feed_thread and self.feed_thread.is_alive():
            self.feed_thread.join(timeout=0.5)
        if self.stream:
            try:
                import time
                time.sleep(0.1)
                if self.stream.is_active():
                    self.stream.stop_stream()
                time.sleep(0.05)
                self.stream.close()
            except Exception:
                pass
            self.stream = None
        if self.p:
            try:
                self.p.terminate()
            except Exception:
                pass
            self.p = None