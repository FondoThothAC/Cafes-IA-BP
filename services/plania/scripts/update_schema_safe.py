import mysql.connector
import os
import sys

# Configuration (loads from env or defaults)
DB_CONFIG = {
    'user': os.getenv('DB_USER', 'plania_user'),
    'password': os.getenv('DB_PASSWORD', 'plania_pass_2026'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'database': os.getenv('DB_NAME', 'plania')
}

NEW_COLUMNS = [
    # Format: (Column Name, SQL Definition)
    # Section 9.5 MODULE DATA
    ('d2_segmento_json', "JSON COMMENT 'Customer segment analysis data'"),
    ('g10_presupuesto_inversion_json', "JSON COMMENT 'Investment budget items'"),
    ('g11_proyeccion_costos_json', "JSON COMMENT 'Cost projection data (fixed and variable)'"),
    ('g12_proyeccion_ingresos_json', "JSON COMMENT 'Revenue projection data (products/services)'"),
    ('i1_clientes_json', "JSON COMMENT 'Customer registry data'"),
    ('i2_encuestas_json', "JSON COMMENT 'Survey data'"),
    ('i3_marketing_json', "JSON COMMENT 'Marketing metrics data'"),
    ('i4_operaciones_json', "JSON COMMENT 'Operations data'"),
    ('i5_cuentas_json', "JSON COMMENT 'Accounting data'"),
    ('i6_estado_resultados_json', "JSON COMMENT 'Income statement data'"),
    ('i7_identidad_json', "JSON COMMENT 'Brand identity (logo, colors, socials)'")
]

def update_schema():
    print(f"🔌 Connecting to {DB_CONFIG['host']}...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SHOW TABLES LIKE 'proyectos_negocio'")
        if not cursor.fetchone():
            print("❌ Table 'proyectos_negocio' does not exist. Please run initial migration first.")
            return

        print("🔍 Checking for missing columns...")
        
        # Get existing columns
        cursor.execute("SHOW COLUMNS FROM proyectos_negocio")
        existing_cols = [row[0] for row in cursor.fetchall()]
        
        for col_name, col_def in NEW_COLUMNS:
            if col_name not in existing_cols:
                alter_query = f"ALTER TABLE proyectos_negocio ADD COLUMN {col_name} {col_def}"
                print(f"   ✨ Adding column: {col_name}")
                try:
                    cursor.execute(alter_query)
                except Exception as e:
                    print(f"   ❌ Error adding {col_name}: {e}")
            else:
                print(f"   ✅ Column {col_name} already exists.")
        
        conn.commit()
        conn.close()
        print("🎉 Schema update structure completed safely.")

    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    update_schema()
