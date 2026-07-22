# WAVE_MANUAL — Cómo interpretar la vista de onda de audio

Guía completa para personas sin conocimientos técnicos sobre cómo leer, entender y sacar partido de la representación visual de un archivo de audio (waveform).

---

## Tabla de contenidos

1. [¿Qué es un waveform?](#1-qué-es-un-waveform)
2. [Anatomía básica de la vista de onda](#2-anatomía-básica-de-la-vista-de-onda)
3. [El eje horizontal: el tiempo](#3-el-eje-horizontal-el-tiempo)
4. [El eje vertical: la amplitud (volumen)](#4-el-eje-vertical-la-amplitud-volumen)
5. [Cómo "leer" un waveform paso a paso](#5-cómo-leer-un-waveform-paso-a-paso)
6. [Patrones típicos y qué significan](#6-patrones-típicos-y-qué-significan)
7. [Comparación visual: antes y después de efectos](#7-comparación-visual-antes-y-después-de-efectos)
8. [Problemas comunes que se ven en el waveform](#8-problemas-comunes-que-se-ven-en-el-waveform)
9. [Espectrograma: la vista complementaria](#9-espectrograma-la-vista-complementaria)
10. [Conceptos de audio explicados visualmente](#10-conceptos-de-audio-explicados-visualmente)
11. [Glosario rápido](#11-glosario-rápido)

---

## 1. ¿Qué es un waveform?

Un **waveform** (forma de onda) es una **imagen que representa el sonido**. Es como una fotografía del movimiento del aire que llega a tu oído cuando escuchas algo.

Imagina que tiras una piedra a un lago y ves las ondas que se forman en el agua. Un waveform de audio es exactamente eso: una representación de las "ondas" que produce el sonido viajando por el aire.

**En términos simples:** Si el audio fuera una montaña rusa, el waveform sería el mapa de esa montaña rusa vista de lado.

---

## 2. Anatomía básica de la vista de onda

Cuando abres un archivo de audio en un programa como Voice Filter, ves una gráfica con:

```
    ▲ Volumen
    │
    │    ╱╲      ╱╲    ╱╲      ╱╲
    │   ╱  ╲    ╱  ╲  ╱  ╲    ╱  ╲
    │──╱────╲──╱────╲╱────╲──╱────╲──  ← Línea central (silencio)
    │        ╲╱      ╲╱    ╲╱
    │
    └──────────────────────────────────▶ Tiempo
          0s      5s      10s
```

| Elemento | Qué es | Ejemplo visual |
|----------|--------|----------------|
| **Línea central** | El silencio (no hay sonido) | Una línea horizontal recta |
| **Picos hacia arriba** | La onda de sonido moviéndose en una dirección | Las montañas de la gráfica |
| **Picos hacia abajo** | La onda de sonida moviéndose en la dirección opuesta | Los valles de la gráfica |
| **Altura de los picos** | Qué tan fuerte es el sonido (volumen) | Montañas altas = fuerte, bajas = suave |
| **Densidad de los picos** | Qué tan complejo/rápido es el sonido | Muchos picos juntos = sonido agudo o complejo |

---

## 3. El eje horizontal: el tiempo

El **eje horizontal** (de izquierda a derecha) representa **el paso del tiempo**.

- **Izquierda** = el inicio del audio
- **Derecha** = el final del audio
- **Cada marca** = un momento específico en el audio (0s, 5s, 10s, etc.)

**Ejemplo práctico:**
Si tu archivo dura 30 segundos, verás marcado desde 0 hasta 30. Si tu cursor está en el segundo 15, estás viendo exactamente la mitad del audio.

```
0s ─────── 5s ─────── 10s ─────── 15s ─────── 20s ─────── 25s ─────── 30s
│Inicio                                               │Mitad           │Final
```

**Consejo:** Puedes hacer clic en cualquier punto del eje temporal para saltar a ese momento del audio.

---

## 4. El eje vertical: la amplitud (volumen)

El **eje vertical** (de abajo a arriba) representa **la amplitud**, que en palabras simples es **el volumen del sonido**.

- **Más arriba/más abajo** = más volumen (más fuerte)
- **Cerca de la línea central** = menos volumen (más suave)
- **En la línea central** = silencio total

```
    ▲
    │  ████  ← Sonido FUERTE (amplitud alta)
    │  ████
────┼──────  ← Silencio (amplitud cero)
    │  ████
    │  ████
    ▼
```

**Regla de oro:**
- Picos **grandes y llenos** = voz fuerte, música con energía
- Picos **pequeños y finos** = voz suave, música tranquila
- **Línea plana** = silencio, pausa, o no hay audio

---

## 5. Cómo "leer" un waveform paso a paso

### Paso 1: Mira el tamaño general

Primero observa la forma general del waveform. ¿Es uniforme o tiene variaciones?

- **Uniforme** (bloques llenos): Probablemente es música con poca dinámica (canciones pop modernas, por ejemplo)
- **Con variaciones** (picos y valles alternados): Probablemente es voz, música clásica, o algo con contrastes de volumen

### Paso 2: Identifica las partes altas y bajas

- Las **partes más altas** (más volumen) suelen ser los coros, partes fuertes, o momentos épicos
- Las **partes más bajas** (menos volumen) suelen ser las intro, intermedios, o partes suaves

### Paso 3: Busca los silencios

Los **espacios vacíos** (línea plana) indican pausas o silencio. Son muy útiles para:
- Encontrar dónde termina una frase
- Detectar cortes o ediciones
- Localizar problemas de grabación

### Paso 4: Compara secciones

Mira si alguna parte del audio se "ve" diferente a las demás. Esto puede indicar:
- Un cambio de volumen
- Un efecto aplicado
- Un error de grabación
- Una edición

---

## 6. Patrones típicos y qué significan

### 6.1 Voz hablada (locución, podcast, audiolibro)

```
    ╱╲  ╱╲╱╲  ╱╲  ╱╲╱╲╱╲  ╱╲
───╱──╲╱────╲╱──╲╱──────╲╱──╲───
          ╲  ╲╱  ╲╱        ╲╱
```

**Características:**
- **Grupos de picos separados por valles**: Cada grupo es una palabra o frase
- **Espacios entre grupos**: Pausas naturales al hablar
- **Altura variable**: Las vocales suenan más fuerte que las consonantes
- **Patrón "dentado"**: Es típico del habla, con picos irregulares

**Ejemplo de lo que ves:**
```
"Hola, ¿cómo estás?" → [picos] [valle] [picos] [valle] [picos]
```

### 6.2 Música pop/rock/moderna

```
██████████████████████████████████████
██████████████████████████████████████
██████████████████████████████████████
```

**Características:**
- **Bloques sólidos y uniformes**: La música está "comprimida" (todas las partes tienen volumen similar)
- **Poca variación en altura**: Es típico de la música moderna (fenómeno de la "guerra de los loudness")
- **Difícil distinguir instrumentos**: Todo se ve como un bloque

### 6.3 Música clásica/orquestal

```
        ╱╲
    ╱╲╱╱  ╲╲╱╲
───╱────────╲────╲──╱╲╱╲╱╲╱╲────
                ╲╱              ╲╱
```

**Características:**
- **Mucha variación de dinámica**: Picos muy altos (tutti) y muy bajos (solo de violín)
- **Forma de "montañas y valles"**: Refleja la expresividad de la música
- **Silencios dramáticos**: Líneas planas que son pausas intencionales
- **Gradualidad**: Los cambios de volumen son suaves (crescendos, decrescendos)

### 6.4 Efectos especiales

**Reverb (reverberación):**
```
╱╲╱╲╱╲╱╲╱╲╱╲    ╱╲╱╲╱╲╱╲╱╲╱╲
            ╲╱╲╱              ╲╱╲╱╲╱╲
                                (cola larga)
```
Los picos "se estiran" hacia la derecha, creando una cola que se desvanece.

**Delay (eco):**
```
╱╲    ╱╲    ╱╲
  ╲╱    ╲╱    ╲╱
```
Los mismos picos se repiten con menor intensidad.

**Distorsión:**
```
████████████████████
████████████████████
```
Los picos se "aplanan" por arriba y por abajo (parecen recortados).

---

## 7. Comparación visual: antes y después de efectos

### Volumen (gain)

**Antes (nivel bajo):**
```
      ╱╲
    ╱╱  ╲╲
───╱──────╲───
```

**Después (volumen +6dB):**
```
    ╱╲
  ╱╱  ╲╲
╱╱──────╲╲╱╲
╲        ╲╱ ╲
```

Los picos se hacen más altos. ¡Cuidado de que no se "recorten" por arriba!

### Ecualización (EQ)

**Antes (sin EQ):**
```
███████████████████
```

**Después (bass boost):**
```
██╲╲██╲╲██╲╲██╲╲██
```

Los graves se hacen más prominentes, los agudos menos. El waveform cambia de "bloque sólido" a "picos más definidos".

### Compresión

**Antes (sin comprimir):**
```
        ╱╲
    ╱╲╱╱  ╲╲╱╲
───╱────────╲────╲──╱╲╱╲╱╲╱╲────
                ╲╱              ╲╱
```

**Después (comprimido):**
```
      ╱╲╱╲╱╲╱╲╱╲
─────╱──────────╲───╱╲╱╲╱╲╱╲─────
                   ╲╱          ╲╱
```

Los picos altos bajan y los bajos suben. Todo se vuelve más uniforme.

### Normalización

**Antes (nivel bajo):**
```
      ╱╲
    ╱╱  ╲╲
───╱──────╲───
```

**Después (normalizado a 0dB):**
```
    ╱╲
  ╱╱  ╲╲
╱╱──────╲╲╱╲
╲        ╲╱ ╲
```

Similar al volumen, pero ajustado automáticamente al nivel óptimo sin distorsión.

---

## 8. Problemas comunes que se ven en el waveform

### 8.1 Clipping (recorte / distorsión por exceso)

```
██████████████████
██████████████████
```

**Qué se ve:** Los picos están "cortados" por arriba y por abajo, como si alguien los hubiera pasado por una guillotina.

**Qué significa:** El audio superó el nivel máximo permitido. Suena distorsionado, como un radio dañado.

**Solución:** Reducir el volumen (gain) o aplicar un compresor con headroom.

### 8.2 Silencio innecesario

```
────────────────────────────────────────────────╱╲╱╲╱╲╱╲╱╲
```

**Qué se ve:** Una línea plana larga al inicio o al final.

**Qué significa:** Hay silencio desperdiciado. El audio real empieza tarde.

**Solución:** Recortar (trim) el silencio innecesario.

### 8.3 Ruido de fondo

```
▓▓▓╱╲╱╲▓▓▓╱╲╱╲▓▓▓
▓▓╱╲╱╲╱╲▓▓╱╲╱╲╱╲▓▓
```

**Qué se ve:** Una "niebla" de picos pequeños donde debería haber silencio.

**Qué significa:** Hay ruido ambiental, zumbido eléctrico, o siseo grabado junto con el audio.

**Solución:** Aplicar un gate (puerta de ruido) o un filtro de paso alto.

### 8.4 Pops y clics

```
╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲  ╱╲╱╲╱╲╱╲╱╲╱╲
                     │
```

**Qué se ve:** Un pico inesperado, muy alto, de duración muy corta.

**Qué significa:** Un "pop" del micrófono, un clic digital, o un error de grabación.

**Solución:** Edición manual o uso de un filtro de paso alto.

### 8.5 Niveles inconsistentes

```
╱╲╱╲╱╲╱╲╱╲╱╲                ╱╲╱╲╱╲╱╲╱╲╱╲╱╲
              ╲╱╲╱╲╱╲╱╲╱╲╱╱╱
```

**Qué se ve:** Una parte del audio es mucho más fuerte que otra sin razón aparente.

**Qué significa:** El micrófono se movió, la distancia cambió, o los niveles de grabación no fueron consistentes.

**Solución:** Normalización por bloques o compresión.

---

## 9. Espectrograma: la vista complementaria

Debajo del waveform, Voice Filter muestra un **espectrograma**. Este es un mapa de color que muestra **qué frecuencias** (tonos) están presentes en cada momento.

```
Frecuencia
alta  │  ▪              ▪▪▪▪▪
      │  ▪▪            ▪▪▪▪▪▪▪▪
      │  ▪▪▪          ▪▪▪▪▪▪▪▪▪▪
      │  ▪▪▪▪        ▪▪▪▪▪▪▪▪▪▪▪▪
baja  │  ▪▪▪▪▪▪    ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
      └──────────────────────────────▶ Tiempo
```

### Cómo leer los colores

| Color | Significado |
|-------|-------------|
| **Negro** | Silencio: no hay energía en esa frecuencia |
| **Azul** | Energía baja: sonido suave o lejano |
| **Verde** | Energía media: sonido moderado |
| **Amarillo** | Energía alta: sonido fuerte |
| **Rojo** | Energía muy alta: sonido muy fuerte o pico |

### Qué buscar en el espectrograma

**Voz humana:**
```
Frecuencia
  8kHz │                    ▪▪▪▪▪▪▪
  4kHz │  ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
  2kHz │  ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
  1kHz │  ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
  500Hz│  ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
       └──────────────────────────────▶ Tiempo
```
- Bandas horizontales = armónicos de la voz
- Se ve como "estratos" apilados

**Batería/percusión:**
```
Frecuencia
  8kHz │     ▪           ▪           ▪
  4kHz │     ▪           ▪           ▪
  2kHz │     ▪           ▪           ▪
  1kHz │  ▪  ▪        ▪  ▪        ▪  ▪
  500Hz│  ▪  ▪        ▪  ▪        ▪  ▪
       └──────────────────────────────▶ Tiempo
```
- Líneas verticales = golpes repentinos
- Sin持续时间: son muy breves

**Ruido de fondo:**
```
Frecuencia
  8kHz │░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  4kHz │░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  2kHz │░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  1kHz │░░░░░░░░░░░░░░░░░░░░░░░░░░░░
  500Hz│░░░░░░░░░░░░░░░░░░░░░░░░░░░░
       └──────────────────────────────▶ Tiempo
```
- "Niebla" de color uniforme en todas las frecuencias = ruido constante (siseo, ventilador, etc.)

---

## 10. Conceptos de audio explicados visualmente

### 10.1 Amplitud (volumen)

```
Bajo volumen:          Alto volumen:

      ╱╲                      ╱╲
    ╱╱  ╲╲                  ╱╱  ╲╲
───╱──────╲───         ╱╲╱╱──────╲╲╱╲
                            ╲    ╲╱  ╲
```

**En palabras simples:** Cuánto se "mueve" el aire. Más alto = más fuerte.

### 10.2 Frecuencia (tono)

```
Frecuencia baja (graves):        Frecuencia alta (agudos):

╱╲                            ╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲
  ╲╱                        ╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲
    ╲╱
      ╲╱
```

**En palabras simples:**
- **Graves** (bass): Ondas anchas y lentas (bombo, bajo, voz grave)
- **Agudos** (treble): Ondas estrechas y rápidas (platillos, silbidos, "S" de la voz)

### 10.3 Rango dinámico

```
Rango DINÁMICO (mucho contraste):        Rango COMPRIMIDO (poco contraste):

        ╱╲                                         ╱╲
    ╱╲╱╱  ╲╲╱╲                              ─────╱──╲─────
───╱────────╲────╲──╱╲╱╲╱╲╱╲────           ─────╱──╲─────
                ╲╱              ╲╱                 ╲╱
```

**En palabras simple:** La diferencia entre lo más suave y lo más fuerte.
- **Rango dinámico:** Música clásica, jazz, podcasts naturales
- **Rango comprimido:** Pop moderno, anuncios, radio

### 10.4 Envolvente (ADSR)

```
                    ┌──────────┐ ← Sustain (sostenido)
                   ╱│          │╲
                  ╱ │          │ ╲
                 ╱  │          │  ╲
Attack          ╱   │          │   ╲  Release
(ataque)  ╱────────┘          └────────╲
─────────╱                              ╲────────
Decay    │                              │
(decaimiento)                            │
```

Cada sonido tiene una "forma de vida":
- **Attack:** Cómo empieza (rápido = percusión; suave = violín)
- **Decay:** Cómo baja después del inicio
- **Sustain:** Cómo se mantiene mientras suena
- **Release:** Cómo termina cuando se deja de tocar

### 10.5 Stereo (estéreo)

Si tu audio tiene dos canales (izquierda y derecha), verás **dos waveforms apilados**:

```
Canal Izquierdo (L):
╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲

Canal Derecho (R):
╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲
```

Si los dos se ven iguales = el audio es **mono** (igual en ambos oídos).
Si son diferentes = el audio tiene **efecto estéreo** (diferente en cada oído).

---

## 11. Glossario rápido

| Término | Definición simple |
|---------|-------------------|
| **Amplitude** | El "tamaño" de la onda. Más alto = más fuerte. |
| **Clipping** | Cuando el audio se pasa del máximo y se distorsiona. Se ve como picos "cortados". |
| **dB (decibelios)** | Unidad de medida del volumen. 0 dB = máximo sin distorsión. |
| **EQ (Ecualización)** | Ajustar graves, medios y agudos por separado. |
| **Frecuencia** | Qué tan rápido vibra el sonido. Grave = lento, agudo = rápido. |
| **Gain** | El nivel de señal. Básicamente "volumen de entrada". |
| **Peak** | El punto más alto de la onda (momento de mayor volumen). |
| **Silencio** | Línea plana en el waveform. No hay sonido. |
| **Spectrogram** | Mapa de colores que muestra qué frecuencias hay en cada momento. |
| **Waveform** | La gráfica de la onda de audio (lo que ves arriba del espectrograma). |

---

## Consejos finales

1. **No necesitas ser experto.** Solo con mirar el waveform puedes detectar si hay silencios innecesarios, si el volumen es muy bajo, o si hay partes que suenan diferente.

2. **El waveform es tu aliado visual.** Si algo "se ve raro", probablemente "suena raro". Confía en tus ojos.

3. **Compara antes y después.** Cuando apliques efectos, siempre compara el waveform original con el modificado. Si los picos están recortados (clipping), reduce el volumen.

4. **El espectrograma complementa al waveform.** El waveform te dice "cuánto" (volumen); el espectrograma te dice "qué" (frecuencias/tonos).

5. **Practica.** Abre un archivo de audio, míralo, escúchalo, y trata de conectar lo que ves con lo que oyes. Poco a poco tus ojos aprenderán a "leer" el sonido.

---

*Manual creado para Voice Filter. Para preguntas sobre efectos específicos de audio, consulta la documentación de la aplicación.*
