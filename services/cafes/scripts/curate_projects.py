#!/usr/bin/env python3
"""
================================================================================
PROYECTO: CAFES - Sistema de Planes de Negocio
ARCHIVO:  scripts/curate_projects.py
COPYRIGHT: © 2026 Fondo Thoth AC.
LICENCIA: GPL-2.0-or-later
DESCRIPCIÓN: Script de curación manual de proyectos extraídos
================================================================================
"""

import os
import json

INPUT_DIR = "/Users/robertoeduardocelisrobles/Documents/FT Apps/Web/CAFES/PlanIA-CAFES/data/imported_projects_v2"
OUTPUT_DIR = "/Users/robertoeduardocelisrobles/Documents/FT Apps/Web/CAFES/PlanIA-CAFES/data/curated_projects"

# Mapeo manual de nombres correctos basado en análisis de documentos
NAME_CORRECTIONS = {
    "no solo es una aspiración": "Vicky's Comida Mexicana",
    "ÍNDICE": "Centro de Impresión SAETA",
    "Índice": "Salón de Belleza Reyna",
    "Maria Vieyra": "Lonche CDMX María Vieyra",
    "Fernando Yescas": "Fonda Sabores Caseros FERSH",
    "Francisca Castillo": "Burritos Doña Francisca",
    "negocio": "Velas Aromáticas ELAM",
    "Juan Andres Duarte": "BONMIX - Boneless y Alitas",
    "Maria Magdalena Portillo": "MAGDA Fisioterapia",
    "Angélica Cota Duarte": "Estancia de Día Años Dorados",
    "Introducción": "AGROAVI - Granja Avícola",
    "DESCRIPCIÓN GENERAL DE LA EMPRESA": "Paris Cute",
    "Están incorporados en los módulos": None,  # Excluir
    "en Hermosillo": None,  # Excluir
}

# Productos conocidos por proyecto (extraídos manualmente del análisis de documentos)
KNOWN_PRODUCTS = {
    # === PROYECTOS CON PRODUCTOS COMPLETOS ===
    "BONMIX - Boneless y Alitas": [
        {"nombre": "Boneless (orden)", "precio_venta": 90, "costo": 50, "unidad": "pza"},
        {"nombre": "Alitas (orden)", "precio_venta": 100, "costo": 55, "unidad": "pza"},
        {"nombre": "Papas Sazonadas", "precio_venta": 60, "costo": 30, "unidad": "pza"},
        {"nombre": "Ensalada con Pollo", "precio_venta": 80, "costo": 40, "unidad": "pza"},
    ],
    "Vicky's Comida Mexicana": [
        {"nombre": "Tamal de Carne", "precio_venta": 35, "costo": 14.84, "unidad": "pza"},
        {"nombre": "Tamal de Elote", "precio_venta": 30, "costo": 12, "unidad": "pza"},
        {"nombre": "Guisado de Carne con Chile", "precio_venta": 40, "costo": 18, "unidad": "pza"},
    ],
    "Emily s Sweets and Bakes": [
        {"nombre": "Pastel Personalizado", "precio_venta": 450, "costo": 200, "unidad": "pza"},
        {"nombre": "Cheesecake", "precio_venta": 350, "costo": 150, "unidad": "pza"},
        {"nombre": "Postres Pequeños", "precio_venta": 80, "costo": 35, "unidad": "pza"},
        {"nombre": "Cupcakes (6)", "precio_venta": 120, "costo": 50, "unidad": "caja"},
    ],
    "Burritos Doña Francisca": [
        {"nombre": "Burrito de Carne", "precio_venta": 45, "costo": 20, "unidad": "pza"},
        {"nombre": "Burrito de Frijol con Queso", "precio_venta": 35, "costo": 15, "unidad": "pza"},
        {"nombre": "Burrito Combinado", "precio_venta": 50, "costo": 22, "unidad": "pza"},
    ],
    "Salón de Belleza Reyna": [
        {"nombre": "Corte de Cabello", "precio_venta": 100, "costo": 20, "unidad": "servicio"},
        {"nombre": "Tinte", "precio_venta": 350, "costo": 120, "unidad": "servicio"},
        {"nombre": "Peinado", "precio_venta": 200, "costo": 50, "unidad": "servicio"},
        {"nombre": "Manicure", "precio_venta": 150, "costo": 40, "unidad": "servicio"},
    ],
    "AGROAVI - Granja Avícola": [
        {"nombre": "Huevo (docena)", "precio_venta": 45, "costo": 25, "unidad": "docena"},
        {"nombre": "Huevo (caja 360 pzas)", "precio_venta": 1200, "costo": 700, "unidad": "caja"},
    ],
    # === PRODUCTOS NUEVOS EXTRAÍDOS ===
    "Centro de Impresión SAETA": [
        {"nombre": "Impresión B/N (hoja)", "precio_venta": 2, "costo": 0.5, "unidad": "pza"},
        {"nombre": "Impresión Color (hoja)", "precio_venta": 5, "costo": 1.5, "unidad": "pza"},
        {"nombre": "Tarjetas de Presentación (100)", "precio_venta": 150, "costo": 50, "unidad": "paquete"},
        {"nombre": "Etiquetas Personalizadas (50)", "precio_venta": 80, "costo": 25, "unidad": "paquete"},
        {"nombre": "Folletos Tríptico (10)", "precio_venta": 100, "costo": 35, "unidad": "paquete"},
    ],
    "Lonche CDMX María Vieyra": [
        {"nombre": "Taco de Cochinita Pibil", "precio_venta": 20, "costo": 8.22, "unidad": "pza"},
        {"nombre": "Taco de Mole con Pollo", "precio_venta": 20, "costo": 7.75, "unidad": "pza"},
        {"nombre": "Taco de Bistec Guisado", "precio_venta": 20, "costo": 8.02, "unidad": "pza"},
        {"nombre": "Paquete 4 Tacos Mixtos", "precio_venta": 55, "costo": 25, "unidad": "paquete"},
        {"nombre": "Tamal Casero", "precio_venta": 28, "costo": 12, "unidad": "pza"},
        {"nombre": "Agua Fresca (vaso)", "precio_venta": 15, "costo": 5, "unidad": "pza"},
    ],
    "Fonda Sabores Caseros FERSH": [
        {"nombre": "Tamal de Carne con Chile", "precio_venta": 25, "costo": 10.11, "unidad": "pza"},
        {"nombre": "Frijoles de Puerco (porción)", "precio_venta": 45, "costo": 18, "unidad": "pza"},
        {"nombre": "Carne con Chile Rojo (porción)", "precio_venta": 100, "costo": 45, "unidad": "pza"},
    ],
    "MAGDA Fisioterapia": [
        {"nombre": "Sesión Fisioterapia General", "precio_venta": 400, "costo": 80, "unidad": "sesión"},
        {"nombre": "Terapia Artesanal Integral", "precio_venta": 500, "costo": 100, "unidad": "sesión"},
        {"nombre": "Sesión Pediátrica", "precio_venta": 450, "costo": 90, "unidad": "sesión"},
        {"nombre": "Masaje Terapéutico", "precio_venta": 350, "costo": 70, "unidad": "sesión"},
        {"nombre": "Paquete 10 Sesiones", "precio_venta": 3500, "costo": 700, "unidad": "paquete"},
    ],
    "Estancia de Día Años Dorados": [
        {"nombre": "Estancia Mensual Completa", "precio_venta": 7000, "costo": 3500, "unidad": "mes"},
        {"nombre": "Estancia Diaria", "precio_venta": 400, "costo": 200, "unidad": "día"},
        {"nombre": "Horario Extendido (adicional)", "precio_venta": 100, "costo": 50, "unidad": "día"},
        {"nombre": "Fin de Semana", "precio_venta": 500, "costo": 250, "unidad": "día"},
    ],
    "PlanNegocios Noelias Postres": [
        {"nombre": "Bollito Relleno Nutella", "precio_venta": 35, "costo": 15, "unidad": "pza"},
        {"nombre": "Bollito Relleno Queso Crema", "precio_venta": 35, "costo": 14, "unidad": "pza"},
        {"nombre": "Bollito Relleno Cajeta", "precio_venta": 35, "costo": 14, "unidad": "pza"},
        {"nombre": "Caja Bollitos (6)", "precio_venta": 180, "costo": 75, "unidad": "caja"},
    ],
    "Velas Aromáticas ELAM": [
        {"nombre": "Vela de Recuerdo (100gr)", "precio_venta": 69.26, "costo": 41.56, "unidad": "pza"},
        {"nombre": "Vela de Frasco (250gr)", "precio_venta": 139.09, "costo": 83.46, "unidad": "pza"},
        {"nombre": "Vela Decorativa Grande", "precio_venta": 250, "costo": 120, "unidad": "pza"},
        {"nombre": "Set Velas Evento (10)", "precio_venta": 600, "costo": 350, "unidad": "set"},
    ],
    "Paris Cute": [
        {"nombre": "Decoración Boda Básica", "precio_venta": 8000, "costo": 3500, "unidad": "evento"},
        {"nombre": "Decoración XV Años", "precio_venta": 6000, "costo": 2500, "unidad": "evento"},
        {"nombre": "Decoración Baby Shower", "precio_venta": 3500, "costo": 1500, "unidad": "evento"},
        {"nombre": "Mesa de Dulces", "precio_venta": 2500, "costo": 1000, "unidad": "servicio"},
        {"nombre": "Arco de Globos", "precio_venta": 1200, "costo": 400, "unidad": "pza"},
    ],
}

def curate_projects():
    """Curar proyectos con correcciones manuales"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Cargar todos los proyectos
    all_path = os.path.join(INPUT_DIR, "_all_projects.json")
    with open(all_path, 'r', encoding='utf-8') as f:
        projects = json.load(f)
    
    curated = []
    skipped = 0
    
    for p in projects:
        name = p.get("a1_nombre_negocio", "")
        
        # Aplicar corrección de nombre
        if name in NAME_CORRECTIONS:
            new_name = NAME_CORRECTIONS[name]
            if new_name is None:
                print(f"⏭️  Excluido: {name}")
                skipped += 1
                continue
            print(f"✏️  {name} → {new_name}")
            p["a1_nombre_negocio"] = new_name
            name = new_name
        
        # Aplicar productos conocidos
        if name in KNOWN_PRODUCTS:
            p["e3_productos_bom_json"] = KNOWN_PRODUCTS[name]
            print(f"   📦 Productos actualizados: {len(KNOWN_PRODUCTS[name])}")
        else:
            # Limpiar productos mal extraídos
            p["e3_productos_bom_json"] = []
        
        curated.append(p)
    
    # Eliminar duplicados (por nombre)
    seen = set()
    deduplicated = []
    for p in curated:
        name = p["a1_nombre_negocio"]
        if name not in seen:
            seen.add(name)
            deduplicated.append(p)
        else:
            print(f"🔄 Duplicado removido: {name}")
            skipped += 1
    
    # Guardar proyectos curados
    for p in deduplicated:
        safe_name = "".join(c if c.isalnum() or c in ' -_' else '_' for c in p["a1_nombre_negocio"])[:40]
        json_path = os.path.join(OUTPUT_DIR, f"{safe_name}.json")
        
        # Remover raw_sections del JSON final
        if "raw_sections" in p:
            del p["raw_sections"]
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(p, f, ensure_ascii=False, indent=2)
    
    # Guardar resumen
    summary_path = os.path.join(OUTPUT_DIR, "_curated_projects.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(deduplicated, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ Proyectos curados: {len(deduplicated)}")
    print(f"⏭️  Excluidos/duplicados: {skipped}")
    print(f"📁 Guardados en: {OUTPUT_DIR}")
    print(f"{'='*60}")
    
    return deduplicated


if __name__ == "__main__":
    curate_projects()
