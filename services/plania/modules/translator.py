# =================================================================================
# PROYECTO: PlanIA (Translator Service)
# ARCHIVO: modules/translator.py
# COPYRIGHT: © 2026 Fondo Thoth AC.
# LICENCIA: MIT
# DESCRIPCIÓN: Servicio de traducción para consultas internacionales.
# =================================================================================

import logging
from typing import Optional
from deep_translator import GoogleTranslator

logger = logging.getLogger("Translator")

class TranslatorService:
    """
    Gestiona la traducción de textos usando APIs públicas (Google Translate)
    o LLMs locales como fallback.
    """
    
    def __init__(self):
        self.en_to_es = GoogleTranslator(source='en', target='es')
        self.es_to_en = GoogleTranslator(source='es', target='en')
        logger.info("🌍 Translator Service initialized")

    def translate(self, text: str, source: str = 'auto', target: str = 'es') -> str:
        """
        Traduce un texto.
        
        Args:
            text: Texto a traducir
            source: Idioma origen ('es', 'en', 'auto')
            target: Idioma destino ('es', 'en', 'zh', etc.)
            
        Returns:
            Texto traducido
        """
        if not text or len(text.strip()) == 0:
            return ""
            
        try:
            # Use specific pre-initialized translators for common pairs
            if source == 'en' and target == 'es':
                return self.en_to_es.translate(text)
            elif source == 'es' and target == 'en':
                return self.es_to_en.translate(text)
            else:
                # Dynamic for other pairs
                return GoogleTranslator(source=source, target=target).translate(text)
                
        except Exception as e:
            logger.error(f"Translation error ({source}->{target}): {e}")
            return text # Return original on failure

    def translate_query_for_research(self, query: str, target_lang: str = 'en') -> str:
        """Prepara una consulta para investigación internacional."""
        logger.info(f"Translating query for research: '{query}' -> {target_lang}")
        return self.translate(query, source='es', target=target_lang)
