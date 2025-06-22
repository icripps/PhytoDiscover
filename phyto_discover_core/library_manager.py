import sqlite3
import os
from pyteomics import mass

def build_database(db_path):
    """Creates the SQLite database and the compounds table."""
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE compounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            formula TEXT NOT NULL,
            mass REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database with 'compounds' table created at {db_path}")

def add_compound_to_db(db_path, name, formula):
    """Calculates the mass of a compound and adds it to the database."""
    try:
        # Calculate the monoisotopic mass
        compound_mass = mass.calculate_mass(formula=formula)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO compounds (name, formula, mass) VALUES (?, ?, ?)",
            (name, formula, compound_mass)
        )
        conn.commit()
        conn.close()
        print(f"Added {name} (Mass: {compound_mass}) to the database.")
        return True
    except Exception as e:
        print(f"Error adding {name} to database: {e}")
        return False

if __name__ == '__main__':
    # Example usage: create and populate the database
    DB_FILE = '../data/phyto_discover_core.db'
    os.makedirs('../data', exist_ok=True)
    build_database(DB_FILE)
    add_compound_to_db(DB_FILE, 'Aspirin', 'C9H8O4')
    add_compound_to_db(DB_FILE, 'Metformin', 'C4H11N5')
    add_compound_to_db(DB_FILE, 'Caffeine', 'C8H10N4O2')
    print("\nLibrary manager script executed successfully.")
