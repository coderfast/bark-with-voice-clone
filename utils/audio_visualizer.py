"""
Audio Visualization Utilities

Generates 4 visualization plots for audio:
- Waveform (_wave.png)      — Time domain: amplitude vs time
- Pitch (_pitch.png)        — F0 tracking via autocorrelation (fundamental frequency)
- Sweep (_sweep.png)        — Spectral centroid trajectory (brightness)
- Spectrogram (_specgram.png) — Full frequency content over time
"""

import os
from typing import Optional

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import signal

# ── Dark theme ──────────────────────────────────────────────────────────────
STYLE = {
    'bg': '#0e1117',
    'panel': '#161b22',
    'grid': '#21262d',
    'text': '#c9d1d9',
    'text_dim': '#8b949e',
    'wave': '#58a6ff',
    'wave_fill': '#1f6feb',
    'pitch': '#3fb950',
    'sweep': '#f0883e',
    'spec_low': '#0d1117',
    'spec_high': '#f0883e',
}


def _apply_style(fig, ax):
    """Apply dark theme to figure."""
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
    """Convert stereo to mono if needed."""
    if audio.ndim > 1:
        return np.mean(audio, axis=0)
    return audio


def _safe_nperseg(audio_len: int, nperseg: int) -> int:
    """Ensure nperseg is valid for the audio length."""
    nperseg = min(nperseg, audio_len // 4)
    return max(nperseg, 64)


# ── 1. WAVEFORM ────────────────────────────────────────────────────────────

def generate_waveform(
    audio: np.ndarray,
    sample_rate: int,
    filepath: str,
    figsize: tuple = (12, 4),
    title: Optional[str] = None,
) -> str:
    """Generate waveform plot (amplitude vs time).

    Shows the raw audio signal with envelope fill. Useful for:
    - Identifying silence, transients, dynamic range
    - Spotting clipping (flat tops at ±1.0)
    - Seeing attack/decay patterns

    Args:
        audio: Audio array (1D mono or 2D stereo)
        sample_rate: Sample rate in Hz
        filepath: Output file path (.png)
        figsize: Figure size (width, height)
        title: Plot title

    Returns:
        Path to saved plot
    """
    audio = _ensure_mono(audio)
    time = np.arange(len(audio)) / sample_rate

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    _apply_style(fig, ax)

    # Plot line + fill
    ax.plot(time, audio, color=STYLE['wave'], linewidth=0.4, alpha=0.9)
    ax.fill_between(time, audio, alpha=0.25, color=STYLE['wave_fill'])

    # Zero line
    ax.axhline(y=0, color=STYLE['text_dim'], linewidth=0.5, alpha=0.5)

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Amplitude')
    ax.set_title(title or 'Waveform')
    ax.set_xlim([0, time[-1] if len(time) > 0 else 1])
    ax.set_ylim([-1.15, 1.15])

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath


# ── 2. PITCH (F0 via autocorrelation) ──────────────────────────────────────

def _estimate_f0_autocorr(
    audio: np.ndarray,
    sample_rate: int,
    frame_length: int = 2048,
    hop_length: int = 512,
    f_min: float = 60.0,
    f_max: float = 600.0,
) -> tuple:
    """Estimate F0 (fundamental frequency) using autocorrelation.

    Returns:
        (times, f0_hz) arrays
    """
    n_frames = 1 + (len(audio) - frame_length) // hop_length
    if n_frames < 1:
        return np.array([0]), np.array([np.nan])

    min_lag = int(sample_rate / f_max)
    max_lag = int(sample_rate / f_min)
    max_lag = min(max_lag, frame_length - 1)

    times = []
    f0_values = []

    for i in range(n_frames):
        start = i * hop_length
        frame = audio[start:start + frame_length]

        # Apply Hamming window
        windowed = frame * np.hamming(len(frame))

        # Autocorrelation via FFT
        fft_size = 1
        while fft_size < 2 * len(windowed):
            fft_size *= 2
        fft_audio = np.fft.rfft(windowed, n=fft_size)
        acf = np.fft.irfft(fft_audio * np.conj(fft_audio))[:len(windowed)]

        # Normalize
        if acf[0] > 0:
            acf = acf / acf[0]

        # Find peak in valid lag range
        if min_lag < max_lag and max_lag <= len(acf):
            search = acf[min_lag:max_lag]
            if len(search) > 0 and np.max(search) > 0.3:
                peak_lag = min_lag + np.argmax(search)
                f0 = sample_rate / peak_lag
            else:
                f0 = np.nan
        else:
            f0 = np.nan

        t_center = (start + frame_length / 2) / sample_rate
        times.append(t_center)
        f0_values.append(f0)

    # Median filter to smooth F0
    f0_arr = np.array(f0_values)
    from scipy.ndimage import median_filter
    mask = ~np.isnan(f0_arr)
    if np.sum(mask) > 3:
        f0_filled = f0_arr.copy()
        f0_filled[~mask] = np.nan
        # Smooth only valid values
        valid = f0_arr[mask]
        if len(valid) > 3:
            smoothed = median_filter(valid, size=5)
            f0_arr[mask] = smoothed

    return np.array(times), f0_arr


def generate_pitch(
    audio: np.ndarray,
    sample_rate: int,
    filepath: str,
    frame_length: int = 2048,
    hop_length: int = 512,
    figsize: tuple = (12, 4),
    title: Optional[str] = None,
) -> str:
    """Generate pitch (F0) tracking plot.

    Shows the fundamental frequency over time using autocorrelation.
    This represents the perceived "note" or intonation in speech.

    Useful for:
    - Analyzing speech intonation (rising/falling pitch)
    - Musical note detection
    - Voice quality assessment (jitter, pitch range)

    Args:
        audio: Audio array (1D mono or 2D stereo)
        sample_rate: Sample rate in Hz
        filepath: Output file path (.png)
        frame_length: FFT window size
        hop_length: Hop size between frames
        figsize: Figure size (width, height)
        title: Plot title

    Returns:
        Path to saved plot
    """
    audio = _ensure_mono(audio)

    times, f0 = _estimate_f0_autocorr(
        audio, sample_rate, frame_length, hop_length
    )

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    _apply_style(fig, ax)

    # Plot F0 curve
    valid = ~np.isnan(f0)
    if np.any(valid):
        ax.plot(times[valid], f0[valid], color=STYLE['pitch'], linewidth=1.5,
                alpha=0.9, label='F0')
        ax.fill_between(times[valid], f0[valid], alpha=0.15, color=STYLE['pitch'])

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Frequency (Hz)')
    ax.set_title(title or 'Pitch (F0 - Fundamental Frequency)')
    ax.set_xlim([0, times[-1] if len(times) > 0 else 1])
    ax.set_ylim([50, 600])
    ax.set_yscale('log')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}'))

    # Reference lines for common pitch ranges
    for hz, label in [(100, '100 Hz'), (200, '200 Hz'), (400, '400 Hz')]:
        ax.axhline(y=hz, color=STYLE['text_dim'], linewidth=0.5, alpha=0.3,
                   linestyle='--')

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath


# ── 3. SWEEP (Spectral Centroid) ───────────────────────────────────────────

def generate_sweep(
    audio: np.ndarray,
    sample_rate: int,
    filepath: str,
    nperseg: int = 1024,
    figsize: tuple = (12, 4),
    title: Optional[str] = None,
) -> str:
    """Generate spectral centroid plot (brightness trajectory).

    The spectral centroid is the "center of mass" of the spectrum.
    It indicates the perceived brightness of the sound.

    Useful for:
    - Tracking timbral changes over time
    - Detecting frequency sweeps (chirps, glissando)
    - Analyzing formant movement in speech
    - Comparing bright vs dark sounds

    Args:
        audio: Audio array (1D mono or 2D stereo)
        sample_rate: Sample rate in Hz
        filepath: Output file path (.png)
        nperseg: Window size for STFT
        figsize: Figure size (width, height)
        title: Plot title

    Returns:
        Path to saved plot
    """
    audio = _ensure_mono(audio)
    nperseg = _safe_nperseg(len(audio), nperseg)

    f, t, Sxx = signal.spectrogram(
        audio, fs=sample_rate, nperseg=nperseg, noverlap=nperseg // 2,
    )

    # Spectral centroid = sum(f * Sxx) / sum(Sxx) per frame
    Sxx_power = Sxx ** 2
    sum_power = np.sum(Sxx_power, axis=0)
    sum_power = np.where(sum_power > 0, sum_power, 1e-10)
    centroid = np.sum(f[:, np.newaxis] * Sxx_power, axis=0) / sum_power

    # Spectral bandwidth for shaded region
    freq_diff = (f[:, np.newaxis] - centroid[np.newaxis, :]) ** 2
    bandwidth = np.sqrt(np.sum(freq_diff * Sxx_power, axis=0) / sum_power)

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    _apply_style(fig, ax)

    # Plot centroid + bandwidth fill
    ax.plot(t, centroid, color=STYLE['sweep'], linewidth=1.5, alpha=0.9,
            label='Spectral Centroid')
    ax.fill_between(t,
                     np.maximum(centroid - bandwidth, 0),
                     centroid + bandwidth,
                     alpha=0.15, color=STYLE['sweep'], label='Bandwidth')

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Frequency (Hz)')
    ax.set_title(title or 'Frequency Sweep (Spectral Centroid)')
    ax.set_xlim([0, t[-1] if len(t) > 0 else 1])
    ax.set_ylim([0, sample_rate / 3])
    ax.legend(loc='upper right', fontsize=8,
              facecolor=STYLE['panel'], edgecolor=STYLE['grid'],
              labelcolor=STYLE['text'])

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath


# ── 4. SPECTROGRAM ─────────────────────────────────────────────────────────

def generate_spectrogram(
    audio: np.ndarray,
    sample_rate: int,
    filepath: str,
    nperseg: int = 1024,
    figsize: tuple = (12, 4),
    title: Optional[str] = None,
) -> str:
    """Generate spectrogram plot (frequency content over time).

    Shows all frequency components simultaneously as a heat map.
    Brighter/warmer colors = more energy at that frequency/time.

    Useful for:
    - Complete spectral analysis
    - Identifying harmonics, formants, noise
    - Comparing original vs processed audio
    - Detecting frequency-specific artifacts

    Args:
        audio: Audio array (1D mono or 2D stereo)
        sample_rate: Sample rate in Hz
        filepath: Output file path (.png)
        nperseg: FFT window size
        figsize: Figure size (width, height)
        title: Plot title

    Returns:
        Path to saved plot
    """
    audio = _ensure_mono(audio)
    nperseg = _safe_nperseg(len(audio), nperseg)

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    _apply_style(fig, ax)

    # Custom colormap: dark blue → orange → white
    from matplotlib.colors import LinearSegmentedColormap
    colors_list = ['#0d1117', '#1a1e2e', '#1f6feb', '#58a6ff',
                   '#f0883e', '#ffa657', '#ffffff']
    cmap = LinearSegmentedColormap.from_list('audio_spec', colors_list, N=256)

    Sxx = ax.specgram(
        audio, NFFT=nperseg, Fs=sample_rate,
        noverlap=nperseg // 2, cmap=cmap,
        scale='dB', vmin=-80, vmax=0,
    )

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Frequency (Hz)')
    ax.set_title(title or 'Spectrogram')
    ax.set_ylim([0, sample_rate / 2])

    # Colorbar
    cbar = plt.colorbar(Sxx[3], ax=ax, label='Intensity (dB)')
    cbar.ax.yaxis.label.set_color(STYLE['text'])
    cbar.ax.tick_params(colors=STYLE['text_dim'])

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath


# ── 5. SPECTRAL FLATNESS ───────────────────────────────────────────────────

def generate_spectral_flatness(
    audio: np.ndarray,
    sample_rate: int,
    filepath: str,
    nperseg: int = 1024,
    figsize: tuple = (12, 4),
    title: Optional[str] = None,
) -> str:
    """Generate spectral flatness plot.

    Spectral flatness = geometric mean / arithmetic mean of spectrum.
    0 = pure tone, 1 = white noise. Useful for voiced/unvoiced detection.

    Args:
        audio: Audio array
        sample_rate: Sample rate in Hz
        filepath: Output file path
        nperseg: Window size
        figsize: Figure size
        title: Plot title

    Returns:
        Path to saved plot
    """
    import librosa
    audio = _ensure_mono(audio).astype(np.float32)
    nperseg = _safe_nperseg(len(audio), nperseg)

    flatness = librosa.feature.spectral_flatness(
        y=audio, n_fft=nperseg, hop_length=nperseg // 2,
    )[0]
    times = librosa.times_like(flatness, sr=sample_rate, hop_length=nperseg // 2)

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    _apply_style(fig, ax)

    ax.plot(times, flatness, color=STYLE['sweep'], linewidth=1.0, alpha=0.9)
    ax.fill_between(times, flatness, alpha=0.2, color=STYLE['sweep'])

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Flatness')
    ax.set_title(title or 'Spectral Flatness (0=Tone, 1=Noise)')
    ax.set_xlim([0, times[-1] if len(times) > 0 else 1])
    ax.set_ylim([0, 1.05])

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath


# ── 6. ZERO CROSSING RATE ──────────────────────────────────────────────────

def generate_zero_crossing_rate(
    audio: np.ndarray,
    sample_rate: int,
    filepath: str,
    figsize: tuple = (12, 4),
    title: Optional[str] = None,
) -> str:
    """Generate zero-crossing rate plot.

    ZCR = rate at which signal changes sign per frame.
    High ZCR = unvoiced fricatives (s, f, sh).
    Low ZCR = voiced vowels.

    Args:
        audio: Audio array
        sample_rate: Sample rate in Hz
        filepath: Output file path
        figsize: Figure size
        title: Plot title

    Returns:
        Path to saved plot
    """
    import librosa
    audio = _ensure_mono(audio).astype(np.float32)

    zcr = librosa.feature.zero_crossing_rate(audio, frame_length=2048, hop_length=512)[0]
    times = librosa.times_like(zcr, sr=sample_rate, hop_length=512)

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    _apply_style(fig, ax)

    ax.plot(times, zcr, color=STYLE['wave'], linewidth=1.0, alpha=0.9)
    ax.fill_between(times, zcr, alpha=0.2, color=STYLE['wave_fill'])

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('ZCR')
    ax.set_title(title or 'Zero Crossing Rate')
    ax.set_xlim([0, times[-1] if len(times) > 0 else 1])

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath


# ── 7. CQT SPECTROGRAM ────────────────────────────────────────────────────

def generate_cqt_spectrogram(
    audio: np.ndarray,
    sample_rate: int,
    filepath: str,
    figsize: tuple = (12, 4),
    title: Optional[str] = None,
) -> str:
    """Generate Constant-Q Transform spectrogram.

    CQT uses logarithmically spaced frequency bins (like musical notes).
    Better than STFT for speech because human hearing is logarithmic.

    Args:
        audio: Audio array
        sample_rate: Sample rate in Hz
        filepath: Output file path
        figsize: Figure size
        title: Plot title

    Returns:
        Path to saved plot
    """
    import librosa
    audio = _ensure_mono(audio).astype(np.float32)

    C = np.abs(librosa.cqt(audio, sr=sample_rate, hop_length=512, n_bins=84))
    C_db = librosa.amplitude_to_db(C, ref=np.max)
    times = librosa.times_like(C, sr=sample_rate, hop_length=512)

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    _apply_style(fig, ax)

    img = librosa.display.specshow(
        C_db, sr=sample_rate, x_axis='time', y_axis='cqt_note',
        ax=ax, cmap='magma', vmin=-80, vmax=0,
    )

    ax.set_title(title or 'CQT Spectrogram')
    cbar = fig.colorbar(img, ax=ax, format='%+2.0f dB')
    cbar.ax.yaxis.label.set_color(STYLE['text'])
    cbar.ax.tick_params(colors=STYLE['text_dim'])

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath


# ── 8. CHROMAGRAM ──────────────────────────────────────────────────────────

def generate_chromagram(
    audio: np.ndarray,
    sample_rate: int,
    filepath: str,
    figsize: tuple = (12, 4),
    title: Optional[str] = None,
) -> str:
    """Generate chromagram (pitch class distribution).

    Maps audio to 12 pitch classes (C, C#, D, ..., B).
    Useful for harmonic and prosodic pattern analysis.

    Args:
        audio: Audio array
        sample_rate: Sample rate in Hz
        filepath: Output file path
        figsize: Figure size
        title: Plot title

    Returns:
        Path to saved plot
    """
    import librosa
    audio = _ensure_mono(audio).astype(np.float32)

    chroma = librosa.feature.chroma_cqt(y=audio, sr=sample_rate, hop_length=512)

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    _apply_style(fig, ax)

    img = librosa.display.specshow(
        chroma, sr=sample_rate, x_axis='time', y_axis='chroma',
        ax=ax, cmap='coolwarm',
    )

    ax.set_title(title or 'Chromagram')
    cbar = fig.colorbar(img, ax=ax)
    cbar.ax.yaxis.label.set_color(STYLE['text'])
    cbar.ax.tick_params(colors=STYLE['text_dim'])

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath


# ── 9. SELF-SIMILARITY MATRIX ─────────────────────────────────────────────

def generate_self_similarity(
    audio: np.ndarray,
    sample_rate: int,
    filepath: str,
    figsize: tuple = (10, 8),
    title: Optional[str] = None,
) -> str:
    """Generate self-similarity (recurrence) matrix.

    A square matrix showing time-vs-time similarity of audio features.
    Diagonal lines indicate repeated patterns.

    Args:
        audio: Audio array
        sample_rate: Sample rate in Hz
        filepath: Output file path
        figsize: Figure size
        title: Plot title

    Returns:
        Path to saved plot
    """
    import librosa
    audio = _ensure_mono(audio).astype(np.float32)

    # Compute MFCC features
    mfcc = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=13)
    # Self-similarity via cosine distance
    sim = librosa.segment.recurrence_matrix(mfcc, mode='affinity', metric='cosine')

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    fig.patch.set_facecolor(STYLE['bg'])
    ax.set_facecolor(STYLE['panel'])

    ax.imshow(sim, cmap='inferno', aspect='auto', origin='lower')

    ax.set_xlabel('Time Frame')
    ax.set_ylabel('Time Frame')
    ax.set_title(title or 'Self-Similarity Matrix')

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath


# ── 10. LPC SPECTRUM ──────────────────────────────────────────────────────

def generate_lpc_spectrum(
    audio: np.ndarray,
    sample_rate: int,
    filepath: str,
    n_frames: int = 5,
    figsize: tuple = (12, 4),
    title: Optional[str] = None,
) -> str:
    """Generate LPC (Linear Predictive Coding) spectral envelope.

    Shows the smoothed spectral envelope at selected time frames.
    Useful for formant analysis and spectral shape comparison.

    Args:
        audio: Audio array
        sample_rate: Sample rate in Hz
        filepath: Output file path
        n_frames: Number of frames to show
        figsize: Figure size
        title: Plot title

    Returns:
        Path to saved plot
    """
    from scipy.signal import lfilter, freqz
    audio = _ensure_mono(audio).astype(np.float32)

    frame_length = min(2048, len(audio) // 4)
    hop = (len(audio) - frame_length) // max(n_frames, 1)
    lpc_order = 2 + sample_rate // 1000

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    _apply_style(fig, ax)

    colors = ['#ff7b72', '#ffa657', '#d2a8ff', '#79c0ff', '#3fb950']

    for i in range(min(n_frames, len(audio) // frame_length)):
        start = i * hop
        frame = audio[start:start + frame_length]
        if len(frame) < frame_length:
            break

        windowed = frame * np.hamming(len(frame))

        # LPC analysis
        try:
            # Autocorrelation method
            r = np.correlate(windowed, windowed, mode='full')
            r = r[len(r) // 2:][:lpc_order + 1]

            # Levinson-Durbin
            a = np.zeros(lpc_order + 1)
            a[0] = 1.0
            e = r[0]
            for j in range(1, lpc_order + 1):
                lam = 0
                for k in range(j):
                    lam += a[k] * r[j - k]
                lam = -lam / e if e > 0 else 0
                a_new = np.zeros(lpc_order + 1)
                a_new[:j + 1] = a[:j + 1]
                a_new[j] = lam
                for k in range(j):
                    a_new[k] = a[k] + lam * a[j - k]
                a = a_new
                e *= (1 - lam ** 2)
                if e <= 0:
                    break

            # Frequency response
            w, h = freqz(1, a, worN=512, fs=sample_rate)
            spectrum_db = 20 * np.log10(np.abs(h) + 1e-10)

            t_label = (start + frame_length / 2) / sample_rate
            ax.plot(w, spectrum_db, color=colors[i % len(colors)],
                    linewidth=1.2, alpha=0.8, label=f't={t_label:.2f}s')
        except Exception:
            continue

    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Magnitude (dB)')
    ax.set_title(title or 'LPC Spectral Envelope')
    ax.legend(fontsize=8, facecolor=STYLE['panel'], edgecolor=STYLE['grid'],
              labelcolor=STYLE['text'])
    ax.set_xlim([0, sample_rate / 2])

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath


# ── 11. WIDEBAND/NARROWBAND SPECTROGRAM ───────────────────────────────────

def generate_spectrogram_wide_narrow(
    audio: np.ndarray,
    sample_rate: int,
    filepath: str,
    figsize: tuple = (12, 6),
    title: Optional[str] = None,
) -> str:
    """Generate side-by-side wideband and narrowband spectrograms.

    Wideband: high temporal resolution, shows individual glottal pulses.
    Narrowband: high frequency resolution, shows individual harmonics.

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

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)
    fig.patch.set_facecolor(STYLE['bg'])

    from matplotlib.colors import LinearSegmentedColormap
    colors_list = ['#0d1117', '#1a1e2e', '#1f6feb', '#58a6ff',
                   '#f0883e', '#ffa657', '#ffffff']
    cmap = LinearSegmentedColormap.from_list('audio_spec', colors_list, N=256)

    # Wideband (short window = good time resolution)
    _apply_style(fig, ax1)
    ax1.specgram(audio, NFFT=256, Fs=sample_rate, noverlap=128, cmap=cmap)
    ax1.set_title('Wideband Spectrogram (temporal detail)')
    ax1.set_ylabel('Frequency (Hz)')

    # Narrowband (long window = good frequency resolution)
    _apply_style(fig, ax2)
    ax2.specgram(audio, NFFT=4096, Fs=sample_rate, noverlap=3072, cmap=cmap)
    ax2.set_title('Narrowband Spectrogram (harmonic detail)')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Frequency (Hz)')

    if title:
        fig.suptitle(title, color=STYLE['text'], fontsize=12)

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=STYLE['bg'])
    plt.close(fig)
    return filepath


# ── GENERATE ALL ────────────────────────────────────────────────────────────

def generate_all_visualizations(
    audio: np.ndarray,
    sample_rate: int,
    output_path: str,
    prefix: Optional[str] = None,
    generate_wave: bool = True,
    generate_pitch_plot: bool = True,
    generate_sweep_plot: bool = True,
    generate_specgram: bool = True,
) -> dict:
    """Generate all 4 audio visualizations.

    Args:
        audio: Audio array (1D for mono, 2D for stereo)
        sample_rate: Sample rate in Hz
        output_path: Output directory for plots
        prefix: Filename prefix
        generate_wave: Generate waveform plot
        generate_pitch_plot: Generate pitch plot
        generate_sweep_plot: Generate sweep plot
        generate_specgram: Generate spectrogram plot

    Returns:
        Dictionary mapping plot type to file path
    """
    audio_mono = _ensure_mono(audio)
    os.makedirs(output_path, exist_ok=True)
    results = {}

    if generate_wave:
        p = os.path.join(output_path, f"{prefix}_wave.png")
        generate_waveform(audio_mono, sample_rate, p)
        results['wave'] = p

    if generate_pitch_plot:
        p = os.path.join(output_path, f"{prefix}_pitch.png")
        generate_pitch(audio_mono, sample_rate, p)
        results['pitch'] = p

    if generate_sweep_plot:
        p = os.path.join(output_path, f"{prefix}_sweep.png")
        generate_sweep(audio_mono, sample_rate, p)
        results['sweep'] = p

    if generate_specgram:
        p = os.path.join(output_path, f"{prefix}_specgram.png")
        generate_spectrogram(audio_mono, sample_rate, p)
        results['specgram'] = p

    return results
