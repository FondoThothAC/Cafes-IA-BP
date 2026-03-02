import json
import urllib.request
import threading
import time

# Configuración de los modelos
MODELS = ["llama3.2:latest", "qwen2.5:3b", "phi3:latest", "gemma2:2b"]
SYNTHESIZER = "llama3.2:latest"
OLLAMA_URL = "http://localhost:11434/api/chat"
TIMEOUT = 60 # Segundos por modelo

def call_ollama(model, prompt, results, index):
    """Llamada a la API de Ollama para un modelo específico."""
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    
    start_time = time.time()
    try:
        req = urllib.request.Request(OLLAMA_URL, data=json.dumps(data).encode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            response = json.loads(resp.read().decode('utf-8'))
            results[index] = response['message']['content']
            elapsed = time.time() - start_time
            print(f"--- Agente {model} completado en {elapsed:.1f}s")
    except Exception as e:
        results[index] = f"Error con {model}: {str(e)}"
        print(f"--- Agente {model} FALLÓ: {str(e)}")

def run_swarm(prompt):
    print(f"\n--- Iniciando Enjambre (MoA) ---")
    print(f"Pregunta: {prompt}\n")
    
    results = [None] * len(MODELS)
    threads = []
    
    for i, model in enumerate(MODELS):
        t = threading.Thread(target=call_ollama, args=(model, prompt, results, i))
        threads.append(t)
        t.start()
        print(f"--- Agente {model} iniciado...")

    for t in threads:
        t.join()
    
    print("\n--- Respuestas obtenidas. Sintetizando... ---")
    
    valid_responses = [r for r in results if r and not r.startswith("Error")]
    if not valid_responses:
        print("Error: No se obtuvieron respuestas válidas de los agentes.")
        return
    
    synthetic_prompt = f"Has recibido {len(valid_responses)} respuestas a: \"{prompt}\"\n\n"
    for i, res in enumerate(valid_responses):
        synthetic_prompt += f"Respuesta {i+1}: {res}\n\n"
    
    synthetic_prompt += "Genera una síntesis final superior en español."

    final_result = [None]
    call_ollama(SYNTHESIZER, synthetic_prompt, final_result, 0)
    
    print("\n--- Respuesta Final del Enjambre ---")
    print(final_result[0])
    return final_result[0]

if __name__ == "__main__":
    test_prompt = "¿Cuáles son las 3 estrategias de marketing más efectivas para una pequeña empresa de software?"
    run_swarm(test_prompt)
