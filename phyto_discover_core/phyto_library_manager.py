"""Plant / Botanical (Phyto) library manager for PhytoDiscover."""
import sqlite3
import os

DB_FILENAME = 'plant_library.db'

def get_db_path(project_root=None):
    if project_root is None:
        project_root = os.path.join(os.path.dirname(__file__), '..')
    return os.path.join(project_root, 'data', DB_FILENAME)

def list_plant_compounds(db_path=None):
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, formula, mass FROM compounds")
    results = cursor.fetchall()
    conn.close()
    return results
