"""
Voice Filter - Audio Processing Application

A GUI application for loading and modifying audio files in real-time.
Supports WAV, MP3, AAC, FLAC, OGG, M4A, WMA and other common audio formats.

Features:
- 20+ audio effects and filters
- Auto-preview mode (plays on slider release)
- Color-coded UI
- Cross-platform (Windows, Linux, macOS)

Requirements:
- Python 3.8+
- ffmpeg in app_voice_filter/ffmpeg/bin/ or in PATH (for MP3/AAC/M4A/WMA)

Usage:
    python voice_filter.py
"""

import sys
import platform

# Enable high-DPI awareness on Windows (prevents blurry UI at 150%+ scaling)
if platform.system() == "Windows":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

from gui.app import main

if __name__ == "__main__":
    main()
