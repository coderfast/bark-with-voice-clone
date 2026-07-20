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

    def play_audio(self, audio: np.ndarray, callback: Optional[callable] = None) -> None:
        """Play audio in a separate thread."""
        with self._play_lock:
            if self.is_playing:
                self.stop_playback()
            self.is_playing = True

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
                    callback()

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


# Color scheme
COLORS = {
    'bg': '#2b2b2b',
    'fg': '#ffffff',
    'accent': '#4a9eff',
    'success': '#4caf50',
    'warning': '#ff9800',
    'error': '#f44336',
    'basic': '#3d5afe',
    'eq': '#00bcd4',
    'modulation': '#9c27b0',
    'distortion': '#ff5722',
    'time': '#ff9800',
    'dynamics': '#4caf50',
    'utility': '#607d8b',
}


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
        """Create waveform visualization."""
        waveform = ttk.LabelFrame(parent, text="Waveform", padding="5")
        waveform.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(waveform, text="Original:", foreground=COLORS['success']).pack(anchor=tk.W)
        self.waveform_canvas = tk.Canvas(waveform, bg="black", height=60)
        self.waveform_canvas.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(waveform, text="Modified:", foreground=COLORS['warning']).pack(anchor=tk.W)
        self.modified_canvas = tk.Canvas(waveform, bg="black", height=60)
        self.modified_canvas.pack(fill=tk.X)

        self.waveform_info = ttk.Label(waveform, text="No audio loaded")
        self.waveform_info.pack(fill=tk.X, pady=(5, 0))

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
                       unit: str = "", color: str = None) -> ttk.Scale:
        """Create a labeled slider with value display."""
        lbl = ttk.Label(parent, text=label, foreground=color) if color else ttk.Label(parent, text=label)
        lbl.grid(row=row, column=0, sticky=tk.W, pady=2)

        scale = ttk.Scale(parent, from_=from_, to=to, variable=variable,
                          orient=tk.HORIZONTAL, length=150)
        scale.grid(row=row, column=1, sticky=tk.EW, padx=(5, 0), pady=2)

        value_label = ttk.Label(parent, text=f"{variable.get():.1f}{unit}")
        value_label.grid(row=row, column=2, padx=(5, 0))

        variable.trace_add('write', lambda *args, lbl=value_label, v=variable, u=unit:
                          lbl.configure(text=f"{v.get():.1f}{u}"))

        # Bind ButtonPress to stop audio immediately
        scale.bind('<ButtonPress-1>', lambda e: self._stop_audio())
        # Bind ButtonRelease to trigger auto-preview
        scale.bind('<ButtonRelease-1>', lambda e: self._on_slider_release())

        return scale

    def _on_slider_release(self) -> None:
        """Handle slider release for auto-preview."""
        self._draw_modified_waveform()
        if self.auto_preview_var.get():
            self._play_modified()

    def _create_basic_tab(self, parent: ttk.Frame) -> None:
        """Create basic parameters tab."""
        inner = ttk.Frame(parent)
        inner.pack(fill=tk.BOTH, expand=True)

        ttk.Label(inner, text="Basic Controls", font=('', 10, 'bold'),
                  foreground=COLORS['basic']).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))

        self._create_slider(inner, 1, "Volume:", self.volume_var, 0, 2, "%", COLORS['basic'])
        self._create_slider(inner, 2, "Pitch:", self.pitch_var, -12, 12, " st", COLORS['basic'])
        self._create_slider(inner, 3, "Speed:", self.speed_var, 0.5, 2, "x", COLORS['basic'])
        inner.columnconfigure(1, weight=1)

    def _create_eq_tab(self, parent: ttk.Frame) -> None:
        """Create EQ parameters tab."""
        inner = ttk.Frame(parent)
        inner.pack(fill=tk.BOTH, expand=True)

        ttk.Label(inner, text="5-Band Equalizer", font=('', 10, 'bold'),
                  foreground=COLORS['eq']).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))

        self._create_slider(inner, 1, "Bass (100 Hz):", self.eq_bass_var, -12, 12, " dB", COLORS['eq'])
        self._create_slider(inner, 2, "Low Mid (400 Hz):", self.eq_low_mid_var, -12, 12, " dB", COLORS['eq'])
        self._create_slider(inner, 3, "Mid (1 kHz):", self.eq_mid_var, -12, 12, " dB", COLORS['eq'])
        self._create_slider(inner, 4, "High Mid (2.5 kHz):", self.eq_high_mid_var, -12, 12, " dB", COLORS['eq'])
        self._create_slider(inner, 5, "Treble (6 kHz):", self.eq_treble_var, -12, 12, " dB", COLORS['eq'])
        inner.columnconfigure(1, weight=1)

    def _create_filters_tab(self, parent: ttk.Frame) -> None:
        """Create filters parameters tab."""
        inner = ttk.Frame(parent)
        inner.pack(fill=tk.BOTH, expand=True)

        ttk.Label(inner, text="Frequency Filters", font=('', 10, 'bold'),
                  foreground=COLORS['eq']).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))

        self._create_slider(inner, 1, "Low Pass:", self.low_pass_var, 100, 20000, " Hz", COLORS['eq'])
        self._create_slider(inner, 2, "High Pass:", self.high_pass_var, 20, 5000, " Hz", COLORS['eq'])
        inner.columnconfigure(1, weight=1)

    def _create_modulation_tab(self, parent: ttk.Frame) -> None:
        """Create modulation parameters tab."""
        inner = ttk.Frame(parent)
        inner.pack(fill=tk.BOTH, expand=True)

        ttk.Label(inner, text="Modulation Effects", font=('', 10, 'bold'),
                  foreground=COLORS['modulation']).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))

        self._create_slider(inner, 1, "Chorus:", self.chorus_var, 0, 1, "", COLORS['modulation'])
        self._create_slider(inner, 2, "Flanger:", self.flanger_var, 0, 1, "", COLORS['modulation'])
        self._create_slider(inner, 3, "Phaser:", self.phaser_var, 0, 1, "", COLORS['modulation'])
        self._create_slider(inner, 4, "Tremolo:", self.tremolo_var, 0, 1, "", COLORS['modulation'])
        self._create_slider(inner, 5, "Vibrato:", self.vibrato_var, 0, 1, "", COLORS['modulation'])
        inner.columnconfigure(1, weight=1)

    def _create_distortion_tab(self, parent: ttk.Frame) -> None:
        """Create distortion parameters tab."""
        inner = ttk.Frame(parent)
        inner.pack(fill=tk.BOTH, expand=True)

        ttk.Label(inner, text="Distortion Effects", font=('', 10, 'bold'),
                  foreground=COLORS['distortion']).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))

        self._create_slider(inner, 1, "Distortion:", self.distortion_var, 0, 1, "", COLORS['distortion'])
        self._create_slider(inner, 2, "Bitcrusher:", self.bitcrusher_var, 4, 32, " bits", COLORS['distortion'])
        self._create_slider(inner, 3, "Overdrive:", self.overdrive_var, 1, 10, "x", COLORS['distortion'])
        inner.columnconfigure(1, weight=1)

    def _create_time_tab(self, parent: ttk.Frame) -> None:
        """Create time-based parameters tab."""
        inner = ttk.Frame(parent)
        inner.pack(fill=tk.BOTH, expand=True)

        ttk.Label(inner, text="Time-Based Effects", font=('', 10, 'bold'),
                  foreground=COLORS['time']).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))

        self._create_slider(inner, 1, "Reverb:", self.reverb_var, 0, 1, "", COLORS['time'])
        self._create_slider(inner, 2, "Delay:", self.delay_var, 0, 500, " ms", COLORS['time'])
        inner.columnconfigure(1, weight=1)

    def _create_dynamics_tab(self, parent: ttk.Frame) -> None:
        """Create dynamics parameters tab."""
        inner = ttk.Frame(parent)
        inner.pack(fill=tk.BOTH, expand=True)

        ttk.Label(inner, text="Dynamics Processing", font=('', 10, 'bold'),
                  foreground=COLORS['dynamics']).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))

        self._create_slider(inner, 1, "Comp Threshold:", self.comp_threshold_var, -40, 0, " dB", COLORS['dynamics'])
        self._create_slider(inner, 2, "Comp Ratio:", self.comp_ratio_var, 1, 20, ":1", COLORS['dynamics'])
        self._create_slider(inner, 3, "Gate:", self.gate_var, -60, 0, " dB", COLORS['dynamics'])
        inner.columnconfigure(1, weight=1)

    def _create_utility_tab(self, parent: ttk.Frame) -> None:
        """Create utility parameters tab."""
        inner = ttk.Frame(parent)
        inner.pack(fill=tk.BOTH, expand=True)

        ttk.Label(inner, text="Utility Functions", font=('', 10, 'bold'),
                  foreground=COLORS['utility']).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))

        self._create_slider(inner, 1, "Fade In:", self.fade_in_var, 0, 5000, " ms", COLORS['utility'])
        self._create_slider(inner, 2, "Fade Out:", self.fade_out_var, 0, 5000, " ms", COLORS['utility'])
        self._create_slider(inner, 3, "Normalize:", self.normalize_var, -24, 0, " dB", COLORS['utility'])
        self._create_slider(inner, 4, "Trim Start:", self.trim_start_var, 0, 100, " s", COLORS['utility'])
        self._create_slider(inner, 5, "Trim End:", self.trim_end_var, 0, 100, " s", COLORS['utility'])

        reverse_cb = ttk.Checkbutton(inner, text="Reverse Audio",
                        variable=self.reverse_var,
                        command=self._on_reverse_change)
        reverse_cb.grid(row=6, column=0, columnspan=3, sticky=tk.W, pady=5)
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

    def _play_original(self) -> None:
        """Play original audio."""
        if self.processor.original_audio is None:
            messagebox.showwarning("Warning", "No audio loaded")
            return
        self._log("Playing original...")
        self.processor.play_audio(self.processor.original_audio,
                                  callback=lambda: self.root.after(0, lambda: self._log("Playback finished")))

    def _play_modified(self) -> None:
        """Play modified audio."""
        if self.processor.original_audio is None:
            return
        processed = self.processor.apply_process_all(self._get_params())
        self._log("Playing modified...")
        self.processor.play_audio(processed,
                                  callback=lambda: self.root.after(0, lambda: self._log("Playback finished")))

    def _stop_audio(self) -> None:
        """Stop audio playback."""
        self.processor.stop_playback()
        self._log("Stopped")

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
