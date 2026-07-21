"""
Voice Filter - Audio Processing Application

A GUI application for loading and modifying audio files in real-time.
Supports WAV, MP3, AAC, and other common audio formats.

Features:
- 20+ audio effects and filters
- Auto-preview mode (plays on slider release)
- Color-coded UI
- Cross-platform (Windows, Linux, macOS)

Usage:
    python voice_filter.py
"""

import os
import sys
import platform
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from typing import Optional, Dict, Any
import time
import queue

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MACOS = platform.system() == "Darwin"


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
        """Load audio file."""
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
        except Exception as e:
            print(f"Error loading audio: {e}")
            return False

    def save_audio(self, filepath: str, audio_data: Optional[np.ndarray] = None) -> bool:
        """Save audio file."""
        try:
            import soundfile as sf
            data = audio_data if audio_data is not None else self.audio_data
            if data is None:
                return False
            sf.write(filepath, data, self.sample_rate)
            return True
        except Exception as e:
            print(f"Error saving audio: {e}")
            return False

    def play_audio(self, audio: np.ndarray, callback: Optional[callable] = None,
                   playback_id: int = 0) -> None:
        """Play audio in a separate thread."""
        # Stop any ongoing playback first (must be outside lock to avoid deadlock)
        was_playing = False
        with self._play_lock:
            was_playing = self.is_playing
            self.is_playing = True
        if was_playing:
            try:
                import sounddevice as sd
                sd.stop()
            except Exception:
                pass

        def _play():
            try:
                import sounddevice as sd
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


# Color scheme - Professional mixer console style
COLORS = {
    # Main background - dark brushed metal
    'bg': '#1a1a1a',
    'bg_light': '#252525',
    'bg_medium': '#2a2a2a',
    'fg': '#e0e0e0',
    'fg_dim': '#888888',
    'accent': '#4a9eff',

    # Status colors
    'success': '#4caf50',
    'warning': '#ff9800',
    'error': '#f44336',

    # Channel strip colors (one per tab)
    'basic': '#3d5afe',
    'eq': '#00bcd4',
    'modulation': '#9c27b0',
    'distortion': '#ff5722',
    'time': '#ff9800',
    'dynamics': '#4caf50',
    'utility': '#607d8b',

    # Fader styling
    'fader_track': '#0d0d0d',
    'fader_groove': '#1a1a1a',
    'fader_thumb': '#555555',
    'fader_thumb_active': '#777777',
    'fader_thumb_edge': '#333333',

    # LED indicators
    'led_off': '#0a0a0a',
    'led_green': '#00cc00',
    'led_green_dim': '#004400',
    'led_yellow': '#cccc00',
    'led_yellow_dim': '#444400',
    'led_red': '#cc0000',
    'led_red_dim': '#440000',

    # Channel strip styling
    'channel_bg': '#1e1e1e',
    'channel_border': '#333333',
    'channel_label': '#666666',
    'meter_bg': '#0a0a0a',

    # Transport controls
    'button_bg': '#3a3a3a',
    'button_active': '#4a4a4a',
    'button_hover': '#4a4a4a',
}


class MixerFader(tk.Canvas):
    """Custom mixer-style fader widget."""

    def __init__(self, parent, variable: tk.DoubleVar, from_: float = 0.0,
                 to: float = 1.0, width: int = 60, height: int = 150,
                 orientation: str = 'vertical', color: str = None,
                 on_release: callable = None, on_press: callable = None, **kwargs):
        """Initialize mixer fader.

        Args:
            parent: Parent widget
            variable: Tkinter variable to bind
            from_: Minimum value
            to: Maximum value
            width: Widget width
            height: Widget height
            orientation: 'vertical' or 'horizontal'
            color: Accent color
            on_release: Callback when slider is released
            on_press: Callback when slider is pressed
        """
        super().__init__(parent, width=width, height=height,
                         bg=COLORS['channel_bg'], highlightthickness=0, **kwargs)

        self.variable = variable
        self.from_ = from_
        self.to = to
        self.width = width
        self.height = height
        self.orientation = orientation
        self.color = color or COLORS['accent']
        self.on_release = on_release
        self.on_press = on_press
        self.isDragging = False
        self.audio_level = 0.0  # External audio level for animation

        # Fader dimensions
        self.track_width = 8
        self.thumb_width = 30
        self.thumb_height = 12
        self.led_count = 10

        # Calculate track bounds
        if orientation == 'vertical':
            self.track_x = (width - self.track_width) // 2
            self.track_top = 20
            self.track_bottom = height - 20
            self.track_height = self.track_bottom - self.track_top
        else:
            self.track_y = (height - self.track_width) // 2
            self.track_left = 20
            self.track_right = width - 20
            self.track_width_actual = self.track_right - self.track_left

        # Draw initial state
        self._draw()

        # Bind events
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<B1-Motion>', self._on_drag)
        self.bind('<ButtonRelease-1>', self._on_release)

    def set_audio_level(self, level: float) -> None:
        """Set audio level for meter animation (0.0 to 1.0)."""
        self.audio_level = max(0.0, min(1.0, level))
        self._draw()

    def _value_to_position(self, value: float) -> float:
        """Convert value to pixel position."""
        if self.orientation == 'vertical':
            # Invert for vertical (top = max, bottom = min)
            normalized = (value - self.from_) / (self.to - self.from_)
            return self.track_bottom - (normalized * self.track_height)
        else:
            normalized = (value - self.from_) / (self.to - self.from_)
            return self.track_left + (normalized * self.track_width_actual)

    def _position_to_value(self, pos: float) -> float:
        """Convert pixel position to value."""
        if self.orientation == 'vertical':
            normalized = (self.track_bottom - pos) / self.track_height
        else:
            normalized = (pos - self.track_left) / self.track_width_actual
        normalized = max(0.0, min(1.0, normalized))
        return self.from_ + (normalized * (self.to - self.from_))

    def _draw(self):
        """Draw the fader."""
        self.delete('all')

        if self.orientation == 'vertical':
            self._draw_vertical()
        else:
            self._draw_horizontal()

    def _draw_vertical(self):
        """Draw vertical fader with professional mixer styling."""
        # Draw LED meter on the right side (uses audio_level for animation)
        led_x = self.track_x + self.track_width + 8

        for i in range(self.led_count):
            led_y = self.track_top + (i * self.track_height / self.led_count)
            led_h = self.track_height / self.led_count - 2

            # Determine LED color based on audio level
            if i / self.led_count > self.audio_level:
                color = COLORS['led_off']
            elif i < 6:
                color = COLORS['led_green']
            elif i < 8:
                color = COLORS['led_yellow']
            else:
                color = COLORS['led_red']

            self.create_rectangle(led_x, led_y, led_x + 6, led_y + led_h,
                                fill=color, outline='#0a0a0a', width=1)

        # Draw track background with metallic look
        self.create_rectangle(
            self.track_x - 1, self.track_top - 1,
            self.track_x + self.track_width + 1, self.track_bottom + 1,
            fill='#0a0a0a', outline='#111111'
        )

        # Draw track groove with depth effect
        self.create_rectangle(
            self.track_x, self.track_top,
            self.track_x + self.track_width, self.track_bottom,
            fill=COLORS['fader_track'], outline=COLORS['fader_groove']
        )

        # Draw center line
        center_y = self.track_top + self.track_height // 2
        self.create_line(
            self.track_x + 1, center_y,
            self.track_x + self.track_width - 1, center_y,
            fill=COLORS['fader_groove'], width=1
        )

        # Draw groove marks
        for i in range(21):
            y = self.track_top + (i * self.track_height / 20)
            self.create_line(
                self.track_x + 1, y,
                self.track_x + self.track_width - 1, y,
                fill=COLORS['fader_groove'] if i % 5 != 0 else COLORS['channel_border']
            )

        # Calculate thumb position
        thumb_pos = self._value_to_position(self.variable.get())
        thumb_x = self.track_x + self.track_width // 2 - self.thumb_width // 2
        thumb_y = thumb_pos - self.thumb_height // 2

        # Draw thumb shadow
        self.create_rectangle(
            thumb_x + 1, thumb_y + 1,
            thumb_x + self.thumb_width + 1, thumb_y + self.thumb_height + 1,
            fill='#000000', outline=''
        )

        # Draw thumb body with metallic gradient effect
        thumb_color = COLORS['fader_thumb_active'] if self.isDragging else COLORS['fader_thumb']
        self.create_rectangle(
            thumb_x, thumb_y,
            thumb_x + self.thumb_width, thumb_y + self.thumb_height,
            fill=thumb_color, outline=COLORS['fader_thumb_edge'], width=1
        )

        # Draw thumb highlight (top edge)
        self.create_line(
            thumb_x + 1, thumb_y + 1,
            thumb_x + self.thumb_width - 1, thumb_y + 1,
            fill='#666666'
        )

        # Draw thumb grip lines (concave groove effect)
        grip_y_center = thumb_y + self.thumb_height // 2
        for offset in [-3, -1, 1, 3]:
            self.create_line(
                thumb_x + 4, grip_y_center + offset,
                thumb_x + self.thumb_width - 4, grip_y_center + offset,
                fill='#333333'
            )

    def _draw_horizontal(self):
        """Draw horizontal fader."""
        # Draw track background
        self.create_rectangle(
            self.track_left, self.track_y,
            self.track_right, self.track_y + self.track_width,
            fill=COLORS['fader_track'], outline=COLORS['fader_groove']
        )

        # Draw track groove lines
        for i in range(11):
            x = self.track_left + (i * self.track_width_actual / 10)
            self.create_line(
                x, self.track_y + 2,
                x, self.track_y + self.track_width - 2,
                fill=COLORS['fader_groove']
            )

        # Calculate thumb position
        thumb_pos = self._value_to_position(self.variable.get())
        thumb_x = thumb_pos - self.thumb_height // 2
        thumb_y = self.track_y + self.track_width // 2 - self.thumb_width // 2

        # Draw thumb shadow
        self.create_rectangle(
            thumb_x + 2, thumb_y + 2,
            thumb_x + self.thumb_height + 2, thumb_y + self.thumb_width + 2,
            fill='#1a1a1a', outline=''
        )

        # Draw thumb body
        thumb_color = COLORS['fader_thumb_active'] if self.isDragging else COLORS['fader_thumb']
        self.create_rectangle(
            thumb_x, thumb_y,
            thumb_x + self.thumb_height, thumb_y + self.thumb_width,
            fill=thumb_color, outline='#555555', width=1
        )

        # Draw thumb grip lines
        grip_x_center = thumb_x + self.thumb_height // 2
        for offset in [-2, 0, 2]:
            self.create_line(
                grip_x_center + offset, thumb_y + 5,
                grip_x_center + offset, thumb_y + self.thumb_width - 5,
                fill='#444444'
            )

    def _on_press(self, event):
        """Handle mouse press."""
        self.isDragging = True
        if self.on_press:
            self.on_press()
        self._update_value(event)
        self._draw()

    def _on_drag(self, event):
        """Handle mouse drag."""
        if self.isDragging:
            self._update_value(event)
            self._draw()

    def _on_release(self, event):
        """Handle mouse release."""
        self.isDragging = False
        self._update_value(event)
        self._draw()
        if self.on_release:
            self.on_release()

    def _update_value(self, event):
        """Update value from mouse position."""
        if self.orientation == 'vertical':
            value = self._position_to_value(event.y)
        else:
            value = self._position_to_value(event.x)
        self.variable.set(round(value, 2))

    def set_value(self, value: float):
        """Set fader value programmatically."""
        self.variable.set(value)
        self._draw()


class AnalogVUMeter(tk.Canvas):
    """Analog VU meter with realistic needle bounce physics."""

    def __init__(self, parent, width: int = 140, height: int = 100,
                 color: str = None, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=COLORS['meter_bg'], highlightthickness=0, **kwargs)

        self.width = width
        self.height = height
        self.color = color or COLORS['accent']

        self.target_level = 0.0
        self.current_level = 0.0
        self.needle_velocity = 0.0

        self.attack_speed = 0.2
        self.decay_speed = 0.04
        self.damping = 0.82
        self.spring_constant = 0.35

        self.center_x = width // 2
        self.center_y = height // 2 + 5
        self.radius = min(width, height) // 2 - 12

        self.start_angle = 225
        self.end_angle = 315
        self.angle_range = self.end_angle - self.start_angle

        self.needle_length = self.radius - 8

        self.isAnimating = False
        self.animation_id = None

        self._draw()

    def set_level(self, level):
        """Set VU meter target level and start animation."""
        self.target_level = max(0.0, min(1.0, level))
        # Always start animation to move needle toward target
        if not self.isAnimating:
            self._start_animation()

    def _start_animation(self):
        self.isAnimating = True
        self._animate_needle()

    def _stop_animation(self):
        self.isAnimating = False
        if self.animation_id is not None:
            self.after_cancel(self.animation_id)
            self.animation_id = None

    def _animate_needle(self):
        if not self.isAnimating:
            return

        error = self.target_level - self.current_level
        spring_force = error * self.spring_constant

        if error > 0:
            self.needle_velocity += spring_force * self.attack_speed
        else:
            self.needle_velocity += spring_force * self.decay_speed

        self.needle_velocity *= self.damping
        self.current_level += self.needle_velocity
        self.current_level = max(0.0, min(1.0, self.current_level))

        self._draw()

        if abs(self.needle_velocity) > 0.001 or abs(error) > 0.01:
            self.animation_id = self.after(16, self._animate_needle)
        else:
            self.isAnimating = False

    def _draw(self):
        self.delete('all')

        self.create_oval(2, 2, self.width - 2, self.height - 2,
                        fill=COLORS['fader_track'], outline='#222222', width=2)
        self.create_oval(8, 8, self.width - 8, self.height - 8,
                        fill='#0f0f0f', outline='#1a1a1a', width=1)

        self._draw_colored_arc()
        self._draw_tick_marks()
        self._draw_labels()
        self._draw_needle()

        self.create_oval(self.center_x - 8, self.center_y - 8,
                        self.center_x + 8, self.center_y + 8,
                        fill='#2a2a2a', outline='#444444', width=2)
        self.create_oval(self.center_x - 4, self.center_y - 4,
                        self.center_x + 4, self.center_y + 4,
                        fill='#555555', outline='#666666', width=1)

    def _draw_colored_arc(self):
        green_end = self.start_angle + self.angle_range * 0.7
        self.create_arc(8, 8, self.width - 8, self.height - 8,
                       start=self.start_angle, extent=green_end - self.start_angle,
                       style='arc', outline=COLORS['led_green'], width=5)

        yellow_end = self.start_angle + self.angle_range * 0.85
        self.create_arc(8, 8, self.width - 8, self.height - 8,
                       start=green_end, extent=yellow_end - green_end,
                       style='arc', outline=COLORS['led_yellow'], width=5)

        self.create_arc(8, 8, self.width - 8, self.height - 8,
                       start=yellow_end, extent=self.end_angle - yellow_end,
                       style='arc', outline=COLORS['led_red'], width=5)

    def _draw_tick_marks(self):
        for i in range(11):
            angle = self.start_angle + (i / 10) * self.angle_range
            angle_rad = np.radians(angle)
            inner_r = self.radius - 5
            outer_r = self.radius + 5
            x1 = self.center_x + inner_r * np.cos(angle_rad)
            y1 = self.center_y - inner_r * np.sin(angle_rad)
            x2 = self.center_x + outer_r * np.cos(angle_rad)
            y2 = self.center_y - outer_r * np.sin(angle_rad)
            self.create_line(x1, y1, x2, y2, fill=COLORS['fg_dim'], width=1)

    def _draw_labels(self):
        labels = [-20, -10, -7, -5, -3, 0, +1, +2, +3]
        self._db_min = labels[0]   # -20 dB at needle position 0.0
        self._db_max = labels[-1]  # +3 dB at needle position 1.0
        for i, db in enumerate(labels):
            angle = self.start_angle + (i / (len(labels) - 1)) * self.angle_range
            angle_rad = np.radians(angle)
            label_r = self.radius + 14
            x = self.center_x + label_r * np.cos(angle_rad)
            y = self.center_y - label_r * np.sin(angle_rad)
            color = COLORS['led_green'] if db < 0 else COLORS['led_yellow'] if db < 2 else COLORS['led_red']
            self.create_text(x, y, text=str(db), fill=color, font=('', 7))

    def _draw_needle(self):
        """Draw needle with glow effect."""
        angle = self.start_angle + self.current_level * self.angle_range
        angle_rad = np.radians(angle)
        tip_x = self.center_x + self.needle_length * np.cos(angle_rad)
        tip_y = self.center_y - self.needle_length * np.sin(angle_rad)

        # Outer glow (large, dim)
        self.create_line(self.center_x, self.center_y, tip_x, tip_y,
                        fill='#440000', width=12, capstyle='round')
        # Middle glow
        self.create_line(self.center_x, self.center_y, tip_x, tip_y,
                        fill='#661111', width=8, capstyle='round')
        # Inner glow
        self.create_line(self.center_x, self.center_y, tip_x, tip_y,
                        fill='#882222', width=5, capstyle='round')
        # Main needle body
        self.create_line(self.center_x, self.center_y, tip_x, tip_y,
                        fill='#ff2222', width=3, capstyle='round')
        # Bright highlight
        self.create_line(self.center_x, self.center_y, tip_x, tip_y,
                        fill='#ff6666', width=1, capstyle='round')


class VoiceFilterGUI:
    """Enhanced GUI application for Voice Filter."""

    def __init__(self, root: tk.Tk):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("Voice Filter - Audio Processor")
        self.root.geometry("1000x800")
        self.root.minsize(900, 700)
        self.root.configure(bg=COLORS['bg'])

        # Audio processor
        self.processor = AudioProcessor()
        self.filepath: Optional[str] = None

        # Auto-preview
        self.auto_preview_var = tk.BooleanVar(value=False)

        # Animation state
        self.faders: list = []
        self.isAnimating = False
        self.animation_id = None
        self._animation_generation = 0
        self._playback_id = 0
        self.playback_position = 0
        self.playback_audio = None
        self.playback_sample_rate = None

        # Variables
        self._create_variables()

        # Create UI
        self._create_menu()
        self._create_main_frame()
        self._create_status_bar()

    def _create_variables(self) -> None:
        """Create all parameter variables."""
        # Basic
        self.volume_var = tk.DoubleVar(value=1.0)
        self.pitch_var = tk.DoubleVar(value=0.0)
        self.speed_var = tk.DoubleVar(value=1.0)

        # EQ
        self.eq_bass_var = tk.DoubleVar(value=0.0)
        self.eq_low_mid_var = tk.DoubleVar(value=0.0)
        self.eq_mid_var = tk.DoubleVar(value=0.0)
        self.eq_high_mid_var = tk.DoubleVar(value=0.0)
        self.eq_treble_var = tk.DoubleVar(value=0.0)

        # Filters
        self.low_pass_var = tk.DoubleVar(value=20000)
        self.high_pass_var = tk.DoubleVar(value=20)

        # Modulation
        self.chorus_var = tk.DoubleVar(value=0.0)
        self.flanger_var = tk.DoubleVar(value=0.0)
        self.phaser_var = tk.DoubleVar(value=0.0)
        self.tremolo_var = tk.DoubleVar(value=0.0)
        self.vibrato_var = tk.DoubleVar(value=0.0)

        # Distortion
        self.distortion_var = tk.DoubleVar(value=0.0)
        self.bitcrusher_var = tk.DoubleVar(value=32)
        self.overdrive_var = tk.DoubleVar(value=1.0)

        # Time-based
        self.reverb_var = tk.DoubleVar(value=0.0)
        self.delay_var = tk.DoubleVar(value=0.0)

        # Dynamics
        self.comp_threshold_var = tk.DoubleVar(value=-20.0)
        self.comp_ratio_var = tk.DoubleVar(value=4.0)
        self.gate_var = tk.DoubleVar(value=-30.0)

        # Utility
        self.fade_in_var = tk.DoubleVar(value=0.0)
        self.fade_out_var = tk.DoubleVar(value=0.0)
        self.normalize_var = tk.DoubleVar(value=0.0)
        self.trim_start_var = tk.DoubleVar(value=0.0)
        self.trim_end_var = tk.DoubleVar(value=0.0)
        self.reverse_var = tk.BooleanVar(value=False)

    def _create_menu(self) -> None:
        """Create the menu bar."""
        menubar = tk.Menu(self.root, bg=COLORS['bg'], fg=COLORS['fg'])
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0, bg=COLORS['bg'], fg=COLORS['fg'])
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Audio", command=self._open_audio)
        file_menu.add_command(label="Save Modified", command=self._save_modified)
        file_menu.add_separator()
        file_menu.add_command(label="Save Preset", command=self._save_preset)
        file_menu.add_command(label="Load Preset", command=self._load_preset)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._exit_app)

        edit_menu = tk.Menu(menubar, tearoff=0, bg=COLORS['bg'], fg=COLORS['fg'])
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Reset All", command=self._reset_all)

        help_menu = tk.Menu(menubar, tearoff=0, bg=COLORS['bg'], fg=COLORS['fg'])
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _create_main_frame(self) -> None:
        """Create the main application frame."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self._create_transport(main_frame)
        self._create_waveform(main_frame)
        self._create_params_notebook(main_frame)

    def _create_transport(self, parent: ttk.Frame) -> None:
        """Create transport controls."""
        transport = ttk.LabelFrame(parent, text="Transport", padding="5")
        transport.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(transport, text="Open", command=self._open_audio).pack(side=tk.LEFT, padx=2)
        ttk.Button(transport, text="Play Original", command=self._play_original).pack(side=tk.LEFT, padx=2)
        ttk.Button(transport, text="Play Modified", command=self._play_modified).pack(side=tk.LEFT, padx=2)
        ttk.Button(transport, text="Stop", command=self._stop_audio).pack(side=tk.LEFT, padx=2)
        ttk.Button(transport, text="Save", command=self._save_modified).pack(side=tk.LEFT, padx=2)
        ttk.Button(transport, text="Reset", command=self._reset_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(transport, text="Exit", command=self._exit_app).pack(side=tk.RIGHT, padx=2)

        ttk.Checkbutton(transport, text="Auto-Preview",
                        variable=self.auto_preview_var).pack(side=tk.RIGHT, padx=10)

    def _create_waveform(self, parent: ttk.Frame) -> None:
        """Create waveform visualization with mixer console styling."""
        waveform = tk.Frame(parent, bg=COLORS['channel_bg'],
                          highlightbackground=COLORS['channel_border'],
                          highlightthickness=1)
        waveform.pack(fill=tk.X, pady=(0, 5), padx=2)

        # Header
        tk.Label(waveform, text="WAVEFORM DISPLAY", font=('', 9, 'bold'),
                fg=COLORS['fg_dim'], bg=COLORS['channel_bg']).pack(anchor=tk.W, padx=10, pady=(5, 2))

        # Original waveform
        orig_frame = tk.Frame(waveform, bg=COLORS['channel_bg'])
        orig_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(orig_frame, text="ORIGINAL", font=('', 8, 'bold'),
                fg=COLORS['success'], bg=COLORS['channel_bg']).pack(side=tk.LEFT)

        self.waveform_canvas = tk.Canvas(orig_frame, bg=COLORS['meter_bg'], height=50,
                                        highlightbackground=COLORS['channel_border'],
                                        highlightthickness=1)
        self.waveform_canvas.pack(fill=tk.X, padx=(10, 0), expand=True)

        # Modified waveform
        mod_frame = tk.Frame(waveform, bg=COLORS['channel_bg'])
        mod_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(mod_frame, text="MODIFIED", font=('', 8, 'bold'),
                fg=COLORS['warning'], bg=COLORS['channel_bg']).pack(side=tk.LEFT)

        self.modified_canvas = tk.Canvas(mod_frame, bg=COLORS['meter_bg'], height=50,
                                        highlightbackground=COLORS['channel_border'],
                                        highlightthickness=1)
        self.modified_canvas.pack(fill=tk.X, padx=(10, 0), expand=True)

        # Info label
        self.waveform_info = tk.Label(waveform, text="No audio loaded",
                                     font=('', 8), fg=COLORS['fg_dim'], bg=COLORS['channel_bg'])
        self.waveform_info.pack(anchor=tk.W, padx=10, pady=(2, 5))

    def _create_params_notebook(self, parent: ttk.Frame) -> None:
        """Create parameter tabs."""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        tabs = [
            ("Basic", self._create_basic_tab, COLORS['basic']),
            ("EQ", self._create_eq_tab, COLORS['eq']),
            ("Filters", self._create_filters_tab, COLORS['eq']),
            ("Modulation", self._create_modulation_tab, COLORS['modulation']),
            ("Distortion", self._create_distortion_tab, COLORS['distortion']),
            ("Time", self._create_time_tab, COLORS['time']),
            ("Dynamics", self._create_dynamics_tab, COLORS['dynamics']),
            ("Utility", self._create_utility_tab, COLORS['utility']),
        ]

        for label, create_func, color in tabs:
            frame = ttk.Frame(notebook, padding="5")
            notebook.add(frame, text=label)
            create_func(frame)

    def _create_slider(self, parent: ttk.Frame, row: int, label: str,
                       variable: tk.DoubleVar, from_: float, to: float,
                       unit: str = "", color: str = None) -> MixerFader:
        """Create a mixer-style fader with value display."""
        # Mixer fader - medium width
        fader = MixerFader(
            parent,
            variable=variable,
            from_=from_,
            to=to,
            width=65,
            height=125,
            orientation='vertical',
            color=color,
            on_press=lambda: self._stop_audio(),
            on_release=lambda: self._on_slider_release()
        )
        fader.pack(pady=(0, 5))

        # Add to faders list for animation
        self.faders.append(fader)

        # Value label
        value_label = ttk.Label(parent, text=f"{variable.get():.1f}{unit}", width=8)
        value_label.pack()

        variable.trace_add('write', lambda *args, lbl=value_label, v=variable, u=unit:
                          lbl.configure(text=f"{v.get():.1f}{u}"))

        return fader

    def _on_slider_release(self) -> None:
        """Handle slider release for auto-preview."""
        self._draw_modified_waveform()
        if self.auto_preview_var.get():
            self._play_modified()

    def _create_basic_tab(self, parent: ttk.Frame) -> None:
        """Create basic parameters tab with mixer-style faders and VU meter."""
        inner = tk.Frame(parent, bg=COLORS['channel_bg'])
        inner.pack(fill=tk.BOTH, expand=True)

        ttk.Label(inner, text="BASIC", font=('', 10, 'bold'),
                  foreground=COLORS['basic'], background=COLORS['channel_bg']).pack(anchor=tk.W, pady=(5, 10))

        # Main content frame using grid for equal-width columns
        content_frame = tk.Frame(inner, bg=COLORS['channel_bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # All 4 columns (VU + 3 faders) have equal width
        for i in range(4):
            content_frame.columnconfigure(i, weight=1, uniform='basic')

        # VU Meter channel (column 0) - expand to fill column width
        vu_channel = tk.Frame(content_frame, bg=COLORS['channel_bg'],
                             highlightbackground=COLORS['channel_border'],
                             highlightthickness=1)
        vu_channel.grid(row=0, column=0, padx=4, pady=5, sticky='nsew')

        tk.Label(vu_channel, text="VU", font=('', 9, 'bold'),
                fg=COLORS['basic'], bg=COLORS['channel_bg']).pack(pady=(5, 2))

        # VU meter container that expands to fill channel width
        vu_meter_container = tk.Frame(vu_channel, bg=COLORS['channel_bg'])
        vu_meter_container.pack(fill=tk.X, padx=5, pady=2)
        self.vu_meter = AnalogVUMeter(vu_meter_container, width=120, height=120, color=COLORS['basic'])
        self.vu_meter.pack(expand=True)

        # VU Meter level display
        vu_val_frame = tk.Frame(vu_channel, bg=COLORS['meter_bg'], height=18)
        vu_val_frame.pack(fill=tk.X, padx=5, pady=(2, 5))
        vu_val_frame.pack_propagate(False)
        self.vu_value_label = tk.Label(vu_val_frame, text="-60.0 dB",
                                      font=('', 8), fg=COLORS['led_green'], bg=COLORS['meter_bg'])
        self.vu_value_label.pack(expand=True)

        # Fader definitions
        faders = [
            ("VOL", self.volume_var, 0, 2, "%"),
            ("PITCH", self.pitch_var, -12, 12, " st"),
            ("SPEED", self.speed_var, 0.5, 2, "x"),
        ]

        for col, (label_text, var, from_, to, unit) in enumerate(faders):
            # Channel strip frame - column 1, 2, 3 - expand to fill column width
            channel = tk.Frame(content_frame, bg=COLORS['channel_bg'],
                             highlightbackground=COLORS['channel_border'],
                             highlightthickness=1)
            channel.grid(row=0, column=col + 1, padx=4, pady=5, sticky='nsew')

            # Channel label
            tk.Label(channel, text=label_text, font=('', 9, 'bold'),
                    fg=COLORS['basic'], bg=COLORS['channel_bg']).pack(pady=(5, 2))

            # Fader - expand to fill channel width
            fader_container = tk.Frame(channel, bg=COLORS['channel_bg'])
            fader_container.pack(fill=tk.X, padx=5, pady=2)
            fader = MixerFader(
                fader_container,
                variable=var,
                from_=from_,
                to=to,
                width=65,
                height=125,
                orientation='vertical',
                color=COLORS['basic'],
                on_press=lambda: self._stop_audio(),
                on_release=lambda: self._on_slider_release()
            )
            fader.pack(expand=True)
            self.faders.append(fader)

            # Value display
            val_frame = tk.Frame(channel, bg=COLORS['meter_bg'], height=18)
            val_frame.pack(fill=tk.X, padx=5, pady=(2, 5))
            val_frame.pack_propagate(False)
            tk.Label(val_frame, text=f"{var.get():.1f}{unit}",
                    font=('', 8), fg=COLORS['led_green'], bg=COLORS['meter_bg']).pack(expand=True)

            # Update value display
            def update_val(v=var, lbl=None, u=unit):
                if lbl and lbl.winfo_exists():
                    lbl.configure(text=f"{v.get():.1f}{u}")
            var.trace_add('write', lambda *args, v=var, u=unit: self.root.after(10, update_val, v, None, u))

    def _create_eq_tab(self, parent: ttk.Frame) -> None:
        """Create EQ parameters tab."""
        inner = tk.Frame(parent, bg=COLORS['channel_bg'])
        inner.pack(fill=tk.BOTH, expand=True)

        ttk.Label(inner, text="EQUALIZER", font=('', 10, 'bold'),
                  foreground=COLORS['eq'], background=COLORS['channel_bg']).pack(anchor=tk.W, pady=(5, 10))

        fader_grid = tk.Frame(inner, bg=COLORS['channel_bg'])
        fader_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        eq_faders = [
            ("BASS\n100Hz", self.eq_bass_var),
            ("LOW\n400Hz", self.eq_low_mid_var),
            ("MID\n1kHz", self.eq_mid_var),
            ("HIGH\n2.5kHz", self.eq_high_mid_var),
            ("TREBLE\n6kHz", self.eq_treble_var),
        ]

        for col, (label_text, var) in enumerate(eq_faders):
            channel = tk.Frame(fader_grid, bg=COLORS['channel_bg'],
                             highlightbackground=COLORS['channel_border'],
                             highlightthickness=1)
            channel.grid(row=0, column=col, padx=3, pady=5, sticky='nsew')

            tk.Label(channel, text=label_text, font=('', 8, 'bold'),
                    fg=COLORS['eq'], bg=COLORS['channel_bg'], justify=tk.CENTER).pack(pady=(8, 2))

            self._create_slider(channel, 0, "", var, -12, 12, " dB", COLORS['eq'])

            val_frame = tk.Frame(channel, bg=COLORS['meter_bg'], height=18)
            val_frame.pack(fill=tk.X, padx=5, pady=(2, 5))
            val_frame.pack_propagate(False)
            tk.Label(val_frame, text=f"{var.get():.1f} dB",
                    font=('', 8), fg=COLORS['eq'], bg=COLORS['meter_bg']).pack(expand=True)

        for i in range(5):
            fader_grid.columnconfigure(i, weight=1)

    def _create_filters_tab(self, parent: ttk.Frame) -> None:
        """Create filters parameters tab."""
        inner = tk.Frame(parent, bg=COLORS['channel_bg'])
        inner.pack(fill=tk.BOTH, expand=True)

        ttk.Label(inner, text="FILTERS", font=('', 10, 'bold'),
                  foreground=COLORS['eq'], background=COLORS['channel_bg']).pack(anchor=tk.W, pady=(5, 10))

        fader_grid = tk.Frame(inner, bg=COLORS['channel_bg'])
        fader_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        filter_faders = [
            ("LOW\nPASS", self.low_pass_var, 100, 20000, " Hz"),
            ("HIGH\nPASS", self.high_pass_var, 20, 5000, " Hz"),
        ]

        for col, (label_text, var, from_, to, unit) in enumerate(filter_faders):
            channel = tk.Frame(fader_grid, bg=COLORS['channel_bg'],
                             highlightbackground=COLORS['channel_border'],
                             highlightthickness=1)
            channel.grid(row=0, column=col, padx=15, pady=5, sticky='nsew')

            tk.Label(channel, text=label_text, font=('', 9, 'bold'),
                    fg=COLORS['eq'], bg=COLORS['channel_bg'], justify=tk.CENTER).pack(pady=(8, 2))

            self._create_slider(channel, 0, "", var, from_, to, unit, COLORS['eq'])

            val_frame = tk.Frame(channel, bg=COLORS['meter_bg'], height=18)
            val_frame.pack(fill=tk.X, padx=5, pady=(2, 5))
            val_frame.pack_propagate(False)
            tk.Label(val_frame, text=f"{var.get():.0f}{unit}",
                    font=('', 8), fg=COLORS['eq'], bg=COLORS['meter_bg']).pack(expand=True)

        fader_grid.columnconfigure(0, weight=1)
        fader_grid.columnconfigure(1, weight=1)

    def _create_modulation_tab(self, parent: ttk.Frame) -> None:
        """Create modulation parameters tab."""
        inner = tk.Frame(parent, bg=COLORS['channel_bg'])
        inner.pack(fill=tk.BOTH, expand=True)

        ttk.Label(inner, text="MODULATION", font=('', 10, 'bold'),
                  foreground=COLORS['modulation'], background=COLORS['channel_bg']).pack(anchor=tk.W, pady=(5, 10))

        fader_grid = tk.Frame(inner, bg=COLORS['channel_bg'])
        fader_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        mod_faders = [
            ("CHORUS", self.chorus_var),
            ("FLANGER", self.flanger_var),
            ("PHASER", self.phaser_var),
            ("TREMOLO", self.tremolo_var),
            ("VIBRATO", self.vibrato_var),
        ]

        for col, (label_text, var) in enumerate(mod_faders):
            channel = tk.Frame(fader_grid, bg=COLORS['channel_bg'],
                             highlightbackground=COLORS['channel_border'],
                             highlightthickness=1)
            channel.grid(row=0, column=col, padx=3, pady=5, sticky='nsew')

            tk.Label(channel, text=label_text, font=('', 9, 'bold'),
                    fg=COLORS['modulation'], bg=COLORS['channel_bg']).pack(pady=(8, 2))

            self._create_slider(channel, 0, "", var, 0, 1, "", COLORS['modulation'])

            val_frame = tk.Frame(channel, bg=COLORS['meter_bg'], height=18)
            val_frame.pack(fill=tk.X, padx=5, pady=(2, 5))
            val_frame.pack_propagate(False)
            tk.Label(val_frame, text=f"{var.get():.0%}",
                    font=('', 8), fg=COLORS['modulation'], bg=COLORS['meter_bg']).pack(expand=True)

        for i in range(5):
            fader_grid.columnconfigure(i, weight=1)

    def _create_distortion_tab(self, parent: ttk.Frame) -> None:
        """Create distortion parameters tab."""
        inner = tk.Frame(parent, bg=COLORS['channel_bg'])
        inner.pack(fill=tk.BOTH, expand=True)

        ttk.Label(inner, text="DISTORTION", font=('', 10, 'bold'),
                  foreground=COLORS['distortion'], background=COLORS['channel_bg']).pack(anchor=tk.W, pady=(5, 10))

        fader_grid = tk.Frame(inner, bg=COLORS['channel_bg'])
        fader_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        dist_faders = [
            ("DIST", self.distortion_var, 0, 1, ""),
            ("BITS", self.bitcrusher_var, 4, 32, " bit"),
            ("DRIVE", self.overdrive_var, 1, 10, "x"),
        ]

        for col, (label_text, var, from_, to, unit) in enumerate(dist_faders):
            channel = tk.Frame(fader_grid, bg=COLORS['channel_bg'],
                             highlightbackground=COLORS['channel_border'],
                             highlightthickness=1)
            channel.grid(row=0, column=col, padx=15, pady=5, sticky='nsew')

            tk.Label(channel, text=label_text, font=('', 9, 'bold'),
                    fg=COLORS['distortion'], bg=COLORS['channel_bg']).pack(pady=(8, 2))

            self._create_slider(channel, 0, "", var, from_, to, unit, COLORS['distortion'])

            val_frame = tk.Frame(channel, bg=COLORS['meter_bg'], height=18)
            val_frame.pack(fill=tk.X, padx=5, pady=(2, 5))
            val_frame.pack_propagate(False)
            tk.Label(val_frame, text=f"{var.get():.1f}{unit}",
                    font=('', 8), fg=COLORS['distortion'], bg=COLORS['meter_bg']).pack(expand=True)

        fader_grid.columnconfigure(0, weight=1)
        fader_grid.columnconfigure(1, weight=1)
        fader_grid.columnconfigure(2, weight=1)

    def _create_time_tab(self, parent: ttk.Frame) -> None:
        """Create time-based parameters tab."""
        inner = tk.Frame(parent, bg=COLORS['channel_bg'])
        inner.pack(fill=tk.BOTH, expand=True)

        ttk.Label(inner, text="TIME EFFECTS", font=('', 10, 'bold'),
                  foreground=COLORS['time'], background=COLORS['channel_bg']).pack(anchor=tk.W, pady=(5, 10))

        fader_grid = tk.Frame(inner, bg=COLORS['channel_bg'])
        fader_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        time_faders = [
            ("REVERB", self.reverb_var, 0, 1, ""),
            ("DELAY", self.delay_var, 0, 500, " ms"),
        ]

        for col, (label_text, var, from_, to, unit) in enumerate(time_faders):
            channel = tk.Frame(fader_grid, bg=COLORS['channel_bg'],
                             highlightbackground=COLORS['channel_border'],
                             highlightthickness=1)
            channel.grid(row=0, column=col, padx=15, pady=5, sticky='nsew')

            tk.Label(channel, text=label_text, font=('', 9, 'bold'),
                    fg=COLORS['time'], bg=COLORS['channel_bg']).pack(pady=(8, 2))

            self._create_slider(channel, 0, "", var, from_, to, unit, COLORS['time'])

            val_frame = tk.Frame(channel, bg=COLORS['meter_bg'], height=18)
            val_frame.pack(fill=tk.X, padx=5, pady=(2, 5))
            val_frame.pack_propagate(False)
            tk.Label(val_frame, text=f"{var.get():.1f}{unit}",
                    font=('', 8), fg=COLORS['time'], bg=COLORS['meter_bg']).pack(expand=True)

        fader_grid.columnconfigure(0, weight=1)
        fader_grid.columnconfigure(1, weight=1)

    def _create_dynamics_tab(self, parent: ttk.Frame) -> None:
        """Create dynamics parameters tab."""
        inner = tk.Frame(parent, bg=COLORS['channel_bg'])
        inner.pack(fill=tk.BOTH, expand=True)

        ttk.Label(inner, text="DYNAMICS", font=('', 10, 'bold'),
                  foreground=COLORS['dynamics'], background=COLORS['channel_bg']).pack(anchor=tk.W, pady=(5, 10))

        fader_grid = tk.Frame(inner, bg=COLORS['channel_bg'])
        fader_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        dyn_faders = [
            ("THRESH", self.comp_threshold_var, -40, 0, " dB"),
            ("RATIO", self.comp_ratio_var, 1, 20, ":1"),
            ("GATE", self.gate_var, -60, 0, " dB"),
        ]

        for col, (label_text, var, from_, to, unit) in enumerate(dyn_faders):
            channel = tk.Frame(fader_grid, bg=COLORS['channel_bg'],
                             highlightbackground=COLORS['channel_border'],
                             highlightthickness=1)
            channel.grid(row=0, column=col, padx=15, pady=5, sticky='nsew')

            tk.Label(channel, text=label_text, font=('', 9, 'bold'),
                    fg=COLORS['dynamics'], bg=COLORS['channel_bg']).pack(pady=(8, 2))

            self._create_slider(channel, 0, "", var, from_, to, unit, COLORS['dynamics'])

            val_frame = tk.Frame(channel, bg=COLORS['meter_bg'], height=18)
            val_frame.pack(fill=tk.X, padx=5, pady=(2, 5))
            val_frame.pack_propagate(False)
            tk.Label(val_frame, text=f"{var.get():.1f}{unit}",
                    font=('', 8), fg=COLORS['dynamics'], bg=COLORS['meter_bg']).pack(expand=True)

        fader_grid.columnconfigure(0, weight=1)
        fader_grid.columnconfigure(1, weight=1)
        fader_grid.columnconfigure(2, weight=1)

    def _create_utility_tab(self, parent: ttk.Frame) -> None:
        """Create utility parameters tab."""
        inner = tk.Frame(parent, bg=COLORS['channel_bg'])
        inner.pack(fill=tk.BOTH, expand=True)

        ttk.Label(inner, text="UTILITY", font=('', 10, 'bold'),
                  foreground=COLORS['utility'], background=COLORS['channel_bg']).pack(anchor=tk.W, pady=(5, 10))

        fader_grid = tk.Frame(inner, bg=COLORS['channel_bg'])
        fader_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        util_faders = [
            ("FADE\nIN", self.fade_in_var, 0, 5000, " ms"),
            ("FADE\nOUT", self.fade_out_var, 0, 5000, " ms"),
            ("NORM", self.normalize_var, -24, 0, " dB"),
            ("TRIM\nSTART", self.trim_start_var, 0, 100, " s"),
            ("TRIM\nEND", self.trim_end_var, 0, 100, " s"),
        ]

        for col, (label_text, var, from_, to, unit) in enumerate(util_faders):
            channel = tk.Frame(fader_grid, bg=COLORS['channel_bg'],
                             highlightbackground=COLORS['channel_border'],
                             highlightthickness=1)
            channel.grid(row=0, column=col, padx=3, pady=5, sticky='nsew')

            tk.Label(channel, text=label_text, font=('', 8, 'bold'),
                    fg=COLORS['utility'], bg=COLORS['channel_bg'], justify=tk.CENTER).pack(pady=(8, 2))

            self._create_slider(channel, 0, "", var, from_, to, unit, COLORS['utility'])

            val_frame = tk.Frame(channel, bg=COLORS['meter_bg'], height=18)
            val_frame.pack(fill=tk.X, padx=5, pady=(2, 5))
            val_frame.pack_propagate(False)
            tk.Label(val_frame, text=f"{var.get():.1f}{unit}",
                    font=('', 8), fg=COLORS['utility'], bg=COLORS['meter_bg']).pack(expand=True)

        for i in range(5):
            fader_grid.columnconfigure(i, weight=1)

        # Reverse checkbox
        reverse_frame = tk.Frame(inner, bg=COLORS['channel_bg'])
        reverse_frame.pack(fill=tk.X, pady=10, padx=10)
        reverse_cb = tk.Checkbutton(reverse_frame, text="REVERSE",
                                   variable=self.reverse_var,
                                   command=self._on_reverse_change,
                                   bg=COLORS['channel_bg'], fg=COLORS['utility'],
                                   selectcolor=COLORS['meter_bg'],
                                   activebackground=COLORS['channel_bg'],
                                   activeforeground=COLORS['utility'])
        reverse_cb.pack(side=tk.LEFT)
        reverse_cb.bind('<ButtonPress-1>', lambda e: self._stop_audio())
        inner.columnconfigure(1, weight=1)

    def _on_reverse_change(self) -> None:
        """Handle reverse checkbox change."""
        self._draw_modified_waveform()
        if self.auto_preview_var.get():
            self._play_modified()

    def _create_status_bar(self) -> None:
        """Create the status bar."""
        self.status_var = tk.StringVar(value="Ready - No audio loaded")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _draw_waveform(self, audio: np.ndarray, canvas: tk.Canvas, color: str) -> None:
        """Draw waveform on canvas."""
        canvas.delete("all")
        if audio is None or len(audio) == 0:
            return
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width <= 1 or height <= 1:
            return
        samples_per_pixel = max(1, len(audio) // width)
        downsampled = audio[::samples_per_pixel]
        max_val = np.max(np.abs(downsampled))
        if max_val > 0:
            normalized = downsampled / max_val
        else:
            normalized = downsampled
        points = []
        for i, val in enumerate(normalized):
            x = i
            y = int(height / 2 - val * (height / 2 - 5))
            points.append(x)
            points.append(y)
        if len(points) >= 4:
            canvas.create_line(points, fill=color, width=1)

    def _draw_original_waveform(self) -> None:
        """Draw original waveform."""
        self._draw_waveform(self.processor.original_audio, self.waveform_canvas, COLORS['success'])

    def _draw_modified_waveform(self) -> None:
        """Draw modified waveform."""
        if self.processor.original_audio is None:
            return
        try:
            processed = self.processor.apply_process_all(self._get_params())
            self._draw_waveform(processed, self.modified_canvas, COLORS['warning'])
        except Exception:
            pass

    def _log(self, message: str) -> None:
        """Log message to status bar."""
        self.status_var.set(message)

    def _open_audio(self) -> None:
        """Open audio file."""
        filepath = filedialog.askopenfilename(
            filetypes=[
                ("Audio files", "*.wav *.mp3 *.aac *.ogg *.flac *.m4a *.wma"),
                ("All files", "*.*"),
            ]
        )
        if filepath:
            if self.processor.load_audio(filepath):
                self.filepath = filepath
                self.trim_end_var.set(self.processor.duration)
                self.root.after(100, self._update_waveforms)
                filename = os.path.basename(filepath)
                self._log(f"Loaded: {filename} | {self.processor.sample_rate} Hz | {self.processor.duration:.1f}s")
            else:
                messagebox.showerror("Error", "Failed to load audio file")

    def _update_waveforms(self) -> None:
        """Update both waveforms after loading."""
        self._draw_original_waveform()
        self._draw_modified_waveform()

    def _save_modified(self) -> None:
        """Save modified audio."""
        if self.processor.original_audio is None:
            messagebox.showwarning("Warning", "No audio to save")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
            initialfile="modified_audio.wav"
        )
        if filepath:
            processed = self.processor.apply_process_all(self._get_params())
            if self.processor.save_audio(filepath, processed):
                self._log(f"Modified saved to: {os.path.basename(filepath)}")
            else:
                messagebox.showerror("Error", "Failed to save modified audio")

    def _save_preset(self) -> None:
        """Save current mixer settings to a preset file."""
        import json
        params = self._get_params()
        params['trim_end'] = self.processor.duration if self.processor.duration else 0
        params['version'] = '1.0'

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Preset files", "*.preset"), ("All files", "*.*")],
            initialfile="mixer_preset.json"
        )
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    json.dump(params, f, indent=2)
                self._log(f"Preset saved: {os.path.basename(filepath)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save preset:\n{e}")

    def _load_preset(self) -> None:
        """Load mixer settings from a preset file."""
        import json
        filepath = filedialog.askopenfilename(
            filetypes=[
                ("JSON files", "*.json"),
                ("Preset files", "*.preset"),
                ("All files", "*.*"),
            ]
        )
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    params = json.load(f)
                self._apply_preset(params)
                self._draw_modified_waveform()
                self._log(f"Preset loaded: {os.path.basename(filepath)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load preset:\n{e}")

    def _apply_preset(self, params: dict) -> None:
        """Apply preset parameters to all controls."""
        # Basic
        self.volume_var.set(params.get('volume', 1.0))
        self.pitch_var.set(params.get('pitch', 0.0))
        self.speed_var.set(params.get('speed', 1.0))

        # EQ
        eq = params.get('eq', {})
        self.eq_bass_var.set(eq.get('bass', 0.0))
        self.eq_low_mid_var.set(eq.get('low_mid', 0.0))
        self.eq_mid_var.set(eq.get('mid', 0.0))
        self.eq_high_mid_var.set(eq.get('high_mid', 0.0))
        self.eq_treble_var.set(eq.get('treble', 0.0))

        # Filters
        self.low_pass_var.set(params.get('low_pass', 20000))
        self.high_pass_var.set(params.get('high_pass', 20))

        # Modulation
        self.chorus_var.set(params.get('chorus', 0.0))
        self.flanger_var.set(params.get('flanger', 0.0))
        self.phaser_var.set(params.get('phaser', 0.0))
        self.tremolo_var.set(params.get('tremolo', 0.0))
        self.vibrato_var.set(params.get('vibrato', 0.0))

        # Distortion
        self.distortion_var.set(params.get('distortion', 0.0))
        self.bitcrusher_var.set(params.get('bitcrusher', 32))
        self.overdrive_var.set(params.get('overdrive', 1.0))

        # Time-based
        self.reverb_var.set(params.get('reverb', 0.0))
        self.delay_var.set(params.get('delay', 0.0))

        # Dynamics
        self.comp_threshold_var.set(params.get('comp_threshold', -20.0))
        self.comp_ratio_var.set(params.get('comp_ratio', 4.0))
        self.gate_var.set(params.get('gate', -30.0))

        # Utility
        self.fade_in_var.set(params.get('fade_in', 0.0))
        self.fade_out_var.set(params.get('fade_out', 0.0))
        self.normalize_var.set(params.get('normalize', 0.0))
        self.trim_start_var.set(params.get('trim_start', 0.0))
        self.trim_end_var.set(params.get('trim_end', self.processor.duration if self.processor.duration else 0))
        self.reverse_var.set(params.get('reverse', False))

    def _play_original(self) -> None:
        """Play original audio with meter animation."""
        if self.processor.original_audio is None:
            messagebox.showwarning("Warning", "No audio loaded")
            return
        self._log("Playing original...")
        self._stop_animation()
        self._playback_id += 1
        current_id = self._playback_id
        self.playback_audio = self.processor.original_audio
        self.playback_sample_rate = self.processor.sample_rate
        self.playback_position = 0
        self._start_animation()
        self.processor.play_audio(self.processor.original_audio,
                                  callback=lambda pid: self.root.after(
                                      0, self._on_playback_finished, pid),
                                  playback_id=current_id)

    def _play_modified(self) -> None:
        """Play modified audio with meter animation."""
        if self.processor.original_audio is None:
            return
        processed = self.processor.apply_process_all(self._get_params())
        self._log("Playing modified...")
        self._stop_animation()
        self._playback_id += 1
        current_id = self._playback_id
        self.playback_audio = processed
        self.playback_sample_rate = self.processor.sample_rate
        self.playback_position = 0
        self._start_animation()
        self.processor.play_audio(processed,
                                  callback=lambda pid: self.root.after(
                                      0, self._on_playback_finished, pid),
                                  playback_id=current_id)

    def _stop_audio(self) -> None:
        """Stop audio playback and animation."""
        self._stop_animation()
        self.processor.stop_playback()
        self._log("Stopped")

    def _on_playback_finished(self, playback_id: int = 0) -> None:
        """Handle playback completion. Ignores if not the current playback."""
        if playback_id != self._playback_id:
            return
        self._stop_animation()
        self._log("Playback finished")

    def _start_animation(self) -> None:
        """Start meter animation."""
        self._animation_generation += 1
        self.isAnimating = True
        self._animate_meters(self._animation_generation)

    def _stop_animation(self) -> None:
        """Stop meter animation and let needles fall to 0."""
        self.isAnimating = False
        self._animation_generation += 1
        self.playback_audio = None
        if self.animation_id is not None:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        # Reset all fader levels to 0
        for fader in self.faders:
            fader.set_audio_level(0.0)
        # Set VU meter target to 0 (needle will animate to -20 dB position)
        if hasattr(self, 'vu_meter'):
            self.vu_meter.set_level(0.0)
        # Update VU label
        if hasattr(self, 'vu_value_label') and self.vu_value_label.winfo_exists():
            self.vu_value_label.configure(text="-20.0 dB")

    def _animate_meters(self, generation: int = 0) -> None:
        """Update meter levels based on audio position."""
        # Bail out if this animation instance has been superseded
        if generation != self._animation_generation:
            return
        if not self.isAnimating or self.playback_audio is None:
            return

        # Calculate current audio level (RMS of a small window)
        window_size = 1024
        start = int(self.playback_position)
        end = min(start + window_size, len(self.playback_audio))

        if start < len(self.playback_audio):
            # Get audio window
            audio_window = self.playback_audio[start:end]

            # Calculate RMS level
            rms = np.sqrt(np.mean(audio_window ** 2))

            # Convert to dB
            if rms > 0:
                level_db = 20 * np.log10(rms)
            else:
                level_db = -60

            # Map dB to needle position (0.0 to 1.0)
            # VU meter scale: -20 dB at position 0.0, +3 dB at position 1.0
            vu_db_min = self.vu_meter._db_min  # -20
            vu_db_max = self.vu_meter._db_max  # +3
            level = np.clip((level_db - vu_db_min) / (vu_db_max - vu_db_min), 0.0, 1.0)

            # Update all faders with the audio level
            for fader in self.faders:
                fader.set_audio_level(level)

            # Update VU meter
            if hasattr(self, 'vu_meter'):
                self.vu_meter.set_level(level)
                # Update VU value label
                if hasattr(self, 'vu_value_label') and self.vu_value_label.winfo_exists():
                    self.vu_value_label.configure(text=f"{level_db:.1f} dB")

            # Advance position (simulate real-time playback)
            self.playback_position += self.playback_sample_rate // 30  # ~30fps

            # Loop or stop
            if self.playback_position >= len(self.playback_audio):
                self.playback_position = 0  # Loop
        else:
            # Reset if we've gone past the end
            self.playback_position = 0
            for fader in self.faders:
                fader.set_audio_level(0.0)
            if hasattr(self, 'vu_meter'):
                self.vu_meter.set_level(0.0)
                if hasattr(self, 'vu_value_label') and self.vu_value_label.winfo_exists():
                    self.vu_value_label.configure(text="-20.0 dB")

        # Schedule next update (~30fps)
        if self.isAnimating:
            self.animation_id = self.root.after(33, lambda: self._animate_meters(generation))

    def _get_params(self) -> Dict[str, Any]:
        """Get all current parameters."""
        return {
            'volume': self.volume_var.get(),
            'pitch': self.pitch_var.get(),
            'speed': self.speed_var.get(),
            'eq': {
                'bass': self.eq_bass_var.get(),
                'low_mid': self.eq_low_mid_var.get(),
                'mid': self.eq_mid_var.get(),
                'high_mid': self.eq_high_mid_var.get(),
                'treble': self.eq_treble_var.get(),
            },
            'low_pass': self.low_pass_var.get(),
            'high_pass': self.high_pass_var.get(),
            'chorus': self.chorus_var.get(),
            'flanger': self.flanger_var.get(),
            'phaser': self.phaser_var.get(),
            'tremolo': self.tremolo_var.get(),
            'vibrato': self.vibrato_var.get(),
            'distortion': self.distortion_var.get(),
            'bitcrusher': self.bitcrusher_var.get(),
            'overdrive': self.overdrive_var.get(),
            'reverb': self.reverb_var.get(),
            'delay': self.delay_var.get(),
            'comp_threshold': self.comp_threshold_var.get(),
            'comp_ratio': self.comp_ratio_var.get(),
            'gate': self.gate_var.get(),
            'fade_in': self.fade_in_var.get(),
            'fade_out': self.fade_out_var.get(),
            'normalize': self.normalize_var.get(),
            'trim_start': self.trim_start_var.get(),
            'trim_end': self.trim_end_var.get(),
            'reverse': self.reverse_var.get(),
        }

    def _reset_all(self) -> None:
        """Reset all parameters to defaults."""
        self._stop_audio()
        self.volume_var.set(1.0)
        self.pitch_var.set(0.0)
        self.speed_var.set(1.0)
        self.eq_bass_var.set(0.0)
        self.eq_low_mid_var.set(0.0)
        self.eq_mid_var.set(0.0)
        self.eq_high_mid_var.set(0.0)
        self.eq_treble_var.set(0.0)
        self.low_pass_var.set(20000)
        self.high_pass_var.set(20)
        self.chorus_var.set(0.0)
        self.flanger_var.set(0.0)
        self.phaser_var.set(0.0)
        self.tremolo_var.set(0.0)
        self.vibrato_var.set(0.0)
        self.distortion_var.set(0.0)
        self.bitcrusher_var.set(32)
        self.overdrive_var.set(1.0)
        self.reverb_var.set(0.0)
        self.delay_var.set(0.0)
        self.comp_threshold_var.set(-20.0)
        self.comp_ratio_var.set(4.0)
        self.gate_var.set(-30.0)
        self.fade_in_var.set(0.0)
        self.fade_out_var.set(0.0)
        self.normalize_var.set(0.0)
        self.trim_start_var.set(0.0)
        self.trim_end_var.set(self.processor.duration if self.processor.duration else 0)
        self.reverse_var.set(False)
        self._draw_modified_waveform()
        self._log("All parameters reset to defaults")

    def _show_about(self) -> None:
        """Show about dialog."""
        messagebox.showinfo("About", """Voice Filter - Audio Processor

A graphical interface for loading and modifying
audio files in real-time.

Features:
- 20+ audio effects and filters
- Auto-preview mode
- Color-coded UI
- Cross-platform support

License: MIT""")

    def _exit_app(self) -> None:
        """Exit the application."""
        self._stop_audio()
        self.root.quit()
        self.root.destroy()


def main() -> None:
    """Main entry point."""
    root = tk.Tk()
    app = VoiceFilterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
