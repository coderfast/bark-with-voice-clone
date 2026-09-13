"""
Shared generation utilities for Bark notebooks.

This module contains common generation functions used across
generate.ipynb, generate_chunked.ipynb, and test_models.ipynb.
"""

import os
import re
from typing import Optional, Dict, Any, Union

import numpy as np
import torch
import torch.nn.functional as F
from scipy.io.wavfile import write as write_wav
from IPython.display import Audio

from bark.generation import (
    SAMPLE_RATE,
    generate_text_semantic,
    generate_coarse,
    generate_fine,
    codec_decode,
)


def split_and_recombine_text(
    text: str,
    desired_length: int = 100,
    max_length: int = 150
) -> list:
    """Split text into chunks of a desired length trying to keep sentences intact.

    From https://github.com/neonbjb/tortoise-tts

    Args:
        text: Input text to split
        desired_length: Target chunk length
        max_length: Maximum chunk length

    Returns:
        List of text chunks
    """
    # Normalize text
    text = re.sub(r"\n\n+", "\n", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[\u201c\u201d]", '"', text)

    rv = []
    in_quote = False
    current = ""
    split_pos = []
    pos = -1
    end_pos = len(text) - 1

    def seek(delta):
        nonlocal pos, in_quote, current
        is_neg = delta < 0
        for _ in range(abs(delta)):
            if is_neg:
                pos -= 1
                current = current[:-1]
            else:
                pos += 1
                current += text[pos]
            if text[pos] == '"':
                in_quote = not in_quote
        return text[pos]

    def peek(delta):
        p = pos + delta
        return text[p] if p < end_pos and p >= 0 else ""

    def commit():
        nonlocal rv, current, split_pos
        rv.append(current)
        current = ""
        split_pos = []

    while pos < end_pos:
        c = seek(1)
        # Force split if too long
        if len(current) >= max_length:
            if len(split_pos) > 0 and len(current) > (desired_length / 2):
                d = pos - split_pos[-1]
                seek(-d)
            else:
                while c not in "!?.\n " and pos > 0 and len(current) > desired_length:
                    c = seek(-1)
            commit()
        # Check for sentence boundaries
        elif not in_quote and (c in "!?\n" or (c == "." and peek(1) in "\n ")):
            while (
                pos < len(text) - 1 and len(current) < max_length and peek(1) in "!?."
            ):
                c = seek(1)
            split_pos.append(pos)
            if len(current) >= desired_length:
                commit()
        # Treat end of quote as boundary if followed by space or newline
        elif in_quote and peek(1) == '"' and peek(2) in "\n ":
            seek(2)
            split_pos.append(pos)
    rv.append(current)

    # Clean up
    rv = [s.strip() for s in rv]
    rv = [s for s in rv if len(s) > 0 and not re.match(r"^[\s\.,;:!?]*$", s)]

    return rv


def generate_with_settings(
    text_prompt: str,
    semantic_temp: float = 0.7,
    semantic_top_k: int = 50,
    semantic_top_p: float = 0.95,
    coarse_temp: float = 0.7,
    coarse_top_k: int = 50,
    coarse_top_p: float = 0.95,
    fine_temp: float = 0.5,
    voice_name: Optional[str] = None,
    use_semantic_history_prompt: bool = True,
    use_coarse_history_prompt: bool = True,
    use_fine_history_prompt: bool = True,
    output_full: bool = False,
) -> Union[np.ndarray, tuple]:
    """Generate audio with full control over generation parameters.

    Args:
        text_prompt: Text to generate audio for
        semantic_temp: Temperature for semantic generation
        semantic_top_k: Top-k for semantic generation
        semantic_top_p: Top-p for semantic generation
        coarse_temp: Temperature for coarse generation
        coarse_top_k: Top-k for coarse generation
        coarse_top_p: Top-p for coarse generation
        fine_temp: Temperature for fine generation
        voice_name: Voice prompt name or path
        use_semantic_history_prompt: Use voice prompt for semantic generation
        use_coarse_history_prompt: Use voice prompt for coarse generation
        use_fine_history_prompt: Use voice prompt for fine generation
        output_full: Return full generation dict along with audio

    Returns:
        Audio array, or tuple of (full_generation, audio) if output_full=True
    """
    x_semantic = generate_text_semantic(
        text_prompt,
        history_prompt=voice_name if use_semantic_history_prompt else None,
        temp=semantic_temp,
        top_k=semantic_top_k,
        top_p=semantic_top_p,
    )

    x_coarse_gen = generate_coarse(
        x_semantic,
        history_prompt=voice_name if use_coarse_history_prompt else None,
        temp=coarse_temp,
        top_k=coarse_top_k,
        top_p=coarse_top_p,
    )
    x_fine_gen = generate_fine(
        x_coarse_gen,
        history_prompt=voice_name if use_fine_history_prompt else None,
        temp=fine_temp,
    )

    if output_full:
        full_generation = {
            'semantic_prompt': x_semantic,
            'coarse_prompt': x_coarse_gen,
            'fine_prompt': x_fine_gen,
        }
        return full_generation, codec_decode(x_fine_gen)
    return codec_decode(x_fine_gen)


def play_audio(audio_array: np.ndarray, rate: int = SAMPLE_RATE) -> Audio:
    """Play audio in Jupyter notebook.

    Args:
        audio_array: Audio samples
        rate: Sample rate

    Returns:
        IPython Audio object
    """
    return Audio(audio_array, rate=rate)


def save_audio(
    filepath: str,
    audio_array: np.ndarray,
    rate: int = SAMPLE_RATE
) -> None:
    """Save audio array to WAV file.

    Args:
        filepath: Output file path
        audio_array: Audio samples
        rate: Sample rate
    """
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
    write_wav(filepath, rate, audio_array)
