# =================================================================================
# PROYECTO: PlanIA (LLM Client)
# ARCHIVO: modules/llm_client.py
# COPYRIGHT: © 2026 Fondo Thoth AC.
# LICENCIA: MIT
# DESCRIPCIÓN: Cliente para interactuar con modelos de lenguaje locales (Ollama).
# =================================================================================

import os
import json
import logging
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger("LLMClient")

class LLMClient:
    """
    Cliente para conectar con Ollama o servidores compatibles con OpenAI API.
    """
    
    def __init__(self, base_url: str = "http://host.docker.internal:11434", model: str = "gemma2:9b"):
        """
        Inicializa el cliente LLM.
        
        Args:
            base_url: URL base del servicio Ollama (por defecto usa host.docker.internal para Docker)
            model: Nombre del modelo a usar (gemma2:9b, llama3, mistral)
        """
        self.base_url = os.getenv("OLLAMA_HOST", base_url)
        self.model = os.getenv("OLLAMA_MODEL", model)
        self.available = False
        
    def check_health(self) -> bool:
        """Verifica si el servicio LLM está disponible."""
        try:
            # Ollama API check
            res = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if res.status_code == 200:
                self.available = True
                logger.info(f"🟢 LLM Service Available: {self.base_url} (Model: {self.model})")
                return True
        except Exception as e:
            logger.warning(f"🔴 LLM Service Unavailable at {self.base_url}: {e}")
        
        self.available = False
        return False

    def generate(self, prompt: str, system: str = "", temperature: float = 0.7) -> Optional[str]:
        """
        Genera texto usando el modelo local.
        
        Returns:
            Texto generado o None si falla.
        """
        if not self.available and not self.check_health():
            return None

        # Endpoint de generación de Ollama
        url = f"{self.base_url}/api/generate"
        
        # Construir prompt completo
        full_prompt = f"{system}\n\nUser: {prompt}\nAssistant:" if system else prompt
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "temperature": temperature,
            "options": {
                "num_ctx": 4096 # Context window
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
            else:
                logger.error(f"LLM Generation Failed ({response.status_code}): {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"LLM Connection Error: {e}")
            return None

    def generate_json(self, prompt: str, schema: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Intenta generar una respuesta en formato JSON válido.
        """
        json_prompt = f"""
        {prompt}
        
        IMPORTANT: Respond ONLY with a valid JSON object matching this structure:
        {json.dumps(schema, indent=2)}
        
        Do not include markdown formatting (```json), just the raw JSON string.
        """
        
        result = self.generate(json_prompt, temperature=0.2)
        if not result:
            return None
            
        try:
            # Limpiar posible markdown
            clean_result = result.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_result)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from LLM: {result[:100]}...")
            return None
