#!/usr/bin/env python3
"""
================================================================================
PROYECTO: CAFES - Sistema de Planes de Negocio
ARCHIVO:  scripts/cleanup_duplicates.py
COPYRIGHT: © 2026 Fondo Thoth AC.
LICENCIA: GPL-2.0-or-later
DESCRIPCIÓN: Script para limpiar registros duplicados de la base de datos
================================================================================
"""

import requests
import json

API_URL = "http://localhost:8082/save_row.php"

# IDs de registros de prueba a eliminar (de importaciones fallidas/duplicadas)
# Solo mantener IDs 39-53 que son los proyectos finales
TEST_IDS = list(range(18, 39))  # IDs 18 a 38


def delete_project(project_id: int) -> dict:
    """Elimina un proyecto por ID"""
    payload = {
        "action": "delete",
        "id_proyecto": project_id
    }
    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def main():
    print("=" * 60)
    print("CAFES - Limpieza de Registros Duplicados")
    print("=" * 60)
    print(f"\n🗑️  IDs a eliminar: {len(TEST_IDS)}")
    print(f"   Rango: {min(TEST_IDS)} - {max(TEST_IDS)}\n")
    
    deleted = 0
    errors = 0
    
    for project_id in TEST_IDS:
        result = delete_project(project_id)
        
        if result.get("success") or result.get("deleted"):
            deleted_count = result.get("deleted", 1)
            if deleted_count > 0:
                print(f"   ✅ ID {project_id}: Eliminado")
                deleted += 1
            else:
                print(f"   ⏭️  ID {project_id}: No existía")
        else:
            error = result.get("error", "Error desconocido")
            print(f"   ❌ ID {project_id}: {error}")
            errors += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Eliminados: {deleted}")
    print(f"❌ Errores: {errors}")
    print("=" * 60)


if __name__ == "__main__":
    main()
