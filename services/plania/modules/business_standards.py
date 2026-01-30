# =================================================================================
# PROYECTO: PlanIA (Business Standards Module)
# ARCHIVO: modules/business_standards.py
# COPYRIGHT: © 2026 Fondo Thoth AC.
# LICENCIA: MIT
# DESCRIPCIÓN: Mapeo de datos del proyecto a estándares de negocio universales.
# =================================================================================
import json
from typing import Dict, Any, List, Optional

class BusinessStandards:
    """
    Rosetta Stone for Business Models.
    Maps internal PlanIA data structures to standard business frameworks.
    """

    def __init__(self, project_data: Dict[str, Any]):
        self.project = project_data
        self.market_data = self._parse_json(project_data.get("d6_analisis_mercado_json"))
        self.revenue_data = self._parse_json(project_data.get("g12_proyeccion_ingresos_json"))
        self.org_data = self._parse_json(project_data.get("c4_organigrama_json"))
        self.ndd_responses = self._parse_json(project_data.get("i_ndd_responses_json"))

    def _parse_json(self, json_str: Any) -> Any:
        if not json_str:
            return None
        if isinstance(json_str, (dict, list)):
            return json_str
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None

    def get_available_models(self) -> List[str]:
        return [
            "business_model_canvas",
            "lean_canvas",
            "swot_analysis",
            "pestel_analysis",
            "porters_five_forces",
            "value_proposition_canvas"
        ]

    def generate_model(self, model_type: str) -> Dict[str, Any]:
        """Generates a specific business model filled with project data."""
        method_name = f"_generate_{model_type}"
        if hasattr(self, method_name):
            return getattr(self, method_name)()
        else:
            raise ValueError(f"Model type '{model_type}' not supported.")

    # =========================================================================
    # 1. BUSINESS MODEL CANVAS (Osterwalder)
    # =========================================================================
    def _generate_business_model_canvas(self) -> Dict[str, Any]:
        return {
            "title": "Business Model Canvas",
            "sections": {
                "key_partners": self._get_key_partners(),
                "key_activities": ["Producción/Servicio", "Marketing y Ventas", "Gestión Administrativa"], # Generalizado, puede mejorarse con IA generativa
                "key_resources": self._get_key_resources(),
                "value_propositions": [self.project.get("d5_ventaja_competitiva")],
                "customer_relationships": ["Atención Personalizada", "Soporte Post-venta"], # Placeholder inteligente
                "channels": ["Directo (Presencial)", "Redes Sociales", "Referidos"], # Placeholder inteligente
                "customer_segments": [self.project.get("d1_segmento_cliente")],
                "cost_structure": self._get_cost_structure(),
                "revenue_streams": self._get_revenue_streams()
            }
        }

    # =========================================================================
    # 2. LEAN CANVAS (Ash Maurya)
    # =========================================================================
    def _generate_lean_canvas(self) -> Dict[str, Any]:
        return {
            "title": "Lean Canvas",
            "sections": {
                "problem": [self.project.get("i_necesidad")],
                "solution": [self.project.get("d5_ventaja_competitiva")], # La ventaja suele ser la solución diferencial
                "key_metrics": ["Ventas Mensuales", "Margen de Ganancia", "CAC (Costo Adquisición)"],
                "unique_value_proposition": [self.project.get("d5_ventaja_competitiva")],
                "unfair_advantage": ["Ubicación estratégica" if self.project.get("d8_direccion_formateada") else "Conocimiento del emprendedor"],
                "channels": ["Directo", "Digital"],
                "customer_segments": [self.project.get("d1_segmento_cliente"), self.project.get("b4_cliente_objetivo_resumen")],
                "cost_structure": self._get_cost_structure(),
                "revenue_streams": self._get_revenue_streams()
            }
        }

    # =========================================================================
    # 3. SWOT ANALYSIS (FODA)
    # =========================================================================
    def _generate_swot_analysis(self) -> Dict[str, Any]:
        internal_strengths = [self.project.get("c1_experiencia_habilidades"), self.project.get("c2_motivacion")]
        internal_weaknesses = ["Recursos financieros limitados (Startup)"] # Asunción segura para nuevos negocios
        
        competitors = self.market_data.get("competidores", []) if self.market_data else []
        external_threats = [f"Competencia: {c.get('nombre')}" for c in competitors[:3]] if competitors else ["Competencia local no identificada"]
        
        external_opportunities = [self.project.get("i_deseo"), self.project.get("i_demanda")]

        return {
            "title": "SWOT Analysis (FODA)",
            "sections": {
                "strengths": [s for s in internal_strengths if s],
                "weaknesses": internal_weaknesses,
                "opportunities": [o for o in external_opportunities if o],
                "threats": external_threats
            }
        }

    # =========================================================================
    # 4. PESTEL ANALYSIS (Macro-environment)
    # =========================================================================
    def _generate_pestel_analysis(self) -> Dict[str, Any]:
        # Este modelo se beneficia mucho de datos externos (INEGI/Banxico)
        # Aquí mapeamos lo que tenemos y dejamos placeholders para la IA generativa
        return {
            "title": "PESTEL Analysis",
            "sections": {
                "political": ["Regulaciones locales de comercio", "Programas de apoyo gubernamental (SE)"],
                "economic": ["Inflación general", "Tasas de interés (Banxico)", "Poder adquisitivo local (INEGI)"],
                "social": [self.project.get("d1_segmento_cliente"), "Tendencias de consumo locales"],
                "technological": ["Adopción de pagos digitales", "Marketing en redes sociales"],
                "environmental": ["Regulaciones de residuos", "Sustentabilidad del producto"],
                "legal": ["Constitución de la empresa", "Licencias de funcionamiento", "Aspectos laborales"]
            }
        }

    # =========================================================================
    # 5. PORTER'S FIVE FORCES
    # =========================================================================
    def _generate_porters_five_forces(self) -> Dict[str, Any]:
        competitors_count = len(self.market_data.get("competidores", [])) if self.market_data else 0
        comp_rivalry = "Alta" if competitors_count > 5 else "Media" if competitors_count > 0 else "Baja"

        return {
            "title": "Porter's Five Forces",
            "sections": {
                "competitive_rivalry": f"Rivalidad {comp_rivalry} ({competitors_count} competidores detectados)",
                "supplier_power": "Medio - Depende de insumos locales vs importados",
                "buyer_power": "Alto - El cliente tiene opciones",
                "threat_of_substitution": "Media - Depende de la diferenciación",
                "threat_of_new_entry": "Alta - Barreras de entrada típicas de PyMEs"
            }
        }

    # =========================================================================
    # 6. VALUE PROPOSITION CANVAS
    # =========================================================================
    def _generate_value_proposition_canvas(self) -> Dict[str, Any]:
        return {
            "title": "Value Proposition Canvas",
            "sections": {
                "customer_profile": {
                    "jobs": ["Resolver necesidad: " + str(self.project.get("i_necesidad"))],
                    "pains": ["Insatisfacción actual", "Costos elevados", "Mala atención"],
                    "gains": [self.project.get("i_deseo"), "Mejor calidad de vida"]
                },
                "value_map": {
                    "products_services": [p.get("nombre_producto") for p in (self.revenue_data or [])],
                    "pain_relievers": ["Solución eficiente", "Precios justos"],
                    "gain_creators": [self.project.get("d5_ventaja_competitiva")]
                }
            }
        }

    # =========================================================================
    # HELPERS
    # =========================================================================
    def _get_key_partners(self) -> List[str]:
        return ["Proveedores de Insumos", "Distribuidores", "Consultores"]

    def _get_key_resources(self) -> List[str]:
        resources = []
        if self.project.get("g8_inversion_inicial"):
            resources.append(f"Capital Inicial: ${self.project.get('g8_inversion_inicial')}")
        
        if self.org_data:
            roles = [r.get("role") for r in self.org_data if r.get("role")]
            resources.extend(roles)
        else:
            resources.append("Equipo Humano")
            
        return resources

    def _get_cost_structure(self) -> List[str]:
        costs = []
        if self.project.get("g5_costos_fijos_mensuales"):
            costs.append(f"Costos Fijos: ${self.project.get('g5_costos_fijos_mensuales')}/mes")
        
        # Intentar extraer costos variables promedio si existen
        if self.revenue_data:
            costs.append("Costos Variables de Producción/Venta")
            
        costs.append("Nómina y Salarios")
        costs.append("Marketing y Publicidad")
        return costs

    def _get_revenue_streams(self) -> List[str]:
        streams = []
        if self.revenue_data:
            for p in self.revenue_data:
                name = p.get("nombre_producto", "Producto")
                price = p.get("precio", 0)
                streams.append(f"Venta de {name} (${price})")
        else:
            streams.append("Venta de Productos/Servicios")
        return streams
