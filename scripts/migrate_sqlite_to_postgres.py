#!/usr/bin/env python3
"""Migrate existing SQLite spectral libraries into unified Postgres schema."""
import sqlite3, os, sys, csv

# Source DB files (current workspace)
SOURCE_DB_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

DB_MAP = {
    'clinical_library.db': ('clinical', 'Clinical Diagnostics'),
    'food_safety_library.db': ('food', 'Food Safety'),
    'forensic_library.db': ('forensic', 'Forensic Toxicology'),
    'plant_library.db': ('plant', 'Plant / Botanical'),
}

def export_to_sql(db_path, module_tag, module_name, output_sql_path):
    if not os.path.exists(db_path):
        print(f"Skipping missing: {db_path}")
        return
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Create module row (id persisted via sequence if needed; for SQL dump use names)
    with open(output_sql_path, 'w', newline='') as f:
        f.write(f"-- Migration for {module_name}\n")
        f.write(f"INSERT INTO modules (name, domain, is_active) VALUES ('{module_name}', '{module_tag}', true) ON CONFLICT (name) DO NOTHING;\n")
        # Compounds
        try:
            cursor.execute("SELECT name, formula, mass FROM compounds")
            for row in cursor.fetchall():
                name, formula, mass = row
                f.write(f"INSERT INTO compound_library (module_id, name, formula, mass) VALUES ((SELECT id FROM modules WHERE name='{module_name}'), '{name}', '{formula}', {mass}) ON CONFLICT DO NOTHING;\n")
        except Exception as e:
            print(f"No compounds table in {db_path}: {e}")
        # Spectra (with embeddings exported as binary hex or array syntax)
        try:
            cursor.execute("SELECT compound_name, precursor_mz, embedding FROM spectra")
            for row in cursor.fetchall():
                compound_name, precursor_mz, embedding = row
                # Postgres array syntax: ARRAY[...] — for simplicity export as text reference note
                # In production, use COPY or psycopg2 binary insert
                f.write(f"-- Spectrum for {compound_name} at m/z {precursor_mz} needs binary embedding import\n")
        except Exception as e:
            print(f"No spectra table in {db_path}: {e}")
    conn.close()
    print(f"Exported SQL for {module_name} to {output_sql_path}")

if __name__ == '__main__':
    out_dir = os.path.join(SOURCE_DB_DIR, '..', 'db', 'migrations')
    os.makedirs(out_dir, exist_ok=True)
    for db_file, (tag, name) in DB_MAP.items():
        db_path = os.path.join(SOURCE_DB_DIR, db_file)
        sql_path = os.path.join(out_dir, f"migrate_{tag}.sql")
        export_to_sql(db_path, tag, name, sql_path)
    print("Migration SQL files generated.")
