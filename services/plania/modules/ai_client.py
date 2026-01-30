# =================================================================================
# PROYECTO: PlanIA - AI Client with Multimodal Support
# ARCHIVO: modules/ai_client.py
# COPYRIGHT: © 2026 Fondo Thoth AC.
# LICENCIA: MIT
# DESCRIPCIÓN: Cliente para Ollama con soporte para Gemma3n multimodal
# =================================================================================
import requests
import json
import os
import base64
from typing import Optional, List, Dict, Any


class AIClient:
    """
    Cliente de IA para Ollama con soporte multimodal (texto + imágenes).
    Usa Gemma3n por defecto pero soporta cualquier modelo de Ollama.
    """
    
    def __init__(self):
        # Primero busca OLLAMA_HOST, luego AI_API_URL para compatibilidad
        self.api_url = os.getenv("OLLAMA_HOST", 
                                  os.getenv("AI_API_URL", "http://localhost:11434"))
        self.default_model = os.getenv("OLLAMA_MODEL", "gemma3:4b-it")
        self.timeout = int(os.getenv("OLLAMA_TIMEOUT", "120"))
    
    def chat(self, prompt: str, model: str = None, images: List[str] = None, 
             system: str = None) -> Optional[str]:
        """
        Send a prompt to the AI model with optional multimodal input.
        
        Args:
            prompt: The text prompt to send
            model: Model name (default: gemma3:4b-it)
            images: List of base64-encoded images for vision models
            system: Optional system prompt for context
            
        Returns:
            The model's response text or None on error
        """
        model = model or self.default_model
        url = f"{self.api_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        # Add images for multimodal models (Gemma3n, LLaVA, etc.)
        if images:
            payload["images"] = images
            
        # Add system prompt if provided
        if system:
            payload["system"] = system
        
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.Timeout:
            print(f"[AI Error] Request timed out after {self.timeout}s")
            return None
        except requests.exceptions.ConnectionError:
            print(f"[AI Error] Could not connect to Ollama at {self.api_url}")
            return None
        except Exception as e:
            print(f"[AI Error] Unexpected error: {e}")
            return None
    
    def chat_conversation(self, messages: List[Dict], model: str = None) -> Optional[str]:
        """
        Send a conversation (multiple messages) to the AI model.
        Uses the /api/chat endpoint for proper conversation handling.
        
        Args:
            messages: List of {"role": "user/assistant/system", "content": "..."}
            model: Model name (default: gemma3:4b-it)
            
        Returns:
            The model's response text or None on error
        """
        model = model or self.default_model
        url = f"{self.api_url}/api/chat"
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "")
        except Exception as e:
            print(f"[AI Error] Chat conversation failed: {e}")
            return None

    # =========================================================================
    # SPECIALIZED ANALYSIS FUNCTIONS
    # =========================================================================
    
    def analyze_project(self, project_data: Dict) -> Optional[str]:
        """Generate a strategic analysis of the business project."""
        system = """Eres un Consultor Senior de Negocios experto en PYMES mexicanas.
        Analiza proyectos de emprendimiento y proporciona recomendaciones prácticas
        y accionables. Responde siempre en español."""
        
        prompt = f"""
        Analiza el siguiente proyecto de negocio y proporciona:
        1. Fortalezas identificadas
        2. Áreas de mejora
        3. 3 recomendaciones estratégicas específicas
        
        Datos del proyecto:
        {json.dumps(project_data, indent=2, ensure_ascii=False)}
        """
        return self.chat(prompt=prompt, system=system)
    
    def analyze_image(self, image_base64: str, context: str = "") -> Optional[str]:
        """
        Analyze an image using Gemma3n's vision capabilities.
        
        Args:
            image_base64: Base64-encoded image
            context: Additional context about what to analyze
            
        Returns:
            Analysis of the image
        """
        system = """Eres un experto en branding y diseño visual para negocios.
        Analiza imágenes de logos, productos y locales comerciales proporcionando
        feedback constructivo y profesional. Responde en español."""
        
        prompt = f"""
        Analiza esta imagen y proporciona:
        1. Descripción objetiva de lo que ves
        2. Fortalezas del diseño/presentación
        3. Sugerencias de mejora
        {f"Contexto adicional: {context}" if context else ""}
        """
        return self.chat(prompt=prompt, images=[image_base64], system=system)
    
    def analyze_market(self, project_data: Dict, inegi_data: Dict = None, 
                       competitors: List[Dict] = None) -> Optional[str]:
        """
        Analyze market conditions for a business project.
        
        Args:
            project_data: Basic project information
            inegi_data: Demographic data from INEGI API
            competitors: List of competitors from DENUE
            
        Returns:
            Market analysis and recommendations
        """
        system = """Eres un analista de mercado especializado en México.
        Utilizas datos de INEGI y DENUE para proporcionar análisis de mercado
        precisos y recomendaciones basadas en datos. Responde en español."""
        
        data = {
            "proyecto": project_data,
            "demograficos": inegi_data or {},
            "competidores": competitors or []
        }
        
        prompt = f"""
        Realiza un análisis de mercado completo:
        
        1. ANÁLISIS DEMOGRÁFICO
        - Tamaño del mercado objetivo
        - Características de la población
        
        2. ANÁLISIS COMPETITIVO
        - Nivel de competencia
        - Diferenciadores potenciales
        
        3. OPORTUNIDADES Y AMENAZAS
        - Oportunidades de mercado
        - Riesgos a considerar
        
        4. RECOMENDACIONES
        - Estrategia de entrada recomendada
        - Segmento prioritario
        
        Datos:
        {json.dumps(data, indent=2, ensure_ascii=False)}
        """
        return self.chat(prompt=prompt, system=system)
    
    def analyze_financials(self, project_data: Dict) -> Optional[str]:
        """
        Analyze financial projections and provide recommendations.
        
        Args:
            project_data: Project data including financial fields
            
        Returns:
            Financial analysis and recommendations
        """
        system = """Eres un asesor financiero especializado en PYMES y startups.
        Analizas proyecciones financieras y proporcionas recomendaciones prácticas
        para mejorar la viabilidad de los negocios. Responde en español."""
        
        # Extract financial fields
        financial_fields = {k: v for k, v in project_data.items() 
                          if 'costo' in k.lower() or 'inversion' in k.lower() 
                          or 'precio' in k.lower() or 'monto' in k.lower()
                          or 'ingreso' in k.lower() or 'gasto' in k.lower()}
        
        prompt = f"""
        Analiza la situación financiera del proyecto:
        
        1. VIABILIDAD FINANCIERA
        - ¿Los números tienen sentido?
        - ¿La inversión es razonable para el sector?
        
        2. RIESGOS FINANCIEROS
        - Posibles problemas de flujo de efectivo
        - Dependencias críticas
        
        3. RECOMENDACIONES
        - Cómo optimizar costos
        - Oportunidades de financiamiento
        - Metas financieras sugeridas
        
        Datos financieros:
        {json.dumps(financial_fields, indent=2, ensure_ascii=False)}
        
        Contexto del negocio:
        Nombre: {project_data.get('a1_nombre_negocio', 'No especificado')}
        Descripción: {project_data.get('b1_descripcion_negocio', 'No especificada')}
        """
        return self.chat(prompt=prompt, system=system)
    
    def generate_recommendations(self, project_data: Dict, module: str) -> Optional[str]:
        """
        Generate specific recommendations for a module.
        
        Args:
            project_data: Full project data
            module: Module name (marketing, finance, organization, etc.)
            
        Returns:
            Specific recommendations for the module
        """
        module_prompts = {
            "marketing": "estrategias de marketing y promoción",
            "finance": "gestión financiera y flujo de efectivo",
            "organization": "estructura organizacional y recursos humanos",
            "market": "posicionamiento de mercado y competencia",
            "operations": "procesos operativos y producción",
            "brand": "identidad de marca y diferenciación"
        }
        
        focus = module_prompts.get(module, "aspectos generales del negocio")
        
        system = f"""Eres un consultor experto en {focus} para PYMES mexicanas.
        Proporciona recomendaciones prácticas, específicas y accionables.
        Responde en español con un tono profesional pero accesible."""
        
        prompt = f"""
        Basándote en los datos del proyecto, proporciona 5 recomendaciones
        específicas para mejorar {focus}:
        
        Proyecto: {project_data.get('a1_nombre_negocio', 'Sin nombre')}
        Descripción: {project_data.get('b1_descripcion_negocio', 'Sin descripción')}
        
        Para cada recomendación incluye:
        - Acción específica a tomar
        - Por qué es importante
        - Cómo implementarla (pasos básicos)
        
        Datos completos:
        {json.dumps(project_data, indent=2, ensure_ascii=False)}
        """
        return self.chat(prompt=prompt, system=system)

    # =========================================================================
    # UTILITY FUNCTIONS
    # =========================================================================
    
    def is_available(self) -> bool:
        """Check if the Ollama server is available."""
        try:
            response = requests.get(f"{self.api_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[str]:
        """Get list of available models on the Ollama server."""
        try:
            response = requests.get(f"{self.api_url}/api/tags", timeout=10)
            response.raise_for_status()
            models = response.json().get("models", [])
            return [m.get("name") for m in models]
        except:
            return []
    
    @staticmethod
    def image_to_base64(image_path: str) -> Optional[str]:
        """Convert an image file to base64 string."""
        try:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            print(f"[AI Error] Could not read image: {e}")
            return None
