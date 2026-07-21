import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from typing import Optional, Dict, Any
from scipy.signal import spectrogram as scipy_spectrogram

from config.colors import COLORS
from audio.processor import AudioProcessor
from widgets.mixer_fader import MixerFader
from gui.tabs import (
    create_basic_tab, create_eq_tab, create_filters_tab,
    create_modulation_tab, create_distortion_tab, create_time_tab,
    create_dynamics_tab, create_utility_tab
)


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
        """Create waveform and spectrogram visualization."""
        waveform = tk.Frame(parent, bg=COLORS['channel_bg'],
                          highlightbackground=COLORS['channel_border'],
                          highlightthickness=1)
        waveform.pack(fill=tk.X, pady=(0, 5), padx=2)

        tk.Label(waveform, text="VISUALIZATION", font=('', 9, 'bold'),
                fg=COLORS['fg_dim'], bg=COLORS['channel_bg']).pack(anchor=tk.W, padx=10, pady=(5, 2))

        # Original waveform + spectrogram
        orig_frame = tk.Frame(waveform, bg=COLORS['channel_bg'])
        orig_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(orig_frame, text="ORIGINAL", font=('', 8, 'bold'),
                fg=COLORS['success'], bg=COLORS['channel_bg']).pack(side=tk.LEFT)

        self.waveform_canvas = tk.Canvas(orig_frame, bg=COLORS['meter_bg'], height=50,
                                        highlightbackground=COLORS['channel_border'],
                                        highlightthickness=1)
        self.waveform_canvas.pack(fill=tk.X, padx=(10, 0), expand=True)

        orig_spec_frame = tk.Frame(waveform, bg=COLORS['channel_bg'])
        orig_spec_frame.pack(fill=tk.X, padx=10, pady=(0, 2))
        tk.Label(orig_spec_frame, text="SPECTROGRAM", font=('', 7, 'bold'),
                fg=COLORS['success'], bg=COLORS['channel_bg']).pack(side=tk.LEFT)

        self.spectrogram_canvas = tk.Canvas(orig_spec_frame, bg=COLORS['meter_bg'], height=80,
                                           highlightbackground=COLORS['channel_border'],
                                           highlightthickness=1)
        self.spectrogram_canvas.pack(fill=tk.X, padx=(10, 0), expand=True)

        # Modified waveform + spectrogram
        mod_frame = tk.Frame(waveform, bg=COLORS['channel_bg'])
        mod_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(mod_frame, text="MODIFIED", font=('', 8, 'bold'),
                fg=COLORS['warning'], bg=COLORS['channel_bg']).pack(side=tk.LEFT)

        self.modified_canvas = tk.Canvas(mod_frame, bg=COLORS['meter_bg'], height=50,
                                        highlightbackground=COLORS['channel_border'],
                                        highlightthickness=1)
        self.modified_canvas.pack(fill=tk.X, padx=(10, 0), expand=True)

        mod_spec_frame = tk.Frame(waveform, bg=COLORS['channel_bg'])
        mod_spec_frame.pack(fill=tk.X, padx=10, pady=(0, 2))
        tk.Label(mod_spec_frame, text="SPECTROGRAM", font=('', 7, 'bold'),
                fg=COLORS['warning'], bg=COLORS['channel_bg']).pack(side=tk.LEFT)

        self.modified_spectrogram_canvas = tk.Canvas(mod_spec_frame, bg=COLORS['meter_bg'], height=80,
                                                    highlightbackground=COLORS['channel_border'],
                                                    highlightthickness=1)
        self.modified_spectrogram_canvas.pack(fill=tk.X, padx=(10, 0), expand=True)

        self.waveform_info = tk.Label(waveform, text="No audio loaded",
                                     font=('', 8), fg=COLORS['fg_dim'], bg=COLORS['channel_bg'])
        self.waveform_info.pack(anchor=tk.W, padx=10, pady=(2, 5))

    def _create_params_notebook(self, parent: ttk.Frame) -> None:
        """Create parameter tabs."""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        tabs = [
            ("Basic", create_basic_tab, COLORS['basic']),
            ("EQ", create_eq_tab, COLORS['eq']),
            ("Filters", create_filters_tab, COLORS['eq']),
            ("Modulation", create_modulation_tab, COLORS['modulation']),
            ("Distortion", create_distortion_tab, COLORS['distortion']),
            ("Time", create_time_tab, COLORS['time']),
            ("Dynamics", create_dynamics_tab, COLORS['dynamics']),
            ("Utility", create_utility_tab, COLORS['utility']),
        ]

        for label, create_func, color in tabs:
            frame = ttk.Frame(notebook, padding="5")
            notebook.add(frame, text=label)
            create_func(self, frame)

    def _create_status_bar(self) -> None:
        """Create the status bar."""
        self.status_var = tk.StringVar(value="Ready - No audio loaded")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # Waveform drawing
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

    def _draw_spectrogram(self, audio: np.ndarray, canvas: tk.Canvas,
                          vmin: float = -80, vmax: float = 0) -> None:
        """Draw spectrogram on canvas using colored rectangles."""
        canvas.delete("all")
        if audio is None or len(audio) == 0:
            return
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width <= 1 or height <= 1:
            return

        # Compute spectrogram
        nperseg = min(1024, len(audio) // 4)
        if nperseg < 64:
            nperseg = 64
        noverlap = nperseg * 3 // 4

        try:
            f, t, Sxx = scipy_spectrogram(audio, fs=self.processor.sample_rate,
                                          nperseg=nperseg, noverlap=noverlap)
        except Exception:
            return

        # Convert to dB
        Sxx_db = 10 * np.log10(Sxx + 1e-10)

        # Limit to first half of frequencies (up to Nyquist)
        n_freqs = min(len(f), height)
        Sxx_db = Sxx_db[:n_freqs, :]

        # Reshape to fit canvas dimensions
        n_time = min(len(t), width)
        if n_time < 2 or n_freqs < 2:
            return

        # Downsample to fit
        time_indices = np.clip(np.linspace(0, n_time - 1, n_time).astype(int), 0, n_time - 1)
        freq_indices = np.clip(np.linspace(0, n_freqs - 1, n_freqs).astype(int), 0, n_freqs - 1)
        Sxx_resized = Sxx_db[np.ix_(freq_indices, time_indices)]

        # Normalize to 0-1 range
        Sxx_norm = np.clip((Sxx_resized - vmin) / (vmax - vmin), 0, 1)

        # Draw each cell as a colored rectangle
        cell_w = max(1, width // n_time)
        cell_h = max(1, height // n_freqs)

        for xi in range(n_time):
            for yi in range(n_freqs):
                val = Sxx_norm[yi, xi]
                if val < 0.01:
                    continue  # Skip very quiet cells
                r, g, b = self._spectrogram_colormap(val)
                color = f'#{r:02x}{g:02x}{b:02x}'
                x0 = xi * cell_w
                y0 = height - (yi + 1) * cell_h  # Flip Y (low freq at bottom)
                x1 = x0 + cell_w
                y1 = y0 + cell_h
                canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline='')

    @staticmethod
    def _spectrogram_colormap(val: float):
        """Convert 0-1 value to RGB for spectrogram (black->blue->green->yellow->red)."""
        val = max(0.0, min(1.0, val))
        if val < 0.25:
            # Black to dark blue
            t = val / 0.25
            return (0, 0, int(80 * t + 40))
        elif val < 0.5:
            # Dark blue to green
            t = (val - 0.25) / 0.25
            return (0, int(180 * t), int(120 - 40 * t))
        elif val < 0.75:
            # Green to yellow
            t = (val - 0.5) / 0.25
            return (int(220 * t), int(180 + 40 * t), 0)
        else:
            # Yellow to red
            t = (val - 0.75) / 0.25
            return (220 + int(35 * t), int(220 - 180 * t), 0)

    def _draw_original_waveform(self) -> None:
        """Draw original waveform and spectrogram."""
        self._draw_waveform(self.processor.original_audio, self.waveform_canvas, COLORS['success'])
        self._draw_spectrogram(self.processor.original_audio, self.spectrogram_canvas)

    def _draw_modified_waveform(self) -> None:
        """Draw modified waveform and spectrogram."""
        if self.processor.original_audio is None:
            return
        try:
            processed = self.processor.apply_process_all(self._get_params())
            self._draw_waveform(processed, self.modified_canvas, COLORS['warning'])
            self._draw_spectrogram(processed, self.modified_spectrogram_canvas)
        except Exception:
            pass

    # Logging
    def _log(self, message: str) -> None:
        """Log message to status bar."""
        self.status_var.set(message)

    # Audio file operations
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

    # Presets
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
        self.volume_var.set(params.get('volume', 1.0))
        self.pitch_var.set(params.get('pitch', 0.0))
        self.speed_var.set(params.get('speed', 1.0))

        eq = params.get('eq', {})
        self.eq_bass_var.set(eq.get('bass', 0.0))
        self.eq_low_mid_var.set(eq.get('low_mid', 0.0))
        self.eq_mid_var.set(eq.get('mid', 0.0))
        self.eq_high_mid_var.set(eq.get('high_mid', 0.0))
        self.eq_treble_var.set(eq.get('treble', 0.0))

        self.low_pass_var.set(params.get('low_pass', 20000))
        self.high_pass_var.set(params.get('high_pass', 20))

        self.chorus_var.set(params.get('chorus', 0.0))
        self.flanger_var.set(params.get('flanger', 0.0))
        self.phaser_var.set(params.get('phaser', 0.0))
        self.tremolo_var.set(params.get('tremolo', 0.0))
        self.vibrato_var.set(params.get('vibrato', 0.0))

        self.distortion_var.set(params.get('distortion', 0.0))
        self.bitcrusher_var.set(params.get('bitcrusher', 32))
        self.overdrive_var.set(params.get('overdrive', 1.0))

        self.reverb_var.set(params.get('reverb', 0.0))
        self.delay_var.set(params.get('delay', 0.0))

        self.comp_threshold_var.set(params.get('comp_threshold', -20.0))
        self.comp_ratio_var.set(params.get('comp_ratio', 4.0))
        self.gate_var.set(params.get('gate', -30.0))

        self.fade_in_var.set(params.get('fade_in', 0.0))
        self.fade_out_var.set(params.get('fade_out', 0.0))
        self.normalize_var.set(params.get('normalize', 0.0))
        self.trim_start_var.set(params.get('trim_start', 0.0))
        self.trim_end_var.set(params.get('trim_end', self.processor.duration if self.processor.duration else 0))
        self.reverse_var.set(params.get('reverse', False))

    # Playback
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

    # Slider callbacks
    def _on_slider_release(self) -> None:
        """Handle slider release for auto-preview."""
        self._draw_modified_waveform()
        if self.auto_preview_var.get():
            self._play_modified()

    def _on_reverse_change(self) -> None:
        """Handle reverse checkbox change."""
        self._draw_modified_waveform()
        if self.auto_preview_var.get():
            self._play_modified()

    # Animation
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
        for fader in self.faders:
            fader.set_audio_level(0.0)
        if hasattr(self, 'vu_meter'):
            self.vu_meter.set_level(0.0)
        if hasattr(self, 'vu_value_label') and self.vu_value_label.winfo_exists():
            self.vu_value_label.configure(text="-20.0 dB")

    def _animate_meters(self, generation: int = 0) -> None:
        """Update meter levels based on audio position."""
        if generation != self._animation_generation:
            return
        if not self.isAnimating or self.playback_audio is None:
            return

        window_size = 1024
        start = int(self.playback_position)
        end = min(start + window_size, len(self.playback_audio))

        if start < len(self.playback_audio):
            audio_window = self.playback_audio[start:end]
            rms = np.sqrt(np.mean(audio_window ** 2))

            if rms > 0:
                level_db = 20 * np.log10(rms)
            else:
                level_db = -60

            vu_db_min = self.vu_meter._db_min
            vu_db_max = self.vu_meter._db_max
            level = np.clip((level_db - vu_db_min) / (vu_db_max - vu_db_min), 0.0, 1.0)

            for fader in self.faders:
                fader.set_audio_level(level)

            if hasattr(self, 'vu_meter'):
                self.vu_meter.set_level(level)
                if hasattr(self, 'vu_value_label') and self.vu_value_label.winfo_exists():
                    self.vu_value_label.configure(text=f"{level_db:.1f} dB")

            self.playback_position += self.playback_sample_rate // 30

            if self.playback_position >= len(self.playback_audio):
                self.playback_position = 0
        else:
            self.playback_position = 0
            for fader in self.faders:
                fader.set_audio_level(0.0)
            if hasattr(self, 'vu_meter'):
                self.vu_meter.set_level(0.0)
                if hasattr(self, 'vu_value_label') and self.vu_value_label.winfo_exists():
                    self.vu_value_label.configure(text="-20.0 dB")

        if self.isAnimating:
            self.animation_id = self.root.after(33, lambda: self._animate_meters(generation))

    # Parameters
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
