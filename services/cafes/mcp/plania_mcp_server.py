# =================================================================================
# PROYECTO: PlanIA - MCP Server for Intelligent Data Search
# ARCHIVO: mcp/plania_mcp_server.py
# COPYRIGHT: © 2026 Fondo Thoth AC.
# LICENCIA: MIT
# DESCRIPCIÓN: Servidor MCP que expone datos del proyecto a modelos de IA
# =================================================================================
"""
PlanIA MCP Server - Model Context Protocol Server

Este servidor expone herramientas y recursos para que los modelos de IA
puedan acceder a datos del proyecto de forma estructurada.

Uso:
    python -m mcp.plania_mcp_server

Requisitos:
    pip install "mcp[cli]" fastmcp
"""

import os
import sys
import json
import mysql.connector
from typing import Optional, Dict, List, Any
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: MCP library not installed. Run: pip install 'mcp[cli]' fastmcp")
    sys.exit(1)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Initialize FastMCP server
mcp = FastMCP(
    name="PlanIA Data Server",
    version="1.0.0",
    description="Servidor MCP para búsqueda inteligente de datos de proyectos de negocio"
)

# =============================================================================
# DATABASE CONNECTION
# =============================================================================

def get_db_connection():
    """Create a database connection using environment variables."""
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "plania_user"),
            password=os.getenv("DB_PASSWORD", "plania_pass_2026"),
            database=os.getenv("DB_NAME", "plania"),
            charset='utf8mb4'
        )
    except mysql.connector.Error as e:
        print(f"[MCP Error] Database connection failed: {e}")
        return None


def fetch_project(project_id: int) -> Optional[Dict]:
    """Fetch a project from the database by ID."""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM proyectos_negocio WHERE id = %s", 
            (project_id,)
        )
        project = cursor.fetchone()
        cursor.close()
        conn.close()
        return project
    except Exception as e:
        print(f"[MCP Error] Could not fetch project: {e}")
        return None


# =============================================================================
# MCP TOOLS - Actions that the AI can perform
# =============================================================================

@mcp.tool()
def search_project_data(project_id: int, query: str) -> Dict[str, Any]:
    """
    Busca información relevante en los datos del proyecto.
    
    Args:
        project_id: ID del proyecto a buscar
        query: Término de búsqueda (ej: "cliente", "costos", "productos")
        
    Returns:
        Diccionario con campos que coinciden con la búsqueda
    """
    project = fetch_project(project_id)
    if not project:
        return {"error": f"Proyecto {project_id} no encontrado"}
    
    query_lower = query.lower()
    results = {}
    
    # Search through all project fields
    for key, value in project.items():
        if value and (
            query_lower in key.lower() or 
            (isinstance(value, str) and query_lower in value.lower())
        ):
            results[key] = value
    
    return {
        "project_id": project_id,
        "project_name": project.get("a1_nombre_negocio", "Sin nombre"),
        "query": query,
        "matches": results,
        "total_matches": len(results)
    }


@mcp.tool()
def get_market_analysis(project_id: int) -> Dict[str, Any]:
    """
    Obtiene el análisis de mercado del proyecto.
    
    Incluye datos demográficos de INEGI y competidores de DENUE
    si están disponibles en el proyecto.
    
    Args:
        project_id: ID del proyecto
        
    Returns:
        Diccionario con análisis de mercado
    """
    project = fetch_project(project_id)
    if not project:
        return {"error": f"Proyecto {project_id} no encontrado"}
    
    # Parse market analysis JSON if available
    market_json = project.get("d6_analisis_mercado_json", "{}")
    try:
        market_data = json.loads(market_json) if market_json else {}
    except json.JSONDecodeError:
        market_data = {}
    
    return {
        "project_id": project_id,
        "project_name": project.get("a1_nombre_negocio"),
        "segment": project.get("d1_segmento_cliente"),
        "competitive_advantage": project.get("d5_ventaja_competitiva"),
        "need": project.get("i_necesidad"),
        "desire": project.get("i_deseo"),
        "demand": project.get("i_demanda"),
        "location": project.get("d8_direccion_formateada"),
        "demographics": market_data.get("poblacion", {}),
        "competitors": market_data.get("competidores", []),
        "map_location": market_data.get("ubicacion", {})
    }


@mcp.tool()
def get_financial_metrics(project_id: int) -> Dict[str, Any]:
    """
    Obtiene las métricas financieras del proyecto.
    
    Calcula indicadores clave como ROI potencial, punto de equilibrio
    y margen de contribución si hay datos suficientes.
    
    Args:
        project_id: ID del proyecto
        
    Returns:
        Diccionario con métricas financieras y proyecciones
    """
    project = fetch_project(project_id)
    if not project:
        return {"error": f"Proyecto {project_id} no encontrado"}
    
    # Extract financial fields
    fixed_costs = float(project.get("g5_costos_fijos_mensuales") or 0)
    initial_investment = float(project.get("g8_inversion_inicial") or 0)
    requested_amount = float(project.get("b5_monto_solicitado") or 0)
    
    # Parse revenue projection JSON
    revenue_json = project.get("g12_proyeccion_ingresos_json", "[]")
    try:
        revenue_data = json.loads(revenue_json) if revenue_json else []
    except json.JSONDecodeError:
        revenue_data = []
    
    # Calculate estimated monthly revenue
    estimated_revenue = 0
    for product in revenue_data:
        price = float(product.get("precio", 0))
        quantity = float(product.get("cantidad_mensual", 0))
        estimated_revenue += price * quantity
    
    # Calculate metrics
    metrics = {
        "project_id": project_id,
        "project_name": project.get("a1_nombre_negocio"),
        "initial_investment": initial_investment,
        "requested_amount": requested_amount,
        "monthly_fixed_costs": fixed_costs,
        "estimated_monthly_revenue": estimated_revenue,
        "products_count": len(revenue_data),
        "capital_use_plan": project.get("g9_uso_capital")
    }
    
    # Calculate derived metrics if we have enough data
    if estimated_revenue > 0 and fixed_costs > 0:
        metrics["gross_margin_pct"] = round((estimated_revenue - fixed_costs) / estimated_revenue * 100, 2)
        
    if initial_investment > 0 and estimated_revenue > 0:
        monthly_profit = estimated_revenue - fixed_costs
        if monthly_profit > 0:
            metrics["roi_months"] = round(initial_investment / monthly_profit, 1)
    
    return metrics


@mcp.tool()
def get_customer_insights(project_id: int) -> Dict[str, Any]:
    """
    Obtiene insights de clientes basados en encuestas NDD.
    
    Retorna las respuestas de encuestas de Necesidad-Deseo-Demanda
    y las tasas de conversión calculadas.
    
    Args:
        project_id: ID del proyecto
        
    Returns:
        Diccionario con insights de clientes
    """
    project = fetch_project(project_id)
    if not project:
        return {"error": f"Proyecto {project_id} no encontrado"}
    
    # Parse NDD responses
    ndd_json = project.get("i_ndd_responses_json", "[]")
    try:
        ndd_responses = json.loads(ndd_json) if ndd_json else []
    except json.JSONDecodeError:
        ndd_responses = []
    
    return {
        "project_id": project_id,
        "project_name": project.get("a1_nombre_negocio"),
        "target_customer": project.get("b4_cliente_objetivo_resumen"),
        "customer_segment": project.get("d1_segmento_cliente"),
        "need_description": project.get("i_necesidad"),
        "desire_description": project.get("i_deseo"),
        "demand_description": project.get("i_demanda"),
        "ndd_responses": ndd_responses,
        "reach_pct": project.get("i_alcance_pct"),
        "conversion_pct": project.get("i_conversion_pct"),
        "total_responses": len(ndd_responses)
    }


@mcp.tool()
def get_organization_structure(project_id: int) -> Dict[str, Any]:
    """
    Obtiene la estructura organizacional del proyecto.
    
    Incluye organigrama, roles y cálculos de nómina.
    
    Args:
        project_id: ID del proyecto
        
    Returns:
        Diccionario con estructura organizacional
    """
    project = fetch_project(project_id)
    if not project:
        return {"error": f"Proyecto {project_id} no encontrado"}
    
    # Parse organization JSON
    org_json = project.get("c4_organigrama_json", "[]")
    try:
        org_data = json.loads(org_json) if org_json else []
    except json.JSONDecodeError:
        org_data = []
    
    total_employees = 0
    total_payroll = 0
    
    for role in org_data:
        count = int(role.get("count", 1))
        salary = float(role.get("salary", 0))
        total_employees += count
        total_payroll += salary * count
        
        # Include children roles
        for child in role.get("children", []):
            child_count = int(child.get("count", 1))
            child_salary = float(child.get("salary", 0))
            total_employees += child_count
            total_payroll += child_salary * child_count
    
    return {
        "project_id": project_id,
        "project_name": project.get("a1_nombre_negocio"),
        "entrepreneur_experience": project.get("c1_experiencia_habilidades"),
        "motivation": project.get("c2_motivacion"),
        "time_commitment": project.get("c3_compromiso_tiempo"),
        "organization_chart": org_data,
        "total_employees": total_employees,
        "total_monthly_payroll": total_payroll
    }


@mcp.tool()
def list_all_projects() -> Dict[str, Any]:
    """
    Lista todos los proyectos disponibles.
    
    Returns:
        Lista de proyectos con ID, nombre y estado
    """
    conn = get_db_connection()
    if not conn:
        return {"error": "No se pudo conectar a la base de datos"}
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, a1_nombre_negocio, a2_nombre_emprendedor, 
                   estatus_proyecto, created_at
            FROM proyectos_negocio 
            ORDER BY created_at DESC 
            LIMIT 50
        """)
        projects = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "total": len(projects),
            "projects": [
                {
                    "id": p["id"],
                    "name": p["a1_nombre_negocio"],
                    "entrepreneur": p["a2_nombre_emprendedor"],
                    "status": p["estatus_proyecto"],
                    "created": str(p["created_at"]) if p["created_at"] else None
                }
                for p in projects
            ]
        }
    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# MCP RESOURCES - Read-only data access
# =============================================================================

@mcp.resource("project://{project_id}")
def get_project_resource(project_id: int) -> str:
    """
    Retorna todos los datos del proyecto como recurso.
    
    URI: project://{project_id}
    """
    project = fetch_project(project_id)
    if not project:
        return json.dumps({"error": f"Proyecto {project_id} no encontrado"})
    
    # Convert datetime objects to strings
    for key, value in project.items():
        if isinstance(value, datetime):
            project[key] = value.isoformat()
    
    return json.dumps(project, ensure_ascii=False, indent=2)


@mcp.resource("products://{project_id}")
def get_products_resource(project_id: int) -> str:
    """
    Retorna el catálogo de productos del proyecto.
    
    URI: products://{project_id}
    """
    project = fetch_project(project_id)
    if not project:
        return json.dumps({"error": f"Proyecto {project_id} no encontrado"})
    
    revenue_json = project.get("g12_proyeccion_ingresos_json", "[]")
    try:
        products = json.loads(revenue_json) if revenue_json else []
    except json.JSONDecodeError:
        products = []
    
    return json.dumps({
        "project_id": project_id,
        "project_name": project.get("a1_nombre_negocio"),
        "products": products,
        "total_products": len(products)
    }, ensure_ascii=False, indent=2)


@mcp.resource("competitors://{project_id}")
def get_competitors_resource(project_id: int) -> str:
    """
    Retorna los competidores identificados del proyecto.
    
    URI: competitors://{project_id}
    """
    project = fetch_project(project_id)
    if not project:
        return json.dumps({"error": f"Proyecto {project_id} no encontrado"})
    
    market_json = project.get("d6_analisis_mercado_json", "{}")
    try:
        market_data = json.loads(market_json) if market_json else {}
    except json.JSONDecodeError:
        market_data = {}
    
    return json.dumps({
        "project_id": project_id,
        "project_name": project.get("a1_nombre_negocio"),
        "competitive_advantage": project.get("d5_ventaja_competitiva"),
        "competitors": market_data.get("competidores", [])
    }, ensure_ascii=False, indent=2)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print("🚀 Starting PlanIA MCP Server...")
    print(f"   Database: {os.getenv('DB_NAME', 'plania')}")
    print(f"   Host: {os.getenv('DB_HOST', 'localhost')}")
    mcp.run()
