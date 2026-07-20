# app_clone_voice

Herramienta CLI independiente para clonar voces humanas a partir de muestras de audio.

## Que hace

Toma un audio corto de una persona hablando (5-13 segundos) y extrae los features de la voz para crear un prompt `.npz` que puede usarse con Bark TTS para generar audio con esa voz.

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Audio humano   │      │   Clonar voz    │      │  Prompt de voz  │
│  (5-13 seg)     │ ───► │   (HuBERT +     │ ───► │   (mi_voz.npz)  │
│  reference.wav  │      │    EnCodec)     │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

**Nota**: Esta herramienta solo clona voces. Para generar audio con la voz clonada, usa el modulo `bark/` incluido en esta carpeta o cualquier herramienta compatible con prompts de Bark.

## Requisitos

- Python >=3.8
- **SO**: Windows, Linux, macOS
- GPU NVIDIA (recomendado), Apple Silicon (MPS), o CPU
- ~2GB de RAM (CPU) o ~4GB de VRAM (GPU)

## Instalacion

```bash
cd app_clone_voice
pip install -r requirements.txt
```

O instalar como paquete:

```bash
pip install -e .
# Ahora puedes usar: voice-clone --name mi_voz
```

### Dependencias

```
torch, torchaudio, encodec, transformers, einops,
scipy, numpy, huggingface_hub, tqdm, soundfile
```

Los modelos se descargan automaticamente en la primera ejecucion:
- HuBERT: `data/models/hubert/` (~390MB)
- EnCodec: `~/.cache/serp/bark_v0/` (~50MB)

## Uso

### Clonar una voz

**Opcion 1: Auto-detectar desde carpeta** (recomendado)

```bash
# 1. Pon tu audio en source_voice_input/
#    source_voice_input/mi_voz.wav

# 2. Ejecuta clone
python voice_clone.py --name mi_voz
```

**Opcion 2: Especificar archivo directamente**

```bash
python voice_clone.py --audio reference.wav --name mi_voz
```

Esto genera el archivo `bark/assets/prompts/mi_voz.npz` con los features de la voz.

**Sobrescribir voz existente:**

```bash
python voice_clone.py --audio reference.wav --name mi_voz --force
```

**Tips para mejores resultados:**
- Audio claro, sin ruido de fondo
- 5-13 segundos de duracion
- Una sola persona hablando
- Formatos soportados: WAV, MP3, OGG, FLAC, M4A, WMA

### Seleccion de dispositivo

```bash
# Auto-detectar (recomendado) — prioridad: CUDA > MPS > CPU
python voice_clone.py --audio ref.wav --name voz --device auto

# Forzar GPU NVIDIA
python voice_clone.py --audio ref.wav --name voz --device cuda

# Forzar Apple Silicon (M1/M2/M3/M4)
python voice_clone.py --audio ref.wav --name voz --device mps

# Forzar CPU
python voice_clone.py --audio ref.wav --name voz --device cpu
```

### Verificar dispositivos disponibles

```bash
python voice_clone.py --device-info
```

### Listar voces disponibles

```bash
python voice_clone.py --list
```

### Ver info de una voz

```bash
python voice_clone.py --info en_speaker_0
```

### Verificar version

```bash
python voice_clone.py --version
```

### Salida detallada (verbose)

```bash
python voice_clone.py --verbose --audio ref.wav --name mi_voz
```

Muestra tiempos de carga de modelos y extraccion de features.

### Ejemplo completo

```bash
# 1. Pon tu audio de referencia en source_voice_input/
#    source_voice_input/carlos.wav

# 2. Clonar voz (auto-detecta el audio)
python voice_clone.py --name carlos

# 3. El prompt se guarda en:
#    bark/assets/prompts/carlos.npz
```

## Comandos disponibles

| Flag | Descripcion |
|------|-------------|
| `--audio PATH` | Archivo de audio de referencia (<13s) |
| `--name NAME` | Nombre para la voz clonada (requerido) |
| `--output PATH` | Ruta de salida para el .npz (default: bark/assets/prompts/<name>.npz) |
| `--force` | Sobrescribir voz existente |
| `--device {auto,cuda,cpu,mps}` | Seleccionar dispositivo (default: auto) |
| `--device-info` | Mostrar dispositivos disponibles |
| `--verbose` | Output detallado con tiempos |
| `--quiet` | Modo silencioso (solo imprime path del resultado) |
| `--version` | Mostrar version |
| `--list` | Listar voces disponibles |
| `--info VOICE` | Mostrar metadata de una voz |

## Audio de entrada

### Formatos soportados
`.wav`, `.mp3`, `.ogg`, `.flac`, `.m4a`, `.wma`

### Parametros
| Parametro | Minimo | Recomendado |
|-----------|--------|-------------|
| Duracion | 5 segundos | 5-12 segundos |
| Duracion maxima | 13 segundos | — |
| Sample rate | 8,000 Hz | 44,100 Hz |
| Canales | Mono o stereo | Mono |

### Recomendaciones para grabar
- Habitacion silenciosa, sin eco
- Micfono a 15-30 cm de la boca
- Sample rate: 44,100 Hz o 48,000 Hz
- Formato: WAV o FLAC (sin compresion)
- Hablar con tono natural y constante
- Evitar pausas largas o muletillas

## Como funciona

1. **Audio** → `torchaudio` carga el archivo
2. **Resample** → Se ajusta a 16kHz (para HuBERT)
3. **HuBERT** → Extrae representaciones semanticas (768 dimensiones)
4. **CustomTokenizer** → Cuantiza a tokens (vocabulario de 10,000)
5. **EnCodec** → Extrae codigos de audio (8 codebooks)
6. **Guardar** → Se guarda como `.npz` en `bark/assets/prompts/`

## Archivos generados

**Prompt de voz:**
- Ubicacion: `bark/assets/prompts/<nombre>.npz`
- Contenido: `semantic_prompt`, `coarse_prompt`, `fine_prompt`
- Tamano: ~20-60 KB

## Estructura

```
app_clone_voice/
├── voice_clone.py          # Script CLI principal
├── requirements.txt        # Dependencias
├── QUICKUSAGE.txt          # Guia rapida de uso
├── README.md               # Este archivo
├── AGENTS.md               # Guia para AI agents
├── APP_ARCHITECTURE.md     # Arquitectura detallada
├── APP_TECHNICALSTACK.md   # Stack tecnico
├── ROADMAP.md              # Mejoras planificadas
├── source_voice_input/     # Carpeta para audios de referencia
├── bark/                   # Modulo Bark local
│   ├── api.py
│   ├── generation.py
│   ├── model.py
│   ├── model_fine.py
│   └── assets/prompts/     # Voces clonadas
└── hubert/                 # Modulo HuBERT local
    ├── hubert_manager.py
    ├── pre_kmeans_hubert.py
    └── customtokenizer.py
```

## Voces predefinidas

El directorio `bark/assets/prompts/` incluye 141 voces predefinidas para testing:

- `en_speaker_0` a `en_speaker_9` — Ingles
- `es_speaker_0` a `es_speaker_9` — Espanol
- `fr_speaker_0` a `fr_speaker_9` — Frances
- `de_speaker_0` a `de_speaker_9` — Aleman
- Y mas idiomas (hi, it, ja, ko, pl, pt, ru, tr, zh)

```bash
# Ver una voz predefinida
python voice_clone.py --info en_speaker_0
```

## Solucion de problemas

### "CUDA out of memory"
- Usar `--device cpu`
- Cerrar otros procesos que usen GPU

### "Audio too long"
- El audio debe durar menos de 13 segundos
- Recortar el audio antes de intentar de nuevo

### "Invalid voice name"
- Solo se permiten letras, numeros, guiones (`-`) y guiones bajos (`_`)

### "Voice already exists"
- Usar `--force` para sobrescribir, o elegir otro nombre
- Ver voces existentes con `--list`

### Audio de mala calidad
- Asegurar audio de referencia limpio (sin ruido)
- Usar audio de 5-13 segundos

### Modelos no se descargan
- Verificar conexion a internet
- Verificar permisos de escritura en `data/` y `~/.cache/`

### Apple Silicon (M1/M2/M3/M4)
- Usar `--device mps` o `--device auto`

### Errores inesperados
- Usar `--verbose` para ver el traceback completo

## Relacion con el proyecto principal

Esta app es una version standalone del notebook `clone_voice.ipynb`.

La app incluye copias locales de `bark/` y `hubert/`, por lo que es completamente independiente.

El prompt `.npz` generado puede usarse con Bark TTS para generar audio:
```python
from bark import generate_audio
audio = generate_audio("Hello!", history_prompt="mi_voz")
```

## Docker

```bash
# Construir imagen
docker build -t voice-clone .

# Ejecutar (montar carpeta de audios)
docker run --rm -v $(pwd)/source_voice_input:/app/source_voice_input voice-clone --name mi_voz

# En Windows:
docker run --rm -v %cd%/source_voice_input:/app/source_voice_input voice-clone --name mi_voz
```

## Compilar como Ejecutable Portable

Para generar un ejecutable standalone sin Python instalado:

```bash
# Instalar dependencias de compilacion
pip install -r requirements-build.txt

# Compilar (directorio, recomendado)
python build.py

# O compilar como archivo unico (~1.5-2GB)
python build.py --onefile

# El ejecutable se genera en: dist/
```

El ejecutable funciona sin Python:
```bash
# Windows
dist\voice_clone.exe --name mi_voz --audio ref.wav

# Linux / macOS
./dist/voice_clone --name mi_voz --audio ref.wav
```

## Tests

```bash
# Ejecutar tests
python -m pytest tests/ -v
```

## Licencia

MIT
