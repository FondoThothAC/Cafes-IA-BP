# =================================================================================
# PROYECTO: PlanIA (RAG Engine)
# ARCHIVO: modules/rag_engine.py
# COPYRIGHT: © 2026 Fondo Thoth AC.
# LICENCIA: MIT
# DESCRIPCIÓN: Motor de búsqueda semántica usando ChromaDB y SentenceTransformers.
# =================================================================================

import os
import logging
from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions

logger = logging.getLogger("RAGEngine")

class RAGEngine:
    """
    Gestiona la base de datos vectorial para búsqueda semántica en la documentación.
    """
    
    def __init__(self, persist_directory: str = "data/chroma_db"):
        self.persist_directory = persist_directory
        setup_chroma = False
        
        # Crear directorio si no existe
        if not os.path.exists(self.persist_directory):
            os.makedirs(self.persist_directory)
            setup_chroma = True
            
        # Inicializar Cliente Chroma
        # Usamos PersistentClient para guardar datos en disco
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Función de Embedding (usamos all-MiniLM-L6-v2 por defecto, ligero y eficiente)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Obtener o crear colección
        self.collection = self.client.get_or_create_collection(
            name="plania_knowledge_base",
            embedding_function=self.embedding_fn
        )
        
        logger.info(f"🧠 RAG Engine initialized at {self.persist_directory}")

    def add_document(self, doc_id: str, text: str, metadata: Dict[str, Any] = None):
        """Agrega un documento al índice vectorial."""
        if not text or len(text) < 10:
            return

        # Chunking simple (dividir por párrafos o longitud)
        # Para simplificar, aquí guardamos párrafos largos o el texto completo si es corto
        chunks = self._chunk_text(text)
        
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        metadatas = [metadata or {"source": doc_id} for _ in range(len(chunks))]
        
        try:
            self.collection.upsert(
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(chunks)} chunks for document {doc_id}")
        except Exception as e:
            logger.error(f"Error indexing document {doc_id}: {e}")

    def query(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Realiza una búsqueda semántica."""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            # Formatear resultados
            formatted_results = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    meta = results['metadatas'][0][i]
                    formatted_results.append({
                        "content": doc,
                        "metadata": meta,
                        "distance": results['distances'][0][i] if results['distances'] else 0
                    })
                    
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error querying RAG: {e}")
            return []

    def _chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Divide el texto en fragmentos manejables con algo de superposición."""
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + chunk_size
            # Intentar cortar en un punto y aparte
            if end < text_len:
                next_space = text.find('\n', end)
                if next_space != -1 and next_space - end < 200:
                    end = next_space
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Overlap de 100 caracteres
            start = end - 100 if end < text_len else text_len
            
        return chunks

# ==============================================================================
# TEST
# ==============================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    rag = RAGEngine(persist_directory="./chroma_test")
    
    # Test Indexing
    rag.add_document("test_doc_1", "El ROI (Retorno de Inversión) mide la rentabilidad.", {"category": "finanzas"})
    rag.add_document("test_doc_2", "Para abrir una cafetería necesitas permiso de suelo y aviso de funcionamiento.", {"category": "legal"})
    
    # Test Query
    results = rag.query("¿Qué permisos necesito para un restaurante?")
    print("\nResultados de búsqueda:")
    for r in results:
        print(f"- {r['content']} (Meta: {r['metadata']})")
