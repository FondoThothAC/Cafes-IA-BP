# 📋 Clasificación de Negocios - Tipos y Sectores

## Resumen

Clasificación completa de tipos de negocio para que el agente Bob pueda adaptar su análisis y prompts según el tipo específico de empresa.

---

## Por Modelo de Negocio

### B2C (Business to Consumer)
Venta directa al consumidor final.

| Subtipo | Descripción | Ejemplos |
|---------|-------------|----------|
| Retail físico | Tiendas de ladrillo y mortero | OXXO, Walmart, tienda de ropa |
| E-commerce | Venta en línea | Amazon, Shein, tienda Shopify |
| Servicios personales | Atención directa | Salón de belleza, gym, taller |
| Alimentos | Consumo inmediato | Restaurante, panadería, cafetería |
| Entretenimiento | Experiencias | Cine, eventos, turismo |

**Métricas clave B2C:**
- Ticket promedio
- Frecuencia de compra
- Retención de clientes
- NPS

---

### B2B (Business to Business)
Venta a otras empresas.

| Subtipo | Descripción | Ejemplos |
|---------|-------------|----------|
| Servicios profesionales | Consultoría, legal, contable | Deloitte, KPMG |
| Software empresarial | SaaS, licencias | Salesforce, SAP |
| Manufactura industrial | Insumos y componentes | Proveedores automotrices |
| Distribución | Mayoreo | NADRO, Grupo Modelo |
| Marketing/Publicidad | Agencias | WPP, Ogilvy |

**Métricas clave B2B:**
- LTV (Lifetime Value)
- CAC (Customer Acquisition Cost)
- Tasa de churn
- MRR/ARR (Monthly/Annual Recurring Revenue)
- Ciclo de ventas

---

### B2G (Business to Government)
Venta al gobierno.

| Subtipo | Descripción | Ejemplos |
|---------|-------------|----------|
| Licitaciones públicas | Proyectos grandes | Infraestructura, sistemas |
| Proveeduría | Insumos recurrentes | Papelería, uniformes |
| Servicios especializados | Consultoría técnica | Auditoría, seguridad |

**Métricas clave B2G:**
- Tasa de adjudicación
- Días de pago (DSO)
- Cartera de licitaciones
- Cumplimiento de contratos

---

### C2C (Consumer to Consumer)
Entre consumidores, facilitado por plataforma.

| Subtipo | Descripción | Ejemplos |
|---------|-------------|----------|
| Marketplace | Plataforma de intercambio | MercadoLibre, eBay |
| Compartidos | Economía colaborativa | Airbnb, BlaBlaCar |

---

### D2C (Direct to Consumer)
Fabricante vende directo, sin intermediarios.

| Subtipo | Descripción | Ejemplos |
|---------|-------------|----------|
| Marcas propias | Manufactura + venta | Warby Parker, Casper |
| Artesanal | Producción pequeña | Etsy, cervecerías artesanales |

---

## Por Sector Económico

### Sector Primario
Extracción de recursos naturales.

| Industria | Actividades | NOMs/Regulaciones |
|-----------|-------------|-------------------|
| Agricultura | Cultivo, cosecha | SAGARPA, NOM-037-FITO |
| Ganadería | Cría de animales | SENASICA |
| Pesca | Extracción marina | CONAPESCA |
| Minería | Extracción minerales | SE, SEMARNAT |
| Silvicultura | Explotación forestal | CONAFOR |

---

### Sector Secundario
Transformación de materias primas.

| Industria | Actividades | NOMs/Regulaciones |
|-----------|-------------|-------------------|
| Manufactura ligera | Textiles, alimentos, papel | NOM-251, NOM-050 |
| Manufactura pesada | Automotriz, maquinaria | NOM-001-STPS serie |
| Construcción | Edificación, obra civil | NOM construcción |
| Energía | Generación eléctrica | CRE, CFE |
| Química | Farmacéutica, plásticos | COFEPRIS |

---

### Sector Terciario (Servicios)

| Industria | Actividades | Regulaciones |
|-----------|-------------|--------------|
| Comercio | Retail, mayoreo | PROFECO |
| Transporte | Logística, pasajeros | SCT |
| Turismo | Hoteles, viajes | SECTUR |
| Financiero | Banca, seguros | CNBV, Banxico |
| Salud | Hospitales, clínicas | SS, COFEPRIS |
| Educación | Escuelas, capacitación | SEP |
| Tecnología | Software, IT | LFPDPPP |

---

### Sector Cuaternario (Conocimiento)

| Industria | Actividades |
|-----------|-------------|
| I+D | Investigación científica |
| Consultoría | Asesoría especializada |
| TI avanzado | IA, Big Data, Blockchain |

---

## Por Tamaño (Clasificación INEGI)

| Tamaño | Empleados | Ventas Anuales (MXN) |
|--------|-----------|----------------------|
| **Micro** | 1-10 | Hasta $4 millones |
| **Pequeña** | 11-50 | $4 - $100 millones |
| **Mediana** | 51-250 | $100 - $250 millones |
| **Grande** | 250+ | Más de $250 millones |

---

## Por Etapa de Crecimiento

### Startups

| Etapa | Características | Financiamiento típico |
|-------|-----------------|----------------------|
| Pre-seed | Solo idea, equipo formándose | FFF, grants |
| Seed | MVP, primeros usuarios | Ángeles, aceleradoras |
| Serie A | Product-market fit | VC: $1-5M USD |
| Serie B | Escalando | VC: $5-25M USD |
| Serie C+ | Expansión/Pre-IPO | VC: $25M+ USD |

### Empresas Establecidas

| Etapa | Características |
|-------|-----------------|
| Crecimiento | Expandiendo mercado |
| Madurez | Optimizando operaciones |
| Declive | Necesita renovación |
| Turnaround | Reestructuración |

---

## Por Cadena de Suministro

### Roles en la Cadena

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PROVEEDORES │───▶│  FABRICANTE  │───▶│ DISTRIBUIDOR │
└──────────────┘    └──────────────┘    └──────────────┘
                                               │
                                               ▼
                    ┌──────────────┐    ┌──────────────┐
                    │  CONSUMIDOR  │◀───│   RETAILER   │
                    └──────────────┘    └──────────────┘
```

| Rol | Prompts Específicos |
|-----|---------------------|
| **Proveedor** | Costos de MP, calidad, tiempos entrega |
| **Fabricante** | Capacidad, OEE, costos conversión |
| **Distribuidor** | Logística, cobertura, días inventario |
| **Retailer** | Rotación, margen, experiencia cliente |

---

## Integración en Bob Agent

### Detección Automática de Tipo

```python
BUSINESS_TYPE_KEYWORDS = {
    # Por modelo
    "b2c": ["tienda", "consumidor", "cliente final", "retail", "público"],
    "b2b": ["empresas", "corporativo", "industrial", "proveedor", "mayoreo"],
    "b2g": ["gobierno", "licitación", "público", "municipal", "federal"],
    "saas": ["software", "suscripción", "plataforma", "app", "digital"],
    
    # Por sector
    "primario": ["agricultura", "ganadería", "pesca", "minería", "forestal"],
    "secundario": ["manufactura", "fábrica", "producción", "industrial", "construcción"],
    "terciario": ["servicio", "consultoría", "comercio", "transporte", "turismo"],
    
    # Por industria específica
    "alimentos": ["restaurante", "comida", "panadería", "cocina", "bebidas"],
    "salud": ["clínica", "hospital", "médico", "farmacia", "dental"],
    "educacion": ["escuela", "academia", "cursos", "capacitación", "universidad"],
    "tecnologia": ["software", "app", "tech", "sistemas", "desarrollo"],
    "logistica": ["transporte", "envío", "almacén", "distribución", "cadena"]
}

def detect_business_type(description: str) -> dict:
    """
    Detecta el tipo de negocio a partir de la descripción.
    Retorna dict con modelo, sector, industria y tamaño.
    """
    description_lower = description.lower()
    
    result = {
        "modelo": None,
        "sector": None,
        "industria": None,
        "tipos_detectados": []
    }
    
    for type_name, keywords in BUSINESS_TYPE_KEYWORDS.items():
        for kw in keywords:
            if kw in description_lower:
                result["tipos_detectados"].append(type_name)
                break
    
    # Determinar modelo principal
    for modelo in ["b2c", "b2b", "b2g", "saas"]:
        if modelo in result["tipos_detectados"]:
            result["modelo"] = modelo
            break
    
    # Determinar sector
    for sector in ["primario", "secundario", "terciario"]:
        if sector in result["tipos_detectados"]:
            result["sector"] = sector
            break
    
    return result
```

### Prompts por Tipo

```python
PROMPTS_BY_TYPE = {
    "b2c": {
        "enfoque": "experiencia del cliente, ticket promedio, frecuencia",
        "metricas": ["NPS", "retención", "ticket_promedio", "frecuencia_compra"]
    },
    "b2b": {
        "enfoque": "ciclo de ventas, LTV, relaciones a largo plazo",
        "metricas": ["LTV", "CAC", "churn", "ciclo_ventas", "ARR"]
    },
    "b2g": {
        "enfoque": "licitaciones, cumplimiento, documentación",
        "metricas": ["tasa_adjudicacion", "dso", "contratos_activos"]
    },
    "saas": {
        "enfoque": "MRR, churn, unit economics",
        "metricas": ["MRR", "ARR", "churn", "LTV_CAC_ratio", "NRR"]
    }
}
```

---

## Programas de Apoyo por Tipo

### Para MiPyMEs

| Programa | Dependencia | Beneficio |
|----------|-------------|-----------|
| Crédito PyME | NAFIN | Financiamiento |
| MiPyME Digital | SE | Digitalización |
| Jóvenes Emprendedores | INADEM | Capacitación |
| Programas INAES | INAES | Economía social |

### Para Exportadores

| Programa | Dependencia | Beneficio |
|----------|-------------|-----------|
| IMMEX | SE | Régimen aduanero |
| PROSEC | SE | Preferencias arancelarias |
| ALTEX | SE | Facilidades exportación |
| ProMéxico | SE | Promoción internacional |

### Certificaciones Relevantes

| Certificación | Sector | Beneficio |
|--------------|--------|-----------|
| ISO 9001 | General | Calidad |
| ISO 14001 | Industrial | Ambiental |
| ISO 22000 | Alimentos | Inocuidad |
| ISO 27001 | Tech | Seguridad info |
| Empresa Socialmente Responsable | General | Reputación |
| Distintivo H | Alimentos | Higiene |

---

*Documento generado para RAG de PlanIA - Febrero 2026*
