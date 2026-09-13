# FORMANTS_MANUAL — Seguimiento de formantes F1-F4 (formants.png)

Guia completa: las resonancias que dan color al sonido, de cero a experto.

---

## Tabla de contenidos

1. [Que es un formante?](#1-qué-es-un-formante)
2. [Analogia: la botella que canta](#2-analogía-la-botella-que-canta)
3. [Anatomia: ejes y bandas](#3-anatomía-ejes-y-bandas)
4. [Como leerlo paso a paso](#4-cómo-leerlo-paso-a-paso)
5. [Patrones tipicos y que significan](#5-patrones-típicos-y-qué-significan)
6. [Ejemplo guiado con el Spy Hunter](#6-ejemplo-guiado-con-el-spy-hunter)
7. [Errores comunes al leerlo](#7-errores-comunes-al-leerlo)
8. [Relacion con las demas graficas](#8-relación-con-las-demás-gráficas)
9. [De la grafica a los parametros del conversor](#9-de-la-gráfica-a-los-parámetros-del-conversor)
10. [Nivel experto: LPC y las raices del polinomio](#10-nivel-experto-lpc-y-las-raíces-del-polinomio)
11. [Ejercicio practico](#11-ejercicio-práctico)
12. [Preguntas frecuentes](#12-preguntas-frecuentes)
13. [Glosario rapido](#13-glosario-rápido)
14. [Chuleta final](#14-chuleta-final)

---

## 1. Que es un formante?

Sopla por una botella vacia y luego por una llena: suenan distinto porque la **cavidad resuena** en frecuencias distintas. Esas frecuencias de resonancia son los **formantes** (F1, F2, F3, F4, de grave a agudo).

```
Botella vacia:                Botella llena:
  F1 = 300 Hz                   F1 = 250 Hz
  F2 = 800 Hz                   F2 = 700 Hz
  (suena "hueco")               (suena "lleno")
```

En la voz humana, los formantes distinguen vocales:
- **"A"** = F1 ~800 Hz, F2 ~1200 Hz
- **"E"** = F1 ~500 Hz, F2 ~2000 Hz
- **"I"** = F1 ~300 Hz, F2 ~3000 Hz
- **"O"** = F1 ~400 Hz, F2 ~800 Hz
- **"U"** = F1 ~300 Hz, F2 ~600 Hz

En sintetizadores e instrumentos, los formantes marcan el **carácter**: nasal, hueco, brillante.

---

## 2. Analogia: la botella que canta

Imagina que tienes 4 botellas de distintos tamaños, cada una sintonizada para resuenar con una frecuencia diferente:

```
Botella grande (F1):     "GLUG GLUG"     -> 300 Hz (grabe)
Botella mediana (F2):    "GLUG GLUG"     -> 1000 Hz (medio)
Botella chica (F3):      "GLUG GLUG"     -> 2500 Hz (agudo)
Botella tiny (F4):       "GLUG GLUG"     -> 4000 Hz (muy agudo)
```

Cuando cantas, tu garganta es la "fuente" y tu boca es la "botella": la boca cambia de forma y los formantes se mueven. Los formantes son la **huella acustica** de la forma de la boca en cada momento.

---

## 3. Anatomia: ejes y bandas

```
Frecuencia (Hz)
    ^
5000|  · · · · · · · · · · · · ·  F4 (brillo, aire)
4000|  ───────────────────────────  F4 estable
3000|  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  F3 (cuerpo agudo)
2500|  ═══════════════════════════  F3
2000|  ───────────────────────────  F2 (vocal, lead)
1500|  ═══════════════════════════  F2
1000|  ██████████████████████████  F1 (grave, cuerpo)
 500|  ██████████████████████████  F1
    +------------------------------------------> Tiempo
    0s        40s        80s       120s      160s
```

| Elemento | Que es | Ejemplo en nuestro tema |
|----------|--------|------------------------|
| **Eje horizontal (X)** | Tiempo transcurrido | 0 a ~163 segundos |
| **Eje vertical (Y)** | Frecuencia (0-5000 Hz) | Donde resuena el sonido |
| **Bandas bajas estables** | F1 y F2 del bajo (cuerpo resonante) | Bajo synth, siempre presente |
| **Trazos medios moviles** | F2-F3 del lead (sigue la melodía) | Lead que sube y baja |
| **Puntos dispersos** | Formantes falsos o de ruido | Armónicos fuertes, transitorios |

---

## 4. Como leerlo paso a paso

### Paso 1: Identifica las bandas estables

Mira si hay **bandas horizontales** que se mantienen todo el rato:

- **Bandas bajas fijas** (< 1000 Hz) = cuerpo resonante estable (bajo synth)
- **Bandas medias** (1000-3000 Hz) = lead o voz
- **Bandas altas** (> 3000 Hz) = brillo, aire, armónicos lejanos

### Paso 2: Busca trazos moviles

Los **trazos** son lineas que suben y bajan con la melodía:

- ¿Siguen la nota del lead? (suben cuando la nota sube)
- ¿Son estables o temblorosos? (estables = sintetizador, temblorosos = vibrato)
- ¿Se superponen con las bandas bajas? (posible solapamiento de voces)

### Paso 3: Marca los cambios

Los **cambios bruscos** en la posicion de los formantes indican:

- **Cambio de vocal** (en voz humana): F1 y F2 saltan a nueva posicion
- **Cambio de instrumento** (en musica): la silueta del espectro cambia
- **Cambio de registro** (el lead sube una octava): los formantes se desplazan

### Paso 4: Busca formantes falsos

Los **formantes falsos** son puntos que aparecen sobre armonicos fuertes:

- En ondas cuadradas, el 3er armonico puede "engañar" al algoritmo
- Son puntos que no siguen el patron del instrumento real
- Se distinguen porque no tienen familia (no hay F1/F2/F3 juntos)

### Paso 5: Concluye el timbre

Con la informacion anterior, decide que oscilador representa mejor el sonido:

- Bandas bajas marcadas + pocos formantes altos = `triangle` o `square` grave
- Formantes moviles en medios = `square` o `sawtooth` para lead
- Poca estructura = ruido, no乐器

---

## 5. Patrones tipicos y que significan

### Patron A: bandas bajas fijas (nuestro caso)

```
Hz
3000|  · · · · · · · · · · · ·  (aire, sin dibujo)
2000|  ════════════════════════  (lead, movil)
1000|  ████████████████████████  (bajo, fijo)
 500|  ████████████████████████  (bajo, fijo)
    +---------------------------------->
= bajo synth estable + lead movil. Un banco de osciladores basta
  para todo el tema (triangle bajo + square lead).
```

### Patron B: trazos que siguen la melodia

```
Hz
2500|     ╭──╮    ╭──╮
2000|  ═══╯  ╰════╯  ╰══════
1500|  ═══════════════════════
    +---------------------------------->
= lead con formantes que siguen la nota. Confirma que es un instrumento
  real, no ruido.
```

### Patron C: nubes dispersas sin bandas

```
Hz
4000|  · · · ·  · ·  · · ·  ·
3000| ·  ·  · ·  ·  ·  ·  · ·
2000|  · ·  · ·  · ·  · ·  ·
    +---------------------------------->
= ruido o mezcla sin resonancias claras. No hay instrumento que
  transcribir aqui.
```

### Patron D: bandas que desaparecen

```
Hz
2000|  ════════════            (se fue)
1000|  ████████████            (se fue)
 500|  ████████████  ████████  (vuelve)
    +---------------------------------->
= instrumento que calla y vuelve. Marca las secciones por aqui.
```

---

## 6. Ejemplo guiado con el Spy Hunter

1. **Abre el formants.png.** Veras bandas bajas estables y trazos medios moviles.

2. **Identifica las bandas fijas.** Hay bandas en 300-800 Hz que se mantienen todo el rato: es el cuerpo del bajo synth (cuadrada del Peter Gunn).

3. **Identifica los trazos moviles.** Hay trazos en 1000-2000 Hz que suben y bajan: es el lead siguiendo la melodía.

4. **Busca cambios.** Alrededor de 90 s, los trazos medios cambian de patron: el lead entra en el puente. Despues de 112 s, vuelve al patron original.

5. **Descarta formantes falsos.** Hay puntos dispersos arriba (> 3000 Hz) que no siguen ningun patron: son armónicos de cuadrada, no notas.

6. **Conclusion para osciladores:**
   - Bajo: `triangle` o `square` grave (bandas fijas bajas)
   - Lead: `square` o `sawtooth` (trazos moviles en medios)
   - Un solo banco basta para todo el tema

---

## 7. Errores comunes al leerlo

### 7.1 Confundir formantes con notas

Un formante no es una nota. Los formantes definen el **timbre** (como suena), no el **pitch** (que nota es). Para notas: pitch, CQT, chroma.

### 7.2 Creer todos los puntos

Los algoritmos de formantes proponen "formantes" sobre armonicos fuertes que no son resonancias reales. Busca bandas con consistencia temporal, no puntos sueltos.

### 7.3 Ignorar la superposicion de voces

Con dos voces sonando, el algoritmo mezcla sus resonancias en una sola lista. Si ves bandas que "saltan" entre dos alturas, puede ser dos voces, no una que cambia.

### 7.4 Pedirle timing fino

Los formantes se calculan con ventanas largas (~30-50 ms). Para onsets exactos, usa el wideband (spec_wb_nb).

### 7.5 Usarlos para transcribir

Los formantes sirven para **elegir osciladores**, no para transcribir notas. Son la informacion del "color", no de la "altura".

---

## 8. Relacion con las demas graficas

| Grafica | Relacion con los formantes |
|---------|--------------------------|
| **lpc** | Los formantes son los picos de las envolventes LPC; misma historia |
| **mfcc** | Otra forma de describir el mismo color timbrico |
| **sweep (centroide)** | El resumen en una linea de hacia donde tira el color |
| **mel** | Las franjas de la mel explican por que los formantes estan donde estan |

---

## 9. De la grafica a los parametros del conversor

| Lectura en la grafica | Parametro del conversor |
|----------------------|------------------------|
| Bandas bajas fijas | `triangle` o `square` grave para bajo |
| Trazos moviles en medios | `square` o `sawtooth` para lead |
| Bandas que desaparecen | Secciones: convierte dentro de una sola |
| Puntos sin banda | Descartar: armónicos, no notas |
| Mismas bandas 163 s | Un solo banco basta para todo el tema |

---

## 10. Nivel experto: LPC y las raices del polinomio

### Como se calculan

Los formantes se extraen de las **raices del polinomio LPC** (ver LPC_MANUAL):

1. Se ajusta un modelo LPC de orden 12-16 al fragmento de audio
2. Se hallan las raices del polinomio resultante
3. Las raices complejas con parte imaginaria significativa son **formantes candidatos**
4. Se filtran por frecuencia (F1: 200-900 Hz, F2: 800-2500 Hz, F3: 1500-3500 Hz, F4: 3000-5000 Hz)

### Limites importantes

- **Ondas cuadradas:** Ricas en armonicos -> el algoritmo propone formantes "falsos" sobre armónicos fuertes
- **Dos voces:** Mezcla sus resonancias en una sola lista
- **Orden del modelo:** Menos de 12 suaviza de mas; mas de 16 empieza a seguir armónicos individuales

### Uso en el proyecto

Los formantes **describen timbre para elegir osciladores**, nunca guian la transcripción de notas. En el proyecto:
- Bandas bajas fijas -> `triangle` para voz0-1 (bajo)
- Trazos medios moviles -> `square`/`sawtooth` para voz2 (lead)
- Un solo banco basta si las bandas no cambian 163 s

---

## 11. Ejercicio practico

1. **Identifica las bandas bajas fijas** y estima su rango de Hz.
2. **Identifica los trazos moviles** y comprueba si siguen la melodia.
3. **Busca un cambio** (~90 s) y anota como cambian los formantes.
4. **Descarta puntos sueltos** arriba: ¿son armónicos o formantes reales?
5. **Propone osciladores** para bajo y lead basandote solo en esta grafica.
6. **Compara con MFCC:** ¿Los cambios de timbre coinciden?

---

## 12. Preguntas frecuentes

**¿Formantes o MFCC para timbre?**
Ambos. Los formantes son mas interpretables (frecuencias exactas); los MFCC son mas compactos (13 numeros). Para elegir osciladores, formantes.

**¿Sirven para saber que nota suena?**
No. Los formantes definen el color, no la altura. Un "A" y un "E" pueden tener la misma nota pero distintos formantes.

**¿Que pasa si hay dos voces?**
El algoritmo mezcla sus resonancias. Para separar, usa mel o `--xover`.

**¿Por que hay puntos falsos?**
Los armonicos fuertes "engañan" al algoritmo. Busca consistencia temporal, no puntos sueltos.

**¿Cuantos formantes debo mirar?**
Tipicamente F1 y F2 bastan para timbre. F3 y F4 son detalle fino.

---

## 13. Glosario rapido

| Termino | Definicion |
|---------|-----------|
| **Formante** | Frecuencia resonante que define el timbre del sonido |
| **F1, F2, F3, F4** | Los cuatro primeros formantes, de grave a agudo |
| **Timbre** | "Color" del sonido: como suena, no que nota es |
| **LPC** | Linear Predictive Coding: modelo que extrae los formantes |
| **Raices del polinomio** | Las frecuencias resonantes del modelo LPC |

---

## 14. Chuleta final

```
bandas estables abajo = cuerpo del bajo -> triangle/square grave
trazos medios moviles = lead -> square/sawtooth
formante != nota: sirve para elegir timbre, no para transcribir
puntos sueltos = armónicos, no formantes reales
mismas bandas 163 s = un solo banco basta
```
