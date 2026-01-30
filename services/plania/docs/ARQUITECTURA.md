# 📚 PlanIA - Arquitectura del Proyecto

## Descripción General
**PlanIA** es una plataforma web para la creación de planes de negocio inteligentes.
Permite a emprendedores crear planes de negocio completos con análisis de mercado INEGI, 
proyecciones financieras, organigrama con cálculo de nómina, y exportación a PDF profesional.

---

## 🏗️ Arquitectura de Archivos

```
PlanIA/
├── public/                     # Frontend - Archivos accesibles desde navegador
│   ├── css/
│   │   └── plania-core.css     # Estilos globales del sistema
│   ├── js/
│   │   └── plania-core.js      # Núcleo JavaScript - Navegación global, estado de proyecto
│   ├── data/
│   │   └── municipios_mexico.json  # Catálogo INEGI de estados y municipios
│   ├── uploads/                # Archivos subidos por usuarios (logos, imágenes)
│   │
│   │── 📊 MÓDULOS PRINCIPALES ──────────────────────────────
│   ├── index.html              # Página de inicio / dashboard
│   ├── projects_list.html      # Lista de proyectos del usuario
│   ├── wizard.html             # Asistente paso a paso para crear proyectos
│   │
│   │── 📈 MÓDULOS FINANCIEROS ──────────────────────────────
│   ├── revenue_projection.html     # Proyección de ingresos (productos/precios)
│   ├── cost_projection.html        # Proyección de costos (fijos/variables)
│   ├── investment_budget.html      # Presupuesto de inversión inicial
│   ├── income_statement.html       # Estado de resultados proyectado
│   ├── balance_general.html        # Balance general
│   ├── estado_resultados.html      # Estado de resultados contable
│   ├── financial_planner.html      # Flujo de caja y punto de equilibrio
│   ├── kpis.html                   # Indicadores clave de rendimiento
│   │
│   │── 📍 MÓDULOS DE MERCADO ───────────────────────────────
│   ├── market_study.html       # Estudio de mercado con mapas INEGI
│   ├── customers.html          # Perfil del cliente objetivo
│   ├── customer_research.html  # Investigación NDD (admin interno)
│   ├── customer_survey.html    # Encuesta pública para clientes
│   ├── surveys.html            # Gestión de encuestas
│   │
│   │── 🎨 MÓDULOS DE IDENTIDAD ─────────────────────────────
│   ├── brand_identity.html     # Identidad de marca (logo, colores)
│   ├── canvas.html             # Business Model Canvas
│   ├── foda.html               # Análisis FODA
│   │
│   │── 👥 MÓDULOS ORGANIZACIONALES ─────────────────────────
│   ├── organization.html       # Organigrama y nómina
│   ├── payroll.html            # Cálculo de nómina detallado
│   ├── operations.html         # Plan operativo
│   ├── marketing_metrics.html  # Métricas de marketing
│   │
│   │── 📄 EXPORTACIÓN ──────────────────────────────────────
│   ├── export_pdf.html         # Generador de PDF del plan de negocios
│   ├── export_pdf.php          # Backend para generación de PDF
│   ├── admin_grid.html         # Panel de administración
│   │
│   │── 🔌 APIs / BACKEND ───────────────────────────────────
│   ├── api_banxico.php         # Proxy para API de Banxico (inflación)
│   ├── api_denue.php           # Proxy para API DENUE (competidores)
│   ├── api_inegi_ageb.php      # Proxy para API INEGI (AGEB)
│   ├── api_inegi_poblacion.php # Proxy para API INEGI (población)
│   ├── api_indicadores.php     # Proxy para indicadores económicos
│   ├── save_row.php            # API para guardar datos en BD
│   └── upload_file.php         # API para subir archivos
```

---

## 🧠 Núcleo del Sistema (`plania-core.js`)

### Funciones Principales:

| Función | Descripción |
|---------|-------------|
| `PlanIA.init()` | Inicializa el sistema, carga proyecto actual |
| `PlanIA.getCurrentProject()` | Retorna el proyecto actualmente seleccionado |
| `PlanIA.setProject(id)` | Cambia el proyecto activo |
| `PlanIA.saveField(field, value)` | Guarda un campo en el proyecto actual |
| `PlanIA.loadProjectData()` | Carga datos del proyecto desde backend |
| `renderNavbar()` | Dibuja la barra de navegación global |

### Eventos Globales:
- `plania:projectChanged` - Se dispara al cambiar de proyecto
- `plania:dataSaved` - Se dispara al guardar datos

---

## 📍 Módulo: Estudio de Mercado (`market_study.html`)

### Propósito:
Permite al usuario dibujar su área de influencia en un mapa y obtener datos demográficos
de INEGI (población, edad, género) y competidores de DENUE.

### Funciones Clave:

```javascript
// Carga el catálogo de estados/municipios desde JSON
async function loadCatalogoMunicipios()

// Puebla el dropdown de estados
function loadEstados()

// Puebla el dropdown de municipios según el estado
function loadMunicipios()

// Centra el mapa en el municipio (usa geocodificación si no hay coords)
async function centerOnMunicipio()

// Carga datos INEGI (AGEB, población, manzanas)
async function loadINEGIData()

// Busca competidores en DENUE
async function searchDENUE()

// Guarda el análisis de mercado en el proyecto
async function saveAnalysisToProject()
```

### Campos que guarda:
- `d6_analisis_mercado_json` - Objeto JSON con:
  - `ubicacion` - Lat/lng del negocio
  - `poblacion` - Datos demográficos
  - `competidores` - Lista de competidores DENUE
  - `mapImageBase64` - Captura del mapa

---

## 🔬 Módulo: Investigación de Cliente (`customer_research.html`)

### Propósito:
Herramienta interna para validar N-D-D (Necesidad, Deseo, Demanda) mediante encuestas
a clientes potenciales, por producto.

### Flujo:
1. Selecciona producto (del módulo de Ingresos)
2. Registra respuestas de cada persona encuestada
3. Ve métricas y embudo de conversión
4. Guarda estadísticas al proyecto

### Funciones Clave:

```javascript
// Carga productos desde g12_proyeccion_ingresos_json
function loadProducts()

// Selecciona un producto para evaluar
function selectProduct(idx)

// Genera opciones de precio dinámicas (50%, 75%, 100%, 125%, 150%)
function generatePriceRanges(basePrice)

// Registra una respuesta de encuesta
function addResponse()

// Calcula y guarda estadísticas agregadas al proyecto
async function saveToProject()

// Genera enlace para encuesta pública
function getSurveyLink()
```

### Campos que guarda:
- `i_ndd_responses_json` - Todas las respuestas por producto
- `i_alcance_pct` - % conversión Necesidad → Deseo
- `i_conversion_pct` - % conversión Deseo → Demanda

---

## 📋 Módulo: Encuesta Pública (`customer_survey.html`)

### Propósito:
Página pública que el emprendedor comparte con clientes potenciales.
Las respuestas se guardan automáticamente en el proyecto.

### URL de acceso:
```
/customer_survey.html?p={projectId}&prod={productIndex}
```

### Flujo:
1. Carga datos del proyecto y producto via URL
2. Personaliza preguntas con nombre del producto
3. Cliente responde las 5 preguntas
4. Respuesta se guarda en `i_ndd_responses_json`

---

## 👥 Módulo: Organización (`organization.html`)

### Propósito:
Gestiona el organigrama de la empresa y calcula la nómina con cargas sociales IMSS.

### Funciones Clave:

```javascript
// Agrega un nuevo puesto
function addRole()

// Agrega un integrante (children) a un puesto
function addChild(roleIndex)

// Calcula cargas sociales IMSS/INFONAVIT/ISN
function calculateSocialCharge(salary, riskClass)

// Dibuja el organigrama visual
function renderRoles()

// Obtiene inflación de Banxico
async function fetchBanxicoInflation()

// Guarda organigrama en proyecto
async function saveOrg()
```

### Campos que guarda:
- `c4_organigrama_json` - Array de roles con:
  - `title`, `salary`, `riskClass`, `count`
  - `children` - Subroles

### Cálculo de Carga Social (IMSS 2026):
1. Riesgo de Trabajo (0.5%-7.5% según clase)
2. Cuota Fija EyM (20.4% UMA)
3. Excedente (1.1% sobre SBC - 3 UMA)
4. Prestaciones en Dinero (0.7%)
5. Gastos Médicos Pensionados (1.05%)
6. Invalidez y Vida (1.75%)
7. Retiro SAR (2.0%)
8. Cesantía y Vejez (3.15%)
9. Guarderías (1.0%)
10. INFONAVIT (5.0%)
11. ISN Sonora (3.0%)

---

## 📄 Módulo: Exportar PDF (`export_pdf.html`)

### Propósito:
Genera un documento PDF profesional del plan de negocios completo.

### Secciones que incluye:
1. **Portada** - Logo, nombre, resumen ejecutivo
2. **Estudio de Mercado** - Mapas, segmento, competidores
3. **Análisis del Cliente** - Buyer personas, Customer Journey, NDD
4. **Organigrama** - Estructura visual, nómina
5. **Marketing** - 4Ps, FODA, Canvas
6. **Finanzas** - Inversión, flujo de caja, punto de equilibrio

### Librerías usadas:
- `Chart.js` - Gráficas de barras/líneas/donas
- `html2canvas` - Captura de elementos HTML a imagen

---

## 🔌 APIs Backend (PHP)

### `save_row.php`
Guarda cualquier registro en la base de datos.
```php
// POST: { table: 'proyectos', id: 123, campo: 'valor', ... }
```

### `api_banxico.php`
Proxy para API de Banco de México.
```javascript
fetch('api_banxico.php?serie=SP1')
// Retorna: { valor: 4.5, fecha: '2026-01-15' }
```

### `api_denue.php`
Proxy para Directorio Estadístico Nacional de Unidades Económicas.
```javascript
fetch('api_denue.php?lat=29.07&lng=-110.95&actividad=restaurante')
// Retorna: [{ nombre, direccion, lat, lng }, ...]
```

### `api_inegi_ageb.php`
Obtiene polígonos de AGEB urbana para visualizar en mapa.

### `api_inegi_poblacion.php`
Obtiene datos de población del Censo 2020.

---

## 📊 Estructura de Datos del Proyecto

Los proyectos se almacenan en la tabla `proyectos` con los siguientes campos principales:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INT | ID único del proyecto |
| `user_id` | INT | ID del usuario dueño |
| `a1_nombre_negocio` | TEXT | Nombre del negocio |
| `b4_cliente_objetivo_resumen` | TEXT | Descripción del cliente objetivo |
| `c4_organigrama_json` | JSON | Estructura organizacional |
| `d6_analisis_mercado_json` | JSON | Datos del estudio de mercado |
| `e3_productos_bom_json` | JSON | Bill of Materials (BOM) |
| `g12_proyeccion_ingresos_json` | JSON | Productos y proyección de ingresos |
| `h_presupuesto_inversion_json` | JSON | Presupuesto de inversión |
| `i_ndd_responses_json` | JSON | Respuestas de encuestas NDD |
| `i_alcance_pct` | FLOAT | % conversión Necesidad→Deseo |
| `i_conversion_pct` | FLOAT | % conversión Deseo→Demanda |

---

## 🔄 Flujo de Datos Típico

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Usuario   │───▶│  Módulo HTML │───▶│  save_row   │
│  (Browser)  │    │  (Frontend)  │    │    .php     │
└─────────────┘    └──────────────┘    └─────────────┘
       ▲                  │                   │
       │                  ▼                   ▼
       │           ┌──────────────┐    ┌─────────────┐
       └───────────│ plania-core  │◀───│  Database   │
                   │    .js       │    │  (MySQL)    │
                   └──────────────┘    └─────────────┘
```

---

## 🐛 Debugging Tips

### Ver proyecto actual en consola:
```javascript
console.log(PlanIA.getCurrentProject());
```

### Ver todos los datos de un campo JSON:
```javascript
JSON.parse(PlanIA.getCurrentProject().g12_proyeccion_ingresos_json);
```

### Forzar recarga de proyecto:
```javascript
PlanIA.loadProjectData().then(() => console.log('Recargado'));
```

### Ver respuestas de encuestas:
```javascript
JSON.parse(PlanIA.getCurrentProject().i_ndd_responses_json);
```

---

## 📝 Convenciones de Código

### Nombrado de campos en BD:
- `a1_`, `b4_`, etc. = Sección del plan de negocios
- `_json` = Campo que almacena JSON
- `_pct` = Campo que almacena porcentaje

### IDs de elementos HTML:
- `selectEstado`, `selectMunicipio` = Dropdowns
- `btn-*` = Botones
- `*-container`, `*-grid` = Contenedores

### Eventos personalizados:
- Prefijo `plania:` para eventos del sistema

---

*Documentación generada: Enero 2026*
*Versión: 1.0*
