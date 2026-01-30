#!/usr/bin/env python3
"""
================================================================================
PROYECTO: CAFES - Sistema de Planes de Negocio
ARCHIVO:  scripts/update_projects_products.py
COPYRIGHT: © 2026 Fondo Thoth AC.
LICENCIA: GPL-2.0-or-later
DESCRIPCIÓN: Script para actualizar productos en proyectos existentes
================================================================================
"""

import os
import json
import requests
from typing import Dict, List

# Configuración
CURATED_DIR = "/Users/robertoeduardocelisrobles/Documents/FT Apps/Web/CAFES/PlanIA-CAFES/data/curated_projects"
API_URL = "http://localhost:8082/save_row.php"

# Mapeo de nombre de proyecto a ID en la base de datos (de la última importación)
PROJECT_IDS = {
    "EDUCACIÓN Y PLANEACIÓN FINANCIERA ACTIVIDAD": 39,
    "Emily s Sweets and Bakes": 40,
    "Centro de Impresión SAETA": 41,
    "Vicky's Comida Mexicana": 42,
    "Lonche CDMX María Vieyra": 43,
    "Fonda Sabores Caseros FERSH": 44,
    "Salón de Belleza Reyna": 45,
    "MAGDA Fisioterapia": 46,
    "Estancia de Día Años Dorados": 47,
    "PlanNegocios Noelias Postres": 48,
    "Burritos Doña Francisca": 49,
    "Velas Aromáticas ELAM": 50,
    "BONMIX - Boneless y Alitas": 51,
    "Paris Cute": 52,
    "AGROAVI - Granja Avícola": 53,
}


def load_curated_projects() -> List[Dict]:
    """Carga proyectos curados desde JSON"""
    summary_path = os.path.join(CURATED_DIR, "_curated_projects.json")
    with open(summary_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def update_project(project_id: int, products: List[Dict]) -> Dict:
    """Actualiza productos de un proyecto via API"""
    # Convertir al formato del BOM del sistema
    import uuid
    
    bom_items = []
    ingresos = []
    
    for p in products:
        bom_items.append({
            "nombre": p.get("nombre", ""),
            "precio_venta": p.get("precio_venta", 0),
            "costo_unitario": p.get("costo", 0),
            "unidad": p.get("unidad", "pza"),
            "cantidad_mensual": 100
        })
        ingresos.append({
            "id": str(uuid.uuid4())[:8],
            "nombre": p.get("nombre", ""),
            "precio": p.get("precio_venta", 0),
            "cantidad": 100,
            "frecuencia": "mensual"
        })
    
    payload = {
        "action": "update",
        "id_proyecto": project_id,
        "e3_productos_bom_json": json.dumps(bom_items, ensure_ascii=False),
        "g12_proyeccion_ingresos_json": json.dumps(ingresos, ensure_ascii=False),
    }
    
    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def main():
    """Función principal"""
    print("=" * 70)
    print("CAFES - Actualización de Productos en BD")
    print("=" * 70)
    
    projects = load_curated_projects()
    print(f"\n📦 Proyectos a actualizar: {len(projects)}\n")
    
    updated = 0
    skipped = 0
    
    for p in projects:
        name = p.get("a1_nombre_negocio", "")
        products = p.get("e3_productos_bom_json", [])
        
        if name not in PROJECT_IDS:
            print(f"⚠️  {name}: No tiene ID asignado")
            skipped += 1
            continue
        
        project_id = PROJECT_IDS[name]
        
        if not products:
            print(f"⏭️  {name}: Sin productos")
            skipped += 1
            continue
        
        print(f"🔄 [{project_id}] {name}: {len(products)} productos")
        
        result = update_project(project_id, products)
        
        if result.get("success") or result.get("affected_rows"):
            print(f"   ✅ Actualizado")
            updated += 1
        else:
            error = result.get("error", "Error desconocido")
            print(f"   ❌ {error}")
    
    print("\n" + "=" * 70)
    print(f"✅ Actualizados: {updated}")
    print(f"⏭️  Omitidos: {skipped}")
    print("=" * 70)


if __name__ == "__main__":
    main()
