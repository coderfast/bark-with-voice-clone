# APP_ARCHITECTURE.md — Voice Filter

## Overview

Voice Filter es una aplicación de procesamiento de audio con interfaz gráfica que permite cargar archivos de audio y modificarlos en tiempo real con más de 20 efectos.

## Estructura del Proyecto

```
app_voice_filter/
├── voice_filter.py          # Aplicación principal (GUI + procesamiento)
├── requirements.txt         # Dependencias
└── APP_ARCHITECTURE.md      # Este archivo
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
|  |  Parámetros por categoría                    ||
|  |  (Sliders con valores)                       ||
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
| Basic | 🔵 Azul | Volume, Pitch, Speed |
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

## Compatibilidad

| Plataforma | Soporte | Backend de Audio |
|------------|---------|------------------|
| Windows | ✅ Completo | WASAPI, MME |
| Linux | ✅ Completo | ALSA, PulseAudio |
| macOS | ✅ Completo | CoreAudio |
