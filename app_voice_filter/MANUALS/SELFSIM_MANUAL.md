# SELFSIM_MANUAL — Matriz de autosimilitud (selfsim.png)

Guia completa: el mapa de los loops del tema, de cero a experto.

---

## Tabla de contenidos

1. [Que es?](#1-qué-es)
2. [Analogia: el Shazam contra si mismo](#2-analogía-el-shazam-contra-sí-mismo)
3. [Anatomia: una tabla gigante](#3-anatomía-una-tabla-gigante)
4. [Como leerlo paso a paso](#4-cómo-leerlo-paso-a-paso)
5. [Patrones tipicos y que significan](#5-patrones-típicos-y-qué-significan)
6. [Ejemplo guiado con el Spy Hunter](#6-ejemplo-guiado-con-el-spy-hunter)
7. [Errores comunes al leerlo](#7-errores-comunes-al-leerlo)
8. [Relacion con las demas graficas](#8-relación-con-las-demás-gráficas)
9. [De la grafica a los parametros del conversor](#9-de-la-gráfica-a-los-parámetros-del-conversor)
10. [Nivel experto: similitud coseno y segmentacion](#10-nivel-experto-similitud-coseno-y-segmentación)
11. [Ejercicio practico](#11-ejercicio-práctico)
12. [Preguntas frecuentes](#12-preguntas-frecuentes)
13. [Glosario rapido](#13-glosario-rápido)
14. [Chuleta final](#14-chuleta-final)

---

## 1. Que es?

Una tabla gigante que compara cada segundo del tema con todos los demas:

- **Casilla brillante** = "estos dos momentos suenan igual"
- **Casilla oscura** = "estos dos momentos suenan distinto"

La **diagonal principal** siempre brilla (cada momento es identico a si mismo). Lo interesante son las **diagonales paralelas**: repeticiones, loops, estribillos que vuelven.

```
     0s   40s   80s   120s  160s
0s  [####........####........####]
40s [........####........####......]
80s [..####........####........####]
    [  diagonal 1    diagonal 2  ]
```

---

## 2. Analogia: el Shazam contra si mismo

Imagina que tienes una cancion y la comparas consigo misma, segundo a segundo:

- **Shazam normal:** compara tu cancion con una base de datos de millones
- **Shazam contra si mismo:** compara la cancion CONSIGO MISMA

Si el segundo 0 suena igual al segundo 12, hay un loop. Si el segundo 40 suena igual al segundo 80, hay repeticion. La matriz te dice **donde se repite** el tema.

---

## 3. Anatomia: una tabla gigante

```
         Y (tiempo)
         ^
    160s |  ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪  (comparar con...)
         |  ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
    120s |  ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
         |  ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
     80s |  ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪  (bloque brillante)
         |  ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
     40s |  ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
         |  ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
      0s +--------------------------->
         0s     40s     80s    120s   160s
                  X (tiempo)
```

| Elemento | Que es | Ejemplo en nuestro tema |
|----------|--------|------------------------|
| **Eje X** | Tiempo (0-163 s) | Un instante del tema |
| **Eje Y** | Tiempo (0-163 s) | Otro instante para comparar |
| **Diagonal principal** | Identidad (ignorar) | Siempre brilla |
| **Bloques brillantes** | Secciones homogeneas | Riff en loop (0-90 s) |
| **Bandas palidas** | Secciones distintas | Puente (90-112 s) |
| **Mini-diagonales** | Repeticiones cortas | Ciclo del Peter Gunn (~12-15 s) |

---

## 4. Como leerlo paso a paso

### Paso 1: Busca el bloque mas grande

El **bloque mas grande y brillante** es la seccion principal del tema:

- ¿Que segundos abarca? (0-90 s en nuestro caso)
- ¿Es uniforme o tiene variaciones internas?
- Dentro de este bloque es donde debes convertir

### Paso 2: Marca las bandas palidas

Las **bandas palidas** son secciones que suenan distinto:

- ¿Donde estan? (~90-112 s en nuestro caso)
- ¿Son anchas o estrechas?
- Son fronteras: **no mezcles** dos secciones en un tramo

### Paso 3: Busca mini-diagonales

Las **mini-diagonales** dentro de un bloque son repeticiones cortas:

- ¿Cada cuantos segundos se repiten? (~12-15 s)
- Eso es el **periodo del loop**
- Convierte un multiplo entero de ese periodo

### Paso 4: Cuenta bloques

¿Cuantos bloques grandes hay?

- **Uno solo** = tema homogeneo, un JSON basta
- **Dos o mas** = secciones con distinto arreglo: convierte cada una aparte
- **Cuadricula de ajedrez** = alternancia verso/estribillo

### Paso 5: Confirma con otras graficas

Cruza la informacion con:

- **intensity:** los escalones de volumen confirman fronteras
- **chroma:** los cambios de filas confirman secciones
- **mfcc:** los cambios de timbre confirman arreglos

---

## 5. Patrones tipicos y que significan

### Patron A: bloque brillante grande (nuestro caso)

```
         +---------------------------+
         |##################        |
         |##################        |  (0-90 s: riff en loop)
         |##################        |
         |        +-----------------+
         |        |   pálido       |  (90-112 s: puente)
         |        +-----------------+
         +---------------------------+
= tema con seccion principal (loop) y puente.
  Convierte dentro del bloque principal.
```

### Patron B: mini-diagonales periodicas

```
         +---+---+---+---+---+---+
         |###|   |###|   |###|   |
         |###|   |###|   |###|   |
         |###|   |###|   |###|   |
         +---+---+---+---+---+---+
           ~12s~
= el mismo dibujo se repite cada ~12 s.
  Periodo del loop: ~12-15 s.
```

### Patron C: cuadricula de ajedrez

```
         +---+---+---+---+
         |###|   |###|   |
         |###|   |###|   |
         +---+---+---+---+
         |   |###|   |###|
         |   |###|   |###|
         +---+---+---+---+
= alternancia verso/estribillo.
  Convierte cada bloque aparte.
```

### Patron D: todo palido

```
         +---------------------------+
         |                           |
         |    (sin bloques claros)   |
         |                           |
         +---------------------------+
= tema sin repeticiones claras.
  Busca otro tramo o acepta JSON grande.
```

---

## 6. Ejemplo guiado con el Spy Hunter

1. **Abre el selfsim.png.** Veras un bloque brillante grande al inicio y bandas palidas despues.

2. **Localiza el bloque principal.** Va de ~0 a ~90 s: es el riff en loop (Peter Gunn). Brillante y uniforme.

3. **Marca la banda palida.** Va de ~90 a ~112 s: es el puente/desarrollo. Suena distinto.

4. **Vuelve el bloque.** Despues de ~112 s, el riff original vuelve hasta el final.

5. **Busca mini-diagonales.** Dentro del bloque 0-90 s, hay repeticiones cada ~12-15 s: el ciclo del Peter Gunn.

6. **Decision de tramo:** Elige 0-20 s (dentro del bloque, sin pisch palido). Eso es 1-2 ciclos del loop.

7. **Duracion del SONG:** El periodo ~12-15 s es la duracion natural del loop HTML.

8. **Conclusion:** Un bloque principal, un puente, y el riff vuelve. Convierte 0-20 s.

---

## 7. Errores comunes al leerlo

### 7.1 Mezclar secciones en un tramo

Un tramo que pise bloque + banda palida mezcla dos arreglos. El MIDI sale con vocabulario el doble de grande.

### 7.2 Ignorar el periodo del loop

Si el `setInterval` del HTML no es multiplo del periodo, el loop corta a mitad de frase.

### 7.3 Leer la diagonal principal

La diagonal es identidad (cada momento consigo mismo). No dice nada.

### 7.4 No cruzar con otras graficas

La selfsim sola no basta. Confirma con intensity (volumen), chroma (notas), y mfcc (timbre).

### 7.5 Convertir el tema entero sin mirar

El tema entero puede tener secciones con distinto arreglo. Mejor convertir un bloque homogeneo.

---

## 8. Relacion con las demas graficas

| Grafica | Relacion con la selfsim |
|---------|------------------------|
| **chroma/mfcc** | Son la materia prima de la matriz; sus cambios explican los bloques |
| **intensity** | Los escalones de volumen confirman las fronteras |
| **cqt** | Muestra las notas del loop que aqui solo se ve repetirse |
| **pitch_voiced** | Los huecos de voicing suelen coincidir con fronteras de bloque |

---

## 9. De la grafica a los parametros del conversor

| Lectura en la grafica | Parametro del conversor |
|----------------------|------------------------|
| Bloque grande y homogeneo | Convierte dentro (0-20 s en nuestro caso) |
| Banda palida | Frontera: no mezcles en un tramo |
| Mini-diagonales ~12-15 s | Periodo del loop: duracion natural del SONG HTML |
| Dos bloques distintos | Dos conversiones aparte o acepta banco medio |
| Todo palido | Busca otro tramo o acepta JSON grande |

---

## 10. Nivel experto: similitud coseno y segmentacion

### Como se calcula

1. **Vectores de features:** Por cada frame (~100 ms), se calcula un vector (tipicamente chroma o MFCC)
2. **Similitud coseno:** Se compara cada par de vectores: similitud = (A . B) / (|A| * |B|)
3. **Matriz:** N x N donde N = numero de frames (~100-1600 segun duracion)

### Complejidad

- **O(N^2)** en memoria y tiempo
- Por eso se usa a ~10-100 frames/s, no a nivel de muestra

### Mejoras classicas

- **Transponer-invarianza:** Comparar chroma rotado para detectar el mismo loop en otro tono
- **Alineacion por DTW:** Para loops con tempo flexible

### Uso avanzado en el proyecto

**Segmentacion automatica:** Cortar el tema por las fronteras de bloque y convertir cada seccion con sus propios parametros (p. ej. puente con `--voices 1`), en vez de un solo JSON global.

---

## 11. Ejercicio practico

1. **Localiza el bloque mas grande** y anota sus segundos.
2. **Cuenta las mini-diagonales** dentro del bloque: estima el periodo del loop.
3. **Marca las bandas palidas** y anota sus segundos.
4. **Cruza con intensity:** ¿Los escalones de volumen coinciden con las fronteras?
5. **Cruza con chroma:** ¿Los cambios de filas coinciden con las bandas palidas?
6. **Propone el tramo ideal** de 20 s para convertir.

---

## 12. Preguntas frecuentes

**¿Que significa "brillante"?**
Alta similitud: los dos momentos suenan igual. La escala de colores va de oscuro (distinto) a brillante (igual).

**¿Y si no hay bloques claros?**
Tema sin repeticiones. Busca otro tramo o acepta un JSON mas grande.

**¿Cada cuanto se repite el loop?**
Mide la distancia entre mini-diagonales. En nuestro tema: ~12-15 s.

**¿Sirve para saber el BPM?**
No directamente. Para tempo: onsets, ZCR, spec_wb_nb.

**¿Puedo convertir el tema entero?**
Si, pero el JSON sera grande y puede mezclar secciones. Mejor un bloque homogeneo.

---

## 13. Glosario rapido

| Termino | Definicion |
|---------|-----------|
| **Autosimilitud** | Comparacion de cada momento del tema consigo mismo |
| **Bloque brillante** | Seccion homogenea (mismo arreglo todo el rato) |
| **Banda palida** | Seccion distinta (puente, cambio de arreglo) |
| **Mini-diagonal** | Repeticion corta del mismo dibujo |
| **Periodo del loop** | Distancia entre mini-diagonales |

---

## 14. Chuleta final

```
bloque grande = seccion en loop -> convierte dentro
banda palida = puente, no mezcles secciones en un tramo
mini-diagonales = periodo del loop -> duracion natural del SONG HTML
dos bloques = dos conversiones aparte o banco medio
cruza con intensity, chroma y mfcc para confirmar fronteras
```
