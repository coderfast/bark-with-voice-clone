# AGENTS.md — Voice Filter

## Project Overview

Voice Filter es una aplicación de procesamiento de audio con interfaz gráfica que permite cargar archivos de audio y modificarlos en tiempo real con más de 20 efectos de audio.

**Propósito:** Modificar, distorsionar y mejorar archivos de audio de forma visual e interactiva.

## Project Structure

```
app_voice_filter/
├── voice_filter.py              # Entry point
├── config/
│   ├── __init__.py
│   └── colors.py                # Diccionario COLORS
├── audio/
│   ├── __init__.py
│   └── processor.py             # AudioProcessor (carga, efectos, reproduccion)
├── widgets/
│   ├── __init__.py
│   ├── mixer_fader.py           # MixerFader (fader custom con LED meter)
│   └── vu_meter.py              # AnalogVUMeter (VU meter analogico)
├── gui/
│   ├── __init__.py
│   ├── app.py                   # VoiceFilterGUI (clase principal)
│   └── tabs.py                  # Funciones de creacion de pestanas
├── requirements.txt
├── APP_ARCHITECTURE.md
├── APP_TECHNICALSTACK.md
├── ROADMAP.md
└── AGENTS.md
```

## Key Architecture

### Clases Principales

#### AudioProcessor
```python
class AudioProcessor:
    """Maneja carga, procesamiento y reproducción de audio."""
    
    # Métodos principales:
    load_audio(filepath) -> bool
    save_audio(filepath, audio_data) -> bool
    play_audio(audio, callback) -> None
    stop_playback() -> None
    apply_process_all(params) -> np.ndarray
    
    # Efectos disponibles:
    apply_volume(audio, volume) -> np.ndarray
    apply_pitch(audio, pitch_shift) -> np.ndarray
    apply_speed(audio, speed) -> np.ndarray
    apply_eq_band(audio, freq, gain) -> np.ndarray
    apply_low_pass(audio, cutoff) -> np.ndarray
    apply_high_pass(audio, cutoff) -> np.ndarray
    apply_chorus(audio, depth, rate) -> np.ndarray
    apply_flanger(audio, depth, rate) -> np.ndarray
    apply_phaser(audio, depth, rate) -> np.ndarray
    apply_tremolo(audio, depth, rate) -> np.ndarray
    apply_vibrato(audio, depth, rate) -> np.ndarray
    apply_distortion(audio, amount) -> np.ndarray
    apply_bitcrusher(audio, bits) -> np.ndarray
    apply_overdrive(audio, gain) -> np.ndarray
    apply_reverb(audio, amount) -> np.ndarray
    apply_delay(audio, delay_ms, feedback) -> np.ndarray
    apply_compression(audio, threshold, ratio) -> np.ndarray
    apply_gate(audio, threshold) -> np.ndarray
    apply_fade_in(audio, duration_ms) -> np.ndarray
    apply_fade_out(audio, duration_ms) -> np.ndarray
    apply_normalize(audio, target_db) -> np.ndarray
    apply_trim(audio, start, end) -> np.ndarray
    apply_reverse(audio) -> np.ndarray
```

#### VoiceFilterGUI
```python
class VoiceFilterGUI:
    """Interfaz gráfica de usuario."""

    # Métodos principales:
    _create_transport(parent) -> None
    _create_waveform(parent) -> None
    _create_params_notebook(parent) -> None
    _create_slider(parent, row, label, variable, from_, to, unit, color) -> MixerFader
    _create_basic_tab(parent) -> None       # 3 faders (grid 3 columnas iguales)
    _create_eq_tab(parent) -> None
    _open_audio() -> None
    _save_modified() -> None
    _play_original() -> None
    _play_modified() -> None
    _stop_audio() -> None
    _start_animation() -> None
    _stop_animation() -> None
    _animate_meters() -> None               # Actualiza VU meter y fader levels durante reproducción
    _reset_all() -> None
    _draw_original_waveform() -> None
    _draw_modified_waveform() -> None
```

#### AnalogVUMeter
```python
class AnalogVUMeter(tk.Canvas):
    """VU meter analógico con física de rebote de aguja."""

    # Atributos de escala:
    _db_min: int    # -20 dB (posición 0.0 del needle)
    _db_max: int    # +3 dB (posición 1.0 del needle)

    # Métodos:
    set_level(level: float) -> None    # level: 0.0 (-20 dB) a 1.0 (+3 dB)
    _animate_needle() -> None          # Física de resorte con attack/decay
    _draw() -> None                    # Dibuja arco, ticks, labels, aguja
```

#### MixerFader
```python
class MixerFader(tk.Canvas):
    """Fader estilo mixer con medidor LED."""

    # Métodos:
    set_audio_level(level: float) -> None    # Para animación del medidor LED
    set_value(value: float) -> None
```

## Key Files to Modify

| Task | File | Function |
|------|------|----------|
| Add new effect | `audio/processor.py` | `AudioProcessor.apply_*()` |
| Modify UI layout | `gui/app.py` | `VoiceFilterGUI._create_*()` |
| Change color scheme | `config/colors.py` | `COLORS` dict |
| Add new parameter | `gui/app.py` | `_create_variables()` |
| Add new tab slider | `gui/tabs.py` | `create_slider()` + `create_*_tab()` |
| Modify auto-preview | `gui/app.py` | `_on_slider_release()` |
| Change audio formats | `audio/processor.py` | `AudioProcessor.load_audio()` |

## Conventions

### Código

- **Type hints** en todos los métodos públicos
- **Docstrings** para todas las funciones
- **Naming**: snake_case para funciones y variables
- **Imports**: stdlib primero, luego third-party, luego locales

### Efectos de Audio

- Retornar `audio` sin modificar si el parámetro es neutro
- Ejemplo: `if volume == 1.0: return audio`
- Usar `np.clip()` para evitar distorsión no intencional

### Threading

- Usar `threading.Lock` para proteger `is_playing`
- Hilos con `daemon=True` para cierre limpio
- Callbacks para notificar completion a la UI

### UI

- Colores codificados por categoría
- Sliders con `<ButtonPress-1>` para cortar audio
- Sliders con `<ButtonRelease-1>` para auto-preview
- Widgets ttk para apariencia nativa

## Dependencies

```
numpy>=1.24.0
scipy>=1.10.0
soundfile>=0.12.0
sounddevice>=0.4.6
tkinter (incluido con Python)
```

## Running the App

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python voice_filter.py
```

## Common Tasks

### Adding a New Effect

1. Agregar método en `AudioProcessor` (`audio/processor.py`):
```python
def apply_new_effect(self, audio: np.ndarray, param: float) -> np.ndarray:
    """Apply new effect."""
    if param == 0:  # Skip if neutral
        return audio
    # Process audio
    return processed_audio
```

2. Agregar variable en `_create_variables()` (`gui/app.py`):
```python
self.new_effect_var = tk.DoubleVar(value=0.0)
```

3. Agregar slider en tab correspondiente (`gui/tabs.py`):
```python
create_slider(gui, inner, row, "New Effect:", gui.new_effect_var, 0, 1, "", COLORS['category'])
```

4. Agregar en `apply_process_all()` (`audio/processor.py`):
```python
new_effect = params.get('new_effect', 0)
if new_effect != 0:
    audio = self.apply_new_effect(audio, new_effect)
```

5. Agregar en `_get_params()` (`gui/app.py`):
```python
'new_effect': self.new_effect_var.get(),
```

6. Agregar en `_reset_all()` (`gui/app.py`):
```python
self.new_effect_var.set(0.0)
```

### Modifying Auto-Preview

El auto-preview se activa al soltar un slider:

```python
# En gui/tabs.py → create_slider():
on_release=lambda: gui._on_slider_release()

# En gui/app.py → _on_slider_release():
def _on_slider_release(self) -> None:
    self._draw_modified_waveform()
    if self.auto_preview_var.get():
        self._play_modified()
```

### Changing Colors

Modificar el diccionario `COLORS` en `config/colors.py`:

```python
COLORS = {
    'bg': '#2b2b2b',        # Fondo
    'fg': '#ffffff',        # Texto
    'accent': '#4a9eff',    # Acento
    'success': '#4caf50',   # Original waveform
    'warning': '#ff9800',   # Modified waveform
    'basic': '#3d5afe',     # Basic tab
    'eq': '#00bcd4',        # EQ tab
    'modulation': '#9c27b0', # Modulation tab
    'distortion': '#ff5722', # Distortion tab
    'time': '#ff9800',      # Time tab
    'dynamics': '#4caf50',  # Dynamics tab
    'utility': '#607d8b',   # Utility tab
}
```

## Notes

- La aplicación es cross-platform (Windows, Linux, macOS)
- El audio se procesa en el hilo principal (no GPU)
- La reproducción usa hilos separados para no bloquear la UI
- El waveform modificado se actualiza al soltar cualquier slider
- Los efectos se aplican en orden: Basic → EQ → Filters → Modulation → Distortion → Time → Dynamics → Utility
- Los spectrogramas se muestran debajo de cada waveform (original y modificado) usando `scipy.signal.spectrogram`
- El colormap del spectrograma va de negro (silencio) → azul → verde → amarillo → rojo (más fuerte)
