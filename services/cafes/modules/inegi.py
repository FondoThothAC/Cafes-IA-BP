import requests
import os

# INEGI Indicator IDs for demographic data (Censo 2020)
# Full catalog: https://www.inegi.org.mx/servicios/api_indicadores.html
DEMOGRAPHIC_INDICATORS = {
    # Population
    "poblacion_total": "6207019014",
    "poblacion_masculina": "6207019015",
    "poblacion_femenina": "6207019016",
    
    # Age Groups
    "edad_0_14": "6207019017",
    "edad_15_29": "6207019018",
    "edad_30_59": "6207019019",
    "edad_60_plus": "6207019020",
    
    # Education
    "alfabetizacion": "6207020032",
    "edu_primaria": "6207020033",
    "edu_secundaria": "6207020034",
    "edu_superior": "6207020035",
    "sin_escolaridad": "6207020036",
    
    # Economic Activity
    "pea_total": "6207020001",         # Población económicamente activa
    "pea_ocupada": "6207020002",       # Ocupados
    "pea_desocupada": "6207020003",    # Desocupados
    "pea_informal": "6207020004",      # Sector informal
    
    # Technology Access
    "hogares_celular": "6207067001",
    "hogares_internet": "6207067002",
    "hogares_computadora": "6207067003",
    "hogares_television": "6207067004",
    
    # Housing
    "viviendas_total": "6207019003",
    "viviendas_electricidad": "6207019004",
    "viviendas_agua": "6207019005",
    "viviendas_drenaje": "6207019006",
    
    # Health
    "con_seguro_salud": "6207074001",
    "sin_seguro_salud": "6207074002",
    "con_discapacidad": "6207074003",
    
    # Income Levels
    "ingreso_1sm": "6207078001",       # Hasta 1 salario mínimo
    "ingreso_1_2sm": "6207078002",     # 1-2 salarios mínimos
    "ingreso_2_3sm": "6207078003",     # 2-3 salarios mínimos
    "ingreso_3_5sm": "6207078004",     # 3-5 salarios mínimos
    "ingreso_5plus_sm": "6207078005",  # 5+ salarios mínimos
    
    # Migration & Indigenous
    "migrantes": "6207085001",
    "lengua_indigena": "6207085002",
    
    # Marital Status
    "casados": "6207019025",
    "solteros": "6207019026",
    "union_libre": "6207019027",
}

# KPIs Específicos para Plan de Negocios (ENIGH / Económicos)
KPI_INDICATORS = {
    # Gasto Trimestral Promedio por Hogar (ENIGH 2022)
    "gasto_alimentos": "673559",       # Alimentos, bebidas y tabaco
    "gasto_vestido": "673560",         # Vestido y calzado
    "gasto_vivienda": "673561",        # Vivienda y servicios
    "gasto_limpieza": "673562",        # Artículos de limpieza
    "gasto_salud": "673563",           # Salud
    "gasto_transporte": "673564",      # Transporte y comunicaciones
    "gasto_educacion": "673565",       # Educación y esparcimiento
    "gasto_personal": "673566",        # Cuidados personales
    
    # Ingresos (ENIGH 2022)
    "ingreso_corriente": "673539",     # Ingreso corriente promedio trimestral
    
    # Precios Consumidor (INPC - Mensual)
    "inpc_general": "628194",          # Índice Nacional de Precios al Consumidor
    "inflacion_anual": "628229",       # Inflación anual
    
    # TIC en Hogares (ENDUTIH)
    "usuarios_internet": "674147",     # Usuarios de internet
    "usuarios_celular": "674148",      # Usuarios de teléfono celular
}

# Geographic codes (INEGI) - Principales de Sonora y Nacional
GEO_CODES = {
    "nacional": "00",
    "sonora": "26",
    "hermosillo": "26030",
    "obregon": "26018",
    "nogales": "26043",
    "guaymas": "26029",
    "navojoa": "26042",
    "slrc": "26055",  # San Luis Río Colorado
    "agua_prieta": "26002",
    "caborca": "26017",
    "cananea": "26019",
    "empalme": "26025",
    "huatabampo": "26033",
    "puerto_penasco": "26048",
    "etchojoa": "26026",
}

# DENUE Activity Sectors (SCIAN 2023 - Gran Sector)
ACTIVITY_SECTORS = {
    "11": "Agricultura, cría y explotación de animales, aprovechamiento forestal, pesca y caza",
    "21": "Minería",
    "22": "Generación, transmisión, distribución y comercialización de energía eléctrica, suministro de agua y de gas natural",
    "23": "Construcción",
    "31-33": "Industrias manufactureras",
    "43": "Comercio al por mayor",
    "46": "Comercio al por menor",
    "48-49": "Transportes, correos y almacenamiento",
    "51": "Información en medios masivos",
    "52": "Servicios financieros y de seguros",
    "53": "Servicios inmobiliarios y de alquiler de bienes muebles e intangibles",
    "54": "Servicios profesionales, científicos y técnicos",
    "55": "Corporativos",
    "56": "Servicios de apoyo a los negocios y manejo de residuos, y servicios de remediación",
    "61": "Servicios educativos",
    "62": "Servicios de salud y de asistencia social",
    "71": "Servicios de esparcimiento culturales y deportivos, y otros servicios recreativos",
    "72": "Servicios de alojamiento temporal y de preparación de alimentos y bebidas",
    "81": "Otros servicios excepto actividades gubernamentales",
    "93": "Actividades legislativas, gubernamentales, de impartición de justicia y de organismos internacionales y extraterritoriales",
    # Subsectores populares
    "722": "Servicios de preparación de alimentos y bebidas (General)",
    "7221": "Restaurantes con servicio de preparación (Subsector)",
    "722515": "Cafeterías, fuentes de sodas, neverías, refresquerías y similares",
}


class InegiService:
    def __init__(self):
        self.api_token = os.getenv("INEGI_API_TOKEN", "1b9e230f-2ae0-48db-bd20-8810b1db575e")
        self.denue_url = "https://www.inegi.org.mx/app/api/denue/v1/consulta"
        self.indicators_url = "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR"

    def get_competitors(self, keyword: str, lat: float, lon: float, radius: int = 2000):
        """
        Busca negocios en INEGI DENUE dado una palabra clave y coordenadas.
        Radio en metros.
        """
        url = f"{self.denue_url}/Buscar/{keyword}/{lat},{lon}/{radius}/{self.api_token}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return self._parse_denue_results(data)
        except Exception as e:
            print(f"Error fetching INEGI DENUE data: {e}")
            return []
    
    def search_by_area_activity(self, area: str, activity: str, keyword: str = "",
                                 clave: str = "", estrato: str = ""):
        """
        Búsqueda por entidad y palabra clave usando BuscarEntidad.
        
        API Format: /BuscarEntidad/{keyword}/{entidad}/{page}/{pageSize}/{token}
        
        Args:
            area: Clave del área (26 = Sonora, 14 = Jalisco, 09 = CDMX)
            activity: Código SCIAN (no usado directamente - INEGI busca por texto)
            keyword: Nombre a buscar (ej: "restaurante", "cafeteria")
        
        Returns:
            Lista de establecimientos
        """
        # Extract state code (first 2 digits of area code)
        entidad = area[:2] if len(area) >= 2 else area
        
        # Build search term: use keyword if provided, otherwise generic "negocio"
        search_term = keyword.strip() if keyword and keyword.lower() != "todos" else "negocio"
        
        # BuscarEntidad format: /BuscarEntidad/{keyword}/{entidad}/{page}/{pageSize}/{token}
        page = 1
        page_size = 50  # Get up to 50 results
        
        url = f"{self.denue_url}/BuscarEntidad/{search_term}/{entidad}/{page}/{page_size}/{self.api_token}"
        
        try:
            print(f"DENUE BuscarEntidad URL: {url}")  # Debug log
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            data = response.json()
            print(f"DENUE returned {len(data) if isinstance(data, list) else 'non-list'} results")
            return self._parse_denue_results(data)
        except Exception as e:
            print(f"Error DENUE BuscarEntidad: {e}")
            return []
    
    def count_businesses(self, area: str, activity: str = "todos", estrato: str = "todos"):
        """
        Cuenta establecimientos por área, actividad y estrato.
        
        Returns:
            int: Número de establecimientos
        """
        url = f"{self.denue_url}/Cuantificar/{area}/{activity}/{estrato}/{self.api_token}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return int(response.text.strip())
        except Exception as e:
            print(f"Error DENUE Cuantificar: {e}")
            return 0
    
    def get_business_detail(self, clave: str):
        """
        Obtiene información detallada de un establecimiento por su clave.
        """
        url = f"{self.denue_url}/Ficha/{clave}/{self.api_token}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data:
                return self._parse_business(data[0] if isinstance(data, list) else data)
            return None
        except Exception as e:
            print(f"Error DENUE Ficha: {e}")
            return None
    
    def _parse_denue_results(self, data):
        """Parsea resultados de DENUE a formato estructurado."""
        if not data:
            return []
        
        results = []
        for item in data:
            results.append(self._parse_business(item))
        return results
    
    def _parse_business(self, item):
        """Parsea un registro de DENUE."""
        return {
            "clave": item.get("CLEE") or item.get("clee"),
            "id": item.get("Id") or item.get("id"),
            "nombre": item.get("Nombre") or item.get("nombre"),
            "razon_social": item.get("Razon_social") or item.get("razon_social"),
            "actividad": item.get("Clase_actividad") or item.get("clase_actividad"),
            "estrato": item.get("Estrato") or item.get("estrato"),
            "calle": item.get("Calle") or item.get("vialidad_principal"),
            "num_exterior": item.get("Num_Exterior") or item.get("num_exterior"),
            "colonia": item.get("Colonia") or item.get("colonia"),
            "cp": item.get("Cod_postal") or item.get("codigo_postal"),
            "localidad": item.get("Localidad") or item.get("localidad"),
            "telefono": item.get("Telefono") or item.get("telefono"),
            "email": item.get("Correo_e") or item.get("correo_electronico"),
            "sitio_web": item.get("Sitio_internet") or item.get("pagina_internet"),
            "latitud": item.get("Latitud") or item.get("latitud"),
            "longitud": item.get("Longitud") or item.get("longitud"),
            "tipo": item.get("Tipo") or item.get("tipo_establecimiento"),
        }

    def get_indicator(self, indicator_id: str, geo_code: str = "2603000"):
        """
        Obtiene un indicador específico del Banco de Indicadores INEGI.
        
        Args:
            indicator_id: ID del indicador INEGI
            geo_code: Código geográfico (default: Hermosillo)
        
        Returns:
            Dict con los datos del indicador
        """
        url = f"{self.indicators_url}/{indicator_id}/es/{geo_code}/true/BISE/2.0/{self.api_token}?type=json"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Parse INEGI response
                if "Series" in data and len(data["Series"]) > 0:
                    series = data["Series"][0]
                    obs = series.get("OBSERVATIONS", [])
                    if obs and len(obs) > 0:
                        return {
                            "indicator": series.get("INDICADOR"),
                            "value": float(obs[0].get("OBS_VALUE", 0)),
                            "unit": series.get("UNIT"),
                            "period": obs[0].get("TIME_PERIOD"),
                            "geo": series.get("COVERAGE_AREA")
                        }
                return None
            else:
                print(f"INEGI API error: {response.status_code}")
                return None
        except Exception as e:
            print(f"INEGI API exception: {e}")
            return None

    def get_demographics(self, geo_code: str = "2603000"):
        """
        Obtiene datos demográficos completos para una zona geográfica.
        
        Args:
            geo_code: Código INEGI (ej: 2603000 = Hermosillo)
        
        Returns:
            Dict con indicadores demográficos
        """
        result = {
            "geo_code": geo_code,
            "poblacion": {},
            "edad": {},
            "educacion": {},
            "empleo": {},
            "tecnologia": {},
            "vivienda": {},
            "salud": {},
            "ingresos": {}
        }
        
        # Population
        for key in ["poblacion_total", "poblacion_masculina", "poblacion_femenina"]:
            data = self.get_indicator(DEMOGRAPHIC_INDICATORS.get(key, ""), geo_code)
            if data:
                result["poblacion"][key] = data
        
        # Age
        for key in ["edad_0_14", "edad_15_29", "edad_30_59", "edad_60_plus"]:
            data = self.get_indicator(DEMOGRAPHIC_INDICATORS.get(key, ""), geo_code)
            if data:
                result["edad"][key] = data
        
        # Technology
        for key in ["hogares_celular", "hogares_internet", "hogares_computadora"]:
            data = self.get_indicator(DEMOGRAPHIC_INDICATORS.get(key, ""), geo_code)
            if data:
                result["tecnologia"][key] = data
        
        # Employment
        for key in ["pea_total", "pea_ocupada", "pea_informal"]:
            data = self.get_indicator(DEMOGRAPHIC_INDICATORS.get(key, ""), geo_code)
            if data:
                result["empleo"][key] = data
        
        return result

    def get_filter_options(self):
        """Returns available filter categories and their INEGI indicator IDs."""
        return {
            "indicators": DEMOGRAPHIC_INDICATORS,
            "geographic_codes": GEO_CODES,
            "categories": [
                {"id": "poblacion", "name": "Población", "filters": ["poblacion_total", "poblacion_masculina", "poblacion_femenina"]},
                {"id": "edad", "name": "Grupos de Edad", "filters": ["edad_0_14", "edad_15_29", "edad_30_59", "edad_60_plus"]},
                {"id": "educacion", "name": "Educación", "filters": ["alfabetizacion", "edu_primaria", "edu_secundaria", "edu_superior", "sin_escolaridad"]},
                {"id": "empleo", "name": "Actividad Económica", "filters": ["pea_total", "pea_ocupada", "pea_desocupada", "pea_informal"]},
                {"id": "tecnologia", "name": "Acceso Tecnológico", "filters": ["hogares_celular", "hogares_internet", "hogares_computadora"]},
                {"id": "vivienda", "name": "Vivienda", "filters": ["viviendas_total", "viviendas_electricidad", "viviendas_agua", "viviendas_drenaje"]},
                {"id": "salud", "name": "Salud", "filters": ["con_seguro_salud", "sin_seguro_salud", "con_discapacidad"]},
                {"id": "ingresos", "name": "Nivel de Ingresos", "filters": ["ingreso_1sm", "ingreso_1_2sm", "ingreso_2_3sm", "ingreso_3_5sm", "ingreso_5plus_sm"]},
            ]
        }

    def get_kpis(self, geo_code: str = "26030"): # 26030 = Hermosillo (Municipio) - Check if ENIGH is available at Muni level, usually State (26)
        """
        Obtiene los KPIs financieros y de mercado (Gasto, Ingreso, Inflación).
        Intenta obtener datos a nivel municipal, si falla, hace fallback a estatal (26).
        """
        results = {}
        
        # Determine codes to try (Requested -> State -> National)
        state_code = geo_code[:2]
        
        # Batch Fetch logic could go here, but for simplicity/robustness we iterate
        for key, indicator_id in KPI_INDICATORS.items():
            # Try specific geo
            data = self.get_indicator(indicator_id, geo_code)
            
            # Fallback to State if None (Common for detailed surveys like ENIGH)
            if not data and len(geo_code) > 2:
                data = self.get_indicator(indicator_id, state_code)
                
            # Fallback to National
            if not data:
                data = self.get_indicator(indicator_id, "00")
                
            if data:
                results[key] = data
        
        return results

    def analyze_competitors(self, keyword, location_query):
        """Analiza competidores en una ubicación usando DENUE."""
        # Centro de Hermosillo por defecto
        lat = 29.072967
        lon = -110.955919
        
        input_keyword = keyword if keyword else "comercio"
        
        data = self.get_competitors(input_keyword, lat, lon)
        
        competitor_count = len(data) if data else 0
        competitor_names = [item.get('Nombre', 'N/A') for item in data[:5]] if data else []
        
        return {
            "count": competitor_count,
            "names": ", ".join(competitor_names),
            "raw_data": data[:5] if data else []
        }

