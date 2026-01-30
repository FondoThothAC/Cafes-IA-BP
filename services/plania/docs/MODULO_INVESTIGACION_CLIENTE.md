# 🔬 Guía del Módulo: Investigación de Cliente

## Archivos: 
- `customer_research.html` (Interno - para el emprendedor)
- `customer_survey.html` (Público - para clientes)

## Propósito
Validar la demanda del mercado mediante encuestas N-D-D (Necesidad, Deseo, Demanda)
aplicadas a clientes potenciales, por cada producto del catálogo.

---

## ⚡ Flujo de Uso

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Seleccionar    │───▶│  Aplicar encuesta│───▶│  Ver métricas   │
│  producto       │    │  o compartir link│    │  y embudo       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

---

## Variables Globales (`customer_research.html`)

```javascript
let currentProject = null;  // Proyecto actualmente seleccionado (del navbar)
let currentProduct = null;  // Producto siendo evaluado
let products = [];          // Lista de productos del módulo de Ingresos
let responses = [];         // Respuestas del producto actual
let allProductResponses = {}; // Todas las respuestas de todos los productos
let currentAnswers = {      // Respuestas de la encuesta actual (en progreso)
    necesidad: null,        // 1 = Sí, 0 = No
    deseo: null,            // 1 = Sí, 2 = Comparar, 0 = No
    demanda: null,          // 0.5, 0.75, 1.0, 1.25, 1.5 o 0
    frecuencia: null,       // 'semanal', 'mensual', etc.
    canal: null,            // 'tienda', 'online', 'whatsapp', etc.
    precioSeleccionado: null
};
```

---

## Funciones Principales

### 1. `loadFromNavbar()`
**Propósito:** Carga el proyecto seleccionado en el navbar global.

```javascript
function loadFromNavbar() {
    // 1. Obtiene proyecto del estado global de PlanIA
    currentProject = PlanIA.getCurrentProject();
    
    if (!currentProject) {
        showError('Selecciona un proyecto en el navbar');
        return;
    }
    
    // 2. Carga los productos del proyecto
    loadProducts();
}
```

---

### 2. `loadProducts()`
**Propósito:** Carga la lista de productos desde el módulo de Ingresos.

```javascript
function loadProducts() {
    // 1. Parsea el JSON de proyección de ingresos
    const revenueData = JSON.parse(currentProject.g12_proyeccion_ingresos_json || '{}');
    products = revenueData.productos || [];
    
    // 2. Carga respuestas guardadas (si existen)
    if (currentProject.i_ndd_responses_json) {
        allProductResponses = JSON.parse(currentProject.i_ndd_responses_json);
    }
    
    // 3. Llena el dropdown de productos
    const select = document.getElementById('productSelect');
    products.forEach((p, idx) => {
        const option = document.createElement('option');
        option.value = idx;
        option.textContent = p.nombre || `Producto ${idx + 1}`;
        select.appendChild(option);
    });
}
```

---

### 3. `selectProduct(idx)`
**Propósito:** Selecciona un producto para evaluar.

```javascript
function selectProduct(idx) {
    currentProduct = products[idx];
    currentProduct._idx = idx;
    
    // 1. Carga respuestas existentes para este producto
    const productKey = `product_${idx}`;
    responses = allProductResponses[productKey] || [];
    
    // 2. Actualiza UI con nombre y precio
    document.getElementById('surveyProductName').textContent = currentProduct.nombre;
    document.getElementById('surveyProductPrice').textContent = `$${currentProduct.precio}`;
    
    // 3. Personaliza las preguntas
    document.getElementById('q1Text').textContent = 
        `¿Tiene la NECESIDAD que "${currentProduct.nombre}" resuelve?`;
    
    // 4. Genera rangos de precio dinámicos
    generatePriceRanges(currentProduct.precio);
    
    // 5. Actualiza métricas
    updateUI();
}
```

---

### 4. `generatePriceRanges(basePrice)`
**Propósito:** Genera botones de precio basados en el precio del producto.

```javascript
function generatePriceRanges(basePrice) {
    const container = document.getElementById('priceRangeOptions');
    
    // Define los rangos como porcentajes del precio base
    const ranges = [
        { pct: 0.5, label: '50% del precio' },
        { pct: 0.75, label: '75% del precio' },
        { pct: 1.0, label: 'Precio completo' },  // ✅ Resaltado
        { pct: 1.25, label: '25% más' },
        { pct: 1.5, label: '50% más' }
    ];
    
    // Genera HTML de botones
    container.innerHTML = ranges.map(range => {
        const price = Math.round(basePrice * range.pct);
        return `
            <button class="answer-btn" 
                    data-question="demanda" 
                    data-value="${range.pct}">
                $${price.toLocaleString()}
            </button>
        `;
    }).join('');
    
    // Re-conecta event listeners
    setupAnswerButtons();
}
```

---

### 5. `addResponse()`
**Propósito:** Registra una respuesta de encuesta.

```javascript
function addResponse() {
    // 1. Valida que haya producto seleccionado
    if (!currentProduct) {
        showToast('Selecciona un producto primero', 'error');
        return;
    }
    
    // 2. Valida que las 3 preguntas obligatorias estén contestadas
    if (currentAnswers.necesidad === null || 
        currentAnswers.deseo === null || 
        currentAnswers.demanda === null) {
        showToast('Responde las 3 preguntas principales', 'error');
        return;
    }
    
    // 3. Crea objeto de respuesta
    const response = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        name: document.getElementById('respondentName').value || 'Anónimo',
        productName: currentProduct.nombre,
        productPrice: currentProduct.precio,
        necesidad: currentAnswers.necesidad,
        deseo: currentAnswers.deseo,
        demanda: currentAnswers.demanda > 0 ? 1 : 0,  // Normalizado
        precioSeleccionado: currentAnswers.demanda,    // % real
        frecuencia: currentAnswers.frecuencia,
        canal: currentAnswers.canal
    };
    
    // 4. Agrega a la lista y guarda
    responses.push(response);
    const productKey = `product_${currentProduct._idx}`;
    allProductResponses[productKey] = responses;
    
    // 5. Limpia formulario y actualiza UI
    resetForm();
    updateUI();
}
```

---

### 6. `updateUI()`
**Propósito:** Actualiza las métricas y gráficas.

```javascript
function updateUI() {
    const total = responses.length;
    
    // Calcula porcentajes
    const necesidadCount = responses.filter(r => r.necesidad === 1).length;
    const deseoCount = responses.filter(r => r.deseo === 1).length;
    const demandaCount = responses.filter(r => r.demanda === 1).length;
    
    const necesidadPct = total ? Math.round((necesidadCount / total) * 100) : 0;
    const deseoPct = total ? Math.round((deseoCount / total) * 100) : 0;
    const demandaPct = total ? Math.round((demandaCount / total) * 100) : 0;
    
    // Actualiza displays
    document.getElementById('necesidadPct').textContent = `${necesidadPct}%`;
    document.getElementById('deseoPct').textContent = `${deseoPct}%`;
    document.getElementById('demandaPct').textContent = `${demandaPct}%`;
    
    // Actualiza embudo visual (barras de ancho variable)
    document.getElementById('funnelNecesidad').style.width = `${necesidadPct}%`;
    document.getElementById('funnelDeseo').style.width = `${deseoPct}%`;
    document.getElementById('funnelDemanda').style.width = `${demandaPct}%`;
    
    // Renderiza lista de respuestas
    renderResponseList();
}
```

---

### 7. `saveToProject()`
**Propósito:** Guarda todas las respuestas y estadísticas en el proyecto.

```javascript
async function saveToProject() {
    // 1. Calcula estadísticas agregadas de TODOS los productos
    let totalResponses = 0, totalNecesidad = 0, totalDeseo = 0, totalDemanda = 0;
    
    Object.values(allProductResponses).forEach(productResps => {
        productResps.forEach(r => {
            totalResponses++;
            if (r.necesidad === 1) totalNecesidad++;
            if (r.deseo === 1) totalDeseo++;
            if (r.demanda === 1) totalDemanda++;
        });
    });
    
    // 2. Calcula tasas de conversión SECUENCIALES (para el embudo del PDF)
    // Alcance = % de los que tienen Necesidad que también tienen Deseo
    const alcancePct = totalNecesidad > 0 
        ? Math.round((totalDeseo / totalNecesidad) * 100) 
        : 0;
    
    // Conversión = % de los que tienen Deseo que también tienen Demanda
    const conversionPct = totalDeseo > 0 
        ? Math.round((totalDemanda / totalDeseo) * 100) 
        : 0;
    
    // 3. Guarda en el proyecto
    await fetch('save_row.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            table: 'proyectos',
            id: currentProject.id,
            i_ndd_responses_json: JSON.stringify(allProductResponses),
            i_alcance_pct: alcancePct,      // Usado en PDF
            i_conversion_pct: conversionPct  // Usado en PDF
        })
    });
}
```

---

### 8. `getSurveyLink()` & `shareSurveyLink()`
**Propósito:** Genera URL para encuesta pública.

```javascript
function getSurveyLink() {
    const baseUrl = window.location.origin + '/customer_survey.html';
    const productIdx = currentProduct ? currentProduct._idx : 0;
    
    // Genera URL con parámetros
    return `${baseUrl}?p=${currentProject.id}&prod=${productIdx}`;
    // Ejemplo: /customer_survey.html?p=123&prod=0
}

function shareSurveyLink() {
    const link = getSurveyLink();
    
    // Copia al portapapeles
    navigator.clipboard.writeText(link).then(() => {
        showToast('Enlace copiado 📋', 'success');
    });
}
```

---

## Encuesta Pública (`customer_survey.html`)

### Parámetros URL:
- `p` - ID del proyecto
- `prod` - Índice del producto (0, 1, 2, ...)

### Flujo:
1. Lee parámetros de URL
2. Carga proyecto desde API
3. Personaliza preguntas con nombre del producto
4. Cliente responde
5. Guarda respuesta en `i_ndd_responses_json` del proyecto

---

## Estructura de Datos

### Respuesta individual:
```json
{
    "id": 1705341234567,
    "timestamp": "2026-01-15T10:00:00.000Z",
    "name": "María García",
    "productName": "Café Orgánico",
    "productPrice": 250,
    "necesidad": 1,           // 1=Sí, 0=No
    "deseo": 1,               // 1=Sí, 2=Comparar, 0=No
    "demanda": 1,             // 1=Pagaría, 0=No
    "precioSeleccionado": 1.0, // 1.0 = precio completo
    "frecuencia": "mensual",
    "canal": "online",
    "source": "public_survey" // Si viene de encuesta pública
}
```

### Almacenamiento por producto:
```json
{
    "product_0": [/* respuestas producto 0 */],
    "product_1": [/* respuestas producto 1 */],
    "product_2": [/* respuestas producto 2 */]
}
```

---

## Debugging

```javascript
// Ver todos los productos
console.log(products);

// Ver respuestas del producto actual
console.log(responses);

// Ver todas las respuestas
console.log(allProductResponses);

// Ver estadísticas guardadas
console.log({
    alcance: currentProject.i_alcance_pct,
    conversion: currentProject.i_conversion_pct
});
```
