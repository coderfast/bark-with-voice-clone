"""
Speech Analyzer - Advanced Voice Analysis Visualizations

Generates speech-specific visualizations for TTS evaluation:
- Mel Spectrogram (_mel.png)
- MFCC Heatmap (_mfcc.png)
- Formant Tracking (_formants.png)
- Pitch + Voicing Probability (_pitch_voiced.png)
- Intensity Contour (_intensity.png)
- Jitter & Shimmer (_jitter_shimmer.png)
- Harmonic-to-Noise Ratio (_hnr.png)
"""

import os
from typing import Optional, Tuple

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import signal
import librosa

# Dark theme (matching audio_visualizer.py)
STYLE = {
    'bg': '#0e1117', 'panel': '#161b22', 'grid': '#21262d',
    'text': '#c9d1d9', 'text_dim': '#8b949e',
    'wave': '#58a6ff', 'wave_fill': '#1f6feb',
    'pitch': '#3fb950', 'sweep': '#f0883e',
    'mel': '#d2a8ff', 'mfcc': '#79c0ff',
    'formant': '#ff7b72', 'voicing': '#3fb950',
    'intensity': '#ffa657', 'jitter': '#f778ba', 'shimmer': '#d2a8ff',
    'hnr': '#58a6ff',
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


def _ensure_mono(audio: np.ndarray) -> np.ndarray:
    if audio.ndim > 1:
        return np.mean(audio, axis=0)
    return audio


# ── 1. MEL SPECTROGRAM ─────────────────────────────────────────────────────

def generate_mel_spectrogram(
    audio: np.ndarray,
    sample_rate: int,
    filepath: str,
    n_mels: int = 128,
    figsize: tuple = (12, 4),
    title: Optional[str] = None,
) -> str:
    """Generate Mel spectrogram (perceptual frequency scale).

    Most important visualization for neural TTS evaluation.
    The Mel scale mimics human auditory perception.

    Args:
        audio: Audio array
        sample_rate: Sample rate in Hz
        filepath: Output file path
        n_mels: Number of Mel bands
        figsize: Figure size
        title: Plot title

    Returns:
        Path to saved plot
    """
    audio = _ensure_mono(audio).astype(np.float32)

    S = librosa.feature.melspectrogram(y=audio, sr=sample_rate, n_mels=n_mels)
    S_db = librosa.power_to_db(S, ref=np.max)

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    _apply_style(fig, ax)

    img = librosa.display.specshow(
        S_db, sr=sample_rate, x_axis='time', y_axis='mel',
        ax=ax, cmap='magma', vmin=-80, vmax=0,
    )

    ax.set_title(title or 'Mel Spectrogram')
    cbar = fig.colorbar(img, ax=ax, format='%+2.0f dB')
    cbar.ax.yaxis.label.set_color(STYLE['text'])
    cbar.ax.tick_params(colors=STYLE['text_dim'])

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath


# ── 2. MFCC HEATMAP ────────────────────────────────────────────────────────

def generate_mfcc(
    audio: np.ndarray,
    sample_rate: int,
    filepath: str,
    n_mfcc: int = 20,
    figsize: tuple = (12, 4),
    title: Optional[str] = None,
) -> str:
    """Generate MFCC heatmap (speaker identity features).

    MFCCs are the gold standard for speaker identification
    and voice conversion evaluation.

    Args:
        audio: Audio array
        sample_rate: Sample rate in Hz
        filepath: Output file path
        n_mfcc: Number of MFCC coefficients
        figsize: Figure size
        title: Plot title

    Returns:
        Path to saved plot
    """
    audio = _ensure_mono(audio).astype(np.float32)

    mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=n_mfcc)

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    _apply_style(fig, ax)

    img = librosa.display.specshow(
        mfccs, sr=sample_rate, x_axis='time',
        ax=ax, cmap='coolwarm',
    )

    ax.set_title(title or f'MFCC ({n_mfcc} coefficients)')
    ax.set_ylabel('MFCC Coefficient')
    cbar = fig.colorbar(img, ax=ax)
    cbar.ax.yaxis.label.set_color(STYLE['text'])
    cbar.ax.tick_params(colors=STYLE['text_dim'])

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath


# ── 3. FORMANT TRACKING ────────────────────────────────────────────────────

def generate_formants(
    audio: np.ndarray,
    sample_rate: int,
    filepath: str,
    n_formants: int = 4,
    figsize: tuple = (12, 5),
    title: Optional[str] = None,
) -> str:
    """Generate formant tracking visualization.

    Formants (F1-F4) are the resonant frequencies of the vocal tract.
    They identify vowel quality and speaker identity.

    Args:
        audio: Audio array
        sample_rate: Sample rate in Hz
        filepath: Output file path
        n_formants: Number of formants to track
        figsize: Figure size
        title: Plot title

    Returns:
        Path to saved plot
    """
    audio = _ensure_mono(audio).astype(np.float32)

    # Compute spectrogram
    nperseg = min(2048, len(audio) // 4)
    f_spec, t_spec, Sxx = signal.spectrogram(
        audio, fs=sample_rate, nperseg=nperseg, noverlap=nperseg // 2,
    )

    # LPC-based formant estimation
    frame_length = min(2048, len(audio) // 4)
    hop = frame_length // 2
    n_frames = 1 + (len(audio) - frame_length) // hop
    lpc_order = 2 + sample_rate // 1000

    formant_freqs = []
    formant_times = []

    for i in range(n_frames):
        start = i * hop
        frame = audio[start:start + frame_length]
        windowed = frame * np.hamming(len(frame))

        # LPC analysis
        try:
            # Autocorrelation-based LPC
            r = np.correlate(windowed, windowed, mode='full')
            r = r[len(r)//2:lpc_order + 1]
            # Levinson-Durbin
            a = np.zeros(lpc_order + 1)
            a[0] = 1.0
            if r[0] > 0:
                ref = np.zeros(lpc_order)
                ref[0] = r[1] / r[0]
                a[1] = ref[0]
                for i in range(1, lpc_order):
                    acc = r[i + 1]
                    for j in range(i):
                        acc -= a[j + 1] * r[i - j]
                    ref[i] = acc / (r[0] * np.prod(1 - ref[:i]**2))
                    for j in range(i, 0, -1):
                        a[j + 1] = a[j] - ref[i] * a[i - j + 1]
                    a[i + 1] = ref[i]

            # Find formants from LPC polynomial roots
            r = np.roots(a)
            r = r[np.imag(r) >= 0]
            angles = np.arctan2(np.imag(r), np.real(r))
            freqs = angles * (sample_rate / (2 * np.pi))
            freqs = np.sort(freqs[(freqs > 50) & (freqs < sample_rate / 2)])

            # Take top n_formants
            if len(freqs) >= n_formants:
                formant_freqs.append(freqs[:n_formants])
            else:
                padded = np.full(n_formants, np.nan)
                padded[:len(freqs)] = freqs
                formant_freqs.append(padded)
        except Exception:
            formant_freqs.append(np.full(n_formants, np.nan))

        formant_times.append((start + frame_length / 2) / sample_rate)

    formant_freqs = np.array(formant_freqs)
    formant_times = np.array(formant_times)

    # Compute spectrogram for background
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    _apply_style(fig, ax)

    # Background spectrogram
    Sxx_db = 10 * np.log10(Sxx + 1e-10)
    ax.pcolormesh(t_spec, f_spec, Sxx_db, shading='gouraud',
                  cmap='gray_r', alpha=0.3, vmin=-80, vmax=0)

    # Plot formant lines
    colors = ['#ff7b72', '#ffa657', '#d2a8ff', '#79c0ff']
    labels = ['F1', 'F2', 'F3', 'F4']
    for j in range(min(n_formants, formant_freqs.shape[1])):
        valid = ~np.isnan(formant_freqs[:, j])
        if np.any(valid):
            ax.plot(formant_times[valid], formant_freqs[valid, j],
                    color=colors[j % len(colors)], linewidth=1.5,
                    alpha=0.9, label=labels[j])

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Frequency (Hz)')
    ax.set_title(title or 'Formant Tracking (F1-F4)')
    ax.set_ylim([0, min(5000, sample_rate / 2)])
    ax.legend(loc='upper right', fontsize=8,
              facecolor=STYLE['panel'], edgecolor=STYLE['grid'],
              labelcolor=STYLE['text'])

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath


# ── 4. PITCH + VOICING PROBABILITY ─────────────────────────────────────────

def generate_pitch_voicing(
    audio: np.ndarray,
    sample_rate: int,
    filepath: str,
    figsize: tuple = (12, 5),
    title: Optional[str] = None,
) -> str:
    """Generate pitch contour with voicing probability.

    Shows F0 (fundamental frequency) and voicing probability (0-1)
    to distinguish voiced vs unvoiced segments.

    Args:
        audio: Audio array
        sample_rate: Sample rate in Hz
        filepath: Output file path
        figsize: Figure size
        title: Plot title

    Returns:
        Path to saved plot
    """
    audio = _ensure_mono(audio).astype(np.float32)

    # Use librosa for pitch and voicing
    f0, voiced_flag, voiced_probs = librosa.pyin(
        audio, fmin=librosa.note_to_hz('C2'),
        fmax=librosa.note_to_hz('C7'),
        sr=sample_rate,
    )
    times = librosa.times_like(f0, sr=sample_rate)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, height_ratios=[2, 1],
                                    sharex=True)
    fig.patch.set_facecolor(STYLE['bg'])

    # Top: Pitch contour
    _apply_style(fig, ax1)
    valid = ~np.isnan(f0)
    if np.any(valid):
        ax1.plot(times[valid], f0[valid], color=STYLE['pitch'],
                 linewidth=1.5, alpha=0.9)
        ax1.fill_between(times[valid], f0[valid], alpha=0.15, color=STYLE['pitch'])

    ax1.set_ylabel('F0 (Hz)')
    ax1.set_title(title or 'Pitch + Voicing Probability')
    ax1.set_yscale('log')
    ax1.set_ylim([80, 600])
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}'))

    # Bottom: Voicing probability
    _apply_style(fig, ax2)
    ax2.fill_between(times, voiced_probs, alpha=0.4, color=STYLE['voicing'])
    ax2.plot(times, voiced_probs, color=STYLE['voicing'], linewidth=0.8)
    ax2.axhline(y=0.5, color=STYLE['text_dim'], linewidth=0.5, linestyle='--')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Voicing Prob.')
    ax2.set_ylim([0, 1.05])

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath


# ── 5. INTENSITY CONTOUR ───────────────────────────────────────────────────

def generate_intensity(
    audio: np.ndarray,
    sample_rate: int,
    filepath: str,
    figsize: tuple = (12, 4),
    title: Optional[str] = None,
) -> str:
    """Generate intensity (loudness) contour over time.

    Shows the dB envelope of the signal, useful for
    evaluating stress patterns and prosody.

    Args:
        audio: Audio array
        sample_rate: Sample rate in Hz
        filepath: Output file path
        figsize: Figure size
        title: Plot title

    Returns:
        Path to saved plot
    """
    audio = _ensure_mono(audio).astype(np.float32)

    # Compute RMS energy
    frame_length = 2048
    hop = 512
    rms = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop)[0]
    times = librosa.times_like(rms, sr=sample_rate, hop_length=hop)

    # Convert to dB
    rms_db = librosa.amplitude_to_db(rms, ref=np.max)

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    _apply_style(fig, ax)

    ax.plot(times, rms_db, color=STYLE['intensity'], linewidth=1.2, alpha=0.9)
    ax.fill_between(times, rms_db, alpha=0.2, color=STYLE['intensity'])

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Intensity (dB)')
    ax.set_title(title or 'Intensity Contour')
    ax.set_xlim([0, times[-1] if len(times) > 0 else 1])

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath


# ── 6. JITTER & SHIMMER ────────────────────────────────────────────────────

def _compute_jitter_shimmer(
    audio: np.ndarray,
    sample_rate: int,
    frame_length: int = 2048,
    hop_length: int = 512,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute jitter and shimmer from pitch-synchronous analysis."""
    # Get pitch periods
    f0, voiced_flag, _ = librosa.pyin(
        audio, fmin=60, fmax=600, sr=sample_rate,
        frame_length=frame_length, hop_length=hop_length,
    )

    times = librosa.times_like(f0, sr=sample_rate, hop_length=hop_length)

    # Jitter: cycle-to-cycle F0 variation
    jitter = np.full_like(f0, np.nan)
    shimmer = np.full_like(f0, np.nan)

    valid = ~np.isnan(f0) & voiced_flag
    if np.sum(valid) > 2:
        f0_valid = f0[valid]
        periods = 1.0 / f0_valid

        # Jitter (period perturbation)
        period_diffs = np.abs(np.diff(periods))
        jitter_vals = np.full(len(f0), np.nan)
        valid_indices = np.where(valid)[0]
        for i in range(1, len(period_diffs)):
            if periods[i] > 0:
                jitter_vals[valid_indices[i + 1]] = period_diffs[i] / periods[i]
        jitter = jitter_vals

        # Shimmer (amplitude perturbation)
        frame_start = valid_indices * hop_length
        amplitudes = []
        for idx in frame_start:
            if idx + frame_length <= len(audio):
                amplitudes.append(np.max(np.abs(audio[idx:idx + frame_length])))
            else:
                amplitudes.append(0)
        amplitudes = np.array(amplitudes)

        if len(amplitudes) > 2:
            amp_diffs = np.abs(np.diff(amplitudes))
            shimmer_vals = np.full(len(f0), np.nan)
            for i in range(1, len(amp_diffs)):
                if amplitudes[i] > 0:
                    shimmer_vals[valid_indices[i + 1]] = amp_diffs[i] / amplitudes[i]
            shimmer = shimmer_vals

    return times, jitter, shimmer


def generate_jitter_shimmer(
    audio: np.ndarray,
    sample_rate: int,
    filepath: str,
    figsize: tuple = (12, 5),
    title: Optional[str] = None,
) -> str:
    """Generate jitter and shimmer plots.

    Jitter = cycle-to-cycle F0 variation (pitch perturbation).
    Shimmer = cycle-to-cycle amplitude variation.
    Both indicate voice quality and naturalness.

    Args:
        audio: Audio array
        sample_rate: Sample rate in Hz
        filepath: Output file path
        figsize: Figure size
        title: Plot title

    Returns:
        Path to saved plot
    """
    audio = _ensure_mono(audio).astype(np.float32)

    times, jitter, shimmer = _compute_jitter_shimmer(audio, sample_rate)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, height_ratios=[1, 1],
                                    sharex=True)
    fig.patch.set_facecolor(STYLE['bg'])

    # Jitter
    _apply_style(fig, ax1)
    valid_j = ~np.isnan(jitter)
    if np.any(valid_j):
        ax1.plot(times[valid_j], jitter[valid_j] * 100, color=STYLE['jitter'],
                 linewidth=1.0, alpha=0.9)
        ax1.fill_between(times[valid_j], jitter[valid_j] * 100,
                         alpha=0.15, color=STYLE['jitter'])
    ax1.set_ylabel('Jitter (%)')
    ax1.set_title(title or 'Jitter & Shimmer')

    # Shimmer
    _apply_style(fig, ax2)
    valid_s = ~np.isnan(shimmer)
    if np.any(valid_s):
        ax2.plot(times[valid_s], shimmer[valid_s] * 100, color=STYLE['shimmer'],
                 linewidth=1.0, alpha=0.9)
        ax2.fill_between(times[valid_s], shimmer[valid_s] * 100,
                         alpha=0.15, color=STYLE['shimmer'])
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Shimmer (%)')

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath


# ── 7. HARMONIC-TO-NOISE RATIO ─────────────────────────────────────────────

def generate_hnr(
    audio: np.ndarray,
    sample_rate: int,
    filepath: str,
    frame_length: int = 2048,
    hop_length: int = 512,
    figsize: tuple = (12, 4),
    title: Optional[str] = None,
) -> str:
    """Generate Harmonic-to-Noise Ratio (HNR) contour.

    HNR measures the ratio of harmonic (voiced) energy to noise energy.
    High HNR = clear voice, low HNR = breathy/rough voice.

    Args:
        audio: Audio array
        sample_rate: Sample rate in Hz
        filepath: Output file path
        frame_length: FFT window size
        hop_length: Hop size
        figsize: Figure size
        title: Plot title

    Returns:
        Path to saved plot
    """
    audio = _ensure_mono(audio).astype(np.float32)

    # Autocorrelation-based HNR estimation
    n_frames = 1 + (len(audio) - frame_length) // hop_length
    times = []
    hnr_values = []

    for i in range(n_frames):
        start = i * hop_length
        frame = audio[start:start + frame_length]
        if len(frame) < frame_length:
            break

        windowed = frame * np.hamming(len(frame))

        # Autocorrelation
        fft_size = 1
        while fft_size < 2 * len(windowed):
            fft_size *= 2
        fft_audio = np.fft.rfft(windowed, n=fft_size)
        acf = np.fft.irfft(fft_audio * np.conj(fft_audio))[:len(windowed)]

        if acf[0] > 0:
            acf = acf / acf[0]

        # Find peak in pitch range (60-600 Hz)
        min_lag = int(sample_rate / 600)
        max_lag = min(int(sample_rate / 60), len(acf) - 1)

        if max_lag > min_lag:
            peak = np.max(acf[min_lag:max_lag])
            if peak > 0:
                # HNR approximation from autocorrelation peak
                hnr = 10 * np.log10(peak / (1 - peak + 1e-10))
            else:
                hnr = -20
        else:
            hnr = -20

        times.append((start + frame_length / 2) / sample_rate)
        hnr_values.append(hnr)

    times = np.array(times)
    hnr_values = np.array(hnr_values)

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    _apply_style(fig, ax)

    ax.plot(times, hnr_values, color=STYLE['hnr'], linewidth=1.2, alpha=0.9)
    ax.fill_between(times, hnr_values, alpha=0.15, color=STYLE['hnr'])
    ax.axhline(y=0, color=STYLE['text_dim'], linewidth=0.5, linestyle='--')

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('HNR (dB)')
    ax.set_title(title or 'Harmonic-to-Noise Ratio')
    ax.set_xlim([0, times[-1] if len(times) > 0 else 1])

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath
