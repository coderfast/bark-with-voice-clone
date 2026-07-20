# RVC-GUI-pkg

## ¿Qué es RVC?

RVC (Retrieval-based Voice Conversion) es una herramienta de **conversión de voz** que permite transformar una voz en otra manteniendo el contenido del habla. Se usa como paso **post-procesamiento** después de generar audio con Bark para mejorar la naturalidad de la voz clonada.

## ¿Por qué está vacía esta carpeta?

Esta carpeta está vacía porque el paquete RVC:

1. **Es pesado** (~2-4 GB) - No es práctico incluirlo en el repositorio de git
2. **Tiene licencia propia** - RVC tiene su propia licencia que difiere de la de este proyecto
3. **Se actualiza frecuentemente** - Mantenerlo separado permite actualizar sin afectar el proyecto principal
4. **Es opcional** - No todos los usuarios necesitan RVC, solo quienes quieran post-procesamiento de voz

## Cómo obtener el paquete

### Opción 1: Descargar release (Recomendado)

1. Ir a: https://github.com/Tiger14n/RVC-GUI/releases/tag/Windows-pkg
2. Descargar el archivo comprimido (`.zip` o `.7z`)
3. Extraer todo el contenido en esta carpeta (`RVC-GUI-pkg/`)
4. Verificar que la estructura sea similar a:

```
RVC-GUI-pkg/
├── inference/
├── configs/
├── weights/
└── ...
```

### Opción 2: Clonar repositorio completo

```bash
# Desde la raíz del proyecto
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
```

**Nota:** Esta opción es más pesada y requiere instalar dependencias adicionales.

## ¿Para qué sirve RVC?

RVC se usa para:

| Uso | Descripción |
|-----|-------------|
| **Conversión de voz** | Transformar una voz generada por Bark en otra voz específica |
| **Ajuste de tono** | Subir o bajar el tono de la voz |
| **Ajuste de timbre** | Modificar las características de la voz |
| **Mejora de naturalidad** | Hacer que la voz suene más natural y menos robótica |

### Ejemplo de uso

```bash
# 1. Generar audio con Bark
python bark_cli.py generate "Hola mundo" -v es_speaker_0 -o bark_output.wav

# 2. Aplicar RVC para convertir la voz
python -c "
from rvc_infer import get_vc, vc_single
get_vc('modelo.pth', 'cuda:0', True)
audio = vc_single(0, 'bark_output.wav', f0_up_key=-6, ...)
"
```

## Configuración

### Modelo RVC

Necesitas un modelo RVC entrenado (archivo `.pth`). Puedes:

1. **Entrenar tu propio modelo** con la GUI de RVC
2. **Descargar modelos pre-entrenados** de comunidades
3. **Usar el modelo de ejemplo** incluido en algunos releases

### Archivos necesarios

| Archivo | Descripción |
|---------|-------------|
| `modelo.pth` | Modelo RVC entrenado |
| `modelo.index` | Índice para búsqueda de voz (opcional pero recomendado) |

## Solución de Problemas

### "RVC no encontrado"

Asegúrate de que los archivos estén en esta carpeta y no en un subdirectorio.

### "Error al cargar modelo"

Verifica que el modelo `.pth` esté completo y no corrupto.

### "CUDA out of memory"

Reduce el `batch_size` o usa CPU en su lugar.

## Enlaces útiles

- [Repositorio oficial de RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)
- [RVC-GUI (versión simplificada)](https://github.com/Tiger14n/RVC-GUI)
- [Documentación de RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/wiki)

## Notas importantes

- RVC es **opcional** - Bark funciona sin él
- Se recomienda usar GPU para mejor rendimiento
- Los modelos RVC deben ser entrenados con cuidado para obtener buenos resultados
- El uso de RVC debe respetar los derechos de voz de las personas
