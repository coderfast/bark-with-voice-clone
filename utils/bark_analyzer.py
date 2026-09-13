"""
Bark Analyzer - TTS-Specific Visualizations

Generates visualizations specific to Bark TTS:
- EnCodec Codebook (_codebook.png)
- Attention Matrix (_attention.png)
- Waveform Comparison (_comparison.png)
"""

import os
from typing import Optional

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

STYLE = {
    'bg': '#0e1117', 'panel': '#161b22', 'grid': '#21262d',
    'text': '#c9d1d9', 'text_dim': '#8b949e',
    'codebook': ['#ff7b72', '#ffa657', '#d2a8ff', '#79c0ff',
                 '#3fb950', '#58a6ff', '#f0883e', '#d2a8ff'],
}


def _apply_style(fig, ax):
    fig.patch.set_facecolor(STYLE['bg'])
    ax.set_facecolor(STYLE['panel'])
    ax.tick_params(colors=STYLE['text_dim'], which='both')
    ax.xaxis.label.set_color(STYLE['text'])
    ax.yaxis.label.set_color(STYLE['text'])
    ax.title.set_color(STYLE['text'])
    ax.grid(True, alpha=0.15, color=STYLE['grid'])
    for spine in ax.spines.values():
        spine.set_color(STYLE['grid'])


# ── 1. ENCODEC CODEBOOK ────────────────────────────────────────────────────

def generate_encodec_codebook(
    codes: np.ndarray,
    filepath: str,
    figsize: tuple = (12, 6),
    title: Optional[str] = None,
) -> str:
    """Generate EnCodec codebook visualization.

    Shows the discrete code indices for each of the 8 EnCodec
    codebooks over time. Each row is one codebook level.

    Useful for:
    - Understanding Bark's internal audio representation
    - Detecting quantization artifacts
    - Comparing codebook usage between original and generated audio

    Args:
        codes: Array of shape (n_codebooks, n_frames) with code indices
        filepath: Output file path
        figsize: Figure size
        title: Plot title

    Returns:
        Path to saved plot
    """
    if codes.ndim == 1:
        codes = codes.reshape(1, -1)

    n_codebooks, n_frames = codes.shape

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    _apply_style(fig, ax)

    # Plot each codebook as a separate row
    for i in range(n_codebooks):
        y_offset = i * 1.3
        codes_normalized = codes[i] / (codes[i].max() + 1) if codes[i].max() > 0 else codes[i]
        color = STYLE['codebook'][i % len(STYLE['codebook'])]

        ax.scatter(
            np.arange(n_frames), codes_normalized + y_offset,
            c=[color], s=1, alpha=0.6, marker='|',
        )

    ax.set_xlabel('Frame')
    ax.set_ylabel('Codebook Level')
    ax.set_title(title or f'EnCodec Codebook ({n_codebooks} levels)')

    # Y-axis labels
    ax.set_yticks([i * 1.3 for i in range(n_codebooks)])
    ax.set_yticklabels([f'CB {i}' for i in range(n_codebooks)])
    ax.set_xlim([0, n_frames - 1])

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath


# ── 2. ATTENTION MATRIX ────────────────────────────────────────────────────

def generate_attention_matrix(
    attention: np.ndarray,
    filepath: str,
    x_labels: Optional[list] = None,
    y_labels: Optional[list] = None,
    figsize: tuple = (10, 8),
    title: Optional[str] = None,
    layer: Optional[int] = None,
) -> str:
    """Generate attention weight matrix visualization.

    Shows which input tokens the model is "looking at" when
    producing each output frame.

    Useful for:
    - Debugging TTS generation quality
    - Detecting misalignment (garbled speech, skipped words)
    - Understanding model behavior across layers

    Args:
        attention: 2D array of attention weights (n_rows, n_cols)
        filepath: Output file path
        x_labels: Optional labels for x-axis (e.g., input tokens)
        y_labels: Optional labels for y-axis (e.g., output frames)
        figsize: Figure size
        title: Plot title
        layer: Layer number (for title)

    Returns:
        Path to saved plot
    """
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    _apply_style(fig, ax)

    cmap = plt.cm.YlOrRd
    im = ax.imshow(attention, cmap=cmap, aspect='auto', vmin=0, vmax=1)

    if x_labels is not None:
        ax.set_xticks(range(len(x_labels)))
        ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=7,
                           color=STYLE['text'])
    else:
        ax.set_xlabel('Input Position')

    if y_labels is not None:
        ax.set_yticks(range(len(y_labels)))
        ax.set_yticklabels(y_labels, fontsize=7, color=STYLE['text'])
    else:
        ax.set_ylabel('Output Position')

    layer_str = f' (Layer {layer})' if layer is not None else ''
    ax.set_title(title or f'Attention Matrix{layer_str}')

    cbar = fig.colorbar(im, ax=ax, label='Attention Weight')
    cbar.ax.yaxis.label.set_color(STYLE['text'])
    cbar.ax.tick_params(colors=STYLE['text_dim'])

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath


# ── 3. WAVEFORM COMPARISON ─────────────────────────────────────────────────

def generate_waveform_comparison(
    audio_original: np.ndarray,
    audio_generated: np.ndarray,
    sample_rate: int,
    filepath: str,
    figsize: tuple = (12, 6),
    title: Optional[str] = None,
) -> str:
    """Generate side-by-side waveform comparison with residual.

    Shows original vs generated audio with a residual (difference)
    waveform below. Structured patterns in the residual indicate
    systematic deviations.

    Args:
        audio_original: Original audio array
        audio_generated: Generated audio array
        sample_rate: Sample rate in Hz
        filepath: Output file path
        figsize: Figure size
        title: Plot title

    Returns:
        Path to saved plot
    """
    if audio_original.ndim > 1:
        audio_original = np.mean(audio_original, axis=0)
    if audio_generated.ndim > 1:
        audio_generated = np.mean(audio_generated, axis=0)

    # Ensure same length
    min_len = min(len(audio_original), len(audio_generated))
    audio_original = audio_original[:min_len]
    audio_generated = audio_generated[:min_len]
    time = np.arange(min_len) / sample_rate

    # Compute residual
    residual = audio_original - audio_generated

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=figsize,
                                          height_ratios=[1, 1, 1],
                                          sharex=True)
    fig.patch.set_facecolor(STYLE['bg'])

    # Original
    _apply_style(fig, ax1)
    ax1.plot(time, audio_original, color='#3fb950', linewidth=0.4, alpha=0.9)
    ax1.fill_between(time, audio_original, alpha=0.2, color='#3fb950')
    ax1.set_ylabel('Amplitude')
    ax1.set_title(title or 'Waveform Comparison: Original vs Generated')
    ax1.set_ylim([-1.15, 1.15])

    # Generated
    _apply_style(fig, ax2)
    ax2.plot(time, audio_generated, color='#58a6ff', linewidth=0.4, alpha=0.9)
    ax2.fill_between(time, audio_generated, alpha=0.2, color='#58a6ff')
    ax2.set_ylabel('Amplitude')
    ax2.set_ylim([-1.15, 1.15])

    # Residual
    _apply_style(fig, ax3)
    ax3.plot(time, residual, color='#ff7b72', linewidth=0.4, alpha=0.9)
    ax3.fill_between(time, residual, alpha=0.2, color='#ff7b72')
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Residual')
    ax3.set_ylim([-1.15, 1.15])

    # Labels
    ax1.text(0.02, 0.95, 'ORIGINAL', transform=ax1.transAxes,
             color='#3fb950', fontsize=10, fontweight='bold', va='top')
    ax2.text(0.02, 0.95, 'GENERATED', transform=ax2.transAxes,
             color='#58a6ff', fontsize=10, fontweight='bold', va='top')
    ax3.text(0.02, 0.95, 'RESIDUAL', transform=ax3.transAxes,
             color='#ff7b72', fontsize=10, fontweight='bold', va='top')

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath
