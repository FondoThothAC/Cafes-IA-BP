# =================================================================================
# PROYECTO: PlanIA (Local Module)
# ARCHIVO: modules/data_harvester.py
# COPYRIGHT: © 2026 Fondo Thoth AC.
# LICENCIA: GPLv2 (Open Source para análisis de datos públicos).
# DESCRIPCIÓN: Orquestador que usa BanxicoService e InegiService existentes.
# =================================================================================

import json
from typing import Optional
from datetime import datetime

# Import existing services from CAFES
from .banxico import BanxicoService, BANXICO_SERIES
from .inegi import InegiService, ACTIVITY_SECTORS, GEO_CODES


class DataHarvester:
    """
    Orchestrates data harvesting from INEGI DENUE and Banxico APIs.
    Uses the existing BanxicoService and InegiService implementations.
    """

    def __init__(self):
        self.banxico = BanxicoService()
        self.inegi = InegiService()

    def get_competitors(self, lat: float, lon: float, keyword: str, radius_meters: int = 2000) -> Optional[dict]:
        """
        Query DENUE API to find local competitors.

        Args:
            lat: Latitude of the business location.
            lon: Longitude of the business location.
            keyword: Business type keyword (e.g., 'panaderia').
            radius_meters: Search radius in meters.

        Returns:
            Dictionary with 'raw', 'processed', and 'count' keys, or None on error.
        """
        print(f"[*] Buscando '{keyword}' a {radius_meters}m de ({lat}, {lon})...")
        
        try:
            results = self.inegi.get_competitors(keyword, lat, lon, radius_meters)
            
            if results:
                # Format for database storage
                processed = []
                for business in results[:10]:  # Top 10 competitors
                    processed.append({
                        "nombre": business.get("nombre", ""),
                        "actividad": business.get("actividad", ""),
                        "calle": business.get("calle", ""),
                        "colonia": business.get("colonia", ""),
                        "telefono": business.get("telefono", ""),
                        "latitud": business.get("latitud", ""),
                        "longitud": business.get("longitud", ""),
                    })
                
                return {
                    "raw": results,
                    "processed": processed,
                    "count": len(results),
                    "source": "API",
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                print("[!] No competitors found or API error.")
                return None
                
        except Exception as e:
            print(f"[!] Exception in get_competitors: {e}")
            return None

    def get_financial_indicators(self) -> Optional[dict]:
        """
        Query Banxico API for USD exchange rate, TIIE interest rate, and more.

        Returns:
            Dictionary with financial indicators, or None on error.
        """
        print("[*] Obteniendo indicadores financieros de Banxico...")
        
        try:
            panel = self.banxico.get_panel_economico()
            
            if panel:
                indicators = {
                    "fecha_consulta": datetime.now().strftime("%Y-%m-%d"),
                    "usd_mxn": panel.get("tipo_cambio", {}).get("valor", 0.0),
                    "usd_fecha": panel.get("tipo_cambio", {}).get("fecha", ""),
                    "tiie_28": panel.get("tasa_interes", {}).get("valor", 0.0),
                    "tiie_fecha": panel.get("tasa_interes", {}).get("fecha", ""),
                    "inflacion": panel.get("inflacion", {}).get("valor", 0.0),
                    "inflacion_fecha": panel.get("inflacion", {}).get("fecha", ""),
                    "salario_minimo": panel.get("salario_minimo", {}).get("valor", 0.0),
                    "salario_minimo_fecha": panel.get("salario_minimo", {}).get("fecha", ""),
                    "source": "API",
                }
                return indicators
            else:
                print("[!] Could not retrieve financial panel.")
                return None
                
        except Exception as e:
            print(f"[!] Exception in get_financial_indicators: {e}")
            return None

    def get_demographics(self, geo_code: str = "2603000") -> Optional[dict]:
        """
        Get demographic data for a geographic area from INEGI.

        Args:
            geo_code: INEGI geographic code (default: Hermosillo).

        Returns:
            Dictionary with demographic indicators.
        """
        print(f"[*] Obteniendo datos demográficos para {geo_code}...")
        
        try:
            return self.inegi.get_demographics(geo_code)
        except Exception as e:
            print(f"[!] Exception in get_demographics: {e}")
            return None

    def get_kpis(self, geo_code: str = "26030") -> Optional[dict]:
        """
        Get business KPIs (spending, income, inflation) from INEGI.

        Args:
            geo_code: INEGI geographic code.

        Returns:
            Dictionary with KPI data.
        """
        print(f"[*] Obteniendo KPIs de negocio para {geo_code}...")
        
        try:
            return self.inegi.get_kpis(geo_code)
        except Exception as e:
            print(f"[!] Exception in get_kpis: {e}")
            return None

    def count_competitors(self, area: str, activity: str = "todos") -> int:
        """
        Count businesses in an area by activity type using DENUE.

        Args:
            area: INEGI area code.
            activity: Activity sector code.

        Returns:
            Number of establishments.
        """
        return self.inegi.count_businesses(area, activity)

    def get_available_sectors(self) -> dict:
        """Return available activity sectors from INEGI SCIAN codes."""
        return ACTIVITY_SECTORS

    def get_geo_codes(self) -> dict:
        """Return available geographic codes."""
        return GEO_CODES

    def get_banxico_series(self) -> dict:
        """Return available Banxico series IDs."""
        return BANXICO_SERIES


# ==================================================
# LOCAL TEST
# ==================================================
if __name__ == "__main__":
    harvester = DataHarvester()

    # Test Banxico
    print("\n=== Banxico Financial Indicators ===")
    finanzas = harvester.get_financial_indicators()
    if finanzas:
        print(f"USD/MXN: ${finanzas['usd_mxn']}")
        print(f"TIIE 28: {finanzas['tiie_28']}%")
        print(f"Inflación: {finanzas['inflacion']}%")
        print(f"Salario Mínimo: ${finanzas['salario_minimo']}")
    else:
        print("Could not retrieve financial indicators.")

    # Test INEGI DENUE
    print("\n=== INEGI DENUE Competitors ===")
    competencia = harvester.get_competitors(29.0729, -110.9559, "panaderia", 2000)
    if competencia:
        print(f"Competidores encontrados: {competencia['count']}")
        if competencia["processed"]:
            print("Ejemplo:", json.dumps(competencia["processed"][0], indent=2, ensure_ascii=False))
    else:
        print("Could not retrieve competitors.")
