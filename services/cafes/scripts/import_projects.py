#!/usr/bin/env python3
"""
================================================================================
PROYECTO: CAFES - Sistema de Planes de Negocio
ARCHIVO:  scripts/import_projects.py
COPYRIGHT: © 2026 Fondo Thoth AC.
LICENCIA: GPL-2.0-or-later
DESCRIPCIÓN: Script para importar proyectos desde documentos .docx a la base de datos
================================================================================
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

# Configuración
PROJECTS_DIR = "/Users/robertoeduardocelisrobles/Documents/FT Apps/Web/CAFES/Proyectos del CAFES"
OUTPUT_DIR = "/Users/robertoeduardocelisrobles/Documents/FT Apps/Web/CAFES/PlanIA-CAFES/data/imported_projects"

def extract_text_from_docx(docx_path: str) -> str:
    """Extrae texto de un archivo .docx usando textutil (macOS)"""
    try:
        result = subprocess.run(
            ['textutil', '-convert', 'txt', docx_path, '-stdout'],
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception as e:
        print(f"Error extracting {docx_path}: {e}")
        return ""

def extract_section(text: str, start_pattern: str, end_patterns: List[str]) -> str:
    """Extrae una sección del texto entre patrones"""
    start_match = re.search(start_pattern, text, re.IGNORECASE | re.MULTILINE)
    if not start_match:
        return ""
    
    start_pos = start_match.end()
    end_pos = len(text)
    
    for pattern in end_patterns:
        end_match = re.search(pattern, text[start_pos:], re.IGNORECASE | re.MULTILINE)
        if end_match:
            end_pos = min(end_pos, start_pos + end_match.start())
    
    return text[start_pos:end_pos].strip()

def extract_numbers(text: str) -> List[float]:
    """Extrae números de un texto"""
    numbers = re.findall(r'\$?\s*[\d,]+\.?\d*', text)
    result = []
    for n in numbers:
        clean = re.sub(r'[$,\s]', '', n)
        try:
            result.append(float(clean))
        except:
            pass
    return result

def parse_project(docx_path: str) -> Dict:
    """Parsea un documento de plan de negocios"""
    text = extract_text_from_docx(docx_path)
    if not text:
        return {}
    
    project = {
        "source_file": os.path.basename(docx_path),
        "a1_nombre_negocio": "",
        "b1_descripcion_negocio": "",
        "b2_problema_oportunidad": "",
        "b3_propuesta_valor": "",
        "b4_cliente_objetivo_resumen": "",
        "g8_inversion_inicial": 0,
        "g5_costos_fijos_mensuales": 0,
        "e3_productos_bom_json": [],
        "d3_competidores_json": [],
    }
    
    # Extraer nombre del negocio (del nombre del archivo o contenido)
    filename = os.path.basename(docx_path)
    project["a1_nombre_negocio"] = filename.replace("Plan de negocios", "").replace("PLAN DE NEGOCIOS", "").replace(".docx", "").replace("-", "").strip()
    
    # Extraer descripción del negocio
    desc = extract_section(
        text,
        r'(descripci[oó]n\s*(general\s*)?del\s*negocio|resumen\s*ejecutivo)',
        [r'\d+\.\s+[A-Za-z]', r'identidad', r'objetivos']
    )
    if desc:
        project["b1_descripcion_negocio"] = desc[:2000]  # Limitar a 2000 chars
    
    # Extraer público objetivo
    publico = extract_section(
        text,
        r'(p[uú]blico\s*objetivo|cliente\s*objetivo|segmento)',
        [r'\d+\.\s+[A-Za-z]', r'competencia', r'oferta']
    )
    if publico:
        project["b4_cliente_objetivo_resumen"] = publico[:1000]
    
    # Extraer inversión inicial
    inversion = extract_section(
        text,
        r'(inversi[oó]n\s*(inicial|total)|capital\s*inicial)',
        [r'\d+\.\s+[A-Za-z]', r'gastos', r'costos\s*fijos']
    )
    nums = extract_numbers(inversion)
    if nums:
        # Buscar el número más grande que parezca inversión (> 1000)
        big_nums = [n for n in nums if n > 1000]
        if big_nums:
            project["g8_inversion_inicial"] = max(big_nums)
    
    # Extraer costos fijos
    costos = extract_section(
        text,
        r'(costos?\s*fijos?|gastos?\s*fijos?)',
        [r'\d+\.\s+[A-Za-z]', r'costos\s*variables', r'ingresos']
    )
    nums = extract_numbers(costos)
    if nums:
        # Buscar número que parezca costo mensual (< 100000)
        monthly_nums = [n for n in nums if 500 < n < 100000]
        if monthly_nums:
            project["g5_costos_fijos_mensuales"] = monthly_nums[0]
    
    # Extraer productos (buscar listas con precios)
    productos = extract_section(
        text,
        r'(productos?|cat[aá]logo|men[uú])',
        [r'\d+\.\s+[A-Za-z]', r'proveedores', r'insumos']
    )
    
    # Buscar patrones de producto:precio
    product_patterns = re.findall(r'([A-Za-záéíóúñÁÉÍÓÚÑ\s]+)[\s:$\-]+(\d+(?:,\d{3})*(?:\.\d{2})?)', productos)
    bom = []
    for name, price in product_patterns[:10]:  # Max 10 productos
        name = name.strip()
        if len(name) > 3 and len(name) < 50:
            try:
                bom.append({
                    "nombre": name,
                    "precio": float(price.replace(",", "")),
                    "unidad": "pza"
                })
            except:
                pass
    project["e3_productos_bom_json"] = bom
    
    return project

def find_docx_files(directory: str) -> List[str]:
    """Encuentra todos los archivos .docx en un directorio (recursivo)"""
    docx_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.docx') and not file.startswith('~'):
                if 'plan' in file.lower() or 'negocio' in file.lower():
                    docx_files.append(os.path.join(root, file))
    return docx_files

def main():
    """Función principal"""
    print("=" * 60)
    print("CAFES - Importador de Proyectos")
    print("=" * 60)
    
    # Crear directorio de salida
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Buscar archivos .docx
    print(f"\nBuscando planes de negocio en: {PROJECTS_DIR}")
    docx_files = find_docx_files(PROJECTS_DIR)
    print(f"Encontrados: {len(docx_files)} archivos\n")
    
    all_projects = []
    
    for i, docx_path in enumerate(docx_files, 1):
        print(f"[{i}/{len(docx_files)}] Procesando: {os.path.basename(docx_path)}")
        
        project = parse_project(docx_path)
        if project.get("a1_nombre_negocio"):
            all_projects.append(project)
            
            # Guardar JSON individual
            safe_name = re.sub(r'[^\w\-]', '_', project["a1_nombre_negocio"])[:30]
            json_path = os.path.join(OUTPUT_DIR, f"{safe_name}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(project, f, ensure_ascii=False, indent=2)
            
            print(f"   → {project['a1_nombre_negocio']}")
            print(f"   → Inversión: ${project['g8_inversion_inicial']:,.0f}")
            print(f"   → Productos: {len(project['e3_productos_bom_json'])}")
    
    # Guardar resumen
    summary_path = os.path.join(OUTPUT_DIR, "_all_projects.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(all_projects, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"✅ Procesados: {len(all_projects)} proyectos")
    print(f"📁 Guardados en: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
