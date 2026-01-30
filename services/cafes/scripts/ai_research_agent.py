#!/usr/bin/env python3
"""
================================================================================
PROYECTO: CAFES - Agente de Investigación Local
ARCHIVO:  scripts/ai_research_agent.py
DESCRIPCIÓN: 
  1. Conecta con Ollama (Local LLM) para entender el negocio.
  2. Navega en internet (DuckDuckGo/Google) para buscar competidores y datos.
  3. Estructura la información y actualiza la base de datos.
REQUISITOS:
  - pip install ollama selenium webdriver_manager mysql-connector-python beautifulsoup4
  - Ollama corriendo localmente (`ollama serve`)
  - Modelo instalado: `ollama pull gemma2:2b` (o llama3)
================================================================================
"""

import os
import json
import time
import sys
import mysql.connector
from typing import List, Dict

# Intentar importar librerías externas (manejo de errores si no están instaladas)
try:
    import ollama
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from webdriver_manager.chrome import ChromeDriverManager
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"❌ Error de dependencias: {e}")
    print("Ejecuta: pip install ollama selenium webdriver_manager mysql-connector-python beautifulsoup4")
    # sys.exit(1) # Comentado para permitir que el script se cree sin dependencias instaladas aún

# Configuración
OLLAMA_MODEL = "gemma:2b"  # Modelo ligero y rápido
DB_CONFIG = {
    'user': 'fondoth1_fondoth1_agent',  # Usuario Remoto
    'password': 'AgenteRemoto2026',       # Contraseña Remota
    'host': 'mx112.hostgator.mx',     # Host de HostGator
    'port': 3306,
    'database': 'fondoth1_plania'     # Base de Datos Remota
}

class CafesResearcher:
    def __init__(self):
        self.driver = None
        
    def connect_db(self):
        return mysql.connector.connect(**DB_CONFIG)

    def start_browser(self):
        """Inicia el navegador en modo Headless (oculto)"""
        print("🌐 Iniciando navegador invisible...")
        chrome_options = Options()
        chrome_options.add_argument("--headless") # Comentar para ver el navegador
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # User agent para parecer humano
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def close_browser(self):
        if self.driver:
            self.driver.quit()

    def ask_ollama(self, prompt: str) -> str:
        """Consulta al LLM local"""
        print(f"🧠 Consultando a {OLLAMA_MODEL}...")
        try:
            response = ollama.chat(model=OLLAMA_MODEL, messages=[
                {'role': 'user', 'content': prompt},
            ])
            return response['message']['content']
        except Exception as e:
            return f"Error Ollama: {str(e)}"

    def search_web(self, query: str) -> List[Dict]:
        """Realiza una búsqueda web y extrae resultados"""
        print(f"🔍 Buscando: '{query}'")
        results = []
        
        try:
            # Usar DuckDuckGo para evitar bloqueos de Google
            self.driver.get(f"https://duckduckgo.com/?q={query}&t=h_&ia=web")
            time.sleep(3) # Esperar carga
            
            # Scrapear resultados básicos
            links = self.driver.find_elements(By.CSS_SELECTOR, "article h2 a")
            snippets = self.driver.find_elements(By.CSS_SELECTOR, "article div[class*='snippet']")
            
            for i in range(min(3, len(links))): # Top 3 resultados
                title = links[i].text
                url = links[i].get_attribute("href")
                snippet = snippets[i].text if i < len(snippets) else ""
                
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet
                })
                print(f"   📄 Encontrado: {title}")
                
        except Exception as e:
            print(f"   ⚠️ Error en búsqueda: {e}")
            
        return results

    def update_project_db(self, project_id: int, data: Dict):
        """Actualiza la base de datos con la información extraída"""
        print("💾 Guardando información en la base de datos...")
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            # 1. Competidores (JSON)
            competidores_json = json.dumps(data.get("competidores", []), ensure_ascii=False)
            
            # 2. Costos Fijos (Numerico)
            costos_fijos = data.get("costos_fijos_estimados", 0)
            if isinstance(costos_fijos, str):
                # Limpiar string si viene como "$5,000"
                costos_fijos = float(costos_fijos.replace("$", "").replace(",", "").strip())
                
            # 3. Propuesta de Valor (Texto)
            propuesta = data.get("propuesta_valor_sugerida", "")
            
            # 4. Segmento Cliente (Texto)
            cliente = data.get("perfil_cliente", "")
            
            # Construir Query Dinámica
            sql = """
                UPDATE proyectos_negocio 
                SET d3_competidores_json = %s,
                    g5_costos_fijos_mensuales = IF(g5_costos_fijos_mensuales = 0 OR g5_costos_fijos_mensuales IS NULL, %s, g5_costos_fijos_mensuales),
                    d5_ventaja_competitiva = IF(d5_ventaja_competitiva = '' OR d5_ventaja_competitiva IS NULL, %s, d5_ventaja_competitiva),
                    d1_segmento_cliente = IF(d1_segmento_cliente = '' OR d1_segmento_cliente IS NULL, %s, d1_segmento_cliente)
                WHERE id_proyecto = %s
            """
            
            cursor.execute(sql, (competidores_json, costos_fijos, propuesta, cliente, project_id))
            conn.commit()
            print(f"✅ ¡Proyecto {project_id} actualizado correctamente!")
            
        except Exception as e:
            print(f"❌ Error guardando en BD: {e}")
        finally:
            cursor.close()
            conn.close()

    def analyze_project(self, project_id: int):
        """Flujo principal del agente"""
        conn = self.connect_db()
        cursor = conn.cursor(dictionary=True)
        
        # 1. Obtener datos básicos
        cursor.execute("SELECT * FROM proyectos_negocio WHERE id_proyecto = %s", (project_id,))
        project = cursor.fetchone()
        conn.close() # Cerrar conexión de lectura
        
        if not project:
            print("❌ Proyecto no encontrado")
            return

        nombre = project.get('a1_nombre_negocio', 'Negocio')
        descripcion = project.get('b1_descripcion_negocio', '')
        ubicacion = project.get('d8_direccion_formateada', 'Hermosillo, Sonora')
        
        print(f"🚀 Iniciando investigación para: {nombre}")
        print(f"📍 Ubicación: {ubicacion}")
        
        # 2. Ollama: Planear Búsqueda
        prompt_plan = f"""
        Actúa como un experto consultor de negocios. Necesito investigar para un plan de negocios de '{nombre}'.
        Descripción: {descripcion[:200]}
        Ubicación: {ubicacion}
        
        Genera 2 frases de búsqueda precisas para encontrar:
        1. Competidores directos en la zona.
        2. Precios de productos similares.
        
        Responde SOLO con las frases separadas por una línea nueva, nada más.
        """
        search_queries = self.ask_ollama(prompt_plan).strip().split('\n')
        search_queries = [q.strip() for q in search_queries if q.strip()]
        
        # 3. Navegar e Investigar
        self.start_browser()
        raw_info = ""
        
        for query in search_queries:
            results = self.search_web(query)
            for res in results:
                raw_info += f"Título: {res['title']}\nTexto: {res['snippet']}\n\n"
        
        self.close_browser()
        
        # 4. Ollama: Sintetizar y Estructurar
        prompt_analysis = f"""
        Con base en esta información encontrada en la web:
        {raw_info[:3000]}
        
        Para el negocio '{nombre}' en {ubicacion}, genera un JSON válido con esta estructura (si no hay datos exactos, estímalos razonablemente basado en el contexto):
        
        {{
            "competidores": [
                {{"nombre": "Nombre Comp 1", "precio_referencia": 0}},
                {{"nombre": "Nombre Comp 2", "precio_referencia": 0}}
            ],
            "costos_fijos_estimados": 0,
            "propuesta_valor_sugerida": "Texto breve",
            "perfil_cliente": "Texto breve"
        }}
        
        Responde SOLO con el JSON.
        """
        
        json_str = self.ask_ollama(prompt_analysis)
        
        # Limpiar respuesta JSON (Ollama a veces pone ```json ... ```)
        json_str = json_str.replace("```json", "").replace("```", "").strip()
        
        try:
            data = json.loads(json_str)
            print("\n📈 RESULTADOS DE LA INVESTIGACIÓN:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Guardar en BD
            self.update_project_db(project_id, data)
            
        except json.JSONDecodeError:
            print("❌ Error parseando JSON de Ollama")
            print(json_str)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 ai_research_agent.py <ID_PROYECTO>")
        # Demo mode
        print("\n--- MODO DEMO (Sin ID) ---")
        agent = CafesResearcher()
        # agent.analyze_project(42) # Descomentar para probar con ID real
    else:
        agent = CafesResearcher()
        agent.analyze_project(int(sys.argv[1]))
