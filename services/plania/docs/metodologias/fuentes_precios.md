# 📦 Fuentes de Precios y Datos de Mercado - México

## Resumen

Este documento cataloga las fuentes de información para obtener precios, costos de materias primas, y datos de mercado en México. El agente Bob utiliza estas fuentes para investigación.

---

## Fuentes de Precios al Consumidor

### 1. Mercado Libre México
| Campo | Valor |
|-------|-------|
| **URL Base** | https://www.mercadolibre.com.mx |
| **API** | https://api.mercadolibre.com |
| **Tipo** | E-commerce general |
| **Cobertura** | Nacional |
| **Frecuencia** | Tiempo real |

**Uso:** Precios de referencia para productos de consumo, equipo, tecnología.

```python
# Ejemplo de consulta
def search_mercadolibre(query: str) -> list:
    url = f"https://api.mercadolibre.com/sites/MLM/search?q={query}&limit=10"
    # Returns: productos con precio, vendedor, condición
```

### 2. Walmart México
| Campo | Valor |
|-------|-------|
| **URL** | https://www.walmart.com.mx |
| **Tipo** | Supermercado/Retail |
| **Cobertura** | Nacional |
| **Categorías** | Alimentos, electrónica, hogar, juguetes |

**Uso:** Precios de consumo masivo, comparación con competencia retail.

### 3. Amazon México
| Campo | Valor |
|-------|-------|
| **URL** | https://www.amazon.com.mx |
| **API** | Amazon Product Advertising API |
| **Tipo** | E-commerce |
| **Cobertura** | Nacional |

**Uso:** Productos de tecnología, libros, general.

### 4. Chedraui
| Campo | Valor |
|-------|-------|
| **URL** | https://www.chedraui.com.mx |
| **Tipo** | Supermercado |
| **Cobertura** | Nacional |

### 5. Bodega Aurrerá
| Campo | Valor |
|-------|-------|
| **URL** | https://www.bodegaaurrera.com.mx |
| **Tipo** | Autoservicio económico |
| **Uso** | Precios populares, canasta básica |

---

## Fuentes Gubernamentales

### 1. PROFECO - Quién es Quién en los Precios (QQP)
| Campo | Valor |
|-------|-------|
| **URL** | https://www.profeco.gob.mx/precios/ |
| **API** | Datos abiertos PROFECO |
| **Tipo** | Comparador oficial de precios |
| **Categorías** | Canasta básica, combustibles, medicamentos |
| **Frecuencia** | Semanal |

**Uso:** Precios oficiales de referencia, canasta básica, benchmarks.

```json
// Ejemplo de datos
{
  "producto": "Leche 1L",
  "precio_min": 22.50,
  "precio_max": 28.00,
  "promedio": 25.25,
  "ciudad": "CDMX",
  "fecha": "2026-02-01"
}
```

### 2. INEGI - Índice Nacional de Precios al Consumidor (INPC)
| Campo | Valor |
|-------|-------|
| **URL** | https://www.inegi.org.mx/temas/inpc/ |
| **API** | https://www.inegi.org.mx/servicios/api_indicadores.html |
| **Tipo** | Índice de inflación |
| **Frecuencia** | Quincenal |

**Uso:** Inflación, ajuste de proyecciones, históricos de precios.

### 3. Banco de México - Indicadores Económicos
| Campo | Valor |
|-------|-------|
| **URL** | https://www.banxico.org.mx/SieInternet/ |
| **API** | SIE Banxico |
| **Tipo** | Indicadores macroeconómicos |
| **Datos** | Inflación, tipo de cambio, tasas de interés |

```python
# Series importantes
SERIES_BANXICO = {
    "inflacion_anual": "SP1",
    "tipo_cambio": "SF43718",
    "cetes_28": "SF43936",
    "tiie_28": "SF43783"
}
```

### 4. Diario Oficial de la Federación (DOF)
| Campo | Valor |
|-------|-------|
| **URL** | https://www.dof.gob.mx |
| **Tipo** | Publicaciones oficiales |
| **Datos** | Salarios mínimos, UMA, tarifas oficiales |

**Información clave:**
- Salario mínimo general y profesional
- Valor de la UMA (Unidad de Medida y Actualización)
- Tarifas de luz (CFE)
- Actualizaciones de NOMs

### 5. Secretaría de Economía - SIEM
| Campo | Valor |
|-------|-------|
| **URL** | https://www.siem.gob.mx |
| **Tipo** | Registro de empresas |
| **Datos** | Directorio de proveedores, competidores |

---

## Fuentes de Materias Primas

### 1. SNIIM - Sistema Nacional de Información e Integración de Mercados
| Campo | Valor |
|-------|-------|
| **URL** | http://www.economia-sniim.gob.mx |
| **Tipo** | Precios agrícolas |
| **Cobertura** | Centrales de abasto nacionales |
| **Categorías** | Frutas, verduras, granos, cárnicos |
| **Frecuencia** | Diaria |

**Uso principal:** Costos de materias primas para restaurantes, panaderías, agroindustria.

```json
// Ejemplo de datos
{
  "producto": "Harina de trigo 44kg",
  "central_abasto": "CDMX",
  "precio_min": 480.00,
  "precio_max": 520.00,
  "fecha": "2026-02-04"
}
```

### 2. Central de Abasto CDMX
| Campo | Valor |
|-------|-------|
| **URL** | https://ficeda.com.mx |
| **Tipo** | Mayor mercado de Latinoamérica |
| **Datos** | Precios de mayoreo |

### 3. SAGARPA/SIAP - Información Agroalimentaria
| Campo | Valor |
|-------|-------|
| **URL** | https://www.gob.mx/siap |
| **API** | Datos abiertos agricultura |
| **Tipo** | Producción y precios agrícolas |

### 4. ASERCA - Precios de Granos
| Campo | Valor |
|-------|-------|
| **URL** | https://www.gob.mx/aserca |
| **Tipo** | Commodities agrícolas |
| **Datos** | Maíz, trigo, sorgo, frijol |

---

## Fuentes Internacionales

### Commodities y Materias Primas

| Fuente | URL | Datos |
|--------|-----|-------|
| **Trading Economics** | tradingeconomics.com | Commodities globales |
| **Investing.com** | mx.investing.com | Futuros, metales, energía |
| **World Bank Commodity** | worldbank.org | Pink Sheet mensual |
| **CME Group** | cmegroup.com | Futuros agrícolas |
| **Alibaba** | alibaba.com | Precios de fábrica China |

### Para SaaS/Tecnología

| Fuente | URL | Datos |
|--------|-----|-------|
| **Capterra** | capterra.mx | Comparativo de software |
| **G2** | g2.com | Reviews y precios de SaaS |
| **Glassdoor** | glassdoor.com.mx | Salarios tech |
| **Levels.fyi** | levels.fyi | Compensación tech |

---

## Fuentes de Salarios

### 1. CONASAMI - Salarios Mínimos
| Campo | Valor |
|-------|-------|
| **URL** | https://www.gob.mx/conasami |
| **Datos** | Salarios mínimos por zona y profesión |
| **Frecuencia** | Anual |

```python
# Salarios mínimos 2026 (ejemplo)
SALARIOS_MINIMOS_2026 = {
    "general": 278.80,  # MXN/día
    "zona_libre": 419.88,
    "profesional_panadero": 285.52,
    "profesional_chofer": 295.34,
    "profesional_cocinero": 285.52
}
```

### 2. Indeed/Glassdoor
| Campo | Valor |
|-------|-------|
| **URL** | indeed.com.mx / glassdoor.com.mx |
| **Tipo** | Salarios reales de mercado |
| **Datos** | Por puesto, industria, ubicación |

### 3. IMSS - Salario Base de Cotización
| Campo | Valor |
|-------|-------|
| **URL** | https://www.imss.gob.mx |
| **Datos** | Promedios por industria |

---

## Fuentes de Competencia

### 1. DENUE - Directorio Estadístico Nacional de Unidades Económicas
| Campo | Valor |
|-------|-------|
| **URL** | https://www.inegi.org.mx/app/mapa/denue/ |
| **API** | API DENUE INEGI |
| **Tipo** | Registro de empresas |
| **Datos** | Ubicación, giro, tamaño |

```python
# Ejemplo de uso
def search_competitors_denue(lat, lng, activity, radius_meters=2000):
    url = f"https://www.inegi.org.mx/app/api/denue/v1/consulta/buscar/{activity}/{lat},{lng}/{radius_meters}"
    # Returns: lista de negocios cercanos del mismo giro
```

### 2. Google Maps / Places API
| Campo | Valor |
|-------|-------|
| **API** | Google Places API |
| **Datos** | Negocios, reviews, horarios |
| **Costo** | Pay per use |

### 3. Yelp
| Campo | Valor |
|-------|-------|
| **URL** | yelp.com.mx |
| **API** | Yelp Fusion API |
| **Datos** | Restaurantes, servicios, reviews |

---

## Integración en Bob Agent

### Módulo de Web Research

```python
class WebResearchEngine:
    """
    Motor de investigación web para el agente Bob.
    """
    
    SOURCES = {
        "precios_consumo": [
            "mercadolibre",
            "profeco",
            "walmart"
        ],
        "materias_primas": [
            "sniim",
            "central_abasto"
        ],
        "competencia": [
            "denue",
            "google_places"
        ],
        "indicadores": [
            "banxico",
            "inegi_inpc"
        ],
        "salarios": [
            "conasami",
            "indeed"
        ]
    }
    
    def research_prices(self, product: str, industry: str) -> dict:
        """
        Investiga precios de un producto según la industria.
        """
        if industry in ["panaderia", "restaurante", "alimentos"]:
            # Buscar en SNIIM para materias primas
            raw_prices = self._query_sniim(product)
            retail_prices = self._query_profeco(product)
        else:
            # Buscar en MercadoLibre/Walmart
            retail_prices = self._query_mercadolibre(product)
        
        return {
            "product": product,
            "sources": [...],
            "prices": {...},
            "last_updated": datetime.now()
        }
    
    def research_competitors(self, lat: float, lng: float, 
                            activity: str, radius: int = 2000) -> list:
        """
        Busca competidores cercanos vía DENUE.
        """
        return self._query_denue(lat, lng, activity, radius)
```

### Cache y Actualización

```python
CACHE_TTL = {
    "precios_consumo": 24 * 3600,      # 24 horas
    "materias_primas": 12 * 3600,      # 12 horas
    "indicadores_macro": 7 * 24 * 3600, # 1 semana
    "competencia": 30 * 24 * 3600,     # 1 mes
    "salarios": 90 * 24 * 3600         # 3 meses
}
```

---

## Notas para Búsquedas Internacionales

Cuando el proyecto requiere datos internacionales:

| Idioma | Fuentes |
|--------|---------|
| **Inglés** | Statista, IBISWorld, Bloomberg |
| **Chino** | Alibaba, 1688.com, Taobao |
| **Español (LATAM)** | MercadoLibre regional |
| **Francés** | Statista FR, INSEE |
| **Alemán** | Statista DE, Destatis |

El agente debe:
1. Traducir la consulta al idioma apropiado
2. Consultar la fuente
3. Convertir monedas a MXN usando tipo de cambio Banxico
4. Citar la fuente en el contexto del proyecto

---

*Documento generado para RAG de PlanIA - Febrero 2026*
