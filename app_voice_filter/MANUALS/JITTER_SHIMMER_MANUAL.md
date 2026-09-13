# JITTER_SHIMMER_MANUAL — Microvariaciones de pitch y amplitud (jitter_shimmer.png)

Guia completa: el "tembleque" que delata si canta una persona o una maquina, de cero a experto.

---

## Tabla de contenidos

1. [Que miden?](#1-qué-miden)
2. [Analogia: el metronomo tembloroso](#2-analogía-el-metronomo-tembloroso)
3. [Anatomia: dos curvas superpuestas](#3-anatomía-dos-curvas-superpuestas)
4. [Como leerlo paso a paso](#4-cómo-leerlo-paso-a-paso)
5. [Patrones tipicos y que significan](#5-patrones-típicos-y-qué-significan)
6. [Ejemplo guiado con el Spy Hunter](#6-ejemplo-guiado-con-el-spy-hunter)
7. [Errores comunes al leerlo](#7-errores-comunes-al-leerlo)
8. [Relacion con las demas graficas](#8-relación-con-las-demás-gráficas)
9. [De la grafica a los parametros del conversor](#9-de-la-gráfica-a-los-parámetros-del-conversor)
10. [Nivel experto: la formula y el vibrato](#10-nivel-experto-la-fórmula-y-el-vibrato)
11. [Ejercicio practico](#11-ejercicio-práctico)
12. [Preguntas frecuentes](#12-preguntas-frecuentes)
13. [Glosario rapido](#13-glosario-rápido)
14. [Chuleta final](#14-chuleta-final)

---

## 1. Que miden?

- **Jitter:** cuanto tiembla la **afinacion** de un ciclo al siguiente (¿la nota vibra en altura?).
- **Shimmer:** cuanto tiembla el **volumen** de un ciclo al siguiente.

```
Jitter (afinacion):              Shimmer (volumen):
    __    __    __                   __    __    __
   /  \  /  \  /  \                 /  \  /  \  /  \
  /    \/    \/    \               /    \/    \/    \
 /  ^   ^   ^       \             /  ^   ^   ^       \
   | +-| +-|           <- variacion de altura          <- variacion de amplitud
```

Una voz humana tiene ambos (nadie clava el pitch al hercio); un chip de NES, casi cero: sus osciladores son matematicamente perfectos.

- **Valores bajos y planos** = **maquina** (sintetizador, chiptune)
- **Valores altos** = **humano** (o vibrato/efectos intencionales)

---

## 2. Analogia: el metronomo tembloroso

Imagina un metronomo:

- **Metronomo perfecto (maquina):** cada clic sale exactamente al mismo tiempo y al mismo volumen. Jitter ~0, Shimmer ~0.
- **Metronomo humano:** cada clic sale "mas o menos" al tiempo, y algunos suenan un poco mas fuertes que otros. Jitter > 0, Shimmer > 0.
- **Metronomo con vibrato:** los clics son regulares pero con una oscilacion periodica. Jitter/Shimmer altos pero sanos.

La pregunta que responden es: ¿este sonido lo hace una maquina o un ser vivo?

---

## 3. Anatomia: dos curvas superpuestas

```
Variacion (%)
    ^
2.0 |  /\        /\        /\    (vibrato humano, picos)
1.5 | /  \      /  \      /  \
1.0 |/    \    /    \    /    \
0.5 |      \  /      \  /      \
0.1 |-------\--------\--------\---  (maquina: casi cero)
    +------------------------------------------> Tiempo
    0s        40s        80s       120s      160s
    ----- jitter (afinacion)
    ----- shimmer (volumen)
```

| Elemento | Que es | Ejemplo en nuestro tema |
|----------|--------|------------------------|
| **Eje horizontal (X)** | Tiempo transcurrido | 0 a ~163 segundos |
| **Eje vertical (Y)** | Porcentaje de variacion | 0 = perfecto, > 1 = tembleque notable |
| **Linea baja y plana** | Maquina, sintetizador | Chiptune limpio (nuestro caso) |
| **Picos** | Transiciones de nota o vibrato | Cambios de nota, efectos |
| **Jitter (una linea)** | Variacion de afinacion ciclo a ciclo | |
| **Shimmer (otra linea)** | Variacion de volumen ciclo a ciclo | |

---

## 4. Como leerlo paso a paso

### Paso 1: Estima el nivel base de cada curva

Mira la linea que mas tiempo se mantiene:

- **Cerca de 0 (< 0.1%)** = maquina perfecta (sintetizador, chiptune)
- **0.1-0.5%** = maquina con algo de variacion (vibrato leve, LFO)
- **0.5-2%** = humano (voz, instrumento acustico)
- **> 2%** = humano con vibrato fuerte o instrumento sin trastes

### Paso 2: Busca picos

Cada pico es un momento de mayor variacion:

- **Picos estrechos** (~10-50 ms) = transiciones de nota (normal, ignorar)
- **Picos anchos** (> 100 ms) = vibrato intencional o inestabilidad
- **Picos periodicos** = vibrato regular (5-7 Hz tipico)

### Paso 3: Compara jitter y shimmer

- **Ambos bajos** = maquina (caso ideal para chiptune)
- **Jitter alto, shimmer bajo** = vibrato de afinacion (cuerda sin trastes)
- **Shimmer alto, jitter bajo** = tremolo (modulacion de volumen)
- **Ambos altos** = humano (voz, instrumento acustico)

### Paso 4: Marca los picos de transicion

Los picos en cambios de nota son normales:

- La ventana de analisis pill la transicion entre dos estados
- No son expresividad real: son artefacto de la medicion
- Ignoralos al evaluar el caracter del sonido

### Paso 5: Concluye la naturaleza del sonido

- **Bajos y planos** = osciladores simples bastan (`square`, `triangle`)
- **Altos sostenidos** = necesitas sampler o LFO al HTML
- **Picoticos** = vibrato sanos: se distinguen del tembleque porque son periodicos

---

## 5. Patrones tipicos y que significan

### Patron A: lineas bajas y planas (nuestro caso)

```
% 
1.0 |
0.5 |
0.1 |-------------------------------  (ambas curvas)
    +---------------------------------->
= sintetizador perfecto. Osciladores simples clavan el timbre.
  No hacen falta muestras ni modelado de vibrato.
```

### Patron B: jitter alto sostenido

```
%
2.0 |  /\  /\  /\  /\  /\  /\
1.0 | /  \/  \/  \/  \/  \/  \
0.1 |-------------------------------
    +---------------------------------->
= vibrato de afinacion (cuerda sin trastes, voz humana).
  Necesitas sampler o LFO al HTML para replicarlo.
```

### Patron C: shimmer alto con jitter bajo

```
%
2.0 |        /\        /\
1.0 |  ------/  \------/  \------
0.1 |-------------------------------
    +---------------------------------->
= tremolo (modulacion de volumen). El instrumento mantiene la nota
  pero el volumen oscila.
```

### Patron D: picos en transiciones

```
%
2.0 |     ^     ^     ^     ^     ^    (picos estrechos)
0.1 |-----|-----|-----|-----|-----|---
    +---------------------------------->
= transiciones de nota. Son artefacto de la medicion, no expresividad.
  Ignoralos: el merge_short_notes las reunifica.
```

---

## 6. Ejemplo guiado con el Spy Hunter

1. **Abre el jitter_shimmer.png.** Veras dos lineas bajas y estables.

2. **Estima el nivel base.** Ambas curvas van por debajo de 0.1%: osciladores matematicamente perfectos.

3. **Busca picos.** Hay picos estrechos en cambios de nota: son artefactos, no vibrato.

4. **No hay jitter/shimmer sostenido.** Confirma chiptune sintetico puro, sin voces ni instrumentos acusticos.

5. **Cruza con pitch_voiced.** El jitter bajo tambien audita que el pitch va bien: si el jitter explota en un tramo, el detector de pitch fallo ahi.

6. **Conclusion para el conversor:**
   - Osciladores simples (`square`, `triangle`) clavan el timbre
   - No hace falta sampler ni LFO de vibrato
   - Si alguna seccion diera jitter alto, sospecha de voz real o efecto

---

## 7. Errores comunes al leerlo

### 7.1 Confundir picos de transicion con vibrato

Los picos en cambios de nota son artefactos de la ventana de analisis. No son expresividad real: son la medicion pillando dos estados diferentes.

### 7.2 Creer que jitter bajo = pitch correcto

Jitter bajo significa que los ciclos son regulares, pero la octava puede estar mal (ver octave_guard). El jitter audita la **calidad** del pitch, no la **correctitud**.

### 7.3 Ignorar el vibrato intencional

El vibrato (5-7 Hz) sale como jitter/shimmer altos sanos. Se distingue del tembleque porque es **periodico**, no aleatorio.

### 7.4 Usarla como filtro automatico

No hay umbrales universales: 1% jitter es patologico en clinica vocal pero normal en un violonchelo. Lee comparativa entre tramos, no absoluta.

### 7.5 Pedirle notas

El jitter/shimmer no dice que nota suena. Solo dice si la nota es estable o temblorosa. Para notas: pitch, CQT.

---

## 8. Relacion con las demas graficas

| Grafica | Relacion con jitter/shimmer |
|---------|----------------------------|
| **pitch_voiced** | Donde el voicing duda, el jitter miente: ignora esos tramos |
| **hnr** | Jitter bajo + HNR alto = oscilador perfecto, caso ideal |
| **formants/lpc** | Confirman el color estatico que el jitter bajo sugiere |
| **flatness** | Flatness baja + jitter bajo = nota clara y estable |

---

## 9. De la grafica a los parametros del conversor

| Lectura en la grafica | Parametro del conversor |
|----------------------|------------------------|
| Bajo y plano | Osciladores simples bastan (`square`, `triangle`) |
| Alto sostenido | Necesitas sampler o LFO al HTML |
| Picos en transiciones | Normal: ignorar, merge_short_notes las reunifica |
| Jitter bajo | Audita que el pitch va bien |
| Solo una de las dos alta | Vibrato (jitter) o tremolo (shimmer): decide si replicar |

---

## 10. Nivel experto: la formula y el vibrato

### Formula del jitter

Jitter(local) = media(|T[n] - T[n-1]|) / media(T)

Donde T[n] es el periodo del ciclo n. Mide la variacion promedio entre ciclos consecutivos.

### Formula del shimmer

Shimmer(local) = media(|A[n] - A[n-1]|) / media(A)

Donde A[n] es la amplitud pico del ciclo n. Mide la variacion de volumen entre ciclos.

### El vibrato

El vibrato intencional (5-7 Hz) produce jitter/shimmer altos **sanos**:

- **Periodico:** la oscilacion tiene patron (no es aleatorio)
- **Rango controlado:** tipicamente +/- 0.5% en afinacion
- **Percebido como expresivo:** no como error

Se distingue del tembleque porque:
- El tembleque es **aleatorio** (sin patron)
- El vibrato es **periodico** (con patron)

### Uso en el proyecto

El jitter bajo tambien **audita la calidad del pitch**: si el jitter explota en un tramo, el detector de pitch fallo ahi (octavas erroneas, ruido "voiced").

---

## 11. Ejercicio practico

1. **Estima el nivel base** de jitter y shimmer a ojo.
2. **Clasifica** el sonido: maquina, humano, o mixto?
3. **Marca los 3 picos** mas altos y anota sus segundos.
4. **Cruza con pitch_voiced:** ¿Esos picos coinciden con caidas de voicing?
5. **¿Hay vibrato periodico?** Si los picos son regulares (~5-7 Hz), es vibrato.
6. **Conclusion:** ¿Necesitas sampler/LFO o bastan osciladores simples?

---

## 12. Preguntas frecuentes

**¿Jitter o shimmer es mas importante?**
Depende del instrumento. La voz humana tiene ambos; un violonchelo tiene mas jitter (sin trastes); un piano tiene mas shimmer (percusion).

**¿Bajo siempre es bueno?**
Para chiptune, si. Para musica acustica, no: un jitter de 0% suena artificial y plano.

**¿Sirve para separar voces?**
No. Dos voces a la vez dan jitter/shimmer intermedio. Para voces, mel o `--xover`.

**¿Que pasa si el jitter explota en un tramo?**
El detector de pitch fallo ahi (octavas erroneas). Audita ese tramo manualmente.

**¿El vibrato se replica en el HTML?**
Depende del nivel. Vibrato leve (~0.5%): ignoralo. Vibrato fuerte (> 1%): considera LFO.

---

## 13. Glosario rapido

| Termino | Definicion |
|---------|-----------|
| **Jitter** | Variacion de afinacion entre ciclos consecutivos (%) |
| **Shimmer** | Variacion de volumen entre ciclos consecutivos (%) |
| **Vibrato** | Oscilacion periodica de afinacion (5-7 Hz tipico) |
| **Tremolo** | Oscilacion periodica de volumen |
| **LFO** | Low Frequency Oscillator: oscilador lento para modular efectos |

---

## 14. Chuleta final

```
bajo y plano = maquina -> osciladores simples bastan
alto sostenido = humano/vibrato -> sampler o LFO
picos en transiciones = normal, ignorar
jitter bajo tambien audita que el pitch va bien
vibrato es periodico; tembleque es aleatorio
```
