# LPC_MANUAL — Envolvente espectral LPC (lpc.png)

Guia completa: la silueta del sonido en varios instantes, de cero a experto.

---

## Tabla de contenidos

1. [Que es?](#1-qué-es)
2. [Analogia: el perfil de una montaña](#2-analogía-el-perfil-de-una-montaña)
3. [Anatomia: curvas superpuestas](#3-anatomía-curvas-superpuestas)
4. [Como leerlo paso a paso](#4-cómo-leerlo-paso-a-paso)
5. [Patrones tipicos y que significan](#5-patrones-típicos-y-qué-significan)
6. [Ejemplo guiado con el Spy Hunter](#6-ejemplo-guiado-con-el-spy-hunter)
7. [Errores comunes al leerlo](#7-errores-comunes-al-leerlo)
8. [Relacion con las demas graficas](#8-relación-con-las-demás-gráficas)
9. [De la grafica a los parametros del conversor](#9-de-la-gráfica-a-los-parámetros-del-conversor)
10. [Nivel experto: el modelo lineal predictivo](#10-nivel-experto-el-modelo-lineal-predictivo)
11. [Ejercicio practico](#11-ejercicio-práctico)
12. [Preguntas frecuentes](#12-preguntas-frecuentes)
13. [Glosario rapido](#13-glosario-rápido)
14. [Chuleta final](#14-chuleta-final)

---

## 1. Que es?

Variar curvas de colores, una por instante (t=0.02 s, 32.7 s, 65 s...). Cada curva es la **silueta del espectro** en ese momento: donde hay colinas (resonancias) y donde valles, ignorando las rayitas finas de cada armonico.

Es como comparar los perfiles de varias montanas: si todas tienen la misma silueta, es el mismo instrumento todo el rato.

```
Magnitud (dB)
    ^
  0 |     /\              /\           /\      <- colinas = resonancias
-10 |    /  \    /\      /  \   /\   /  \
-20 |   /    \  /  \    /    \ /  \ /    \
-30 |  /      \/    \  /      \    \      \
-40 | /                \/              \        <- valles = huecos
    +------------------------------------------> Frecuencia (Hz)
    0       5000     10000     15000    20000
```

---

## 2. Analogia: el perfil de una montaña

Imagina que tomas una montaña y dibujas su silueta vista desde el sur:

- **Colinas** = zonas altas (formantes, resonancias)
- **Valles** = zonas bajas (huecos entre resonancias)
- **Pendiente** = como cae la energia hacia los agudos

Si comparas la silueta de 5 montanas diferentes y son casi iguales, tienes un solo tipo de montana (un solo instrumento). Si una es muy distinta, es otra montana (otro instrumento o seccion).

Los formantes (FORMANTS_MANUAL) son las colinas de estas siluetas.

---

## 3. Anatomia: curvas superpuestas

```
Magnitud (dB)
    ^
  0 |  -t=0.02s  -t=32.7s  -t=65s  -t=112s
-10 |     /\         /\        /\       /\
-20 |    /  \       /  \      /  \     /  \
-30 |   /    \     /    \    /    \   /    \
-40 |  /      \   /      \  /      \ /      \
-50 | /        \ /        \/        \        \
    +------------------------------------------> Frecuencia (Hz)
    0       5000     10000     15000    20000
                          |
                    muro a ~15300 Hz
```

| Elemento | Que es | Ejemplo en nuestro tema |
|----------|--------|------------------------|
| **Eje horizontal (X)** | Frecuencia (0-22050 Hz) | Mismo rango que el espectro |
| **Eje vertical (Y)** | Magnitud en dB | Mas arriba = mas energia |
| **Curvas superpuestas** | Perfiles en distintos instantes | Mismo timbre = curvas similares |
| **Colinas** | Formantes (resonancias) | Cuerpo del bajo, lead |
| **Muro vertical** | Limite de banda de la fuente | ~15300 Hz (ripeo limitado) |

---

## 4. Como leerlo paso a paso

### Paso 1: Compara las curvas entre si

Mira si las curvas se parecen o son muy distintas:

- **Curvas casi identicas** = un solo instrumento/todo el tema
- **Una curva muy distinta** = seccion con otro arreglo
- **Gradualmente diferentes** = derivada del timbre (filtro que se abre/cierra)

### Paso 2: Identifica las colinas (formantes)

Las **colinas** son las zonas donde la curva sube:

- **Colinas bajas** (< 1000 Hz) = cuerpo del sonido (bajo, fundamental)
- **Colinas medias** (1000-3000 Hz) = vocal, presencia del lead
- **Colinas altas** (> 3000 Hz) = brillo, aire, armónicos

### Paso 3: Busca el muro

El **muro** es una caida vertical comun a todas las curvas:

- En nuestro tema: ~15300 Hz
- Significa: la fuente esta limitada en banda (ripeo/masterizacion)
- Por encima: solo ruido de codificacion, nunca musica

### Paso 4: Marca los valles

Los **valles** son zonas donde la curva baja:

- Valles entre colinas = huecos entre resonancias
- Valles profundos = buen sitio para `--xover`
- Si los valles cambian de posicion entre curvas = el timbre cambia

### Paso 5: Concluye el timbre

Si las curvas son iguales:
- Un banco de osciladores basta para todo el tema
- En nuestro tema: `triangle` bajo + `square` lead

Si una curva difiere mucho:
- Esa seccion merece sus propios timbres

---

## 5. Patrones tipicos y que significan

### Patron A: curvas casi identicas (nuestro caso)

```
Magnitud
  0 |  -todas las curvas superpuestas
-20 |     /\  /\  /\
-40 |    /  \/  \/  \
-60 |  /              \
    +----------------------> Frecuencia
= un solo timbre, mismos osciladores 163 s. Caso ideal.
```

### Patron B: una curva distinta

```
Magnitud
  0 |  -t=0s:    /\
-20 |            /  \
-40 |  -t=65s:      /\
    +----------------------> Frecuencia
= seccion con otro arreglo (puente). Convierte aparte o acepta banco medio.
```

### Patron C: colinas que se desplazan

```
Magnitud
  0 |     /\      (t=0)
-20 |    /  \
-40 |       /\    (t=80, desplazado)
    +----------------------> Frecuencia
= filtro que se abre/cierra (sweep de sintetizador). El timbre cambia
  dentro de la seccion.
```

### Patron D: muro comun a todas

```
Magnitud
  0 |     /\
-20 |    /  \
-40 |   /    \
-60 |  /      \|
    +-----------|-------> Frecuencia
              ~15300 Hz
= limite de la fuente (ripeo). Todo lo de arriba es ruido: ignoralo.
  Nuestro cap de 1200 Hz queda muy por debajo: margen de sobra.
```

---

## 6. Ejemplo guiado con el Spy Hunter

1. **Abre el lpc.png.** Veras varias curvas superpuestas.

2. **Compara las curvas.** Son casi identicas: mismo timbre de principio a fin (chiptune homogeneo).

3. **Identifica las colinas.** Hay colinas en 300-800 Hz (cuerpo del bajo) y en 1000-2000 Hz (lead). Coinciden con los formantes del FORMANTS_MANUAL.

4. **Localiza el muro.** Caida vertical a ~15300 Hz: la fuente esta limitada. Por encima solo hay suelo de ruido a -25 dB.

5. **Busca valles.** Hay un valle claro ~300 Hz: buen candidato a `--xover`.

6. **Conclusion para el conversor:**
   - Un banco de osciladores basta (curvas iguales)
   - El cap de 1200 Hz queda muy por debajo del muro: seguro
   - El valle ~300 Hz justifica `--xover 300`

---

## 7. Errores comunes al leerlo

### 7.1 Leer armonicos como formantes

Las curvas muestran la **envolvente** (silueta), no los armonicos individuales. Las colinas son formantes; las rayitas finas (que no se ven aqui) son armonicos.

### 7.2 Ignorar el muro

El muro a ~15300 Hz no es un problema: es una limitacion de la fuente. Todo lo de arriba es ruido de codificacion.

### 7.3 Pedirle notas

Las curvas no dicen que nota suena. Solo muestran la forma del espectro (timbre). Para notas: pitch, CQT.

### 7.4 Confundir una curva distinta con otro instrumento

Puede ser la misma nota en otra octava (el lead sube). Compara la posicion de las colinas: si se desplazan proporcionalmente, es un cambio de registro, no de instrumento.

### 7.5 Usarla para timing

Las curvas se calculan con ventanas largas (~30-50 ms). Para onsets exactos, usa el wideband.

---

## 8. Relacion con las demas graficas

| Grafica | Relacion con LPC |
|---------|-----------------|
| **formants** | Los picos de estas curvas, vistos en el tiempo |
| **sweep (centroide)** | El centro de gravedad de estas siluetas |
| **flatness** | El suelo plano de -25 dB arriba es lo que la flatness llama "ruido" |
| **mel** | Las franjas de la mel explican la forma de estas curvas |

---

## 9. De la grafica a los parametros del conversor

| Lectura en la grafica | Parametro del conversor |
|----------------------|------------------------|
| Curvas iguales | Un banco: `--waveforms triangle,square,...` fijo |
| Una curva distinta | Seccion: convierte aparte con sus timbres |
| Colinas que se desplazan | Filtro en movimiento: acepta banco medio o trocea |
| Muro a ~15300 Hz | Cap de 1200 Hz justificado (muy por debajo) |
| Valles profundos | Candidatos a `--xover` |

---

## 10. Nivel experto: el modelo lineal predictivo

### Que es LPC

LPC (Linear Predictive Coding) modela cada muestra como combinacion lineal de las anteriores:

x[n] = a1*x[n-1] + a2*x[n-2] + ... + ap*x[n-p] + e[n]

Donde:
- a1..ap = coeficientes del modelo
- p = orden del modelo (tipicamente 12-16)
- e[n] = error (ruido de excitacion)

### Como salen las curvas

La envolvente espectral es la respuesta en frecuencia del filtro resultante:

H(f) = 1 / |1 - a1*z^-1 - a2*z^-2 - ... - ap*z^-p|  (z = e^(j*2*pi*f/fs))

### Orden del modelo

- **Menos de 12:** Suaviza demasiado, pierde formantes
- **12-16:** Rango ideal para voz/musica
- **Mas de 16:** Empieza a seguir armonicos individuales (deja de ser "envolvente")

### El muro a ~15300 Hz

Delata remuestreo/filtro antialias del ripeo. Trabajar a 48 kHz no devuelve informacion por encima: es normal y no afecta al conversor, que vive por debajo de 1200 Hz.

---

## 11. Ejercicio practico

1. **Compara 2 curvas** de instantes distintos: ¿se parecen? ¿Que formantes comparten?
2. **Identifica el valle** mas profundo entre colinas: estima sus Hz.
3. **Localiza el muro** y comprueba que es comun a todas las curvas.
4. **Busca una curva distinta** (si existe): ¿en que segundo esta? ¿Que cambio?
5. **Cruza con formants:** ¿Las colinas de aqui coinciden con los formantes?
6. **Conclusion:** ¿Un banco de osciladores basta o necesitas dos?

---

## 12. Preguntas frecuentes

**¿LPC o formants para timbre?**
Ambos. LPC muestra la silueta completa; formants extrae los picos. Para elegir osciladores, ambos sirven.

**¿Que es el muro a ~15300 Hz?**
Limite de banda del ripeo. No es musica: es ruido de codificacion. Ignoralo.

**¿Por que las curvas se parecen tanto?**
Chiptune homogeneo: los osciladores no cambian de timbre. En musica acustica verias mas variacion.

**¿Sirve para saber que nota suena?**
No. Solo muestra la forma del espectro (timbre). Para notas: pitch, CQT.

**¿Cuantas curvas debo mirar?**
4-6 bastan para ver si el timbre cambia. No necesitas mirar todas.

---

## 13. Glosario rapido

| Termino | Definicion |
|---------|-----------|
| **LPC** | Linear Predictive Coding: modelo que predice muestras |
| **Envolvente espectral** | Silueta del espectro, sin armonicos individuales |
| **Formantes** | Colinas de la envolvente (resonancias) |
| **Orden del modelo** | Numero de coeficientes (12-16 tipico) |
| **Muro** | Limite de banda de la fuente (~15300 Hz en ripeos) |

---

## 14. Chuleta final

```
curvas iguales = mismo timbre, mismos osciladores
muro vertical comun = limite de la fuente, ignoralo
colinas = formantes; valles profundos = buen sitio para --xover
colinas que se desplazan = filtro en movimiento
curva distinta = seccion con otro arreglo
```
