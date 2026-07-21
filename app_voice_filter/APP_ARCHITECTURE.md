# APP_ARCHITECTURE.md — Voice Filter

## Overview

Voice Filter es una aplicación de procesamiento de audio con interfaz gráfica que permite cargar archivos de audio y modificarlos en tiempo real con más de 20 efectos.

## Estructura del Proyecto

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
└── ROADMAP.md
```

## Arquitectura de la Aplicación

### Componentes Principales

```
+--------------------------------------------------+
|                    VoiceFilterGUI                  |
|  (Interfaz gráfica con tkinter)                   |
+--------------------------------------------------+
         |                    |
         v                    v
+------------------+  +------------------+
| AudioProcessor   |  |   UI Controls    |
| (Procesamiento)  |  | (Sliders, etc.)  |
+------------------+  +------------------+
         |
         v
+--------------------------------------------------+
|              Audio Effects Pipeline               |
|  Volume → Pitch → Speed → EQ → Filters → ...    |
+--------------------------------------------------+
         |
         v
+--------------------------------------------------+
|              SoundDevice / SoundFile              |
|          (Reproducción / Guardado)                |
+--------------------------------------------------+
```

### Clases Principales

#### 1. AudioProcessor
Maneja todo el procesamiento de audio.

**Responsabilidades:**
- Cargar archivos de audio (WAV, MP3, AAC, etc.)
- Guardar archivos de audio
- Aplicar efectos de audio
- Controlar reproducción

**Métodos principales:**
| Método | Descripción |
|--------|-------------|
| `load_audio()` | Carga archivo de audio |
| `save_audio()` | Guarda archivo de audio |
| `play_audio()` | Reproduce audio en hilo separado |
| `stop_playback()` | Detiene reproducción |
| `apply_process_all()` | Aplica todos los efectos |

#### 2. VoiceFilterGUI
Interfaz gráfica de usuario.

**Responsabilidades:**
- Mostrar controles de audio
- Actualizar visualización de onda
- Manejar eventos de usuario
- Coordinar reproducción

### Pipeline de Procesamiento

```
Audio Original
    │
    ├──→ Volume (0.0 - 2.0)
    ├──→ Speed (0.5x - 2.0x)
    ├──→ Pitch (-12 - +12 st)
    ├──→ EQ (5 bandas)
    ├──→ Low Pass Filter
    ├──→ High Pass Filter
    ├──→ Chorus / Flanger / Phaser
    ├──→ Tremolo / Vibrato
    ├──→ Distortion / Bitcrusher / Overdrive
    ├──→ Reverb / Delay
    ├──→ Compression / Gate
    ├──→ Fade In / Fade Out
    ├──→ Normalize
    ├──→ Trim
    ├──→ Reverse
    │
    ▼
Audio Modificado
```

### Estructura de la Interfaz

```
+--------------------------------------------------+
|  Menu: File | Edit | Help                        |
+--------------------------------------------------+
|  Transport:                                       |
|  [Open] [Play Original] [Play Modified]          |
|  [Stop] [Save] [Reset] [Exit]                    |
|  [✓ Auto-Preview]                                |
+--------------------------------------------------+
|  Waveform:                                        |
|  Original: [=======~~~~======] (verde)           |
|  Modified: [==~~====~~====~~==] (naranja)         |
+--------------------------------------------------+
|  [Basic] [EQ] [Filters] [Modulation] ...         |
|  +----------------------------------------------+|
|  |  Tab Basic (4 columnas de igual ancho):      ||
|  |  +--------+--------+--------+--------+       ||
|  |  |   VU   |  VOL   | PITCH  | SPEED  |       ||
|  |  | Meter  |  Fader | Fader  | Fader  |       ||
|  |  | [-20   | 0.0%   | 0.0 st | 1.0x   |       ||
|  |  |  to    |        |        |        |       ||
|  |  |  +3]   |        |        |        |       ||
|  |  +--------+--------+--------+--------+       ||
|  +----------------------------------------------+|
+--------------------------------------------------+
|  Status: Ready                                    |
+--------------------------------------------------+
```

## Flujo de Datos

### 1. Carga de Audio

```
Usuario clickea "Open"
    │
    v
filedialog.askopenfilename()
    │
    v
AudioProcessor.load_audio()
    │
    ├──→ soundfile.read() (carga datos)
    ├──→ Convierte a mono si es estéreo
    └──→ Guarda original_audio (copia)
    │
    v
_draw_original_waveform()
_draw_modified_waveform()
```

### 2. Modificación de Parámetros

```
Usuario mueve slider
    │
    v
<ButtonPress-1> → _stop_audio() (corta reproducción)
    │
    v
Usuario arrastra slider
    │
    v
_variable.trace_add() → Actualiza label de valor
    │
    v
<ButtonRelease-1> → _on_slider_release()
    │
    ├──→ _draw_modified_waveform()
    │
    └──→ Si auto_preview activo:
         └──→ _play_modified()
```

### 3. Guardado de Audio

```
Usuario clickea "Save"
    │
    v
_save_modified()
    │
    ├──→ filedialog.asksaveasfilename()
    │
    v
AudioProcessor.apply_process_all(params)
    │
    v
AudioProcessor.save_audio()
    │
    └──→ soundfile.write()
```

## Hilos (Threading)

### Uso de Hilos

| Operación | Hilo | Propósito |
|-----------|------|-----------|
| Reproducción de audio | `threading.Thread(daemon=True)` | No bloquear UI |
| Guardado de audio | Hilo principal | Operación rápida |

### Sincronización

```python
# Lock para proteger is_playing
self._play_lock = threading.Lock()

def play_audio(self, audio, callback=None):
    with self._play_lock:
        if self.is_playing:
            self.stop_playback()
        self.is_playing = True
    
    def _play():
        # ... reproducción ...
        with self._play_lock:
            self.is_playing = False
        if callback:
            callback()
    
    thread = threading.Thread(target=_play, daemon=True)
    thread.start()
```

## Efectos de Audio

### Categorías

| Categoría | Color | Efectos |
|-----------|-------|---------|
| Basic | 🔵 Azul | VU Meter, Volume, Pitch, Speed |
| EQ | 🔵 Cyan | 5-band equalizer |
| Filters | 🔵 Cyan | Low-pass, High-pass |
| Modulation | 🟣 Púrpura | Chorus, Flanger, Phaser, Tremolo, Vibrato |
| Distortion | 🔴 Naranja | Distortion, Bitcrusher, Overdrive |
| Time | 🟠 Amarillo | Reverb, Delay |
| Dynamics | 🟢 Verde | Compression, Gate |
| Utility | ⚪ Gris | Fade, Normalize, Trim, Reverse |

### Procesamiento Condicional

```python
# Solo aplica efecto si el parámetro no es neutro
volume = params.get('volume', 1.0)
if volume != 1.0:
    audio = self.apply_volume(audio, volume)
```

## Dependencias

| Librería | Propósito | Versión |
|----------|-----------|---------|
| `numpy` | Computación numérica | >=1.24.0 |
| `scipy` | Procesamiento de señales | >=1.10.0 |
| `soundfile` | E/S de audio | >=0.12.0 |
| `sounddevice` | Reproducción de audio | >=0.4.6 |
| `tkinter` | Interfaz gráfica | Incluido con Python |

## VU Meter - Escala y Mapeo

### Escala Visual

El VU meter analógico muestra una escala de **-20 dB a +3 dB**:

```
Posición del needle:  0.0                    1.0
                      |                       |
Escala dB:          -20  -10  -7  -5  -3   0  +1  +2  +3
                    |    |    |   |   |    |   |   |   |
Color:             verde      verde   amarillo    rojo
```

### Mapeo de Niveles de Audio

Durante la reproducción, el nivel RMS del audio se convierte a la posición del needle:

```python
# Conversión de RMS a dB
level_db = 20 * np.log10(rms)  # rango típico: -60 a 0 dB

# Mapeo a posición del needle (0.0 a 1.0)
# VU meter scale: -20 dB = 0.0, +3 dB = 1.0
level = (level_db - vu_db_min) / (vu_db_max - vu_db_min)
level = np.clip(level, 0.0, 1.0)
```

### Ejemplos de Mapeo

| RMS | dB | Needle Position | Label Visual |
|-----|-----|-----------------|--------------|
| 0.001 | -60 dB | 0.00 | -20 (clip inferior) |
| 0.01 | -40 dB | 0.00 | -20 (clip inferior) |
| 0.1 | -20 dB | 0.00 | **-20** |
| 0.5 | -6 dB | 0.61 | entre -7 y -5 |
| 1.0 | 0 dB | 0.87 | **0** |
| 1.41 | +3 dB | 1.00 | **+3** (clip superior) |

### Layout del Tab Basic

El tab Basic usa un grid layout con 4 columnas de igual ancho:

```python
# Grid con 4 columnas uniformes
for i in range(4):
    content_frame.columnconfigure(i, weight=1, uniform='basic')

# Columna 0: VU Meter
vu_channel.grid(row=0, column=0, sticky='nsew')

# Columnas 1-3: Faders (VOL, PITCH, SPEED)
channel.grid(row=0, column=col + 1, sticky='nsew')
```

## Compatibilidad

| Plataforma | Soporte | Backend de Audio |
|------------|---------|------------------|
| Windows | ✅ Completo | WASAPI, MME |
| Linux | ✅ Completo | ALSA, PulseAudio |
| macOS | ✅ Completo | CoreAudio |
