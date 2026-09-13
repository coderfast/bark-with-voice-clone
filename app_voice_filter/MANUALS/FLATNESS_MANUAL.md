# FLATNESS_MANUAL — Planitud espectral (flatness.png)

Guia completa: ¿suena a nota o a estatica? De cero a experto.

---

## Tabla de contenidos

1. [Que es?](#1-qué-es)
2. [Analogia: el electrocardiograma del sonido](#2-analogía-el-electrocardiograma-del-sonido)
3. [Anatomia: ejes y curva](#3-anatomía-ejes-y-curva)
4. [Como leerlo paso a paso](#4-cómo-leerlo-paso-a-paso)
5. [Patrones tipicos y que significan](#5-patrones-típicos-y-qué-significan)
6. [Ejemplo guiado con el Spy Hunter](#6-ejemplo-guiado-con-el-spy-hunter)
7. [Errores comunes al leerlo](#7-errores-comunes-al-leerlo)
8. [Relacion con las demas graficas](#8-relación-con-las-demás-gráficas)
9. [De la grafica a los parametros del conversor](#9-de-la-gráfica-a-los-parámetros-del-conversor)
10. [Nivel experto: la formula geometrica](#10-nivel-experto-la-fórmula-geométrica)
11. [Ejercicio practico](#11-ejercicio-práctico)
12. [Preguntas frecuentes](#12-preguntas-frecuentes)
13. [Glosario rapido](#13-glosario-rápido)
14. [Chuleta final](#14-chuleta-final)

---

## 1. Que es?

Un valor por instante entre 0 y 1 que responde: ¿el espectro tiene **picos** (notas) o es **plano** (ruido)?

- Cerca de **0** = espectro con picos marcados = **tono musical**.
- Cerca de **1** = espectro plano como una mesa = **ruido** (estatica, platillo, consonante "s").

```
Flatness cercana a 0 (TONO):     Flatness cercana a 1 (RUIDO):

    /\                              ------------------
   /  \                             ------------------
  /    \                            ------------------
 /      \                           ------------------
= notas con picos claros            = espectro plano, sin notas
```

---

## 2. Analogia: el electrocardiograma del sonido

Piensa en un electrocardiograma (ECG):

- **Picos regulares** = el corazon late (nota musical)
- **Linea plana con temblor** = interferencia (ruido, sin ritmo)

La flatness es el ECG del espectro: si ves picos, hay notas; si ves linea plana, hay ruido. No te dice que nota es (para eso esta pitch), te dice si **merece la pena** buscar notas ahi.

---

## 3. Anatomia: ejes y curva

```
Flatness (0-1)
    ^
1.0 |  /\      /\          /\    (ruido, percusion)
0.8 | /  \    /  \        /  \
0.6 |/    \  /    \      /    \
0.4 |      \/      \    /      \
0.2 |               \  /        \  (notas claras)
0.0 |                \/          \___
    +------------------------------------------> Tiempo
    0s        40s        80s       120s      160s
```

| Elemento | Que es | Ejemplo en nuestro tema |
|----------|--------|------------------------|
| **Eje horizontal (X)** | Tiempo transcurrido | 0 a ~163 segundos |
| **Eje vertical (Y)** | Planitud (0 a 1) | 0 = tono puro, 1 = ruido puro |
| **Linea baja y plana** | Tema tonal, notas claras | Chiptune limpio (nuestro caso) |
| **Picos hacia 1** | Ruido, percusion, golpes | Transitorios, bursts |
| **Mesetas altas** | Secciones ruidosas sostenidas | Efectos, reverberacion densa |

---

## 4. Como leerlo paso a paso

### Paso 1: Estima el nivel base

Mira la linea que mas tiempo se mantiene: ¿esta cerca de 0, de 0.5, o de 1?

- **Cerca de 0 (< 0.3)** = tema mayormente tonal (musica, voz cantada)
- **Cerca de 0.5** = mezcla de tono y ruido (voz hablada con respiraciones)
- **Cerca de 1 (> 0.7)** = tema mayormente ruidoso (percusion, efectos)

### Paso 2: Marca los picos

Cada pico hacia 1 es un momento donde el espectro se aplana:

- **Picos estrechos** (~50-200 ms) = golpes de percusion, transitorios
- **Picos anchos** (> 500 ms) = secciones ruidosas o de efectos
- **Picos periodicos** = percusion regular entre notas

### Paso 3: Busca mesetas altas

Una **meseta alta** sostenida (> 0.7) indica una seccion donde el ruido domina:

- ¿Dura mucho (> 5 s)? Seccion que debes evitar al convertir
- ¿Es corta (< 1 s)? Transicion o efecto: se filtra sola
- ¿Se repite? Arreglo con percusion densa

### Paso 4: Busca mesetas bajas

Una **meseta baja** sostenida (< 0.2) indica notas claras:

- ¿Dura todo el tema? Chiptune limpio, ideal para convertir
- ¿Solo en partes? El detector de pitch solo funcionara ahi
- ¿Coincide con voicing alto? Confirmacion de nota real

### Paso 5: Cruza con HNR

Flatness baja + HNR alto = nota segura (doble confirmacion)
Flatness alta + HNR bajo = ruido seguro (doble confirmacion)
Flatness baja + HNR bajo = extraño: revisa manualmente
Flatness alta + HNR alto = extraño: revisa manualmente

---

## 5. Patrones tipicos y que significan

### Patron A: baja y plana (nuestro caso)

```
flatness
0.3 |  ------------------------------  (siempre baja)
    +---------------------------------->
= musica tonal limpia. Chiptune ideal: el detector trabaja a gusto.
  --min-conf 0.15 basta.
```

### Patron B: picos periodicos estrechos

```
flatness
0.8 |     /\     /\     /\     /\
0.3 |----/  \---/  \---/  \---/  \----
    +---------------------------------->
= percusion entre notas. Los picos son golpes de bateria.
  filter_short_notes los entierra. No subas --min-conf por ellos.
```

### Patron C: meseta alta sostenida

```
flatness
0.8 |  ------------------------------
0.3 |                               \--------
    +---------------------------------->
= seccion ruidosa/efectos. No conviertas ahi.
  Busca otro tramo (ver selfsim para elegir bloque).
```

### Patron D: subida al final

```
flatness
0.8 |                          /--------
0.3 |  -----------------------/
    +---------------------------------->
= fade con ruido o cola de reverberacion.
  Corta antes del fade: el detector fallara ahi.
```

---

## 6. Ejemplo guiado con el Spy Hunter

1. **Abre el flatness.png.** Veras una linea baja y estable a lo largo de los ~163 s.

2. **Estima el nivel base.** Se mantiene cerca de 0.1-0.2: chiptune limpio, sin percusion acustica que estorbe.

3. **Busca picos.** Hay picos estrechos ocasionales (~0.3-0.5): son transitorios de notas o golpes sinteticos. No son ruido sostenido.

4. **No hay mesetas altas.** Todo el tema es tonal. Esto confirma que cualquier tramo de 0-60 s es convertible.

5. **Cruza con HNR.** Ambos confirman: chiptune limpio, sin secciones ruidosas que evitar.

6. **Cruza con pitch_voiced.** Donde la flatness es baja, el voicing deberia estar alto. Si hay un pico de flatness sin caida de voicing, el detector esta siendo optimista.

7. **Conclusion para el conversor:** Tema ideal. --min-conf 0.15, cualquier tramo 0-60 s vale.

---

## 7. Errores comunes al leerlo

### 7.1 Creer que flatness 0 = nota perfecta

No. Una onda cuadrada (armónicos hasta arriba) da flatness media aunque sea perfectamente musical. La flatness no distingue entre "nota rica en armonicos" y "ruido tonal".

### 7.2 Usarla como umbral automatico

No hay numero magico universal: 0.3 es gloria en chiptune y mediocridad en orquesta. Lee siempre comparativa entre tramos, no absoluta.

### 7.3 Ignorar los picos de transicion

Los picos en cambios de nota son normales: la ventana de analisis pill la transicion entre dos estados. No son ruido real.

### 7.4 Confundirla con HNR

Ambos miden "tono vs ruido" pero por caminos distintos. HNR asume periodicidad (mejor con musica), flatness no (mejor con ruido puro). Juntos no fallan.

### 7.5 Pedirle notas

La flatness no dice que nota suena. Para notas: pitch, CQT, chroma.

---

## 8. Relacion con las demas graficas

| Grafica | Relacion con la flatness |
|---------|------------------------|
| **hnr** | Cuentan la misma historia (tono vs ruido) por caminos distintos; si ambas acusan un tramo, creelas |
| **zcr** | La pareja de desempate: ruido = flatness alta + ZCR alto; nota aguda = flatness baja + ZCR alto |
| **pitch_voiced** | Donde la flatness pica, el voicing deberia caer; si no cae, el detector esta siendo optimista |
| **intensity** | Donde la intensidad cae, la flatness puede subir (silencio ruidoso) |

---

## 9. De la grafica a los parametros del conversor

| Lectura en la grafica | Parametro del conversor |
|----------------------|------------------------|
| Baja y plana todo el rato | `--min-conf` 0.15: conversion fiable |
| Picos periodicos estrechos | Nada: `filter_short_notes` los entierra |
| Meseta alta sostenida | Cambia de tramo (ver selfsim) |
| Pico sin caida de voicing | Sospecha: sube `--min-conf` para ese instante |
| Flatness media estable | Cuadrada rica en armonicos: normal, no fallo |

---

## 10. Nivel experto: la formula geometrica

### Formula

Flatness = media_geometrica(espectro) / media_aritmetica(espectro)

- **Media geometrica:** (x1 * x2 * ... * xN)^(1/N) -> tiende a cero si hay ceros
- **Media aritmética:** (x1 + x2 + ... + xN) / N -> estable

Si el espectro tiene picos claros, la geometrica es mucho menor que la aritmetica -> flatness baja.
Si el espectro es plano, ambas son similares -> flatness ~1.

### Por que funciona

Un tono puro concentra energia en pocos bins -> geometrica baja, aritmetica alta -> flatness ~0.
Ruido blanco reparte energia en todos los bins -> ambas similares -> flatness ~1.

### Limites

- **Ondas cuadradas:** Ricas en armonicos -> flatness media aunque sean notas perfectas. No la uses como umbral para chiptune.
- **Ventana corta:** La flatness es ruidosa con ventanas < 20 ms. Usa ventanas de 20-50 ms.
- **No distingue fuentes:** Dos notas a la vez dan flatness intermedia.

### Uso en el proyecto

El conversor no filtra por flatness por estos limites. Su uso es **diagnostico visual**:
- Flatness baja + HNR alto = nota segura
- Flatness alta = sospecha de ruido, verifica con HNR
- Comparativa entre tramos, no absoluta

---

## 11. Ejercicio practico

1. **Estima el nivel base** de la flatness a ojo (bajo/medio/alto).
2. **Cuenta los picos** que superen 0.5 en 10 segundos.
3. **Cruza con HNR** en esos picos: ¿coinciden con valles de HNR?
4. **Busca mesetas** sostenidas: ¿durmas de 1 s? Anota sus segundos.
5. **Compara con pitch_voiced:** ¿Las mesetas altas coinciden con caidas de voicing?
6. **Conclusion:** ¿El tema es tonal, ruidoso, o mixto?

---

## 12. Preguntas frecuentes

**¿Flatness o HNR para detectar ruido?**
Ambos. HNR asume periodicidad (mejor con musica), flatness no (mejor con ruido puro). Juntos no fallan.

**¿Un pico de flatness invalida el tramo?**
Si es sostenido, si. Si son picos estrechos, no: es la percusion haciendo su trabajo.

**¿Que valor de flatness es "bueno"?**
Depende del tema. En chiptune: < 0.3 es bueno. En orquesta: < 0.5 puede ser bueno. Lee comparativa, no absoluta.

**¿Sirve para separar voces?**
No. Dos voces a la vez dan flatness intermedia. Para voces, mel o `--xover`.

**¿Por que no la usa el conversor como filtro?**
Porque las cuadradas dan flatness media (falso positivo) y porque la confianza de pitch ya incluye esta informacion de forma mas robusta.

---

## 13. Glosario rapido

| Termino | Definicion |
|---------|-----------|
| **Flatness** | Planitud espectral: 0 = tono puro, 1 = ruido puro |
| **Media geometrica** | Raiz N-esima del producto de los valores |
| **Media aritmetica** | Suma dividida por N |
| **Espectro plano** | Sin picos claros = ruido |
| **Espectro picudo** | Con picos marcados = notas |

---

## 14. Chuleta final

```
baja y plana = musica tonal, convierte
picos = golpes/ruido -> se filtran con --min-conf
meseta alta = cambia de tramo
comparativa, no absoluta (las cuadradas dan planitud media)
complementa a hnr: juntos no fallan
```
