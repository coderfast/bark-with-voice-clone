"""Generate images using Duck.ai (free, no API key)."""

import base64
import time
from pathlib import Path

from duckmind import DuckMind, image_gen

IMAGES_DIR = Path(__file__).parent / "images"

# Filename → prompt (only for images that are still placeholders)
IMAGE_PROMPTS = {
    "05_srai_cadena.png": "Technical flowchart showing SRAI redirection chain: BUENOS DIAS -> HOLA -> Hello!, with arrows and central node, modern clean style, blue and white colors",
    "06_condiciones_arbol.png": "Decision tree diagram of a chatbot showing conditionals: if-else with branches for mood happy sad angry, with emoji icons and responses, modern tree style",
    "07_random_respuestas.png": "Illustration of random response selection: dice or roulette with multiple response options emerging, modern conceptual style, flat design",
    "08_contexto_conversacion.png": "UML sequence diagram showing conversation context: User Bot that previous response next response, with chat bubbles, modern sequence style",
    "09_sistema_temas.png": "Container diagram showing topics as boxes grouping related categories: TOPIC WEATHER with weather categories inside, modern container diagram style",
    "10_variables_alcance.png": "Scope diagram showing 3 levels of AIML variables: user session, bot global, topic topic, with concentric circles, modern diagram style",
    "11_operaciones_lista.png": "Infographic of list operations: list, first, rest, size, repeat, loop, with icons and visual examples for each operation, icon grid style",
    "12_historial_conversacion.png": "Visual timeline of conversation history showing: input 1, input 2, input 3 with timestamps and content, modern timeline style",
    "13_aprendizaje_ciclo.png": "Circular diagram of dynamic learning cycle: learn use unlearn learn, with brain icons and circular arrows, modern circular diagram",
    "14_transformaciones_texto.png": "Pipeline diagram of text transformations: input person person2 gender formal output, with arrows and visual examples, modern pipeline style",
    "15_operaciones_sistema.png": "Icon grid showing system operations: thinking brain, date clock, eval terminal, system server, with modern icons",
    "16_formato_respuesta.png": "UI mockup of rich chatbot response showing: formatted text, links, images, tables, inside a window frame, modern UI mockup style",
    "17_patrones_conversacion.png": "Mind map of conversation patterns: greeting, farewell, fallback, confirmation, multi-turn, with branches and colors, modern mind map style",
    "18_patrones_personalidad.png": "Chatbot personality diagram showing: formal, casual, funny, empathetic, with scales and indicators, modern personality diagram style",
    "19_patrones_memoria.png": "Memory architecture diagram: short-term RAM, long-term disk, preferences database, context buffer, with storage icons, modern memory diagram",
    "20_testing_debugging.png": "CI/CD pipeline diagram: unit tests integration tests performance tests deploy, with checkmarks and bug icons, modern pipeline style",
    "21_optimizacion.png": "Dashboard showing optimization metrics: response time, memory usage, cache hit ratio, with charts and KPIs, modern dashboard style",
    "22_organizacion_proyectos.png": "File tree diagram of AIML project structure: main.aiml, modules, topics, tests, data, with folder and file icons, modern tree style",
    "23_mejores_practicas.png": "Visual checklist of best practices: clean code, security, testing, documentation, with checkmarks and X marks, infographic checklist style",
    "24_bot_cliente.png": "Customer service chatbot UI mockup showing: options menu, FAQ, support form, modern UI design",
    "25_bot_educativo.png": "Educational chatbot interface showing: active lesson, interactive quiz, student progress, modern e-learning UI",
    "26_bot_salud.png": "Health chatbot interface with warnings: symptom form, recommendations, emergency button, modern medical UI style",
    "27_bot_multilingue.png": "Multilingual chatbot diagram showing: language detection, translation, responses in multiple languages, with flags and text, modern internationalization style",
    "28_integracion_llm.png": "Hybrid architecture diagram AIML plus LLM: AIML as control layer fallback to LLM response, with brain and rules icons, modern architecture diagram",
    "29_despliegue_produccion.png": "Production deployment diagram: Docker Load Balancer Instances Monitoring, with container icons and charts, modern DevOps diagram style",
}


def generate_image(client: DuckMind, filename: str, prompt: str) -> bool:
    """Generate an image using Duck.ai and save it."""
    out_path = IMAGES_DIR / filename
    full_prompt = f"Generate an image: {prompt}. Only output the image, no text."

    try:
        print(f"  Generating {filename}...")
        # The image model returns the image in the stream
        # We need to collect the response and decode it
        response = client.ask(full_prompt, model=image_gen)

        # Check if response contains base64 image data
        if "data:image" in response:
            # Extract base64 data
            b64_data = response.split("base64,")[1].split('"')[0]
            img_bytes = base64.b64decode(b64_data)
            out_path.write_bytes(img_bytes)
            size_kb = out_path.stat().st_size / 1024
            print(f"    OK ({size_kb:.1f} KB)")
            return True
        elif response.startswith("data:"):
            # Handle case where response is just the data URI
            b64_data = response.split("base64,")[1]
            img_bytes = base64.b64decode(b64_data)
            out_path.write_bytes(img_bytes)
            size_kb = out_path.stat().st_size / 1024
            print(f"    OK ({size_kb:.1f} KB)")
            return True
        else:
            # Response might be raw base64 or just text
            # Try to decode as base64
            try:
                img_bytes = base64.b64decode(response)
                if len(img_bytes) > 1000:  # Reasonable image size
                    out_path.write_bytes(img_bytes)
                    size_kb = out_path.stat().st_size / 1024
                    print(f"    OK ({size_kb:.1f} KB)")
                    return True
            except Exception:
                pass
            print(f"    WARN: Unexpected response format: {response[:200]}")
            return False
    except Exception as e:
        print(f"    ERROR: {e}")
        return False


def main():
    IMAGES_DIR.mkdir(exist_ok=True)

    # Check which images are still placeholders (< 50KB)
    to_generate = []
    for filename, prompt in IMAGE_PROMPTS.items():
        img_path = IMAGES_DIR / filename
        if img_path.exists() and img_path.stat().st_size > 50_000:
            print(f"  Skipping {filename} (already {img_path.stat().st_size // 1024} KB)")
        else:
            to_generate.append((filename, prompt))

    if not to_generate:
        print("All images are already generated!")
        return

    print(f"\nGenerating {len(to_generate)} images via Duck.ai...\n")

    # Create client with image generation model
    client = DuckMind(model="image-generation")

    success = 0
    for i, (filename, prompt) in enumerate(to_generate):
        if i > 0:
            time.sleep(3)  # Rate limit - be generous
        if generate_image(client, filename, prompt):
            success += 1

    client.close()
    print(f"\nDone: {success}/{len(to_generate)} images generated")
    print(f"Images saved to: {IMAGES_DIR}")


if __name__ == "__main__":
    main()
