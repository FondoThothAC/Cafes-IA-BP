# =================================================================================
# PROYECTO: PlanIA (Bob Agent API)
# ARCHIVO: app.py
# COPYRIGHT: © 2026 Fondo Thoth AC.
# LICENCIA: MIT
# DESCRIPCIÓN: API server Flask para interactuar con el Agente Bob desde el frontend.
# =================================================================================

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Importar Agente Bob
from modules.bob_agent import BobAgent
from modules.ocr_mapper import OCRMapper
from modules.audit_logger import AuditLogger

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PlanIA-API")

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde el frontend

# ==============================================================================
# RUTAS API
# ==============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "service": "PlanIA Python Agent API"})

@app.route('/api/agent/analyze', methods=['POST'])
def run_analysis():
    """
    Ejecuta el análisis y generación de sugerencias del Agente Bob.
    Requiere un project_id o el objeto proyecto completo en el body.
    """
    try:
        data = request.json
        project_id = data.get('project_id')
        
        # Opcionalmente recibir datos del proyecto directamente (útil para previews sin guardar)
        project_data = data.get('project_data')
        
        logger.info(f"🤖 Solicitud de análisis para proyecto {project_id}")
        
        # Inicializar agente
        # Nota: Si se pasa project_data, el agente debería poder usarlo en memoria
        # Por ahora asumimos carga desde BD o archivo para simplificar
        bob = BobAgent(project_id)
        
        # Si se enviaron datos frescos, sobreescribir los cargados
        if project_data:
            bob.project = project_data
            
        # Ejecutar flujo completo del agente
        # 1. Cargar/Crear contexto MD
        bob.load_or_create_context()
        
        # 2. Análisis
        completeness = bob.analyze_completeness()
        complexity = bob.determine_complexity()
        industry = bob.determine_industry()
        
        # 3. Generar sugerencias (Web + Reglas + LLM)
        suggestions = bob.complete_all()
        
        # 4. Guardar estado (Complejidad, Contexto, Timestamp)
        bob.save_agent_state()
        
        response = {
            "success": True,
            "project_id": project_id,
            "analysis": {
                "complexity": complexity,
                "industry": industry,
                "completeness": completeness
            },
            "suggestions": suggestions,
            "context_md": bob.context_md
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error en endpoint /api/agent/analyze: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/agent/context', methods=['GET'])
def get_context():
    """
    Obtiene el contexto Markdown actual del proyecto.
    """
    try:
        project_id = request.args.get('project_id')
        if not project_id:
            return jsonify({"error": "project_id required"}), 400
            
        bob = BobAgent(project_id)
        context = bob.load_or_create_context()
        
        return jsonify({"success": True, "context": context})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/agent/ocr-map', methods=['POST'])
def map_ocr_text():
    """
    Recibe texto crudo (OCR) y devuelve campos estructurados.
    """
    try:
        data = request.json
        raw_text = data.get('text', '')
        
        if not raw_text:
            return jsonify({"error": "No text provided"}), 400
            
        mapper = OCRMapper()
        mapped_data = mapper.map_text_to_fields(raw_text)
        
        return jsonify({
            "success": True, 
            "mapped_data": mapped_data,
            "field_count": len(mapped_data)
        })
        
    except Exception as e:
        logger.error(f"Error mapping OCR: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/agent/ocr-upload', methods=['POST'])
def upload_ocr_file():
    """
    Recibe un archivo (imagen), ejecuta OCR y devuelve campos mapeados.
    """
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "No selected file"}), 400
            
        # Guardar temporalmente
        filename = secure_filename(file.filename)
        # Asegurar directorio /tmp existe (en docker suele existir pero por si acaso)
        temp_dir = '/tmp'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        filepath = os.path.join(temp_dir, filename)
        file.save(filepath)
        logger.info(f"📄 Archivo recibido para OCR: {filepath}")
        
        # Procesar
        mapper = OCRMapper()
        raw_text = mapper.extract_text_from_image(filepath)
        
        # Eliminar archivo temp
        try:
            os.remove(filepath)
        except: pass
        
        if not raw_text:
            return jsonify({"success": False, "error": "No text could be extracted (OCR failed)"})
            
        # Mapear
        mapped_data = mapper.map_text_to_fields(raw_text)
        
        return jsonify({
            "success": True,
            "text": raw_text,
            "mapped_data": mapped_data,
            "field_count": len(mapped_data)
        })

    except Exception as e:
        logger.error(f"Error en OCR Upload: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/audit/logs', methods=['GET'])
def get_audit_logs():
    """
    Obtiene los logs de auditoría (para panel admin).
    """
    try:
        limit = int(request.args.get('limit', 100))
        audit = AuditLogger()
        logs = audit.get_logs(limit=limit)
        
        # Reverse to show newest first
        logs.reverse()
        
        return jsonify({"success": True, "logs": logs})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    logger.info(f"🚀 Iniciando PlanIA Agent API en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
