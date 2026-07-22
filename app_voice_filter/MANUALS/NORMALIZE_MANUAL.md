# NORMALIZE_MANUAL — Normalización de audio LUFS para videojuegos

Guía completa para normalizar archivos de audio a un mismo volumen, explicada paso a paso para personas sin experiencia técnica.

---

## Tabla de contenidos

1. [¿Para qué sirve esto?](#1-para-qué-sirve-esto)
2. [El problema: audios con diferentes volúmenes](#2-el-problema-audios-con-diferentes-volúmenes)
3. [¿Qué es LUFS?](#3-qué-es-lufs)
4. [Instalación](#4-instalación)
5. [Uso rápido (en 3 pasos)](#5-uso-rápido-en-3-pasos)
6. [Modo archivo único](#6-modo-archivo-único)
7. [Modo carpeta (batch)](#7-modo-carpeta-batch)
8. [Modo análisis (solo leer, no modificar)](#8-modo-análisis-solo-leer-no-modificar)
9. [Generar reporte CSV](#9-generar-reporte-csv)
10. [Targets LUFS recomendados](#10-targets-lufs-recomendados)
11. [Ejemplos prácticos de videojuegos](#11-ejemplos-prácticos-de-videojuegos)
12. [Errores comunes y cómo solucionarlos](#12-errores-comunes-y-cómo-solucionarlos)
13. [Preguntas frecuentes](#13-preguntas-frecuentes)

---

## 1. ¿Para qué sirve esto?

Cuando desarrollas un videojuego, grabas muchos sonidos diferentes: pasos, explosiones, diálogos, música ambiental, efectos de interfaz. El problema es que **cada audio puede haber sido grabado a un volumen diferente**:

- Un audio de pasos puede estar a **-18 LUFS** (bajo)
- Una explosión puede estar a **-8 LUFS** (muy alto)
- Un diálogo puede estar a **-12 LUFS** (medio)

Cuando los metes en el motor 3D (Unity, Unreal, Godot) y les aplicas **atenuación por distancia**, no funciona bien porque los audios no empiezan desde el mismo punto de volumen.

**Este script resuelve ese problema:** pone todos los audios al mismo nivel de volumen percibido, para que la calibración de distancias sea consistente.

---

## 2. El problema: audios con diferentes volúmenes

Imagina que tienes estos audios para tu juego:

```
Sonido              Volumen actual    Lo que deberían sonar
─────────────────────────────────────────────────────────────
Pasos               ████████░░░░░░    (muy suave)
Espada              ██████████████    (muy fuerte)
Explosión           ████████████████  (demasiado fuerte)
Diálogo "Hola"      ██████████░░░░    (normal)
Música ambiental    ██████░░░░░░░░    (suave)
Interfaz "click"    ████████████░░    (un poco fuerte)
```

**Sin normalizar:** Si pones la distancia de audición a 10 metros en el motor 3D:
- La explosión se escucha a 30 metros (demasiado lejos)
- Los pasos no se escuchan ni a 3 metros (demasiado cerca)
- No puedes encontrar un punto medio que funcione para todos

**Con normalizar:** Todos al mismo volumen, la distancia de 10 metros funciona para todos.

---

## 3. ¿Qué es LUFS?

**LUFS** significa **Loudness Units Full Scale**. Es una medida estándar de **qué tan fuerte suena** un audio para el oído humano.

### ¿Por qué no usar simplemente "volumen"?

Porque el volumen tradicional (dB) mide la **potencia** de la señal, pero el oído humano percibe el volumen de forma diferente:
- Un audio con mucho bajo grave suena más fuerte que uno sin bajo, aunque tengan la misma potencia
- Un audio con muchas pausas suena más suave que uno continuo, aunque el volumen pico sea el mismo

**LUFS mide lo que realmente escuchas**, no lo que el medidor dice.

### La escala LUFS

```
  -6 LUFS  ████████████████  Muy fuerte (clip, distorsión)
 -10 LUFS  ██████████████    Fuerte (diálogos en película)
 -14 LUFS  ████████████      Estándar (videojuegos, streaming)
 -16 LUFS  ██████████        Moderado (juegos AAA, PC)
 -20 LUFS  ████████          Suave (podcasts, radio)
 -24 LUFS  ██████            Muy suave (audio de calidad)
 -70 LUFS                    Silencio
```

**Nota importante:** LUFS es un número **negativo**. -14 es **más fuerte** que -20. A menor número negativo, más fuerte.

---

## 4. Instalación

### Requisitos previos

- Python 3.8 o superior
- pip (el instalador de paquetes de Python)

### Paso 1: Instalar dependencias

Abre una terminal (CMD, PowerShell, o Terminal de VS Code) y ejecuta:

```bash
pip install -r requirements.txt
```

O instala solo lo necesario:

```bash
pip install pyloudnorm soundfile numpy
```

### Paso 2: Verificar que funciona

```bash
python normalize_audio.py --help
```

Si ves la ayuda del script, todo está correcto.

---

## 5. Uso rápido (en 3 pasos)

### Paso 1: Analizar tus audios

```bash
python normalize_audio.py --folder mis_sonidos/ --analyze-only --report analisis.csv
```

Esto te dice qué volumen tiene cada audio **sin modificar nada**.

### Paso 2: Normalizar todos

```bash
python normalize_audio.py --folder mis_sonidos/ --output-folder mis_sonidos_norm/ --target -14
```

Esto crea una carpeta nueva con todos los audios al mismo volumen.

### Paso 3: Verificar el resultado

```bash
python normalize_audio.py --folder mis_sonidos_norm/ --analyze-only
```

Todos los audios deben estar cerca de -14 LUFS.

---

## 6. Modo archivo único

Para normalizar un solo archivo:

```bash
python normalize_audio.py input.wav -o output.wav --target -14
```

### Resultado en pantalla

```
Input:    input.wav
Output:   output.wav
Target:   -14.0 LUFS

  Original:  -18.5 LUFS (-3.2 dBTP)
  Normalized: -14.0 LUFS (-1.0 dBTP)
  Gain:       +4.5 dB

Saved to: output.wav
```

### Qué significa cada línea

| Línea | Significado |
|-------|-------------|
| `Original: -18.5 LUFS` | El audio original era suave (-18.5 es bajo) |
| `Normalized: -14.0 LUFS` | Ahora está al nivel que pediste (-14) |
| `Gain: +4.5 dB` | Se aumentó el volumen 4.5 decibelios |
| `-3.2 dBTP` | El pico más alto del original estaba a -3.2 dB |
| `-1.0 dBTP` | El pico más alto del normalizado está a -1.0 dB (límite seguro) |

---

## 7. Modo carpeta (batch)

Para normalizar muchos archivos a la vez:

### Básico

```bash
python normalize_audio.py --folder sonidos_raw/ --output-folder sonidos_norm/ --target -14
```

### Con opciones adicionales

```bash
python normalize_audio.py \
  --folder sonidos_raw/ \
  --output-folder sonidos_norm/ \
  --target -16 \
  --true-peak -1.0 \
  --recursive \
  --report reporte.csv
```

### Qué hace cada opción

| Opción | Qué hace |
|--------|----------|
| `--folder` | Carpeta con los audios originales |
| `--output-folder` | Carpeta donde se guardan los normalizados |
| `--target -16` | Volumen objetivo (-14, -16, -12, etc.) |
| `--true-peak -1.0` | Límite máximo de pico (evita distorsión) |
| `--recursive` | Busca también en subcarpetas |
| `--report` | Genera un archivo CSV con los resultados |

### Resultado en pantalla

```
Input:     sonidos_raw/
Output:    sonidos_norm/
Target:    -14.0 LUFS
Recursive: Yes
Extensions: .wav, .flac, .ogg, .mp3

Processing 12 file(s)...

  [1/12] footstep_01.wav ... -18.5 -> -14.0 LUFS (gain: +4.5 dB)
  [2/12] footstep_02.wav ... -17.2 -> -14.0 LUFS (gain: +3.2 dB)
  [3/12] explosion_01.wav ... -8.2 -> -14.0 LUFS (gain: -5.8 dB)
  [4/12] dialogue_hello.wav ... -12.0 -> -14.0 LUFS (gain: -2.0 dB)
  ...
  [12/12] ui_click.wav ... -10.5 -> -14.0 LUFS (gain: -3.5 dB)

==================================================
Processed: 12 files
  OK:      12
  Errors:  0
  Gain range: -5.8 to +4.5 dB

Report saved to: reporte.csv
```

---

## 8. Modo análisis (solo leer, no modificar)

Si solo quieres saber qué volumen tienen tus audios **sin cambiar nada**:

```bash
python normalize_audio.py --folder sonidos/ --analyze-only
```

### Resultado

```
Analyzing 6 file(s)...

  [1/6] footstep.wav: -18.5 LUFS, -3.2 dBTP
  [2/6] explosion.wav: -8.2 LUFS, -0.5 dBTP
  [3/6] dialogue.wav: -12.0 LUFS, -2.1 dBTP
  [4/6] music.wav: -14.0 LUFS, -1.0 dBTP
  [5/6] ambient.wav: -30.1 LUFS, -12.0 dBTP
  [6/6] ui_click.wav: -10.5 LUFS, -1.5 dBTP

Summary:
  Files analyzed: 6
  LUFS range:     -30.1 to -8.2
  LUFS spread:    21.9 dB
  Target:         -14.0 LUFS
```

**"LUFS spread: 21.9 dB"** significa que hay una diferencia de casi 22 decibelios entre el más suave y el más fuerte. ¡Eso es mucho! Por eso necesitas normalizar.

---

## 9. Generar reporte CSV

El reporte CSV es un archivo que se puede abrir en Excel, Google Sheets, o cualquier programa de hojas de cálculo.

### Generar reporte al normalizar

```bash
python normalize_audio.py --folder sonidos/ --output-folder sonidos_norm/ --report reporte.csv
```

### Generar reporte solo con análisis

```bash
python normalize_audio.py --folder sonidos/ --analyze-only --report analisis.csv
```

### Formato del reporte

| Campo | Significado |
|-------|-------------|
| `filename` | Nombre del archivo |
| `original_lufs` | Volumen original en LUFS |
| `original_true_peak_dbtp` | Pico máximo original en dBTP |
| `normalized_lufs` | Volumen después de normalizar |
| `normalized_true_peak_dbtp` | Pico máximo después de normalizar |
| `gain_applied_db` | Cuánto se subió (+) o bajó (-) el volumen |
| `duration_sec` | Duración del audio en segundos |
| `sample_rate` | Frecuencia de muestreo (44100, 48000, etc.) |
| `status` | `ok` = éxito, otro = error |

### Ejemplo en Excel

```
filename            original_lufs  normalized_lufs  gain_applied_db  status
footstep_01.wav     -18.5          -14.0            +4.5             ok
explosion_01.wav    -8.2           -14.0            -5.8             ok
dialogue_hello.wav  -12.0          -14.0            -2.0             ok
ambient_wind.wav    -30.1          -14.0            +16.1            ok
```

---

## 10. Targets LUFS recomendados

### Para videojuegos

| Contexto | Target LUFS | Cuándo usarlo |
|----------|-------------|---------------|
| **Móvil / casual** | **-14 LUFS** | La mayoría de juegos móviles |
| **AAA / PC** | **-16 LUFS** | Juegos con más dinámica |
| **Diálogos / voz** | **-12 LUFS** | Voces que necesitan estar presentes |
| **Efectos (SFX)** | **-16 LUFS** | Explosiones, impactos, etc. |
| **Música** | **-14 LUFS** | Banda sonora general |
| **Ambiente** | **-18 LUFS** | Sonidos de fondo, viento, lluvia |

### Ejemplo: Juego móvil

```bash
# Normalizar todo a -14 LUFS (estándar móvil)
python normalize_audio.py --folder sonidos/ --output-folder sonidos_norm/ --target -14
```

### Ejemplo: Juego AAA con categorías

```bash
# Diálogos a -12 (más presentes)
python normalize_audio.py --folder dialogos/ --output-folder dialogos_norm/ --target -12

# Efectos a -16 (más headroom)
python normalize_audio.py --folder sfx/ --output-folder sfx_norm/ --target -16

# Música a -14 (balance general)
python normalize_audio.py --folder music/ --output-folder music_norm/ --target -14

# Ambiente a -18 (más suave)
python normalize_audio.py --folder ambiance/ --output-folder ambiance_norm/ --target -18
```

### Usar presets (atajos)

```bash
# mobile = -14 LUFS
python normalize_audio.py --folder sonidos/ --output-folder norm/ --target mobile

# aaa = -16 LUFS
python normalize_audio.py --folder sonidos/ --output-folder norm/ --target aaa

# dialogue = -12 LUFS
python normalize_audio.py --folder sonidos/ --output-folder norm/ --target dialogue
```

---

## 11. Ejemplos prácticos de videojuegos

### Ejemplo 1: Preparar sonidos para Unity

Tienes una carpeta `Assets/Sounds/raw/` con todos los audios grabados por diferentes personas.

```bash
# 1. Analizar primero para entender el estado actual
python normalize_audio.py --folder Assets/Sounds/raw/ --analyze-only --report before.csv

# 2. Normalizar todos a -14 LUFS
python normalize_audio.py --folder Assets/Sounds/raw/ --output-folder Assets/Sounds/ --target -14

# 3. Verificar que quedaron bien
python normalize_audio.py --folder Assets/Sounds/ --analyze-only --report after.csv
```

### Ejemplo 2: Audios de un asset pack

Descargaste un pack de sonidos y vienen a diferentes volúmenes.

```bash
# Normalizar todo y generar reporte para tu documentación
python normalize_audio.py \
  --folder asset_pack/ \
  --output-folder asset_pack_normalized/ \
  --target -14 \
  --report asset_pack_loudness.csv
```

### Ejemplo 3: Solo analizar antes de integrar

Quieres saber si necesitas normalizar antes de meter los audios al motor.

```bash
python normalize_audio.py --folder sonidos/ --analyze-only

# Si ves "LUFS spread" mayor a 6 dB, necesitas normalizar
# Si es menor a 3 dB, probablemente no hace falta
```

---

## 12. Errores comunes y cómo solucionarlos

### Error: "No audio files found"

**Causa:** No encontró archivos de audio en la carpeta.

**Solución:**
- Verifica que la ruta sea correcta
- Verifica que los archivos tengan extensión `.wav`, `.flac`, `.ogg`, o `.mp3`
- Usa `--extensions` si tus archivos tienen otra extensión

### Error: "read_error" o "write_error"

**Causa:** El archivo está corrupto o no se puede leer/escribir.

**Solución:**
- Verifica que el archivo no esté dañado (abre en un reproductor de audio)
- Verifica que tengas permisos de escritura en la carpeta de salida
- Cierra otros programas que puedan tener el archivo abierto

### Error: "Invalid target"

**Causa:** El valor de `--target` no es válido.

**Solución:**
- Usa un número: `--target -14`
- O usa un preset: `--target mobile`
- Presets disponibles: mobile, aaa, dialogue, sfx, music, quiet

### Los archivos normalizados suenan distorsionados

**Causa:** El audio original estaba demasiado fuerte y al normalizar se recortó.

**Solución:**
- Reduce el `--true-peak`: `--true-peak -2.0` (más conservador)
- Usa un target más bajo: `--target -16` en lugar de `-14`

### Los archivos normalizados suenan muy suaves

**Causa:** El target es muy bajo para tu caso de uso.

**Solución:**
- Usa un target más alto: `--target -12` para voz
- Verifica que el audio original no tenga mucho silencio al inicio/final

---

## 13. Preguntas frecuentes

### ¿Puedo deshacer el normalizado?

No directamente. Por eso es importante:
1. **Siempre** analizar primero con `--analyze-only`
2. **No** sobrescribir los originales (usar `--output-folder` diferente)
3. **Generar** un reporte para documentar qué se hizo

### ¿Cuánto LUFS debo usar?

Para la mayoría de videojuegos: **-14 LUFS**. Si no estás seguro, empieza con -14 y ajusta después.

### ¿Puedo normalizar MP3?

Sí. El script soporta `.wav`, `.flac`, `.ogg`, `.mp3`, `.aiff`.

### ¿Funciona con audio mono y estéreo?

Sí. Funciona con cualquier número de canales.

### ¿Cuánto tiempo tarda?

Depende del tamaño de los archivos. Un archivo de 3 segundos tarda menos de 1 segundo. Una carpeta con 100 archivos de 5 segundos tarda unos 10-20 segundos.

### ¿Necesito instalar algo especial?

Solo `pyloudnorm`, `soundfile` y `numpy`. Todo se instala con:
```bash
pip install -r requirements.txt
```

### ¿Puedo usar esto para normalizar podcast o música?

Sí. Aunque está pensado para videojuegos, funciona para cualquier audio. Para podcast usa `-16 LUFS` (estándar Spotify/Apple Podcasts). Para música usa `-14 LUFS`.

---

## Referencia rápida de comandos

```bash
# Ver ayuda
python normalize_audio.py --help

# Analizar carpeta
python normalize_audio.py --folder sonidos/ --analyze-only

# Normalizar carpeta
python normalize_audio.py --folder raw/ --output-folder norm/ --target -14

# Normalizar con reporte
python normalize_audio.py --folder raw/ --output-folder norm/ --target -14 --report report.csv

# Archivo único
python normalize_audio.py input.wav -o output.wav --target -14

# Usar preset
python normalize_audio.py --folder raw/ --output-folder norm/ --target mobile

# Con true peak más conservador
python normalize_audio.py --folder raw/ --output-folder norm/ --target -14 --true-peak -2.0

# Buscar en subcarpetas
python normalize_audio.py --folder raw/ --output-folder norm/ --target -14 --recursive
```

---

*Creado para Voice Filter — Herramienta de normalización LUFS para audio de videojuegos.*
