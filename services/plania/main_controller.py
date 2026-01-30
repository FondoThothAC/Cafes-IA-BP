# =================================================================================
# PROYECTO: PlanIA (Local Orchestrator)
# ARCHIVO: main_controller.py
# COPYRIGHT: © 2026 Fondo Thoth AC.
# LICENCIA: GPLv2 (Open Source para análisis de datos públicos).
# DESCRIPCIÓN: Script principal que orquesta el flujo de datos y cálculos.
# =================================================================================

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import local modules (ensure PYTHONPATH includes this directory)
from modules.data_harvester import DataHarvester
from modules.price_scraper import PriceScraper
from modules.finance_calc import FinancialBrain
from modules.ai_client import AIClient
from modules.delta_logic import DeltaLogicEngine

# Database connector placeholder
# In production, use mysql-connector-python or pymysql
try:
    import mysql.connector
    HAS_MYSQL = True
except ImportError:
    HAS_MYSQL = False
    print("[!] mysql-connector-python not installed. Running in dry-run mode.")


class MainController:
    """
    Orchestrates the data harvesting, price scraping, and financial calculations
    for each project row flagged for processing.
    """

    def __init__(self):
        self.harvester = DataHarvester()
        self.ai = AIClient()
        self.db_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD", ""),
            "database": os.getenv("DB_NAME", "plania"),
        }

    def get_connection(self):
        """Create and return a MySQL connection."""
        if not HAS_MYSQL:
            return None
        return mysql.connector.connect(**self.db_config)

    def fetch_pending_projects(self) -> list[dict]:
        """
        Fetch all project rows where ia_flag_procesar = TRUE.

        Returns:
            List of project dictionaries with relevant fields.
        """
        conn = self.get_connection()
        if not conn:
            print("[!] No database connection. Returning empty list.")
            return []

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                id_proyecto, uuid_usuario,
                d6_latitud, d7_longitud,
                e3_productos_bom_json, g12_proyeccion_ingresos_json,
                g5_costos_fijos_mensuales, g8_inversion_inicial
            FROM proyectos_negocio
            WHERE ia_flag_procesar = TRUE
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    def process_project(self, project: dict) -> dict:
        """
        Process a single project:
        1. Fetch macro indicators (Banxico).
        2. Fetch competitors (INEGI DENUE).
        3. Update ingredient costs (PriceScraper).
        4. Calculate financials (FinancialBrain).

        Args:
            project: Dictionary with project data from DB.

        Returns:
            Dictionary with processed results to update in DB.
        """
        project_id = project.get("id_proyecto")
        lat = float(project.get("d6_latitud") or 0)
        lon = float(project.get("d7_longitud") or 0)
        bom_raw = project.get("e3_productos_bom_json")
        fixed_costs = float(project.get("g5_costos_fijos_mensuales") or 0)
        initial_investment = float(project.get("g8_inversion_inicial") or 0)

        result = {
            "id_proyecto": project_id,
            "success": False,
            "log": "",
            "data_source": "Manual",
        }

        # 1. Get financial indicators from Banxico
        print(f"[{project_id}] Fetching Banxico indicators...")
        indicators = self.harvester.get_financial_indicators()
        if indicators:
            result["g1_tipo_cambio_usd"] = indicators["usd_mxn"]
            result["g2_tasa_interes_tiie"] = indicators["tiie_28"]
            result["g4_fecha_datos_macro"] = indicators["fecha_consulta"]
            result["data_source"] = "API"
            usd_mxn = indicators["usd_mxn"]
        else:
            result["log"] += "Banxico API failed. Using manual data.\n"
            usd_mxn = 17.0  # Fallback

        # 2. Get competitors from INEGI DENUE
        print(f"[{project_id}] Fetching DENUE competitors...")
        if lat != 0 and lon != 0:
            competitors = self.harvester.get_competitors(lat, lon, "negocio", 1000)
            if competitors:
                result["d3_competidores_json"] = json.dumps(competitors["processed"], ensure_ascii=False)
                result["d4_api_inegi_raw"] = json.dumps(competitors["raw"][:10], ensure_ascii=False)
            else:
                result["log"] += "INEGI DENUE API failed. Competitors not updated.\n"
        else:
            result["log"] += "No coordinates provided. Skipping DENUE lookup.\n"

        # 3. Update ingredient costs
        print(f"[{project_id}] Updating BOM costs...")
        if bom_raw:
            try:
                bom = json.loads(bom_raw) if isinstance(bom_raw, str) else bom_raw
                scraper = PriceScraper(lat=lat, lon=lon)
                updated_bom = scraper.update_costs(bom)
                result["e3_productos_bom_json"] = json.dumps(updated_bom, ensure_ascii=False)
            except Exception as e:
                result["log"] += f"BOM update error: {e}\n"
                updated_bom = []
        else:
            updated_bom = []
            result["log"] += "No BOM data to process.\n"

        # 4. Calculate financials
        print(f"[{project_id}] Calculating financials...")
        if updated_bom and fixed_costs > 0 and initial_investment > 0:
            brain = FinancialBrain(
                fixed_costs_monthly=fixed_costs,
                initial_investment=initial_investment,
                bom_json=updated_bom,
                usd_mxn=usd_mxn,
            )

            # Break-even
            be = brain.calculate_break_even()
            result["g7_punto_equilibrio"] = json.dumps(be, ensure_ascii=False)

            # Cash flow (assume linear growth for demo)
            monthly_sales = [int(30 + i * 5) for i in range(12)]
            cf = brain.project_cash_flow(monthly_sales)
            result["g9_flujo_efectivo_anual_json"] = json.dumps(cf, ensure_ascii=False)

            # ROI
            annual_profit = cf.get("resumen_anual", {}).get("utilidad_neta_total", 0)
            roi = brain.calculate_roi(annual_profit)
            result["g10_rentabilidad_roi"] = f"ROI: {roi.get('roi_pct', 0)}%"



            # 5. AI Strategic Analysis
            print(f"[{project_id}] Running Local AI Analysis (Llama3)...")
            project_summary = {
                "roi": roi, 
                "break_even": be, 
                "investment": initial_investment
            }
            ai_analysis = self.ai.analyze_project(project_summary)
            if ai_analysis:
                # Appending to log for now as a demo field
                result["log"] += f"\n[AI ANALYSIS]:\n{ai_analysis}\n"

            result["success"] = True
        else:
            result["log"] += "Insufficient data for financial calculations.\n"

        # 5. Delta Logic Analysis (Deterministic)
        print(f"[{project_id}] Running Delta Logic Engine...")
        
        delta_data_context = project.copy()
        delta_data_context["d3_competidores_json"] = result.get("d3_competidores_json", "[]") 
        # Use real revenue data fetched from DB
        delta_data_context["g12_proyeccion_ingresos_json"] = project.get("g12_proyeccion_ingresos_json") 
        
        delta_engine = DeltaLogicEngine(delta_data_context)
        delta_analysis = delta_engine.analyze_position()
        
        result["log"] += f"\n[DELTA LOGIC]:\nPosición Recomendada: {delta_analysis['recommended_position']} ({delta_analysis['sub_position']})\nReasoning: {'; '.join(delta_analysis['reasoning'])}\n"
        
        result["d5_ventaja_competitiva"] = f"{delta_analysis['recommended_position']} - {delta_analysis['sub_position']}"

        return result

    def update_project(self, result: dict):
        """
        Update the project row in the database with processed results.

        Args:
            result: Dictionary with fields to update.
        """
        conn = self.get_connection()
        if not conn:
            print("[!] No database connection. Cannot update project.")
            return

        project_id = result["id_proyecto"]
        fields = []
        values = []

        for key in [
            "g1_tipo_cambio_usd", "g2_tasa_interes_tiie", "g4_fecha_datos_macro",
            "d3_competidores_json", "d4_api_inegi_raw",
            "e3_productos_bom_json",
            "g7_punto_equilibrio", "g9_flujo_efectivo_anual_json", "g10_rentabilidad_roi",
            "d5_ventaja_competitiva"
        ]:
            if key in result:
                fields.append(f"{key} = %s")
                values.append(result[key])

        # Always update flags
        fields.append("ia_flag_procesar = FALSE")
        fields.append("ia_ultimo_log = %s")
        fields.append("ia_fecha_procesamiento = %s")
        fields.append("data_source = %s")

        values.append(result.get("log", ""))
        values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        values.append(result.get("data_source", "Manual"))
        values.append(project_id)

        sql = f"UPDATE proyectos_negocio SET {', '.join(fields)} WHERE id_proyecto = %s"

        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[{project_id}] Updated successfully.")

    def run_once(self):
        """Process all pending projects once."""
        projects = self.fetch_pending_projects()
        print(f"[*] Found {len(projects)} projects to process.")

        for project in projects:
            result = self.process_project(project)
            self.update_project(result)

    def run_loop(self, interval_seconds: int = 60):
        """Continuously process pending projects at specified interval."""
        print(f"[*] Starting processing loop (every {interval_seconds}s)...")
        while True:
            self.run_once()
            time.sleep(interval_seconds)


# ==================================================
# ENTRY POINT
# ==================================================
if __name__ == "__main__":
    controller = MainController()
    # Run once for testing; use run_loop() for production
    controller = MainController()
    
    if os.getenv("LOOP_MODE", "false").lower() == "true":
        controller.run_loop(interval_seconds=60)
    else:
        # Run once for testing or manual trigger
        controller.run_once()
