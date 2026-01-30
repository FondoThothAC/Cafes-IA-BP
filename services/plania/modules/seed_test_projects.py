import mysql.connector
import json
import os
import sys
from datetime import datetime

# DB Config
DB_CONFIG = {
    'host': 'localhost',
    'user': 'plania_user',
    'password': 'plania_pass_2026',
    'database': 'plania',
    'charset': 'utf8mb4'
}

def create_full_test_project():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 1. Define Rich Data
        # Revenue Data (Balanced Portfolio for Delta Logic -> Target: Total Customer Solution)
        revenue_data = [
            {"nombre_producto": "Suscripción Premium", "precio": 500, "cantidad_mensual": 100}, # 50000 (29.4%)
            {"nombre_producto": "Consultoría Base", "precio": 2000, "cantidad_mensual": 20},    # 40000 (23.5%)
            {"nombre_producto": "Workshop Mensual", "precio": 1500, "cantidad_mensual": 30},    # 45000 (26.4%)
            {"nombre_producto": "Ebook Guía", "precio": 350, "cantidad_mensual": 100}           # 35000 (20.5%)
        ]
        # Total: ~170k. Balanced mix.

        # Competitors (Moderate count)
        competitors_data = [
            {"nombre": "Consultora A", "tipo": "Directo", "fortaleza": "Precio"},
            {"nombre": "Plataforma B", "tipo": "Indirecto", "fortaleza": "Tecnología"},
            {"nombre": "Agencia C", "tipo": "Directo", "fortaleza": "Marketing"}
        ]

        # Financials
        fixed_costs = 50000
        investment = 200000

        project_data = {
            "uuid_usuario": "test_user_generic", # Placeholder
            "estatus_proyecto": "completo",
            "a1_nombre_negocio": "Delta Corp Test",
            "a2_nombre_emprendedor": "Tester User",
            "b1_descripcion_negocio": "Una empresa de consultoría tecnológica integral que ofrece software, capacitación y soporte estratégico para PYMES.",
            "b4_cliente_objetivo_resumen": "PYMES de servicios en crecimiento (10-50 empleados).",
            "d1_segmento_cliente": "Empresas B2B sector servicios",
            "d3_competidores_json": json.dumps(competitors_data, ensure_ascii=False),
            "d5_ventaja_competitiva": "", # Will be filled by logic
            "g5_costos_fijos_mensuales": fixed_costs,
            "g8_inversion_inicial": investment,
            "g12_proyeccion_ingresos_json": json.dumps(revenue_data, ensure_ascii=False),
            "c4_organigrama_json": json.dumps([{"role": "CEO", "count": 1, "salary": 20000}, {"role": "Ventas", "count": 2, "salary": 8000}], ensure_ascii=False),
            "fecha_creacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "fecha_actualizacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "ia_flag_procesar": 1 # Auto-trigger analysis
        }

        # Build SQL
        columns = ', '.join(project_data.keys())
        placeholders = ', '.join(['%s'] * len(project_data))
        sql = f"INSERT INTO proyectos_negocio ({columns}) VALUES ({placeholders})"
        values = list(project_data.values())

        print(f"Executing SQL for project 'Delta Corp Test'...")
        cursor.execute(sql, values)
        conn.commit()
        
        new_id = cursor.lastrowid
        print(f"✅ Success! Created Test Project ID: {new_id}")
        print(f"Recomendación esperada: Horizontal Breadth (Total Customer Solution) debido al balance de ingresos.")

        cursor.close()
        conn.close()
        return new_id

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    create_full_test_project()
