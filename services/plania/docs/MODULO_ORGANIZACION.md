# 👥 Guía del Módulo: Organización y Nómina

## Archivo: `organization.html`

## Propósito
Gestiona el organigrama de la empresa y calcula la nómina con cargas sociales 
(IMSS, INFONAVIT, ISN) según la ley laboral mexicana.

---

## Variables Globales

```javascript
let roles = [];           // Array de puestos [{title, salary, count, riskClass, children}]
let currentProject = null; // Proyecto actual

// Constantes de cálculo (valores 2026)
const UMA = 108.57;       // Unidad de Medida y Actualización diaria
const ISN_RATE = 0.03;    // Impuesto Sobre Nómina (Sonora)

// Primas de riesgo de trabajo por clase
const riskPremiums = {
    'I': 0.0052150,    // Clase I - Oficinas, comercio
    'II': 0.0113650,   // Clase II - Servicios
    'III': 0.0253500,  // Clase III - Industria ligera
    'IV': 0.0435575,   // Clase IV - Industria
    'V': 0.0754500     // Clase V - Construcción, minería
};
```

---

## Funciones Principales

### 1. `loadProjectData()`
**Propósito:** Carga el organigrama guardado del proyecto.

```javascript
function loadProjectData() {
    currentProject = PlanIA.getCurrentProject();
    
    if (currentProject.c4_organigrama_json) {
        roles = JSON.parse(currentProject.c4_organigrama_json);
    } else {
        // Estructura default
        roles = [
            { title: 'Director General', salary: 25000, count: 1, riskClass: 'I', children: [] }
        ];
    }
    
    renderRoles();
}
```

---

### 2. `addRole()`
**Propósito:** Agrega un nuevo puesto al organigrama.

```javascript
function addRole() {
    roles.push({
        title: 'Nuevo Puesto',
        salary: 8000,        // Salario mensual default
        count: 1,            // Número de personas
        riskClass: 'I',      // Clase de riesgo IMSS
        children: []         // Sub-puestos
    });
    
    renderRoles();
}
```

---

### 3. `addChild(roleIndex)`
**Propósito:** Agrega un sub-puesto (reporta a otro).

```javascript
function addChild(roleIndex) {
    roles[roleIndex].children.push({
        title: 'Sub-Puesto',
        salary: 6000,
        count: 1,
        riskClass: 'I',
        children: []
    });
    
    renderRoles();
}
```

---

### 4. `calculateSocialCharge(salary, riskClass)`
**Propósito:** Calcula las cargas sociales patronales por empleado.

```javascript
function calculateSocialCharge(salary, riskClass) {
    const uma = UMA;
    const umaMensual = uma * 30.4;
    
    // Salario Base de Cotización (con factor de integración)
    const sbc = salary * 1.0493;
    
    // 1. RIESGO DE TRABAJO (variable por clase)
    // Clase I: 0.52%, Clase V: 7.54%
    const riesgoTrabajo = sbc * (riskPremiums[riskClass] || 0.0052150);
    
    // 2. ENFERMEDADES Y MATERNIDAD - Cuota Fija
    // 20.40% de la UMA mensual
    const eymCuotaFija = umaMensual * 0.204;
    
    // 3. EXCEDENTE (si SBC > 3 UMA)
    // 1.10% del excedente
    const excedente = Math.max(0, sbc - (umaMensual * 3)) * 0.011;
    
    // 4. PRESTACIONES EN DINERO: 0.70%
    const prestacionesDinero = sbc * 0.007;
    
    // 5. GASTOS MÉDICOS PENSIONADOS: 1.05%
    const gastosMedicos = sbc * 0.0105;
    
    // 6. INVALIDEZ Y VIDA: 1.75%
    const invalidezVida = sbc * 0.0175;
    
    // 7. RETIRO (SAR): 2.00%
    const retiro = sbc * 0.02;
    
    // 8. CESANTÍA Y VEJEZ: 3.15% (patrón)
    const cesantiaVejez = sbc * 0.0315;
    
    // 9. GUARDERÍAS: 1.00%
    const guarderias = sbc * 0.01;
    
    // 10. INFONAVIT: 5.00%
    const infonavit = sbc * 0.05;
    
    // 11. ISN (Impuesto Sobre Nómina, varía por estado)
    // Sonora = 3%
    const isn = salary * ISN_RATE;
    
    // TOTAL CARGA SOCIAL
    return riesgoTrabajo + eymCuotaFija + excedente + prestacionesDinero +
           gastosMedicos + invalidezVida + retiro + cesantiaVejez + 
           guarderias + infonavit + isn;
}
```

**Ejemplo de cálculo:**
| Salario | Carga Social | % del Salario |
|---------|--------------|---------------|
| $8,000  | ~$3,400      | ~42.5%        |
| $15,000 | ~$5,800      | ~38.7%        |
| $30,000 | ~$10,500     | ~35.0%        |

---

### 5. `renderRoles()`
**Propósito:** Dibuja la tabla de puestos y totales.

```javascript
function renderRoles() {
    const tbody = document.getElementById('roles-body');
    let totalEmp = 0, totalSal = 0, totalSocial = 0, totalCost = 0;
    
    // Genera filas HTML
    tbody.innerHTML = roles.map((role, idx) => {
        const social = calculateSocialCharge(role.salary, role.riskClass);
        const cost = (role.salary + social) * role.count;
        
        totalEmp += role.count;
        totalSal += role.salary * role.count;
        totalSocial += social * role.count;
        totalCost += cost;
        
        return `
            <tr>
                <td><input value="${role.title}" onchange="updateRole(${idx}, 'title', this.value)"></td>
                <td><input type="number" value="${role.salary}" onchange="updateRole(${idx}, 'salary', this.value)"></td>
                <td><select onchange="updateRole(${idx}, 'riskClass', this.value)">
                    ${['I','II','III','IV','V'].map(c => 
                        `<option value="${c}" ${c===role.riskClass?'selected':''}>${c}</option>`
                    ).join('')}
                </select></td>
                <td><input type="number" value="${role.count}" onchange="updateRole(${idx}, 'count', this.value)"></td>
                <td>$${social.toLocaleString()}</td>
                <td>$${cost.toLocaleString()}</td>
                <td>
                    <button onclick="addChild(${idx})">➕</button>
                    <button onclick="removeRole(${idx})">🗑️</button>
                </td>
            </tr>
        `;
    }).join('');
    
    // Actualiza totales
    document.getElementById('totalEmpleados').textContent = totalEmp;
    document.getElementById('totalNomina').textContent = `$${totalSal.toLocaleString()}`;
    document.getElementById('totalCargaSocial').textContent = `$${totalSocial.toLocaleString()}`;
    document.getElementById('totalCosto').textContent = `$${totalCost.toLocaleString()}`;
}
```

---

### 6. `fetchBanxicoInflation()`
**Propósito:** Obtiene proyección de inflación de Banxico.

```javascript
async function fetchBanxicoInflation() {
    try {
        const res = await fetch('api_banxico.php?serie=SP1');
        const data = await res.json();
        
        document.getElementById('inflacionActual').textContent = `${data.valor}%`;
        showToast(`Inflación: ${data.valor}% (Banxico)`, 'success');
    } catch (err) {
        // Fallback a proyección manual
        document.getElementById('inflacionActual').textContent = '4.5% (proyección)';
    }
}
```

---

### 7. `saveOrg()`
**Propósito:** Guarda el organigrama en el proyecto.

```javascript
async function saveOrg() {
    await fetch('save_row.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            table: 'proyectos',
            id: currentProject.id,
            c4_organigrama_json: JSON.stringify(roles)
        })
    });
    
    showToast('Organigrama guardado', 'success');
}
```

---

## Estructura de Datos

### Formato de roles:
```json
[
    {
        "title": "Director General",
        "salary": 25000,
        "count": 1,
        "riskClass": "I",
        "children": [
            {
                "title": "Gerente de Ventas",
                "salary": 15000,
                "count": 1,
                "riskClass": "II",
                "children": [
                    {
                        "title": "Vendedor",
                        "salary": 8000,
                        "count": 3,
                        "riskClass": "II",
                        "children": []
                    }
                ]
            }
        ]
    }
]
```

---

## Clases de Riesgo IMSS

| Clase | Prima | Ejemplos |
|-------|-------|----------|
| I | 0.52% | Oficinas, comercio, servicios profesionales |
| II | 1.13% | Restaurantes, hoteles, educación |
| III | 2.53% | Industria textil, alimentos procesados |
| IV | 4.35% | Manufactura, transporte |
| V | 7.58% | Construcción, minería, petróleo |

---

## Debugging

```javascript
// Ver todos los puestos
console.log(roles);

// Calcular carga social manual
console.log(calculateSocialCharge(15000, 'II'));

// Ver organigrama guardado
console.log(JSON.parse(currentProject.c4_organigrama_json));
```
