import os
import sys
import threading
import numpy as np
from typing import Optional, Dict, Any

# Configure ffmpeg path for pydub
_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ffmpeg_dir = os.path.join(_app_dir, 'ffmpeg', 'bin')
if os.path.isdir(_ffmpeg_dir):
    os.environ['PATH'] = _ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')


class AudioProcessor:
    """Handle audio loading, processing, and playback."""

    def __init__(self):
        """Initialize audio processor."""
        self.audio_data: Optional[np.ndarray] = None
        self.sample_rate: Optional[int] = None
        self.original_audio: Optional[np.ndarray] = None
        self.duration: float = 0
        self.is_playing: bool = False
        self._play_lock = threading.Lock()

    def load_audio(self, filepath: str) -> bool:
        """Load audio file. Tries soundfile first, then pydub for MP3/AAC/M4A/WMA."""
        # Try soundfile first (WAV, FLAC, OGG, AIFF)
        try:
            import soundfile as sf
            data, sr = sf.read(filepath)
            if data.ndim > 1:
                data = np.mean(data, axis=1)
            self.audio_data = data
            self.sample_rate = sr
            self.original_audio = data.copy()
            self.duration = len(data) / sr
            return True
        except Exception:
            pass

        # Fallback to pydub for MP3, AAC, M4A, WMA (requires ffmpeg)
        try:
            from pydub import AudioSegment
            audio_segment = AudioSegment.from_file(filepath)
            # Convert to numpy array
            samples = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
            if audio_segment.channels == 2:
                samples = samples.reshape((-1, 2))
                samples = np.mean(samples, axis=1)
            # Normalize to -1.0 to 1.0
            max_val = np.max(np.abs(samples))
            if max_val > 0:
                samples = samples / max_val
            self.audio_data = samples
            self.sample_rate = audio_segment.frame_rate
            self.original_audio = samples.copy()
            self.duration = len(samples) / audio_segment.frame_rate
            return True
        except ImportError:
            print("Error: pydub not installed. Run: pip install pydub")
            print("Also requires ffmpeg in app_voice_filter/ffmpeg/bin/ or in PATH")
            return False
        except Exception as e:
            print(f"Error loading audio: {e}")
            return False

    def save_audio(self, filepath: str, audio_data: Optional[np.ndarray] = None) -> bool:
        """Save audio file. Supports WAV/FLAC via soundfile, MP3 via pydub+ffmpeg."""
        data = audio_data if audio_data is not None else self.audio_data
        if data is None:
            return False

        ext = os.path.splitext(filepath)[1].lower()

        # MP3 export via pydub
        if ext == '.mp3':
            try:
                from pydub import AudioSegment
                # Convert numpy array to pydub AudioSegment
                samples = (data * 32767).astype(np.int16)
                audio_segment = AudioSegment(
                    samples.tobytes(),
                    frame_rate=self.sample_rate,
                    sample_width=2,
                    channels=1
                )
                audio_segment.export(filepath, format="mp3")
                return True
            except ImportError:
                print("Error: pydub not installed. Run: pip install pydub")
                return False
            except Exception as e:
                print(f"Error saving MP3: {e}")
                return False

        # WAV/FLAC/OGG export via soundfile
        try:
            import soundfile as sf
            sf.write(filepath, data, self.sample_rate)
            return True
        except ImportError:
            print("Error: soundfile not installed. Run: pip install soundfile")
            return False
        except Exception as e:
            print(f"Error saving audio: {e}")
            return False

    def play_audio(self, audio: np.ndarray, callback: Optional[callable] = None,
                   playback_id: int = 0) -> None:
        """Play audio in a separate thread."""
        try:
            import sounddevice as sd
        except ImportError:
            print("Error: sounddevice not installed. Run: pip install sounddevice")
            return
        except OSError as e:
            print(f"Error: audio backend not available ({e}). On Linux, install libportaudio2.")
            return

        # Stop any ongoing playback first (must be outside lock to avoid deadlock)
        was_playing = False
        with self._play_lock:
            was_playing = self.is_playing
            self.is_playing = True
        if was_playing:
            try:
                sd.stop()
            except Exception:
                pass

        def _play():
            try:
                sd.play(audio, self.sample_rate)
                sd.wait()
            except Exception as e:
                print(f"Playback error: {e}")
            finally:
                with self._play_lock:
                    self.is_playing = False
                if callback:
                    callback(playback_id)

        thread = threading.Thread(target=_play, daemon=True)
        thread.start()

    def stop_playback(self) -> None:
        """Stop audio playback."""
        with self._play_lock:
            self.is_playing = False
        try:
            import sounddevice as sd
            sd.stop()
        except Exception:
            pass

    # Basic effects
    def apply_volume(self, audio: np.ndarray, volume: float) -> np.ndarray:
        """Apply volume adjustment (0.0 to 2.0)."""
        if volume == 1.0:
            return audio
        return np.clip(audio * volume, -1.0, 1.0)

    def apply_pitch(self, audio: np.ndarray, pitch_shift: float) -> np.ndarray:
        """Apply pitch shift in semitones (-12 to +12)."""
        if pitch_shift == 0:
            return audio
        factor = 2 ** (pitch_shift / 12.0)
        indices = np.linspace(0, len(audio) - 1, int(len(audio) / factor))
        return np.interp(indices, np.arange(len(audio)), audio)

    def apply_speed(self, audio: np.ndarray, speed: float) -> np.ndarray:
        """Apply speed change (0.5x to 2.0x)."""
        if speed == 1.0:
            return audio
        indices = np.linspace(0, len(audio) - 1, int(len(audio) / speed))
        return np.interp(indices, np.arange(len(audio)), audio)

    # EQ effects
    def apply_eq_band(self, audio: np.ndarray, center_freq: float,
                      gain_db: float, q: float = 1.0) -> np.ndarray:
        """Apply single band EQ."""
        if gain_db == 0:
            return audio
        from scipy.signal import lfilter
        gain = 10 ** (gain_db / 20.0)
        w0 = 2 * np.pi * center_freq / self.sample_rate
        alpha = np.sin(w0) / (2 * q)
        b0 = 1 + alpha * gain
        b1 = -2 * np.cos(w0)
        b2 = 1 - alpha * gain
        a0 = 1 + alpha / gain
        a1 = -2 * np.cos(w0)
        a2 = 1 - alpha / gain
        b = np.array([b0, b1, b2]) / a0
        a = np.array([1.0, a1 / a0, a2 / a0])
        return lfilter(b, a, audio)

    def apply_low_pass(self, audio: np.ndarray, cutoff: float) -> np.ndarray:
        """Apply low-pass filter."""
        from scipy.signal import butter, filtfilt
        nyq = self.sample_rate / 2
        cutoff = min(cutoff / nyq, 0.99)
        b, a = butter(4, cutoff, btype='low')
        return filtfilt(b, a, audio)

    def apply_high_pass(self, audio: np.ndarray, cutoff: float) -> np.ndarray:
        """Apply high-pass filter."""
        from scipy.signal import butter, filtfilt
        nyq = self.sample_rate / 2
        cutoff = min(cutoff / nyq, 0.99)
        b, a = butter(4, cutoff, btype='high')
        return filtfilt(b, a, audio)

    # Modulation effects
    def apply_chorus(self, audio: np.ndarray, depth: float = 0.5,
                     rate: float = 1.0) -> np.ndarray:
        """Apply chorus effect."""
        if depth == 0:
            return audio
        t = np.arange(len(audio)) / self.sample_rate
        mod = depth * np.sin(2 * np.pi * rate * t)
        delay_samples = (mod * self.sample_rate * 0.01).astype(int)
        output = audio.copy()
        for i in range(len(audio)):
            delay = delay_samples[i]
            if i + delay < len(audio):
                output[i] = (audio[i] + audio[i + delay] * depth) / (1 + depth)
        return output

    def apply_flanger(self, audio: np.ndarray, depth: float = 0.5,
                      rate: float = 0.5) -> np.ndarray:
        """Apply flanger effect."""
        if depth == 0:
            return audio
        t = np.arange(len(audio)) / self.sample_rate
        mod = depth * (np.sin(2 * np.pi * rate * t) + 1) / 2
        delay_samples = (mod * self.sample_rate * 0.005).astype(int)
        output = audio.copy()
        for i in range(len(audio)):
            delay = delay_samples[i]
            if i + delay < len(audio):
                output[i] = audio[i] * 0.7 + audio[i + delay] * 0.3 * depth
        return output

    def apply_phaser(self, audio: np.ndarray, depth: float = 0.5,
                     rate: float = 0.5) -> np.ndarray:
        """Apply phaser effect."""
        if depth == 0:
            return audio
        from scipy.signal import lfilter
        t = np.arange(len(audio)) / self.sample_rate
        mod = (np.sin(2 * np.pi * rate * t) + 1) / 2
        output = audio.copy()
        stages = 4
        for _ in range(stages):
            b = [1, 0]
            a = [1, -0.9]
            output = lfilter(b, a, output)
        return np.clip(output * (1 + depth * 0.3), -1.0, 1.0)

    def apply_tremolo(self, audio: np.ndarray, depth: float = 0.5,
                      rate: float = 5.0) -> np.ndarray:
        """Apply tremolo (amplitude modulation)."""
        if depth == 0:
            return audio
        t = np.arange(len(audio)) / self.sample_rate
        mod = 1 - depth + depth * np.sin(2 * np.pi * rate * t)
        return np.clip(audio * mod, -1.0, 1.0)

    def apply_vibrato(self, audio: np.ndarray, depth: float = 0.5,
                      rate: float = 5.0) -> np.ndarray:
        """Apply vibrato (frequency modulation)."""
        if depth == 0:
            return audio
        t = np.arange(len(audio)) / self.sample_rate
        mod = depth * np.sin(2 * np.pi * rate * t)
        indices = np.arange(len(audio)) + mod * self.sample_rate * 0.01
        indices = np.clip(indices, 0, len(audio) - 1)
        return np.interp(indices, np.arange(len(audio)), audio)

    # Distortion effects
    def apply_distortion(self, audio: np.ndarray, amount: float = 0.5) -> np.ndarray:
        """Apply soft clipping distortion."""
        if amount == 0:
            return audio
        gain = 1 + amount * 10
        return np.tanh(audio * gain) / np.tanh(gain)

    def apply_bitcrusher(self, audio: np.ndarray, bits: float = 8) -> np.ndarray:
        """Apply bitcrusher effect."""
        if bits >= 32:
            return audio
        levels = 2 ** bits
        return np.round(audio * levels) / levels

    def apply_overdrive(self, audio: np.ndarray, gain: float = 2.0) -> np.ndarray:
        """Apply overdrive effect."""
        if gain == 1.0:
            return audio
        return np.clip(audio * gain, -1.0, 1.0)

    # Time-based effects
    def apply_reverb(self, audio: np.ndarray, amount: float = 0.3) -> np.ndarray:
        """Apply reverb effect."""
        if amount == 0:
            return audio
        delays = [50, 80, 120, 170]
        output = audio.copy()
        for delay_ms in delays:
            delay_samples = int(self.sample_rate * delay_ms / 1000)
            decay = amount * 0.3
            for i in range(delay_samples, len(output)):
                output[i] += output[i - delay_samples] * decay
        return np.clip(output, -1.0, 1.0)

    def apply_delay(self, audio: np.ndarray, delay_ms: float = 100,
                    feedback: float = 0.3) -> np.ndarray:
        """Apply delay effect."""
        if delay_ms == 0:
            return audio
        delay_samples = int(self.sample_rate * delay_ms / 1000)
        output = audio.copy()
        for i in range(delay_samples, len(output)):
            output[i] += output[i - delay_samples] * feedback
        return np.clip(output, -1.0, 1.0)

    # Dynamics effects
    def apply_compression(self, audio: np.ndarray, threshold_db: float = -20.0,
                          ratio: float = 4.0) -> np.ndarray:
        """Apply dynamic range compression."""
        threshold = 10 ** (threshold_db / 20.0)
        output = audio.copy()
        for i in range(len(audio)):
            level = abs(audio[i])
            if level > threshold:
                excess_db = 20 * np.log10(level / threshold)
                reduced_db = excess_db / ratio
                gain = 10 ** ((reduced_db - excess_db) / 20.0)
                output[i] = audio[i] * gain
        return output

    def apply_gate(self, audio: np.ndarray, threshold_db: float = -30.0) -> np.ndarray:
        """Apply noise gate."""
        threshold = 10 ** (threshold_db / 20.0)
        output = audio.copy()
        for i in range(len(audio)):
            if abs(audio[i]) < threshold:
                output[i] = 0
        return output

    # Utility effects
    def apply_fade_in(self, audio: np.ndarray, duration_ms: int) -> np.ndarray:
        """Apply fade in."""
        if duration_ms == 0:
            return audio
        fade_samples = int(self.sample_rate * duration_ms / 1000)
        fade_samples = min(fade_samples, len(audio))
        output = audio.copy()
        output[:fade_samples] *= np.linspace(0, 1, fade_samples)
        return output

    def apply_fade_out(self, audio: np.ndarray, duration_ms: int) -> np.ndarray:
        """Apply fade out."""
        if duration_ms == 0:
            return audio
        fade_samples = int(self.sample_rate * duration_ms / 1000)
        fade_samples = min(fade_samples, len(audio))
        output = audio.copy()
        output[-fade_samples:] *= np.linspace(1, 0, fade_samples)
        return output

    def apply_normalize(self, audio: np.ndarray, target_db: float = 0.0) -> np.ndarray:
        """Normalize audio to target level."""
        if target_db == 0:
            return audio
        rms = np.sqrt(np.mean(audio ** 2))
        if rms == 0:
            return audio
        current_db = 20 * np.log10(rms)
        gain = 10 ** ((target_db - current_db) / 20.0)
        return np.clip(audio * gain, -1.0, 1.0)

    def apply_trim(self, audio: np.ndarray, start_sec: float, end_sec: float) -> np.ndarray:
        """Trim audio to time range."""
        start_sample = int(start_sec * self.sample_rate)
        end_sample = int(end_sec * self.sample_rate)
        start_sample = max(0, start_sample)
        end_sample = min(len(audio), end_sample)
        return audio[start_sample:end_sample]

    def apply_reverse(self, audio: np.ndarray) -> np.ndarray:
        """Reverse audio."""
        return audio[::-1].copy()

    def apply_process_all(self, params: Dict[str, Any]) -> np.ndarray:
        """Process audio with all parameters."""
        if self.original_audio is None:
            return np.array([])
        audio = self.original_audio.copy()

        # Basic
        volume = params.get('volume', 1.0)
        if volume != 1.0:
            audio = self.apply_volume(audio, volume)

        speed = params.get('speed', 1.0)
        if speed != 1.0:
            audio = self.apply_speed(audio, speed)

        pitch = params.get('pitch', 0.0)
        if pitch != 0.0:
            audio = self.apply_pitch(audio, pitch)

        # EQ
        eq = params.get('eq', {})
        eq_values = [eq.get('bass', 0), eq.get('low_mid', 0), eq.get('mid', 0),
                     eq.get('high_mid', 0), eq.get('treble', 0)]
        if any(v != 0 for v in eq_values):
            freqs = [100, 400, 1000, 2500, 6000]
            for freq, val in zip(freqs, eq_values):
                audio = self.apply_eq_band(audio, freq, val)

        # Filters
        low_pass = params.get('low_pass', 20000)
        if low_pass < 20000:
            audio = self.apply_low_pass(audio, low_pass)

        high_pass = params.get('high_pass', 20)
        if high_pass > 20:
            audio = self.apply_high_pass(audio, high_pass)

        # Modulation
        modulation = {
            'chorus': params.get('chorus', 0),
            'flanger': params.get('flanger', 0),
            'phaser': params.get('phaser', 0),
            'tremolo': params.get('tremolo', 0),
            'vibrato': params.get('vibrato', 0),
        }
        if any(v != 0 for v in modulation.values()):
            audio = self.apply_chorus(audio, modulation['chorus'])
            audio = self.apply_flanger(audio, modulation['flanger'])
            audio = self.apply_phaser(audio, modulation['phaser'])
            audio = self.apply_tremolo(audio, modulation['tremolo'])
            audio = self.apply_vibrato(audio, modulation['vibrato'])

        # Distortion
        distortion = params.get('distortion', 0)
        if distortion != 0:
            audio = self.apply_distortion(audio, distortion)

        bitcrusher = params.get('bitcrusher', 32)
        if bitcrusher < 32:
            audio = self.apply_bitcrusher(audio, bitcrusher)

        overdrive = params.get('overdrive', 1.0)
        if overdrive != 1.0:
            audio = self.apply_overdrive(audio, overdrive)

        # Time-based
        reverb = params.get('reverb', 0)
        if reverb != 0:
            audio = self.apply_reverb(audio, reverb)

        delay = params.get('delay', 0)
        if delay != 0:
            audio = self.apply_delay(audio, delay)

        # Dynamics
        comp_threshold = params.get('comp_threshold', -20.0)
        comp_ratio = params.get('comp_ratio', 4.0)
        if comp_threshold != -20.0 or comp_ratio != 4.0:
            audio = self.apply_compression(audio, comp_threshold, comp_ratio)

        gate = params.get('gate', -30.0)
        if gate != -30.0:
            audio = self.apply_gate(audio, gate)

        # Utility
        fade_in = params.get('fade_in', 0)
        if fade_in != 0:
            audio = self.apply_fade_in(audio, fade_in)

        fade_out = params.get('fade_out', 0)
        if fade_out != 0:
            audio = self.apply_fade_out(audio, fade_out)

        normalize = params.get('normalize', 0)
        if normalize != 0:
            audio = self.apply_normalize(audio, normalize)

        # Trim
        trim_start = params.get('trim_start', 0)
        trim_end = params.get('trim_end', self.duration)
        if trim_start > 0 or trim_end < self.duration:
            audio = self.apply_trim(audio, trim_start, trim_end)

        # Reverse
        if params.get('reverse', False):
            audio = self.apply_reverse(audio)

        return audio
