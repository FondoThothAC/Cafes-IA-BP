import sys
import os
import json
import mysql.connector
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules import BusinessStandards

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# OVERRIDE for local testing (running outside Docker)
os.environ["DB_HOST"] = "127.0.0.1"

def get_db_connection():
    """Create a database connection using environment variables."""
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "plania_user"),
            password=os.getenv("DB_PASSWORD", "plania_pass_2026"),
            database=os.getenv("DB_NAME", "plania"),
            charset='utf8mb4'
        )
    except mysql.connector.Error as e:
        print(f"[Error] Database connection failed: {e}")
        return None

def fetch_project(project_id):
    """Fetch a project from the database by ID (Standalone for testing)."""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM proyectos_negocio WHERE id_proyecto = %s", 
            (project_id,)
        )
        project = cursor.fetchone()
        cursor.close()
        conn.close()
        return project
    except Exception as e:
        print(f"[Error] Could not fetch project: {e}")
        return None

def test_standards(project_id):
    print(f"--- Testing Standards for Project {project_id} ---")
    
    project = fetch_project(project_id)
    if not project:
        print(f"Project {project_id} not found.")
        # Try to find ANY project
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SHOW COLUMNS FROM proyectos_negocio")
            columns = [column[0] for column in cursor.fetchall()]
            print(f"Columns in table: {columns}")
            
            # Try to guess ID column
            id_col = columns[0] # Usually the first one
            print(f"Guessing ID column is: {id_col}")
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM proyectos_negocio LIMIT 1")
            p = cursor.fetchone()
            if p:
                print(f"Found project with ID {p.get(id_col)}: {p.get('a1_nombre_negocio')}")
                test_standards(p[id_col])
            conn.close()
        return

    print(f"Project Name: {project.get('a1_nombre_negocio')}")
    standards = BusinessStandards(project)
    available = standards.get_available_models()
    print(f"Available Models: {available}")
    
    for model in available:
        print(f"\n[Generating {model}]...")
        try:
            data = standards.generate_model(model)
            # Print a summary to avoid flooding console
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    # Test with a common ID. If 26 fails, the script will try to find one.
    test_standards(26) 
