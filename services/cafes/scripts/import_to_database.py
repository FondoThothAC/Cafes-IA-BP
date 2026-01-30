#!/usr/bin/env python3
"""
================================================================================
PROYECTO: CAFES - Sistema de Planes de Negocio
ARCHIVO:  scripts/import_to_database.py
COPYRIGHT: © 2026 Fondo Thoth AC.
LICENCIA: GPL-2.0-or-later
DESCRIPCIÓN: Script para importar proyectos curados a la base de datos CAFES
================================================================================
"""

import os
import json
import uuid
import requests
from typing import Dict, List

# Configuración
CURATED_DIR = "/Users/robertoeduardocelisrobles/Documents/FT Apps/Web/CAFES/PlanIA-CAFES/data/curated_projects"
API_URL = "http://localhost:8082/save_row.php"
CAFES_USER_UUID = "cafes-projects-" + str(uuid.uuid4())[:8]  # UUID único para proyectos CAFES


def sanitize_text(text: str) -> str:
    """Sanitiza texto para evitar problemas con caracteres especiales"""
    if not text:
        return ""
    # Reemplazar caracteres problemáticos
    replacements = {
        '"': '"',  # Comilla tipográfica izquierda
        '"': '"',  # Comilla tipográfica derecha
        ''': "'",  # Apóstrofo tipográfico
        ''': "'",  # Comilla simple tipográfica
        '–': '-',  # Guión en-dash
        '—': '-',  # Guión em-dash
        '…': '...',  # Elipsis
        '\u00a0': ' ',  # Non-breaking space
        '\t': ' ',  # Tab
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def load_curated_projects() -> List[Dict]:
    """Carga proyectos curados desde JSON"""
    summary_path = os.path.join(CURATED_DIR, "_curated_projects.json")
    with open(summary_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def prepare_project_payload(project: Dict) -> Dict:
    """Prepara el payload para la API"""
    # Límites de caracteres basados en la estructura de la BD
    LIMITS = {
        "a1_nombre_negocio": 200,
        "b1_descripcion_negocio": 5000,
        "b2_problema_oportunidad": 3000,
        "b3_propuesta_valor": 3000,
        "b4_cliente_objetivo_resumen": 500,  # VARCHAR(500) en la BD
    }
    
    def truncate(text: str, field: str) -> str:
        text = sanitize_text(text)
        limit = LIMITS.get(field, 1000)
        if len(text) > limit:
            return text[:limit-3] + "..."
        return text
    
    payload = {
        "action": "create",
        "uuid_usuario": CAFES_USER_UUID,
        "estatus_proyecto": "borrador",
        "a1_nombre_negocio": truncate(project.get("a1_nombre_negocio", ""), "a1_nombre_negocio"),
        "a2_nombre_emprendedor": "",
        "b1_descripcion_negocio": truncate(project.get("b1_descripcion_negocio", ""), "b1_descripcion_negocio"),
        "b2_problema_oportunidad": truncate(project.get("b2_problema_oportunidad", ""), "b2_problema_oportunidad"),
        "b3_propuesta_valor": truncate(project.get("b3_propuesta_valor", ""), "b3_propuesta_valor"),
        "b4_cliente_objetivo_resumen": truncate(project.get("b4_cliente_objetivo_resumen", ""), "b4_cliente_objetivo_resumen"),
        "g8_inversion_inicial": project.get("g8_inversion_inicial", 0),
        "g5_costos_fijos_mensuales": project.get("g5_costos_fijos_mensuales", 0),
    }
    
    # Agregar productos BOM como JSON
    productos = project.get("e3_productos_bom_json", [])
    if productos:
        # Convertir al formato del BOM del sistema
        bom_items = []
        for p in productos:
            bom_items.append({
                "nombre": p.get("nombre", ""),
                "precio_venta": p.get("precio_venta", 0),
                "costo_unitario": p.get("costo", 0),
                "unidad": p.get("unidad", "pza"),
                "cantidad_mensual": 100  # Valor por defecto
            })
        payload["e3_productos_bom_json"] = json.dumps(bom_items, ensure_ascii=False)
    
    # Agregar al proyección de ingresos también
    if productos:
        ingresos = []
        for p in productos:
            ingresos.append({
                "id": str(uuid.uuid4())[:8],
                "nombre": p.get("nombre", ""),
                "precio": p.get("precio_venta", 0),
                "cantidad": 100,
                "frecuencia": "mensual"
            })
        payload["g12_proyeccion_ingresos_json"] = json.dumps(ingresos, ensure_ascii=False)
    
    return payload


def import_project(payload: Dict) -> Dict:
    """Importa un proyecto a la base de datos via API"""
    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "No se pudo conectar al servidor CAFES en localhost:8082"}
    except Exception as e:
        return {"error": str(e)}


def main():
    """Función principal"""
    print("=" * 70)
    print("CAFES - Importador de Proyectos a Base de Datos")
    print("=" * 70)
    print(f"\n🔗 API: {API_URL}")
    print(f"👤 UUID Usuario: {CAFES_USER_UUID}\n")
    
    projects = load_curated_projects()
    print(f"📦 Proyectos a importar: {len(projects)}\n")
    
    results = {
        "success": [],
        "failed": []
    }
    
    for i, project in enumerate(projects, 1):
        name = project.get("a1_nombre_negocio", "Sin nombre")
        print(f"[{i:2}/{len(projects)}] {name}")
        
        payload = prepare_project_payload(project)
        result = import_project(payload)
        
        if result.get("success"):
            project_id = result.get("id_proyecto")
            print(f"       ✅ ID: {project_id}")
            results["success"].append({"name": name, "id": project_id})
        else:
            error = result.get("error", "Error desconocido")
            print(f"       ❌ {error}")
            results["failed"].append({"name": name, "error": error})
    
    print("\n" + "=" * 70)
    print(f"✅ Importados exitosamente: {len(results['success'])}")
    print(f"❌ Fallidos: {len(results['failed'])}")
    print("=" * 70)
    
    # Guardar reporte
    report_path = os.path.join(CURATED_DIR, "_import_report.json")
    results["uuid_usuario"] = CAFES_USER_UUID
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 Reporte guardado: {report_path}")
    print(f"\n💡 Para ver los proyectos en CAFES, usa el UUID:")
    print(f"   {CAFES_USER_UUID}")


if __name__ == "__main__":
    main()
