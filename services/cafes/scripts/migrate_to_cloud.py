import mysql.connector
import sys

# --- CONFIGURACIÓN ---
LOCAL_CONFIG = {
    'user': 'plania_user',
    'password': 'plania_pass_2026',
    'host': '127.0.0.1',
    'port': 3306
}

REMOTE_CONFIG = {
    'user': 'fondoth1_fondoth1_agent',
    'password': 'AgenteRemoto2026',
    'host': 'mx112.hostgator.mx',
    'port': 3306,
    'database': 'fondoth1_plania'
}

DATABASES_TO_MIGRATE = ['plania', 'plania_cafes']
TABLES_TO_MIGRATE = ['proyectos_negocio'] # Agregar otras tablas si es necesario (ej: usuarios)

def get_connection(config, db_name=None):
    try:
        conf = config.copy()
        if db_name:
            conf['database'] = db_name
        return mysql.connector.connect(**conf)
    except Exception as e:
        print(f"❌ Error conectando a {config['host']} ({db_name}): {e}")
        return None

def get_table_schema(cursor, table_name):
    """Obtiene el CREATE TABLE de la base de datos origen"""
    cursor.execute(f"SHOW CREATE TABLE {table_name}")
    row = cursor.fetchone() # Develve (Table, Create Table)
    if row:
        if isinstance(row, dict):
            return row['Create Table']
        return row[1]
    return None

def migrate_table(local_conn, remote_conn, table_name, project_source_tag):
    l_cursor = local_conn.cursor(dictionary=True)
    r_cursor = remote_conn.cursor()

    # 1. Leer Schema Local y Crear en Remoto si no existe
    # Usamos un cursor NO dict para esto
    l_cursor_raw = local_conn.cursor()
    create_sql = get_table_schema(l_cursor_raw, table_name)
    l_cursor_raw.close()
    
    if create_sql:
        try:
            # Quitamos AUTO_INCREMENT específico para empezar limpio o mantenemos
            r_cursor.execute(create_sql)
            print(f"   ✨ Tabla '{table_name}' creada/verificada en remoto.")
        except Exception as e:
            # Ignoramos si ya existe (aunque el IF NOT EXISTS debería manejarlo si modificamos el SQL, 
            # pero standard SHOW CREATE no trae IF NOT EXISTS. El error 1050 es Table exists)
            if "1050" not in str(e):
                print(f"   ⚠️ Nota sobre creación de tabla: {e}")

    # 2. Leer Datos Locales
    print(f"   📖 Leyendo datos de '{table_name}'...")
    l_cursor.execute(f"SELECT * FROM {table_name}")
    rows = l_cursor.fetchall()
    
    if not rows:
        print("   ⚠️ Tabla vacía, saltando.")
        return

    print(f"   🚀 Migrando {len(rows)} registros...")
    
    # 3. Insertar
    if rows:
        columns = list(rows[0].keys())
        # Filtramos ID para dejar que el remoto asigne nuevos
        columns_no_id = [c for c in columns if c != 'id_proyecto']
        
        placeholders = ", ".join(["%s"] * len(columns_no_id))
        col_names = ", ".join(columns_no_id)
        
        sql_insert = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"
        
        success_count = 0
        for row in rows:
            values = [row[c] for c in columns_no_id]
            try:
                r_cursor.execute(sql_insert, values)
                success_count += 1
            except Exception as e:
                print(f"   ❌ Error insertando: {e}")
    
    remote_conn.commit()
    print(f"   ✅ {success_count} registros migrados.")

def main():
    print("--- 🚀 INICIANDO MIGRACIÓN A LA NUBE ---")
    
    remote_conn = get_connection(REMOTE_CONFIG)
    if not remote_conn:
        return

    # Intentamos conectar localmente.
    # Si falla plania_user para cafes, intentamos root
    configs_to_try = [
        ('plania', LOCAL_CONFIG),
        ('plania_cafes', {**LOCAL_CONFIG, 'user': 'root', 'password': ''}) # Fallback a root para CAFES
    ]

    for db_name, config in configs_to_try:
        print(f"\n📂 Procesando BD Local: {db_name}")
        local_conn = get_connection(config, db_name)
        
        if not local_conn:
            # Fallback reintento con config original si root falló
            if db_name == 'plania_cafes':
                 local_conn = get_connection(LOCAL_CONFIG, db_name)
        
        if not local_conn:
            continue
            
        for table in TABLES_TO_MIGRATE:
            migrate_table(local_conn, remote_conn, table, db_name)
            
        local_conn.close()

    remote_conn.close()
    print("\n✨ --- MIGRACIÓN COMPLETADA --- ✨")

if __name__ == "__main__":
    main()
