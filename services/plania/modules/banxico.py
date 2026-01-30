"""
Banxico API Service - Datos económicos en tiempo real
Banco de México Sistema de Información Económica (SIE)
"""
import requests
import os
from datetime import datetime

# Series de Banxico más útiles para análisis empresarial
BANXICO_SERIES = {
    # Tipo de cambio
    "tipo_cambio_fix": "SF43718",      # Tipo de cambio FIX
    "tipo_cambio_compra": "SF43718",
    "tipo_cambio_venta": "SF43719",
    
    # Inflación
    "inflacion_general": "SP68257",     # INPC General
    "inflacion_subyacente": "SP68258",
    "inflacion_alimentos": "SP68296",
    
    # Tasas de interés
    "tasa_objetivo": "SF61745",         # Tasa de fondeo bancario objetivo
    "tasa_interbancaria": "SF43878",    # TIIE 28 días
    "cetes_28": "SF43936",              # CETES 28 días
    
    # Salarios
    "salario_minimo_general": "SL11297",  # Salario mínimo general diario
    "salario_minimo_zona_libre": "SL11296",
    
    # Indicadores económicos
    "igae": "SR16734",                  # Indicador Global Actividad Económica
    "pib": "SR17574",                   # PIB Trimestral
    
    # Precios
    "udi": "SP68088",                   # Unidad de Inversión
    "precio_petroleo": "SE47730",       # Precio mezcla mexicana
}

# Categorías para UI
BANXICO_CATEGORIES = [
    {
        "id": "tipo_cambio",
        "name": "Tipo de Cambio",
        "icon": "💱",
        "series": ["tipo_cambio_fix", "tipo_cambio_venta"]
    },
    {
        "id": "inflacion",
        "name": "Inflación",
        "icon": "📈",
        "series": ["inflacion_general", "inflacion_subyacente", "inflacion_alimentos"]
    },
    {
        "id": "tasas",
        "name": "Tasas de Interés",
        "icon": "🏦",
        "series": ["tasa_objetivo", "tasa_interbancaria", "cetes_28"]
    },
    {
        "id": "salarios",
        "name": "Salarios Mínimos",
        "icon": "💰",
        "series": ["salario_minimo_general", "salario_minimo_zona_libre"]
    },
    {
        "id": "economia",
        "name": "Indicadores Económicos",
        "icon": "📊",
        "series": ["igae", "pib", "udi", "precio_petroleo"]
    }
]


class BanxicoService:
    def __init__(self):
        self.api_token = os.getenv(
            "BANXICO_API_TOKEN",
            "898a538159ee2d3c3741018fec6dc22462759cf51d713475980b9ebd1458a49d"
        )
        self.base_url = "https://www.banxico.org.mx/SieAPIRest/service/v1/series"
    
    def _make_request(self, endpoint: str):
        """Realiza petición a la API de Banxico."""
        headers = {
            "Bmx-Token": self.api_token
        }
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=headers,
                timeout=15
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Banxico API error: {e}")
            return None
    
    def get_serie(self, serie_id: str, last_n: int = 10):
        """
        Obtiene datos de una serie de Banxico.
        
        Args:
            serie_id: ID de la serie (ej: SF43718)
            last_n: Últimos N datos a obtener
        
        Returns:
            Dict con datos de la serie
        """
        endpoint = f"/{serie_id}/datos/oportuno?mediaType=json"
        
        data = self._make_request(endpoint)
        
        if data and "bmx" in data:
            series = data["bmx"].get("series", [])
            if series:
                serie_data = series[0]
                return {
                    "id": serie_id,
                    "titulo": serie_data.get("titulo"),
                    "datos": serie_data.get("datos", [])[-last_n:],
                    "unidad": self._extract_unit(serie_data.get("titulo", ""))
                }
        return None
    
    def get_multiple_series(self, serie_ids: list):
        """Obtiene múltiples series en una sola petición."""
        ids = ",".join(serie_ids)
        endpoint = f"/{ids}/datos/oportuno?mediaType=json"
        
        data = self._make_request(endpoint)
        
        result = {}
        if data and "bmx" in data:
            for serie in data["bmx"].get("series", []):
                id_serie = serie.get("idSerie")
                result[id_serie] = {
                    "titulo": serie.get("titulo"),
                    "datos": serie.get("datos", []),
                    "unidad": self._extract_unit(serie.get("titulo", ""))
                }
        return result
    
    def get_tipo_cambio(self):
        """Obtiene tipo de cambio actual."""
        data = self.get_serie("SF43718")
        if data and data.get("datos"):
            ultimo = data["datos"][-1]
            return {
                "valor": float(ultimo.get("dato", "0").replace(",", "")),
                "fecha": ultimo.get("fecha"),
                "titulo": "Tipo de Cambio FIX"
            }
        # Fallback
        return {
            "valor": 17.15,
            "fecha": datetime.now().strftime("%d/%m/%Y"),
            "titulo": "Tipo de Cambio (estimado)"
        }
    
    def get_inflacion(self):
        """Obtiene inflación actual."""
        data = self.get_serie("SP68257")
        if data and data.get("datos"):
            ultimo = data["datos"][-1]
            return {
                "valor": float(ultimo.get("dato", "0").replace(",", "")),
                "fecha": ultimo.get("fecha"),
                "titulo": "Inflación General Anual"
            }
        return {
            "valor": 4.5,
            "fecha": datetime.now().strftime("%d/%m/%Y"),
            "titulo": "Inflación (estimada)"
        }
    
    def get_tasa_interes(self):
        """Obtiene tasa de interés de referencia."""
        data = self.get_serie("SF61745")
        if data and data.get("datos"):
            ultimo = data["datos"][-1]
            return {
                "valor": float(ultimo.get("dato", "0").replace(",", "")),
                "fecha": ultimo.get("fecha"),
                "titulo": "Tasa Objetivo Banco de México"
            }
        return {
            "valor": 10.0,
            "fecha": datetime.now().strftime("%d/%m/%Y"),
            "titulo": "Tasa Objetivo (estimada)"
        }
    
    def get_salario_minimo(self):
        """Obtiene salario mínimo actual."""
        data = self.get_serie("SL11297")
        if data and data.get("datos"):
            ultimo = data["datos"][-1]
            return {
                "valor": float(ultimo.get("dato", "0").replace(",", "")),
                "fecha": ultimo.get("fecha"),
                "titulo": "Salario Mínimo General Diario"
            }
        # Fallback 2025
        return {
            "valor": 278.80,
            "fecha": "01/01/2025",
            "titulo": "Salario Mínimo 2025"
        }
    
    def get_panel_economico(self):
        """Obtiene panel con indicadores económicos clave."""
        return {
            "tipo_cambio": self.get_tipo_cambio(),
            "inflacion": self.get_inflacion(),
            "tasa_interes": self.get_tasa_interes(),
            "salario_minimo": self.get_salario_minimo(),
            "categorias": BANXICO_CATEGORIES,
            "series_disponibles": BANXICO_SERIES,
            "actualizado": datetime.now().isoformat()
        }
    
    def _extract_unit(self, titulo: str) -> str:
        """Extrae unidad del título de la serie."""
        if "pesos" in titulo.lower():
            return "MXN"
        if "porcentaje" in titulo.lower() or "%" in titulo:
            return "%"
        if "dólares" in titulo.lower():
            return "USD"
        return ""
