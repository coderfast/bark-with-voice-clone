# Audio Generation & RVC Guide

Guía completa sobre generación de audio y uso de RVC (Retrieval-based Voice Conversion).

---

## Fine-tuning vs RVC

### ¿Cuál es la diferencia?

| Proceso | Qué hace | Cuándo se usa |
|---------|----------|---------------|
| **Fine-tuning** | Entrena modelos de Bark para que suenen como una voz específica | **Antes** de generar audio |
| **RVC** | Convierte una voz generada en otra voz diferente | **Después** de generar audio |

### Flujo completo

```
1. Fine-tuning (opcional) → Entrenar modelos Bark con tu voz
2. Bark genera audio → Texto a voz
3. RVC (opcional) → Convertir la voz generada a otra voz
```

### Analogía simple

- **Fine-tuning** = Enseñarle a Bark a hablar como tú
- **RVC** = Tomar el audio de Bark y transformarlo para que suene como otra persona

---

## ¿Cuándo usar RVC?

| Situación | ¿Usar RVC? | Razón |
|-----------|------------|-------|
| Quieres que suene como alguien específico | Sí | RVC transforma la voz al estilo deseado |
| La voz generada no te convence | Sí | RVC puede mejorar la naturalidad |
| Necesitas cambiar tono o timbre | Sí | RVC permite ajustar estas propiedades |
| Solo quieres generar audio rápido | No | RVC añade un paso extra |
| Ya hiciste fine-tuning con buena calidad | No | El fine-tuning ya logró el resultado |

### Ejemplo práctico

**Sin RVC:**
1. Bark genera audio con voz genérica de `es_speaker_0`
2. Suena bien pero no como la persona que quieres

**Con RVC:**
1. Bark genera audio con voz genérica
2. RVC transforma esa voz para que suene como la persona específica
3. Resultado: voz más personalizada

---

## Instalación de RVC

### Soporte por plataforma

| Plataforma | Soporte | Método recomendado |
|------------|---------|-------------------|
| **Windows** | ✅ Completo | Release pre-compilado o repositorio |
| **Linux** | ✅ Completo | Repositorio (requiere compilación) |
| **Mac** | ✅ Parcial | Repositorio (puede tener limitaciones) |

---

### Windows

#### Opción 1: Release pre-compilado (Recomendado)

1. Ir a: https://github.com/Tiger14n/RVC-GUI/releases/tag/Windows-pkg
2. Descargar el archivo comprimido (`.zip` o `.7z`)
3. Extraer en la carpeta `RVC-GUI-pkg/` del proyecto
4. Ejecutar directamente (no requiere instalación adicional)

#### Opción 2: Clonar repositorio

```cmd
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
cd Retrieval-based-Voice-Conversion-WebUI
pip install -r requirements.txt
```

#### Requisitos previos Windows

- Python 3.8+
- CUDA 11.7 o superior (para GPU)
- Git

---

### Linux

#### Paso 1: Instalar dependencias del sistema

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip python3-venv git ffmpeg libsndfile1

# Fedora/RHEL
sudo dnf install python3-devel python3-pip python3-virtualenv git ffmpeg libsndfile-devel

# Arch Linux
sudo pacman -S python python-pip git ffmpeg libsndfile
```

#### Paso 2: Clonar e instalar RVC

```bash
# Clonar repositorio
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
cd Retrieval-based-Voice-Conversion-WebUI

# Crear entorno virtual (recomendado)
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar PyTorch con CUDA (si tienes GPU NVIDIA)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Paso 3: Verificar instalación

```bash
python -c "from rvc_infer import get_vc; print('RVC OK')"
```

#### Requisitos previos Linux

- Python 3.8+
- CUDA 11.7 o superior (para GPU NVIDIA)
- FFmpeg
- Git
- 8GB+ RAM recomendado

---

### Mac

#### Paso 1: Instalar dependencias del sistema

```bash
# Instalar Homebrew (si no está instalado)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar dependencias
brew install python@3.10 git ffmpeg libsndfile
```

#### Paso 2: Clonar e instalar RVC

```bash
# Clonar repositorio
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
cd Retrieval-based-Voice-Conversion-WebUI

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar PyTorch (para Apple Silicon M1/M2/M3)
pip install torch torchvision torchaudio
```

#### Paso 3: Verificar instalación

```bash
python -c "from rvc_infer import get_vc; print('RVC OK')"
```

#### Notas para Mac

- **Apple Silicon (M1/M2/M3):** PyTorch soporta nativamente Metal Performance Shaders (MPS)
- **Intel Mac:** Funciona con CPU, sin aceleración GPU específica
- **Rendimiento:** Puede ser más lento que en Linux/Windows con GPU NVIDIA

#### Requisitos previos Mac

- Python 3.10+ (recomendado)
- Homebrew
- FFmpeg
- Git
- macOS 12.0+ (para Apple Silicon)

---

### Verificación universal

Independientemente de la plataforma, verifica la instalación con:

```bash
python -c "from rvc_infer import get_vc, vc_single; print('RVC OK')"
```

---

## Uso de RVC

### Método 1: Usando el CLI

```bash
# Generar audio con Bark
python bark_cli.py generate "Hola mundo" -v es_speaker_0 -o bark_output.wav

# Aplicar RVC (código de ejemplo)
python -c "
from rvc_infer import get_vc, vc_single
get_vc('modelo.pth', 'cuda:0', True)
audio = vc_single(0, 'bark_output.wav', f0_up_key=-6, ...)
"
```

### Método 2: Usando Python

```python
from rvc_infer import get_vc, vc_single

# 1. Cargar modelo RVC
get_vc("Retrieval-based-Voice-Conversion-WebUI/weights/modelo.pth", "cuda:0", True)

# 2. Convertir audio
audio = vc_single(
    sid=0,
    input_audio="bark_output.wav",
    f0_up_key=-6,           # Cambio de tono (-12 a +12)
    f0_file=None,
    f0_method="harvest",    # Método de extracción de F0
    file_index="path/to/index",  # Archivo índice (opcional)
    index_rate=0.75,        # Tasa de index (0.0 a 1.0)
    filter_radius=3,        # Radio de filtro
    resample_sr=24000,      # Sample rate de salida
    rms_mix_rate=0.25,      # Tasa de mezcla RMS
    protect=0.33            # Protección de consonantes
)

# 3. Guardar audio
from scipy.io.wavfile import write
write("output_rvc.wav", 24000, audio)
```

### Método 3: Usando la GUI de RVC

1. Abrir la GUI de RVC desde `RVC-GUI-pkg/`
2. Cargar el modelo `.pth`
3. Cargar el archivo de audio generado por Bark
4. Ajustar parámetros
5. Procesar y guardar

---

## Parámetros de RVC

### Parámetros principales

| Parámetro | Rango | Descripción | Valor recomendado |
|-----------|-------|-------------|-------------------|
| `f0_up_key` | -12 a +12 | Cambio de tono (semitonos) | -6 a +6 |
| `f0_method` | harvest, pm | Método de extracción de F0 | harvest (mejor calidad) |
| `index_rate` | 0.0 a 1.0 | Tasa de búsqueda por índice | 0.75 |
| `filter_radius` | 0 a 10 | Radio de suavizado de F0 | 3 |
| `resample_sr` | 0, 16000, 24000, 44100 | Sample rate de salida | 24000 o 44100 |
| `rms_mix_rate` | 0.0 a 1.0 | Mezcla de volumen | 0.25 |
| `protect` | 0.0 a 0.5 | Protección de consonantes | 0.33 |

### Descripción detallada

**f0_up_key (Cambio de tono)**
- Valores negativos: voz más grave
- Valores positivos: voz más aguda
- 0: sin cambio

**f0_method (Método de extracción)**
- `harvest`: Mejor calidad, más lento
- `pm`: Más rápido, menor calidad

**index_rate (Tasa de índice)**
- 0.0: No usa índice (más rápido)
- 1.0: Usa mucho índice (más lento, más fiel)
- 0.75: Balance recomendado

**protect (Protección)**
- 0.0: Sin protección
- 0.5: Máxima protección de consonantes
- 0.33: Valor por defecto recomendado

---

## Archivos necesarios para RVC

### Modelo RVC (`.pth`)

- **Qué es:** El modelo entrenado con la voz que quieres usar
- **Dónde obtenerlo:**
  - Entrenarlo con la GUI de RVC
  - Descargar modelos pre-entrenados
- **Dónde guardarlo:** `Retrieval-based-Voice-Conversion-WebUI/weights/`

### Archivo índice (`.index`)

- **Qué es:** Archivo de búsqueda para mejorar la calidad
- **Es obligatorio:** No, pero mejora los resultados
- **Dónde obtenerlo:** Se genera automáticamente al entrenar el modelo
- **Dónde guardarlo:** `Retrieval-based-Voice-Conversion-WebUI/logs/`

---

## Proceso completo paso a paso

### Paso 1: Preparar audio de referencia

1. Grabar audio claro de 5-12 segundos
2. Sin ruido de fondo
3. Formato WAV, 16kHz o superior

### Paso 2: Entrenar modelo RVC

1. Abrir GUI de RVC
2. Ir a pestaña "Train"
3. Configurar parámetros:
   - Epochs: 200-500
   - Batch size: 8-16
   - Sample rate: 40k o 48k
4. Iniciar entrenamiento
5. Esperar a que termine (puede tomar horas)

### Paso 3: Generar audio con Bark

```bash
python bark_cli.py generate "Texto a generar" -v es_speaker_0 -o bark_output.wav
```

### Paso 4: Aplicar RVC

```python
from rvc_infer import get_vc, vc_single

# Cargar modelo
get_vc("pesos/modelo.pth", "cuda:0", True)

# Convertir
audio = vc_single(0, "bark_output.wav", f0_up_key=-6, ...)

# Guardar
from scipy.io.wavfile import write
write("final_output.wav", 24000, audio)
```

### Paso 5: Verificar resultado

1. Escuchar el audio generado
2. Ajustar `f0_up_key` si el tono no es correcto
3. Reintentar con diferentes parámetros si es necesario

---

## Solución de problemas

### "RVC no encontrado"

**Causa:** Los archivos de RVC no están en la ubicación correcta.

**Solución:**
1. Verificar que `Retrieval-based-Voice-Conversion-WebUI` esté en la raíz del proyecto
2. O verificar que `RVC-GUI-pkg/` tenga los archivos

### "CUDA out of memory"

**Causa:** No hay suficiente memoria GPU.

**Solución:**
1. Usar CPU en su lugar
2. Reducir el batch size
3. Usar modelo más pequeño

### "Error al cargar modelo"

**Causa:** Archivo `.pth` corrupto o incompatible.

**Solución:**
1. Verificar que el archivo no esté corrupto
2. Reentrenar el modelo
3. Usar otro modelo

### "Audio suena mal después de RVC"

**Causa:** Parámetros incorrectos.

**Solución:**
1. Ajustar `f0_up_key` (tono)
2. Cambiar `f0_method` a "harvest"
3. Ajustar `index_rate` a 0.75
4. Verificar que el modelo RVC esté bien entrenado

### "Proceso muy lento"

**Causa:** Usando CPU o modelo muy grande.

**Solución:**
1. Usar GPU si está disponible
2. Reducir calidad de salida
3. Usar modelo más pequeño

---

## Consejos para mejores resultados

### 1. Calidad del audio de entrada

- Usar audio claro sin ruido
- Sample rate de 16kHz o superior
- Duración de 5-12 segundos

### 2. Parámetros RVC

- Empezar con valores por defecto
- Ajustar `f0_up_key` según sea necesario
- Usar `harvest` para mejor calidad

### 3. Modelo RVC

- Entrenar con suficientes epochs (200+)
- Usar dataset variado
- Verificar calidad antes de usar

### 4. Post-procesamiento

- Escuchar resultado completo
- Ajustar volumen si es necesario
- Considerar ecualización para mejorar

---

## Resumen

| Concepto | Descripción |
|----------|-------------|
| **Fine-tuning** | Entrena modelos Bark con tu voz (antes de generar) |
| **RVC** | Convierte audio generado en otra voz (después de generar) |
| **Modelo .pth** | Modelo RVC entrenado |
| **Archivo .index** | Índice para búsqueda de voz |
| **f0_up_key** | Cambio de tono en semitonos |
| **f0_method** | Método de extracción de frecuencia fundamental |
| **index_rate** | Tasa de uso del índice |

---

## Enlaces útiles

- [Repositorio oficial de RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)
- [RVC-GUI (versión simplificada)](https://github.com/Tiger14n/RVC-GUI)
- [Documentación de RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/wiki)
