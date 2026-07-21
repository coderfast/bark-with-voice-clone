# APP_TECHNICALSTACK.md — Voice Filter

## Technical Stack

### Lenguaje de Programación

| Lenguaje | Versión | Uso |
|----------|---------|-----|
| **Python** | 3.8+ | Lenguaje principal |

### Framework de GUI

| Librería | Versión | Propósito |
|----------|---------|-----------|
| **Tkinter** | Incluido | Interfaz gráfica |
| **ttk** | Incluido | Widgets temáticos |

### Procesamiento de Audio

| Librería | Propósito |
|----------|-----------|
| **NumPy** | Computación numérica, arrays |
| **SciPy** | Filtros, ecualización, procesamiento de señales |
| **SoundFile** | Lectura/escritura de archivos de audio |
| **SoundDevice** | Reproducción de audio en tiempo real |

### Formatos Soportados

#### Entrada

| Formato | Extensión | Soporte |
|---------|-----------|---------|
| WAV | `.wav` | ✅ Completo |
| MP3 | `.mp3` | ✅ Completo |
| AAC | `.aac` | ✅ Completo |
| FLAC | `.flac` | ✅ Completo |
| OGG | `.ogg` | ✅ Completo |
| M4A | `.m4a` | ✅ Completo |
| WMA | `.wma` | ✅ Completo |

#### Salida

| Formato | Sample Rates | Bits |
|---------|--------------|------|
| WAV | 11025, 22050, 24000, 44100 Hz | 8, 16, 32-bit float |

## Requisitos del Sistema

### Requisitos Mínimos

| Componente | Requisito |
|------------|-----------|
| **SO** | Windows 10+, Linux, macOS 10.15+ |
| **Python** | 3.8 o superior |
| **RAM** | 8 GB |
| **Almacenamiento** | 500 MB |
| **GPU** | Opcional |

### Requisitos Recomendados

| Componente | Requisito |
|------------|-----------|
| **SO** | Windows 11, Ubuntu 20.04+, macOS 12+ |
| **Python** | 3.10 o superior |
| **RAM** | 16 GB |
| **Almacenamiento** | 1 GB |

## Instalación

### Windows

```cmd
cd app_voice_filter
pip install -r requirements.txt
python voice_filter.py
```

### Linux

```bash
cd app_voice_filter
sudo apt-get install python3-tk libportaudio2
pip install -r requirements.txt
python3 voice_filter.py
```

### macOS

```bash
cd app_voice_filter
brew install python@3.10
pip install -r requirements.txt
python3 voice_filter.py
```

## Efectos de Audio

### Basic (🔵 Azul)

| Efecto | Rango | Descripción |
|--------|-------|-------------|
| VU Meter | -20 a +3 dB | Visualización de nivel de audio |
| Volume | 0.0 - 2.0 | Ajuste de amplitud |
| Pitch | -12 - +12 st | Cambio de tono |
| Speed | 0.5x - 2.0x | Velocidad de reproducción |

### EQ (🔵 Cyan)

| Banda | Frecuencia | Rango |
|-------|------------|-------|
| Bass | 100 Hz | -12 - +12 dB |
| Low Mid | 400 Hz | -12 - +12 dB |
| Mid | 1 kHz | -12 - +12 dB |
| High Mid | 2.5 kHz | -12 - +12 dB |
| Treble | 6 kHz | -12 - +12 dB |

### Filters (🔵 Cyan)

| Filtro | Rango | Descripción |
|--------|-------|-------------|
| Low Pass | 100 - 20000 Hz | Elimina frecuencias altas |
| High Pass | 20 - 5000 Hz | Elimina frecuencias bajas |

### Modulation (🟣 Púrpura)

| Efecto | Rango | Descripción |
|--------|-------|-------------|
| Chorus | 0.0 - 1.0 | Efecto de duplicación |
| Flanger | 0.0 - 1.0 | Efecto de barrido |
| Phaser | 0.0 - 1.0 | Cambio de fase |
| Tremolo | 0.0 - 1.0 | Modulación de amplitud |
| Vibrato | 0.0 - 1.0 | Modulación de frecuencia |

### Distortion (🔴 Naranja)

| Efecto | Rango | Descripción |
|--------|-------|-------------|
| Distortion | 0.0 - 1.0 | Clip suave |
| Bitcrusher | 4 - 32 bits | Reducción de bits |
| Overdrive | 1.0 - 10.0x | Aumento de ganancia |

### Time (🟠 Amarillo)

| Efecto | Rango | Descripción |
|--------|-------|-------------|
| Reverb | 0.0 - 1.0 | Simulación de sala |
| Delay | 0 - 500 ms | Efecto de eco |

### Dynamics (🟢 Verde)

| Efecto | Rango | Descripción |
|--------|-------|-------------|
| Comp Threshold | -40 - 0 dB | Nivel de activación |
| Comp Ratio | 1:1 - 20:1 | Cantidad de compresión |
| Gate | -60 - 0 dB | Umbral de ruido |

### Utility (⚪ Gris)

| Efecto | Rango | Descripción |
|--------|-------|-------------|
| Fade In | 0 - 5000 ms | Aumento gradual |
| Fade Out | 0 - 5000 ms | Disminución gradual |
| Normalize | -24 - 0 dB | Normalización de nivel |
| Trim Start | 0 - 100 s | Punto de inicio |
| Trim End | 0 - 100 s | Punto final |
| Reverse | On/Off | Inversión |

## Hilos (Threading)

### Modelo de Concurrency

```python
import threading

class AudioProcessor:
    def __init__(self):
        self.is_playing = False
        self._play_lock = threading.Lock()
    
    def play_audio(self, audio, callback=None):
        with self._play_lock:
            if self.is_playing:
                self.stop_playback()
            self.is_playing = True
        
        def _play():
            try:
                import sounddevice as sd
                sd.play(audio, self.sample_rate)
                sd.wait()
            finally:
                with self._play_lock:
                    self.is_playing = False
                if callback:
                    callback()
        
        thread = threading.Thread(target=_play, daemon=True)
        thread.start()
```

### Backends de Audio

| Plataforma | Backend | Soporte |
|------------|---------|---------|
| Windows | WASAPI | ✅ |
| Windows | MME | ✅ |
| Linux | ALSA | ✅ |
| Linux | PulseAudio | ✅ |
| macOS | CoreAudio | ✅ |

## Dependencias

### requirements.txt

```
numpy>=1.24.0
scipy>=1.10.0
soundfile>=0.12.0
sounddevice>=0.4.6
```

### Opcionales

```
librosa>=0.10.0    # Procesamiento avanzado
pedalboard>=0.7.0  # Efectos adicionales
```

## Seguridad

### Validación de Entrada

```python
# Clips audio para evitar distorsión
return np.clip(audio * volume, -1.0, 1.0)

# Verifica archivos antes de cargar
if not os.path.isfile(filepath):
    return False
```

### Protección de Hilos

```python
# Lock para operaciones compartidas
self._play_lock = threading.Lock()

# Hilos daemon para cierre limpio
thread = threading.Thread(target=_play, daemon=True)
```

## Rendimiento

### Optimizaciones

- **Procesamiento condicional**: Solo aplica efectos cuando el parámetro no es neutro
- **Downsampling para visualización**: Reduce samples para dibujar onda
- **Hilos daemon**: No bloquean el cierre de la aplicación
- **Cache de audio original**: No recarga al procesar

### Limitaciones

- Efectos de modulación usan loops en Python (no optimizados para GPU)
- Compresión y gate procesan sample por sample
- Reverb usa delays fijos (no configurable)

## Futuras Mejoras

### Planeadas

- Procesamiento GPU para efectos pesados
- Efectos adicionales (Chorus estéreo, Multi-tap delay)
- Exportación a múltiples formatos
- Presets guardables
- Historial de cambios (undo/redo)

## VU Meter - Detalles Técnicos

### Componentes

| Componente | Descripción |
|------------|-------------|
| `AnalogVUMeter` | Widget Canvas con aguja animada |
| `MixerFader` | Widget Canvas con medidor LED |
| Física de resorte | Simula rebote de aguja con damping |

### Escala del VU Meter

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `_db_min` | -20 dB | Posición 0.0 del needle |
| `_db_max` | +3 dB | Posición 1.0 del needle |
| Rango total | 23 dB | De -20 a +3 dB |
| Colores | Verde/Amarillo/Rojo | Indicación visual de nivel |

### Física de la Aguja

```python
# Parámetros de animación
attack_speed = 0.2      # Velocidad de subida
decay_speed = 0.04      # Velocidad de bajada
damping = 0.82          # Amortiguación
spring_constant = 0.35  # Constante del resorte

# Ecuación de movimiento
error = target_level - current_level
spring_force = error * spring_constant
velocity += spring_force * (attack_speed if error > 0 else decay_speed)
velocity *= damping
current_level += velocity
```

### Layout Grid

El tab Basic usa un grid layout con 4 columnas de igual ancho:

```python
# Todas las columnas tienen el mismo peso
for i in range(4):
    content_frame.columnconfigure(i, weight=1, uniform='basic')

# Los canales se expanden para llenar su columna
channel.grid(row=0, column=col, sticky='nsew')
```
