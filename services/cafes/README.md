# =================================================================================
# PROYECTO: PlanIA
# ARCHIVO: README.md
# COPYRIGHT: © 2026 Fondo Thoth AC.
# LICENCIA: GPLv2 (Backend/Datos) | MIT (Frontend/UI)
# =================================================================================

# 🚀 PlanIA

**Sistema de Gestión de Planes de Negocio basado en datos reales.**

PlanIA es una plataforma que permite crear, gestionar y analizar planes de negocio utilizando datos de fuentes externas como INEGI DENUE y Banxico. El sistema almacena cada proyecto como una "Super Fila" en MySQL, con columnas estáticas para datos estructurados y columnas JSON para datos dinámicos.

---

## 📁 Estructura del Proyecto

```
PlanIA/
├── config/
│   ├── database.php        # Configuración de conexión MySQL
│   └── .env.example        # Template de variables de entorno
├── database/
│   └── schema_master.sql   # Esquema SQL ("Super Fila")
├── modules/
│   ├── data_harvester.py   # Conexión a INEGI DENUE y Banxico
│   ├── price_scraper.py    # Actualización de costos de insumos
│   └── finance_calc.py     # Cálculos financieros (TIR, VAN, ROI)
├── public/
│   └── save_row.php        # API REST para CRUD de proyectos
├── views/
│   ├── admin_grid.html     # Vista de administración (hoja de cálculo)
│   └── wizard.html         # Formulario paso a paso (SAETA index)
├── main_controller.py      # Orquestador principal
├── README.md
└── LICENSE
```

---

## ⚙️ Instalación

### 1. Base de Datos
```bash
mysql -u root -p < database/schema_master.sql
```

### 2. Configuración
```bash
cp config/.env.example config/.env
# Editar .env con tus credenciales
```

### 3. Dependencias Python
```bash
pip install requests mysql-connector-python python-dotenv
```

### 4. Servidor PHP (desarrollo)
```bash
cd public
php -S localhost:8000
```

---

## 🔌 APIs Externas

| API | Propósito | Documentación |
|-----|-----------|---------------|
| INEGI DENUE | Competidores locales | [inegi.org.mx](https://www.inegi.org.mx/servicios/api_denue.html) |
| Banxico SIE | USD/MXN, TIIE | [banxico.org.mx](https://www.banxico.org.mx/SieAPIRest/service/v1/) |
| Mapbox/Google | Geocodificación | [mapbox.com](https://docs.mapbox.com/api/) |

---

## 🧮 Cálculos Financieros

El módulo `FinancialBrain` calcula automáticamente:

- **Punto de Equilibrio**: Unidades mínimas a vender para cubrir costos fijos.
- **Flujo de Efectivo**: Proyección mensual a 12 meses.
- **ROI**: Retorno de inversión y periodo de recuperación.

---

## 📊 Uso del Sistema

1. **Crear Proyecto**: Abre `views/wizard.html` y completa el formulario paso a paso.
2. **Procesar con IA**: Ejecuta `python main_controller.py` para obtener datos externos.
3. **Administrar**: Usa `views/admin_grid.html` para ver y editar proyectos.

---

## 📜 Licencias

| Componente | Licencia |
|------------|----------|
| Backend (modules/, database/) | GPLv2 |
| Frontend (views/) | MIT |
| Módulos comerciales | Privada |

---

© 2026 Fondo Thoth AC. Todos los derechos reservados.
