# 🗺️ Guía del Módulo: Estudio de Mercado

## Archivo: `market_study.html`

## Propósito
Permite análisis geográfico de mercado usando datos de INEGI y DENUE.
El usuario dibuja un área en el mapa y obtiene información demográfica y de competidores.

---

## Estructura HTML Principal

```html
<!-- Barra de control superior -->
<div class="control-bar">
    <select id="selectEstado">    <!-- Dropdown de estados -->
    <select id="selectMunicipio"> <!-- Dropdown de municipios -->
    <button>Cargar Datos INEGI</button>
</div>

<!-- Mapa Leaflet -->
<div id="map"></div>

<!-- Panel lateral derecho con estadísticas -->
<div class="stats-panel">
    <div id="areaStats">     <!-- Área y población -->
    <div id="denueStats">    <!-- Competidores -->
    <div id="funnelStats">   <!-- Embudo de ventas -->
</div>
```

---

## Variables Globales

```javascript
// === MAPAS ===
let map;           // Instancia principal de Leaflet
let drawnItems;    // Capa de dibujos del usuario (polígonos, círculos)
let businessMarker; // Marcador de ubicación del negocio

// === CAPAS DE DATOS ===
let agebLayer;     // GeoJSON de AGEB (Áreas Geoestadísticas Básicas)
let manzanasLayer; // GeoJSON de manzanas urbanas
let denueMarkers;  // Array de marcadores de competidores

// === DATOS CARGADOS ===
let popData;       // Datos de población {pop, men, women, young, adult, senior}
let denueData;     // Array de unidades económicas del DENUE

// === CATÁLOGOS ===
let ESTADOS;       // Array de estados [{cve, nombre}]
let MUNICIPIOS;    // Object de municipios por estado {'26': {'001': 'Aconchi', ...}}
```

---

## Funciones Principales

### 1. `loadCatalogoMunicipios()`
**Propósito:** Carga el catálogo de estados y municipios desde JSON.

```javascript
async function loadCatalogoMunicipios() {
    // 1. Fetch del archivo JSON
    const res = await fetch('data/municipios_mexico.json');
    const data = await res.json();
    
    // 2. Guarda en variables globales
    ESTADOS = data.estados;      // Array de 32 estados
    MUNICIPIOS = data.municipios; // Object con ~2500 municipios
    
    // 3. Si falla, usa fallback con Sonora básico
}
```

---

### 2. `loadEstados()`
**Propósito:** Llena el dropdown de estados.

```javascript
function loadEstados() {
    const select = document.getElementById('selectEstado');
    
    // 1. Limpia opciones existentes
    select.innerHTML = '<option value="">Selecciona estado...</option>';
    
    // 2. Agrega cada estado del catálogo
    ESTADOS.forEach(e => {
        const opt = document.createElement('option');
        opt.value = e.cve;        // Ej: '26'
        opt.textContent = e.nombre; // Ej: 'Sonora'
        select.appendChild(opt);
    });
    
    // 3. Dispara carga de municipios para estado default
    loadMunicipios();
}
```

---

### 3. `loadMunicipios()`
**Propósito:** Llena el dropdown de municipios según el estado seleccionado.

```javascript
function loadMunicipios() {
    const estado = document.getElementById('selectEstado').value;
    const select = document.getElementById('selectMunicipio');
    
    // 1. Obtiene municipios del estado
    const muns = MUNICIPIOS[estado] || {};
    
    // 2. Ordena alfabéticamente
    const sorted = Object.entries(muns).sort((a,b) => a[1].localeCompare(b[1]));
    
    // 3. Genera opciones
    select.innerHTML = sorted.map(([cve, nom]) => 
        `<option value="${cve}">${nom}</option>`
    ).join('');
}
```

---

### 4. `centerOnMunicipio()`
**Propósito:** Centra el mapa en el municipio seleccionado.

```javascript
async function centerOnMunicipio() {
    const estado = document.getElementById('selectEstado').value;
    const mun = document.getElementById('selectMunicipio').value;
    
    // 1. Busca en coordenadas conocidas (cache local)
    const key = estado + mun;
    if (knownCenters[key]) {
        map.setView(knownCenters[key], 14);
        return;
    }
    
    // 2. Si no existe, usa Nominatim para geocodificar
    const munName = MUNICIPIOS[estado]?.[mun];
    const query = `${munName}, ${estadoNombre}, México`;
    const res = await fetch(`https://nominatim.openstreetmap.org/search?q=${query}&format=json`);
    const data = await res.json();
    
    // 3. Centra el mapa en las coordenadas encontradas
    map.setView([data[0].lat, data[0].lon], 14);
}
```

---

### 5. `loadINEGIData()`
**Propósito:** Carga datos de INEGI (población, AGEB) para el municipio.

```javascript
async function loadINEGIData() {
    const estado = document.getElementById('selectEstado').value;
    const mun = document.getElementById('selectMunicipio').value;
    
    // 1. Llama API de AGEB
    const agebRes = await fetch(`api_inegi_ageb.php?estado=${estado}&municipio=${mun}`);
    const agebGeoJSON = await agebRes.json();
    
    // 2. Dibuja polígonos de AGEB en el mapa
    agebLayer = L.geoJSON(agebGeoJSON, {
        style: feature => ({
            fillColor: getColorByDensity(feature.properties.POBTOT),
            fillOpacity: 0.6
        })
    }).addTo(map);
    
    // 3. Obtiene datos de población
    const popRes = await fetch(`api_inegi_poblacion.php?cvegeo=${estado}${mun}`);
    popData = await popRes.json();
    
    // 4. Actualiza estadísticas en el panel
    updatePopulationStats(popData);
}
```

---

### 6. `searchDENUE()`
**Propósito:** Busca competidores usando el Directorio DENUE.

```javascript
async function searchDENUE() {
    const actividad = document.getElementById('denueSearch').value;
    const lat = businessMarker.getLatLng().lat;
    const lng = businessMarker.getLatLng().lng;
    
    // 1. Llama API del DENUE (via proxy PHP)
    const res = await fetch(`api_denue.php?lat=${lat}&lng=${lng}&actividad=${actividad}`);
    denueData = await res.json();
    
    // 2. Limpia marcadores anteriores
    denueMarkers.forEach(m => map.removeLayer(m));
    denueMarkers = [];
    
    // 3. Agrega nuevos marcadores
    denueData.forEach(biz => {
        const marker = L.marker([biz.lat, biz.lng])
            .bindPopup(`<b>${biz.nombre}</b><br>${biz.direccion}`);
        denueMarkers.push(marker);
        marker.addTo(map);
    });
    
    // 4. Actualiza contador
    document.getElementById('denueCount').textContent = denueData.length;
}
```

---

### 7. `saveAnalysisToProject()`
**Propósito:** Guarda el análisis de mercado en el proyecto actual.

```javascript
async function saveAnalysisToProject() {
    // 1. Captura imágenes de los mapas
    const mapImage = await html2canvas(document.getElementById('map'));
    
    // 2. Construye objeto de análisis
    const analysis = {
        ubicacion: businessMarker.getLatLng(),
        poblacion: popData,
        competidores: denueData,
        mapImageBase64: mapImage.toDataURL(),
        fecha: new Date().toISOString()
    };
    
    // 3. Guarda en el proyecto via API
    await fetch('save_row.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            table: 'proyectos',
            id: PlanIA.getCurrentProject().id,
            d6_analisis_mercado_json: JSON.stringify(analysis)
        })
    });
}
```

---

## APIs Usadas

| API | Endpoint | Datos |
|-----|----------|-------|
| INEGI AGEB | `api_inegi_ageb.php` | GeoJSON de polígonos AGEB |
| INEGI Población | `api_inegi_poblacion.php` | Datos del Censo 2020 |
| DENUE | `api_denue.php` | Lista de negocios cercanos |
| Nominatim | `nominatim.openstreetmap.org` | Geocodificación |

---

## Debugging

### Ver datos cargados:
```javascript
console.log('Estados:', ESTADOS);
console.log('Municipios Sonora:', MUNICIPIOS['26']);
console.log('Competidores:', denueData);
```

### Obtener coordenadas actuales:
```javascript
console.log(map.getCenter()); // {lat, lng}
```

### Ver análisis guardado:
```javascript
const project = PlanIA.getCurrentProject();
console.log(JSON.parse(project.d6_analisis_mercado_json));
```
