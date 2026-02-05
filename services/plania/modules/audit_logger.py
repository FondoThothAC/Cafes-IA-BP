# =================================================================================
# PROYECTO: PlanIA (Audit Logger)
# ARCHIVO: modules/audit_logger.py
# COPYRIGHT: © 2026 Fondo Thoth AC.
# LICENCIA: MIT
# DESCRIPCIÓN: Sistema de registro de auditoría en formato JSONL.
# =================================================================================

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("AuditLogger")

class AuditLogger:
    """
    Registra todas las acciones críticas del sistema en un archivo de auditoría inmutable.
    Formato: JSON Lines (un objeto JSON por línea).
    """
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "audit.jsonl"
        
        # Ensure file exists
        if not self.log_file.exists():
            self.log_file.touch()
            
    def log_action(self, 
                   actor: str, 
                   action: str, 
                   target: str, 
                   details: Dict[str, Any] = {}, 
                   project_id: Optional[str] = None,
                   ip_address: Optional[str] = None):
        """
        Registra una acción en el log de auditoría.
        
        Args:
            actor: Quién realizó la acción ('User', 'BobAgent', 'System')
            action: Qué hizo ('create', 'update', 'delete', 'research', 'suggest')
            target: Sobre qué actuó ('module:finanzas', 'file:context.md')
            details: Datos adicionales (diff, reason, query)
            project_id: ID del proyecto asociado
            ip_address: IP del cliente (si aplica)
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "actor": actor,
            "action": action,
            "target": target,
            "project_id": str(project_id) if project_id else None,
            "ip_address": ip_address,
            "details": details
        }
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    def get_logs(self, limit: int = 100) -> list:
        """Lee los últimos N logs."""
        logs = []
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        logs.append(json.loads(line))
        except Exception as e:
            logger.error(f"Error reading audit logs: {e}")
            
        return logs[-limit:]
