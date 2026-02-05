# =================================================================================
# PROYECTO: PlanIA (Bob Agent - Web Research Client)
# ARCHIVO: modules/web_research_client.py
# COPYRIGHT: © 2026 Fondo Thoth AC.
# LICENCIA: MIT
# DESCRIPCIÓN: Cliente Python para interactuar con el microservicio de scraping
#              (services/web-scraper/server.js running on port 3005).
# =================================================================================

import json
import logging
import requests
from typing import Dict, Any, List, Optional

import os

# Setup logging
logger = logging.getLogger("WebResearch")

class WebResearchClient:
    """
    Cliente para el servicio de investigación web de PlanIA.
    """
    
    def __init__(self, base_url: str = None):
        if base_url:
            self.base_url = base_url
        else:
            # Default to env var (Docker) or localhost (local dev)
            self.base_url = os.getenv("WEBSCRAPER_URL", "http://localhost:3005")
    
    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Helper para peticiones POST seguras."""
        try:
            response = requests.post(f"{self.base_url}{endpoint}", json=data, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling {endpoint}: {e}")
            return {"success": False, "error": str(e)}

    def _get(self, endpoint: str) -> Dict[str, Any]:
        """Helper para peticiones GET seguras."""
        try:
            response = requests.get(f"{self.base_url}{endpoint}", timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling {endpoint}: {e}")
            return {"success": False, "error": str(e)}

    def check_health(self) -> bool:
        """Verifica si el servicio de scraping está disponible."""
        try:
            res = self._get("/health")
            return res.get("status") == "ok"
        except:
            return False

    # --------------------------------------------------------------------------
    # Specialized Search Methods
    # --------------------------------------------------------------------------

    def search_prices(self, product: str) -> Dict[str, Any]:
        """
        Busca precios en MercadoLibre y Profeco.
        endpoint: POST /prices
        """
        logger.info(f"💰 Searching prices for: {product}")
        return self._post("/prices", {"product": product})

    def search_agricultural_prices(self, product: str) -> List[Dict[str, Any]]:
        """
        Busca precios agrícolas en SNIIM.
        endpoint: POST /prices/agriculture
        """
        logger.info(f"🌽 Searching SNIIM prices for: {product}")
        res = self._post("/prices/agriculture", {"product": product})
        return res.get("data", [])

    def search_retail_prices(self, product: str) -> List[Dict[str, Any]]:
        """
        Busca precios en supermercados (Walmart, Soriana, etc).
        endpoint: POST /prices/retail
        """
        logger.info(f"🛒 Searching Retail prices for: {product}")
        res = self._post("/prices/retail", {"product": product})
        return res.get("data", [])

    def search_competitors(self, industry: str, location: str) -> List[Dict[str, Any]]:
        """
        Busca competidores en Google Maps.
        endpoint: POST /search (type=competitors)
        """
        logger.info(f"🏢 Searching competitors: {industry} in {location}")
        res = self._post("/search", {
            "query": industry,
            "location": location,
            "type": "competitors"
        })
        return res.get("results", [])

    def search_general(self, query: str, region: str = "mx-es") -> List[Dict[str, Any]]:
        """
        Búsqueda general en DuckDuckGo.
        endpoint: POST /search (type=general)
        region: código de región (mx-es, us-en, cn-zh, etc.)
        """
        logger.info(f"🔍 General search: {query} (Region: {region})")
        res = self._post("/search", {
            "query": query,
            "type": "general",
            "region": region
        })
        return res.get("results", [])

    def get_economic_indicators(self) -> Dict[str, Any]:
        """
        Obtiene indicadores económicos (INEGI, Banxico).
        endpoint: GET /indicators
        """
        logger.info("📈 Fetching economic indicators")
        return self._get("/indicators")

    def full_business_research(self, business_name: str, industry: str, location: str) -> Dict[str, Any]:
        """
        Realiza una investigación completa (360°) para un negocio.
        endpoint: POST /research
        """
        logger.info(f"🚀 Full research for {business_name} ({industry})")
        return self._post("/research", {
            "businessName": business_name,
            "industry": industry,
            "location": location
        })

# ==============================================================================
# MAIN (Test)
# ==============================================================================

if __name__ == "__main__":
    # Configurar logging para ver output en consola
    logging.basicConfig(level=logging.INFO)
    
    client = WebResearchClient()
    
    if client.check_health():
        print("✅ Service is running")
        
        # Test 1: Indicadores
        indicators = client.get_economic_indicators()
        print("\n📈 Indicators:", json.dumps(indicators, indent=2)[:200] + "...")
        
        # Test 2: Precios (simulado si no hay internet)
        # prices = client.search_prices("Harina de trigo 1kg")
        # print("\n💰 Prices:", json.dumps(prices, indent=2)[:200] + "...")
        
    else:
        print("❌ Service is NOT running at http://localhost:3005")
