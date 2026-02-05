# =================================================================================
# PROYECTO: PlanIA (Form Importer Service)
# ARCHIVO: services/form_importer/app.py
# COPYRIGHT: © 2026 Fondo Thoth AC.
# LICENCIA: MIT
# DESCRIPCIÓN: Microservicio para procesar documentos escaneados (OCR) y 
#              extraer información estructurada para el Plan de Negocios.
# =================================================================================

import os
import logging
import pytesseract
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
from pdf2image import convert_from_path
from werkzeug.utils import secure_filename

# Configurar Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FormImporter")

app = Flask(__name__)
CORS(app)

# Configurar carpeta de subidas
UPLOAD_FOLDER = '/tmp/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max limit

# ==============================================================================
# OCR LOGIC
# ==============================================================================

def extract_text_from_image(image_path):
    """Extrae texto de una imagen usando Tesseract."""
    try:
        text = pytesseract.image_to_string(Image.open(image_path), lang='spa')
        return text
    except Exception as e:
        logger.error(f"Error OCR Image: {e}")
        return ""

def extract_text_from_pdf(pdf_path):
    """Convierte PDF a imágenes y extrae texto."""
    text_content = ""
    try:
        # Convertir páginas a imágenes
        pages = convert_from_path(pdf_path)
        for i, page in enumerate(pages):
            text = pytesseract.image_to_string(page, lang='spa')
            text_content += f"\n--- Page {i+1} ---\n{text}"
    except Exception as e:
        logger.error(f"Error OCR PDF: {e}")
        return ""
    return text_content

# ==============================================================================
# API ROUTES
# ==============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "service": "PlanIA Form Importer (OCR)"})

@app.route('/api/ocr/scan', methods=['POST'])
def scan_document():
    """
    Recibe un archivo (PDF o Imagen), extrae el texto y (futuro) lo mapea a campos.
    """
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    logger.info(f"Processing file: {filename}")
    
    try:
        raw_text = ""
        if filename.lower().endswith('.pdf'):
            raw_text = extract_text_from_pdf(filepath)
        elif filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
            raw_text = extract_text_from_image(filepath)
        else:
            return jsonify({"success": False, "error": "Formato no soportado"}), 400
            
        # Limpieza básica
        clean_text = raw_text.strip()
        
        # TODO: Aquí iría la lógica de LLM/Regex para mapear a JSON
        # Por ahora devolvemos el texto crudo para que el frontend o el agente lo procesen
        
        return jsonify({
            "success": True,
            "filename": filename,
            "extracted_text": clean_text,
            "char_count": len(clean_text)
        })
        
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        # Limpiar archivo temporal
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
