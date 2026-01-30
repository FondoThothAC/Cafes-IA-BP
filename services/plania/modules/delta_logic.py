# =================================================================================
# PROYECTO: PlanIA (Delta Logic Engine)
# ARCHIVO: modules/delta_logic.py
# COPYRIGHT: © 2026 Fondo Thoth AC.
# LICENCIA: MIT
# DESCRIPCIÓN: Motor de lógica determinista para el modelo Delta.
#              Analiza datos del proyecto para recomendar posición estratégica.
# =================================================================================

import json
from typing import Dict, Any, List, Tuple

class DeltaLogicEngine:
    """
    Analyzes project data to determine the optimal Delta Model position.
    """

    def __init__(self, project_data: Dict[str, Any]):
        self.project_id = project_data.get("id_proyecto") or project_data.get("id")
        self.project = project_data
        
        # Parse JSON fields safely
        self.revenue_data = self._parse_json(project_data.get("g12_proyeccion_ingresos_json"))
        self.competitors = self._parse_json(project_data.get("d3_competidores_json"))
        self.segments = self._parse_json(project_data.get("d2_segmento_json")) or []

    def _parse_json(self, json_str: Any) -> Any:
        if not json_str:
            return []
        if isinstance(json_str, (dict, list)):
            return json_str
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return []

    def analyze_position(self) -> Dict[str, Any]:
        """
        Determines the recommended strategic position based on business rules.
        
        Returns:
            Dict containing:
            - position: str (Best Product, Total Customer Solution, System Lock-In)
            - sub_position: str (Low Cost, Differentiation, Horizontal Breadth, etc.)
            - confidence: int (0-100)
            - reasoning: List[str] (Analysis steps)
            - metrics: Dict (Calculated metrics)
        """
        logs = []
        scores = {
            "Best Product": 0,
            "Total Customer Solution": 0,
            "System Lock-In": 0
        }
        
        # ---------------------------------------------------------
        # 1. Product Portfolio Analysis (Revenue Distribution)
        # ---------------------------------------------------------
        # User Rule: "If >3 products with similar revenue (20-30%) -> Broad Scope (TCS)"
        products = self.revenue_data
        total_revenue = 0
        product_shares = []

        if products:
            for p in products:
                try:
                    price = float(p.get("precio", 0) or 0)
                    qty = float(p.get("cantidad_mensual", 0) or 0)
                    rev = price * qty
                    total_revenue += rev
                    if rev > 0:
                        product_shares.append({"name": p.get("nombre_producto"), "revenue": rev})
                except (ValueError, TypeError):
                    continue

        if total_revenue > 0:
            # Calculate percentages
            for p in product_shares:
                p["share"] = (p["revenue"] / total_revenue) * 100
            
            # Sort by share descending
            product_shares.sort(key=lambda x: x["share"], reverse=True)
            
            logs.append(f"Análisis de Ingresos: {len(product_shares)} productos activos.")
            
            # CHECK RULE: Balanced Portfolio (>3 items in 20-30% range)
            balanced_items = [p for p in product_shares if 15 <= p["share"] <= 35]
            
            if len(balanced_items) >= 3:
                scores["Total Customer Solution"] += 50
                logs.append(f"DETECTADO: Portafolio balanceado ({len(balanced_items)} productos entre 15-35%). Sugiere 'Horizontal Breadth'.")
            elif product_shares[0]["share"] > 70:
                scores["Best Product"] += 40
                logs.append(f"DETECTADO: Mono-producto dominante ({product_shares[0]['name']} = {product_shares[0]['share']:.1f}%). Sugiere 'Best Product'.")
            else:
                scores["Total Customer Solution"] += 10
                scores["Best Product"] += 10
                logs.append("Distribución de ingresos mixta.")

        else:
            logs.append("Sin datos de ingresos proyectados. Asumiendo etapa inicial.")
            scores["Best Product"] += 20 # Default startup mode

        # ---------------------------------------------------------
        # 2. Competitor Analysis
        # ---------------------------------------------------------
        comp_count = len(self.competitors) if self.competitors else 0
        logs.append(f"Análisis de Competencia: {comp_count} competidores detectados.")
        
        if comp_count > 10:
            scores["Best Product"] += 30
            logs.append("Alta competencia (Océano Rojo). Se requiere eficiencia (Low Cost) o Diferenciación agresiva.")
        elif comp_count == 0:
            scores["System Lock-In"] += 20
            logs.append("Sin competencia directa detectada. Posible oportunidad de 'System Lock-In' o Monopolio temporal.")
        else:
            scores["Total Customer Solution"] += 20
            logs.append("Competencia moderada. Oportunidad para fidelizar clientes (Customer Integration).")

        # ---------------------------------------------------------
        # 3. Determine Winner
        # ---------------------------------------------------------
        winner = max(scores, key=scores.get)
        
        # Determine Sub-Position
        sub_position = self._determine_sub_position(winner, scores, product_shares)

        return {
            "recommended_position": winner,
            "sub_position": sub_position,
            "scores": scores,
            "reasoning": logs,
            "metrics": {
                "product_count": len(product_shares),
                "revenue_concentration": product_shares[0]["share"] if product_shares else 0,
                "competitor_count": comp_count
            }
        }

    def _determine_sub_position(self, winner: str, scores: Dict, products: List) -> str:
        """Refines the main category into a specific Delta axiom."""
        if winner == "Best Product":
            # If we have many competitors, maybe 'Low Cost'. If explicitly marked as 'Unique', 'Differentiation'.
            # Heuristic: If margins are tight (costs high), Low Cost. (We assume margins for now)
            return "Differentiation" # Default for startups
            
        elif winner == "Total Customer Solution":
            # If we hit the "Balanced Portfolio" rule
            balanced_items = [p for p in products if 15 <= p["share"] <= 35]
            if len(balanced_items) >= 3:
                return "Horizontal Breadth"
            else:
                return "Customer Integration"
                
        elif winner == "System Lock-In":
            return "Dominant Exchange" # Default aspiration
            
        return winner
