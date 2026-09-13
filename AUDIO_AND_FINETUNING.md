# Audio Generation & Fine-tuning Guide

Guía completa sobre generación de audio y fine-tuning en Bark with Voice Clone.

---

## Pipeline de Generación de Audio

### Flujo de datos

```
Texto → SEMANTIC → COARSE → FINE → Audio
```

### Los 3 modelos de Bark

Bark utiliza tres modelos de IA que trabajan en secuencia para convertir texto en audio.

---

### 1. SEMANTIC (text → semantic)

**Qué hace:** Convierte texto en tokens semánticos (10,000 tokens posibles).

**Qué controla:**
- La entonación del habla
- El ritmo y pausas
- El significado y emoción del mensaje

**Efecto en calidad:** ALTO - Define QUÉ se dice y CÓMO se dice.

**Sin buen modelo semantic:** El audio suena robótico o sin sentido.

**Archivo:** `semantic_output/` o `text_2.pt`

---

### 2. COARSE (semantic → coarse)

**Qué hace:** Convierte tokens semánticos en 2 codebooks de audio (estructura básica).

**Qué controla:**
- La estructura básica del sonido
- Los primeros 2 niveles de calidad del audio
- La forma general de las ondas de audio

**Efecto en calidad:** MEDIO - Afecta la claridad general del audio.

**Sin buen modelo coarse:** El audio suena distorsionado o incompleto.

**Archivo:** `coarse_output/` o `coarse_2.pt`

---

### 3. FINE (coarse → fine)

**Qué hace:** Convierte 2 codebooks en 8 codebooks completos (detalles finos).

**Qué controla:**
- Los detalles de alta frecuencia
- La nitidez del audio
- Los matices vocales (respiración, clicks, etc.)

**Efecto en calidad:** ALTO - Define la CALIDAD y NITIDEZ del audio final.

**Sin buen modelo fine:** El audio suena turbio o de baja calidad.

**Archivo:** `fine_output/` o `fine_2.pt`

---

### Relación entre los modelos

| Modelo | Qué aprende | Impacto en calidad |
|--------|-------------|-------------------|
| **Semantic** | Prosodia, entonación, significado | ALTO - Sin buen semantic, suena robótico |
| **Coarse** | Estructura básica del sonido | MEDIO - Afecta claridad general |
| **Fine** | Detalles de alta frecuencia | ALTO - Sin buen fine, suena turbio |

### Resumen

- **Semantic** = QUÉ dice (texto → significado)
- **Coarse** = CÓMO suena (estructura básica)
- **Fine** = CALIDAD del sonido (detalles finos)

---

## Fine-tuning (Ajuste Fino)

### Qué es

Fine-tuning es **entrenar un modelo pre-entrenado** con **tus propios datos** para que se adapte a algo específico.

### Ejemplo simple

Bark habla bien en general, pero quieres que suene como **una voz específica** (por ejemplo, tu voz o la de alguien).

- **Sin fine-tuning:** Bark usa su conocimiento general
- **Con fine-tuning:** Bark aprende a imitar esa voz específica

### Cómo funciona

1. **Tomas audio** de la voz que quieres clonar (varios minutos)
2. **Lo transformas** en datos de entrenamiento (tokens)
3. **Entrenas** el modelo con esos datos
4. **El modelo aprende** patrones de esa voz específica

### Qué puedes fine-tunear

| Qué fine-tuneas | Qué mejora |
|-----------------|------------|
| **Semantic** | Que el modelo escriba como esa persona (estilo, ritmo) |
| **Coarse** | Que la voz suene más parecida en estructura |
| **Fine** | Que la voz suene más clara y nítida |

### Resultado

- **Sin fine-tuning:** Voz genérica, suena "como Bark"
- **Con fine-tuning:** Voz más personalizada, suena más como la persona original

---

## Cómo hacer Fine-tuning

### Proceso paso a paso

1. **Preparas tu dataset** de audio (varios minutos de la voz que quieres)
2. **Abres los notebooks** de entrenamiento
3. **Ejecutas las celdas** en orden

### Notebooks disponibles

| Notebook | Qué entrena |
|----------|-------------|
| `train_semantic.ipynb` | Modelo semantic (texto → entonación) |
| `train_coarse.ipynb` | Modelo coarse (estructura del sonido) |
| `train_fine.ipynb` | Modelo fine (detalles de calidad) |

### Comando para abrir

```bash
# Windows
jupyter notebook train_semantic.ipynb
jupyter notebook train_coarse.ipynb
jupyter notebook train_fine.ipynb

# Linux/Mac
jupyter notebook train_semantic.ipynb
jupyter notebook train_coarse.ipynb
jupyter notebook train_fine.ipynb
```

### Qué necesitas

1. **Archivos de audio** (.wav) de la voz que quieres clonar
2. **Transcripción** del texto de cada audio (en un archivo `train.txt`)
3. **GPU** con al menos 8GB de VRAM (recomendado)

### Estructura del dataset

```
mi_dataset/
├── train.txt          # Formato: ruta_audio|texto
├── valid.txt          # Formato: ruta_audio|texto
└── wavs/              # Archivos de audio
    ├── audio1.wav
    ├── audio2.wav
    └── ...
```

### Resultado

Después de entrenar, se guardan archivos en:
- `semantic_output/pytorch_model.bin`
- `coarse_output/pytorch_model.bin`
- `fine_output/pytorch_model.bin`

Estos archivos se usan automáticamente al generar audio.

### No hay comando CLI para fine-tuning

Actualmente solo se puede hacer desde los notebooks de Jupyter. No hay un comando de línea de comando para entrenar.

---

## Formatos de Audio

### Parámetros disponibles

| Parámetro | Opciones | Descripción |
|-----------|----------|-------------|
| `sample_rate` | 11025, 22050, 44100 Hz | Frecuencia de muestreo |
| `bits_per_sample` | 8, 16 bits | Bits por muestra |
| `channels` | mono, stereo | Canales de audio |

### Calidad por configuración

| Configuración | Calidad | Tamaño | Uso recomendado |
|---------------|---------|--------|-----------------|
| 11025 Hz, 8 bits, mono | Baja | Pequeño | Prototipos rápidos |
| 22050 Hz, 16 bits, mono | Media | Medio | Uso general |
| 44100 Hz, 16 bits, mono | Alta | Grande | Producción profesional |
| 44100 Hz, 16 bits, stereo | Máxima | Muy grande | Audio estéreo |

### Usar con CLI

```bash
# Básico (24kHz, float32, mono)
python bark_cli.py generate "Hola" -o output.wav

# Alta calidad
python bark_cli.py generate "Hola" -o output.wav --sample-rate 44100 --bits 16

# Estéreo
python bark_cli.py generate "Hola" -o output.wav --sample-rate 44100 --bits 16 --channels stereo
```

### Usar con Python

```python
from bark import generate_audio, preload_models
from bark.api import save_audio

preload_models()

# Generar con parámetros personalizados
audio = generate_audio(
    "Hola mundo",
    sample_rate=44100,
    bits_per_sample=16,
    channels="mono"
)

save_audio("output.wav", audio, sample_rate=44100)
```

---

## Consejos para Mejorar la Calidad

### 1. Usar voces adecuadas

```bash
# Listar voces disponibles
python bark_cli.py voices
```

Probar diferentes speakers:
- `es_speaker_0` a `es_speaker_9` para español
- `en_speaker_0` a `en_speaker_9` para inglés

### 2. Ajustar temperaturas

| Temperatura | Efecto |
|-------------|--------|
| 0.3 - 0.5 | Más estable, menos variación |
| 0.7 (default) | Balance entre estabilidad y naturalidad |
| 0.8 - 1.0 | Más diverso, puede sonar más natural pero menos predecible |

### 3. Usar fine-tuning

Para la mejor calidad posible, fine-tunea los 3 modelos con tu dataset de voz específica.

### 4. Post-procesamiento con RVC

Usar RVC para mejorar aún más la naturalidad de la voz generada.

### 5. Texto bien formateado

- Usar puntuación adecuada
- Incluir pausas con `...` o `—`
- Agregar emociones con `[laughs]`, `[sighs]`, etc.

---

## Solución de Problemas

### Audio suena robótico

- Probar diferentes voces (`es_speaker_1`, `es_speaker_3`, etc.)
- Ajustar temperatura a 0.5
- Fine-tunear el modelo semantic

### Audio suena turbio

- Fine-tunear el modelo fine
- Usar `--sample-rate 44100` para mejor calidad
- Verificar que el modelo fine esté bien entrenado

### Audio tiene ruido de fondo

- Probar otras voces
- Reducir temperatura a 0.4-0.5
- Usar modelo fine bien entrenado

### Generación es muy lenta

- Usar `--small` para modelos pequeños
- Tener GPU disponible
- Reducir la longitud del texto

---

## Resumen

| Concepto | Descripción |
|----------|-------------|
| **Semantic** | Convierte texto en entonación (QUÉ dice) |
| **Coarse** | Crea estructura básica del sonido (CÓMO suena) |
| **Fine** | Añade detalles de calidad (CALIDAD del sonido) |
| **Fine-tuning** | Entrenar modelo con datos específicos |
| **Sample rate** | Calidad del audio (11025, 22050, 44100 Hz) |
| **Bits** | Precisión del audio (8 o 16 bits) |
| **Channels** | Mono o stereo |
