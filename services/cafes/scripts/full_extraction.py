#!/usr/bin/env python3
"""
================================================================================
PROYECTO: CAFES - Sistema de Planes de Negocio
ARCHIVO:  scripts/full_extraction.py
COPYRIGHT: © 2026 Fondo Thoth AC.
LICENCIA: GPL-2.0-or-later
DESCRIPCIÓN: Extracción completa de TODOS los módulos desde documentos .docx
================================================================================
"""

import os
import re
import json
import uuid
from typing import Dict, List, Optional
from docx import Document

# Configuración
PROJECTS_DIR = "/Users/robertoeduardocelisrobles/Documents/FT Apps/Web/CAFES/Proyectos del CAFES"
OUTPUT_DIR = "/Users/robertoeduardocelisrobles/Documents/FT Apps/Web/CAFES/PlanIA-CAFES/data/full_extraction"


def clean_text(text: str) -> str:
    """Limpia y normaliza texto"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    # Reemplazar caracteres tipográficos
    replacements = {'"': '"', '"': '"', ''': "'", ''': "'", '–': '-', '—': '-', '…': '...'}
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.strip()


def find_section(paragraphs: List, keywords: List[str], max_paras: int = 8) -> str:
    """Encuentra una sección por palabras clave"""
    content = []
    capturing = False
    count = 0
    
    for para in paragraphs:
        text = para.text.strip()
        if not text:
            continue
        
        text_lower = text.lower()
        
        # Iniciar captura si encontramos keyword
        for kw in keywords:
            if kw.lower() in text_lower and len(text) < 120:
                capturing = True
                count = 0
                content = []
                break
        
        if capturing:
            content.append(text)
            count += 1
            
            # Detener si parece nuevo título
            if count > 1 and len(text) < 80:
                if re.match(r'^[\d\.]+\s+[A-ZÁÉÍÓÚ]', text) or text.endswith(':'):
                    if any(stop in text_lower for stop in ['unidad', 'capítulo', 'sección', 'anexo']):
                        break
            
            if count >= max_paras:
                break
    
    return clean_text(' '.join(content))


def extract_money(text: str, patterns: List[str] = None) -> Optional[float]:
    """Extrae valor monetario del texto"""
    if patterns is None:
        patterns = [
            r'\$\s*([\d,]+(?:\.\d{2})?)',
            r'([\d,]+(?:\.\d{2})?)\s*(?:pesos|MXN)',
        ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = match.group(1).replace(',', '')
            try:
                return float(val)
            except:
                pass
    return None


def extract_percentage(text: str) -> Optional[float]:
    """Extrae porcentaje del texto"""
    match = re.search(r'(\d+(?:\.\d+)?)\s*%', text)
    if match:
        try:
            return float(match.group(1))
        except:
            pass
    return None


def parse_document_complete(doc_path: str) -> Dict:
    """Extrae TODOS los datos posibles del documento"""
    try:
        doc = Document(doc_path)
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return {}
    
    paragraphs = doc.paragraphs
    full_text = '\n'.join([p.text for p in paragraphs])
    filename = os.path.basename(doc_path)
    
    project = {
        "source_file": filename,
        # === MÓDULO A: IDENTIDAD ===
        "a1_nombre_negocio": "",
        "a2_nombre_emprendedor": "",
        "a4_carta_presentacion": "",
        
        # === MÓDULO B: RESUMEN EJECUTIVO ===
        "b1_descripcion_negocio": "",
        "b2_problema_oportunidad": "",
        "b3_propuesta_valor": "",
        "b4_cliente_objetivo_resumen": "",
        "b5_monto_solicitado": 0,
        
        # === MÓDULO C: EMPRENDEDOR ===
        "c1_experiencia_previa": "",
        "c2_motivacion": "",
        "c3_disponibilidad_tiempo": "",
        "c4_organigrama_json": [],
        
        # === MÓDULO D: MERCADO ===
        "d1_segmento_cliente": "",
        "d2_necesidades_gustos": "",
        "d3_competidores_json": [],
        "d5_ventaja_competitiva": "",
        "d8_direccion_formateada": "",
        
        # === MÓDULO E: ESTUDIO TÉCNICO ===
        "e1_proceso_produccion": "",
        "e2_capacidad_produccion": "",
        "e3_productos_bom_json": [],
        "e4_proveedores_json": [],
        
        # === MÓDULO F: MARKETING ===
        "f1_identidad_marca": "",
        "f2_estrategia_precios": "",
        "f3_canales_venta": [],
        "f4_estrategia_promocion": "",
        
        # === MÓDULO G: FINANCIERO ===
        "g5_costos_fijos_mensuales": 0,
        "g8_inversion_inicial": 0,
        "g10_presupuesto_inversion_json": [],
        "g11_proyeccion_costos_json": [],
        "g12_proyeccion_ingresos_json": [],
        
        # === MÓDULO H: IMPACTO ===
        "h1_impacto_social": "",
        "h2_impacto_economico": "",
    }
    
    # ========== EXTRACCIONES ==========
    
    # A1: Nombre del negocio
    patterns = [
        r'nombre\s+comercial[:\s]+([A-Za-záéíóúñÁÉÍÓÚÑ\s\'"&]+)',
        r'"([A-Za-záéíóúñÁÉÍÓÚÑ\s\'&]+)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, full_text[:2000], re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            if 5 < len(name) < 50:
                project["a1_nombre_negocio"] = name
                break
    
    # A2: Nombre del emprendedor
    emp_patterns = [
        r'(?:mi nombre es|emprendedor[a]?|fundador[a]?)[:\s]+([A-Za-záéíóúñÁÉÍÓÚÑ\s]+)',
        r'([A-Za-záéíóúñÁÉÍÓÚÑ]+\s+[A-Za-záéíóúñÁÉÍÓÚÑ]+(?:\s+[A-Za-záéíóúñÁÉÍÓÚÑ]+)?)\s*(?:,|\.|es\s+(?:la|el)\s+(?:fundador|emprendedor))',
    ]
    for pattern in emp_patterns:
        match = re.search(pattern, full_text[:3000], re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            if 5 < len(name) < 60 and not any(w in name.lower() for w in ['estimados', 'patronato', 'saeta']):
                project["a2_nombre_emprendedor"] = name
                break
    
    # A4: Carta de presentación (primeros párrafos sustanciales)
    carta = []
    for para in paragraphs[:15]:
        text = para.text.strip()
        if len(text) > 100 and not text.startswith('Unidad'):
            carta.append(text)
            if len(' '.join(carta)) > 500:
                break
    project["a4_carta_presentacion"] = clean_text(' '.join(carta))[:1500]
    
    # B1: Descripción del negocio
    project["b1_descripcion_negocio"] = find_section(paragraphs, 
        ['descripción del negocio', 'descripción general', 'resumen ejecutivo', 'naturaleza del proyecto'], 6)[:2000]
    
    # B2: Problema/Oportunidad
    project["b2_problema_oportunidad"] = find_section(paragraphs,
        ['oportunidad detectada', 'problema', 'oportunidad de mercado', 'problema que resuelve'], 5)[:1500]
    
    # B3: Propuesta de valor
    project["b3_propuesta_valor"] = find_section(paragraphs,
        ['propuesta de valor', 'diferenciador', 'qué te hace diferente', 'valor único'], 4)[:1000]
    
    # B4: Cliente objetivo
    project["b4_cliente_objetivo_resumen"] = find_section(paragraphs,
        ['cliente meta', 'cliente objetivo', 'público objetivo', 'segmento de mercado'], 4)[:800]
    
    # B5: Monto solicitado
    monto_section = find_section(paragraphs, ['capital semilla', 'monto solicitado', 'inversión requerida'], 3)
    if monto_section:
        project["b5_monto_solicitado"] = extract_money(monto_section) or 0
    
    # C1: Experiencia previa
    project["c1_experiencia_previa"] = find_section(paragraphs,
        ['experiencia', 'trayectoria', 'antecedentes', 'formación'], 4)[:1000]
    
    # C2: Motivación
    project["c2_motivacion"] = find_section(paragraphs,
        ['motivación', 'por qué emprender', 'origen de la idea', 'justificación'], 4)[:1000]
    
    # C4: Organigrama (buscar roles)
    org_section = find_section(paragraphs, ['organigrama', 'estructura organizacional', 'equipo', 'personal'], 6)
    roles = []
    role_patterns = [
        r'(?:gerente|director|administrador|encargado|responsable|dueño|propietario)[:\s]+([^,\.\n]+)',
        r'([A-Za-záéíóúñÁÉÍÓÚÑ\s]+):\s*(?:gerente|director|administrador)', 
    ]
    for pattern in role_patterns:
        matches = re.findall(pattern, org_section, re.IGNORECASE)
        for match in matches[:5]:
            name = match.strip() if isinstance(match, str) else match
            if 3 < len(name) < 50:
                roles.append({"nombre": name, "puesto": "Colaborador"})
    project["c4_organigrama_json"] = roles
    
    # D1: Segmento cliente
    project["d1_segmento_cliente"] = find_section(paragraphs,
        ['segmento', 'perfil del cliente', 'demografía', 'características del cliente'], 4)[:800]
    
    # D2: Necesidades
    project["d2_necesidades_gustos"] = find_section(paragraphs,
        ['necesidades', 'gustos', 'preferencias', 'hábitos de consumo'], 3)[:500]
    
    # D3: Competidores
    competitors = []
    comp_section = find_section(paragraphs, ['competencia', 'competidor', 'análisis de competencia'], 8)
    comp_patterns = [
        r'[Cc]ompetidor\s*\d*[:\s]+([^,\.\n]+)(?:,?\s*\$?\s*(\d+))?',
        r'([A-Za-záéíóúñÁÉÍÓÚÑ\s]+):\s*(?:tacos?|precio|vende)',
    ]
    for pattern in comp_patterns:
        matches = re.findall(pattern, comp_section)
        for match in matches[:5]:
            name = match[0].strip() if isinstance(match, tuple) else match.strip()
            if 3 < len(name) < 80:
                comp = {"nombre": name}
                if isinstance(match, tuple) and len(match) > 1 and match[1]:
                    try:
                        comp["precio_referencia"] = float(match[1])
                    except:
                        pass
                if name not in [c.get("nombre") for c in competitors]:
                    competitors.append(comp)
    project["d3_competidores_json"] = competitors
    
    # D5: Ventaja competitiva
    project["d5_ventaja_competitiva"] = find_section(paragraphs,
        ['ventaja competitiva', 'diferenciadores', 'qué nos hace únicos'], 4)[:1000]
    
    # D8: Dirección
    dir_match = re.search(r'(?:ubicad[oa]|dirección|domicilio)[:\s]+([^,\n]{10,100})', full_text, re.IGNORECASE)
    if dir_match:
        project["d8_direccion_formateada"] = dir_match.group(1).strip()
    
    # E1: Proceso de producción
    project["e1_proceso_produccion"] = find_section(paragraphs,
        ['proceso de producción', 'proceso productivo', 'elaboración', 'proceso de servicio'], 5)[:1500]
    
    # E2: Capacidad de producción
    cap_section = find_section(paragraphs, ['capacidad', 'producción diaria', 'capacidad instalada'], 3)
    project["e2_capacidad_produccion"] = cap_section[:500]
    
    # E4: Proveedores
    providers = []
    prov_section = find_section(paragraphs, ['proveedor', 'insumos', 'materias primas'], 5)
    prov_mentions = re.findall(r'(?:proveedor|compra\s+en|adquiere\s+en)[:\s]+([A-Za-záéíóúñÁÉÍÓÚÑ\s]+)', prov_section, re.IGNORECASE)
    for prov in prov_mentions[:5]:
        if 3 < len(prov.strip()) < 50:
            providers.append({"nombre": prov.strip()})
    project["e4_proveedores_json"] = providers
    
    # F1: Identidad de marca
    project["f1_identidad_marca"] = find_section(paragraphs,
        ['identidad', 'marca', 'imagen corporativa', 'logotipo'], 3)[:500]
    
    # F2: Estrategia de precios
    project["f2_estrategia_precios"] = find_section(paragraphs,
        ['estrategia de precio', 'política de precio', 'fijación de precio'], 4)[:800]
    
    # F3: Canales de venta
    canales = []
    canal_section = find_section(paragraphs, ['canales de venta', 'distribución', 'punto de venta', 'cómo vende'], 4)
    if 'domicilio' in canal_section.lower():
        canales.append("Entrega a domicilio")
    if any(word in canal_section.lower() for word in ['whatsapp', 'redes', 'facebook', 'instagram']):
        canales.append("Redes sociales")
    if any(word in canal_section.lower() for word in ['local', 'tienda', 'establecimiento', 'punto de venta']):
        canales.append("Punto de venta físico")
    if any(word in canal_section.lower() for word in ['web', 'internet', 'en línea']):
        canales.append("Venta en línea")
    project["f3_canales_venta"] = canales if canales else ["Venta directa"]
    
    # F4: Estrategia de promoción
    project["f4_estrategia_promocion"] = find_section(paragraphs,
        ['promoción', 'publicidad', 'estrategia de marketing', 'difusión'], 4)[:800]
    
    # G5: Costos fijos mensuales
    costos_section = find_section(paragraphs, ['costos fijos', 'gastos fijos', 'gastos mensuales'], 5)
    project["g5_costos_fijos_mensuales"] = extract_money(costos_section) or 0
    
    # G8: Inversión inicial
    inv_patterns = [
        r'inversi[oó]n\s+(?:inicial|total)[:\s]*\$\s*([\d,]+(?:\.\d{2})?)',
        r'capital\s+(?:inicial|semilla|requerido)[:\s]*\$\s*([\d,]+(?:\.\d{2})?)',
        r'total\s+(?:de\s+)?inversi[oó]n[:\s]*\$\s*([\d,]+(?:\.\d{2})?)',
    ]
    for pattern in inv_patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            val = match.group(1).replace(',', '')
            try:
                project["g8_inversion_inicial"] = float(val)
                break
            except:
                pass
    
    # G10: Presupuesto de inversión (desglose)
    presupuesto = []
    inv_section = find_section(paragraphs, ['presupuesto', 'desglose de inversión', 'activos fijos', 'equipamiento'], 10)
    inv_items = re.findall(r'([A-Za-záéíóúñÁÉÍÓÚÑ\s]+)[:\s]+\$\s*([\d,]+(?:\.\d{2})?)', inv_section)
    for item, amount in inv_items[:10]:
        item_name = item.strip()
        if 3 < len(item_name) < 60:
            try:
                presupuesto.append({
                    "concepto": item_name,
                    "monto": float(amount.replace(',', ''))
                })
            except:
                pass
    project["g10_presupuesto_inversion_json"] = presupuesto
    
    # G12: Proyección de ingresos (productos con precios)
    ingresos = []
    prod_section = find_section(paragraphs, ['productos', 'catálogo', 'menú', 'servicios ofrecidos'], 10)
    prod_patterns = [
        r'([A-Za-záéíóúñÁÉÍÓÚÑ\s]+)\s*(?:a|por|:)\s*\$\s*(\d+(?:\.\d{2})?)',
    ]
    for pattern in prod_patterns:
        matches = re.findall(pattern, full_text)
        for name, price in matches[:15]:
            name = name.strip()
            if 3 < len(name) < 50 and not any(w in name.lower() for w in ['total', 'suma', 'costo']):
                try:
                    ingresos.append({
                        "id": str(uuid.uuid4())[:8],
                        "nombre": name,
                        "precio": float(price),
                        "cantidad": 100,
                        "frecuencia": "mensual"
                    })
                except:
                    pass
    project["g12_proyeccion_ingresos_json"] = ingresos
    
    # H1: Impacto social
    project["h1_impacto_social"] = find_section(paragraphs,
        ['impacto social', 'beneficio social', 'contribución social', 'responsabilidad social'], 4)[:800]
    
    # H2: Impacto económico
    project["h2_impacto_economico"] = find_section(paragraphs,
        ['impacto económico', 'generación de empleo', 'contribución económica'], 4)[:800]
    
    return project


def find_plan_files(directory: str) -> List[str]:
    """Encuentra archivos de planes de negocio"""
    files = []
    keywords = ['plan', 'negocio', 'proyecto']
    
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.docx') and not filename.startswith('~'):
                fname_lower = filename.lower()
                if any(kw in fname_lower for kw in keywords):
                    files.append(os.path.join(root, filename))
    
    return files


def main():
    print("=" * 70)
    print("CAFES - Extracción Completa de Todos los Módulos")
    print("=" * 70)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"\n📂 Buscando planes en: {PROJECTS_DIR}")
    files = find_plan_files(PROJECTS_DIR)
    print(f"   Encontrados: {len(files)} archivos\n")
    
    all_projects = []
    
    for i, filepath in enumerate(files, 1):
        basename = os.path.basename(filepath)
        print(f"[{i:2}/{len(files)}] {basename[:50]}")
        
        project = parse_document_complete(filepath)
        
        if project:
            all_projects.append(project)
            
            # Contar campos poblados
            filled = sum(1 for k, v in project.items() if v and v != 0 and v != [] and k != 'source_file')
            total = len([k for k in project.keys() if k != 'source_file'])
            
            print(f"       ✓ Campos: {filled}/{total} ({filled*100//total}%)")
            
            if project.get("a1_nombre_negocio"):
                print(f"       📋 {project['a1_nombre_negocio'][:40]}")
            if project.get("g8_inversion_inicial"):
                print(f"       💰 Inversión: ${project['g8_inversion_inicial']:,.0f}")
    
    # Guardar resultados
    summary_path = os.path.join(OUTPUT_DIR, "_full_extraction.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(all_projects, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 70)
    print(f"✅ Procesados: {len(all_projects)} proyectos")
    print(f"📁 Guardados en: {OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
