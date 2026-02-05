# 📊 Metodologías Adicionales para Análisis de Negocios

## Resumen

Este documento recopila metodologías complementarias a Lean Startup y Delta Model para diferentes etapas y tipos de negocio.

---

## Para Negocios en Operación (No Solo Startups)

### Análisis de Negocio Existente

Cuando un negocio **ya está funcionando**, el análisis cambia de validar hipótesis a **diagnosticar y optimizar**.

#### Framework de Diagnóstico Operativo

```
┌─────────────────────────────────────────────────────────────┐
│                   DIAGNÓSTICO 360°                          │
├─────────────────────────────────────────────────────────────┤
│  1. FINANCIERO        │  2. OPERATIVO         │  3. MERCADO │
│  - Rentabilidad       │  - Eficiencia         │  - Posición │
│  - Flujo de caja      │  - Capacidad          │  - Clientes │
│  - Estructura costos  │  - Calidad            │  - Competencia│
├─────────────────────────────────────────────────────────────┤
│  4. ORGANIZACIONAL    │  5. TECNOLÓGICO       │  6. LEGAL   │
│  - Estructura         │  - Sistemas           │  - Cumplimiento│
│  - Talento            │  - Automatización     │  - Riesgos  │
│  - Cultura            │  - Datos              │  - Contratos│
└─────────────────────────────────────────────────────────────┘
```

#### Métricas Clave por Área

**Financiero:**
| Métrica | Fórmula | Meta General |
|---------|---------|--------------|
| Margen Bruto | (Ventas - Costo) / Ventas | > 40% |
| Margen Operativo | EBIT / Ventas | > 15% |
| ROE | Utilidad Neta / Capital | > 15% |
| Liquidez | Activo Circulante / Pasivo Circulante | > 1.5 |
| Endeudamiento | Pasivo Total / Activo Total | < 60% |

**Operativo:**
| Métrica | Fórmula | Varía por industria |
|---------|---------|---------------------|
| Productividad | Output / Horas trabajadas | Industria |
| Utilización capacidad | Producción real / Capacidad máxima | > 75% |
| Tiempo de ciclo | Tiempo total de proceso | Minimizar |
| Tasa de defectos | Defectos / Producción total | < 2% |

---

## Modelo de Madurez Empresarial

### Etapas de Vida del Negocio

| Etapa | Características | Enfoque Principal | Metodología |
|-------|-----------------|-------------------|-------------|
| **1. Ideación** | Solo concepto | Validar problema | Lean Startup |
| **2. Validación** | MVP en pruebas | Encontrar product-market fit | Customer Development |
| **3. Tracción** | Primeros clientes | Crecer de forma repetible | Growth Hacking |
| **4. Escalamiento** | Modelo probado | Expandir operaciones | Scaling Up |
| **5. Madurez** | Negocio establecido | Optimizar y diversificar | Six Sigma, OKRs |
| **6. Renovación** | Declive o pivote | Reinventar el modelo | Blue Ocean |

### Diagnóstico de Etapa

```python
def determine_business_stage(project: dict) -> str:
    """
    Determina en qué etapa está el negocio.
    """
    revenue = project.get("ingresos_mensuales", 0)
    months_operating = project.get("meses_operando", 0)
    employees = project.get("num_empleados", 0)
    
    if months_operating == 0:
        return "ideacion"
    elif months_operating < 6 and revenue < 50000:
        return "validacion"
    elif months_operating < 24 and revenue < 500000:
        return "traccion"
    elif employees > 10 and revenue > 500000:
        return "escalamiento"
    else:
        return "madurez"
```

---

## Blue Ocean Strategy

### Concepto
Crear mercados sin competencia (océanos azules) en lugar de competir en mercados saturados (océanos rojos).

### Matriz ERIC

| Acción | Pregunta | Ejemplo |
|--------|----------|---------|
| **Eliminar** | ¿Qué factores damos por sentado que podemos eliminar? | Cirque du Soleil eliminó animales |
| **Reducir** | ¿Qué factores podemos reducir muy por debajo del estándar? | Southwest redujo servicios a bordo |
| **Incrementar** | ¿Qué factores podemos incrementar muy por encima del estándar? | Yellow Tail incrementó facilidad de elección |
| **Crear** | ¿Qué factores nunca ofrecidos podemos crear? | iTunes creó compra por canción |

### Curva de Valor

```
                    Competidor A
Nivel    ─────────────────────────────────────
de         ╱╲              ╱╲
Valor     ╱  ╲            ╱  ╲
         ╱    ╲    ╱╲    ╱    ╲
        ╱      ╲  ╱  ╲  ╱      ╲____  Tu Empresa
       ╱        ╲╱    ╲╱
      ─────────────────────────────────────────
      Factor1  Factor2  Factor3  Factor4  Factor5
```

---

## OKRs (Objectives & Key Results)

### Estructura

```
OBJECTIVE: Declaración cualitativa, inspiradora
    └── KEY RESULT 1: Métrica cuantificable (de X a Y)
    └── KEY RESULT 2: Métrica cuantificable (de X a Y)
    └── KEY RESULT 3: Métrica cuantificable (de X a Y)
```

### Ejemplo para Panadería

```markdown
## Q1 2026

### Objetivo 1: Ser la panadería favorita del barrio
- KR1: Aumentar clientes recurrentes de 100 a 200
- KR2: Lograr NPS de 8.5 (actualmente 7.2)
- KR3: Reducir tiempo de espera de 10 min a 5 min

### Objetivo 2: Optimizar operaciones
- KR1: Reducir merma de 8% a 4%
- KR2: Aumentar producción de 500 a 700 piezas/día
- KR3: Implementar 3 automatizaciones en cocina
```

---

## Six Sigma / Lean Manufacturing

### Aplicable a negocios en operación con problemas de calidad/eficiencia.

### DMAIC

| Fase | Objetivo | Herramientas |
|------|----------|--------------|
| **D**efine | Definir problema y alcance | Project Charter, SIPOC |
| **M**easure | Medir estado actual | Diagrama de flujo, métricas |
| **A**nalyze | Analizar causas raíz | Ishikawa, 5 porqués, Pareto |
| **I**mprove | Implementar mejoras | Piloto, diseño de experimentos |
| **C**ontrol | Mantener mejoras | Control charts, SOPs |

### Las 7 Mudas (Desperdicios)

| Muda | Descripción | Ejemplo Panadería |
|------|-------------|-------------------|
| Sobreproducción | Producir más de lo necesario | Pan que se echa a perder |
| Inventario | Stock excesivo | Demasiada harina almacenada |
| Defectos | Productos con fallas | Pan quemado o crudo |
| Movimiento | Movimientos innecesarios | Layout mal diseñado |
| Transporte | Mover materiales sin agregar valor | Ir y venir por ingredientes |
| Espera | Tiempos muertos | Esperar que el horno se caliente |
| Sobreprocesamiento | Trabajar más de lo necesario | Decorar pan que no lo requiere |

---

## Balanced Scorecard

### Las 4 Perspectivas

```
┌────────────────────────────────────────────────┐
│              PERSPECTIVA FINANCIERA            │
│  "¿Cómo nos ven los accionistas/dueños?"      │
│  - ROI, Margen, Flujo de caja, Crecimiento    │
└────────────────────────────────────────────────┘
                        │
┌────────────────────────────────────────────────┐
│              PERSPECTIVA DEL CLIENTE           │
│  "¿Cómo nos ven los clientes?"                │
│  - Satisfacción, Retención, Adquisición       │
└────────────────────────────────────────────────┘
                        │
┌────────────────────────────────────────────────┐
│           PERSPECTIVA DE PROCESOS             │
│  "¿En qué debemos ser excelentes?"            │
│  - Calidad, Tiempo de ciclo, Productividad    │
└────────────────────────────────────────────────┘
                        │
┌────────────────────────────────────────────────┐
│      PERSPECTIVA DE APRENDIZAJE Y CRECIMIENTO │
│  "¿Cómo podemos seguir mejorando?"            │
│  - Capacitación, Innovación, Cultura          │
└────────────────────────────────────────────────┘
```

---

## Cuándo Usar Cada Metodología

| Situación | Metodología Recomendada |
|-----------|------------------------|
| Negocio nuevo, sin validar | **Lean Startup** |
| Negocio funcionando, optimizar | **Six Sigma, OKRs** |
| Buscar posición estratégica | **Delta Model, Porter** |
| Diferenciarse de competencia | **Blue Ocean** |
| Alinear equipo con objetivos | **Balanced Scorecard, OKRs** |
| Analizar modelo de negocio | **Business Model Canvas** |
| Mejorar experiencia cliente | **Customer Journey, NDD** |
| Innovar en industria madura | **Disciplined Entrepreneurship (MIT)** |

---

## Para el Agente Bob

### Detección de Metodología Apropiada

```python
def suggest_methodology(project: dict) -> list:
    """
    Sugiere metodologías basadas en el estado del negocio.
    """
    stage = determine_business_stage(project)
    goals = project.get("objetivos", [])
    problems = project.get("problemas_actuales", [])
    
    suggestions = []
    
    if stage in ["ideacion", "validacion"]:
        suggestions.append("Lean Startup")
        suggestions.append("Customer Development")
    
    if stage in ["traccion", "escalamiento"]:
        suggestions.append("OKRs")
        suggestions.append("Growth Hacking")
    
    if stage == "madurez":
        suggestions.append("Six Sigma")
        suggestions.append("Balanced Scorecard")
    
    if "diferenciación" in goals or "competencia" in problems:
        suggestions.append("Blue Ocean Strategy")
        suggestions.append("Delta Model")
    
    return suggestions
```

---

## Referencias

- Kim, W. Chan. *Blue Ocean Strategy* (2005)
- Kaplan, Robert S. *The Balanced Scorecard* (1996)
- Doerr, John. *Measure What Matters* (2018)
- Blank, Steve. *The Four Steps to the Epiphany* (2005)
- Womack, James. *Lean Thinking* (1996)

---

*Documento generado para RAG de PlanIA - Febrero 2026*
