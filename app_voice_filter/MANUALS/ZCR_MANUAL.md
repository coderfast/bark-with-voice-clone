# ZCR_MANUAL — Tasa de cruces por cero (zcr.png)

Guia completa: el contador de vibraciones de la onda, de cero a experto.

---

## Tabla de contenidos

1. [Que es?](#1-qué-es)
2. [Analogia: el medidor de vibraciones](#2-analogía-el-medidor-de-vibraciones)
3. [Anatomia: ejes y curva](#3-anatomía-ejes-y-curva)
4. [Como leerlo paso a paso](#4-cómo-leerlo-paso-a-paso)
5. [Patrones tipicos y que significan](#5-patrones-típicos-y-qué-significan)
6. [Ejemplo guiado con el Spy Hunter](#6-ejemplo-guiado-con-el-spy-hunter)
7. [Errores comunes al leerlo](#7-errores-comunes-al-leerlo)
8. [Relacion con las demas graficas](#8-relación-con-las-demás-gráficas)
9. [De la grafica a los parametros del conversor](#9-de-la-gráfica-a-los-parámetros-del-conversor)
10. [Nivel experto: la formula y sus trampas](#10-nivel-experto-la-fórmula-y-sus-trampas)
11. [Ejercicio practico](#11-ejercicio-práctico)
12. [Preguntas frecuentes](#12-preguntas-frecuentes)
13. [Glosario rapido](#13-glosario-rápido)
14. [Chuleta final](#14-chuleta-final)

---

## 1. Que es?

Cada vez que la onda de audio cruza la linea del silencio (de + a - o al reves), suma uno. En un segundo, una nota grave cruza ~200 veces y un platillo decenas de miles. El **ZCR** (Zero Crossing Rate) es ese contador por segundo:

- ZCR **bajo** = vibracion lenta = **grave o silencio**.
- ZCR **alto** = vibracion rapida = **agudo o ruido**.

Es el medidor mas barato de audio: dos lineas de codigo y ya orienta.

```
ZCR bajo (~200 Hz):           ZCR alto (~5000 Hz):
    __    __    __               _  _  _  _  _  _
   /  \  /  \  /  \             / \/ \/ \/ \/ \/
  /    \/    \/    \           /                  \
= NOTA GRAVE                    = NOTA AGUDA O RUIDO
  (bajo, bombo, voz grave)       (platillos, silbidos, "S")
```

---

## 2. Analogia: el medidor de vibraciones

Imagina que cuentas cuantas veces por segundo una cuerda de guitarra cruza una linea imaginaria dibujada en su centro:

- **Cuerda grave (Mi grave):** vibra lenta -> cruza ~80 veces por segundo -> ZCR ~80
- **Cuerda aguda (Mi agudo):** vibra rapida -> cruza ~1.300 veces por segundo -> ZCR ~1.300
- **Cuerda rota (sin afinar):** vibra sin patron -> ZCR erratico

El ZCR no te dice que nota es (para eso esta pitch), te dice **si vibra ordenado y a que velocidad**. Es como mirar una cuerda y adivinar si es grave o aguda sin oirla.

---

## 3. Anatomia: ejes y curva

```
Cruces por segundo (Hz)
    ^
8000|                          /\  /\    (lead agudo, hats)
6000|                         /  \/  \
4000|
2000|  /\  /\  /\  /\  /\  /\  /\  /\  (bajo, riff)
 500|\/  \/  \/  \/  \/  \/  \/  \/
    +------------------------------------------> Tiempo
    0s        40s        80s       120s      160s
```

| Elemento | Que es | Ejemplo en nuestro tema |
|----------|--------|------------------------|
| **Eje horizontal (X)** | Tiempo transcurrido | 0 a ~163 segundos |
| **Eje vertical (Y)** | Cruces por segundo (Hz equivalentes) | Mas arriba = vibracion mas rapida |
| **Nivel bajo y estable** | Notas graves con patron regular | El riff de bajo (70-140 Hz) |
| **Rafagas altas** | Lead agudo, percusion, o ruido | Entradas del lead, hats |
| **Caidas a cero** | Silencio total (sin cruce) | Pausas o puertas de ruido |

---

## 4. Como leerlo paso a paso

### Paso 1: Identifica el nivel base

Mira la linea que mas tiempo se mantiene: ¿esta baja (< 1000 Hz), media (1000-3000 Hz) o alta (> 3000 Hz)?

- **Baja** = el tema es mayormente grave (bajo, bombo, voz grave)
- **Media** = mezcla equilibrada o lead predominante
- **Alta** = mucho agudo o ruido (hats, cimbales, estatica)

### Paso 2: Busca dientes regulares

Los **dientes** son subidas y bajadas que se repiten a intervalos regulares. Cada diente es un golpe o nota con su vibracion:

- **Dientes bajos y regulares** = notas graves marcadas (riff de bajo)
- **Dientes agudos y regulares** = lead agudo o percusion brillante
- **Ancho del diente** = duracion de la nota (mas ancho = nota mas larga)

### Paso 3: Marca lasrafagas

Las **rafagas** son subidas repentinas de ZCR que duran poco:

- **Rafagas cortas** (~50-200 ms) = golpes de percusion, transitorios
- **Rafagas largas** (> 500 ms) = secciones con mas agudo (lead entrando)
- **Rafagas sin patron** = ruido o interferencia

### Paso 4: Busca caidas a cero

Las **caidas a cero** son momentos donde el ZCR toca ~0:

- **Caidas estrechas** (< 100 ms) = silencio entre notas (normal)
- **Caidas anchas** (> 500 ms) = pausa real o break del arreglo
- **Caidas irregulares** = ediciones o cortes en el audio

### Paso 5: Cruza con la frecuencia

ZCR alto + flatness baja = nota aguda real (lead, platillo tonal)
ZCR alto + flatness alta = ruido (estatica, percusion sin tono)

Esta cruzada es la clave para saber si un pico agudo es musica o ruido.

---

## 5. Patrones tipicos y que significan

### Patron A: dientes bajos regulares (nuestro riff)

```
Hz
2000|  /\  /\  /\  /\  /\  /\
 500|\/  \/  \/  \/  \/  \/  \
    +---------------------------------->
= notas graves marcadas (bajo). Cada diente = una nota del riff.
  Tempo estable, interpolacion barata.
```

### Patron B: rafagas altas intercaladas

```
Hz
6000|        /\        /\
4000|       /  \      /  \
2000|  /\  /    \  /\    \  /\
 500|\/  \/      \/  \    \/  \
    +---------------------------------->
= lead agudo que entra y sale. Lasrafagas = frases del lead.
  Con flatness baja = notas agudas reales.
```

### Patron C: meseta alta continua

```
Hz
6000|  --------------------------
4000|  --------------------------
    +---------------------------------->
= ruido sostenido o seccion brillante (hats, estatica).
  flatness alta = NO hay notas que transcribir.
```

### Patron D: caidas a cero

```
Hz
2000|  /\  /\      /\  /\  /\
 500|\/  \/  \    /  \/  \/  \
    0|       +--+  <- silencio digital
    +---------------------------------->
= pausas o silencios. Las caidas a ~0 confirman gate de RMS agresivo.
```

---

## 6. Ejemplo guiado con el Spy Hunter

1. **Abre el zcr.png.** Veras un nivel base bajo con dientes regulares yrafagas ocasionales.

2. **Identifica el nivel base.** Se mantiene bajo (~200-500 Hz) con dientes: son las notas graves del riff (70-140 Hz). Cada diente es un golpe del bajo.

3. **Cuenta dientes en 10 segundos.** Entre 0 y 10 s hay ~30-40 dientes. Eso equivale a ~3-4 dientes por segundo, coherente con corcheas a ~90-100 BPM.

4. **Busca lasrafagas.** Hay subidas repentinas que alcanzan ~3000-4000 Hz: son las entradas del lead o percusion brillante. Si la flatness es baja ahi, son notas agudas reales.

5. **Marca caidas a cero.** Son escasas y estrechas: no hay breaks largos en el tema.

6. **Cruza con flatness.** Donde el ZCR sube y la flatness baja, hay nota aguda real. Donde suben las dos, es ruido.

7. **Conclusion para el conversor:** Los dientes bajos confirman los onsets del riff. Si el conversor falla en detectar un onset, compara con estos dientes para ver si el problema es el audio o el umbral.

---

## 7. Errores comunes al leerlo

### 7.1 Creer que ZCR alto = nota aguda

No siempre. Un ruido de banda ancha (estatica, reverberacion) tambien da ZCR alto. La clave es cruzar con flatness: ZCR alto + flatness baja = nota; ZCR alto + flatness alta = ruido.

### 7.2 Contar rafagas de percusion como tempo

Si hay hats a semicorcheas, el ZCR los muestra como dientes rapidos. El BPM estimado puede ir al doble. Verifica con el ancho de los dientes del riff, no con los hats.

### 7.3 Usarla como detector principal

El ZCR es O(N), barato y robusto, pero da mas falsos positivos que el flux espectral. En el conversor no se usa como detector principal: su papel es **verificacion**. Si un onset del log no tiene diente de ZCR cerca, es sospechoso.

### 7.4 Ignorar el offset de continua

Si la onda no esta centrada en cero (offset DC), el ZCR se infla artificialmente. Esto es raro en audio maduro pero posible en grabaciones crudas. Combina con RMS: silencio real = ZCR erratico + RMS ~0.

### 7.5 Confundir una seno de 3 kHz con ruido a 3 kHz

El ZCR no distingue: ambos dan la misma tasa. Para desempatar, usa flatness o HNR.

---

## 8. Relacion con las demas graficas

| Grafica | Relacion con el ZCR |
|---------|---------------------|
| **flatness** | La pareja de desempate (nota aguda vs ruido) |
| **intensity** | Los dientes de ZCR suelen ir sobre cimas de energia |
| **spec_wb_nb** | Cada raya vertical del wideband deberia tener su diente aqui |
| **pitch_voiced** | Los dientes de ZCR confirman que hay nota real sonando |
| **hnr** | ZCR alto + HNR bajo = ruido; ZCR alto + HNR medio = nota aguda |

---

## 9. De la grafica a los parametros del conversor

| Lectura en la grafica | Parametro del conversor |
|----------------------|------------------------|
| Dientes bajos regulares | Confirman onsets del riff: verificacion del `--onset-hop` |
| Rafagas altas + flatness baja | Notas agudas reales: validan `--hi` |
| Rafagas altas + flatness alta | Ruido: `--min-conf` alto para filtrar |
| Caidas a cero | Silencios: gate de RMS agresivo sin miedo |
| Dientes sin patron | Tempo irregular: acepta quantize suave |

---

## 10. Nivel experto: la formula y sus trampas

### Formula

ZCR = (1/2N) * sum(|signo(x[n]) - signo(x[n-1])|)

Donde:
- N = numero de muestras en la ventana
- signo(x) = +1 si x > 0, -1 si x < 0, 0 si x = 0
- El resultado es la fraccion de cruces por cero

### Fortalezas

- **O(N):** Mas barato que cualquier FFT
- **Sin ventana:** No necesita parametros de ventana como el spectrograma
- **Robusto:** Funciona para segmentar en presencia de ruido

### Debilidades

- **No distingue seno de ruido filtrado:** Una seno de 3 kHz y ruido filtrado a 3 kHz dan el mismo ZCR
- **Offset DC:** Si la onda no esta centrada en cero, el ZCR se infla
- **Dither:** El ruido de cuantificacion infla el ZCR en silencios

### Uso en el proyecto

El ZCR no se usa como detector principal porque el flux espectral da menos falsos positivos en mezclas. Su papel es **verificacion**:

- Si un onset del log no tiene diente de ZCR cerca -> sospechoso
- Si un pico agudo del MIDI no tiene rafaga de ZCR -> fantasma
- Si hay caida a cero + RMS bajo -> silencio confirmado

---

## 11. Ejercicio practico

1. **Estima el nivel base** del ZCR a ojo (bajo/medio/alto).
2. **Cuenta dientes** en un intervalo de 5 segundos y estima el tempo.
3. **Marca las 3rafagas mas altas** y anota sus segundos.
4. **Cruza con flatness** en esos segundos: ¿son notas o ruido?
5. **Busca caidas a cero** y comprueba si coinciden con silencios en el waveform.
6. **Compara los dientes** con las rayas del wideband (spec_wb_nb): ¿coinciden?

---

## 12. Preguntas frecuentes

**¿Sirve para saber el BPM?**
Barato: si los dientes son regulares, si. Pero el wideband es mas preciso para onsets.

**¿Puedo usarlo para separar voces?**
No. El ZCR no distingue frecuencias: un grave y un agudo dan ZCRs distintos pero no dice cual es cual.

**¿Que pasa si el ZCR es erratico?**
Offset DC o ruido de cuantificacion. Combina con RMS para descartar falsos positivos.

**¿Es mejor que el flux espectral?**
No para deteccion de onsets: el flux es mas preciso. El ZCR es mejor para verificacion y segmentacion barata.

**¿Por que no se usa como detector principal en el conversor?**
Porque da mas falsos positivos en mezclas con percusion. El flux espectral es mas robusto.

---

## 13. Glosario rapido

| Termino | Definicion |
|---------|-----------|
| **ZCR** | Zero Crossing Rate: tasa de cruces por cero por ventana |
| **Diente** | Subida-bajada regular del ZCR = una nota con su vibracion |
| **Rafaga** | Subida repentina de ZCR = golpe, lead agudo, o ruido |
| **Offset DC** | Desplazamiento de la onda respecto a cero: infla el ZCR |
| **Flatness** | Planitud espectral: pareja de desempate con el ZCR |
| **Flux espectral** | Variacion del espectro entre ventanas: mejor detector de onsets |

---

## 14. Chuleta final

```
dientes bajos regulares = notas graves, confirman onsets
rafagas altas: con flatness baja = nota aguda; con flatness alta = ruido
caidas a cero = silencios, puerta agresiva sin miedo
verificacion de onsets, no detector principal
ZCR barato O(N) pero no distingue seno de ruido filtrado
```
