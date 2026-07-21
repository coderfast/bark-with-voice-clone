# SPECTROGRAMA_MANUAL.md — Guia Completa para Principiantes

## Que es un Espectrograma

Un **espectrograma** es una imagen que muestra como cambian las frecuencias de un sonido a lo largo del tiempo. Piensa en el como un **mapa de calor del sonido**.

Mientras que un waveform (la onda clasica) solo muestra que tan fuerte es el sonido en cada momento, el espectrograma te dice **que frecuencias componen** ese sonido en cada instante.

---

## Los Tres Ejes

```
    Frecuencia (Hz)
    ↑
    │  ┌─────────────────────────────┐
    │  │  ████░░░░░░████░░░░░░░████  │  ← Alta frecuencia (agudos)
    │  │  ████████░░████████░░██████  │
    │  │  ██████████████████████████  │  ← Media frecuencia (vocales)
    │  │  ██████████████████████████  │
    │  │  ░░░░░░░░░░░░░░░░░░░░░░░░░  │  ← Baja frecuencia (graves)
    │  └─────────────────────────────┘
    └──────────────────────────────→ Tiempo
         0s    1s    2s    3s    4s
```

| Eje | Que representa | Ejemplo |
|-----|---------------|---------|
| **Horizontal (X)** | Tiempo transcurrido | 0s, 1s, 2s, 3s... |
| **Vertical (Y)** | Frecuencia del sonido | 0 Hz (graves) a 20,000 Hz (agudos) |
| **Color/Brillo** | Intensidad o volumen | Mas brillante = mas fuerte esa frecuencia |

---

## Que es la Frecuencia

La frecuencia es **cuantas veces por segundo vibra el aire**. Se mide en **Hercios (Hz)**.

```
Baja frecuencia (100 Hz)     Alta frecuencia (5000 Hz)
~\    /~\    /~\    /~       ~\/\/\/\/\/\/\/\/\/\/\/\
  ~\/    ~\/    ~\/          (vibracion muy rapida)
(vibracion lenta)
= GRAVE                      = AGUDO
= Bombos, bajos              = Silbidos, cimbales
= Voz grave                  = Vocales "S", "T"
```

### Rangos de frecuencia importantes

| Rango | Hz | Que lo produce | Ejemplo |
|-------|----|----------------|---------|
| Sub-graves | 20 - 60 Hz | Bombos, organo pedal | El "boom" que sientes en el pecho |
| Graves | 60 - 250 Hz | Voz masculina, bajo, tom | La potencia de la voz |
| Medios bajos | 250 - 2,000 Hz | Voces, guitarra, piano | La mayoria de lo que escuchas |
| Medios altos | 2,000 - 6,000 Hz | Vocales claras, cuerdas | La inteligibilidad del habla |
| Agudos | 6,000 - 20,000 Hz | Silbidos, cimbales, aire | Los detalles y la "brillantez" |

---

## Como se Lee un Espectrograma

### Regla basica

- **Zona oscura** = No hay sonido ahi (silencio en esa frecuencia)
- **Zona brillante/colorida** = Hay sonido fuerte ahi
- **Linea horizontal** = Un tono que se mantiene (como una nota de piano)
- **Linea vertical** = Un golpe repentino (como un platillo o consonante)

### Ejemplo 1: Un silbido

Un silbido es una nota aguda que se mantiene:

```
Hz
8000 │         ────────────────    ← Linea horizontal = tono constante
4000 │
2000 │
1000 │
     └──────────────────────────→ Tiempo
```

Solo hay energia en una frecuencia alta y se mantiene estable.

### Ejemplo 2: Una voz hablando

La voz es compleja, con armónicos (multiples frecuencias):

```
Hz
8000 │  ░░░░░░░░░░░░░░░░░░░░░░░   ← Armónicos superiores (detalles)
6000 │  ▓▓▓░░░▓▓▓░░░▓▓▓▓░░░▓▓▓
4000 │  ████░░████░░██████░░████   ← Formantes (identifican la vocal)
2000 │  ████████████████████████   ← Fundamental (tono de la voz)
1000 │  ████████████████████████
 500 │  ████████████████████████   ← Bajos de la voz
     └──────────────────────────→ Tiempo
         "H"  "O"  "L"  "A"
```

### Ejemplo 3: Un golpe de bateria (kick drum)

```
Hz
4000 │  │                          ← Impacto repentino (vertical)
2000 │  │
1000 │  │
 500 │  ██
 200 │  █████                       ← Energia concentrada en graves
 100 │  ████████
     └──────────────────────────→ Tiempo
```

Todo ocurre muy rapido y la energia esta en las frecuencias bajas.

### Ejemplo 4: Ruido blanco (estatica de radio)

```
Hz
8000 │  ████████████████████████   ← Energia en TODAS las frecuencias
6000 │  ████████████████████████
4000 │  ████████████████████████
2000 │  ████████████████████████
1000 │  ████████████████████████
 500 │  ████████████████████████
     └──────────────────────────→ Tiempo
```

Color uniforme en todo el espectro = ruido sin estructura musical.

---

## Que Te Indica el Espectrograma

### 1. Que notas o tonos estan sonando

Las **lineas horizontales** representan tonos. Si ves una linea en 440 Hz, es la nota La (A4).

```
Hz
1000 │        ────────────────      ← Primer armonico (880 Hz)
 880 │
 660 │
 440 │  ────────────────────────    ← Fundamental (La = 440 Hz)
     └──────────────────────────→ Tiempo
```

### 2. Si hay armónicos (riqueza del sonido)

Un sonido "puro" (como un diapasón) tiene solo una linea. Un sonido "rico" (como un violín) tiene multiples lineas paralelas:

```
Sonido puro (diapasón):        Sonido rico (violin):
Hz                             Hz
1000 │                         1000 │  ───────────────
 800 │                          800 │  ───────────────
 600 │                          600 │  ───────────────
 400 │  ───────────────         400 │  ───────────────  ← Multiples armonicos
 200 │                          200 │  ───────────────
     └──────────────→              └──────────────→
```

### 3. El volumen relativo

El **brillo o color** indica que tan fuerte es cada frecuencia:

```
Mas brillante = Mas fuerte
Mas oscuro   = Mas suave

██  = fuerte
▓▓  = medio
░░  = suave
    = silencio
```

### 4. Cambios en el tiempo

Puedes ver cuando un sonido empieza, cambia o termina:

```
Hz
4000 │        ▓▓▓▓▓▓▓▓▓▓▓▓        ← Empieza con frecuencias altas
2000 │  ████▓▓████████████▓▓       ← Luego se llenan los medios
1000 │  ████████████████████░░     ← Al final solo quedan los graves
 500 │  ████████████████████░░
     └──────────────────────────→ Tiempo
         Inicio    Cuerpo    Fin
```

---

## Parametros Importantes del Espectrograma

### Resolucion en frecuencia vs tiempo

Hay un compromiso fundamental: no puedes tener precision perfecta en ambas cosas al mismo tiempo.

```
Alta resolucion de frecuencia:     Alta resolucion de tiempo:
(ves bien QUE frecuencias)        (ves bien CUANDO ocurren)

Hz                                Hz
│  ════════════════               │  │  │  │  │  │  │
│  ════════════════               │  │  │  │  │  │  │
│  ════════════════               │  │  │  │  │  │  │
└──────────────────→              └──────────────────→
  (bien definido en Y)              (bien definido en X)
  (borroso en X)                    (borroso en Y)
```

La mayoria de espectrogramas usan un equilibrio (window size de 20-50 ms).

### Escala de color (colormap)

Los colores representan la intensidad en decibelios (dB):

| dB | Que significa | Visual |
|----|--------------|--------|
| 0 dB | Sonido maximo (referencia) | Color mas brillante (amarillo/blanco) |
| -20 dB | 10 veces mas suave | Color medio (verde/amarillo) |
| -40 dB | 100 veces mas suave | Color oscuro (azul/rojo) |
| -60 dB | Casi silencio | Casi negro |
| -80 dB | Silencio practico | Negro |

```
Ejemplo de barra de colores:

██████  0 dB    (blanco/amarillo - muy fuerte)
██████  -20 dB  (amarillo/verde - fuerte)
██████  -40 dB  (verde/azul - suave)
██████  -60 dB  (azul/rojo - muy suave)
██████  -80 dB  (negro - silencio)
```

---

## Espectrograma vs Waveform

| Aspecto | Waveform | Espectrograma |
|---------|----------|---------------|
| Que muestra | Amplitud vs Tiempo | Frecuencia vs Tiempo (con amplitud como color) |
| Que ves | La "forma" de la onda | Las "capas" de frecuencias |
| Para que sirve | Ver volumen, detectar silencios, cortes | Ver contenido tonal, ruido, armónicos |
| Ejemplo | Ver que la voz se hace mas fuerte | Ver que la voz tiene mas agudos en "S" |

### Visualizacion conjunta

```
WAVEFORM (arriba):
Amplitud
  ↑    ╱╲    ╱╲╱╲    ╱╲
  │   ╱  ╲  ╱    ╲  ╱  ╲
  │──╱────╲╱──────╲╱────╲──→ Tiempo

ESPECTROGRAMA (abajo):
Hz
  │  ░░░░░░░░░░░░░░░░░░░░░░
  │  ▓▓▓▓░░░░▓▓▓▓▓░░░▓▓▓▓░░
  │  ██████░░████████░░██████
  │  ████████████████████████
  └──────────────────────────→ Tiempo
     Mismo momento en ambos graficos
```

---

## Casos de Uso Reales

### 1. Analisis de voz

- **Identificar vocales**: cada vocal tiene un patron espectral unico
  - "A" = energia fuerte en 800-1200 Hz
  - "E" = energia en 1800-2500 Hz
  - "I" = energia en 2500-3500 Hz
  - "O" = energia en 400-800 Hz
  - "U" = energia en 300-600 Hz

- **Detectar consonantes**: aparecen como borrones verticales
  - "S" = energia alta (6000-8000 Hz)
  - "T" = golpe vertical repentino
  - "P" = silencio seguido de explosion

### 2. Produccion musical

- Ver si un instrumento esta bien afinado
- Detectar frecuencias problemáticas en una mezcla
- Comparar antes/despues de aplicar efectos (EQ, filtros)

### 3. Deteccion de problemas

- **Ruido**: energia donde no deberia haberla
- **Clip**: la energia "se corta" arriba
- **Feedback**: linea horizontal persistente en frecuencia alta
- **Ronquido**: linea horizontal en frecuencia muy baja (50-100 Hz)

### 4. Comparar audio original vs procesado

```
ORIGINAL:                    DESPUES DE EQ:
Hz                           Hz
│  ████████████████████      │  ░░░░░░░░░░░░░░░░░░░░   ← Graves cortados
│  ████████████████████      │  ░░░░░░░░░░░░░░░░░░░░
│  ████████████████████      │  ████████████████████    ← Medios igual
│  ████████████████████      │  ████████████████████
│  ████████████████████      │  ████████████████████
└──────────────────────→     └──────────────────────→
  (sin filtro)                 (con high-pass filter)
```

---

## Terminos Clave

| Termino | Definicion |
|---------|-----------|
| **Hz (Hercios)** | Unidades de frecuencia (vibraciones por segundo) |
| **dB (Decibelios)** | Unidades de intensidad/volumen |
| **Formante** | Frecuencia resonante que define el timbre (especialmente en voces) |
| **Armonico** | Multiplos de una frecuencia fundamental |
| **Espectro** | Todas las frecuencias presentes en un sonido en un momento dado |
| **FFT** | Fast Fourier Transform - algoritmo que calcula el espectrograma |
| **Window size** | Tamaño del fragmento de audio analizado (afecta resolucion) |
| **Hop size** | Cuanto se avanza entre analisis consecutivos |
| **Colormap** | Paleta de colores usada para representar la intensidad |

---

## Ejercicio Practico

Toma un archivo de audio y hazte estas preguntas al mirar su espectrograma:

1. **Donde hay mas energia?** (graves, medios o agudos)
2. **Hay lineas horizontales claras?** (tonos musicales presentes)
3. **Hay zonas oscuras?** (frecuencias ausentes o filtradas)
4. **Cambian los patrones?** (el sonido evoluciona en el tiempo)
5. **Es uniforme o tiene estructura?** (ruido vs sonido organizado)
