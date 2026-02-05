# =================================================================================
# PROYECTO: PlanIA (Bob Agent - Autonomous Project Completion)
# ARCHIVO: modules/bob_agent.py
# COPYRIGHT: © 2026 Fondo Thoth AC.
# LICENCIA: MIT
# DESCRIPCIÓN: Agente autónomo para completar proyectos de negocio usando RAG,
#              investigación web, y LLMs locales.
# =================================================================================

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from .web_research_client import WebResearchClient
from .ocr_mapper import OCRMapper
from .rag_engine import RAGEngine
from .llm_client import LLMClient
from .audit_logger import AuditLogger
from .translator import TranslatorService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BobAgent")

# ==============================================================================
# CONSTANTS
# ==============================================================================

# Project complexity levels
COMPLEXITY_MICRO = "micro"          # Panadería, tiendita, servicios locales
COMPLEXITY_STARTUP = "startup"      # Tech startup, franquicia, e-commerce
COMPLEXITY_ENTERPRISE = "enterprise"  # Manufactura, SaaS B2B, exportación

# Module definitions mapping to DB fields
MODULES = {
    "identidad": {
        "fields": ["a1_nombre_negocio", "a2_tipo_empresa", "a3_descripcion_negocio", 
                   "b1_vision", "b2_mision", "b3_propuesta_valor"],
        "required_for_analysis": ["a1_nombre_negocio", "a3_descripcion_negocio"],
        "weight": 1.0
    },
    "mercado": {
        "fields": ["d1_segmento_cliente", "d2_segmento_json", "d3_competidores_json",
                   "d4_tamano_mercado", "d5_ventaja_competitiva", "d6_analisis_mercado_json"],
        "required_for_analysis": ["d1_segmento_cliente"],
        "weight": 1.5
    },
    "productos": {
        "fields": ["e1_proceso_produccion", "e2_capacidad_produccion", "e3_productos_bom_json",
                   "g12_proyeccion_ingresos_json"],
        "required_for_analysis": ["g12_proyeccion_ingresos_json"],
        "weight": 1.5
    },
    "organizacion": {
        "fields": ["c1_forma_legal", "c2_estructura_accionaria", "c3_equipo_fundador",
                   "c4_organigrama_json"],
        "required_for_analysis": ["c4_organigrama_json"],
        "weight": 1.0
    },
    "finanzas": {
        "fields": ["g5_costos_fijos_mensuales", "g6_punto_equilibrio", "g7_roi_esperado",
                   "g8_inversion_inicial", "h_presupuesto_inversion_json"],
        "required_for_analysis": ["g8_inversion_inicial", "g5_costos_fijos_mensuales"],
        "weight": 2.0
    },
    "marketing": {
        "fields": ["f1_estrategia_precio", "f2_estrategia_producto", "f3_canales_venta",
                   "f4_estrategia_promocion"],
        "required_for_analysis": ["f3_canales_venta"],
        "weight": 1.0
    }
}

# Industry-specific prompts
INDUSTRY_KEYWORDS = {
    "panaderia": ["pan", "panadería", "pastelería", "repostería", "tortillería", "bakery"],
    "restaurante": ["restaurante", "comida", "cocina", "alimentos", "fonda", "cafetería", "bar", "restaurant"],
    "tienda": ["tienda", "abarrotes", "minisuper", "comercio", "retail", "venta"],
    "servicios": ["servicio", "consultoría", "taller", "reparación", "mantenimiento", "salón"],
    "manufactura": ["fábrica", "manufactura", "producción", "industrial", "maquila"],
    "tecnologia": ["software", "app", "tecnología", "saas", "plataforma", "digital", "tech", "startup"]
}


# ==============================================================================
# BOB AGENT CLASS
# ==============================================================================

class BobAgent:
    """
    Agente autónomo para completar proyectos de negocio.
    
    Capacidades:
    - Analizar completitud del proyecto
    - Determinar complejidad del negocio
    - Consultar RAG de metodologías
    - Investigar web para datos de mercado
    - Generar sugerencias con LLM
    - Mantener contexto en Markdown por proyecto
    """
    
    def __init__(self, project_id: int, db_connection=None):
        """
        Inicializa el agente Bob para un proyecto específico.
        
        Args:
            project_id: ID del proyecto en la base de datos
            db_connection: Conexión a la base de datos (opcional)
        """
        self.project_id = project_id
        self.db = db_connection
        self.project: Dict[str, Any] = {}
        self.context_md: str = ""
        self.complexity: str = COMPLEXITY_MICRO
        self.industry: str = "general"
        self.completeness: Dict[str, float] = {}
        
        # Paths
        self.base_path = Path(__file__).parent.parent
        self.docs_path = self.base_path / "docs" / "metodologias"
        self.data_path = self.base_path / "data" / "projects" / str(project_id)
        
        # Initialize Clients
        self.research_client = WebResearchClient()
        self.ocr_mapper = OCRMapper()
        
        # Initialize RAG Engine
        self.rag = RAGEngine(persist_directory=str(self.base_path / "data" / "chroma_db"))
        
        self.web_service_available = False # Will check on first use
        
        # Initialize RAG Engine
        self.rag = RAGEngine(persist_directory=str(self.base_path / "data" / "chroma_db"))
        self._index_knowledge_base()
        
        # Initialize LLM Client
        self.llm = LLMClient()
        
        # Initialize Audit & Translation
        self.audit = AuditLogger()
        self.translator = TranslatorService()
        
        self.web_service_available = False # Will check on first use
        
        if not self.db:
            # Try to auto-connect if possible
            from .db_connector import get_db_connection
            self.db = get_db_connection()
            
        logger.info(f"🤖 Bob Agent initialized for project {project_id}")
        self.audit.log_action("BobAgent", "init", f"project:{project_id}", {"msg": "Agent initialized"})

    def save_agent_state(self):
        """
        Guarda el estado del agente (complejidad, timestamp, contexto) en la BD.
        """
        if not self.db:
            logger.warning("No DB connection available to save agent state")
            return

        try:
            cursor = self.db.cursor()
            sql = """
                UPDATE proyectos_negocio 
                SET agent_complexity = %s,
                    agent_context_md = %s,
                    ia_fecha_procesamiento = NOW(),
                    ia_flag_procesar = FALSE
                WHERE id_proyecto = %s
            """
            cursor.execute(sql, (self.complexity, self.context_md, self.project_id))
            self.db.commit()
            logger.info("💾 Agent state saved to DB")
            cursor.close()
        except Exception as e:
            logger.error(f"Error saving agent state: {e}")

    def _index_knowledge_base(self):
        """Si la base de conocimiento está vacía, indexar los documentos MD."""
        # Simple check: query for anything
        count = len(self.rag.query("test", n_results=1))
        
        if count == 0:
            logger.info("🗂️ Indexing Knowledge Base into ChromaDB...")
            for md_file in self.docs_path.rglob("*.md"):
                try:
                    content = md_file.read_text(encoding="utf-8")
                    self.rag.add_document(
                        doc_id=md_file.name,
                        text=content,
                        metadata={"source": md_file.name, "category": md_file.parent.name}
                    )
                except Exception as e:
                    logger.error(f"Error indexing {md_file}: {e}")
    
    # --------------------------------------------------------------------------
    # Data Loading
    # --------------------------------------------------------------------------
    
    def load_project(self) -> Dict[str, Any]:
        """Carga los datos del proyecto desde la base de datos."""
        if self.db:
            # Real database query
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM proyectos_negocio WHERE id_proyecto = %s", (self.project_id,))
            self.project = cursor.fetchone() or {}
        else:
            # Fallback: load from JSON file if exists
            project_file = self.data_path / "project.json"
            if project_file.exists():
                with open(project_file, 'r', encoding='utf-8') as f:
                    self.project = json.load(f)
            else:
                logger.warning(f"No project data found for ID {self.project_id}")
                self.project = {}
        
        return self.project
    
    def load_or_create_context(self) -> str:
        """Carga o crea el archivo Markdown de contexto del proyecto."""
        self.data_path.mkdir(parents=True, exist_ok=True)
        context_file = self.data_path / "context.md"
        
        if context_file.exists():
            with open(context_file, 'r', encoding='utf-8') as f:
                self.context_md = f.read()
        else:
            # Create initial context
            nombre = self.project.get("a1_nombre_negocio", "Sin nombre")
            self.context_md = f"""# Proyecto: {nombre}
ID: {self.project_id} | Creado: {datetime.now().strftime('%Y-%m-%d')}

## Resumen Ejecutivo
(Pendiente de análisis)

## Investigaciones Realizadas
| Fecha | Tipo | Hallazgo |
|-------|------|----------|

## Decisiones del Usuario
(Sin registros)

## Notas del Agente
(Sin notas)
"""
            self._save_context()
        
        return self.context_md
    
    def _save_context(self):
        """Guarda el contexto actualizado."""
        context_file = self.data_path / "context.md"
        with open(context_file, 'w', encoding='utf-8') as f:
            f.write(self.context_md)
    
    # --------------------------------------------------------------------------
    # Analysis
    # --------------------------------------------------------------------------
    
    def analyze_completeness(self) -> Dict[str, float]:
        """
        Analiza qué tan completo está cada módulo del proyecto.
        
        Returns:
            Dict con porcentaje de completitud por módulo
        """
        completeness = {}
        
        for module_name, module_config in MODULES.items():
            fields = module_config["fields"]
            filled = 0
            total = len(fields)
            
            for field in fields:
                value = self.project.get(field)
                if value and str(value).strip() and value not in ["null", "None", "[]", "{}"]:
                    # Check if JSON field is not empty
                    if field.endswith("_json"):
                        try:
                            parsed = json.loads(value) if isinstance(value, str) else value
                            if parsed and (isinstance(parsed, list) and len(parsed) > 0 or 
                                          isinstance(parsed, dict) and len(parsed) > 0):
                                filled += 1
                        except:
                            pass
                    else:
                        filled += 1
            
            completeness[module_name] = round((filled / total) * 100, 1) if total > 0 else 0
        
        self.completeness = completeness
        logger.info(f"📊 Completeness: {completeness}")
        return completeness
    
    def determine_complexity(self) -> str:
        """
        Determina la complejidad del proyecto basado en sus características.
        
        Returns:
            'micro', 'startup', o 'enterprise'
        """
        score = 0
        
        # Check investment level
        inversion = float(self.project.get("g8_inversion_inicial", 0) or 0)
        if inversion > 1_000_000:
            score += 3
        elif inversion > 200_000:
            score += 2
        elif inversion > 50_000:
            score += 1
        
        # Check employee count
        try:
            org = json.loads(self.project.get("c4_organigrama_json", "[]"))
            total_employees = sum(role.get("count", 1) for role in org) if org else 0
            if total_employees > 20:
                score += 3
            elif total_employees > 5:
                score += 2
            elif total_employees > 0:
                score += 1
        except:
            pass
        
        # Check business type
        descripcion = str(self.project.get("a3_descripcion_negocio", "")).lower()
        tipo = str(self.project.get("a2_tipo_empresa", "")).lower()
        
        complex_keywords = ["saas", "b2b", "manufactura", "exportación", "franquicia", "plataforma", "marketplace"]
        if any(kw in descripcion or kw in tipo for kw in complex_keywords):
            score += 2
        
        # Determine level
        if score >= 5:
            self.complexity = COMPLEXITY_ENTERPRISE
        elif score >= 2:
            self.complexity = COMPLEXITY_STARTUP
        else:
            self.complexity = COMPLEXITY_MICRO
        
        logger.info(f"🎯 Complexity: {self.complexity} (score: {score})")
        return self.complexity
    
    def determine_industry(self) -> str:
        """
        Determina la industria del proyecto para cargar prompts específicos.
        
        Returns:
            Nombre de la industria detectada
        """
        descripcion = str(self.project.get("a3_descripcion_negocio", "")).lower()
        nombre = str(self.project.get("a1_nombre_negocio", "")).lower()
        text = f"{nombre} {descripcion}"
        
        for industry, keywords in INDUSTRY_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                self.industry = industry
                break
        else:
            self.industry = "general"
        
        logger.info(f"🏭 Industry: {self.industry}")
        return self.industry
    
    # --------------------------------------------------------------------------
    # RAG Integration
    # --------------------------------------------------------------------------
    
    def query_rag(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Búsqueda semántica usando RAG Engine (ChromaDB).
        """
        try:
            results = self.rag.query(query, n_results=top_k)
            return results
        except Exception as e:
            logger.error(f"RAG Error: {e}")
            return []
    
    def get_methodology_context(self) -> str:
        """
        Obtiene contexto de metodologías relevantes para el proyecto.
        
        Returns:
            Texto con contexto de Lean Startup, Delta Model, etc.
        """
        context_parts = []
        
        # Always include Lean Startup basics
        lean_file = self.docs_path / "lean_startup.md"
        if lean_file.exists():
            with open(lean_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract key sections
                context_parts.append("## Lean Startup\n" + content[:2000])
        
        # Include Delta Model
        delta_file = self.docs_path / "delta_model.md"
        if delta_file.exists():
            with open(delta_file, 'r', encoding='utf-8') as f:
                content = f.read()
                context_parts.append("## Modelo Delta\n" + content[:1500])
        
        # Include industry-specific guide if available
        industry_file = self.docs_path / "industrias" / f"{self.industry}.md"
        if industry_file.exists():
            with open(industry_file, 'r', encoding='utf-8') as f:
                content = f.read()
                context_parts.append(f"## Guía de Industria: {self.industry.title()}\n" + content[:2000])
        
        return "\n\n".join(context_parts)
    
    # --------------------------------------------------------------------------
    # Module Completion
    # --------------------------------------------------------------------------
    
    def complete_module(self, module_name: str, use_web: bool = True, 
                       use_llm: bool = True) -> Dict[str, Any]:
        """
        Completa un módulo específico usando RAG, web research, y LLM.
        
        Args:
            module_name: Nombre del módulo (identidad, mercado, productos, etc.)
            use_web: Si debe investigar en internet
            use_llm: Si debe usar LLM para generar contenido
            
        Returns:
            Dict con campos sugeridos para el módulo
        """
        if module_name not in MODULES:
            raise ValueError(f"Módulo desconocido: {module_name}")
        
        module_config = MODULES[module_name]
        suggestions = {}
        
        logger.info(f"🔄 Completing module: {module_name}")
        
        # Get methodology context
        methodology_context = self.get_methodology_context()
        
        # Get industry-specific data if available
        industry_context = self._get_industry_data(module_name)
        
        # For each empty field, generate suggestion
        for field in module_config["fields"]:
            current_value = self.project.get(field)
            if not current_value or str(current_value).strip() in ["", "null", "None", "[]", "{}"]:
                suggestion = self._suggest_field_value(
                    field, 
                    methodology_context, 
                    industry_context,
                    use_web=use_web,
                    use_llm=use_llm,
                    module_name=module_name  # Pass module name for live research
                )
                if suggestion:
                    suggestions[field] = suggestion
                    logger.info(f"  ✅ Suggested: {field}")
                    
        self.audit.log_action("BobAgent", "complete_module", f"module:{module_name}", 
                             {"project_id": self.project_id, "suggestions_count": len(suggestions)},
                             project_id=str(self.project_id))
        
        return suggestions
    
    def _get_industry_data(self, module_name: str) -> Dict[str, Any]:
        """Obtiene datos de referencia de la industria para un módulo."""
        data = {}
        
        industry_file = self.docs_path / "industrias" / f"{self.industry}.md"
        if not industry_file.exists():
            return data
        
        with open(industry_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract relevant section based on module
        sections = {
            "finanzas": ["Costos de Referencia", "Inversión Inicial", "Punto de Equilibrio", "Margen"],
            "organizacion": ["Salarios", "Personal", "Estructura"],
            "productos": ["Producción", "Capacidad", "Precios"],
            "mercado": ["Competencia", "Normativas", "Licencias"]
        }
        
        if module_name in sections:
            for keyword in sections[module_name]:
                if keyword.lower() in content.lower():
                    data[f"industria_{keyword.lower()}"] = True
        
        data["raw_content"] = content
        return data

    def process_uploaded_document(self, file_path: str, doc_type: str = "general") -> Dict[str, Any]:
        """
        Procesa un documento subido (PDF/Img) -> OCR -> Mapeo -> Contexto.
        """
        import requests
        
        ocr_url = "http://localhost:5001/api/ocr/scan"
        # Check if running in Docker (use service name)
        if os.getenv("OCR_SERVICE_URL"): ocr_url = os.getenv("OCR_SERVICE_URL") + "/api/ocr/scan"
            
        try:
            # 1. Send to OCR Service
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(ocr_url, files=files, timeout=60)
                
            if response.status_code == 200:
                result = response.json()
                raw_text = result.get("extracted_text", "")
                
                # 2. Map Text
                mapped_data = self.ocr_mapper.map_text_to_project(raw_text, doc_type)
                
                # 3. Add findings to context
                finding_msg = f"Documento '{os.path.basename(file_path)}' procesado.\nDatos extraídos: {json.dumps(mapped_data, indent=2, ensure_ascii=False)}"
                self.add_research_finding("Document Analysis", finding_msg)
                
                return mapped_data
            else:
                logger.error(f"OCR Service failed: {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return {}

    def _perform_live_research(self, module_name: str) -> Dict[str, Any]:
        """Realiza investigación en vivo si el servicio está disponible."""
        research_data = {}
        
        # Check health once
        if not self.web_service_available:
            self.web_service_available = self.research_client.check_health()
        
        if not self.web_service_available:
            return {}
            
        try:
            location = self.project.get("d1_ubicacion", "Mexico") or "Mexico"
            
            if module_name == "mercado":
                # Competitor search
                # International support check
                query_location = location
                
                if self.complexity == COMPLEXITY_ENTERPRISE and self.industry in ["tecnologia", "saas", "manufactura"]:
                    # Translate query for better results
                    logger.info("🌍 Enterprise project detected: Enabling global search")
                    query_location = self.translator.translate_query_for_research(location, 'en')
                
                competitors = self.research_client.search_competitors(self.industry, query_location)
                if competitors:
                    research_data["competitors_live"] = competitors
                    self.add_research_finding("Competencia", f"Encontrados {len(competitors)} competidores en {location}")
                    
            elif module_name == "finanzas":
                # Indicators
                indicators = self.research_client.get_economic_indicators()
                if indicators.get("success"):
                    research_data["indicators"] = indicators.get("indicators", {})
                    
            elif module_name == "productos":
                # Price search generic (example product based on industry)
                product_map = {
                    "panaderia": "Harina de trigo",
                    "restaurante": "Aceite vegetal",
                    "construccion": "Cemento gris",
                    "tecnologia": "MacBook Pro"
                }
                product = product_map.get(self.industry)
                if product:
                    prices = self.research_client.search_prices(product)
                    if prices.get("success"):
                        research_data["prices_live"] = prices.get("data", {})
                        
        except Exception as e:
            logger.error(f"Error in live research: {e}")
            
        return research_data
    
    def _suggest_field_value(self, field: str, methodology_context: str,
                            industry_context: Dict, use_web: bool = True,
                            use_llm: bool = True, module_name: str = "") -> Optional[str]:
        """
        Genera una sugerencia para un campo específico.
        
        Args:
            field: Nombre del campo de la BD
            methodology_context: Contexto de metodologías
            industry_context: Datos de la industria
            use_web: Si usar investigación web
            use_llm: Si usar LLM
            
        Returns:
            Valor sugerido para el campo
        """
        # Build prompt based on field type
        field_prompts = self._get_field_prompt(field)
        
        if use_llm and self.llm.check_health():
            # Generate using LLM
            logger.info(f"Generating content for {field} using LLM...")
            
            # Combine all context
            live_data_str = json.dumps(live_data, indent=2, ensure_ascii=False) if live_data else "No live data"
            
            full_prompt = f"""
            Contexto del Negocio:
            - Nombre: {self.project.get("a1_nombre_negocio")}
            - Descripción: {self.project.get("a3_descripcion_negocio")}
            - Industria: {self.industry}
            - Complejidad: {self.complexity}
            
            Contexto de Metodología:
            {methodology_context[:1000]}
            
            Datos de Industria:
            {json.dumps(industry_context, ensure_ascii=False)[:1000]}
            
            Investigación en Vivo:
            {live_data_str[:1000]}
            
            TAREA:
            {field_prompts}
            
            Responde de manera concisa y profesional en Español.
            """
            
            generated = self.llm.generate(full_prompt, temperature=0.7)
            if generated:
                return generated

        # Fallback to rules if LLM fails or is disabled
        return self._rule_based_suggestion(field, industry_context, live_data)
    
    def _get_field_prompt(self, field: str) -> str:
        """Obtiene el prompt específico para un campo."""
        prompts = {
            "b3_propuesta_valor": """
                Crea una propuesta de valor única para {nombre_negocio}.
                Considera:
                - Qué problema resuelve
                - Para quién lo resuelve
                - Por qué es mejor que alternativas
                Formato: Una oración clara y memorable.
            """,
            "g8_inversion_inicial": """
                Calcula la inversión inicial necesaria para {nombre_negocio}.
                Basado en:
                - Tipo de negocio: {tipo_negocio}
                - Ubicación: {ubicacion}
                - Datos de industria: {industria_referencia}
                Incluye: local, equipo, inventario, capital de trabajo, licencias.
            """,
            # Add more field-specific prompts...
        }
        
        return prompts.get(field, f"Genera contenido apropiado para el campo {field}")
    
    def _rule_based_suggestion(self, field: str, industry_context: Dict, live_data: Dict = {}) -> Optional[str]:
        """Genera sugerencias basadas en reglas simples (fallback sin LLM)."""
        
        # Investment suggestion based on industry
        if field == "g8_inversion_inicial":
            if self.industry == "panaderia":
                return "250000"  # Promedio de inversión panadería
            elif self.industry == "restaurante":
                return "500000"
            elif self.industry == "tecnologia":
                return "150000"
            else:
                return "200000"
            
        # Competitors JSON from Live Data
        if field == "d3_competidores_json" and "competitors_live" in live_data:
            comps = live_data["competitors_live"]
            # Format as simple list of names for JSON
            return json.dumps([c.get("name") for c in comps[:5]])
            
        # Inflation/Economic data from Live Data
        if field == "d6_analisis_mercado_json" and "indicators" in live_data:
            inds = live_data["indicators"]
            try:
                # Extract USD rate and Inflation
                usd = inds.get("banxico", {}).get("value", "N/A")
                infl = inds.get("inegi", {}).get("value", "N/A")
                return json.dumps({
                    "tipo_cambio": usd,
                    "inflacion": infl,
                    "nota": "Datos obtenidos en tiempo real de Banxico/INEGI"
                })
            except:
                pass
        
        # Monthly costs
        if field == "g5_costos_fijos_mensuales":
            inversion = float(self.project.get("g8_inversion_inicial", 200000) or 200000)
            return str(int(inversion * 0.15))  # ~15% of investment as monthly costs
        
        # ROI
        if field == "g7_roi_esperado":
            return "24"  # 24 months to recover investment (industry average)
        
        return None
    
    # --------------------------------------------------------------------------
    # Full Project Completion
    # --------------------------------------------------------------------------
    
    def complete_all(self, confirm_each: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Completa todos los módulos vacíos del proyecto.
        
        Args:
            confirm_each: Si pedir confirmación antes de cada campo
            
        Returns:
            Dict con todas las sugerencias por módulo
        """
        logger.info(f"🚀 Starting full project completion for ID {self.project_id}")
        
        # Load and analyze
        self.load_project()
        self.load_or_create_context()
        self.analyze_completeness()
        self.determine_complexity()
        self.determine_industry()
        
        all_suggestions = {}
        
        # Complete each module in order of priority
        module_order = ["identidad", "mercado", "productos", "organizacion", "finanzas", "marketing"]
        
        for module_name in module_order:
            if self.completeness.get(module_name, 0) < 100:
                suggestions = self.complete_module(module_name)
                if suggestions:
                    all_suggestions[module_name] = suggestions
        
        # Update context
        self._update_context_with_suggestions(all_suggestions)
        
        return all_suggestions
    
    def _update_context_with_suggestions(self, suggestions: Dict):
        """Actualiza el markdown de contexto con las sugerencias generadas."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        new_entry = f"\n\n## Sesión de Agente: {timestamp}\n\n"
        new_entry += "### Sugerencias Generadas\n\n"
        
        for module, fields in suggestions.items():
            new_entry += f"**{module.title()}:**\n"
            for field, value in fields.items():
                new_entry += f"- `{field}`: {str(value)[:100]}...\n" if len(str(value)) > 100 else f"- `{field}`: {value}\n"
        
        self.context_md += new_entry
        self._save_context()
    
    # --------------------------------------------------------------------------
    # Public API
    # --------------------------------------------------------------------------
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual del proyecto y el agente."""
        return {
            "project_id": self.project_id,
            "complexity": self.complexity,
            "industry": self.industry,
            "completeness": self.completeness,
            "total_completion": sum(self.completeness.values()) / len(self.completeness) if self.completeness else 0,
            "context_path": str(self.data_path / "context.md")
        }
    
    def add_user_decision(self, decision: str):
        """Registra una decisión del usuario en el contexto."""
        timestamp = datetime.now().strftime('%Y-%m-%d')
        
        new_entry = f"\n- [{timestamp}] {decision}"
        
        # Insert in "Decisiones del Usuario" section
        if "## Decisiones del Usuario" in self.context_md:
            self.context_md = self.context_md.replace(
                "## Decisiones del Usuario\n",
                f"## Decisiones del Usuario\n{new_entry}"
            )
        else:
            self.context_md += f"\n\n## Decisiones del Usuario{new_entry}"
        
        self._save_context()
        self.audit.log_action("User", "add_decision", "context.md", {"decision": decision}, str(self.project_id))
    
    def add_research_finding(self, finding_type: str, finding: str):
        """Registra un hallazgo de investigación."""
        timestamp = datetime.now().strftime('%Y-%m-%d')
        
        new_row = f"\n| {timestamp} | {finding_type} | {finding} |"
        
        if "## Investigaciones Realizadas" in self.context_md:
            # Find the table and add row
            lines = self.context_md.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('| Fecha |'):
                    # Find end of table header
                    insert_idx = i + 2  # After header and separator
                    while insert_idx < len(lines) and lines[insert_idx].startswith('|'):
                        insert_idx += 1
                    lines.insert(insert_idx, new_row)
                    break
            self.context_md = '\n'.join(lines)
        
        self._save_context()


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def run_bob_for_project(project_id: int, db_connection=None) -> Dict[str, Any]:
    """
    Función helper para ejecutar Bob en un proyecto.
    
    Args:
        project_id: ID del proyecto
        db_connection: Conexión a BD (opcional)
        
    Returns:
        Dict con resultados de la ejecución
    """
    bob = BobAgent(project_id, db_connection)
    
    # Load and analyze
    bob.load_project()
    bob.load_or_create_context()
    
    # Get current status
    bob.analyze_completeness()
    bob.determine_complexity()
    bob.determine_industry()
    
    # Generate suggestions for incomplete modules
    suggestions = bob.complete_all()
    
    return {
        "status": bob.get_status(),
        "suggestions": suggestions
    }


# ==============================================================================
# MAIN (for testing)
# ==============================================================================

if __name__ == "__main__":
    # Test with a sample project
    print("🤖 Bob Agent - Test Mode")
    print("=" * 50)
    
    # Create a test instance
    bob = BobAgent(project_id=1)
    
    # Simulate project data
    bob.project = {
        "id_proyecto": 1,
        "a1_nombre_negocio": "Panadería La Rosa",
        "a3_descripcion_negocio": "Panadería artesanal con productos tradicionales mexicanos",
        "a2_tipo_empresa": "PYME",
        "g8_inversion_inicial": None,
        "g5_costos_fijos_mensuales": None,
        "c4_organigrama_json": "[]"
    }
    
    # Run analysis
    bob.load_or_create_context()
    completeness = bob.analyze_completeness()
    complexity = bob.determine_complexity()
    industry = bob.determine_industry()
    
    print(f"\nCompleteness: {completeness}")
    print(f"Complexity: {complexity}")
    print(f"Industry: {industry}")
    
    # Generate suggestions
    suggestions = bob.complete_all()
    print(f"\nSuggestions: {json.dumps(suggestions, indent=2, ensure_ascii=False)}")
    
    # Print status
    print(f"\nFinal Status: {bob.get_status()}")
