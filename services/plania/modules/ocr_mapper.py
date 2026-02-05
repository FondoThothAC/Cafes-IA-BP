# =================================================================================
# PROYECTO: PlanIA (Intelligent OCR Mapping)
# ARCHIVO: modules/ocr_mapper.py
# COPYRIGHT: © 2026 Fondo Thoth AC.
# LICENCIA: MIT
# DESCRIPCIÓN: Mapea texto crudo (OCR) a campos estructurados usando Regex y reglas.
# =================================================================================

import re
import json
import logging
from typing import Dict, Any, List, Optional
try:
    import pytesseract
    from PIL import Image
except ImportError:
    logging.warning("OCR libraries not found (pytesseract/Pillow)")

logger = logging.getLogger("OCRMapper")

class OCRMapper:
    """
    Analiza texto extraído de documentos y lo convierte en estructuras JSON
    compatibles con la base de datos de PlanIA.
    """
    
    def __init__(self):
        # Patrones comunes
        self.patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'(?:\+?52)?[\s\.-]?\(?\d{2,3}\)?[\s\.-]?\d{3,4}[\s\.-]?\d{4}',
            "rfc": r'[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}',
            "currency": r'\$\s?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            "date": r'\d{2}[/-]\d{2}[/-]\d{4}',
        }

    def extract_text_from_image(self, image_path: str) -> str:
        """Extrae texto de una imagen usando Tesseract OCR."""
        try:
            # En Linux (Docker), tesseract suele estar en path
            # pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
            text = pytesseract.image_to_string(Image.open(image_path))
            return text
        except Exception as e:
            logger.error(f"OCR Extraction Error: {e}")
            return ""

    def map_text_to_project(self, raw_text: str, doc_type: str = "general") -> Dict[str, Any]:
        """
        Función principal de mapeo.
        
        Args:
            raw_text: Texto completo extraído por OCR.
            doc_type: Tipo de documento (estado_cuenta, factura, general).
            
        Returns:
            Diccionario con campos mapeados (ej: {'g5_costos_fijos_mensuales': 5000}).
        """
        mapped_data = {}
        
        # 1. Extracción General (Metadatos)
        emails = re.findall(self.patterns["email"], raw_text)
        phones = re.findall(self.patterns["phone"], raw_text)
        rfcs = re.findall(self.patterns["rfc"], raw_text)
        
        if emails: mapped_data["extracted_emails"] = emails
        if phones: mapped_data["extracted_phones"] = phones
        if rfcs: mapped_data["extracted_rfcs"] = rfcs

        # 2. Análisis Específico por Tipo
        if doc_type == "estado_cuenta":
            self._map_bank_statement(raw_text, mapped_data)
        elif doc_type == "factura":
            self._map_invoice(raw_text, mapped_data)
        else:
            # Intento genérico de encontrar costos e ingresos
            self._map_generic_financials(raw_text, mapped_data)
            
        return mapped_data

    def _map_generic_financials(self, text: str, data: Dict[str, Any]):
        """Intenta encontrar costos fijos o inversión en texto libre."""
        
        # Buscar "Renta"
        renta_match = re.search(r'(?:renta|alquiler)[\s\w]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', text, re.IGNORECASE)
        if renta_match:
            try:
                amount = float(renta_match.group(1).replace(',', ''))
                # Asumimos que es parte de costos fijos
                data["g5_costos_fijos_mensuales"] = data.get("g5_costos_fijos_mensuales", 0) + amount
                logger.info(f"Found Rent: {amount}")
            except: pass

        # Buscar "Luz/Electricidad"
        luz_match = re.search(r'(?:luz|electricidad|cfě)[\s\w]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', text, re.IGNORECASE)
        if luz_match:
            try:
                amount = float(luz_match.group(1).replace(',', ''))
                data["g5_costos_fijos_mensuales"] = data.get("g5_costos_fijos_mensuales", 0) + amount
                logger.info(f"Found Electricity: {amount}")
            except: pass

        # Buscar "Sueldos/Nómina"
        nomina_match = re.search(r'(?:sueldos|nómina|salarios)[\s\w]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', text, re.IGNORECASE)
        if nomina_match:
            try:
                amount = float(nomina_match.group(1).replace(',', ''))
                data["g5_costos_fijos_mensuales"] = data.get("g5_costos_fijos_mensuales", 0) + amount
                logger.info(f"Found Payroll: {amount}")
            except: pass
            
    def _map_invoice(self, text: str, data: Dict[str, Any]):
        """Mapeo para facturas (busca totales y conceptos)."""
        # Buscar Total
        total_match = re.search(r'(?:total|neto)[\s\w]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', text, re.IGNORECASE)
        if total_match:
            try:
                amount = float(total_match.group(1).replace(',', ''))
                # Podría ser un costo variable o activo fijo depending on context
                # Por ahora lo guardamos en un log de costos
                data["detected_invoice_total"] = amount
            except: pass
            
    def _map_bank_statement(self, text: str, data: Dict[str, Any]):
        """Mapeo para estados de cuenta (busca saldos y movimientos)."""
        pass
