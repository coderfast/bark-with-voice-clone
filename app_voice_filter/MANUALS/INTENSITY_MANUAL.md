# INTENSITY_MANUAL — Contorno de intensidad (intensity.png)

Guia completa: el termometro del volumen a lo largo del tema, de cero a experto.

---

## Tabla de contenidos

1. [Que es?](#1-qué-es)
2. [Analogia: el termometro del sonido](#2-analogía-el-termómetro-del-sonido)
3. [Anatomia: ejes y curva](#3-anatomía-ejes-y-curva)
4. [Como leerlo paso a paso](#4-cómo-leerlo-paso-a-paso)
5. [Patrones tipicos y que significan](#5-patrones-típicos-y-qué-significan)
6. [Ejemplo guiado con el Spy Hunter](#6-ejemplo-guiado-con-el-spy-hunter)
7. [Errores comunes al leerlo](#7-errores-comunes-al-leerlo)
8. [Relacion con las demas graficas](#8-relación-con-las-demás-gráficas)
9. [De la grafica a los parametros del conversor](#9-de-la-gráfica-a-los-parámetros-del-conversor)
10. [Nivel experto: como se calcula y sus limites](#10-nivel-experto-cómo-se-calcula-y-sus-límites)
11. [Ejercicio practico](#11-ejercicio-práctico)
12. [Preguntas frecuentes](#12-preguntas-frecuentes)
13. [Glosario rapido](#13-glosario-rápido)
14. [Chuleta final](#14-chuleta-final)

---

## 1. Que es?

La intensidad es la **curva del volumen percibido** instante a instante, medida en decibelios (dB). Si el waveform es la foto completa de la onda (con sus subidas y bajadas detalladas), la intensidad es el **termometro**: una sola linea que resume cuanta presion sonora hay en cada momento.

No te dice que nota suena (eso es pitch), ni que frecuencias hay (eso es el espectrograma). Te dice **cuanto volumen** tiene cada instante: donde hay forte, donde piano, donde silencio.

```
dB
 50 |    /\      /\      /\
 40 |   /  \    /  \    /  \
 30 |--/----\--/----\--/----\--  <- nivel medio
 20 |        \/      \/      \/
 10 |
    +----------------------------------> Tiempo
```

---

## 2. Analogia: el termometro del sonido

Imagina que cuelgas un termometro en una habitacion, pero en lugar de medir temperatura, mide **cuanto ruido** hace cada momento. El termometro no sabe si el ruido viene de una guitarra, una voz o una explosion: solo sabe si sube o baja.

- **Aguja arriba** = la habitacion esta ruidosa (forte)
- **Aguja abajo** = la habitacion esta tranquila (piano)
- **Aguja en cero** = silencio total

La intensidad es ese termometro aplicado a tu archivo de audio: una lectura limpia y continua del volumen, sin distracciones.

---

## 3. Anatomia: ejes y curva

```
dB (intensidad)
    ^
 60 |
 50 |        /\          /\
 40 |  /\   /  \   /\  /  \
 30 |\/  \_/    \_/  \/    \/
 20 |                         \
 10 |                          \___
    +------------------------------------------> Tiempo
    0s        40s        80s       120s      160s
```

| Elemento | Que es | Ejemplo en nuestro tema |
|----------|--------|------------------------|
| **Eje horizontal (X)** | Tiempo transcurrido | 0 a ~163 segundos |
| **Eje vertical (Y)** | Intensidad en dB | Mas arriba = mas fuerte |
| **Linea continua** | Volumen percibido por ventana (~100 ms) | El "termometro" en accion |
| **Cimas locales** | Momentos mas fuertes (fortes, acentos) | Picos del riff |
| **Valles locales** | Momentos mas suaves (pianos, pausas) | Pausas entre frases |
| **Pendiente ascendente** | Crescendo (sube el volumen) | Entrada de instrumento |
| **Pendiente descendente** | Decrescendo/fade-out (baja el volumen) | Final del tema |

---

## 4. Como leerlo paso a paso

### Paso 1: Localiza el nivel medio

Mira la linea general: ¿esta alta (> 40 dB), media (20-40 dB) o baja (< 20 dB)?

- **Alta y estable** = tema con energia constante (pop, rock, chiptune en loop)
- **Media con variaciones** = tema con dinamica (musica clasica, jazz)
- **Baja** = tema suave o grabacion lejana

### Paso 2: Identifica las cimas (picos)

Las **cimas** son los momentos mas fuertes del tema. Marca sus segundos:

- ¿Son regulares? (riff en loop, percusion constante)
- ¿Son irregulares? (frases con acentos variables)
- ¿Son todos iguales? (tema comprimido) ¿O hay unos mas altos que otros? (dinamica)

### Paso 3: Identifica los valles

Los **valles** son los momentos mas suaves. Pueden ser:

- **Valles estrechos** (~0.1-0.3 s): pausas entre notas o frases (normales)
- **Valles anchos** (> 1 s): secciones de transicion o silencios largos
- **Valles profundos** (casi silencio): fronteras de seccion, breaks

### Paso 4: Busca patrones temporales

- ¿Los picos se repiten a intervalos regulares? = Tempo estable (candidato a loop)
- ¿Hay escalones? = Cambio de seccion (entra/sale instrumento)
- ¿Hay una tendencia general? = Fade-in (sube), fade-out (baja), plano (constante)

### Paso 5: Marca las anomalias

- **Picos inesperados** = golpes, pops, o entradas repentinas
- **Caidas bruscas** = cortes, ediciones, o silencios forzados
- **Deriva lenta** = cambio gradual de arreglo o efecto de compresion

---

## 5. Patrones tipicos y que significan

### Patron A: dientes regulares (nuestro caso)

```
dB
 50 |  /\  /\  /\  /\  /\  /\
 40 |\/  \/  \/  \/  \/  \/  \
 30 |
    +---------------------------------->
= riff continuo con acentos regulares. Cada diente = un golpe del riff.
  El tempo es estable y el arreglo no cambia.
```

**Que significa:** Tema en loop con energia constante. Ideal para transcribir:
el volumen no distrae y los acentos son predecibles.

### Patron B: escalones de seccion

```
dB
 50 |            +----------+
 40 |  ----------+          +----------
 30 |
    +---------------------------------->
    intro      verso       estribillo
= entra un instrumento (o se hace mas fuerte) y se mantiene.
  Cada escalon = cambio de arreglo.
```

### Patron C: valles profundos aislados

```
dB
 50 |\/\/\/\    \/\/\/\/\/\/\/\
 40 |      \  /
 30 |       \/  <- pausa o break
    +---------------------------------->
= respirio del arreglo o transicion dramatica. Los valles anchos son
  fronteras naturales para cortar el tramo de conversion.
```

### Patron D: fade-out gradual

```
dB
 50 |\
 40 | \
 30 |  \
 20 |   \
 10 |    \___________
    +---------------------------------->
= el tema se desvanece. La ultima parte tiene poca energia: el detector
  de pitch fallara aqui. Corta antes del fade.
```

### Patron E: bloque solido comprimido

```
dB
 50 |---------------------------
 40 |---------------------------
    +---------------------------------->
= tema comprimido (pop moderno, masterizacion agresiva). Poca dinamica,
  todo al mismo volumen. Distinguir secciones por aqui es casi imposible.
```

---

## 6. Ejemplo guiado con el Spy Hunter

1. **Abre el intensity.png.** Veras una linea con dientes regulares a lo largo de los ~163 s.

2. **Mira el nivel general.** Se mantiene alto con valles ritmicos: el riff no descansa. Esto confirma que es un tema de accion continua (Spy Hunter = persecucion).

3. **Cuenta los dientes en 10 segundos.** Entre 0 y 10 s hay ~15-20 dientes. Eso equivale a un acento cada ~0.5-0.7 s, coherente con corcheas a ~90-100 BPM.

4. **Busca cambios de nivel.** Alrededor de 90 s hay un escalon (el puente: el lead cambia de patron). Despues de 112 s vuelve el nivel alto (el riff original).

5. **Marca valles profundos.** Son escasos: no hay breaks largos. Esto confirma que el tema es continuo, sin pausas que filtrar.

6. **Compara con el pitch_voiced.** Los pocos valles de intensidad coinciden con las caidas de voicing en 65-100 s: donde baja el volumen, el detector de pitch duda.

7. **Conclusion para el conversor:** El tramo 0-60 s tiene intensidad alta y estable -> candidato ideal. El tramo 65-100 s tiene valles -> evitalo o sube `--min-conf`.

---

## 7. Errores comunes al leerlo

### 7.1 Confundir intensidad con pitch

La intensidad dice **cuanto** suena, no **que** suena. Un bajo fuerte y un lead agudo pueden tener la misma intensidad pero notas completamente distintas. Para notas: pitch_voiced o CQT.

### 7.2 Creer que los picos son notas

Un pico de intensidad puede ser un golpe de bateria (sin nota), un pop del microfono (sin musica), o un acorde (varias notas). La intensidad no distingue: solo mide volumen.

### 7.3 Ignorar la escala dB

El eje es logaritmico: 3 dB mas es el doble de energia pero apenas "un poco mas fuerte" al oido. No esperes que un pico de 6 dB sobre el nivel medio signifique el doble de volumen percibido.

### 7.4 Usarla para separar voces

Un bajo fuerte tapa un lead suave en esta curva, aunque ambos existan. La intensidad **no separa voces**: para eso usa mel (franjas de frecuencia) o `--xover`.

### 7.5 Cortar por valles minimos

No todos los valles son fronteras de seccion. Los valles estrechos (~0.1 s) son pausas normales entre notas. Solo los valles anchos (> 0.5 s) son candidatos a corte.

---

## 8. Relacion con las demas graficas

| Grafica | Relacion con la intensidad |
|---------|---------------------------|
| **waveform** | El termometro frente a la foto: mismos picos, lectura mas limpia |
| **pitch_voiced** | Los valles de intensidad suelen coincidir con huecos de voicing |
| **selfsim** | Los escalones de intensidad confirman las fronteras de seccion |
| **flatness** | Donde la intensidad cae, la flatness puede subir (silencio ruidoso) |
| **hnr** | Valles de intensidad sobre picos de HNR bajo = golpes de percusion |
| **zcr** | Cada diente de intensidad deberia tener su diente de cruces por cero |

---

## 9. De la grafica a los parametros del conversor

| Lectura en la grafica | Parametro del conversor |
|----------------------|------------------------|
| Dientes regulares | Acentos -> `--normalize-vel` para mapear a velocities MIDI |
| Valles profundos anchos | Fronteras de seccion: corta el tramo por ahi |
| Nivel medio alto y estable | `--min-conf` bajo (0.15): conversion fiable |
| Caida gradual (fade) | Corta antes del fade: el voicing caera |
| Bloque comprimido | La intensidad no ayuda a segmentar: usa selfsim |
| Valles estrechos periodicos | Percusion entre notas: `filter_short_notes` los entierra |

---

## 10. Nivel experto: como se calcula y sus limites

### Calculo

La intensidad se calcula con una ventana deslizante de ~100 ms:

1. Se toma un fragmento de audio (~100 ms = ~4.410 muestras a 44.1 kHz)
2. Se calcula la energia RMS: `sqrt(sum(x^2)/N)`
3. Se convierte a dB: `20*log10(RMS)`
4. Se avanza la ventana (tipicamente 10 ms) y se repite
5. El resultado es una curva suave que representa el volumen percibido

### Limites importantes

- **No distingue voces:** Un bajo fuerte y un lead suave dan la misma intensidad si suman la misma energia. La separacion es espectral (`--xover`, mel), no por volumen.
- **No distingue frecuencias:** Un bombo grave y un platillo agudo a la misma intensidad dB suenan muy distinto al oido. Por eso existe la escala Mel.
- **Percepcion logaritmica:** 3 dB mas = doble energia pero apenas "un poco mas fuerte". La relacion entre dB y volumen percibido no es lineal.
- **Ventana de 100 ms:** No detecta transitorios de menos de ~50 ms. Para ataques mas finos, usa el wideband (spec_wb_nb).

### Uso en el proyecto

El conversor usa la envolvente de energia (misma idea que la intensidad) para:
- **Gate de RMS:** Umbral de 0.01 para descartar silencios
- **Segmentacion por energia:** Detectar tramos con senal vs sin ella
- **Confianza de pitch:** La energia influye en si el detector "confia" en la nota

---

## 11. Ejercicio practico

1. **Estima el nivel medio** a ojo y clasificalo (alto/medio/bajo).
2. **Cuenta los dientes** en un intervalo de 10 segundos y estima el tempo.
3. **Localiza los 3 valles mas profundos** y anota sus segundos.
4. **Cruza con pitch_voiced:** ¿Esos valles coinciden con caidas de voicing?
5. **Elige el mejor tramo de 20 s** basandote solo en intensidad (alto y estable).
6. **Compara tu eleccion** con la del selfsim: ¿coinciden?

---

## 12. Preguntas frecuentes

**¿Sirve para saber el BPM?**
No directamente. Los dientes marcan acentos, pero el tempo real lo da el ancho de los dientes del ZCR o las rayas del wideband.

**¿Puedo usarla para separar voces?**
No. Un bajo fuerte tapa un lead suave. Para separar voces, usa mel o `--xover`.

**¿Que pasa si la curva es plana?**
Tema comprimido o sin dinamica. La intensidad no ayuda a segmentar: usa selfsim o MFCC.

**¿Los dB son los mismos que en un ecualizador?**
Si y no: ambos usan decibelios, pero la intensidad mide el nivel global por ventana, mientras que un EQ ajusta frecuencias especificas.

**¿Por que a veces la intensidad sube pero el audio no suena mas fuerte?**
Porque la percepcion depende de la frecuencia: un aumento de graves suena mas que uno de agudos, aunque ambos sumen los mismos dB.

---

## 13. Glosario rapido

| Termino | Definicion |
|---------|-----------|
| **Intensidad** | Nivel de presion sonora percibido, en dB por ventana |
| **dB (decibelios)** | Unidad logaritmica del volumen. 0 dB = referencia; negativos = mas suave |
| **RMS** | Root Mean Square: raiz cuadrada de la media de la energia |
| **Forte** | Momento fuerte del tema (pico de intensidad) |
| **Piano** | Momento suave del tema (valle de intensidad) |
| **Crescendo** | Aumento gradual de volumen (pendiente ascendente) |
| **Decrescendo** | Disminucion gradual de volumen (pendiente descendente) |
| **Gate** | Puerta de ruido: silencia por debajo de un umbral de energia |

---

## 14. Chuleta final

```
dientes regulares = acentos del riff -> velocities MIDI
valles profundos anchos = fronteras de seccion, corta por ahi
nivel alto y estable = --min-conf 0.15, conversion fiable
fade-out = corta antes, el voicing caera
no separa voces: un bajo fuerte tapa al lead aqui
dB es logaritmico: 3 dB = doble energia, apenas mas fuerte
```
