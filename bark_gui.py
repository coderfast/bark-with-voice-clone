"""
Bark Voice Clone - Graphical User Interface

A simple GUI for generating audio with Bark text-to-speech and voice cloning.

Usage:
    python bark_gui.py
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import Optional
import time


class BarkGUI:
    """Main GUI application for Bark Voice Clone."""

    def __init__(self, root):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("Bark Voice Clone - Text to Speech")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Variables
        self.text_var = tk.StringVar()
        self.voice_var = tk.StringVar(value="es_speaker_0")
        self.output_var = tk.StringVar(value="output.wav")
        self.sample_rate_var = tk.StringVar(value="24000")
        self.bits_var = tk.StringVar(value="float32")
        self.channels_var = tk.StringVar(value="mono")
        self.small_models_var = tk.BooleanVar(value=False)
        self.is_generating = False

        # Available voices
        self.voices = self._get_available_voices()

        # Create UI
        self._create_menu()
        self._create_main_frame()
        self._create_status_bar()

    def _get_available_voices(self):
        """Get list of available voices."""
        voices = []
        languages = {
            "es": "Español",
            "en": "English",
            "de": "Deutsch",
            "fr": "Français",
            "it": "Italiano",
            "pt": "Português",
            "ja": "日本語",
            "ko": "한국어",
            "zh": "中文",
            "hi": "हिन्दी",
            "pl": "Polski",
            "ru": "Русский",
            "tr": "Türkçe",
        }
        for lang_code, lang_name in languages.items():
            for i in range(10):
                voice_name = f"{lang_code}_speaker_{i}"
                voices.append(f"{voice_name} ({lang_name})")
        return voices

    def _create_menu(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Settings", command=self._save_settings)
        file_menu.add_command(label="Load Settings", command=self._load_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._exit_app)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _create_main_frame(self):
        """Create the main application frame."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Input
        left_frame = ttk.LabelFrame(main_frame, text="Input", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Text input
        ttk.Label(left_frame, text="Text to generate:").pack(anchor=tk.W)
        self.text_input = scrolledtext.ScrolledText(
            left_frame, height=10, width=40, wrap=tk.WORD
        )
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Voice selection
        ttk.Label(left_frame, text="Voice:").pack(anchor=tk.W)
        voice_frame = ttk.Frame(left_frame)
        voice_frame.pack(fill=tk.X, pady=(0, 10))

        self.voice_combo = ttk.Combobox(
            voice_frame,
            textvariable=self.voice_var,
            values=self.voices,
            state="readonly",
        )
        self.voice_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(voice_frame, text="Voices", command=self._show_voices).pack(
            side=tk.RIGHT, padx=(5, 0)
        )

        # Right panel - Settings
        right_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Output file
        ttk.Label(right_frame, text="Output file:").pack(anchor=tk.W)
        output_frame = ttk.Frame(right_frame)
        output_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Entry(output_frame, textvariable=self.output_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(output_frame, text="Browse", command=self._browse_output).pack(
            side=tk.RIGHT, padx=(5, 0)
        )

        # Sample rate
        ttk.Label(right_frame, text="Sample rate:").pack(anchor=tk.W)
        sample_rates = ["11025", "22050", "24000", "44100"]
        ttk.Combobox(
            right_frame,
            textvariable=self.sample_rate_var,
            values=sample_rates,
            state="readonly",
        ).pack(fill=tk.X, pady=(0, 10))

        # Bits per sample
        ttk.Label(right_frame, text="Bits per sample:").pack(anchor=tk.W)
        bits_options = ["8", "16", "float32"]
        ttk.Combobox(
            right_frame,
            textvariable=self.bits_var,
            values=bits_options,
            state="readonly",
        ).pack(fill=tk.X, pady=(0, 10))

        # Channels
        ttk.Label(right_frame, text="Channels:").pack(anchor=tk.W)
        channels_options = ["mono", "stereo"]
        ttk.Combobox(
            right_frame,
            textvariable=self.channels_var,
            values=channels_options,
            state="readonly",
        ).pack(fill=tk.X, pady=(0, 10))

        # Small models checkbox
        ttk.Checkbutton(
            right_frame,
            text="Use small models (faster)",
            variable=self.small_models_var,
        ).pack(anchor=tk.W, pady=(0, 10))

        # Buttons
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        self.generate_btn = ttk.Button(
            button_frame, text="Generate Audio", command=self._generate_audio
        )
        self.generate_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(button_frame, text="Clear", command=self._clear_text).pack(
            side=tk.LEFT, padx=(0, 5)
        )

        ttk.Button(button_frame, text="Exit", command=self._exit_app).pack(
            side=tk.RIGHT
        )

        # Bottom panel - Log
        bottom_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.log_text = scrolledtext.ScrolledText(
            bottom_frame, height=8, width=80, state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _create_status_bar(self):
        """Create the status bar."""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _log(self, message):
        """Add message to log."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _browse_output(self):
        """Browse for output file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
        )
        if filename:
            self.output_var.set(filename)

    def _show_voices(self):
        """Show available voices dialog."""
        voices_text = "Available Voices:\n\n"
        current_lang = ""
        for voice in self.voices:
            lang_code = voice.split("_")[0]
            if lang_code != current_lang:
                current_lang = lang_code
                voices_text += f"\n{voice.split('(')[1].replace(')', '')}:\n"
            voices_text += f"  {voice.split(' ')[0]}\n"

        messagebox.showinfo("Available Voices", voices_text)

    def _clear_text(self):
        """Clear text input."""
        self.text_input.delete("1.0", tk.END)

    def _exit_app(self):
        """Exit the application."""
        if self.is_generating:
            if messagebox.askyesno("Exit", "Audio generation in progress. Exit anyway?"):
                self.root.quit()
                self.root.destroy()
        else:
            self.root.quit()
            self.root.destroy()

    def _save_settings(self):
        """Save current settings to file."""
        settings = {
            "voice": self.voice_var.get(),
            "sample_rate": self.sample_rate_var.get(),
            "bits": self.bits_var.get(),
            "channels": self.channels_var.get(),
            "small_models": self.small_models_var.get(),
        }

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if filename:
            import json
            with open(filename, "w") as f:
                json.dump(settings, f, indent=2)
            self._log(f"Settings saved to {filename}")

    def _load_settings(self):
        """Load settings from file."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            import json
            with open(filename, "r") as f:
                settings = json.load(f)
            self.voice_var.set(settings.get("voice", "es_speaker_0"))
            self.sample_rate_var.set(settings.get("sample_rate", "24000"))
            self.bits_var.set(settings.get("bits", "float32"))
            self.channels_var.set(settings.get("channels", "mono"))
            self.small_models_var.set(settings.get("small_models", False))
            self._log(f"Settings loaded from {filename}")

    def _show_about(self):
        """Show about dialog."""
        about_text = """Bark Voice Clone - GUI

A graphical interface for Bark text-to-speech
with voice cloning capabilities.

Features:
- Text-to-speech generation
- Voice cloning
- Multiple languages support
- Custom audio format options

Based on:
- Suno's BARK model
- HuBERT voice cloning
- RVC voice conversion

License: MIT"""
        messagebox.showinfo("About", about_text)

    def _generate_audio(self):
        """Generate audio from text."""
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter text to generate.")
            return

        if self.is_generating:
            messagebox.showwarning("Warning", "Generation already in progress.")
            return

        # Get settings
        voice = self.voice_var.get().split(" ")[0]  # Extract voice name
        output = self.output_var.get()
        sample_rate = self.sample_rate_var.get()
        bits = self.bits_var.get()
        channels = self.channels_var.get()
        small_models = self.small_models_var.get()

        # Validate output path
        if not output:
            messagebox.showwarning("Warning", "Please specify output file.")
            return

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)

        # Start generation in separate thread
        self.is_generating = True
        self.generate_btn.config(state=tk.DISABLED)
        self.status_var.set("Generating audio...")
        self._log(f"Starting generation: '{text[:50]}...'")

        thread = threading.Thread(
            target=self._generate_thread,
            args=(text, voice, output, sample_rate, bits, channels, small_models),
            daemon=True,
        )
        thread.start()

    def _generate_thread(
        self,
        text,
        voice,
        output,
        sample_rate,
        bits,
        channels,
        small_models,
    ):
        """Generate audio in separate thread."""
        try:
            # Import bark
            from bark import SAMPLE_RATE, generate_audio, preload_models
            from bark.api import save_audio

            # Load models
            self.root.after(0, self._log, "Loading models...")
            start_time = time.time()
            preload_models(
                text_use_small=small_models,
                coarse_use_small=small_models,
                fine_use_small=small_models,
            )
            load_time = time.time() - start_time
            self.root.after(0, self._log, f"Models loaded in {load_time:.1f}s")

            # Generate audio
            self.root.after(0, self._log, "Generating audio...")
            start_time = time.time()

            # Parse settings
            sr = int(sample_rate) if sample_rate != "24000" else None
            bps = int(bits) if bits != "float32" else None
            ch = channels if channels != "mono" else None

            audio = generate_audio(
                text,
                history_prompt=voice,
                sample_rate=sr,
                bits_per_sample=bps,
                channels=ch,
            )

            gen_time = time.time() - start_time
            self.root.after(0, self._log, f"Audio generated in {gen_time:.1f}s")

            # Save audio
            effective_sr = sr if sr else SAMPLE_RATE
            save_audio(output, audio, sample_rate=effective_sr, source_sample_rate=effective_sr)

            # Get file size
            file_size = os.path.getsize(output)
            size_str = (
                f"{file_size / (1024 * 1024):.1f} MB"
                if file_size > 1024 * 1024
                else f"{file_size / 1024:.1f} KB"
            )

            self.root.after(0, self._log, f"Audio saved to: {output} ({size_str})")
            self.root.after(0, self.status_var.set, "Generation complete!")
            self.root.after(
                0,
                messagebox.showinfo,
                "Success",
                f"Audio generated successfully!\n\nSaved to: {output}\nSize: {size_str}",
            )

        except Exception as e:
            error_msg = str(e)
            self.root.after(0, self._log, f"Error: {error_msg}")
            self.root.after(0, self.status_var.set, "Generation failed!")
            self.root.after(
                0,
                messagebox.showerror,
                "Error",
                f"Failed to generate audio:\n\n{error_msg}",
            )

        finally:
            self.is_generating = False
            self.root.after(0, self.generate_btn.config, (), {"state": "normal"})


def main():
    """Main entry point."""
    root = tk.Tk()
    app = BarkGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
