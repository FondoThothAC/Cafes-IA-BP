#!/usr/bin/env python3
"""
================================================================================
PROYECTO: CAFES - Sistema de Planes de Negocio
ARCHIVO:  scripts/import_projects_v2.py
COPYRIGHT: © 2026 Fondo Thoth AC.
LICENCIA: GPL-2.0-or-later
DESCRIPCIÓN: Script mejorado para importar proyectos desde documentos .docx
================================================================================
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from docx import Document

# Configuración
PROJECTS_DIR = "/Users/robertoeduardocelisrobles/Documents/FT Apps/Web/CAFES/Proyectos del CAFES"
OUTPUT_DIR = "/Users/robertoeduardocelisrobles/Documents/FT Apps/Web/CAFES/PlanIA-CAFES/data/imported_projects_v2"


def clean_text(text: str) -> str:
    """Limpia y normaliza texto"""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_money(text: str) -> Optional[float]:
    """Extrae un monto monetario de texto"""
    patterns = [
        r'\$\s*([\d,]+(?:\.\d{2})?)',  # $1,234.56
        r'([\d,]+(?:\.\d{2})?)\s*pesos',  # 1234.56 pesos
        r'([\d,]+(?:\.\d{2})?)\s*MXN',  # 1234 MXN
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = match.group(1).replace(',', '')
            try:
                return float(val)
            except:
                continue
    return None


def find_section_content(paragraphs: List, section_keywords: List[str], max_paragraphs: int = 10) -> str:
    """Encuentra una sección por palabras clave y extrae su contenido"""
    content = []
    capturing = False
    capture_count = 0
    
    for para in paragraphs:
        text = para.text.strip()
        if not text:
            continue
            
        # Verificar si es el inicio de la sección buscada
        text_lower = text.lower()
        for keyword in section_keywords:
            if keyword.lower() in text_lower and len(text) < 100:
                capturing = True
                capture_count = 0
                content = []
                break
        
        # Si estamos capturando, agregar contenido
        if capturing and text:
            # Verificar si llegamos a otra sección (texto corto que parece título)
            if capture_count > 0 and len(text) < 80 and re.match(r'^[A-ZÁÉÍÓÚ\d\.]', text):
                # Posible nuevo título, detener captura
                if any(stop in text_lower for stop in ['unidad', 'estudio', 'análisis', 'cliente', 'proyección', 'inversión']):
                    break
            
            content.append(text)
            capture_count += 1
            
            if capture_count >= max_paragraphs:
                break
    
    return clean_text(' '.join(content))


def extract_products_from_text(full_text: str) -> List[Dict]:
    """Extrae productos con precios del texto completo"""
    products = []
    seen = set()
    
    # Patrones para productos con precios
    patterns = [
        # "tamal de carne $35" o "tamal de carne: $35"
        r'([A-Za-záéíóúñÁÉÍÓÚÑ\s]+(?:de|con|en)?[A-Za-záéíóúñÁÉÍÓÚÑ\s]*)[:\s]+\$\s*(\d+(?:\.\d{2})?)',
        # "se ofrece a $35" después de mencionar producto
        r'(\w+[A-Za-záéíóúñÁÉÍÓÚÑ\s]*)\s+(?:se|a|por)\s+\$\s*(\d+(?:\.\d{2})?)',
        # precio venta: $35 (con contexto previo)
        r'precio\s+(?:de\s+)?venta[:\s]+\$\s*(\d+(?:\.\d{2})?)',
    ]
    
    # Buscar en el texto líneas que mencionen productos con precios
    lines = full_text.split('\n')
    for line in lines:
        # Buscar patrones de productos
        for pattern in patterns[:2]:
            matches = re.findall(pattern, line, re.IGNORECASE)
            for match in matches:
                name = match[0].strip()
                price = float(match[1])
                
                # Filtrar nombres no válidos
                if len(name) < 3 or len(name) > 50:
                    continue
                if name.lower() in ['con', 'de', 'el', 'la', 'los', 'las', 'un', 'una']:
                    continue
                if any(word in name.lower() for word in ['tabla', 'gráfica', 'figura', 'página']):
                    continue
                
                # Evitar duplicados
                key = f"{name.lower()}_{price}"
                if key not in seen:
                    seen.add(key)
                    products.append({
                        "nombre": name,
                        "precio_venta": price,
                        "unidad": "pza"
                    })
    
    return products[:15]  # Máximo 15 productos


def extract_competitors(full_text: str) -> List[Dict]:
    """Extrae información de competidores del texto"""
    competitors = []
    
    # Patrones para encontrar competidores
    patterns = [
        # "Competidor 1: tacos de cabeza, $25/taco"
        r'[Cc]ompetidor\s*\d*[:\s]+([^,\.\n]+)(?:,?\s*\$?\s*(\d+))?',
        # "competencia: ..." 
        r'[Cc]ompetencia\s+(?:directa\s+)?(?:principal\s+)?[:\s]+([^,\.\n]+)',
    ]
    
    lines = full_text.split('\n')
    
    for line in lines:
        for pattern in patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                if isinstance(match, tuple):
                    name = match[0].strip()
                    price = match[1] if len(match) > 1 else None
                else:
                    name = match.strip()
                    price = None
                
                # Filtrar
                if len(name) < 3 or len(name) > 100:
                    continue
                if name.lower() in ['la', 'el', 'los', 'las', 'es', 'son']:
                    continue
                
                comp = {"nombre": name}
                if price:
                    try:
                        comp["precio_referencia"] = float(price)
                    except:
                        pass
                
                # Evitar duplicados
                if name not in [c.get("nombre") for c in competitors]:
                    competitors.append(comp)
    
    # Buscar sección de competencia
    comp_section = re.search(
        r'(?:competencia|competidores?)(?:\s+directa)?[:\s]+([^\.]{20,300})',
        full_text, re.IGNORECASE
    )
    if comp_section and not competitors:
        text = comp_section.group(1)
        competitors.append({"descripcion": text.strip()})
    
    return competitors[:5]  # Máximo 5 competidores


def parse_docx(doc_path: str) -> Dict:
    """Parsea un archivo .docx y extrae datos estructurados"""
    try:
        doc = Document(doc_path)
    except Exception as e:
        print(f"  ❌ Error abriendo {doc_path}: {e}")
        return {}
    
    paragraphs = doc.paragraphs
    full_text = '\n'.join([p.text for p in paragraphs])
    
    # Datos base
    filename = os.path.basename(doc_path)
    project = {
        "source_file": filename,
        "a1_nombre_negocio": "",
        "b1_descripcion_negocio": "",
        "b2_problema_oportunidad": "",
        "b3_propuesta_valor": "",
        "b4_cliente_objetivo_resumen": "",
        "d5_ventaja_competitiva": "",
        "g8_inversion_inicial": 0,
        "g5_costos_fijos_mensuales": 0,
        "g4_utilidad_mensual": 0,
        "e3_productos_bom_json": [],
        "d3_competidores_json": [],
        "raw_sections": {}
    }
    
    # 1. Extraer nombre del negocio - buscar en primeros párrafos
    name_patterns = [
        r'proyecto\s+(?:de\s+)?(?:negocio\s+)?(?:de\s+)?([A-Za-záéíóúñÁÉÍÓÚÑ\s\'\"]+)',
        r'nombre\s+(?:comercial|del\s+negocio)[:\s]+([A-Za-záéíóúñÁÉÍÓÚÑ\s\'\"]+)',
        r'^([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñÁÉÍÓÚÑ\s\'\"]+)$',
    ]
    
    for para in paragraphs[:30]:
        text = para.text.strip()
        if not text:
            continue
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                potential_name = match.group(1).strip()
                if len(potential_name) > 3 and len(potential_name) < 50:
                    if not any(word in potential_name.lower() for word in ['estimados', 'miembros', 'mi nombre', 'unidad']):
                        project["a1_nombre_negocio"] = potential_name
                        break
        if project["a1_nombre_negocio"]:
            break
    
    # Si no encontró nombre, usar del filename
    if not project["a1_nombre_negocio"]:
        name = filename.replace(".docx", "")
        name = re.sub(r'(plan\s*de\s*negocios|plan\s*técnico|[_\-])', ' ', name, flags=re.IGNORECASE)
        project["a1_nombre_negocio"] = clean_text(name)[:50]
    
    # 2. Extraer descripción del negocio
    desc = find_section_content(paragraphs, ['descripción del negocio', 'descripción general', 'resumen ejecutivo'], 5)
    if desc:
        project["b1_descripcion_negocio"] = desc[:2000]
        project["raw_sections"]["descripcion"] = desc
    
    # 3. Extraer oportunidad/problema
    opp = find_section_content(paragraphs, ['oportunidad detectada', 'problema', 'oportunidad de mercado'], 4)
    if opp:
        project["b2_problema_oportunidad"] = opp[:1000]
        project["raw_sections"]["oportunidad"] = opp
    
    # 4. Extraer propuesta de valor
    prop = find_section_content(paragraphs, ['propuesta de valor', 'diferenciador', 'valor único'], 4)
    if prop:
        project["b3_propuesta_valor"] = prop[:1000]
        project["raw_sections"]["propuesta_valor"] = prop
    
    # 5. Extraer cliente objetivo
    cliente = find_section_content(paragraphs, ['cliente meta', 'cliente objetivo', 'público objetivo', 'segmento'], 4)
    if cliente:
        project["b4_cliente_objetivo_resumen"] = cliente[:1000]
        project["raw_sections"]["cliente"] = cliente
    
    # 6. Extraer datos financieros del texto
    financial_keywords = [
        (r'inversión\s+(?:inicial|total)[:\s]*\$\s*([\d,]+(?:\.\d{2})?)', 'g8_inversion_inicial'),
        (r'capital\s+(?:inicial|semilla)[:\s]*\$\s*([\d,]+(?:\.\d{2})?)', 'g8_inversion_inicial'),
        (r'costos?\s+fijos?\s+(?:mensuales?)?[:\s]*\$\s*([\d,]+(?:\.\d{2})?)', 'g5_costos_fijos_mensuales'),
        (r'gastos?\s+fijos?\s+(?:mensuales?)?[:\s]*\$\s*([\d,]+(?:\.\d{2})?)', 'g5_costos_fijos_mensuales'),
        (r'utilidad\s+(?:neta\s+)?mensual[:\s]*\$\s*([\d,]+(?:\.\d{2})?)', 'g4_utilidad_mensual'),
        (r'ganancia\s+(?:neta\s+)?mensual[:\s]*\$\s*([\d,]+(?:\.\d{2})?)', 'g4_utilidad_mensual'),
    ]
    
    for pattern, field in financial_keywords:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            val = match.group(1).replace(',', '')
            try:
                project[field] = float(val)
            except:
                pass
    
    # 7. Extraer productos con precios
    products = extract_products_from_text(full_text)
    project["e3_productos_bom_json"] = products
    
    # 8. Extraer competidores
    competitors = extract_competitors(full_text)
    project["d3_competidores_json"] = competitors
    
    # 9. Extraer ventaja competitiva
    ventaja = find_section_content(paragraphs, ['ventaja competitiva', 'diferenciadores', 'ventaja de precio'], 3)
    if ventaja:
        project["d5_ventaja_competitiva"] = ventaja[:1000]
        project["raw_sections"]["ventaja_competitiva"] = ventaja
    
    return project


def find_plan_files(directory: str) -> List[str]:
    """Encuentra archivos de planes de negocio"""
    files = []
    keywords = ['plan', 'negocio', 'proyecto']
    
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.docx') and not filename.startswith('~'):
                # Priorizar archivos que parecen ser planes de negocio
                fname_lower = filename.lower()
                if any(kw in fname_lower for kw in keywords):
                    files.append(os.path.join(root, filename))
    
    return files


def main():
    """Función principal"""
    print("=" * 70)
    print("CAFES - Importador de Proyectos v2 (con python-docx)")
    print("=" * 70)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"\n📂 Buscando planes en: {PROJECTS_DIR}")
    files = find_plan_files(PROJECTS_DIR)
    print(f"   Encontrados: {len(files)} archivos\n")
    
    all_projects = []
    success_count = 0
    
    for i, filepath in enumerate(files, 1):
        basename = os.path.basename(filepath)
        print(f"[{i:2}/{len(files)}] {basename}")
        
        project = parse_docx(filepath)
        
        if project.get("a1_nombre_negocio"):
            all_projects.append(project)
            success_count += 1
            
            # Guardar JSON individual
            safe_name = re.sub(r'[^\w\-]', '_', project["a1_nombre_negocio"])[:40]
            json_path = os.path.join(OUTPUT_DIR, f"{safe_name}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(project, f, ensure_ascii=False, indent=2)
            
            print(f"       ✓ {project['a1_nombre_negocio']}")
            if project['b1_descripcion_negocio']:
                print(f"         📝 Descripción: {len(project['b1_descripcion_negocio'])} chars")
            if project['g8_inversion_inicial']:
                print(f"         💰 Inversión: ${project['g8_inversion_inicial']:,.0f}")
            if project['e3_productos_bom_json']:
                print(f"         📦 Productos: {len(project['e3_productos_bom_json'])}")
        else:
            print(f"       ⚠️ No se pudo extraer nombre")
    
    # Guardar resumen
    summary_path = os.path.join(OUTPUT_DIR, "_all_projects.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(all_projects, f, ensure_ascii=False, indent=2)
    
    # Guardar reporte
    report_path = os.path.join(OUTPUT_DIR, "_extraction_report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# CAFES - Reporte de Extracción de Proyectos\n\n")
        f.write(f"**Total archivos procesados:** {len(files)}\n")
        f.write(f"**Proyectos extraídos con éxito:** {success_count}\n\n")
        f.write("## Proyectos Extraídos\n\n")
        for p in all_projects:
            f.write(f"### {p['a1_nombre_negocio']}\n")
            f.write(f"- **Archivo:** {p['source_file']}\n")
            if p['b1_descripcion_negocio']:
                f.write(f"- **Descripción:** {p['b1_descripcion_negocio'][:200]}...\n")
            if p['g8_inversion_inicial']:
                f.write(f"- **Inversión Inicial:** ${p['g8_inversion_inicial']:,.2f}\n")
            if p['g5_costos_fijos_mensuales']:
                f.write(f"- **Costos Fijos Mensuales:** ${p['g5_costos_fijos_mensuales']:,.2f}\n")
            if p['e3_productos_bom_json']:
                f.write(f"- **Productos:** {len(p['e3_productos_bom_json'])}\n")
            f.write("\n")
    
    print("\n" + "=" * 70)
    print(f"✅ Procesados: {success_count}/{len(files)} proyectos")
    print(f"📁 Guardados en: {OUTPUT_DIR}")
    print(f"📊 Reporte: {report_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
